# PROVENANCE: Fable 5 (claude-fable-5) — the Shipyard (0009's provisioner, first wire landing) · 2026-07-07
"""The Shipyard: floors on demand — a universe that grows by conversation.

JB's ask (2026-07-07): "can you add it so it builds a true docker container of an
ecosystem?" This module is the shipyard's BRAIN — pure planning: names validated,
ports allocated, tier profiles generated from the same shapes the rig boots with.
The worker's dock crew executes the plan (docker, ledger, replant); consequence
waits for the human first (0012) — growing the universe is a consequential act.

A launched floor needs nothing else: it pulls its parent's floors at boot, beats
upward every 5s, and simply APPEARS in the orrery — the topology was always
assembled from heartbeats, so a new world is just a new heartbeat.
"""
from __future__ import annotations

import re

BASE_PORT = 4503                      # 4500-4502 belong to the composed rig
_SLUG = re.compile(r"^[a-z][a-z0-9-]{0,23}$")


def valid_name(name: str) -> bool:
    """Scope slugs stay lowercase-kebab — they travel in DIDs, DNS names, and paths."""
    return bool(_SLUG.match(name or ""))


def allocate_ports(count: int, used: set[int]) -> list[int]:
    out, p = [], BASE_PORT
    while len(out) < count:
        if p not in used:
            out.append(p)
        p += 1
    return out


def eco_profile(universe_scope: str, name: str, trust_root: str) -> dict:
    """An ecosystem's TierProfile — same dials as the composed demo-eco (0004)."""
    scope = f"{universe_scope}/e:{name}"
    return _profile(scope, "ecosystem", is_leaf=False, raw="P395D", horizon="P395D",
                    qa=0.001, trust_root=trust_root)


def field_profile(eco_scope: str, name: str, trust_root: str) -> dict:
    """A field's TierProfile — same dials as the composed demo-field (0004)."""
    scope = f"{eco_scope}/f:{name}"
    return _profile(scope, "field", is_leaf=True, raw="P90D", horizon="P90D",
                    qa=0.01, trust_root=trust_root)


def _profile(scope: str, label: str, *, is_leaf: bool, raw: str, horizon: str,
             qa: float, trust_root: str) -> dict:
    return {
        "tier_label": label, "scope": scope, "is_leaf": is_leaf,
        "clock": {"mode": "wall", "high_water_scope": scope},
        "objective": [{"objective": "reliability", "weight": 1.0}],
        "signal_capture": "state-changing",
        "memory": {"raw_retention": raw, "distilled_retention": "P395D",
                   "qa_sample_rate": qa},
        "retrieval": {"time_budget": {"time_ms": 500, "cost": 3}, "horizon": horizon},
        "steward": {"token_budget": {"tokens": 100000}, "cadence": "P1D",
                    "on_budget_exhaustion": "degrade-to-floors-and-flag"},
        "tokens": {"workforce_ttl": "P1D", "resident_ttl": "P30D"},
        "model_gateway": {"judge_sample_rate": 0.1, "routing": "litellm"},
        "join_default": "floors-only",
        "trust_root": {"mode": "did-web", "root": trust_root},
        "version": "0.1.0",
        "signature": {"alg": "ed25519", "by": trust_root, "sig": "ZGVtbw"},
    }


def plan(universe_scope: str, name: str, fields: list[str], used_ports: set[int],
         trust_root: str) -> dict:
    """The launch plan: one ecosystem hull + its field moons, ports and containers
    named, profiles generated — everything the dock crew needs, nothing executed."""
    if not valid_name(name):
        raise ValueError(f"'{name}' cannot sail — names are lowercase-kebab, ≤24 chars")
    for f in fields:
        if not valid_name(f):
            raise ValueError(f"field '{f}' cannot sail — names are lowercase-kebab")
    ports = allocate_ports(1 + len(fields), used_ports)
    eco = {
        "kind": "ecosystem", "name": name,
        "scope": f"{universe_scope}/e:{name}",
        "port": ports[0], "container": f"orreth-dyn-e-{name}",
        "parent_container": None,                    # the composed universe
        "profile": eco_profile(universe_scope, name, trust_root),
        "profile_file": f"dyn-e-{name}.json",
    }
    moons = [{
        "kind": "field", "name": f,
        "scope": f"{eco['scope']}/f:{f}",
        "port": p, "container": f"orreth-dyn-e-{name}-f-{f}",
        "parent_container": eco["container"],
        "profile": field_profile(eco["scope"], f, trust_root),
        "profile_file": f"dyn-e-{name}-f-{f}.json",
    } for f, p in zip(fields, ports[1:])]
    return {"eco": eco, "fields": moons,
            "summary": f"e:{name} on :{ports[0]}"
                       + (f" with field(s) {', '.join(f'{f}:{p}' for f, p in zip(fields, ports[1:]))}"
                          if fields else " — sailing alone (fields can join later)")}
