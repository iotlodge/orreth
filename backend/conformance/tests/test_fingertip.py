# PROVENANCE: authored by Fable 5 (claude-fable-5), 2026-07-11 — 0027, the Fingertip
"""The Fingertip (0027): the universe as node graph — dispatch down, review up,
the human at the top. Templates refused-at-save; intentions carry nothing extra;
standing jobs never complete."""
import pytest

from orreth_sim import fingertip
from orreth_sim.world import build


@pytest.fixture()
def world():
    return build()


def _tidy_think(_klass, prompt):
    """A fingertip that finishes first cycle — the clean path."""
    if "Plan the MINIMUM" in prompt:
        return "OBSERVE reason: the assigned sliver"
    if "Answer concisely" in prompt:
        return "considered"
    return "DONE: sliver satisfied."


# ---------------------------------------------------------------- the template gate
def test_workflow_template_gates_refuse_at_save():
    """0008's discipline kept: tampering, missing intents, and a missing human top
    all refuse at SAVE — never at incident review."""
    spec = fingertip.workflow_template(
        "u:demo", name="product-dev",
        intentions=[{"id": "design", "intent": "draft the approach"}])
    fingertip.check_workflow(spec)                      # well-formed passes
    moved = dict(spec, title="renamed-under-its-id")
    with pytest.raises(fingertip.WorkflowError):
        fingertip.check_workflow(moved)                 # the artifact moved
    # the human's request IS the top (JB lock 2026-07-11): a non-standing
    # workflow without the human node is refused
    headless = fingertip.workflow_template(
        "u:demo", name="x", intentions=[{"id": "a", "intent": "b"}])
    headless["nodes"] = [n for n in headless["nodes"] if n.get("role") != "human"]
    headless["id"] = fingertip.crypto.content_hash(fingertip._content(headless))
    with pytest.raises(fingertip.WorkflowError):
        fingertip.check_workflow(headless)
    # and a standing job must NOT have one — no completion condition exists
    standing = fingertip.workflow_template(
        "u:demo", name="monitor", standing=True,
        intentions=[{"id": "watch", "intent": "review the floors"}])
    fingertip.check_workflow(standing)
    assert not any(n.get("role") == "human" for n in standing["nodes"])


def test_template_is_a_versioned_artifact_in_memory(world):
    """R8: config IS memory — the template lands as a signed record."""
    spec = fingertip.workflow_template(
        "u:demo", name="product-dev",
        intentions=[{"id": "design", "intent": "draft the approach"}])
    rid = fingertip.save_template(world.universe, spec)
    rec = world.universe.records[rid]
    assert "workflow-template" in rec["tags"] and "product-dev" in rec["tags"]


# ---------------------------------------------------------------- the intention contract
def test_intention_carries_the_intention_and_nothing_else():
    """0027 §3 · 0030 · 0033 §4: one intent, a budget slice, citation refs, and its
    own content-address — never the plan, never the siblings, never the why. The
    id is the hash OF the other four fields: it provably smuggles nothing."""
    from orreth_sim import crypto
    s = fingertip.make_intention("sha256:goal", "test the widget", 300, ["sha256:ref1"])
    assert set(s) == {"id", "of", "intent", "budget", "refs"}
    assert s["budget"] == {"tokens": 300}
    assert s["id"] == crypto.content_hash({k: s[k] for k in
                                           ("of", "intent", "budget", "refs")})


def test_review_severity_rides_the_lanes():
    """0024 discharged: clean DONE → low; corrected DONE → medium; unfinished →
    high (the human's lane — unfinished work is where the risk lives)."""
    assert fingertip.review_severity("done", 1) == "low"
    assert fingertip.review_severity("done", 2) == "medium"
    assert fingertip.review_severity("parked", 2) == "high"


# ---------------------------------------------------------------- the Phase D gate
def test_the_gate_apertures_pin_runs_and_the_coordinate_is_hard(world):
    """0031 §2 + 0033 §4 at the gate (JB approvals 2026-07-15): the dispatching
    seat cuts a signed APERTURE per intention — everything by reference, the law
    cited within — every RunRecord pins it, and the outcome's COORDINATE is a
    first-class field: 'every Thought that served Objective O' is a field
    lookup, not a lineage recursion."""
    spec = fingertip.workflow_template(
        "u:demo", name="gate-proof",
        intentions=[{"id": "probe", "intent": "measure the thing",
                     "seat": "u:demo/e:cloud/f:prod"}])
    orch = fingertip.Orchestration(world.universe, world.becky, spec,
                                   "prove the gate", budget_tokens=1200)
    seats = {n.scope: n for n in (world.field_prod, world.eco_cloud)}
    out = orch.run(seats, world.beckys, _tidy_think, plan_approved=True)
    assert out["verification"] == "complete"
    # the aperture: assembled at dispatch, signed by the DISPATCHING seat,
    # written at the dispatcher's floor
    aps = [r for r in world.universe.records.values()
           if "aperture" in r.get("tags", [])]
    assert len(aps) == 1
    ap = aps[0]
    import json as _json
    from orreth_sim import crypto as _crypto
    a = _json.loads(_crypto._b64d(ap["body"]).decode())["aperture"]
    assert a["seat"] == orch.surface.identity["did"]     # the dispatcher signed
    assert a["task"]["intent"] == "measure the thing"
    from orreth_sim import resolver as _resolver
    # the law cited within is the resolver's own deterministic address — same
    # cascade ⇒ same hash, recomputable on demand (0007's law-as-lookup)
    assert a["law"] == _resolver.resolve(world.field_prod)["id"]
    assert a["behavior"]["profile"] and len(a["behavior"]["prompts"]) == 2
    # every RunRecord pins the whole opening (context_hash, widened semantics)
    runs = [r for r in world.field_prod.runs.values()
            if r.get("context_hash") == ap["id"]]
    assert runs, "no RunRecord pinned the aperture"
    # the coordinate is HARD: the outcome's address is a field, and the lookup
    # needs no tags and no recursion
    outcome = next(r for r in world.field_prod.records.values()
                   if "intention-outcome" in r.get("tags", []))
    assert outcome["coordinate"]["objective"] == orch.goal
    assert outcome["coordinate"]["intention"]            # the delegated unit, cited
    assert ap["coordinate"] == {"objective": orch.goal,
                                "intention": outcome["coordinate"]["intention"]}
    hard = [r for r in world.field_prod.records.values()
            if (r.get("coordinate") or {}).get("objective") == orch.goal]
    assert outcome in hard
    # and the assembly at home carries its address too
    assembly = next(r for r in world.universe.records.values()
                    if "objective-outcome" in r.get("tags", []))
    assert assembly["coordinate"] == {"objective": orch.goal}


# ---------------------------------------------------------------- the flow, end to end
def test_objective_dispatches_reviews_and_assembles(world):
    """The universe plans high, works low, reviews on the way back up — intentions
    execute at their seats, outcomes land there, critic markers land at home,
    and the assembly is a report, never a self-confirmation."""
    spec = fingertip.workflow_template(
        "u:demo", name="product-dev",
        intentions=[{"id": "design", "intent": "draft the approach",
                  "seat": "u:demo/e:cloud/f:prod"},
                 {"id": "ml", "intent": "train the ranking model",
                  "seat": "u:demo/e:dev/f:lab"}])       # cross-ecosystem dispatch
    orch = fingertip.Orchestration(world.universe, world.becky, spec,
                                   "build me a product that does FOO",
                                   budget_tokens=2400)
    seats = {n.scope: n for n in
             (world.field_prod, world.field_lab, world.eco_cloud, world.eco_dev)}
    out = orch.run(seats, world.beckys, _tidy_think, plan_approved=True)
    assert out["verification"] == "complete"
    assert {b["intention"] for b in out["branches"]} == {"design", "ml"}
    # outcomes landed AT the seats (R7: the outcome is what rides up)
    prod_outcomes = [r for r in world.field_prod.records.values()
                     if "intention-outcome" in r.get("tags", [])]
    lab_outcomes = [r for r in world.field_lab.records.values()
                    if "intention-outcome" in r.get("tags", [])]
    assert len(prod_outcomes) == 1 and len(lab_outcomes) == 1
    # the dispatching seat graded every return, on the record, author ≠ agent
    marks = [r for r in world.universe.records.values()
             if "marker" in r.get("tags", [])]
    assert len(marks) == 2
    # RunRecords landed at the seats per cycle (chassis law; scratch evaporated)
    assert world.field_prod.runs and world.field_lab.runs
    # the fingertips were the intention's life — retired after it
    assert world.field_prod.stamped_live == 0 and world.field_lab.stamped_live == 0
    # the assembly rode up as a record (what resolves the human's request)
    assert "objective-outcome" in world.universe.records[out["record"]]["tags"]


def test_hitl_question_parks_the_branch_until_answered(world):
    """0027 §8: a flow node asks the human; the branch parks (consequence waits,
    0012), the rest proceeds, and the answer resumes it — finished stays finished."""
    spec = fingertip.workflow_template(
        "u:demo", name="deploy-flow",
        intentions=[{"id": "build", "intent": "compile the artifact"},
                 {"id": "iac", "intent": "provision infrastructure",
                  "ask_human": "where shall this deploy?"}])
    orch = fingertip.Orchestration(world.universe, world.becky, spec,
                                   "ship the FOO service", budget_tokens=2400)
    seats, beckys = {}, world.beckys
    first = orch.run(seats, beckys, _tidy_think, plan_approved=True)
    assert first["verification"] == "partial"
    assert first["waiting_on_human"] == ["iac"]
    assert orch.questions() == [{"intention": "iac",
                                 "question": "where shall this deploy?"}]
    outcomes_before = sum(1 for r in world.universe.records.values()
                          if "intention-outcome" in r.get("tags", []))
    orch.answer_human("iac", "eu-west, the green account")
    second = orch.run(seats, beckys, _tidy_think, plan_approved=True)
    assert second["verification"] == "complete" and not orch.questions()
    iac = next(b for b in second["branches"] if b["intention"] == "iac")
    assert iac["status"] == "done"
    outcomes_after = sum(1 for r in world.universe.records.values()
                         if "intention-outcome" in r.get("tags", []))
    assert outcomes_after == outcomes_before + 1        # build did NOT re-run


def test_cross_ecosystem_dispatch_refuses_and_asks(world):
    """JB lock 2026-07-11: a dispatch the token does not cover goes dark AND
    stages a human-visible entitlement ask — the flow degrades honestly."""
    spec = fingertip.workflow_template(
        "u:demo/e:cloud/f:prod", name="overreach",
        intentions=[{"id": "local", "intent": "do the local part"},
                 {"id": "foreign", "intent": "borrow the lab",
                  "seat": "u:demo/e:dev/f:lab"}])
    b_prod = world.beckys["u:demo/e:cloud/f:prod"]
    orch = fingertip.Orchestration(world.field_prod, b_prod, spec,
                                   "a field-tier objective", budget_tokens=1200)
    out = orch.run({world.field_lab.scope: world.field_lab}, world.beckys,
                   _tidy_think, plan_approved=True)
    assert out["verification"] == "partial" and out["dark"] == ["foreign"]
    dark = next(b for b in out["branches"] if b["intention"] == "foreign")
    ask = world.field_prod.records[dark["entitlement_ask"]]
    assert "entitlement-ask" in ask["tags"]             # refused — and it ASKED
    # nothing executed at the lab: no outcome, no fingertip stamped
    assert not any("intention-outcome" in r.get("tags", [])
                   for r in world.field_lab.records.values())
    assert world.field_lab.stamped_live == 0


# ---------------------------------------------------------------- the standing job
def test_standing_monitor_beats_and_never_completes(world):
    """R8 + JB lock: the portfolio monitor is an immortal job — each beat writes
    one observation (aggregates only, 0005's sibling law), and there is no
    completion state to reach."""
    mon = fingertip.PortfolioMonitor(world.universe, world.becky)
    r1, r2 = mon.beat(), mon.beat()
    assert r1 != r2 and mon.beats == 2
    obs = [r for r in world.universe.records.values()
           if "portfolio-observation" in r.get("tags", [])]
    assert len(obs) == 2
    assert world.universe.stamped_live == 1             # alive — an organ, beating


# ---------------------------------------------------------------- 0030 §3: the plan gate
def test_origin_plans_wait_for_their_human(world):
    """JB canon 2026-07-12: an objective is curated into a plan, and the plan is
    HITL-approved BEFORE any intention fans. Without approval: staged, readable,
    and nothing moves anywhere."""
    spec = fingertip.workflow_template(
        "u:demo", name="gated",
        intentions=[{"id": "design", "intent": "draft the approach",
                     "seat": "u:demo/e:cloud/f:prod"}])
    orch = fingertip.Orchestration(world.universe, world.becky, spec,
                                   "a gated objective", budget_tokens=1200)
    seats = {world.field_prod.scope: world.field_prod}
    held = orch.run(seats, world.beckys, _tidy_think)          # no approval given
    assert held["status"] == "staged"
    assert held["plan"]["intentions"][0]["seat"] == "u:demo/e:cloud/f:prod"
    assert not orch.branches                                    # nothing fanned
    assert not any("intention-outcome" in r.get("tags", [])
                   for r in world.field_prod.records.values()) # nothing landed below
    out = orch.run(seats, world.beckys, _tidy_think, plan_approved=True)
    assert out["verification"] == "complete"                   # the human's word fans it


# ---------------------------------------------------------------- 0031 §6 — the visible mind


def _bijection_holds(g):
    """0008 §3's discipline, applied to the composed graph: the narrative names
    every node and every edge — sentences and picture never disagree."""
    ids = sorted(n["id"] for n in g["nodes"])
    named_n = sorted({n for s in g["narrative"] for n in s.get("nodes", [])})
    edges = sorted(f"{e['from']}→{e['to']}" for e in g["edges"])
    named_e = sorted({e for s in g["narrative"] for e in s.get("edges", [])})
    return ids == named_n and edges == named_e


def test_choreography_is_the_plan_made_visible():
    plan = {"objective": "check on the fleet",
            "intentions": [{"seat": "u:demo/e:cloud", "intent": "look at cloud",
                            "budget": {"tokens": 300}},
                           {"seat": "u:demo/e:retail", "intent": "look at retail",
                            "budget": {"tokens": 300}, "beyond_token": True}]}
    g = fingertip.choreography(plan)
    assert g["kind"] == "graph" and _bijection_holds(g)
    roles = [n["role"] for n in g["nodes"]]
    assert roles == ["orchestrator", "fingertip", "fingertip", "review", "human"]
    assert g["nodes"][2]["beyond_token"] is True
    assert "status" not in g["nodes"][1]          # unlit before anything runs
    assert "ask leave" in g["narrative"][2]["text"]


def test_choreography_lights_what_ran_and_keeps_every_branch():
    """One world, one picture (rule 7): branch state lights the seats, and a
    mid-flow leg (the iac after the human's answer) still shows."""
    plan = {"objective": "check on the fleet",
            "intentions": [{"seat": "u:demo/e:cloud", "intent": "look",
                            "budget": {"tokens": 300}}]}
    branches = [{"seat": "u:demo/e:cloud", "status": "done", "cycles": 1,
                 "severity": "low", "marker": "m1", "outcome": "o1",
                 "answer": "all well"},
                {"seat": "u:demo", "status": "done", "cycles": 1,
                 "severity": "medium", "marker": "m2", "outcome": "o2",
                 "answer": "provisioned"}]
    g = fingertip.choreography(plan, branches, question_answer="all floors")
    assert _bijection_holds(g)
    fingers = [n for n in g["nodes"] if n["role"] == "fingertip"]
    assert len(fingers) == 2                      # the mid-flow leg is not dropped
    assert fingers[0]["status"] == "done" and fingers[0]["severity"] == "low"
    assert fingers[0]["marker"] == "m1" and fingers[0]["outcome"] == "o1"
    assert fingers[1]["intent"] == "dispatched mid-flow, on the human's answer"
    assert "graded low by the dispatching seat" in g["narrative"][1]["text"]
    assert "You answered: “all floors”." in g["narrative"][-1]["text"]


# ---------------------------------------------------------------- 0033 sp3 — the coordinate, soft


def test_the_coordinate_rides_every_record_of_the_work(world):
    """0033 §4: outcomes, review markers, and the assembly all wear of:/via: tags —
    'every record that served objective O' becomes an index lookup, not a walk."""
    spec = fingertip.workflow_template(
        "u:demo", name="coord-run",
        intentions=[{"id": "look", "intent": "survey the floor",
                     "seat": "u:demo/e:cloud/f:prod"}])
    orch = fingertip.Orchestration(world.universe, world.becky, spec,
                                   "know the state of things", budget_tokens=1200)
    seats = {n.scope: n for n in (world.field_prod, world.eco_cloud)}
    out = orch.run(seats, world.beckys, _tidy_think, plan_approved=True)
    goal = out["goal_hash"]
    # the seat's outcome carries both axes
    outcome = next(r for r in world.field_prod.records.values()
                   if "intention-outcome" in r.get("tags", []))
    of_tags = [t for t in outcome["tags"] if t.startswith("of:")]
    via_tags = [t for t in outcome["tags"] if t.startswith("via:")]
    assert of_tags == [f"of:{goal}"] and len(via_tags) == 1
    # the review marker at home carries the same coordinate
    mark = next(r for r in world.universe.records.values()
                if "marker" in r.get("tags", []))
    assert f"of:{goal}" in mark["tags"] and via_tags[0] in mark["tags"]
    # the assembly carries the objective axis
    assembly = next(r for r in world.universe.records.values()
                    if "objective-outcome" in r.get("tags", []))
    assert f"of:{goal}" in assembly["tags"]
    # THE LOOKUP: the whole family by objective — a tag match, not a recursion
    family_home = fingertip.by_coordinate(world.universe, objective=goal)
    family_seat = fingertip.by_coordinate(world.field_prod, objective=goal)
    assert len(family_home) >= 2 and len(family_seat) >= 1
    # ...and by single intention
    iid = via_tags[0].split("via:", 1)[1]
    assert fingertip.by_coordinate(world.field_prod, intention=iid)


def test_parked_failure_and_its_knowledge_inherit_the_coordinate(world):
    """0033 §4 through 0014: a breaker's parked intent carries the coordinate, and
    the knowledge the librarian gathers for it INHERITS the same tags — the
    knowledge loop joins the ladder."""
    from orreth_sim import librarian
    from orreth_sim.agent_surface import join_workforce
    from orreth_sim.chassis import Chassis
    f = world.field_prod
    b_prod = world.beckys["u:demo/e:cloud/f:prod"]
    surf = join_workforce(f, b_prod)
    coord = fingertip.coordinate_tags("sha256:" + "a" * 64, "sha256:" + "b" * 64)
    res = Chassis(surf, lambda k, p: "RETRY: missing data", max_cycles=1,
                  coordinate=coord).run("an unsolvable ask")
    assert res["status"] == "parked"
    parked = f.records[res["record"]]
    assert set(coord) <= set(parked["tags"])
    # the librarian tends the lot; the commissioned knowledge wears the same axes
    librarian.tend(f, lambda intent: [
        {"claim": "the missing fact", "source_did": "did:web:src.example"}])
    entry = next(r for r in f.records.values()
                 if "knowledge" in r.get("tags", [])
                 and set(coord) <= set(r.get("tags", [])))
    assert entry is not None
    handled = next(r for r in f.records.values()
                   if "librarian-handled" in r.get("tags", []))
    assert set(coord) <= set(handled["tags"])


# ---------------------------------------------------------------- 0047 sp4 · author_plan
def test_the_mind_proposes_and_the_law_disposes():
    """0047 sp4: a well-shaped mind plan is priced by the LAW (never the mind),
    entitlement marked honestly, and the plan carries the spec hash the walk
    will name — a template that survives check_workflow."""
    floors = ["u:demo/e:cloud/f:prod", "u:demo/e:retail"]
    plan = fingertip.author_plan(
        "u:demo", req_id="req-1", objective="summarize the week",
        proposals=[{"seat": "u:demo/e:cloud/f:prod",
                    "intent": "gather the prod floor's week"},
                   {"seat": "u:demo/e:retail",
                    "intent": "gather the retail week"}],
        floors=floors, budget=2400)
    assert len(plan["intentions"]) == 2 and plan["dark"] == []
    assert all(i["budget"]["tokens"] == 800 for i in plan["intentions"])
    assert plan["spec"].startswith("sha256:")          # the walk's name
    assert all(not i.get("beyond_token") for i in plan["intentions"])
    # beyond the token: honest marking, never a silent skip
    wide = fingertip.author_plan(
        "u:demo/e:cloud", req_id="req-2", objective="x",
        proposals=[{"seat": "u:demo/e:retail", "intent": "reach sideways"}],
        floors=["u:demo/e:retail"])
    assert wide["intentions"][0]["beyond_token"] is True


def test_a_bad_mind_plan_is_refused_at_save():
    """Empty, malformed, unknown-seat, duplicated-seat, and own-floor plans
    all refuse LOUDLY before anything stages — the fallback stands."""
    floors = ["u:demo/e:retail"]
    for bad in ([],                                            # empty
                [{"seat": "u:demo/e:retail"}],                 # no intent
                ["just a string"],                             # not a dict
                [{"seat": "u:demo/e:ghost", "intent": "x"}],   # unknown seat
                [{"seat": "u:demo/e:retail", "intent": "a"},
                 {"seat": "u:demo/e:retail", "intent": "b"}],  # duplicated
                [{"seat": "u:demo", "intent": "grade myself"}]):  # own floor
        with pytest.raises(fingertip.WorkflowError):
            fingertip.author_plan("u:demo", req_id="r", objective="o",
                                  proposals=bad, floors=floors)
