// PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp3, the ask road · 2026-09-22
// Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp6, the bodies' seam: `publish_delta` — the spawned bodies' words as they form · 2026-09-24
//! The Bridge feed's heart — mirrors `orreth_spine.bridgefeed.Feed` and
//! `consume_rail` (canon 0002): the one place the glass connects. The browser
//! never touches a broker; it receives small, pointer-only notices —
//! `{rev, kind, ref, message_id, at}` — never bodies, never prompts. Every
//! notice wears a monotone revision; a bounded ring replays what a
//! reconnecting client missed, or `since` says `None` — resync — when the gap
//! outlived the ring. The SSE framing lives in [`crate::bridge`].
//! P7 sp6: the feed also carries the spawned bodies' streaming DELTAS to
//! connected clients (`publish_delta`) — a body POSTs its words to the
//! kernel's `/delta` door as they form; never the ring, never a revision.

use crate::envelope::now_iso;
use crate::events::Reader;
use crate::rail_error::RailError;
use crate::world::World;
use serde_json::{json, Value};
use std::collections::VecDeque;
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::{Arc, Mutex};
use std::time::Duration;
use tokio::sync::broadcast;

struct Inner {
    rev: u64,
    ring: VecDeque<Value>,
    cap: usize,
}

/// The fan-out heart: a monotone revision, a bounded ring of recent
/// notices, and one broadcast channel every connected client listens on.
pub struct Feed {
    inner: Mutex<Inner>,
    tx: broadcast::Sender<Value>,
}

impl Feed {
    pub fn new(ring: usize) -> Feed {
        let (tx, _rx) = broadcast::channel(ring.max(16));
        Feed {
            inner: Mutex::new(Inner {
                rev: 0,
                ring: VecDeque::with_capacity(ring),
                cap: ring,
            }),
            tx,
        }
    }

    /// One notice: the next revision, into the ring, to every client.
    pub fn publish(&self, kind: &str, r#ref: &str, message_id: &str) -> Value {
        let notice = {
            let mut i = self.inner.lock().unwrap_or_else(|p| p.into_inner());
            i.rev += 1;
            let n = json!({"rev": i.rev, "kind": kind, "ref": r#ref, "message_id": message_id, "at": now_iso()});
            if i.ring.len() == i.cap {
                i.ring.pop_front();
            }
            i.ring.push_back(n.clone());
            n
        };
        let _ = self.tx.send(notice.clone());
        notice
    }

    /// P7 sp6: a body's words as they form — to CONNECTED clients only, never
    /// the ring, never a revision (`Feed.publish_delta`): the glass draws them
    /// live; the durable truth stays the reply behind the door.
    pub fn publish_delta(&self, r#ref: &str, text: &str) {
        let _ = self
            .tx
            .send(json!({"delta": true, "ref": r#ref, "text": text}));
    }

    /// A client's ear — subscribe BEFORE asking `since`, so nothing falls between.
    pub fn subscribe(&self) -> broadcast::Receiver<Value> {
        self.tx.subscribe()
    }

    /// Notices after `rev` — or `None` when the gap outlives the ring (the
    /// caller must resync from an authoritative snapshot).
    pub fn since(&self, rev: u64) -> Option<Vec<Value>> {
        let i = self.inner.lock().unwrap_or_else(|p| p.into_inner());
        if rev >= i.rev {
            return Some(Vec::new());
        }
        let first = i.ring.front().and_then(|n| n["rev"].as_u64());
        match first {
            None => None,
            Some(f) if f > rev + 1 => None,
            _ => Some(
                i.ring
                    .iter()
                    .filter(|n| n["rev"].as_u64().unwrap_or(0) > rev)
                    .cloned()
                    .collect(),
            ),
        }
    }

    pub fn rev(&self) -> u64 {
        self.inner.lock().unwrap_or_else(|p| p.into_inner()).rev
    }

    /// Connected clients.
    pub fn clients(&self) -> usize {
        self.tx.receiver_count()
    }
}

/// The rail-side of the gateway: read committed facts, publish pointer-only
/// notices. Position loss here is harmless — revisions are gateway-local and
/// the glass fetches truth through doors anyway. `ready` fires once the
/// broker has assigned partitions; topics are DECLARED before subscribing.
pub async fn consume_rail(
    feed: Arc<Feed>,
    w: &World,
    topics: &[&str],
    group: &str,
    stop: Arc<AtomicBool>,
    ready: Arc<AtomicBool>,
) -> Result<(), RailError> {
    let reader = Reader::open(&w.kafka, group, topics, false).await?;
    while !stop.load(Ordering::Relaxed) {
        if !ready.load(Ordering::Relaxed) && reader.assigned() {
            ready.store(true, Ordering::Relaxed);
        }
        let Some(p) = reader.next(Duration::from_millis(300)).await? else {
            continue;
        };
        if let Some(env) = &p.env {
            let r = &env["payload"]["ref"];
            let r#ref = if r.is_null() {
                String::new()
            } else {
                crate::py::python_str(r)
            };
            feed.publish(
                env["type"].as_str().unwrap_or_default(),
                &r#ref,
                env["message_id"].as_str().unwrap_or_default(),
            );
        }
        reader.commit(&p)?;
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn the_ring_replays_or_says_resync() {
        let f = Feed::new(3);
        assert_eq!(f.since(0), Some(vec![]));
        for i in 0..5 {
            f.publish("k", &format!("r{i}"), "m");
        }
        assert_eq!(f.rev(), 5);
        assert_eq!(f.since(5), Some(vec![]));
        assert_eq!(f.since(1), None); // the ring holds 3..5; 2 is gone
        let got = f.since(2).unwrap();
        assert_eq!(
            got.iter()
                .map(|n| n["rev"].as_u64().unwrap())
                .collect::<Vec<_>>(),
            [3, 4, 5]
        );
        assert_eq!(f.since(4).unwrap().len(), 1);
    }
}
