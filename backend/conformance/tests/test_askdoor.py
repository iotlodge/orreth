# PROVENANCE: Claude Fable 5 (claude-fable-5) — 0071 sp2, the ask door's laws · 2026-09-08
"""The ask door (0071 sp2): signature never bearer · refs always whole · the
selection never a secret. Laws, not scores."""
from orreth_sim import askdoor, crypto
from orreth_sim.identity import NOW

import pytest


def _signed(text="what protects walls from rain?", variant=None):
    kp = crypto.KeyPair()
    did = crypto.did_key_for(kp.public)
    return kp, did, askdoor.make_ask(kp, did, text, at=NOW(), variant=variant)


def test_signed_ask_verifies():
    _, did, ask = _signed()
    ok, why = askdoor.verify_ask(ask)
    assert ok and why == "verified"
    assert ask["did"] == did and "sig" in ask


def test_tampered_text_refuses():
    _, _, ask = _signed()
    ask["text"] = "a different question entirely"
    ok, _ = askdoor.verify_ask(ask)
    assert not ok


def test_foreign_key_refuses():
    kp1, did1, _ = _signed()
    kp2 = crypto.KeyPair()
    forged = {"kind": "ask", "did": did1, "text": "q", "at_signed": NOW()}
    forged["sig"] = kp2.sign(did1, {"did": did1, "text": "q",
                                    "at": forged["at_signed"]})
    ok, _ = askdoor.verify_ask(forged)
    assert not ok


def test_unsigned_refuses():
    ok, why = askdoor.verify_ask({"did": "did:key:zSomeone", "text": "q"})
    assert not ok and "signed" in why


def test_non_didkey_refuses():
    ok, _ = askdoor.verify_ask({"did": "did:web:example.com", "text": "q",
                                "sig": {"x": 1}})
    assert not ok


def test_envelope_refs_are_whole():
    env = askdoor.envelope(
        reply="the answer", by="did:key:zSeat",
        citations=[{"doc": "walls", "ref": "sha256:" + "a" * 64, "score": 0.9}],
        variant="graph", choice_ref="sha256:" + "b" * 64,
        exchange="sha256:" + "c" * 64)
    assert env["variant"] == "graph"
    assert env["choice_ref"].startswith("sha256:")
    assert env["guardrails"]["set_version"] is None  # honest until 0068 builds


def test_envelope_refuses_shortened_refs():
    with pytest.raises(ValueError):
        askdoor.envelope(reply="r", by="d",
                         citations=[{"doc": "x", "ref": "sha256:abcdef01…",
                                     "score": 0.1}],
                         variant="naive", choice_ref="sha256:" + "b" * 64,
                         exchange="e")
    with pytest.raises(ValueError):
        askdoor.envelope(reply="r", by="d", citations=[],
                         variant="naive", choice_ref="sha256:abcd…",
                         exchange="e")


def test_variant_rides_the_ask_and_the_confession_rides_the_grace():
    _, _, ask = _signed(variant="graph")
    assert ask["variant"] == "graph"
    env = askdoor.envelope(reply="r", by="d", citations=[], variant="graph",
                           choice_ref="sha256:" + "b" * 64, exchange="e",
                           confession="unsigned ask served under dev grace")
    assert "dev grace" in env["confession"]