// PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp4, the loops · 2026-09-23
// Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp6, the bodies' seam: the run OVER THE RAIL · the A/B arms · the Stable's four checks · 2026-09-24
//! The harness's WORLD CHECKS — `orreth_spine.harness.checks` (walk #8; P6.5):
//! laws the harness reads off the ground itself, no mind invoked — "a duty
//! answered, not refused" (W21) · "the monitor's offers arrive as holds" (W22)
//! · "every service healthy or retired" · "every MCP server answers
//! initialize" · "the keeper proposes after strikes, never retires alone"
//! (rule 11). A failed check is a wound named in words.
//!
//! The A/B RUN (`harness.run` — golden cases through a body's own graph, a
//! failing run a fact on the rail) needs a body's mind: since P7 sp6 the
//! kernel ASKS the body over the invoke rail (`orreth.resident.harness.v1`,
//! the cases riding the command, the run recorded under the kernel's run id
//! — `body::harness_payload`) and reads the run off the ground (`wait_run`);
//! the door answers with the run, or 202 while it runs. P6.5 sp3's four Stable
//! checks read here too: every mind answers · the gateway answers and holds
//! every mind · the meter and the gateway agree · a model change is announced.

use crate::ask::refused_words;
use crate::body::{harness_payload, verdict, HARNESS_CMD, KERNEL};
use crate::envelope::Mint;
use crate::gateway::Gateway;
use crate::ground::Ground;
use crate::mcp::strikes_n;
use crate::py::fold_ws;
use crate::schema::has_table;
use crate::sessions::services_listing;
use crate::watch::is_offer;
use crate::world::{head, RoadError};
use crate::world::{isoformat, json_text, refused, token_hex, World};
use serde_json::{json, Value};
use std::path::PathBuf;
use std::time::{Duration, SystemTime};

fn plural(n: usize, word: &str) -> String {
    format!("{n} {word}{}", if n != 1 { "s" } else { "" })
}

/// W21: for every runner with a human or role schedule, the LATEST replied
/// occurrence is an answer, never a refusal.
pub async fn duty_answered(g: &Ground, scope: &str) -> Result<Value, RoadError> {
    let rows = g
        .client()
        .query(
            "SELECT DISTINCT ON (s.runner) s.runner, s.schedule_id, a.ask_id, a.reply, a.replied_at \
             FROM spine_schedules s JOIN spine_occurrences o ON o.schedule_id = s.schedule_id JOIN \
             spine_asks a ON a.ask_id = o.ref WHERE s.scope = $1 AND s.kind IN ('human', 'role') AND \
             a.status = 'replied' ORDER BY s.runner, a.replied_at DESC",
            &[&scope],
        )
        .await?;
    let mut refused = Vec::new();
    for r in &rows {
        let reply: Option<String> = r.get(3);
        if refused_words(reply.as_deref()) {
            refused.push(json!({
                "runner": r.get::<_, String>(0), "schedule_id": r.get::<_, String>(1),
                "ask": r.get::<_, String>(2), "opens": head(&fold_ws(reply.as_deref().unwrap_or("")), 120),
            }));
        }
    }
    let names: Vec<&str> = refused
        .iter()
        .map(|r| r["runner"].as_str().unwrap_or_default())
        .collect();
    let detail = format!(
        "{} with a duty answered; {}",
        plural(rows.len(), "runner"),
        if refused.is_empty() {
            "none refused".to_string()
        } else {
            format!("{} refused: {}", refused.len(), names.join(", "))
        }
    );
    Ok(
        json!({"name": "a duty answered, not refused", "ok": refused.is_empty(), "detail": detail, "refused": refused}),
    )
}

/// W22: the monitor's latest N replies that speak of proposing a watch each
/// have a hold behind them — an add-watch act held (or settled) by the
/// monitor at or after the reply.
pub async fn offers_are_holds(g: &Ground, scope: &str, n: i64) -> Result<Value, RoadError> {
    let name = "the monitor's offers arrive as holds";
    let did: Option<String> = g
        .client()
        .query_opt(
            "SELECT did FROM spine_joins WHERE name = 'monitor' AND scope = $1 ORDER BY join_id \
             DESC LIMIT 1",
            &[&scope],
        )
        .await?
        .map(|r| r.get(0));
    let Some(did) = did else {
        return Ok(
            json!({"name": name, "ok": true, "detail": "no monitor on this ground", "unheld": []}),
        );
    };
    let rows = g
        .client()
        .query(
            "SELECT ask_id, reply, replied_at FROM spine_asks WHERE served_by = $1 AND status = \
             'replied' AND scope = $2 ORDER BY replied_at DESC LIMIT $3",
            &[&did, &scope, &n],
        )
        .await?;
    let offers: Vec<(String, String, SystemTime)> = rows
        .iter()
        .filter_map(|r| {
            let reply: Option<String> = r.get(1);
            let reply = reply.unwrap_or_default();
            is_offer(&reply).then(|| (r.get(0), reply, r.get(2)))
        })
        .collect();
    let mut unheld = Vec::new();
    for (aid, reply, at) in &offers {
        let held = g
            .client()
            .query_opt(
                "SELECT 1 FROM spine_asks WHERE served_by = $1 AND scope = $2 AND held IS NOT NULL \
                 AND held::json->>'tool' = 'add-watch' AND asked_at >= $3::timestamptz - interval '5 \
                 seconds' LIMIT 1",
                &[&did, &scope, at],
            )
            .await?;
        if held.is_none() {
            unheld.push(json!({"ask": aid, "opens": head(&fold_ws(reply), 120)}));
        }
    }
    let detail = format!(
        "{} in the last {n} replies; {}",
        plural(offers.len(), "offer"),
        if unheld.is_empty() {
            "every offer held".to_string()
        } else {
            format!("{} without a hold", unheld.len())
        }
    );
    Ok(json!({"name": name, "ok": unheld.is_empty(), "detail": detail, "unheld": unheld}))
}

fn names_of(rows: &[Value], pred: impl Fn(&Value) -> bool) -> Vec<&str> {
    rows.iter()
        .filter(|r| pred(r))
        .map(|r| r["name"].as_str().unwrap_or_default())
        .collect()
}

/// P6.5 sp1: every registered service is healthy or retired — read off the
/// shelf's LAST recorded health; the unhealthy named, the never-probed named.
pub async fn services_healthy(g: &Ground, scope: &str) -> Result<Value, RoadError> {
    let rows = services_listing(g, scope, None).await?;
    let standing: Vec<Value> = rows
        .iter()
        .filter(|r| r["state"] != json!("retired"))
        .cloned()
        .collect();
    let unhealthy = names_of(&standing, |r| r["state"] == json!("unhealthy"));
    let unprobed = names_of(&standing, |r| {
        r["state"] != json!("healthy") && r["state"] != json!("unhealthy")
    });
    let retired = names_of(&rows, |r| r["state"] == json!("retired"));
    let detail = if rows.is_empty() {
        "no services on the shelf".to_string()
    } else {
        let mut d = format!(
            "{} healthy · {} retired",
            standing.len() - unhealthy.len() - unprobed.len(),
            retired.len()
        );
        if !unhealthy.is_empty() {
            d.push_str(&format!(" · unhealthy: {}", unhealthy.join(", ")));
        }
        if !unprobed.is_empty() {
            d.push_str(&format!(" · not yet probed: {}", unprobed.join(", ")));
        }
        d
    };
    Ok(
        json!({"name": "every service healthy or retired", "ok": unhealthy.is_empty() && unprobed.is_empty(),
              "detail": detail, "unhealthy": unhealthy, "unprobed": unprobed}),
    )
}

/// P6.5 sp2: every standing MCP server answered initialize at its LAST probe.
pub async fn mcp_servers_answer(g: &Ground, scope: &str) -> Result<Value, RoadError> {
    let rows: Vec<Value> = services_listing(g, scope, Some("mcp"))
        .await?
        .into_iter()
        .filter(|r| r["state"] != json!("retired"))
        .collect();
    let silent = names_of(&rows, |r| r["last_health"]["ok"] == json!(false));
    let unprobed = names_of(&rows, |r| r["last_health"].is_null());
    let detail = if rows.is_empty() {
        "no MCP server on the shelf".to_string()
    } else {
        let mut d = format!(
            "{} of {} answered initialize",
            rows.len() - silent.len() - unprobed.len(),
            rows.len()
        );
        if !silent.is_empty() {
            d.push_str(&format!(" · silent: {}", silent.join(", ")));
        }
        if !unprobed.is_empty() {
            d.push_str(&format!(" · never probed: {}", unprobed.join(", ")));
        }
        d
    };
    Ok(
        json!({"name": "every MCP server answers initialize", "ok": silent.is_empty() && unprobed.is_empty(),
              "detail": detail, "silent": silent, "unprobed": unprobed}),
    )
}

/// The keeper's newest proposal to retire this service (any status) — its asked_at.
async fn last_proposal_at(
    g: &Ground,
    scope: &str,
    name: &str,
) -> Result<Option<SystemTime>, RoadError> {
    Ok(g
        .client()
        .query_opt(
            "SELECT asked_at FROM spine_asks WHERE scope = $1 AND served_by = 'the kernel' AND held \
             IS NOT NULL AND held::json->>'tool' = 'service.retire' AND held::json->'args'->>'name' \
             = $2 ORDER BY asked_at DESC LIMIT 1",
            &[&scope, &name],
        )
        .await?
        .map(|r| r.get(0)))
}

/// Unhealthy checks IN A ROW, newest first, counted since the keeper's last
/// proposal about this service (a proposal resets the count).
pub async fn strikes(g: &Ground, scope: &str, name: &str) -> Result<i64, RoadError> {
    if !has_table(g, "spine_service_health").await? {
        return Ok(0);
    }
    let since = last_proposal_at(g, scope, name).await?;
    let rows = g
        .client()
        .query(
            "SELECT ok FROM spine_service_health WHERE name = $1 AND scope = $2 AND ($3::timestamptz \
             IS NULL OR at > $3::timestamptz) ORDER BY health_id DESC LIMIT 50",
            &[&name, &scope, &since],
        )
        .await?;
    let mut n = 0;
    for r in rows {
        if r.get::<_, Option<bool>>(0) == Some(false) {
            n += 1;
        } else {
            break;
        }
    }
    Ok(n)
}

/// P6.5 sp2, the strikes rule (rule 11): a service unhealthy across N checks
/// in a row has a PROPOSAL at the interlock (or the human has heard one
/// since) — and no service was ever retired by a body's own hand.
pub async fn keeper_proposes(g: &Ground, scope: &str) -> Result<Value, RoadError> {
    let n = strikes_n();
    let mut unproposed = Vec::new();
    for s in services_listing(g, scope, None).await? {
        if s["state"] == json!("retired") {
            continue;
        }
        let name = s["name"].as_str().unwrap_or_default().to_string();
        if strikes(g, scope, &name).await? >= n {
            unproposed.push(name);
        }
    }
    let alone: i64 = g
        .client()
        .query_one(
            "SELECT count(*) FROM spine_markers WHERE scope = $1 AND kind = 'observation' AND note \
             LIKE '% retire: retired%' AND by_did LIKE 'did:orreth:agent:%'",
            &[&scope],
        )
        .await?
        .get(0);
    let mut detail = format!("strikes rule: {n} in a row");
    detail.push_str(&if unproposed.is_empty() {
        " · every strike proposed".to_string()
    } else {
        format!(" · unproposed: {}", unproposed.join(", "))
    });
    if alone > 0 {
        detail.push_str(&format!(" · {alone} retired by a body alone"));
    }
    Ok(
        json!({"name": "the keeper proposes after strikes, never retires alone",
              "ok": unproposed.is_empty() && alone == 0, "detail": detail, "unproposed": unproposed, "alone": alone}),
    )
}

// ---- P6.5 sp3's four, ported P7 sp6: the Stable's health -------------------------------

/// Every standing mind answered its canary at its LAST check (the keeper's beat).
pub async fn minds_answer(g: &Ground, scope: &str) -> Result<Value, RoadError> {
    let rows: Vec<Value> = services_listing(g, scope, Some("mind"))
        .await?
        .into_iter()
        .filter(|r| r["state"] != json!("retired"))
        .collect();
    let silent = names_of(&rows, |r| r["last_health"]["ok"] == json!(false));
    let unprobed = names_of(&rows, |r| r["last_health"].is_null());
    let detail = if rows.is_empty() {
        "no mind in the Stable".to_string()
    } else {
        let mut d = format!(
            "{} of {} answered",
            rows.len() - silent.len() - unprobed.len(),
            rows.len()
        );
        if !silent.is_empty() {
            d.push_str(&format!(" · silent: {}", silent.join(", ")));
        }
        if !unprobed.is_empty() {
            d.push_str(&format!(" · never checked: {}", unprobed.join(", ")));
        }
        d
    };
    Ok(
        json!({"name": "every mind answers", "ok": silent.is_empty() && unprobed.is_empty(), "detail": detail,
              "silent": silent, "unprobed": unprobed}),
    )
}

/// The gateway answers, and holds a model entry for every standing mind (a
/// stall with a DEAL; the test lane's fake mind is never in the gateway).
pub async fn gateway_holds(g: &Ground, scope: &str, gw: &Gateway) -> Result<Value, RoadError> {
    let name = "the gateway answers and holds every mind";
    let rows: Vec<Value> = services_listing(g, scope, Some("mind"))
        .await?
        .into_iter()
        .filter(|r| r["state"] != json!("retired") && crate::py::truthy(&r["manifest"]["provider"]))
        .collect();
    if !gw.ready().await {
        let missing: Vec<&str> = rows
            .iter()
            .map(|r| r["name"].as_str().unwrap_or_default())
            .collect();
        return Ok(json!({"name": name, "ok": rows.is_empty(),
                         "detail": format!("the gateway at {} is dark{}", gw.base,
                                           if rows.is_empty() { String::new() } else { format!(" — {} minds cannot think", rows.len()) }),
                         "missing": missing}));
    }
    let held = match gw.models().await {
        Ok(m) => m,
        Err(e) => {
            return Ok(json!({"name": name, "ok": false, "detail": e.to_string(), "missing": []}))
        }
    };
    let missing = names_of(&rows, |r| {
        !held.contains_key(r["name"].as_str().unwrap_or_default())
    });
    let mut detail = format!(
        "the gateway answers · {} of {} minds held",
        rows.len() - missing.len(),
        rows.len()
    );
    if !missing.is_empty() {
        detail.push_str(&format!(" · missing: {}", missing.join(", ")));
    }
    Ok(json!({"name": name, "ok": missing.is_empty(), "detail": detail, "missing": missing}))
}

/// The 100%: the meter's dollars against the gateway's ledger — within a tenth of a cent.
pub async fn meter_agrees(g: &Ground, scope: &str, gw: &Gateway) -> Result<Value, RoadError> {
    let r = crate::stable_live::reconcile(g, scope, Some(gw), 20, 30.0).await?;
    let mismatched = r["mismatched"].as_array().cloned().unwrap_or_default();
    Ok(
        json!({"name": "the meter and the gateway agree", "ok": mismatched.is_empty(), "detail": r["words"],
              "meter_usd": r["meter_usd"], "gateway_usd": r["gateway_usd"], "mismatched": mismatched}),
    )
}

/// "Model changed without an announcement": every meter line that rode a
/// mind other than the one asked for carries the why — a silent swap is a wound.
pub async fn changes_announced(g: &Ground) -> Result<Value, RoadError> {
    let name = "a model change is announced";
    if !has_table(g, "spine_meter").await? {
        return Ok(
            json!({"name": name, "ok": true, "detail": "no thought metered yet", "silent": 0}),
        );
    }
    let silent: i64 = g
        .client()
        .query_one(
            "SELECT count(*) FROM spine_meter WHERE ok AND stall IS NOT NULL AND note IS NULL AND model <> stall \
             AND at >= now() - interval '1 day'",
            &[],
        )
        .await?
        .get(0);
    let confessed: i64 = g
        .client()
        .query_one(
            "SELECT count(*) FROM spine_meter WHERE ok AND note IS NOT NULL AND at >= now() - interval '1 day'",
            &[],
        )
        .await?
        .get(0);
    Ok(json!({"name": name, "ok": silent == 0,
              "detail": format!("{confessed} confessed swap{} today{}", if confessed != 1 { "s" } else { "" },
                                if silent > 0 { format!(" · {silent} SILENT") } else { " · none silent".to_string() }),
              "silent": silent}))
}

/// Every world check, read off the ground — the harness door lists them (nine, as the reference's).
pub async fn checks(g: &Ground, scope: &str, gw: &Gateway) -> Result<Vec<Value>, RoadError> {
    Ok(vec![
        duty_answered(g, scope).await?,
        offers_are_holds(g, scope, 5).await?,
        services_healthy(g, scope).await?,
        mcp_servers_answer(g, scope).await?,
        keeper_proposes(g, scope).await?,
        minds_answer(g, scope).await?,
        gateway_holds(g, scope, gw).await?,
        meter_agrees(g, scope, gw).await?,
        changes_announced(g).await?,
    ])
}

// ---- the run, over the rail (P7 sp6) ----------------------------------------------------------

/// The spine home: `ORRETH_SPINE`, else the crate's `../../../../spine`.
pub fn spine_dir() -> PathBuf {
    std::env::var("ORRETH_SPINE")
        .ok()
        .filter(|p| !p.is_empty())
        .map(PathBuf::from)
        .unwrap_or_else(|| PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("../../../../spine"))
}

/// `harness.golden`: a template's golden cases (`spine/golden/<template>.v0.json`), or none.
pub fn golden(template: &str) -> Vec<Value> {
    let p = spine_dir()
        .join("golden")
        .join(format!("{template}.v0.json"));
    std::fs::read_to_string(p)
        .ok()
        .and_then(|t| serde_json::from_str::<Value>(&t).ok())
        .and_then(|v| v.as_array().cloned())
        .unwrap_or_default()
}

/// The kernel asks a body to run cases through its own graph — the command
/// on the body's own bench; the run lands under `run_id`. A body not joined
/// here is refused in words (the reference's 404).
pub async fn run_over_rail(
    g: &Ground,
    w: &World,
    template: &str,
    cases: &[Value],
    arm: Option<&str>,
    parent_marker: Option<&str>,
) -> Result<String, RoadError> {
    if crate::services_live::did_of_body(g.client(), &w.scope, template)
        .await?
        .is_none()
    {
        return Err(refused("no such body"));
    }
    if let Some(a) = arm {
        let s = crate::services_live::get(g.client(), &w.scope, a).await?;
        if !s.is_some_and(|s| s["kind"] == json!("mind")) {
            return Err(refused(format!(
                "no mind named {} stands in the Stable — an arm is a mind by name",
                crate::py::repr_str(a)
            )));
        }
    }
    let run_id = format!("run_{}", token_hex(5));
    let e = Mint {
        kind: "command".into(),
        r#type: HARNESS_CMD.into(),
        universe_id: w.scope.clone(),
        scope_path: w.scope.clone(),
        payload: harness_payload(&run_id, template, cases, arm, parent_marker),
        correlation_id: Some(run_id.clone()),
        authority_chain: Some(vec![KERNEL.to_string()]),
        ..Default::default()
    }
    .mint()?;
    crate::invoke::publish_command(&w.rabbit_url, &e, &w.ns).await?;
    Ok(run_id)
}

/// The run's row as the reference's `harness.run` returns it, once it lands.
pub async fn run_row(g: &Ground, run_id: &str) -> Result<Option<Value>, RoadError> {
    Ok(g
        .client()
        .query_opt(
            "SELECT run_id, template, version, passed, failed, details, ran_at, arm FROM spine_harness_runs WHERE \
             run_id = $1",
            &[&run_id],
        )
        .await?
        .map(|r| {
            json!({"run_id": r.get::<_, String>(0), "template": r.get::<_, String>(1), "version": r.get::<_, String>(2),
                   "passed": r.get::<_, i32>(3), "failed": r.get::<_, i32>(4),
                   "details": json_text(r.get::<_, Option<String>>(5).as_deref()).unwrap_or(json!([])),
                   "ran_at": isoformat(r.get::<_, SystemTime>(6)), "arm": r.get::<_, Option<String>>(7)})
        }))
}

/// Wait for a run to land, within a bound.
pub async fn wait_run(
    g: &Ground,
    run_id: &str,
    within: Duration,
) -> Result<Option<Value>, RoadError> {
    let end = tokio::time::Instant::now() + within;
    loop {
        if let Some(r) = run_row(g, run_id).await? {
            return Ok(Some(r));
        }
        if tokio::time::Instant::now() >= end {
            return Ok(None);
        }
        tokio::time::sleep(Duration::from_millis(300)).await;
    }
}

/// `harness.ab`: the same golden cases against each named mind, one run each,
/// over the rail; the verdict names the arm that passed most — a PROPOSAL for
/// the human's cut, never an assignment made by the machine.
pub async fn ab(
    g: &Ground,
    w: &World,
    template: &str,
    arms: &[String],
    within: Duration,
) -> Result<Value, RoadError> {
    let cases = golden(template);
    let mut runs = serde_json::Map::new();
    for a in arms {
        let rid = run_over_rail(g, w, template, &cases, Some(a), None).await?;
        let row = wait_run(g, &rid, within).await?.ok_or_else(|| {
            refused(format!("the {a} arm's run did not land within {} s — the body may be busy; the run id is {rid}", within.as_secs()))
        })?;
        runs.insert(
            a.clone(),
            json!({"run_id": rid, "passed": row["passed"], "failed": row["failed"]}),
        );
    }
    let mut ranked: Vec<(&String, &Value)> = runs.iter().collect();
    ranked.sort_by(|(an, av), (bn, bv)| {
        bv["passed"]
            .as_i64()
            .cmp(&av["passed"].as_i64())
            .then(an.cmp(bn))
    });
    let best = ranked.first().map(|(n, _)| (*n).clone());
    let words: Vec<String> = arms
        .iter()
        .filter_map(|a| {
            runs.get(a)
                .map(|r| format!("{a}: {} passed, {} failed", r["passed"], r["failed"]))
        })
        .collect();
    let mut sentence = format!(
        "{template} over {} arms — {}",
        arms.len(),
        words.join(" · ")
    );
    if let Some(b) = &best {
        sentence.push_str(&format!(
            "; {b} did best — say \"assign {template} to {b}\" to make it so"
        ));
    }
    let _ = verdict; // the shared law lives in `body::verdict`; the body applies it
    Ok(json!({"template": template, "arms": runs, "best": best, "words": sentence}))
}
