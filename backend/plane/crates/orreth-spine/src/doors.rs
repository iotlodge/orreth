// PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch row 4, PANEL sp3: per-door latency in the Monitoring · 2026-09-28
//! `orreth.doors/1` — how long every door takes, in the kernel's own words
//! (canon 0005 row 4, JB's lock 3 of "the kernel that lasts": *a p50 and p95
//! per door, judged by the same beat that judges watches, so the performance
//! law is watched before a walk finds it*).
//!
//! The pure half, measured by `doors-v0.json` on both kernels: a door's NAME
//! (`door_name` — the method and the route as the router spells it, an id
//! folded to `:id`, a stranger's path folded to `other` so a scanner never
//! grows the table) and the FOLD (`fold` — nearest-rank p50 · p95 · the max
//! over the samples, in integer arithmetic so both languages pick the same
//! sample). The live half is the ring below: every knock this process served
//! lands as one sample under its door's name, the last [`KEEP`] kept, the
//! reading folded over the last [`WINDOW_S`] seconds so a slow door an hour
//! ago does not hold the lamp red now. The Monitoring reads it (`monitor::
//! snapshot` → `doors` and `values.door_p95_ms`), the judge judges it on the
//! intent beat, the glass draws it under PERFORMANCE.
//!
//! Honest scope: the ring is this PROCESS's — the doors it served. Two kernels
//! lit in one process (a test) share one reading.

use serde_json::{json, Value};
use std::collections::{HashMap, VecDeque};
use std::sync::{LazyLock, Mutex};
use std::time::Instant;

/// Samples kept per door.
pub const KEEP: usize = 256;
/// The reading's window: a sample older than this is not folded.
pub const WINDOW_S: u64 = 600;
/// A door whose p95 crosses this is slow by the standing law (≤ 1 s cold).
pub const SLOW_MS: f64 = 1000.0;

/// The first path segments the kernel answers (both kernels' doors; anything
/// else is `other`).
const KNOWN: &[&str] = &[
    "",
    "index.html",
    "feed",
    "health",
    "shadow",
    "ask",
    "fact",
    "asks",
    "residents",
    "crew",
    "sessions",
    "session",
    "recall",
    "export",
    "digest",
    "guide",
    "proof",
    "analyzer",
    "services",
    "intentions",
    "levers",
    "markers",
    "monitor",
    "profile",
    "world",
    "seam",
    "schedules",
    "harness",
    "delta",
    "bodies",
    "minds",
    "confirm",
    "enroll",
    "seat",
    "join",
    "mitl",
    "impact",
    "mark",
];

/// A door's name: `METHOD /route` as the router spells it. The second
/// segment is folded to `:id` after `ask · fact · session · digest · join`
/// and to `:runner` after `schedules` (except the fixed `/schedules/rest`);
/// deeper segments are dropped; a first segment the kernel does not answer is
/// `other` (a scanner never grows the table). Queries are not part of a name.
pub fn door_name(method: &str, path: &str) -> String {
    let path = path.split('?').next().unwrap_or_default();
    let mut segs = path.trim_start_matches('/').splitn(3, '/');
    let first = segs.next().unwrap_or_default();
    let second = segs.next();
    let method = method.to_ascii_uppercase();
    if !KNOWN.contains(&first) {
        return format!("{method} other");
    }
    let mut name = format!("{method} /{first}");
    if let Some(s) = second.filter(|s| !s.is_empty()) {
        let folded = match first {
            "ask" | "fact" | "session" | "digest" | "join" => ":id",
            "schedules" if s != "rest" => ":runner",
            _ => s,
        };
        name.push('/');
        name.push_str(folded);
    }
    name
}

/// Nearest-rank percentile over `sorted` (ascending): the sample at rank
/// `ceil(p · n / 100)`, in integer arithmetic. `None` on no samples.
pub fn percentile(sorted: &[f64], p: usize) -> Option<f64> {
    if sorted.is_empty() {
        return None;
    }
    let n = sorted.len();
    let rank = (p * n).div_ceil(100).max(1);
    sorted.get(rank - 1).copied()
}

/// The fold of one door's samples: how many, the p50, the p95 and the max —
/// each an actual sample (no arithmetic on the values), `null`s on none.
pub fn fold(samples_ms: &[f64]) -> Value {
    let mut sorted: Vec<f64> = samples_ms
        .iter()
        .copied()
        .filter(|v| v.is_finite())
        .collect();
    sorted.sort_by(|a, b| a.partial_cmp(b).unwrap_or(std::cmp::Ordering::Equal));
    json!({
        "n": sorted.len(),
        "p50_ms": percentile(&sorted, 50),
        "p95_ms": percentile(&sorted, 95),
        "max_ms": sorted.last().copied(),
    })
}

/// One door's reading: its name and its fold.
pub fn door_view(door: &str, samples_ms: &[f64]) -> Value {
    let mut v = fold(samples_ms);
    v["door"] = json!(door);
    v
}

/// The readings ordered the slowest first (by p95, then by name), so the
/// glass and a human read the door that needs looking at first.
pub fn slowest_first(mut reads: Vec<Value>) -> Vec<Value> {
    reads.sort_by(|a, b| {
        let pa = a["p95_ms"].as_f64().unwrap_or(0.0);
        let pb = b["p95_ms"].as_f64().unwrap_or(0.0);
        pb.partial_cmp(&pa)
            .unwrap_or(std::cmp::Ordering::Equal)
            .then_with(|| a["door"].as_str().cmp(&b["door"].as_str()))
    });
    reads
}

/// The metric the watches read: the slowest door's p95 now (0 when no door
/// has been knocked on in the window).
pub fn slowest_p95(reads: &[Value]) -> f64 {
    reads
        .iter()
        .filter_map(|r| r["p95_ms"].as_f64())
        .fold(0.0, f64::max)
}

/// The ring of samples — this process's doors.
#[derive(Default)]
pub struct Doors {
    rings: Mutex<HashMap<String, VecDeque<(Instant, f64)>>>,
}

impl Doors {
    /// One knock served: `ms` under the door's name.
    pub fn record(&self, door: &str, ms: f64) {
        let mut rings = self.rings.lock().unwrap_or_else(|p| p.into_inner());
        let ring = rings.entry(door.to_string()).or_default();
        ring.push_back((Instant::now(), ms));
        while ring.len() > KEEP {
            ring.pop_front();
        }
    }

    /// Every door's reading over the window, the slowest first.
    pub fn read(&self) -> Vec<Value> {
        let now = Instant::now();
        let rings = self.rings.lock().unwrap_or_else(|p| p.into_inner());
        let reads = rings
            .iter()
            .filter_map(|(door, ring)| {
                let recent: Vec<f64> = ring
                    .iter()
                    .filter(|(at, _)| now.duration_since(*at).as_secs() < WINDOW_S)
                    .map(|(_, ms)| *ms)
                    .collect();
                (!recent.is_empty()).then(|| door_view(door, &recent))
            })
            .collect();
        slowest_first(reads)
    }

    /// Forget everything (a test's clean slate).
    pub fn clear(&self) {
        self.rings.lock().unwrap_or_else(|p| p.into_inner()).clear();
    }
}

/// This process's ring.
pub static DOORS: LazyLock<Doors> = LazyLock::new(Doors::default);

/// One knock served by this process.
pub fn record(method: &str, path: &str, ms: f64) {
    DOORS.record(&door_name(method, path), ms);
}

/// This process's doors, the slowest first.
pub fn read() -> Vec<Value> {
    DOORS.read()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn a_door_is_named_as_the_router_spells_it() {
        assert_eq!(door_name("get", "/monitor"), "GET /monitor");
        assert_eq!(door_name("GET", "/ask/ask_1a2b3c?x=1"), "GET /ask/:id");
        assert_eq!(door_name("GET", "/fact/0123abcd"), "GET /fact/:id");
        assert_eq!(
            door_name("GET", "/schedules/librarian"),
            "GET /schedules/:runner"
        );
        assert_eq!(door_name("POST", "/schedules/rest"), "POST /schedules/rest");
        assert_eq!(door_name("GET", "/markers/kinds"), "GET /markers/kinds");
        assert_eq!(door_name("GET", "/"), "GET /");
        assert_eq!(door_name("GET", "/wp-admin/x"), "GET other");
        assert_eq!(door_name("GET", "/join/j_1/deeper/still"), "GET /join/:id");
    }

    #[test]
    fn the_fold_is_nearest_rank_over_actual_samples() {
        let s: Vec<f64> = (1..=20).map(|i| i as f64).collect();
        let f = fold(&s);
        assert_eq!(f["n"], json!(20));
        assert_eq!(f["p50_ms"], json!(10.0));
        assert_eq!(f["p95_ms"], json!(19.0));
        assert_eq!(f["max_ms"], json!(20.0));
        let one = fold(&[3.25]);
        assert_eq!(
            (one["p50_ms"].clone(), one["p95_ms"].clone()),
            (json!(3.25), json!(3.25))
        );
        let none = fold(&[]);
        assert_eq!(none["n"], json!(0));
        assert!(none["p50_ms"].is_null() && none["max_ms"].is_null());
    }

    #[test]
    fn the_ring_keeps_the_last_samples_and_reads_the_slowest_first() {
        let d = Doors::default();
        for i in 0..(KEEP + 10) {
            d.record("GET /monitor", i as f64);
        }
        d.record("GET /ask/:id", 5000.0);
        let r = d.read();
        assert_eq!(r[0]["door"], json!("GET /ask/:id"));
        assert_eq!(r[1]["n"], json!(KEEP));
        assert_eq!(r[1]["max_ms"], json!((KEEP + 9) as f64));
        assert_eq!(slowest_p95(&r), 5000.0);
        d.clear();
        assert!(d.read().is_empty());
        assert_eq!(slowest_p95(&[]), 0.0);
    }
}
