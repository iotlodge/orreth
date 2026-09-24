// PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp4, the loops · 2026-09-23
//! THE SHADOW PROOF OF THE LOOPS (canon 0008: fixture unchanged → SHADOW → the
//! door), on the dev rig, by name:
//!
//!     cargo test -p orreth-spine --features bridge --test loops -- --nocapture
//!
//! TWO KERNELS BEAT ON ONE GROUND: the Python rig whole (its residents on
//! their benches, its scheduler and intent loops ALIVE; only its dispatcher
//! held, so what dispatches is provably Rust's) and the Rust bridge lit
//! in-process on the same ground, its scheduler and intent loops alive too.
//! The beat lock is the law under test: a schedule every 5 s occurs ONCE per
//! cadence (no two occurrences closer than the cadence), though two tickers
//! beat; a watch born red turns ONCE — one `watch.turned` fact, one
//! `watch-red` observation under Resiliency, one plan to the planner, one
//! objective filed — though two turners beat. Then the doors: `/monitor` ·
//! `/schedules/<runner>` · `/harness` · `/intentions` read equal on both; a
//! human intention is stopped through the Rust door — held for the code,
//! settled by the Rust kernel on the right code (intent.stop ran in the
//! record's own transaction) — and restarted the same way; the kernel's
//! Resiliency stop is held for code-then-master and cancelled. With no rig it
//! prints "rails not up — skipped by name" and passes green without proving
//! anything; beside a live Bridge on :4600 it refuses to run.

#![cfg(feature = "bridge")]

use orreth_spine::bridge::{glass_path, light, Config};
use orreth_spine::ground::Ground;
use orreth_spine::world::{token_hex, World};
use orreth_spine::{monitor, proof, proof_live, rails};
use serde_json::{json, Value};
use std::process::Stdio;
use std::time::{Duration, Instant, SystemTime};
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

/// The Python rig WHOLE but for its dispatcher (the Rust one dispatches): its
/// loops beat beside ours. The fake mind's one reply is the planner's
/// objective — every body shares it, so the librarian answers with it too.
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

fn intention<'a>(listing: &'a Value, id: &str) -> Option<&'a Value> {
    listing["intentions"]
        .as_array()?
        .iter()
        .find(|i| i["intention_id"] == json!(id))
}

/// Poll a door until `pred` holds on its body.
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
async fn shadow_two_kernels_beat_on_one_ground_one_beat_at_a_time() {
    if !rig_up("shadow_two_kernels_beat_on_one_ground") {
        return;
    }
    if port_open(4600) {
        println!("a Bridge holds :4600 — the shadow proof refuses to run beside a live rig (stop it: scripts/dev.sh bridge stop)");
        return;
    }
    let tok = token_hex(3);
    let world = World {
        scope: format!("u:loops-{tok}"),
        ns: format!("t{tok}"),
        pg_dsn: rails::pg_dsn(),
        rabbit_url: rails::rabbit_url(),
        kafka: rails::kafka_bootstrap(),
    };
    let objective = format!("Serve the waiting ask and confirm the bench is drained ({tok}).");

    // ---- the Python kernel, whole but for its dispatcher — its loops beat
    let mut py = tokio::process::Command::new("uv")
        .args(["run", "--quiet", "python", "-u", "-c", LAUNCHER])
        .current_dir(spine_dir())
        .env("SPINE_QUEUE_NS", &world.ns)
        .env("SPINE_SCOPE", &world.scope)
        .env("SPINE_PG", &world.pg_dsn)
        .env("SHADOW_REPLY", &objective)
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

    // ---- the Rust kernel, in-process, on the same ground — its loops beat too
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
    let g = Ground::connect(&world.pg_dsn).await.unwrap();

    // ---- Resiliency: declared once per world, by whichever kernel came first
    let (_, ints) = get(rs_port, "/intentions?kind=kernel").await;
    let kernel_ints: Vec<&Value> = ints["intentions"].as_array().unwrap().iter().collect();
    assert_eq!(
        kernel_ints.len(),
        1,
        "one Resiliency, never doubled: {ints}"
    );
    let res_id = kernel_ints[0]["intention_id"].as_str().unwrap().to_string();
    assert!(kernel_ints[0]["words"]
        .as_str()
        .unwrap()
        .starts_with("keep this world resilient"));

    // ---- a schedule every 5 s through the Rust door; two tickers beat — one occurrence per cadence
    let t0 = SystemTime::now();
    let (s, made) = post(
        rs_port,
        "/schedules",
        json!({"runner": "echo", "text": "say the time, please", "every_s": 5}),
    )
    .await;
    assert_eq!(s, 201, "{made}");
    let sid = made["schedule_id"].as_str().unwrap().to_string();
    assert_eq!(
        post(
            rs_port,
            "/schedules",
            json!({"runner": "echo", "text": "x", "every_s": 2})
        )
        .await
        .0,
        400
    );

    // ---- a watch born red: one turn, one observation, one plan, one objective — though two turners beat
    let wid = monitor::add_watch(
        &g,
        &world.scope,
        "always red",
        "bodies_alive",
        ">=",
        0.0,
        "did:orreth:person:jb",
    )
    .await
    .unwrap();
    let path = "/intentions?kind=kernel";
    let res = wait_for(rs_port, path, Duration::from_secs(60), |v| {
        intention(v, &res_id).is_some_and(|i| i["objectives"] == json!(1))
    })
    .await;
    let row = intention(&res, &res_id).unwrap();
    assert_eq!(
        (
            row["observations"].clone(),
            row["turns"].clone(),
            row["objectives"].clone()
        ),
        (json!(1), json!(1), json!(1)),
        "one red, one observation, one plan, one objective: {row}"
    );
    tokio::time::sleep(Duration::from_secs(7)).await; // both turners beat on: nothing doubles
    let (_, again) = get(rs_port, path).await;
    let row = intention(&again, &res_id).unwrap();
    assert_eq!(
        (
            row["observations"].clone(),
            row["turns"].clone(),
            row["objectives"].clone()
        ),
        (json!(1), json!(1), json!(1)),
        "a standing red is never observed twice: {row}"
    );
    let turned: i64 = g
        .client()
        .query_one(
            "SELECT count(*) FROM spine_outbox WHERE convert_from(body, 'UTF8') LIKE $1 AND convert_from(body, 'UTF8') LIKE '%orreth.watch.turned.v1%'",
            &[&format!("%{wid}%")],
        )
        .await
        .unwrap()
        .get(0);
    assert_eq!(turned, 1, "one watch.turned fact for {wid}");
    let red: Vec<(String, Option<String>)> = g
        .client()
        .query(
            "SELECT marker_id, parent FROM spine_markers WHERE scope = $1 AND kind = 'watch-red' AND ref = $2",
            &[&world.scope, &wid],
        )
        .await
        .unwrap()
        .iter()
        .map(|r| (r.get(0), r.get(1)))
        .collect();
    assert_eq!(red.len(), 1, "one watch-red marker: {red:?}");
    assert_eq!(
        red[0].1.as_deref(),
        row["marker"].as_str(),
        "under Resiliency"
    );
    let turn_row = g
        .client()
        .query_one(
            "SELECT plan_ask, objective_ask FROM spine_intent_turns WHERE intention_id = $1",
            &[&res_id],
        )
        .await
        .unwrap();
    let (plan_ask, objective_ask): (String, Option<String>) = (turn_row.get(0), turn_row.get(1));
    let (_, pv) = get(rs_port, &format!("/ask/{plan_ask}")).await;
    assert_eq!(pv["target"], json!("planner"));
    assert!(
        pv["text"]
            .as_str()
            .unwrap()
            .contains("OBSERVED: a marker of kind 'watch-red'"),
        "{pv}"
    );
    let oid = objective_ask.expect("the objective was filed");
    let (_, ov) = get(rs_port, &format!("/ask/{oid}")).await;
    assert_eq!(
        ov["text"],
        json!(objective),
        "the planner's reply IS the objective"
    );
    assert_eq!(ov["target"], json!("librarian"));
    assert_eq!(
        ov["session"], row["session"],
        "filed in the intention's session"
    );
    assert_eq!(
        get(py_port, &format!("/ask/{oid}")).await.1,
        ov,
        "equal on both doors"
    );

    // ---- the cadence: occurrences one per 5 s, never two within a cadence
    let elapsed = t0.elapsed().unwrap_or_default().as_secs_f64();
    let ats: Vec<SystemTime> = g
        .client()
        .query(
            "SELECT at FROM spine_occurrences WHERE schedule_id = $1 ORDER BY at",
            &[&sid],
        )
        .await
        .unwrap()
        .iter()
        .map(|r| r.get(0))
        .collect();
    assert!(
        !ats.is_empty(),
        "the schedule occurred at least once in {elapsed:.0} s"
    );
    assert!(
        (ats.len() as f64) <= elapsed / 5.0 + 1.5,
        "{} occurrences in {elapsed:.0} s — two tickers never doubled a beat",
        ats.len()
    );
    for pair in ats.windows(2) {
        let gap = pair[1]
            .duration_since(pair[0])
            .unwrap_or_default()
            .as_secs_f64();
        assert!(
            gap >= 4.5,
            "two occurrences {gap:.2} s apart — a doubled beat"
        );
    }
    let (s, card) = get(rs_port, "/schedules/echo").await;
    assert_eq!(s, 200);
    assert_eq!(card["human"][0]["schedule_id"], json!(sid));
    assert_eq!(card["human"][0]["occurrences"], json!(ats.len()));
    assert_eq!(
        get(py_port, "/schedules/echo").await.1,
        card,
        "the card, equal on both doors"
    );
    let occ: Vec<Option<String>> = g
        .client()
        .query(
            "SELECT ref FROM spine_occurrences WHERE schedule_id = $1 ORDER BY at LIMIT 1",
            &[&sid],
        )
        .await
        .unwrap()
        .iter()
        .map(|r| r.get(0))
        .collect();
    let (_, first) = get(rs_port, &format!("/ask/{}", occ[0].clone().unwrap())).await;
    assert!(
        first["text"].as_str().unwrap().starts_with(
            "“say the time, please” — your duty every 5 seconds (every 5 s) · your first run"
        ),
        "the occurrence is framed as a duty (W21): {}",
        first["text"]
    );

    // ---- the doors read one ground
    let (s, mon) = get(rs_port, "/monitor").await;
    assert_eq!(s, 200);
    let (_, mon_py) = get(py_port, "/monitor").await;
    assert_eq!(
        mon["watches"], mon_py["watches"],
        "the watches, equal on both doors"
    );
    assert_eq!(
        mon["values"]["bodies_alive"],
        mon_py["values"]["bodies_alive"]
    );
    assert_eq!(mon["world"], json!(world.scope));
    let w0 = &mon["watches"][0];
    assert_eq!(
        (w0["state"].clone(), w0["red"].clone()),
        (json!("red"), json!(true))
    );
    assert!(
        w0["since"].is_string(),
        "the record agrees with the metric: since is shown"
    );
    assert!(w0["reads"]
        .as_str()
        .unwrap()
        .starts_with("red when bodies_alive >= 0.0 · now "));
    assert!(
        mon["benches"].is_object() && !mon["benches"].as_object().unwrap().contains_key("error"),
        "{}",
        mon["benches"]
    );
    let (s, hz) = get(rs_port, "/harness").await;
    assert_eq!(s, 200);
    let (_, hz_py) = get(py_port, "/harness").await;
    // P6.5 sp3 grew the Python harness by the Stable's four checks (every mind answers · the
    // gateway holds every mind · the meter and the gateway agree · a model change is announced);
    // the Rust kernel reads the first five until P7 sp6 ports the Stable's seam — so the five
    // are compared, and the Python door's four more are named, not hidden
    let py_checks = hz_py["checks"].as_array().unwrap();
    assert_eq!(hz["checks"].as_array().unwrap().len(), 5);
    assert_eq!(
        hz["checks"].as_array().unwrap()[..],
        py_checks[..5],
        "the five world checks, equal on both doors"
    );
    assert_eq!(
        py_checks.len(),
        9,
        "the Python door reads the Stable's four more (sp6 ports them)"
    );
    assert_eq!(
        hz["checks"][0]["name"],
        json!("a duty answered, not refused")
    );
    assert_eq!(
        post(rs_port, "/harness/run", json!({"template": "librarian"}))
            .await
            .0,
        501
    );
    assert_eq!(
        get(rs_port, "/intentions").await.1,
        get(py_port, "/intentions").await.1,
        "the intentions, equal on both doors"
    );

    // ---- rule 11 through the Rust door: a human intention stopped on the code, restarted on the code
    let me = "did:orreth:person:jb";
    let (s, b) = post(rs_port, "/enroll", json!({"person": me})).await;
    assert_eq!(s, 201);
    let secret = b["secret"].as_str().unwrap().to_string();
    let code = proof::totp(&secret, proof_live::now_unix()).unwrap();
    assert_eq!(
        post(
            rs_port,
            "/enroll/confirm",
            json!({"person": me, "code": code})
        )
        .await
        .0,
        200
    );
    let (s, made) = post(
        rs_port,
        "/ask",
        json!({"text": "keep the crew alive: whenever a watch goes red, wake me", "kind": "intention", "person": me}),
    )
    .await;
    assert_eq!(s, 201, "{made}");
    let hid = made["intention"]["intention_id"]
        .as_str()
        .unwrap()
        .to_string();
    assert_eq!(made["intention"]["kind"], json!("human"));
    let (s, held) = post(
        rs_port,
        "/intentions/stop",
        json!({"intention_id": hid, "person": me}),
    )
    .await;
    assert_eq!(s, 202, "{held}");
    assert_eq!(
        (held["level"].clone(), held["needs_code"].clone()),
        (json!("L3-code"), json!(true))
    );
    let hold = held["held"].as_str().unwrap().to_string();
    let (_, hv) = get(rs_port, &format!("/ask/{hold}")).await;
    assert_eq!(hv["status"], json!("awaiting-confirm"));
    assert!(
        hv["reply"]
            .as_str()
            .unwrap()
            .starts_with("This needs your code. Stopping the human's intention"),
        "{}",
        hv["reply"]
    );
    assert_eq!(
        post(
            rs_port,
            "/confirm",
            json!({"ask_id": hold, "approve": true, "person": me, "code": "000000"})
        )
        .await
        .0,
        403,
        "a wrong code: the one face"
    );
    let code = proof::totp(&secret, proof_live::now_unix()).unwrap();
    let (s, settled) = post(
        rs_port,
        "/confirm",
        json!({"ask_id": hold, "approve": true, "person": me, "code": code}),
    )
    .await;
    assert_eq!(s, 202, "{settled}");
    let (_, hv) = get(rs_port, &format!("/ask/{hold}")).await;
    assert_eq!(
        (hv["status"].clone(), hv["proof"].clone()),
        (json!("replied"), json!("L3-code"))
    );
    assert!(
        hv["reply"]
            .as_str()
            .unwrap()
            .starts_with("Done, on your code: the intention “keep the crew alive"),
        "{}",
        hv["reply"]
    );
    let (_, ints) = get(rs_port, "/intentions?kind=human").await;
    let h = intention(&ints, &hid).unwrap();
    assert_eq!(
        (h["active"].clone(), h["stopped_by"].clone()),
        (json!(false), json!(me))
    );
    assert_eq!(
        get(py_port, "/intentions?kind=human").await.1,
        ints,
        "the stop, equal on both doors"
    );
    // its reverse (W20)
    let (s, held) = post(
        rs_port,
        "/intentions/restart",
        json!({"intention_id": hid, "person": me}),
    )
    .await;
    assert_eq!(s, 202);
    let hold = held["held"].as_str().unwrap().to_string();
    let code = proof::totp(&secret, proof_live::now_unix()).unwrap();
    assert_eq!(
        post(
            rs_port,
            "/confirm",
            json!({"ask_id": hold, "approve": true, "person": me, "code": code})
        )
        .await
        .0,
        202
    );
    let (_, ints) = get(rs_port, "/intentions?kind=human").await;
    let h = intention(&ints, &hid).unwrap();
    assert_eq!(
        (
            h["active"].clone(),
            h["restarted_by"].clone(),
            h["stopped_by"].clone()
        ),
        (json!(true), json!(me), json!(me)),
        "history whole: {h}"
    );
    assert_eq!(
        post(
            rs_port,
            "/intentions/stop",
            json!({"intention_id": "int_nobody"})
        )
        .await
        .0,
        404
    );
    // the kernel's own: code, then master — cancelled here, the default
    let (s, held) = post(
        rs_port,
        "/intentions/stop",
        json!({"intention_id": res_id, "person": me}),
    )
    .await;
    assert_eq!(s, 202);
    assert_eq!(
        (held["level"].clone(), held["needs_code"].clone()),
        (json!("L3-master"), json!(true))
    );
    let hold = held["held"].as_str().unwrap().to_string();
    let (s, c) = post(
        rs_port,
        "/confirm",
        json!({"ask_id": hold, "approve": false, "person": me}),
    )
    .await;
    assert_eq!(s, 202, "{c}");
    let (_, hv) = get(rs_port, &format!("/ask/{hold}")).await;
    assert_eq!(hv["status"], json!("cancelled"));
    assert_eq!(
        intention(&get(rs_port, "/intentions?kind=kernel").await.1, &res_id).unwrap()["active"],
        json!(true)
    );

    let (_, shadow) = get(rs_port, "/shadow").await;
    println!(
        "loops · SHADOW: two kernels beat on {} (Python rig :{py_port} + Rust :{rs_port}) — schedule {sid} occurred {} times in {elapsed:.0} s, never twice within a cadence; watch {wid} born red turned ONCE (fact 1 · watch-red 1 · plan {plan_ask} · objective {oid}); /monitor · /schedules · /harness · /intentions equal on both doors; a human intention {hid} stopped and restarted on the code through the Rust door; the kernel's stop held for code-then-master and cancelled; meter {shadow}",
        world.scope, ats.len()
    );

    // ---- stopped whole
    py_stdin.write_all(b"stop\n").await.unwrap();
    drop(py_stdin);
    let _ = tokio::time::timeout(Duration::from_secs(60), py.wait()).await;
    let _ = py.kill().await;
    lit.stop().await;
}
