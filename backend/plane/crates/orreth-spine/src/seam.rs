// PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp7, cells · partition · isolation · hardening · 2026-09-25
// Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp8, the routed ask carries the asker's profile slice (W58) · 2026-09-26
//! THE SEAM between cells (canon 0002 rule 8 · JB's locks 2026-09-25): two
//! cells that NAME each other as peers (`SPINE_PEERS`) speak over one door,
//! `POST /seam`, in messages SIGNED by their kernels' own selves — the peer's
//! DID pinned on first sight, every message checked through every fence
//! (`cells::seam_verify`: the pin, the signature, the nonce, the clock
//! window, the epoch) and a knock ceiling per signer. COMMANDS ROUTE HOME:
//! an ask addressed "librarian@two, …" is filed here as ROUTED, carried to
//! cell two, served there by its own body, and its answer carried back as a
//! reply on the ask the human asked. SELECTED FACTS REPLICATE: a peer's
//! world card and its roster ride every hello and stand on the peer's row
//! with their lag; the answers to routed asks ride the seam as facts. Under
//! PARTITION (the peer does not answer) nothing is lost: every outbound
//! message waits in `spine_seam_out` with a backoff, the ask reads PARKED in
//! plain words, and the moment the peer answers again the message goes and
//! the ask resumes — never doubled (a nonce is spent once; a reply lands
//! once). The human can always stop a routed ask (rule 11): the stop rides
//! the seam first of all and the home cell rests the ask at its next safe
//! boundary. A re-homed universe advances its EPOCH; a message wearing an
//! old one is refused and the sender re-hears the world before it speaks
//! again (the fencing law at the action boundary).

use crate::asks::{self, Submit, JOURNEY, REPLY};
use crate::cells::{self, Peer};
use crate::envelope::{self, Mint};
use crate::ground::Ground;
use crate::kernel_self::KernelSelf;
use crate::outbox;
use crate::presence;
use crate::rail_error::RailError;
use crate::world::{refused, token_hex, RoadError, World};
use serde_json::{json, Value};
use std::collections::HashMap;
use std::sync::Mutex;
use std::time::{Duration, SystemTime, UNIX_EPOCH};
use tokio::sync::Notify;

/// The seam's tables and the columns it adds beside the ask road's (both spines
/// declare them; `IF NOT EXISTS` keeps two spines on one ground in agreement).
pub const SEAM_DDL: &[&str] = &[
    "CREATE TABLE IF NOT EXISTS spine_seam_out ( out_id bigserial PRIMARY KEY, cell text NOT NULL, scope \
     text NOT NULL, kind text NOT NULL, body text NOT NULL, ref text, attempts int NOT NULL DEFAULT 0, \
     next_at timestamptz NOT NULL DEFAULT now(), sent_at timestamptz, last_error text, added_at \
     timestamptz NOT NULL DEFAULT now())",
    "ALTER TABLE spine_asks ADD COLUMN IF NOT EXISTS home_cell text",
    "ALTER TABLE spine_asks ADD COLUMN IF NOT EXISTS remote_id text",
    "ALTER TABLE spine_asks ADD COLUMN IF NOT EXISTS seam_side text",
    "ALTER TABLE spine_asks ADD COLUMN IF NOT EXISTS seam_sent boolean NOT NULL DEFAULT false",
    "ALTER TABLE spine_peers ADD COLUMN IF NOT EXISTS picture text",
];

/// How often a peer is greeted when all is well.
pub const HELLO_EVERY_S: f64 = 10.0;
/// The seam's HTTP patience.
pub const SEAM_TIMEOUT: Duration = Duration::from_secs(5);
pub const KERNEL: &str = "the kernel";

/// What came back from a peer, or why nothing did.
#[derive(Debug)]
pub enum SeamMiss {
    /// The peer did not answer at all (dark, or the road to it).
    Transport(String),
    /// The peer answered with a refusal: its status and its words.
    Refused(u16, Value),
}

impl std::fmt::Display for SeamMiss {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            SeamMiss::Transport(w) => f.write_str(w),
            SeamMiss::Refused(s, b) => write!(f, "refused {s}: {b}"),
        }
    }
}

/// The seam this kernel keeps: who it is, whom it names, how it signs.
pub struct Seam {
    pub cell: String,
    pub peers: Vec<Peer>,
    pub kernel: KernelSelf,
    pub door: String,
    pub world: World,
    /// W52: every clock a human reads is the human's (`SPINE_HUMAN_ZONE`).
    pub zone: String,
    /// Raised when something is queued — the beat drains at once, not on its next tick.
    pub wake: Notify,
    ceilings: Mutex<HashMap<String, (f64, f64)>>,
}

fn now_f() -> f64 {
    SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap_or_default()
        .as_secs_f64()
}

/// The ground's clock in the human's zone, `HH:MM` — the same tzdata the Python spine's ZoneInfo reads.
async fn hhmm_now(g: &Ground, zone: &str) -> String {
    g.client()
        .query_one(
            "SELECT to_char(clock_timestamp() AT TIME ZONE $1, 'HH24:MI')",
            &[&zone],
        )
        .await
        .map(|r| r.get::<_, String>(0))
        .unwrap_or_else(|_| "--:--".into())
}

impl Seam {
    pub fn new(
        cell: &str,
        peers: Vec<Peer>,
        kernel: KernelSelf,
        door: &str,
        world: World,
        zone: &str,
    ) -> Seam {
        Seam {
            cell: cell.to_string(),
            peers,
            kernel,
            door: door.to_string(),
            world,
            zone: zone.to_string(),
            wake: Notify::new(),
            ceilings: Mutex::new(HashMap::new()),
        }
    }

    /// The peer this cell names by that name.
    pub fn named(&self, cell: &str) -> Option<&Peer> {
        self.peers.iter().find(|p| p.cell == cell)
    }

    /// The knock ceiling per signer (0071): a token bucket, spent at the door.
    pub fn knock(&self, who: &str) -> bool {
        let now = now_f();
        let mut m = self.ceilings.lock().unwrap_or_else(|p| p.into_inner());
        let (tokens, last) = m.get(who).copied().unwrap_or((cells::CEILING_BURST, now));
        let (ok, after) =
            cells::ceiling(tokens, last, now, cells::CEILING_RATE, cells::CEILING_BURST);
        m.insert(who.to_string(), (after, now));
        ok
    }

    /// Every peer this cell names stands on the ground from the first beat.
    pub async fn ensure_peers(&self, g: &Ground) -> Result<(), RoadError> {
        for p in &self.peers {
            g.client()
                .execute(
                    "INSERT INTO spine_peers (cell, scope, door) VALUES ($1, $2, $3) ON CONFLICT (cell, scope) DO \
                     UPDATE SET door = EXCLUDED.door",
                    &[&p.cell, &self.world.scope, &p.door],
                )
                .await?;
        }
        Ok(())
    }

    /// My own hello: my door, my world, my cell, my epoch, my self, my roster.
    pub async fn hello_body(&self, g: &Ground) -> Result<Value, RoadError> {
        let epoch = crate::cells_live::epoch(g, &self.world.scope).await?;
        let roster: Vec<Value> = presence::roster(g, &self.world.scope)
            .await?
            .iter()
            .map(|b| json!({"name": b["name"], "kind": b["kind"], "alive": b["alive"]}))
            .collect();
        Ok(
            json!({"door": self.door, "world": self.world.scope, "cell": self.cell, "epoch": epoch,
                  "kernel": self.kernel.did(), "roster": roster}),
        )
    }

    /// A message for a peer, signed by this kernel's self, wearing my epoch.
    pub async fn sign(
        &self,
        g: &Ground,
        to: &str,
        kind: &str,
        body: Value,
    ) -> Result<Value, RoadError> {
        let epoch = crate::cells_live::epoch(g, &self.world.scope).await?;
        let msg = cells::seam_message(
            &self.cell,
            &self.world.scope,
            to,
            epoch,
            kind,
            body,
            &format!("n_{}", token_hex(12)),
            &envelope::now_iso(),
        );
        Ok(cells::seam_sign(&msg, &self.kernel))
    }

    /// One knock on a peer's door (blocking HTTP off the runtime): 200 → its answer.
    pub async fn post(&self, door: &str, signed: Value) -> Result<Value, SeamMiss> {
        let url = format!("{door}/seam");
        tokio::task::spawn_blocking(move || {
            let agent = ureq::AgentBuilder::new().timeout(SEAM_TIMEOUT).build();
            let res = agent
                .post(&url)
                .set("content-type", "application/json")
                .send_string(&signed.to_string());
            let resp = match res {
                Ok(r) => r,
                Err(ureq::Error::Status(_, r)) => r,
                Err(ureq::Error::Transport(t)) => {
                    return Err(SeamMiss::Transport(format!(
                        "{url} did not answer: {}",
                        t.message().unwrap_or("no route")
                    )))
                }
            };
            let status = resp.status();
            let text = resp.into_string().unwrap_or_default();
            let body: Value = serde_json::from_str(&text).unwrap_or(json!({"error": text}));
            if status == 200 {
                Ok(body)
            } else {
                Err(SeamMiss::Refused(status, body))
            }
        })
        .await
        .map_err(|e| SeamMiss::Transport(format!("the seam call was lost: {e}")))?
    }

    /// The peer's row, as the ground remembers it.
    async fn peer_row(&self, g: &Ground, cell: &str) -> Result<Option<PeerRow>, RoadError> {
        let r = g
            .client()
            .query_opt(
                "SELECT door, did, world, epoch, unreachable_since IS NOT NULL, \
                 extract(epoch FROM (clock_timestamp() - coalesce(last_seen, 'epoch'::timestamptz)))::float8 \
                 FROM spine_peers WHERE cell = $1 AND scope = $2",
                &[&cell, &self.world.scope],
            )
            .await?;
        Ok(r.map(|r| PeerRow {
            cell: cell.to_string(),
            door: r.get(0),
            did: r.get(1),
            epoch: r.get::<_, Option<i32>>(3).map(|e| e as i64),
            unreachable: r.get(4),
            since_heard_s: r.get(5),
        }))
    }

    /// What a peer's answer (or its hello) teaches: pin its self on first
    /// sight, keep its world and epoch, mark it heard. A pinned self that
    /// changed is NOT taken — it is refused in words.
    async fn learn(&self, g: &Ground, cell: &str, signed: &Value) -> Result<(), RoadError> {
        let did = signed["signer"].as_str().unwrap_or_default().to_string();
        let world = signed["world"].as_str().map(str::to_string);
        let epoch = signed["epoch"].as_i64().unwrap_or(1) as i32;
        let picture = if signed["kind"] == json!("hello") {
            Some(signed["body"]["roster"].to_string())
        } else {
            None
        };
        g.client()
            .execute(
                "UPDATE spine_peers SET did = coalesce(did, $3), world = coalesce($4, world), epoch = $5, \
                 pinned_at = coalesce(pinned_at, clock_timestamp()), last_seen = clock_timestamp(), \
                 unreachable_since = NULL, picture = coalesce($6, picture) WHERE cell = $1 AND scope = $2",
                &[&cell, &self.world.scope, &did, &world, &epoch, &picture],
            )
            .await?;
        Ok(())
    }

    async fn unreachable(&self, g: &Ground, cell: &str) -> Result<(), RoadError> {
        g.client()
            .execute(
                "UPDATE spine_peers SET unreachable_since = coalesce(unreachable_since, clock_timestamp()) \
                 WHERE cell = $1 AND scope = $2",
                &[&cell, &self.world.scope],
            )
            .await?;
        Ok(())
    }

    /// Greet a peer: my hello over, its hello back, its self pinned on first sight.
    pub async fn hello(&self, g: &Ground, cell: &str) -> Result<bool, RoadError> {
        let Some(row) = self.peer_row(g, cell).await? else {
            return Ok(false);
        };
        let signed = self
            .sign(g, cell, "hello", self.hello_body(g).await?)
            .await?;
        match self.post(&row.door, signed).await {
            Ok(answer) => {
                // its answer is a signed hello of its own: checked through the same fences
                let verdict = self.verify_answer(g, &row, &answer).await?;
                if verdict != "ok" {
                    eprintln!("cell {cell}'s hello refused: {verdict}");
                    self.unreachable(g, cell).await?;
                    return Ok(false);
                }
                self.learn(g, cell, &answer).await?;
                Ok(true)
            }
            Err(SeamMiss::Refused(status, body)) => {
                eprintln!("cell {cell} refused my hello ({status}): {body}");
                self.unreachable(g, cell).await?;
                Ok(false)
            }
            Err(SeamMiss::Transport(w)) => {
                if !row.unreachable {
                    eprintln!("cell {cell} is out of reach: {w}");
                }
                self.unreachable(g, cell).await?;
                Ok(false)
            }
        }
    }

    /// A peer's answer checked: the pin (first sight pins), the signature, the
    /// nonce, the clock; an answer's epoch may run ahead of my pin (a hello
    /// teaches), never behind it.
    async fn verify_answer(
        &self,
        g: &Ground,
        row: &PeerRow,
        answer: &Value,
    ) -> Result<String, RoadError> {
        let pinned = match &row.did {
            Some(d) => Some(d.clone()),
            None => answer["signer"].as_str().map(str::to_string), // first sight
        };
        let nonce = answer["nonce"].as_str().unwrap_or_default().to_string();
        let seen = self.nonce_seen(g, &nonce).await?;
        let seen_list: Vec<String> = if seen { vec![nonce.clone()] } else { vec![] };
        let verdict = cells::seam_verify(
            answer,
            pinned.as_deref(),
            &envelope::now_iso(),
            &seen_list,
            None,
        );
        if verdict != "ok" {
            return Ok(verdict);
        }
        if answer["from"].as_str() != Some(&row.cell) || answer["to"].as_str() != Some(&self.cell) {
            return Ok("not for this cell".into());
        }
        if let Some(mine) = row.epoch {
            let theirs = answer["epoch"].as_i64().unwrap_or(0);
            if theirs < mine {
                return Ok("stale epoch".into());
            }
        }
        self.spend_nonce(g, &nonce).await?;
        Ok("ok".into())
    }

    async fn nonce_seen(&self, g: &Ground, nonce: &str) -> Result<bool, RoadError> {
        let r = g
            .client()
            .query_opt(
                "SELECT 1 FROM spine_seam_nonces WHERE nonce = $1",
                &[&nonce],
            )
            .await?;
        Ok(r.is_some())
    }

    async fn spend_nonce(&self, g: &Ground, nonce: &str) -> Result<(), RoadError> {
        g.client()
            .execute(
                "INSERT INTO spine_seam_nonces (nonce, scope) VALUES ($1, $2) ON CONFLICT DO NOTHING",
                &[&nonce, &self.world.scope],
            )
            .await?;
        Ok(())
    }

    // ---- outbound -----------------------------------------------------------------------

    /// Queue a message for a peer; the beat carries it (now, if it can).
    pub async fn enqueue(
        &self,
        g: &Ground,
        cell: &str,
        kind: &str,
        body: &Value,
        r#ref: Option<&str>,
    ) -> Result<i64, RoadError> {
        let r = g
            .client()
            .query_one(
                "INSERT INTO spine_seam_out (cell, scope, kind, body, ref) VALUES ($1, $2, $3, $4, $5) RETURNING out_id",
                &[&cell, &self.world.scope, &kind, &body.to_string(), &r#ref],
            )
            .await?;
        self.wake.notify_one();
        Ok(r.get(0))
    }

    /// Carry every due message to its peer; a miss waits with a backoff and
    /// parks the ask it carries; a stale-epoch refusal re-hears the peer first.
    pub async fn drain(&self, g: &mut Ground) -> Result<(), RoadError> {
        let rows = g
            .client()
            .query(
                "SELECT out_id, cell, kind, body, ref, attempts FROM spine_seam_out WHERE scope = $1 AND sent_at IS \
                 NULL AND next_at <= clock_timestamp() ORDER BY out_id LIMIT 50",
                &[&self.world.scope],
            )
            .await?;
        for r in rows {
            let (out_id, cell, kind, body, r#ref, attempts): (
                i64,
                String,
                String,
                String,
                Option<String>,
                i32,
            ) = (r.get(0), r.get(1), r.get(2), r.get(3), r.get(4), r.get(5));
            let body: Value = serde_json::from_str(&body).unwrap_or(json!({}));
            let Some(row) = self.peer_row(g, &cell).await? else {
                self.fail_row(g, out_id, attempts, "no such peer").await?;
                continue;
            };
            let signed = self.sign(g, &cell, &kind, body.clone()).await?;
            match self.post(&row.door, signed).await {
                Ok(answer) => {
                    let verdict = self.verify_answer(g, &row, &answer).await?;
                    if verdict != "ok" {
                        self.fail_row(g, out_id, attempts, &format!("its answer: {verdict}"))
                            .await?;
                        continue;
                    }
                    self.learn(g, &cell, &answer).await?;
                    g.client()
                        .execute(
                            "UPDATE spine_seam_out SET sent_at = clock_timestamp(), last_error = NULL WHERE out_id = $1",
                            &[&out_id],
                        )
                        .await?;
                    if kind == "ask" {
                        if let Some(id) = r#ref.as_deref() {
                            self.ask_went(g, id, &cell, &answer["body"]).await?;
                        }
                    }
                }
                Err(SeamMiss::Refused(409, b)) => {
                    // an epoch fence: hear the peer again, then try once more
                    self.fail_row(g, out_id, attempts, &format!("epoch: {}", b["error"]))
                        .await?;
                    let _ = self.hello(g, &cell).await;
                }
                Err(SeamMiss::Refused(status, b)) => {
                    // the one face, or words: said on the ask, the row rests
                    let words = format!(
                        "cell {cell} refused it ({status}): {}",
                        b["error"].as_str().unwrap_or("not confirmed")
                    );
                    g.client()
                        .execute(
                            "UPDATE spine_seam_out SET sent_at = clock_timestamp(), last_error = $2 WHERE out_id = $1",
                            &[&out_id, &words],
                        )
                        .await?;
                    if kind == "ask" {
                        if let Some(id) = r#ref.as_deref() {
                            self.ask_refused(g, id, &words).await?;
                        }
                    }
                }
                Err(SeamMiss::Transport(w)) => {
                    self.fail_row(g, out_id, attempts, &w).await?;
                    self.unreachable(g, &cell).await?;
                    if kind == "ask" {
                        if let Some(id) = r#ref.as_deref() {
                            self.ask_parked(g, id, &cell).await?;
                        }
                    }
                }
            }
        }
        Ok(())
    }

    async fn fail_row(
        &self,
        g: &Ground,
        out_id: i64,
        attempts: i32,
        why: &str,
    ) -> Result<(), RoadError> {
        let wait = crate::body::backoff_s((attempts + 1) as i64);
        g.client()
            .execute(
                "UPDATE spine_seam_out SET attempts = attempts + 1, last_error = $2, next_at = clock_timestamp() + \
                 make_interval(secs => $3::float8) WHERE out_id = $1",
                &[&out_id, &why, &wait],
            )
            .await?;
        Ok(())
    }

    // ---- the routed ask, origin side ------------------------------------------------------

    /// File an ask addressed to a body in a peer cell: the row here (ROUTED),
    /// its journey said, the message queued for the peer — one motion.
    pub async fn route_ask(
        &self,
        g: &mut Ground,
        w: &World,
        cell: &str,
        name: &str,
        s: &Submit,
    ) -> Result<String, RoadError> {
        if self.named(cell).is_none() {
            return Err(refused(format!(
                "no cell named '{cell}' is a peer of this one — SPINE_PEERS names the cells this kernel may speak to"
            )));
        }
        let ask_id = format!("ask_{}", token_hex(8));
        let target = format!("{name}@{cell}");
        let mid = crate::markers_live::new_id();
        let marker =
            json!({"kind": "objective", "id": mid, "parent": s.parent_marker, "by": s.person});
        let note = format!("{KERNEL}: routed home to cell {cell} — {name} answers there");
        let j = Mint {
            kind: "event".into(),
            r#type: JOURNEY.into(),
            universe_id: w.scope.clone(),
            scope_path: w.scope.clone(),
            payload: json!({"ref": ask_id, "hash": "sha256:-", "note": note}),
            correlation_id: Some(ask_id.clone()),
            authority_chain: Some(vec![s.person.clone(), KERNEL.to_string()]),
            aggregate: Some(json!({"type": "ask", "id": ask_id, "sequence": 1})),
            marker: Some(marker),
        }
        .mint()?;
        let raw = envelope::encode(&j)?;
        let (a, text, person, t, sc, ses, mk, pa, cell_s) = (
            ask_id.clone(),
            s.text.clone(),
            s.person.clone(),
            target.clone(),
            w.scope.clone(),
            s.session.clone(),
            mid.clone(),
            s.parent_marker.clone(),
            cell.to_string(),
        );
        outbox::commit_with_outbox(g, &raw, j["message_id"].as_str().unwrap_or_default(), None, async move |tx| {
            crate::markers_live::insert(tx, &mk, "objective", pa.as_deref(), &a, &person, None, &sc)
                .await
                .map_err(|e| RailError::Refused(e.to_string()))?;
            tx.execute(
                "INSERT INTO spine_asks (ask_id, text, person, target, scope, session, state, marker, status, \
                 home_cell, seam_side) VALUES ($1, $2, $3, $4, $5, $6, 'in', $7, 'routed', $8, 'origin')",
                &[&a, &text, &person, &t, &sc, &ses, &mk, &cell_s],
            )
            .await?;
            Ok(())
        })
        .await?;
        // P7 sp8 (W58): the asker's profile slice RIDES with the ask — the far cell answers for their
        // place and clock and stores nothing about them (it lands on the ask's row there, never in its profile)
        let carried = crate::profile_live::carry(g, w, &s.person).await?;
        let body = json!({"ask_id": ask_id, "text": cells::strip_home(&s.text), "person": s.person,
                          "session": s.session, "at": envelope::now_iso(), "profile": carried});
        self.enqueue(g, cell, "ask", &body, Some(&ask_id)).await?;
        Ok(ask_id)
    }

    /// The peer took the ask: remember its id there; a parked ask resumes in words.
    async fn ask_went(
        &self,
        g: &mut Ground,
        ask_id: &str,
        cell: &str,
        answer: &Value,
    ) -> Result<(), RoadError> {
        let remote = answer["ask_id"].as_str().map(str::to_string);
        let row = g
            .client()
            .query_opt(
                "SELECT status, target FROM spine_asks WHERE ask_id = $1",
                &[&ask_id],
            )
            .await?;
        let Some(row) = row else { return Ok(()) };
        let (status, target): (String, Option<String>) = (row.get(0), row.get(1));
        g.client()
            .execute(
                "UPDATE spine_asks SET remote_id = coalesce($2, remote_id), status = CASE WHEN status = 'parked' THEN 'routed' \
                 ELSE status END WHERE ask_id = $1",
                &[&ask_id, &remote],
            )
            .await?;
        if status == "parked" {
            let name = target
                .as_deref()
                .and_then(|t| t.split('@').next())
                .unwrap_or("it")
                .to_string();
            self.journey(
                g,
                ask_id,
                &format!("{KERNEL}: {}", cells::resumed_words(&name, cell)),
            )
            .await?;
        }
        Ok(())
    }

    /// The peer is out of reach: the ask reads PARKED, said once in plain words.
    async fn ask_parked(&self, g: &mut Ground, ask_id: &str, cell: &str) -> Result<(), RoadError> {
        let row = g
            .client()
            .query_opt(
                "SELECT status, target FROM spine_asks WHERE ask_id = $1",
                &[&ask_id],
            )
            .await?;
        let Some(row) = row else { return Ok(()) };
        let (status, target): (String, Option<String>) = (row.get(0), row.get(1));
        if status != "routed" {
            return Ok(());
        }
        g.client()
            .execute(
                "UPDATE spine_asks SET status = 'parked' WHERE ask_id = $1",
                &[&ask_id],
            )
            .await?;
        let name = target
            .as_deref()
            .and_then(|t| t.split('@').next())
            .unwrap_or("it")
            .to_string();
        self.journey(
            g,
            ask_id,
            &format!(
                "{KERNEL}: {}",
                cells::park_words(&name, cell, &hhmm_now(g, &self.zone).await)
            ),
        )
        .await
    }

    async fn ask_refused(
        &self,
        g: &mut Ground,
        ask_id: &str,
        words: &str,
    ) -> Result<(), RoadError> {
        self.settle(
            g,
            ask_id,
            "refused",
            words,
            None,
            &[KERNEL.to_string()],
            &format!("{KERNEL}: {words}"),
        )
        .await
    }

    /// A journey note on an ask — a fact, through the outbox.
    async fn journey(&self, g: &mut Ground, ask_id: &str, note: &str) -> Result<(), RoadError> {
        let w = &self.world;
        let note_s = note.to_string();
        let (a, sc) = (ask_id.to_string(), w.scope.clone());
        let e = Mint {
            kind: "event".into(),
            r#type: JOURNEY.into(),
            universe_id: sc.clone(),
            scope_path: sc.clone(),
            payload: json!({"ref": ask_id, "hash": "sha256:-", "note": note_s}),
            correlation_id: Some(a.clone()),
            authority_chain: Some(vec![KERNEL.to_string()]),
            aggregate: None,
            marker: None,
        }
        .mint()?;
        let raw = envelope::encode(&e)?;
        outbox::commit_with_outbox(
            g,
            &raw,
            e["message_id"].as_str().unwrap_or_default(),
            None,
            async |_tx| Ok(()),
        )
        .await?;
        Ok(())
    }

    /// A reply (or a refusal, or a rest) lands on an ask: the row, its journey
    /// note and its reply fact in ONE transaction — the feed carries the notice.
    #[allow(clippy::too_many_arguments)]
    async fn settle(
        &self,
        g: &mut Ground,
        ask_id: &str,
        status: &str,
        reply: &str,
        served_by: Option<&str>,
        chain: &[String],
        note: &str,
    ) -> Result<(), RoadError> {
        let w = self.world.clone();
        let (a, st, rp, sb, ch) = (
            ask_id.to_string(),
            status.to_string(),
            reply.to_string(),
            served_by.map(str::to_string),
            chain.to_vec(),
        );
        let j = Mint {
            kind: "event".into(),
            r#type: JOURNEY.into(),
            universe_id: w.scope.clone(),
            scope_path: w.scope.clone(),
            payload: json!({"ref": ask_id, "hash": "sha256:-", "note": note}),
            correlation_id: Some(ask_id.to_string()),
            authority_chain: Some(chain.to_vec()),
            aggregate: None,
            marker: None,
        }
        .mint()?;
        let raw = envelope::encode(&j)?;
        outbox::commit_with_outbox(g, &raw, j["message_id"].as_str().unwrap_or_default(), None, async move |tx| {
            tx.execute(
                "UPDATE spine_asks SET status = $2, reply = $3, served_by = coalesce($4, served_by), replied_at = \
                 clock_timestamp() WHERE ask_id = $1",
                &[&a, &st, &rp, &sb],
            )
            .await?;
            let seq = asks::next_seq(tx, &a).await.map_err(|e| RailError::Refused(e.to_string()))?;
            let r = Mint {
                kind: "event".into(),
                r#type: REPLY.into(),
                universe_id: w.scope.clone(),
                scope_path: w.scope.clone(),
                payload: json!({"ref": a, "hash": crate::content_hash(&Value::String(rp.clone())), "proof": "L1"}),
                correlation_id: Some(a.clone()),
                authority_chain: Some(ch),
                aggregate: Some(json!({"type": "ask", "id": a, "sequence": seq})),
                marker: None,
            }
            .mint()
            .map_err(|e| RailError::Refused(e.to_string()))?;
            outbox::add_row(tx, &envelope::encode(&r).map_err(|e| RailError::Refused(e.to_string()))?,
                            r["message_id"].as_str().unwrap_or_default())
                .await?;
            Ok(())
        })
        .await?;
        Ok(())
    }

    /// The human's stop on a routed ask (rule 11): rested here at once, and
    /// the stop carried to the home cell first of anything else waiting.
    pub async fn stop_ask(
        &self,
        g: &mut Ground,
        ask_id: &str,
        person: &str,
    ) -> Result<Value, RoadError> {
        let row = g
            .client()
            .query_opt(
                "SELECT status, home_cell, remote_id, target FROM spine_asks WHERE ask_id = $1 AND scope = $2 AND \
                 seam_side = 'origin'",
                &[&ask_id, &self.world.scope],
            )
            .await?;
        let Some(row) = row else {
            return Err(refused("no such routed ask"));
        };
        let (status, cell, remote, target): (
            String,
            Option<String>,
            Option<String>,
            Option<String>,
        ) = (row.get(0), row.get(1), row.get(2), row.get(3));
        if status != "routed" && status != "parked" {
            return Ok(
                json!({"ask_id": ask_id, "status": status, "words": "it had already come to rest"}),
            );
        }
        let cell = cell.unwrap_or_default();
        // not yet carried: the message rests before it ever goes
        g.client()
            .execute(
                "UPDATE spine_seam_out SET sent_at = clock_timestamp(), last_error = 'stopped before it went' WHERE ref = $1 \
                 AND kind = 'ask' AND sent_at IS NULL",
                &[&ask_id],
            )
            .await?;
        let words = format!(
            "Stopped on your word — the ask to {} was set to rest here{}.",
            target.as_deref().unwrap_or("the peer"),
            if remote.is_some() {
                format!(" and cell {cell} was told to rest it too")
            } else {
                String::new()
            }
        );
        self.settle(
            g,
            ask_id,
            "cancelled",
            &words,
            Some(KERNEL),
            &[person.to_string(), KERNEL.to_string()],
            &format!("{KERNEL}: stopped by {person} — rule 11, the human can always stop"),
        )
        .await?;
        if let Some(rid) = remote {
            self.enqueue(
                g,
                &cell,
                "stop",
                &json!({"ask_id": rid, "by": person}),
                Some(ask_id),
            )
            .await?;
        }
        Ok(json!({"ask_id": ask_id, "status": "cancelled", "words": words}))
    }

    // ---- the home side -------------------------------------------------------------------

    /// Answers to asks that came over the seam go back over it — once.
    async fn carry_replies(&self, g: &Ground) -> Result<(), RoadError> {
        let rows = g
            .client()
            .query(
                "SELECT ask_id, home_cell, remote_id, status, reply, served_by FROM spine_asks WHERE scope = $1 AND \
                 seam_side = 'home' AND NOT seam_sent AND status IN ('replied', 'refused', 'cancelled') AND reply IS NOT NULL",
                &[&self.world.scope],
            )
            .await?;
        for r in rows {
            let (ask_id, cell, remote, status, reply, served_by): (
                String,
                String,
                String,
                String,
                String,
                Option<String>,
            ) = (r.get(0), r.get(1), r.get(2), r.get(3), r.get(4), r.get(5));
            let name = match &served_by {
                Some(did) => asks::name_of(g, &self.world.scope, Some(did))
                    .await?
                    .unwrap_or_else(|| did.clone()),
                None => "the kernel".to_string(),
            };
            let body = json!({"ask_id": remote, "home_ask_id": ask_id, "status": status, "reply": reply,
                              "served_by": name, "at": envelope::now_iso()});
            self.enqueue(g, &cell, "reply", &body, Some(&ask_id))
                .await?;
            g.client()
                .execute(
                    "UPDATE spine_asks SET seam_sent = true WHERE ask_id = $1",
                    &[&ask_id],
                )
                .await?;
        }
        Ok(())
    }

    /// An ask from a peer, filed as the person's ask in THIS world and served
    /// by this cell's own address rule — a name not here is refused at the door
    /// in words, and the words go back.
    async fn land_ask(&self, g: &mut Ground, from: &str, body: &Value) -> Result<Value, RoadError> {
        let text = body["text"].as_str().unwrap_or_default().trim().to_string();
        if text.is_empty() {
            return Err(refused("an empty ask asks nothing"));
        }
        let person = body["person"]
            .as_str()
            .unwrap_or("did:orreth:person:unknown")
            .to_string();
        let origin_id = body["ask_id"].as_str().unwrap_or_default().to_string();
        // once: the same origin ask lands once, whatever the road did
        if let Some(r) = g
            .client()
            .query_opt(
                "SELECT ask_id FROM spine_asks WHERE remote_id = $1 AND home_cell = $2 AND seam_side = 'home'",
                &[&origin_id, &from],
            )
            .await?
        {
            return Ok(json!({"ask_id": r.get::<_, String>(0), "again": true}));
        }
        let names = asks::names_here(g, &self.world.scope).await?;
        let head = text
            .split([',', ':'])
            .next()
            .unwrap_or_default()
            .trim()
            .trim_start_matches('@')
            .to_string();
        let to = match crate::ask::address(&text, &names) {
            Some(who) => Some(vec![who]),
            None if !head.is_empty() && !head.contains(' ') => Some(vec![head]), // named, not here → refused in words
            None => None,
        };
        let submitted = asks::submit_ask(
            g,
            &self.world,
            Submit {
                text: text.clone(),
                person: person.clone(),
                to,
                window: None,
                session: None,
                parent_marker: None,
                kind: None,
                zone: None,
            },
        )
        .await?;
        let ask_id = match submitted {
            asks::Submitted::One(id) => id,
            asks::Submitted::Many(mut ids) => ids.remove(0),
        };
        let carried: Option<String> = body
            .get("profile")
            .filter(|p| p.is_object())
            .map(|p| p.to_string()); // P7 sp8: what rode with the ask — read for this answer only
        g.client()
            .execute(
                "UPDATE spine_asks SET home_cell = $2, remote_id = $3, seam_side = 'home', carried_profile = $4 WHERE ask_id = $1",
                &[&ask_id, &from, &origin_id, &carried],
            )
            .await?;
        self.journey(g, &ask_id, &format!("{KERNEL}: came over the seam from cell {from} (its ask {origin_id}), asked by {person}"))
            .await?;
        Ok(json!({"ask_id": ask_id}))
    }

    /// The answer to an ask this cell routed away lands on the ask the human asked.
    async fn land_reply(
        &self,
        g: &mut Ground,
        from: &str,
        signer: &str,
        body: &Value,
    ) -> Result<Value, RoadError> {
        let ask_id = body["ask_id"].as_str().unwrap_or_default().to_string();
        let row = g
            .client()
            .query_opt(
                "SELECT status FROM spine_asks WHERE ask_id = $1 AND scope = $2 AND seam_side = 'origin' AND \
                 home_cell = $3",
                &[&ask_id, &self.world.scope, &from],
            )
            .await?;
        let Some(row) = row else {
            return Err(refused("no such routed ask"));
        };
        let status: String = row.get(0);
        if status != "routed" && status != "parked" {
            // once, and never over a stop: an answer after the rest is set aside, said
            self.journey(g, &ask_id, &format!("{KERNEL}: an answer came from cell {from} after the ask was at rest — set aside"))
                .await?;
            return Ok(json!({"ask_id": ask_id, "set_aside": true}));
        }
        let reply = body["reply"].as_str().unwrap_or_default().to_string();
        let served = body["served_by"].as_str().unwrap_or("the kernel");
        let by = format!("{served}@{from}");
        let st = match body["status"].as_str() {
            Some("refused") => "refused",
            Some("cancelled") => "cancelled",
            _ => "replied",
        };
        self.settle(g, &ask_id, st, &reply, Some(&by), &[signer.to_string(), format!("cell {from}")],
                    &format!("{KERNEL}: answered in cell {from} by {served} — carried back over the seam, signed by its kernel"))
            .await?;
        Ok(json!({"ask_id": ask_id, "status": st}))
    }

    /// A stop from the ask's origin: rested here at the next safe boundary (now).
    async fn land_stop(
        &self,
        g: &mut Ground,
        from: &str,
        body: &Value,
    ) -> Result<Value, RoadError> {
        let ask_id = body["ask_id"].as_str().unwrap_or_default().to_string();
        let by = body["by"].as_str().unwrap_or("its origin").to_string();
        let row = g
            .client()
            .query_opt(
                "SELECT status FROM spine_asks WHERE ask_id = $1 AND scope = $2 AND seam_side = 'home' AND home_cell = $3",
                &[&ask_id, &self.world.scope, &from],
            )
            .await?;
        let Some(row) = row else {
            return Err(refused("no such ask from that cell"));
        };
        let status: String = row.get(0);
        if status == "replied" || status == "refused" || status == "cancelled" {
            return Ok(
                json!({"ask_id": ask_id, "status": status, "words": "it had already come to rest"}),
            );
        }
        let words = format!("Stopped from cell {from} on {by}'s word — set to rest here; an answer still forming is set aside.");
        self.settle(
            g,
            &ask_id,
            "cancelled",
            &words,
            Some(KERNEL),
            &[by.clone(), KERNEL.to_string()],
            &format!("{KERNEL}: stopped over the seam by {by} of cell {from} — rule 11"),
        )
        .await?;
        // a reply must not go back for a stopped ask
        g.client()
            .execute(
                "UPDATE spine_asks SET seam_sent = true WHERE ask_id = $1",
                &[&ask_id],
            )
            .await?;
        Ok(json!({"ask_id": ask_id, "status": "cancelled"}))
    }

    // ---- the door ------------------------------------------------------------------------

    /// `POST /seam`: the fences in order — the ceiling, the pin, the signature,
    /// the nonce, the window, the epoch — then the kind. The answer is my own
    /// signed message (a hello answers a hello; every other kind is
    /// acknowledged with what it made). A refusal at the fences wears the one
    /// face (403); an epoch fence, past the signature, says so (409) so the
    /// sender re-hears the world.
    pub async fn receive(&self, g: &mut Ground, signed: &Value) -> Result<(u16, Value), RoadError> {
        let one_face = || Ok((403u16, crate::proof::one_face()));
        let from = signed["from"].as_str().unwrap_or_default().to_string();
        let signer = signed["signer"].as_str().unwrap_or_default().to_string();
        if from.is_empty() || signer.is_empty() || !self.knock(&signer) {
            return one_face();
        }
        if self.named(&from).is_none() {
            return one_face(); // a cell this one never named: nothing to learn here
        }
        let Some(row) = self.peer_row(g, &from).await? else {
            return one_face();
        };
        let pinned = row.did.clone().or_else(|| Some(signer.clone())); // first sight pins
        let nonce = signed["nonce"].as_str().unwrap_or_default().to_string();
        let seen: Vec<String> = if self.nonce_seen(g, &nonce).await? {
            vec![nonce.clone()]
        } else {
            vec![]
        };
        let kind = signed["kind"].as_str().unwrap_or_default().to_string();
        let epoch_fence = if kind == "hello" { None } else { row.epoch };
        let verdict = cells::seam_verify(
            signed,
            pinned.as_deref(),
            &envelope::now_iso(),
            &seen,
            epoch_fence,
        );
        if verdict.ends_with("epoch") {
            return Ok((409, json!({"error": verdict, "epoch": row.epoch})));
        }
        if verdict != "ok" || signed["to"].as_str() != Some(&self.cell) {
            return one_face();
        }
        if kind == "hello" {
            if let Some(mine) = row.epoch {
                if signed["epoch"].as_i64().unwrap_or(0) < mine {
                    return Ok((409, json!({"error": "stale epoch", "epoch": mine})));
                }
            }
        }
        if kind == "ask" {
            if let Some(words) = crate::cells_live::fence(g, &self.world.scope, &self.cell).await? {
                return Err(RoadError::Forbidden(words));
            }
        }
        self.spend_nonce(g, &nonce).await?;
        self.learn(g, &from, signed).await?;
        let body = &signed["body"];
        let made = match kind.as_str() {
            "hello" => self.hello_body(g).await?,
            "ask" => self.land_ask(g, &from, body).await?,
            "reply" => self.land_reply(g, &from, &signer, body).await?,
            "stop" => self.land_stop(g, &from, body).await?,
            other => {
                return Err(refused(format!(
                    "the seam carries hello, ask, reply and stop — not '{other}'"
                )))
            }
        };
        let answer_kind = if kind == "hello" { "hello" } else { "ack" };
        let answer = self.sign(g, &from, answer_kind, made).await?;
        Ok((200, answer))
    }

    // ---- the beat ------------------------------------------------------------------------

    /// One beat: greet the peers due, carry what waits, carry the answers home, sweep old nonces.
    pub async fn beat(&self, g: &mut Ground) -> Result<(), RoadError> {
        self.ensure_peers(g).await?;
        for p in &self.peers {
            let Some(row) = self.peer_row(g, &p.cell).await? else {
                continue;
            };
            if row.did.is_none()
                || row.unreachable
                || row.since_heard_s.unwrap_or(f64::MAX) >= HELLO_EVERY_S
            {
                let _ = self.hello(g, &p.cell).await?;
            }
        }
        self.carry_replies(g).await?;
        self.drain(g).await?;
        g.client()
            .execute(
                "DELETE FROM spine_seam_nonces WHERE seen_at < clock_timestamp() - make_interval(secs => $1::float8)",
                &[&(2.0 * cells::SEAM_WINDOW_S as f64)],
            )
            .await?;
        Ok(())
    }

    /// The seam's standing task: a beat every two seconds, or at once when woken;
    /// a rail's refusal stands the beat again on a fresh connection.
    pub async fn run(&self, stop: &std::sync::atomic::AtomicBool) {
        use std::sync::atomic::Ordering;
        while !stop.load(Ordering::Relaxed) {
            match Ground::connect(&self.world.pg_dsn).await {
                Ok(mut g) => {
                    while !stop.load(Ordering::Relaxed) {
                        if let Err(e) = self.beat(&mut g).await {
                            eprintln!("the seam's beat stumbled: {e}");
                            if matches!(e, RoadError::Rail(_)) {
                                break;
                            }
                        }
                        let _ = tokio::time::timeout(Duration::from_secs(2), self.wake.notified())
                            .await;
                    }
                }
                Err(e) => eprintln!("the seam could not reach the ground: {e}"),
            }
            if !stop.load(Ordering::Relaxed) {
                tokio::time::sleep(Duration::from_millis(500)).await;
            }
        }
    }
}

struct PeerRow {
    cell: String,
    door: String,
    did: Option<String>,
    epoch: Option<i64>,
    unreachable: bool,
    since_heard_s: Option<f64>,
}
