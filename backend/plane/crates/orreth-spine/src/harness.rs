// PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp4, the loops · 2026-09-23
//! The harness's WORLD CHECKS — `orreth_spine.harness.checks` (walk #8; P6.5):
//! laws the harness reads off the ground itself, no mind invoked — "a duty
//! answered, not refused" (W21) · "the monitor's offers arrive as holds" (W22)
//! · "every service healthy or retired" · "every MCP server answers
//! initialize" · "the keeper proposes after strikes, never retires alone"
//! (rule 11). A failed check is a wound named in words.
//!
//! The A/B RUN itself (`harness.run` — golden cases through a body's own
//! graph, a failing run a fact on the rail) needs a body's mind; the bodies
//! are Python's until the seam (P7 sp6) — `/harness/run` here answers 501 by
//! name, and the kernel's scheduled run is left due for the Python kernel.

use crate::ask::refused_words;
use crate::ground::Ground;
use crate::mcp::strikes_n;
use crate::py::fold_ws;
use crate::schema::has_table;
use crate::sessions::services_listing;
use crate::watch::is_offer;
use crate::world::{head, RoadError};
use serde_json::{json, Value};
use std::time::SystemTime;

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

/// Every world check, read off the ground — the harness door lists them.
pub async fn checks(g: &Ground, scope: &str) -> Result<Vec<Value>, RoadError> {
    Ok(vec![
        duty_answered(g, scope).await?,
        offers_are_holds(g, scope, 5).await?,
        services_healthy(g, scope).await?,
        mcp_servers_answer(g, scope).await?,
        keeper_proposes(g, scope).await?,
    ])
}
