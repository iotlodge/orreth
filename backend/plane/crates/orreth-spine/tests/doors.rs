// PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch row 4, re-base sp1: the four Python-only doors cross — walked over HTTP on the Rust kernel alone · 2026-09-28
//! THE FOUR DOORS (re-base sp1): `GET/POST /mitl` · `POST /impact` · `POST /mark` ·
//! `POST /markers/kinds` — until now the reference's alone — knocked on the Rust
//! kernel lit alone, through the gate (a seated person), each answer's shape the
//! reference's: a kind declared and a bad name refused in words; a mark set with its
//! fact and the interested asked; MITL's card with its citations; the toggle
//! recorded; the impact of a watch read from the ground and judged by the ladder,
//! its ask filed to mitl as a thought; a change of no known kind refused in words.
//! Also the two doors THE PARKED opened: `GET /parked` (a read) and
//! `POST /parked/advance` (a governing seat's word).
#![cfg(feature = "bridge")]

use orreth_spine::bridge::{light, Config};
use orreth_spine::world::{token_hex, World};
use orreth_spine::{proof, proof_live, rails};
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

fn glass_path() -> std::path::PathBuf {
    spine_dir().join("glass/index.html")
}

async fn knock(
    port: u16,
    method: &str,
    path: &str,
    body: Option<&Value>,
    headers: &[(&str, &str)],
) -> (u16, Value) {
    for _ in 0..8 {
        let mut s = TcpStream::connect(("127.0.0.1", port))
            .await
            .expect("the door answers");
        let body_s = body.map(|b| b.to_string()).unwrap_or_default();
        let extra: String = headers
            .iter()
            .map(|(k, v)| format!("{k}: {v}\r\n"))
            .collect();
        let req = format!(
            "{method} {path} HTTP/1.1\r\nHost: 127.0.0.1:{port}\r\nConnection: close\r\n{extra}content-type: \
             application/json\r\ncontent-length: {}\r\n\r\n{body_s}",
            body_s.len()
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
        let v: Value = text
            .split_once("\r\n\r\n")
            .and_then(|(_, b)| serde_json::from_str(b).ok())
            .unwrap_or(Value::Null);
        if status == 429 {
            let after = v["retry_after_s"].as_f64().unwrap_or(1.0).max(0.25);
            tokio::time::sleep(Duration::from_secs_f64(after)).await;
            continue;
        }
        return (status, v);
    }
    panic!("the door stayed busy");
}

/// The ground's own count of table reads (sequential + index scans), per spine table.
async fn table_reads(g: &orreth_spine::ground::Ground) -> std::collections::BTreeMap<String, i64> {
    g.client()
        .query(
            "SELECT relname, (seq_scan + idx_scan)::bigint FROM pg_stat_user_tables WHERE schemaname = \
             current_schema() AND relname LIKE 'spine\\_%'",
            &[],
        )
        .await
        .unwrap()
        .iter()
        .map(|r| (r.get::<_, String>(0), r.get::<_, i64>(1)))
        .collect()
}

/// The reads between two counts, per table, the busiest first — and their sum.
fn reads_between(
    before: &std::collections::BTreeMap<String, i64>,
    after: &std::collections::BTreeMap<String, i64>,
) -> (i64, Vec<(String, i64)>) {
    let mut per: Vec<(String, i64)> = after
        .iter()
        .map(|(t, n)| (t.clone(), n - before.get(t).copied().unwrap_or(0)))
        .filter(|(_, d)| *d > 0)
        .collect();
    per.sort_by_key(|a| std::cmp::Reverse(a.1));
    (per.iter().map(|(_, d)| d).sum(), per)
}

#[tokio::test]
async fn the_four_doors_answer_on_the_rust_kernel_alone() {
    if !rig_up("the_four_doors_answer_on_the_rust_kernel_alone") {
        return;
    }
    if port_open(4600) || port_open(4601) {
        println!("a kernel holds :4600 or the reference :4601 — the doors proof refuses to run beside a live rig (stop it: scripts/dev.sh kernel stop · scripts/dev.sh reference stop)");
        return;
    }
    let tok = token_hex(3);
    let world = World {
        scope: format!("u:doors-{tok}"),
        ns: format!("t{tok}"),
        pg_dsn: rails::pg_dsn(),
        rabbit_url: rails::rabbit_url(),
        kafka: rails::kafka_bootstrap(),
    };
    let home = std::env::temp_dir().join(format!("orreth-doors-{tok}"));
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

    // ---- the seat: the ceremony's first prover is the owner (the gate's law)
    let jb = "did:orreth:person:jb";
    let (s, b) = knock(port, "POST", "/enroll", Some(&json!({"person": "jb"})), &[]).await;
    assert_eq!(s, 201, "{b}");
    let secret = b["secret"].as_str().unwrap().to_string();
    let code = proof::totp(&secret, proof_live::now_unix()).unwrap();
    let (s, _) = knock(
        port,
        "POST",
        "/enroll/confirm",
        Some(&json!({"person": jb, "code": code})),
        &[],
    )
    .await;
    assert_eq!(s, 200);
    let code = proof::totp(&secret, proof_live::now_unix()).unwrap();
    let (s, seated) = knock(
        port,
        "POST",
        "/seat",
        Some(&json!({"person": "jb", "code": code})),
        &[],
    )
    .await;
    assert_eq!(s, 201, "{seated}");
    let wire = format!("Bearer {}", seated["wire"].as_str().unwrap());
    let h: Vec<(&str, &str)> = vec![("authorization", wire.as_str())];

    // ---- 1. the four doors need a seat (the gate, unchanged)
    for (m, p) in [
        ("GET", "/mitl"),
        ("POST", "/mitl"),
        ("POST", "/impact"),
        ("POST", "/mark"),
        ("POST", "/markers/kinds"),
    ] {
        let (s, v) = knock(port, m, p, Some(&json!({})), &[]).await;
        assert_eq!((s, v), (401, json!({"error": "not seated"})), "{m} {p}");
    }

    // ---- 2. POST /markers/kinds: declared, never invented — a fresh kind (the kernel's seven are seeded and kept); the answer carries the group as said
    let (s, v) = knock(port, "POST", "/markers/kinds",
        Some(&json!({"kind": " Betterment ", "group": "Quality", "description": "a way to do better"})), &h).await;
    assert_eq!(
        (s, v),
        (201, json!({"kind": "betterment", "group": "Quality"}))
    );
    let (s, v) = knock(port, "GET", "/markers/kinds", None, &h).await;
    assert_eq!(s, 200);
    let mine = v["kinds"]
        .as_array()
        .unwrap()
        .iter()
        .find(|k| k["kind"] == json!("betterment"))
        .cloned()
        .expect("the kind on the registry");
    assert_eq!(
        (mine["group"].clone(), mine["declared_by"].clone()),
        (json!("quality"), json!(jb))
    );
    let (s, v) = knock(
        port,
        "POST",
        "/markers/kinds",
        Some(&json!({"kind": "not a kind", "group": "x"})),
        &h,
    )
    .await;
    assert_eq!(
        (s, v),
        (
            400,
            json!({"error": "a kind is a short lowercase name: letters, digits, dashes"})
        )
    );

    // ---- 3. POST /mark: a human marks an ask — its fact, the marked ask's marker as parent; the words when nothing is named
    let (s, v) = knock(
        port,
        "POST",
        "/mark",
        Some(&json!({"kind": "betterment", "note": "shorter"})),
        &h,
    )
    .await;
    assert_eq!(
        (s, v),
        (400, json!({"error": "mark what? name an ask or a session"}))
    );
    let (s, v) = knock(port, "POST", "/sessions", Some(&json!({})), &h).await;
    assert_eq!(s, 201, "{v}");
    let ses = v["session_id"].as_str().unwrap().to_string();
    let (s, v) = knock(
        port,
        "POST",
        "/ask",
        Some(&json!({"text": "librarian, what is the covenant?", "session": ses})),
        &h,
    )
    .await;
    assert_eq!(s, 201, "{v}");
    let ask_id = v["id"]
        .as_str()
        .or(v["ids"][0].as_str())
        .unwrap()
        .to_string();
    let (s, v) = knock(
        port,
        "POST",
        "/mark",
        Some(&json!({"kind": "betterment", "session": ses, "note": "say it shorter"})),
        &h,
    )
    .await;
    assert_eq!(s, 201, "{v}");
    assert_eq!(
        (
            v["marker"]["kind"].clone(),
            v["marker"]["ref"].clone(),
            v["marker"]["by"].clone(),
            v["marker"]["note"].clone()
        ),
        (
            json!("betterment"),
            json!(ask_id),
            json!(jb),
            json!("say it shorter")
        )
    );
    assert!(v["marker"]["id"].as_str().unwrap().starts_with("mk_"));
    assert!(v["asked"].is_array());
    let (s, v) = knock(
        port,
        "POST",
        "/mark",
        Some(&json!({"kind": "wish", "ref": ask_id})),
        &h,
    )
    .await;
    assert_eq!(s, 400);
    assert!(
        v["error"]
            .as_str()
            .unwrap()
            .starts_with("no marker kind named 'wish' is declared here"),
        "{v}"
    );
    let (s, v) = knock(port, "GET", "/markers?kind=betterment", None, &h).await;
    assert_eq!(s, 200);
    assert!(
        v["markers"]
            .as_array()
            .unwrap()
            .iter()
            .any(|m| m["ref"] == json!(ask_id)),
        "{v}"
    );

    // ---- 4. GET /mitl: the card — not summoned, nothing worn yet, the citations from the canon on disk
    let (s, v) = knock(port, "GET", "/mitl", None, &h).await;
    assert_eq!(s, 200, "{v}");
    assert_eq!(
        (
            v["name"].clone(),
            v["expansion"].clone(),
            v["summoned"].clone()
        ),
        (
            json!("mitl"),
            json!("the Master Mind In the Loop"),
            json!(false)
        )
    );
    assert_eq!(v["ontology"], json!({"passages": 0, "files": []}));
    let cites = v["citations"].as_object().unwrap();
    assert!(
        cites.len() > 100,
        "the citations come from the canon on disk: {}",
        cites.len()
    );
    assert_eq!(
        cites
            .get(".claude/skills/orreth-covenant/SKILL.md#1")
            .map(|c| c.as_str().unwrap().starts_with("the covenant")),
        Some(true)
    );
    assert_eq!(
        cites.get("SKILL.md#1"),
        cites.get(".claude/skills/orreth-covenant/SKILL.md#1")
    );

    // ---- 5. POST /mitl: the toggle — summoned for the session, recorded; dismissed for the person outside one
    let (s, v) = knock(port, "POST", "/mitl", Some(&json!({"session": ses})), &h).await;
    assert_eq!(s, 201, "{v}");
    assert_eq!(
        (
            v["summoned"].clone(),
            v["state"].clone(),
            v["person"].clone(),
            v["session"].clone()
        ),
        (json!(true), json!("summoned"), json!(jb), json!(ses))
    );
    assert!(v["marker"].as_str().unwrap().starts_with("mk_"));
    let (s, v) = knock(port, "GET", &format!("/mitl?session={ses}"), None, &h).await;
    assert_eq!((s, v["summoned"].clone()), (200, json!(true)));
    let (s, v) = knock(port, "GET", "/mitl", None, &h).await;
    assert_eq!(
        (s, v["summoned"].clone()),
        (200, json!(false)),
        "outside the session: the person's own word, not yet said"
    );
    let (s, v) = knock(port, "POST", "/mitl", Some(&json!({"summon": false})), &h).await;
    assert_eq!(
        (s, v["state"].clone(), v["session"].clone()),
        (201, json!("dismissed"), Value::Null)
    );

    // ---- 6. POST /impact: a change of no known kind, and a shapeless one, refused in words
    let (s, v) = knock(
        port,
        "POST",
        "/impact",
        Some(&json!({"change": "watch"})),
        &h,
    )
    .await;
    assert_eq!(
        (s, v),
        (
            400,
            json!({"error": "a change is {kind, ref or draft, words}"})
        )
    );
    let (s, v) = knock(
        port,
        "POST",
        "/impact",
        Some(&json!({"change": {"kind": "wish"}})),
        &h,
    )
    .await;
    assert_eq!(
        (s, v),
        (
            400,
            json!({"error": "a change is one of watch, intention, template, binding, placement, act, service"})
        )
    );
    // a watch about to be declared: the ground read (no monitor here — said plainly), the class
    // by the add-watch tool's declaration, the verdict by the ladder, the ask filed to mitl as a thought
    let (s, v) = knock(port, "POST", "/impact", Some(&json!({"change": {"kind": "watch", "words": "no body is dormant",
        "draft": {"name": "no body is dormant", "metric": "bodies_dormant", "op": "<=", "threshold": 0}}, "session": ses})), &h).await;
    assert_eq!(s, 201, "{v}");
    assert_eq!(
        (
            v["contract"].clone(),
            v["served_by"].clone(),
            v["expansion"].clone()
        ),
        (
            json!("orreth.impact/1"),
            json!("mitl"),
            json!("the Master Mind In the Loop")
        )
    );
    let t = &v["touches"];
    assert_eq!(
        (
            t["metric"].clone(),
            t["class"].clone(),
            t["level"].clone(),
            t["kernel"].clone()
        ),
        (
            json!("bodies_dormant"),
            json!("consequential"),
            json!("L2"),
            json!(false)
        )
    );
    assert_eq!(v["verdict"], json!("consider"));
    // the monitor first; the kernel's own Resiliency intention wakes on watch-red and names its
    // planner and runner too (as the reference's `test_mitl` sees)
    assert_eq!(t["bodies"][0], json!("monitor"), "{t}");
    assert!(
        t["intentions"]
            .as_array()
            .unwrap()
            .iter()
            .any(|i| i["kind"] == json!("kernel")),
        "{t}"
    );
    assert!(t["chains"]
        .as_array()
        .unwrap()
        .contains(&json!("H → monitor → tool:add-watch")));
    assert!(
        t["notes"].as_array().unwrap().contains(&json!(
            "no monitor body has joined this world yet — the watch would land by hand"
        )),
        "{t}"
    );
    let ground = v["ground"].as_array().unwrap();
    assert!(
        ground[0]
            .as_str()
            .unwrap()
            .starts_with("bodies: monitor (not joined)"),
        "{ground:?}"
    );
    assert!(
        ground.contains(&json!("metric: bodies_dormant"))
            && ground.contains(&json!("consequence: consequential → L2")),
        "{ground:?}"
    );
    let aid = v["ask_id"].as_str().expect("the ask filed").to_string();
    let (s, a) = knock(port, "GET", &format!("/ask/{aid}"), None, &h).await;
    assert_eq!(s, 200, "{a}");
    // filed to mitl in the session; no crew is seated on this kernel, so the door answers "not
    // here" at once (W19) — the reference with a mitl body joined sees `received`
    assert_eq!(
        (a["target"].clone(), a["session"].clone()),
        (json!("mitl"), json!(ses))
    );
    assert!(
        ["received", "refused"].contains(&a["status"].as_str().unwrap_or_default()),
        "{a}"
    );
    let text = a["text"].as_str().unwrap();
    assert!(text.starts_with("the change: no body is dormant — expected impact?\nTHE CHANGE: a watch\nTHE GROUND (read by the kernel — this is the record):\n- bodies: monitor (not joined)"), "{text}");
    assert!(text.contains("VERDICT BY THE LADDER: consider\n"), "{text}");
    // an act by a tool the shelf declares grave: the verdict is grave before any brain speaks
    let (s, v) = knock(
        port,
        "POST",
        "/impact",
        Some(&json!({"change": {"kind": "act", "draft": {"tool": "erase-record"}}})),
        &h,
    )
    .await;
    assert_eq!(s, 201, "{v}");
    assert_eq!(
        (v["verdict"].clone(), v["touches"]["level"].clone()),
        (json!("grave — needs L3"), json!("L3-code"))
    );
    let (s, v) = knock(
        port,
        "POST",
        "/impact",
        Some(&json!({"change": {"kind": "act", "draft": {"tool": "weather"}}})),
        &h,
    )
    .await;
    assert_eq!(
        (s, v["verdict"].clone(), v["touches"]["level"].clone()),
        (201, json!("low"), json!("L1"))
    );
    let (s, v) = knock(
        port,
        "POST",
        "/impact",
        Some(&json!({"change": {"kind": "service", "ref": "nobody"}})),
        &h,
    )
    .await;
    assert_eq!(s, 201);
    assert_eq!(
        v["touches"]["notes"][0],
        json!("no service named 'nobody' is on the shelf — \"what services are here?\" lists them")
    );

    // ---- 7. THE PARKED's doors: the read, and the person's word on a poison that was never parked
    let (s, v) = knock(port, "GET", "/parked", None, &h).await;
    assert_eq!(
        (s, v["parked"].clone(), v["held"].clone()),
        (200, json!([]), json!(0))
    );
    let (s, v) = knock(port, "POST", "/parked/advance", Some(&json!({})), &h).await;
    assert_eq!(s, 400, "{v}");
    let (s, v) = knock(
        port,
        "POST",
        "/parked/advance",
        Some(&json!({"parked_id": 424242})),
        &h,
    )
    .await;
    assert_eq!((s, v), (404, json!({"error": "no such parked event"})));

    // ---- 8. THE PERF CURE (2026-09-29): the crew door reads a FIXED handful of tables however
    // large the crew — thirty bodies joined by hand on the ground, one knock, and the ground's
    // own count of table reads (sequential + index scans over spine_% tables) stays under a
    // dozen; the old door read six tables per body (a hundred and eighty here)
    {
        use orreth_spine::ground::Ground;
        let g = Ground::connect(&rails::pg_dsn()).await.unwrap();
        for i in 0..30 {
            let (name, did) = (
                format!("body{i:02}"),
                format!("did:orreth:agent:perf{i:02}{tok}"),
            );
            g.client()
                .execute(
                    "INSERT INTO spine_joins (did, name, life, template_hash, policy_version, policy_hash, sig, \
                     scope, kind, nature) VALUES ($1, $2, 1, 'sha256:t', 'v1', 'sha256:p', 'sig', $3, 'resident', 'a proof body')",
                    &[&did, &name, &world.scope],
                )
                .await
                .unwrap();
            g.client()
                .execute(
                    "INSERT INTO spine_leases (did, name, kind, scope, until) VALUES ($1, $2, 'resident', $3, now() + \
                     interval '1 hour') ON CONFLICT (did) DO NOTHING",
                    &[&did, &name, &world.scope],
                )
                .await
                .unwrap();
        }
        let (s, v) = knock(port, "GET", "/crew", None, &h).await; // a warm-up: the pool's line, the plan cache
        assert_eq!(s, 200, "{v}");
        // the kernel's own loops read the ground while we measure (the beats every few seconds), so
        // the judgment is on the CREW DOOR'S OWN tables: each read a fixed few times however large
        // the crew — the old door read the meter thirty times and the services sixty for thirty bodies
        g.client()
            .execute("SELECT pg_stat_force_next_flush()", &[])
            .await
            .unwrap(); // this connection's own inserts counted BEFORE the baseline
        tokio::time::sleep(Duration::from_millis(1500)).await;
        let before = table_reads(&g).await;
        let t0 = std::time::Instant::now();
        let (s, v) = knock(port, "GET", "/crew", None, &h).await;
        let took = t0.elapsed();
        assert_eq!(s, 200, "{v}");
        assert_eq!(v["crew"].as_array().map(Vec::len), Some(30), "thirty cards");
        tokio::time::sleep(Duration::from_millis(1500)).await;
        let after = table_reads(&g).await;
        let (_total, per) = reads_between(&before, &after);
        let own = [
            "spine_joins",
            "spine_leases",
            "spine_refusals",
            "spine_services",
            "spine_mind_assignments",
            "spine_meter",
        ];
        let mine: Vec<(String, i64)> = per
            .iter()
            .filter(|(t, _)| own.contains(&t.as_str()))
            .cloned()
            .collect();
        let reads: i64 = mine.iter().map(|(_, d)| d).sum();
        // the beats read joins and asks every second or so (about ten reads in the window); the old
        // door's signature was a table read ONCE PER BODY — thirty here, sixty for the services
        for (t, d) in &mine {
            assert!(
                *d < 15,
                "the crew door read {t} {d} times for thirty bodies — a fixed few, never one per body; all: {per:?}"
            );
        }
        assert!(
            reads <= 40,
            "the crew door's own tables read {reads} times for thirty bodies: {mine:?}"
        );
        println!(
            "doors · the perf cure: thirty bodies, one knock, the crew's own tables read {reads} times in all, {} ms",
            took.as_millis()
        );
        g.client()
            .execute(
                "DELETE FROM spine_joins WHERE scope = $1 AND name LIKE 'body%'",
                &[&world.scope],
            )
            .await
            .unwrap();
        g.client()
            .execute(
                "DELETE FROM spine_leases WHERE scope = $1 AND name LIKE 'body%'",
                &[&world.scope],
            )
            .await
            .unwrap();
    }

    println!("doors · the four doors answer on the Rust kernel alone: a kind declared and refused · a mark set with the interested asked · MITL's card with {} citations · the toggle recorded · the impact read from the ground and judged by the ladder, the ask filed to mitl", cites.len());
    lit.stop().await;
    let _ = orreth_spine::events::prune_namespace(&world.kafka, &format!("t{tok}")).await; // the proof's residue leaves with it
    let _ = std::fs::remove_dir_all(&home);
}
