# PROVENANCE: Claude Fable 5 (claude-fable-5) — 0065 sp3, the graph law · 2026-09-09
"""The graph extraction law (0065 §3.4) — 0038's Shape-A promise, made one
deterministic law.

Terms are nodes; co-occurrence WITHIN ONE SPAN is an edge; and every edge
carries its witness — the record and span that bound the pair. The citation
IS the edge's provenance (the sim's graph row taught this from birth); an
edge with no witness cannot exist here by shape.

This module OWNS the term law — the rebuild's rows (`rivals`) and the
standing sweep both import it, so the two graphs can never disagree about
what a term is. The extractor is the honest scaffold: deterministic term
co-occurrence, the same walk the sim has always taken; a governed extraction
mind (real entities, typed relations) saddles later through the Stable
without changing this module's shape — the law version names the extractor,
so a smarter one re-cuts the world visibly, never silently.

The walk's one law: traversal reads ONLY within the authorized id set — a
matching edge in a record the caller's retrieve did not serve contributes
nothing, or the graph would become a second read path (refused by design).
"""
from __future__ import annotations

import hashlib
import json
import re

STOP = {"the", "a", "an", "and", "or", "of", "in", "on", "at", "to", "is",
        "are", "it", "its", "with", "for", "by", "as", "that", "this",
        "through", "between", "how", "what", "why", "when", "do", "does"}

EXTRACTOR = "co-occur-v1"        # the scaffold's name — a saddled mind bumps it


def terms(text: str) -> list[str]:
    """THE term law — one definition for rebuild, sweep, and walk alike."""
    return [w for w in re.findall(r"[a-z][a-z0-9-]+", (text or "").lower())
            if w not in STOP and len(w) > 2]


def law_hash(chunk_policy: dict) -> str:
    """The extraction law's full name: extractor version × the chunk policy
    that shapes the spans edges bind within. Either turning re-cuts the
    world, visibly."""
    raw = json.dumps({"extractor": EXTRACTOR,
                      "chunk_chars": int(chunk_policy["chunk_chars"]),
                      "overlap_chars": int(chunk_policy["overlap_chars"])},
                     sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def extract(text: str, spans: list[tuple[int, int]], lane: str,
            doc: str, trust: float) -> tuple[list[dict], list[dict]]:
    """One record's graph rows: nodes (term mentions with counts) and edges
    (within-span pairs, each carrying its witnessing span and the piece's
    hash — the same drift catch the chunk rows wear)."""
    counts: dict = {}
    edges: list[dict] = []
    for seq, (s0, e0) in enumerate(spans):
        piece = text[s0:e0]
        ts = terms(piece)
        for t in ts:
            counts[t] = counts.get(t, 0) + 1
        ph = hashlib.sha256(piece.encode()).hexdigest()[:16]
        seen: set = set()
        for i, a in enumerate(ts):
            for b in ts[i + 1:]:      # a span is small — bind all its pairs
                if a == b:
                    continue
                key = tuple(sorted((a, b)))
                if key in seen:       # one edge per pair per span — the
                    continue          # witness is the span, not the echo
                seen.add(key)
                edges.append({"a": key[0], "b": key[1], "seq": seq,
                              "span": [s0, e0], "lane": lane, "doc": doc,
                              "trust": trust, "hash": ph})
    nodes = [{"name": t, "cnt": c} for t, c in sorted(counts.items())]
    return nodes, edges


# ---- the standing book, as pure law (the plane's Postgres twin: the suite
# ---- proves the lifecycle here; the wire proves it on the rig) -------------

def put(book: dict, record_id: str, law: str, nodes: list[dict],
        edges: list[dict]) -> None:
    """One record, one law, one truth — landing replaces the record's rows."""
    book[record_id] = {"law": law, "nodes": list(nodes), "edges": list(edges)}


def evict(book: dict, record_id: str) -> int:
    """Purge reach: a shredded record's edges AND its node mentions die in
    the same breath — an entity the world only knew through that record is
    forgotten with it."""
    e = book.pop(record_id, None)
    return (len(e["nodes"]) + len(e["edges"])) if e else 0


def missing(book: dict, live_ids, law: str) -> list[str]:
    """The sweep's worklist: living records with no rows under the CURRENT
    law — the unextracted and the law-stale alike."""
    return [rid for rid in live_ids
            if book.get(rid, {}).get("law") != law]


def walk(book: dict, authorized_ids, query_terms: list[str],
         k: int = 4) -> list[dict]:
    """The walking read, inside the authorized set ONLY: an edge binding two
    of the ask's terms makes its witness a hit (score = pairs bound); a
    one-term ask falls to the edges touching that term, dampened."""
    allowed = set(authorized_ids)
    qt = [t for t in query_terms if t]
    hits: dict = {}
    for rid, entry in book.items():
        if rid not in allowed:
            continue                  # never a second read path
        for e in entry["edges"]:
            for i, a in enumerate(qt):
                for b in qt[i + 1:]:
                    if tuple(sorted((a, b))) == (e["a"], e["b"]):
                        key = (rid, e["seq"])
                        h = hits.setdefault(key, {**e, "ref": rid,
                                                  "score": 0.0,
                                                  "pair": f"{a}↔{b}"})
                        h["score"] = round(h["score"] + 1.0, 4)
    if not hits and len(qt) == 1:
        for rid, entry in book.items():
            if rid not in allowed:
                continue
            for e in entry["edges"]:
                if qt[0] in (e["a"], e["b"]):
                    hits.setdefault((rid, e["seq"]),
                                    {**e, "ref": rid, "score": 0.5,
                                     "pair": f"{e['a']}↔{e['b']}"})
    return sorted(hits.values(), key=lambda h: -h["score"])[:k]
