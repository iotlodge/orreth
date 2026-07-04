"""The Model Plane (0016): LiteLLM through the floors — the governed door to real minds.

The gateway is fractal: config cascades down (resolver), calls serve locally, model-misses
escalate up, usage rolls up (StatBundle.cost). Model classes (low/medium/high/xhigh) are
policy; skills pin classes, never models. Models carry a LIFECYCLE — candidate → canaried →
available → deprecated → sunset — and no call ever lands on a retired model (locked
2026-07-04). Dev default: Anthropic for heavy lifting + OpenAI cheap-smart; OpenRouter
plumbed, never default.
"""
from __future__ import annotations

from .agent_surface import BudgetExceeded
from .identity import NOW

# ---- the model registry: classes are policy, entries have a lifecycle -------------------
# (contract-ified as model-registry.schema.json once the shape survives real usage — 0016 §6)

LIFECYCLE = ("candidate", "canaried", "available", "deprecated", "sunset")

DEFAULT_REGISTRY = {
    # class -> ordered candidates (first available wins; later = fallback)
    "low": [
        {"model": "anthropic/claude-haiku-4-5-20251001", "state": "available"},
        {"model": "openai/gpt-4o-mini", "state": "available"},
    ],
    "medium": [
        {"model": "anthropic/claude-sonnet-4-6", "state": "available"},
        {"model": "openai/gpt-4o", "state": "available"},
    ],
    "high": [
        {"model": "anthropic/claude-opus-4-8", "state": "available"},
    ],
    "xhigh": [
        {"model": "anthropic/claude-fable-5", "state": "available"},
    ],
}


class ModelSunset(Exception):
    """Every candidate in the class is deprecated/sunset — re-route before this ever ships."""


class LiveGateway:
    """One tier's door to real models. Budgets ride the lease (0010); the ladder and
    registry arrive via resolved config; every call is metered for the roll-up."""

    def __init__(self, registry: dict | None = None, allowed_classes: list[str] | None = None):
        self.registry = registry or {k: [dict(e) for e in v] for k, v in DEFAULT_REGISTRY.items()}
        self.allowed = allowed_classes or list(self.registry)   # floors may narrow this
        self.call_log: list[dict] = []                          # vigil's tap + the meter
        self.parent: "LiveGateway | None" = None                # model-miss escalates up

    # ---- lifecycle (0016 §3): providers get polled; states flip; routing adapts --------
    def set_state(self, model: str, state: str) -> None:
        assert state in LIFECYCLE
        for entries in self.registry.values():
            for e in entries:
                if e["model"] == model:
                    e["state"] = state

    def resolve(self, klass: str) -> str:
        """First serviceable candidate in the class — deprecated is a loud last resort,
        sunset is never served. A full miss escalates to the parent gateway."""
        if klass not in self.allowed:
            raise BudgetExceeded(f"class '{klass}' is outside this tier's floors")
        entries = self.registry.get(klass, [])
        for e in entries:
            if e["state"] in ("available", "canaried"):
                return e["model"]
        for e in entries:
            if e["state"] == "deprecated":                      # serve, but scream
                self.call_log.append({"lifecycle_warning": e["model"], "at": NOW()})
                return e["model"]
        if self.parent is not None:
            return self.parent.resolve(klass)                   # the miss climbs
        raise ModelSunset(f"class '{klass}' has no living model at any tier")

    # ---- the call: budget-gated, class-resolved, fully metered --------------------------
    def call(self, surface, klass: str, messages: list[dict], *, pinned: bool = False,
             max_tokens: int = 300) -> dict:
        est = max_tokens + sum(len(m.get("content", "")) // 3 for m in messages)
        if est > surface.budget_left:
            if pinned:
                raise BudgetExceeded("pinned class unaffordable — never silently dumber")
            order = ["xhigh", "high", "medium", "low"]
            lower = [k for k in order[order.index(klass) + 1:] if k in self.allowed] \
                if klass in order else []
            if not lower:
                raise BudgetExceeded("budget exhausted at the floor class")
            return self.call(surface, lower[0], messages, max_tokens=max_tokens)

        model = self.resolve(klass)
        import litellm
        resp = litellm.completion(model=model, messages=messages, max_tokens=max_tokens)
        usage = resp.usage
        try:
            usd = litellm.completion_cost(completion_response=resp)
        except Exception:
            usd = 0.0
        tokens = usage.total_tokens
        surface.budget_left -= tokens
        meter = {
            "caller": surface.identity["did"], "class": klass, "model": model,
            "tokens": tokens, "prompt_tokens": usage.prompt_tokens,
            "completion_tokens": usage.completion_tokens, "usd": round(usd, 6),
            "at": NOW(),
        }
        self.call_log.append(meter)                             # rolls up via RunRecords (0005)
        return {"text": resp.choices[0].message.content, **meter}
