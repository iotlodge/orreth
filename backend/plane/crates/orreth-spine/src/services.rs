// PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp3, the ask road · 2026-09-22
//! `orreth.services/1` — the pure half of `orreth_spine.services` (P6.5 sp1):
//! the ONE ladder's legality (`ladder_step`: from a state, may a verb step,
//! and to where — the reason in a newcomer's words) and the manifest pin
//! (sha256 over the canonical bytes, 0000 §3). Measured by the conformance
//! kinds `ladder_step` · `manifest_pin` (`spine/conformance/services-v0.json`).

use crate::hash::content_hash;
use serde_json::{json, Value};

/// The kinds a service can be.
pub const KINDS: [&str; 5] = ["tool", "mcp", "store", "source", "mind"];
/// The ladder's rungs.
pub const STATES: [&str; 5] = ["registered", "versioned", "healthy", "unhealthy", "retired"];
/// The steps, in the order the refusal names them.
pub const VERBS: [&str; 6] = [
    "register",
    "version",
    "healthy",
    "unhealthy",
    "retire",
    "restore",
];

/// The one legality: from `state` (`None` = not registered) may `verb` step,
/// and to where? `{ok, to, reason}` — the reason names the step and the state
/// it was refused from, in words a newcomer reads.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Step {
    pub ok: bool,
    pub to: Option<&'static str>,
    pub reason: Option<String>,
}

impl Step {
    fn to(rung: &'static str) -> Step {
        Step {
            ok: true,
            to: Some(rung),
            reason: None,
        }
    }
    fn refused(reason: String) -> Step {
        Step {
            ok: false,
            to: None,
            reason: Some(reason),
        }
    }
    /// The Python dict, as the door and the fixture spell it.
    pub fn to_value(&self) -> Value {
        json!({"ok": self.ok, "to": self.to, "reason": self.reason})
    }
}

/// `services.ladder_step`, word for word.
pub fn ladder_step(state: Option<&str>, verb: &str) -> Step {
    if !VERBS.contains(&verb) {
        return Step::refused(format!(
            "no step named '{verb}' on the ladder — the steps: {}",
            VERBS.join(", ")
        ));
    }
    let Some(state) = state else {
        if verb == "register" {
            return Step::to("registered");
        }
        return Step::refused(format!(
            "not registered — {verb} is not a step from there; register it first"
        ));
    };
    if !STATES.contains(&state) {
        return Step::refused(format!(
            "in an unknown state '{state}' — the rungs: {}",
            STATES.join(", ")
        ));
    }
    match verb {
        "register" => {
            if state == "retired" {
                Step::refused(
                    "retired — a retired service is restored, never registered twice".into(),
                )
            } else {
                Step::refused(
                    "already registered — version it when its manifest changes, never register \
                     it twice"
                        .into(),
                )
            }
        }
        "restore" => {
            if state == "retired" {
                Step::to("registered")
            } else {
                Step::refused(format!("{state}, not retired — nothing to restore"))
            }
        }
        "retire" => {
            if state == "retired" {
                Step::refused("already retired — nothing to retire".into())
            } else {
                Step::to("retired")
            }
        }
        "version" | "healthy" | "unhealthy" => {
            if state == "retired" {
                Step::refused(format!(
                    "retired — the ladder runs no {verb} on a retired service; restore it first"
                ))
            } else {
                Step::to(match verb {
                    "version" => "versioned",
                    "healthy" => "healthy",
                    _ => "unhealthy",
                })
            }
        }
        _ => unreachable!("every verb is matched above"),
    }
}

/// The manifest pin: sha256 over the canonical bytes.
pub fn pin(manifest: &Value) -> String {
    content_hash(manifest)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn the_ladder_steps_and_refuses_in_words() {
        assert_eq!(ladder_step(None, "register").to, Some("registered"));
        assert_eq!(ladder_step(Some("healthy"), "retire").to, Some("retired"));
        assert_eq!(
            ladder_step(Some("retired"), "restore").to,
            Some("registered")
        );
        let r = ladder_step(Some("registered"), "fly");
        assert!(r.reason.unwrap().starts_with("no step named 'fly'"));
        let r = ladder_step(None, "retire");
        assert_eq!(
            r.reason.as_deref(),
            Some("not registered — retire is not a step from there; register it first")
        );
        assert_eq!(
            ladder_step(Some("healthy"), "restore").reason.as_deref(),
            Some("healthy, not retired — nothing to restore")
        );
    }
}
