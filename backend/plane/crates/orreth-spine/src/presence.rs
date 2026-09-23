// PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp4, the loops · 2026-09-23
//! Presence leases (canon 0002 M2) — `orreth_spine.presence`: a body is ALIVE
//! while its lease is fresh — it renews as it serves; a body that stops
//! renewing goes DORMANT in seconds and stays listed (the roster breathes;
//! nothing is deleted). Liveness is a fact on the ground, never an assumption
//! of the glass. This bridge holds no residents (they renew from Python);
//! `renew` is ported for the day it does, `roster` is what the monitor reads.

use crate::ground::Ground;
use crate::world::{isoformat, RoadError};
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
