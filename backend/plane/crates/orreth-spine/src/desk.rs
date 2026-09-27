// PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp8 row 3, THE GATE (b): the machine join desk, the pure law · 2026-09-26
//! THE MACHINE JOIN DESK — `orreth_spine.desk`'s pure half, law for law (canon 0005
//! sp8 row 3b · 0006 §2–3 · 0012 · covenant rule 3), measured by `desk-v0`:
//! the five statuses and their transitions, the challenge's bytes (`{did, join_nonce}`,
//! the old SDK's shape carried), the proof's verdict (the declared key derives the DID
//! it claims, the signature stands over the desk's OWN nonce), the lease (`seat::mint`
//! to the body's DID with the fuel clause — the Stable's dollars per window — in its
//! budget), the collect's bytes, and the words. The ground half is `desk_live`.

use crate::kernel_self::KernelSelf;
use crate::seat;
use serde_json::{json, Value};

pub const CONTRACT: &str = "orreth.desk/1";
pub const STATUSES: [&str; 6] = [
    "pending",
    "challenged",
    "proved",
    "staged",
    "done",
    "denied",
];
/// What may knock: a body (a service is the keeper's to register).
pub const KINDS: [&str; 1] = ["agent"];

pub const JOIN_ASKED: &str = "orreth.join.asked.v1";
pub const JOIN_PROVED: &str = "orreth.join.proved.v1";
pub const JOIN_ADMITTED: &str = "orreth.join.admitted.v1";
pub const JOIN_DENIED: &str = "orreth.join.denied.v1";

/// The kernel-held act (the human's yes): a click, cancel the default.
pub const ADMIT_TOOL: &str = "join.admit";
pub const ADMIT_CLASS: &str = "consequential";
pub const ADMIT_LEVEL: &str = "L2";
pub const REFUSED_WORDS: &str = "join refused";
pub const BY_MANIFEST: &str = "the crew manifest";
pub const LEASE_DAYS_DIAL: &str = "SPINE_JOIN_LEASE_DAYS";
pub const LEASE_DAYS_DEFAULT: i64 = 30;
/// A challenge is answered within two minutes, else re-challenged.
pub const NONCE_S: f64 = 120.0;
pub const SPAWN_TICKET_DIAL: &str = "SPINE_SPAWN_TICKET";

/// The desk's one face — a prober learns nothing.
pub fn refused() -> Value {
    json!({"error": REFUSED_WORDS})
}

/// May `to` follow `from`? A settled word is never rewritten; a challenge may be
/// re-issued from any open status; `proved` answers only a `challenged`; the
/// human's word lands on a `staged` join; the same status again is idempotent.
pub fn transition_legal(from: &str, to: &str) -> bool {
    if !STATUSES.contains(&from) || !STATUSES.contains(&to) {
        return false;
    }
    if from == "done" || from == "denied" {
        return false;
    }
    if from == to {
        return true;
    }
    match to {
        "challenged" => matches!(from, "pending" | "proved" | "staged"),
        "proved" => from == "challenged",
        "staged" => from == "proved",
        "done" => matches!(from, "proved" | "staged"),
        "denied" => true,
        _ => false,
    }
}

/// The bytes the joiner signs.
pub fn challenge_payload(did: &str, nonce: &str) -> Value {
    json!({"did": did, "join_nonce": nonce})
}

/// The bytes that collect the lease — the same key, a different sentence.
pub fn collect_payload(did: &str, join_id: &str, nonce: &str) -> Value {
    json!({"did": did, "join": join_id, "join_nonce": nonce})
}

/// A body's answer to a challenge (the proof's own side, for the proofs).
pub fn proof_of(signer: &KernelSelf, nonce: &str) -> Value {
    seat::sig_of(signer, &challenge_payload(&signer.did(), nonce))
}

pub fn collect_sig(signer: &KernelSelf, join_id: &str, nonce: &str) -> Value {
    seat::sig_of(signer, &collect_payload(&signer.did(), join_id, nonce))
}

/// The desk's verdict on a proof: the declared key derives the DID it claims (the
/// kind read from the DID, and a kind that may knock), and the signature stands over
/// the desk's OWN nonce.
pub fn prove(did: &str, public_key_hex: &str, nonce: &str, sig: &Value) -> bool {
    let kind = seat::kind_of(did);
    if !KINDS.contains(&kind) {
        return false;
    }
    if seat::did_of_key(kind, public_key_hex).as_deref() != Some(did) {
        return false;
    }
    seat::sig_ok(sig, &challenge_payload(did, nonce), public_key_hex)
}

pub fn collect_ok(
    did: &str,
    public_key_hex: &str,
    join_id: &str,
    nonce: &str,
    sig: &Value,
) -> bool {
    seat::sig_ok(sig, &collect_payload(did, join_id, nonce), public_key_hex)
}

/// What a lease may do here: the body reads and writes what is its own.
pub fn lease_grants() -> Value {
    json!([{"action": "retrieve", "space": "self"}, {"action": "write", "space": "self"}])
}

/// The lease's fuel: dollars per window; `renew_days` 0 is the old lump.
pub fn fuel_clause(usd: f64, renew_days: i64) -> Value {
    let mut c = json!({"cost": usd});
    if renew_days > 0 {
        c["renew_days"] = json!(renew_days);
    }
    c
}

/// The body's lease: one hop from the kernel's own self.
pub fn lease(
    signer: &KernelSelf,
    did: &str,
    scope: &str,
    expiry: &str,
    usd: f64,
    renew_days: i64,
) -> Result<Value, String> {
    seat::mint(
        signer,
        did,
        scope,
        &lease_grants(),
        expiry,
        "within",
        Some(&fuel_clause(usd, renew_days)),
        None,
    )
}

pub fn lease_days() -> i64 {
    std::env::var(LEASE_DAYS_DIAL)
        .ok()
        .and_then(|v| v.parse::<f64>().ok())
        .map(|d| (d as i64).max(1))
        .unwrap_or(LEASE_DAYS_DEFAULT)
}

/// `join_` + sha256(did · "\n" · nonce)[..12].
pub fn join_id_of(did: &str, nonce: &str) -> String {
    let h = crate::hash::sha256_hex(format!("{did}\n{nonce}").as_bytes());
    format!("join_{}", &h[..12])
}

/// A body's name: lower-case, 2–32 of a-z 0-9 _ -, a letter first.
pub fn name_ok(name: &str) -> bool {
    let b = name.as_bytes();
    (2..=32).contains(&b.len())
        && b[0].is_ascii_lowercase()
        && b.iter()
            .all(|c| c.is_ascii_lowercase() || c.is_ascii_digit() || *c == b'_' || *c == b'-')
}

/// The desk's plain words at each status.
pub fn words(status: &str, name: &str, scope: &str, by: Option<&str>) -> String {
    match status {
        "challenged" => {
            "sign this nonce with the key behind your DID — the door answers proof, not claims"
                .to_string()
        }
        "staged" => format!("{name} proved its key — the door waits for a governing seat's yes"),
        "done" => {
            let tail = by.map(|b| format!(" · {b}")).unwrap_or_default();
            format!("lease granted — welcome to {scope}, {name}{tail}")
        }
        "denied" => REFUSED_WORDS.to_string(),
        _ => format!("{name} asks to join {scope}"),
    }
}

/// Whose word admitted a proven key.
pub fn admitted_by(ticket: bool, welcome: Option<&str>, person: Option<&str>) -> String {
    if ticket {
        return format!("admitted on {BY_MANIFEST} — this kernel spawned this body");
    }
    if let Some(w) = welcome.filter(|w| !w.is_empty()) {
        return format!("admitted on its standing welcome ({w}) — the same self, the same world");
    }
    let who = person
        .and_then(|p| p.rsplit(':').next())
        .filter(|w| !w.is_empty())
        .unwrap_or("a governing seat");
    format!("admitted on {who}'s word")
}

/// The text the kernel's hold carries — plain, for the person who will click.
pub fn hold_words(name: &str, kind: &str, template_hash: &str, days: i64) -> String {
    let tail = template_hash.rsplit(':').next().unwrap_or_default();
    let short = if tail.is_empty() {
        "unknown".to_string()
    } else {
        tail.chars().take(8).collect()
    };
    format!(
        "{name} (a {kind}) asks to join this world — its key is proven, its template {short}. A yes gives it a LEASE for {days} days: its own words on the feed and nothing more, fueled by the Stable's allowance; a no turns it away. Cancel is the default."
    )
}
