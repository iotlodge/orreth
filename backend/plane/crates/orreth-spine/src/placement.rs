// PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp1, the bytes · 2026-09-22
//! `orreth.placement/1` — the pure half of `orreth_spine.placement`: a
//! template's placement with the defaults applied, the honor rule (honored
//! iff the cell is this ground's, the metal is here or `any`, and every named
//! secret is reachable — every unmet clause named in plain words), and the
//! card's one line. The ground declaring itself (dials, the environment's
//! secret names) and the refusal as a fact are sp3's.

use crate::py::{get, python_str, truthy};
use serde_json::{json, Value};
use std::fmt;

pub const METALS: [&str; 3] = ["any", "cpu", "gpu"];
pub const DEFAULT_CELL: &str = "local";
pub const DEFAULT_METAL: &str = "any";

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum PlacementError {
    /// `a placement is {cell, affinity, secrets_with, metal}`.
    NotAPlacement,
    /// `metal is one of any, cpu, gpu — not '…'`.
    UnknownMetal(String),
    /// A record that is not the shape the law reads.
    Shape(String),
}

impl fmt::Display for PlacementError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            PlacementError::NotAPlacement => {
                write!(f, "a placement is {{cell, affinity, secrets_with, metal}}")
            }
            PlacementError::UnknownMetal(m) => {
                write!(f, "metal is one of {} — not '{m}'", METALS.join(", "))
            }
            PlacementError::Shape(why) => write!(f, "{why}"),
        }
    }
}

impl std::error::Error for PlacementError {}

/// The placement profile — the wire shape; the fixture's law.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Profile {
    pub cell: String,
    pub affinity: Vec<String>,
    pub secrets_with: Vec<String>,
    pub metal: String,
}

/// What a ground declares of itself: its cell, its metal, the secret NAMES it can reach.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Ground {
    pub cell: String,
    pub metal: String,
    pub secrets: Vec<String>,
}

fn strings(v: &Value, field: &str) -> Result<Vec<String>, PlacementError> {
    if !truthy(v) {
        return Ok(Vec::new());
    }
    v.as_array()
        .map(|a| a.iter().map(python_str).collect())
        .ok_or_else(|| PlacementError::Shape(format!("{field} is a list of names")))
}

fn string(v: &Value, field: &str) -> Result<String, PlacementError> {
    v.as_str()
        .map(str::to_string)
        .ok_or_else(|| PlacementError::Shape(format!("{field} is a string")))
}

impl Profile {
    /// The profile as its record (canonical key order comes from the bytes, not here).
    pub fn to_value(&self) -> Value {
        json!({
            "cell": self.cell, "affinity": self.affinity,
            "secrets_with": self.secrets_with, "metal": self.metal,
        })
    }

    /// A complete profile from its record — every clause present.
    pub fn from_value(v: &Value) -> Result<Profile, PlacementError> {
        Ok(Profile {
            cell: string(get(v, "cell"), "cell")?,
            affinity: strings(get(v, "affinity"), "affinity")?,
            secrets_with: strings(get(v, "secrets_with"), "secrets_with")?,
            metal: string(get(v, "metal"), "metal")?,
        })
    }
}

impl Ground {
    pub fn from_value(v: &Value) -> Result<Ground, PlacementError> {
        Ok(Ground {
            cell: string(get(v, "cell"), "cell")?,
            metal: string(get(v, "metal"), "metal")?,
            secrets: strings(get(v, "secrets"), "secrets")?,
        })
    }
}

/// The template's placement with the defaults applied — every list a list of
/// strings. A template that declares no placement wears the default and is
/// born exactly as before.
pub fn profile(template: &Value) -> Result<Profile, PlacementError> {
    if !template.is_object() {
        return Err(PlacementError::Shape("a template is a record".into()));
    }
    let raw = get(template, "placement");
    let raw = if truthy(raw) {
        raw
    } else {
        &Value::Object(Default::default())
    };
    if !raw.is_object() {
        return Err(PlacementError::NotAPlacement);
    }
    let or_default = |field: &str, default: &str| {
        let v = get(raw, field);
        if truthy(v) {
            python_str(v)
        } else {
            default.to_string()
        }
    };
    let p = Profile {
        cell: or_default("cell", DEFAULT_CELL),
        affinity: strings(get(raw, "affinity"), "affinity")?,
        secrets_with: strings(get(raw, "secrets_with"), "secrets_with")?,
        metal: or_default("metal", DEFAULT_METAL),
    };
    if !METALS.contains(&p.metal.as_str()) {
        return Err(PlacementError::UnknownMetal(p.metal));
    }
    Ok(p)
}

/// The rule: honored iff the cell is this ground's, the metal is here (or
/// `any`), and every named secret is reachable. Every unmet clause is named,
/// cell then metal then each secret — the owner learns why.
pub fn honor(prof: &Profile, ground: &Ground) -> (bool, Vec<String>) {
    let mut reasons = Vec::new();
    if prof.cell != ground.cell {
        reasons.push(format!(
            "cell '{}' is not this ground ('{}')",
            prof.cell, ground.cell
        ));
    }
    if prof.metal != "any" && prof.metal != ground.metal {
        reasons.push(format!(
            "metal {} is not here ({})",
            prof.metal, ground.metal
        ));
    }
    for s in &prof.secrets_with {
        if !ground.secrets.contains(s) {
            reasons.push(format!("secret {s} is not reachable here"));
        }
    }
    (reasons.is_empty(), reasons)
}

/// The card's one line: where the body stands and why — or `refused: …`.
pub fn why_here(prof: &Profile, ground: &Ground) -> String {
    let (ok, reasons) = honor(prof, ground);
    if !ok {
        return format!("refused: {}", reasons.join("; "));
    }
    let n = prof.secrets_with.len();
    let reached = prof
        .secrets_with
        .iter()
        .filter(|s| ground.secrets.contains(s))
        .count();
    let mut line = format!("stands on {} · {}", ground.cell, ground.metal);
    if n > 0 {
        line.push_str(&format!(" · reaches {reached} of {n} secrets"));
    }
    if !prof.affinity.is_empty() {
        line.push_str(&format!(
            " · beside {} (advisory)",
            prof.affinity.join(", ")
        ));
    }
    line
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn defaults_fill_and_strangers_refuse() {
        let p = profile(&json!({"name": "echo"})).unwrap();
        assert_eq!(
            p,
            Profile {
                cell: "local".into(),
                affinity: vec![],
                secrets_with: vec![],
                metal: "any".into()
            }
        );
        assert_eq!(profile(&json!({"placement": null})).unwrap(), p);
        assert_eq!(
            profile(&json!({"placement": {"metal": "tpu"}})).unwrap_err(),
            PlacementError::UnknownMetal("tpu".into())
        );
        assert_eq!(
            profile(&json!({"placement": "gpu"})).unwrap_err(),
            PlacementError::NotAPlacement
        );
        assert!(profile(&json!({"placement": {"affinity": "echo"}})).is_err());
    }

    #[test]
    fn the_card_counts_what_it_reaches() {
        let p = Profile {
            cell: "local".into(),
            affinity: vec!["echo".into()],
            secrets_with: vec!["A".into(), "B".into()],
            metal: "any".into(),
        };
        let g = Ground {
            cell: "local".into(),
            metal: "cpu".into(),
            secrets: vec!["A".into()],
        };
        assert_eq!(
            honor(&p, &g),
            (false, vec!["secret B is not reachable here".to_string()])
        );
        assert_eq!(why_here(&p, &g), "refused: secret B is not reachable here");
        let g = Ground {
            secrets: vec!["A".into(), "B".into()],
            ..g
        };
        assert_eq!(
            why_here(&p, &g),
            "stands on local · cpu · reaches 2 of 2 secrets · beside echo (advisory)"
        );
    }
}
