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

from . import continuity

BASE_PORT = 4503                      # 4500-4502 belong to the composed rig
_SLUG = re.compile(r"^[a-z][a-z0-9-]{0,23}$")
TEMPLATES = {continuity.TEMPLATE: continuity.overlay}   # 0009's named templates


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
         trust_root: str, template: str | None = None) -> dict:
    """The launch plan: one ecosystem hull + its field moons, ports and containers
    named, profiles generated — everything the dock crew needs, nothing executed.
    A named template (0009 · 0034) is RENDERED here: the overlay dresses every
    profile in the plan — the provisioner renders it, the floor is born wearing
    its law."""
    if not valid_name(name):
        raise ValueError(f"'{name}' cannot sail — names are lowercase-kebab, ≤24 chars")
    for f in fields:
        if not valid_name(f):
            raise ValueError(f"field '{f}' cannot sail — names are lowercase-kebab")
    if template is not None and template not in TEMPLATES:
        raise ValueError(f"no template named '{template}' — the yard knows: "
                         + ", ".join(sorted(TEMPLATES)))
    dress = TEMPLATES.get(template or "", lambda p: p)
    ports = allocate_ports(1 + len(fields), used_ports)
    eco = {
        "kind": "ecosystem", "name": name,
        "scope": f"{universe_scope}/e:{name}",
        "port": ports[0], "container": f"orreth-dyn-e-{name}",
        "parent_container": None,                    # the composed universe
        "profile": dress(eco_profile(universe_scope, name, trust_root)),
        "profile_file": f"dyn-e-{name}.json",
        **({"template": template} if template else {}),
    }
    moons = [{
        "kind": "field", "name": f,
        "scope": f"{eco['scope']}/f:{f}",
        "port": p, "container": f"orreth-dyn-e-{name}-f-{f}",
        "parent_container": eco["container"],
        "profile": dress(field_profile(eco["scope"], f, trust_root)),
        "profile_file": f"dyn-e-{name}-f-{f}.json",
        **({"template": template} if template else {}),
    } for f, p in zip(fields, ports[1:])]
    return {"eco": eco, "fields": moons,
            "summary": (f"a {template} " if template else "") + f"e:{name} on :{ports[0]}"
                       + (f" with field(s) {', '.join(f'{f}:{p}' for f, p in zip(fields, ports[1:]))}"
                          if fields else " — sailing alone (fields can join later)")}


def join_plan(universe_scope: str, name: str, fields: list[str],
              used_ports: set[int], trust_root: str, eco_port: int) -> dict:
    """The field-join door (0038 sp4 — JB's gate catch 2026-07-22: the yard
    only knew whole ecosystems, and "fields can join later" had no door; a
    second hull on a standing scope would be two truths). New moons for a
    STANDING eco: same shapes, same gate — nothing relaunched, nothing doubled."""
    if not valid_name(name):
        raise ValueError(f"'{name}' cannot sail — names are lowercase-kebab")
    for f in fields:
        if not valid_name(f):
            raise ValueError(f"field '{f}' cannot sail — names are lowercase-kebab")
    if not fields:
        raise ValueError("a join names at least one field")
    eco_scope = f"{universe_scope}/e:{name}"
    eco_container = f"orreth-dyn-e-{name}"
    ports = allocate_ports(len(fields), used_ports)
    moons = [{
        "kind": "field", "name": f,
        "scope": f"{eco_scope}/f:{f}",
        "port": p, "container": f"orreth-dyn-e-{name}-f-{f}",
        "parent_container": eco_container, "parent_port": eco_port,
        "profile": field_profile(eco_scope, f, trust_root),
        "profile_file": f"dyn-e-{name}-f-{f}.json",
    } for f, p in zip(fields, ports)]
    return {"eco": name, "eco_scope": eco_scope, "fields": moons,
            "summary": f"field(s) {', '.join(f'{f}:{p}' for f, p in zip(fields, ports))} "
                       f"join the STANDING e:{name} (:{eco_port}) — nothing doubled"}
