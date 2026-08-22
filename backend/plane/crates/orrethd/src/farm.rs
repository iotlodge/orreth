// PROVENANCE: Fable 5 (claude-fable-5) — 0018, the Tool Farm · 2026-07-05
//! The plane side of the Tool Farm (0018): registry, lifecycle legality, and the meter.
//! The keeper (cognition) decides WHEN a service moves; this module refuses illegal
//! WHATs — and the rug-pull check lives HERE: a rejoin's manifest is compared against
//! the pinned hash by the plane, never trusted from the keeper's summary of it.
//! The plane verifies and meters; it never signs — worldline records are the keeper's
//! (0005: nothing self-attests, and the plane attests nothing either).

use serde_json::{json, Value};
use std::collections::BTreeMap;

pub const PROBATION_BEATS: i64 = 3;

/// every legal move, and no other — the state machine IS the governance card (0018 §2)
fn legal(from: &str, to: &str) -> bool {
    match from {
        "proposed" => matches!(to, "probation" | "decommissioned"),
        "probation" => matches!(to, "serving" | "dropped" | "quarantined" | "resting" | "decommissioned"),
        "serving" => matches!(to, "dropped" | "quarantined" | "resting" | "decommissioned"),
        "dropped" => matches!(to, "serving" | "quarantined" | "decommissioned"),
        // resting (0059 §2.4): the HUMAN'S word, lease kept — distinct from
        // dropped (the wire's silence). Resume re-earns through probation.
        "resting" => matches!(to, "probation" | "decommissioned"),
        "quarantined" => matches!(to, "probation" | "decommissioned"),
        _ => false, // decommissioned is terminal — history remains
    }
}

pub struct Farm {
    /// name -> ServiceRecord (0018 §1) — this floor's toolshed
    pub services: BTreeMap<String, Value>,
    /// volume and shape, never payloads (0016 §6) — the roll-up's raw material
    pub meter_log: Vec<Value>,
}

impl Farm {
    pub fn new() -> Self {
        Self { services: BTreeMap::new(), meter_log: Vec::new() }
    }

    /// Planting: the staged request made visible. Proposed only — approval is a
    /// human's move in the queue, attestation is the keeper's after it.
    pub fn plant(&mut self, req: &Value, floor: &str, now: &str) -> Result<Value, &'static str> {
        let name = req["name"].as_str().ok_or("a service needs a name")?;
        if let Some(s) = self.services.get(name) {
            if s["state"] != "decommissioned" {
                return Err("already lives on this farm");
            }
        }
        let manifest = req.get("manifest").cloned().unwrap_or_else(|| json!([]));
        let svc = json!({
            "name": name,
            "did": req["did"].as_str().unwrap_or(""),
            "kind": req["kind"].as_str().unwrap_or("http"),
            "endpoint": req["endpoint"].as_str().unwrap_or(""),
            "transport": req["transport"].as_str().unwrap_or("rest"),
            "manifest_hash": orreth_crypto::content_hash(&manifest),
            "manifest": manifest,
            // 0059: a tool's SOURCE is a first-class fact (human · seed:<eye>
            // · capability:<key>), and a standing-spend guard rides the record
            "source": req["source"].as_str().unwrap_or("human"),
            "spend_guard": req["spend_guard"].as_str().unwrap_or(""),
            "state": "proposed", "floor": floor,
            "planted_at": now, "last_seen": Value::Null, "beats": 0, "calls": 0,
        });
        self.services.insert(name.to_string(), svc.clone());
        Ok(svc)
    }

    /// The guarded move. Ops carry their own manifest rules:
    ///   attest    — proposed → probation, pin what the keeper SAW
    ///   rejoin    — dropped → serving on the SAME hash, quarantined on any other
    ///   reapprove — quarantined → probation, adopting the proposed hash (a human's call)
    ///   expire    — → dropped (the lease aged out)
    ///   decom     — → decommissioned (terminal; may carry discredit for 0014 §4)
    pub fn transition(&mut self, req: &Value, now: &str) -> Result<Value, &'static str> {
        let name = req["name"].as_str().ok_or("which service?")?.to_string();
        let svc = self.services.get_mut(&name).ok_or("no such service on this farm")?;
        let from = svc["state"].as_str().unwrap_or("").to_string();
        let op = req["op"].as_str().ok_or("which move?")?;
        let (to, extra) = match op {
            "attest" => {
                let manifest = req.get("manifest").cloned().unwrap_or_else(|| json!([]));
                svc["manifest_hash"] = json!(orreth_crypto::content_hash(&manifest));
                svc["manifest"] = manifest;
                svc["beats"] = json!(0);
                ("probation", json!({}))
            }
            "rejoin" => {
                let manifest = req.get("manifest").cloned().unwrap_or_else(|| json!([]));
                let seen = orreth_crypto::content_hash(&manifest);
                if seen == svc["manifest_hash"].as_str().unwrap_or("") {
                    svc["beats"] = json!(0);
                    ("serving", json!({}))
                } else {
                    // the rug-pull door (CVE-2025-54136): a changed manifest is a NEW
                    // claim — held at the gate until a human re-opens it
                    svc["proposed_manifest"] = manifest;
                    svc["proposed_hash"] = json!(seen);
                    ("quarantined", json!({"pinned": svc["manifest_hash"], "seen": seen}))
                }
            }
            "reapprove" => {
                if let Some(m) = svc.as_object_mut().unwrap().remove("proposed_manifest") {
                    svc["manifest"] = m;
                }
                if let Some(h) = svc.as_object_mut().unwrap().remove("proposed_hash") {
                    svc["manifest_hash"] = h;
                }
                svc["beats"] = json!(0);
                ("probation", json!({}))
            }
            "expire" => {
                svc["beats"] = json!(0);
                ("dropped", json!({"reason": req["reason"].as_str().unwrap_or("missed heartbeats")}))
            }
            "rest" => ("resting",
                       json!({"reason": req["reason"].as_str().unwrap_or("the human's word")})),
            "resume" => {
                svc["beats"] = json!(0);
                ("probation", json!({}))    // service is re-earned, never granted
            }
            "decom" => ("decommissioned",
                        json!({"reason": req["reason"].as_str().unwrap_or(""),
                               "discredit": req["discredit"].as_bool().unwrap_or(false)})),
            _ => return Err("which move?"),
        };
        if !legal(&from, to) {
            return Err("not a move this farm knows");
        }
        svc["state"] = json!(to);
        let mut out = svc.clone();
        out["transition"] = json!({"from": from, "to": to, "op": op, "at": now, "extra": extra});
        Ok(out)
    }

    /// The lease: beats earn probation's exit; the keeper reports, the plane promotes.
    pub fn beat(&mut self, name: &str, now: &str) -> Result<Value, &'static str> {
        let svc = self.services.get_mut(name).ok_or("no such service on this farm")?;
        let state = svc["state"].as_str().unwrap_or("").to_string();
        if !matches!(state.as_str(), "probation" | "serving") {
            return Err("only probation and serving services beat");
        }
        svc["last_seen"] = json!(now);
        let beats = svc["beats"].as_i64().unwrap_or(0) + 1;
        svc["beats"] = json!(beats);
        if state == "probation" && beats >= PROBATION_BEATS {
            svc["state"] = json!("serving"); // earned, not granted — rookie probation
            let mut out = svc.clone();
            out["transition"] = json!({"from": "probation", "to": "serving", "op": "beat", "at": now});
            return Ok(out);
        }
        Ok(svc.clone())
    }

    /// Only a serving service is consumed — the refusal is the caller's uniform shape.
    pub fn meter(&mut self, req: &Value, now: &str) -> Result<Value, &'static str> {
        let name = req["name"].as_str().ok_or("which service?")?;
        let svc = self.services.get_mut(name).ok_or("no such service on this farm")?;
        if svc["state"] != "serving" {
            return Err("request cannot be served under this capability");
        }
        svc["calls"] = json!(svc["calls"].as_i64().unwrap_or(0) + 1);
        self.meter_log.push(json!({"at": now, "service": name,
            "caller": req["caller"].as_str().unwrap_or(""),
            "ms": req["ms"].as_i64().unwrap_or(0)}));
        Ok(json!({"ok": true, "calls": svc["calls"]}))
    }

    /// The roster this floor beats upward — one world, one picture.
    pub fn roster(&self) -> Vec<Value> {
        self.services.values().cloned().collect()
    }

    /// The meter-log door (2026-08-22 — 0059's named park paid): WHO leaned on
    /// each service, folded from the meter's own entries — per service, each
    /// distinct caller with its call count and last-seen. The blast radius on
    /// a rest/decom card stops guessing at the long tail. Volume and shape,
    /// never payloads (0016 §6) — a caller DID is already on the log.
    pub fn recent_callers(&self) -> Value {
        let mut per: BTreeMap<String, BTreeMap<String, (i64, String)>> = BTreeMap::new();
        for m in &self.meter_log {
            let (svc, caller) = (m["service"].as_str().unwrap_or(""),
                                 m["caller"].as_str().unwrap_or(""));
            if svc.is_empty() || caller.is_empty() {
                continue;
            }
            let at = m["at"].as_str().unwrap_or("").to_string();
            let e = per.entry(svc.to_string()).or_default()
                .entry(caller.to_string()).or_insert((0, String::new()));
            e.0 += 1;
            if at > e.1 {
                e.1 = at;
            }
        }
        json!(per.into_iter().map(|(svc, callers)| {
            let mut rows: Vec<Value> = callers.into_iter()
                .map(|(c, (n, last))| json!({"caller": c, "calls": n, "last": last}))
                .collect();
            rows.sort_by(|a, b| b["last"].as_str().cmp(&a["last"].as_str()));
            (svc, json!(rows))
        }).collect::<BTreeMap<String, Value>>())
    }
}

// ------------------------------------------------------- the callers' fold, suite-held
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn the_fold_names_who_leaned_and_when() {
        let mut f = Farm::new();
        f.services.insert("tavily-mcp".into(),
                          json!({"state": "serving", "calls": 0}));
        for (caller, at) in [("did:key:zcha", "t1"), ("did:key:zcha", "t3"),
                             ("did:key:zdesk", "t2")] {
            f.meter(&json!({"name": "tavily-mcp", "caller": caller}), at).unwrap();
        }
        let rc = f.recent_callers();
        let rows = rc["tavily-mcp"].as_array().unwrap();
        // most recent caller leads; counts and last-seen ride each row
        assert_eq!(rows[0]["caller"], "did:key:zcha");
        assert_eq!(rows[0]["calls"], 2);
        assert_eq!(rows[0]["last"], "t3");
        assert_eq!(rows[1]["caller"], "did:key:zdesk");
    }

    #[test]
    fn a_resting_service_is_never_consumed() {
        let mut f = Farm::new();
        f.services.insert("t".into(), json!({"state": "resting", "calls": 0}));
        assert!(f.meter(&json!({"name": "t", "caller": "c"}), "t1").is_err());
        assert!(f.recent_callers()["t"].is_null());
    }
}
