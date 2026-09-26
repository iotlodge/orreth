// PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp8, the human profile (W58, the Mirror's first row carried) · 2026-09-26
//! `orreth.profile/1` — the pure half of `orreth_spine.profile` (canon 0003
//! "packing the mind" slot 1 · "who remembers what" · the old world's 0025 +
//! 0070 carried; W58, walk #15: cell two's librarian answered the weather for
//! the WRONG PLACE because no ground knew where JB was). What a person tells
//! this ground about themselves, provenance-labeled as the Mirror had it —
//! `you told me` (human, trusted) · `I observed` (the kernel: a told place's
//! coordinates and clock) · `the mirror noticed` (reserved) — read by every
//! body at the voiced answer, by the weather tool as its default, by the
//! clock ahead of the ground's dial, and carried over the seam with a routed
//! ask. Every regex here is the reference's, character for character; the
//! fixture `spine/conformance/profile-v0.json` measures each function. The
//! record on the ground and the doors are `profile_live`.

use crate::py::fold_ws;
use regex::Regex;
use serde_json::{json, Value};
use std::sync::LazyLock;

pub const CONTRACT: &str = "orreth.profile/1";
/// A person's own word about themselves — a fact.
pub const TOLD: &str = "orreth.profile.told.v1";
/// What the kernel found out beside a told word — a fact.
pub const OBSERVED: &str = "orreth.profile.observed.v1";
/// A word withdrawn on the person's say — a fact, never a deletion.
pub const WITHDRAWN: &str = "orreth.profile.withdrawn.v1";

pub const FIELDS: [&str; 4] = ["name", "place", "zone", "claim"];
pub const ASSERTERS: [&str; 3] = ["human", "kernel", "mirror"];
pub const KERNEL: &str = "the kernel";
pub const PROFILE_REF: &str = "the profile";
/// The pack's budget for slot 1 (0003).
pub const SLICE_CAP: usize = 700;
pub const GEOCODER: &str = "https://geocoding-api.open-meteo.com/v1/search";

pub const NOTHING_WORDS: &str = "those words tell me nothing about you — say \"my name is …\", \"I live in …\", \
                                 \"my time zone is …\", \"remember about me: …\", \"what do you know about me?\" \
                                 or \"forget about me: …\"";
pub const NONE_YET: &str = "nothing yet — you have told this ground nothing about yourself";

static READ: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(r"(?i)^(?:what do you know about me|show (?:me )?my profile|read my profile|my profile|who am i)\s*\??$").unwrap()
});
static NAME: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(r"(?i)^(?:my name is|call me|i am|i'm)\s+(?P<v>[^,.;:!?]{1,60}?)\s*[.!]?$").unwrap()
});
static PLACE: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(r"(?i)^(?:i live in|i'm in|i am in|my place is|my home is|my town is|i live at|i am living in|i'm living in)\s+(?P<v>[^;:!?]{1,120}?)\s*[.!]?$").unwrap()
});
static ZONE: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(r"(?i)^(?:my (?:time ?zone|zone|clock) is|i am on|i'm on)\s+(?P<v>[A-Za-z_]+(?:/[A-Za-z0-9_+\-]+){1,2}|UTC|GMT)\s*[.!]?$").unwrap()
});
static CLAIM: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(r"(?i)^(?:remember about me|about me|my profile)\s*:\s*(?P<v>.{1,240}?)\s*$")
        .unwrap()
});
static FORGET_FIELD: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(r"(?i)^forget (?:about me:\s*)?my (?P<f>name|place|zone|time ?zone|home|town|clock)\s*[.!]?$").unwrap()
});
static FORGET_TOPIC: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(r"(?i)^forget (?:about me:|that|about)\s*(?P<v>.{1,240}?)\s*[.!]?$").unwrap()
});
static NOT_A_NAME: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(
        r"(?i)\b(?:not|very|so|here|there|back|going|feeling|tired|happy|sad|busy|ready|done)\b",
    )
    .unwrap()
});

fn field_of(word: &str) -> &'static str {
    match word.to_lowercase().as_str() {
        "name" => "name",
        "place" | "home" | "town" => "place",
        _ => "zone", // zone · timezone · time zone · clock
    }
}

fn nothing() -> Value {
    json!({"act": Value::Null, "field": Value::Null, "value": Value::Null})
}

/// What a sentence says about the person (conformance `profile_words`):
/// `act` is `tell` · `read` · `forget` · null; a `tell` names its field and
/// carries the value in the person's own spelling; a `forget` names a field
/// or a topic; words that say nothing about the person read null.
pub fn read_words(text: &str) -> Value {
    let t = fold_ws(text);
    if t.is_empty() {
        return nothing();
    }
    if READ.is_match(&t) {
        return json!({"act": "read", "field": Value::Null, "value": Value::Null});
    }
    if let Some(m) = CLAIM.captures(&t) {
        return json!({"act": "tell", "field": "claim", "value": m["v"].trim()});
    }
    if let Some(m) = FORGET_FIELD.captures(&t) {
        return json!({"act": "forget", "field": field_of(&m["f"]), "value": Value::Null});
    }
    if let Some(m) = FORGET_TOPIC.captures(&t) {
        return json!({"act": "forget", "field": Value::Null, "value": m["v"].trim()});
    }
    if let Some(m) = ZONE.captures(&t) {
        return json!({"act": "tell", "field": "zone", "value": m["v"].trim()});
    }
    if let Some(m) = PLACE.captures(&t) {
        return json!({"act": "tell", "field": "place", "value": m["v"].trim()});
    }
    if let Some(m) = NAME.captures(&t) {
        let v = m["v"].trim().to_string();
        // a name is one to four words, no verb-ish tails ("I am tired" is not a name)
        if v.split_whitespace().count() <= 4 && !NOT_A_NAME.is_match(&v) {
            return json!({"act": "tell", "field": "name", "value": v});
        }
    }
    nothing()
}

/// The provenance label a read wears (conformance `profile_label`).
pub fn label_of(asserted_by: &str) -> Result<&'static str, String> {
    match asserted_by {
        "human" => Ok("you told me"),
        "kernel" => Ok("I observed"),
        "mirror" => Ok("the mirror noticed"),
        other => Err(format!(
            "a profile word is asserted by one of {}, not {:?}",
            ASSERTERS.join(", "),
            other
        )),
    }
}

fn s(v: &Value) -> String {
    match v {
        Value::String(x) => x.clone(),
        Value::Null => String::new(),
        other => crate::py::python_str(other),
    }
}

fn withdrawn(c: &Value) -> bool {
    crate::py::truthy(&c["withdrawn_at"])
}

/// One row's plain words — the same sentence the reference writes.
pub fn row_words(c: &Value) -> String {
    let (f, v) = (s(&c["field"]), s(&c["value"]));
    match f.as_str() {
        "name" => format!("your name is {v}"),
        "place" => {
            if s(&c["asserted_by"]) == "kernel" && c["lat"].is_number() {
                let zone = match c["zone"].as_str().filter(|z| !z.is_empty()) {
                    Some(z) => format!(", its clock {z}"),
                    None => String::new(),
                };
                format!(
                    "{v} is at {:.2},{:.2}{zone}",
                    c["lat"].as_f64().unwrap_or_default(),
                    c["lon"].as_f64().unwrap_or_default()
                )
            } else {
                format!("you live in {v}")
            }
        }
        "zone" => format!("your clock is {v}"),
        _ => v,
    }
}

/// The profile as one paragraph for the pack's first slot (conformance
/// `profile_slice`): the person's own words first, then what the kernel
/// observed (only beside the told place it explains), then what the mirror
/// noticed — each group one label, rows joined by " · " in field order
/// (name · place · zone · then the claims), the newest word per named field
/// winning, capped at SLICE_CAP. Nothing told reads NONE_YET.
pub fn slice_words(claims: &[Value]) -> String {
    let live: Vec<&Value> = claims.iter().filter(|c| !withdrawn(c)).collect();
    if live.is_empty() {
        return NONE_YET.to_string();
    }
    let told_place: Option<String> = live
        .iter()
        .find(|c| s(&c["field"]) == "place" && s(&c["asserted_by"]) == "human")
        .map(|c| s(&c["value"]));
    let mut groups: Vec<(&str, Vec<(usize, String)>)> =
        ASSERTERS.iter().map(|a| (*a, Vec::new())).collect();
    let mut seen: Vec<(String, String)> = Vec::new();
    for c in &live {
        let (by, field) = (s(&c["asserted_by"]), s(&c["field"]));
        if ["name", "place", "zone"].contains(&field.as_str()) && by == "human" {
            let key = (by.clone(), field.clone());
            if seen.contains(&key) {
                continue;
            }
            seen.push(key);
        }
        if field == "place" && by == "kernel" {
            let ev = c["evidence"].as_str().map(str::to_string);
            if ev != told_place {
                continue;
            }
        }
        let rank = FIELDS.iter().position(|f| *f == field).unwrap_or(9);
        if let Some(g) = groups.iter_mut().find(|(a, _)| *a == by) {
            g.1.push((rank, row_words(c)));
        }
    }
    let mut parts: Vec<String> = Vec::new();
    for (a, rows) in groups.iter_mut() {
        if rows.is_empty() {
            continue;
        }
        rows.sort_by_key(|(r, _)| *r); // a stable sort: newest first within a field, as the reference
        let words: Vec<&str> = rows.iter().map(|(_, w)| w.as_str()).collect();
        parts.push(format!(
            "{}: {}",
            label_of(a).unwrap_or_default(),
            words.join(" · ")
        ));
    }
    let out = parts.join(" — ");
    if out.chars().count() > SLICE_CAP {
        let head: String = out.chars().take(SLICE_CAP - 1).collect();
        return format!("{}…", head.trim_end());
    }
    out
}

/// The weather tool's default (conformance `place_default`): the newest
/// OBSERVED coordinates standing beside a live told place — `{place, lat,
/// lon, zone}` — or null when the person has told this ground no place.
pub fn place_default(claims: &[Value]) -> Value {
    let live: Vec<&Value> = claims.iter().filter(|c| !withdrawn(c)).collect();
    let told = match live
        .iter()
        .find(|c| s(&c["field"]) == "place" && s(&c["asserted_by"]) == "human")
    {
        Some(t) => s(&t["value"]),
        None => return Value::Null,
    };
    let seen = live.iter().find(|c| {
        s(&c["field"]) == "place"
            && s(&c["asserted_by"]) == "kernel"
            && c["lat"].is_number()
            && c["evidence"].as_str() == Some(told.as_str())
    });
    match seen {
        None => json!({"place": told, "lat": Value::Null, "lon": Value::Null, "zone": Value::Null}),
        Some(c) => json!({
            "place": told, "lat": c["lat"].as_f64(), "lon": c["lon"].as_f64(),
            "zone": c["zone"].as_str().filter(|z| !z.is_empty()),
        }),
    }
}

/// `did:orreth:person:jb` → `jb`; a bare name stays itself.
pub fn short(person: &str) -> &str {
    match person.rsplit_once(':') {
        Some((_, tail)) => tail,
        None => person,
    }
}

/// Slot 1 of the pack — what every body reads about the human it serves
/// (`profile.seat_words`): the carried slice when the ask came over the
/// seam, else this ground's profile of the asker.
pub fn seat_words(person: &str, words: &str, rode: bool) -> String {
    let who = short(person);
    if words == NONE_YET {
        return format!(
            "THE HUMAN you serve is {who}. They have told this ground nothing about themselves yet — \
             if their place, clock or name matters to the ask, say so plainly and invite them to say \
             \"I live in …\", \"my name is …\" or \"remember about me: …\"."
        );
    }
    let where_ = if rode {
        " (it rode here with the ask, from their home cell)"
    } else {
        ""
    };
    format!(
        "THE HUMAN you serve is {who} — their own profile, in their own provenance{where_}: {words}. \
         Sovereign: honor it, never recite it unasked; when the ask turns on their place or clock, use these."
    )
}
