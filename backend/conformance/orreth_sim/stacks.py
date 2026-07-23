# PROVENANCE: Fable 5 (claude-fable-5) — 0038, the Stacks · 2026-07-22
"""The Stacks (0038) spoonful 1: the baseline breathes.

The one-truth law, enforced by construction: ingestion happens ONCE through the
gateway — a signed MemoryRecord is the document's only truth. The naive stack
holds no documents; it holds a PROJECTION (chunks + vectors) derived from the
log, rebuildable and therefore disposable: tear it down, regrow it, the same
answers return. A record that leaves the log stops speaking in the projection
at the next rebuild — the purge's reach (0026), kept.

Every answer carries CITATIONS — record ids the caller may walk. The sim's
embedder is a deterministic bag-of-hashed-ngrams (honest, local, reproducible);
the wire rides 0022 Phase 2's fastembed under the same contract.

The eco assets (chunking policy · embedding standard · prompt template) are
versioned data on the shelf (0031) — the commonality, factored UP; a field is
its delta, and naive's delta is deliberately NOTHING: the baseline control
every rival must beat on the record (locked 2026-07-22).
"""
from __future__ import annotations

import json
import math
import re

from . import crypto, improver
from .node import make_memory

# ---------------------------------------------------------------- the eco assets
ECO_ASSETS = {
    "stacks-chunking": {"chunk_chars": 280, "overlap_chars": 40,
                        "note": "the shared knife — every stack cuts alike"},
    "stacks-embedding": {"dim": 512, "method": "hashed-ngram (sim) / fastembed (wire)",
                         "note": "one standard, every projection comparable"},
    "stacks-prompt": {"template": "Answer ONLY from the cited passages. Cite "
                                  "every claim by [ref]. Unknown → say so.",
                      "note": "the shared voice — grounded, cited, honest"},
}


def plant_eco_assets(node, librarian: dict, librarian_kp) -> list[str]:
    """The commonality, factored up (0038 §2): three assets at the eco scope,
    versioned on the shelf under the librarian's signature — grace may propose
    revisions; every field inherits by the cascade, none carries its own copy."""
    out = []
    for name, profile in ECO_ASSETS.items():
        if improver.active_asset(node, name):
            continue                          # genesis plants once; siblings later
        rec = improver.make_asset(librarian, librarian_kp, node.scope,
                                  name=name, profile=profile)
        out.append(node.write(rec))
    return out


def _chunking(node) -> dict:
    row = improver.active_asset(node, "stacks-chunking")
    return improver._profile_of(row[1]) if row else ECO_ASSETS["stacks-chunking"]


# ---------------------------------------------------------------- the one truth

def ingest(node, librarian: dict, librarian_kp, name: str, text: str) -> str:
    """ONCE, through the gateway: the document lands as a signed MemoryRecord —
    quarantine, provenance, and the purge all apply because it is memory like
    any other. No stack ever holds a second copy of the truth."""
    if not (text or "").strip():
        raise ValueError("an empty document is not a document")
    body = {"stacks_document": {"name": name, "text": text}}
    rec = make_memory(librarian, librarian_kp, node.scope, body, kind="semantic",
                      tags=["stacks", "document", name])
    return node.write(rec)


# ---------------------------------------------------------------- the projection

def _embed(text: str, dim: int = 512) -> list[float]:
    """Deterministic sim embedding: hashed word-and-bigram bag, L2-normalized.
    Honest and reproducible — the wire swaps in fastembed under the same shape."""
    v = [0.0] * dim
    words = re.findall(r"[a-z0-9]+", (text or "").lower())
    for i, w in enumerate(words):
        for tok in (w, " ".join(words[i:i + 2])):
            h = int(crypto.content_hash({"t": tok})[7:23], 16)
            v[h % dim] += 1.0
    n = math.sqrt(sum(x * x for x in v)) or 1.0
    return [x / n for x in v]


# the trust law, carried into every projection (0038 — "the rows meet the real
# memory", JB-locked 2026-07-22): gathered knowledge joins the stacks WEARING
# its state — corroborated speaks fully, quarantined speaks dampened and
# labeled, investigating barely, and RECALLED IS DEAD (0022's law, kept)
_TRUST = {"corroborated": 1.0, "promoted": 1.0, "untrusted": 0.4,
          "investigating": 0.15, "recalled": 0.0}


def project(node) -> dict:
    """The stack's whole body: chunks + vectors DERIVED from the log —
    shelved documents AND the librarian's gathered knowledge (head versions
    only, trust-weighted). Rebuildable, therefore disposable — this function
    IS the field."""
    pol = _chunking(node)
    size, ov = int(pol["chunk_chars"]), int(pol["overlap_chars"])
    chunks = []
    superseded: set = set()
    for r in node.records.values():
        if "knowledge" in (r.get("tags") or []):
            superseded.update(r.get("derived_from") or [])
    from . import canon
    for rid, r in sorted(node.records.items()):
        # THE PRIVACY FLOOR (0039 §7, locked 2026-07-23): floors apply BEFORE
        # any projection sees a byte — a sovereign record never chunks, no
        # matter what else it wears
        if not canon.retrievable(node, r):
            continue
        tags = r.get("tags") or []
        if "document" in tags and "stacks" in tags:
            doc = json.loads(crypto._b64d(r["body"]).decode()).get("stacks_document") or {}
            text, name = doc.get("text", ""), doc.get("name", "?")
            i = 0
            while i < len(text):
                piece = text[i:i + size]
                chunks.append({"ref": rid, "doc": name, "at": i, "text": piece,
                               "vec": _embed(piece), "trust": 1.0})
                i += max(1, size - ov)
        elif "knowledge" in tags and rid not in superseded:
            b = json.loads(crypto._b64d(r["body"]).decode())
            # both dialects: the sim's {claim, category} and the wire's
            # gathered {knowledge, intent} — one law over both
            claim = b.get("claim") or b.get("knowledge") or ""
            state = b.get("state", "untrusted")
            w = _TRUST.get(state, 0.4)
            if not claim or w <= 0:
                continue                     # recalled is DEAD — it never speaks
            src = str((b.get("source") or {}).get("did") or
                      (b.get("source") or {}).get("ref") or "?")[-16:]
            doc = f"{b.get('category') or b.get('intent') or 'knowledge'} · {src}"
            i = 0
            while i < len(claim):            # long findings meet the same knife
                piece = claim[i:i + size]
                chunks.append({"ref": rid, "doc": doc, "at": i, "text": piece,
                               "vec": _embed(piece), "trust": w, "state": state})
                i += max(1, size - ov)
    return {"flavor": "naive", "chunks": chunks, "policy": pol}


def retrieve(projection: dict, query: str, k: int = 4) -> list[dict]:
    """Cosine over the projection — the baseline: no rerank, no graph, no
    tricks. Hits carry their refs; authorization stayed at the gateway."""
    qv = _embed(query)
    scored = []
    for c in projection.get("chunks", []):
        raw = sum(a * b for a, b in zip(qv, c["vec"]))
        if raw <= 0.2:                       # the relevance floor gates on the
            continue                         # RAW match — does it speak to the ask?
        scored.append((raw * c.get("trust", 1.0), c))
    scored.sort(key=lambda x: -x[0])         # …and TRUST orders the rank: the
    # corroborated outrank the quarantined saying the same thing; recalled
    # never entered the projection at all
    return [{"ref": c["ref"], "doc": c["doc"], "at": c["at"],
             "text": c["text"], "score": round(s, 4),
             **({"state": c["state"]} if c.get("state") else {})}
            for s, c in scored[:k]]


def answer(node, projection: dict, query: str) -> dict:
    """The grounded reply: extractive in the sim (deterministic — the wire may
    voice it through a governed thought), every claim wearing its citation.
    An empty retrieval answers honestly — the prompt standard's law."""
    hits = retrieve(projection, query)
    if not hits:
        return {"answer": "the stacks hold nothing on this — an honest unknown "
                          "(the prompt standard forbids invention)",
                "citations": [], "flavor": "naive"}
    lines = [f"“{h['text'][:160].strip()}”"
             + (f" ⟨{h['state']}⟩" if h.get("state") not in (None, "corroborated",
                                                             "promoted") else "")
             + f" [{h['ref'][:18]}…]" for h in hits[:2]]
    return {"answer": " · ".join(lines), "flavor": "naive",
            "citations": [{"ref": h["ref"], "doc": h["doc"], "score": h["score"],
                           **({"state": h["state"]} if h.get("state") else {})}
                          for h in hits]}
