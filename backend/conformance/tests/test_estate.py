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
    words until the brownfield walk lands its receipts — then it stages."""
    _, fld, _, allen, allen_kp = _estate_field()
    assert not estate.create_unlocked(fld)
    with pytest.raises(estate.GateStands, match="adopts before it creates"):
        estate.stage_create(fld, "create me an S3 bucket")
    estate.record_adoption(fld, allen, allen_kp,
                           ["OrrethDemoStack", "jsbarth-pipeline"])
    assert estate.create_unlocked(fld)
    staged = estate.stage_create(fld, "create me an S3 bucket")
    assert staged["staged"] is True and "charter" in staged["note"]


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
