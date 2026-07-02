//! The cascade resolver (0007) — the plane's hot path, ported from the Python reference.
//!
//! One fold, per-field merge laws: soft = most-specific-wins (attributed) · skills =
//! additive, higher version wins · floors sorted by content hash. The output is
//! CONTENT-ADDRESSED: same chain ⇒ same id — the conformance fixture pins the hash
//! against the reference, so both implementations produce one truth.

use serde_json::{json, Map, Value};

/// The pure fold: tiers root → leaf (scope, soft, skills, version) + the merged floor set.
/// Returns the resolved content including its content-addressed `id`.
pub fn resolve(tiers: &[Value], floors: &[Value]) -> Value {
    let mut soft: Map<String, Value> = Map::new();
    let mut skills: Map<String, Value> = Map::new();

    for tier in tiers {
        let scope = tier["scope"].as_str().unwrap();
        if let Some(tier_soft) = tier.get("soft").and_then(Value::as_object) {
            for (key, std) in tier_soft {
                let mut entry = Map::new();
                entry.insert("value".into(), std["value"].clone());
                entry.insert("from_scope".into(), json!(scope));
                if let Some(v) = std.get("version") {
                    entry.insert("version".into(), v.clone());
                }
                soft.insert(key.clone(), Value::Object(entry)); // later tier = more specific = wins
            }
        }
        if let Some(tier_skills) = tier.get("skills").and_then(Value::as_object) {
            for (name, ver) in tier_skills {
                let ver_s = ver.as_str().unwrap();
                let keep = match skills.get(name) {
                    Some(existing) => version_key(ver_s) > version_key(existing.as_str().unwrap()),
                    None => true,
                };
                if keep {
                    skills.insert(name.clone(), ver.clone()); // additive; higher version wins
                }
            }
        }
    }

    let mut sorted_floors: Vec<Value> = floors.to_vec();
    sorted_floors.sort_by_key(orreth_crypto::content_hash);

    let as_of: Vec<Value> = tiers
        .iter()
        .map(|t| json!({"scope": t["scope"], "version": t["version"]}))
        .collect();

    let mut content = Map::new();
    content.insert("scope".into(), tiers.last().unwrap()["scope"].clone());
    content.insert("floors".into(), Value::Array(sorted_floors));
    content.insert("soft".into(), Value::Object(soft));
    content.insert("skills".into(), Value::Object(skills));
    content.insert("as_of".into(), Value::Array(as_of));
    let content = Value::Object(content);

    let mut out = content.as_object().unwrap().clone();
    out.insert("id".into(), json!(orreth_crypto::content_hash(&content)));
    Value::Object(out)
}

/// "2.0.0" (anything after '-' ignored) → [2, 0, 0], for lexicographic comparison.
fn version_key(v: &str) -> Vec<u64> {
    v.split('-')
        .next()
        .unwrap_or("0")
        .split('.')
        .map(|p| p.parse().unwrap_or(0))
        .collect()
}
