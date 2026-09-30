// PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp2, the ground and the rails · 2026-09-22
// Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp4, the loops' three tags · 2026-09-23
// Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp3, the ask road: the road's six tags at birth · 2026-09-22
// Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch row 4, re-base sp1: THE MIGRATOR (lock 2) — the single writer, the version on the ground, the later kernel waits and verifies · 2026-09-28
// Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch row 4, the honest glass sp2: THE GROUND'S PRUNE — one world's rows gone across every table with a scope column (`prune_scope`; a proof's teardown) · 2026-09-29
//! The ground — mirrors `orreth_spine.ground` and the memo half of
//! `orreth_spine.outbox` (`once` · `ground_key` · `mark_ground_done`).
//!
//! The law (canon 0008's ground law, found live at the intent sp1 relight
//! and sharpened in CI 2026-09-21): DDL runs ONCE per GROUND per PROCESS —
//! never per connection, never inside a serve. A ground is the DSN plus the
//! connection's `search_path` (a test schema and the public one are two
//! grounds). `once(tag)` is true the first time this process sees the tag on
//! this ground; a connection born after a birth FINISHED (`ensure_all` ran to
//! its end and `mark_ground_done` was called) is born flagged and runs no DDL
//! at all — flagged only once the birth has finished, never when a first
//! caller merely claimed the tag (a thread born mid-birth once skipped DDL,
//! hit an undefined table, and the relay died). Every DDL runs inside one
//! transaction holding the advisory lock 742199, the same lock the Python
//! spine takes, so two spines standing on one ground never race a `CREATE`.
//!
//! The tables are THE SAME tables the Python spine uses — same names, same
//! columns, the same `CREATE TABLE IF NOT EXISTS` words — so both spines can
//! stand on one ground in shadow (the sp2 proof).
//!
//! THE MIGRATOR (lock 2, re-base sp1 — "the single-writer schema migrator"):
//! the memo above is per PROCESS; the ground itself now remembers, in
//! `spine_schema`, which VERSION of the schema it holds. A birth takes the
//! DDL lock, creates the version table if it is missing, reads the highest
//! version recorded, and then does ONE of two things: below this kernel's
//! `SCHEMA_VERSION` it runs every statement this kernel knows (all
//! `IF NOT EXISTS` — an old ground is grown, a fresh one is born) and records
//! the version; at or past it, it runs NO DDL and VERIFIES that every table it
//! declares stands, refusing to light on a ground whose version lies. Two
//! kernels lighting together on a fresh ground: the second waits at the lock
//! while the first migrates, then verifies — one writer, ever. Hundreds of
//! kernels on one ground cost one migration, not hundreds of `ALTER`s.

use crate::rail_error::RailError;
use serde_json::{json, Value};
use std::collections::{HashMap, HashSet};
use std::sync::{Mutex, OnceLock};
use tokio_postgres::{Client, NoTls};

/// The DDL race guard — `pg_advisory_xact_lock(742199)`, as Python takes it.
pub const DDL_LOCK: i64 = 742199;

/// The tags this spine ensures at birth — every tag the migrator runs, in order
/// (the rails' three, then the road; `schema::every_ddl`).
pub fn tags() -> Vec<&'static str> {
    crate::schema::every_ddl()
        .into_iter()
        .map(|(tag, _)| tag)
        .collect()
}

/// What a birth found on the ground and what it did (lock 2's honest answer;
/// the health door says it).
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct Migration {
    /// The version the ground held before this birth (0: a ground never versioned).
    pub found: i32,
    /// The version the ground holds now.
    pub ground: i32,
    /// This kernel's own schema version.
    pub kernel: i32,
    /// Did THIS birth run the DDL (the single writer)? Else it waited and verified.
    pub migrated: bool,
}

impl Migration {
    /// The health door's word: `{"ground", "kernel", "found", "migrated"}`.
    pub fn to_value(&self) -> Value {
        json!({"ground": self.ground, "kernel": self.kernel, "found": self.found, "migrated": self.migrated})
    }

    /// Plain words for the log at light.
    pub fn words(&self) -> String {
        if self.migrated {
            format!(
                "the ground's schema migrated {} → {} by this kernel",
                self.found, self.ground
            )
        } else if self.ground > self.kernel {
            format!(
                "the ground's schema is {} — newer than this kernel's {} — verified, nothing run",
                self.ground, self.kernel
            )
        } else {
            format!(
                "the ground's schema verified at {} — nothing run",
                self.ground
            )
        }
    }
}

static GROUNDS_DONE: OnceLock<Mutex<HashMap<String, HashSet<String>>>> = OnceLock::new();

fn memo() -> &'static Mutex<HashMap<String, HashSet<String>>> {
    GROUNDS_DONE.get_or_init(|| Mutex::new(HashMap::new()))
}

/// A birth finished on this ground: connections born later are born flagged
/// for these tags and run no DDL.
pub fn mark_ground_done<'a>(key: &str, tags: impl IntoIterator<Item = &'a str>) {
    let mut m = memo().lock().unwrap_or_else(|p| p.into_inner());
    m.entry(key.to_string())
        .or_default()
        .extend(tags.into_iter().map(str::to_string));
}

/// Has a birth finished on this ground for this tag (the memo's evidence)?
pub fn born_flagged(key: &str, tag: &str) -> bool {
    memo()
        .lock()
        .unwrap_or_else(|p| p.into_inner())
        .get(key)
        .is_some_and(|tags| tags.contains(tag))
}

/// One connection standing on one ground.
pub struct Ground {
    client: Client,
    dsn: String,
    key: String,
    ensured: HashSet<String>,
}

impl Ground {
    /// Open a connection and learn its ground (DSN + `search_path`).
    pub async fn connect(dsn: &str) -> Result<Ground, RailError> {
        let (client, connection) = tokio_postgres::connect(dsn, NoTls).await?;
        tokio::spawn(async move {
            if let Err(e) = connection.await {
                eprintln!("the ground's connection ended: {e}");
            }
        });
        let path: String = client.query_one("SHOW search_path", &[]).await?.get(0);
        Ok(Ground {
            client,
            dsn: dsn.to_string(),
            key: format!("{dsn}|{path}"),
            ensured: HashSet::new(),
        })
    }

    /// Stand on another schema: a NEW ground (new key, nothing ensured yet).
    pub async fn set_search_path(&mut self, path: &str) -> Result<(), RailError> {
        self.client
            .batch_execute(&format!("SET search_path TO {path}"))
            .await?;
        let path: String = self.client.query_one("SHOW search_path", &[]).await?.get(0);
        self.key = format!("{}|{}", self.dsn, path);
        self.ensured.clear();
        Ok(())
    }

    /// The ground this connection stands on — its DSN and its search_path.
    pub fn key(&self) -> &str {
        &self.key
    }

    pub fn client(&self) -> &Client {
        &self.client
    }

    pub fn client_mut(&mut self) -> &mut Client {
        &mut self.client
    }

    /// The tags this connection has flagged — the law's evidence.
    pub fn ensured(&self) -> &HashSet<String> {
        &self.ensured
    }

    /// True the first time this PROCESS sees `tag` on this ground.
    pub fn once(&mut self, tag: &str) -> bool {
        if !self.ensured.insert(tag.to_string()) {
            return false;
        }
        !born_flagged(&self.key, tag)
    }

    /// Run a module's DDL once per ground per process, inside one transaction
    /// holding the advisory lock. Returns whether the DDL ran on this call.
    pub async fn ensure(&mut self, tag: &str, ddl: &[&str]) -> Result<bool, RailError> {
        if !self.once(tag) {
            return Ok(false);
        }
        let tx = self.client.transaction().await?;
        tx.execute("SELECT pg_advisory_xact_lock($1)", &[&DDL_LOCK])
            .await?;
        for stmt in ddl {
            tx.batch_execute(stmt).await?;
        }
        tx.commit().await?;
        Ok(true)
    }

    /// Every ground this spine knows, ensured at BIRTH — never inside a serve
    /// — through THE MIGRATOR: one locked transaction; the version read; below
    /// this kernel's version every statement runs and the version is recorded
    /// (the single writer); at or past it nothing runs and every declared
    /// table is verified. Then the ground is marked done so later connections
    /// are born flagged.
    pub async fn ensure_all(&mut self) -> Result<Migration, RailError> {
        let every = crate::schema::every_ddl();
        let kernel = crate::schema::SCHEMA_VERSION;
        let tx = self.client.transaction().await?;
        tx.execute("SELECT pg_advisory_xact_lock($1)", &[&DDL_LOCK])
            .await?; // a kernel lighting beside a migrating one WAITS here
        for stmt in crate::schema::SCHEMA_DDL {
            tx.batch_execute(stmt).await?;
        }
        let found: i32 = tx
            .query_one("SELECT coalesce(max(version), 0) FROM spine_schema", &[])
            .await?
            .get(0);
        let migrated = found < kernel;
        if migrated {
            for (_, ddl) in &every {
                for stmt in *ddl {
                    tx.batch_execute(stmt).await?;
                }
            }
            tx.execute(
                "INSERT INTO spine_schema (version, kernel) VALUES ($1, 'rust')",
                &[&kernel],
            )
            .await?;
        } else {
            for table in crate::schema::tables() {
                let stands: bool = tx
                    .query_one("SELECT to_regclass($1) IS NOT NULL", &[&table])
                    .await?
                    .get(0);
                if !stands {
                    return Err(RailError::Refused(format!(
                        "the ground says its schema is version {found} but the table {table} is \
                         missing — a ground that lies is not stood on (drop the spine_schema row \
                         to let a kernel migrate it again, or restore the table)"
                    )));
                }
            }
        }
        tx.commit().await?;
        for (tag, _) in &every {
            self.ensured.insert(tag.to_string());
        }
        mark_ground_done(&self.key, every.iter().map(|(t, _)| *t));
        Ok(Migration {
            found,
            ground: found.max(kernel),
            kernel,
            migrated,
        })
    }
}

/// The tables without a scope that hang off a parent that has one (the reference's
/// `prune.CHILDREN`): `(child, key, parent, parent key)`.
pub const PRUNE_CHILDREN: [(&str, &str, &str, &str); 3] = [
    (
        "spine_intent_turns",
        "intention_id",
        "spine_intentions",
        "intention_id",
    ),
    (
        "spine_occurrences",
        "schedule_id",
        "spine_schedules",
        "schedule_id",
    ),
    ("spine_proof_attempts", "ask_id", "spine_asks", "ask_id"),
];

/// THE GROUND'S PRUNE (the honest glass sp2, 2026-09-29): ONE world's rows, gone — every spine
/// table with a `scope` column (read from the catalogue, so a table born after this line is
/// pruned too) and the three child tables by their parent. A proof calls it for its own world
/// at its end, beside `events::prune_namespace` (found live: 388 test worlds on the dev ground;
/// twenty-three watch rows in dead proof scopes the WATCHES card could never rest). Returns
/// `(table, rows)` for what was touched. The reference's `prune.scope`, law for law.
pub async fn prune_scope(g: &mut Ground, scope: &str) -> Result<Vec<(String, u64)>, RailError> {
    let mut out = Vec::new();
    let tx = g.client.transaction().await?;
    for (child, key, parent, pkey) in PRUNE_CHILDREN {
        let both: bool = tx
            .query_one(
                "SELECT to_regclass($1) IS NOT NULL AND to_regclass($2) IS NOT NULL",
                &[&child, &parent],
            )
            .await?
            .get(0);
        if !both {
            continue;
        }
        let n = tx
            .execute(
                &format!("DELETE FROM {child} WHERE {key} IN (SELECT {pkey} FROM {parent} WHERE scope = $1)"),
                &[&scope],
            )
            .await?;
        if n > 0 {
            out.push((child.to_string(), n));
        }
    }
    let tables: Vec<String> = tx
        .query(
            "SELECT table_name FROM information_schema.columns WHERE table_schema = current_schema() AND \
             column_name = 'scope' AND table_name LIKE 'spine\\_%' ORDER BY 1",
            &[],
        )
        .await?
        .iter()
        .map(|r| r.get::<_, String>(0))
        .collect();
    for t in tables {
        let n = tx
            .execute(&format!("DELETE FROM {t} WHERE scope = $1"), &[&scope])
            .await?;
        if n > 0 {
            out.push((t, n));
        }
    }
    tx.commit().await?;
    Ok(out)
}
