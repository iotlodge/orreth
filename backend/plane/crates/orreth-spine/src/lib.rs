// PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp1, the bytes · 2026-09-22
// Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp2, the ground and the rails · 2026-09-22
// Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp3, the ask road · 2026-09-22
// Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp4, the loops · 2026-09-23
// Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp5, memory and the export: memory · kernel_self · store · digest · export_live · 2026-09-24
//! `orreth-spine` — the kernel's pure laws in Rust, ported from the Python spine
//! (`spine/orreth_spine/`) against the conformance suite (canon 0008).
//!
//! Phase 7 sp1 is hermetic: no ground, no broker, no door, no clock. Every
//! function here is a pure map from its inputs to bytes, a hash, a verdict or
//! a sentence — and every one of them is measured against the fixtures under
//! `spine/conformance/`, the same files the Python reference generated and
//! passes, unchanged (rule 6: canonical bytes are the contract; 0008's law of
//! a ported module). The runner is `tests/conformance.rs`.
//!
//! Module map (the Python module each mirrors is named on the module):
//! - [`canonical`] — the one true byte form (`envelope.canonical`) — THE CRUX.
//! - [`hash`] — the content hash over those bytes.
//! - [`envelope`] — `orreth.transport/1`: encode · decode · refusals by name.
//! - [`proof`] — TOTP (RFC 6238), the consequence ladder, the stop's demand.
//! - [`export`] — `orreth.compliance/1`: the hash chain, the chain's status, `verify`.
//! - [`watch`] — the sense of a watch, its sentence, the monitor's offer.
//! - [`placement`] — the profile with its defaults, the honor rule, the card's line.
//! - [`ask`] — the address at the head of an ask, the door's refusal, the
//!   refusal in a reply, echo's reply, the duty's framing.
//! - [`mitl`] — a citation in a human's name, the verdict ladder.
//! - [`py`] — Python's truth and `str()`, where a law was written in that idiom.
//! - [`rails`] — the rails' NAMES and SHAPES (queues · keys · topics · the
//!   outbox row · the inbox road), pure; measured by `rails-v0.json`.
//!
//! Phase 7 sp2 adds the GROUND AND THE RAILS behind the `rails` feature —
//! off by default so `cargo test` stays hermetic; on, the crate stands on
//! the dev rig (`spine/compose.yaml`) and `tests/rails.rs` proves it:
//! - [`ground`] — connect; the once-guard, the ground memo, the advisory law.
//! - [`outbox`] — `commit_with_outbox` · `relay_once` · the bounded budget.
//! - [`inbox`] — `apply_once` · `apply_event` — effects once, gaps refuse.
//! - [`sinks`] — `KafkaSink`: topic = type, key = aggregate id.
//! - [`invoke`] — RabbitMQ: declare · publish with confirms · receive and ack.
//! - [`events`] — Kafka: declare topics · a reader that commits after the work.
//! - [`heartbeat`] — one breath through each rail, and all three composed.
//! - [`rail_error`] — the rails' refusals, in the reference's words.
//!
//! Phase 7 sp3 adds THE ASK ROAD — pure: [`services`] (the ladder's step,
//! the manifest pin) · [`intent`] (the kind of an ask, P23) · the hold's
//! words and the otpauth URI in [`proof`]; behind `rails`: [`schema`] (the
//! road's tables, word for word) · [`world`] (the dials, the road's refusals,
//! Python's `isoformat`) · [`markers_live`] (minting with the fact; the
//! Analyzer's origins) · [`proof_live`] (enroll · confirm · masters · the
//! judgement at the door) · [`asks`] (`submit_ask` = the row and its fact in
//! one transaction; `absent`; `confirm_ask`; the views) · [`sessions`] (roll
//! · list · load; the residents; the crew; the shelf's read) ·
//! [`intent_live`] (an intention declared at the door; the listing) ·
//! [`dispatcher`] (the standing events consumer: `ask.received` → a serve
//! command on the target's bench; the relay loop) · [`feed`] (the Bridge
//! feed's heart: revisions, the ring, the fan-out); and behind `bridge`:
//! [`bridge`] — the doors and the SSE feed on axum, the `spine-bridge`
//! binary's whole, in SHADOW on :4601 beside the Python Bridge on :4600.
//!
//! Phase 7 sp4 adds THE LOOPS — pure: [`beat`] (the beat lock's classes and
//! words) · [`mcp`] (the five mcp kinds: the requests' bytes, the pins, the
//! transport, the words) · the loop's words in [`intent`] · the turned fact
//! in [`watch`] · W26's words in [`ask`]; behind `rails`: [`presence`] (the
//! leases, the roster) · [`monitor`] (the snapshot, the watches judged, the
//! turn recorded as a fact) · [`scheduler`] (the schedules, the occurrence
//! framed as a duty, the tick) · [`harness`] (the five world checks) · the
//! stop, the restart and the loop in [`intent_live`] · `set_marker` and the
//! interest law in [`markers_live`] · the kernel's hold in [`proof_live`] ·
//! the APPROVE of a kernel-held act in [`asks`]; and in [`bridge`] the two
//! loops as standing tasks and their doors. THE BEAT LOCK is the loops'
//! shadow law: a beat is claimed on the ground (`pg_try_advisory_lock(class,
//! hashtext(scope))`) before it runs, so two kernels on one world never tick
//! or turn it at once — one ground, one beat at a time, per world.

pub mod ask;
pub mod beat;
pub mod canonical;
pub mod envelope;
pub mod export;
pub mod hash;
pub mod intent;
pub mod kernel_self;
pub mod mcp;
pub mod memory;
pub mod mitl;
pub mod placement;
pub mod proof;
pub mod py;
pub mod rails;
pub mod services;
pub mod watch;

#[cfg(feature = "rails")]
pub mod asks;
#[cfg(feature = "bridge")]
pub mod bridge;
#[cfg(feature = "rails")]
pub mod digest;
#[cfg(feature = "rails")]
pub mod dispatcher;
#[cfg(feature = "rails")]
pub mod events;
#[cfg(feature = "rails")]
pub mod export_live;
#[cfg(feature = "rails")]
pub mod feed;
#[cfg(feature = "rails")]
pub mod ground;
#[cfg(feature = "rails")]
pub mod harness;
#[cfg(feature = "rails")]
pub mod heartbeat;
#[cfg(feature = "rails")]
pub mod inbox;
#[cfg(feature = "rails")]
pub mod intent_live;
#[cfg(feature = "rails")]
pub mod invoke;
#[cfg(feature = "rails")]
pub mod markers_live;
#[cfg(feature = "rails")]
pub mod monitor;
#[cfg(feature = "rails")]
pub mod outbox;
#[cfg(feature = "rails")]
pub mod presence;
#[cfg(feature = "rails")]
pub mod proof_live;
#[cfg(feature = "rails")]
pub mod rail_error;
#[cfg(feature = "rails")]
pub mod scheduler;
#[cfg(feature = "rails")]
pub mod schema;
#[cfg(feature = "rails")]
pub mod sessions;
#[cfg(feature = "rails")]
pub mod sinks;
#[cfg(feature = "rails")]
pub mod store;
#[cfg(feature = "rails")]
pub mod world;

pub use canonical::canonical;
pub use hash::content_hash;
