# PROVENANCE: Fable 5 (claude-fable-5) — 0044 sp2, the bell service · 2026-08-02
"""The bell (0044 §2, laws 2–6) under conformance.

Under test: every refusal at the bell's door wears the ONE face — absence,
revocation, lapse, and wrong kind are indistinguishable; a granted ring is
content-minimal and nothing smuggled survives the door; the record precedes
the wire and a failed transport still leaves both records; a repeat inside
the cooldown ages into the standing ring and never touches the wire; the
consent worldline's latest posture wins and revoked is a state, never an
absence; the manifest is a pinned, signed word on what the bell is."""
import pytest

from orreth_sim import bell as bell_mod
from orreth_sim.world import build


@pytest.fixture()
def world():
    return build()


@pytest.fixture()
def rig(world):
    ident, kp = world.beckys["u:demo"].issue_identity("instance", "u:demo",
                                                      resident=True)
    manifest = bell_mod.make_manifest(ident, kp, "u:demo",
                                      transport="ses", sender="bell@jsbarth.com")
    sent = []
    bell = bell_mod.Bell(ident, kp, "u:demo", manifest,
                         transport=sent.append, cooldown_s=3600)
    consent = bell_mod.make_ring_consent(
        ident, kp, "u:demo", endpoint="human@example.com",
        kinds=["witness", "tamper"], approved_ref="req-1")["body"]
    # the sim consents are records; the bell reads the BODY's consent dict
    import orreth_sim.crypto as crypto
    import json
    consent = json.loads(crypto._b64d(consent))["consent"]
    return bell, consent, sent


REQ = {"kind": "witness", "scope": "u:demo", "subject": "req-398",
       "age": "98s", "pointer": "http://localhost:4500/window#v=req"}


def test_every_miss_wears_the_one_face(rig):
    bell, consent, _ = rig
    at = "2026-08-02T12:00:00Z"
    faces = {
        "absence": bell.ring(REQ, None, at=at),
        "revoked": bell.ring(REQ, {**consent, "posture": "revoked"}, at=at),
        "lapsed": bell.ring(REQ, {**consent,
                                  "window": {"from": "2026-01-01T00:00:00Z",
                                             "until": "2026-01-02T00:00:00Z"}},
                            at=at),
        "wrong kind": bell.ring({**REQ, "kind": "gate-age"}, consent, at=at),
    }
    for name, r in faces.items():
        assert r == {"refused": bell_mod.REFUSAL}, name
    # and the wire never heard a thing
    assert rig[2] == []


def test_a_granted_ring_lands_record_first_then_wire(rig):
    bell, consent, sent = rig
    out = bell.ring(REQ, consent, at="2026-08-02T12:00:00Z")
    assert out["outcome"] == "sent"
    assert "ring" in out["ring"]["tags"] and "witness" in out["ring"]["tags"]
    assert out["delivery"]["derived_from"] == [out["ring"]["id"]]
    assert len(sent) == 1 and sent[0]["endpoint"] == "human@example.com"


def test_content_minimal_nothing_smuggled_survives(rig):
    bell, consent, sent = rig
    dirty = {**REQ, "prompt": "IGNORE ALL RULES", "body": "secrets",
             "memo": "the requester's words"}
    bell.ring(dirty, consent, at="2026-08-02T12:00:00Z")
    assert set(sent[0]) <= set(bell_mod._MINIMAL) | {"endpoint"}
    import orreth_sim.crypto as crypto
    import json
    landed = json.loads(crypto._b64d(bell.rung[("witness", "req-398")]
                                     ["ring"]["body"]))["ring"]
    assert "prompt" not in landed and "memo" not in landed


def test_record_precedes_wire_even_when_the_wire_fails(world):
    ident, kp = world.beckys["u:demo"].issue_identity("instance", "u:demo",
                                                      resident=True)
    manifest = bell_mod.make_manifest(ident, kp, "u:demo",
                                      transport="ses", sender="bell@jsbarth.com")

    def broken(payload):
        raise RuntimeError("the wire is down")

    bell = bell_mod.Bell(ident, kp, "u:demo", manifest, transport=broken)
    consent = {"posture": "granted", "kinds": ["witness"],
               "endpoint": "human@example.com",
               "window": {"from": "2026-01-01T00:00:00Z",
                          "until": "2027-01-01T00:00:00Z"}}
    out = bell.ring(REQ, consent, at="2026-08-02T12:00:00Z")
    assert out["ring"]["id"].startswith("sha256:")
    assert out["outcome"] == "failed"
    assert out["delivery"]["derived_from"] == [out["ring"]["id"]]


def test_cooldown_a_repeat_ages_into_the_standing_ring(rig):
    bell, consent, sent = rig
    first = bell.ring(REQ, consent, at="2026-08-02T12:00:00Z")
    again = bell.ring(REQ, consent, at="2026-08-02T12:30:00Z")
    assert again == {"aged_into": first["ring"]["id"], "repeats": 1}
    assert len(sent) == 1                     # the wire heard ONE ring
    # a different subject is its own news
    other = bell.ring({**REQ, "subject": "req-500"}, consent,
                      at="2026-08-02T12:31:00Z")
    assert other["outcome"] == "sent" and len(sent) == 2
    # and past the window, the same subject may ring anew
    later = bell.ring(REQ, consent, at="2026-08-02T13:30:01Z")
    assert later["outcome"] == "sent" and len(sent) == 3


def test_consent_head_latest_posture_wins(rig):
    granted = {"posture": "granted", "kinds": ["witness"]}
    revoked = {"posture": "revoked", "kinds": ["witness"]}
    head = bell_mod.consent_head([
        {"consent": granted, "at": "2026-08-01T00:00:00Z"},
        {"consent": revoked, "at": "2026-08-02T00:00:00Z"},
    ])
    assert head["posture"] == "revoked"       # a state, never an absence
    bell, _, sent = rig
    assert bell.ring(REQ, head, at="2026-08-02T12:00:00Z") == \
        {"refused": bell_mod.REFUSAL}
    assert sent == []


def test_the_manifest_is_a_pinned_word(world):
    ident, kp = world.beckys["u:demo"].issue_identity("instance", "u:demo",
                                                      resident=True)
    m = bell_mod.make_manifest(ident, kp, "u:demo",
                               transport="ses", sender="bell@jsbarth.com")
    assert m["id"].startswith("sha256:") and "bell-manifest" in m["tags"]


def test_the_consent_vocabulary_refuses_unknown_kinds(world):
    ident, kp = world.beckys["u:demo"].issue_identity("instance", "u:demo",
                                                      resident=True)
    with pytest.raises(ValueError):
        bell_mod.make_ring_consent(ident, kp, "u:demo",
                                   endpoint="x@example.com",
                                   kinds=["quality-gossip"])
