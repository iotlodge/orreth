# PROVENANCE: authored by Fable 5 (claude-fable-5), 2026-07-14 — 0033, the Physics of Memory
"""The harness proves the physics (0033 §6): entropy is a dial, not a decay.
Every metric computes from records that already exist; measures inform, lanes decide."""
import pytest

from orreth_sim import crypto, infotheory as it
from orreth_sim.knowledge import KnowledgeCategory
from orreth_sim.node import make_memory
from orreth_sim.world import build


@pytest.fixture()
def world():
    return build()


def _mem(node, body, tags=None):
    rec = make_memory(node.steward, node.steward_kp, node.scope, body,
                      kind="semantic", tags=tags or [])
    return node.write(rec), rec


def test_entropy_and_information_gain():
    """Shannon, plain: uniform is log2(n), certainty is zero, a look is worth bits."""
    assert it.entropy({"a": 0.5, "b": 0.5}) == pytest.approx(1.0)
    assert it.entropy({"a": 1.0}) == pytest.approx(0.0)
    assert it.entropy({}) == 0.0
    assert it.entropy({"a": 2, "b": 2}) == pytest.approx(1.0)   # tolerant of counts
    prior = {"Michael": 0.52, "David": 0.31, "Unknown": 0.17}   # the doc's own example
    posterior = {"Michael": 0.95, "David": 0.04, "Unknown": 0.01}
    assert it.information_gain(prior, posterior) > 1.0          # the second look was worth it


def test_reconstruction_entropy_is_bounded_by_contract(world):
    """The headline: live chain = zero bits; a tombstoned source costs exactly its
    declared stub bound; nothing silently disappears."""
    f = world.field_prod
    a, _ = _mem(f, {"obs": "raw morning reading"})
    b, _ = _mem(f, {"obs": "raw evening reading"})
    dist = f._distill([a, b], push=False)
    r0 = it.reconstruction_entropy(f, dist["id"])
    assert r0 == {"bits": 0.0, "links": 2, "live": 2, "stubs": 0, "missing": 0}
    # the schedule fires: one raw drops to a stub — uncertainty appears, BOUNDED
    f.tombstone(a, by=f.steward["did"], reason="retention schedule")
    r1 = it.reconstruction_entropy(f, dist["id"])
    assert r1["stubs"] == 1 and r1["live"] == 1
    assert r1["bits"] == pytest.approx(it.STUB_BITS)
    # honest ignorance is louder than bounded loss
    assert it.MISSING_BITS > it.STUB_BITS


def test_mortal_world_staircases_while_orreth_stays_flat(world):
    """The demo's foil: a provenance-less world loses a full link past every
    horizon; Orreth's answer never exceeds stubs × their declared bound."""
    ages = [10.0, 40.0, 100.0, 200.0, 400.0]
    assert it.mortal_reconstruction_entropy(ages, retention_days=90) == \
        pytest.approx(3 * it.MISSING_BITS)
    assert it.mortal_reconstruction_entropy(ages, retention_days=500) == 0.0
    f = world.field_prod
    ids = [_mem(f, {"obs": f"day {i}"})[0] for i in range(5)]
    dist = f._distill(ids, push=False)
    for rid in ids[:3]:                        # the same three "expire" — as stubs
        f.tombstone(rid, by=f.steward["did"], reason="retention schedule")
    orreth = it.reconstruction_entropy(f, dist["id"])["bits"]
    mortal = it.mortal_reconstruction_entropy(ages, retention_days=90)
    assert orreth == pytest.approx(3 * it.STUB_BITS)
    assert orreth < mortal                     # bounded by contract beats gone-is-gone


def test_missing_reference_is_loud(world):
    """A reference to silence is the one state the architecture exists to prevent —
    the metric caps it and names it."""
    f = world.field_prod
    a, _ = _mem(f, {"obs": "anchored"})
    rec = make_memory(f.steward, f.steward_kp, f.scope, {"conclusion": "derived"},
                      kind="semantic")
    nowhere = "sha256:" + "0" * 64
    rec["derived_from"] = [a, nowhere]                  # one live link, one to nowhere
    rid = f.write(rec)
    r = it.reconstruction_entropy(f, rid)
    assert r["missing"] == 1 and r["bits"] == pytest.approx(it.MISSING_BITS)
    pc = it.provenance_completeness(f)
    assert pc["missing"] == [nowhere]
    assert pc["completeness"] < 1.0


def test_stub_counts_as_complete_provenance(world):
    """0026's law carried into the metric: THAT it existed stays on the record —
    a tombstone stub is an honest answer, only silence counts against."""
    f = world.field_prod
    a, _ = _mem(f, {"obs": "to be purged"})
    dist = f._distill([a], push=False)
    f.tombstone(a, by=f.steward["did"], reason="consent withdrawal")
    pc = it.provenance_completeness(f)
    assert pc["completeness"] == 1.0 and pc["missing"] == []
    assert it.resolution_fidelity(f, dist["id"]) == 0.0   # ...but bytes are honestly gone


def test_distillation_ratio_measures_the_pyramid(world):
    f = world.field_prod
    ids = [_mem(f, {"obs": "a long verbose observation " * 8, "n": i})[0]
           for i in range(4)]
    f._distill(ids, push=False)
    dr = it.distillation_ratio(f)
    assert dr["links"] == 4 and dr["sized"] == 4
    assert dr["ratio"] > 1.0                   # the pyramid narrows as it rises


def test_context_efficiency_reads_the_runs(world):
    """0027's restraint as a number — and deterministic thought counted apart,
    never divided by zero."""
    f = world.field_prod
    for tokens, score in ((100, 1.0), (300, 0.5), (0, 1.0)):
        run = {
            "id": crypto.content_hash({"t": tokens, "s": score}),
            "agent": "did:key:zworker", "scope": f.scope,
            "goal_hash": crypto.content_hash({"goal": "g"}),
            "occurred_at": f._universe_now(), "outcome": "success",
            "scores": [{"objective": "objective-met", "score": score}],
            "cost": {"tokens": tokens, "model_calls": 1},
            "author": f.steward["did"],
        }
        run["sig"] = f.steward_kp.sign(f.steward["did"], {k: run[k] for k in
                     ("id", "agent", "scope", "goal_hash", "occurred_at")})
        f.record_run(run)
    ce = it.context_efficiency(f)
    assert ce["runs"] == 3 and ce["deterministic_runs"] == 1
    assert ce["metered_tokens"] == 400
    assert ce["value_per_kilotoken"] == pytest.approx(1000 * 1.5 / 400)


def test_corroboration_counts_voices_not_echoes(world):
    """0014 sharpened by 0033: one claim mirrored across many sites is one voice."""
    f = world.field_prod
    cat = KnowledgeCategory(f, "test", "voices-test")
    e1 = cat.admit("larch outlasts pine in standing water",
                   {"did": "did:web:forestry.example"})
    echo = cat.admit("larch outlasts pine in standing water (mirror)",
                     {"did": "did:web:forestry.example"})     # same voice again
    other = cat.admit("larch holds in wet ground",
                      {"did": "did:web:timber.example"})      # a different voice
    cat.corroborate(e1, receipt_ids=[echo, other])
    ci = it.corroboration_independence(f, "voices-test")
    claim = ci["claims"][0]
    assert claim["receipts"] == 2 and claim["independent_voices"] == 1
    assert claim["echo"] is True and ci["echoes_detected"] == 1
