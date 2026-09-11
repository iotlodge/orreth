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
             );
             -- 0065 sp3 (L2's rule-9 gate): the graph projection — Shape A,
             -- finally in Postgres. Terms as nodes, within-span co-occurrence
             -- as edges, EVERY edge carrying its witness (record + span + the
             -- piece's hash): the citation IS the edge's provenance. Pure SQL
             -- — the graph stands even where the meaning axis is dark.
             CREATE TABLE IF NOT EXISTS graph_nodes (
                 node_scope  TEXT NOT NULL,
                 record_id   TEXT NOT NULL,
                 name        TEXT NOT NULL,
                 cnt         INT NOT NULL DEFAULT 0,
                 law         TEXT NOT NULL,
                 PRIMARY KEY (node_scope, record_id, name)
             );
             CREATE INDEX IF NOT EXISTS graph_nodes_name
                 ON graph_nodes (node_scope, name);
             CREATE TABLE IF NOT EXISTS graph_edges (
                 node_scope  TEXT NOT NULL,
                 record_id   TEXT NOT NULL,
                 a           TEXT NOT NULL,
                 b           TEXT NOT NULL,
                 seq         INT NOT NULL,
                 span_start  INT NOT NULL,
                 span_end    INT NOT NULL,
                 lane        TEXT NOT NULL,
                 doc         TEXT NOT NULL DEFAULT '',
                 trust       DOUBLE PRECISION NOT NULL DEFAULT 1.0,
                 hash        TEXT NOT NULL DEFAULT '',
                 law         TEXT NOT NULL,
                 PRIMARY KEY (node_scope, record_id, a, b, seq)
             );
             CREATE INDEX IF NOT EXISTS graph_edges_a
                 ON graph_edges (node_scope, a);
             CREATE INDEX IF NOT EXISTS graph_edges_b
                 ON graph_edges (node_scope, b);
             -- 0068 sp2: the ResolvedContext's durable referent — every
             -- composed law this node ever served under, by id
             CREATE TABLE IF NOT EXISTS resolved_contexts (
                 node_scope  TEXT NOT NULL,
                 id          TEXT NOT NULL,
                 context     JSONB NOT NULL,
                 at          TEXT NOT NULL DEFAULT '',
                 PRIMARY KEY (node_scope, id)
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
                     model       TEXT NOT NULL DEFAULT '',
                     PRIMARY KEY (node_scope, id)
                 );
                 ALTER TABLE embeddings
                     ADD COLUMN IF NOT EXISTS model TEXT NOT NULL DEFAULT '';
                 CREATE INDEX IF NOT EXISTS embeddings_hnsw
                     ON embeddings USING hnsw (embedding vector_cosine_ops);
                 -- 0065 sp2 (L2's rule-9 gate, JB 2026-09-06): the standing
                 -- chunk/tree projection — POINTERS into derived text, never
                 -- blobs; level 0 = leaf chunks, level >= 1 = tree parents;
                 -- every row wears the policy that cut it
                 CREATE TABLE IF NOT EXISTS chunks (
                     node_scope  TEXT NOT NULL,
                     record_id   TEXT NOT NULL,
                     level       INT NOT NULL DEFAULT 0,
                     seq         INT NOT NULL,
                     span_start  INT NOT NULL,
                     span_end    INT NOT NULL,
                     lane        TEXT NOT NULL,
                     hash        TEXT NOT NULL DEFAULT '',
                     policy      TEXT NOT NULL,
                     doc         TEXT NOT NULL DEFAULT '',
                     trust       DOUBLE PRECISION NOT NULL DEFAULT 1.0,
                     occurred    TEXT NOT NULL DEFAULT '',
                     embedding   vector(384),
                     PRIMARY KEY (node_scope, record_id, level, seq)
                 );
                 CREATE INDEX IF NOT EXISTS chunks_record
                     ON chunks (node_scope, record_id);
                 CREATE INDEX IF NOT EXISTS chunks_hnsw
                     ON chunks USING hnsw (embedding vector_cosine_ops);",
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
    pub fn save_embedding(&self, node_scope: &str, id: &str, vec: &[f32],
                          model: &str)
                          -> Result<(), postgres::Error> {
        // 0069 sp5 — every vector wears the MODEL that made it: a model
        // swap makes old rows visibly stale, and the sweep re-embeds them
        // at its own pace — loud, resumable, never silent
        if !self.vectors { return Ok(()); }
        let mut client = self.client.lock().unwrap();
        if vec.is_empty() {
            client.execute(
                "INSERT INTO embeddings (node_scope, id, embedding, model)
                 VALUES ($1, $2, NULL, $3)
                 ON CONFLICT (node_scope, id) DO UPDATE SET model = $3",
                &[&node_scope, &id, &model],
            )?;
        } else {
            client.execute(
                &format!(
                    "INSERT INTO embeddings (node_scope, id, embedding, model)
                     VALUES ($1, $2, '{}'::vector, $3)
                     ON CONFLICT (node_scope, id) DO UPDATE
                         SET embedding = EXCLUDED.embedding,
                             model = EXCLUDED.model",
                    Self::vec_literal(vec)
                ),
                &[&node_scope, &id, &model],
            )?;
        }
        Ok(())
    }

    /// Records this node accepted that the projection has not yet embedded —
    /// the sweep's worklist. Purged stubs are never on it (0026 §1: a purge
    /// that misses the vector index is not a purge; they never enter it).
    pub fn missing_embeddings(&self, node_scope: &str, limit: i64,
                              model: &str)
                              -> Result<Vec<String>, postgres::Error> {
        // absent rows AND wrong-model rows are BOTH the sweep's work — the
        // survey's exact wound (0069 §2.4): «the sweep only finds absent
        // rows, not wrong-model rows» — paid here
        if !self.vectors { return Ok(Vec::new()); }
        let rows = self.client.lock().unwrap().query(
            "SELECT r.id FROM records r
             LEFT JOIN embeddings e ON e.node_scope = r.node_scope AND e.id = r.id
             LEFT JOIN purged p     ON p.node_scope = r.node_scope AND p.id = r.id
             WHERE r.node_scope = $1 AND p.id IS NULL
               AND (e.id IS NULL OR e.model <> $3)
             ORDER BY r.occurred_at DESC LIMIT $2",
            &[&node_scope, &limit, &model],
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

    /// 0065 sp2 — one record, one policy, one truth: landing a record's rows
    /// replaces every row it had, whatever policy the old ones wore. Tree
    /// parents (level >= 1) ride the same door, vectorless.
    pub fn save_chunks(&self, node_scope: &str, record_id: &str, policy: &str,
                       rows: &[Value]) -> Result<(), postgres::Error> {
        if !self.vectors { return Ok(()); }
        let mut client = self.client.lock().unwrap();
        client.execute(
            "DELETE FROM chunks WHERE node_scope = $1 AND record_id = $2",
            &[&node_scope, &record_id],
        )?;
        for r in rows {
            let span = r["span"].as_array().cloned().unwrap_or_default();
            let (s, e) = (span.first().and_then(|v| v.as_i64()).unwrap_or(0) as i32,
                          span.get(1).and_then(|v| v.as_i64()).unwrap_or(0) as i32);
            let level = r["level"].as_i64().unwrap_or(0) as i32;
            let seq = r["seq"].as_i64().unwrap_or(0) as i32;
            let lane = r["lane"].as_str().unwrap_or("document");
            let hash = r["hash"].as_str().unwrap_or("");
            let doc = r["doc"].as_str().unwrap_or("");
            let trust = r["trust"].as_f64().unwrap_or(1.0);
            let occurred = r["occurred"].as_str().unwrap_or("");
            let vec: Vec<f32> = r["vector"].as_array().map(|a| {
                a.iter().filter_map(|x| x.as_f64().map(|f| f as f32)).collect()
            }).unwrap_or_default();
            if vec.is_empty() {
                client.execute(
                    "INSERT INTO chunks (node_scope, record_id, level, seq,
                         span_start, span_end, lane, hash, policy, doc, trust,
                         occurred, embedding)
                     VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,NULL)",
                    &[&node_scope, &record_id, &level, &seq, &s, &e, &lane,
                      &hash, &policy, &doc, &trust, &occurred],
                )?;
            } else {
                client.execute(
                    &format!(
                        "INSERT INTO chunks (node_scope, record_id, level, seq,
                             span_start, span_end, lane, hash, policy, doc,
                             trust, occurred, embedding)
                         VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,
                                 '{}'::vector)",
                        Self::vec_literal(&vec)
                    ),
                    &[&node_scope, &record_id, &level, &seq, &s, &e, &lane,
                      &hash, &policy, &doc, &trust, &occurred],
                )?;
            }
        }
        Ok(())
    }

    /// The chunk sweep's worklist: living records with no leaf rows under the
    /// CURRENT policy — the uncut and the policy-stale alike; purged stubs
    /// never appear (a purge that misses the projection is not a purge).
    pub fn missing_chunks(&self, node_scope: &str, policy: &str,
                          ids: &[String], limit: i64)
                          -> Result<Vec<String>, postgres::Error> {
        if !self.vectors { return Ok(Vec::new()); }
        // ids given → answer only for THAT set (the caller's own authorized
        // pull — the sweep may never judge records it cannot see); empty →
        // the whole log, material first
        let sql = if ids.is_empty() {
            "SELECT r.id FROM records r
             LEFT JOIN chunks c ON c.node_scope = r.node_scope
                               AND c.record_id = r.id AND c.level = 0
                               AND c.policy = $2
             LEFT JOIN purged p ON p.node_scope = r.node_scope AND p.id = r.id
             WHERE r.node_scope = $1 AND c.record_id IS NULL AND p.id IS NULL
             ORDER BY (CASE WHEN r.record->'tags' ? 'stacks'
                              OR r.record->'tags' ? 'knowledge'
                            THEN 0 ELSE 1 END),
                      r.occurred_at DESC LIMIT $3"
        } else {
            "SELECT r.id FROM records r
             LEFT JOIN chunks c ON c.node_scope = r.node_scope
                               AND c.record_id = r.id AND c.level = 0
                               AND c.policy = $2
             LEFT JOIN purged p ON p.node_scope = r.node_scope AND p.id = r.id
             WHERE r.node_scope = $1 AND r.id = ANY($4)
               AND c.record_id IS NULL AND p.id IS NULL
             ORDER BY (CASE WHEN r.record->'tags' ? 'stacks'
                              OR r.record->'tags' ? 'knowledge'
                            THEN 0 ELSE 1 END),
                      r.occurred_at DESC LIMIT $3"
        };
        let rows = if ids.is_empty() {
            self.client.lock().unwrap().query(sql, &[&node_scope, &policy, &limit])?
        } else {
            self.client.lock().unwrap().query(sql, &[&node_scope, &policy, &limit, &ids])?
        };
        Ok(rows.into_iter().map(|r| r.get(0)).collect())
    }

    /// The purge reaches the standing projection: a shredded record's chunk
    /// rows and tree nodes are DELETED in the same breath as its bytes.
    pub fn evict_chunks(&self, node_scope: &str, id: &str)
                        -> Result<(), postgres::Error> {
        if !self.vectors { return Ok(()); }
        self.client.lock().unwrap().execute(
            "DELETE FROM chunks WHERE node_scope = $1 AND record_id = $2",
            &[&node_scope, &id],
        )?;
        Ok(())
    }

    /// Chunk-grain cosine against exactly the given ids — the standing
    /// projection's read, over the set THE NODE AUTHORIZED, never a second
    /// read path (cosine_for's law at chunk grain).
    pub fn chunk_search(&self, node_scope: &str, ids: &[String], qv: &[f32],
                        k: i64)
                        -> Result<Vec<(String, i32, i32, i32, String, String,
                                       f64, String, String, f64)>, postgres::Error> {
        if !self.vectors || ids.is_empty() || qv.is_empty() { return Ok(Vec::new()); }
        let rows = self.client.lock().unwrap().query(
            &format!(
                "SELECT record_id, seq, span_start, span_end, lane, doc,
                        trust, occurred, hash,
                        1 - (embedding <=> '{lit}'::vector) AS sim
                 FROM chunks
                 WHERE node_scope = $1 AND record_id = ANY($2)
                   AND level = 0 AND embedding IS NOT NULL
                 ORDER BY embedding <=> '{lit}'::vector LIMIT $3",
                lit = Self::vec_literal(qv)
            ),
            &[&node_scope, &ids, &k],
        )?;
        Ok(rows.into_iter().map(|r| (r.get(0), r.get(1), r.get(2), r.get(3),
                                     r.get(4), r.get(5), r.get(6), r.get(7),
                                     r.get(8), r.get(9))).collect())
    }

    /// 0065 sp3 — one record, one law, one truth: landing a record's graph
    /// rows replaces every row it had in both tables. Empty nodes land a
    /// marker mention (name '') so the worklist stops listing a record this
    /// floor looked at and found non-material.
    pub fn save_graph(&self, node_scope: &str, record_id: &str, law: &str,
                      nodes: &[Value], edges: &[Value])
                      -> Result<(), postgres::Error> {
        let mut client = self.client.lock().unwrap();
        client.execute(
            "DELETE FROM graph_nodes WHERE node_scope = $1 AND record_id = $2",
            &[&node_scope, &record_id])?;
        client.execute(
            "DELETE FROM graph_edges WHERE node_scope = $1 AND record_id = $2",
            &[&node_scope, &record_id])?;
        if nodes.is_empty() {
            client.execute(
                "INSERT INTO graph_nodes (node_scope, record_id, name, cnt, law)
                 VALUES ($1, $2, '', 0, $3)",
                &[&node_scope, &record_id, &law])?;
        }
        for n in nodes {
            let name = n["name"].as_str().unwrap_or("");
            let cnt = n["cnt"].as_i64().unwrap_or(0) as i32;
            if name.is_empty() { continue; }
            client.execute(
                "INSERT INTO graph_nodes (node_scope, record_id, name, cnt, law)
                 VALUES ($1, $2, $3, $4, $5) ON CONFLICT DO NOTHING",
                &[&node_scope, &record_id, &name, &cnt, &law])?;
        }
        for e in edges {
            let span = e["span"].as_array().cloned().unwrap_or_default();
            let (s0, e0) = (span.first().and_then(|v| v.as_i64()).unwrap_or(0) as i32,
                            span.get(1).and_then(|v| v.as_i64()).unwrap_or(0) as i32);
            client.execute(
                "INSERT INTO graph_edges (node_scope, record_id, a, b, seq,
                     span_start, span_end, lane, doc, trust, hash, law)
                 VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12)
                 ON CONFLICT DO NOTHING",
                &[&node_scope, &record_id,
                  &e["a"].as_str().unwrap_or(""), &e["b"].as_str().unwrap_or(""),
                  &(e["seq"].as_i64().unwrap_or(0) as i32), &s0, &e0,
                  &e["lane"].as_str().unwrap_or("document"),
                  &e["doc"].as_str().unwrap_or(""),
                  &e["trust"].as_f64().unwrap_or(1.0),
                  &e["hash"].as_str().unwrap_or(""), &law])?;
        }
        Ok(())
    }

    /// The extraction sweep's worklist — answering ONLY for the ids the
    /// caller sends (sp2's live lesson, baked in from birth here): living
    /// records among them with no graph rows under the current law.
    pub fn missing_graph(&self, node_scope: &str, law: &str, ids: &[String],
                         limit: i64) -> Result<Vec<String>, postgres::Error> {
        if ids.is_empty() { return Ok(Vec::new()); }
        let rows = self.client.lock().unwrap().query(
            "SELECT r.id FROM records r
             LEFT JOIN purged p ON p.node_scope = r.node_scope AND p.id = r.id
             WHERE r.node_scope = $1 AND r.id = ANY($3) AND p.id IS NULL
               AND NOT EXISTS (SELECT 1 FROM graph_nodes gn
                               WHERE gn.node_scope = r.node_scope
                                 AND gn.record_id = r.id AND gn.law = $2)
             ORDER BY (CASE WHEN r.record->'tags' ? 'stacks'
                              OR r.record->'tags' ? 'knowledge'
                            THEN 0 ELSE 1 END),
                      r.occurred_at DESC LIMIT $4",
            &[&node_scope, &law, &ids, &limit],
        )?;
        Ok(rows.into_iter().map(|r| r.get(0)).collect())
    }

    /// The purge reaches the graph: a shredded record's edges AND its node
    /// mentions die in the same breath — what only that record knew is
    /// forgotten with it.
    pub fn evict_graph(&self, node_scope: &str, id: &str)
                       -> Result<(), postgres::Error> {
        let mut client = self.client.lock().unwrap();
        client.execute(
            "DELETE FROM graph_nodes WHERE node_scope = $1 AND record_id = $2",
            &[&node_scope, &id])?;
        client.execute(
            "DELETE FROM graph_edges WHERE node_scope = $1 AND record_id = $2",
            &[&node_scope, &id])?;
        Ok(())
    }

    /// The walking read, inside the authorized set ONLY: witnesses binding
    /// two of the ask's terms, scored by pairs bound; a one-term ask falls
    /// to the edges touching that term, dampened. Never a second read path.
    pub fn graph_walk(&self, node_scope: &str, ids: &[String],
                      terms: &[String], k: i64)
                      -> Result<Vec<(String, i32, i32, i32, String, String,
                                     f64, String, f64, String)>, postgres::Error> {
        if ids.is_empty() || terms.is_empty() { return Ok(Vec::new()); }
        let mut client = self.client.lock().unwrap();
        let rows = client.query(
            "SELECT record_id, seq, span_start, span_end, lane, doc,
                    MAX(trust) AS trust, MAX(hash) AS hash,
                    COUNT(*)::float8 AS score,
                    string_agg(a || '↔' || b, ' · ') AS pairs
             FROM graph_edges
             WHERE node_scope = $1 AND record_id = ANY($2)
               AND a = ANY($3) AND b = ANY($3)
             GROUP BY record_id, seq, span_start, span_end, lane, doc
             ORDER BY score DESC LIMIT $4",
            &[&node_scope, &ids, &terms, &k],
        )?;
        if !rows.is_empty() || terms.len() != 1 {
            return Ok(rows.into_iter().map(|r| (r.get(0), r.get(1), r.get(2),
                                                r.get(3), r.get(4), r.get(5),
                                                r.get(6), r.get(7), r.get(8),
                                                r.get(9))).collect());
        }
        let rows = client.query(
            "SELECT record_id, seq, span_start, span_end, lane, doc,
                    MAX(trust) AS trust, MAX(hash) AS hash,
                    0.5::float8 AS score,
                    MIN(a || '↔' || b) AS pairs
             FROM graph_edges
             WHERE node_scope = $1 AND record_id = ANY($2)
               AND (a = $3 OR b = $3)
             GROUP BY record_id, seq, span_start, span_end, lane, doc
             LIMIT $4",
            &[&node_scope, &ids, &terms[0], &k],
        )?;
        Ok(rows.into_iter().map(|r| (r.get(0), r.get(1), r.get(2), r.get(3),
                                     r.get(4), r.get(5), r.get(6), r.get(7),
                                     r.get(8), r.get(9))).collect())
    }

    /// 0068 sp2 — the ResolvedContext persists: the id a thought will pin
    /// has a durable referent, never just a hash in the air.
    pub fn save_context(&self, node_scope: &str, id: &str, context: &Value,
                        at: &str) -> Result<(), postgres::Error> {
        self.client.lock().unwrap().execute(
            "INSERT INTO resolved_contexts (node_scope, id, context, at)
             VALUES ($1, $2, $3, $4) ON CONFLICT (node_scope, id) DO NOTHING",
            &[&node_scope, &id, context, &at],
        )?;
        Ok(())
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
