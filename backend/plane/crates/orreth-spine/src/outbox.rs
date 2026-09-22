// PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp2, the ground and the rails · 2026-09-22
//! The transactional outbox and its relay — mirrors `orreth_spine.outbox`
//! (canon 0002, law 2). Domain state and the intent to publish commit in ONE
//! Postgres transaction: a committed row can never lack its event, a
//! rolled-back row can never emit one, and success never depends on a
//! broker. The relay publishes after the fact, at-least-once: a death
//! between publish and mark publishes again, and the stable message id makes
//! the duplicate harmless downstream (the inbox). Backpressure is explicit:
//! at the declared budget, new writes refuse BY NAME.
//!
//! The table is the Python spine's `spine_outbox`, word for word.

use crate::ground::Ground;
use crate::rail_error::RailError;
use std::time::{Duration, Instant};
use tokio_postgres::Transaction;

/// The Python spine's DDL for the outbox, word for word (the heartbeat's
/// earlier, poorer table grows the missing columns).
pub const DDL: &[&str] = &[
    "CREATE TABLE IF NOT EXISTS spine_outbox ( outbox_id bigserial PRIMARY KEY, message_id text \
     NOT NULL UNIQUE, body bytea NOT NULL, committed_at timestamptz NOT NULL DEFAULT now(), \
     published_at timestamptz, publish_attempts int NOT NULL DEFAULT 0)",
    "ALTER TABLE spine_outbox ADD COLUMN IF NOT EXISTS committed_at timestamptz NOT NULL DEFAULT \
     now()",
    "ALTER TABLE spine_outbox ADD COLUMN IF NOT EXISTS publish_attempts int NOT NULL DEFAULT 0",
];

pub async fn ensure_schema(g: &mut Ground) -> Result<(), RailError> {
    g.ensure("outbox", DDL).await.map(|_| ())
}

/// One transaction: the caller's domain writes plus the outbox row. Any
/// failure inside rolls back BOTH — no state without its event, no event
/// without its state. With a budget, the unpublished backlog is counted
/// first and the write refused by name at the line.
pub async fn commit_with_outbox<F>(
    g: &mut Ground,
    raw: &[u8],
    message_id: &str,
    budget: Option<i64>,
    domain: F,
) -> Result<(), RailError>
where
    F: for<'t, 'c> AsyncFnOnce(&'t Transaction<'c>) -> Result<(), RailError>,
{
    let tx = g.client_mut().transaction().await?;
    if let Some(budget) = budget {
        let pending: i64 = tx
            .query_one(
                "SELECT count(*) FROM spine_outbox WHERE published_at IS NULL",
                &[],
            )
            .await?
            .get(0);
        if pending >= budget {
            return Err(RailError::Budget { pending, budget });
        }
    }
    domain(&tx).await?;
    add_row(&tx, raw, message_id).await?;
    tx.commit().await?;
    Ok(())
}

/// Add an outbox row INSIDE a transaction someone else owns — for effects
/// that must land state + events atomically (the inbox's apply-once effects).
pub async fn add_row(tx: &Transaction<'_>, raw: &[u8], message_id: &str) -> Result<(), RailError> {
    tx.execute(
        "INSERT INTO spine_outbox (message_id, body) VALUES ($1, $2)",
        &[&message_id, &raw],
    )
    .await?;
    Ok(())
}

/// The honest meter: rows awaiting publish, and the oldest one's age.
#[derive(Debug, Clone, PartialEq)]
pub struct Lag {
    pub pending: i64,
    pub oldest_age_s: Option<f64>,
}

pub async fn outbox_lag(g: &Ground) -> Result<Lag, RailError> {
    let row = g
        .client()
        .query_one(
            "SELECT count(*), extract(epoch FROM (now() - min(committed_at)))::float8 \
             FROM spine_outbox WHERE published_at IS NULL",
            &[],
        )
        .await?;
    Ok(Lag {
        pending: row.get(0),
        oldest_age_s: row.get(1),
    })
}

/// Where the relay publishes to. A refusal raises; the row stays unpublished.
pub trait Sink {
    fn publish(
        &mut self,
        message_id: &str,
        body: &[u8],
    ) -> impl std::future::Future<Output = Result<(), RailError>> + Send;
}

/// The test sink: remembers every publish; can be told to fail before
/// accepting (broker down) or after accepting (a death before the mark) —
/// the fault schedule's two relay deaths, deterministic.
#[derive(Debug, Default)]
pub struct MemorySink {
    pub published: Vec<(String, Vec<u8>)>,
    pub fail_before: usize,
    pub fail_after: usize,
}

impl Sink for MemorySink {
    async fn publish(&mut self, message_id: &str, body: &[u8]) -> Result<(), RailError> {
        if self.fail_before > 0 {
            self.fail_before -= 1;
            return Err(RailError::Sink(
                "sink refused before accepting (injected)".into(),
            ));
        }
        self.published.push((message_id.to_string(), body.to_vec()));
        if self.fail_after > 0 {
            self.fail_after -= 1;
            return Err(RailError::Sink(
                "sink crashed after accepting (injected)".into(),
            ));
        }
        Ok(())
    }
}

/// What one relay pass did.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Relayed {
    pub published: usize,
    pub attempts: usize,
    pub remaining: usize,
}

/// Claim unpublished rows oldest-first and publish each. A refusal records
/// the attempt and stops the batch (the broker is likely down); the row
/// stays unpublished and will be retried — at-least-once, never at-most-once.
pub async fn relay_once<S: Sink>(
    g: &Ground,
    sink: &mut S,
    batch: i64,
) -> Result<Relayed, RailError> {
    let rows = g
        .client()
        .query(
            "SELECT outbox_id, message_id, body FROM spine_outbox WHERE published_at IS NULL \
             ORDER BY outbox_id LIMIT $1 FOR UPDATE SKIP LOCKED",
            &[&batch],
        )
        .await?;
    let (mut published, mut attempts) = (0usize, 0usize);
    for row in &rows {
        let outbox_id: i64 = row.get(0);
        let message_id: String = row.get(1);
        let body: Vec<u8> = row.get(2);
        attempts += 1;
        if sink.publish(&message_id, &body).await.is_err() {
            g.client()
                .execute(
                    "UPDATE spine_outbox SET publish_attempts = publish_attempts + 1 WHERE \
                     outbox_id = $1",
                    &[&outbox_id],
                )
                .await?;
            break;
        }
        g.client()
            .execute(
                "UPDATE spine_outbox SET published_at = now(), publish_attempts = \
                 publish_attempts + 1 WHERE outbox_id = $1",
                &[&outbox_id],
            )
            .await?;
        published += 1;
    }
    Ok(Relayed {
        published,
        attempts,
        remaining: rows.len() - published,
    })
}

/// Relay until nothing is pending or the deadline passes; how many published.
pub async fn drain<S: Sink>(
    g: &Ground,
    sink: &mut S,
    deadline: Duration,
) -> Result<usize, RailError> {
    let end = Instant::now() + deadline;
    let mut total = 0;
    while Instant::now() < end {
        let out = relay_once(g, sink, 100).await?;
        total += out.published;
        if out.remaining == 0 && outbox_lag(g).await?.pending == 0 {
            break;
        }
    }
    Ok(total)
}
