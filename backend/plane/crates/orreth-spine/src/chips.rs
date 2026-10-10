// PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch Phase 8 THE WORKSHOP sp6, THE TWO CHIPS: the pure laws · 2026-10-09
//! THE TWO CHIPS (canon 0010 §8, lock 8 · 0005 Phase 8 sp6), PURE — the laws
//! `orreth_spine.chips` keeps, word for word (fixture `chips-v0.json`): the trial life's CLAIMS
//! against the kernel's record (who · what · where · left) and their words; the candidate's DIFF
//! against the standing version (the capabilities widened and narrowed, the graph, the mind, the
//! policy, the binding, the summon word) and its words; the FORM each chip's verdict takes
//! (`identity: kept | broken` · `security: clear | concern`) and how it is read off the words; a
//! chip's line on the proposal card and what holds a promotion; THE KEY-CHECK's law — when a seated
//! body is due, the bytes it signs (the join desk's challenge, repeated), the kernel's verdict on
//! its proof, the kernel's seventh watch, the glass's line. The ground half is `chips_live`.

use regex::Regex;
use serde_json::{json, Value};
use std::sync::OnceLock;

use crate::py::{python_str, truthy};

pub const CONTRACT: &str = "orreth.chips/1";
pub const KERNEL: &str = "the kernel";
pub const IDENTITY: &str = "identity";
pub const SECURITY: &str = "security";
pub const CHIPS: [&str; 2] = [IDENTITY, SECURITY];
pub const IDENTITY_WORDS: [&str; 2] = ["kept", "broken"];
pub const SECURITY_WORDS: [&str; 2] = ["clear", "concern"];
pub const CLAIMS: [&str; 4] = ["who", "what", "where", "left"];

pub const KEYCHECK_CMD: &str = "orreth.resident.keycheck.v1";
pub const KEYCHECK_ASKED: &str = "orreth.keycheck.asked.v1";
pub const KEYCHECK_VERDICT: &str = "orreth.keycheck.v1";
pub const CADENCE_DIAL: &str = "SPINE_KEYCHECK_S";
pub const CADENCE_DEFAULT: i64 = 300;
pub const WAIT_S: f64 = crate::desk::NONCE_S;
pub const KEYCHECK_WATCH: &str = "key_checks_failed";
pub const KEYCHECK_WINDOW_H: i64 = 24;
pub const KEYCHECK_EVERY_S: u64 = 10;

/// A template's `function` → the reviewer it is (`chips.FUNCTIONS`).
pub fn reviewer_of_function(function: &str) -> Option<&'static str> {
    match function {
        "identify" => Some(IDENTITY),
        "secure" => Some(SECURITY),
        _ => None,
    }
}

/// Eight characters of a declaration hash AFTER its `sha256:` prefix (W113: `sha256:0` said nothing).
fn h8(v: &Value) -> String {
    let s = if v.is_null() { String::new() } else { python_str(v) };
    let s = s.strip_prefix("sha256:").map(str::to_string).unwrap_or(s);
    if s.is_empty() {
        "?".into()
    } else {
        s.chars().take(8).collect()
    }
}

fn claim(name: &str, kept: bool, said: String) -> Value {
    json!({"claim": name, "kept": kept, "said": said})
}

/// `chips.lease_claims`: THE TRIAL LIFE'S CLAIMS against the kernel's record — four, each `{claim, kept, said}`.
pub fn lease_claims(exp: &Value, trial: &Value, standing_did: Option<&str>) -> Value {
    if trial.is_null() {
        return Value::Array(
            CLAIMS
                .iter()
                .map(|c| claim(c, false, "no trial life joined the experiment room — the candidate never stood".into()))
                .collect(),
        );
    }
    let mut out = Vec::new();
    let did = python_str(&trial["did"]);
    match standing_did {
        None => out.push(claim("who", true, format!("joined as {did} — the first life of this self; no standing life to compare"))),
        Some(s) if s == did => out.push(claim(
            "who",
            true,
            format!("joined as {did} — the same self as the standing life (life {})", python_str(&trial["life"])),
        )),
        Some(s) => out.push(claim("who", false, format!("joined as {did} but the standing life is {s} — another self (rule 1)"))),
    }
    let want = &exp["candidate_hash"];
    if trial["template_hash"] == *want {
        out.push(claim("what", true, format!("stood on the candidate's declaration ({})", h8(want))));
    } else {
        out.push(claim("what", false, format!("said it was {} but the candidate is {}", h8(&trial["template_hash"]), h8(want))));
    }
    if trial["scope"] == exp["room"] {
        out.push(claim("where", true, "stood in the experiment room, nowhere else".into()));
    } else {
        out.push(claim(
            "where",
            false,
            format!("stood at {} — not the experiment room {}", python_str(&trial["scope"]), python_str(&exp["room"])),
        ));
    }
    if truthy(&trial["wear_open"]) {
        out.push(claim("left", false, "its wear is still open — the trial life did not stop whole".into()));
    } else {
        out.push(claim("left", true, "left the room — its wear closed when it stopped".into()));
    }
    Value::Array(out)
}

/// `chips.claims_words`: the claims in one line.
pub fn claims_words(claims: &Value) -> String {
    let all: Vec<&Value> = claims.as_array().map(|a| a.iter().collect()).unwrap_or_default();
    let broken = all.iter().filter(|c| !truthy(&c["kept"])).count();
    let head = if broken == 0 { "every claim kept".to_string() } else { format!("{broken} of {} claims broken", all.len()) };
    let body: Vec<String> = all.iter().map(|c| format!("{} — {}", python_str(&c["claim"]), python_str(&c["said"]))).collect();
    format!("{head}: {}", body.join("; "))
}

fn caps(m: &Value) -> Vec<String> {
    let mut v: Vec<String> = m["capabilities"].as_array().map(|a| a.iter().map(python_str).collect()).unwrap_or_default();
    v.sort();
    v.dedup();
    v
}

fn mind_of(m: &Value) -> Value {
    let mind = &m["mind"];
    if truthy(&mind["pin"]) {
        mind["pin"].clone()
    } else if truthy(&mind["model"]) {
        mind["model"].clone()
    } else {
        Value::Null
    }
}

/// `chips.capability_diff`: THE CANDIDATE'S DIFF against the standing version's manifest.
pub fn capability_diff(current: &Value, candidate: &Value) -> Value {
    let first = current.is_null();
    let (a, b) = (caps(current), caps(candidate));
    let widened: Vec<&String> = b.iter().filter(|c| !a.contains(c)).collect();
    let narrowed: Vec<&String> = a.iter().filter(|c| !b.contains(c)).collect();
    let mut d = json!({"first": first, "widened": widened, "narrowed": narrowed,
                       "graph": null, "mind": null, "policy": null, "binding": null, "summonable": null});
    for key in ["graph", "policy", "binding"] {
        let (x, y) = (&current[key], &candidate[key]);
        if x != y {
            d[key] = json!([x, y]);
        }
    }
    let (x, y) = (mind_of(current), mind_of(candidate));
    if x != y {
        d["mind"] = json!([x, y]);
    }
    let (x, y) = (truthy(&current["summonable"]), truthy(&candidate["summonable"]));
    if x != y {
        d["summonable"] = json!([x, y]);
    }
    d
}

fn unset(v: &Value) -> String {
    if truthy(v) {
        python_str(v)
    } else {
        "unset".into()
    }
}

/// `chips.diff_words`: the diff in plain words.
pub fn diff_words(diff: &Value) -> String {
    let mut bits: Vec<String> = Vec::new();
    if truthy(&diff["first"]) {
        bits.push("a first version — every capability it declares is new".into());
    }
    let list = |v: &Value| v.as_array().map(|a| a.iter().map(python_str).collect::<Vec<_>>().join(", ")).unwrap_or_default();
    if truthy(&diff["widened"]) {
        bits.push(format!("WIDENED: {}", list(&diff["widened"])));
    }
    if truthy(&diff["narrowed"]) {
        bits.push(format!("narrowed: {}", list(&diff["narrowed"])));
    }
    for (key, word) in [("graph", "the graph"), ("mind", "the mind"), ("policy", "the policy"), ("binding", "the binding")] {
        let v = &diff[key];
        if truthy(v) {
            bits.push(format!("{word} {} → {}", unset(&v[0]), unset(&v[1])));
        }
    }
    if truthy(&diff["summonable"]) {
        bits.push(format!("summonable {}", if truthy(&diff["summonable"][1]) { "now" } else { "no longer" }));
    }
    if bits.is_empty() {
        return "nothing changes in what the candidate may do — the same capabilities, graph, mind and policy".into();
    }
    bits.join("; ")
}

/// `chips.review_form`: the form a chip's answer takes.
pub fn review_form(reviewer: &str) -> &'static str {
    if reviewer == IDENTITY {
        "Judge whether the trial life is WHO and WHAT it says — the claims above are the kernel's record. End with exactly one line `identity: kept` or `identity: broken` — <one line of reason>."
    } else {
        "Judge what the candidate may do that the standing version may not, and whether anything on the refusals ground speaks against it. End with exactly one line `security: clear` or `security: concern` — <one line of reason>."
    }
}

fn identity_rx() -> &'static Regex {
    static RX: OnceLock<Regex> = OnceLock::new();
    RX.get_or_init(|| Regex::new(r"(?im)^\s*\**\s*identity\s*\**\s*:\s*\**\s*(kept|broken)\b").unwrap())
}

fn security_rx() -> &'static Regex {
    static RX: OnceLock<Regex> = OnceLock::new();
    RX.get_or_init(|| Regex::new(r"(?im)^\s*\**\s*security\s*\**\s*:\s*\**\s*(clear|concern)\b").unwrap())
}

fn line_after(text: &str, head: &str) -> Value {
    for ln in text.lines() {
        let lead = ln.trim_start_matches(['*', ' ']).to_lowercase();
        if lead.starts_with(&format!("{head}:")) && ln.contains('—') {
            let tail = ln.splitn(2, '—').nth(1).unwrap_or("").trim().trim_end_matches('*').trim();
            return if tail.is_empty() { Value::Null } else { json!(tail) };
        }
    }
    Value::Null
}

/// `chips.identity_of`: `{identity, line}` — None where the form was not kept.
pub fn identity_of(text: &str) -> Value {
    match identity_rx().captures(text) {
        Some(c) => json!({"identity": c[1].to_lowercase(), "line": line_after(text, "identity")}),
        None => json!({"identity": null, "line": null}),
    }
}

/// `chips.security_of`: `{security, line}`.
pub fn security_of(text: &str) -> Value {
    match security_rx().captures(text) {
        Some(c) => json!({"security": c[1].to_lowercase(), "line": line_after(text, "security")}),
        None => json!({"security": null, "line": null}),
    }
}

/// `chips.verdict_of`: a chip's verdict and whether the form was kept.
pub fn verdict_of(reviewer: &str, text: &str) -> (Value, bool) {
    if reviewer == IDENTITY {
        let v = identity_of(text);
        let kept = !v["identity"].is_null();
        (v, kept)
    } else {
        let v = security_of(text);
        let kept = !v["security"].is_null();
        (v, kept)
    }
}

/// `chips.slot_words`: one chip's line on the proposal card.
pub fn slot_words(reviewer: &str, slot: &Value) -> String {
    let line = |w: String| if truthy(&slot["line"]) { format!("{w}: {}", python_str(&slot["line"])) } else { w };
    let missing = |fallback: &str| if truthy(&slot["missing"]) { python_str(&slot["missing"]) } else { fallback.to_string() };
    if reviewer == IDENTITY {
        if truthy(&slot["identity"]) {
            return line(format!("the identity chip finds the trial life's claims {}", python_str(&slot["identity"])));
        }
        return format!("the identity chip: {}", missing("no verdict yet"));
    }
    if truthy(&slot["security"]) {
        return line(format!("the security chip reads the candidate as {}", python_str(&slot["security"])));
    }
    format!("the security chip: {}", missing("no review yet"))
}

/// `chips.chip_holds`: what the chips say that HOLDS a promotion.
pub fn chip_holds(reviewers: &Value) -> Vec<String> {
    let mut out = Vec::new();
    if reviewers[IDENTITY]["identity"] == json!("broken") {
        out.push("the identity chip finds the trial life's claims broken".to_string());
    }
    if reviewers[SECURITY]["security"] == json!("concern") {
        out.push("the security chip reads a concern".to_string());
    }
    out
}

// ---- the key-check law ----

/// `chips.cadence_s`: the dial; 0 turns the cadence off.
pub fn cadence_s() -> i64 {
    std::env::var(CADENCE_DIAL).ok().and_then(|v| v.trim().parse::<i64>().ok()).map(|v| v.max(0)).unwrap_or(CADENCE_DEFAULT)
}

/// `chips.keycheck_due`: never with the cadence off; at once when never asked; else past the cadence.
pub fn keycheck_due(last_asked_s_ago: Option<f64>, cadence: i64) -> bool {
    if cadence <= 0 {
        return false;
    }
    match last_asked_s_ago {
        None => true,
        Some(ago) => ago >= cadence as f64,
    }
}

/// `chips.keycheck_payload`: the bytes the body signs — the join desk's challenge, repeated.
pub fn keycheck_payload(did: &str, nonce: &str) -> Value {
    crate::desk::challenge_payload(did, nonce)
}

/// `chips.keycheck_verdict`: the kernel's verdict on a check — `{ok, words}`; `ok` null while waiting.
pub fn keycheck_verdict(did: &str, nonce: &str, answer: &Value, joined_as: Option<&str>, waited_s: f64) -> Value {
    if answer.is_null() {
        if waited_s >= WAIT_S {
            return json!({"ok": false, "words": format!("silent — no proof within {} minutes of the kernel's challenge", (WAIT_S as i64) / 60)});
        }
        return json!({"ok": null, "words": "waiting for the body's proof"});
    }
    let pk = python_str(&answer["public_key"]);
    let what = if answer["what"].is_null() { String::new() } else { python_str(&answer["what"]) };
    if !crate::desk::prove(did, &pk, nonce, &answer["sig"]) {
        return json!({"ok": false, "words": "the signature does not stand over the kernel's nonce under the key behind this DID — not WHO it says"});
    }
    if let Some(j) = joined_as {
        if what != j {
            return json!({"ok": false, "words": format!("it says it stands on {} but joined as {} — not WHAT it says", h8(&json!(what)), h8(&json!(j)))});
        }
    }
    let tail: String = did.chars().rev().take(8).collect::<Vec<_>>().into_iter().rev().collect();
    json!({"ok": true, "words": format!("proven — who it says ({tail}) and what it says ({})", h8(&json!(what)))})
}

/// `chips.keycheck_watch`: the kernel's seventh watch at light — `key_checks_failed > 0` is red.
pub fn keycheck_watch(failed: Option<i64>) -> Value {
    let state = match failed {
        None => "unknown",
        Some(f) if f > 0 => "red",
        Some(_) => "green",
    };
    let words = match failed {
        Some(f) if f > 0 => format!("{f} key-check{} failed in the last day — a seated body could not prove itself", if f != 1 { "s" } else { "" }),
        _ => "every seated body proved itself on the cadence".to_string(),
    };
    json!({"metric": KEYCHECK_WATCH, "op": ">", "threshold": 0, "severity": "red", "state": state, "words": words})
}

/// `chips.keycheck_words`: the glass's line on the key-check.
pub fn keycheck_words(checked: i64, failed: i64, pending: i64, cadence: i64) -> String {
    if cadence <= 0 {
        return "the key-check cadence is off (SPINE_KEYCHECK_S=0) — no body is asked to prove itself".into();
    }
    if checked == 0 && pending == 0 {
        return format!("no body has been asked to prove itself yet — every {cadence} s once one is seated");
    }
    let tail = if pending > 0 { format!("{pending} waiting") } else { "none waiting".to_string() };
    format!(
        "{checked} key-check{} in the last day, {failed} failed, {tail} — every seated body is asked every {cadence} s to prove who and what it is",
        if checked != 1 { "s" } else { "" }
    )
}

/// `chips.refusals_words`: THE REFUSALS GROUND in one line (the rows as `chips_live::refusals_for` reads them).
pub fn refusals_words(rows: &Value, name: Option<&str>) -> String {
    let who = match name {
        Some(n) => format!("for {n}"),
        None => "in this universe".to_string(),
    };
    let rows: Vec<&Value> = rows.as_array().map(|a| a.iter().collect()).unwrap_or_default();
    if rows.is_empty() {
        return format!("THE REFUSALS GROUND {who}: nothing in the last day — no body was turned away at the join or the desk");
    }
    let bits: Vec<String> = rows
        .iter()
        .map(|r| {
            let reasons = r["reasons"].as_array().map(|a| a.iter().map(python_str).collect::<Vec<_>>().join(", ")).unwrap_or_default();
            let door = if truthy(&r["door"]) { python_str(&r["door"]) } else { "the join".into() };
            let at: String = python_str(&r["at"]).chars().take(19).collect();
            format!("{} ({}) turned away at {door} {at}: {}", python_str(&r["name"]), python_str(&r["kind"]), crate::py::cut_chars(&reasons, 160))
        })
        .collect();
    format!("THE REFUSALS GROUND {who}: {} refusal{} in the last day — {}", rows.len(), if rows.len() != 1 { "s" } else { "" }, bits.join("; "))
}

/// `chips.seats_words`: THE SEATS as the identity chip holds them.
pub fn seats_words(s: &Value) -> String {
    let mut people: Vec<(String, i64)> =
        s["people"].as_object().map(|m| m.iter().map(|(k, v)| (k.clone(), v.as_i64().unwrap_or(0))).collect()).unwrap_or_default();
    people.sort();
    let ppl = if people.is_empty() {
        "nobody".to_string()
    } else {
        people.iter().map(|(role, n)| format!("{n} {role}")).collect::<Vec<_>>().join(", ")
    };
    let bodies = s["bodies"].as_i64().unwrap_or(0);
    let k = &s["keychecks"];
    let n = |key: &str| k[key].as_i64().unwrap_or(0);
    format!(
        "THE SEATS: {ppl} seated by the ceremony; {bodies} bod{} alive on a lease; {}",
        if bodies != 1 { "ies" } else { "y" },
        keycheck_words(n("checked"), n("failed"), n("pending"), n("cadence"))
    )
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn the_forms_read() {
        assert_eq!(identity_of("fine.\n**identity: KEPT** — the same self")["identity"], json!("kept"));
        assert_eq!(identity_of("fine.\n**identity: KEPT** — the same self")["line"], json!("the same self"));
        assert_eq!(security_of("security: concern — a tool widened")["security"], json!("concern"));
        assert!(security_of("no form").get("security").unwrap().is_null());
        assert_eq!(verdict_of(IDENTITY, "identity: broken").1, true);
    }

    #[test]
    fn the_diff_speaks() {
        let d = capability_diff(&json!({"capabilities": ["ask"], "graph": "bob.v0"}), &json!({"capabilities": ["ask", "tools:propose"], "graph": "bob.v1"}));
        assert_eq!(d["widened"], json!(["tools:propose"]));
        assert_eq!(diff_words(&d), "WIDENED: tools:propose; the graph bob.v0 → bob.v1");
        assert_eq!(diff_words(&capability_diff(&json!({"capabilities": ["ask"]}), &json!({"capabilities": ["ask"]}))),
                   "nothing changes in what the candidate may do — the same capabilities, graph, mind and policy");
    }

    #[test]
    fn the_check_is_due() {
        assert!(keycheck_due(None, 300) && keycheck_due(Some(301.0), 300) && !keycheck_due(Some(10.0), 300) && !keycheck_due(None, 0));
        assert_eq!(keycheck_verdict("did:orreth:agent:x", "n", &Value::Null, None, 10.0)["ok"], Value::Null);
        assert_eq!(keycheck_verdict("did:orreth:agent:x", "n", &Value::Null, None, 200.0)["ok"], json!(false));
    }
}
