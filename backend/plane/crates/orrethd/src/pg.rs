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
    /// The meaning axis's projection is OPTIONAL (0022 §1: every index is a
    /// rebuildable projection): a pg without the vector extension leaves the
    /// axis dark on the wire — never an error, never a second truth.
    vectors: bool,
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
             );
             CREATE TABLE IF NOT EXISTS purged (
                 node_scope  TEXT NOT NULL,
                 id          TEXT NOT NULL,
                 at          TEXT NOT NULL,
                 reason      TEXT NOT NULL,
                 PRIMARY KEY (node_scope, id)
             );
             CREATE TABLE IF NOT EXISTS meter_archive (
                 node_scope  TEXT NOT NULL,
                 seq         BIGINT NOT NULL,
                 entry       JSONB NOT NULL,
                 PRIMARY KEY (node_scope, seq)
             );
             CREATE TABLE IF NOT EXISTS meter_totals (
                 node_scope  TEXT NOT NULL,
                 subject     TEXT NOT NULL,
                 calls       BIGINT NOT NULL,
                 tokens      BIGINT NOT NULL,
                 usd         DOUBLE PRECISION NOT NULL,
                 PRIMARY KEY (node_scope, subject)
             );",
        )?;
        // 0022 §4 Phase 2 (JB's rule-9 approval 2026-07-17): the vector
        // projection. NULL embedding = "looked, nothing to embed" — the sweep
        // never revisits it. A pg without pgvector leaves `vectors` false.
        let vectors = client
            .batch_execute(
                "CREATE EXTENSION IF NOT EXISTS vector;
                 CREATE TABLE IF NOT EXISTS embeddings (
                     node_scope  TEXT NOT NULL,
                     id          TEXT NOT NULL,
                     embedding   vector(384),
                     PRIMARY KEY (node_scope, id)
                 );
                 CREATE INDEX IF NOT EXISTS embeddings_hnsw
                     ON embeddings USING hnsw (embedding vector_cosine_ops);",
            )
            .map(|_| true)
            .unwrap_or_else(|e| {
                eprintln!("orrethd · the meaning axis stays dark (no pgvector): {e}");
                false
            });
        Ok(Self { client: Mutex::new(client), vectors })
    }

    fn vec_literal(v: &[f32]) -> String {
        let mut s = String::with_capacity(v.len() * 10 + 2);
        s.push('[');
        for (i, x) in v.iter().enumerate() {
            if i > 0 { s.push(','); }
            s.push_str(&format!("{x}"));
        }
        s.push(']');
        s
    }

    /// Store one record's vector — or a NULL marker when there was nothing to
    /// embed (a purged stub, an empty body): the sweep moves on, honestly.
    pub fn save_embedding(&self, node_scope: &str, id: &str, vec: &[f32])
                          -> Result<(), postgres::Error> {
        if !self.vectors { return Ok(()); }
        let mut client = self.client.lock().unwrap();
        if vec.is_empty() {
            client.execute(
                "INSERT INTO embeddings (node_scope, id, embedding)
                 VALUES ($1, $2, NULL) ON CONFLICT (node_scope, id) DO NOTHING",
                &[&node_scope, &id],
            )?;
        } else {
            client.execute(
                &format!(
                    "INSERT INTO embeddings (node_scope, id, embedding)
                     VALUES ($1, $2, '{}'::vector)
                     ON CONFLICT (node_scope, id) DO UPDATE
                         SET embedding = EXCLUDED.embedding",
                    Self::vec_literal(vec)
                ),
                &[&node_scope, &id],
            )?;
        }
        Ok(())
    }

    /// Records this node accepted that the projection has not yet embedded —
    /// the sweep's worklist. Purged stubs are never on it (0026 §1: a purge
    /// that misses the vector index is not a purge; they never enter it).
    pub fn missing_embeddings(&self, node_scope: &str, limit: i64)
                              -> Result<Vec<String>, postgres::Error> {
        if !self.vectors { return Ok(Vec::new()); }
        let rows = self.client.lock().unwrap().query(
            "SELECT r.id FROM records r
             LEFT JOIN embeddings e ON e.node_scope = r.node_scope AND e.id = r.id
             LEFT JOIN purged p     ON p.node_scope = r.node_scope AND p.id = r.id
             WHERE r.node_scope = $1 AND e.id IS NULL AND p.id IS NULL
             ORDER BY r.occurred_at DESC LIMIT $2",
            &[&node_scope, &limit],
        )?;
        Ok(rows.into_iter().map(|r| r.get(0)).collect())
    }

    /// The purge reaches the projection (0026 §1, the stated hard rule): a
    /// shredded record's vector is evicted in the same breath as its bytes.
    pub fn evict_embedding(&self, node_scope: &str, id: &str)
                           -> Result<(), postgres::Error> {
        if !self.vectors { return Ok(()); }
        self.client.lock().unwrap().execute(
            "UPDATE embeddings SET embedding = NULL
             WHERE node_scope = $1 AND id = $2",
            &[&node_scope, &id],
        )?;
        Ok(())
    }

    /// Cosine similarity of the query vector against exactly the given ids —
    /// the meaning rerank runs over the set THE NODE AUTHORIZED, never a
    /// second read path.
    pub fn cosine_for(&self, node_scope: &str, ids: &[String], qv: &[f32])
                      -> Result<Vec<(String, f64)>, postgres::Error> {
        if !self.vectors || ids.is_empty() || qv.is_empty() { return Ok(Vec::new()); }
        let rows = self.client.lock().unwrap().query(
            &format!(
                "SELECT id, 1 - (embedding <=> '{}'::vector) AS sim
                 FROM embeddings
                 WHERE node_scope = $1 AND id = ANY($2) AND embedding IS NOT NULL",
                Self::vec_literal(qv)
            ),
            &[&node_scope, &ids],
        )?;
        Ok(rows.into_iter().map(|r| (r.get(0), r.get(1))).collect())
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

    /// The purge survives the daemon (0026 §1): a restart must never resurrect
    /// readability. The stub row sheds its body pointers in the same breath — the
    /// signed stub remains; the bytes are already gone from the store.
    pub fn save_purged(&self, node_scope: &str, id: &str, at: &str, reason: &str)
                       -> Result<(), postgres::Error> {
        let mut client = self.client.lock().unwrap();
        client.execute(
            "INSERT INTO purged (node_scope, id, at, reason) VALUES ($1, $2, $3, $4)
             ON CONFLICT (node_scope, id) DO NOTHING",
            &[&node_scope, &id, &at, &reason],
        )?;
        client.execute(
            "UPDATE records SET record = (record - 'body') - 'body_ref'
             WHERE node_scope = $1 AND id = $2",
            &[&node_scope, &id],
        )?;
        Ok(())
    }

    /// Exactly this node's purge stubs, for boot-restore.
    pub fn load_purged(&self, node_scope: &str) -> Result<Vec<String>, postgres::Error> {
        let rows = self.client.lock().unwrap().query(
            "SELECT id FROM purged WHERE node_scope = $1",
            &[&node_scope],
        )?;
        Ok(rows.into_iter().map(|r| r.get(0)).collect())
    }

    /// The meter's metabolism (0022 §8): fold entries older than the hot window into
    /// per-subject totals, ARCHIVE the raw — usage history is memory, not vapor
    /// (0019 §4) — and clear them from the hot table so boot-restore stays bounded.
    /// Returns how many entries rotated. 30 days is the v1 dial; the TierProfile owns
    /// it when profiles grow a meter block. Entries without a subject or a timestamp
    /// (lifecycle warnings) stay hot — they are findings, not usage.
    pub fn rotate_meters(&self, node_scope: &str) -> Result<u64, postgres::Error> {
        let mut client = self.client.lock().unwrap();
        let mut tx = client.transaction()?;
        let cutoff = "to_char(now() at time zone 'UTC' - interval '30 days', \
                      'YYYY-MM-DD\"T\"HH24:MI:SS\"Z\"')";
        tx.execute(
            &format!(
                "INSERT INTO meter_totals (node_scope, subject, calls, tokens, usd)
                 SELECT node_scope, entry->>'subject', count(*),
                        COALESCE(sum((entry->>'tokens')::bigint), 0),
                        COALESCE(sum((entry->>'usd')::double precision), 0)
                 FROM meters
                 WHERE node_scope = $1 AND entry->>'subject' IS NOT NULL
                   AND entry->>'at' < {cutoff}
                 GROUP BY node_scope, entry->>'subject'
                 ON CONFLICT (node_scope, subject) DO UPDATE SET
                     calls  = meter_totals.calls  + EXCLUDED.calls,
                     tokens = meter_totals.tokens + EXCLUDED.tokens,
                     usd    = meter_totals.usd    + EXCLUDED.usd"
            ),
            &[&node_scope],
        )?;
        tx.execute(
            &format!(
                "INSERT INTO meter_archive (node_scope, seq, entry)
                 SELECT node_scope, seq, entry FROM meters
                 WHERE node_scope = $1 AND entry->>'subject' IS NOT NULL
                   AND entry->>'at' < {cutoff}
                 ON CONFLICT (node_scope, seq) DO NOTHING"
            ),
            &[&node_scope],
        )?;
        let n = tx.execute(
            &format!(
                "DELETE FROM meters
                 WHERE node_scope = $1 AND entry->>'subject' IS NOT NULL
                   AND entry->>'at' < {cutoff}"
            ),
            &[&node_scope],
        )?;
        tx.commit()?;
        Ok(n)
    }

    /// The folded cold-window totals per subject, for boot-restore seeding.
    pub fn load_meter_totals(
        &self,
        node_scope: &str,
    ) -> Result<Vec<(String, i64, i64, f64)>, postgres::Error> {
        let rows = self.client.lock().unwrap().query(
            "SELECT subject, calls, tokens, usd FROM meter_totals WHERE node_scope = $1",
            &[&node_scope],
        )?;
        Ok(rows
            .into_iter()
            .map(|r| (r.get(0), r.get(1), r.get(2), r.get(3)))
            .collect())
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
