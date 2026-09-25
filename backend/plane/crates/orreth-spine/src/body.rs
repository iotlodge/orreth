// PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp6, the bodies' seam · 2026-09-24
//! `orreth.bodies/1` — the pure laws of `orreth_spine.body` and the rail half
//! of `orreth_spine.harness` (P7 sp6, THE BODIES' SEAM), measured by
//! `spine/conformance/bodies-v0.json`: the wait before the n-th restart of a
//! body that died (`backoff_s`), the PARK law (`park_rule`: deaths inside the
//! window; at the strikes the kernel stops restarting — visibly), the plain
//! words of a parked body with the human's lever (`parked_words`, rule 13 ·
//! rule 11), the parked fact's payload (`parked_payload`), the shared verdict
//! of a harness run (`verdict`: a case passes when every expected word is in
//! the reply, case folded) and the kernel's ask of a body to run its golden
//! cases (`harness_command`, `orreth.resident.harness.v1`). The spawning and
//! the supervising are [`crate::bodies`]'s (feature `bridge`).

use crate::hash::content_hash;
use crate::py::{fold_ws, parse_iso_secs};
use serde_json::{json, Value};

/// Python's `text[:n]` — a plain cut, no ellipsis.
fn cut(s: &str, n: usize) -> String {
    s.chars().take(n).collect()
}

/// The kernel stopped restarting a body — a fact, with its evidence.
pub const PARKED: &str = "orreth.body.parked.v1";
/// The kernel asks a body to run its golden cases through its own graph.
pub const HARNESS_CMD: &str = "orreth.resident.harness.v1";
pub const KERNEL: &str = "the kernel";

pub const EXIT_STOPPED: i32 = 0;
/// Refused at birth (placement) — terminal, never restarted.
pub const EXIT_REFUSED: i32 = 3;
/// No covenant policy — terminal (AG-3).
pub const EXIT_NO_POLICY: i32 = 4;

pub const PARK_STRIKES: i64 = 3;
pub const PARK_WINDOW_S: i64 = 300;
pub const BACKOFF_CAP_S: f64 = 30.0;

/// `body.backoff_s`: 1 s after the first death, doubling, capped.
pub fn backoff_s(deaths: i64) -> f64 {
    if deaths <= 0 {
        return 0.0;
    }
    let raw = 2f64.powi((deaths - 1).min(30) as i32);
    raw.min(BACKOFF_CAP_S)
}

/// `body.park_rule`: `{parked, deaths, wait_s}` — the deaths at or after
/// `now - window` counted; at `strikes`, PARKED.
pub fn park_rule(exits: &[String], now: &str, window_s: i64, strikes: i64) -> Value {
    let t = parse_iso_secs(now).unwrap_or(0);
    let n = exits
        .iter()
        .filter(|e| parse_iso_secs(e).is_some_and(|at| t - at <= window_s))
        .count() as i64;
    if n >= strikes {
        return json!({"parked": true, "deaths": n, "wait_s": null});
    }
    json!({"parked": false, "deaths": n, "wait_s": backoff_s(n)})
}

/// `body.window_words`: `5 minutes` · `1 hour` · `90 seconds`.
pub fn window_words(window_s: i64) -> String {
    let plural = |n: i64, w: &str| format!("{n} {w}{}", if n != 1 { "s" } else { "" });
    if window_s % 3600 == 0 {
        return plural(window_s / 3600, "hour");
    }
    if window_s % 60 == 0 {
        return plural(window_s / 60, "minute");
    }
    plural(window_s, "second")
}

/// `body.parked_words`: what happened, what stands, the human's lever.
pub fn parked_words(name: &str, deaths: i64, window_s: i64, last_words: Option<&str>) -> String {
    let said = fold_ws(last_words.unwrap_or(""));
    let tail = if said.is_empty() {
        " It left no words.".to_string()
    } else {
        format!(" Its last words: \u{201c}{}\u{201d}.", cut(&said, 200))
    };
    format!(
        "{name} is PARKED \u{2014} it died {deaths} time{} in {}, so the kernel stopped restarting \
         it.{tail} Nothing is deleted: its seat, its self and its record stand. Say \u{201c}restart the \
         {name} body\u{201d} to try again.",
        if deaths != 1 { "s" } else { "" },
        window_words(window_s)
    )
}

/// `body.parked_payload`: pointer + the evidence (the words cut at 600).
pub fn parked_payload(
    name: &str,
    did: Option<&str>,
    deaths: i64,
    window_s: i64,
    last_words: Option<&str>,
) -> Value {
    let said = cut(&fold_ws(last_words.unwrap_or("")), 600);
    json!({"ref": name, "hash": content_hash(&Value::String(said.clone())), "did": did,
           "deaths": deaths, "window_s": window_s, "last_words": said})
}

/// `orreth.body.parked.v1` with a given id and clock (the fixture's law);
/// the live kernel mints both ([`crate::bodies`]).
pub fn parked_fact(
    scope: &str,
    name: &str,
    payload: Value,
    message_id: &str,
    occurred_at: &str,
) -> Value {
    json!({
        "specversion": crate::envelope::SPECVERSION,
        "message_id": message_id,
        "message_kind": "event",
        "type": PARKED,
        "universe_id": scope,
        "scope_path": scope,
        "occurred_at": occurred_at,
        "payload": payload,
        "correlation_id": name,
        "authority_chain": [KERNEL],
    })
}

/// `harness.verdict`: `{passed, failed, details, note}`.
pub fn verdict(cases: &[Value], replies: &[Value]) -> Value {
    let mut details = Vec::new();
    let mut passed = 0i64;
    for (c, reply) in cases.iter().zip(replies.iter()) {
        let reply = reply.as_str().unwrap_or("");
        let low = reply.to_lowercase();
        let expect: Vec<Value> = c["expect"].as_array().cloned().unwrap_or_default();
        let ok = expect
            .iter()
            .all(|x| low.contains(&crate::py::python_str(x).to_lowercase()));
        if ok {
            passed += 1;
        }
        details
            .push(json!({"ask": c["ask"], "expect": expect, "reply": cut(reply, 300), "ok": ok}));
    }
    let failed = cases.len() as i64 - passed;
    json!({"passed": passed, "failed": failed, "details": details,
           "note": format!("harness: {passed} passed, {failed} failed")})
}

/// `harness.command_for`'s payload: the run id, the cases' hash, the target,
/// the cases whole; the arm and the parent marker only when given.
pub fn harness_payload(
    run_id: &str,
    target: &str,
    cases: &[Value],
    arm: Option<&str>,
    parent_marker: Option<&str>,
) -> Value {
    let mut p = json!({"ref": run_id, "hash": content_hash(&Value::Array(cases.to_vec())),
                       "target": target, "cases": cases});
    if let Some(a) = arm.filter(|a| !a.is_empty()) {
        p["arm"] = json!(a);
    }
    if let Some(m) = parent_marker.filter(|m| !m.is_empty()) {
        p["parent_marker"] = json!(m);
    }
    p
}

/// `orreth.resident.harness.v1` with a given id and clock (the fixture's law).
pub fn harness_command(
    scope: &str,
    run_id: &str,
    payload: Value,
    message_id: &str,
    occurred_at: &str,
) -> Value {
    json!({
        "specversion": crate::envelope::SPECVERSION,
        "message_id": message_id,
        "message_kind": "command",
        "type": HARNESS_CMD,
        "universe_id": scope,
        "scope_path": scope,
        "occurred_at": occurred_at,
        "payload": payload,
        "correlation_id": run_id,
        "authority_chain": [KERNEL],
    })
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn the_park_law() {
        assert_eq!(backoff_s(0), 0.0);
        assert_eq!(backoff_s(3), 4.0);
        assert_eq!(backoff_s(9), 30.0);
        let r = park_rule(
            &[
                "2026-09-24T17:59:00Z".into(),
                "2026-09-24T17:58:30Z".into(),
                "2026-09-24T17:57:00Z".into(),
            ],
            "2026-09-24T18:00:00+00:00",
            300,
            3,
        );
        assert_eq!(r, json!({"parked": true, "deaths": 3, "wait_s": null}));
        assert!(parked_words("echo", 1, 60, None).contains("died 1 time in 1 minute"));
        assert_eq!(window_words(90), "90 seconds");
    }
}
