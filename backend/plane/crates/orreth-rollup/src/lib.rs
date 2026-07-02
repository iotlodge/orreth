//! The StatBundle monoid (0005 §2–§4), ported from the Python reference.
//!
//! merge() is associative with empty_bundle() as identity; the Beta prior is applied
//! ONCE at report time (merging posteriors would double-count it); floors flag,
//! never average away. The conformance fixtures pin parity with the reference.

use serde_json::{json, Map, Value};

const OUTCOMES: [&str; 4] = ["success", "failure", "partial", "aborted"];
const COSTS: [&str; 4] = ["tokens", "model_calls", "usd", "wall_ms"];

pub fn empty_bundle() -> Value {
    let outcomes: Map<String, Value> = OUTCOMES.iter().map(|o| (o.to_string(), json!(0))).collect();
    let cost: Map<String, Value> = COSTS.iter().map(|c| (c.to_string(), json!(0))).collect();
    json!({"n": 0, "outcomes": outcomes, "per_objective": [], "cost": cost, "compliance": "clean"})
}

/// Lift one RunRecord into the monoid.
pub fn bundle_of(run: &Value) -> Value {
    let mut b = empty_bundle();
    b["n"] = json!(1);
    b["outcomes"][run["outcome"].as_str().unwrap()] = json!(1);
    let mut breached_any = false;
    let mut per_obj = Vec::new();
    for s in run["scores"].as_array().unwrap() {
        let score = s["score"].as_f64().unwrap();
        let breached = s.get("floor_breached").and_then(Value::as_bool).unwrap_or(false);
        breached_any |= breached;
        per_obj.push(json!({
            "objective": s["objective"], "n": 1, "sum": score,
            "sum_sq": score * score, "min": score, "max": score,
            "floor_breaches": if breached { 1 } else { 0 },
        }));
    }
    b["per_objective"] = Value::Array(per_obj);
    if breached_any {
        b["compliance"] = json!("breached");
    }
    if let Some(cost) = run.get("cost").and_then(Value::as_object) {
        for (k, v) in cost {
            b["cost"][k] = v.clone();
        }
    }
    b
}

/// Component-wise, associative; a breach anywhere is a breach of the whole.
pub fn merge(a: &Value, b: &Value) -> Value {
    let mut out = empty_bundle();
    out["n"] = json!(a["n"].as_i64().unwrap() + b["n"].as_i64().unwrap());
    for o in OUTCOMES {
        out["outcomes"][o] = json!(a["outcomes"][o].as_i64().unwrap() + b["outcomes"][o].as_i64().unwrap());
    }
    let mut stats: std::collections::BTreeMap<String, Value> = a["per_objective"]
        .as_array()
        .unwrap()
        .iter()
        .map(|s| (s["objective"].as_str().unwrap().to_string(), s.clone()))
        .collect();
    for s in b["per_objective"].as_array().unwrap() {
        let key = s["objective"].as_str().unwrap().to_string();
        match stats.get_mut(&key) {
            Some(t) => {
                t["n"] = json!(t["n"].as_i64().unwrap() + s["n"].as_i64().unwrap());
                t["sum"] = json!(t["sum"].as_f64().unwrap() + s["sum"].as_f64().unwrap());
                t["sum_sq"] = json!(t["sum_sq"].as_f64().unwrap() + s["sum_sq"].as_f64().unwrap());
                t["min"] = json!(t["min"].as_f64().unwrap().min(s["min"].as_f64().unwrap()));
                t["max"] = json!(t["max"].as_f64().unwrap().max(s["max"].as_f64().unwrap()));
                t["floor_breaches"] =
                    json!(t["floor_breaches"].as_i64().unwrap() + s["floor_breaches"].as_i64().unwrap());
            }
            None => {
                stats.insert(key, s.clone());
            }
        }
    }
    out["per_objective"] = Value::Array(stats.into_values().collect());
    for c in COSTS {
        let av = a["cost"].get(c).and_then(Value::as_f64).unwrap_or(0.0);
        let bv = b["cost"].get(c).and_then(Value::as_f64).unwrap_or(0.0);
        let total = av + bv;
        out["cost"][c] = if total.fract() == 0.0 { json!(total as i64) } else { json!(total) };
    }
    let breached = a["compliance"] == "breached" || b["compliance"] == "breached";
    out["compliance"] = json!(if breached { "breached" } else { "clean" });
    out
}

/// The read edge (locked 2026-07-02): Beta posterior, mean + 95% CI + n.
/// The tier's weak prior enters here and only here.
pub fn report(bundle: &Value, objective: &str, prior: (f64, f64)) -> Value {
    let stat = bundle["per_objective"]
        .as_array()
        .unwrap()
        .iter()
        .find(|s| s["objective"] == objective);
    let (a0, b0, n, breaches) = match stat {
        Some(s) if s["n"].as_i64().unwrap() > 0 => {
            let sn = s["n"].as_f64().unwrap();
            let sum = s["sum"].as_f64().unwrap();
            (prior.0 + sum, prior.1 + (sn - sum), s["n"].as_i64().unwrap(),
             s["floor_breaches"].as_i64().unwrap())
        }
        Some(s) => (prior.0, prior.1, 0, s["floor_breaches"].as_i64().unwrap()),
        None => (prior.0, prior.1, 0, 0),
    };
    let mean = a0 / (a0 + b0);
    let var = (a0 * b0) / ((a0 + b0).powi(2) * (a0 + b0 + 1.0));
    let half = 1.96 * var.sqrt(); // normal approx of the Beta, same as the reference
    json!({
        "mean": mean,
        "ci95": [(mean - half).max(0.0), (mean + half).min(1.0)],
        "n": n,
        "compliance": bundle["compliance"],
        "floor_breaches": breaches,
    })
}

/// 0004 §3's semantics: weighted mean over NON-floor objectives; floors gate, never dilute.
pub fn tier_score(bundle: &Value, objective_vector: &[Value], prior: (f64, f64)) -> Value {
    let soft: Vec<&Value> = objective_vector
        .iter()
        .filter(|o| !o.get("floor").and_then(Value::as_bool).unwrap_or(false))
        .collect();
    let total_w: f64 = soft.iter().map(|o| o["weight"].as_f64().unwrap()).sum();
    let total_w = if total_w == 0.0 { 1.0 } else { total_w };
    let score: f64 = soft
        .iter()
        .map(|o| {
            let r = report(bundle, o["objective"].as_str().unwrap(), prior);
            o["weight"].as_f64().unwrap() / total_w * r["mean"].as_f64().unwrap()
        })
        .sum();
    json!({"score": score, "compliance": bundle["compliance"]})
}
