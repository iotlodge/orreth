// PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp3, the ask road · 2026-09-22
// Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp4, the loops: the watches · the schedules · the harness runs · 2026-09-23
// Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp5, memory and the export · 2026-09-24
// Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp6, the bodies' seam: the shelf · the Stable · the meter · 2026-09-24
// Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp7, cells: the meter's world · the cells' tables · 2026-09-25
// Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp8, the human profile's table (W58) · 2026-09-26
// Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp8 row 3, the seat's tables (the gate) · 2026-09-26
// Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch row 4, PANEL sp2: `spine_leases.noted_alive` — the sweep's note on the ground · 2026-09-28
// Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch row 4, re-base sp1: THE MIGRATOR (lock 2) — `spine_schema`, the version, every table both kernels stand on · 2026-09-28
// Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch row 4, the perf cure before sp2 (JB's word 2026-09-29): SCHEMA VERSION 2 — the indexes the doors and the relay were missing · 2026-09-29
// Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch row 4, the honest glass sp2: SCHEMA VERSION 3 — a watch's rest (`spine_watches.active` · `rested_by` · `rested_at`) and a peer's forgetting (`spine_peers.forgotten_by` · `forgotten_at`), recorded on their rows (rule 11) · 2026-09-29
//! The ask road's tables — the Python spine's DDL, word for word, under the
//! same tags its `once` guard uses (`resident` · `markers` · `proof` · `intent`
//! · `presence` · `digest`), so two spines on one ground never disagree about a
//! column. Every statement is `IF NOT EXISTS`; every birth runs inside the
//! advisory-locked transaction the ground law demands (`Ground::ensure`).
//! P7 sp4 adds the loops' three (`monitor` · `scheduler` · `harness`). The
//! tables this spine only READS (`spine_refusals` · `spine_services` · its
//! health) are the Python's to create — the readers ask `to_regclass` first,
//! as the reference does.

#[cfg(feature = "rails")]
use crate::ground::Ground;
#[cfg(feature = "rails")]
use crate::rail_error::RailError;
use regex::Regex;
use std::sync::LazyLock;

/// THE MIGRATOR (lock 2, re-base sp1): the ground's schema wears a VERSION. Both kernels
/// carry the same number and the same set of tables (fixture `schema-v0.json` pins both);
/// whenever any DDL statement changes, the number is bumped in BOTH kernels in the same
/// change. At birth the first kernel to take the DDL lock and find the ground below its
/// number runs every statement and records the number; a kernel that finds the ground at
/// (or past) its number runs no DDL at all — it VERIFIES that every table it declares
/// stands, and refuses to light on a ground that lies. A kernel lighting beside a
/// migrating one WAITS at the lock and then verifies (`Ground::ensure_all`).
pub const SCHEMA_VERSION: i32 = 3; // 2: the indexes (the perf cure, 2026-09-29) · 3: a watch's rest, a peer's forgetting (the honest glass sp2, 2026-09-29)

/// The version table itself — created before the version is read, under the same lock.
pub const SCHEMA_DDL: &[&str] = &[
    "CREATE TABLE IF NOT EXISTS spine_schema ( version int PRIMARY KEY, kernel text NOT NULL, \
     migrated_at timestamptz NOT NULL DEFAULT now())",
];

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
    // schema 2 (the perf cure): the crew's read, the served count, a session's latest ask, the
    // monitor's counts by status — each was a sequential scan of every world's rows
    "CREATE INDEX IF NOT EXISTS spine_joins_scope_name ON spine_joins (scope, name, join_id DESC)",
    "CREATE INDEX IF NOT EXISTS spine_asks_scope_served ON spine_asks (scope, served_by)",
    "CREATE INDEX IF NOT EXISTS spine_asks_session ON spine_asks (session, asked_at DESC)",
    "CREATE INDEX IF NOT EXISTS spine_asks_scope_status ON spine_asks (scope, status)",
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
    // P7 sp8 row 3c: the remediation rail — the dossier the planner read, the lever the kernel
    // pulled (its args, the planner's reason, the hop's ask, when), the outcome attributed
    "ALTER TABLE spine_intent_turns ADD COLUMN IF NOT EXISTS dossier text",
    "ALTER TABLE spine_intent_turns ADD COLUMN IF NOT EXISTS watch text",
    "ALTER TABLE spine_intent_turns ADD COLUMN IF NOT EXISTS episode text",
    "ALTER TABLE spine_intent_turns ADD COLUMN IF NOT EXISTS tries int NOT NULL DEFAULT 1",
    "ALTER TABLE spine_intent_turns ADD COLUMN IF NOT EXISTS lever text",
    "ALTER TABLE spine_intent_turns ADD COLUMN IF NOT EXISTS lever_args text",
    "ALTER TABLE spine_intent_turns ADD COLUMN IF NOT EXISTS because text",
    "ALTER TABLE spine_intent_turns ADD COLUMN IF NOT EXISTS lever_ask text",
    "ALTER TABLE spine_intent_turns ADD COLUMN IF NOT EXISTS pulled_at timestamptz",
    "ALTER TABLE spine_intent_turns ADD COLUMN IF NOT EXISTS outcome text",
    "ALTER TABLE spine_intent_turns ADD COLUMN IF NOT EXISTS outcome_at timestamptz",
    "ALTER TABLE spine_intent_turns ADD COLUMN IF NOT EXISTS outcome_note text",
];

/// `presence.ensure_schema`: the leases (M2).
pub const PRESENCE_DDL: &[&str] = &[
    "CREATE TABLE IF NOT EXISTS spine_leases ( did text PRIMARY KEY, name text NOT NULL, kind text \
     NOT NULL, scope text NOT NULL, until timestamptz NOT NULL, renewed_at timestamptz NOT NULL \
     DEFAULT now())",
    // row 4, panel sp2: what the sweep last noted of the lease's liveness — the note lives on
    // the ground so two kernels never mint one lapse twice (`presence::sweep`)
    "ALTER TABLE spine_leases ADD COLUMN IF NOT EXISTS noted_alive boolean",
    // schema 2: the roster and the sweep read one world's leases, not every world's
    "CREATE INDEX IF NOT EXISTS spine_leases_scope ON spine_leases (scope, name)",
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

/// `monitor.ensure_schema`: the watches, their recorded state (W14).
pub const MONITOR_DDL: &[&str] = &[
    "CREATE TABLE IF NOT EXISTS spine_watches ( watch_id text PRIMARY KEY, name text NOT NULL, \
     metric text NOT NULL, op text NOT NULL, threshold double precision NOT NULL, added_by text \
     NOT NULL, scope text NOT NULL, added_at timestamptz NOT NULL DEFAULT now())",
    "ALTER TABLE spine_watches ADD COLUMN IF NOT EXISTS last_ok boolean",
    "ALTER TABLE spine_watches ADD COLUMN IF NOT EXISTS since timestamptz",
    // schema 3 (the honest glass sp2, W86): a watch's REST — recorded on its row, never a delete
    // (rule 11: there was no way to rest a watch)
    "ALTER TABLE spine_watches ADD COLUMN IF NOT EXISTS active boolean NOT NULL DEFAULT true",
    "ALTER TABLE spine_watches ADD COLUMN IF NOT EXISTS rested_by text",
    "ALTER TABLE spine_watches ADD COLUMN IF NOT EXISTS rested_at timestamptz",
];

/// `scheduler.ensure_schema`: the schedules (with their intention's marker), the occurrences.
pub const SCHEDULER_DDL: &[&str] = &[
    "CREATE TABLE IF NOT EXISTS spine_schedules ( schedule_id text PRIMARY KEY, runner text NOT \
     NULL, kind text NOT NULL, text text NOT NULL, every_s int NOT NULL, next_at timestamptz NOT \
     NULL DEFAULT now(), last_at timestamptz, active boolean NOT NULL DEFAULT true, added_by text \
     NOT NULL, rested_by text, rested_at timestamptz, scope text NOT NULL, added_at timestamptz \
     NOT NULL DEFAULT now())",
    "ALTER TABLE spine_schedules ADD COLUMN IF NOT EXISTS marker text",
    "CREATE TABLE IF NOT EXISTS spine_occurrences ( occurrence_id text PRIMARY KEY, schedule_id \
     text NOT NULL, ref text, at timestamptz NOT NULL DEFAULT now())",
];

/// `harness.ensure_schema`: the runs.
pub const HARNESS_DDL: &[&str] = &[
    "CREATE TABLE IF NOT EXISTS spine_harness_runs ( run_id text PRIMARY KEY, template text NOT \
     NULL, version text NOT NULL, passed int NOT NULL, failed int NOT NULL, details text NOT \
     NULL, scope text NOT NULL, ran_at timestamptz NOT NULL DEFAULT now())",
    // P6.5 sp3 on the reference: the mind this run rode (the migrator's parity proof found it missing here)
    "ALTER TABLE spine_harness_runs ADD COLUMN IF NOT EXISTS arm text",
];

/// `services.ensure_schema` (P6.5 sp1): the shelf — one registry for tool · mcp · store · source · mind.
pub const SERVICES_DDL: &[&str] = &[
    "CREATE TABLE IF NOT EXISTS spine_services ( name text NOT NULL, scope text NOT NULL, kind text \
     NOT NULL, did text NOT NULL, manifest text NOT NULL, manifest_hash text NOT NULL, version int \
     NOT NULL DEFAULT 1, placement text NOT NULL, secrets_with text NOT NULL DEFAULT '[]', state \
     text NOT NULL, by_did text NOT NULL, since timestamptz NOT NULL DEFAULT now(), registered_at \
     timestamptz NOT NULL DEFAULT now(), last_ok boolean, last_detail text, last_checked_at \
     timestamptz, marker text, root_marker text, PRIMARY KEY (name, scope))",
    "CREATE TABLE IF NOT EXISTS spine_service_versions ( version_id bigserial PRIMARY KEY, name \
     text NOT NULL, scope text NOT NULL, version int NOT NULL, manifest text NOT NULL, \
     manifest_hash text NOT NULL, by_did text NOT NULL, at timestamptz NOT NULL DEFAULT now())",
    "CREATE TABLE IF NOT EXISTS spine_service_health ( health_id bigserial PRIMARY KEY, name text \
     NOT NULL, scope text NOT NULL, did text NOT NULL, ok boolean, detail text NOT NULL, at \
     timestamptz NOT NULL DEFAULT now())",
    "CREATE INDEX IF NOT EXISTS spine_services_kind ON spine_services (scope, kind)",
    "DO $$ BEGIN IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema = current_schema() AND table_name = \
     'spine_services' AND column_name = 'root_marker') THEN ALTER TABLE spine_services ADD COLUMN root_marker text; END IF; \
     END $$",
];

/// `stable.ensure_schema` (P6.5 sp3): the assignments and the bodies' keys (the fuel clause).
pub const STABLE_DDL: &[&str] = &[
    "CREATE TABLE IF NOT EXISTS spine_mind_assignments ( subject text NOT NULL, scope text NOT \
     NULL, klass text NOT NULL, stall text NOT NULL, by_did text NOT NULL, at timestamptz NOT NULL \
     DEFAULT now(), PRIMARY KEY (subject, scope, klass))",
    "CREATE TABLE IF NOT EXISTS spine_mind_keys ( did text NOT NULL, scope text NOT NULL, alias \
     text NOT NULL, key text NOT NULL, max_usd double precision NOT NULL, renew_days int NOT NULL, \
     made_at timestamptz NOT NULL DEFAULT now(), drained_at timestamptz, refills int NOT NULL \
     DEFAULT 0, PRIMARY KEY (did, scope))",
];

/// `gateway.ensure_schema`: the meter — every thought's line.
pub const GATEWAY_DDL: &[&str] = &[
    "CREATE TABLE IF NOT EXISTS spine_meter ( meter_id bigserial PRIMARY KEY, did text NOT NULL, \
     model text NOT NULL, tokens_in int NOT NULL, tokens_out int NOT NULL, at timestamptz NOT NULL \
     DEFAULT now())",
    // P7 sp7: the meter wears its world — the per-world roll-up
    "ALTER TABLE spine_meter ADD COLUMN IF NOT EXISTS scope text",
    "DO $$ BEGIN IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema = current_schema() AND table_name = \
     'spine_meter' AND column_name = 'service') THEN ALTER TABLE spine_meter ADD COLUMN service text; END IF; \
     END $$",
    "DO $$ BEGIN IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema = current_schema() AND table_name = \
     'spine_meter' AND column_name = 'usd') THEN ALTER TABLE spine_meter ADD COLUMN usd double precision; END IF; \
     END $$",
    "DO $$ BEGIN IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema = current_schema() AND table_name = \
     'spine_meter' AND column_name = 'stall') THEN ALTER TABLE spine_meter ADD COLUMN stall text; END IF; \
     END $$",
    "DO $$ BEGIN IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema = current_schema() AND table_name = \
     'spine_meter' AND column_name = 'request_id') THEN ALTER TABLE spine_meter ADD COLUMN request_id text; END IF; \
     END $$",
    "DO $$ BEGIN IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema = current_schema() AND table_name = \
     'spine_meter' AND column_name = 'ok') THEN ALTER TABLE spine_meter ADD COLUMN ok boolean NOT NULL DEFAULT true; END IF; \
     END $$",
    "DO $$ BEGIN IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema = current_schema() AND table_name = \
     'spine_meter' AND column_name = 'note') THEN ALTER TABLE spine_meter ADD COLUMN note text; END IF; \
     END $$",
    // schema 2: a body's last meter line and its spend, by its self
    "CREATE INDEX IF NOT EXISTS spine_meter_did ON spine_meter (did, meter_id DESC)",
];

/// `mitl.ensure_schema` (re-base sp1: the four Python-only doors cross): the soft toggle's
/// record — summoned · dismissed, never a deletion.
pub const MITL_DDL: &[&str] = &[
    "CREATE TABLE IF NOT EXISTS spine_mitl ( row_id bigserial PRIMARY KEY, session text, person \
     text NOT NULL, state text NOT NULL, marker text, scope text NOT NULL, at timestamptz NOT \
     NULL DEFAULT now())",
];

/// `placement.ensure_schema`: the refusals at birth (the Python body records its own; this
/// kernel reads them — and now stands the table too, so one migrator serves both kernels).
pub const PLACEMENT_DDL: &[&str] = &[
    "CREATE TABLE IF NOT EXISTS spine_refusals ( refusal_id bigserial PRIMARY KEY, did text NOT \
     NULL, name text NOT NULL, kind text NOT NULL, template_hash text NOT NULL, placement text \
     NOT NULL, ground text NOT NULL, reasons text NOT NULL, marker text, scope text NOT NULL, \
     refused_at timestamptz NOT NULL DEFAULT now())",
    // schema 2: the latest refusal per body, one world at a time
    "CREATE INDEX IF NOT EXISTS spine_refusals_scope_name ON spine_refusals (scope, name, refusal_id DESC)",
];

/// `tools.ensure_schema`: the tool journal — every hop a body made through its tool door
/// (the Python body's to write; the kernel's export reads it).
pub const TOOLS_DDL: &[&str] = &[
    "CREATE TABLE IF NOT EXISTS spine_tool_calls ( call_id bigserial PRIMARY KEY, did text NOT \
     NULL, tool text NOT NULL, args text NOT NULL, ok boolean NOT NULL, result text, at \
     timestamptz NOT NULL DEFAULT now())",
    "ALTER TABLE spine_tool_calls ADD COLUMN IF NOT EXISTS authority_chain text",
    "ALTER TABLE spine_tool_calls ADD COLUMN IF NOT EXISTS ask text",
    "ALTER TABLE spine_tool_calls ADD COLUMN IF NOT EXISTS service text",
    // schema 2: a body's hops by its self, newest first (the export, the tool lamps)
    "CREATE INDEX IF NOT EXISTS spine_tool_calls_did ON spine_tool_calls (did, call_id DESC)",
];

// ---- the rails' three and the tables their own modules once held (re-base sp1: every DDL lives
// here, PURE, so the migrator's contract — the version and the tables — is read without a rail) ----

/// The table its home module (`outbox`) once held — re-exported there.
pub const OUTBOX_DDL: &[&str] = &[
    "CREATE TABLE IF NOT EXISTS spine_outbox ( outbox_id bigserial PRIMARY KEY, message_id text \
     NOT NULL UNIQUE, body bytea NOT NULL, committed_at timestamptz NOT NULL DEFAULT now(), \
     published_at timestamptz, publish_attempts int NOT NULL DEFAULT 0)",
    "ALTER TABLE spine_outbox ADD COLUMN IF NOT EXISTS committed_at timestamptz NOT NULL DEFAULT \
     now()",
    "ALTER TABLE spine_outbox ADD COLUMN IF NOT EXISTS publish_attempts int NOT NULL DEFAULT 0",
    // schema 2: THE RELAY'S POLL — five times a second, `WHERE published_at IS NULL` — walks the
    // pending rows alone, never the whole table (found 2026-09-28: a 131k-row sequential scan per poll)
    "CREATE INDEX IF NOT EXISTS spine_outbox_pending ON spine_outbox (outbox_id) WHERE published_at IS NULL",
];

/// The table its home module (`inbox`) once held — re-exported there.
pub const INBOX_DDL: &[&str] = &[
    "CREATE TABLE IF NOT EXISTS spine_inbox ( consumer text NOT NULL, message_id text NOT NULL, \
     first_seen timestamptz NOT NULL DEFAULT now(), status text NOT NULL DEFAULT 'working', \
     attempts int NOT NULL DEFAULT 1, PRIMARY KEY (consumer, message_id))",
    "CREATE TABLE IF NOT EXISTS spine_aggregate_cursor ( consumer text NOT NULL, aggregate_id \
     text NOT NULL, last_sequence bigint NOT NULL DEFAULT 0, PRIMARY KEY (consumer, \
     aggregate_id))",
    // re-base sp1: THE PARKED — a poison event's evidence (the Python projector's table, word
    // for word) and the operator's word that let a consumer advance past it
    "CREATE TABLE IF NOT EXISTS spine_parked ( parked_id bigserial PRIMARY KEY, consumer text NOT \
     NULL, topic text, partition int, kafka_offset bigint, body bytea, reason text NOT NULL, \
     parked_at timestamptz NOT NULL DEFAULT now())",
    "ALTER TABLE spine_parked ADD COLUMN IF NOT EXISTS advanced_by text",
    "ALTER TABLE spine_parked ADD COLUMN IF NOT EXISTS advanced_at timestamptz",
];

/// The table its home module (`heartbeat`) once held — re-exported there.
pub const HEARTBEAT_DDL: &[&str] = &[
    "CREATE TABLE IF NOT EXISTS spine_heartbeat ( message_id text PRIMARY \
                            KEY, body bytea NOT NULL, committed_at timestamptz NOT NULL DEFAULT \
                            now())",
];

/// The table its home module (`store`) once held — re-exported there.
pub const STORE_DDL: &[&str] = &[
    "CREATE TABLE IF NOT EXISTS spine_memories ( memory_id bigserial PRIMARY KEY, namespace text NOT \
     NULL, key text NOT NULL, body text NOT NULL, hash text NOT NULL, by_did text NOT NULL, scope \
     text, landed_at timestamptz NOT NULL DEFAULT now(), valid_from timestamptz NOT NULL DEFAULT \
     now(), valid_to timestamptz, supersedes text, understanding text NOT NULL DEFAULT \
     'tsvector:english', tsv tsvector GENERATED ALWAYS AS (to_tsvector('english', body)) STORED)",
    "CREATE UNIQUE INDEX IF NOT EXISTS spine_memories_id ON spine_memories (memory_id)",
    "CREATE UNIQUE INDEX IF NOT EXISTS spine_memories_current ON spine_memories (namespace, key, \
     scope) WHERE valid_to IS NULL",
    "CREATE INDEX IF NOT EXISTS spine_memories_tsv ON spine_memories USING GIN (tsv)",
    // the column added only when missing: an ALTER takes an AccessExclusive lock even when it
    // has nothing to add, and a kernel booting beside another's inserts deadlocked on it
    // (found by the memory proof, 2026-09-24)
    "DO $$ BEGIN IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema = current_schema() AND table_name = \
     'spine_memories' AND column_name = 'state') THEN ALTER TABLE spine_memories ADD COLUMN state \
     text NOT NULL DEFAULT 'in'; END IF; END $$",
    "CREATE INDEX IF NOT EXISTS spine_memories_landed ON spine_memories (namespace, scope, landed_at)",
];

/// The table its home module (`cells_live`) once held — re-exported there.
pub const CELLS_DDL: &[&str] = &[
    "CREATE TABLE IF NOT EXISTS spine_world ( scope text PRIMARY KEY, cell text NOT NULL, epoch int NOT \
     NULL DEFAULT 1, kernel text NOT NULL, door text, opened_at timestamptz NOT NULL DEFAULT now(), \
     rehomed_at timestamptz, rehomed_by text)",
    "CREATE TABLE IF NOT EXISTS spine_peers ( cell text NOT NULL, scope text NOT NULL, door text NOT \
     NULL, did text, world text, epoch int, pinned_at timestamptz, last_seen timestamptz, cursor bigint \
     NOT NULL DEFAULT 0, unreachable_since timestamptz, PRIMARY KEY (cell, scope))",
    "CREATE TABLE IF NOT EXISTS spine_seam_nonces ( nonce text PRIMARY KEY, scope text NOT NULL, \
     seen_at timestamptz NOT NULL DEFAULT now())",
    // schema 3 (the honest glass sp2, W87): a peer LET GO — recorded on its row, never deleted; a
    // kernel relit naming the cell (SPINE_PEERS) names it again
    "ALTER TABLE spine_peers ADD COLUMN IF NOT EXISTS forgotten_by text",
    "ALTER TABLE spine_peers ADD COLUMN IF NOT EXISTS forgotten_at timestamptz",
];

/// The table its home module (`seam`) once held — re-exported there.
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

/// The table its home module (`profile_live`) once held — re-exported there.
pub const PROFILE_DDL: &[&str] = &[
    "CREATE TABLE IF NOT EXISTS spine_profile ( claim_id bigserial PRIMARY KEY, scope text NOT NULL, \
     person text NOT NULL, field text NOT NULL, value text NOT NULL, asserted_by text NOT NULL, state \
     text NOT NULL, quoted text, evidence text, lat double precision, lon double precision, zone text, \
     by_did text NOT NULL, marker text, ask text, at timestamptz NOT NULL DEFAULT now(), withdrawn_at \
     timestamptz, withdrawn_by text, withdrawn_marker text)",
    "CREATE INDEX IF NOT EXISTS spine_profile_person ON spine_profile (scope, person, at DESC)",
    "ALTER TABLE spine_asks ADD COLUMN IF NOT EXISTS carried_profile text",
];

/// The table its home module (`seat_live`) once held — re-exported there.
pub const SEAT_DDL: &[&str] = &[
    "CREATE TABLE IF NOT EXISTS spine_owner ( scope text PRIMARY KEY, person text NOT NULL, \
     declared_at timestamptz NOT NULL DEFAULT now())",
    "CREATE TABLE IF NOT EXISTS spine_seats ( seat_id text PRIMARY KEY, person text NOT NULL, scope \
     text NOT NULL, role text NOT NULL, expiry timestamptz NOT NULL, taken_at timestamptz NOT NULL \
     DEFAULT now(), left_at timestamptz, left_by text)",
];

/// The table its home module (`desk_live`) once held — re-exported there.
pub const DESK_DDL: &[&str] = &[
    "CREATE TABLE IF NOT EXISTS spine_desk ( join_id text PRIMARY KEY, scope text NOT NULL, did text NOT NULL, \
     name text NOT NULL, kind text NOT NULL, public_key text NOT NULL, template_hash text NOT NULL DEFAULT '', \
     policy_hash text NOT NULL DEFAULT '', status text NOT NULL, nonce text NOT NULL, nonce_at timestamptz NOT \
     NULL DEFAULT now(), ticket text, ask_id text, admitted_by text, lease_id text, lease text, expiry \
     timestamptz, asked_at timestamptz NOT NULL DEFAULT now(), updated_at timestamptz NOT NULL DEFAULT now())",
    "CREATE INDEX IF NOT EXISTS spine_desk_did ON spine_desk (scope, did)",
];

/// The tags and their DDL, in the order the road ensures them.
pub const ROAD: [(&str, &[&str]); 21] = [
    ("resident", RESIDENT_DDL),
    ("markers", MARKERS_DDL),
    ("proof", PROOF_DDL),
    ("intent", INTENT_DDL),
    ("presence", PRESENCE_DDL),
    ("digest", DIGEST_DDL),
    ("monitor", MONITOR_DDL),
    ("scheduler", SCHEDULER_DDL),
    ("harness", HARNESS_DDL),
    ("store", STORE_DDL),       // P7 sp5: the Record (spine_memories)
    ("services", SERVICES_DDL), // P7 sp6: the shelf, the Stable, the meter — the registry seam
    ("stable", STABLE_DDL),
    ("gateway", GATEWAY_DDL),
    ("cells", CELLS_DDL),     // P7 sp7: the world, its peers, the seam's nonces
    ("seam", SEAM_DDL),       // P7 sp7: the seam's outbound queue, the routed ask's columns
    ("profile", PROFILE_DDL), // P7 sp8: the human's own profile, the carried slice on the ask
    ("seat", SEAT_DDL),       // P7 sp8 row 3: the owner and the seats (the gate)
    ("desk", DESK_DDL),       // P7 sp8 row 3b: the machine join desk
    // re-base sp1: the tables the Python reference stood alone until the migrator — one
    // migrator, one set of tables, either kernel the writer
    ("mitl", MITL_DDL),
    ("placement", PLACEMENT_DDL),
    ("tools", TOOLS_DDL),
];

/// Every table the ask road stands on, once per ground per process.
#[cfg(feature = "rails")]
pub async fn ensure_road(g: &mut Ground) -> Result<(), RailError> {
    for (tag, ddl) in ROAD {
        g.ensure(tag, ddl).await?;
    }
    Ok(())
}

/// EVERY tag and its DDL this kernel stands on, in birth order — the rails' three, then
/// the road. The migrator runs them all inside one locked transaction; the version row
/// is the memo on the ground.
pub fn every_ddl() -> Vec<(&'static str, &'static [&'static str])> {
    let mut out: Vec<(&'static str, &'static [&'static str])> = vec![
        ("outbox", OUTBOX_DDL),
        ("inbox", INBOX_DDL),
        ("heartbeat", HEARTBEAT_DDL),
    ];
    out.extend(ROAD);
    out
}

static CREATE_TABLE_RE: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r"CREATE TABLE IF NOT EXISTS (\w+)").unwrap());

/// The table names a DDL list declares (the `CREATE TABLE IF NOT EXISTS` words).
pub fn tables_of(ddl: &[&str]) -> Vec<String> {
    ddl.iter()
        .filter_map(|stmt| CREATE_TABLE_RE.captures(stmt))
        .map(|c| c[1].to_string())
        .collect()
}

/// Every table this kernel's schema declares, sorted and unique — the version table
/// among them (fixture `schema_tables`; the verify step of the migrator).
pub fn tables() -> Vec<String> {
    let mut out = tables_of(SCHEMA_DDL);
    for (_, ddl) in every_ddl() {
        out.extend(tables_of(ddl));
    }
    out.sort();
    out.dedup();
    out
}

/// Does a table the Python spine owns stand on this ground?
#[cfg(feature = "rails")]
pub async fn has_table(g: &Ground, table: &str) -> Result<bool, RailError> {
    let row = g
        .client()
        .query_one("SELECT to_regclass($1) IS NOT NULL", &[&table])
        .await?;
    Ok(row.get(0))
}
