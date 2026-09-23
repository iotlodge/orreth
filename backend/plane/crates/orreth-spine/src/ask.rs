// PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp1, the bytes · 2026-09-22
// Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp4, the loops: W26's words · 2026-09-23
// Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp3, the ask road: the ask's fact and the door's refusal, as bytes · 2026-09-22
//! `orreth.ask/1` and the word-shaped laws of `orreth.intent/1` — the pure
//! half of `orreth_spine.dispatch` (the address at the head of an ask, W7;
//! the door's refusal for a body that is not here, W19), `harness` (a reply
//! that OPENS as a refusal, W21), `resident` (echo's reply, W24) and
//! `scheduler` (a duty framed as a duty, W21). Every regex here is the
//! reference's, character for character; the words are the fixtures'.

use crate::hash::content_hash;
use crate::py::fold_ws;
use regex::Regex;
use serde_json::{json, Value};
use std::sync::LazyLock;

pub const ASK_RECEIVED: &str = "orreth.ask.received.v1";
/// W19: an ask to a body that is not here.
pub const ASK_REFUSED: &str = "orreth.ask.refused.v1";
/// The holder of its own acts (`proof.KERNEL`).
pub const KERNEL: &str = "the kernel";
/// W26 (P7 sp4): a mind that returns no words is asked again ONCE; a second
/// silence lands as these words with status `replied` — never an empty bubble.
/// The serve is the Python body's until the bodies' seam; the words are the law.
pub const W26_WORDS: &str = "the mind returned nothing; asked again, nothing";
pub const W26_STEP: &str = "the mind returned no words — asked again, once (W26)";
/// A failing harness run is a fact on the rail (AG-6).
pub const HARNESS_FAILED: &str = "orreth.harness.failed.v1";
/// M2: a body is alive while its lease is fresh — the lease's length in seconds.
pub const LEASE_TTL_S: i64 = 15;

// ---- dispatch.py ------------------------------------------------------------------

static ADDRESS_RE: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r"^\s*@?([A-Za-z0-9_-]+)\s*[,:]\s*\S").unwrap());

/// W7: a name at the HEAD of an ask selects that body — `echo, …` · `@echo …`
/// · `librarian: …` — when the name is a body of this world (`names`).
/// Anything else is unaddressed and the fan-out stays. Case does not matter;
/// the name comes back as the body spells it.
pub fn address<S: AsRef<str>>(text: &str, names: &[S]) -> Option<String> {
    let m = ADDRESS_RE.captures(text)?;
    let want = m[1].to_lowercase();
    names
        .iter()
        .map(AsRef::as_ref)
        .find(|n| n.to_lowercase() == want)
        .map(str::to_string)
}

/// W19: the door's plain reply for an ask to a body that is not here.
pub fn refusal_words(name: &str, reason: &str) -> String {
    format!("{name} is not here — {reason}")
}

// ---- the ask's fact, as bytes (the fixture's law: `askroad-v0.json`) ---------------

/// The `ask.received` payload: pointer-only — the ref and the words' hash;
/// the target only when named, the session only when given, the window as
/// two strings (`submit_ask`'s law).
pub fn received_payload(
    ask_id: &str,
    text: &str,
    target: Option<&str>,
    session: Option<&str>,
    window: Option<(&str, &str)>,
) -> Value {
    let mut p = json!({"ref": ask_id, "hash": content_hash(&Value::String(text.into()))});
    if let Some(t) = target {
        p["target"] = json!(t);
    }
    if let Some(s) = session {
        p["session"] = json!(s);
    }
    if let Some((from, to)) = window {
        p["window"] = json!({"from": from, "to": to});
    }
    p
}

/// The `ask.refused` payload (W19): the target and the reason ride it.
pub fn refused_payload(
    ask_id: &str,
    text: &str,
    target: &str,
    reason: &str,
    session: Option<&str>,
) -> Value {
    let mut p = json!({
        "ref": ask_id, "hash": content_hash(&Value::String(text.into())),
        "target": target, "reason": reason,
    });
    if let Some(s) = session {
        p["session"] = json!(s);
    }
    p
}

/// An ask's fact, whole: the correlation is the fanout or the ask, the
/// aggregate is the ask at sequence 1, the chain and the marker as given —
/// `ask.received` wears the human alone, `ask.refused` the human then the
/// kernel. The id and the clock are the caller's (the live path mints them;
/// the fixture fixes them).
#[allow(clippy::too_many_arguments)]
pub fn ask_fact(
    typ: &str,
    scope: &str,
    ask_id: &str,
    payload: Value,
    fanout: Option<&str>,
    chain: &[&str],
    marker: &Value,
    message_id: &str,
    occurred_at: &str,
) -> Value {
    json!({
        "specversion": crate::envelope::SPECVERSION,
        "message_id": message_id,
        "message_kind": "event",
        "type": typ,
        "universe_id": scope,
        "scope_path": scope,
        "occurred_at": occurred_at,
        "payload": payload,
        "correlation_id": fanout.unwrap_or(ask_id),
        "authority_chain": chain,
        "aggregate": {"type": "ask", "id": ask_id, "sequence": 1},
        "marker": marker,
    })
}

// ---- harness.py -------------------------------------------------------------------

static REFUSAL_RE: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(
        r"(?i)^(i will not\b|i won'?t\b|i am not answering\b|i'?m not answering\b|not answering this\b|i refuse\b|i decline\b|i am not going to answer\b|i will not answer\b)",
    )
    .unwrap()
});

/// W21: does a reply OPEN as a refusal? "I will not …", "I am not answering
/// …", "not answering this …", "I refuse/decline …" — the opening alone
/// counts, markdown stripped; a reply that merely mentions the words is an answer.
pub fn refused_words(reply: Option<&str>) -> bool {
    let folded = fold_ws(reply.unwrap_or(""));
    let head = folded.trim_start_matches(|c: char| "*#-> \"“'".contains(c));
    REFUSAL_RE.is_match(head)
}

// ---- resident.py ------------------------------------------------------------------

static QUESTION_RE: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(r"(?i)(\?\s*$|^(who|what|what's|whats|when|where|why|how|is|are|does|do|can|could|would|should|which|did|tell me)\b)").unwrap()
});
static DATE_ASK_RE: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(r"(?i)\b(date|time|clock|year|month|what day|which day|day is it|day it is|day of the week)\b").unwrap()
});

/// W24: the echoed words alone — "hello" is "hello". A QUESTION the body
/// cannot answer by nature adds one plain line: "echo repeats; ask the
/// librarian for the date" (a date or time ask) — or "… for an answer".
pub fn echo_reply(name: &str, text: &str) -> String {
    let words = fold_ws(text);
    if !QUESTION_RE.is_match(&words) {
        return words;
    }
    let want = if DATE_ASK_RE.is_match(&words) {
        "the date"
    } else {
        "an answer"
    };
    format!("{words}\n{name} repeats; ask the librarian for {want}")
}

// ---- scheduler.py -----------------------------------------------------------------

/// The cadence in a human's word: hourly · daily · weekly · every N hours ·
/// every N minutes · every N seconds.
pub fn cadence_words(every_s: i64) -> String {
    let n = every_s;
    match n {
        3600 => "hourly".into(),
        86400 => "daily".into(),
        604800 => "weekly".into(),
        _ if n % 3600 == 0 => format!("every {} hours", n / 3600),
        _ if n % 60 == 0 && n >= 60 => {
            let m = n / 60;
            format!("every {m} minute{}", if m != 1 { "s" } else { "" })
        }
        _ => format!("every {n} seconds"),
    }
}

/// W21: the framing of a duty's occurrence — `“<the duty's words>” — your
/// <cadence> duty (every N s) · since <the last run's time> | your first run ·
/// your earlier notes today: <one line each, newest first, at most 3, each cut
/// at 160> | no earlier notes today`. The clock is the caller's (`since`).
pub fn duty_text<S: AsRef<str>>(
    text: &str,
    every_s: i64,
    since: Option<&str>,
    notes: &[S],
) -> String {
    let words = fold_ws(text);
    let cadence = cadence_words(every_s);
    let head = if cadence.starts_with("every") {
        format!("“{words}” — your duty {cadence} (every {every_s} s)")
    } else {
        format!("“{words}” — your {cadence} duty (every {every_s} s)")
    };
    let window = match since {
        Some(s) if !s.is_empty() => format!("since {s}"),
        _ => "your first run".to_string(),
    };
    let lines: Vec<String> = notes
        .iter()
        .take(3)
        .map(|n| fold_ws(n.as_ref()).chars().take(160).collect())
        .collect();
    let tail = if lines.is_empty() {
        "no earlier notes today".to_string()
    } else {
        format!("your earlier notes today: {}", lines.join(" · "))
    };
    format!("{head} · {window} · {tail}")
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn the_head_of_an_ask() {
        let names = ["echo", "librarian"];
        assert_eq!(address("  @ECHO:  hi", &names).as_deref(), Some("echo"));
        assert_eq!(address("echo,", &names), None); // nothing after the name
        assert_eq!(address("hello echo, hi", &names), None);
        assert_eq!(refusal_words("nobody", "why"), "nobody is not here — why");
    }

    #[test]
    fn a_refusal_opens_the_reply() {
        assert!(refused_words(Some("> **I won't.**")));
        assert!(refused_words(Some("I'm not answering that.")));
        assert!(!refused_words(Some("I willnot")));
        assert!(!refused_words(None));
    }

    #[test]
    fn echo_and_the_duty() {
        assert_eq!(
            echo_reply("echo", "Which year is it?"),
            "Which year is it?\necho repeats; ask the librarian for the date"
        );
        assert_eq!(
            echo_reply("echo", "tell me a joke"),
            "tell me a joke\necho repeats; ask the librarian for an answer"
        );
        assert_eq!(cadence_words(7200), "every 2 hours");
        assert_eq!(cadence_words(60), "every 1 minute");
        assert_eq!(cadence_words(45), "every 45 seconds");
        let long = "x".repeat(200);
        let t = duty_text("  sweep  ", 60, None, &[long.as_str(), "b", "c", "d"]);
        assert!(t.starts_with("“sweep” — your duty every 1 minute (every 60 s) · your first run · your earlier notes today: "));
        assert!(t.ends_with(&format!("{} · b · c", "x".repeat(160))));
    }
}
