# PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch intent sp1, the fifth firmware-rail · 2026-09-19
"""The intent loop — the fifth firmware-rail (canon 0007, block 11).

Human INTENTION is the topmost origin of work. An intention is a record
on the ground with a body — words · serves · kind · interests · planner
· cadence · gates · stop — and a root marker; a schedule is its smallest
form. The loop: an intention OBSERVES (a marker of a kind it is
interested in — a red watch — or its cadence coming due); the kernel asks
its PLANNER under the observation ("the next objective?"); the planner's
reply IS an objective — an ask to the crew with the intention as parent,
filed in the intention's own session so the chat that promised it shows
it. The crew acts; observations land; the loop turns.

The stop is recorded, never a deletion (covenant rule 11): the human can
always stop what the machine manages — the kernel's intentions included
(kernel DUTIES stay immutable; a standing PROGRAM rests on the human's
word). "State is an outcome of applied Intent" (P24): every act here
wears the marker of the intention it serves.
"""
from __future__ import annotations

import json
import re
import secrets

from . import envelope as ev, outbox

INTENTION_DECLARED = "orreth.intention.declared.v1"
INTENTION_STOPPED = "orreth.intention.stopped.v1"
SERVES = ("business", "security", "resiliency", "compliance", "cost")
KINDS = ("human", "role", "kernel")
ASK_KINDS = ("thought", "objective", "intention")      # P23: the ask wears its kind
WATCH_RED = "watch-red"                                # seeded by the kernel (markers.SEED)

RESILIENCY = {                    # the first Infinite Horizon Intention (0007)
    "words": "keep this world resilient: when a watch goes red, get it green",
    "serves": "resiliency", "interests": [WATCH_RED], "planner": "planner"}


def ensure_schema(conn) -> None:
    from .outbox import once
    if not once(conn, "intent"):
        return
    with conn.transaction():
        cur = conn.cursor()
        cur.execute("SELECT pg_advisory_xact_lock(742199)")  # DDL race guard
        cur.execute(
            "CREATE TABLE IF NOT EXISTS spine_intentions ("
            " intention_id text PRIMARY KEY, words text NOT NULL, serves text NOT NULL,"
            " kind text NOT NULL, interests text NOT NULL, planner text NOT NULL,"
            " runner text, every_s int, gates text,"
            " active boolean NOT NULL DEFAULT true, stopped_by text, stopped_at timestamptz,"
            " added_by text NOT NULL, scope text NOT NULL, marker text NOT NULL,"
            " session text, next_at timestamptz, last_at timestamptz,"
            " added_at timestamptz NOT NULL DEFAULT now())")
        cur.execute(
            "CREATE TABLE IF NOT EXISTS spine_intent_turns ("
            " turn_id text PRIMARY KEY, intention_id text NOT NULL, cause text,"
            " plan_ask text NOT NULL, objective_ask text,"
            " at timestamptz NOT NULL DEFAULT now())")
        cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS spine_intent_turns_cause"
                    " ON spine_intent_turns (cause) WHERE cause IS NOT NULL")


# ---- the kind of an ask (P23): the words propose it, the human flips it ----
_PREFIX = re.compile(r"^(thought|objective|intention)\s*:\s*(.+)$", re.I | re.S)
_INTENT = re.compile(
    r"(\bkeep\b.{0,60}\b(resilient|green|alive|safe|secure|compliant|healthy|under|below|within)\b"
    r"|\bwhen(ever)?\b.{0,60}\b(goes|turns|is|are|go)\s+(red|down|dormant|late|over)\b"
    r"|\bevery\s+(\d+\s+)?(minute|hour|day|week)s?\b|\bfrom now on\b|\bwatch for\b"
    r"|\bstanding\b|\bas long as\b|\bany ?time\b)", re.I)
_THOUGHT = re.compile(
    r"(\?\s*$|^(who|what|what's|whats|when|where|why|how|is|are|does|do|can|could|would"
    r"|should|which|did|tell me|explain|describe|repeat)\b)", re.I)
_EVERY = re.compile(r"\bevery\s+(\d+\s+)?(minute|hour|day|week)s?\b", re.I)
_UNIT = {"minute": 60, "hour": 3600, "day": 86400, "week": 604800}
_SERVES = (("cost", r"cost|spend|run rate|budget|meter|token"),
           ("security", r"secur|threat|vulnerab|attack|intrus"),
           ("compliance", r"complian|audit|regulat|policy"),
           ("resiliency", r"resilien|\bred\b|watch|alive|dormant|lease|outage|uptime|health|green"))


def read_words(text: str) -> dict:
    """The chip's proposal: what kind of ask these words are — thought ·
    objective · intention — and, for an intention, what it serves, what
    wakes it (interests), and its cadence. A typed prefix ("intention: …")
    is the human's flip and wins; the words after it are the ask. Word
    rules, v0 — the human always flips; the marker records the outcome."""
    t = " ".join(text.split())
    kind, pinned = None, False
    m = _PREFIX.match(t)
    if m:
        kind, t, pinned = m.group(1).lower(), m.group(2).strip(), True
    low = t.lower()
    if kind is None:
        if _INTENT.search(low):
            kind = "intention"
        elif _THOUGHT.search(low):
            kind = "thought"
        else:
            kind = "objective"
    out = {"kind": kind, "words": t, "pinned": pinned}
    if kind == "intention":
        serves = "business"
        for s, pat in _SERVES:
            if re.search(pat, low):
                serves = s
                break
        interests = []
        if re.search(r"watch|\bred\b|green|resilien", low):
            interests.append(WATCH_RED)
        if re.search(r"improv", low):
            interests.append("improvement")
        if re.search(r"cost|spend|budget", low):
            interests.append("cost-anomaly")
        em = _EVERY.search(low)
        every = (int((em.group(1) or "1").strip()) * _UNIT[em.group(2).lower()]) if em else None
        out.update(serves=serves, interests=interests, every_s=every)
    return out


# ---- the record ----
_COLS = ("intention_id, words, serves, kind, interests, planner, runner, every_s, gates,"
         " active, stopped_by, stopped_at, added_by, marker, session, next_at, last_at, added_at")


def _dict(r) -> dict:
    return {"intention_id": r[0], "words": r[1], "serves": r[2], "kind": r[3],
            "interests": json.loads(r[4] or "[]"), "planner": r[5], "runner": r[6],
            "every_s": r[7], "gates": json.loads(r[8]) if r[8] else None,
            "active": r[9], "stopped_by": r[10],
            "stopped_at": r[11].isoformat() if r[11] else None, "added_by": r[12],
            "marker": r[13], "session": r[14],
            "next_at": r[15].isoformat() if r[15] else None,
            "last_at": r[16].isoformat() if r[16] else None, "added_at": r[17].isoformat()}


def declare(conn, words: str, *, serves: str, kind: str, by: str,
            interests: list[str] | tuple = (), planner: str = "planner",
            runner: str | None = None, every_s: int | None = None,
            gates: dict | None = None) -> dict:
    """An intention lands: its row, its root marker, its own session (where
    its objectives show), and its fact on the rail — one transaction."""
    from . import markers
    from .resident import ensure_schema as _ground
    if serves not in SERVES:
        raise ValueError(f"serves is one of {', '.join(SERVES)}")
    if kind not in KINDS:
        raise ValueError(f"kind is one of {', '.join(KINDS)}")
    words = " ".join(words.split())
    if not words:
        raise ValueError("an intention is words")
    interests = [str(k).strip().lower() for k in (interests or ()) if str(k).strip()]
    if not interests and not every_s:
        raise ValueError("an intention needs something to wake it: say WHEN — "
                         "'when a watch goes red', 'every hour', 'when an improvement is marked'")
    _ground(conn); ensure_schema(conn); markers.ensure_schema(conn); outbox.ensure_schema(conn)
    for k in interests:
        markers.check_kind(conn, k)        # interests name declared kinds — the teaching otherwise
    iid = "int_" + secrets.token_hex(6)
    mid = markers.new_id()
    sid = "ses_" + secrets.token_hex(6)
    marker = {"kind": "intention", "id": mid, "parent": None, "by": by}
    e = ev.make_envelope(
        kind="event", type=INTENTION_DECLARED, universe_id=ev.scope(), scope_path=ev.scope(),
        payload={"ref": iid, "hash": ev.content_hash(words), "serves": serves, "kind": kind,
                 "interests": interests, "planner": planner, "every_s": every_s},
        correlation_id=iid, authority_chain=[by],
        aggregate={"type": "intention", "id": iid, "sequence": 1}, marker=marker)

    def domain(cur):
        markers.insert(cur, mid, "intention", None, iid, by, words[:200])   # the root: WHY
        cur.execute("INSERT INTO spine_sessions (session_id, person, scope, title, state)"
                    " VALUES (%s, %s, %s, %s, 'in')", (sid, by, ev.scope(), words[:120]))
        cur.execute(
            "INSERT INTO spine_intentions (intention_id, words, serves, kind, interests,"
            " planner, runner, every_s, gates, added_by, scope, marker, session, next_at)"
            " VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,"
            " CASE WHEN %s::int IS NULL THEN NULL ELSE now() + make_interval(secs => %s) END)",
            (iid, words, serves, kind, json.dumps(interests), planner, runner, every_s,
             json.dumps(gates) if gates else None, by, ev.scope(), mid, sid,
             every_s, every_s or 0))

    outbox.commit_with_outbox(conn, ev.encode(e), e["message_id"], domain)
    return get(conn, iid)


def declared(conn, words: str, **kw) -> dict:
    """Register once per world (the kernel's at every boot): the same
    intention is never doubled — and one at rest stays at rest."""
    ensure_schema(conn)
    cur = conn.cursor()
    cur.execute("SELECT intention_id FROM spine_intentions WHERE words = %s AND kind = %s"
                " AND scope = %s", (" ".join(words.split()), kw.get("kind"), ev.scope()))
    row = cur.fetchone()
    return get(conn, row[0]) if row else declare(conn, words, **kw)


def get(conn, intention_id: str) -> dict | None:
    ensure_schema(conn)
    cur = conn.cursor()
    cur.execute(f"SELECT {_COLS} FROM spine_intentions WHERE intention_id = %s AND scope = %s",
                (intention_id, ev.scope()))
    r = cur.fetchone()
    return _dict(r) if r else None


def listing(conn, *, serves: str | None = None, kind: str | None = None,
            active: bool | None = None, limit: int = 60) -> list[dict]:
    """Every intention in this world, newest first, with what grew under it."""
    ensure_schema(conn)
    cur = conn.cursor()
    cur.execute(
        f"SELECT {_COLS},"
        " (SELECT count(*) FROM spine_markers c WHERE c.parent = i.marker AND c.kind = 'objective'),"
        " (SELECT count(*) FROM spine_markers c WHERE c.parent = i.marker"
        "   AND c.kind NOT IN ('objective', 'thought')),"
        " (SELECT count(*) FROM spine_intent_turns t WHERE t.intention_id = i.intention_id)"
        " FROM spine_intentions i WHERE i.scope = %s"
        " AND (%s::text IS NULL OR i.serves = %s) AND (%s::text IS NULL OR i.kind = %s)"
        " AND (%s::boolean IS NULL OR i.active = %s)"
        " ORDER BY i.added_at DESC LIMIT %s",
        (ev.scope(), serves, serves, kind, kind, active, active, limit))
    out = []
    for r in cur.fetchall():
        d = _dict(r[:18])
        d.update(objectives=int(r[18]), observations=int(r[19]), turns=int(r[20]))
        out.append(d)
    return out


def stop(conn, intention_id: str, by: str) -> dict:
    """The human's stop (rule 11): recorded on the row and on the rail,
    never a deletion; the loop does not turn again for it."""
    ensure_schema(conn); outbox.ensure_schema(conn)
    cur = conn.cursor()
    cur.execute("SELECT marker, active FROM spine_intentions WHERE intention_id = %s AND scope = %s",
                (intention_id, ev.scope()))
    row = cur.fetchone()
    if row is None:
        raise KeyError(intention_id)
    if not row[1]:
        return get(conn, intention_id)      # already at rest: one face
    marker = {"kind": "intention", "id": row[0], "parent": None, "by": by}
    e = ev.make_envelope(
        kind="event", type=INTENTION_STOPPED, universe_id=ev.scope(), scope_path=ev.scope(),
        payload={"ref": intention_id, "hash": "sha256:-", "by": by},
        correlation_id=intention_id, authority_chain=[by], marker=marker)

    def domain(cur):
        cur.execute("UPDATE spine_intentions SET active = false, stopped_by = %s, stopped_at = now()"
                    " WHERE intention_id = %s", (by, intention_id))

    outbox.commit_with_outbox(conn, ev.encode(e), e["message_id"], domain)
    return get(conn, intention_id)


# ---- the loop ----
def interested(conn, kind: str) -> list[dict]:
    """The active intentions of this world that declared interest in a kind."""
    ensure_schema(conn)
    cur = conn.cursor()
    cur.execute(f"SELECT {_COLS} FROM spine_intentions WHERE scope = %s AND active"
                " ORDER BY added_at", (ev.scope(),))
    return [d for d in (_dict(r) for r in cur.fetchall()) if kind in d["interests"]]


def plan(conn, intention: dict, *, cause: dict | None, observed: str) -> dict:
    """The kernel asks the intention's planner — under the observation
    that woke it (or under the intention itself, on cadence): 'the next
    objective?' One turn per cause, ever."""
    from . import dispatch
    cur = conn.cursor()
    if cause:
        cur.execute("SELECT turn_id FROM spine_intent_turns WHERE cause = %s", (cause["id"],))
        if cur.fetchone():
            return {"planned": False, "intention_id": intention["intention_id"]}
    text = (f"INTENTION (serves {intention['serves']}): {intention['words']}\n"
            f"OBSERVED: {observed}\n"
            "Reply with the ONE next objective for the crew that serves this intention — "
            "one imperative sentence, nothing else.")
    [aid] = dispatch.submit_ask(conn, text, person=intention["added_by"],
                                to=[intention["planner"]],
                                parent_marker=(cause["id"] if cause else intention["marker"]),
                                session=intention["session"])
    tid = "turn_" + secrets.token_hex(5)
    with conn.transaction():
        c = conn.cursor()
        c.execute("INSERT INTO spine_intent_turns (turn_id, intention_id, cause, plan_ask)"
                  " VALUES (%s, %s, %s, %s)",
                  (tid, intention["intention_id"], cause["id"] if cause else None, aid))
        c.execute("UPDATE spine_intentions SET last_at = now() WHERE intention_id = %s",
                  (intention["intention_id"],))
    return {"planned": True, "turn_id": tid, "intention_id": intention["intention_id"],
            "planner": intention["planner"], "plan_ask": aid, "words": intention["words"]}


def on_marker(conn, marker: dict, ref: str, note: str | None) -> list[dict]:
    """The interest law at intention level: every active intention that
    cares about this kind plans its next objective under the marker —
    when the marker already sits under one of them, that one alone."""
    from . import markers
    cands = interested(conn, marker["kind"])
    if not cands:
        return []
    if marker.get("parent"):
        anc = markers.ancestry(conn, marker["id"])
        root = anc[-1]["id"] if anc else None
        mine = [i for i in cands if i["marker"] == root]
        if mine:
            cands = mine
    observed = f"a marker of kind {marker['kind']!r} on {ref}" + (f": {note}" if note else "")
    return [t for t in (plan(conn, i, cause=marker, observed=observed) for i in cands)
            if t["planned"]]


def _watch_transitions(conn) -> list[dict]:
    """Watches judged; the ones newly red (first seen red, or green before)."""
    from . import monitor
    snap = monitor.snapshot(conn, rails=False)
    cur = conn.cursor()
    cur.execute("SELECT watch_id, last_ok FROM spine_watches WHERE scope = %s", (ev.scope(),))
    last = dict(cur.fetchall())
    red = [w for w in snap["watches"] if not w["ok"] and last.get(w["watch_id"]) is not False]
    with conn.transaction():
        c = conn.cursor()
        for w in snap["watches"]:
            c.execute("UPDATE spine_watches SET last_ok = %s WHERE watch_id = %s",
                      (bool(w["ok"]), w["watch_id"]))
    return red


def _due(conn) -> list[dict]:
    """Cadence: every active intention whose beat came due plans once."""
    cur = conn.cursor()
    cur.execute(f"SELECT {_COLS} FROM spine_intentions WHERE scope = %s AND active"
                " AND every_s IS NOT NULL AND next_at <= now() ORDER BY next_at", (ev.scope(),))
    out = []
    for i in (_dict(r) for r in cur.fetchall()):
        out.append(plan(conn, i, cause=None, observed="the cadence came due; nothing new was observed"))
        with conn.transaction():
            conn.cursor().execute(
                "UPDATE spine_intentions SET next_at = now() + make_interval(secs => %s)"
                " WHERE intention_id = %s", (int(i["every_s"]), i["intention_id"]))
    return out


def _file_objectives(conn) -> list[dict]:
    """A replied plan becomes the objective: an ask to the crew, the
    intention as parent, in the intention's session — while it stands."""
    from . import dispatch
    cur = conn.cursor()
    cur.execute(
        "SELECT t.turn_id, i.intention_id, i.added_by, i.runner, i.marker, i.session, a.reply"
        " FROM spine_intent_turns t"
        " JOIN spine_intentions i ON i.intention_id = t.intention_id"
        " JOIN spine_asks a ON a.ask_id = t.plan_ask"
        " WHERE t.objective_ask IS NULL AND a.status = 'replied' AND i.active AND i.scope = %s",
        (ev.scope(),))
    filed = []
    for tid, iid, by, runner, marker, session, reply in cur.fetchall():
        words = " ".join((reply or "").split())[:500]
        if not words:
            with conn.transaction():
                conn.cursor().execute("UPDATE spine_intent_turns SET objective_ask = '-'"
                                      " WHERE turn_id = %s", (tid,))
            continue
        out = dispatch.submit_ask(conn, words, person=by, to=[runner] if runner else None,
                                  parent_marker=marker, session=session)
        oid = out[0] if isinstance(out, list) else out
        with conn.transaction():
            conn.cursor().execute("UPDATE spine_intent_turns SET objective_ask = %s"
                                  " WHERE turn_id = %s", (oid, tid))
        filed.append({"turn_id": tid, "intention_id": iid, "objective_ask": oid})
    return filed


def turn(conn) -> dict:
    """The rail's beat: watches judged and the newly red ones observed
    under every intention that cares (the marker set is a fact; the
    interest law asks the planner under it); cadences that came due
    plan; replied plans are filed as objectives."""
    from . import markers
    ensure_schema(conn)
    observed = []
    for w in _watch_transitions(conn):
        note = (f"watch {w['name']!r} went red: {w['metric']} {w['op']} {w['threshold']},"
                f" value {w['value']}")
        for i in interested(conn, WATCH_RED):
            m = markers.set_marker(conn, WATCH_RED, ref=w["watch_id"], by="the kernel",
                                   parent=i["marker"], note=note)
            observed.append(m["id"])
            markers.dispatch_interests(conn, m, w["watch_id"], note)   # → on_marker → the plan
    due = _due(conn)
    filed = _file_objectives(conn)
    return {"observed": observed, "due": due, "filed": filed}
