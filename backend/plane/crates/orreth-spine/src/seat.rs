// PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp8 row 3, THE GATE (a): the human seat · 2026-09-26
//! `orreth.seat/1` — the pure half of `orreth_spine.seat` (canon 0005 sp8 row
//! 3 · 0006 §3 · covenant rules 3 and 4): THE HUMAN SEAT. A capability token
//! in the 0006 shape (subject · audience · grants · constraints{expiry,
//! direction} · chain · sig), attenuation-only, minted by a kernel self as the
//! universe root and verified offline through its fences in order (malformed ·
//! expired · foreign authority · broken chain · bad signature · amplified);
//! the seat's id and its wire form; the doors' needs (`open` · `enroll` ·
//! `retrieve` · `write` · `govern`); the closed origin; the person grammar;
//! the plain words. The fixture `spine/conformance/seat-v0.json` measures
//! every function here against the Python reference; the ground half — the
//! owner, the seats, the facts, the ceilings — is `seat_live`.

use crate::canonical::canonical;
use crate::hash::sha256_hex;
use crate::kernel_self::KernelSelf;
use crate::py::parse_iso_secs;
use ed25519_dalek::{Signature, Verifier, VerifyingKey};
use regex::Regex;
use serde_json::{json, Map, Value};

pub const CONTRACT: &str = "orreth.seat/1";
pub const ACTIONS: [&str; 8] = [
    "retrieve",
    "write",
    "distill",
    "interview",
    "govern",
    "transfer",
    "issue",
    "resolve",
];
pub const DIRECTIONS: [&str; 4] = ["down", "within", "up", "across"];
/// JB's lock, 2026-09-26: one proof a day.
pub const HOURS_DEFAULT: f64 = 24.0;
/// The doors' bucket (the seam keeps its own 5 · 20).
pub const CEILING_RATE_DEFAULT: f64 = 20.0;
pub const CEILING_BURST_DEFAULT: f64 = 60.0;

pub const SEAT_TAKEN: &str = "orreth.seat.taken.v1";
pub const SEAT_LEFT: &str = "orreth.seat.left.v1";
pub const OWNER_DECLARED: &str = "orreth.owner.declared.v1";
/// 0071's words at the ceiling (429).
pub const BUSY_WORDS: &str = "the door is busy for you — try again shortly";
pub const CEREMONY: &str = "the ceremony";

/// The unseated's one face (401).
pub fn not_seated() -> Value {
    json!({"error": "not seated"})
}

pub fn busy() -> Value {
    json!({"error": BUSY_WORDS, "retry_after_s": 1})
}

/// `did:orreth:<kind>:` + sha256(public)[..32].
pub fn did_of_key(kind: &str, public_key_hex: &str) -> Option<String> {
    let bytes = hex_decode(public_key_hex)?;
    Some(format!("did:orreth:{kind}:{}", &sha256_hex(&bytes)[..32]))
}

fn kind_of(did: &str) -> &str {
    let parts: Vec<&str> = did.split(':').collect();
    if parts.len() >= 4 && parts[0] == "did" && parts[1] == "orreth" {
        parts[2]
    } else {
        ""
    }
}

pub fn hex_decode(h: &str) -> Option<Vec<u8>> {
    if !h.len().is_multiple_of(2) {
        return None;
    }
    (0..h.len())
        .step_by(2)
        .map(|i| u8::from_str_radix(&h[i..i + 2], 16).ok())
        .collect()
}

fn sig_of(signer: &KernelSelf, payload: &Value) -> Value {
    json!({"alg": "ed25519", "by": signer.did(), "sig": signer.sign(payload)})
}

fn sig_ok(sig: &Value, payload: &Value, public_key_hex: &str) -> bool {
    if sig.get("alg").and_then(Value::as_str) != Some("ed25519") {
        return false;
    }
    let Some(public) = hex_decode(public_key_hex) else {
        return false;
    };
    let Ok(arr) = <[u8; 32]>::try_from(public.as_slice()) else {
        return false;
    };
    let Ok(key) = VerifyingKey::from_bytes(&arr) else {
        return false;
    };
    let Some(raw) = hex_decode(sig.get("sig").and_then(Value::as_str).unwrap_or_default()) else {
        return false;
    };
    let Ok(s) = Signature::from_slice(&raw) else {
        return false;
    };
    key.verify(&canonical(payload), &s).is_ok()
}

/// A scope path is within an ancestor when it is the ancestor or stands below it.
pub fn within(scope: &str, ancestor: &str) -> bool {
    scope == ancestor || scope.starts_with(&format!("{ancestor}/"))
}

fn space_within(space: &Value, parent: &Value) -> bool {
    if space == parent {
        return true;
    }
    match (space.get("scope"), parent.get("scope")) {
        (Some(Value::String(s)), Some(Value::String(p))) => within(s, p),
        _ => false,
    }
}

fn grants_within(grants: &[Value], parent: &[Value]) -> bool {
    grants.iter().all(|g| {
        parent.iter().any(|p| {
            g.get("action") == p.get("action")
                && space_within(
                    g.get("space").unwrap_or(&Value::Null),
                    p.get("space").unwrap_or(&Value::Null),
                )
        })
    })
}

fn content(token: &Value) -> Value {
    let mut m = Map::new();
    for k in ["subject", "audience", "grants", "constraints"] {
        m.insert(k.into(), token.get(k).cloned().unwrap_or(Value::Null));
    }
    Value::Object(m)
}

/// A capability token in the 0006 shape, one hop appended to `chain` (none: the
/// signer is the root and this is the first hop) — `seat.mint`, byte for byte.
#[allow(clippy::too_many_arguments)]
pub fn mint(
    signer: &KernelSelf,
    subject: &str,
    audience: &str,
    grants: &Value,
    expiry: &str,
    direction: &str,
    budget: Option<&Value>,
    chain: Option<&Value>,
) -> Result<Value, String> {
    if !DIRECTIONS.contains(&direction) {
        return Err(format!("direction is one of {}", DIRECTIONS.join(", ")));
    }
    for g in grants.as_array().cloned().unwrap_or_default() {
        if !ACTIONS.contains(&g.get("action").and_then(Value::as_str).unwrap_or_default()) {
            return Err(format!("a grant's action is one of {}", ACTIONS.join(", ")));
        }
    }
    let mut constraints = json!({"expiry": expiry, "direction": direction});
    if let Some(b) = budget.filter(|b| crate::py::truthy(b)) {
        constraints["budget"] = b.clone();
    }
    let mut hop = json!({"issuer": signer.did(), "public_key": signer.verify_key_hex(), "subject": subject,
                         "audience": audience, "grants": grants, "constraints": constraints});
    let hop_sig = sig_of(signer, &hop);
    hop["sig"] = hop_sig;
    let content = json!({"subject": subject, "audience": audience, "grants": grants, "constraints": constraints});
    let mut chain_v: Vec<Value> = chain.and_then(Value::as_array).cloned().unwrap_or_default();
    chain_v.push(Value::String(
        String::from_utf8(canonical(&hop)).unwrap_or_default(),
    ));
    let sig = sig_of(signer, &content);
    let mut out = content.as_object().cloned().unwrap_or_default();
    out.insert("chain".into(), Value::Array(chain_v));
    out.insert("sig".into(), sig);
    Ok(Value::Object(out))
}

/// A narrower token below this one, issued by the self that holds it.
pub fn attenuate(
    token: &Value,
    signer: &KernelSelf,
    subject: &str,
    grants: Option<&Value>,
    expiry: Option<&str>,
    audience: Option<&str>,
) -> Result<Value, String> {
    let c = &token["constraints"];
    mint(
        signer,
        subject,
        audience.unwrap_or(token["audience"].as_str().unwrap_or_default()),
        grants.unwrap_or(&token["grants"]),
        expiry.unwrap_or(c["expiry"].as_str().unwrap_or_default()),
        c["direction"].as_str().unwrap_or("within"),
        c.get("budget"),
        token.get("chain"),
    )
}

/// The verdict, in one word: `ok`, or the first fence that refused.
pub fn verify(token: &Value, root_did: &str, root_key_hex: &str, now: &str) -> String {
    verify_inner(token, root_did, root_key_hex, now).unwrap_or_else(|| "malformed".into())
}

fn verify_inner(token: &Value, root_did: &str, root_key_hex: &str, now: &str) -> Option<String> {
    let o = token.as_object()?;
    let mut keys: Vec<&str> = o.keys().map(String::as_str).collect();
    keys.sort_unstable();
    if keys
        != [
            "audience",
            "chain",
            "constraints",
            "grants",
            "sig",
            "subject",
        ]
    {
        return Some("malformed".into());
    }
    let c = token["constraints"].as_object()?;
    let grants = token["grants"].as_array()?;
    let chain = token["chain"].as_array()?;
    if grants.is_empty() || chain.is_empty() {
        return Some("malformed".into());
    }
    if !DIRECTIONS.contains(&c.get("direction")?.as_str()?) {
        return Some("malformed".into());
    }
    let expiry = parse_iso_secs(c.get("expiry")?.as_str()?)?;
    if expiry <= parse_iso_secs(now)? {
        return Some("expired".into());
    }
    let hops: Vec<Value> = chain
        .iter()
        .map(|h| serde_json::from_str::<Value>(h.as_str()?).ok())
        .collect::<Option<Vec<_>>>()?;
    let first = &hops[0];
    if first["issuer"].as_str() != Some(root_did)
        || first["public_key"].as_str() != Some(root_key_hex)
    {
        return Some("foreign authority".into());
    }
    let mut prev: Option<&Value> = None;
    for hop in &hops {
        let issuer = hop["issuer"].as_str().unwrap_or_default();
        let pk = hop["public_key"].as_str().unwrap_or_default();
        if let Some(p) = prev {
            if Some(issuer) != p["subject"].as_str()
                || did_of_key(kind_of(issuer), pk).as_deref() != Some(issuer)
            {
                return Some("broken chain".into());
            }
        }
        let mut body = hop.as_object()?.clone();
        body.remove("sig");
        if !sig_ok(&hop["sig"], &Value::Object(body), pk) {
            return Some("bad signature".into());
        }
        if let Some(p) = prev {
            let (pc, hc) = (&p["constraints"], &hop["constraints"]);
            let widened = !within(
                hop["audience"].as_str().unwrap_or_default(),
                p["audience"].as_str().unwrap_or_default(),
            ) || !grants_within(hop["grants"].as_array()?, p["grants"].as_array()?)
                || parse_iso_secs(hc["expiry"].as_str()?)?
                    > parse_iso_secs(pc["expiry"].as_str()?)?
                || hc["direction"] != pc["direction"];
            if widened {
                return Some("amplified".into());
            }
        }
        prev = Some(hop);
    }
    let last = hops.last()?;
    for k in ["subject", "audience", "grants", "constraints"] {
        if last.get(k) != token.get(k) {
            return Some("broken chain".into());
        }
    }
    if !sig_ok(
        &token["sig"],
        &content(token),
        last["public_key"].as_str().unwrap_or_default(),
    ) {
        return Some("bad signature".into());
    }
    Some("ok".into())
}

/// `seat_` + sha256(canonical token)[..16].
pub fn seat_id(token: &Value) -> String {
    format!("seat_{}", &sha256_hex(&canonical(token))[..16])
}

const B64: &[u8; 64] = b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_";

/// base64url of the canonical bytes, unpadded.
pub fn wire(token: &Value) -> String {
    let bytes = canonical(token);
    let mut out = String::with_capacity(bytes.len().div_ceil(3) * 4);
    for chunk in bytes.chunks(3) {
        let n = chunk.len();
        let b = [
            chunk[0],
            *chunk.get(1).unwrap_or(&0),
            *chunk.get(2).unwrap_or(&0),
        ];
        let v = ((b[0] as u32) << 16) | ((b[1] as u32) << 8) | b[2] as u32;
        out.push(B64[(v >> 18) as usize & 63] as char);
        out.push(B64[(v >> 12) as usize & 63] as char);
        if n > 1 {
            out.push(B64[(v >> 6) as usize & 63] as char);
        }
        if n > 2 {
            out.push(B64[v as usize & 63] as char);
        }
    }
    out
}

/// The wire back to the token, or None.
pub fn unwire(s: &str) -> Option<Value> {
    let s = s.trim().trim_end_matches('=');
    let mut bytes = Vec::with_capacity(s.len() * 3 / 4);
    let mut acc: u32 = 0;
    let mut bits = 0;
    for ch in s.bytes() {
        let v = match ch {
            b'A'..=b'Z' => ch - b'A',
            b'a'..=b'z' => ch - b'a' + 26,
            b'0'..=b'9' => ch - b'0' + 52,
            b'-' | b'+' => 62,
            b'_' | b'/' => 63,
            _ => return None,
        } as u32;
        acc = (acc << 6) | v;
        bits += 6;
        if bits >= 8 {
            bits -= 8;
            bytes.push((acc >> bits) as u8);
            acc &= (1 << bits) - 1;
        }
    }
    let v: Value = serde_json::from_slice(&bytes).ok()?;
    v.is_object().then_some(v)
}

/// `authorization: Bearer <wire>` → the wire, or None.
pub fn bearer(header: Option<&str>) -> Option<String> {
    let h = header?.trim();
    let (scheme, rest) = h.split_once(char::is_whitespace)?;
    let rest = rest.trim();
    (scheme.eq_ignore_ascii_case("bearer") && !rest.is_empty()).then(|| rest.to_string())
}

/// What a seat may do here: read and write within this world; the owner and a master also govern.
pub fn grants_for(role: &str, scope: &str) -> Value {
    let space = json!({"scope": scope});
    let mut out = vec![
        json!({"action": "retrieve", "space": space}),
        json!({"action": "write", "space": space}),
    ];
    if role == "owner" || role == "master" {
        out.push(json!({"action": "govern", "space": space}));
    }
    Value::Array(out)
}

pub const OPEN_GET: [&str; 6] = ["/", "/index.html", "/health", "/guide", "/harness", "/seat"];
pub const OPEN_POST: [&str; 4] = ["/seat", "/enroll/confirm", "/seam", "/delta"];
pub const GOVERN_POST: [&str; 13] = [
    "/world/rehome",
    "/bodies/restart",
    "/services",
    "/services/version",
    "/services/retire",
    "/services/restore",
    "/services/mcp",
    "/minds",
    "/minds/assign",
    "/minds/unassign",
    "/minds/refill",
    "/minds/retire",
    "/minds/restore",
];

/// What a door asks of the one who knocks: `open` · `enroll` · `retrieve` · `write` · `govern`.
pub fn door_needs(method: &str, path: &str) -> &'static str {
    match method.to_ascii_uppercase().as_str() {
        "GET" => {
            if OPEN_GET.contains(&path) {
                "open"
            } else {
                "retrieve"
            }
        }
        "POST" => {
            if path == "/enroll" {
                "enroll"
            } else if OPEN_POST.contains(&path) {
                "open"
            } else if GOVERN_POST.contains(&path) {
                "govern"
            } else {
                "write"
            }
        }
        _ => "write",
    }
}

/// The browser origin is closed: an Origin is served only when it IS this door.
pub fn origin_ok(origin: Option<&str>, host: Option<&str>) -> bool {
    let Some(o) = origin.filter(|o| !o.is_empty()) else {
        return true;
    };
    let h = host.unwrap_or_default().trim().to_ascii_lowercase();
    if h.is_empty() {
        return false;
    }
    let o = o.trim().to_ascii_lowercase();
    o == format!("http://{h}") || o == format!("https://{h}")
}

/// persons.py's grammar: lower-case, 2–24 of a-z 0-9 _ -, a letter first.
pub fn person_did(text: Option<&str>) -> Option<String> {
    let t = text.unwrap_or_default().trim();
    let rx = Regex::new(r"^[a-z][a-z0-9_-]{1,23}$").ok()?;
    if let Some(name) = t.strip_prefix("did:orreth:person:") {
        return rx.is_match(name).then(|| t.to_string());
    }
    rx.is_match(t).then(|| format!("did:orreth:person:{t}"))
}

/// The words on a seat taken (`seat.taken_words`).
pub fn taken_words(person: &str, role: &str, hours: f64, ceremony: bool) -> String {
    let name = person.rsplit(':').next().unwrap_or(person);
    let base = if ceremony {
        format!("you hold this ground now, {name} — the first to prove an authenticator here is its owner")
    } else {
        format!("seated, {name}")
    };
    let r = match role {
        "owner" => "the owner",
        "master" => "a master",
        _ => "a person",
    };
    let h = if hours.fract() == 0.0 {
        format!("{}", hours as i64)
    } else {
        crate::py::python_str(&json!(hours))
    };
    format!("{base} · your seat is {r}'s for {h} hours; say “leave my seat” to end it sooner")
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn wire_round_trips_and_a_bad_wire_is_none() {
        let t = json!({"a": 1, "b": [1, 2, 3], "c": "x/y"});
        assert_eq!(unwire(&wire(&t)), Some(t));
        assert_eq!(unwire("!!!"), None);
        assert_eq!(unwire(&wire(&json!("s"))), None);
    }

    #[test]
    fn a_seat_minted_here_verifies_and_a_widened_hop_is_amplified() {
        let root = KernelSelf::from_seed(&[7u8; 32], "kernel");
        let t = mint(
            &root,
            "did:orreth:person:jb",
            "u:dev",
            &grants_for("owner", "u:dev"),
            "2026-09-27T18:00:00.000Z",
            "within",
            None,
            None,
        )
        .unwrap();
        let now = "2026-09-26T18:00:00.000Z";
        assert_eq!(verify(&t, &root.did(), &root.verify_key_hex(), now), "ok");
        assert_eq!(
            verify(
                &t,
                &root.did(),
                &root.verify_key_hex(),
                "2026-09-28T00:00:00.000Z"
            ),
            "expired"
        );
        let body = KernelSelf::from_seed(&[9u8; 32], "agent");
        let lease = mint(
            &root,
            &body.did(),
            "u:dev",
            &grants_for("person", "u:dev"),
            "2026-09-27T18:00:00.000Z",
            "within",
            None,
            None,
        )
        .unwrap();
        let wide = attenuate(
            &lease,
            &body,
            "did:orreth:agent:x",
            Some(&grants_for("owner", "u:dev")),
            None,
            None,
        )
        .unwrap();
        assert_eq!(
            verify(&wide, &root.did(), &root.verify_key_hex(), now),
            "amplified"
        );
    }
}
