//! Write-through Postgres persistence for the record store (0000 §2 "Stores").
//!
//! The node stays a pure in-memory structure (the conformance suite stays hermetic);
//! orrethd persists every ACCEPTED record as JSONB and restores records + the
//! high-water mark at boot — the clock's monotonicity survives restarts. Bodies
//! already live in the object store; what's persisted here is the stored form
//! (pointers, not blobs).

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
