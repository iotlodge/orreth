// PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp8 row 3, THE GATE (a): the human seat's proof · 2026-09-26
//! THE GATE'S PROOF (canon 0005 sp8 row 3 · 0006 §3 · covenant rules 3 and 4),
//! on the dev rig, by name:
//!
//!     cargo test -p orreth-spine --features bridge --test gate -- --nocapture
//!
//! One Rust kernel lit alone (no bodies). Before anyone holds the ground every
//! door but the open ones answers the unseated with one face (401). THE
//! CEREMONY: the first person to prove an authenticator becomes the OWNER — a
//! master from that moment; their seat governs. A second person, enrolled on
//! the owner's word, holds a seat that reads and writes but cannot govern (the
//! proof's one face at a governing door, and at enrolling a third). A stranger
//! cannot enroll once the ground is held. A seat minted by another kernel and a
//! seat whose bytes were touched are not seats. The browser origin is closed:
//! a knock wearing a foreign Origin is refused before its body is read; this
//! door's own origin passes. A seat left is a seat no more. The feed carries
//! the seat as its query. And the knock ceiling stands at every door: a flood
//! from one seat meets «the door is busy for you — try again shortly».
//! With no rig it prints "rails not up — skipped by name" and passes green.

#![cfg(feature = "bridge")]

use orreth_spine::bridge::{glass_path, light, Config};
use orreth_spine::kernel_self::KernelSelf;
use orreth_spine::world::{token_hex, World};
use orreth_spine::{proof, proof_live, rails, seat};
use serde_json::{json, Value};
use std::time::Duration;
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

/// One knock, with whatever headers the case needs (a seat, an origin, none).
async fn knock(
    port: u16,
    method: &str,
    path: &str,
    body: Option<&Value>,
    headers: &[(&str, &str)],
) -> (u16, String, Value) {
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
    let _ = tokio::time::timeout(Duration::from_secs(5), s.read_to_end(&mut raw)).await;
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
    (
        status,
        head,
        serde_json::from_str(&body).unwrap_or(Value::Null),
    )
}

fn bearer(wire: &str) -> String {
    format!("Bearer {wire}")
}

#[tokio::test]
async fn the_gate_seats_the_owner_first_and_every_door_reads_the_seat() {
    if !rig_up("the_gate_seats_the_owner_first_and_every_door_reads_the_seat") {
        return;
    }
    if port_open(4600) {
        println!("a Bridge holds :4600 — the gate proof refuses to run beside a live rig (stop it: scripts/dev.sh bridge stop)");
        return;
    }
    let tok = token_hex(3);
    let world = World {
        scope: format!("u:gate-{tok}"),
        ns: format!("t{tok}"),
        pg_dsn: rails::pg_dsn(),
        rabbit_url: rails::rabbit_url(),
        kafka: rails::kafka_bootstrap(),
    };
    let home = std::env::temp_dir().join(format!("orreth-gate-{tok}"));
    // the ceiling dialed low for the proof (this binary alone): a burst of 8, refilling 4 a second
    std::env::set_var("SPINE_CEILING_BURST", "8");
    std::env::set_var("SPINE_CEILING_RATE", "4");
    let lit = light(Config {
        port: 0,
        world: world.clone(),
        glass: glass_path(),
        masters: String::new(),
        human_zone: "America/Denver".into(),
        bodies: false,
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
    let one_face = json!({"error": "not confirmed"});
    let not_seated = json!({"error": "not seated"});
    let host_origin = format!("http://127.0.0.1:{port}");

    // ---- 1. nobody holds the ground: the open doors answer, every other door says "not seated"
    let (s, _, v) = knock(port, "GET", "/seat", None, &[]).await;
    assert_eq!(
        (s, v["ceremony"].clone(), v["hours"].clone()),
        (200, json!(true), json!(24.0)),
        "{v}"
    );
    let (s, _, _) = knock(port, "GET", "/health", None, &[]).await;
    assert_eq!(s, 200, "the health is an open door");
    let (s, _, _) = knock(port, "GET", "/", None, &[]).await;
    assert_eq!(s, 200, "the page is an open door");
    let (s, _, v) = knock(port, "GET", "/asks", None, &[]).await;
    assert_eq!((s, v), (401, not_seated.clone()), "a read needs a seat");
    let (s, _, v) = knock(port, "POST", "/ask", Some(&json!({"text": "hello?"})), &[]).await;
    assert_eq!((s, v), (401, not_seated.clone()), "an act needs a seat");
    let (s, _, v) = knock(
        port,
        "POST",
        "/seat",
        Some(&json!({"person": "jb", "code": "000000"})),
        &[],
    )
    .await;
    assert_eq!(
        (s, v),
        (403, one_face.clone()),
        "no authenticator yet: the one face"
    );
    let (s, _, v) = knock(
        port,
        "POST",
        "/seat",
        Some(&json!({"person": "Not A Name"})),
        &[],
    )
    .await;
    assert_eq!(s, 400, "the person grammar, in words: {v}");
    println!("gate · nobody holds the ground: the unseated wear one face");

    // ---- 2. THE CEREMONY: the first to prove an authenticator here is the owner
    let jb = "did:orreth:person:jb";
    let (s, _, b) = knock(port, "POST", "/enroll", Some(&json!({"person": "jb"})), &[]).await;
    assert_eq!(
        s, 201,
        "the door stands open while no one holds the ground: {b}"
    );
    let jb_secret = b["secret"].as_str().unwrap().to_string();
    let code = proof::totp(&jb_secret, proof_live::now_unix()).unwrap();
    let (s, _, b) = knock(
        port,
        "POST",
        "/enroll/confirm",
        Some(&json!({"person": jb, "code": code})),
        &[],
    )
    .await;
    assert_eq!((s, b), (200, json!({"person": jb, "enrolled": true})));
    let code = proof::totp(&jb_secret, proof_live::now_unix()).unwrap();
    let (s, _, seated) = knock(
        port,
        "POST",
        "/seat",
        Some(&json!({"person": "jb", "code": code})),
        &[],
    )
    .await;
    assert_eq!(s, 201, "{seated}");
    assert_eq!(
        (
            seated["owner"].clone(),
            seated["role"].clone(),
            seated["person"].clone()
        ),
        (json!(true), json!("owner"), json!(jb))
    );
    assert!(
        seated["words"]
            .as_str()
            .unwrap()
            .starts_with("you hold this ground now, jb"),
        "{seated}"
    );
    assert_eq!(seated["seat"]["subject"], json!(jb));
    assert_eq!(seated["seat"]["audience"], json!(world.scope));
    assert_eq!(seated["seat"]["constraints"]["direction"], json!("within"));
    let jb_wire = seated["wire"].as_str().unwrap().to_string();
    let jb_seat = [("authorization", bearer(&jb_wire))];
    let jb_h: Vec<(&str, &str)> = jb_seat.iter().map(|(k, v)| (*k, v.as_str())).collect();
    let (s, _, v) = knock(port, "GET", "/seat", None, &[]).await;
    assert_eq!((s, v["ceremony"].clone()), (200, json!(false)));
    let (s, _, v) = knock(port, "GET", "/proof", None, &jb_h).await;
    assert_eq!(s, 200, "{v}");
    assert_eq!(
        (
            v["person"].clone(),
            v["owner"].clone(),
            v["masters"].clone(),
            v["seat"]["role"].clone()
        ),
        (json!(jb), json!(jb), json!([jb]), json!("owner")),
        "{v}"
    );
    let (s, _, v) = knock(port, "GET", "/asks", None, &jb_h).await;
    assert_eq!(s, 200, "seated, the read answers: {v}");
    println!("gate · the ceremony: {}", seated["words"]);

    // ---- 3. a stranger cannot enroll now; the owner enrolls a second person, who sits but cannot govern
    let (s, _, v) = knock(
        port,
        "POST",
        "/enroll",
        Some(&json!({"person": "mallory"})),
        &[],
    )
    .await;
    assert_eq!(
        (s, v),
        (401, not_seated.clone()),
        "the ground is held: enrolling is the owner's word"
    );
    let quinn = "did:orreth:person:quinn";
    let (s, _, b) = knock(
        port,
        "POST",
        "/enroll",
        Some(&json!({"person": "quinn"})),
        &jb_h,
    )
    .await;
    assert_eq!(s, 201, "on the owner's word: {b}");
    let q_secret = b["secret"].as_str().unwrap().to_string();
    let code = proof::totp(&q_secret, proof_live::now_unix()).unwrap();
    let (s, _, _) = knock(
        port,
        "POST",
        "/enroll/confirm",
        Some(&json!({"person": quinn, "code": code})),
        &[],
    )
    .await;
    assert_eq!(s, 200);
    let code = proof::totp(&q_secret, proof_live::now_unix()).unwrap();
    let (s, _, qs) = knock(
        port,
        "POST",
        "/seat",
        Some(&json!({"person": quinn, "code": code})),
        &[],
    )
    .await;
    assert_eq!(
        (s, qs["role"].clone(), qs["owner"].clone()),
        (201, json!("person"), json!(false)),
        "{qs}"
    );
    assert!(
        qs["words"].as_str().unwrap().starts_with("seated, quinn"),
        "{qs}"
    );
    let q_wire = qs["wire"].as_str().unwrap().to_string();
    let q_seat = [("authorization", bearer(&q_wire))];
    let q_h: Vec<(&str, &str)> = q_seat.iter().map(|(k, v)| (*k, v.as_str())).collect();
    let (s, _, v) = knock(port, "GET", "/sessions", None, &q_h).await;
    assert_eq!(
        (s, v),
        (200, json!({"sessions": []})),
        "quinn reads as quinn: none of jb's"
    );
    let (s, _, v) = knock(
        port,
        "POST",
        "/sessions",
        Some(&json!({"person": jb, "title": "quinn's"})),
        &q_h,
    )
    .await;
    assert_eq!(s, 201, "{v}");
    let (s, _, v) = knock(port, "GET", "/sessions", None, &q_h).await;
    assert_eq!(
        v["sessions"].as_array().unwrap().len(),
        1,
        "the body's `person` was ignored — the seat's person owns the session: {v} ({s})"
    );
    let (s, _, v) = knock(port, "GET", "/sessions", None, &jb_h).await;
    assert_eq!(
        (s, v),
        (200, json!({"sessions": []})),
        "jb sees none of quinn's"
    );
    let (s, _, v) = knock(
        port,
        "POST",
        "/world/rehome",
        Some(&json!({"to_cell": "px"})),
        &q_h,
    )
    .await;
    assert_eq!(
        (s, v),
        (403, one_face.clone()),
        "a person's seat does not govern"
    );
    let (s, _, v) = knock(
        port,
        "POST",
        "/enroll",
        Some(&json!({"person": "eve"})),
        &q_h,
    )
    .await;
    assert_eq!((s, v), (403, one_face.clone()), "nor enrolls another");
    let (s, _, v) = knock(
        port,
        "POST",
        "/enroll",
        Some(&json!({"person": "quinn"})),
        &q_h,
    )
    .await;
    assert_eq!(
        (s, v),
        (403, one_face.clone()),
        "re-enrolling oneself is grave: the old code"
    );
    println!("gate · quinn sits as a person; the governing doors wear the one face");

    // ---- 3b. W69 (walk #19, 2026-09-27): the word at the interlock is the ASKER's own, or a
    // governing seat's. jb (the owner) holds a consequential act; quinn — seated, reads and
    // writes, does not govern — clicks Yes and meets the one face; the hold stands; jb's
    // own cancel is taken.
    let (s, _, v) = knock(
        port,
        "POST",
        "/world/rehome",
        Some(&json!({"to_cell": "px"})),
        &jb_h,
    )
    .await;
    assert_eq!(
        s, 202,
        "the owner's re-home holds at the interlock (L2): {v}"
    );
    let held = v["held"].as_str().expect("a held ask id").to_string();
    for approve in [true, false] {
        let (s, _, v) = knock(
            port,
            "POST",
            "/confirm",
            Some(&json!({"ask_id": held, "approve": approve})),
            &q_h,
        )
        .await;
        assert_eq!(
            (s, v),
            (403, one_face.clone()),
            "quinn's word on jb's hold (approve={approve}) is refused with the one face"
        );
    }
    let (_, _, v) = knock(port, "GET", &format!("/ask/{held}"), None, &jb_h).await;
    assert_eq!(
        v["status"],
        json!("awaiting-confirm"),
        "the hold stands after quinn's clicks: {v}"
    );
    let (s, _, _) = knock(
        port,
        "POST",
        "/confirm",
        Some(&json!({"ask_id": held, "approve": false})),
        &jb_h,
    )
    .await;
    assert_eq!(s, 202, "the asker's own cancel is taken");
    let (_, _, v) = knock(port, "GET", &format!("/ask/{held}"), None, &jb_h).await;
    assert_eq!(
        v["status"],
        json!("cancelled"),
        "cancelled on the asker's word: {v}"
    );
    println!("gate · W69: a seat that only reads and writes decides nobody's hold — the one face; the asker's cancel taken");

    // ---- 4. a seat from another kernel, a seat with its bytes touched, a seat past its time
    let stranger = KernelSelf::ephemeral();
    let forged = seat::mint(
        &stranger,
        jb,
        &world.scope,
        &seat::grants_for("owner", &world.scope),
        "2099-01-01T00:00:00.000Z",
        "within",
        None,
        None,
    )
    .unwrap();
    let f = [("authorization", bearer(&seat::wire(&forged)))];
    let f_h: Vec<(&str, &str)> = f.iter().map(|(k, v)| (*k, v.as_str())).collect();
    let (s, _, v) = knock(port, "GET", "/asks", None, &f_h).await;
    assert_eq!(
        (s, v),
        (401, not_seated.clone()),
        "another kernel's seat is no seat here"
    );
    let mut touched = seated["seat"].clone();
    touched["grants"] = seat::grants_for("owner", "u:elsewhere");
    let t = [("authorization", bearer(&seat::wire(&touched)))];
    let t_h: Vec<(&str, &str)> = t.iter().map(|(k, v)| (*k, v.as_str())).collect();
    let (s, _, v) = knock(port, "GET", "/asks", None, &t_h).await;
    assert_eq!(
        (s, v),
        (401, not_seated.clone()),
        "a seat whose bytes were touched is no seat"
    );
    let (s, _, v) = knock(
        port,
        "GET",
        "/asks",
        None,
        &[("authorization", "Bearer !!not-a-seat!!")],
    )
    .await;
    assert_eq!((s, v), (401, not_seated.clone()));
    println!("gate · a forged seat, a touched seat, no seat: one face");

    // ---- 5. the origin is closed
    let (s, _, v) = knock(
        port,
        "GET",
        "/asks",
        None,
        &[
            ("authorization", jb_h[0].1),
            ("origin", "http://evil.example"),
        ],
    )
    .await;
    assert_eq!(
        (s, v),
        (403, one_face.clone()),
        "a foreign origin is refused"
    );
    let (s, _, v) = knock(
        port,
        "POST",
        "/ask",
        Some(&json!({"text": "hi"})),
        &[
            ("authorization", jb_h[0].1),
            ("origin", "http://127.0.0.1:4600"),
        ],
    )
    .await;
    assert_eq!(
        (s, v),
        (403, one_face.clone()),
        "another door's origin is foreign too"
    );
    let (s, head, _) = knock(
        port,
        "GET",
        "/asks",
        None,
        &[
            ("authorization", jb_h[0].1),
            ("origin", host_origin.as_str()),
        ],
    )
    .await;
    assert_eq!(s, 200, "this door's own origin passes");
    assert!(
        !head
            .to_ascii_lowercase()
            .contains("access-control-allow-origin"),
        "no open origin on the answer: {head}"
    );
    println!("gate · the origin is closed");

    // ---- 6. the feed carries the seat as its query
    let (s, head, _) = knock(port, "GET", "/feed", None, &[]).await;
    assert_eq!(s, 401, "the feed needs a seat: {head}");
    {
        let mut f = TcpStream::connect(("127.0.0.1", port)).await.unwrap();
        f.write_all(format!("GET /feed?seat={jb_wire} HTTP/1.1\r\nHost: 127.0.0.1:{port}\r\naccept: text/event-stream\r\n\r\n").as_bytes()).await.unwrap();
        let mut buf = vec![0u8; 512];
        let n = tokio::time::timeout(Duration::from_secs(5), f.read(&mut buf))
            .await
            .unwrap()
            .unwrap();
        let head = String::from_utf8_lossy(&buf[..n]).to_string();
        assert!(
            head.starts_with("HTTP/1.1 200") && head.contains("text/event-stream"),
            "the seated feed streams: {head}"
        );
    }
    println!("gate · the feed reads the seat from its query");

    // ---- 7. a seat left is a seat no more
    let (s, _, v) = knock(port, "POST", "/seat/leave", None, &q_h).await;
    assert_eq!(s, 200, "{v}");
    assert_eq!(v["person"], json!(quinn));
    let (s, _, v) = knock(port, "GET", "/sessions", None, &q_h).await;
    assert_eq!((s, &v), (401, &not_seated), "the left seat is no seat");
    println!("gate · quinn left: {v}");

    // ---- 8. the knock ceiling at every door: a flood from one seat meets the busy words (burst 8 here)
    let mut handles = Vec::new();
    for _ in 0..24 {
        let h: Vec<(String, String)> = vec![("authorization".into(), bearer(&jb_wire))];
        handles.push(tokio::spawn(async move {
            let hh: Vec<(&str, &str)> = h.iter().map(|(k, v)| (k.as_str(), v.as_str())).collect();
            knock(port, "GET", "/asks", None, &hh).await
        }));
    }
    let mut served = 0;
    let mut busy = 0;
    for h in handles {
        let (s, _, v) = h.await.unwrap();
        match s {
            200 => served += 1,
            429 => {
                busy += 1;
                assert_eq!(v["error"], json!(seat::BUSY_WORDS), "{v}");
                assert_eq!(v["retry_after_s"], json!(1));
            }
            other => panic!("a flood knock answered {other}: {v}"),
        }
    }
    assert!(busy >= 8 && served >= 4, "twenty-four knocks at once from one seat: {served} served, {busy} busy (burst 8, rate 4/s)");
    println!(
        "gate · twenty-four knocks at once from one seat: {served} served, {busy} met the ceiling"
    );
    // an open door keeps its own bucket, per address — and it too has a ceiling
    let (s, _, _) = knock(port, "GET", "/health", None, &[]).await;
    assert_eq!(s, 200, "the open door's bucket is its own");
    let mut open_busy = 0;
    for _ in 0..24 {
        let (s, _, v) = knock(port, "GET", "/health", None, &[]).await;
        if s == 429 {
            open_busy += 1;
            assert_eq!(v["error"], json!(seat::BUSY_WORDS));
        }
    }
    assert!(open_busy > 0, "the open door's ceiling, per address");
    println!("gate · the open door met its own ceiling {open_busy} times in twenty-four");

    lit.stop().await;
    let _ = std::fs::remove_dir_all(&home);
}
