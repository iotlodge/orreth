# PROVENANCE: Fable 5 (claude-fable-5) — 0038, the Stacks · 2026-07-22
"""The Stacks (0038) spoonful 3: the rivals — rerank · graph · hybrid.

Three more rows over the SAME one truth: each is a flow plus a projection
derived from the signed log — never a second store. The rerank row retrieves
wide and re-scores narrow (precision earns a second pass). The graph row
extracts entities and co-occurrence edges from the log into a graph
PROJECTION (Shape A holds — tables in the sim dict, Postgres on the wire) and
answers relationship-shaped asks by WALKING, not measuring. The hybrid row
fuses both scores. All deterministic in the sim — the standings must compare
flows, not dice.

Same laws as the baseline: rebuildable therefore disposable; a record gone
from the log stops speaking everywhere; every answer wears citations.
"""
from __future__ import annotations

import re

from . import stacks

STOP = {"the", "a", "an", "and", "or", "of", "in", "on", "at", "to", "is",
        "are", "it", "its", "with", "for", "by", "as", "that", "this",
        "through", "between", "how", "what", "why", "when", "do", "does"}


def _terms(text: str) -> list[str]:
    return [w for w in re.findall(r"[a-z][a-z0-9-]+", (text or "").lower())
            if w not in STOP and len(w) > 2]


# ---------------------------------------------------------------- f:rerank

def rerank_retrieve(projection: dict, query: str, k: int = 4) -> list[dict]:
    """Wide then narrow: cosine casts a broad net (3k), then a second pass
    re-scores by exact term overlap — the precision row's delta, nothing else."""
    wide = stacks.retrieve(projection, query, k=3 * k)
    qt = set(_terms(query))
    for h in wide:
        overlap = len(qt & set(_terms(h["text"]))) / (len(qt) or 1)
        h["score"] = round(0.4 * h["score"] + 0.6 * overlap, 4)
    wide.sort(key=lambda h: -h["score"])
    return [h for h in wide[:k] if h["score"] > 0.15]


# ---------------------------------------------------------------- f:graph

def graph_project(node) -> dict:
    """The graph PROJECTION: terms as nodes, within-chunk co-occurrence as
    edges, every edge remembering the chunk (and record) that made it — the
    citation IS the edge's provenance. Derived from the log; regrown at will."""
    base = stacks.project(node)
    nodes: set = set()
    edges: dict = {}
    for c in base["chunks"]:
        ts = _terms(c["text"])
        nodes.update(ts)
        for i, a in enumerate(ts):
            for b in ts[i + 1:]:      # a chunk is small — bind all its pairs
                if a != b:
                    edges.setdefault(tuple(sorted((a, b))), []).append(
                        {"ref": c["ref"], "doc": c["doc"], "text": c["text"]})
    return {"flavor": "graph", "nodes": nodes, "edges": edges,
            "chunks": base["chunks"]}


def graph_retrieve(gproj: dict, query: str, k: int = 4) -> list[dict]:
    """Walking, not measuring: find edges CONNECTING the ask's terms — a hit
    is a chunk that binds two of them together. One-term asks fall to the
    edges touching that term."""
    qt = [t for t in _terms(query) if t in gproj["nodes"]]
    hits: dict = {}
    for i, a in enumerate(qt):
        for b in qt[i + 1:]:
            for w in gproj["edges"].get(tuple(sorted((a, b))), []):
                e = hits.setdefault(w["ref"] + str(w["text"][:24]),
                                    {**w, "score": 0.0, "pair": f"{a}↔{b}"})
                e["score"] = round(e["score"] + 1.0, 4)
    if not hits and len(qt) == 1:
        for (a, b), ws in gproj["edges"].items():
            if qt[0] in (a, b):
                for w in ws[:2]:
                    hits.setdefault(w["ref"] + str(w["text"][:24]),
                                    {**w, "score": 0.5, "pair": f"{a}↔{b}"})
    out = sorted(hits.values(), key=lambda h: -h["score"])[:k]
    return [{"ref": h["ref"], "doc": h["doc"], "text": h["text"],
             "score": h["score"], "pair": h.get("pair", "")} for h in out]


# ---------------------------------------------------------------- f:hybrid

def hybrid_retrieve(node, projection: dict, gproj: dict, query: str,
                    k: int = 4) -> list[dict]:
    """Vector + graph, fused at query time: distance finds the like, walking
    finds the bound; the fusion ranks what BOTH ways can defend."""
    vec = {h["ref"] + h["text"][:24]: h
           for h in stacks.retrieve(projection, query, k=2 * k)}
    gr = {h["ref"] + h["text"][:24]: h
          for h in graph_retrieve(gproj, query, k=2 * k)}
    fused: dict = {}
    for key in set(vec) | set(gr):
        v, g2 = vec.get(key), gr.get(key)
        base = v or g2
        fused[key] = {**base, "score": round(
            0.5 * (v["score"] if v else 0) + 0.5 * min(1.0, (g2["score"] if g2
                                                             else 0) / 3), 4)}
    out = sorted(fused.values(), key=lambda h: -h["score"])[:k]
    return [h for h in out if h["score"] > 0.1]


# ---------------------------------------------------------------- one door

RETRIEVERS = {
    "naive": lambda node, q, k=4: stacks.retrieve(stacks.project(node), q, k),
    "rerank": lambda node, q, k=4: rerank_retrieve(stacks.project(node), q, k),
    "graph": lambda node, q, k=4: graph_retrieve(graph_project(node), q, k),
    "hybrid": lambda node, q, k=4: hybrid_retrieve(
        node, stacks.project(node), graph_project(node), q, k),
}


def answer_as(node, flavor: str, query: str) -> dict:
    """One door for every built row: retrieve by flavor, answer with citations
    — the shape the Dispatcher routes into and the standings will grade."""
    hits = RETRIEVERS[flavor](node, query)
    if not hits:
        return {"answer": "the stacks hold nothing on this — an honest unknown",
                "citations": [], "flavor": flavor}
    lines = [f"“{h['text'][:160].strip()}”"
             + (f" ({h['pair']})" if h.get("pair") else "")
             + f" [{h['ref'][:18]}…]" for h in hits[:2]]
    return {"answer": " · ".join(lines), "flavor": flavor,
            "citations": [{"ref": h["ref"], "doc": h["doc"],
                           "score": h["score"]} for h in hits]}
