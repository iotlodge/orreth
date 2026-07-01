"""Build a universe — the layering claim, proven every time this runs (0000 §7).

One node kind, three profiles: u:demo (apex) / two ecosystems / fields with agents.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .identity import Becky, Nanda
from .node import HarnessNode


def _profile(label: str, scope: str, *, leaf: bool, parent: str | None,
             horizon: str, root: str) -> dict:
    return {
        "tier_label": label,
        "scope": scope,
        **({"parent_endpoint": parent} if parent else {}),
        "is_leaf": leaf,
        "memory": {
            "raw_retention": "P90D" if leaf else "P395D",
            "distilled_retention": "forever" if label == "universe" else "P395D",
            "qa_sample_rate": 0.01 if leaf else 0.001,
        },
        "retrieval": {
            "time_budget": {"time_ms": 500, "cost": 3},
            "horizon": horizon,
        },
        "steward": {
            "token_budget": {"tokens": 100000},
            "cadence": "P1D",
            "on_budget_exhaustion": "degrade-to-floors-and-flag",
        },
        "tokens": {"workforce_ttl": "P1D", "resident_ttl": "P30D"},
        "model_gateway": {"judge_sample_rate": 0.1, "routing": "litellm"},
        "join_default": "fully-joined",
        "trust_root": {"mode": "did-web", "root": root},
        "version": "0.0.1",
        "signature": {"alg": "ed25519", "by": root, "sig": "cHJvZmlsZQ"},
    }


@dataclass
class World:
    nanda: Nanda
    becky: Becky
    universe: HarnessNode
    eco_cloud: HarnessNode
    eco_dev: HarnessNode
    field_prod: HarnessNode
    field_lab: HarnessNode
    agents: dict = field(default_factory=dict)   # name -> (identity, keypair)
    beckys: dict = field(default_factory=dict)   # scope -> Becky


def build() -> World:
    nanda = Nanda()
    root = Becky("u:demo", nanda, universe_name="demo")
    b_cloud = Becky("u:demo/e:cloud", nanda, parent=root)
    b_dev = Becky("u:demo/e:dev", nanda, parent=root)
    b_prod = Becky("u:demo/e:cloud/f:prod", nanda, parent=b_cloud)
    b_lab = Becky("u:demo/e:dev/f:lab", nanda, parent=b_dev)

    uni = HarnessNode(_profile("universe", "u:demo", leaf=False, parent=None,
                               horizon="forever", root=root.did), root, nanda)
    cloud = HarnessNode(_profile("ecosystem", "u:demo/e:cloud", leaf=False,
                                 parent="mem://u:demo", horizon="P395D", root=root.did),
                        b_cloud, nanda, parent=uni)
    dev = HarnessNode(_profile("ecosystem", "u:demo/e:dev", leaf=False,
                               parent="mem://u:demo", horizon="P395D", root=root.did),
                      b_dev, nanda, parent=uni)
    prod = HarnessNode(_profile("field", "u:demo/e:cloud/f:prod", leaf=True,
                                parent="mem://u:demo/e:cloud", horizon="P90D", root=root.did),
                       b_prod, nanda, parent=cloud)
    lab = HarnessNode(_profile("field", "u:demo/e:dev/f:lab", leaf=True,
                               parent="mem://u:demo/e:dev", horizon="P90D", root=root.did),
                      b_lab, nanda, parent=dev)

    w = World(nanda, root, uni, cloud, dev, prod, lab,
              beckys={"u:demo": root, "u:demo/e:cloud": b_cloud, "u:demo/e:dev": b_dev,
                      "u:demo/e:cloud/f:prod": b_prod, "u:demo/e:dev/f:lab": b_lab})

    # an archetype and its incarnations — shared skills, isolated memory (0002 §1)
    archetype, akp = root.issue_identity("archetype", "u:demo")
    w.agents["architect-archetype"] = (archetype, akp)
    a1, k1 = b_prod.issue_identity("instance", "u:demo/e:cloud/f:prod", lineage=archetype["did"])
    a2, k2 = b_prod.issue_identity("instance", "u:demo/e:cloud/f:prod", lineage=archetype["did"])
    a3, k3 = b_lab.issue_identity("instance", "u:demo/e:dev/f:lab", lineage=archetype["did"])
    w.agents["prod-1"], w.agents["prod-2"], w.agents["lab-1"] = (a1, k1), (a2, k2), (a3, k3)
    return w
