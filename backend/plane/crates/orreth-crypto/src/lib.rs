//! Real crypto from day one (0000 §3): canonical JSON + sha256 content-addressing + Ed25519.
//!
//! Canonicalization matches the Python reference (`orreth_sim.crypto`) BYTE-FOR-BYTE:
//! sorted keys, compact separators, and Python's `ensure_ascii` escaping (`\uXXXX` for
//! all non-ASCII, surrogate pairs beyond the BMP). The conformance vectors in
//! `conformance/fixtures/crypto.json` are the proof.

use base64::engine::general_purpose::URL_SAFE_NO_PAD;
use base64::Engine;
use ed25519_dalek::{Signature, Verifier, VerifyingKey};
use serde_json::Value;
use sha2::{Digest, Sha256};
use std::fmt::Write as _;

/// Canonical JSON: sorted keys (serde_json's Map is a BTreeMap), no whitespace,
/// Python-compatible string escaping and float formatting (ryu keeps the trailing `.0`).
pub fn canonical(v: &Value) -> String {
    let mut out = String::new();
    write_canonical(v, &mut out);
    out
}

pub fn content_hash(v: &Value) -> String {
    format!("sha256:{:x}", Sha256::digest(canonical(v).as_bytes()))
}

fn write_canonical(v: &Value, out: &mut String) {
    match v {
        Value::Null => out.push_str("null"),
        Value::Bool(b) => out.push_str(if *b { "true" } else { "false" }),
        // serde_json's number formatting (ryu) prints 1.0 as "1.0", matching Python's repr
        Value::Number(n) => out.push_str(&n.to_string()),
        Value::String(s) => write_escaped(s, out),
        Value::Array(items) => {
            out.push('[');
            for (i, item) in items.iter().enumerate() {
                if i > 0 {
                    out.push(',');
                }
                write_canonical(item, out);
            }
            out.push(']');
        }
        Value::Object(map) => {
            out.push('{');
            for (i, (k, val)) in map.iter().enumerate() {
                if i > 0 {
                    out.push(',');
                }
                write_escaped(k, out);
                out.push(':');
                write_canonical(val, out);
            }
            out.push('}');
        }
    }
}

fn write_escaped(s: &str, out: &mut String) {
    out.push('"');
    for c in s.chars() {
        match c {
            '"' => out.push_str("\\\""),
            '\\' => out.push_str("\\\\"),
            '\n' => out.push_str("\\n"),
            '\r' => out.push_str("\\r"),
            '\t' => out.push_str("\\t"),
            '\u{08}' => out.push_str("\\b"),
            '\u{0c}' => out.push_str("\\f"),
            c if (c as u32) < 0x20 => {
                let _ = write!(out, "\\u{:04x}", c as u32);
            }
            c if c.is_ascii() => out.push(c),
            c => {
                // Python ensure_ascii: \uXXXX for the BMP, surrogate pairs beyond it
                let cp = c as u32;
                if cp > 0xFFFF {
                    let v = cp - 0x10000;
                    let _ = write!(out, "\\u{:04x}\\u{:04x}", 0xd800 + (v >> 10), 0xdc00 + (v & 0x3ff));
                } else {
                    let _ = write!(out, "\\u{:04x}", cp);
                }
            }
        }
    }
    out.push('"');
}

/// Verify a `Sig` (common.schema.json) over `canonical(payload minus "sig"/"signature")`.
/// `public` is the reference format: `'z'` + urlsafe-b64 (no pad) raw Ed25519 key.
pub fn verify_sig(sig_b64: &str, payload: &Value, public: &str) -> bool {
    let body = match payload {
        Value::Object(map) => {
            let filtered: serde_json::Map<String, Value> = map
                .iter()
                .filter(|(k, _)| k.as_str() != "sig" && k.as_str() != "signature")
                .map(|(k, v)| (k.clone(), v.clone()))
                .collect();
            Value::Object(filtered)
        }
        other => other.clone(),
    };
    let Some(stripped) = public.strip_prefix('z') else { return false };
    let (Ok(key_bytes), Ok(sig_bytes)) = (
        URL_SAFE_NO_PAD.decode(stripped),
        URL_SAFE_NO_PAD.decode(sig_b64),
    ) else {
        return false;
    };
    let (Ok(key_arr), Ok(sig_arr)) = (
        <[u8; 32]>::try_from(key_bytes.as_slice()),
        <[u8; 64]>::try_from(sig_bytes.as_slice()),
    ) else {
        return false;
    };
    let Ok(key) = VerifyingKey::from_bytes(&key_arr) else { return false };
    key.verify(canonical(&body).as_bytes(), &Signature::from_bytes(&sig_arr))
        .is_ok()
}
