// PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch row 4, PANEL sp3: THE POOL — a connection pool at every door · 2026-09-28
// Amended: Claude Fable 5.1 (claude-fable-5-1) — THE GROUND CONNECTIONS CURE (JB's word 2026-10-08): a pool SHEDS the lines idle past `SPINE_POOL_IDLE_S`; a PRIVATE pool for the kernel's beats (one registry, the doors' alone); every line named on the ground · 2026-10-08
//! THE POOL — lines to the ground, held by the kernel, borrowed by every door
//! (canon 0005 row 4, JB's lock 1 of "the kernel that lasts": *today each
//! door opens a fresh ground connection per knock; the gate proof exhausted
//! Postgres with ninety knocks from one seat. The App holds a pool; handlers
//! borrow. The performance law's first fixed cost, gone.*)
//!
//! A [`Line`] is one open [`Ground`] on loan: a door borrows it, stands on it
//! for the knock (reads, a transaction through `client_mut`), and drops it —
//! the line goes back to the pool for the next knock. The pool holds at most
//! [`Pool::ceiling`] lines (`SPINE_POOL`, default 16); a knock past the
//! ceiling WAITS for a line rather than opening one, and the wait is counted
//! (`waiting` now · the longest wait) so the Monitoring can watch it. A line
//! whose connection ended, or whose ground moved (`set_search_path` — a new
//! key), is not returned. The rails' loops keep their own standing lines
//! (one each for their whole life); the pool is the doors'.
//!
//! The reading (`read`) is this pool's; [`read_all`] sums every pool alive in
//! this process for the Monitoring (`monitor::snapshot` → `pool` and
//! `values.pool_busy` · `values.pool_waiting`).
//!
//! THE GROUND CONNECTIONS CURE (2026-10-08): a line idle past
//! [`idle_from_env`] (`SPINE_POOL_IDLE_S`, default 60 s) is SHED — closed and
//! forgotten — when [`Pool::shed`] is called (the presence sweep calls it every
//! five seconds), so a kernel nobody knocks on holds no door lines at all; the
//! next knock opens one. The kernel's standing beats borrow from a PRIVATE pool
//! of two lines ([`Pool::private`], unlisted — the Monitoring's `pool` stays the
//! doors') instead of each holding a connection for life. Every line is named
//! on the ground (`application_name`), so `pg_stat_activity` reads who holds what.

use crate::ground::Ground;
use crate::world::RoadError;
use serde_json::{json, Value};
use std::ops::{Deref, DerefMut};
use std::sync::atomic::{AtomicU64, Ordering};
use std::sync::{Arc, LazyLock, Mutex, OnceLock, Weak};
use std::time::{Duration, Instant};
use tokio::sync::{OwnedSemaphorePermit, Semaphore};

/// `SPINE_POOL` — the most lines a pool holds open at once (default 16).
pub const CEILING_DEFAULT: usize = 16;

pub fn ceiling_from_env() -> usize {
    std::env::var("SPINE_POOL")
        .ok()
        .and_then(|v| v.trim().parse::<usize>().ok())
        .filter(|n| *n > 0)
        .unwrap_or(CEILING_DEFAULT)
}

/// `SPINE_POOL_IDLE_S` — how long an idle door line is kept before it is shed (default 60 s).
pub const IDLE_DEFAULT_S: u64 = 60;

pub fn idle_from_env() -> Duration {
    Duration::from_secs(
        std::env::var("SPINE_POOL_IDLE_S")
            .ok()
            .and_then(|v| v.trim().parse::<u64>().ok())
            .unwrap_or(IDLE_DEFAULT_S),
    )
}

/// The beats' private pool holds this many lines at most.
pub const BEATS_CEILING: usize = 2;

/// The doors' lines to one ground.
pub struct Pool {
    dsn: String,
    /// The name every line of this pool wears on the ground (`application_name`).
    name: String,
    ceiling: usize,
    /// The idle lines, each with the moment it came back.
    idle: Mutex<Vec<(Ground, Instant)>>,
    permits: Arc<Semaphore>,
    /// The ground a line is born on (its key); a line that moved is dropped.
    key: OnceLock<String>,
    /// Lines opened since light.
    opened: AtomicU64,
    /// Knocks that borrowed a line since light.
    borrowed: AtomicU64,
    /// Knocks waiting for a line right now.
    waiting: AtomicU64,
    /// Lines on loan right now.
    busy: AtomicU64,
    /// The longest a knock waited for a line, in microseconds.
    wait_max_us: AtomicU64,
    /// Lines shed for standing idle (the cure).
    shed: AtomicU64,
    born: Instant,
}

static POOLS: LazyLock<Mutex<Vec<Weak<Pool>>>> = LazyLock::new(|| Mutex::new(Vec::new()));

impl Pool {
    /// The doors' pool for `dsn`, at most `ceiling` lines, each named `orrethd door`;
    /// registered for the Monitoring.
    pub fn new(dsn: &str, ceiling: usize) -> Arc<Pool> {
        let pool = Self::private(dsn, ceiling, "orrethd door");
        let mut pools = POOLS.lock().unwrap_or_else(|p| p.into_inner());
        pools.retain(|w| w.strong_count() > 0);
        pools.push(Arc::downgrade(&pool));
        pool
    }

    /// A pool the Monitoring does not list (the cure): the kernel's beats borrow their lines
    /// here — `name` is what each line wears on the ground.
    pub fn private(dsn: &str, ceiling: usize, name: &str) -> Arc<Pool> {
        let ceiling = ceiling.max(1);
        Arc::new(Pool {
            dsn: dsn.to_string(),
            name: name.to_string(),
            ceiling,
            idle: Mutex::new(Vec::new()),
            permits: Arc::new(Semaphore::new(ceiling)),
            key: OnceLock::new(),
            opened: AtomicU64::new(0),
            borrowed: AtomicU64::new(0),
            waiting: AtomicU64::new(0),
            busy: AtomicU64::new(0),
            wait_max_us: AtomicU64::new(0),
            shed: AtomicU64::new(0),
            born: Instant::now(),
        })
    }

    /// THE SHED (the cure, 2026-10-08): every idle line that came back longer than `max_idle`
    /// ago is closed and forgotten; the count shed now. A kernel nobody knocks on holds no
    /// door lines; the next knock opens one.
    pub fn shed(&self, max_idle: Duration) -> usize {
        let mut idle = self.idle.lock().unwrap_or_else(|p| p.into_inner());
        let before = idle.len();
        idle.retain(|(_, back)| back.elapsed() < max_idle);
        let n = before - idle.len();
        self.shed.fetch_add(n as u64, Ordering::Relaxed);
        n
    }

    pub fn ceiling(&self) -> usize {
        self.ceiling
    }

    /// A line on loan: an idle one, else a fresh one under the ceiling, else
    /// the wait for one to come back.
    pub async fn borrow(self: &Arc<Self>) -> Result<Line, RoadError> {
        let t0 = Instant::now();
        self.waiting.fetch_add(1, Ordering::Relaxed);
        let permit = self.permits.clone().acquire_owned().await;
        self.waiting.fetch_sub(1, Ordering::Relaxed);
        let waited = t0.elapsed().as_micros() as u64;
        self.wait_max_us.fetch_max(waited, Ordering::Relaxed);
        let permit = permit.map_err(|_| RoadError::Refused("the pool is closed".into()))?;
        let mut g = loop {
            let idle = self.idle.lock().unwrap_or_else(|p| p.into_inner()).pop();
            match idle {
                Some((g, _)) if !g.client().is_closed() => break Some(g),
                Some(_) => continue, // its connection ended while idle: forgotten
                None => break None,
            }
        };
        if g.is_none() {
            let fresh = Ground::connect_as(&self.dsn, &self.name).await?;
            self.opened.fetch_add(1, Ordering::Relaxed);
            let _ = self.key.set(fresh.key().to_string());
            g = Some(fresh);
        }
        self.borrowed.fetch_add(1, Ordering::Relaxed);
        self.busy.fetch_add(1, Ordering::Relaxed);
        Ok(Line {
            g,
            pool: self.clone(),
            _permit: permit,
        })
    }

    /// This pool's reading, in the Monitoring's words.
    pub fn read(&self) -> Value {
        let idle = self.idle.lock().unwrap_or_else(|p| p.into_inner()).len() as u64;
        let busy = self.busy.load(Ordering::Relaxed);
        json!({
            "ceiling": self.ceiling,
            "open": idle + busy,
            "idle": idle,
            "busy": busy,
            "waiting": self.waiting.load(Ordering::Relaxed),
            "opened_total": self.opened.load(Ordering::Relaxed),
            "borrowed_total": self.borrowed.load(Ordering::Relaxed),
            "wait_max_ms": self.wait_max_us.load(Ordering::Relaxed) as f64 / 1000.0,
            "shed_total": self.shed.load(Ordering::Relaxed),
            "up_s": self.born.elapsed().as_secs(),
        })
    }

    fn give_back(&self, g: Ground) {
        if g.client().is_closed() {
            return;
        }
        if self.key.get().is_some_and(|k| k != g.key()) {
            return; // it stands on another ground now: not this pool's
        }
        self.idle
            .lock()
            .unwrap_or_else(|p| p.into_inner())
            .push((g, Instant::now()));
    }
}

/// Every pool alive in this process, summed — `None` when no door has a pool
/// here (the reference kernel's shape says the same: `pool: null`).
pub fn read_all() -> Option<Value> {
    let pools = POOLS.lock().unwrap_or_else(|p| p.into_inner());
    let live: Vec<Arc<Pool>> = pools.iter().filter_map(Weak::upgrade).collect();
    if live.is_empty() {
        return None;
    }
    let mut sum = json!({"ceiling": 0, "open": 0, "idle": 0, "busy": 0, "waiting": 0,
                         "opened_total": 0, "borrowed_total": 0, "shed_total": 0, "wait_max_ms": 0.0, "up_s": 0});
    for p in live {
        let r = p.read();
        for k in [
            "ceiling",
            "open",
            "idle",
            "busy",
            "waiting",
            "opened_total",
            "borrowed_total",
            "shed_total",
        ] {
            sum[k] = json!(sum[k].as_u64().unwrap_or(0) + r[k].as_u64().unwrap_or(0));
        }
        let wm = sum["wait_max_ms"]
            .as_f64()
            .unwrap_or(0.0)
            .max(r["wait_max_ms"].as_f64().unwrap_or(0.0));
        sum["wait_max_ms"] = json!(wm);
        sum["up_s"] = json!(sum["up_s"]
            .as_u64()
            .unwrap_or(0)
            .max(r["up_s"].as_u64().unwrap_or(0)));
    }
    Some(sum)
}

/// A ground on loan from the pool; back in the pool when dropped.
pub struct Line {
    g: Option<Ground>,
    pool: Arc<Pool>,
    _permit: OwnedSemaphorePermit,
}

impl Deref for Line {
    type Target = Ground;
    fn deref(&self) -> &Ground {
        self.g
            .as_ref()
            .expect("a line holds its ground until dropped")
    }
}

impl DerefMut for Line {
    fn deref_mut(&mut self) -> &mut Ground {
        self.g
            .as_mut()
            .expect("a line holds its ground until dropped")
    }
}

impl Drop for Line {
    fn drop(&mut self) {
        self.pool.busy.fetch_sub(1, Ordering::Relaxed);
        if let Some(g) = self.g.take() {
            self.pool.give_back(g);
        }
    }
}
