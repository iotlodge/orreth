# PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P6 sp3, MITL v0 + the impact door · 2026-09-21
# Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P6 sp4, placement policy v0 · 2026-09-21
"""MITL v0 — the Master Mind In the Loop (canon 0001 · 0004 · 0005 P6 sp3).

The specialist of Orreth as a firmware body of the third kind: the same
body of laws as planner · critic · grader, named by its function
(`impact`), thinking ONLY through the gateway (covenant rule 5: the
meter is universal). It wears the **Orreth ontology v0** — the canon
files acquired into the store under its own namespace through the SAME
`acquire` door the librarian uses (every passage a provenance-bearing
memory: its source path in the key, its sha256 on the row, its
acquired_at as the landing), and its Understanding is the store's own
projection. It is scribe-class: it weighs a change, the human cuts —
it never executes one and its identity is refused at the confirm door.

Two doors. The **soft toggle** — summoned or dismissed by words or the
chip; each a recorded fact through the outbox with the human's chain and
a marker, never a deletion (rule 11). The **impact door** — "expected
impact of this change?": the kernel reads the GROUND deterministically
(which bodies, intentions, watches, markers and cost a change touches)
and judges the VERDICT by sp1's ladder (a kernel intention ⇒ grave,
whatever any brain says); the words come from MITL as an ordinary ask,
filed under the change's marker so the confirm that follows shows it.

Factories are OUT of v0 (a proof's need decides).
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from . import envelope as ev, outbox

NAME = "mitl"
EXPANSION = "the Master Mind In the Loop"
FUNCTION = "impact"
SUMMONED = "orreth.mitl.summoned.v1"
DISMISSED = "orreth.mitl.dismissed.v1"
CONTRACT = "orreth.impact/1"
REPO = Path(__file__).resolve().parents[2]          # spine/orreth_spine/mitl.py → the repo
ONTOLOGY = (                                        # the Orreth ontology v0: the canon files
    "docs/rearch/0001-experience-charter.md",
    "docs/rearch/0002-transport-architecture.md",
    "docs/rearch/0003-memory-architecture.md",
    "docs/rearch/0004-agent-architecture.md",
    "docs/rearch/0005-v1-scope-and-build-plan.md",
    "docs/rearch/0006-markers-dive.md",
    "docs/rearch/0007-intent-dive.md",
    "docs/rearch/0008-the-rust-plane-and-the-port.md",
    ".claude/skills/orreth-covenant/SKILL.md",
)
PASSAGE = 2400                                      # a passage the pack can carry whole
KINDS = ("watch", "intention", "template", "binding", "placement", "act")
VERDICTS = ("low", "consider", "grave — needs L3")  # sp1's ladder, in MITL's words

SYSTEM = (
    "You are MITL — the Master Mind In the Loop — Orreth's own specialist, a "
    "firmware agent of the third kind. You read the canon (your recalled notes "
    "carry its passages, each named by its source path) and the GROUND the kernel "
    "read for you, and you say what a change touches. Laws: you weigh, you never "
    "decide — the human cuts, and only a human confirms; name bodies, intentions, "
    "watches and costs by their names as the ground gives them; when you lean on "
    "the canon, say which passage (its path); plain words a newcomer understands — "
    "expand your name once ('the Master Mind In the Loop'); never invent a fact "
    "your notes do not hold; complete, never a teaser. When asked what the canon "
    "says, answer from the passages you recalled and name their paths. For an "
    "EXPECTED IMPACT ask, answer in three short parts — WHO AND WHAT IT TOUCHES · "
    "THE RISK · WHAT TO WATCH AFTER — and end with the verdict line the kernel "
    "gave you, word for word: the ladder is law, not opinion."
)


# ---- the ontology: the canon acquired through the librarian's door --------------------

def passages(text: str, limit: int = PASSAGE) -> list[str]:
    """The canon in passages the pack can carry whole: a new passage at
    every heading, paragraphs packed up to the limit — every word kept."""
    out: list[str] = []
    cur = ""
    for para in re.split(r"\n\s*\n", text):
        para = para.strip("\n")
        if not para.strip():
            continue
        if cur and (para.lstrip().startswith("#") or len(cur) + len(para) + 2 > limit):
            out.append(cur)
            cur = ""
        while len(para) > limit:                    # one paragraph wider than the pack
            out.append(para[:limit])
            para = para[limit:]
        cur = f"{cur}\n\n{para}" if cur else para
    if cur:
        out.append(cur)
    return out


def acquire_ontology(conn, body, root: str | Path | None = None) -> dict:
    """MITL takes the canon into its own memory — passage by passage,
    through the SAME `acquire` tool door the librarian uses (journaled,
    the hop on the wire, an action marker under ONE root that names the
    acquisition). The key is the source path plus the passage number;
    the row's hash is the sha256 of the words; landed_at is acquired_at.
    A passage already held with the same words lands nothing (idempotent
    — the store's own law); a changed one becomes a sibling that
    supersedes. Returns what happened, honestly."""
    from . import markers
    from .store import OrrethStore
    from .tools import ToolDoor
    base = Path(root or REPO)
    st = OrrethStore(conn, by_did=body.identity.did)
    plan: list[tuple[str, str]] = []
    missing: list[str] = []
    files = 0
    for rel in ONTOLOGY:
        p = base / rel
        if not p.exists():
            missing.append(rel)
            continue
        files += 1
        for i, part in enumerate(passages(p.read_text("utf-8")), 1):
            key = f"{rel}#{i}"
            if st.get(NAME, key) == part:           # the same words: nothing new
                continue
            plan.append((key, part))
    if not plan:
        return {"acquired": 0, "files": files, "missing": missing, "marker": None}
    markers.ensure_schema(conn)
    markers.seed(conn)
    m = markers.mint(conn, "action", body.identity.did, body.identity.did,
                     note=f"MITL acquired the Orreth ontology v0 — {len(plan)} passages of the canon")
    door = ToolDoor(conn, did=body.identity.did, name=NAME, marker=m["id"],
                    capabilities=body.template.get("capabilities", []),
                    chain=[body.identity.did])
    for key, part in plan:
        door.call("acquire", {"key": key, "text": part})
    return {"acquired": len(plan), "files": files, "missing": missing, "marker": m["id"]}


def ontology(conn) -> list[dict]:
    """What MITL wears, with its provenance: every current passage's
    source path, passage number, sha256 and when it was acquired."""
    from .store import ensure_schema as _mem
    _mem(conn)
    cur = conn.cursor()
    cur.execute("SELECT key, hash, landed_at, length(body) FROM spine_memories"
                " WHERE namespace = %s AND scope = %s AND valid_to IS NULL ORDER BY key",
                (NAME, ev.scope()))
    out = []
    for key, h, at, n in cur.fetchall():
        path, _, num = key.partition("#")
        out.append({"key": key, "path": path, "passage": int(num or 0), "hash": h,
                    "acquired_at": at.isoformat(), "chars": int(n)})
    return out


# ---- the soft toggle: summoned · dismissed — recorded facts, never a deletion ----------

def ensure_schema(conn) -> None:
    if not outbox.once(conn, "mitl"):
        return
    with conn.transaction():
        cur = conn.cursor()
        cur.execute("SELECT pg_advisory_xact_lock(742199)")  # DDL race guard
        cur.execute(
            "CREATE TABLE IF NOT EXISTS spine_mitl ("
            " row_id bigserial PRIMARY KEY, session text, person text NOT NULL,"
            " state text NOT NULL, marker text, scope text NOT NULL,"
            " at timestamptz NOT NULL DEFAULT now())")


def _latest_objective(conn, session: str | None) -> str | None:
    if not session:
        return None
    cur = conn.cursor()
    cur.execute(
        "SELECT a.marker FROM spine_asks a JOIN spine_markers m ON m.marker_id = a.marker"
        " WHERE a.session = %s AND m.kind = 'objective' ORDER BY a.asked_at DESC LIMIT 1",
        (session,))
    r = cur.fetchone()
    return r[0] if r else None


def summon(conn, person: str, session: str | None = None, *, on: bool = True) -> dict:
    """The toggle's effect: a row, its marker (an action under the
    session's latest objective, or a root), and its fact on the rail
    wearing the human's chain — summoned or dismissed, both recorded."""
    from . import markers
    from .resident import ensure_schema as _ground
    _ground(conn); ensure_schema(conn); outbox.ensure_schema(conn)
    markers.ensure_schema(conn); markers.seed(conn)
    parent = _latest_objective(conn, session)
    mid = markers.new_id()
    marker = {"kind": "action", "id": mid, "parent": parent, "by": person}
    state = "summoned" if on else "dismissed"
    ref = session or person
    e = ev.make_envelope(
        kind="event", type=SUMMONED if on else DISMISSED, universe_id=ev.scope(),
        scope_path=ev.scope(),
        payload={"ref": ref, "hash": "sha256:-", "by": person, "session": session,
                 "body": NAME},
        correlation_id=ref, authority_chain=[person], marker=marker)

    def domain(cur):
        markers.insert(cur, mid, "action", parent, ref, person,
                       f"MITL {state} — {EXPANSION}")
        cur.execute("INSERT INTO spine_mitl (session, person, state, marker, scope)"
                    " VALUES (%s, %s, %s, %s, %s)", (session, person, state, mid, ev.scope()))

    outbox.commit_with_outbox(conn, ev.encode(e), e["message_id"], domain)
    return {"summoned": on, "state": state, "person": person, "session": session,
            "marker": mid, "name": NAME, "expansion": EXPANSION}


def summoned(conn, session: str | None = None, person: str | None = None) -> bool:
    """Is MITL in the lit crew — for this session, or for this person
    outside any session? The latest recorded word decides."""
    ensure_schema(conn)
    cur = conn.cursor()
    if session:
        cur.execute("SELECT state FROM spine_mitl WHERE session = %s AND scope = %s"
                    " ORDER BY row_id DESC LIMIT 1", (session, ev.scope()))
    else:
        cur.execute("SELECT state FROM spine_mitl WHERE session IS NULL AND person = %s"
                    " AND scope = %s ORDER BY row_id DESC LIMIT 1", (person or "", ev.scope()))
    r = cur.fetchone()
    return bool(r and r[0] == "summoned")


# ---- the impact door: the ground read, the verdict judged, the words asked -------------

def _has(conn, table: str) -> bool:
    cur = conn.cursor()
    cur.execute("SELECT to_regclass(%s) IS NOT NULL", (table,))
    return bool(cur.fetchone()[0])


def _bodies(conn) -> dict[str, dict]:
    """Every body of this world by name — its kind, self, and life."""
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT ON (name) name, kind, did, life FROM spine_joins"
                " WHERE scope = %s ORDER BY name, join_id DESC", (ev.scope(),))
    return {n: {"name": n, "kind": k, "did": d, "life": life} for n, k, d, life in cur.fetchall()}


def _cost(conn, dids: list[str]) -> dict[str, dict]:
    """The meter's cost so far for the selves named (rule 5: the count,
    never the prompt)."""
    if not dids or not _has(conn, "spine_meter"):
        return {}
    cur = conn.cursor()
    cur.execute("SELECT did, count(*), coalesce(sum(tokens_in + tokens_out), 0) FROM spine_meter"
                " WHERE did = ANY(%s) GROUP BY did", (dids,))
    return {d: {"thoughts": int(n), "tokens": int(t)} for d, n, t in cur.fetchall()}


_METRIC_WORDS = (                 # a watch in plain words names its metric (v0 word rules)
    ("bodies_dormant", r"dormant"),
    ("bodies_alive", r"\balive\b|\bliving\b"),
    ("oldest_outbox_age_s", r"oldest|\bage\b|\bold\b|stale"),
    ("outbox_pending", r"outbox|pending|backlog"),
    ("asks_received", r"\basks?\b|received|waiting|unserved"),
)


def _metric_in(words: str) -> str | None:
    from . import monitor
    low = words.lower()
    for m in monitor.METRICS:
        if m in low.replace(" ", "_"):
            return m
    for m, pat in _METRIC_WORDS:
        if re.search(pat, low):
            return m
    return None


def read_ground(conn, change: dict) -> dict:
    """The kernel reads the ground for MITL — deterministically: what the
    change touches (bodies · chains · intentions · watches · markers ·
    the meter's cost so far), its consequence class and the level it
    demands. A held ask (`ref` = ask_…) is read from its hold; an
    intention from its record; a draft from its words."""
    from . import intent, monitor
    from .proof import level_for
    from .tools import TOOLS, consequence_of
    kind = str(change.get("kind") or "")
    if kind not in KINDS:
        raise ValueError(f"a change is one of {', '.join(KINDS)}")
    ref = str(change.get("ref") or "") or None
    draft = dict(change.get("draft") or {})
    words = " ".join(str(change.get("words") or "").split())
    t: dict = {"kind": kind, "ref": ref, "words": words, "bodies": [], "chains": [],
               "intentions": [], "watches": [], "markers": [], "cost": {}, "notes": [],
               "kernel": False, "class": "routine", "level": "L1", "marker": None}
    bodies = _bodies(conn)
    named: list[str] = []

    def name_body(n: str | None) -> None:
        if n and n not in named:
            named.append(n)

    # a held ask: the hold names the act, its class and its level (sp1)
    hold = None
    if ref and ref.startswith("ask_"):
        cur = conn.cursor()
        cur.execute("SELECT held, marker, served_by, text, status FROM spine_asks"
                    " WHERE ask_id = %s AND scope = %s", (ref, ev.scope()))
        row = cur.fetchone()
        if row is None:
            t["notes"].append("no such ask is held on this ground")
        else:
            hold = json.loads(row[0]) if row[0] else {}
            t["marker"] = row[1]
            t["markers"].append({"id": row[1], "kind": "objective", "ref": ref})
            if hold:
                t["class"], t["level"] = hold.get("class", "consequential"), hold.get("level", "L2")
                merged = dict(hold.get("args") or {})       # the hold's own args first,
                merged["tool"] = hold.get("tool")           # the caller's draft on top
                merged.update(draft)
                draft = merged
            if row[2] and row[2] != "the kernel":
                holder = next((b["name"] for b in bodies.values() if b["did"] == row[2]), None)
                name_body(holder)
            words = words or " ".join((row[3] or "").split())[:200]
            t["words"] = words
            if row[4] != "awaiting-confirm":
                t["notes"].append(f"this ask is {row[4]} — nothing is held now")

    if kind == "watch":
        metric = str(draft.get("metric") or "") or _metric_in(words)
        t["metric"] = metric
        t["watch"] = {"name": draft.get("name") or words[:80], "metric": metric,
                      "op": draft.get("op"), "threshold": draft.get("threshold")}
        if metric and metric not in monitor.METRICS:
            t["notes"].append(f"no metric named {metric!r} — the metrics are "
                              + ", ".join(monitor.METRICS))
        tool = TOOLS.get("add-watch") or {}
        if not hold:
            t["class"] = consequence_of(tool)
            t["level"] = level_for(t["class"], master=bool(tool.get("master")))
        mon = bodies.get("monitor")
        name_body("monitor")
        if mon is None:
            t["notes"].append("no monitor body has joined this world yet — the watch would land by hand")
        t["chains"].append("H → monitor → tool:add-watch")
        if _has(conn, "spine_watches"):
            cur = conn.cursor()
            cur.execute("SELECT watch_id, name, metric, op, threshold, last_ok FROM spine_watches"
                        " WHERE scope = %s ORDER BY added_at", (ev.scope(),))
            for w in cur.fetchall():
                if metric and w[2] == metric:
                    t["watches"].append({"watch_id": w[0], "name": w[1], "metric": w[2], "op": w[3],
                                         "threshold": w[4], "red": w[5] is False})
        for i in intent.interested(conn, intent.WATCH_RED):     # who wakes when it goes red
            t["intentions"].append({"intention_id": i["intention_id"], "words": i["words"],
                                    "kind": i["kind"], "serves": i["serves"], "wakes": True})
            name_body(i["planner"]); name_body(i["runner"])
            t["chains"].append(f"the kernel → {i['planner']} → {i['runner'] or 'the crew'}"
                               f" (when “{i['words'][:60]}” wakes on watch-red)")
            t["kernel"] = t["kernel"] or False               # waking a kernel intention is not grave

    elif kind == "intention":
        iid = str(draft.get("intention_id") or "") or (ref if ref and ref.startswith("int_") else None)
        if iid:
            i = intent.get(conn, iid)
            if i is None:
                t["notes"].append("no such intention on this ground")
            else:
                t["intentions"].append({"intention_id": iid, "words": i["words"], "kind": i["kind"],
                                        "serves": i["serves"], "active": i["active"], "wakes": False})
                t["kernel"] = i["kind"] == "kernel"
                t["marker"] = t["marker"] or i["marker"]
                cur = conn.cursor()
                cur.execute("SELECT kind, count(*) FROM spine_markers WHERE root = %s AND marker_id <> %s"
                            " GROUP BY kind", (i["marker"], i["marker"]))
                grew = {k: int(n) for k, n in cur.fetchall()}
                t["markers"].append({"id": i["marker"], "kind": "intention", "ref": iid, "under": grew})
                name_body(i["planner"]); name_body(i["runner"])
                t["chains"].append(f"the kernel → {i['planner']} → {i['runner'] or 'the crew'}")
                if t["kernel"]:
                    t["class"], t["level"] = "grave", "L3-master"
                    t["chains"].append("H → a master → the kernel (the stop)")
                elif not hold:
                    t["class"], t["level"] = "routine", "L1"
                if not i["active"]:
                    t["notes"].append("this intention is already at rest")
        else:                                                   # a draft, from its words
            rw = intent.read_words("intention: " + (words or draft.get("words") or ""))
            t["draft"] = {"serves": rw.get("serves"), "interests": rw.get("interests"),
                          "every_s": rw.get("every_s"), "runner": draft.get("runner")}
            name_body("planner"); name_body(draft.get("runner"))
            t["chains"].append(f"the kernel → planner → {draft.get('runner') or 'the crew'}")
            for i in intent.listing(conn, active=True):
                shared = sorted(set(i["interests"]) & set(rw.get("interests") or []))
                if shared:
                    t["intentions"].append({"intention_id": i["intention_id"], "words": i["words"],
                                            "kind": i["kind"], "serves": i["serves"],
                                            "shares": shared, "wakes": False})
            if not (rw.get("interests") or rw.get("every_s")):
                t["notes"].append("nothing wakes it yet — say WHEN (a red watch, a cadence)")

    elif kind == "placement":
        # P6 sp4: a placement change is consequential (L2) in v0 — MITL reads
        # the profile the change proposes (the draft's `placement`, else the
        # named body's own from its join) and judges it against THIS ground
        from . import placement as _placement
        who = str(draft.get("name") or ref or "")
        if who in bodies:
            name_body(who)
        cur = conn.cursor()
        worn = None
        if who in bodies:
            cur.execute("SELECT placement FROM spine_joins WHERE did = %s ORDER BY join_id DESC LIMIT 1",
                        (bodies[who]["did"],))
            r = cur.fetchone()
            worn = json.loads(r[0]) if r and r[0] else dict(_placement.DEFAULT)
        try:
            prof = _placement.profile({"placement": draft.get("placement") or worn or {}})
        except ValueError as e:
            prof, t["notes"] = None, t["notes"] + [str(e)]
        t["class"], t["level"] = "consequential", "L2"
        t["placement"] = prof
        if prof is not None:
            here = _placement.ground_declares()
            ok, reasons = _placement.honor(prof, here)
            t["notes"].append(("this ground honors it: " if ok else "this ground would REFUSE it at birth: ")
                              + _placement.why_here(prof, here))
            if worn is not None and worn != prof:
                t["notes"].append(f"{who} stands today on cell '{worn['cell']}' · metal {worn['metal']}"
                                  + (" · beside " + ", ".join(worn["affinity"]) if worn.get("affinity") else ""))
            if prof["affinity"]:
                t["notes"].append("affinity is advisory in v0 — recorded and shown, not enforced (P7's cells)")
        if not who:
            t["notes"].append("no body named — the profile is judged on its own against this ground")

    elif kind in ("template", "binding"):
        who = str(draft.get("name") or ref or "")
        if who in bodies:
            name_body(who)
        else:
            for b in bodies.values():
                if kind == "template" and b["kind"] == "resident":
                    name_body(b["name"])
                elif kind == "binding" and b["kind"] == "firmware":
                    name_body(b["name"])

    elif kind == "act":
        tool = str(draft.get("tool") or ref or "")
        spec = TOOLS.get(tool)
        t["tool"] = tool
        if spec is None:
            t["notes"].append(f"no tool named {tool!r} lives on this shelf")
        elif not hold:
            t["class"] = consequence_of(spec)
            t["level"] = level_for(t["class"], master=bool(spec.get("master")))
        if named:
            t["chains"].append(f"H → {named[0]} → tool:{tool}")

    for n in named:
        b = bodies.get(n)
        t["bodies"].append({"name": n, "kind": b["kind"] if b else None,
                            "did": b["did"] if b else None, "joined": b is not None})
    cost = _cost(conn, [b["did"] for b in t["bodies"] if b["did"]])
    for b in t["bodies"]:
        if b["did"] in cost:
            t["cost"][b["name"]] = cost[b["did"]]
    return t


def verdict(touches: dict) -> str:
    """The ladder (sp1), applied by rule — never by a brain: a kernel
    intention, or any act held at L3, is grave; a change that touches a
    standing intention, a consequential act, or what bodies wear is
    'consider'; the rest is low."""
    if touches.get("kernel") or str(touches.get("level") or "").startswith("L3"):
        return VERDICTS[2]
    if (touches.get("intentions") or touches.get("class") == "consequential"
            or touches.get("kind") in ("intention", "template", "binding", "placement")):
        return VERDICTS[1]
    return VERDICTS[0]


def describe(t: dict) -> list[str]:
    """The ground, in lines MITL can read and the glass can show."""
    lines = []
    if t["bodies"]:
        lines.append("bodies: " + ", ".join(
            f"{b['name']} ({b['kind'] or 'not joined'})" for b in t["bodies"]))
    if t["chains"]:
        lines.append("chains: " + " · ".join(t["chains"]))
    for i in t["intentions"]:
        tag = ("wakes on it" if i.get("wakes") else
               f"shares {', '.join(i['shares'])}" if i.get("shares") else
               ("at rest" if i.get("active") is False else "standing"))
        lines.append(f"intention ({i['kind']}, serves {i['serves']}): “{i['words'][:90]}” — {tag}")
    for w in t["watches"]:
        lines.append(f"watch on the same metric: {w['name']} — {w['metric']} {w['op']} {w['threshold']}"
                     + (" (red now)" if w.get("red") else ""))
    for m in t["markers"]:
        under = m.get("under")
        lines.append(f"marker: {m['kind']} {m['id']}" + (
            " — grew " + ", ".join(f"{n} {k}" for k, n in under.items()) if under else ""))
    for n, c in t["cost"].items():
        lines.append(f"cost so far: {n} — {c['thoughts']} thoughts, {c['tokens']} tokens on the meter")
    if t.get("metric"):
        lines.append(f"metric: {t['metric']}")
    if t.get("placement"):
        p = t["placement"]
        lines.append(f"placement asked: cell '{p['cell']}' · metal {p['metal']}"
                     + (" · beside " + ", ".join(p["affinity"]) if p["affinity"] else "")
                     + (" · secrets " + ", ".join(p["secrets_with"]) if p["secrets_with"] else ""))
    lines.append(f"consequence: {t['class']} → {t['level']}")
    lines.extend(t["notes"])
    return lines


def shape(change: dict, touches: dict, verdict_: str, ask_id: str | None,
          marker: str | None) -> dict:
    """The impact answer's shape on the wire (`orreth.impact/1`) — what
    the door returns and the Rust plane must produce byte for byte."""
    return {
        "contract": CONTRACT,
        "change": {"kind": touches["kind"], "ref": touches["ref"], "words": touches["words"]},
        "touches": {
            "bodies": [b["name"] for b in touches["bodies"]],
            "chains": list(touches["chains"]),
            "intentions": [{"intention_id": i["intention_id"], "kind": i["kind"],
                            "words": i["words"]} for i in touches["intentions"]],
            "watches": [w["watch_id"] for w in touches["watches"]],
            "markers": [m["id"] for m in touches["markers"] if m.get("id")],
            "cost": touches["cost"],
            "metric": touches.get("metric"),
            "class": touches["class"], "level": touches["level"], "kernel": bool(touches["kernel"]),
            "notes": list(touches["notes"]),
            **({"placement": touches["placement"]} if touches.get("placement") else {}),
        },
        "verdict": verdict_,
        "served_by": NAME,
        "ask_id": ask_id,
        "marker": marker,
    }


def impact(conn, change: dict, *, person: str, session: str | None = None) -> dict:
    """The door: the ground read and the verdict judged here, by rule;
    the words asked of MITL as an ordinary ask (its journey, its reply,
    its marker) filed under the change's marker — else the session's
    latest objective — so the confirm that follows can show it."""
    from . import dispatch
    t = read_ground(conn, change)
    v = verdict(t)
    ground = describe(t)
    head = t["words"] or f"a {t['kind']}" + (f" {t['ref']}" if t["ref"] else "")
    text = (f"EXPECTED IMPACT? {head}\n"
            f"THE CHANGE: a {t['kind']}" + (f" ({t['ref']})" if t["ref"] else "") + "\n"
            "THE GROUND (read by the kernel — this is the record):\n- " + "\n- ".join(ground) + "\n"
            f"VERDICT BY THE LADDER: {v}\n"
            "Answer in plain words, three short parts — WHO AND WHAT IT TOUCHES · THE RISK · "
            "WHAT TO WATCH AFTER — and end with the verdict line above, unchanged.")
    parent = t["marker"] or _latest_objective(conn, session)
    [aid] = dispatch.submit_ask(conn, text, person=person, to=[NAME], session=session,
                                parent_marker=parent, kind="thought")
    out = shape(change, t, v, aid, parent)
    out["ground"] = ground
    out["expansion"] = EXPANSION
    return out
