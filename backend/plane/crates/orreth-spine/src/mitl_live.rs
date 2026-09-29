// PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch row 4, re-base sp1: the four Python-only doors cross — MITL's ground half (the ontology · the toggle · the impact read) · 2026-09-28
//! MITL on the ground — mirrors the ground half of `orreth_spine.mitl` (the
//! pure half is `mitl`): the canon in passages and their citations (W15), what
//! MITL wears (its ontology in the Record), the soft toggle (summoned ·
//! dismissed — recorded facts, never a deletion), and THE IMPACT DOOR: the
//! kernel reads the GROUND deterministically — which bodies, chains,
//! intentions, watches, markers, services and cost a change touches, its
//! consequence class and the level it demands — judges the VERDICT by the
//! ladder (a kernel intention is grave whatever any brain says), and asks
//! MITL for the words as an ordinary ask filed under the change's marker.
//! Every note is the reference's, word for word; the pure parts (the passages,
//! the citations, the metric in words, the lines, the ask's text) live in `mitl`
//! (fixture `mitl-v0.json`: `passages` · `metric_in` · `describe` · `impact_text`).

use crate::envelope::{self, Mint};
use crate::ground::Ground;
use crate::intent::{self, read_words};
use crate::intent_live;
use crate::markers_live;
use crate::mcp_live;
use crate::mitl::{
    ask_text, citations, describe, metric_in, s_of, shape, verdict, DISMISSED, EXPANSION, KINDS,
    NAME, SUMMONED,
};
use crate::outbox;
use crate::placement;
use crate::proof::level_for;
use crate::py::{cut_chars, get, python_str, repr_str, truthy};
use crate::schema::has_table;
use crate::services_live;
use crate::sessions;
use crate::tools;
use crate::world::{isoformat, json_text, refused, RoadError, World};
use serde_json::{json, Map, Value};
use std::collections::{BTreeMap, BTreeSet, HashMap};
use std::time::SystemTime;

// ---- the ontology: the canon in passages, and their citations ---------------------------

/// `mitl.ontology`: what MITL wears, with its provenance — every current passage's source
/// path, passage number, sha256 and when it was acquired.
pub async fn ontology(g: &Ground, scope: &str) -> Result<Vec<Value>, RoadError> {
    let rows = g
        .client()
        .query(
            "SELECT key, hash, landed_at, length(body) FROM spine_memories WHERE namespace = $1 AND \
             scope = $2 AND valid_to IS NULL ORDER BY key",
            &[&NAME, &scope],
        )
        .await?;
    Ok(rows
        .iter()
        .map(|r| {
            let key: String = r.get(0);
            let (path, num) = key.split_once('#').unwrap_or((&key, ""));
            json!({"key": key, "path": path, "passage": num.parse::<i64>().unwrap_or(0),
                   "hash": r.get::<_, String>(1), "acquired_at": isoformat(r.get::<_, SystemTime>(2)),
                   "chars": r.get::<_, i32>(3)})
        })
        .collect())
}

/// The `GET /mitl` answer: is MITL in the lit crew, what it wears, every citation.
pub async fn card(
    g: &Ground,
    scope: &str,
    session: Option<&str>,
    person: &str,
) -> Result<Value, RoadError> {
    let ont = ontology(g, scope).await?;
    let files: BTreeSet<String> = ont
        .iter()
        .map(|o| o["path"].as_str().unwrap_or_default().to_string())
        .collect();
    Ok(json!({"name": NAME, "expansion": EXPANSION,
              "summoned": summoned(g, scope, session, person).await?,
              "ontology": {"passages": ont.len(), "files": files},
              "citations": citations(None)}))
}

// ---- the soft toggle: summoned · dismissed — recorded facts, never a deletion ----------

/// The session's latest objective marker — the toggle's and the impact ask's parent.
pub async fn latest_objective(
    g: &Ground,
    session: Option<&str>,
) -> Result<Option<String>, RoadError> {
    let Some(session) = session else {
        return Ok(None);
    };
    Ok(g.client()
        .query_opt(
            "SELECT a.marker FROM spine_asks a JOIN spine_markers m ON m.marker_id = a.marker WHERE \
             a.session = $1 AND m.kind = 'objective' ORDER BY a.asked_at DESC LIMIT 1",
            &[&session],
        )
        .await?
        .and_then(|r| r.get(0)))
}

/// `mitl.summon`: the toggle's effect — a row, its marker (an action under the session's
/// latest objective, or a root), and its fact on the rail wearing the human's chain —
/// summoned or dismissed, both recorded, in ONE transaction.
pub async fn summon(
    g: &mut Ground,
    w: &World,
    person: &str,
    session: Option<&str>,
    on: bool,
) -> Result<Value, RoadError> {
    let parent = latest_objective(g, session).await?;
    let mid = markers_live::new_id();
    let marker = json!({"kind": "action", "id": mid, "parent": parent, "by": person});
    let state = if on { "summoned" } else { "dismissed" };
    let r#ref = session.unwrap_or(person).to_string();
    let e = Mint {
        kind: "event".into(),
        r#type: if on { SUMMONED } else { DISMISSED }.into(),
        universe_id: w.scope.clone(),
        scope_path: w.scope.clone(),
        payload: json!({"ref": r#ref, "hash": "sha256:-", "by": person, "session": session, "body": NAME}),
        correlation_id: Some(r#ref.clone()),
        authority_chain: Some(vec![person.to_string()]),
        aggregate: None,
        marker: Some(marker),
    }
    .mint()?;
    let raw = envelope::encode(&e)?;
    let note = format!("MITL {state} — {EXPANSION}");
    let tx = g.client_mut().transaction().await?;
    markers_live::insert(
        &tx,
        &mid,
        "action",
        parent.as_deref(),
        &r#ref,
        person,
        Some(&note),
        &w.scope,
    )
    .await?;
    tx.execute(
        "INSERT INTO spine_mitl (session, person, state, marker, scope) VALUES ($1, $2, $3, $4, $5)",
        &[&session, &person, &state, &mid, &w.scope],
    )
    .await?;
    outbox::add_row(&tx, &raw, e["message_id"].as_str().unwrap_or_default()).await?;
    tx.commit().await?;
    Ok(
        json!({"summoned": on, "state": state, "person": person, "session": session,
              "marker": mid, "name": NAME, "expansion": EXPANSION}),
    )
}

/// `mitl.summoned`: is MITL in the lit crew — for this session, or for this person outside
/// any session? The latest recorded word decides.
pub async fn summoned(
    g: &Ground,
    scope: &str,
    session: Option<&str>,
    person: &str,
) -> Result<bool, RoadError> {
    let row = match session {
        Some(s) => {
            g.client()
                .query_opt(
                    "SELECT state FROM spine_mitl WHERE session = $1 AND scope = $2 ORDER BY row_id DESC LIMIT 1",
                    &[&s, &scope],
                )
                .await?
        }
        None => {
            g.client()
                .query_opt(
                    "SELECT state FROM spine_mitl WHERE session IS NULL AND person = $1 AND scope = $2 \
                     ORDER BY row_id DESC LIMIT 1",
                    &[&person, &scope],
                )
                .await?
        }
    };
    Ok(row.is_some_and(|r| r.get::<_, String>(0) == "summoned"))
}

// ---- the impact door: the ground read, the verdict judged, the words asked -------------

/// Every body of this world by name — its kind, self, and life.
async fn bodies_of(g: &Ground, scope: &str) -> Result<BTreeMap<String, Value>, RoadError> {
    let rows = g
        .client()
        .query(
            "SELECT DISTINCT ON (name) name, kind, did, life FROM spine_joins WHERE scope = $1 ORDER BY \
             name, join_id DESC",
            &[&scope],
        )
        .await?;
    Ok(rows
        .iter()
        .map(|r| {
            let n: String = r.get(0);
            (
                n.clone(),
                json!({"name": n, "kind": r.get::<_, String>(1), "did": r.get::<_, String>(2), "life": r.get::<_, i32>(3)}),
            )
        })
        .collect())
}

/// The meter's cost so far for the selves named (rule 5: the count, never the prompt).
async fn cost_of(g: &Ground, dids: &[String]) -> Result<HashMap<String, Value>, RoadError> {
    if dids.is_empty() || !has_table(g, "spine_meter").await? {
        return Ok(HashMap::new());
    }
    let rows = g
        .client()
        .query(
            "SELECT did, count(*), coalesce(sum(tokens_in + tokens_out), 0) FROM spine_meter WHERE did = \
             ANY($1) GROUP BY did",
            &[&dids],
        )
        .await?;
    Ok(rows
        .iter()
        .map(|r| {
            (
                r.get::<_, String>(0),
                json!({"thoughts": r.get::<_, i64>(1), "tokens": r.get::<_, i64>(2)}),
            )
        })
        .collect())
}

fn push(t: &mut Value, key: &str, v: Value) {
    t[key].as_array_mut().expect("a list").push(v);
}

fn note(t: &mut Value, words: impl Into<String>) {
    push(t, "notes", Value::String(words.into()));
}

/// The service a change touches, from the shelf (P6.5 sp1), and the names of the bodies
/// that DECLARED it (a tool: `tools:<name>` at their join) — the caller names them.
async fn service_touched(
    g: &Ground,
    scope: &str,
    t: &mut Value,
    kind: &str,
    name: &str,
) -> Result<(Option<Value>, Vec<String>), RoadError> {
    let svc = services_live::get(g.client(), scope, name).await?;
    let Some(svc) = svc.filter(|s| s["kind"].as_str() == Some(kind)) else {
        return Ok((None, Vec::new()));
    };
    push(
        t,
        "services",
        json!({"name": svc["name"], "kind": svc["kind"], "did": svc["did"], "state": svc["state"], "version": svc["version"]}),
    );
    let mut declared = Vec::new();
    if kind == "tool" {
        let want = format!("tools:{name}");
        for r in g
            .client()
            .query(
                "SELECT DISTINCT ON (name) name, capabilities FROM spine_joins WHERE scope = $1 ORDER BY \
                 name, join_id DESC",
                &[&scope],
            )
            .await?
        {
            let caps = json_text(r.get::<_, Option<String>>(1).as_deref()).unwrap_or(json!([]));
            if caps.as_array().is_some_and(|a| a.iter().any(|c| c == &json!(want))) {
                declared.push(r.get::<_, String>(0));
            }
        }
    }
    Ok((Some(svc), declared))
}

/// `mitl.read_ground`: the kernel reads the ground for MITL — deterministically: what the
/// change touches (bodies · chains · intentions · watches · markers · the meter's cost so
/// far), its consequence class and the level it demands. A held ask (`ref` = ask_…) is
/// read from its hold; an intention from its record; a draft from its words. Refuses a
/// kind it does not know, in words.
pub async fn read_ground(g: &Ground, w: &World, change: &Value) -> Result<Value, RoadError> {
    let scope = w.scope.as_str();
    let kind = s_of(get(change, "kind"));
    if !KINDS.contains(&kind.as_str()) {
        return Err(refused(format!("a change is one of {}", KINDS.join(", "))));
    }
    let r#ref: Option<String> = Some(s_of(get(change, "ref"))).filter(|r| !r.is_empty());
    let mut draft: Map<String, Value> = get(change, "draft")
        .as_object()
        .cloned()
        .unwrap_or_default();
    let mut words: String = s_of(get(change, "words"))
        .split_whitespace()
        .collect::<Vec<_>>()
        .join(" ");
    let mut t = json!({"kind": kind, "ref": r#ref, "words": words, "bodies": [], "chains": [],
                       "intentions": [], "watches": [], "markers": [], "services": [], "cost": {}, "notes": [],
                       "kernel": false, "class": "routine", "level": "L1", "marker": null});
    let bodies = bodies_of(g, scope).await?;
    let mut named: Vec<String> = Vec::new();
    let name_body = |n: Option<&str>, named: &mut Vec<String>| {
        if let Some(n) = n.filter(|n| !n.is_empty()) {
            if !named.iter().any(|x| x == n) {
                named.push(n.to_string());
            }
        }
    };
    let decls = tools::declarations(&tools::spine_dir()).unwrap_or_default();

    // a held ask: the hold names the act, its class and its level (sp1)
    let mut hold: Option<Map<String, Value>> = None;
    if let Some(r) = r#ref.as_deref().filter(|r| r.starts_with("ask_")) {
        let row = g
            .client()
            .query_opt(
                "SELECT held, marker, served_by, text, status FROM spine_asks WHERE ask_id = $1 AND scope = $2",
                &[&r, &scope],
            )
            .await?;
        match row {
            None => note(&mut t, "no such ask is held on this ground"),
            Some(row) => {
                let held: Map<String, Value> =
                    json_text(row.get::<_, Option<String>>(0).as_deref())
                        .and_then(|v| v.as_object().cloned())
                        .unwrap_or_default();
                let marker: Option<String> = row.get(1);
                t["marker"] = json!(marker);
                push(
                    &mut t,
                    "markers",
                    json!({"id": marker, "kind": "objective", "ref": r}),
                );
                if !held.is_empty() {
                    t["class"] = held.get("class").cloned().unwrap_or(json!("consequential"));
                    t["level"] = held.get("level").cloned().unwrap_or(json!("L2"));
                    let mut merged: Map<String, Value> = held
                        .get("args")
                        .and_then(|a| a.as_object().cloned())
                        .unwrap_or_default();
                    merged.insert(
                        "tool".into(),
                        held.get("tool").cloned().unwrap_or(Value::Null),
                    );
                    for (k, v) in draft.iter() {
                        merged.insert(k.clone(), v.clone());
                    }
                    draft = merged;
                    hold = Some(held);
                }
                let served_by: Option<String> = row.get(2);
                if let Some(sb) = served_by.filter(|s| !s.is_empty() && s != "the kernel") {
                    let holder = bodies
                        .values()
                        .find(|b| b["did"].as_str() == Some(&sb))
                        .and_then(|b| b["name"].as_str().map(str::to_string));
                    name_body(holder.as_deref(), &mut named);
                }
                if words.is_empty() {
                    let text: Option<String> = row.get(3);
                    words = cut_chars(
                        &text
                            .unwrap_or_default()
                            .split_whitespace()
                            .collect::<Vec<_>>()
                            .join(" "),
                        200,
                    );
                }
                t["words"] = json!(words);
                let status: String = row.get(4);
                if status != "awaiting-confirm" {
                    note(
                        &mut t,
                        format!("this ask is {status} — nothing is held now"),
                    );
                }
            }
        }
    }
    let held = hold.is_some();

    match kind.as_str() {
        "watch" => {
            let metric = Some(s_of(draft.get("metric").unwrap_or(&Value::Null)))
                .filter(|m| !m.is_empty())
                .or_else(|| metric_in(&words));
            t["metric"] = json!(metric);
            let name = draft
                .get("name")
                .filter(|v| truthy(v))
                .cloned()
                .unwrap_or_else(|| json!(cut_chars(&words, 80)));
            t["watch"] = json!({"name": name, "metric": metric, "op": draft.get("op").cloned().unwrap_or(Value::Null),
                                "threshold": draft.get("threshold").cloned().unwrap_or(Value::Null)});
            if let Some(m) = metric
                .as_deref()
                .filter(|m| !crate::watch::METRICS.contains(m))
            {
                note(
                    &mut t,
                    format!(
                        "no metric named {} — the metrics are {}",
                        repr_str(m),
                        crate::watch::METRICS.join(", ")
                    ),
                );
            }
            let tool = tools::declared(&decls, "add-watch")
                .cloned()
                .unwrap_or(json!({}));
            if !held {
                let cls = tools::consequence_of(&tool, None);
                t["level"] =
                    json!(level_for(&cls, tools::master(&tool))
                        .map_err(|e| refused(e.to_string()))?);
                t["class"] = json!(cls);
            }
            let mon = bodies.get("monitor");
            name_body(Some("monitor"), &mut named);
            if mon.is_none() {
                note(
                    &mut t,
                    "no monitor body has joined this world yet — the watch would land by hand",
                );
            }
            push(&mut t, "chains", json!("H → monitor → tool:add-watch"));
            if has_table(g, "spine_watches").await? {
                for r in g
                    .client()
                    .query(
                        "SELECT watch_id, name, metric, op, threshold, last_ok FROM spine_watches WHERE scope = $1 \
                         ORDER BY added_at",
                        &[&scope],
                    )
                    .await?
                {
                    let wm: String = r.get(2);
                    if metric.as_deref() == Some(wm.as_str()) {
                        push(&mut t, "watches", json!({"watch_id": r.get::<_, String>(0), "name": r.get::<_, String>(1),
                            "metric": wm, "op": r.get::<_, String>(3), "threshold": r.get::<_, f64>(4),
                            "red": r.get::<_, Option<bool>>(5) == Some(false)}));
                    }
                }
            }
            for i in intent_live::interested(g, scope, intent::WATCH_RED).await? {
                push(
                    &mut t,
                    "intentions",
                    json!({"intention_id": i["intention_id"], "words": i["words"], "kind": i["kind"],
                                                  "serves": i["serves"], "wakes": true}),
                );
                name_body(i["planner"].as_str(), &mut named);
                name_body(i["runner"].as_str(), &mut named);
                push(
                    &mut t,
                    "chains",
                    json!(format!(
                        "the kernel → {} → {} (when “{}” wakes on watch-red)",
                        s_of(&i["planner"]),
                        i["runner"]
                            .as_str()
                            .filter(|r| !r.is_empty())
                            .unwrap_or("the crew"),
                        cut_chars(i["words"].as_str().unwrap_or_default(), 60)
                    )),
                );
            }
        }
        "intention" => {
            let iid = Some(s_of(draft.get("intention_id").unwrap_or(&Value::Null)))
                .filter(|s| !s.is_empty())
                .or_else(|| r#ref.clone().filter(|r| r.starts_with("int_")));
            if let Some(iid) = iid {
                match intent_live::get(g, scope, &iid).await? {
                    None => note(&mut t, "no such intention on this ground"),
                    Some(i) => {
                        push(
                            &mut t,
                            "intentions",
                            json!({"intention_id": iid, "words": i["words"], "kind": i["kind"],
                                                          "serves": i["serves"], "active": i["active"], "wakes": false}),
                        );
                        let kernel = i["kind"].as_str() == Some("kernel");
                        t["kernel"] = json!(kernel);
                        if !truthy(&t["marker"]) {
                            t["marker"] = i["marker"].clone();
                        }
                        let im = s_of(&i["marker"]);
                        let mut grew = Map::new();
                        for r in g
                            .client()
                            .query(
                                "SELECT kind, count(*) FROM spine_markers WHERE root = $1 AND marker_id <> $2 GROUP BY kind",
                                &[&im, &im],
                            )
                            .await?
                        {
                            grew.insert(r.get::<_, String>(0), json!(r.get::<_, i64>(1)));
                        }
                        push(
                            &mut t,
                            "markers",
                            json!({"id": i["marker"], "kind": "intention", "ref": iid, "under": grew}),
                        );
                        name_body(i["planner"].as_str(), &mut named);
                        name_body(i["runner"].as_str(), &mut named);
                        push(
                            &mut t,
                            "chains",
                            json!(format!(
                                "the kernel → {} → {}",
                                s_of(&i["planner"]),
                                i["runner"]
                                    .as_str()
                                    .filter(|r| !r.is_empty())
                                    .unwrap_or("the crew")
                            )),
                        );
                        if kernel {
                            t["class"] = json!("grave");
                            t["level"] = json!("L3-master");
                            push(
                                &mut t,
                                "chains",
                                json!("H → a master → the kernel (the stop)"),
                            );
                        } else if !held {
                            t["class"] = json!("routine");
                            t["level"] = json!("L1");
                        }
                        if i["active"] == json!(false) {
                            note(&mut t, "this intention is already at rest");
                        }
                    }
                }
            } else {
                let dw = draft.get("words").map(s_of).unwrap_or_default();
                let rw = read_words(&format!(
                    "intention: {}",
                    if words.is_empty() { dw } else { words.clone() }
                ));
                let runner = draft.get("runner").cloned().unwrap_or(Value::Null);
                t["draft"] = json!({"serves": rw.serves, "interests": rw.interests, "every_s": rw.every_s, "runner": runner});
                name_body(Some("planner"), &mut named);
                let runner_s = s_of(&runner);
                name_body(Some(runner_s.as_str()), &mut named);
                push(
                    &mut t,
                    "chains",
                    json!(format!(
                        "the kernel → planner → {}",
                        if runner_s.is_empty() {
                            "the crew"
                        } else {
                            runner_s.as_str()
                        }
                    )),
                );
                let mine: BTreeSet<String> = rw
                    .interests
                    .clone()
                    .unwrap_or_default()
                    .into_iter()
                    .collect();
                for i in intent_live::listing(g, scope, None, None, 500).await? {
                    if i["active"] != json!(true) {
                        continue;
                    }
                    let theirs: BTreeSet<String> = i["interests"]
                        .as_array()
                        .map(|a| a.iter().map(python_str).collect())
                        .unwrap_or_default();
                    let shared: Vec<&String> = theirs.intersection(&mine).collect();
                    if !shared.is_empty() {
                        push(
                            &mut t,
                            "intentions",
                            json!({"intention_id": i["intention_id"], "words": i["words"], "kind": i["kind"],
                                                          "serves": i["serves"], "shares": shared, "wakes": false}),
                        );
                    }
                }
                if !(rw.interests.as_ref().is_some_and(|v| !v.is_empty()) || rw.every_s.is_some()) {
                    note(
                        &mut t,
                        "nothing wakes it yet — say WHEN (a red watch, a cadence)",
                    );
                }
            }
        }
        "placement" => {
            // P6 sp4: a placement change is consequential (L2) in v0 — MITL reads the profile
            // the change proposes (the draft's `placement`, else the named body's own from its
            // join) and judges it against THIS ground
            let who = Some(s_of(draft.get("name").unwrap_or(&Value::Null)))
                .filter(|s| !s.is_empty())
                .or_else(|| r#ref.clone())
                .unwrap_or_default();
            let known = bodies.get(&who);
            if known.is_some() {
                name_body(Some(&who), &mut named);
            }
            let mut worn: Option<Value> = None;
            if let Some(b) = known {
                let did = s_of(&b["did"]);
                let r = g
                    .client()
                    .query_opt(
                        "SELECT placement FROM spine_joins WHERE did = $1 ORDER BY join_id DESC LIMIT 1",
                        &[&did],
                    )
                    .await?;
                worn = Some(
                    r.and_then(|r| json_text(r.get::<_, Option<String>>(0).as_deref()))
                        .unwrap_or_else(|| sessions::default_profile().to_value()),
                );
            }
            let asked = draft
                .get("placement")
                .filter(|v| truthy(v))
                .cloned()
                .or_else(|| worn.clone().filter(truthy))
                .unwrap_or(json!({}));
            let prof = match placement::profile(&json!({"placement": asked})) {
                Ok(p) => Some(p),
                Err(e) => {
                    note(&mut t, e.to_string());
                    None
                }
            };
            t["class"] = json!("consequential");
            t["level"] = json!("L2");
            t["placement"] = prof
                .as_ref()
                .map(placement::Profile::to_value)
                .unwrap_or(Value::Null);
            if let Some(prof) = &prof {
                let here = sessions::ground_declares();
                let (ok, _reasons) = placement::honor(prof, &here);
                note(
                    &mut t,
                    format!(
                        "{}{}",
                        if ok {
                            "this ground honors it: "
                        } else {
                            "this ground would REFUSE it at birth: "
                        },
                        placement::why_here(prof, &here)
                    ),
                );
                if let Some(worn) = worn.as_ref().filter(|w| **w != prof.to_value()) {
                    let affinity: Vec<String> = worn["affinity"]
                        .as_array()
                        .map(|a| a.iter().map(python_str).collect())
                        .unwrap_or_default();
                    note(
                        &mut t,
                        format!(
                            "{who} stands today on cell '{}' · metal {}{}",
                            python_str(&worn["cell"]),
                            python_str(&worn["metal"]),
                            if affinity.is_empty() {
                                String::new()
                            } else {
                                format!(" · beside {}", affinity.join(", "))
                            }
                        ),
                    );
                }
                if !prof.affinity.is_empty() {
                    note(&mut t, "affinity is advisory in v0 — recorded and shown, not enforced (P7's cells)");
                }
            }
            if who.is_empty() {
                note(
                    &mut t,
                    "no body named — the profile is judged on its own against this ground",
                );
            }
        }
        "template" | "binding" => {
            let who = Some(s_of(draft.get("name").unwrap_or(&Value::Null)))
                .filter(|s| !s.is_empty())
                .or_else(|| r#ref.clone())
                .unwrap_or_default();
            if bodies.contains_key(&who) {
                name_body(Some(&who), &mut named);
            } else {
                for b in bodies.values() {
                    let bk = b["kind"].as_str().unwrap_or_default();
                    if (kind == "template" && bk == "resident")
                        || (kind == "binding" && bk == "firmware")
                    {
                        name_body(b["name"].as_str(), &mut named);
                    }
                }
            }
        }
        "act" => {
            let tool = Some(s_of(draft.get("tool").unwrap_or(&Value::Null)))
                .filter(|s| !s.is_empty())
                .or_else(|| r#ref.clone())
                .unwrap_or_default();
            let spec = tools::declared(&decls, &tool).cloned();
            t["tool"] = json!(tool);
            match &spec {
                None => note(
                    &mut t,
                    format!("no tool named {} lives on this shelf", repr_str(&tool)),
                ),
                Some(spec) if !held => {
                    let cls = tools::consequence_of(spec, None);
                    t["level"] =
                        json!(level_for(&cls, tools::master(spec))
                            .map_err(|e| refused(e.to_string()))?);
                    t["class"] = json!(cls);
                }
                Some(_) => {}
            }
            let (svc, declared) = service_touched(g, scope, &mut t, "tool", &tool).await?; // P6.5 sp1: the service the act calls
            for n in &declared {
                name_body(Some(n), &mut named);
            }
            if let Some(first) = named.first() {
                let to = svc
                    .as_ref()
                    .map(|s| s_of(&s["did"]))
                    .unwrap_or_else(|| format!("tool:{tool}"));
                push(&mut t, "chains", json!(format!("H → {first} → {to}")));
            }
        }
        "service" => {
            // P6.5 sp1: a change on the shelf — retiring (consequential, L2), versioning,
            // restoring a service: the kernel reads its row, names the bodies that declared it,
            // and says where it stands on the ladder
            let who = Some(s_of(draft.get("name").unwrap_or(&Value::Null)))
                .filter(|s| !s.is_empty())
                .or_else(|| r#ref.clone())
                .unwrap_or_default();
            let svc = if who.is_empty() {
                None
            } else {
                services_live::get(g.client(), scope, &who).await?
            };
            if !held {
                t["class"] = json!(services_live::RETIRE_CLASS);
                t["level"] = json!(services_live::RETIRE_LEVEL);
            }
            match svc {
                None => note(
                    &mut t,
                    format!(
                        "no service named {} is on the shelf — \"what services are here?\" lists them",
                        repr_str(&who)
                    ),
                ),
                Some(svc) => {
                    let (sk, sn) = (s_of(&svc["kind"]), s_of(&svc["name"]));
                    let (_svc, declared) = service_touched(g, scope, &mut t, &sk, &sn).await?;
                    for n in &declared {
                        name_body(Some(n), &mut named);
                    }
                    push(&mut t, "chains", json!(format!("H → the kernel → {}", s_of(&svc["did"]))));
                    let manifest = &svc["manifest"];
                    // P6.5 sp2: a change on an MCP server touches every tool listed under it; a
                    // change on an MCP-born tool names the server it came through
                    if sk == "mcp" {
                        let under = mcp_live::tools_of(g, scope, &sn, false).await?;
                        for u in &under {
                            let un = s_of(&u["name"]);
                            let (_u, dec) = service_touched(g, scope, &mut t, "tool", &un).await?;
                            for n in &dec {
                                name_body(Some(n), &mut named);
                            }
                        }
                        let transport = manifest.get("transport").map(python_str).unwrap_or_else(|| "?".into());
                        let locator = manifest.get("locator").filter(|v| truthy(v)).map(python_str).unwrap_or_default();
                        let tail = if under.is_empty() {
                            "no tools under it".to_string()
                        } else {
                            format!(
                                "{} tool{} under it: {}",
                                under.len(),
                                if under.len() != 1 { "s" } else { "" },
                                under
                                    .iter()
                                    .map(|u| format!("{} ({})", s_of(&u["name"]), s_of(&u["state"])))
                                    .collect::<Vec<_>>()
                                    .join(", ")
                            )
                        };
                        note(
                            &mut t,
                            format!(
                                "{who} is an MCP server ({transport}, at {}) — {tail}",
                                mcp_live::locator_words(&locator)
                            ),
                        );
                    } else if sk == "tool" && truthy(get(manifest, "server")) {
                        note(
                            &mut t,
                            format!(
                                "{who} came through the {} MCP server (tools/call at the one door)",
                                python_str(get(manifest, "server"))
                            ),
                        );
                    }
                    if svc["state"].as_str() == Some("retired") {
                        note(
                            &mut t,
                            format!(
                                "{who} is already retired (since {}) — restore is the step from there",
                                cut_chars(&s_of(&svc["since"]), 16)
                            ),
                        );
                    } else {
                        let health = match &svc["last_health"] {
                            Value::Null => " · never probed".to_string(),
                            lh => format!(
                                " · last health: {}",
                                match lh["ok"] {
                                    Value::Bool(true) => "ok",
                                    Value::Bool(false) => "not ok",
                                    _ => "not probed",
                                }
                            ),
                        };
                        note(
                            &mut t,
                            format!(
                                "{who} stands {} on the ladder, version {}{health}",
                                s_of(&svc["state"]),
                                python_str(&svc["version"])
                            ),
                        );
                    }
                }
            }
        }
        _ => unreachable!("the kind was checked"),
    }

    for n in &named {
        let b = bodies.get(n);
        push(
            &mut t,
            "bodies",
            json!({"name": n, "kind": b.map(|b| b["kind"].clone()).unwrap_or(Value::Null),
                                       "did": b.map(|b| b["did"].clone()).unwrap_or(Value::Null), "joined": b.is_some()}),
        );
    }
    let dids: Vec<String> = t["bodies"]
        .as_array()
        .unwrap()
        .iter()
        .filter_map(|b| b["did"].as_str().map(str::to_string))
        .collect();
    let cost = cost_of(g, &dids).await?;
    let mut by_name = Map::new();
    for b in t["bodies"].as_array().unwrap() {
        if let Some(c) = b["did"].as_str().and_then(|d| cost.get(d)) {
            by_name.insert(s_of(&b["name"]), c.clone());
        }
    }
    t["cost"] = Value::Object(by_name);
    Ok(t)
}

/// `mitl.impact`: the door — the ground read and the verdict judged here, by rule; the
/// words asked of MITL as an ordinary ask (its journey, its reply, its marker) filed under
/// the change's marker — else the session's latest objective — so the confirm that
/// follows can show it.
pub async fn impact(
    g: &mut Ground,
    w: &World,
    change: &Value,
    person: &str,
    session: Option<&str>,
) -> Result<Value, RoadError> {
    let t = read_ground(g, w, change).await?;
    let v = verdict(&t);
    let ground = describe(&t);
    let text = ask_text(&t, v, &ground);
    let parent = match t["marker"].as_str().filter(|m| !m.is_empty()) {
        Some(m) => Some(m.to_string()),
        None => latest_objective(g, session).await?,
    };
    let filed = crate::asks::submit_ask(
        g,
        w,
        crate::asks::Submit {
            text,
            person: person.to_string(),
            to: Some(vec![NAME.to_string()]),
            session: session.map(str::to_string),
            parent_marker: parent.clone(),
            kind: Some("thought".into()),
            ..Default::default()
        },
    )
    .await?;
    let aid = filed.ids().first().cloned();
    let mut out = shape(&t, v, aid.as_deref(), parent.as_deref());
    out["ground"] = json!(ground);
    out["expansion"] = json!(EXPANSION);
    Ok(out)
}
