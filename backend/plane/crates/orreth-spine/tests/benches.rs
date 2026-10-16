// PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch Phase 8 THE STUDIO sp8, THE BENCH: the bench's proof on the rig · 2026-10-13
//! THE BENCH'S PROOF (canon 0011 §2 · 0005 Phase 8 sp8), on the dev rig, by name:
//!
//!     cargo test -p orreth-spine --features bridge --test benches -- --nocapture
//!
//! One Rust kernel lit alone: a person opens a bench (201; the same name opened again is handed
//! back, not doubled); a draft files ON the bench and a loose one beside it; the bench reads whole
//! (its drafts under it, no experiment, no seat); its step, state and hold are kept and cleared
//! (routine); another seat sees none of it (AG-9); letting it go discards its drafts and leaves the
//! loose one; a closed bench is at rest and a new one opens under the same name. With no rig it
//! prints "rails not up — skipped by name" and passes green.

#![cfg(feature = "bridge")]

use orreth_spine::bridge::{glass_path, light, Config};
use orreth_spine::world::{token_hex, World};
use orreth_spine::{proof, proof_live, rails};
use serde_json::{json, Value};
use std::time::Duration;
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
        "{method} {path} HTTP/1.1\r\nHost: 127.0.0.1:{port}\r\nConnection: close\r\n{extra}content-type: application/json\r\ncontent-length: {}\r\n\r\n{body}",
        body.len()
    );
    s.write_all(req.as_bytes()).await.unwrap();
    let mut raw = Vec::new();
    let _ = tokio::time::timeout(Duration::from_secs(10), s.read_to_end(&mut raw)).await;
    let text = String::from_utf8_lossy(&raw).to_string();
    let status: u16 = text.split_whitespace().nth(1).and_then(|c| c.parse().ok()).unwrap_or(0);
    let body = text.split_once("\r\n\r\n").map(|(_, b)| b.to_string()).unwrap_or_default();
    (status, serde_json::from_str(&body).unwrap_or(Value::Null))
}

async fn sit(port: u16, person: &str, owner: Option<&str>) -> String {
    let h: Vec<(&str, &str)> = owner.map(|w| vec![("authorization", w)]).unwrap_or_default();
    let (s, b) = knock(port, "POST", "/enroll", Some(&json!({"person": person})), &h).await;
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

#[tokio::test]
async fn a_bench_is_one_effort_one_place_under_the_seat() {
    if !rig_up("a_bench_is_one_effort_one_place_under_the_seat") {
        return;
    }
    if port_open(4600) || port_open(4601) {
        println!("a kernel holds :4600 or the reference :4601 — the bench proof refuses to run beside a live rig (stop it: scripts/dev.sh kernel stop · scripts/dev.sh reference stop)");
        return;
    }
    let tok = token_hex(3);
    let world = World { scope: format!("u:bench-{tok}"), ns: format!("t{tok}"), pg_dsn: rails::pg_dsn(), rabbit_url: rails::rabbit_url(), kafka: rails::kafka_bootstrap() };
    let home = std::env::temp_dir().join(format!("orreth-benches-{tok}"));
    std::fs::create_dir_all(home.join("agents")).unwrap();
    std::env::set_var("ORRETH_HOME", &home);
    std::env::set_var("SPINE_KERNEL_HOME", home.join("kernel"));
    std::env::set_var("SPINE_SERVICES_HOME", home.join("services"));
    std::env::set_var("SPINE_GATEWAY", "http://127.0.0.1:1");
    std::env::set_var("SPINE_MIND_CHECK_S", "3600");
    std::env::set_var("SPINE_TOOL_CHECK_S", "3600");
    std::env::remove_var("SPINE_MODE");
    let crew = home.join("crew.v0.json");
    std::fs::write(&crew, json!({"format": "orreth-crew/1", "levels": [{"at": "f:ops"}], "seats": [{"template": "templates/echo-resident.v0.json"}]}).to_string()).unwrap();   // sp10: the floor the experiment room opens on
    std::env::set_var("SPINE_CREW", &crew);
    let lit = light(Config {
        port: 0, world: world.clone(), glass: glass_path(), masters: String::new(), human_zone: "America/Denver".into(),
        bodies: false, ephemeral: true, spine: spine_dir(), cell: "local".into(), peers: vec![], kernel_home: Some(home.join("kernel")),
    })
    .await
    .expect("the Rust kernel lights alone");
    let port = lit.port;
    assert!(lit.wait_ready(Duration::from_secs(60)).await);
    let jb_wire = sit(port, "jb", None).await;
    let quinn_wire = sit(port, "quinn", Some(&jb_wire)).await;
    let jb = [("authorization", jb_wire.as_str())];
    let quinn = [("authorization", quinn_wire.as_str())];

    // 1. a bench opens; the same name opened again is handed back, never doubled
    let (s, r) = knock(port, "POST", "/benches", Some(&json!({"name": "jonathan", "words": "answers hello"})), &jb).await;
    assert_eq!(s, 201, "{r}");
    let b = &r["bench"];
    assert_eq!((b["name"].as_str(), b["step"].as_str(), b["state"].as_str()), (Some("jonathan"), Some("name"), Some("open")));
    assert!(b["drafts"].as_array().unwrap().is_empty() && b["experiments"].as_array().unwrap().is_empty() && b["seat"].is_null());
    let bid = b["bench_id"].as_str().unwrap().to_string();
    let (s, r) = knock(port, "POST", "/benches", Some(&json!({"name": "jonathan"})), &jb).await;
    assert_eq!((s, r["bench"]["bench_id"].as_str()), (201, Some(bid.as_str())));
    let (s, r) = knock(port, "POST", "/benches", Some(&json!({"name": "Bob.v0"})), &jb).await;
    assert_eq!(s, 400, "{r}");

    // 2. a draft files ON the bench; a loose one beside it; the bench reads whole
    let (s, r) = knock(port, "POST", "/drafts", Some(&json!({"kind": "graph", "name": "jonathan.v0", "bench": "jonathan", "body": {"entry": "say", "nodes": [{"id": "say", "kind": "echo"}], "edges": []}})), &jb).await;
    assert_eq!((s, r["draft"]["bench"].as_str()), (201, Some("jonathan")), "{r}");
    let (s, r) = knock(port, "POST", "/drafts", Some(&json!({"kind": "prompt", "name": "greeting", "body": {"text": "hi"}})), &jb).await;
    assert_eq!((s, r["draft"]["bench"].is_null()), (201, true), "{r}");
    let (s, r) = knock(port, "GET", "/benches/jonathan", None, &jb).await;
    assert_eq!(s, 200, "{r}");
    let names: Vec<&str> = r["bench"]["drafts"].as_array().unwrap().iter().map(|d| d["name"].as_str().unwrap()).collect();
    assert_eq!(names, vec!["jonathan.v0"]);

    // 3. the place is kept and cleared (routine); a wrong step is refused in words
    let (s, r) = knock(port, "POST", "/benches/jonathan", Some(&json!({"step": "golden", "body": {"shape": "echo", "cases": [{"ask": "hello", "expect": ["HELLO"]}]}, "hold": "ask_1"})), &jb).await;
    assert_eq!((s, r["bench"]["step"].as_str(), r["bench"]["hold"].as_str(), r["bench"]["body"]["shape"].as_str()), (200, Some("golden"), Some("ask_1"), Some("echo")), "{r}");
    let (s, r) = knock(port, "POST", "/benches/jonathan", Some(&json!({"hold": ""})), &jb).await;
    assert_eq!((s, r["bench"]["hold"].is_null()), (200, true), "{r}");
    let (s, r) = knock(port, "POST", "/benches/jonathan", Some(&json!({"step": "experiment"})), &jb).await;
    assert_eq!(s, 400, "{r}");

    // 4. another seat sees none of it (AG-9)
    let (s, r) = knock(port, "GET", "/benches", None, &quinn).await;
    assert_eq!((s, r["benches"].as_array().unwrap().len()), (200, 0));
    let (s, _) = knock(port, "GET", "/benches/jonathan", None, &quinn).await;
    assert_eq!(s, 404);
    let (s, r) = knock(port, "GET", "/benches", None, &jb).await;
    assert_eq!((s, r["benches"].as_array().unwrap().len(), r["steps"].as_array().unwrap().len()), (200, 1, 8));

    // 5. letting it go discards its drafts and leaves the loose one; at rest, a new effort opens under the same name
    let (s, r) = knock(port, "POST", "/benches/jonathan/close", None, &jb).await;
    assert_eq!((s, r["discarded"].as_i64(), r["bench"]["state"].as_str()), (200, Some(1), Some("closed")), "{r}");
    assert!(r["declined"].as_array().unwrap().is_empty() && r["words"].as_str().unwrap().contains("1 draft discarded"));
    let (_, r) = knock(port, "GET", "/drafts", None, &jb).await;
    let names: Vec<&str> = r["drafts"].as_array().unwrap().iter().map(|d| d["name"].as_str().unwrap()).collect();
    assert_eq!(names, vec!["greeting"]);
    let (s, r) = knock(port, "POST", "/benches/jonathan/close", None, &jb).await;
    assert_eq!(s, 400, "closed is closed: {r}");
    let (s, r) = knock(port, "POST", "/benches", Some(&json!({"name": "jonathan"})), &jb).await;
    assert_eq!(s, 201);
    assert_ne!(r["bench"]["bench_id"].as_str(), Some(bid.as_str()));
    let (_, r) = knock(port, "GET", "/benches", None, &jb).await;
    let states: Vec<&str> = r["benches"].as_array().unwrap().iter().map(|b| b["state"].as_str().unwrap()).collect();
    assert_eq!(states, vec!["open", "closed"]);
    println!("benches · jonathan opened once, kept its place, let go with its draft, opened again — quinn saw none of it");

    // 6. THE STUDIO sp10 ONE WORD TO WORK (canon 0011 §5): the chain refuses in words while something is missing;
    //    then ONE hold names every cut; the Yes cuts in order, opens the Experiment and moves the bench to THE CARD
    let (s, r) = knock(port, "POST", "/benches/jonathan/work", None, &jb).await;
    assert_eq!(s, 400, "{r}");
    assert!(r["error"].as_str().unwrap().contains("no graph jonathan.v0"), "{r}");
    for (kind, name, body) in [
        ("graph", "jonathan.v0", json!({"entry": "say", "nodes": [{"id": "say", "kind": "echo", "prompt": "jonathan-words"}], "edges": []})), // W149: the graph NAMES a prompt
        ("template", "jonathan", json!({"kind": "agent", "name": "jonathan", "graph": "jonathan.v0", "nature": "answers hello", "capabilities": ["ask"]})),
    ] {
        let (s, r) = knock(port, "POST", "/drafts", Some(&json!({"kind": kind, "name": name, "bench": "jonathan", "body": body})), &jb).await;
        assert_eq!(s, 201, "{r}");
    }
    let (s, r) = knock(port, "POST", "/benches/jonathan/work", None, &jb).await; // W149: a named prompt neither drafted nor standing refuses first
    assert_eq!(s, 400, "{r}");
    assert!(r["error"].as_str().unwrap().contains("the graph names prompt jonathan-words, which is neither a draft on the bench nor on the shelf"), "{r}");
    let (s, r) = knock(port, "POST", "/drafts", Some(&json!({"kind": "prompt", "name": "jonathan-words", "bench": "jonathan", "body": {"text": "Say hello."}})), &jb).await;
    assert_eq!(s, 201, "{r}");
    let (s, r) = knock(port, "POST", "/benches/jonathan/work", None, &jb).await;
    assert_eq!(s, 400, "{r}");
    assert!(r["error"].as_str().unwrap().contains("no golden set"), "{r}");
    let (s, r) = knock(port, "POST", "/drafts", Some(&json!({"kind": "golden", "name": "jonathan", "bench": "jonathan", "body": {"template": "jonathan", "cases": [{"ask": "hello", "expect": ["HELLO"]}]}})), &jb).await;
    assert_eq!(s, 201, "{r}");
    let (s, r) = knock(port, "POST", "/benches/jonathan/work", None, &quinn).await;
    assert_eq!(s, 403, "a reading seat may not put an agent to work: {r}");
    let (s, r) = knock(port, "POST", "/benches/jonathan/work", None, &jb).await;
    assert_eq!(s, 202, "{r}");
    let lines: Vec<&str> = r["lines"].as_array().unwrap().iter().map(|l| l.as_str().unwrap()).collect();
    assert_eq!(lines, vec!["the prompt jonathan-words as version 1", "the graph jonathan.v0 as version 1", "the golden set jonathan as version 1", "the agent jonathan as version 1 -> the experiment"]); // W149: the prompt first
    assert_eq!((r["level"].as_str(), r["cuts"].as_array().unwrap().len()), (Some("L2"), 4));
    let held = r["held"].as_str().unwrap().to_string();
    let (_, b) = knock(port, "GET", "/benches/jonathan", None, &jb).await;
    assert_eq!((b["bench"]["step"].as_str(), b["bench"]["hold"].as_str()), (Some("cut"), Some(held.as_str())), "{b}");
    let (s, r) = knock(port, "POST", "/benches/jonathan/work", None, &jb).await; // W148: one chain, ONE hold
    assert!(s != 202 && r.to_string().contains("already held"), "filed twice must refuse in words: {s} {r}");
    // the shelf's listing is the one read door for a craft by name (there is no /services/<name>)
    let on_shelf = |name: &'static str| {
        let jb = jb.clone();
        async move {
            let (_, r) = knock(port, "GET", "/services", None, &jb).await;
            r["services"].as_array().cloned().unwrap_or_default().into_iter().find(|x| x["name"] == json!(name)).map(|x| x["version"].as_i64().unwrap_or(0))
        }
    };
    assert_eq!((on_shelf("jonathan.v0.graph").await, on_shelf("jonathan-words.prompt").await), (None, None), "nothing lands before the Yes");
    knock(port, "POST", "/confirm", Some(&json!({"ask_id": held, "approve": true})), &jb).await;
    let t0 = std::time::Instant::now();
    let mut v = Value::Null;
    while t0.elapsed() < Duration::from_secs(30) {
        let (_, x) = knock(port, "GET", &format!("/ask/{held}"), None, &jb).await;
        if x["status"] == json!("replied") { v = x; break; }
        tokio::time::sleep(Duration::from_millis(400)).await;
    }
    let reply = v["reply"].as_str().unwrap_or_default().to_string();
    assert!(reply.contains("jonathan-words.prompt is on the shelf as version 1") && reply.contains("jonathan.v0.graph is on the shelf as version 1") && reply.contains("experiment room"), "{v}");
    assert_eq!((on_shelf("jonathan-words.prompt").await, on_shelf("jonathan.v0.graph").await), (Some(1), Some(1)), "W149: the prompt the graph names landed with the chain");
    let (_, b) = knock(port, "GET", "/benches/jonathan", None, &jb).await;
    assert_eq!((b["bench"]["step"].as_str(), b["bench"]["hold"].is_null(), b["bench"]["experiments"].as_array().unwrap().len()), (Some("card"), true, 1), "{b}");
    let (s, r) = knock(port, "POST", "/benches/jonathan/work", None, &jb).await;
    assert_eq!(s, 400, "{r}");
    assert!(r["error"].as_str().unwrap().contains("already running"), "{r}");
    println!("benches · ONE WORD TO WORK: refused in words until the chain stood, one hold named four cuts (the prompt the graph names first, W149), the Yes cut them in order and opened the experiment — the bench at THE CARD");

    lit.stop().await;
}
