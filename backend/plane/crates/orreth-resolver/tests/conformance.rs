//! Resolver conformance: same chain ⇒ same id, across languages. The fixture's expected
//! id was computed by the Python reference — matching it here proves canonicalization,
//! hashing, and the fold all agree: one truth, two implementations.

use serde_json::Value;

fn fixtures() -> Value {
    let path = concat!(
        env!("CARGO_MANIFEST_DIR"),
        "/../../../conformance/fixtures/resolver.json"
    );
    serde_json::from_str(&std::fs::read_to_string(path).expect("fixtures — run gen_fixtures.py"))
        .unwrap()
}

#[test]
fn resolved_context_matches_the_reference_including_the_hash() {
    for case in fixtures()["cases"].as_array().unwrap() {
        let tiers = case["tiers"].as_array().unwrap();
        let floors = case["floors"].as_array().unwrap();
        let got = orreth_resolver::resolve(tiers, floors);
        assert_eq!(got, case["expected"], "case {}", case["name"]);
    }
}

#[test]
fn declaration_order_is_irrelevant() {
    // most-specific-wins and additive-union are order-free within a tier: shuffling the
    // soft/skills key insertion cannot change the output (BTreeMap makes this structural),
    // and the id is a pure function of the fold.
    let f = fixtures();
    let case = &f["cases"].as_array().unwrap()[0];
    let tiers = case["tiers"].as_array().unwrap();
    let floors = case["floors"].as_array().unwrap();
    let a = orreth_resolver::resolve(tiers, floors);
    let b = orreth_resolver::resolve(tiers, floors);
    assert_eq!(a["id"], b["id"]);
}
