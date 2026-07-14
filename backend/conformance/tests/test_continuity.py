# PROVENANCE: authored by Fable 5 (claude-fable-5), 2026-07-14 — 0034, the Continuity Universe
"""The continuity template (0034 §7 sp1): the label canon is structural, the
retention regime is law on the substrate, and the provisioner renders the
template — a floor is born wearing its dignity."""
import json

import pytest

from orreth_sim import continuity, crypto, parlor, shipyard
from orreth_sim.node import make_memory
from orreth_sim.world import build


@pytest.fixture()
def world():
    return build()


def _body(rec):
    return json.loads(crypto._b64d(rec["body"]).decode())


def test_the_label_canon_speaks_from_the_state():
    """0034 §3: honest confidence in human words — the sentence shape comes off
    the record's state; a mind cannot upgrade confidence the substrate doesn't
    hold, and the recalled are never spoken as memory."""
    say = continuity.speak_claim
    assert say("verified", "on May 12th you visited Anna") \
        == "on May 12th you visited Anna"               # say it plainly
    assert say("trusted", "my sister is Anna") == "my sister is Anna"
    corr = say("corroborated", "you were at the coast in May",
               sources=["the photos", "your calendar"])
    assert "the photos, your calendar" in corr           # show the receipts
    hedged = say("untrusted", "this trip happened in May 2024", hints=2)
    assert hedged.startswith("this MAY be so") and "not proof" in hedged
    assert say("investigating", "the address changed") \
        .startswith("I'm re-checking")                   # doubt out loud
    assert say("recalled", "a poisoned claim") is None   # the dead never speak


def test_the_regime_is_law_on_the_substrate(world):
    """0034 §2 through 0033 §5: identity at λ≈0 and medication zero-D — the
    intolerables ride every distillation with their sources cited, while the
    narrative compresses away. The template is physics, not preference."""
    f = world.field_prod
    continuity.apply(f)
    me = {"did": f.steward["did"], "scope": f.scope}
    ids = []
    for who, rel in (("Michael", "your neighbor"), ("Anna", "your sister")):
        rec = make_memory(me, f.steward_kp, f.scope,
                          {"name": who, "relationship": rel,
                           "narrative": "a long visit remembered warmly " * 10},
                          kind="semantic", tags=["identity"])
        ids.append(f.write(rec))
    dist = f._distill(ids, push=False)
    body = _body(dist)
    assert {e["value"] for e in body["preserved"]["name"]} == {"Michael", "Anna"}
    assert {e["value"] for e in body["preserved"]["relationship"]} \
        == {"your neighbor", "your sister"}
    assert "narrative" not in body["preserved"]          # the compressible compresses
    assert body["contract"]["distortion_bound"] == 0.0   # λ≈0 — who people are survives


def test_the_provisioner_renders_the_template():
    """0034 §7 sp1: plan(template="continuity") dresses every profile — the
    dignity vector (summing to 1.0, unsupported-memory heaviest), the regime,
    the canon; an unknown template is refused by name."""
    p = shipyard.plan("u:demo", "care", ["home"], set(), "did:web:test",
                      template="continuity")
    assert p["summary"].startswith("a continuity e:care")
    for spec in (p["eco"], p["fields"][0]):
        prof = spec["profile"]
        assert spec["template"] == "continuity"
        assert prof["template"] == "continuity"
        weights = [o["weight"] for o in prof["objective"]]
        assert abs(sum(weights) - 1.0) < 1e-9
        assert prof["objective"][0]["objective"] == "unsupported-memory-rate"
        assert prof["distortion_contracts"]["identity"]["distortion_bound"] == 0.0
        assert prof["label_canon"]["recalled"] == "never spoken as memory"
        assert prof["memory"]["distilled_retention"] == "P3650D"
    # a plain plan is untouched — the template never leaks
    plain = shipyard.plan("u:demo", "plain", [], set(), "did:web:test")
    assert "template" not in plain["eco"]
    assert "template" not in plain["eco"]["profile"]
    with pytest.raises(ValueError):
        shipyard.plan("u:demo", "x", [], set(), "did:web:test", template="bogus")


def test_the_parlor_hears_the_template():
    """0034 §7 sp1 at becky's door: "create continuity ecosystem …" stages with
    the template named, verbatim; plain grows keep their shape."""
    tpl, plain = parlor.grow_template(
        "create continuity ecosystem care with fields home")
    assert tpl == "continuity"
    assert parlor.parse_grow(plain) == ("care", ["home"])
    assert parlor.grow_template("create ecosystem care") == (None,
                                                             "create ecosystem care")
    ans = parlor.answer("becky",
                        "create continuity ecosystem care with fields home", {})
    assert ans["action"] == "ecosystem" and ans["template"] == "continuity"
    assert ans["verbatim"] is True and "continuity template" in ans["reply"]
    ans2 = parlor.answer("becky", "create ecosystem plain as is", {})
    assert ans2["action"] == "ecosystem" and "template" not in ans2


def test_the_charter_is_config_as_memory(world):
    """R8: the floor's law on its own record — template, vector, regime, canon,
    legible to the glass and to every resident."""
    f = world.field_prod
    me = {"did": f.steward["did"], "scope": f.scope}
    rec = continuity.make_charter(me, f.steward_kp, f.scope)
    assert "continuity-charter" in rec["tags"]
    ch = _body(rec)["continuity_charter"]
    assert ch["template"] == "continuity"
    assert ch["regime"]["medication"]["contract"]["must_preserve"] \
        == ["dosage", "timing"]
    assert ch["regime"]["location"]["retention"] == "PT10M"
    assert ch["label_canon"]["untrusted"] == "hedged honestly — may, never definitely"
