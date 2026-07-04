//! Replay the reference's three-flow scenario and match every expected outcome:
//! writes (accepted / clock-violation / bad-signature), keep_class under floors,
//! the pushed-up distillation, the tombstone, and all seven retrieval queries —
//! escalation, budget-miss ≡ authz-miss, sibling isolation, the interview firewall,
//! the uniform refusal, and tombstone fidelity labeling.

use orreth_node::{Universe, Node, WriteError, dur_days};
use serde_json::Value;
use std::collections::{BTreeMap, BTreeSet};

fn fixtures() -> Value {
    let path = concat!(
        env!("CARGO_MANIFEST_DIR"),
        "/../../../conformance/fixtures/flows.json"
    );
    serde_json::from_str(&std::fs::read_to_string(path).expect("fixtures — run gen_fixtures.py"))
        .unwrap()
}

fn build_universe(f: &Value) -> (Universe, BTreeMap<String, usize>) {
    // two chains sharing the apex: universe → eco_cloud → field_prod, and → eco_dev → field_lab
    let mut nodes = Vec::new();
    let mut index = BTreeMap::new();
    for chain_key in ["topology", "lab_chain"] {
        let mut parent: Option<usize> = None;
        for tier in f[chain_key].as_array().unwrap() {
            let scope = tier["scope"].as_str().unwrap().to_string();
            if let Some(&i) = index.get(&scope) {
                parent = Some(i); // the shared apex
                continue;
            }
            let i = nodes.len();
            nodes.push(Node {
                scope: scope.clone(),
                horizon_days: dur_days(tier["horizon"].as_str().unwrap()),
                parent,
                records: BTreeMap::new(),
                high_water: None,
                floors: f["floors"].as_array().unwrap().clone(), // published apex-wide, cascaded
            });
            index.insert(scope, i);
            parent = Some(i);
        }
    }
    let identities = f["identities"]
        .as_object()
        .unwrap()
        .iter()
        .map(|(k, v)| (k.clone(), v.as_str().unwrap().to_string()))
        .collect();
    (
        Universe {
            nodes,
            identities,
            revoked: BTreeSet::new(),
            purged: BTreeSet::new(),
            now: f["now"].as_str().unwrap().to_string(),
            body_store: None,
            trust_root: Some("did:web:orreth.ai:u:demo".to_string()),
            runs: BTreeMap::new(),
        },
        index,
    )
}

#[test]
fn the_three_flows_replay_exactly() {
    let f = fixtures();
    let (mut u, index) = build_universe(&f);

    // flow 2 (ingress): every write outcome must match the reference
    for w in f["writes"].as_array().unwrap() {
        let node = index[w["at_scope"].as_str().unwrap()];
        let result = u.write(node, &w["record"]);
        match w["expect"].as_str().unwrap() {
            "ok" => {
                let id = result.expect("reference accepted this write");
                let got_class = u.nodes[node].records[&id]["keep_class"].clone();
                assert_eq!(got_class, w["expect_keep_class"], "keep_class for {id}");
            }
            "clock-violation" => assert_eq!(result.unwrap_err(), WriteError::ClockViolation),
            _ => assert_eq!(result.unwrap_err(), WriteError::AuthzError),
        }
    }

    // the steward's distillation arrives pre-signed (the plane verifies, never signs)
    let dist = &f["distillation_pushed_up"];
    let field_prod = index["u:demo/e:cloud/f:prod"];
    let eco_cloud = index["u:demo/e:cloud"];
    u.write(field_prod, dist).expect("distillation at the field");
    u.write(eco_cloud, dist).expect("distillation pushed up");

    // the governed tombstone: purge raw, annotate provenance (fidelity checks below)
    for t in f["tombstones"].as_array().unwrap() {
        u.tombstone(index[t["at_scope"].as_str().unwrap()], t["record_id"].as_str().unwrap());
    }

    // flow 3 (egress): all seven queries, exact expected shapes
    for q in f["queries"].as_array().unwrap() {
        let name = q["name"].as_str().unwrap();
        let node = index[q["at_scope"].as_str().unwrap()];
        let result = u.retrieve(node, &q["query"], &q["token"],
                                q["requester_scope"].as_str().unwrap());
        let expect = &q["expect"];
        if expect.get("refusal").and_then(Value::as_bool).unwrap_or(false) {
            assert!(result.is_err(), "{name}: reference refused; we must too");
            continue;
        }
        let res = result.unwrap_or_else(|_| panic!("{name}: reference served; we refused"));
        let refs: Vec<&str> = res["hits"].as_array().unwrap().iter()
            .map(|h| h["ref"].as_str().unwrap()).collect();
        let want: Vec<&str> = expect["hit_refs"].as_array().unwrap().iter()
            .map(|v| v.as_str().unwrap()).collect();
        assert_eq!(refs, want, "{name}: hit refs (order matters)");
        for h in res["hits"].as_array().unwrap() {
            assert_eq!(&h["fidelity"], &expect["fidelity"][h["ref"].as_str().unwrap()],
                       "{name}: fidelity of {}", h["ref"]);
        }
        assert_eq!(&res["provenance"]["served_by"], &expect["served_by"], "{name}: served_by");
        assert_eq!(&res["verification"], &expect["verification"], "{name}: verification");
        assert_eq!(res.get("remainder").is_some(),
                   expect["has_remainder"].as_bool().unwrap(), "{name}: remainder presence");
    }
}
