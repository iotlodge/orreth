// PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — THE GROUND CONNECTIONS CURE (JB's word 2026-10-08) · 2026-10-08
//! THE GROUND CONNECTIONS PROOF, on the dev rig, by name:
//!
//!     cargo test -p orreth-spine --features bridge --test connections -- --nocapture
//!
//! One Rust kernel lit alone with a two-seat crew. The finding this cures: the
//! crew of 11 idle held 22 ground connections (two per body, serving or not)
//! beside the kernel's 15, and the suite beside the lit kernel died of "too many
//! clients". What this proves: the crew IDLE leaves the ground holding the
//! kernel's lines alone (no line named for a body; the kernel's own a handful,
//! named — relay · dispatcher · beats · door); an ask served takes the body's
//! two lines (its serve line and its working memory's) and the idle release lets
//! them go; the Monitor counts the ground's lines (`values.ground_connections`),
//! the snapshot's `ground` card says the budget, and the kernel's sixth watch
//! stands beside the five. With no rig it prints "rails not up — skipped by
//! name"; beside a live kernel it refuses to run.

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

/// The ground's own count of the lines whose name starts with `prefix`.
async fn lines_named(g: &orreth_spine::ground::Ground, prefix: &str) -> i64 {
    let like = format!("{prefix}%");
    g.client()
        .query_one(
            "SELECT count(*) FROM pg_stat_activity WHERE datname = current_database() AND application_name LIKE $1",
            &[&like],
        )
        .await
        .unwrap()
        .get(0)
}

/// Every name the ground holds a line under, with its count — the assert's evidence.
async fn names_held(g: &orreth_spine::ground::Ground) -> String {
    g.client()
        .query(
            "SELECT application_name, count(*) FROM pg_stat_activity WHERE datname = current_database() GROUP BY 1 ORDER BY 1",
            &[],
        )
        .await
        .unwrap()
        .iter()
        .map(|r| format!("{} ×{}", r.get::<_, String>(0), r.get::<_, i64>(1)))
        .collect::<Vec<_>>()
        .join(" · ")
}

/// Wait until the ground's count for `prefix` satisfies `ok` (or say what it read).
async fn wait_lines(g: &orreth_spine::ground::Ground, prefix: &str, within: Duration, ok: impl Fn(i64) -> bool) -> i64 {
    let t0 = Instant::now();
    let mut n = lines_named(g, prefix).await;
    while t0.elapsed() < within && !ok(n) {
        tokio::time::sleep(Duration::from_millis(250)).await;
        n = lines_named(g, prefix).await;
    }
    n
}

#[tokio::test]
async fn the_crew_idle_leaves_the_ground_holding_the_kernels_lines_alone_and_a_serve_takes_two() {
    if !rig_up("the_crew_idle_leaves_the_ground_holding_the_kernels_lines_alone_and_a_serve_takes_two") {
        return;
    }
    if port_open(4600) || port_open(4601) {
        println!("a kernel holds :4600 or the reference :4601 — the connections proof refuses to run beside a live rig (stop it: scripts/dev.sh kernel stop · scripts/dev.sh reference stop)");
        return;
    }
    let tok = token_hex(3);
    let u = format!("u:lines-{tok}");
    let world = World {
        scope: u.clone(),
        ns: format!("t{tok}"),
        pg_dsn: rails::pg_dsn(),
        rabbit_url: rails::rabbit_url(),
        kafka: rails::kafka_bootstrap(),
    };
    let home = std::env::temp_dir().join(format!("orreth-lines-{tok}"));
    std::fs::create_dir_all(home.join("agents")).unwrap();
    std::env::set_var("ORRETH_HOME", &home);
    std::env::set_var("SPINE_KERNEL_HOME", home.join("kernel"));
    std::env::set_var("SPINE_SERVICES_HOME", home.join("services"));
    std::env::set_var("SPINE_GATEWAY", "http://127.0.0.1:1"); // the gateway dark: the fake mind, no spend
    std::env::set_var("SPINE_MIND_CHECK_S", "3600");
    std::env::set_var("SPINE_TOOL_CHECK_S", "3600");
    std::env::set_var("SPINE_BODY_IDLE_S", "3"); // a body lets its line go three seconds after its last serve
    std::env::set_var("SPINE_POOL_IDLE_S", "2"); // the doors' idle lines shed on the next sweep
    std::env::remove_var("SPINE_GROUND_CONNECTIONS");
    std::env::remove_var("SPINE_GROUND_RESERVE");
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
    let jb = [("authorization", jb_wire.as_str())];

    // ---- 1. both bodies alive
    wait_for(port, "/crew", &jb_wire, Duration::from_secs(240), |v| {
        v["crew"].as_array().is_some_and(|a| {
            a.iter().any(|c| c["name"] == json!("echo") && c["alive"] == json!(true))
                && a.iter().any(|c| c["name"] == json!("librarian") && c["alive"] == json!(true))
        })
    })
    .await;
    let mut g = orreth_spine::ground::Ground::connect_as(&world.pg_dsn, "the connections proof").await.unwrap();

    // ---- 2. the crew IDLE: no line named for a body stands on the ground (their birth lines closed, their
    // leases renewed on a line that opens and closes) — the kernel's own are a named handful
    let bodies_idle = wait_lines(&g, "orreth body ", Duration::from_secs(20), |n| n == 0).await;
    assert_eq!(bodies_idle, 0, "an idle crew holds no ground line");
    // the doors' lines this proof's own knocks opened are SHED once idle (SPINE_POOL_IDLE_S, on the sweep)
    let doors_idle = wait_lines(&g, "orrethd door", Duration::from_secs(20), |n| n == 0).await;
    assert_eq!(doors_idle, 0, "a kernel nobody knocks on holds no door lines");
    let kernel_lines = lines_named(&g, "orrethd").await;
    assert!(kernel_lines >= 2 && kernel_lines <= 4, "the kernel's standing lines: the relay, the dispatcher, the beats' two at most — read {kernel_lines}: {}", names_held(&g).await);
    for name in ["orrethd relay", "orrethd dispatcher", "orrethd beat"] {
        assert!(lines_named(&g, name).await >= 1, "the ground names the kernel's {name}");
    }
    let crew_still_alive = knock(port, "GET", "/crew", None, &jb).await.1;
    assert!(crew_still_alive["crew"].as_array().unwrap().iter().all(|c| c["alive"] == json!(true)), "{crew_still_alive}");
    println!("connections · the crew of two idle: 0 body lines; the kernel holds {kernel_lines} named lines");

    // ---- 3. an ask: the echo serves, its line taken (two: the serve line and the working memory's), then let go
    let (s, ses) = knock(port, "POST", "/sessions", Some(&json!({"person": "did:orreth:person:jb"})), &jb).await;
    let sid = ses["session_id"].as_str().map(str::to_string);
    assert!(s == 201 || s == 200, "a session opens: {s} {ses}");
    let (s, a) = knock(port, "POST", "/ask", Some(&json!({"text": "echo, say the word HERON once", "to": ["echo"], "person": "did:orreth:person:jb", "session": sid})), &jb).await;
    assert_eq!(s, 201, "{a}");
    let aid = a["ids"][0].as_str().unwrap_or_else(|| panic!("the ask door's ids: {a}")).to_string();
    let v = wait_for(port, &format!("/ask/{aid}"), &jb_wire, Duration::from_secs(120), |v| v["status"] == json!("replied")).await;
    assert!(v["reply"].as_str().unwrap_or_default().contains("HERON"), "{v}");
    let serving = wait_lines(&g, "orreth body echo", Duration::from_secs(3), |n| n == 2).await;
    assert_eq!(serving, 2, "a body that just served holds its serve line and its working memory's for the idle window");
    let released = wait_lines(&g, "orreth body echo", Duration::from_secs(15), |n| n == 0).await;
    assert_eq!(released, 0, "the line let go after SPINE_BODY_IDLE_S of nothing served");
    println!("connections · the echo served HERON on two lines and let them go within the idle window");

    // ---- 4. the Monitor: the ground's lines counted, the budget said, the kernel's sixth watch beside the five
    let (s, m) = knock(port, "GET", "/monitor", None, &jb).await;
    assert_eq!(s, 200, "{m}");
    let now = m["values"]["ground_connections"].as_i64().unwrap_or_else(|| panic!("{m}"));
    assert!(now >= 3, "the ground's lines counted: {now}");
    assert_eq!(m["ground"]["connections"], json!(now));
    assert_eq!(m["ground"]["per_body"], json!(2));
    let (ceiling, reserve, seats) = (m["ground"]["ceiling"].as_i64().unwrap(), m["ground"]["reserve"].as_i64().unwrap(), m["ground"]["seats"].as_i64().unwrap());
    assert_eq!(seats, ((ceiling - reserve) / 2).max(0), "{m}");
    assert_eq!(m["ground"]["seated"], json!(2));
    let watches = m["watches"].as_array().unwrap();
    let gw = watches.iter().find(|w| w["metric"] == json!("ground_connections")).unwrap_or_else(|| panic!("the kernel's ground watch stands: {m}"));
    assert_eq!((gw["op"].as_str(), gw["added_by"].as_str(), gw["red"].as_bool()), (Some(">="), Some("the kernel"), Some(false)));
    assert_eq!(gw["threshold"], json!((ceiling - reserve) as f64));
    assert!(m["pool"]["shed_total"].is_number(), "the doors' pool counts what it shed: {}", m["pool"]);
    println!("connections · the Monitor reads {now} lines of a ceiling {ceiling} (reserve {reserve}, {seats} seats); the kernel watches ground_connections >= {}", ceiling - reserve);

    lit.stop().await;
    let _ = orreth_spine::ground::prune_scope(&mut g, &u).await;
}
