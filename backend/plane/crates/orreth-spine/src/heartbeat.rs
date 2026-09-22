// PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp2, the ground and the rails · 2026-09-22
//! The rig's breath from Rust — mirrors `orreth_spine.heartbeat` and the
//! three breaths of `orreth_spine.rails`. Every breath is the same proof: an
//! envelope goes in, comes back, and the bytes match exactly. The ground
//! writes the heartbeat AND its outbox row in one transaction (law 2 from
//! the very first breath); the invoke rail publishes with confirms and acks
//! only after the bytes are verified; the events rail produces to the topic
//! and reads it back from the log. `all_rails` composes them into Phase 0's
//! whole proof: a fact on the ground → its outbox row → relayed to the
//! events rail → seen by a consumer → absorbed once by the inbox.

use crate::envelope::{self, Mint};
use crate::ground::Ground;
use crate::inbox::{self, Outcome};
use crate::outbox;
use crate::rail_error::RailError;
use crate::rails::{heartbeat_key, heartbeat_queue, HEARTBEAT_TOPIC};
use crate::sinks::KafkaSink;
use crate::{content_hash, events};
use serde_json::{json, Value};
use std::time::{Duration, Instant};

pub const DDL: &[&str] = &[
    "CREATE TABLE IF NOT EXISTS spine_heartbeat ( message_id text PRIMARY \
                            KEY, body bytea NOT NULL, committed_at timestamptz NOT NULL DEFAULT \
                            now())",
];

pub async fn ensure_schema(g: &mut Ground) -> Result<(), RailError> {
    g.ensure("heartbeat", DDL).await.map(|_| ())
}

/// One heartbeat envelope for a rail, as the Python heartbeat mints it.
pub fn beat(kind: &str, rail: &str, universe: &str, scope: &str) -> Value {
    Mint {
        kind: kind.into(),
        r#type: HEARTBEAT_TOPIC.into(),
        universe_id: universe.into(),
        scope_path: scope.into(),
        payload: json!({"ref": format!("heartbeat:{rail}"),
                        "hash": content_hash(&json!({"rail": rail}))}),
        authority_chain: Some(vec![
            "did:orreth:person:jb".into(),
            "did:orreth:agent:fable".into(),
        ]),
        ..Default::default()
    }
    .mint()
    .expect("a heartbeat is a complete envelope")
}

/// Postgres: heartbeat + outbox row in ONE transaction, read back exact.
pub async fn ground_breath(g: &mut Ground, env: &Value) -> Result<Duration, RailError> {
    let raw = envelope::encode(env)?;
    let message_id = env["message_id"].as_str().unwrap_or_default().to_string();
    let t0 = Instant::now();
    ensure_schema(g).await?;
    outbox::ensure_schema(g).await?;
    let (mid, body) = (message_id.clone(), raw.clone());
    outbox::commit_with_outbox(g, &raw, &message_id, None, async move |tx| {
        tx.execute(
            "INSERT INTO spine_heartbeat (message_id, body) VALUES ($1, $2) ON CONFLICT DO NOTHING",
            &[&mid, &body],
        )
        .await?;
        Ok(())
    })
    .await?;
    let back: Vec<u8> = g
        .client()
        .query_one(
            "SELECT body FROM spine_heartbeat WHERE message_id = $1",
            &[&message_id],
        )
        .await?
        .get(0);
    if back != raw {
        return Err(RailError::Refused(
            "the ground returned different bytes".into(),
        ));
    }
    Ok(t0.elapsed())
}

/// RabbitMQ: publish with confirms on the command exchange, consume, verify
/// the bytes, and only then acknowledge.
pub async fn invoke_breath(
    url: &str,
    env: &Value,
    ns: &str,
    timeout: Duration,
) -> Result<Duration, RailError> {
    let raw = envelope::encode(env)?;
    let t0 = Instant::now();
    let (queue, key) = (heartbeat_queue(ns), heartbeat_key(ns));
    crate::invoke::publish(
        url,
        &queue,
        &key,
        &raw,
        env["message_id"].as_str().unwrap_or_default(),
    )
    .await?;
    let back = crate::invoke::receive(url, &queue, &key, timeout, |b| b == raw).await?;
    if back != raw {
        return Err(RailError::Refused(
            "the invoke rail returned different bytes".into(),
        ));
    }
    Ok(t0.elapsed())
}

/// Kafka: produce to the heartbeat topic, read the log from the start with a
/// fresh group, and verify our exact bytes came back.
pub async fn events_breath(
    bootstrap: &str,
    env: &Value,
    timeout: Duration,
) -> Result<Duration, RailError> {
    let raw = envelope::encode(env)?;
    let message_id = env["message_id"].as_str().unwrap_or_default().to_string();
    let t0 = Instant::now();
    let mut sink = KafkaSink::new(bootstrap)?;
    outbox::Sink::publish(&mut sink, &message_id, &raw).await?;
    let group = format!(
        "spine-breath-{}",
        &message_id[message_id.len().saturating_sub(8)..]
    );
    let reader = events::Reader::open(bootstrap, &group, &[HEARTBEAT_TOPIC], true).await?;
    let back = reader
        .read_until(timeout, |e| e["message_id"].as_str() == Some(&message_id))
        .await?;
    if envelope::encode(&back)? != raw {
        return Err(RailError::Refused(
            "the events rail returned different bytes".into(),
        ));
    }
    Ok(t0.elapsed())
}

/// Phase 0's whole proof, composed: the fact lands on the ground with its
/// outbox row → the relay publishes it to the events rail → a consumer sees
/// it → the inbox absorbs it once (and the redelivery as a duplicate).
pub async fn all_rails(
    g: &mut Ground,
    bootstrap: &str,
    env: &Value,
    consumer: &str,
    timeout: Duration,
) -> Result<(Outcome, Outcome), RailError> {
    ground_breath(g, env).await?;
    let mut sink = KafkaSink::new(bootstrap)?;
    outbox::drain(g, &mut sink, timeout).await?;
    let message_id = env["message_id"].as_str().unwrap_or_default().to_string();
    let topic = env["type"].as_str().unwrap_or(HEARTBEAT_TOPIC).to_string();
    let reader = events::Reader::open(bootstrap, &format!("{consumer}-g"), &[&topic], true).await?;
    let seen = reader
        .read_until(timeout, |e| e["message_id"].as_str() == Some(&message_id))
        .await?;
    inbox::ensure_schema(g).await?;
    let first = inbox::apply_event(g, consumer, &seen, async |_tx| Ok(())).await?;
    let again = inbox::apply_event(g, consumer, &seen, async |_tx| Ok(())).await?;
    Ok((first, again))
}
