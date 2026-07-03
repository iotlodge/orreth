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

struct App {
    universe: Mutex<Universe>,
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

    let node = Node {
        scope: scope.clone(),
        horizon_days: dur_days(horizon),
        parent: None,
        records: BTreeMap::new(),
        high_water: None,
        floors: profile.get("floors").and_then(Value::as_array).cloned().unwrap_or_default(),
    };
    // trust-root pinning: token chains must start at the profile's root. did:key roots
    // embed their key; did:web roots need --root-pub until the resolver joins.
    let trust_root = profile["trust_root"]["root"].as_str().map(str::to_string);
    let mut identities = BTreeMap::new();
    if let (Some(root), Some(pub_key)) = (&trust_root, arg("--root-pub")) {
        identities.insert(root.clone(), pub_key);
    }
    let universe = Universe {
        nodes: vec![node],
        identities,
        revoked: BTreeSet::new(),
        purged: BTreeSet::new(),
        now: now_iso(),
        body_store: arg("--store-dir").map(|d| BodyStore::local(std::path::Path::new(&d))),
        trust_root,
    };
    let app = Arc::new(App { universe: Mutex::new(universe) });

    let router = Router::new()
        .route("/health", get(health))
        .route("/records", post(ingress))
        .route("/records/:id/body", get(body))
        .route("/retrieve", post(egress))
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
            Ok(id) => (StatusCode::CREATED, Json(json!({"id": id}))),
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

async fn egress(State(app): State<Arc<App>>, Json(req): Json<Value>) -> impl IntoResponse {
    tokio::task::spawn_blocking(move || {
        let u = app.universe.lock().unwrap();
        let requester_scope = req["requester_scope"].as_str().unwrap_or("");
        match u.retrieve(0, &req["query"], &req["token"], requester_scope) {
            Ok(result) => (StatusCode::OK, Json(result)),
            // the uniform refusal: authz-miss and every other miss share one shape (0002 §4)
            Err(_) => (
                StatusCode::FORBIDDEN,
                Json(json!({"error": "request cannot be served under this capability"})),
            ),
        }
    })
    .await
    .unwrap()
}
