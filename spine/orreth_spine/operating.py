# PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch Phase 8 THE WORKSHOP sp5, THE OPERATING STATE · 2026-10-08
# Amended: Claude Fable 5.1 (claude-fable-5-1) — THE GROUND CONNECTIONS CURE (2026-10-08): the kernel's sixth watch at light — `ground_connections >= ceiling − reserve` — beside the five · 2026-10-08
"""THE OPERATING STATE (canon 0010 §7 · 0005 Phase 8 sp5; JB's Kernel Strategic Measurements,
2026-10-05): the kernel's top-level scorecard, five measurements each 1.0 at the ideal, read
LIVE off the ground and WATCHED like any metric —

- TRUST — the ability to do the right thing — v0: the graded live replies that PASSED over all
  graded live replies (the grader's signed verdicts, `spine_verdicts.on_ask`; A · B · C pass);
- RECALL — the ability to replay — v0: the served asks whose reply landed under a marker (the
  chain is the replay) over all served asks;
- EFFICIENCY — the use of Orreth — v0: the serves of the last day finished inside their
  LATENCY CLASS (a chat ask 30 s; work and events 180 s) over all serves;
- EXPERIENCE — feedback — v0: the non-negative human feedback (a thumb up) over all feedback
  given through the feedback door; UNKNOWN when none was given, never a silent 1.0;
- COST — correlation and itemisation — v0: the spend a serving ask can be named for (the meter
  line wears the ask) over all spend, until the Costs Panel brings itemisation to the metal.

Each measurement is UNKNOWN (null) while its denominator is empty — said, never a silent 1.0;
an unknown turns no watch red. The five are watches declared by the kernel at light (`trust <
1.0` …), and ONE KERNEL INTENTION, THE OPERATING STATE, stands beside Resiliency, interested in
`watch-red` like it: the WATCH is the discriminator — an intention that names `watches` takes
the reds of those metrics alone, and one that names none takes every other red. Its runner is
the critic, whose PROPOSE tool closes THE IMPROVEMENT LOOP in the Workshop: a draft on the
draft shelf UNDER THE AGENT'S OWNER, marked "proposed by the critic from marker X" — raw
feedback never reaches a body. THE GRADE BEAT makes the grader the consumer of live replies:
a body's reply of the last hour not yet graded is handed to the grader under the reply's own
marker (the hull's event edge), the evidence in the ask and the form in the answer (`grade:
<A–F> — <one line>`); the grader writes its SIGNED verdict on the reply (rule 2). SUMMON is
generalized from the MITL toggle: any body whose template declares `summonable` joins a
session's includes on the human's word, dismissed the same way, both facts recorded; helpers
never. IMPORT runs a repo'd graph inside the hull: a graph node of kind `import` names a
`source` of the repo form (repo · commit · entry); the body fetches the commit once under its
home and runs the entry (a compiled LangGraph, or a callable of the words) — in a dev universe
only. Law for law with the Rust kernel (`operating.rs`, fixture `operating-v0.json`).
"""
from __future__ import annotations

import json
import re
import secrets

from . import envelope as ev
from . import outbox

KERNEL = "the kernel"
MEASUREMENTS = ("trust", "recall", "efficiency", "experience", "cost")
TARGET = 1.0
WATCH_OP = "<"                                  # red when a measurement falls below the ideal
PASS_GRADES = ("A", "B", "C")
LATENCY_CLASSES = {"chat": 30.0, "work": 180.0, "event": 180.0}   # v0: by the ask's edge
EFFICIENCY_WINDOW_H = 24
GRADE_WINDOW_MIN = 60                           # the grade beat reads the last hour's replies
GRADE_PER_BEAT = 5
GRADE_EVERY_S = 60
GRADE_DIAL = "SPINE_GRADE_LIVE"                 # "0" turns the live grading off (spend)
SERVES = "operating-state"
OPERATING = {
    "words": "keep this world's operating state at 1.0 — Trust · Recall · Efficiency · Experience · Cost: "
             "when a measurement goes red, get it green",
    "serves": SERVES, "interests": ["watch-red"], "planner": "planner", "runner": "critic",
    "watches": list(MEASUREMENTS)}
FEEDBACK_GIVEN = "orreth.feedback.given.v1"
INCLUDE_SUMMONED = "orreth.include.summoned.v1"
INCLUDE_DISMISSED = "orreth.include.dismissed.v1"
DRAFT_PROPOSED = "orreth.draft.proposed.v1"
BASE_INCLUDES = ("planner", "critic", "grader", "mitl")
GRADE_HEAD = "grader, grade the reply"
GRADING_KIND = "grading"                        # the marker a live grading hangs under (seeded by the kernel)
IMPORT_NODE = "import"


class OperatingRefused(ValueError):
    """Refused in words."""


# ---- the law (pure; mirrored in operating.rs) ----------------------------------------------------

def ratio(num: int | float, den: int | float) -> float | None:
    """A coverage ratio: unknown (None) while the denominator is empty — never a silent 1.0."""
    if not den or den <= 0:
        return None
    return round(float(num) / float(den), 4)


def latency_class(marker_kind: str | None, parent_kind: str | None) -> tuple[str, float]:
    """v0: a serve's class is the hull's edge its ask took — chat (30 s), work or event (180 s)."""
    from . import crafts
    edge = crafts.hull_edge(marker_kind, parent_kind)
    return edge, LATENCY_CLASSES[edge]


def pass_grade(grade: str | None) -> bool:
    return (grade or "").upper() in PASS_GRADES


def measure_words(name: str, value: float | None, num: int | float, den: int | float) -> str:
    """One measurement, in words."""
    what = {"trust": ("graded replies passed", "graded"),
            "recall": ("served asks replayable by their marker chain", "served"),
            "efficiency": ("serves inside their latency class", "serves of the last day"),
            "experience": ("thumbs up", "thumbs given"),
            "cost": ("spend a serving ask can be named for", "spend")}[name]
    if value is None:
        return f"{name}: unknown — no {what[1]} yet (never a silent 1.0)"
    if name == "cost":
        return f"{name}: {value:.4f} — ${num:.4f} of ${den:.4f} {what[0]}"
    return f"{name}: {value:.4f} — {int(num)} of {int(den)} {what[0]}"


def routes_to(intention_watches: list | None, metric: str) -> bool:
    """The watch is the discriminator: an intention naming `watches` takes the reds of those
    metrics alone; one naming none takes every red that is NOT a measurement."""
    if intention_watches:
        return metric in intention_watches
    return metric not in MEASUREMENTS


_GRADE_RX = re.compile(r"^\s*\**\s*grade\s*\**\s*:\s*\**\s*([A-Fa-f])\b", re.I | re.M)


def grade_of_live(text: str | None) -> dict:
    """The grader's verdict on a live reply, by the form `grade: <A–F> — <one line>`; the
    grade None when the form was not kept (said, never guessed)."""
    m = _GRADE_RX.search(text or "")
    line = None
    if m:
        rest = (text or "")[m.end():].split("\n", 1)[0]
        line = rest.split("—", 1)[1].strip(" *") if "—" in rest else (rest.strip(" -:*") or None)
    return {"grade": m.group(1).upper() if m else None, "line": line}


def grade_ask(ask_id: str, who: str, text: str, reply: str) -> str:
    """The kernel's ask of the grader on a live reply — the evidence in the ask, the form in the answer."""
    return (f"{GRADE_HEAD} {ask_id} by {who}. The ask: {text!r}. The reply: {str(reply)[:1200]!r}. "
            "Grade the reply against the ask — did it do the right thing, completely and plainly? "
            "Answer in exactly this form, one line: `grade: <A-F> — <one line of reason>`. Never grade your own words.")


def proposal_words(agent: str, name: str, kind: str, marker: str) -> str:
    return f"proposed by the critic from marker {marker} — for {agent}: the {name} {kind}"


def summon_words(body: str, on: bool, session: str | None) -> str:
    where = "this session's crew" if session else "your crew"
    if on:
        return f"{body} summoned — it joins {where}: address it as “{body}, …”; say “dismiss {body}” to let it go · recorded"
    return f"{body} dismissed — it leaves {where} · recorded, never deleted; say “summon {body}” to call it back"


def measurement_watch(name: str) -> dict:
    """The kernel's own watch on a measurement: red when it falls below the ideal."""
    return {"name": name, "metric": name, "op": WATCH_OP, "threshold": TARGET}


def import_words(source: str, commit: str, entry: str) -> str:
    return f"ran the imported graph {source} at {commit[:12]} — entry {entry}"


# ---- the ground ----------------------------------------------------------------------------------

DDL = (
    "CREATE TABLE IF NOT EXISTS spine_feedback ("
    " feedback_id text PRIMARY KEY, scope text NOT NULL, ask_id text NOT NULL, person text NOT NULL,"
    " sign int NOT NULL, words text, at timestamptz NOT NULL DEFAULT now())",
    "CREATE INDEX IF NOT EXISTS spine_feedback_scope ON spine_feedback (scope, at)",
    "CREATE TABLE IF NOT EXISTS spine_includes ("
    " row_id bigserial PRIMARY KEY, scope text NOT NULL, session text, person text NOT NULL, body text NOT NULL,"
    " state text NOT NULL, marker text, at timestamptz NOT NULL DEFAULT now())",
    "CREATE INDEX IF NOT EXISTS spine_includes_session ON spine_includes (scope, session, body, row_id DESC)",
    "CREATE TABLE IF NOT EXISTS spine_grading ("
    " ask_id text PRIMARY KEY, scope text NOT NULL, grade_ask text NOT NULL, at timestamptz NOT NULL DEFAULT now())",
    "ALTER TABLE spine_meter ADD COLUMN IF NOT EXISTS ask text",
    "ALTER TABLE spine_verdicts ALTER COLUMN experiment_id DROP NOT NULL",
    "ALTER TABLE spine_verdicts ADD COLUMN IF NOT EXISTS on_ask text",
    "CREATE INDEX IF NOT EXISTS spine_verdicts_on_ask ON spine_verdicts (scope, on_ask)",
    "ALTER TABLE spine_intentions ADD COLUMN IF NOT EXISTS watches text",
)


def ensure_schema(conn) -> None:
    from .outbox import once
    if not once(conn, "operating"):
        return
    from . import experiments, gateway, intent
    experiments.ensure_schema(conn); gateway.ensure_schema(conn); intent.ensure_schema(conn)
    with conn.transaction():
        cur = conn.cursor()
        cur.execute("SELECT pg_advisory_xact_lock(742199)")
        for stmt in DDL:
            cur.execute(stmt)


def _fact(cur, type_: str, ref: str, payload: dict, by: list[str], marker: dict | None = None) -> None:
    e = ev.make_envelope(kind="event", type=type_, universe_id=ev.universe(), scope_path=ev.universe(),
                         payload={"ref": ref, "hash": ev.content_hash(payload), **payload},
                         correlation_id=ref, authority_chain=by, marker=marker)
    outbox.add_row(cur, ev.encode(e), e["message_id"])


# ---- the five, measured --------------------------------------------------------------------------

def measure(conn) -> dict:
    """The five measurements, live: `{name: {value, num, den, words}}`."""
    ensure_schema(conn)
    u = ev.universe()
    cur = conn.cursor()
    out = {}
    cur.execute("SELECT verdict FROM spine_verdicts WHERE scope = %s AND on_ask IS NOT NULL", (u,))
    grades = [json.loads(r[0]).get("grade") for r in cur.fetchall()]
    out["trust"] = _m("trust", sum(1 for g in grades if pass_grade(g)), len(grades))
    cur.execute("SELECT count(*) FILTER (WHERE marker IS NOT NULL AND reply IS NOT NULL), count(*) FROM spine_asks"
                " WHERE scope = %s AND status = 'replied' AND served_by <> %s", (u, KERNEL))
    r = cur.fetchone()
    out["recall"] = _m("recall", int(r[0]), int(r[1]))
    cur.execute("SELECT a.asked_at, a.replied_at, m.kind, p.kind FROM spine_asks a"
                " LEFT JOIN spine_markers m ON m.marker_id = a.marker LEFT JOIN spine_markers p ON p.marker_id = m.parent"
                " WHERE a.scope = %s AND a.status = 'replied' AND a.served_by <> %s AND a.replied_at IS NOT NULL"
                " AND a.replied_at >= now() - make_interval(hours => %s)", (u, KERNEL, EFFICIENCY_WINDOW_H))
    rows = cur.fetchall()
    inside = 0
    for asked, replied, mk, pk in rows:
        _, limit = latency_class(mk, pk)
        if (replied - asked).total_seconds() <= limit:
            inside += 1
    out["efficiency"] = _m("efficiency", inside, len(rows))
    cur.execute("SELECT count(*) FILTER (WHERE sign >= 0), count(*) FROM spine_feedback WHERE scope = %s", (u,))
    r = cur.fetchone()
    out["experience"] = _m("experience", int(r[0]), int(r[1]))
    cur.execute("SELECT coalesce(sum(usd) FILTER (WHERE ask IS NOT NULL), 0), coalesce(sum(usd), 0) FROM spine_meter"
                " WHERE scope = %s", (u,))
    r = cur.fetchone()
    out["cost"] = _m("cost", float(r[0]), float(r[1]))
    return out


def _m(name: str, num, den) -> dict:
    v = ratio(num, den)
    return {"value": v, "num": num, "den": den, "words": measure_words(name, v, num, den)}


def values(conn) -> dict:
    """The five as watchable metric values (None = unknown)."""
    return {k: v["value"] for k, v in measure(conn).items()}


# ---- the watches and the intention at light ----------------------------------------------------

GROUND_WATCH = "ground_connections"      # the cure (2026-10-08): the kernel's sixth watch


def ground_watch(connections: dict) -> dict:
    """THE GROUND'S WATCH (the cure, 2026-10-08): red when the lines the ground holds reach its
    ceiling less the kernel's reserve — the bodies' share spent, only the kernel's own left — so
    Resiliency sees the ground filling before Postgres refuses the next line (conformance `ground_watch`)."""
    return {"name": GROUND_WATCH, "metric": GROUND_WATCH, "op": ">=",
            "threshold": float(max(1, int(connections["ceiling"]) - int(connections["reserve"])))}


def watches_at_light(conn) -> list[str]:
    """The kernel's watches, once per world: the five `trust < 1.0` … — red when a measurement
    falls below the ideal; an unknown turns none red — and the ground's (`ground_connections >=
    ceiling − reserve`, the cure). Returns the names declared now."""
    from . import monitor, placement
    monitor.ensure_schema(conn)
    cur = conn.cursor()
    cur.execute("SELECT name FROM spine_watches WHERE scope = %s AND added_by = %s", (ev.universe(), KERNEL))
    have = {r[0] for r in cur.fetchall()}
    made = []
    for name in MEASUREMENTS:
        if name in have:
            continue
        w = measurement_watch(name)
        monitor.add_watch(conn, w["name"], w["metric"], w["op"], w["threshold"], KERNEL)
        made.append(name)
    if GROUND_WATCH not in have:
        w = ground_watch(placement.connections_declared(conn=conn))
        monitor.add_watch(conn, w["name"], w["metric"], w["op"], w["threshold"], KERNEL)
        made.append(GROUND_WATCH)
    return made


def intention_at_light(conn) -> dict:
    """THE OPERATING STATE declared beside Resiliency, once per world."""
    from . import intent
    return intent.declared(conn, OPERATING["words"], serves=OPERATING["serves"], kind="kernel", by=KERNEL,
                           interests=OPERATING["interests"], planner=OPERATING["planner"],
                           runner=OPERATING["runner"], watches=OPERATING["watches"])


# ---- feedback ------------------------------------------------------------------------------------

def give_feedback(conn, person: str, ask_id: str, sign: int, words: str | None = None) -> dict:
    """A human's thumb on a reply — routine, recorded, a fact; it feeds the Experience measurement
    and the grader's evidence, never a body directly (0010 §7: raw feedback never reaches a body)."""
    ensure_schema(conn)
    cur = conn.cursor()
    cur.execute("SELECT status, served_by FROM spine_asks WHERE ask_id = %s AND scope = %s", (ask_id, ev.universe()))
    r = cur.fetchone()
    if r is None:
        raise OperatingRefused("no such ask here")
    if r[0] != "replied":
        raise OperatingRefused(f"the ask is {r[0]} — a thumb goes on a reply")
    sign = 1 if int(sign) > 0 else -1 if int(sign) < 0 else 0
    fid = "fb_" + secrets.token_hex(6)
    with conn.transaction():
        c = conn.cursor()
        c.execute("INSERT INTO spine_feedback (feedback_id, scope, ask_id, person, sign, words) VALUES (%s, %s, %s, %s, %s, %s)",
                  (fid, ev.universe(), ask_id, person, sign, words))
        _fact(c, FEEDBACK_GIVEN, fid, {"ask": ask_id, "sign": sign, "words": words, "by": person, "served_by": r[1]}, [person])
    return {"feedback_id": fid, "ask_id": ask_id, "sign": sign,
            "words": "thank you — recorded; it feeds the Experience measurement and the grader's evidence, never a body directly"}


def feedback_on(conn, ask_id: str) -> list[dict]:
    cur = conn.cursor()
    cur.execute("SELECT feedback_id, person, sign, words, at FROM spine_feedback WHERE ask_id = %s ORDER BY at", (ask_id,))
    return [{"feedback_id": r[0], "person": r[1], "sign": r[2], "words": r[3], "at": r[4].isoformat()} for r in cur.fetchall()]


# ---- summon, generalized --------------------------------------------------------------------------

def summonable(conn, body: str) -> tuple[bool, str]:
    """May this body be summoned? Its template on the shelf declares `summonable` (firmware by
    declaration); MITL by its own toggle; a helper never (a life, not a self)."""
    from . import services
    if body == "mitl":
        return False, "MITL is summoned by its own word — say “summon MITL”"
    row = services.get(conn, f"{body}.template")
    if row is None or row["state"] == "retired":
        return False, f"no template named {body} stands on the shelf — only a body with a template is summoned"
    m = row["manifest"] or {}
    if m.get("kind") == "helper":
        return False, f"{body} is a helper — a life under its creator, never summoned (0010 §6)"
    if not m.get("summonable"):
        return False, f"{body}'s template does not declare it summonable — a cut of the template with `summonable: true` opens it"
    return True, "summonable"


def summon(conn, person: str, body: str, session: str | None = None, *, on: bool = True) -> dict:
    """The generalized toggle: a row, its marker (an action under the session's latest objective),
    its fact wearing the human's chain — summoned or dismissed, both recorded."""
    from . import markers, mitl
    ensure_schema(conn); markers.ensure_schema(conn); markers.seed(conn)
    body = str(body or "").strip().lower()
    ok, why = summonable(conn, body)
    if not ok:
        raise OperatingRefused(why)
    parent = mitl._latest_objective(conn, session)
    mid = markers.new_id()
    state = "summoned" if on else "dismissed"
    ref = session or person
    with conn.transaction():
        cur = conn.cursor()
        markers.insert(cur, mid, "action", parent, ref, person, f"{body} {state}")
        cur.execute("INSERT INTO spine_includes (scope, session, person, body, state, marker) VALUES (%s, %s, %s, %s, %s, %s)",
                    (ev.universe(), session, person, body, state, mid))
        _fact(cur, INCLUDE_SUMMONED if on else INCLUDE_DISMISSED, ref, {"by": person, "session": session, "body": body},
              [person], {"kind": "action", "id": mid, "parent": parent, "by": person})
    return {"summoned": on, "state": state, "body": body, "person": person, "session": session, "marker": mid,
            "words": summon_words(body, on, session)}


def summoned(conn, session: str | None = None, person: str | None = None) -> list[str]:
    """The bodies summoned into this session (or this person's crew outside any session) — the
    latest word per body decides."""
    ensure_schema(conn)
    cur = conn.cursor()
    if session:
        cur.execute("SELECT DISTINCT ON (body) body, state FROM spine_includes WHERE session = %s AND scope = %s"
                    " ORDER BY body, row_id DESC", (session, ev.universe()))
    else:
        cur.execute("SELECT DISTINCT ON (body) body, state FROM spine_includes WHERE session IS NULL AND person = %s"
                    " AND scope = %s ORDER BY body, row_id DESC", (person or "", ev.universe()))
    return sorted(b for b, st in cur.fetchall() if st == "summoned")


def includes(conn, session: str | None = None, person: str | None = None) -> list[str]:
    """The includes of a session: the four of the third kind, and every body summoned into it."""
    return list(BASE_INCLUDES) + [b for b in summoned(conn, session, person) if b not in BASE_INCLUDES]


# ---- the grade beat: the grader hears every live reply ----------------------------------------------

def grade_beat(conn, *, limit: int = GRADE_PER_BEAT) -> list[str]:
    """Under the `grade` beat: a body's reply of the last hour not yet graded is handed to the
    grader under the reply's own marker (an include's thought under a served ask's objective — the
    hull's event edge), a few per beat, never the reviewers' own words, never a grading ask."""
    import os
    from . import dispatch
    ensure_schema(conn)
    if os.environ.get(GRADE_DIAL, "1").strip() in ("0", "off", "no"):
        return []
    if dispatch.absent(conn, "grader"):
        return []
    u = ev.universe()
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT did FROM spine_joins WHERE name IN ('grader', 'critic') AND (scope = %s OR scope LIKE %s || '/%%')", (u, u))
    reviewers = [r[0] for r in cur.fetchall()] or ["-"]
    cur.execute(
        "SELECT a.ask_id, a.person, a.text, a.reply, coalesce(j.name, 'a body'), a.marker FROM spine_asks a"
        " LEFT JOIN LATERAL (SELECT name FROM spine_joins WHERE did = a.served_by ORDER BY join_id DESC LIMIT 1) j ON true"
        " WHERE a.scope = %s AND a.status = 'replied' AND a.reply IS NOT NULL AND a.served_by <> %s"
        " AND NOT (a.served_by = ANY(%s)) AND a.replied_at >= now() - make_interval(mins => %s)"
        " AND a.text NOT LIKE %s AND a.ask_id NOT IN (SELECT ask_id FROM spine_grading WHERE scope = %s)"
        " AND NOT EXISTS (SELECT 1 FROM spine_verdicts v WHERE v.on_ask = a.ask_id)"
        " ORDER BY a.replied_at LIMIT %s",
        (u, KERNEL, reviewers, GRADE_WINDOW_MIN, GRADE_HEAD + "%", u, limit))
    rows = cur.fetchall()
    asked = []
    from . import markers
    for ask_id, person, text, reply, who, marker in rows:
        # the GRADING marker under the reply's own ask: the grader's ask hangs under it, so the hull takes the
        # EVENT edge by law (an include's thought under a non-structural parent is an event)
        gm = markers.set_marker(conn, GRADING_KIND, ref=ask_id, by=KERNEL, parent=marker,
                                note=f"{who}'s reply handed to the grader")
        [gid] = dispatch.submit_ask(conn, grade_ask(ask_id, who, text, reply), person=person or KERNEL,
                                    to=["grader"], parent_marker=gm["id"])
        with conn.transaction():
            conn.cursor().execute("INSERT INTO spine_grading (ask_id, scope, grade_ask) VALUES (%s, %s, %s)"
                                  " ON CONFLICT (ask_id) DO NOTHING", (ask_id, u, gid))
        asked.append(f"{ask_id} by {who} → the grader ({gid})")
    return asked


def graded_ask_of(conn, ask_id: str) -> str | None:
    """The live reply a grading ask grades, when it is one (`spine_grading.grade_ask`)."""
    cur = conn.cursor()
    cur.execute("SELECT ask_id FROM spine_grading WHERE grade_ask = %s", (ask_id,))
    r = cur.fetchone()
    return r[0] if r else None


def live_verdicts(conn, ask_id: str) -> list[dict]:
    cur = conn.cursor()
    cur.execute("SELECT verdict_id, by_name, verdict, words, sig, at FROM spine_verdicts WHERE on_ask = %s ORDER BY at", (ask_id,))
    return [{"verdict_id": r[0], "by_name": r[1], "verdict": json.loads(r[2]), "words": r[3], "sig": r[4], "at": r[5].isoformat()}
            for r in cur.fetchall()]


# ---- the critic's proposal: the improvement loop closes in the Workshop -------------------------------

def owner_of(conn, agent: str) -> str | None:
    """The agent's owner: the person who promoted it (its seat), else the person who registered
    its template, else the world's owner."""
    from . import experiments, seat, services
    s = experiments.seat_of(conn, agent)
    if s and s.get("by") and s["by"].startswith("did:orreth:person:"):
        return s["by"]
    row = services.get(conn, f"{agent}.template")
    if row and str(row.get("by_did") or "").startswith("did:orreth:person:"):
        return row["by_did"]
    return seat.owner(conn)


def propose(conn, *, by: str, agent: str, kind: str, name: str, body: dict, words: str | None, marker: str | None) -> dict:
    """The critic's proposal: a DRAFT on the draft shelf under the AGENT'S OWNER, marked with the
    marker it came from — routine (L1); the owner opens it in the Workshop, cuts it, and the
    Experiment judges it. Its fact tells the owner's glass."""
    from . import crafts, markers
    owner = owner_of(conn, agent)
    if not owner:
        raise OperatingRefused(f"{agent} has no owner on this ground — no seat, no registrar, no world owner; nothing proposed")
    # the marker it came from: the IMPROVEMENT the critic was asked under (the critic's own ask hangs beneath it)
    mk = markers.get(conn, marker) if marker else None
    if mk and mk["kind"] != "improvement" and mk.get("parent"):
        up = markers.get(conn, mk["parent"])
        if up and up["kind"] == "improvement":
            marker = up["id"]
    tag = proposal_words(agent, name, kind, marker or "none")
    prior = next((d for d in crafts.drafts(conn, owner) if d["name"] == name and d["kind"] == kind), None)
    d = crafts.save_draft(conn, owner, kind, name, body, words=(f"{tag}" + (f": {words}" if words else "")),
                          draft_id=prior["draft_id"] if prior else None, from_marker=marker)
    with conn.transaction():
        _fact(conn.cursor(), DRAFT_PROPOSED, d["draft_id"],
              {"agent": agent, "owner": owner, "kind": kind, "name": name, "marker": marker, "by": by},
              [by], {"kind": "action", "id": marker, "parent": None, "by": by} if marker else None)
    return {"draft": d, "owner": owner, "words": tag}


# ---- import: a repo'd graph inside the hull -------------------------------------------------------

def import_home():
    import os
    from pathlib import Path
    return Path(os.environ.get("ORRETH_HOME", Path.home() / ".orreth")) / "imports"


def checkout(source: dict, home=None):
    """The repo at its commit, fetched once under the imports home (`<name>/<commit>`); a
    checkout that stands is reused."""
    import subprocess
    home = home or import_home()
    m = source["manifest"]
    repo, commit = str(m["repo"]), str(m["commit"])
    dest = home / source["name"] / commit
    if (dest / ".git").exists():
        return dest
    dest.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "clone", "--quiet", repo, str(dest)], check=True, capture_output=True, text=True, timeout=120)
    subprocess.run(["git", "-C", str(dest), "checkout", "--quiet", commit], check=True, capture_output=True, text=True, timeout=60)
    return dest


def run_import(conn, node: dict, text: str) -> tuple[str, str]:
    """An `import` node run: the source on the shelf (the repo form), its commit fetched, its
    entry `module:attr` loaded from the checkout and run — a compiled LangGraph (`.invoke({"text"})`
    → `reply`) or a callable of the words. Dev universes only. Returns (reply, the journey's words);
    a refusal is a CANNOT ACT reply, said."""
    import importlib
    import sys
    from . import levels, services
    name = str(node.get("source") or "")
    u = levels.row(conn, ev.universe())
    if str((u or {}).get("mode") or levels.MODE_DEFAULT) == "prod":
        return (f"CANNOT ACT: the imported graph {name} runs only in a dev universe at v0 — this universe is prod",
                f"import node {node.get('id')}: refused in prod")
    src = services.get(conn, name)
    if src is None or src["kind"] != "source" or src["state"] == "retired":
        return (f"CANNOT ACT: no standing source named {name!r} on the shelf — register it (repo · commit · entry) first",
                f"import node {node.get('id')}: no source {name!r}")
    m = src["manifest"] or {}
    if m.get("locator") or not m.get("repo"):
        return (f"CANNOT ACT: the source {name} is not a repo'd source (repo · commit · entry) — nothing to import",
                f"import node {node.get('id')}: {name} is not repo'd")
    entry = str(m.get("entry") or "")
    if ":" not in entry:
        return (f"CANNOT ACT: the source {name}'s entry {entry!r} is not module:attr", f"import node {node.get('id')}: bad entry")
    try:
        dest = checkout(src)
    except Exception as e:                                       # noqa: BLE001 — said, never a crash
        return (f"CANNOT ACT: the source {name} could not be fetched at {str(m['commit'])[:12]}: {type(e).__name__}: {str(e)[:200]}",
                f"import node {node.get('id')}: fetch failed")
    mod_name, attr = entry.split(":", 1)
    try:
        if str(dest) not in sys.path:
            sys.path.insert(0, str(dest))
        mod = importlib.import_module(mod_name)
        target = mod
        for part in attr.split("."):
            target = getattr(target, part)
        if hasattr(target, "invoke"):
            out = target.invoke({"text": text})
            reply = out.get("reply") if isinstance(out, dict) else None
            reply = str(reply if reply is not None else out)
        elif callable(target):
            reply = str(target(text))
        else:
            reply = str(target)
    except Exception as e:                                       # noqa: BLE001
        return (f"CANNOT ACT: the imported graph {name} ({entry}) failed: {type(e).__name__}: {str(e)[:300]}",
                f"import node {node.get('id')}: {entry} failed — {type(e).__name__}")
    return reply, import_words(name, str(m["commit"]), entry)
