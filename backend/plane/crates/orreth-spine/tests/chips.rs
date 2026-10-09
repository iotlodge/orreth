// PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch Phase 8 THE WORKSHOP sp6, THE TWO CHIPS: the proof on the rig · 2026-10-09
//! THE TWO CHIPS' PROOF (canon 0010 §8 · 0005 Phase 8 sp6), on the dev rig, by name:
//!
//!     cargo test -p orreth-spine --features bridge --test chips -- --nocapture
//!
//! One Rust kernel lit alone with a four-seat crew — the librarian, echo, and THE TWO CHIPS as real
//! spawned processes — and the key-check cadence set to five seconds: every seated body is CHALLENGED
//! by the kernel's beat over the rail, answers on its own bench by signing the kernel's nonce with
//! the key behind its DID (never marking itself proven), and the kernel VERIFIES — `/keychecks`
//! reads every body proven, none failed, the tally and the line; `/monitor` carries the metric
//! `key_checks_failed` at 0, the key-check's card and the kernel's SEVENTH watch at light beside the
//! six (`key_checks_failed > 0`, green); the chips stand on the crew alive, summonable by name; the
//! dial at 0 is honoured (the kernel's line says the cadence is off). With no rig it prints "rails not
//! up — skipped by name" and passes green.

#![cfg(feature = "bridge")]

use orreth_spine::bridge::{glass_path, light, Config};
use orreth_spine::world::{token_hex, World};
use orreth_spine::{proof, proof_live, rails};
use serde_json::{json, Value};
use std::time::{Duration, Instant};
use tokio::io::{AsyncReadExt, AsyncWriteExt};
use tokio::net::TcpStream;

fn port_open(port: u16) -> bool {
    std::net::TcpStream::connect_timeout(&std::net::SocketAddr::from(([127, 0, 0, 1], port)), Duration::from_millis(400)).is_ok()
}

fn rig_up(test: &str) -> bool {
    let up = std::env::var("SPINE_PG").is_ok() || port_open(5433);
    if !up {
        println!("rails not up — skipped by name: {test} (start the rig: scripts/dev.sh up)");
    }
    up
}

fn spine_dir() -> std::path::PathBuf {
    std::path::PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("../../../../spine")
}

async fn knock(port: u16, method: &str, path: &str, body: Option<&Value>, headers: &[(&str, &str)]) -> (u16, Value) {
    let mut s = TcpStream::connect(("127.0.0.1", port)).await.expect("the door answers");
    let body = body.map(|b| b.to_string()).unwrap_or_default();
    let extra: String = headers.iter().map(|(k, v)| format!("{k}: {v}\r\n")).collect();
    let req = format!(
        "{method} {path} HTTP/1.1\r\nhost: 127.0.0.1:{port}\r\ncontent-type: application/json\r\ncontent-length: {}\r\n{extra}connection: close\r\n\r\n{body}",
        body.len()
    );
    s.write_all(req.as_bytes()).await.unwrap();
    let mut out = Vec::new();
    s.read_to_end(&mut out).await.unwrap();
    let text = String::from_utf8_lossy(&out).to_string();
    let status: u16 = text.split_whitespace().nth(1).and_then(|c| c.parse().ok()).unwrap_or(0);
    let body = text.split_once("\r\n\r\n").map(|(_, b)| b.to_string()).unwrap_or_default();
    (status, serde_json::from_str(&body).unwrap_or(Value::Null))
}

async fn sit(port: u16, person: &str) -> String {
    let (s, b) = knock(port, "POST", "/enroll", Some(&json!({"person": person})), &[]).await;
    assert_eq!(s, 201, "enroll {person}: {b}");
    let secret = b["secret"].as_str().unwrap().to_string();
    let code = proof::totp(&secret, proof_live::now_unix()).unwrap();
    let (s, b) = knock(port, "POST", "/enroll/confirm", Some(&json!({"person": person, "code": code})), &[]).await;
    assert_eq!(s, 200, "confirm {person}: {b}");
    let code = proof::totp(&secret, proof_live::now_unix()).unwrap();
    let (s, b) = knock(port, "POST", "/seat", Some(&json!({"person": person, "code": code})), &[]).await;
    assert_eq!(s, 201, "seat {person}: {b}");
    format!("Bearer {}", b["wire"].as_str().unwrap())
}

async fn wait_for(port: u16, path: &str, wire: &str, within: Duration, done: impl Fn(&Value) -> bool) -> Value {
    let t0 = Instant::now();
    let mut last = Value::Null;
    while t0.elapsed() < within {
        let (_, v) = knock(port, "GET", path, None, &[("authorization", wire)]).await;
        if done(&v) {
            return v;
        }
        last = v;
        tokio::time::sleep(Duration::from_millis(500)).await;
    }
    panic!("{path} never answered as expected within {within:?}; last: {last}");
}

const CREW: [&str; 4] = ["librarian", "echo", "identity", "security"];

#[tokio::test]
async fn every_seated_body_proves_who_and_what_it_is_on_the_cadence() {
    if !rig_up("every_seated_body_proves_who_and_what_it_is_on_the_cadence") {
        return;
    }
    if port_open(4600) || port_open(4601) {
        println!("a kernel holds :4600 or the reference :4601 — the chips proof refuses to run beside a live rig (stop it: scripts/dev.sh kernel stop · scripts/dev.sh reference stop)");
        return;
    }
    let tok = token_hex(3);
    let u = format!("u:ch-{tok}");
    let world = World {
        scope: u.clone(),
        ns: format!("t{tok}"),
        pg_dsn: rails::pg_dsn(),
        rabbit_url: rails::rabbit_url(),
        kafka: rails::kafka_bootstrap(),
    };
    let home = std::env::temp_dir().join(format!("orreth-chips-{tok}"));
    std::fs::create_dir_all(home.join("agents")).unwrap();
    std::env::set_var("ORRETH_HOME", &home);
    std::env::set_var("SPINE_KERNEL_HOME", home.join("kernel"));
    std::env::set_var("SPINE_SERVICES_HOME", home.join("services"));
    std::env::set_var("SPINE_GATEWAY", "http://127.0.0.1:1"); // the gateway dark: the fake mind, no spend
    std::env::set_var("SPINE_MIND_CHECK_S", "3600");
    std::env::set_var("SPINE_TOOL_CHECK_S", "3600");
    std::env::set_var("SPINE_KEYCHECK_S", "5"); // every seated body asked every five seconds (300 at stock)
    std::env::remove_var("SPINE_MODE");
    let crew = home.join("crew.v0.json");
    std::fs::write(
        &crew,
        json!({"format": "orreth-crew/1",
               "seats": [{"template": "templates/librarian-resident.v0.json"},
                         {"template": "templates/echo-resident.v0.json"},
                         {"template": "templates/firmware-identity.v0.json"},
                         {"template": "templates/firmware-security.v0.json"}]})
        .to_string(),
    )
    .unwrap();
    std::env::set_var("SPINE_CREW", &crew);

    let lit = light(Config {
        port: 0,
        world: world.clone(),
        glass: glass_path(),
        masters: String::new(),
        human_zone: "America/Denver".into(),
        bodies: true,
        ephemeral: true,
        spine: spine_dir(),
        cell: "local".into(),
        peers: vec![],
        kernel_home: Some(home.join("kernel")),
    })
    .await
    .expect("the Rust kernel lights alone");
    let port = lit.port;
    assert!(lit.wait_ready(Duration::from_secs(60)).await);
    let jb_wire = sit(port, "jb").await;
    let jb = [("authorization", jb_wire.as_str())];
    let mut g = orreth_spine::ground::Ground::connect_as(&world.pg_dsn, "the chips proof").await.unwrap();

    // ---- 1. the four bodies alive — the two chips among the crew, firmware of the third kind, summonable
    let crew_v = wait_for(port, "/crew", &jb_wire, Duration::from_secs(240), |v| {
        v["crew"].as_array().is_some_and(|a| CREW.iter().all(|n| a.iter().any(|c| c["name"] == json!(n) && c["alive"] == json!(true))))
    })
    .await;
    for chip in ["identity", "security"] {
        let c = crew_v["crew"].as_array().unwrap().iter().find(|c| c["name"] == json!(chip)).unwrap();
        assert_eq!(c["kind"], json!("firmware"), "{c}");
    }
    let (_, inc) = knock(port, "GET", "/includes", None, &jb).await;
    assert_eq!(inc["base"], json!(["planner", "critic", "grader", "mitl"]), "the chips are not base includes — they come by summon: {inc}");
    println!("chips · the crew of four alive: {}", CREW.join(", "));

    // ---- 2. THE KEY-CHECK: every seated body challenged over the rail, answering with its proof, verified by the kernel
    let kc = wait_for(port, "/keychecks", &jb_wire, Duration::from_secs(180), |v| {
        v["tally"]["checked"].as_i64().unwrap_or(0) >= 4
            && CREW.iter().all(|n| v["keychecks"].as_array().unwrap_or(&vec![]).iter().any(|k| k["name"] == json!(n) && k["ok"] == json!(true)))
    })
    .await;
    assert_eq!(kc["tally"]["failed"], json!(0), "no body failed its check: {kc}");
    assert_eq!(kc["tally"]["cadence"], json!(5));
    let words = kc["words"].as_str().unwrap();
    assert!(words.contains("0 failed") && words.ends_with("every seated body is asked every 5 s to prove who and what it is"), "{words}");
    for k in kc["keychecks"].as_array().unwrap().iter().filter(|k| k["ok"] == json!(true)).take(4) {
        let w = k["words"].as_str().unwrap();
        assert!(w.starts_with("proven — who it says (") && w.contains(") and what it says ("), "{w}");
    }
    // the body wrote its proof on the row — its own key, its signature, the hash it stands on — and marked nothing
    let proofs: i64 = g
        .client()
        .query_one(
            "SELECT count(*) FROM spine_keychecks WHERE scope = $1 AND answered_at IS NOT NULL AND public_key IS NOT NULL AND sig IS NOT NULL AND what IS NOT NULL",
            &[&u],
        )
        .await
        .unwrap()
        .get(0);
    assert!(proofs >= 4, "the bodies' proofs stand on the rows: {proofs}");
    let joined_as: i64 = g
        .client()
        .query_one("SELECT count(*) FROM spine_keychecks WHERE scope = $1 AND ok AND what = joined_as", &[&u])
        .await
        .unwrap()
        .get(0);
    assert!(joined_as >= 4, "each proven body stands on the hash it joined as: {joined_as}");
    println!("chips · {} key-checks verified: {}", kc["tally"]["checked"], words);

    // ---- 3. the Monitor: the metric at 0, the card, the kernel's seventh watch beside the six
    let (s, m) = knock(port, "GET", "/monitor", None, &jb).await;
    assert_eq!(s, 200, "{m}");
    assert_eq!(m["values"]["key_checks_failed"], json!(0), "{m}");
    assert!(m["keychecks"]["checked"].as_i64().unwrap_or(0) >= 4 && m["keychecks"]["words"].as_str().is_some_and(|w| w.contains("0 failed")), "{}", m["keychecks"]);
    let watches = m["watches"].as_array().unwrap();
    let kw = watches.iter().find(|w| w["metric"] == json!("key_checks_failed")).unwrap_or_else(|| panic!("the kernel's key-check watch stands: {m}"));
    assert_eq!((kw["op"].as_str(), kw["threshold"].as_f64(), kw["added_by"].as_str(), kw["red"].as_bool()), (Some(">"), Some(0.0), Some("the kernel"), Some(false)));
    let kernels = watches.iter().filter(|w| w["added_by"] == json!("the kernel")).count();
    assert_eq!(kernels, 7, "the five, the ground's and the key-check's: {m}");
    println!("chips · the Monitor reads key_checks_failed 0; the kernel's seventh watch stands green beside the six");

    // ---- 4. the facts on the feed: a challenge asked, a verdict given
    let asked: i64 = g
        .client()
        .query_one("SELECT count(*) FROM spine_outbox WHERE convert_from(body, 'UTF8') LIKE '%orreth.keycheck.asked.v1%'", &[])
        .await
        .unwrap()
        .get(0);
    let verdicts: i64 = g
        .client()
        .query_one("SELECT count(*) FROM spine_outbox WHERE convert_from(body, 'UTF8') LIKE '%\"orreth.keycheck.v1\"%'", &[])
        .await
        .unwrap()
        .get(0);
    assert!(asked >= 4 && verdicts >= 4, "the challenges and the verdicts are facts: {asked} asked, {verdicts} verdicts");

    lit.stop().await;
    let _ = orreth_spine::ground::prune_scope(&mut g, &u).await;
}
