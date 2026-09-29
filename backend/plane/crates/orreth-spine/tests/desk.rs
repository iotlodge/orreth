// PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp8 row 3, THE GATE (b): the machine join desk's proof · 2026-09-26
//! THE DESK'S PROOF (canon 0005 sp8 row 3b · 0006 §2–3 · 0012 · covenant rule 3),
//! on the dev rig, by name:
//!
//!     cargo test -p orreth-spine --features bridge --test desk -- --nocapture
//!
//! One Rust kernel lit alone (no bodies); the owner and a second person seated by
//! the ceremony. A stranger's body asks to join and is CHALLENGED; a forged proof
//! is DENIED with the one face; the right key is PROVEN and STAGED — the kernel
//! holds `join.admit` in the chat like a keeper's proposal; a person's seat cannot
//! click it (the one face), a lease cannot be collected before the word; the
//! OWNER's click admits it; the lease is collected only by the same key, wears the
//! fuel clause, and stands as a seat with the role `body`: the body's words at
//! `/delta` need it (unleased → 401; a person's seat → 403), and the lease opens
//! nothing else. The same self asks again and is admitted on its STANDING
//! WELCOME with no click. A stale challenge is re-issued. A hold nobody answers
//! is denied when the holds expire. Malformed asks wear the one face.
//! With no rig it prints "rails not up — skipped by name" and passes green.

#![cfg(feature = "bridge")]

use orreth_spine::bridge::{glass_path, light, Config};
use orreth_spine::ground::Ground;
use orreth_spine::kernel_self::KernelSelf;
use orreth_spine::world::{token_hex, World};
use orreth_spine::{desk, proof, proof_live, rails};
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

/// One knock, with whatever headers the case needs (a seat, a lease, none).
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

/// The ceremony through the doors: enroll (open while no one holds the ground, else on
/// the owner's seat), confirm with the first code, sit with the next. Returns the wire.
async fn sit(port: u16, person: &str, owner: Option<&str>) -> String {
    let h: Vec<(&str, &str)> = owner
        .map(|w| vec![("authorization", w)])
        .unwrap_or_default();
    let (s, b) = knock(
        port,
        "POST",
        "/enroll",
        Some(&json!({"person": person})),
        &h,
    )
    .await;
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

fn agent(name: &str) -> KernelSelf {
    let mut seed = [0u8; 32];
    for (i, b) in token_hex(32).as_bytes().iter().take(32).enumerate() {
        seed[i] = *b;
    }
    let mut me = KernelSelf::from_seed(&seed, "agent");
    me.name = name.to_string();
    me
}

fn ask_of(me: &KernelSelf, name: &str) -> Value {
    json!({"did": me.did(), "name": name, "role": "resident", "public_key": me.verify_key_hex(),
           "template_hash": "sha256:0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
           "policy_hash": "sha256:deadbeef"})
}

#[tokio::test]
async fn the_desk_challenges_proves_stages_and_leases_a_body() {
    if !rig_up("the_desk_challenges_proves_stages_and_leases_a_body") {
        return;
    }
    if port_open(4600) || port_open(4601) {
        println!("a kernel holds :4600 or the reference :4601 — the desk proof refuses to run beside a live rig (stop it: scripts/dev.sh kernel stop · scripts/dev.sh reference stop)");
        return;
    }
    let tok = token_hex(3);
    let world = World {
        scope: format!("u:desk-{tok}"),
        ns: format!("t{tok}"),
        pg_dsn: rails::pg_dsn(),
        rabbit_url: rails::rabbit_url(),
        kafka: rails::kafka_bootstrap(),
    };
    let home = std::env::temp_dir().join(format!("orreth-desk-{tok}"));
    std::env::set_var("SPINE_JOIN_LEASE_DAYS", "7");
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
    let refused = json!({"error": "join refused"});

    // ---- 0. the ceremony: jb owns the ground; quinn holds a person's seat
    let jb_wire = sit(port, "jb", None).await;
    let quinn_wire = sit(port, "quinn", Some(&jb_wire)).await;
    let jb = [("authorization", jb_wire.as_str())];
    let quinn = [("authorization", quinn_wire.as_str())];
    println!("desk · the ceremony: jb owns the ground, quinn is a person");

    // ---- 1. a stranger's body asks and is CHALLENGED; the status door says so
    let scout = agent("scout");
    let (s, a) = knock(port, "POST", "/join", Some(&ask_of(&scout, "scout")), &[]).await;
    assert_eq!(s, 201, "{a}");
    assert_eq!(a["status"], json!("challenged"));
    let nonce = a["nonce"].as_str().unwrap().to_string();
    assert_eq!(nonce.len(), 32, "a 16-byte nonce, hex");
    let jid = a["id"].as_str().unwrap().to_string();
    assert!(jid.starts_with("join_"), "{a}");
    assert_eq!(
        a["words"],
        json!("sign this nonce with the key behind your DID — the door answers proof, not claims")
    );
    let (s, v) = knock(port, "GET", &format!("/join/{jid}"), None, &[]).await;
    assert_eq!(
        (s, v["status"].clone(), v["nonce"].clone()),
        (200, json!("challenged"), json!(nonce)),
        "{v}"
    );
    assert!(
        v.get("lease").is_none(),
        "the lease never rides the status door"
    );
    println!("desk · scout asked and was challenged");

    // ---- 2. a forged proof — another key signing scout's nonce — is DENIED with the one face
    let imposter = agent("imposter");
    let forged = desk::proof_of(&imposter, &nonce);
    let (s, v) = knock(
        port,
        "POST",
        "/join/prove",
        Some(&json!({"id": jid, "did": scout.did(), "sig": forged})),
        &[],
    )
    .await;
    assert_eq!(
        (s, v["status"].clone(), v["words"].clone()),
        (200, json!("denied"), json!("join refused")),
        "{v}"
    );
    let (_, v) = knock(port, "GET", &format!("/join/{jid}"), None, &[]).await;
    assert_eq!(v["status"], json!("denied"));
    let (s, v) = knock(
        port,
        "POST",
        "/join/prove",
        Some(&json!({"id": jid, "did": scout.did(), "sig": desk::proof_of(&scout, &nonce)})),
        &[],
    )
    .await;
    assert_eq!(
        (s, v["status"].clone()),
        (200, json!("denied")),
        "a settled word is never rewritten: {v}"
    );
    println!("desk · a forged proof was turned away; the denial stands");

    // ---- 3. scout asks again and PROVES — staged: the kernel holds join.admit in the chat
    let (s, a) = knock(port, "POST", "/join", Some(&ask_of(&scout, "scout")), &[]).await;
    assert_eq!(s, 201, "{a}");
    let jid = a["id"].as_str().unwrap().to_string();
    let nonce = a["nonce"].as_str().unwrap().to_string();
    let (s, v) = knock(
        port,
        "POST",
        "/join/prove",
        Some(&json!({"id": jid, "did": scout.did(), "sig": desk::proof_of(&scout, &nonce)})),
        &[],
    )
    .await;
    assert_eq!((s, v["status"].clone()), (200, json!("staged")), "{v}");
    assert_eq!(
        v["words"],
        json!("scout proved its key — the door waits for a governing seat's yes")
    );
    let ask_id = v["ask"].as_str().unwrap().to_string();
    let (s, h) = knock(port, "GET", &format!("/ask/{ask_id}"), None, &jb).await;
    assert_eq!(s, 200, "{h}");
    assert_eq!(h["served_by"], json!("the kernel"));
    assert_eq!(h["status"], json!("awaiting-confirm"));
    assert_eq!(h["hold"]["tool"], json!("join.admit"));
    assert_eq!(h["hold"]["level"], json!("L2"));
    assert_eq!(
        h["person"],
        json!(scout.did()),
        "the body asked; the human cuts"
    );
    assert!(h["text"].as_str().unwrap().starts_with("scout (a resident) asks to join this world — its key is proven, its template 01234567. A yes gives it a LEASE for 7 days"), "{h}");
    println!("desk · scout proved its key; the kernel holds join.admit for a governing seat");

    // ---- 4. a person's seat cannot admit (the one face); the lease cannot be collected before the word
    let (s, v) = knock(
        port,
        "POST",
        "/confirm",
        Some(&json!({"ask_id": ask_id, "approve": true})),
        &quinn,
    )
    .await;
    assert_eq!((s, v), (403, one_face.clone()), "quinn's click");
    let (_, v) = knock(port, "GET", &format!("/join/{jid}"), None, &[]).await;
    assert_eq!(
        v["status"],
        json!("staged"),
        "still staged after a person's click: {v}"
    );
    let (s, v) = knock(
        port,
        "POST",
        "/join/lease",
        Some(
            &json!({"id": jid, "did": scout.did(), "sig": desk::collect_sig(&scout, &jid, &nonce)}),
        ),
        &[],
    )
    .await;
    assert_eq!((s, v), (403, one_face.clone()), "no lease before the word");
    println!("desk · a person's seat cannot admit; nothing collects before the word");

    // ---- 5. the OWNER's click admits scout; the lease is collected by the same key only
    let (s, v) = knock(
        port,
        "POST",
        "/confirm",
        Some(&json!({"ask_id": ask_id, "approve": true})),
        &jb,
    )
    .await;
    assert_eq!(s, 202, "{v}");
    let (_, v) = knock(port, "GET", &format!("/join/{jid}"), None, &[]).await;
    assert_eq!(v["status"], json!("done"), "{v}");
    assert_eq!(v["admitted_by"], json!("admitted on jb's word"));
    let (s, h) = knock(port, "GET", &format!("/ask/{ask_id}"), None, &jb).await;
    assert_eq!((s, h["status"].clone()), (200, json!("replied")), "{h}");
    assert!(
        h["reply"]
            .as_str()
            .unwrap()
            .contains("lease granted — welcome to"),
        "{h}"
    );
    let (s, v) = knock(
        port,
        "POST",
        "/join/lease",
        Some(&json!({"id": jid, "did": scout.did(), "sig": desk::collect_sig(&imposter, &jid, &nonce)})),
        &[],
    )
    .await;
    assert_eq!(
        (s, v),
        (403, one_face.clone()),
        "another key collects nothing"
    );
    let (s, v) = knock(
        port,
        "POST",
        "/join/lease",
        Some(
            &json!({"id": jid, "did": scout.did(), "sig": desk::collect_sig(&scout, &jid, &nonce)}),
        ),
        &[],
    )
    .await;
    assert_eq!(s, 200, "{v}");
    let lease = v["lease"].clone();
    assert_eq!(lease["subject"], json!(scout.did()));
    assert_eq!(lease["audience"], json!(world.scope));
    assert_eq!(lease["grants"], desk::lease_grants());
    assert_eq!(
        lease["constraints"]["budget"],
        json!({"cost": 1.0, "renew_days": 1}),
        "the fuel clause"
    );
    assert_eq!(lease["constraints"]["direction"], json!("within"));
    let lease_id = v["lease_id"].as_str().unwrap().to_string();
    assert!(lease_id.starts_with("seat_"));
    let wire = v["wire"].as_str().unwrap().to_string();
    assert!(
        v["words"].as_str().unwrap().starts_with(&format!(
            "lease granted — welcome to {}, scout",
            world.scope
        )),
        "{v}"
    );
    let (s, again) = knock(
        port,
        "POST",
        "/join/lease",
        Some(
            &json!({"id": jid, "did": scout.did(), "sig": desk::collect_sig(&scout, &jid, &nonce)}),
        ),
        &[],
    )
    .await;
    assert_eq!(
        (s, again["lease_id"].clone()),
        (200, json!(lease_id)),
        "the same knock, the same lease"
    );
    println!(
        "desk · jb admitted scout; the lease was collected by scout's key, with the fuel clause"
    );

    // ---- 6. the lease at the doors: /delta needs it; a person's seat is not a body; the lease opens nothing else
    let delta = json!({"ref": "ask_test", "text": "hello from scout"});
    let (s, v) = knock(port, "POST", "/delta", Some(&delta), &[]).await;
    assert_eq!((s, v), (401, not_seated.clone()), "unleased words");
    let (s, v) = knock(port, "POST", "/delta", Some(&delta), &jb).await;
    assert_eq!(
        (s, v),
        (403, one_face.clone()),
        "a person never speaks as a body"
    );
    let bearer = format!("Bearer {wire}");
    let leased = [("authorization", bearer.as_str())];
    let (s, _) = knock(port, "POST", "/delta", Some(&delta), &leased).await;
    assert_eq!(s, 204, "the body's own words, leased");
    let (s, v) = knock(port, "GET", "/asks", None, &leased).await;
    assert_eq!(
        (s, v),
        (403, one_face.clone()),
        "a lease opens no person's door"
    );
    let (s, v) = knock(port, "POST", "/ask", Some(&json!({"text": "hi"})), &leased).await;
    assert_eq!((s, v), (403, one_face.clone()), "nor an act");
    println!("desk · the lease opens scout's own words and nothing else");

    // ---- 7. the same self asks again: proven, then admitted on its STANDING WELCOME — no click
    let (s, a) = knock(port, "POST", "/join", Some(&ask_of(&scout, "scout")), &[]).await;
    assert_eq!(s, 201, "{a}");
    let jid2 = a["id"].as_str().unwrap().to_string();
    let nonce2 = a["nonce"].as_str().unwrap().to_string();
    let (s, v) = knock(
        port,
        "POST",
        "/join/prove",
        Some(&json!({"id": jid2, "did": scout.did(), "sig": desk::proof_of(&scout, &nonce2)})),
        &[],
    )
    .await;
    assert_eq!((s, v["status"].clone()), (200, json!("done")), "{v}");
    assert_eq!(
        v["admitted_by"],
        json!(format!(
            "admitted on its standing welcome ({jid}) — the same self, the same world"
        ))
    );
    let (s, v) = knock(
        port,
        "POST",
        "/join/lease",
        Some(&json!({"id": jid2, "did": scout.did(), "sig": desk::collect_sig(&scout, &jid2, &nonce2)})),
        &[],
    )
    .await;
    assert_eq!(s, 200, "{v}");
    assert_ne!(v["lease_id"], json!(lease_id), "a new life, a new lease");
    println!("desk · scout re-joined on its standing welcome, no click owed");

    // ---- 8. a stale challenge is re-issued; the desk's list is a seated read
    let rover = agent("rover");
    let (s, a) = knock(port, "POST", "/join", Some(&ask_of(&rover, "rover")), &[]).await;
    assert_eq!(s, 201, "{a}");
    let jid3 = a["id"].as_str().unwrap().to_string();
    let nonce3 = a["nonce"].as_str().unwrap().to_string();
    let mut g = Ground::connect(&world.pg_dsn).await.expect("the ground");
    g.client()
        .execute(
            "UPDATE spine_desk SET nonce_at = now() - interval '3 minutes' WHERE join_id = $1",
            &[&jid3],
        )
        .await
        .unwrap();
    let (s, v) = knock(
        port,
        "POST",
        "/join/prove",
        Some(&json!({"id": jid3, "did": rover.did(), "sig": desk::proof_of(&rover, &nonce3)})),
        &[],
    )
    .await;
    assert_eq!((s, v["status"].clone()), (200, json!("challenged")), "{v}");
    let nonce4 = v["nonce"].as_str().unwrap().to_string();
    assert_ne!(nonce4, nonce3, "a fresh nonce");
    let (s, v) = knock(
        port,
        "POST",
        "/join/prove",
        Some(&json!({"id": jid3, "did": rover.did(), "sig": desk::proof_of(&rover, &nonce4)})),
        &[],
    )
    .await;
    assert_eq!((s, v["status"].clone()), (200, json!("staged")), "{v}");
    let (s, v) = knock(port, "GET", "/join", None, &[]).await;
    assert_eq!(
        (s, v),
        (401, not_seated.clone()),
        "the desk is a seated read"
    );
    let (s, v) = knock(port, "GET", "/join", None, &jb).await;
    assert_eq!(s, 200, "{v}");
    let joins = v["joins"].as_array().unwrap();
    assert_eq!(joins.len(), 4, "{v}");
    assert_eq!(v["lease_days"], json!(7));
    assert_eq!(joins[0]["name"], json!("rover"));
    assert_eq!(joins[0]["status"], json!("staged"));
    assert!(
        joins.iter().all(|j| j.get("lease").is_none()),
        "the lease never rides the desk's list"
    );
    println!("desk · a stale challenge was re-issued; the desk lists every join, newest first");

    // ---- 9. a hold nobody answers is DENIED when the holds expire (0012: expire = deny + signal)
    let settled = proof_live::expire_holds(&mut g, &world, 0).await.unwrap();
    assert!(!settled.is_empty(), "rover's hold expired");
    let (_, v) = knock(port, "GET", &format!("/join/{jid3}"), None, &[]).await;
    assert_eq!(v["status"], json!("denied"), "{v}");
    assert!(
        v["admitted_by"]
            .as_str()
            .unwrap()
            .starts_with("no word came"),
        "{v}"
    );
    println!("desk · a hold nobody answered turned rover away, recorded");

    // ---- 10. malformed asks wear the one face; a stranger's status is no one's
    let (s, v) = knock(port, "POST", "/join", Some(&json!({"did": "did:orreth:person:jb", "name": "jb", "public_key": scout.verify_key_hex()})), &[]).await;
    assert_eq!((s, v), (400, refused.clone()), "a person has no key");
    let (s, v) = knock(
        port,
        "POST",
        "/join",
        Some(
            &json!({"did": scout.did(), "name": "scout", "public_key": imposter.verify_key_hex()}),
        ),
        &[],
    )
    .await;
    assert_eq!(
        (s, v),
        (400, refused.clone()),
        "a key that does not derive the DID"
    );
    let (s, v) = knock(port, "POST", "/join", Some(&json!({"did": scout.did(), "name": "Not A Name", "public_key": scout.verify_key_hex()})), &[]).await;
    assert_eq!((s, v), (400, refused.clone()), "the name grammar");
    let (s, v) = knock(port, "GET", "/join/join_000000000000", None, &[]).await;
    assert_eq!((s, v), (404, refused.clone()));
    let (s, v) = knock(
        port,
        "POST",
        "/join/prove",
        Some(&json!({"id": "join_000000000000", "did": scout.did(), "sig": {}})),
        &[],
    )
    .await;
    assert_eq!((s, v), (404, refused.clone()));
    println!("desk · malformed asks wear the one face");

    lit.stop().await;
    let _ = orreth_spine::events::prune_namespace(&world.kafka, &format!("t{tok}")).await; // the proof's residue leaves with it
    let _ = std::fs::remove_dir_all(&home);
    println!("desk · PASS — challenged · denied · proved · staged · a person refused · the owner's yes · the lease by the key · the lease at the doors · the standing welcome · a stale challenge · the expired hold · the one face");
}
