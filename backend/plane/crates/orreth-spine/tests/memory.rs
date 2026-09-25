// PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp5, memory and the export · 2026-09-24
//! THE SHADOW PROOF OF MEMORY AND THE EXPORT (canon 0008, P7 sp5): two
//! kernels on one ground — the Python reference and the Rust bridge — read
//! ONE Record. A memory landed by the Rust kernel is recalled verbatim on
//! both doors, as of now and by its lineage; a session digested by the Rust
//! kernel reads byte-identical on the Python door and the Python kernel
//! rebuilds it to the SAME hash (nothing new); the compliance export from
//! either door is SIGNED by the same kernel self (one seed, both spines),
//! agrees on its root, and verifies; a purge leaves both doors empty.
//! Needs the rig (scripts/dev.sh up) and NO Bridge on :4600.
//!   cargo test -p orreth-spine --features bridge --test memory -- --nocapture

use orreth_spine::bridge::{glass_path, light, Config};
use orreth_spine::export;
use orreth_spine::ground::Ground;
use orreth_spine::rails;
use orreth_spine::store;
use orreth_spine::world::{token_hex, World};
use serde_json::{json, Value};
use std::process::Stdio;
use std::time::{Duration, Instant};
use tokio::io::{AsyncBufReadExt, AsyncReadExt, AsyncWriteExt, BufReader};
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

/// The Python rig whole (its echo answers), on the same ground and the same kernel seed.
const LAUNCHER: &str = r#"
import os, sys
from orreth_spine import glass, gateway
rig = glass.BridgeRig(gateway=gateway.FakeGateway(reply="a thought from the fake mind"), port=0, home=None, second=True)
rig.start()
ok = rig.feed_ready.wait(60)
print(f"python: ready port={rig.port} feed={ok} kernel={rig.kernel.did}", flush=True)
sys.stdin.readline()
rig.stop()
print("python: stopped whole", flush=True)
"#;

async fn http(port: u16, method: &str, path: &str, body: Option<&Value>) -> (u16, String, String) {
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
    let (head, body) = text
        .split_once("\r\n\r\n")
        .map(|(h, b)| (h.to_string(), b.to_string()))
        .unwrap_or_default();
    (status, head, body)
}

async fn get(port: u16, path: &str) -> (u16, Value) {
    let (s, _, b) = http(port, "GET", path, None).await;
    (s, serde_json::from_str(&b).unwrap_or(Value::Null))
}

async fn post(port: u16, path: &str, body: Value) -> (u16, Value) {
    let (s, _, b) = http(port, "POST", path, Some(&body)).await;
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

#[tokio::test]
async fn shadow_two_kernels_read_one_record_and_sign_as_one_self() {
    if !rig_up("shadow_two_kernels_read_one_record") {
        return;
    }
    if port_open(4600) {
        println!("a Bridge holds :4600 — the shadow proof refuses to run beside a live rig (stop it: scripts/dev.sh bridge stop)");
        return;
    }
    let tok = token_hex(3);
    let world = World {
        scope: format!("u:memory-{tok}"),
        ns: format!("t{tok}"),
        pg_dsn: rails::pg_dsn(),
        rabbit_url: rails::rabbit_url(),
        kafka: rails::kafka_bootstrap(),
    };
    let person = "did:orreth:person:jb".to_string();
    let kernel_home = std::env::temp_dir().join(format!("orreth-kernel-{tok}"));
    std::env::set_var("SPINE_KERNEL_HOME", &kernel_home); // ONE seed, both spines

    // ---- the Python kernel, whole
    let mut py = tokio::process::Command::new("uv")
        .args(["run", "--quiet", "python", "-u", "-c", LAUNCHER])
        .current_dir(spine_dir())
        .env("SPINE_QUEUE_NS", &world.ns)
        .env("SPINE_SCOPE", &world.scope)
        .env("SPINE_PG", &world.pg_dsn)
        .env("SPINE_KERNEL_HOME", &kernel_home)
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::inherit())
        .spawn()
        .expect("uv runs the Python reference");
    let mut py_stdin = py.stdin.take().unwrap();
    let mut py_lines = BufReader::new(py.stdout.take().unwrap()).lines();
    let ready = tokio::time::timeout(Duration::from_secs(120), async {
        loop {
            match py_lines.next_line().await {
                Ok(Some(l)) if l.starts_with("python: ready") => return l,
                Ok(Some(l)) => println!("{l}"),
                _ => panic!("the Python rig ended before it was ready"),
            }
        }
    })
    .await
    .expect("the Python rig became ready in time");
    println!("{ready}");
    let py_port: u16 = ready
        .split("port=")
        .nth(1)
        .and_then(|r| r.split_whitespace().next())
        .and_then(|p| p.parse().ok())
        .expect("the Python rig printed its port");
    let py_kernel = ready
        .split("kernel=")
        .nth(1)
        .map(|s| s.trim().to_string())
        .expect("the Python kernel's DID");

    // ---- the Rust kernel, in-process, on the same ground
    let lit = light(Config {
        port: 0,
        world: world.clone(),
        glass: glass_path(),
        masters: String::new(),
        human_zone: "America/Denver".into(),
    })
    .await
    .expect("the Rust bridge lights");
    let rs_port = lit.port;
    assert!(
        lit.wait_ready(Duration::from_secs(60)).await,
        "the Rust feed and dispatcher hold their assignments"
    );
    let mut g = Ground::connect(&world.pg_dsn).await.unwrap();
    g.ensure_all().await.unwrap();

    // the human's session opens first: what lands in its span is what its digest acquires
    let (st, made) = post(rs_port, "/sessions", json!({"person": person})).await;
    assert_eq!(st, 201);
    let sid = made["session_id"].as_str().unwrap().to_string();

    // ---- 1. a memory landed by the Rust kernel is recalled verbatim on both doors
    let by = "did:orreth:agent:memoryproof";
    let h1 = store::put(
        &mut g,
        &world.scope,
        by,
        "in",
        "librarian",
        "walk.note",
        "JB likes plain words.",
    )
    .await
    .unwrap();
    let path = "/recall?ref=librarian/walk.note";
    let (s1, r1) = get(rs_port, path).await;
    let (s2, r2) = get(py_port, path).await;
    assert_eq!((s1, s2), (200, 200), "both doors recall");
    assert_eq!(r1["memory"], r2["memory"], "the same memory on both doors");
    assert_eq!(r1["memory"]["hash"], json!(h1));
    assert_eq!(r1["memory"]["body"], json!("JB likes plain words."));
    // the sibling law: changed words supersede; both doors read the new body and the same lineage
    let h2 = store::put(
        &mut g,
        &world.scope,
        by,
        "in",
        "librarian",
        "walk.note",
        "JB likes plain words and a quiet monitor.",
    )
    .await
    .unwrap();
    assert_ne!(h1, h2);
    assert_eq!(
        get(py_port, path).await.1["memory"]["body"],
        json!("JB likes plain words and a quiet monitor.")
    );
    let (_, l1) = get(rs_port, "/recall?ref=librarian/walk.note&history=1").await;
    let (_, l2) = get(py_port, "/recall?ref=librarian/walk.note&history=1").await;
    assert_eq!(l1, l2, "the lineage reads equal");
    assert_eq!(l1["history"].as_array().unwrap().len(), 2);
    assert_eq!(l1["history"][1]["supersedes"], json!(h1));
    // the same words again land nothing
    assert_eq!(
        store::put(
            &mut g,
            &world.scope,
            by,
            "in",
            "librarian",
            "walk.note",
            "JB likes plain words and a quiet monitor."
        )
        .await
        .unwrap(),
        h2
    );

    // ---- 2. a session digested by the Rust kernel reads byte-identical on the Python door
    let (st, asked) = post(py_port, "/ask", json!({"text": "echo, say the word HERON once.", "to": ["echo"], "person": person, "session": sid})).await;
    assert_eq!(st, 201, "the Python door took the ask: {asked}");
    let aid = asked["ids"][0].as_str().unwrap().to_string();
    wait_for(
        py_port,
        &format!("/ask/{aid}"),
        Duration::from_secs(60),
        |v| v["status"] == json!("replied"),
    )
    .await;
    // the roll closes the span (the episode boundary, MEM-3): the Rust kernel builds the archived
    // session's digest at the roll — an OPEN session's summary moves as memories land in its span
    let (st, rolled) = post(
        rs_port,
        "/sessions",
        json!({"person": person, "archive": sid}),
    )
    .await;
    assert_eq!(st, 201, "the roll on the Rust door: {rolled}");
    let (_, d1) = get(rs_port, &format!("/digest/{sid}")).await;
    let (_, d2) = get(py_port, &format!("/digest/{sid}")).await;
    assert_eq!(d1, d2, "the digest reads equal on both doors");
    assert!(
        d1["body"]
            .as_str()
            .unwrap()
            .contains("asked: echo, say the word HERON once."),
        "{d1}"
    );
    assert!(
        d1["body"]
            .as_str()
            .unwrap()
            .contains("acquired [librarian/walk.note]"),
        "{d1}"
    );
    // the Python kernel rebuilds it: the same substance, the same hash, nothing new
    let (st, again) = post(
        py_port,
        "/digest",
        json!({"session": sid, "person": person}),
    )
    .await;
    assert_eq!(
        (st, again["new"].clone(), again["hash"].clone()),
        (200, json!(false), d1["hash"].clone()),
        "byte-identical across kernels — the Rust digest: {d1} · the Python rebuild: {again}"
    );
    let short = |v: &Value| {
        v["sessions"]
            .as_array()
            .unwrap()
            .iter()
            .find(|s| s["session_id"] == json!(sid))
            .map(|s| s["short_version"].clone())
    };
    let (_, s1) = get(rs_port, &format!("/sessions?person={person}")).await;
    let (_, s2) = get(py_port, &format!("/sessions?person={person}")).await;
    assert_eq!(short(&s1), short(&s2));
    assert!(
        short(&s1).is_some_and(|v| v.is_string()),
        "the short version rides the listing"
    );

    // ---- 3. the export from either door is SIGNED by the same kernel self and verifies
    let (st, e1) = get(rs_port, &format!("/export?person={person}&session={sid}")).await;
    let (st2, e2) = get(py_port, &format!("/export?person={person}&session={sid}")).await;
    assert_eq!((st, st2), (200, 200));
    assert_eq!(
        e1["signed_by"], e2["signed_by"],
        "one seed, one self on both spines"
    );
    assert_eq!(e1["signed_by"], json!(py_kernel));
    assert!(e1["signed_by"]
        .as_str()
        .unwrap()
        .starts_with("did:orreth:kernel:"));
    assert_eq!(e1["signer_key"], e2["signer_key"]);
    assert_eq!(
        e1["root_hash"], e2["root_hash"],
        "the same rows, the same chain"
    );
    assert_eq!(
        e1["rows"].as_array().unwrap().len(),
        e2["rows"].as_array().unwrap().len()
    );
    assert!(
        e1["rows"].as_array().unwrap().len() >= 2,
        "an ask and a reply at least: {e1}"
    );
    assert!(
        export::verify(&e1) && export::verify(&e2),
        "both bundles verify"
    );
    assert_eq!(e1["summary"]["chain_broken"], json!(0));
    let (st, head, csv) = http(
        rs_port,
        "GET",
        &format!("/export?person={person}&session={sid}&format=csv"),
        None,
    )
    .await;
    assert_eq!(st, 200);
    assert!(
        head.to_lowercase().contains("content-type: text/csv"),
        "{head}"
    );
    assert!(
        csv.starts_with("at,kind,ref,person,authority_chain,chain_status,proof,"),
        "{csv}"
    );
    let (_, _, csv_py) = http(
        py_port,
        "GET",
        &format!("/export?person={person}&session={sid}&format=csv"),
        None,
    )
    .await;
    assert_eq!(
        csv.lines().count(),
        csv_py.lines().count(),
        "the same lines from both doors"
    );

    // ---- 4. a purge leaves both doors empty; the digest that cited it is rebuilt without the words
    let purged = store::purge(&mut g, &world.scope, by, "librarian", "walk.note")
        .await
        .unwrap();
    assert_eq!(purged["versions"], json!(2));
    assert_eq!(get(rs_port, path).await.0, 404);
    assert_eq!(get(py_port, path).await.0, 404);
    let n = orreth_spine::digest::rebuild_citing(
        &mut g,
        &world.scope,
        "librarian/walk.note",
        "the digest builder",
        "America/Denver",
    )
    .await
    .unwrap();
    assert_eq!(n, 1);
    let (_, d3) = get(py_port, &format!("/digest/{sid}")).await;
    assert!(!d3["body"].as_str().unwrap().contains("walk.note"), "{d3}");
    assert_eq!(d3["supersedes"], d1["hash"]);

    // ---- down, whole
    py_stdin.write_all(b"\n").await.unwrap();
    let _ = tokio::time::timeout(Duration::from_secs(60), py.wait()).await;
    lit.stop().await;
    let _ = std::fs::remove_dir_all(&kernel_home);
    println!(
        "memory proof: one Record, one self — {} export rows, signed by {}",
        e1["rows"].as_array().unwrap().len(),
        e1["signed_by"]
    );
}
