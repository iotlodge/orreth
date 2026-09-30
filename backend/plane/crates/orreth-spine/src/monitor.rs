// PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp4, the loops · 2026-09-23
// Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch row 4, PANEL sp3: the doors' latency and the pool in the snapshot · 2026-09-28
// Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp7, cells: the Operating State names the cell and epoch · 2026-09-25
// Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch row 4, re-base sp1: POISON-PARKING — the dispatcher parks a poison with its evidence and HOLDS at it until a person advances it · 2026-09-28
// Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch row 4, the perf cure before sp2 (JB's word 2026-09-29): the topic's depth read on ONE held broker client — never a fresh client (a full-metadata fetch) per snapshot · 2026-09-29
// Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch row 4, the honest glass (JB's screenshots 2026-09-29): the farm's six values and THE STABLE's face ported from the reference (the pulse read $0 over a metered crew — nine values where the reference carries fifteen); the meter read BY WORLD on both; the roster folded one row per name · 2026-09-29
// Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch row 4, the honest glass sp2 (W86): THE WATCH'S REST — `rest_watch` recorded on the row (schema 3), the judge and the snapshot read the ACTIVE watches; the asks left WAITING listed in the snapshot for their stop · 2026-09-29
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

/// The human's stop of a watch (the honest glass sp2, W86 — rule 11): recorded on the row —
/// `active` false, who rested it, when — never a delete; the judge and the snapshot read the
/// active watches alone, so a rested watch turns no intention and draws no red. Modeled on
/// `scheduler::rest`. `Ok(None)` — no such watch here; else the row's name, author and
/// whether it was already at rest.
pub async fn rest_watch(
    g: &Ground,
    scope: &str,
    watch_id: &str,
    by: &str,
) -> Result<Option<Value>, RoadError> {
    let row = g
        .client()
        .query_opt(
            "SELECT name, added_by, active FROM spine_watches WHERE watch_id = $1 AND scope = $2",
            &[&watch_id, &scope],
        )
        .await?;
    let Some(row) = row else {
        return Ok(None);
    };
    let (name, added_by, active): (String, String, bool) = (row.get(0), row.get(1), row.get(2));
    if active {
        g.client()
            .execute(
                "UPDATE spine_watches SET active = false, rested_by = $1, rested_at = now() WHERE \
                 watch_id = $2",
                &[&by, &watch_id],
            )
            .await?;
    }
    Ok(Some(json!({
        "watch_id": watch_id, "name": name, "added_by": added_by, "rested_by": by, "already": !active,
    })))
}

/// The asks left WAITING in this world (status `received`, nobody serving yet), newest first
/// — each one a person can stop (the honest glass sp2, W86: seven of nine received asks were
/// the watch loop's own orphaned objectives, and the ASKS card showed a count with no way to
/// reach them). Field for field the reference's `monitor.waiting`.
pub async fn waiting(g: &Ground, scope: &str, limit: i64) -> Result<Vec<Value>, RoadError> {
    let rows = g
        .client()
        .query(
            "SELECT ask_id, text, person, target, asked_at FROM spine_asks WHERE scope = $1 AND \
             status = 'received' ORDER BY asked_at DESC LIMIT $2",
            &[&scope, &limit],
        )
        .await?;
    Ok(rows
        .iter()
        .map(|r| {
            let text: String = r.get(1);
            json!({
                "ask_id": r.get::<_, String>(0), "text": text.chars().take(140).collect::<String>(),
                "person": r.get::<_, String>(2), "target": r.get::<_, Option<String>>(3),
                "asked_at": isoformat(r.get::<_, SystemTime>(4)),
            })
        })
        .collect())
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
    use rdkafka::consumer::{BaseConsumer, Consumer};
    use std::sync::{Mutex, OnceLock};
    // the perf cure (2026-09-29): ONE client for the process's life — a fresh client per snapshot
    // fetched the broker's whole metadata each time (400–700 ms against five thousand topics, every
    // five seconds while the Monitoring was open) and left a ghost group behind
    static HELD: OnceLock<Mutex<Option<(String, BaseConsumer)>>> = OnceLock::new();
    let kafka = w.kafka.clone();
    let depth = tokio::task::spawn_blocking(move || -> Option<i64> {
        let held = HELD.get_or_init(|| Mutex::new(None));
        let mut slot = held.lock().unwrap_or_else(|p| p.into_inner());
        if slot.as_ref().is_none_or(|(b, _)| *b != kafka) {
            let c: BaseConsumer = rdkafka::config::ClientConfig::new()
                .set("bootstrap.servers", &kafka)
                .set("group.id", "monitor-depth")
                .create()
                .ok()?;
            *slot = Some((kafka.clone(), c));
        }
        let (lo, hi) = slot
            .as_ref()?
            .1
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

/// P6.5 sp3's farm metrics, ported (the honest glass, 2026-09-29): the Stable's numbers off
/// THIS world's ground — minds standing and unhealthy, dollars today, route failures in the
/// last hour, the meter's rate over ten minutes, bodies out of fuel. Field for field the
/// reference's `_farm`, with one law both now keep: the meter is read BY SCOPE — the pulse
/// says "world u:dev", so its dollars are that world's and no other's.
async fn farm(g: &Ground, scope: &str) -> Result<Value, RoadError> {
    let mut out = json!({"minds_standing": 0, "minds_unhealthy": 0, "usd_today": 0.0,
                         "route_failures_1h": 0, "meter_rate_10m": 0.0, "bodies_drained": 0});
    if crate::schema::has_table(g, "spine_services").await? {
        let r = g
            .client()
            .query_one(
                "SELECT count(*) FILTER (WHERE state IN ('registered','versioned','healthy')), count(*) \
                 FILTER (WHERE state = 'unhealthy') FROM spine_services WHERE scope = $1 AND kind = 'mind'",
                &[&scope],
            )
            .await?;
        out["minds_standing"] = json!(r.get::<_, i64>(0));
        out["minds_unhealthy"] = json!(r.get::<_, i64>(1));
    }
    if crate::schema::has_table(g, "spine_meter").await? {
        let r = g
            .client()
            .query_one(
                "SELECT coalesce(sum(usd) FILTER (WHERE at >= date_trunc('day', now())), 0)::float8, \
                 count(*) FILTER (WHERE ok = false AND at >= now() - interval '1 hour'), count(*) FILTER \
                 (WHERE at >= now() - interval '10 minutes') FROM spine_meter WHERE scope = $1",
                &[&scope],
            )
            .await?;
        let usd: f64 = r.get(0);
        out["usd_today"] = json!((usd * 1e6).round() / 1e6);
        out["route_failures_1h"] = json!(r.get::<_, i64>(1));
        out["meter_rate_10m"] = json!((r.get::<_, i64>(2) as f64 / 10.0 * 100.0).round() / 100.0);
    }
    if crate::schema::has_table(g, "spine_mind_keys").await? {
        let r = g
            .client()
            .query_one(
                "SELECT count(*) FROM spine_mind_keys WHERE scope = $1 AND drained_at IS NOT NULL",
                &[&scope],
            )
            .await?;
        out["bodies_drained"] = json!(r.get::<_, i64>(0));
    }
    Ok(out)
}

/// THE STABLE's face (P6.5 sp3, ported): each mind's words and spend, the assignments —
/// the reference's `_stable`; the face never breaks the snapshot.
async fn stable_face(g: &Ground, scope: &str) -> Value {
    if !matches!(
        crate::schema::has_table(g, "spine_services").await,
        Ok(true)
    ) {
        return json!({"minds": [], "assignments": []});
    }
    let out: Result<Value, RoadError> = async {
        let minds: Vec<Value> = crate::stable_live::stalls(g, scope)
            .await?
            .iter()
            .map(|s| {
                json!({
                    "name": s["name"], "state": s["state"], "words": crate::stable::stall_words(s),
                    "spend": s.get("spend").cloned().unwrap_or(Value::Null),
                    "last": s.get("last_health").and_then(|h| h.get("detail")).cloned()
                        .or_else(|| s.get("last_detail").cloned()).unwrap_or(Value::Null),
                })
            })
            .collect();
        Ok(json!({"minds": minds, "assignments": crate::stable_live::assignments(g.client(), scope).await?}))
    }
    .await;
    out.unwrap_or_else(|e| json!({"minds": [], "assignments": [], "error": format!("{e}")}))
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
    // row 4, panel sp3: the doors this process served (their p50 · p95 over the window) and
    // the pool's strain — read in-process, so the judge and the levers see what the door shows
    let doors = crate::doors::read();
    let pool = crate::pool::read_all();
    // re-base sp1: the poison events the dispatcher holds at (the ground's count — the same
    // on both kernels), watchable as `parked`
    let parked = crate::inbox::parked(g, Some(crate::dispatcher::CONSUMER), 20).await?;
    let mut values = json!({
        "parked": parked.len(),
        "outbox_pending": lag.pending,
        "oldest_outbox_age_s": lag.oldest_age_s.unwrap_or(0.0),
        "asks_received": asks.get("received").and_then(Value::as_i64).unwrap_or(0),
        "bodies_alive": alive,
        "bodies_dormant": bodies.len() - alive,
        "door_p95_ms": crate::doors::slowest_p95(&doors),
        "pool_busy": pool.as_ref().and_then(|p| p["busy"].as_u64()).unwrap_or(0),
        "pool_waiting": pool.as_ref().and_then(|p| p["waiting"].as_u64()).unwrap_or(0),
    });
    // the honest glass (2026-09-29): the farm's six — the pulse had read $0 over a metered crew
    if let Some(m) = farm(g, scope).await?.as_object() {
        for (k, v) in m {
            values[k] = v.clone();
        }
    }
    let stable_view = stable_face(g, scope).await;
    let rows = g
        .client()
        .query(
            "SELECT watch_id, name, metric, op, threshold, added_by, last_ok, since FROM \
             spine_watches WHERE scope = $1 AND active ORDER BY added_at",
            &[&scope],
        )
        .await?; // sp2: the active alone — a rested watch turns nothing and draws no red
    let rested: i64 = g
        .client()
        .query_one(
            "SELECT count(*) FROM spine_watches WHERE scope = $1 AND NOT active",
            &[&scope],
        )
        .await?
        .get(0);
    let waiting = waiting(g, scope, 20).await?;
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
    // P7 sp7: the cell and epoch this universe stands in (the world card's words)
    let home = if crate::schema::has_table(g, "spine_world").await? {
        g.client()
            .query_opt(
                "SELECT cell, epoch FROM spine_world WHERE scope = $1",
                &[&scope],
            )
            .await?
    } else {
        None
    };
    let home = json!({
        "cell": home.as_ref().map(|r| r.get::<_, String>(0)).unwrap_or_else(crate::cells_live::cell_here),
        "epoch": home.as_ref().map(|r| r.get::<_, i32>(1)),
        "namespace": w.ns,
    });
    Ok(json!({
        "world": scope,
        "home": home,
        "outbox": {"pending": lag.pending, "oldest_age_s": lag.oldest_age_s},
        "asks": Value::Object(asks),
        "bodies": bodies,
        "values": values,
        "watches": watches,
        "watches_rested": rested, // sp2 (W86): how many watches a person has rested here
        "waiting": waiting,       // sp2 (W86): the asks left waiting, each with its stop
        "benches": if rails { benches(w, &names).await } else { json!({}) },
        "topic_depth": if rails { topic_depth(w).await } else { Value::Null },
        "harness": last,
        "stable": stable_view,
        "doors": doors,
        "pool": pool,
        "parked": parked,
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
