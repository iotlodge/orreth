// PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — W91 THE BENCH SWEEP · 2026-10-02
//! THE BENCH SWEEP (W91, walk #21 — JB's COMPLIANT-STATE principle: every
//! residue is a queue the kernel drives to compliance). Six asks waited for
//! DAYS on the dev ground: each dispatched once, its command returned by the
//! broker and read as delivered (part a cured that), and no beat ever looked
//! at the bench again. Now a kernel beat does: an ask still `received` after
//! `SPINE_BENCH_SWEEP_S` seconds (default 90) with nobody serving it is
//! DISPATCHED AGAIN, ONCE — a new serve command on the same road, a journey
//! line saying so, `resent_at` on the row (a resident never re-serves a
//! settled ask: the conditional-transition law, `resident._serve_ask`). Still
//! `received` the same span after that: the kernel RESTS it with plain words
//! as its reply (cancelled · the kernel as its server · the reply on the
//! rail) — the person sees it in the chat, not a count. Mirrors
//! `dispatch.sweep_bench`.

use crate::ask::{rested_words, swept_words, KERNEL};
use crate::asks::{command_for, fact_now, next_seq, ASK_RECEIVED, JOURNEY, REPLY};
use crate::envelope::{self, Mint};
use crate::ground::Ground;
use crate::hash::content_hash;
use crate::outbox;
use crate::world::{RoadError, World};
use crate::{invoke, py};
use serde_json::{json, Value};
use std::time::Duration;

/// `SPINE_BENCH_SWEEP_S`: how long an ask may sit `received` with no body
/// serving it before the kernel dispatches it again (and, the same span
/// later, rests it). Default 90 s; 0 or an unreadable value reads as the default.
pub fn sweep_after() -> Duration {
    let s = std::env::var("SPINE_BENCH_SWEEP_S")
        .ok()
        .and_then(|v| v.trim().parse::<u64>().ok())
        .filter(|s| *s > 0)
        .unwrap_or(90);
    Duration::from_secs(s)
}

/// One ask left waiting, as the sweep reads it.
struct Waiting {
    ask_id: String,
    text: String,
    person: String,
    target: Option<String>,
    fanout: Option<String>,
    session: Option<String>,
    window: Option<String>,
    /// already dispatched again once
    again: bool,
    /// seconds since it was received
    waited: i64,
}

/// One sweep of this world's bench: every ask `received` longer than
/// `older_than` and not yet re-dispatched is dispatched again, once; one
/// re-dispatched that long ago and still `received` is rested. Returns
/// `{"resent": [ids], "rested": [ids]}`.
pub async fn sweep(g: &mut Ground, w: &World, older_than: Duration) -> Result<Value, RoadError> {
    let secs = older_than.as_secs_f64();
    let rows = g
        .client()
        .query(
            "SELECT ask_id, text, person, target, fanout, session, time_window, resent_at IS NOT NULL, \
             floor(extract(epoch FROM (clock_timestamp() - asked_at)))::int8 FROM spine_asks WHERE scope = $1 \
             AND status = 'received' AND asked_at < clock_timestamp() - $2 * interval '1 second' AND \
             (resent_at IS NULL OR resent_at < clock_timestamp() - $2 * interval '1 second') ORDER BY \
             asked_at LIMIT 50",
            &[&w.scope, &secs],
        )
        .await?;
    let found: Vec<Waiting> = rows
        .iter()
        .map(|r| Waiting {
            ask_id: r.get(0),
            text: r.get(1),
            person: r.get(2),
            target: r.get(3),
            fanout: r.get(4),
            session: r.get(5),
            window: r.get(6),
            again: r.get(7),
            waited: r.get(8),
        })
        .collect();
    let (mut resent, mut rested) = (Vec::new(), Vec::new());
    for Waiting {
        ask_id,
        text,
        person,
        target,
        fanout,
        session,
        window,
        again,
        waited,
    } in found
    {
        if !again {
            // the first miss: the same road once more — the command minted from the ask row as the
            // door minted it, published (part a: a return is a refusal, never a delivery), then the
            // row and its journey line in one transaction
            let window: Option<Value> =
                window.as_deref().and_then(|t| serde_json::from_str(t).ok());
            let win = window
                .as_ref()
                .and_then(|v| Some((v["from"].as_str()?, v["to"].as_str()?)));
            let payload = crate::ask::received_payload(
                &ask_id,
                &text,
                target.as_deref(),
                session.as_deref(),
                win,
            );
            let fact = fact_now(
                ASK_RECEIVED,
                &w.scope,
                &ask_id,
                payload,
                fanout.as_deref(),
                &[&person],
                &Value::Null,
            );
            let cmd = command_for(&fact)?;
            invoke::publish_command(&w.rabbit_url, &cmd, &w.ns).await?;
            let tx = g.client_mut().transaction().await?;
            tx.execute(
                "UPDATE spine_asks SET resent_at = clock_timestamp() WHERE ask_id = $1",
                &[&ask_id],
            )
            .await?;
            journey(&tx, w, &ask_id, &swept_words(waited), &[KERNEL.to_string()]).await?;
            tx.commit().await?;
            eprintln!(
                "  [kernel] bench sweep: {ask_id} dispatched again after {waited} s ({})",
                py::repr_str(&crate::memory::head(&text, 60))
            );
            resent.push(ask_id);
            continue;
        }
        // the second miss: the kernel rests it with plain words — the reply, the journey line and
        // the row in one transaction, the person reads it in the chat
        let words = rested_words(waited);
        let tx = g.client_mut().transaction().await?;
        tx.execute(
            "UPDATE spine_asks SET status = 'cancelled', reply = $1, served_by = $2, replied_at = \
             clock_timestamp() WHERE ask_id = $3",
            &[&words, &KERNEL, &ask_id],
        )
        .await?;
        let chain = vec![KERNEL.to_string()];
        journey(
            &tx,
            w,
            &ask_id,
            &format!("{KERNEL}: rested by the bench sweep — dispatched twice, no body took it in {waited} s (W91)"),
            &chain,
        )
        .await?;
        let seq = next_seq(&tx, &ask_id).await?;
        let r = Mint {
            kind: "event".into(),
            r#type: REPLY.into(),
            universe_id: w.scope.clone(),
            scope_path: w.scope.clone(),
            payload: json!({"ref": ask_id, "hash": content_hash(&Value::String(words.clone())), "proof": "L1"}),
            correlation_id: Some(ask_id.clone()),
            authority_chain: Some(chain),
            aggregate: Some(json!({"type": "ask", "id": ask_id, "sequence": seq})),
            ..Default::default()
        }
        .mint()?;
        outbox::add_row(
            &tx,
            &envelope::encode(&r)?,
            r["message_id"].as_str().unwrap_or_default(),
        )
        .await?;
        tx.commit().await?;
        eprintln!("  [kernel] bench sweep: {ask_id} rested — dispatched twice, no body took it in {waited} s");
        rested.push(ask_id);
    }
    Ok(json!({"resent": resent, "rested": rested}))
}

async fn journey(
    tx: &tokio_postgres::Transaction<'_>,
    w: &World,
    ask_id: &str,
    note: &str,
    chain: &[String],
) -> Result<(), RoadError> {
    let seq = next_seq(tx, ask_id).await?;
    let j = Mint {
        kind: "event".into(),
        r#type: JOURNEY.into(),
        universe_id: w.scope.clone(),
        scope_path: w.scope.clone(),
        payload: json!({"ref": ask_id, "hash": "sha256:-", "note": note}),
        correlation_id: Some(ask_id.to_string()),
        authority_chain: Some(chain.to_vec()),
        aggregate: Some(json!({"type": "ask", "id": ask_id, "sequence": seq})),
        ..Default::default()
    }
    .mint()?;
    outbox::add_row(
        tx,
        &envelope::encode(&j)?,
        j["message_id"].as_str().unwrap_or_default(),
    )
    .await?;
    Ok(())
}
