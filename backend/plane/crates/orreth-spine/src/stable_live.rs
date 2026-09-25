// PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp6, the bodies' seam · 2026-09-24
//! THE STABLE on the ground — the live half of `orreth_spine.stable` (P6.5 sp3
//! · 0009 §2 · 0019 · 0058; JB's lock 2026-09-24: LiteLLM executes, the
//! registry knows and decides): stalls (services of kind mind, each a model
//! entry in the gateway), assignments (subject → {class: stall}, a fact each),
//! THE ROUTING DECISION for a body (`resolve_for`, the pure law on the ground's
//! rows), the FUEL CLAUSE (a body's own virtual key at the gateway with its
//! allowance and window — minted once, the same key every life; the gauge;
//! the refill, a fact), the METER in dollars (every thought's line — the
//! kernel writes only the canary's here), the held acts (register · assign ·
//! unassign · refill · re-pin · retire: the kernel holds, the human cuts,
//! `settle_in` runs the act inside the record's own transaction), the market's
//! eyes (drift → a re-pin proposal; EOL → a retire proposal with the swap
//! named; a drained body → a refill proposal; the strikes rule — one hold at
//! a time, never an act by the machine alone), search, spend, and the 100%
//! (`reconcile`: the meter against the gateway's ledger, thought by thought).

use crate::envelope::{self, Mint};
use crate::gateway::{Gateway, GatewayDark};
use crate::ground::Ground;
use crate::markers_live;
use crate::proof_live;
use crate::py::{g_fmt, python_str, truthy};
use crate::services_live::{self, FactWhere, KERNEL};
use crate::stable::{
    self, act_words, deal, drift, eol_due, recommend, resolve, DealAsk, ResolveAsk, ANY, ASSIGNED,
    ASSIGN_TOOL, CLASSES, FUELED, HELD_TOOLS, REFILL_TOOL, REGISTER_TOOL, REPIN_TOOL, RETIRE_TOOL,
    STANDING, UNASSIGNED, UNASSIGN_TOOL,
};
use crate::world::{isoformat, refused, RoadError, World};
use regex::Regex;
use serde_json::{json, Value};
use std::sync::{LazyLock, Mutex};
use std::time::{Duration, Instant, SystemTime};
use tokio_postgres::{GenericClient, Transaction};

pub const LEASE_USD_DIAL: &str = "SPINE_LEASE_USD";
pub const LEASE_USD_DEFAULT: f64 = 1.0;
pub const LEASE_DAYS_DIAL: &str = "SPINE_LEASE_RENEW_DAYS";
pub const LEASE_DAYS_DEFAULT: i64 = 1;
pub const EOL_DIAL: &str = "SPINE_EOL_HORIZON_DAYS";
pub const EOL_DEFAULT: i64 = 30;
pub const MIND_CHECK_DIAL: &str = "SPINE_MIND_CHECK_S";
pub const MIND_CHECK_DEFAULT: f64 = 600.0;
pub const OPENROUTER_CATALOG: &str = "https://openrouter.ai/api/v1/models";
const CATALOG_TTL: Duration = Duration::from_secs(300);

static MIND_NAME: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r"^[a-z][a-z0-9_.-]{0,63}$").unwrap());

fn dial_f(name: &str, default: f64) -> f64 {
    std::env::var(name)
        .ok()
        .and_then(|v| v.trim().parse().ok())
        .unwrap_or(default)
}

fn dial_i(name: &str, default: i64) -> i64 {
    std::env::var(name)
        .ok()
        .and_then(|v| v.trim().parse().ok())
        .unwrap_or(default)
}

fn standing(s: &Value) -> bool {
    s["state"].as_str().is_some_and(|st| STANDING.contains(&st))
}

// ---- the shelf's minds, with their spend ------------------------------------------------------------

/// `stable.stalls`: every mind in the Stable — the shelf's rows of kind mind
/// with its spend today and all time off the meter.
pub async fn stalls(g: &Ground, scope: &str) -> Result<Vec<Value>, RoadError> {
    let mut rows = crate::sessions::services_listing(g, scope, Some("mind")).await?;
    let mut spend = std::collections::HashMap::new();
    if crate::schema::has_table(g, "spine_meter").await? {
        for r in g
            .client()
            .query(
                "SELECT stall, count(*), coalesce(sum(usd), 0), coalesce(sum(usd) FILTER (WHERE at >= \
                 date_trunc('day', now())), 0), count(*) FILTER (WHERE ok = false) FROM spine_meter WHERE \
                 stall IS NOT NULL GROUP BY stall",
                &[],
            )
            .await?
        {
            spend.insert(
                r.get::<_, String>(0),
                json!({"calls": r.get::<_, i64>(1), "usd": r.get::<_, f64>(2), "usd_today": r.get::<_, f64>(3), "failed": r.get::<_, i64>(4)}),
            );
        }
    }
    for s in rows.iter_mut() {
        let name = python_str(&s["name"]);
        s["spend"] = spend
            .get(&name)
            .cloned()
            .unwrap_or(json!({"calls": 0, "usd": 0.0, "usd_today": 0.0, "failed": 0}));
    }
    Ok(rows)
}

/// `stable.assignments`.
pub async fn assignments<C: GenericClient>(c: &C, scope: &str) -> Result<Vec<Value>, RoadError> {
    let rows = c
        .query(
            "SELECT subject, klass, stall, by_did, at FROM spine_mind_assignments WHERE scope = $1 ORDER BY \
             subject, klass",
            &[&scope],
        )
        .await?;
    Ok(rows
        .iter()
        .map(|r| {
            json!({"subject": r.get::<_, String>(0), "klass": r.get::<_, String>(1), "stall": r.get::<_, String>(2),
                   "by": r.get::<_, String>(3), "at": isoformat(r.get::<_, SystemTime>(4))})
        })
        .collect())
}

/// `stable.resolve_for`: the routing decision on this ground's rows.
pub async fn resolve_for<C: GenericClient>(
    c: &C,
    scope: &str,
    subject: Option<&str>,
    model: Option<&str>,
    klass: Option<&str>,
    pin: Option<&str>,
) -> Result<Value, RoadError> {
    let stalls = services_live::rows(c, scope, Some("mind")).await?;
    let assigned = assignments(c, scope).await?;
    Ok(resolve(
        &stalls,
        &assigned,
        ResolveAsk {
            subject,
            klass,
            pin,
            model,
        },
    ))
}

// ---- the facts ------------------------------------------------------------------------------------

/// `stable._mind_fact` inside `tx`: the fact and its marker (an ACTION under
/// the ask that released it, else an OBSERVATION under the shelf root).
#[allow(clippy::too_many_arguments)]
async fn mind_fact_in(
    tx: &Transaction<'_>,
    w: &World,
    typ: &str,
    r#ref: &str,
    mut payload: Value,
    by: &str,
    note: &str,
    at: FactWhere<'_>,
) -> Result<String, RoadError> {
    let mid = markers_live::new_id();
    let kind = if at.ask.is_some() {
        "action"
    } else {
        "observation"
    };
    let parent = match at.parent_marker {
        Some(p) => p.to_string(),
        None => services_live::shelf_root(tx, &w.scope).await?,
    };
    let mut chain: Vec<String> = if by == KERNEL {
        vec![KERNEL.into()]
    } else {
        vec![by.into(), KERNEL.into()]
    };
    if let Some(c) = at.confirmed_by.filter(|c| *c != by) {
        chain = vec![by.into(), c.into(), KERNEL.into()];
    }
    payload["ref"] = json!(r#ref);
    payload["by"] = json!(by);
    let corr = at.ask.unwrap_or(r#ref).to_string();
    markers_live::insert(
        tx,
        &mid,
        kind,
        Some(&parent),
        &corr,
        by,
        Some(note),
        &w.scope,
    )
    .await?;
    let e = Mint {
        kind: "event".into(),
        r#type: typ.into(),
        universe_id: w.scope.clone(),
        scope_path: w.scope.clone(),
        payload,
        correlation_id: Some(corr),
        authority_chain: Some(chain),
        aggregate: None,
        marker: Some(json!({"kind": kind, "id": mid, "parent": parent, "by": by})),
    }
    .mint()?;
    crate::outbox::add_row(
        tx,
        &envelope::encode(&e)?,
        e["message_id"].as_str().unwrap_or_default(),
    )
    .await?;
    Ok(mid)
}

// ---- the stalls: register · re-pin · retire · restore -------------------------------------------------

/// `stable.register_mind` inside `tx`: the gateway entry FIRST (words on
/// refusal; the ladder untouched), then the service on the ladder with the
/// deal as its manifest and the key by NAME as its secret.
pub async fn register_mind_in(
    tx: &Transaction<'_>,
    w: &World,
    gw: Option<&Gateway>,
    name: &str,
    d: &Value,
    by: &str,
) -> Result<Value, RoadError> {
    let name = name.trim().to_lowercase();
    if !MIND_NAME.is_match(&name) {
        return Err(refused(
            "an LLM needs a short lowercase name (letters, digits, . _ -)",
        ));
    }
    if let Some(gw) = gw {
        gw.add_stall(&name, d).await?;
    }
    let secrets: Vec<String> = d["key"]
        .as_str()
        .filter(|k| !k.is_empty())
        .map(|k| vec![k.to_string()])
        .unwrap_or_default();
    services_live::register_in(tx, w, &name, "mind", d, by, None, &secrets).await
}

/// `stable.repin_mind` inside `tx`: a changed deal re-pins the stall and rewrites its entry.
pub async fn repin_mind_in(
    tx: &Transaction<'_>,
    w: &World,
    gw: Option<&Gateway>,
    name: &str,
    d: &Value,
    by: &str,
) -> Result<Value, RoadError> {
    if let Some(gw) = gw {
        gw.drop_stall(name).await?;
        gw.add_stall(name, d).await?;
    }
    services_live::version_in(tx, w, name, d, by).await
}

/// `stable.retire_mind` inside `tx`: retired on the ladder (dormancy) and
/// dropped from the gateway when it is a mind — the ladder is the truth; a
/// dark gateway is re-synced by the beat.
pub async fn retire_mind_in(
    tx: &Transaction<'_>,
    w: &World,
    gw: Option<&Gateway>,
    name: &str,
    by: &str,
    at: FactWhere<'_>,
) -> Result<Value, RoadError> {
    let made = services_live::retire_in(tx, w, name, by, at).await?;
    if made["kind"] == json!("mind") {
        if let Some(gw) = gw {
            let _ = gw.drop_stall(name).await;
        }
    }
    Ok(made)
}

/// `stable.restore_mind`: a new fact; the entry written back into the gateway.
pub async fn restore_mind(
    g: &mut Ground,
    w: &World,
    gw: Option<&Gateway>,
    name: &str,
    by: &str,
) -> Result<Value, RoadError> {
    let made = services_live::restore(g, w, name, by).await?;
    if made["kind"] == json!("mind") {
        if let Some(gw) = gw {
            gw.add_stall(name, &made["manifest"]).await?;
        }
    }
    Ok(made)
}

// ---- assignments ----------------------------------------------------------------------------------

/// `stable.assign` inside `tx`: subject → {class: stall}, a fact; the stall must stand.
pub async fn assign_in(
    tx: &Transaction<'_>,
    w: &World,
    subject: &str,
    klass: &str,
    stall: &str,
    by: &str,
    at: FactWhere<'_>,
) -> Result<Value, RoadError> {
    if !CLASSES.contains(&klass) && klass != ANY {
        return Err(refused(format!(
            "no class of work named {} — fast, standard, deep, or any",
            crate::py::repr_str(klass)
        )));
    }
    let s = services_live::get(tx, &w.scope, stall).await?;
    let Some(s) = s.filter(|s| s["kind"] == json!("mind")) else {
        return Err(refused(format!(
            "no LLM named {} stands in the Stable",
            crate::py::repr_str(stall)
        )));
    };
    if !standing(&s) {
        return Err(refused(format!(
            "the {stall} LLM is {} — assign an LLM that stands",
            python_str(&s["state"])
        )));
    }
    let work = if klass == ANY {
        "all".to_string()
    } else {
        klass.to_string()
    };
    mind_fact_in(
        tx,
        w,
        ASSIGNED,
        &python_str(&s["did"]),
        json!({"subject": subject, "klass": klass, "stall": stall, "hash": s["manifest_hash"]}),
        by,
        &format!("{subject} uses the {stall} LLM for {work} work"),
        at,
    )
    .await?;
    tx.execute(
        "INSERT INTO spine_mind_assignments (subject, scope, klass, stall, by_did, at) VALUES ($1, $2, $3, $4, \
         $5, clock_timestamp()) ON CONFLICT (subject, scope, klass) DO UPDATE SET stall = EXCLUDED.stall, by_did \
         = EXCLUDED.by_did, at = clock_timestamp()",
        &[&subject, &w.scope, &klass, &stall, &by],
    )
    .await?;
    Ok(json!({"subject": subject, "klass": klass, "stall": stall}))
}

/// `stable.unassign` inside `tx`.
pub async fn unassign_in(
    tx: &Transaction<'_>,
    w: &World,
    subject: &str,
    klass: &str,
    by: &str,
    at: FactWhere<'_>,
) -> Result<Value, RoadError> {
    let row = tx
        .query_opt(
            "SELECT stall FROM spine_mind_assignments WHERE subject = $1 AND scope = $2 AND klass = $3",
            &[&subject, &w.scope, &klass],
        )
        .await?;
    let Some(row) = row else {
        return Err(refused(format!(
            "{subject} has no {klass} assignment to lift"
        )));
    };
    let stall: String = row.get(0);
    let s = services_live::get(tx, &w.scope, &stall).await?;
    let r#ref = s
        .map(|s| python_str(&s["did"]))
        .unwrap_or_else(|| stall.clone());
    mind_fact_in(
        tx,
        w,
        UNASSIGNED,
        &r#ref,
        json!({"subject": subject, "klass": klass, "stall": stall}),
        by,
        &format!("{subject} no longer pinned to {stall} ({klass})"),
        at,
    )
    .await?;
    tx.execute(
        "DELETE FROM spine_mind_assignments WHERE subject = $1 AND scope = $2 AND klass = $3",
        &[&subject, &w.scope, &klass],
    )
    .await?;
    Ok(json!({"subject": subject, "klass": klass, "stall": stall}))
}

// ---- the fuel clause: a body's lease is its virtual key ------------------------------------------------

pub fn lease_defaults() -> (f64, i64) {
    (
        dial_f(LEASE_USD_DIAL, LEASE_USD_DEFAULT),
        dial_i(LEASE_DAYS_DIAL, LEASE_DAYS_DEFAULT),
    )
}

/// `stable.key_for`: the body's own key at the gateway, minted once with the
/// default lease — a fuel fact — and the SAME key every life after.
pub async fn key_for(
    g: &mut Ground,
    scope: &str,
    gw: &Gateway,
    did: &str,
    name: &str,
) -> Result<String, RoadError> {
    if let Some(r) = g
        .client()
        .query_opt(
            "SELECT key FROM spine_mind_keys WHERE did = $1 AND scope = $2",
            &[&did, &scope],
        )
        .await?
    {
        return Ok(r.get(0));
    }
    let (max_usd, days) = lease_defaults();
    let alias = format!("{scope}:{name}");
    let made = gw.key_new(did, &alias, max_usd, days).await?;
    let key = made["key"].as_str().unwrap_or_default().to_string();
    let w = World {
        scope: scope.to_string(),
        ..World::from_env()
    };
    let tx = g.client_mut().transaction().await?;
    mind_fact_in(
        &tx,
        &w,
        FUELED,
        did,
        json!({"max_usd": max_usd, "renew_days": days, "alias": alias, "first": true}),
        KERNEL,
        &format!(
            "{name} fueled: ${} every {days} day{}",
            g_fmt(max_usd),
            if days != 1 { "s" } else { "" }
        ),
        FactWhere::default(),
    )
    .await?;
    let days32 = days as i32;
    tx.execute(
        "INSERT INTO spine_mind_keys (did, scope, alias, key, max_usd, renew_days) VALUES ($1, $2, $3, $4, $5, $6) \
         ON CONFLICT (did, scope) DO NOTHING",
        &[&did, &scope, &alias, &key, &max_usd, &days32],
    )
    .await?;
    tx.commit().await?;
    Ok(key)
}

pub async fn mark_drained(g: &Ground, scope: &str, did: &str) -> Result<(), RoadError> {
    g.client()
        .execute(
            "UPDATE spine_mind_keys SET drained_at = clock_timestamp() WHERE did = $1 AND scope = $2",
            &[&did, &scope],
        )
        .await?;
    Ok(())
}

/// `stable.fuel`: a body's gauge — the allowance, the spend in this window, when it renews.
pub async fn fuel(
    g: &Ground,
    scope: &str,
    gw: Option<&Gateway>,
    did: &str,
) -> Result<Option<Value>, RoadError> {
    let row = g
        .client()
        .query_opt(
            "SELECT key, max_usd, renew_days, drained_at, refills FROM spine_mind_keys WHERE did = $1 AND scope = $2",
            &[&did, &scope],
        )
        .await?;
    let Some(r) = row else {
        return Ok(None);
    };
    let key: String = r.get(0);
    let mut out = json!({"max_usd": r.get::<_, f64>(1), "renew_days": r.get::<_, i32>(2),
                         "drained_at": crate::world::iso_opt(r.get::<_, Option<SystemTime>>(3)),
                         "refills": r.get::<_, i32>(4), "spend": null, "renews_at": null});
    if let Some(gw) = gw {
        match gw.key_info(&key).await {
            Ok(info) => {
                out["spend"] = json!(info["spend"].as_f64().unwrap_or(0.0));
                if let Some(m) = info["max_budget"].as_f64() {
                    out["max_usd"] = json!(m);
                }
                out["renews_at"] = info["budget_reset_at"].clone();
            }
            Err(GatewayDark(w)) => out["gauge"] = json!(w),
        }
    }
    Ok(Some(out))
}

/// `stable.refill` inside `tx`: the allowance grows at the gateway — a fuel fact; the drained mark lifted.
#[allow(clippy::too_many_arguments)]
pub async fn refill_in(
    tx: &Transaction<'_>,
    w: &World,
    gw: &Gateway,
    did: &str,
    add_usd: f64,
    by: &str,
    name: Option<&str>,
    at: FactWhere<'_>,
) -> Result<Value, RoadError> {
    let row = tx
        .query_opt(
            "SELECT key, alias, max_usd FROM spine_mind_keys WHERE did = $1 AND scope = $2",
            &[&did, &w.scope],
        )
        .await?;
    let Some(row) = row else {
        return Err(refused(format!(
            "{} has no lease yet — it is fueled on its first thought",
            name.unwrap_or(did)
        )));
    };
    if add_usd <= 0.0 {
        return Err(refused("a refill adds a positive amount of dollars"));
    }
    let key: String = row.get(0);
    let alias: String = row.get(1);
    let info = gw.key_info(&key).await?;
    let new_max = ((info["max_budget"]
        .as_f64()
        .unwrap_or_else(|| row.get::<_, f64>(2))
        + add_usd)
        * 1e6)
        .round()
        / 1e6;
    gw.key_update(&key, json!({"max_budget": new_max})).await?;
    let whom = name.unwrap_or(did);
    mind_fact_in(
        tx,
        w,
        FUELED,
        did,
        json!({"max_usd": new_max, "added_usd": add_usd, "alias": alias, "first": false}),
        by,
        &format!(
            "{whom} refilled by ${} — allowance now ${}",
            g_fmt(add_usd),
            g_fmt(new_max)
        ),
        at,
    )
    .await?;
    tx.execute(
        "UPDATE spine_mind_keys SET max_usd = $1, drained_at = NULL, refills = refills + 1 WHERE did = $2 AND \
         scope = $3",
        &[&new_max, &did, &w.scope],
    )
    .await?;
    Ok(json!({"did": did, "max_usd": new_max, "added_usd": add_usd}))
}

// ---- the meter --------------------------------------------------------------------------------------

/// `gateway.meter`: ONE meter line — who thought, which model, the tokens,
/// the dollars, the stall, the gateway's request id; the service DID read
/// from the ladder (rule 5: the meter reads the ladder).
#[allow(clippy::too_many_arguments)]
pub async fn meter(
    g: &Ground,
    scope: &str,
    did: &str,
    model: &str,
    tokens_in: i64,
    tokens_out: i64,
    usd: f64,
    stall: Option<&str>,
    request_id: Option<&str>,
    ok: bool,
    note: Option<&str>,
) -> Result<(), RoadError> {
    let service = match stall {
        Some(s) => services_live::stall_did(g.client(), scope, s).await?,
        None => services_live::mind_did(g.client(), scope, model).await?,
    };
    let (tin, tout) = (tokens_in as i32, tokens_out as i32);
    g.client()
        .execute(
            "INSERT INTO spine_meter (did, model, tokens_in, tokens_out, at, service, usd, stall, request_id, ok, \
             note) VALUES ($1, $2, $3, $4, clock_timestamp(), $5, $6, $7, $8, $9, $10)",
            &[&did, &model, &tin, &tout, &service, &usd, &stall, &request_id, &ok, &note],
        )
        .await?;
    Ok(())
}

/// The honest failed line (`LiteLLMGateway._fail`).
pub async fn meter_failed(
    g: &Ground,
    scope: &str,
    did: &str,
    stall: Option<&str>,
    note: &str,
) -> Result<(), RoadError> {
    let note: String = note.chars().take(300).collect();
    meter(
        g,
        scope,
        did,
        stall.unwrap_or("-"),
        0,
        0,
        0.0,
        stall,
        None,
        false,
        Some(&note),
    )
    .await
}

// ---- the held acts: the keeper proposes, the human cuts -------------------------------------------------

/// `stable.hold`: one of the kernel's own held acts at the interlock (L2).
pub async fn hold(
    g: &mut Ground,
    w: &World,
    tool: &str,
    args: Value,
    text: &str,
    person: &str,
    session: Option<&str>,
) -> Result<String, RoadError> {
    if !HELD_TOOLS.contains(&tool) {
        return Err(refused(format!(
            "no held act named {}",
            crate::py::repr_str(tool)
        )));
    }
    proof_live::hold_kernel_act(
        g,
        w,
        text,
        person,
        tool,
        args,
        stable::ACT_LEVEL,
        session,
        stable::ACT_CLASS,
        false,
    )
    .await
}

/// `stable.settle` inside `tx`: run a Stable act the human said yes to — the words of what happened.
#[allow(clippy::too_many_arguments)]
pub async fn settle_in(
    tx: &Transaction<'_>,
    w: &World,
    gw: Option<&Gateway>,
    held: &Value,
    asker: &str,
    ask_id: &str,
    parent_marker: Option<&str>,
    confirmed_by: Option<&str>,
) -> Result<String, RoadError> {
    let tool = held["tool"].as_str().unwrap_or_default();
    let a = &held["args"];
    let at = FactWhere {
        parent_marker,
        ask: Some(ask_id),
        confirmed_by,
    };
    match tool {
        REGISTER_TOOL => {
            let made =
                register_mind_in(tx, w, gw, &python_str(&a["name"]), &a["deal"], asker).await?;
            let d = &made["manifest"];
            Ok(format!(
                "the {} LLM stands in the Stable — {} {}, ${} in / ${} out per million, class {}; say \u{201c}check \
                 the minds\u{201d} to hear it answer",
                python_str(&made["name"]),
                python_str(&d["provider"]),
                python_str(&d["model"]),
                g_fmt(d["price"]["in_per_m"].as_f64().unwrap_or(0.0)),
                g_fmt(d["price"]["out_per_m"].as_f64().unwrap_or(0.0)),
                python_str(&d["class"])
            ))
        }
        ASSIGN_TOOL => {
            let made = assign_in(
                tx,
                w,
                &python_str(&a["subject"]),
                &python_str(&a["klass"]),
                &python_str(&a["stall"]),
                asker,
                at,
            )
            .await?;
            let who = if made["subject"] == json!("*") {
                "every body".to_string()
            } else {
                python_str(&made["subject"])
            };
            let work = if made["klass"] == json!(ANY) {
                "all its".to_string()
            } else {
                python_str(&made["klass"])
            };
            Ok(format!(
                "{who} now uses the {} LLM for {work} work — recorded",
                python_str(&made["stall"])
            ))
        }
        UNASSIGN_TOOL => {
            let made = unassign_in(
                tx,
                w,
                &python_str(&a["subject"]),
                &python_str(&a["klass"]),
                asker,
                at,
            )
            .await?;
            Ok(format!(
                "{}'s {} assignment to {} is lifted — recorded",
                python_str(&made["subject"]),
                python_str(&made["klass"]),
                python_str(&made["stall"])
            ))
        }
        REFILL_TOOL => {
            let gw = gw.ok_or_else(|| refused("the gateway is dark — a refill needs it"))?;
            let name = a["name"].as_str().filter(|n| !n.is_empty());
            let made = refill_in(
                tx,
                w,
                gw,
                &python_str(&a["did"]),
                a["usd"].as_f64().unwrap_or(0.0),
                asker,
                name,
                at,
            )
            .await?;
            Ok(format!(
                "{} refilled by ${} — its allowance is now ${}",
                name.map(str::to_string)
                    .unwrap_or_else(|| python_str(&a["did"])),
                g_fmt(made["added_usd"].as_f64().unwrap_or(0.0)),
                g_fmt(made["max_usd"].as_f64().unwrap_or(0.0))
            ))
        }
        REPIN_TOOL => {
            let made = repin_mind_in(tx, w, gw, &python_str(&a["name"]), &a["deal"], asker).await?;
            Ok(format!(
                "the {} LLM is re-pinned to its new deal (version {}) — the old pin stays in its history",
                python_str(&made["name"]),
                python_str(&made["version"])
            ))
        }
        RETIRE_TOOL => {
            let made = retire_mind_in(tx, w, gw, &python_str(&a["name"]), asker, at).await?;
            Ok(format!(
                "the {} {} is retired — at rest on the shelf, recorded, never deleted; say \u{201c}restore the {} {}\u{201d} \
                 to bring it back",
                python_str(&made["name"]),
                python_str(&made["kind"]),
                python_str(&made["name"]),
                python_str(&made["kind"])
            ))
        }
        other => Err(refused(format!(
            "no Stable act named {}",
            crate::py::repr_str(other)
        ))),
    }
}

// ---- the market's eyes: drift and EOL off the catalog -----------------------------------------------------

static CATALOG: LazyLock<Mutex<Option<(Instant, Value)>>> = LazyLock::new(|| Mutex::new(None));

/// `stable.openrouter_catalog`: OpenRouter's public list, keyless — by model
/// id: price per million in and out, context, expiry when named. Cached 300 s;
/// intel never authority — a miss returns the last catalog, or nothing.
pub async fn openrouter_catalog() -> Value {
    if let Some((at, v)) = CATALOG.lock().unwrap_or_else(|p| p.into_inner()).clone() {
        if at.elapsed() < CATALOG_TTL {
            return v;
        }
    }
    let fetched = tokio::task::spawn_blocking(|| {
        ureq::AgentBuilder::new()
            .timeout(Duration::from_secs(15))
            .build()
            .get(OPENROUTER_CATALOG)
            .set("accept", "application/json")
            .call()
            .ok()
            .and_then(|r| r.into_json::<Value>().ok())
    })
    .await
    .ok()
    .flatten();
    let Some(data) = fetched else {
        return CATALOG
            .lock()
            .unwrap_or_else(|p| p.into_inner())
            .clone()
            .map(|(_, v)| v)
            .unwrap_or(json!({}));
    };
    let mut out = serde_json::Map::new();
    for m in data["data"].as_array().cloned().unwrap_or_default() {
        let pr = &m["pricing"];
        let per_m = |v: &Value| -> f64 {
            let f = v
                .as_f64()
                .or_else(|| v.as_str().and_then(|s| s.parse().ok()))
                .unwrap_or(0.0);
            (f * 1e6 * 1e6).round() / 1e6
        };
        let expires = if m["expiration_date"].is_null() {
            m["deprecation_date"].clone()
        } else {
            m["expiration_date"].clone()
        };
        out.insert(
            python_str(&m["id"]),
            json!({"price": {"in_per_m": per_m(&pr["prompt"]), "out_per_m": per_m(&pr["completion"])},
                   "context": m["context_length"], "expires": expires}),
        );
    }
    let v = Value::Object(out);
    *CATALOG.lock().unwrap_or_else(|p| p.into_inner()) = Some((Instant::now(), v.clone()));
    v
}

/// `stable.seen_deal`: what the market says of this stall now.
pub async fn seen_deal(gw: Option<&Gateway>, s: &Value, catalog: Option<&Value>) -> Option<Value> {
    let m = &s["manifest"];
    if m["provider"] == json!("openrouter") {
        let cat = match catalog {
            Some(c) => c.clone(),
            None => openrouter_catalog().await,
        };
        return cat.get(m["model"].as_str().unwrap_or_default()).cloned();
    }
    let gw = gw?;
    gw.seen_deal(&python_str(&s["name"])).await.ok().flatten()
}

/// `stable.drift_scan`: every standing stall's pin against the market — a
/// move is recorded UNHEALTHY with what moved, never re-pinned by the machine.
pub async fn drift_scan(
    g: &mut Ground,
    w: &World,
    gw: Option<&Gateway>,
    by: &str,
    catalog: Option<&Value>,
) -> Result<Vec<Value>, RoadError> {
    let mut out = Vec::new();
    for s in services_live::rows(g.client(), &w.scope, Some("mind")).await? {
        if s["state"] == json!("retired") {
            continue;
        }
        let Some(seen) = seen_deal(gw, &s, catalog).await else {
            continue;
        };
        let pin = &s["manifest"];
        let pin_in = pin["price"]["in_per_m"].as_f64().unwrap_or(0.0);
        let pin_out = pin["price"]["out_per_m"].as_f64().unwrap_or(0.0);
        if pin_in == 0.0 && pin_out == 0.0 {
            continue; // a stall pinned without a price: nothing to drift from
        }
        let moved = drift(pin, &seen);
        if !moved.is_empty() {
            let name = python_str(&s["name"]);
            services_live::record_health(
                g,
                w,
                &name,
                Some(false),
                &format!("the deal moved under the pin: {}", moved.join("; ")),
                by,
            )
            .await?;
            let mut d = pin.clone();
            d["price"] = json!({"in_per_m": seen["price"]["in_per_m"].as_f64().unwrap_or(pin_in),
                                "out_per_m": seen["price"]["out_per_m"].as_f64().unwrap_or(pin_out)});
            if truthy(&seen["context"]) {
                d["context"] = seen["context"].clone();
            }
            out.push(json!({"name": name, "moved": moved, "deal": d}));
        }
    }
    Ok(out)
}

/// `stable.eol_scan`: every standing stall whose expiry is inside the horizon, with the swap.
pub async fn eol_scan(
    g: &Ground,
    scope: &str,
    gw: Option<&Gateway>,
    now: &str,
    catalog: Option<&Value>,
) -> Result<Vec<Value>, RoadError> {
    let horizon = dial_i(EOL_DIAL, EOL_DEFAULT);
    let rows = services_live::rows(g.client(), scope, Some("mind")).await?;
    let mut out = Vec::new();
    for s in &rows {
        if s["state"] == json!("retired") {
            continue;
        }
        let seen = seen_deal(gw, s, catalog).await.unwrap_or(json!({}));
        let exp = if truthy(&seen["expires"]) {
            seen["expires"].clone()
        } else {
            s["manifest"]["expires"].clone()
        };
        let exp_s = exp.as_str().map(str::to_string);
        let due = eol_due(exp_s.as_deref(), now, horizon);
        if due["due"] == json!(true) {
            out.push(
                json!({"name": s["name"], "expires": exp, "words": due["words"],
                            "swap": recommend(&rows, s["name"].as_str().unwrap_or_default())}),
            );
        }
    }
    Ok(out)
}

/// The kernel's newest held act of this tool about this service — `(ask_id, status)`.
pub async fn last_hold(
    g: &Ground,
    scope: &str,
    tool: &str,
    name: &str,
) -> Result<Option<(String, String)>, RoadError> {
    Ok(g
        .client()
        .query_opt(
            "SELECT ask_id, status FROM spine_asks WHERE scope = $1 AND served_by = $2 AND held IS NOT NULL AND \
             held::json->>'tool' = $3 AND (held::json->'args'->>'name' = $4 OR held::json->'args'->>'did' = $4) \
             ORDER BY asked_at DESC LIMIT 1",
            &[&scope, &KERNEL, &tool, &name],
        )
        .await?
        .map(|r| (r.get(0), r.get(1))))
}

/// `stable.proposals`: the keeper's proposals, each ONE hold at the
/// interlock (none while one waits): drift → re-pin; EOL → retire with the
/// swap; a drained body → refill; the strikes rule for minds.
pub async fn proposals(
    g: &mut Ground,
    w: &World,
    keeper: &str,
    gw: Option<&Gateway>,
    catalog: Option<&Value>,
) -> Result<Vec<Value>, RoadError> {
    let mut out = Vec::new();
    for d in drift_scan(g, w, gw, keeper, catalog).await? {
        let name = python_str(&d["name"]);
        if matches!(last_hold(g, &w.scope, REPIN_TOOL, &name).await?, Some((_, st)) if st == "awaiting-confirm")
        {
            continue;
        }
        let moved: Vec<String> = d["moved"]
            .as_array()
            .map(|a| a.iter().map(python_str).collect())
            .unwrap_or_default();
        let held = hold(
            g,
            w,
            REPIN_TOOL,
            json!({"name": name, "deal": d["deal"]}),
            &format!(
                "the stablekeeper proposes re-pinning the {name} LLM — {}",
                moved.join("; ")
            ),
            keeper,
            None,
        )
        .await?;
        out.push(json!({"kind": "repin", "name": name, "held": held}));
    }
    let now = envelope::now_iso();
    for e in eol_scan(g, &w.scope, gw, &now, catalog).await? {
        let name = python_str(&e["name"]);
        if matches!(last_hold(g, &w.scope, RETIRE_TOOL, &name).await?, Some((_, st)) if st == "awaiting-confirm")
        {
            continue;
        }
        let swap = &e["swap"];
        let tail = if truthy(&swap["stall"]) {
            format!(
                "; the swap: the {} LLM ({})",
                python_str(&swap["stall"]),
                python_str(&swap["why"])
            )
        } else {
            format!("; {}", python_str(&swap["why"]))
        };
        let held = hold(
            g,
            w,
            RETIRE_TOOL,
            json!({"name": name}),
            &format!(
                "the stablekeeper proposes retiring the {name} LLM — it {}{tail}",
                python_str(&e["words"])
            ),
            keeper,
            None,
        )
        .await?;
        out.push(json!({"kind": "retire", "name": name, "held": held}));
    }
    let drained = g
        .client()
        .query(
            "SELECT did, alias, max_usd FROM spine_mind_keys WHERE scope = $1 AND drained_at IS NOT NULL",
            &[&w.scope],
        )
        .await?;
    let drained: Vec<(String, String, f64)> = drained
        .iter()
        .map(|r| (r.get(0), r.get(1), r.get(2)))
        .collect();
    for (did, alias, max_usd) in drained {
        if matches!(last_hold(g, &w.scope, REFILL_TOOL, &did).await?, Some((_, st)) if st == "awaiting-confirm")
        {
            continue;
        }
        let name = alias.rsplit(':').next().unwrap_or(&alias).to_string();
        let add = max_usd.max(1.0);
        let held = hold(
            g,
            w,
            REFILL_TOOL,
            json!({"did": did, "name": name, "usd": add}),
            &format!(
                "the stablekeeper proposes refilling {name} by ${} — its allowance is spent and it cannot think",
                g_fmt(add)
            ),
            keeper,
            None,
        )
        .await?;
        out.push(json!({"kind": "refill", "name": name, "held": held}));
    }
    for p in crate::mcp_live::proposals(g, w, keeper, Some(&["mind"]), "the stablekeeper").await? {
        out.push(json!({"kind": "retire", "name": p["name"], "held": p["held"], "strikes": p["strikes"]}));
    }
    Ok(out)
}

/// `stable.keeper_beat`: every standing mind pinged through the gateway under
/// the keeper's DID (metered), then the market's eyes, then the proposals.
pub async fn keeper_beat(
    g: &mut Ground,
    w: &World,
    keeper: &str,
    gw: Option<&Gateway>,
) -> Result<Value, RoadError> {
    let checked = services_live::check_all(g, w, gw, Some("mind"), keeper).await?;
    let proposed = proposals(g, w, keeper, gw, None).await?;
    Ok(json!({"checked": checked, "proposed": proposed}))
}

/// The Stable keeper's cadence (`SPINE_MIND_CHECK_S`, default 600 s, at least 5).
pub fn mind_check_s() -> f64 {
    dial_f(MIND_CHECK_DIAL, MIND_CHECK_DEFAULT).max(5.0)
}

// ---- search and spend ---------------------------------------------------------------------------------

/// `stable.search`: which mind knows or does what — by words, class, ceiling price, modality.
pub async fn search(
    g: &Ground,
    scope: &str,
    q: Option<&str>,
    klass: Option<&str>,
    max_in_per_m: Option<f64>,
    modality: Option<&str>,
) -> Result<Vec<Value>, RoadError> {
    let words = q.unwrap_or("").trim().to_lowercase();
    let mut out = Vec::new();
    for s in stalls(g, scope).await? {
        let m = &s["manifest"];
        if let Some(k) = klass {
            if m["class"].as_str() != Some(k) {
                continue;
            }
        }
        if let Some(cap) = max_in_per_m {
            if m["price"]["in_per_m"].as_f64().unwrap_or(0.0) > cap {
                continue;
            }
        }
        if let Some(mo) = modality {
            if !m["modalities"]
                .as_array()
                .is_some_and(|a| a.iter().any(|x| x.as_str() == Some(mo)))
            {
                continue;
            }
        }
        let mods: Vec<String> = m["modalities"]
            .as_array()
            .map(|a| a.iter().map(python_str).collect())
            .unwrap_or_default();
        let hay = format!(
            "{} {} {} {} {}",
            python_str(&s["name"]),
            m["model"].as_str().unwrap_or(""),
            m["provider"].as_str().unwrap_or(""),
            m["class"].as_str().unwrap_or(""),
            mods.join(" ")
        )
        .to_lowercase();
        if !words.is_empty() && !words.split_whitespace().all(|w| hay.contains(w)) {
            continue;
        }
        out.push(s);
    }
    Ok(out)
}

/// `stable.spend`: the meter rolled up — per body, per mind; today and all time.
pub async fn spend(g: &Ground) -> Result<Value, RoadError> {
    if !crate::schema::has_table(g, "spine_meter").await? {
        return Ok(json!({"rows": [], "usd": 0.0, "usd_today": 0.0}));
    }
    let rows: Vec<Value> = g
        .client()
        .query(
            "SELECT did, coalesce(stall, model), count(*), coalesce(sum(usd), 0), coalesce(sum(usd) FILTER (WHERE \
             at >= date_trunc('day', now())), 0), sum(tokens_in), sum(tokens_out), count(*) FILTER (WHERE ok = \
             false) FROM spine_meter GROUP BY did, coalesce(stall, model) ORDER BY 4 DESC",
            &[],
        )
        .await?
        .iter()
        .map(|r| {
            json!({"did": r.get::<_, String>(0), "stall": r.get::<_, String>(1), "calls": r.get::<_, i64>(2),
                   "usd": r.get::<_, f64>(3), "usd_today": r.get::<_, f64>(4),
                   "tokens_in": r.get::<_, Option<i64>>(5).unwrap_or(0), "tokens_out": r.get::<_, Option<i64>>(6).unwrap_or(0),
                   "failed": r.get::<_, i64>(7)})
        })
        .collect();
    let round6 = |x: f64| (x * 1e6).round() / 1e6;
    let usd: f64 = rows.iter().map(|r| r["usd"].as_f64().unwrap_or(0.0)).sum();
    let today: f64 = rows
        .iter()
        .map(|r| r["usd_today"].as_f64().unwrap_or(0.0))
        .sum();
    Ok(json!({"rows": rows, "usd": round6(usd), "usd_today": round6(today)}))
}

/// `stable.reconcile`: the 100%, thought by thought — the last N metered
/// thoughts of each of this world's bodies against the gateway's ledger.
pub async fn reconcile(
    g: &Ground,
    scope: &str,
    gw: Option<&Gateway>,
    n: i64,
    grace_s: f64,
) -> Result<Value, RoadError> {
    let both = crate::schema::has_table(g, "spine_mind_keys").await?
        && crate::schema::has_table(g, "spine_meter").await?;
    let mut out = json!({"checked": 0, "agreed": 0, "fresh": 0, "unkeyed": 0, "mismatched": [], "meter_usd": 0.0, "gateway_usd": 0.0});
    if !both {
        out["words"] = json!("no lease and no meter on this ground yet");
        return Ok(out);
    }
    let Some(gw) = gw else {
        out["words"] = json!("no gateway to reconcile against");
        return Ok(out);
    };
    let dids: Vec<String> = g
        .client()
        .query(
            "SELECT did FROM spine_mind_keys WHERE scope = $1",
            &[&scope],
        )
        .await?
        .iter()
        .map(|r| r.get(0))
        .collect();
    let (mut checked, mut agreed, mut fresh, mut unkeyed) = (0i64, 0i64, 0i64, 0i64);
    let (mut meter_usd, mut gateway_usd) = (0.0f64, 0.0f64);
    let mut mismatched = Vec::new();
    for did in dids {
        let mine = g
            .client()
            .query(
                "SELECT request_id, usd, stall, extract(epoch FROM (clock_timestamp() - at))::float8 FROM spine_meter \
                 WHERE did = $1 AND ok AND request_id IS NOT NULL ORDER BY meter_id DESC LIMIT $2",
                &[&did, &n],
            )
            .await?;
        if mine.is_empty() {
            continue;
        }
        let theirs = match gw.spend_logs(&did).await {
            Ok(rows) => rows,
            Err(GatewayDark(w)) => {
                out["words"] = json!(w);
                return Ok(out);
            }
        };
        for r in &mine {
            let rid: String = r.get(0);
            let usd: Option<f64> = r.get(1);
            let stall: Option<String> = r.get(2);
            let age: Option<f64> = r.get(3);
            if !rid.starts_with("chatcmpl-") {
                unkeyed += 1;
                continue;
            }
            checked += 1;
            meter_usd += usd.unwrap_or(0.0);
            let row = theirs
                .iter()
                .find(|t| t["request_id"].as_str() == Some(rid.as_str()));
            match row {
                None => {
                    if age.unwrap_or(0.0) < grace_s {
                        fresh += 1;
                    } else {
                        mismatched.push(json!({"request_id": rid, "stall": stall, "meter_usd": usd, "gateway_usd": null,
                                               "why": "no row in the gateway's ledger"}));
                    }
                }
                Some(t) => {
                    let gusd = t["spend"].as_f64().unwrap_or(0.0);
                    gateway_usd += gusd;
                    if (gusd - usd.unwrap_or(0.0)).abs() <= 1e-6 {
                        agreed += 1;
                    } else {
                        mismatched.push(json!({"request_id": rid, "stall": stall, "meter_usd": usd, "gateway_usd": gusd,
                                               "why": "the dollars differ"}));
                    }
                }
            }
        }
    }
    let round6 = |x: f64| (x * 1e6).round() / 1e6;
    let older = if unkeyed > 0 {
        format!(
            " · {unkeyed} older thought{} not comparable (metered before the ledger's id was kept)",
            if unkeyed != 1 { "s" } else { "" }
        )
    } else {
        String::new()
    };
    let words = if checked == 0 {
        format!("no thought metered yet{older}")
    } else if mismatched.is_empty() {
        format!(
            "the meter and the gateway agree on {agreed} of the last {checked} thoughts{}{older}",
            if fresh > 0 {
                format!(" ({fresh} not yet flushed)")
            } else {
                String::new()
            }
        )
    } else {
        let zero = mismatched
            .iter()
            .filter(|x| x["gateway_usd"] == json!(0.0))
            .count();
        format!(
            "{} of the last {checked} thoughts disagree — {}the meter reads ${:.4}, the gateway ${:.4}{older}",
            mismatched.len(),
            if zero > 0 { format!("{zero} charged $0 by the gateway (streamed before the entry named its base model); ") } else { String::new() },
            round6(meter_usd),
            round6(gateway_usd)
        )
    };
    Ok(
        json!({"checked": checked, "agreed": agreed, "fresh": fresh, "unkeyed": unkeyed, "mismatched": mismatched,
              "meter_usd": round6(meter_usd), "gateway_usd": round6(gateway_usd), "words": words}),
    )
}

/// `glass.mind_line` (walk #12, W43): which LLM this body thinks with NOW and
/// why — the Stable's decision for it, and the last thought it rode.
pub async fn mind_line(
    g: &Ground,
    scope: &str,
    name: &str,
    did: &str,
    template: Option<&Value>,
) -> Result<Option<Value>, RoadError> {
    let Some(mind) = template.map(|t| &t["mind"]).filter(|m| truthy(m)) else {
        return Ok(None);
    };
    let d = resolve_for(
        g.client(),
        scope,
        Some(name),
        mind["model"].as_str(),
        mind["class"].as_str(),
        mind["pin"].as_str(),
    )
    .await?;
    let why = if truthy(&d["why"]) {
        d["why"].clone()
    } else {
        d["reason"].clone()
    };
    let mut out = json!({"stall": d["stall"], "why": why, "degraded": truthy(&d["degraded"])});
    if let Some(stall) = d["stall"].as_str() {
        if let Some(s) = services_live::get(g.client(), scope, stall).await? {
            let m = &s["manifest"];
            out["route"] = json!(format!(
                "{} {}",
                m["provider"].as_str().unwrap_or("?"),
                m["model"].as_str().unwrap_or("?")
            ));
            out["klass"] = m["class"].clone();
        }
    }
    if crate::schema::has_table(g, "spine_meter").await? {
        if let Some(r) = g
            .client()
            .query_opt(
                "SELECT stall, usd, at, ok FROM spine_meter WHERE did = $1 AND stall IS NOT NULL ORDER BY meter_id DESC \
                 LIMIT 1",
                &[&did],
            )
            .await?
        {
            out["last"] = json!({"stall": r.get::<_, String>(0), "usd": r.get::<_, Option<f64>>(1),
                                 "at": isoformat(r.get::<_, SystemTime>(2)), "ok": r.get::<_, bool>(3)});
        }
    }
    Ok(Some(out))
}

/// The register door's deal from a body — `stable.deal` on the door's fields.
pub fn deal_from(p: &Value) -> Result<Value, RoadError> {
    let key = p.get("key").filter(|k| truthy(k)).map(|k| k.as_str());
    deal(
        &python_str(&p["model"]),
        &python_str(&p["provider"]),
        DealAsk {
            base: p["base"].as_str().filter(|b| !b.is_empty()),
            price: p.get("price"),
            context: p.get("context"),
            modalities: p.get("modalities"),
            klass: Some(
                p["klass"]
                    .as_str()
                    .filter(|k| !k.is_empty())
                    .unwrap_or("standard"),
            ),
            key,
            expires: p["expires"].as_str(),
        },
    )
    .map_err(refused)
}

/// The act's words for a held Stable act (re-exported for the doors).
pub fn words_for(tool: &str, args: &Value) -> String {
    act_words(tool, args)
}
