// PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch Phase 8 THE WORKSHOP sp2, THE SHELF WIDENED: the wear table · the draft shelf · the cut · the crafts seeded at light · 2026-10-05
//! THE SHELF WIDENED on the ground — `orreth_spine.crafts` ported (canon 0010 lock 3 · 0004
//! AG-9 · 0005 Phase 8 sp2), schema 6: THE WEAR TABLE (`spine_wear` — which body wears which
//! component at which version; the body writes its rows in its join's transaction, this
//! kernel READS them: "in use by N", the blast radius, the repo-to-running correlation) and
//! THE DRAFT SHELF (`spine_drafts` — a draft lives in the ground UNDER THE PERSON; only its
//! author's seat reads it; saving one is routine, L1, no fact; THE CUT is the gate — the
//! kernel's own held act `craft.cut` at the level the class demands, settled onto the shelf as
//! the ladder's own register or version with the person on the chain, the draft spent). At
//! light the kernel registers every craft the spine ships (the templates and bindings, the
//! covenant policy, the graphs, the golden sets, the prompts and the skills) — the same self
//! every boot; a changed declaration re-pins. A craft's health is its declaration reading
//! whole (a template's graph must stand on the shelf).

use crate::crafts::{
    self, craft_name, cut_demand, cut_words, is_craft, validate, CRAFT_KINDS, CUT_CLASS, CUT_TOOL,
};
use crate::ground::Ground;
use crate::py::python_str;
use crate::services_live;
use crate::world::{isoformat, refused, token_hex, within_sql, RoadError, World};
use serde_json::{json, Value};
use std::path::Path;
use std::time::SystemTime;
use tokio_postgres::{GenericClient, Transaction};

pub const KERNEL: &str = "the kernel";

// ---- the shipped crafts, read from the spine home (both kernels read the same files) ----

fn read_json(p: &Path) -> Option<Value> {
    std::fs::read_to_string(p)
        .ok()
        .and_then(|t| serde_json::from_str(&t).ok())
}

fn folder(spine: &Path, name: &str) -> Vec<Value> {
    let mut paths: Vec<_> = std::fs::read_dir(spine.join(name))
        .map(|rd| {
            rd.filter_map(Result::ok)
                .map(|e| e.path())
                .filter(|p| p.extension().and_then(|e| e.to_str()) == Some("json"))
                .collect()
        })
        .unwrap_or_default();
    paths.sort();
    paths.iter().filter_map(|p| read_json(p).map(|v| (p.clone(), v))).map(|(p, v)| {
        // the harness's bare golden list, wrapped in its declaration (the file's stem names the template)
        if let Value::Array(cases) = &v {
            let stem = p.file_name().and_then(|f| f.to_str()).unwrap_or("").split('.').next().unwrap_or("").to_string();
            return crafts::golden_document(&stem, cases);
        }
        v
    }).collect()
}

/// `crafts.shipped`: every craft the spine ships — `[{name, kind, shelf_name, manifest}]`.
pub fn shipped(spine: &Path) -> Vec<Value> {
    let mut out: Vec<Value> = Vec::new();
    let mut seen: Vec<String> = Vec::new();
    let mut one = |kind: &str, doc: Value, name: Option<String>| {
        if !doc.is_object() {
            return;
        }
        let n = name.or_else(|| doc.get("name").and_then(Value::as_str).map(str::to_string));
        let Some(n) = n.filter(|n| !n.is_empty()) else { return };
        let Ok(sn) = craft_name(&n, kind) else { return };
        if seen.contains(&sn) {
            return;
        }
        seen.push(sn.clone());
        out.push(json!({"name": n, "kind": kind, "shelf_name": sn, "manifest": doc}));
    };
    for d in folder(spine, "templates") {
        one("template", d, None);
    }
    for d in folder(spine, "bindings") {
        one("binding", d, None);
    }
    if let Some(pol) = read_json(&spine.join("policy").join("covenant-policy.v1.json")) {
        let n = pol.get("name").and_then(Value::as_str).unwrap_or("covenant-policy").to_string();
        one("policy", pol, Some(n));
    }
    for d in folder(spine, "graphs") {
        one("graph", d, None);
    }
    for d in folder(spine, "golden") {
        let t = d.get("template").and_then(Value::as_str).map(str::to_string);
        one("golden", d, t);
    }
    for d in folder(spine, "prompts") {
        one("prompt", d, None);
    }
    for d in folder(spine, "skills") {
        one("skill", d, None);
    }
    out
}

/// `crafts.seed`: at light the kernel registers every craft the spine ships — the same self
/// every boot; a changed declaration re-pins (a fact, never unhealthy). `{registered, versioned, refused}`.
pub async fn seed(g: &mut Ground, w: &World, spine: &Path) -> Result<Value, RoadError> {
    let (mut made, mut versioned, mut refused_) = (Vec::new(), Vec::new(), Vec::new());
    for c in shipped(spine) {
        let (kind, sn, m) = (python_str(&c["kind"]), python_str(&c["shelf_name"]), c["manifest"].clone());
        let v = validate(&kind, &m);
        if v["ok"] != json!(true) {
            refused_.push(format!("{sn}: {}", python_str(&v["reason"])));
            continue;
        }
        let before = services_live::get(g.client(), &w.scope, &sn).await?;
        let out = match &before {
            Some(b) if b["kind"] == json!(kind) && b["state"] != json!("retired") && b["manifest_hash"] != json!(crafts::pin(&m)) => {
                services_live::version(g, w, &sn, &m, KERNEL).await.map(|_| versioned.push(sn.clone()))
            }
            _ => services_live::register(g, w, &sn, &kind, &m, KERNEL, None, &[]).await.map(|_| {
                if before.is_none() {
                    made.push(sn.clone());
                }
            }),
        };
        if let Err(e) = out {
            refused_.push(format!("{sn}: {e}"));
        }
    }
    Ok(json!({"registered": made, "versioned": versioned, "refused": refused_}))
}

/// A craft by its bare name and kind — the shelf's row, or none.
pub async fn get<C: GenericClient>(c: &C, scope: &str, name: &str, kind: &str) -> Result<Option<Value>, RoadError> {
    let sn = craft_name(name, kind).map_err(refused)?;
    services_live::get(c, scope, &sn).await
}

/// `crafts.probe`: a craft's honest health — its declaration reads whole; a template's graph
/// stands on the shelf; a golden set's template stands on the shelf.
pub async fn probe<C: GenericClient>(c: &C, scope: &str, row: &Value) -> Result<(Option<bool>, String), RoadError> {
    let (kind, m) = (python_str(&row["kind"]), row["manifest"].clone());
    let v = validate(&kind, &m);
    if v["ok"] != json!(true) {
        return Ok((Some(false), format!("the declaration does not read whole: {}", python_str(&v["reason"]))));
    }
    match kind.as_str() {
        "template" => {
            let gname = python_str(&m["graph"]);
            let g = get(c, scope, &gname, "graph").await?;
            match g {
                Some(g) if g["state"] != json!("retired") => Ok((Some(true), format!("the declaration reads whole; its graph {gname} stands on the shelf"))),
                _ => Ok((Some(false), format!("names graph {}, which is not on the shelf — register it, or restore it", crate::py::repr_str(&gname)))),
            }
        }
        "golden" => {
            let t = python_str(&m["template"]);
            let n = m["cases"].as_array().map(Vec::len).unwrap_or(0);
            match get(c, scope, &t, "template").await? {
                None => Ok((Some(true), format!("the declaration reads whole ({n} cases); its template {t} is not on the shelf yet"))),
                Some(_) => Ok((Some(true), format!("the declaration reads whole ({n} cases) for the {t} template"))),
            }
        }
        "graph" => {
            let n = m["nodes"].as_array().map(Vec::len).unwrap_or(0);
            let p = crafts::path(&m).unwrap_or_default();
            let br = crafts::branches(&m);                 // Phase 8 sp3: the probe names where it branches
            let tail = if br.is_empty() { String::new() } else { format!(" · branches at {}", br.join(", ")) };
            Ok((Some(true), format!("the declaration reads whole — {n} node(s): {}{tail}", p.join(" → "))))
        }
        _ => Ok((Some(true), "the declaration reads whole".into())),
    }
}

/// `crafts.golden_for`: a template's golden cases — the shelf's component first, the spine's
/// file as the fallback (a bare list, or the declaration).
pub async fn golden_for<C: GenericClient>(c: &C, scope: &str, template: &str, spine: &Path) -> Result<Vec<Value>, RoadError> {
    if let Some(row) = get(c, scope, template, "golden").await? {
        if row["state"] != json!("retired") {
            return Ok(row["manifest"]["cases"].as_array().cloned().unwrap_or_default());
        }
    }
    let p = spine.join("golden").join(format!("{template}.v0.json"));
    Ok(match read_json(&p) {
        Some(Value::Array(a)) => a,
        Some(v) => v["cases"].as_array().cloned().unwrap_or_default(),
        None => Vec::new(),
    })
}

// ---- the wear table (the body writes; this kernel reads) ----

fn wear_row(r: &tokio_postgres::Row) -> Value {
    json!({"body": r.get::<_, String>(0), "did": r.get::<_, String>(1), "life": r.get::<_, i32>(2),
           "component": r.get::<_, String>(3), "kind": r.get::<_, String>(4), "version": r.get::<_, Option<i32>>(5),
           "hash": r.get::<_, String>(6), "since": isoformat(r.get::<_, SystemTime>(7)), "scope": r.get::<_, String>(8)})
}

const WEAR_COLS: &str = "body, did, life, component, kind, version, hash, since, scope";

/// `crafts.worn_by`: who wears a component now (the open rows within this universe).
pub async fn worn_by<C: GenericClient>(c: &C, scope: &str, component: &str) -> Result<Vec<Value>, RoadError> {
    let q = format!("SELECT {WEAR_COLS} FROM spine_wear WHERE {} AND component = $2 AND until IS NULL ORDER BY body", within_sql("scope", 1));
    let rows = c.query(&q, &[&scope, &component]).await?;
    Ok(rows.iter().map(|r| {
        let mut v = wear_row(r);
        if let Some(m) = v.as_object_mut() {
            m.remove("component");
            m.remove("kind");
            m.remove("scope");
        }
        v
    }).collect())
}

/// `crafts.wears`: what a body wears now.
pub async fn wears<C: GenericClient>(c: &C, did: &str) -> Result<Vec<Value>, RoadError> {
    let rows = c
        .query("SELECT component, kind, version, hash, since FROM spine_wear WHERE did = $1 AND until IS NULL ORDER BY wear_id", &[&did])
        .await?;
    Ok(rows.iter().map(|r| json!({"component": r.get::<_, String>(0), "kind": r.get::<_, String>(1), "version": r.get::<_, Option<i32>>(2),
                                   "hash": r.get::<_, String>(3), "since": isoformat(r.get::<_, SystemTime>(4))})).collect())
}

/// `crafts.wear_counts`: component → how many bodies wear it now.
pub async fn wear_counts<C: GenericClient>(c: &C, scope: &str) -> Result<Value, RoadError> {
    let q = format!("SELECT component, count(DISTINCT did) FROM spine_wear WHERE {} AND until IS NULL GROUP BY component", within_sql("scope", 1));
    let rows = c.query(&q, &[&scope]).await?;
    let mut out = serde_json::Map::new();
    for r in rows {
        out.insert(r.get::<_, String>(0), json!(r.get::<_, i64>(1)));
    }
    Ok(Value::Object(out))
}

/// `crafts.wear_table`: the whole table, open rows, within this universe.
pub async fn wear_table<C: GenericClient>(c: &C, scope: &str) -> Result<Vec<Value>, RoadError> {
    let q = format!("SELECT {WEAR_COLS} FROM spine_wear WHERE {} AND until IS NULL ORDER BY body, wear_id", within_sql("scope", 1));
    Ok(c.query(&q, &[&scope]).await?.iter().map(wear_row).collect())
}

// ---- the draft shelf, under the person ----

const DRAFT_COLS: &str = "draft_id, person, kind, name, body, words, from_marker, at, updated_at, bench";

fn draft_row(r: &tokio_postgres::Row) -> Value {
    json!({"draft_id": r.get::<_, String>(0), "person": r.get::<_, String>(1), "kind": r.get::<_, String>(2),
           "name": r.get::<_, String>(3), "body": serde_json::from_str::<Value>(&r.get::<_, String>(4)).unwrap_or(json!({})),
           "words": r.get::<_, Option<String>>(5), "from_marker": r.get::<_, Option<String>>(6),
           "at": isoformat(r.get::<_, SystemTime>(7)), "updated_at": isoformat(r.get::<_, SystemTime>(8)),
           "bench": r.get::<_, Option<String>>(9)})   // Phase 8 sp8 THE BENCH: the effort it files on, or null (loose)
}

/// `benches.whole`'s drafts: the person's drafts ON a bench, newest first.
pub async fn drafts_on<C: GenericClient>(c: &C, scope: &str, person: &str, bench: &str) -> Result<Vec<Value>, RoadError> {
    let q = format!("SELECT {DRAFT_COLS} FROM spine_drafts WHERE scope = $1 AND person = $2 AND bench = $3 ORDER BY updated_at DESC");
    Ok(c.query(&q, &[&scope, &person, &bench]).await?.iter().map(draft_row).collect())
}

/// `crafts.drafts`: this person's drafts, newest first — and ONLY this person's (AG-9).
pub async fn drafts<C: GenericClient>(c: &C, scope: &str, person: &str) -> Result<Vec<Value>, RoadError> {
    let q = format!("SELECT {DRAFT_COLS} FROM spine_drafts WHERE scope = $1 AND person = $2 ORDER BY updated_at DESC");
    Ok(c.query(&q, &[&scope, &person]).await?.iter().map(draft_row).collect())
}

pub async fn draft<C: GenericClient>(c: &C, scope: &str, person: &str, draft_id: &str) -> Result<Option<Value>, RoadError> {
    let q = format!("SELECT {DRAFT_COLS} FROM spine_drafts WHERE draft_id = $1 AND scope = $2 AND person = $3");
    Ok(c.query_opt(&q, &[&draft_id, &scope, &person]).await?.as_ref().map(draft_row))
}

/// `crafts.save_draft`: routine (L1) — the draft lands under the person, new or updated. No fact.
#[allow(clippy::too_many_arguments)]
pub async fn save_draft(
    g: &mut Ground,
    w: &World,
    person: &str,
    kind: &str,
    name: &str,
    body: &Value,
    words: Option<&str>,
    draft_id: Option<&str>,
    from_marker: Option<&str>,
    bench: Option<&str>,
) -> Result<Value, RoadError> {
    if !is_craft(kind) {
        return Err(refused(format!("a draft is of a craft kind — one of {}, not {}", CRAFT_KINDS.join(", "), crate::py::repr_str(kind))));
    }
    let n = name.trim();
    if !crafts::name_ok(n) {
        return Err(refused("a draft's name is a short lowercase name: letters, digits, dashes, dots, underscores"));
    }
    let Some(obj) = body.as_object() else {
        return Err(refused("a draft's body is an object — the declaration as it stands"));
    };
    let mut body = obj.clone();
    body.entry("format").or_insert(json!(crafts::format_of(kind)));
    if matches!(kind, "template" | "binding" | "skill" | "graph") {
        body.entry("name").or_insert(json!(n));
    }
    let body_txt = serde_json::to_string(&Value::Object(body)).unwrap_or_else(|_| "{}".into());
    let did = draft_id.map(str::to_string).unwrap_or_else(|| format!("draft_{}", token_hex(6)));
    let scope = w.scope.clone();
    let tx = g.client_mut().transaction().await?;
    if let Some(d) = draft_id {
        let mine = tx
            .query_opt("SELECT 1 FROM spine_drafts WHERE draft_id = $1 AND scope = $2 AND person = $3", &[&d, &scope, &person])
            .await?;
        if mine.is_none() {
            return Err(refused("no such draft of yours here"));
        }
        tx.execute(
            "UPDATE spine_drafts SET kind = $1, name = $2, body = $3, words = $4, bench = coalesce($6, bench), updated_at = clock_timestamp() WHERE draft_id = $5",
            &[&kind, &n, &body_txt, &words, &d, &bench],   // sp8: a bench named moves it; unnamed keeps it
        )
        .await?;
    } else {
        tx.execute(
            "INSERT INTO spine_drafts (draft_id, scope, person, kind, name, body, words, from_marker, bench) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)",
            &[&did, &scope, &person, &kind, &n, &body_txt, &words, &from_marker, &bench],
        )
        .await?;
    }
    tx.commit().await?;
    draft(g.client(), &scope, person, &did)
        .await?
        .ok_or_else(|| refused("the draft did not land"))
}

/// `crafts.discard_draft`: the author lets a draft go — never recorded, nothing kept.
pub async fn discard_draft(g: &mut Ground, w: &World, person: &str, draft_id: &str) -> Result<bool, RoadError> {
    let n = g
        .client()
        .execute("DELETE FROM spine_drafts WHERE draft_id = $1 AND scope = $2 AND person = $3", &[&draft_id, &w.scope, &person])
        .await?;
    Ok(n > 0)
}

/// `crafts.cut_check`: what a cut of this draft would do, or why it refuses — `{draft,
/// shelf_name, verb, version, level, mode}`.
pub async fn cut_check<C: GenericClient>(c: &C, scope: &str, person: &str, draft_id: &str) -> Result<Value, RoadError> {
    let Some(d) = draft(c, scope, person, draft_id).await? else {
        return Err(refused("no such draft of yours here"));
    };
    let (kind, name, body) = (python_str(&d["kind"]), python_str(&d["name"]), d["body"].clone());
    let v = validate(&kind, &body);
    if v["ok"] != json!(true) {
        return Err(refused(format!("the draft does not read whole yet: {}", python_str(&v["reason"]))));
    }
    let universe = scope.split('/').next().unwrap_or(scope).to_string();
    let mode = crate::levels_live::row(c, &universe)
        .await?
        .and_then(|r| r["mode"].as_str().map(str::to_string))
        .unwrap_or_else(|| crate::levels::MODE_DEFAULT.to_string());
    let dem = cut_demand(&kind, &body, &mode);
    if dem["ok"] != json!(true) {
        return Err(refused(python_str(&dem["reason"])));
    }
    let sn = craft_name(&name, &kind).map_err(refused)?;
    if dem["gate"] == json!("experiment") {
        // Phase 8 sp4: an agent's cut OPENS the Experiment — checked now, in words
        let w = World { scope: scope.to_string(), ..World::from_env() };
        let x = crate::experiments_live::check_open(c, &w, person, draft_id).await?;
        return Ok(json!({"draft": d, "shelf_name": sn, "verb": "experiment", "version": x["current_version"].as_i64().unwrap_or(0) + 1,
                         "level": dem["level"], "mode": mode, "gate": "experiment", "room": x["room"], "cases": x["cases"],
                         "current_version": x["current_version"]}));
    }
    let (verb, version) = match services_live::get(c, scope, &sn).await? {
        None => ("register", 1),
        Some(row) if row["kind"] != json!(kind) => {
            return Err(refused(format!("{sn} is on the shelf as a {} — a name wears one kind", python_str(&row["kind"]))));
        }
        Some(row) if row["state"] == json!("retired") => {
            return Err(refused(format!("{sn} is retired — restore it first, then cut the next version")));
        }
        Some(row) if row["manifest_hash"] == json!(crafts::pin(&body)) => {
            return Err(refused(format!(
                "{sn} already stands on the shelf with these exact bytes (version {}) — nothing to cut",
                row["version"]
            )));
        }
        Some(row) => ("version", row["version"].as_i64().unwrap_or(1) + 1),
    };
    Ok(json!({"draft": d, "shelf_name": sn, "verb": verb, "version": version, "level": dem["level"], "mode": mode, "gate": "shelf"}))
}

/// `crafts.hold_cut`: the cut is the gate — held at the interlock as the kernel's own act at
/// the level the class demands; the human's yes settles it. 202 `{held, level, class, shelf_name, verb, version}`.
pub async fn hold_cut(g: &mut Ground, w: &World, person: &str, draft_id: &str, session: Option<&str>) -> Result<Value, RoadError> {
    let c = cut_check(g.client(), &w.scope, person, draft_id).await?;
    if c["gate"] == json!("experiment") {
        // Phase 8 sp4: the Experiment's opening is held instead (`experiment.open`, L2)
        let made = crate::experiments_live::hold_open(g, w, person, draft_id, session).await?;
        return Ok(json!({"held": made["held"], "level": made["level"], "class": CUT_CLASS, "shelf_name": c["shelf_name"],
                         "verb": "experiment", "version": c["version"], "gate": "experiment", "room": c["room"], "cases": c["cases"]}));
    }
    let (name, kind) = (python_str(&c["draft"]["name"]), python_str(&c["draft"]["kind"]));
    let level = python_str(&c["level"]);
    let held = crate::proof_live::hold_kernel_act(
        g,
        w,
        &cut_words(&name, &kind, &python_str(&c["verb"]), c["version"].as_i64().unwrap_or(1)),
        person,
        CUT_TOOL,
        json!({"draft_id": draft_id, "person": person}),
        &level,
        session,
        CUT_CLASS,
        false,
    )
    .await?;
    Ok(json!({"held": held, "level": level, "class": CUT_CLASS, "shelf_name": c["shelf_name"], "verb": c["verb"], "version": c["version"], "gate": "shelf"}))
}

/// `crafts.cut` inside `tx` (the settle arm): the draft lands on the shelf — registered, or
/// the next version — as the ladder's own fact with the person on the chain; the draft spent.
pub async fn cut_in(tx: &Transaction<'_>, w: &World, args: &Value, by: &str) -> Result<String, RoadError> {
    let (person, draft_id) = (python_str(&args["person"]), python_str(&args["draft_id"]));
    let c = cut_check(tx, &w.scope, &person, &draft_id).await?;
    let (kind, body, sn) = (python_str(&c["draft"]["kind"]), c["draft"]["body"].clone(), python_str(&c["shelf_name"]));
    let row = if c["verb"] == json!("register") {
        services_live::register_in(tx, w, &sn, &kind, &body, by, None, &[]).await?
    } else {
        services_live::version_in(tx, w, &sn, &body, by).await?
    };
    tx.execute("DELETE FROM spine_drafts WHERE draft_id = $1", &[&draft_id]).await?;
    // walk SPEC-SHELF-01: a cut craft is probed at the cut — its card reads healthy, never "never probed"
    let (ok, detail) = probe(tx, &w.scope, &row).await?;
    services_live::record_health_in(tx, w, &sn, ok, &detail, by).await?;
    let hash = python_str(&row["manifest_hash"]);
    Ok(format!(
        "the {sn} is on the shelf as version {} ({}) — pin {}…; the draft is spent",
        row["version"],
        python_str(&row["state"]),
        hash.get(7..19).unwrap_or("")
    ))
}
