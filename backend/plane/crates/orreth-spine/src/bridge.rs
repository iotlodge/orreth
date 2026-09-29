// PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp3, the ask road · 2026-09-22
// Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch row 4, PANEL sp3: THE POOL at every door (`ground` borrows a line) · THE CLOCK middleware · 2026-09-28
// Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp4, the loops: the schedule and intent loops as tasks · /monitor · /schedules · /harness · /intentions/stop|restart · 2026-09-23
// Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp5, memory and the export · 2026-09-24
// Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch walk #13 cures: W51 a roll is a fact the feed carries · W52 the digest in the human's zone · THE GUIDE door · 2026-09-24
// Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp6, the bodies' seam: the crew spawned and governed · /delta · /bodies · the Stable's doors · the shelf's doors · the harness over the rail · the keepers' beats · 2026-09-24
// Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp7, cells: the cell — the home at light · the /world door · 2026-09-25
// Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp8, the profile doors (W58) · 2026-09-26
// Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch row 4, PANEL sp2: the fact door `/fact/<message_id>` · the presence sweep's loop · 2026-09-28
// Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch row 4, re-base sp1: POISON-PARKING — the dispatcher parks a poison with its evidence and HOLDS at it until a person advances it · 2026-09-28
// Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch row 4, the perf cure before sp2 (JB's word 2026-09-29): the RETENTION beat (hourly, one kernel) · 2026-09-29
//! The Rust bridge — the doors and the feed of `orreth_spine.glass` +
//! `bridgefeed` on axum, lit in SHADOW on :4601 beside the Python Bridge on
//! :4600, both on one ground. It serves the SAME page (`spine/glass/index.html`
//! read from disk — `ORRETH_GLASS`, else the crate's `../../../../spine/glass/
//! index.html`), the same JSON shapes and status codes at every door it has
//! ported, and the same SSE feed (`/feed`: `id: <rev>` + `data: <notice>`,
//! `event: resync` when the gap outlived the ring, `: keepalive` every 15 s),
//! so the one page works unchanged against either port. Since P7 sp6 it SEATS
//! THE CREW: every seat of `spine/crew.v0.json` spawned as its own Python
//! process (`orreth_spine.body`), governed — restarted, parked, stopped whole
//! — by [`crate::bodies`]; `SPINE_BODIES=none` leaves the seats to the Python
//! Bridge beside it. It relays, it dispatches, it feeds, it answers — and
//! since P7 sp4 it BEATS: the scheduler's tick and
//! the intent rail's turn run as standing tasks, each beat CLAIMED on the
//! ground first (`beat` — the loops' shadow law), so two kernels on one world
//! never tick or turn it at once. The kernel's Resiliency intention is
//! declared at boot (once per world; one at rest stays at rest).
//!
//! Doors ported: `GET /` · `/feed` · `/health` · `/ask/<id>` · `/asks` ·
//! `/residents` · `/crew` · `/sessions` · `/session/<id>` · `/proof` ·
//! `/analyzer[?origin=]` · `/services[?kind=]` · `/intentions` · `/markers`
//! · `/markers/kinds` · `/monitor` · `/schedules/<runner>` · `/harness` ·
//! `/shadow` (Rust-only: the dispatcher's meter); `POST /ask` · `/confirm` ·
//! `/enroll` · `/enroll/confirm` · `/sessions` · `/schedules` ·
//! `/schedules/rest` · `/intentions/stop` · `/intentions/restart`; P7 sp6:
//! `POST /harness/run` · `/harness/ab` (the run over the rail) · `/delta` (a
//! body's words as they form) · `GET /bodies` · `POST /bodies/restart` · the
//! Stable's `/minds…` · the shelf's `POST /services…`. Every other door
//! answers 404 with no body, as the Python handler does.
// Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp8 row 3, THE GATE (a): the seat read at every door by a tower layer — the person from the token, never the body; the origin closed; the knock ceiling per person; the seat doors · 2026-09-26
// Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp8 walk #19, W71: the shelf's restore door routes every kind through restore_mind — one restore law · 2026-09-27

use crate::asks::{self, Submit, FEED_TOPICS};
use crate::bodies::{self, Bodies};
use crate::dispatcher::{self, Meter};
use crate::feed::{self, Feed};
use crate::gateway::Gateway;
use crate::ground::Ground;
use crate::harness;
use crate::intent::{read_words, ASK_KINDS};
use crate::intent_live::{self, Declare};
use crate::markers_live;
use crate::monitor;
use crate::outbox;
use crate::pool::{Line, Pool};
use crate::presence;
use crate::proof::one_face;
use crate::proof_live;
use crate::py::{python_str, truthy};
use crate::scheduler;
use crate::seat;
use crate::seat_live::{self, Seated};
use crate::services::KINDS as SERVICE_KINDS;
use crate::services_live;
use crate::sessions;
use crate::stable_live;
use crate::world::{RoadError, World};
use crate::{desk, desk_live};
use axum::body::Bytes;
use axum::extract::{ConnectInfo, Path, Query, State};
use axum::http::{header, HeaderMap, StatusCode};
use axum::middleware::{self, Next};
use axum::response::sse::{Event, KeepAlive, Sse};
use axum::response::{IntoResponse, Response};
use axum::routing::{get, post};
use axum::Extension;
use axum::Router;
use serde_json::{json, Value};
use std::collections::HashMap;
use std::convert::Infallible;
use std::net::SocketAddr;
use std::path::PathBuf;
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::Arc;
use std::time::Duration;
use tokio_stream::wrappers::BroadcastStream;
use tokio_stream::StreamExt;

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
    /// P7 sp6: does this kernel seat the crew (`SPINE_BODIES`, default crew; `none` beside the Python Bridge)?
    pub bodies: bool,
    /// Tests only: the bodies mint ephemeral selves (`SPINE_BODY_EPHEMERAL`).
    pub ephemeral: bool,
    /// The spine home (`ORRETH_SPINE`, else beside the crate) — the crew manifest, the templates, the golden sets.
    pub spine: PathBuf,
    /// P7 sp7: the cell this kernel IS (`SPINE_CELL`, else `local`) — the universe's home.
    pub cell: String,
    /// P7 sp7: the peers this cell names (`SPINE_PEERS`: `name=door,…`).
    pub peers: Vec<crate::cells::Peer>,
    /// The kernel self's seed directory (`None`: `SPINE_KERNEL_HOME`, else `ORRETH_HOME/kernel`) — a proof stands two kernels in one process.
    pub kernel_home: Option<PathBuf>,
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
            bodies: bodies::wanted(),
            ephemeral: std::env::var("SPINE_BODY_EPHEMERAL")
                .ok()
                .is_some_and(|v| !v.is_empty()),
            spine: bodies::spine_dir(),
            cell: crate::cells_live::cell_here(),
            peers: crate::cells::peers_from(std::env::var("SPINE_PEERS").ok().as_deref()),
            kernel_home: None,
        }
    }
}

struct App {
    cfg: Config,
    kernel: crate::kernel_self::KernelSelf, // P7 sp5: the kernel's own self — the export's signer
    cell: String,                           // P7 sp7: the cell this kernel IS — the universe's home
    seam: Arc<crate::seam::Seam>,           // P7 sp7: the seam to the peers this cell names
    feed: Arc<Feed>,
    meter: Arc<Meter>,
    group: String,
    port: u16,
    bodies: Option<Arc<Bodies>>, // P7 sp6: the crew this kernel seats and governs
    gateway: Gateway,            // THE GATEWAY's doors from the kernel's side
    templates: HashMap<String, Value>, // the seats' templates by body name (the crew card's LLM line)
    gate: seat_live::Ceilings, // P7 sp8 row 3: the knock ceiling at every door (per person · per address)
    pool: Arc<Pool>, // row 4, panel sp3: THE POOL — the doors' lines to the ground, borrowed per knock
    lit_at: String, // JB's ask 2026-09-28: the version whisper — when this kernel was lit, said by the health door
    schema: crate::ground::Migration, // re-base sp1 (lock 2): what the birth found on the ground and what it did
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
    /// P7 sp6: the crew this kernel seats — `None` when it seats none.
    pub bodies: Option<Arc<Bodies>>,
    tasks: Vec<tokio::task::JoinHandle<()>>,
    kafka: String,
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

    /// Stopped whole: the bodies first (SIGINT, a bounded wait), then the
    /// flag, then every task joined (bounded).
    pub async fn stop(self) {
        if let Some(b) = &self.bodies {
            b.stop().await;
        }
        self.stop.store(true, Ordering::Relaxed);
        for t in self.tasks {
            let _ = tokio::time::timeout(Duration::from_secs(15), t).await;
        }
        // the perf cure (2026-09-29): the group-per-life law leaves no ghost — this life's groups go with it
        let feed_group = format!("glass-feed-{}", self.port);
        let _ = tokio::time::timeout(
            Duration::from_secs(10),
            crate::events::delete_groups(&self.kafka, &[self.group.as_str(), feed_group.as_str()]),
        )
        .await;
    }
}

/// Light the bridge: the ground ensured at birth, the kinds and the masters
/// seeded, the door bound, then the relay · the dispatcher · the feed as
/// standing tasks. `port` 0 picks a free one (tests).
pub async fn light(cfg: Config) -> Result<Lit, RoadError> {
    let w = cfg.world.clone();
    let mut g = Ground::connect(&w.pg_dsn).await?;
    let schema = g.ensure_all().await?; // THE MIGRATOR: one writer; the rest wait and verify
    eprintln!("  [kernel] {}", schema.words());
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
    let kernel_home = cfg
        .kernel_home
        .clone()
        .unwrap_or_else(crate::kernel_self::KernelSelf::home);
    let kernel = match crate::kernel_self::KernelSelf::load(&kernel_home) {
        Ok(k) => k,
        Err(e) => {
            eprintln!("the kernel's self could not be read ({e}) — an ephemeral self this life");
            crate::kernel_self::KernelSelf::ephemeral()
        }
    };
    let gateway = Gateway::from_env();
    // P7 sp7: THE CELL — the universe's home settled at light, said once as a fact; a kernel of
    // another cell may not light over a universe homed here (the fencing law at the door)
    let cell = cfg.cell.clone();
    let home = crate::cells_live::home(
        &mut g,
        &w.scope,
        &cell,
        &kernel.did(),
        &format!("http://127.0.0.1:{port}"),
    )
    .await?;
    eprintln!(
        "{} stands in cell {cell} at epoch {} — kept by {}",
        w.scope,
        home["epoch"],
        kernel.did()
    );
    // P7 sp7: THE SEAM — signed by this kernel's self; the peers this cell names
    let seam = Arc::new(crate::seam::Seam::new(
        &cell,
        cfg.peers.clone(),
        kernel.clone(),
        &format!("http://127.0.0.1:{port}"),
        w.clone(),
        &cfg.human_zone,
    ));
    if !cfg.peers.is_empty() {
        eprintln!(
            "cell {cell} names its peers: {}",
            cfg.peers
                .iter()
                .map(|p| format!("{} at {}", p.cell, p.door))
                .collect::<Vec<_>>()
                .join(" · ")
        );
    }
    // P7 sp6: THE CREW — every seat a process this kernel spawns and governs
    let bodies_arc: Option<Arc<Bodies>> = if cfg.bodies {
        let seats = bodies::crew(&cfg.spine)?;
        Some(Bodies::new(
            seats,
            cfg.spine.clone(),
            w.clone(),
            format!("http://127.0.0.1:{port}"),
            cfg.ephemeral,
        ))
    } else {
        None
    };
    // the seats' templates by name — read from the one manifest whether or not this kernel
    // spawns the crew, so the crew card's LLM line reads the same on both doors (rule 7)
    let templates = match &bodies_arc {
        Some(b) => b.templates(),
        None => bodies::crew(&cfg.spine)
            .map(|seats| {
                seats
                    .into_iter()
                    .map(|s| (s.name, s.template_json))
                    .collect()
            })
            .unwrap_or_default(),
    };
    let app = Arc::new(App {
        cfg: cfg.clone(),
        kernel,
        cell,
        seam: seam.clone(),
        feed: feed.clone(),
        meter: meter.clone(),
        group: group.clone(),
        port,
        bodies: bodies_arc.clone(),
        gateway: gateway.clone(),
        templates,
        gate: seat_live::Ceilings::new(),
        pool: Pool::new(&w.pg_dsn, crate::pool::ceiling_from_env()),
        lit_at: crate::envelope::now_iso(),
        schema,
    });
    let mut tasks = Vec::new();
    // the crew: the benches swept, the boot rite once, the kernel's duties declared, then every seat spawned
    if let Some(b) = bodies_arc.clone() {
        let (w2, stop2, gw2) = (w.clone(), stop.clone(), gateway.clone());
        tasks.push(tokio::spawn(async move {
            if let Err(e) = b.sweep_benches().await {
                eprintln!("the benches could not be swept: {e}");
            }
            if stop2.load(Ordering::Relaxed) {
                return;
            }
            // P7 sp8 row 2: the rite is this kernel's own — no Python is spawned to seed the shelf
            let ready = gw2.ready().await;
            if let Err(e) = b.seed_shelf(if ready { Some(&gw2) } else { None }).await {
                eprintln!("the boot rite could not run: {e}");
            }
            match Ground::connect(&w2.pg_dsn).await {
                Ok(mut g) => match b.declare_duties(&mut g).await {
                    Ok(names) if !names.is_empty() => eprintln!(
                        "the kernel's harness duty declared for: {}",
                        names.join(", ")
                    ),
                    Ok(_) => {}
                    Err(e) => eprintln!("the kernel's duties could not be declared: {e}"),
                },
                Err(e) => eprintln!("the kernel's duties could not reach the ground: {e}"),
            }
            if !stop2.load(Ordering::Relaxed) {
                b.spawn_all();
                eprintln!(
                    "the crew is seated: {} bodies spawned as processes",
                    b.seats.len()
                );
            }
        }));
        // the keepers' beats (P6.5 sp2 · sp3), on the kernel that holds the keepers' bodies
        let (w3, stop3, gw3) = (w.clone(), stop.clone(), gateway.clone());
        tasks.push(tokio::spawn(async move {
            let mut next_tool = tokio::time::Instant::now()
                + Duration::from_secs_f64(crate::mcp_live::tool_check_s());
            let mut next_mind =
                tokio::time::Instant::now() + Duration::from_secs_f64(stable_live::mind_check_s());
            while !stop3.load(Ordering::Relaxed) {
                sleep_unless_stopped(&stop3, Duration::from_secs(5)).await;
                if stop3.load(Ordering::Relaxed) {
                    break;
                }
                let now = tokio::time::Instant::now();
                if now >= next_tool {
                    next_tool = now + Duration::from_secs_f64(crate::mcp_live::tool_check_s());
                    keeper_beat(&w3, "toolkeeper", None).await;
                }
                if now >= next_mind {
                    next_mind = now + Duration::from_secs_f64(stable_live::mind_check_s());
                    keeper_beat(&w3, "stablekeeper", Some(&gw3)).await;
                }
            }
        }));
    }
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
    // P7 sp7: the seam's beat — the peers greeted, what waits carried, the answers carried home
    {
        let (seam, stop) = (seam.clone(), stop.clone());
        tasks.push(tokio::spawn(async move {
            seam.run(&stop).await;
        }));
    }
    // the scheduler's beat — every 5 s, claimed on the ground first
    {
        let (w, stop, zone) = (w.clone(), stop.clone(), cfg.human_zone.clone());
        tasks.push(tokio::spawn(async move {
            while !stop.load(Ordering::Relaxed) {
                match Ground::connect(&w.pg_dsn).await {
                    Ok(mut g) => {
                        while !stop.load(Ordering::Relaxed) {
                            if let Err(e) = scheduler::tick(&mut g, &w, &zone).await {
                                eprintln!("the scheduler's beat stumbled: {e}");
                                if matches!(e, RoadError::Rail(_)) {
                                    break; // stand again on a fresh connection
                                }
                            }
                            sleep_unless_stopped(&stop, Duration::from_secs(5)).await;
                        }
                    }
                    Err(e) => eprintln!("the scheduler could not reach the ground: {e}"),
                }
                if !stop.load(Ordering::Relaxed) {
                    tokio::time::sleep(Duration::from_millis(500)).await;
                }
            }
        }));
    }
    // row 4, panel sp2: the presence sweep — every 5 s; a lease that lapses or is seated
    // again becomes a fact on the feed (the note lives on the ground: no beat claim needed,
    // two kernels race for the row and one wins it)
    {
        let (w, stop) = (w.clone(), stop.clone());
        tasks.push(tokio::spawn(async move {
            while !stop.load(Ordering::Relaxed) {
                match Ground::connect(&w.pg_dsn).await {
                    Ok(mut g) => {
                        while !stop.load(Ordering::Relaxed) {
                            if let Err(e) = presence::sweep(&mut g, &w).await {
                                eprintln!("the presence sweep stumbled: {e}");
                                if matches!(e, RoadError::Rail(_)) {
                                    break; // stand again on a fresh connection
                                }
                            }
                            sleep_unless_stopped(&stop, Duration::from_secs(presence::SWEEP_S))
                                .await;
                        }
                    }
                    Err(e) => eprintln!("the presence sweep could not reach the ground: {e}"),
                }
                if !stop.load(Ordering::Relaxed) {
                    tokio::time::sleep(Duration::from_millis(500)).await;
                }
            }
        }));
    }
    // RETENTION (the perf cure, 2026-09-29): once an hour, under the `retention` beat, the outbox's
    // published rows past the keep window are pruned — the relay's poll stays O(pending) by the
    // partial index, the table stays a queue's size, the fact door keeps its window
    {
        let (w, stop) = (w.clone(), stop.clone());
        tasks.push(tokio::spawn(async move {
            while !stop.load(Ordering::Relaxed) {
                match Ground::connect(&w.pg_dsn).await {
                    Ok(g) => {
                        while !stop.load(Ordering::Relaxed) {
                            match crate::beat::try_beat(&g, &w.scope, "retention").await {
                                Ok(true) => {
                                    match outbox::prune(&g, outbox::keep_days()).await {
                                        Ok(n) if n > 0 => eprintln!(
                                            "  [kernel] retention: {n} published outbox rows older than {} days pruned",
                                            outbox::keep_days()
                                        ),
                                        Ok(_) => {}
                                        Err(e) => eprintln!("the retention sweep stumbled: {e}"),
                                    }
                                    let _ = crate::beat::end_beat(&g, &w.scope, "retention").await;
                                }
                                Ok(false) => {}
                                Err(e) => {
                                    eprintln!("the retention beat could not be claimed: {e}");
                                    break;
                                }
                            }
                            sleep_unless_stopped(&stop, Duration::from_secs(3600)).await;
                        }
                    }
                    Err(e) => eprintln!("the retention sweep could not reach the ground: {e}"),
                }
                if !stop.load(Ordering::Relaxed) {
                    tokio::time::sleep(Duration::from_millis(500)).await;
                }
            }
        }));
    }
    // the intent rail's beat — Resiliency declared at boot, then a turn every 3 s
    {
        let (w, stop) = (w.clone(), stop.clone());
        tasks.push(tokio::spawn(async move {
            while !stop.load(Ordering::Relaxed) {
                match Ground::connect(&w.pg_dsn).await {
                    Ok(mut g) => {
                        let r = crate::intent::resiliency();
                        let mut declared = false;
                        for attempt in 0..20 {
                            match intent_live::declared(
                                &mut g,
                                &w,
                                Declare {
                                    words: r["words"].as_str().unwrap_or_default().into(),
                                    serves: r["serves"].as_str().unwrap_or_default().into(),
                                    kind: "kernel".into(),
                                    by: "the kernel".into(),
                                    interests: vec![crate::intent::WATCH_RED.into()],
                                    planner: "planner".into(),
                                    runner: Some("librarian".into()),
                                    every_s: None,
                                    gates: None,
                                },
                            )
                            .await
                            {
                                Ok(_) => {
                                    declared = true;
                                    break;
                                }
                                Err(e) => {
                                    if attempt == 19 {
                                        eprintln!("the intent rail could not declare at boot: {e}");
                                    }
                                    tokio::time::sleep(Duration::from_millis(300)).await;
                                }
                            }
                        }
                        let _ = declared;
                        while !stop.load(Ordering::Relaxed) {
                            if let Err(e) = intent_live::turn(&mut g, &w).await {
                                eprintln!("the intent rail's turn stumbled: {e}");
                                if matches!(e, RoadError::Rail(_)) {
                                    break;
                                }
                            }
                            sleep_unless_stopped(&stop, Duration::from_secs(3)).await;
                        }
                    }
                    Err(e) => eprintln!("the intent rail could not reach the ground: {e}"),
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
            if let Err(e) = axum::serve(
                listener,
                router.into_make_service_with_connect_info::<SocketAddr>(),
            )
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
        bodies: bodies_arc,
        tasks,
        kafka: w.kafka.clone(),
    })
}

/// One keeper's beat (`BridgeRig._keeper_beat` · `_stable_beat`): under the
/// keeper's DID when the keeper is joined here; its words on the kernel's stderr.
async fn keeper_beat(w: &World, keeper: &str, gw: Option<&Gateway>) {
    let mut g = match Ground::connect(&w.pg_dsn).await {
        Ok(g) => g,
        Err(e) => {
            eprintln!("the {keeper}'s beat could not reach the ground: {e}");
            return;
        }
    };
    let did = match services_live::did_of_body(g.client(), &w.scope, keeper).await {
        Ok(Some(d)) => d,
        Ok(None) => return, // the keeper is not seated here (yet)
        Err(e) => {
            eprintln!("the {keeper}'s beat stumbled: {e}");
            return;
        }
    };
    let out = if keeper == "stablekeeper" {
        let ready = match gw {
            Some(g) => g.ready().await,
            None => false,
        };
        stable_live::keeper_beat(&mut g, w, &did, if ready { gw } else { None }).await
    } else {
        crate::mcp_live::keeper_beat(&mut g, w, &did).await
    };
    match out {
        Ok(v) => {
            let bad: Vec<String> = v["checked"]
                .as_array()
                .map(|a| {
                    a.iter()
                        .filter(|c| c["ok"] == json!(false))
                        .map(|c| python_str(&c["name"]))
                        .collect()
                })
                .unwrap_or_default();
            let proposed: Vec<String> = v["proposed"]
                .as_array()
                .map(|a| {
                    a.iter()
                        .map(|p| format!("{} {}", python_str(&p["kind"]), python_str(&p["name"])))
                        .collect()
                })
                .unwrap_or_default();
            if !bad.is_empty() || !proposed.is_empty() {
                eprintln!(
                    "the {keeper}'s beat: {} checked{}{}",
                    v["checked"].as_array().map(|a| a.len()).unwrap_or(0),
                    if bad.is_empty() {
                        String::new()
                    } else {
                        format!(", UNHEALTHY: {}", bad.join(", "))
                    },
                    if proposed.is_empty() {
                        String::new()
                    } else {
                        format!(", proposed: {}", proposed.join(", "))
                    }
                );
            }
        }
        Err(e) => eprintln!("the {keeper}'s beat stumbled: {e}"),
    }
}

/// A beat's rest, cut short by the stop (so a stop is felt within 100 ms).
async fn sleep_unless_stopped(stop: &AtomicBool, d: Duration) {
    let end = tokio::time::Instant::now() + d;
    while tokio::time::Instant::now() < end && !stop.load(Ordering::Relaxed) {
        tokio::time::sleep(Duration::from_millis(100)).await;
    }
}

fn router(app: Arc<App>) -> Router {
    Router::new()
        .route("/", get(page))
        .route("/index.html", get(page))
        .route("/feed", get(feed_door))
        .route("/health", get(health))
        .route("/shadow", get(shadow))
        .route("/parked", get(parked_door)) // re-base sp1: the poison events held at
        .route("/parked/advance", post(parked_advance)) // … and the person's word to go past one
        .route("/ask/:id", get(ask_door))
        .route("/fact/:id", get(fact_door)) // row 4, panel sp2: a fact by its message id — the feed's pointer read through one door
        .route("/ask", post(ask_post))
        .route("/asks", get(asks_door))
        .route("/residents", get(residents_door))
        .route("/crew", get(crew_door))
        .route("/sessions", get(sessions_get).post(sessions_post))
        .route("/session/:id", get(session_door))
        .route("/recall", get(recall_door))
        .route("/export", get(export_door))
        .route("/digest/:id", get(digest_door))
        .route("/digest", post(digest_post))
        .route("/guide", get(guide_door))
        .route("/proof", get(proof_door))
        .route("/analyzer", get(analyzer_door))
        .route("/services", get(services_door).post(services_post))
        .route("/intentions", get(intentions_door))
        .route("/levers", get(levers_door)) // P7 sp8 row 3c: THE LEVER CATALOGUE — what the kernel itself can pull
        .route("/markers", get(markers_door))
        .route("/markers/kinds", get(markers_kinds).post(markers_declare)) // re-base sp1: the four Python-only doors cross
        .route("/mark", post(mark_door))
        .route("/mitl", get(mitl_door).post(mitl_toggle))
        .route("/impact", post(impact_door))
        .route("/monitor", get(monitor_door))
        .route("/profile", get(profile_door).post(profile_post)) // P7 sp8: the human's own profile — theirs to see and adjust (W58)
        .route("/world", get(world_door)) // P7 sp7: the world card — the universe, its cell, its epoch, its peers
        .route("/world/rehome", post(world_rehome)) // P7 sp7: re-home the universe — held at L2, the epoch advances on the yes
        .route("/seam", post(seam_post)) // P7 sp7: the seam — signed messages between peer cells
        .route("/asks/stop", post(asks_stop)) // P7 sp7: the human stops a routed ask (rule 11)
        .route("/schedules", post(schedules_post))
        .route("/schedules/rest", post(schedules_rest))
        .route("/schedules/:runner", get(schedules_door))
        .route("/harness", get(harness_door))
        .route("/harness/run", post(harness_run))
        .route("/harness/ab", post(harness_ab))
        .route("/delta", post(delta_post))
        .route("/bodies", get(bodies_door))
        .route("/bodies/restart", post(bodies_restart))
        .route("/minds", get(minds_door).post(minds_post))
        .route("/minds/spend", get(minds_spend))
        .route("/minds/fuel", get(minds_fuel))
        .route("/minds/search", get(minds_search))
        .route("/minds/assign", post(minds_post))
        .route("/minds/unassign", post(minds_post))
        .route("/minds/refill", post(minds_post))
        .route("/minds/check", post(minds_post))
        .route("/minds/retire", post(minds_post))
        .route("/minds/restore", post(minds_post))
        .route("/services/version", post(services_post))
        .route("/services/check", post(services_post))
        .route("/services/retire", post(services_post))
        .route("/services/restore", post(services_post))
        .route("/services/mcp", post(services_post))
        .route("/intentions/stop", post(intentions_stop))
        .route("/intentions/restart", post(intentions_restart))
        .route("/confirm", post(confirm_post))
        .route("/enroll", post(enroll_post))
        .route("/enroll/confirm", post(enroll_confirm_post))
        .route("/seat", get(seat_get).post(seat_post)) // P7 sp8 row 3: the seat — the person's code in, the token out
        .route("/seat/leave", post(seat_leave)) // the person ends their own seat — recorded
        .route("/join", get(desk_door).post(join_post)) // P7 sp8 row 3b: THE MACHINE JOIN DESK — a body asks and is challenged; the desk is a seated read
        .route("/join/prove", post(join_prove)) // the body's signature over the desk's own nonce
        .route("/join/lease", post(join_lease)) // the admitted body collects its lease with the same key
        .route("/join/:id", get(join_door)) // a join's status (open: the id is its own secret; the lease never rides it)
        .fallback(|| async { StatusCode::NOT_FOUND })
        .layer(middleware::from_fn_with_state(app.clone(), gate)) // P7 sp8 row 3: THE GATE at every door
        .layer(middleware::from_fn(clock)) // row 4, panel sp3: THE CLOCK outside the gate — the whole knock is timed
        .with_state(app)
}

/// P7 sp8 row 3: THE GATE at every door — the browser origin closed, the knock ceiling,
/// the seat read from the bearer (the feed: its `seat` query), the door's need against
/// the seat's grants. An open door (the page, the health, the guide, the world checks,
/// the seat door, the enrollment's confirm, the seam, the bodies' display door) passes
/// with a per-address ceiling; `/enroll` stands open while no one holds the ground (the
/// ceremony). The unseated wear one face (401); a seated person lacking the grant wears
/// the proof's (403). Law for law with the Python handler's `_admit`.
async fn gate(
    State(app): State<Arc<App>>,
    ConnectInfo(addr): ConnectInfo<SocketAddr>,
    mut req: axum::extract::Request,
    next: Next,
) -> Response {
    let path = req.uri().path().to_string();
    let method = req.method().as_str().to_string();
    let query = req.uri().query().map(str::to_string);
    let (origin, host, authorization) = {
        let header = |name: &str| -> Option<String> {
            req.headers()
                .get(name)
                .and_then(|v| v.to_str().ok())
                .map(str::to_string)
        };
        (header("origin"), header("host"), header("authorization"))
    };
    if !seat::origin_ok(origin.as_deref(), host.as_deref()) {
        return answer(403, one_face());
    }
    let needs = seat::door_needs(&method, &path);
    let by_addr = format!("addr:{}", addr.ip());
    if needs == "open" {
        if !app.gate.knock(&by_addr) {
            return answer(429, seat::busy());
        }
        return next.run(req).await;
    }
    let mut tok = seat::bearer(authorization.as_deref());
    if tok.is_none() && path == "/feed" {
        tok = query.as_deref().and_then(|q| {
            q.split('&')
                .find_map(|kv| kv.strip_prefix("seat=").map(str::to_string))
        });
    }
    // the offline half first (no ground for a forged seat); the ceiling spent BEFORE the ground is asked (a
    // flood never reaches it); then the gate's memory, and the ground once per SEEN_S
    let mut seated = None;
    if let Some(off) = tok
        .as_deref()
        .and_then(|t| seat_live::offline(&app.kernel, t))
    {
        if !app.gate.knock(&off.person) {
            return answer(429, seat::busy());
        }
        seated = app.gate.remembered(&off.seat_id);
        if seated.is_none() {
            if let Ok(g) = ground(&app).await {
                seated = seat_live::on_ground(&g, &app.cfg.world, off)
                    .await
                    .unwrap_or(None);
                if let Some(s) = &seated {
                    app.gate.remember(s);
                }
            }
        }
    }
    let Some(s) = seated else {
        if needs == "enroll" {
            let held = match ground(&app).await {
                Ok(g) => seat_live::owner(&g, scope(&app))
                    .await
                    .ok()
                    .flatten()
                    .is_some(),
                Err(_) => true,
            };
            if !held {
                if !app.gate.knock(&by_addr) {
                    return answer(429, seat::busy());
                }
                return next.run(req).await;
            }
        }
        return answer(401, seat::not_seated());
    };
    if needs == "govern" && !s.govern {
        return answer(403, one_face());
    }
    // P7 sp8 row 3b: a body's LEASE opens its own words and nothing more; a person's seat never speaks as a body
    if (needs == "lease") != (s.role == "body") {
        return answer(403, one_face());
    }
    req.extensions_mut().insert(s);
    next.run(req).await
}

/// `GET /seat` — the seat door's face: is this ground held? how long is a seat?
async fn seat_get(State(app): State<Arc<App>>) -> Response {
    let out = async {
        let g = ground(&app).await?;
        Ok::<_, RoadError>(
            json!({"ceremony": seat_live::owner(&g, scope(&app)).await?.is_none(),
                                  "hours": seat_live::hours()}),
        )
    }
    .await;
    match out {
        Ok(v) => answer(200, v),
        Err(e) => refuse(e),
    }
}

const PERSON_GRAMMAR: &str = "a person is named by a lower-case name (letters, digits, - or _; 2 to 24) or their did:orreth:person:… DID";

/// `POST /seat {person, code}` — the person's code from their authenticator; the token back (201).
async fn seat_post(State(app): State<Arc<App>>, body: Bytes) -> Response {
    let p = body_json(&body);
    let Some(person) = seat::person_did(p["person"].as_str()) else {
        return answer(400, json!({"error": PERSON_GRAMMAR}));
    };
    let code = s_opt(&p, "code");
    let out = async {
        let mut g = ground(&app).await?;
        seat_live::take(
            &mut g,
            &app.cfg.world,
            &app.kernel,
            &person,
            code.as_deref(),
            None,
        )
        .await
    }
    .await;
    match out {
        Ok(v) => answer(201, v),
        Err(e) => refuse(e),
    }
}

/// `POST /seat/leave` — the seated person ends their own seat (200).
async fn seat_leave(State(app): State<Arc<App>>, Extension(seated): Extension<Seated>) -> Response {
    let out = async {
        let mut g = ground(&app).await?;
        let made =
            seat_live::leave(&mut g, &app.cfg.world, &seated.seat_id, &seated.person).await?;
        app.gate.forget(&seated.seat_id); // this kernel forgets the seat at once
        Ok::<_, RoadError>(made)
    }
    .await;
    match out {
        Ok(v) => answer(200, v),
        Err(e) => refuse(e),
    }
}

type Q = Query<HashMap<String, String>>;

/// The door's JSON answer, with the headers the Python handler sends.
fn answer(code: u16, v: Value) -> Response {
    (
        StatusCode::from_u16(code).unwrap_or(StatusCode::INTERNAL_SERVER_ERROR),
        [(header::CONTENT_TYPE, "application/json")], // P7 sp8 row 3: no open origin — the glass is served by this door
        v.to_string(),
    )
        .into_response()
}

/// Every refusal at a door, by its face: the one face (403), kernel-required
/// (403, in words), a refusal in words (400), a door not yet served (501), a
/// rail's fall (500). A proof's demand never reaches here — the door holds.
fn refuse(e: RoadError) -> Response {
    match e {
        RoadError::NotConfirmed { .. } => answer(403, one_face()),
        RoadError::NotSeated => answer(401, seat::not_seated()),
        RoadError::Busy => answer(429, seat::busy()),
        RoadError::Forbidden(w) => answer(403, json!({"error": w})),
        RoadError::Refused(w) => answer(400, json!({"error": w})),
        RoadError::NotYet(w) => answer(501, json!({"error": w})),
        RoadError::Rail(r) => answer(500, json!({"error": r.to_string()})),
        RoadError::ProofRequired { level, what, .. } => {
            answer(400, json!({"error": format!("{what} needs {level}")}))
        }
    }
}

/// Row 4, panel sp3: a door stands on a LINE borrowed from the pool — back in the
/// pool when the knock is answered, never a fresh connection per knock.
async fn ground(app: &App) -> Result<Line, RoadError> {
    app.pool.borrow().await
}

/// Row 4, panel sp3: THE CLOCK at every door — how long the knock took, from the
/// gate to the answer, one sample under the door's name (`doors::door_name`); the
/// Monitoring folds it to a p50 and a p95 per door and the judge watches it.
async fn clock(req: axum::extract::Request, next: Next) -> Response {
    let method = req.method().as_str().to_string();
    let path = req.uri().path().to_string();
    let t0 = std::time::Instant::now();
    let res = next.run(req).await;
    if path != "/feed" {
        // the feed is a stream, not a knock: its life is not a door's latency
        crate::doors::record(&method, &path, t0.elapsed().as_secs_f64() * 1000.0);
    }
    res
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
    if n["delta"] == json!(true) {
        // P7 sp6: a body's words as they form — `event: delta`, no revision (as the Python feed frames it)
        return Event::default().event("delta").data(n.to_string());
    }
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
        // JB's ask 2026-09-28: a LIVE version number up top — the kernel says what it is (its crate
        // version, which kernel, when it was lit); the glass reads it here, never from its own words
        // re-base sp1 (lock 2): and which schema the ground holds against this kernel's own
        json!({"rev": app.feed.rev(), "clients": app.feed.clients(),
               "version": env!("CARGO_PKG_VERSION"), "kernel": "rust", "lit_at": app.lit_at,
               "schema": app.schema.to_value()}),
    )
}

/// re-base sp1: THE PARKED — every poison event the dispatcher holds at, with its
/// evidence, newest first (both kernels).
async fn parked_door(State(app): State<Arc<App>>) -> Response {
    let out = async {
        let g = ground(&app).await?;
        let rows = crate::inbox::parked(&g, None, 50).await?;
        Ok::<_, RoadError>(json!({"parked": rows, "consumer": dispatcher::CONSUMER,
                                  "held": rows.iter().filter(|r| r["consumer"] == json!(dispatcher::CONSUMER)).count()}))
    }
    .await;
    match out {
        Ok(v) => answer(200, v),
        Err(e) => refuse(e),
    }
}

/// re-base sp1: the operator's explicit decision (a governing seat) — advance the
/// dispatcher past a parked poison; the advance is a recorded fact in the person's name.
async fn parked_advance(
    State(app): State<Arc<App>>,
    Extension(seated): Extension<Seated>,
    body: Bytes,
) -> Response {
    let p = body_json(&body);
    let Some(id) = p["parked_id"].as_i64() else {
        return answer(
            400,
            json!({"error": "name the parked event: {parked_id} (GET /parked lists them)"}),
        );
    };
    let out = async {
        let mut g = ground(&app).await?;
        let sc = scope(&app).to_string();
        Ok::<_, RoadError>(crate::inbox::advance(&mut g, &sc, id, &seated.person).await?)
    }
    .await;
    match out {
        Ok(Some(v)) => answer(202, v),
        Ok(None) => answer(404, json!({"error": "no such parked event"})),
        Err(e) => refuse(e),
    }
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

/// Row 4, panel sp2: THE FACT DOOR — a committed fact by its message id, the pointer
/// every feed notice carries. The glass reads what a notice points at through this one
/// door instead of a door per topic. Only this world's facts; anything else is "no such
/// fact" — one face (rule 4). A seated read, like `/ask/<id>`.
async fn fact_door(State(app): State<Arc<App>>, Path(id): Path<String>) -> Response {
    let out = async {
        let g = ground(&app).await?;
        Ok::<_, RoadError>(outbox::fact_by_id(&g, &id).await?)
    }
    .await;
    match out {
        Ok(Some(e)) if e["universe_id"].as_str() == Some(scope(&app)) => answer(
            200,
            json!({
                "message_id": e["message_id"], "type": e["type"], "occurred_at": e["occurred_at"],
                "payload": e["payload"], "authority_chain": e["authority_chain"],
                "correlation_id": e["correlation_id"], "marker": e["marker"],
            }),
        ),
        Ok(_) => answer(404, json!({"error": "no such fact"})),
        Err(e) => refuse(e),
    }
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
        sessions::crew_view(&g, scope(&app), Some(&app.templates)).await
    }
    .await;
    match out {
        Ok(v) => answer(200, json!({"crew": v})),
        Err(e) => refuse(e),
    }
}

async fn sessions_get(
    State(app): State<Arc<App>>,
    Extension(seated): Extension<Seated>,
) -> Response {
    let person = seated.person.clone();
    let out = async {
        let mut g = ground(&app).await?;
        sessions::sessions_view(&mut g, scope(&app), &person, 30, &app.cfg.human_zone).await
    }
    .await;
    match out {
        Ok(v) => answer(200, json!({"sessions": v})),
        Err(e) => refuse(e),
    }
}

async fn sessions_post(
    State(app): State<Arc<App>>,
    Extension(seated): Extension<Seated>,
    body: Bytes,
) -> Response {
    let p = body_json(&body);
    let person = seated.person.clone();
    let title = s_opt(&p, "title");
    let opt_out = crate::py::truthy(&p["opt_out"]);
    let archive = s_opt(&p, "archive");
    let out = async {
        let mut g = ground(&app).await?;
        sessions::open_session(
            &mut g,
            scope(&app),
            &person,
            title.as_deref(),
            opt_out,
            archive.as_deref(),
            &app.cfg.human_zone,
        )
        .await
    }
    .await;
    match out {
        Ok(sid) => answer(201, json!({"session_id": sid})),
        Err(e) => refuse(e),
    }
}

/// P7 sp5: verbatim recall (MEM-1) — by ref (as of a time, or its lineage), by ask, by session, by window.
async fn recall_door(
    State(app): State<Arc<App>>,
    Extension(seated): Extension<Seated>,
    Query(q): Q,
) -> Response {
    let person = seated.person.clone();
    let window = match (q.get("from"), q.get("to")) {
        (Some(f), Some(t)) if !f.is_empty() && !t.is_empty() => Some((f.as_str(), t.as_str())),
        _ => None,
    };
    let opt = |k: &str| q.get(k).map(String::as_str).filter(|v| !v.is_empty());
    let out = async {
        let g = ground(&app).await?;
        crate::store::recall_view(
            &g,
            scope(&app),
            opt("ref"),
            opt("ask"),
            opt("session"),
            window,
            &person,
            opt("at"),
            q.get("history").map(String::as_str) == Some("1"),
        )
        .await
    }
    .await;
    match out {
        Ok(Some(v)) => answer(200, v),
        Ok(None) => answer(404, json!({"error": "nothing recalled — one face"})),
        Err(RoadError::Rail(r))
            if r.to_string().contains("timestamp")
                || r.to_string().contains("invalid input syntax") =>
        {
            answer(
                400,
                json!({"error": "the window is two ISO times, from and to"}),
            )
        }
        Err(e) => refuse(e),
    }
}

/// P7 sp5: the compliance export — a READ, the requester's own asks only, SIGNED by the kernel's self.
async fn export_door(
    State(app): State<Arc<App>>,
    Extension(seated): Extension<Seated>,
    Query(q): Q,
) -> Response {
    let person = seated.person.clone();
    let fmt = q
        .get("format")
        .cloned()
        .filter(|f| !f.is_empty())
        .unwrap_or_else(|| "json".into());
    if fmt != "json" && fmt != "csv" {
        return answer(400, json!({"error": "format is json or csv"}));
    }
    let window = match (q.get("from"), q.get("to")) {
        (Some(f), Some(t)) if !f.is_empty() && !t.is_empty() => Some((f.as_str(), t.as_str())),
        _ => None,
    };
    let opt = |k: &str| q.get(k).map(String::as_str).filter(|v| !v.is_empty());
    let out = async {
        let g = ground(&app).await?;
        crate::export_live::build(
            &g,
            scope(&app),
            &person,
            opt("session"),
            window,
            opt("marker"),
            Some(&app.kernel),
        )
        .await
    }
    .await;
    match out {
        Ok(bundle) if fmt == "csv" => (
            StatusCode::OK,
            [
                (header::CONTENT_TYPE, "text/csv; charset=utf-8"),
                (
                    header::CONTENT_DISPOSITION,
                    "attachment; filename=\"orreth-compliance.csv\"",
                ),
            ],
            crate::export::to_csv(&bundle),
        )
            .into_response(),
        Ok(bundle) => answer(200, bundle),
        Err(RoadError::Rail(r))
            if r.to_string().contains("timestamp")
                || r.to_string().contains("invalid input syntax") =>
        {
            answer(
                400,
                json!({"error": "the window is two ISO times, from and to"}),
            )
        }
        Err(e) => refuse(e),
    }
}

/// THE GUIDE (JB's seed, walk #13): kept by the kernel beside the glass — the same words on every door.
async fn guide_door(State(app): State<Arc<App>>) -> Response {
    let path = app
        .cfg
        .glass
        .parent()
        .and_then(|p| p.parent())
        .map(|p| p.join("guide").join("guide.v0.json"));
    let read = path
        .as_ref()
        .and_then(|p| std::fs::read_to_string(p).ok())
        .and_then(|t| serde_json::from_str::<Value>(&t).ok());
    match read {
        Some(v) => answer(200, v),
        None => answer(
            500,
            json!({"error": format!("the guide is not at {}", path.map(|p| p.display().to_string()).unwrap_or_default())}),
        ),
    }
}

/// P7 sp5: the short version, and every source it cites.
async fn digest_door(State(app): State<Arc<App>>, Path(id): Path<String>) -> Response {
    let out = async {
        let g = ground(&app).await?;
        crate::digest::of_session(&g, scope(&app), &id).await
    }
    .await;
    match out {
        Ok(Some(v)) => answer(200, v),
        Ok(None) => answer(404, json!({"error": "no digest yet — one face"})),
        Err(e) => refuse(e),
    }
}

/// P7 sp5: on demand, or rebuild.
async fn digest_post(
    State(app): State<Arc<App>>,
    Extension(seated): Extension<Seated>,
    body: Bytes,
) -> Response {
    let p = body_json(&body);
    let sid = s_or(&p, "session", "");
    let person = seated.person.clone();
    let out = async {
        let mut g = ground(&app).await?;
        crate::digest::build(&mut g, scope(&app), &sid, &person, &app.cfg.human_zone).await
    }
    .await;
    match out {
        Ok(Some(v)) => {
            let code = if v["new"].as_bool().unwrap_or(false) {
                201
            } else {
                200
            };
            answer(code, v)
        }
        Ok(None) => answer(404, json!({"error": "no such session"})),
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

async fn proof_door(State(app): State<Arc<App>>, Extension(seated): Extension<Seated>) -> Response {
    let person = seated.person.clone();
    let out = async {
        let g = ground(&app).await?;
        let enrolled = proof_live::enrolled(&g, scope(&app), &person).await?;
        let masters = proof_live::masters(&g, scope(&app)).await?;
        let owner = seat_live::owner(&g, scope(&app)).await?;
        Ok::<_, RoadError>(json!({"person": person, "enrolled": enrolled, "masters": masters, "owner": owner,
                                  "seat": {"seat_id": seated.seat_id, "role": seated.role, "expiry": seated.expiry}}))
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

/// P7 sp8 row 3c: the lever catalogue as data — every governed act this kernel can pull, and which it serves.
async fn levers_door() -> Response {
    match crate::levers_live::catalogue() {
        Ok(cat) => answer(
            200,
            json!({"door": crate::levers::DOOR,
                   "levers": cat.iter().map(crate::levers::manifest).collect::<Vec<_>>(),
                   "served": cat.iter().filter(|d| d["doors"].as_array().is_some_and(|a| a.iter().any(|x| x == crate::levers::DOOR)))
                                .filter_map(|d| d["name"].as_str()).collect::<Vec<_>>()}),
        ),
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

// ---- re-base sp1: the four Python-only doors cross — `POST /markers/kinds` · `POST /mark` ·
// `GET/POST /mitl` · `POST /impact` (the reference's `glass.py` mounts, law for law) ----

/// `POST /markers/kinds`: declare a kind — `{kind, group, description}`; the seat's person declares.
async fn markers_declare(
    State(app): State<Arc<App>>,
    Extension(seated): Extension<Seated>,
    body: Bytes,
) -> Response {
    let p = body_json(&body);
    let out = async {
        let g = ground(&app).await?;
        markers_live::declare(
            &g,
            scope(&app),
            &s_or(&p, "kind", ""),
            &s_or(&p, "group", ""),
            &s_or(&p, "description", ""),
            &seated.person,
        )
        .await
    }
    .await;
    match out {
        Ok(v) => answer(201, v),
        Err(e) => refuse(e),
    }
}

/// `POST /mark`: a human marks from the chat — `{kind, note?, ref?, session?}`; no ref
/// but a session marks the session's latest ask; the marked ask's marker is the parent;
/// every interested body (and intention) is asked to act.
async fn mark_door(
    State(app): State<Arc<App>>,
    Extension(seated): Extension<Seated>,
    body: Bytes,
) -> Response {
    let p = body_json(&body);
    let out = async {
        let mut g = ground(&app).await?;
        let mut r#ref = s_or(&p, "ref", "");
        if r#ref.is_empty() && truthy(&p["session"]) {
            let session = python_str(&p["session"]);
            r#ref = g
                .client()
                .query_opt(
                    "SELECT ask_id FROM spine_asks WHERE session = $1 ORDER BY asked_at DESC LIMIT 1",
                    &[&session],
                )
                .await?
                .map(|r| r.get::<_, String>(0))
                .unwrap_or_default();
        }
        if r#ref.is_empty() {
            return Err(RoadError::Refused("mark what? name an ask or a session".into()));
        }
        let parent: Option<String> = g
            .client()
            .query_opt("SELECT marker FROM spine_asks WHERE ask_id = $1", &[&r#ref])
            .await?
            .and_then(|r| r.get(0));
        let note = s_opt(&p, "note");
        let m = markers_live::set_marker(
            &mut g,
            &app.cfg.world,
            &s_or(&p, "kind", ""),
            &r#ref,
            &seated.person,
            parent.as_deref(),
            note.as_deref(),
            None,
        )
        .await?;
        let asked = markers_live::dispatch_interests(&mut g, &app.cfg.world, &m, &r#ref, m["note"].as_str()).await?;
        Ok::<_, RoadError>(json!({"marker": m, "asked": asked}))
    }
    .await;
    match out {
        Ok(v) => answer(201, v),
        Err(e) => refuse(e),
    }
}

/// `GET /mitl`: is MITL in the lit crew (for this session, or this person)? what does it
/// wear? every citation (W15).
async fn mitl_door(
    State(app): State<Arc<App>>,
    Extension(seated): Extension<Seated>,
    Query(q): Q,
) -> Response {
    let out = async {
        let g = ground(&app).await?;
        crate::mitl_live::card(
            &g,
            scope(&app),
            q.get("session")
                .map(String::as_str)
                .filter(|s| !s.is_empty()),
            &seated.person,
        )
        .await
    }
    .await;
    match out {
        Ok(v) => answer(200, v),
        Err(e) => refuse(e),
    }
}

/// `POST /mitl`: the soft toggle — `{summon: bool (default true), session?}`, a recorded fact.
async fn mitl_toggle(
    State(app): State<Arc<App>>,
    Extension(seated): Extension<Seated>,
    body: Bytes,
) -> Response {
    let p = body_json(&body);
    let on = match p.get("summon") {
        None => true,
        Some(v) => truthy(v),
    };
    let out = async {
        let mut g = ground(&app).await?;
        crate::mitl_live::summon(
            &mut g,
            &app.cfg.world,
            &seated.person,
            s_opt(&p, "session").as_deref(),
            on,
        )
        .await
    }
    .await;
    match out {
        Ok(v) => answer(201, v),
        Err(e) => refuse(e),
    }
}

/// `POST /impact`: "expected impact of this change?" — `{change: {kind, ref or draft, words}, session?}`.
async fn impact_door(
    State(app): State<Arc<App>>,
    Extension(seated): Extension<Seated>,
    body: Bytes,
) -> Response {
    let p = body_json(&body);
    let change = &p["change"];
    if !change.is_object() {
        return answer(
            400,
            json!({"error": "a change is {kind, ref or draft, words}"}),
        );
    }
    let out = async {
        let mut g = ground(&app).await?;
        crate::mitl_live::impact(
            &mut g,
            &app.cfg.world,
            change,
            &seated.person,
            s_opt(&p, "session").as_deref(),
        )
        .await
    }
    .await;
    match out {
        Ok(v) => answer(201, v),
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
async fn ask_post(
    State(app): State<Arc<App>>,
    Extension(seated): Extension<Seated>,
    body: Bytes,
) -> Response {
    let p = body_json(&body);
    let text = s_or(&p, "text", "").trim().to_string();
    if text.is_empty() {
        return answer(400, json!({"error": "an empty ask asks nothing"}));
    }
    let person = seated.person.clone();
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
        // P7 sp7: the fence at the action boundary — a re-homed universe is not this kernel's to serve
        if let Some(words) = crate::cells_live::fence(&g, &w.scope, &app.cell).await? {
            return Err(RoadError::Forbidden(words));
        }
        // P7 sp7: an ask that names a CELL routes home over the seam
        if let Some((cell, name)) = crate::cells::address_home(&text) {
            let id = app
                .seam
                .route_ask(
                    &mut g,
                    w,
                    &cell,
                    &name,
                    &Submit {
                        text: text.clone(),
                        person: person.clone(),
                        to: None,
                        window: window.clone(),
                        session: session.clone(),
                        parent_marker: parent.clone(),
                        kind: Some(kind.clone()),
                        zone: zone.clone(),
                    },
                )
                .await?;
            return Ok((201, json!({"id": id})));
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

async fn confirm_post(
    State(app): State<Arc<App>>,
    Extension(seated): Extension<Seated>,
    body: Bytes,
) -> Response {
    let p = body_json(&body);
    let ask_id = s_or(&p, "ask_id", "");
    let approve = crate::py::truthy(&p["approve"]);
    let by = seated.person.clone(); // P7 sp8 row 3: the word is the SEAT's — a master confirms from their own seat
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

async fn enroll_post(
    State(app): State<Arc<App>>,
    seated: Option<Extension<Seated>>,
    body: Bytes,
) -> Response {
    let p = body_json(&body);
    let actor = seated.map(|e| e.0);
    let named = if crate::py::truthy(&p["person"]) {
        python_str(&p["person"])
    } else {
        actor.as_ref().map(|a| a.person.clone()).unwrap_or_default()
    };
    let Some(person) = seat::person_did(Some(&named)) else {
        return answer(400, json!({"error": PERSON_GRAMMAR}));
    };
    let code = s_opt(&p, "code");
    let out = async {
        let mut g = ground(&app).await?;
        // P7 sp8 row 3: the ceremony while no one holds the ground; else oneself (the old code, grave) or a governing seat
        if !seat_live::may_enroll(&g, scope(&app), actor.as_ref(), &person).await? {
            return Err(RoadError::NotConfirmed { rest: false });
        }
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
    let Some(person) = seat::person_did(p["person"].as_str()) else {
        return answer(403, one_face()); // the code IS the proof, for a person named in the grammar
    };
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

// ---- the loops' doors (P7 sp4) --------------------------------------------------------

/// P7 sp8: `GET /profile?person=` — the portrait: every live word with its label, the named
/// fields resolved, the slice the bodies read, the clock this ground would use.
async fn profile_door(
    State(app): State<Arc<App>>,
    Extension(seated): Extension<Seated>,
) -> Response {
    let person = seated.person.clone();
    let out = async {
        let g = ground(&app).await?;
        crate::profile_live::portrait(&g, &app.cfg.world, &person).await
    }
    .await;
    match out {
        Ok(v) => answer(200, v),
        Err(e) => refuse(e),
    }
}

/// P7 sp8: `POST /profile {person, text}` — "my name is …" · "I live in …" · "forget about me: …" ·
/// "what do you know about me?" — read by the law; words that say nothing refuse in words (400).
async fn profile_post(
    State(app): State<Arc<App>>,
    Extension(seated): Extension<Seated>,
    body: Bytes,
) -> Response {
    let p = body_json(&body);
    let person = seated.person.clone();
    let text = s_or(&p, "text", "").trim().to_string();
    if text.is_empty() {
        return answer(
            400,
            json!({"error": "say something about yourself, or ask what I know"}),
        );
    }
    let geocode_it = !matches!(p["geocode"], Value::Bool(false)); // a proof may say no road
    let out = async {
        let mut g = ground(&app).await?;
        crate::profile_live::say(&mut g, &app.cfg.world, &person, &text, None, geocode_it).await
    }
    .await;
    match out {
        Ok((code, v)) => answer(code, v),
        Err(e) => refuse(e),
    }
}

/// P7 sp7: the world card (rule 7 — the same on both doors).
async fn world_door(State(app): State<Arc<App>>) -> Response {
    let out = async {
        let g = ground(&app).await?;
        crate::cells_live::card(
            &g,
            scope(&app),
            &app.cell,
            Some(&app.kernel.did()),
            &app.cfg.world.ns,
            &app.cfg.human_zone,
        )
        .await
    }
    .await;
    match out {
        Ok(v) => answer(200, v),
        Err(e) => refuse(e),
    }
}

/// P7 sp7: `POST /seam` — a peer's signed message through every fence, answered in kind.
async fn seam_post(State(app): State<Arc<App>>, body: Bytes) -> Response {
    let signed = body_json(&body);
    let out = async {
        let mut g = ground(&app).await?;
        app.seam.receive(&mut g, &signed).await
    }
    .await;
    match out {
        Ok((code, v)) => answer(code, v),
        Err(e) => refuse(e),
    }
}

/// P7 sp7: `POST /asks/stop {id}` — a routed ask set to rest here and at its home.
async fn asks_stop(
    State(app): State<Arc<App>>,
    Extension(seated): Extension<Seated>,
    body: Bytes,
) -> Response {
    let p = body_json(&body);
    let id = s_or(&p, "id", "");
    let person = seated.person.clone();
    let out = async {
        let mut g = ground(&app).await?;
        app.seam.stop_ask(&mut g, &id, &person).await
    }
    .await;
    match out {
        Ok(v) => answer(200, v),
        Err(e) => refuse(e),
    }
}

/// P7 sp7: `POST /world/rehome {to_cell}` — held at the interlock (L2); on the yes the epoch advances.
async fn world_rehome(
    State(app): State<Arc<App>>,
    Extension(seated): Extension<Seated>,
    body: Bytes,
) -> Response {
    let p = body_json(&body);
    let to_cell = s_or(&p, "to_cell", "");
    let person = seated.person.clone();
    let out = async {
        let mut g = ground(&app).await?;
        let held = crate::cells_live::hold_rehome(
            &mut g,
            &app.cfg.world,
            &to_cell,
            &person,
            s_opt(&p, "session").as_deref(),
        )
        .await?;
        Ok::<_, RoadError>(json!({"held": held, "level": crate::cells_live::REHOME_LEVEL}))
    }
    .await;
    match out {
        Ok(v) => answer(202, v),
        Err(e) => refuse(e),
    }
}

async fn monitor_door(State(app): State<Arc<App>>) -> Response {
    let out = async {
        let g = ground(&app).await?;
        monitor::snapshot(&g, &app.cfg.world, true).await
    }
    .await;
    match out {
        Ok(v) => answer(200, v),
        Err(e) => refuse(e),
    }
}

/// The card's side B: every schedule this runner runs, by kind.
async fn schedules_door(State(app): State<Arc<App>>, Path(runner): Path<String>) -> Response {
    let out = async {
        let g = ground(&app).await?;
        scheduler::for_runner(&g, scope(&app), &runner).await
    }
    .await;
    match out {
        Ok(v) => answer(200, v),
        Err(e) => refuse(e),
    }
}

/// A human schedule lands: `{runner, text, every_s >= 5}`.
async fn schedules_post(
    State(app): State<Arc<App>>,
    Extension(seated): Extension<Seated>,
    body: Bytes,
) -> Response {
    let p = body_json(&body);
    let runner = s_or(&p, "runner", "");
    let text = s_or(&p, "text", "").trim().to_string();
    let every = p["every_s"]
        .as_i64()
        .or_else(|| p["every_s"].as_f64().map(|f| f as i64))
        .or_else(|| p["every_s"].as_str().and_then(|s| s.parse().ok()))
        .unwrap_or(0);
    if runner.is_empty() || text.is_empty() || every < 5 {
        return answer(
            400,
            json!({"error": "a schedule is {runner, text, every_s >= 5}"}),
        );
    }
    let person = seated.person.clone();
    let out = async {
        let mut g = ground(&app).await?;
        scheduler::add(
            &mut g,
            scope(&app),
            &runner,
            "human",
            &text,
            every,
            &person,
            None,
        )
        .await
    }
    .await;
    match out {
        Ok(sid) => answer(201, json!({"schedule_id": sid})),
        Err(e) => refuse(e),
    }
}

/// The human's stop of a schedule: recorded, never a delete; a kernel one refuses.
async fn schedules_rest(
    State(app): State<Arc<App>>,
    Extension(seated): Extension<Seated>,
    body: Bytes,
) -> Response {
    let p = body_json(&body);
    let person = seated.person.clone();
    let sid = s_or(&p, "schedule_id", "");
    let out = async {
        let g = ground(&app).await?;
        scheduler::rest(&g, scope(&app), &sid, &person).await
    }
    .await;
    match out {
        Ok(true) => answer(202, json!({"rested": python_str(&p["schedule_id"])})),
        Ok(false) => answer(404, json!({"error": "no such schedule"})),
        Err(e) => refuse(e),
    }
}

/// The world checks, read off the ground; the last harness run beside them.
async fn harness_door(State(app): State<Arc<App>>) -> Response {
    let out = async {
        let g = ground(&app).await?;
        let sc = scope(&app);
        let ch = harness::checks(&g, sc, &app.gateway).await?;
        let ok = ch.iter().all(|c| c["ok"] == json!(true));
        Ok::<_, RoadError>(
            json!({"checks": ch, "ok": ok, "last": monitor::last_harness(&g, sc).await?}),
        )
    }
    .await;
    match out {
        Ok(v) => answer(200, v),
        Err(e) => refuse(e),
    }
}

/// P7 sp6: a mind's run OVER THE RAIL — the kernel asks the body to run its
/// golden cases as this run id; the run's row answers (200), or 202 while the
/// body still works. A body not here: 404, as the Python door says.
async fn harness_run(State(app): State<Arc<App>>, body: Bytes) -> Response {
    let p = body_json(&body);
    let template = s_or(&p, "template", "librarian");
    let out = async {
        let g = ground(&app).await?;
        let w = &app.cfg.world;
        let cases = harness::golden(&template);
        let rid = harness::run_over_rail(&g, w, &template, &cases, s_opt(&p, "arm").as_deref(), None).await?;
        match harness::wait_run(&g, &rid, Duration::from_secs(90)).await? {
            Some(row) => Ok::<_, RoadError>((200, row)),
            None => Ok((202, json!({"run_id": rid, "template": template, "running": true,
                                    "words": format!("{template} is still running its {} golden cases — the run lands as {rid}; the Monitoring shows it when it does", cases.len())}))),
        }
    }
    .await;
    match out {
        Ok((code, v)) => answer(code, v),
        Err(RoadError::Refused(w)) if w == "no such body" => answer(404, json!({"error": w})),
        Err(e) => refuse(e),
    }
}

/// P6.5 sp3's A/B with model ARMS, over the rail: the same golden cases against two or more minds.
async fn harness_ab(State(app): State<Arc<App>>, body: Bytes) -> Response {
    let p = body_json(&body);
    let template = s_or(&p, "template", "librarian");
    let arms: Vec<String> = p["arms"]
        .as_array()
        .map(|a| {
            a.iter()
                .map(python_str)
                .filter(|s| !s.trim().is_empty())
                .collect()
        })
        .unwrap_or_default();
    if arms.len() < 2 {
        return answer(
            400,
            json!({"error": "an A/B run names two or more minds as arms"}),
        );
    }
    let out = async {
        let g = ground(&app).await?;
        harness::ab(
            &g,
            &app.cfg.world,
            &template,
            &arms,
            Duration::from_secs(120),
        )
        .await
    }
    .await;
    match out {
        Ok(v) => answer(200, v),
        Err(RoadError::Refused(w)) if w == "no such body" => answer(404, json!({"error": w})),
        Err(e) => refuse(e),
    }
}

// ---- the machine join desk (P7 sp8 row 3b) --------------------------------------------------

/// `POST /join {did, name, role, public_key, template_hash, policy_hash, ticket?}` — a body asks
/// to join and is challenged in the same breath (201: `{id, status: challenged, nonce, words}`).
async fn join_post(State(app): State<Arc<App>>, body: Bytes) -> Response {
    let p = body_json(&body);
    let out = async {
        let mut g = ground(&app).await?;
        desk_live::ask(&mut g, &app.cfg.world, &p).await
    }
    .await;
    match out {
        Ok(v) => answer(201, v),
        Err(e) => refuse(e),
    }
}

/// `POST /join/prove {id, did, sig}` — the proof over the desk's own nonce (200: the join's
/// word — done on a standing word, staged for a governing seat's click, or denied).
async fn join_prove(State(app): State<Arc<App>>, body: Bytes) -> Response {
    let p = body_json(&body);
    let (id, did) = (s_or(&p, "id", ""), s_or(&p, "did", ""));
    let sig = p["sig"].clone();
    let out = async {
        let mut g = ground(&app).await?;
        let manifest: Option<&dyn desk_live::Manifest> =
            app.bodies.as_deref().map(|b| b as &dyn desk_live::Manifest);
        desk_live::prove(&mut g, &app.cfg.world, manifest, &id, &did, &sig).await
    }
    .await;
    match out {
        Ok(Some(v)) => answer(200, v),
        Ok(None) => answer(404, desk::refused()),
        Err(e) => refuse(e),
    }
}

/// `GET /join/<id>` — the join's status in the desk's words (never the lease).
async fn join_door(State(app): State<Arc<App>>, Path(id): Path<String>) -> Response {
    let out = async {
        let g = ground(&app).await?;
        desk_live::status(&g, &app.cfg.world, &id).await
    }
    .await;
    match out {
        Ok(Some(v)) => answer(200, v),
        Ok(None) => answer(404, desk::refused()),
        Err(e) => refuse(e),
    }
}

/// `POST /join/lease {id, did, sig}` — the admitted body collects its lease with the same key
/// (200: `{lease, wire, lease_id, expiry, admitted_by, words}`); any other knock wears the one face.
async fn join_lease(State(app): State<Arc<App>>, body: Bytes) -> Response {
    let p = body_json(&body);
    let (id, did) = (s_or(&p, "id", ""), s_or(&p, "did", ""));
    let sig = p["sig"].clone();
    let out = async {
        let mut g = ground(&app).await?;
        desk_live::collect(&mut g, &app.cfg.world, &app.kernel, &id, &did, &sig).await
    }
    .await;
    match out {
        Ok(Some(v)) => answer(200, v),
        Ok(None) => answer(404, desk::refused()),
        Err(e) => refuse(e),
    }
}

/// `GET /join` — the desk as a seated person reads it: every join asked of this world, newest first.
async fn desk_door(State(app): State<Arc<App>>, Extension(_seated): Extension<Seated>) -> Response {
    let out = async {
        let g = ground(&app).await?;
        desk_live::list(&g, &app.cfg.world, 50).await
    }
    .await;
    match out {
        Ok(v) => answer(200, json!({"joins": v, "lease_days": desk::lease_days()})),
        Err(e) => refuse(e),
    }
}

// ---- the bodies' seam (P7 sp6) ------------------------------------------------------------

/// A spawned body's words as they form: `{ref, text}` → the feed's delta frame (display only).
async fn delta_post(State(app): State<Arc<App>>, body: Bytes) -> Response {
    let p = body_json(&body);
    let r#ref = s_or(&p, "ref", "");
    let text = s_or(&p, "text", "");
    if r#ref.is_empty() || text.is_empty() {
        return answer(400, json!({"error": "a delta is {ref, text}"}));
    }
    app.feed.publish_delta(&r#ref, &text);
    StatusCode::NO_CONTENT.into_response()
}

/// Every body this kernel seats, as the kernel sees it (the ground's leases say alive).
async fn bodies_door(State(app): State<Arc<App>>) -> Response {
    match &app.bodies {
        Some(b) => answer(
            200,
            json!({"mode": "crew", "spine": app.cfg.spine.display().to_string(), "bodies": b.view()}),
        ),
        None => answer(
            200,
            json!({"mode": "none", "spine": app.cfg.spine.display().to_string(), "bodies": [],
                                   "words": "this kernel seats no bodies — the Python Bridge's serve from their benches (SPINE_BODIES=none)"}),
        ),
    }
}

/// The human's lever: a parked or refused body is tried again.
async fn bodies_restart(State(app): State<Arc<App>>, body: Bytes) -> Response {
    let p = body_json(&body);
    let name = s_or(&p, "name", "").trim().to_lowercase();
    let Some(b) = &app.bodies else {
        return answer(
            400,
            json!({"error": "this kernel seats no bodies (SPINE_BODIES=none)"}),
        );
    };
    match b.restart(&name) {
        Ok(v) => answer(202, v),
        Err(e) => refuse(e),
    }
}

/// The Stable's read: every LLM with its deal, health and spend; the assignments; the gateway.
async fn minds_door(State(app): State<Arc<App>>) -> Response {
    let out = async {
        let g = ground(&app).await?;
        let sc = scope(&app);
        let minds: Vec<Value> = stable_live::stalls(&g, sc)
            .await?
            .into_iter()
            .map(|mut r| {
                r["words"] = json!(crate::stable::stall_words(&r));
                r
            })
            .collect();
        Ok::<_, RoadError>(json!({"minds": minds, "assignments": stable_live::assignments(g.client(), sc).await?,
                                  "gateway": {"base": app.gateway.base, "ready": app.gateway.ready().await}}))
    }
    .await;
    match out {
        Ok(v) => answer(200, v),
        Err(e) => refuse(e),
    }
}

async fn minds_spend(State(app): State<Arc<App>>) -> Response {
    let out = async {
        let g = ground(&app).await?;
        stable_live::spend(&g).await
    }
    .await;
    match out {
        Ok(v) => answer(200, v),
        Err(e) => refuse(e),
    }
}

/// A body's gauge, by name.
async fn minds_fuel(State(app): State<Arc<App>>, Query(q): Q) -> Response {
    let name = q.get("name").cloned().unwrap_or_default();
    let out = async {
        let g = ground(&app).await?;
        let Some(did) = services_live::did_of_body(g.client(), scope(&app), &name).await? else {
            return Ok::<_, RoadError>((404, json!({"error": format!("no body named {} is joined here", crate::py::repr_str(&name))})));
        };
        let gw = if app.gateway.ready().await { Some(&app.gateway) } else { None };
        Ok((200, json!({"name": name, "fuel": stable_live::fuel(&g, scope(&app), gw, &did).await?})))
    }
    .await;
    match out {
        Ok((code, v)) => answer(code, v),
        Err(e) => refuse(e),
    }
}

async fn minds_search(State(app): State<Arc<App>>, Query(q): Q) -> Response {
    let out = async {
        let g = ground(&app).await?;
        let rows = stable_live::search(
            &g,
            scope(&app),
            q.get("q").map(String::as_str),
            q.get("klass").map(String::as_str).filter(|k| !k.is_empty()),
            q.get("max_in_per_m").and_then(|v| v.parse().ok()),
            q.get("modality")
                .map(String::as_str)
                .filter(|m| !m.is_empty()),
        )
        .await?;
        let minds: Vec<Value> = rows
            .into_iter()
            .map(|mut r| {
                r["words"] = json!(crate::stable::stall_words(&r));
                r
            })
            .collect();
        Ok::<_, RoadError>(json!({"minds": minds}))
    }
    .await;
    match out {
        Ok(v) => answer(200, v),
        Err(e) => refuse(e),
    }
}

/// The Stable's acts — the held ones hold at the interlock (L2); check and restore run at once.
async fn minds_post(
    State(app): State<Arc<App>>,
    Extension(seated): Extension<Seated>,
    uri: axum::http::Uri,
    body: Bytes,
) -> Response {
    let path = uri.path().to_string();
    let p = body_json(&body);
    let person = seated.person.clone();
    let session = s_opt(&p, "session");
    let name = s_or(&p, "name", "").trim().to_lowercase();
    let out = async {
        let mut g = ground(&app).await?;
        let w = &app.cfg.world;
        let ready = app.gateway.ready().await;
        let gw = if ready { Some(&app.gateway) } else { None };
        match path.as_str() {
            "/minds/check" => {
                let checked = if name.is_empty() {
                    services_live::check_all(&mut g, w, gw, Some("mind"), &person).await?
                } else {
                    vec![services_live::check(&mut g, w, gw, &name, &person).await?]
                };
                let ok = checked.iter().all(|c| c["ok"] == json!(true));
                Ok::<_, RoadError>((200, json!({"checked": checked, "ok": ok})))
            }
            "/minds/restore" => {
                let made = stable_live::restore_mind(&mut g, w, gw, &name, &person).await?;
                Ok((201, json!({"service": made})))
            }
            "/minds/retire" => {
                let held = services_live::hold_retire(&mut g, w, &name, &person, session.as_deref()).await?;
                Ok((202, json!({"held": held, "level": services_live::RETIRE_LEVEL, "class": services_live::RETIRE_CLASS})))
            }
            _ => {
                let (tool, args) = match path.as_str() {
                    "/minds" => {
                        let d = stable_live::deal_from(&p)?;
                        (crate::stable::REGISTER_TOOL, json!({"name": name, "deal": d}))
                    }
                    "/minds/assign" => (
                        crate::stable::ASSIGN_TOOL,
                        json!({"subject": s_or(&p, "subject", "*"), "klass": s_or(&p, "klass", crate::stable::ANY),
                               "stall": if crate::py::truthy(&p["stall"]) { python_str(&p["stall"]) } else { name.clone() }}),
                    ),
                    "/minds/unassign" => (
                        crate::stable::UNASSIGN_TOOL,
                        json!({"subject": s_or(&p, "subject", "*"), "klass": s_or(&p, "klass", crate::stable::ANY)}),
                    ),
                    _ => {
                        let who = if crate::py::truthy(&p["subject"]) { python_str(&p["subject"]) } else { name.clone() };
                        let Some(did) = services_live::did_of_body(g.client(), &w.scope, &who).await? else {
                            return Ok((404, json!({"error": format!("no body named {} is joined here", crate::py::repr_str(&who))})));
                        };
                        let usd = p["usd"].as_f64().or_else(|| p["usd"].as_str().and_then(|s| s.parse().ok())).unwrap_or(1.0);
                        (crate::stable::REFILL_TOOL, json!({"did": did, "name": who, "usd": usd}))
                    }
                };
                let text = stable_live::words_for(tool, &args);
                let held = stable_live::hold(&mut g, w, tool, args, &text, &person, session.as_deref()).await?;
                Ok((202, json!({"held": held, "level": crate::stable::ACT_LEVEL, "class": crate::stable::ACT_CLASS})))
            }
        }
    }
    .await;
    match out {
        Ok((code, v)) => answer(code, v),
        Err(e) => refuse(e),
    }
}

/// The shelf's doors — the owner's, plain words (P6.5 sp1 · sp2).
async fn services_post(
    State(app): State<Arc<App>>,
    Extension(seated): Extension<Seated>,
    uri: axum::http::Uri,
    body: Bytes,
) -> Response {
    let path = uri.path().to_string();
    let p = body_json(&body);
    let person = seated.person.clone();
    let name = s_or(&p, "name", "").trim().to_string();
    let secrets: Vec<String> = p["secrets_with"]
        .as_array()
        .map(|a| a.iter().map(python_str).collect())
        .unwrap_or_default();
    let placement = p.get("placement").filter(|v| crate::py::truthy(v));
    let out = async {
        let mut g = ground(&app).await?;
        let w = &app.cfg.world;
        match path.as_str() {
            "/services/mcp" => {
                let made = crate::mcp_live::register_server(&mut g, w, &name, &s_or(&p, "locator", ""), &person, &secrets, placement).await?;
                Ok::<_, RoadError>((201, json!({"service": made["server"], "tools": made["tools"], "info": made["info"]})))
            }
            "/services" => {
                let made = services_live::register(&mut g, w, &name, &s_or(&p, "kind", ""), &p["manifest"], &person, placement, &secrets).await?;
                Ok((201, json!({"service": made})))
            }
            "/services/version" => {
                let made = services_live::version(&mut g, w, &name, &p["manifest"], &person).await?;
                Ok((200, json!({"service": made})))
            }
            "/services/check" => {
                let ready = app.gateway.ready().await;
                let gw = if ready { Some(&app.gateway) } else { None };
                let checked = if name.is_empty() {
                    services_live::check_all(&mut g, w, gw, s_opt(&p, "kind").as_deref(), &person).await?
                } else {
                    vec![services_live::check(&mut g, w, gw, &name, &person).await?]
                };
                let ok = checked.iter().all(|c| c["ok"] == json!(true));
                Ok((200, json!({"checked": checked, "ok": ok})))
            }
            "/services/retire" => {
                let held = services_live::hold_retire(&mut g, w, &name, &person, s_opt(&p, "session").as_deref()).await?;
                Ok((202, json!({"held": held, "level": services_live::RETIRE_LEVEL, "class": services_live::RETIRE_CLASS})))
            }
            _ => {
                // W71 (walk #19, 2026-09-27): ONE restore law — "restore the gemma mind" through the
                // shelf's door left the ladder registered and the gateway without its entry
                // ("Invalid model name"); a restored mind's entry is written back, as /minds/restore does
                let ready = app.gateway.ready().await;
                let gw = if ready { Some(&app.gateway) } else { None };
                let made = stable_live::restore_mind(&mut g, w, gw, &name, &person).await?;
                Ok((201, json!({"service": made})))
            }
        }
    }
    .await;
    match out {
        Ok((code, v)) => answer(code, v),
        Err(e) => refuse(e),
    }
}

/// Rule 11: the stop — and its reverse (W20). ANY intention's stop is grave
/// (W5): a bare one is HELD for the code (the kernel's: code, then master).
async fn intentions_act(app: Arc<App>, seated: Seated, p: Value, restart: bool) -> Response {
    let person = seated.person.clone();
    let iid = {
        let v = s_or(&p, "intention_id", "");
        if v.is_empty() {
            s_or(&p, "ref", "")
        } else {
            v
        }
    };
    let verb = if restart { "restart" } else { "stop" };
    let out = async {
        let mut g = ground(&app).await?;
        let w = &app.cfg.world;
        let made = if restart {
            intent_live::restart(&mut g, w, &iid, &person, None, None).await
        } else {
            intent_live::stop(&mut g, w, &iid, &person, None, None).await
        };
        match made {
            Ok(Some(v)) => Ok((202, json!({"intention": v}))),
            Ok(None) => Ok((404, json!({"error": "no such intention"}))),
            Err(RoadError::ProofRequired {
                level,
                what,
                needs_code,
            }) => {
                let held = proof_live::hold_kernel_act(
                    &mut g,
                    w,
                    &what,
                    &person,
                    &format!("intent.{verb}"),
                    json!({"intention_id": iid}),
                    level,
                    s_opt(&p, "session").as_deref(),
                    "grave",
                    needs_code,
                )
                .await?;
                Ok((
                    202,
                    json!({"held": held, "level": level, "needs_code": needs_code}),
                ))
            }
            Err(e) => Err(e),
        }
    }
    .await;
    match out {
        Ok((code, v)) => answer(code, v),
        Err(e) => refuse(e),
    }
}

async fn intentions_stop(
    State(app): State<Arc<App>>,
    Extension(seated): Extension<Seated>,
    body: Bytes,
) -> Response {
    intentions_act(app, seated, body_json(&body), false).await
}

async fn intentions_restart(
    State(app): State<Arc<App>>,
    Extension(seated): Extension<Seated>,
    body: Bytes,
) -> Response {
    intentions_act(app, seated, body_json(&body), true).await
}
