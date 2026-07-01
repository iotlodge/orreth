"""becky, simulated — the IAM agent (never a human).

did:web roots + did:key leaves (locked 2026-07-01). Delegation is attenuation-only;
revoking an ancestor kills the subtree (the structural kill-switch, 0006 §4).
"""
from __future__ import annotations

import json
from datetime import datetime, timezone

from . import crypto
from .schemas import validate

NOW = lambda: datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def is_within(scope: str, ancestor: str) -> bool:
    """True if `scope` is at-or-below `ancestor` in the tree."""
    return scope == ancestor or scope.startswith(ancestor + "/")


def tenant_of(scope: str) -> str:
    """The tenancy wall: the first two segments (universe/ecosystem). Siblings never read raw."""
    return "/".join(scope.split("/")[:2])


class AuthzError(Exception):
    pass


class Nanda:
    """The NANDA index sim: DID -> public key + status. Revocation cascades structurally."""

    def __init__(self) -> None:
        self._e: dict[str, dict] = {}

    def register(self, did: str, public: str) -> None:
        self._e[did] = {"public": public, "status": "active"}

    def revoke(self, did: str) -> None:
        self._e[did]["status"] = "revoked"

    def active(self, did: str) -> bool:
        return self._e.get(did, {}).get("status") == "active"

    def public(self, did: str) -> str:
        embedded = crypto.public_from_did(did)
        return embedded or self._e[did]["public"]


class Becky:
    """One issuer, root -> leaf. Each layer's becky is a delegate of its parent's."""

    def __init__(self, scope: str, nanda: Nanda, parent: "Becky | None" = None,
                 universe_name: str | None = None):
        self.scope, self.nanda, self.parent = scope, nanda, parent
        self.kp = crypto.KeyPair()
        if parent is None:
            # universe root: did:web anchored at orreth.ai (key via index — did:web can't embed)
            self.did = f"did:web:orreth.ai:u:{universe_name}"
        else:
            self.did = crypto.did_key_for(self.kp.public)
            if not is_within(scope, parent.scope):
                raise AuthzError("delegate scope must be within parent scope")
        nanda.register(self.did, self.kp.public)
        # delegation certificate chain, root -> here
        if parent is None:
            self.chain: list[dict] = []
        else:
            cert = {"issuer": parent.did, "subject": self.did, "scope": scope, "at": NOW()}
            cert["sig"] = parent.kp.sign(parent.did, cert)
            self.chain = parent.chain + [cert]

    # ---- identities -------------------------------------------------------
    def issue_identity(self, role: str, scope: str, *, resident: bool = False,
                       lineage: str | None = None) -> tuple[dict, crypto.KeyPair]:
        if not is_within(scope, self.scope):
            raise AuthzError("becky cannot issue outside its own scope")
        kp = crypto.KeyPair()
        ident = {
            "did": crypto.did_key_for(kp.public),
            "lineage": lineage,
            "role": role,
            "scope": scope,
            "keys": {"signing": kp.public},
            "status": "online",
            "resident": resident,
            "born_at": NOW(),
        }
        validate(ident, "identity.schema.json")
        self.nanda.register(ident["did"], kp.public)
        return ident, kp

    # ---- capability tokens (attenuation-only) -----------------------------
    def issue_token(self, subject: str, audience: str, grants: list[dict], *,
                    direction: str = "within", expiry: str = "2027-01-01T00:00:00Z",
                    budget: dict | None = None) -> dict:
        if not is_within(audience, self.scope):
            raise AuthzError("token audience exceeds issuer authority — no amplification exists")
        constraints: dict = {"expiry": expiry, "direction": direction}
        if budget:
            constraints["budget"] = budget
        hop = {"issuer": self.did, "subject": subject, "audience": audience,
               "grants": grants, "constraints": constraints}
        hop["sig"] = self.kp.sign(self.did, hop)
        token = {
            "subject": subject,
            "audience": audience,
            "grants": grants,
            "constraints": constraints,
            "chain": [json.dumps(c, sort_keys=True) for c in self.chain + [hop]],
            "sig": self.kp.sign(self.did, {"subject": subject, "audience": audience,
                                           "grants": grants, "constraints": constraints}),
        }
        return validate(token, "capability-token.schema.json")

    def verify_token(self, token: dict) -> None:
        """Every hop signed, every issuer alive, subject alive, not expired.
        Ancestor revocation anywhere in the chain kills the token."""
        if token["constraints"]["expiry"] < NOW():
            raise AuthzError("expired")
        if not self.nanda.active(token["subject"]):
            raise AuthzError("subject revoked")
        for raw in token["chain"]:
            cert = json.loads(raw)
            issuer = cert["issuer"]
            if not self.nanda.active(issuer):
                raise AuthzError("issuer revoked (ancestor kill-switch)")
            if not crypto.verify_sig(cert["sig"], cert, self.nanda.public(issuer)):
                raise AuthzError("bad delegation signature")
        # the final hop must bind this token's content
        last = json.loads(token["chain"][-1])
        if last.get("audience") != token["audience"] or last.get("subject") != token["subject"]:
            raise AuthzError("chain does not bind token")
