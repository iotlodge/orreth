# PROVENANCE: Claude Fable 5 (claude-fable-5) — rearch P2 sp2, the mind arrives · 2026-09-16
"""The OrrethStore v0 (canon 0003): LangGraph memory ergonomics, kernel
truth beneath.

`put` lands a memory as a content-hashed row on the ground WITH its
event in one transaction (the write path is the write path — memories
are not special). `get` is verbatim by key. `search` is v0-naive
(plain-text match) — the Understanding projection replaces its innards
in Phase 5 without changing this interface. A namespace here is a
label; enforcement stays at the door that owns the connection.
"""
from __future__ import annotations

from . import envelope as ev
from . import outbox

MEMORY_EVENT = "orreth.memory.landed.v1"


def ensure_schema(conn) -> None:
    from .outbox import once
    if not once(conn, "store"):
        return
    with conn.transaction():
        cur = conn.cursor()
        cur.execute("SELECT pg_advisory_xact_lock(742199)")  # DDL race guard
        cur.execute(
            "CREATE TABLE IF NOT EXISTS spine_memories ("
            " namespace text NOT NULL,"
            " key text NOT NULL,"
            " body text NOT NULL,"
            " hash text NOT NULL,"
            " by_did text NOT NULL,"
            " landed_at timestamptz NOT NULL DEFAULT now(),"
            " PRIMARY KEY (namespace, key))")
        cur.execute("ALTER TABLE spine_memories ADD COLUMN IF NOT EXISTS"
                    " scope text")          # a memory wears its world (0002)


class OrrethStore:
    """v0 of the seam: enough of the Store shape for the resident's
    recall node. The full LangGraph BaseStore adapter arrives when the
    template needs cross-thread memory tools; the ground truth beneath
    will not change."""

    def __init__(self, conn, *, by_did: str):
        self._conn = conn
        self.by_did = by_did
        ensure_schema(conn)
        outbox.ensure_schema(conn)

    def put(self, namespace: str, key: str, body: str) -> str:
        h = ev.content_hash(body)
        e = ev.make_envelope(
            kind="event", type=MEMORY_EVENT, universe_id=ev.scope(),
            scope_path=ev.scope(),
            payload={"ref": f"{namespace}/{key}", "hash": h},
            authority_chain=[self.by_did])
        with self._conn.transaction():
            cur = self._conn.cursor()
            cur.execute(
                "INSERT INTO spine_memories (namespace, key, body, hash,"
                " by_did, scope) VALUES (%s, %s, %s, %s, %s, %s)"
                " ON CONFLICT (namespace, key) DO UPDATE SET"
                " body = EXCLUDED.body, hash = EXCLUDED.hash,"
                " by_did = EXCLUDED.by_did, landed_at = now(),"
                " scope = EXCLUDED.scope",
                (namespace, key, body, h, self.by_did, ev.scope()))
            outbox.add_row(cur, ev.encode(e), e["message_id"])
        return h

    def get(self, namespace: str, key: str) -> str | None:
        cur = self._conn.cursor()
        cur.execute("SELECT body FROM spine_memories"
                    " WHERE namespace = %s AND key = %s AND scope = %s",
                    (namespace, key, ev.scope()))    # a memory is its world's
        row = cur.fetchone()
        return row[0] if row else None

    def search(self, namespace: str, query: str, limit: int = 5) -> list[dict]:
        """v0: word-match, newest first — any meaningful word of the ask
        can find a memory (a whole sentence never matches anything).
        Honest about what it is; meaning-shaped recall is Phase 5's
        projection behind this same call."""
        import re
        words = [w for w in re.findall(r"[A-Za-z0-9]+", query)
                 if len(w) >= 4][:6] or [query]
        conds = " OR ".join(["body ILIKE %s"] * len(words))
        cur = self._conn.cursor()
        cur.execute(
            f"SELECT key, body FROM spine_memories"
            f" WHERE namespace = %s AND scope = %s AND ({conds})"
            f" ORDER BY landed_at DESC LIMIT %s",
            (namespace, ev.scope(), *[f"%{w}%" for w in words], limit))
        return [{"key": k, "body": b} for k, b in cur.fetchall()]

    def within(self, namespace: str, from_iso: str, to_iso: str,
               limit: int = 6) -> list[dict]:
        """Recall by timeframe (MEM-1): every word landed between X and Y,
        oldest first — the window the human typed, honored by the store."""
        cur = self._conn.cursor()
        cur.execute(
            "SELECT key, body, landed_at FROM spine_memories WHERE namespace = %s"
            " AND scope = %s AND landed_at BETWEEN %s AND %s"
            " ORDER BY landed_at LIMIT %s",
            (namespace, ev.scope(), from_iso, to_iso, limit))
        return [{"key": k, "body": b, "landed_at": t.isoformat()}
                for k, b, t in cur.fetchall()]

    def recent(self, namespace: str, limit: int = 5) -> list[dict]:
        cur = self._conn.cursor()
        cur.execute(
            "SELECT key, body FROM spine_memories WHERE namespace = %s"
            " AND scope = %s ORDER BY landed_at DESC LIMIT %s",
            (namespace, ev.scope(), limit))
        return [{"key": k, "body": b} for k, b in cur.fetchall()]
