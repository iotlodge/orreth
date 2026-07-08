# PROVENANCE: Fable 5 (claude-fable-5) — the join door, hardened · 2026-07-07
"""The join door (0006 · 0012, JB's lock 2026-07-07): HITL gate + nonce challenge.

Joining was a governed request in name only — becky leased any DID that asked. Now
the door has a desk: becky CHALLENGES the joiner to sign a nonce (key control is
proven, so roster names bind to real keys), stages the join for the HUMAN gate
(consequence waits, 0012), and mints the lease only after both. The five-status
protocol rides the existing queue — no new plumbing:

    pending → challenged → proved → staged → done | denied
      agent     becky      agent     becky    becky (after the human's approve)

The desk's nonce is the truth — a proof is verified against what becky ISSUED, never
against what the joiner echoes. An "approved" that arrives without a proven key
(forged, or the desk restarted) earns a fresh challenge, never a lease.
"""
from __future__ import annotations

import secrets

from . import crypto


class JoinDesk:
    """becky's desk at the door. `grant(did) -> token` is injected (the worker hands
    in the real lease mint); `tend(request)` returns (status, result) to resolve onto
    the queue, or None when there is nothing to do. Idempotent: it acts only when the
    queue's status and the desk's own phase disagree in a way that demands a move."""

    def __init__(self, grant, *, nonce=None):
        self.grant = grant
        self._nonce = nonce or (lambda: secrets.token_hex(16))
        self.desk: dict[str, dict] = {}      # request id → {nonce, did, proven}

    def _challenge(self, r: dict) -> tuple[str, dict]:
        nonce = self._nonce()
        self.desk[r["id"]] = {"nonce": nonce, "did": r.get("did", ""), "proven": False}
        return ("challenged",
                {"nonce": nonce,
                 "note": "sign this nonce with the key behind your DID — the door "
                         "answers proof, not claims"})

    def tend(self, r: dict):
        rid, status = r.get("id", ""), r.get("status")
        if not rid or r.get("kind") != "join":
            return None
        if status in ("done", "denied"):
            self.desk.pop(rid, None)
            return None
        did = str(r.get("did") or "")
        if not did.startswith("did:key:"):
            # only self-certifying DIDs can be challenged today; nothing else enters
            return ("denied", {"note": "join refused"}) if status == "pending" else None

        if status == "pending" and rid not in self.desk:
            return self._challenge(r)

        if status == "proved":
            entry = self.desk.get(rid)
            if entry is None or entry["proven"]:
                # a proof for a nonce this desk never issued (restart, or replay
                # after acceptance) — issue a fresh challenge; never verify blind
                return self._challenge(r) if entry is None else None
            proof = (r.get("result") or {}).get("proof") or {}
            public = crypto.public_from_did(did)
            ok = bool(public) and crypto.verify_sig(
                proof, {"join_nonce": entry["nonce"], "did": did}, public)
            if not ok:
                self.desk.pop(rid, None)
                return ("denied", {"note": "join refused"})
            entry["proven"] = True
            return ("staged",
                    {"note": "key proven — the human holds the door (0012)",
                     "did": did, "name": r.get("name", "")})

        if status == "approved":
            entry = self.desk.get(rid)
            if entry is None or not entry["proven"] or entry["did"] != did:
                # approval without a proven key mints NOTHING — challenge again
                return self._challenge(r)
            token = self.grant(did)
            self.desk.pop(rid, None)
            return ("done", {"token": token, "granted_by": "becky", "did": did})

        return None
