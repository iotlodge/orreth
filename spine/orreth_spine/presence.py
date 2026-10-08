# PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P4 sp4, presence leases (M2) · 2026-09-18
# Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch row 4, PANEL sp2: THE LEASE FACTS — `orreth.lease.lapsed.v1` · `orreth.lease.seated.v1` minted by the sweep, noted on the ground (`noted_alive`) · 2026-09-28
# Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch row 4, the honest glass sp2 (W85): ONE NAME, ONE SELF — the roster folded one row per name, the earlier selves counted · 2026-09-29
# Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch Phase 8 sp1 THE PATH: a lease wears the body's level; the roster and the sweep see every level within the universe · 2026-10-05
# Amended: Claude Fable 5.1 (claude-fable-5-1) — THE GROUND CONNECTIONS CURE (2026-10-08): `RENEW_S` — a body renews on a cadence, not every pass; `seated_now` counts the bodies alive for the seat budget · 2026-10-08
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
RENEW_S = 5                                   # the cure (2026-10-08): a body renews every RENEW_S, never every pass — an idle body
                                              # opens a line for the renew and closes it; a serving body renews on its serve line


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


def renew(conn, did: str, name: str, kind: str, ttl_s: int = TTL_S, scope: str | None = None) -> None:
    """The body's own act, every serve: 'I am here until <now + ttl>' — the lease wears the
    body's own scope path (Phase 8 sp1: the level it is seated on)."""
    ensure_schema(conn)
    with conn.transaction():
        conn.cursor().execute(
            "INSERT INTO spine_leases (did, name, kind, scope, until)"
            " VALUES (%s, %s, %s, %s, now() + make_interval(secs => %s))"
            " ON CONFLICT (did) DO UPDATE SET until = EXCLUDED.until,"
            " renewed_at = now(), name = EXCLUDED.name, kind = EXCLUDED.kind",
            (did, name, kind, scope or ev.scope(), ttl_s))


def seated_now(conn, exclude_did: str | None = None) -> int:
    """The bodies ALIVE in this universe right now — the selves whose lease is fresh — less
    one self when asked (a body re-joining as its next life never counts itself). The seat
    budget's denominator (the cure, 2026-10-08)."""
    ensure_schema(conn)
    cur = conn.cursor()
    cur.execute(f"SELECT count(*) FROM spine_leases WHERE {ev.WITHIN} AND until > now() AND did <> %s",
                (*ev.within_params(ev.universe()), exclude_did or ""))
    return int(cur.fetchone()[0])


def roster(conn) -> list[dict]:
    """Every NAME that ever held a lease in this world, ONE row each — the self
    serving under it now (a living lease first, else the latest), alive or
    dormant, with the EARLIER SELVES counted (the honest glass sp2, W85: JB's
    BODIES card drew every body twice — a box's first crew of ten fresh selves
    beside the host's, keyed on the keypair; a name is what the person reads, a
    self is what the ground keys, and the card folds to the name). Nothing is
    deleted: the earlier selves stay on the ground, counted, never drawn as
    a second body."""
    ensure_schema(conn)
    cur = conn.cursor()
    cur.execute(
        "SELECT DISTINCT ON (name) did, name, kind, until, renewed_at, until > now(),"
        " (count(*) OVER (PARTITION BY name))::int - 1, scope FROM spine_leases"
        f" WHERE {ev.WITHIN} ORDER BY name, (until > now()) DESC, until DESC", ev.within_params(ev.universe()))
    return [{"did": r[0], "name": r[1], "kind": r[2], "until": r[3].isoformat(),
             "renewed_at": r[4].isoformat(), "alive": bool(r[5]), "earlier_selves": int(r[6]), "scope": r[7]}
            for r in cur.fetchall()]


def lease_payload(name: str, did: str, kind: str, until: str) -> dict:
    """The payload of a lease fact: the body by NAME (the feed's pointer — the
    panel's station), its self, its kind, the lease's edge as the ground holds it."""
    return {"ref": name, "hash": ev.content_hash(did), "did": did, "kind": kind, "until": until}


def lease_fact(type: str, name: str, did: str, kind: str, until: str, scope: str | None = None) -> dict:
    """A lease fact whole: the kernel's chain, the body's self as correlation, no
    aggregate, no marker (conformance `lease_fact`)."""
    sc = scope or ev.scope()
    return ev.make_envelope(kind="event", type=type, universe_id=sc.split("/", 1)[0], scope_path=sc,
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
                f" WHERE {ev.WITHIN} AND noted_alive IS NULL", ev.within_params(ev.universe()))
    cur.execute("UPDATE spine_leases SET noted_alive = (until > now())"
                f" WHERE {ev.WITHIN} AND noted_alive IS DISTINCT FROM (until > now())"
                " RETURNING did, name, kind, until, (until > now()), scope", ev.within_params(ev.universe()))
    minted = []
    for did, name, kind, until, alive, sc in cur.fetchall():
        e = lease_fact(LEASE_SEATED if alive else LEASE_LAPSED, name, did, kind, until.isoformat(), scope=sc)
        outbox.commit_with_outbox(conn, ev.encode(e), e["message_id"])
        minted.append(e)
    return minted
