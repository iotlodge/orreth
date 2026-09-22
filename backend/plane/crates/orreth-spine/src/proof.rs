// PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp1, the bytes · 2026-09-22
//! `orreth.proof/1` — the pure half of `orreth_spine.proof` and the stop's
//! demand from `orreth_spine.intent`: the code (TOTP per RFC 6238 — HMAC-SHA1,
//! 30 s steps, 6 digits, ±1 step of drift), the consequence ladder
//! (`routine < consequential < grave` → `L1 < L2 < L3`, the gravest with a
//! second named person as `L3-master`), and what the stop or restart of an
//! intention demands (W5 · W20: ANY stop is grave; the kernel's needs the
//! asker's code and THEN a declared master's click).
//!
//! The clock is the caller's: `totp` and `verify` take the unix time. The
//! doors (enroll · confirm · masters · the rest after three wrongs) live on a
//! ground and are sp3's.

use hmac::{Hmac, Mac};
use serde_json::{json, Value};
use sha1::Sha1;
use std::fmt;

/// The ladder, in order.
pub const CLASSES: [&str; 3] = ["routine", "consequential", "grave"];
/// The level each class demands.
pub const LEVEL_OF_CLASS: [(&str, &str); 3] =
    [("routine", "L1"), ("consequential", "L2"), ("grave", "L3")];

pub const STEP_S: u64 = 30;
pub const DIGITS: usize = 6;
pub const DRIFT: i64 = 1;

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum ProofError {
    /// `a consequence class is one of routine, consequential, grave`.
    UnknownClass(String),
    /// The secret is not base32.
    BadSecret(String),
}

impl fmt::Display for ProofError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            ProofError::UnknownClass(c) => {
                write!(
                    f,
                    "a consequence class is one of {} — not '{c}'",
                    CLASSES.join(", ")
                )
            }
            ProofError::BadSecret(why) => write!(f, "the secret is not base32: {why}"),
        }
    }
}

impl std::error::Error for ProofError {}

// ---- the ladder --------------------------------------------------------------------

/// A class's place on the ladder (0 · 1 · 2); an unknown class refuses.
pub fn rank(cls: &str) -> Result<usize, ProofError> {
    CLASSES
        .iter()
        .position(|c| *c == cls)
        .ok_or_else(|| ProofError::UnknownClass(cls.to_string()))
}

/// The bare level of a class: `L1` · `L2` · `L3`.
pub fn level_of_class(cls: &str) -> Result<&'static str, ProofError> {
    Ok(LEVEL_OF_CLASS[rank(cls)?].1)
}

/// The proof a class demands: routine → L1 · consequential → L2 · grave →
/// L3-code, or L3-master for the gravest (a second named person).
pub fn level_for(cls: &str, master: bool) -> Result<&'static str, ProofError> {
    let base = level_of_class(cls)?;
    if base != "L3" {
        return Ok(base);
    }
    Ok(if master { "L3-master" } else { "L3-code" })
}

/// The classes sorted up the ladder (`sorted(order, key=rank)`).
pub fn ladder<'a>(order: &[&'a str]) -> Result<Vec<&'a str>, ProofError> {
    let mut ranked: Vec<(usize, &str)> = order
        .iter()
        .map(|c| rank(c).map(|r| (r, *c)))
        .collect::<Result<_, _>>()?;
    ranked.sort_by_key(|(r, _)| *r); // stable, like Python's sort
    Ok(ranked.into_iter().map(|(_, c)| c).collect())
}

// ---- the stop's demand (intent.py: stop_demand · restart_demand) ------------------

/// What the stop (or restart) of an intention demands.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Demand {
    pub level: &'static str,
    pub needs_code: bool,
}

impl Demand {
    pub fn to_value(&self) -> Value {
        json!({"level": self.level, "needs_code": self.needs_code})
    }
}

/// W5 (JB's lock 2026-09-21): a human's or a role's intention rests on the
/// asker's CODE (L3-code); the kernel's needs the asker's code AND a declared
/// master's click (L3-master, `needs_code`). The order built: the code first,
/// then the master confirms.
pub fn stop_demand(intention_kind: &str) -> Demand {
    if intention_kind == "kernel" {
        Demand {
            level: "L3-master",
            needs_code: true,
        }
    } else {
        Demand {
            level: "L3-code",
            needs_code: true,
        }
    }
}

/// W20: the reverse of a grave act is grave — the restart climbs the stop's ladder.
pub fn restart_demand(intention_kind: &str) -> Demand {
    stop_demand(intention_kind)
}

// ---- the code (RFC 6238) -----------------------------------------------------------

const B32: &[u8; 32] = b"ABCDEFGHIJKLMNOPQRSTUVWXYZ234567";

/// `base64.b32decode(s.strip().replace(" ", "").upper() + padding)`: the RFC 4648
/// alphabet, spaces dropped, case folded, padding optional; anything else refuses.
pub fn base32_decode(secret: &str) -> Result<Vec<u8>, ProofError> {
    let s: String = secret
        .trim()
        .chars()
        .filter(|c| *c != ' ')
        .collect::<String>()
        .to_uppercase();
    let s = s.trim_end_matches('=');
    if matches!(s.len() % 8, 1 | 3 | 6) {
        return Err(ProofError::BadSecret("incorrect padding".into()));
    }
    let mut out = Vec::with_capacity(s.len() * 5 / 8);
    let (mut acc, mut bits) = (0u64, 0u32);
    for c in s.bytes() {
        let v = B32.iter().position(|b| *b == c).ok_or_else(|| {
            ProofError::BadSecret(format!("non-alphabet character {:?}", c as char))
        })?;
        acc = (acc << 5) | v as u64;
        bits += 5;
        if bits >= 8 {
            bits -= 8;
            out.push((acc >> bits) as u8);
            acc &= (1 << bits) - 1;
        }
    }
    Ok(out)
}

/// HOTP (RFC 4226) over HMAC-SHA1: dynamic truncation, `digits` decimal digits, zero-filled.
pub fn hotp(key: &[u8], counter: u64, digits: usize) -> String {
    let mut mac = Hmac::<Sha1>::new_from_slice(key).expect("HMAC takes a key of any length");
    mac.update(&counter.to_be_bytes());
    let mac = mac.finalize().into_bytes();
    let offset = (mac[19] & 0x0f) as usize;
    let code = u32::from_be_bytes([
        mac[offset],
        mac[offset + 1],
        mac[offset + 2],
        mac[offset + 3],
    ]) & 0x7fff_ffff;
    format!(
        "{:0width$}",
        code % 10u32.pow(digits as u32),
        width = digits
    )
}

/// The step a unix time falls in (`int(t // step)`).
fn step_of(t: f64) -> i64 {
    (t / STEP_S as f64).floor() as i64
}

/// The code at unix time `t` for a base32 secret.
pub fn totp(secret_b32: &str, t: f64) -> Result<String, ProofError> {
    let key = base32_decode(secret_b32)?;
    Ok(hotp(&key, step_of(t) as u64, DIGITS))
}

/// The current step and ±`drift` steps; constant-time compares; a malformed
/// code (or a secret that is not base32) is simply wrong.
pub fn verify(secret_b32: &str, code: Option<&str>, t: f64, drift: i64) -> bool {
    let Some(code) = code else { return false };
    let given = code.trim();
    if given.len() != DIGITS || !given.bytes().all(|b| b.is_ascii_digit()) {
        return false;
    }
    let Ok(key) = base32_decode(secret_b32) else {
        return false;
    };
    let step = step_of(t);
    let mut ok = false;
    for d in -drift..=drift {
        let Ok(counter) = u64::try_from(step + d) else {
            continue;
        };
        ok |= constant_time_eq(hotp(&key, counter, DIGITS).as_bytes(), given.as_bytes());
    }
    ok
}

/// `hmac.compare_digest` for two equal-length ASCII codes.
fn constant_time_eq(a: &[u8], b: &[u8]) -> bool {
    if a.len() != b.len() {
        return false;
    }
    let mut diff = 0u8;
    for (x, y) in a.iter().zip(b) {
        diff |= x ^ y;
    }
    diff == 0
}

#[cfg(test)]
mod tests {
    use super::*;

    const RFC_SECRET: &str = "GEZDGNBVGY3TQOJQGEZDGNBVGY3TQOJQ"; // "12345678901234567890"

    #[test]
    fn base32_reads_the_rfc_secret_with_spaces_case_and_padding_forgiven() {
        assert_eq!(base32_decode(RFC_SECRET).unwrap(), b"12345678901234567890");
        assert_eq!(
            base32_decode(" gezd gnbv GY3TQOJQGEZDGNBVGY3TQOJQ== ").unwrap(),
            b"12345678901234567890"
        );
        assert!(base32_decode("GEZD1").is_err()); // '1' is not in the alphabet
        assert!(base32_decode("G").is_err()); // an impossible length
    }

    #[test]
    fn the_ladder_sorts_stably_and_refuses_strangers() {
        assert_eq!(
            ladder(&["grave", "routine", "consequential"]).unwrap(),
            ["routine", "consequential", "grave"]
        );
        assert_eq!(level_for("grave", true).unwrap(), "L3-master");
        assert!(level_for("mild", false).is_err());
    }

    #[test]
    fn the_stop_and_the_restart_share_one_ladder() {
        assert_eq!(
            stop_demand("kernel"),
            Demand {
                level: "L3-master",
                needs_code: true
            }
        );
        assert_eq!(
            restart_demand("human"),
            Demand {
                level: "L3-code",
                needs_code: true
            }
        );
        assert_eq!(
            stop_demand("role").to_value(),
            serde_json::json!({"level": "L3-code", "needs_code": true})
        );
    }

    #[test]
    fn verify_refuses_the_malformed_and_the_far() {
        let code = totp(RFC_SECRET, 1111111111.0).unwrap();
        assert!(verify(RFC_SECRET, Some(&code), 1111111111.0, DRIFT));
        assert!(verify(
            RFC_SECRET,
            Some(&format!(" {code} ")),
            1111111111.0,
            DRIFT
        ));
        assert!(!verify(RFC_SECRET, Some("12345"), 1111111111.0, DRIFT));
        assert!(!verify(RFC_SECRET, Some("12345a"), 1111111111.0, DRIFT));
        assert!(!verify(RFC_SECRET, None, 1111111111.0, DRIFT));
        assert!(!verify(RFC_SECRET, Some(&code), 1111111111.0 + 61.0, DRIFT));
        assert!(!verify("not*base32", Some(&code), 1111111111.0, DRIFT));
    }
}
