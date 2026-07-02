//! Roll-up conformance: the Rust monoid must match the Python reference to 1e-9,
//! and must satisfy the monoid laws on the fixture data itself.

use serde_json::Value;

fn fixtures() -> Value {
    let path = concat!(
        env!("CARGO_MANIFEST_DIR"),
        "/../../../conformance/fixtures/rollup.json"
    );
    serde_json::from_str(&std::fs::read_to_string(path).expect("fixtures — run gen_fixtures.py"))
        .unwrap()
}

fn approx_eq(a: &Value, b: &Value, path: &str) {
    match (a, b) {
        (Value::Number(x), Value::Number(y)) => {
            let (x, y) = (x.as_f64().unwrap(), y.as_f64().unwrap());
            assert!((x - y).abs() < 1e-9, "{path}: {x} != {y}");
        }
        (Value::Array(xs), Value::Array(ys)) => {
            assert_eq!(xs.len(), ys.len(), "{path}: length");
            for (i, (x, y)) in xs.iter().zip(ys).enumerate() {
                approx_eq(x, y, &format!("{path}[{i}]"));
            }
        }
        (Value::Object(xm), Value::Object(ym)) => {
            assert_eq!(
                xm.keys().collect::<Vec<_>>(),
                ym.keys().collect::<Vec<_>>(),
                "{path}: keys"
            );
            for (k, x) in xm {
                approx_eq(x, &ym[k], &format!("{path}.{k}"));
            }
        }
        _ => assert_eq!(a, b, "{path}"),
    }
}

#[test]
fn merged_bundles_match_the_reference() {
    for case in fixtures()["cases"].as_array().unwrap() {
        let mut merged = orreth_rollup::empty_bundle();
        for run in case["runs"].as_array().unwrap() {
            merged = orreth_rollup::merge(&merged, &orreth_rollup::bundle_of(run));
        }
        approx_eq(&merged, &case["merged"], case["name"].as_str().unwrap());
    }
}

#[test]
fn reports_and_tier_scores_match_the_reference() {
    for case in fixtures()["cases"].as_array().unwrap() {
        let name = case["name"].as_str().unwrap();
        let rep = orreth_rollup::report(&case["merged"], "reliability", (1.0, 1.0));
        approx_eq(&rep, &case["report_reliability_uniform_prior"], &format!("{name}.report"));
        let vec: Vec<Value> = vec![
            serde_json::json!({"objective": "reliability", "weight": 1.0}),
            serde_json::json!({"objective": "compliance", "weight": 1.0, "floor": true}),
        ];
        let ts = orreth_rollup::tier_score(&case["merged"], &vec, (1.0, 1.0));
        approx_eq(&ts, &case["tier_score"], &format!("{name}.tier_score"));
    }
}

#[test]
fn monoid_laws_hold_on_fixture_data() {
    let f = fixtures();
    let runs: Vec<Value> = f["cases"].as_array().unwrap()[1]["runs"]
        .as_array()
        .unwrap()
        .clone();
    let bundles: Vec<Value> = runs.iter().map(orreth_rollup::bundle_of).collect();
    // associativity: left fold == right-grouped fold
    let left = bundles
        .iter()
        .fold(orreth_rollup::empty_bundle(), |acc, b| orreth_rollup::merge(&acc, b));
    let right = bundles
        .iter()
        .rev()
        .fold(orreth_rollup::empty_bundle(), |acc, b| orreth_rollup::merge(b, &acc));
    approx_eq(&left, &right, "associativity");
    // identity
    approx_eq(
        &orreth_rollup::merge(&orreth_rollup::empty_bundle(), &left),
        &left,
        "identity",
    );
}
