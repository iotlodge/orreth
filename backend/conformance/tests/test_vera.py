# PROVENANCE: Fable 5 (claude-fable-5) — 0043 sp2, vera & the assay loop · 2026-07-30
"""vera, the astronomer (0043 sp2) — the assay loop, under conformance.

Under test: the examiner rests below the assay dial (and refuses a dial that
does not exist); the verdict is signed by another floor's mind and never the
executor; a universe with no outside bench refuses rather than lets a floor
grade its own homework; her own cost is her first exhibit (metered under her
DID, pinned so a squeezed budget halts loudly instead of seating a cheaper
judge); human gradings enter the same shelf by the same shape; detection
wears no levers — a degrading standing becomes a card, never an act; and
there is no hall of mirrors — verdicts are never themselves assayed and
judged work is never re-drummed."""
import pytest

from orreth_sim import vera as vera_mod
from orreth_sim.node import make_memory
from orreth_sim.world import build


@pytest.fixture()
def world():
    return build()


def _outcome(world, node, *, of="sha256:goal", status="done",
             answer="the sliver, satisfied"):
    """A completed intention on the floor's shelf — the work vera samples."""
    seat, kp = world.beckys[node.scope].issue_identity("instance", node.scope)
    rec = make_memory({"did": seat["did"], "scope": node.scope}, kp, node.scope,
                      {"outcome": {"intention": "i1", "of": of,
                                   "status": status, "answer": answer,
                                   "cycles": 1}},
                      kind="semantic", tags=["intention-outcome"])
    return node.write(rec), seat["did"]


def _bench(world, scope, *, score=0.9):
    seat, kp = world.beckys[scope].issue_identity("instance", scope,
                                                  resident=True)
    return {"seat": seat, "kp": kp,
            "think": lambda body, rubric, s=score: {
                "score": s, "why": f"held against: {rubric[:48]}"}}


def test_the_examiner_rests_below_assay(world):
    """§5: glance and watch are free depths and say so — no sample, no judge,
    no spend; a dial position that does not exist is refused."""
    v = vera_mod.Vera(world.universe, world.becky)
    _outcome(world, world.field_prod)
    benches = {world.eco_cloud.scope: _bench(world, world.eco_cloud.scope)}
    for dial in ("glance", "watch"):
        out = v.assay_beat(world.field_prod, benches, dial=dial)
        assert out["assayed"] == 0 and "rests" in out["note"]
    assert not vera_mod.verdicts(world.field_prod)
    assert v.surface.budget_left == 2400                 # not a token moved
    with pytest.raises(ValueError):
        v.assay_beat(world.field_prod, benches, dial="stare")


def test_a_judge_from_another_floors_mind_signs_the_verdict(world):
    """Law 2, structural: the bench on the work's own floor is never picked;
    the verdict lands under the JUDGE'S authorship (author ≠ executor), the
    declared rubric rides when the objective declared one, and the default
    rubric is labeled default when it did not."""
    rid, executor = _outcome(world, world.field_prod, of="sha256:goal-a")
    benches = {
        world.field_prod.scope: _bench(world, world.field_prod.scope),
        world.eco_cloud.scope: _bench(world, world.eco_cloud.scope),
    }
    v = vera_mod.Vera(world.universe, world.becky)
    out = v.assay_beat(world.field_prod, benches, dial="assay",
                       rubrics={"sha256:goal-a": "cites at least three records"})
    assert out["assayed"] == 1
    [vid] = out["verdicts"]
    rec = world.field_prod.records[vid]
    a = vera_mod.verdicts(world.field_prod)[0]["assay"]
    assert rec["author"] == benches[world.eco_cloud.scope]["seat"]["did"]
    assert rec["author"] != executor                     # author ≠ executor (0005)
    assert a["judge_floor"] == world.eco_cloud.scope
    assert a["judge_floor"] != a["work_floor"]
    assert a["rubric"] == "cites at least three records" and a["rubric_declared"]
    assert rec["derived_from"] == [rid]
    # a second objective with NO declared rubric wears the default, labeled
    _outcome(world, world.field_prod, of="sha256:goal-b")
    out2 = v.assay_beat(world.field_prod, benches, dial="assay")
    a2 = [x["assay"] for x in vera_mod.verdicts(world.field_prod)
          if x["id"] in out2["verdicts"]][0]
    assert a2["rubric"] == vera_mod.DEFAULT_RUBRIC and not a2["rubric_declared"]


def test_no_outside_bench_means_refusal_not_self_grading(world):
    """Law 2's hard edge: when the universe holds no bench beyond the work's
    floor, the assay refuses honestly — a floor never grades its own
    homework, even at the price of no grade at all."""
    rid, _ = _outcome(world, world.field_prod)
    benches = {world.field_prod.scope: _bench(world, world.field_prod.scope)}
    v = vera_mod.Vera(world.universe, world.becky)
    out = v.assay_beat(world.field_prod, benches, dial="assay")
    assert out["assayed"] == 0 and not out["verdicts"]
    assert out["refused"][0]["of"] == rid
    assert "never self-grades" in out["refused"][0]["why"]


def test_her_own_cost_is_her_first_exhibit(world):
    """Law 4: the commission is metered under HER did before the judge
    thinks; the verdict carries the charge; the exhibit prices her curiosity
    to the token the meter showed."""
    _outcome(world, world.field_prod)
    benches = {world.eco_cloud.scope: _bench(world, world.eco_cloud.scope)}
    v = vera_mod.Vera(world.universe, world.becky)
    out = v.assay_beat(world.field_prod, benches, dial="assay")
    charged = out["cost"]["tokens"]
    assert charged > 0 and v.surface.budget_left == 2400 - charged
    assert world.universe.model_gateway.call_log[-1]["caller"] == v.did
    a = vera_mod.verdicts(world.field_prod)[0]["assay"]
    assert a["cost"]["tokens"] == charged
    ex = v.exhibit(world.field_prod)
    assert ex == {"assays": 1, "tokens": charged, "human_gradings": 0,
                  "budget_left": 2400 - charged}


def test_the_meter_halts_the_beat_loudly(world):
    """Law 4's edge, pinned (0016): a squeezed budget stops the examiner and
    says so — it never seats a silently cheaper judge to keep going."""
    _outcome(world, world.field_prod, of="sha256:g1")
    _outcome(world, world.field_prod, of="sha256:g2")
    benches = {world.eco_cloud.scope: _bench(world, world.eco_cloud.scope)}
    v = vera_mod.Vera(world.universe, world.becky, budget_tokens=500)
    out = v.assay_beat(world.field_prod, benches, dial="assay")
    assert out["assayed"] == 1                           # the first was affordable
    assert "the meter said no" in out["halted"]
    assert len(vera_mod.verdicts(world.field_prod)) == 1


def test_human_gradings_enter_the_same_shelf(world):
    """§6: the human's verdict is a card, a score, a signature — the same
    shape on the same shelf; the standings hear it beside the judges', and
    the exhibit prices it at zero, honestly apart."""
    rid, _ = _outcome(world, world.field_prod)
    human, kp = world.becky.issue_identity("instance", "u:demo")
    g = vera_mod.make_human_grading(human, kp, world.field_prod.scope,
                                    of=rid, score=0.8,
                                    word="good work — cite one more source")
    world.field_prod.write(g)
    stand = vera_mod.standings(world.field_prod)
    s = stand[world.field_prod.scope]
    assert s["n"] == 1 and s["humans"] == 1 and s["mean"] == 0.8
    v = vera_mod.Vera(world.universe, world.becky)
    assert v.exhibit(world.field_prod)["human_gradings"] == 1
    assert v.exhibit(world.field_prod)["tokens"] == 0


def test_detection_wears_no_levers(world):
    """Law 3: a low mean and a falling trend each become a CARD — yardstick
    named, evidence cited, standing attached — and NOTHING on the shelf
    moves: the record count after judging is the verdicts and nothing else."""
    benches = {world.eco_cloud.scope: _bench(world, world.eco_cloud.scope,
                                             score=0.3)}
    v = vera_mod.Vera(world.universe, world.becky)
    for i in range(2):
        _outcome(world, world.field_prod, of=f"sha256:low-{i}")
    before = set(world.field_prod.records)
    out = v.assay_beat(world.field_prod, benches, dial="assay", sample=2)
    [card] = out["findings"]
    assert card["kind"] == "assay-degradation"
    assert "sits under the 0.55 floor" in card["why"]
    assert sorted(card["evidence"]) == sorted(out["verdicts"])
    grew = set(world.field_prod.records) - before
    assert grew == set(out["verdicts"])                  # cards, never acts
    # the trend branch: healthy mean, falling halves — still a card
    trend_stand = {"u:x/e:y/f:z": {"n": 4, "mean": 0.75, "trend": -0.3,
                                   "humans": 0, "refs": ["a", "b", "c", "d"]}}
    [tcard] = vera_mod.degradations(trend_stand)
    assert "trend fell 0.3" in tcard["why"]


def test_no_hall_of_mirrors_and_no_redrumming(world):
    """The Mirror's law, kept: verdicts are never themselves sampled; work
    already under verdict is never re-assayed; and the parlor's conversations
    are not vera's to grade — she assays WORK."""
    _outcome(world, world.field_prod)
    seat, kp = world.beckys[world.field_prod.scope].issue_identity(
        "instance", world.field_prod.scope)
    chat = make_memory({"did": seat["did"], "scope": world.field_prod.scope},
                       kp, world.field_prod.scope,
                       {"audience": {"asked": "hi", "reply": "hello"}},
                       kind="episodic", tags=["parlor"])
    world.field_prod.write(chat)
    benches = {world.eco_cloud.scope: _bench(world, world.eco_cloud.scope)}
    v = vera_mod.Vera(world.universe, world.becky)
    first = v.assay_beat(world.field_prod, benches, dial="assay")
    assert first["assayed"] == 1                         # the outcome, not the chat
    second = v.assay_beat(world.field_prod, benches, dial="assay")
    assert second["assayed"] == 0 and not second["refused"]
    assert len(vera_mod.verdicts(world.field_prod)) == 1
