# PROVENANCE: Claude Fable 5 (claude-fable-5) — rearch P1 sp1, the durability boundary (M1) · 2026-09-16
"""The durable inbox (canon 0002, laws 3 and 4).

Delivery is at-least-once; EFFECTS are once. Every side-effecting
consumer records the message id it acted on in the same transaction as
the effect, so a redelivered message finds its own footprint and steps
around it. Aggregate ordering is enforced per aggregate, never globally:
an older sequence is recorded and skipped, the next sequence applies,
and a GAP refuses to guess — the caller fetches what's missing instead
of applying history out of order.
"""
from __future__ import annotations


class GapDetected(Exception):
    """A sequence arrived from the future: expected `expected`, got `got`
    for `aggregate_id`. The consumer must recover the missing events —
    applying out of order would let an older truth overwrite a newer one."""

    def __init__(self, aggregate_id: str, expected: int, got: int):
        self.aggregate_id, self.expected, self.got = aggregate_id, expected, got
        super().__init__(
            f"gap on {aggregate_id}: expected sequence {expected}, got {got}"
            " — fetch the missing events; never guess")


def ensure_schema(conn) -> None:
    from .outbox import once
    if not once(conn, "inbox"):
        return
    with conn.transaction():
        cur = conn.cursor()
        cur.execute("SELECT pg_advisory_xact_lock(742199)")  # DDL race guard
        cur.execute(
            "CREATE TABLE IF NOT EXISTS spine_inbox ("
            " consumer text NOT NULL,"
            " message_id text NOT NULL,"
            " first_seen timestamptz NOT NULL DEFAULT now(),"
            " status text NOT NULL DEFAULT 'working',"
            " attempts int NOT NULL DEFAULT 1,"
            " PRIMARY KEY (consumer, message_id))")
        cur.execute(
            "CREATE TABLE IF NOT EXISTS spine_aggregate_cursor ("
            " consumer text NOT NULL,"
            " aggregate_id text NOT NULL,"
            " last_sequence bigint NOT NULL DEFAULT 0,"
            " PRIMARY KEY (consumer, aggregate_id))")


def apply_once(conn, consumer: str, message_id: str, effect) -> str:
    """Run `effect(cur)` exactly once per (consumer, message id). The
    inbox footprint and the effect share one transaction: if the effect
    fails, the footprint rolls back too and a redelivery retries clean.
    Returns "applied" or "duplicate"."""
    with conn.transaction():
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO spine_inbox (consumer, message_id)"
            " VALUES (%s, %s) ON CONFLICT (consumer, message_id) DO NOTHING"
            " RETURNING message_id", (consumer, message_id))
        if cur.fetchone() is None:
            cur.execute(
                "UPDATE spine_inbox SET attempts = attempts + 1"
                " WHERE consumer = %s AND message_id = %s",
                (consumer, message_id))
            return "duplicate"
        effect(cur)
        cur.execute(
            "UPDATE spine_inbox SET status = 'done'"
            " WHERE consumer = %s AND message_id = %s", (consumer, message_id))
    return "applied"


def apply_event(conn, consumer: str, env: dict, effect) -> str:
    """apply_once plus the ordering law for envelopes wearing an
    aggregate {id, sequence}: stale sequences are recorded and skipped,
    the next sequence applies and advances the cursor, and a gap raises
    GapDetected inside a rolled-back transaction. Returns "applied",
    "duplicate", or "stale"."""
    agg = env.get("aggregate") or {}
    aid = str(agg.get("id") or "")
    seq = int(agg.get("sequence") or 0)
    if not aid or seq <= 0:
        return apply_once(conn, consumer, env["message_id"], effect)
    with conn.transaction():
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO spine_aggregate_cursor (consumer, aggregate_id)"
            " VALUES (%s, %s) ON CONFLICT DO NOTHING", (consumer, aid))
        cur.execute(
            "SELECT last_sequence FROM spine_aggregate_cursor"
            " WHERE consumer = %s AND aggregate_id = %s FOR UPDATE",
            (consumer, aid))
        last = cur.fetchone()[0]
        if seq <= last:
            cur.execute(
                "INSERT INTO spine_inbox (consumer, message_id, status)"
                " VALUES (%s, %s, 'stale')"
                " ON CONFLICT (consumer, message_id)"
                " DO UPDATE SET attempts = spine_inbox.attempts + 1",
                (consumer, env["message_id"]))
            return "stale"
        if seq > last + 1:
            raise GapDetected(aid, last + 1, seq)
        cur.execute(
            "INSERT INTO spine_inbox (consumer, message_id)"
            " VALUES (%s, %s) ON CONFLICT (consumer, message_id) DO NOTHING"
            " RETURNING message_id", (consumer, env["message_id"]))
        if cur.fetchone() is None:
            cur.execute(
                "UPDATE spine_inbox SET attempts = attempts + 1"
                " WHERE consumer = %s AND message_id = %s",
                (consumer, env["message_id"]))
            return "duplicate"
        effect(cur)
        cur.execute(
            "UPDATE spine_aggregate_cursor SET last_sequence = %s"
            " WHERE consumer = %s AND aggregate_id = %s", (seq, consumer, aid))
        cur.execute(
            "UPDATE spine_inbox SET status = 'done'"
            " WHERE consumer = %s AND message_id = %s",
            (consumer, env["message_id"]))
    return "applied"


def duplicates_seen(conn, consumer: str) -> int:
    """The honest duplicate meter: redeliveries absorbed without effect."""
    cur = conn.cursor()
    cur.execute(
        "SELECT coalesce(sum(attempts - 1), 0) FROM spine_inbox"
        " WHERE consumer = %s", (consumer,))
    return int(cur.fetchone()[0])
