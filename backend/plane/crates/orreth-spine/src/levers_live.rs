// PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp8 row 3c, THE REMEDIATION RAIL · 2026-09-27
//! The ground half of `orreth_spine.levers` (P7 sp8 row 3c, THE REMEDIATION
//! RAIL): the FORENSIC TURN (`forensic` — the dossier read off the ground, no
//! mind), the KERNEL AS THE REMEDIATION RUNNER (`pull` — a routine lever run
//! at once through the same door a person would use, a consequential one held
//! at the interlock for a person's click; each a recorded hop in the
//! intention's own session, `kernel_row`), and THE ATTRIBUTED OUTCOME
//! (`attribute` — green after our act is an improvement with its cause, green
//! with no act is self-healed, red past the lever's settle plans once more
//! with what was tried and then hands the human the dossier, a cancelled hold
//! is recorded). Law for law with the reference; the loop turns in
//! [`crate::intent_live`].

use crate::envelope::{self, Mint};
use crate::ground::Ground;
use crate::hash::content_hash;
use crate::levers::{
    ago_words, cancelled_note, cured_note, declared, dossier_words, handed_words, pulled_words,
    remedies, self_healed_note, still_red_note, DOOR, KERNEL, NONE, TRIES,
};
use crate::markers_live;
use crate::outbox;
use crate::py::repr_str;
use crate::rail_error::RailError;
use crate::world::{isoformat, json_text, token_hex, RoadError, World};
use serde_json::{json, Value};
use std::time::SystemTime;

/// The catalogue this kernel reads, from the spine home.
pub fn catalogue() -> Result<Vec<Value>, RoadError> {
    crate::levers::catalogue(&crate::levers::spine_dir()).map_err(RoadError::Refused)
}

/// The kernel's own view of the bodies it seats as processes, for the dossier.
pub fn bodies_view() -> Option<Vec<Value>> {
    #[cfg(feature = "bridge")]
    {
        return crate::bodies::handle().map(|b| b.view());
    }
    #[allow(unreachable_code)]
    None
}

/// The body.restart lever's hand — this kernel's own `Bodies`, when it seats any.
fn restart_body(name: &str) -> String {
    #[cfg(feature = "bridge")]
    {
        if let Some(b) = crate::bodies::handle() {
            return match b.restart(name) {
                Ok(v) => v["words"].as_str().unwrap_or_default().to_string(),
                Err(e) => format!("refused — {e}"),
            };
        }
    }
    let _ = name;
    "refused — this kernel seats no bodies as processes (SPINE_BODIES=none); nothing to restart."
        .to_string()
}

async fn events(g: &Ground, like: &str, r#type: &str, limit: i64) -> Result<Vec<Value>, RoadError> {
    let rows = g
        .client()
        .query(
            "SELECT body FROM spine_outbox WHERE convert_from(body, 'UTF8') LIKE $1 AND \
             convert_from(body, 'UTF8') LIKE $2 ORDER BY outbox_id DESC LIMIT $3",
            &[&format!("%{like}%"), &format!("%{type}%"), &limit],
        )
        .await?;
    let mut out = Vec::new();
    for r in rows {
        let body: Vec<u8> = r.get(0);
        if let Ok(e) = envelope::decode(&body) {
            if e["type"].as_str() == Some(r#type) {
                out.push(e);
            }
        }
    }
    Ok(out)
}

fn args_words(args: &Value) -> String {
    args.as_object()
        .map(|m| {
            m.iter()
                .map(|(k, v)| format!("{k}={}", crate::py::python_str(v)))
                .collect::<Vec<_>>()
                .join(" ")
        })
        .unwrap_or_default()
}

fn with_args(head: &str, args: &Value) -> String {
    format!("{head} {}", args_words(args))
        .trim_end()
        .to_string()
}

/// THE FORENSIC TURN: the dossier for a watch, read off the ground — no mind,
/// no guessing. `episode` names this red's first turn, so what was tried this
/// time is listed apart from the last time.
pub async fn forensic(
    g: &Ground,
    w: &World,
    watch_id: &str,
    episode: Option<&str>,
    bodies: Option<&[Value]>,
) -> Result<Value, RoadError> {
    let snap = crate::monitor::snapshot(g, w, false).await?;
    let Some(wv) = snap["watches"]
        .as_array()
        .and_then(|a| a.iter().find(|x| x["watch_id"].as_str() == Some(watch_id)))
        .cloned()
    else {
        return Err(RoadError::Refused(format!(
            "no watch named {} stands here",
            repr_str(watch_id)
        )));
    };
    let since_s: Option<i64> = match wv["since"].as_str() {
        Some(_) => {
            let r = g
                .client()
                .query_opt(
                    "SELECT greatest(0, extract(epoch from now() - since))::float8 FROM spine_watches WHERE \
                     watch_id = $1",
                    &[&watch_id],
                )
                .await?;
            r.and_then(|r| r.get::<_, Option<f64>>(0)).map(|f| f as i64)
        }
        None => None,
    };
    let watch = json!({
        "watch_id": watch_id, "name": wv["name"], "metric": wv["metric"], "op": wv["op"],
        "threshold": wv["threshold"], "value": wv["value"], "state": wv["state"],
        "since": wv["since"], "since_s": since_s,
    });
    let readings: Vec<Value> = events(g, watch_id, crate::watch::WATCH_TURNED, 6)
        .await?
        .iter()
        .map(|e| json!({"at": e["occurred_at"], "to": e["payload"]["to"], "value": e["payload"]["value"]}))
        .collect();
    let metric = wv["metric"].as_str().unwrap_or_default().to_string();
    let mut subjects = Vec::new();
    let mut names: Vec<String> = Vec::new();
    if metric == "bodies_dormant" || metric == "bodies_alive" {
        let rows = g
            .client()
            .query(
                "SELECT name, did, greatest(0, extract(epoch from now() - until))::float8 FROM spine_leases \
                 WHERE scope = $1 AND until <= now() ORDER BY name",
                &[&w.scope],
            )
            .await?;
        for r in rows {
            let (name, did, ago): (String, String, f64) = (r.get(0), r.get(1), r.get(2));
            let mut state = format!("dormant — its lease lapsed {}", ago_words(Some(ago as i64)));
            let seated = bodies.and_then(|b| b.iter().find(|x| x["name"].as_str() == Some(&name)));
            match seated {
                Some(b) if b["state"] == json!("parked") => {
                    state.push_str(&format!(
                        "; PARKED by the kernel: it died {} times",
                        b["deaths"].as_array().map(|a| a.len()).unwrap_or(0)
                    ));
                    let last = b["last_words"]
                        .as_array()
                        .map(|a| {
                            a.iter()
                                .filter_map(Value::as_str)
                                .collect::<Vec<_>>()
                                .join(" / ")
                        })
                        .unwrap_or_default();
                    if !last.is_empty() {
                        state.push_str(&format!(
                            " (last words: “{}”)",
                            last.chars().take(160).collect::<String>()
                        ));
                    }
                }
                Some(b) if b["state"].as_str().is_some() => {
                    state.push_str(&format!(
                        "; the kernel's process is {}",
                        b["state"].as_str().unwrap_or_default()
                    ));
                }
                _ => {
                    let parked = events(g, &name, crate::body::PARKED, 1).await?;
                    if let Some(p) = parked.first() {
                        if p["correlation_id"].as_str() == Some(&name) {
                            state.push_str(&format!(
                                "; PARKED by the kernel: it died {} times",
                                crate::py::python_str(&p["payload"]["deaths"])
                            ));
                        }
                    }
                }
            }
            subjects.push(json!({"kind": "body", "name": name, "did": did, "state": state}));
            names.push(name);
        }
        let alive: Vec<String> = crate::presence::roster(g, &w.scope)
            .await?
            .iter()
            .filter(|b| b["alive"] == json!(true))
            .filter_map(|b| b["name"].as_str().map(str::to_string))
            .collect();
        if !alive.is_empty() && !subjects.is_empty() {
            subjects.push(json!({"kind": "crew", "name": "alive", "state": alive.join(", ")}));
        }
    } else if metric == "asks_received" {
        let rows = g
            .client()
            .query(
                "SELECT ask_id, text, target, greatest(0, extract(epoch from now() - asked_at))::float8 FROM \
                 spine_asks WHERE scope = $1 AND status = 'received' ORDER BY asked_at LIMIT 6",
                &[&w.scope],
            )
            .await?;
        for r in rows {
            let (aid, text, target, ago): (String, String, Option<String>, f64) =
                (r.get(0), r.get(1), r.get(2), r.get(3));
            let head: String = crate::py::fold_ws(&text).chars().take(80).collect();
            subjects.push(json!({"kind": "ask", "name": aid,
                "state": format!("waiting {} — for {}: “{head}”", ago_words(Some(ago as i64)),
                                 target.as_deref().unwrap_or("any body"))}));
            names.push(aid);
        }
    } else if metric == "outbox_pending" || metric == "oldest_outbox_age_s" {
        let lag = &snap["outbox"];
        subjects.push(json!({"kind": "outbox", "name": "the outbox",
            "state": format!("{} facts waiting, the oldest {} s", crate::py::python_str(&lag["pending"]),
                             lag["oldest_age_s"].as_f64().unwrap_or(0.0) as i64)}));
    } else if metric == "minds_unhealthy"
        || metric == "minds_standing"
        || metric == "route_failures_1h"
    {
        for s in crate::sessions::services_listing(g, &w.scope, Some("mind")).await? {
            let st = s["state"].as_str().unwrap_or_default();
            if st == "unhealthy" || st == "retired" {
                let name = s["name"].as_str().unwrap_or_default().to_string();
                subjects.push(json!({"kind": "mind", "name": name,
                    "state": format!("{st} — {}", s["last_detail"].as_str().filter(|d| !d.is_empty()).unwrap_or("no detail"))}));
                names.push(name);
            }
        }
    }
    let mut acts: Vec<(String, String)> = Vec::new();
    for name in names.iter().take(6) {
        let rows = g
            .client()
            .query(
                "SELECT asked_at, held::json->>'tool', status, person FROM spine_asks WHERE scope = $1 AND \
                 served_by = $2 AND held IS NOT NULL AND held::json->'args'->>'name' = $3 ORDER BY asked_at \
                 DESC LIMIT 3",
                &[&w.scope, &KERNEL, name],
            )
            .await?;
        for r in rows {
            let at: SystemTime = r.get(0);
            let (tool, status, person): (Option<String>, String, String) =
                (r.get(1), r.get(2), r.get(3));
            acts.push((
                isoformat(at),
                format!(
                    "{} on {name} — {status}, asked by {person}",
                    tool.unwrap_or_default()
                ),
            ));
        }
        for e in events(g, name, crate::body::PARKED, 2).await? {
            if e["correlation_id"].as_str() == Some(name) {
                acts.push((
                    e["occurred_at"].as_str().unwrap_or_default().to_string(),
                    format!(
                        "the kernel parked {name} after {} deaths",
                        crate::py::python_str(&e["payload"]["deaths"])
                    ),
                ));
            }
        }
        let rows = g
            .client()
            .query(
                "SELECT pulled_at, lever, lever_args, outcome FROM spine_intent_turns WHERE lever IS NOT NULL \
                 AND lever <> $1 AND lever_args LIKE $2 AND pulled_at IS NOT NULL ORDER BY pulled_at DESC \
                 LIMIT 3",
                &[&NONE, &format!("%{name}%")],
            )
            .await?;
        for r in rows {
            let at: SystemTime = r.get(0);
            let (lever, largs, outcome): (String, Option<String>, Option<String>) =
                (r.get(1), r.get(2), r.get(3));
            let args = json_text(largs.as_deref()).unwrap_or_else(|| json!({}));
            acts.push((
                isoformat(at),
                format!(
                    "{}{}",
                    with_args(&format!("the kernel pulled {lever}"), &args),
                    outcome.map(|o| format!(" → {o}")).unwrap_or_default()
                ),
            ));
        }
    }
    acts.sort_by(|a, b| b.0.cmp(&a.0));
    acts.truncate(6);
    let acts: Vec<Value> = acts
        .into_iter()
        .map(|(at, words)| json!({"at": at, "words": words}))
        .collect();
    let last = g
        .client()
        .query_opt(
            "SELECT at, lever, lever_args, outcome, outcome_note FROM spine_intent_turns WHERE watch = $1 AND \
             outcome IS NOT NULL AND ($2::text IS NULL OR episode <> $2) ORDER BY at DESC LIMIT 1",
            &[&watch_id, &episode],
        )
        .await?;
    let last_red = last.map(|r| {
        let at: SystemTime = r.get(0);
        json!({"at": isoformat(at), "lever": r.get::<_, Option<String>>(1),
               "args": json_text(r.get::<_, Option<String>>(2).as_deref()).unwrap_or_else(|| json!({})),
               "outcome": r.get::<_, Option<String>>(3), "note": r.get::<_, Option<String>>(4)})
    });
    let mut tried = Vec::new();
    if let Some(ep) = episode {
        for r in g
            .client()
            .query(
                "SELECT lever, lever_args, outcome FROM spine_intent_turns WHERE episode = $1 AND lever IS NOT \
                 NULL ORDER BY at",
                &[&ep],
            )
            .await?
        {
            tried.push(json!({"lever": r.get::<_, String>(0),
                "args": json_text(r.get::<_, Option<String>>(1).as_deref()).unwrap_or_else(|| json!({})),
                "outcome": r.get::<_, Option<String>>(2)}));
        }
    }
    Ok(
        json!({"watch": watch, "readings": readings, "subjects": subjects, "acts": acts,
              "last_red": last_red, "tried": tried}),
    )
}

/// A hop the KERNEL itself records in the intention's session: an ask row
/// served by the kernel, born replied, its marker under the turn's cause, its
/// journey note and its reply on the rail — one transaction.
#[allow(clippy::too_many_arguments)]
pub async fn kernel_row(
    g: &mut Ground,
    w: &World,
    person: &str,
    session: Option<&str>,
    text: &str,
    reply: &str,
    parent_marker: Option<&str>,
    note: Option<&str>,
) -> Result<String, RoadError> {
    let ask_id = format!("ask_{}", token_hex(8));
    let mid = markers_live::new_id();
    let marker = json!({"kind": "action", "id": mid, "parent": parent_marker, "by": KERNEL});
    let chain = if person != KERNEL {
        vec![person.to_string(), KERNEL.to_string()]
    } else {
        vec![KERNEL.to_string()]
    };
    let note_text = note.unwrap_or(text).to_string();
    let j = Mint {
        kind: "event".into(),
        r#type: crate::asks::JOURNEY.into(),
        universe_id: w.scope.clone(),
        scope_path: w.scope.clone(),
        payload: json!({"ref": ask_id, "hash": "sha256:-", "note": format!("{KERNEL}: {note_text}")}),
        correlation_id: Some(ask_id.clone()),
        authority_chain: Some(chain.clone()),
        aggregate: Some(json!({"type": "ask", "id": ask_id, "sequence": 1})),
        marker: Some(marker.clone()),
    }
    .mint()?;
    let r = Mint {
        kind: "event".into(),
        r#type: crate::asks::REPLY.into(),
        universe_id: w.scope.clone(),
        scope_path: w.scope.clone(),
        payload: json!({"ref": ask_id, "hash": content_hash(&Value::String(reply.into())), "proof": "L1"}),
        correlation_id: Some(ask_id.clone()),
        authority_chain: Some(chain),
        aggregate: Some(json!({"type": "ask", "id": ask_id, "sequence": 2})),
        marker: Some(marker),
    }
    .mint()?;
    let raw_j = envelope::encode(&j)?;
    let raw_r = envelope::encode(&r)?;
    let mid_r = r["message_id"].as_str().unwrap_or_default().to_string();
    let (scope, person2, ask2, mid2, text2, reply2, parent2, session2) = (
        w.scope.clone(),
        person.to_string(),
        ask_id.clone(),
        mid.clone(),
        text.to_string(),
        reply.to_string(),
        parent_marker.map(str::to_string),
        session.map(str::to_string),
    );
    let head: String = note_text.chars().take(200).collect();
    outbox::commit_with_outbox(
        g,
        &raw_j,
        j["message_id"].as_str().unwrap_or_default(),
        None,
        async move |tx| {
            markers_live::insert(
                tx,
                &mid2,
                "action",
                parent2.as_deref(),
                &ask2,
                KERNEL,
                Some(&head),
                &scope,
            )
            .await
            .map_err(|e| RailError::Refused(e.to_string()))?;
            tx.execute(
                "INSERT INTO spine_asks (ask_id, text, person, status, reply, served_by, scope, session, \
                 marker, seq, proof, replied_at) VALUES ($1, $2, $3, 'replied', $4, $5, $6, $7, $8, 2, 'L1', \
                 clock_timestamp())",
                &[
                    &ask2, &text2, &person2, &reply2, &KERNEL, &scope, &session2, &mid2,
                ],
            )
            .await?;
            outbox::add_row(tx, &raw_r, &mid_r).await?;
            Ok(())
        },
    )
    .await?;
    Ok(ask_id)
}

/// A ROUTINE lever pulled through the same door a person would use — the
/// result in words. A refusal is words too, never an error: the outcome is
/// judged by the watch, not by the lever's mood.
pub async fn perform(g: &mut Ground, w: &World, lever: &str, args: &Value) -> String {
    let name = args["name"]
        .as_str()
        .unwrap_or_default()
        .trim()
        .to_lowercase();
    let gw = crate::gateway::Gateway::from_env();
    let gw_ref = if gw.ready().await { Some(&gw) } else { None };
    let out: Result<String, RoadError> = async {
        match lever {
            "service.check" | "mind.check" => {
                let c = crate::services_live::check(g, w, gw_ref, &name, KERNEL).await?;
                let state = c["state"].as_str().map(str::to_string).unwrap_or_else(|| {
                    if c["ok"] == json!(true) {
                        "healthy".into()
                    } else {
                        "unhealthy".into()
                    }
                });
                let detail = c["detail"]
                    .as_str()
                    .filter(|d| !d.is_empty())
                    .map(|d| format!(": {d}"))
                    .unwrap_or_default();
                Ok(format!("{name} was probed — it reads {state}{detail}."))
            }
            "service.restore" | "mind.restore" => {
                let made = crate::stable_live::restore_mind(g, w, gw_ref, &name, KERNEL).await?;
                Ok(format!(
                    "the {} {} stands on the shelf again — a new fact, its rest in the record.",
                    made["name"].as_str().unwrap_or(&name),
                    made["kind"].as_str().unwrap_or("service")
                ))
            }
            "body.restart" => Ok(restart_body(&name)),
            other => Ok(format!("refused — {other} is not a lever this door pulls.")),
        }
    }
    .await;
    match out {
        Ok(words) => words,
        Err(e) => format!("refused — {e}"),
    }
}

/// THE KERNEL PULLS A LEVER under the intention's authority, as a hop in its
/// session. Routine → performed now, the row born replied. Consequential →
/// held at the interlock for a person's click, the planner's reason in the
/// hold's words.
#[allow(clippy::too_many_arguments)]
pub async fn pull(
    g: &mut Ground,
    w: &World,
    intention: &Value,
    turn_id: &str,
    cause_marker: Option<&str>,
    lever: &Value,
    args: &Value,
    because: &str,
) -> Result<Value, RoadError> {
    let name = lever["name"].as_str().unwrap_or_default().to_string();
    let cls = lever["consequence"].as_str().unwrap_or("routine");
    let level =
        crate::proof::level_for(cls, false).map_err(|e| RoadError::Refused(e.to_string()))?;
    let person = intention["added_by"].as_str().unwrap_or(KERNEL);
    let session = intention["session"].as_str();
    let (ask_id, held) = if cls == "consequential" {
        let text = format!(
            "{} — the kernel proposes it for the intention “{}” because {because}",
            with_args(&name, args),
            intention["words"].as_str().unwrap_or_default()
        );
        let hid = crate::proof_live::hold_kernel_act(
            g,
            w,
            &text,
            person,
            &name,
            args.clone(),
            level,
            session,
            cls,
            false,
        )
        .await?;
        (hid, true)
    } else {
        let result = perform(g, w, &name, args).await;
        let aid = kernel_row(
            g,
            w,
            person,
            session,
            &with_args(&format!("the kernel pulls {name}"), args),
            &pulled_words(&name, args, because, &result),
            cause_marker,
            Some(&format!(
                "{} — {result}",
                with_args(&format!("pulled {name}"), args)
            )),
        )
        .await?;
        (aid, false)
    };
    g.client()
        .execute(
            "UPDATE spine_intent_turns SET lever = $1, lever_args = $2, because = $3, lever_ask = $4, pulled_at \
             = CASE WHEN $5 THEN NULL ELSE now() END, objective_ask = '-' WHERE turn_id = $6",
            &[&name, &args.to_string(), &because, &ask_id, &held, &turn_id],
        )
        .await?;
    Ok(json!({"turn_id": turn_id, "lever": name, "args": args, "ask_id": ask_id, "held": held}))
}

async fn close(g: &Ground, turn_id: &str, outcome: &str, note: &str) -> Result<(), RoadError> {
    g.client()
        .execute(
            "UPDATE spine_intent_turns SET outcome = $1, outcome_at = now(), outcome_note = $2 WHERE turn_id = $3",
            &[&outcome, &note, &turn_id],
        )
        .await?;
    Ok(())
}

/// One open remediation turn, as `attribute` reads it.
#[allow(clippy::type_complexity)]
type Open = (
    String,
    String,
    Option<String>,
    String,
    Option<String>,
    Option<String>,
    Option<String>,
    Option<String>,
    Option<f64>,
    i32,
    Option<String>,
    String,
    Option<bool>,
    String,
    Option<String>,
    Option<String>,
);

/// THE ATTRIBUTED OUTCOME: every open remediation turn re-read against its
/// watch (the monitor judged first this beat).
pub async fn attribute(
    g: &mut Ground,
    w: &World,
    levers: &[Value],
    bodies: Option<&[Value]>,
) -> Result<Vec<Value>, RoadError> {
    let rows = g
        .client()
        .query(
            "SELECT t.turn_id, t.intention_id, t.cause, t.watch, t.lever, t.lever_args, t.because, t.lever_ask, \
             CASE WHEN t.pulled_at IS NULL THEN NULL ELSE extract(epoch from now() - t.pulled_at)::float8 END, \
             t.tries, t.episode, w.name, w.last_ok, w.metric, a.status, a.reply FROM spine_intent_turns t JOIN \
             spine_watches w ON w.watch_id = t.watch LEFT JOIN spine_asks a ON a.ask_id = t.lever_ask WHERE \
             t.outcome IS NULL AND t.watch IS NOT NULL AND w.scope = $1 ORDER BY t.at",
            &[&w.scope],
        )
        .await?;
    let open: Vec<Open> = rows
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
                r.get(8),
                r.get(9),
                r.get(10),
                r.get(11),
                r.get(12),
                r.get(13),
                r.get(14),
                r.get(15),
            )
        })
        .collect();
    let mut moved = Vec::new();
    for (
        tid,
        iid,
        cause,
        wid,
        lever,
        largs,
        because,
        lask,
        waited,
        tries,
        episode,
        wname,
        last_ok,
        metric,
        hstatus,
        hreply,
    ) in open
    {
        let Some(intention) = crate::intent_live::get(g, &w.scope, &iid).await? else {
            continue;
        };
        let args = json_text(largs.as_deref()).unwrap_or_else(|| json!({}));
        let green = last_ok.unwrap_or(false);
        let pulled = lever.as_deref().is_some_and(|l| l != NONE) && waited.is_some();
        let holding = lask.is_some() && hstatus.as_deref() == Some("awaiting-confirm");
        let imarker = intention["marker"].as_str().map(str::to_string);
        if green {
            if holding {
                // the act is not needed after all
                let _ = crate::asks::settle_kernel_act(
                    g,
                    w,
                    lask.as_deref().unwrap_or_default(),
                    false,
                    KERNEL,
                    None,
                    Some("withdrawn — the watch went green on its own"),
                )
                .await;
            }
            let (outcome, note) = if pulled {
                (
                    "cured",
                    cured_note(
                        &wname,
                        lever.as_deref().unwrap_or_default(),
                        &args,
                        because.as_deref().unwrap_or_default(),
                    ),
                )
            } else {
                ("self-healed", self_healed_note(&wname))
            };
            let m = markers_live::set_marker(
                g,
                w,
                "improvement",
                &wid,
                KERNEL,
                imarker.as_deref(),
                Some(&note),
                None,
            )
            .await?;
            close(g, &tid, outcome, &note).await?;
            moved.push(json!({"turn_id": tid, "outcome": outcome, "improvement": m["id"]}));
            continue;
        }
        if lask.is_some() && hstatus.as_deref() == Some("cancelled") && !pulled {
            let why: String = crate::py::fold_ws(hreply.as_deref().unwrap_or(""))
                .chars()
                .take(160)
                .collect();
            let why = if why.is_empty() {
                "the hold was cancelled".to_string()
            } else {
                why
            };
            let note = cancelled_note(&wname, lever.as_deref().unwrap_or_default(), &args, &why);
            markers_live::set_marker(
                g,
                w,
                "observation",
                &wid,
                KERNEL,
                imarker.as_deref(),
                Some(&note),
                None,
            )
            .await?;
            close(g, &tid, "cancelled", &note).await?;
            moved.push(json!({"turn_id": tid, "outcome": "cancelled"}));
            continue;
        }
        if !pulled {
            continue; // waiting on the planner, or on a person
        }
        let lname = lever.clone().unwrap_or_default();
        let settles = declared(levers, &lname)
            .and_then(|d| d["settles_s"].as_i64())
            .unwrap_or(30);
        if waited.unwrap_or(0.0) < settles as f64 {
            continue;
        }
        let note = still_red_note(&wname, &lname, &args, settles);
        markers_live::set_marker(
            g,
            w,
            "observation",
            &wid,
            KERNEL,
            imarker.as_deref(),
            Some(&note),
            None,
        )
        .await?;
        close(g, &tid, "still-red", &note).await?;
        let d = forensic(g, w, &wid, episode.as_deref(), bodies).await?;
        let tries = tries.max(1) as i64;
        if tries < TRIES {
            let offered: Vec<Value> = remedies(levers, &metric, DOOR)
                .into_iter()
                .cloned()
                .collect();
            let cause_id = format!("{}#{}", cause.clone().unwrap_or_default(), tries + 1);
            let t = crate::intent_live::plan(
                g,
                w,
                &intention,
                Some(&json!({"id": cause_id})),
                &dossier_words(&d),
                crate::intent_live::Remedy {
                    dossier: Some(d.clone()),
                    levers: offered,
                    parent: cause.clone(),
                    watch: Some(wid.clone()),
                    episode: episode.clone(),
                    tries: tries + 1,
                },
            )
            .await?;
            moved.push(json!({"turn_id": tid, "outcome": "still-red", "again": t["turn_id"]}));
        } else {
            let tried: Vec<Value> = d["tried"].as_array().cloned().unwrap_or_default();
            let words = handed_words(&wname, &tried, &dossier_words(&d));
            let aid = kernel_row(
                g,
                w,
                intention["added_by"].as_str().unwrap_or(KERNEL),
                intention["session"].as_str(),
                &format!(
                    "watch {} is still red after {TRIES} levers",
                    repr_str(&wname)
                ),
                &words,
                cause.as_deref(),
                Some(&format!(
                    "handed to the human: watch {} still red",
                    repr_str(&wname)
                )),
            )
            .await?;
            moved.push(json!({"turn_id": tid, "outcome": "still-red", "handed": aid}));
        }
    }
    Ok(moved)
}
