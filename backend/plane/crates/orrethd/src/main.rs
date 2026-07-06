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

    let model_plane = model::ModelPlane::from_file(
        &arg("--models").unwrap_or_else(|| "profiles/model-registry.json".into()));
    let app = Arc::new(App {
        universe: Mutex::new(universe),
        model: Mutex::new(model_plane),
        farm: Mutex::new(farm::Farm::new()),
        parent,
        horizon_days: dur_days(horizon),
        pg: pg_store,
        requests: Mutex::new(Vec::new()),
        children: Mutex::new(BTreeMap::new()),
    });

    // the upward presence beat: every 5s tell the parent what this subtree holds,
    // children riding along — so the apex assembles the whole world from heartbeats
    if let Some(parent_url) = app.parent.clone() {
        let beat = app.clone();
        std::thread::spawn(move || loop {
            let s = summary(&beat);
            let _ = ureq::post(&format!("{parent_url}/hello")).send_json(&s);
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
        .route("/runs", post(runs_ingress))
        .route("/presence", get(presence))
        .route("/rollup", get(rollup))
        .route("/hello", post(hello))
        .route("/topology", get(topology))
        .route("/requests", get(requests_list))
        .route("/requests", post(requests_submit))
        .route("/requests/resolve", post(requests_resolve))
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
                            h["tags"] = tags;
                        }
                    }
                    result
                }
                // the uniform refusal: authz-miss and every other miss share one shape (0002 §4)
                Err(_) => {
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
        m.meter_log.push(entry);          // the roll-up's raw material — usage rises
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
    match app.farm.lock().unwrap().meter(&req, &now_iso()) {
        Ok(v) => (StatusCode::OK, Json(v)),
        // the uniform refusal: a non-serving service and a missing grant wear one face
        Err(_) => (StatusCode::FORBIDDEN,
                   Json(json!({"error": "request cannot be served under this capability"}))),
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
    // names an agent gave when it joined — so the roster shows "scout", not a did:key prefix
    let names: BTreeMap<String, String> = app.requests.lock().unwrap().iter()
        .filter(|r| r["kind"] == "join")
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

async fn presence(State(app): State<Arc<App>>) -> Json<Value> {
    let scope = { app.universe.lock().unwrap().nodes[0].scope.clone() };
    let leaf = scope.rsplit('/').next().unwrap_or(&scope).to_string();
    let residents = json!([
        {"agent": format!("becky·{leaf}"), "role":"becky · IAM",
         "state":"resident", "blurb":"issues every identity; the pinned trust root"},
        {"agent": format!("vigil·{leaf}"), "role":"vigil · the Warden",
         "state":"watching", "blurb":"detection, content-blind; stages, never enforces"},
        {"agent": format!("steward·{leaf}"), "role":"steward · memory",
         "state":"distilling", "blurb":"prunes and distills what the layer learns"},
        {"agent": format!("governance·{leaf}"), "role":"governance",
         "state":"resident", "blurb":"arbitrates drift; guards the floors"}
    ]);
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
/// The Console's orrery renders exactly this shape, nested all the way down.
fn summary(app: &App) -> Value {
    let (scope, records) = {
        let u = app.universe.lock().unwrap();
        (u.nodes[0].scope.clone(), u.nodes[0].records.len())
    };
    let (runs, agents) = {
        let u = app.universe.lock().unwrap();
        let mut agents = BTreeSet::new();
        for r in u.runs.values() {
            if let Some(a) = r["agent"].as_str() {
                agents.insert(a.to_string());
            }
        }
        (u.runs.len(), agents.len())
    };
    let usd: f64 = app.model.lock().unwrap().meter_log.iter()
        .filter_map(|e| e["usd"].as_f64()).sum();
    let children: Vec<Value> = app.children.lock().unwrap().values().cloned().collect();
    // horizon rides the beat (serde maps a non-finite "forever" to null — the apex)
    json!({"scope": scope, "records": records, "runs": runs, "agents": agents,
           "usd": (usd * 1e6).round() / 1e6, "horizon_days": app.horizon_days,
           "workforce": local_workforce(app), "farm": app.farm.lock().unwrap().roster(),
           "children": children})
}

/// A child announces its subtree — the upward beat. Grandchildren ride along, so
/// heartbeats cascade floor by floor and the apex ends up holding the whole world.
async fn hello(State(app): State<Arc<App>>, Json(mut beat): Json<Value>) -> impl IntoResponse {
    let Some(scope) = beat["scope"].as_str().map(str::to_string) else {
        return (StatusCode::BAD_REQUEST, Json(json!({"error": "a beat needs a scope"})));
    };
    beat["heard_at"] = json!(now_iso());
    app.children.lock().unwrap().insert(scope, beat);
    (StatusCode::OK, Json(json!({"ok": true})))
}

/// The world below this floor — ecosystems, fields, agents — assembled from heartbeats.
async fn topology(State(app): State<Arc<App>>) -> Json<Value> {
    Json(summary(&app))
}

/// The tier's living numbers — what the Console's Pulse renders (0005 roll-up, at a glance).
async fn rollup(State(app): State<Arc<App>>) -> Json<Value> {
    let u = app.universe.lock().unwrap();
    let m = app.model.lock().unwrap();
    let (mut runs, mut ok, mut tok) = (0i64, 0i64, 0i64);
    for r in u.runs.values() {
        runs += 1;
        if r["outcome"] == "success" { ok += 1; }
        tok += r["cost"]["tokens"].as_i64().unwrap_or(0);
    }
    let usd: f64 = m.meter_log.iter().filter_map(|e| e["usd"].as_f64()).sum();
    let calls = m.meter_log.len();
    let f = app.farm.lock().unwrap();
    let serving = f.services.values().filter(|s| s["state"] == "serving").count();
    Json(json!({"scope": u.nodes[0].scope,
        "memories": u.nodes[0].records.len(), "runs": runs, "success": ok,
        "success_rate": if runs>0 {100*ok/runs} else {0},
        "tokens": tok, "usd": (usd*1e6).round()/1e6, "model_calls": calls,
        "services": serving, "tool_calls": f.meter_log.len()}))
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
