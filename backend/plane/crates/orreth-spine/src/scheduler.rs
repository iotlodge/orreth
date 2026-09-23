// PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp4, the loops · 2026-09-23
//! The scheduler — a kernel organ (`orreth_spine.scheduler`; canon 0004:
//! three schedulers, one body). A SCHEDULE is a standing intention on the
//! ground: HUMAN (the identity's, CRUD through the door), ROLE (declared by a
//! body's template at its join), KERNEL (registered by the rig — required,
//! visible, NEVER editable). An OCCURRENCE of a human or role schedule is an
//! ask to its runner on the invoke rail, FRAMED as a duty (W21: the words,
//! the cadence, the window since the last run, the runner's own earlier
//! notes); a kernel occurrence acts directly. Rest is a recorded act, never a
//! deletion (rule 11).
//!
//! The tick runs under the scheduler BEAT (the beat lock): two kernels on one
//! ground never tick one world at once. What this bridge cannot run it leaves
//! due: the kernel's "run the harness" duty needs a body's mind, and the
//! bodies are Python's until the seam (P7 sp6) — the Python kernel's next
//! beat runs it.

use crate::ask::duty_text;
use crate::asks::{self, Submit};
use crate::beat;
use crate::ground::Ground;
use crate::intent::KINDS;
use crate::markers_live;
use crate::world::{iso_opt, isoformat, refused, token_hex, RoadError, World};
use serde_json::{json, Value};
use std::time::SystemTime;

pub const KERNEL_REQUIRED: &str = "kernel-required — visible, never editable";
/// The kernel's duty every mind with a golden set carries (the rig declares it).
pub const HARNESS_DUTY: &str = "run the harness against my golden set";

/// A standing intention lands. `first_in_s` None = due now.
#[allow(clippy::too_many_arguments)]
pub async fn add(
    g: &mut Ground,
    scope: &str,
    runner: &str,
    kind: &str,
    text: &str,
    every_s: i64,
    by: &str,
    first_in_s: Option<i64>,
) -> Result<String, RoadError> {
    if !KINDS.contains(&kind) {
        return Err(refused(format!("kind is one of {}", KINDS.join(", "))));
    }
    let sid = format!("sch_{}", token_hex(5));
    let mid = markers_live::new_id();
    let every = every_s as i32;
    let first = first_in_s.unwrap_or(0) as f64;
    let tx = g.client_mut().transaction().await?;
    markers_live::insert(&tx, &mid, "intention", None, &sid, by, None, scope).await?; // a root: WHY it beats
    tx.execute(
        "INSERT INTO spine_schedules (schedule_id, runner, kind, text, every_s, next_at, added_by, \
         scope, marker) VALUES ($1, $2, $3, $4, $5, now() + make_interval(secs => $6::float8), $7, \
         $8, $9)",
        &[&sid, &runner, &kind, &text, &every, &first, &by, &scope, &mid],
    )
    .await?;
    tx.commit().await?;
    Ok(sid)
}

/// Register once (a template's role schedule at every join; the kernel's
/// duties at every boot): the same intention is never doubled.
pub async fn declared(
    g: &mut Ground,
    scope: &str,
    runner: &str,
    kind: &str,
    text: &str,
    every_s: i64,
    by: &str,
) -> Result<String, RoadError> {
    let row = g
        .client()
        .query_opt(
            "SELECT schedule_id, marker FROM spine_schedules WHERE runner = $1 AND kind = $2 AND \
             text = $3 AND scope = $4",
            &[&runner, &kind, &text, &scope],
        )
        .await?;
    let Some(row) = row else {
        return add(g, scope, runner, kind, text, every_s, by, Some(every_s)).await;
    };
    let sid: String = row.get(0);
    let marker: Option<String> = row.get(1);
    if marker.is_none() {
        // declared before markers existed: it gets its intention now, once
        let mid = markers_live::new_id();
        let tx = g.client_mut().transaction().await?;
        markers_live::insert(&tx, &mid, "intention", None, &sid, by, None, scope).await?;
        tx.execute(
            "UPDATE spine_schedules SET marker = $1 WHERE schedule_id = $2",
            &[&mid, &sid],
        )
        .await?;
        tx.commit().await?;
    }
    Ok(sid)
}

/// The human's stop: recorded, reversible in the Record, never a delete.
/// `Ok(false)` — no such schedule; a kernel schedule refuses with one plain face.
pub async fn rest(g: &Ground, scope: &str, schedule_id: &str, by: &str) -> Result<bool, RoadError> {
    let row = g
        .client()
        .query_opt(
            "SELECT kind FROM spine_schedules WHERE schedule_id = $1 AND scope = $2",
            &[&schedule_id, &scope],
        )
        .await?;
    let Some(row) = row else {
        return Ok(false);
    };
    if row.get::<_, String>(0) == "kernel" {
        return Err(RoadError::Forbidden(KERNEL_REQUIRED.into()));
    }
    g.client()
        .execute(
            "UPDATE spine_schedules SET active = false, rested_by = $1, rested_at = now() WHERE \
             schedule_id = $2",
            &[&by, &schedule_id],
        )
        .await?;
    Ok(true)
}

/// The card's side B (P16): every schedule this runner runs, by kind.
pub async fn for_runner(g: &Ground, scope: &str, runner: &str) -> Result<Value, RoadError> {
    let rows = g
        .client()
        .query(
            "SELECT s.schedule_id, s.kind, s.text, s.every_s, s.next_at, s.last_at, s.active, \
             s.added_by, s.rested_by, s.rested_at, (SELECT count(*) FROM spine_occurrences o WHERE \
             o.schedule_id = s.schedule_id) FROM spine_schedules s WHERE s.runner = $1 AND s.scope \
             = $2 ORDER BY s.kind, s.added_at",
            &[&runner, &scope],
        )
        .await?;
    let mut out = json!({"human": [], "role": [], "kernel": []});
    for r in rows {
        let kind: String = r.get(1);
        let d = json!({
            "schedule_id": r.get::<_, String>(0), "text": r.get::<_, String>(2),
            "every_s": r.get::<_, i32>(3),
            "next_at": isoformat(r.get::<_, SystemTime>(4)),
            "last_at": iso_opt(r.get::<_, Option<SystemTime>>(5)),
            "active": r.get::<_, bool>(6), "added_by": r.get::<_, String>(7),
            "rested_by": r.get::<_, Option<String>>(8),
            "rested_at": iso_opt(r.get::<_, Option<SystemTime>>(9)),
            "occurrences": r.get::<_, i64>(10), "editable": kind != "kernel",
        });
        if let Some(list) = out[&kind].as_array_mut() {
            list.push(d);
        }
    }
    Ok(out)
}

/// The runner's own earlier notes on this duty — the first line of each
/// replied occurrence, newest first, today (the last 24 h).
pub async fn notes_for(
    g: &Ground,
    schedule_id: &str,
    limit: i64,
) -> Result<Vec<String>, RoadError> {
    let rows = g
        .client()
        .query(
            "SELECT a.reply FROM spine_occurrences o JOIN spine_asks a ON a.ask_id = o.ref WHERE \
             o.schedule_id = $1 AND a.status = 'replied' AND a.reply IS NOT NULL AND a.replied_at > \
             now() - interval '24 hours' ORDER BY a.replied_at DESC LIMIT $2",
            &[&schedule_id, &limit],
        )
        .await?;
    Ok(rows
        .iter()
        .filter_map(|r| {
            let rp: Option<String> = r.get(0);
            let first = rp
                .unwrap_or_default()
                .trim()
                .split('\n')
                .next()
                .unwrap_or("")
                .trim()
                .to_string();
            (!first.is_empty()).then_some(first)
        })
        .collect())
}

/// The last run's clock in the human's zone — `3:07 PM` (Python's
/// `strftime("%I:%M %p").lstrip("0")`), read off the ground's own tzdata;
/// a zone the ground does not know falls back to `HH:MM UTC`.
pub async fn clock(
    g: &Ground,
    at: Option<SystemTime>,
    zone: &str,
) -> Result<Option<String>, RoadError> {
    let Some(at) = at else {
        return Ok(None);
    };
    let local = g
        .client()
        .query_one(
            "SELECT to_char($1::timestamptz AT TIME ZONE $2, 'FMHH12:MI AM')",
            &[&at, &zone],
        )
        .await;
    match local {
        Ok(r) => Ok(Some(r.get(0))),
        Err(_) => {
            let r = g
                .client()
                .query_one(
                    "SELECT to_char($1::timestamptz AT TIME ZONE 'UTC', 'HH24:MI') || ' UTC'",
                    &[&at],
                )
                .await?;
            Ok(Some(r.get(0)))
        }
    }
}

/// The organ's beat: every due, active schedule occurs — human and role ones
/// as an ask to the runner on the rail (framed as a duty, W21) — and the next
/// beat is set. Returns what occurred. The beat is CLAIMED first: the kernel
/// that finds it held returns nothing. A kernel "run the harness" duty is
/// LEFT DUE here (it runs a body's mind — the Python kernel's beat takes it).
pub async fn tick(g: &mut Ground, w: &World, zone: &str) -> Result<Vec<Value>, RoadError> {
    if !beat::try_beat(g, &w.scope, "scheduler").await? {
        return Ok(Vec::new());
    }
    let out = tick_inner(g, w, zone).await;
    let _ = beat::end_beat(g, &w.scope, "scheduler").await;
    out
}

/// A due row: id · runner · kind · text · every_s · added_by · marker · last_at.
type Due = (
    String,
    String,
    String,
    String,
    i32,
    String,
    Option<String>,
    Option<SystemTime>,
);

async fn tick_inner(g: &mut Ground, w: &World, zone: &str) -> Result<Vec<Value>, RoadError> {
    let rows = g
        .client()
        .query(
            "SELECT schedule_id, runner, kind, text, every_s, added_by, marker, last_at FROM \
             spine_schedules WHERE active AND next_at <= now() AND scope = $1 ORDER BY next_at",
            &[&w.scope],
        )
        .await?;
    let due: Vec<Due> = rows
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
    let mut occurred = Vec::new();
    for (sid, runner, kind, text, every_s, by, marker, last_at) in due {
        if kind == "kernel" && text.starts_with("run the harness") {
            continue; // a mind's run: left due for the kernel that holds the bodies
        }
        let since = clock(g, last_at, zone).await?;
        let notes = notes_for(g, &sid, 3).await?;
        let framed = duty_text(&text, every_s as i64, since.as_deref(), &notes);
        let filed = asks::submit_ask(
            g,
            w,
            Submit {
                text: framed,
                person: by.clone(),
                to: Some(vec![runner.clone()]),
                parent_marker: marker.clone(),
                ..Default::default()
            },
        )
        .await?;
        let r#ref = filed.ids().into_iter().next();
        let oid = format!("occ_{}", token_hex(5));
        let every = every_s as f64;
        let tx = g.client_mut().transaction().await?;
        tx.execute(
            "INSERT INTO spine_occurrences (occurrence_id, schedule_id, ref) VALUES ($1, $2, $3)",
            &[&oid, &sid, &r#ref],
        )
        .await?;
        tx.execute(
            "UPDATE spine_schedules SET last_at = now(), next_at = now() + make_interval(secs => \
             $1::float8) WHERE schedule_id = $2",
            &[&every, &sid],
        )
        .await?;
        tx.commit().await?;
        occurred.push(json!({"schedule_id": sid, "runner": runner, "kind": kind, "ref": r#ref}));
    }
    Ok(occurred)
}
