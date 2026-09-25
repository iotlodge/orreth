// PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp5, memory and the export · 2026-09-24
//! The Record on the ground — `orreth_spine.store.OrrethStore` ported
//! (canon 0003 · MEM-1..MEM-6): `spine_memories` with its intervals and
//! its projection (tsvector, English), the SIBLING LAW (the same words land
//! nothing; different words become a sibling that supersedes the current
//! one — never an overwrite), verbatim reads now or as of a time, the
//! lineage, stemmed and RANKED search with the word-match fallback, the
//! window, the recent, and the governed purge with its tombstone — every
//! fact through the outbox in the same transaction, the same SQL as the
//! reference so both kernels read one Record.

use crate::envelope::{self, Mint};
use crate::ground::Ground;
use crate::hash::content_hash;
use crate::memory::{
    fallback_words, landed_payload, purge_payload, search_terms, MEMORY_EVENT, PURGE_EVENT,
};
use crate::outbox;
use crate::world::{iso_opt, isoformat, RoadError};
use serde_json::{json, Value};
use std::time::SystemTime;

/// `store.ensure_schema` — the same DDL as the Python spine (a fresh ground;
/// the old-ground migration the reference carries is a no-op here).
pub const STORE_DDL: &[&str] = &[
    "CREATE TABLE IF NOT EXISTS spine_memories ( memory_id bigserial PRIMARY KEY, namespace text NOT \
     NULL, key text NOT NULL, body text NOT NULL, hash text NOT NULL, by_did text NOT NULL, scope \
     text, landed_at timestamptz NOT NULL DEFAULT now(), valid_from timestamptz NOT NULL DEFAULT \
     now(), valid_to timestamptz, supersedes text, understanding text NOT NULL DEFAULT \
     'tsvector:english', tsv tsvector GENERATED ALWAYS AS (to_tsvector('english', body)) STORED)",
    "CREATE UNIQUE INDEX IF NOT EXISTS spine_memories_id ON spine_memories (memory_id)",
    "CREATE UNIQUE INDEX IF NOT EXISTS spine_memories_current ON spine_memories (namespace, key, \
     scope) WHERE valid_to IS NULL",
    "CREATE INDEX IF NOT EXISTS spine_memories_tsv ON spine_memories USING GIN (tsv)",
    // the column added only when missing: an ALTER takes an AccessExclusive lock even when it
    // has nothing to add, and a kernel booting beside another's inserts deadlocked on it
    // (found by the memory proof, 2026-09-24)
    "DO $$ BEGIN IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = \
     'spine_memories' AND column_name = 'state') THEN ALTER TABLE spine_memories ADD COLUMN state \
     text NOT NULL DEFAULT 'in'; END IF; END $$",
    "CREATE INDEX IF NOT EXISTS spine_memories_landed ON spine_memories (namespace, scope, landed_at)",
];

const VALID_NOW: &str = "valid_to IS NULL";

/// An ISO time from the door, cast on the ground (`$n::timestamptz`) — the
/// reference hands psycopg the text and lets Postgres read it; a text the
/// ground cannot read refuses as a rail's word.
fn at_ts(at: &str) -> Result<String, RoadError> {
    if at.trim().is_empty() {
        return Err(crate::world::refused("the time is one ISO time"));
    }
    Ok(at.trim().to_string())
}

/// Land a memory with its event (the sibling law). Returns the content hash.
pub async fn put(
    g: &mut Ground,
    scope: &str,
    by_did: &str,
    state: &str,
    namespace: &str,
    key: &str,
    body: &str,
) -> Result<String, RoadError> {
    let h = content_hash(&Value::String(body.into()));
    let tx = g.client_mut().transaction().await?;
    let prev = tx
        .query_opt(
            "SELECT memory_id, hash FROM spine_memories WHERE namespace = $1 AND key = $2 AND scope = \
             $3 AND valid_to IS NULL FOR UPDATE",
            &[&namespace, &key, &scope],
        )
        .await?;
    let prev: Option<(i64, String)> = prev.map(|r| (r.get(0), r.get(1)));
    if let Some((_, ph)) = &prev {
        if *ph == h {
            tx.commit().await?;
            return Ok(h); // the same words: nothing new
        }
    }
    let payload = landed_payload(namespace, key, &h, prev.as_ref().map(|p| p.1.as_str()));
    if let Some((id, _)) = &prev {
        tx.execute(
            "UPDATE spine_memories SET valid_to = now() WHERE memory_id = $1",
            &[id],
        )
        .await?;
    }
    let e = Mint {
        kind: "event".into(),
        r#type: MEMORY_EVENT.into(),
        universe_id: scope.into(),
        scope_path: scope.into(),
        payload,
        correlation_id: None,
        authority_chain: Some(vec![by_did.to_string()]),
        aggregate: None,
        marker: None,
    }
    .mint()?;
    tx.execute(
        "INSERT INTO spine_memories (namespace, key, body, hash, by_did, scope, supersedes, state) \
         VALUES ($1, $2, $3, $4, $5, $6, $7, $8)",
        &[&namespace, &key, &body, &h, &by_did, &scope, &prev.as_ref().map(|p| p.1.clone()), &state],
    )
    .await?;
    let raw = envelope::encode(&e)?;
    outbox::add_row(&tx, &raw, e["message_id"].as_str().unwrap_or_default()).await?;
    tx.commit().await?;
    Ok(h)
}

/// Verbatim by key — what is true now, or what was true at `at`.
pub async fn get(
    g: &Ground,
    scope: &str,
    state: &str,
    namespace: &str,
    key: &str,
    at: Option<&str>,
) -> Result<Option<String>, RoadError> {
    let row = match at {
        None => g
            .client()
            .query_opt(
                "SELECT body FROM spine_memories WHERE namespace = $1 AND key = $2 AND scope = $3 \
                     AND valid_to IS NULL AND state = $4",
                &[&namespace, &key, &scope, &state],
            )
            .await?,
        Some(at) => {
            let t = at_ts(at)?;
            g.client()
                .query_opt(
                    "SELECT body FROM spine_memories WHERE namespace = $1 AND key = $2 AND scope = $3 \
                     AND valid_from <= $4::timestamptz AND (valid_to IS NULL OR valid_to > $4::timestamptz) AND state = $5 \
                     ORDER BY valid_from DESC LIMIT 1",
                    &[&namespace, &key, &scope, &t, &state],
                )
                .await?
        }
    };
    Ok(row.map(|r| r.get(0)))
}

/// Every version, oldest first — the lineage, never an overwrite.
pub async fn history(
    g: &Ground,
    scope: &str,
    namespace: &str,
    key: &str,
) -> Result<Vec<Value>, RoadError> {
    let rows = g
        .client()
        .query(
            "SELECT hash, body, valid_from, valid_to, supersedes, understanding FROM spine_memories \
             WHERE namespace = $1 AND key = $2 AND scope = $3 ORDER BY valid_from",
            &[&namespace, &key, &scope],
        )
        .await?;
    Ok(rows
        .iter()
        .map(|r| {
            json!({
                "hash": r.get::<_, String>(0), "body": r.get::<_, String>(1),
                "valid_from": isoformat(r.get::<_, SystemTime>(2)),
                "valid_to": iso_opt(r.get::<_, Option<SystemTime>>(3)),
                "supersedes": r.get::<_, Option<String>>(4), "understanding": r.get::<_, String>(5),
            })
        })
        .collect())
}

/// Understanding v0: full-text, stemmed, RANKED; the rows valid now or at
/// `at`; the word-match fallback when the projection holds nothing of the query.
pub async fn search(
    g: &Ground,
    scope: &str,
    state: &str,
    namespace: &str,
    query: &str,
    limit: i64,
    at: Option<&str>,
) -> Result<Vec<Value>, RoadError> {
    let terms = search_terms(query);
    let rows = match at {
        None => {
            g.client()
                .query(
                    "SELECT key, body, ts_rank(tsv, q) AS rank FROM spine_memories, \
                     websearch_to_tsquery('english', $1) q WHERE namespace = $2 AND scope = $3 AND \
                     valid_to IS NULL AND state = $4 AND tsv @@ q ORDER BY rank DESC, landed_at DESC \
                     LIMIT $5",
                    &[&terms, &namespace, &scope, &state, &limit],
                )
                .await?
        }
        Some(at) => {
            let t = at_ts(at)?;
            g.client()
                .query(
                    "SELECT key, body, ts_rank(tsv, q) AS rank FROM spine_memories, \
                     websearch_to_tsquery('english', $1) q WHERE namespace = $2 AND scope = $3 AND \
                     valid_from <= $4::timestamptz AND (valid_to IS NULL OR valid_to > $4::timestamptz) AND state = $5 AND tsv \
                     @@ q ORDER BY rank DESC, landed_at DESC LIMIT $6",
                    &[&terms, &namespace, &scope, &t, &state, &limit],
                )
                .await?
        }
    };
    let out: Vec<Value> = rows
        .iter()
        .map(|r| json!({"key": r.get::<_, String>(0), "body": r.get::<_, String>(1), "rank": r.get::<_, f32>(2) as f64}))
        .collect();
    if !out.is_empty() {
        return Ok(out);
    }
    let words: Vec<String> = fallback_words(query)
        .into_iter()
        .map(|w| format!("%{w}%"))
        .collect();
    let conds = (0..words.len())
        .map(|i| format!("body ILIKE ${}", i + 1))
        .collect::<Vec<_>>()
        .join(" OR ");
    let n = words.len();
    let (valid, extra) = match at {
        None => (VALID_NOW.to_string(), 0),
        Some(_) => (format!("valid_from <= ${}::timestamptz AND (valid_to IS NULL OR valid_to > ${}::timestamptz)", n + 4, n + 4), 1),
    };
    let sql = format!(
        "SELECT key, body FROM spine_memories WHERE namespace = ${} AND scope = ${} AND {valid} AND state = ${} \
         AND ({conds}) ORDER BY landed_at DESC LIMIT ${}",
        n + 1,
        n + 2,
        n + 3,
        n + 4 + extra
    );
    let mut params: Vec<Box<dyn tokio_postgres::types::ToSql + Sync + Send>> = Vec::new();
    for w in &words {
        params.push(Box::new(w.clone()));
    }
    params.push(Box::new(namespace.to_string()));
    params.push(Box::new(scope.to_string()));
    params.push(Box::new(state.to_string()));
    if let Some(at) = at {
        params.push(Box::new(at_ts(at)?));
    }
    params.push(Box::new(limit));
    let refs: Vec<&(dyn tokio_postgres::types::ToSql + Sync)> = params
        .iter()
        .map(|p| p.as_ref() as &(dyn tokio_postgres::types::ToSql + Sync))
        .collect();
    let rows = g.client().query(&sql, &refs).await?;
    Ok(rows
        .iter()
        .map(|r| json!({"key": r.get::<_, String>(0), "body": r.get::<_, String>(1), "rank": 0.0}))
        .collect())
}

/// Recall by timeframe (MEM-1): every word landed between X and Y, oldest first.
pub async fn within(
    g: &Ground,
    scope: &str,
    state: &str,
    namespace: &str,
    from: &str,
    to: &str,
    limit: i64,
) -> Result<Vec<Value>, RoadError> {
    let (f, t) = (at_ts(from)?, at_ts(to)?);
    let rows = g
        .client()
        .query(
            "SELECT key, body, landed_at FROM spine_memories WHERE namespace = $1 AND scope = $2 AND \
             state = $3 AND landed_at BETWEEN $4::timestamptz AND $5::timestamptz ORDER BY landed_at LIMIT $6",
            &[&namespace, &scope, &state, &f, &t, &limit],
        )
        .await?;
    Ok(rows
        .iter()
        .map(|r| json!({"key": r.get::<_, String>(0), "body": r.get::<_, String>(1), "landed_at": isoformat(r.get::<_, SystemTime>(2))}))
        .collect())
}

pub async fn recent(
    g: &Ground,
    scope: &str,
    state: &str,
    namespace: &str,
    limit: i64,
) -> Result<Vec<Value>, RoadError> {
    let rows = g
        .client()
        .query(
            "SELECT key, body FROM spine_memories WHERE namespace = $1 AND scope = $2 AND valid_to IS \
             NULL AND state = $3 ORDER BY landed_at DESC LIMIT $4",
            &[&namespace, &scope, &state, &limit],
        )
        .await?;
    Ok(rows
        .iter()
        .map(|r| json!({"key": r.get::<_, String>(0), "body": r.get::<_, String>(1)}))
        .collect())
}

/// Governed erasure (MEM-5): every version leaves the Record; a TOMBSTONE keeps the hashes.
pub async fn purge(
    g: &mut Ground,
    scope: &str,
    by_did: &str,
    namespace: &str,
    key: &str,
) -> Result<Value, RoadError> {
    let tx = g.client_mut().transaction().await?;
    let rows = tx
        .query(
            "DELETE FROM spine_memories WHERE namespace = $1 AND key = $2 AND scope = $3 RETURNING hash",
            &[&namespace, &key, &scope],
        )
        .await?;
    let hashes: Vec<String> = rows.iter().map(|r| r.get(0)).collect();
    if !hashes.is_empty() {
        let e = Mint {
            kind: "event".into(),
            r#type: PURGE_EVENT.into(),
            universe_id: scope.into(),
            scope_path: scope.into(),
            payload: purge_payload(namespace, key, &hashes),
            correlation_id: None,
            authority_chain: Some(vec![by_did.to_string()]),
            aggregate: None,
            marker: None,
        }
        .mint()?;
        let raw = envelope::encode(&e)?;
        outbox::add_row(&tx, &raw, e["message_id"].as_str().unwrap_or_default()).await?;
    }
    tx.commit().await?;
    Ok(json!({"ref": format!("{namespace}/{key}"), "versions": hashes.len(), "hashes": hashes}))
}

/// `glass.recall_view` — verbatim recall (MEM-1): by ref (a memory, as of a
/// time, or its lineage), by ask, by session, or by timeframe.
#[allow(clippy::too_many_arguments)]
pub async fn recall_view(
    g: &Ground,
    scope: &str,
    r#ref: Option<&str>,
    ask: Option<&str>,
    session: Option<&str>,
    window: Option<(&str, &str)>,
    person: &str,
    at: Option<&str>,
    history_wanted: bool,
) -> Result<Option<Value>, RoadError> {
    if let Some(r) = r#ref {
        let (ns, key) = r.split_once('/').unwrap_or((r, ""));
        if history_wanted {
            let versions = history(g, scope, ns, key).await?;
            return Ok(if versions.is_empty() {
                None
            } else {
                Some(json!({"ref": r, "history": versions}))
            });
        }
        let Some(body) = get(g, scope, "in", ns, key, at).await? else {
            return Ok(None);
        };
        let row = g
            .client()
            .query_opt(
                "SELECT hash, by_did, landed_at, valid_from, valid_to FROM spine_memories WHERE namespace = \
                 $1 AND key = $2 AND scope = $3 AND body = $4 ORDER BY valid_from DESC LIMIT 1",
                &[&ns, &key, &scope, &body],
            )
            .await?;
        let Some(m) = row else {
            return Ok(None);
        };
        return Ok(Some(json!({"memory": {
            "ref": r, "body": body, "hash": m.get::<_, String>(0), "by": m.get::<_, String>(1),
            "landed_at": isoformat(m.get::<_, SystemTime>(2)), "valid_from": isoformat(m.get::<_, SystemTime>(3)),
            "valid_to": iso_opt(m.get::<_, Option<SystemTime>>(4)), "as_of": at,
        }})));
    }
    if let Some(a) = ask {
        return Ok(crate::asks::ask_view(g, scope, a)
            .await?
            .map(|v| json!({"ask": v})));
    }
    if let Some(s) = session {
        return Ok(crate::sessions::session_view(g, scope, s)
            .await?
            .map(|v| json!({"session": v})));
    }
    if let Some((from, to)) = window {
        let (f, t) = (at_ts(from)?, at_ts(to)?);
        let asks = g
            .client()
            .query(
                "SELECT ask_id, text, reply, asked_at, replied_at, served_by FROM spine_asks WHERE person = \
                 $1 AND scope = $2 AND asked_at BETWEEN $3::timestamptz AND $4::timestamptz ORDER BY asked_at",
                &[&person, &scope, &f, &t],
            )
            .await?;
        let asks: Vec<Value> = asks
            .iter()
            .map(|r| {
                json!({"ask_id": r.get::<_, String>(0), "text": r.get::<_, String>(1), "reply": r.get::<_, Option<String>>(2),
                       "asked_at": isoformat(r.get::<_, SystemTime>(3)), "replied_at": iso_opt(r.get::<_, Option<SystemTime>>(4)),
                       "served_by": r.get::<_, Option<String>>(5)})
            })
            .collect();
        let mems = g
            .client()
            .query(
                "SELECT namespace, key, body, hash, landed_at FROM spine_memories WHERE scope = $1 AND \
                 landed_at BETWEEN $2::timestamptz AND $3::timestamptz ORDER BY landed_at",
                &[&scope, &f, &t],
            )
            .await?;
        let memories: Vec<Value> = mems
            .iter()
            .map(|r| {
                json!({"ref": format!("{}/{}", r.get::<_, String>(0), r.get::<_, String>(1)), "body": r.get::<_, String>(2),
                       "hash": r.get::<_, String>(3), "landed_at": isoformat(r.get::<_, SystemTime>(4))})
            })
            .collect();
        return Ok(Some(
            json!({"window": {"from": from, "to": to}, "asks": asks, "memories": memories}),
        ));
    }
    Ok(None)
}
