# PROVENANCE: Claude Fable 5 (claude-fable-5) — 0066 sp2, the Analyzer's suite · 2026-09-09
"""The deterministic read never wavers, the escalation fires only when it
should, the mind's contract is typed, and a stumbling mind parks honestly —
the deterministic path serving, on the record."""
import json

from orreth_sim import dispatcher, featurizer, provisioner, stacks, variants
from orreth_sim.tournament import ALL_RETRIEVERS

BUILT = variants.built(ALL_RETRIEVERS)      # the worker's own call-site truth


def _floor():
    prov = provisioner.provision(provisioner.second_brain_template(), "t")
    fld = prov.fields["desk"]
    b = prov.beckys["u:t/e:life/f:desk"]
    lib, kp = b.issue_identity("instance", "u:t/e:life/f:desk", resident=True)
    stacks.plant_eco_assets(fld, lib, kp)
    return fld, lib, kp


AMBIGUOUS = ("what image relates to walls and seasons versus rain, "
             "and which desk gave each report?")


def test_the_read_is_deterministic_and_whole():
    a = featurizer.featurize(AMBIGUOUS)
    b = featurizer.featurize(AMBIGUOUS)
    assert a == b, "same ask, same features, forever"
    for k in ("shapes", "type", "parts", "length", "domain", "freshness",
              "modality", "latency_pref", "confidence"):
        assert k in a, f"the read must emit {k}"


def test_freshness_reads_the_clock_honestly():
    assert featurizer.featurize(
        "what did we believe as of 2026-01-01 about walls?")["freshness"] == \
        "historical"
    assert featurizer.featurize(
        "what is the latest word on walls?")["freshness"] == "current"
    assert featurizer.featurize(
        "how are walls cured?")["freshness"] == "timeless"


def test_confidence_high_on_one_clear_shape_low_on_conflict():
    assert featurizer.featurize(
        "how are walls connected to seasons?")["confidence"] == "high"
    assert featurizer.featurize(AMBIGUOUS)["confidence"] == "low"


def test_the_gate_is_the_whole_of_hot_when_applicable():
    low = featurizer.featurize(AMBIGUOUS)
    assert featurizer.should_consult(low)
    fast = featurizer.featurize(AMBIGUOUS, {"latency": "fast"})
    assert not featurizer.should_consult(fast), \
        "an asker who demanded speed never waits on a thought"
    clear = featurizer.featurize("how are walls cured?")
    assert not featurizer.should_consult(clear), \
        "a confident read spends no thought — the hot path stays hot"


def test_a_confident_ask_never_calls_the_mind():
    fld, lib, kp = _floor()
    calls = []
    d = dispatcher.dispatch(fld, lib, kp,
                            "how are walls connected to seasons?",
                            built=BUILT,
                            consult=lambda p: calls.append(p) or "{}")
    assert not calls, "the mind was never consulted"
    assert d["flavor"] == "graph"


def test_the_mind_chooses_on_ambiguity_and_the_record_keeps_it():
    fld, lib, kp = _floor()
    mind = lambda p: json.dumps({"style": "multi-agent",
                                 "why": "many parts across sources — split "
                                        "it and answer each"})
    d = dispatcher.dispatch(fld, lib, kp, AMBIGUOUS, built=BUILT,
                            consult=mind)
    assert d["flavor"] == "multi-agent"
    assert "quick governed look" in d["why"] and "split" in d["why"]
    from orreth_sim import crypto
    body = json.loads(crypto._b64d(
        fld.records[d["record"]]["body"]).decode())["dispatch"]
    assert body["consulted"]["style"] == "multi-agent"
    assert body["features"]["confidence"] == "low"
    assert body["featurizer_version"] == featurizer.VERSION


def test_the_askers_word_outranks_the_mind():
    fld, lib, kp = _floor()
    calls = []
    d = dispatcher.dispatch(fld, lib, kp, AMBIGUOUS, force="hyde",
                            built=BUILT,
                            consult=lambda p: calls.append(p) or "{}")
    assert d["flavor"] == "hyde" and not calls, \
        "Auto stood aside — and so did the mind"


def test_one_typed_reask_then_an_honest_park():
    fld, lib, kp = _floor()
    replies = iter(["not json at all", '{"style": "quantum", "why": "nope"}'])
    d = dispatcher.dispatch(fld, lib, kp, AMBIGUOUS,
                            consult=lambda p: next(replies))
    assert d["flavor"] == "naive", "the deterministic read served"
    assert "deterministic read served" in d["why"], "the park is on the record"
    from orreth_sim import crypto
    body = json.loads(crypto._b64d(
        fld.records[d["record"]]["body"]).decode())["dispatch"]
    assert body["consulted"].get("parked"), "the stumble is never a secret"


def test_an_unreachable_mind_parks_without_drama():
    fld, lib, kp = _floor()
    d = dispatcher.dispatch(fld, lib, kp, AMBIGUOUS, consult=lambda p: None)
    assert d["flavor"] == "naive" and "unreachable" in d["why"]
