// PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp8 row 3, THE GATE (a): the human seat on the ground · 2026-09-26
//! The seat's LIVE half — mirrors the ground half of `orreth_spine.seat`
//! (canon 0005 sp8 row 3): the OWNER (the ceremony: the first person to prove
//! an authenticator on a ground no one holds — one fact, one row, a master
//! from that moment), the seats (a token minted by this kernel's own self as
//! the root, its row and its fact in one transaction; left early on the
//! person's word — recorded, never deleted), who sits (the token verified
//! offline, then its row), who may enroll whom, and the knock ceiling at every
//! door (per person, per address at an open door). The tables are the Python
//! spine's, word for word.

use crate::envelope::{self, Mint};
use crate::ground::Ground;
use crate::hash::content_hash;
use crate::kernel_self::KernelSelf;
use crate::outbox;
use crate::proof::DRIFT;
use crate::proof_live;
use crate::seat::{self, CEREMONY};
use crate::world::{RoadError, World};
use serde_json::{json, Value};
use std::collections::HashMap;
use std::sync::Mutex;
use std::time::{SystemTime, UNIX_EPOCH};

/// `seat.ensure_schema`: the owner, the seats.
pub const SEAT_DDL: &[&str] = &[
    "CREATE TABLE IF NOT EXISTS spine_owner ( scope text PRIMARY KEY, person text NOT NULL, \
     declared_at timestamptz NOT NULL DEFAULT now())",
    "CREATE TABLE IF NOT EXISTS spine_seats ( seat_id text PRIMARY KEY, person text NOT NULL, scope \
     text NOT NULL, role text NOT NULL, expiry timestamptz NOT NULL, taken_at timestamptz NOT NULL \
     DEFAULT now(), left_at timestamptz, left_by text)",
];

/// `SPINE_SEAT_HOURS` (24).
pub fn hours() -> f64 {
    std::env::var("SPINE_SEAT_HOURS")
        .ok()
        .and_then(|h| h.parse().ok())
        .filter(|h: &f64| *h > 0.0)
        .unwrap_or(seat::HOURS_DEFAULT)
}

fn dial_f(name: &str, default: f64) -> f64 {
    std::env::var(name)
        .ok()
        .and_then(|v| v.parse().ok())
        .unwrap_or(default)
}

fn now_f() -> f64 {
    SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap_or_default()
        .as_secs_f64()
}

fn event(
    w: &World,
    typ: &str,
    r#ref: &str,
    extra: Value,
    chain: Vec<String>,
) -> Result<Value, RoadError> {
    let mut payload = json!({"ref": r#ref, "hash": "sha256:-"});
    if let Some(o) = extra.as_object() {
        for (k, v) in o {
            payload[k] = v.clone();
        }
    }
    Ok(Mint {
        kind: "event".into(),
        r#type: typ.into(),
        universe_id: w.scope.clone(),
        scope_path: w.scope.clone(),
        payload,
        correlation_id: Some(r#ref.to_string()),
        authority_chain: Some(chain),
        ..Default::default()
    }
    .mint()?)
}

pub async fn owner(g: &Ground, scope: &str) -> Result<Option<String>, RoadError> {
    let row = g
        .client()
        .query_opt("SELECT person FROM spine_owner WHERE scope = $1", &[&scope])
        .await?;
    Ok(row.map(|r| r.get(0)))
}

/// THE CEREMONY: the first person to prove an authenticator on a ground no one
/// holds becomes its owner — one fact, one row, and a master from that moment.
pub async fn declare_owner(g: &mut Ground, w: &World, person: &str) -> Result<bool, RoadError> {
    if owner(g, &w.scope).await?.is_some() {
        return Ok(false);
    }
    let e = event(
        w,
        seat::OWNER_DECLARED,
        person,
        json!({"person": person, "by": CEREMONY}),
        vec![person.to_string(), crate::cells::KERNEL.to_string()],
    )?;
    let raw = envelope::encode(&e)?;
    let mid = e["message_id"].as_str().unwrap_or_default().to_string();
    let (p, sc) = (person.to_string(), w.scope.clone());
    outbox::commit_with_outbox(g, &raw, &mid, None, async move |tx| {
        tx.execute(
            "INSERT INTO spine_owner (scope, person) VALUES ($1, $2) ON CONFLICT DO NOTHING",
            &[&sc, &p],
        )
        .await?;
        Ok(())
    })
    .await?;
    proof_live::declare_master(g, w, person, CEREMONY).await?;
    Ok(true)
}

pub async fn role_of(g: &Ground, scope: &str, person: &str) -> Result<String, RoadError> {
    if owner(g, scope).await?.as_deref() == Some(person) {
        return Ok("owner".into());
    }
    Ok(if proof_live::is_master(g, scope, person).await? {
        "master".into()
    } else {
        "person".into()
    })
}

/// The seat door: the person's code from their enrolled authenticator, or the
/// one face; on a ground no one holds, this proof is the ceremony.
pub async fn take(
    g: &mut Ground,
    w: &World,
    signer: &KernelSelf,
    person: &str,
    code: Option<&str>,
    hours_: Option<f64>,
) -> Result<Value, RoadError> {
    let Some(secret) = proof_live::active_secret(g, &w.scope, person).await? else {
        return Err(RoadError::NotConfirmed { rest: false });
    };
    if !crate::proof::verify(&secret, code, proof_live::now_unix(), DRIFT) {
        return Err(RoadError::NotConfirmed { rest: false });
    }
    let ceremony = declare_owner(g, w, person).await?;
    let role = role_of(g, &w.scope, person).await?;
    let h = hours_.unwrap_or_else(hours);
    let now_ms = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .map(|d| d.as_millis() as u64)
        .unwrap_or(0);
    let expiry = envelope::iso_millis(now_ms + (h * 3_600_000.0) as u64);
    let token = seat::mint(
        signer,
        person,
        &w.scope,
        &seat::grants_for(&role, &w.scope),
        &expiry,
        "within",
        None,
        None,
    )
    .map_err(RoadError::Refused)?;
    let sid = seat::seat_id(&token);
    let e = event(
        w,
        seat::SEAT_TAKEN,
        &sid,
        json!({"hash": content_hash(&token), "person": person, "role": role, "expiry": expiry, "ceremony": ceremony}),
        vec![person.to_string(), crate::cells::KERNEL.to_string()],
    )?;
    let raw = envelope::encode(&e)?;
    let mid = e["message_id"].as_str().unwrap_or_default().to_string();
    let (s2, p2, sc2, r2, x2) = (
        sid.clone(),
        person.to_string(),
        w.scope.clone(),
        role.clone(),
        expiry.clone(),
    );
    outbox::commit_with_outbox(g, &raw, &mid, None, async move |tx| {
        tx.execute(
            "INSERT INTO spine_seats (seat_id, person, scope, role, expiry) VALUES ($1, $2, $3, $4, \
             CAST($5::text AS timestamptz))",
            &[&s2, &p2, &sc2, &r2, &x2],
        )
        .await?;
        Ok(())
    })
    .await?;
    Ok(
        json!({"seat": token, "wire": seat::wire(&token), "seat_id": sid, "person": person, "role": role,
              "expiry": expiry, "owner": ceremony, "words": seat::taken_words(person, &role, h, ceremony)}),
    )
}

/// Who sits here: `{person, seat_id, role, grants, govern, expiry}` — the token
/// verified offline against this kernel's root, then its row on the ground.
#[derive(Clone, Debug)]
pub struct Seated {
    pub person: String,
    pub seat_id: String,
    pub role: String,
    pub grants: Value,
    pub govern: bool,
    pub expiry: String,
}

/// The seat's offline half: the token from the wire, verified against this kernel's
/// root — no ground touched (the ceiling is spent on this before the ground is asked,
/// so a flood never reaches it). The role is the ground's to say (`on_ground`).
pub fn offline(signer: &KernelSelf, wire: &str) -> Option<Seated> {
    let tok = seat::unwire(wire)?;
    if seat::verify(
        &tok,
        &signer.did(),
        &signer.verify_key_hex(),
        &envelope::now_iso(),
    ) != "ok"
    {
        return None;
    }
    let grants = tok["grants"].clone();
    let govern = grants
        .as_array()
        .is_some_and(|a| a.iter().any(|g| g["action"] == json!("govern")));
    Some(Seated {
        person: tok["subject"].as_str().unwrap_or_default().to_string(),
        seat_id: seat::seat_id(&tok),
        role: String::new(),
        grants,
        govern,
        expiry: tok["constraints"]["expiry"]
            .as_str()
            .unwrap_or_default()
            .to_string(),
    })
}

/// The seat's row: its role, and that it was not left.
pub async fn on_ground(g: &Ground, w: &World, off: Seated) -> Result<Option<Seated>, RoadError> {
    let row = g
        .client()
        .query_opt(
            "SELECT role FROM spine_seats WHERE seat_id = $1 AND scope = $2 AND left_at IS NULL",
            &[&off.seat_id, &w.scope],
        )
        .await?;
    Ok(row.map(|r| Seated {
        role: r.get(0),
        ..off
    }))
}

/// Who sits here: the offline half, then the ground.
pub async fn read(
    g: &Ground,
    w: &World,
    signer: &KernelSelf,
    wire: &str,
) -> Result<Option<Seated>, RoadError> {
    match offline(signer, wire) {
        Some(off) => on_ground(g, w, off).await,
        None => Ok(None),
    }
}

/// How long the gate remembers a seat it checked on the ground.
pub const SEEN_S: f64 = 5.0;

/// The person ends their own seat early — recorded, never deleted.
pub async fn leave(
    g: &mut Ground,
    w: &World,
    seat_id: &str,
    person: &str,
) -> Result<Value, RoadError> {
    let e = event(
        w,
        seat::SEAT_LEFT,
        seat_id,
        json!({"person": person}),
        vec![person.to_string(), crate::cells::KERNEL.to_string()],
    )?;
    let raw = envelope::encode(&e)?;
    let mid = e["message_id"].as_str().unwrap_or_default().to_string();
    let (s2, p2) = (seat_id.to_string(), person.to_string());
    outbox::commit_with_outbox(g, &raw, &mid, None, async move |tx| {
        tx.execute(
            "UPDATE spine_seats SET left_at = now(), left_by = $1 WHERE seat_id = $2 AND person = $1 \
             AND left_at IS NULL",
            &[&p2, &s2],
        )
        .await?;
        Ok(())
    })
    .await?;
    Ok(json!({"left": seat_id, "person": person,
              "words": "your seat is ended — prove your authenticator to sit again"}))
}

/// Who may enroll an authenticator for `target`: anyone while the ground has no
/// owner (the ceremony); afterwards the person themselves or a seat that governs.
pub async fn may_enroll(
    g: &Ground,
    scope: &str,
    actor: Option<&Seated>,
    target: &str,
) -> Result<bool, RoadError> {
    if owner(g, scope).await?.is_none() {
        return Ok(true);
    }
    Ok(match actor {
        None => false,
        Some(a) => a.person == target || a.govern,
    })
}

/// The knock ceiling at every door (0071, generalized from the seam).
pub struct Ceilings {
    pub rate: f64,
    pub burst: f64,
    buckets: Mutex<HashMap<String, (f64, f64)>>,
    /// The gate's memory: seat_id → (the seat as the ground answered, when) — asked once per `SEEN_S`.
    seen: Mutex<HashMap<String, (Seated, f64)>>,
}

impl Default for Ceilings {
    fn default() -> Self {
        Self::new()
    }
}

impl Ceilings {
    pub fn new() -> Ceilings {
        Ceilings {
            rate: dial_f("SPINE_CEILING_RATE", seat::CEILING_RATE_DEFAULT),
            burst: dial_f("SPINE_CEILING_BURST", seat::CEILING_BURST_DEFAULT),
            buckets: Mutex::new(HashMap::new()),
            seen: Mutex::new(HashMap::new()),
        }
    }

    /// The seat as the ground answered within the last `SEEN_S` seconds, or None.
    pub fn remembered(&self, seat_id: &str) -> Option<Seated> {
        let now = now_f();
        let m = self.seen.lock().unwrap_or_else(|p| p.into_inner());
        m.get(seat_id)
            .filter(|(_, t)| *t > now - SEEN_S)
            .map(|(s, _)| s.clone())
    }

    pub fn remember(&self, who: &Seated) {
        let now = now_f();
        let mut m = self.seen.lock().unwrap_or_else(|p| p.into_inner());
        m.insert(who.seat_id.clone(), (who.clone(), now));
        if m.len() > 10_000 {
            m.retain(|_, (_, t)| *t >= now - SEEN_S);
        }
    }

    /// This kernel forgets a seat at once (a leave); another over the same ground within `SEEN_S`.
    pub fn forget(&self, seat_id: &str) {
        let mut m = self.seen.lock().unwrap_or_else(|p| p.into_inner());
        m.remove(seat_id);
    }

    pub fn knock(&self, who: &str) -> bool {
        let now = now_f();
        let mut m = self.buckets.lock().unwrap_or_else(|p| p.into_inner());
        let (tokens, last) = m.get(who).copied().unwrap_or((self.burst, now));
        let (ok, after) = crate::cells::ceiling(tokens, last, now, self.rate, self.burst);
        m.insert(who.to_string(), (after, now));
        if m.len() > 10_000 {
            m.retain(|_, (_, t)| *t >= now - 600.0);
        }
        ok
    }
}
