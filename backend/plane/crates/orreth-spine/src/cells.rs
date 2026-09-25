// PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp7, cells · partition · isolation · hardening · 2026-09-25
//! `orreth.cells/1` — the pure half of `orreth_spine.cells` (canon 0002 rule
//! 8 · 0001 P9/P10 · JB's locks 2026-09-25): a CELL is one universe's
//! physical home; "cells = worlds". The topic wearing the cell's namespace,
//! the peers a cell names, a cell address at the head of an ask, the fencing
//! epoch, the world's homing fact, the SEAM's message (signed by a kernel
//! self, verified against a pinned DID through every fence in turn), the
//! plain words (parked · resumed · lag · sealed · re-homed) and the knock
//! ceiling. The fixture `spine/conformance/cells-v0.json` measures every
//! function here against the Python reference. The seam's live half — the
//! peers on the ground, the relay, the parking — is `cells_live`.

use crate::canonical::canonical;
use crate::hash::sha256_hex;
use crate::kernel_self::KernelSelf;
use crate::py::parse_iso_secs;
use ed25519_dalek::{Signature, Verifier, VerifyingKey};
use regex::Regex;
use serde_json::{json, Map, Value};

pub const CONTRACT: &str = "orreth.cells/1";
/// A universe stands in its home cell at an epoch — a fact.
pub const WORLD_HOMED: &str = "orreth.world.homed.v1";
/// The cross-cell message's own specversion.
pub const SEAM: &str = "orreth.seam/1";
pub const KERNEL: &str = "the kernel";
pub const DEFAULT_CELL: &str = "local";
/// A seam message older (or newer) than this is refused — replay's first fence.
pub const SEAM_WINDOW_S: i64 = 120;
/// Knocks per second a caller may sustain at a door, and the burst it may spend at once (0071).
pub const CEILING_RATE: f64 = 5.0;
pub const CEILING_BURST: f64 = 20.0;

/// The topic a fact rides on: the envelope's TYPE wearing the cell's
/// namespace the way a bench does — `orreth.ask.received.v1` alone in the
/// first cell, `orreth.ask.received.v1.two` in cell two.
pub fn topic_name(base: &str, ns: Option<&str>) -> String {
    match ns {
        Some(n) if !n.is_empty() => format!("{base}.{n}"),
        _ => base.to_string(),
    }
}

/// A peer this cell names: its name and its door.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Peer {
    pub cell: String,
    pub door: String,
}

impl Peer {
    pub fn to_value(&self) -> Value {
        json!({"cell": self.cell, "door": self.door})
    }
}

/// `SPINE_PEERS` → the peers this cell names: `name=door` pairs, comma
/// separated, a door an http(s) origin. A malformed pair is dropped by name.
pub fn peers_from(dial: Option<&str>) -> Vec<Peer> {
    let name_re = Regex::new(r"^[a-z0-9_-]+$").unwrap();
    let door_re = Regex::new(r"^https?://\S+$").unwrap();
    let mut out = Vec::new();
    for pair in dial.unwrap_or_default().split(',') {
        let pair = pair.trim();
        let Some((name, door)) = pair.split_once('=') else {
            continue;
        };
        let name = name.trim().to_lowercase();
        let door = door.trim().trim_end_matches('/').to_string();
        if name_re.is_match(&name) && door_re.is_match(&door) {
            out.push(Peer { cell: name, door });
        }
    }
    out
}

/// Where an ask is addressed when it names a CELL: "librarian@two, …" ·
/// "two/librarian: …" · "@librarian@two …" → (cell, name), both lower-cased;
/// a bare name at the head is this world's own rule and reads `None` here.
pub fn address_home(text: &str) -> Option<(String, String)> {
    let at = Regex::new(r"^\s*@?([A-Za-z0-9_-]+)@([A-Za-z0-9_-]+)\s*[,:]\s*\S").unwrap();
    if let Some(c) = at.captures(text) {
        return Some((c[2].to_lowercase(), c[1].to_lowercase()));
    }
    let slash = Regex::new(r"^\s*([A-Za-z0-9_-]+)/([A-Za-z0-9_-]+)\s*[,:]\s*\S").unwrap();
    slash
        .captures(text)
        .map(|c| (c[1].to_lowercase(), c[2].to_lowercase()))
}

/// The words the home cell serves: the cell address rewritten as a plain one
/// ("librarian@two, hello" → "librarian, hello").
pub fn strip_home(text: &str) -> String {
    let at =
        Regex::new(r"(?s)^(\s*)@?([A-Za-z0-9_-]+)@([A-Za-z0-9_-]+)(\s*[,:]\s*)(\S.*)$").unwrap();
    if let Some(c) = at.captures(text) {
        return format!("{}{}{}", &c[2], &c[4], &c[5]);
    }
    let slash =
        Regex::new(r"(?s)^(\s*)([A-Za-z0-9_-]+)/([A-Za-z0-9_-]+)(\s*[,:]\s*)(\S.*)$").unwrap();
    if let Some(c) = slash.captures(text) {
        return format!("{}{}{}", &c[3], &c[4], &c[5]);
    }
    text.to_string()
}

/// The fencing law: `current` · `stale` (the sender's home moved on — it may
/// not commit) · `future` (I am the one behind — refresh my pin first).
pub fn epoch_check(mine: i64, theirs: i64) -> &'static str {
    if theirs == mine {
        "current"
    } else if theirs < mine {
        "stale"
    } else {
        "future"
    }
}

/// The homing fact's payload: the universe as the pointer, the (cell, epoch) hashed.
pub fn world_payload(
    scope: &str,
    cell: &str,
    epoch: i64,
    kernel_did: &str,
    door: &str,
    reason: &str,
) -> Value {
    json!({
        "ref": scope,
        "hash": crate::content_hash(&json!({"cell": cell, "epoch": epoch})),
        "cell": cell, "epoch": epoch, "kernel": kernel_did, "door": door, "reason": reason,
    })
}

/// `orreth.world.homed.v1` — minted now, the kernel's own chain, the world as correlation.
#[cfg(feature = "rails")]
pub fn world_fact(
    scope: &str,
    cell: &str,
    epoch: i64,
    kernel_did: &str,
    door: &str,
    reason: &str,
) -> Result<Value, crate::envelope::EnvelopeError> {
    crate::envelope::Mint {
        kind: "event".into(),
        r#type: WORLD_HOMED.into(),
        universe_id: scope.into(),
        scope_path: scope.into(),
        payload: world_payload(scope, cell, epoch, kernel_did, door, reason),
        correlation_id: Some(scope.into()),
        authority_chain: Some(vec![KERNEL.into()]),
        aggregate: None,
        marker: None,
    }
    .mint()
}

/// One message across the seam, unsigned.
#[allow(clippy::too_many_arguments)]
pub fn seam_message(
    from_cell: &str,
    from_world: &str,
    to_cell: &str,
    epoch: i64,
    kind: &str,
    body: Value,
    nonce: &str,
    at: &str,
) -> Value {
    json!({
        "specversion": SEAM, "from": from_cell, "world": from_world, "to": to_cell,
        "epoch": epoch, "kind": kind, "body": body, "nonce": nonce, "at": at,
    })
}

fn unsigned_part(msg: &Value) -> Value {
    let mut m = Map::new();
    if let Some(o) = msg.as_object() {
        for (k, v) in o {
            if k != "signer" && k != "public_key" && k != "signature" {
                m.insert(k.clone(), v.clone());
            }
        }
    }
    Value::Object(m)
}

/// The message signed by a kernel self — Ed25519 over the canonical bytes of
/// the message without its signature fields; the signer's DID and key beside it.
pub fn seam_sign(msg: &Value, signer: &KernelSelf) -> Value {
    let m = unsigned_part(msg);
    let mut out = m.as_object().cloned().unwrap_or_default();
    out.insert("signer".into(), json!(signer.did()));
    out.insert("public_key".into(), json!(signer.verify_key_hex()));
    out.insert("signature".into(), json!(signer.sign(&m)));
    Value::Object(out)
}

fn hex_decode(h: &str) -> Option<Vec<u8>> {
    if !h.len().is_multiple_of(2) {
        return None;
    }
    (0..h.len())
        .step_by(2)
        .map(|i| u8::from_str_radix(&h[i..i + 2], 16).ok())
        .collect()
}

/// `did:orreth:kernel:` + sha256(public)[..32].
pub fn did_of_key(public_key_hex: &str) -> Option<String> {
    let bytes = hex_decode(public_key_hex)?;
    Some(format!("did:orreth:kernel:{}", &sha256_hex(&bytes)[..32]))
}

/// The seam's gate, one verdict in words: `ok`, or the first fence that
/// refused — `unknown signer` · `bad signature` · `replayed` · `too old` ·
/// `too new` · `stale epoch` · `future epoch`.
pub fn seam_verify(
    signed: &Value,
    pinned_did: Option<&str>,
    now: &str,
    seen_nonces: &[String],
    epoch: Option<i64>,
) -> String {
    seam_verify_inner(signed, pinned_did, now, seen_nonces, epoch, SEAM_WINDOW_S)
        .unwrap_or_else(|| "bad signature".to_string())
}

fn seam_verify_inner(
    signed: &Value,
    pinned_did: Option<&str>,
    now: &str,
    seen_nonces: &[String],
    epoch: Option<i64>,
    window_s: i64,
) -> Option<String> {
    if signed.get("specversion").and_then(Value::as_str) != Some(SEAM) {
        return Some("bad signature".into());
    }
    let pk = signed
        .get("public_key")
        .and_then(Value::as_str)
        .unwrap_or_default();
    let did = signed
        .get("signer")
        .and_then(Value::as_str)
        .unwrap_or_default();
    let of_key = did_of_key(pk)?;
    match pinned_did {
        Some(p) if !p.is_empty() && did == p && of_key == did => {}
        _ => return Some("unknown signer".into()),
    }
    let m = unsigned_part(signed);
    let public = hex_decode(pk)?;
    let key = VerifyingKey::from_bytes(&<[u8; 32]>::try_from(public.as_slice()).ok()?).ok()?;
    let sig_hex = signed
        .get("signature")
        .and_then(Value::as_str)
        .unwrap_or_default();
    let sig = Signature::from_bytes(&<[u8; 64]>::try_from(hex_decode(sig_hex)?.as_slice()).ok()?);
    if key.verify(&canonical(&m), &sig).is_err() {
        return Some("bad signature".into());
    }
    let nonce = signed
        .get("nonce")
        .and_then(Value::as_str)
        .unwrap_or_default();
    if seen_nonces.iter().any(|n| n == nonce) {
        return Some("replayed".into());
    }
    let at = parse_iso_secs(signed.get("at").and_then(Value::as_str)?)?;
    let now_s = parse_iso_secs(now)?;
    let dt = at - now_s;
    if dt < -window_s {
        return Some("too old".into());
    }
    if dt > window_s {
        return Some("too new".into());
    }
    if let Some(mine) = epoch {
        let theirs = signed.get("epoch").and_then(Value::as_i64).unwrap_or(0);
        let v = epoch_check(mine, theirs);
        if v != "current" {
            return Some(format!("{v} epoch"));
        }
    }
    Some("ok".into())
}

/// The plain words on an ask whose home cell does not answer.
pub fn park_words(name: &str, cell: &str, since_hhmm: &str) -> String {
    format!(
        "{name}@{cell} is out of reach — cell {cell} has not answered since {since_hhmm}; \
         your ask is parked and will go the moment it answers"
    )
}

pub fn resumed_words(name: &str, cell: &str) -> String {
    format!("cell {cell} answers again — your ask to {name}@{cell} is on its way")
}

/// A peer's one line in the glass.
pub fn lag_words(
    cell: &str,
    world: Option<&str>,
    behind_s: Option<f64>,
    unreachable_since: Option<&str>,
) -> String {
    let who = match world {
        Some(w) if !w.is_empty() => format!("cell {cell} · {w}"),
        _ => format!("cell {cell}"),
    };
    if let Some(u) = unreachable_since.filter(|u| !u.is_empty()) {
        return format!("{who} · unreachable since {u}");
    }
    match behind_s {
        None => format!("{who} · not yet heard"),
        Some(b) if b < 1.0 => format!("{who} · live"),
        Some(b) => format!("{who} · {} s behind", b.round_ties_even() as i64),
    }
}

/// The harness's tenth check: this cell's role reaches its own database and no other.
pub fn sealed_words(role: &str, own_db: &str, reachable: &[String]) -> (bool, String) {
    let mut others: Vec<&String> = reachable.iter().filter(|d| d.as_str() != own_db).collect();
    others.sort();
    if others.is_empty() {
        return (true, format!("the role {role} reaches only {own_db}"));
    }
    (
        false,
        format!(
            "the role {role} reaches {} databases: {own_db}, {} — unsealed (the dev profile); seal it with scripts/dev.sh cell",
            others.len() + 1,
            others
                .iter()
                .map(|s| s.as_str())
                .collect::<Vec<_>>()
                .join(", ")
        ),
    )
}

/// A knock ceiling per caller: a token bucket that refills `rate` a second up
/// to `burst`; a knock spends one; an empty bucket refuses.
pub fn ceiling(tokens: f64, last_at: f64, now: f64, rate: f64, burst: f64) -> (bool, f64) {
    let have = burst.min(tokens + (now - last_at).max(0.0) * rate);
    if have >= 1.0 {
        (true, have - 1.0)
    } else {
        (false, have)
    }
}

pub fn rehome_words(scope: &str, from_cell: &str, to_cell: &str, epoch: i64) -> String {
    format!(
        "{scope} is re-homed from cell {from_cell} to cell {to_cell} at epoch {epoch} — \
         a kernel still wearing epoch {} may not commit for it",
        epoch - 1
    )
}
