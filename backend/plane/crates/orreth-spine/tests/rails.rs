// PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp2, the ground and the rails · 2026-09-22
// Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp7, cells: the shadow rides the cell's topic · 2026-09-25
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
//! test refuses to run while a kernel holds :4600 or the reference :4601 (the stale-rig law).

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
    if port_open(4600) || port_open(4601) {
        println!("a kernel holds :4600 or the reference :4601 — the shadow proof refuses to run beside a live rig (stop it: scripts/dev.sh kernel stop · scripts/dev.sh reference stop)");
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
        "from orreth_spine import outbox, sinks, projector, rails, envelope as ev; import psycopg, os\n\
         c = psycopg.connect(os.environ['SPINE_PG'], autocommit=True)\n\
         n = outbox.drain(c, sinks.KafkaSink())\n\
         t = projector.run_once(c, group='shadow-py-{tok}', topics=[rails.topic('{typ}')], consumer_name='shadow-py-{tok}',\n\
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
    let mut sink = KafkaSink::new(&kafka, &format!("t{tok}")).unwrap(); // P7 sp7: the cell's namespace
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
    let worn = orreth_spine::rails::topic(&typ, &format!("t{tok}"));
    let reader = events::Reader::open(&kafka, &format!("shadow-rs-{tok}"), &[&worn], true)
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

// ---- 6. THE MIGRATOR (re-base sp1, lock 2): one writer, the rest wait and verify ---------

/// The columns a schema holds, `spine_%` only — the contract both kernels must produce.
async fn columns(g: &Ground, schema: &str) -> Vec<(String, String, String, String)> {
    g.client()
        .query(
            "SELECT table_name, column_name, data_type, is_nullable FROM information_schema.columns \
             WHERE table_schema = $1 AND table_name LIKE 'spine\\_%' ORDER BY 1, 2",
            &[&schema],
        )
        .await
        .unwrap()
        .iter()
        .map(|r| (r.get(0), r.get(1), r.get(2), r.get(3)))
        .collect()
}

/// The index names a schema holds, `spine_%` tables only.
async fn indexes(g: &Ground, schema: &str) -> Vec<String> {
    g.client()
        .query(
            "SELECT indexname FROM pg_indexes WHERE schemaname = $1 AND tablename LIKE 'spine\\_%' ORDER BY 1",
            &[&schema],
        )
        .await
        .unwrap()
        .iter()
        .map(|r| r.get::<_, String>(0))
        .collect()
}

#[tokio::test]
async fn schema_the_first_birth_migrates_and_the_next_verifies() {
    if !rig_up("schema_the_first_birth_migrates_and_the_next_verifies") {
        return;
    }
    let tok = token();
    let g = own_ground(&tok).await; // its birth: the first writer
    let schema = format!("spine_rs_{tok}");
    let row = g
        .client()
        .query_one("SELECT version, kernel FROM spine_schema", &[])
        .await
        .unwrap();
    assert_eq!(
        (row.get::<_, i32>(0), row.get::<_, String>(1)),
        (orreth_spine::schema::SCHEMA_VERSION, "rust".to_string())
    );
    let tables: Vec<String> = g
        .client()
        .query(
            "SELECT table_name FROM information_schema.tables WHERE table_schema = $1 AND \
             table_name LIKE 'spine\\_%' ORDER BY 1",
            &[&schema],
        )
        .await
        .unwrap()
        .iter()
        .map(|r| r.get(0))
        .collect();
    let mut declared = orreth_spine::schema::tables();
    declared.sort();
    let tables: Vec<String> = tables
        .into_iter()
        .filter(|t| t != "spine_counter")
        .collect(); // own_ground's test table
    assert_eq!(
        tables, declared,
        "the ground holds exactly the declared tables"
    );
    // the next birth: no DDL, verified
    let mut b = Ground::connect(&rails::pg_dsn()).await.unwrap();
    b.set_search_path(&schema).await.unwrap();
    let m = b.ensure_all().await.unwrap();
    assert!(!m.migrated && m.found == orreth_spine::schema::SCHEMA_VERSION);
    assert!(m.words().contains("verified"));
    let n: i64 = g
        .client()
        .query_one("SELECT count(*) FROM spine_schema", &[])
        .await
        .unwrap()
        .get(0);
    assert_eq!(n, 1, "one version row — one writer");
    // a ground whose version lies is refused in plain words
    g.client()
        .batch_execute("DROP TABLE spine_mitl")
        .await
        .unwrap();
    let mut c = Ground::connect(&rails::pg_dsn()).await.unwrap();
    c.set_search_path(&schema).await.unwrap();
    let e = c.ensure_all().await.unwrap_err().to_string();
    assert!(
        e.contains("spine_mitl is missing") && e.contains("not stood on"),
        "{e}"
    );
    println!("rails · the migrator: the first birth wrote version {}, the next verified, the lie refused",
             orreth_spine::schema::SCHEMA_VERSION);
    drop_ground(&g, &tok).await;
}

#[tokio::test]
async fn schema_two_kernels_birthing_together_have_one_writer() {
    if !rig_up("schema_two_kernels_birthing_together_have_one_writer") {
        return;
    }
    let tok = token();
    let schema = format!("spine_rs_{tok}");
    let g = Ground::connect(&rails::pg_dsn()).await.unwrap();
    g.client()
        .batch_execute(&format!(
            "DROP SCHEMA IF EXISTS {schema} CASCADE; CREATE SCHEMA {schema}"
        ))
        .await
        .unwrap();
    let mut a = Ground::connect(&rails::pg_dsn()).await.unwrap();
    let mut b = Ground::connect(&rails::pg_dsn()).await.unwrap();
    let mut c = Ground::connect(&rails::pg_dsn()).await.unwrap();
    a.set_search_path(&schema).await.unwrap();
    b.set_search_path(&schema).await.unwrap();
    c.set_search_path(&schema).await.unwrap();
    let (ma, mb, mc) = tokio::join!(a.ensure_all(), b.ensure_all(), c.ensure_all());
    let ms = [ma.unwrap(), mb.unwrap(), mc.unwrap()];
    assert_eq!(
        ms.iter().filter(|m| m.migrated).count(),
        1,
        "exactly one writer: {ms:?}"
    );
    assert!(ms
        .iter()
        .all(|m| m.ground == orreth_spine::schema::SCHEMA_VERSION));
    println!(
        "rails · the migrator: three kernels born together — one wrote, two waited and verified"
    );
    drop_ground(&g, &tok).await;
}

#[tokio::test]
async fn schema_the_two_kernels_migrate_one_ground_the_same() {
    if !rig_up("schema_the_two_kernels_migrate_one_ground_the_same") {
        return;
    }
    let tok = token();
    let g = own_ground(&tok).await; // the Rust birth on schema spine_rs_<tok>
    let py_schema = format!("spine_py_{tok}");
    // the Python reference's birth on ITS OWN fresh schema, through its own migrator
    let out = python(
        &tok,
        &format!(
            "from orreth_spine import ground; import psycopg, os\n\
             c = psycopg.connect(os.environ['SPINE_PG'], autocommit=True)\n\
             c.execute('DROP SCHEMA IF EXISTS {py_schema} CASCADE'); c.execute('CREATE SCHEMA {py_schema}')\n\
             c.execute('SET search_path TO {py_schema}')\n\
             m = ground.ensure_all(c); print(m['migrated'], m['ground'], ground.SCHEMA_VERSION)"
        ),
    )
    .await;
    assert_eq!(
        out.trim(),
        format!("True {v} {v}", v = orreth_spine::schema::SCHEMA_VERSION),
        "the reference carries the same version"
    );
    let rs = columns(&g, &format!("spine_rs_{tok}")).await;
    let py = columns(&g, &py_schema).await;
    // schema 2: the indexes too — the same names on both kernels (the doors' and the relay's cure)
    let (rs_idx, py_idx) = (
        indexes(&g, &format!("spine_rs_{tok}")).await,
        indexes(&g, &py_schema).await,
    );
    let rs_idx: Vec<String> = rs_idx
        .into_iter()
        .filter(|i| i != "spine_counter_pkey")
        .collect(); // own_ground's test table
    assert_eq!(rs_idx, py_idx, "the two kernels' indexes differ");
    assert!(
        rs_idx.iter().any(|i| i == "spine_outbox_pending"),
        "the relay's partial index stands"
    );
    let rs: Vec<_> = rs.into_iter().filter(|c| c.0 != "spine_counter").collect();
    let only_rs: Vec<_> = rs.iter().filter(|c| !py.contains(c)).collect();
    let only_py: Vec<_> = py.iter().filter(|c| !rs.contains(c)).collect();
    assert!(
        only_rs.is_empty() && only_py.is_empty(),
        "the two kernels' schemas differ —\n  only the Rust kernel: {only_rs:?}\n  only the reference: {only_py:?}"
    );
    println!(
        "rails · the migrator: both kernels stand {} columns over {} tables and {} indexes, the same",
        rs.len(),
        orreth_spine::schema::tables().len(),
        rs_idx.len()
    );
    g.client()
        .batch_execute(&format!("DROP SCHEMA IF EXISTS {py_schema} CASCADE"))
        .await
        .ok();
    drop_ground(&g, &tok).await;
}

// ---- 7. POISON-PARKING (re-base sp1): parked with its evidence, the rail holds, a person advances --

#[tokio::test]
async fn poison_parks_visibly_and_the_dispatcher_holds_until_a_person_advances() {
    if !rig_up("poison_parks_visibly_and_the_dispatcher_holds_until_a_person_advances") {
        return;
    }
    use orreth_spine::dispatcher::{self, Meter, CONSUMER};
    use orreth_spine::world::World;
    use rdkafka::producer::{FutureProducer, FutureRecord};
    use std::sync::atomic::{AtomicBool, Ordering};
    use std::sync::Arc;
    let tok = token();
    let schema = format!("spine_rs_{tok}");
    let mut g = own_ground(&tok).await;
    let mut w = World::from_env();
    w.scope = format!("u:poison-{tok}");
    w.ns = format!("p{tok}");
    let topic = rails::topic(orreth_spine::asks::ASK_RECEIVED, &w.ns);
    events::declare_topics(&w.kafka, &[&topic]).await.unwrap();
    let producer: FutureProducer = rdkafka::config::ClientConfig::new()
        .set("bootstrap.servers", &w.kafka)
        .create()
        .unwrap();
    // the poison first — bytes that are not an envelope
    producer
        .send(
            FutureRecord::to(&topic)
                .key("poison")
                .payload(b"this is not an envelope"),
            Duration::from_secs(10),
        )
        .await
        .map_err(|(e, _)| e)
        .unwrap();
    // then a good ask of THIS world, behind it
    let good = Mint {
        kind: "event".into(),
        r#type: orreth_spine::asks::ASK_RECEIVED.into(),
        universe_id: w.scope.clone(),
        scope_path: w.scope.clone(),
        payload: json!({"ref": format!("ask_{tok}"), "hash": "sha256:-", "text": "hello", "person": "did:orreth:person:t"}),
        ..Default::default()
    }
    .mint()
    .unwrap();
    let raw = envelope::encode(&good).unwrap();
    producer
        .send(
            FutureRecord::to(&topic).key("good").payload(&raw),
            Duration::from_secs(10),
        )
        .await
        .map_err(|(e, _)| e)
        .unwrap();
    // the dispatcher stands on the same ground, its own line
    let mut gd = Ground::connect(&rails::pg_dsn()).await.unwrap();
    gd.set_search_path(&schema).await.unwrap();
    gd.ensure_all().await.unwrap();
    let stop = Arc::new(AtomicBool::new(false));
    let ready = Arc::new(AtomicBool::new(false));
    let meter = Arc::new(Meter::default());
    let group = dispatcher::group_per_life();
    let (w2, stop2, ready2, meter2) = (w.clone(), stop.clone(), ready.clone(), meter.clone());
    let task = tokio::spawn(async move {
        dispatcher::run_dispatcher(&mut gd, &w2, &group, stop2, ready2, meter2).await
    });
    // parked, with its evidence, within the deadline
    let deadline = std::time::Instant::now() + Duration::from_secs(40);
    while inbox::parked_count(&g, CONSUMER).await.unwrap() == 0 {
        assert!(
            std::time::Instant::now() < deadline,
            "the poison was never parked"
        );
        tokio::time::sleep(Duration::from_millis(300)).await;
    }
    let rows = inbox::parked(&g, Some(CONSUMER), 10).await.unwrap();
    assert_eq!(rows.len(), 1);
    let p = &rows[0];
    assert!(
        p["reason"]
            .as_str()
            .unwrap()
            .starts_with("undecodable body:"),
        "{p}"
    );
    assert_eq!(p["bytes"], json!(23));
    assert_eq!(
        p["hash"],
        json!(orreth_spine::ask::body_hash(b"this is not an envelope"))
    );
    assert_eq!(p["topic"].as_str().unwrap(), topic);
    assert!(p["words"]
        .as_str()
        .unwrap()
        .contains("holds there until a person advances it"));
    let id = p["parked_id"].as_i64().unwrap();
    // the fact rode the outbox with the row
    let facts: Vec<Value> = g
        .client()
        .query(
            "SELECT body FROM spine_outbox ORDER BY outbox_id DESC LIMIT 5",
            &[],
        )
        .await
        .unwrap()
        .iter()
        .filter_map(|r| envelope::decode(&r.get::<_, Vec<u8>>(0)).ok())
        .collect();
    let parked_fact = facts
        .iter()
        .find(|e| e["type"] == json!(orreth_spine::ask::INBOX_PARKED))
        .expect("the parked fact on the outbox");
    assert_eq!(parked_fact["payload"]["ref"], json!(format!("parked:{id}")));
    assert_eq!(parked_fact["authority_chain"], json!(["the kernel"]));
    // the rail HOLDS: the good ask behind the poison is not dispatched
    tokio::time::sleep(Duration::from_secs(3)).await;
    assert_eq!(meter.read().0, 0, "the dispatcher went past the poison");
    assert_eq!(meter.parked.load(Ordering::Relaxed), 1);
    // a person's word: advanced — recorded and said
    let v = inbox::advance(&mut g, &w.scope, id, "did:orreth:person:jb")
        .await
        .unwrap()
        .expect("the parked row");
    assert_eq!(
        (v["advanced"].clone(), v["already"].clone()),
        (json!(true), json!(false))
    );
    assert_eq!(v["advanced_by"], json!("did:orreth:person:jb"));
    let deadline = std::time::Instant::now() + Duration::from_secs(20);
    while meter.read().0 == 0 {
        assert!(
            std::time::Instant::now() < deadline,
            "the dispatcher never went on after the advance"
        );
        tokio::time::sleep(Duration::from_millis(300)).await;
    }
    assert_eq!(inbox::parked_count(&g, CONSUMER).await.unwrap(), 0);
    let again = inbox::advance(&mut g, &w.scope, id, "did:orreth:person:jb")
        .await
        .unwrap()
        .unwrap();
    assert_eq!(again["already"], json!(true));
    assert!(inbox::advance(&mut g, &w.scope, 999_999, "x")
        .await
        .unwrap()
        .is_none());
    stop.store(true, Ordering::Relaxed);
    let _ = tokio::time::timeout(Duration::from_secs(15), task).await;
    println!("rails · poison-parking: parked:{id} with 23 bytes of evidence and its fact, the good ask held behind it, advanced on a person's word, then dispatched");
    drop_ground(&g, &tok).await;
}

// ---- 8. RETENTION (the perf cure, 2026-09-29): the outbox is a queue, not the log ------------

#[tokio::test]
async fn retention_prunes_old_published_rows_and_never_an_unpublished_one() {
    if !rig_up("retention_prunes_old_published_rows_and_never_an_unpublished_one") {
        return;
    }
    let tok = token();
    let g = own_ground(&tok).await;
    for (mid, published, age_days) in [
        ("msg_old_published", true, 10),
        ("msg_new_published", true, 1),
        ("msg_old_unpublished", false, 10),
    ] {
        g.client()
            .execute(
                "INSERT INTO spine_outbox (message_id, body, committed_at, published_at) VALUES ($1, $2, now() - \
                 ($3 * interval '1 day'), CASE WHEN $4 THEN now() - ($3 * interval '1 day') ELSE NULL END)",
                &[&mid, &b"{}".as_slice(), &(age_days as f64), &published],
            )
            .await
            .unwrap();
    }
    let n = outbox::prune(&g, 7.0).await.unwrap();
    assert_eq!(n, 1, "the old published row alone");
    let left: Vec<String> = g
        .client()
        .query("SELECT message_id FROM spine_outbox ORDER BY 1", &[])
        .await
        .unwrap()
        .iter()
        .map(|r| r.get(0))
        .collect();
    assert_eq!(left, vec!["msg_new_published", "msg_old_unpublished"]);
    assert_eq!(outbox::keep_days(), 7.0);
    println!(
        "rails · retention: one old published row pruned; the new one and the unpublished one kept"
    );
    drop_ground(&g, &tok).await;
}
