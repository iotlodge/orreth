# PROVENANCE: Claude Fable 5 (claude-fable-5) — 0065 sp1, the variant registry · 2026-09-09
"""The eleven retrieval styles as DECLARATIONS — the 0063 pattern applied to
flows (0065 §3.2). Two layers, one razor:

- **This registry is firmware**: each style's name, its composition over the
  six module boundaries (understand → retrieve → refine → construct →
  generate → enhance), what it needs to run, what it costs, and its delta —
  the one sentence naming what this style does that the plain baseline
  cannot. Changing a declaration is a release.
- **A style's numbers are craft**: each declaration carries a `genesis`
  config — the `variant-<name>` asset's starting profile — turned in prod
  through the one craft door, gate-checked here BEFORE landing, teachings on
  every sibling. That is what the proof's Workshop edits and versions.

The menu the charter locked (2026-09-06): Auto is the selector's own switch
position (the Router's subject, dive 0066 — never a registry row), Modular is
the chassis itself, and these eleven are the selectable styles. Six ride
flows that already breathe (`row` names the executing flow); five are
declared with `row: None` until 0065 sp4 builds their scaffolds — a declared
style whose flow is not yet standing refuses loudly and falls to the
baseline, on the record, exactly as the Dispatcher has always fallen.

The routing standard's `built` list DERIVES from this registry — the
hand-maintained arrays in three files retire with this module's birth.
"""
from __future__ import annotations

MODULES = ("understand", "retrieve", "refine", "construct", "generate",
           "enhance")

# legacy flow names → the canonical menu style that grew from them
_LEGACY = {"rerank": "advanced", "swarm": "multi-agent"}

VARIANTS_V1: dict = {
    "naive": {
        "title": "Naive",
        "row": "naive",
        "stages": ["retrieve", "construct"],
        "requires": [],
        "cost_class": "low",
        "delta": "the baseline control — one plain search, top matches, "
                 "citations; every other style is measured against it",
        "why": "the yardstick law (0038): standings mean nothing without an "
               "unchanging floor to stand on",
        "blast": "turning its numbers moves the FLOOR every other style is "
                 "judged against",
        "genesis": {"k": 4},
    },
    "advanced": {
        "title": "Advanced",
        "row": "rerank",
        "stages": ["understand", "retrieve", "refine", "construct"],
        "requires": [],
        "cost_class": "medium",
        "delta": "casts a wide net first, then re-scores the catch — "
                 "exactness-shaped questions earn the second pass",
        "why": "professional retrieval beyond baseline (the proof's charter); "
               "grows from the standing rerank flow",
        "blast": "a wider net costs more per ask; a narrower one misses the "
                 "exact phrase the asker quoted",
        "genesis": {"k": 4, "wide_factor": 2},
    },
    "hierarchical": {
        "title": "Hierarchical",
        "row": None,
        "stages": ["retrieve", "refine", "construct"],
        "requires": ["tree-projection"],
        "cost_class": "medium",
        "delta": "climbs a document's own structure — section to page to "
                 "passage — so long documents answer from the right floor "
                 "of the building, not a random room",
        "why": "long-document asks lose the plot at flat-chunk grain (the "
               "wiki research's short/long split); arrives with sp2's tree "
               "projection + sp4's scaffold",
        "blast": "deeper trees read more; shallower ones flatten long "
                 "documents back into noise",
        "genesis": {"k": 4, "levels": 2},
    },
    "multimodal": {
        "title": "Multimodal",
        "row": "multimodal",
        "stages": ["retrieve", "construct"],
        "requires": ["vision-mind"],
        "cost_class": "high",
        "delta": "searches what pictures, audio, and diagrams hold — not "
                 "only what words say",
        "why": "media-shaped asks need a media-shaped shelf; the eye "
               "honestly awaits a saddled vision mind (0029) and confesses "
               "until then",
        "blast": "per-modality embedding spend; a dark vision mind means "
                 "honest refusals, never pretended sight",
        "genesis": {"k": 4},
    },
    "multi-agent": {
        "title": "Multi-Agent",
        "row": "swarm",
        "stages": ["understand", "retrieve", "refine", "construct"],
        "requires": [],
        "cost_class": "high",
        "delta": "splits a many-part question into parts, retrieves each, "
                 "and recomposes one answer — each-and-which asks stop "
                 "serving noise",
        "why": "cross-source and comparative asks decompose or they fail "
               "(the yardstick's own find, 0053 sp3); grows from the "
               "standing swarm flow; async fan-out stays parked per 0038",
        "blast": "more parts read more and spend more; fewer parts glue "
                 "distinct questions back together",
        "genesis": {"parts": 4, "k_per_part": 2},
    },
    "reasoning-first": {
        "title": "Reasoning-First",
        "row": None,
        "stages": ["understand", "retrieve", "refine", "construct",
                   "generate"],
        "requires": ["planning-mind"],
        "cost_class": "high",
        "delta": "thinks before it looks — writes a retrieval plan as a "
                 "signed record, then runs targeted retrieves against it "
                 "and hands back an evidence pack",
        "why": "hard questions fail on eager retrieval; the plan-as-record "
               "makes the thinking auditable (arrives sp4, scaffold first)",
        "blast": "more steps cost more thinking; fewer steps degrade it "
                 "back into the baseline it was meant to beat",
        "genesis": {"k": 4, "max_steps": 3},
    },
    "memory-augmented": {
        "title": "Memory-Augmented",
        "row": None,
        "stages": ["understand", "retrieve", "refine", "construct"],
        "requires": ["conversation-worldlines"],
        "cost_class": "medium",
        "delta": "remembers the conversation first — rewrites the question "
                 "with what was already said, then retrieves; follow-ups "
                 "and as-of-when asks stop starting from zero",
        "why": "temporal and follow-up asks classify today and route "
               "nowhere; the worldline substrate arrives with dive 0070, "
               "the scaffold with sp4",
        "blast": "too much memory drags old context into new questions; "
                 "too little forgets what the asker just said",
        "genesis": {"k": 4, "memory_k": 3},
    },
    "graph": {
        "title": "Graph",
        "row": "graph",
        "stages": ["retrieve", "refine", "construct"],
        "requires": ["graph-projection"],
        "cost_class": "medium",
        "delta": "answers relationship-shaped questions by WALKING the "
                 "edges between things instead of measuring distances "
                 "between texts",
        "why": "pays 0038's Shape-A promise; Full GraphRAG locked by the "
               "proof's charter (sp3 lands the Postgres projection)",
        "blast": "more hops walk further and slower; zero hops make it the "
                 "baseline wearing a costume",
        "genesis": {"k": 4, "hops": 1},
    },
    "hybrid": {
        "title": "Hybrid",
        "row": "hybrid",
        "stages": ["retrieve", "refine", "construct"],
        "requires": [],
        "cost_class": "medium",
        "delta": "fuses distance-search and edge-walking into one ranking — "
                 "what BOTH ways can defend outranks what only one found",
        "why": "the fusion machinery the meaning axis and the graph row "
               "already model, made a style of its own",
        "blast": "the weights ARE the style: tilt them far enough and it "
                 "collapses into whichever side you favored",
        "genesis": {"k": 4, "w_vector": 0.5, "w_graph": 0.5},
    },
    "hyde": {
        "title": "HyDE",
        "row": None,
        "stages": ["understand", "generate", "retrieve", "construct"],
        "requires": ["drafting-mind"],
        "cost_class": "medium",
        "delta": "imagines what a perfect answer would look like, then "
                 "searches for records that RESEMBLE that imagined answer — "
                 "vague questions find precise shelves",
        "why": "hypothetical-document search needs the meaning axis plus a "
               "drafting mind (arrives sp4, scaffold first)",
        "blast": "the hypothesis steers the search: a bad draft finds "
                 "confidently wrong shelves",
        "genesis": {"k": 4, "hypotheses": 1},
    },
    "corrective": {
        "title": "Corrective",
        "row": None,
        "stages": ["retrieve", "refine", "generate", "enhance"],
        "requires": ["judging-mind"],
        "cost_class": "high",
        "delta": "checks its own catch before answering — a weak or "
                 "unfaithful retrieval triggers a targeted second look "
                 "instead of a confident wrong answer",
        "why": "the critic's three moves entering the retrieval loop "
               "(arrives sp4, scaffold first)",
        "blast": "a high bar re-retrieves often and spends double; a low "
                 "one never corrects anything",
        "genesis": {"k": 4, "max_retries": 1, "faithfulness_floor": 0.5},
    },
}

MENU = ("naive", "advanced", "hierarchical", "multimodal", "multi-agent",
        "reasoning-first", "memory-augmented", "graph", "hybrid", "hyde",
        "corrective")


def resolve(name: str) -> str | None:
    """Any spoken name → the canonical style, or None. Accepts the menu's
    own names and the legacy flow names the world already speaks ('rerank',
    'swarm'); 'router' resolves to None — Auto is a switch position, never
    a style."""
    n = str(name or "").strip().lower()
    if n in VARIANTS_V1:
        return n
    return _LEGACY.get(n)


def row_for(short: str) -> str | None:
    """The executing flow behind a style — None until its scaffold lands."""
    d = VARIANTS_V1.get(short)
    return d["row"] if d else None


def built(available_rows) -> list[str]:
    """The styles that can SERVE here, derived — registry × the flows that
    actually stand. Never hand-maintained again (the three-copies wound)."""
    rows = set(available_rows or ())
    return [s for s in MENU if VARIANTS_V1[s]["row"] in rows]


def teachings(short: str) -> dict:
    """What rides every variant-* sibling so no config record has amnesia."""
    d = VARIANTS_V1[short]
    return {k: d[k] for k in
            ("title", "stages", "requires", "cost_class", "delta", "why",
             "blast")}


def gate_check(asset_name: str, profile) -> tuple[str | None, dict | None]:
    """The craft door's law for variant-* assets (the dial gate's twin):
    an undeclared style refuses naming the menu; an undeclared knob refuses
    naming the declared ones; a wrong-typed number refuses with the blast.
    A clean turn lands CANONICAL — genesis keys only, genesis-typed."""
    short = asset_name[len("variant-"):]
    d = VARIANTS_V1.get(short)
    if d is None:
        return (f"no declared style is named “{asset_name}” — a style's "
                f"SHAPE is firmware, and the registry declares only: "
                + ", ".join(f"variant-{s}" for s in MENU), None)
    if not isinstance(profile, dict):
        return ("a style turns by its config alone — the body is an object "
                "of the declared knobs, nothing else", None)
    g = d["genesis"]
    clean: dict = {}
    for k, v in profile.items():
        if k not in g:
            return (f"“{k}” is not a knob this style declares — {short} "
                    f"turns only: {', '.join(sorted(g))}. Its blast: "
                    f"{d['blast']}", None)
        want = type(g[k])
        try:
            cv = want(v)
        except (TypeError, ValueError):
            return (f"“{k}” must be {want.__name__} like its genesis "
                    f"({g[k]!r}) — the declaration holds", None)
        if isinstance(cv, (int, float)) and not isinstance(cv, bool) and cv < 0:
            return (f"“{k}” cannot be negative — the declaration holds; "
                    f"this style's blast: {d['blast']}", None)
        clean[k] = cv
    return None, clean


def config(short: str, head: dict | None = None) -> dict:
    """The style's working numbers: genesis under the shelf head's word —
    read-side, a head never widens the knob set (undeclared keys are
    dropped, the genesis serves beneath). The threading into each flow is
    sp4's work; the law lives here from birth."""
    g = dict(VARIANTS_V1[short]["genesis"])
    for k, v in (head or {}).items():
        if k in g:
            g[k] = v
    return g
