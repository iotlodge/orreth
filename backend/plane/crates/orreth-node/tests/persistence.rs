//! The body store behind the node (decision 2026-07-02): same flows, real files.
//! Proves the two properties content addressing buys: tamper-evident reads, and
//! tombstones as PHYSICAL erasure — the bytes leave the disk, the stub remains.

use orreth_node::{scope_root, Node, Universe};
use orreth_store::{BodyStore, StoreError};
use serde_json::Value;
use std::collections::{BTreeMap, BTreeSet};

fn fixtures() -> Value {
    let path = concat!(
        env!("CARGO_MANIFEST_DIR"),
        "/../../../conformance/fixtures/flows.json"
    );
    serde_json::from_str(&std::fs::read_to_string(path).unwrap()).unwrap()
}

fn store_dir(name: &str) -> std::path::PathBuf {
    let dir = std::path::Path::new(env!("CARGO_MANIFEST_DIR"))
        .join("../../target/test-bodies")
        .join(name);
    let _ = std::fs::remove_dir_all(&dir);
    dir
}

fn universe_with_store(f: &Value, dir: &std::path::Path) -> Universe {
    let tiers = f["topology"].as_array().unwrap();
    let mut nodes = Vec::new();
    for (i, tier) in tiers.iter().enumerate() {
        nodes.push(Node {
            scope: tier["scope"].as_str().unwrap().to_string(),
            horizon_days: orreth_node::dur_days(tier["horizon"].as_str().unwrap()),
            parent: if i == 0 { None } else { Some(i - 1) },
            records: BTreeMap::new(),
            high_water: None,
            floors: f["floors"].as_array().unwrap().clone(),
        });
    }
    Universe {
        nodes,
        identities: f["identities"].as_object().unwrap().iter()
            .map(|(k, v)| (k.clone(), v.as_str().unwrap().to_string()))
            .collect(),
        revoked: BTreeSet::new(),
        purged: BTreeSet::new(),
        now: f["now"].as_str().unwrap().to_string(),
        body_store: Some(BodyStore::local(dir)),
        trust_root: None, // no retrieval in these tests; production profiles always pin
    }
}

/// The accepted writes from the fixture, applied at field_prod (index 2 of the chain).
fn apply_ok_writes(u: &mut Universe, f: &Value) -> Vec<Value> {
    let mut accepted = Vec::new();
    for w in f["writes"].as_array().unwrap() {
        if w["expect"] == "ok" && w["at_scope"] == "u:demo/e:cloud/f:prod" {
            u.write(2, &w["record"]).unwrap();
            accepted.push(w["record"].clone());
        }
    }
    accepted
}

#[test]
fn bodies_live_in_the_store_verified_by_their_own_address() {
    let f = fixtures();
    let dir = store_dir("roundtrip");
    let mut u = universe_with_store(&f, &dir);
    for rec in apply_ok_writes(&mut u, &f) {
        let id = rec["id"].as_str().unwrap();
        let stored = &u.nodes[2].records[id];
        assert!(stored.get("body").is_none(), "the node holds pointers, not blobs");
        assert!(stored["body_ref"].as_str().unwrap().starts_with("store://"));
        let bytes = u.get_body(stored).expect("verified read");
        assert!(!bytes.is_empty());
    }
}

#[test]
fn tampering_on_disk_is_caught_by_the_content_address() {
    let f = fixtures();
    let dir = store_dir("tamper");
    let mut u = universe_with_store(&f, &dir);
    let rec = apply_ok_writes(&mut u, &f).remove(0);
    let id = rec["id"].as_str().unwrap();
    // an attacker with disk access rewrites the object...
    let obj_path = dir
        .join("bodies")
        .join(scope_root(rec["scope"].as_str().unwrap()))
        .join(id.replace(':', "_"));
    std::fs::write(&obj_path, b"forged bytes").unwrap();
    // ...and the very next read refuses it: the address IS the checksum
    let stored = &u.nodes[2].records[id];
    assert_eq!(u.get_body(stored).unwrap_err(), StoreError::IntegrityViolation);
}

#[test]
fn tombstone_is_physical_erasure_stub_remains() {
    let f = fixtures();
    let dir = store_dir("erasure");
    let mut u = universe_with_store(&f, &dir);
    let rec = apply_ok_writes(&mut u, &f).remove(0);
    let id = rec["id"].as_str().unwrap().to_string();
    let root = scope_root(rec["scope"].as_str().unwrap());
    assert!(u.body_store.as_ref().unwrap().exists(&root, &id));
    u.tombstone(2, &id);
    // the bytes are GONE from storage — provable retirement, not soft deletion...
    assert!(!u.body_store.as_ref().unwrap().exists(&root, &id));
    assert_eq!(u.get_body(&u.nodes[2].records[&id]).unwrap_err(), StoreError::NotFound);
    // ...while the signed stub remains for audit: the identity of the memory outlives its content
    let stub = &u.nodes[2].records[&id];
    assert!(stub.get("body").is_none() && stub.get("body_ref").is_none());
    assert_eq!(stub["id"].as_str().unwrap(), id);
}
