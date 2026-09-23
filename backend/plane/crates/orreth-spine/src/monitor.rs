// PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp4, the loops · 2026-09-23
//! The Monitoring workspace's ground — `orreth_spine.monitor` (canon 0001:
//! "if it's monitoring, it goes here"): the live snapshot of the Operating
//! State — rails, benches, bodies, asks, the last harness run — and the
//! WATCHES: named checks, each judged against the snapshot, honestly red or
//! green. The sense of a watch (W14) is [`crate::watch::judge`]: RED when
//! `metric op threshold` holds now. The state is judged on every beat; red →
//! green and green → red are recorded TRANSITIONS — `last_ok` and `since` on
//! the row, a `orreth.watch.turned.v1` fact through the outbox — and the
//! intent loop wakes on the red transition alone, never on a standing red.
//! `judge` runs under the intent beat (the beat lock): two kernels never
//! record one turn twice.

use crate::ask::ASK_RECEIVED;
use crate::envelope::{self, Mint};
use crate::ground::Ground;
use crate::invoke;
use crate::outbox::{self, outbox_lag};
use crate::presence;
use crate::rails::serve_queue;
use crate::watch::{self, judge as judge_one, reads, turned_payload, METRICS, OPS, WATCH_TURNED};
use crate::world::{iso_opt, isoformat, refused, token_hex, RoadError, World};
use lapin::options::QueueDeclareOptions;
use lapin::types::FieldTable;
use serde_json::{json, Map, Value};
use std::time::{Duration, SystemTime};

/// A new watch on the ground — the act the interlock guards. The condition is
/// what the watch catches: red WHEN it holds. Refusals in the reference's words.
pub async fn add_watch(
    g: &Ground,
    scope: &str,
    name: &str,
    metric: &str,
    op: &str,
    threshold: f64,
    by: &str,
) -> Result<String, RoadError> {
    if !METRICS.contains(&metric) {
        return Err(refused(format!(
            "no metric named '{metric}'; the metrics are {}",
            METRICS.join(", ")
        )));
    }
    if !OPS.contains(&op) {
        return Err(refused(format!("the op is one of {}", OPS.join(", "))));
    }
    let wid = format!("watch_{}", token_hex(5));
    g.client()
        .execute(
            "INSERT INTO spine_watches (watch_id, name, metric, op, threshold, added_by, scope) \
             VALUES ($1, $2, $3, $4, $5, $6, $7)",
            &[&wid, &name, &metric, &op, &threshold, &by, &scope],
        )
        .await?;
    Ok(wid)
}

/// The benches' depths: the shared bench and every body's own, by a passive
/// declare (a queue that is not there reads `null`; a rail that does not
/// answer reads `{"error": …}`), as `monitor._benches`.
async fn benches(w: &World, names: &[String]) -> Value {
    let out: Result<Value, crate::rail_error::RailError> = async {
        let conn = invoke::connect(&w.rabbit_url).await?;
        let mut ch = conn.create_channel().await?;
        let mut m = Map::new();
        let mut queues = vec![serve_queue(&w.ns, None)];
        queues.extend(names.iter().map(|n| serve_queue(&w.ns, Some(n))));
        for q in queues {
            let declared = ch
                .queue_declare(
                    q.as_str().into(),
                    QueueDeclareOptions {
                        passive: true,
                        durable: true,
                        ..Default::default()
                    },
                    FieldTable::default(),
                )
                .await;
            match declared {
                Ok(queue) => {
                    m.insert(q, json!(queue.message_count()));
                }
                Err(_) => {
                    ch = conn.create_channel().await?; // a passive miss closes the channel
                    m.insert(q, Value::Null);
                }
            }
        }
        let _ = conn.close(200, "read".into()).await;
        Ok(Value::Object(m))
    }
    .await;
    out.unwrap_or_else(|e| json!({"error": format!("{e}")}))
}

/// The `ask.received` topic's depth (high − low watermark), or `null` when
/// the rail does not answer — as `monitor._topic_depth`.
async fn topic_depth(w: &World) -> Value {
    let kafka = w.kafka.clone();
    let depth = tokio::task::spawn_blocking(move || -> Option<i64> {
        use rdkafka::consumer::{BaseConsumer, Consumer};
        let c: BaseConsumer = rdkafka::config::ClientConfig::new()
            .set("bootstrap.servers", &kafka)
            .set("group.id", format!("monitor-{}", token_hex(3)))
            .create()
            .ok()?;
        let (lo, hi) = c
            .fetch_watermarks(ASK_RECEIVED, 0, Duration::from_secs(3))
            .ok()?;
        Some(hi - lo)
    })
    .await
    .ok()
    .flatten();
    json!(depth)
}

/// The last harness run in this world (the snapshot's `harness`).
pub async fn last_harness(g: &Ground, scope: &str) -> Result<Value, RoadError> {
    let row = g
        .client()
        .query_opt(
            "SELECT template, version, passed, failed, ran_at FROM spine_harness_runs WHERE scope = \
             $1 ORDER BY ran_at DESC LIMIT 1",
            &[&scope],
        )
        .await?;
    Ok(row
        .map(|r| {
            json!({
                "template": r.get::<_, String>(0), "version": r.get::<_, String>(1),
                "passed": r.get::<_, i32>(2), "failed": r.get::<_, i32>(3),
                "ran_at": isoformat(r.get::<_, SystemTime>(4)),
            })
        })
        .unwrap_or(Value::Null))
}

fn as_f64(v: &Value) -> f64 {
    v.as_f64().unwrap_or(0.0)
}

/// The Operating State, live, for this world — `monitor.snapshot`, field for
/// field: the rails read only when `rails` is asked (the door asks; the judge
/// does not).
pub async fn snapshot(g: &Ground, w: &World, rails: bool) -> Result<Value, RoadError> {
    let scope = &w.scope;
    let mut asks = Map::new();
    for r in g
        .client()
        .query(
            "SELECT status, count(*) FROM spine_asks WHERE scope = $1 GROUP BY status",
            &[&scope],
        )
        .await?
    {
        asks.insert(r.get::<_, String>(0), json!(r.get::<_, i64>(1)));
    }
    let bodies = presence::roster(g, scope).await?;
    let alive = bodies.iter().filter(|b| b["alive"] == json!(true)).count();
    let lag = outbox_lag(g).await?;
    let last = last_harness(g, scope).await?;
    let values = json!({
        "outbox_pending": lag.pending,
        "oldest_outbox_age_s": lag.oldest_age_s.unwrap_or(0.0),
        "asks_received": asks.get("received").and_then(Value::as_i64).unwrap_or(0),
        "bodies_alive": alive,
        "bodies_dormant": bodies.len() - alive,
    });
    let rows = g
        .client()
        .query(
            "SELECT watch_id, name, metric, op, threshold, added_by, last_ok, since FROM \
             spine_watches WHERE scope = $1 ORDER BY added_at",
            &[&scope],
        )
        .await?;
    let mut watches = Vec::new();
    for r in rows {
        let (metric, op): (String, String) = (r.get(2), r.get(3));
        let threshold: f64 = r.get(4);
        let value = values[&metric].clone();
        let red = judge_one(&op, as_f64(&value), threshold).unwrap_or(false);
        let last_ok: Option<bool> = r.get(6);
        let since: Option<SystemTime> = r.get(7);
        // `since`: when the RECORDED state last turned (judge writes it) — shown
        // only while the record agrees with the metric now
        let recorded_red = last_ok.map(|ok| !ok);
        let since_v = if recorded_red == Some(red) {
            iso_opt(since)
        } else {
            Value::Null
        };
        let thr = json!(threshold);
        let mut d = json!({
            "watch_id": r.get::<_, String>(0), "name": r.get::<_, String>(1),
            "metric": metric, "op": op, "threshold": thr,
            "added_by": r.get::<_, String>(5), "value": value,
            "red": red, "ok": !red, "state": watch::state(red), "since": since_v,
        });
        d["reads"] = json!(reads(
            d["metric"].as_str().unwrap_or_default(),
            d["op"].as_str().unwrap_or_default(),
            &d["threshold"],
            &d["value"],
            red
        ));
        watches.push(d);
    }
    let names: Vec<String> = bodies
        .iter()
        .map(|b| b["name"].as_str().unwrap_or_default().to_string())
        .collect();
    Ok(json!({
        "world": scope,
        "outbox": {"pending": lag.pending, "oldest_age_s": lag.oldest_age_s},
        "asks": Value::Object(asks),
        "bodies": bodies,
        "values": values,
        "watches": watches,
        "benches": if rails { benches(w, &names).await } else { json!({}) },
        "topic_depth": if rails { topic_depth(w).await } else { Value::Null },
        "harness": last,
    }))
}

/// Every watch judged against its metric NOW; the ones whose state CHANGED
/// are recorded — `last_ok` and `since` on the row, and a
/// `orreth.watch.turned.v1` fact through the outbox — and returned, each with
/// `to` and `from` (`null` when first judged). A standing red records nothing
/// and returns nothing; a watch first judged red is a red transition (born
/// red is news). Runs under the intent beat.
pub async fn judge(g: &mut Ground, w: &World) -> Result<Vec<Value>, RoadError> {
    let snap = snapshot(g, w, false).await?;
    let mut turned = Vec::new();
    for wv in snap["watches"].as_array().cloned().unwrap_or_default() {
        let wid = wv["watch_id"].as_str().unwrap_or_default().to_string();
        let ok = wv["ok"].as_bool().unwrap_or(true);
        let was_ok: Option<bool> = g
            .client()
            .query_opt(
                "SELECT last_ok FROM spine_watches WHERE watch_id = $1",
                &[&wid],
            )
            .await?
            .and_then(|r| r.get(0));
        if was_ok.is_some_and(|w| w == ok) {
            continue; // standing: nothing turned
        }
        if was_ok.is_none() && ok {
            g.client() // first judged green: recorded, no turn
                .execute(
                    "UPDATE spine_watches SET last_ok = true, since = clock_timestamp() WHERE \
                     watch_id = $1",
                    &[&wid],
                )
                .await?;
            continue;
        }
        let from = was_ok.map(|w| if w { "green" } else { "red" });
        let to = wv["state"].as_str().unwrap_or_default().to_string();
        let payload = turned_payload(
            &wid,
            wv["name"].as_str().unwrap_or_default(),
            wv["metric"].as_str().unwrap_or_default(),
            wv["op"].as_str().unwrap_or_default(),
            &wv["threshold"],
            &wv["value"],
            from,
            &to,
        );
        let e = Mint {
            kind: "event".into(),
            r#type: WATCH_TURNED.into(),
            universe_id: w.scope.clone(),
            scope_path: w.scope.clone(),
            payload,
            correlation_id: Some(wid.clone()),
            authority_chain: Some(vec!["the kernel".into()]),
            ..Default::default()
        }
        .mint()?;
        let raw = envelope::encode(&e)?;
        let mid = e["message_id"].as_str().unwrap_or_default().to_string();
        let wid2 = wid.clone();
        let since = std::sync::Arc::new(std::sync::Mutex::new(None::<SystemTime>));
        let since2 = since.clone();
        outbox::commit_with_outbox(g, &raw, &mid, None, async move |tx| {
            let r = tx
                .query_one(
                    "UPDATE spine_watches SET last_ok = $1, since = clock_timestamp() WHERE watch_id \
                     = $2 RETURNING since",
                    &[&ok, &wid2],
                )
                .await?;
            *since2.lock().unwrap_or_else(|p| p.into_inner()) = Some(r.get(0));
            Ok(())
        })
        .await?;
        let mut d = wv.clone();
        d["since"] = iso_opt(*since.lock().unwrap_or_else(|p| p.into_inner()));
        d["to"] = json!(to);
        d["from"] = json!(from);
        turned.push(d);
    }
    Ok(turned)
}
