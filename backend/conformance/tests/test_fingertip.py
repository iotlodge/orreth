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
    """0027 §3 · 0030: one intent, a budget slice, citation refs — never the plan,
    never the siblings, never the why."""
    s = fingertip.make_intention("sha256:goal", "test the widget", 300, ["sha256:ref1"])
    assert set(s) == {"of", "intent", "budget", "refs"}
    assert s["budget"] == {"tokens": 300}


def test_review_severity_rides_the_lanes():
    """0024 discharged: clean DONE → low; corrected DONE → medium; unfinished →
    high (the human's lane — unfinished work is where the risk lives)."""
    assert fingertip.review_severity("done", 1) == "low"
    assert fingertip.review_severity("done", 2) == "medium"
    assert fingertip.review_severity("parked", 2) == "high"


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
