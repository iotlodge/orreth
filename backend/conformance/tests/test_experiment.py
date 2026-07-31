# PROVENANCE: Fable 5 (claude-fable-5) — 0043 sp4, the experiment · 2026-07-30
"""The Experiment (0043 §7) — A/B where each arm is a machine, under conformance.

Under test: an arm is a NAMED machine whose fingerprint differs from its
sibling in exactly the asset under test; the split waits for a human and the
policy is declared; the split is deterministic and honors its shares; the
standings ride the log join (verdict → work → arm tag) with no side-table;
an experiment never concludes on thin evidence; the conclusion is a card and
the rollout is a word — the adoption names the variant AND the experiment
(the 0038 orphan law), the loser stays on the shelf; and the word may be no
at every door."""
import pytest

from orreth_sim import experiment as exp_mod
from orreth_sim import improver, vera as vera_mod
from orreth_sim.node import make_memory
from orreth_sim.world import build


@pytest.fixture()
def world():
    return build()


def _seat(world, scope):
    ident, kp = world.beckys[scope].issue_identity("instance", scope,
                                                   resident=True)
    return ident, kp


def _stand_two_variants(world):
    """The control (the standing head) and a challenger that does NOT become
    the head — it rides a variant tag until an adoption says otherwise."""
    node = world.field_prod
    seat, kp = _seat(world, node.scope)
    control = node.write(improver.make_asset(
        seat, kp, node.scope, name="routing-standard",
        profile={"default": "router", "version": "92"}))
    challenger = node.write(improver.make_asset(
        seat, kp, node.scope, name="routing-standard",
        profile={"default": "hybrid", "version": "93-candidate"},
        tag="asset-variant"))
    head = improver.active_asset(node, "routing-standard")
    assert head and head[0] == control          # the challenger never took the head
    return node, seat, kp, control, challenger


def _experiment(world, *, min_n=2, share=None):
    node, seat, kp, control, challenger = _stand_two_variants(world)
    e = exp_mod.Experiment(node, seat, kp, name="routing-ab",
                           asset="routing-standard",
                           variants={"a": control, "b": challenger},
                           share=share, min_n=min_n)
    return node, seat, kp, e, control, challenger


def _fly(world, node, e, units):
    """Units through the split: each outcome lands wearing its arm's tag —
    the join the standings will walk."""
    seat, kp = _seat(world, node.scope)
    for u in units:
        r = e.route(u)
        rec = make_memory({"did": seat["did"], "scope": node.scope}, kp,
                          node.scope,
                          {"outcome": {"intention": u, "of": "sha256:ab-goal",
                                       "status": "done",
                                       "answer": f"answer under {r['arm']}",
                                       "cycles": 1}},
                          kind="semantic",
                          tags=["intention-outcome", r["tag"]])
        node.write(rec)


def _judge_all(world, node, sample=12):
    seat, kp = _seat(world, world.eco_cloud.scope)
    benches = {world.eco_cloud.scope: {
        "seat": seat, "kp": kp,
        "think": lambda body, rubric: {
            "score": 0.9 if "under b" in (body.get("outcome") or {}).get("answer", "")
            else 0.4,
            "why": "the challenger's answers landed; the control's wandered"}}}
    v = vera_mod.Vera(world.universe, world.becky, budget_tokens=24000)
    return v.assay_beat(node, benches, dial="assay", sample=sample)


def test_an_arm_is_a_named_machine_and_only_the_asset_differs(world):
    """Law 1: the arm IS the fingerprint — the floor's machine with the
    variant as head, content-hashed; two arms differ in exactly the asset
    under test, provably."""
    node, seat, kp, e, control, challenger = _experiment(world)
    fa, fb = e.arms["a"]["fingerprint"], e.arms["b"]["fingerprint"]
    assert fa["assets"]["routing-standard"] == control
    assert fb["assets"]["routing-standard"] == challenger
    diff = {k for k in set(fa["assets"]) | set(fb["assets"])
            if fa["assets"].get(k) != fb["assets"].get(k)}
    assert diff == {"routing-standard"}          # exactly one moving part
    assert fa["plane"] == fb["plane"] and fa["worldlines"] == fb["worldlines"]
    from orreth_sim import crypto
    assert e.arms["a"]["machine"] == crypto.content_hash(fa)
    assert e.arms["a"]["machine"] != e.arms["b"]["machine"]
    assert node.records[e.arms["b"]["record"]]["derived_from"] == [challenger]
    assert node.records[e.record]["derived_from"] == \
        [e.arms["a"]["record"], e.arms["b"]["record"]]


def test_the_split_waits_for_a_human_and_the_policy_is_declared(world):
    """Law 2: a proposed experiment serves NOTHING — the standing Canon
    serves alone; the policy that opens is the policy that was declared."""
    node, seat, kp, e, *_ = _experiment(world)
    with pytest.raises(exp_mod.SplitRefused):
        e.route("who is asking?")
    with pytest.raises(exp_mod.IllegalMove):
        e.open(human_word=False)
    assert e.state == "proposed"
    decl = exp_mod.experiments_on(node)[-1]
    assert decl["policy"] == {"kind": "hash-split", "unit": "ask",
                              "share": {"a": 0.5, "b": 0.5}}
    e.open(human_word=True)
    assert e.route("who is asking?")["arm"] in ("a", "b")


def test_the_split_is_deterministic_and_honors_the_share(world):
    """Law 3: same unit, same arm, forever; and the declared shares are the
    shares the traffic actually sees."""
    node, seat, kp, e, *_ = _experiment(world)
    e.open(human_word=True)
    units = [f"question-{i}" for i in range(400)]
    first = [e.route(u)["arm"] for u in units]
    again = [e.route(u)["arm"] for u in units]
    assert first == again                        # no coin anyone must trust
    n_b = sum(1 for a in first if a == "b")
    assert 140 <= n_b <= 260                     # ~half, hash-shaped
    lop = exp_mod.assign({"share": {"a": 0.9, "b": 0.1}}, "x")
    assert lop in ("a", "b")
    skew = [exp_mod.assign({"share": {"a": 0.9, "b": 0.1}}, f"u{i}")
            for i in range(300)]
    assert sum(1 for a in skew if a == "a") > 230


def test_standings_ride_the_log_join(world):
    """Law 4: verdict → its work → the arm tag the work wears — per-arm
    quality as a projection over records that already exist."""
    node, seat, kp, e, *_ = _experiment(world)
    e.open(human_word=True)
    _fly(world, node, e, [f"q-{i}" for i in range(8)])
    out = _judge_all(world, node)
    assert out["assayed"] == 8
    stand = e.arm_standings()
    assert stand["a"]["n"] + stand["b"]["n"] == 8
    assert stand["a"]["n"] >= 1 and stand["b"]["n"] >= 1
    assert stand["a"]["mean"] == 0.4 and stand["b"]["mean"] == 0.9


def test_no_conclusion_on_thin_evidence(world):
    """Law 5: min_n per arm holds — a premature conclusion is refused and
    the experiment keeps running."""
    node, seat, kp, e, *_ = _experiment(world, min_n=5)
    e.open(human_word=True)
    _fly(world, node, e, [f"q-{i}" for i in range(4)])
    _judge_all(world, node)
    with pytest.raises(exp_mod.IllegalMove, match="thin evidence"):
        e.conclude()
    assert e.state == "running"


def test_the_conclusion_is_a_card_and_the_rollout_is_a_word(world):
    """Law 6: the card carries winner, standings, and every evidence ref —
    and NOTHING moves until the human's word; the adoption names the variant
    AND the experiment; the loser stays on the shelf."""
    node, seat, kp, e, control, challenger = _experiment(world, min_n=2)
    e.open(human_word=True)
    _fly(world, node, e, [f"q-{i}" for i in range(10)])
    _judge_all(world, node)
    before = set(node.records)
    card = e.conclude()
    assert set(node.records) == before           # a card, never an act
    assert card["winner"] == "b" and card["variant"] == challenger
    assert card["machine"] == e.arms["b"]["machine"]
    assert e.record in card["evidence"]
    assert improver.active_asset(node, "routing-standard")[0] == control
    with pytest.raises(exp_mod.IllegalMove):
        e.adopt(seat, kp, human_word=False)      # the gate holds the evidence
    rid = e.adopt(seat, kp, human_word=True)
    head = improver.active_asset(node, "routing-standard")
    assert head[0] == rid                        # the winner is the head now
    from orreth_sim import crypto
    import json as _json
    body = _json.loads(crypto._b64d(head[1]["body"]).decode())["asset"]
    assert body["adopted_from"] == challenger    # lineage: the variant…
    assert set(node.records[rid]["derived_from"]) == {challenger, e.record}
    assert challenger in node.records and control in node.records  # nothing deleted
    assert e.state == "adopted"


def test_the_word_may_be_no_at_every_door(world):
    """The human's no is honored at proposed, running, and concluded — and a
    terminal experiment refuses every further move."""
    node, seat, kp, e, *_ = _experiment(world, min_n=1)
    with pytest.raises(exp_mod.IllegalMove):
        e.decline(human_word=False)
    e.decline(human_word=True)
    assert e.state == "declined"
    with pytest.raises(exp_mod.IllegalMove):
        e.open(human_word=True)                  # terminal — history remains
    node2, seat2, kp2, e2, *_ = _experiment(world, min_n=1)
    e2.open(human_word=True)
    _fly(world, node2, e2, ["q-a", "q-b", "q-c"])
    _judge_all(world, node2)
    e2.conclude()
    e2.decline(human_word=True)                  # the evidence heard; the word is no
    assert e2.state == "declined"
    assert improver.active_asset(node2, "routing-standard")[1] is not None
