// PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp1, the bytes · 2026-09-22
// Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp7 walk #15, W54: the default cell means wherever this ground stands · 2026-09-25
// Amended: Claude Fable 5.1 (claude-fable-5-1) — THE GROUND CONNECTIONS CURE (JB's word 2026-10-08): the ground's CONNECTIONS budget — `seats_budget` · `seat_honor` — the pure half of the seat rule · 2026-10-08
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
// the ground connections cure (2026-10-08) — `placement.CEILING_DEFAULT` · `RESERVE_DEFAULT` · `LINES_PER_BODY`
/// Postgres's stock `max_connections` — what a ground answers before anyone tunes it.
pub const CEILING_DEFAULT: i64 = 100;
/// The kernel's own lines: a door pool of 16 · the rails' loops · Postgres's 3 for its superuser · a person's tools.
pub const RESERVE_DEFAULT: i64 = 30;
/// A SERVING body holds its serve line and its working memory's line; an idle body holds none.
pub const LINES_PER_BODY: i64 = 2;
pub const CONNECTIONS_DIAL: &str = "SPINE_GROUND_CONNECTIONS";
pub const RESERVE_DIAL: &str = "SPINE_GROUND_RESERVE";

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

/// The ground's CONNECTIONS budget as it declares it (the cure, 2026-10-08) — `placement.connections_declared`.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Connections {
    pub ceiling: i64,
    pub reserve: i64,
    pub per_body: i64,
    pub seats: i64,
}

impl Connections {
    /// The budget from a ceiling and a reserve (the seats follow).
    pub fn new(ceiling: i64, reserve: i64) -> Connections {
        Connections {
            ceiling,
            reserve,
            per_body: LINES_PER_BODY,
            seats: seats_budget(ceiling, reserve, LINES_PER_BODY),
        }
    }

    /// The budget the dials and the ground's own ceiling declare: the LESSER of
    /// `SPINE_GROUND_CONNECTIONS` and `max_connections` when both are said (a dial may narrow
    /// the ground, never widen it), else 100; the reserve `SPINE_GROUND_RESERVE`, else 30.
    pub fn declared(max_connections: Option<i64>) -> Connections {
        let dial = |name: &str| {
            std::env::var(name)
                .ok()
                .and_then(|v| v.trim().parse::<i64>().ok())
                .filter(|n| *n > 0)
        };
        let said: Vec<i64> = [dial(CONNECTIONS_DIAL), max_connections.filter(|n| *n > 0)]
            .into_iter()
            .flatten()
            .collect();
        let ceiling = said.into_iter().min().unwrap_or(CEILING_DEFAULT);
        Connections::new(ceiling, dial(RESERVE_DIAL).unwrap_or(RESERVE_DEFAULT))
    }

    pub fn to_value(&self) -> Value {
        json!({"ceiling": self.ceiling, "reserve": self.reserve, "per_body": self.per_body, "seats": self.seats})
    }

    pub fn from_value(v: &Value) -> Result<Connections, PlacementError> {
        let int = |field: &str| {
            get(v, field)
                .as_i64()
                .ok_or_else(|| PlacementError::Shape(format!("{field} is a number")))
        };
        Ok(Connections {
            ceiling: int("ceiling")?,
            reserve: int("reserve")?,
            per_body: int("per_body")?,
            seats: int("seats")?,
        })
    }
}

/// THE SEATS (`placement.seats_budget`): how many bodies may stand here so that every one of
/// them could serve at once — the ceiling less the kernel's reserve, in lines per serving body;
/// never below zero.
pub fn seats_budget(ceiling: i64, reserve: i64, per_body: i64) -> i64 {
    ((ceiling - reserve) / per_body.max(1)).max(0)
}

/// The seat rule (`placement.seat_honor`): a body may be seated iff fewer bodies than the
/// budget stand alive here now; the one reason in a newcomer's words.
pub fn seat_honor(c: &Connections, seated: i64) -> (bool, Vec<String>) {
    if seated < c.seats {
        return (true, Vec::new());
    }
    (
        false,
        vec![format!(
            "the ground seats {} bod{} at once — its ceiling of {} connections less the kernel's {}, {} lines per \
             serving body — and {} {} seated already",
            c.seats,
            if c.seats == 1 { "y" } else { "ies" },
            c.ceiling,
            c.reserve,
            c.per_body,
            seated,
            if seated == 1 { "is" } else { "are" }
        )],
    )
}

/// The rule: honored iff the cell is this ground's, the metal is here (or
/// `any`), and every named secret is reachable. Every unmet clause is named,
/// cell then metal then each secret — the owner learns why.
pub fn honor(prof: &Profile, ground: &Ground) -> (bool, Vec<String>) {
    let mut reasons = Vec::new();
    // W54 (walk #15): the default cell, `local`, means "wherever this ground stands"
    if prof.cell != ground.cell && prof.cell != DEFAULT_CELL {
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
    fn the_seats_follow_the_ceiling() {
        assert_eq!(seats_budget(100, 30, 2), 35);
        assert_eq!(seats_budget(20, 30, 2), 0);
        let c = Connections::new(32, 30);
        assert_eq!(c.seats, 1);
        assert_eq!(seat_honor(&c, 0), (true, vec![]));
        assert_eq!(
            seat_honor(&c, 1),
            (false, vec!["the ground seats 1 body at once — its ceiling of 32 connections less the kernel's 30, 2 lines per serving body — and 1 is seated already".to_string()])
        );
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
