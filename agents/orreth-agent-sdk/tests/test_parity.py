# PROVENANCE: authored by Opus 4.8 (2026-07-05), pending Fable 5 review — see agents/PROVENANCE.md
"""The SDK signs bytes the plane must accept. This proves it — canonicalization parity
against the Orreth reference, plus a signature the reference verifier accepts.

    cd agents/orreth-agent-sdk && uv run --with cryptography \
        --with pytest --with ../../backend/conformance pytest -q
    # or simply, from backend/conformance's env which already has orreth_sim:
    #   PYTHONPATH=agents/orreth-agent-sdk:backend/conformance pytest agents/orreth-agent-sdk/tests
"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "backend" / "conformance"))

from orreth_agent import crypto as sdk

try:
    from orreth_sim import crypto as ref
except Exception:                                    # reference not importable → skip parity
    ref = None

# Inputs chosen to break naive canonicalization: key order, non-ASCII, nesting, unicode.
CASES = [
    {"b": 1, "a": 2},
    {"z": {"y": 3, "x": [1, 2, 3]}, "a": "café · déjà"},
    {"knowledge": "wind ≥ 40 m/s · –18 °C", "source": {"ref": "https://x/é"}},
    {"nested": {"deep": {"deeper": {"k": "π ≈ 3.14159"}}}, "list": [{"b": 1}, {"a": 2}]},
]


@pytest.mark.skipif(ref is None, reason="orreth_sim reference not on path")
@pytest.mark.parametrize("obj", CASES)
def test_canonical_bytes_match_reference(obj):
    assert sdk.canonical(obj) == ref.canonical(obj)


@pytest.mark.skipif(ref is None, reason="orreth_sim reference not on path")
@pytest.mark.parametrize("obj", CASES)
def test_content_hash_matches_reference(obj):
    assert sdk.content_hash(obj) == ref.content_hash(obj)


@pytest.mark.skipif(ref is None, reason="orreth_sim reference not on path")
def test_reference_verifier_accepts_sdk_signature():
    """A signature the SDK produces must verify under the reference's verifier — the exact
    property the plane relies on when it checks an agent's memory."""
    kp = sdk.KeyPair()
    did = sdk.did_key_for(kp.public)
    payload = {"id": "sha256:x", "kind": "episodic", "scope": "u:demo/e:cloud/f:prod",
               "author": did, "occurred_at": "2026-07-05T00:00:00Z", "provenance_class": "lived"}
    sig = kp.sign(did, payload)
    assert ref.verify_sig(sig, payload, kp.public)


def test_did_key_roundtrip():
    kp = sdk.KeyPair(seed=b"\x01" * 32)
    assert sdk.did_key_for(kp.public).startswith("did:key:z")
    assert sdk.KeyPair(seed=kp.seed).public == kp.public       # seed persists the identity


# ---- 0068 sp4: the rails twin (Fable 5, 2026-09-10) --------------------------------
# The SDK carries its own copy of the content rails so a field agent enforces
# the same law the kernel's lanes do. One corpus through both modules —
# detection, masking, refusal, and events must be IDENTICAL.

RAIL_CORPUS = [
    "clean text with nothing to see",
    "pay with 4111 1111 1111 1111 today",
    "the SSN on file is 078-05-1120.",
    "mail jo@example.com or call 555-867-5309",
    "078-05-1120 paid with 4111-1111-1111-1111",
    "order 4111 1111 1111 1112 shipped",          # Luhn-invalid: not an incident
]

RAIL_SETS = [
    {"rules": [
        {"match": {"category": "pii", "direction": "leaving"}, "action": "mask",
         "reason": "pii masked leaving"},
        {"match": {"category": "pci", "direction": "both"}, "action": "refuse",
         "reason": "pci never rides"}]},
    {"rules": [
        {"match": {"category": "pii", "direction": "both"},
         "action": "quarantine", "reason": "hold for a human"}]},
]


@pytest.mark.skipif(ref is None, reason="orreth_sim reference not on path")
@pytest.mark.parametrize("text", RAIL_CORPUS)
@pytest.mark.parametrize("direction", ["entering", "leaving"])
def test_rails_enforcement_matches_reference(text, direction):
    from orreth_agent import rails as sdk_rails
    from orreth_sim import rails as ref_rails
    for rules in RAIL_SETS:
        assert (sdk_rails.enforce(rules, direction, text)
                == ref_rails.enforce(rules, direction, text))
