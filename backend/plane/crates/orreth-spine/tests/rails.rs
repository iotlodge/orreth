// PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp2, the ground and the rails · 2026-09-22
//! The rails, proven on the dev rig (`spine/compose.yaml`) — Phase 0's and
//! Phase 1 sp1/sp2's laws, in Rust, on the same ground the Python spine
//! stands on. Runs only by name with the feature on:
//!
//!     cargo test -p orreth-spine --features rails --test rails -- --nocapture
//!
//! With no rig (CI's rust job has none) every test prints
//! "rails not up — skipped by name" and passes green WITHOUT proving anything:
//! the report line is the honest word. Each test stands on its own throwaway
//! schema (a ground of its own, per the ground law) and its own queue
//! namespace, so it can never race a live rig or another test. The shadow
//! test refuses to run while a Bridge holds :4600 (the stale-rig law).

#![cfg(feature = "rails")]

use orreth_spine::envelope::{self, Mint};
use orreth_spine::ground::{self, Ground};
use orreth_spine::inbox::{self, Outcome};
use orreth_spine::outbox::{self, MemorySink};
use orreth_spine::rail_error::RailError;
use orreth_spine::sinks::KafkaSink;
use orreth_spine::{events, heartbeat, rails};
use serde_json::{json, Value};
use std::time::Duration;

fn port_open(port: u16) -> bool {
    std::net::TcpStream::connect_timeout(
        &std::net::SocketAddr::from(([127, 0, 0, 1], port)),
        Duration::from_millis(400),
    )
    .is_ok()
}

/// The rig: the ground answers on :5433 (or `SPINE_PG` is set by hand).
fn rig_up(test: &str) -> bool {
    let up = std::env::var("SPINE_PG").is_ok() || port_open(5433);
    if !up {
        println!("rails not up — skipped by name: {test} (start the rig: scripts/dev.sh up)");
    }
    up
}

fn token() -> String {
    let e = Mint {
        kind: "event".into(),
        r#type: "t".into(),
        payload: json!({}),
        ..Default::default()
    }
    .mint()
    .unwrap();
    e["message_id"].as_str().unwrap()[4..10].to_string()
}

/// A ground of this test's own: a fresh schema, every table ensured at birth.
async fn own_ground(tok: &str) -> Ground {
    let mut g = Ground::connect(&rails::pg_dsn()).await.expect("the ground");
    let schema = format!("spine_rs_{tok}");
    g.client()
        .batch_execute(&format!(
            "DROP SCHEMA IF EXISTS {schema} CASCADE; CREATE SCHEMA {schema}"
        ))
        .await
        .unwrap();
    g.set_search_path(&schema).await.unwrap();
    g.ensure_all().await.expect("ensured at birth");
    g.client()
        .batch_execute(
            "CREATE TABLE IF NOT EXISTS spine_counter (aggregate_id text PRIMARY KEY, value int \
             NOT NULL DEFAULT 0)",
        )
        .await
        .unwrap();
    g
}

async fn drop_ground(g: &Ground, tok: &str) {
    g.client()
        .batch_execute(&format!("DROP SCHEMA IF EXISTS spine_rs_{tok} CASCADE"))
        .await
        .ok();
}

fn fact(typ: &str, aid: &str, seq: Option<i64>) -> Value {
    Mint {
        kind: "event".into(),
        r#type: typ.into(),
        universe_id: "u:dev".into(),
        scope_path: "u:dev".into(),
        payload: json!({"ref": format!("{aid}#{}", seq.unwrap_or(0)), "hash": "sha256:x"}),
        aggregate: seq.map(|s| json!({"type": "counter", "id": aid, "sequence": s})),
        ..Default::default()
    }
    .mint()
    .unwrap()
}

async fn counter(g: &Ground, aid: &str) -> i32 {
    g.client()
        .query_opt(
            "SELECT value FROM spine_counter WHERE aggregate_id = $1",
            &[&aid],
        )
        .await
        .unwrap()
        .map(|r| r.get(0))
        .unwrap_or(0)
}

async fn outbox_rows(g: &Ground, message_id: &str) -> Vec<(bool, i32)> {
    g.client()
        .query(
            "SELECT published_at IS NOT NULL, publish_attempts FROM spine_outbox WHERE message_id \
             = $1",
            &[&message_id],
        )
        .await
        .unwrap()
        .iter()
        .map(|r| (r.get(0), r.get(1)))
        .collect()
}

// ---- 1. the write side: state and event are one fate ----------------------------

#[tokio::test]
async fn commit_with_outbox_is_atomic_and_the_budget_refuses_by_name() {
    if !rig_up("commit_with_outbox_is_atomic_and_the_budget_refuses_by_name") {
        return;
    }
    let tok = token();
    let mut g = own_ground(&tok).await;
    let aid = format!("atomic-{tok}");

    // a dying write: no state, no event, no phantom
    let e = fact("orreth.counter.incremented.v1", &aid, None);
    let raw = envelope::encode(&e).unwrap();
    let mid = e["message_id"].as_str().unwrap().to_string();
    let a = aid.clone();
    let died = outbox::commit_with_outbox(&mut g, &raw, &mid, None, async move |tx| {
        tx.execute(
            "INSERT INTO spine_counter (aggregate_id, value) VALUES ($1, 1)",
            &[&a],
        )
        .await?;
        Err(RailError::Refused(
            "writer killed before commit (injected)".into(),
        ))
    })
    .await;
    assert!(died.is_err());
    assert_eq!(
        counter(&g, &aid).await,
        0,
        "the rolled-back state left no trace"
    );
    assert!(outbox_rows(&g, &mid).await.is_empty(), "and no outbox row");

    // a committed write: both rows are down, atomically
    let a = aid.clone();
    outbox::commit_with_outbox(&mut g, &raw, &mid, None, async move |tx| {
        tx.execute(
            "INSERT INTO spine_counter (aggregate_id, value) VALUES ($1, 1)",
            &[&a],
        )
        .await?;
        Ok(())
    })
    .await
    .unwrap();
    assert_eq!(counter(&g, &aid).await, 1);
    let body: Vec<u8> = g
        .client()
        .query_one(
            "SELECT body FROM spine_outbox WHERE message_id = $1",
            &[&mid],
        )
        .await
        .unwrap()
        .get(0);
    assert_eq!(body, raw, "the outbox carries the canonical bytes exactly");

    // the budget: one pending row, budget one → refused BY NAME, nothing written
    let e2 = fact("orreth.counter.incremented.v1", &aid, None);
    let raw2 = envelope::encode(&e2).unwrap();
    let mid2 = e2["message_id"].as_str().unwrap().to_string();
    let refused = outbox::commit_with_outbox(&mut g, &raw2, &mid2, Some(1), async |_tx| Ok(()))
        .await
        .unwrap_err();
    assert_eq!(
        refused.to_string(),
        "the outbox holds 1 unpublished rows — the declared budget is 1; publish (or raise the \
         budget) before writing more"
    );
    assert!(outbox_rows(&g, &mid2).await.is_empty());
    assert_eq!(outbox::outbox_lag(&g).await.unwrap().pending, 1);
    println!("rails · commit_with_outbox: a dying write left nothing; a committed one left both rows; the budget refused by name");
    drop_ground(&g, &tok).await;
}

// ---- 2. the relay: at-least-once, marked after the publish ------------------------

#[tokio::test]
async fn relay_publishes_at_least_once_and_marks() {
    if !rig_up("relay_publishes_at_least_once_and_marks") {
        return;
    }
    let tok = token();
    let mut g = own_ground(&tok).await;
    let e = fact(
        "orreth.counter.incremented.v1",
        &format!("relay-{tok}"),
        None,
    );
    let raw = envelope::encode(&e).unwrap();
    let mid = e["message_id"].as_str().unwrap().to_string();
    outbox::commit_with_outbox(&mut g, &raw, &mid, None, async |_tx| Ok(()))
        .await
        .unwrap();

    // the broker is down: the attempt is recorded, the row stays unpublished
    let mut sink = MemorySink {
        fail_before: 1,
        ..Default::default()
    };
    let r = outbox::relay_once(&g, &mut sink, 100).await.unwrap();
    assert_eq!((r.published, r.attempts, r.remaining), (0, 1, 1));
    assert_eq!(outbox_rows(&g, &mid).await, vec![(false, 1)]);
    assert!(sink.published.is_empty());

    // the relay dies AFTER the broker accepted: published again on retry —
    // at-least-once, never at-most-once — then marked
    let mut sink = MemorySink {
        fail_after: 1,
        ..Default::default()
    };
    let r = outbox::relay_once(&g, &mut sink, 100).await.unwrap();
    assert_eq!((r.published, r.remaining), (0, 1));
    let r = outbox::relay_once(&g, &mut sink, 100).await.unwrap();
    assert_eq!((r.published, r.remaining), (1, 0));
    assert_eq!(sink.published.len(), 2, "the wire carried it twice");
    assert!(sink.published.iter().all(|(m, b)| m == &mid && b == &raw));
    assert_eq!(outbox_rows(&g, &mid).await, vec![(true, 3)]);
    assert_eq!(outbox::outbox_lag(&g).await.unwrap().pending, 0);
    println!("rails · relay_once: a refused publish recorded and retried; a death after accept published twice; marked once");
    drop_ground(&g, &tok).await;
}

// ---- 3. the inbox: effects once; stale skipped; a gap refuses -------------------------

#[tokio::test]
async fn inbox_absorbs_a_duplicate_and_a_gap_refuses_to_guess() {
    if !rig_up("inbox_absorbs_a_duplicate_and_a_gap_refuses_to_guess") {
        return;
    }
    let tok = token();
    let mut g = own_ground(&tok).await;
    let consumer = format!("c-{tok}");
    let aid = format!("inbox-{tok}");
    g.client()
        .execute(
            "INSERT INTO spine_counter (aggregate_id) VALUES ($1)",
            &[&aid],
        )
        .await
        .unwrap();
    let bump = |aid: String| {
        async move |tx: &tokio_postgres::Transaction<'_>| {
            tx.execute(
                "UPDATE spine_counter SET value = value + 1 WHERE aggregate_id = $1",
                &[&aid],
            )
            .await?;
            Ok(())
        }
    };

    // five deliveries of one message → one effect, four confessed duplicates
    let mid = format!("msg_{tok}_once");
    let mut outcomes = Vec::new();
    for _ in 0..5 {
        outcomes.push(
            inbox::apply_once(&mut g, &consumer, &mid, bump(aid.clone()))
                .await
                .unwrap(),
        );
    }
    assert_eq!(outcomes[0], Outcome::Applied);
    assert!(outcomes[1..].iter().all(|o| *o == Outcome::Duplicate));
    assert_eq!(counter(&g, &aid).await, 1);
    assert_eq!(inbox::duplicates_seen(&g, &consumer).await.unwrap(), 4);

    // the ordering law: 1 · 2 apply; 1 again is stale; 4 is a gap; 3 applies
    let typ = "orreth.counter.incremented.v1";
    let (e1, e2, e3, e4) = (
        fact(typ, &aid, Some(1)),
        fact(typ, &aid, Some(2)),
        fact(typ, &aid, Some(3)),
        fact(typ, &aid, Some(4)),
    );
    assert_eq!(
        inbox::apply_event(&mut g, &consumer, &e1, bump(aid.clone()))
            .await
            .unwrap(),
        Outcome::Applied
    );
    assert_eq!(
        inbox::apply_event(&mut g, &consumer, &e2, bump(aid.clone()))
            .await
            .unwrap(),
        Outcome::Applied
    );
    // a redelivery behind the cursor is STALE (the sequence law speaks before
    // the footprint does — as the Python reference orders it)
    assert_eq!(
        inbox::apply_event(&mut g, &consumer, &e1, bump(aid.clone()))
            .await
            .unwrap(),
        Outcome::Stale
    );
    let stale = fact(typ, &aid, Some(1));
    assert_eq!(
        inbox::apply_event(&mut g, &consumer, &stale, bump(aid.clone()))
            .await
            .unwrap(),
        Outcome::Stale
    );
    let gap = inbox::apply_event(&mut g, &consumer, &e4, bump(aid.clone()))
        .await
        .unwrap_err();
    assert_eq!(
        gap.to_string(),
        format!("gap on {aid}: expected sequence 3, got 4 — fetch the missing events; never guess")
    );
    assert_eq!(counter(&g, &aid).await, 3, "the gap applied nothing");
    assert_eq!(
        inbox::apply_event(&mut g, &consumer, &e3, bump(aid.clone()))
            .await
            .unwrap(),
        Outcome::Applied
    );
    assert_eq!(
        inbox::apply_event(&mut g, &consumer, &e4, bump(aid.clone()))
            .await
            .unwrap(),
        Outcome::Applied
    );
    assert_eq!(counter(&g, &aid).await, 5);

    // the ground law's evidence: a second connection to this ground is born flagged
    let mut born_later = Ground::connect(&rails::pg_dsn()).await.unwrap();
    born_later
        .set_search_path(&format!("spine_rs_{tok}"))
        .await
        .unwrap();
    assert!(ground::born_flagged(born_later.key(), "inbox"));
    assert!(
        !born_later.ensure("inbox", inbox::DDL).await.unwrap(),
        "no DDL ran on a flagged ground"
    );
    println!("rails · inbox: 5 deliveries → 1 effect (4 confessed); stale skipped; the gap refused by name; a later connection born flagged");
    drop_ground(&g, &tok).await;
}

// ---- 4. the heartbeat through each rail, and all three composed ------------------------

#[tokio::test]
async fn the_heartbeat_rides_all_three_rails() {
    if !rig_up("the_heartbeat_rides_all_three_rails") {
        return;
    }
    let tok = token();
    let mut g = own_ground(&tok).await;
    let ns = format!("t{tok}");
    let scope = format!("u:test-{tok}");
    let (rabbit, kafka) = (rails::rabbit_url(), rails::kafka_bootstrap());

    let ground_ms =
        heartbeat::ground_breath(&mut g, &heartbeat::beat("event", "ground", &scope, &scope))
            .await
            .expect("the ground breathes");
    let invoke_ms = heartbeat::invoke_breath(
        &rabbit,
        &heartbeat::beat("command", "invoke", &scope, &scope),
        &ns,
        Duration::from_secs(10),
    )
    .await
    .expect("the invoke rail breathes");
    let events_ms = heartbeat::events_breath(
        &kafka,
        &heartbeat::beat("event", "events", &scope, &scope),
        Duration::from_secs(30),
    )
    .await
    .expect("the events rail breathes");

    // composed: ground row + outbox → relay → Kafka → a consumer → the inbox, once
    let mut composed = heartbeat::beat("event", "all", &scope, &scope);
    composed["type"] = json!(format!("orreth.test-{tok}.heartbeat.v1"));
    let (first, again) = heartbeat::all_rails(
        &mut g,
        &kafka,
        &composed,
        &format!("hb-{tok}"),
        Duration::from_secs(30),
    )
    .await
    .expect("all three rails");
    assert_eq!((first, again), (Outcome::Applied, Outcome::Duplicate));
    let mid = composed["message_id"].as_str().unwrap();
    assert_eq!(
        outbox_rows(&g, mid).await,
        vec![(true, 1)],
        "relayed and marked"
    );

    // and the invoke command road: a serve command lands on the session's own bench
    let cmd = Mint {
        kind: "command".into(),
        r#type: "orreth.resident.serve.v1".into(),
        universe_id: scope.clone(),
        scope_path: scope.clone(),
        payload: json!({"ref": "ask_x", "hash": "sha256:x", "target": "echo"}),
        ..Default::default()
    }
    .mint()
    .unwrap();
    orreth_spine::invoke::publish_command(&rabbit, &cmd, &ns)
        .await
        .unwrap();
    let raw = envelope::encode(&cmd).unwrap();
    let back = orreth_spine::invoke::receive(
        &rabbit,
        &rails::serve_queue(&ns, Some("echo")),
        &rails::serve_key(&ns, Some("echo")),
        Duration::from_secs(10),
        |b| b == raw,
    )
    .await
    .unwrap();
    assert_eq!(back, raw);
    println!(
        "rails · the rig breathes from Rust: ground {:.1} ms · invoke {:.1} ms · events {:.1} ms · all three composed (applied, then duplicate) · a targeted serve command round-tripped on {}",
        ground_ms.as_secs_f64() * 1e3,
        invoke_ms.as_secs_f64() * 1e3,
        events_ms.as_secs_f64() * 1e3,
        rails::serve_queue(&ns, Some("echo"))
    );
    drop_ground(&g, &tok).await;
}

// ---- 5. SHADOW: two spines, one ground, one truth --------------------------------------

fn spine_dir() -> std::path::PathBuf {
    std::path::PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("../../../../spine")
}

/// Run the Python reference in the spine's own venv, on THIS test's benches.
async fn python(tok: &str, code: &str) -> String {
    let out = tokio::process::Command::new("uv")
        .args(["run", "--quiet", "python", "-c", code])
        .current_dir(spine_dir())
        .env("SPINE_QUEUE_NS", format!("t{tok}"))
        .env("SPINE_SCOPE", format!("u:shadow-{tok}"))
        .env("SPINE_PG", rails::pg_dsn())
        .output()
        .await
        .expect("uv runs the Python reference");
    let stdout = String::from_utf8_lossy(&out.stdout).to_string();
    assert!(
        out.status.success(),
        "the Python reference refused:\n{}\n{}",
        stdout,
        String::from_utf8_lossy(&out.stderr)
    );
    stdout
}

#[tokio::test]
async fn shadow_the_two_spines_share_one_ground_and_one_truth() {
    if !rig_up("shadow_the_two_spines_share_one_ground_and_one_truth") {
        return;
    }
    if port_open(4600) {
        println!("a Bridge holds :4600 — the shadow proof refuses to run beside a live rig (stop it: scripts/dev.sh bridge stop)");
        return;
    }
    let tok = token();
    let kafka = rails::kafka_bootstrap();
    let typ = format!("orreth.shadow-{tok}.v1");
    let aid = format!("shadow-{tok}");

    // the Python spine's birth on the PUBLIC ground: every table it knows
    python(
        &tok,
        "from orreth_spine import ground; import psycopg, os\n\
                  c = psycopg.connect(os.environ['SPINE_PG'], autocommit=True)\n\
                  ground.ensure_all(c); print('python: ground ensured')",
    )
    .await;
    // the Rust spine stands on the SAME ground (public schema), same tables
    let mut g = Ground::connect(&rails::pg_dsn()).await.unwrap();
    g.ensure_all().await.unwrap();
    g.client()
        .batch_execute(
            "CREATE TABLE IF NOT EXISTS spine_shadow_marks (tok text NOT NULL, side text NOT \
             NULL, message_id text NOT NULL, PRIMARY KEY (tok, side, message_id))",
        )
        .await
        .unwrap();

    // ---- Rust → Python: Rust commits; the PYTHON relay publishes; the PYTHON projector reads
    let e = fact(&typ, &aid, Some(1));
    let raw = envelope::encode(&e).unwrap();
    let mid_rs = e["message_id"].as_str().unwrap().to_string();
    let (t, m) = (tok.clone(), mid_rs.clone());
    outbox::commit_with_outbox(&mut g, &raw, &mid_rs, None, async move |tx| {
        tx.execute(
            "INSERT INTO spine_shadow_marks (tok, side, message_id) VALUES ($1, 'rust-wrote', $2)",
            &[&t, &m],
        )
        .await?;
        Ok(())
    })
    .await
    .unwrap();
    let py = python(&tok, &format!(
        "from orreth_spine import outbox, sinks, projector, envelope as ev; import psycopg, os\n\
         c = psycopg.connect(os.environ['SPINE_PG'], autocommit=True)\n\
         n = outbox.drain(c, sinks.KafkaSink())\n\
         t = projector.run_once(c, group='shadow-py-{tok}', topics=['{typ}'], consumer_name='shadow-py-{tok}',\n\
             apply=lambda cur, env: cur.execute(\"INSERT INTO spine_shadow_marks (tok, side, message_id) VALUES (%s, 'python-saw', %s)\", ('{tok}', env['message_id'])))\n\
         print('python: relayed', n, 'projected', t)")).await;
    print!("{py}");
    let saw: i64 = g
        .client()
        .query_one(
            "SELECT count(*) FROM spine_shadow_marks WHERE tok = $1 AND side = 'python-saw' AND \
             message_id = $2",
            &[&tok, &mid_rs],
        )
        .await
        .unwrap()
        .get(0);
    assert_eq!(
        saw, 1,
        "the Python consumer saw the fact the Rust outbox committed"
    );
    let footprint: String = g
        .client()
        .query_one(
            "SELECT status FROM spine_inbox WHERE consumer = $1 AND message_id = $2",
            &[&format!("shadow-py-{tok}"), &mid_rs],
        )
        .await
        .unwrap()
        .get(0);
    assert_eq!(
        footprint, "done",
        "the Python inbox's footprint on the shared table"
    );
    assert_eq!(
        outbox_rows(&g, &mid_rs).await,
        vec![(true, 1)],
        "the Python relay marked the Rust row"
    );

    // ---- Python → Rust: Python commits; the RUST relay publishes; the RUST reader + inbox absorb
    let py = python(&tok, &format!(
        "from orreth_spine import outbox, envelope as ev; import psycopg, os\n\
         c = psycopg.connect(os.environ['SPINE_PG'], autocommit=True)\n\
         e = ev.make_envelope(kind='event', type='{typ}', universe_id='u:dev', scope_path='u:dev',\n\
             payload={{'ref': '{aid}#2', 'hash': 'sha256:x'}}, aggregate={{'type': 'counter', 'id': '{aid}', 'sequence': 2}})\n\
         outbox.commit_with_outbox(c, ev.encode(e), e['message_id'],\n\
             lambda cur: cur.execute(\"INSERT INTO spine_shadow_marks (tok, side, message_id) VALUES (%s, 'python-wrote', %s)\", ('{tok}', e['message_id'])))\n\
         print(e['message_id'])")).await;
    let mid_py = py.trim().lines().last().unwrap().trim().to_string();
    assert!(
        mid_py.starts_with("msg_"),
        "python printed the message id: {py}"
    );
    let mut sink = KafkaSink::new(&kafka).unwrap();
    outbox::drain(&g, &mut sink, Duration::from_secs(30))
        .await
        .unwrap();
    assert_eq!(
        outbox_rows(&g, &mid_py).await,
        vec![(true, 1)],
        "the Rust relay marked the Python row"
    );
    // one partition, published in order: Python relayed seq 1 before Rust relayed
    // seq 2 — the Rust reader sees them in that order and feeds the inbox's cursor
    // honestly (1 then 2), never a guess
    let consumer = format!("shadow-rs-{tok}");
    let reader = events::Reader::open(&kafka, &format!("shadow-rs-{tok}"), &[&typ], true)
        .await
        .unwrap();
    let e1 = reader
        .read_until(Duration::from_secs(30), |e| {
            e["message_id"].as_str() == Some(&mid_rs)
        })
        .await
        .expect("the Rust reader sees the fact Python relayed (seq 1)");
    let seen = reader
        .read_until(Duration::from_secs(30), |e| {
            e["message_id"].as_str() == Some(&mid_py)
        })
        .await
        .expect("the Rust reader sees the fact Python committed (seq 2)");
    assert_eq!(e1["aggregate"]["sequence"], json!(1));
    assert_eq!(seen["aggregate"]["sequence"], json!(2));
    for env in [&e1, &seen] {
        let (t, m) = (tok.clone(), env["message_id"].as_str().unwrap().to_string());
        let o = inbox::apply_event(&mut g, &consumer, env, async move |tx| {
            tx.execute(
                "INSERT INTO spine_shadow_marks (tok, side, message_id) VALUES ($1, 'rust-saw', $2)",
                &[&t, &m],
            )
            .await?;
            Ok(())
        })
        .await
        .unwrap();
        assert_eq!(o, Outcome::Applied);
    }
    // redelivered behind the cursor: STALE, no second effect (the Python law)
    let again = inbox::apply_event(&mut g, &consumer, &seen, async |_tx| Ok(()))
        .await
        .unwrap();
    assert_eq!(again, Outcome::Stale);
    let marks: Vec<(String, String)> = g
        .client()
        .query(
            "SELECT side, message_id FROM spine_shadow_marks WHERE tok = $1 ORDER BY side, message_id",
            &[&tok],
        )
        .await
        .unwrap()
        .iter()
        .map(|r| (r.get(0), r.get(1)))
        .collect();
    let sides: Vec<&str> = marks.iter().map(|(s, _)| s.as_str()).collect();
    assert_eq!(
        sides,
        [
            "python-saw",
            "python-wrote",
            "rust-saw",
            "rust-saw",
            "rust-wrote"
        ]
    );
    println!("rails · SHADOW: Rust wrote {mid_rs} → Python relayed + projected it (inbox footprint done); Python wrote {mid_py} → Rust relayed + read + absorbed it (a redelivery read stale); one ground, one truth, marks: {sides:?}");
    g.client()
        .execute("DELETE FROM spine_shadow_marks WHERE tok = $1", &[&tok])
        .await
        .ok();
}
