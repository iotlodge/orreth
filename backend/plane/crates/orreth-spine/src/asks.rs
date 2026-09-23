// PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp3, the ask road · 2026-09-22
// Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp4, the loops: the APPROVE of a kernel-held act runs intent.stop · intent.restart · 2026-09-23
//! The ask road on the ground — mirrors `orreth_spine.dispatch` (the write
//! half) and the ask views of `orreth_spine.glass`: ONE write path. A human's
//! ask lands on `spine_asks` WITH its marker and its `ask.received` fact in
//! one transaction (`submit_ask`); a fan-out is one ask per named body under
//! one fanout id; a name at the head of the ask selects that body (W7); an
//! ask to a body that is NOT HERE is answered at the door (W19) — its row
//! `refused`, its fact `orreth.ask.refused.v1`, never left in flight; the
//! human's word at the interlock (`confirm_ask`) is judged for the proof the
//! hold demands and rides a command wearing the human's own authority — every
//! refusal the ONE face (rule 4), a cancel ALWAYS taken (rule 11).
//! The columns are the Python spine's (`schema::RESIDENT_DDL`), the words the
//! fixtures' (`askroad-v0.json` · `ask-v0.json`).

use crate::ask::{address, ask_fact, received_payload, refusal_words, refused_payload};
pub use crate::ask::{ASK_RECEIVED, ASK_REFUSED};
use crate::envelope::{self, Mint};
use crate::ground::Ground;
use crate::hash::content_hash;
use crate::markers_live::{self, INCLUDES};
use crate::proof::KERNEL;
use crate::proof_live;
use crate::schema::has_table;
use crate::world::{head, iso_opt, isoformat, json_text, refused, token_hex, RoadError, World};
use crate::{invoke, outbox, watch};
use serde_json::{json, Value};
use std::collections::HashMap;
use std::time::SystemTime;
use tokio_postgres::Transaction;

pub const JOURNEY: &str = "orreth.journey.v1";
pub const REPLY: &str = "orreth.reply.v1";
pub const CONFIRM_NEEDED: &str = "orreth.confirm.needed.v1";
pub const CONFIRM_CMD: &str = "orreth.resident.confirm.v1";
pub const SERVE_CMD: &str = "orreth.resident.serve.v1";
pub use crate::ask::HARNESS_FAILED;
pub use crate::watch::WATCH_TURNED;

/// The topics the Bridge feed reads — `glass.FEED_TOPICS`, in order.
pub const FEED_TOPICS: [&str; 8] = [
    ASK_RECEIVED,
    JOURNEY,
    REPLY,
    CONFIRM_NEEDED,
    HARNESS_FAILED,
    markers_live::MARKER_SET,
    ASK_REFUSED,
    WATCH_TURNED,
];

// ---- the fact, minted now ------------------------------------------------------------

/// `msg_` + twelve random bytes — `make_envelope`'s id for an event.
fn new_message_id() -> String {
    format!("msg_{}", token_hex(12))
}

/// `ask::ask_fact` with the id and the clock minted now.
fn fact_now(
    typ: &str,
    scope: &str,
    ask_id: &str,
    payload: Value,
    fanout: Option<&str>,
    chain: &[&str],
    marker: &Value,
) -> Value {
    ask_fact(
        typ,
        scope,
        ask_id,
        payload,
        fanout,
        chain,
        marker,
        &new_message_id(),
        &envelope::now_iso(),
    )
}

/// A committed `ask.received` becomes a serve command — `dispatch._command_for`.
pub fn command_for(event: &Value) -> Result<Value, RoadError> {
    let s = |k: &str| {
        event
            .get(k)
            .and_then(Value::as_str)
            .unwrap_or_default()
            .to_string()
    };
    Ok(Mint {
        kind: "command".into(),
        r#type: SERVE_CMD.into(),
        universe_id: s("universe_id"),
        scope_path: s("scope_path"),
        payload: event.get("payload").cloned().unwrap_or(json!({})),
        correlation_id: event
            .get("correlation_id")
            .and_then(Value::as_str)
            .map(str::to_string),
        authority_chain: event
            .get("authority_chain")
            .and_then(Value::as_array)
            .map(|a| a.iter().map(crate::py::python_str).collect()),
        ..Default::default()
    }
    .mint()?)
}

// ---- who is here ----------------------------------------------------------------------

/// A body the ground could not seat — `placement.refusals`' row.
#[derive(Debug, Clone)]
pub struct Refusal {
    pub name: String,
    pub did: String,
    pub kind: String,
    pub template: String,
    pub placement: Value,
    pub ground: Value,
    pub reasons: Vec<String>,
    pub marker: Option<String>,
    pub refused_at: SystemTime,
}

/// The latest refusal per body name in this world (none when the Python
/// spine never made the table).
pub async fn refusals(g: &Ground, scope: &str) -> Result<HashMap<String, Refusal>, RoadError> {
    if !has_table(g, "spine_refusals").await? {
        return Ok(HashMap::new());
    }
    let rows = g
        .client()
        .query(
            "SELECT DISTINCT ON (name) name, did, kind, template_hash, placement, ground, \
             reasons, marker, refused_at FROM spine_refusals WHERE scope = $1 ORDER BY name, \
             refusal_id DESC",
            &[&scope],
        )
        .await?;
    Ok(rows
        .iter()
        .map(|r| {
            let name: String = r.get(0);
            let reasons: Vec<String> =
                crate::world::json_strings(r.get::<_, Option<String>>(6).as_deref());
            (
                name.clone(),
                Refusal {
                    name,
                    did: r.get(1),
                    kind: r.get(2),
                    template: r.get(3),
                    placement: json_text(r.get::<_, Option<String>>(4).as_deref())
                        .unwrap_or(json!({})),
                    ground: json_text(r.get::<_, Option<String>>(5).as_deref())
                        .unwrap_or(json!({})),
                    reasons,
                    marker: r.get(7),
                    refused_at: r.get(8),
                },
            )
        })
        .collect())
}

/// Is the body named here to serve? `None` when it is (a join row in this
/// world, not refused since); else the reason in words (W19).
pub async fn absent(g: &Ground, scope: &str, name: &str) -> Result<Option<String>, RoadError> {
    let joined: Option<SystemTime> = g
        .client()
        .query_one(
            "SELECT max(joined_at) FROM spine_joins WHERE name = $1 AND scope = $2",
            &[&name, &scope],
        )
        .await?
        .get(0);
    if let Some(r) = refusals(g, scope).await?.get(name) {
        if joined.is_none_or(|j| r.refused_at > j) {
            return Ok(Some(format!(
                "refused at birth: {}; fix its template to seat it",
                r.reasons.join("; ")
            )));
        }
    }
    if joined.is_none() {
        return Ok(Some("no body of that name has joined this world".into()));
    }
    Ok(None)
}

/// The names that ever joined this world.
pub async fn names_here(g: &Ground, scope: &str) -> Result<Vec<String>, RoadError> {
    let rows = g
        .client()
        .query(
            "SELECT DISTINCT name FROM spine_joins WHERE scope = $1",
            &[&scope],
        )
        .await?;
    Ok(rows.iter().map(|r| r.get(0)).collect())
}

/// W7: a name at the head of the ask selects THAT body alone — when it is a
/// body of this world; the fan-out stays for an unaddressed ask.
pub async fn address_to(
    g: &Ground,
    scope: &str,
    text: &str,
    to: Option<Vec<String>>,
) -> Result<Option<Vec<String>>, RoadError> {
    let names = names_here(g, scope).await?;
    Ok(match address(text, &names) {
        Some(who) => Some(vec![who]),
        None => to,
    })
}

// ---- the write --------------------------------------------------------------------------

/// What the door hands `submit_ask`.
#[derive(Debug, Clone, Default)]
pub struct Submit {
    pub text: String,
    pub person: String,
    pub to: Option<Vec<String>>,
    pub window: Option<(String, String)>,
    pub session: Option<String>,
    pub parent_marker: Option<String>,
    pub kind: Option<String>,
    pub zone: Option<String>,
}

/// One id for an untargeted ask, the list for a fan-out.
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum Submitted {
    One(String),
    Many(Vec<String>),
}

impl Submitted {
    /// The door's reply body: `{"id": …}` or `{"ids": […]}`.
    pub fn to_value(&self) -> Value {
        match self {
            Submitted::One(id) => json!({"id": id}),
            Submitted::Many(ids) => json!({"ids": ids}),
        }
    }
    pub fn ids(&self) -> Vec<String> {
        match self {
            Submitted::One(id) => vec![id.clone()],
            Submitted::Many(ids) => ids.clone(),
        }
    }
}

/// The glass's write: the ask row and its committed event, one transaction
/// — `dispatch.submit_ask`, law for law.
pub async fn submit_ask(g: &mut Ground, w: &World, s: Submit) -> Result<Submitted, RoadError> {
    let fanout = match &s.to {
        Some(to) if to.len() > 1 => Some(format!("fan_{}", token_hex(6))),
        _ => None,
    };
    let mut state = "in".to_string();
    if let Some(session) = &s.session {
        if let Some(r) = g
            .client()
            .query_opt(
                "SELECT coalesce(state, 'in') FROM spine_sessions WHERE session_id = $1",
                &[session],
            )
            .await?
        {
            state = r.get(0);
        }
    }
    if !matches!(
        s.kind.as_deref(),
        None | Some("thought") | Some("objective")
    ) {
        return Err(refused(
            "an ask is a thought or an objective — an intention is declared",
        ));
    }
    let targets: Vec<Option<String>> = match &s.to {
        Some(to) => to.iter().cloned().map(Some).collect(),
        None => vec![None],
    };
    let mut ids = Vec::new();
    for target in targets {
        let ask_id = format!("ask_{}", token_hex(8));
        let mut ask_kind = s.kind.clone().unwrap_or_else(|| "objective".into());
        let mut parent = s.parent_marker.clone();
        if target.as_deref().is_some_and(|t| INCLUDES.contains(&t)) || ask_kind == "thought" {
            ask_kind = "thought".into();
            if parent.is_none() {
                if let Some(session) = &s.session {
                    parent = g
                        .client()
                        .query_opt(
                            "SELECT a.marker FROM spine_asks a JOIN spine_markers m ON m.marker_id \
                             = a.marker WHERE a.session = $1 AND m.kind = 'objective' ORDER BY \
                             a.asked_at DESC LIMIT 1",
                            &[session],
                        )
                        .await?
                        .and_then(|r| r.get(0));
                }
            }
        }
        let marker_id = markers_live::new_id();
        let marker = json!({"kind": ask_kind, "id": marker_id, "parent": parent, "by": s.person});
        let why = match &target {
            Some(t) => absent(g, &w.scope, t).await?,
            None => None,
        };
        if let (Some(t), Some(why)) = (&target, why) {
            ids.push(
                refuse_at_door(
                    g,
                    w,
                    &ask_id,
                    &s.text,
                    &s.person,
                    t,
                    &why,
                    &marker,
                    fanout.as_deref(),
                    s.session.as_deref(),
                    &state,
                )
                .await?,
            );
            continue;
        }
        let payload = received_payload(
            &ask_id,
            &s.text,
            target.as_deref(),
            s.session.as_deref(),
            s.window.as_ref().map(|(f, t)| (f.as_str(), t.as_str())),
        );
        let window_text = payload.get("window").map(|w| w.to_string());
        let e = fact_now(
            ASK_RECEIVED,
            &w.scope,
            &ask_id,
            payload,
            fanout.as_deref(),
            &[&s.person],
            &marker,
        );
        let raw = envelope::encode(&e)?;
        let mid = e["message_id"].as_str().unwrap_or_default().to_string();
        let (a, text, person, t, fo, sc, ses, st, mk, kd, pa, zone) = (
            ask_id.clone(),
            s.text.clone(),
            s.person.clone(),
            target.clone(),
            fanout.clone(),
            w.scope.clone(),
            s.session.clone(),
            state.clone(),
            marker_id.clone(),
            ask_kind.clone(),
            parent.clone(),
            s.zone.clone().filter(|z| !z.is_empty()),
        );
        outbox::commit_with_outbox(g, &raw, &mid, None, async move |tx| {
            markers_live::insert(tx, &mk, &kd, pa.as_deref(), &a, &person, None, &sc)
                .await
                .map_err(rail)?;
            tx.execute(
                "INSERT INTO spine_asks (ask_id, text, person, target, fanout, scope, \
                 time_window, session, state, marker, zone) VALUES ($1, $2, $3, $4, $5, $6, $7, \
                 $8, $9, $10, $11)",
                &[
                    &a,
                    &text,
                    &person,
                    &t,
                    &fo,
                    &sc,
                    &window_text,
                    &ses,
                    &st,
                    &mk,
                    &zone,
                ],
            )
            .await?;
            Ok(())
        })
        .await?;
        ids.push(ask_id);
    }
    Ok(if s.to.is_some() {
        Submitted::Many(ids)
    } else {
        Submitted::One(ids.remove(0))
    })
}

/// A road refusal inside an outbox transaction is a rail refusal.
fn rail(e: RoadError) -> crate::rail_error::RailError {
    match e {
        RoadError::Rail(r) => r,
        other => crate::rail_error::RailError::Refused(other.to_string()),
    }
}

/// The refused ask: its row (status `refused`, the reply, the kernel as
/// server, replied at the landing) and its fact in one transaction — wearing
/// the marker the ask would have worn.
#[allow(clippy::too_many_arguments)]
async fn refuse_at_door(
    g: &mut Ground,
    w: &World,
    ask_id: &str,
    text: &str,
    person: &str,
    target: &str,
    why: &str,
    marker: &Value,
    fanout: Option<&str>,
    session: Option<&str>,
    state: &str,
) -> Result<String, RoadError> {
    let reply = refusal_words(target, why);
    let payload = refused_payload(ask_id, text, target, why, session);
    let e = fact_now(
        ASK_REFUSED,
        &w.scope,
        ask_id,
        payload,
        fanout,
        &[person, KERNEL],
        marker,
    );
    let raw = envelope::encode(&e)?;
    let mid = e["message_id"].as_str().unwrap_or_default().to_string();
    let (a, tx_text, p, t, fo, sc, ses, st, r) = (
        ask_id.to_string(),
        text.to_string(),
        person.to_string(),
        target.to_string(),
        fanout.map(str::to_string),
        w.scope.clone(),
        session.map(str::to_string),
        state.to_string(),
        reply.clone(),
    );
    let (mk, kd, pa) = (
        marker["id"].as_str().unwrap_or_default().to_string(),
        marker["kind"].as_str().unwrap_or_default().to_string(),
        marker["parent"].as_str().map(str::to_string),
    );
    outbox::commit_with_outbox(g, &raw, &mid, None, async move |tx| {
        markers_live::insert(tx, &mk, &kd, pa.as_deref(), &a, &p, None, &sc)
            .await
            .map_err(rail)?;
        tx.execute(
            "INSERT INTO spine_asks (ask_id, text, person, target, fanout, scope, session, state, \
             marker, status, reply, served_by, replied_at) VALUES ($1, $2, $3, $4, $5, $6, $7, \
             $8, $9, 'refused', $10, $11, clock_timestamp())",
            &[&a, &tx_text, &p, &t, &fo, &sc, &ses, &st, &mk, &r, &KERNEL],
        )
        .await?;
        Ok(())
    })
    .await?;
    Ok(ask_id.to_string())
}

// ---- the interlock ---------------------------------------------------------------------

/// The ask's own event counter — monotone per aggregate, durable on the row.
pub async fn next_seq(tx: &Transaction<'_>, ask_id: &str) -> Result<i64, RoadError> {
    let r = tx
        .query_one(
            "UPDATE spine_asks SET seq = seq + 1 WHERE ask_id = $1 RETURNING seq",
            &[&ask_id],
        )
        .await?;
    Ok(r.get::<_, i32>(0) as i64)
}

/// The human's word at the interlock — `dispatch.confirm_ask`, law for law:
/// only an explicit approve releases the act; a cancel is ALWAYS taken; a
/// BODY never confirms; every refusal is the one face; the third wrong
/// proof rests the act. The decision rides a command wearing the human's
/// own authority; an act the kernel holds itself is settled on the ground.
pub async fn confirm_ask(
    g: &mut Ground,
    w: &World,
    ask_id: &str,
    approve: bool,
    person: &str,
    code: Option<&str>,
) -> Result<Value, RoadError> {
    let body = g
        .client()
        .query_opt(
            "SELECT 1 FROM spine_joins WHERE did = $1 LIMIT 1",
            &[&person],
        )
        .await?;
    if body.is_some() {
        return Err(RoadError::NotConfirmed { rest: false });
    }
    let row = g
        .client()
        .query_opt(
            "SELECT target, served_by, held, person, status FROM spine_asks WHERE ask_id = $1 \
             AND scope = $2",
            &[&ask_id, &w.scope],
        )
        .await?;
    let held_row = row.as_ref().map(|r| Held {
        target: r.get(0),
        served_by: r.get(1),
        held: json_text(r.get::<_, Option<String>>(2).as_deref()).unwrap_or(json!({})),
        person: r.get(3),
        status: r.get(4),
    });
    let mut held = held_row
        .as_ref()
        .map(|h| h.held.clone())
        .unwrap_or(json!({}));
    let level = held["level"]
        .as_str()
        .filter(|l| !l.is_empty())
        .unwrap_or("L2")
        .to_string();
    if approve {
        let Some(h) = &held_row else {
            return Err(RoadError::NotConfirmed { rest: false });
        };
        if h.status != "awaiting-confirm" {
            return Err(RoadError::NotConfirmed { rest: false });
        }
        if level == "L3-master"
            && held["needs_code"].as_bool() == Some(true)
            && held["code_ok"].as_bool() != Some(true)
        {
            if person != h.person {
                return Err(RoadError::NotConfirmed { rest: false });
            }
            if let Err(e) =
                proof_live::judge(g, w, ask_id, "L3-code", &h.person, person, code).await
            {
                if let RoadError::NotConfirmed { rest: true } = e {
                    settle(
                        g,
                        w,
                        h,
                        ask_id,
                        false,
                        person,
                        &level,
                        Some("three wrong proofs — the kernel rested this act"),
                    )
                    .await?;
                }
                return Err(e);
            }
            held["code_ok"] = json!(true);
            g.client()
                .execute(
                    "UPDATE spine_asks SET held = $1 WHERE ask_id = $2",
                    &[&held.to_string(), &ask_id],
                )
                .await?;
            return Ok(
                json!({"id": ask_id, "approve": true, "level": level, "step": "code", "next": "master"}),
            );
        }
        if let Err(e) = proof_live::judge(g, w, ask_id, &level, &h.person, person, code).await {
            if let RoadError::NotConfirmed { rest: true } = e {
                settle(
                    g,
                    w,
                    h,
                    ask_id,
                    false,
                    person,
                    &level,
                    Some("three wrong proofs — the kernel rested this act"),
                )
                .await?;
            }
            return Err(e);
        }
    }
    match &held_row {
        Some(h) => settle(g, w, h, ask_id, approve, person, &level, None).await?,
        None => settle_command(g, w, None, ask_id, approve, person, &level, None).await?,
    }
    Ok(json!({"id": ask_id, "approve": approve, "level": level}))
}

/// The held row's columns the interlock reads.
#[derive(Debug, Clone)]
pub struct Held {
    pub target: Option<String>,
    pub served_by: Option<String>,
    pub held: Value,
    pub person: String,
    pub status: String,
}

#[allow(clippy::too_many_arguments)]
async fn settle(
    g: &mut Ground,
    w: &World,
    h: &Held,
    ask_id: &str,
    approve: bool,
    person: &str,
    level: &str,
    reason: Option<&str>,
) -> Result<(), RoadError> {
    if h.served_by.as_deref() == Some(KERNEL) {
        settle_kernel_act(g, w, ask_id, approve, person, Some(level), reason).await?;
        return Ok(());
    }
    settle_command(g, w, Some(h), ask_id, approve, person, level, reason).await
}

/// The decision rides a `resident.confirm` command on the invoke rail,
/// wearing the human's own authority, to the holder's own bench.
#[allow(clippy::too_many_arguments)]
async fn settle_command(
    g: &Ground,
    w: &World,
    h: Option<&Held>,
    ask_id: &str,
    approve: bool,
    person: &str,
    level: &str,
    reason: Option<&str>,
) -> Result<(), RoadError> {
    let mut payload = json!({"ref": ask_id, "hash": "sha256:-", "approved": approve, "proof": level, "by": person});
    if let Some(r) = reason {
        payload["reason"] = json!(r);
    }
    if let Some(h) = h {
        let mut target = h.target.clone();
        if target.is_none() {
            if let Some(did) = &h.served_by {
                target = g
                    .client()
                    .query_opt(
                        "SELECT name FROM spine_joins WHERE did = $1 ORDER BY join_id DESC LIMIT 1",
                        &[did],
                    )
                    .await?
                    .map(|r| r.get(0));
            }
        }
        if let Some(t) = target {
            payload["target"] = json!(t);
        }
    }
    let e = Mint {
        kind: "command".into(),
        r#type: CONFIRM_CMD.into(),
        universe_id: w.scope.clone(),
        scope_path: w.scope.clone(),
        payload,
        correlation_id: Some(ask_id.to_string()),
        authority_chain: Some(vec![person.to_string()]),
        ..Default::default()
    }
    .mint()?;
    invoke::publish_command(&w.rabbit_url, &e, &w.ns).await?;
    Ok(())
}

/// The kernel settles its own held act after the door judged the proof: yes
/// → the held act runs (`intent.stop` · `intent.restart`, in the SAME
/// transaction as the record) and the record wears its level; anything else →
/// a recorded cancel, the act never ran (rule 11). `service.retire` is the
/// Python organ's until the bodies' seam — named (501), never silent.
pub async fn settle_kernel_act(
    g: &mut Ground,
    w: &World,
    ask_id: &str,
    approve: bool,
    by: &str,
    level: Option<&str>,
    reason: Option<&str>,
) -> Result<Value, RoadError> {
    let tx = g.client_mut().transaction().await?;
    let row = tx
        .query_opt(
            "SELECT status, held, person, marker FROM spine_asks WHERE ask_id = $1 AND served_by \
             = $2 FOR UPDATE",
            &[&ask_id, &KERNEL],
        )
        .await?;
    let Some(row) = row else {
        return Err(RoadError::NotConfirmed { rest: false });
    };
    let status: String = row.get(0);
    let held = json_text(row.get::<_, Option<String>>(1).as_deref());
    let asker: String = row.get(2);
    let marker_id: Option<String> = row.get(3);
    let (Some(held), true) = (held, status == "awaiting-confirm") else {
        return Err(RoadError::NotConfirmed { rest: false });
    };
    let level = level
        .map(str::to_string)
        .or_else(|| held["level"].as_str().map(str::to_string))
        .unwrap_or_else(|| "L3-master".into());
    let marker = match &marker_id {
        Some(id) => tx
            .query_opt(
                "SELECT kind, marker_id, parent, by_did FROM spine_markers WHERE marker_id = $1 AND scope = $2",
                &[id, &w.scope],
            )
            .await?
            .map(|r| json!({"kind": r.get::<_, String>(0), "id": r.get::<_, String>(1), "parent": r.get::<_, Option<String>>(2), "by": r.get::<_, String>(3)})),
        None => None,
    };
    let chain: Vec<String> = if by != asker {
        vec![asker.clone(), by.to_string(), KERNEL.to_string()]
    } else {
        vec![asker.clone(), KERNEL.to_string()]
    };
    let tool = held["tool"].as_str().unwrap_or_default().to_string();
    let (note, reply, status, proof): (String, String, &str, String) = if approve {
        let iid = held["args"]["intention_id"]
            .as_str()
            .unwrap_or_default()
            .to_string();
        let result = match tool.as_str() {
            "intent.stop" | "intent.restart" => {
                let made = crate::intent_live::stop_or_restart_in(
                    &tx,
                    w,
                    &iid,
                    &asker,
                    Some(&level),
                    Some(by),
                    tool == "intent.restart",
                )
                .await?
                .ok_or(RoadError::NotConfirmed { rest: false })?;
                let words = made["words"].as_str().unwrap_or_default();
                if tool == "intent.stop" {
                    format!("the intention “{words}” is at rest — recorded, never deleted")
                } else {
                    format!("the intention “{words}” stands again — its stop stays in the record, its history whole")
                }
            }
            "service.retire" => return Err(RoadError::NotYet(
                "the kernel's service.retire settles at the Python door until the bodies' seam \
                     (P7 sp6) — cancel is taken here, always"
                    .into(),
            )),
            _ => return Err(RoadError::NotConfirmed { rest: false }),
        };
        let (n, r) = match level.as_str() {
            "L2" => (
                format!("the human said yes — the {tool} act ran · proof {level}"),
                format!("Done, on your word: {result}."),
            ),
            "L3-code" => (
                format!("the code was right — the {tool} act ran · proof {level}"),
                format!("Done, on your code: {result}."),
            ),
            _ => {
                let word = if crate::py::truthy(&held["needs_code"]) {
                    " after the asker's code"
                } else {
                    ""
                };
                (
                    format!("{by} confirmed as master{word} — the {tool} act ran · proof {level}"),
                    format!(
                        "Done, on {}'s word as master{word}: {result}.",
                        by.rsplit(':').next().unwrap_or(by)
                    ),
                )
            }
        };
        (format!("{KERNEL}: {n}"), r, "replied", level.clone())
    } else {
        let why = reason.unwrap_or("the human cancelled");
        let r = if reason.is_some() {
            "Rested — three wrong proofs were given, so nothing was done. The act is at rest, \
             recorded; ask again when you are ready."
        } else {
            "Cancelled — nothing was done. Cancel is always the default here."
        };
        (
            format!("{KERNEL}: {why} — the {tool} act never ran (cancel is always the default)"),
            r.to_string(),
            "cancelled",
            "L1".to_string(),
        )
    };
    let seq = next_seq(&tx, ask_id).await?;
    let j = Mint {
        kind: "event".into(),
        r#type: JOURNEY.into(),
        universe_id: w.scope.clone(),
        scope_path: w.scope.clone(),
        payload: json!({"ref": ask_id, "hash": "sha256:-", "note": note}),
        correlation_id: Some(ask_id.to_string()),
        authority_chain: Some(chain.clone()),
        aggregate: Some(json!({"type": "ask", "id": ask_id, "sequence": seq})),
        marker: marker.clone(),
    }
    .mint()?;
    outbox::add_row(
        &tx,
        &envelope::encode(&j)?,
        j["message_id"].as_str().unwrap_or_default(),
    )
    .await?;
    tx.execute(
        "UPDATE spine_asks SET status = $1, reply = $2, proof = $3, replied_at = clock_timestamp() \
         WHERE ask_id = $4",
        &[&status, &reply, &proof, &ask_id],
    )
    .await?;
    let seq = next_seq(&tx, ask_id).await?;
    let r = Mint {
        kind: "event".into(),
        r#type: REPLY.into(),
        universe_id: w.scope.clone(),
        scope_path: w.scope.clone(),
        payload: json!({"ref": ask_id, "hash": content_hash(&Value::String(reply.clone())), "proof": proof}),
        correlation_id: Some(ask_id.to_string()),
        authority_chain: Some(chain),
        aggregate: Some(json!({"type": "ask", "id": ask_id, "sequence": seq})),
        marker,
    }
    .mint()?;
    outbox::add_row(
        &tx,
        &envelope::encode(&r)?,
        r["message_id"].as_str().unwrap_or_default(),
    )
    .await?;
    tx.commit().await?;
    Ok(json!({"ask_id": ask_id, "status": status, "proof": proof, "reply": reply}))
}

// ---- the views --------------------------------------------------------------------------

async fn name_of(g: &Ground, scope: &str, did: Option<&str>) -> Result<Option<String>, RoadError> {
    let Some(did) = did.filter(|d| d.starts_with("did:")) else {
        return Ok(None);
    };
    Ok(g.client()
        .query_opt(
            "SELECT name FROM spine_joins WHERE did = $1 AND scope = $2 ORDER BY join_id DESC LIMIT 1",
            &[&did, &scope],
        )
        .await?
        .map(|r| r.get(0)))
}

/// The Questions door: the ask row plus its journey notes, read from the
/// ground — `glass.ask_view`, field for field. Another world's ask is "no
/// such ask" here (rule 4).
pub async fn ask_view(g: &Ground, scope: &str, ask_id: &str) -> Result<Option<Value>, RoadError> {
    let row = g
        .client()
        .query_opt(
            "SELECT text, person, status, reply, served_by, target, scope, asked_at, replied_at, \
             time_window, session, marker, proof, held FROM spine_asks WHERE ask_id = $1 AND \
             scope = $2",
            &[&ask_id, &scope],
        )
        .await?;
    let Some(row) = row else {
        return Ok(None);
    };
    let status: String = row.get(2);
    let reply: Option<String> = row.get(3);
    let served_by: Option<String> = row.get(4);
    let target: Option<String> = row.get(5);
    let marker: Option<String> = row.get(11);
    let mut origin = Value::Null;
    if let Some(mk) = &marker {
        let r0 = g
            .client()
            .query_opt(
                "SELECT r.marker_id, r.kind, r.parent, r.ref, r.by_did, r.note, r.at, 0 FROM \
                 spine_markers m JOIN spine_markers r ON r.marker_id = m.root WHERE m.marker_id = $1",
                &[mk],
            )
            .await?;
        if let Some(r0) = r0 {
            if r0.get::<_, String>(0) != *mk {
                let rows = markers_live::with_words(g, vec![markers_live::row_of(&r0)]).await?;
                let o = &rows[0];
                let words = if o["words"].is_null() {
                    o["note"].clone()
                } else {
                    o["words"].clone()
                };
                origin = json!({"marker": o["id"], "kind": o["kind"], "ref": o["ref"], "by": o["by"], "words": words});
            }
        }
    }
    let bodies = g
        .client()
        .query(
            "SELECT body FROM spine_outbox WHERE convert_from(body, 'UTF8') LIKE $1 ORDER BY outbox_id",
            &[&format!("%{ask_id}%")],
        )
        .await?;
    let mut journey = Vec::new();
    for b in &bodies {
        let body: Vec<u8> = b.get(0);
        if let Ok(e) = envelope::decode(&body) {
            if e["type"].as_str() == Some(JOURNEY) {
                let note = e["payload"]["note"].as_str().unwrap_or_default();
                if !note.is_empty() {
                    journey.push(note.to_string());
                }
            }
        }
    }
    let mut offer = Value::Null;
    if status == "replied" && reply.as_deref().is_some_and(|r| !r.is_empty()) {
        let by_monitor = target.as_deref() == Some("monitor")
            || name_of(g, scope, served_by.as_deref()).await?.as_deref() == Some("monitor");
        if by_monitor {
            offer = watch::offer_in(reply.as_deref())
                .map(|o| o.to_value())
                .unwrap_or(Value::Null);
        }
    }
    let held = json_text(row.get::<_, Option<String>>(13).as_deref());
    let hold = match (&status[..], held) {
        ("awaiting-confirm", Some(h)) if h.as_object().is_some_and(|o| !o.is_empty()) => {
            let mut v = json!({
                "tool": h["tool"],
                "class": if h["class"].is_null() { json!("consequential") } else { h["class"].clone() },
                "level": if h["level"].is_null() { json!("L2") } else { h["level"].clone() },
            });
            if h["needs_code"].as_bool() == Some(true) {
                v["needs_code"] = json!(true);
                v["code_ok"] = json!(h["code_ok"].as_bool() == Some(true));
            }
            v
        }
        _ => Value::Null,
    };
    let proof: Option<String> = row.get(12);
    Ok(Some(json!({
        "ask_id": ask_id, "text": row.get::<_, String>(0), "person": row.get::<_, String>(1),
        "status": status, "reply": reply, "served_by": served_by,
        "offer": offer, "target": target, "scope": row.get::<_, Option<String>>(6),
        "asked_at": isoformat(row.get::<_, SystemTime>(7)),
        "replied_at": iso_opt(row.get::<_, Option<SystemTime>>(8)),
        "window": json_text(row.get::<_, Option<String>>(9).as_deref()),
        "session": row.get::<_, Option<String>>(10),
        "marker": marker, "origin": origin,
        "proof": proof.filter(|p| !p.is_empty()).unwrap_or_else(|| "L1".into()),
        "hold": hold, "journey": journey,
    })))
}

/// The Objectives band's door: everything running, everything run — newest first.
pub async fn asks_view(g: &Ground, scope: &str, limit: i64) -> Result<Vec<Value>, RoadError> {
    let rows = g
        .client()
        .query(
            "SELECT ask_id, text, person, status, served_by, target, fanout, asked_at, replied_at \
             FROM spine_asks WHERE scope = $1 ORDER BY asked_at DESC LIMIT $2",
            &[&scope, &limit],
        )
        .await?;
    Ok(rows
        .iter()
        .map(|r| {
            json!({
                "ask_id": r.get::<_, String>(0), "text": head(&r.get::<_, String>(1), 140),
                "person": r.get::<_, String>(2), "status": r.get::<_, String>(3),
                "served_by": r.get::<_, Option<String>>(4), "target": r.get::<_, Option<String>>(5),
                "fanout": r.get::<_, Option<String>>(6),
                "asked_at": isoformat(r.get::<_, SystemTime>(7)),
                "replied_at": iso_opt(r.get::<_, Option<SystemTime>>(8)),
            })
        })
        .collect())
}
