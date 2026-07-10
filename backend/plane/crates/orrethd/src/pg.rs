//! Write-through Postgres persistence for the record store (0000 §2 "Stores").
//!
//! The node stays a pure in-memory structure (the conformance suite stays hermetic);
//! orrethd persists every ACCEPTED record — and every scribe-signed run (0022 §8) —
//! as JSONB and restores records, runs, and the high-water mark at boot: the clock's
//! monotonicity and the diary both survive restarts. Bodies already live in the
//! object store; what's persisted here is the stored form (pointers, not blobs).
//! Indexes serve the persisted log's query families (0022 §2): scoped time-range,
//! tag membership, author forensics, distillation cohorts, lineage walks.

use serde_json::Value;
use std::sync::Mutex;

pub struct PgRecords {
    client: Mutex<postgres::Client>,
}

impl PgRecords {
    pub fn connect(conn: &str) -> Result<Self, postgres::Error> {
        let mut client = postgres::Client::connect(conn, postgres::NoTls)?;
        client.batch_execute(
            "CREATE TABLE IF NOT EXISTS records (
                 node_scope  TEXT NOT NULL,
                 id          TEXT NOT NULL,
                 scope       TEXT NOT NULL,
                 occurred_at TEXT NOT NULL,
                 record      JSONB NOT NULL,
                 PRIMARY KEY (node_scope, id)
             );
             CREATE INDEX IF NOT EXISTS records_node ON records (node_scope);
             CREATE TABLE IF NOT EXISTS meters (
                 node_scope  TEXT NOT NULL,
                 seq         BIGSERIAL,
                 entry       JSONB NOT NULL,
                 PRIMARY KEY (node_scope, seq)
             );
             CREATE TABLE IF NOT EXISTS runs (
                 node_scope  TEXT NOT NULL,
                 id          TEXT NOT NULL,
                 agent       TEXT NOT NULL,
                 occurred_at TEXT NOT NULL,
                 run         JSONB NOT NULL,
                 PRIMARY KEY (node_scope, id)
             );
             CREATE INDEX IF NOT EXISTS runs_scope_agent_time
                 ON runs (node_scope, agent, occurred_at DESC);
             CREATE INDEX IF NOT EXISTS records_scope_time
                 ON records (node_scope, occurred_at DESC);
             CREATE INDEX IF NOT EXISTS records_tags
                 ON records USING GIN ((record->'tags'));
             CREATE INDEX IF NOT EXISTS records_author
                 ON records ((record->>'author'));
             CREATE INDEX IF NOT EXISTS records_distillations
                 ON records ((record->>'kind')) WHERE record->>'kind' = 'distillation';
             CREATE INDEX IF NOT EXISTS records_derived_from
                 ON records USING GIN ((record->'derived_from'));
             CREATE TABLE IF NOT EXISTS requests (
                 node_scope  TEXT NOT NULL,
                 seq         BIGINT NOT NULL,
                 id          TEXT NOT NULL,
                 request     JSONB NOT NULL,
                 PRIMARY KEY (node_scope, id)
             );",
        )?;
        Ok(Self { client: Mutex::new(client) })
    }

    /// Persist the STORED form of an accepted record, keyed by the ACCEPTING node —
    /// in a shared database the tree's daemons each restore only what they accepted
    /// (a record may legitimately live at several tiers: the push-up). Idempotent.
    pub fn save(&self, node_scope: &str, record: &Value) -> Result<(), postgres::Error> {
        self.client.lock().unwrap().execute(
            "INSERT INTO records (node_scope, id, scope, occurred_at, record)
             VALUES ($1, $2, $3, $4, $5) ON CONFLICT (node_scope, id) DO NOTHING",
            &[
                &node_scope,
                &record["id"].as_str().unwrap(),
                &record["scope"].as_str().unwrap(),
                &record["occurred_at"].as_str().unwrap(),
                &postgres::types::Json(record),
            ],
        )?;
        Ok(())
    }

    /// Persist a scribe-signed RunRecord — the diary survives the daemon (0022 §8:
    /// presence stats and rollup continuity no longer reset with the process). Idempotent.
    pub fn save_run(&self, node_scope: &str, run: &Value) -> Result<(), postgres::Error> {
        self.client.lock().unwrap().execute(
            "INSERT INTO runs (node_scope, id, agent, occurred_at, run)
             VALUES ($1, $2, $3, $4, $5) ON CONFLICT (node_scope, id) DO NOTHING",
            &[
                &node_scope,
                &run["id"].as_str().unwrap(),
                &run["agent"].as_str().unwrap_or(""),
                &run["occurred_at"].as_str().unwrap_or(""),
                &postgres::types::Json(run),
            ],
        )?;
        Ok(())
    }

    /// Exactly this node's runs, for boot-restore.
    pub fn load_runs(&self, node_scope: &str) -> Result<Vec<Value>, postgres::Error> {
        let rows = self.client.lock().unwrap().query(
            "SELECT run FROM runs WHERE node_scope = $1 ORDER BY occurred_at",
            &[&node_scope],
        )?;
        Ok(rows
            .into_iter()
            .map(|r| r.get::<_, postgres::types::Json<Value>>(0).0)
            .collect())
    }

    /// Persist one model-meter entry — usage history is memory, not vapor (0019 §4).
    pub fn save_meter(&self, node_scope: &str, entry: &Value) -> Result<(), postgres::Error> {
        self.client.lock().unwrap().execute(
            "INSERT INTO meters (node_scope, entry) VALUES ($1, $2)",
            &[&node_scope, &postgres::types::Json(entry)],
        )?;
        Ok(())
    }

    /// This node's meter history, for boot-restore.
    pub fn load_meters(&self, node_scope: &str) -> Result<Vec<Value>, postgres::Error> {
        let rows = self.client.lock().unwrap().query(
            "SELECT entry FROM meters WHERE node_scope = $1 ORDER BY seq",
            &[&node_scope],
        )?;
        Ok(rows
            .into_iter()
            .map(|r| r.get::<_, postgres::types::Json<Value>>(0).0)
            .collect())
    }

    /// Persist one queue entry (0022 §8) — the HITL queue survives the daemon: a staged
    /// escalation, a granted lease, an agent's name must not vanish in a crash. Requests
    /// MUTATE (pending → … → done), so this upserts; `seq` pins the queue order at first
    /// insert and never changes after.
    pub fn save_request(&self, node_scope: &str, seq: i64, request: &Value) -> Result<(), postgres::Error> {
        self.client.lock().unwrap().execute(
            "INSERT INTO requests (node_scope, seq, id, request)
             VALUES ($1, $2, $3, $4)
             ON CONFLICT (node_scope, id) DO UPDATE SET request = EXCLUDED.request",
            &[
                &node_scope,
                &seq,
                &request["id"].as_str().unwrap(),
                &postgres::types::Json(request),
            ],
        )?;
        Ok(())
    }

    /// Exactly this node's queue, in submission order, for boot-restore.
    pub fn load_requests(&self, node_scope: &str) -> Result<Vec<Value>, postgres::Error> {
        let rows = self.client.lock().unwrap().query(
            "SELECT request FROM requests WHERE node_scope = $1 ORDER BY seq",
            &[&node_scope],
        )?;
        Ok(rows
            .into_iter()
            .map(|r| r.get::<_, postgres::types::Json<Value>>(0).0)
            .collect())
    }

    /// Exactly this node's records, for boot-restore.
    pub fn load(&self, node_scope: &str) -> Result<Vec<Value>, postgres::Error> {
        let rows = self.client.lock().unwrap().query(
            "SELECT record FROM records WHERE node_scope = $1 ORDER BY occurred_at",
            &[&node_scope],
        )?;
        Ok(rows
            .into_iter()
            .map(|r| r.get::<_, postgres::types::Json<Value>>(0).0)
            .collect())
    }
}
