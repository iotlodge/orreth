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

mod pg;

struct App {
    universe: Mutex<Universe>,
    /// PUSH up / PULL down (0000 §1): a child knows its parent; a parent never reaches in.
    parent: Option<String>,
    horizon_days: f64,
    /// Write-through persistence: the daemon may die; the records don't.
    pg: Option<pg::PgRecords>,
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
        match ureq::get(&format!("{parent_url}/standards")).call() {
            Ok(resp) => {
                let pulled: Value = resp.into_json().expect("parent standards json");
                let inherited = pulled["floors"].as_array().cloned().unwrap_or_default();
                println!("orrethd · pulled {} inherited floor(s) from {parent_url}", inherited.len());
                floors.extend(inherited);
            }
            Err(e) => {
                // fail-closed continue (0007): last-known would apply if we had it; at first
                // boot there is nothing known — start with own floors and keep trying later
                eprintln!("orrethd · parent unreachable at boot ({e}); starting with local floors only");
            }
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

    let app = Arc::new(App {
        universe: Mutex::new(universe),
        parent,
        horizon_days: dur_days(horizon),
        pg: pg_store,
    });

    let router = Router::new()
        .route("/health", get(health))
        .route("/records", post(ingress))
        .route("/records/:id/body", get(body))
        .route("/retrieve", post(egress))
        .route("/standards", get(standards))
        .with_state(app);

    let listener = tokio::net::TcpListener::bind(("127.0.0.1", port)).await.unwrap();
    println!("orrethd · scope={scope} · tier_label={} · listening on 127.0.0.1:{port}",
             profile["tier_label"].as_str().unwrap_or("?"));
    axum::serve(listener, router).await.unwrap();
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
                    if let Err(e) = store.save(&u.nodes[0].records[&id]) {
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
                Ok(result) => result,
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
