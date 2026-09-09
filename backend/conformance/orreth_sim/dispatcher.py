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
    # 0066 sp3 — THE REWARD FUNCTION IS LAW: the signal vector's combining
    # weights live HERE, so re-weighting reward is a gated standard change
    # like any rule — and history is re-scorable under any future weights
    "weights": {"retrieval": 0.3, "faithfulness": 0.3,
                "answer": 0.25, "coverage": 0.15},
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


def plant_router_retirement(node, librarian: dict, librarian_kp) -> str | None:
    """0066 sp5 — the router ROW retires honorably, ON THE RECORD (0065 L1's
    word): one signed record per world, the librarian's authorship, saying
    what retired, what absorbed it, and where the tactic-picker lives on.
    Dormancy is never deletion — the record IS the honorable rest."""
    for r in node.records.values():
        if "router-retired" in (r.get("tags") or []):
            return None                    # the rest already stands
    rec = make_memory(librarian, librarian_kp, node.scope,
                      {"retirement": {
                          "row": "router",
                          "absorbed_by": "Auto — the selector's own switch "
                                         "position, never a style",
                          "tactic_lives_on": "inside the swarm's fan-out, "
                                             "picking each part's row",
                          "why": "0065 L1 (flows, not floors) + 0066: the "
                                 "Router became the Dispatcher's own brain; "
                                 "a contestant that IS the referee cannot "
                                 "stand in the contest"}},
                      kind="episodic", tags=["router-retired", "dispatch"])
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
             built: list | None = None, force: str | None = None,
             attributes: dict | None = None, consult=None,
             slice_pct: int = 0) -> dict:
    """One ask through the reflex: the Analyzer reads → the standard's first
    matching rule → the flavor — falling to the baseline LOUDLY when the
    chosen row is not yet built. The choice lands as a signed record, always.
    force (0071 sp2): the asker chose the row itself — Auto stands aside.
    consult (0066 sp2): the escalation the docstring always promised — on an
    AMBIGUOUS read (and only when the asker did not demand speed), a governed
    mind picks from the menu under a typed contract; it parks honestly and
    the deterministic read serves. The asker's own word always outranks the
    mind; the mind's choice still obeys the built law like everyone."""
    from . import featurizer
    std = standard(node)
    features = featurizer.featurize(ask, attributes)
    shapes = features["shapes"]
    rule = next((r for r in std.get("rules", [])
                 if r.get("when") in shapes), None)
    consulted = None
    if force:
        chosen = force
        why = f"the asker chose «{force}» — Auto stood aside"
        rule = {"when": "caller-selected", "why": why}
    else:
        chosen = rule["route"] if rule else std.get("default", "naive")
        why = rule["why"] if rule else "no shape matched — the default row serves"
        if consult is not None and featurizer.should_consult(features):
            consulted = featurizer.consult(consult, ask, features)
            if "style" in consulted:
                chosen = consulted["style"]
                why = (f"the ask was ambiguous — a quick governed look chose "
                       f"«{chosen}»: {consulted['why']}")
                rule = {"when": "mind-consulted", "why": why}
            else:
                why += f" ({consulted['parked']})"
    # the rows standing NOW — the caller's truth; the standard's genesis list
    # is the fallback (v2 of the asset rides the lanes as the rows earn it)
    built = built or std.get("built") or ["naive"]
    # 0065 sp1 — one vocabulary: a standing world's shelf standard may still
    # speak the legacy flow names ('rerank', 'swarm') while the registry
    # speaks the menu's — both resolve to the canonical style, so no honest
    # choice ever falls to the baseline over a name
    chosen = variants.resolve(chosen) or chosen
    built = [variants.resolve(b) or b for b in built]
    # 0066 sp5 — THE LIVE SLICE: a small, dialed share of Auto-routed asks
    # deterministically tries a style the rulebook did not pick — the
    # standings' only live exploration, confessed on the record. Never on a
    # caller's own choice, never over a spent thought.
    exploration = None
    if slice_pct > 0 and not force and not consulted and len(built) > 1:
        from .crypto import content_hash
        h = int(content_hash({"explore": (ask or "")})[7:15], 16)
        if (h % 100) < min(int(slice_pct), 20):     # the hard bound holds
            others = [b for b in built
                      if (variants.resolve(b) or b) !=
                      (variants.resolve(chosen) or chosen)]
            if others:
                exploration = {"instead_of": chosen}
                chosen = others[(h // 100) % len(others)]
                why = (f"the exploration slice tried «{chosen}» instead of "
                       f"«{exploration['instead_of']}» — a small measured "
                       "share, inside the human's dial, on the record")
                rule = {"when": "exploration-slice", "why": why}
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
                         "featurizer_version": featurizer.VERSION,
                         "features": features,
                         **({"consulted": consulted} if consulted else {}),
                         **({"exploration": exploration} if exploration
                            else {}),
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
    """The PUT side (0066 sp5 — 0065's parked stub, paid): which styles'
    projections index a new record, DERIVED from the registry and the
    record's own modality — deterministic, never "everything". A
    media-tagged record feeds the media style and the baseline; everything
    else feeds every text style and skips the media shelf. Placement itself
    stays the universe's law (0022) — this only names the indexes."""
    std = standard(node)
    built = [variants.resolve(b) or b for b in (std.get("built") or ["naive"])]
    media = any(str(t).startswith("media") for t in (tags or []))
    if media:
        rows = [s for s in built if s in ("multimodal", "naive")]
    else:
        rows = [s for s in built if s != "multimodal"]
    return rows or ["naive"]


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
