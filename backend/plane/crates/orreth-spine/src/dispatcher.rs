// PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp3, the ask road · 2026-09-22
// Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp7, cells: the dispatcher and the relay on the cell's topics · 2026-09-25
// Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch row 4, re-base sp1: POISON-PARKING — the dispatcher parks a poison with its evidence and HOLDS at it until a person advances it · 2026-09-28
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
//!
//! POISON-PARKING (re-base sp1 — the projector's law, `projector.py`: "a body
//! that cannot be decoded is PARKED visibly with its evidence and the projector
//! stops at it — advancing past a poison event is an operator's explicit
//! decision, never a silent loss"): a body that is not an envelope, or a fact
//! that can never apply (a gap in its aggregate's sequence, a refused shape),
//! is parked ONCE by its place on the rail — the row and its fact
//! (`orreth.inbox.parked.v1`) together — and the dispatcher HOLDS at it: the
//! offset is never committed past, nothing after it is dispatched, and every
//! two seconds it asks the ground whether a person has advanced it
//! (`inbox::advance` — `POST /parked/advance`, a governing seat). A transient
//! refusal (the ground, the broker, the bench) is NOT poison: it returns as
//! before and the kernel stands the dispatcher again from the committed offset.

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
    /// re-base sp1: poison events this life PARKED (each held at until advanced).
    pub parked: AtomicU64,
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

/// How often a holding dispatcher asks the ground whether a person advanced it.
pub const HOLD_POLL: Duration = Duration::from_secs(2);

/// Is this refusal the FACT's own (poison — it will never apply), or the rail's
/// (transient — stand again and it may)?
pub fn is_poison(e: &RailError) -> bool {
    matches!(
        e,
        RailError::Gap { .. } | RailError::Refused(_) | RailError::Envelope(_)
    )
}

/// The park and the hold: the facts skipped before it committed (they are done), the
/// poison parked once with its evidence, then the dispatcher standing at it — never
/// committing past — until a person's word advances it (then the offset is committed
/// and the loop goes on) or the kernel stops (the offset uncommitted: a relit
/// dispatcher re-reads the same poison, finds its row, and holds again).
#[allow(clippy::too_many_arguments)]
async fn hold_at(
    g: &mut Ground,
    w: &World,
    reader: &Reader,
    p: &Pending,
    reason: &str,
    stop: &AtomicBool,
    meter: &Meter,
    behind: &mut Option<Pending>,
) -> Result<(), RailError> {
    if let Some(b) = behind.take() {
        reader.commit(&b)?;
    }
    let (id, fresh) = inbox::park(
        g,
        &w.scope,
        CONSUMER,
        &p.topic,
        p.partition,
        p.offset,
        &p.raw,
        reason,
    )
    .await?;
    if fresh {
        meter.parked.fetch_add(1, Ordering::Relaxed);
    }
    eprintln!(
        "  [kernel] {} (parked:{id})",
        crate::ask::parked_words(CONSUMER, &p.topic, p.partition, p.offset, reason)
    );
    while !stop.load(Ordering::Relaxed) {
        if inbox::advanced(g, id).await? {
            reader.commit(p)?;
            eprintln!(
                "  [kernel] advanced past parked:{id} on a person's word — the dispatcher goes on"
            );
            return Ok(());
        }
        tokio::time::sleep(HOLD_POLL).await;
    }
    Ok(())
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
    let reader = Reader::open(
        &w.kafka,
        group,
        &[&crate::rails::topic(ASK_RECEIVED, &w.ns)],
        true,
    )
    .await?; // P7 sp7: the cell's topic
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
        if p.env.is_none() {
            // a body that is not an envelope: parked with its evidence, and the rail holds
            let reason = format!(
                "undecodable body: {}",
                p.flaw.as_deref().unwrap_or("no body")
            );
            hold_at(g, w, &reader, &p, &reason, &stop, &meter, &mut behind).await?;
            skipped_since = 0;
            continue;
        }
        let ours = p
            .env
            .as_ref()
            .is_some_and(|env| env["scope_path"].as_str() == Some(&w.scope));
        if let (Some(env), true) = (&p.env, ours) {
            let (url, ns) = (w.rabbit_url.clone(), w.ns.clone());
            let out = match command_for(env) {
                Err(e) => Err(RailError::Refused(e.to_string())),
                Ok(cmd) => {
                    inbox::apply_event(g, CONSUMER, env, async move |_tx| {
                        invoke::publish_command(&url, &cmd, &ns).await
                    })
                    .await
                }
            };
            match out {
                Ok(Outcome::Applied) => {
                    meter.dispatched.fetch_add(1, Ordering::Relaxed);
                }
                Ok(Outcome::Duplicate | Outcome::Stale) => {
                    meter.absorbed.fetch_add(1, Ordering::Relaxed);
                }
                Err(e) if is_poison(&e) => {
                    // the fact itself can never apply: parked, and the rail holds
                    let reason = format!("could not apply: {e}");
                    hold_at(g, w, &reader, &p, &reason, &stop, &meter, &mut behind).await?;
                    skipped_since = 0;
                    continue;
                }
                Err(e) => return Err(e), // the rail's own refusal: stand again from the committed offset
            }
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
    let mut sink = KafkaSink::new(&w.kafka, &w.ns)?;
    while !stop.load(Ordering::Relaxed) {
        let _ = outbox::relay_once(g, &mut sink, 100).await;
        tokio::time::sleep(Duration::from_millis(200)).await;
    }
    Ok(())
}
