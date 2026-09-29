// PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp1, the bytes · 2026-09-22
// Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch row 4, re-base sp1: the four doors cross — the pure parts (passages · citations · metric_in · describe · shape · ask_text) · 2026-09-28
//! `orreth.impact/1` — the pure half of `orreth_spine.mitl`: a citation in a
//! human's name (W15 — the canon file's title and the passage's place) and
//! the verdict ladder applied by rule, never by a brain. MITL's corpus, the
//! toggle's facts and the impact door read a ground — `mitl_live` (re-base sp1);
//! the pure parts they lean on live here: the passages and their citations, the
//! metric in words, the ground's lines, the impact answer's shape and its ask's text.

use crate::py::{cut_chars, get, python_str, truthy};
use crate::tools;
use regex::Regex;
use serde_json::{json, Value};
use std::collections::{BTreeMap, HashMap};
use std::path::{Path, PathBuf};
use std::sync::{LazyLock, Mutex};

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

// ---- re-base sp1: the pure parts of the doors (mitl_live leans on them) ----------------

pub const NAME: &str = "mitl";
pub const EXPANSION: &str = "the Master Mind In the Loop";
pub const CONTRACT: &str = "orreth.impact/1";
pub const SUMMONED: &str = "orreth.mitl.summoned.v1";
pub const DISMISSED: &str = "orreth.mitl.dismissed.v1";
/// A passage the pack can carry whole.
pub const PASSAGE: usize = 2400;
pub const KINDS: [&str; 7] = [
    "watch",
    "intention",
    "template",
    "binding",
    "placement",
    "act",
    "service",
];

/// The Orreth ontology v0: the canon files, in the reference's order (`TITLES` keeps it).
pub fn ontology_paths() -> Vec<&'static str> {
    TITLES.iter().map(|(p, _)| *p).collect()
}

/// The repo — the spine home's parent (`ORRETH_SPINE`, else beside the crate).
pub fn repo() -> PathBuf {
    tools::spine_dir()
        .parent()
        .map(Path::to_path_buf)
        .unwrap_or_else(|| PathBuf::from("."))
}

static PARA_RE: LazyLock<Regex> = LazyLock::new(|| Regex::new(r"\n\s*\n").unwrap());
static HEADING_RE: LazyLock<Regex> = LazyLock::new(|| Regex::new(r"(?m)^#{1,6}\s+(.+)$").unwrap());
static RULE_RE: LazyLock<Regex> = LazyLock::new(|| Regex::new(r"(?m)^(\d+)\.\s+\*\*").unwrap());

/// `mitl.passages`: the canon in passages the pack can carry whole — a new passage at
/// every heading, paragraphs packed up to the limit, every word kept (a paragraph wider
/// than the pack is cut). Lengths are in characters, as the reference counts them.
pub fn passages(text: &str, limit: usize) -> Vec<String> {
    let mut out: Vec<String> = Vec::new();
    let mut cur = String::new();
    for para in PARA_RE.split(text) {
        let mut para: String = para.trim_matches('\n').to_string();
        if para.trim().is_empty() {
            continue;
        }
        let (cur_len, para_len) = (cur.chars().count(), para.chars().count());
        if !cur.is_empty() && (para.trim_start().starts_with('#') || cur_len + para_len + 2 > limit)
        {
            out.push(std::mem::take(&mut cur));
        }
        while para.chars().count() > limit {
            let head: String = para.chars().take(limit).collect();
            let tail: String = para.chars().skip(limit).collect();
            out.push(head);
            para = tail;
        }
        cur = if cur.is_empty() {
            para
        } else {
            format!("{cur}\n\n{para}")
        };
    }
    if !cur.is_empty() {
        out.push(cur);
    }
    out
}

static CITES: LazyLock<Mutex<HashMap<PathBuf, BTreeMap<String, String>>>> =
    LazyLock::new(|| Mutex::new(HashMap::new()));

/// `mitl.citations`: every passage key MITL can cite → its human name, from the same
/// files split the same way the ontology was acquired: `path#n` and the bare `file.md#n`
/// both resolve. Cached per root.
pub fn citations(root: Option<&Path>) -> BTreeMap<String, String> {
    let base = root.map(Path::to_path_buf).unwrap_or_else(repo);
    if let Some(c) = CITES.lock().unwrap_or_else(|p| p.into_inner()).get(&base) {
        return c.clone();
    }
    let mut out = BTreeMap::new();
    for rel in ontology_paths() {
        let Ok(text) = std::fs::read_to_string(base.join(rel)) else {
            continue;
        };
        let mut heading: Option<String> = None;
        for (i, part) in passages(&text, PASSAGE).iter().enumerate() {
            let i = i + 1;
            let hm = HEADING_RE.captures(part).map(|c| c[1].to_string());
            if part.trim_start().starts_with('#') {
                if let Some(h) = hm {
                    heading = Some(h);
                }
            }
            let rules: Vec<i64> = if rel.ends_with("SKILL.md") {
                RULE_RE
                    .captures_iter(part)
                    .filter_map(|c| c[1].parse().ok())
                    .collect()
            } else {
                Vec::new()
            };
            let rule = (!rules.is_empty()).then(|| Rule::Span(rules[0], rules[rules.len() - 1]));
            let name = citation_name(rel, heading.as_deref(), rule);
            out.insert(format!("{rel}#{i}"), name.clone());
            let bare = rel.rsplit('/').next().unwrap_or(rel);
            out.entry(format!("{bare}#{i}")).or_insert(name);
        }
    }
    CITES
        .lock()
        .unwrap_or_else(|p| p.into_inner())
        .insert(base, out.clone());
    out
}

/// A watch in plain words names its metric (v0 word rules) — the reference's `_METRIC_WORDS`.
const METRIC_WORDS: [(&str, &str); 7] = [
    ("bodies_dormant", r"dormant"),
    ("bodies_alive", r"\balive\b|\bliving\b"),
    ("oldest_outbox_age_s", r"oldest|\bage\b|\bold\b|stale"),
    ("outbox_pending", r"outbox|pending|backlog"),
    ("asks_received", r"\basks?\b|received|waiting|unserved"),
    ("door_p95_ms", r"\bslow\b|latency|\bdoors?\b|p95"),
    ("parked", r"parked|poison"),
];
static METRIC_RES: LazyLock<Vec<(&'static str, Regex)>> = LazyLock::new(|| {
    METRIC_WORDS
        .iter()
        .map(|(m, pat)| (*m, Regex::new(pat).unwrap()))
        .collect()
});

/// `mitl._metric_in`: a metric's own name in the words first (spaces as underscores),
/// else the word rules. (The metrics are this kernel's — `watch::METRICS`.)
pub fn metric_in(words: &str) -> Option<String> {
    let low = words.to_lowercase();
    let joined = low.replace(' ', "_");
    for m in crate::watch::METRICS {
        if joined.contains(m) {
            return Some(m.to_string());
        }
    }
    for (m, re) in METRIC_RES.iter() {
        if re.is_match(&low) {
            return Some(m.to_string());
        }
    }
    None
}

/// `str(x)` for a truthy value, else the empty string (the reference's `str(x or "")`).
pub(crate) fn s_of(v: &Value) -> String {
    if truthy(v) {
        python_str(v)
    } else {
        String::new()
    }
}

/// `mitl.describe`: the ground, in lines MITL can read and the glass can show.
pub fn describe(t: &Value) -> Vec<String> {
    let mut lines = Vec::new();
    let arr = |k: &str| t[k].as_array().cloned().unwrap_or_default();
    let bodies = arr("bodies");
    if !bodies.is_empty() {
        lines.push(format!(
            "bodies: {}",
            bodies
                .iter()
                .map(|b| format!(
                    "{} ({})",
                    s_of(&b["name"]),
                    b["kind"]
                        .as_str()
                        .filter(|k| !k.is_empty())
                        .unwrap_or("not joined")
                ))
                .collect::<Vec<_>>()
                .join(", ")
        ));
    }
    let chains = arr("chains");
    if !chains.is_empty() {
        lines.push(format!(
            "chains: {}",
            chains
                .iter()
                .map(python_str)
                .collect::<Vec<_>>()
                .join(" · ")
        ));
    }
    for i in arr("intentions") {
        let shares: Vec<String> = i["shares"]
            .as_array()
            .map(|a| a.iter().map(python_str).collect())
            .unwrap_or_default();
        let tag = if truthy(&i["wakes"]) {
            "wakes on it".to_string()
        } else if !shares.is_empty() {
            format!("shares {}", shares.join(", "))
        } else if i["active"] == json!(false) {
            "at rest".to_string()
        } else {
            "standing".to_string()
        };
        lines.push(format!(
            "intention ({}, serves {}): “{}” — {tag}",
            s_of(&i["kind"]),
            s_of(&i["serves"]),
            cut_chars(i["words"].as_str().unwrap_or_default(), 90)
        ));
    }
    for w in arr("watches") {
        lines.push(format!(
            "watch on the same metric: {} — {} {} {}{}",
            s_of(&w["name"]),
            s_of(&w["metric"]),
            python_str(&w["op"]),
            python_str(&w["threshold"]),
            if truthy(&w["red"]) { " (red now)" } else { "" }
        ));
    }
    for m in arr("markers") {
        let under = m["under"].as_object();
        lines.push(format!(
            "marker: {} {}{}",
            s_of(&m["kind"]),
            python_str(&m["id"]),
            match under.filter(|u| !u.is_empty()) {
                Some(u) => format!(
                    " — grew {}",
                    u.iter()
                        .map(|(k, n)| format!("{} {k}", python_str(n)))
                        .collect::<Vec<_>>()
                        .join(", ")
                ),
                None => String::new(),
            }
        ));
    }
    if let Some(cost) = t["cost"].as_object() {
        for (n, c) in cost {
            lines.push(format!(
                "cost so far: {n} — {} thoughts, {} tokens on the meter",
                python_str(&c["thoughts"]),
                python_str(&c["tokens"])
            ));
        }
    }
    if truthy(&t["metric"]) {
        lines.push(format!("metric: {}", python_str(&t["metric"])));
    }
    if truthy(&t["placement"]) {
        let p = &t["placement"];
        let list = |k: &str| -> Vec<String> {
            p[k].as_array()
                .map(|a| a.iter().map(python_str).collect())
                .unwrap_or_default()
        };
        let (affinity, secrets) = (list("affinity"), list("secrets_with"));
        lines.push(format!(
            "placement asked: cell '{}' · metal {}{}{}",
            python_str(&p["cell"]),
            python_str(&p["metal"]),
            if affinity.is_empty() {
                String::new()
            } else {
                format!(" · beside {}", affinity.join(", "))
            },
            if secrets.is_empty() {
                String::new()
            } else {
                format!(" · secrets {}", secrets.join(", "))
            }
        ));
    }
    lines.push(format!(
        "consequence: {} → {}",
        python_str(&t["class"]),
        python_str(&t["level"])
    ));
    lines.extend(arr("notes").iter().map(python_str));
    lines
}

/// `mitl.shape`: the impact answer's shape on the wire (`orreth.impact/1`).
pub fn shape(touches: &Value, verdict_: &str, ask_id: Option<&str>, marker: Option<&str>) -> Value {
    let arr = |k: &str| touches[k].as_array().cloned().unwrap_or_default();
    let mut t = json!({
        "bodies": arr("bodies").iter().map(|b| b["name"].clone()).collect::<Vec<_>>(),
        "chains": touches["chains"],
        "intentions": arr("intentions").iter().map(|i| json!({"intention_id": i["intention_id"], "kind": i["kind"], "words": i["words"]})).collect::<Vec<_>>(),
        "watches": arr("watches").iter().map(|w| w["watch_id"].clone()).collect::<Vec<_>>(),
        "markers": arr("markers").iter().filter(|m| truthy(&m["id"])).map(|m| m["id"].clone()).collect::<Vec<_>>(),
        "cost": touches["cost"],
        "metric": touches["metric"],
        "class": touches["class"], "level": touches["level"], "kernel": truthy(&touches["kernel"]),
        "notes": touches["notes"],
    });
    if truthy(&touches["placement"]) {
        t["placement"] = touches["placement"].clone();
    }
    json!({
        "contract": CONTRACT,
        "change": {"kind": touches["kind"], "ref": touches["ref"], "words": touches["words"]},
        "touches": t,
        "verdict": verdict_,
        "served_by": NAME,
        "ask_id": ask_id,
        "marker": marker,
    })
}

/// `mitl.ask_text` (conformance `impact_text`): the impact ask's words — the change first
/// (W6 — the Analyzer's twig reads "the change: keep this world resilient…", never the
/// prompt's shape), then THE GROUND as the kernel read it, the verdict by the ladder, the ask.
pub fn ask_text(t: &Value, verdict_: &str, ground: &[String]) -> String {
    let arr = |k: &str| t[k].as_array().cloned().unwrap_or_default();
    let head = Some(s_of(&t["words"]))
        .filter(|w| !w.is_empty())
        .or_else(|| {
            arr("intentions")
                .iter()
                .find(|i| truthy(&i["words"]))
                .map(|i| s_of(&i["words"]))
        })
        .or_else(|| {
            arr("watches")
                .iter()
                .find(|w| truthy(&w["name"]))
                .map(|w| s_of(&w["name"]))
        })
        .unwrap_or_else(|| {
            format!(
                "the {}{}",
                s_of(&t["kind"]),
                if truthy(&t["ref"]) {
                    format!(" {}", s_of(&t["ref"]))
                } else {
                    String::new()
                }
            )
        });
    format!(
        "the change: {head} — expected impact?\nTHE CHANGE: a {}{}\nTHE GROUND (read by the kernel — this is the \
         record):\n- {}\nVERDICT BY THE LADDER: {verdict_}\nAnswer in plain words, three short parts — WHO AND WHAT \
         IT TOUCHES · THE RISK · WHAT TO WATCH AFTER — and end with the verdict line above, unchanged.",
        s_of(&t["kind"]),
        if truthy(&t["ref"]) { format!(" ({})", s_of(&t["ref"])) } else { String::new() },
        ground.join("\n- ")
    )
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
