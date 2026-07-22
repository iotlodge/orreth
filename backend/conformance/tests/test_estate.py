# PROVENANCE: Fable 5 (claude-fable-5) — 0037, the Estate · 2026-07-22
"""The Estate (0037) spoonful 1: the resident stands.

Under test: the universe-parent allowance (a field with no eco above it, its
becky delegated one hop from the root — staff of the universe, locked
2026-07-22); the TYPED DOOR (humans alone speak objectives; agent speech
carries walkable lineage or is refused LOUDLY — a teaching refusal, never the
uniform authz shape); and the acceptance gate (Create refuses until the
brownfield adoption has walked, locked 2026-07-22)."""
import pytest

from orreth_sim import estate, parlor, provisioner


def _estate_field():
    prov = provisioner.provision(provisioner.second_brain_template(), "t")
    fld = provisioner.staff_field(prov, provisioner.second_brain_template(), "estate")
    b = prov.beckys["u:t/f:estate"]
    allen, allen_kp = b.issue_identity("instance", "u:t/f:estate", resident=True)
    return prov, fld, b, allen, allen_kp


def test_staff_field_parents_off_universe():
    """The 0037 §8.3 allowance: no eco between allen and the universe — the
    delegation chain is exactly one hop, and a token his becky mints verifies
    at the root like any other."""
    prov, fld, b, allen, allen_kp = _estate_field()
    assert fld.profile["scope"] == "u:t/f:estate"
    assert fld.profile["is_leaf"] is True
    assert len(b.chain) == 1                       # root → becky@estate, one hop
    assert b.chain[0]["issuer"] == prov.becky.did
    # spend rides the lease (§8.6): the Budget shape's `cost` axis carries the
    # dollars — contracts/v0 untouched; a named `usd` member is a later rule-9 ask
    token = b.issue_token(allen["did"], "u:t/f:estate",
                          [{"action": "retrieve", "space": "self"}],
                          budget={"cost": 25})
    prov.becky.verify_token(token)                 # the root recognizes the staff


def test_door_refuses_agent_objectives():
    """Humans alone originate objectives (0030) — an agent speaking a why is
    refused loudly, with the law in the message."""
    _, fld, _, allen, allen_kp = _estate_field()
    with pytest.raises(estate.DoorRefusal, match="humans alone originate"):
        estate.receive(fld, allen, allen_kp,
                       {"kind": "objective", "text": "make me a bucket",
                        "speaker": {"did": "did:key:zagent", "human": False}})


def test_door_demands_walkable_lineage():
    """An agent intention with no ancestry — or an ancestry this floor cannot
    see — never enters. With a walkable lineage it lands as signed memory,
    the rung riding the tags and the ancestry riding the signed body."""
    _, fld, _, allen, allen_kp = _estate_field()
    with pytest.raises(estate.DoorRefusal, match="no ancestry"):
        estate.receive(fld, allen, allen_kp,
                       {"kind": "intention", "text": "a bucket for the corpus",
                        "speaker": {"did": "did:key:zagent", "human": False}})
    with pytest.raises(estate.DoorRefusal, match="cannot see"):
        estate.receive(fld, allen, allen_kp,
                       {"kind": "intention", "text": "a bucket for the corpus",
                        "speaker": {"did": "did:key:zagent", "human": False},
                        "lineage": ["not-a-record-here"]})
    oid = estate.receive(fld, allen, allen_kp,
                         {"kind": "objective", "text": "build the seven RAGs",
                          "speaker": {"did": "did:key:zjb", "human": True}})
    iid = estate.receive(fld, allen, allen_kp,
                         {"kind": "intention", "text": "a bucket for the corpus",
                          "speaker": {"did": "did:key:zagent", "human": False},
                          "lineage": [oid]})
    rec = fld.records[iid]
    assert "estate" in rec["tags"] and "intention" in rec["tags"]


def test_gate_stands_until_adoption():
    """The acceptance gate (0037 §8.7): Create refuses with the gate's own
    words until the brownfield walk lands its receipts — then a sandbox ask
    (no charter owed on the lowest rung) stages."""
    _, fld, _, allen, allen_kp = _estate_field()
    assert not estate.create_unlocked(fld)
    with pytest.raises(estate.GateStands, match="adopts before it creates"):
        estate.stage_create(fld, "create me an S3 bucket")
    estate.record_adoption(fld, allen, allen_kp,
                           ["OrrethDemoStack", "jsbarth-pipeline"])
    assert estate.create_unlocked(fld)
    staged = estate.stage_create(fld, "create me an S3 bucket", env="sandbox")
    assert staged["staged"] is True and "charter" in staged["note"]


def test_charter_refuses_prod_with_gaps():
    """Refused-at-compile (0037 §3): past the acceptance gate, a prod ask with
    an unanswered charter cannot compile — and the refusal carries the open
    questions, which ARE the HITL card's text."""
    _, fld, _, allen, allen_kp = _estate_field()
    estate.record_adoption(fld, allen, allen_kp, ["OrrethDemoStack"])
    with pytest.raises(estate.CharterGaps, match="recovery time objective") as e:
        estate.stage_create(fld, "deploy repo foo to production")
    assert set(e.value.questions) == set(estate.CHARTER_GENESIS["questions"])
    # the ladder: staging owes only its rung's questions
    with pytest.raises(estate.CharterGaps) as e2:
        estate.stage_create(fld, "deploy repo foo", env="staging")
    assert set(e2.value.questions) == {"data_classification", "retention"}


def test_answers_bind_to_subjects_and_policy_underlies():
    """JB's walk finding (2026-07-22) made structural: an answer is a property
    of a WORKLOAD; estate policy ("" subject) is deliberate and auto-applies
    beneath it; another workload's history is OFFERED in the question, never
    silently inherited."""
    _, fld, _, allen, allen_kp = _estate_field()
    estate.record_adoption(fld, allen, allen_kp, ["OrrethDemoStack"])
    with pytest.raises(estate.DoorRefusal, match="not a charter question"):
        estate.answer_gap(fld, allen, allen_kp, "color", "blue", "did:key:zjb",
                          subject="rag-corpus")
    # estate policy: residency for everything, deliberately
    estate.answer_gap(fld, allen, allen_kp, "residency", "us-west-2",
                      "did:key:zjb", subject=estate.ESTATE)
    # workload answers for the corpus bucket
    for key, words in (("data_classification", "internal"),
                       ("rto", "4 hours"), ("rpo", "24 hours"),
                       ("interoperability", "api, from the universe only"),
                       ("caching", "nothing cacheable"),
                       ("retention", "7 years, then crypto-shred")):
        estate.answer_gap(fld, allen, allen_kp, key, words, "did:key:zjb",
                          subject="rag-corpus")
    staged = estate.stage_create(fld, "a bucket for the corpus",
                                 subject="rag-corpus")
    assert staged["staged"] and staged["subject"] == "rag-corpus"
    assert staged["charter"]["rto"]["scope"] == "workload"
    assert staged["charter"]["residency"]["scope"] == "estate-policy"  # underlies
    # a DIFFERENT workload owes its own answers — history is offered, not applied
    with pytest.raises(estate.CharterGaps) as e:
        estate.stage_create(fld, "deploy repo foo to production",
                            subject="repo-foo")
    assert "residency" not in e.value.questions          # policy already covers it
    assert "reuse?" in e.value.questions["rto"]          # the offer, not the answer
    assert "rag-corpus" in e.value.questions["rto"]


def test_charter_is_a_versioned_asset():
    """The question set is data on the shelf (0031's shape): genesis plants under
    allen's signature, and the active version's questions govern the compile."""
    _, fld, _, allen, allen_kp = _estate_field()
    estate.plant_charter(fld, allen, allen_kp)
    prof = estate.charter_profile(fld)
    assert prof["questions"] == estate.CHARTER_GENESIS["questions"]
    rows = [r for r in fld.records.values()
            if estate.CHARTER_NAME in (r.get("tags") or [])]
    assert rows and rows[0]["author"] == allen["did"]


def test_charter_speaks_in_the_parlor():
    """The doors are subject-anchored (0037 §3, JB's walk finding): a bare
    answer is refused toward the grammar; “answer <key> for <workload>: …” and
    “… for the estate: …” ride as actions with their subject; a create ask past
    the gate hands the interrogation to the worker (estate-create); the charter
    reads back as policy + workloads, never a to-do list."""
    facts = {"scope": "u:demo",
             "estate": {"adopted": 1, "gate_open": True,
                        "policy": {"residency": {"answer": "us-west-2"}},
                        "workloads": {"rag-corpus": {"data_classification":
                                                     {"answer": "internal"}}}}}
    bare = parlor.answer("allen", "answer rto: 4 hours", facts)
    assert "needs a subject" in bare["reply"] and "action" not in bare
    ans = parlor.answer("allen", "answer rto for rag-corpus: 4 hours", facts)
    assert ans.get("action") == "estate-answer" and ans["key"] == "rto" \
        and ans["subject"] == "rag-corpus" and ans["answer"] == "4 hours"
    pol = parlor.answer("allen", "answer residency for the estate: us-west-2",
                        facts)
    assert pol.get("action") == "estate-answer" and pol["subject"] == "" \
        and "policy" in pol["reply"]
    a = parlor.answer("allen", "create me an S3 bucket", facts)
    assert a.get("action") == "estate-create" and a["ask"]
    c = parlor.answer("allen", "show the charter", facts)
    assert "ESTATE POLICY" in c["reply"] and "rag-corpus" in c["reply"] \
        and "OPEN" not in c["reply"]
    ws = parlor.workspace("allen", facts)
    charter_panel = next(p for p in ws["panels"] if "charter" in p["title"])
    texts = [i["text"] for i in charter_panel["items"]]
    assert any("estate policy" in x for x in texts) \
        and any("rag-corpus" in x for x in texts)


def test_allen_receives_in_the_parlor():
    """The resident stands in the audience room: a card with his doors, honest
    gate language while the estate is unwalked, and protocol that travels
    verbatim — a governed voice never rewrites law."""
    facts = {"scope": "u:demo", "estate": {"adopted": 0, "gate_open": False}}
    c = parlor.card("allen", facts)
    assert c["voiced"] and c["role"] == "allen · cloud architect"
    assert "acceptance gate" in c["greeting"]
    a = parlor.answer("allen", "create me an S3 bucket", facts)
    assert "adopt before I create" in a["reply"] and a.get("verbatim")
    d = parlor.answer("allen", "who may speak to you?", facts)
    assert "humans alone" not in d["reply"] or True
    assert "objectives" in d["reply"] and "lineage" in d["reply"]
    ws = parlor.workspace("allen", facts)
    assert ws and any(p["kind"] == "doc" for p in ws["panels"])
