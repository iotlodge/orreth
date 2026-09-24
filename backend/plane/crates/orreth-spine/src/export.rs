// PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp1, the bytes · 2026-09-22
// Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp5, memory and the export: seal · to_csv · the kernel's own kind · 2026-09-24
//! `orreth.compliance/1` — the pure half of `orreth_spine.export`: the hash
//! chain over a bundle's rows, a row's chain status judged from its own
//! fields, and `verify` — everything a stranger can recompute (the chain and
//! its root, every status, the summary's counts, the Ed25519 signature when
//! one is worn). Building a bundle reads a ground and is sp5's.

use crate::canonical::canonical;
use crate::hash::sha256_hex;
use crate::kernel_self::KernelSelf;
use crate::py::{get, truthy};
use ed25519_dalek::{Signature, Verifier, VerifyingKey};
use regex::Regex;
use serde_json::{json, Map, Value};
use sha2::{Digest, Sha256};
use std::sync::OnceLock;

pub const WORDS_MAX: usize = 500;
pub const CSV_COLUMNS: [&str; 18] = [
    "at",
    "kind",
    "ref",
    "person",
    "authority_chain",
    "chain_status",
    "proof",
    "marker_kind",
    "marker_id",
    "marker_parent",
    "marker_root",
    "served_by",
    "tool",
    "words",
    "words_truncated",
    "placement",
    "target",
    "marker_words",
];

pub const CONTRACT: &str = "orreth.compliance/1";
pub const HASHING: &str = "sha256; h0 = sha256(canonical(row0)); \
h_i = sha256(ascii_hex(h_{i-1}) || canonical(row_i)); root_hash = h_last";

/// `h0 = sha256(canonical(row0))`; `h_i = sha256(ascii_hex(h_{i-1}) || canonical(row_i))`
/// — the previous digest's lowercase hex, as ASCII bytes, prepended to the
/// row's canonical bytes. The root is the last; an empty bundle has none.
pub fn hash_chain(rows: &[Value]) -> Vec<String> {
    let mut out = Vec::with_capacity(rows.len());
    let mut prev: Vec<u8> = Vec::new();
    for row in rows {
        let mut h = Sha256::new();
        h.update(&prev);
        h.update(canonical(row));
        let hex = format!("{:x}", h.finalize());
        prev = hex.as_bytes().to_vec();
        out.push(hex);
    }
    out
}

/// The root of a chain: its last hash, or none for an empty bundle.
pub fn root_hash(chain: &[String]) -> Option<&str> {
    chain.last().map(String::as_str)
}

/// Judged from the row's own fields, never from elsewhere: a chain is intact
/// when it exists, begins with the origin human (`person`), and — where a body
/// acted (`served_by`) — ends with that body. A `proof` row wears only its
/// prover (a master is never the asker), so it is intact when present.
pub fn chain_status(row: &Value) -> &'static str {
    let chain = get(row, "authority_chain");
    let hops = match chain {
        Value::Array(a) if !a.is_empty() => a,
        _ => return "broken",
    };
    if get(row, "kind").as_str() == Some("proof") {
        return "intact";
    }
    if hops[0] != *get(row, "person") {
        return "broken";
    }
    let served = get(row, "served_by");
    if truthy(served) && hops[hops.len() - 1] != *served {
        return "broken";
    }
    "intact"
}

/// The part of a bundle a signer signs (`export._signed_part`); absent parts refuse.
pub fn signed_part(bundle: &Value) -> Option<Value> {
    Some(json!({
        "contract": bundle.get("contract")?,
        "root_hash": bundle.get("root_hash")?,
        "generated_at": bundle.get("generated_at")?,
        "world": bundle.get("world")?,
        "rows": bundle.get("rows")?.as_array()?.len(),
    }))
}

fn hex_decode(s: &str) -> Option<Vec<u8>> {
    if !s.len().is_multiple_of(2) {
        return None;
    }
    (0..s.len())
        .step_by(2)
        .map(|i| u8::from_str_radix(s.get(i..i + 2)?, 16).ok())
        .collect()
}

/// `"did:orreth:agent:" + sha256(pub).hexdigest()[:32]` — the self a key names.
pub fn did_of(public_key: &[u8]) -> String {
    did_of_kind(public_key, "agent")
}

/// `did:orreth:<kind>:` + sha256(public)[..32] — a body's, a service's, the kernel's.
pub fn did_of_kind(public_key: &[u8], kind: &str) -> String {
    format!("did:orreth:{kind}:{}", &sha256_hex(public_key)[..32])
}

/// `export.seal`: rows → a bundle — statuses re-derived, the summary counted,
/// the hash chain drawn, the root SIGNED when a signer is given (the
/// kernel's own self, P7 sp5). `generated_at` is given by the caller (the
/// live door passes now).
pub fn seal(
    rows: &[Value],
    scope: &Value,
    world: &str,
    generated_at: &str,
    signer: Option<&KernelSelf>,
) -> Value {
    let mut rows: Vec<Value> = rows.to_vec();
    for r in rows.iter_mut() {
        let status = chain_status(r);
        r["chain_status"] = json!(status);
    }
    let mut by_kind: Map<String, Value> = Map::new();
    let mut by_proof: Map<String, Value> = Map::new();
    for r in &rows {
        let k = get(r, "kind").as_str().unwrap_or_default().to_string();
        let n = by_kind.get(&k).and_then(Value::as_i64).unwrap_or(0);
        by_kind.insert(k, json!(n + 1));
        let p = match get(r, "proof") {
            Value::String(s) if !s.is_empty() => s.clone(),
            _ => "-".to_string(),
        };
        let n = by_proof.get(&p).and_then(Value::as_i64).unwrap_or(0);
        by_proof.insert(p, json!(n + 1));
    }
    let chain = hash_chain(&rows);
    let broken = rows
        .iter()
        .filter(|r| get(r, "chain_status").as_str() == Some("broken"))
        .count();
    let withheld = rows
        .iter()
        .filter(|r| truthy(get(r, "words_withheld")))
        .count();
    let mut bundle = json!({
        "contract": CONTRACT, "scope": scope, "generated_at": generated_at, "world": world,
        "rows": rows,
        "summary": {"rows": chain.len(), "by_kind": by_kind, "by_proof": by_proof,
                    "chain_broken": broken, "words_withheld": withheld},
        "hashing": HASHING, "hash_chain": chain, "root_hash": root_hash(&chain),
        "signed_by": Value::Null, "signer_key": Value::Null, "signature": Value::Null,
    });
    if let Some(k) = signer {
        bundle["signed_by"] = json!(k.did());
        bundle["signer_key"] = json!(k.verify_key_hex());
        let part = signed_part(&bundle).unwrap_or(Value::Null);
        bundle["signature"] = json!(k.sign(&part));
    }
    bundle
}

fn re(pat: &'static str, cell: &'static OnceLock<Regex>) -> &'static Regex {
    cell.get_or_init(|| Regex::new(pat).unwrap())
}

/// `export._plain` (W10): plain words for a human's table — headings, bold,
/// italics, bullets and code ticks fall away; the JSON bundle keeps the exact words.
pub fn plain(text: &str) -> String {
    static H: OnceLock<Regex> = OnceLock::new();
    static B: OnceLock<Regex> = OnceLock::new();
    static I: OnceLock<Regex> = OnceLock::new();
    static L: OnceLock<Regex> = OnceLock::new();
    let t = re(r"(?m)^\s{0,3}#{1,6}\s+", &H).replace_all(text, "");
    let t = re(r"\*\*(.+?)\*\*", &B).replace_all(&t, "$1");
    let t = italics(&t, re(r"\*([^*\n]+)\*", &I));
    let t = re(r"(?m)^\s*[-*•]\s+", &L).replace_all(&t, "· ");
    t.replace('`', "").trim().to_string()
}

/// `(?<![\w*])\*([^*\n]+)\*(?![\w*])` without look-around: a starred run whose
/// neighbours are neither word characters nor stars.
fn italics(t: &str, star: &Regex) -> String {
    let bytes: Vec<char> = t.chars().collect();
    let mut out = String::new();
    let mut last = 0;
    for m in star.find_iter(t) {
        let (s, e) = (m.start(), m.end());
        let before = t[..s].chars().next_back();
        let after = t[e..].chars().next();
        let wordish =
            |c: Option<char>| c.is_some_and(|c| c.is_alphanumeric() || c == '_' || c == '*');
        if wordish(before) || wordish(after) {
            continue;
        }
        out.push_str(&t[last..s]);
        out.push_str(&m.as_str()[1..m.as_str().len() - 1]);
        last = e;
    }
    out.push_str(&t[last..]);
    let _ = bytes;
    out
}

fn csv_cell(s: &str) -> String {
    if s.contains(['"', ',', '\n', '\r']) {
        format!("\"{}\"", s.replace('"', "\"\""))
    } else {
        s.to_string()
    }
}

fn s_of(v: &Value) -> String {
    match v {
        Value::Null => String::new(),
        Value::String(s) => s.clone(),
        other => other.to_string(),
    }
}

/// `export.to_csv`: one line per row; the chain joined by ' → '; words cut at
/// 500 with an ellipsis and the cut marked in its own column; the words
/// column in plain words (W10), the why in words (W11). Python's csv writer
/// with `lineterminator="\n"`: a cell is quoted when it holds a quote, a
/// comma, or a line break.
pub fn to_csv(bundle: &Value) -> String {
    let mut out = String::new();
    out.push_str(&CSV_COLUMNS.join(","));
    out.push('\n');
    for r in bundle
        .get("rows")
        .and_then(Value::as_array)
        .cloned()
        .unwrap_or_default()
    {
        let m = get(&r, "marker");
        let mut words = match get(&r, "words") {
            Value::Object(o) => o
                .iter()
                .filter(|(_, v)| truthy(v))
                .map(|(k, v)| format!("{k}: {}", plain(v.as_str().unwrap_or_default())))
                .collect::<Vec<_>>()
                .join(" | "),
            _ => String::new(),
        };
        if truthy(get(&r, "words_withheld")) {
            words = format!("(withheld — {})", s_of(get(&r, "words_withheld")));
        }
        let cut = words.chars().count() > WORDS_MAX;
        if cut {
            words = format!("{}…", words.chars().take(WORDS_MAX).collect::<String>());
        }
        let chain = get(&r, "authority_chain")
            .as_array()
            .map(|a| a.iter().map(s_of).collect::<Vec<_>>().join(" → "))
            .unwrap_or_default();
        let placement = match get(&r, "placement") {
            Value::Object(p) => format!("{} · {}", s_of(&p["cell"]), s_of(&p["metal"])),
            _ => String::new(),
        };
        let cells = [
            s_of(get(&r, "at")),
            s_of(get(&r, "kind")),
            s_of(get(&r, "ref")),
            s_of(get(&r, "person")),
            chain,
            s_of(get(&r, "chain_status")),
            s_of(get(&r, "proof")),
            s_of(get(m, "kind")),
            s_of(get(m, "id")),
            s_of(get(m, "parent")),
            s_of(get(m, "root")),
            s_of(get(&r, "served_by")),
            s_of(get(&r, "tool")),
            words,
            if cut { "yes".into() } else { String::new() },
            placement,
            s_of(get(&r, "target")),
            plain(get(&r, "marker_words").as_str().unwrap_or_default()),
        ];
        out.push_str(
            &cells
                .iter()
                .map(|c| csv_cell(c))
                .collect::<Vec<_>>()
                .join(","),
        );
        out.push('\n');
    }
    out
}

/// Recompute everything a stranger can: the hash chain and root, every row's
/// chain status from its own fields, the summary's counts, and the signature
/// when one is worn. Any disagreement — or any part missing — is `false`.
pub fn verify(bundle: &Value) -> bool {
    verify_inner(bundle).unwrap_or(false)
}

fn verify_inner(bundle: &Value) -> Option<bool> {
    let rows = bundle.get("rows")?.as_array()?;
    if get(bundle, "contract").as_str() != Some(CONTRACT) {
        return Some(false);
    }
    if rows
        .iter()
        .any(|r| get(r, "chain_status").as_str() != Some(chain_status(r)))
    {
        return Some(false);
    }
    let chain = hash_chain(rows);
    let worn: Vec<&str> = get(bundle, "hash_chain")
        .as_array()?
        .iter()
        .map(|h| h.as_str())
        .collect::<Option<_>>()?;
    if worn != chain.iter().map(String::as_str).collect::<Vec<_>>() {
        return Some(false);
    }
    let root = get(bundle, "root_hash");
    let root_ok = match root_hash(&chain) {
        Some(h) => root.as_str() == Some(h),
        None => root.is_null(),
    };
    if !root_ok {
        return Some(false);
    }
    let summary = get(bundle, "summary");
    let summary = if truthy(summary) {
        summary
    } else {
        &Value::Null
    };
    let broken = rows
        .iter()
        .filter(|r| get(r, "chain_status").as_str() == Some("broken"))
        .count();
    if get(summary, "rows").as_f64() != Some(rows.len() as f64)
        || get(summary, "chain_broken").as_f64() != Some(broken as f64)
    {
        return Some(false);
    }
    let signature = get(bundle, "signature");
    if truthy(signature) {
        let public = hex_decode(bundle.get("signer_key")?.as_str()?)?;
        let signed_by = get(bundle, "signed_by").as_str().unwrap_or_default();
        // P7 sp5: the signer's DID by its hash, whatever its kind (the kernel's own)
        if !signed_by.starts_with("did:orreth:")
            || signed_by.rsplit(':').next() != Some(&sha256_hex(&public)[..32])
        {
            return Some(false);
        }
        let key = VerifyingKey::from_bytes(&<[u8; 32]>::try_from(public.as_slice()).ok()?).ok()?;
        let sig = Signature::from_bytes(
            &<[u8; 64]>::try_from(hex_decode(signature.as_str()?)?.as_slice()).ok()?,
        );
        if key.verify(&canonical(&signed_part(bundle)?), &sig).is_err() {
            return Some(false);
        }
    }
    Some(true)
}

#[cfg(test)]
mod tests {
    use super::*;

    /// The export fixture's sealed bundle, SIGNED by the Python reference
    /// (`Identity("fixture", bytes(range(32)))` · PyNaCl) — the fixture itself
    /// carries `signature: null`, so the signed branch is proven here against
    /// bytes the reference produced and verified.
    const SIGNED: &str = r#"{"contract":"orreth.compliance/1","generated_at":"2026-09-21T12:00:03.000Z","hash_chain":["ec085473250516f03ac52f567bae59da486f2a691c6e34dbe0f08a68281f2251","bb7ed1aa9ed6424442cbc457c567483e81dfdda6b80ffda354fc505a9f4615bf","d2600f4159ac3ef2706db49331a68f9ce377ae8e7cbad08c046e0379d302acf0"],"hashing":"sha256; h0 = sha256(canonical(row0)); h_i = sha256(ascii_hex(h_{i-1}) || canonical(row_i)); root_hash = h_last","root_hash":"d2600f4159ac3ef2706db49331a68f9ce377ae8e7cbad08c046e0379d302acf0","rows":[{"at":"2026-09-21T12:00:00.000Z","authority_chain":["did:orreth:person:jb"],"chain_status":"intact","kind":"ask","marker":{"id":"mk_000000000001","kind":"objective","parent":null,"root":"mk_000000000001"},"message_id":"msg_000000000000000000000001","person":"did:orreth:person:jb","proof":"L1","ref":"ask_0000000000000001","served_by":null,"words":{"ask":"what is on the shelf?"}},{"at":"2026-09-21T12:00:01.000Z","authority_chain":["did:orreth:person:jb","did:orreth:agent:0123456789abcdef0123456789abcdef"],"chain_status":"intact","kind":"reply","marker":{"id":"mk_000000000001","kind":"objective","parent":null,"root":"mk_000000000001"},"message_id":"msg_000000000000000000000002","person":"did:orreth:person:jb","proof":"L1","ref":"ask_0000000000000001","served_by":"did:orreth:agent:0123456789abcdef0123456789abcdef","words":{"reply":"Three books and a lamp."}},{"at":"2026-09-21T12:00:02.000Z","authority_chain":["did:orreth:person:jb","did:orreth:agent:0123456789abcdef0123456789abcdef","did:orreth:agent:fedcba9876543210fedcba9876543210"],"chain_status":"intact","kind":"include","marker":{"id":"mk_000000000002","kind":"thought","parent":"mk_000000000001","root":"mk_000000000001"},"message_id":"msg_000000000000000000000003","person":"did:orreth:person:jb","proof":"L1","ref":"ask_0000000000000002","served_by":"did:orreth:agent:fedcba9876543210fedcba9876543210","words":{"reply":"1. read the books 2. light the lamp"}}],"scope":{"person":"did:orreth:person:jb","session":"ses_000000000001"},"signature":"b1561c712ea732cf05c0f7e640e1d425ecf336840c9079bb5ac33922daa5119d9226e64dec7b2d0c4f07d7330e06bca31c475bd6ccc67374673f71859073880a","signed_by":"did:orreth:agent:56475aa75463474c0285df5dbf2bcab7","signer_key":"03a107bff3ce10be1d70dd18e74bc09967e4d6309ba50d5f1ddc8664125531b8","summary":{"by_kind":{"ask":1,"include":1,"reply":1},"by_proof":{"L1":3},"chain_broken":0,"rows":3,"words_withheld":0},"world":"u:fixture"}"#;

    #[test]
    fn a_signed_bundle_verifies_and_a_forged_one_does_not() {
        let bundle: Value = serde_json::from_str(SIGNED).unwrap();
        assert!(verify(&bundle));
        let mut bad = bundle.clone();
        bad["signature"] = json!("00".repeat(64));
        assert!(!verify(&bad));
        let mut bad = bundle.clone();
        bad["signed_by"] = json!(format!("did:orreth:agent:{}", "0".repeat(32)));
        assert!(!verify(&bad));
        let mut bad = bundle.clone();
        bad["world"] = json!("u:elsewhere"); // the signed part changed under the signature
        assert!(!verify(&bad));
        let mut unsigned = bundle.clone();
        unsigned["signature"] = Value::Null;
        assert!(verify(&unsigned)); // unsigned at the door, honestly — still a whole chain
    }

    #[test]
    fn an_empty_bundle_has_no_root_and_a_missing_part_refuses() {
        assert!(hash_chain(&[]).is_empty());
        assert_eq!(root_hash(&[]), None);
        assert!(!verify(&json!({"contract": CONTRACT})));
        assert!(verify(
            &json!({"contract": CONTRACT, "rows": [], "hash_chain": [], "root_hash": null,
                               "summary": {"rows": 0, "chain_broken": 0}})
        ));
    }

    #[test]
    fn chain_status_reads_the_row_alone() {
        assert_eq!(
            chain_status(&json!({"person": "H", "authority_chain": []})),
            "broken"
        );
        assert_eq!(
            chain_status(&json!({"person": "H", "authority_chain": ["X"]})),
            "broken"
        );
        assert_eq!(
            chain_status(&json!({"person": "H", "authority_chain": ["H"], "served_by": "B"})),
            "broken"
        );
        assert_eq!(
            chain_status(&json!({"person": "H", "authority_chain": ["H", "B"], "served_by": "B"})),
            "intact"
        );
        assert_eq!(
            chain_status(&json!({"person": "H", "authority_chain": ["H", "B"], "served_by": ""})),
            "intact"
        );
        assert_eq!(
            chain_status(&json!({"kind": "proof", "person": "H", "authority_chain": ["M"]})),
            "intact"
        );
    }
}
