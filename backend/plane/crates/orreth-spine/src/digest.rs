// PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp5, memory and the export · 2026-09-24
// Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch walk #13 cures: W51 a roll is a fact the feed carries · W52 the digest in the human's zone · THE GUIDE door · 2026-09-24
//! The Digest — `orreth_spine.digest` ported (MEM-3, canon 0003): the short
//! version of a session composed from the Record alone (deterministic,
//! extractive — a rebuild lands byte-identical), the sibling law over
//! `spine_digests` (the same substance lands nothing; changed substance
//! supersedes), its fact through the outbox, the current digest of a
//! session, the rebuild after a purge, and the pack's third rung — the
//! same SQL as the reference so both kernels write one Digest.

use crate::envelope::{self, Mint};
use crate::ground::Ground;
use crate::hash::content_hash;
use crate::memory::{digest_lines, digest_payload, Civil, DigestAsk, DIGEST_EVENT};
use crate::outbox;
use crate::schema::has_table;
use crate::world::{isoformat, token_hex, RoadError};
use serde_json::{json, Value};
use std::time::SystemTime;

pub const BUILDER: &str = "the digest builder";

/// `digest.compose_session`: (body, sources, state) — None when no such session.
pub async fn compose_session(
    g: &Ground,
    scope: &str,
    session_id: &str,
    zone: &str,
) -> Result<Option<(String, Vec<String>, String)>, RoadError> {
    // W52: the digest's clock is the human's — the ground shifts every time into the zone
    // (`AT TIME ZONE`, the same tzdata the Python spine's ZoneInfo reads) before it is worded
    let row = g
        .client()
        .query_opt(
            "SELECT session_id, title, opened_at, person, coalesce(state, 'in'), \
             to_char(opened_at AT TIME ZONE $3, 'YYYY-MM-DD\"T\"HH24:MI:SS') FROM spine_sessions \
             WHERE session_id = $1 AND scope = $2",
            &[&session_id, &scope, &zone],
        )
        .await?;
    let Some(row) = row else {
        return Ok(None);
    };
    let title: Option<String> = row.get(1);
    let opened: SystemTime = row.get(2);
    let person: String = row.get(3);
    let state: String = row.get(4);
    let opened_civil = Civil::parse(&row.get::<_, String>(5)).expect("the ground's own text");
    let span_end: SystemTime = g
        .client()
        .query_one(
            "SELECT coalesce(min(opened_at), now()) FROM spine_sessions WHERE person = $1 AND scope = $2 \
             AND opened_at > $3",
            &[&person, &scope, &opened],
        )
        .await?
        .get(0);
    let asks = g
        .client()
        .query(
            "SELECT a.ask_id, a.text, a.reply, a.status, \
             to_char(a.asked_at AT TIME ZONE $2, 'YYYY-MM-DD\"T\"HH24:MI:SS'), \
             to_char(a.replied_at AT TIME ZONE $2, 'YYYY-MM-DD\"T\"HH24:MI:SS'), coalesce(j.name, 'a \
             resident') FROM spine_asks a LEFT JOIN LATERAL (  SELECT name FROM spine_joins WHERE did = \
             a.served_by  ORDER BY join_id DESC LIMIT 1) j ON true WHERE a.session = $1 ORDER BY a.asked_at",
            &[&session_id, &zone],
        )
        .await?;
    let asks: Vec<DigestAsk> = asks
        .iter()
        .map(|r| DigestAsk {
            ask_id: r.get(0),
            text: r.get(1),
            reply: r.get(2),
            status: r.get(3),
            asked_at: Civil::parse(&r.get::<_, String>(4)).expect("the ground's own text"),
            replied_at: r.get::<_, Option<String>>(5).and_then(|t| Civil::parse(&t)),
            who: r.get(6),
        })
        .collect();
    let mut memories: Vec<(String, String, String)> = Vec::new();
    if !asks.is_empty() && has_table(g, "spine_memories").await? {
        let rows = g
            .client()
            .query(
                "SELECT namespace, key, body FROM spine_memories WHERE scope = $1 AND state = $2 AND \
                 landed_at BETWEEN $3 AND $4 ORDER BY landed_at",
                &[&scope, &state, &opened, &span_end],
            )
            .await?;
        memories = rows
            .iter()
            .map(|r| (r.get(0), r.get(1), r.get(2)))
            .collect();
    }
    let (body, sources) =
        digest_lines(session_id, title.as_deref(), opened_civil, &asks, &memories);
    Ok(Some((body, sources, state)))
}

/// `digest.build`: write (or rebuild) the session's digest — the same
/// substance lands nothing new; changed substance lands a sibling.
pub async fn build(
    g: &mut Ground,
    scope: &str,
    session_id: &str,
    by: &str,
    zone: &str,
) -> Result<Option<Value>, RoadError> {
    let Some((body, sources, state)) = compose_session(g, scope, session_id, zone).await? else {
        return Ok(None);
    };
    let h = content_hash(&Value::String(body.clone()));
    let tx = g.client_mut().transaction().await?;
    let prev = tx
        .query_opt(
            "SELECT digest_id, hash FROM spine_digests WHERE kind = 'session' AND ref = $1 AND scope = $2 \
             AND valid_to IS NULL FOR UPDATE",
            &[&session_id, &scope],
        )
        .await?;
    let prev: Option<(String, String)> = prev.map(|r| (r.get(0), r.get(1)));
    if let Some((id, ph)) = &prev {
        if *ph == h {
            tx.commit().await?;
            return Ok(Some(
                json!({"digest_id": id, "hash": h, "body": body, "sources": sources, "new": false}),
            ));
        }
    }
    let did = format!("dig_{}", token_hex(5));
    if let Some((id, _)) = &prev {
        tx.execute(
            "UPDATE spine_digests SET valid_to = now() WHERE digest_id = $1",
            &[id],
        )
        .await?;
    }
    let sources_json = serde_json::to_string(&sources).unwrap_or_else(|_| "[]".into());
    tx.execute(
        "INSERT INTO spine_digests (digest_id, kind, ref, body, sources, hash, by_did, scope, supersedes, \
         state) VALUES ($1, 'session', $2, $3, $4, $5, $6, $7, $8, $9)",
        &[&did, &session_id, &body, &sources_json, &h, &by, &scope, &prev.as_ref().map(|p| p.1.clone()), &state],
    )
    .await?;
    let e = Mint {
        kind: "event".into(),
        r#type: DIGEST_EVENT.into(),
        universe_id: scope.into(),
        scope_path: scope.into(),
        payload: digest_payload(&did, &body, session_id, sources.len()),
        correlation_id: Some(session_id.into()),
        authority_chain: Some(vec![by.to_string()]),
        aggregate: None,
        marker: None,
    }
    .mint()?;
    let raw = envelope::encode(&e)?;
    outbox::add_row(&tx, &raw, e["message_id"].as_str().unwrap_or_default()).await?;
    tx.commit().await?;
    Ok(Some(
        json!({"digest_id": did, "hash": h, "body": body, "sources": sources, "new": true}),
    ))
}

/// The current digest of a session, with its sources.
pub async fn of_session(
    g: &Ground,
    scope: &str,
    session_id: &str,
) -> Result<Option<Value>, RoadError> {
    let row = g
        .client()
        .query_opt(
            "SELECT digest_id, body, sources, hash, by_did, built_at, supersedes FROM spine_digests WHERE \
             kind = 'session' AND ref = $1 AND scope = $2 AND valid_to IS NULL",
            &[&session_id, &scope],
        )
        .await?;
    Ok(row.map(|r| {
        json!({
            "digest_id": r.get::<_, String>(0), "session": session_id, "body": r.get::<_, String>(1),
            "sources": serde_json::from_str::<Value>(&r.get::<_, String>(2)).unwrap_or(json!([])),
            "hash": r.get::<_, String>(3), "by": r.get::<_, String>(4),
            "built_at": isoformat(r.get::<_, SystemTime>(5)), "supersedes": r.get::<_, Option<String>>(6),
        })
    }))
}

/// After a purge: every current digest that cited the ref is rebuilt.
pub async fn rebuild_citing(
    g: &mut Ground,
    scope: &str,
    r#ref: &str,
    by: &str,
    zone: &str,
) -> Result<usize, RoadError> {
    let needle = format!("%\"{}\"%", r#ref);
    let rows = g
        .client()
        .query(
            "SELECT ref FROM spine_digests WHERE kind = 'session' AND scope = $1 AND valid_to IS NULL AND \
             sources LIKE $2",
            &[&scope, &needle],
        )
        .await?;
    let sessions: Vec<String> = rows.iter().map(|r| r.get(0)).collect();
    let mut n = 0;
    for sid in sessions {
        if let Some(made) = build(g, scope, &sid, by, zone).await? {
            if made["new"].as_bool().unwrap_or(false) {
                n += 1;
            }
        }
    }
    Ok(n)
}

/// A listed session without its short version gets it from the log (MEM-3 —
/// the Digest is a projection, rebuildable at any time).
pub async fn build_missing(
    g: &mut Ground,
    scope: &str,
    person: &str,
    limit: i64,
    zone: &str,
) -> Result<usize, RoadError> {
    let rows = g
        .client()
        .query(
            "SELECT s.session_id FROM spine_sessions s WHERE s.person = $1 AND s.scope = $2 AND EXISTS (SELECT \
             1 FROM spine_asks a WHERE a.session = s.session_id) AND NOT EXISTS (SELECT 1 FROM spine_digests d \
             WHERE d.kind = 'session'  AND d.ref = s.session_id AND d.scope = s.scope AND d.valid_to IS NULL) \
             ORDER BY s.opened_at DESC LIMIT $3",
            &[&person, &scope, &limit],
        )
        .await?;
    let sids: Vec<String> = rows.iter().map(|r| r.get(0)).collect();
    let mut n = 0;
    for sid in sids {
        build(g, scope, &sid, BUILDER, zone).await?;
        n += 1;
    }
    Ok(n)
}
