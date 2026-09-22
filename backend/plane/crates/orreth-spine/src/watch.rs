// PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp1, the bytes · 2026-09-22
//! `orreth.watch/1` — the pure half of `orreth_spine.monitor`: the SENSE of a
//! watch (W14 — RED when `value op threshold` holds now, green otherwise),
//! its human sentence, and the monitor's offer read from its words (W22).
//! Measuring the metrics and recording the turn read a ground — sp4's.

use crate::py::python_str;
use regex::Regex;
use serde_json::{json, Value};
use std::sync::LazyLock;

/// The metrics this world measures.
pub const METRICS: [&str; 5] = [
    "outbox_pending",
    "oldest_outbox_age_s",
    "asks_received",
    "bodies_alive",
    "bodies_dormant",
];
/// The ops a watch may wear.
pub const OPS: [&str; 5] = ["<=", ">=", "<", ">", "=="];

/// The sense of a watch, in one place: `Some(true)` = RED — the watched
/// condition holds now. An op not in [`OPS`] is `None` (Python's `KeyError`).
pub fn judge(op: &str, value: f64, threshold: f64) -> Option<bool> {
    Some(match op {
        "<=" => value <= threshold,
        ">=" => value >= threshold,
        "<" => value < threshold,
        ">" => value > threshold,
        "==" => value == threshold,
        _ => return None,
    })
}

/// `red` / `green`.
pub fn state(red: bool) -> &'static str {
    if red {
        "red"
    } else {
        "green"
    }
}

/// The watch in a human's sentence — the sense spelled out, never left to a
/// bare `> 0`: `red when bodies_dormant > 0.0 · now 0 → green`. The threshold
/// and value are printed as Python prints them (`0.0` stays `0.0`, `0` stays `0`).
pub fn reads(metric: &str, op: &str, threshold: &Value, value: &Value, red: bool) -> String {
    format!(
        "red when {metric} {op} {} · now {} → {}",
        python_str(threshold),
        python_str(value),
        if red { "RED" } else { "green" }
    )
}

static OFFER_RE: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r"(?i)\bpropos(?:e|ing)\b[^.\n]{0,80}?\bwatch\b").unwrap());
static COND_RE: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(r"(?i)`?\s*\b([a-z_]+)\s*(>=|<=|==|!=|>|<)\s*(-?\d+(?:\.\d+)?)\b\s*`?").unwrap()
});
pub const PROPOSE_BARE: &str =
    "propose the watch you described — call add-watch with its name, metric, op and threshold";

/// The monitor's offer: the condition in words (none when the reply names no
/// condition, or a metric this world does not measure) and the ask one click sends.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Offer {
    pub words: Option<String>,
    pub ask: String,
}

impl Offer {
    pub fn to_value(&self) -> Value {
        json!({"words": self.words, "ask": self.ask})
    }
}

/// Walk #7's friction, walk #8's cure (W22): the monitor's OFFER, read
/// honestly from its words. A reply that offers to propose a watch yields the
/// offer; the condition is read with or without backticks; an offer that
/// names no condition (or a metric this world does not measure) still offers,
/// with `words` none and the ask telling the monitor to propose through
/// add-watch. No offer: `None` — a bare condition in a sentence is a reading.
pub fn offer_in(reply: Option<&str>) -> Option<Offer> {
    let reply = reply?;
    if reply.is_empty() || !OFFER_RE.is_match(reply) {
        return None;
    }
    let Some(m) = COND_RE.captures(reply) else {
        return Some(Offer {
            words: None,
            ask: PROPOSE_BARE.into(),
        });
    };
    let metric = m[1].to_lowercase();
    if !METRICS.contains(&metric.as_str()) {
        return Some(Offer {
            words: None,
            ask: PROPOSE_BARE.into(),
        });
    }
    let words = format!("{metric} {} {}", &m[2], &m[3]);
    Some(Offer {
        ask: format!("propose a watch that {words}"),
        words: Some(words),
    })
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;

    #[test]
    fn the_sense_and_the_sentence() {
        assert_eq!(judge(">", 1.0, 0.0), Some(true));
        assert_eq!(judge("==", 0.0, 0.0), Some(true));
        assert_eq!(judge("!=", 0.0, 0.0), None);
        assert_eq!(
            reads("bodies_dormant", ">", &json!(0.0), &json!(0), false),
            "red when bodies_dormant > 0.0 · now 0 → green"
        );
        assert_eq!(
            reads("asks_received", ">", &json!(4.0), &json!(5), true),
            "red when asks_received > 4.0 · now 5 → RED"
        );
    }

    #[test]
    fn the_offer_is_read_from_the_words() {
        assert_eq!(offer_in(None), None);
        assert_eq!(offer_in(Some("")), None);
        assert_eq!(
            offer_in(Some("I am proposing a watch: BODIES_DORMANT >= 1."))
                .unwrap()
                .words
                .as_deref(),
            Some("bodies_dormant >= 1")
        );
        assert_eq!(
            offer_in(Some("I could propose a watch if you like.")).unwrap(),
            Offer {
                words: None,
                ask: PROPOSE_BARE.into()
            }
        );
    }
}
