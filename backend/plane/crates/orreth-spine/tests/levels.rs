// PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch Phase 8 THE WORKSHOP sp1, THE PATH: the levels' proof on the rig · 2026-10-05
//! THE PATH'S PROOF (canon 0010 lock 2 · 0005 Phase 8 sp1), on the dev rig, by name:
//!
//!     cargo test -p orreth-spine --features bridge --test levels -- --nocapture
//!
//! One Rust kernel lit alone with a two-seat crew whose manifest DECLARES a floor and seats
//! the echo on it: the universe's level row stands at light in its declared mode (`SPINE_MODE`
//! unset → dev) and the floor is declared by the manifest; the echo is born with the floor's
//! path as its `SPINE_SCOPE`, joins at the desk AT THE FLOOR (its join, its lease, its seat
//! row wear the floor), and is seen from the universe (the crew door, the residents, the
//! roster — one world, one picture) with its level on the card; an ask from the universe
//! names it and is served; `/levels` rolls the floor's body up to the universe; the cascade at
//! the floor folds two tiers and is content-addressed; a person's seat may not open a level
//! (govern) and the owner's word holds it at L2 — a no leaves nothing, a yes stands a room
//! whose fact is on the feed; a looser mode is refused in words; an experiment room opens
//! only on a floor. With no rig it prints "rails not up — skipped by name" and passes green.

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

async fn knock(
    port: u16,
    method: &str,
    path: &str,
    body: Option<&Value>,
    headers: &[(&str, &str)],
) -> (u16, Value) {
    let mut s = TcpStream::connect(("127.0.0.1", port))
        .await
        .expect("the door answers");
    let body = body.map(|b| b.to_string()).unwrap_or_default();
    let extra: String = headers
        .iter()
        .map(|(k, v)| format!("{k}: {v}\r\n"))
        .collect();
    let req = format!(
        "{method} {path} HTTP/1.1\r\nHost: 127.0.0.1:{port}\r\nConnection: close\r\n{extra}content-type: \
         application/json\r\ncontent-length: {}\r\n\r\n{body}",
        body.len()
    );
    s.write_all(req.as_bytes()).await.unwrap();
    let mut raw = Vec::new();
    let _ = tokio::time::timeout(Duration::from_secs(10), s.read_to_end(&mut raw)).await;
    let text = String::from_utf8_lossy(&raw).to_string();
    let status: u16 = text
        .split_whitespace()
        .nth(1)
        .and_then(|c| c.parse().ok())
        .unwrap_or(0);
    let body = text
        .split_once("\r\n\r\n")
        .map(|(_, b)| b.to_string())
        .unwrap_or_default();
    (status, serde_json::from_str(&body).unwrap_or(Value::Null))
}

/// The ceremony: enroll, confirm with the first code, sit with the next. Returns the wire.
async fn sit(port: u16, person: &str, owner: Option<&str>) -> String {
    let h: Vec<(&str, &str)> = owner
        .map(|w| vec![("authorization", w)])
        .unwrap_or_default();
    let (s, b) = knock(port, "POST", "/enroll", Some(&json!({"person": person})), &h).await;
    assert_eq!(s, 201, "enroll {person}: {b}");
    let secret = b["secret"].as_str().unwrap().to_string();
    let code = proof::totp(&secret, proof_live::now_unix()).unwrap();
    let (s, b) = knock(
        port,
        "POST",
        "/enroll/confirm",
        Some(&json!({"person": person, "code": code})),
        &[],
    )
    .await;
    assert_eq!(s, 200, "confirm {person}: {b}");
    let code = proof::totp(&secret, proof_live::now_unix()).unwrap();
    let (s, b) = knock(
        port,
        "POST",
        "/seat",
        Some(&json!({"person": person, "code": code})),
        &[],
    )
    .await;
    assert_eq!(s, 201, "seat {person}: {b}");
    format!("Bearer {}", b["wire"].as_str().unwrap())
}

/// Poll a door until `done` says so (or the wait runs out — then the last answer is asserted on).
async fn wait_for(
    port: u16,
    path: &str,
    wire: &str,
    within: Duration,
    done: impl Fn(&Value) -> bool,
) -> Value {
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

fn level_row<'a>(levels: &'a Value, path: &str) -> &'a Value {
    levels["levels"]
        .as_array()
        .unwrap()
        .iter()
        .find(|l| l["path"] == json!(path))
        .unwrap_or_else(|| panic!("no level {path} in {levels}"))
}

#[tokio::test]
async fn the_path_a_floor_declared_a_body_seated_on_it_seen_from_the_universe_and_a_room_opened_at_l2() {
    if !rig_up("the_path_a_floor_declared_a_body_seated_on_it_seen_from_the_universe_and_a_room_opened_at_l2") {
        return;
    }
    if port_open(4600) || port_open(4601) {
        println!("a kernel holds :4600 or the reference :4601 — the levels proof refuses to run beside a live rig (stop it: scripts/dev.sh kernel stop · scripts/dev.sh reference stop)");
        return;
    }
    let tok = token_hex(3);
    let u = format!("u:path-{tok}");
    let floor = format!("{u}/f:ops");
    let world = World {
        scope: u.clone(),
        ns: format!("t{tok}"),
        pg_dsn: rails::pg_dsn(),
        rabbit_url: rails::rabbit_url(),
        kafka: rails::kafka_bootstrap(),
    };
    let home = std::env::temp_dir().join(format!("orreth-levels-{tok}"));
    std::fs::create_dir_all(home.join("agents")).unwrap();
    std::env::set_var("ORRETH_HOME", &home);
    std::env::set_var("SPINE_KERNEL_HOME", home.join("kernel"));
    std::env::set_var("SPINE_SERVICES_HOME", home.join("services"));
    std::env::set_var("SPINE_GATEWAY", "http://127.0.0.1:1"); // the gateway dark: the fake mind, no spend
    std::env::set_var("SPINE_MIND_CHECK_S", "3600");
    std::env::set_var("SPINE_TOOL_CHECK_S", "3600");
    std::env::remove_var("SPINE_MODE"); // the universe opens dev
    // a two-seat crew: the librarian at the universe, the echo ON THE FLOOR the manifest declares
    let crew = home.join("crew.v0.json");
    std::fs::write(
        &crew,
        json!({"format": "orreth-crew/1",
               "levels": [{"at": "f:ops", "words": "the operations floor"}],
               "seats": [
                   {"template": "templates/librarian-resident.v0.json"},
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

    // ---- 1. the universe's level stands at light (dev); the floor is declared by the manifest
    let (s, w) = knock(port, "GET", "/world", None, &jb).await;
    assert_eq!(s, 200, "{w}");
    assert_eq!(w["mode"], json!("dev"), "the world card says the mode: {w}");
    let (s, l) = knock(port, "GET", "/levels", None, &jb).await;
    assert_eq!(s, 200, "{l}");
    assert_eq!(l["universe"], json!(u));
    assert_eq!(l["mode"], json!("dev"));
    let uni = level_row(&l, &u);
    assert_eq!((uni["level"].as_str(), uni["mode"].as_str(), uni["opened_by"].as_str()), (Some("universe"), Some("dev"), Some("the kernel")));
    let fl = level_row(&l, &floor);
    assert_eq!((fl["level"].as_str(), fl["mode"].as_str(), fl["opened_by"].as_str(), fl["parent"].as_str()),
               (Some("floor"), Some("dev"), Some("the crew manifest"), Some(u.as_str())));
    assert_eq!(fl["words"], json!(format!("floor ops of universe path-{tok}")));
    println!("levels · the universe stands dev; {} declared by the crew manifest", fl["words"]);

    // ---- 2. the echo is born on the floor: joined AT the floor, seen from the universe with its level
    let crew_view = wait_for(port, "/crew", &jb_wire, Duration::from_secs(240), |v| {
        v["crew"].as_array().is_some_and(|a| {
            a.iter().any(|c| c["name"] == json!("echo") && c["alive"] == json!(true))
                && a.iter().any(|c| c["name"] == json!("librarian") && c["alive"] == json!(true))
        })
    })
    .await;
    let echo = crew_view["crew"].as_array().unwrap().iter().find(|c| c["name"] == json!("echo")).unwrap();
    let lib = crew_view["crew"].as_array().unwrap().iter().find(|c| c["name"] == json!("librarian")).unwrap();
    assert_eq!(echo["scope"], json!(floor), "the echo's card wears the floor: {echo}");
    assert_eq!(lib["scope"], json!(u), "the librarian's card wears the universe: {lib}");
    let (_, residents) = knock(port, "GET", "/residents", None, &jb).await;
    let names: Vec<&str> = residents["residents"].as_array().unwrap().iter().filter_map(|r| r["name"].as_str()).collect();
    assert!(names.contains(&"echo") && names.contains(&"librarian"), "{residents}");
    // the desk's rows and the seat row wear the floor
    let (_, desk) = knock(port, "GET", "/join", None, &jb).await;
    let echo_join = desk.as_array().or_else(|| desk["joins"].as_array()).unwrap().iter()
        .find(|j| j["name"] == json!("echo")).cloned().unwrap_or(Value::Null);
    assert_eq!(echo_join["status"], json!("done"), "{desk}");
    let g = orreth_spine::ground::Ground::connect(&world.pg_dsn).await.unwrap();
    let row = g.client().query_one("SELECT scope FROM spine_desk WHERE name = 'echo' AND (scope = $1 OR scope LIKE $1 || '/%') ORDER BY asked_at DESC LIMIT 1", &[&u]).await.unwrap();
    assert_eq!(row.get::<_, String>(0), floor, "the desk's row wears the floor");
    let row = g.client().query_one("SELECT scope FROM spine_leases WHERE name = 'echo' AND (scope = $1 OR scope LIKE $1 || '/%') LIMIT 1", &[&u]).await.unwrap();
    assert_eq!(row.get::<_, String>(0), floor, "the lease wears the floor");
    let row = g.client().query_one("SELECT count(*) FROM spine_seats WHERE role = 'body' AND scope = $1", &[&floor]).await.unwrap();
    assert!(row.get::<_, i64>(0) >= 1, "the body's seat row wears the floor");
    println!("levels · the echo joined at {floor}; the crew door at the universe sees it with its level");

    // ---- 3. an ask from the universe names the floor's body and is served; the roll-up folds it up
    let (s, ses) = knock(port, "POST", "/sessions", Some(&json!({"person": "did:orreth:person:jb"})), &jb).await;
    let sid = ses["session_id"].as_str().map(str::to_string);
    assert!(s == 201 || s == 200, "a session opens: {s} {ses}");
    let (s, a) = knock(port, "POST", "/ask", Some(&json!({"text": "echo, say the word HERON once", "to": ["echo"], "person": "did:orreth:person:jb", "session": sid})), &jb).await;
    assert_eq!(s, 201, "{a}");
    let aid = a["ids"][0].as_str().unwrap_or_else(|| panic!("the ask door's ids: {a}")).to_string();
    let v = wait_for(port, &format!("/ask/{aid}"), &jb_wire, Duration::from_secs(120), |v| v["status"] == json!("replied")).await;
    assert!(v["reply"].as_str().unwrap_or_default().contains("HERON"), "{v}");
    let l = wait_for(port, "/levels", &jb_wire, Duration::from_secs(30), |v| {
        v["levels"].as_array().is_some_and(|a| a.iter().any(|x| x["path"] == json!(floor) && x["here"]["asks_served"].as_i64() == Some(1)))
    })
    .await;
    let fl = level_row(&l, &floor);
    let uni = level_row(&l, &u);
    assert_eq!(fl["here"]["bodies"], json!(1));
    assert_eq!(uni["here"]["bodies"], json!(1));
    assert_eq!(uni["rolled"]["bodies"], json!(2), "the universe rolls the floor's body up: {uni}");
    assert_eq!(uni["rolled"]["asks_served"], json!(1));
    assert_eq!(uni["rolled"]["bundle"]["compliance"], json!("clean"));
    println!("levels · the floor's echo served an ask from the universe; the universe rolls up 2 bodies, 1 ask");

    // ---- 4. the cascade at the floor: two tiers, content-addressed, the policy's rules the universe's floors
    let (s, c) = knock(port, "GET", &format!("/levels/context?path={floor}"), None, &jb).await;
    assert_eq!(s, 200, "{c}");
    assert_eq!(c["as_of"].as_array().unwrap().len(), 2);
    assert_eq!(c["mode"], json!("dev"));
    assert!(c["id"].as_str().unwrap().starts_with("sha256:"));
    assert!(!c["floors"].as_array().unwrap().is_empty(), "the policy sheet's rules are the universe's floors");
    let (_, c2) = knock(port, "GET", &format!("/levels/context?path={floor}"), None, &jb).await;
    assert_eq!(c["id"], c2["id"], "the same chain, the same id");
    let (s, c3) = knock(port, "GET", &format!("/levels/context?path={u}/f:nowhere"), None, &jb).await;
    assert_eq!(s, 404, "{c3}");
    assert_eq!(c3["error"], json!(format!("{u}/f:nowhere is not open here")));

    // ---- 5. a level opens on a GOVERNING seat's word: quinn's seat may not; the owner's hold at L2
    let open = json!({"parent": floor, "level": "room", "name": "bob", "experiment": true, "person": "did:orreth:person:jb"});
    let (s, r) = knock(port, "POST", "/levels/open", Some(&open), &quinn).await;
    assert_ne!(s, 202, "a person's seat opened a level: {r}");
    let (s, r) = knock(port, "POST", "/levels/open", Some(&open), &jb).await;
    assert_eq!(s, 202, "{r}");
    assert_eq!((r["level"].as_str(), r["class"].as_str(), r["path"].as_str()), (Some("L2"), Some("consequential"), Some(format!("{floor}/r:bob").as_str())));
    let held = r["held"].as_str().unwrap().to_string();
    let (_, l) = knock(port, "GET", "/levels", None, &jb).await;
    assert!(l["levels"].as_array().unwrap().iter().all(|x| x["path"] != json!(format!("{floor}/r:bob"))), "nothing stands before the yes");
    // a no: nothing stands, recorded
    let (s, r) = knock(port, "POST", "/confirm", Some(&json!({"ask_id": held, "approve": false})), &jb).await;
    assert_eq!(s, 202, "{r}");
    let (_, h) = knock(port, "GET", &format!("/ask/{held}"), None, &jb).await;
    assert_eq!(h["status"], json!("cancelled"), "{h}");
    let (_, l) = knock(port, "GET", "/levels", None, &jb).await;
    assert!(l["levels"].as_array().unwrap().iter().all(|x| x["path"] != json!(format!("{floor}/r:bob"))), "a no stands nothing");
    // a yes: the room stands, an experiment room, its fact on the feed
    let mut feed = lit.feed.subscribe();
    let (s, r) = knock(port, "POST", "/levels/open", Some(&open), &jb).await;
    assert_eq!(s, 202, "{r}");
    let held = r["held"].as_str().unwrap().to_string();
    let (s, r) = knock(port, "POST", "/confirm", Some(&json!({"ask_id": held, "approve": true})), &jb).await;
    assert_eq!(s, 202, "{r}");
    let (_, h) = knock(port, "GET", &format!("/ask/{held}"), None, &jb).await;
    assert_eq!(h["status"], json!("replied"), "{h}");
    assert!(h["reply"].as_str().unwrap().contains(&format!("room bob on floor ops of universe path-{tok} is open (dev) — an experiment room")), "{h}");
    let (_, l) = knock(port, "GET", "/levels", None, &jb).await;
    let room = level_row(&l, &format!("{floor}/r:bob"));
    assert_eq!((room["level"].as_str(), room["mode"].as_str(), room["experiment"].as_bool(), room["opened_by"].as_str()),
               (Some("room"), Some("dev"), Some(true), Some("did:orreth:person:jb")));
    assert_eq!(room["ask"], json!(held));
    let t0 = Instant::now();
    let mut seen = false;
    while t0.elapsed() < Duration::from_secs(30) && !seen {
        match tokio::time::timeout(Duration::from_secs(5), feed.recv()).await {
            Ok(Ok(n)) => {
                let text = n.to_string();
                seen = text.contains("orreth.level.opened.v1") && text.contains(&format!("{floor}/r:bob"));
            }
            _ => {}
        }
    }
    assert!(seen, "the level's fact reached the feed");
    println!("levels · quinn's seat could not open a level; jb's no stood nothing; jb's yes opened an experiment room, its fact on the feed");

    // ---- 6. the refusals, in words: a looser mode · an experiment room off a floor · a room off a floor · already open
    let (s, r) = knock(port, "POST", "/levels/open", Some(&json!({"parent": u, "level": "floor", "name": "prodfloor", "mode": "prod"})), &jb).await;
    assert_eq!(s, 202, "{r}");
    let held = r["held"].as_str().unwrap().to_string();
    let (s, _) = knock(port, "POST", "/confirm", Some(&json!({"ask_id": held, "approve": true})), &jb).await;
    assert_eq!(s, 202);
    let (s, r) = knock(port, "POST", "/levels/open", Some(&json!({"parent": format!("{u}/f:prodfloor"), "level": "room", "name": "loose", "mode": "dev"})), &jb).await;
    assert_eq!(s, 400, "{r}");
    assert!(r["error"].as_str().unwrap().starts_with("mode only tightens down the path"), "{r}");
    let (s, r) = knock(port, "POST", "/levels/open", Some(&json!({"parent": u, "level": "floor", "name": "lab", "experiment": true})), &jb).await;
    assert_eq!(s, 400, "{r}");
    assert_eq!(r["error"], json!("only a room opens as an experiment room"));
    let (s, r) = knock(port, "POST", "/levels/open", Some(&json!({"parent": u, "level": "room", "name": "bob"})), &jb).await;
    assert_eq!(s, 400, "{r}");
    assert_eq!(r["error"], json!(format!("a room opens on a floor — {u} is a universe")));
    let (s, r) = knock(port, "POST", "/levels/open", Some(&json!({"parent": u, "level": "floor", "name": "ops"})), &jb).await;
    assert_eq!(s, 400, "{r}");
    assert_eq!(r["error"], json!(format!("floor ops of universe path-{tok} is already open")));
    let (_, c) = knock(port, "GET", &format!("/levels/context?path={u}/f:prodfloor"), None, &jb).await;
    assert_eq!(c["mode"], json!("prod"), "the fold tightens: {c}");
    println!("levels · the refusals in words: a looser mode, an experiment floor, a room off a floor, a floor twice");

    lit.stop().await;
    // the proof's world leaves the ground, its levels with it (prune reads every level)
    let mut g = orreth_spine::ground::Ground::connect(&world.pg_dsn).await.unwrap();
    let gone = orreth_spine::ground::prune_scope(&mut g, &u).await.unwrap();
    assert!(gone.iter().any(|(t, _)| t == "spine_levels"), "the levels were pruned with the world: {gone:?}");
    let left: i64 = g.client().query_one("SELECT count(*) FROM spine_levels WHERE scope = $1", &[&u]).await.unwrap().get(0);
    assert_eq!(left, 0);
    let _ = std::fs::remove_dir_all(&home);
}
