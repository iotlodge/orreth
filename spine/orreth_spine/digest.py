# PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P5 sp3, the Digest (MEM-3) · 2026-09-19
"""The Digest (canon 0003, JB's compression law): the short version of an
episode, written at its boundary, CITING every record it compresses. v0
is extractive and deterministic — the head of every exchange, who
replied and when, the words acquired — so a rebuilt digest is
byte-identical when nothing changed, and a grown episode gets a SIBLING
digest that supersedes (never an overwrite). A mind's prose digest can
land later as a sibling of the same record. The pack reads the short
version first; the verbatim opens on demand through the recall door."""
from __future__ import annotations

import json
import secrets

from . import envelope as ev, outbox

DIGEST_EVENT = "orreth.digest.landed.v1"
HEAD = 120


def ensure_schema(conn) -> None:
    from .outbox import once
    if not once(conn, "digest"):
        return
    with conn.transaction():
        cur = conn.cursor()
        cur.execute("SELECT pg_advisory_xact_lock(742199)")  # DDL race guard
        cur.execute(
            "CREATE TABLE IF NOT EXISTS spine_digests ("
            " digest_id text PRIMARY KEY, kind text NOT NULL, ref text NOT NULL,"
            " body text NOT NULL, sources text NOT NULL, hash text NOT NULL,"
            " by_did text NOT NULL, scope text NOT NULL, supersedes text,"
            " built_at timestamptz NOT NULL DEFAULT now(),"
            " valid_from timestamptz NOT NULL DEFAULT now(), valid_to timestamptz)")
        cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS spine_digests_current"
                    " ON spine_digests (kind, ref, scope) WHERE valid_to IS NULL")


def _head(text: str, n: int = HEAD) -> str:
    text = " ".join((text or "").split())
    return text if len(text) <= n else text[:n - 1].rstrip() + "…"


def compose_session(conn, session_id: str) -> tuple[str, list[str]] | None:
    """The short version of a session, from the Record alone: every ask's
    head, who replied and when, the reply's head; the words acquired in
    the session's span. Returns (body, sources) or None if no session."""
    from .resident import ensure_schema as _ground
    _ground(conn)
    cur = conn.cursor()
    cur.execute("SELECT session_id, title, opened_at, person FROM spine_sessions"
                " WHERE session_id = %s AND scope = %s", (session_id, ev.scope()))
    row = cur.fetchone()
    if row is None:
        return None
    _sid, title, opened, person = row
    # the episode's span: from this session's opening to the next session's
    # opening (the same human, this world) — or now, for the latest one
    cur.execute("SELECT coalesce(min(opened_at), now()) FROM spine_sessions"
                " WHERE person = %s AND scope = %s AND opened_at > %s",
                (person, ev.scope(), opened))
    span_end = cur.fetchone()[0]
    cur.execute(
        "SELECT a.ask_id, a.text, a.reply, a.status, a.asked_at, a.replied_at,"
        " coalesce(j.name, 'a resident')"
        " FROM spine_asks a LEFT JOIN LATERAL ("
        "  SELECT name FROM spine_joins WHERE did = a.served_by"
        "  ORDER BY join_id DESC LIMIT 1) j ON true"
        " WHERE a.session = %s ORDER BY a.asked_at", (session_id,))
    asks = cur.fetchall()
    sources = [a[0] for a in asks]
    lines = [f"session {session_id[4:10]}" + (f" — {title}" if title else "")
             + f" · opened {opened.strftime('%a %b %d %H:%M')} · {len(asks)} ask"
             + ("" if len(asks) == 1 else "s")]
    for aid, text, reply, status, at, rat, who in asks:
        lines.append(f"· {at.strftime('%H:%M')} asked: {_head(text)}")
        if status == "replied" and reply:
            lines.append(f"  {who} replied ({rat.strftime('%H:%M') if rat else '—'}): {_head(reply)}")
        elif status != "received":
            lines.append(f"  {status}")
    if asks:
        cur.execute("SELECT to_regclass('spine_memories') IS NOT NULL")
        if cur.fetchone()[0]:
            cur.execute(
                "SELECT namespace, key, body FROM spine_memories WHERE scope = %s"
                " AND landed_at BETWEEN %s AND %s ORDER BY landed_at",
                (ev.scope(), opened, span_end))
            for ns, key, body in cur.fetchall():
                sources.append(f"{ns}/{key}")
                lines.append(f"· acquired [{ns}/{key}]: {_head(body)}")
    return "\n".join(lines), sources


def build(conn, session_id: str, by: str = "the digest builder") -> dict | None:
    """Write (or rebuild) the session's digest: the same substance lands
    nothing new; changed substance lands a sibling that supersedes."""
    ensure_schema(conn)
    outbox.ensure_schema(conn)
    made = compose_session(conn, session_id)
    if made is None:
        return None
    body, sources = made
    h = ev.content_hash(body)
    with conn.transaction():
        cur = conn.cursor()
        cur.execute("SELECT digest_id, hash FROM spine_digests WHERE kind = 'session'"
                    " AND ref = %s AND scope = %s AND valid_to IS NULL FOR UPDATE",
                    (session_id, ev.scope()))
        prev = cur.fetchone()
        if prev and prev[1] == h:
            return {"digest_id": prev[0], "hash": h, "body": body, "sources": sources,
                    "new": False}
        did = "dig_" + secrets.token_hex(5)
        if prev:
            cur.execute("UPDATE spine_digests SET valid_to = now() WHERE digest_id = %s",
                        (prev[0],))
        cur.execute(
            "INSERT INTO spine_digests (digest_id, kind, ref, body, sources, hash,"
            " by_did, scope, supersedes) VALUES (%s, 'session', %s, %s, %s, %s, %s, %s, %s)",
            (did, session_id, body, json.dumps(sources), h, by, ev.scope(),
             prev[1] if prev else None))
        e = ev.make_envelope(
            kind="event", type=DIGEST_EVENT, universe_id=ev.scope(), scope_path=ev.scope(),
            payload={"ref": did, "hash": h, "session": session_id,
                     "sources": len(sources)}, correlation_id=session_id,
            authority_chain=[by])
        outbox.add_row(cur, ev.encode(e), e["message_id"])
    return {"digest_id": did, "hash": h, "body": body, "sources": sources, "new": True}


def of_session(conn, session_id: str) -> dict | None:
    """The current digest of a session, with its sources."""
    ensure_schema(conn)
    cur = conn.cursor()
    cur.execute("SELECT digest_id, body, sources, hash, by_did, built_at, supersedes"
                " FROM spine_digests WHERE kind = 'session' AND ref = %s AND scope = %s"
                " AND valid_to IS NULL", (session_id, ev.scope()))
    r = cur.fetchone()
    return {"digest_id": r[0], "session": session_id, "body": r[1],
            "sources": json.loads(r[2]), "hash": r[3], "by": r[4],
            "built_at": r[5].isoformat(), "supersedes": r[6]} if r else None


def for_person(conn, person: str, *, exclude: str | None = None,
               window: dict | None = None, limit: int = 3) -> list[dict]:
    """The short version first (the pack's third rung): the current digests
    of this human's sessions in this world — newest first; inside a
    window, only sessions with asks in it."""
    ensure_schema(conn)
    cur = conn.cursor()
    if window and window.get("from") and window.get("to"):
        cur.execute(
            "SELECT d.digest_id, d.ref, d.body, d.sources FROM spine_digests d"
            " JOIN spine_sessions s ON s.session_id = d.ref"
            " WHERE d.kind = 'session' AND d.scope = %s AND d.valid_to IS NULL"
            " AND s.person = %s AND d.ref <> %s AND EXISTS (SELECT 1 FROM spine_asks a"
            "  WHERE a.session = d.ref AND a.asked_at BETWEEN %s AND %s)"
            " ORDER BY s.opened_at DESC LIMIT %s",
            (ev.scope(), person, exclude or "", window["from"], window["to"], limit))
    else:
        cur.execute(
            "SELECT d.digest_id, d.ref, d.body, d.sources FROM spine_digests d"
            " JOIN spine_sessions s ON s.session_id = d.ref"
            " WHERE d.kind = 'session' AND d.scope = %s AND d.valid_to IS NULL"
            " AND s.person = %s AND d.ref <> %s ORDER BY s.opened_at DESC LIMIT %s",
            (ev.scope(), person, exclude or "", limit))
    return [{"digest_id": r[0], "session": r[1], "body": r[2],
             "sources": json.loads(r[3])} for r in cur.fetchall()]
