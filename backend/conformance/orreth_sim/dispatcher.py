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

from . import improver, variants
from .identity import NOW
from .node import make_memory

STANDARD_NAME = "routing-standard"

# v2 (0065 sp1) — the genesis standard speaks the MENU's canonical names and
# its `built` list DERIVES from the variant registry (the three hand-kept
# copies retire). Rules stay DATA on the shelf: a fresh world plants this;
# a standing world's shelf version keeps serving until the promotion lane
# revises it. Two shapes the recon found classified-but-unrouted now route:
# comparative asks decompose (a built flow serves today) and temporal asks
# name Memory-Augmented — falling to the baseline LOUDLY until sp4 builds it,
# which is the Dispatcher's own honest law, never a special case.
STANDARD_V1 = {
    "version": "2",
    "rules": [
        {"when": "media", "route": "multimodal",
         "why": "media asks need the multimodal embedder"},
        {"when": "relational", "route": "graph",
         "why": "relationship-shaped asks walk edges, not distances"},
        {"when": "multi-source", "route": "multi-agent",
         "why": "cross-source asks decompose and recompose"},
        {"when": "comparative", "route": "multi-agent",
         "why": "each-and-which asks span subjects — they decompose per "
                "subject or they serve noise (the yardstick's find, 0053)"},
        {"when": "temporal", "route": "memory-augmented",
         "why": "as-of-when asks need the conversation's own past — the "
                "right row by name; the baseline serves loudly until it "
                "stands (0065 sp4)"},
        {"when": "precision", "route": "advanced",
         "why": "exactness-shaped asks earn the second pass"},
    ],
    "default": "naive",
    # derived, never hand-maintained: the genesis truth is the registry's
    "built": variants.built(["naive"]),
}

_SHAPES = (
    ("temporal", re.compile(r"\b(as of|since|before|after)\s+\d{4}-\d{2}-\d{2}\b|"
                            r"\bwhat changed\b|\bhistory of\b")),
    ("media", re.compile(r"\b(image|photo|picture|video|audio|diagram|png|jpg)\b")),
    ("relational", re.compile(r"\b(relate[ds]?|relationship|connect(?:ed|ion)?s?|"
                              r"between|depends? on|linked?|who knows)\b")),
    ("multi-source", re.compile(r"\b(compare|across|versus|vs\.?|difference between|"
                                r"both|all sources)\b")),
    # the yardstick's find (0053 sp3): each-and-which asks span subjects —
    # they decompose per subject and recompose, or they serve noise
    ("comparative", re.compile(r"\beach\s+\w+\b|\bwhich\s+\w+\s+(?:was|is|gave|"
                               r"has|did)\b|\bmost\s+\w+\s+(?:this|last)\s+week\b|"
                               r"\bper\s+(?:desk|floor|world|resident)\b")),
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
             kind: str = "get", origin: str = "",
             built: list | None = None, force: str | None = None) -> dict:
    """One ask through the reflex: classify → the standard's first matching
    rule → the flavor — falling to the baseline LOUDLY when the chosen row is
    not yet built. The choice lands as a signed record, always.
    force (0071 sp2): the asker chose the row itself — Auto stands aside, the
    classification is still recorded, and the choice record says who chose."""
    std = standard(node)
    shapes = classify(ask)
    rule = next((r for r in std.get("rules", [])
                 if r.get("when") in shapes), None)
    if force:
        chosen = force
        why = f"the asker chose «{force}» — Auto stood aside"
        rule = {"when": "caller-selected", "why": why}
    else:
        chosen = rule["route"] if rule else std.get("default", "naive")
        why = rule["why"] if rule else "no shape matched — the default row serves"
    # the rows standing NOW — the caller's truth; the standard's genesis list
    # is the fallback (v2 of the asset rides the lanes as the rows earn it)
    built = built or std.get("built") or ["naive"]
    # 0065 sp1 — one vocabulary: a standing world's shelf standard may still
    # speak the legacy flow names ('rerank', 'swarm') while the registry
    # speaks the menu's — both resolve to the canonical style, so no honest
    # choice ever falls to the baseline over a name
    chosen = variants.resolve(chosen) or chosen
    built = [variants.resolve(b) or b for b in built]
    fallback = None
    if chosen not in built:
        fallback = chosen
        chosen = std.get("default", "naive")
        why += (f"; «{fallback}» is not yet built — falling to the baseline, "
                "on the record")
    if chosen not in built:
        # the DEFAULT itself may be absent where this ask landed (caught live
        # 2026-07-25: v2 made «router» the default while a caller still stood
        # four rows) — the baseline is the LAST floor, and the fall stays loud
        fallback = fallback or chosen
        chosen = "naive"
        why += (f"; the default «{fallback}» does not stand here either — "
                "the baseline row serves, on the record")
    # 0066 sp1 — THE CHOICE JOINS THE WORLD: it stops being a leaf. Lineage
    # points at the exact policy version that made it (re-scorable under any
    # future weights); the coordinate rides as tags (0033 §4's idiom — the
    # style tag matching 0065 sp5's answer-record law, the origin when one
    # spoke); the featurizer names its version so sp2's mind replaces a
    # NAMED v0, never an anonymous regex.
    srow = improver.active_asset(node, STANDARD_NAME)
    body = {"dispatch": {"kind": kind, "ask": (ask or "")[:200],
                         **({"origin": origin} if origin else {}),
                         "shapes": shapes, "flavor": chosen,
                         **({"wanted": fallback} if fallback else {}),
                         "rule": (rule or {}).get("when", "default"),
                         "why": why, "standard_version": std.get("version", "?"),
                         **({"standard_ref": srow[0]} if srow else {}),
                         "featurizer_version": "shapes-v0",
                         "at": NOW()}}
    rec = make_memory(librarian, librarian_kp, node.scope, body,
                      kind="episodic",
                      tags=["dispatch", chosen, kind, f"variant:{chosen}",
                            *([f"origin:{origin[:48]}"] if origin else [])])
    if srow:
        rec["derived_from"] = [srow[0]]   # the choice ← the rulebook version;
        # an unplanted (genesis-only) standard leaves lineage EMPTY, honestly —
        # never a fabricated ref
    rid = node.write(rec)
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
