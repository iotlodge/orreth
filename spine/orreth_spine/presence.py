# PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P4 sp4, presence leases (M2) · 2026-09-18
"""Presence leases (canon 0002 M2): a body is ALIVE while its lease is
fresh — it renews as it serves; a body that stops renewing goes DORMANT
in seconds and stays listed (the roster breathes; nothing is deleted).
Liveness is a fact on the ground, never an assumption of the glass."""
from __future__ import annotations

from . import envelope as ev

TTL_S = 15


def ensure_schema(conn) -> None:
    from .outbox import once
    if not once(conn, "presence"):
        return
    with conn.transaction():
        cur = conn.cursor()
        cur.execute("SELECT pg_advisory_xact_lock(742199)")  # DDL race guard
        cur.execute(
            "CREATE TABLE IF NOT EXISTS spine_leases ("
            " did text PRIMARY KEY, name text NOT NULL, kind text NOT NULL,"
            " scope text NOT NULL, until timestamptz NOT NULL,"
            " renewed_at timestamptz NOT NULL DEFAULT now())")


def renew(conn, did: str, name: str, kind: str, ttl_s: int = TTL_S) -> None:
    """The body's own act, every serve: 'I am here until <now + ttl>'."""
    ensure_schema(conn)
    with conn.transaction():
        conn.cursor().execute(
            "INSERT INTO spine_leases (did, name, kind, scope, until)"
            " VALUES (%s, %s, %s, %s, now() + make_interval(secs => %s))"
            " ON CONFLICT (did) DO UPDATE SET until = EXCLUDED.until,"
            " renewed_at = now(), name = EXCLUDED.name, kind = EXCLUDED.kind",
            (did, name, kind, ev.scope(), ttl_s))


def roster(conn) -> list[dict]:
    """Every body that ever held a lease in this world, alive or dormant."""
    ensure_schema(conn)
    cur = conn.cursor()
    cur.execute(
        "SELECT did, name, kind, until, renewed_at, until > now() FROM spine_leases"
        " WHERE scope = %s ORDER BY name", (ev.scope(),))
    return [{"did": r[0], "name": r[1], "kind": r[2], "until": r[3].isoformat(),
             "renewed_at": r[4].isoformat(), "alive": bool(r[5])}
            for r in cur.fetchall()]
