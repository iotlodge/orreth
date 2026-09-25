// PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp6, the bodies' seam · 2026-09-24
//! THE BODIES' PROOF (canon 0008 · P7 sp6): the Rust kernel stands ALONE —
//! no Python Bridge — and SEATS THE CREW: every seat a Python process it
//! spawns and governs. On the dev rig, by name:
//!
//!     cargo test -p orreth-spine --features bridge --test bodies -- --nocapture
//!
//! What it proves: the bodies join this world and hold their leases (the
//! roster reads alive); an ask through the Rust door is served by a body the
//! Rust kernel spawned and the words stream back to the kernel's feed as they
//! form; a body killed by hand comes back as THE SAME SELF (AG-2: one DID,
//! life 2); the harness runs OVER THE RAIL — the kernel asks the body, the
//! body runs its golden cases through its own graph and the run lands under
//! the kernel's run id (a failing run is a fact); a body that dies three
//! times in the window is PARKED — said in plain words, a fact on the outbox
//! — and the human's lever restarts it; the Stable's doors answer from the
//! Rust kernel; and at dark every body is stopped WHOLE — nothing left
//! running. With no rig it prints "rails not up — skipped by name"; beside a
//! live Bridge on :4600 it refuses to run. The bodies think with the fake
//! mind (the gateway dial points at a dark port) — no spend.

#![cfg(feature = "bridge")]

use orreth_spine::bridge::{glass_path, light, Config};
use orreth_spine::ground::Ground;
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
    let req = format!(
        "{method} {path} HTTP/1.1\r\nHost: 127.0.0.1\r\nConnection: close\r\ncontent-type: \
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

async fn wait_for(port: u16, path: &str, within: Duration, pred: impl Fn(&Value) -> bool) -> Value {
    let end = Instant::now() + within;
    let mut last = Value::Null;
    while Instant::now() < end {
        let (_, v) = get(port, path).await;
        if pred(&v) {
            return v;
        }
        last = v;
        tokio::time::sleep(Duration::from_millis(500)).await;
    }
    panic!("{path} never satisfied the wait; last: {last}");
}

fn body_of<'a>(bodies: &'a Value, name: &str) -> &'a Value {
    bodies["bodies"]
        .as_array()
        .and_then(|a| a.iter().find(|b| b["name"] == json!(name)))
        .unwrap_or(&Value::Null)
}

fn alive(pid: u32) -> bool {
    unsafe { libc::kill(pid as libc::pid_t, 0) == 0 }
}

#[tokio::test]
async fn the_rust_kernel_alone_seats_and_governs_the_crew() {
    if !rig_up("the_rust_kernel_alone_seats_and_governs_the_crew") {
        return;
    }
    if port_open(4600) {
        println!("a Bridge holds :4600 — the bodies proof refuses to run beside a live rig (stop it: scripts/dev.sh bridge stop)");
        return;
    }
    let tok = token_hex(3);
    let world = World {
        scope: format!("u:bodies-{tok}"),
        ns: format!("t{tok}"),
        pg_dsn: rails::pg_dsn(),
        rabbit_url: rails::rabbit_url(),
        kafka: rails::kafka_bootstrap(),
    };
    let person = "did:orreth:person:jb".to_string();
    // one home for this proof: the bodies' seeds persist across the kill (AG-2), nothing under ~/.orreth
    let home = std::env::temp_dir().join(format!("orreth-bodies-{tok}"));
    std::fs::create_dir_all(home.join("agents")).unwrap();
    std::env::set_var("ORRETH_HOME", &home);
    std::env::set_var("SPINE_KERNEL_HOME", home.join("kernel"));
    std::env::set_var("SPINE_SERVICES_HOME", home.join("services"));
    std::env::set_var("SPINE_GATEWAY", "http://127.0.0.1:1"); // the gateway dark: the fake mind, no spend
    std::env::set_var("SPINE_MIND_CHECK_S", "5"); // the keepers beat inside the proof's minute
    std::env::set_var("SPINE_TOOL_CHECK_S", "5");
    // a two-seat crew for the proof: the librarian (a mind, a golden set) and the echo
    let crew = home.join("crew.v0.json");
    std::fs::write(
        &crew,
        json!({"format": "orreth-crew/1", "seats": [
            {"template": "templates/librarian-resident.v0.json"},
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
        ephemeral: false,
        spine: spine_dir(),
    })
    .await
    .expect("the Rust kernel lights alone");
    let port = lit.port;
    assert!(lit.wait_ready(Duration::from_secs(60)).await);
    let bodies = lit.bodies.clone().expect("this kernel seats a crew");
    assert_eq!(bodies.seats.len(), 2);
    let mut feed = lit.feed.subscribe();

    // ---- 1. the crew is seated: two processes, joined, alive on their leases
    let v = wait_for(port, "/bodies", Duration::from_secs(240), |v| {
        body_of(v, "echo")["state"] == json!("alive")
            && body_of(v, "librarian")["state"] == json!("alive")
    })
    .await;
    assert_eq!(v["mode"], json!("crew"));
    let echo_did = body_of(&v, "echo")["did"].as_str().unwrap().to_string();
    let echo_pid = body_of(&v, "echo")["pid"].as_u64().unwrap() as u32;
    assert!(echo_did.starts_with("did:orreth:agent:"), "{v}");
    assert_eq!(body_of(&v, "echo")["lives"], json!(1));
    let residents = wait_for(port, "/residents", Duration::from_secs(60), |v| {
        v["residents"].as_array().is_some_and(|a| a.len() == 2)
    })
    .await;
    let echo_row = residents["residents"]
        .as_array()
        .unwrap()
        .iter()
        .find(|r| r["name"] == json!("echo"))
        .unwrap();
    assert_eq!(
        echo_row["did"],
        json!(echo_did),
        "the roster's self is the process's self"
    );
    let mon = wait_for(port, "/monitor", Duration::from_secs(60), |v| {
        v["values"]["bodies_alive"] == json!(2)
    })
    .await;
    assert_eq!(mon["values"]["bodies_dormant"], json!(0));

    // ---- 2. an ask through the Rust door, served by a body the Rust kernel spawned
    let (st, made) = post(port, "/sessions", json!({"person": person})).await;
    assert_eq!(st, 201);
    let sid = made["session_id"].as_str().unwrap().to_string();
    let (st, asked) = post(port, "/ask", json!({"text": "echo, the walk's word is HERON", "to": ["echo"], "person": person, "session": sid})).await;
    assert_eq!(st, 201, "{asked}");
    let aid = asked["ids"][0].as_str().unwrap().to_string();
    let a = wait_for(port, &format!("/ask/{aid}"), Duration::from_secs(60), |v| {
        v["status"] == json!("replied")
    })
    .await;
    assert!(a["reply"].as_str().unwrap().contains("HERON"), "{a}");
    assert_eq!(a["served_by"], json!(echo_did));

    // ---- 3. the words as they form: the librarian (the fake mind streams) → the kernel's /delta → the feed
    let (st, asked) = post(port, "/ask", json!({"text": "librarian, in one word, who are you?", "to": ["librarian"], "person": person, "session": sid})).await;
    assert_eq!(st, 201, "{asked}");
    let lid = asked["ids"][0].as_str().unwrap().to_string();
    let mut saw_delta = false;
    let end = Instant::now() + Duration::from_secs(90);
    while Instant::now() < end {
        match tokio::time::timeout(Duration::from_secs(1), feed.recv()).await {
            Ok(Ok(n)) => {
                if n["delta"] == json!(true) && n["ref"] == json!(lid) {
                    saw_delta = true;
                }
                if n["kind"] == json!("orreth.reply.v1") && n["ref"] == json!(lid) && saw_delta {
                    break;
                }
            }
            Ok(Err(_)) => continue,
            Err(_) => {
                let (_, v) = get(port, &format!("/ask/{lid}")).await;
                if v["status"] == json!("replied") && saw_delta {
                    break;
                }
            }
        }
    }
    assert!(
        saw_delta,
        "the librarian's words never reached the kernel's feed as deltas"
    );
    let l = wait_for(port, &format!("/ask/{lid}"), Duration::from_secs(60), |v| {
        v["status"] == json!("replied")
    })
    .await;
    assert!(l["reply"].as_str().unwrap().contains("fake mind"), "{l}");

    // ---- 4. the harness OVER THE RAIL: the kernel asks the librarian; the run lands under the kernel's id
    let (st, run) = post(port, "/harness/run", json!({"template": "librarian"})).await;
    assert!(st == 200 || st == 202, "{st} {run}");
    let rid = run["run_id"].as_str().unwrap().to_string();
    assert!(rid.starts_with("run_"));
    let g = Ground::connect(&world.pg_dsn).await.unwrap();
    let row = if st == 200 {
        run.clone()
    } else {
        orreth_spine::harness::wait_run(&g, &rid, Duration::from_secs(120))
            .await
            .unwrap()
            .expect("the run lands")
    };
    assert_eq!(row["template"], json!("librarian"));
    assert_eq!(
        row["passed"].as_i64().unwrap() + row["failed"].as_i64().unwrap(),
        2,
        "{row}"
    );
    assert_eq!(
        row["failed"],
        json!(2),
        "the fake mind fails both golden cases, honestly: {row}"
    );
    let facts: i64 = g
        .client()
        .query_one(
            "SELECT count(*) FROM spine_outbox WHERE convert_from(body, 'UTF8') LIKE $1",
            &[&format!("%{rid}%")],
        )
        .await
        .unwrap()
        .get(0);
    assert!(facts >= 1, "a failing run is a fact on the rail");
    let (_, hz) = get(port, "/harness").await;
    assert_eq!(hz["last"]["template"], json!("librarian"));
    assert_eq!(
        hz["checks"].as_array().unwrap().len(),
        9,
        "nine world checks on the Rust door: {hz}"
    );
    assert_eq!(
        post(port, "/harness/run", json!({"template": "nobody"}))
            .await
            .0,
        404
    );

    // ---- 5. the Stable's doors answer from the Rust kernel (the gateway dark, said in words)
    let (st, minds) = get(port, "/minds").await;
    assert_eq!(st, 200, "{minds}");
    assert_eq!(minds["gateway"]["ready"], json!(false));
    assert!(
        minds["minds"].is_array() && minds["assignments"].is_array(),
        "{minds}"
    );
    let (st, fuel) = get(port, "/minds/fuel?name=librarian").await;
    assert_eq!(st, 200, "{fuel}");
    assert_eq!(get(port, "/minds/fuel?name=nobody").await.0, 404);
    let (st, held) = post(
        port,
        "/minds/assign",
        json!({"subject": "librarian", "stall": "ghost", "klass": "fast", "person": person}),
    )
    .await;
    assert_eq!(
        st, 202,
        "an assign is HELD at the interlock, whatever the stall: {held}"
    );
    let hold = held["held"].as_str().unwrap().to_string();
    let (st, c) = post(
        port,
        "/confirm",
        json!({"ask_id": hold, "approve": true, "person": person}),
    )
    .await;
    // the kernel settles: a ghost stall REFUSES in words — the record says so, nothing assigned
    assert!(st == 202 || st == 400, "{st} {c}");
    let (_, sv) = get(port, "/services").await;
    assert!(sv["services"].is_array());
    let (st, checked) = post(
        port,
        "/services/check",
        json!({"kind": "store", "person": person}),
    )
    .await;
    assert_eq!(st, 200, "{checked}");

    // ---- 6. AG-2: the echo killed by hand comes back as THE SAME SELF (life 2)
    assert!(alive(echo_pid));
    unsafe {
        libc::kill(echo_pid as libc::pid_t, libc::SIGKILL);
    }
    let v = wait_for(port, "/bodies", Duration::from_secs(120), |v| {
        let b = body_of(v, "echo");
        b["state"] == json!("alive") && b["lives"] == json!(2)
    })
    .await;
    assert_eq!(
        body_of(&v, "echo")["did"],
        json!(echo_did),
        "one self, two lives"
    );
    assert_eq!(body_of(&v, "echo")["deaths"].as_array().unwrap().len(), 1);
    let residents = wait_for(port, "/residents", Duration::from_secs(60), |v| {
        v["residents"].as_array().is_some_and(|a| {
            a.iter()
                .any(|r| r["name"] == json!("echo") && r["lives"] == json!(2))
        })
    })
    .await;
    let echo_row = residents["residents"]
        .as_array()
        .unwrap()
        .iter()
        .find(|r| r["name"] == json!("echo"))
        .unwrap();
    assert_eq!(echo_row["did"], json!(echo_did));
    let (_, asked) = post(
        port,
        "/ask",
        json!({"text": "echo, say GULL", "to": ["echo"], "person": person, "session": sid}),
    )
    .await;
    let aid2 = asked["ids"][0].as_str().unwrap().to_string();
    wait_for(
        port,
        &format!("/ask/{aid2}"),
        Duration::from_secs(60),
        |v| v["status"] == json!("replied"),
    )
    .await;
    let (st, r) = post(port, "/bodies/restart", json!({"name": "echo"})).await;
    assert_eq!(st, 202);
    assert_eq!(
        r["restarting"],
        json!(false),
        "an alive body has nothing to restart: {r}"
    );

    // ---- 7. the PARK law: two more deaths inside the window park the echo, said in words, a fact; the lever restarts it
    for life in 2..=3 {
        let v = wait_for(port, "/bodies", Duration::from_secs(120), |v| {
            let b = body_of(v, "echo");
            b["state"] == json!("alive") && b["lives"] == json!(life)
        })
        .await;
        let pid = body_of(&v, "echo")["pid"].as_u64().unwrap() as u32;
        unsafe {
            libc::kill(pid as libc::pid_t, libc::SIGKILL);
        }
    }
    let v = wait_for(port, "/bodies", Duration::from_secs(120), |v| {
        body_of(v, "echo")["state"] == json!("parked")
    })
    .await;
    let words = body_of(&v, "echo")["words"].as_str().unwrap().to_string();
    assert!(
        words.contains("echo is PARKED")
            && words.contains("died 3 times in 5 minutes")
            && words.contains("restart the echo body"),
        "{words}"
    );
    let parked: i64 = g
        .client()
        .query_one(
            "SELECT count(*) FROM spine_outbox WHERE convert_from(body, 'UTF8') LIKE '%orreth.body.parked.v1%' AND convert_from(body, 'UTF8') LIKE $1",
            &[&format!("%{}%", world.scope)],
        )
        .await
        .unwrap()
        .get(0);
    assert_eq!(parked, 1, "the parked fact, once, on the outbox");
    tokio::time::sleep(Duration::from_secs(16)).await; // the lease lapses: the roster reads dormant
    let (_, mon) = get(port, "/monitor").await;
    assert_eq!(mon["values"]["bodies_dormant"], json!(1), "{mon}");
    let (st, r) = post(port, "/bodies/restart", json!({"name": "echo"})).await;
    assert_eq!(st, 202);
    assert_eq!(r["restarting"], json!(true), "{r}");
    let v = wait_for(port, "/bodies", Duration::from_secs(120), |v| {
        let b = body_of(v, "echo");
        b["state"] == json!("alive") && b["lives"] == json!(4)
    })
    .await;
    assert_eq!(
        body_of(&v, "echo")["did"],
        json!(echo_did),
        "still the same self after the park"
    );
    assert_eq!(
        body_of(&v, "echo")["deaths"].as_array().unwrap().len(),
        0,
        "its deaths forgotten on the human's word"
    );

    // ---- 8. the crew card knows which LLM the librarian thinks with (the Stable's decision, from this kernel)
    let (_, crew) = get(port, "/crew").await;
    let lib = crew["crew"]
        .as_array()
        .unwrap()
        .iter()
        .find(|c| c["name"] == json!("librarian"))
        .unwrap();
    assert!(lib.get("mind").is_some(), "{lib}");

    // ---- down, WHOLE: nothing left running
    let pids: Vec<u32> = ["echo", "librarian"]
        .iter()
        .filter_map(|n| bodies.pid_of(n))
        .collect();
    assert_eq!(pids.len(), 2);
    lit.stop().await;
    for pid in &pids {
        let end = Instant::now() + Duration::from_secs(10);
        while alive(*pid) && Instant::now() < end {
            tokio::time::sleep(Duration::from_millis(200)).await;
        }
        assert!(!alive(*pid), "body pid {pid} outlived the kernel");
    }
    let (_, v) = (0u16, Value::Null);
    let _ = v;
    let _ = std::fs::remove_dir_all(&home);
    println!(
        "bodies proof: the Rust kernel alone seated {} bodies as processes on {}, served asks through them, streamed the words, ran the harness over the rail (run {rid}), brought the echo back as the same self ({echo_did}) after a kill, parked it after three deaths and restarted it on the word, and stopped whole — pids {pids:?} gone",
        bodies.seats.len(),
        world.scope
    );
}
