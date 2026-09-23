// PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp3, the ask road · 2026-09-22
//! The standing loops of a bridge — mirrors `dispatch.run_dispatcher` (the
//! events-rail consumer turning a committed `ask.received` into a serve
//! command on the target's bench) and the rig's relay loop.
//!
//! THE SHADOW LAW (why two bridges on one ground never double-dispatch): the
//! Kafka group is per LIFE (`glass-dispatcher-<hex>`, the Python rig's own
//! law — a wedged ghost dies with its rig), so EVERY dispatcher sees every
//! fact; what hands each fact to exactly one is the durable INBOX on the
//! shared ground — both spines apply under the same consumer name
//! (`glass-dispatcher`), and the footprint `(consumer, message_id)` with the
//! per-ask cursor lets only the first claimant publish; the other finds the
//! footprint and absorbs (`Duplicate`/`Stale`, counted on the meter, never a
//! second command). A replay from `earliest` at boot costs the same: every
//! old fact is already a footprint. Facts of another world are skipped by
//! scope and committed (`SPINE_SCOPE` fences worlds on one broker).

use crate::asks::{command_for, ASK_RECEIVED};
use crate::events::{Pending, Reader};
use crate::ground::Ground;
use crate::inbox::{self, Outcome};
use crate::invoke;
use crate::outbox;
use crate::rail_error::RailError;
use crate::sinks::KafkaSink;
use crate::world::{token_hex, World};
use std::sync::atomic::{AtomicBool, AtomicU64, Ordering};
use std::sync::Arc;
use std::time::Duration;

/// The inbox consumer name BOTH spines dispatch under — the shadow law's hinge.
pub const CONSUMER: &str = "glass-dispatcher";

/// A group per life, as the Python rig names it.
pub fn group_per_life() -> String {
    format!("glass-dispatcher-{}", token_hex(3))
}

/// The honest meter of one dispatcher's life.
#[derive(Debug, Default)]
pub struct Meter {
    /// Facts this dispatcher turned into a serve command.
    pub dispatched: AtomicU64,
    /// Facts another dispatcher (or an earlier life) had already claimed.
    pub absorbed: AtomicU64,
    /// Facts of another world, committed past.
    pub skipped: AtomicU64,
}

impl Meter {
    pub fn read(&self) -> (u64, u64, u64) {
        (
            self.dispatched.load(Ordering::Relaxed),
            self.absorbed.load(Ordering::Relaxed),
            self.skipped.load(Ordering::Relaxed),
        )
    }
}

/// The standing dispatcher: one consumer for its whole life, dispatching
/// only its own world's facts; `ready` set once the broker assigned it;
/// returns when `stop` is raised. A rail's refusal returns the error — the
/// caller decides whether to stand again.
pub async fn run_dispatcher(
    g: &mut Ground,
    w: &World,
    group: &str,
    stop: Arc<AtomicBool>,
    ready: Arc<AtomicBool>,
    meter: Arc<Meter>,
) -> Result<(), RailError> {
    let reader = Reader::open(&w.kafka, group, &[ASK_RECEIVED], true).await?;
    // a replay from `earliest` walks every world's facts on the broker: the
    // ones not ours are committed in batches (the offset is monotone on the
    // one partition; the latest commit covers the rest), so the catch-up is
    // seconds, not a sync commit per skipped fact
    let mut behind: Option<Pending> = None;
    let mut skipped_since = 0u32;
    while !stop.load(Ordering::Relaxed) {
        if !ready.load(Ordering::Relaxed) && reader.assigned() {
            ready.store(true, Ordering::Relaxed);
        }
        let Some(p) = reader.next(Duration::from_millis(500)).await? else {
            if let Some(b) = behind.take() {
                reader.commit(&b)?;
                skipped_since = 0;
            }
            continue;
        };
        let ours = p
            .env
            .as_ref()
            .is_some_and(|env| env["scope_path"].as_str() == Some(&w.scope));
        if let (Some(env), true) = (&p.env, ours) {
            let cmd = command_for(env).map_err(|e| RailError::Refused(e.to_string()))?;
            let (url, ns) = (w.rabbit_url.clone(), w.ns.clone());
            let out = inbox::apply_event(g, CONSUMER, env, async move |_tx| {
                invoke::publish_command(&url, &cmd, &ns).await
            })
            .await?;
            match out {
                Outcome::Applied => meter.dispatched.fetch_add(1, Ordering::Relaxed),
                Outcome::Duplicate | Outcome::Stale => {
                    meter.absorbed.fetch_add(1, Ordering::Relaxed)
                }
            };
            reader.commit(&p)?;
            behind = None;
            skipped_since = 0;
        } else {
            meter.skipped.fetch_add(1, Ordering::Relaxed);
            skipped_since += 1;
            behind = Some(p);
            if skipped_since >= 500 {
                if let Some(b) = behind.take() {
                    reader.commit(&b)?;
                }
                skipped_since = 0;
            }
        }
    }
    if let Some(b) = behind.take() {
        reader.commit(&b)?;
    }
    Ok(())
}

/// The relay loop: every 200 ms, the unpublished rows to the events rail —
/// a refusal is recorded on the row and retried (at-least-once).
pub async fn run_relay(g: &Ground, w: &World, stop: Arc<AtomicBool>) -> Result<(), RailError> {
    let mut sink = KafkaSink::new(&w.kafka)?;
    while !stop.load(Ordering::Relaxed) {
        let _ = outbox::relay_once(g, &mut sink, 100).await;
        tokio::time::sleep(Duration::from_millis(200)).await;
    }
    Ok(())
}
