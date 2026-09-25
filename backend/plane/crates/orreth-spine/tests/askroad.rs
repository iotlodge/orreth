// PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp3, the ask road · 2026-09-22
// Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp6, the bodies' seam: the Config's bodies dial · 2026-09-24
// Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp4: the Analyzer's two reads converge instead of racing a body still acquiring · 2026-09-23
//! THE SHADOW PROOF of the ask road (canon 0008: fixture unchanged → SHADOW →
//! the door), on the dev rig, by name:
//!
//!     cargo test -p orreth-spine --features bridge --test askroad -- --nocapture
//!
//! The Python rig's residents stand on THEIR benches (the test starts them
//! through `uv`, on this test's own queue namespace and scope, with the
//! Python DISPATCHER HELD — one world, one dispatcher, so what dispatches is
//! provably the Rust one); the Rust bridge is lit in-process on a free port
//! on the SAME ground. An ask submitted through the Rust door is dispatched
//! by the Rust dispatcher (its meter says 1; the inbox footprint under
//! `glass-dispatcher` is one row, `done`), served by the Python librarian,
//! and its reply shows at the Rust door AND the Python door — the two views
//! equal as JSON; `/analyzer` equal on both. Then W19 at the door, a fan-out
//! to two benches, the proof doors' one face, a rolled session, and the
//! feed's notice — all through the Rust door alone, as a browser would.
//! With no rig it prints "rails not up — skipped by name" and passes green
//! without proving anything; beside a live Bridge on :4600 it refuses to run.

#![cfg(feature = "bridge")]

use orreth_spine::bridge::{glass_path, light, Config};
use orreth_spine::ground::Ground;
use orreth_spine::world::{token_hex, World};
use orreth_spine::{proof, proof_live, rails};
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

/// The Python rig, residents only: the same BridgeRig the Python Bridge
/// lights, on THIS test's benches and scope, its dispatcher thread held back
/// before start (the Rust one dispatches), a fake mind with a known reply.
/// It prints its port when the feed holds an assignment, then waits for a
/// line on stdin and stops whole.
const LAUNCHER: &str = r#"
import os, sys
from orreth_spine import glass, gateway
rig = glass.BridgeRig(gateway=gateway.FakeGateway(reply=os.environ['SHADOW_REPLY']), port=0, home=None)
rig._threads = [t for t in rig._threads if t._target != rig._dispatch_loop]   # the Python dispatcher HELD
rig.start()
ok = rig.feed_ready.wait(60)
print(f"python: ready port={rig.port} feed={ok} crew=" + ",".join(r.name for r in rig.residents), flush=True)
sys.stdin.readline()
rig.stop()
print("python: stopped whole", flush=True)
"#;

/// One HTTP/1.1 exchange, `Connection: close` — as a browser's fetch, no client crate.
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

/// Poll the ask's door until its status is one of `want`.
async fn wait_status(port: u16, ask_id: &str, want: &[&str], within: Duration) -> Value {
    let end = Instant::now() + within;
    let mut last = Value::Null;
    while Instant::now() < end {
        let (_, v) = get(port, &format!("/ask/{ask_id}")).await;
        if v["status"].as_str().is_some_and(|s| want.contains(&s)) {
            return v;
        }
        last = v;
        tokio::time::sleep(Duration::from_millis(400)).await;
    }
    panic!("{ask_id} never reached {want:?}; last: {}", last["status"]);
}

#[tokio::test]
async fn shadow_an_ask_through_the_rust_door_is_served_by_the_python_librarian_and_shows_at_both() {
    if !rig_up("shadow_an_ask_through_the_rust_door") {
        return;
    }
    if port_open(4600) {
        println!("a Bridge holds :4600 — the shadow proof refuses to run beside a live rig (stop it: scripts/dev.sh bridge stop)");
        return;
    }
    let tok = token_hex(3);
    let world = World {
        scope: format!("u:shadow-{tok}"),
        ns: format!("t{tok}"),
        pg_dsn: rails::pg_dsn(),
        rabbit_url: rails::rabbit_url(),
        kafka: rails::kafka_bootstrap(),
    };
    let reply = format!("The whole answer from the Python librarian, marker {tok}.");

    // ---- the Python residents on their benches, the Python dispatcher held
    let mut py = tokio::process::Command::new("uv")
        .args(["run", "--quiet", "python", "-u", "-c", LAUNCHER])
        .current_dir(spine_dir())
        .env("SPINE_QUEUE_NS", &world.ns)
        .env("SPINE_SCOPE", &world.scope)
        .env("SPINE_PG", &world.pg_dsn)
        .env("SHADOW_REPLY", &reply)
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
    assert!(
        ready.contains("feed=True"),
        "the Python feed holds an assignment: {ready}"
    );
    let py_port: u16 = ready
        .split("port=")
        .nth(1)
        .and_then(|r| r.split_whitespace().next())
        .and_then(|p| p.parse().ok())
        .expect("the Python rig printed its port");

    // ---- the Rust bridge, in-process, on the same ground
    let lit = light(Config {
        port: 0,
        world: world.clone(),
        glass: glass_path(),
        masters: String::new(),
        human_zone: "America/Denver".into(),
        bodies: false, // beside the Python rig: its bodies serve
        ephemeral: true,
        spine: spine_dir(),
    })
    .await
    .expect("the Rust bridge lights");
    let rs_port = lit.port;
    assert!(
        lit.wait_ready(Duration::from_secs(60)).await,
        "the Rust feed and dispatcher hold their assignments"
    );
    let (s, page) = http(rs_port, "GET", "/", None).await;
    assert_eq!(s, 200);
    assert!(
        page.contains("id=\"chat") && page.contains("Escape"),
        "the one page, unchanged"
    );

    // ---- the ask through the RUST door
    let (s, filed) = post(
        rs_port,
        "/ask",
        json!({"text": format!("Say the whole answer (marker {tok})."), "to": ["librarian"]}),
    )
    .await;
    assert_eq!(s, 201, "{filed}");
    let ask_id = filed["ids"][0].as_str().expect("an id").to_string();
    assert!(ask_id.starts_with("ask_"));
    let view = wait_status(rs_port, &ask_id, &["replied"], Duration::from_secs(90)).await;
    assert_eq!(view["reply"], json!(reply), "the FULL reply");
    assert!(
        view["journey"].as_array().is_some_and(|j| j
            .iter()
            .any(|n| n.as_str().unwrap_or("").contains("librarian"))),
        "the ask wore its way: {}",
        view["journey"]
    );
    assert_eq!(view["scope"], json!(world.scope));
    assert!(view["served_by"]
        .as_str()
        .is_some_and(|d| d.starts_with("did:")));
    assert!(view["replied_at"].is_string() && view["asked_at"].is_string());
    // one ground, one truth: the PYTHON door shows the same view, whole
    let (s, py_view) = get(py_port, &format!("/ask/{ask_id}")).await;
    assert_eq!(s, 200);
    assert_eq!(py_view, view, "the two doors read one ground");
    // who dispatched: the Rust meter says one; the inbox footprint under the shared consumer name is one row, done
    let (_, shadow) = get(rs_port, "/shadow").await;
    assert_eq!(
        shadow["dispatched"],
        json!(1),
        "the Rust dispatcher dispatched it: {shadow}"
    );
    assert_eq!(shadow["consumer"], json!("glass-dispatcher"));
    let g = Ground::connect(&world.pg_dsn).await.unwrap();
    let mid: String = g
        .client()
        .query_one(
            "SELECT message_id FROM spine_outbox WHERE convert_from(body, 'UTF8') LIKE $1 AND convert_from(body, 'UTF8') LIKE '%orreth.ask.received.v1%' ORDER BY outbox_id LIMIT 1",
            &[&format!("%{ask_id}%")],
        )
        .await
        .unwrap()
        .get(0);
    let footprints: Vec<(String, String)> = g
        .client()
        .query("SELECT consumer, status FROM spine_inbox WHERE message_id = $1 AND consumer = 'glass-dispatcher'", &[&mid])
        .await
        .unwrap()
        .iter()
        .map(|r| (r.get(0), r.get(1)))
        .collect();
    assert_eq!(
        footprints,
        vec![("glass-dispatcher".to_string(), "done".to_string())],
        "exactly one dispatch of {mid}"
    );
    // the two doors read one ground — read until they agree (a body still
    // acquiring at boot grows a root's counts between two reads: P7 sp4 saw
    // MITL's `action` count move 46 → 48 across the pair)
    let end = Instant::now() + Duration::from_secs(30);
    let (mut an_rs, mut an_py) = (Value::Null, Value::Null);
    while Instant::now() < end {
        an_rs = get(rs_port, "/analyzer").await.1;
        an_py = get(py_port, "/analyzer").await.1;
        if an_rs == an_py {
            break;
        }
        tokio::time::sleep(Duration::from_millis(500)).await;
    }
    assert_eq!(an_rs, an_py, "the Analyzer's origins, equal on both doors");
    assert!(
        an_rs["origins"]
            .as_array()
            .is_some_and(|o| o.iter().any(|r| r["ref"] == json!(ask_id))),
        "the ask is a root: {an_rs}"
    );

    // ---- W19: a body that is not here is answered at the door
    let (s, filed) = post(
        rs_port,
        "/ask",
        json!({"text": "ghost, hello", "to": ["ghost"]}),
    )
    .await;
    assert_eq!(s, 201);
    let ghost = filed["ids"][0].as_str().unwrap().to_string();
    let (_, v) = get(rs_port, &format!("/ask/{ghost}")).await;
    assert_eq!(v["status"], json!("refused"));
    assert_eq!(
        v["reply"],
        json!("ghost is not here — no body of that name has joined this world")
    );
    assert_eq!(v["served_by"], json!("the kernel"));
    assert_eq!(get(py_port, &format!("/ask/{ghost}")).await.1, v);

    // ---- the proof doors, the one face (P6 sp1's door test, through the Rust door)
    let me = "did:orreth:person:jb";
    assert_eq!(
        get(rs_port, &format!("/proof?person={me}")).await,
        (200, json!({"person": me, "enrolled": false, "masters": []}))
    );
    let (s, b) = post(rs_port, "/enroll", json!({"person": me})).await;
    assert_eq!(s, 201);
    assert!(
        b["uri"]
            .as_str()
            .unwrap()
            .starts_with("otpauth://totp/Orreth:jb"),
        "{b}"
    );
    assert!(b["qr"]
        .as_str()
        .unwrap()
        .starts_with("data:image/png;base64,"));
    assert_eq!(b["re_enrolled"], json!(false));
    let one_face = json!({"error": "not confirmed"});
    assert_eq!(
        post(
            rs_port,
            "/enroll/confirm",
            json!({"person": me, "code": "000000"})
        )
        .await,
        (403, one_face.clone())
    );
    let code = proof::totp(b["secret"].as_str().unwrap(), proof_live::now_unix()).unwrap();
    assert_eq!(
        post(
            rs_port,
            "/enroll/confirm",
            json!({"person": me, "code": code})
        )
        .await,
        (200, json!({"person": me, "enrolled": true}))
    );
    assert_eq!(
        get(rs_port, &format!("/proof?person={me}")).await.1["enrolled"],
        json!(true)
    );
    assert_eq!(
        get(py_port, &format!("/proof?person={me}")).await.1["enrolled"],
        json!(true),
        "the Python door sees the enrollment"
    );
    assert_eq!(
        post(rs_port, "/enroll", json!({"person": me})).await,
        (403, one_face.clone())
    );
    assert_eq!(
        post(
            rs_port,
            "/confirm",
            json!({"ask_id": "ask_nobody", "approve": true})
        )
        .await,
        (403, one_face.clone())
    );

    // ---- a session rolled, an ask in it (with the feed listening), the fan-out to two benches
    let mut feed = TcpStream::connect(("127.0.0.1", rs_port)).await.unwrap();
    feed.write_all(b"GET /feed HTTP/1.1\r\nHost: 127.0.0.1\r\naccept: text/event-stream\r\n\r\n")
        .await
        .unwrap();
    let (s, rolled) = post(
        rs_port,
        "/sessions",
        json!({"person": me, "title": "the shadow"}),
    )
    .await;
    assert_eq!(s, 201);
    let sid = rolled["session_id"].as_str().unwrap().to_string();
    assert!(sid.starts_with("ses_"));
    let (s, filed) = post(
        rs_port,
        "/ask",
        json!({"text": "say it twice", "to": ["librarian", "echo"], "session": sid}),
    )
    .await;
    assert_eq!(s, 201);
    let ids: Vec<String> = filed["ids"]
        .as_array()
        .unwrap()
        .iter()
        .map(|i| i.as_str().unwrap().to_string())
        .collect();
    assert_eq!(ids.len(), 2, "a fan-out is one ask per named body");
    let v1 = wait_status(rs_port, &ids[0], &["replied"], Duration::from_secs(90)).await;
    let v2 = wait_status(rs_port, &ids[1], &["replied"], Duration::from_secs(90)).await;
    assert_eq!(
        (v1["target"].clone(), v2["target"].clone()),
        (json!("librarian"), json!("echo"))
    );
    assert_eq!(v1["reply"], json!(reply));
    assert_eq!(v2["reply"], json!("say it twice"), "echo repeats");
    assert_eq!(v1["session"], json!(sid));
    let (s, listed) = get(rs_port, &format!("/sessions?person={me}")).await;
    assert_eq!(s, 200);
    let mine = listed["sessions"]
        .as_array()
        .unwrap()
        .iter()
        .find(|x| x["session_id"] == json!(sid))
        .cloned()
        .expect("the rolled session is listed");
    assert_eq!(
        (
            mine["asks"].clone(),
            mine["title"].clone(),
            mine["last_words"].clone()
        ),
        (json!(2), json!("the shadow"), json!("say it twice"))
    );
    let (s, loaded) = get(rs_port, &format!("/session/{sid}")).await;
    assert_eq!(s, 200);
    assert_eq!(
        loaded["asks"]
            .as_array()
            .unwrap()
            .iter()
            .map(|a| a["ask_id"].clone())
            .collect::<Vec<_>>(),
        vec![json!(ids[0]), json!(ids[1])]
    );
    assert_eq!(
        get(py_port, &format!("/session/{sid}")).await.1,
        loaded,
        "the session, equal on both doors"
    );
    assert_eq!(
        get(rs_port, "/session/ses_nobody").await,
        (404, json!({"error": "no such session"}))
    );
    // the feed carried the notices: the ask received, its reply
    let mut seen = String::new();
    let mut buf = [0u8; 4096];
    let end = Instant::now() + Duration::from_secs(30);
    while Instant::now() < end
        && !(seen.contains(&format!("\"ref\":\"{}\"", ids[0])) && seen.contains("orreth.reply.v1"))
    {
        match tokio::time::timeout(Duration::from_secs(2), feed.read(&mut buf)).await {
            Ok(Ok(n)) if n > 0 => seen.push_str(&String::from_utf8_lossy(&buf[..n])),
            Ok(Ok(_)) => break,
            _ => {}
        }
    }
    assert!(
        seen.contains("text/event-stream"),
        "the feed is SSE: {seen}"
    );
    assert!(
        seen.contains(&format!("\"ref\":\"{}\"", ids[0])) && seen.contains("orreth.reply.v1"),
        "the feed carried the ask and its reply: {seen}"
    );
    assert!(
        seen.lines().any(|l| l.starts_with("id: ")),
        "every notice wears its revision"
    );
    drop(feed);
    let (_, crew) = get(rs_port, "/crew").await;
    assert!(
        crew["crew"].as_array().is_some_and(|c| c
            .iter()
            .any(|b| b["name"] == json!("librarian") && b["alive"] == json!(true))),
        "the crew door sees the living librarian: {crew}"
    );
    assert_eq!(
        get(rs_port, "/crew").await.1,
        get(py_port, "/crew").await.1,
        "the crew, equal on both doors"
    );
    let (s, shelf) = get(rs_port, "/services").await;
    assert_eq!(s, 200);
    assert_eq!(
        shelf["kinds"],
        json!(["tool", "mcp", "store", "source", "mind"])
    );
    assert_eq!(
        shelf["services"],
        get(py_port, "/services").await.1["services"],
        "the shelf, equal on both doors"
    );
    let (_, shadow) = get(rs_port, "/shadow").await;
    println!(
        "askroad · SHADOW: the Rust door :{rs_port} filed {ask_id} → the RUST dispatcher (group {}, inbox consumer glass-dispatcher) dispatched it once → the PYTHON librarian (rig :{py_port}, benches '{}') served it → the reply showed at :{rs_port} AND :{py_port}, the views equal; /analyzer equal; W19 refused {ghost} at the door; the fan-out reached librarian + echo; the proof doors wore one face; session {sid} rolled, listed, loaded; the feed carried the notices; meter {shadow}",
        lit.group, world.ns
    );

    // ---- stopped whole
    py_stdin.write_all(b"stop\n").await.unwrap();
    drop(py_stdin);
    let _ = tokio::time::timeout(Duration::from_secs(60), py.wait()).await;
    let _ = py.kill().await;
    lit.stop().await;
}
