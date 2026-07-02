//! The crypto conformance vectors: byte-for-byte parity with the Python reference.

use serde_json::Value;

fn fixtures() -> Value {
    let path = concat!(
        env!("CARGO_MANIFEST_DIR"),
        "/../../../conformance/fixtures/crypto.json"
    );
    serde_json::from_str(&std::fs::read_to_string(path).expect("fixtures — run gen_fixtures.py"))
        .unwrap()
}

#[test]
fn canonicalization_matches_python_byte_for_byte() {
    for case in fixtures()["canonical_vectors"].as_array().unwrap() {
        let got = orreth_crypto::canonical(&case["input"]);
        assert_eq!(got, case["canonical"].as_str().unwrap(), "canonical mismatch");
        let hash = orreth_crypto::content_hash(&case["input"]);
        assert_eq!(hash, case["hash"].as_str().unwrap(), "content hash mismatch");
    }
}

#[test]
fn python_signed_ed25519_verifies_here() {
    let v = fixtures();
    let sv = &v["signature_vector"];
    assert!(orreth_crypto::verify_sig(
        sv["sig"]["sig"].as_str().unwrap(),
        &sv["payload"],
        sv["public"].as_str().unwrap(),
    ));
    // and a tampered payload must NOT verify — Sourced or nothing
    let mut tampered = sv["payload"].clone();
    tampered["kind"] = Value::String("procedural".into());
    assert!(!orreth_crypto::verify_sig(
        sv["sig"]["sig"].as_str().unwrap(),
        &tampered,
        sv["public"].as_str().unwrap(),
    ));
}
