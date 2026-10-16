// PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch Phase 8 THE STUDIO sp8, THE BENCH (canon 0011 §2): the ground half · 2026-10-13
//! THE BENCH on the ground — `orreth_spine.benches` ported (canon 0011 §2, JB's lock 2026-10-13),
//! schema 10: `spine_benches` (one effort, one row: name · step · body · hold · state) and the
//! drafts' `bench` column. The doors are ROUTINE (L1) like a draft's save and discard: opening,
//! moving the step, keeping the wizard's state. CLOSING lets the effort go — its drafts discarded,
//! its open experiment declined through the experiments' own word — routine too; what reached the
//! shelf stays. Opening and closing are facts on the feed; a step moved is read, not announced
//! (the glass re-reads the row on a clock — W133's law).

use crate::benches::{name_ok, step_ok, BENCH_CLOSED, BENCH_OPENED, STEPS};
use crate::ground::Ground;
use crate::py::python_str;
use crate::world::{isoformat, refused, token_hex, RoadError, World};
use serde_json::{json, Value};
use std::time::SystemTime;
use tokio_postgres::{GenericClient, Transaction};

const KERNEL: &str = "the kernel";
const COLS: &str = "bench_id, person, name, words, step, body, hold, state, at, updated_at, closed_at";

fn row_of(r: &tokio_postgres::Row) -> Value {
    json!({"bench_id": r.get::<_, String>(0), "person": r.get::<_, String>(1), "name": r.get::<_, String>(2),
           "words": r.get::<_, Option<String>>(3), "step": r.get::<_, String>(4),
           "body": serde_json::from_str::<Value>(&r.get::<_, String>(5)).unwrap_or(json!({})),
           "hold": r.get::<_, Option<String>>(6), "state": r.get::<_, String>(7),
           "at": isoformat(r.get::<_, SystemTime>(8)), "updated_at": isoformat(r.get::<_, SystemTime>(9)),
           "closed_at": r.get::<_, Option<SystemTime>>(10).map(isoformat)})
}

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

/// `benches.get`: the OPEN bench of this name under the person; a closed one if no open one stands (the newest).
pub async fn get<C: GenericClient>(c: &C, scope: &str, person: &str, name: &str) -> Result<Option<Value>, RoadError> {
    Ok(c
        .query_opt(
            &format!("SELECT {COLS} FROM spine_benches WHERE scope = $1 AND person = $2 AND name = $3 ORDER BY (state = 'open') DESC, updated_at DESC LIMIT 1"),
            &[&scope, &person, &name],
        )
        .await?
        .as_ref()
        .map(row_of))
}

/// `benches.listing`: this person's benches, the open ones first, newest first — and ONLY this person's (AG-9).
pub async fn listing<C: GenericClient>(c: &C, scope: &str, person: &str, state: Option<&str>) -> Result<Vec<Value>, RoadError> {
    Ok(c
        .query(
            &format!("SELECT {COLS} FROM spine_benches WHERE scope = $1 AND person = $2 AND ($3::text IS NULL OR state = $3) ORDER BY (state = 'open') DESC, updated_at DESC LIMIT 200"),
            &[&scope, &person, &state],
        )
        .await?
        .iter()
        .map(row_of)
        .collect())
}

/// `benches.open_bench`: routine (L1) — a bench opens under the person, or the open one of that
/// name is handed back (one open bench per name per person: an effort is one place). A fact.
pub async fn open_bench(g: &mut Ground, w: &World, person: &str, name: &str, words: Option<&str>) -> Result<Value, RoadError> {
    let n = name.trim().to_ascii_lowercase();
    if !name_ok(&n) {
        return Err(refused("a bench is named for its agent: a short lowercase name — letters, digits, dashes, underscores"));
    }
    if let Some(have) = get(g.client(), &w.scope, person, &n).await? {
        if have["state"] == json!("open") {
            return Ok(have);
        }
    }
    let bid = format!("bench_{}", token_hex(6));
    let tx = g.client_mut().transaction().await?;
    tx.execute("INSERT INTO spine_benches (bench_id, scope, person, name, words) VALUES ($1, $2, $3, $4, $5)", &[&bid, &w.scope, &person, &n, &words])
        .await?;
    fact(&tx, w, BENCH_OPENED, &bid, json!({"name": n, "person": person, "words": words.unwrap_or("")}), vec![person.to_string(), KERNEL.into()]).await?;
    tx.commit().await?;
    get(g.client(), &w.scope, person, &n).await?.ok_or_else(|| refused("the bench did not open"))
}

/// `benches.move`: routine (L1) — the bench keeps its place: the step, the wizard's state, the ask
/// it holds (`Some("")` clears the hold). No fact: the glass reads the row.
pub async fn move_bench(
    g: &mut Ground,
    w: &World,
    person: &str,
    name: &str,
    step: Option<&str>,
    body: Option<&Value>,
    hold: Option<&str>,
    words: Option<&str>,
) -> Result<Value, RoadError> {
    let Some(b) = get(g.client(), &w.scope, person, name).await? else {
        return Err(refused(format!("no open bench named {} under your seat", crate::py::repr_str(name))));
    };
    if b["state"] != json!("open") {
        return Err(refused(format!("no open bench named {} under your seat", crate::py::repr_str(name))));
    }
    if let Some(s) = step {
        if !step_ok(s) {
            return Err(refused(format!("a bench's step is one of {}, not {}", STEPS.join(", "), crate::py::repr_str(s))));
        }
    }
    if let Some(bd) = body {
        if !bd.is_object() {
            return Err(refused("a bench's body is an object — the wizard's state as it stands"));
        }
    }
    if step.is_none() && body.is_none() && hold.is_none() && words.is_none() {
        return Ok(b);
    }
    let bid = python_str(&b["bench_id"]);
    let body_txt = body.map(|v| serde_json::to_string(v).unwrap_or_else(|_| "{}".into()));
    let hold_v: Option<Option<String>> = hold.map(|h| if h.is_empty() { None } else { Some(h.to_string()) });
    let words_v: Option<Option<String>> = words.map(|x| if x.is_empty() { None } else { Some(x.to_string()) });
    g.client()
        .execute(
            "UPDATE spine_benches SET step = coalesce($1, step), body = coalesce($2, body), \
             hold = CASE WHEN $3 THEN $4 ELSE hold END, words = CASE WHEN $5 THEN $6 ELSE words END, \
             updated_at = clock_timestamp() WHERE bench_id = $7",
            &[&step, &body_txt, &hold_v.is_some(), &hold_v.clone().flatten(), &words_v.is_some(), &words_v.clone().flatten(), &bid],
        )
        .await?;
    get(g.client(), &w.scope, person, name).await?.ok_or_else(|| refused("the bench did not move"))
}

/// `benches.whole`: the bench with everything that stands under its name — its drafts, its
/// experiments since it opened, its seat on the shelf (where the agent's life stands, if promoted).
pub async fn whole<C: GenericClient>(c: &C, scope: &str, person: &str, bench: &Value) -> Result<Value, RoadError> {
    let name = python_str(&bench["name"]);
    let drafts = crate::crafts_live::drafts_on(c, scope, person, &name).await?;
    let since = python_str(&bench["at"]);
    let xs: Vec<Value> = crate::experiments_live::listing(c, scope, Some(&name), None)
        .await?
        .into_iter()
        .filter(|x| python_str(&x["opened_at"]) >= since)
        .map(|x| json!({"experiment_id": x["experiment_id"], "state": x["state"], "leaning": x["leaning"], "room": x["room"],
                         "opened_at": x["opened_at"], "proposed_at": x["proposed_at"], "settled_at": x["settled_at"]}))
        .collect();
    let seat = crate::experiments_live::seat_of(c, scope, &name).await?;
    let mut out = bench.clone();
    out["drafts"] = json!(drafts);
    out["experiments"] = json!(xs);
    out["seat"] = seat.unwrap_or(Value::Null);
    Ok(out)
}

/// `benches.close`: routine (L1), like discard and decline — the effort is let go: its drafts
/// discarded, its open experiment declined (the experiments' own word), the bench closed. What
/// reached the shelf stays. A fact.
pub async fn close(g: &mut Ground, w: &World, person: &str, name: &str, reason: Option<&str>) -> Result<Value, RoadError> {
    let Some(b) = get(g.client(), &w.scope, person, name).await? else {
        return Err(refused(format!("no open bench named {} under your seat", crate::py::repr_str(name))));
    };
    if b["state"] != json!("open") {
        return Err(refused(format!("no open bench named {} under your seat", crate::py::repr_str(name))));
    }
    let full = whole(g.client(), &w.scope, person, &b).await?;
    let open_x = full["experiments"].as_array().cloned().unwrap_or_default();
    if open_x.iter().any(|x| matches!(python_str(&x["state"]).as_str(), "running" | "proposed"))
        && !crate::desk_live::governs(g.client(), &w.scope, person).await?
    {
        return Err(RoadError::Forbidden(format!("the {name} bench holds an open experiment — declining it is a governing seat's act; yours reads and writes")));
    }
    let mut declined: Vec<String> = vec![];
    for x in open_x {
        let st = python_str(&x["state"]);
        if st == "running" || st == "proposed" {
            let xid = python_str(&x["experiment_id"]);
            let why = reason.map(str::to_string).unwrap_or_else(|| format!("the {name} bench was let go"));
            crate::experiments_live::decline(g, w, person, &xid, Some(&why)).await?;
            declined.push(xid);
        }
    }
    let bid = python_str(&b["bench_id"]);
    let tx = g.client_mut().transaction().await?;
    let discarded = tx
        .execute("DELETE FROM spine_drafts WHERE scope = $1 AND person = $2 AND bench = $3", &[&w.scope, &person, &name])
        .await?;
    tx.execute(
        "UPDATE spine_benches SET state = 'closed', hold = NULL, closed_at = clock_timestamp(), updated_at = clock_timestamp() WHERE bench_id = $1",
        &[&bid],
    )
    .await?;
    fact(
        &tx,
        w,
        BENCH_CLOSED,
        &bid,
        json!({"name": name, "person": person, "discarded": discarded, "declined": declined, "reason": reason.unwrap_or("")}),
        vec![person.to_string(), KERNEL.into()],
    )
    .await?;
    tx.commit().await?;
    let words = format!(
        "the {name} bench is let go — {discarded} draft{} discarded{}; what reached the shelf stays",
        if discarded == 1 { "" } else { "s" },
        if declined.is_empty() { String::new() } else { format!(", {} experiment{} declined", declined.len(), if declined.len() == 1 { "" } else { "s" }) }
    );
    Ok(json!({"bench": get(g.client(), &w.scope, person, name).await?, "discarded": discarded, "declined": declined, "words": words}))
}

// ---- THE STUDIO sp10 — ONE WORD TO WORK (canon 0011 §5, JB's lock 2026-10-13: ONE Yes for the chain; built 2026-10-14) ----

/// `benches.work_check`: what "put <name> to work" would do, read off the bench and the shelf — or
/// why it refuses, in words. The chain's drafts are validated here, as a cut would.
pub async fn work_check<C: GenericClient>(c: &C, w: &World, person: &str, name: &str, answering: Option<&str>) -> Result<Value, RoadError> {
    let Some(b) = get(c, &w.scope, person, name).await? else {
        return Err(refused(format!("no open bench named {} under your seat", crate::py::repr_str(name))));
    };
    if b["state"] != json!("open") {
        return Err(refused(format!("no open bench named {} under your seat", crate::py::repr_str(name))));
    }
    let wh = whole(c, &w.scope, person, &b).await?;
    if let Some(x) = wh["experiments"].as_array().and_then(|xs| xs.iter().find(|x| x["state"] == json!("running") || x["state"] == json!("proposed"))) {
        return Err(refused(format!(
            "an experiment on {name} is already {} ({}) — its card is the next step; decline it to start over",
            python_str(&x["state"]),
            python_str(&x["experiment_id"])
        )));
    }
    // W148 (sp11's proof, 2026-10-16): one chain, ONE hold — filed twice, the door (and the maker) doubled the
    // hold; while the bench's ask still awaits the human, the pending one is the answer (`answering`: the
    // settle reads the chain for the hold it is answering)
    if let Some(hold) = b["hold"].as_str().filter(|h| Some(*h) != answering) {
        let st = c
            .query_opt("SELECT status FROM spine_asks WHERE ask_id = $1 AND scope = $2", &[&hold, &w.scope])
            .await?
            .map(|r| r.get::<_, String>(0));
        if st.as_deref() == Some("awaiting-confirm") {
            return Err(refused(format!(
                "put {name} to work is already held ({hold}) — the human's Yes is pending; answer that hold, or cancel it, before filing again"
            )));
        }
    }
    let mut by_kind: std::collections::HashMap<String, Value> = std::collections::HashMap::new();
    for d in wh["drafts"].as_array().cloned().unwrap_or_default() {
        by_kind.entry(python_str(&d["kind"])).or_insert(d); // newest first
    }
    let mut ins = serde_json::Map::new();
    let mut drafts = serde_json::Map::new();
    // W149: the prompts and skills the GRAPH names — read off the bench's graph draft, or the graph standing on
    // the shelf when the bench has no graph draft — each a cut before the graph, or a line, or a refusal
    let all_drafts = wh["drafts"].as_array().cloned().unwrap_or_default();
    let gbody: Value = match by_kind.get("graph") {
        Some(d) if d["body"].is_object() => d["body"].clone(),
        _ => match crate::services_live::get(c, &w.scope, &crate::crafts::craft_name(&format!("{name}.v0"), "graph").map_err(refused)?).await? {
            Some(r) if r["kind"] == json!("graph") => r["manifest"].clone(),
            _ => Value::Null,
        },
    };
    let mut refs: Vec<Value> = Vec::new();
    for node in gbody["nodes"].as_array().cloned().unwrap_or_default() {
        for rk in ["prompt", "skill"] {
            let rn = node[rk].as_str().unwrap_or("").trim().to_string();
            if !rn.is_empty() && !refs.iter().any(|r| r["kind"] == json!(rk) && r["name"] == json!(rn)) {
                refs.push(json!({"kind": rk, "name": rn}));
            }
        }
    }
    for r in refs.iter_mut() {
        let (rk, rn) = (python_str(&r["kind"]), python_str(&r["name"]));
        let d = all_drafts.iter().find(|x| x["kind"] == json!(rk) && x["name"] == json!(rn)).cloned(); // newest first
        let row = crate::services_live::get(c, &w.scope, &crate::crafts::craft_name(&rn, &rk).map_err(refused)?).await?;
        if let Some(x) = &row {
            if x["kind"] != json!(rk) {
                return Err(refused(format!("{} is on the shelf as a {} — a name wears one kind", python_str(&x["name"]), python_str(&x["kind"]))));
            }
            if x["state"] == json!("retired") {
                return Err(refused(format!("{} is retired — restore it first, then put {name} to work", python_str(&x["name"]))));
            }
        }
        if let Some(d) = &d {
            let v = crate::crafts::validate(&rk, &d["body"]);
            if v["ok"] != json!(true) {
                return Err(refused(format!("the {rn} {rk} draft does not read whole yet: {}", python_str(&v["reason"]))));
            }
            drafts.insert(format!("{rk}:{rn}"), d["draft_id"].clone());
        }
        let same = match (&d, &row) {
            (Some(d), Some(x)) => x["manifest_hash"] == json!(crate::crafts::pin(&d["body"])),
            _ => false,
        };
        r["draft"] = json!(d.is_some());
        r["same"] = json!(same);
        r["version"] = json!(row.as_ref().and_then(|x| x["version"].as_i64()));
    }
    for kind in crate::benches::WORK_ORDER {
        let cname = if kind == "graph" { format!("{name}.v0") } else { name.to_string() };
        let row = crate::services_live::get(c, &w.scope, &crate::crafts::craft_name(&cname, kind).map_err(refused)?).await?;
        let d = by_kind.get(kind);
        if let Some(d) = d {
            if d["name"] != json!(cname) {
                return Err(refused(format!(
                    "the {kind} draft on the {name} bench is named {} — a bench's crafts wear the agent's name ({cname})",
                    crate::py::repr_str(&python_str(&d["name"]))
                )));
            }
        }
        if let Some(r) = &row {
            if r["kind"] != json!(kind) {
                return Err(refused(format!("{} is on the shelf as a {} — a name wears one kind", python_str(&r["name"]), python_str(&r["kind"]))));
            }
            if r["state"] == json!("retired") {
                return Err(refused(format!("{} is retired — restore it first, then put {name} to work", python_str(&r["name"]))));
            }
        }
        if let Some(d) = d {
            let v = crate::crafts::validate(kind, &d["body"]);
            if v["ok"] != json!(true) {
                return Err(refused(format!("the {} draft does not read whole yet: {}", crate::benches::plain_words(name, kind), python_str(&v["reason"]))));
            }
            drafts.insert(kind.into(), d["draft_id"].clone());
        }
        let same = match (d, &row) {
            (Some(d), Some(r)) => r["manifest_hash"] == json!(crate::crafts::pin(&d["body"])),
            _ => false,
        };
        ins.insert(kind.into(), json!({"draft": d.is_some(), "same": same, "version": row.as_ref().and_then(|r| r["version"].as_i64())}));
    }
    let plan = crate::benches::plan_work(name, &ins["graph"], &ins["golden"], &ins["template"], &Value::Array(refs));
    if plan["ok"] != json!(true) {
        return Err(refused(plan["reason"].as_str().unwrap_or("nothing to put to work")));
    }
    let t = &by_kind["template"]["body"];
    if !t.is_object() || t["kind"] != json!("agent") || t["name"] != json!(name) {
        return Err(refused(format!("the {name} template is not an agent of that name — the wizard writes it so; fix the draft")));
    }
    if t["graph"] != json!(format!("{name}.v0")) {
        return Err(refused(format!(
            "the {name} template names graph {} — a bench's agent wears its own graph, {name}.v0",
            crate::py::repr_str(&python_str(&t["graph"]))
        )));
    }
    Ok(json!({"bench": b, "plan": plan, "drafts": drafts}))
}

/// `benches.hold_work`: ONE hold for the chain (L2) — the card's lines are the held act's words;
/// the bench keeps the ask it holds at the step CUT. 202 `{held, level, class, lines, cuts}`.
pub async fn hold_work(g: &mut Ground, w: &World, person: &str, name: &str, session: Option<&str>) -> Result<Value, RoadError> {
    let c = work_check(g.client(), w, person, name, None).await?;
    let held = crate::proof_live::hold_kernel_act(
        g,
        w,
        &python_str(&c["plan"]["text"]),
        person,
        crate::benches::WORK_TOOL,
        json!({"bench": name, "person": person}),
        crate::benches::WORK_LEVEL,
        session,
        crate::benches::WORK_CLASS,
        false,
    )
    .await?;
    move_bench(g, w, person, name, Some("cut"), None, Some(&held), None).await?;
    Ok(json!({"held": held, "level": crate::benches::WORK_LEVEL, "class": crate::benches::WORK_CLASS, "lines": c["plan"]["lines"], "cuts": c["plan"]["cuts"]}))
}

/// `benches.work_in` inside `tx` (the settle arm): the cuts in order — each its own fact on the
/// shelf — then the Experiment opened on the agent's own; the bench at THE CARD, its hold cleared.
pub async fn work_in(tx: &Transaction<'_>, w: &World, args: &Value, by: &str, ask: Option<&str>, marker: Option<&str>) -> Result<String, RoadError> {
    let person = if args["person"].as_str().map(|s| !s.is_empty()).unwrap_or(false) { python_str(&args["person"]) } else { by.to_string() };
    let name = python_str(&args["bench"]);
    let c = work_check(tx, w, &person, &name, ask).await?;
    let mut said: Vec<String> = Vec::new();
    for kind in c["plan"]["cuts"].as_array().cloned().unwrap_or_default() {
        let kind = python_str(&kind);
        let draft_id = c["drafts"][&kind].clone();
        if kind == "template" {
            said.push(crate::experiments_live::open_in(tx, w, &json!({"draft_id": draft_id, "person": person}), by, ask, marker).await?);
        } else {
            let words = crate::crafts_live::cut_in(tx, w, &json!({"draft_id": draft_id, "person": person}), by).await?;
            said.push(words.split(" (").next().unwrap_or(&words).to_string());
        }
    }
    let skipped: Vec<String> = c["plan"]["lines"].as_array().cloned().unwrap_or_default().iter().map(python_str).filter(|l| l.contains("stands")).collect();
    tx.execute(
        "UPDATE spine_benches SET step = 'card', hold = NULL, updated_at = clock_timestamp() WHERE bench_id = $1",
        &[&python_str(&c["bench"]["bench_id"])],
    )
    .await?;
    Ok(format!("{name} is put to work — {}{}", said.join("; "), if skipped.is_empty() { String::new() } else { format!(" ({})", skipped.join("; ")) }))
}

