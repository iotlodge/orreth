# PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch intent sp1, the ground at birth · 2026-09-19
# Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P6 sp4, placement policy v0 · 2026-09-21
# Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P6.5 sp1, the services ground · 2026-09-22
# Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp4, the beat lock (the loops' shadow law) · 2026-09-23
# Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp8, the human profile's ground · 2026-09-26
# Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch row 4, re-base sp1: THE MIGRATOR (lock 2) — the single writer, the version on the ground, the later kernel waits and verifies · 2026-09-28
"""Every ground, ensured when a connection is BORN — never inside a serve.

The law (found live at the intent sp1 relight): `outbox.once` keeps a
connection from re-entering DDL, but the FIRST entry happens wherever the
first call lands — and when that is inside a serving transaction (a
resident reading its ask's marker), the DDL's locks live as long as the
serve. A new column on `spine_markers` took an AccessExclusiveLock inside
one serve's savepoint; that serve then waited on the graph, and every
loop and door of the Bridge queued behind a backend "idle in transaction"
for five minutes. So: a rig connection ensures EVERY ground the moment it
is opened, on its own autocommit statements, and no serve ever runs DDL.
Sharpened 2026-09-21 (CI, three runs: two fan-out asks deadlocked a serving
resident at the advisory lock): `outbox.once` keeps a PROCESS memo per
ground (DSN + search_path), so a door's fresh connection to an ensured
ground is born flagged and runs no DDL at all — flagged only once a birth has
FINISHED (the same day, CI: a thread born mid-birth skipped DDL, its seed hit an
undefined table, and the relay died; no resident ever replied).

THE BEAT LOCK (P7 sp4 — the loops' shadow law): two kernels stand on one
ground in SHADOW (the Python Bridge on :4600, the Rust bridge on :4601),
and each runs the standing loops — the scheduler's tick, the intent
rail's turn. A beat reads what is due and acts on it; two beats at once
would file the same occurrence twice, observe the same red twice, plan
the same cause twice. So a beat is CLAIMED before it runs: a session
advisory lock on the ground keyed by the beat's class and this world's
scope (`pg_try_advisory_lock(class, hashtext(scope))`) — held for the
beat, released after; the other kernel's beat finds it held and steps
back, saying so. The lock is Postgres's own: a kernel that dies mid-beat
drops it with its connection. One ground, one beat at a time, per world.

THE MIGRATOR (re-base sp1 — lock 2, "the single-writer schema migrator"):
the memo above is per PROCESS; the ground itself now remembers, in
`spine_schema`, which VERSION of the schema it holds. A birth takes the DDL
lock, creates the version table if it is missing, reads the highest version
recorded, and then does ONE of two things: below this kernel's
SCHEMA_VERSION it runs every module's DDL (all IF NOT EXISTS — an old ground
is grown, a fresh one is born) and records the version; at or past it, it
runs NO DDL and VERIFIES that every table it declares stands, refusing to
light on a ground whose version lies. Two kernels lighting together on a
fresh ground: the second waits at the lock while the first migrates, then
verifies — one writer, ever. Both kernels carry the same number and the same
TABLES (fixture `schema-v0.json` pins both); a change to any DDL statement
bumps the number in BOTH kernels in the same change.
"""
from __future__ import annotations

from contextlib import contextmanager

from . import envelope as ev

BEAT_LOCK = 742200                  # the beat classes count up from here (the DDL guard is 742199)
BEATS = {"scheduler": 1, "intent": 2, "keeper": 3}
HELD = "the beat is held by another kernel on this ground"


def beat_key(name: str) -> int:
    """The advisory lock's first key for a beat class (conformance `beat_lock`)."""
    return BEAT_LOCK + BEATS[name]


def try_beat(conn, name: str) -> bool:
    """Claim this world's beat of a class — True when it is ours to run."""
    cur = conn.cursor()
    cur.execute("SELECT pg_try_advisory_lock(%s::int, hashtext(%s))", (beat_key(name), ev.scope()))
    return bool(cur.fetchone()[0])


def end_beat(conn, name: str) -> None:
    conn.cursor().execute("SELECT pg_advisory_unlock(%s::int, hashtext(%s))",
                          (beat_key(name), ev.scope()))


@contextmanager
def beat(conn, name: str):
    """`with beat(conn, "intent") as ours:` — the beat runs only when ours;
    the lock is released however the beat ends."""
    ours = try_beat(conn, name)
    try:
        yield ours
    finally:
        if ours:
            end_beat(conn, name)

TAGS = ("outbox", "inbox", "heartbeat", "projector", "resident", "gateway", "tools", "store",
        "markers", "monitor", "scheduler", "harness", "presence", "digest", "intent",
        "proof", "mitl", "placement", "services", "stable", "cells", "profile", "seat", "desk")
# re-base sp1: `heartbeat` (the rig's breath stood its table unguarded before), `stable` (its
# tag was orphaned — the Stable's tables were born inside a request, the very thing the law
# forbids) and `desk` (the machine join desk, the Rust kernel's table) join the one list.

SCHEMA_VERSION = 1          # THE MIGRATOR: bumped in BOTH kernels whenever any DDL statement changes
TABLES = (                  # every table both kernels stand on at this version (fixture `schema_tables`)
    "spine_aggregate_cursor", "spine_asks", "spine_authenticators", "spine_desk", "spine_digests",
    "spine_harness_runs", "spine_heartbeat", "spine_inbox", "spine_intent_turns", "spine_intentions",
    "spine_joins", "spine_leases", "spine_marker_kinds", "spine_markers", "spine_masters", "spine_memories",
    "spine_meter", "spine_mind_assignments", "spine_mind_keys", "spine_mitl", "spine_occurrences",
    "spine_outbox", "spine_owner", "spine_parked", "spine_peers", "spine_profile", "spine_proof_attempts",
    "spine_refusals", "spine_schedules", "spine_schema", "spine_seam_nonces", "spine_seam_out", "spine_seats",
    "spine_service_health", "spine_service_versions", "spine_services", "spine_sessions", "spine_tool_calls",
    "spine_watches", "spine_world",
)
SCHEMA_DDL = ("CREATE TABLE IF NOT EXISTS spine_schema ( version int PRIMARY KEY, kernel text NOT NULL,"
              " migrated_at timestamptz NOT NULL DEFAULT now())")
SCHEMA: dict = {"ground": None, "kernel": SCHEMA_VERSION, "found": None, "migrated": None}   # this process's last birth


class GroundRefused(RuntimeError):
    """The ground's version lies (a declared table is missing) — not stood on."""


def _modules():
    from . import (cells, desk, digest, gateway, harness, heartbeat, inbox, intent, markers, mitl, monitor,
                   outbox, placement, presence, profile, projector, proof, resident, scheduler, seat, services,
                   stable, store, tools)
    return (outbox, inbox, heartbeat, projector, resident, gateway, tools, store, markers,
            monitor, scheduler, harness, presence, digest, intent, proof, mitl, placement, cells,
            services, stable, profile, seat, desk)


def migrate(conn) -> dict:
    """THE MIGRATOR: one locked transaction; the version read; below this kernel's
    version every module's DDL runs and the version is recorded (the single
    writer); at or past it nothing runs and every declared table is verified.
    Returns what the birth found and did — `{"found", "ground", "kernel", "migrated"}`."""
    from . import outbox
    with conn.transaction():
        cur = conn.cursor()
        cur.execute("SELECT pg_advisory_xact_lock(742199)")     # a kernel lighting beside a migrating one WAITS here
        cur.execute(SCHEMA_DDL)
        cur.execute("SELECT coalesce(max(version), 0) FROM spine_schema")
        found = int(cur.fetchone()[0])
        migrated = found < SCHEMA_VERSION
        if migrated:
            for mod in _modules():             # each module's `once` + its DDL (a savepoint; the lock re-entered)
                mod.ensure_schema(conn)
            cur.execute("INSERT INTO spine_schema (version, kernel) VALUES (%s, 'reference')",
                        (SCHEMA_VERSION,))
        else:
            for table in TABLES:
                cur.execute("SELECT to_regclass(%s) IS NOT NULL", (table,))
                if not cur.fetchone()[0]:
                    raise GroundRefused(
                        f"the ground says its schema is version {found} but the table {table} is missing"
                        " — a ground that lies is not stood on (drop the spine_schema row to let a kernel"
                        " migrate it again, or restore the table)")
            for tag in TAGS:                   # flagged on this connection, no DDL run
                outbox.once(conn, tag)
    out = {"found": found, "ground": max(found, SCHEMA_VERSION), "kernel": SCHEMA_VERSION, "migrated": migrated}
    SCHEMA.update(out)
    return out


def words(m: dict) -> str:
    """Plain words for the log at light."""
    if m["migrated"]:
        return f"the ground's schema migrated {m['found']} → {m['ground']} by this kernel"
    if m["ground"] > m["kernel"]:
        return (f"the ground's schema is {m['ground']} — newer than this kernel's {m['kernel']}"
                " — verified, nothing run")
    return f"the ground's schema verified at {m['ground']} — nothing run"


def ensure_all(conn) -> dict:
    """Every ground on this connection at BIRTH, through the migrator (each
    module's `once` tag flagged either way), so the serving transaction never
    runs DDL and never takes the lock; then the world's seeds."""
    from . import markers, outbox, proof
    out = migrate(conn)
    markers.seed(conn)                      # the kernel's kinds, in this world
    outbox.mark_ground_done(conn, TAGS)     # the birth FINISHED: later connections are born flagged
    proof.seed_masters(conn)                # the SPINE_MASTERS dial, in this world (P6 sp1)
    return out


def ensured(conn) -> set[str]:
    """The tags this connection has flagged — the law's evidence."""
    return set(getattr(conn, "_spine_ensured", None) or ())
