# PROVENANCE: Fable 5 (claude-fable-5) — the Shipyard (0009's provisioner, first wire landing) · 2026-07-07
"""The Shipyard: a universe that grows by conversation — planned pure, gated human.

Under test: the launch plan (names validated, ports allocated around the composed
rig, profiles carrying the same dials the rig boots with), and the parlor grammar
that turns "create ecosystem foo with fields bar, baz" into a staged intent — with
the fields QUESTION asked when the caller hasn't said.
"""
import pytest

from orreth_sim import parlor, shipyard

ROOT = "did:web:orreth.ai:u:demo"


def test_the_plan_lays_a_hull_and_moons():
    p = shipyard.plan("u:demo", "foo", ["bar", "baz"], {4500, 4501, 4502}, ROOT)
    assert p["eco"]["scope"] == "u:demo/e:foo" and p["eco"]["port"] == 4503
    assert [m["scope"] for m in p["fields"]] == ["u:demo/e:foo/f:bar", "u:demo/e:foo/f:baz"]
    assert [m["port"] for m in p["fields"]] == [4504, 4505]
    assert p["fields"][0]["parent_container"] == p["eco"]["container"]


def test_ports_step_around_whats_taken():
    p = shipyard.plan("u:demo", "solo", [], {4500, 4501, 4502, 4503, 4505}, ROOT)
    assert p["eco"]["port"] == 4504 and p["fields"] == []
    assert "sailing alone" in p["summary"]


def test_profiles_wear_the_rigs_own_dials():
    eco = shipyard.eco_profile("u:demo", "foo", ROOT)
    fld = shipyard.field_profile("u:demo/e:foo", "bar", ROOT)
    assert eco["tier_label"] == "ecosystem" and not eco["is_leaf"]
    assert eco["retrieval"]["horizon"] == "P395D"
    assert fld["tier_label"] == "field" and fld["is_leaf"]
    assert fld["retrieval"]["horizon"] == "P90D"
    assert eco["trust_root"]["root"] == ROOT == fld["trust_root"]["root"]


def test_unsailable_names_never_leave_the_dock():
    for bad in ("Foo", "e cosystem", "", "x" * 25, "rm -rf", "foo/bar"):
        with pytest.raises(ValueError):
            shipyard.plan("u:demo", bad, [], set(), ROOT)
    with pytest.raises(ValueError):
        shipyard.plan("u:demo", "ok", ["BAD"], set(), ROOT)


def test_becky_hears_grow_and_asks_the_fields_question():
    assert parlor.parse_grow("what is serving?") is None
    assert parlor.parse_grow("create ecosystem foo") == ("foo", None)
    assert parlor.parse_grow("create ecosystem foo with fields bar, baz") == ("foo", ["bar", "baz"])
    assert parlor.parse_grow("add ecosystem retail with fields web and pos") == ("retail", ["web", "pos"])
    assert parlor.parse_grow("grow ecosystem lab as is") == ("lab", [])
    # no fields named → becky asks before anything stages
    asked = parlor.answer("becky", "create ecosystem foo", {"scope": "u:demo"})
    assert "would you like one or more fields" in asked["reply"] and "action" not in asked
    staged = parlor.answer("becky", "create ecosystem foo with fields bar", {"scope": "u:demo"})
    assert staged["action"] == "ecosystem" and staged["eco"] == "foo" and staged["fields"] == ["bar"]
    alone = parlor.answer("becky", "create ecosystem foo as is", {"scope": "u:demo"})
    assert alone["action"] == "ecosystem" and alone["fields"] == []
