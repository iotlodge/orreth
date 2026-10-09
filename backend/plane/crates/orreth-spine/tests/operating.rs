// PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch Phase 8 THE WORKSHOP sp5, THE OPERATING STATE: the proof on the rig · 2026-10-08
// Amended: Claude Fable 5.1 (claude-fable-5-1) — THE GROUND CONNECTIONS CURE (2026-10-08): the kernel's sixth watch beside the five · 2026-10-08
//! THE OPERATING STATE'S PROOF (canon 0010 §7 · 0005 Phase 8 sp5), on the dev rig, by name:
//!
//!     cargo test -p orreth-spine --features bridge --test operating -- --nocapture
//!
//! One Rust kernel lit alone with a three-seat crew (the librarian, the echo, the grader): at light
//! the kernel's five measurement watches stand (added by the kernel, unknown, none red) and THE
//! OPERATING STATE intention stands beside Resiliency with its five watches named; `/measurements`
//! reads every measurement unknown — never a silent 1.0; the echo serves an ask (Recall and
//! Efficiency measure it); a thumb through `/feedback` lands (Experience 1.0; a thumb on nothing is
//! refused in words); THE GRADE BEAT hands the echo's reply to the grader under a GRADING marker
//! beneath the reply's own ask (the grader's mind is the fake one here — its reply keeps no form, so
//! no verdict is written and Trust stays unknown, said in its journey); `/summon` takes the grader
//! (summonable by declaration) into the session's crew and refuses the echo in words; `/includes`
//! reads it; the Monitor's snapshot carries the five. With no rig it prints "rails not up — skipped
//! by name" and passes green.

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

#[tokio::test]
async fn the_operating_state_is_measured_watched_and_the_grader_hears_live_replies() {
    if !rig_up("the_operating_state_is_measured_watched_and_the_grader_hears_live_replies") {
        return;
    }
    if port_open(4600) || port_open(4601) {
        println!("a kernel holds :4600 or the reference :4601 — the operating proof refuses to run beside a live rig (stop it: scripts/dev.sh kernel stop · scripts/dev.sh reference stop)");
        return;
    }
    let tok = token_hex(3);
    let u = format!("u:op-{tok}");
    let world = World {
        scope: u.clone(),
        ns: format!("t{tok}"),
        pg_dsn: rails::pg_dsn(),
        rabbit_url: rails::rabbit_url(),
        kafka: rails::kafka_bootstrap(),
    };
    let home = std::env::temp_dir().join(format!("orreth-operating-{tok}"));
    std::fs::create_dir_all(home.join("agents")).unwrap();
    std::env::set_var("ORRETH_HOME", &home);
    std::env::set_var("SPINE_KERNEL_HOME", home.join("kernel"));
    std::env::set_var("SPINE_SERVICES_HOME", home.join("services"));
    std::env::set_var("SPINE_GATEWAY", "http://127.0.0.1:1");
    std::env::set_var("SPINE_MIND_CHECK_S", "3600");
    std::env::set_var("SPINE_TOOL_CHECK_S", "3600");
    std::env::remove_var("SPINE_MODE");
    std::env::remove_var("SPINE_GRADE_LIVE");
    let crew = home.join("crew.v0.json");
    std::fs::write(
        &crew,
        json!({"format": "orreth-crew/1",
               "seats": [{"template": "templates/librarian-resident.v0.json"},
                         {"template": "templates/echo-resident.v0.json"},
                         {"template": "templates/firmware-grader.v0.json"}]})
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

    // ---- 1. at light: the five watches (the kernel's, unknown, none red) and THE OPERATING STATE beside Resiliency
    let ints = wait_for(port, "/intentions", &jb_wire, Duration::from_secs(60), |v| {
        v["intentions"].as_array().is_some_and(|a| a.iter().filter(|i| i["kind"] == json!("kernel")).count() >= 2)
    })
    .await;
    let ops = ints["intentions"].as_array().unwrap().iter().find(|i| i["serves"] == json!("operating-state")).expect("the Operating State stands");
    assert_eq!(ops["watches"], json!(["trust", "recall", "efficiency", "experience", "cost"]), "{ops}");
    assert_eq!(ops["runner"], json!("critic"));
    let res = ints["intentions"].as_array().unwrap().iter().find(|i| i["serves"] == json!("resiliency")).unwrap();
    assert!(res["watches"].is_null());
    // the ground connections cure (2026-10-08): the kernel's SIXTH watch, the ground's, stands beside the five
    let snap = wait_for(port, "/monitor", &jb_wire, Duration::from_secs(60), |v| {
        v["watches"].as_array().is_some_and(|a| a.iter().filter(|w| w["added_by"] == json!("the kernel")).count() == 7) // the five, the ground's, the key-check's (Phase 8 sp6)
    })
    .await;
    let kernels: Vec<&Value> = snap["watches"].as_array().unwrap().iter().filter(|w| w["added_by"] == json!("the kernel")).collect();
    let ground = kernels.iter().find(|w| w["metric"] == json!("ground_connections")).expect("the ground's watch stands");
    assert!(ground["op"] == json!(">=") && ground["red"] == json!(false) && ground["value"].as_i64().is_some_and(|n| n >= 1), "{ground}");
    let five: Vec<&Value> = kernels.iter().copied().filter(|w| w["metric"] != json!("ground_connections") && w["metric"] != json!("key_checks_failed")).collect();
    assert_eq!(five.len(), 5);
    assert!(five.iter().all(|w| w["red"] == json!(false) && w["value"].is_null() && w["op"] == json!("<")), "{five:?}");
    assert!(five.iter().any(|w| w["reads"].as_str().unwrap() == "red when trust < 1.0 · now unknown (nothing to measure yet) → green"), "{five:?}");
    assert!(snap["measurements"]["trust"]["value"].is_null() && snap["values"]["cost"].is_null(), "{}", snap["measurements"]);
    let (s, m) = knock(port, "GET", "/measurements", None, &jb).await;
    assert_eq!(s, 200, "{m}");
    assert_eq!(m["order"], json!(["trust", "recall", "efficiency", "experience", "cost"]));
    assert_eq!(m["measurements"]["experience"]["words"], json!("experience: unknown — no thumbs given yet (never a silent 1.0)"));
    println!("light · the five watches stand, unknown; THE OPERATING STATE beside Resiliency");

    // ---- 2. a served ask: Recall and Efficiency measure it; a thumb lands (Experience); a thumb on nothing refuses
    wait_for(port, "/crew", &jb_wire, Duration::from_secs(240), |v| {
        v["crew"].as_array().is_some_and(|a| a.iter().any(|c| c["name"] == json!("echo") && c["alive"] == json!(true))
            && a.iter().any(|c| c["name"] == json!("grader") && c["alive"] == json!(true)))
    })
    .await;
    let (s, a) = knock(port, "POST", "/ask", Some(&json!({"text": "echo, the moon is round"})), &jb).await;
    assert_eq!(s, 201, "{a}");
    let aid = a["id"].as_str().or_else(|| a["ids"][0].as_str()).unwrap().to_string();
    wait_for(port, &format!("/ask/{aid}"), &jb_wire, Duration::from_secs(60), |v| v["status"] == json!("replied")).await;
    let (s, r) = knock(port, "POST", "/feedback", Some(&json!({"ask_id": "ask_nowhere", "sign": 1})), &jb).await;
    assert_eq!(s, 400, "{r}");
    assert_eq!(r["error"], json!("no such ask here"));
    let (s, r) = knock(port, "POST", "/feedback", Some(&json!({"ask_id": aid, "sign": 1, "words": "plain and whole"})), &jb).await;
    assert_eq!(s, 201, "{r}");
    assert_eq!(r["sign"], json!(1));
    let (_, m) = knock(port, "GET", "/measurements", None, &jb).await;
    assert_eq!(m["measurements"]["experience"]["value"], json!(1.0), "{}", m["measurements"]);
    assert_eq!(m["measurements"]["recall"]["value"], json!(1.0));
    assert_eq!(m["measurements"]["efficiency"]["value"], json!(1.0));
    println!("served · recall {} · efficiency {} · experience {}", m["measurements"]["recall"]["value"], m["measurements"]["efficiency"]["value"], m["measurements"]["experience"]["value"]);

    // ---- 3. THE GRADE BEAT: the echo's reply handed to the grader under a grading marker beneath the reply's own ask;
    //         the grader's fake mind keeps no form — no verdict, said; Trust stays unknown, never guessed
    let graded = wait_for(port, "/asks", &jb_wire, Duration::from_secs(120), |v| {
        v["asks"].as_array().is_some_and(|a| a.iter().any(|x| x["text"].as_str().is_some_and(|t| t.starts_with("grader, grade the reply")) && x["status"] == json!("replied")))
    })
    .await;
    let g = graded["asks"].as_array().unwrap().iter().find(|x| x["text"].as_str().is_some_and(|t| t.starts_with("grader, grade the reply"))).unwrap();
    let gid = g["ask_id"].as_str().unwrap().to_string();
    assert!(g["text"].as_str().unwrap().starts_with(&format!("grader, grade the reply {aid} by echo.")), "{g}");
    let (_, gv) = knock(port, "GET", &format!("/ask/{gid}"), None, &jb).await;
    let journey = gv["journey"].as_array().unwrap().iter().map(|j| j.as_str().unwrap_or_default()).collect::<Vec<_>>().join(" / ");
    assert!(journey.contains("routed to the event edge — a marker of kind grading asked for a response"), "{journey}");
    assert!(journey.contains(&format!("no verdict written on {aid} — my reply did not keep the form")), "{journey}");
    let (_, m) = knock(port, "GET", "/measurements", None, &jb).await;
    assert!(m["measurements"]["trust"]["value"].is_null(), "unknown, never guessed: {}", m["measurements"]["trust"]);
    println!("graded · the grader was asked under a grading marker; its fake mind kept no form — said");

    // ---- 4. SUMMON generalized: the grader (summonable by declaration) in; the echo refused in words; the includes read it
    let (s, r) = knock(port, "POST", "/summon", Some(&json!({"name": "echo", "session": "ses_x"})), &jb).await;
    assert_eq!(s, 400, "{r}");
    assert!(r["error"].as_str().unwrap().contains("does not declare it summonable"), "{r}");
    let (s, r) = knock(port, "POST", "/summon", Some(&json!({"name": "grader", "session": "ses_x"})), &jb).await;
    assert_eq!(s, 201, "{r}");
    assert!(r["words"].as_str().unwrap().starts_with("grader summoned — it joins this session's crew"), "{r}");
    let (_, inc) = knock(port, "GET", "/includes?session=ses_x", None, &jb).await;
    assert_eq!(inc["summoned"], json!(["grader"]));
    assert_eq!(inc["includes"], json!(["planner", "critic", "grader", "mitl"]));
    let (s, r) = knock(port, "POST", "/summon", Some(&json!({"name": "grader", "session": "ses_x", "summon": false})), &jb).await;
    assert_eq!(s, 201, "{r}");
    let (_, inc) = knock(port, "GET", "/includes?session=ses_x", None, &jb).await;
    assert_eq!(inc["summoned"], json!([]));
    println!("summon · the grader in and out of the session's crew on the owner's word; the echo refused in words");

    lit.stop().await;
}
