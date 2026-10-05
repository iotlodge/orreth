// PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch Phase 8 THE WORKSHOP sp1, THE PATH: universe · floor · room on one ScopePath · 2026-10-05
//! THE PATH (canon 0010 lock 2 · 0000's recursion contract carried back), PURE — the
//! laws `orreth_spine.levels` keeps, word for word (fixture `levels-v0.json`): the path
//! grammar (`u:<universe>[/f:<floor>[/r:<room>]]`), the child law, the words, mode
//! tighten-only (dev → prod, never back), the experiment room (rooms only), the cascade
//! fold (0007's resolver at its minimum — soft most-specific-wins and attributed, skills
//! additive with the higher version winning, floors sorted by content hash, the resolved
//! context CONTENT-ADDRESSED), the roll-up monoid (0005's StatBundle — merge associative
//! with an identity, a breach anywhere a breach of the whole, the Beta prior applied ONCE
//! at report), the level fact, and the manifest's relative `at`. The ground half is
//! `levels_live`.

use crate::content_hash;
use serde_json::{json, Map, Value};

pub const CONTRACT: &str = "orreth.levels/1";
pub const ORDER: [&str; 3] = ["u", "f", "r"];
pub const LEVELS: [&str; 3] = ["universe", "floor", "room"];
pub const MODES: [&str; 2] = ["dev", "prod"];
/// The universe's mode, declared when its cell opens.
pub const MODE_DIAL: &str = "SPINE_MODE";
pub const MODE_DEFAULT: &str = "dev";
/// A level opened — at light, by the manifest, or on a person's word.
pub const LEVEL_OPENED: &str = "orreth.level.opened.v1";
pub const OPEN_TOOL: &str = "level.open";
pub const OPEN_CLASS: &str = "consequential";
pub const OPEN_LEVEL: &str = "L2";
pub const KERNEL: &str = "the kernel";
pub const BY_MANIFEST: &str = "the crew manifest";
pub const GRAMMAR: &str =
    "a scope path reads u:<universe>, u:<universe>/f:<floor>, or u:<universe>/f:<floor>/r:<room>";
const OUTCOMES: [&str; 4] = ["success", "failure", "partial", "aborted"];
const COSTS: [&str; 4] = ["tokens", "model_calls", "usd", "wall_ms"];

fn name_ok(name: &str) -> bool {
    let b = name.as_bytes();
    (1..=48).contains(&b.len())
        && b.iter()
            .all(|c| c.is_ascii_lowercase() || c.is_ascii_digit() || *c == b'_' || *c == b'-')
}

fn level_word(letter: &str) -> &'static str {
    match letter {
        "u" => "universe",
        "f" => "floor",
        _ => "room",
    }
}

// ---- the path grammar ---------------------------------------------------------------------

/// The path's levels, root to leaf — `[("u","dev"), ("f","ops"), ("r","bob")]`; a path that
/// does not read as the grammar refuses in words (Python's `repr` quotes, as the fixture pins).
pub fn parse(path: &str) -> Result<Vec<(String, String)>, String> {
    let refuse = || format!("{GRAMMAR} — got {}", py_repr(path));
    let parts: Vec<&str> = path.split('/').collect();
    if parts.is_empty() || parts.len() > 3 {
        return Err(refuse());
    }
    let mut out = Vec::new();
    for (i, part) in parts.iter().enumerate() {
        let (letter, name) = part.split_once(':').unwrap_or((part, ""));
        if letter != ORDER[i] || !name_ok(name) {
            return Err(refuse());
        }
        out.push((letter.to_string(), name.to_string()));
    }
    Ok(out)
}

/// Python's `repr` of a str: single quotes unless the text holds one and no double quote.
pub fn py_repr(s: &str) -> String {
    if s.contains('\'') && !s.contains('"') {
        format!("\"{s}\"")
    } else {
        format!("'{}'", s.replace('\\', "\\\\").replace('\'', "\\'"))
    }
}

pub fn ok(path: &str) -> bool {
    parse(path).is_ok()
}

/// universe · floor · room.
pub fn level_of(path: &str) -> Result<&'static str, String> {
    Ok(level_word(&parse(path)?.last().unwrap().0))
}

pub fn name_of(path: &str) -> Result<String, String> {
    Ok(parse(path)?.last().unwrap().1.clone())
}

/// The universe a path stands in — its first segment.
pub fn universe_of(path: &str) -> Result<String, String> {
    Ok(format!("u:{}", parse(path)?[0].1))
}

/// The level above (None at the universe).
pub fn parent_of(path: &str) -> Result<Option<String>, String> {
    let levels = parse(path)?;
    if levels.len() == 1 {
        return Ok(None);
    }
    Ok(Some(join(&levels[..levels.len() - 1])))
}

fn join(levels: &[(String, String)]) -> String {
    levels
        .iter()
        .map(|(k, v)| format!("{k}:{v}"))
        .collect::<Vec<_>>()
        .join("/")
}

/// Root to leaf, the path itself last.
pub fn ancestors(path: &str) -> Result<Vec<String>, String> {
    let levels = parse(path)?;
    Ok((0..levels.len()).map(|i| join(&levels[..=i])).collect())
}

/// A path is within an ancestor when it is the ancestor or stands below it (the seat's law).
pub fn within(path: &str, ancestor: &str) -> bool {
    crate::seat::within(path, ancestor)
}

/// The path a new level would have — the child law.
pub fn child(parent: &str, level: &str, name: &str) -> Result<String, String> {
    if !LEVELS.contains(&level) {
        return Err(format!(
            "a level is one of floor or room (a universe opens as a cell) — got {}",
            py_repr(level)
        ));
    }
    if level == "universe" {
        return Err("a universe opens as a cell, never under another scope".into());
    }
    if !name_ok(name) {
        return Err("a level's name is lower-case letters, digits, - and _ (1 to 48)".into());
    }
    let up = level_of(parent)?;
    if level == "floor" && up != "universe" {
        return Err(format!("a floor opens under a universe — {parent} is a {up}"));
    }
    if level == "room" && up != "floor" {
        return Err(format!("a room opens on a floor — {parent} is a {up}"));
    }
    Ok(format!(
        "{parent}/{}:{name}",
        if level == "floor" { "f" } else { "r" }
    ))
}

/// The path in the human's words.
pub fn words(path: &str) -> Result<String, String> {
    let l = parse(path)?;
    Ok(match l.len() {
        1 => format!("universe {}", l[0].1),
        2 => format!("floor {} of universe {}", l[1].1, l[0].1),
        _ => format!(
            "room {} on floor {} of universe {}",
            l[2].1, l[1].1, l[0].1
        ),
    })
}

// ---- mode: tighten-only -------------------------------------------------------------------

/// The universe's declared mode from its dial: unset or empty → dev; else dev or prod.
pub fn mode_of_dial(value: Option<&str>) -> Result<String, String> {
    let v = value.unwrap_or("").trim().to_ascii_lowercase();
    if v.is_empty() {
        return Ok(MODE_DEFAULT.into());
    }
    if !MODES.contains(&v.as_str()) {
        return Err(format!(
            "a universe's mode is dev or prod — {MODE_DIAL} says {}",
            py_repr(value.unwrap_or(""))
        ));
    }
    Ok(v)
}

fn mode_rank(m: &str) -> Option<usize> {
    MODES.iter().position(|x| *x == m)
}

/// The mode a level opens with: unasked → its parent's; the same or tighter → as asked;
/// looser → refused.
pub fn tighten(parent_mode: &str, asked: Option<&str>) -> Result<String, String> {
    let Some(p) = mode_rank(parent_mode) else {
        return Err(format!("a mode is dev or prod — got {}", py_repr(parent_mode)));
    };
    let Some(a) = asked.filter(|a| !a.trim().is_empty()) else {
        return Ok(parent_mode.to_string());
    };
    let al = a.trim().to_ascii_lowercase();
    let Some(r) = mode_rank(&al) else {
        return Err(format!("a mode is dev or prod — got {}", py_repr(a)));
    };
    if r < p {
        return Err(format!(
            "mode only tightens down the path — under a {parent_mode} level every floor and room is \
             {parent_mode}; {al} is looser"
        ));
    }
    Ok(al)
}

/// Only a room opens as an experiment room.
pub fn experiment_ok(level: &str, experiment: bool) -> Result<(), String> {
    if experiment && level != "room" {
        return Err("only a room opens as an experiment room".into());
    }
    Ok(())
}

// ---- the cascade fold ---------------------------------------------------------------------

fn ver_key(v: &str) -> Vec<i64> {
    v.split('-')
        .next()
        .unwrap_or("")
        .split('.')
        .map(|x| x.parse::<i64>().unwrap_or(0))
        .collect()
}

/// The fold, root → leaf: `soft` most-specific-wins and attributed, `skills` additive with
/// the higher version winning (a tie keeps the earlier), `floors` the union sorted by content
/// hash, `mode` the tightest, `as_of` every tier; the id the content hash of the content.
pub fn cascade(tiers: &[Value]) -> Result<Value, String> {
    if tiers.is_empty() {
        return Err("a cascade folds at least one tier".into());
    }
    let mut soft: Map<String, Value> = Map::new();
    let mut skills: Vec<(String, String)> = Vec::new();
    let mut floors: Vec<Value> = Vec::new();
    let mut mode = "dev".to_string();
    let mut as_of = Vec::new();
    for t in tiers {
        let scope = t["scope"].as_str().unwrap_or_default().to_string();
        if let Some(o) = t["soft"].as_object() {
            for (key, std) in o {
                let mut v = json!({"value": std["value"], "from_scope": scope});
                if let Some(ver) = std.get("version") {
                    v["version"] = ver.clone();
                }
                soft.insert(key.clone(), v);
            }
        }
        if let Some(o) = t["skills"].as_object() {
            for (name, ver) in o {
                let ver = match ver {
                    Value::String(s) => s.clone(),
                    other => other.to_string(),
                };
                match skills.iter_mut().find(|(n, _)| n == name) {
                    Some((_, have)) => {
                        if ver_key(&ver) > ver_key(have) {
                            *have = ver;
                        }
                    }
                    None => {
                        if ver_key(&ver) > ver_key("0.0.0") || ver_key(&ver) == ver_key("0.0.0") {
                            // Python: max("0.0.0", ver) — the earlier (the default) wins a tie
                            let keep = if ver_key(&ver) > ver_key("0.0.0") {
                                ver
                            } else {
                                "0.0.0".into()
                            };
                            skills.push((name.clone(), keep));
                        }
                    }
                }
            }
        }
        if let Some(a) = t["floors"].as_array() {
            for fl in a {
                if !floors.contains(fl) {
                    floors.push(fl.clone());
                }
            }
        }
        let m = t["mode"].as_str().filter(|m| !m.is_empty()).unwrap_or("dev").to_string();
        if let (Some(r), Some(have)) = (mode_rank(&m), mode_rank(&mode)) {
            if r > have {
                mode = m.clone();
            }
        }
        let version = match &t["version"] {
            Value::Null => "0".to_string(),
            Value::String(s) if s.is_empty() => "0".to_string(),
            Value::String(s) => s.clone(),
            other => other.to_string(),
        };
        as_of.push(json!({"scope": scope, "version": version, "mode": m}));
    }
    floors.sort_by_key(content_hash);
    skills.sort();
    let skills: Map<String, Value> = skills
        .into_iter()
        .map(|(n, v)| (n, Value::String(v)))
        .collect();
    let content = json!({
        "scope": tiers[tiers.len() - 1]["scope"], "mode": mode, "floors": floors, "soft": soft,
        "skills": skills, "as_of": as_of,
    });
    let mut out = json!({"id": content_hash(&content)});
    for (k, v) in content.as_object().unwrap() {
        out[k] = v.clone();
    }
    Ok(out)
}

// ---- the roll-up monoid ------------------------------------------------------------------

/// A number as the reference keeps it: an int stays an int, a float a float.
fn num_add(a: &Value, b: &Value) -> Value {
    match (a.as_i64(), b.as_i64()) {
        (Some(x), Some(y)) if !a.is_f64() && !b.is_f64() => json!(x + y),
        _ => json!(a.as_f64().unwrap_or(0.0) + b.as_f64().unwrap_or(0.0)),
    }
}

fn num_min(a: &Value, b: &Value) -> Value {
    if b.as_f64().unwrap_or(0.0) < a.as_f64().unwrap_or(0.0) {
        b.clone()
    } else {
        a.clone()
    }
}

fn num_max(a: &Value, b: &Value) -> Value {
    if b.as_f64().unwrap_or(0.0) > a.as_f64().unwrap_or(0.0) {
        b.clone()
    } else {
        a.clone()
    }
}

fn num_sq(a: &Value) -> Value {
    match a.as_i64() {
        Some(x) if !a.is_f64() => json!(x * x),
        _ => json!(a.as_f64().unwrap_or(0.0).powf(2.0)),
    }
}

pub fn empty_bundle() -> Value {
    let mut outcomes = Map::new();
    for o in OUTCOMES {
        outcomes.insert(o.into(), json!(0));
    }
    let mut cost = Map::new();
    for c in COSTS {
        cost.insert(c.into(), json!(0));
    }
    json!({"n": 0, "outcomes": outcomes, "per_objective": [], "cost": cost, "compliance": "clean"})
}

/// Lift one run into the monoid.
pub fn bundle_of(run: &Value) -> Value {
    let mut b = empty_bundle();
    b["n"] = json!(1);
    if let Some(o) = run["outcome"].as_str() {
        b["outcomes"][o] = json!(1);
    }
    let mut per = Vec::new();
    for s in run["scores"].as_array().cloned().unwrap_or_default() {
        let breached = if s["floor_breached"].as_bool().unwrap_or(false) { 1 } else { 0 };
        per.push(json!({
            "objective": s["objective"], "n": 1, "sum": s["score"], "sum_sq": num_sq(&s["score"]),
            "min": s["score"], "max": s["score"], "floor_breaches": breached,
        }));
        if breached == 1 {
            b["compliance"] = json!("breached");
        }
    }
    b["per_objective"] = Value::Array(per);
    if let Some(c) = run["cost"].as_object() {
        for (k, v) in c {
            b["cost"][k] = v.clone();
        }
    }
    b
}

/// Component-wise, associative, the empty bundle its identity; a breach anywhere is a
/// breach of the whole.
pub fn merge(a: &Value, b: &Value) -> Value {
    let mut out = empty_bundle();
    out["n"] = num_add(&a["n"], &b["n"]);
    for o in OUTCOMES {
        out["outcomes"][o] = num_add(
            a["outcomes"].get(o).unwrap_or(&json!(0)),
            b["outcomes"].get(o).unwrap_or(&json!(0)),
        );
    }
    let mut stats: Vec<Value> = a["per_objective"].as_array().cloned().unwrap_or_default();
    for s in b["per_objective"].as_array().cloned().unwrap_or_default() {
        match stats
            .iter_mut()
            .find(|t| t["objective"] == s["objective"])
        {
            Some(t) => {
                t["n"] = num_add(&t["n"], &s["n"]);
                t["sum"] = num_add(&t["sum"], &s["sum"]);
                t["sum_sq"] = num_add(&t["sum_sq"], &s["sum_sq"]);
                t["min"] = num_min(&t["min"], &s["min"]);
                t["max"] = num_max(&t["max"], &s["max"]);
                t["floor_breaches"] = num_add(&t["floor_breaches"], &s["floor_breaches"]);
            }
            None => stats.push(s),
        }
    }
    stats.sort_by(|x, y| {
        x["objective"]
            .as_str()
            .unwrap_or_default()
            .cmp(y["objective"].as_str().unwrap_or_default())
    });
    out["per_objective"] = Value::Array(stats);
    for k in COSTS {
        out["cost"][k] = num_add(
            a["cost"].get(k).unwrap_or(&json!(0)),
            b["cost"].get(k).unwrap_or(&json!(0)),
        );
    }
    out["compliance"] = json!(if a["compliance"] == "breached" || b["compliance"] == "breached" {
        "breached"
    } else {
        "clean"
    });
    out
}

/// The read edge: the Beta posterior's mean, 95 % interval and n — the prior applied here
/// and only here.
pub fn report(bundle: &Value, objective: &str, prior: (f64, f64)) -> Value {
    let stat = bundle["per_objective"]
        .as_array()
        .and_then(|a| a.iter().find(|s| s["objective"] == objective));
    let (a0, b0, n) = match stat {
        Some(s) if s["n"].as_f64().unwrap_or(0.0) != 0.0 => {
            let sum = s["sum"].as_f64().unwrap_or(0.0);
            let n = s["n"].as_f64().unwrap_or(0.0);
            (prior.0 + sum, prior.1 + (n - sum), s["n"].clone())
        }
        _ => (prior.0, prior.1, json!(0)),
    };
    let mean = a0 / (a0 + b0);
    let var = (a0 * b0) / ((a0 + b0).powf(2.0) * (a0 + b0 + 1.0));
    let half = 1.96 * var.sqrt();
    json!({
        "mean": mean, "ci95": [f64::max(0.0, mean - half), f64::min(1.0, mean + half)], "n": n,
        "compliance": bundle["compliance"],
        "floor_breaches": stat.map(|s| s["floor_breaches"].clone()).unwrap_or(json!(0)),
    })
}

/// The weighted mean over NON-floor objectives (weights renormalized).
pub fn tier_score(bundle: &Value, objectives: &[Value], prior: (f64, f64)) -> Value {
    let soft: Vec<&Value> = objectives
        .iter()
        .filter(|o| !o["floor"].as_bool().unwrap_or(false))
        .collect();
    let mut total_w: f64 = soft.iter().map(|o| o["weight"].as_f64().unwrap_or(0.0)).sum();
    if total_w == 0.0 {
        total_w = 1.0;
    }
    let mut score = 0.0f64;
    for o in &soft {
        let w = o["weight"].as_f64().unwrap_or(0.0);
        let m = report(bundle, o["objective"].as_str().unwrap_or_default(), prior)["mean"]
            .as_f64()
            .unwrap_or(0.0);
        score += w / total_w * m;
    }
    json!({"score": score, "compliance": bundle["compliance"]})
}

// ---- the fact -----------------------------------------------------------------------------

/// The level fact's payload: the path as the pointer, its shape hashed, whose word and why.
pub fn opened_payload(path: &str, mode: &str, experiment: bool, by: &str, reason: &str) -> Result<Value, String> {
    let shape = json!({
        "level": level_of(path)?, "name": name_of(path)?, "parent": parent_of(path)?, "mode": mode,
        "experiment": experiment,
    });
    let mut p = json!({"ref": path, "hash": content_hash(&shape)});
    for (k, v) in shape.as_object().unwrap() {
        p[k] = v.clone();
    }
    p["by"] = json!(by);
    p["reason"] = json!(reason);
    Ok(p)
}

/// The chain: a person's word then the kernel's; the kernel's or the manifest's alone.
pub fn opened_chain(by: &str) -> Vec<String> {
    if by == KERNEL || by == BY_MANIFEST {
        vec![KERNEL.into()]
    } else {
        vec![by.into(), KERNEL.into()]
    }
}

/// `orreth.level.opened.v1` — minted now.
#[cfg(feature = "rails")]
pub fn opened_fact(path: &str, mode: &str, experiment: bool, by: &str, reason: &str) -> Result<Value, String> {
    crate::envelope::Mint {
        kind: "event".into(),
        r#type: LEVEL_OPENED.into(),
        universe_id: universe_of(path)?,
        scope_path: path.into(),
        payload: opened_payload(path, mode, experiment, by, reason)?,
        correlation_id: Some(path.into()),
        authority_chain: Some(opened_chain(by)),
        aggregate: None,
        marker: None,
    }
    .mint()
    .map_err(|e| e.to_string())
}

/// The act's plain words: what stands now.
pub fn opened_words(path: &str, mode: &str, experiment: bool) -> Result<String, String> {
    let tail = if experiment {
        " — an experiment room: nothing promotes out of it except through the Experiment gate"
    } else {
        ""
    };
    Ok(format!("{} is open ({mode}){tail}", words(path)?))
}

// ---- the manifest's levels ----------------------------------------------------------------

/// One level a crew manifest declares.
#[derive(Debug, Clone)]
pub struct Declared {
    pub at: String,
    pub mode: Option<String>,
    pub experiment: bool,
    pub declares: Option<Value>,
    pub words: String,
}

/// The levels a crew manifest declares, in order (`at` relative to the universe).
pub fn manifest_levels(manifest: &Value) -> Result<Vec<Declared>, String> {
    let mut out = Vec::new();
    for lv in manifest["levels"].as_array().cloned().unwrap_or_default() {
        let at = lv["at"].as_str().unwrap_or_default().trim().to_string();
        if at.is_empty() {
            return Err(
                "a declared level names where it stands (`at`: f:<floor> or f:<floor>/r:<room>)".into(),
            );
        }
        out.push(Declared {
            at,
            mode: lv["mode"]
                .as_str()
                .map(str::trim)
                .filter(|m| !m.is_empty())
                .map(str::to_string),
            experiment: lv["experiment"].as_bool().unwrap_or(false),
            declares: lv.get("declares").filter(|d| !d.is_null()).cloned(),
            words: lv["words"].as_str().unwrap_or_default().to_string(),
        });
    }
    Ok(out)
}

/// A manifest's relative `at` under this universe; absent → the universe; a full path
/// stands as it is when it is within.
pub fn absolute(universe: &str, at: Option<&str>) -> Result<String, String> {
    let a = at.unwrap_or("").trim();
    if a.is_empty() {
        return Ok(universe.to_string());
    }
    if a.starts_with("u:") {
        if !within(a, universe) {
            return Err(format!("{a} does not stand in {universe}"));
        }
        parse(a)?;
        return Ok(a.to_string());
    }
    let path = format!("{universe}/{a}");
    parse(&path)?;
    Ok(path)
}
