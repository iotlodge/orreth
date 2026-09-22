// PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp1, the bytes · 2026-09-22
//! The shared transport envelope (`orreth.transport/1`), v0 — mirrors
//! `orreth_spine.envelope.encode` / `decode`. One broker-neutral metadata
//! contract for every rail (canon 0002): an envelope is its canonical bytes,
//! an incomplete one is refused with its missing fields NAMED (never guessed
//! at), an unknown specversion is refused by name, and unknown additive
//! fields survive a decode (a newer publisher never breaks an older reader).
//!
//! Minting (`make_envelope`) needs a clock and randomness; it is not sp1's.

use crate::canonical::canonical;
use serde_json::Value;
use std::fmt;

pub const SPECVERSION: &str = "orreth.transport/1";
pub const KINDS: [&str; 2] = ["command", "event"];
pub const REQUIRED: [&str; 8] = [
    "specversion",
    "message_id",
    "message_kind",
    "type",
    "universe_id",
    "scope_path",
    "occurred_at",
    "payload",
];

/// The refusals, worded as the reference words them (the fixtures assert the names).
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum EnvelopeError {
    /// `envelope missing required fields: a, b` — every missing name, in REQUIRED's order.
    MissingFields(Vec<String>),
    /// `unknown specversion '…'`.
    UnknownSpecversion(String),
    /// The value is not a JSON object.
    NotAnObject,
    /// The bytes are not ASCII JSON.
    NotJson(String),
}

impl fmt::Display for EnvelopeError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            EnvelopeError::MissingFields(names) => {
                write!(f, "envelope missing required fields: {}", names.join(", "))
            }
            EnvelopeError::UnknownSpecversion(v) => write!(f, "unknown specversion '{v}'"),
            EnvelopeError::NotAnObject => write!(f, "an envelope is a JSON object"),
            EnvelopeError::NotJson(why) => write!(f, "an envelope is ASCII JSON: {why}"),
        }
    }
}

impl std::error::Error for EnvelopeError {}

fn missing(env: &serde_json::Map<String, Value>) -> Result<(), EnvelopeError> {
    let names: Vec<String> = REQUIRED
        .iter()
        .filter(|k| !env.contains_key(**k))
        .map(|k| k.to_string())
        .collect();
    if names.is_empty() {
        Ok(())
    } else {
        Err(EnvelopeError::MissingFields(names))
    }
}

/// Canonical bytes of a complete envelope; an incomplete one is refused with
/// its missing fields named, a foreign specversion by name.
pub fn encode(env: &Value) -> Result<Vec<u8>, EnvelopeError> {
    let map = env.as_object().ok_or(EnvelopeError::NotAnObject)?;
    missing(map)?;
    let spec = &map["specversion"];
    if spec.as_str() != Some(SPECVERSION) {
        return Err(EnvelopeError::UnknownSpecversion(crate::py::python_str(
            spec,
        )));
    }
    Ok(canonical(env))
}

/// Read an envelope back. Unknown additive fields are preserved; missing
/// required ones refuse.
pub fn decode(raw: &[u8]) -> Result<Value, EnvelopeError> {
    if !raw.is_ascii() {
        return Err(EnvelopeError::NotJson("not ascii".into()));
    }
    let env: Value =
        serde_json::from_slice(raw).map_err(|e| EnvelopeError::NotJson(e.to_string()))?;
    let map = env.as_object().ok_or(EnvelopeError::NotAnObject)?;
    missing(map)?;
    Ok(env)
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;

    fn full() -> Value {
        json!({
            "specversion": SPECVERSION, "message_id": "msg_1", "message_kind": "event",
            "type": "orreth.heartbeat.v1", "universe_id": "u:dev", "scope_path": "u:dev",
            "occurred_at": "2026-09-22T00:00:00.000Z", "payload": {"ref": "rec_1", "hash": "sha256:-"}
        })
    }

    #[test]
    fn refusals_name_what_is_missing_in_required_order() {
        let mut env = full();
        env.as_object_mut().unwrap().remove("occurred_at");
        env.as_object_mut().unwrap().remove("message_id");
        let err = encode(&env).unwrap_err();
        assert_eq!(
            err.to_string(),
            "envelope missing required fields: message_id, occurred_at"
        );
        let mut env = full();
        env["specversion"] = json!("orreth.transport/9");
        assert_eq!(
            encode(&env).unwrap_err().to_string(),
            "unknown specversion 'orreth.transport/9'"
        );
        assert_eq!(encode(&json!([1])).unwrap_err(), EnvelopeError::NotAnObject);
    }

    #[test]
    fn decode_round_trips_and_keeps_the_unknown() {
        let mut env = full();
        env["future_field"] = json!({"a": 1});
        let bytes = encode(&env).unwrap();
        assert_eq!(decode(&bytes).unwrap(), env);
        assert!(decode(b"{\"x\":\"\xc3\xbc\"}").is_err());
        assert!(decode(b"[]").is_err());
    }
}
