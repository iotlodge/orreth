// PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp2, the ground and the rails · 2026-09-22
// Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch row 4, re-base sp1: POISON-PARKING — the dispatcher parks a poison with its evidence and HOLDS at it until a person advances it · 2026-09-28
//! The durable inbox — mirrors `orreth_spine.inbox` (canon 0002, laws 3 and
//! 4). Delivery is at-least-once; EFFECTS are once. A consumer records the
//! message id it acted on in the same transaction as the effect, so a
//! redelivery finds its own footprint and steps around it. Ordering is per
//! aggregate, never global: a stale sequence is recorded and skipped, the
//! next applies, and a GAP refuses to guess.
//!
//! The tables are the Python spine's `spine_inbox` and
//! `spine_aggregate_cursor`, word for word.

use crate::ask::{
    advanced_payload, body_hash, parked_payload, parked_ref, parked_words, INBOX_ADVANCED,
    INBOX_PARKED,
};
use crate::envelope::{self, Mint};
use crate::ground::Ground;
use crate::outbox;
use crate::rail_error::RailError;
use crate::rails::{inbox_route, InboxRoute};
use crate::world::isoformat;
use serde_json::{json, Value};
use std::fmt;
use std::time::SystemTime;
use tokio_postgres::Transaction;

/// The kernel's own name on a fact it minted (the projector's chain).
pub const KERNEL: &str = "the kernel";

pub use crate::schema::INBOX_DDL as DDL;

pub async fn ensure_schema(g: &mut Ground) -> Result<(), RailError> {
    g.ensure("inbox", DDL).await.map(|_| ())
}

/// What the inbox did with a delivery.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Outcome {
    Applied,
    Duplicate,
    Stale,
}

impl fmt::Display for Outcome {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        f.write_str(match self {
            Outcome::Applied => "applied",
            Outcome::Duplicate => "duplicate",
            Outcome::Stale => "stale",
        })
    }
}

/// The footprint: the row claimed → `true`; a duplicate bumps attempts → `false`.
async fn claim(tx: &Transaction<'_>, consumer: &str, message_id: &str) -> Result<bool, RailError> {
    let claimed = tx
        .query_opt(
            "INSERT INTO spine_inbox (consumer, message_id) VALUES ($1, $2) ON CONFLICT \
             (consumer, message_id) DO NOTHING RETURNING message_id",
            &[&consumer, &message_id],
        )
        .await?;
    if claimed.is_none() {
        tx.execute(
            "UPDATE spine_inbox SET attempts = attempts + 1 WHERE consumer = $1 AND message_id = \
             $2",
            &[&consumer, &message_id],
        )
        .await?;
        return Ok(false);
    }
    Ok(true)
}

async fn done(tx: &Transaction<'_>, consumer: &str, message_id: &str) -> Result<(), RailError> {
    tx.execute(
        "UPDATE spine_inbox SET status = 'done' WHERE consumer = $1 AND message_id = $2",
        &[&consumer, &message_id],
    )
    .await?;
    Ok(())
}

/// Run `effect` exactly once per (consumer, message id). The footprint and
/// the effect share one transaction: if the effect fails, the footprint
/// rolls back too and a redelivery retries clean.
pub async fn apply_once<F>(
    g: &mut Ground,
    consumer: &str,
    message_id: &str,
    effect: F,
) -> Result<Outcome, RailError>
where
    F: for<'t, 'c> AsyncFnOnce(&'t Transaction<'c>) -> Result<(), RailError>,
{
    let tx = g.client_mut().transaction().await?;
    if !claim(&tx, consumer, message_id).await? {
        tx.commit().await?;
        return Ok(Outcome::Duplicate);
    }
    effect(&tx).await?;
    done(&tx, consumer, message_id).await?;
    tx.commit().await?;
    Ok(Outcome::Applied)
}

/// `apply_once` plus the ordering law for envelopes wearing an aggregate
/// `{id, sequence}`: stale sequences are recorded and skipped, the next
/// sequence applies and advances the cursor, and a gap refuses inside a
/// rolled-back transaction (`RailError::Gap`).
pub async fn apply_event<F>(
    g: &mut Ground,
    consumer: &str,
    env: &Value,
    effect: F,
) -> Result<Outcome, RailError>
where
    F: for<'t, 'c> AsyncFnOnce(&'t Transaction<'c>) -> Result<(), RailError>,
{
    let (message_id, aggregate_id, sequence) = match inbox_route(env) {
        InboxRoute::Once { message_id } => {
            return apply_once(g, consumer, &message_id, effect).await;
        }
        InboxRoute::Sequenced {
            message_id,
            aggregate_id,
            sequence,
        } => (message_id, aggregate_id, sequence),
    };
    let tx = g.client_mut().transaction().await?;
    tx.execute(
        "INSERT INTO spine_aggregate_cursor (consumer, aggregate_id) VALUES ($1, $2) ON \
         CONFLICT DO NOTHING",
        &[&consumer, &aggregate_id],
    )
    .await?;
    let last: i64 = tx
        .query_one(
            "SELECT last_sequence FROM spine_aggregate_cursor WHERE consumer = $1 AND \
             aggregate_id = $2 FOR UPDATE",
            &[&consumer, &aggregate_id],
        )
        .await?
        .get(0);
    if sequence <= last {
        tx.execute(
            "INSERT INTO spine_inbox (consumer, message_id, status) VALUES ($1, $2, 'stale') ON \
             CONFLICT (consumer, message_id) DO UPDATE SET attempts = spine_inbox.attempts + 1",
            &[&consumer, &message_id],
        )
        .await?;
        tx.commit().await?;
        return Ok(Outcome::Stale);
    }
    if sequence > last + 1 {
        drop(tx); // rolled back: nothing recorded, the caller fetches what is missing
        return Err(RailError::Gap {
            aggregate_id,
            expected: last + 1,
            got: sequence,
        });
    }
    if !claim(&tx, consumer, &message_id).await? {
        tx.commit().await?;
        return Ok(Outcome::Duplicate);
    }
    effect(&tx).await?;
    tx.execute(
        "UPDATE spine_aggregate_cursor SET last_sequence = $1 WHERE consumer = $2 AND \
         aggregate_id = $3",
        &[&sequence, &consumer, &aggregate_id],
    )
    .await?;
    done(&tx, consumer, &message_id).await?;
    tx.commit().await?;
    Ok(Outcome::Applied)
}

// ---- THE PARKED (re-base sp1): a poison's evidence, the hold, the operator's word --------

/// PARK a poison event with its evidence — the row and its fact
/// (`orreth.inbox.parked.v1`) in one transaction, once per PLACE on the rail: a
/// restart that re-reads the same offset finds the row and parks nothing twice.
/// Returns the parked id and whether this call wrote it. The reason is cut at
/// 500 characters as the reference cuts it.
#[allow(clippy::too_many_arguments)]
pub async fn park(
    g: &mut Ground,
    scope: &str,
    consumer: &str,
    topic: &str,
    partition: i32,
    offset: i64,
    body: &[u8],
    reason: &str,
) -> Result<(i64, bool), RailError> {
    let reason: String = reason.chars().take(500).collect();
    if let Some(r) = g
        .client()
        .query_opt(
            "SELECT parked_id FROM spine_parked WHERE consumer = $1 AND topic = $2 AND partition = \
             $3 AND kafka_offset = $4 ORDER BY parked_id LIMIT 1",
            &[&consumer, &topic, &partition, &offset],
        )
        .await?
    {
        return Ok((r.get(0), false));
    }
    let tx = g.client_mut().transaction().await?;
    let id: i64 = tx
        .query_one(
            "INSERT INTO spine_parked (consumer, topic, partition, kafka_offset, body, reason) \
             VALUES ($1, $2, $3, $4, $5, $6) RETURNING parked_id",
            &[&consumer, &topic, &partition, &offset, &body, &reason],
        )
        .await?
        .get(0);
    let e = Mint {
        kind: "event".into(),
        r#type: INBOX_PARKED.into(),
        universe_id: scope.into(),
        scope_path: scope.into(),
        payload: parked_payload(
            id,
            consumer,
            topic,
            partition,
            offset,
            &body_hash(body),
            &reason,
        ),
        correlation_id: Some(parked_ref(id)),
        authority_chain: Some(vec![KERNEL.into()]),
        ..Default::default()
    }
    .mint()?;
    outbox::add_row(
        &tx,
        &envelope::encode(&e)?,
        e["message_id"].as_str().unwrap_or_default(),
    )
    .await?;
    tx.commit().await?;
    Ok((id, true))
}

/// The hold's question: has a person advanced past this parked event?
pub async fn advanced(g: &Ground, parked_id: i64) -> Result<bool, RailError> {
    let row = g
        .client()
        .query_opt(
            "SELECT advanced_at IS NOT NULL FROM spine_parked WHERE parked_id = $1",
            &[&parked_id],
        )
        .await?;
    Ok(row.is_some_and(|r| r.get::<_, bool>(0)))
}

/// THE OPERATOR'S WORD: advance past a parked event — recorded on the row with who
/// and when, and said as `orreth.inbox.advanced.v1`; the holding consumer commits the
/// offset on its next look. `None` when no such event was parked; an event already
/// advanced answers with `already: true` and mints nothing twice.
pub async fn advance(
    g: &mut Ground,
    scope: &str,
    parked_id: i64,
    by: &str,
) -> Result<Option<Value>, RailError> {
    let Some(r) = g
        .client()
        .query_opt(
            "SELECT consumer, topic, partition, kafka_offset, advanced_by, advanced_at FROM \
             spine_parked WHERE parked_id = $1",
            &[&parked_id],
        )
        .await?
    else {
        return Ok(None);
    };
    let (consumer, topic, partition, offset): (String, Option<String>, Option<i32>, Option<i64>) =
        (r.get(0), r.get(1), r.get(2), r.get(3));
    if let Some(at) = r.get::<_, Option<SystemTime>>(5) {
        return Ok(Some(
            json!({"parked_id": parked_id, "advanced": true, "already": true,
                              "advanced_by": r.get::<_, Option<String>>(4), "advanced_at": isoformat(at)}),
        ));
    }
    let tx = g.client_mut().transaction().await?;
    let at: SystemTime = tx
        .query_one(
            "UPDATE spine_parked SET advanced_by = $1, advanced_at = now() WHERE parked_id = $2 \
             RETURNING advanced_at",
            &[&by, &parked_id],
        )
        .await?
        .get(0);
    let e = Mint {
        kind: "event".into(),
        r#type: INBOX_ADVANCED.into(),
        universe_id: scope.into(),
        scope_path: scope.into(),
        payload: advanced_payload(
            parked_id,
            &consumer,
            topic.as_deref().unwrap_or_default(),
            partition.unwrap_or_default(),
            offset.unwrap_or_default(),
            by,
        ),
        correlation_id: Some(parked_ref(parked_id)),
        authority_chain: Some(vec![by.into()]),
        ..Default::default()
    }
    .mint()?;
    outbox::add_row(
        &tx,
        &envelope::encode(&e)?,
        e["message_id"].as_str().unwrap_or_default(),
    )
    .await?;
    tx.commit().await?;
    Ok(Some(
        json!({"parked_id": parked_id, "advanced": true, "already": false,
                   "advanced_by": by, "advanced_at": isoformat(at), "message_id": e["message_id"]}),
    ))
}

/// The parked events still HELD (not advanced), newest first — of one consumer or
/// of every consumer; each with its place, its reason, the evidence's size and hash,
/// and plain words.
pub async fn parked(
    g: &Ground,
    consumer: Option<&str>,
    limit: i64,
) -> Result<Vec<Value>, RailError> {
    let rows = g
        .client()
        .query(
            "SELECT parked_id, consumer, topic, partition, kafka_offset, body, reason, parked_at \
             FROM spine_parked WHERE advanced_at IS NULL AND ($1::text IS NULL OR consumer = $1) \
             ORDER BY parked_id DESC LIMIT $2",
            &[&consumer, &limit],
        )
        .await?;
    Ok(rows
        .iter()
        .map(|r| {
            let (id, consumer, reason): (i64, String, String) = (r.get(0), r.get(1), r.get(6));
            let topic = r.get::<_, Option<String>>(2).unwrap_or_default();
            let partition = r.get::<_, Option<i32>>(3).unwrap_or_default();
            let offset = r.get::<_, Option<i64>>(4).unwrap_or_default();
            let body = r.get::<_, Option<Vec<u8>>>(5).unwrap_or_default();
            json!({
                "parked_id": id, "ref": parked_ref(id), "consumer": consumer, "topic": topic,
                "partition": partition, "offset": offset, "reason": reason,
                "parked_at": isoformat(r.get::<_, SystemTime>(7)),
                "bytes": body.len(), "hash": body_hash(&body),
                "words": parked_words(&consumer, &topic, partition, offset, &reason),
            })
        })
        .collect())
}

/// How many parked events a consumer still holds at (the watchable `parked`).
pub async fn parked_count(g: &Ground, consumer: &str) -> Result<i64, RailError> {
    let row = g
        .client()
        .query_one(
            "SELECT count(*) FROM spine_parked WHERE consumer = $1 AND advanced_at IS NULL",
            &[&consumer],
        )
        .await?;
    Ok(row.get(0))
}

/// The honest duplicate meter: redeliveries absorbed without effect.
pub async fn duplicates_seen(g: &Ground, consumer: &str) -> Result<i64, RailError> {
    let row = g
        .client()
        .query_one(
            "SELECT coalesce(sum(attempts - 1), 0)::bigint FROM spine_inbox WHERE consumer = $1",
            &[&consumer],
        )
        .await?;
    Ok(row.get(0))
}
