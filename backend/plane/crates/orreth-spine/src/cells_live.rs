// PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp7, cells · partition · isolation · hardening · 2026-09-25
//! The cell's LIVE half (canon 0002 rule 8 · 0005 P7 sp7): the universe's
//! home on the ground (`spine_world`: one row per universe — its cell, its
//! epoch, the kernel that keeps it), settled at light and said as a fact
//! (`orreth.world.homed.v1`); the world card both doors serve (rule 7); the
//! tenth health check ("this cell is sealed": the connection's role reaches
//! its own database and no other); the peers as the ground remembers them.
//! Mirrors `orreth_spine.cells`' record half word for word.

use crate::cells::{self, DEFAULT_CELL};
use crate::envelope;
use crate::ground::Ground;
use crate::rail_error::RailError;
use crate::world::{refused, RoadError, World};
use serde_json::{json, Value};
use tokio_postgres::Transaction;

pub const REHOME_TOOL: &str = "world.rehome";
pub const REHOME_CLASS: &str = "consequential";
pub const REHOME_LEVEL: &str = "L2";

/// `cells.ensure_schema`: the world, its peers, the seam's nonces.
pub use crate::schema::CELLS_DDL;

/// This kernel's cell — the ground declares it (`SPINE_CELL`, else `local`).
pub fn cell_here() -> String {
    std::env::var("SPINE_CELL")
        .ok()
        .filter(|c| !c.is_empty())
        .unwrap_or_else(|| DEFAULT_CELL.to_string())
}

/// The universe's home, settled at light: absent → this cell, epoch 1, the
/// `opened` fact in the row's own transaction; present in THIS cell → the
/// kernel and its door refreshed, nothing new said; present in another cell
/// → refused in words (a kernel of a different cell may not light over it).
pub async fn home(
    g: &mut Ground,
    scope: &str,
    cell: &str,
    kernel_did: &str,
    door: &str,
) -> Result<Value, RoadError> {
    let row = g
        .client()
        .query_opt(
            "SELECT cell, epoch FROM spine_world WHERE scope = $1",
            &[&scope],
        )
        .await?;
    match row {
        None => {
            let e = cells::world_fact(scope, cell, 1, kernel_did, door, "opened")?;
            let raw = envelope::encode(&e)?;
            let (scope_s, cell_s, kernel_s, door_s) = (
                scope.to_string(),
                cell.to_string(),
                kernel_did.to_string(),
                door.to_string(),
            );
            crate::outbox::commit_with_outbox(
                g,
                &raw,
                e["message_id"].as_str().unwrap_or_default(),
                None,
                async |tx| {
                    tx.execute(
                        "INSERT INTO spine_world (scope, cell, epoch, kernel, door) VALUES ($1, $2, 1, $3, $4) \
                         ON CONFLICT (scope) DO NOTHING",
                        &[&scope_s, &cell_s, &kernel_s, &door_s],
                    )
                    .await?;
                    Ok::<(), RailError>(())
                },
            )
            .await?;
        }
        Some(r) => {
            let (there, epoch): (String, i32) = (r.get(0), r.get(1));
            if there != cell {
                return Err(refused(format!(
                    "{scope} is homed in cell {there} (epoch {epoch}) — this kernel says it is cell {cell}; \
                     light it as cell {there}, or re-home the universe first"
                )));
            }
            g.client()
                .execute(
                    "UPDATE spine_world SET kernel = $1, door = $2 WHERE scope = $3",
                    &[&kernel_did, &door, &scope],
                )
                .await?;
        }
    }
    card(g, scope, cell, Some(kernel_did), "", "UTC").await
}

/// The world card (rule 7 — the same on both doors): the universe, its cell
/// and epoch, the kernel that keeps it, its peers with their lag.
pub async fn card(
    g: &Ground,
    scope: &str,
    cell: &str,
    kernel_did: Option<&str>,
    ns: &str,
    zone: &str,
) -> Result<Value, RoadError> {
    let row = g
        .client()
        .query_opt(
            "SELECT cell, epoch, kernel, door, opened_at, rehomed_at, rehomed_by FROM spine_world WHERE scope = $1",
            &[&scope],
        )
        .await?;
    let iso = |t: Option<std::time::SystemTime>| t.map(crate::world::isoformat);
    Ok(match row {
        Some(r) => json!({
            "scope": scope, "cell": r.get::<_, String>(0), "epoch": r.get::<_, i32>(1),
            "kernel": r.get::<_, String>(2), "door": r.get::<_, Option<String>>(3),
            "opened_at": iso(r.get::<_, Option<std::time::SystemTime>>(4)),
            "rehomed_at": iso(r.get::<_, Option<std::time::SystemTime>>(5)),
            "rehomed_by": r.get::<_, Option<String>>(6), "homed": true,
            "namespace": ns, "peers": peers(g, scope, zone).await?,
        }),
        None => json!({
            "scope": scope, "cell": cell, "epoch": Value::Null, "kernel": kernel_did, "door": Value::Null,
            "opened_at": Value::Null, "rehomed_at": Value::Null, "rehomed_by": Value::Null, "homed": false,
            "namespace": ns, "peers": peers(g, scope, zone).await?,
        }),
    })
}

/// The world's epoch as the ground holds it (1 when the row is missing).
pub async fn epoch(g: &Ground, scope: &str) -> Result<i64, RoadError> {
    let row = g
        .client()
        .query_opt("SELECT epoch FROM spine_world WHERE scope = $1", &[&scope])
        .await?;
    Ok(row.map(|r| r.get::<_, i32>(0) as i64).unwrap_or(1))
}

/// Every peer this cell names, as the ground remembers it.
pub async fn peers(g: &Ground, scope: &str, zone: &str) -> Result<Vec<Value>, RoadError> {
    let rows = g
        .client()
        .query(
            "SELECT cell, door, did, world, epoch, pinned_at, last_seen, cursor, unreachable_since, \
             extract(epoch FROM (clock_timestamp() - last_seen))::float8, \
             to_char(unreachable_since AT TIME ZONE $2, 'HH24:MI') FROM spine_peers WHERE scope = $1 ORDER BY cell",
            &[&scope, &zone],
        )
        .await?;
    let iso = |t: Option<std::time::SystemTime>| t.map(crate::world::isoformat);
    Ok(rows
        .iter()
        .map(|r| {
            let cell: String = r.get(0);
            let world: Option<String> = r.get(3);
            let behind: Option<f64> = r.get(9);
            let since: Option<String> = r.get(10);
            json!({
                "cell": cell, "door": r.get::<_, String>(1), "did": r.get::<_, Option<String>>(2),
                "world": world, "epoch": r.get::<_, Option<i32>>(4),
                "pinned_at": iso(r.get::<_, Option<std::time::SystemTime>>(5)),
                "last_seen": iso(r.get::<_, Option<std::time::SystemTime>>(6)),
                "cursor": r.get::<_, i64>(7),
                "unreachable_since": iso(r.get::<_, Option<std::time::SystemTime>>(8)),
                "words": cells::lag_words(&cell, world.as_deref(), behind, since.as_deref()),
            })
        })
        .collect())
}

/// The tenth check, read off the ground: which databases this connection's
/// role may enter. Sealed iff only its own.
pub async fn sealed(g: &Ground) -> Result<Value, RoadError> {
    let r = g
        .client()
        .query_one("SELECT current_user::text, current_database()::text", &[])
        .await?;
    let (role, own): (String, String) = (r.get(0), r.get(1));
    let reachable: Vec<String> = g
        .client()
        .query(
            "SELECT datname::text FROM pg_database WHERE datallowconn AND NOT datistemplate AND \
             has_database_privilege(current_user, datname, 'CONNECT') ORDER BY datname",
            &[],
        )
        .await?
        .iter()
        .map(|r| r.get(0))
        .collect();
    let (ok, words) = cells::sealed_words(&role, &own, &reachable);
    Ok(
        json!({"name": "this cell is sealed", "ok": ok, "detail": words, "role": role,
              "database": own, "reachable": reachable}),
    )
}

/// The fencing law at the action boundary: a universe re-homed elsewhere is
/// no longer this kernel's to serve — the words, or `None` when it is.
pub async fn fence(g: &Ground, scope: &str, cell: &str) -> Result<Option<String>, RoadError> {
    let row = g
        .client()
        .query_opt(
            "SELECT cell, epoch FROM spine_world WHERE scope = $1",
            &[&scope],
        )
        .await?;
    Ok(match row {
        Some(r) if r.get::<_, String>(0) != cell => Some(format!(
            "{scope} was re-homed to cell {} at epoch {} — this kernel (cell {cell}) no longer serves it",
            r.get::<_, String>(0),
            r.get::<_, i32>(1)
        )),
        _ => None,
    })
}

/// Re-homing is consequential: held at the interlock as one of the kernel's own acts (L2).
pub async fn hold_rehome(
    g: &mut Ground,
    w: &World,
    to_cell: &str,
    person: &str,
    session: Option<&str>,
) -> Result<String, RoadError> {
    let to_cell = to_cell.trim().to_lowercase();
    if to_cell.is_empty()
        || !to_cell
            .chars()
            .all(|c| c.is_ascii_alphanumeric() || c == '-' || c == '_')
    {
        return Err(refused(
            "a cell's name is lower-case letters, digits, - and _",
        ));
    }
    let here: String = g
        .client()
        .query_opt("SELECT cell FROM spine_world WHERE scope = $1", &[&w.scope])
        .await?
        .map(|r| r.get(0))
        .unwrap_or_else(cell_here);
    if here == to_cell {
        return Err(refused(format!(
            "{} already stands in cell {to_cell}",
            w.scope
        )));
    }
    crate::proof_live::hold_kernel_act(
        g,
        w,
        &format!("re-homing {} from cell {here} to cell {to_cell}", w.scope),
        person,
        REHOME_TOOL,
        json!({"to_cell": to_cell}),
        REHOME_LEVEL,
        session,
        REHOME_CLASS,
        false,
    )
    .await
}

/// The act settled on the yes, inside the held ask's own transaction: the
/// row moves, the epoch advances, the fact rides the same outbox.
pub async fn rehome_in(
    tx: &Transaction<'_>,
    w: &World,
    to_cell: &str,
    by: &str,
) -> Result<String, RoadError> {
    let r = tx
        .query_one(
            "UPDATE spine_world SET cell = $2, epoch = epoch + 1, rehomed_at = clock_timestamp(), rehomed_by = $3 \
             WHERE scope = $1 RETURNING epoch, kernel, door, (SELECT cell FROM spine_world WHERE scope = $1)",
            &[&w.scope, &to_cell, &by],
        )
        .await?;
    let (epoch, kernel, door): (i32, String, Option<String>) = (r.get(0), r.get(1), r.get(2));
    let from_cell: String = r.get(3);
    let e = cells::world_fact(
        &w.scope,
        to_cell,
        epoch as i64,
        &kernel,
        door.as_deref().unwrap_or(""),
        "re-homed",
    )?;
    crate::outbox::add_row(
        tx,
        &envelope::encode(&e)?,
        e["message_id"].as_str().unwrap_or_default(),
    )
    .await?;
    Ok(cells::rehome_words(
        &w.scope,
        &from_cell,
        to_cell,
        epoch as i64,
    ))
}
