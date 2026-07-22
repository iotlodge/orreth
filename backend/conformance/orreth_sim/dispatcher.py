# PROVENANCE: Fable 5 (claude-fable-5) — 0038, the Stacks · 2026-07-22
"""The Dispatcher (0038 §3) — spoonful 2: the reflex and the judgment, split.

An unembodied organ in the put/get path — AFTER the gateway's authorization,
never around it — routing every ask by the CURRENT routing standard: a
versioned asset the librarian tends from receipts. No thinking in the hot
path: `classify()` is deterministic; ambiguity ESCALATES to her seat rather
than guessing quietly. The organ enforces; the resident learns.

EVERY CHOICE IS A RECORD — which flavor, which rule, why, and whether the
chosen row exists yet. A flavor not yet built falls to the baseline LOUDLY,
on the record: the universe never pretends a row it does not have. And so the
spacetime window answers "why did this question go to the graph field?" as a
query — the substrate JB's closed loop and reinforcement learning will stand
on (choices = actions · gradings = reward · standard revisions = policy).
"""
from __future__ import annotations

import re

from . import improver
from .identity import NOW
from .node import make_memory

STANDARD_NAME = "routing-standard"

# v1 — the genesis standard: rules are DATA on the shelf, never code. The
# librarian proposes revisions from the standings; JB gates rewrites (0031).
STANDARD_V1 = {
    "version": "1",
    "rules": [
        {"when": "media", "route": "multimodal",
         "why": "media asks need the multimodal embedder"},
        {"when": "relational", "route": "graph",
         "why": "relationship-shaped asks walk edges, not distances"},
        {"when": "multi-source", "route": "swarm",
         "why": "cross-source asks decompose and recompose"},
        {"when": "precision", "route": "rerank",
         "why": "exactness-shaped asks earn the second pass"},
    ],
    "default": "naive",
    "built": ["naive"],          # the rows that BREATHE — grown as sp3/sp4 land
}

_SHAPES = (
    ("media", re.compile(r"\b(image|photo|picture|video|audio|diagram|png|jpg)\b")),
    ("relational", re.compile(r"\b(relate[ds]?|relationship|connect(?:ed|ion)?s?|"
                              r"between|depends? on|linked?|who knows)\b")),
    ("multi-source", re.compile(r"\b(compare|across|versus|vs\.?|difference between|"
                                r"both|all sources)\b")),
    ("precision", re.compile(r"(\"[^\"]+\"|“[^”]+”|\bexact(?:ly)?\b|\bverbatim\b|"
                             r"\bword for word\b)")),
)


def plant_standard(node, librarian: dict, librarian_kp) -> str | None:
    """Genesis: the routing standard enters the shelf versioned, under the
    librarian's signature — from here a routing change is a proposal on the
    lanes, never an edit to code."""
    if improver.active_asset(node, STANDARD_NAME):
        return None
    rec = improver.make_asset(librarian, librarian_kp, node.scope,
                              name=STANDARD_NAME, profile=STANDARD_V1)
    return node.write(rec)


def standard(node) -> dict:
    """The ACTIVE standard's word — genesis shape until a version stands."""
    row = improver.active_asset(node, STANDARD_NAME)
    prof = improver._profile_of(row[1]) if row else {}
    return prof if prof.get("rules") else STANDARD_V1


def classify(ask: str) -> list[str]:
    """The ask's shape, read deterministically — no thinking in the hot path.
    Returns every matched shape, first match strongest."""
    low = (ask or "").lower()
    return [name for name, rx in _SHAPES if rx.search(low)]


def dispatch(node, librarian: dict, librarian_kp, ask: str, *,
             kind: str = "get", origin: str = "") -> dict:
    """One ask through the reflex: classify → the standard's first matching
    rule → the flavor — falling to the baseline LOUDLY when the chosen row is
    not yet built. The choice lands as a signed record, always."""
    std = standard(node)
    shapes = classify(ask)
    rule = next((r for r in std.get("rules", [])
                 if r.get("when") in shapes), None)
    chosen = rule["route"] if rule else std.get("default", "naive")
    why = rule["why"] if rule else "no shape matched — the baseline serves"
    built = std.get("built") or ["naive"]
    fallback = None
    if chosen not in built:
        fallback = chosen
        chosen = std.get("default", "naive")
        why += (f"; «{fallback}» is not yet built — falling to the baseline, "
                "on the record")
    body = {"dispatch": {"kind": kind, "ask": (ask or "")[:200],
                         **({"origin": origin} if origin else {}),
                         "shapes": shapes, "flavor": chosen,
                         **({"wanted": fallback} if fallback else {}),
                         "rule": (rule or {}).get("when", "default"),
                         "why": why, "standard_version": std.get("version", "?"),
                         "at": NOW()}}
    rid = node.write(make_memory(librarian, librarian_kp, node.scope, body,
                                 kind="episodic", tags=["dispatch", chosen, kind]))
    return {"flavor": chosen, "why": why, "shapes": shapes, "record": rid,
            **({"wanted": fallback} if fallback else {})}


def dispatch_put(node, tags: list[str]) -> list[str]:
    """The PUT side: which projections index a new record — every BUILT row
    whose appetite matches (v1: the baseline eats everything; the specialists
    declare appetites as they land in sp3/sp4). Placement itself stays the
    universe's law (0022) — this only names the indexes."""
    std = standard(node)
    return list(std.get("built") or ["naive"])


def choices(node, k: int = 8) -> list[dict]:
    """The organ's ledger — newest choices, walkable: the RL substrate and the
    human's 'why did this go there?' in one query."""
    import json

    from . import crypto
    rows = sorted((r for r in node.records.values()
                   if "dispatch" in (r.get("tags") or [])),
                  key=lambda r: r["received_at"], reverse=True)
    return [json.loads(crypto._b64d(r["body"]).decode())["dispatch"]
            for r in rows[:k]]
