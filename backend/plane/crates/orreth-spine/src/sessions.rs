// PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp3, the ask road · 2026-09-22
// Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp5, memory and the export · 2026-09-24
// Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch walk #13 cures: W51 a roll is a fact the feed carries · W52 the digest in the human's zone · THE GUIDE door · 2026-09-24
// Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp6, the bodies' seam: the crew card's LLM line for the bodies this kernel seats · 2026-09-24
//! The human's worldlines and the roster's reads — mirrors the session,
//! resident, crew and shelf views of `orreth_spine.glass` (P20 · canon 0004)
//! and the reads of `presence` · `placement` · `services` they stand on:
//! roll a session (archived means 'not active', never 'gone'), list them
//! newest first with their span and short version, load one whole; who
//! lives here; the Crew's cards — both sides (the asks served, the duties
//! run), the placement why-line, a body the ground refused shown greyed
//! (rule 7); the shelf, every service on its ladder. P7 sp5: a roll is an
//! EPISODE BOUNDARY — the archived session gets its digest (MEM-3) — and a
//! listed session without its short version gets it from the log.

use crate::ground::Ground;
use crate::placement::{honor, why_here, Ground as Here, Profile};
use crate::schema::has_table;
use crate::services::{ladder_step, KINDS};
use crate::world::{head, iso_opt, isoformat, json_strings, json_text, token_hex, RoadError};
use serde_json::{json, Value};
use std::time::SystemTime;

/// Every body runs these — kernel-required, visible in its card, never editable (P16).
pub const KERNEL_DUTIES: [&str; 4] = [
    "serve the invocation rail",
    "emit the journey at every hop",
    "think only on the meter",
    "wear the covenant policy it joined with",
];

/// Roll (P20): a fresh worldline for this human in this world.
pub async fn open_session(
    g: &mut Ground,
    scope: &str,
    person: &str,
    title: Option<&str>,
    opt_out: bool,
    archive: Option<&str>,
    zone: &str,
) -> Result<String, RoadError> {
    let sid = format!("ses_{}", token_hex(6));
    let state = if opt_out { "opt-out" } else { "in" };
    let e = crate::envelope::Mint {
        kind: "event".into(),
        r#type: crate::memory::SESSION_OPENED.into(),
        universe_id: scope.into(),
        scope_path: scope.into(),
        payload: crate::memory::session_payload(&sid, person, title, archive, state),
        correlation_id: Some(sid.clone()),
        authority_chain: Some(vec![person.to_string()]),
        aggregate: None,
        marker: None,
    }
    .mint()?;
    let raw = crate::envelope::encode(&e)?;
    let tx = g.client_mut().transaction().await?;
    tx.execute(
        "INSERT INTO spine_sessions (session_id, person, scope, title, state) VALUES ($1, $2, \
         $3, $4, $5)",
        &[&sid, &person, &scope, &title, &state],
    )
    .await?;
    crate::outbox::add_row(&tx, &raw, e["message_id"].as_str().unwrap_or_default()).await?; // W51
    tx.commit().await?;
    if let Some(a) = archive.filter(|a| !a.is_empty()) {
        // MEM-3, AFTER the new row stands: the archived span ends at this opening, so the digest
        // built here is the one a rebuild finds (the roll's race, found by test_digest)
        crate::digest::build(g, scope, a, person, zone).await?;
    }
    Ok(sid)
}

/// List (P20): this human's worldlines in this world, newest first — each
/// with its span, how many asks it holds, its last words, its short version.
pub async fn sessions_view(
    g: &mut Ground,
    scope: &str,
    person: &str,
    limit: i64,
    zone: &str,
) -> Result<Vec<Value>, RoadError> {
    crate::digest::build_missing(g, scope, person, limit, zone).await?; // P7 sp5 (MEM-3): the Digest is a projection
    let rows = g
        .client()
        .query(
            "SELECT s.session_id, s.title, s.opened_at, count(a.ask_id), max(a.asked_at), \
             coalesce(s.state, 'in'), (SELECT text FROM spine_asks WHERE session = s.session_id  \
             ORDER BY asked_at DESC LIMIT 1), (SELECT body FROM spine_digests d WHERE d.kind = \
             'session'  AND d.ref = s.session_id AND d.scope = s.scope AND d.valid_to IS NULL) \
             FROM spine_sessions s LEFT JOIN spine_asks a ON a.session = s.session_id WHERE \
             s.person = $1 AND s.scope = $2 GROUP BY s.session_id ORDER BY s.opened_at DESC \
             LIMIT $3",
            &[&person, &scope, &limit],
        )
        .await?;
    Ok(rows
        .iter()
        .map(|r| {
            let short = head(&r.get::<_, Option<String>>(7).unwrap_or_default(), 280);
            json!({
                "session_id": r.get::<_, String>(0), "title": r.get::<_, Option<String>>(1),
                "opened_at": isoformat(r.get::<_, SystemTime>(2)),
                "asks": r.get::<_, i64>(3), "last_at": iso_opt(r.get::<_, Option<SystemTime>>(4)),
                "state": r.get::<_, String>(5),
                "last_words": head(&r.get::<_, Option<String>>(6).unwrap_or_default(), 140),
                "short_version": if short.is_empty() { Value::Null } else { json!(short) },
            })
        })
        .collect())
}

/// Load (P20): the session and its asks in the order they were asked.
pub async fn session_view(
    g: &Ground,
    scope: &str,
    session_id: &str,
) -> Result<Option<Value>, RoadError> {
    let row = g
        .client()
        .query_opt(
            "SELECT session_id, person, title, opened_at FROM spine_sessions WHERE session_id = $1 \
             AND scope = $2",
            &[&session_id, &scope],
        )
        .await?;
    let Some(row) = row else {
        return Ok(None);
    };
    let asks = g
        .client()
        .query(
            "SELECT ask_id, text, status, reply, served_by, target, asked_at, replied_at, \
             time_window FROM spine_asks WHERE session = $1 ORDER BY asked_at",
            &[&session_id],
        )
        .await?;
    let asks: Vec<Value> = asks
        .iter()
        .map(|r| {
            json!({
                "ask_id": r.get::<_, String>(0), "text": r.get::<_, String>(1),
                "status": r.get::<_, String>(2), "reply": r.get::<_, Option<String>>(3),
                "served_by": r.get::<_, Option<String>>(4), "target": r.get::<_, Option<String>>(5),
                "asked_at": isoformat(r.get::<_, SystemTime>(6)),
                "replied_at": iso_opt(r.get::<_, Option<SystemTime>>(7)),
                "window": json_text(r.get::<_, Option<String>>(8).as_deref()),
            })
        })
        .collect();
    Ok(Some(json!({
        "session_id": row.get::<_, String>(0), "person": row.get::<_, String>(1),
        "title": row.get::<_, Option<String>>(2), "opened_at": isoformat(row.get::<_, SystemTime>(3)),
        "scope": scope, "asks": asks,
    })))
}

/// The chat's right edge: who lives here — name, self, lives.
pub async fn residents_view(g: &Ground, scope: &str) -> Result<Vec<Value>, RoadError> {
    let rows = g
        .client()
        .query(
            "SELECT DISTINCT ON (name) name, did, life, joined_at, kind, nature FROM spine_joins \
             WHERE scope = $1 ORDER BY name, join_id DESC",
            &[&scope],
        )
        .await?;
    Ok(rows
        .iter()
        .map(|r| {
            json!({
                "name": r.get::<_, String>(0), "did": r.get::<_, String>(1),
                "lives": r.get::<_, i32>(2), "joined_at": isoformat(r.get::<_, SystemTime>(3)),
                "kind": r.get::<_, String>(4),
                "nature": r.get::<_, Option<String>>(5).unwrap_or_default(),
            })
        })
        .collect())
}

/// What THIS ground is — `placement.ground_declares`: its cell, its metal,
/// the secret NAMES it can reach (names only; the values never leave the
/// environment).
pub fn ground_declares() -> Here {
    let dial = |name: &str| std::env::var(name).ok().filter(|v| !v.is_empty());
    let mut secrets: Vec<String> = std::env::vars()
        .filter(|(_, v)| !v.is_empty())
        .map(|(k, _)| k)
        .collect();
    secrets.sort();
    Here {
        cell: dial("SPINE_CELL").unwrap_or_else(|| "local".into()),
        metal: dial("SPINE_METAL").unwrap_or_else(|| "cpu".into()),
        secrets,
    }
}

/// The default profile a body without a placement wears.
pub fn default_profile() -> Profile {
    Profile {
        cell: "local".into(),
        affinity: Vec::new(),
        secrets_with: Vec::new(),
        metal: "any".into(),
    }
}

/// What the crew card shows — `placement.card`: the profile, each secret by
/// NAME with a reached mark, the honor verdict and the why-line.
pub fn card(prof: &Profile, ground: &Here) -> Value {
    let (ok, reasons) = honor(prof, ground);
    json!({
        "cell": prof.cell, "metal": prof.metal, "affinity": prof.affinity,
        "secrets": prof.secrets_with.iter().map(|s| json!({"name": s, "reached": ground.secrets.contains(s)})).collect::<Vec<_>>(),
        "ground": {"cell": ground.cell, "metal": ground.metal},
        "honored": ok, "reasons": reasons, "why": why_here(prof, ground),
    })
}

fn profile_of(text: Option<&str>) -> Profile {
    json_text(text)
        .and_then(|v| Profile::from_value(&v).ok())
        .unwrap_or_else(default_profile)
}

/// Every body that ever held a lease in this world — `did → alive`.
async fn alive_map(
    g: &Ground,
    scope: &str,
) -> Result<std::collections::HashMap<String, bool>, RoadError> {
    let rows = g
        .client()
        .query(
            "SELECT did, until > now() FROM spine_leases WHERE scope = $1 ORDER BY name",
            &[&scope],
        )
        .await?;
    Ok(rows.iter().map(|r| (r.get(0), r.get(1))).collect())
}

fn refused_card(r: &crate::asks::Refusal, nature: Option<&str>) -> Value {
    let prof = Profile::from_value(&r.placement).unwrap_or_else(|_| default_profile());
    let ground = Here {
        cell: r.ground["cell"].as_str().unwrap_or_default().into(),
        metal: r.ground["metal"].as_str().unwrap_or_default().into(),
        secrets: Vec::new(),
    };
    let mut c = card(&prof, &ground);
    c["honored"] = json!(false);
    c["reasons"] = json!(r.reasons);
    c["why"] = json!(format!("refused: {}", r.reasons.join("; ")));
    json!({
        "name": r.name, "kind": r.kind, "did": r.did, "lives": 0,
        "nature": nature.unwrap_or_default(), "joined_at": Value::Null,
        "policy_version": Value::Null, "alive": false, "refused": true,
        "refused_at": isoformat(r.refused_at), "marker": r.marker,
        "template": head(&r.template, 12), "capabilities": [], "placement": c,
        "side_a": {"asks_served": 0, "last_served": Value::Null},
        "side_b": {"kernel": [], "human": [], "role": []},
    })
}

/// The Crew workspace's door: one card per body in this world — who it is,
/// what it wears, what it declared, and BOTH SIDES (canon 0004).
pub async fn crew_view(
    g: &Ground,
    scope: &str,
    templates: Option<&std::collections::HashMap<String, Value>>,
) -> Result<Vec<Value>, RoadError> {
    let rows = g
        .client()
        .query(
            "SELECT DISTINCT ON (name) name, kind, did, life, joined_at, policy_version, \
             template_hash, capabilities, placement, nature FROM spine_joins WHERE scope = $1 \
             ORDER BY name, join_id DESC",
            &[&scope],
        )
        .await?;
    let alive = alive_map(g, scope).await?;
    let here = ground_declares();
    let mut refused = crate::asks::refusals(g, scope).await?;
    let mut cards = Vec::new();
    for r in &rows {
        let name: String = r.get(0);
        let did: String = r.get(2);
        let joined: SystemTime = r.get(4);
        let nature: Option<String> = r.get(9);
        let served = g
            .client()
            .query_one(
                "SELECT count(*), max(replied_at) FROM spine_asks WHERE served_by = $1 AND scope \
                 = $2 AND status <> 'received'",
                &[&did, &scope],
            )
            .await?;
        let prof = profile_of(r.get::<_, Option<String>>(8).as_deref());
        if let Some(rf) = refused.remove(&name) {
            if rf.refused_at > joined {
                cards.push(refused_card(&rf, nature.as_deref()));
                continue;
            }
        }
        // P6.5 sp3 (walk #12, W43): which LLM this body thinks with, and why — when this
        // kernel seats the body (its template is known); else null, as the reference's
        let mind = match templates.and_then(|t| t.get(&name)) {
            Some(t) => crate::stable_live::mind_line(g, scope, &name, &did, Some(t)).await?,
            None => None,
        };
        cards.push(json!({
            "mind": mind,
            "name": name, "kind": r.get::<_, String>(1), "did": did, "lives": r.get::<_, i32>(3),
            "nature": nature.unwrap_or_default(), "joined_at": isoformat(joined),
            "policy_version": r.get::<_, String>(5), "alive": alive.get(&did).copied(),
            "template": head(&r.get::<_, String>(6), 12),
            "capabilities": json_text(r.get::<_, Option<String>>(7).as_deref()).unwrap_or(json!([])),
            "placement": card(&prof, &here),
            "side_a": {"asks_served": served.get::<_, i64>(0), "last_served": iso_opt(served.get::<_, Option<SystemTime>>(1))},
            "side_b": {"kernel": KERNEL_DUTIES.iter().map(|d| json!({"duty": d, "editable": false})).collect::<Vec<_>>(), "human": [], "role": []},
        }));
    }
    let mut rest: Vec<_> = refused.into_values().collect();
    rest.sort_by(|a, b| a.name.cmp(&b.name));
    for r in rest {
        cards.push(refused_card(&r, None));
    }
    Ok(cards)
}

/// The shelf's read — `services.listing`: every service in this world with
/// its ladder state, the placement why-line, its secrets by NAME, its last
/// health; nothing when the Python spine never made the table.
pub async fn services_listing(
    g: &Ground,
    scope: &str,
    kind: Option<&str>,
) -> Result<Vec<Value>, RoadError> {
    if !has_table(g, "spine_services").await? {
        return Ok(Vec::new());
    }
    let here = ground_declares();
    let rows = g
        .client()
        .query(
            "SELECT name, scope, kind, did, manifest, manifest_hash, version, placement, \
             secrets_with, state, by_did, since, registered_at, last_ok, last_detail, \
             last_checked_at, marker, root_marker FROM spine_services WHERE scope = $1 AND \
             ($2::text IS NULL OR kind = $2) ORDER BY kind, name",
            &[&scope, &kind],
        )
        .await?;
    Ok(rows
        .iter()
        .map(|r| {
            let prof_v = json_text(r.get::<_, Option<String>>(7).as_deref()).unwrap_or(json!({}));
            let prof = Profile::from_value(&prof_v).unwrap_or_else(|_| default_profile());
            let c = card(&prof, &here);
            let state: String = r.get(9);
            let checked: Option<SystemTime> = r.get(15);
            json!({
                "name": r.get::<_, String>(0), "kind": r.get::<_, String>(2), "did": r.get::<_, String>(3),
                "manifest": json_text(r.get::<_, Option<String>>(4).as_deref()),
                "manifest_hash": r.get::<_, String>(5), "version": r.get::<_, i32>(6),
                "placement": c.clone(), "secrets_with": json_strings(r.get::<_, Option<String>>(8).as_deref()),
                "state": state, "by": r.get::<_, String>(10),
                "since": isoformat(r.get::<_, SystemTime>(11)),
                "registered_at": isoformat(r.get::<_, SystemTime>(12)),
                "last_health": checked.map(|at| json!({"ok": r.get::<_, Option<bool>>(13), "detail": r.get::<_, Option<String>>(14), "at": isoformat(at)})),
                "marker": r.get::<_, Option<String>>(16), "root_marker": r.get::<_, Option<String>>(17),
                "secrets": c["secrets"].clone(),
                "retirable": ladder_step(Some(&state), "retire").ok,
                "restorable": ladder_step(Some(&state), "restore").ok,
            })
        })
        .collect())
}

/// The shelf door's whole body: the services, the kinds, this ground.
pub async fn services_door(
    g: &Ground,
    scope: &str,
    kind: Option<&str>,
) -> Result<Value, RoadError> {
    let here = ground_declares();
    Ok(json!({
        "services": services_listing(g, scope, kind).await?,
        "kinds": KINDS,
        "ground": {"cell": here.cell, "metal": here.metal},
    }))
}
