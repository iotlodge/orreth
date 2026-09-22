// PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp1, the bytes · 2026-09-22
//! The shared transport envelope (`orreth.transport/1`), v0 — mirrors
//! `orreth_spine.envelope.encode` / `decode`. One broker-neutral metadata
//! contract for every rail (canon 0002): an envelope is its canonical bytes,
//! an incomplete one is refused with its missing fields NAMED (never guessed
//! at), an unknown specversion is refused by name, and unknown additive
//! fields survive a decode (a newer publisher never breaks an older reader).
//!
//! Minting (`make_envelope`) needs a clock and randomness: [`Mint`] behind the
//! `rails` feature (sp2); the clock's spelling [`iso_millis`] is pure.

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

/// `now_iso`'s spelling, pure: UTC, millisecond precision, Z-suffixed — one
/// clock spelling everywhere (`%Y-%m-%dT%H:%M:%S.mmmZ`).
pub fn iso_millis(unix_ms: u64) -> String {
    let (secs, ms) = (unix_ms / 1000, unix_ms % 1000);
    let (days, rem) = (secs / 86_400, secs % 86_400);
    let (h, m, s) = (rem / 3600, (rem % 3600) / 60, rem % 60);
    // civil-from-days (Howard Hinnant), proleptic Gregorian
    let z = days as i64 + 719_468;
    let era = z.div_euclid(146_097);
    let doe = z.rem_euclid(146_097);
    let yoe = (doe - doe / 1460 + doe / 36_524 - doe / 146_096) / 365;
    let y = yoe + era * 400;
    let doy = doe - (365 * yoe + yoe / 4 - yoe / 100);
    let mp = (5 * doy + 2) / 153;
    let d = doy - (153 * mp + 2) / 5 + 1;
    let mo = if mp < 10 { mp + 3 } else { mp - 9 };
    let y = if mo <= 2 { y + 1 } else { y };
    format!("{y:04}-{mo:02}-{d:02}T{h:02}:{m:02}:{s:02}.{ms:03}Z")
}

/// The clock now, in the one spelling.
pub fn now_iso() -> String {
    let ms = std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .map(|d| d.as_millis() as u64)
        .unwrap_or(0);
    iso_millis(ms)
}

/// Mint one envelope — mirrors `orreth_spine.envelope.make_envelope`. The
/// message id is globally unique and immutable (commands wear `cmd_`, events
/// `msg_`, 12 random bytes as hex); everything else is plain data. `aggregate`
/// `{type, id, sequence}` names the one thing whose order matters; `marker`
/// `{kind, id, parent, by}` the typed origin the fact serves (0006).
#[cfg(feature = "rails")]
#[derive(Debug, Clone, Default)]
pub struct Mint {
    pub kind: String,
    pub r#type: String,
    pub universe_id: String,
    pub scope_path: String,
    pub payload: Value,
    pub correlation_id: Option<String>,
    pub authority_chain: Option<Vec<String>>,
    pub aggregate: Option<Value>,
    pub marker: Option<Value>,
}

#[cfg(feature = "rails")]
impl Mint {
    pub fn mint(self) -> Result<Value, EnvelopeError> {
        if !KINDS.contains(&self.kind.as_str()) {
            return Err(EnvelopeError::NotJson(format!(
                "message_kind must be one of {KINDS:?}, not {:?}",
                self.kind
            )));
        }
        use rand::RngCore;
        let mut bytes = [0u8; 12];
        rand::thread_rng().fill_bytes(&mut bytes);
        let hex: String = bytes.iter().map(|b| format!("{b:02x}")).collect();
        let prefix = if self.kind == "command" {
            "cmd_"
        } else {
            "msg_"
        };
        let mut env = serde_json::Map::new();
        env.insert("specversion".into(), Value::String(SPECVERSION.into()));
        env.insert("message_id".into(), Value::String(format!("{prefix}{hex}")));
        env.insert("message_kind".into(), Value::String(self.kind));
        env.insert("type".into(), Value::String(self.r#type));
        env.insert("universe_id".into(), Value::String(self.universe_id));
        env.insert("scope_path".into(), Value::String(self.scope_path));
        env.insert("occurred_at".into(), Value::String(now_iso()));
        env.insert("payload".into(), self.payload);
        if let Some(c) = self.correlation_id.filter(|c| !c.is_empty()) {
            env.insert("correlation_id".into(), Value::String(c));
        }
        if let Some(chain) = self.authority_chain.filter(|c| !c.is_empty()) {
            env.insert(
                "authority_chain".into(),
                Value::Array(chain.into_iter().map(Value::String).collect()),
            );
        }
        if let Some(a) = self.aggregate.filter(crate::py::truthy) {
            env.insert("aggregate".into(), a);
        }
        if let Some(m) = self.marker.filter(crate::py::truthy) {
            env.insert("marker".into(), m);
        }
        Ok(Value::Object(env))
    }
}

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
    fn the_clock_spelling_is_pythons() {
        // the epoch · 2026-09-22 · a leap day · the last millisecond before one (values from CPython)
        assert_eq!(iso_millis(0), "1970-01-01T00:00:00.000Z");
        assert_eq!(iso_millis(1_790_035_200_000), "2026-09-22T00:00:00.000Z");
        assert_eq!(iso_millis(1_709_164_800_123), "2024-02-29T00:00:00.123Z");
        assert_eq!(iso_millis(951_782_399_999), "2000-02-28T23:59:59.999Z");
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
