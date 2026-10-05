// PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch Phase 8 THE WORKSHOP sp1, THE PATH: the levels on the ground · 2026-10-05
//! THE PATH's ground half (canon 0010 lock 2 · 0005 Phase 8 sp1), mirroring
//! `orreth_spine.levels`' record half word for word: `spine_levels` (schema 5) — one row
//! per level of this universe; the universe's own row seeded at light with the cell's
//! declared mode (`SPINE_MODE`, default dev), tightened on a relight and never loosened;
//! the crew manifest's floors and rooms declared at light; a floor or room opened on a
//! person's word through the kernel's held act (`level.open`, L2); the listing with what
//! stands HERE and what ROLLS UP from within (the 0005 monoid at its minimum); the
//! cascade at a path (0007's fold at its minimum: the policy sheet's rules the universe's
//! floors, each level's `declares` its soft · skills · floors).

use crate::ground::Ground;
use crate::levels::{self, BY_MANIFEST, KERNEL};
use crate::world::{isoformat, json_text, refused, RoadError, World};
use serde_json::{json, Value};
use std::time::SystemTime;
use tokio_postgres::GenericClient;

pub use crate::schema::LEVELS_DDL;

const COLS: &str =
    "path, scope, level, name, parent, mode, experiment, declares, opened_by, opened_at, ask";

fn view(r: &tokio_postgres::Row) -> Value {
    let path: String = r.get(0);
    json!({
        "path": path, "scope": r.get::<_, String>(1), "level": r.get::<_, String>(2),
        "name": r.get::<_, String>(3), "parent": r.get::<_, Option<String>>(4),
        "mode": r.get::<_, String>(5), "experiment": r.get::<_, bool>(6),
        "declares": json_text(r.get::<_, Option<String>>(7).as_deref()),
        "opened_by": r.get::<_, String>(8), "opened_at": isoformat(r.get::<_, SystemTime>(9)),
        "ask": r.get::<_, Option<String>>(10), "words": levels::words(&path).unwrap_or_default(),
    })
}

/// One level's row, or none.
pub async fn row<C: GenericClient>(c: &C, path: &str) -> Result<Option<Value>, RoadError> {
    Ok(c
        .query_opt(
            &format!("SELECT {COLS} FROM spine_levels WHERE path = $1"),
            &[&path],
        )
        .await?
        .map(|r| view(&r)))
}

/// The row and its fact, inside the caller's transaction.
#[allow(clippy::too_many_arguments)]
async fn insert(
    tx: &tokio_postgres::Transaction<'_>,
    path: &str,
    mode: &str,
    experiment: bool,
    declares: Option<&Value>,
    by: &str,
    reason: &str,
    ask: Option<&str>,
    marker: Option<&str>,
) -> Result<Value, RoadError> {
    let e = levels::opened_fact(path, mode, experiment, by, reason).map_err(refused)?;
    let declares_text = declares.map(|d| d.to_string());
    tx.execute(
        "INSERT INTO spine_levels (path, scope, level, name, parent, mode, experiment, declares, opened_by, ask, \
         marker) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11) ON CONFLICT (path) DO NOTHING",
        &[
            &path,
            &levels::universe_of(path).map_err(refused)?,
            &levels::level_of(path).map_err(refused)?,
            &levels::name_of(path).map_err(refused)?,
            &levels::parent_of(path).map_err(refused)?,
            &mode,
            &experiment,
            &declares_text,
            &by,
            &ask,
            &marker,
        ],
    )
    .await?;
    crate::outbox::add_row(
        tx,
        &crate::envelope::encode(&e)?,
        e["message_id"].as_str().unwrap_or_default(),
    )
    .await?;
    Ok(e)
}

/// The universe's own row, settled at light: absent → opened with the declared mode
/// (`dial`, else `SPINE_MODE`, default dev) and said as a fact; present → the dial may
/// TIGHTEN it (recorded) and never loosen it (a prod universe refuses to light as dev).
pub async fn ensure_universe(
    g: &mut Ground,
    universe: &str,
    dial: Option<&str>,
) -> Result<Value, RoadError> {
    levels::parse(universe).map_err(refused)?;
    if levels::level_of(universe).map_err(refused)? != "universe" {
        return Err(refused(format!(
            "a kernel stands at a universe — SPINE_SCOPE says {universe}"
        )));
    }
    let env = std::env::var(levels::MODE_DIAL).ok();
    let mode = levels::mode_of_dial(dial.or(env.as_deref())).map_err(refused)?;
    let have = row(g.client(), universe).await?;
    match have {
        None => {
            let tx = g.client_mut().transaction().await?;
            insert(&tx, universe, &mode, false, None, KERNEL, "opened at light", None, None).await?;
            tx.commit().await?;
        }
        Some(r) if r["mode"].as_str() != Some(mode.as_str()) => {
            let was = r["mode"].as_str().unwrap_or("dev").to_string();
            levels::tighten(&was, Some(&mode)).map_err(|e| {
                refused(format!(
                    "{universe} is a {was} universe and {} asks {mode}: {e}",
                    levels::MODE_DIAL
                ))
            })?;
            let tx = g.client_mut().transaction().await?;
            tx.execute(
                "UPDATE spine_levels SET mode = $1 WHERE path = $2",
                &[&mode, &universe],
            )
            .await?;
            let e = levels::opened_fact(universe, &mode, false, KERNEL, "tightened at light")
                .map_err(refused)?;
            crate::outbox::add_row(
                &tx,
                &crate::envelope::encode(&e)?,
                e["message_id"].as_str().unwrap_or_default(),
            )
            .await?;
            tx.commit().await?;
        }
        Some(_) => {}
    }
    row(g.client(), universe)
        .await?
        .ok_or_else(|| refused(format!("{universe} could not be opened")))
}

/// What a level would be, or the refusal in words: the parent stands here, the child law,
/// mode tighten-only, the experiment room, not already open.
pub async fn check_open<C: GenericClient>(
    c: &C,
    parent: &str,
    level: &str,
    name: &str,
    mode: Option<&str>,
    experiment: bool,
) -> Result<(String, String, bool), RoadError> {
    let Some(up) = row(c, parent).await? else {
        return Err(refused(if levels::ok(parent) {
            format!("{parent} is not open here")
        } else {
            format!("{} — got {}", levels::GRAMMAR, levels::py_repr(parent))
        }));
    };
    let path = levels::child(parent, level, name).map_err(refused)?;
    let m = levels::tighten(up["mode"].as_str().unwrap_or("dev"), mode).map_err(refused)?;
    levels::experiment_ok(level, experiment).map_err(refused)?;
    if row(c, &path).await?.is_some() {
        return Err(refused(format!(
            "{} is already open",
            levels::words(&path).unwrap_or_default()
        )));
    }
    Ok((path, m, experiment))
}

fn arg<'a>(args: &'a Value, k: &str) -> &'a str {
    args[k].as_str().unwrap_or_default()
}

/// The held act, settled: the row and its fact in the caller's transaction; the words.
pub async fn open_in(
    tx: &tokio_postgres::Transaction<'_>,
    args: &Value,
    by: &str,
    ask: Option<&str>,
    marker: Option<&str>,
) -> Result<String, RoadError> {
    let (path, mode, experiment) = check_open(
        tx,
        arg(args, "parent"),
        arg(args, "level"),
        arg(args, "name"),
        args["mode"].as_str(),
        args["experiment"].as_bool().unwrap_or(false),
    )
    .await?;
    insert(
        tx,
        &path,
        &mode,
        experiment,
        args.get("declares").filter(|d| !d.is_null()),
        by,
        "opened on a person's word",
        ask,
        marker,
    )
    .await?;
    levels::opened_words(&path, &mode, experiment).map_err(refused)
}

/// `POST /levels/open`: the laws checked NOW (a refusal is immediate, in words), then the
/// act held at L2 for the person's yes — the kernel's own held act, `level.open`.
pub async fn hold_open(
    g: &mut Ground,
    w: &World,
    args: &Value,
    person: &str,
    session: Option<&str>,
) -> Result<Value, RoadError> {
    let parent = if arg(args, "parent").is_empty() {
        w.scope.clone()
    } else {
        arg(args, "parent").to_string()
    };
    let (path, mode, experiment) = check_open(
        g.client(),
        &parent,
        arg(args, "level"),
        arg(args, "name"),
        args["mode"].as_str(),
        args["experiment"].as_bool().unwrap_or(false),
    )
    .await?;
    let text = format!(
        "open {} as {mode}{}",
        levels::words(&path).map_err(refused)?,
        if experiment { " — an experiment room" } else { "" }
    );
    let mut held_args = json!({
        "parent": parent, "level": levels::level_of(&path).map_err(refused)?,
        "name": levels::name_of(&path).map_err(refused)?, "mode": mode, "experiment": experiment,
    });
    if let Some(d) = args.get("declares").filter(|d| !d.is_null()) {
        held_args["declares"] = d.clone();
    }
    let held = crate::proof_live::hold_kernel_act(
        g,
        w,
        &text,
        person,
        levels::OPEN_TOOL,
        held_args,
        levels::OPEN_LEVEL,
        session,
        levels::OPEN_CLASS,
        false,
    )
    .await?;
    Ok(json!({"held": held, "level": levels::OPEN_LEVEL, "class": levels::OPEN_CLASS, "path": path}))
}

/// The crew manifest's levels at light: each opened under the universe if it is not yet
/// (mode tightened from its parent, `the crew manifest` the opener); one that would loosen
/// refuses the light in words. Returns the rows opened now.
pub async fn declare(g: &mut Ground, universe: &str, manifest: &Value) -> Result<Vec<Value>, RoadError> {
    let mut opened = Vec::new();
    for lv in levels::manifest_levels(manifest).map_err(refused)? {
        let path = levels::absolute(universe, Some(&lv.at)).map_err(refused)?;
        if row(g.client(), &path).await?.is_some() {
            continue;
        }
        let parent = levels::parent_of(&path).map_err(refused)?;
        let up = match &parent {
            Some(p) => row(g.client(), p).await?,
            None => None,
        };
        let Some(up) = up else {
            return Err(refused(format!(
                "the crew manifest declares {path} but {} is not open — declare the floor first",
                parent.unwrap_or_default()
            )));
        };
        let mode = levels::tighten(up["mode"].as_str().unwrap_or("dev"), lv.mode.as_deref())
            .map_err(|e| refused(format!("the crew manifest's level {path}: {e}")))?;
        levels::experiment_ok(levels::level_of(&path).map_err(refused)?, lv.experiment)
            .map_err(|e| refused(format!("the crew manifest's level {path}: {e}")))?;
        let tx = g.client_mut().transaction().await?;
        insert(
            &tx,
            &path,
            &mode,
            lv.experiment,
            lv.declares.as_ref(),
            BY_MANIFEST,
            "declared by the crew manifest",
            None,
            None,
        )
        .await?;
        tx.commit().await?;
        if let Some(r) = row(g.client(), &path).await? {
            opened.push(r);
        }
    }
    Ok(opened)
}

/// Every level of this universe, root first, each with what stands HERE and what is ROLLED
/// up from within it (the monoid at its minimum: bodies · asks served · spend).
pub async fn listing(g: &Ground, universe: &str) -> Result<Vec<Value>, RoadError> {
    let c = g.client();
    let mut rows: Vec<Value> = c
        .query(
            &format!("SELECT {COLS} FROM spine_levels WHERE scope = $1 ORDER BY path"),
            &[&universe],
        )
        .await?
        .iter()
        .map(view)
        .collect();
    let within = crate::world::within_sql("scope", 1);
    let mut bodies = std::collections::HashMap::new();
    for r in c
        .query(
            &format!(
                "SELECT scope, count(*) FROM (SELECT DISTINCT ON (name) name, scope FROM spine_joins WHERE {within} \
                 ORDER BY name, join_id DESC) j GROUP BY scope"
            ),
            &[&universe],
        )
        .await?
    {
        bodies.insert(r.get::<_, String>(0), r.get::<_, i64>(1));
    }
    let mut served = std::collections::HashMap::new();
    for r in c
        .query(
            &format!(
                "SELECT j.scope, count(*) FROM spine_asks a JOIN (SELECT DISTINCT ON (did) did, scope FROM spine_joins \
                 WHERE {within} ORDER BY did, join_id DESC) j ON a.served_by = j.did WHERE a.status <> 'received' \
                 GROUP BY j.scope"
            ),
            &[&universe],
        )
        .await?
    {
        served.insert(r.get::<_, String>(0), r.get::<_, i64>(1));
    }
    let mut usd: std::collections::HashMap<String, f64> = std::collections::HashMap::new();
    if crate::schema::has_table(g, "spine_meter").await? {
        for r in c
            .query(
                &format!(
                    "SELECT scope, coalesce(sum(usd), 0)::float8 FROM spine_meter WHERE {within} GROUP BY scope"
                ),
                &[&universe],
            )
            .await?
        {
            usd.insert(r.get::<_, String>(0), r.get::<_, f64>(1));
        }
    }
    let paths: Vec<String> = rows
        .iter()
        .map(|r| r["path"].as_str().unwrap_or_default().to_string())
        .collect();
    for r in rows.iter_mut() {
        let p = r["path"].as_str().unwrap_or_default().to_string();
        r["here"] = json!({
            "bodies": bodies.get(&p).copied().unwrap_or(0), "asks_served": served.get(&p).copied().unwrap_or(0),
            "usd": usd.get(&p).copied().unwrap_or(0.0),
        });
    }
    let heres: Vec<(String, Value)> = rows
        .iter()
        .map(|r| (r["path"].as_str().unwrap_or_default().to_string(), r["here"].clone()))
        .collect();
    for (i, r) in rows.iter_mut().enumerate() {
        let mut b = levels::empty_bundle();
        let (mut nb, mut na) = (0i64, 0i64);
        for (p, here) in &heres {
            if levels::within(p, &paths[i]) {
                nb += here["bodies"].as_i64().unwrap_or(0);
                na += here["asks_served"].as_i64().unwrap_or(0);
                let mut one = levels::empty_bundle();
                one["cost"]["usd"] = json!(here["usd"].as_f64().unwrap_or(0.0));
                b = levels::merge(&b, &one);
            }
        }
        r["rolled"] = json!({"bodies": nb, "asks_served": na, "usd": b["cost"]["usd"], "bundle": b});
    }
    Ok(rows)
}

/// The universe tier's floors: the policy sheet's rules, each a floor.
pub fn policy_floors() -> Vec<Value> {
    let p = std::env::var("SPINE_POLICY")
        .ok()
        .filter(|p| !p.is_empty())
        .map(std::path::PathBuf::from)
        .unwrap_or_else(|| {
            crate::tools::spine_dir()
                .join("policy")
                .join("covenant-policy.v1.json")
        });
    std::fs::read_to_string(&p)
        .ok()
        .and_then(|t| serde_json::from_str::<Value>(&t).ok())
        .and_then(|d| d["rules"].as_array().cloned())
        .unwrap_or_default()
}

/// The cascade at a path: the tiers are its ancestors' rows, folded root → leaf.
pub async fn context(g: &Ground, path: &str) -> Result<Value, RoadError> {
    let mut tiers = Vec::new();
    for p in levels::ancestors(path).map_err(refused)? {
        let Some(r) = row(g.client(), &p).await? else {
            return Err(refused(format!("{p} is not open here")));
        };
        let d = r["declares"].clone();
        let mut floors: Vec<Value> = d["floors"].as_array().cloned().unwrap_or_default();
        if r["level"] == "universe" {
            let mut all = policy_floors();
            all.append(&mut floors);
            floors = all;
        }
        tiers.push(json!({
            "scope": p, "mode": r["mode"], "version": "0",
            "soft": d.get("soft").cloned().unwrap_or(json!({})),
            "skills": d.get("skills").cloned().unwrap_or(json!({})),
            "floors": floors,
        }));
    }
    let mut out = levels::cascade(&tiers).map_err(refused)?;
    out["words"] = json!(levels::words(path).map_err(refused)?);
    Ok(out)
}
