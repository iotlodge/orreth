// PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp3, the ask road · 2026-09-22
//! Intentions on the ground — the row half of `orreth_spine.intent` (0007):
//! an intention declared at the door lands as its row, its ROOT marker, its
//! own session (where its objectives show) and its fact, in one transaction;
//! the listing the glass reads. The LOOP — watches judged, the planner asked,
//! the objective filed — is sp4's; the stop's and restart's demands are pure
//! and live in [`crate::proof`].

use crate::envelope::{self, Mint};
use crate::ground::Ground;
use crate::hash::content_hash;
use crate::intent::{INTENTION_DECLARED, KINDS, SERVES};
use crate::markers_live;
use crate::outbox;
use crate::world::{iso_opt, isoformat, json_text, refused, token_hex, RoadError, World};
use serde_json::{json, Value};
use std::time::SystemTime;

const COLS: &str =
    "intention_id, words, serves, kind, interests, planner, runner, every_s, gates, \
                    active, stopped_by, stopped_at, added_by, marker, session, next_at, last_at, \
                    added_at, blocked_crew, blocked_note, restarted_by, restarted_at";

fn dict(r: &tokio_postgres::Row) -> Value {
    let blocked_crew: Option<String> = r.get(18);
    json!({
        "intention_id": r.get::<_, String>(0), "words": r.get::<_, String>(1),
        "serves": r.get::<_, String>(2), "kind": r.get::<_, String>(3),
        "interests": json_text(Some(r.get::<_, String>(4).as_str())).unwrap_or(json!([])),
        "planner": r.get::<_, String>(5), "runner": r.get::<_, Option<String>>(6),
        "every_s": r.get::<_, Option<i32>>(7),
        "gates": json_text(r.get::<_, Option<String>>(8).as_deref()),
        "active": r.get::<_, bool>(9), "stopped_by": r.get::<_, Option<String>>(10),
        "stopped_at": iso_opt(r.get::<_, Option<SystemTime>>(11)),
        "added_by": r.get::<_, String>(12), "marker": r.get::<_, String>(13),
        "session": r.get::<_, Option<String>>(14),
        "next_at": iso_opt(r.get::<_, Option<SystemTime>>(15)),
        "last_at": iso_opt(r.get::<_, Option<SystemTime>>(16)),
        "added_at": isoformat(r.get::<_, SystemTime>(17)),
        "blocked": blocked_crew.is_some(), "blocked_note": r.get::<_, Option<String>>(19),
        "restarted_by": r.get::<_, Option<String>>(20),
        "restarted_at": iso_opt(r.get::<_, Option<SystemTime>>(21)),
    })
}

pub async fn get(g: &Ground, scope: &str, intention_id: &str) -> Result<Option<Value>, RoadError> {
    let row = g
        .client()
        .query_opt(
            &format!("SELECT {COLS} FROM spine_intentions WHERE intention_id = $1 AND scope = $2"),
            &[&intention_id, &scope],
        )
        .await?;
    Ok(row.as_ref().map(dict))
}

/// What the door hands `declare`.
#[derive(Debug, Clone, Default)]
pub struct Declare {
    pub words: String,
    pub serves: String,
    pub kind: String,
    pub by: String,
    pub interests: Vec<String>,
    pub planner: String,
    pub runner: Option<String>,
    pub every_s: Option<i64>,
    pub gates: Option<Value>,
}

/// An intention lands: its row, its root marker, its own session, and its
/// fact on the rail — one transaction. Refusals in the reference's words.
pub async fn declare(g: &mut Ground, w: &World, d: Declare) -> Result<Value, RoadError> {
    if !SERVES.contains(&d.serves.as_str()) {
        return Err(refused(format!("serves is one of {}", SERVES.join(", "))));
    }
    if !KINDS.contains(&d.kind.as_str()) {
        return Err(refused(format!("kind is one of {}", KINDS.join(", "))));
    }
    let words = d.words.split_whitespace().collect::<Vec<_>>().join(" ");
    if words.is_empty() {
        return Err(refused("an intention is words"));
    }
    let interests: Vec<String> = d
        .interests
        .iter()
        .map(|k| k.trim().to_lowercase())
        .filter(|k| !k.is_empty())
        .collect();
    if interests.is_empty() && d.every_s.is_none() {
        return Err(refused(
            "an intention needs something to wake it: say WHEN — 'when a watch goes red', \
             'every hour', 'when an improvement is marked'",
        ));
    }
    for k in &interests {
        markers_live::check_kind(g, &w.scope, k).await?;
    }
    let iid = format!("int_{}", token_hex(6));
    let mid = markers_live::new_id();
    let sid = format!("ses_{}", token_hex(6));
    let marker = json!({"kind": "intention", "id": mid, "parent": Value::Null, "by": d.by});
    let planner = if d.planner.is_empty() {
        "planner".to_string()
    } else {
        d.planner.clone()
    };
    let e = Mint {
        kind: "event".into(),
        r#type: INTENTION_DECLARED.into(),
        universe_id: w.scope.clone(),
        scope_path: w.scope.clone(),
        payload: json!({
            "ref": iid, "hash": content_hash(&Value::String(words.clone())), "serves": d.serves,
            "kind": d.kind, "interests": interests, "planner": planner, "every_s": d.every_s,
        }),
        correlation_id: Some(iid.clone()),
        authority_chain: Some(vec![d.by.clone()]),
        aggregate: Some(json!({"type": "intention", "id": iid, "sequence": 1})),
        marker: Some(marker),
    }
    .mint()?;
    let raw = envelope::encode(&e)?;
    let message_id = e["message_id"].as_str().unwrap_or_default().to_string();
    let (scope, by, serves, kind, runner) = (
        w.scope.clone(),
        d.by.clone(),
        d.serves.clone(),
        d.kind.clone(),
        d.runner.clone(),
    );
    let interests_text = serde_json::to_string(&interests).unwrap_or_else(|_| "[]".into());
    let gates_text = d.gates.as_ref().map(|g| g.to_string());
    let every: Option<i32> = d.every_s.map(|e| e as i32);
    let note = markers_live::note_head(&words);
    let (iid2, mid2, sid2, words2) = (iid.clone(), mid.clone(), sid.clone(), words.clone());
    outbox::commit_with_outbox(g, &raw, &message_id, None, async move |tx| {
        markers_live::insert(tx, &mid2, "intention", None, &iid2, &by, Some(&note), &scope)
            .await
            .map_err(|e| crate::rail_error::RailError::Refused(e.to_string()))?;
        let title: String = words2.chars().take(120).collect();
        tx.execute(
            "INSERT INTO spine_sessions (session_id, person, scope, title, state) VALUES ($1, $2, \
             $3, $4, 'in')",
            &[&sid2, &by, &scope, &title],
        )
        .await?;
        tx.execute(
            "INSERT INTO spine_intentions (intention_id, words, serves, kind, interests, planner, \
             runner, every_s, gates, added_by, scope, marker, session, next_at) VALUES ($1, $2, $3, \
             $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, CASE WHEN $8::int IS NULL THEN NULL ELSE \
             now() + make_interval(secs => coalesce($8, 0)) END)",
            &[
                &iid2, &words2, &serves, &kind, &interests_text, &planner, &runner, &every,
                &gates_text, &by, &scope, &mid2, &sid2,
            ],
        )
        .await?;
        Ok(())
    })
    .await?;
    Ok(get(g, &w.scope, &iid).await?.unwrap_or(Value::Null))
}

/// Every intention in this world, newest first, with what grew under it.
pub async fn listing(
    g: &Ground,
    scope: &str,
    serves: Option<&str>,
    kind: Option<&str>,
    limit: i64,
) -> Result<Vec<Value>, RoadError> {
    let rows = g
        .client()
        .query(
            &format!(
                "SELECT {COLS}, (SELECT count(*) FROM spine_markers c WHERE c.parent = i.marker \
                 AND c.kind = 'objective'), (SELECT count(*) FROM spine_markers c WHERE c.parent \
                 = i.marker   AND c.kind NOT IN ('objective', 'thought')), (SELECT count(*) FROM \
                 spine_intent_turns t WHERE t.intention_id = i.intention_id) FROM spine_intentions \
                 i WHERE i.scope = $1 AND ($2::text IS NULL OR i.serves = $2) AND ($3::text IS \
                 NULL OR i.kind = $3) ORDER BY i.added_at DESC LIMIT $4"
            ),
            &[&scope, &serves, &kind, &limit],
        )
        .await?;
    Ok(rows
        .iter()
        .map(|r| {
            let mut d = dict(r);
            d["objectives"] = json!(r.get::<_, i64>(22));
            d["observations"] = json!(r.get::<_, i64>(23));
            d["turns"] = json!(r.get::<_, i64>(24));
            d
        })
        .collect())
}
