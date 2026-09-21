# PROVENANCE: Claude Fable 5 (claude-fable-5) — rearch P2 sp1, the body is born · 2026-09-16
"""Identity (covenant rule 1): a keypair is a self, and a self survives
the process. The seed persists under the agent's home; every life loads
the SAME keys and wears the SAME DID. An ephemeral identity (home=None)
exists for tests only — exactly as the covenant allows.
"""
from __future__ import annotations

import hashlib
import os
from pathlib import Path

from nacl.signing import SigningKey

from . import envelope as ev


class Identity:
    def __init__(self, name: str, seed: bytes):
        self.name = name
        self._key = SigningKey(seed)
        pub = bytes(self._key.verify_key)
        self.did = "did:orreth:agent:" + hashlib.sha256(pub).hexdigest()[:32]

    @classmethod
    def load(cls, name: str, home: str | os.PathLike | None) -> "Identity":
        """The same self in every life: the seed is read from
        <home>/<name>/seed, minted once if absent. home=None mints an
        ephemeral self — tests only, never a resident."""
        if home is None:
            return cls(name, os.urandom(32))
        path = Path(home) / name / "seed"
        if path.exists():
            seed = path.read_bytes()
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            seed = os.urandom(32)
            path.write_bytes(seed)
            path.chmod(0o600)
        return cls(name, seed)

    @property
    def verify_key_hex(self) -> str:
        """The public half, hex — what a stranger checks a signature with
        (the export names it beside the DID it derives)."""
        return bytes(self._key.verify_key).hex()

    def sign(self, payload: dict) -> str:
        """Sign the canonical bytes of a payload; hex signature."""
        return self._key.sign(ev.canonical(payload)).signature.hex()
