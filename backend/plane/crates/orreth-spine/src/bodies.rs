// PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp6, the bodies' seam · 2026-09-24
//! THE BODIES' SEAM (canon 0004 · 0008's end shape · 0005 P7 sp6): the kernel
//! SPAWNS and GOVERNS the crew as processes. Each seat of the one crew
//! manifest (`spine/crew.v0.json`, read by both spines) becomes ONE process —
//! `python -m orreth_spine.body --template … [--binding …]`, the SDK-side
//! body — in the world the kernel stands in, streaming its words to the
//! kernel's own door. The kernel watches every body: one that dies is
//! restarted after a backoff (`body::backoff_s`); one that dies
//! `PARK_STRIKES` times inside `PARK_WINDOW_S` is PARKED — visibly, as a
//! fact (`orreth.body.parked.v1`) carrying its last words, its seat and its
//! self standing, the human's lever a door away (`restart`); one refused at
//! birth (placement) or without a policy is TERMINAL and never restarted (its
//! refusal is already a recorded fact). At dark every body is stopped WHOLE:
//! SIGINT, a bounded wait, then — only for one that would not stop — SIGKILL;
//! nothing is left running. Liveness stays a fact on the ground (the leases,
//! M2): what this module knows is the process; what the world knows is the lease.
//!
//! Before the crew: the kernel's BOOT RITE runs once, NATIVE since P7 sp8 row
//! 2 (the built-ins on the shelf from `spine/tools.v0.json` — the declarations
//! both kernels read — the ground, the Record and the rig's own stall, each
//! probed by this kernel; the reference clock by the dial; no Python spawned to
//! seed) and the world's benches are swept of a prior life's leftovers.

use crate::body::{
    park_rule, parked_payload, parked_words, EXIT_NO_POLICY, EXIT_REFUSED, KERNEL, PARKED,
    PARK_STRIKES, PARK_WINDOW_S,
};
use crate::envelope::{self, Mint};
use crate::ground::Ground;
use crate::world::{RoadError, World};
use serde_json::{json, Value};
use std::collections::{HashMap, VecDeque};
use std::path::{Path, PathBuf};
use std::process::Stdio;
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::{Arc, Mutex, RwLock, Weak};
use std::time::Duration;

/// P7 sp8 row 3c: the crew this process governs, for the remediation rail's hand
/// (`body.restart` pulled by the kernel under an intention) and its dossier.
static HANDLE: RwLock<Option<Weak<Bodies>>> = RwLock::new(None);

/// The bodies this kernel seats, if any — the newest lit in this process.
pub fn handle() -> Option<Arc<Bodies>> {
    HANDLE
        .read()
        .unwrap_or_else(|p| p.into_inner())
        .as_ref()
        .and_then(Weak::upgrade)
}
use tokio::io::{AsyncBufReadExt, BufReader};
use tokio::sync::Notify;

pub const BODIES_DIAL: &str = "SPINE_BODIES"; // crew (default) · none
pub const SPINE_DIAL: &str = crate::tools::SPINE_DIAL; // the spine home; default beside the crate
pub const CREW_FORMAT: &str = "orreth-crew/1";
/// The Python that runs a body: `SPINE_PYTHON`, else the spine's own venv
/// (`<spine>/.venv/bin/python3`), else `python3` on PATH. NEVER through `uv run`:
/// a wrapper's pid is not the body's — a kill of the wrapper would orphan the
/// body, still serving, still renewing its lease (found by the proof, 2026-09-24).
pub const PYTHON_DIAL: &str = "SPINE_PYTHON";
/// A manifest other than `crew.v0.json` (a proof's two-seat crew; a smaller rig) — a path.
pub const CREW_DIAL: &str = "SPINE_CREW";
const LAST_WORDS: usize = 20;

/// The spine home: `ORRETH_SPINE`, else the crate's `../../../../spine` (the
/// one reading, shared with the tools' declarations — `tools::spine_dir`).
pub fn spine_dir() -> PathBuf {
    crate::tools::spine_dir()
}

/// Does this kernel seat a crew? `SPINE_BODIES=none` says no (side by side
/// with the Python Bridge, whose bodies serve).
pub fn wanted() -> bool {
    !matches!(
        std::env::var(BODIES_DIAL).ok().as_deref().map(str::trim),
        Some("none") | Some("0") | Some("off") | Some("no")
    )
}

/// One seat of the crew.
#[derive(Debug, Clone)]
pub struct Seat {
    pub name: String,
    pub kind: String,
    pub template: PathBuf,
    pub binding: Option<PathBuf>,
    pub template_json: Value,
}

/// `body.crew`: the manifest's seats with their paths resolved and their
/// templates read (the name a binding gives, else the template's).
pub fn crew(spine: &Path) -> Result<Vec<Seat>, RoadError> {
    let path = std::env::var(CREW_DIAL)
        .ok()
        .filter(|p| !p.is_empty())
        .map(PathBuf::from)
        .unwrap_or_else(|| spine.join("crew.v0.json"));
    let text = std::fs::read_to_string(&path).map_err(|e| {
        RoadError::Refused(format!(
            "the crew manifest at {} could not be read: {e}",
            path.display()
        ))
    })?;
    let doc: Value = serde_json::from_str(&text)
        .map_err(|e| RoadError::Refused(format!("the crew manifest is not JSON: {e}")))?;
    if doc["format"].as_str() != Some(CREW_FORMAT) {
        return Err(RoadError::Refused(format!(
            "not a crew manifest: {}",
            doc["format"]
        )));
    }
    let mut out = Vec::new();
    for s in doc["seats"].as_array().cloned().unwrap_or_default() {
        let t = s["template"].as_str().unwrap_or("").trim().to_string();
        if t.is_empty() {
            return Err(RoadError::Refused("a seat names its template".into()));
        }
        let template = spine.join(&t);
        let tj: Value = serde_json::from_str(&std::fs::read_to_string(&template).map_err(|e| {
            RoadError::Refused(format!(
                "the template {} could not be read: {e}",
                template.display()
            ))
        })?)
        .map_err(|e| {
            RoadError::Refused(format!(
                "the template {} is not JSON: {e}",
                template.display()
            ))
        })?;
        let binding = s["binding"]
            .as_str()
            .filter(|b| !b.trim().is_empty())
            .map(|b| spine.join(b.trim()));
        let mut name = tj["name"].as_str().unwrap_or("").to_string();
        if let Some(b) = &binding {
            let bj: Value = serde_json::from_str(&std::fs::read_to_string(b).map_err(|e| {
                RoadError::Refused(format!(
                    "the binding {} could not be read: {e}",
                    b.display()
                ))
            })?)
            .map_err(|e| {
                RoadError::Refused(format!("the binding {} is not JSON: {e}", b.display()))
            })?;
            if let Some(n) = bj["name"].as_str() {
                name = n.to_string();
            }
        }
        out.push(Seat {
            name,
            kind: tj["kind"].as_str().unwrap_or("resident").to_string(),
            template,
            binding,
            template_json: tj,
        });
    }
    if out.is_empty() {
        return Err(RoadError::Refused("a crew has at least one seat".into()));
    }
    Ok(out)
}

/// Where a governed body stands, in the kernel's eyes.
#[derive(Debug, Clone)]
pub struct BodyState {
    pub name: String,
    pub kind: String,
    pub state: &'static str, // starting · alive · restarting · parked · refused · stopped
    pub pid: Option<u32>,
    pub did: Option<String>,
    pub lives: u32,
    pub deaths: Vec<String>,
    pub since: String,
    pub exit: Option<i32>,
    pub words: String,
    pub last_words: VecDeque<String>,
}

impl BodyState {
    fn new(seat: &Seat) -> BodyState {
        BodyState {
            name: seat.name.clone(),
            kind: seat.kind.clone(),
            state: "starting",
            pid: None,
            did: None,
            lives: 0,
            deaths: Vec::new(),
            since: envelope::now_iso(),
            exit: None,
            words: String::new(),
            last_words: VecDeque::with_capacity(LAST_WORDS),
        }
    }

    pub fn to_value(&self) -> Value {
        json!({
            "name": self.name, "kind": self.kind, "state": self.state, "pid": self.pid, "did": self.did,
            "lives": self.lives, "deaths": self.deaths, "since": self.since, "exit": self.exit,
            "words": self.words, "last_words": self.last_words.iter().cloned().collect::<Vec<_>>(),
        })
    }
}

struct Inner {
    states: HashMap<String, BodyState>,
    pids: HashMap<String, u32>,
    /// P7 sp8 row 3b: the one-time SPAWN TICKET each life carries to the join desk — the
    /// kernel's own word for a body it spawned (the crew manifest is the human's), spent once.
    tickets: HashMap<String, String>,
}

/// The crew a kernel governs.
pub struct Bodies {
    pub seats: Vec<Seat>,
    pub spine: PathBuf,
    pub world: World,
    pub door: String,
    pub ephemeral: bool,
    inner: Mutex<Inner>,
    stop: AtomicBool,
    wake: HashMap<String, Arc<Notify>>,
    tasks: Mutex<Vec<tokio::task::JoinHandle<()>>>,
}

fn now() -> String {
    envelope::now_iso()
}

impl Bodies {
    pub fn new(
        seats: Vec<Seat>,
        spine: PathBuf,
        world: World,
        door: String,
        ephemeral: bool,
    ) -> Arc<Bodies> {
        let states = seats
            .iter()
            .map(|s| (s.name.clone(), BodyState::new(s)))
            .collect();
        let wake = seats
            .iter()
            .map(|s| (s.name.clone(), Arc::new(Notify::new())))
            .collect();
        let me = Arc::new(Bodies {
            seats,
            spine,
            world,
            door,
            ephemeral,
            inner: Mutex::new(Inner {
                states,
                pids: HashMap::new(),
                tickets: HashMap::new(),
            }),
            stop: AtomicBool::new(false),
            wake,
            tasks: Mutex::new(Vec::new()),
        });
        *HANDLE.write().unwrap_or_else(|p| p.into_inner()) = Some(Arc::downgrade(&me));
        me
    }

    /// The child's environment: the kernel's own, the world's dials on top,
    /// the kernel's door for the words as they form.
    fn env(&self) -> Vec<(String, String)> {
        let mut e = vec![
            ("SPINE_QUEUE_NS".to_string(), self.world.ns.clone()),
            ("SPINE_SCOPE".to_string(), self.world.scope.clone()),
            ("SPINE_PG".to_string(), self.world.pg_dsn.clone()),
            ("SPINE_RABBIT".to_string(), self.world.rabbit_url.clone()),
            ("SPINE_KAFKA".to_string(), self.world.kafka.clone()),
            ("SPINE_KERNEL_DOOR".to_string(), self.door.clone()),
            ("PYTHONUNBUFFERED".to_string(), "1".to_string()),
        ];
        if self.ephemeral {
            e.push(("SPINE_BODY_EPHEMERAL".to_string(), "1".to_string()));
        }
        e
    }

    /// The interpreter a body runs in — the process IS the body (its pid the one the kernel governs).
    pub fn python(&self) -> PathBuf {
        if let Ok(p) = std::env::var(PYTHON_DIAL) {
            if !p.is_empty() {
                return PathBuf::from(p);
            }
        }
        let venv = self.spine.join(".venv").join("bin").join("python3");
        if venv.exists() {
            return venv;
        }
        PathBuf::from("python3")
    }

    fn command(&self, args: &[String], ticket: &str) -> tokio::process::Command {
        let mut c = tokio::process::Command::new(self.python());
        c.args(["-u", "-m", "orreth_spine.body"])
            .args(args)
            .current_dir(&self.spine)
            .envs(self.env())
            .env(crate::desk::SPAWN_TICKET_DIAL, ticket) // P7 sp8 row 3b: this life's word at the join desk
            .stdin(Stdio::null())
            .stdout(Stdio::null())
            .stderr(Stdio::piped())
            .kill_on_drop(true); // a kernel that falls takes its bodies with it — never an orphan serving unseen
        c
    }

    /// The kernel's boot rite, once, NATIVE (P7 sp8 row 2 — the spawned Python
    /// `--seed-shelf` one-shot retired): the built-ins on the shelf from the
    /// declarations file both kernels read, the ground and the Record, the rig's
    /// own stall, each probed once by this kernel; the reference clock by the
    /// dial. Its words are said on the kernel's own stderr and returned; a
    /// refusal is said, never a crash.
    pub async fn seed_shelf(
        &self,
        gw: Option<&crate::gateway::Gateway>,
    ) -> Result<Vec<String>, RoadError> {
        use crate::{mcp_live, services_live, stable_live};
        let mut said = Vec::new();
        let mut say = |line: String| {
            eprintln!("{line}");
            said.push(line);
        };
        let mut g = crate::ground::Ground::connect(&self.world.pg_dsn).await?;
        let made = services_live::seed(&mut g, &self.world, &self.spine).await?;
        let st = stable_live::seed(&mut g, &self.world, gw).await?;
        let names = |v: &Value| -> Vec<String> {
            v.as_array()
                .map(|a| a.iter().map(crate::py::python_str).collect())
                .unwrap_or_default()
        };
        for line in names(&made["refused"])
            .into_iter()
            .chain(names(&st["refused"]))
        {
            say(format!("the shelf refused a built-in: {line}"));
        }
        for n in names(&st["retired"]) {
            say(format!(
                "the shelf: {n}, the old world's built-in mind, retired — the Stable's {} stall serves the same model through the gateway",
                stable_live::DEFAULT_STALL.0
            ));
        }
        let checked =
            services_live::check_all(&mut g, &self.world, gw, None, services_live::KERNEL).await?;
        let bad: Vec<String> = checked
            .iter()
            .filter(|c| c["ok"] == json!(false))
            .map(|c| crate::py::python_str(&c["name"]))
            .collect();
        let registered: Vec<String> = names(&made["registered"])
            .into_iter()
            .chain(names(&st["registered"]))
            .collect();
        let versioned: Vec<String> = names(&made["versioned"])
            .into_iter()
            .chain(names(&st["versioned"]))
            .collect();
        let mut words = format!("the shelf: {} services probed", checked.len());
        if !registered.is_empty() {
            words.push_str(&format!(", registered now: {}", registered.join(", ")));
        }
        if !versioned.is_empty() {
            words.push_str(&format!(
                ", re-pinned (their words changed): {}",
                versioned.join(", ")
            ));
        }
        if !bad.is_empty() {
            words.push_str(&format!(", UNHEALTHY: {}", bad.join(", ")));
        }
        say(words);
        if mcp_live::ref_on() {
            match mcp_live::seed_ref(&mut g, &self.world, &self.python(), &self.spine).await {
                Ok(r) => {
                    let t = &r["tools"];
                    let listed: Vec<String> = ["new", "present", "versioned"]
                        .iter()
                        .flat_map(|k| names(&t[*k]))
                        .collect();
                    say(format!(
                        "the shelf: the reference clock server registered at {} — tools {}",
                        mcp_live::locator_words(&mcp_live::ref_locator(
                            &self.python(),
                            &self.spine
                        )),
                        if listed.is_empty() {
                            "none".to_string()
                        } else {
                            listed.join(", ")
                        }
                    ));
                }
                Err(e) => say(format!("the reference clock could not be registered: {e}")), // the rig runs on
            }
        }
        Ok(said)
    }

    /// Operator's act at light (`BridgeRig._sweep_benches`): this world's
    /// queues cleared of a prior life's leftovers.
    pub async fn sweep_benches(&self) -> Result<(), RoadError> {
        let conn = crate::invoke::connect(&self.world.rabbit_url).await?;
        let ch = conn
            .create_channel()
            .await
            .map_err(crate::rail_error::RailError::from)?;
        let mut queues = vec![crate::rails::serve_queue(&self.world.ns, None)];
        queues.extend(
            self.seats
                .iter()
                .map(|s| crate::rails::serve_queue(&self.world.ns, Some(&s.name))),
        );
        for q in queues {
            ch.queue_declare(
                q.as_str().into(),
                lapin::options::QueueDeclareOptions {
                    durable: true,
                    ..Default::default()
                },
                lapin::types::FieldTable::default(),
            )
            .await
            .map_err(crate::rail_error::RailError::from)?;
            ch.queue_purge(
                q.as_str().into(),
                lapin::options::QueuePurgeOptions::default(),
            )
            .await
            .map_err(crate::rail_error::RailError::from)?;
        }
        conn.close(200, "swept".into()).await.ok();
        Ok(())
    }

    /// The kernel's duties for the bodies it seats (AG-6's scheduled run):
    /// every body with a golden set runs the harness on the kernel's clock.
    pub async fn declare_duties(&self, g: &mut Ground) -> Result<Vec<String>, RoadError> {
        let mut out = Vec::new();
        for s in &self.seats {
            if self
                .spine
                .join("golden")
                .join(format!("{}.v0.json", s.name))
                .exists()
            {
                crate::scheduler::declared(
                    g,
                    &self.world.scope,
                    &s.name,
                    "kernel",
                    crate::scheduler::HARNESS_DUTY,
                    1800,
                    KERNEL,
                )
                .await?;
                out.push(s.name.clone());
            }
        }
        Ok(out)
    }

    fn set<F: FnOnce(&mut BodyState)>(&self, name: &str, f: F) {
        let mut i = self.inner.lock().unwrap_or_else(|p| p.into_inner());
        if let Some(s) = i.states.get_mut(name) {
            f(s);
        }
    }

    /// P7 sp8 row 3b: the desk's question — did this kernel hand this body this ticket? Spent on a yes.
    pub fn take_ticket(&self, name: &str, ticket: &str) -> bool {
        let mut i = self.inner.lock().unwrap_or_else(|p| p.into_inner());
        if i.tickets.get(name).is_some_and(|t| t == ticket) {
            i.tickets.remove(name);
            true
        } else {
            false
        }
    }

    /// The template this kernel spawned a seat from, by its hash — WHAT the body says it is, checked at the desk.
    pub fn template_hash_of(&self, name: &str) -> Option<String> {
        self.seats
            .iter()
            .find(|s| s.name == name)
            .map(|s| crate::hash::content_hash(&s.template_json))
    }

    fn set_pid(&self, name: &str, pid: Option<u32>) {
        let mut i = self.inner.lock().unwrap_or_else(|p| p.into_inner());
        match pid {
            Some(p) => {
                i.pids.insert(name.to_string(), p);
            }
            None => {
                i.pids.remove(name);
            }
        }
        if let Some(s) = i.states.get_mut(name) {
            s.pid = pid;
        }
    }

    /// Spawn every seat and watch it — the standing tasks of the seam.
    pub fn spawn_all(self: &Arc<Self>) {
        for seat in self.seats.clone() {
            let me = self.clone();
            let h = tokio::spawn(async move { me.govern(seat).await });
            self.tasks.lock().unwrap_or_else(|p| p.into_inner()).push(h);
        }
    }

    /// One body's whole governed life, life after life.
    async fn govern(self: Arc<Self>, seat: Seat) {
        let wake = self.wake.get(&seat.name).cloned().unwrap_or_default();
        loop {
            if self.stop.load(Ordering::Relaxed) {
                break;
            }
            let mut args = vec![
                "--template".to_string(),
                seat.template.display().to_string(),
            ];
            if let Some(b) = &seat.binding {
                args.push("--binding".into());
                args.push(b.display().to_string());
            }
            // P7 sp8 row 3b: a fresh ticket every life — the desk admits this body's proven key on it, once
            let ticket = crate::world::token_hex(16);
            self.inner
                .lock()
                .unwrap_or_else(|p| p.into_inner())
                .tickets
                .insert(seat.name.clone(), ticket.clone());
            let mut child = match self.command(&args, &ticket).spawn() {
                Ok(c) => c,
                Err(e) => {
                    self.set(&seat.name, |s| {
                        s.state = "parked";
                        s.words = format!(
                            "{} could not be started: {e} — SPINE_PYTHON names another interpreter",
                            seat.name
                        );
                    });
                    wake.notified().await;
                    continue;
                }
            };
            let pid = child.id();
            self.set_pid(&seat.name, pid);
            self.set(&seat.name, |s| {
                s.state = "starting";
                s.lives += 1;
                s.since = now();
                s.exit = None;
                s.words = format!("{} is starting (life {})", seat.name, s.lives);
            });
            // the body's words on the kernel's stderr, and its last words kept
            let reader = {
                let me = self.clone();
                let name = seat.name.clone();
                let stderr = child.stderr.take();
                tokio::spawn(async move {
                    let Some(err) = stderr else { return };
                    let mut lines = BufReader::new(err).lines();
                    while let Ok(Some(l)) = lines.next_line().await {
                        eprintln!("  [{name}] {l}");
                        let alive = l.contains(" is alive: ");
                        let did = if alive {
                            l.split("is alive: ")
                                .nth(1)
                                .and_then(|r| r.split_whitespace().next())
                                .map(str::to_string)
                        } else {
                            None
                        };
                        me.set(&name, |s| {
                            if s.last_words.len() == LAST_WORDS {
                                s.last_words.pop_front();
                            }
                            s.last_words.push_back(l.clone());
                            if alive {
                                s.state = "alive";
                                s.words = format!("{name} is alive (life {})", s.lives);
                                if did.is_some() {
                                    s.did = did.clone();
                                }
                            }
                        });
                    }
                })
            };
            let status = child.wait().await;
            let _ = tokio::time::timeout(Duration::from_secs(2), reader).await;
            let code = status.ok().and_then(|s| s.code());
            self.set_pid(&seat.name, None);
            if self.stop.load(Ordering::Relaxed) {
                self.set(&seat.name, |s| {
                    s.state = "stopped";
                    s.exit = code;
                    s.words = format!("{} stopped whole on the kernel's word", seat.name);
                });
                break;
            }
            match code {
                Some(EXIT_REFUSED) => {
                    self.set(&seat.name, |s| {
                        s.state = "refused";
                        s.exit = code;
                        s.words = format!("{} was refused at birth — the ground cannot seat it (recorded); never restarted; fix its template to seat it", seat.name);
                    });
                    wake.notified().await;
                    self.set(&seat.name, |s| s.deaths.clear());
                    continue;
                }
                Some(EXIT_NO_POLICY) => {
                    self.set(&seat.name, |s| {
                        s.state = "refused";
                        s.exit = code;
                        s.words = format!(
                            "{} wears no covenant policy — it never joins (AG-3); never restarted",
                            seat.name
                        );
                    });
                    wake.notified().await;
                    continue;
                }
                _ => {}
            }
            let at = now();
            let (rule, deaths, last) = {
                let mut i = self.inner.lock().unwrap_or_else(|p| p.into_inner());
                let s = i.states.get_mut(&seat.name).expect("a seat has a state");
                s.deaths.push(at.clone());
                s.exit = code;
                let rule = park_rule(&s.deaths, &at, PARK_WINDOW_S, PARK_STRIKES);
                (
                    rule,
                    s.deaths.len() as i64,
                    s.last_words.iter().cloned().collect::<Vec<_>>().join(" / "),
                )
            };
            if rule["parked"] == json!(true) {
                let n = rule["deaths"].as_i64().unwrap_or(deaths);
                let words = parked_words(&seat.name, n, PARK_WINDOW_S, Some(&last));
                let did = self
                    .inner
                    .lock()
                    .unwrap_or_else(|p| p.into_inner())
                    .states
                    .get(&seat.name)
                    .and_then(|s| s.did.clone());
                // the fact FIRST, then the state the door shows — what a reader sees parked is already recorded
                if let Err(e) = self.park_fact(&seat.name, did.as_deref(), n, &last).await {
                    eprintln!("  [kernel] the parked fact could not land: {e}");
                }
                self.set(&seat.name, |s| {
                    s.state = "parked";
                    s.words = words.clone();
                });
                eprintln!("  [kernel] {words}");
                wake.notified().await; // the human's lever: restart
                self.set(&seat.name, |s| {
                    s.deaths.clear();
                    s.state = "starting";
                    s.words = format!("{} is being restarted on the human's word", seat.name);
                });
                continue;
            }
            let wait = rule["wait_s"].as_f64().unwrap_or(1.0);
            self.set(&seat.name, |s| {
                s.state = "restarting";
                s.words = format!(
                    "{} died (exit {}) — death {} in the window; restarting in {wait:.0} s",
                    seat.name,
                    code.map(|c| c.to_string())
                        .unwrap_or_else(|| "by a signal".into()),
                    rule["deaths"]
                );
            });
            eprintln!(
                "  [kernel] {} died (exit {code:?}) — restarting in {wait:.0} s",
                seat.name
            );
            let end = tokio::time::Instant::now() + Duration::from_secs_f64(wait);
            while tokio::time::Instant::now() < end && !self.stop.load(Ordering::Relaxed) {
                tokio::time::sleep(Duration::from_millis(100)).await;
            }
        }
    }

    /// `orreth.body.parked.v1` through the outbox — the kernel's own fact.
    async fn park_fact(
        &self,
        name: &str,
        did: Option<&str>,
        deaths: i64,
        last_words: &str,
    ) -> Result<(), RoadError> {
        let mut g = Ground::connect(&self.world.pg_dsn).await?;
        let e = Mint {
            kind: "event".into(),
            r#type: PARKED.into(),
            universe_id: self.world.scope.clone(),
            scope_path: self.world.scope.clone(),
            payload: parked_payload(name, did, deaths, PARK_WINDOW_S, Some(last_words)),
            correlation_id: Some(name.to_string()),
            authority_chain: Some(vec![KERNEL.to_string()]),
            aggregate: None,
            marker: None,
        }
        .mint()?;
        let raw = envelope::encode(&e)?;
        crate::outbox::commit_with_outbox(
            &mut g,
            &raw,
            e["message_id"].as_str().unwrap_or_default(),
            None,
            async |_tx| Ok(()),
        )
        .await?;
        Ok(())
    }

    /// The human's lever: a parked or refused body is tried again (its deaths forgotten).
    pub fn restart(&self, name: &str) -> Result<Value, RoadError> {
        self.restart_on(name, "your word")
    }

    /// The same lever pulled on another's word — the kernel's, under an intention (row 3c;
    /// W83: the words name whose word it was).
    pub fn restart_on(&self, name: &str, whose: &str) -> Result<Value, RoadError> {
        let state = self
            .inner
            .lock()
            .unwrap_or_else(|p| p.into_inner())
            .states
            .get(name)
            .map(|s| s.state);
        match state {
            None => Err(RoadError::Refused(format!(
                "no body named {} is seated by this kernel",
                crate::py::repr_str(name)
            ))),
            Some("parked") | Some("refused") => {
                if let Some(w) = self.wake.get(name) {
                    w.notify_one();
                }
                Ok(
                    json!({"name": name, "restarting": true, "words": format!("{name} is being restarted on {whose} — its deaths are forgotten; if it dies {PARK_STRIKES} times again in {} it parks again", crate::body::window_words(PARK_WINDOW_S))}),
                )
            }
            Some(st) => Ok(
                json!({"name": name, "restarting": false, "words": format!("{name} is {st} — nothing to restart")}),
            ),
        }
    }

    /// Every body's state, for the door.
    pub fn view(&self) -> Vec<Value> {
        let i = self.inner.lock().unwrap_or_else(|p| p.into_inner());
        self.seats
            .iter()
            .filter_map(|s| i.states.get(&s.name))
            .map(BodyState::to_value)
            .collect()
    }

    /// A body's pid, for a proof that kills one by hand.
    pub fn pid_of(&self, name: &str) -> Option<u32> {
        self.inner
            .lock()
            .unwrap_or_else(|p| p.into_inner())
            .pids
            .get(name)
            .copied()
    }

    /// Stopped WHOLE: SIGINT to every living body, a bounded wait for each
    /// governor to see its exit, then SIGKILL for one that would not stop.
    pub async fn stop(&self) {
        self.stop.store(true, Ordering::Relaxed);
        for w in self.wake.values() {
            w.notify_one();
        }
        let pids: Vec<u32> = self
            .inner
            .lock()
            .unwrap_or_else(|p| p.into_inner())
            .pids
            .values()
            .copied()
            .collect();
        for pid in &pids {
            unsafe {
                libc::kill(*pid as libc::pid_t, libc::SIGINT);
            }
        }
        let tasks: Vec<_> = self
            .tasks
            .lock()
            .unwrap_or_else(|p| p.into_inner())
            .drain(..)
            .collect();
        let deadline = tokio::time::Instant::now() + Duration::from_secs(25);
        for t in tasks {
            if tokio::time::timeout_at(deadline, t).await.is_err() {
                break;
            }
        }
        let left: Vec<u32> = self
            .inner
            .lock()
            .unwrap_or_else(|p| p.into_inner())
            .pids
            .values()
            .copied()
            .collect();
        for pid in left {
            eprintln!("  [kernel] a body (pid {pid}) did not stop whole in 25 s — killed");
            unsafe {
                libc::kill(pid as libc::pid_t, libc::SIGKILL);
            }
        }
    }

    /// The templates by body name (the crew card's LLM line reads a body's `mind`).
    pub fn templates(&self) -> HashMap<String, Value> {
        self.seats
            .iter()
            .map(|s| (s.name.clone(), s.template_json.clone()))
            .collect()
    }
}

impl crate::desk_live::Manifest for Bodies {
    fn take_ticket(&self, name: &str, ticket: &str) -> bool {
        Bodies::take_ticket(self, name, ticket)
    }
    fn template_hash_of(&self, name: &str) -> Option<String> {
        Bodies::template_hash_of(self, name)
    }
}
