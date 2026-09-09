# PROVENANCE: Claude Fable 5 (claude-fable-5) — 0065 sp4, the five new styles · 2026-09-09
"""The five new retrieval styles (0065 §3.3), scaffold-first — the house
method: deterministic, law-tested, conformance-green from birth, each gaining
its mind through the Stable when one saddles (and confessing until then).

Every composition here is built from machinery that already stands — the
projection, the knife, the graph law, the other rows — and reads its numbers
from the variant registry's craft (`variants.config_for`): the knobs the
Workshop turns finally take effect where the work happens.

- **hierarchical** — a hit from a long document carries its SECTION, not just
  its chunk: the tree law (sp2's `chunklaw.tree_for`) climbs from the best
  chunk to its parent span, so the answer stands in its own context.
- **reasoning-first** — think before looking: a deterministic retrieval PLAN
  (the ask split on its seams), landed as a signed record where a seat
  stands, then targeted retrieves per step — an evidence pack, auditable.
- **memory-augmented** — remember first: the chronicle's own recent words
  expand the ask before external retrieval (the worldline substrate arrives
  with dive 0070; this scaffold reads the chronicle lane that already
  projects).
- **hyde** — search by the imagined answer: the best seed's text becomes the
  hypothesis and the shelf is searched by ITS shape (pseudo-relevance
  feedback — the honest deterministic stand-in until a drafting mind
  saddles).
- **corrective** — check the catch before answering: a top hit under the
  faithfulness floor triggers a visible second look with the ask expanded by
  what the first look found; a served correction says so on every hit.
"""
from __future__ import annotations

import re

from . import chunklaw, graphlaw, rivals, stacks, variants
from .node import make_memory


def _cfg(node, short: str) -> dict:
    return variants.config_for(node, short)


# ---------------------------------------------------------------- hierarchical

def hierarchical_retrieve(node, query: str, k: int = 4) -> list[dict]:
    """Best chunks first, then each hit CLIMBS to its section: the tree law
    over the record's own derived text — a long document answers from the
    right floor of the building."""
    cfg = _cfg(node, "hierarchical")
    k = int(cfg.get("k", k))
    pol = stacks._chunking(node)
    sup = stacks.superseded_of(node)
    hits = stacks.retrieve(stacks.project(node), query, k)
    out = []
    for h in hits:
        r = node.records.get(h["ref"])
        d = stacks.derived_text(node, h["ref"], r, sup) if r else None
        if d is None:
            out.append(h)
            continue
        lane, text, doc, trust, state, when = d
        spans = stacks.lane_spans(lane, text, pol)
        rows = [{"seq": i, "span": [s0, e0], "lane": lane}
                for i, (s0, e0) in enumerate(spans)]
        tree = chunklaw.tree_for(rows, levels=int(cfg.get("levels", 2)))
        parent = next((t for t in tree if t["level"] == 1
                       and t["span"][0] <= h["at"] < t["span"][1]), None)
        if parent:
            s0, e0 = parent["span"]
            out.append({**h, "text": text[s0:e0][:800],
                        "section": [s0, e0]})
        else:
            out.append(h)     # a short text has no tree — the chunk stands
    return out


# ---------------------------------------------------------------- reasoning-first

def reasoning_retrieve(node, query: str, k: int = 4) -> list[dict]:
    """Decompose → PLAN (a signed record where a seat stands) → targeted
    retrieves per step → the evidence pack. The plan is the audit: which
    sub-asks were run, in what order, each hit naming its step."""
    cfg = _cfg(node, "reasoning-first")
    k = int(cfg.get("k", k))
    steps = [p.strip() for p in re.split(r",| and | then | versus |\?",
                                         (query or "").lower()) if p.strip()]
    steps = steps[:max(1, int(cfg.get("max_steps", 3)))] or [query]
    plan_ref = None
    if getattr(node, "_me", None) and getattr(node, "_kp", None):
        rec = make_memory(node._me, node._kp, node.scope,
                          {"retrieval_plan": {"ask": (query or "")[:200],
                                              "steps": steps,
                                              "style": "reasoning-first"}},
                          kind="episodic", tags=["retrieval-plan"])
        plan_ref = node.write(rec)
    proj = stacks.project(node)
    merged: dict = {}
    per = max(1, k // len(steps))
    for i, s in enumerate(steps):
        for h in stacks.retrieve(proj, s, k=per + 1):
            key = h["ref"] + h["text"][:24]
            e = merged.setdefault(key, {**h, "score": 0.0,
                                        "step": f"{i + 1}/{len(steps)}"})
            e["score"] = round(e["score"] + h["score"], 4)
    out = sorted(merged.values(), key=lambda h: -h["score"])[:k]
    for h in out:
        if plan_ref:
            h["plan"] = plan_ref     # a WHOLE ref — the audit door opens
        else:
            h["plan_note"] = "plan unrecorded — no seat on this node"
    return out


# ---------------------------------------------------------------- memory-augmented

def memory_retrieve(node, query: str, k: int = 4) -> list[dict]:
    """Remember first: the chronicle lane's recent words expand the ask, then
    the shelf answers the EXPANDED ask — follow-ups stop starting from zero.
    (The conversation-worldline substrate arrives with 0070; the chronicle
    is the memory that already projects.)"""
    cfg = _cfg(node, "memory-augmented")
    k = int(cfg.get("k", k))
    proj = stacks.project(node)
    chron = [c for c in proj["chunks"] if c.get("when")]
    mem = stacks.retrieve({"chunks": chron, "flavor": "memory"}, query,
                          k=int(cfg.get("memory_k", 3))) if chron else []
    qt = set(graphlaw.terms(query))
    added = []
    for m in mem:
        for t in graphlaw.terms(m["text"]):
            if t not in qt and t not in added:
                added.append(t)
            if len(added) >= 4:
                break
        if len(added) >= 4:
            break
    q2 = query + (" " + " ".join(added) if added else "")
    hits = stacks.retrieve(proj, q2, k)
    for h in hits:
        if added:
            h["memory"] = " ".join(added)   # what remembering contributed
    return hits


# ---------------------------------------------------------------- hyde

def hyde_retrieve(node, query: str, k: int = 4) -> list[dict]:
    """Search by the imagined answer: the strongest seed's text stands in for
    the hypothesis a drafting mind will one day write, and the shelf is
    searched by THAT shape — vague questions find precise neighbors."""
    cfg = _cfg(node, "hyde")
    k = int(cfg.get("k", k))
    proj = stacks.project(node)
    seeds = stacks.retrieve(proj, query, k=max(1, int(cfg.get("hypotheses", 1))))
    if not seeds:
        return []
    hypothesis = " ".join(s["text"] for s in seeds)
    seen = {s["ref"] + s["text"][:24] for s in seeds}
    hits = [h for h in stacks.retrieve(proj, hypothesis, k=k + len(seeds))
            if h["ref"] + h["text"][:24] not in seen][:k]
    for h in hits:
        h["hypothesis"] = hypothesis[:80]   # what the search imagined
    return hits or seeds[:k]


# ---------------------------------------------------------------- corrective

def corrective_retrieve(node, query: str, k: int = 4) -> list[dict]:
    """Check the catch: a top hit under the faithfulness floor earns a
    visible second look — the ask expanded by what the first look found,
    re-run through the precision row; a served correction says so."""
    cfg = _cfg(node, "corrective")
    k = int(cfg.get("k", k))
    floor = float(cfg.get("faithfulness_floor", 0.5))
    proj = stacks.project(node)
    first = stacks.retrieve(proj, query, k)
    qt = set(graphlaw.terms(query))
    def faith(hits):
        if not hits or not qt:
            return 0.0
        return len(qt & set(graphlaw.terms(hits[0]["text"]))) / len(qt)
    if faith(first) >= floor or int(cfg.get("max_retries", 1)) < 1:
        return first
    expand = " ".join(list(qt) + graphlaw.terms(" ".join(
        h["text"] for h in first[:1]))[:4])
    second = rivals.rerank_retrieve(proj, expand or query, k)
    chosen = second if faith(second) > faith(first) else first
    corrected = chosen is second
    for h in chosen:
        h["corrected"] = corrected      # the second look is never a secret
    return chosen


RETRIEVERS = {
    "hierarchical": lambda n, q, k=4: hierarchical_retrieve(n, q, k),
    "reasoning-first": lambda n, q, k=4: reasoning_retrieve(n, q, k),
    "memory-augmented": lambda n, q, k=4: memory_retrieve(n, q, k),
    "hyde": lambda n, q, k=4: hyde_retrieve(n, q, k),
    "corrective": lambda n, q, k=4: corrective_retrieve(n, q, k),
}
