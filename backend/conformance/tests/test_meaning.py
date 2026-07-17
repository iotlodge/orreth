# PROVENANCE: authored by Fable 5 (claude-fable-5), 2026-07-17 — 0022 Phase 2, the meaning axis (Phase E)
"""The meaning axis (0022 §4): retrieval's second sense — hybrid fusion,
standing over relevance, the dead ranked dead — and the three stated waits it
ends: reactivation (0031 §5), cross-source contradiction (0032 §3), the
Mirror's meaning-aware assessor (0034 sp3). Local model, bytes never leave."""
import pytest

from orreth_sim import meaning, mirror
from orreth_sim.schemas import SchemaError, validate

needs_axis = pytest.mark.skipif(meaning.embedder() is None,
                                reason="the meaning axis is dark on this "
                                       "node — consumers degrade to identity")


def test_the_meaning_facet_is_contract_legal():
    """0022 §4's contract delta, JB's rule-9 approval 2026-07-17: the facet is
    OPTIONAL and additive — a query without it validates untouched, one with
    it validates whole, and a malformed one refuses at the schema."""
    q = {"requester": "did:key:z6MkTESTTESTTESTTESTTESTTESTTESTTESTTESTTESTTEST",
         "subject": "self", "space": "self",
         "time": {"from": "2026-01-01T00:00:00Z"},
         "intent": "recall", "budget": {"cost": 4}, "auth": "biscuit-sim"}
    validate(q, "retrieval.schema.json#/$defs/Query")          # an old client
    validate({**q, "meaning": {"text": "when do I take my pills", "k": 5}},
             "retrieval.schema.json#/$defs/Query")             # a new one
    validate({**q, "meaning": {"text": "just the text"}},
             "retrieval.schema.json#/$defs/Query")             # k optional
    with pytest.raises(SchemaError):
        validate({**q, "meaning": {"k": 5}},                   # text required
                 "retrieval.schema.json#/$defs/Query")
    with pytest.raises(SchemaError):
        validate({**q, "meaning": {"text": "x", "vector": [1]}},  # nothing extra
                 "retrieval.schema.json#/$defs/Query")


def _rows():
    return [
        {"id": "r-med", "text": "take the heart medication at 8am with food",
         "state": "trusted", "at": "2026-07-01T00:00:00Z"},
        {"id": "r-dose", "text": "the dosage schedule for the pills is morning",
         "state": "corroborated", "at": "2026-07-02T00:00:00Z"},
        {"id": "r-gate", "text": "the garden gate squeaks in the wind",
         "state": "trusted", "at": "2026-07-03T00:00:00Z"},
        {"id": "r-dead", "text": "the pills should be taken at midnight",
         "state": "recalled", "at": "2026-07-04T00:00:00Z"},
    ]


@needs_axis
def test_the_hybrid_ranks_by_meaning_and_the_dead_rank_dead():
    """0022 §4: a question finds what it MEANS, not what it spells — and
    `recalled` never surfaces unless the query asks for the dead, and then
    wears the label."""
    hits = meaning.meaning_search("when do I take my pills", _rows(), k=3)
    assert hits[0]["id"] in ("r-med", "r-dose")     # meaning, not spelling
    assert all(h["id"] != "r-dead" for h in hits)   # the dead rank dead
    assert all(h["id"] != "r-gate" for h in hits[:2])
    assert "standing(" in hits[0]["why"]            # every hit names why
    with_dead = meaning.meaning_search("when do I take my pills", _rows(),
                                       k=4, include_the_dead=True)
    dead = [h for h in with_dead if h.get("dead")]
    assert len(dead) == 1 and dead[0]["id"] == "r-dead"
    assert dead[0]["standing"] == 0.0               # visible, and labeled


@needs_axis
def test_standing_outranks_relevance_alone():
    """0022 §4: the industry reranks by relevance; Orreth reranks by
    STANDING — an investigating claim yields to a trusted one of equal
    meaning."""
    rows = [
        {"id": "a", "text": "the pharmacy closes at six in the evening",
         "state": "investigating", "at": "2026-07-02T00:00:00Z"},
        {"id": "b", "text": "the pharmacy shuts at 6pm",
         "state": "trusted", "at": "2026-07-01T00:00:00Z"},
    ]
    hits = meaning.meaning_search("what time does the pharmacy close", rows,
                                  k=2)
    assert hits[0]["id"] == "b"                     # standing decides
    assert meaning.standing_weight("recalled") == 0.0
    assert meaning.standing_weight("investigating") < \
        meaning.standing_weight("untrusted") < \
        meaning.standing_weight("trusted")


@needs_axis
def test_the_aperture_and_the_coordinate_pull():
    """Phase E's reason to be built LAST: the ranker consumes what the gate
    made hard — an aperture pin (0031) or coordinate kinship (0033) pulls a
    row past a slightly better stranger."""
    rows = [
        {"id": "r-med", "text": "take the heart medication at 8am with food",
         "state": "trusted", "tags": ["of:obj-1"]},
        {"id": "r-dose", "text": "the dosage schedule for the pills is morning",
         "state": "trusted", "tags": []},
    ]
    plain = meaning.meaning_search("when do I take my pills", rows, k=2)
    assert plain[0]["id"] == "r-dose"               # the stranger is closer
    pinned = meaning.meaning_search("when do I take my pills", rows, k=2,
                                    aperture_refs={"r-med"})
    assert pinned[0]["id"] == "r-med"               # the aperture pulls
    assert "aperture proximity" in pinned[0]["why"]
    kin = meaning.meaning_search("when do I take my pills", rows, k=2,
                                 coordinate={"of:obj-1"})
    assert kin[0]["id"] == "r-med"                  # the coordinate pulls
    assert "coordinate kinship" in kin[0]["why"]
    react = meaning.reactivate("when do I take my pills", rows, {"r-med"})
    assert react[0]["id"] == "r-med"                # 0031 §5, discharged


@needs_axis
def test_cross_source_contradiction_speaks_where_numbers_disagree():
    """0032 §3's deferral, discharged at meaning-v1: same subject by cosine,
    different sources, numbers that disagree — and only there; one voice
    cannot contradict itself, and no numbers means no verdict."""
    claims = [
        {"id": "c1", "source": "did:web:coindesk",
         "text": "the bitcoin price is 61000 dollars"},
        {"id": "c2", "source": "did:web:reuters",
         "text": "bitcoin trades at 118000 dollars today"},
        {"id": "c3", "source": "did:web:coindesk",
         "text": "bitcoin trades near 61000 dollars this week"},
        {"id": "c4", "source": "did:web:reuters",
         "text": "the garden gate squeaks in the wind"},
    ]
    pairs = meaning.contradiction_pairs(claims)
    ids = {(p["a"]["id"], p["b"]["id"]) for p in pairs}
    assert ("c1", "c2") in ids                      # the contradiction fires
    assert "values disagree" in pairs[0]["why"]
    assert not any("c4" in pair for pair in ids)    # different subject: silent
    assert ("c1", "c3") not in ids                  # same source: silent
    assert ("c2", "c3") in ids                      # 118000 vs 61000, cross-source
    assert meaning.contradiction_pairs([claims[0]]) == []


@needs_axis
def test_the_mirror_hears_meaning():
    """0034 sp3's stated wait, ended: three phrasings, one worry — the Mirror
    counts them as one ask with the meaning axis, and honestly cannot without
    it."""
    audiences = [
        {"ref": f"x{i}", "resident": "librarian", "asked": ask,
         "reply": "an answer"}
        for i, ask in enumerate(["where are my reading glasses",
                                 "I cannot find my spectacles",
                                 "where did my glasses go"])
    ]
    heard = mirror.assess(audiences, meaning=meaning)["librarian"]
    assert len(heard["repeats"]) == 1
    assert heard["repeats"][0][1] == 3              # one worry, counted whole
    deaf = mirror.assess(audiences)["librarian"]
    assert deaf["repeats"] == []                    # identity alone cannot hear it
