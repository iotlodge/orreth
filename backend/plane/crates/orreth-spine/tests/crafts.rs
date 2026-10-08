// PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch Phase 8 THE WORKSHOP sp2, THE SHELF WIDENED: the shelf's proof on the rig · 2026-10-05
//! THE SHELF WIDENED'S PROOF (canon 0010 lock 3 · lock 6 · 0005 Phase 8 sp2), on the dev rig, by name:
//!
//!     cargo test -p orreth-spine --features bridge --test crafts -- --nocapture
//!
//! One Rust kernel lit alone with a two-seat crew: at light the shelf holds the crafts the spine
//! ships beside the identities — each craft ADDRESSED (`craft:<name>.<kind>`), never a DID, its
//! health its declaration reading whole; the echo and the librarian join and WRITE WHAT THEY WEAR
//! (template · policy · graph · golden, each by the shelf's pin and version), seen through the
//! wear door and counted on every craft card ("in use by N"); a person's draft lives under their
//! seat alone (the owner sees none of it); the cut is refused in words before anything is held
//! (not whole · same bytes · an agent's template), held at L2 on the owner's word, and on the yes
//! lands the craft on the shelf as version 1 with the person on the chain, the draft spent; the
//! second cut lands version 2; a person's seat may not cut (govern). With no rig it prints
//! "rails not up — skipped by name" and passes green.

#![cfg(feature = "bridge")]

use orreth_spine::bridge::{glass_path, light, Config};
use orreth_spine::world::{token_hex, World};
use orreth_spine::{proof, proof_live, rails};
use serde_json::{json, Value};
use std::time::{Duration, Instant};
use tokio::io::{AsyncReadExt, AsyncWriteExt};
use tokio::net::TcpStream;

fn port_open(port: u16) -> bool {
    std::net::TcpStream::connect_timeout(
        &std::net::SocketAddr::from(([127, 0, 0, 1], port)),
        Duration::from_millis(400),
    )
    .is_ok()
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
        "{method} {path} HTTP/1.1\r\nHost: 127.0.0.1:{port}\r\nConnection: close\r\n{extra}content-type: \
         application/json\r\ncontent-length: {}\r\n\r\n{body}",
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

fn service<'a>(shelf: &'a Value, name: &str) -> &'a Value {
    shelf["services"]
        .as_array()
        .unwrap()
        .iter()
        .find(|s| s["name"] == json!(name))
        .unwrap_or_else(|| panic!("no {name} on the shelf: {shelf}"))
}

#[tokio::test]
async fn the_shelf_widened_crafts_addressed_the_wear_rows_written_and_a_draft_cut_at_l2() {
    if !rig_up("the_shelf_widened_crafts_addressed_the_wear_rows_written_and_a_draft_cut_at_l2") {
        return;
    }
    if port_open(4600) || port_open(4601) {
        println!("a kernel holds :4600 or the reference :4601 — the shelf proof refuses to run beside a live rig (stop it: scripts/dev.sh kernel stop · scripts/dev.sh reference stop)");
        return;
    }
    let tok = token_hex(3);
    let u = format!("u:shelf-{tok}");
    let world = World {
        scope: u.clone(),
        ns: format!("t{tok}"),
        pg_dsn: rails::pg_dsn(),
        rabbit_url: rails::rabbit_url(),
        kafka: rails::kafka_bootstrap(),
    };
    let home = std::env::temp_dir().join(format!("orreth-crafts-{tok}"));
    std::fs::create_dir_all(home.join("agents")).unwrap();
    std::env::set_var("ORRETH_HOME", &home);
    std::env::set_var("SPINE_KERNEL_HOME", home.join("kernel"));
    std::env::set_var("SPINE_SERVICES_HOME", home.join("services"));
    std::env::set_var("SPINE_GATEWAY", "http://127.0.0.1:1");
    std::env::set_var("SPINE_MIND_CHECK_S", "3600");
    std::env::set_var("SPINE_TOOL_CHECK_S", "3600");
    std::env::remove_var("SPINE_MODE");
    let crew = home.join("crew.v0.json");
    std::fs::write(
        &crew,
        json!({"format": "orreth-crew/1",
               "seats": [{"template": "templates/librarian-resident.v0.json"},
                         {"template": "templates/echo-resident.v0.json"}]})
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
    let jb_wire = sit(port, "jb", None).await;
    let quinn_wire = sit(port, "quinn", Some(&jb_wire)).await;
    let jb = [("authorization", jb_wire.as_str())];
    let quinn = [("authorization", quinn_wire.as_str())];

    // ---- 1. the shelf widened at light: the crafts beside the identities, addressed, their health whole
    let shelf = wait_for(port, "/services", &jb_wire, Duration::from_secs(120), |v| {
        v["services"].as_array().is_some_and(|a| {
            a.iter().any(|s| s["name"] == json!("librarian.template")) && a.iter().any(|s| s["name"] == json!("mind.v0.graph"))
        })
    })
    .await;
    assert_eq!(shelf["kinds"].as_array().unwrap().len(), 12, "twelve kinds: {}", shelf["kinds"]);
    let t = service(&shelf, "librarian.template");
    assert_eq!((t["kind"].as_str(), t["did"].as_str(), t["craft"].as_str(), t["version"].as_i64()),
               (Some("template"), Some("craft:librarian.template"), Some("librarian"), Some(1)));
    let g = service(&shelf, "mind.v0.graph");
    assert_eq!(g["did"], json!("craft:mind.v0.graph"));
    assert!(service(&shelf, "librarian.golden")["manifest"]["cases"].as_array().is_some_and(|c| c.len() == 2));
    assert_eq!(service(&shelf, "the-orreth-covenant.policy")["kind"], json!("policy"));
    assert_eq!(service(&shelf, "shelf.skill")["kind"], json!("skill"));
    // Phase 8 sp3, THE WORKSHOP v0: the third workspace seat's binding and the Workshop's Orreth skill stand at light;
    // the Workshop agent's one tool, `draft`, is a built-in on the shelf (routine — a draft under the human's seat)
    assert_eq!(service(&shelf, "workshop.binding")["manifest"]["pull"], json!("workshop"));
    assert_eq!(service(&shelf, "workshop.skill")["kind"], json!("skill"));
    assert_eq!(service(&shelf, "draft")["manifest"]["consequence"], json!("routine"));
    assert!(service(&shelf, "weather")["did"].as_str().unwrap().starts_with("did:orreth:service:"), "an identity is still a self");
    let (s, c) = knock(port, "POST", "/services/check", Some(&json!({"name": "librarian.template"})), &jb).await;
    assert_eq!(s, 200, "{c}");
    assert_eq!(c["checked"][0]["ok"], json!(true));
    assert!(c["checked"][0]["detail"].as_str().unwrap().contains("its graph mind.v0 stands on the shelf"), "{c}");
    println!("shelf · {} services, the crafts addressed: {}", shelf["services"].as_array().unwrap().len(), t["did"]);
    // a bare-named craft and a graph that does not read whole refuse at the door, in words
    let (s, r) = knock(port, "POST", "/services", Some(&json!({"name": "bare", "kind": "template",
        "manifest": {"format": "orreth-resident-template/1", "name": "bare", "graph": "mind.v0"}})), &jb).await;
    assert_eq!(s, 400, "{r}");
    assert!(r["error"].as_str().unwrap().contains("named <name>.template"), "{r}");
    let (s, r) = knock(port, "POST", "/services", Some(&json!({"name": "broken.graph", "kind": "graph",
        "manifest": {"format": "orreth-graph/1", "name": "broken", "nodes": [{"id": "a", "kind": "think"}]}})), &jb).await;
    assert_eq!(s, 400, "{r}");
    assert!(r["error"].as_str().unwrap().contains("a graph names its entry node"), "{r}");
    // a source's repo form: declared, not probed here
    let (s, r) = knock(port, "POST", "/services", Some(&json!({"name": "bob-src", "kind": "source",
        "manifest": {"repo": "https://github.com/x/bob", "commit": "a1b2c3d4e5f6", "entry": "bob.graph:build"}})), &jb).await;
    assert_eq!(s, 201, "{r}");
    let (s, c) = knock(port, "POST", "/services/check", Some(&json!({"name": "bob-src"})), &jb).await;
    assert_eq!(s, 200, "{c}");
    assert!(c["checked"][0]["ok"].is_null() && c["checked"][0]["detail"].as_str().unwrap().contains("fetched at import"), "{c}");

    // ---- 2. the bodies join and write what they wear; the wear door and the cards count it
    wait_for(port, "/crew", &jb_wire, Duration::from_secs(240), |v| {
        v["crew"].as_array().is_some_and(|a| {
            a.iter().any(|c| c["name"] == json!("echo") && c["alive"] == json!(true))
                && a.iter().any(|c| c["name"] == json!("librarian") && c["alive"] == json!(true))
        })
    })
    .await;
    let worn = wait_for(port, "/wear?component=librarian.template", &jb_wire, Duration::from_secs(60), |v| {
        v["worn_by"].as_array().is_some_and(|a| !a.is_empty())
    })
    .await;
    assert_eq!(worn["worn_by"][0]["body"], json!("librarian"));
    assert_eq!(worn["worn_by"][0]["version"], json!(1), "the version read by the shelf's pin: {worn}");
    assert!(worn["words"].as_str().unwrap().starts_with("librarian.template is worn by 1 body: librarian (life "), "{worn}");
    let (_, table) = knock(port, "GET", "/wear", None, &jb).await;
    assert_eq!(table["counts"]["the-orreth-covenant.policy"], json!(2), "both bodies wear the policy: {}", table["counts"]);
    assert_eq!(table["counts"]["mind.v0.graph"], json!(1));
    assert_eq!(table["counts"]["echo.v0.graph"], json!(1));
    assert_eq!(table["counts"]["librarian.golden"], json!(1));
    let (_, crew) = knock(port, "GET", "/crew", None, &jb).await;
    let echo_did = crew["crew"].as_array().unwrap().iter().find(|c| c["name"] == json!("echo")).unwrap()["did"].as_str().unwrap().to_string();
    let (_, mine) = knock(port, "GET", &format!("/wear?did={echo_did}"), None, &jb).await;
    let comps: Vec<&str> = mine["wears"].as_array().unwrap().iter().map(|w| w["component"].as_str().unwrap()).collect();
    assert_eq!(comps, vec!["echo.template", "the-orreth-covenant.policy", "echo.v0.graph"]);
    let (_, shelf) = knock(port, "GET", "/services?kind=template", None, &jb).await;
    assert_eq!(service(&shelf, "librarian.template")["worn_by"], json!(1));
    assert_eq!(service(&shelf, "planner.template")["worn_by"], json!(0));
    println!("wear · {}", worn["words"]);

    // ---- 3. the draft shelf under the person; the cut refused in words, held at L2, landed on the yes
    let (s, d) = knock(port, "POST", "/drafts", Some(&json!({"kind": "prompt", "name": "greeting",
        "body": {"text": "Greet the human by name."}, "words": "a warm opener"})), &quinn).await;
    assert_eq!(s, 201, "{d}");
    let draft_id = d["draft"]["draft_id"].as_str().unwrap().to_string();
    assert_eq!(d["draft"]["body"]["format"], json!("orreth-prompt/1"));
    let (_, q) = knock(port, "GET", "/drafts", None, &quinn).await;
    assert_eq!(q["drafts"].as_array().unwrap().len(), 1);
    let (_, j) = knock(port, "GET", "/drafts", None, &jb).await;
    assert!(j["drafts"].as_array().unwrap().is_empty(), "the owner sees no one else's drafts (AG-9): {j}");
    let (_, shelf) = knock(port, "GET", "/services?kind=prompt", None, &jb).await;
    assert!(shelf["services"].as_array().unwrap().is_empty(), "a draft is never on the shelf: {shelf}");
    // quinn's seat reads and writes — the cut is a governing seat's word
    let (s, r) = knock(port, "POST", "/drafts/cut", Some(&json!({"draft_id": draft_id})), &quinn).await;
    assert_eq!(s, 403, "{r}");
    // the owner may not cut quinn's draft (not theirs), and an unfinished draft of their own refuses in words
    let (s, r) = knock(port, "POST", "/drafts/cut", Some(&json!({"draft_id": draft_id})), &jb).await;
    assert_eq!(s, 400, "{r}");
    assert!(r["error"].as_str().unwrap().contains("no such draft of yours"), "{r}");
    let (s, h) = knock(port, "POST", "/drafts", Some(&json!({"kind": "graph", "name": "two", "body": {"nodes": [{"id": "a", "kind": "think"}]}})), &jb).await;
    assert_eq!(s, 201, "{h}");
    let half = h["draft"]["draft_id"].as_str().unwrap().to_string();
    let (s, r) = knock(port, "POST", "/drafts/cut", Some(&json!({"draft_id": half})), &jb).await;
    assert_eq!(s, 400, "{r}");
    assert!(r["error"].as_str().unwrap().contains("does not read whole yet: a graph names its entry node"), "{r}");
    let (s, a) = knock(port, "POST", "/drafts", Some(&json!({"kind": "template", "name": "bob", "body": {"graph": "mind.v0", "kind": "agent"}})), &jb).await;
    assert_eq!(s, 201, "{a}");
    let (s, r) = knock(port, "POST", "/drafts/cut", Some(&json!({"draft_id": a["draft"]["draft_id"]})), &jb).await;
    assert_eq!(s, 400, "{r}");
    // Phase 8 sp4: an agent's cut OPENS the Experiment — and the Experiment's evidence is required
    assert!(r["error"].as_str().unwrap().contains("bob has no golden set on the shelf"), "{r}");
    // the owner's own prompt: held at L2, nothing on the shelf before the yes
    let (s, d) = knock(port, "POST", "/drafts", Some(&json!({"kind": "prompt", "name": "greeting", "body": {"text": "Greet the human by name."}})), &jb).await;
    assert_eq!(s, 201, "{d}");
    let mine = d["draft"]["draft_id"].as_str().unwrap().to_string();
    let (s, held) = knock(port, "POST", "/drafts/cut", Some(&json!({"draft_id": mine})), &jb).await;
    assert_eq!(s, 202, "{held}");
    assert_eq!((held["level"].as_str(), held["class"].as_str(), held["verb"].as_str(), held["version"].as_i64(), held["shelf_name"].as_str()),
               (Some("L2"), Some("consequential"), Some("register"), Some(1), Some("greeting.prompt")));
    let ask_id = held["held"].as_str().unwrap().to_string();
    let (_, v) = knock(port, "GET", &format!("/ask/{ask_id}"), None, &jb).await;
    assert_eq!(v["status"], json!("awaiting-confirm"), "{v}");
    assert!(v["text"].as_str().unwrap().starts_with("cutting the greeting prompt — version 1 onto the shelf"), "{v}");
    let (_, shelf) = knock(port, "GET", "/services?kind=prompt", None, &jb).await;
    assert!(shelf["services"].as_array().unwrap().is_empty(), "nothing lands before the yes");
    let (s, done) = knock(port, "POST", "/confirm", Some(&json!({"ask_id": ask_id, "approve": true})), &jb).await;
    assert!(s == 200 || s == 202, "{done}");
    let v = wait_for(port, &format!("/ask/{ask_id}"), &jb_wire, Duration::from_secs(30), |v| v["status"] == json!("replied")).await;
    assert!(v["reply"].as_str().unwrap().contains("the greeting.prompt is on the shelf as version 1 (registered)"), "{v}");
    let (_, shelf) = knock(port, "GET", "/services?kind=prompt", None, &jb).await;
    let p = service(&shelf, "greeting.prompt");
    assert_eq!((p["did"].as_str(), p["version"].as_i64(), p["worn_by"].as_i64()), (Some("craft:greeting.prompt"), Some(1), Some(0)));
    assert!(p["by"].as_str().unwrap().contains("jb"), "the person on the chain: {p}");
    let (_, j) = knock(port, "GET", "/drafts", None, &jb).await;
    assert!(j["drafts"].as_array().unwrap().iter().all(|d| d["draft_id"] != json!(mine)), "the cut draft is spent: {j}");
    // the same bytes again refuse; changed words land version 2 — a sibling
    let (s, d) = knock(port, "POST", "/drafts", Some(&json!({"kind": "prompt", "name": "greeting", "body": {"text": "Greet the human by name."}})), &jb).await;
    assert_eq!(s, 201);
    let again = d["draft"]["draft_id"].as_str().unwrap().to_string();
    let (s, r) = knock(port, "POST", "/drafts/cut", Some(&json!({"draft_id": again})), &jb).await;
    assert_eq!(s, 400, "{r}");
    assert!(r["error"].as_str().unwrap().contains("already stands on the shelf with these exact bytes"), "{r}");
    let (s, _) = knock(port, "POST", "/drafts", Some(&json!({"kind": "prompt", "name": "greeting", "draft_id": again, "body": {"text": "Greet the human by name, warmly."}})), &jb).await;
    assert_eq!(s, 201);
    let (s, held) = knock(port, "POST", "/drafts/cut", Some(&json!({"draft_id": again})), &jb).await;
    assert_eq!(s, 202, "{held}");
    assert_eq!((held["verb"].as_str(), held["version"].as_i64()), (Some("version"), Some(2)));
    let ask2 = held["held"].as_str().unwrap().to_string();
    knock(port, "POST", "/confirm", Some(&json!({"ask_id": ask2, "approve": true})), &jb).await;
    wait_for(port, &format!("/ask/{ask2}"), &jb_wire, Duration::from_secs(30), |v| v["status"] == json!("replied")).await;
    let (_, shelf) = knock(port, "GET", "/services?kind=prompt", None, &jb).await;
    assert_eq!(service(&shelf, "greeting.prompt")["version"], json!(2));
    // a no stands nothing; a discard keeps nothing
    let (s, held) = knock(port, "POST", "/drafts", Some(&json!({"kind": "prompt", "name": "never", "body": {"text": "x"}})), &jb).await;
    assert_eq!(s, 201);
    let never = held["draft"]["draft_id"].as_str().unwrap().to_string();
    let (_, held) = knock(port, "POST", "/drafts/cut", Some(&json!({"draft_id": never})), &jb).await;
    let ask3 = held["held"].as_str().unwrap().to_string();
    knock(port, "POST", "/confirm", Some(&json!({"ask_id": ask3, "approve": false})), &jb).await;
    wait_for(port, &format!("/ask/{ask3}"), &jb_wire, Duration::from_secs(30), |v| v["status"] == json!("cancelled")).await;
    let (_, shelf) = knock(port, "GET", "/services?kind=prompt", None, &jb).await;
    assert!(shelf["services"].as_array().unwrap().iter().all(|s| s["name"] != json!("never.prompt")));
    let (s, r) = knock(port, "POST", "/drafts/discard", Some(&json!({"draft_id": never})), &jb).await;
    assert_eq!((s, r["discarded"].as_bool()), (200, Some(true)));
    let (s, r) = knock(port, "POST", "/drafts/discard", Some(&json!({"draft_id": never})), &quinn).await;
    assert_eq!(s, 404, "not quinn's: {r}");
    println!("drafts · greeting.prompt cut to version 2 on the owner's word; quinn's draft stays quinn's");

    lit.stop().await;
}
