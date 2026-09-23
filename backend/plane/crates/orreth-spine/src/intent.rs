// PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp3, the ask road · 2026-09-22
//! The pure half of `orreth_spine.intent` that the ask door needs — P23
//! (block 11): THE KIND OF AN ASK. The words propose it (thought · objective
//! · intention), a typed prefix is the human's flip and wins, and an
//! intention's words also say what it serves, what wakes it (its interests)
//! and its cadence. Every regex is the reference's, character for character;
//! measured by the conformance kind `ask_kind` (`askroad-v0.json`). The stop's
//! and restart's demands live in [`crate::proof`]; the loop itself is sp4's.

use regex::Regex;
use serde_json::{json, Value};
use std::sync::LazyLock;

pub const INTENTION_DECLARED: &str = "orreth.intention.declared.v1";
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
        r"(?i)(\bkeep\b.{0,60}\b(resilient|green|alive|safe|secure|compliant|healthy|under|below|within)\b|\bwhen(ever)?\b.{0,60}\b(goes|turns|is|are|go)\s+(red|down|dormant|late|over)\b|\bevery\s+(\d+\s+)?(minute|hour|day|week)s?\b|\bfrom now on\b|\bwatch for\b|\bstanding\b|\bas long as\b|\bany ?time\b)",
    )
    .unwrap()
});
static THOUGHT: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(r"(?i)(\?\s*$|^(who|what|what's|whats|when|where|why|how|is|are|does|do|can|could|would|should|which|did|tell me|explain|describe|repeat)\b)").unwrap()
});
static EVERY: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r"(?i)\bevery\s+(\d+\s+)?(minute|hour|day|week)s?\b").unwrap());
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
