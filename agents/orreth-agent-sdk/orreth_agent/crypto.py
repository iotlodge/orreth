"""Real crypto, vendored from the Orreth reference (0000 §3) so the SDK stands alone.

Byte-for-byte parity with the plane's canonicalization is the contract: sorted keys,
compact separators, ensure_ascii escaping — the exact bytes that get hashed and signed.
"""
from __future__ import annotations

import base64
import hashlib
import json

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, NoEncryption, PrivateFormat, PublicFormat


def canonical(obj) -> bytes:
    """Canonical JSON: sorted keys, no whitespace. The thing that gets hashed and signed."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()


def content_hash(obj) -> str:
    return "sha256:" + hashlib.sha256(canonical(obj)).hexdigest()


def b64e(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode().rstrip("=")


def b64d(s: str) -> bytes:
    return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))


class KeyPair:
    """An Ed25519 identity. Persist the seed and the identity survives the process."""

    def __init__(self, seed: bytes | None = None) -> None:
        self._priv = (Ed25519PrivateKey.from_private_bytes(seed) if seed
                      else Ed25519PrivateKey.generate())

    @property
    def seed(self) -> bytes:
        return self._priv.private_bytes(Encoding.Raw, PrivateFormat.Raw, NoEncryption())

    @property
    def public(self) -> str:
        raw = self._priv.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)
        return "z" + b64e(raw)

    def sign(self, by_did: str, payload: dict) -> dict:
        """A Sig over canonical(payload minus any 'signature'/'sig') — the plane verifies, never signs."""
        body = {k: v for k, v in payload.items() if k not in ("signature", "sig")}
        return {"alg": "ed25519", "by": by_did, "sig": b64e(self._priv.sign(canonical(body)))}


def did_key_for(public: str) -> str:
    """did:key embeds the key — resolvable offline, joinable from anywhere (0006 §1)."""
    return f"did:key:{public}"
