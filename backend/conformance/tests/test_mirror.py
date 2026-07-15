# PROVENANCE: authored by Fable 5 (claude-fable-5), 2026-07-14 — 0034 sp3, the Mirror
"""The Mirror (0034 sp3): assessor ≠ assessed, both sides of the glass updated,
the interoperability profile as its ledger — identity and counting, never
meaning."""
import json

import pytest

from orreth_sim import crypto, mirror, profile
from orreth_sim.world import build


@pytest.fixture()
def world():
    return build()


def _body(rec):
    return json.loads(crypto._b64d(rec["body"]).decode())


def _aud(i, resident="librarian", asked="where are my reading glasses",
         reply="3 claim(s) held: …", author="did:key:zSeat"):
    return {"ref": f"sha256:aud{i}", "resident": resident, "asked": asked,
            "reply": reply, "author": author, "at": f"2026-07-14T0{i}:00:00Z"}


def test_the_mirror_sorts_by_identity_never_meaning():
    """Repeated asks are found by normalized identity; recurring words surface;
    an unmet reply is friction — counted, never judged."""
    audiences = [
        _aud(1, asked="Where are my reading glasses?"),
        _aud(2, asked="where are my reading glasses",
             reply="nothing held here"),
        _aud(3, asked="tell me about my medication schedule"),
        _aud(4, asked="what medication do I take in the morning"),
        _aud(5, asked="is my medication refill due",
             reply="nothing gathered — the Farm has no serving search source."),
    ]
    a = mirror.assess(audiences)["librarian"]
    assert a["exchanges"] == 5
    assert a["repeats"] == [("where are my reading glasses", 2)]
    assert ("medication", 3) in a["topics"]
    assert len(a["friction"]) == 2
    assert len(a["refs"]) == 5


def test_the_mirror_never_reads_its_own_reflection():
    """0005, absolute: rows the Mirror authored are invisible to it — a mirror
    that assesses its own reflections is a hall of mirrors."""
    mine = "did:key:zMirror"
    audiences = [_aud(1), _aud(2, author=mine), _aud(3, author=mine)]
    a = mirror.assess(audiences, mirror_did=mine)["librarian"]
    assert a["exchanges"] == 1


def test_both_sides_of_the_glass(world):
    """The profile stroke enters UNTRUSTED with evidence required (0025 — the
    Mirror is never the human); the friction note counts and never judges."""
    stats = {"exchanges": 5,
             "repeats": [("where are my reading glasses", 2)],
             "topics": [("medication", 3)],
             "friction": ["sha256:aud2", "sha256:aud5"],
             "refs": ["sha256:aud1"]}
    obs = mirror.observations("librarian", stats)
    assert any("2 times" in o and "reading glasses" in o for o in obs)
    assert any("medication" in o for o in obs)
    note = mirror.friction_note("librarian", stats)
    assert "2 of 5" in note and "came back empty" in note
    assert mirror.friction_note("librarian", {**stats, "friction": []}) is None
    f = world.field_prod
    mir = {"did": "did:key:zMirror", "scope": f.scope}
    rec = profile.make_claim(mir, f.steward_kp, f.scope, obs[0],
                             asserted_by="mirror", inferred_from="sha256:ev1")
    assert _body(rec)["profile"]["state"] == "untrusted"
    assert rec["derived_from"] == ["sha256:ev1"]
    with pytest.raises(ValueError):           # an inference names its evidence
        profile.make_claim(mir, f.steward_kp, f.scope, "x", asserted_by="mirror")
    human = profile.make_claim(mir, f.steward_kp, f.scope, "I toast with cocoa",
                               asserted_by="human")
    assert _body(human)["profile"]["state"] == "trusted"


def test_the_interop_ledger_is_a_worldline(world):
    """One worldline per resident, a sibling per sweep, evidence cited — the
    relationship measured, never self-reported."""
    f = world.field_prod
    mir = {"did": f.steward["did"], "scope": f.scope}
    stats = {"exchanges": 3, "repeats": [("where are my keys", 2)],
             "topics": [], "friction": ["sha256:aud2"],
             "refs": [f"sha256:aud{i}" for i in range(1, 20)]}
    first = mirror.make_interop(mir, f.steward_kp, f.scope, "librarian", stats,
                                window={"from": "t1", "to": "t3"})
    f.write(first)
    b = _body(first)["interop"]
    assert b["resident"] == "librarian" and b["friction"] == 1
    assert b["repeats"][0] == {"ask": "where are my keys", "times": 2}
    assert len(b["evidence"]) == 12           # cited, capped, honest
    second = mirror.make_interop(mir, f.steward_kp, f.scope, "librarian",
                                 {**stats, "exchanges": 4},
                                 window={"from": "t3", "to": "t4"},
                                 prev=first["id"])
    f.write(second)
    rows = [{"id": rid, "interop": _body(r)["interop"],
             "derived_from": r.get("derived_from") or [], "at": r["received_at"]}
            for rid, r in f.records.items() if "mirror" in r.get("tags", [])]
    rows.sort(key=lambda x: x["at"])
    heads = mirror.interop_heads(rows)
    assert len(heads) == 1 and heads[0]["exchanges"] == 4
    assert first["id"] in f.records           # the sweep history never vanishes
