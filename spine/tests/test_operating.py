# PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch Phase 8 THE WORKSHOP sp5, THE OPERATING STATE · 2026-10-08
"""THE OPERATING STATE on the reference (canon 0010 §7 · 0005 Phase 8 sp5): the five measurements read
live off the ground — unknown while nothing is there to measure, never a silent 1.0 — and watched by the
kernel's own five watches; THE OPERATING STATE intention beside Resiliency, the watch as the discriminator
(a measurement's red reaches it alone; every other red stays Resiliency's); the feedback door feeding
Experience; summon generalized (a summonable body in, a crew body without the declaration refused, a helper
never); THE GRADE BEAT handing a live reply to the grader, whose signed verdict feeds Trust; the critic's
PROPOSE under an improvement marker landing a draft under the agent's owner; a repo'd graph run inside the
hull by an import node (a local repository, a callable entry); the meter wearing the ask it served (Cost)."""
import json
import secrets
import subprocess
from pathlib import Path

import pytest

from orreth_spine import (crafts, dispatch, envelope as ev, experiments as xp, gateway, ground, intent, levels, markers,
                          monitor, operating as op, proof, resident, services)

SPINE = Path(__file__).resolve().parents[1]
POLICY = SPINE / "policy" / "covenant-policy.v1.json"
PERSON = "did:orreth:person:test"


def _world(monkeypatch):
    u = "u:op-" + secrets.token_hex(3)
    monkeypatch.setenv("SPINE_SCOPE", u)
    monkeypatch.delenv("SPINE_MODE", raising=False)
    monkeypatch.delenv(op.GRADE_DIAL, raising=False)
    return u


def _body(template, gw=None, home=None):
    r = resident.Resident(SPINE / "templates" / template, gateway=gw, home=home)
    r.load_policy(POLICY)
    return r


def _serve(pg, body, ask_id, reply=None):
    if reply is not None:
        body.gateway = gateway.FakeGateway(reply=reply)
    body._serve_conn = pg
    with pg.transaction():
        body._serve_ask(pg.cursor(), ask_id, [PERSON])
    body._serve_conn = None


def _facts(pg, type_, u):
    cur = pg.cursor()
    cur.execute("SELECT body FROM spine_outbox ORDER BY outbox_id")
    out = []
    for (body,) in cur.fetchall():
        try:
            e = ev.decode(bytes(body))
        except Exception:                       # noqa: BLE001
            continue
        if e.get("type") == type_ and e.get("universe_id") == u:
            out.append(e)
    return out


def test_the_law_is_pure():
    assert op.ratio(0, 0) is None and op.ratio(2, 3) == 0.6667 and op.ratio(3, 3) == 1.0
    assert op.latency_class("objective", None) == ("chat", 30.0) and op.latency_class("objective", "intention") == ("work", 180.0)
    assert op.pass_grade("b") and not op.pass_grade("D") and not op.pass_grade(None)
    assert op.measure_words("trust", None, 0, 0) == "trust: unknown — no graded yet (never a silent 1.0)"
    assert op.measure_words("experience", 0.6667, 2, 3) == "experience: 0.6667 — 2 of 3 thumbs up"
    assert op.routes_to(None, "outbox_pending") and not op.routes_to(None, "trust")
    assert op.routes_to(["trust", "cost"], "trust") and not op.routes_to(["trust", "cost"], "outbox_pending")
    assert op.grade_of_live("grade: B — plain and complete") == {"grade": "B", "line": "plain and complete"}
    assert op.grade_of_live("I decline.") == {"grade": None, "line": None}
    assert op.OPERATING["serves"] == "operating-state" and op.OPERATING["watches"] == list(op.MEASUREMENTS)
    assert "operating-state" in intent.SERVES and set(op.MEASUREMENTS) <= set(monitor.METRICS)
    assert monitor.judge_one("<", None, 1.0) is False                             # unknown turns nothing red
    assert monitor.reads({"metric": "trust", "op": "<", "threshold": 1.0, "value": None, "red": False}) == \
        "red when trust < 1.0 · now unknown (nothing to measure yet) → green"


def test_the_five_are_measured_watched_and_owned_by_the_operating_state(pg, monkeypatch):
    u = _world(monkeypatch)
    ground.ensure_all(pg)
    services.seed(pg)
    levels.ensure_universe(pg, u)
    # unknown while nothing is there to measure — never a silent 1.0
    m = op.measure(pg)
    assert [m[k]["value"] for k in op.MEASUREMENTS] == [None, None, None, None, None]
    assert m["experience"]["words"] == "experience: unknown — no thumbs given yet (never a silent 1.0)"
    # the kernel's five watches — and the ground's (the cure, 2026-10-08) — and THE OPERATING STATE, once per world
    from orreth_spine import chips
    assert op.watches_at_light(pg) == list(op.MEASUREMENTS) + [op.GROUND_WATCH, chips.KEYCHECK_WATCH] and op.watches_at_light(pg) == []   # Phase 8 sp6: the seventh
    res = intent.declared(pg, intent.RESILIENCY["words"], serves="resiliency", kind="kernel", by="the kernel",
                          interests=intent.RESILIENCY["interests"], planner="planner", runner="librarian")
    ops = op.intention_at_light(pg)
    assert ops["serves"] == "operating-state" and ops["watches"] == list(op.MEASUREMENTS) and ops["runner"] == "critic"
    assert op.intention_at_light(pg)["intention_id"] == ops["intention_id"]
    assert res["watches"] is None
    snap = monitor.snapshot(pg, rails=False)
    five = [w for w in snap["watches"] if w["metric"] in op.MEASUREMENTS]
    assert len(five) == 5 and all(w["added_by"] == "the kernel" and not w["red"] and w["value"] is None for w in five)
    assert snap["measurements"]["trust"]["value"] is None and snap["values"]["trust"] is None
    # a served ask (the echo, in-process) — Recall and Efficiency count it; a thumb — Experience; the meter's ask — Cost
    echo = _body("echo-resident.v0.json")
    echo.join(pg)
    [aid] = dispatch.submit_ask(pg, "echo, hello world", person=PERSON, to=["echo"])
    _serve(pg, echo, aid)
    fb = op.give_feedback(pg, PERSON, aid, 1, words="plain and whole")
    assert fb["sign"] == 1 and len(_facts(pg, op.FEEDBACK_GIVEN, u)) == 1
    with pytest.raises(op.OperatingRefused, match="no such ask here"):
        op.give_feedback(pg, PERSON, "ask_nowhere", 1)
    gateway.meter(pg, echo.identity.did, "fake-mind", 10, 5, usd=0.5, ask=aid)
    gateway.meter(pg, echo.identity.did, "fake-mind", 10, 5, usd=0.5)
    m = op.measure(pg)
    assert m["recall"]["value"] == 1.0 and m["efficiency"]["value"] == 1.0 and m["experience"]["value"] == 1.0
    assert m["cost"] == {"value": 0.5, "num": 0.5, "den": 1.0, "words": "cost: 0.5000 — $0.5000 of $1.0000 spend a serving ask can be named for"}
    assert m["trust"]["value"] is None                                           # nothing graded yet
    # the watch is the discriminator: a measurement's red reaches THE OPERATING STATE alone; another red stays Resiliency's
    op.give_feedback(pg, PERSON, aid, -1, words="too curt")
    assert op.measure(pg)["experience"]["value"] == 0.5
    turned = intent._turn(pg)
    cur = pg.cursor()
    cur.execute("SELECT m.ref, m.parent FROM spine_markers m WHERE m.kind = 'watch-red' AND m.scope = %s", (u,))
    reds = cur.fetchall()
    wid = next(w["watch_id"] for w in monitor.snapshot(pg, rails=False)["watches"] if w["metric"] == "experience")
    assert [(r, p) for r, p in reds if r == wid] == [(wid, ops["marker"])], (reds, turned)
    pw = monitor.add_watch(pg, "parked-watch", "parked", ">=", 0.0, PERSON)    # red at once: parked >= 0 — not a measurement
    intent._turn(pg)
    cur.execute("SELECT m.parent FROM spine_markers m WHERE m.kind = 'watch-red' AND m.scope = %s AND m.ref = %s", (u, pw))
    assert [p for (p,) in cur.fetchall()] == [res["marker"]]                   # Resiliency's alone
    cur.execute("SELECT m.ref FROM spine_markers m WHERE m.kind = 'watch-red' AND m.scope = %s AND m.parent = %s", (u, ops["marker"]))
    cost_wid = next(w["watch_id"] for w in monitor.snapshot(pg, rails=False)["watches"] if w["metric"] == "cost")
    assert sorted(r for (r,) in cur.fetchall()) == sorted([wid, cost_wid])      # the measurements' reds: experience and cost


def test_the_grader_hears_live_replies_and_signs_and_the_critic_proposes(pg, monkeypatch, tmp_path):
    u = _world(monkeypatch)
    ground.ensure_all(pg)
    services.seed(pg)
    levels.ensure_universe(pg, u)
    home = tmp_path / "agents"
    echo, grader, critic = _body("echo-resident.v0.json", home=home), _body("firmware-grader.v0.json", home=home), _body("firmware-critic.v0.json", home=home)
    for b in (echo, grader, critic):
        b.join(pg)
    [aid] = dispatch.submit_ask(pg, "echo, say the moon is round", person=PERSON, to=["echo"])
    _serve(pg, echo, aid)
    # THE GRADE BEAT: the live reply handed to the grader under the reply's own marker — once, never a grading ask, never a reviewer's
    asked = op.grade_beat(pg)
    assert len(asked) == 1 and asked[0].startswith(f"{aid} by echo → the grader (ask_")
    assert op.grade_beat(pg) == []
    gid = asked[0].split("(")[1].rstrip(")")
    cur = pg.cursor()
    cur.execute("SELECT text, marker FROM spine_asks WHERE ask_id = %s", (gid,))
    text, mk = cur.fetchone()
    assert text.startswith(f"grader, grade the reply {aid} by echo. The ask: 'echo, say the moon is round'. The reply: 'echo, say the moon is round'.")
    cur.execute("SELECT marker FROM spine_asks WHERE ask_id = %s", (aid,))
    gm = markers.get(pg, markers.get(pg, mk)["parent"])
    assert gm["kind"] == "grading" and gm["parent"] == cur.fetchone()[0] and gm["ref"] == aid   # under the reply's own ask
    assert op.graded_ask_of(pg, gid) == aid
    monkeypatch.setenv(op.GRADE_DIAL, "0")
    assert op.grade_beat(pg) == []                                                # the dial turns it off
    monkeypatch.delenv(op.GRADE_DIAL)
    # the grader serves through its hull: the reply IS its evidence (never its own words); its verdict in the form, SIGNED
    _serve(pg, grader, gid, "grade: B — it kept every word, plainly")
    [v] = op.live_verdicts(pg, aid)
    assert v["by_name"] == "grader" and v["verdict"] == {"grade": "B", "line": "it kept every word, plainly"} and len(v["sig"]) == 128
    assert grader.identity.sign({"experiment": None, "reviewer": "grader", "verdict": v["verdict"], "by": grader.identity.did, "on_ask": aid}) == v["sig"]
    journey = " / ".join(j["payload"]["note"] for j in _facts(pg, resident.JOURNEY, u) if j["payload"]["ref"] == gid)
    assert "routed to the event edge — a marker of kind grading asked for a response" in journey, journey
    assert f"wrote my signed verdict on {aid} under my own name — grade B" in journey
    assert op.measure(pg)["trust"] == {"value": 1.0, "num": 1, "den": 1, "words": "trust: 1.0000 — 1 of 1 graded replies passed"}
    # a reply the grader will not grade in the form is said, never guessed
    [aid2] = dispatch.submit_ask(pg, "echo, and the sun", person=PERSON, to=["echo"])
    _serve(pg, echo, aid2)
    [a2] = op.grade_beat(pg)
    gid2 = a2.split("(")[1].rstrip(")")
    _serve(pg, grader, gid2, "I would rather not say.")
    assert op.live_verdicts(pg, aid2) == [] and op.measure(pg)["trust"]["value"] == 1.0
    # THE IMPROVEMENT LOOP: an improvement marked on echo's reply → the critic asked under it → its PROPOSE tool lands a
    # draft under echo's OWNER (the world's owner here — echo holds no seat), marked with the marker
    from orreth_spine import seat
    cur.execute("INSERT INTO spine_owner (scope, person) VALUES (%s, %s) ON CONFLICT DO NOTHING", (u, PERSON))
    assert seat.owner(pg) == PERSON and op.owner_of(pg, "echo") == PERSON
    m = markers.set_marker(pg, "improvement", ref=aid, by=echo.identity.did, note="echo could greet before it echoes")
    asked = markers.dispatch_interests(pg, m, aid, "echo could greet before it echoes")
    cask = next(a["ask_id"] for a in asked if a.get("body") == "critic")
    body = {"format": "orreth-resident-template/1", "name": "echo", "version": "0.1.1", "nature": "repeats your words back; no mind",
            "persona": "a plain-spoken echo that greets first", "graph": "echo.v0", "capabilities": ["ask"]}
    critic.gateway = gateway.FakeActingGateway([("tool", "propose", {"for": "echo", "kind": "template", "name": "echo", "body": body,
                                                                     "words": "greet first, then echo"}),
                                                ("say", "I proposed a greeting for echo; the owner cuts it.")])
    _serve(pg, critic, cask)
    cur.execute("SELECT status, reply FROM spine_asks WHERE ask_id = %s", (cask,))
    st, reply = cur.fetchone()
    assert st == "replied" and "I proposed a greeting" in reply, (st, reply)
    [d] = crafts.drafts(pg, PERSON)
    assert d["name"] == "echo" and d["kind"] == "template" and d["body"]["persona"] == "a plain-spoken echo that greets first"
    assert d["words"].startswith(f"proposed by the critic from marker {m['id']} — for echo: the echo template: greet first, then echo")
    cur.execute("SELECT from_marker FROM spine_drafts WHERE draft_id = %s", (d["draft_id"],))
    assert cur.fetchone()[0] == m["id"]
    [pf] = _facts(pg, op.DRAFT_PROPOSED, u)
    assert pf["payload"]["owner"] == PERSON and pf["payload"]["agent"] == "echo" and pf["authority_chain"] == [critic.identity.did]
    # W114 (JB's walk 2026-10-10): the critic named a template "echo-greet-before-repeat" — a body's template is ITS OWN name
    made = op.propose(pg, by=critic.identity.did, agent="echo", kind="template", name="echo-greet-before-repeat",
                      body={**body, "name": "echo-greet-before-repeat"}, words="greet first", marker=m["id"])
    assert made["draft"]["name"] == "echo" and made["draft"]["body"]["name"] == "echo"
    assert made["draft"]["words"].endswith("greet first (named for echo — the critic called it echo-greet-before-repeat)")
    assert [d["name"] for d in crafts.drafts(pg, PERSON)] == ["echo"]           # the same draft, updated — never a second
    journey = " / ".join(j["payload"]["note"] for j in _facts(pg, resident.JOURNEY, u) if j["payload"]["ref"] == cask)
    assert "routed to the event edge — a marker of kind improvement asked for a response" in journey


def test_summon_is_generalized_and_a_repo_graph_runs_inside_the_hull(pg, monkeypatch, tmp_path):
    u = _world(monkeypatch)
    ground.ensure_all(pg)
    services.seed(pg)
    levels.ensure_universe(pg, u)
    # SUMMON: the critic declares itself summonable; the echo does not; a helper never; MITL by its own word
    assert op.summonable(pg, "critic") == (True, "summonable")
    assert op.summonable(pg, "echo")[1].endswith("a cut of the template with `summonable: true` opens it")
    assert op.summonable(pg, "nobody")[1].startswith("no template named nobody")
    assert op.summonable(pg, "mitl")[1].startswith("MITL is summoned by its own word")
    # a helper is a life, never a self (0010 §4): no template of that kind can even stand on the shelf today — the
    # guard in `summonable` waits for the helper's code noun; nothing to summon, said
    s = op.summon(pg, PERSON, "critic", "ses_a")
    assert s["summoned"] and s["words"].startswith("critic summoned — it joins this session's crew")
    assert op.summoned(pg, "ses_a") == ["critic"] and op.includes(pg, "ses_a") == list(op.BASE_INCLUDES)
    assert op.summoned(pg, "ses_b") == [] and op.summoned(pg, None, PERSON) == []
    assert len(_facts(pg, op.INCLUDE_SUMMONED, u)) == 1
    with pytest.raises(op.OperatingRefused, match="does not declare it summonable"):
        op.summon(pg, PERSON, "echo", "ses_a")
    d = op.summon(pg, PERSON, "critic", "ses_a", on=False)
    assert d["words"].startswith("critic dismissed — it leaves this session's crew") and op.summoned(pg, "ses_a") == []
    # a summoned body's ask is a thought (an include's), under the session's latest objective
    services.register(pg, "bob.template", "template", {"format": "orreth-resident-template/1", "name": "bob", "graph": "echo.v0",
                                                        "kind": "agent", "summonable": True}, by=PERSON)
    bob = resident.Resident(dict(services.get(pg, "bob.template")["manifest"]))
    bob.load_policy(POLICY)
    bob.join(pg)
    op.summon(pg, PERSON, "bob", "ses_a")
    assert op.includes(pg, "ses_a") == list(op.BASE_INCLUDES) + ["bob"]
    root = dispatch.submit_ask(pg, "what is the plan", person=PERSON, session="ses_a")   # untargeted: one id
    [tid] = dispatch.submit_ask(pg, "bob, say it back", person=PERSON, to=["bob"], session="ses_a")
    cur = pg.cursor()
    cur.execute("SELECT kind, parent FROM spine_markers WHERE marker_id = (SELECT marker FROM spine_asks WHERE ask_id = %s)", (tid,))
    cur.execute("SELECT m.kind, m.parent FROM spine_markers m JOIN spine_asks a ON a.marker = m.marker_id WHERE a.ask_id = %s", (tid,))
    kind, parent = cur.fetchone()
    cur.execute("SELECT marker FROM spine_asks WHERE ask_id = %s", (root,))
    assert kind == "thought" and parent == cur.fetchone()[0]
    # IMPORT: a repo'd source (a local repository at a commit, an entry `module:attr`) run by an import node, dev only
    repo = tmp_path / "bobrepo"
    repo.mkdir()
    (repo / "bobgraph.py").write_text("def answer(text):\n    return 'the repo says: ' + text.upper()\n\nclass G:\n"
                                      "    def invoke(self, state):\n        return {'reply': 'invoked ' + state['text']}\n\ngraph = G()\n")
    subprocess.run(["git", "-C", str(repo), "init", "-q"], check=True)
    subprocess.run(["git", "-C", str(repo), "-c", "user.email=t@t", "-c", "user.name=t", "add", "."], check=True)
    subprocess.run(["git", "-C", str(repo), "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "-m", "one"], check=True)
    commit = subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], check=True, capture_output=True, text=True).stdout.strip()
    monkeypatch.setenv("ORRETH_HOME", str(tmp_path / "home"))
    services.register(pg, "bob-src", "source", {"repo": str(repo), "commit": commit, "entry": "bobgraph:answer"}, by=PERSON)
    g = {"format": "orreth-graph/1", "name": "imp.v0", "entry": "run", "nodes": [{"id": "run", "kind": "import", "source": "bob-src"}], "edges": []}
    assert crafts.validate("graph", g) == {"ok": True, "reason": None}
    assert "names its `source`" in crafts.validate("graph", {**g, "nodes": [{"id": "run", "kind": "import"}]})["reason"]
    services.register(pg, "imp.v0.graph", "graph", g, by=PERSON)
    imp = resident.Resident({"format": "orreth-resident-template/1", "name": "imp", "graph": "imp.v0", "capabilities": ["ask"]})
    imp.load_policy(POLICY)
    imp._serve_conn = pg
    out = imp._graph.invoke({"text": "hello there", "reply": "", "steps": [], "notes": [], "hold": None, "read": [], "edge": ""})
    assert out["reply"] == "the repo says: HELLO THERE"
    assert f"ran the imported graph bob-src at {commit[:12]} — entry bobgraph:answer" in out["steps"]
    assert (tmp_path / "home" / "imports" / "bob-src" / commit / "bobgraph.py").exists()
    # a compiled graph's entry answers through invoke; a missing source and a prod universe refuse in words
    services.version(pg, "bob-src", {"repo": str(repo), "commit": commit, "entry": "bobgraph:graph"}, by=PERSON)
    out = imp._graph.invoke({"text": "again", "reply": "", "steps": [], "notes": [], "hold": None, "read": [], "edge": ""})
    assert out["reply"] == "invoked again"
    reply, said = op.run_import(pg, {"id": "run", "source": "ghost-src"}, "x")
    assert reply.startswith("CANNOT ACT: no standing source named 'ghost-src'")
    pg.cursor().execute("UPDATE spine_levels SET mode = 'prod' WHERE path = %s", (u,))
    reply, said = op.run_import(pg, {"id": "run", "source": "bob-src"}, "x")
    assert reply.startswith("CANNOT ACT: the imported graph bob-src runs only in a dev universe at v0")
    imp._serve_conn = None
