# PROVENANCE: Claude Fable 5 (claude-fable-5) — rearch P1 sp1, the durability boundary (M1) · 2026-09-16
"""The transactional outbox and its relay (canon 0002, law 2).

Domain state and the intent to publish commit in ONE Postgres
transaction: a committed row can never lack its event, a rolled-back row
can never emit one, and the human-visible success depends only on the
commit — never on a broker. The relay publishes after the fact,
at-least-once: a crash between publish and mark simply publishes again,
and the stable message id makes the duplicate harmless downstream.

Backpressure is explicit: when the unpublished backlog reaches the
declared budget, new writes refuse BY NAME instead of silently growing
(canon 0002: bounded outbox budget, honest refusal).
"""
from __future__ import annotations

import threading
import time

# The ground memo (canon 0008's ground law, sharpened 2026-09-21): DDL runs
# once per GROUND per process — never per connection. A door opens a fresh
# connection for every request; with a per-connection guard alone, every
# request re-ran the schema DDL (ALTER TABLE … ADD COLUMN IF NOT EXISTS takes
# an AccessExclusiveLock even when the column exists) inside a transaction
# holding the advisory lock, and two concurrent asks deadlocked against a
# serving resident (CI, three runs in a row: DeadlockDetected at the lock).
# A ground is the DSN plus the connection's search_path (PG ≥ 14 reports it):
# the test schema and the public one stay two grounds (markers.seed's lesson).
_GROUNDS: dict[str, set[str]] = {}
_GROUNDS_LOCK = threading.Lock()


def ground_key(conn) -> str:
    """The ground a connection stands on: its DSN and its search_path. The
    server does not report search_path (probed: parameter_status is None
    after SET), so it is asked ONCE per connection — safely in every
    transaction state: autocommit or already inside a transaction, a bare
    SHOW; idle without autocommit, SHOW then rollback so no implicit
    transaction lingers (the conftest lesson); in error or mid-statement,
    no query — the key falls back to this connection alone, so DDL is
    never wrongly skipped."""
    key = getattr(conn, "_spine_ground", None)
    if key is None:
        path = None
        try:
            status = int(conn.info.transaction_status)     # 0 idle · 2 in a transaction
            if conn.autocommit or status == 2:
                path = conn.execute("SHOW search_path").fetchone()[0]
            elif status == 0:
                path = conn.execute("SHOW search_path").fetchone()[0]
                conn.rollback()
        except Exception:
            path = None
        dsn = getattr(getattr(conn, "info", None), "dsn", "?")
        key = f"{dsn}|{path}" if path is not None else f"{dsn}|conn:{id(conn)}"
        conn._spine_ground = key
    return key


def once(conn, tag: str) -> bool:
    """True the first time this PROCESS sees `tag` on this connection's
    ground — ensure_schema runs its DDL (and takes the advisory lock)
    exactly once per ground, so a long serving transaction never re-enters
    DDL and never drags the lock with it (found live: one thinking resident
    held the xact-scoped lock and every door queued behind it), and a
    connection born after the ground was ensured is born flagged: a door's
    fresh connection never runs DDL inside a request (found in CI: two
    fan-out asks deadlocked a serving resident at the advisory lock)."""
    done = getattr(conn, "_spine_ensured", None)
    if done is None:
        done = set()
        conn._spine_ensured = done
    if tag in done:
        return False
    done.add(tag)
    with _GROUNDS_LOCK:
        tags = _GROUNDS.setdefault(ground_key(conn), set())
        if tag in tags:
            return False                       # born flagged: this ground is ensured
        tags.add(tag)
    return True


class OutboxBudgetExceeded(RuntimeError):
    """The unpublished backlog reached its declared budget — the write is
    refused honestly rather than the backlog growing without bound."""


def ensure_schema(conn) -> None:
    if not once(conn, "outbox"):
        return
    with conn.transaction():
        cur = conn.cursor()
        cur.execute("SELECT pg_advisory_xact_lock(742199)")  # DDL race guard
        cur.execute(
            "CREATE TABLE IF NOT EXISTS spine_outbox ("
            " outbox_id bigserial PRIMARY KEY,"
            " message_id text NOT NULL UNIQUE,"
            " body bytea NOT NULL,"
            " committed_at timestamptz NOT NULL DEFAULT now(),"
            " published_at timestamptz,"
            " publish_attempts int NOT NULL DEFAULT 0)")
        # the heartbeat's earlier, poorer table grows the missing columns
        cur.execute("ALTER TABLE spine_outbox ADD COLUMN IF NOT EXISTS"
                    " committed_at timestamptz NOT NULL DEFAULT now()")
        cur.execute("ALTER TABLE spine_outbox ADD COLUMN IF NOT EXISTS"
                    " publish_attempts int NOT NULL DEFAULT 0")


def commit_with_outbox(conn, raw: bytes, message_id: str,
                       domain=None, *, budget: int | None = None) -> None:
    """One transaction: the caller's domain writes (`domain(cur)`) plus the
    outbox row. Any failure inside rolls back BOTH — there is no state
    without its event and no event without its state."""
    with conn.transaction():
        cur = conn.cursor()
        if budget is not None:
            cur.execute("SELECT count(*) FROM spine_outbox"
                        " WHERE published_at IS NULL")
            pending = cur.fetchone()[0]
            if pending >= budget:
                raise OutboxBudgetExceeded(
                    f"the outbox holds {pending} unpublished rows — the "
                    f"declared budget is {budget}; publish (or raise the "
                    f"budget) before writing more")
        if domain is not None:
            domain(cur)
        cur.execute("INSERT INTO spine_outbox (message_id, body)"
                    " VALUES (%s, %s)", (message_id, raw))


def add_row(cur, raw: bytes, message_id: str) -> None:
    """Add an outbox row INSIDE a transaction someone else owns — for
    effects that must land state + events atomically (the inbox's
    apply-once effects use this; commit_with_outbox opens its own
    transaction and cannot nest)."""
    cur.execute("INSERT INTO spine_outbox (message_id, body) VALUES (%s, %s)",
                (message_id, raw))


def outbox_lag(conn) -> dict:
    """The honest meter: how many rows await publish, and how old the
    oldest one is (now - committed_at) in seconds."""
    cur = conn.cursor()
    cur.execute("SELECT count(*),"
                " extract(epoch FROM (now() - min(committed_at)))"
                " FROM spine_outbox WHERE published_at IS NULL")
    n, age = cur.fetchone()
    return {"pending": n, "oldest_age_s": float(age) if age is not None else None}


class MemorySink:
    """The test sink: remembers every publish; can be told to fail before
    accepting (broker down) or after accepting (crash before mark) —
    the fault schedule's two relay deaths, deterministic."""

    def __init__(self, fail_before: int = 0, fail_after: int = 0):
        self.published: list[tuple[str, bytes]] = []
        self._fail_before = fail_before
        self._fail_after = fail_after

    def publish(self, message_id: str, body: bytes) -> None:
        if self._fail_before > 0:
            self._fail_before -= 1
            raise ConnectionError("sink refused before accepting (injected)")
        self.published.append((message_id, body))
        if self._fail_after > 0:
            self._fail_after -= 1
            raise ConnectionError("sink crashed after accepting (injected)")


def relay_once(conn, sink, batch: int = 100) -> dict:
    """Claim unpublished rows oldest-first and publish each. A publish
    failure records the attempt and stops the batch (the broker is likely
    down); the row stays unpublished and will be retried — at-least-once,
    never at-most-once."""
    cur = conn.cursor()
    cur.execute("SELECT outbox_id, message_id, body FROM spine_outbox"
                " WHERE published_at IS NULL ORDER BY outbox_id"
                " LIMIT %s FOR UPDATE SKIP LOCKED", (batch,))
    rows = cur.fetchall()
    conn.commit()
    published = attempts = 0
    for outbox_id, message_id, body in rows:
        attempts += 1
        try:
            sink.publish(message_id, bytes(body))
        except Exception:
            with conn.transaction():
                conn.cursor().execute(
                    "UPDATE spine_outbox SET publish_attempts ="
                    " publish_attempts + 1 WHERE outbox_id = %s", (outbox_id,))
            break
        with conn.transaction():
            conn.cursor().execute(
                "UPDATE spine_outbox SET published_at = now(),"
                " publish_attempts = publish_attempts + 1"
                " WHERE outbox_id = %s", (outbox_id,))
        published += 1
    return {"published": published, "attempts": attempts,
            "remaining": len(rows) - published}


def drain(conn, sink, deadline_s: float = 10.0) -> int:
    """Relay until nothing is pending or the deadline passes; returns how
    many were published. A convenience for tests and dev, not a service."""
    total = 0
    end = time.monotonic() + deadline_s
    while time.monotonic() < end:
        out = relay_once(conn, sink)
        total += out["published"]
        if out["remaining"] == 0 and outbox_lag(conn)["pending"] == 0:
            break
    return total
