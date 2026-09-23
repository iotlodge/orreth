// PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp3, the ask road · 2026-09-22
//! The ask road's tables — the Python spine's DDL, word for word, under the
//! same tags its `once` guard uses (`resident` · `markers` · `proof` · `intent`
//! · `presence` · `digest`), so two spines on one ground never disagree about a
//! column. Every statement is `IF NOT EXISTS`; every birth runs inside the
//! advisory-locked transaction the ground law demands (`Ground::ensure`).
//! The tables this spine only READS (`spine_refusals` · `spine_services` ·
//! `spine_schedules`) are the Python's to create — the readers ask
//! `to_regclass` first, as the reference does.

use crate::ground::Ground;
use crate::rail_error::RailError;

/// `resident.ensure_schema`: the joins, the asks, the sessions.
pub const RESIDENT_DDL: &[&str] = &[
    "CREATE TABLE IF NOT EXISTS spine_joins ( join_id bigserial PRIMARY KEY, did text NOT NULL, \
     name text NOT NULL, life int NOT NULL, template_hash text NOT NULL, policy_version text NOT \
     NULL, policy_hash text NOT NULL, sig text NOT NULL, joined_at timestamptz NOT NULL DEFAULT \
     now())",
    "CREATE TABLE IF NOT EXISTS spine_asks ( ask_id text PRIMARY KEY, text text NOT NULL, person \
     text NOT NULL, status text NOT NULL DEFAULT 'received', reply text, served_by text, held \
     text, asked_at timestamptz NOT NULL DEFAULT now(), replied_at timestamptz)",
    "ALTER TABLE spine_asks ADD COLUMN IF NOT EXISTS held text",
    "ALTER TABLE spine_asks ADD COLUMN IF NOT EXISTS seq int NOT NULL DEFAULT 1",
    "ALTER TABLE spine_asks ADD COLUMN IF NOT EXISTS target text",
    "ALTER TABLE spine_asks ADD COLUMN IF NOT EXISTS scope text",
    "ALTER TABLE spine_joins ADD COLUMN IF NOT EXISTS scope text",
    "ALTER TABLE spine_asks ADD COLUMN IF NOT EXISTS time_window text",
    "ALTER TABLE spine_asks ADD COLUMN IF NOT EXISTS session text",
    "ALTER TABLE spine_joins ADD COLUMN IF NOT EXISTS kind text NOT NULL DEFAULT 'resident'",
    "ALTER TABLE spine_joins ADD COLUMN IF NOT EXISTS capabilities text",
    "CREATE TABLE IF NOT EXISTS spine_sessions ( session_id text PRIMARY KEY, person text NOT \
     NULL, scope text NOT NULL, title text, opened_at timestamptz NOT NULL DEFAULT now())",
    "ALTER TABLE spine_sessions ADD COLUMN IF NOT EXISTS state text NOT NULL DEFAULT 'in'",
    "ALTER TABLE spine_asks ADD COLUMN IF NOT EXISTS state text NOT NULL DEFAULT 'in'",
    "ALTER TABLE spine_asks ADD COLUMN IF NOT EXISTS marker text",
    "ALTER TABLE spine_joins ADD COLUMN IF NOT EXISTS interests text",
    "ALTER TABLE spine_asks ADD COLUMN IF NOT EXISTS fanout text",
    "ALTER TABLE spine_asks ADD COLUMN IF NOT EXISTS proof text NOT NULL DEFAULT 'L1'",
    "ALTER TABLE spine_joins ADD COLUMN IF NOT EXISTS placement text",
    "ALTER TABLE spine_asks ADD COLUMN IF NOT EXISTS zone text",
    "ALTER TABLE spine_sessions ADD COLUMN IF NOT EXISTS zone text",
    "ALTER TABLE spine_joins ADD COLUMN IF NOT EXISTS nature text",
];

/// `markers.ensure_schema`: the registry, the markers, the ROOT column (P25)
/// and its once-only back-fill for rows from before the column.
pub const MARKERS_DDL: &[&str] = &[
    "CREATE TABLE IF NOT EXISTS spine_marker_kinds ( kind text NOT NULL, grp text NOT NULL, \
     description text NOT NULL, declared_by text NOT NULL, scope text NOT NULL, declared_at \
     timestamptz NOT NULL DEFAULT now(), PRIMARY KEY (kind, scope))",
    "CREATE TABLE IF NOT EXISTS spine_markers ( marker_id text PRIMARY KEY, kind text NOT NULL, \
     parent text, ref text NOT NULL, by_did text NOT NULL, note text, scope text NOT NULL, at \
     timestamptz NOT NULL DEFAULT now())",
    "CREATE INDEX IF NOT EXISTS spine_markers_parent ON spine_markers (parent)",
    "CREATE INDEX IF NOT EXISTS spine_markers_kind ON spine_markers (scope, kind, at)",
    "ALTER TABLE spine_markers ADD COLUMN IF NOT EXISTS root text",
    "CREATE INDEX IF NOT EXISTS spine_markers_root ON spine_markers (scope, root)",
    "CREATE INDEX IF NOT EXISTS spine_markers_roots ON spine_markers (scope, at) WHERE parent IS \
     NULL",
    "WITH RECURSIVE r AS (  SELECT marker_id, marker_id AS root FROM spine_markers WHERE parent \
     IS NULL  UNION ALL  SELECT m.marker_id, r.root FROM spine_markers m JOIN r ON m.parent = \
     r.marker_id) UPDATE spine_markers s SET root = r.root FROM r WHERE s.marker_id = \
     r.marker_id AND s.root IS NULL",
];

/// `proof.ensure_schema`: the authenticators, the masters, the attempts.
pub const PROOF_DDL: &[&str] = &[
    "CREATE TABLE IF NOT EXISTS spine_authenticators ( auth_id bigserial PRIMARY KEY, person text \
     NOT NULL, secret text NOT NULL, scope text NOT NULL, enrolled_at timestamptz NOT NULL \
     DEFAULT now(), confirmed_at timestamptz, retired_at timestamptz)",
    "CREATE TABLE IF NOT EXISTS spine_masters ( person text NOT NULL, declared_by text NOT NULL, \
     scope text NOT NULL, declared_at timestamptz NOT NULL DEFAULT now(), PRIMARY KEY (person, \
     scope))",
    "CREATE TABLE IF NOT EXISTS spine_proof_attempts ( attempt_id bigserial PRIMARY KEY, ask_id \
     text NOT NULL, by_did text NOT NULL, level text NOT NULL, ok boolean NOT NULL, at \
     timestamptz NOT NULL DEFAULT now())",
];

/// `intent.ensure_schema`: the intentions and their turns.
pub const INTENT_DDL: &[&str] = &[
    "CREATE TABLE IF NOT EXISTS spine_intentions ( intention_id text PRIMARY KEY, words text NOT \
     NULL, serves text NOT NULL, kind text NOT NULL, interests text NOT NULL, planner text NOT \
     NULL, runner text, every_s int, gates text, active boolean NOT NULL DEFAULT true, \
     stopped_by text, stopped_at timestamptz, added_by text NOT NULL, scope text NOT NULL, \
     marker text NOT NULL, session text, next_at timestamptz, last_at timestamptz, added_at \
     timestamptz NOT NULL DEFAULT now())",
    "CREATE TABLE IF NOT EXISTS spine_intent_turns ( turn_id text PRIMARY KEY, intention_id text \
     NOT NULL, cause text, plan_ask text NOT NULL, objective_ask text, at timestamptz NOT NULL \
     DEFAULT now())",
    "CREATE UNIQUE INDEX IF NOT EXISTS spine_intent_turns_cause ON spine_intent_turns (cause) \
     WHERE cause IS NOT NULL",
    "ALTER TABLE spine_intentions ADD COLUMN IF NOT EXISTS blocked_crew text",
    "ALTER TABLE spine_intentions ADD COLUMN IF NOT EXISTS blocked_note text",
    "ALTER TABLE spine_intent_turns ADD COLUMN IF NOT EXISTS heard boolean NOT NULL DEFAULT false",
    "ALTER TABLE spine_intentions ADD COLUMN IF NOT EXISTS restarted_by text",
    "ALTER TABLE spine_intentions ADD COLUMN IF NOT EXISTS restarted_at timestamptz",
];

/// `presence.ensure_schema`: the leases (M2).
pub const PRESENCE_DDL: &[&str] = &[
    "CREATE TABLE IF NOT EXISTS spine_leases ( did text PRIMARY KEY, name text NOT NULL, kind text \
     NOT NULL, scope text NOT NULL, until timestamptz NOT NULL, renewed_at timestamptz NOT NULL \
     DEFAULT now())",
];

/// `digest.ensure_schema`: the short versions (MEM-3) — read by the sessions door.
pub const DIGEST_DDL: &[&str] = &[
    "CREATE TABLE IF NOT EXISTS spine_digests ( digest_id text PRIMARY KEY, kind text NOT NULL, \
     ref text NOT NULL, body text NOT NULL, sources text NOT NULL, hash text NOT NULL, by_did \
     text NOT NULL, scope text NOT NULL, supersedes text, built_at timestamptz NOT NULL DEFAULT \
     now(), valid_from timestamptz NOT NULL DEFAULT now(), valid_to timestamptz)",
    "CREATE UNIQUE INDEX IF NOT EXISTS spine_digests_current ON spine_digests (kind, ref, scope) \
     WHERE valid_to IS NULL",
    "ALTER TABLE spine_digests ADD COLUMN IF NOT EXISTS state text NOT NULL DEFAULT 'in'",
];

/// The tags and their DDL, in the order the road ensures them.
pub const ROAD: [(&str, &[&str]); 6] = [
    ("resident", RESIDENT_DDL),
    ("markers", MARKERS_DDL),
    ("proof", PROOF_DDL),
    ("intent", INTENT_DDL),
    ("presence", PRESENCE_DDL),
    ("digest", DIGEST_DDL),
];

/// Every table the ask road stands on, once per ground per process.
pub async fn ensure_road(g: &mut Ground) -> Result<(), RailError> {
    for (tag, ddl) in ROAD {
        g.ensure(tag, ddl).await?;
    }
    Ok(())
}

/// Does a table the Python spine owns stand on this ground?
pub async fn has_table(g: &Ground, table: &str) -> Result<bool, RailError> {
    let row = g
        .client()
        .query_one("SELECT to_regclass($1) IS NOT NULL", &[&table])
        .await?;
    Ok(row.get(0))
}
