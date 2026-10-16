// PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch Phase 8 THE STUDIO sp8, THE BENCH (canon 0011 §2): the pure laws · 2026-10-13
//! THE BENCH — `orreth_spine.benches` ported, the pure half (the ground half is `benches_live`).
//! One effort, one place: a bench is a named effort under a person's seat — the agent's name is
//! the bench's name — holding the agent's whole story in ONE ROW of the ground: the step of its
//! making (the wizard's place), the wizard's state, the ask it holds at the interlock; and by
//! name its drafts (`spine_drafts.bench`), its experiments and its seat. THE WORD: `bench.rs`
//! beside this file is the dispatcher's waiting bench for asks (W91); that bench is the
//! kernel's, this one is the Workshop's — the two never meet in code.

use serde_json::{json, Value};

pub const BENCH_OPENED: &str = "orreth.bench.opened.v1";
pub const BENCH_CLOSED: &str = "orreth.bench.closed.v1";
pub const STEPS: [&str; 8] = ["name", "graph", "golden", "save", "cut", "card", "promote", "joined"];
pub const STATES: [&str; 2] = ["open", "closed"];
pub const WORK_TOOL: &str = "bench.work"; // THE STUDIO sp10 ONE WORD TO WORK (canon 0011 §5): the kernel's own held act — the chain
pub const WORK_LEVEL: &str = "L2";
pub const WORK_CLASS: &str = "consequential";
pub const WORK_ORDER: [&str; 3] = ["graph", "golden", "template"]; // the cuts, in order; the agent's own cut opens the Experiment

/// `benches.step_ok`: a step of the making.
pub fn step_ok(step: &str) -> bool {
    STEPS.contains(&step)
}

/// `benches.name_ok`: an agent's name — a short lowercase name, letters · digits · dashes ·
/// underscores, no dots (a craft's name may carry one; a bench is the agent).
pub fn name_ok(name: &str) -> bool {
    let b = name.as_bytes();
    (1..=64).contains(&b.len())
        && (b[0].is_ascii_lowercase() || b[0].is_ascii_digit())
        && b.iter().all(|c| c.is_ascii_lowercase() || c.is_ascii_digit() || *c == b'_' || *c == b'-')
}

/// the chain's plain words for a kind — "the graph x.v0" · "the golden set x" · "the agent x"
pub fn plain_words(name: &str, kind: &str) -> String {
    plain_of(name, kind)
}

fn plain_of(name: &str, kind: &str) -> String {
    match kind {
        "graph" => format!("the graph {name}.v0"),
        "golden" => format!("the golden set {name}"),
        _ => format!("the agent {name}"),
    }
}

/// `benches.plan_work`: the pure law of the chain (fixture `bench_work_plan`). Each of graph ·
/// golden · template is null (nothing of that kind under the bench or on the shelf) or
/// `{draft, same, version}` — whether a draft lies on the bench, whether its bytes equal the
/// shelf's, the shelf's standing version. Returns `{ok, cuts, lines, reason, text}`: the cuts in
/// order, a line per craft for the card, the one reason when the chain refuses, the held act's words.
pub fn plan_work(name: &str, graph: &Value, golden: &Value, template: &Value) -> Value {
    let mut lines: Vec<String> = Vec::new();
    let mut cuts: Vec<String> = Vec::new();
    let mut reason: Option<String> = None;
    for kind in WORK_ORDER {
        let c = match kind {
            "graph" => graph,
            "golden" => golden,
            _ => template,
        };
        let has = c["draft"].as_bool().unwrap_or(false);
        let same = c["same"].as_bool().unwrap_or(false);
        let ver = c["version"].as_i64();
        let what = plain_of(name, kind);
        if kind == "template" {
            if !has {
                reason.get_or_insert(format!("no template draft for {name} - SAVE first"));
                lines.push(format!("{what}: no draft"));
            } else if same {
                reason.get_or_insert(format!(
                    "the {name} template stands unchanged (version {}) - an experiment needs a change to judge: change what {name} is for, or its graph, then put it to work again",
                    ver.map(|v| v.to_string()).unwrap_or_else(|| "None".into())
                ));
                lines.push(format!("{what} stands unchanged (version {})", ver.map(|v| v.to_string()).unwrap_or_else(|| "None".into())));
            } else {
                cuts.push(kind.into());
                lines.push(format!("{what} as version {} -> the experiment", ver.unwrap_or(0) + 1));
            }
            continue;
        }
        if has && !same {
            cuts.push(kind.into());
            lines.push(format!("{what} as version {}", ver.unwrap_or(0) + 1));
        } else if has && same {
            lines.push(format!("{what} stands (version {}) - unchanged, skipped", ver.map(|v| v.to_string()).unwrap_or_else(|| "None".into())));
        } else if let Some(v) = ver.filter(|v| *v != 0) {
            lines.push(format!("{what} stands (version {v})"));
        } else {
            let need = if kind == "graph" { "SAVE the graph first" } else { "every engineered agent is born with one; SAVE its cases first" };
            reason.get_or_insert(format!("no {} - {need}", &what[4..]));
            lines.push(format!("{what}: none"));
        }
    }
    let ok = reason.is_none() && cuts.iter().any(|k| k == "template");
    let text = if ok { format!("putting {name} to work - {}", lines.join(" · ")) } else { String::new() };
    json!({"ok": ok, "cuts": cuts, "lines": lines, "reason": reason, "text": text})
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn the_steps_and_the_names() {
        assert!(STEPS.iter().all(|s| step_ok(s)));
        assert!(!step_ok("NAME") && !step_ok("") && !step_ok("experiment"));
        assert!(name_ok("jonathan") && name_ok("imp2") && name_ok("bob-2") && name_ok("a_b"));
        assert!(!name_ok("Bob") && !name_ok("bob.v0") && !name_ok("") && !name_ok("-bob") && !name_ok(&"x".repeat(65)));
    }
}
