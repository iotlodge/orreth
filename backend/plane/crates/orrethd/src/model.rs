//! The plane side of the Model Plane (0016 §6): the plane AUTHORIZES and METERS;
//! cognition executes. orrethd never holds provider keys or proxies LLM bytes —
//! budgets stop being a client-side honor system and become plane-enforced state:
//! present your lease, get a resolved model and a debit; reconcile actuals after.
//! Model-misses escalate to the parent gateway, like retrieval.

use serde_json::{json, Value};
use std::collections::BTreeMap;

pub const LIFECYCLE: [&str; 5] = ["candidate", "canaried", "available", "deprecated", "sunset"];
pub const CANARY_BEATS: i64 = 3;

/// every legal move, and no other — the state machine IS the governance card (0016 §3 · 0019)
fn legal(from: &str, to: &str) -> bool {
    match from {
        "candidate" => matches!(to, "canaried" | "sunset"),
        "canaried" => matches!(to, "available" | "deprecated" | "sunset"),
        "available" => matches!(to, "deprecated" | "sunset"),
        "deprecated" => matches!(to, "available" | "sunset"),
        _ => false, // sunset is terminal — never served, always remembered
    }
}

pub struct ModelPlane {
    /// class -> ordered candidates [{model, state}] — the legacy routing file; stalls win
    /// when they exist, so the two views can never disagree (0019: one owner for minds).
    pub registry: BTreeMap<String, Vec<Value>>,
    /// model id -> Stall (0019 §1) — this floor's stable: identity, deal pin, lifecycle.
    pub stalls: BTreeMap<String, Value>,
    /// lease subject (DID) -> remaining tokens; initialized from the token's constraints.budget.
    pub ledger: BTreeMap<String, i64>,
    /// the meter: every authorize/reconcile on the record — vigil's tap and the usage roll-up.
    pub meter_log: Vec<Value>,
    /// subject -> (calls, tokens, usd) folded from meter entries past the hot window
    /// (0022 §8 rotation). Totals + hot log = the same honest all-time meter (0019 §4);
    /// the raw cold entries live on in the meter_archive table, never vapor.
    pub meter_totals: BTreeMap<String, (i64, i64, f64)>,
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
        Self { registry: raw, stalls: BTreeMap::new(), ledger: BTreeMap::new(),
               meter_log: Vec::new(), meter_totals: BTreeMap::new() }
    }

    /// First serviceable candidate: available serves before canaried (a rookie on canary
    /// must never shadow a veteran); deprecated serves LOUDLY; sunset is never served —
    /// the retired-model outage is structurally impossible. Stalls are the routing truth
    /// for any class they populate; the legacy registry file only answers when no stall
    /// of that class exists. A pin narrows the field to one named mind — the canary's
    /// ping must exercise the stall it vouches for, never whatever the router prefers.
    pub fn resolve(&mut self, class: &str, pin: Option<&str>) -> Resolved {
        let stalled: Vec<Value> = self.stalls.values()
            .filter(|s| s["class"] == class).cloned().collect();
        let mut entries: Vec<Value> = if stalled.is_empty() {
            match self.registry.get(class) {
                Some(e) => e.clone(),
                None => return Resolved::Miss,
            }
        } else {
            stalled.iter().map(|s| json!({"model": s["id"], "state": s["state"]})).collect()
        };
        if let Some(p) = pin {
            entries.retain(|e| e["model"] == p);
        }
        for want in ["available", "canaried"] {
            for e in &entries {
                if e["state"] == want {
                    return Resolved::Model { model: e["model"].as_str().unwrap().to_string(),
                                             deprecated: false };
                }
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

    /// Dev-only lever over the LEGACY registry file. Stalls never move through here —
    /// their transitions are governed (staged request → human → wrangler → transition()).
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

    /// Saddling: the staged request made visible. Candidate only — approval is a human's
    /// move in the queue, attestation is the wrangler's after it (0019 §2).
    pub fn saddle(&mut self, req: &Value, floor: &str, now: &str) -> Result<Value, &'static str> {
        let id = req["id"].as_str().ok_or("a mind needs an id")?;
        if let Some(s) = self.stalls.get(id) {
            if s["state"] != "sunset" {
                return Err("already stands in this stable");
            }
        }
        let manifest = req.get("manifest").cloned().unwrap_or_else(|| json!({}));
        let stall = json!({
            "id": id,
            "provider": req["provider"].as_str().unwrap_or(""),
            "route": req["route"].as_str().unwrap_or("litellm-direct"),
            "did": req["did"].as_str().unwrap_or(""),
            "class": req["class"].as_str().unwrap_or("medium"),
            "manifest_hash": orreth_crypto::content_hash(&manifest),
            "manifest": manifest,
            "state": "candidate", "floor": floor,
            "expires_at": req.get("expires_at").cloned().unwrap_or(Value::Null),
            "saddled_at": now, "last_synced": Value::Null, "canary_beats": 0, "calls": 0,
        });
        self.stalls.insert(id.to_string(), stall.clone());
        Ok(stall)
    }

    /// The guarded move. Ops carry their own deal rules:
    ///   attest    — candidate → canaried, pin the deal the wrangler SAW
    ///   sync      — same bytes: freshness · changed bytes: → deprecated, the drift held
    ///               at the gate (the rug-pull door, applied to pricing/context)
    ///   reapprove — deprecated → available, adopting the proposed deal (a human's call)
    ///   eol       — → deprecated, the expiry announced (loud, still resolvable)
    ///   retire    — → sunset (terminal; the staged decom or the expiry arriving)
    pub fn transition(&mut self, req: &Value, now: &str) -> Result<Value, &'static str> {
        let id = req["id"].as_str().ok_or("which mind?")?.to_string();
        let stall = self.stalls.get_mut(&id).ok_or("no such stall in this stable")?;
        let from = stall["state"].as_str().unwrap_or("").to_string();
        let op = req["op"].as_str().ok_or("which move?")?;
        let (to, extra) = match op {
            "attest" => {
                let manifest = req.get("manifest").cloned().unwrap_or_else(|| json!({}));
                stall["manifest_hash"] = json!(orreth_crypto::content_hash(&manifest));
                stall["manifest"] = manifest;
                if let Some(e) = req.get("expires_at") { stall["expires_at"] = e.clone(); }
                stall["canary_beats"] = json!(0);
                ("canaried", json!({}))
            }
            "sync" => {
                let manifest = req.get("manifest").cloned().unwrap_or_else(|| json!({}));
                let seen = orreth_crypto::content_hash(&manifest);
                stall["last_synced"] = json!(now);
                if let Some(e) = req.get("expires_at") {
                    if !e.is_null() { stall["expires_at"] = e.clone(); }
                }
                if seen == stall["manifest_hash"].as_str().unwrap_or("") {
                    return Ok(stall.clone()); // freshness, not a move
                }
                // the deal moved under the pin — held at the gate until a human re-approves
                stall["proposed_manifest"] = manifest;
                stall["proposed_hash"] = json!(seen);
                if !matches!(from.as_str(), "canaried" | "available") {
                    return Ok(stall.clone()); // drift noted; nothing to demote
                }
                ("deprecated", json!({"pinned": stall["manifest_hash"], "seen": seen}))
            }
            "reapprove" => {
                if let Some(m) = stall.as_object_mut().unwrap().remove("proposed_manifest") {
                    stall["manifest"] = m;
                }
                if let Some(h) = stall.as_object_mut().unwrap().remove("proposed_hash") {
                    stall["manifest_hash"] = h;
                }
                ("available", json!({}))
            }
            "eol" => {
                if let Some(e) = req.get("expires_at") { stall["expires_at"] = e.clone(); }
                ("deprecated", json!({"expires_at": stall["expires_at"]}))
            }
            "retire" => ("sunset",
                         json!({"reason": req["reason"].as_str().unwrap_or("retired")})),
            _ => return Err("which move?"),
        };
        if !legal(&from, to) {
            return Err("not a move this stable knows");
        }
        stall["state"] = json!(to);
        let mut out = stall.clone();
        out["transition"] = json!({"from": from, "to": to, "op": op, "at": now, "extra": extra});
        Ok(out)
    }

    /// Canary: verified syncs (and metered ping calls) earn service — the wrangler
    /// reports, the plane promotes (0019 §2, mirroring the farm's probation beats).
    pub fn canary(&mut self, id: &str, now: &str) -> Result<Value, &'static str> {
        let stall = self.stalls.get_mut(id).ok_or("no such stall in this stable")?;
        if stall["state"] != "canaried" {
            return Err("only canaried minds beat");
        }
        stall["last_synced"] = json!(now);
        let beats = stall["canary_beats"].as_i64().unwrap_or(0) + 1;
        stall["canary_beats"] = json!(beats);
        if beats >= CANARY_BEATS {
            stall["state"] = json!("available"); // earned, not granted
            let mut out = stall.clone();
            out["transition"] = json!({"from": "canaried", "to": "available",
                                       "op": "canary", "at": now});
            return Ok(out);
        }
        Ok(stall.clone())
    }

    /// The roster this floor beats upward — one world, one picture.
    pub fn roster(&self) -> Vec<Value> {
        self.stalls.values().cloned().collect()
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

    /// The Cortex-style usage view: totals per subject — the folded cold window (0022 §8
    /// rotation) seeds the counts, the hot log rides on top. Same all-time truth.
    pub fn usage(&self) -> Value {
        let mut per: BTreeMap<String, (i64, f64, i64)> = BTreeMap::new();
        for (s, (calls, tokens, usd)) in &self.meter_totals {
            per.insert(s.clone(), (*tokens, *usd, *calls));
        }
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
