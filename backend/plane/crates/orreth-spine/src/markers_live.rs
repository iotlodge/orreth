// PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp3, the ask road · 2026-09-22
// Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp4, the loops: `set_marker` with its fact · the interest law (`dispatch_interests`) · 2026-09-23
//! Markers on the ground — mirrors `orreth_spine.markers` (canon 0006): the
//! registry (the kernel's seven seeded in every world), the marker row minted
//! WITH the fact inside the write path's own transaction, the ROOT column
//! (P25: every marker knows its root, so the Analyzer is a GROUP BY over the
//! ground — never a walk per request), the tree · the ancestry · the stream,
//! and `with_words` — the why in words (an ask's text and status, an
//! intention's words and whether it stands, a schedule's cadence). The
//! `origins` / `origin` projections are the Analyzer's doors; they return the
//! same JSON VALUES the Python doors return (key order is serde's — sorted —
//! and the wire's JSON is the same JSON).

use crate::envelope::{self, Mint};
use crate::ground::Ground;
use crate::hash::content_hash;
use crate::outbox;
use crate::schema::has_table;
use crate::world::{head, iso_opt, isoformat, json_text, refused, token_hex, RoadError, World};
use serde_json::{json, Map, Value};
use std::time::SystemTime;
use tokio_postgres::Transaction;

pub const MARKER_SET: &str = "orreth.marker.set.v1";
/// P6 sp3: MITL is an include of the third kind.
pub const INCLUDES: [&str; 4] = ["planner", "critic", "grader", "mitl"];

/// The kernel's kinds, in every world — kind, group, description.
pub const SEED: [(&str, &str, &str); 7] = [
    ("objective", "structural", "a human's ask — a root"),
    (
        "intention",
        "structural",
        "a schedule (human · role · kernel) — a root; occurrences under it",
    ),
    (
        "thought",
        "structural",
        "an include's reasoning — under the session's latest objective",
    ),
    (
        "action",
        "structural",
        "a tool call, a purge, a watch — under the serving ask",
    ),
    (
        "observation",
        "structural",
        "a harness run, a red watch, a lease lapse — under its kernel intention",
    ),
    (
        "improvement",
        "quality",
        "an improvement observed to what was being executed — every body's policy marks it",
    ),
    (
        "watch-red",
        "resiliency",
        "a watch judged red — under the intention that keeps it green (0007)",
    ),
];

pub fn new_id() -> String {
    format!("mk_{}", token_hex(6))
}

/// The marker row, inside a transaction someone else owns (the write path:
/// the fact and its marker land together). The root is the parent's root,
/// or itself.
#[allow(clippy::too_many_arguments)]
pub async fn insert(
    tx: &Transaction<'_>,
    marker_id: &str,
    kind: &str,
    parent: Option<&str>,
    r#ref: &str,
    by: &str,
    note: Option<&str>,
    scope: &str,
) -> Result<(), RoadError> {
    tx.execute(
        "INSERT INTO spine_markers (marker_id, kind, parent, ref, by_did, note, scope, root) \
         VALUES ($1, $2, $3, $4, $5, $6, $7, coalesce((SELECT root FROM spine_markers WHERE \
         marker_id = $8), $9))",
        &[
            &marker_id, &kind, &parent, &r#ref, &by, &note, &scope, &parent, &marker_id,
        ],
    )
    .await?;
    Ok(())
}

/// The `mark` door's effect (and the loop's): a marker set by a body, a human
/// or the kernel on what was being executed — with its fact on the rail
/// (`orreth.marker.set.v1`) so interested bodies can act, in ONE transaction.
/// The fact wears the setter's FULL chain (AG-7): the chain given, the setter
/// appended when absent; `[by]` alone when a human marks by hand. Returns the
/// marker's four fields plus `ref` and `note`.
#[allow(clippy::too_many_arguments)]
pub async fn set_marker(
    g: &mut Ground,
    w: &World,
    kind: &str,
    r#ref: &str,
    by: &str,
    parent: Option<&str>,
    note: Option<&str>,
    chain: Option<&[String]>,
) -> Result<Value, RoadError> {
    check_kind(g, &w.scope, kind).await?;
    let mid = new_id();
    let marker = json!({"kind": kind, "id": mid, "parent": parent, "by": by});
    let mut authority: Vec<String> = chain.map(|c| c.to_vec()).unwrap_or_default();
    if !authority.iter().any(|a| a == by) {
        authority.push(by.to_string());
    }
    let e = Mint {
        kind: "event".into(),
        r#type: MARKER_SET.into(),
        universe_id: w.scope.clone(),
        scope_path: w.scope.clone(),
        payload: json!({"ref": r#ref, "hash": content_hash(&Value::String(note.unwrap_or("").into())),
                        "marker_id": mid, "kind": kind, "parent": parent}),
        correlation_id: Some(r#ref.to_string()),
        authority_chain: Some(authority),
        aggregate: None,
        marker: Some(marker.clone()),
    }
    .mint()?;
    let raw = envelope::encode(&e)?;
    let tx = g.client_mut().transaction().await?;
    insert(&tx, &mid, kind, parent, r#ref, by, note, &w.scope).await?;
    outbox::add_row(&tx, &raw, e["message_id"].as_str().unwrap_or_default()).await?;
    tx.commit().await?;
    let mut out = marker;
    out["ref"] = json!(r#ref);
    out["note"] = json!(note);
    Ok(out)
}

/// The bodies of this world whose templates declared interest in a kind.
pub async fn interested_bodies(
    g: &Ground,
    scope: &str,
    kind: &str,
) -> Result<Vec<String>, RoadError> {
    let rows = g
        .client()
        .query(
            "SELECT DISTINCT ON (name) name, interests FROM spine_joins WHERE scope = $1 ORDER BY \
             name, join_id DESC",
            &[&scope],
        )
        .await?;
    Ok(rows
        .iter()
        .filter(|r| {
            let ints: Option<String> = r.get(1);
            json_text(ints.as_deref())
                .and_then(|v| v.as_array().cloned())
                .is_some_and(|a| a.iter().any(|k| k == kind))
        })
        .map(|r| r.get(0))
        .collect())
}

/// The interest law: every interested body is asked to act — the marker as
/// PARENT, so the lineage records who acted, on what, and why; the act lands
/// in the marked ask's session. Then the same law at intention level (0007):
/// an interested intention plans (`intent_live::on_marker`).
pub async fn dispatch_interests(
    g: &mut Ground,
    w: &World,
    marker: &Value,
    r#ref: &str,
    note: Option<&str>,
) -> Result<Vec<Value>, RoadError> {
    let session: Option<String> = g
        .client()
        .query_opt(
            "SELECT session FROM spine_asks WHERE ask_id = $1",
            &[&r#ref],
        )
        .await?
        .and_then(|r| r.get(0));
    let kind = marker["kind"].as_str().unwrap_or_default().to_string();
    let by = marker["by"].as_str().unwrap_or_default().to_string();
    let mid = marker["id"].as_str().unwrap_or_default().to_string();
    let mut asked = Vec::new();
    for name in interested_bodies(g, &w.scope, &kind).await? {
        if name == by {
            continue;
        }
        let text = format!(
            "A marker of kind {} was set on {ref} by {by}{}. Act on it as your role requires.",
            crate::py::repr_str(&kind),
            note.map(|n| format!(": {n}")).unwrap_or_default()
        );
        let filed = crate::asks::submit_ask(
            g,
            w,
            crate::asks::Submit {
                text,
                person: by.clone(),
                to: Some(vec![name.clone()]),
                parent_marker: Some(mid.clone()),
                session: session.clone(),
                ..Default::default()
            },
        )
        .await?;
        asked.push(json!({"body": name, "ask_id": filed.ids().first().cloned()}));
    }
    for t in crate::intent_live::on_marker(g, w, marker, r#ref, note).await? {
        asked.push(json!({"body": t["planner"], "ask_id": t["plan_ask"],
                          "intention": t["intention_id"], "words": t["words"]}));
    }
    Ok(asked)
}

/// The kernel's kinds, in THIS world — idempotent.
pub async fn seed(g: &Ground, scope: &str) -> Result<(), RoadError> {
    for (kind, grp, desc) in SEED {
        g.client()
            .execute(
                "INSERT INTO spine_marker_kinds (kind, grp, description, declared_by, scope) \
                 VALUES ($1, $2, $3, 'the kernel', $4) ON CONFLICT DO NOTHING",
                &[&kind, &grp, &desc, &scope],
            )
            .await?;
    }
    Ok(())
}

/// The registry, by group then kind.
pub async fn kinds(g: &Ground, scope: &str) -> Result<Vec<Value>, RoadError> {
    seed(g, scope).await?;
    let rows = g
        .client()
        .query(
            "SELECT kind, grp, description, declared_by, declared_at FROM spine_marker_kinds \
             WHERE scope = $1 ORDER BY grp, kind",
            &[&scope],
        )
        .await?;
    Ok(rows
        .iter()
        .map(|r| {
            json!({
                "kind": r.get::<_, String>(0), "group": r.get::<_, String>(1),
                "description": r.get::<_, String>(2), "declared_by": r.get::<_, String>(3),
                "declared_at": isoformat(r.get::<_, SystemTime>(4)),
            })
        })
        .collect())
}

/// Declared before use — the teaching names the registry (`UnknownKind`).
pub async fn check_kind(g: &Ground, scope: &str, kind: &str) -> Result<(), RoadError> {
    seed(g, scope).await?;
    let known = g
        .client()
        .query_opt(
            "SELECT 1 FROM spine_marker_kinds WHERE kind = $1 AND scope = $2",
            &[&kind, &scope],
        )
        .await?;
    if known.is_some() {
        return Ok(());
    }
    let names: Vec<String> = kinds(g, scope)
        .await?
        .iter()
        .map(|k| k["kind"].as_str().unwrap_or_default().to_string())
        .collect();
    Err(refused(format!(
        "no marker kind named '{kind}' is declared here — declare it first (kind, group, what \
         it means); the kinds today: {}",
        names.join(", ")
    )))
}

/// One marker, or nothing.
pub async fn get(g: &Ground, scope: &str, marker_id: &str) -> Result<Option<Value>, RoadError> {
    let row = g
        .client()
        .query_opt(
            "SELECT marker_id, kind, parent, ref, by_did, note, at FROM spine_markers WHERE \
             marker_id = $1 AND scope = $2",
            &[&marker_id, &scope],
        )
        .await?;
    Ok(row.map(|r| {
        json!({
            "id": r.get::<_, String>(0), "kind": r.get::<_, String>(1),
            "parent": r.get::<_, Option<String>>(2), "ref": r.get::<_, String>(3),
            "by": r.get::<_, String>(4), "note": r.get::<_, Option<String>>(5),
            "at": isoformat(r.get::<_, SystemTime>(6)),
        })
    }))
}

/// The envelope's four fields for a marker id.
pub async fn as_env(
    g: &Ground,
    scope: &str,
    marker_id: Option<&str>,
) -> Result<Option<Value>, RoadError> {
    let Some(id) = marker_id else {
        return Ok(None);
    };
    Ok(get(g, scope, id)
        .await?
        .map(|m| json!({"kind": m["kind"], "id": m["id"], "parent": m["parent"], "by": m["by"]})))
}

/// `_row`: the eight columns every tree/ancestry/stream row carries.
pub fn row_of(r: &tokio_postgres::Row) -> Value {
    json!({
        "id": r.get::<_, String>(0), "kind": r.get::<_, String>(1),
        "parent": r.get::<_, Option<String>>(2), "ref": r.get::<_, String>(3),
        "by": r.get::<_, String>(4), "note": r.get::<_, Option<String>>(5),
        "at": isoformat(r.get::<_, SystemTime>(6)), "depth": r.get::<_, i32>(7),
    })
}

/// Everything under a marker — the dependency, downward.
pub async fn tree(
    g: &Ground,
    scope: &str,
    root: &str,
    limit: i64,
) -> Result<Vec<Value>, RoadError> {
    let rows = g
        .client()
        .query(
            "WITH RECURSIVE t AS (  SELECT marker_id, kind, parent, ref, by_did, note, at, 0 AS \
             depth FROM spine_markers   WHERE marker_id = $1 AND scope = $2  UNION ALL  SELECT \
             m.marker_id, m.kind, m.parent, m.ref, m.by_did, m.note, m.at, t.depth + 1   FROM \
             spine_markers m JOIN t ON m.parent = t.marker_id) SELECT * FROM t ORDER BY depth, at \
             LIMIT $3",
            &[&root, &scope, &limit],
        )
        .await?;
    Ok(rows.iter().map(row_of).collect())
}

/// Up from a marker to its root — what this serves.
pub async fn ancestry(g: &Ground, scope: &str, marker_id: &str) -> Result<Vec<Value>, RoadError> {
    let rows = g
        .client()
        .query(
            "WITH RECURSIVE a AS (  SELECT marker_id, kind, parent, ref, by_did, note, at, 0 AS \
             depth FROM spine_markers   WHERE marker_id = $1 AND scope = $2  UNION ALL  SELECT \
             m.marker_id, m.kind, m.parent, m.ref, m.by_did, m.note, m.at, a.depth + 1   FROM \
             spine_markers m JOIN a ON m.marker_id = a.parent) SELECT * FROM a ORDER BY depth",
            &[&marker_id, &scope],
        )
        .await?;
    Ok(rows.iter().map(row_of).collect())
}

/// The live stream, newest first — by kind, by group, or all.
pub async fn stream(
    g: &Ground,
    scope: &str,
    kind: Option<&str>,
    grp: Option<&str>,
    limit: i64,
) -> Result<Vec<Value>, RoadError> {
    let rows = g
        .client()
        .query(
            "SELECT m.marker_id, m.kind, m.parent, m.ref, m.by_did, m.note, m.at, 0, k.grp FROM \
             spine_markers m LEFT JOIN spine_marker_kinds k ON k.kind = m.kind AND k.scope = \
             m.scope WHERE m.scope = $1 AND ($2::text IS NULL OR m.kind = $2) AND ($3::text IS \
             NULL OR k.grp = $3) ORDER BY m.at DESC LIMIT $4",
            &[&scope, &kind, &grp, &limit],
        )
        .await?;
    Ok(rows
        .iter()
        .map(|r| {
            let mut d = row_of(r);
            d["group"] = json!(r.get::<_, Option<String>>(8));
            d
        })
        .collect())
}

fn refs_with(rows: &[Value], prefix: &str) -> Vec<String> {
    rows.iter()
        .filter_map(|m| m["ref"].as_str())
        .filter(|r| r.starts_with(prefix))
        .map(str::to_string)
        .collect()
}

fn obj(v: &mut Value) -> &mut Map<String, Value> {
    v.as_object_mut().expect("a marker row is an object")
}

/// The why in words: an ask ref carries the ask's text and status (walk #5:
/// the why printed ids); an intention ref its words and whether it stands;
/// a schedule ref its text and cadence (W21).
pub async fn with_words(g: &Ground, mut rows: Vec<Value>) -> Result<Vec<Value>, RoadError> {
    let ids = refs_with(&rows, "ask_");
    if !ids.is_empty() {
        let found = g
            .client()
            .query(
                "SELECT ask_id, left(text, 100), status, target FROM spine_asks WHERE ask_id = \
                 ANY($1)",
                &[&ids],
            )
            .await?;
        for r in &found {
            let id: String = r.get(0);
            for m in rows.iter_mut().filter(|m| m["ref"].as_str() == Some(&id)) {
                let o = obj(m);
                o.insert("words".into(), json!(r.get::<_, Option<String>>(1)));
                o.insert("status".into(), json!(r.get::<_, String>(2)));
                o.insert("target".into(), json!(r.get::<_, Option<String>>(3)));
            }
        }
    }
    let iids = refs_with(&rows, "int_");
    if !iids.is_empty() && has_table(g, "spine_intentions").await? {
        let found = g
            .client()
            .query(
                "SELECT intention_id, left(words, 100), active, serves, kind, blocked_note FROM \
                 spine_intentions WHERE intention_id = ANY($1)",
                &[&iids],
            )
            .await?;
        for r in &found {
            let id: String = r.get(0);
            for m in rows.iter_mut().filter(|m| m["ref"].as_str() == Some(&id)) {
                let note: Option<String> = r.get(5);
                let o = obj(m);
                o.insert("words".into(), json!(r.get::<_, Option<String>>(1)));
                o.insert("active".into(), json!(r.get::<_, bool>(2)));
                o.insert("serves".into(), json!(r.get::<_, String>(3)));
                o.insert("origin_kind".into(), json!(r.get::<_, String>(4)));
                o.insert("blocked".into(), json!(note.is_some()));
                o.insert("blocked_note".into(), json!(note));
            }
        }
    }
    let sids = refs_with(&rows, "sch_");
    if !sids.is_empty() && has_table(g, "spine_schedules").await? {
        let found = g
            .client()
            .query(
                "SELECT s.schedule_id, left(s.text, 100), s.active, s.kind, s.every_s, \
                 s.last_at, (SELECT count(*) FROM spine_occurrences o WHERE o.schedule_id = \
                 s.schedule_id) FROM spine_schedules s WHERE s.schedule_id = ANY($1)",
                &[&sids],
            )
            .await?;
        for r in &found {
            let id: String = r.get(0);
            for m in rows.iter_mut().filter(|m| m["ref"].as_str() == Some(&id)) {
                let every: i32 = r.get(4);
                let o = obj(m);
                o.insert("words".into(), json!(r.get::<_, Option<String>>(1)));
                o.insert("active".into(), json!(r.get::<_, bool>(2)));
                o.insert("origin_kind".into(), json!(r.get::<_, String>(3)));
                o.insert("serves".into(), json!("schedule"));
                o.insert(
                    "cadence".into(),
                    json!(crate::ask::cadence_words(every as i64)),
                );
                o.insert("runs".into(), json!(r.get::<_, i64>(6)));
                o.insert("last_at".into(), iso_opt(r.get::<_, Option<SystemTime>>(5)));
            }
        }
    }
    Ok(rows)
}

/// The Analyzer's door (P25): every ROOT in this world — intentions and
/// objectives — newest first, with what grew under each, counted by kind,
/// from the ground alone (the root column: no walk per request).
pub async fn origins(g: &Ground, scope: &str, limit: i64) -> Result<Vec<Value>, RoadError> {
    let rows = g
        .client()
        .query(
            "SELECT r.marker_id, r.kind, r.parent, r.ref, r.by_did, r.note, r.at, 0, (SELECT \
             coalesce(json_object_agg(x.kind, x.n), '{}'::json) FROM   (SELECT c.kind, count(*) \
             AS n FROM spine_markers c     WHERE c.scope = r.scope AND c.root = r.marker_id AND \
             c.marker_id <> r.marker_id     GROUP BY c.kind) x)::text FROM spine_markers r WHERE \
             r.scope = $1 AND r.parent IS NULL ORDER BY r.at DESC LIMIT $2",
            &[&scope, &limit],
        )
        .await?;
    let mut out = Vec::with_capacity(rows.len());
    for r in &rows {
        let mut d = row_of(r);
        let root = d["id"].clone();
        let counts: Value = serde_json::from_str(&r.get::<_, String>(8)).unwrap_or(json!({}));
        let o = obj(&mut d);
        o.insert("root".into(), root);
        o.insert("counts".into(), counts);
        out.push(d);
    }
    with_words(g, out).await
}

/// One origin's tree, in words.
pub async fn origin(g: &Ground, scope: &str, root: &str) -> Result<Value, RoadError> {
    let t = with_words(g, tree(g, scope, root, 500).await?).await?;
    Ok(json!({"root": root, "tree": t}))
}

/// The note a root marker wears — the first 200 characters (`declare`'s law).
pub fn note_head(words: &str) -> String {
    head(words, 200)
}
