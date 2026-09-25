// PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp2, the ground and the rails · 2026-09-22
// Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp4, the loops' three tags · 2026-09-23
// Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp3, the ask road: the road's six tags at birth · 2026-09-22
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

use crate::rail_error::RailError;
use std::collections::{HashMap, HashSet};
use std::sync::{Mutex, OnceLock};
use tokio_postgres::{Client, NoTls};

/// The DDL race guard — `pg_advisory_xact_lock(742199)`, as Python takes it.
pub const DDL_LOCK: i64 = 742199;

/// The tags this spine ensures at birth (the Python spine ensures more —
/// its `ground.TAGS`; the Rust spine grows its list spoonful by spoonful —
/// sp3 added the ask road's six, sp4 the loops' three).
pub const TAGS: [&str; 16] = [
    "outbox",
    "inbox",
    "heartbeat",
    "resident",
    "markers",
    "proof",
    "intent",
    "presence",
    "digest",
    "store",
    "monitor",
    "scheduler",
    "harness",
    "services",
    "stable",
    "gateway",
];

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
    /// — then the ground marked done so later connections are born flagged.
    pub async fn ensure_all(&mut self) -> Result<(), RailError> {
        crate::outbox::ensure_schema(self).await?;
        crate::inbox::ensure_schema(self).await?;
        crate::heartbeat::ensure_schema(self).await?;
        crate::schema::ensure_road(self).await?;
        mark_ground_done(&self.key, TAGS);
        Ok(())
    }
}
