"""The AgentField & the Gateway (0010): the medium agents live in, the doors everything passes through.

Any-SDK workforce joins at the Gateway (0006 §2) and receives an AgentSurface — the ONLY
handle it ever holds. No agent calls a model ungoverned (0000 §2); the per-identity budget
rides the lease token; a skill's pinned tier is a floor (degrade-where-pins-allow, locked
2026-07-02); signals are transport unless they change state (locked 2026-07-02).
"""
from __future__ import annotations

from .identity import NOW
from .schemas import validate

TIER_LADDER = ["nano", "standard", "premium"]      # sim ladder; tiers are policy strings on the wire
_TIER_COST = {"nano": 1, "standard": 4, "premium": 20}


class BudgetExceeded(Exception):
    pass


class ModelGateway:
    """The layer's governed door to models. Every call is logged — caller, tiers, charge —
    which is exactly vigil's tap: shape and volume, never content (0013 §3)."""

    def __init__(self) -> None:
        self.call_log: list[dict] = []

    def call(self, surface: "AgentSurface", requested_tier: str, tokens: int,
             *, pinned: bool = False, skill_ref: dict | None = None) -> dict:
        req = {"caller": surface.identity["did"], "requested_tier": requested_tier,
               "tokens": tokens, "pinned": pinned,
               **({"skill_ref": skill_ref} if skill_ref else {})}
        validate(req, "agent-surface.schema.json#/$defs/ModelCall")
        tier, degraded = requested_tier, False
        while tokens * _TIER_COST[tier] > surface.budget_left:
            if pinned:
                # a pin is a floor: fail honestly, never run the skill silently dumber
                self.call_log.append({**req, "refused": "pinned tier unaffordable", "at": NOW()})
                raise BudgetExceeded("pinned tier unaffordable")
            i = TIER_LADDER.index(tier)
            if i == 0:
                self.call_log.append({**req, "refused": "budget exhausted", "at": NOW()})
                raise BudgetExceeded("budget exhausted at the floor tier")
            tier, degraded = TIER_LADDER[i - 1], True
        charged = tokens * _TIER_COST[tier]
        surface.budget_left -= charged
        result = {"served_tier": tier, "requested_tier": requested_tier,
                  "degraded": degraded, "charged": charged}
        validate(result, "agent-surface.schema.json#/$defs/ModelCallResult")
        self.call_log.append({**req, **result, "at": NOW()})
        return result


class AgentSurface:
    """The five verbs (0010 §3) — write, retrieve, standards, call_model, signal.
    GraphSpec compiles onto this; governance sees the surface, never the SDK."""

    def __init__(self, node, identity: dict, kp, lease: dict):
        self.node, self.identity, self.kp, self.lease = node, identity, kp, lease
        self.budget_left: int = lease["constraints"].get("budget", {}).get("tokens", 0)
        self.inbox: list[dict] = []

    def write(self, body: dict, **kw) -> str:
        from .node import make_memory
        return self.node.write(make_memory(self.identity, self.kp,
                                           self.identity["scope"], body, **kw))

    def retrieve(self, query: dict) -> dict:
        return self.node.retrieve(query, self.lease, self.identity["scope"])

    def standards(self) -> dict:
        return self.node.all_floors()

    def call_model(self, requested_tier: str = "standard", tokens: int = 100,
                   *, pinned: bool = False, skill_ref: dict | None = None) -> dict:
        return self.node.model_gateway.call(self, requested_tier, tokens,
                                            pinned=pinned, skill_ref=skill_ref)

    def signal(self, other: "AgentSurface", body: dict, *, state_changing: bool = False) -> str | None:
        """Transport always delivers; memory is a policy question (the signal_capture dial).
        'If it's not memory, it didn't happen' — a state-change MUST land to have happened."""
        sig = {"from": self.identity["did"], "to": other.identity["did"],
               "scope": self.identity["scope"],
               "payload_class": "state-changing" if state_changing else "chatter",
               "occurred_at": NOW(), "body": body}
        validate(sig, "agent-surface.schema.json#/$defs/Signal")
        other.inbox.append(body)
        self.node.signal_count += 1        # vigil's metadata: volume/shape, content-blind
        dial = self.node.profile.get("signal_capture", "state-changing")
        persist = dial == "full" or (dial == "state-changing" and state_changing)
        if persist:
            return self.write({"signal": body, "to": other.identity["did"]}, tags=["signal"])
        return None


def join_workforce(node, sponsor_becky, *, budget_tokens: int = 10_000) -> AgentSurface:
    """The workforce join flow (0006 §2): present at the Gateway, receive a leased identity,
    a budgeted capability token, and the surface — never raw access, never a key to the store."""
    ident, kp = sponsor_becky.issue_identity("instance", node.scope)
    lease = sponsor_becky.issue_token(
        ident["did"], node.scope,
        [{"action": "retrieve", "space": "self"}, {"action": "write", "space": "self"}],
        budget={"tokens": budget_tokens})
    return AgentSurface(node, ident, kp, lease)
