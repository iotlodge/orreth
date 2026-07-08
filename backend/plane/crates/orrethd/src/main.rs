//! orrethd — one thin recursive node (0000 §0): tier = a profile, not code.
//!
//! v0 surface: the gateway over HTTP. Ingress verifies (signature, revocation, scope,
//! high-water clock) and stores — bodies to the object store, pointers to the node.
//! Egress is the retrieval router with the uniform refusal (budget-miss ≡ authz-miss;
//! the reason never leaks). The plane verifies, never signs — cognition lives elsewhere.
//!
//!   orrethd --profile profiles/demo-field.json [--store-dir ./bodies] [--port 4400]

use axum::extract::{Path as UrlPath, State};
use axum::http::StatusCode;
use axum::response::IntoResponse;
use axum::routing::{get, post};
use axum::{Json, Router};
use orreth_node::{dur_days, Node, Universe, WriteError};
use orreth_store::{BodyStore, StoreError};
use serde_json::{json, Value};
use std::collections::{BTreeMap, BTreeSet};
use std::sync::{Arc, Mutex};

mod farm;
mod model;
mod pg;

struct App {
    universe: Mutex<Universe>,
    /// the plane authorizes and meters; cognition executes (0016 §6)
    model: Mutex<model::ModelPlane>,
    /// the Tool Farm (0018): this floor's toolshed — services as identities, leased
    farm: Mutex<farm::Farm>,
    /// PUSH up / PULL down (0000 §1): a child knows its parent; a parent never reaches in.
    parent: Option<String>,
    horizon_days: f64,
    /// Write-through persistence: the daemon may die; the records don't.
    pg: Option<pg::PgRecords>,
    /// Human requests: asks + HITL. Unsigned intents (inputs, not memories);
    /// cognition executes them with authority and the results become signed memories.
    requests: Mutex<Vec<Value>>,
    /// Presence flows UP (0000 §1): children heartbeat their subtree summaries here.
    /// A parent learns the world below without ever reaching into it.
    children: Mutex<BTreeMap<String, Value>>,
    /// Per-process display counters (beats heard, refusals, upward beats) surfaced as
    /// resident vitals in the Console. Unsigned, reset on restart, never read by governance.
    vitals: Mutex<BTreeMap<String, i64>>,
    /// Organ DIDs pinned at join (the R1 door, closed): becky mints the token, the
    /// plane verifies its chain against the pinned root — authority beats archaeology.
    organs: Mutex<BTreeMap<String, String>>,
}

fn bump(app: &App, key: &str) {
    *app.vitals.lock().unwrap().entry(key.to_string()).or_insert(0) += 1;
}

/// "%Y-%m-%dT%H:%M:%SZ" from the system clock (civil-from-days; no chrono).
fn now_iso() -> String {
    let secs = std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .unwrap()
        .as_secs() as i64;
    let (days, rem) = (secs.div_euclid(86_400), secs.rem_euclid(86_400));
    let z = days + 719_468;
    let era = z.div_euclid(146_097);
    let doe = z - era * 146_097;
    let yoe = (doe - doe / 1460 + doe / 36_524 - doe / 146_096) / 365;
    let doy = doe - (365 * yoe + yoe / 4 - yoe / 100);
    let mp = (5 * doy + 2) / 153;
    let (d, m) = (doy - (153 * mp + 2) / 5 + 1, if mp < 10 { mp + 3 } else { mp - 9 });
    let y = yoe + era * 400 + if m <= 2 { 1 } else { 0 };
    format!(
        "{:04}-{:02}-{:02}T{:02}:{:02}:{:02}Z",
        y, m, d, rem / 3_600, (rem / 60) % 60, rem % 60
    )
}

fn arg(name: &str) -> Option<String> {
    let args: Vec<String> = std::env::args().collect();
    args.iter().position(|a| a == name).and_then(|i| args.get(i + 1).cloned())
}

#[tokio::main]
async fn main() {
    let profile_path = arg("--profile").expect("orrethd --profile <tier-profile.json>");
    let profile: Value =
        serde_json::from_str(&std::fs::read_to_string(&profile_path).expect("profile file"))
            .expect("profile json");
    let scope = profile["scope"].as_str().expect("profile.scope").to_string();
    let horizon = profile["retrieval"]["horizon"].as_str().unwrap_or("forever");
    let port: u16 = arg("--port").and_then(|p| p.parse().ok()).unwrap_or(4400);

    // PULL down at boot (0000 §1): the child fetches its parent's floors — never pushed in.
    // Inherited floors go FIRST: they dominate classification; a child tightens, never loosens.
    let parent = arg("--parent").or_else(|| {
        profile["parent_endpoint"].as_str()
            .filter(|p| p.starts_with("http"))
            .map(str::to_string)
    });
    let mut floors: Vec<Value> = Vec::new();
    if let Some(parent_url) = &parent {
        // in a composed topology the parent may still be waking — be patient at the door
        let mut pulled_ok = false;
        for attempt in 1..=10 {
            match ureq::get(&format!("{parent_url}/standards")).call() {
                Ok(resp) => {
                    let pulled: Value = resp.into_json().expect("parent standards json");
                    let inherited = pulled["floors"].as_array().cloned().unwrap_or_default();
                    println!("orrethd · pulled {} inherited floor(s) from {parent_url}", inherited.len());
                    floors.extend(inherited);
                    pulled_ok = true;
                    break;
                }
                Err(_) => std::thread::sleep(std::time::Duration::from_millis(500 * attempt)),
            }
        }
        if !pulled_ok {
            // fail-closed continue (0007): last-known would apply if we had it; at first
            // boot there is nothing known — start with own floors, loudly
            eprintln!("orrethd · parent unreachable after retries; starting with local floors only");
        }
    }
    floors.extend(profile.get("floors").and_then(Value::as_array).cloned().unwrap_or_default());

    let node = Node {
        scope: scope.clone(),
        horizon_days: dur_days(horizon),
        parent: None,
        records: BTreeMap::new(),
        high_water: None,
        floors,
    };
    // trust-root pinning: token chains must start at the profile's root. did:key roots
    // embed their key; did:web roots need --root-pub until the resolver joins.
    let trust_root = profile["trust_root"]["root"].as_str().map(str::to_string);
    let mut identities = BTreeMap::new();
    if let (Some(root), Some(pub_key)) = (&trust_root, arg("--root-pub")) {
        identities.insert(root.clone(), pub_key);
    }
    let mut universe = Universe {
        nodes: vec![node],
        identities,
        revoked: BTreeSet::new(),
        purged: BTreeSet::new(),
        now: now_iso(),
        body_store: arg("--store-dir").map(|d| BodyStore::local(std::path::Path::new(&d))),
        trust_root,
        runs: BTreeMap::new(),
    };

    // boot-restore: records return, and the high-water mark with them — the clock's
    // monotonicity survives the daemon (0004 §1). Loaded rows are already the stored
    // form (verified at original ingress); re-verification happens on every read anyway.
    // the sync postgres client drives its own runtime — keep it off the async threads
    let pg_store = tokio::task::block_in_place(|| {
        arg("--pg").map(|conn| pg::PgRecords::connect(&conn).expect("postgres"))
    });
    if let Some(store) = &pg_store {
        let restored = tokio::task::block_in_place(|| store.load(&scope)).expect("boot restore");
        let n = restored.len();
        for rec in restored {
            let id = rec["id"].as_str().unwrap().to_string();
            let occurred = rec["occurred_at"].as_str().unwrap();
            let lived = rec.get("provenance_class").and_then(Value::as_str).unwrap_or("lived") == "lived";
            let node = &mut universe.nodes[0];
            if lived
                && node.high_water.as_deref()
                    .map_or(true, |hw| orreth_node::ts_seconds(occurred) > orreth_node::ts_seconds(hw))
            {
                node.high_water = Some(occurred.to_string());
            }
            node.records.insert(id, rec);
        }
        println!("orrethd · restored {n} record(s) from postgres · high_water={:?}",
                 universe.nodes[0].high_water);
    }

    let mut model_plane = model::ModelPlane::from_file(
        &arg("--models").unwrap_or_else(|| "profiles/model-registry.json".into()));
    // the meter survives the daemon (0019 §4): usage history is memory, not vapor
    if let Some(store) = &pg_store {
        let meters = tokio::task::block_in_place(|| store.load_meters(&scope))
            .unwrap_or_default();
        if !meters.is_empty() {
            println!("orrethd · restored {} meter entr(ies) from postgres", meters.len());
        }
        model_plane.meter_log = meters;
    }
    let app = Arc::new(App {
        universe: Mutex::new(universe),
        model: Mutex::new(model_plane),
        farm: Mutex::new(farm::Farm::new()),
        parent,
        horizon_days: dur_days(horizon),
        pg: pg_store,
        requests: Mutex::new(Vec::new()),
        children: Mutex::new(BTreeMap::new()),
        vitals: Mutex::new(BTreeMap::new()),
        organs: Mutex::new(BTreeMap::new()),
    });

    // the upward presence beat: every 5s tell the parent what this subtree holds,
    // children riding along — so the apex assembles the whole world from heartbeats
    if let Some(parent_url) = app.parent.clone() {
        let beat = app.clone();
        std::thread::spawn(move || loop {
            let s = summary(&beat);
            if ureq::post(&format!("{parent_url}/hello")).send_json(&s).is_ok() {
                bump(&beat, "beats_up"); // count successful upward beats
            }
            std::thread::sleep(std::time::Duration::from_secs(5));
        });
    }

    let router = Router::new()
        .route("/health", get(health))
        .route("/records", post(ingress))
        .route("/records/:id/body", get(body))
        .route("/retrieve", post(egress))
        .route("/standards", get(standards))
        .route("/window", get(window))
        .route("/model/authorize", post(model_authorize))
        .route("/model/meter", post(model_meter))
        .route("/model/usage", get(model_usage))
        .route("/model/state", post(model_state))
        .route("/farm", get(farm_list))
        .route("/farm/plant", post(farm_plant))
        .route("/farm/state", post(farm_state))
        .route("/farm/hello", post(farm_hello))
        .route("/farm/meter", post(farm_meter))
        .route("/stable", get(stable_list))
        .route("/stable/saddle", post(stable_saddle))
        .route("/stable/state", post(stable_state))
        .route("/stable/hello", post(stable_hello))
        .route("/runs", post(runs_ingress))
        .route("/presence", get(presence))
        .route("/rollup", get(rollup))
        .route("/hello", post(hello))
        .route("/topology", get(topology))
        .route("/requests", get(requests_list))
        .route("/requests", post(requests_submit))
        .route("/requests/resolve", post(requests_resolve))
        .route("/organs", get(organs_list))
        .route("/organs/pin", post(organs_pin))
        .with_state(app);

    let bind = arg("--bind").unwrap_or_else(|| "127.0.0.1".to_string()); // 0.0.0.0 in containers
    let listener = tokio::net::TcpListener::bind((bind.as_str(), port)).await.unwrap();
    println!("orrethd · scope={scope} · tier_label={} · listening on {bind}:{port}",
             profile["tier_label"].as_str().unwrap_or("?"));
    axum::serve(listener, router).await.unwrap();
}

/// The daemon carries its own glass — but the pane is a CLIENT of the retrieval
/// contract (0008): every render is a tokened query; there is no privileged path.
async fn window() -> axum::response::Html<&'static str> {
    axum::response::Html(include_str!("window.html"))
}

async fn health(State(app): State<Arc<App>>) -> Json<Value> {
    let u = app.universe.lock().unwrap();
    Json(json!({
        "scope": u.nodes[0].scope,
        "records": u.nodes[0].records.len(),
        "high_water": u.nodes[0].high_water,
        "bodies": u.body_store.is_some(),
    }))
}

async fn ingress(State(app): State<Arc<App>>, Json(record): Json<Value>) -> impl IntoResponse {
    // Universe ops call the store's own runtime — keep them off the async workers
    tokio::task::spawn_blocking(move || {
        let mut u = app.universe.lock().unwrap();
        u.now = now_iso();
        match u.write(0, &record) {
            Ok(id) => {
                // write-through: persist the STORED form (body_ref, keep_class, received_at)
                if let Some(store) = &app.pg {
                    let node_scope = u.nodes[0].scope.clone();
                    if let Err(e) = store.save(&node_scope, &u.nodes[0].records[&id]) {
                        eprintln!("orrethd · postgres write-through failed for {id}: {e}");
                    }
                }
                (StatusCode::CREATED, Json(json!({"id": id})))
            }
            Err(WriteError::ClockViolation) => (
                StatusCode::CONFLICT,
                Json(json!({"error": "occurred_at below scope high-water — lived memory cannot be backdated"})),
            ),
            Err(WriteError::AuthzError) => (
                StatusCode::FORBIDDEN,
                Json(json!({"error": "record rejected — Sourced or nothing"})),
            ),
        }
    })
    .await
    .unwrap()
}

async fn body(State(app): State<Arc<App>>, UrlPath(id): UrlPath<String>) -> impl IntoResponse {
    tokio::task::spawn_blocking(move || {
        let u = app.universe.lock().unwrap();
        let Some(rec) = u.nodes[0].records.get(&id) else {
            return (StatusCode::NOT_FOUND, Vec::new());
        };
        match u.get_body(rec) {
            Ok(bytes) => (StatusCode::OK, bytes),
            Err(StoreError::IntegrityViolation) => (StatusCode::CONFLICT, Vec::new()),
            Err(_) => (StatusCode::NOT_FOUND, Vec::new()),
        }
    })
    .await
    .unwrap()
}

async fn standards(State(app): State<Arc<App>>) -> Json<Value> {
    // the PULL-down surface: children fetch; this node never pushes into anyone
    let u = app.universe.lock().unwrap();
    Json(json!({"scope": u.nodes[0].scope, "floors": u.nodes[0].floors}))
}

async fn egress(State(app): State<Arc<App>>, Json(req): Json<Value>) -> impl IntoResponse {
    tokio::task::spawn_blocking(move || {
        let requester_scope = req["requester_scope"].as_str().unwrap_or("").to_string();
        let local = {
            let u = app.universe.lock().unwrap();
            match u.retrieve(0, &req["query"], &req["token"], &requester_scope) {
                Ok(mut result) => {
                    // enrichment at the plane, not the node (0018 §8): hits gain their
                    // record's tags, and knowledge still in quarantine stops dressing as
                    // verified — each tier decorates its own hits before merging up.
                    if let Some(hits) = result["hits"].as_array_mut() {
                        for h in hits {
                            let Some(rec) = h["ref"].as_str()
                                .and_then(|r| u.nodes[0].records.get(r)) else { continue };
                            let tags = rec.get("tags").cloned().unwrap_or_else(|| json!([]));
                            let knowledge = tags.as_array()
                                .is_some_and(|t| t.iter().any(|x| x == "knowledge"));
                            if knowledge && rec["provenance_class"] == "ingested-archive" {
                                h["fidelity"] = json!("untrusted");
                            }
                            // the poison visibly dead (0014 §4): a recall version never
                            // dresses as anything else, whatever its provenance class
                            if tags.as_array().is_some_and(|t| t.iter().any(|x| x == "recalled")) {
                                h["fidelity"] = json!("recalled");
                            }
                            // lineage rides the hit so the librarian's walk (and any
                            // client) can follow derived_from without a privileged path
                            if let Some(df) = rec.get("derived_from") {
                                h["derived_from"] = df.clone();
                            }
                            h["tags"] = tags;
                        }
                    }
                    result
                }
                // the uniform refusal: authz-miss and every other miss share one shape (0002 §4)
                Err(_) => {
                    bump(&app, "refusals"); // count only; the refusal shape is unchanged (0002 §4)
                    return (
                        StatusCode::FORBIDDEN,
                        Json(json!({"error": "request cannot be served under this capability"})),
                    )
                }
            }
        };
        // time-horizon escalation, now across processes (0002 §3): serve-what-you-have,
        // delegate the deeper-time remainder UP over the wire
        let covered = {
            let u = app.universe.lock().unwrap();
            let now_u = u.nodes[0].high_water.clone().unwrap_or_else(|| u.now.clone());
            let from = req["query"]["time"]["from"].as_str().unwrap_or(&now_u);
            let age_days = (orreth_node::ts_seconds(&now_u) - orreth_node::ts_seconds(from)) as f64
                / 86_400.0;
            age_days <= app.horizon_days
        };
        if covered || app.parent.is_none() {
            return (StatusCode::OK, Json(local));
        }
        let spent = local["provenance"]["budget_spent"]["cost"].as_i64().unwrap_or(1);
        let remaining = req["query"]["budget"]["cost"].as_i64().unwrap_or(1).max(1) - spent;
        if remaining <= 0 {
            // budget-miss: un-served coverage, never an error shape
            let mut out = local;
            out["verification"] = json!("partial");
            out["remainder"] = json!({"not_served": {"from": req["query"]["time"]["from"]}});
            return (StatusCode::OK, Json(out));
        }
        let mut fwd = req.clone();
        fwd["query"]["budget"]["cost"] = json!(remaining);
        let parent_url = app.parent.as_ref().unwrap();
        match ureq::post(&format!("{parent_url}/retrieve")).send_json(&fwd) {
            Ok(resp) => {
                let upstream: Value = resp.into_json().unwrap_or_else(|_| json!({}));
                (StatusCode::OK, Json(merge_results(local, upstream)))
            }
            Err(_) => {
                // parent refused or unreachable ≡ un-served coverage — the shape never
                // distinguishes authz-miss, budget-miss, or a dead parent (0002 §4 + 0007)
                let mut out = local;
                out["verification"] = json!("partial");
                out["remainder"] = json!({"not_served": {"from": req["query"]["time"]["from"]}});
                (StatusCode::OK, Json(out))
            }
        }
    })
    .await
    .unwrap()
}

/// The locked merge semantics (0002 §3), across the wire: dedup by ref, newest first
/// (occurred_at travels with the hit for exactly this), remainder from the deepest tier.
fn merge_results(local: Value, upstream: Value) -> Value {
    let mut seen = std::collections::BTreeSet::new();
    let mut hits: Vec<Value> = Vec::new();
    for h in local["hits"].as_array().into_iter().flatten()
        .chain(upstream["hits"].as_array().into_iter().flatten())
    {
        if seen.insert(h["ref"].as_str().unwrap_or("").to_string()) {
            hits.push(h.clone());
        }
    }
    hits.sort_by(|a, b| b["occurred_at"].as_str().cmp(&a["occurred_at"].as_str()));
    let mut served_by = local["provenance"]["served_by"].as_array().cloned().unwrap_or_default();
    served_by.extend(upstream["provenance"]["served_by"].as_array().cloned().unwrap_or_default());
    let spent = local["provenance"]["budget_spent"]["cost"].as_i64().unwrap_or(0)
        + upstream["provenance"]["budget_spent"]["cost"].as_i64().unwrap_or(0);
    let mut out = json!({
        "hits": hits,
        "provenance": {"served_by": served_by, "time_span": local["provenance"]["time_span"],
                        "budget_spent": {"cost": spent}},
        "verification": if upstream["verification"] == "partial" { "partial" } else { "verified" },
    });
    if let Some(rem) = upstream.get("remainder") {
        out["remainder"] = rem.clone();
    }
    out
}

// ---------------------------------------------------------------- the model plane (0016)

async fn model_authorize(State(app): State<Arc<App>>, Json(req): Json<Value>) -> impl IntoResponse {
    tokio::task::spawn_blocking(move || {
        let token = &req["token"];
        {
            let u = app.universe.lock().unwrap();
            if u.verify_token(token).is_err() {
                bump(&app, "refusals");
                return (StatusCode::FORBIDDEN,
                        Json(json!({"error": "request cannot be served under this capability"})));
            }
        }
        let subject = token["subject"].as_str().unwrap_or("").to_string();
        let budget = token["constraints"]["budget"]["tokens"].as_i64().unwrap_or(0);
        let class = req["class"].as_str().unwrap_or("").to_string();
        let est = req["est_tokens"].as_i64().unwrap_or(0);
        let mut m = app.model.lock().unwrap();
        match m.resolve(&class) {
            model::Resolved::Model { model, deprecated } => {
                match m.debit(&subject, budget, est) {
                    Ok(remaining) => (StatusCode::OK, Json(json!({
                        "model": model, "deprecated": deprecated,
                        "subject": subject, "est_tokens": est, "remaining": remaining }))),
                    Err(()) => (StatusCode::FORBIDDEN,
                        Json(json!({"error": "request cannot be served under this capability"}))),
                }
            }
            model::Resolved::Miss => {
                if let Some(parent) = &app.parent {
                    // the model-miss climbs, like retrieval (0016 §1)
                    match ureq::post(&format!("{parent}/model/authorize")).send_json(&req) {
                        Ok(resp) => (StatusCode::OK,
                                     Json(resp.into_json().unwrap_or_else(|_| json!({})))),
                        Err(_) => (StatusCode::SERVICE_UNAVAILABLE,
                                   Json(json!({"error": "class has no living model at any tier"}))),
                    }
                } else {
                    (StatusCode::SERVICE_UNAVAILABLE,
                     Json(json!({"error": "class has no living model at any tier"})))
                }
            }
        }
    })
    .await
    .unwrap()
}

async fn model_meter(State(app): State<Arc<App>>, Json(req): Json<Value>) -> impl IntoResponse {
    tokio::task::spawn_blocking(move || {
        let mut m = app.model.lock().unwrap();
        let subject = req["subject"].as_str().unwrap_or("").to_string();
        let remaining = m.reconcile(&subject,
                                    req["est_tokens"].as_i64().unwrap_or(0),
                                    req["tokens"].as_i64().unwrap_or(0));
        let mut entry = req.clone();
        entry["at"] = json!(now_iso());
        if let Some(mid) = entry["model"].as_str() {
            if let Some(stall) = m.stalls.get_mut(mid) {
                stall["calls"] = json!(stall["calls"].as_i64().unwrap_or(0) + 1);
            }
        }
        m.meter_log.push(entry.clone());  // the roll-up's raw material — usage rises
        drop(m);
        // write-through (0019 §4): the meter outlives the daemon, like the records do
        if let Some(store) = &app.pg {
            let node_scope = app.universe.lock().unwrap().nodes[0].scope.clone();
            if let Err(e) = store.save_meter(&node_scope, &entry) {
                eprintln!("orrethd · postgres meter write-through failed: {e}");
            }
        }
        (StatusCode::OK, Json(json!({"remaining": remaining})))
    })
    .await
    .unwrap()
}

async fn model_usage(State(app): State<Arc<App>>) -> Json<Value> {
    Json(app.model.lock().unwrap().usage())
}

/// Dev-only lifecycle flip; becomes a governed escalation (0012 lanes) before any
/// multi-tenant deployment — flipping a model's state is a consequential act.
async fn model_state(State(app): State<Arc<App>>, Json(req): Json<Value>) -> impl IntoResponse {
    let ok = app.model.lock().unwrap().set_state(
        req["model"].as_str().unwrap_or(""), req["state"].as_str().unwrap_or(""));
    (if ok { StatusCode::OK } else { StatusCode::BAD_REQUEST },
     Json(json!({"ok": ok})))
}

// ---------------------------------------------------------------- the stable (0019)

/// This floor's stable plus every stable below, and per-agent usage floor-tagged from
/// the beats — who is thinking, and what it costs, one picture for the whole subtree.
async fn stable_list(State(app): State<Arc<App>>) -> Json<Value> {
    let scope = { app.universe.lock().unwrap().nodes[0].scope.clone() };
    let (mut stalls, own_usage) = {
        let m = app.model.lock().unwrap();
        (m.roster(), m.usage())
    };
    let mut usage: Vec<Value> = own_usage.as_array().cloned().unwrap_or_default();
    for u in usage.iter_mut() { u["floor"] = json!(scope.clone()); }
    fn descend(beat: &Value, stalls: &mut Vec<Value>, usage: &mut Vec<Value>) {
        if let Some(ss) = beat["stable"].as_array() { stalls.extend(ss.iter().cloned()); }
        if let Some(us) = beat["usage"].as_array() {
            for u in us {
                let mut u = u.clone();
                u["floor"] = beat["scope"].clone();
                usage.push(u);
            }
        }
        if let Some(kids) = beat["children"].as_array() {
            for k in kids { descend(k, stalls, usage); }
        }
    }
    for beat in app.children.lock().unwrap().values() { descend(beat, &mut stalls, &mut usage); }
    Json(json!({"scope": scope, "stalls": stalls, "usage": usage}))
}

/// Dev-only direct saddling (the wrangler's move after it probes a staged request);
/// becomes a governed escalation (0012 lanes) before any multi-tenant deployment.
async fn stable_saddle(State(app): State<Arc<App>>, Json(req): Json<Value>) -> impl IntoResponse {
    let floor = { app.universe.lock().unwrap().nodes[0].scope.clone() };
    match app.model.lock().unwrap().saddle(&req, &floor, &now_iso()) {
        Ok(stall) => (StatusCode::CREATED, Json(stall)),
        Err(e) => (StatusCode::CONFLICT, Json(json!({"error": e}))),
    }
}

/// The guarded lifecycle move — the drift check lives plane-side (model.rs), never
/// trusted from the wrangler's summary of it.
async fn stable_state(State(app): State<Arc<App>>, Json(req): Json<Value>) -> impl IntoResponse {
    match app.model.lock().unwrap().transition(&req, &now_iso()) {
        Ok(stall) => (StatusCode::OK, Json(stall)),
        Err(e) => (StatusCode::CONFLICT, Json(json!({"error": e}))),
    }
}

/// A canary beat observed by the wrangler — beats earn `available` (0019 §2).
async fn stable_hello(State(app): State<Arc<App>>, Json(req): Json<Value>) -> impl IntoResponse {
    match app.model.lock().unwrap().canary(req["id"].as_str().unwrap_or(""), &now_iso()) {
        Ok(stall) => (StatusCode::OK, Json(stall)),
        Err(e) => (StatusCode::CONFLICT, Json(json!({"error": e}))),
    }
}

// ---------------------------------------------------------------- the tool farm (0018)

/// This floor's toolshed, plus every toolshed below — assembled from the beats,
/// exactly like presence (one world, one picture; the F2 lesson applied in advance).
async fn farm_list(State(app): State<Arc<App>>) -> Json<Value> {
    let scope = { app.universe.lock().unwrap().nodes[0].scope.clone() };
    let mut services = app.farm.lock().unwrap().roster();
    fn descend(beat: &Value, out: &mut Vec<Value>) {
        if let Some(fs) = beat["farm"].as_array() { out.extend(fs.iter().cloned()); }
        if let Some(kids) = beat["children"].as_array() { for k in kids { descend(k, out); } }
    }
    for beat in app.children.lock().unwrap().values() { descend(beat, &mut services); }
    Json(json!({"scope": scope, "services": services}))
}

/// Dev-only direct planting (the keeper's move after it probes a staged request);
/// becomes a governed escalation (0012 lanes) before any multi-tenant deployment.
async fn farm_plant(State(app): State<Arc<App>>, Json(req): Json<Value>) -> impl IntoResponse {
    let floor = { app.universe.lock().unwrap().nodes[0].scope.clone() };
    match app.farm.lock().unwrap().plant(&req, &floor, &now_iso()) {
        Ok(svc) => (StatusCode::CREATED, Json(svc)),
        Err(e) => (StatusCode::CONFLICT, Json(json!({"error": e}))),
    }
}

/// The guarded lifecycle move — the rug-pull check lives plane-side (farm.rs).
async fn farm_state(State(app): State<Arc<App>>, Json(req): Json<Value>) -> impl IntoResponse {
    match app.farm.lock().unwrap().transition(&req, &now_iso()) {
        Ok(svc) => (StatusCode::OK, Json(svc)),
        Err(e) => (StatusCode::CONFLICT, Json(json!({"error": e}))),
    }
}

/// A heartbeat observed by the keeper — beats earn probation's exit (0018 §2).
async fn farm_hello(State(app): State<Arc<App>>, Json(req): Json<Value>) -> impl IntoResponse {
    match app.farm.lock().unwrap().beat(req["name"].as_str().unwrap_or(""), &now_iso()) {
        Ok(svc) => (StatusCode::OK, Json(svc)),
        Err(e) => (StatusCode::CONFLICT, Json(json!({"error": e}))),
    }
}

/// Every consumption on the record — volume and shape, never payloads (0016 §6).
async fn farm_meter(State(app): State<Arc<App>>, Json(req): Json<Value>) -> impl IntoResponse {
    let out = app.farm.lock().unwrap().meter(&req, &now_iso());
    match out {
        Ok(v) => (StatusCode::OK, Json(v)),
        // the uniform refusal: a non-serving service and a missing grant wear one face
        Err(_) => {
            bump(&app, "refusals");
            (StatusCode::FORBIDDEN,
             Json(json!({"error": "request cannot be served under this capability"})))
        }
    }
}

// ---------------------------------------------------------------- presence: the life layer

async fn runs_ingress(State(app): State<Arc<App>>, Json(run): Json<Value>) -> impl IntoResponse {
    tokio::task::spawn_blocking(move || {
        let mut u = app.universe.lock().unwrap();
        match u.record_run(&run) {
            Ok(id) => (StatusCode::CREATED, Json(json!({"id": id}))),
            Err(_) => (StatusCode::FORBIDDEN,
                       Json(json!({"error": "run rejected — resident-signed or nothing"}))),
        }
    }).await.unwrap()
}

/// The roster, alive. RESIDENTS are the organs every tier is staffed with (0000 §2):
/// becky issues identity, vigil watches (content-blind), the steward distills, governance
/// arbitrates. WORKFORCE is the leased agents, their activity read from the signed diary of
/// thought (0005). This is what the Console renders as "who is awake in this world."
/// The leased agents on THIS floor, read from the signed diary (0005). Shared by
/// `/presence` and the upward beat, so a parent's roster matches the floor's own.
fn local_workforce(app: &App) -> Vec<Value> {
    let u = app.universe.lock().unwrap();
    let scope = u.nodes[0].scope.clone();
    // per-agent USD from the model meter (0016) — what each agent COSTS, not just its tokens
    let mut cost: BTreeMap<String, f64> = BTreeMap::new();
    for e in &app.model.lock().unwrap().meter_log {
        if let Some(s) = e["subject"].as_str() {
            *cost.entry(s.to_string()).or_insert(0.0) += e["usd"].as_f64().unwrap_or(0.0);
        }
    }
    let mut per: BTreeMap<String, (i64, i64, i64, String)> = BTreeMap::new();
    for r in u.runs.values() {
        let a = r["agent"].as_str().unwrap_or("?").to_string();
        let e = per.entry(a).or_insert((0, 0, 0, String::new()));
        e.0 += 1;
        if r["outcome"] == "success" { e.1 += 1; }
        e.2 += r["cost"]["tokens"].as_i64().unwrap_or(0);
        let at = r["occurred_at"].as_str().unwrap_or("");
        if at > e.3.as_str() { e.3 = at.to_string(); }
    }
    // names an agent gave when it joined — so the roster shows "scout", not a did:key
    // prefix. Only COMPLETED joins bind (key proven + human-admitted, the hardened
    // door): a squatter's pending claim never names anyone on this roster.
    let names: BTreeMap<String, String> = app.requests.lock().unwrap().iter()
        .filter(|r| r["kind"] == "join" && r["status"] == "done")
        .filter_map(|r| Some((r["did"].as_str()?.to_string(), r["name"].as_str()?.to_string())))
        .collect();
    let now = now_iso();
    per.into_iter().map(|(agent,(runs,ok,tok,last))| {
        let idle = orreth_node::ts_seconds(&now)
                 - orreth_node::ts_seconds(if last.is_empty() { &now } else { &last });
        let usd = *cost.get(&agent).unwrap_or(&0.0);
        json!({"agent": agent, "name": names.get(&agent), "role":"workforce",
               "scope": scope, "runs": runs, "success": ok,
               "tokens": tok, "usd": (usd*1e6).round()/1e6, "last_seen": last,
               "state": if idle < 120 { "thinking" } else { "idle" }})
    }).collect()
}

/// Resident roster for this floor: names, display vitals from real state, and DIDs.
/// An organ's DID comes from its JOIN PIN when one exists (becky-minted token, chain
/// verified against the pinned root — see organs_pin); only unpinned organs fall back
/// to mining signed records, anchored to the EARLIEST tagged claim and marked
/// contested when more than one DID has signed (tags are author-chosen; the mined
/// fallback stays honest, never silently picks). Shared by /presence and the upward
/// beat — one roster for rail + orrery.
fn residents(app: &App) -> Vec<Value> {
    let u = app.universe.lock().unwrap();
    let leaf = u.nodes[0].scope.rsplit('/').next().unwrap_or("").to_string();
    let memories = u.nodes[0].records.len();
    let floors = u.nodes[0].floors.len();
    let root = u.trust_root.clone();
    // earliest (occurred_at, author) claim per tag, plus distinct-author counts
    let (mut cha, mut lib, mut ada) =
        (None::<(String, String)>, None::<(String, String)>, None::<(String, String)>);
    let (mut cha_authors, mut lib_authors, mut ada_authors) =
        (BTreeSet::new(), BTreeSet::new(), BTreeSet::new());
    let (mut worldlines, mut knowledge, mut mindlines) = (0i64, 0i64, 0i64);
    for rec in u.nodes[0].records.values() {
        let tags = rec.get("tags").and_then(Value::as_array);
        let has = |t: &str| tags.is_some_and(|ts| ts.iter().any(|x| x == t));
        let claim = |slot: &mut Option<(String, String)>, authors: &mut BTreeSet<String>| {
            if let Some(a) = rec["author"].as_str() {
                authors.insert(a.to_string());
                let at = rec["occurred_at"].as_str().unwrap_or("").to_string();
                // ties on occurred_at break by author, so the winner is deterministic
                if slot.as_ref().map_or(true, |(t, d)| (at.as_str(), a) < (t.as_str(), d.as_str())) {
                    *slot = Some((at, a.to_string()));
                }
            }
        };
        if has("service") {
            worldlines += 1;
            claim(&mut cha, &mut cha_authors);
        }
        if has("knowledge") {
            knowledge += 1;
            claim(&mut lib, &mut lib_authors);
        }
        if has("mind") {
            mindlines += 1;
            claim(&mut ada, &mut ada_authors);
        }
    }
    drop(u);
    let (leases, gathers) = {
        let q = app.requests.lock().unwrap();
        (q.iter().filter(|r| r["kind"] == "join" && r["status"] == "done").count(),
         q.iter().filter(|r| r["kind"] == "gather" && r["status"] == "done").count())
    };
    let (serving, tool_calls) = {
        let f = app.farm.lock().unwrap();
        (f.services.values().filter(|s| s["state"] == "serving").count(), f.meter_log.len())
    };
    // every resident wears its meter — the honest zero included (0019 §4): per-DID
    // llm calls/usd from the meter log, plus the stable's headcount for ada
    let (n_stalls, minds_live, spend) = {
        let m = app.model.lock().unwrap();
        let live = m.stalls.values()
            .filter(|s| matches!(s["state"].as_str(), Some("available") | Some("canaried")))
            .count();
        let mut spend: BTreeMap<String, (i64, f64)> = BTreeMap::new();
        for e in &m.meter_log {
            if let Some(s) = e["subject"].as_str() {
                let en = spend.entry(s.to_string()).or_insert((0, 0.0));
                en.0 += 1;
                en.1 += e["usd"].as_f64().unwrap_or(0.0);
            }
        }
        (m.stalls.len(), live, spend)
    };
    let llm = |did: Option<&str>| -> (i64, f64) {
        did.and_then(|d| spend.get(d))
            .map(|&(c, u)| (c, (u * 1e6).round() / 1e6))
            .unwrap_or((0, 0.0))
    };
    // authority beats archaeology (the R1 door, closed): a pin granted at join —
    // becky-chained, verified against the pinned root — overrides earliest-record
    // mining and retires the contested flag for that organ. Mining stays as the
    // honest fallback on floors nobody has pinned yet.
    let pins = app.organs.lock().unwrap().clone();
    let (cha_pin, lib_pin, ada_pin) =
        (pins.get("charlotte").cloned(), pins.get("librarian").cloned(), pins.get("ada").cloned());
    let cha_did = cha_pin.clone().or(cha.map(|(_, d)| d));
    let lib_did = lib_pin.clone().or(lib.map(|(_, d)| d));
    let ada_did = ada_pin.clone().or(ada.map(|(_, d)| d));
    let v = app.vitals.lock().unwrap();
    let vital = |k: &str| v.get(k).copied().unwrap_or(0);

    let (bk_c, bk_u) = llm(root.as_deref());
    let mut out = vec![
        json!({"agent": format!("becky·{leaf}"), "name": "becky", "role": "becky · IAM",
               "state": "resident", "did": root,
               "blurb": "issues every identity; the pinned trust root",
               "vitals": {"leases": leases, "llm calls": bk_c, "llm usd": bk_u}}),
        json!({"agent": format!("vigil·{leaf}"), "name": "vigil", "role": "vigil · the Warden",
               "state": "watching",
               "blurb": "detection, content-blind; stages, never enforces",
               "vitals": {"beats heard": vital("beats_heard"), "refusals": vital("refusals"),
                          "llm calls": 0, "llm usd": 0}}),
        json!({"agent": format!("steward·{leaf}"), "name": "steward", "role": "steward · memory",
               "state": "distilling",
               "blurb": "prunes and distills what the layer learns",
               "vitals": {"memories": memories, "llm calls": 0, "llm usd": 0}}),
        json!({"agent": format!("governance·{leaf}"), "name": "governance", "role": "governance",
               "state": "resident",
               "blurb": "arbitrates drift; guards the floors",
               "vitals": {"floors": floors, "beats up": vital("beats_up"),
                          "llm calls": 0, "llm usd": 0}}),
    ];
    if serving > 0 || worldlines > 0 {
        let (c_c, c_u) = llm(cha_did.as_deref());
        let mut c = json!({"agent": format!("charlotte·{leaf}"), "name": "charlotte",
            "role": "charlotte · farm keeper", "state": "tending",
            "did": cha_did,
            "blurb": "probes, pins, and attests the toolshed; writes the worldlines",
            "vitals": {"tools serving": serving, "tool calls": tool_calls,
                       "worldline events": worldlines, "llm calls": c_c, "llm usd": c_u}});
        if cha_pin.is_some() {
            c["pinned"] = json!(true);
        } else if cha_authors.len() > 1 {
            c["did_contested"] = json!(cha_authors.len());
        }
        out.push(c);
    }
    if knowledge > 0 {
        let (l_c, l_u) = llm(lib_did.as_deref());
        let mut l = json!({"agent": format!("librarian·{leaf}"), "name": "librarian",
            "role": "librarian · knowledge", "state": "gathering",
            "did": lib_did,
            "blurb": "gathers from identified sources; admits quarantined",
            "vitals": {"gathers": gathers, "knowledge held": knowledge,
                       "llm calls": l_c, "llm usd": l_u}});
        if lib_pin.is_some() {
            l["pinned"] = json!(true);
        } else if lib_authors.len() > 1 {
            l["did_contested"] = json!(lib_authors.len());
        }
        out.push(l);
    }
    if n_stalls > 0 || mindlines > 0 {
        let (a_c, a_u) = llm(ada_did.as_deref());
        let mut a = json!({"agent": format!("ada·{leaf}"), "name": "ada",
            "role": "ada · the wrangler", "state": "syncing",
            "did": ada_did,
            "blurb": "tends the stable; syncs the catalogs, pins the deals",
            "vitals": {"stalls": n_stalls, "minds live": minds_live,
                       "worldline events": mindlines, "llm calls": a_c, "llm usd": a_u}});
        if ada_pin.is_some() {
            a["pinned"] = json!(true);
        } else if ada_authors.len() > 1 {
            a["did_contested"] = json!(ada_authors.len());
        }
        out.push(a);
    }
    out
}

async fn presence(State(app): State<Arc<App>>) -> Json<Value> {
    let scope = { app.universe.lock().unwrap().nodes[0].scope.clone() };
    let residents = json!(residents(&app));
    // this floor's leased agents, then every floor below: each child beat carries its
    // subtree's rosters, so the Console here shows the whole world — matching the orrery
    let mut workforce = local_workforce(&app);
    fn descend(beat: &Value, out: &mut Vec<Value>) {
        if let Some(ws) = beat["workforce"].as_array() { out.extend(ws.iter().cloned()); }
        if let Some(kids) = beat["children"].as_array() { for k in kids { descend(k, out); } }
    }
    for beat in app.children.lock().unwrap().values() { descend(beat, &mut workforce); }
    Json(json!({"scope": scope, "as_of": now_iso(), "residents": residents, "workforce": workforce}))
}

/// This node's subtree summary: own stats + everything its children last reported.
/// The Console's orrery renders exactly this shape, nested all the way down. The beat
/// now also carries `stable`, per-agent `usage`, and a `pulse` mini-rollup, so the apex
/// can total the whole world without reaching into any floor (0019 §4).
fn summary(app: &App) -> Value {
    let (scope, records) = {
        let u = app.universe.lock().unwrap();
        (u.nodes[0].scope.clone(), u.nodes[0].records.len())
    };
    let (runs, agents, success, tokens) = {
        let u = app.universe.lock().unwrap();
        let mut agents = BTreeSet::new();
        let (mut ok, mut tok) = (0i64, 0i64);
        for r in u.runs.values() {
            if let Some(a) = r["agent"].as_str() {
                agents.insert(a.to_string());
            }
            if r["outcome"] == "success" { ok += 1; }
            tok += r["cost"]["tokens"].as_i64().unwrap_or(0);
        }
        (u.runs.len(), agents.len(), ok, tok)
    };
    let (usd, model_calls, usage, stable) = {
        let m = app.model.lock().unwrap();
        let usd: f64 = m.meter_log.iter().filter_map(|e| e["usd"].as_f64()).sum();
        (usd, m.meter_log.len(), m.usage(), m.roster())
    };
    let (services, tool_calls, farm_roster) = {
        let f = app.farm.lock().unwrap();
        (f.services.values().filter(|s| s["state"] == "serving").count(),
         f.meter_log.len(), f.roster())
    };
    let children: Vec<Value> = app.children.lock().unwrap().values().cloned().collect();
    // horizon rides the beat (serde maps a non-finite "forever" to null — the apex)
    json!({"scope": scope, "records": records, "runs": runs, "agents": agents,
           "usd": (usd * 1e6).round() / 1e6, "horizon_days": app.horizon_days,
           "workforce": local_workforce(app), "farm": farm_roster,
           "stable": stable, "usage": usage,
           "pulse": {"memories": records, "runs": runs, "success": success,
                     "tokens": tokens, "usd": (usd * 1e6).round() / 1e6,
                     "model_calls": model_calls, "services": services,
                     "tool_calls": tool_calls},
           "residents": residents(app), "children": children})
}

/// A child announces its subtree — the upward beat. Grandchildren ride along, so
/// heartbeats cascade floor by floor and the apex ends up holding the whole world.
async fn hello(State(app): State<Arc<App>>, Json(mut beat): Json<Value>) -> impl IntoResponse {
    let Some(scope) = beat["scope"].as_str().map(str::to_string) else {
        return (StatusCode::BAD_REQUEST, Json(json!({"error": "a beat needs a scope"})));
    };
    beat["heard_at"] = json!(now_iso());
    app.children.lock().unwrap().insert(scope, beat);
    bump(&app, "beats_heard"); // count beats received from children
    (StatusCode::OK, Json(json!({"ok": true})))
}

/// The world below this floor — ecosystems, fields, agents — assembled from heartbeats.
async fn topology(State(app): State<Arc<App>>) -> Json<Value> {
    Json(summary(&app))
}

/// The tier's living numbers — what the Console's Pulse renders (0005 roll-up, at a
/// glance). Own floor PLUS every descendant beat's pulse, so the dashboard and the
/// orrery describe the same world (0019 §4 — the F2 lesson, at the numbers too).
async fn rollup(State(app): State<Arc<App>>) -> Json<Value> {
    let scope = { app.universe.lock().unwrap().nodes[0].scope.clone() };
    let mut acc: BTreeMap<&str, f64> = BTreeMap::new();
    {
        let u = app.universe.lock().unwrap();
        for r in u.runs.values() {
            *acc.entry("runs").or_default() += 1.0;
            if r["outcome"] == "success" { *acc.entry("success").or_default() += 1.0; }
            *acc.entry("tokens").or_default() += r["cost"]["tokens"].as_i64().unwrap_or(0) as f64;
        }
        *acc.entry("memories").or_default() += u.nodes[0].records.len() as f64;
    }
    {
        let m = app.model.lock().unwrap();
        *acc.entry("usd").or_default() += m.meter_log.iter()
            .filter_map(|e| e["usd"].as_f64()).sum::<f64>();
        *acc.entry("model_calls").or_default() += m.meter_log.len() as f64;
    }
    {
        let f = app.farm.lock().unwrap();
        *acc.entry("services").or_default() +=
            f.services.values().filter(|s| s["state"] == "serving").count() as f64;
        *acc.entry("tool_calls").or_default() += f.meter_log.len() as f64;
    }
    fn descend(beat: &Value, acc: &mut BTreeMap<&str, f64>) {
        if let Some(p) = beat["pulse"].as_object() {
            for k in ["memories", "runs", "success", "tokens", "usd",
                      "model_calls", "services", "tool_calls"] {
                *acc.entry(k).or_default() += p.get(k).and_then(Value::as_f64).unwrap_or(0.0);
            }
        }
        if let Some(kids) = beat["children"].as_array() {
            for k in kids { descend(k, acc); }
        }
    }
    for beat in app.children.lock().unwrap().values() { descend(beat, &mut acc); }
    let g = |k: &str| acc.get(k).copied().unwrap_or(0.0);
    let (runs, ok) = (g("runs"), g("success"));
    Json(json!({"scope": scope,
        "memories": g("memories") as i64, "runs": runs as i64, "success": ok as i64,
        "success_rate": if runs > 0.0 {(100.0 * ok / runs) as i64} else {0},
        "tokens": g("tokens") as i64, "usd": (g("usd") * 1e6).round() / 1e6,
        "model_calls": g("model_calls") as i64,
        "services": g("services") as i64, "tool_calls": g("tool_calls") as i64}))
}

/// The pinned organ roster — transparency for the pin round and any curious client.
async fn organs_list(State(app): State<Arc<App>>) -> Json<Value> {
    let scope = { app.universe.lock().unwrap().nodes[0].scope.clone() };
    Json(json!({"scope": scope, "pins": *app.organs.lock().unwrap()}))
}

/// An organ's DID, pinned at join (the stricter R1): becky mints the token, this
/// floor verifies the chain against its pinned trust root (0006) — the same math
/// as every lease — and the roster stops mining archaeology for that organ.
/// Re-pinning is idempotent; a rotated organ is one more becky-minted pin away.
async fn organs_pin(State(app): State<Arc<App>>, Json(req): Json<Value>) -> impl IntoResponse {
    tokio::task::spawn_blocking(move || {
        let organ = req["organ"].as_str().unwrap_or("").to_string();
        let subject = req["token"]["subject"].as_str().unwrap_or("").to_string();
        let ok = { app.universe.lock().unwrap().verify_token(&req["token"]).is_ok() };
        if organ.is_empty() || subject.is_empty() || !ok {
            bump(&app, "refusals"); // the uniform refusal — a bad chain learns nothing
            return (StatusCode::FORBIDDEN,
                    Json(json!({"error": "request cannot be served under this capability"})));
        }
        app.organs.lock().unwrap().insert(organ.clone(), subject.clone());
        (StatusCode::OK, Json(json!({"organ": organ, "did": subject})))
    })
    .await
    .unwrap()
}

async fn requests_resolve(State(app): State<Arc<App>>, Json(body): Json<Value>) -> impl IntoResponse {
    let mut q = app.requests.lock().unwrap();
    let id = body["id"].as_str().unwrap_or("");
    for r in q.iter_mut() {
        if r["id"] == id {
            r["status"] = body.get("status").cloned().unwrap_or(json!("done"));
            if let Some(n) = body.get("result") { r["result"] = n.clone(); }
        }
    }
    (StatusCode::OK, Json(json!({"ok": true})))
}

async fn requests_list(State(app): State<Arc<App>>) -> Json<Value> {
    Json(json!({"requests": *app.requests.lock().unwrap()}))
}

/// A human submits an intent — an ask ("gather knowledge on X") or a HITL decision.
/// Unsigned: it is an INPUT, not a memory. Cognition picks it up and acts with authority,
/// and the result becomes a signed memory in the Window (0014's loop, human-initiated).
async fn requests_submit(State(app): State<Arc<App>>, Json(mut req): Json<Value>) -> impl IntoResponse {
    let mut q = app.requests.lock().unwrap();
    // the id carries the submission second: the queue is in-memory, so a restarted daemon
    // must never reissue an id a long-lived consumer (becky) has already seen
    let at = now_iso();
    let id = format!("req-{}-{}", q.len() + 1, orreth_node::ts_seconds(&at));
    req["id"] = json!(id);
    req["status"] = json!("pending");
    req["at"] = json!(at);
    q.push(req.clone());
    (StatusCode::CREATED, Json(req))
}
