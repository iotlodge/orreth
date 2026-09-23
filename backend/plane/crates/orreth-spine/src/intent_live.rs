// PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp3, the ask road · 2026-09-22
// Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp4, the loops: the stop and the restart · `declared` · the loop (interested · plan · on_marker · due · file · hear · turn) · 2026-09-23
// Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch walk #11 cures: W35 a stop asked is a stop held · W37 a duplicate purpose named at the door · 2026-09-23
//! Intentions on the ground — the row half of `orreth_spine.intent` (0007):
//! an intention declared at the door lands as its row, its ROOT marker, its
//! own session (where its objectives show) and its fact, in one transaction;
//! the listing the glass reads. P7 sp4 adds THE LOOP — watches judged (the
//! monitor), the newly red observed under every intention that cares, the
//! planner asked under the observation, its reply filed as the objective to
//! the crew in the intention's session, runners heard (W8) — turning under
//! the intent BEAT (the beat lock), and the stop with its reverse (rule 11 ·
//! W5 · W20), grave through the ladder in [`crate::proof`].

use crate::envelope::{self, Mint};
use crate::ground::Ground;
use crate::hash::content_hash;
use crate::intent::{
    cannot_act, crew_shape_hash, duplicate_words, improvement_note, observed_words, plan_words,
    watch_note, CADENCE_DUE, INTENTION_DECLARED, INTENTION_RESTARTED, INTENTION_STOPPED, KINDS,
    SERVES, WATCH_RED,
};
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
    if d.kind == "human" {
        // W37: a duplicate purpose is named at the door
        if let Some(r) = g
            .client()
            .query_opt(
                "SELECT kind FROM spine_intentions WHERE words = $1 AND scope = $2 AND active ORDER \
                 BY added_at LIMIT 1",
                &[&words, &w.scope],
            )
            .await?
        {
            return Err(refused(duplicate_words(r.get::<_, &str>(0), &words)));
        }
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

// ---- the stop and its reverse (rule 11 · W5 · W20) --------------------------------------

/// `get` inside a transaction someone else owns.
async fn get_in(
    c: &impl tokio_postgres::GenericClient,
    scope: &str,
    intention_id: &str,
) -> Result<Option<Value>, RoadError> {
    let row = c
        .query_opt(
            &format!("SELECT {COLS} FROM spine_intentions WHERE intention_id = $1 AND scope = $2"),
            &[&intention_id, &scope],
        )
        .await?;
    Ok(row.as_ref().map(dict))
}

fn whose(kind: &str) -> &'static str {
    match kind {
        "kernel" => "the kernel's",
        "role" => "the role's",
        _ => "the human's",
    }
}

/// The stop (`restart` false) or the restart (`restart` true) of an intention,
/// INSIDE a transaction someone else owns — the row, the fact through the
/// outbox row, one commit. `Ok(None)`: no such intention. An intention already
/// in the asked state keeps one face (returned unchanged). A bare act — the
/// proof not the demand's level — is `RoadError::ProofRequired`: the door
/// holds it instead. The proven act carries its level and who confirmed.
pub async fn stop_or_restart_in(
    tx: &tokio_postgres::Transaction<'_>,
    w: &World,
    intention_id: &str,
    by: &str,
    proof: Option<&str>,
    confirmed_by: Option<&str>,
    restart: bool,
) -> Result<Option<Value>, RoadError> {
    let row = tx
        .query_opt(
            "SELECT marker, active, kind, words FROM spine_intentions WHERE intention_id = $1 AND \
             scope = $2",
            &[&intention_id, &w.scope],
        )
        .await?;
    let Some(row) = row else {
        return Ok(None);
    };
    let (marker_id, active, kind, words): (String, bool, String, String) =
        (row.get(0), row.get(1), row.get(2), row.get(3));
    if active == restart {
        return get_in(tx, &w.scope, intention_id).await; // already at rest / already standing: one face
    }
    let demand = if restart {
        crate::proof::restart_demand(&kind)
    } else {
        crate::proof::stop_demand(&kind)
    };
    if proof != Some(demand.level) {
        let verb = if restart { "restarting" } else { "stopping" };
        return Err(RoadError::ProofRequired {
            level: demand.level,
            what: format!("{verb} {} intention “{words}”", whose(&kind)),
            needs_code: demand.needs_code,
        });
    }
    let marker = json!({"kind": "intention", "id": marker_id, "parent": Value::Null, "by": by});
    let mut payload = json!({"ref": intention_id, "hash": "sha256:-", "by": by, "proof": proof});
    let mut chain = vec![by.to_string()];
    if let Some(c) = confirmed_by {
        payload["confirmed_by"] = json!(c);
        if c != by {
            chain.push(c.to_string());
        }
    }
    let e = Mint {
        kind: "event".into(),
        r#type: if restart {
            INTENTION_RESTARTED.into()
        } else {
            INTENTION_STOPPED.into()
        },
        universe_id: w.scope.clone(),
        scope_path: w.scope.clone(),
        payload,
        correlation_id: Some(intention_id.to_string()),
        authority_chain: Some(chain),
        aggregate: None,
        marker: Some(marker),
    }
    .mint()?;
    if restart {
        // active again; the stop's columns stay (the history is whole); the
        // cadence counts from now — never a beat owed from the rest
        tx.execute(
            "UPDATE spine_intentions SET active = true, restarted_by = $1, restarted_at = now(), \
             next_at = CASE WHEN every_s IS NULL THEN NULL ELSE now() + make_interval(secs => \
             every_s) END WHERE intention_id = $2",
            &[&by, &intention_id],
        )
        .await?;
    } else {
        tx.execute(
            "UPDATE spine_intentions SET active = false, stopped_by = $1, stopped_at = now() WHERE \
             intention_id = $2",
            &[&by, &intention_id],
        )
        .await?;
    }
    outbox::add_row(
        tx,
        &envelope::encode(&e)?,
        e["message_id"].as_str().unwrap_or_default(),
    )
    .await?;
    get_in(tx, &w.scope, intention_id).await
}

/// The human's stop (rule 11): recorded on the row and on the rail, never a
/// deletion; the loop does not turn again for it. Grave (W5): a bare stop is
/// `ProofRequired` at the level `stop_demand` names.
pub async fn stop(
    g: &mut Ground,
    w: &World,
    intention_id: &str,
    by: &str,
    proof: Option<&str>,
    confirmed_by: Option<&str>,
) -> Result<Option<Value>, RoadError> {
    let tx = g.client_mut().transaction().await?;
    let out = stop_or_restart_in(&tx, w, intention_id, by, proof, confirmed_by, false).await?;
    tx.commit().await?;
    Ok(out)
}

/// The reverse of the stop (W20): a rested intention stands again, its history
/// whole — a NEW fact, grave through the same ladder; it wakes on the NEXT red
/// transition and its cadence counts from the restart.
pub async fn restart(
    g: &mut Ground,
    w: &World,
    intention_id: &str,
    by: &str,
    proof: Option<&str>,
    confirmed_by: Option<&str>,
) -> Result<Option<Value>, RoadError> {
    let tx = g.client_mut().transaction().await?;
    let out = stop_or_restart_in(&tx, w, intention_id, by, proof, confirmed_by, true).await?;
    tx.commit().await?;
    Ok(out)
}

/// Register once per world (the kernel's at every boot): the same intention
/// is never doubled — and one at rest stays at rest.
pub async fn declared(g: &mut Ground, w: &World, d: Declare) -> Result<Value, RoadError> {
    let words = crate::py::fold_ws(&d.words);
    let row = g
        .client()
        .query_opt(
            "SELECT intention_id FROM spine_intentions WHERE words = $1 AND kind = $2 AND scope = $3",
            &[&words, &d.kind, &w.scope],
        )
        .await?;
    match row {
        Some(r) => Ok(get(g, &w.scope, r.get::<_, &str>(0))
            .await?
            .unwrap_or(Value::Null)),
        None => declare(g, w, d).await,
    }
}

// ---- the loop (0007) --------------------------------------------------------------------

/// W35 (walk #11): a stop ASKED is a stop HELD — every intention whose stop
/// waits at the interlock (the kernel's held `intent.stop`, the code not yet
/// given). The loop files nothing new for these: a cancel resumes them, the
/// code rests them.
pub async fn held_stops(g: &Ground, scope: &str) -> Result<Vec<String>, RoadError> {
    let rows = g
        .client()
        .query(
            "SELECT held::json->'args'->>'intention_id' FROM spine_asks WHERE scope = $1 AND \
             served_by = 'the kernel' AND status = 'awaiting-confirm' AND held::json->>'tool' = \
             'intent.stop'",
            &[&scope],
        )
        .await?;
    Ok(rows
        .iter()
        .filter_map(|r| r.get::<_, Option<String>>(0))
        .collect())
}

/// The active intentions of this world that declared interest in a kind — a
/// stop held at the interlock pauses one (W35).
pub async fn interested(g: &Ground, scope: &str, kind: &str) -> Result<Vec<Value>, RoadError> {
    let held = held_stops(g, scope).await?;
    let rows = g
        .client()
        .query(
            &format!(
                "SELECT {COLS} FROM spine_intentions WHERE scope = $1 AND active ORDER BY added_at"
            ),
            &[&scope],
        )
        .await?;
    Ok(rows
        .iter()
        .map(dict)
        .filter(|d| {
            d["interests"]
                .as_array()
                .is_some_and(|a| a.iter().any(|k| k == kind))
                && !held
                    .iter()
                    .any(|h| h == d["intention_id"].as_str().unwrap_or_default())
        })
        .collect())
}

/// The crew's shape — every body's name and declared capabilities — hashed.
pub async fn crew_hash(g: &Ground, scope: &str) -> Result<String, RoadError> {
    let rows = g
        .client()
        .query(
            "SELECT DISTINCT ON (name) name, capabilities FROM spine_joins WHERE scope = $1 ORDER BY \
             name, join_id DESC",
            &[&scope],
        )
        .await?;
    let shape: Vec<(String, Value)> = rows
        .iter()
        .map(|r| {
            let caps: Option<String> = r.get(1);
            (
                r.get(0),
                json_text(caps.as_deref()).unwrap_or_else(|| json!([])),
            )
        })
        .collect();
    Ok(crew_shape_hash(&shape))
}

/// Is this intention blocked — its runner said it cannot act and the crew has
/// not changed since? A changed crew lifts the block (recorded on the row).
async fn blocked(g: &Ground, scope: &str, intention: &Value) -> Result<bool, RoadError> {
    if intention["blocked"] != json!(true) {
        return Ok(false);
    }
    let iid = intention["intention_id"].as_str().unwrap_or_default();
    let row = g
        .client()
        .query_opt(
            "SELECT blocked_crew FROM spine_intentions WHERE intention_id = $1",
            &[&iid],
        )
        .await?;
    let Some(crew) = row.and_then(|r| r.get::<_, Option<String>>(0)) else {
        return Ok(false);
    };
    if crew == crew_hash(g, scope).await? {
        return Ok(true);
    }
    g.client()
        .execute(
            "UPDATE spine_intentions SET blocked_crew = NULL, blocked_note = NULL WHERE intention_id \
             = $1",
            &[&iid],
        )
        .await?;
    Ok(false)
}

/// The kernel asks the intention's planner — under the observation that woke
/// it (or under the intention itself, on cadence): "the next objective?" One
/// turn per cause, ever; nothing while the intention is blocked (W8).
pub async fn plan(
    g: &mut Ground,
    w: &World,
    intention: &Value,
    cause: Option<&Value>,
    observed: &str,
) -> Result<Value, RoadError> {
    let iid = intention["intention_id"]
        .as_str()
        .unwrap_or_default()
        .to_string();
    if let Some(c) = cause {
        let cid = c["id"].as_str().unwrap_or_default();
        let seen = g
            .client()
            .query_opt(
                "SELECT turn_id FROM spine_intent_turns WHERE cause = $1",
                &[&cid],
            )
            .await?;
        if seen.is_some() {
            return Ok(json!({"planned": false, "intention_id": iid}));
        }
    }
    if blocked(g, &w.scope, intention).await? {
        return Ok(
            json!({"planned": false, "blocked": true, "intention_id": iid,
                         "note": intention["blocked_note"]}),
        );
    }
    let text = plan_words(
        intention["serves"].as_str().unwrap_or_default(),
        intention["words"].as_str().unwrap_or_default(),
        observed,
    );
    let planner = intention["planner"]
        .as_str()
        .unwrap_or("planner")
        .to_string();
    let parent = match cause {
        Some(c) => c["id"].as_str().map(str::to_string),
        None => intention["marker"].as_str().map(str::to_string),
    };
    let filed = crate::asks::submit_ask(
        g,
        w,
        crate::asks::Submit {
            text,
            person: intention["added_by"]
                .as_str()
                .unwrap_or_default()
                .to_string(),
            to: Some(vec![planner.clone()]),
            parent_marker: parent,
            session: intention["session"].as_str().map(str::to_string),
            ..Default::default()
        },
    )
    .await?;
    let aid = filed.ids().into_iter().next().unwrap_or_default();
    let tid = format!("turn_{}", token_hex(5));
    let cause_id = cause.and_then(|c| c["id"].as_str().map(str::to_string));
    let tx = g.client_mut().transaction().await?;
    tx.execute(
        "INSERT INTO spine_intent_turns (turn_id, intention_id, cause, plan_ask) VALUES ($1, $2, $3, $4)",
        &[&tid, &iid, &cause_id, &aid],
    )
    .await?;
    tx.execute(
        "UPDATE spine_intentions SET last_at = now() WHERE intention_id = $1",
        &[&iid],
    )
    .await?;
    tx.commit().await?;
    Ok(
        json!({"planned": true, "turn_id": tid, "intention_id": iid, "planner": planner,
              "plan_ask": aid, "words": intention["words"]}),
    )
}

/// The interest law at intention level: every active intention that cares
/// about this kind plans its next objective under the marker — when the
/// marker already sits under one of them, that one alone.
pub async fn on_marker(
    g: &mut Ground,
    w: &World,
    marker: &Value,
    r#ref: &str,
    note: Option<&str>,
) -> Result<Vec<Value>, RoadError> {
    let kind = marker["kind"].as_str().unwrap_or_default();
    let mut cands = interested(g, &w.scope, kind).await?;
    if cands.is_empty() {
        return Ok(Vec::new());
    }
    if crate::py::truthy(&marker["parent"]) {
        let anc =
            markers_live::ancestry(g, &w.scope, marker["id"].as_str().unwrap_or_default()).await?;
        let root = anc.last().map(|m| m["id"].clone());
        if let Some(root) = root {
            let mine: Vec<Value> = cands
                .iter()
                .filter(|i| i["marker"] == root)
                .cloned()
                .collect();
            if !mine.is_empty() {
                cands = mine;
            }
        }
    }
    let observed = observed_words(kind, r#ref, note);
    let mut out = Vec::new();
    for i in cands {
        let t = plan(g, w, &i, Some(marker), &observed).await?;
        if t["planned"] == json!(true) {
            out.push(t);
        }
    }
    Ok(out)
}

/// A turn to hear: turn · intention · marker · runner · blocked_crew · ask · reply · who.
type Heard = (
    String,
    String,
    String,
    Option<String>,
    Option<String>,
    String,
    Option<String>,
    String,
);
/// A plan to file: turn · intention · added_by · runner · marker · session · reply.
type Pending = (
    String,
    String,
    String,
    Option<String>,
    String,
    Option<String>,
    Option<String>,
);

/// Every objective the crew replied to is heard ONCE (W8): a runner that
/// opened with "cannot act" marks an `improvement` under the intention and
/// blocks it until the crew changes.
async fn hear_runners(g: &mut Ground, w: &World) -> Result<Vec<Value>, RoadError> {
    let rows = g
        .client()
        .query(
            "SELECT t.turn_id, i.intention_id, i.marker, i.runner, i.blocked_crew, a.ask_id, a.reply, \
             coalesce(j.name, i.runner, 'the crew') FROM spine_intent_turns t JOIN spine_intentions i \
             ON i.intention_id = t.intention_id JOIN spine_asks a ON a.ask_id = t.objective_ask LEFT \
             JOIN LATERAL (SELECT name FROM spine_joins WHERE did = a.served_by   ORDER BY join_id \
             DESC LIMIT 1) j ON true WHERE NOT t.heard AND a.status IN ('replied', 'refused') AND \
             i.scope = $1",
            &[&w.scope],
        )
        .await?;
    let heard_rows: Vec<Heard> = rows
        .iter()
        .map(|r| {
            (
                r.get(0),
                r.get(1),
                r.get(2),
                r.get(3),
                r.get(4),
                r.get(5),
                r.get(6),
                r.get(7),
            )
        })
        .collect();
    let mut heard = Vec::new();
    for (tid, iid, marker, _runner, blocked_crew, aid, reply, who) in heard_rows {
        g.client()
            .execute(
                "UPDATE spine_intent_turns SET heard = true WHERE turn_id = $1",
                &[&tid],
            )
            .await?;
        if !cannot_act(reply.as_deref()) {
            continue;
        }
        let note = improvement_note(&who, reply.as_deref());
        if blocked_crew.is_none() {
            let m = markers_live::set_marker(
                g,
                w,
                "improvement",
                &aid,
                crate::ask::KERNEL,
                Some(&marker),
                Some(&note),
                None,
            )
            .await?;
            let crew = crew_hash(g, &w.scope).await?;
            g.client()
                .execute(
                    "UPDATE spine_intentions SET blocked_crew = $1, blocked_note = $2 WHERE \
                     intention_id = $3",
                    &[&crew, &note, &iid],
                )
                .await?;
            heard.push(json!({"intention_id": iid, "objective_ask": aid, "improvement": m["id"]}));
        }
    }
    Ok(heard)
}

/// Cadence: every active intention whose beat came due plans once.
async fn due(g: &mut Ground, w: &World) -> Result<Vec<Value>, RoadError> {
    let rows = g
        .client()
        .query(
            &format!(
                "SELECT {COLS} FROM spine_intentions WHERE scope = $1 AND active AND every_s IS NOT \
                 NULL AND next_at <= now() ORDER BY next_at"
            ),
            &[&w.scope],
        )
        .await?;
    let intentions: Vec<Value> = rows.iter().map(dict).collect();
    let held = held_stops(g, &w.scope).await?; // W35: a held stop pauses the cadence
    let mut out = Vec::new();
    for i in intentions {
        if held
            .iter()
            .any(|h| h == i["intention_id"].as_str().unwrap_or_default())
        {
            continue;
        }
        out.push(plan(g, w, &i, None, CADENCE_DUE).await?);
        let every = i["every_s"].as_i64().unwrap_or(0) as f64;
        g.client()
            .execute(
                "UPDATE spine_intentions SET next_at = now() + make_interval(secs => $1::float8) \
                 WHERE intention_id = $2",
                &[&every, &i["intention_id"].as_str().unwrap_or_default()],
            )
            .await?;
    }
    Ok(out)
}

/// A replied plan becomes the objective: an ask to the crew, the intention as
/// parent, in the intention's session — while it stands.
async fn file_objectives(g: &mut Ground, w: &World) -> Result<Vec<Value>, RoadError> {
    let rows = g
        .client()
        .query(
            "SELECT t.turn_id, i.intention_id, i.added_by, i.runner, i.marker, i.session, a.reply \
             FROM spine_intent_turns t JOIN spine_intentions i ON i.intention_id = t.intention_id \
             JOIN spine_asks a ON a.ask_id = t.plan_ask WHERE t.objective_ask IS NULL AND a.status = \
             'replied' AND i.active AND i.scope = $1",
            &[&w.scope],
        )
        .await?;
    let pending: Vec<Pending> = rows
        .iter()
        .map(|r| {
            (
                r.get(0),
                r.get(1),
                r.get(2),
                r.get(3),
                r.get(4),
                r.get(5),
                r.get(6),
            )
        })
        .collect();
    let held = held_stops(g, &w.scope).await?; // W35: nothing new filed while the code is awaited
    let mut filed = Vec::new();
    for (tid, iid, by, runner, marker, session, reply) in pending {
        if held.contains(&iid) {
            continue;
        }
        let words: String = crate::py::fold_ws(reply.as_deref().unwrap_or(""))
            .chars()
            .take(500)
            .collect();
        if words.is_empty() {
            g.client()
                .execute(
                    "UPDATE spine_intent_turns SET objective_ask = '-' WHERE turn_id = $1",
                    &[&tid],
                )
                .await?;
            continue;
        }
        let out = crate::asks::submit_ask(
            g,
            w,
            crate::asks::Submit {
                text: words,
                person: by,
                to: runner.map(|r| vec![r]),
                parent_marker: Some(marker),
                session,
                ..Default::default()
            },
        )
        .await?;
        let oid = out.ids().into_iter().next().unwrap_or_default();
        g.client()
            .execute(
                "UPDATE spine_intent_turns SET objective_ask = $1 WHERE turn_id = $2",
                &[&oid, &tid],
            )
            .await?;
        filed.push(json!({"turn_id": tid, "intention_id": iid, "objective_ask": oid}));
    }
    Ok(filed)
}

/// The rail's beat: watches judged and the newly red ones observed under
/// every intention that cares (the marker set is a fact; the interest law
/// asks the planner under it); cadences that came due plan; replied plans are
/// filed as objectives; runners heard. The beat is CLAIMED first (the beat
/// lock): the kernel that finds it held returns an empty turn that says so.
pub async fn turn(g: &mut Ground, w: &World) -> Result<Value, RoadError> {
    if !crate::beat::try_beat(g, &w.scope, "intent").await? {
        return Ok(
            json!({"observed": [], "due": [], "filed": [], "heard": [], "beat": crate::beat::HELD}),
        );
    }
    let out = turn_inner(g, w).await;
    let _ = crate::beat::end_beat(g, &w.scope, "intent").await;
    out
}

async fn turn_inner(g: &mut Ground, w: &World) -> Result<Value, RoadError> {
    let mut observed = Vec::new();
    let turned: Vec<Value> = crate::monitor::judge(g, w)
        .await?
        .into_iter()
        .filter(|t| t["to"] == json!("red"))
        .collect();
    for t in turned {
        let note = watch_note(
            t["name"].as_str().unwrap_or_default(),
            t["metric"].as_str().unwrap_or_default(),
            t["op"].as_str().unwrap_or_default(),
            &t["threshold"],
            &t["value"],
        );
        let wid = t["watch_id"].as_str().unwrap_or_default().to_string();
        for i in interested(g, &w.scope, WATCH_RED).await? {
            let m = markers_live::set_marker(
                g,
                w,
                WATCH_RED,
                &wid,
                crate::ask::KERNEL,
                i["marker"].as_str(),
                Some(&note),
                None,
            )
            .await?;
            observed.push(m["id"].clone());
            markers_live::dispatch_interests(g, w, &m, &wid, Some(&note)).await?;
            // → on_marker → the plan
        }
    }
    let due = due(g, w).await?;
    let filed = file_objectives(g, w).await?;
    let heard = hear_runners(g, w).await?; // W8: a runner that cannot act is heard once
    Ok(json!({"observed": observed, "due": due, "filed": filed, "heard": heard}))
}
