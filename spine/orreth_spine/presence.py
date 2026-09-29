# PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P4 sp4, presence leases (M2) · 2026-09-18
# Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch row 4, PANEL sp2: THE LEASE FACTS — `orreth.lease.lapsed.v1` · `orreth.lease.seated.v1` minted by the sweep, noted on the ground (`noted_alive`) · 2026-09-28
"""Presence leases (canon 0002 M2): a body is ALIVE while its lease is
fresh — it renews as it serves; a body that stops renewing goes DORMANT
in seconds and stays listed (the roster breathes; nothing is deleted).
Liveness is a fact on the ground, never an assumption of the glass."""
from __future__ import annotations

from . import envelope as ev

TTL_S = 15
# row 4, panel sp2: THE LEASE FACTS — a lease was polled state; now every line crossed is a fact
LEASE_LAPSED = "orreth.lease.lapsed.v1"       # alive → dormant: the body stopped renewing
LEASE_SEATED = "orreth.lease.seated.v1"       # dormant → alive: the body serves again (or first seated)
KERNEL = "the kernel"
SWEEP_S = 5                                   # the sweep's cadence — a third of the lease's life


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
        # panel sp2: what the sweep last noted of the lease's liveness — on the ground, so two
        # kernels never mint one lapse twice
        cur.execute("ALTER TABLE spine_leases ADD COLUMN IF NOT EXISTS noted_alive boolean")
        cur.execute("CREATE INDEX IF NOT EXISTS spine_leases_scope ON spine_leases (scope, name)")   # schema 2 (the perf cure)


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


def lease_payload(name: str, did: str, kind: str, until: str) -> dict:
    """The payload of a lease fact: the body by NAME (the feed's pointer — the
    panel's station), its self, its kind, the lease's edge as the ground holds it."""
    return {"ref": name, "hash": ev.content_hash(did), "did": did, "kind": kind, "until": until}


def lease_fact(type: str, name: str, did: str, kind: str, until: str, scope: str | None = None) -> dict:
    """A lease fact whole: the kernel's chain, the body's self as correlation, no
    aggregate, no marker (conformance `lease_fact`)."""
    sc = scope or ev.scope()
    return ev.make_envelope(kind="event", type=type, universe_id=sc, scope_path=sc,
                            payload=lease_payload(name, did, kind, until),
                            correlation_id=did, authority_chain=[KERNEL])


def sweep(conn) -> list[dict]:
    """THE SWEEP: every lease whose liveness differs from what the ground last NOTED
    is noted anew in one atomic update — the rows returned are the lines crossed, and
    each becomes its fact through the outbox. The note lives on the ground
    (`noted_alive`), never in the kernel: two kernels on one ground race for the row
    and one wins it. A lease never noted (the column born NULL on an old ground) is
    noted silently — its history was not watched, so no fact is invented."""
    from . import outbox
    ensure_schema(conn); outbox.ensure_schema(conn)
    cur = conn.cursor()
    cur.execute("UPDATE spine_leases SET noted_alive = (until > now())"
                " WHERE scope = %s AND noted_alive IS NULL", (ev.scope(),))
    cur.execute("UPDATE spine_leases SET noted_alive = (until > now())"
                " WHERE scope = %s AND noted_alive IS DISTINCT FROM (until > now())"
                " RETURNING did, name, kind, until, (until > now())", (ev.scope(),))
    minted = []
    for did, name, kind, until, alive in cur.fetchall():
        e = lease_fact(LEASE_SEATED if alive else LEASE_LAPSED, name, did, kind, until.isoformat())
        outbox.commit_with_outbox(conn, ev.encode(e), e["message_id"])
        minted.append(e)
    return minted
