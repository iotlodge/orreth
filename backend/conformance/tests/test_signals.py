# PROVENANCE: Claude Fable 5 (claude-fable-5) — 0066 sp3, the signals' suite · 2026-09-09
"""Signals are data, the reward function is law, a verdict lands at every
rung — and a thumb is never a reward scalar."""
import json

from orreth_sim import (chassis, crypto, provisioner, signals, stacks, thumb,
                        vera)
from orreth_sim.node import make_memory


def _floor():
    prov = provisioner.provision(provisioner.second_brain_template(), "t")
    fld = prov.fields["desk"]
    b = prov.beckys["u:t/e:life/f:desk"]
    lib, kp = b.issue_identity("instance", "u:t/e:life/f:desk", resident=True)
    stacks.plant_eco_assets(fld, lib, kp)
    return fld, lib, kp


ANSWER = {"answer": '“rammed earth walls breathe with the seasons” '
                    '[sha256:abc123abc123abc1…]',
          "citations": [{"ref": "sha256:x", "doc": "rammed", "score": 0.62},
                        {"ref": "sha256:y", "doc": "lime", "score": 0.31}]}


def test_the_bench_is_deterministic_bounded_and_whole():
    a = signals.bench("how do walls breathe with seasons?", ANSWER)
    b = signals.bench("how do walls breathe with seasons?", ANSWER)
    assert a == b, "same answer, same bench, forever"
    for k in ("retrieval", "faithfulness", "answer", "coverage"):
        assert k in a and 0.0 <= a[k] <= 1.0, f"{k} is a bounded proxy"
    assert a["retrieval"] == 0.62 and a["coverage"] == 0.5


def test_the_vector_joins_exchange_verdict_and_thumb():
    fld, lib, kp = _floor()
    exch = make_memory(lib, kp, fld.scope,
                       {"ask": {"asked": "walls?", "reply": "they breathe",
                                "signals": {"retrieval": 0.6, "answer": 0.5,
                                            "faithfulness": 0.8,
                                            "coverage": 0.75,
                                            "latency_ms": 42,
                                            "cost_chars": 900}}},
                       kind="episodic", tags=["ask"])
    fld.write(exch)
    v = vera.make_verdict(lib, kp, fld.scope, of=exch["id"],
                          work_floor=fld.scope, judge_floor="u:t",
                          rubric=vera.DEFAULT_RUBRIC, rubric_declared=False,
                          score=0.7, why="faithful and complete",
                          cost={"tokens": 60})
    fld.write(v)
    verdict, _ = thumb.make_thumb(lib, kp, fld.scope, of=exch["id"], up=True)
    fld.write(verdict)
    vec = signals.vector_for(fld.records, exch["id"])
    assert vec["bench"]["retrieval"] == 0.6 and vec["latency_ms"] == 42
    assert vec["judge"] == [0.7] and vec["thumb"] == 1.0


def test_reward_is_governed_arithmetic_and_rescorable():
    vec = {"bench": {"retrieval": 1.0, "faithfulness": 0.0,
                     "answer": 0.0, "coverage": 0.0}}
    genesis = signals.reward(vec)
    tilted = signals.reward(vec, {"retrieval": 0.9, "faithfulness": 0.05,
                                  "answer": 0.03, "coverage": 0.02})
    assert tilted["score"] > genesis["score"], \
        "the same history re-scores under new weights — signals never left " \
        "the records"


def test_veras_tier_outranks_the_answer_proxy():
    vec = {"bench": {"retrieval": 0.5, "faithfulness": 0.5,
                     "answer": 0.1, "coverage": 0.5}, "judge": [0.9, 0.9]}
    r = signals.reward(vec)
    proxy_only = signals.reward({"bench": dict(vec["bench"])})
    assert r["score"] > proxy_only["score"], \
        "the richer tier replaces the approximation, on the record"


def test_L3_a_thumb_is_never_a_reward_scalar():
    base = {"bench": {"retrieval": 0.5, "faithfulness": 0.5,
                      "answer": 0.5, "coverage": 0.5}}
    up = signals.reward({**base, "thumb": 1.0})
    down = signals.reward({**base, "thumb": 0.0})
    assert up["score"] == down["score"], \
        "the sum never moves on a thumb — sycophancy refused by name"
    assert down.get("vetoed") and not up.get("vetoed"), \
        "a 👎 vetoes the sample; it never tilts it"


def test_the_weights_live_in_the_standard():
    from orreth_sim import dispatcher
    assert dispatcher.STANDARD_V1["weights"] == signals.WEIGHTS_GENESIS, \
        "one genesis truth — re-weighting reward is a gated standard change"


def test_the_chassis_signs_its_observations_scribe_authored():
    from orreth_sim.agent_surface import join_workforce
    from orreth_sim.world import build
    world = build()
    fld2 = world.field_prod
    surf = join_workforce(fld2, world.beckys[fld2.scope])
    ident = surf.identity

    def think(_klass, prompt):
        if "Plan the MINIMUM" in prompt:
            return "OBSERVE reason: the ask"
        if "Answer concisely" in prompt:
            return "considered"
        return "DONE: hello"
    chassis.Chassis(surf, think, max_cycles=1).run("say hello")
    obs = [r for r in fld2.records.values()
           if "observation-outcome" in (r.get("tags") or [])]
    assert obs, "the third rung's records finally exist"
    for r in obs:
        assert r["author"] == fld2.steward["did"] != ident["did"], \
            "scribe-authored — nothing grades its own yardstick"
        body = json.loads(crypto._b64d(r["body"]).decode())["observation"]
        assert body["agent"] == ident["did"] and body["question"]


def test_a_verdict_lands_at_every_rung():
    fld, lib, kp = _floor()
    rungs = {}
    for tag, name in (("objective-outcome", "objective"),
                      ("intention-outcome", "intention"),
                      ("observation-outcome", "observation")):
        rec = make_memory(lib, kp, fld.scope,
                          {"outcome": {"rung": name, "status": "done"}},
                          kind="episodic", tags=[tag])
        fld.write(rec)
        rungs[name] = rec["id"]
    assert all(t in vera.WORK_TAGS for t in
               ("objective-outcome", "intention-outcome",
                "observation-outcome")), "vera's universe holds all three"
    for name, rid in rungs.items():
        v = vera.make_verdict(lib, kp, fld.scope, of=rid,
                              work_floor=fld.scope, judge_floor="u:t",
                              rubric=vera.DEFAULT_RUBRIC,
                              rubric_declared=False, score=0.8,
                              why=f"the {name} rung, judged",
                              cost={"tokens": 60})
        fld.write(v)
        stood = [r for r in fld.records.values()
                 if (json.loads(crypto._b64d(r["body"]).decode() or "{}")
                     .get("assay") or {}).get("of") == rid]
        assert stood, f"a verdict stands at the {name} rung"
