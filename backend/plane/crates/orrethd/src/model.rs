//! The plane side of the Model Plane (0016 §6): the plane AUTHORIZES and METERS;
//! cognition executes. orrethd never holds provider keys or proxies LLM bytes —
//! budgets stop being a client-side honor system and become plane-enforced state:
//! present your lease, get a resolved model and a debit; reconcile actuals after.
//! Model-misses escalate to the parent gateway, like retrieval.

use serde_json::{json, Value};
use std::collections::BTreeMap;

pub const LIFECYCLE: [&str; 5] = ["candidate", "canaried", "available", "deprecated", "sunset"];

pub struct ModelPlane {
    /// class -> ordered candidates [{model, state}] — the trust lifecycle's third application.
    pub registry: BTreeMap<String, Vec<Value>>,
    /// lease subject (DID) -> remaining tokens; initialized from the token's constraints.budget.
    pub ledger: BTreeMap<String, i64>,
    /// the meter: every authorize/reconcile on the record — vigil's tap and the usage roll-up.
    pub meter_log: Vec<Value>,
}

pub enum Resolved {
    Model { model: String, deprecated: bool },
    /// no living model at this tier — the miss climbs (0016 §1)
    Miss,
}

impl ModelPlane {
    pub fn from_file(path: &str) -> Self {
        let raw: BTreeMap<String, Vec<Value>> = std::fs::read_to_string(path)
            .ok()
            .and_then(|s| serde_json::from_str(&s).ok())
            .unwrap_or_default();
        Self { registry: raw, ledger: BTreeMap::new(), meter_log: Vec::new() }
    }

    /// First serviceable candidate: available/canaried serve; deprecated serves LOUDLY;
    /// sunset is never served — the retired-model outage is structurally impossible.
    pub fn resolve(&mut self, class: &str) -> Resolved {
        let entries = match self.registry.get(class) {
            Some(e) => e.clone(),
            None => return Resolved::Miss,
        };
        for e in &entries {
            if matches!(e["state"].as_str(), Some("available") | Some("canaried")) {
                return Resolved::Model { model: e["model"].as_str().unwrap().to_string(),
                                         deprecated: false };
            }
        }
        for e in &entries {
            if e["state"] == "deprecated" {
                self.meter_log.push(json!({"lifecycle_warning": e["model"], "class": class}));
                return Resolved::Model { model: e["model"].as_str().unwrap().to_string(),
                                         deprecated: true };
            }
        }
        Resolved::Miss
    }

    pub fn set_state(&mut self, model: &str, state: &str) -> bool {
        if !LIFECYCLE.contains(&state) {
            return false;
        }
        let mut hit = false;
        for entries in self.registry.values_mut() {
            for e in entries.iter_mut() {
                if e["model"] == model {
                    e["state"] = json!(state);
                    hit = true;
                }
            }
        }
        hit
    }

    /// Debit the lease's budget (initializing from the verified token on first sight).
    /// Err(()) = budget refused — the caller sees the uniform shape.
    pub fn debit(&mut self, subject: &str, token_budget: i64, amount: i64) -> Result<i64, ()> {
        let remaining = self.ledger.entry(subject.to_string()).or_insert(token_budget);
        if amount > *remaining {
            return Err(());
        }
        *remaining -= amount;
        Ok(*remaining)
    }

    /// Reconcile actuals after the call: refund over-estimates, debit under-estimates
    /// (an under-estimate may drive the ledger negative — visible, never hidden).
    pub fn reconcile(&mut self, subject: &str, estimated: i64, actual: i64) -> i64 {
        let remaining = self.ledger.entry(subject.to_string()).or_insert(0);
        *remaining += estimated - actual;
        *remaining
    }

    /// The Cortex-style usage view: totals per subject from the meter log.
    pub fn usage(&self) -> Value {
        let mut per: BTreeMap<String, (i64, f64, i64)> = BTreeMap::new();
        for m in &self.meter_log {
            if let Some(s) = m.get("subject").and_then(Value::as_str) {
                let e = per.entry(s.to_string()).or_insert((0, 0.0, 0));
                e.0 += m["tokens"].as_i64().unwrap_or(0);
                e.1 += m["usd"].as_f64().unwrap_or(0.0);
                e.2 += 1;
            }
        }
        json!(per
            .into_iter()
            .map(|(s, (t, u, c))| json!({"subject": s, "tokens": t,
                                          "usd": (u * 1e6).round() / 1e6, "calls": c,
                                          "remaining": self.ledger.get(&s)}))
            .collect::<Vec<_>>())
    }
}
