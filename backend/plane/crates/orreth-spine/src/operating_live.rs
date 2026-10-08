// PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch Phase 8 THE WORKSHOP sp5, THE OPERATING STATE: the ground half · 2026-10-08
// Amended: Claude Fable 5.1 (claude-fable-5-1) — THE GROUND CONNECTIONS CURE (2026-10-08): the ground's watch declared at light beside the five · 2026-10-08
//! THE OPERATING STATE on the ground — `orreth_spine.operating` ported (canon 0010 §7 · 0005
//! Phase 8 sp5), schema 8: the five measurements read LIVE off the ground (the grader's verdicts
//! on live replies, the served asks and their markers, the serves' latency against their class,
//! the thumbs given, the meter's lines that wear an ask); the kernel's five watches and THE
//! OPERATING STATE intention declared at light; the feedback door; summon generalized (the
//! includes of a session); THE GRADE BEAT handing the last hour's live replies to the grader
//! under each reply's own marker. The import of a repo'd graph runs in the body (Python); this
//! kernel reads its words off the journey like any hop.

use crate::ground::Ground;
use crate::operating::{self, BASE_INCLUDES, FEEDBACK_GIVEN, GRADE_HEAD, INCLUDE_DISMISSED, INCLUDE_SUMMONED, KERNEL, MEASUREMENTS};
use crate::py::{python_str, truthy};
use crate::world::{isoformat, json_text, refused, RoadError, World};
use serde_json::{json, Value};
use std::time::SystemTime;
use tokio_postgres::GenericClient;

// ---- the fact ----

async fn fact(
    tx: &tokio_postgres::Transaction<'_>,
    w: &World,
    type_: &str,
    r#ref: &str,
    mut payload: Value,
    by: Vec<String>,
    marker: Option<Value>,
) -> Result<(), RoadError> {
    let hash = crate::hash::content_hash(&payload);
    payload["ref"] = json!(r#ref);
    payload["hash"] = json!(hash);
    let e = crate::envelope::Mint {
        kind: "event".into(),
        r#type: type_.into(),
        universe_id: w.scope.clone(),
        scope_path: w.scope.clone(),
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

// ---- the five, measured ----

fn m(name: &str, num: f64, den: f64) -> Value {
    let v = operating::ratio(num, den);
    json!({"value": operating::value_of(v), "num": num, "den": den, "words": operating::measure_words(name, v, num, den)})
}

/// `operating.measure`: the five measurements, live — `{name: {value, num, den, words}}`.
pub async fn measure<C: GenericClient>(c: &C, scope: &str) -> Result<Value, RoadError> {
    let mut out = json!({});
    let grades = c
        .query("SELECT verdict FROM spine_verdicts WHERE scope = $1 AND on_ask IS NOT NULL", &[&scope])
        .await?;
    let passed = grades
        .iter()
        .filter(|r| {
            let v = json_text(Some(&r.get::<_, String>(0))).unwrap_or(json!({}));
            operating::pass_grade(v["grade"].as_str())
        })
        .count();
    out["trust"] = m("trust", passed as f64, grades.len() as f64);
    let r = c
        .query_one(
            "SELECT count(*) FILTER (WHERE marker IS NOT NULL AND reply IS NOT NULL), count(*) FROM spine_asks WHERE scope = $1 AND \
             status = 'replied' AND served_by <> $2",
            &[&scope, &KERNEL],
        )
        .await?;
    out["recall"] = m("recall", r.get::<_, i64>(0) as f64, r.get::<_, i64>(1) as f64);
    let rows = c
        .query(
            "SELECT extract(epoch FROM (a.replied_at - a.asked_at))::float8, m.kind, p.kind FROM spine_asks a LEFT JOIN spine_markers m ON \
             m.marker_id = a.marker LEFT JOIN spine_markers p ON p.marker_id = m.parent WHERE a.scope = $1 AND a.status = 'replied' AND \
             a.served_by <> $2 AND a.replied_at IS NOT NULL AND a.replied_at >= now() - make_interval(hours => $3::int)",
            &[&scope, &KERNEL, &(operating::EFFICIENCY_WINDOW_H as i32)],
        )
        .await?;
    let inside = rows
        .iter()
        .filter(|r| {
            let secs: f64 = r.get(0);
            let (_, limit) = operating::latency_class(r.get::<_, Option<String>>(1).as_deref(), r.get::<_, Option<String>>(2).as_deref());
            secs <= limit
        })
        .count();
    out["efficiency"] = m("efficiency", inside as f64, rows.len() as f64);
    let r = c
        .query_one("SELECT count(*) FILTER (WHERE sign >= 0), count(*) FROM spine_feedback WHERE scope = $1", &[&scope])
        .await?;
    out["experience"] = m("experience", r.get::<_, i64>(0) as f64, r.get::<_, i64>(1) as f64);
    let r = c
        .query_one(
            "SELECT coalesce(sum(usd) FILTER (WHERE ask IS NOT NULL), 0)::float8, coalesce(sum(usd), 0)::float8 FROM spine_meter WHERE scope = $1",
            &[&scope],
        )
        .await?;
    out["cost"] = m("cost", r.get::<_, f64>(0), r.get::<_, f64>(1));
    Ok(out)
}

// ---- the watches and the intention at light ----

/// `operating.watches_at_light`: the kernel's five watches — and the ground's (the cure,
/// 2026-10-08: `ground_connections >= ceiling − reserve`) — once per world.
pub async fn watches_at_light(g: &Ground, scope: &str) -> Result<Vec<String>, RoadError> {
    let have: Vec<String> = g
        .client()
        .query("SELECT name FROM spine_watches WHERE scope = $1 AND added_by = $2", &[&scope, &KERNEL])
        .await?
        .iter()
        .map(|r| r.get(0))
        .collect();
    let mut made = Vec::new();
    for name in MEASUREMENTS {
        if have.iter().any(|h| h == name) {
            continue;
        }
        let w = operating::measurement_watch(name);
        crate::monitor::add_watch(g, scope, name, name, operating::WATCH_OP, w["threshold"].as_f64().unwrap_or(1.0), KERNEL).await?;
        made.push(name.to_string());
    }
    if !have.iter().any(|h| h == operating::GROUND_WATCH) {
        let w = operating::ground_watch(&crate::monitor::connections_declared(g).await?);
        crate::monitor::add_watch(g, scope, operating::GROUND_WATCH, operating::GROUND_WATCH, ">=", w["threshold"].as_f64().unwrap_or(70.0), KERNEL).await?;
        made.push(operating::GROUND_WATCH.to_string());
    }
    Ok(made)
}

/// `operating.intention_at_light`: THE OPERATING STATE declared beside Resiliency, once per world.
pub async fn intention_at_light(g: &mut Ground, w: &World) -> Result<Value, RoadError> {
    let o = operating::operating();
    crate::intent_live::declared(
        g,
        w,
        crate::intent_live::Declare {
            words: python_str(&o["words"]),
            serves: python_str(&o["serves"]),
            kind: "kernel".into(),
            by: KERNEL.into(),
            interests: vec![crate::intent::WATCH_RED.into()],
            planner: "planner".into(),
            runner: Some("critic".into()),
            every_s: None,
            gates: None,
            watches: Some(MEASUREMENTS.iter().map(|s| s.to_string()).collect()),
        },
    )
    .await
}

// ---- feedback ----

/// `operating.give_feedback`: a human's thumb on a reply — routine, recorded, a fact.
pub async fn give_feedback(g: &mut Ground, w: &World, person: &str, ask_id: &str, sign: i64, words: Option<&str>) -> Result<Value, RoadError> {
    let row = g
        .client()
        .query_opt("SELECT status, served_by FROM spine_asks WHERE ask_id = $1 AND scope = $2", &[&ask_id, &w.scope])
        .await?;
    let Some(row) = row else {
        return Err(refused("no such ask here"));
    };
    let status: String = row.get(0);
    let served_by: Option<String> = row.get(1);
    if status != "replied" {
        return Err(refused(format!("the ask is {status} — a thumb goes on a reply")));
    }
    let sign: i32 = if sign > 0 { 1 } else if sign < 0 { -1 } else { 0 };
    let fid = format!("fb_{}", crate::world::token_hex(6));
    let tx = g.client_mut().transaction().await?;
    tx.execute(
        "INSERT INTO spine_feedback (feedback_id, scope, ask_id, person, sign, words) VALUES ($1, $2, $3, $4, $5, $6)",
        &[&fid, &w.scope, &ask_id, &person, &sign, &words],
    )
    .await?;
    fact(&tx, w, FEEDBACK_GIVEN, &fid, json!({"ask": ask_id, "sign": sign, "words": words, "by": person, "served_by": served_by}), vec![person.to_string()], None).await?;
    tx.commit().await?;
    Ok(json!({"feedback_id": fid, "ask_id": ask_id, "sign": sign,
              "words": "thank you — recorded; it feeds the Experience measurement and the grader's evidence, never a body directly"}))
}

// ---- summon, generalized ----

/// `operating.summonable`: may this body be summoned?
pub async fn summonable<C: GenericClient>(c: &C, scope: &str, body: &str) -> Result<(bool, String), RoadError> {
    if body == "mitl" {
        return Ok((false, "MITL is summoned by its own word — say “summon MITL”".into()));
    }
    let row = crate::services_live::get(c, scope, &format!("{body}.template")).await?;
    let Some(row) = row.filter(|r| r["state"] != json!("retired")) else {
        return Ok((false, format!("no template named {body} stands on the shelf — only a body with a template is summoned")));
    };
    if row["manifest"]["kind"] == json!("helper") {
        return Ok((false, format!("{body} is a helper — a life under its creator, never summoned (0010 §6)")));
    }
    if !truthy(&row["manifest"]["summonable"]) {
        return Ok((false, format!("{body}'s template does not declare it summonable — a cut of the template with `summonable: true` opens it")));
    }
    Ok((true, "summonable".into()))
}

/// `operating.summon`: the generalized toggle — a row, its marker, its fact; summoned or dismissed.
pub async fn summon(g: &mut Ground, w: &World, person: &str, body: &str, session: Option<&str>, on: bool) -> Result<Value, RoadError> {
    let body = body.trim().to_lowercase();
    let (ok, why) = summonable(g.client(), &w.scope, &body).await?;
    if !ok {
        return Err(refused(why));
    }
    let parent = crate::mitl_live::latest_objective(g, session).await?;
    let mid = crate::markers_live::new_id();
    let state = if on { "summoned" } else { "dismissed" };
    let r#ref = session.unwrap_or(person).to_string();
    let tx = g.client_mut().transaction().await?;
    crate::markers_live::insert(&tx, &mid, "action", parent.as_deref(), &r#ref, person, Some(&format!("{body} {state}")), &w.scope).await?;
    tx.execute(
        "INSERT INTO spine_includes (scope, session, person, body, state, marker) VALUES ($1, $2, $3, $4, $5, $6)",
        &[&w.scope, &session, &person, &body, &state, &mid],
    )
    .await?;
    fact(
        &tx,
        w,
        if on { INCLUDE_SUMMONED } else { INCLUDE_DISMISSED },
        &r#ref,
        json!({"by": person, "session": session, "body": body}),
        vec![person.to_string()],
        Some(json!({"kind": "action", "id": mid, "parent": parent, "by": person})),
    )
    .await?;
    tx.commit().await?;
    Ok(json!({"summoned": on, "state": state, "body": body, "person": person, "session": session, "marker": mid,
              "words": operating::summon_words(&body, on, session)}))
}

/// `operating.summoned`: the bodies summoned into this session (or this person's crew).
pub async fn summoned<C: GenericClient>(c: &C, scope: &str, session: Option<&str>, person: Option<&str>) -> Result<Vec<String>, RoadError> {
    let rows = match session {
        Some(s) => {
            c.query(
                "SELECT DISTINCT ON (body) body, state FROM spine_includes WHERE session = $1 AND scope = $2 ORDER BY body, row_id DESC",
                &[&s, &scope],
            )
            .await?
        }
        None => {
            c.query(
                "SELECT DISTINCT ON (body) body, state FROM spine_includes WHERE session IS NULL AND person = $1 AND scope = $2 ORDER BY body, row_id DESC",
                &[&person.unwrap_or(""), &scope],
            )
            .await?
        }
    };
    let mut out: Vec<String> = rows
        .iter()
        .filter(|r| r.get::<_, String>(1) == "summoned")
        .map(|r| r.get::<_, String>(0))
        .collect();
    out.sort();
    Ok(out)
}

/// `operating.includes`: the four of the third kind, and every body summoned into the session.
pub async fn includes<C: GenericClient>(c: &C, scope: &str, session: Option<&str>, person: Option<&str>) -> Result<Vec<String>, RoadError> {
    let mut out: Vec<String> = BASE_INCLUDES.iter().map(|s| s.to_string()).collect();
    for b in summoned(c, scope, session, person).await? {
        if !out.contains(&b) {
            out.push(b);
        }
    }
    Ok(out)
}

// ---- the grade beat ----

/// THE GRADE BEAT: a body's reply of the last hour not yet graded is handed to the grader under
/// the reply's own marker, a few per beat, never the reviewers' own words, never a grading ask.
pub async fn grade_beat(g: &mut Ground, w: &World) -> Result<Vec<String>, RoadError> {
    if matches!(std::env::var(operating::GRADE_DIAL).ok().as_deref().map(str::trim), Some("0") | Some("off") | Some("no")) {
        return Ok(Vec::new());
    }
    if crate::asks::absent(g, &w.scope, "grader").await?.is_some() {
        return Ok(Vec::new());
    }
    let mut reviewers: Vec<String> = g
        .client()
        .query(
            "SELECT DISTINCT did FROM spine_joins WHERE name IN ('grader', 'critic') AND (scope = $1 OR scope LIKE $1 || '/%')",
            &[&w.scope],
        )
        .await?
        .iter()
        .map(|r| r.get(0))
        .collect();
    if reviewers.is_empty() {
        reviewers.push("-".into());
    }
    let like = format!("{GRADE_HEAD}%");
    let rows = g
        .client()
        .query(
            "SELECT a.ask_id, a.person, a.text, a.reply, coalesce(j.name, 'a body'), a.marker FROM spine_asks a LEFT JOIN LATERAL (SELECT \
             name FROM spine_joins WHERE did = a.served_by ORDER BY join_id DESC LIMIT 1) j ON true WHERE a.scope = $1 AND a.status = \
             'replied' AND a.reply IS NOT NULL AND a.served_by <> $2 AND NOT (a.served_by = ANY($3)) AND a.replied_at >= now() - \
             make_interval(mins => $4::int) AND a.text NOT LIKE $5 AND a.ask_id NOT IN (SELECT ask_id FROM spine_grading WHERE scope = $1) \
             AND NOT EXISTS (SELECT 1 FROM spine_verdicts v WHERE v.on_ask = a.ask_id) ORDER BY a.replied_at LIMIT $6",
            &[&w.scope, &KERNEL, &reviewers, &(operating::GRADE_WINDOW_MIN as i32), &like, &operating::GRADE_PER_BEAT],
        )
        .await?;
    let mut asked = Vec::new();
    let todo: Vec<(String, Option<String>, String, String, String, Option<String>)> =
        rows.iter().map(|r| (r.get(0), r.get(1), r.get(2), r.get(3), r.get(4), r.get(5))).collect();
    for (ask_id, person, text, reply, who, marker) in todo {
        // the GRADING marker under the reply's own ask: the grader's ask hangs under it — the hull's EVENT edge by law
        let gm = crate::markers_live::set_marker(
            g,
            w,
            operating::GRADING_KIND,
            &ask_id,
            KERNEL,
            marker.as_deref(),
            Some(&format!("{who}'s reply handed to the grader")),
            None,
        )
        .await?;
        let made = crate::asks::submit_ask(
            g,
            w,
            crate::asks::Submit {
                text: operating::grade_ask(&ask_id, &who, &text, &reply),
                person: person.unwrap_or_else(|| KERNEL.into()),
                to: Some(vec!["grader".into()]),
                parent_marker: gm["id"].as_str().map(str::to_string),
                ..Default::default()
            },
        )
        .await?;
        let gid = made.ids().first().cloned().unwrap_or_default();
        g.client()
            .execute(
                "INSERT INTO spine_grading (ask_id, scope, grade_ask) VALUES ($1, $2, $3) ON CONFLICT (ask_id) DO NOTHING",
                &[&ask_id, &w.scope, &gid],
            )
            .await?;
        asked.push(format!("{ask_id} by {who} → the grader ({gid})"));
    }
    Ok(asked)
}

/// The verdicts on a live reply, for the door.
pub async fn live_verdicts<C: GenericClient>(c: &C, ask_id: &str) -> Result<Vec<Value>, RoadError> {
    Ok(c
        .query("SELECT verdict_id, by_name, verdict, words, sig, at FROM spine_verdicts WHERE on_ask = $1 ORDER BY at", &[&ask_id])
        .await?
        .iter()
        .map(|r| {
            json!({"verdict_id": r.get::<_, String>(0), "by_name": r.get::<_, String>(1),
                   "verdict": json_text(Some(&r.get::<_, String>(2))), "words": r.get::<_, String>(3),
                   "sig": r.get::<_, String>(4), "at": isoformat(r.get::<_, SystemTime>(5))})
        })
        .collect())
}
