# PROVENANCE: Fable 5 (claude-fable-5) — 0047 sp1, typed thoughts · 2026-08-07
"""Typed thoughts (0047 sp1) — the law under conformance.

Under test: a well-dressed word passes first ask; a badly dressed word earns
exactly ONE re-ask carrying the named error and lands typed; a word that
fails twice is voided/retried HONESTLY — counted, never guessed, never
silently lost; the ground falling away is its own named state; the truncated
verdict's salvaged number stays labeled (the 0041-era lesson kept); vera's
raw-speak bench meters EVERY ask including the re-ask, records how many asks
the word took, and halts loudly when the meter refuses mid-re-ask; and the
chassis critic never invents a DONE from a word that wore neither face."""
import pytest

from orreth_sim import typed, vera as vera_mod
from orreth_sim.agent_surface import _TIER_COST, join_workforce
from orreth_sim.chassis import Chassis
from orreth_sim.node import make_memory
from orreth_sim.world import build


@pytest.fixture()
def world():
    return build()


# ---- the parsers: strict, salvage labeled, none -----------------------------------------

def test_parse_verdict_strict_salvage_and_none():
    assert typed.parse_verdict('{"score": 0.85, "why": "held"}') == (0.85, "held")
    # found anywhere in the reply, clamped into [0, 1]
    assert typed.parse_verdict('word first {"score": 1.7, "why": "x"}')[0] == 1.0
    # the truncated verdict's number survives — LABELED, never guessed
    sc, why = typed.parse_verdict('{"score": 0.62, "why": "the sentence was')
    assert sc == 0.62 and "cut short" in why
    assert typed.parse_verdict("no verdict here at all") is None
    assert typed.parse_verdict("") is None


def test_parse_critic_two_faces_and_nothing_else():
    assert typed.parse_critic("DONE: the answer") == (True, "the answer")
    assert typed.parse_critic("  retry: more data\n") == (False, "more data")
    # multi-line answers keep everything after the colon
    done, word = typed.parse_critic("DONE: line one\nline two")
    assert done and "line two" in word
    # neither face — including the answerless DONE — is None, never a guess
    assert typed.parse_critic("I think it looks good!") is None
    assert typed.parse_critic("DONE") is None
    assert typed.parse_critic("DONE:   ") is None
    assert typed.parse_critic("") is None


# ---- the verdict lane: typed → re-ask → honest void -------------------------------------

def test_typed_verdict_first_ask_needs_no_feedback():
    calls = []
    got = typed.typed_verdict(lambda fb: calls.append(fb) or
                              '{"score": 0.9, "why": "clean"}')
    assert got == {"status": "typed", "score": 0.9, "why": "clean", "asks": 1}
    assert calls == [""]                       # no error was ever named


def test_typed_verdict_reask_carries_the_named_error_and_lands():
    calls = []

    def ask(feedback):
        calls.append(feedback)
        return ("I rate this highly!" if len(calls) == 1
                else '{"score": 0.7, "why": "second dressing"}')

    got = typed.typed_verdict(ask)
    assert got["status"] == "typed" and got["asks"] == 2
    assert got["score"] == 0.7
    # the re-ask NAMED the error — the model is told what was wrong, not
    # merely asked again
    assert "not a valid verdict" in calls[1] and "STRICT JSON" in calls[1]


def test_typed_verdict_voids_only_after_a_real_reask():
    calls = []
    got = typed.typed_verdict(lambda fb: calls.append(fb) or "still just prose")
    assert got == {"status": "void", "asks": 2}
    assert len(calls) == 2                     # the re-ask was really tried


def test_typed_verdict_dark_ground_is_its_own_state():
    assert typed.typed_verdict(lambda fb: None) == {"status": "dark", "asks": 0}


# ---- the critic lane: never a guessed DONE ----------------------------------------------

def test_typed_critic_reasks_then_breaks_to_honest_retry():
    done, word, asks = typed.typed_critic(lambda fb: "DONE: solved")
    assert (done, word, asks) == (True, "solved", 1)

    replies = iter(["looks good to me!", "DONE: solved on the second face"])
    done, word, asks = typed.typed_critic(lambda fb: next(replies))
    assert done and asks == 2 and "second face" in word

    done, word, asks = typed.typed_critic(lambda fb: "never a face")
    assert done is False and "never a guess" in word and asks == 2


# ---- vera's raw lane: metered re-asks, counted voids, loud halts ------------------------

# one metered ask, priced by the gateway's own law (never hardcoded)
CHARGE = vera_mod.EST_TOKENS * _TIER_COST["standard"]


def _outcome(world, node, *, of="sha256:goal"):
    seat, kp = world.beckys[node.scope].issue_identity("instance", node.scope)
    rec = make_memory({"did": seat["did"], "scope": node.scope}, kp, node.scope,
                      {"outcome": {"intention": "i1", "of": of,
                                   "status": "done", "answer": "satisfied",
                                   "cycles": 1}},
                      kind="semantic", tags=["intention-outcome"])
    return node.write(rec), seat["did"]


def _speak_bench(world, scope, replies):
    """A raw-lane bench: the judge's word arrives as TEXT, one reply per ask."""
    seat, kp = world.beckys[scope].issue_identity("instance", scope,
                                                  resident=True)
    replies = list(replies)
    return {"seat": seat, "kp": kp,
            "speak": lambda body, rubric, feedback: replies.pop(0)}


def test_speak_bench_reask_lands_typed_with_both_asks_metered(world):
    """A badly dressed first word earns the re-ask and lands — asks=2 on the
    signed record, BOTH asks charged under vera's meter."""
    _outcome(world, world.field_prod)
    benches = {world.eco_cloud.scope: _speak_bench(
        world, world.eco_cloud.scope,
        ["I rate this work very highly indeed.",
         '{"score": 0.8, "why": "typed on the re-ask"}'])}
    v = vera_mod.Vera(world.universe, world.becky)
    out = v.assay_beat(world.field_prod, benches, dial="assay")
    assert out["assayed"] == 1 and not out["voided"]
    a = vera_mod.verdicts(world.field_prod)[0]["assay"]
    assert a["asks"] == 2 and a["score"] == 0.8
    assert a["cost"]["tokens"] == 2 * CHARGE                # the re-ask is paid for
    assert out["cost"]["tokens"] == 2 * CHARGE
    assert v.surface.budget_left == 2400 - 2 * CHARGE


def test_speak_bench_voids_only_after_the_reask_and_counts_it(world):
    """A word that fails twice is VOIDED — counted with its asks, no verdict
    record written, the spend honest on the beat."""
    _outcome(world, world.field_prod)
    benches = {world.eco_cloud.scope: _speak_bench(
        world, world.eco_cloud.scope, ["prose", "still prose"])}
    v = vera_mod.Vera(world.universe, world.becky)
    out = v.assay_beat(world.field_prod, benches, dial="assay")
    assert out["assayed"] == 0
    assert out["voided"] == [{"of": out["voided"][0]["of"], "asks": 2,
                              "status": "void"}]
    assert not vera_mod.verdicts(world.field_prod)          # nothing scored
    assert out["cost"]["tokens"] == 2 * CHARGE               # but the spend is real


def test_the_meter_can_refuse_the_reask_and_the_beat_halts_loudly(world):
    """The re-ask is a REAL commission: when the budget covers one ask but
    not two, the beat halts honestly mid-word rather than seating a free
    thought (law 4, kept through the new lane)."""
    _outcome(world, world.field_prod)
    benches = {world.eco_cloud.scope: _speak_bench(
        world, world.eco_cloud.scope,
        ["prose", '{"score": 0.9, "why": "never reached"}'])}
    v = vera_mod.Vera(world.universe, world.becky,
                      budget_tokens=CHARGE)                  # one ask, no more
    out = v.assay_beat(world.field_prod, benches, dial="assay")
    assert "halted" in out and out["assayed"] == 0
    assert out["cost"]["tokens"] == CHARGE                   # the first ask was paid


def test_the_pretyped_bench_lane_is_unchanged(world):
    """The dict lane ("think") keeps its exact shape — one charge, asks=1 on
    the record: the 0043 benches age without breaking."""
    _outcome(world, world.field_prod)
    seat, kp = world.beckys[world.eco_cloud.scope].issue_identity(
        "instance", world.eco_cloud.scope, resident=True)
    benches = {world.eco_cloud.scope: {
        "seat": seat, "kp": kp,
        "think": lambda body, rubric: {"score": 0.9, "why": "pre-typed"}}}
    v = vera_mod.Vera(world.universe, world.becky)
    out = v.assay_beat(world.field_prod, benches, dial="assay")
    assert out["assayed"] == 1 and not out["voided"]
    a = vera_mod.verdicts(world.field_prod)[0]["assay"]
    assert a["asks"] == 1 and a["cost"]["tokens"] == CHARGE


# ---- the chassis critic: the loop never lies --------------------------------------------

def test_chassis_critic_reasks_once_then_retries_honestly(world):
    """A critic word that wears neither face earns ONE re-ask; failing that,
    the cycle is an honest RETRY — the chassis parks rather than guesses,
    and the re-ask prompt carries the contract."""
    f = world.field_prod
    surf = join_workforce(f, world.beckys[f.scope])
    seen = []

    def think(_klass, prompt):
        seen.append(prompt)
        if "Plan the MINIMUM" in prompt:
            return "OBSERVE reason: the ask"
        if "Answer concisely" in prompt:
            return "considered"
        return "the vibes are good"                 # neither face, ever
    res = Chassis(surf, think, max_cycles=1).run("an ask")
    assert res["status"] == "parked"                # never a guessed DONE
    reasks = [p for p in seen if "wore neither face" in p]
    assert len(reasks) == 1                         # exactly one re-ask


def test_chassis_critic_lands_on_the_reask(world):
    """The second dressing counts: a critic that finds its face on the
    re-ask completes the cycle as if it always had one."""
    f = world.field_prod
    surf = join_workforce(f, world.beckys[f.scope])
    state = {"critic_asks": 0}

    def think(_klass, prompt):
        if "Plan the MINIMUM" in prompt:
            return "OBSERVE reason: the ask"
        if "Answer concisely" in prompt:
            return "considered"
        state["critic_asks"] += 1
        return ("mumble" if state["critic_asks"] == 1
                else "DONE: found its face")
    res = Chassis(surf, think, max_cycles=1).run("an ask")
    assert res["status"] == "done" and res["answer"] == "found its face"
    assert state["critic_asks"] == 2
