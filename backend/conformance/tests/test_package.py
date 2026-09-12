# PROVENANCE: Claude Fable 5 (claude-fable-5) — 0072 sp4, the package · 2026-09-12
"""The package's laws (KCR-0002's payment): identity is the bytes,
provenance is the signature, crew never shells into a checkout, and the
receiving vocabulary is the canon's own."""
import pytest

from orreth_sim import crypto, package

KP = crypto.KeyPair()
DID = crypto.did_key_for(KP.public)
MAN = {"key": "boxed", "name": "Boxed World", "view": [
    {"kind": "chat", "label": "the chat"}], "floors": [{"scope": "u:t/e:x"}]}
KINDS = {"chat", "sources", "workspace"}


def _box(**kw):
    args = dict(key="boxed", manifest=MAN, craft={"boxed-gloss": {"t": "w"}},
                crew=[], keypair=KP, publisher_did=DID)
    args.update(kw)
    return package.pack(**args)


def test_pack_verify_roundtrip_and_content_address():
    b = _box()
    assert package.verify(b, KINDS) is None
    assert b["id"].startswith("sha256:")
    assert b["id"] == _box()["id"]           # same bytes, same box


def test_a_changed_byte_is_a_different_box():
    b = _box()
    b["declarations"]["craft"]["smuggled"] = {"t": "x"}
    why = package.verify(b, KINDS)
    assert why and "not the hash" in why


def test_a_forged_signature_refuses():
    b = _box()
    other = crypto.KeyPair()
    b["signature"] = other.sign(DID, b)      # someone else's pen, my name
    why = package.verify(b, KINDS)
    assert why and "signature" in why


def test_crew_never_shells_into_a_checkout():
    with pytest.raises(ValueError, match="checkout era"):
        package.pack(key="boxed", manifest=MAN,
                     crew=[{"name": "x", "image": "img:1",
                            "cmd": "uv run python evil.py"}],
                     keypair=KP, publisher_did=DID)
    b = _box()
    b["declarations"]["crew"] = [{"name": "x", "image": "img:1",
                                  "cwd": "backend"}]
    b["id"] = crypto.content_hash(
        {"format": package.FORMAT, "key": "boxed",
         "declarations": b["declarations"]})
    b["signature"] = KP.sign(DID, b)
    why = package.verify(b, KINDS)           # re-sealed by the publisher —
    assert why and "checkout era" in why     # the LAW still refuses it


def test_beyond_canon_panels_refuse_at_the_receiving_world():
    man = dict(MAN, view=[{"kind": "hologram", "label": "x"}])
    b = package.pack(key="boxed", manifest=man, keypair=KP,
                     publisher_did=DID)
    why = package.verify(b, KINDS)
    assert why and "hologram" in why and "RELEASE" in why


def test_the_gate_card_summary_carries_the_weighables():
    s = package.summary(_box())
    assert s["key"] == "boxed" and s["rooms"] == ["chat"]
    assert s["publisher"] == DID and s["id"].startswith("sha256:")
    assert s["craft"] == ["boxed-gloss"]
