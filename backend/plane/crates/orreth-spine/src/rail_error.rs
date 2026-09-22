// PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp2, the ground and the rails · 2026-09-22
//! The rails' refusals, worded as the Python reference words them: the
//! outbox budget names its numbers (`OutboxBudgetExceeded`), a gap names the
//! aggregate and the sequences (`GapDetected`), a sink's refusal carries the
//! rail's own words. Never a bare code.

use crate::envelope::EnvelopeError;
use std::fmt;

#[derive(Debug)]
pub enum RailError {
    /// The ground refused (Postgres).
    Ground(tokio_postgres::Error),
    /// The unpublished backlog reached its declared budget — refused BY NAME.
    Budget { pending: i64, budget: i64 },
    /// A sequence arrived from the future — fetch the missing events; never guess.
    Gap {
        aggregate_id: String,
        expected: i64,
        got: i64,
    },
    /// The events rail refused a publish (the row stays unpublished).
    Sink(String),
    /// The invoke rail refused (AMQP).
    Invoke(lapin::Error),
    /// The events rail refused (Kafka).
    Events(String),
    /// A rail never answered in time.
    Timeout(String),
    /// A body that is not an envelope.
    Envelope(EnvelopeError),
    /// The rails' own refusal in words (a wrong kind, bytes that differ, …).
    Refused(String),
}

impl fmt::Display for RailError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            RailError::Ground(e) => write!(f, "the ground refused: {e}"),
            RailError::Budget { pending, budget } => write!(
                f,
                "the outbox holds {pending} unpublished rows — the declared budget is {budget}; \
                 publish (or raise the budget) before writing more"
            ),
            RailError::Gap {
                aggregate_id,
                expected,
                got,
            } => write!(
                f,
                "gap on {aggregate_id}: expected sequence {expected}, got {got} — fetch the \
                 missing events; never guess"
            ),
            RailError::Sink(why) => write!(f, "{why}"),
            RailError::Invoke(e) => write!(f, "the invoke rail refused: {e}"),
            RailError::Events(why) => write!(f, "the events rail refused: {why}"),
            RailError::Timeout(what) => write!(f, "{what}"),
            RailError::Envelope(e) => write!(f, "{e}"),
            RailError::Refused(why) => write!(f, "{why}"),
        }
    }
}

impl std::error::Error for RailError {}

impl From<tokio_postgres::Error> for RailError {
    fn from(e: tokio_postgres::Error) -> Self {
        RailError::Ground(e)
    }
}

impl From<lapin::Error> for RailError {
    fn from(e: lapin::Error) -> Self {
        RailError::Invoke(e)
    }
}

impl From<rdkafka::error::KafkaError> for RailError {
    fn from(e: rdkafka::error::KafkaError) -> Self {
        RailError::Events(e.to_string())
    }
}

impl From<EnvelopeError> for RailError {
    fn from(e: EnvelopeError) -> Self {
        RailError::Envelope(e)
    }
}
