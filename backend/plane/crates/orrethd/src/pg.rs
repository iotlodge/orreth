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
                 id          TEXT PRIMARY KEY,
                 scope       TEXT NOT NULL,
                 occurred_at TEXT NOT NULL,
                 record      JSONB NOT NULL
             );
             CREATE INDEX IF NOT EXISTS records_scope ON records (scope);",
        )?;
        Ok(Self { client: Mutex::new(client) })
    }

    /// Persist the STORED form of an accepted record (post-ingress: body_ref, keep_class,
    /// received_at all present). Idempotent — content-addressed ids make replays harmless.
    pub fn save(&self, record: &Value) -> Result<(), postgres::Error> {
        self.client.lock().unwrap().execute(
            "INSERT INTO records (id, scope, occurred_at, record)
             VALUES ($1, $2, $3, $4) ON CONFLICT (id) DO NOTHING",
            &[
                &record["id"].as_str().unwrap(),
                &record["scope"].as_str().unwrap(),
                &record["occurred_at"].as_str().unwrap(),
                &postgres::types::Json(record),
            ],
        )?;
        Ok(())
    }

    /// Everything at-or-below this scope, for boot-restore.
    pub fn load(&self, scope: &str) -> Result<Vec<Value>, postgres::Error> {
        let rows = self.client.lock().unwrap().query(
            "SELECT record FROM records
             WHERE scope = $1 OR scope LIKE $2
             ORDER BY occurred_at",
            &[&scope, &format!("{scope}/%")],
        )?;
        Ok(rows
            .into_iter()
            .map(|r| r.get::<_, postgres::types::Json<Value>>(0).0)
            .collect())
    }
}
