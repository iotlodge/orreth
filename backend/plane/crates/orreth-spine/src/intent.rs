// PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp3, the ask road · 2026-09-22
// Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp4, the loops: the loop's words in one place · walk #11 W.1: a cadence in seconds · W37 · W38 · 2026-09-23
//! The pure half of `orreth_spine.intent` that the ask door needs — P23
//! (block 11): THE KIND OF AN ASK. The words propose it (thought · objective
//! · intention), a typed prefix is the human's flip and wins, and an
//! intention's words also say what it serves, what wakes it (its interests)
//! and its cadence. Every regex is the reference's, character for character;
//! measured by the conformance kind `ask_kind` (`askroad-v0.json`). The stop's
//! and restart's demands live in [`crate::proof`]. P7 sp4 adds THE LOOP'S
//! WORDS, pure — what the kernel asks the planner, the observation under a
//! marker, a red watch's note, the runner's honest opening (W8), the
//! improvement's note, the crew's shape hashed — measured by `loops-v0.json`;
//! the loop itself turns in [`crate::intent_live`].

use crate::hash::content_hash;
use crate::py::{fold_ws, python_str, repr_str};
use regex::Regex;
use serde_json::{json, Value};
use std::sync::LazyLock;

pub const INTENTION_DECLARED: &str = "orreth.intention.declared.v1";
pub const INTENTION_STOPPED: &str = "orreth.intention.stopped.v1";
/// W20: the reverse act, its own fact.
pub const INTENTION_RESTARTED: &str = "orreth.intention.restarted.v1";
/// The runner's honest opening (W8).
pub const CANNOT_ACT: &str = "cannot act";
/// The cadence's observation, when nothing new was seen.
pub const CADENCE_DUE: &str = "the cadence came due; nothing new was observed";

/// The first Infinite Horizon Intention (0007), as the Python dict spells it.
pub fn resiliency() -> Value {
    json!({"words": "keep this world resilient: when a watch goes red, get it green",
           "serves": "resiliency", "interests": [WATCH_RED], "planner": "planner"})
}

/// The observation's words when a watch turns red: the name in Python's
/// quotes, the condition, the value (numbers as Python prints them).
pub fn watch_note(name: &str, metric: &str, op: &str, threshold: &Value, value: &Value) -> String {
    format!(
        "watch {} went red: {metric} {op} {}, value {}",
        repr_str(name),
        python_str(threshold),
        python_str(value)
    )
}

/// What the kernel asks the planner under an observation.
pub fn plan_words(serves: &str, words: &str, observed: &str) -> String {
    format!(
        "INTENTION (serves {serves}): {words}\nOBSERVED: {observed}\nReply with the ONE next \
         objective for the crew that serves this intention — one imperative sentence, nothing else."
    )
}

/// The observation under a marker.
pub fn observed_words(kind: &str, r#ref: &str, note: Option<&str>) -> String {
    match note {
        Some(n) => format!("a marker of kind {} on {ref}: {n}", repr_str(kind)),
        None => format!("a marker of kind {} on {ref}", repr_str(kind)),
    }
}

static CANNOT_RE: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(
        r"^(cannot act\b|i (?:cannot|can't|can not|am unable to|am not able to|lack the tool|lack a tool|don't have (?:a|the|any) tool|do not have (?:a|the|any) tool|have no tool)\b)",
    )
    .unwrap()
});
static PREFACE_RE: LazyLock<Regex> = LazyLock::new(|| Regex::new(r"^[^:.]{0,60}:\s*").unwrap());

fn strip_marks(s: &str) -> &str {
    s.trim_start_matches(|c| "*#-> \"“'".contains(c))
}

/// W8, walk #11 W38: the runner's honest word, heard in more than one shape —
/// a reply that OPENS by saying the body cannot ("cannot act: …", "I cannot
/// …", "I can't …", "I lack the tool …", "I don't have a tool …"), after at
/// most one short preface ending in a colon. Only the opening counts — a
/// reply that merely mentions the words is a reply.
pub fn cannot_act(reply: Option<&str>) -> bool {
    let low = fold_ws(reply.unwrap_or("")).to_lowercase();
    let head = strip_marks(&low);
    if CANNOT_RE.is_match(head) {
        return true;
    }
    match PREFACE_RE.find(head) {
        Some(m) => CANNOT_RE.is_match(strip_marks(&head[m.end()..])),
        None => false,
    }
}

/// W37: the door's refusal when an intention with these words already stands.
pub fn duplicate_words(kind: &str, words: &str) -> String {
    let whose = match kind {
        "kernel" => "the kernel's",
        "role" => "the role's",
        _ => "your own",
    };
    format!(
        "an intention with these words already stands — {whose} “{words}” is at work; stop it \
         first, or say what is different"
    )
}

/// W8's marker note when a runner says it cannot act: the first 200 characters of what it said.
pub fn improvement_note(who: &str, reply: Option<&str>) -> String {
    let first: String = fold_ws(reply.unwrap_or("")).chars().take(200).collect();
    format!("runner cannot act: {who} said “{first}” — needs a body with the tools for it")
}

/// The crew's shape hashed: the (name, capabilities) pairs sorted by name, as
/// canonical bytes of a list of lists — when it changes, a runner that could
/// not act may now.
pub fn crew_shape_hash(shape: &[(String, Value)]) -> String {
    let mut pairs: Vec<&(String, Value)> = shape.iter().collect();
    pairs.sort_by(|a, b| a.0.cmp(&b.0));
    let list: Vec<Value> = pairs.into_iter().map(|(n, c)| json!([n, c])).collect();
    content_hash(&Value::Array(list))
}
pub const SERVES: [&str; 5] = ["business", "security", "resiliency", "compliance", "cost"];
pub const KINDS: [&str; 3] = ["human", "role", "kernel"];
/// P23: the ask wears its kind.
pub const ASK_KINDS: [&str; 3] = ["thought", "objective", "intention"];
/// Seeded by the kernel (`markers.SEED`).
pub const WATCH_RED: &str = "watch-red";

static PREFIX: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r"(?is)^(thought|objective|intention)\s*:\s*(.+)$").unwrap());
static INTENT: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(
        r"(?i)(\bkeep\b.{0,60}\b(resilient|green|alive|safe|secure|compliant|healthy|under|below|within)\b|\bwhen(ever)?\b.{0,60}\b(goes|turns|is|are|go)\s+(red|down|dormant|late|over)\b|\bevery\s+(\d+\s+)?(second|minute|hour|day|week)s?\b|\bfrom now on\b|\bwatch for\b|\bstanding\b|\bas long as\b|\bany ?time\b)",
    )
    .unwrap()
});
static THOUGHT: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(r"(?i)(\?\s*$|^(who|what|what's|whats|when|where|why|how|is|are|does|do|can|could|would|should|which|did|tell me|explain|describe|repeat)\b)").unwrap()
});
static EVERY: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(r"(?i)\bevery\s+(\d+\s+)?(second|minute|hour|day|week)s?\b").unwrap()
});
static SERVES_RE: LazyLock<Vec<(&'static str, Regex)>> = LazyLock::new(|| {
    vec![
        (
            "cost",
            Regex::new(r"cost|spend|run rate|budget|meter|token").unwrap(),
        ),
        (
            "security",
            Regex::new(r"secur|threat|vulnerab|attack|intrus").unwrap(),
        ),
        (
            "compliance",
            Regex::new(r"complian|audit|regulat|policy").unwrap(),
        ),
        (
            "resiliency",
            Regex::new(r"resilien|\bred\b|watch|alive|dormant|lease|outage|uptime|health|green")
                .unwrap(),
        ),
    ]
});
static WAKES_WATCH: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r"watch|\bred\b|green|resilien").unwrap());
static WAKES_IMPROVE: LazyLock<Regex> = LazyLock::new(|| Regex::new(r"improv").unwrap());
static WAKES_COST: LazyLock<Regex> = LazyLock::new(|| Regex::new(r"cost|spend|budget").unwrap());

fn unit_seconds(unit: &str) -> i64 {
    match unit {
        "second" => 1,
        "minute" => 60,
        "hour" => 3600,
        "day" => 86400,
        _ => 604800,
    }
}

/// What `read_words` reads.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Read {
    pub kind: String,
    pub words: String,
    pub pinned: bool,
    /// Present only for an intention: what it serves, what wakes it, its cadence.
    pub serves: Option<String>,
    pub interests: Option<Vec<String>>,
    pub every_s: Option<i64>,
}

impl Read {
    /// The Python dict, as the fixture spells it.
    pub fn to_value(&self) -> Value {
        let mut v = json!({"kind": self.kind, "words": self.words, "pinned": self.pinned});
        if self.kind == "intention" {
            v["serves"] = json!(self.serves);
            v["interests"] = json!(self.interests.clone().unwrap_or_default());
            v["every_s"] = json!(self.every_s);
        }
        v
    }
}

/// The chip's proposal: what kind of ask these words are — thought ·
/// objective · intention — and, for an intention, what it serves, what
/// wakes it, and its cadence. A typed prefix ("intention: …") is the human's
/// flip and wins; the words after it are the ask.
pub fn read_words(text: &str) -> Read {
    let mut t: String = text.split_whitespace().collect::<Vec<_>>().join(" ");
    let mut kind: Option<String> = None;
    let mut pinned = false;
    if let Some(m) = PREFIX.captures(&t) {
        kind = Some(m[1].to_lowercase());
        t = m[2].trim().to_string();
        pinned = true;
    }
    let low = t.to_lowercase();
    let kind = kind.unwrap_or_else(|| {
        if INTENT.is_match(&low) {
            "intention".into()
        } else if THOUGHT.is_match(&low) {
            "thought".into()
        } else {
            "objective".into()
        }
    });
    let mut out = Read {
        kind: kind.clone(),
        words: t,
        pinned,
        serves: None,
        interests: None,
        every_s: None,
    };
    if kind == "intention" {
        let mut serves = "business";
        for (s, pat) in SERVES_RE.iter() {
            if pat.is_match(&low) {
                serves = s;
                break;
            }
        }
        let mut interests = Vec::new();
        if WAKES_WATCH.is_match(&low) {
            interests.push(WATCH_RED.to_string());
        }
        if WAKES_IMPROVE.is_match(&low) {
            interests.push("improvement".to_string());
        }
        if WAKES_COST.is_match(&low) {
            interests.push("cost-anomaly".to_string());
        }
        let every = EVERY.captures(&low).map(|m| {
            let n: i64 = m
                .get(1)
                .map(|g| g.as_str().trim().parse().unwrap_or(1))
                .unwrap_or(1);
            n * unit_seconds(&m[2].to_lowercase())
        });
        out.serves = Some(serves.to_string());
        out.interests = Some(interests);
        out.every_s = every;
    }
    out
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn the_loops_words() {
        assert!(cannot_act(Some("  **Cannot act** — no tools here")));
        assert!(!cannot_act(Some("I could act, but I cannot act on this")));
        assert!(!cannot_act(None));
        assert_eq!(
            watch_note(
                "a body's lease lapsed",
                "bodies_dormant",
                ">=",
                &json!(1.0),
                &json!(2)
            ),
            "watch \"a body's lease lapsed\" went red: bodies_dormant >= 1.0, value 2"
        );
        assert_eq!(
            observed_words("improvement", "ask_1", None),
            "a marker of kind 'improvement' on ask_1"
        );
        let h1 = crew_shape_hash(&[("b".into(), json!([])), ("a".into(), json!(["x"]))]);
        let h2 = crew_shape_hash(&[("a".into(), json!(["x"])), ("b".into(), json!([]))]);
        assert_eq!(h1, h2);
    }

    #[test]
    fn the_words_propose_the_kind_and_the_prefix_flips_it() {
        let r = read_words("what is today's date?");
        assert_eq!((r.kind.as_str(), r.pinned), ("thought", false));
        let r = read_words("stock the pantry for the week");
        assert_eq!(r.kind, "objective");
        let r = read_words("keep the crew alive; whenever a watch goes red, act every 2 hours");
        assert_eq!(r.kind, "intention");
        assert_eq!(r.serves.as_deref(), Some("resiliency"));
        assert_eq!(r.interests.as_deref(), Some(&["watch-red".to_string()][..]));
        assert_eq!(r.every_s, Some(7200));
        let r = read_words("  Objective:  what is this?  ");
        assert_eq!(
            (r.kind.as_str(), r.words.as_str(), r.pinned),
            ("objective", "what is this?", true)
        );
    }
}
