// PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp1, the bytes · 2026-09-22
//! `orreth.impact/1` — the pure half of `orreth_spine.mitl`: a citation in a
//! human's name (W15 — the canon file's title and the passage's place) and
//! the verdict ladder applied by rule, never by a brain. MITL's corpus, the
//! toggle's facts and the impact door read a ground — sp3's.

use crate::py::{get, truthy};
use regex::Regex;
use serde_json::Value;
use std::sync::LazyLock;

/// The canon in human names (the path stays in the record).
pub const TITLES: [(&str, &str); 9] = [
    (
        "docs/rearch/0001-experience-charter.md",
        "the experience charter",
    ),
    (
        "docs/rearch/0002-transport-architecture.md",
        "the transport architecture",
    ),
    (
        "docs/rearch/0003-memory-architecture.md",
        "the memory architecture",
    ),
    ("docs/rearch/0004-agent-architecture.md", "the agent canon"),
    (
        "docs/rearch/0005-v1-scope-and-build-plan.md",
        "the build plan",
    ),
    ("docs/rearch/0006-markers-dive.md", "the markers dive"),
    ("docs/rearch/0007-intent-dive.md", "the intent dive"),
    (
        "docs/rearch/0008-the-rust-plane-and-the-port.md",
        "the Rust plane and the port",
    ),
    (".claude/skills/orreth-covenant/SKILL.md", "the covenant"),
];

/// sp1's ladder, in MITL's words.
pub const VERDICTS: [&str; 3] = ["low", "consider", "grave — needs L3"];

/// The passage's place by rule number: one rule, or a span of rules.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Rule {
    One(i64),
    Span(i64, i64),
}

impl Rule {
    /// The reference's `rule` argument: an int, a list/tuple (first and last), or none.
    pub fn from_value(v: &Value) -> Option<Rule> {
        match v {
            Value::Null => None,
            Value::Array(a) if !a.is_empty() => {
                let a0 = a[0].as_f64()? as i64;
                let a1 = a[a.len() - 1].as_f64()? as i64;
                Some(Rule::Span(a0, a1))
            }
            Value::Array(_) => None, // an empty list is falsy: no rule
            other => Some(Rule::One(other.as_f64()? as i64)),
        }
    }
}

static MARKS_RE: LazyLock<Regex> = LazyLock::new(|| Regex::new(r"\*\*|__|`").unwrap());
static TAIL_RE: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r"\s+\((?:opened|CLOSED|why|JB|block|re-sliced)").unwrap());
static NUMBER_RE: LazyLock<Regex> = LazyLock::new(|| Regex::new(r"^\d{4}\s+—\s+").unwrap());

/// `Path(path).stem` — the last component without its final suffix.
fn stem(path: &str) -> &str {
    let name = path.rsplit('/').next().unwrap_or(path);
    match name.rfind('.') {
        Some(i) if i > 0 && i + 1 < name.len() => &name[..i],
        _ => name,
    }
}

/// W15: one citation in a human's words — the file's title from [`TITLES`]
/// (an unknown path keeps its bare name), then the passage's place: `rule N`
/// for a covenant rule, else the heading with its marks and its parenthetical
/// tail dropped, cut short. "the covenant, rule 5" · "the build plan, Phase 6 — GOVERNANCE FELT".
pub fn citation_name(path: &str, heading: Option<&str>, rule: Option<Rule>) -> String {
    let title = TITLES
        .iter()
        .find(|(p, _)| *p == path)
        .map(|(_, t)| t.to_string())
        .unwrap_or_else(|| stem(path).to_string());
    match rule {
        Some(Rule::Span(a, b)) if a == b => return format!("{title}, rule {a}"),
        Some(Rule::Span(a, b)) => return format!("{title}, rules {a}–{b}"),
        Some(Rule::One(n)) => return format!("{title}, rule {n}"),
        None => {}
    }
    let h = heading.unwrap_or("").trim().trim_start_matches('#').trim();
    let h = MARKS_RE.replace_all(h, "");
    let h = match TAIL_RE.find(&h) {
        Some(m) => h[..m.start()].trim().to_string(),
        None => h.trim().to_string(),
    };
    let h = NUMBER_RE.replace(&h, "").to_string();
    let h = if h.chars().count() > 48 {
        format!("{}…", h.chars().take(48).collect::<String>().trim_end())
    } else {
        h
    };
    if h.is_empty() {
        title
    } else {
        format!("{title}, {h}")
    }
}

/// The ladder (sp1), applied by rule — never by a brain: a kernel intention,
/// or any act held at L3, is grave; a change that touches a standing
/// intention, a consequential act, or what bodies wear is `consider`; the rest is low.
pub fn verdict(touches: &Value) -> &'static str {
    let level = get(touches, "level");
    let level = if truthy(level) {
        crate::py::python_str(level)
    } else {
        String::new()
    };
    if truthy(get(touches, "kernel")) || level.starts_with("L3") {
        return VERDICTS[2];
    }
    let kind = get(touches, "kind").as_str().unwrap_or("");
    if truthy(get(touches, "intentions"))
        || get(touches, "class").as_str() == Some("consequential")
        || ["intention", "template", "binding", "placement"].contains(&kind)
    {
        return VERDICTS[1];
    }
    VERDICTS[0]
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;

    #[test]
    fn a_citation_in_human_words() {
        assert_eq!(
            citation_name(
                ".claude/skills/orreth-covenant/SKILL.md",
                None,
                Some(Rule::Span(3, 5))
            ),
            "the covenant, rules 3–5"
        );
        assert_eq!(
            citation_name(
                ".claude/skills/orreth-covenant/SKILL.md",
                None,
                Some(Rule::Span(5, 5))
            ),
            "the covenant, rule 5"
        );
        assert_eq!(
            citation_name(
                "docs/rearch/0005-v1-scope-and-build-plan.md",
                Some("# 0005 — V1 Scope **and** `Build` Plan (why: x)"),
                None
            ),
            "the build plan, V1 Scope and Build Plan"
        );
        assert_eq!(
            citation_name("docs/rearch/0007-intent-dive.md", Some("   "), None),
            "the intent dive"
        );
        // 20 words = 99 chars; the first 48 are nine words and "wor", the cut trailing space dropped.
        let long = format!("## {}", "word ".repeat(20));
        assert_eq!(
            citation_name("a/b.tar.gz", Some(&long), None),
            format!("b.tar, {}wor…", "word ".repeat(9))
        );
        assert_eq!(Rule::from_value(&json!([2, 3, 4])), Some(Rule::Span(2, 4)));
        assert_eq!(Rule::from_value(&json!(null)), None);
        assert_eq!(Rule::from_value(&json!(7)), Some(Rule::One(7)));
    }

    #[test]
    fn the_ladder_by_rule() {
        assert_eq!(verdict(&json!({"kernel": true})), "grave — needs L3");
        assert_eq!(verdict(&json!({"level": "L3-code"})), "grave — needs L3");
        assert_eq!(verdict(&json!({"kind": "template"})), "consider");
        assert_eq!(verdict(&json!({"intentions": [{"id": 1}]})), "consider");
        assert_eq!(
            verdict(&json!({"intentions": [], "kind": "act", "class": "routine"})),
            "low"
        );
        assert_eq!(verdict(&json!({})), "low");
    }
}
