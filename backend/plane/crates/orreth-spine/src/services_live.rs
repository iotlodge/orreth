// PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp6, the bodies' seam · 2026-09-24
//! The services registry on the ground — `orreth_spine.services` ported
//! (P6.5 sp1 · 0009 §3 "one ladder, two keepers" · 0018 services as
//! identities · 0059 the env-secrets law): ONE registry for tool · mcp ·
//! store · source · mind, each an IDENTITY (`did:orreth:service:…`, its seed
//! under `<services home>/<name>/seed` — the same self every life, rule 1),
//! a MANIFEST PIN, a PLACEMENT honored at register (a refusal records
//! nothing), secrets by NAME only. One LADDER (`crate::services::ladder_step`
//! is the law): register → version → healthy | unhealthy → retire ⇄ restore,
//! every step a FACT through the outbox with the chain and a marker under
//! the world's one shelf root ("the kernel keeps the shelf"). Health is the
//! kind's honest probe: a mind — the canary through the gateway; an mcp —
//! initialize + tools/list, its tools synced; a store or source — its locator
//! reachable by NAME; a built-in tool — the body's door describes it, so
//! this kernel says "not probed here" and records nothing (the tool door
//! moves in sp8). W49: a service healthy again withdraws the keeper's waiting
//! proposal to retire it, in words.
//!
//! The writes are `_in(tx)` — inside a transaction someone else owns — so the
//! kernel's settle of a held act (`asks::settle_kernel_act`) lands the act and
//! its record together; the `&mut Ground` faces wrap one transaction each.

use crate::envelope::{self, Mint};
use crate::ground::Ground;
use crate::hash::content_hash;
use crate::markers_live;
use crate::placement::{honor, profile, Profile};
use crate::py::{python_str, repr_str, truthy};
use crate::services::{ladder_step, KINDS};
use crate::sessions::ground_declares;
use crate::world::{isoformat, json_strings, json_text, refused, token_hex, RoadError, World};
use serde_json::{json, Value};
use std::path::PathBuf;
use std::time::SystemTime;
use tokio_postgres::{GenericClient, Transaction};

pub const KERNEL: &str = "the kernel";
pub const REGISTERED: &str = "orreth.service.registered.v1";
pub const VERSIONED: &str = "orreth.service.versioned.v1";
pub const HEALTH: &str = "orreth.service.health.v1";
pub const RETIRED: &str = "orreth.service.retired.v1";
pub const RESTORED: &str = "orreth.service.restored.v1";
pub const RETIRE_TOOL: &str = "service.retire";
pub const RETIRE_CLASS: &str = "consequential";
pub const RETIRE_LEVEL: &str = "L2";
pub const GROUND_LOCATOR: &str = "SPINE_PG";
pub const SHELF_REF: &str = "the shelf";
pub const SERVICES_HOME_DIAL: &str = "SPINE_SERVICES_HOME";

fn fact_of(verb: &str) -> &'static str {
    match verb {
        "register" => REGISTERED,
        "version" => VERSIONED,
        "healthy" | "unhealthy" => HEALTH,
        "retire" => RETIRED,
        _ => RESTORED,
    }
}

/// Where the services' seeds live: `SPINE_SERVICES_HOME`, else `ORRETH_HOME/services`,
/// else `~/.orreth/services` (beside the agents' — `services.services_home`).
pub fn services_home() -> PathBuf {
    if let Ok(h) = std::env::var(SERVICES_HOME_DIAL) {
        if !h.is_empty() {
            return PathBuf::from(h);
        }
    }
    let base = std::env::var("ORRETH_HOME")
        .ok()
        .filter(|h| !h.is_empty())
        .map(PathBuf::from)
        .unwrap_or_else(|| {
            PathBuf::from(std::env::var("HOME").unwrap_or_else(|_| ".".into())).join(".orreth")
        });
    base.join("services")
}

/// A service's self — `Identity.load(name, home, kind="service")`: the same DID every life.
pub fn service_did(name: &str) -> Result<String, RoadError> {
    let me = crate::kernel_self::KernelSelf::load_as(&services_home().join(name), name, "service")
        .map_err(|e| refused(format!("the {name} service's seed could not be read: {e}")))?;
    Ok(me.did())
}

const COLS: &str = "name, scope, kind, did, manifest, manifest_hash, version, placement, secrets_with, \
                    state, by_did, since, registered_at, last_ok, last_detail, last_checked_at, marker, root_marker";

/// `services._row`: the record as the reference shapes it.
pub fn row_of(r: &tokio_postgres::Row) -> Value {
    let checked: Option<SystemTime> = r.get(15);
    json!({
        "name": r.get::<_, String>(0), "kind": r.get::<_, String>(2), "did": r.get::<_, String>(3),
        "manifest": json_text(r.get::<_, Option<String>>(4).as_deref()).unwrap_or(json!({})),
        "manifest_hash": r.get::<_, String>(5), "version": r.get::<_, i32>(6),
        "placement": json_text(r.get::<_, Option<String>>(7).as_deref()).unwrap_or(json!({})),
        "secrets_with": json_strings(r.get::<_, Option<String>>(8).as_deref()),
        "state": r.get::<_, String>(9), "by": r.get::<_, String>(10),
        "since": isoformat(r.get::<_, SystemTime>(11)),
        "registered_at": isoformat(r.get::<_, SystemTime>(12)),
        "last_health": checked.map(|at| json!({"ok": r.get::<_, Option<bool>>(13), "detail": r.get::<_, Option<String>>(14), "at": isoformat(at)})),
        "marker": r.get::<_, Option<String>>(16), "root_marker": r.get::<_, Option<String>>(17),
    })
}

/// One service by name, or none.
pub async fn get<C: GenericClient>(
    c: &C,
    scope: &str,
    name: &str,
) -> Result<Option<Value>, RoadError> {
    let row = c
        .query_opt(
            &format!("SELECT {COLS} FROM spine_services WHERE name = $1 AND scope = $2"),
            &[&name, &scope],
        )
        .await?;
    Ok(row.as_ref().map(row_of))
}

/// Every service in this world (of a kind), the reference's rows — no card.
pub async fn rows<C: GenericClient>(
    c: &C,
    scope: &str,
    kind: Option<&str>,
) -> Result<Vec<Value>, RoadError> {
    let rows = c
        .query(
            &format!(
                "SELECT {COLS} FROM spine_services WHERE scope = $1 AND ($2::text IS NULL OR kind = $2) \
                 ORDER BY kind, name"
            ),
            &[&scope, &kind],
        )
        .await?;
    Ok(rows.iter().map(row_of).collect())
}

/// The mind service by its stall NAME — what a dollar meter row carries.
pub async fn stall_did<C: GenericClient>(
    c: &C,
    scope: &str,
    stall: &str,
) -> Result<Option<String>, RoadError> {
    Ok(c.query_opt(
        "SELECT did FROM spine_services WHERE scope = $1 AND kind = 'mind' AND name = $2",
        &[&scope, &stall],
    )
    .await?
    .map(|r| r.get(0)))
}

/// The mind service whose manifest names this model.
pub async fn mind_did<C: GenericClient>(
    c: &C,
    scope: &str,
    model: &str,
) -> Result<Option<String>, RoadError> {
    Ok(c
        .query_opt(
            "SELECT did FROM spine_services WHERE scope = $1 AND kind = 'mind' AND manifest::json->>'model' \
             = $2 ORDER BY registered_at LIMIT 1",
            &[&scope, &model],
        )
        .await?
        .map(|r| r.get(0)))
}

/// ONE origin per world for the shelf — "the kernel keeps the shelf"; minted once.
pub async fn shelf_root(tx: &Transaction<'_>, scope: &str) -> Result<String, RoadError> {
    let row = tx
        .query_opt(
            "SELECT marker_id FROM spine_markers WHERE scope = $1 AND parent IS NULL AND kind = \
             'observation' AND ref = $2 AND by_did = $3 ORDER BY at LIMIT 1",
            &[&scope, &SHELF_REF, &KERNEL],
        )
        .await?;
    if let Some(r) = row {
        return Ok(r.get(0));
    }
    let mid = markers_live::new_id();
    markers_live::insert(
        tx,
        &mid,
        "observation",
        None,
        SHELF_REF,
        KERNEL,
        Some("the kernel keeps the shelf — every service it governs, on one ladder"),
        scope,
    )
    .await?;
    Ok(mid)
}

/// What a fact hangs under and who cut it.
#[derive(Debug, Clone, Default)]
pub struct FactWhere<'a> {
    pub parent_marker: Option<&'a str>,
    pub ask: Option<&'a str>,
    pub confirmed_by: Option<&'a str>,
}

/// `services._fact`: the marker (an ACTION under the ask that released it,
/// else an OBSERVATION under the service's register, itself under the
/// shelf root) and the fact through the outbox — inside `tx`. Returns the marker id.
pub async fn fact_in(
    tx: &Transaction<'_>,
    w: &World,
    verb: &str,
    svc: &Value,
    by: &str,
    extra: Value,
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
        None => match svc["root_marker"].as_str().filter(|s| !s.is_empty()) {
            Some(r) => r.to_string(),
            None => shelf_root(tx, &w.scope).await?,
        },
    };
    let mut chain: Vec<String> = if by == KERNEL {
        vec![KERNEL.into()]
    } else {
        vec![by.into(), KERNEL.into()]
    };
    if let Some(c) = at.confirmed_by.filter(|c| *c != by) {
        chain = vec![by.into(), c.into(), KERNEL.into()];
    }
    let mut payload = json!({"ref": svc["did"], "hash": svc["manifest_hash"], "name": svc["name"],
                             "kind": svc["kind"], "version": svc["version"], "state": svc["state"], "by": by});
    if let Some(o) = extra.as_object() {
        for (k, v) in o {
            payload[k] = v.clone();
        }
    }
    let r#ref = at
        .ask
        .map(str::to_string)
        .unwrap_or_else(|| python_str(&svc["did"]));
    let mut note = format!(
        "{} ({}) {verb}: {}",
        python_str(&svc["name"]),
        python_str(&svc["kind"]),
        python_str(&svc["state"])
    );
    if let Some(d) = extra.get("detail").filter(|d| truthy(d)) {
        note.push_str(&format!(" — {}", python_str(d)));
    }
    markers_live::insert(
        tx,
        &mid,
        kind,
        Some(&parent),
        &r#ref,
        by,
        Some(&note),
        &w.scope,
    )
    .await?;
    let e = Mint {
        kind: "event".into(),
        r#type: fact_of(verb).into(),
        universe_id: w.scope.clone(),
        scope_path: w.scope.clone(),
        payload,
        correlation_id: Some(r#ref),
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

fn validate(name: &str, kind: &str, manifest: &Value) -> Result<(), RoadError> {
    let n = name.trim();
    let plain = n.replace(['-', '_', '.'], "");
    if n.is_empty() || !plain.chars().all(|c| c.is_ascii_alphanumeric()) || n != n.to_lowercase() {
        return Err(refused(
            "a service name is a short lowercase name: letters, digits, dashes, dots",
        ));
    }
    if !KINDS.contains(&kind) {
        return Err(refused(format!(
            "a service kind is one of {} — not {}",
            KINDS.join(", "),
            repr_str(kind)
        )));
    }
    if !manifest.as_object().is_some_and(|m| !m.is_empty()) {
        return Err(refused(
            "a manifest is a non-empty object: what the service declares (a tool's schema, a mind's \
             route and model, an mcp server's tools, a store's or source's locator by NAME)",
        ));
    }
    Ok(())
}

fn refuse_step(name: &str, state: Option<&str>, verb: &str) -> Result<&'static str, RoadError> {
    let st = ladder_step(state, verb);
    if !st.ok {
        return Err(refused(format!(
            "the {name} service is {}",
            st.reason.unwrap_or_default()
        )));
    }
    Ok(st.to.unwrap_or("registered"))
}

/// The placement a service registers under: the raw profile plus its secrets by NAME.
fn placement_of(raw: Option<&Value>, secrets_with: &[String]) -> Result<Profile, RoadError> {
    let mut raw = raw.cloned().unwrap_or(json!({}));
    if !raw.is_object() {
        raw = json!({});
    }
    let mut names: Vec<String> = json_strings(raw["secrets_with"].as_array().map(|_| "").and(None));
    if let Some(a) = raw["secrets_with"].as_array() {
        names = a.iter().map(python_str).collect();
    }
    names.extend(secrets_with.iter().cloned());
    names.sort();
    names.dedup();
    raw["secrets_with"] = json!(names);
    profile(&json!({"placement": raw})).map_err(|e| refused(e.to_string()))
}

/// `services.register` inside `tx`: the first rung — placement (with its
/// secrets by NAME) honored FIRST, a refusal records nothing; the same
/// manifest again is the same self; a changed manifest is refused by name.
#[allow(clippy::too_many_arguments)]
pub async fn register_in(
    tx: &Transaction<'_>,
    w: &World,
    name: &str,
    kind: &str,
    manifest: &Value,
    by: &str,
    placement: Option<&Value>,
    secrets_with: &[String],
) -> Result<Value, RoadError> {
    validate(name, kind, manifest)?;
    let prof = placement_of(placement, secrets_with)?;
    let here = ground_declares();
    let (ok, reasons) = honor(&prof, &here);
    if !ok {
        return Err(refused(format!(
            "{name} is refused here: {}",
            reasons.join("; ")
        )));
    }
    let h = content_hash(manifest);
    if let Some(row) = get(tx, &w.scope, name).await? {
        let state = row["state"].as_str().unwrap_or_default();
        if state != "retired"
            && row["kind"].as_str() == Some(kind)
            && row["manifest_hash"].as_str() == Some(h.as_str())
        {
            return Ok(row); // the same self, every life (rule 1)
        }
        if state != "retired" && row["kind"].as_str() != Some(kind) {
            return Err(refused(format!(
                "the {name} service is already registered as a {} — a name wears one kind; {kind} \
                 needs its own name",
                python_str(&row["kind"])
            )));
        }
        refuse_step(name, Some(state), "register")?;
    }
    let did = service_did(name)?;
    let prof_v = prof.to_value();
    let svc = json!({"name": name, "kind": kind, "did": did, "manifest": manifest, "manifest_hash": h,
                     "version": 1, "placement": prof_v, "secrets_with": prof.secrets_with, "state": "registered"});
    let mid = fact_in(
        tx,
        w,
        "register",
        &svc,
        by,
        json!({"placement": prof_v, "secrets_with": prof.secrets_with}),
        FactWhere::default(),
    )
    .await?;
    let manifest_txt = String::from_utf8(crate::canonical::canonical(manifest)).unwrap_or_default();
    let prof_txt = String::from_utf8(crate::canonical::canonical(&prof_v)).unwrap_or_default();
    let secrets_txt = serde_json::to_string(&prof.secrets_with).unwrap_or_else(|_| "[]".into());
    tx.execute(
        "INSERT INTO spine_services (name, scope, kind, did, manifest, manifest_hash, version, placement, \
         secrets_with, state, by_did, since, marker, root_marker) VALUES ($1, $2, $3, $4, $5, $6, 1, $7, $8, \
         'registered', $9, clock_timestamp(), $10, $10)",
        &[&name, &w.scope, &kind, &did, &manifest_txt, &h, &prof_txt, &secrets_txt, &by, &mid],
    )
    .await?;
    tx.execute(
        "INSERT INTO spine_service_versions (name, scope, version, manifest, manifest_hash, by_did) VALUES \
         ($1, $2, 1, $3, $4, $5)",
        &[&name, &w.scope, &manifest_txt, &h, &by],
    )
    .await?;
    get(tx, &w.scope, name)
        .await?
        .ok_or_else(|| refused("the register did not land"))
}

/// `services.version` inside `tx`: a changed manifest re-pins the service.
pub async fn version_in(
    tx: &Transaction<'_>,
    w: &World,
    name: &str,
    manifest: &Value,
    by: &str,
) -> Result<Value, RoadError> {
    let Some(row) = get(tx, &w.scope, name).await? else {
        return Err(refused(format!(
            "no service named {} is registered here — register it first",
            repr_str(name)
        )));
    };
    let kind = python_str(&row["kind"]);
    validate(name, &kind, manifest)?;
    refuse_step(name, row["state"].as_str(), "version")?;
    let h = content_hash(manifest);
    if row["manifest_hash"].as_str() == Some(h.as_str()) {
        return Err(refused(format!(
            "the {name} service's manifest is unchanged — nothing to version"
        )));
    }
    let n = row["version"].as_i64().unwrap_or(1) + 1;
    let mut svc = row.clone();
    svc["manifest"] = manifest.clone();
    svc["manifest_hash"] = json!(h);
    svc["version"] = json!(n);
    svc["state"] = json!("versioned");
    let mid = fact_in(
        tx,
        w,
        "version",
        &svc,
        by,
        json!({"previous_hash": row["manifest_hash"]}),
        FactWhere::default(),
    )
    .await?;
    let manifest_txt = String::from_utf8(crate::canonical::canonical(manifest)).unwrap_or_default();
    let n32 = n as i32;
    tx.execute(
        "UPDATE spine_services SET manifest = $1, manifest_hash = $2, version = $3, state = 'versioned', \
         since = clock_timestamp(), marker = $4 WHERE name = $5 AND scope = $6",
        &[&manifest_txt, &h, &n32, &mid, &name, &w.scope],
    )
    .await?;
    tx.execute(
        "INSERT INTO spine_service_versions (name, scope, version, manifest, manifest_hash, by_did) VALUES \
         ($1, $2, $3, $4, $5, $6)",
        &[&name, &w.scope, &n32, &manifest_txt, &h, &by],
    )
    .await?;
    get(tx, &w.scope, name)
        .await?
        .ok_or_else(|| refused("the version did not land"))
}

/// `services.record_health` inside `tx`: the health row and the fact; the
/// ladder steps to healthy or unhealthy (or stays, `ok` null). Returns the
/// verdict as the reference words it.
pub async fn record_health_in(
    tx: &Transaction<'_>,
    w: &World,
    name: &str,
    ok: Option<bool>,
    detail: &str,
    by: &str,
) -> Result<Value, RoadError> {
    let Some(row) = get(tx, &w.scope, name).await? else {
        return Err(refused(format!(
            "no service named {} is registered here — the shelf lists them",
            repr_str(name)
        )));
    };
    let state_now = python_str(&row["state"]);
    refuse_step(name, Some(&state_now), "healthy")?;
    let verb = match ok {
        Some(true) => Some("healthy"),
        Some(false) => Some("unhealthy"),
        None => None,
    };
    let state = match verb {
        Some(v) => ladder_step(Some(&state_now), v)
            .to
            .unwrap_or("registered")
            .to_string(),
        None => state_now.clone(),
    };
    let mut svc = row.clone();
    svc["state"] = json!(state);
    fact_in(
        tx,
        w,
        verb.unwrap_or("healthy"),
        &svc,
        by,
        json!({"ok": ok, "detail": detail}),
        FactWhere::default(),
    )
    .await?;
    let did = python_str(&row["did"]);
    tx.execute(
        "INSERT INTO spine_service_health (name, scope, did, ok, detail) VALUES ($1, $2, $3, $4, $5)",
        &[&name, &w.scope, &did, &ok, &detail],
    )
    .await?;
    tx.execute(
        "UPDATE spine_services SET state = $1, since = CASE WHEN state = $1 THEN since ELSE clock_timestamp() \
         END, last_ok = $2, last_detail = $3, last_checked_at = clock_timestamp() WHERE name = $4 AND scope = $5",
        &[&state, &ok, &detail, &name, &w.scope],
    )
    .await?;
    Ok(
        json!({"name": name, "kind": row["kind"], "did": did, "ok": ok, "detail": detail, "state": state}),
    )
}

/// `services.record_health` on a ground of its own: one transaction, then
/// W49 — a service healthy again withdraws the keeper's waiting proposal.
pub async fn record_health(
    g: &mut Ground,
    w: &World,
    name: &str,
    ok: Option<bool>,
    detail: &str,
    by: &str,
) -> Result<Value, RoadError> {
    let tx = g.client_mut().transaction().await?;
    let out = record_health_in(&tx, w, name, ok, detail, by).await?;
    tx.commit().await?;
    if ok == Some(true) {
        withdraw_stale_proposals(g, w, name).await?;
    }
    Ok(out)
}

/// W49: a keeper proposed retiring this service for being unhealthy; it is
/// healthy again — the kernel withdraws the waiting proposal with the reason
/// in words (a recorded cancel, never a deletion).
pub async fn withdraw_stale_proposals(
    g: &mut Ground,
    w: &World,
    name: &str,
) -> Result<Vec<String>, RoadError> {
    let rows = g
        .client()
        .query(
            "SELECT ask_id FROM spine_asks WHERE scope = $1 AND served_by = $2 AND status = \
             'awaiting-confirm' AND held IS NOT NULL AND held::json->>'tool' = $3 AND \
             held::json->'args'->>'name' = $4 AND person LIKE 'did:orreth:agent:%'",
            &[&w.scope, &KERNEL, &RETIRE_TOOL, &name],
        )
        .await?;
    let ids: Vec<String> = rows.iter().map(|r| r.get(0)).collect();
    let mut out = Vec::new();
    for aid in ids {
        let reason = format!(
            "withdrawn — the {name} service answered its check and is healthy again; nothing to retire"
        );
        match crate::asks::settle_kernel_act(g, w, &aid, false, KERNEL, None, Some(&reason)).await {
            Ok(_) => out.push(aid),
            Err(RoadError::NotConfirmed { .. }) => {}
            Err(e) => return Err(e),
        }
    }
    Ok(out)
}

/// `services.retire` inside `tx`: dormancy, never deletion — the fact hangs
/// under the held ask's marker when the interlock released it.
pub async fn retire_in(
    tx: &Transaction<'_>,
    w: &World,
    name: &str,
    by: &str,
    at: FactWhere<'_>,
) -> Result<Value, RoadError> {
    let row = get(tx, &w.scope, name).await?;
    refuse_step(
        name,
        row.as_ref().and_then(|r| r["state"].as_str()),
        "retire",
    )?;
    let row = row.unwrap_or(json!({}));
    let mut svc = row.clone();
    svc["state"] = json!("retired");
    let mid = fact_in(tx, w, "retire", &svc, by, json!({"from": row["state"]}), at).await?;
    tx.execute(
        "UPDATE spine_services SET state = 'retired', since = clock_timestamp(), marker = $1 WHERE name = $2 \
         AND scope = $3",
        &[&mid, &name, &w.scope],
    )
    .await?;
    get(tx, &w.scope, name)
        .await?
        .ok_or_else(|| refused("the retire did not land"))
}

/// `services.restore` inside `tx`: a NEW fact — the service stands registered again.
pub async fn restore_in(
    tx: &Transaction<'_>,
    w: &World,
    name: &str,
    by: &str,
) -> Result<Value, RoadError> {
    let row = get(tx, &w.scope, name).await?;
    refuse_step(
        name,
        row.as_ref().and_then(|r| r["state"].as_str()),
        "restore",
    )?;
    let row = row.unwrap_or(json!({}));
    let mut svc = row.clone();
    svc["state"] = json!("registered");
    let mid = fact_in(tx, w, "restore", &svc, by, json!({}), FactWhere::default()).await?;
    tx.execute(
        "UPDATE spine_services SET state = 'registered', since = clock_timestamp(), marker = $1 WHERE name = \
         $2 AND scope = $3",
        &[&mid, &name, &w.scope],
    )
    .await?;
    get(tx, &w.scope, name)
        .await?
        .ok_or_else(|| refused("the restore did not land"))
}

/// The `&mut Ground` faces: one transaction each.
#[allow(clippy::too_many_arguments)]
pub async fn register(
    g: &mut Ground,
    w: &World,
    name: &str,
    kind: &str,
    manifest: &Value,
    by: &str,
    placement: Option<&Value>,
    secrets_with: &[String],
) -> Result<Value, RoadError> {
    let tx = g.client_mut().transaction().await?;
    let out = register_in(&tx, w, name, kind, manifest, by, placement, secrets_with).await?;
    tx.commit().await?;
    Ok(out)
}

pub async fn version(
    g: &mut Ground,
    w: &World,
    name: &str,
    manifest: &Value,
    by: &str,
) -> Result<Value, RoadError> {
    let tx = g.client_mut().transaction().await?;
    let out = version_in(&tx, w, name, manifest, by).await?;
    tx.commit().await?;
    Ok(out)
}

pub async fn restore(g: &mut Ground, w: &World, name: &str, by: &str) -> Result<Value, RoadError> {
    let tx = g.client_mut().transaction().await?;
    let out = restore_in(&tx, w, name, by).await?;
    tx.commit().await?;
    Ok(out)
}

/// `services.hold_retire`: retiring is consequential (L2) — the kernel holds
/// it at the interlock as its own act; cancel is the default.
pub async fn hold_retire(
    g: &mut Ground,
    w: &World,
    name: &str,
    person: &str,
    session: Option<&str>,
) -> Result<String, RoadError> {
    let row = get(g.client(), &w.scope, name).await?;
    refuse_step(
        name,
        row.as_ref().and_then(|r| r["state"].as_str()),
        "retire",
    )?;
    let kind = row.map(|r| python_str(&r["kind"])).unwrap_or_default();
    crate::proof_live::hold_kernel_act(
        g,
        w,
        &format!("retiring the {name} {kind}"),
        person,
        RETIRE_TOOL,
        json!({"name": name}),
        RETIRE_LEVEL,
        session,
        RETIRE_CLASS,
        false,
    )
    .await
}

/// The kind's honest probe — `services._probe`. `Ok(None, words)` = not probed here.
pub async fn probe(
    g: &mut Ground,
    w: &World,
    gw: Option<&crate::gateway::Gateway>,
    row: &Value,
    by: &str,
) -> Result<(Option<bool>, String), RoadError> {
    let kind = python_str(&row["kind"]);
    let m = row["manifest"].clone();
    let name = python_str(&row["name"]);
    if kind == "tool" && truthy(&m["server"]) {
        return Ok(crate::mcp_live::probe_tool(g, w, row).await);
    }
    if kind == "tool" {
        return Ok((
            None,
            "not probed by this kernel — a built-in tool's door is the body's; the Python kernel probes \
             it at boot (the tool door moves in sp8)"
                .into(),
        ));
    }
    if kind == "mind" {
        let Some(gw) = gw else {
            return Ok((
                None,
                "not probed — no gateway was handed to the check".into(),
            ));
        };
        let who = if by.starts_with("did:") {
            by.to_string()
        } else {
            python_str(&row["did"])
        };
        let route = python_str(&m["route"]);
        return Ok(
            match gw.ping(g, &w.scope, &who, &name, &name, &route).await {
                Ok(said) => {
                    let low = said.trim_start().to_lowercase();
                    if low.starts_with("i cannot think") || low.starts_with("i am out of fuel") {
                        (
                            Some(false),
                            format!(
                                "the mind did not answer: {}",
                                crate::world::head(&said, 160)
                            ),
                        )
                    } else {
                        (
                            Some(true),
                            format!(
                                "the gateway answered a one-token ping through the meter ({})",
                                if route.is_empty() {
                                    python_str(&m["model"])
                                } else {
                                    route
                                }
                            ),
                        )
                    }
                }
                Err(words) => (
                    Some(false),
                    format!(
                        "the mind did not answer: {}",
                        crate::world::head(&words, 160)
                    ),
                ),
            },
        );
    }
    if kind == "mcp" {
        return Ok(crate::mcp_live::probe(g, w, row, by).await);
    }
    let loc = python_str(&m["locator"]);
    if loc.is_empty() {
        return Ok((Some(false), "the manifest names no locator".into()));
    }
    if loc != GROUND_LOCATOR && std::env::var(&loc).ok().filter(|v| !v.is_empty()).is_none() {
        return Ok((
            Some(false),
            format!("the locator {loc} is not reachable by name here"),
        ));
    }
    if loc == GROUND_LOCATOR {
        g.client().execute("SELECT 1", &[]).await?;
        if let Some(table) = m["table"].as_str() {
            let exists: bool = g
                .client()
                .query_one("SELECT to_regclass($1) IS NOT NULL", &[&table])
                .await?
                .get(0);
            if !exists {
                return Ok((
                    Some(false),
                    format!("the ground answers but {table} is not on it yet"),
                ));
            }
            return Ok((
                Some(true),
                format!("the ground answers and {table} stands on it"),
            ));
        }
        return Ok((Some(true), "the ground answers".into()));
    }
    Ok((
        Some(true),
        format!("the locator {loc} is reachable by name"),
    ))
}

/// `services.check`: the probe, recorded — one by name.
pub async fn check(
    g: &mut Ground,
    w: &World,
    gw: Option<&crate::gateway::Gateway>,
    name: &str,
    by: &str,
) -> Result<Value, RoadError> {
    let Some(row) = get(g.client(), &w.scope, name).await? else {
        return Err(refused(format!(
            "no service named {} is registered here — the shelf lists them",
            repr_str(name)
        )));
    };
    refuse_step(name, row["state"].as_str(), "healthy")?;
    let (ok, detail) = probe(g, w, gw, &row, by).await?;
    if ok.is_none() && row["kind"] == json!("tool") {
        // a built-in tool: nothing recorded — the last verdict (the Python kernel's) stands
        return Ok(
            json!({"name": name, "kind": row["kind"], "did": row["did"], "ok": Value::Null, "detail": detail, "state": row["state"]}),
        );
    }
    record_health(g, w, name, ok, &detail, by).await
}

/// `services.check_all`: every standing service (of a kind) probed.
pub async fn check_all(
    g: &mut Ground,
    w: &World,
    gw: Option<&crate::gateway::Gateway>,
    kind: Option<&str>,
    by: &str,
) -> Result<Vec<Value>, RoadError> {
    let mut out = Vec::new();
    for s in rows(g.client(), &w.scope, kind).await? {
        if s["state"] == json!("retired") {
            continue;
        }
        out.push(check(g, w, gw, &python_str(&s["name"]), by).await?);
    }
    Ok(out)
}

/// The body's DID by name (`tools._did_of_body`).
pub async fn did_of_body<C: GenericClient>(
    c: &C,
    scope: &str,
    name: &str,
) -> Result<Option<String>, RoadError> {
    Ok(c
        .query_opt(
            "SELECT did FROM spine_joins WHERE scope = $1 AND lower(name) = lower($2) ORDER BY join_id DESC LIMIT 1",
            &[&scope, &name],
        )
        .await?
        .map(|r| r.get(0)))
}

/// A fresh id for a marker-less row (`token_hex`), kept here for the callers that mint.
pub fn new_token(n: usize) -> String {
    token_hex(n)
}
