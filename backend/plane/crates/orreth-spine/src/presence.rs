// PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp4, the loops · 2026-09-23
// Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch row 4, PANEL sp2: THE LEASE FACTS — `orreth.lease.lapsed.v1` · `orreth.lease.seated.v1` minted by the kernel's sweep, noted on the ground (`noted_alive`) so two kernels never mint one lapse twice · 2026-09-28
//! Presence leases (canon 0002 M2) — `orreth_spine.presence`: a body is ALIVE
//! while its lease is fresh — it renews as it serves; a body that stops
//! renewing goes DORMANT in seconds and stays listed (the roster breathes;
//! nothing is deleted). Liveness is a fact on the ground, never an assumption
//! of the glass. This bridge holds no residents (they renew from Python);
//! `renew` is ported for the day it does, `roster` is what the monitor reads.

use crate::envelope::{self, Mint};
use crate::ground::Ground;
use crate::outbox;
use crate::world::{isoformat, RoadError, World};
use serde_json::{json, Value};
use std::time::SystemTime;

pub use crate::ask::LEASE_TTL_S as TTL_S;

/// The body's own act, every serve: "I am here until now + ttl".
pub async fn renew(
    g: &Ground,
    scope: &str,
    did: &str,
    name: &str,
    kind: &str,
    ttl_s: i64,
) -> Result<(), RoadError> {
    let ttl = ttl_s as f64;
    g.client()
        .execute(
            "INSERT INTO spine_leases (did, name, kind, scope, until) VALUES ($1, $2, $3, $4, now() \
             + make_interval(secs => $5::float8)) ON CONFLICT (did) DO UPDATE SET until = \
             EXCLUDED.until, renewed_at = now(), name = EXCLUDED.name, kind = EXCLUDED.kind",
            &[&did, &name, &kind, &scope, &ttl],
        )
        .await?;
    Ok(())
}

/// Every body that ever held a lease in this world, alive or dormant.
pub async fn roster(g: &Ground, scope: &str) -> Result<Vec<Value>, RoadError> {
    let rows = g
        .client()
        .query(
            "SELECT did, name, kind, until, renewed_at, until > now() FROM spine_leases WHERE scope \
             = $1 ORDER BY name",
            &[&scope],
        )
        .await?;
    Ok(rows
        .iter()
        .map(|r| {
            json!({
                "did": r.get::<_, String>(0), "name": r.get::<_, String>(1),
                "kind": r.get::<_, String>(2),
                "until": isoformat(r.get::<_, SystemTime>(3)),
                "renewed_at": isoformat(r.get::<_, SystemTime>(4)),
                "alive": r.get::<_, bool>(5),
            })
        })
        .collect())
}

// ---- row 4, panel sp2: THE LEASE FACTS ------------------------------------------------
// A lease was polled state: the glass re-read the roster on a beat and a body that stopped
// renewing went dark twenty seconds late. Now the kernel SWEEPS the leases and every line
// crossed is a fact on the feed — the panel's station follows within the sweep's cadence.

pub use crate::ask::{lease_fact, lease_payload, KERNEL, LEASE_LAPSED, LEASE_SEATED};
/// The sweep's cadence, in seconds — a third of the lease's life.
pub const SWEEP_S: u64 = 5;

/// THE SWEEP: every lease whose liveness differs from what the ground last NOTED is
/// noted anew in one atomic update — the rows returned are the lines crossed, and each
/// becomes its fact through the outbox. The note lives on the ground (`noted_alive`),
/// not in this kernel: two kernels on one ground race for the row and only one wins
/// it, so no lapse is minted twice. A lease never noted (the column born NULL on an old
/// ground) is noted silently — its history was not watched, so no fact is invented.
/// Returns the facts minted, in the roster's order.
pub async fn sweep(g: &mut Ground, w: &World) -> Result<Vec<Value>, RoadError> {
    g.client()
        .execute(
            "UPDATE spine_leases SET noted_alive = (until > now()) WHERE scope = $1 AND noted_alive \
             IS NULL",
            &[&w.scope],
        )
        .await?;
    let rows = g
        .client()
        .query(
            "UPDATE spine_leases SET noted_alive = (until > now()) WHERE scope = $1 AND noted_alive \
             IS DISTINCT FROM (until > now()) RETURNING did, name, kind, until, (until > now()) \
             AS alive",
            &[&w.scope],
        )
        .await?;
    let mut minted = Vec::new();
    for r in rows {
        let (did, name, kind): (String, String, String) = (r.get(0), r.get(1), r.get(2));
        let until = isoformat(r.get::<_, SystemTime>(3));
        let alive: bool = r.get(4);
        let e = Mint {
            kind: "event".into(),
            r#type: if alive { LEASE_SEATED } else { LEASE_LAPSED }.into(),
            universe_id: w.scope.clone(),
            scope_path: w.scope.clone(),
            payload: lease_payload(&name, &did, &kind, &until),
            correlation_id: Some(did.clone()),
            authority_chain: Some(vec![KERNEL.into()]),
            ..Default::default()
        }
        .mint()?;
        let raw = envelope::encode(&e)?;
        let mid = e["message_id"].as_str().unwrap_or_default().to_string();
        outbox::commit_with_outbox(g, &raw, &mid, None, async |_tx| Ok(())).await?;
        eprintln!(
            "  [kernel] {name}'s lease {} ({})",
            if alive {
                "is seated again"
            } else {
                "lapsed — it stopped renewing"
            },
            kind
        );
        minted.push(e);
    }
    Ok(minted)
}
