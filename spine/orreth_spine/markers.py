# PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch markers sp1, the open vocabulary of WHY · 2026-09-19
"""Markers (canon 0006): the kernel's open, governed vocabulary of WHY.
A marker is a typed origin on a fact — {kind, id, parent, by}: a root
fact mints it, a serving fact carries it, a new beginning under it mints
a child. Kinds are DECLARED into a registry before use (the kernel seeds
the structural five and `improvement`); any body sets markers on
whatever it is executing through the `mark` door; the INTEREST LAW
dispatches an ask to every body that declared interest in a kind, the
marker as parent — setting AND using markers drives automation."""
from __future__ import annotations

import json
import secrets

from . import envelope as ev, outbox

MARKER_SET = "orreth.marker.set.v1"
INCLUDES = ("planner", "critic", "grader")

SEED = [  # kind, group, description — the kernel's, in every world
    ("objective", "structural", "a human's ask — a root"),
    ("intention", "structural", "a schedule (human · role · kernel) — a root; occurrences under it"),
    ("thought", "structural", "an include's reasoning — under the session's latest objective"),
    ("action", "structural", "a tool call, a purge, a watch — under the serving ask"),
    ("observation", "structural", "a harness run, a red watch, a lease lapse — under its kernel intention"),
    ("improvement", "quality", "an improvement observed to what was being executed — every body's policy marks it"),
]


class UnknownKind(ValueError):
    """Declared before use — the teaching names the registry."""


def ensure_schema(conn) -> None:
    from .outbox import once
    if not once(conn, "markers"):
        return
    with conn.transaction():
        cur = conn.cursor()
        cur.execute("SELECT pg_advisory_xact_lock(742199)")  # DDL race guard
        cur.execute(
            "CREATE TABLE IF NOT EXISTS spine_marker_kinds ("
            " kind text NOT NULL, grp text NOT NULL, description text NOT NULL,"
            " declared_by text NOT NULL, scope text NOT NULL,"
            " declared_at timestamptz NOT NULL DEFAULT now(),"
            " PRIMARY KEY (kind, scope))")
        cur.execute(
            "CREATE TABLE IF NOT EXISTS spine_markers ("
            " marker_id text PRIMARY KEY, kind text NOT NULL, parent text,"
            " ref text NOT NULL, by_did text NOT NULL, note text,"
            " scope text NOT NULL, at timestamptz NOT NULL DEFAULT now())")
        cur.execute("CREATE INDEX IF NOT EXISTS spine_markers_parent ON spine_markers (parent)")
        cur.execute("CREATE INDEX IF NOT EXISTS spine_markers_kind ON spine_markers (scope, kind, at)")


_SEEDED: set[str] = set()      # worlds this process has seeded (the ground keeps them)


def seed(conn) -> None:
    """The kernel's kinds, in THIS world — idempotent, once per world per
    process (the DDL guard is per connection; a world is not)."""
    ensure_schema(conn)
    scope = ev.scope()
    if scope in _SEEDED:
        return
    with conn.transaction():
        cur = conn.cursor()
        for kind, grp, desc in SEED:
            cur.execute(
                "INSERT INTO spine_marker_kinds (kind, grp, description, declared_by, scope)"
                " VALUES (%s, %s, %s, 'the kernel', %s) ON CONFLICT DO NOTHING",
                (kind, grp, desc, scope))
    _SEEDED.add(scope)


def kinds(conn) -> list[dict]:
    seed(conn)
    cur = conn.cursor()
    cur.execute("SELECT kind, grp, description, declared_by, declared_at FROM spine_marker_kinds"
                " WHERE scope = %s ORDER BY grp, kind", (ev.scope(),))
    return [{"kind": r[0], "group": r[1], "description": r[2], "declared_by": r[3],
             "declared_at": r[4].isoformat()} for r in cur.fetchall()]


def declare(conn, kind: str, grp: str, description: str, by: str) -> dict:
    """A new kind enters the vocabulary — declared, never invented."""
    seed(conn)
    kind = kind.strip().lower()
    if not kind or not kind.replace("-", "").replace("_", "").isalnum():
        raise ValueError("a kind is a short lowercase name: letters, digits, dashes")
    with conn.transaction():
        conn.cursor().execute(
            "INSERT INTO spine_marker_kinds (kind, grp, description, declared_by, scope)"
            " VALUES (%s, %s, %s, %s, %s) ON CONFLICT DO NOTHING",
            (kind, grp.strip().lower() or "declared", description, by, ev.scope()))
    return {"kind": kind, "group": grp}


def check_kind(conn, kind: str) -> None:
    seed(conn)
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM spine_marker_kinds WHERE kind = %s AND scope = %s",
                (kind, ev.scope()))
    if cur.fetchone() is None:
        known = ", ".join(k["kind"] for k in kinds(conn))
        raise UnknownKind(f"no marker kind named {kind!r} is declared here — declare it "
                          f"first (kind, group, what it means); the kinds today: {known}")


def new_id() -> str:
    return "mk_" + secrets.token_hex(6)


def insert(cur, marker_id: str, kind: str, parent: str | None, ref: str,
           by: str, note: str | None = None) -> None:
    """The marker row, inside a transaction someone else owns (the write
    path: the fact and its marker land together)."""
    cur.execute(
        "INSERT INTO spine_markers (marker_id, kind, parent, ref, by_did, note, scope)"
        " VALUES (%s, %s, %s, %s, %s, %s, %s)",
        (marker_id, kind, parent, ref, by, note, ev.scope()))


def mint(conn, kind: str, ref: str, by: str, parent: str | None = None,
         note: str | None = None) -> dict:
    """A marker on its own transaction (a structural mint outside the
    write path)."""
    check_kind(conn, kind)
    mid = new_id()
    with conn.transaction():
        insert(conn.cursor(), mid, kind, parent, ref, by, note)
    return {"kind": kind, "id": mid, "parent": parent, "by": by}


def get(conn, marker_id: str) -> dict | None:
    ensure_schema(conn)
    cur = conn.cursor()
    cur.execute("SELECT marker_id, kind, parent, ref, by_did, note, at FROM spine_markers"
                " WHERE marker_id = %s AND scope = %s", (marker_id, ev.scope()))
    r = cur.fetchone()
    return {"id": r[0], "kind": r[1], "parent": r[2], "ref": r[3], "by": r[4],
            "note": r[5], "at": r[6].isoformat()} if r else None


def as_env(conn, marker_id: str | None) -> dict | None:
    """The envelope's four fields for a marker id."""
    m = get(conn, marker_id) if marker_id else None
    return {"kind": m["kind"], "id": m["id"], "parent": m["parent"], "by": m["by"]} if m else None


def set_marker(conn, kind: str, ref: str, by: str, parent: str | None = None,
               note: str | None = None) -> dict:
    """The `mark` door's effect: a marker set by a body or a human on what
    was being executed — with its fact on the rail (orreth.marker.set.v1)
    so interested bodies can act."""
    check_kind(conn, kind)
    outbox.ensure_schema(conn)
    mid = new_id()
    marker = {"kind": kind, "id": mid, "parent": parent, "by": by}
    e = ev.make_envelope(
        kind="event", type=MARKER_SET, universe_id=ev.scope(), scope_path=ev.scope(),
        payload={"ref": ref, "hash": ev.content_hash(note or ""), "marker_id": mid,
                 "kind": kind, "parent": parent},
        correlation_id=ref, authority_chain=[by], marker=marker)
    with conn.transaction():
        cur = conn.cursor()
        insert(cur, mid, kind, parent, ref, by, note)
        outbox.add_row(cur, ev.encode(e), e["message_id"])
    return dict(marker, ref=ref, note=note)


def interested(conn, kind: str) -> list[str]:
    """The bodies of this world whose templates declared interest in a kind."""
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT ON (name) name, interests FROM spine_joins"
                " WHERE scope = %s ORDER BY name, join_id DESC", (ev.scope(),))
    return [name for name, ints in cur.fetchall()
            if ints and kind in json.loads(ints)]


def dispatch_interests(conn, marker: dict, ref: str, note: str | None) -> list[dict]:
    """The interest law: every interested body is asked to act — the
    marker as PARENT, so the lineage records who acted, on what, and why."""
    from . import dispatch
    cur = conn.cursor()                     # the act lands in the marked ask's
    cur.execute("SELECT session FROM spine_asks WHERE ask_id = %s", (ref,))   # session,
    row = cur.fetchone()                    # so the chat that promised it shows it
    session = row[0] if row else None
    asked = []
    for name in interested(conn, marker["kind"]):
        if name == marker["by"]:
            continue
        text = (f"A marker of kind {marker['kind']!r} was set on {ref} by {marker['by']}"
                + (f": {note}" if note else "") + ". Act on it as your role requires.")
        [aid] = dispatch.submit_ask(conn, text, person=marker["by"], to=[name],
                                    parent_marker=marker["id"], session=session)
        asked.append({"body": name, "ask_id": aid})
    return asked


def tree(conn, root: str, limit: int = 500) -> list[dict]:
    """Everything under a marker — the dependency, downward."""
    ensure_schema(conn)
    cur = conn.cursor()
    cur.execute(
        "WITH RECURSIVE t AS ("
        "  SELECT marker_id, kind, parent, ref, by_did, note, at, 0 AS depth FROM spine_markers"
        "   WHERE marker_id = %s AND scope = %s"
        "  UNION ALL"
        "  SELECT m.marker_id, m.kind, m.parent, m.ref, m.by_did, m.note, m.at, t.depth + 1"
        "   FROM spine_markers m JOIN t ON m.parent = t.marker_id)"
        " SELECT * FROM t ORDER BY depth, at LIMIT %s", (root, ev.scope(), limit))
    return [_row(r) for r in cur.fetchall()]


def ancestry(conn, marker_id: str) -> list[dict]:
    """Up from a marker to its root — what this serves."""
    ensure_schema(conn)
    cur = conn.cursor()
    cur.execute(
        "WITH RECURSIVE a AS ("
        "  SELECT marker_id, kind, parent, ref, by_did, note, at, 0 AS depth FROM spine_markers"
        "   WHERE marker_id = %s AND scope = %s"
        "  UNION ALL"
        "  SELECT m.marker_id, m.kind, m.parent, m.ref, m.by_did, m.note, m.at, a.depth + 1"
        "   FROM spine_markers m JOIN a ON m.marker_id = a.parent)"
        " SELECT * FROM a ORDER BY depth", (marker_id, ev.scope()))
    return [_row(r) for r in cur.fetchall()]


def stream(conn, kind: str | None = None, grp: str | None = None, limit: int = 60) -> list[dict]:
    """The live stream, newest first — by kind, by group, or all."""
    ensure_schema(conn)
    cur = conn.cursor()
    cur.execute(
        "SELECT m.marker_id, m.kind, m.parent, m.ref, m.by_did, m.note, m.at, 0, k.grp"
        " FROM spine_markers m LEFT JOIN spine_marker_kinds k"
        " ON k.kind = m.kind AND k.scope = m.scope"
        " WHERE m.scope = %s AND (%s::text IS NULL OR m.kind = %s)"
        " AND (%s::text IS NULL OR k.grp = %s) ORDER BY m.at DESC LIMIT %s",
        (ev.scope(), kind, kind, grp, grp, limit))
    out = []
    for r in cur.fetchall():
        d = _row(r[:8]); d["group"] = r[8]; out.append(d)
    return out


def _row(r) -> dict:
    return {"id": r[0], "kind": r[1], "parent": r[2], "ref": r[3], "by": r[4],
            "note": r[5], "at": r[6].isoformat(), "depth": r[7]}


def with_words(conn, rows: list[dict]) -> list[dict]:
    """The why in words: an ask ref carries the ask's text (walk #5: the
    why printed ids)."""
    ids = [m["ref"] for m in rows if m["ref"].startswith("ask_")]
    if not ids:
        return rows
    cur = conn.cursor()
    cur.execute("SELECT ask_id, left(text, 100) FROM spine_asks WHERE ask_id = ANY(%s)", (ids,))
    words = dict(cur.fetchall())
    for m in rows:
        if m["ref"] in words:
            m["words"] = words[m["ref"]]
    return rows
