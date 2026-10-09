# PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch Phase 8 THE WORKSHOP sp4, THE EXPERIMENT AND THE CUT · 2026-10-07
"""THE EXPERIMENT AND THE CUT on the reference (canon 0010 §5 · 0005 Phase 8 sp4): an agent's cut
OPENS the Experiment (held at L2, the golden set required) — an experiment room on a floor of the
path, the candidate as a TRIAL LIFE of the agent's own self in the room (its wear at the room's
scope, the standing life's untouched), the golden set run through its own graph and recorded under
the kernel's run id; the grader and the critic asked under the experiment's marker (the hull's
event edge), each writing a SIGNED verdict under its own DID (rule 2) — the kernel's record of the
arms is what they grade, never their own words; the proposal composed with every reviewer named (a chip not seated said as MISSING — Phase 8 sp6 filled the empty slots);
the stamped promotion (L2) landing the sibling version, the seat and the draft spent, the kernel's
hand owed after the commit; the ladder — rest (L2) · decommission (L3: the live objects removed,
the DID and the joins kept) · restore (a new life, refused while the template is retired); the prune
beat retiring what nobody wears and keeping the spine's own."""
import json
import secrets
from pathlib import Path

import pytest

from orreth_spine import crafts, dispatch, envelope as ev, experiments as xp, gateway, ground, levels, markers, proof, resident, services

SPINE = Path(__file__).resolve().parents[1]
POLICY = SPINE / "policy" / "covenant-policy.v1.json"
PERSON = "did:orreth:person:test"


def _world(monkeypatch):
    u = "u:xp-" + secrets.token_hex(3)
    monkeypatch.setenv("SPINE_SCOPE", u)
    monkeypatch.delenv("SPINE_MODE", raising=False)
    return u


def _body(template, gw=None):
    r = resident.Resident(SPINE / "templates" / template, gateway=gw)
    r.load_policy(POLICY)
    return r


def _facts(pg, type_, u=None):
    """The facts of one type on the session's ground — this world's alone when `u` is given (the
    test schema is shared by every test of the session)."""
    cur = pg.cursor()
    cur.execute("SELECT body FROM spine_outbox ORDER BY outbox_id")
    out = []
    for (body,) in cur.fetchall():
        try:
            e = ev.decode(bytes(body))
        except Exception:                       # noqa: BLE001
            continue
        if e.get("type") == type_ and (u is None or e.get("universe_id") == u):
            out.append(e)
    return out


def _cut(pg, kind, name, body):
    d = crafts.save_draft(pg, PERSON, kind, name, body)
    held = crafts.hold_cut(pg, PERSON, d["draft_id"])
    out = proof.settle_kernel_act(pg, held, approve=True, by=PERSON)
    assert out["status"] == "replied", out
    return out


def exp_missing_chips(rv):
    """Phase 8 sp6: with no chip seated in this world, each slot is an honest MISSING, never an empty slot by law."""
    return rv["identity"]["missing"] == "the identity is not seated here — no verdict" and \
        rv["security"]["missing"] == "the security is not seated here — no verdict"


def _serve(pg, body, ask_id, reply):
    """A body serves one ask in-process through its whole hull, its mind scripted."""
    body.gateway = gateway.FakeGateway(reply=reply)
    body._serve_conn = pg
    with pg.transaction():
        body._serve_ask(pg.cursor(), ask_id, [PERSON])
    body._serve_conn = None


def test_the_law_is_pure():
    assert xp.room_name("bob", 2) == "exp-bob-2"
    assert xp.arms_plan(None).startswith("one arm — the candidate alone")
    assert xp.arms_plan(3) == "two arms — the standing version 3 and the candidate"
    assert xp.grade_of("current: B — fine\n**candidate: A** — better\nverdict: candidate") == \
        {"current": "B", "candidate": "A", "verdict": "candidate"}
    assert xp.grade_of("current: none\ncandidate: C\nverdict: neither") == {"current": None, "candidate": "C", "verdict": "neither"}
    assert xp.grade_of("I decline.") == {"current": None, "candidate": None, "verdict": None}
    assert xp.risk_of("risk: HIGH — it rewrites the entry") == "high" and xp.risk_of("no form") is None
    assert xp.promote_demand("agent") == {"ok": True, "level": "L2", "reason": None}
    assert xp.promote_demand("resident")["level"] == "L3-code" and not xp.promote_demand("firmware")["ok"]
    assert xp.ladder_legal("active", "rested") and xp.ladder_legal("rested", "decommissioned")
    assert xp.ladder_legal("decommissioned", "active") and not xp.ladder_legal("active", "decommissioned")
    assert xp.ladder_refusal("bob", None, "rested").startswith("bob holds no seat this kernel wrote")
    assert xp.ladder_refusal("bob", "active", "decommissioned") == "bob is active — rest it first; the grave takes a rested body"
    assert xp.deploy_at("u:dev", None, None) == "u:dev" and xp.deploy_at("u:dev", "f:ops", "u:dev/f:x") == "u:dev/f:ops"
    assert xp.deploy_at("u:dev", None, "u:dev/f:ops") == "u:dev/f:ops"
    exp = {"agent": "bob", "current_version": 1,
           "arms": {"candidate": {"passed": 3, "failed": 0}, "current": {"passed": 2, "failed": 1}},
           "reviewers": {"grader": {"verdict": {"current": "B", "candidate": "A", "verdict": "candidate"}, "signed": True},
                         "critic": {"risk": "low", "line": "one node"}}, "resiliency": {"reds": 0}}
    assert xp.leaning_of(exp) == "promote"
    w = xp.proposal_words(exp)
    assert w.startswith("THE EXPERIMENT on bob proposes: the candidate passed 3 of 3 · the standing version 1 passed 2 of 3 · "
                        "the grader (signed) grades the candidate A and the current B and names candidate · the critic reads the "
                        "risk as low: one node · the identity chip: no verdict yet · the security chip: no review yet")
    # Phase 8 sp6: the chips' words on the card, and their holds
    exp["reviewers"]["identity"] = {"identity": "kept", "line": "the same self"}
    exp["reviewers"]["security"] = {"security": "clear", "line": "nothing widened"}
    assert "the identity chip finds the trial life's claims kept: the same self · the security chip reads the candidate as clear: nothing widened" in xp.proposal_words(exp)
    assert xp.leaning_of(exp) == "promote"
    exp["reviewers"]["security"] = {"security": "concern", "line": "a tool widened"}
    assert xp.leaning_of(exp) == "hold"
    exp["reviewers"]["security"] = {"missing": "the security is not seated here — no verdict"}
    exp["reviewers"]["identity"] = {"identity": "broken", "line": "another self"}
    assert xp.leaning_of(exp) == "hold" and "the security chip: the security is not seated here — no verdict" in xp.proposal_words(exp)
    del exp["reviewers"]["identity"]; del exp["reviewers"]["security"]
    assert "resiliency: no watch turned red while the arms ran. the evidence leans to promote." in w
    assert "say “promote bob” (or “promote bob to floor <name>”) — or “decline the bob experiment”" in w
    exp["arms"]["candidate"]["failed"] = 1
    assert xp.leaning_of(exp) == "hold"
    exp["arms"]["candidate"]["failed"] = 0; exp["reviewers"] = {}
    assert xp.leaning_of(exp) == "unsure"


def test_an_agents_cut_opens_the_experiment_and_the_proposal_is_the_humans(pg, monkeypatch):
    u = _world(monkeypatch)
    ground.ensure_all(pg)
    services.seed(pg)
    # the floor the room opens on, as the crew manifest declares it
    levels.ensure_universe(pg, u)
    levels.declare(pg, u, {"levels": [{"at": "f:ops"}], "seats": []})
    # the agent's components: a graph of one echo node, its golden set — born with it
    _cut(pg, "graph", "bob.v0", {"entry": "say", "nodes": [{"id": "say", "kind": "echo"}], "edges": []})
    # an agent template without its golden set refuses in words — the evidence is required
    d = crafts.save_draft(pg, PERSON, "template", "bob", {"kind": "agent", "graph": "bob.v0", "nature": "a test agent", "capabilities": ["ask"]})
    with pytest.raises(crafts.CraftRefused, match="bob has no golden set on the shelf"):
        crafts.cut_check(pg, PERSON, d["draft_id"])
    _cut(pg, "golden", "bob", crafts.golden_document("bob", [{"ask": "hello bob", "expect": ["hello"]}, {"ask": "say moon", "expect": ["moon"]}]))
    c = crafts.cut_check(pg, PERSON, d["draft_id"])
    assert (c["gate"], c["verb"], c["level"], c["room"], c["cases"], c["current_version"]) == \
        ("experiment", "experiment", "L2", f"{u}/f:ops/r:exp-bob-1", 2, None)
    # the cut HOLDS the Experiment's opening at L2 — in words
    held = crafts.hold_cut(pg, PERSON, d["draft_id"])
    cur = pg.cursor()
    cur.execute("SELECT text, held FROM spine_asks WHERE ask_id = %s", (held,))
    text, h = cur.fetchone()
    assert text.startswith("opening an experiment on the bob agent — room exp-bob-1 on floor ops of universe")
    assert "one arm — the candidate alone" in text and "its golden set (2 cases)" in text
    assert json.loads(h)["tool"] == "experiment.open" and json.loads(h)["level"] == "L2"
    assert xp.listing(pg) == []                                                     # nothing before the yes
    out = proof.settle_kernel_act(pg, held, approve=True, by=PERSON)
    assert out["status"] == "replied" and out["reply"].startswith("Done, on your word: room exp-bob-1 on floor ops")
    assert "is open as an experiment room and the experiment exp_" in out["reply"]
    room = levels.row(pg, f"{u}/f:ops/r:exp-bob-1")
    assert room and room["experiment"] is True and room["mode"] == "dev"
    [e] = xp.listing(pg)
    exp = xp.get(pg, e["experiment_id"])
    assert exp["state"] == "running" and exp["arms"]["current"] is None and exp["arms"]["candidate"]["run_id"] is None
    assert set(exp["reviewers"]) == {"grader", "critic", "security", "identity"} and all(v == {"ask_id": None} for v in exp["reviewers"].values())   # Phase 8 sp6: four reviewers, no empty slot
    mk = markers.get(pg, exp["marker"])
    assert mk["kind"] == "experiment" and mk["ref"] == exp["experiment_id"]
    assert len(_facts(pg, xp.EXPERIMENT_OPENED, u)) == 1 and _facts(pg, xp.EXPERIMENT_OPENED, u)[0]["scope_path"] == exp["room"]
    assert crafts.draft(pg, PERSON, d["draft_id"]) is not None                      # the draft stands until the promotion
    # THE BEAT, step 1: the trial life — the candidate as a life of bob's own self IN THE ROOM
    ran = {}

    def spawn(x):
        ran["run"] = xp.trial(pg, x, gateway=None, home=None, policy=POLICY)        # in-process here (a thread on the rig)
    moved = xp.beat(pg, spawn_trial=spawn, publish=None)
    assert any("trial life spawned" in m for m in moved)
    assert ran["run"]["passed"] == 2 and ran["run"]["failed"] == 0
    cur.execute("SELECT name, life, scope, kind FROM spine_joins WHERE name = 'bob' AND scope LIKE %s || '/%%' ORDER BY join_id", (u,))
    assert cur.fetchall() == [("bob", 1, exp["room"], "agent")]                      # one life, in the room, an agent (this world's — the session's schema is shared)
    cur.execute("SELECT component, scope, until IS NOT NULL FROM spine_wear WHERE body = 'bob' AND scope LIKE %s || '/%%' ORDER BY component", (u,))
    worn = cur.fetchall()
    assert [w[0] for w in worn] == ["bob.golden", "bob.template", "bob.v0.graph", "the-orreth-covenant.policy"]
    assert all(w[1] == exp["room"] and w[2] for w in worn)                           # at the room's scope; closed when the trial ended
    # step 2: the run read; no reviewer is seated in this world yet → both slots say so, honestly
    moved = xp.beat(pg, spawn_trial=spawn, publish=None)
    exp = xp.get(pg, e["experiment_id"])
    assert exp["arms"]["candidate"]["passed"] == 2 and any("the candidate ran — 2 passed, 0 failed" in m for m in moved)
    assert exp["state"] == "proposed" and exp["leaning"] == "unsure"
    assert "the grader: the grader is not seated here — no verdict" in exp["proposal"]
    assert "the critic: the critic is not seated here — no verdict" in exp["proposal"]
    assert "resiliency: no watch turned red while the arms ran" in exp["proposal"]
    assert len(_facts(pg, xp.EXPERIMENT_PROPOSED, u)) == 1
    # the human declines: recorded, the draft stays, the room stands
    out = xp.decline(pg, PERSON, exp["experiment_id"])
    assert out["state"] == "declined" and crafts.draft(pg, PERSON, d["draft_id"]) is not None
    assert xp.get(pg, exp["experiment_id"])["state"] == "declined" and levels.row(pg, exp["room"]) is not None
    with pytest.raises(xp.ExperimentRefused, match="already declined"):
        xp.decline(pg, PERSON, exp["experiment_id"])


def test_the_reviewers_sign_their_verdicts_and_the_promotion_seats_the_agent(pg, monkeypatch, tmp_path):
    u = _world(monkeypatch)
    home = tmp_path / "agents"                      # bob's self survives its lives: the trial, then the seat (rule 1)
    ground.ensure_all(pg)
    services.seed(pg)
    levels.ensure_universe(pg, u)
    levels.declare(pg, u, {"levels": [{"at": "f:ops"}], "seats": []})
    _cut(pg, "graph", "bob.v0", {"entry": "say", "nodes": [{"id": "say", "kind": "echo"}], "edges": []})
    _cut(pg, "golden", "bob", crafts.golden_document("bob", [{"ask": "hello bob", "expect": ["hello"]}]))
    # the grader and the critic seated in this world (joined), so the kernel may ask them
    grader, critic = _body("firmware-grader.v0.json"), _body("firmware-critic.v0.json")
    grader.join(pg); critic.join(pg)
    d = crafts.save_draft(pg, PERSON, "template", "bob", {"kind": "agent", "graph": "bob.v0", "nature": "a test agent", "capabilities": ["ask"]})
    held = crafts.hold_cut(pg, PERSON, d["draft_id"])
    proof.settle_kernel_act(pg, held, approve=True, by=PERSON)
    [e] = xp.listing(pg)
    xid = e["experiment_id"]
    xp.beat(pg, spawn_trial=lambda x: xp.trial(pg, x, gateway=None, home=home, policy=POLICY), publish=None)
    moved = xp.beat(pg, spawn_trial=None, publish=None)
    assert any("the reviewers were asked — grader, critic" in m for m in moved), moved
    assert exp_missing_chips(xp.get(pg, xid)["reviewers"])
    exp = xp.get(pg, xid)
    g_ask, c_ask = exp["reviewers"]["grader"]["ask_id"], exp["reviewers"]["critic"]["ask_id"]
    cur = pg.cursor()
    cur.execute("SELECT text, marker FROM spine_asks WHERE ask_id = %s", (g_ask,))
    text, mk = cur.fetchone()
    assert text.startswith(f"grader, review experiment {xid} on the bob agent (one arm — the candidate alone")
    assert "case 1: asked 'hello bob'; expected hello; replied 'hello bob' — passed" in text
    assert "Answer in exactly this form" in text and markers.get(pg, mk)["parent"] == exp["marker"]
    # nothing settles while the reviewers think
    assert xp.beat(pg, spawn_trial=None, publish=None) == [] and xp.get(pg, xid)["state"] == "running"
    # the grader serves through its hull: the EVENT edge, the kernel's evidence in its recall (never its own words),
    # its reply in the form, its SIGNED verdict written under its own DID in the reply's transaction
    _serve(pg, grader, g_ask, "current: none\ncandidate: A — the echo answered every case\nverdict: candidate")
    cur.execute("SELECT status, reply FROM spine_asks WHERE ask_id = %s", (g_ask,))
    st, reply = cur.fetchone()
    assert st == "replied" and reply.startswith("current: none")
    [v] = xp.verdicts(pg, xid)
    assert (v["reviewer"], v["by"], v["by_name"]) == ("grader", grader.identity.did, "grader")
    assert v["verdict"] == {"current": None, "candidate": "A", "verdict": "candidate"} and len(v["sig"]) == 128
    assert grader.identity.sign({"experiment": xid, "reviewer": "grader", "verdict": v["verdict"], "by": grader.identity.did, "on_ask": None}) == v["sig"]
    [vf] = _facts(pg, xp.VERDICT, u)
    assert vf["authority_chain"] == [grader.identity.did] and vf["payload"]["sig"] == v["sig"]
    journey = " / ".join(j["payload"]["note"] for j in _facts(pg, resident.JOURNEY, u) if j["payload"]["ref"] == g_ask)
    assert "wrote my signed verdict on the experiment" in journey, journey
    assert "routed to the event edge" in journey, journey
    _serve(pg, critic, c_ask, "the candidate is bob's first version — one echo node.\nrisk: low — nothing stands to break")
    moved = xp.beat(pg, spawn_trial=None, publish=None)
    exp = xp.get(pg, xid)
    assert exp["state"] == "proposed" and exp["leaning"] == "promote", moved
    assert exp["reviewers"]["grader"]["signed"] is True and exp["reviewers"]["critic"]["risk"] == "low"
    assert exp["proposal"].startswith("THE EXPERIMENT on bob proposes: the candidate passed 1 of 1 · no current arm — the first version · "
                                      "the grader (signed) grades the candidate A and names candidate · the critic reads the risk as low: "
                                      "nothing stands to break · the identity chip: the identity is not seated here — no verdict · "
                                      "the security chip: the security is not seated here — no verdict")
    # THE PROMOTION — the human's stamped act at L2; where the next life stands is a field of it
    with pytest.raises(xp.ExperimentRefused, match="is an experiment room — nothing stands there but an arm"):
        xp.promote_check(pg, PERSON, xid, at=exp["room"])
    with pytest.raises(xp.ExperimentRefused, match="is not open"):
        xp.promote_check(pg, PERSON, xid, at="f:nowhere")
    hands = []
    xp.HOOKS["seat"] = lambda name, at, version: hands.append(("seat", name, at, version))
    xp.HOOKS["rest"] = lambda name: hands.append(("rest", name))
    was_queue = xp.HOOKS.get("queue")
    xp.HOOKS["queue"] = None                                   # the session's rig may hold the bench hand — this proof reads the ground's words alone
    try:
        made = xp.hold_promote(pg, PERSON, xid, at="f:ops")
        assert (made["level"], made["version"], made["at"]) == ("L2", 1, f"{u}/f:ops")
        cur.execute("SELECT text FROM spine_asks WHERE ask_id = %s", (made["held"],))
        assert cur.fetchone()[0] == "promoting bob to version 1 — its next life stands on floor ops of universe " + u[2:]
        assert services.get(pg, "bob.template") is None and hands == []
        out = proof.settle_kernel_act(pg, made["held"], approve=True, by=PERSON)
        assert out["reply"].startswith("Done, on your word: bob.template is version 1 on the shelf (pin ")
        assert "bob's next life stands on floor ops" in out["reply"] and "the draft is spent" in out["reply"]
        row = services.get(pg, "bob.template")
        assert row["version"] == 1 and row["manifest"]["kind"] == "agent" and row["last_health"]["ok"] is True
        assert crafts.draft(pg, PERSON, d["draft_id"]) is None
        assert xp.get(pg, xid)["state"] == "promoted" and xp.get(pg, xid)["at_path"] == f"{u}/f:ops"
        assert xp.seat_of(pg, "bob") == {**xp.seat_of(pg, "bob"), "state": "active", "at_path": f"{u}/f:ops", "version": 1, "template": "bob.template"}
        assert hands == [("seat", "bob", f"{u}/f:ops", 1)]                        # the hand ran AFTER the commit
        [sf] = _facts(pg, xp.EXPERIMENT_SETTLED, u)
        assert sf["payload"]["settled"] == "promoted" and sf["scope_path"] == f"{u}/f:ops"
        with pytest.raises(xp.ExperimentRefused, match="is promoted — only a proposed experiment promotes"):
            xp.promote_check(pg, PERSON, xid)
        # bob's next life: the body born from the shelf's standing version, its wear re-pointed at version 1
        bob = resident.Resident(dict(row["manifest"]), home=home, scope=f"{u}/f:ops")
        bob.load_policy(POLICY)
        joined = bob.join(pg)
        assert joined["life"] == 2                                                   # the trial was life 1 — the same self
        assert [(w["component"], w["version"]) for w in crafts.wears(pg, bob.identity.did) if w["component"] == "bob.template"] == [("bob.template", 1)]
        # THE LADDER: a crew body holds no seat; bob rests (L2), the grave takes a rested body (L3), restore is a new life
        with pytest.raises(xp.ExperimentRefused, match="grader holds no seat this kernel wrote"):
            xp.hold_rest(pg, PERSON, "grader")
        with pytest.raises(xp.ExperimentRefused, match="bob is active — rest it first; the grave takes a rested body"):
            xp.hold_decom(pg, PERSON, "bob")
        hands.clear()
        r = xp.hold_rest(pg, PERSON, "bob")
        out = proof.settle_kernel_act(pg, r["held"], approve=True, by=PERSON)
        assert out["reply"] == "Done, on your word: bob is at rest — its life stopped at a safe boundary, its self kept, its record whole; say “restore bob” for a new life or “decommission bob” for the grave."
        assert xp.seat_of(pg, "bob")["state"] == "rested" and hands == [("rest", "bob")]
        assert crafts.wears(pg, bob.identity.did) == []                             # the wear links closed at the rest
        with pytest.raises(xp.ExperimentRefused, match="bob is rested — only an active body rests"):
            xp.hold_rest(pg, PERSON, "bob")
        # the grave (L3-code): live objects removed, the DID and the joins kept
        cur.execute("INSERT INTO spine_leases (did, name, kind, scope, until) VALUES (%s, 'bob', 'agent', %s, now() + interval '1 hour')",
                    (bob.identity.did, f"{u}/f:ops"))
        cur.execute("INSERT INTO spine_mind_assignments (subject, scope, klass, stall, by_did) VALUES ('bob', %s, 'default', 'haiku', %s)", (u, PERSON))
        g = xp.hold_decom(pg, PERSON, "bob")
        assert g["level"] == "L3-code"
        out = proof.settle_kernel_act(pg, g["held"], approve=True, by=PERSON, level="L3-code")
        assert out["reply"].startswith("Done, on your code: bob is decommissioned — removed: its lease, its mind assignment; its DID did:orreth:")
        assert ", its joins and its record stay; say “restore bob” for a new life from the shelf." in out["reply"]
        assert xp.seat_of(pg, "bob")["state"] == "decommissioned"
        cur.execute("SELECT count(*) FROM spine_joins WHERE did = %s", (bob.identity.did,))
        assert cur.fetchone()[0] == 2                                                # the joins stay
        cur.execute("SELECT count(*) FROM spine_leases WHERE did = %s", (bob.identity.did,))
        assert cur.fetchone()[0] == 0
        [df] = _facts(pg, xp.BODY_DECOMMISSIONED, u)
        assert df["payload"]["removed"] == ["its lease", "its mind assignment"] and "its DID, its joins and its record" in df["payload"]["kept"]
        # THE PRUNE BEAT: bob's own crafts, worn by no body now and every wearer in the grave, are retired; the spine's own kept
        pruned = sorted(p["component"] for p in xp.prune(pg))
        assert pruned == ["bob.golden", "bob.template", "bob.v0.graph"]
        assert services.get(pg, "bob.v0.graph")["state"] == "retired" and services.get(pg, "the-orreth-covenant.policy")["state"] != "retired"
        assert services.get(pg, "bob.v0.graph")["last_health"]["detail"] == "pruned by the beat — worn by no body since bob was decommissioned"
        assert xp.prune(pg) == []                                                    # once
        # restore: a NEW life from the shelf — refused while the template is retired, then owed to the kernel's hand
        with pytest.raises(xp.ExperimentRefused, match="bob.template is retired from the shelf — restore the template first"):
            xp.restore_in(pg, {"name": "bob"}, PERSON)
        services.restore(pg, "bob.template", by=PERSON)
        hands.clear()
        rs = xp.hold_restore(pg, PERSON, "bob")
        out = proof.settle_kernel_act(pg, rs["held"], approve=True, by=PERSON)
        assert out["reply"] == f"Done, on your word: bob returns — a new life from the shelf's standing version, on floor ops of universe {u[2:]}; never a revival."
        assert xp.seat_of(pg, "bob")["state"] == "active" and hands == [("seat", "bob", f"{u}/f:ops", 1)]
    finally:
        xp.HOOKS.update({"seat": None, "rest": None, "queue": was_queue})
        xp.PENDING_HANDS.clear()
