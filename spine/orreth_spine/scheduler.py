# PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P4 sp5, the scheduler · 2026-09-18
# Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P6 cure sp3 (the re-walk's wounds): W21 a duty is framed as a duty · 2026-09-21
"""The scheduler — a kernel organ (canon 0004: three schedulers, one
body). A SCHEDULE is a standing intention on the ground: HUMAN (the
identity's, CRUD through the door), ROLE (declared by a body's template,
registered at its join), KERNEL (registered by the rig — required,
visible, NEVER editable). An OCCURRENCE of a human or role schedule is
an ask to its runner on the Invocation rail — seen in the band, wearing
its journey; a kernel occurrence acts directly and is recorded. Rest is
a first-class recorded act, never a deletion (covenant rule 11): the
human can always stop what the machine manages.

Walk #8's cure (W21, the reasoning wound): an occurrence is FRAMED as a
duty — the ask the runner receives carries the duty's words, its cadence,
the window since its last run, and the runner's own earlier notes — never
the bare sentence a twelfth time, as if a human re-asked it."""
from __future__ import annotations

import secrets
from datetime import datetime, timezone

from . import envelope as ev

KINDS = ("human", "role", "kernel")


class KernelRequired(PermissionError):
    """Visible, never editable — the one plain face for a kernel schedule."""


def ensure_schema(conn) -> None:
    from .outbox import once
    if not once(conn, "scheduler"):
        return
    with conn.transaction():
        cur = conn.cursor()
        cur.execute("SELECT pg_advisory_xact_lock(742199)")  # DDL race guard
        cur.execute(
            "CREATE TABLE IF NOT EXISTS spine_schedules ("
            " schedule_id text PRIMARY KEY, runner text NOT NULL,"
            " kind text NOT NULL, text text NOT NULL, every_s int NOT NULL,"
            " next_at timestamptz NOT NULL DEFAULT now(), last_at timestamptz,"
            " active boolean NOT NULL DEFAULT true, added_by text NOT NULL,"
            " rested_by text, rested_at timestamptz, scope text NOT NULL,"
            " added_at timestamptz NOT NULL DEFAULT now())")
        cur.execute("ALTER TABLE spine_schedules ADD COLUMN IF NOT EXISTS"
                    " marker text")                 # the intention's marker
        cur.execute(
            "CREATE TABLE IF NOT EXISTS spine_occurrences ("
            " occurrence_id text PRIMARY KEY, schedule_id text NOT NULL,"
            " ref text, at timestamptz NOT NULL DEFAULT now())")


def cadence_words(every_s: int) -> str:
    """The cadence in a human's word (conformance `duty_text`): hourly ·
    daily · weekly · every N minutes · every N seconds."""
    n = int(every_s)
    if n == 3600:
        return "hourly"
    if n == 86400:
        return "daily"
    if n == 604800:
        return "weekly"
    if n % 3600 == 0:
        return f"every {n // 3600} hours"
    if n % 60 == 0 and n >= 60:
        return f"every {n // 60} minute{'s' if n // 60 != 1 else ''}"
    return f"every {n} seconds"


def duty_text(text: str, every_s: int, since: str | None, notes: list[str]) -> str:
    """The framing of a duty's occurrence (W21; conformance `duty_text`):
    `"<the duty's words>" — your <cadence> duty (every N s) · since <the
    last run's time | your first run> · your earlier notes today: <one
    line each, newest first, at most 3>` — or `· no earlier notes today`."""
    words = " ".join((text or "").split())
    cadence = cadence_words(every_s)
    head = (f"“{words}” — your duty {cadence} (every {int(every_s)} s)" if cadence.startswith("every")
            else f"“{words}” — your {cadence} duty (every {int(every_s)} s)")
    window = f"since {since}" if since else "your first run"
    lines = [" ".join((n or "").split())[:160] for n in (notes or [])][:3]
    tail = ("your earlier notes today: " + " · ".join(lines)) if lines else "no earlier notes today"
    return f"{head} · {window} · {tail}"


def _clock(at: datetime | None, zone: str) -> str | None:
    if at is None:
        return None
    try:
        from zoneinfo import ZoneInfo
        return at.astimezone(ZoneInfo(zone)).strftime("%I:%M %p").lstrip("0")
    except Exception:
        return at.astimezone(timezone.utc).strftime("%H:%M UTC")


def notes_for(conn, schedule_id: str, *, limit: int = 3) -> list[str]:
    """The runner's own earlier notes on this duty — the first line of
    each replied occurrence, newest first, today (the last 24 h)."""
    cur = conn.cursor()
    cur.execute(
        "SELECT a.reply FROM spine_occurrences o JOIN spine_asks a ON a.ask_id = o.ref"
        " WHERE o.schedule_id = %s AND a.status = 'replied' AND a.reply IS NOT NULL"
        " AND a.replied_at > now() - interval '24 hours'"
        " ORDER BY a.replied_at DESC LIMIT %s", (schedule_id, limit))
    out = []
    for (rp,) in cur.fetchall():
        first = (rp or "").strip().split("\n", 1)[0].strip()
        if first:
            out.append(first)
    return out


def add(conn, runner: str, kind: str, text: str, every_s: int, by: str,
        *, first_in_s: int | None = None) -> str:
    """A standing intention lands. `first_in_s` None = due now."""
    if kind not in KINDS:
        raise ValueError(f"kind is one of {', '.join(KINDS)}")
    from . import markers
    ensure_schema(conn)
    markers.ensure_schema(conn)
    sid = "sch_" + secrets.token_hex(5)
    mid = markers.new_id()
    with conn.transaction():
        cur = conn.cursor()
        markers.insert(cur, mid, "intention", None, sid, by)   # a root: WHY it beats
        cur.execute(
            "INSERT INTO spine_schedules (schedule_id, runner, kind, text, every_s,"
            " next_at, added_by, scope, marker) VALUES (%s, %s, %s, %s, %s,"
            " now() + make_interval(secs => %s), %s, %s, %s)",
            (sid, runner, kind, text, int(every_s),
             int(first_in_s if first_in_s is not None else 0), by, ev.scope(), mid))
    return sid


def declared(conn, runner: str, kind: str, text: str, every_s: int, by: str) -> str:
    """Register once (a template's role schedule at every join; the
    kernel's duties at every boot): the same intention is never doubled."""
    ensure_schema(conn)
    cur = conn.cursor()
    cur.execute("SELECT schedule_id, marker FROM spine_schedules WHERE runner = %s AND kind = %s"
                " AND text = %s AND scope = %s", (runner, kind, text, ev.scope()))
    row = cur.fetchone()
    if row is None:
        return add(conn, runner, kind, text, every_s, by, first_in_s=every_s)
    if row[1] is None:                 # declared before markers existed: it
        from . import markers          # gets its intention now, once
        mid = markers.mint(conn, "intention", row[0], by)["id"]
        with conn.transaction():
            conn.cursor().execute("UPDATE spine_schedules SET marker = %s"
                                  " WHERE schedule_id = %s", (mid, row[0]))
    return row[0]


def rest(conn, schedule_id: str, by: str) -> None:
    """The human's stop: recorded, reversible in the Record, never a delete."""
    cur = conn.cursor()
    cur.execute("SELECT kind FROM spine_schedules WHERE schedule_id = %s AND scope = %s",
                (schedule_id, ev.scope()))
    row = cur.fetchone()
    if row is None:
        raise KeyError(schedule_id)
    if row[0] == "kernel":
        raise KernelRequired("kernel-required — visible, never editable")
    with conn.transaction():
        conn.cursor().execute(
            "UPDATE spine_schedules SET active = false, rested_by = %s, rested_at = now()"
            " WHERE schedule_id = %s", (by, schedule_id))


def for_runner(conn, runner: str) -> dict:
    """The card's side B (P16): every schedule this runner runs, by kind."""
    ensure_schema(conn)
    cur = conn.cursor()
    cur.execute(
        "SELECT s.schedule_id, s.kind, s.text, s.every_s, s.next_at, s.last_at,"
        " s.active, s.added_by, s.rested_by, s.rested_at,"
        " (SELECT count(*) FROM spine_occurrences o WHERE o.schedule_id = s.schedule_id)"
        " FROM spine_schedules s WHERE s.runner = %s AND s.scope = %s"
        " ORDER BY s.kind, s.added_at", (runner, ev.scope()))
    out = {"human": [], "role": [], "kernel": []}
    for r in cur.fetchall():
        out[r[1]].append({
            "schedule_id": r[0], "text": r[2], "every_s": r[3],
            "next_at": r[4].isoformat(), "last_at": r[5].isoformat() if r[5] else None,
            "active": r[6], "added_by": r[7], "rested_by": r[8],
            "rested_at": r[9].isoformat() if r[9] else None,
            "occurrences": int(r[10]), "editable": r[1] != "kernel"})
    return out


def tick(conn, bodies: dict | None = None) -> list[dict]:
    """The organ's beat: every due, active schedule occurs — human and
    role ones as an ask to the runner on the rail; kernel ones act here
    (the harness run) — and the next beat is set. Returns what occurred."""
    from . import dispatch, harness
    from .resident import ensure_schema as _ground   # the notes read the asks' ground (W21)
    ensure_schema(conn); _ground(conn)
    cur = conn.cursor()
    cur.execute("SELECT schedule_id, runner, kind, text, every_s, added_by, marker, last_at"
                " FROM spine_schedules WHERE active AND next_at <= now() AND scope = %s"
                " ORDER BY next_at", (ev.scope(),))
    occurred = []
    from .resident import HUMAN_ZONE_DEFAULT, HUMAN_ZONE_DIAL
    import os
    zone = os.environ.get(HUMAN_ZONE_DIAL, HUMAN_ZONE_DEFAULT)
    for sid, runner, kind, text, every_s, by, marker, last_at in cur.fetchall():
        ref = None
        if kind == "kernel" and text.startswith("run the harness"):
            body = (bodies or {}).get(runner)
            if body is not None:              # an OBSERVATION under the intention
                ref = harness.run(conn, body, parent_marker=marker)["run_id"]
        else:                                 # an occurrence: an objective under it —
            framed = duty_text(text, every_s, _clock(last_at, zone),   # framed as a DUTY (W21)
                               notes_for(conn, sid))
            ref = dispatch.submit_ask(conn, framed, person=by, to=[runner],
                                      parent_marker=marker)[0]
        oid = "occ_" + secrets.token_hex(5)
        with conn.transaction():
            c = conn.cursor()
            c.execute("INSERT INTO spine_occurrences (occurrence_id, schedule_id, ref)"
                      " VALUES (%s, %s, %s)", (oid, sid, ref))
            c.execute("UPDATE spine_schedules SET last_at = now(),"
                      " next_at = now() + make_interval(secs => %s)"
                      " WHERE schedule_id = %s", (int(every_s), sid))
        occurred.append({"schedule_id": sid, "runner": runner, "kind": kind, "ref": ref})
    return occurred
