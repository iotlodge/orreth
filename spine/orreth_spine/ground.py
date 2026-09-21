# PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch intent sp1, the ground at birth · 2026-09-19
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
"""
from __future__ import annotations

TAGS = ("outbox", "inbox", "projector", "resident", "gateway", "tools", "store",
        "markers", "monitor", "scheduler", "harness", "presence", "digest", "intent",
        "proof", "mitl")


def ensure_all(conn) -> None:
    """Flag every ground on this connection (each module's `once` tag), so
    the serving transaction never runs DDL and never takes the lock."""
    from . import (digest, gateway, harness, inbox, intent, markers, mitl, monitor, outbox,
                   presence, projector, proof, resident, scheduler, store, tools)
    for mod in (outbox, inbox, projector, resident, gateway, tools, store, markers,
                monitor, scheduler, harness, presence, digest, intent, proof, mitl):
        mod.ensure_schema(conn)
    markers.seed(conn)                      # the kernel's kinds, in this world
    outbox.mark_ground_done(conn, TAGS)     # the birth FINISHED: later connections are born flagged
    proof.seed_masters(conn)                # the SPINE_MASTERS dial, in this world (P6 sp1)


def ensured(conn) -> set[str]:
    """The tags this connection has flagged — the law's evidence."""
    return set(getattr(conn, "_spine_ensured", None) or ())
