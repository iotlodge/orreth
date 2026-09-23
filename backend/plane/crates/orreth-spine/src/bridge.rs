// PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp3, the ask road · 2026-09-22
//! The Rust bridge — the doors and the feed of `orreth_spine.glass` +
//! `bridgefeed` on axum, lit in SHADOW on :4601 beside the Python Bridge on
//! :4600, both on one ground. It serves the SAME page (`spine/glass/index.html`
//! read from disk — `ORRETH_GLASS`, else the crate's `../../../../spine/glass/
//! index.html`), the same JSON shapes and status codes at every door it has
//! ported, and the same SSE feed (`/feed`: `id: <rev>` + `data: <notice>`,
//! `event: resync` when the gap outlived the ring, `: keepalive` every 15 s),
//! so the one page works unchanged against either port. It holds NO residents
//! (they stay Python, serving from their benches) and runs no schedule or
//! intent loop (sp4): it relays, it dispatches, it feeds, it answers.
//!
//! Doors ported: `GET /` · `/feed` · `/health` · `/ask/<id>` · `/asks` ·
//! `/residents` · `/crew` · `/sessions` · `/session/<id>` · `/proof` ·
//! `/analyzer[?origin=]` · `/services[?kind=]` · `/intentions` · `/markers`
//! · `/markers/kinds` · `/shadow` (Rust-only: the dispatcher's meter);
//! `POST /ask` · `/confirm` · `/enroll` · `/enroll/confirm` · `/sessions`.
//! Every other door answers 404 with no body, as the Python handler does —
//! the page treats a missing door as "nothing here".

use crate::asks::{self, Submit, FEED_TOPICS};
use crate::dispatcher::{self, Meter};
use crate::feed::{self, Feed};
use crate::ground::Ground;
use crate::intent::{read_words, ASK_KINDS};
use crate::intent_live::{self, Declare};
use crate::markers_live;
use crate::proof::one_face;
use crate::proof_live;
use crate::py::python_str;
use crate::services::KINDS as SERVICE_KINDS;
use crate::sessions;
use crate::world::{RoadError, World};
use axum::body::Bytes;
use axum::extract::{Path, Query, State};
use axum::http::{header, HeaderMap, StatusCode};
use axum::response::sse::{Event, KeepAlive, Sse};
use axum::response::{IntoResponse, Response};
use axum::routing::{get, post};
use axum::Router;
use serde_json::{json, Value};
use std::collections::HashMap;
use std::convert::Infallible;
use std::path::PathBuf;
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::Arc;
use std::time::Duration;
use tokio_stream::wrappers::BroadcastStream;
use tokio_stream::StreamExt;

pub const PERSON_DEFAULT: &str = "did:orreth:person:jb";
pub const PORT_DEFAULT: u16 = 4601;

/// The glass's path law: `ORRETH_GLASS`, else the one page beside the crate.
pub fn glass_path() -> PathBuf {
    std::env::var("ORRETH_GLASS")
        .ok()
        .filter(|p| !p.is_empty())
        .map(PathBuf::from)
        .unwrap_or_else(|| {
            PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("../../../../spine/glass/index.html")
        })
}

/// What lights a bridge.
#[derive(Debug, Clone)]
pub struct Config {
    pub port: u16,
    pub world: World,
    pub glass: PathBuf,
    /// `SPINE_MASTERS` — comma-separated person DIDs declared at birth.
    pub masters: String,
    /// `SPINE_HUMAN_ZONE` — the ground's default human zone (the residents
    /// read it; the bridge only says it).
    pub human_zone: String,
}

impl Config {
    /// The dials: `SPINE_BRIDGE_PORT` (4601) and the world's.
    pub fn from_env() -> Config {
        Config {
            port: std::env::var("SPINE_BRIDGE_PORT")
                .ok()
                .and_then(|p| p.parse().ok())
                .unwrap_or(PORT_DEFAULT),
            world: World::from_env(),
            glass: glass_path(),
            masters: std::env::var("SPINE_MASTERS").unwrap_or_default(),
            human_zone: std::env::var("SPINE_HUMAN_ZONE")
                .ok()
                .filter(|z| !z.is_empty())
                .unwrap_or_else(|| "America/Denver".into()),
        }
    }
}

struct App {
    cfg: Config,
    feed: Arc<Feed>,
    meter: Arc<Meter>,
    group: String,
    port: u16,
}

/// A lit bridge: its port, its readiness, its meter, and its stop.
pub struct Lit {
    pub port: u16,
    pub group: String,
    pub stop: Arc<AtomicBool>,
    pub dispatcher_ready: Arc<AtomicBool>,
    pub feed_ready: Arc<AtomicBool>,
    pub meter: Arc<Meter>,
    pub feed: Arc<Feed>,
    tasks: Vec<tokio::task::JoinHandle<()>>,
}

impl Lit {
    /// Both listeners hold assignments: the feed AND the dispatcher.
    pub async fn wait_ready(&self, timeout: Duration) -> bool {
        let deadline = tokio::time::Instant::now() + timeout;
        while tokio::time::Instant::now() < deadline {
            if self.feed_ready.load(Ordering::Relaxed)
                && self.dispatcher_ready.load(Ordering::Relaxed)
            {
                return true;
            }
            tokio::time::sleep(Duration::from_millis(100)).await;
        }
        false
    }

    /// Stopped whole: the flag, then every task joined (bounded).
    pub async fn stop(self) {
        self.stop.store(true, Ordering::Relaxed);
        for t in self.tasks {
            let _ = tokio::time::timeout(Duration::from_secs(15), t).await;
        }
    }
}

/// Light the bridge: the ground ensured at birth, the kinds and the masters
/// seeded, the door bound, then the relay · the dispatcher · the feed as
/// standing tasks. `port` 0 picks a free one (tests).
pub async fn light(cfg: Config) -> Result<Lit, RoadError> {
    let w = cfg.world.clone();
    let mut g = Ground::connect(&w.pg_dsn).await?;
    g.ensure_all().await?;
    markers_live::seed(&g, &w.scope).await?;
    let masters = proof_live::seed_masters(&mut g, &w, &cfg.masters).await?;
    if !masters.is_empty() {
        eprintln!(
            "masters declared from SPINE_MASTERS: {}",
            masters.join(", ")
        );
    }
    let listener = tokio::net::TcpListener::bind(("127.0.0.1", cfg.port))
        .await
        .map_err(|e| RoadError::Refused(format!("the door could not bind :{} — {e}", cfg.port)))?;
    let port = listener.local_addr().map(|a| a.port()).unwrap_or(cfg.port);
    let stop = Arc::new(AtomicBool::new(false));
    let dispatcher_ready = Arc::new(AtomicBool::new(false));
    let feed_ready = Arc::new(AtomicBool::new(false));
    let feed = Arc::new(Feed::new(1024));
    let meter = Arc::new(Meter::default());
    let group = dispatcher::group_per_life();
    let app = Arc::new(App {
        cfg: cfg.clone(),
        feed: feed.clone(),
        meter: meter.clone(),
        group: group.clone(),
        port,
    });
    let mut tasks = Vec::new();
    // the relay
    {
        let (w, stop) = (w.clone(), stop.clone());
        tasks.push(tokio::spawn(async move {
            while !stop.load(Ordering::Relaxed) {
                match Ground::connect(&w.pg_dsn).await {
                    Ok(g) => {
                        if let Err(e) = dispatcher::run_relay(&g, &w, stop.clone()).await {
                            eprintln!("the relay fell: {e}");
                        }
                    }
                    Err(e) => eprintln!("the relay could not reach the ground: {e}"),
                }
                if !stop.load(Ordering::Relaxed) {
                    tokio::time::sleep(Duration::from_millis(500)).await;
                }
            }
        }));
    }
    // the dispatcher — a group per life; stands again after a rail's refusal
    {
        let (w, stop, ready, meter, group) = (
            w.clone(),
            stop.clone(),
            dispatcher_ready.clone(),
            meter.clone(),
            group.clone(),
        );
        tasks.push(tokio::spawn(async move {
            while !stop.load(Ordering::Relaxed) {
                match Ground::connect(&w.pg_dsn).await {
                    Ok(mut g) => {
                        if let Err(e) = dispatcher::run_dispatcher(
                            &mut g,
                            &w,
                            &group,
                            stop.clone(),
                            ready.clone(),
                            meter.clone(),
                        )
                        .await
                        {
                            eprintln!("the dispatcher fell: {e}");
                        }
                    }
                    Err(e) => eprintln!("the dispatcher could not reach the ground: {e}"),
                }
                if !stop.load(Ordering::Relaxed) {
                    tokio::time::sleep(Duration::from_millis(500)).await;
                }
            }
        }));
    }
    // the feed
    {
        let (w, stop, ready, feed) = (w.clone(), stop.clone(), feed_ready.clone(), feed.clone());
        let group = format!("glass-feed-{port}");
        tasks.push(tokio::spawn(async move {
            while !stop.load(Ordering::Relaxed) {
                if let Err(e) = feed::consume_rail(
                    feed.clone(),
                    &w,
                    &FEED_TOPICS,
                    &group,
                    stop.clone(),
                    ready.clone(),
                )
                .await
                {
                    eprintln!("the feed fell: {e}");
                }
                if !stop.load(Ordering::Relaxed) {
                    tokio::time::sleep(Duration::from_millis(500)).await;
                }
            }
        }));
    }
    // the door
    {
        let stop = stop.clone();
        let router = router(app);
        tasks.push(tokio::spawn(async move {
            let shutdown = async move {
                while !stop.load(Ordering::Relaxed) {
                    tokio::time::sleep(Duration::from_millis(100)).await;
                }
            };
            if let Err(e) = axum::serve(listener, router)
                .with_graceful_shutdown(shutdown)
                .await
            {
                eprintln!("the door fell: {e}");
            }
        }));
    }
    Ok(Lit {
        port,
        group,
        stop,
        dispatcher_ready,
        feed_ready,
        meter,
        feed,
        tasks,
    })
}

fn router(app: Arc<App>) -> Router {
    Router::new()
        .route("/", get(page))
        .route("/index.html", get(page))
        .route("/feed", get(feed_door))
        .route("/health", get(health))
        .route("/shadow", get(shadow))
        .route("/ask/:id", get(ask_door))
        .route("/ask", post(ask_post))
        .route("/asks", get(asks_door))
        .route("/residents", get(residents_door))
        .route("/crew", get(crew_door))
        .route("/sessions", get(sessions_get).post(sessions_post))
        .route("/session/:id", get(session_door))
        .route("/proof", get(proof_door))
        .route("/analyzer", get(analyzer_door))
        .route("/services", get(services_door))
        .route("/intentions", get(intentions_door))
        .route("/markers", get(markers_door))
        .route("/markers/kinds", get(markers_kinds))
        .route("/confirm", post(confirm_post))
        .route("/enroll", post(enroll_post))
        .route("/enroll/confirm", post(enroll_confirm_post))
        .fallback(|| async { StatusCode::NOT_FOUND })
        .with_state(app)
}

type Q = Query<HashMap<String, String>>;

/// The door's JSON answer, with the headers the Python handler sends.
fn answer(code: u16, v: Value) -> Response {
    (
        StatusCode::from_u16(code).unwrap_or(StatusCode::INTERNAL_SERVER_ERROR),
        [
            (header::CONTENT_TYPE, "application/json"),
            (header::ACCESS_CONTROL_ALLOW_ORIGIN, "*"),
        ],
        v.to_string(),
    )
        .into_response()
}

/// Every refusal at a door, by its face: the one face (403), a refusal in
/// words (400), a door not yet served (501), a rail's fall (500).
fn refuse(e: RoadError) -> Response {
    match e {
        RoadError::NotConfirmed { .. } => answer(403, one_face()),
        RoadError::Refused(w) => answer(400, json!({"error": w})),
        RoadError::NotYet(w) => answer(501, json!({"error": w})),
        RoadError::Rail(r) => answer(500, json!({"error": r.to_string()})),
    }
}

async fn ground(app: &App) -> Result<Ground, RoadError> {
    Ok(Ground::connect(&app.cfg.world.pg_dsn).await?)
}

fn scope(app: &App) -> &str {
    &app.cfg.world.scope
}

/// `str(p.get(k) or default)` — Python's door idiom.
fn s_or<'a>(p: &'a Value, k: &str, default: &'a str) -> String {
    let v = &p[k];
    if crate::py::truthy(v) {
        python_str(v)
    } else {
        default.to_string()
    }
}

/// `str(p.get(k) or "") or None`.
fn s_opt(p: &Value, k: &str) -> Option<String> {
    let v = s_or(p, k, "");
    if v.is_empty() {
        None
    } else {
        Some(v)
    }
}

fn body_json(body: &Bytes) -> Value {
    if body.is_empty() {
        return json!({});
    }
    serde_json::from_slice(body).unwrap_or(json!({}))
}

async fn page(State(app): State<Arc<App>>) -> Response {
    match std::fs::read(&app.cfg.glass) {
        Ok(html) => (
            StatusCode::OK,
            [(header::CONTENT_TYPE, "text/html; charset=utf-8")],
            html,
        )
            .into_response(),
        Err(e) => answer(
            500,
            json!({"error": format!("the glass is not at {} — {e}", app.cfg.glass.display())}),
        ),
    }
}

fn frame(n: &Value) -> Event {
    Event::default()
        .id(n["rev"].as_u64().unwrap_or(0).to_string())
        .data(n.to_string())
}

async fn feed_door(State(app): State<Arc<App>>, headers: HeaderMap) -> Response {
    let rx = app.feed.subscribe();
    let last = headers
        .get("last-event-id")
        .and_then(|v| v.to_str().ok())
        .and_then(|v| v.trim().parse::<u64>().ok());
    let missed: Vec<Event> = match last {
        None => Vec::new(),
        Some(rev) => match app.feed.since(rev) {
            None => vec![Event::default().event("resync").data(
                r#"{"reason": "the gap outlived the ring - fetch a fresh snapshot through the doors"}"#,
            )],
            Some(ns) => ns.iter().map(frame).collect(),
        },
    };
    let live = BroadcastStream::new(rx)
        .filter_map(|r| r.ok())
        .map(|n| frame(&n));
    let stream = tokio_stream::iter(missed)
        .chain(live)
        .map(Ok::<_, Infallible>);
    Sse::new(stream)
        .keep_alive(
            KeepAlive::new()
                .interval(Duration::from_secs(15))
                .text("keepalive"),
        )
        .into_response()
}

async fn health(State(app): State<Arc<App>>) -> Response {
    answer(
        200,
        json!({"rev": app.feed.rev(), "clients": app.feed.clients()}),
    )
}

/// Rust-only: the dispatcher's meter — what this life dispatched, absorbed, skipped.
async fn shadow(State(app): State<Arc<App>>) -> Response {
    let (d, a, s) = app.meter.read();
    answer(
        200,
        json!({
            "port": app.port, "scope": scope(&app), "ns": app.cfg.world.ns,
            "group": app.group, "consumer": dispatcher::CONSUMER,
            "dispatched": d, "absorbed": a, "skipped": s,
            "human_zone": app.cfg.human_zone, "glass": app.cfg.glass.display().to_string(),
        }),
    )
}

async fn ask_door(State(app): State<Arc<App>>, Path(id): Path<String>) -> Response {
    let out = async {
        let g = ground(&app).await?;
        asks::ask_view(&g, scope(&app), &id).await
    }
    .await;
    match out {
        Ok(Some(v)) => answer(200, v),
        Ok(None) => answer(404, json!({"error": "no such ask"})),
        Err(e) => refuse(e),
    }
}

async fn asks_door(State(app): State<Arc<App>>) -> Response {
    let out = async {
        let g = ground(&app).await?;
        asks::asks_view(&g, scope(&app), 30).await
    }
    .await;
    match out {
        Ok(v) => answer(200, json!({"asks": v})),
        Err(e) => refuse(e),
    }
}

async fn residents_door(State(app): State<Arc<App>>) -> Response {
    let out = async {
        let g = ground(&app).await?;
        sessions::residents_view(&g, scope(&app)).await
    }
    .await;
    match out {
        Ok(v) => answer(200, json!({"residents": v})),
        Err(e) => refuse(e),
    }
}

async fn crew_door(State(app): State<Arc<App>>) -> Response {
    let out = async {
        let g = ground(&app).await?;
        sessions::crew_view(&g, scope(&app)).await
    }
    .await;
    match out {
        Ok(v) => answer(200, json!({"crew": v})),
        Err(e) => refuse(e),
    }
}

async fn sessions_get(State(app): State<Arc<App>>, Query(q): Q) -> Response {
    let person = q
        .get("person")
        .cloned()
        .filter(|p| !p.is_empty())
        .unwrap_or_else(|| PERSON_DEFAULT.into());
    let out = async {
        let g = ground(&app).await?;
        sessions::sessions_view(&g, scope(&app), &person, 30).await
    }
    .await;
    match out {
        Ok(v) => answer(200, json!({"sessions": v})),
        Err(e) => refuse(e),
    }
}

async fn sessions_post(State(app): State<Arc<App>>, body: Bytes) -> Response {
    let p = body_json(&body);
    let person = s_or(&p, "person", PERSON_DEFAULT);
    let title = s_opt(&p, "title");
    let opt_out = crate::py::truthy(&p["opt_out"]);
    let out = async {
        let g = ground(&app).await?;
        sessions::open_session(&g, scope(&app), &person, title.as_deref(), opt_out).await
    }
    .await;
    match out {
        Ok(sid) => answer(201, json!({"session_id": sid})),
        Err(e) => refuse(e),
    }
}

async fn session_door(State(app): State<Arc<App>>, Path(id): Path<String>) -> Response {
    let out = async {
        let g = ground(&app).await?;
        sessions::session_view(&g, scope(&app), &id).await
    }
    .await;
    match out {
        Ok(Some(v)) => answer(200, v),
        Ok(None) => answer(404, json!({"error": "no such session"})),
        Err(e) => refuse(e),
    }
}

async fn proof_door(State(app): State<Arc<App>>, Query(q): Q) -> Response {
    let person = q
        .get("person")
        .cloned()
        .filter(|p| !p.is_empty())
        .unwrap_or_else(|| PERSON_DEFAULT.into());
    let out = async {
        let g = ground(&app).await?;
        let enrolled = proof_live::enrolled(&g, scope(&app), &person).await?;
        let masters = proof_live::masters(&g, scope(&app)).await?;
        Ok::<_, RoadError>(json!({"person": person, "enrolled": enrolled, "masters": masters}))
    }
    .await;
    match out {
        Ok(v) => answer(200, v),
        Err(e) => refuse(e),
    }
}

async fn analyzer_door(State(app): State<Arc<App>>, Query(q): Q) -> Response {
    let out = async {
        let g = ground(&app).await?;
        match q.get("origin").filter(|o| !o.is_empty()) {
            Some(root) => markers_live::origin(&g, scope(&app), root).await,
            None => Ok(json!({"origins": markers_live::origins(&g, scope(&app), 60).await?})),
        }
    }
    .await;
    match out {
        Ok(v) => answer(200, v),
        Err(e) => refuse(e),
    }
}

async fn services_door(State(app): State<Arc<App>>, Query(q): Q) -> Response {
    let kind = q.get("kind").cloned().filter(|k| !k.is_empty());
    if let Some(k) = &kind {
        if !SERVICE_KINDS.contains(&k.as_str()) {
            return answer(
                400,
                json!({"error": format!("a kind is one of {}", SERVICE_KINDS.join(", "))}),
            );
        }
    }
    let out = async {
        let g = ground(&app).await?;
        sessions::services_door(&g, scope(&app), kind.as_deref()).await
    }
    .await;
    match out {
        Ok(v) => answer(200, v),
        Err(e) => refuse(e),
    }
}

async fn intentions_door(State(app): State<Arc<App>>, Query(q): Q) -> Response {
    let out = async {
        let g = ground(&app).await?;
        intent_live::listing(
            &g,
            scope(&app),
            q.get("serves").map(String::as_str),
            q.get("kind").map(String::as_str),
            60,
        )
        .await
    }
    .await;
    match out {
        Ok(v) => answer(200, json!({"intentions": v})),
        Err(e) => refuse(e),
    }
}

async fn markers_door(State(app): State<Arc<App>>, Query(q): Q) -> Response {
    let out = async {
        let g = ground(&app).await?;
        let sc = scope(&app);
        if let Some(root) = q.get("root").filter(|r| !r.is_empty()) {
            let t =
                markers_live::with_words(&g, markers_live::tree(&g, sc, root, 500).await?).await?;
            return Ok(json!({"root": root, "tree": t}));
        }
        if let Some(from) = q.get("from").filter(|r| !r.is_empty()) {
            let a =
                markers_live::with_words(&g, markers_live::ancestry(&g, sc, from).await?).await?;
            return Ok(json!({"from": from, "ancestry": a}));
        }
        let m = markers_live::stream(
            &g,
            sc,
            q.get("kind").map(String::as_str),
            q.get("group").map(String::as_str),
            60,
        )
        .await?;
        Ok::<_, RoadError>(json!({"markers": m}))
    }
    .await;
    match out {
        Ok(v) => answer(200, v),
        Err(e) => refuse(e),
    }
}

async fn markers_kinds(State(app): State<Arc<App>>) -> Response {
    let out = async {
        let g = ground(&app).await?;
        markers_live::kinds(&g, scope(&app)).await
    }
    .await;
    match out {
        Ok(v) => answer(200, json!({"kinds": v})),
        Err(e) => refuse(e),
    }
}

/// `POST /ask` — the glass's write, law for law with the Python door: the
/// words validated, the kind read (P23: a typed prefix wins, then the chip's
/// word, then the words' own read), an intention DECLARED, a name at the
/// head selecting its body (W7), then `submit_ask`.
async fn ask_post(State(app): State<Arc<App>>, body: Bytes) -> Response {
    let p = body_json(&body);
    let text = s_or(&p, "text", "").trim().to_string();
    if text.is_empty() {
        return answer(400, json!({"error": "an empty ask asks nothing"}));
    }
    let person = s_or(&p, "person", PERSON_DEFAULT);
    let to: Option<Vec<String>> = if crate::py::truthy(&p["to"]) {
        match p["to"].as_array() {
            Some(a) if !a.is_empty() && a.iter().all(Value::is_string) => Some(
                a.iter()
                    .map(|t| t.as_str().unwrap_or_default().to_string())
                    .collect(),
            ),
            _ => {
                return answer(
                    400,
                    json!({"error": "'to' names residents as a list of names"}),
                )
            }
        }
    } else {
        None
    };
    let window: Option<(String, String)> = if crate::py::truthy(&p["window"]) {
        let w = &p["window"];
        if w.is_object() && crate::py::truthy(&w["from"]) && crate::py::truthy(&w["to"]) {
            Some((python_str(&w["from"]), python_str(&w["to"])))
        } else {
            return answer(400, json!({"error": "'window' is {from, to} in ISO time"}));
        }
    } else {
        None
    };
    let session = s_opt(&p, "session");
    let zone = s_opt(&p, "zone");
    let rw = read_words(&text);
    let kind = if rw.pinned {
        rw.kind.clone()
    } else {
        let chip = s_or(&p, "kind", "");
        if chip.is_empty() {
            rw.kind.clone()
        } else {
            chip
        }
    };
    if !ASK_KINDS.contains(&kind.as_str()) {
        return answer(
            400,
            json!({"error": "'kind' is thought, objective, or intention"}),
        );
    }
    let text = if rw.pinned { rw.words.clone() } else { text };
    let parent = s_opt(&p, "parent");
    let out = async {
        let mut g = ground(&app).await?;
        let w = &app.cfg.world;
        if kind == "intention" {
            let r2 = read_words(&format!("intention: {text}"));
            let interests = if crate::py::truthy(&p["interests"]) {
                p["interests"]
                    .as_array()
                    .map(|a| a.iter().map(python_str).collect())
                    .unwrap_or_default()
            } else {
                r2.interests.clone().unwrap_or_default()
            };
            let every_s = if crate::py::truthy(&p["every_s"]) {
                p["every_s"]
                    .as_i64()
                    .or_else(|| p["every_s"].as_f64().map(|f| f as i64))
            } else {
                r2.every_s
            };
            let serves = if crate::py::truthy(&p["serves"]) {
                python_str(&p["serves"])
            } else {
                r2.serves.clone().unwrap_or_else(|| "business".into())
            };
            let made = intent_live::declare(
                &mut g,
                w,
                Declare {
                    words: text.clone(),
                    serves,
                    kind: "human".into(),
                    by: person.clone(),
                    interests,
                    planner: "planner".into(),
                    runner: to.as_ref().and_then(|t| t.first().cloned()),
                    every_s,
                    gates: None,
                },
            )
            .await?;
            return Ok((201, json!({"intention": made})));
        }
        let to = asks::address_to(&g, &w.scope, &text, to).await?;
        let out = asks::submit_ask(
            &mut g,
            w,
            Submit {
                text,
                person,
                to,
                window,
                session,
                parent_marker: parent,
                kind: Some(kind),
                zone,
            },
        )
        .await?;
        Ok::<_, RoadError>((201, out.to_value()))
    }
    .await;
    match out {
        Ok((code, v)) => answer(code, v),
        Err(e) => refuse(e),
    }
}

async fn confirm_post(State(app): State<Arc<App>>, body: Bytes) -> Response {
    let p = body_json(&body);
    let ask_id = s_or(&p, "ask_id", "");
    let approve = crate::py::truthy(&p["approve"]);
    let by = if crate::py::truthy(&p["by"]) {
        python_str(&p["by"])
    } else {
        s_or(&p, "person", PERSON_DEFAULT)
    };
    let code = s_opt(&p, "code");
    let out = async {
        let mut g = ground(&app).await?;
        asks::confirm_ask(
            &mut g,
            &app.cfg.world,
            &ask_id,
            approve,
            &by,
            code.as_deref(),
        )
        .await
    }
    .await;
    match out {
        Ok(v) => answer(202, v),
        Err(e) => refuse(e),
    }
}

async fn enroll_post(State(app): State<Arc<App>>, body: Bytes) -> Response {
    let p = body_json(&body);
    let person = s_or(&p, "person", PERSON_DEFAULT);
    let code = s_opt(&p, "code");
    let out = async {
        let mut g = ground(&app).await?;
        proof_live::enroll(&mut g, &app.cfg.world, &person, code.as_deref()).await
    }
    .await;
    match out {
        Ok(v) => answer(201, v),
        Err(e) => refuse(e),
    }
}

async fn enroll_confirm_post(State(app): State<Arc<App>>, body: Bytes) -> Response {
    let p = body_json(&body);
    let person = s_or(&p, "person", PERSON_DEFAULT);
    let code = s_or(&p, "code", "");
    let out = async {
        let mut g = ground(&app).await?;
        proof_live::confirm_enrollment(&mut g, &app.cfg.world, &person, Some(&code)).await
    }
    .await;
    match out {
        Ok(v) => answer(200, v),
        Err(e) => refuse(e),
    }
}
