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

    # ---- the flight recorder's refusal taxonomy (0043 sp1): the gateway's own book -----
    def _refuse(self, surface, klass: str, taxon: str) -> None:
        """Recorded HERE, in the meter's book only — outside, refusal keeps its
        one face (rule 4): the exception that rides out is unchanged."""
        self.call_log.append({"refusal": taxon, "caller": surface.identity["did"],
                              "class": klass, "at": NOW()})

    # ---- the call: budget-gated, class-resolved, fully metered --------------------------
    def call(self, surface, klass: str, messages: list[dict], *, pinned: bool = False,
             max_tokens: int = 300) -> dict:
        est = max_tokens + sum(len(m.get("content", "")) // 3 for m in messages)
        if est > surface.budget_left:
            if pinned:
                self._refuse(surface, klass, "pinned-unaffordable")
                raise BudgetExceeded("pinned class unaffordable — never silently dumber")
            order = ["xhigh", "high", "medium", "low"]
            lower = [k for k in order[order.index(klass) + 1:] if k in self.allowed] \
                if klass in order else []
            if not lower:
                self._refuse(surface, klass, "budget-exhausted")
                raise BudgetExceeded("budget exhausted at the floor class")
            return self.call(surface, lower[0], messages, max_tokens=max_tokens)

        try:
            model = self.resolve(klass)
        except BudgetExceeded:
            self._refuse(surface, klass, "class-outside-floors")
            raise
        except ModelSunset:
            self._refuse(surface, klass, "model-sunset")
            raise
        import time

        import litellm
        t0 = time.perf_counter()
        resp = litellm.completion(model=model, messages=messages, max_tokens=max_tokens)
        ms = int((time.perf_counter() - t0) * 1000)
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
            "ms": ms,                                       # the flight recorder (0043 sp1)
            "at": NOW(),
        }
        self.call_log.append(meter)                             # rolls up via RunRecords (0005)
        return {"text": resp.choices[0].message.content, **meter}


class PlaneClient:
    """Cognition's side of the split (0016 §6): the plane authorizes and meters;
    we execute. Budgets live in the daemon's ledger now — not in our honor."""

    def __init__(self, base: str, token: dict):
        self.base, self.token = base, token

    def _post(self, path: str, payload: dict) -> tuple[int, dict]:
        import json as _json
        import urllib.request
        from urllib.error import HTTPError
        req = urllib.request.Request(self.base + path, method="POST",
                                     data=_json.dumps(payload).encode(),
                                     headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req) as r:
                return r.status, _json.loads(r.read())
        except HTTPError as e:
            return e.code, _json.loads(e.read() or b"{}")

    def call(self, klass: str, messages: list[dict], *, max_tokens: int = 300) -> dict:
        est = max_tokens + sum(len(m.get("content", "")) // 3 for m in messages)
        status, grant = self._post("/model/authorize",
                                   {"token": self.token, "class": klass, "est_tokens": est})
        if status != 200:
            raise BudgetExceeded(grant.get("error", f"authorize refused ({status})"))
        import litellm
        resp = litellm.completion(model=grant["model"], messages=messages,
                                  max_tokens=max_tokens)
        tokens = resp.usage.total_tokens
        try:
            usd = litellm.completion_cost(completion_response=resp)
        except Exception:
            usd = 0.0
        _, meter = self._post("/model/meter", {
            "subject": grant["subject"], "est_tokens": est, "tokens": tokens,
            "usd": round(usd, 6), "model": grant["model"], "class": klass})
        return {"text": resp.choices[0].message.content, "model": grant["model"],
                "class": klass, "tokens": tokens, "usd": round(usd, 6),
                "remaining": meter.get("remaining")}
