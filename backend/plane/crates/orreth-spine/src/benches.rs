// PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch Phase 8 THE STUDIO sp8, THE BENCH (canon 0011 §2): the pure laws · 2026-10-13
//! THE BENCH — `orreth_spine.benches` ported, the pure half (the ground half is `benches_live`).
//! One effort, one place: a bench is a named effort under a person's seat — the agent's name is
//! the bench's name — holding the agent's whole story in ONE ROW of the ground: the step of its
//! making (the wizard's place), the wizard's state, the ask it holds at the interlock; and by
//! name its drafts (`spine_drafts.bench`), its experiments and its seat. THE WORD: `bench.rs`
//! beside this file is the dispatcher's waiting bench for asks (W91); that bench is the
//! kernel's, this one is the Workshop's — the two never meet in code.

pub const BENCH_OPENED: &str = "orreth.bench.opened.v1";
pub const BENCH_CLOSED: &str = "orreth.bench.closed.v1";
pub const STEPS: [&str; 8] = ["name", "graph", "golden", "save", "cut", "card", "promote", "joined"];
pub const STATES: [&str; 2] = ["open", "closed"];

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
