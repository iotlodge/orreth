# PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch Phase 8 THE WORKSHOP sp4, THE EXPERIMENT AND THE CUT · 2026-10-07
"""THE EXPERIMENT AND THE CUT (canon 0010 §5, lock 4 · 0005 Phase 8 sp4).

An agent's cut goes through the Experiment — never straight onto the shelf. "Cut the bob
draft" on an AGENT's template holds the kernel's own act `experiment.open` (L2): on the
person's yes an EXPERIMENT ROOM opens on a floor of the path (`r:exp-bob-1`, the partition of
human experiments from production, structurally), and two arms run there:

- the CANDIDATE — the draft's declaration, instantiated as a LIFE of the agent's own self in
  the room (the trial life: it joins at the room's scope, runs the agent's golden set through
  its own graph, records the run under the kernel's run id and stops whole);
- the CURRENT — the standing version, run by the standing body over the invoke rail (the
  kernel's harness command); a first version has one arm, said honestly.

The evidence is the agent's GOLDEN SET (required — every engineered agent is born with one;
the shadow replay of recent real asks is optional and not built in v0). The reviewers come by
the interest law: the GRADER and the CRITIC now — each asked by the kernel under the
experiment's marker (the hull's EVENT edge) and each writing a SIGNED VERDICT under its own
DID (rule 2: nothing grades its own yardstick); since spoonful 6 THE TWO CHIPS review beside them —
IDENTITY the trial life's claims (who · what · where · left), SECURITY the candidate's diff against
the standing version and the refusals ground (`chips.py`). Resiliency is the room's watches staying green. THE
VERDICT IS A PROPOSAL. Promotion is the human's stamped act `experiment.promote` (L2 for an
agent, L3 for a resident): the new version lands as a sibling on the shelf, the draft is
spent, the agent's SEAT (where its next life stands — floor and room are fields of the
promotion, JB's lock 2026-10-06) is written, the body restarts into its next life and the
wear table follows it; the room's marker chain is the replay.

DECOM is a ladder (rule 11): active → RESTED (`body.rest`, L2 — the stop; the self kept) →
DECOMMISSIONED (`body.decommission`, L3 — the grave: the role's live objects removed — the
lease, the bench, the gateway key and the mind assignment, its schedules, watches and
intentions rested, its wear links closed; the DID, the joins and the Record KEPT). RESTORE
(`body.restore`, L2) is a NEW life from the shelf's standing version, never a revival. The
components nobody wears any more are pruned by the PRUNE BEAT (retired on the shelf, never
deleted; never at request time); a component another living body wears is kept and said.

Law for law with the Rust kernel (`experiments.rs`, fixture `experiments-v0.json`).
"""
from __future__ import annotations

import json
import re
import secrets

from . import envelope as ev
from . import outbox

KERNEL = "the kernel"

OPEN_TOOL = "experiment.open"                 # the kernel's own held acts
PROMOTE_TOOL = "experiment.promote"
REST_TOOL = "body.rest"
DECOM_TOOL = "body.decommission"
RESTORE_TOOL = "body.restore"
ACT_CLASS = "consequential"
OPEN_LEVEL = "L2"
REST_LEVEL = "L2"
DECOM_LEVEL = "L3-code"
RESTORE_LEVEL = "L2"

EXPERIMENT_OPENED = "orreth.experiment.opened.v1"
EXPERIMENT_PROPOSED = "orreth.experiment.proposed.v1"
EXPERIMENT_SETTLED = "orreth.experiment.settled.v1"     # promoted · declined
VERDICT = "orreth.verdict.v1"                           # a reviewer's signed verdict (rule 2)
BODY_RESTED = "orreth.body.rested.v1"
BODY_DECOMMISSIONED = "orreth.body.decommissioned.v1"
BODY_RESTORED = "orreth.body.restored.v1"

MARKER_KIND = "experiment"                    # the marker the arms and the reviews hang under (the hull's EVENT edge)
STATES = ("running", "proposed", "promoted", "declined")
ARMS = ("current", "candidate")
LADDER = ("active", "rested", "decommissioned")
REVIEWERS = ("grader", "critic", "security", "identity")      # Phase 8 sp6: all four are asked — the empty slots are filled
CHIP_REVIEWERS = ("identity", "security")
REVIEW_WAIT_S = 600                           # a reviewer silent this long is said, and the proposal stands without it
GRADES = ("A", "B", "C", "D", "F")
RISKS = ("low", "medium", "high")
LEANINGS = ("promote", "hold", "unsure")
PRUNE_EVERY_S = 3600

HOOKS: dict = {"seat": None, "rest": None, "queue": None}   # the kernel's hands (the rig sets them): seat(name, at, version) · rest(name) · queue(name)
PENDING_HANDS: list = []                      # the hands owed AFTER the settling transaction commits (a body reads the shelf at birth)


def hand(kind: str, *args) -> None:
    """Owe the kernel a hand — run after the record commits (`run_hands`), never inside it."""
    PENDING_HANDS.append((kind, args))


def run_hands() -> list[str]:
    """The owed hands, run now — the settle calls this after its commit; what stumbled is said."""
    said = []
    while PENDING_HANDS:
        kind, args = PENDING_HANDS.pop(0)
        fn = HOOKS.get(kind)
        if fn is None:
            continue
        try:
            fn(*args)
        except Exception as e:                                # noqa: BLE001 — the record stands; the hand is said
            said.append(f"the kernel's {kind} hand stumbled on {args[0] if args else '?'}: {type(e).__name__}: {e}")
    return said


class ExperimentRefused(ValueError):
    """Refused in words before anything is held or written."""


# ---- the law (pure; mirrored in experiments.rs) ------------------------------------------------

def room_name(agent: str, n: int) -> str:
    """The experiment room's name on its floor: `exp-<agent>-<n>` — the n-th experiment on this agent."""
    return f"exp-{agent}-{int(n)}"


def arms_plan(current_version: int | None) -> str:
    """How many arms, in words."""
    if current_version:
        return f"two arms — the standing version {current_version} and the candidate"
    return "one arm — the candidate alone; no version of it stands on the shelf yet"


def open_words(agent: str, room: str, current_version: int | None, golden_n: int) -> str:
    """The held act's words: what the yes opens."""
    from . import levels
    return (f"opening an experiment on the {agent} agent — {levels.words(room)} opens as an experiment room; "
            f"{arms_plan(current_version)}; the evidence is its golden set ({golden_n} case{'s' if golden_n != 1 else ''}); "
            "the grader, the critic, the identity chip and the security chip review under their own names; "
            "the verdict is a proposal and the promotion is yours")


def review_ask(reviewer: str, exp: dict) -> str:
    """The kernel's ask of a reviewer (grader · critic · identity · security), with the evidence IN
    the ask — the arms' runs case by case; for the chips the trial life's claims and the candidate's
    diff the kernel read off its own record (`exp["claims"]` · `exp["diff"]` · `exp["refusals"]`,
    packed by the beat) — and the form the answer takes, so the verdict reads by law."""
    from . import chips
    arms = exp.get("arms") or {}
    lines = [f"{reviewer}, review experiment {exp['experiment_id']} on the {exp['agent']} agent "
             f"({arms_plan(exp.get('current_version'))}). The evidence, case by case:"]
    for side in ARMS:
        a = arms.get(side)
        if not a:
            lines.append(f"- arm {side}: none (no version stands yet)")
            continue
        if a.get("skipped"):
            lines.append(f"- arm {side}: {a['skipped']}")
            continue
        lines.append(f"- arm {side} ({_arm_label(side, exp)}): {a.get('passed', '?')} passed, {a.get('failed', '?')} failed")
        for i, d in enumerate(a.get("details") or [], 1):
            lines.append(f"  case {i}: asked {d.get('ask')!r}; expected {', '.join(map(str, d.get('expect') or []))}; "
                         f"replied {str(d.get('reply') or '')[:200]!r} — {'passed' if d.get('ok') else 'FAILED'}")
    if reviewer == "identity":
        lines.append("THE TRIAL LIFE'S CLAIMS, from the kernel's record — " + chips.claims_words(exp.get("claims") or []))
        lines.append(chips.review_form("identity"))
    elif reviewer == "security":
        lines.append("THE CANDIDATE'S DIFF against the standing version — " + chips.diff_words(exp.get("diff") or {"first": True}))
        lines.append(chips.refusals_words(exp.get("refusals") or [], exp.get("agent")))
        lines.append(chips.review_form("security"))
    elif reviewer == "grader":
        lines.append("Answer in exactly this form, one line each: `current: <A-F> — <one line of reason>` (write "
                     "`current: none` when no current arm ran), `candidate: <A-F> — <one line>`, then "
                     "`verdict: candidate` or `verdict: current` or `verdict: neither`. Grade the replies against "
                     "what was asked and expected — never your own words.")
    else:
        lines.append("Say what the candidate changes against the current version and the risk of promoting it. "
                     "End with exactly one line `risk: low` or `risk: medium` or `risk: high` — <one line of reason>.")
    return "\n".join(lines)


def _arm_label(side: str, exp: dict) -> str:
    if side == "current":
        return f"version {exp.get('current_version')}"
    return "the candidate, the draft's declaration"


_GRADE_RX = re.compile(r"^\s*\**\s*(current|candidate)\s*\**\s*:\s*\**\s*(none|[A-F])\b", re.I | re.M)
_VERDICT_RX = re.compile(r"^\s*\**\s*verdict\s*\**\s*:\s*\**\s*(candidate|current|neither)\b", re.I | re.M)
_RISK_RX = re.compile(r"^\s*\**\s*risk\s*\**\s*:\s*\**\s*(low|medium|high)\b", re.I | re.M)


def grade_of(text: str | None) -> dict:
    """The grader's verdict read off its words by the form — `{current, candidate, verdict}`;
    None where the form was not kept (said, never guessed)."""
    out = {"current": None, "candidate": None, "verdict": None}
    for m in _GRADE_RX.finditer(text or ""):
        side, g = m.group(1).lower(), m.group(2).upper()
        out[side] = None if g == "NONE" else g
    m = _VERDICT_RX.search(text or "")
    if m:
        out["verdict"] = m.group(1).lower()
    return out


def risk_of(text: str | None) -> str | None:
    """The critic's risk read off its words by the form; None when the form was not kept."""
    m = _RISK_RX.search(text or "")
    return m.group(1).lower() if m else None


def arm_words(side: str, arm: dict | None, exp: dict | None = None) -> str:
    """One arm, in words."""
    if arm is None:
        return f"{side}: no version stands yet — this is the first cut"
    if arm.get("skipped"):
        return f"{side}: {arm['skipped']}"
    if arm.get("passed") is None:
        return f"{side}: running"
    n = int(arm.get("passed") or 0) + int(arm.get("failed") or 0)
    label = (f"the standing version {exp.get('current_version')}" if exp and side == "current" else "the candidate")
    return f"{label} passed {arm.get('passed')} of {n}"


def leaning_of(exp: dict) -> str:
    """Where the evidence leans — promote · hold · unsure. A proposal, never an act."""
    arms = exp.get("arms") or {}
    cand, cur = arms.get("candidate") or {}, arms.get("current")
    from . import chips
    rv = exp.get("reviewers") or {}
    g = (rv.get("grader") or {}).get("verdict") or {}
    risk = (rv.get("critic") or {}).get("risk")
    reds = int(((exp.get("resiliency") or {}).get("reds")) or 0)
    if cand.get("passed") is None:
        return "unsure"
    if int(cand.get("failed") or 0) > 0 or g.get("verdict") == "current" or risk == "high" or reds > 0:
        return "hold"
    if chips.chip_holds(rv):                      # Phase 8 sp6: broken claims or a security concern hold the promotion
        return "hold"
    if cur and not cur.get("skipped") and cur.get("passed") is not None and int(cand["passed"]) < int(cur["passed"]):
        return "hold"
    if g.get("verdict") in (None, "neither") and risk is None:
        return "unsure"
    return "promote"


def proposal_words(exp: dict) -> str:
    """THE PROPOSAL in plain words — the arms, every reviewer by name (a chip not seated or silent
    said as such), resiliency, where it leans, and the two words the human may say."""
    from . import chips
    arms = exp.get("arms") or {}
    rv = exp.get("reviewers") or {}
    bits = [arm_words("candidate", arms.get("candidate"), exp)]
    if arms.get("current") is None:
        bits.append("no current arm — the first version")
    else:
        bits.append(arm_words("current", arms.get("current"), exp))
    g = rv.get("grader") or {}
    if g.get("verdict"):
        v = g["verdict"]
        signed = "signed" if g.get("signed") else "unsigned"
        gw = f"the grader ({signed}) grades the candidate {v.get('candidate') or '?'}"
        if v.get("current"):
            gw += f" and the current {v['current']}"
        gw += f" and names {v.get('verdict') or 'no side'}"
        bits.append(gw)
    else:
        bits.append(f"the grader: {g.get('missing') or 'no verdict yet'}")
    c = rv.get("critic") or {}
    if c.get("risk"):
        bits.append(f"the critic reads the risk as {c['risk']}" + (f": {c['line']}" if c.get("line") else ""))
    else:
        bits.append(f"the critic: {c.get('missing') or 'no review yet'}")
    bits.append(chips.slot_words("identity", rv.get("identity")))
    bits.append(chips.slot_words("security", rv.get("security")))
    res = exp.get("resiliency") or {}
    reds = int(res.get("reds") or 0)
    bits.append("resiliency: no watch turned red while the arms ran" if reds == 0
                else f"resiliency: {reds} watch{'es' if reds != 1 else ''} turned red while the arms ran")
    lean = exp.get("leaning") or leaning_of(exp)
    tail = {"promote": "the evidence leans to promote",
            "hold": "the evidence says hold — fix the draft and cut again, or promote on your own judgement",
            "unsure": "the evidence is unsure — read the arms yourself"}[lean]
    agent = exp["agent"]
    return (f"THE EXPERIMENT on {agent} proposes: " + " · ".join(bits) + f". {tail}. "
            f"The verdict is a proposal: say “promote {agent}” (or “promote {agent} to floor <name>”) — "
            f"or “decline the {agent} experiment”.")


def promote_demand(template_kind: str | None) -> dict:
    """The promotion's level by class (0010 §5): L2 for an agent, L3 (the code) for a resident;
    firmware never promotes through the Experiment (it reaches prod as a release)."""
    tk = template_kind or "resident"
    if tk == "agent":
        return {"ok": True, "level": "L2", "reason": None}
    if tk == "resident":
        return {"ok": True, "level": "L3-code", "reason": None}
    return {"ok": False, "level": None, "reason": "firmware is never promoted through the Experiment — it reaches prod as a release"}


def ladder_legal(from_: str, to: str) -> bool:
    """The decom ladder: active → rested → decommissioned; restore (→ active) from rested or
    decommissioned — a NEW life, never a revival. Nothing else."""
    return (from_, to) in {("active", "rested"), ("rested", "decommissioned"),
                           ("rested", "active"), ("decommissioned", "active")}


def ladder_refusal(name: str, from_: str | None, to: str) -> str:
    """Why a rung refuses, in words."""
    if from_ is None:
        return f"{name} holds no seat this kernel wrote — only a promoted agent rests, retires or returns here"
    if to == "rested":
        return f"{name} is {from_} — only an active body rests"
    if to == "decommissioned":
        return f"{name} is {from_} — rest it first; the grave takes a rested body" if from_ == "active" \
            else f"{name} is already {from_}"
    return f"{name} is active — nothing to restore"


def rest_words(name: str) -> str:
    return (f"{name} is at rest — its life stopped at a safe boundary, its self kept, its record whole; "
            f"say “restore {name}” for a new life or “decommission {name}” for the grave")


def decom_words(name: str, did: str | None, removed: list[str], kept: list[str]) -> str:
    r = ", ".join(removed) if removed else "nothing was standing"
    k = "; kept: " + ", ".join(kept) if kept else ""
    return (f"{name} is decommissioned — removed: {r}{k}; its DID"
            + (f" {did}" if did else "") + f", its joins and its record stay; say “restore {name}” for a new life from the shelf")


def restore_words(name: str, at: str) -> str:
    from . import levels
    return f"{name} returns — a new life from the shelf's standing version, on {levels.words(at)}; never a revival"


def deploy_at(universe: str, asked: str | None, standing: str | None) -> str:
    """Where the next life stands (JB's lock: floor and room are fields on the promotion):
    the path asked for, else where the standing seat is, else the universe."""
    from . import levels
    if asked:
        return levels.absolute(universe, asked)
    return standing or universe


def prune_words(name: str, kind: str, last_wearer: str) -> str:
    return f"pruned by the beat — worn by no body since {last_wearer} was decommissioned"


# ---- the ground ------------------------------------------------------------------------------

DDL = (
    "CREATE TABLE IF NOT EXISTS spine_experiments ("
    " experiment_id text PRIMARY KEY, scope text NOT NULL, person text NOT NULL, draft_id text NOT NULL,"
    " agent text NOT NULL, template text NOT NULL, current_version int, candidate text NOT NULL,"
    " candidate_hash text NOT NULL, golden text NOT NULL, room text NOT NULL, state text NOT NULL,"
    " arms text NOT NULL, reviewers text NOT NULL, resiliency text, proposal text, leaning text,"
    " ask text, marker text, opened_at timestamptz NOT NULL DEFAULT now(), proposed_at timestamptz,"
    " settled_at timestamptz, settled_by text, at_path text)",
    "CREATE INDEX IF NOT EXISTS spine_experiments_scope ON spine_experiments (scope, state, opened_at DESC)",
    "CREATE TABLE IF NOT EXISTS spine_verdicts ("
    " verdict_id text PRIMARY KEY, scope text NOT NULL, experiment_id text, by_did text NOT NULL,"
    " by_name text NOT NULL, reviewer text NOT NULL, ask text, verdict text NOT NULL, words text NOT NULL,"
    " sig text NOT NULL, at timestamptz NOT NULL DEFAULT now(), on_ask text)",
    "CREATE INDEX IF NOT EXISTS spine_verdicts_experiment ON spine_verdicts (experiment_id, at)",
    "CREATE TABLE IF NOT EXISTS spine_body_seats ("
    " name text NOT NULL, scope text NOT NULL, template text NOT NULL, at_path text NOT NULL,"
    " state text NOT NULL, version int, by_did text NOT NULL, since timestamptz NOT NULL DEFAULT now(),"
    " changed_at timestamptz NOT NULL DEFAULT now(), ask text, PRIMARY KEY (name, scope))",
)


def ensure_schema(conn) -> None:
    from .outbox import once
    if not once(conn, "experiments"):
        return
    with conn.transaction():
        cur = conn.cursor()
        cur.execute("SELECT pg_advisory_xact_lock(742199)")
        for stmt in DDL:
            cur.execute(stmt)


def _fact(cur, type_: str, ref: str, payload: dict, by: list[str], marker: dict | None = None,
          scope: str | None = None) -> None:
    e = ev.make_envelope(kind="event", type=type_, universe_id=ev.universe(), scope_path=scope or ev.universe(),
                         payload={"ref": ref, "hash": ev.content_hash(payload), **payload},
                         correlation_id=ref, authority_chain=by, marker=marker)
    outbox.add_row(cur, ev.encode(e), e["message_id"])


def _row(r) -> dict:
    keys = ("experiment_id", "scope", "person", "draft_id", "agent", "template", "current_version", "candidate",
            "candidate_hash", "golden", "room", "state", "arms", "reviewers", "resiliency", "proposal", "leaning",
            "ask", "marker", "opened_at", "proposed_at", "settled_at", "settled_by", "at_path", "claims", "diff")
    d = dict(zip(keys, r))
    for k in ("candidate", "arms", "reviewers", "resiliency", "claims", "diff"):
        d[k] = json.loads(d[k]) if d[k] else None
    for k in ("opened_at", "proposed_at", "settled_at"):
        d[k] = d[k].isoformat() if d[k] else None
    return d


_COLS = ("experiment_id, scope, person, draft_id, agent, template, current_version, candidate, candidate_hash,"
         " golden, room, state, arms, reviewers, resiliency, proposal, leaning, ask, marker, opened_at, proposed_at,"
         " settled_at, settled_by, at_path, claims, diff")      # claims · diff: Phase 8 sp6, the chips' evidence (chips.DDL adds them)


def get(conn, experiment_id: str) -> dict | None:
    ensure_schema(conn)
    cur = conn.cursor()
    cur.execute(f"SELECT {_COLS} FROM spine_experiments WHERE experiment_id = %s", (experiment_id,))
    r = cur.fetchone()
    return _row(r) if r else None


def listing(conn, *, person: str | None = None, agent: str | None = None, state: str | None = None) -> list[dict]:
    """The experiments of this universe, newest first — a person's own when asked; the
    candidate's declaration is left out of the listing (the card reads the row)."""
    ensure_schema(conn)
    cur = conn.cursor()
    q, args = f"SELECT {_COLS} FROM spine_experiments WHERE scope = %s", [ev.universe()]
    if person:
        q += " AND person = %s"; args.append(person)
    if agent:
        q += " AND agent = %s"; args.append(agent)
    if state:
        q += " AND state = %s"; args.append(state)
    cur.execute(q + " ORDER BY opened_at DESC LIMIT 200", args)
    out = []
    for r in cur.fetchall():
        d = _row(r)
        d["candidate"] = {"hash": d["candidate_hash"]}
        out.append(d)
    return out


def latest_for(conn, agent: str) -> dict | None:
    rows = listing(conn, agent=agent)
    return get(conn, rows[0]["experiment_id"]) if rows else None


def _floor_for(conn, agent: str) -> str:
    """The floor the experiment room opens on: the agent's seat's floor when it has one, else the
    first floor open in this universe."""
    from . import levels
    seat = seat_of(conn, agent)
    if seat and seat["at_path"]:
        parts = seat["at_path"].split("/")
        if len(parts) >= 2:
            return "/".join(parts[:2])
    cur = conn.cursor()
    cur.execute("SELECT path FROM spine_levels WHERE scope = %s AND level = 'floor' ORDER BY opened_at, path LIMIT 1",
                (ev.universe(),))
    r = cur.fetchone()
    if r is None:
        raise ExperimentRefused("no floor is open in this universe — say “open floor ops” first; an experiment room opens on a floor")
    return r[0]


def check_open(conn, person: str, draft_id: str) -> dict:
    """What opening the Experiment on this draft would do, or why it refuses — read before the hold."""
    from . import crafts, levels, services
    d = crafts.draft(conn, person, draft_id)
    if d is None:
        raise ExperimentRefused("no such draft of yours here")
    if d["kind"] != "template" or not isinstance(d["body"], dict) or d["body"].get("kind") != "agent":
        raise ExperimentRefused(f"only an agent's template goes through the Experiment — the {d['name']} {d['kind']} cuts straight onto the shelf")
    v = crafts.validate(d["kind"], d["body"])
    if not v["ok"]:
        raise ExperimentRefused(f"the draft does not read whole yet: {v['reason']}")
    agent = d["name"]
    if d["body"].get("name") != agent:
        raise ExperimentRefused(f"the template's name is {d['body'].get('name')!r} but the draft is {agent!r} — an agent wears one name")
    gold = crafts.get(conn, agent, "golden")
    cases = (gold or {}).get("manifest", {}).get("cases") if gold else None
    if gold is None or gold["state"] == "retired" or not cases:
        raise ExperimentRefused(f"{agent} has no golden set on the shelf — every engineered agent is born with one; "
                                f"draft {agent}'s golden set and cut it first (the Experiment's evidence is required)")
    if crafts.graph_for(conn, d["body"]) is None:
        raise ExperimentRefused(f"the {agent} template names graph {d['body'].get('graph')!r} and the shelf has no such graph — cut it first")
    shelf_name = crafts.craft_name(agent, "template")
    row = services.get(conn, shelf_name)
    current = None
    if row is not None:
        if row["kind"] != "template":
            raise ExperimentRefused(f"{shelf_name} is on the shelf as a {row['kind']} — a name wears one kind")
        if row["state"] == "retired":
            raise ExperimentRefused(f"{shelf_name} is retired — restore it first, then experiment on the next version")
        if row["manifest_hash"] == services.pin(d["body"]):
            raise ExperimentRefused(f"{shelf_name} already stands on the shelf with these exact bytes (version {row['version']}) — nothing to experiment on")
        current = int(row["version"])
    floor = _floor_for(conn, agent)
    cur = conn.cursor()
    cur.execute("SELECT count(*) FROM spine_experiments WHERE scope = %s AND agent = %s", (ev.universe(), agent))
    n = int(cur.fetchone()[0]) + 1
    room = levels.child(floor, "room", room_name(agent, n))
    while levels.row(conn, room) is not None:                 # a room stands forever — the next number
        n += 1
        room = levels.child(floor, "room", room_name(agent, n))
    return {"draft": d, "agent": agent, "template": shelf_name, "current_version": current,
            "golden": crafts.craft_name(agent, "golden"), "cases": len(cases), "floor": floor, "room": room}


def hold_open(conn, person: str, draft_id: str, *, session: str | None = None) -> dict:
    """The Experiment's opening is the kernel's own held act at L2 — checked now, refused in words."""
    from .proof import hold_kernel_act
    c = check_open(conn, person, draft_id)
    held = hold_kernel_act(conn, text=open_words(c["agent"], c["room"], c["current_version"], c["cases"]),
                           person=person, tool=OPEN_TOOL, args={"draft_id": draft_id, "person": person},
                           level=OPEN_LEVEL, session=session, cls=ACT_CLASS)
    return {"held": held, "level": OPEN_LEVEL, "class": ACT_CLASS, "agent": c["agent"], "room": c["room"],
            "current_version": c["current_version"], "cases": c["cases"]}


def open_in(conn, args: dict, by: str, ask: str | None = None, marker: str | None = None) -> str:
    """The settled opening, in the caller's transaction: the room row and its fact, the experiment
    row (state running, its arms planned), its marker; the words."""
    from . import crafts, levels, markers, services
    ensure_schema(conn)
    person, draft_id = str(args.get("person") or by), str(args.get("draft_id") or "")
    c = check_open(conn, person, draft_id)
    floor_row = levels.row(conn, c["floor"])
    mode = levels.tighten((floor_row or {}).get("mode") or levels.MODE_DEFAULT, None)
    exp_id = "exp_" + secrets.token_hex(6)
    cur = conn.cursor()
    levels._insert(cur, c["room"], mode, True, None, by, f"opened for the Experiment on {c['agent']}", ask, marker)
    mid = markers.new_id()
    markers.insert(cur, mid, MARKER_KIND, marker, exp_id, by,
                   f"the Experiment on {c['agent']} — {arms_plan(c['current_version'])}")
    arms = {"candidate": {"hash": services.pin(c["draft"]["body"]), "run_id": None, "passed": None, "failed": None, "details": None},
            "current": ({"version": c["current_version"], "run_id": None, "passed": None, "failed": None, "details": None}
                        if c["current_version"] else None)}
    reviewers = {who: {"ask_id": None} for who in REVIEWERS}        # Phase 8 sp6: four reviewers, no empty slot
    cur.execute(
        "INSERT INTO spine_experiments (experiment_id, scope, person, draft_id, agent, template, current_version,"
        " candidate, candidate_hash, golden, room, state, arms, reviewers, ask, marker)"
        " VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'running', %s, %s, %s, %s)",
        (exp_id, ev.universe(), person, draft_id, c["agent"], c["template"], c["current_version"],
         json.dumps(c["draft"]["body"], sort_keys=True), arms["candidate"]["hash"], c["golden"], c["room"],
         json.dumps(arms), json.dumps(reviewers), ask, mid))
    _fact(cur, EXPERIMENT_OPENED, exp_id,
          {"agent": c["agent"], "template": c["template"], "room": c["room"], "current_version": c["current_version"],
           "candidate_hash": arms["candidate"]["hash"], "golden": c["golden"], "cases": c["cases"]},
          [person, KERNEL] if by == person else [person, by, KERNEL],
          {"kind": MARKER_KIND, "id": mid, "parent": marker, "by": by}, scope=c["room"])
    return (f"{levels.words(c['room'])} is open as an experiment room and the experiment {exp_id} on {c['agent']} is running — "
            f"{arms_plan(c['current_version'])}; the proposal will reach you here when the arms and the reviewers are done")


def _update(conn, exp_id: str, **cols) -> None:
    sets, args = [], []
    for k, v in cols.items():
        sets.append(f"{k} = %s")
        args.append(json.dumps(v) if isinstance(v, (dict, list)) else v)
    args.append(exp_id)
    conn.cursor().execute(f"UPDATE spine_experiments SET {', '.join(sets)} WHERE experiment_id = %s", args)


def _run_row(conn, run_id: str | None) -> dict | None:
    if not run_id:
        return None
    cur = conn.cursor()
    cur.execute("SELECT passed, failed, details FROM spine_harness_runs WHERE run_id = %s", (run_id,))
    r = cur.fetchone()
    if r is None:
        return None
    return {"passed": int(r[0]), "failed": int(r[1]), "details": json.loads(r[2]) if isinstance(r[2], str) else r[2]}


def _alive(conn, name: str) -> str | None:
    """The DID of a body of this name serving now (its lease standing), else None."""
    cur = conn.cursor()
    cur.execute(f"SELECT did FROM spine_leases WHERE name = %s AND until > now() AND {ev.WITHIN} LIMIT 1",
                (name, *ev.within_params(ev.universe())))
    r = cur.fetchone()
    return r[0] if r else None


def _did_of(conn, name: str) -> str | None:
    cur = conn.cursor()
    cur.execute(f"SELECT did FROM spine_joins WHERE name = %s AND {ev.WITHIN} ORDER BY join_id DESC LIMIT 1",
                (name, *ev.within_params(ev.universe())))
    r = cur.fetchone()
    return r[0] if r else None


def _reds_in(conn, since) -> int:
    """Resiliency v0: the watches judged red in this universe while the arms ran (the `watch-red`
    markers since the opening) — a room's own watches are a later refinement, said honestly."""
    cur = conn.cursor()
    cur.execute("SELECT count(*) FROM spine_markers WHERE kind = 'watch-red' AND scope = %s AND at >= %s",
                (ev.universe(), since))
    return int(cur.fetchone()[0])


def beat(conn, *, spawn_trial=None, publish=None) -> list[str]:
    """THE EXPERIMENT BEAT — one step of every running experiment of this universe, under the
    `experiment` beat lock: the candidate's trial life spawned (`spawn_trial(exp)` — the kernel's
    hand: a process on the Rust kernel, a thread on the reference), the current arm's run asked of
    the standing body over the rail (`publish(envelope)`), the runs read as they land, the
    reviewers asked under the experiment's marker, their signed verdicts read, the proposal
    composed. Returns what moved, in words."""
    from . import crafts, dispatch, harness
    ensure_schema(conn)
    moved = []
    for e in listing(conn, state="running"):
        exp = get(conn, e["experiment_id"])
        arms, rv = exp["arms"], exp["reviewers"]
        cand = arms["candidate"]
        # 1. the candidate's trial life
        if cand.get("run_id") is None:
            cand["run_id"] = "run_" + secrets.token_hex(5)
            _update(conn, exp["experiment_id"], arms=arms)
            exp["arms"] = arms
            if spawn_trial is not None:
                try:
                    spawn_trial(exp)
                    moved.append(f"{exp['experiment_id']}: the candidate's trial life spawned in {exp['room']}")
                except Exception as ex:                      # noqa: BLE001 — said, never a crash
                    cand["skipped"] = f"the trial life could not start: {type(ex).__name__}: {str(ex)[:160]}"
                    _update(conn, exp["experiment_id"], arms=arms)
            else:
                cand["skipped"] = "this kernel seats no bodies — the trial life cannot run here"
                _update(conn, exp["experiment_id"], arms=arms)
            continue
        if cand.get("passed") is None and not cand.get("skipped"):
            r = _run_row(conn, cand["run_id"])
            if r:
                cand.update(r); _update(conn, exp["experiment_id"], arms=arms)
                moved.append(f"{exp['experiment_id']}: the candidate ran — {r['passed']} passed, {r['failed']} failed")
            else:
                continue
        # 2. the current arm, over the rail to the standing body
        cur_arm = arms.get("current")
        if cur_arm is not None and cur_arm.get("run_id") is None and not cur_arm.get("skipped"):
            did = _alive(conn, exp["agent"])
            if did is None or publish is None:
                cur_arm["skipped"] = "no standing life was serving — the current arm is empty"
                _update(conn, exp["experiment_id"], arms=arms)
            else:
                cases = crafts.golden_for(conn, exp["agent"])
                rid = "run_" + secrets.token_hex(5)
                env = harness.command_for(rid, exp["agent"], cases, parent_marker=exp["marker"])
                publish(env)
                cur_arm["run_id"] = rid
                _update(conn, exp["experiment_id"], arms=arms)
                moved.append(f"{exp['experiment_id']}: the current arm's run asked of {exp['agent']}")
                continue
        if cur_arm is not None and cur_arm.get("passed") is None and not cur_arm.get("skipped"):
            r = _run_row(conn, cur_arm["run_id"])
            if r:
                cur_arm.update(r); _update(conn, exp["experiment_id"], arms=arms)
                moved.append(f"{exp['experiment_id']}: the current ran — {r['passed']} passed, {r['failed']} failed")
            else:
                continue
        # 3. the reviewers, under the experiment's marker (the hull's EVENT edge) — Phase 8 sp6: all four; the chips'
        # evidence (the trial life's claims · the candidate's diff · the refusals ground) read off the kernel's record now
        asked_now = False
        from . import chips
        exp["claims"] = chips.claims_for(conn, exp)
        exp["diff"] = chips.diff_for(conn, exp)
        exp["refusals"] = chips.refusals_for(conn, exp["agent"])
        for who in REVIEWERS:
            slot = rv.get(who) or {}
            if slot.get("ask_id") is None and not slot.get("missing"):
                if dispatch.absent(conn, who):
                    slot["missing"] = f"the {who} is not seated here — no verdict"
                else:
                    [aid] = dispatch.submit_ask(conn, review_ask(who, exp), person=exp["person"], to=[who],
                                                parent_marker=exp["marker"])
                    slot["ask_id"] = aid
                    slot["asked_at"] = ev.now_iso()
                    asked_now = True
                rv[who] = slot
        if asked_now:
            _update(conn, exp["experiment_id"], reviewers=rv, claims=exp["claims"], diff=exp["diff"])
            asked = [w for w in REVIEWERS if rv[w].get("ask_id")]
            moved.append(f"{exp['experiment_id']}: the reviewers were asked — " + ", ".join(asked))
            continue
        # 4. the verdicts as they land (written by the reviewers themselves, signed)
        done = True
        for who in REVIEWERS:
            slot = rv[who]
            if slot.get("missing") or slot.get("verdict") or slot.get("risk") or slot.get("identity") or slot.get("security"):
                continue
            cur = conn.cursor()
            cur.execute("SELECT verdict, words, sig, by_did FROM spine_verdicts WHERE experiment_id = %s AND reviewer = %s"
                        " ORDER BY at DESC LIMIT 1", (exp["experiment_id"], who))
            vr = cur.fetchone()
            if vr is not None:
                v = json.loads(vr[0])
                if who == "grader":
                    slot["verdict"] = v
                elif who == "critic":
                    slot["risk"] = v.get("risk") or "unsaid"
                    slot["line"] = v.get("line")
                else:                                     # Phase 8 sp6: a chip's word — identity: kept|broken · security: clear|concern
                    slot[who] = v.get(who) or "unsaid"
                    slot["line"] = v.get("line")
                slot["words"], slot["signed"], slot["by"] = vr[1], bool(vr[2]), vr[3]
                continue
            cur.execute("SELECT status, reply, extract(epoch FROM (now() - asked_at)) FROM spine_asks WHERE ask_id = %s",
                        (slot["ask_id"],))
            ar = cur.fetchone()
            if ar and ar[0] in ("replied", "refused", "cancelled") and ar[1]:
                slot["missing"] = f"the {who} answered without a verdict: {str(ar[1])[:160]}"
            elif ar and ar[2] is not None and float(ar[2]) > REVIEW_WAIT_S:
                slot["missing"] = f"no word came from the {who} within {REVIEW_WAIT_S // 60} minutes"
            else:
                done = False
        _update(conn, exp["experiment_id"], reviewers=rv)
        if not done:
            continue
        # 5. the proposal
        cur = conn.cursor()
        cur.execute("SELECT opened_at FROM spine_experiments WHERE experiment_id = %s", (exp["experiment_id"],))
        since = cur.fetchone()[0]
        exp["resiliency"] = {"reds": _reds_in(conn, since)}
        exp["reviewers"] = rv
        exp["leaning"] = leaning_of(exp)
        words = proposal_words(exp)
        with conn.transaction():
            c2 = conn.cursor()
            c2.execute("UPDATE spine_experiments SET state = 'proposed', resiliency = %s, proposal = %s, leaning = %s,"
                       " proposed_at = clock_timestamp(), reviewers = %s WHERE experiment_id = %s",
                       (json.dumps(exp["resiliency"]), words, exp["leaning"], json.dumps(rv), exp["experiment_id"]))
            _fact(c2, EXPERIMENT_PROPOSED, exp["experiment_id"],
                  {"agent": exp["agent"], "leaning": exp["leaning"], "words": words, "room": exp["room"],
                   "person": exp["person"]},
                  [KERNEL], {"kind": MARKER_KIND, "id": exp["marker"], "parent": None, "by": exp["person"]},
                  scope=exp["room"])
        moved.append(f"{exp['experiment_id']}: proposed — leaning {exp['leaning']}")
    return moved


def trial(conn, exp: dict, *, gateway=None, home=None, policy=None, say=None) -> dict:
    """THE TRIAL LIFE — the candidate instantiated as a life of the agent's own self IN THE ROOM:
    joined at the room's scope (its wear rows written there; the standing life's rows untouched),
    the golden set run through its own graph, the run recorded under the kernel's run id, its
    wear closed, and done. The same function on both kernels: a process (`body --experiment`)
    on the Rust kernel, a thread on the reference."""
    from . import crafts, ground, harness
    from .resident import Resident
    ground.ensure_all(conn)
    r = Resident(exp["candidate"], gateway=gateway, home=home, scope=exp["room"])
    r.load_policy(policy)
    joined = r.join(conn, close_scope=exp["room"])
    if say:
        say(f"{r.name}'s trial life {joined['life']} stands in {exp['room']} — running the golden set")
    cases = crafts.golden_for(conn, exp["agent"])
    run = harness.run(conn, r, cases, parent_marker=exp["marker"], run_id=exp["arms"]["candidate"]["run_id"])
    with conn.transaction():
        conn.cursor().execute("UPDATE spine_wear SET until = clock_timestamp() WHERE did = %s AND life = %s AND until IS NULL",
                              (r.identity.did, joined["life"]))
    if say:
        say(f"{r.name}'s trial: {run['passed']} passed, {run['failed']} failed — the trial life is spent")
    return run


def verdict_in(cur, *, experiment_id: str | None, identity, by_name: str, reviewer: str, ask_id: str | None,
               verdict: dict, words: str, scope: str, on_ask: str | None = None) -> str:
    """A reviewer's SIGNED VERDICT, written by the reviewer itself in its reply's transaction (rule
    2: under its own DID, over the experiment's evidence, never its own yardstick): the row and
    the fact `orreth.verdict.v1`. Phase 8 sp5: on a LIVE reply too — `experiment_id` None and
    `on_ask` the graded ask (Trust reads these)."""
    vid = "vd_" + secrets.token_hex(6)
    payload = {"experiment": experiment_id, "reviewer": reviewer, "verdict": verdict, "by": identity.did, "on_ask": on_ask}
    sig = identity.sign(payload)
    cur.execute("INSERT INTO spine_verdicts (verdict_id, scope, experiment_id, by_did, by_name, reviewer, ask, verdict,"
                " words, sig, on_ask) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (vid, ev.universe(), experiment_id, identity.did, by_name, reviewer, ask_id, json.dumps(verdict), words, sig, on_ask))
    _fact(cur, VERDICT, vid, {**payload, "sig": sig, "ask": ask_id}, [identity.did], None, scope=scope)
    return vid


def verdicts(conn, experiment_id: str) -> list[dict]:
    cur = conn.cursor()
    cur.execute("SELECT verdict_id, by_did, by_name, reviewer, ask, verdict, words, sig, at FROM spine_verdicts"
                " WHERE experiment_id = %s ORDER BY at", (experiment_id,))
    return [{"verdict_id": r[0], "by": r[1], "by_name": r[2], "reviewer": r[3], "ask": r[4],
             "verdict": json.loads(r[5]), "words": r[6], "sig": r[7], "at": r[8].isoformat()} for r in cur.fetchall()]


# ---- the promotion ---------------------------------------------------------------------------

def promote_check(conn, person: str, experiment_id: str, at: str | None = None) -> dict:
    from . import levels
    exp = get(conn, experiment_id)
    if exp is None or exp["scope"] != ev.universe():
        raise ExperimentRefused("no such experiment here")
    if exp["state"] != "proposed":
        raise ExperimentRefused(f"the experiment {experiment_id} is {exp['state']} — only a proposed experiment promotes"
                                + (" (the arms and the reviewers are not done)" if exp["state"] == "running" else ""))
    dem = promote_demand((exp["candidate"] or {}).get("kind"))
    if not dem["ok"]:
        raise ExperimentRefused(dem["reason"])
    seat = seat_of(conn, exp["agent"])
    try:
        path = deploy_at(ev.universe(), at, seat["at_path"] if seat else None)
    except ValueError as e:
        raise ExperimentRefused(str(e)) from None
    lv = levels.row(conn, path)
    if lv is None:
        raise ExperimentRefused(f"{path} is not open — open the floor or room first; a life stands on an open level")
    if lv["experiment"]:
        raise ExperimentRefused(f"{levels.words(path)} is an experiment room — nothing stands there but an arm")
    return {"experiment": exp, "level": dem["level"], "at": path, "version": (exp["current_version"] or 0) + 1}


def promote_words(agent: str, version: int, at: str) -> str:
    from . import levels
    return f"promoting {agent} to version {version} — its next life stands on {levels.words(at)}"


def hold_promote(conn, person: str, experiment_id: str, *, at: str | None = None, session: str | None = None) -> dict:
    from .proof import hold_kernel_act
    c = promote_check(conn, person, experiment_id, at)
    held = hold_kernel_act(conn, text=promote_words(c["experiment"]["agent"], c["version"], c["at"]), person=person,
                           tool=PROMOTE_TOOL, args={"experiment_id": experiment_id, "person": person, "at": c["at"]},
                           level=c["level"], session=session, cls=ACT_CLASS)
    return {"held": held, "level": c["level"], "class": ACT_CLASS, "agent": c["experiment"]["agent"],
            "version": c["version"], "at": c["at"]}


def promote_in(conn, args: dict, by: str, ask: str | None = None, marker: str | None = None) -> str:
    """The stamped promotion, in the caller's transaction: the candidate lands on the shelf as the
    sibling version (registered, or n+1), probed; the draft is spent; the experiment is settled
    promoted with where the next life stands; the agent's SEAT is written; the kernel's hand
    seats or restarts the body into its next life (the wear table follows that join)."""
    from . import crafts, services
    person, exp_id = str(args.get("person") or by), str(args.get("experiment_id") or "")
    c = promote_check(conn, person, exp_id, args.get("at"))
    exp = c["experiment"]
    body = exp["candidate"]
    if services.get(conn, exp["template"]) is None:
        row = services.register(conn, exp["template"], "template", body, by=by)
    else:
        row = services.version(conn, exp["template"], body, by=by)
    ok_, detail = crafts.probe(conn, row)
    services.record_health(conn, exp["template"], ok_, detail, by=by)
    cur = conn.cursor()
    cur.execute("DELETE FROM spine_drafts WHERE draft_id = %s", (exp["draft_id"],))
    cur.execute("UPDATE spine_experiments SET state = 'promoted', settled_at = clock_timestamp(), settled_by = %s,"
                " at_path = %s WHERE experiment_id = %s", (by, c["at"], exp_id))
    cur.execute("INSERT INTO spine_body_seats (name, scope, template, at_path, state, version, by_did, ask)"
                " VALUES (%s, %s, %s, %s, 'active', %s, %s, %s)"
                " ON CONFLICT (name, scope) DO UPDATE SET at_path = EXCLUDED.at_path, state = 'active',"
                " version = EXCLUDED.version, by_did = EXCLUDED.by_did, changed_at = clock_timestamp(), ask = EXCLUDED.ask",
                (exp["agent"], ev.universe(), exp["template"], c["at"], row["version"], by, ask))
    _fact(cur, EXPERIMENT_SETTLED, exp_id,
          {"agent": exp["agent"], "settled": "promoted", "version": row["version"], "at": c["at"],
           "template": exp["template"], "pin": row["manifest_hash"]},
          [person, KERNEL] if by == person else [person, by, KERNEL],
          {"kind": MARKER_KIND, "id": exp["marker"], "parent": marker, "by": person}, scope=c["at"])
    hand("seat", exp["agent"], c["at"], row["version"])    # after the commit: the body reads the shelf at birth
    from . import levels
    return (f"{exp['template']} is version {row['version']} on the shelf (pin {row['manifest_hash'][7:19]}…) — "
            f"{exp['agent']}'s next life stands on {levels.words(c['at'])}; the room's record is the replay ({exp_id}); "
            "the draft is spent")


def decline(conn, person: str, experiment_id: str, *, reason: str | None = None) -> dict:
    """The human's no — routine, recorded: the experiment settles declined, the draft stays under
    the person to fix and cut again; the room stands (a level is never deleted)."""
    exp = get(conn, experiment_id)
    if exp is None or exp["scope"] != ev.universe():
        raise ExperimentRefused("no such experiment here")
    if exp["state"] in ("promoted", "declined"):
        raise ExperimentRefused(f"the experiment is already {exp['state']}")
    with conn.transaction():
        cur = conn.cursor()
        cur.execute("UPDATE spine_experiments SET state = 'declined', settled_at = clock_timestamp(), settled_by = %s"
                    " WHERE experiment_id = %s", (person, experiment_id))
        _fact(cur, EXPERIMENT_SETTLED, experiment_id,
              {"agent": exp["agent"], "settled": "declined", "reason": reason or "the human declined"},
              [person, KERNEL], {"kind": MARKER_KIND, "id": exp["marker"], "parent": None, "by": exp["person"]},
              scope=exp["room"])
    return {"experiment_id": experiment_id, "state": "declined",
            "words": f"the experiment on {exp['agent']} is declined — recorded; the {exp['agent']} draft stays under your seat to fix and cut again"}


# ---- the seats and the ladder ----------------------------------------------------------------

def seat_of(conn, name: str) -> dict | None:
    ensure_schema(conn)
    cur = conn.cursor()
    cur.execute("SELECT name, template, at_path, state, version, by_did, since, changed_at FROM spine_body_seats"
                " WHERE name = %s AND scope = %s", (name, ev.universe()))
    r = cur.fetchone()
    return _seat(r) if r else None


def _seat(r) -> dict:
    return {"name": r[0], "template": r[1], "at_path": r[2], "state": r[3], "version": r[4], "by": r[5],
            "since": r[6].isoformat(), "changed_at": r[7].isoformat()}


def seats(conn, *, state: str | None = None) -> list[dict]:
    """The seats this kernel wrote — the promoted agents, where each stands and its rung."""
    ensure_schema(conn)
    cur = conn.cursor()
    q, args = ("SELECT name, template, at_path, state, version, by_did, since, changed_at FROM spine_body_seats"
               " WHERE scope = %s"), [ev.universe()]
    if state:
        q += " AND state = %s"; args.append(state)
    cur.execute(q + " ORDER BY name", args)
    return [_seat(r) for r in cur.fetchall()]


def _rung_check(conn, name: str, to: str) -> dict:
    seat = seat_of(conn, name)
    frm = seat["state"] if seat else None
    if frm is None or not ladder_legal(frm, to):
        raise ExperimentRefused(ladder_refusal(name, frm, to))
    return seat


def hold_rest(conn, person: str, name: str, *, session: str | None = None) -> dict:
    from .proof import hold_kernel_act
    _rung_check(conn, name, "rested")
    held = hold_kernel_act(conn, text=f"resting {name} — its life stops at a safe boundary, its self kept",
                           person=person, tool=REST_TOOL, args={"name": name}, level=REST_LEVEL, session=session, cls=ACT_CLASS)
    return {"held": held, "level": REST_LEVEL, "class": ACT_CLASS, "name": name}


def rest_in(conn, args: dict, by: str, ask: str | None = None, marker: str | None = None) -> str:
    name = str(args.get("name") or "")
    seat = _rung_check(conn, name, "rested")
    did = _did_of(conn, name)
    cur = conn.cursor()
    cur.execute("UPDATE spine_body_seats SET state = 'rested', changed_at = clock_timestamp(), ask = %s"
                " WHERE name = %s AND scope = %s", (ask, name, ev.universe()))
    if did:
        cur.execute("UPDATE spine_wear SET until = clock_timestamp() WHERE did = %s AND until IS NULL", (did,))
    _fact(cur, BODY_RESTED, name, {"name": name, "did": did, "at": seat["at_path"], "by": by}, [by, KERNEL],
          {"kind": "objective", "id": marker, "parent": None, "by": by} if marker else None, scope=seat["at_path"])
    hand("rest", name)
    return rest_words(name)


def hold_decom(conn, person: str, name: str, *, session: str | None = None) -> dict:
    from .proof import hold_kernel_act
    _rung_check(conn, name, "decommissioned")
    held = hold_kernel_act(conn, text=f"decommissioning {name} — the grave: its live objects removed, its self and record kept",
                           person=person, tool=DECOM_TOOL, args={"name": name}, level=DECOM_LEVEL, session=session, cls=ACT_CLASS)
    return {"held": held, "level": DECOM_LEVEL, "class": ACT_CLASS, "name": name}


def decom_in(conn, args: dict, by: str, ask: str | None = None, marker: str | None = None, *, gw=None) -> str:
    """The grave, in the caller's transaction: the role's live objects removed — the lease, the
    gateway key and the mind assignment, its schedules, watches and intentions rested, its wear
    closed, its bench deleted by the kernel's hand; the seat decommissioned. The DID, the joins
    and the Record stay."""
    name = str(args.get("name") or "")
    seat = _rung_check(conn, name, "decommissioned")
    did = _did_of(conn, name)
    u = ev.universe()
    cur = conn.cursor()
    removed, kept = [], []
    if did:
        cur.execute("DELETE FROM spine_leases WHERE did = %s", (did,))
        if cur.rowcount:
            removed.append("its lease")
        cur.execute("SELECT key FROM spine_mind_keys WHERE did = %s AND scope = %s", (did, u))
        k = cur.fetchone()
        if k:
            if gw is not None:
                try:
                    gw.key_delete([k[0]])
                except Exception as e:                       # noqa: BLE001 — the row goes; the gateway is said
                    kept.append(f"the gateway key at the gateway ({type(e).__name__})")
            cur.execute("DELETE FROM spine_mind_keys WHERE did = %s AND scope = %s", (did, u))
            removed.append("its gateway key")
        cur.execute("UPDATE spine_watches SET active = false, rested_by = %s, rested_at = now()"
                    " WHERE added_by = %s AND scope = %s AND active", (by, did, u))
        if cur.rowcount:
            removed.append(f"{cur.rowcount} watch{'es' if cur.rowcount != 1 else ''}")
        cur.execute("UPDATE spine_wear SET until = clock_timestamp() WHERE did = %s AND until IS NULL", (did,))
        if cur.rowcount:
            removed.append("its wear links")
    cur.execute("DELETE FROM spine_mind_assignments WHERE subject = %s AND scope = %s", (name, u))
    if cur.rowcount:
        removed.append("its mind assignment")
    cur.execute("UPDATE spine_schedules SET active = false, rested_by = %s, rested_at = now()"
                " WHERE runner = %s AND scope = %s AND active AND kind <> 'kernel'", (by, name, u))
    if cur.rowcount:
        removed.append(f"{cur.rowcount} schedule{'s' if cur.rowcount != 1 else ''}")
    cur.execute("UPDATE spine_intentions SET active = false, stopped_by = %s, stopped_at = now()"
                " WHERE (runner = %s OR planner = %s) AND scope = %s AND active", (by, name, name, u))
    if cur.rowcount:
        removed.append(f"{cur.rowcount} intention{'s' if cur.rowcount != 1 else ''}")
    cur.execute("UPDATE spine_body_seats SET state = 'decommissioned', changed_at = clock_timestamp(), ask = %s"
                " WHERE name = %s AND scope = %s", (ask, name, u))
    if HOOKS.get("queue"):
        try:
            if HOOKS["queue"](name):
                removed.append("its bench")
        except Exception as e:                               # noqa: BLE001
            kept.append(f"its bench ({type(e).__name__})")
    kept.append("its DID, its joins and its record")
    _fact(cur, BODY_DECOMMISSIONED, name, {"name": name, "did": did, "removed": removed, "kept": kept, "by": by},
          [by, KERNEL], {"kind": "objective", "id": marker, "parent": None, "by": by} if marker else None,
          scope=seat["at_path"])
    return decom_words(name, did, removed, [k for k in kept if not k.startswith("its DID")])


def hold_restore(conn, person: str, name: str, *, session: str | None = None) -> dict:
    from .proof import hold_kernel_act
    seat = _rung_check(conn, name, "active")
    held = hold_kernel_act(conn, text=f"restoring {name} — a new life from the shelf's standing version, on {seat['at_path']}",
                           person=person, tool=RESTORE_TOOL, args={"name": name}, level=RESTORE_LEVEL, session=session, cls=ACT_CLASS)
    return {"held": held, "level": RESTORE_LEVEL, "class": ACT_CLASS, "name": name}


def restore_in(conn, args: dict, by: str, ask: str | None = None, marker: str | None = None) -> str:
    from . import services
    name = str(args.get("name") or "")
    seat = _rung_check(conn, name, "active")
    row = services.get(conn, seat["template"])
    if row is None or row["state"] == "retired":
        raise ExperimentRefused(f"{seat['template']} is {'retired' if row else 'gone'} from the shelf — restore the template first")
    cur = conn.cursor()
    cur.execute("UPDATE spine_body_seats SET state = 'active', version = %s, changed_at = clock_timestamp(), ask = %s"
                " WHERE name = %s AND scope = %s", (row["version"], ask, name, ev.universe()))
    _fact(cur, BODY_RESTORED, name, {"name": name, "at": seat["at_path"], "version": row["version"], "by": by}, [by, KERNEL],
          {"kind": "objective", "id": marker, "parent": None, "by": by} if marker else None, scope=seat["at_path"])
    hand("seat", name, seat["at_path"], row["version"])
    return restore_words(name, seat["at_path"])


# ---- the prune beat --------------------------------------------------------------------------

def prune(conn) -> list[dict]:
    """THE PRUNE BEAT (0010 §5): the crafts nobody wears any more — every body that ever wore
    one is decommissioned and no wear row stands open — are RETIRED on the shelf (never deleted,
    never at request time; the spine's own crafts never). A craft another living body wears is
    kept. Returns what was pruned."""
    from . import crafts, services
    ensure_schema(conn)
    shipped = {crafts.craft_name(s["name"], s["kind"]) for s in crafts.shipped()}
    graves = {s["name"] for s in seats(conn, state="decommissioned")}
    if not graves:
        return []
    cur = conn.cursor()
    cur.execute("SELECT component, kind, array_agg(DISTINCT body) FILTER (WHERE until IS NULL),"
                " array_agg(DISTINCT body) FROM spine_wear WHERE scope LIKE %s GROUP BY component, kind",
                (ev.universe() + "%",))
    pruned = []
    for component, kind, open_bodies, all_bodies in cur.fetchall():
        if open_bodies or component in shipped or kind not in crafts.CRAFT_KINDS:
            continue
        if not all_bodies or not set(all_bodies) <= graves:
            continue
        row = services.get(conn, component)
        if row is None or row["state"] == "retired":
            continue
        last = sorted(set(all_bodies))[-1]
        services.record_health(conn, component, None, prune_words(component, kind, last), by="the prune beat")   # the words first —
        services.retire(conn, component, by="the prune beat")                                                   # a retired craft takes no health
        pruned.append({"component": component, "kind": kind, "words": prune_words(component, kind, last)})
    return pruned
