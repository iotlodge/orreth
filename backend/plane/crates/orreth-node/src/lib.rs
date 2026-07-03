//! The plane's node semantics (0000 §2), ported from the reference: the store
//! (append-only, content-addressed, high-water clock — 0004), the gateway's ingress
//! checks (signature, revocation, scope — the plane VERIFIES, never signs; the steward
//! is cognition), and the retrieval router (escalation, budget-miss ≡ authz-miss,
//! fidelity labeling — 0002). Conformance: `fixtures/flows.json`.

use serde_json::{json, Map, Value};
use std::collections::{BTreeMap, BTreeSet};

// ---------------------------------------------------------------- scope & time helpers

pub fn is_within(scope: &str, ancestor: &str) -> bool {
    scope == ancestor || scope.starts_with(&format!("{ancestor}/"))
}

pub fn tenant_of(scope: &str) -> String {
    scope.split('/').take(2).collect::<Vec<_>>().join("/")
}

/// The universe segment — the storage isolation prefix (one prefix per tenant universe).
pub fn scope_root(scope: &str) -> String {
    scope.split('/').next().unwrap_or(scope).to_string()
}

/// "%Y-%m-%dT%H:%M:%SZ" → seconds since epoch (days_from_civil; no deps, no clocks).
pub fn ts_seconds(iso: &str) -> i64 {
    let b = iso.as_bytes();
    let num = |r: std::ops::Range<usize>| -> i64 {
        std::str::from_utf8(&b[r]).unwrap().parse().unwrap()
    };
    let (y, m, d) = (num(0..4), num(5..7), num(8..10));
    let (hh, mm, ss) = (num(11..13), num(14..16), num(17..19));
    let y2 = if m <= 2 { y - 1 } else { y };
    let era = y2.div_euclid(400);
    let yoe = y2 - era * 400;
    let doy = (153 * (if m > 2 { m - 3 } else { m + 9 }) + 2) / 5 + d - 1;
    let doe = yoe * 365 + yoe / 4 - yoe / 100 + doy;
    let days = era * 146_097 + doe - 719_468;
    days * 86_400 + hh * 3_600 + mm * 60 + ss
}

/// ISO-8601 duration → days (Y=365, M=30, matching the reference); "forever" → +inf.
pub fn dur_days(d: &str) -> f64 {
    if d == "forever" {
        return f64::INFINITY;
    }
    let (mut days, mut n, mut in_time) = (0.0_f64, 0.0_f64, false);
    for c in d.chars() {
        match c {
            'P' => {}
            'T' => in_time = true,
            '0'..='9' => n = n * 10.0 + (c as u8 - b'0') as f64,
            'Y' => { days += n * 365.0; n = 0.0 }
            'M' => { days += if in_time { n / 1_440.0 } else { n * 30.0 }; n = 0.0 }
            'W' => { days += n * 7.0; n = 0.0 }
            'D' => { days += n; n = 0.0 }
            'H' => { days += n / 24.0; n = 0.0 }
            'S' => { days += n / 86_400.0; n = 0.0 }
            _ => {}
        }
    }
    days
}

// ---------------------------------------------------------------- errors

#[derive(Debug, PartialEq)]
pub enum WriteError {
    AuthzError,
    ClockViolation,
}

/// Uniform caller-visible refusal — the reason never leaks (0002 §4).
#[derive(Debug)]
pub struct Refusal;

// ---------------------------------------------------------------- the universe of nodes

pub struct Node {
    pub scope: String,
    pub horizon_days: f64,
    pub parent: Option<usize>,
    pub records: BTreeMap<String, Value>,
    pub high_water: Option<String>,
    pub floors: Vec<Value>,
}

pub struct Universe {
    pub nodes: Vec<Node>,
    pub identities: BTreeMap<String, String>, // DID -> public (index; did:key embeds its own)
    pub revoked: BTreeSet<String>,
    pub purged: BTreeSet<String>, // tree-global, like the reference's purged_anywhere
    pub now: String,              // the pinned wall clock (fixtures are deterministic)
    /// When present, record bodies live here — content-addressed, tamper-evident,
    /// physically erasable (decision 2026-07-02: S3 API as contract, backend as config).
    pub body_store: Option<orreth_store::BodyStore>,
    /// The pinned trust root (0006 §1): token chains must START here. None = unpinned
    /// (tests only) — a production profile always pins.
    pub trust_root: Option<String>,
}

impl Universe {
    pub fn public_of(&self, did: &str) -> Option<String> {
        did.strip_prefix("did:key:")
            .map(str::to_string)
            .or_else(|| self.identities.get(did).cloned())
    }

    fn active(&self, did: &str) -> bool {
        !self.revoked.contains(did) && self.public_of(did).is_some()
    }

    // ---- ingress: the gateway's write pipeline -----------------------------------
    pub fn write(&mut self, node_idx: usize, record: &Value) -> Result<String, WriteError> {
        let now = self.now.clone();
        let author = record["author"].as_str().ok_or(WriteError::AuthzError)?;
        if !self.active(author) {
            return Err(WriteError::AuthzError);
        }
        let public = self.public_of(author).ok_or(WriteError::AuthzError)?;
        let signed = sig_subset(record);
        if !orreth_crypto::verify_sig(record["signature"]["sig"].as_str().unwrap_or(""), &signed, &public) {
            return Err(WriteError::AuthzError); // Sourced or nothing
        }
        let node = &mut self.nodes[node_idx];
        if !is_within(record["scope"].as_str().unwrap_or(""), &node.scope) {
            return Err(WriteError::AuthzError);
        }
        // the declared clock (0004): lived memory only moves forward; archives are labeled
        let occurred = record["occurred_at"].as_str().unwrap_or("");
        let lived = record.get("provenance_class").and_then(Value::as_str).unwrap_or("lived") == "lived";
        if lived {
            if let Some(hw) = &node.high_water {
                if ts_seconds(occurred) < ts_seconds(hw) {
                    return Err(WriteError::ClockViolation);
                }
            }
            if node.high_water.as_deref().map_or(true, |hw| ts_seconds(occurred) > ts_seconds(hw)) {
                node.high_water = Some(occurred.to_string());
            }
        }
        let mut rec = record.clone();
        rec["received_at"] = json!(now); // gateway stamp — physics, nobody's claim
        rec["keep_class"] = json!(classify(&node.floors, record));
        let id = rec["id"].as_str().unwrap().to_string();
        // bodies leave the record at ingress: the store holds bytes, the node holds pointers
        if let (Some(store), Some(body)) = (&self.body_store, rec.get("body").and_then(Value::as_str)) {
            let root = scope_root(rec["scope"].as_str().unwrap());
            let body_ref = store
                .put_body(&root, &id, body)
                .map_err(|_| WriteError::AuthzError)?;
            let obj = rec.as_object_mut().unwrap();
            obj.remove("body");
            obj.insert("body_ref".into(), json!(body_ref));
        }
        node.records.insert(id.clone(), rec);
        Ok(id)
    }

    /// Fetch a record's body from the store — VERIFIED against its own content address.
    pub fn get_body(&self, record: &Value) -> Result<Vec<u8>, orreth_store::StoreError> {
        let store = self.body_store.as_ref().ok_or(orreth_store::StoreError::NotFound)?;
        let id = record["id"].as_str().unwrap();
        store.get_body(&scope_root(record["scope"].as_str().unwrap()), id)
    }

    pub fn tombstone(&mut self, node_idx: usize, record_id: &str) {
        let scope = self.nodes[node_idx].records.get(record_id)
            .map(|r| r["scope"].as_str().unwrap().to_string());
        if let Some(rec) = self.nodes[node_idx].records.get_mut(record_id) {
            rec.as_object_mut().unwrap().remove("body");
            rec.as_object_mut().unwrap().remove("body_ref");
        }
        // the tombstone's storage twin: the bytes are PHYSICALLY gone; the signed stub remains
        if let (Some(store), Some(scope)) = (&self.body_store, scope) {
            let _ = store.delete_body(&scope_root(&scope), record_id);
        }
        self.purged.insert(record_id.to_string());
    }

    // ---- egress: the retrieval router (0002 §3–§4) --------------------------------
    pub fn retrieve(&self, node_idx: usize, query: &Value, token: &Value,
                    requester_scope: &str) -> Result<Value, Refusal> {
        self.verify_token(token)?;
        let grant = covering_grant(token, "retrieve").ok_or(Refusal)?;
        let interview = query["intent"] == "interview";
        if interview {
            let vis = grant.get("visibility").and_then(Value::as_array);
            if !vis.is_some_and(|v| v.iter().any(|x| x == "portfolio")) {
                return Err(Refusal);
            }
        }
        let audience = token["audience"].as_str().unwrap();
        let mut budget = query["budget"]["cost"].as_i64().unwrap_or(1).max(1);
        let window_from = query["time"]["from"].as_str().unwrap();
        let (mut hits_raw, mut served_by) = (BTreeMap::<String, &Value>::new(), Vec::new());
        let mut not_served = false;
        let mut cursor = Some(node_idx);

        while let Some(i) = cursor {
            let node = &self.nodes[i];
            // budget-miss ≡ authz-miss: both are un-served coverage, never an error shape
            if budget <= 0 || !is_within(&node.scope, audience) {
                not_served = true;
                break;
            }
            budget -= 1;
            served_by.push(node.scope.clone());
            for rec in node.records.values() {
                if self.readable(rec, query, token, requester_scope, interview) {
                    hits_raw.entry(rec["id"].as_str().unwrap().to_string()).or_insert(rec);
                }
            }
            let now_u = node.high_water.clone().unwrap_or_else(|| self.now.clone());
            let age_days = (ts_seconds(&now_u) - ts_seconds(window_from)) as f64 / 86_400.0;
            if age_days <= node.horizon_days {
                break; // this tier's horizon covers the window ('forever' always covers)
            }
            cursor = node.parent; // time-horizon miss: delegate the deeper remainder UP
        }

        let mut ordered: Vec<&&Value> = hits_raw.values().collect();
        ordered.sort_by(|a, b| b["occurred_at"].as_str().cmp(&a["occurred_at"].as_str()));
        let hits: Vec<Value> = ordered
            .iter()
            .map(|r| {
                json!({"ref": r["id"], "source": r["author"], "scope": r["scope"],
                       "occurred_at": r["occurred_at"], "fidelity": self.fidelity(r)})
            })
            .collect();
        let mut result = json!({
            "hits": hits,
            "provenance": {"served_by": served_by, "time_span": query["time"],
                            "budget_spent": {"cost": query["budget"]["cost"].as_i64().unwrap_or(1).max(1) - budget}},
            "verification": if not_served { "partial" } else { "verified" },
        });
        if not_served {
            result["remainder"] = json!({"not_served": {"from": window_from}});
        }
        Ok(result)
    }

    fn verify_token(&self, token: &Value) -> Result<(), Refusal> {
        if token["constraints"]["expiry"].as_str().unwrap_or("") < self.now.as_str() {
            return Err(Refusal);
        }
        if !self.active(token["subject"].as_str().unwrap_or("")) {
            return Err(Refusal);
        }
        // pinned root + continuity + attenuation: verified at presentation, not trusted
        // from issuance — no foreign root mints authority here (0006 §1/§3)
        let mut prev_subject: Option<String> = None;
        let mut prev_scope: Option<String> = None;
        for raw in token["chain"].as_array().ok_or(Refusal)? {
            let cert: Value = serde_json::from_str(raw.as_str().ok_or(Refusal)?).map_err(|_| Refusal)?;
            let issuer = cert["issuer"].as_str().ok_or(Refusal)?;
            match &prev_subject {
                None => {
                    if let Some(root) = &self.trust_root {
                        if issuer != root {
                            return Err(Refusal); // chain does not start at the trust root
                        }
                    }
                }
                Some(ps) => {
                    if issuer != ps {
                        return Err(Refusal); // delegation continuity broken
                    }
                }
            }
            if !self.active(issuer) {
                return Err(Refusal); // ancestor revocation kills the subtree
            }
            let public = self.public_of(issuer).ok_or(Refusal)?;
            if !orreth_crypto::verify_sig(cert["sig"]["sig"].as_str().unwrap_or(""), &cert, &public) {
                return Err(Refusal);
            }
            let this_scope = cert
                .get("scope")
                .or_else(|| cert.get("audience"))
                .and_then(Value::as_str)
                .map(str::to_string);
            if let (Some(prev), Some(this)) = (&prev_scope, &this_scope) {
                if !is_within(this, prev) {
                    return Err(Refusal); // attenuation violated — scopes only narrow
                }
            }
            prev_subject = cert["subject"].as_str().map(str::to_string);
            prev_scope = this_scope.or(prev_scope);
        }
        let last: Value = serde_json::from_str(
            token["chain"].as_array().unwrap().last().ok_or(Refusal)?.as_str().unwrap(),
        )
        .map_err(|_| Refusal)?;
        if last["audience"] != token["audience"] || last["subject"] != token["subject"] {
            return Err(Refusal); // chain must bind the token
        }
        Ok(())
    }

    fn readable(&self, rec: &Value, query: &Value, token: &Value, requester_scope: &str,
                interview: bool) -> bool {
        let id = rec["id"].as_str().unwrap();
        if rec["kind"] != "distillation" && self.purged.contains(id) {
            return false;
        }
        if !is_within(rec["scope"].as_str().unwrap(), token["audience"].as_str().unwrap()) {
            return false;
        }
        match &query["subject"] {
            Value::String(s) if s == "self" => {
                if rec["author"] != query["requester"] {
                    return false;
                }
            }
            Value::Object(m) if m.contains_key("identity") => {
                if rec["author"] != m["identity"] {
                    return false;
                }
            }
            Value::Object(m) if m.contains_key("cohort") => {
                if let Some(scope) = m["cohort"].get("scope").and_then(Value::as_str) {
                    if !is_within(rec["scope"].as_str().unwrap(), scope) {
                        return false;
                    }
                }
            }
            _ => {}
        }
        if ts_seconds(query["time"]["from"].as_str().unwrap())
            > ts_seconds(rec["occurred_at"].as_str().unwrap())
        {
            return false;
        }
        let tenancy = rec
            .get("visibility")
            .and_then(|v| v.get("tenancy"))
            .and_then(Value::as_str)
            .unwrap_or("tenant-private");
        if interview {
            return tenancy == "portfolio";
        }
        if tenancy == "tenant-private" {
            let r_scope = rec["scope"].as_str().unwrap();
            let same_tenant = tenant_of(r_scope) == tenant_of(requester_scope)
                || is_within(r_scope, requester_scope);
            let apex_grant = token["grants"]
                .as_array()
                .is_some_and(|gs| gs.iter().any(|g| g.get("space") == Some(&json!("apex"))));
            if !(same_tenant || apex_grant) {
                return false;
            }
        }
        true
    }

    fn fidelity(&self, rec: &Value) -> &'static str {
        if rec["kind"] != "distillation" {
            return "verified";
        }
        let expired = rec["derived_from"]
            .as_array()
            .is_some_and(|srcs| srcs.iter().any(|s| self.purged.contains(s.as_str().unwrap())));
        if expired {
            "distilled-raw-expired"
        } else {
            "distilled"
        }
    }
}

// ---------------------------------------------------------------- pure helpers

/// The signed subset: occurred_at and provenance_class are author claims; received_at is not.
fn sig_subset(record: &Value) -> Value {
    let mut m = Map::new();
    for k in ["id", "kind", "scope", "author", "occurred_at", "provenance_class"] {
        if let Some(v) = record.get(k) {
            m.insert(k.into(), v.clone());
        }
    }
    Value::Object(m)
}

/// Floor classification (0003 §1), matching the reference's rule walk.
fn classify(floors: &[Value], record: &Value) -> &'static str {
    let tags: Vec<&str> = record
        .get("tags")
        .and_then(Value::as_array)
        .map(|a| a.iter().filter_map(Value::as_str).collect())
        .unwrap_or_default();
    for rule in floors {
        let m = &rule["match"];
        if let Some(outcome) = m.get("outcome").and_then(Value::as_str) {
            if outcome != "any" && tags.contains(&outcome) {
                return if rule["action"] == "keep-raw" { "keep-raw" } else { "distilled-raw-retained" };
            }
        }
        if let Some(rule_tags) = m.get("tags").and_then(Value::as_array) {
            if rule_tags.iter().filter_map(Value::as_str).any(|t| tags.contains(&t)) {
                return if rule["action"] == "keep-raw" { "keep-raw" } else { "distilled-raw-retained" };
            }
        }
    }
    "distilled-raw-retained"
}

fn covering_grant<'a>(token: &'a Value, action: &str) -> Option<&'a Value> {
    token["grants"].as_array()?.iter().find(|g| g["action"] == action)
}
