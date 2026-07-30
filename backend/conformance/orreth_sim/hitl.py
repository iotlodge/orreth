"""HITL mechanics (0012): gates, queues, and the co-sign — consequence waits for humans.

Staging is free (vigil, stewards, gateways, humans); deciding is gated. Bars are ABSOLUTE:
fewer entitled humans than the rule requires makes the action structurally unavailable —
no clamping, no bootstrap exception (locked 2026-07-02). Silence never approves: expiry
is denial and a vigil signal (locked 2026-07-02). Everything here is wall-clock (0004).
"""
from __future__ import annotations

from datetime import datetime, timedelta

from . import crypto
from .identity import AuthzError
from .node import dur_days
from .schemas import validate


class GateViolation(Exception):
    """A child gate tried to LOOSEN an inherited rule — gates cascade tighten-only, like floors."""


class QuorumUnavailable(Exception):
    """Bars are absolute: the org has fewer entitled humans than the rule requires."""


def _ts(iso: str) -> datetime:
    return datetime.fromisoformat(iso.replace("Z", "+00:00"))


def _plus_days(iso: str, days: float) -> str:
    return (_ts(iso) + timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ")


def cascade_gate(parent: dict[str, dict], child: dict[str, dict]) -> dict[str, dict]:
    """Merge a child's gate policy under a parent's: co_signs may rise, cooling_off may
    lengthen, ttl may shorten — never the reverse. Co-sign bars are floors."""
    merged = {k: dict(v) for k, v in parent.items()}
    for cls, rule in child.items():
        inh = merged.get(cls)
        if inh:
            if rule["co_signs"] < inh["co_signs"]:
                raise GateViolation(f"{cls}: co_signs may only rise")
            if dur_days(rule.get("cooling_off", "P0D")) < dur_days(inh.get("cooling_off", "P0D")):
                raise GateViolation(f"{cls}: cooling_off may only lengthen")
            if dur_days(rule["ttl"]) > dur_days(inh["ttl"]):
                raise GateViolation(f"{cls}: ttl may only shorten")
        merged[cls] = dict(rule)
    return merged


class EscalationQueue:
    """One per tier. Escalations validate against contracts/v0 at every transition;
    every stage, approval, rejection, and expiry is on the record — the watchers watched."""

    def __init__(self, gate_policy: dict[str, dict], entitled: set[str], nanda):
        self.policy, self.entitled, self.nanda = gate_policy, entitled, nanda
        self.items: dict[str, dict] = {}
        self.expired_signals = 0            # vigil's tap: an unattended queue is a finding
        self.decisions: list[dict] = []     # 0043 sp1: the queue's own book — a rejection's
        #   clock lives here because the escalation contract holds no decided stamp;
        #   the Observatory reads it as an instrument reading, never as testimony

    def stage(self, action_class: str, action: dict, *, scope: str, staged_by: str,
              staged_by_kp, evidence: list[str] | None = None, now: str) -> dict:
        rule = self.policy[action_class]
        alive = {d for d in self.entitled if self.nanda.active(d)}
        if rule["co_signs"] > len(alive):
            # locked 2026-07-02: no single employee is a god — from day one, structurally
            raise QuorumUnavailable(
                f"{action_class} needs {rule['co_signs']} entitled humans; {len(alive)} exist")
        esc = {
            "id": crypto.content_hash({"c": action_class, "a": action, "at": now}),
            "action_class": action_class,
            "action": action,
            "scope": scope,
            "staged_by": staged_by,
            "evidence": evidence or [],
            "required": rule,
            "staged_at": now,
            "expires_at": _plus_days(now, dur_days(rule["ttl"])),
            "state": "pending",
            "approvals": [],
        }
        esc["sig"] = staged_by_kp.sign(staged_by, {k: esc[k] for k in
                                                   ("id", "action_class", "scope", "staged_at")})
        validate(esc, "escalation.schema.json")
        self.items[esc["id"]] = esc
        return esc

    def approve(self, esc_id: str, human_did: str, kp, *, now: str) -> dict:
        esc = self.items[esc_id]
        self._sweep_one(esc, now)
        if esc["state"] != "pending":
            raise AuthzError(f"cannot approve an escalation in state '{esc['state']}'")
        if human_did not in self.entitled or not self.nanda.active(human_did):
            raise AuthzError("approver is not a control-entitled, active human principal")
        if any(a["by"] == human_did for a in esc["approvals"]):
            raise AuthzError("distinct principals only — no DID signs twice")
        appr = {"by": human_did, "at": now}
        appr["sig"] = kp.sign(human_did, {"esc": esc_id, "at": now})
        esc["approvals"].append(appr)
        if len(esc["approvals"]) >= esc["required"]["co_signs"]:
            esc["state"], esc["approved_at"] = "approved", now
        validate(esc, "escalation.schema.json")
        return esc

    def execute(self, esc_id: str, *, now: str) -> dict:
        esc = self.items[esc_id]
        self._sweep_one(esc, now)
        if esc["state"] != "approved":
            raise AuthzError(f"execute refused: state is '{esc['state']}', quorum is not a formality")
        hold = dur_days(esc["required"].get("cooling_off", "P0D"))
        if _ts(now) < _ts(esc["approved_at"]) + timedelta(days=hold):
            raise AuthzError("cooling-off holds — the abort window is the point")
        esc["state"] = "executed"
        return esc

    def reject(self, esc_id: str, human_did: str, *, now: str) -> dict:
        """Any entitled human can kill a pending OR approved-and-cooling escalation —
        the cooling-off window exists precisely so this remains possible."""
        esc = self.items[esc_id]
        if human_did not in self.entitled:
            raise AuthzError("only entitled principals reject")
        if esc["state"] not in ("pending", "approved"):
            raise AuthzError(f"cannot reject state '{esc['state']}'")
        esc["state"] = "rejected"
        self.decisions.append({"id": esc_id, "outcome": "rejected", "at": now})
        return esc

    def _sweep_one(self, esc: dict, now: str) -> None:
        if esc["state"] == "pending" and now > esc["expires_at"]:
            esc["state"] = "expired"        # default-deny: silence never approves
            self.expired_signals += 1       # and the silence itself is a signal
