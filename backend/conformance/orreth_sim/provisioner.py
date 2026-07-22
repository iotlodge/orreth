"""The provisioner (0009): a template rendered into a running universe.

Build My First Universe, mechanically: complete the profile fragments, stand up the
tiers (a layer is born with its staff), publish the floors, seed the tone, stamp the
roster — and gate the door by trust tier (0013 §8; a template above your tier refuses).
Anonymous renders clamp quotas and budgets to the platform caps: the safety architecture
IS the free-tier economics. Out of fuel ⇒ hibernate, never delete (locked 2026-07-02).
"""
from __future__ import annotations

from dataclasses import dataclass, field as dc_field

from . import factory
from .agent_surface import AgentSurface
from .identity import Becky, Nanda
from .node import HarnessNode
from .schemas import validate

TRUST_ORDER = {"anonymous": 0, "verified": 1, "regulated": 2}
ANON_CAPS = {"stamp_quota": 12, "budget_tokens": 2000}   # 0013 §8 hard scale caps, mechanical

# The wild-vs-REAL dial members (locked 2026-07-02: rigor, never safety)
_TONE_DIALS = {"wild": {"signal_capture": "none", "judge_sample_rate": 0.05},
               "REAL": {"signal_capture": "full", "judge_sample_rate": 0.25}}

# Platform floors: IDENTICAL at both ends of the dial — the spectrum never touches safety (0013 §2)
PLATFORM_FLOORS = [
    {"match": {"tags": ["real-world-identity"]}, "action": "keep-raw", "keep_for": "promote",
     "reason": "no targeting of non-consenting real people — platform floor, tone-independent"},
    {"match": {"outcome": "floor-breach"}, "action": "keep-raw", "keep_for": "promote",
     "reason": "floor-breach evidence always survives — platform floor, tone-independent"},
]


class TrustTierError(Exception):
    """The 0013 §8 door: this template requires a higher trust tier than the requester holds."""


@dataclass
class ProvisionedUniverse:
    name: str
    nanda: Nanda
    becky: Becky
    universe: HarnessNode
    fields: dict[str, HarnessNode]
    surfaces: dict[str, list[AgentSurface]]      # field name -> stamped roster
    fuel_tokens: int
    hibernated: bool = False
    beckys: dict = dc_field(default_factory=dict)

    def hibernate(self) -> None:
        """Out of fuel or idle: agents pause, nothing dies. The window stays watchable —
        'your universe never dies; it dreams only when fueled.'"""
        self.hibernated = True
        for roster in self.surfaces.values():
            for s in roster:
                s.budget_left = 0                # every model call now refuses (0010)


def _profile(template: dict, tier_key: str, label: str, scope: str, *, leaf: bool,
             parent: str | None, root_did: str, trust_tier: str) -> dict:
    dials = dict(template["profile_dials"].get(tier_key, {}))
    tone = _TONE_DIALS[template["tone"]]
    quota = dials.pop("stamp_quota", None)
    if trust_tier == "anonymous" and leaf:
        quota = min(quota or ANON_CAPS["stamp_quota"], ANON_CAPS["stamp_quota"])
    p = {
        "tier_label": label,
        "scope": scope,
        **({"parent_endpoint": parent} if parent else {}),
        "is_leaf": leaf,
        "clock": {"mode": template["clock_mode"], "high_water_scope": scope},
        "objective": dials.pop("objective", [{"objective": "reliability", "weight": 1.0}]),
        "signal_capture": tone["signal_capture"],
        **({"stamp_quota": quota} if quota is not None else {}),
        "memory": dials.pop("memory", {"raw_retention": "P90D", "distilled_retention": "forever",
                                       "qa_sample_rate": 0.01}),
        "retrieval": dials.pop("retrieval", {"time_budget": {"time_ms": 500, "cost": 3},
                                             "horizon": "forever" if not parent else "P90D"}),
        "steward": {"token_budget": {"tokens": 100000}, "cadence": "P1D",
                    "on_budget_exhaustion": "degrade-to-floors-and-flag"},
        "tokens": {"workforce_ttl": "P1D", "resident_ttl": "P30D"},
        "model_gateway": {"judge_sample_rate": tone["judge_sample_rate"], "routing": "litellm"},
        "join_default": "floors-only",
        "trust_root": {"mode": "did-web", "root": root_did},
        "version": template["version"],
        "signature": {"alg": "ed25519", "by": root_did, "sig": "dGVtcGxhdGU"},
    }
    return validate(p, "tier-profile.schema.json")


def provision(template: dict, name: str, *, trust_tier: str = "anonymous") -> ProvisionedUniverse:
    validate(template, "universe-template.schema.json")
    if TRUST_ORDER[trust_tier] < TRUST_ORDER[template["trust_tier_required"]]:
        raise TrustTierError(f"template '{template['name']}' requires "
                             f"{template['trust_tier_required']}; requester is {trust_tier}")
    nanda = Nanda()
    root = Becky(f"u:{name}", nanda, universe_name=name)
    uni = HarnessNode(_profile(template, "universe", "universe", f"u:{name}", leaf=False,
                               parent=None, root_did=root.did, trust_tier=trust_tier), root, nanda)
    uni.soft.update(template.get("soft", {}))
    uni.soft["tone"] = {"value": template["tone"], "version": template["version"]}
    uni.skills.update(template.get("skills", {}))
    uni.publish_floors(PLATFORM_FLOORS + template.get("floors", []))

    prov = ProvisionedUniverse(name, nanda, root, uni, {}, {},
                               fuel_tokens=template["fuel"]["allotment_tokens"])
    budget_cap = (ANON_CAPS["budget_tokens"] if trust_tier == "anonymous" else None)
    for eco_t in template["topology"]["ecosystems"]:
        e_scope = f"u:{name}/e:{eco_t['name']}"
        b_eco = Becky(e_scope, nanda, parent=root)
        eco = HarnessNode(_profile(template, "ecosystem", "ecosystem", e_scope, leaf=False,
                                   parent=f"mem://u:{name}", root_did=root.did,
                                   trust_tier=trust_tier), b_eco, nanda, parent=uni)
        for f_name in eco_t["fields"]:
            f_scope = f"{e_scope}/f:{f_name}"
            b_f = Becky(f_scope, nanda, parent=b_eco)
            fld = HarnessNode(_profile(template, "field", "field", f_scope, leaf=True,
                                       parent=f"mem://{e_scope}", root_did=root.did,
                                       trust_tier=trust_tier), b_f, nanda, parent=eco)
            fld.pull_standards()
            prov.fields[f_name], prov.beckys[f_scope] = fld, b_f
            prov.surfaces[f_name] = []
            for entry in template["roster"]:
                arch, _ = root.issue_identity("archetype", f"u:{name}")
                budget = entry.get("budget_tokens", 2000)
                prov.surfaces[f_name] += factory.stamp(
                    fld, b_f, arch, entry["per_field"], generation=entry["generation"],
                    budget_tokens=min(budget, budget_cap) if budget_cap else budget,
                    probation_runs=entry.get("probation_runs", 5))
    return prov


def staff_field(prov: ProvisionedUniverse, template: dict, name: str, *,
                trust_tier: str = "anonymous") -> HarnessNode:
    """The 0037 §8.3 allowance (locked 2026-07-22): a field parented DIRECTLY
    off the universe — staff of the universe, as becky and vigil are; no
    decorative eco. Same chain math, one hop shorter: becky@field delegates
    straight from the root. The template schema's hard landing (universe-level
    fields in topology) is staged for a later rule-9 gate; this is the soft
    landing, in code the way the coordinate landed in tags (0033)."""
    f_scope = f"u:{prov.name}/f:{name}"
    b_f = Becky(f_scope, prov.nanda, parent=prov.becky)
    fld = HarnessNode(_profile(template, "field", "field", f_scope, leaf=True,
                               parent=f"mem://u:{prov.name}", root_did=prov.becky.did,
                               trust_tier=trust_tier), b_f, prov.nanda,
                      parent=prov.universe)
    fld.pull_standards()
    prov.fields[name], prov.beckys[f_scope] = fld, b_f
    prov.surfaces[name] = []
    return fld


# ---- the first three templates (locked 2026-07-02: League · Second Brain · Company) ----

def league_template() -> dict:
    return validate({
        "name": "league", "version": "0.1.0",
        "description": "Create Your Sports League — the time axis, playable (PG-1).",
        "trust_tier_required": "anonymous", "tone": "wild", "clock_mode": "declared",
        "topology": {"ecosystems": [{"name": "conference", "fields": ["team-a", "team-b"]}]},
        "profile_dials": {"field": {"stamp_quota": 30}},
        "roster": [{"archetype": "player", "per_field": 3, "generation": "draft-1",
                    "budget_tokens": 1500, "probation_runs": 5}],
        "fuel": {"allotment_tokens": 50_000, "idle_hibernate": "P14D"},
    }, "universe-template.schema.json")


def second_brain_template() -> dict:
    return validate({
        "name": "second-brain", "version": "0.1.0",
        "description": "A personal universe — the cheapest world, everyone's first 'mine'.",
        "trust_tier_required": "anonymous", "tone": "REAL", "clock_mode": "wall",
        "topology": {"ecosystems": [{"name": "life", "fields": ["desk"]}]},
        "profile_dials": {},
        "roster": [{"archetype": "librarian", "per_field": 1, "generation": "gen-1"}],
        "fuel": {"allotment_tokens": 20_000, "idle_hibernate": "P14D"},
    }, "universe-template.schema.json")


def company_template() -> dict:
    return validate({
        "name": "company", "version": "0.1.0",
        "description": "The Agentic Enterprise seed — REAL-toned, production-shaped (PG-3).",
        "trust_tier_required": "verified", "tone": "REAL", "clock_mode": "wall",
        "topology": {"ecosystems": [{"name": "ops", "fields": ["finance", "delivery"]}]},
        "profile_dials": {"field": {"stamp_quota": 100}},
        "roster": [{"archetype": "analyst", "per_field": 2, "generation": "cohort-1",
                    "budget_tokens": 8000, "probation_runs": 10}],
        "fuel": {"allotment_tokens": 0, "idle_hibernate": "P30D"},
    }, "universe-template.schema.json")
