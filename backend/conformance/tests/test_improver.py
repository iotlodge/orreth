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
