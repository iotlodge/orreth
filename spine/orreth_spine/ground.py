# PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch intent sp1, the ground at birth · 2026-09-19
# Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P6 sp4, placement policy v0 · 2026-09-21
# Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P6.5 sp1, the services ground · 2026-09-22
# Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp4, the beat lock (the loops' shadow law) · 2026-09-23
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

TAGS = ("outbox", "inbox", "projector", "resident", "gateway", "tools", "store",
        "markers", "monitor", "scheduler", "harness", "presence", "digest", "intent",
        "proof", "mitl", "placement", "services")


def ensure_all(conn) -> None:
    """Flag every ground on this connection (each module's `once` tag), so
    the serving transaction never runs DDL and never takes the lock."""
    from . import (digest, gateway, harness, inbox, intent, markers, mitl, monitor, outbox,
                   placement, presence, projector, proof, resident, scheduler, services, store, tools)
    for mod in (outbox, inbox, projector, resident, gateway, tools, store, markers,
                monitor, scheduler, harness, presence, digest, intent, proof, mitl, placement,
                services):
        mod.ensure_schema(conn)
    markers.seed(conn)                      # the kernel's kinds, in this world
    outbox.mark_ground_done(conn, TAGS)     # the birth FINISHED: later connections are born flagged
    proof.seed_masters(conn)                # the SPINE_MASTERS dial, in this world (P6 sp1)


def ensured(conn) -> set[str]:
    """The tags this connection has flagged — the law's evidence."""
    return set(getattr(conn, "_spine_ensured", None) or ())
