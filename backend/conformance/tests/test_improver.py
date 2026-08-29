# PROVENANCE: authored by Fable 5 (claude-fable-5), 2026-07-11 — 0028, the Improvement Engine
"""The Improvement Engine (0028): evidence → proposal → grade → lanes → adoption.
Nothing grades its own yardstick; siblings, never silent successors; the human's
lane holds until the human speaks."""
import pytest

from orreth_sim import improver
from orreth_sim.node import make_memory
from orreth_sim.world import build


@pytest.fixture()
def world():
    return build()


def _seed_asset(world, profile=None):
    me = {"did": world.universe.steward["did"], "scope": "u:demo"}
    rec = improver.make_asset(me, world.universe.steward_kp, "u:demo",
                              name="fingertip-default",
                              profile=profile or {"max_cycles": 2, "max_obs": 3})
    return world.universe.write(rec)


def _park_one(world):
    """A breaker firing is evidence — the receipts the improver reads."""
    rid = world.universe.write(make_memory(
        world.universe.steward, world.universe.steward_kp, "u:demo",
        {"parked_intent": "unsolved", "missing": "data", "handoff": "knowledge-acquisition"},
        kind="semantic", tags=["parked", "knowledge-intent"]))
    return rid


def test_change_kind_is_computed_never_declared():
    """JB lock: bounded parameters are a nudge; persona/prompt/shape — or a mixed
    change — is a rewrite, the human's lane."""
    old = {"max_cycles": 2, "persona": "terse"}
    assert improver.classify_change(old, {"max_cycles": 3, "persona": "terse"}) == "nudge"
    assert improver.classify_change(old, {"max_cycles": 2, "persona": "florid"}) == "rewrite"
    assert improver.classify_change(old, {"max_cycles": 3, "persona": "florid"}) == "rewrite"
    assert improver.LANES == {"nudge": "medium", "rewrite": "high"}


def test_healthy_assets_are_left_alone(world):
    _seed_asset(world)
    imp = improver.Improver(world.universe, world.becky)
    assert imp.beat("fingertip-default") is None        # no evidence, no proposal


def test_evidence_earns_a_proposal_with_receipts(world):
    aid = _seed_asset(world)
    parked = _park_one(world)
    imp = improver.Improver(world.universe, world.becky)
    pid = imp.beat("fingertip-default")
    assert pid is not None
    prop = world.universe.records[pid]
    assert "asset-proposal" in prop["tags"]
    assert aid in prop["derived_from"]                  # succeeds the version it cites
    assert parked in prop["derived_from"]               # ...and cites the evidence
    # one open proposal per asset — the lane holds, no storms
    assert imp.beat("fingertip-default") is None
    assert improver.open_proposal(world.universe, "fingertip-default") == pid


def test_nudge_grades_medium_and_adopts_loud(world):
    _seed_asset(world)
    _park_one(world)
    imp = improver.Improver(world.universe, world.becky)
    pid = imp.beat("fingertip-default")
    gov, gov_kp = world.becky.issue_identity("instance", "u:demo", resident=True)
    graded = improver.grade(world.universe, gov, gov_kp, pid)
    assert graded["kind"] == "nudge" and graded["severity"] == "medium"
    mk = world.universe.records[graded["marker"]]
    assert pid in mk["derived_from"]                    # the grade, on the record
    assert mk["author"] != world.universe.records[pid]["author"]  # never the proposer
    adopted = improver.adopt(world.universe, gov, gov_kp, pid, graded)
    assert adopted is not None
    assert adopted != pid          # adoption is new content — never an id collision
    assert "asset-proposal" in world.universe.records[pid]["tags"]  # ...and never an overwrite
    rec = world.universe.records[adopted]
    assert pid in rec["derived_from"] and graded["marker"] in rec["derived_from"]
    # the new version is now active; the old one still stands behind it
    assert improver.active_asset(world.universe, "fingertip-default")[0] == adopted
    assert improver.open_proposal(world.universe, "fingertip-default") is None


def test_rewrite_waits_for_the_human(world):
    _seed_asset(world)
    me = {"did": world.universe.steward["did"], "scope": "u:demo"}
    pid = world.universe.write(improver.make_asset(
        me, world.universe.steward_kp, "u:demo", name="fingertip-default",
        profile={"max_cycles": 2, "max_obs": 3, "persona": "a bolder voice"},
        tag="asset-proposal"))
    gov, gov_kp = world.becky.issue_identity("instance", "u:demo", resident=True)
    graded = improver.grade(world.universe, gov, gov_kp, pid)
    assert graded["kind"] == "rewrite" and graded["severity"] == "high"
    assert improver.adopt(world.universe, gov, gov_kp, pid, graded) is None
    # the human speaks — the lane opens
    adopted = improver.adopt(world.universe, gov, gov_kp, pid, graded,
                             human_approved=True)
    assert adopted is not None


# ---------------------------------------------------------------- 0031 §4 — the shelf


def test_prompts_leave_the_code(world):
    """0031 §4: the chassis constants become version one on the shelf; a template
    change is not a bounded parameter — the diff grades it a rewrite."""
    me = {"did": world.universe.steward["did"], "scope": "u:demo"}
    minted = improver.seed_prompts(world.universe, me, world.universe.steward_kp)
    assert set(minted) == {"prompt-plan", "prompt-critic"}
    assert improver.seed_prompts(world.universe, me, world.universe.steward_kp) == {}
    beh = improver.resolve_behavior(world.universe)
    assert "OBSERVE" in beh["plan_template"] and "DONE" in beh["critic_template"]
    assert set(beh["versions"]) == {"prompt-plan", "prompt-critic"}
    old = {"template": beh["plan_template"]}
    assert improver.classify_change(old, {"template": "be brief."}) == "rewrite"


def test_adoption_changes_the_next_run(world):
    """0031 §4: resolve_behavior serves the ACTIVE version — an adoption changes
    what the next chassis runs under, not just the record."""
    _seed_asset(world, {"max_cycles": 2, "max_obs": 3})
    _park_one(world)
    imp = improver.Improver(world.universe, world.becky)
    pid = imp.beat("fingertip-default")
    gov, gov_kp = world.becky.issue_identity("instance", "u:demo", resident=True)
    graded = improver.grade(world.universe, gov, gov_kp, pid)
    improver.adopt(world.universe, gov, gov_kp, pid, graded)
    assert improver.resolve_behavior(world.universe)["profile"]["max_cycles"] == 3


def test_chassis_templates_are_data():
    """0031 §4: the loop is the law; the prompts are the profile."""
    from orreth_sim.chassis import Chassis
    seen = {}

    def think(_klass, prompt):
        seen.setdefault("first", prompt)
        return "OBSERVE reason: x"

    c = Chassis(None, think,
                plan_template="CUSTOM {persona}|{intent}|{feedback}|{skills}|{max_obs}")
    c._plan("the goal", "", "low")
    assert seen["first"].startswith("CUSTOM") and "the goal" in seen["first"]


def test_decline_releases_the_lane(world):
    """0031 §4: a refusal never dams the river — the decline derives from the
    proposal, and the asset's lane opens for the next beat."""
    _seed_asset(world)
    _park_one(world)
    imp = improver.Improver(world.universe, world.becky)
    pid = imp.beat("fingertip-default")
    assert improver.open_proposal(world.universe, "fingertip-default") == pid
    me = {"did": world.universe.steward["did"], "scope": "u:demo"}
    did_ = improver.decline(world.universe, me, world.universe.steward_kp, pid)
    assert pid in world.universe.records[did_]["derived_from"]
    assert improver.open_proposal(world.universe, "fingertip-default") is None
    assert imp.beat("fingertip-default") is not None    # the river runs again


def test_feedback_is_evidence_the_smith_must_carry(world):
    """0031 §4 (v0 lock): feedback is evidence, never an auto-trigger — but the
    next proposal MUST cite it, verbatim on the record."""
    aid = _seed_asset(world)
    me = {"did": world.universe.steward["did"], "scope": "u:demo"}
    fid = improver.feedback(world.universe, me, world.universe.steward_kp,
                            "fingertip-default", "too many retries on cold floors")
    rec = world.universe.records[fid]
    assert "asset-feedback" in rec["tags"] and aid in rec["derived_from"]
    ev = improver.evidence(world.universe)
    assert ev["feedback"] == 1 and fid in ev["refs"]
    _park_one(world)                                    # health dips; the beat proposes
    imp = improver.Improver(world.universe, world.becky)
    pid = imp.beat("fingertip-default")
    assert fid in world.universe.records[pid]["derived_from"]


def test_shelf_and_version_walk(world):
    """0031 §4: the whole chain readable — evidence → proposal → grade →
    adoption, and the shelf knows who holds a lane."""
    _seed_asset(world)
    _park_one(world)
    imp = improver.Improver(world.universe, world.becky)
    pid = imp.beat("fingertip-default")
    gov, gov_kp = world.becky.issue_identity("instance", "u:demo", resident=True)
    graded = improver.grade(world.universe, gov, gov_kp, pid)
    improver.adopt(world.universe, gov, gov_kp, pid, graded)
    rows = improver.shelf(world.universe)
    row = next(r for r in rows if r["name"] == "fingertip-default")
    assert row["versions"] == 2 and row["open"] is None
    walk = improver.version_walk(world.universe, "fingertip-default")
    assert len(walk) == 2
    assert walk[0]["changed"] == ["max_cycles", "max_obs"]   # genesis vs nothing
    assert walk[1]["adopted_from"] == pid
    assert walk[1]["grade"]["severity"] == "medium"


def test_approval_package_reads_before_the_gate(world):
    """0031 §4: HITL reviews a checked candidate — computed diff, resolved
    receipts (the human's words verbatim), and the rollback that never left."""
    aid = _seed_asset(world)
    me = {"did": world.universe.steward["did"], "scope": "u:demo"}
    improver.feedback(world.universe, me, world.universe.steward_kp,
                      "fingertip-default", "give it one more cycle")
    _park_one(world)
    imp = improver.Improver(world.universe, world.becky)
    pid = imp.beat("fingertip-default")
    pkg = improver.approval_package(world.universe, pid)
    assert pkg["asset"] == "fingertip-default" and pkg["kind"] == "nudge"
    assert pkg["changed"]["max_cycles"] == {"from": 2, "to": 3}
    assert any("give it one more cycle" in r["what"] for r in pkg["receipts"])
    assert pkg["rollback"] == aid
    assert pkg["checks"] == {"no_op": False, "cites_active": True}


def test_the_humans_word_is_the_nudge_ceiling(world):
    """0063 sp3 (L3's law): the improver climbs toward the human's cycle cap
    and never over it — at the cap, the dial is at its stop and nothing
    proposes; the machine optimizes INSIDE the human's word."""
    _seed_asset(world)                       # max_cycles 2
    _park_one(world)                         # evidence that would earn a nudge
    imp = improver.Improver(world.universe, world.becky)
    assert imp.beat("fingertip-default", cycle_cap=2) is None
    pid = imp.beat("fingertip-default", cycle_cap=3)
    assert pid is not None
    prof = improver._profile_of(world.universe.records[pid])
    assert prof["max_cycles"] == 3           # climbed to the word, not past it
