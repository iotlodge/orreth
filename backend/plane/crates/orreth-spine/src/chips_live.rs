// PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch Phase 8 THE WORKSHOP sp6, THE TWO CHIPS: the ground half · 2026-10-09
//! THE TWO CHIPS on the ground — `orreth_spine.chips` ported (canon 0010 §8 · 0005 Phase 8 sp6),
//! schema 9: `spine_keychecks` (the standing key-check's record) and the two columns the chips'
//! evidence rides on an experiment's row (`claims` · `diff`). The evidence the chips read is this
//! kernel's record: THE TRIAL LIFE'S CLAIMS (its join in the experiment room against the agent's
//! standing self and the candidate's hash), THE CANDIDATE'S DIFF (against the standing version's
//! manifest on the shelf), THE REFUSALS GROUND (the bodies turned away at the join and the desk)
//! and THE SEATS (the people seated by the ceremony, the bodies alive). THE KEY-CHECK BEAT asks
//! every seated body on the cadence to prove who and what it is — the desk's challenge repeated
//! over the rail — and verifies the proof the body wrote on the row (`desk::prove`); the body never
//! marks itself proven. The verdicts feed the metric `key_checks_failed` and the kernel's seventh
//! watch.

use crate::chips::{self, KERNEL, KEYCHECK_ASKED, KEYCHECK_CMD, KEYCHECK_VERDICT, KEYCHECK_WINDOW_H};
use crate::ground::Ground;
use crate::py::python_str;
use crate::world::{isoformat, json_text, RoadError, World};
use serde_json::{json, Value};
use std::time::SystemTime;
use tokio_postgres::{GenericClient, Transaction};

async fn fact(tx: &Transaction<'_>, w: &World, type_: &str, r#ref: &str, mut payload: Value, by: Vec<String>) -> Result<(), RoadError> {
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
        marker: None,
    }
    .mint()?;
    crate::outbox::add_row(tx, &crate::envelope::encode(&e)?, e["message_id"].as_str().unwrap_or_default()).await?;
    Ok(())
}

// ---- the evidence the chips read ----

/// `chips.trial_life`: the trial life's join in the experiment room, with whether its wear is still open.
pub async fn trial_life<C: GenericClient>(c: &C, exp: &Value) -> Result<Value, RoadError> {
    let agent = python_str(&exp["agent"]);
    let room = python_str(&exp["room"]);
    let Some(r) = c
        .query_opt(
            "SELECT did, life, template_hash, scope FROM spine_joins WHERE name = $1 AND scope = $2 ORDER BY join_id DESC LIMIT 1",
            &[&agent, &room],
        )
        .await?
    else {
        return Ok(Value::Null);
    };
    let did: String = r.get(0);
    let life: i32 = r.get(1);
    let open: i64 = c
        .query_one("SELECT count(*) FROM spine_wear WHERE did = $1 AND life = $2 AND until IS NULL", &[&did, &life])
        .await?
        .get(0);
    Ok(json!({"did": did, "life": life, "template_hash": r.get::<_, String>(2), "scope": r.get::<_, String>(3), "wear_open": open > 0}))
}

/// `chips.standing_did`: the agent's standing self — its latest join OUTSIDE the experiment room.
pub async fn standing_did<C: GenericClient>(c: &C, scope: &str, exp: &Value) -> Result<Option<String>, RoadError> {
    let agent = python_str(&exp["agent"]);
    let room = python_str(&exp["room"]);
    Ok(c
        .query_opt(
            "SELECT did FROM spine_joins WHERE name = $1 AND scope <> $2 AND (scope = $3 OR scope LIKE $3 || '/%') ORDER BY join_id DESC LIMIT 1",
            &[&agent, &room, &scope],
        )
        .await?
        .map(|r| r.get(0)))
}

pub async fn claims_for<C: GenericClient>(c: &C, scope: &str, exp: &Value) -> Result<Value, RoadError> {
    let trial = trial_life(c, exp).await?;
    let standing = standing_did(c, scope, exp).await?;
    Ok(chips::lease_claims(exp, &trial, standing.as_deref()))
}

/// `chips.diff_for`: the candidate's diff against the standing version's manifest on the shelf.
pub async fn diff_for<C: GenericClient>(c: &C, scope: &str, exp: &Value) -> Result<Value, RoadError> {
    let mut current = Value::Null;
    if exp["current_version"].as_i64().is_some_and(|v| v > 0) {
        if let Some(row) = crate::services_live::get(c, scope, &format!("{}.template", python_str(&exp["agent"]))).await? {
            current = row["manifest"].clone();
        }
    }
    Ok(chips::capability_diff(&current, &exp["candidate"]))
}

/// `chips.refusals_for`: THE REFUSALS GROUND — the join's refusals and the desk's denials over the window.
pub async fn refusals_for<C: GenericClient>(c: &C, scope: &str, name: Option<&str>, hours: i64) -> Result<Value, RoadError> {
    let mut rows: Vec<(String, String, String, Value, SystemTime, &str)> = Vec::new();
    let has = |t: &str| format!("SELECT to_regclass('{t}') IS NOT NULL");
    let refusals_stand: bool = c.query_one(&has("spine_refusals"), &[]).await?.get(0);
    if refusals_stand {
        for r in c
            .query(
                "SELECT name, did, kind, reasons, refused_at FROM spine_refusals WHERE (scope = $1 OR scope LIKE $1 || '/%') \
                 AND refused_at > now() - make_interval(hours => $2::int) AND ($3::text IS NULL OR name = $3) ORDER BY refusal_id DESC LIMIT 20",
                &[&scope, &(hours as i32), &name],
            )
            .await?
        {
            let reasons = json_text(Some(&r.get::<_, String>(3))).unwrap_or_else(|| json!([r.get::<_, String>(3)]));
            rows.push((r.get(0), r.get(1), r.get(2), reasons, r.get(4), "the join"));
        }
    }
    let desk_stands: bool = c.query_one(&has("spine_desk"), &[]).await?.get(0);
    if desk_stands {
        for r in c
            .query(
                "SELECT name, did, kind, updated_at FROM spine_desk WHERE (scope = $1 OR scope LIKE $1 || '/%') AND status = 'denied' \
                 AND updated_at > now() - make_interval(hours => $2::int) AND ($3::text IS NULL OR name = $3) ORDER BY updated_at DESC LIMIT 20",
                &[&scope, &(hours as i32), &name],
            )
            .await?
        {
            rows.push((r.get(0), r.get(1), r.get(2), json!(["denied at the desk"]), r.get(3), "the desk"));
        }
    }
    rows.sort_by(|a, b| b.4.cmp(&a.4));
    Ok(Value::Array(
        rows.into_iter()
            .take(20)
            .map(|(n, d, k, reasons, at, door)| json!({"name": n, "did": d, "kind": k, "reasons": reasons, "at": isoformat(at), "door": door}))
            .collect(),
    ))
}

/// `chips.seats_held`: THE CEREMONY AND THE SEATS as the identity chip holds them.
pub async fn seats_held<C: GenericClient>(c: &C, scope: &str) -> Result<Value, RoadError> {
    let mut people = serde_json::Map::new();
    for r in c
        .query(
            "SELECT role, count(*) FROM spine_seats WHERE left_at IS NULL AND expiry > now() AND role <> 'body' AND (scope = $1 OR scope LIKE $1 || '/%') GROUP BY role", // W113: a lease is a seat with the role `body` — never a person
            &[&scope],
        )
        .await?
    {
        people.insert(r.get::<_, String>(0), json!(r.get::<_, i64>(1)));
    }
    let bodies: i64 = c
        .query_one("SELECT count(*) FROM spine_leases WHERE until > now() AND (scope = $1 OR scope LIKE $1 || '/%')", &[&scope])
        .await?
        .get(0);
    Ok(json!({"people": people, "bodies": bodies, "keychecks": keycheck_tally(c, scope).await?}))
}

// ---- the key-check on the ground ----

/// `chips.keycheck_tally`: the checks of the window — verified · failed · pending, the latest, the cadence.
pub async fn keycheck_tally<C: GenericClient>(c: &C, scope: &str) -> Result<Value, RoadError> {
    let r = c
        .query_one(
            "SELECT count(*) FILTER (WHERE verified_at IS NOT NULL), count(*) FILTER (WHERE ok IS FALSE), \
             count(*) FILTER (WHERE verified_at IS NULL), max(verified_at) FROM spine_keychecks \
             WHERE (scope = $1 OR scope LIKE $1 || '/%') AND asked_at > now() - make_interval(hours => $2::int)",
            &[&scope, &(KEYCHECK_WINDOW_H as i32)],
        )
        .await?;
    Ok(json!({"checked": r.get::<_, i64>(0), "failed": r.get::<_, i64>(1), "pending": r.get::<_, i64>(2),
              "last": r.get::<_, Option<SystemTime>>(3).map(isoformat), "cadence": chips::cadence_s()}))
}

/// `chips.key_checks_failed`: the watch metric — the failed checks of the last day.
pub async fn key_checks_failed<C: GenericClient>(c: &C, scope: &str) -> Result<i64, RoadError> {
    Ok(keycheck_tally(c, scope).await?["failed"].as_i64().unwrap_or(0))
}

/// `chips.listing`: the checks, newest first.
pub async fn listing<C: GenericClient>(c: &C, scope: &str, limit: i64) -> Result<Vec<Value>, RoadError> {
    let rows = c
        .query(
            "SELECT check_id, name, did, asked_at, answered_at, ok, words, verified_at FROM spine_keychecks \
             WHERE (scope = $1 OR scope LIKE $1 || '/%') ORDER BY asked_at DESC LIMIT $2",
            &[&scope, &limit],
        )
        .await?;
    Ok(rows
        .iter()
        .map(|r| {
            json!({"check_id": r.get::<_, String>(0), "name": r.get::<_, String>(1), "did": r.get::<_, String>(2),
                   "asked_at": isoformat(r.get::<_, SystemTime>(3)), "answered_at": r.get::<_, Option<SystemTime>>(4).map(isoformat),
                   "ok": r.get::<_, Option<bool>>(5), "words": r.get::<_, Option<String>>(6),
                   "verified_at": r.get::<_, Option<SystemTime>>(7).map(isoformat)})
        })
        .collect())
}

/// The key-check's face for the glass: the listing, the tally and the line.
pub async fn card<C: GenericClient>(c: &C, scope: &str) -> Result<Value, RoadError> {
    let t = keycheck_tally(c, scope).await?;
    let n = |k: &str| t[k].as_i64().unwrap_or(0);
    Ok(json!({"keychecks": listing(c, scope, 50).await?, "tally": t,
              "words": chips::keycheck_words(n("checked"), n("failed"), n("pending"), n("cadence"))}))
}

/// `chips.command_for`: the kernel's command to one body — prove yourself; the nonce rides it.
pub fn command_for(w: &World, check_id: &str, did: &str, name: &str, nonce: &str) -> Result<Value, RoadError> {
    let payload = json!({"ref": check_id, "hash": crate::hash::content_hash(&json!({"did": did, "nonce": nonce})),
                         "target": name, "did": did, "nonce": nonce});
    Ok(crate::envelope::Mint {
        kind: "command".into(),
        r#type: KEYCHECK_CMD.into(),
        universe_id: w.scope.clone(),
        scope_path: w.scope.clone(),
        payload,
        correlation_id: Some(check_id.to_string()),
        authority_chain: Some(vec![KERNEL.to_string()]),
        aggregate: None,
        marker: None,
    }
    .mint()?)
}

/// THE KEY-CHECK BEAT (`chips.beat`): (1) verify every answered check, fail the silent past the desk's
/// wait — each verdict a fact; (2) challenge every seated body whose last challenge is older than
/// the cadence — a row, a fact, the command over the rail to the body's own queue. `publish` false
/// (a proof reading the ground alone) records the challenge without the rail.
pub async fn beat(g: &mut Ground, w: &World, publish: bool) -> Result<Vec<String>, RoadError> {
    let cad = chips::cadence_s();
    let mut moved = Vec::new();
    if cad <= 0 {
        return Ok(moved);
    }
    // 1. the verdicts
    let open = g
        .client()
        .query(
            "SELECT check_id, did, name, nonce, joined_as, public_key, sig, what, answered_at IS NOT NULL, \
             extract(epoch FROM (now() - asked_at))::float8 FROM spine_keychecks WHERE verified_at IS NULL AND (scope = $1 OR scope LIKE $1 || '/%')",
            &[&w.scope],
        )
        .await?;
    for r in open {
        let cid: String = r.get(0);
        let did: String = r.get(1);
        let name: String = r.get(2);
        let nonce: String = r.get(3);
        let joined_as: Option<String> = r.get(4);
        let answered: bool = r.get(8);
        let waited: f64 = r.get::<_, Option<f64>>(9).unwrap_or(0.0);
        let answer = if answered {
            let sig = r.get::<_, Option<String>>(6).and_then(|s| json_text(Some(&s))).unwrap_or(Value::Null);
            json!({"public_key": r.get::<_, Option<String>>(5), "sig": sig, "what": r.get::<_, Option<String>>(7)})
        } else {
            Value::Null
        };
        let v = chips::keycheck_verdict(&did, &nonce, &answer, joined_as.as_deref(), waited);
        let Some(ok) = v["ok"].as_bool() else { continue };
        let words = python_str(&v["words"]);
        let tx = g.client_mut().transaction().await?;
        tx.execute("UPDATE spine_keychecks SET ok = $1, words = $2, verified_at = clock_timestamp() WHERE check_id = $3", &[&ok, &words, &cid])
            .await?;
        fact(&tx, w, KEYCHECK_VERDICT, &cid, json!({"did": did, "name": name, "ok": ok, "words": words}), vec![KERNEL.into()]).await?;
        tx.commit().await?;
        moved.push(if ok { format!("{name}: {words}") } else { format!("{name}: FAILED — {words}") });
    }
    // 2. the challenges
    let due = g
        .client()
        .query(
            "SELECT l.did, l.name, extract(epoch FROM (now() - k.asked_at))::float8 FROM spine_leases l \
             LEFT JOIN LATERAL (SELECT asked_at FROM spine_keychecks WHERE did = l.did ORDER BY asked_at DESC LIMIT 1) k ON true \
             WHERE l.until > now() AND (l.scope = $1 OR l.scope LIKE $1 || '/%')",
            &[&w.scope],
        )
        .await?;
    for r in due {
        let did: String = r.get(0);
        let name: String = r.get(1);
        let ago: Option<f64> = r.get(2);
        if !chips::keycheck_due(ago, cad) {
            continue;
        }
        let joined_as: Option<String> = g
            .client()
            .query_opt("SELECT template_hash FROM spine_joins WHERE did = $1 ORDER BY join_id DESC LIMIT 1", &[&did])
            .await?
            .map(|j| j.get(0));
        let cid = format!("kc_{}", crate::world::token_hex(6));
        let nonce = crate::world::token_hex(16);
        let tx = g.client_mut().transaction().await?;
        tx.execute(
            "INSERT INTO spine_keychecks (check_id, scope, did, name, nonce, joined_as) VALUES ($1, $2, $3, $4, $5, $6)",
            &[&cid, &w.scope, &did, &name, &nonce, &joined_as],
        )
        .await?;
        fact(&tx, w, KEYCHECK_ASKED, &cid, json!({"did": did, "name": name}), vec![KERNEL.into()]).await?;
        tx.commit().await?;
        if publish {
            let env = command_for(w, &cid, &did, &name, &nonce)?;
            crate::invoke::publish_command(&w.rabbit_url, &env, &w.ns).await?;
        }
        moved.push(format!("{name}: challenged to prove who and what it is"));
    }
    Ok(moved)
}
