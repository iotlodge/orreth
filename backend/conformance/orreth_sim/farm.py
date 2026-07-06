# PROVENANCE: Fable 5 (claude-fable-5) — 0018, the Tool Farm · 2026-07-05
"""The Tool Farm (0018): services are identities with worldlines.

A tool/MCP is a service consumed by an agent. Every service holds a DID, a hash-pinned
manifest (the anti-rug-pull pin, CVE-2025-54136's lesson), and a lifecycle — the trust
ladder's fourth application: proposed → probation → serving ⇄ dropped, quarantined on any
manifest change, decommissioned with its data's lineage walked (0014 §4).

Drop/rejoin is the SPIFFE lesson: a lease that expires, not a certificate to revoke.
Nothing self-attests — the keeper observes and signs (0005's rule, third application):
every transition lands in `events`, the raw material of the service's worldline.
"""
from __future__ import annotations

from . import crypto
from .identity import NOW

STATES = ("proposed", "probation", "serving", "dropped", "quarantined", "decommissioned")

# every legal move, and no other — the state machine IS the governance card (0018 §2)
LEGAL: dict[str, set[str]] = {
    "proposed": {"probation", "decommissioned"},            # approved+attested · or denied
    "probation": {"serving", "dropped", "quarantined", "decommissioned"},
    "serving": {"dropped", "quarantined", "decommissioned"},
    "dropped": {"serving", "quarantined", "decommissioned"},  # rejoin: same self · new claim
    "quarantined": {"probation", "decommissioned"},         # only a human re-opens the gate
    "decommissioned": set(),                                # terminal — history remains
}

PROBATION_BEATS = 3  # heartbeats a rookie service must earn before it serves


class IllegalTransition(Exception):
    pass


def manifest_hash(manifest) -> str:
    """The pin: sha256 over CANONICAL manifest bytes (0000 §3) — content, never name."""
    return crypto.content_hash(manifest)


class Farm:
    """One floor's toolshed: registry + lifecycle + meter. The keeper drives the WHEN;
    this class refuses illegal WHATs — plane-shaped logic, cognition-shaped policy."""

    def __init__(self, scope: str) -> None:
        self.scope = scope
        self.services: dict[str, dict] = {}
        self.meter_log: list[dict] = []
        self.events: list[dict] = []          # the worldline's raw material

    # ---- planting: a governed request, exactly like joining (0006 §2) ------------------
    def plant(self, name: str, *, did: str, kind: str, endpoint: str,
              transport: str = "rest", manifest: list | None = None) -> dict:
        if name in self.services and self.services[name]["state"] != "decommissioned":
            raise IllegalTransition(f"{name} already lives on this farm")
        svc = {
            "name": name, "did": did, "kind": kind, "endpoint": endpoint,
            "transport": transport, "manifest": manifest or [],
            "manifest_hash": manifest_hash(manifest or []),
            "state": "proposed", "floor": self.scope,
            "planted_at": NOW(), "last_seen": None, "beats": 0, "calls": 0,
        }
        self.services[name] = svc
        self._event(name, "planted", did=did, endpoint=endpoint)
        return svc

    # ---- the guarded move: every transition legal, every transition an event -----------
    def _transition(self, name: str, to: str, event: str, **extra) -> dict:
        svc = self.services[name]
        if to not in LEGAL[svc["state"]]:
            raise IllegalTransition(f"{svc['state']} → {to} is not a move this farm knows")
        svc["state"] = to
        self._event(name, event, state=to, **extra)
        return svc

    def _event(self, name: str, event: str, **extra) -> None:
        svc = self.services[name]
        self.events.append({"at": NOW(), "service": name, "did": svc["did"],
                            "event": event, "state": svc["state"],
                            "manifest_hash": svc["manifest_hash"], **extra})

    # ---- attestation: the human approved; the keeper pins what it SAW ------------------
    def attest(self, name: str, manifest: list) -> dict:
        svc = self.services[name]
        svc["manifest"] = manifest
        svc["manifest_hash"] = manifest_hash(manifest)
        svc["beats"] = 0
        return self._transition(name, "probation", "attested",
                                tools=len(manifest))

    # ---- the lease: beats earn probation's exit; silence ages the lease out ------------
    def beat(self, name: str) -> dict:
        svc = self.services[name]
        svc["last_seen"] = NOW()
        svc["beats"] += 1
        if svc["state"] == "probation" and svc["beats"] >= PROBATION_BEATS:
            return self._transition(name, "serving", "serving",
                                    earned_after=svc["beats"])
        return svc

    def expire(self, name: str, reason: str = "missed heartbeats") -> dict:
        svc = self.services[name]
        svc["beats"] = 0
        return self._transition(name, "dropped", "dropped", reason=reason)

    # ---- rejoin: same hash, same self · changed hash, a NEW claim (the rug-pull door) --
    def rejoin(self, name: str, manifest: list) -> dict:
        svc = self.services[name]
        seen = manifest_hash(manifest)
        if seen == svc["manifest_hash"]:
            svc["beats"] = 0
            return self._transition(name, "serving", "rejoined")
        svc["proposed_manifest"] = manifest
        svc["proposed_hash"] = seen
        return self._transition(name, "quarantined", "manifest-changed",
                                pinned=svc["manifest_hash"], seen=seen)

    def reapprove(self, name: str) -> dict:
        """A human accepted the NEW manifest — re-pin and re-earn from probation."""
        svc = self.services[name]
        if "proposed_manifest" in svc:
            svc["manifest"] = svc.pop("proposed_manifest")
            svc["manifest_hash"] = svc.pop("proposed_hash")
        svc["beats"] = 0
        return self._transition(name, "probation", "re-attested")

    # ---- decom: staged, human-decided; discredit hands 0014 §4 the recall --------------
    def decommission(self, name: str, *, reason: str = "", discredit: bool = False) -> dict:
        return self._transition(name, "decommissioned", "decommissioned",
                                reason=reason, discredit=discredit)

    # ---- the meter: volume and shape, never payloads (0016 §6) -------------------------
    def meter(self, name: str, caller: str, *, ms: int = 0) -> None:
        svc = self.services[name]
        if svc["state"] != "serving":
            raise IllegalTransition("only a serving service is consumed")
        svc["calls"] += 1
        self.meter_log.append({"at": NOW(), "service": name, "caller": caller, "ms": ms})

    def usage(self) -> list[dict]:
        return [{"service": s["name"], "state": s["state"], "calls": s["calls"],
                 "last_seen": s["last_seen"]} for s in self.services.values()]
