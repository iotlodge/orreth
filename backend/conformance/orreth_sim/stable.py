# PROVENANCE: Fable 5 (claude-fable-5) — 0019, the Stable · 2026-07-06
"""The Stable (0019): minds are identities with worldlines.

A model is a service an agent thinks through. Every stall holds a vendor DID, a
hash-pinned manifest over the DEAL (pricing, context, modalities — not just the name),
and the 0016 lifecycle: candidate → canaried → available → deprecated → sunset.

The pin makes price drift a rug-pull event (0018's door, applied to minds): changed
manifest bytes at sync stop new service until a human re-approves the new deal. EOL is
an appointment, not an incident: an announced expiry flips the stall deprecated (loud)
and the wrangler stages a recommendation. Sunset is never served — structurally.

Nothing self-attests — ada observes and signs; every transition lands in `events`,
the raw material of the stall's worldline.
"""
from __future__ import annotations

from . import crypto
from .identity import NOW

STATES = ("candidate", "canaried", "available", "deprecated", "sunset")

# every legal move, and no other — the state machine IS the governance card (0016 §3)
LEGAL: dict[str, set[str]] = {
    "candidate": {"canaried", "sunset"},              # approved → canary · denied → history
    "canaried": {"available", "deprecated", "sunset"},
    "available": {"deprecated", "sunset"},            # drift/EOL speak loudly · staged retire
    "deprecated": {"available", "sunset"},            # human re-approves the new deal · or lets it set
    "sunset": set(),                                  # terminal — never served, always remembered
}

CANARY_BEATS = 3      # verified syncs / governed calls a rookie mind earns before it serves
EOL_HORIZON_DAYS = 30  # inside this window an expiry burns on the pasture calendar


class IllegalTransition(Exception):
    pass


def manifest_hash(manifest) -> str:
    """The pin: sha256 over CANONICAL manifest bytes (0000 §3) — the deal, not the name."""
    return crypto.content_hash(manifest)


class Stable:
    """One floor's stable: stalls + lifecycle + drift/EOL detection. The wrangler drives
    the WHEN; this class refuses illegal WHATs — plane-shaped logic, cognition-shaped policy."""

    def __init__(self, scope: str) -> None:
        self.scope = scope
        self.stalls: dict[str, dict] = {}
        self.events: list[dict] = []          # the worldline's raw material

    # ---- saddling: a governed request, exactly like planting (0018 §2) -----------------
    def saddle(self, mid: str, *, provider: str, route: str, did: str, klass: str,
               manifest: dict | None = None, expires_at: str | None = None) -> dict:
        if mid in self.stalls and self.stalls[mid]["state"] != "sunset":
            raise IllegalTransition(f"{mid} already stands in this stable")
        stall = {
            "id": mid, "provider": provider, "route": route, "did": did, "class": klass,
            "manifest": manifest or {}, "manifest_hash": manifest_hash(manifest or {}),
            "state": "candidate", "expires_at": expires_at,
            "saddled_at": NOW(), "last_synced": None, "canary_beats": 0,
        }
        self.stalls[mid] = stall
        self._event(mid, "saddled")
        return stall

    def _move(self, mid: str, to: str, event: str, **extra) -> dict:
        stall = self.stalls.get(mid)
        if stall is None:
            raise IllegalTransition(f"no stall named {mid}")
        if to not in LEGAL[stall["state"]]:
            raise IllegalTransition(f"{mid}: {stall['state']} → {to} is not a legal move")
        stall["state"] = to
        self._event(mid, event, **extra)
        return stall

    def _event(self, mid: str, event: str, **extra) -> None:
        self.events.append({"id": mid, "event": event, "at": NOW(),
                            "state": self.stalls[mid]["state"], **extra})

    # ---- the gate: human approval attests; canary earns service ------------------------
    def attest(self, mid: str, manifest: dict, expires_at: str | None = None) -> dict:
        """Human approved the saddle: pin the deal as verified, enter canary."""
        stall = self._move(mid, "canaried", "attested", pinned=manifest_hash(manifest))
        stall["manifest"] = manifest
        stall["manifest_hash"] = manifest_hash(manifest)
        stall["expires_at"] = expires_at
        stall["last_synced"] = NOW()
        return stall

    def canary_beat(self, mid: str) -> dict:
        """One verified sync or governed call. Enough beats earn `available` (0016 §3)."""
        stall = self.stalls.get(mid)
        if stall is None or stall["state"] != "canaried":
            raise IllegalTransition(f"{mid} is not on canary")
        stall["canary_beats"] += 1
        if stall["canary_beats"] >= CANARY_BEATS:
            self._move(mid, "available", "available", earned_after=stall["canary_beats"])
        return stall

    # ---- the sync: the pin compared against the market — drift walks the rug-pull door -
    def sync(self, mid: str, manifest: dict, expires_at: str | None = None) -> dict:
        """The wrangler's catalog pass. Same bytes → freshness; changed bytes → the deal
        moved, service pauses (deprecated, loudly) until a human re-approves the new pin."""
        stall = self.stalls.get(mid)
        if stall is None:
            raise IllegalTransition(f"no stall named {mid}")
        stall["last_synced"] = NOW()
        new_hash = manifest_hash(manifest)
        if expires_at and expires_at != stall.get("expires_at"):
            stall["expires_at"] = expires_at
            self._event(mid, "expiry-announced", expires_at=expires_at)
        if new_hash == stall["manifest_hash"]:
            return {"drift": False, "stall": stall}
        stall["proposed_manifest"] = manifest
        stall["proposed_hash"] = new_hash
        if stall["state"] in ("canaried", "available"):
            self._move(mid, "deprecated", "manifest-drift",
                       pinned=stall["manifest_hash"], seen=new_hash)
        return {"drift": True, "stall": stall}

    def reapprove(self, mid: str) -> dict:
        """Human accepted the new deal: the proposed bytes become the pin."""
        stall = self.stalls.get(mid)
        if stall is None or "proposed_hash" not in stall:
            raise IllegalTransition(f"{mid} has no drifted deal awaiting approval")
        stall["manifest"] = stall.pop("proposed_manifest")
        stall["manifest_hash"] = stall.pop("proposed_hash")
        return self._move(mid, "available", "re-approved", pinned=stall["manifest_hash"])

    # ---- the pasture calendar: expiry is an appointment, never an incident -------------
    def eol_scan(self, today: str, horizon_days: int = EOL_HORIZON_DAYS) -> list[dict]:
        """Flip every serving stall whose announced expiry falls inside the horizon to
        deprecated (loud) — ISO dates compare lexically, no calendar math needed here."""
        from datetime import date, timedelta
        edge = (date.fromisoformat(today[:10]) + timedelta(days=horizon_days)).isoformat()
        flipped = []
        for stall in self.stalls.values():
            exp = stall.get("expires_at")
            if exp and exp[:10] <= edge and stall["state"] in ("canaried", "available"):
                self._move(stall["id"], "deprecated", "expiring", expires_at=exp)
                flipped.append(stall)
        return flipped

    def retire(self, mid: str, reason: str = "retired") -> dict:
        """Staged decom (0012) or the expiry arriving: the stall sets, history remains."""
        return self._move(mid, "sunset", reason)

    # ---- routing view: who serves a class right now (0016 resolve, mirrored) -----------
    def resolve(self, klass: str) -> dict | None:
        stalls = [s for s in self.stalls.values() if s["class"] == klass]
        for s in stalls:
            if s["state"] in ("available", "canaried"):
                return {"id": s["id"], "deprecated": False}
        for s in stalls:
            if s["state"] == "deprecated":
                return {"id": s["id"], "deprecated": True}  # loud last resort — never sunset
        return None

    # ---- the recommendation: same class → nearest price → newest (0019 §7 call 4) ------
    def recommend(self, mid: str, catalog: list[dict]) -> dict | None:
        """Pick the failing stall's replacement. Serving same-class stalls win outright;
        else the catalog ranks by price distance, then recency. Explainable on purpose."""
        old = self.stalls.get(mid)
        if old is None:
            return None
        for s in self.stalls.values():
            if s["id"] != mid and s["class"] == old["class"] and s["state"] == "available":
                return {"id": s["id"], "why": "already serving this class", "in_stable": True}
        old_price = float(old["manifest"].get("pricing", {}).get("prompt", 0) or 0)
        live = [c for c in catalog if c["id"] != mid and not c.get("expires_at")]
        if not live:
            return None
        best = min(live, key=lambda c: (
            abs(float(c.get("pricing", {}).get("prompt", 0) or 0) - old_price),
            -(c.get("created") or 0)))
        return {"id": best["id"], "why": "nearest price, newest catalog entry",
                "in_stable": False, "pricing": best.get("pricing", {})}
