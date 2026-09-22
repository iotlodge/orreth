// PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp2, the ground and the rails · 2026-09-22
//! The rails' NAMES and SHAPES — pure, no I/O. Mirrors `orreth_spine.rails`
//! (the command exchange, the heartbeat's queue · key · topic, the dials
//! `SPINE_PG` · `SPINE_RABBIT` · `SPINE_KAFKA`), `orreth_spine.resident.serve_queue`
//! / `serve_key` (queue names wear the `SPINE_QUEUE_NS` namespace so a test
//! session never races a live rig on one broker), `orreth_spine.envelope.scope`
//! (`SPINE_SCOPE`: the world a fact wears), `orreth_spine.sinks.KafkaSink`'s two
//! laws (the TOPIC is the envelope's type — schema families, never per-identity;
//! the KEY is the aggregate id when the envelope wears one, else the message id)
//! and the head of `orreth_spine.inbox.apply_event` (which road an envelope takes
//! through the inbox: once by message id, or sequenced per aggregate).
//!
//! The conformance kinds `rail_names` · `outbox_row` · `inbox_key`
//! (`spine/conformance/rails-v0.json`) measure every function here against the
//! Python reference. The I/O that stands on these names lives behind the
//! `rails` feature (`ground` · `outbox` · `inbox` · `sinks` · `invoke` ·
//! `events` · `heartbeat`).

use crate::envelope::{self, EnvelopeError};
use crate::py;
use serde_json::Value;

/// The dev rig's ground (`spine/compose.yaml`: Postgres 16 on :5433).
pub const PG_DSN_DEFAULT: &str = "postgresql://orreth:orreth-dev@localhost:5433/spine";
/// The invoke rail (RabbitMQ 3.13 on :5672).
pub const RABBIT_URL_DEFAULT: &str = "amqp://orreth:orreth-dev@localhost:5672/%2F";
/// The events rail (Kafka 3.9 on :9092).
pub const KAFKA_BOOTSTRAP_DEFAULT: &str = "localhost:9092";
/// The world a process belongs to when `SPINE_SCOPE` is silent.
pub const SCOPE_DEFAULT: &str = "u:dev";

pub const COMMAND_EXCHANGE: &str = "orreth.command.v1";
pub const HEARTBEAT_QUEUE: &str = "spine.heartbeat";
pub const HEARTBEAT_KEY: &str = "cmd.dev.00.heartbeat";
pub const HEARTBEAT_TOPIC: &str = "orreth.heartbeat.v1";
pub const SERVE_QUEUE: &str = "resident.serve.00";
pub const SERVE_KEY: &str = "cmd.dev.00.resident.serve";

fn dial(name: &str, default: &str) -> String {
    std::env::var(name)
        .ok()
        .filter(|v| !v.is_empty())
        .unwrap_or_else(|| default.to_string())
}

/// `SPINE_PG`, else the rig's ground.
pub fn pg_dsn() -> String {
    dial("SPINE_PG", PG_DSN_DEFAULT)
}

/// `SPINE_RABBIT`, else the rig's invoke rail.
pub fn rabbit_url() -> String {
    dial("SPINE_RABBIT", RABBIT_URL_DEFAULT)
}

/// `SPINE_KAFKA`, else the rig's events rail.
pub fn kafka_bootstrap() -> String {
    dial("SPINE_KAFKA", KAFKA_BOOTSTRAP_DEFAULT)
}

/// `SPINE_QUEUE_NS` — the session's own benches; empty means the rig's.
pub fn queue_ns() -> String {
    std::env::var("SPINE_QUEUE_NS").unwrap_or_default()
}

/// The world a dial names: unset or empty → `u:dev` (pure; `scope()` reads the env).
pub fn scope_from(dial: Option<&str>) -> String {
    match dial {
        Some(v) if !v.is_empty() => v.to_string(),
        _ => SCOPE_DEFAULT.to_string(),
    }
}

/// `SPINE_SCOPE` — the world this process belongs to (default `u:dev`).
/// A dispatcher only dispatches its OWN world's facts.
pub fn scope() -> String {
    scope_from(std::env::var("SPINE_SCOPE").ok().as_deref())
}

fn namespaced(base: &str, ns: &str, name: Option<&str>) -> String {
    let mut out = base.to_string();
    if !ns.is_empty() {
        out.push('.');
        out.push_str(ns);
    }
    if let Some(n) = name {
        out.push('.');
        out.push_str(n);
    }
    out
}

/// The serve queue: `resident.serve.00[.<ns>][.<name>]` — a targeted command
/// rides the named resident's own queue, an untargeted one the shared bench.
pub fn serve_queue(ns: &str, name: Option<&str>) -> String {
    namespaced(SERVE_QUEUE, ns, name)
}

/// The serve routing key: `cmd.dev.00.resident.serve[.<ns>][.<name>]`.
pub fn serve_key(ns: &str, name: Option<&str>) -> String {
    namespaced(SERVE_KEY, ns, name)
}

/// The heartbeat's queue, namespaced the same way (Rust-only: the Python
/// heartbeat wears the bare name; with an empty namespace they agree).
pub fn heartbeat_queue(ns: &str) -> String {
    namespaced(HEARTBEAT_QUEUE, ns, None)
}

/// The heartbeat's routing key, namespaced the same way.
pub fn heartbeat_key(ns: &str) -> String {
    namespaced(HEARTBEAT_KEY, ns, None)
}

/// The topic a fact is published to: the envelope's TYPE.
pub fn topic_for(env: &Value) -> Option<&str> {
    env.get("type").and_then(Value::as_str)
}

/// The partition key: the aggregate's id when the envelope wears a truthy
/// one, else the message id — `str(aggregate.id or message_id)` in Python.
pub fn key_for(env: &Value) -> Option<String> {
    let agg_id = env.get("aggregate").and_then(|a| a.get("id"));
    match agg_id {
        Some(id) if py::truthy(id) => Some(py::python_str(id)),
        _ => env.get("message_id").map(py::python_str),
    }
}

/// One outbox row: the stable message id and the canonical bytes.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct OutboxRow {
    pub message_id: String,
    pub body: Vec<u8>,
}

/// The row a fact becomes on the ground — `encode` refuses an incomplete
/// envelope by name, so a row can never carry a fact the wire would refuse.
pub fn outbox_row(env: &Value) -> Result<OutboxRow, EnvelopeError> {
    let body = envelope::encode(env)?;
    let message_id = env
        .get("message_id")
        .and_then(Value::as_str)
        .ok_or_else(|| EnvelopeError::MissingFields(vec!["message_id".into()]))?
        .to_string();
    Ok(OutboxRow { message_id, body })
}

/// Which road an envelope takes through the inbox.
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum InboxRoute {
    /// Effects once per (consumer, message id); no ordering claim.
    Once { message_id: String },
    /// Effects once AND in sequence per aggregate — a stale sequence is
    /// recorded and skipped, a gap refuses to guess.
    Sequenced {
        message_id: String,
        aggregate_id: String,
        sequence: i64,
    },
}

impl InboxRoute {
    pub fn message_id(&self) -> &str {
        match self {
            InboxRoute::Once { message_id } | InboxRoute::Sequenced { message_id, .. } => {
                message_id
            }
        }
    }
    pub fn road(&self) -> &'static str {
        match self {
            InboxRoute::Once { .. } => "once",
            InboxRoute::Sequenced { .. } => "sequenced",
        }
    }
}

/// Python's `int(x or 0)` for the sequence, on the JSON values a fact carries.
fn sequence_of(v: Option<&Value>) -> i64 {
    match v {
        Some(Value::Number(n)) => n
            .as_i64()
            .or_else(|| n.as_f64().map(|f| f.trunc() as i64))
            .unwrap_or(0),
        Some(Value::String(s)) => s.trim().parse().unwrap_or(0),
        Some(Value::Bool(true)) => 1,
        _ => 0,
    }
}

/// `aid = str(aggregate.id or "")`, `seq = int(aggregate.sequence or 0)`;
/// no id or no positive sequence → once by message id.
pub fn inbox_route(env: &Value) -> InboxRoute {
    let message_id = env
        .get("message_id")
        .map(py::python_str)
        .unwrap_or_default();
    let agg = env.get("aggregate").filter(|a| py::truthy(a));
    let aggregate_id = agg
        .and_then(|a| a.get("id"))
        .filter(|id| py::truthy(id))
        .map(py::python_str)
        .unwrap_or_default();
    let sequence = sequence_of(agg.and_then(|a| a.get("sequence")));
    if aggregate_id.is_empty() || sequence <= 0 {
        InboxRoute::Once { message_id }
    } else {
        InboxRoute::Sequenced {
            message_id,
            aggregate_id,
            sequence,
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;

    #[test]
    fn names_wear_the_namespace_and_the_name_in_order() {
        assert_eq!(serve_queue("", None), "resident.serve.00");
        assert_eq!(serve_queue("t1", None), "resident.serve.00.t1");
        assert_eq!(serve_queue("t1", Some("echo")), "resident.serve.00.t1.echo");
        assert_eq!(
            serve_key("", Some("echo")),
            "cmd.dev.00.resident.serve.echo"
        );
        assert_eq!(heartbeat_queue(""), HEARTBEAT_QUEUE);
        assert_eq!(heartbeat_key("t1"), "cmd.dev.00.heartbeat.t1");
    }

    #[test]
    fn the_key_is_the_aggregate_or_the_message() {
        let e = json!({"message_id": "msg_1", "type": "orreth.x.v1", "aggregate": {"id": "ask_9"}});
        assert_eq!(key_for(&e).as_deref(), Some("ask_9"));
        assert_eq!(topic_for(&e), Some("orreth.x.v1"));
        let e = json!({"message_id": "msg_1", "aggregate": {"id": ""}});
        assert_eq!(key_for(&e).as_deref(), Some("msg_1"));
        let e = json!({"message_id": "msg_1", "aggregate": {"id": 7}});
        assert_eq!(key_for(&e).as_deref(), Some("7"));
    }

    #[test]
    fn the_inbox_road_is_sequenced_only_with_an_id_and_a_positive_sequence() {
        let once = |e: Value| matches!(inbox_route(&e), InboxRoute::Once { .. });
        assert!(once(json!({"message_id": "m"})));
        assert!(once(
            json!({"message_id": "m", "aggregate": {"id": "a", "sequence": 0}})
        ));
        assert!(once(
            json!({"message_id": "m", "aggregate": {"id": "", "sequence": 2}})
        ));
        assert!(once(json!({"message_id": "m", "aggregate": null})));
        assert_eq!(
            inbox_route(&json!({"message_id": "m", "aggregate": {"id": "a", "sequence": 3}})),
            InboxRoute::Sequenced {
                message_id: "m".into(),
                aggregate_id: "a".into(),
                sequence: 3
            }
        );
    }
}
