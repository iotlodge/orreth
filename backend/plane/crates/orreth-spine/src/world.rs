// PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp3, the ask road · 2026-09-22
// Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp4, the loops: the kernel-required face · the proof's demand · 2026-09-23
//! The world a bridge process stands in — its scope (`SPINE_SCOPE`), its
//! benches (`SPINE_QUEUE_NS`), its rails — carried explicitly so a test can
//! stand two worlds in one process; and the small idioms every live module
//! shares: the road's refusals, Python's `isoformat` for a `timestamptz`
//! (the ground's clock is UTC, as the dev rig's is), and the text-JSON
//! columns the Python spine writes with `json.dumps`.

use crate::rail_error::RailError;
use crate::rails;
use serde_json::Value;
use std::fmt;
use std::time::{SystemTime, UNIX_EPOCH};

/// The dials, read once at birth (the Python spine reads them per call;
/// with the same environment the two agree).
#[derive(Debug, Clone)]
pub struct World {
    pub scope: String,
    pub ns: String,
    pub pg_dsn: String,
    pub rabbit_url: String,
    pub kafka: String,
}

impl World {
    /// `SPINE_SCOPE` · `SPINE_QUEUE_NS` · `SPINE_PG` · `SPINE_RABBIT` · `SPINE_KAFKA`.
    pub fn from_env() -> World {
        World {
            scope: rails::scope(),
            ns: rails::queue_ns(),
            pg_dsn: rails::pg_dsn(),
            rabbit_url: rails::rabbit_url(),
            kafka: rails::kafka_bootstrap(),
        }
    }
}

/// The road's refusals — each one a door's answer, never a bare code.
#[derive(Debug)]
pub enum RoadError {
    /// A rail refused.
    Rail(RailError),
    /// Rule 4: the one face (`{"error": "not confirmed"}`, 403); `rest` is the
    /// inward word — the third wrong proof rested the act.
    NotConfirmed { rest: bool },
    /// The door's plain refusal in words (400).
    Refused(String),
    /// A door this spine does not yet serve — named, never silent (501).
    NotYet(String),
    /// Kernel-required — visible, never editable (403, in words).
    Forbidden(String),
    /// A grave act asked bare: the door HOLDS it at this level instead
    /// (`proof.ProofRequired`) — `what` is the act in words, `needs_code` the
    /// kernel's demand for the asker's code before the master's click.
    ProofRequired {
        level: &'static str,
        what: String,
        needs_code: bool,
    },
}

impl fmt::Display for RoadError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            RoadError::Rail(e) => write!(f, "{e}"),
            RoadError::NotConfirmed { .. } => f.write_str("not confirmed"),
            RoadError::Refused(w) | RoadError::NotYet(w) | RoadError::Forbidden(w) => {
                f.write_str(w)
            }
            RoadError::ProofRequired { level, what, .. } => write!(f, "{what} needs {level}"),
        }
    }
}

impl std::error::Error for RoadError {}

impl From<RailError> for RoadError {
    fn from(e: RailError) -> Self {
        RoadError::Rail(e)
    }
}

impl From<tokio_postgres::Error> for RoadError {
    fn from(e: tokio_postgres::Error) -> Self {
        RoadError::Rail(RailError::Ground(e))
    }
}

impl From<crate::envelope::EnvelopeError> for RoadError {
    fn from(e: crate::envelope::EnvelopeError) -> Self {
        RoadError::Rail(RailError::Envelope(e))
    }
}

/// `RoadError::Refused` from a sentence.
pub fn refused(words: impl Into<String>) -> RoadError {
    RoadError::Refused(words.into())
}

/// Twelve random bytes as hex — `secrets.token_hex(n)`.
pub fn token_hex(n: usize) -> String {
    use rand::RngCore;
    let mut bytes = vec![0u8; n];
    rand::thread_rng().fill_bytes(&mut bytes);
    bytes.iter().map(|b| format!("{b:02x}")).collect()
}

/// Howard Hinnant's civil-from-days (proleptic Gregorian, days since 1970-01-01).
fn civil_from_days(z: i64) -> (i64, u32, u32) {
    let z = z + 719_468;
    let era = z.div_euclid(146_097);
    let doe = z.rem_euclid(146_097);
    let yoe = (doe - doe / 1460 + doe / 36_524 - doe / 146_096) / 365;
    let y = yoe + era * 400;
    let doy = doe - (365 * yoe + yoe / 4 - yoe / 100);
    let mp = (5 * doy + 2) / 153;
    let d = (doy - (153 * mp + 2) / 5 + 1) as u32;
    let m = if mp < 10 { mp + 3 } else { mp - 9 } as u32;
    (if m <= 2 { y + 1 } else { y }, m, d)
}

/// Python's `datetime.isoformat()` for an aware UTC time as psycopg hands it
/// back from a `timestamptz` on a UTC ground: `YYYY-MM-DDTHH:MM:SS[.ffffff]+00:00`
/// — the microseconds only when they are not zero.
pub fn isoformat(t: SystemTime) -> String {
    let d = t.duration_since(UNIX_EPOCH).unwrap_or_default();
    let secs = d.as_secs() as i64;
    let micros = d.subsec_micros();
    let (y, m, day) = civil_from_days(secs.div_euclid(86_400));
    let sod = secs.rem_euclid(86_400);
    let (h, mi, s) = (sod / 3600, sod % 3600 / 60, sod % 60);
    if micros == 0 {
        format!("{y:04}-{m:02}-{day:02}T{h:02}:{mi:02}:{s:02}+00:00")
    } else {
        format!("{y:04}-{m:02}-{day:02}T{h:02}:{mi:02}:{s:02}.{micros:06}+00:00")
    }
}

/// `isoformat` of an optional time — `None` stays `null`.
pub fn iso_opt(t: Option<SystemTime>) -> Value {
    t.map(|t| Value::String(isoformat(t)))
        .unwrap_or(Value::Null)
}

/// A text column the Python spine filled with `json.dumps` — `null`/empty is `None`.
pub fn json_text(s: Option<&str>) -> Option<Value> {
    s.filter(|s| !s.is_empty())
        .and_then(|s| serde_json::from_str(s).ok())
}

/// `json.loads(x or "[]")` as a list of strings.
pub fn json_strings(s: Option<&str>) -> Vec<String> {
    json_text(s)
        .and_then(|v| v.as_array().cloned())
        .map(|a| a.iter().map(crate::py::python_str).collect())
        .unwrap_or_default()
}

/// The first `n` characters (Python's `text[:n]`).
pub fn head(s: &str, n: usize) -> String {
    s.chars().take(n).collect()
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::time::Duration;

    #[test]
    fn isoformat_is_pythons() {
        let t = UNIX_EPOCH + Duration::new(1_790_000_000, 123_456_000);
        assert_eq!(isoformat(t), "2026-09-21T14:13:20.123456+00:00");
        let t = UNIX_EPOCH + Duration::new(1_790_000_000, 0);
        assert_eq!(isoformat(t), "2026-09-21T14:13:20+00:00");
        assert_eq!(isoformat(UNIX_EPOCH), "1970-01-01T00:00:00+00:00");
    }
}
