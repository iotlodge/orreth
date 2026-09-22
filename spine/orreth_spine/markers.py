# PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch markers sp1, the open vocabulary of WHY · 2026-09-19
# Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P6 cure sp3 (the re-walk's wounds): W21 the schedule row wears its cadence · 2026-09-21
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
INCLUDES = ("planner", "critic", "grader", "mitl")   # P6 sp3: MITL is an include of the third kind

SEED = [  # kind, group, description — the kernel's, in every world
    ("objective", "structural", "a human's ask — a root"),
    ("intention", "structural", "a schedule (human · role · kernel) — a root; occurrences under it"),
    ("thought", "structural", "an include's reasoning — under the session's latest objective"),
    ("action", "structural", "a tool call, a purge, a watch — under the serving ask"),
    ("observation", "structural", "a harness run, a red watch, a lease lapse — under its kernel intention"),
    ("improvement", "quality", "an improvement observed to what was being executed — every body's policy marks it"),
    ("watch-red", "resiliency", "a watch judged red — under the intention that keeps it green (0007)"),
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
        # block 11 / P25: every marker knows its ROOT, so the Analyzer is a
        # GROUP BY over the ground — lookups, never a walk per request
        cur.execute("ALTER TABLE spine_markers ADD COLUMN IF NOT EXISTS root text")
        cur.execute("CREATE INDEX IF NOT EXISTS spine_markers_root ON spine_markers (scope, root)")
        cur.execute("CREATE INDEX IF NOT EXISTS spine_markers_roots ON spine_markers (scope, at)"
                    " WHERE parent IS NULL")
        cur.execute("SELECT 1 FROM spine_markers WHERE root IS NULL LIMIT 1")
        if cur.fetchone():                 # rows from before the column: once
            cur.execute(
                "WITH RECURSIVE r AS ("
                "  SELECT marker_id, marker_id AS root FROM spine_markers WHERE parent IS NULL"
                "  UNION ALL"
                "  SELECT m.marker_id, r.root FROM spine_markers m JOIN r ON m.parent = r.marker_id)"
                " UPDATE spine_markers s SET root = r.root FROM r"
                " WHERE s.marker_id = r.marker_id AND s.root IS NULL")


def seed(conn) -> None:
    """The kernel's kinds, in THIS world — idempotent, once per world per
    CONNECTION (a process-wide memo lied: two connections on different
    grounds — the test schema and the public one — share a process, and
    the second ground never got its seed; the rig's `watch-red` was then
    unknown and Resiliency never declared)."""
    ensure_schema(conn)
    scope = ev.scope()
    done = getattr(conn, "_spine_seeded", None)
    if done is None:
        done = set()
        conn._spine_seeded = done
    if scope in done:
        return
    with conn.transaction():
        cur = conn.cursor()
        for kind, grp, desc in SEED:
            cur.execute(
                "INSERT INTO spine_marker_kinds (kind, grp, description, declared_by, scope)"
                " VALUES (%s, %s, %s, 'the kernel', %s) ON CONFLICT DO NOTHING",
                (kind, grp, desc, scope))
    done.add(scope)


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
        "INSERT INTO spine_markers (marker_id, kind, parent, ref, by_did, note, scope, root)"
        " VALUES (%s, %s, %s, %s, %s, %s, %s,"
        " coalesce((SELECT root FROM spine_markers WHERE marker_id = %s), %s))",
        (marker_id, kind, parent, ref, by, note, ev.scope(), parent, marker_id))


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
               note: str | None = None, chain: list[str] | None = None) -> dict:
    """The `mark` door's effect: a marker set by a body or a human on what
    was being executed — with its fact on the rail (orreth.marker.set.v1)
    so interested bodies can act. The fact wears the setter's FULL chain
    (P6 sp2 · AG-7): the origin human first, then the body — `[by]` alone
    only when a human marks by hand."""
    check_kind(conn, kind)
    outbox.ensure_schema(conn)
    mid = new_id()
    marker = {"kind": kind, "id": mid, "parent": parent, "by": by}
    authority = list(chain) if chain else [by]
    if by not in authority:
        authority.append(by)
    e = ev.make_envelope(
        kind="event", type=MARKER_SET, universe_id=ev.scope(), scope_path=ev.scope(),
        payload={"ref": ref, "hash": ev.content_hash(note or ""), "marker_id": mid,
                 "kind": kind, "parent": parent},
        correlation_id=ref, authority_chain=authority, marker=marker)
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
    from . import intent                    # 0007: the same law at intention level —
    for t in intent.on_marker(conn, marker, ref, note):   # an interested intention plans
        asked.append({"body": t["planner"], "ask_id": t["plan_ask"],
                      "intention": t["intention_id"], "words": t["words"]})
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


def _has(conn, table: str) -> bool:
    cur = conn.cursor()
    cur.execute("SELECT to_regclass(%s) IS NOT NULL", (table,))
    return bool(cur.fetchone()[0])


def with_words(conn, rows: list[dict]) -> list[dict]:
    """The why in words: an ask ref carries the ask's text and status
    (walk #5: the why printed ids); an intention ref its words and
    whether it stands; a schedule ref its text."""
    cur = conn.cursor()
    ids = [m["ref"] for m in rows if m["ref"].startswith("ask_")]
    if ids:
        cur.execute("SELECT ask_id, left(text, 100), status, target FROM spine_asks"
                    " WHERE ask_id = ANY(%s)", (ids,))
        found = {r[0]: r[1:] for r in cur.fetchall()}
        for m in rows:
            if m["ref"] in found:
                m["words"], m["status"], m["target"] = found[m["ref"]]
    iids = [m["ref"] for m in rows if m["ref"].startswith("int_")]
    if iids and _has(conn, "spine_intentions"):
        cur.execute("SELECT count(*) FROM pg_attribute WHERE attrelid = to_regclass('spine_intentions')"
                    " AND attname = 'blocked_note' AND NOT attisdropped")
        blk = ", blocked_note" if cur.fetchone()[0] else ", NULL"
        cur.execute("SELECT intention_id, left(words, 100), active, serves, kind" + blk +
                    " FROM spine_intentions WHERE intention_id = ANY(%s)", (iids,))
        found = {r[0]: r[1:] for r in cur.fetchall()}
        for m in rows:
            if m["ref"] in found:
                m["words"], m["active"], m["serves"], m["origin_kind"], note = found[m["ref"]]
                m["blocked"], m["blocked_note"] = note is not None, note   # W6: waiting for a crew
    sids = [m["ref"] for m in rows if m["ref"].startswith("sch_")]
    if sids and _has(conn, "spine_schedules"):
        cur.execute("SELECT s.schedule_id, left(s.text, 100), s.active, s.kind, s.every_s, s.last_at,"
                    " (SELECT count(*) FROM spine_occurrences o WHERE o.schedule_id = s.schedule_id)"
                    " FROM spine_schedules s WHERE s.schedule_id = ANY(%s)", (sids,))
        found = {r[0]: r[1:] for r in cur.fetchall()}
        from .scheduler import cadence_words
        for m in rows:
            if m["ref"] in found:
                m["words"], m["active"], m["origin_kind"], every, last, runs = found[m["ref"]]
                m["serves"] = "schedule"
                m["cadence"], m["runs"] = cadence_words(every), int(runs)     # W21: "hourly · 12 runs · last 08:12 PM"
                m["last_at"] = last.isoformat() if last else None
    return rows


def origins(conn, limit: int = 60) -> list[dict]:
    """The Analyzer's door (P25): every ROOT in this world — intentions and
    objectives — newest first, with what grew under each, counted by kind,
    from the ground alone (the root column: no walk per request)."""
    ensure_schema(conn)
    cur = conn.cursor()
    cur.execute(
        "SELECT r.marker_id, r.kind, r.parent, r.ref, r.by_did, r.note, r.at, 0,"
        " (SELECT coalesce(json_object_agg(x.kind, x.n), '{}'::json) FROM"
        "   (SELECT c.kind, count(*) AS n FROM spine_markers c"
        "     WHERE c.scope = r.scope AND c.root = r.marker_id AND c.marker_id <> r.marker_id"
        "     GROUP BY c.kind) x)"
        " FROM spine_markers r WHERE r.scope = %s AND r.parent IS NULL"
        " ORDER BY r.at DESC LIMIT %s", (ev.scope(), limit))
    out = []
    for row in cur.fetchall():
        d = _row(row[:8]); d["root"] = d["id"]
        d["counts"] = row[8] if isinstance(row[8], dict) else json.loads(row[8] or "{}")
        out.append(d)
    return with_words(conn, out)


def origin(conn, root: str) -> dict:
    """One origin's tree, in words."""
    return {"root": root, "tree": with_words(conn, tree(conn, root))}
