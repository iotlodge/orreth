// PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch Phase 8 THE WORKSHOP sp4, THE EXPERIMENT AND THE CUT: the proof on the rig · 2026-10-07
//! THE EXPERIMENT'S PROOF (canon 0010 §5 · 0005 Phase 8 sp4), on the dev rig, by name:
//!
//!     cargo test -p orreth-spine --features bridge --test experiments -- --nocapture
//!
//! One Rust kernel lit alone with a two-seat crew on a floor: the owner cuts an agent's graph and
//! its golden set onto the shelf (held at L2 each); an agent template WITHOUT its golden set is
//! refused in words at the cut; with it, the cut HOLDS THE EXPERIMENT'S OPENING (`experiment.open`,
//! L2, the words naming the room, the one arm and the cases); on the yes the experiment room stands
//! on the floor and the experiment runs — THE EXPERIMENT BEAT spawns the candidate's TRIAL LIFE as
//! `body --experiment` (a real process: it knocks at the desk on its ticket, joins in the room, runs
//! the golden set through its own echo graph, records the run and stops whole), reads the run, finds
//! no grader or critic seated here (said honestly) and PROPOSES; `/experiments` reads it whole; the
//! owner PROMOTES (held at L2) — on the yes the template stands on the shelf as version 1, the seat is
//! written on the floor and the kernel SEATS bob's life from the shelf (`/bodies` shows it alive, the
//! crew shows it on the floor); "bob, hello" is served by bob; `rest bob` holds at L2 and on the yes
//! the body stops whole and `/bodies` reads rested; the grave is refused for an active body and a crew
//! body holds no seat. With no rig it prints "rails not up — skipped by name" and passes green.

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

async fn cut(port: u16, jb: &[(&str, &str)], jb_wire: &str, kind: &str, name: &str, body: Value) -> Value {
    let (s, d) = knock(port, "POST", "/drafts", Some(&json!({"kind": kind, "name": name, "body": body})), jb).await;
    assert_eq!(s, 201, "{d}");
    let draft_id = d["draft"]["draft_id"].as_str().unwrap().to_string();
    let (s, held) = knock(port, "POST", "/drafts/cut", Some(&json!({"draft_id": draft_id})), jb).await;
    assert_eq!(s, 202, "{held}");
    let ask_id = held["held"].as_str().unwrap().to_string();
    knock(port, "POST", "/confirm", Some(&json!({"ask_id": ask_id, "approve": true})), jb).await;
    wait_for(port, &format!("/ask/{ask_id}"), jb_wire, Duration::from_secs(30), |v| v["status"] == json!("replied")).await
}

#[tokio::test]
async fn the_experiment_opens_on_an_agents_cut_and_the_promotion_seats_its_life() {
    if !rig_up("the_experiment_opens_on_an_agents_cut_and_the_promotion_seats_its_life") {
        return;
    }
    if port_open(4600) || port_open(4601) {
        println!("a kernel holds :4600 or the reference :4601 — the experiment proof refuses to run beside a live rig (stop it: scripts/dev.sh kernel stop · scripts/dev.sh reference stop)");
        return;
    }
    let tok = token_hex(3);
    let u = format!("u:xp-{tok}");
    let world = World {
        scope: u.clone(),
        ns: format!("t{tok}"),
        pg_dsn: rails::pg_dsn(),
        rabbit_url: rails::rabbit_url(),
        kafka: rails::kafka_bootstrap(),
    };
    let home = std::env::temp_dir().join(format!("orreth-experiments-{tok}"));
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
               "levels": [{"at": "f:ops"}],
               "seats": [{"template": "templates/librarian-resident.v0.json"},
                         {"template": "templates/echo-resident.v0.json", "at": "f:ops"}]})
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
        ephemeral: false, // the agent's self survives its lives: the trial, then the seat
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
    wait_for(port, "/crew", &jb_wire, Duration::from_secs(240), |v| {
        v["crew"].as_array().is_some_and(|a| a.iter().any(|c| c["name"] == json!("echo") && c["alive"] == json!(true)))
    })
    .await;

    // ---- 1. the agent's components onto the shelf: its graph, then its golden set
    cut(port, &jb, &jb_wire, "graph", "bob.v0", json!({"entry": "say", "nodes": [{"id": "say", "kind": "echo"}], "edges": []})).await;
    let (s, d) = knock(port, "POST", "/drafts", Some(&json!({"kind": "template", "name": "bob",
        "body": {"kind": "agent", "graph": "bob.v0", "nature": "a test agent", "capabilities": ["ask"]}})), &jb).await;
    assert_eq!(s, 201, "{d}");
    let draft_id = d["draft"]["draft_id"].as_str().unwrap().to_string();
    let (s, r) = knock(port, "POST", "/drafts/cut", Some(&json!({"draft_id": draft_id})), &jb).await;
    assert_eq!(s, 400, "{r}");
    assert!(r["error"].as_str().unwrap().contains("bob has no golden set on the shelf"), "{r}");
    cut(port, &jb, &jb_wire, "golden", "bob", json!({"template": "bob", "cases": [{"ask": "hello bob", "expect": ["hello"]}, {"ask": "say moon", "expect": ["moon"]}]})).await;

    // ---- 2. the agent's cut HOLDS the Experiment's opening at L2; the yes opens the room and runs it
    let (s, held) = knock(port, "POST", "/drafts/cut", Some(&json!({"draft_id": draft_id})), &jb).await;
    assert_eq!(s, 202, "{held}");
    assert_eq!((held["gate"].as_str(), held["verb"].as_str(), held["level"].as_str(), held["cases"].as_i64()),
               (Some("experiment"), Some("experiment"), Some("L2"), Some(2)));
    assert_eq!(held["room"], json!(format!("{u}/f:ops/r:exp-bob-1")));
    let ask_id = held["held"].as_str().unwrap().to_string();
    let (_, v) = knock(port, "GET", &format!("/ask/{ask_id}"), None, &jb).await;
    assert_eq!(v["status"], json!("awaiting-confirm"), "{v}");
    assert!(v["text"].as_str().unwrap().starts_with("opening an experiment on the bob agent — room exp-bob-1 on floor ops of universe"), "{v}");
    assert!(v["text"].as_str().unwrap().contains("one arm — the candidate alone"), "{v}");
    let (_, xs) = knock(port, "GET", "/experiments", None, &jb).await;
    assert!(xs["experiments"].as_array().unwrap().is_empty(), "nothing before the yes: {xs}");
    knock(port, "POST", "/confirm", Some(&json!({"ask_id": ask_id, "approve": true})), &jb).await;
    let done = wait_for(port, &format!("/ask/{ask_id}"), &jb_wire, Duration::from_secs(30), |v| v["status"] == json!("replied")).await;
    assert!(done["reply"].as_str().unwrap().starts_with("Done, on your word: room exp-bob-1 on floor ops of universe"), "{done}");
    let (_, lv) = knock(port, "GET", "/levels", None, &jb).await;
    let room = lv["levels"].as_array().unwrap().iter().find(|l| l["path"] == json!(format!("{u}/f:ops/r:exp-bob-1"))).expect("the room stands");
    assert_eq!(room["experiment"], json!(true));
    let (_, xs) = knock(port, "GET", "/experiments", None, &jb).await;
    let x = &xs["experiments"][0];
    assert_eq!((x["agent"].as_str(), x["state"].as_str()), (Some("bob"), Some("running")));
    let xid = x["experiment_id"].as_str().unwrap().to_string();
    println!("experiment · {xid} running in {}", x["room"]);

    // ---- 3. THE BEAT: the trial life (a real `body --experiment` process in the room), the run read, the proposal
    let proposed = wait_for(port, &format!("/experiments?id={xid}"), &jb_wire, Duration::from_secs(180), |v| v["experiment"]["state"] == json!("proposed")).await;
    let x = &proposed["experiment"];
    assert_eq!((x["arms"]["candidate"]["passed"].as_i64(), x["arms"]["candidate"]["failed"].as_i64()), (Some(2), Some(0)), "{x}");
    assert!(x["arms"]["current"].is_null(), "a first version has one arm: {x}");
    assert_eq!(x["leaning"], json!("unsure"), "no reviewer is seated in this two-seat world: {x}");
    let words = x["proposal"].as_str().unwrap();
    assert!(words.starts_with("THE EXPERIMENT on bob proposes: the candidate passed 2 of 2 · no current arm — the first version · the grader: the grader is not seated here — no verdict"), "{words}");
    assert!(words.contains("the identity chip: the identity is not seated here — no verdict · the security chip: the security is not seated here — no verdict") && words.contains("say “promote bob”"), "{words}"); // Phase 8 sp6: the chips named, missing honestly in a two-seat world
    let (_, joins) = knock(port, "GET", "/crew", None, &jb).await;
    let trial = joins["crew"].as_array().unwrap().iter().find(|c| c["name"] == json!("bob")).expect("the trial life joined");
    assert_eq!(trial["scope"], json!(format!("{u}/f:ops/r:exp-bob-1")), "the trial life stood in the room: {trial}");
    let (_, worn) = knock(port, "GET", "/wear?component=bob.v0.graph", None, &jb).await;
    assert_eq!(worn["words"], json!("bob.v0.graph is worn by no body now"), "the trial's wear closed when it stopped: {worn}");
    println!("proposal · {}", &words[..words.len().min(160)]);

    // ---- 4. THE PROMOTION (L2): the version, the seat on the floor, bob's life seated from the shelf
    let (s, p) = knock(port, "POST", "/experiments/promote", Some(&json!({"experiment_id": xid, "at": "f:ops"})), &jb).await;
    assert_eq!(s, 202, "{p}");
    assert_eq!((p["level"].as_str(), p["version"].as_i64(), p["at"].as_str()), (Some("L2"), Some(1), Some(format!("{u}/f:ops").as_str())));
    let pask = p["held"].as_str().unwrap().to_string();
    knock(port, "POST", "/confirm", Some(&json!({"ask_id": pask, "approve": true})), &jb).await;
    let done = wait_for(port, &format!("/ask/{pask}"), &jb_wire, Duration::from_secs(30), |v| v["status"] == json!("replied")).await;
    assert!(done["reply"].as_str().unwrap().starts_with("Done, on your word: bob.template is version 1 on the shelf"), "{done}");
    let (_, shelf) = knock(port, "GET", "/services?kind=template", None, &jb).await;
    let t = shelf["services"].as_array().unwrap().iter().find(|s| s["name"] == json!("bob.template")).expect("bob.template on the shelf");
    assert_eq!((t["version"].as_i64(), t["manifest"]["kind"].as_str()), (Some(1), Some("agent")));
    let (_, seats) = knock(port, "GET", "/seats", None, &jb).await;
    assert_eq!((seats["seats"][0]["name"].as_str(), seats["seats"][0]["state"].as_str(), seats["seats"][0]["at_path"].as_str()),
               (Some("bob"), Some("active"), Some(format!("{u}/f:ops").as_str())));
    let (_, mine) = knock(port, "GET", "/drafts", None, &jb).await;
    assert!(mine["drafts"].as_array().unwrap().is_empty(), "the draft is spent: {mine}");
    let bodies = wait_for(port, "/bodies", &jb_wire, Duration::from_secs(120), |v| {
        v["bodies"].as_array().is_some_and(|a| a.iter().any(|b| b["name"] == json!("bob") && b["state"] == json!("alive")))
    })
    .await;
    let bob = bodies["bodies"].as_array().unwrap().iter().find(|b| b["name"] == json!("bob")).unwrap();
    assert_eq!(bob["kind"], json!("agent"));
    let crew = wait_for(port, "/crew", &jb_wire, Duration::from_secs(60), |v| {
        v["crew"].as_array().is_some_and(|a| a.iter().any(|c| c["name"] == json!("bob") && c["alive"] == json!(true) && c["scope"] == json!(format!("{u}/f:ops"))))
    })
    .await;
    let life = crew["crew"].as_array().unwrap().iter().find(|c| c["name"] == json!("bob")).unwrap()["lives"].as_i64();
    assert_eq!(life, Some(2), "the trial was life 1 — the same self: {crew}");
    let (_, worn) = knock(port, "GET", "/wear?component=bob.template", None, &jb).await;
    assert_eq!(worn["worn_by"][0]["version"], json!(1), "the wear table follows the next life: {worn}");
    // bob serves: an ask addressed to it is answered by its echo graph
    let (s, a) = knock(port, "POST", "/ask", Some(&json!({"text": "bob, hello from the owner"})), &jb).await;
    assert_eq!(s, 201, "{a}");
    let aid = a["id"].as_str().or_else(|| a["ids"][0].as_str()).unwrap_or_else(|| panic!("an ask id: {a}")).to_string();
    let served = wait_for(port, &format!("/ask/{aid}"), &jb_wire, Duration::from_secs(60), |v| v["status"] == json!("replied")).await;
    assert_eq!(served["reply"], json!("bob, hello from the owner"), "{served}"); // the echo keeps every word
    println!("promotion · bob seated on f:ops, life {life:?}, serving");

    // ---- 5. THE LADDER: a crew body holds no seat; the grave takes a rested body only; rest bob at L2 → stopped whole
    let (s, r) = knock(port, "POST", "/bodies/rest", Some(&json!({"name": "echo"})), &jb).await;
    assert_eq!(s, 400, "{r}");
    assert!(r["error"].as_str().unwrap().contains("echo holds no seat this kernel wrote"), "{r}");
    let (s, r) = knock(port, "POST", "/bodies/decommission", Some(&json!({"name": "bob"})), &jb).await;
    assert_eq!(s, 400, "{r}");
    assert!(r["error"].as_str().unwrap().contains("rest it first; the grave takes a rested body"), "{r}");
    let (s, r) = knock(port, "POST", "/bodies/rest", Some(&json!({"name": "bob"})), &jb).await;
    assert_eq!(s, 202, "{r}");
    let rask = r["held"].as_str().unwrap().to_string();
    knock(port, "POST", "/confirm", Some(&json!({"ask_id": rask, "approve": true})), &jb).await;
    let done = wait_for(port, &format!("/ask/{rask}"), &jb_wire, Duration::from_secs(30), |v| v["status"] == json!("replied")).await;
    assert!(done["reply"].as_str().unwrap().starts_with("Done, on your word: bob is at rest — its life stopped at a safe boundary"), "{done}");
    wait_for(port, "/bodies", &jb_wire, Duration::from_secs(60), |v| {
        v["bodies"].as_array().is_some_and(|a| a.iter().any(|b| b["name"] == json!("bob") && b["state"] == json!("rested")))
    })
    .await;
    let (_, seats) = knock(port, "GET", "/seats", None, &jb).await;
    assert_eq!(seats["seats"][0]["state"], json!("rested"));
    let (s, r) = knock(port, "POST", "/bodies/rest", Some(&json!({"name": "bob"})), &jb).await;
    assert_eq!(s, 400, "{r}");
    assert!(r["error"].as_str().unwrap().contains("bob is rested — only an active body rests"), "{r}");
    println!("ladder · bob rested on the owner's word; its self kept");

    lit.stop().await;
}
