"""Real crypto from day one (0000 §3): Ed25519 signatures + sha256 content addressing.

The HMAC stand-in is never built twice — even the simulator signs for real.
"""
from __future__ import annotations

import base64
import hashlib
import json

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat


def canonical(obj) -> bytes:
    """Canonical JSON: sorted keys, no whitespace. The thing that gets hashed and signed."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()


def content_hash(obj) -> str:
    return "sha256:" + hashlib.sha256(canonical(obj)).hexdigest()


def _b64e(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode().rstrip("=")


def _b64d(s: str) -> bytes:
    return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))


class KeyPair:
    def __init__(self, seed: bytes | None = None) -> None:
        self._priv = (Ed25519PrivateKey.from_private_bytes(seed) if seed
                      else Ed25519PrivateKey.generate())

    @property
    def seed(self) -> bytes:
        """The raw private bytes — for root/becky persistence across processes (0006)."""
        from cryptography.hazmat.primitives.serialization import (
            NoEncryption, PrivateFormat)
        return self._priv.private_bytes(Encoding.Raw, PrivateFormat.Raw, NoEncryption())

    @property
    def public(self) -> str:
        raw = self._priv.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)
        return "z" + _b64e(raw)

    def sign(self, by_did: str, payload: dict) -> dict:
        """Produce a Sig (common.schema.json#/$defs/Sig) over canonical(payload minus any 'signature'/'sig')."""
        body = {k: v for k, v in payload.items() if k not in ("signature", "sig")}
        return {
            "alg": "ed25519",
            "by": by_did,
            "sig": _b64e(self._priv.sign(canonical(body))),
        }


def verify_sig(sig: dict, payload: dict, public: str) -> bool:
    """Verify a Sig against a payload and a public key ('z' + urlsafe-b64 raw ed25519)."""
    body = {k: v for k, v in payload.items() if k not in ("signature", "sig")}
    try:
        key = Ed25519PublicKey.from_public_bytes(_b64d(public[1:]))
        key.verify(_b64d(sig["sig"]), canonical(body))
        return True
    except (InvalidSignature, ValueError, KeyError):
        return False


def did_key_for(public: str) -> str:
    """did:key embeds the public key — resolvable offline, no index needed for key material (0006 §1)."""
    return f"did:key:{public}"


def public_from_did(did: str) -> str | None:
    if did.startswith("did:key:"):
        return did.removeprefix("did:key:")
    return None  # did:web keys resolve via the index (NANDA sim)
