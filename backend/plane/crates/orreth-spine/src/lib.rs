// PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp1, the bytes · 2026-09-22
// Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp2, the ground and the rails · 2026-09-22
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

pub mod ask;
pub mod canonical;
pub mod envelope;
pub mod export;
pub mod hash;
pub mod mitl;
pub mod placement;
pub mod proof;
pub mod py;
pub mod rails;
pub mod watch;

#[cfg(feature = "rails")]
pub mod events;
#[cfg(feature = "rails")]
pub mod ground;
#[cfg(feature = "rails")]
pub mod heartbeat;
#[cfg(feature = "rails")]
pub mod inbox;
#[cfg(feature = "rails")]
pub mod invoke;
#[cfg(feature = "rails")]
pub mod outbox;
#[cfg(feature = "rails")]
pub mod rail_error;
#[cfg(feature = "rails")]
pub mod sinks;

pub use canonical::canonical;
pub use hash::content_hash;
