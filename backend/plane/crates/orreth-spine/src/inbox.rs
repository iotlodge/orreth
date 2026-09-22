// PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp2, the ground and the rails · 2026-09-22
//! The durable inbox — mirrors `orreth_spine.inbox` (canon 0002, laws 3 and
//! 4). Delivery is at-least-once; EFFECTS are once. A consumer records the
//! message id it acted on in the same transaction as the effect, so a
//! redelivery finds its own footprint and steps around it. Ordering is per
//! aggregate, never global: a stale sequence is recorded and skipped, the
//! next applies, and a GAP refuses to guess.
//!
//! The tables are the Python spine's `spine_inbox` and
//! `spine_aggregate_cursor`, word for word.

use crate::ground::Ground;
use crate::rail_error::RailError;
use crate::rails::{inbox_route, InboxRoute};
use serde_json::Value;
use std::fmt;
use tokio_postgres::Transaction;

pub const DDL: &[&str] = &[
    "CREATE TABLE IF NOT EXISTS spine_inbox ( consumer text NOT NULL, message_id text NOT NULL, \
     first_seen timestamptz NOT NULL DEFAULT now(), status text NOT NULL DEFAULT 'working', \
     attempts int NOT NULL DEFAULT 1, PRIMARY KEY (consumer, message_id))",
    "CREATE TABLE IF NOT EXISTS spine_aggregate_cursor ( consumer text NOT NULL, aggregate_id \
     text NOT NULL, last_sequence bigint NOT NULL DEFAULT 0, PRIMARY KEY (consumer, \
     aggregate_id))",
];

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
