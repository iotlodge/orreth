"""FieldClient — an agent's whole relationship with its universe, over HTTP.

The lifeforce sequence (0000 · 0005 · 0006 · 0016):
  spawn (a keypair is a self)  →  join (a governed REQUEST; becky answers with a lease)
  →  remember / recall (signed memory, tokened retrieval)  →  think (the plane
  authorizes and meters; cognition executes)  →  diary (every cycle on the record).

Nothing here holds privilege: the plane verifies every byte, refuses uniformly, and
the Console renders whatever this client does within one breath of the tick.
"""
from __future__ import annotations

import json
import time
import urllib.request
from datetime import datetime, timezone
from urllib.error import HTTPError, URLError

from .crypto import KeyPair, b64e, canonical, content_hash, did_key_for

SIG_KEYS = ("id", "kind", "scope", "author", "occurred_at", "provenance_class")
RUN_SIG_KEYS = ("id", "agent", "scope", "goal_hash", "occurred_at")


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class JoinRefused(Exception):
    """The floor did not grant a lease (timeout, denial, or a dark daemon)."""


class FieldClient:
    """One agent, one floor. Point it at any orrethd URL — local, docker, or across the world."""

    def __init__(self, field_url: str, name: str, *, role: str = "workforce",
                 keypair: KeyPair | None = None, scribe: KeyPair | None = None):
        self.base = field_url.rstrip("/")
        self.kp = keypair or KeyPair()
        self.did = did_key_for(self.kp.public)
        # the diary's co-signer: RunRecords are authored by a scribe, never self-attested (0005)
        self.scribe = scribe or KeyPair()
        self.scribe_did = did_key_for(self.scribe.public)
        self.name, self.role = name, role
        self.token: dict | None = None
        self.scope: str | None = None

    # ---- wire ---------------------------------------------------------------------------
    def _call(self, method: str, path: str, payload: dict | None = None) -> tuple[int, dict]:
        req = urllib.request.Request(self.base + path, method=method,
                                     data=json.dumps(payload).encode() if payload is not None else None,
                                     headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=10) as r:
                raw = r.read()
                return r.status, (json.loads(raw) if raw[:1] in (b"{", b"[") else {})
        except HTTPError as e:
            raw = e.read() or b"{}"
            return e.code, (json.loads(raw) if raw[:1] in (b"{", b"[") else {})
        except URLError as e:
            raise ConnectionError(f"the floor at {self.base} is dark: {e.reason}") from e

    # ---- the lifeforce ------------------------------------------------------------------
    def health(self) -> dict:
        return self._call("GET", "/health")[1]

    def join(self, *, timeout: float = 60.0, poll: float = 1.0) -> dict:
        """Ask the floor for a lease. Joining is a REQUEST in the human-visible queue —
        becky (cognition) mints the token; in governed floors a human may hold the door."""
        self.scope = self.health().get("scope")
        status, req = self._call("POST", "/requests", {
            "kind": "join", "did": self.did, "name": self.name, "role": self.role,
            "text": f"{self.name} asks to join {self.scope} as {self.role}"})
        if status != 201:
            raise JoinRefused(f"the request queue refused ({status})")
        rid, deadline = req["id"], time.monotonic() + timeout
        while time.monotonic() < deadline:
            for r in self._call("GET", "/requests")[1].get("requests", []):
                if r.get("id") == rid:
                    if r.get("status") == "done" and isinstance(r.get("result"), dict):
                        self.token = r["result"]["token"]
                        self.remember({"joined": self.name, "role": self.role, "did": self.did},
                                      kind="episodic", tags=["birth"])
                        return self.token
                    if r.get("status") == "denied":
                        raise JoinRefused("becky declined the lease")
            time.sleep(poll)
        raise JoinRefused(f"no lease within {timeout}s — is a becky worker tending {self.base}?")

    def remember(self, body: dict, *, kind: str = "episodic", tags: list[str] | None = None,
                 occurred_at: str | None = None, provenance_class: str = "lived") -> str | None:
        rec = {
            "id": content_hash(body), "kind": kind, "scope": self.scope,
            "author": self.did, "occurred_at": occurred_at or now_iso(),
            "provenance_class": provenance_class,
            "body": b64e(canonical(body)), "retention": "active",
            "visibility": {"tenancy": "tenant-private", "mobility": "branch-bound"},
            "tags": tags or [],
        }
        rec["signature"] = self.kp.sign(self.did, {k: rec[k] for k in SIG_KEYS})
        status, out = self._call("POST", "/records", rec)
        return out.get("id") if status == 201 else None

    def recall(self, *, days: float = 90, budget: int = 4) -> dict:
        """My biography, through the governed window — escalates up the tree by itself."""
        from_iso = datetime.fromtimestamp(
            datetime.now(timezone.utc).timestamp() - days * 86400, tz=timezone.utc
        ).strftime("%Y-%m-%dT%H:%M:%SZ")
        status, out = self._call("POST", "/retrieve", {
            "query": {"requester": self.did, "subject": "self", "space": "self",
                      "time": {"from": from_iso}, "intent": "recall",
                      "budget": {"cost": budget}, "auth": "biscuit-sim"},
            "token": self.token, "requester_scope": self.scope})
        return out if status == 200 else {"hits": []}

    def body_of(self, ref: str) -> dict | None:
        status, out = self._call("GET", f"/records/{ref}/body")
        return out if status == 200 else None

    # ---- the governed mind (0016: the plane authorizes and meters; we execute) -----------
    def authorize(self, klass: str, est_tokens: int) -> dict | None:
        status, grant = self._call("POST", "/model/authorize",
                                   {"token": self.token, "class": klass, "est_tokens": est_tokens})
        return grant if status == 200 else None

    def meter(self, grant: dict, *, klass: str, tokens: int, usd: float = 0.0, model: str = "") -> None:
        self._call("POST", "/model/meter", {
            "subject": grant.get("subject", self.did), "est_tokens": grant.get("est_tokens", 0),
            "tokens": tokens, "usd": round(usd, 6), "model": model or grant.get("model", ""),
            "class": klass})

    # ---- the diary (0005: signed, scribe-authored, never self-attested) ------------------
    def diary(self, intent: str, *, cycle: int, done: bool, tokens: int = 0,
              model_calls: int = 0, score: float | None = None) -> None:
        run = {
            "id": content_hash({"i": intent, "c": cycle, "at": now_iso(), "a": self.did}),
            "agent": self.did, "scope": self.scope,
            "goal_hash": content_hash({"intent": intent}),
            "occurred_at": now_iso(), "outcome": "success" if done else "partial",
            "scores": [{"objective": "objective-met",
                        "score": score if score is not None else (1.0 if done else 0.0)}],
            "cost": {"tokens": max(tokens, 0), "model_calls": model_calls},
            "author": self.scribe_did,
        }
        run["sig"] = self.scribe.sign(self.scribe_did, {k: run[k] for k in RUN_SIG_KEYS})
        self._call("POST", "/runs", run)

    def park(self, intent: str, missing: str) -> str | None:
        """The breaker doesn't fail — the unsolved objective becomes fuel (0014)."""
        return self.remember({"parked_intent": intent, "missing": missing,
                              "handoff": "knowledge-acquisition"},
                             kind="semantic", tags=["parked", "knowledge-intent"])

    def ask_librarian(self, text: str) -> None:
        """File a gather request — the librarian answers with sourced, quarantined memory."""
        self._call("POST", "/requests", {"kind": "gather", "text": text})
