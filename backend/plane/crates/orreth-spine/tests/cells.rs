// PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp7, cells · partition · isolation · hardening · 2026-09-25
// Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp8, the profile rides the routed ask (W58) · 2026-09-26
// Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp8 row 3c: eleven world checks · 2026-09-27
//! THE CELLS' PROOF (canon 0002 rule 8 · 0005 P7 sp7 · M7 + M8): two Rust
//! kernels stand as two CELLS on one Postgres box — each its own database
//! and role, its own benches and topics, its own kernel self — and name
//! each other as peers. On the dev rig, by name:
//!
//!     cargo test -p orreth-spine --features bridge --test cells -- --nocapture
//!
//! What it proves: each cell homes its universe (the world card, the
//! `opened` fact) and is SEALED (the tenth check holds: its role reaches no
//! other database — a connection as cell A's role to cell B's database is
//! refused); the seam pins the peer's self on first sight and every hello
//! after reads live; an ask "echo@pb, say HERON" from cell A ROUTES HOME to
//! cell B, is served there by B's own body and answered on A's ask, its
//! journey said; the human's PROFILE told on A rides with a routed ask and B
//! reads it for that answer alone, keeping no row of it (P7 sp8, W58); the
//! human STOPS a routed ask and the home cell rests it
//! within the SLO (< 2 s); under PARTITION (cell B dark) the ask PARKS in
//! plain words and nothing is lost — when B returns the ask resumes and is
//! answered, never doubled; a universe RE-HOMED advances its epoch (held at
//! L2, settled on the yes): the old home refuses to serve, a message
//! wearing the old epoch is refused as stale, a replayed message and a
//! stranger's message wear the one face, and a flood meets the ceiling.
//! With no rig it prints "rails not up — skipped by name".
// Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp8 row 3, the gate: the proof SITS before it knocks (the ceremony through the doors) · 2026-09-26

#![cfg(feature = "bridge")]

use orreth_spine::bridge::{glass_path, light, Config};
use orreth_spine::cells;
use orreth_spine::ground::Ground;
use orreth_spine::kernel_self::KernelSelf;
use orreth_spine::rails;
use orreth_spine::world::{token_hex, World};
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

async fn http(port: u16, method: &str, path: &str, body: Option<&Value>) -> (u16, String) {
    let mut s = TcpStream::connect(("127.0.0.1", port))
        .await
        .expect("the door answers");
    let body = body.map(|b| b.to_string()).unwrap_or_default();
    let seat = seat_header(port);
    let req = format!(
        "{method} {path} HTTP/1.1\r\nHost: 127.0.0.1\r\nConnection: close\r\n{seat}content-type: \
         application/json\r\ncontent-length: {}\r\n\r\n{body}",
        body.len()
    );
    s.write_all(req.as_bytes()).await.unwrap();
    let mut raw = Vec::new();
    s.read_to_end(&mut raw).await.unwrap();
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
    (status, body)
}

async fn get(port: u16, path: &str) -> (u16, Value) {
    let (s, b) = http(port, "GET", path, None).await;
    (s, serde_json::from_str(&b).unwrap_or(Value::Null))
}

async fn post(port: u16, path: &str, body: Value) -> (u16, Value) {
    let (s, b) = http(port, "POST", path, Some(&body)).await;
    (s, serde_json::from_str(&b).unwrap_or(Value::Null))
}

// ---- P7 sp8 row 3: THE GATE — every door reads the person from the SEAT; a proof sits first
static SEATS: std::sync::OnceLock<std::sync::Mutex<std::collections::HashMap<u16, String>>> =
    std::sync::OnceLock::new();
static SECRETS: std::sync::OnceLock<std::sync::Mutex<std::collections::HashMap<String, String>>> =
    std::sync::OnceLock::new();

/// The seat this proof holds at a port, as the request header line — or nothing.
fn seat_header(port: u16) -> String {
    SEATS
        .get_or_init(Default::default)
        .lock()
        .unwrap()
        .get(&port)
        .map(|w| format!("authorization: Bearer {w}\r\n"))
        .unwrap_or_default()
}

#[allow(dead_code)]
fn secret_of(person: &str) -> String {
    SECRETS
        .get_or_init(Default::default)
        .lock()
        .unwrap()
        .get(person)
        .cloned()
        .expect("the person's secret is known: sit first")
}

/// The ceremony a human runs in the glass, through the doors alone: enroll (the door
/// stands open while no one holds this ground; afterwards on the seated owner's word),
/// confirm with the first code, sit with the next — the seat rides every later knock at
/// this port. Returns the seat's answer.
async fn sit(port: u16, person: &str) -> Value {
    let known = SECRETS
        .get_or_init(Default::default)
        .lock()
        .unwrap()
        .get(person)
        .cloned();
    let secret = match known {
        Some(s) => s,
        None => {
            let (s, b) = post(port, "/enroll", json!({"person": person})).await;
            assert_eq!(s, 201, "the enroll at :{port} for {person}: {b}");
            let secret = b["secret"].as_str().unwrap().to_string();
            let code =
                orreth_spine::proof::totp(&secret, orreth_spine::proof_live::now_unix()).unwrap();
            let (s, b) = post(
                port,
                "/enroll/confirm",
                json!({"person": person, "code": code}),
            )
            .await;
            assert_eq!(s, 200, "the confirm at :{port} for {person}: {b}");
            SECRETS
                .get_or_init(Default::default)
                .lock()
                .unwrap()
                .insert(person.to_string(), secret.clone());
            secret
        }
    };
    let code = orreth_spine::proof::totp(&secret, orreth_spine::proof_live::now_unix()).unwrap();
    let (mut s, mut b) = post(port, "/seat", json!({"person": person, "code": code})).await;
    if s == 403 {
        // another GROUND at this port (a second cell): the known secret is not enrolled here — its own ceremony
        let (es, eb) = post(port, "/enroll", json!({"person": person})).await;
        assert_eq!(
            es, 201,
            "the enroll at :{port} for {person} (a second ground): {eb}"
        );
        let secret2 = eb["secret"].as_str().unwrap().to_string();
        let code2 =
            orreth_spine::proof::totp(&secret2, orreth_spine::proof_live::now_unix()).unwrap();
        let (cs, cb) = post(
            port,
            "/enroll/confirm",
            json!({"person": person, "code": code2}),
        )
        .await;
        assert_eq!(cs, 200, "the confirm at :{port}: {cb}");
        let code3 =
            orreth_spine::proof::totp(&secret2, orreth_spine::proof_live::now_unix()).unwrap();
        let r = post(port, "/seat", json!({"person": person, "code": code3})).await;
        s = r.0;
        b = r.1;
    }
    assert_eq!(s, 201, "the seat at :{port} for {person}: {b}");
    SEATS
        .get_or_init(Default::default)
        .lock()
        .unwrap()
        .insert(port, b["wire"].as_str().unwrap().to_string());
    b
}

async fn wait_for(port: u16, path: &str, within: Duration, pred: impl Fn(&Value) -> bool) -> Value {
    let end = Instant::now() + within;
    let mut last = Value::Null;
    while Instant::now() < end {
        let (_, v) = get(port, path).await;
        if pred(&v) {
            return v;
        }
        last = v;
        tokio::time::sleep(Duration::from_millis(400)).await;
    }
    panic!("{path} never satisfied the wait; last: {last}");
}

fn peer<'a>(card: &'a Value, cell: &str) -> &'a Value {
    card["peers"]
        .as_array()
        .and_then(|a| a.iter().find(|p| p["cell"] == json!(cell)))
        .unwrap_or(&Value::Null)
}

fn body_of<'a>(bodies: &'a Value, name: &str) -> &'a Value {
    bodies["bodies"]
        .as_array()
        .and_then(|a| a.iter().find(|b| b["name"] == json!(name)))
        .unwrap_or(&Value::Null)
}

fn journey_has(v: &Value, words: &str) -> bool {
    v["journey"].as_array().is_some_and(|a| {
        a.iter()
            .any(|n| n.as_str().unwrap_or_default().contains(words))
    })
}

fn free_port() -> u16 {
    std::net::TcpListener::bind(("127.0.0.1", 0))
        .unwrap()
        .local_addr()
        .unwrap()
        .port()
}

/// The admin DSN's host part, re-aimed at a cell's role and database.
fn dsn_for(admin: &str, role: &str, pw: &str, db: &str) -> String {
    let after_at = admin.rsplit('@').next().unwrap_or("localhost:5433/spine");
    let host = after_at.split('/').next().unwrap_or("localhost:5433");
    format!("postgresql://{role}:{pw}@{host}/{db}")
}

fn config(
    world: &World,
    port: u16,
    cell: &str,
    peers: Vec<cells::Peer>,
    kernel_home: std::path::PathBuf,
    bodies: bool,
) -> Config {
    Config {
        port,
        world: world.clone(),
        glass: glass_path(),
        masters: String::new(),
        human_zone: "America/Denver".into(),
        bodies,
        ephemeral: true,
        spine: spine_dir(),
        cell: cell.into(),
        peers,
        kernel_home: Some(kernel_home),
    }
}

fn alive(pid: u32) -> bool {
    unsafe { libc::kill(pid as libc::pid_t, 0) == 0 }
}

#[tokio::test]
async fn two_cells_on_one_box_route_home_park_resume_and_fence() {
    if !rig_up("two_cells_on_one_box_route_home_park_resume_and_fence") {
        return;
    }
    let tok = token_hex(3);
    let admin = rails::pg_dsn();
    let g0 = Ground::connect(&admin).await.expect("the admin ground");
    // leftovers of a run that panicked before its cleanup: dropped at the start, by name
    for r in g0
        .client()
        .query(
            "SELECT datname::text FROM pg_database WHERE datname LIKE 'spine_cells_%'",
            &[],
        )
        .await
        .unwrap()
    {
        let db: String = r.get(0);
        let _ = g0
            .client()
            .batch_execute(&format!("DROP DATABASE {db} WITH (FORCE)"))
            .await;
        let _ = g0
            .client()
            .batch_execute(&format!(
                "DROP ROLE {}",
                db.replace("spine_cells_", "cell_")
            ))
            .await;
    }
    // ---- the two cells' grounds: a database and a role each, sealed (M8's isolation at the dev profile)
    let (db_a, db_b) = (
        format!("spine_cells_a_{tok}"),
        format!("spine_cells_b_{tok}"),
    );
    let (role_a, role_b) = (format!("cell_a_{tok}"), format!("cell_b_{tok}"));
    let pw = "cell-proof-dev";
    for (role, db) in [(&role_a, &db_a), (&role_b, &db_b)] {
        g0.client()
            .batch_execute(&format!("CREATE ROLE {role} LOGIN PASSWORD '{pw}'"))
            .await
            .unwrap();
        g0.client()
            .batch_execute(&format!("CREATE DATABASE {db} OWNER {role}"))
            .await
            .unwrap();
        g0.client()
            .batch_execute(&format!("REVOKE CONNECT ON DATABASE {db} FROM PUBLIC; GRANT CONNECT ON DATABASE {db} TO {role}"))
            .await
            .unwrap();
    }
    // the seal the rig applies (`dev.sh cell`): PUBLIC enters no database of ours
    for d in ["spine", "litellm", "postgres"] {
        let _ = g0
            .client()
            .batch_execute(&format!("REVOKE CONNECT ON DATABASE {d} FROM PUBLIC"))
            .await;
    }
    let dsn_a = dsn_for(&admin, &role_a, pw, &db_a);
    let dsn_b = dsn_for(&admin, &role_b, pw, &db_b);
    // cell A's role may not enter cell B's database — the seal, felt
    let cross =
        tokio_postgres::connect(&dsn_for(&admin, &role_a, pw, &db_b), tokio_postgres::NoTls).await;
    assert!(cross.is_err(), "cell A's role entered cell B's database");

    let home = std::env::temp_dir().join(format!("orreth-cells-{tok}"));
    std::fs::create_dir_all(home.join("agents")).unwrap();
    std::env::set_var("ORRETH_HOME", &home);
    std::env::set_var("SPINE_SERVICES_HOME", home.join("services"));
    std::env::set_var("SPINE_GATEWAY", "http://127.0.0.1:1"); // the gateway dark: the fake mind, no spend
    std::env::set_var("SPINE_MIND_CHECK_S", "3600");
    std::env::set_var("SPINE_TOOL_CHECK_S", "3600");
    let crew = home.join("crew.v0.json");
    std::fs::write(
        &crew,
        json!({"format": "orreth-crew/1", "seats": [{"template": "templates/echo-resident.v0.json"}]}).to_string(),
    )
    .unwrap();
    std::env::set_var("SPINE_CREW", &crew);

    let world_a = World {
        scope: format!("u:pa-{tok}"),
        ns: format!("a{tok}"),
        pg_dsn: dsn_a.clone(),
        rabbit_url: rails::rabbit_url(),
        kafka: rails::kafka_bootstrap(),
    };
    let world_b = World {
        scope: format!("u:pb-{tok}"),
        ns: format!("b{tok}"),
        pg_dsn: dsn_b.clone(),
        rabbit_url: rails::rabbit_url(),
        kafka: rails::kafka_bootstrap(),
    };
    let (port_a, port_b) = (free_port(), free_port());
    let peers_a = vec![cells::Peer {
        cell: "pb".into(),
        door: format!("http://127.0.0.1:{port_b}"),
    }];
    let peers_b = vec![cells::Peer {
        cell: "pa".into(),
        door: format!("http://127.0.0.1:{port_a}"),
    }];
    let (home_a, home_b) = (home.join("kernel-a"), home.join("kernel-b"));

    // ---- 1. two cells lit: B seats the echo, A seats nobody (it asks)
    let lit_b = light(config(
        &world_b,
        port_b,
        "pb",
        peers_b.clone(),
        home_b.clone(),
        true,
    ))
    .await
    .expect("cell B lights");
    let lit_a = light(config(
        &world_a,
        port_a,
        "pa",
        peers_a.clone(),
        home_a.clone(),
        false,
    ))
    .await
    .expect("cell A lights");
    assert!(
        lit_a.wait_ready(Duration::from_secs(60)).await
            && lit_b.wait_ready(Duration::from_secs(60)).await
    );
    sit(port_a, "did:orreth:person:jb").await; // P7 sp8 row 3: two grounds, two ceremonies — jb holds both
    sit(port_b, "did:orreth:person:jb").await;
    let (_, card_a) = get(port_a, "/world").await;
    let (_, card_b) = get(port_b, "/world").await;
    assert_eq!(card_a["cell"], json!("pa"));
    assert_eq!(card_b["cell"], json!("pb"));
    assert_eq!(card_a["epoch"], json!(1));
    assert!(card_a["homed"] == json!(true) && card_b["homed"] == json!(true));
    let (kernel_a, kernel_b) = (
        card_a["kernel"].as_str().unwrap().to_string(),
        card_b["kernel"].as_str().unwrap().to_string(),
    );
    assert_ne!(kernel_a, kernel_b, "two cells, two selves");
    assert!(kernel_a.starts_with("did:orreth:kernel:"));
    // the opened fact stands on each ground
    let ga = Ground::connect(&dsn_a).await.unwrap();
    let opened: i64 = ga
        .client()
        .query_one(
            "SELECT count(*) FROM spine_outbox WHERE convert_from(body, 'UTF8') LIKE '%orreth.world.homed.v1%'",
            &[],
        )
        .await
        .unwrap()
        .get(0);
    assert_eq!(opened, 1, "the universe's homing is said once");
    println!(
        "cells · two cells lit: {} in pa (kernel {kernel_a}) · {} in pb (kernel {kernel_b})",
        world_a.scope, world_b.scope
    );

    // ---- 2. sealed: the tenth check holds on each cell's role
    let (_, h) = get(port_a, "/harness").await;
    let sealed = h["checks"]
        .as_array()
        .unwrap()
        .iter()
        .find(|c| c["name"] == json!("this cell is sealed"))
        .cloned()
        .unwrap();
    assert_eq!(sealed["ok"], json!(true), "{sealed}");
    assert_eq!(sealed["reachable"], json!([db_a]));
    assert_eq!(h["checks"].as_array().unwrap().len(), 11, "eleven checks"); // row 3c: the eleventh
    println!("cells · sealed: {}", sealed["detail"]);

    // ---- 3. the seam: peers pinned on first sight, live
    let card_a = wait_for(port_a, "/world", Duration::from_secs(30), |v| {
        peer(v, "pb")["did"].is_string()
            && peer(v, "pb")["words"]
                .as_str()
                .is_some_and(|w| w.contains("live"))
    })
    .await;
    assert_eq!(
        peer(&card_a, "pb")["did"],
        json!(kernel_b),
        "cell B's self pinned"
    );
    assert_eq!(peer(&card_a, "pb")["world"], json!(world_b.scope));
    assert_eq!(peer(&card_a, "pb")["epoch"], json!(1));
    let card_b = wait_for(port_b, "/world", Duration::from_secs(30), |v| {
        peer(v, "pa")["did"].is_string()
    })
    .await;
    assert_eq!(
        peer(&card_b, "pa")["did"],
        json!(kernel_a),
        "cell A's self pinned"
    );
    println!(
        "cells · the seam: {} · {}",
        peer(&card_a, "pb")["words"],
        peer(&card_b, "pa")["words"]
    );

    // ---- 4. the echo seated in B; parked by hand (three deaths) so an ask can be stopped IN FLIGHT
    let v = wait_for(port_b, "/bodies", Duration::from_secs(240), |v| {
        body_of(v, "echo")["state"] == json!("alive")
    })
    .await;
    let mut pid = body_of(&v, "echo")["pid"].as_u64().unwrap() as u32;
    for life in 1..=3 {
        unsafe { libc::kill(pid as libc::pid_t, libc::SIGKILL) };
        let want = if life < 3 { "alive" } else { "parked" };
        let v = wait_for(port_b, "/bodies", Duration::from_secs(90), |v| {
            let b = body_of(v, "echo");
            b["state"] == json!(want)
                && (want == "parked" || b["pid"].as_u64().map(|p| p as u32) != Some(pid))
        })
        .await;
        pid = body_of(&v, "echo")["pid"].as_u64().unwrap_or(0) as u32;
    }
    println!("cells · B's echo parked by hand — its bench stands, nobody serves it");

    // ---- 5. an ask routed home and STOPPED: the home cell rests it within the SLO
    let (st, r) = post(
        port_a,
        "/ask",
        json!({"text": "echo@pb, say GULL", "person": "did:orreth:person:jb"}),
    )
    .await;
    assert_eq!(st, 201, "{r}");
    let id1 = r["id"].as_str().unwrap().to_string();
    let v = wait_for(
        port_a,
        &format!("/ask/{id1}"),
        Duration::from_secs(30),
        |v| v["status"] == json!("routed") && journey_has(v, "routed home to cell pb"),
    )
    .await;
    assert_eq!(v["target"], json!("echo@pb"));
    // B took it: a row of its own, the words stripped of the cell, the journey saying whence it came
    let gb = Ground::connect(&dsn_b).await.unwrap();
    let remote: String = {
        let end = Instant::now() + Duration::from_secs(30);
        loop {
            if let Some(r) = gb
                .client()
                .query_opt(
                    "SELECT ask_id, text, status FROM spine_asks WHERE remote_id = $1",
                    &[&id1],
                )
                .await
                .unwrap()
            {
                assert_eq!(r.get::<_, String>(1), "echo, say GULL");
                assert_eq!(
                    r.get::<_, String>(2),
                    "received",
                    "nobody serves a parked body's bench"
                );
                break r.get(0);
            }
            assert!(Instant::now() < end, "cell B never filed the routed ask");
            tokio::time::sleep(Duration::from_millis(300)).await;
        }
    };
    let (_, vb) = get(port_b, &format!("/ask/{remote}")).await;
    assert!(journey_has(&vb, "came over the seam from cell pa"), "{vb}");
    let t0 = Instant::now();
    let (st, s) = post(
        port_a,
        "/asks/stop",
        json!({"id": id1, "person": "did:orreth:person:jb"}),
    )
    .await;
    assert_eq!(st, 200, "{s}");
    assert_eq!(s["status"], json!("cancelled"));
    wait_for(
        port_b,
        &format!("/ask/{remote}"),
        Duration::from_secs(10),
        |v| v["status"] == json!("cancelled"),
    )
    .await;
    let took = t0.elapsed();
    assert!(
        took < Duration::from_secs(2),
        "the stop reached cell B in {took:?} — the SLO is 2 s"
    );
    let (_, va) = get(port_a, &format!("/ask/{id1}")).await;
    assert_eq!(va["status"], json!("cancelled"));
    assert!(
        va["reply"]
            .as_str()
            .unwrap()
            .starts_with("Stopped on your word"),
        "{va}"
    );
    println!("cells · the stop reached cell B in {took:?} (SLO 2 s) — the human can always stop");

    // ---- 6. the echo restarted on the word; an ask routed home is SERVED there and answered here
    let (st, r) = post(port_b, "/bodies/restart", json!({"name": "echo"})).await;
    assert!(st == 200 || st == 202, "{r}");
    wait_for(port_b, "/bodies", Duration::from_secs(90), |v| {
        body_of(v, "echo")["state"] == json!("alive")
    })
    .await;
    let (_, r) = post(
        port_a,
        "/ask",
        json!({"text": "echo@pb, say HERON", "person": "did:orreth:person:jb"}),
    )
    .await;
    let id2 = r["id"].as_str().unwrap().to_string();
    let v = wait_for(
        port_a,
        &format!("/ask/{id2}"),
        Duration::from_secs(60),
        |v| v["status"] == json!("replied"),
    )
    .await;
    assert!(v["reply"].as_str().unwrap().contains("HERON"), "{v}");
    assert_eq!(v["served_by"], json!("echo@pb"));
    assert!(journey_has(&v, "answered in cell pb by echo"), "{v}");
    println!(
        "cells · routed home: echo@pb, say HERON → {:?} by {}",
        v["reply"], v["served_by"]
    );

    // ---- 6b. P7 sp8 (W58): the human's profile on A RIDES with a routed ask — B reads it for that
    // answer only (the ask's own column), and keeps no profile row of the person
    let (st, r) = post(
        port_a,
        "/profile",
        json!({"person": "did:orreth:person:jb", "text": "my name is JB", "geocode": false}),
    )
    .await;
    assert_eq!(st, 201, "{r}");
    assert_eq!(r["act"], json!("tell"));
    assert_eq!(r["portrait"]["name"], json!("JB"));
    let (st, r) = post(
        port_a,
        "/profile",
        json!({"person": "did:orreth:person:jb", "text": "my clock is Europe/Rome", "geocode": false}),
    )
    .await;
    assert_eq!(st, 201, "{r}");
    assert_eq!(r["portrait"]["clock"], json!("Europe/Rome"));
    let (st, r) = post(
        port_a,
        "/profile",
        json!({"person": "did:orreth:person:jb", "text": "what is the temperature outside?"}),
    )
    .await;
    assert_eq!(st, 400, "{r}");
    assert!(
        r["error"]
            .as_str()
            .unwrap()
            .contains("tell me nothing about you"),
        "{r}"
    );
    let (st, pa) = get(port_a, "/profile?person=did:orreth:person:jb").await;
    assert_eq!(st, 200);
    assert_eq!(
        pa["words"],
        json!("you told me: your name is JB · your clock is Europe/Rome")
    );
    assert_eq!(pa["claims"][0]["label"], json!("you told me"));
    let (_, r) = post(
        port_a,
        "/ask",
        json!({"text": "echo@pb, say KITE", "person": "did:orreth:person:jb"}),
    )
    .await;
    let id_k = r["id"].as_str().unwrap().to_string();
    wait_for(
        port_a,
        &format!("/ask/{id_k}"),
        Duration::from_secs(60),
        |v| v["status"] == json!("replied"),
    )
    .await;
    let carried: String = gb
        .client()
        .query_one(
            "SELECT carried_profile FROM spine_asks WHERE remote_id = $1",
            &[&id_k],
        )
        .await
        .unwrap()
        .get(0);
    let carried: Value = serde_json::from_str(&carried).unwrap();
    assert_eq!(carried["words"], pa["words"], "the slice rode whole");
    assert_eq!(carried["zone"], json!("Europe/Rome"));
    let kept: i64 = gb
        .client()
        .query_one(
            "SELECT count(*) FROM spine_profile WHERE person = 'did:orreth:person:jb'",
            &[],
        )
        .await
        .unwrap()
        .get(0);
    assert_eq!(kept, 0, "the far cell keeps no profile row of the person");
    let (_, pb) = get(port_b, "/profile?person=did:orreth:person:jb").await;
    assert_eq!(pb["name"], Value::Null);
    println!(
        "cells · the profile rode with the ask: {} → B kept nothing",
        carried["words"]
    );

    // ---- 7. PARTITION: cell B dark — the ask parks in plain words; B back — it resumes, once
    let pid_b_echo = body_of(&get(port_b, "/bodies").await.1, "echo")["pid"]
        .as_u64()
        .unwrap() as u32;
    lit_b.stop().await;
    assert!(!alive(pid_b_echo), "B's echo stopped with its kernel");
    let (_, r) = post(
        port_a,
        "/ask",
        json!({"text": "echo@pb, say TERN", "person": "did:orreth:person:jb"}),
    )
    .await;
    let id3 = r["id"].as_str().unwrap().to_string();
    let v = wait_for(
        port_a,
        &format!("/ask/{id3}"),
        Duration::from_secs(30),
        |v| v["status"] == json!("parked"),
    )
    .await;
    assert!(
        journey_has(
            &v,
            "echo@pb is out of reach — cell pb has not answered since"
        ),
        "{v}"
    );
    let card_a = wait_for(port_a, "/world", Duration::from_secs(30), |v| {
        peer(v, "pb")["unreachable_since"].is_string()
    })
    .await;
    assert!(
        peer(&card_a, "pb")["words"]
            .as_str()
            .unwrap()
            .contains("unreachable since"),
        "{card_a}"
    );
    println!(
        "cells · partition: {} · {}",
        v["journey"].as_array().unwrap().last().unwrap(),
        peer(&card_a, "pb")["words"]
    );
    let lit_b = light(config(
        &world_b,
        port_b,
        "pb",
        peers_b.clone(),
        home_b.clone(),
        true,
    ))
    .await
    .expect("cell B relights on its port");
    assert!(lit_b.wait_ready(Duration::from_secs(60)).await);
    let (_, card_b) = get(port_b, "/world").await;
    assert_eq!(
        card_b["kernel"],
        json!(kernel_b),
        "the same self every life"
    );
    assert_eq!(card_b["epoch"], json!(1));
    let v = wait_for(
        port_a,
        &format!("/ask/{id3}"),
        Duration::from_secs(240),
        |v| v["status"] == json!("replied"),
    )
    .await;
    assert!(v["reply"].as_str().unwrap().contains("TERN"), "{v}");
    assert!(journey_has(&v, "cell pb answers again"), "{v}");
    let twice: i64 = gb
        .client()
        .query_one(
            "SELECT count(*) FROM spine_asks WHERE remote_id = $1",
            &[&id3],
        )
        .await
        .unwrap()
        .get(0);
    assert_eq!(twice, 1, "the parked ask landed in cell B exactly once");
    println!("cells · resumed: {:?} — landed once in B", v["reply"]);

    // ---- 8. HARDENING at the seam: a stranger, a replay, a flood
    let self_a = KernelSelf::load(&home_a).unwrap();
    assert_eq!(self_a.did(), kernel_a);
    let (st, b) = post(port_b, "/seam", json!({"hello": "from nobody"})).await;
    assert_eq!(
        (st, b),
        (403, json!({"error": "not confirmed"})),
        "a bare knock wears the one face"
    );
    let stranger = cells::seam_sign(
        &cells::seam_message(
            "px",
            "u:px",
            "pb",
            1,
            "hello",
            json!({}),
            &format!("n_{}", token_hex(8)),
            &orreth_spine::envelope::now_iso(),
        ),
        &KernelSelf::ephemeral(),
    );
    let (st, b) = post(port_b, "/seam", stranger).await;
    assert_eq!(
        (st, b),
        (403, json!({"error": "not confirmed"})),
        "a cell never named wears the one face"
    );
    let once = cells::seam_sign(
        &cells::seam_message(
            "pa",
            &world_a.scope,
            "pb",
            1,
            "hello",
            json!({"door": format!("http://127.0.0.1:{port_a}"), "roster": []}),
            &format!("n_{}", token_hex(8)),
            &orreth_spine::envelope::now_iso(),
        ),
        &self_a,
    );
    let (st, b) = post(port_b, "/seam", once.clone()).await;
    assert_eq!(st, 200, "a signed hello from the pinned peer: {b}");
    assert_eq!(
        b["signer"],
        json!(kernel_b),
        "answered in B's own signature"
    );
    let (st, b) = post(port_b, "/seam", once).await;
    assert_eq!(
        (st, b),
        (403, json!({"error": "not confirmed"})),
        "the same message again is a replay"
    );
    // thirty knocks AT ONCE (concurrent, so the bucket sees them inside one refill) — the burst is 20
    let mut flood = Vec::new();
    for _ in 0..30 {
        let m = cells::seam_sign(
            &cells::seam_message(
                "pa",
                &world_a.scope,
                "pb",
                1,
                "hello",
                json!({"roster": []}),
                &format!("n_{}", token_hex(8)),
                &orreth_spine::envelope::now_iso(),
            ),
            &self_a,
        );
        flood.push(tokio::spawn(post(port_b, "/seam", m)));
    }
    let mut refused = 0;
    for h in flood {
        if h.await.unwrap().0 == 403 {
            refused += 1;
        }
    }
    assert!(
        refused > 0,
        "thirty knocks at once meet the ceiling (burst 20)"
    );
    println!("cells · hardening: a stranger and a replay wear the one face; {refused}/30 of a flood refused at the ceiling");

    // ---- 9. RE-HOMED: the epoch advances on the yes; the old home refuses; a stale message is fenced
    let (st, r) = post(
        port_b,
        "/world/rehome",
        json!({"to_cell": "pc", "person": "did:orreth:person:jb"}),
    )
    .await;
    assert_eq!(st, 202, "{r}");
    let held = r["held"].as_str().unwrap().to_string();
    let (st, c) = post(
        port_b,
        "/confirm",
        json!({"ask_id": held, "approve": true, "person": "did:orreth:person:jb"}),
    )
    .await;
    assert!(st == 200 || st == 202, "{st} {c}");
    let card_b = wait_for(port_b, "/world", Duration::from_secs(10), |v| {
        v["epoch"] == json!(2)
    })
    .await;
    assert_eq!(card_b["cell"], json!("pc"));
    let (_, vh) = get(port_b, &format!("/ask/{held}")).await;
    assert!(
        vh["reply"]
            .as_str()
            .unwrap()
            .contains("re-homed from cell pb to cell pc at epoch 2"),
        "{vh}"
    );
    let (st, r) = post(
        port_b,
        "/ask",
        json!({"text": "echo, say GANNET", "person": "did:orreth:person:jb"}),
    )
    .await;
    assert_eq!(st, 403, "{r}");
    assert!(
        r["error"]
            .as_str()
            .unwrap()
            .contains("re-homed to cell pc at epoch 2"),
        "{r}"
    );
    let stale = cells::seam_sign(
        &cells::seam_message(
            "pa",
            &world_a.scope,
            "pb",
            1,
            "stop",
            json!({"ask_id": "ask_none"}),
            &format!("n_{}", token_hex(8)),
            &orreth_spine::envelope::now_iso(),
        ),
        &self_a,
    );
    let _ = stale; // B's pin of A still says epoch 1 — A's epoch did not move; the fence is B's own epoch for its peers.
                   // A hears the new epoch on its next hello
    let card_a = wait_for(port_a, "/world", Duration::from_secs(30), |v| {
        peer(v, "pb")["epoch"] == json!(2)
    })
    .await;
    assert_eq!(peer(&card_a, "pb")["epoch"], json!(2), "{card_a}");
    // and a message wearing pb's OLD epoch, signed by pb's own self, is refused as stale by pa
    let self_b = KernelSelf::load(&home_b).unwrap();
    let old = cells::seam_sign(
        &cells::seam_message(
            "pb",
            &world_b.scope,
            "pa",
            1,
            "stop",
            json!({"ask_id": "ask_none"}),
            &format!("n_{}", token_hex(8)),
            &orreth_spine::envelope::now_iso(),
        ),
        &self_b,
    );
    let (st, b) = post(port_a, "/seam", old).await;
    assert_eq!(st, 409, "{b}");
    assert_eq!(b["error"], json!("stale epoch"));
    println!(
        "cells · re-homed: {} · the old home refuses to serve · a stale epoch is fenced (409)",
        vh["reply"]
    );

    // ---- 10. dark: both cells stopped whole; the proof's grounds dropped
    lit_a.stop().await;
    lit_b.stop().await;
    assert!(!port_open(port_a) && !port_open(port_b));
    drop(ga);
    drop(gb);
    for (role, db) in [(&role_a, &db_a), (&role_b, &db_b)] {
        let _ = g0
            .client()
            .batch_execute(&format!("DROP DATABASE {db} WITH (FORCE)"))
            .await;
        let _ = g0
            .client()
            .batch_execute(&format!("DROP ROLE {role}"))
            .await;
    }
    println!("cells · dark: both cells stopped whole; the proof's grounds dropped");
}
