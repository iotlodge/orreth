// PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch Phase 8 THE WORKSHOP sp4, THE EXPERIMENT AND THE CUT: the ground half · 2026-10-07
//! THE EXPERIMENT AND THE CUT on the ground — `orreth_spine.experiments` ported (canon 0010 §5 ·
//! 0005 Phase 8 sp4), schema 7: `spine_experiments` (an agent's candidate against its standing
//! version, in an experiment room on the path; its arms, its reviewers, its proposal),
//! `spine_verdicts` (a reviewer's SIGNED verdict — written by the reviewer body itself, this kernel
//! reads it) and `spine_body_seats` (where a promoted agent's life stands, and its rung on the
//! decom ladder). An agent's cut OPENS the Experiment (`experiment.open`, L2): the room row and its
//! fact, the experiment row, its marker. THE EXPERIMENT BEAT drives it: the candidate's trial life
//! spawned (`body --experiment`), the current arm's run asked of the standing body over the rail,
//! the runs read as they land, the grader and the critic asked under the experiment's marker, their
//! verdicts read, the proposal composed. Promotion is the human's stamped act (`experiment.promote`):
//! the sibling version onto the shelf, the draft spent, the seat written, the body's next life.
//! The ladder: `body.rest` (L2) · `body.decommission` (L3 — the live objects removed, the self and
//! the record kept) · `body.restore` (L2 — a new life). THE PRUNE BEAT retires the crafts nobody wears.

use crate::experiments::{
    self, ACT_CLASS, BODY_DECOMMISSIONED, BODY_RESTED, BODY_RESTORED, DECOM_LEVEL, DECOM_TOOL, EXPERIMENT_OPENED,
    EXPERIMENT_PROPOSED, EXPERIMENT_SETTLED, KERNEL, MARKER_KIND, OPEN_LEVEL, OPEN_TOOL, PROMOTE_TOOL, RESTORE_LEVEL,
    RESTORE_TOOL, REST_LEVEL, REST_TOOL, REVIEW_WAIT_S,
};
use crate::ground::Ground;
use crate::py::{python_str, truthy};
use crate::world::{isoformat, json_text, refused, RoadError, World};
use serde_json::{json, Value};
use std::sync::Mutex;

/// The spine home the shipped crafts are read from (`ORRETH_SPINE`, else beside the crate).
fn spine_dir() -> std::path::PathBuf {
    crate::tools::spine_dir()
}
use std::time::SystemTime;
use tokio_postgres::{GenericClient, Transaction};

const COLS: &str = "experiment_id, scope, person, draft_id, agent, template, current_version, candidate, candidate_hash, \
                    golden, room, state, arms, reviewers, resiliency, proposal, leaning, ask, marker, opened_at, \
                    proposed_at, settled_at, settled_by, at_path, claims, diff"; // claims · diff: Phase 8 sp6, the chips' evidence

fn row_of(r: &tokio_postgres::Row) -> Value {
    let t = |i: usize| r.get::<_, Option<SystemTime>>(i).map(isoformat);
    json!({
        "experiment_id": r.get::<_, String>(0), "scope": r.get::<_, String>(1), "person": r.get::<_, String>(2),
        "draft_id": r.get::<_, String>(3), "agent": r.get::<_, String>(4), "template": r.get::<_, String>(5),
        "current_version": r.get::<_, Option<i32>>(6), "candidate": json_text(Some(&r.get::<_, String>(7))),
        "candidate_hash": r.get::<_, String>(8), "golden": r.get::<_, String>(9), "room": r.get::<_, String>(10),
        "state": r.get::<_, String>(11), "arms": json_text(Some(&r.get::<_, String>(12))),
        "reviewers": json_text(Some(&r.get::<_, String>(13))), "resiliency": json_text(r.get::<_, Option<String>>(14).as_deref()),
        "proposal": r.get::<_, Option<String>>(15), "leaning": r.get::<_, Option<String>>(16),
        "ask": r.get::<_, Option<String>>(17), "marker": r.get::<_, Option<String>>(18),
        "opened_at": t(19), "proposed_at": t(20), "settled_at": t(21), "settled_by": r.get::<_, Option<String>>(22),
        "at_path": r.get::<_, Option<String>>(23),
        "claims": json_text(r.get::<_, Option<String>>(24).as_deref()), "diff": json_text(r.get::<_, Option<String>>(25).as_deref()),
    })
}

pub async fn get<C: GenericClient>(c: &C, experiment_id: &str) -> Result<Option<Value>, RoadError> {
    Ok(c
        .query_opt(&format!("SELECT {COLS} FROM spine_experiments WHERE experiment_id = $1"), &[&experiment_id])
        .await?
        .as_ref()
        .map(row_of))
}

/// The experiments of this universe, newest first; the candidate's declaration left out of the listing.
pub async fn listing<C: GenericClient>(c: &C, scope: &str, agent: Option<&str>, state: Option<&str>) -> Result<Vec<Value>, RoadError> {
    let rows = c
        .query(
            &format!(
                "SELECT {COLS} FROM spine_experiments WHERE scope = $1 AND ($2::text IS NULL OR agent = $2) AND ($3::text IS NULL OR state = $3) \
                 ORDER BY opened_at DESC LIMIT 200"
            ),
            &[&scope, &agent, &state],
        )
        .await?;
    Ok(rows
        .iter()
        .map(|r| {
            let mut v = row_of(r);
            v["candidate"] = json!({"hash": v["candidate_hash"]});
            v
        })
        .collect())
}

pub async fn verdicts<C: GenericClient>(c: &C, experiment_id: &str) -> Result<Vec<Value>, RoadError> {
    let rows = c
        .query(
            "SELECT verdict_id, by_did, by_name, reviewer, ask, verdict, words, sig, at FROM spine_verdicts WHERE experiment_id = $1 ORDER BY at",
            &[&experiment_id],
        )
        .await?;
    Ok(rows
        .iter()
        .map(|r| {
            json!({"verdict_id": r.get::<_, String>(0), "by": r.get::<_, String>(1), "by_name": r.get::<_, String>(2),
                   "reviewer": r.get::<_, String>(3), "ask": r.get::<_, Option<String>>(4),
                   "verdict": json_text(Some(&r.get::<_, String>(5))), "words": r.get::<_, String>(6),
                   "sig": r.get::<_, String>(7), "at": isoformat(r.get::<_, SystemTime>(8))})
        })
        .collect())
}

// ---- the seats ----

fn seat_of_row(r: &tokio_postgres::Row) -> Value {
    json!({"name": r.get::<_, String>(0), "template": r.get::<_, String>(1), "at_path": r.get::<_, String>(2),
           "state": r.get::<_, String>(3), "version": r.get::<_, Option<i32>>(4), "by": r.get::<_, String>(5),
           "since": isoformat(r.get::<_, SystemTime>(6)), "changed_at": isoformat(r.get::<_, SystemTime>(7))})
}

const SEAT_COLS: &str = "name, template, at_path, state, version, by_did, since, changed_at";

pub async fn seat_of<C: GenericClient>(c: &C, scope: &str, name: &str) -> Result<Option<Value>, RoadError> {
    Ok(c
        .query_opt(&format!("SELECT {SEAT_COLS} FROM spine_body_seats WHERE name = $1 AND scope = $2"), &[&name, &scope])
        .await?
        .as_ref()
        .map(seat_of_row))
}

pub async fn seats<C: GenericClient>(c: &C, scope: &str, state: Option<&str>) -> Result<Vec<Value>, RoadError> {
    Ok(c
        .query(
            &format!("SELECT {SEAT_COLS} FROM spine_body_seats WHERE scope = $1 AND ($2::text IS NULL OR state = $2) ORDER BY name"),
            &[&scope, &state],
        )
        .await?
        .iter()
        .map(seat_of_row)
        .collect())
}

// ---- the fact ----

async fn fact(
    tx: &Transaction<'_>,
    w: &World,
    type_: &str,
    r#ref: &str,
    mut payload: Value,
    by: Vec<String>,
    marker: Option<Value>,
    scope: &str,
) -> Result<(), RoadError> {
    let hash = crate::hash::content_hash(&payload);
    payload["ref"] = json!(r#ref);
    payload["hash"] = json!(hash);
    let e = crate::envelope::Mint {
        kind: "event".into(),
        r#type: type_.into(),
        universe_id: w.scope.clone(),
        scope_path: scope.to_string(),
        payload,
        correlation_id: Some(r#ref.to_string()),
        authority_chain: Some(by),
        aggregate: None,
        marker,
    }
    .mint()?;
    crate::outbox::add_row(tx, &crate::envelope::encode(&e)?, e["message_id"].as_str().unwrap_or_default()).await?;
    Ok(())
}

// ---- the opening ----

async fn floor_for<C: GenericClient>(c: &C, scope: &str, agent: &str) -> Result<String, RoadError> {
    if let Some(seat) = seat_of(c, scope, agent).await? {
        let at = python_str(&seat["at_path"]);
        let parts: Vec<&str> = at.split('/').collect();
        if parts.len() >= 2 {
            return Ok(parts[..2].join("/"));
        }
    }
    let r = c
        .query_opt(
            "SELECT path FROM spine_levels WHERE scope = $1 AND level = 'floor' ORDER BY opened_at, path LIMIT 1",
            &[&scope],
        )
        .await?;
    r.map(|r| r.get(0))
        .ok_or_else(|| refused("no floor is open in this universe — say “open floor ops” first; an experiment room opens on a floor"))
}

/// `experiments.check_open`: what opening the Experiment on this draft would do, or why it refuses.
pub async fn check_open<C: GenericClient>(c: &C, w: &World, person: &str, draft_id: &str) -> Result<Value, RoadError> {
    let scope = &w.scope;
    let Some(d) = crate::crafts_live::draft(c, scope, person, draft_id).await? else {
        return Err(refused("no such draft of yours here"));
    };
    let (kind, name, body) = (python_str(&d["kind"]), python_str(&d["name"]), d["body"].clone());
    if kind != "template" || body["kind"] != json!("agent") {
        return Err(refused(format!(
            "only an agent's template goes through the Experiment — the {name} {kind} cuts straight onto the shelf"
        )));
    }
    let v = crate::crafts::validate(&kind, &body);
    if v["ok"] != json!(true) {
        return Err(refused(format!("the draft does not read whole yet: {}", python_str(&v["reason"]))));
    }
    if body["name"] != json!(name) {
        return Err(refused(format!(
            "the template's name is {} but the draft is {} — an agent wears one name",
            crate::py::repr_str(&python_str(&body["name"])),
            crate::py::repr_str(&name)
        )));
    }
    let gold = crate::crafts_live::get(c, scope, &name, "golden").await?;
    let cases = gold.as_ref().and_then(|g| g["manifest"]["cases"].as_array().cloned()).unwrap_or_default();
    if gold.as_ref().is_none_or(|g| g["state"] == json!("retired")) || cases.is_empty() {
        return Err(refused(format!(
            "{name} has no golden set on the shelf — every engineered agent is born with one; draft {name}'s golden set and cut it first (the Experiment's evidence is required)"
        )));
    }
    let graph = python_str(&body["graph"]);
    let shipped_graph = crate::crafts_live::shipped(&spine_dir()).iter().any(|s| s["kind"] == json!("graph") && s["name"] == json!(graph));
    if crate::crafts_live::get(c, scope, &graph, "graph").await?.is_none() && !shipped_graph {
        return Err(refused(format!(
            "the {name} template names graph {} and the shelf has no such graph — cut it first",
            crate::py::repr_str(&graph)
        )));
    }
    let shelf_name = crate::crafts::craft_name(&name, "template").map_err(refused)?;
    let mut current: Option<i64> = None;
    if let Some(row) = crate::services_live::get(c, scope, &shelf_name).await? {
        if row["kind"] != json!("template") {
            return Err(refused(format!("{shelf_name} is on the shelf as a {} — a name wears one kind", python_str(&row["kind"]))));
        }
        if row["state"] == json!("retired") {
            return Err(refused(format!("{shelf_name} is retired — restore it first, then experiment on the next version")));
        }
        if row["manifest_hash"] == json!(crate::crafts::pin(&body)) {
            return Err(refused(format!(
                "{shelf_name} already stands on the shelf with these exact bytes (version {}) — nothing to experiment on",
                row["version"]
            )));
        }
        current = row["version"].as_i64();
    }
    let floor = floor_for(c, scope, &name).await?;
    let n: i64 = c
        .query_one("SELECT count(*) FROM spine_experiments WHERE scope = $1 AND agent = $2", &[scope, &name])
        .await?
        .get(0);
    let mut n = n + 1;
    let mut room = crate::levels::child(&floor, "room", &experiments::room_name(&name, n)).map_err(refused)?;
    while crate::levels_live::row(c, &room).await?.is_some() {
        n += 1;
        room = crate::levels::child(&floor, "room", &experiments::room_name(&name, n)).map_err(refused)?;
    }
    Ok(json!({"draft": d, "agent": name, "template": shelf_name, "current_version": current,
              "golden": crate::crafts::craft_name(&name, "golden").map_err(refused)?, "cases": cases.len(),
              "floor": floor, "room": room}))
}

/// `experiments.hold_open`: the Experiment's opening — the kernel's own held act at L2.
pub async fn hold_open(g: &mut Ground, w: &World, person: &str, draft_id: &str, session: Option<&str>) -> Result<Value, RoadError> {
    let c = check_open(g.client(), w, person, draft_id).await?;
    let text = experiments::open_words(
        &python_str(&c["agent"]),
        &python_str(&c["room"]),
        c["current_version"].as_i64(),
        c["cases"].as_i64().unwrap_or(0),
    )
    .map_err(refused)?;
    let held = crate::proof_live::hold_kernel_act(
        g,
        w,
        &text,
        person,
        OPEN_TOOL,
        json!({"draft_id": draft_id, "person": person}),
        OPEN_LEVEL,
        session,
        ACT_CLASS,
        false,
    )
    .await?;
    Ok(json!({"held": held, "level": OPEN_LEVEL, "class": ACT_CLASS, "agent": c["agent"], "room": c["room"],
              "current_version": c["current_version"], "cases": c["cases"]}))
}

/// `experiments.open_in` inside `tx` (the settle arm): the room row and its fact, the experiment
/// row (state running, its arms planned), its marker; the words.
pub async fn open_in(tx: &Transaction<'_>, w: &World, args: &Value, by: &str, ask: Option<&str>, marker: Option<&str>) -> Result<String, RoadError> {
    let person = if truthy(&args["person"]) { python_str(&args["person"]) } else { by.to_string() };
    let draft_id = python_str(&args["draft_id"]);
    let c = check_open(tx, w, &person, &draft_id).await?;
    let (agent, room, floor) = (python_str(&c["agent"]), python_str(&c["room"]), python_str(&c["floor"]));
    let floor_mode = crate::levels_live::row(tx, &floor)
        .await?
        .and_then(|r| r["mode"].as_str().map(str::to_string))
        .unwrap_or_else(|| crate::levels::MODE_DEFAULT.to_string());
    let mode = crate::levels::tighten(&floor_mode, None).map_err(refused)?;
    let exp_id = format!("exp_{}", crate::world::token_hex(6));
    crate::levels_live::insert(tx, &room, &mode, true, None, by, &format!("opened for the Experiment on {agent}"), ask, marker).await?;
    let mid = crate::markers_live::new_id();
    let cv = c["current_version"].as_i64();
    crate::markers_live::insert(
        tx,
        &mid,
        MARKER_KIND,
        marker,
        &exp_id,
        by,
        Some(&format!("the Experiment on {agent} — {}", experiments::arms_plan(cv))),
        &w.scope,
    )
    .await?;
    let body = &c["draft"]["body"];
    let hash = crate::crafts::pin(body);
    let arms = json!({
        "candidate": {"hash": hash, "run_id": null, "passed": null, "failed": null, "details": null},
        "current": cv.map(|v| json!({"version": v, "run_id": null, "passed": null, "failed": null, "details": null})).unwrap_or(Value::Null),
    });
    let reviewers = json!({"grader": {"ask_id": null}, "critic": {"ask_id": null},
                           "security": {"ask_id": null}, "identity": {"ask_id": null}}); // Phase 8 sp6: four reviewers, no empty slot
    let candidate_txt = crate::canonical::canonical_string(body);
    let cv32: Option<i32> = cv.map(|v| v as i32);
    tx.execute(
        "INSERT INTO spine_experiments (experiment_id, scope, person, draft_id, agent, template, current_version, candidate, \
         candidate_hash, golden, room, state, arms, reviewers, ask, marker) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, \
         'running', $12, $13, $14, $15)",
        &[
            &exp_id, &w.scope, &person, &draft_id, &agent, &python_str(&c["template"]), &cv32, &candidate_txt, &hash,
            &python_str(&c["golden"]), &room, &arms.to_string(), &reviewers.to_string(), &ask, &mid,
        ],
    )
    .await?;
    let chain = if by == person { vec![person.clone(), KERNEL.into()] } else { vec![person.clone(), by.to_string(), KERNEL.into()] };
    fact(
        tx,
        w,
        EXPERIMENT_OPENED,
        &exp_id,
        json!({"agent": agent, "template": c["template"], "room": room, "current_version": cv, "candidate_hash": hash,
               "golden": c["golden"], "cases": c["cases"]}),
        chain,
        Some(json!({"kind": MARKER_KIND, "id": mid, "parent": marker, "by": by})),
        &room,
    )
    .await?;
    Ok(format!(
        "{} is open as an experiment room and the experiment {exp_id} on {agent} is running — {}; the proposal will reach you here when the arms and the reviewers are done",
        crate::levels::words(&room).map_err(refused)?,
        experiments::arms_plan(cv)
    ))
}

// ---- the beat ----

async fn update<C: GenericClient>(c: &C, exp_id: &str, col: &str, v: &Value) -> Result<(), RoadError> {
    c.execute(&format!("UPDATE spine_experiments SET {col} = $1 WHERE experiment_id = $2"), &[&v.to_string(), &exp_id]).await?;
    Ok(())
}

async fn run_row<C: GenericClient>(c: &C, run_id: &str) -> Result<Option<Value>, RoadError> {
    Ok(c
        .query_opt("SELECT passed, failed, details FROM spine_harness_runs WHERE run_id = $1", &[&run_id])
        .await?
        .map(|r| {
            json!({"passed": r.get::<_, i32>(0), "failed": r.get::<_, i32>(1),
                   "details": json_text(Some(&r.get::<_, String>(2))).unwrap_or(json!([]))})
        }))
}

async fn alive<C: GenericClient>(c: &C, scope: &str, name: &str) -> Result<Option<String>, RoadError> {
    Ok(c
        .query_opt(
            "SELECT did FROM spine_leases WHERE name = $1 AND until > now() AND (scope = $2 OR scope LIKE $2 || '/%') LIMIT 1",
            &[&name, &scope],
        )
        .await?
        .map(|r| r.get(0)))
}

async fn did_of<C: GenericClient>(c: &C, scope: &str, name: &str) -> Result<Option<String>, RoadError> {
    Ok(c
        .query_opt(
            "SELECT did FROM spine_joins WHERE name = $1 AND (scope = $2 OR scope LIKE $2 || '/%') ORDER BY join_id DESC LIMIT 1",
            &[&name, &scope],
        )
        .await?
        .map(|r| r.get(0)))
}

/// The kernel's hand that spawns the candidate's trial life — the beat's caller provides it
/// (the Rust kernel: `Bodies::spawn_trial`; none when this kernel seats no bodies).
pub type SpawnTrial = dyn Fn(&Value) -> Result<(), String> + Send + Sync;

/// THE EXPERIMENT BEAT — one step of every running experiment of this universe.
pub async fn beat(g: &mut Ground, w: &World, spawn_trial: Option<&SpawnTrial>) -> Result<Vec<String>, RoadError> {
    let mut moved = Vec::new();
    for e in listing(g.client(), &w.scope, None, Some("running")).await? {
        let Some(mut exp) = get(g.client(), &python_str(&e["experiment_id"])).await? else { continue };
        let exp_id = python_str(&exp["experiment_id"]);
        let agent = python_str(&exp["agent"]);
        let mut arms = exp["arms"].clone();
        // 1. the candidate's trial life
        if arms["candidate"]["run_id"].is_null() {
            arms["candidate"]["run_id"] = json!(format!("run_{}", crate::world::token_hex(5)));
            update(g.client(), &exp_id, "arms", &arms).await?;
            exp["arms"] = arms.clone();
            match spawn_trial {
                Some(f) => match f(&exp) {
                    Ok(()) => moved.push(format!("{exp_id}: the candidate's trial life spawned in {}", python_str(&exp["room"]))),
                    Err(why) => {
                        arms["candidate"]["skipped"] = json!(format!("the trial life could not start: {why}"));
                        update(g.client(), &exp_id, "arms", &arms).await?;
                    }
                },
                None => {
                    arms["candidate"]["skipped"] = json!("this kernel seats no bodies — the trial life cannot run here");
                    update(g.client(), &exp_id, "arms", &arms).await?;
                }
            }
            continue;
        }
        if arms["candidate"]["passed"].is_null() && !truthy(&arms["candidate"]["skipped"]) {
            match run_row(g.client(), &python_str(&arms["candidate"]["run_id"])).await? {
                Some(r) => {
                    for k in ["passed", "failed", "details"] {
                        arms["candidate"][k] = r[k].clone();
                    }
                    update(g.client(), &exp_id, "arms", &arms).await?;
                    moved.push(format!("{exp_id}: the candidate ran — {} passed, {} failed", r["passed"], r["failed"]));
                }
                None => continue,
            }
        }
        // 2. the current arm, over the rail to the standing body
        if !arms["current"].is_null() && arms["current"]["run_id"].is_null() && !truthy(&arms["current"]["skipped"]) {
            match alive(g.client(), &w.scope, &agent).await? {
                None => {
                    arms["current"]["skipped"] = json!("no standing life was serving — the current arm is empty");
                    update(g.client(), &exp_id, "arms", &arms).await?;
                }
                Some(_) => {
                    let cases = crate::crafts_live::golden_for(g.client(), &w.scope, &agent, &spine_dir()).await?;
                    let rid = format!("run_{}", crate::world::token_hex(5));
                    let env = crate::envelope::Mint {
                        kind: "command".into(),
                        r#type: crate::body::HARNESS_CMD.into(),
                        universe_id: w.scope.clone(),
                        scope_path: w.scope.clone(),
                        payload: crate::body::harness_payload(&rid, &agent, &cases, None, exp["marker"].as_str()),
                        correlation_id: Some(rid.clone()),
                        authority_chain: Some(vec![KERNEL.to_string()]),
                        ..Default::default()
                    }
                    .mint()?;
                    crate::invoke::publish_command(&w.rabbit_url, &env, &w.ns).await?;
                    arms["current"]["run_id"] = json!(rid);
                    update(g.client(), &exp_id, "arms", &arms).await?;
                    moved.push(format!("{exp_id}: the current arm's run asked of {agent}"));
                    continue;
                }
            }
        }
        if !arms["current"].is_null() && arms["current"]["passed"].is_null() && !truthy(&arms["current"]["skipped"]) {
            match run_row(g.client(), &python_str(&arms["current"]["run_id"])).await? {
                Some(r) => {
                    for k in ["passed", "failed", "details"] {
                        arms["current"][k] = r[k].clone();
                    }
                    update(g.client(), &exp_id, "arms", &arms).await?;
                    moved.push(format!("{exp_id}: the current ran — {} passed, {} failed", r["passed"], r["failed"]));
                }
                None => continue,
            }
        }
        exp["arms"] = arms.clone();
        // 3. the reviewers, under the experiment's marker (the hull's EVENT edge) — Phase 8 sp6: all four; the chips'
        // evidence (the trial life's claims · the candidate's diff · the refusals ground) read off the kernel's record now
        let mut rv = exp["reviewers"].clone();
        let mut asked_now = false;
        exp["claims"] = crate::chips_live::claims_for(g.client(), &w.scope, &exp).await?;
        exp["diff"] = crate::chips_live::diff_for(g.client(), &w.scope, &exp).await?;
        exp["refusals"] = crate::chips_live::refusals_for(g.client(), &w.scope, Some(&agent), 24).await?;
        for who in experiments::REVIEWERS {
            if rv[who]["ask_id"].is_null() && !truthy(&rv[who]["missing"]) {
                if crate::asks::absent(g, &w.scope, who).await?.is_some() {
                    rv[who]["missing"] = json!(format!("the {who} is not seated here — no verdict"));
                } else {
                    let made = crate::asks::submit_ask(
                        g,
                        w,
                        crate::asks::Submit {
                            text: experiments::review_ask(who, &exp),
                            person: python_str(&exp["person"]),
                            to: Some(vec![who.to_string()]),
                            parent_marker: exp["marker"].as_str().map(str::to_string),
                            ..Default::default()
                        },
                    )
                    .await?;
                    rv[who]["ask_id"] = json!(made.ids().first().cloned().unwrap_or_default());
                    rv[who]["asked_at"] = json!(crate::envelope::now_iso());
                    asked_now = true;
                }
            }
        }
        if asked_now {
            update(g.client(), &exp_id, "reviewers", &rv).await?;
            update(g.client(), &exp_id, "claims", &exp["claims"]).await?;
            update(g.client(), &exp_id, "diff", &exp["diff"]).await?;
            let asked: Vec<&str> = experiments::REVIEWERS.iter().copied().filter(|who| truthy(&rv[*who]["ask_id"])).collect();
            moved.push(format!("{exp_id}: the reviewers were asked — {}", asked.join(", ")));
            continue;
        }
        // 4. the verdicts as they land (written by the reviewers themselves, signed)
        let mut done = true;
        for who in experiments::REVIEWERS {
            if truthy(&rv[who]["missing"]) || truthy(&rv[who]["verdict"]) || truthy(&rv[who]["risk"]) || truthy(&rv[who]["identity"]) || truthy(&rv[who]["security"]) {
                continue;
            }
            let vr = g
                .client()
                .query_opt(
                    "SELECT verdict, words, sig, by_did FROM spine_verdicts WHERE experiment_id = $1 AND reviewer = $2 ORDER BY at DESC LIMIT 1",
                    &[&exp_id, &who],
                )
                .await?;
            if let Some(r) = vr {
                let v = json_text(Some(&r.get::<_, String>(0))).unwrap_or(json!({}));
                if who == "grader" {
                    rv[who]["verdict"] = v;
                } else if who == "critic" {
                    rv[who]["risk"] = if truthy(&v["risk"]) { v["risk"].clone() } else { json!("unsaid") };
                    rv[who]["line"] = v["line"].clone();
                } else {
                    // Phase 8 sp6: a chip's word — identity: kept|broken · security: clear|concern
                    rv[who][who] = if truthy(&v[who]) { v[who].clone() } else { json!("unsaid") };
                    rv[who]["line"] = v["line"].clone();
                }
                rv[who]["words"] = json!(r.get::<_, String>(1));
                rv[who]["signed"] = json!(!r.get::<_, String>(2).is_empty());
                rv[who]["by"] = json!(r.get::<_, String>(3));
                continue;
            }
            let ar = g
                .client()
                .query_opt(
                    "SELECT status, reply, extract(epoch FROM (now() - asked_at))::float8 FROM spine_asks WHERE ask_id = $1",
                    &[&python_str(&rv[who]["ask_id"])],
                )
                .await?;
            match ar {
                Some(r) => {
                    let status: String = r.get(0);
                    let reply: Option<String> = r.get(1);
                    let age: Option<f64> = r.get(2);
                    if matches!(status.as_str(), "replied" | "refused" | "cancelled") && reply.as_deref().is_some_and(|x| !x.is_empty()) {
                        rv[who]["missing"] = json!(format!("the {who} answered without a verdict: {}", crate::world::head(&reply.unwrap_or_default(), 160)));
                    } else if age.is_some_and(|a| a > REVIEW_WAIT_S as f64) {
                        rv[who]["missing"] = json!(format!("no word came from the {who} within {} minutes", REVIEW_WAIT_S / 60));
                    } else {
                        done = false;
                    }
                }
                None => done = false,
            }
        }
        update(g.client(), &exp_id, "reviewers", &rv).await?;
        if !done {
            continue;
        }
        // 5. the proposal
        let since: SystemTime = g
            .client()
            .query_one("SELECT opened_at FROM spine_experiments WHERE experiment_id = $1", &[&exp_id])
            .await?
            .get(0);
        let reds: i64 = g
            .client()
            .query_one("SELECT count(*) FROM spine_markers WHERE kind = 'watch-red' AND scope = $1 AND at >= $2", &[&w.scope, &since])
            .await?
            .get(0);
        exp["resiliency"] = json!({"reds": reds});
        exp["reviewers"] = rv.clone();
        let leaning = experiments::leaning_of(&exp);
        exp["leaning"] = json!(leaning);
        let words = experiments::proposal_words(&exp);
        let tx = g.client_mut().transaction().await?;
        tx.execute(
            "UPDATE spine_experiments SET state = 'proposed', resiliency = $1, proposal = $2, leaning = $3, proposed_at = clock_timestamp(), \
             reviewers = $4 WHERE experiment_id = $5",
            &[&exp["resiliency"].to_string(), &words, &leaning, &rv.to_string(), &exp_id],
        )
        .await?;
        let room = python_str(&exp["room"]);
        fact(
            &tx,
            w,
            EXPERIMENT_PROPOSED,
            &exp_id,
            json!({"agent": agent, "leaning": leaning, "words": words, "room": room, "person": exp["person"]}),
            vec![KERNEL.to_string()],
            Some(json!({"kind": MARKER_KIND, "id": exp["marker"], "parent": null, "by": exp["person"]})),
            &room,
        )
        .await?;
        tx.commit().await?;
        moved.push(format!("{exp_id}: proposed — leaning {leaning}"));
    }
    Ok(moved)
}

// ---- the promotion ----

pub async fn promote_check<C: GenericClient>(c: &C, w: &World, experiment_id: &str, at: Option<&str>) -> Result<Value, RoadError> {
    let Some(exp) = get(c, experiment_id).await? else {
        return Err(refused("no such experiment here"));
    };
    if exp["scope"] != json!(w.scope) {
        return Err(refused("no such experiment here"));
    }
    let state = python_str(&exp["state"]);
    if state != "proposed" {
        return Err(refused(format!(
            "the experiment {experiment_id} is {state} — only a proposed experiment promotes{}",
            if state == "running" { " (the arms and the reviewers are not done)" } else { "" }
        )));
    }
    let dem = experiments::promote_demand(exp["candidate"]["kind"].as_str());
    if dem["ok"] != json!(true) {
        return Err(refused(python_str(&dem["reason"])));
    }
    let agent = python_str(&exp["agent"]);
    let seat = seat_of(c, &w.scope, &agent).await?;
    let standing = seat.as_ref().and_then(|s| s["at_path"].as_str().map(str::to_string));
    let path = experiments::deploy_at(&w.scope, at, standing.as_deref()).map_err(refused)?;
    let Some(lv) = crate::levels_live::row(c, &path).await? else {
        return Err(refused(format!("{path} is not open — open the floor or room first; a life stands on an open level")));
    };
    if lv["experiment"] == json!(true) {
        return Err(refused(format!(
            "{} is an experiment room — nothing stands there but an arm",
            crate::levels::words(&path).map_err(refused)?
        )));
    }
    let version = exp["current_version"].as_i64().unwrap_or(0) + 1;
    Ok(json!({"experiment": exp, "level": dem["level"], "at": path, "version": version}))
}

pub async fn hold_promote(g: &mut Ground, w: &World, person: &str, experiment_id: &str, at: Option<&str>, session: Option<&str>) -> Result<Value, RoadError> {
    let c = promote_check(g.client(), w, experiment_id, at).await?;
    let agent = python_str(&c["experiment"]["agent"]);
    let level = python_str(&c["level"]);
    let text = experiments::promote_words(&agent, c["version"].as_i64().unwrap_or(1), &python_str(&c["at"])).map_err(refused)?;
    let held = crate::proof_live::hold_kernel_act(
        g,
        w,
        &text,
        person,
        PROMOTE_TOOL,
        json!({"experiment_id": experiment_id, "person": person, "at": c["at"]}),
        &level,
        session,
        ACT_CLASS,
        false,
    )
    .await?;
    Ok(json!({"held": held, "level": level, "class": ACT_CLASS, "agent": agent, "version": c["version"], "at": c["at"]}))
}

/// The kernel's hands owed AFTER the settling transaction commits (a body reads the shelf at birth).
#[derive(Debug, Clone)]
pub enum Hand {
    Seat { name: String, at: String },
    Rest { name: String },
}

static HANDS: Mutex<Vec<Hand>> = Mutex::new(Vec::new());

fn owe(h: Hand) {
    HANDS.lock().unwrap_or_else(|p| p.into_inner()).push(h);
}

/// The owed hands, drained — the settle's caller runs them after its commit.
pub fn take_hands() -> Vec<Hand> {
    HANDS.lock().unwrap_or_else(|p| p.into_inner()).drain(..).collect()
}

/// The owed hands, run AFTER the commit — on the kernel that seats bodies; said when none does.
pub async fn run_hands(g: &mut Ground, w: &World) {
    let hands = take_hands();
    if hands.is_empty() {
        return;
    }
    #[cfg(feature = "bridge")]
    {
        let Some(b) = crate::bodies::handle() else {
            eprintln!(
                "  [kernel] {} hand(s) owed but this kernel seats no bodies (SPINE_BODIES=none) — the seat stands on the ground; a kernel that seats bodies lights it at its next light",
                hands.len()
            );
            return;
        };
        for h in hands {
            match h {
                Hand::Seat { name, at } => {
                    let sn = crate::crafts::craft_name(&name, "template").unwrap_or_default();
                    match crate::services_live::get(g.client(), &w.scope, &sn).await {
                        Ok(Some(row)) => b.seat_agent(&name, &at, row["manifest"].clone()),
                        Ok(None) => eprintln!("  [kernel] {name}'s template is not on the shelf — no life seated"),
                        Err(e) => eprintln!("  [kernel] {name}'s template could not be read: {e}"),
                    }
                }
                Hand::Rest { name } => b.rest(&name),
            }
        }
    }
    #[cfg(not(feature = "bridge"))]
    {
        let _ = (g, w);
        eprintln!("  [kernel] {} hand(s) owed — this build seats no bodies", hands.len());
    }
}

/// `experiments.promote_in` inside `tx`: the sibling version onto the shelf (probed), the draft
/// spent, the experiment settled promoted, the seat written; the body's next life owed.
pub async fn promote_in(tx: &Transaction<'_>, w: &World, args: &Value, by: &str, ask: Option<&str>, marker: Option<&str>) -> Result<String, RoadError> {
    let person = if truthy(&args["person"]) { python_str(&args["person"]) } else { by.to_string() };
    let exp_id = python_str(&args["experiment_id"]);
    let c = promote_check(tx, w, &exp_id, args["at"].as_str()).await?;
    let exp = &c["experiment"];
    let (agent, template, at) = (python_str(&exp["agent"]), python_str(&exp["template"]), python_str(&c["at"]));
    let body = exp["candidate"].clone();
    let row = if crate::services_live::get(tx, &w.scope, &template).await?.is_none() {
        crate::services_live::register_in(tx, w, &template, "template", &body, by, None, &[]).await?
    } else {
        crate::services_live::version_in(tx, w, &template, &body, by).await?
    };
    let (ok, detail) = crate::crafts_live::probe(tx, &w.scope, &row).await?;
    crate::services_live::record_health_in(tx, w, &template, ok, &detail, by).await?;
    tx.execute("DELETE FROM spine_drafts WHERE draft_id = $1", &[&python_str(&exp["draft_id"])]).await?;
    tx.execute(
        "UPDATE spine_experiments SET state = 'promoted', settled_at = clock_timestamp(), settled_by = $1, at_path = $2 WHERE experiment_id = $3",
        &[&by, &at, &exp_id],
    )
    .await?;
    let version: i32 = row["version"].as_i64().unwrap_or(1) as i32;
    tx.execute(
        "INSERT INTO spine_body_seats (name, scope, template, at_path, state, version, by_did, ask) VALUES ($1, $2, $3, $4, 'active', $5, $6, $7) \
         ON CONFLICT (name, scope) DO UPDATE SET at_path = EXCLUDED.at_path, state = 'active', version = EXCLUDED.version, by_did = \
         EXCLUDED.by_did, changed_at = clock_timestamp(), ask = EXCLUDED.ask",
        &[&agent, &w.scope, &template, &at, &version, &by, &ask],
    )
    .await?;
    let chain = if by == person { vec![person.clone(), KERNEL.into()] } else { vec![person.clone(), by.to_string(), KERNEL.into()] };
    fact(
        tx,
        w,
        EXPERIMENT_SETTLED,
        &exp_id,
        json!({"agent": agent, "settled": "promoted", "version": row["version"], "at": at, "template": template, "pin": row["manifest_hash"]}),
        chain,
        Some(json!({"kind": MARKER_KIND, "id": exp["marker"], "parent": marker, "by": person})),
        &at,
    )
    .await?;
    owe(Hand::Seat { name: agent.clone(), at: at.clone() });
    let hash = python_str(&row["manifest_hash"]);
    Ok(format!(
        "{template} is version {} on the shelf (pin {}…) — {agent}'s next life stands on {}; the room's record is the replay ({exp_id}); the draft is spent",
        row["version"],
        hash.get(7..19).unwrap_or(""),
        crate::levels::words(&at).map_err(refused)?
    ))
}

/// `experiments.decline`: the human's no — routine, recorded; the draft stays.
pub async fn decline(g: &mut Ground, w: &World, person: &str, experiment_id: &str, reason: Option<&str>) -> Result<Value, RoadError> {
    let Some(exp) = get(g.client(), experiment_id).await? else {
        return Err(refused("no such experiment here"));
    };
    if exp["scope"] != json!(w.scope) {
        return Err(refused("no such experiment here"));
    }
    let state = python_str(&exp["state"]);
    if state == "promoted" || state == "declined" {
        return Err(refused(format!("the experiment is already {state}")));
    }
    let agent = python_str(&exp["agent"]);
    let tx = g.client_mut().transaction().await?;
    tx.execute(
        "UPDATE spine_experiments SET state = 'declined', settled_at = clock_timestamp(), settled_by = $1 WHERE experiment_id = $2",
        &[&person, &experiment_id],
    )
    .await?;
    let room = python_str(&exp["room"]);
    fact(
        &tx,
        w,
        EXPERIMENT_SETTLED,
        experiment_id,
        json!({"agent": agent, "settled": "declined", "reason": reason.unwrap_or("the human declined")}),
        vec![person.to_string(), KERNEL.into()],
        Some(json!({"kind": MARKER_KIND, "id": exp["marker"], "parent": null, "by": exp["person"]})),
        &room,
    )
    .await?;
    tx.commit().await?;
    Ok(json!({"experiment_id": experiment_id, "state": "declined",
              "words": format!("the experiment on {agent} is declined — recorded; the {agent} draft stays under your seat to fix and cut again")}))
}

// ---- the ladder ----

async fn rung_check<C: GenericClient>(c: &C, scope: &str, name: &str, to: &str) -> Result<Value, RoadError> {
    let seat = seat_of(c, scope, name).await?;
    let from = seat.as_ref().and_then(|s| s["state"].as_str().map(str::to_string));
    match (&seat, &from) {
        (Some(s), Some(f)) if experiments::ladder_legal(f, to) => Ok(s.clone()),
        _ => Err(refused(experiments::ladder_refusal(name, from.as_deref(), to))),
    }
}

pub async fn hold_rung(g: &mut Ground, w: &World, person: &str, name: &str, tool: &str, session: Option<&str>) -> Result<Value, RoadError> {
    let (to, level, text) = match tool {
        REST_TOOL => ("rested", REST_LEVEL, format!("resting {name} — its life stops at a safe boundary, its self kept")),
        DECOM_TOOL => ("decommissioned", DECOM_LEVEL, format!("decommissioning {name} — the grave: its live objects removed, its self and record kept")),
        _ => ("active", RESTORE_LEVEL, String::new()),
    };
    let seat = rung_check(g.client(), &w.scope, name, to).await?;
    let text = if tool == RESTORE_TOOL {
        format!("restoring {name} — a new life from the shelf's standing version, on {}", python_str(&seat["at_path"]))
    } else {
        text
    };
    let held = crate::proof_live::hold_kernel_act(g, w, &text, person, tool, json!({"name": name}), level, session, ACT_CLASS, false).await?;
    Ok(json!({"held": held, "level": level, "class": ACT_CLASS, "name": name}))
}

fn objective_marker(marker: Option<&str>, by: &str) -> Option<Value> {
    marker.map(|m| json!({"kind": "objective", "id": m, "parent": null, "by": by}))
}

pub async fn rest_in(tx: &Transaction<'_>, w: &World, args: &Value, by: &str, ask: Option<&str>, marker: Option<&str>) -> Result<String, RoadError> {
    let name = python_str(&args["name"]);
    let seat = rung_check(tx, &w.scope, &name, "rested").await?;
    let did = did_of(tx, &w.scope, &name).await?;
    tx.execute(
        "UPDATE spine_body_seats SET state = 'rested', changed_at = clock_timestamp(), ask = $1 WHERE name = $2 AND scope = $3",
        &[&ask, &name, &w.scope],
    )
    .await?;
    if let Some(d) = &did {
        tx.execute("UPDATE spine_wear SET until = clock_timestamp() WHERE did = $1 AND until IS NULL", &[d]).await?;
    }
    let at = python_str(&seat["at_path"]);
    fact(tx, w, BODY_RESTED, &name, json!({"name": name, "did": did, "at": at, "by": by}), vec![by.to_string(), KERNEL.into()], objective_marker(marker, by), &at).await?;
    owe(Hand::Rest { name: name.clone() });
    Ok(experiments::rest_words(&name))
}

pub async fn decom_in(tx: &Transaction<'_>, w: &World, args: &Value, by: &str, ask: Option<&str>, marker: Option<&str>, gw: Option<&crate::gateway::Gateway>) -> Result<String, RoadError> {
    let name = python_str(&args["name"]);
    let seat = rung_check(tx, &w.scope, &name, "decommissioned").await?;
    let did = did_of(tx, &w.scope, &name).await?;
    let (mut removed, mut kept): (Vec<String>, Vec<String>) = (Vec::new(), Vec::new());
    if let Some(d) = &did {
        if tx.execute("DELETE FROM spine_leases WHERE did = $1", &[d]).await? > 0 {
            removed.push("its lease".into());
        }
        if let Some(k) = tx.query_opt("SELECT key FROM spine_mind_keys WHERE did = $1 AND scope = $2", &[d, &w.scope]).await? {
            let key: String = k.get(0);
            if let Some(gw) = gw {
                if let Err(e) = gw.key_delete(&[key]).await {
                    kept.push(format!("the gateway key at the gateway ({e})"));
                }
            }
            tx.execute("DELETE FROM spine_mind_keys WHERE did = $1 AND scope = $2", &[d, &w.scope]).await?;
            removed.push("its gateway key".into());
        }
        let n = tx
            .execute(
                "UPDATE spine_watches SET active = false, rested_by = $1, rested_at = now() WHERE added_by = $2 AND scope = $3 AND active",
                &[&by, d, &w.scope],
            )
            .await?;
        if n > 0 {
            removed.push(format!("{n} watch{}", if n != 1 { "es" } else { "" }));
        }
        if tx.execute("UPDATE spine_wear SET until = clock_timestamp() WHERE did = $1 AND until IS NULL", &[d]).await? > 0 {
            removed.push("its wear links".into());
        }
    }
    if tx.execute("DELETE FROM spine_mind_assignments WHERE subject = $1 AND scope = $2", &[&name, &w.scope]).await? > 0 {
        removed.push("its mind assignment".into());
    }
    let n = tx
        .execute(
            "UPDATE spine_schedules SET active = false, rested_by = $1, rested_at = now() WHERE runner = $2 AND scope = $3 AND active AND kind <> 'kernel'",
            &[&by, &name, &w.scope],
        )
        .await?;
    if n > 0 {
        removed.push(format!("{n} schedule{}", if n != 1 { "s" } else { "" }));
    }
    let n = tx
        .execute(
            "UPDATE spine_intentions SET active = false, stopped_by = $1, stopped_at = now() WHERE (runner = $2 OR planner = $2) AND scope = $3 AND active",
            &[&by, &name, &w.scope],
        )
        .await?;
    if n > 0 {
        removed.push(format!("{n} intention{}", if n != 1 { "s" } else { "" }));
    }
    tx.execute(
        "UPDATE spine_body_seats SET state = 'decommissioned', changed_at = clock_timestamp(), ask = $1 WHERE name = $2 AND scope = $3",
        &[&ask, &name, &w.scope],
    )
    .await?;
    // the bench: the body's own queue on the rail, deleted by the kernel's hand
    match crate::invoke::connect(&w.rabbit_url).await {
        Ok(conn) => match conn.create_channel().await {
            Ok(ch) => {
                let q = crate::rails::serve_queue(&w.ns, Some(&name));
                if ch.queue_delete(q.as_str().into(), lapin::options::QueueDeleteOptions::default()).await.is_ok() {
                    removed.push("its bench".into());
                } else {
                    kept.push("its bench (the rail would not delete it)".into());
                }
            }
            Err(_) => kept.push("its bench (the rail was dark)".into()),
        },
        Err(_) => kept.push("its bench (the rail was dark)".into()),
    }
    let at = python_str(&seat["at_path"]);
    let mut kept_all = kept.clone();
    kept_all.push("its DID, its joins and its record".into());
    fact(
        tx,
        w,
        BODY_DECOMMISSIONED,
        &name,
        json!({"name": name, "did": did, "removed": removed, "kept": kept_all, "by": by}),
        vec![by.to_string(), KERNEL.into()],
        objective_marker(marker, by),
        &at,
    )
    .await?;
    owe(Hand::Rest { name: name.clone() });
    Ok(experiments::decom_words(&name, did.as_deref(), &removed, &kept))
}

pub async fn restore_in(tx: &Transaction<'_>, w: &World, args: &Value, by: &str, ask: Option<&str>, marker: Option<&str>) -> Result<String, RoadError> {
    let name = python_str(&args["name"]);
    let seat = rung_check(tx, &w.scope, &name, "active").await?;
    let template = python_str(&seat["template"]);
    let row = crate::services_live::get(tx, &w.scope, &template).await?;
    let Some(row) = row.filter(|r| r["state"] != json!("retired")) else {
        return Err(refused(format!("{template} is not standing on the shelf — restore the template first")));
    };
    let version: i32 = row["version"].as_i64().unwrap_or(1) as i32;
    tx.execute(
        "UPDATE spine_body_seats SET state = 'active', version = $1, changed_at = clock_timestamp(), ask = $2 WHERE name = $3 AND scope = $4",
        &[&version, &ask, &name, &w.scope],
    )
    .await?;
    let at = python_str(&seat["at_path"]);
    fact(tx, w, BODY_RESTORED, &name, json!({"name": name, "at": at, "version": row["version"], "by": by}), vec![by.to_string(), KERNEL.into()], objective_marker(marker, by), &at).await?;
    owe(Hand::Seat { name: name.clone(), at: at.clone() });
    experiments::restore_words(&name, &at).map_err(refused)
}

// ---- the prune beat ----

/// THE PRUNE BEAT: the crafts nobody wears any more — every body that ever wore one is
/// decommissioned and no wear row stands open — are retired on the shelf; the spine's own never.
pub async fn prune(g: &mut Ground, w: &World) -> Result<Vec<Value>, RoadError> {
    let shipped: Vec<String> = crate::crafts_live::shipped(&spine_dir()).iter().map(|s| python_str(&s["shelf_name"])).collect();
    let graves: Vec<String> = seats(g.client(), &w.scope, Some("decommissioned")).await?.iter().map(|s| python_str(&s["name"])).collect();
    if graves.is_empty() {
        return Ok(Vec::new());
    }
    let like = format!("{}%", w.scope);
    let rows = g
        .client()
        .query(
            "SELECT component, kind, array_agg(DISTINCT body) FILTER (WHERE until IS NULL), array_agg(DISTINCT body) FROM spine_wear \
             WHERE scope LIKE $1 GROUP BY component, kind",
            &[&like],
        )
        .await?;
    let mut pruned = Vec::new();
    for r in rows {
        let component: String = r.get(0);
        let kind: String = r.get(1);
        let open: Option<Vec<String>> = r.get(2);
        let all: Option<Vec<String>> = r.get(3);
        if open.is_some_and(|o| !o.is_empty()) || shipped.contains(&component) || !crate::crafts::is_craft(&kind) {
            continue;
        }
        let Some(all) = all.filter(|a| !a.is_empty()) else { continue };
        if !all.iter().all(|b| graves.contains(b)) {
            continue;
        }
        let Some(row) = crate::services_live::get(g.client(), &w.scope, &component).await? else { continue };
        if row["state"] == json!("retired") {
            continue;
        }
        let mut last = all.clone();
        last.sort();
        last.dedup();
        let last = last.last().cloned().unwrap_or_default();
        let words = experiments::prune_words(&component, &kind, &last);
        let tx = g.client_mut().transaction().await?;
        // the words first — a retired craft takes no health
        crate::services_live::record_health_in(&tx, w, &component, None, &words, "the prune beat").await?;
        crate::services_live::retire_in(&tx, w, &component, "the prune beat", crate::services_live::FactWhere::default()).await?;
        tx.commit().await?;
        pruned.push(json!({"component": component, "kind": kind, "words": words}));
    }
    Ok(pruned)
}
