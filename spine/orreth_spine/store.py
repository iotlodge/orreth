# PROVENANCE: Claude Fable 5 (claude-fable-5) — rearch P2 sp2, the mind arrives · 2026-09-16
# Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P5 sp2, Understanding v0 (lineage · validity · a ranked projection) · 2026-09-19
# Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp5, memory and the export: the pure laws factored for the fixture; the kernel's own self signs the export · 2026-09-24
"""The OrrethStore (canon 0003): LangGraph memory ergonomics, kernel truth
beneath.

`put` lands a memory as a content-hashed row on the ground WITH its event
in one transaction — and NEVER overwrites: a new memory under the same key
is a SIBLING that supersedes the old one (lineage), each with a validity
interval, so "what is true now" and "what was true then" both answer
(MEM-4). `get` is verbatim by key — current, or as of a moment. `search`
rides the Understanding projection v0: Postgres full-text (stemmed,
ranked) — honestly lexical until an embedding lane exists; the projection
wears its kind on the row ("tsvector:english"), is derived from the body,
and is rebuildable. A memory wears its world. A namespace is a label;
enforcement stays at the door that owns the connection.
"""
from __future__ import annotations

from . import envelope as ev
import re

from . import outbox

MEMORY_EVENT = "orreth.memory.landed.v1"
PURGE_EVENT = "orreth.memory.purged.v1"     # the tombstone: hashes, never words
UNDERSTANDING = "tsvector:english"      # the projection's kind, worn by every row

_VALID_NOW = "valid_to IS NULL"
_WORD = re.compile(r"[A-Za-z0-9]+")


def search_terms(query: str) -> str:
    """The recall query in the projection's grammar (fixture `search_terms`):
    OR-shaped — any word of the ask may find a memory, and the memory
    holding MORE of them ranks first (websearch ANDs by default); a query
    with no word passes through whole."""
    return " or ".join(_WORD.findall(query)) or query


def fallback_words(query: str) -> list[str]:
    """The word-match fallback's needles: the query's words of four letters
    or more, the first six; the whole query when none."""
    return [w for w in _WORD.findall(query) if len(w) >= 4][:6] or [query]


def landed_payload(namespace: str, key: str, hash_: str, supersedes: str | None = None) -> dict:
    """`orreth.memory.landed.v1`'s payload: the ref, the hash, the hash it supersedes."""
    p = {"ref": f"{namespace}/{key}", "hash": hash_}
    if supersedes:
        p["supersedes"] = supersedes
    return p


def purge_payload(namespace: str, key: str, hashes: list[str]) -> dict:
    """The tombstone's payload (MEM-5): every version's hash, never the words,
    and one hash over them all."""
    return {"ref": f"{namespace}/{key}", "hashes": list(hashes), "hash": ev.content_hash(",".join(hashes))}
_VALID_AT = "valid_from <= %s AND (valid_to IS NULL OR valid_to > %s)"
_IN_STATE = "state = %s"      # quarantine (P11): a read never crosses states


def ensure_schema(conn) -> None:
    from .outbox import once
    if not once(conn, "store"):
        return
    with conn.transaction():
        cur = conn.cursor()
        cur.execute("SELECT pg_advisory_xact_lock(742199)")  # DDL race guard
        cur.execute(
            "CREATE TABLE IF NOT EXISTS spine_memories ("
            " memory_id bigserial PRIMARY KEY,"
            " namespace text NOT NULL, key text NOT NULL,"
            " body text NOT NULL, hash text NOT NULL, by_did text NOT NULL,"
            " scope text,"
            " landed_at timestamptz NOT NULL DEFAULT now(),"
            " valid_from timestamptz NOT NULL DEFAULT now(), valid_to timestamptz,"
            " supersedes text,"
            f" understanding text NOT NULL DEFAULT '{UNDERSTANDING}',"
            " tsv tsvector GENERATED ALWAYS AS (to_tsvector('english', body)) STORED)")
        # an older ground (v0: PRIMARY KEY (namespace, key), no lineage)
        # migrates in place — the rows stay, they gain their intervals
        cur.execute(
            "SELECT 1 FROM pg_index i JOIN pg_attribute a"
            " ON a.attrelid = i.indrelid AND a.attnum = ANY(i.indkey)"
            " WHERE i.indrelid = 'spine_memories'::regclass AND i.indisprimary"
            " AND a.attname = 'namespace'")
        if cur.fetchone():
            cur.execute("ALTER TABLE spine_memories DROP CONSTRAINT spine_memories_pkey")
        for col in ("memory_id bigserial", "scope text",
                    "valid_from timestamptz NOT NULL DEFAULT now()",
                    "valid_to timestamptz", "supersedes text",
                    f"understanding text NOT NULL DEFAULT '{UNDERSTANDING}'",
                    "tsv tsvector GENERATED ALWAYS AS (to_tsvector('english', body)) STORED"):
            cur.execute(f"ALTER TABLE spine_memories ADD COLUMN IF NOT EXISTS {col}")
        cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS spine_memories_id"
                    " ON spine_memories (memory_id)")
        cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS spine_memories_current"
                    " ON spine_memories (namespace, key, scope) WHERE valid_to IS NULL")
        cur.execute("CREATE INDEX IF NOT EXISTS spine_memories_tsv"
                    " ON spine_memories USING GIN (tsv)")
        cur.execute("ALTER TABLE spine_memories ADD COLUMN IF NOT EXISTS"
                    " state text NOT NULL DEFAULT 'in'")   # P11: opt-out is a state
        cur.execute("CREATE INDEX IF NOT EXISTS spine_memories_landed"
                    " ON spine_memories (namespace, scope, landed_at)")  # MEM-6


class OrrethStore:
    """LangGraph's Store shape (put / get / search) over the kernel's laws."""

    def __init__(self, conn, *, by_did: str, state: str = "in"):
        self._conn = conn
        self.by_did = by_did
        self.state = state          # P11: 'in' or 'opt-out' — what is done and
        ensure_schema(conn)         # remembered in a state stays in that state
        outbox.ensure_schema(conn)

    def put(self, namespace: str, key: str, body: str) -> str:
        """Land a memory with its event. The same words again land nothing
        (idempotent); different words become a sibling that supersedes
        the current one — the old row keeps its words and closes its
        interval. Never an overwrite (canon 0003: a correction is a
        sibling)."""
        h = ev.content_hash(body)
        with self._conn.transaction():
            cur = self._conn.cursor()
            cur.execute("SELECT memory_id, hash FROM spine_memories WHERE namespace = %s"
                        " AND key = %s AND scope = %s AND valid_to IS NULL FOR UPDATE",
                        (namespace, key, ev.scope()))
            prev = cur.fetchone()
            if prev and prev[1] == h:
                return h                       # the same words: nothing new
            payload = landed_payload(namespace, key, h, prev[1] if prev else None)
            if prev:
                cur.execute("UPDATE spine_memories SET valid_to = now()"
                            " WHERE memory_id = %s", (prev[0],))
            e = ev.make_envelope(
                kind="event", type=MEMORY_EVENT, universe_id=ev.scope(),
                scope_path=ev.scope(), payload=payload,
                authority_chain=[self.by_did])
            cur.execute(
                "INSERT INTO spine_memories (namespace, key, body, hash, by_did,"
                " scope, supersedes, state) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                (namespace, key, body, h, self.by_did, ev.scope(),
                 prev[1] if prev else None, self.state))
            outbox.add_row(cur, ev.encode(e), e["message_id"])
        return h

    def get(self, namespace: str, key: str, at: str | None = None) -> str | None:
        """Verbatim by key — what is true now, or what was true at `at`."""
        cur = self._conn.cursor()
        if at is None:
            cur.execute(f"SELECT body FROM spine_memories WHERE namespace = %s"
                        f" AND key = %s AND scope = %s AND {_VALID_NOW} AND {_IN_STATE}",
                        (namespace, key, ev.scope(), self.state))
        else:
            cur.execute(f"SELECT body FROM spine_memories WHERE namespace = %s"
                        f" AND key = %s AND scope = %s AND {_VALID_AT} AND {_IN_STATE}"
                        " ORDER BY valid_from DESC LIMIT 1",
                        (namespace, key, ev.scope(), at, at, self.state))
        row = cur.fetchone()
        return row[0] if row else None

    def history(self, namespace: str, key: str) -> list[dict]:
        """Every version, oldest first — the lineage, never an overwrite."""
        cur = self._conn.cursor()
        cur.execute(
            "SELECT hash, body, valid_from, valid_to, supersedes, understanding"
            " FROM spine_memories WHERE namespace = %s AND key = %s AND scope = %s"
            " ORDER BY valid_from", (namespace, key, ev.scope()))
        return [{"hash": r[0], "body": r[1], "valid_from": r[2].isoformat(),
                 "valid_to": r[3].isoformat() if r[3] else None,
                 "supersedes": r[4], "understanding": r[5]} for r in cur.fetchall()]

    def search(self, namespace: str, query: str, limit: int = 5,
               at: str | None = None) -> list[dict]:
        """Understanding v0: full-text, stemmed, RANKED — "cure" finds
        "cures"; the best match first. Current rows, or the rows valid at
        `at` (what we knew then). Falls back to the old word-match when
        the query carries nothing the projection can hold (stopwords
        only), so a young memory is never unreachable."""
        cur = self._conn.cursor()
        valid, vargs = (_VALID_NOW, ()) if at is None else (_VALID_AT, (at, at))
        terms = search_terms(query)                   # OR-shaped recall (the fixture's law)
        cur.execute(
            f"SELECT key, body, ts_rank(tsv, q) AS rank FROM spine_memories,"
            f" websearch_to_tsquery('english', %s) q"
            f" WHERE namespace = %s AND scope = %s AND {valid} AND {_IN_STATE} AND tsv @@ q"
            f" ORDER BY rank DESC, landed_at DESC LIMIT %s",
            (terms, namespace, ev.scope(), *vargs, self.state, limit))
        rows = [{"key": k, "body": b, "rank": float(r)} for k, b, r in cur.fetchall()]
        if rows:
            return rows
        words = fallback_words(query)
        conds = " OR ".join(["body ILIKE %s"] * len(words))
        cur.execute(
            f"SELECT key, body FROM spine_memories"
            f" WHERE namespace = %s AND scope = %s AND {valid} AND {_IN_STATE} AND ({conds})"
            f" ORDER BY landed_at DESC LIMIT %s",
            (namespace, ev.scope(), *vargs, self.state, *[f"%{w}%" for w in words], limit))
        return [{"key": k, "body": b, "rank": 0.0} for k, b in cur.fetchall()]

    def within(self, namespace: str, from_iso: str, to_iso: str,
               limit: int = 6) -> list[dict]:
        """Recall by timeframe (MEM-1): every word landed between X and Y,
        oldest first — any version; the window the human typed, honored."""
        cur = self._conn.cursor()
        cur.execute(
            f"SELECT key, body, landed_at FROM spine_memories WHERE namespace = %s"
            f" AND scope = %s AND {_IN_STATE} AND landed_at BETWEEN %s AND %s"
            f" ORDER BY landed_at LIMIT %s",
            (namespace, ev.scope(), self.state, from_iso, to_iso, limit))
        return [{"key": k, "body": b, "landed_at": t.isoformat()}
                for k, b, t in cur.fetchall()]

    def recent(self, namespace: str, limit: int = 5) -> list[dict]:
        cur = self._conn.cursor()
        cur.execute(
            f"SELECT key, body FROM spine_memories WHERE namespace = %s"
            f" AND scope = %s AND {_VALID_NOW} AND {_IN_STATE}"
            f" ORDER BY landed_at DESC LIMIT %s",
            (namespace, ev.scope(), self.state, limit))
        return [{"key": k, "body": b} for k, b in cur.fetchall()]

    def purge(self, namespace: str, key: str) -> dict:
        """Governed erasure (canon 0003 · MEM-5): every version of a memory
        leaves the Record; the projection leaves with the rows; a TOMBSTONE
        event keeps the hashes — never the words — so the erasure itself is
        remembered. Digests that cited it are rebuilt by the caller."""
        with self._conn.transaction():
            cur = self._conn.cursor()
            cur.execute("DELETE FROM spine_memories WHERE namespace = %s AND key = %s"
                        " AND scope = %s RETURNING hash", (namespace, key, ev.scope()))
            hashes = [r[0] for r in cur.fetchall()]
            if hashes:
                e = ev.make_envelope(
                    kind="event", type=PURGE_EVENT, universe_id=ev.scope(),
                    scope_path=ev.scope(), payload=purge_payload(namespace, key, hashes),
                    authority_chain=[self.by_did])
                outbox.add_row(cur, ev.encode(e), e["message_id"])
        return {"ref": f"{namespace}/{key}", "versions": len(hashes), "hashes": hashes}
