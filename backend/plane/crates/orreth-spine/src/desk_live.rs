// PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp8 row 3, THE GATE (b): the machine join desk on the ground · 2026-09-26
//! THE MACHINE JOIN DESK on the ground (canon 0005 sp8 row 3b · 0006 · 0012 ·
//! covenant rule 3) — the doors' half of `desk`. A body ASKS and is CHALLENGED in
//! one motion (the desk's own nonce); it PROVES with the key behind its DID; a
//! proven key is admitted at once on one of two standing words — the CREW
//! MANIFEST (a one-time spawn ticket this kernel handed the body, and the
//! template it spawned) or the STANDING WELCOME (the same self admitted here
//! before) — else STAGED: the kernel holds `join.admit` at the interlock as its
//! own act, and only a governing seat's click settles it (a hold nobody answers
//! is denied when the holds expire). The body then COLLECTS its lease with the
//! same key; the lease stands as a SEAT with the role `body` — one gate law for
//! people and bodies. Facts: `orreth.join.asked.v1` · `.proved.v1` ·
//! `.admitted.v1` · `.denied.v1`, and the lease's `orreth.seat.taken.v1`.

use crate::desk;
use crate::envelope::{self, Mint};
use crate::ground::Ground;
use crate::hash::content_hash;
use crate::kernel_self::KernelSelf;
use crate::outbox;
use crate::rail_error::RailError;
use crate::seat;
use crate::world::{isoformat, token_hex, RoadError, World};
use serde_json::{json, Value};
use std::time::{SystemTime, UNIX_EPOCH};
use tokio_postgres::{GenericClient, Transaction};

pub const KERNEL: &str = "the kernel";

/// `spine_desk`: every join this world was asked for, by status.
pub const DESK_DDL: &[&str] = &[
    "CREATE TABLE IF NOT EXISTS spine_desk ( join_id text PRIMARY KEY, scope text NOT NULL, did text NOT NULL, \
     name text NOT NULL, kind text NOT NULL, public_key text NOT NULL, template_hash text NOT NULL DEFAULT '', \
     policy_hash text NOT NULL DEFAULT '', status text NOT NULL, nonce text NOT NULL, nonce_at timestamptz NOT \
     NULL DEFAULT now(), ticket text, ask_id text, admitted_by text, lease_id text, lease text, expiry \
     timestamptz, asked_at timestamptz NOT NULL DEFAULT now(), updated_at timestamptz NOT NULL DEFAULT now())",
    "CREATE INDEX IF NOT EXISTS spine_desk_did ON spine_desk (scope, did)",
];

fn fact(
    w: &World,
    typ: &str,
    join_id: &str,
    extra: Value,
    chain: Vec<String>,
) -> Result<Value, RoadError> {
    let mut payload = json!({"ref": join_id, "hash": "sha256:-"});
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
        correlation_id: Some(join_id.to_string()),
        authority_chain: Some(chain),
        ..Default::default()
    }
    .mint()?)
}

/// One join's row, as the desk reads it.
#[derive(Debug, Clone)]
pub struct Row {
    pub join_id: String,
    pub did: String,
    pub name: String,
    pub kind: String,
    pub public_key: String,
    pub template_hash: String,
    pub status: String,
    pub nonce: String,
    pub nonce_at: SystemTime,
    pub ticket: Option<String>,
    pub ask_id: Option<String>,
    pub admitted_by: Option<String>,
    pub lease_id: Option<String>,
    pub lease: Option<String>,
    pub expiry: Option<SystemTime>,
    pub asked_at: SystemTime,
    pub updated_at: SystemTime,
}

const COLS: &str = "join_id, did, name, kind, public_key, template_hash, status, nonce, nonce_at, ticket, ask_id, \
                    admitted_by, lease_id, lease, expiry, asked_at, updated_at";

fn row_of(r: &tokio_postgres::Row) -> Row {
    Row {
        join_id: r.get(0),
        did: r.get(1),
        name: r.get(2),
        kind: r.get(3),
        public_key: r.get(4),
        template_hash: r.get(5),
        status: r.get(6),
        nonce: r.get(7),
        nonce_at: r.get(8),
        ticket: r.get(9),
        ask_id: r.get(10),
        admitted_by: r.get(11),
        lease_id: r.get(12),
        lease: r.get(13),
        expiry: r.get(14),
        asked_at: r.get(15),
        updated_at: r.get(16),
    }
}

async fn get<C: GenericClient>(
    c: &C,
    scope: &str,
    join_id: &str,
) -> Result<Option<Row>, RoadError> {
    Ok(c.query_opt(
        &format!("SELECT {COLS} FROM spine_desk WHERE join_id = $1 AND scope = $2"),
        &[&join_id, &scope],
    )
    .await?
    .map(|r| row_of(&r)))
}

/// The join as the door says it: its status and the words for it; the nonce while it
/// is challenged, the held ask while staged, the admitting word once done — never the
/// lease (that is collected by the key).
pub fn view(r: &Row, scope: &str) -> Value {
    let mut v = json!({
        "id": r.join_id, "status": r.status, "name": r.name, "did": r.did, "kind": r.kind,
        "template_hash": r.template_hash,
        "words": desk::words(&r.status, &r.name, scope, r.admitted_by.as_deref()),
        "asked_at": isoformat(r.asked_at), "updated_at": isoformat(r.updated_at),
    });
    if r.status == "challenged" {
        v["nonce"] = json!(r.nonce);
    }
    if let Some(a) = &r.ask_id {
        v["ask"] = json!(a);
    }
    if let Some(b) = &r.admitted_by {
        v["admitted_by"] = json!(b);
    }
    if let Some(e) = r.expiry {
        v["expiry"] = json!(isoformat(e));
    }
    v
}

/// `POST /join` — a body asks, and is challenged in the same breath (201).
pub async fn ask(g: &mut Ground, w: &World, p: &Value) -> Result<Value, RoadError> {
    let s = |k: &str| p[k].as_str().unwrap_or_default().trim().to_string();
    let (did, name, public_key) = (s("did"), s("name"), s("public_key"));
    let kind = seat::kind_of(&did).to_string(); // what the DID says it is (a body: `agent`)
    let role = {
        let r = s("role");
        if r.is_empty() {
            "body".to_string()
        } else {
            r
        }
    }; // the body's own word: resident · firmware
    let (template_hash, policy_hash) = (s("template_hash"), s("policy_hash"));
    let ticket = p["ticket"]
        .as_str()
        .map(str::trim)
        .filter(|t| !t.is_empty())
        .map(str::to_string);
    if !desk::KINDS.contains(&kind.as_str())
        || !desk::name_ok(&name)
        || !desk::name_ok(&role)
        || seat::did_of_key(&kind, &public_key).as_deref() != Some(did.as_str())
    {
        return Err(RoadError::Refused(desk::REFUSED_WORDS.into()));
    }
    let nonce = token_hex(16);
    let join_id = desk::join_id_of(&did, &nonce);
    let e = fact(
        w,
        desk::JOIN_ASKED,
        &join_id,
        json!({"did": did, "name": name, "kind": role, "template": template_hash, "status": "challenged"}),
        vec![did.clone()],
    )?;
    let raw = envelope::encode(&e)?;
    let mid = e["message_id"].as_str().unwrap_or_default().to_string();
    let (j2, sc2, d2, n2, k2, pk2, t2, p2, no2, tk2) = (
        join_id.clone(),
        w.scope.clone(),
        did.clone(),
        name.clone(),
        role.clone(),
        public_key.clone(),
        template_hash.clone(),
        policy_hash.clone(),
        nonce.clone(),
        ticket.clone(),
    );
    outbox::commit_with_outbox(g, &raw, &mid, None, async move |tx| {
        tx.execute(
            "INSERT INTO spine_desk (join_id, scope, did, name, kind, public_key, template_hash, policy_hash, \
             status, nonce, ticket) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, 'challenged', $9, $10)",
            &[&j2, &sc2, &d2, &n2, &k2, &pk2, &t2, &p2, &no2, &tk2],
        )
        .await?;
        Ok(())
    })
    .await?;
    Ok(
        json!({"id": join_id, "status": "challenged", "nonce": nonce,
              "words": desk::words("challenged", &name, &w.scope, None)}),
    )
}

/// `GET /join/<id>` — the join's status, or none.
pub async fn status(g: &Ground, w: &World, join_id: &str) -> Result<Option<Value>, RoadError> {
    Ok(get(g.client(), &w.scope, join_id)
        .await?
        .map(|r| view(&r, &w.scope)))
}

/// `GET /join` — the desk: every join asked of this world, newest first.
pub async fn list(g: &Ground, w: &World, limit: i64) -> Result<Vec<Value>, RoadError> {
    let rows = g
        .client()
        .query(
            &format!(
                "SELECT {COLS} FROM spine_desk WHERE scope = $1 ORDER BY asked_at DESC LIMIT $2"
            ),
            &[&w.scope, &limit],
        )
        .await?;
    Ok(rows.iter().map(|r| view(&row_of(r), &w.scope)).collect())
}

fn stale(nonce_at: SystemTime) -> bool {
    SystemTime::now()
        .duration_since(nonce_at)
        .map(|d| d.as_secs_f64() > desk::NONCE_S)
        .unwrap_or(false)
}

async fn set_status(
    g: &mut Ground,
    w: &World,
    join_id: &str,
    status: &str,
    admitted_by: Option<&str>,
    ask_id: Option<&str>,
    facts: Vec<Value>,
) -> Result<(), RoadError> {
    let tx = g.client_mut().transaction().await?;
    tx.execute(
        "UPDATE spine_desk SET status = $1, admitted_by = COALESCE($2, admitted_by), ask_id = COALESCE($3, \
         ask_id), updated_at = now() WHERE join_id = $4 AND scope = $5",
        &[&status, &admitted_by, &ask_id, &join_id, &w.scope],
    )
    .await?;
    for e in facts {
        outbox::add_row(
            &tx,
            &envelope::encode(&e)?,
            e["message_id"].as_str().unwrap_or_default(),
        )
        .await?;
    }
    tx.commit().await?;
    Ok(())
}

/// The kernel's own word for a body it spawned: the ticket it handed the body, spent
/// once, and the template it spawned — WHAT the body says it is, checked.
pub trait Manifest: Send + Sync {
    fn take_ticket(&self, name: &str, ticket: &str) -> bool;
    fn template_hash_of(&self, name: &str) -> Option<String>;
}

/// `POST /join/prove` — the body's signature over the desk's own nonce (200). A stale
/// nonce is re-challenged; a bad proof is denied with the one face; a good one is
/// admitted on a standing word or staged for a governing seat's click.
pub async fn prove(
    g: &mut Ground,
    w: &World,
    manifest: Option<&dyn Manifest>,
    join_id: &str,
    did: &str,
    sig: &Value,
) -> Result<Option<Value>, RoadError> {
    let Some(r) = get(g.client(), &w.scope, join_id).await? else {
        return Ok(None);
    };
    if r.status != "challenged" {
        return Ok(Some(view(&r, &w.scope))); // an idempotent knock: the desk's word as it stands
    }
    if stale(r.nonce_at) {
        let nonce = token_hex(16);
        g.client()
            .execute(
                "UPDATE spine_desk SET nonce = $1, nonce_at = now(), updated_at = now() WHERE join_id = $2",
                &[&nonce, &join_id],
            )
            .await?;
        return Ok(Some(
            json!({"id": join_id, "status": "challenged", "nonce": nonce,
                              "words": desk::words("challenged", &r.name, &w.scope, None)}),
        ));
    }
    if did != r.did || !desk::prove(did, &r.public_key, &r.nonce, sig) {
        let e = fact(
            w,
            desk::JOIN_DENIED,
            join_id,
            json!({"did": r.did, "name": r.name, "reason": "the proof did not verify"}),
            vec![r.did.clone(), KERNEL.into()],
        )?;
        set_status(g, w, join_id, "denied", None, None, vec![e]).await?;
        return Ok(Some(
            json!({"id": join_id, "status": "denied", "words": desk::REFUSED_WORDS}),
        ));
    }
    // the key is proven — whose word admits it?
    let by_ticket = match (&r.ticket, manifest) {
        (Some(t), Some(m)) => {
            m.template_hash_of(&r.name).as_deref() == Some(r.template_hash.as_str())
                && m.take_ticket(&r.name, t)
        }
        _ => false,
    };
    let welcome: Option<String> = if by_ticket {
        None
    } else {
        g.client()
            .query_opt(
                "SELECT join_id FROM spine_desk WHERE scope = $1 AND did = $2 AND status = 'done' AND join_id <> \
                 $3 ORDER BY updated_at DESC LIMIT 1",
                &[&w.scope, &r.did, &join_id],
            )
            .await?
            .map(|x| x.get(0))
    };
    let proved = fact(
        w,
        desk::JOIN_PROVED,
        join_id,
        json!({"did": r.did, "name": r.name, "kind": r.kind, "template": r.template_hash}),
        vec![r.did.clone(), KERNEL.into()],
    )?;
    if by_ticket || welcome.is_some() {
        let by = desk::admitted_by(by_ticket, welcome.as_deref(), None);
        let admitted = fact(
            w,
            desk::JOIN_ADMITTED,
            join_id,
            json!({"did": r.did, "name": r.name, "by": by}),
            vec![
                r.did.clone(),
                if by_ticket {
                    desk::BY_MANIFEST.into()
                } else {
                    "its standing welcome".into()
                },
                KERNEL.into(),
            ],
        )?;
        set_status(
            g,
            w,
            join_id,
            "done",
            Some(&by),
            None,
            vec![proved, admitted],
        )
        .await?;
        return Ok(Some(
            json!({"id": join_id, "status": "done", "admitted_by": by,
                              "words": desk::words("done", &r.name, &w.scope, Some(&by))}),
        ));
    }
    // staged: the kernel holds the human's yes as its own act; a body asked, the human cuts
    let ask_id = crate::proof_live::hold_kernel_act(
        g,
        w,
        &desk::hold_words(&r.name, &r.kind, &r.template_hash, desk::lease_days()),
        &r.did,
        desk::ADMIT_TOOL,
        json!({"join": join_id, "name": r.name, "did": r.did}),
        desk::ADMIT_LEVEL,
        None,
        desk::ADMIT_CLASS,
        false,
    )
    .await?;
    set_status(g, w, join_id, "staged", None, Some(&ask_id), vec![proved]).await?;
    Ok(Some(
        json!({"id": join_id, "status": "staged", "ask": ask_id,
                   "words": desk::words("staged", &r.name, &w.scope, None)}),
    ))
}

/// Does this person hold a governing seat here — the owner, or a declared master?
pub async fn governs<C: GenericClient>(
    c: &C,
    scope: &str,
    person: &str,
) -> Result<bool, RoadError> {
    let owner = c
        .query_opt(
            "SELECT 1 FROM spine_owner WHERE scope = $1 AND person = $2",
            &[&scope, &person],
        )
        .await?
        .is_some();
    if owner {
        return Ok(true);
    }
    Ok(c.query_opt(
        "SELECT 1 FROM spine_masters WHERE scope = $1 AND person = $2",
        &[&scope, &person],
    )
    .await?
    .is_some())
}

/// The settle of `join.admit` on a yes (inside the ask's own transaction): the join
/// goes `done` on a GOVERNING seat's word — a person's seat is refused with the one
/// face — and the admission is a fact. Returns the plain words.
pub async fn admit_in(
    tx: &Transaction<'_>,
    w: &World,
    join_id: &str,
    by: &str,
) -> Result<String, RoadError> {
    if !governs(tx, &w.scope, by).await? {
        return Err(RoadError::NotConfirmed { rest: false });
    }
    let Some(r) = get(tx, &w.scope, join_id).await? else {
        return Err(RoadError::NotConfirmed { rest: false });
    };
    if !desk::transition_legal(&r.status, "done") {
        return Err(RoadError::NotConfirmed { rest: false });
    }
    let by_words = desk::admitted_by(false, None, Some(by));
    let e = fact(
        w,
        desk::JOIN_ADMITTED,
        join_id,
        json!({"did": r.did, "name": r.name, "by": by_words, "person": by}),
        vec![r.did.clone(), by.to_string(), KERNEL.into()],
    )?;
    tx.execute(
        "UPDATE spine_desk SET status = 'done', admitted_by = $1, updated_at = now() WHERE join_id = $2",
        &[&by_words, &join_id],
    )
    .await?;
    outbox::add_row(
        tx,
        &envelope::encode(&e)?,
        e["message_id"].as_str().unwrap_or_default(),
    )
    .await?;
    Ok(desk::words("done", &r.name, &w.scope, Some(&by_words)))
}

/// The settle of `join.admit` on a no (a click, or no word within the holds' fifteen
/// minutes — 0012's "expire = deny + signal"): the join goes `denied`, recorded.
pub async fn deny_in(
    tx: &Transaction<'_>,
    w: &World,
    join_id: &str,
    why: &str,
) -> Result<(), RoadError> {
    let Some(r) = get(tx, &w.scope, join_id).await? else {
        return Ok(());
    };
    if !desk::transition_legal(&r.status, "denied") {
        return Ok(());
    }
    let e = fact(
        w,
        desk::JOIN_DENIED,
        join_id,
        json!({"did": r.did, "name": r.name, "reason": why}),
        vec![r.did.clone(), KERNEL.into()],
    )?;
    tx.execute(
        "UPDATE spine_desk SET status = 'denied', admitted_by = $1, updated_at = now() WHERE join_id = $2",
        &[&why, &join_id],
    )
    .await?;
    outbox::add_row(
        tx,
        &envelope::encode(&e)?,
        e["message_id"].as_str().unwrap_or_default(),
    )
    .await?;
    Ok(())
}

/// `POST /join/lease` — the admitted body collects its lease with the same key (200):
/// minted once by the kernel's own self with the fuel clause, standing on the ground as
/// a seat with the role `body`; the same knock again returns the same lease.
pub async fn collect(
    g: &mut Ground,
    w: &World,
    signer: &KernelSelf,
    join_id: &str,
    did: &str,
    sig: &Value,
) -> Result<Option<Value>, RoadError> {
    let Some(r) = get(g.client(), &w.scope, join_id).await? else {
        return Ok(None);
    };
    if r.status != "done"
        || did != r.did
        || !desk::collect_ok(did, &r.public_key, join_id, &r.nonce, sig)
    {
        return Err(RoadError::NotConfirmed { rest: false });
    }
    let by = r.admitted_by.clone().unwrap_or_default();
    if let (Some(lid), Some(raw)) = (&r.lease_id, &r.lease) {
        let token: Value = serde_json::from_str(raw).unwrap_or(Value::Null);
        return Ok(Some(
            json!({"id": join_id, "status": "done", "lease": token, "wire": seat::wire(&token),
                              "lease_id": lid, "expiry": r.expiry.map(isoformat), "admitted_by": by,
                              "words": desk::words("done", &r.name, &w.scope, Some(&by))}),
        ));
    }
    let (usd, renew_days) = crate::stable_live::lease_defaults();
    let now_ms = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .map(|d| d.as_millis() as u64)
        .unwrap_or(0);
    let expiry = envelope::iso_millis(now_ms + (desk::lease_days() as u64) * 86_400_000);
    let token =
        desk::lease(signer, did, &w.scope, &expiry, usd, renew_days).map_err(RoadError::Refused)?;
    let lid = seat::seat_id(&token);
    let e = fact(
        w,
        seat::SEAT_TAKEN,
        &lid,
        json!({"hash": content_hash(&token), "person": did, "role": "body", "expiry": expiry, "ceremony": false,
               "join": join_id}),
        vec![did.to_string(), KERNEL.into()],
    )?;
    let raw = envelope::encode(&e)?;
    let mid = e["message_id"].as_str().unwrap_or_default().to_string();
    let (l2, d2, sc2, x2, j2, t2) = (
        lid.clone(),
        did.to_string(),
        w.scope.clone(),
        expiry.clone(),
        join_id.to_string(),
        token.to_string(),
    );
    outbox::commit_with_outbox(g, &raw, &mid, None, async move |tx| {
        tx.execute(
            "INSERT INTO spine_seats (seat_id, person, scope, role, expiry) VALUES ($1, $2, $3, 'body', \
             CAST($4::text AS timestamptz)) ON CONFLICT (seat_id) DO NOTHING",
            &[&l2, &d2, &sc2, &x2],
        )
        .await?;
        tx.execute(
            "UPDATE spine_desk SET lease_id = $1, lease = $2, expiry = CAST($3::text AS timestamptz), updated_at = \
             now() WHERE join_id = $4",
            &[&l2, &t2, &x2, &j2],
        )
        .await
        .map_err(RailError::from)?;
        Ok(())
    })
    .await?;
    Ok(Some(
        json!({"id": join_id, "status": "done", "lease": token, "wire": seat::wire(&token), "lease_id": lid,
                   "expiry": expiry, "admitted_by": by,
                   "words": desk::words("done", &r.name, &w.scope, Some(&by))}),
    ))
}
