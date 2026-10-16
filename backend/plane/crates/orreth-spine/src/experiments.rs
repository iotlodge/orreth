// PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch Phase 8 THE WORKSHOP sp4, THE EXPERIMENT AND THE CUT: the pure laws · 2026-10-07
//! THE EXPERIMENT AND THE CUT (canon 0010 §5 · 0005 Phase 8 sp4), PURE — the laws
//! `orreth_spine.experiments` keeps, word for word (fixture `experiments-v0.json`): the
//! experiment room's name, the arms in words, the opening's words, the reviewers' ask and the
//! FORM their verdicts take (a grade A–F per arm and a side; a risk low · medium · high), the
//! proposal's leaning and words (every reviewer by name — since sp6 the two chips among them), the
//! promotion's demand by class, the decom ladder and its words, where a next life stands. The
//! ground half is `experiments_live`.

use crate::py::repr_str;
use regex::Regex;
use serde_json::{json, Value};
use std::sync::OnceLock;

pub const CONTRACT: &str = "orreth.experiments/1";
pub const KERNEL: &str = "the kernel";
pub const OPEN_TOOL: &str = "experiment.open";
pub const PROMOTE_TOOL: &str = "experiment.promote";
pub const REST_TOOL: &str = "body.rest";
pub const DECOM_TOOL: &str = "body.decommission";
pub const RESTORE_TOOL: &str = "body.restore";
pub const ACT_CLASS: &str = "consequential";
pub const OPEN_LEVEL: &str = "L2";
pub const REST_LEVEL: &str = "L2";
pub const DECOM_LEVEL: &str = "L3-code";
pub const RESTORE_LEVEL: &str = "L2";
pub const EXPERIMENT_OPENED: &str = "orreth.experiment.opened.v1";
pub const EXPERIMENT_PROPOSED: &str = "orreth.experiment.proposed.v1";
pub const EXPERIMENT_SETTLED: &str = "orreth.experiment.settled.v1";
pub const VERDICT: &str = "orreth.verdict.v1";
pub const BODY_RESTED: &str = "orreth.body.rested.v1";
pub const BODY_DECOMMISSIONED: &str = "orreth.body.decommissioned.v1";
pub const BODY_RESTORED: &str = "orreth.body.restored.v1";
pub const MARKER_KIND: &str = "experiment";
pub const STATES: [&str; 4] = ["running", "proposed", "promoted", "declined"];
pub const ARMS: [&str; 2] = ["current", "candidate"];
pub const LADDER: [&str; 3] = ["active", "rested", "decommissioned"];
pub const REVIEWERS: [&str; 4] = ["grader", "critic", "security", "identity"]; // Phase 8 sp6: all four are asked — the empty slots are filled
pub const CHIP_REVIEWERS: [&str; 2] = ["identity", "security"];
pub const REVIEW_WAIT_S: i64 = 600;
pub const PRUNE_EVERY_S: u64 = 3600;

/// `experiments.room_name`: `exp-<agent>-<n>`.
pub fn room_name(agent: &str, n: i64) -> String {
    format!("exp-{agent}-{n}")
}

/// `experiments.arms_plan`: how many arms, in words.
pub fn arms_plan(current_version: Option<i64>) -> String {
    match current_version {
        Some(v) if v > 0 => format!("two arms — the standing version {v} and the candidate"),
        _ => "one arm — the candidate alone; no version of it stands on the shelf yet".into(),
    }
}

/// `experiments.open_words`: the held act's words.
pub fn open_words(agent: &str, room: &str, current_version: Option<i64>, golden_n: i64) -> Result<String, String> {
    let words = crate::levels::words(room)?;
    Ok(format!(
        "opening an experiment on the {agent} agent — {words} opens as an experiment room; {}; the evidence is its golden set ({golden_n} case{}); the grader, the critic, the identity chip and the security chip review under their own names; the verdict is a proposal and the promotion is yours",
        arms_plan(current_version),
        if golden_n != 1 { "s" } else { "" }
    ))
}

fn arm_label(side: &str, exp: &Value) -> String {
    if side == "current" {
        format!("version {}", crate::py::python_str(&exp["current_version"]))
    } else {
        "the candidate, the draft's declaration".into()
    }
}

fn py_list(v: &Value) -> String {
    // Python's `', '.join(map(str, expect))`
    v.as_array()
        .map(|a| a.iter().map(crate::py::python_str).collect::<Vec<_>>().join(", "))
        .unwrap_or_default()
}

fn head(s: &str, n: usize) -> String {
    s.chars().take(n).collect()
}

/// `experiments.review_ask`: the kernel's ask of a reviewer, with the evidence in it and the form.
/// The same words as the Python reference's `experiments.HARNESS_LAW` — told to every reviewer.
pub const HARNESS_LAW: &str = "THE HARNESS'S LAW: a case passes when every expected phrase appears somewhere in the reply, in any case — 'HELLO' inside 'hello work1' passes by law, not by accident. Read a pass as a pass; judge the reply's substance, never the letter-case of the match.";

pub fn review_ask(reviewer: &str, exp: &Value) -> String {
    let arms = &exp["arms"];
    let cv = exp["current_version"].as_i64();
    let mut lines = vec![format!(
        "{reviewer}, review experiment {} on the {} agent ({}). The evidence, case by case:",
        crate::py::python_str(&exp["experiment_id"]),
        crate::py::python_str(&exp["agent"]),
        arms_plan(cv)
    )];
    for side in ARMS {
        let a = &arms[side];
        if a.is_null() {
            lines.push(format!("- arm {side}: none (no version stands yet)"));
            continue;
        }
        if crate::py::truthy(&a["skipped"]) {
            lines.push(format!("- arm {side}: {}", crate::py::python_str(&a["skipped"])));
            continue;
        }
        let q = |v: &Value| if v.is_null() { "?".to_string() } else { crate::py::python_str(v) };
        lines.push(format!(
            "- arm {side} ({}): {} passed, {} failed",
            arm_label(side, exp),
            q(&a["passed"]),
            q(&a["failed"])
        ));
        for (i, d) in a["details"].as_array().map(|x| x.as_slice()).unwrap_or(&[]).iter().enumerate() {
            lines.push(format!(
                "  case {}: asked {}; expected {}; replied {} — {}",
                i + 1,
                repr_str(&crate::py::python_str(&d["ask"])),
                py_list(&d["expect"]),
                repr_str(&head(&crate::py::python_str(&d["reply"]), 200)),
                if crate::py::truthy(&d["ok"]) { "passed" } else { "FAILED" }
            ));
        }
    }
    lines.push(HARNESS_LAW.into()); // JB (SPEC-STUDIO-01 step 11, 2026-10-14): the critic read a lawful pass as a broken yardstick — the law is told
    if reviewer == "identity" {
        // Phase 8 sp6: the identity chip judges THE TRIAL LIFE'S CLAIMS the beat read off the record
        lines.push(format!("THE TRIAL LIFE'S CLAIMS, from the kernel's record — {}", crate::chips::claims_words(&exp["claims"])));
        lines.push(crate::chips::review_form("identity").into());
    } else if reviewer == "security" {
        let diff = if exp["diff"].is_null() { json!({"first": true}) } else { exp["diff"].clone() };
        lines.push(format!("THE CANDIDATE'S DIFF against the standing version — {}", crate::chips::diff_words(&diff)));
        lines.push(crate::chips::refusals_words(&exp["refusals"], exp["agent"].as_str()));
        lines.push(crate::chips::review_form("security").into());
    } else if reviewer == "grader" {
        lines.push("Answer in exactly this form, one line each: `current: <A-F> — <one line of reason>` (write `current: none` when no current arm ran), `candidate: <A-F> — <one line>`, then `verdict: candidate` or `verdict: current` or `verdict: neither`. Grade the replies against what was asked and expected — never your own words.".into());
    } else {
        lines.push("Say what the candidate changes against the current version and the risk of promoting it. End with exactly one line `risk: low` or `risk: medium` or `risk: high` — <one line of reason>.".into());
    }
    lines.join("\n")
}

fn grade_rx() -> &'static Regex {
    static RX: OnceLock<Regex> = OnceLock::new();
    RX.get_or_init(|| Regex::new(r"(?im)^\s*\**\s*(current|candidate)\s*\**\s*:\s*\**\s*(none|[A-Fa-f])\b").unwrap())
}
fn verdict_rx() -> &'static Regex {
    static RX: OnceLock<Regex> = OnceLock::new();
    RX.get_or_init(|| Regex::new(r"(?im)^\s*\**\s*verdict\s*\**\s*:\s*\**\s*(candidate|current|neither)\b").unwrap())
}
fn risk_rx() -> &'static Regex {
    static RX: OnceLock<Regex> = OnceLock::new();
    RX.get_or_init(|| Regex::new(r"(?im)^\s*\**\s*risk\s*\**\s*:\s*\**\s*(low|medium|high)\b").unwrap())
}

/// `experiments.grade_of`: the grader's verdict read off its words by the form — `{current, candidate, verdict}`.
pub fn grade_of(text: &str) -> Value {
    let mut out = json!({"current": null, "candidate": null, "verdict": null});
    for m in grade_rx().captures_iter(text) {
        let side = m[1].to_lowercase();
        let g = m[2].to_uppercase();
        out[side] = if g == "NONE" { Value::Null } else { json!(g) };
    }
    if let Some(m) = verdict_rx().captures(text) {
        out["verdict"] = json!(m[1].to_lowercase());
    }
    out
}

/// `experiments.risk_of`: the critic's risk by the form; None when the form was not kept.
pub fn risk_of(text: &str) -> Option<String> {
    risk_rx().captures(text).map(|m| m[1].to_lowercase())
}

/// `experiments.arm_words`: one arm, in words.
pub fn arm_words(side: &str, arm: &Value, exp: Option<&Value>) -> String {
    if arm.is_null() {
        return format!("{side}: no version stands yet — this is the first cut");
    }
    if crate::py::truthy(&arm["skipped"]) {
        return format!("{side}: {}", crate::py::python_str(&arm["skipped"]));
    }
    if arm["passed"].is_null() {
        return format!("{side}: running");
    }
    let passed = arm["passed"].as_i64().unwrap_or(0);
    let n = passed + arm["failed"].as_i64().unwrap_or(0);
    let label = match exp {
        Some(e) if side == "current" => format!("the standing version {}", crate::py::python_str(&e["current_version"])),
        _ => "the candidate".to_string(),
    };
    format!("{label} passed {passed} of {n}")
}

/// `experiments.leaning_of`: promote · hold · unsure — a proposal, never an act.
pub fn leaning_of(exp: &Value) -> &'static str {
    let arms = &exp["arms"];
    let cand = &arms["candidate"];
    let cur = &arms["current"];
    let g = &exp["reviewers"]["grader"]["verdict"];
    let risk = exp["reviewers"]["critic"]["risk"].as_str();
    let reds = exp["resiliency"]["reds"].as_i64().unwrap_or(0);
    if cand["passed"].is_null() {
        return "unsure";
    }
    if cand["failed"].as_i64().unwrap_or(0) > 0 || g["verdict"] == json!("current") || risk == Some("high") || reds > 0 {
        return "hold";
    }
    if !crate::chips::chip_holds(&exp["reviewers"]).is_empty() {
        return "hold"; // Phase 8 sp6: broken claims or a security concern hold the promotion
    }
    if !cur.is_null()
        && !crate::py::truthy(&cur["skipped"])
        && !cur["passed"].is_null()
        && cand["passed"].as_i64().unwrap_or(0) < cur["passed"].as_i64().unwrap_or(0)
    {
        return "hold";
    }
    if (g["verdict"].is_null() || g["verdict"] == json!("neither")) && risk.is_none() {
        return "unsure";
    }
    "promote"
}

/// `experiments.proposal_words`: THE PROPOSAL in plain words.
pub fn proposal_words(exp: &Value) -> String {
    let arms = &exp["arms"];
    let rv = &exp["reviewers"];
    let mut bits = vec![arm_words("candidate", &arms["candidate"], Some(exp))];
    if arms["current"].is_null() {
        bits.push("no current arm — the first version".into());
    } else {
        bits.push(arm_words("current", &arms["current"], Some(exp)));
    }
    let g = &rv["grader"];
    if crate::py::truthy(&g["verdict"]) {
        let v = &g["verdict"];
        let signed = if crate::py::truthy(&g["signed"]) { "signed" } else { "unsigned" };
        let q = |x: &Value| if x.is_null() { "?".to_string() } else { crate::py::python_str(x) };
        let mut gw = format!("the grader ({signed}) grades the candidate {}", q(&v["candidate"]));
        if crate::py::truthy(&v["current"]) {
            gw.push_str(&format!(" and the current {}", crate::py::python_str(&v["current"])));
        }
        gw.push_str(&format!(
            " and names {}",
            if v["verdict"].is_null() { "no side".to_string() } else { crate::py::python_str(&v["verdict"]) }
        ));
        bits.push(gw);
    } else {
        let m = if crate::py::truthy(&g["missing"]) { crate::py::python_str(&g["missing"]) } else { "no verdict yet".into() };
        bits.push(format!("the grader: {m}"));
    }
    let c = &rv["critic"];
    if crate::py::truthy(&c["risk"]) {
        let mut cw = format!("the critic reads the risk as {}", crate::py::python_str(&c["risk"]));
        if crate::py::truthy(&c["line"]) {
            cw.push_str(&format!(": {}", crate::py::python_str(&c["line"])));
        }
        bits.push(cw);
    } else {
        let m = if crate::py::truthy(&c["missing"]) { crate::py::python_str(&c["missing"]) } else { "no review yet".into() };
        bits.push(format!("the critic: {m}"));
    }
    bits.push(crate::chips::slot_words("identity", &rv["identity"]));
    bits.push(crate::chips::slot_words("security", &rv["security"]));
    let reds = exp["resiliency"]["reds"].as_i64().unwrap_or(0);
    bits.push(if reds == 0 {
        "resiliency: no watch turned red while the arms ran".into()
    } else {
        format!("resiliency: {reds} watch{} turned red while the arms ran", if reds != 1 { "es" } else { "" })
    });
    let lean = exp["leaning"].as_str().filter(|l| !l.is_empty()).map(str::to_string).unwrap_or_else(|| leaning_of(exp).to_string());
    let tail = match lean.as_str() {
        "promote" => "the evidence leans to promote",
        "hold" => "the evidence says hold — fix the draft and cut again, or promote on your own judgement",
        _ => "the evidence is unsure — read the arms yourself",
    };
    let agent = crate::py::python_str(&exp["agent"]);
    format!(
        "THE EXPERIMENT on {agent} proposes: {}. {tail}. The verdict is a proposal: say “promote {agent}” (or “promote {agent} to floor <name>”) — or “decline the {agent} experiment”.",
        bits.join(" · ")
    )
}

/// `experiments.promote_demand`: L2 for an agent, L3 (the code) for a resident; firmware never.
pub fn promote_demand(template_kind: Option<&str>) -> Value {
    match template_kind.unwrap_or("resident") {
        "agent" => json!({"ok": true, "level": "L2", "reason": null}),
        "resident" => json!({"ok": true, "level": "L3-code", "reason": null}),
        _ => json!({"ok": false, "level": null, "reason": "firmware is never promoted through the Experiment — it reaches prod as a release"}),
    }
}

/// `experiments.ladder_legal`: active → rested → decommissioned; restore from rested or decommissioned.
pub fn ladder_legal(from: &str, to: &str) -> bool {
    matches!((from, to), ("active", "rested") | ("rested", "decommissioned") | ("rested", "active") | ("decommissioned", "active"))
}

/// `experiments.ladder_refusal`: why a rung refuses, in words.
pub fn ladder_refusal(name: &str, from: Option<&str>, to: &str) -> String {
    let Some(from) = from else {
        return format!("{name} holds no seat this kernel wrote — only a promoted agent rests, retires or returns here");
    };
    match to {
        "rested" => format!("{name} is {from} — only an active body rests"),
        "decommissioned" => {
            if from == "active" {
                format!("{name} is {from} — rest it first; the grave takes a rested body")
            } else {
                format!("{name} is already {from}")
            }
        }
        _ => format!("{name} is active — nothing to restore"),
    }
}

pub fn rest_words(name: &str) -> String {
    format!("{name} is at rest — its life stopped at a safe boundary, its self kept, its record whole; say “restore {name}” for a new life or “decommission {name}” for the grave")
}

pub fn decom_words(name: &str, did: Option<&str>, removed: &[String], kept: &[String]) -> String {
    let r = if removed.is_empty() { "nothing was standing".to_string() } else { removed.join(", ") };
    let k = if kept.is_empty() { String::new() } else { format!("; kept: {}", kept.join(", ")) };
    format!(
        "{name} is decommissioned — removed: {r}{k}; its DID{}, its joins and its record stay; say “restore {name}” for a new life from the shelf",
        did.map(|d| format!(" {d}")).unwrap_or_default()
    )
}

pub fn restore_words(name: &str, at: &str) -> Result<String, String> {
    Ok(format!(
        "{name} returns — a new life from the shelf's standing version, on {}; never a revival",
        crate::levels::words(at)?
    ))
}

pub fn promote_words(agent: &str, version: i64, at: &str) -> Result<String, String> {
    Ok(format!("promoting {agent} to version {version} — its next life stands on {}", crate::levels::words(at)?))
}

/// `experiments.deploy_at`: the path asked for, else where the standing seat is, else the universe.
pub fn deploy_at(universe: &str, asked: Option<&str>, standing: Option<&str>) -> Result<String, String> {
    match asked.filter(|a| !a.trim().is_empty()) {
        Some(a) => crate::levels::absolute(universe, Some(a)),
        None => Ok(standing.filter(|s| !s.is_empty()).unwrap_or(universe).to_string()),
    }
}

pub fn prune_words(_name: &str, _kind: &str, last_wearer: &str) -> String {
    format!("pruned by the beat — worn by no body since {last_wearer} was decommissioned")
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn the_form_reads() {
        let g = grade_of("current: B — fine\n**candidate: A** — better\nverdict: candidate");
        assert_eq!(g, json!({"current": "B", "candidate": "A", "verdict": "candidate"}));
        assert_eq!(grade_of("current: none\ncandidate: C — meh\nverdict: neither"), json!({"current": null, "candidate": "C", "verdict": "neither"}));
        assert_eq!(risk_of("the change is small.\nrisk: low — one node"), Some("low".into()));
        assert_eq!(risk_of("no form here"), None);
    }

    #[test]
    fn the_ladder_and_the_leaning() {
        assert!(ladder_legal("active", "rested") && ladder_legal("rested", "decommissioned") && ladder_legal("decommissioned", "active"));
        assert!(!ladder_legal("active", "decommissioned") && !ladder_legal("active", "active"));
        let exp = json!({"agent": "bob", "current_version": 1,
            "arms": {"candidate": {"passed": 3, "failed": 0}, "current": {"passed": 2, "failed": 1}},
            "reviewers": {"grader": {"verdict": {"current": "B", "candidate": "A", "verdict": "candidate"}, "signed": true},
                          "critic": {"risk": "low", "line": "one node"}}, "resiliency": {"reds": 0}});
        assert_eq!(leaning_of(&exp), "promote");
        let w = proposal_words(&exp);
        assert!(w.starts_with("THE EXPERIMENT on bob proposes: the candidate passed 3 of 3 · the standing version 1 passed 2 of 3 · the grader (signed) grades the candidate A and the current B and names candidate · the critic reads the risk as low: one node · the identity chip: no verdict yet · the security chip: no review yet"));
        let mut exp2 = exp.clone();
        exp2["reviewers"]["security"] = json!({"security": "concern", "line": "a tool widened"});
        assert_eq!(leaning_of(&exp2), "hold");
        assert!(proposal_words(&exp2).contains("the security chip reads the candidate as concern: a tool widened"));
        assert!(w.contains("say “promote bob”"));
    }
}
