// PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp8 row 3c, THE REMEDIATION RAIL · 2026-09-27
//! `orreth.levers/1` — the pure half of `orreth_spine.levers` (P7 sp8 row 3c,
//! THE REMEDIATION RAIL): every governed act the kernel itself can pull is
//! DECLARED as data in `spine/levers.v0.json` beside `tools.v0.json`, read by
//! BOTH kernels; the planner is shown the levers this door serves for a red
//! watch's metric and answers IN the catalogue ("LEVER: body.restart name=echo
//! — BECAUSE: …"); the DOSSIER the kernel read off the ground is handed to it
//! in plain words in place of a marker id; and every outcome the kernel
//! attributes has its words here. Measured by `spine/conformance/levers-v0.json`
//! (`lever_manifest` · `lever_remedies` · `lever_words` · `read_lever` ·
//! `dossier_words` · `remedy_words` · `outcome_words` · `ago_words`). The
//! forensic read, the pull and the attribution turn in [`crate::levers_live`].

use crate::py::{fold_ws, python_str, repr_str};
use regex::Regex;
use serde_json::{json, Map, Value};
use std::path::{Path, PathBuf};
use std::sync::LazyLock;

/// The catalogue's format word.
pub const FORMAT: &str = "orreth-levers/1";
/// The file, beside `tools.v0.json`.
pub const FILE: &str = "levers.v0.json";
/// What every declaration carries.
pub const DECLARED_KEYS: [&str; 7] = [
    "name",
    "description",
    "needs",
    "consequence",
    "for",
    "doors",
    "settles_s",
];
pub const CLASSES: [&str; 3] = ["routine", "consequential", "grave"];
/// This kernel's door, as the catalogue names it.
pub const DOOR: &str = "rust";
pub const KERNEL: &str = "the kernel";
/// Levers per red episode before the human is told.
pub const TRIES: i64 = 2;
/// The planner's word for "no lever fits".
pub const NONE: &str = "none";
pub const OUTCOMES: [&str; 4] = ["cured", "self-healed", "still-red", "cancelled"];

/// The spine home: `ORRETH_SPINE`, else the crate's `../../../../spine`.
pub fn spine_dir() -> PathBuf {
    crate::tools::spine_dir()
}

/// `levers.catalogue` on a document already read: the format checked, every
/// lever whole, the class known, no name twice. Refuses in words.
pub fn catalogue_of(doc: &Value) -> Result<Vec<Value>, String> {
    if doc["format"].as_str() != Some(FORMAT) {
        return Err(format!(
            "not a lever catalogue: format {}, expected {}",
            doc["format"],
            repr_str(FORMAT)
        ));
    }
    let mut out = Vec::new();
    let mut seen = std::collections::HashSet::new();
    for d in doc["levers"].as_array().cloned().unwrap_or_default() {
        let name = d["name"].as_str().unwrap_or("?").to_string();
        let missing: Vec<&str> = DECLARED_KEYS
            .iter()
            .copied()
            .filter(|k| d.get(k).is_none())
            .collect();
        if !missing.is_empty() {
            return Err(format!(
                "the lever declaration {} lacks {}",
                repr_str(&name),
                missing.join(", ")
            ));
        }
        let cls = d["consequence"].as_str().unwrap_or("");
        if !CLASSES.contains(&cls) {
            return Err(format!(
                "the {} lever declares an unknown class {} — the classes: {}",
                repr_str(&name),
                repr_str(cls),
                CLASSES.join(", ")
            ));
        }
        if !seen.insert(name.clone()) {
            return Err(format!("the lever {} is declared twice", repr_str(&name)));
        }
        out.push(d);
    }
    Ok(out)
}

/// `levers.catalogue`: the file beside the tools', read and checked.
pub fn catalogue(spine: &Path) -> Result<Vec<Value>, String> {
    let path = spine.join(FILE);
    let text = std::fs::read_to_string(&path).map_err(|e| {
        format!(
            "the lever catalogue at {} could not be read: {e}",
            path.display()
        )
    })?;
    let doc: Value = serde_json::from_str(&text)
        .map_err(|e| format!("the lever catalogue at {} is not JSON: {e}", path.display()))?;
    catalogue_of(&doc)
}

/// `levers.lever_manifest`: what a lever DECLARES, as the conformance pins it.
pub fn manifest(decl: &Value) -> Value {
    json!({
        "name": decl["name"], "description": decl["description"], "needs": decl["needs"],
        "consequence": decl["consequence"], "for": decl["for"], "doors": decl["doors"],
        "settles_s": decl["settles_s"].as_i64().unwrap_or(0),
    })
}

/// One declaration by name.
pub fn declared<'a>(levers: &'a [Value], name: &str) -> Option<&'a Value> {
    levers.iter().find(|d| d["name"].as_str() == Some(name))
}

fn has(list: &Value, s: &str) -> bool {
    list.as_array()
        .is_some_and(|a| a.iter().any(|x| x.as_str() == Some(s)))
}

/// `levers.remedies`: the levers this door serves that can remedy a watch on
/// `metric` — declared for the metric (or for any, `*`), served by the door,
/// never grave.
pub fn remedies<'a>(levers: &'a [Value], metric: &str, door: &str) -> Vec<&'a Value> {
    levers
        .iter()
        .filter(|d| {
            has(&d["doors"], door)
                && d["consequence"].as_str() != Some("grave")
                && (has(&d["for"], metric) || has(&d["for"], "*"))
        })
        .collect()
}

/// `levers.lever_words`: the catalogue as the planner reads it.
pub fn lever_words(levers: &[&Value]) -> String {
    if levers.is_empty() {
        return "LEVERS this kernel can pull for this watch: none.".into();
    }
    let mut lines = vec![
        "LEVERS this kernel can pull for this watch (name and what it needs · what it does):"
            .to_string(),
    ];
    for d in levers {
        let needs = d["needs"]
            .as_object()
            .map(|m| {
                m.iter()
                    .map(|(k, v)| format!("{k}=<{}>", python_str(v)))
                    .collect::<Vec<_>>()
                    .join(" ")
            })
            .unwrap_or_default();
        let hold = if d["consequence"].as_str() == Some("consequential") {
            " Holds for a person's yes before it runs."
        } else {
            " Runs at once."
        };
        lines.push(format!(
            "- {}{} · {}{hold}",
            d["name"].as_str().unwrap_or_default(),
            if needs.is_empty() {
                String::new()
            } else {
                format!(" {needs}")
            },
            d["description"].as_str().unwrap_or_default()
        ));
    }
    lines.join("\n")
}

pub const ANSWER_SHAPE: &str = "Reply on ONE line, in this shape and nothing else:\nLEVER: <name> <what it \
                                needs>=<value> — BECAUSE: <one plain sentence, from the dossier>\nor, when no \
                                lever fits: LEVER: none — BECAUSE: <one plain sentence>";

/// `levers.remedy_words`: what the kernel asks the planner under a RED WATCH.
pub fn remedy_words(serves: &str, words: &str, dossier_text: &str, levers_text: &str) -> String {
    format!(
        "INTENTION (serves {serves}): {words}\nTHE DOSSIER — what the kernel read on the ground, no guessing \
         needed:\n{dossier_text}\n{levers_text}\n{ANSWER_SHAPE}"
    )
}

const MARKS: &str = "*#-> \"“'`";
static LEVER_RE: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(
        r#"(?is)^lever\s*:[\s*_`]*(none|[a-z][a-z0-9_.-]*)((?:\s+[a-z_][a-z0-9_]*\s*=\s*(?:"[^"]*"|“[^”]*”|'[^']*'|[^\s,;]+))*)\s*[\s—–\-:,;.]*\s*(?:because\s*:?\s*)?(.*)$"#,
    )
    .unwrap()
});
static ARG_RE: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(r#"(?i)([a-z_][a-z0-9_]*)\s*=\s*("[^"]*"|“[^”]*”|'[^']*'|[^\s,;]+)"#).unwrap()
});
static PREFACE_RE: LazyLock<Regex> = LazyLock::new(|| Regex::new(r"^[^:.]{0,60}:\s*").unwrap());

fn strip_marks(s: &str) -> &str {
    s.trim_start_matches(|c| MARKS.contains(c))
}

/// What `read_lever` reads: the lever named (`None` = "no lever fits"), its
/// arguments, the planner's reason.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Read {
    pub lever: Option<String>,
    pub args: Map<String, Value>,
    pub because: String,
}

impl Read {
    /// The Python dict, as the fixture spells it.
    pub fn to_value(&self) -> Value {
        json!({"lever": self.lever, "args": Value::Object(self.args.clone()), "because": self.because})
    }
}

fn read_match(head: &str) -> Option<Read> {
    let m = LEVER_RE.captures(head)?;
    let name = m[1].to_lowercase();
    let mut args = Map::new();
    for a in ARG_RE.captures_iter(m.get(2).map_or("", |g| g.as_str())) {
        let v = a[2].trim_matches(|c| "\"'“”".contains(c)).to_string();
        args.insert(a[1].to_lowercase(), Value::String(v));
    }
    let because = fold_ws(&m[3]);
    let because = because
        .trim_matches(|c| MARKS.contains(c) || c == '”')
        .trim_end_matches('.')
        .to_string();
    Some(Read {
        lever: if name == NONE { None } else { Some(name) },
        args,
        because,
    })
}

/// `levers.read_lever`: the planner's answer read IN the catalogue — `None`
/// when the reply is not in the shape at all (a sentence: the crew's road).
/// Marks and one short preface ending in a colon are forgiven.
pub fn read_lever(reply: Option<&str>) -> Option<Read> {
    let folded = fold_ws(reply.unwrap_or(""));
    let head = strip_marks(&folded);
    if let Some(r) = read_match(head) {
        return Some(r);
    }
    let p = PREFACE_RE.find(head)?;
    if p.as_str().trim().to_lowercase().starts_with("lever") {
        return None;
    }
    read_match(strip_marks(&head[p.end()..]))
}

/// `levers.ago_words`: `40` → `40 seconds ago` · `130` → `2 minutes ago` · `7300` → `2 hours ago`.
pub fn ago_words(s: Option<i64>) -> String {
    let Some(s) = s else {
        return "just now".into();
    };
    let plural = |n: i64, w: &str| format!("{n} {w}{} ago", if n == 1 { "" } else { "s" });
    if s < 60 {
        return plural(s, "second");
    }
    if s < 3600 {
        return plural(s / 60, "minute");
    }
    plural(s / 3600, "hour")
}

fn hms(iso: &Value) -> String {
    let Some(s) = iso.as_str() else {
        return "?".into();
    };
    if s.is_empty() {
        return "?".into();
    }
    let chars: Vec<char> = s.chars().collect();
    if chars.len() >= 19 && chars[10] == 'T' {
        chars[11..19].iter().collect()
    } else {
        s.to_string()
    }
}

fn args_words(args: &Value) -> String {
    args.as_object()
        .map(|m| {
            m.iter()
                .map(|(k, v)| format!("{k}={}", python_str(v)))
                .collect::<Vec<_>>()
                .join(" ")
        })
        .unwrap_or_default()
}

fn with_args(head: &str, args: &Value) -> String {
    format!("{head} {}", args_words(args))
        .trim_end()
        .to_string()
}

fn str_or(v: &Value, or: &str) -> String {
    v.as_str()
        .filter(|s| !s.is_empty())
        .unwrap_or(or)
        .to_string()
}

/// `levers.dossier_words`: the dossier as the planner (and the human) reads it
/// — six lines, each a plain sentence. Pure: every clock and every "ago" is
/// already in the value.
pub fn dossier_words(d: &Value) -> String {
    let w = &d["watch"];
    let since = if w["since"].as_str().is_some_and(|s| !s.is_empty()) {
        format!(
            ", since {} ({})",
            hms(&w["since"]),
            ago_words(w["since_s"].as_f64().map(|f| f as i64))
        )
    } else {
        String::new()
    };
    let mut out = vec![format!(
        "THE WATCH: {} is {} — red when {} {} {}, now {}{since}.",
        repr_str(w["name"].as_str().unwrap_or_default()),
        python_str(&w["state"]),
        python_str(&w["metric"]),
        python_str(&w["op"]),
        python_str(&w["threshold"]),
        python_str(&w["value"])
    )];
    let readings: Vec<String> = d["readings"]
        .as_array()
        .map(|a| {
            a.iter()
                .map(|x| {
                    format!(
                        "{} at {} (value {})",
                        python_str(&x["to"]),
                        hms(&x["at"]),
                        python_str(&x["value"])
                    )
                })
                .collect()
        })
        .unwrap_or_default();
    out.push(format!(
        "WHAT IT SAW LATELY: {}.",
        if readings.is_empty() {
            "nothing before this".to_string()
        } else {
            readings.join(" · ")
        }
    ));
    let subjects: Vec<String> = d["subjects"]
        .as_array()
        .map(|a| {
            a.iter()
                .map(|x| {
                    format!(
                        "{} ({}) — {}",
                        python_str(&x["name"]),
                        python_str(&x["kind"]),
                        python_str(&x["state"])
                    )
                })
                .collect()
        })
        .unwrap_or_default();
    out.push(format!(
        "WHO IT NAMES: {}.",
        if subjects.is_empty() {
            "no one by name — the metric is the world's".to_string()
        } else {
            subjects.join("; ")
        }
    ));
    let acts: Vec<String> = d["acts"]
        .as_array()
        .map(|a| {
            a.iter()
                .map(|x| format!("{} {}", hms(&x["at"]), python_str(&x["words"])))
                .collect()
        })
        .unwrap_or_default();
    out.push(format!(
        "THE LAST ACTS ON THEM: {}.",
        if acts.is_empty() {
            "none recorded".to_string()
        } else {
            acts.join(" · ")
        }
    ));
    let last = &d["last_red"];
    if last.is_object() {
        let pulled = match last["lever"].as_str() {
            Some(l) if !l.is_empty() && l != NONE => {
                with_args(&format!("the kernel pulled {l}"), &last["args"])
            }
            _ => "no lever was pulled".to_string(),
        };
        let note = match last["note"].as_str() {
            Some(n) if !n.is_empty() => format!(" ({n})"),
            _ => String::new(),
        };
        out.push(format!(
            "THE LAST TIME IT WENT RED: {} — {pulled}; {}{note}.",
            hms(&last["at"]),
            str_or(&last["outcome"], "still open")
        ));
    } else {
        out.push("THE LAST TIME IT WENT RED: never before.".into());
    }
    let tried: Vec<String> = d["tried"]
        .as_array()
        .map(|a| {
            a.iter()
                .map(|x| {
                    format!(
                        "{} → {}",
                        with_args(x["lever"].as_str().unwrap_or_default(), &x["args"]),
                        str_or(&x["outcome"], "no change yet")
                    )
                })
                .collect()
        })
        .unwrap_or_default();
    out.push(format!(
        "TRIED THIS TIME: {}.",
        if tried.is_empty() {
            "nothing yet".to_string()
        } else {
            tried.join(" · ")
        }
    ));
    out.join("\n")
}

// ---- the outcome's words (d) ------------------------------------------------------------------

pub fn cured_note(watch: &str, lever: &str, args: &Value, because: &str) -> String {
    format!(
        "{} — the planner's reason: {because}",
        with_args(
            &format!(
                "watch {} went green after the kernel pulled {lever}",
                repr_str(watch)
            ),
            args
        )
    )
}

pub fn self_healed_note(watch: &str) -> String {
    format!(
        "watch {} went green on its own — the kernel pulled no lever; recorded as self-healed",
        repr_str(watch)
    )
}

pub fn still_red_note(watch: &str, lever: &str, args: &Value, settles_s: i64) -> String {
    with_args(
        &format!(
            "watch {} is still red {settles_s} seconds after the kernel pulled {lever}",
            repr_str(watch)
        ),
        args,
    )
}

pub fn cancelled_note(watch: &str, lever: &str, args: &Value, why: &str) -> String {
    format!(
        "{} lever for watch {} never ran — {why}",
        with_args(&format!("the {lever}"), args),
        repr_str(watch)
    )
}

pub fn no_lever_note(watch: &str, because: &str) -> String {
    format!(
        "no lever fits watch {} — the planner's reason: {because}",
        repr_str(watch)
    )
}

pub fn unserved_note(watch: &str, lever: &str) -> String {
    format!(
        "the planner named {lever} for watch {} — a lever this door does not serve",
        repr_str(watch)
    )
}

pub fn pulled_words(lever: &str, args: &Value, because: &str, result: &str) -> String {
    format!(
        "{}: {result} Because {because}.",
        with_args(
            &format!("On the intention's authority the kernel pulled {lever}"),
            args
        )
    )
}

pub fn handed_words(watch: &str, tried: &[Value], dossier_text: &str) -> String {
    let what: Vec<String> = tried
        .iter()
        .map(|t| with_args(t["lever"].as_str().unwrap_or_default(), &t["args"]))
        .collect();
    let what = if what.is_empty() {
        "no lever".to_string()
    } else {
        what.join(" · ")
    };
    format!(
        "Watch {} is still red after the kernel tried {what}. The kernel has no other lever for it — this one \
         is yours. What the kernel read on the ground:\n{dossier_text}",
        repr_str(watch)
    )
}

pub fn notice_words(watch: &str, because: &str, dossier_text: &str) -> String {
    format!(
        "Watch {} is red and no lever the kernel holds fits it — the planner's reason: {because}. This one is \
         yours. What the kernel read on the ground:\n{dossier_text}",
        repr_str(watch)
    )
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn the_planner_answers_in_the_catalogue() {
        let r = read_lever(Some(
            "LEVER: body.restart name=echo — BECAUSE: echo is parked after three deaths.",
        ))
        .unwrap();
        assert_eq!(r.lever.as_deref(), Some("body.restart"));
        assert_eq!(r.args["name"], json!("echo"));
        assert_eq!(r.because, "echo is parked after three deaths");
        let r = read_lever(Some(
            "**LEVER:** none - because the waiting ask needs a body",
        ))
        .unwrap();
        assert_eq!(r.lever, None);
        assert_eq!(r.because, "the waiting ask needs a body");
        assert!(read_lever(Some("Restart the echo body.")).is_none());
        assert!(read_lever(None).is_none());
        assert_eq!(ago_words(Some(61)), "1 minute ago");
        assert_eq!(ago_words(None), "just now");
    }
}
