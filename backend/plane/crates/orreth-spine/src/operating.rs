// PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch Phase 8 THE WORKSHOP sp5, THE OPERATING STATE: the pure laws · 2026-10-08
//! THE OPERATING STATE (canon 0010 §7 · 0005 Phase 8 sp5), PURE — the laws
//! `orreth_spine.operating` keeps, word for word (fixture `operating-v0.json`): the five
//! measurements (Trust · Recall · Efficiency · Experience · Cost) as coverage ratios, unknown
//! while nothing is there to measure; a serve's latency class by the hull's edge; a passing
//! grade; each measurement in words; the watch as the discriminator between THE OPERATING
//! STATE and Resiliency; the grader's verdict on a live reply by its FORM; the kernel's ask of
//! the grader; the critic's proposal words; a summons in words. The ground half is
//! `operating_live`.

use crate::py::{python_str, repr_str};
use regex::Regex;
use serde_json::{json, Value};
use std::sync::OnceLock;

pub const CONTRACT: &str = "orreth.operating/1";
pub const KERNEL: &str = "the kernel";
pub const MEASUREMENTS: [&str; 5] = ["trust", "recall", "efficiency", "experience", "cost"];
pub const TARGET: f64 = 1.0;
pub const WATCH_OP: &str = "<";
pub const PASS_GRADES: [&str; 3] = ["A", "B", "C"];
pub const EFFICIENCY_WINDOW_H: i64 = 24;
pub const GRADE_WINDOW_MIN: i64 = 60;
pub const GRADE_PER_BEAT: i64 = 5;
pub const GRADE_EVERY_S: u64 = 60;
pub const GRADE_DIAL: &str = "SPINE_GRADE_LIVE";
pub const SERVES: &str = "operating-state";
pub const FEEDBACK_GIVEN: &str = "orreth.feedback.given.v1";
pub const INCLUDE_SUMMONED: &str = "orreth.include.summoned.v1";
pub const INCLUDE_DISMISSED: &str = "orreth.include.dismissed.v1";
pub const DRAFT_PROPOSED: &str = "orreth.draft.proposed.v1";
pub const BASE_INCLUDES: [&str; 4] = ["planner", "critic", "grader", "mitl"];
pub const GRADE_HEAD: &str = "grader, grade the reply";
pub const GRADING_KIND: &str = "grading";
pub const IMPORT_NODE: &str = "import";

/// `operating.OPERATING` — the kernel's second intention, as the Python dict spells it.
pub fn operating() -> Value {
    json!({"words": "keep this world's operating state at 1.0 — Trust · Recall · Efficiency · Experience · Cost: when a measurement goes red, get it green",
           "serves": SERVES, "interests": ["watch-red"], "planner": "planner", "runner": "critic",
           "watches": MEASUREMENTS})
}

/// `operating.LATENCY_CLASSES`: a chat ask 30 s; work and events 180 s.
pub fn latency_limit(edge: &str) -> f64 {
    match edge {
        "chat" => 30.0,
        _ => 180.0,
    }
}

/// `operating.ratio`: a coverage ratio, unknown (None) while the denominator is empty — never a silent 1.0.
pub fn ratio(num: f64, den: f64) -> Option<f64> {
    if den <= 0.0 {
        return None;
    }
    Some((num / den * 10000.0).round() / 10000.0)
}

/// `operating.latency_class`: a serve's class is the hull's edge its ask took.
pub fn latency_class(marker_kind: Option<&str>, parent_kind: Option<&str>) -> (&'static str, f64) {
    let edge = crate::crafts::hull_edge(marker_kind, parent_kind);
    (edge, latency_limit(edge))
}

pub fn pass_grade(grade: Option<&str>) -> bool {
    grade.is_some_and(|g| PASS_GRADES.contains(&g.to_uppercase().as_str()))
}

fn what(name: &str) -> (&'static str, &'static str) {
    match name {
        "trust" => ("graded replies passed", "graded"),
        "recall" => ("served asks replayable by their marker chain", "served"),
        "efficiency" => ("serves inside their latency class", "serves of the last day"),
        "experience" => ("thumbs up", "thumbs given"),
        _ => ("spend a serving ask can be named for", "spend"),
    }
}

/// `operating.measure_words`: one measurement, in words.
pub fn measure_words(name: &str, value: Option<f64>, num: f64, den: f64) -> String {
    let (w0, w1) = what(name);
    match value {
        None => format!("{name}: unknown — no {w1} yet (never a silent 1.0)"),
        Some(v) if name == "cost" => format!("{name}: {v:.4} — ${num:.4} of ${den:.4} {w0}"),
        Some(v) => format!("{name}: {v:.4} — {} of {} {w0}", num as i64, den as i64),
    }
}

/// `operating.routes_to`: the watch is the discriminator.
pub fn routes_to(intention_watches: Option<&Vec<Value>>, metric: &str) -> bool {
    match intention_watches {
        Some(ws) if !ws.is_empty() => ws.iter().any(|w| w == metric),
        _ => !MEASUREMENTS.contains(&metric),
    }
}

fn grade_rx() -> &'static Regex {
    static RX: OnceLock<Regex> = OnceLock::new();
    RX.get_or_init(|| Regex::new(r"(?im)^\s*\**\s*grade\s*\**\s*:\s*\**\s*([A-Fa-f])\b").unwrap())
}

/// `operating.grade_of_live`: the grader's verdict on a live reply by the form `grade: <A–F> — <one line>`.
pub fn grade_of_live(text: &str) -> Value {
    let Some(m) = grade_rx().captures(text) else {
        return json!({"grade": null, "line": null});
    };
    let rest = &text[m.get(0).unwrap().end()..];
    let rest = rest.split('\n').next().unwrap_or("");
    let line = match rest.split_once('—') {
        Some((_, l)) => Some(l.trim_matches(|c: char| c == ' ' || c == '*').to_string()),
        None => {
            let t = rest.trim_matches(|c: char| c == ' ' || c == '-' || c == ':' || c == '*');
            if t.is_empty() { None } else { Some(t.to_string()) }
        }
    };
    json!({"grade": m[1].to_uppercase(), "line": line})
}

/// `operating.grade_ask`: the kernel's ask of the grader on a live reply.
pub fn grade_ask(ask_id: &str, who: &str, text: &str, reply: &str) -> String {
    let head: String = reply.chars().take(1200).collect();
    format!(
        "{GRADE_HEAD} {ask_id} by {who}. The ask: {}. The reply: {}. Grade the reply against the ask — did it do the right thing, completely and plainly? Answer in exactly this form, one line: `grade: <A-F> — <one line of reason>`. Never grade your own words.",
        repr_str(text),
        repr_str(&head)
    )
}

pub fn proposal_words(agent: &str, name: &str, kind: &str, marker: &str) -> String {
    format!("proposed by the critic from marker {marker} — for {agent}: the {name} {kind}")
}

pub fn summon_words(body: &str, on: bool, session: Option<&str>) -> String {
    let where_ = if session.is_some() { "this session's crew" } else { "your crew" };
    if on {
        format!("{body} summoned — it joins {where_}: address it as “{body}, …”; say “dismiss {body}” to let it go · recorded")
    } else {
        format!("{body} dismissed — it leaves {where_} · recorded, never deleted; say “summon {body}” to call it back")
    }
}

/// `operating.measurement_watch`: the kernel's own watch on a measurement.
pub fn measurement_watch(name: &str) -> Value {
    json!({"name": name, "metric": name, "op": WATCH_OP, "threshold": TARGET})
}

pub fn import_words(source: &str, commit: &str, entry: &str) -> String {
    let c: String = commit.chars().take(12).collect();
    format!("ran the imported graph {source} at {c} — entry {entry}")
}

/// The measurement's value as the snapshot carries it (null = unknown).
pub fn value_of(v: Option<f64>) -> Value {
    match v {
        Some(x) => json!(x),
        None => Value::Null,
    }
}

#[allow(dead_code)]
fn _py(v: &Value) -> String {
    python_str(v)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn the_law_is_pure() {
        assert_eq!(ratio(0.0, 0.0), None);
        assert_eq!(ratio(2.0, 3.0), Some(0.6667));
        assert_eq!(latency_class(Some("objective"), None), ("chat", 30.0));
        assert_eq!(latency_class(Some("objective"), Some("intention")), ("work", 180.0));
        assert!(pass_grade(Some("b")) && !pass_grade(Some("D")) && !pass_grade(None));
        assert_eq!(measure_words("trust", None, 0.0, 0.0), "trust: unknown — no graded yet (never a silent 1.0)");
        assert_eq!(measure_words("trust", Some(0.5), 1.0, 2.0), "trust: 0.5000 — 1 of 2 graded replies passed");
        assert_eq!(measure_words("cost", Some(0.25), 0.5, 2.0), "cost: 0.2500 — $0.5000 of $2.0000 spend a serving ask can be named for");
        assert!(routes_to(None, "outbox_pending") && !routes_to(None, "trust"));
        let ws = vec![json!("trust"), json!("cost")];
        assert!(routes_to(Some(&ws), "trust") && !routes_to(Some(&ws), "outbox_pending"));
        assert_eq!(grade_of_live("grade: B — plain and complete"), json!({"grade": "B", "line": "plain and complete"}));
        assert_eq!(grade_of_live("I decline."), json!({"grade": null, "line": null}));
        assert_eq!(grade_of_live("**Grade: a**"), json!({"grade": "A", "line": null}));
    }
}
