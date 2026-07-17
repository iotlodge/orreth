# PROVENANCE: authored by Fable 5 (claude-fable-5), 2026-07-17 — 0022 Phase 2, the meaning axis (Phase E)
"""The meaning axis (0022 §4 — Phase E of the build order, built LAST so it
consumes hard coordinates and aperture scores instead of being rebuilt for
them). Retrieval grows its second sense: not just WHEN and WHAT-TAGGED a
memory is, but what it MEANS.

The laws it lands under:
  · bytes-local (JB's 0022 §10 lock): embeddings run in-process on this node
    via fastembed (ONNX, CPU) — record bytes never leave for indexing. When
    the library or model is unavailable, every consumer DEGRADES TO IDENTITY
    honestly — the axis is an upgrade, never a dependency.
  · hybrid is one fusion (0022 §4): lexical rank × vector rank × recency
    rank (× coordinate kinship × aperture proximity, when given), fused with
    weighted Reciprocal Rank Fusion. Trust and scope stay filters.
  · the trust-weighted rerank is ours alone: the industry ranks by
    relevance; Orreth ranks by STANDING — and `recalled` ranks DEAD,
    surfaced only when the query asks for the dead, and then labeled.

It discharges three stated waits: the reactivation rerank (0031 §5), cross-
source contradiction beyond identity (0032 §3 — meaning-v1: same subject by
cosine, values that disagree by the numbers; the general case stays honestly
deferred), and the Mirror's meaning-aware assessor (0034 sp3)."""
from __future__ import annotations

import math
import os
import re

# ---------------------------------------------------------------- the embedder

_EMBEDDER = None


def embedder():
    """Lazy, local-only, honest: fastembed's small English model on this
    node's CPU, or None — and None means identity, never an error. The
    ORRETH_MEANING=off dial darkens the axis deliberately (a fast dev loop);
    every consumer states its degradation."""
    global _EMBEDDER
    if _EMBEDDER is None:
        if os.environ.get("ORRETH_MEANING", "").lower() in ("off", "0", "no"):
            _EMBEDDER = False
            return None
        try:
            from fastembed import TextEmbedding
            _EMBEDDER = TextEmbedding()
        except Exception:
            _EMBEDDER = False
    return _EMBEDDER or None


def embed(texts: list[str]) -> list[list[float]] | None:
    """Vectors for texts, or None when the axis is dark."""
    e = embedder()
    if e is None:
        return None
    return [list(map(float, v)) for v in e.embed(list(texts))]


def cosine(a, b) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a)) or 1.0
    nb = math.sqrt(sum(x * x for x in b)) or 1.0
    return dot / (na * nb)


# ---------------------------------------------------------------- the ranks

def _terms(text: str) -> list[str]:
    return [w for w in re.sub(r"[^a-z0-9 ]+", " ", (text or "").lower()).split()
            if len(w) >= 3]


def bm25(query: str, docs: list[str], *, k1: float = 1.5, b: float = 0.75
         ) -> list[float]:
    """The lexical rank, small-corpus honest (Okapi BM25, pure)."""
    q = _terms(query)
    toks = [_terms(d) for d in docs]
    n = len(docs) or 1
    avg = sum(len(t) for t in toks) / n or 1.0
    df: dict[str, int] = {}
    for t in toks:
        for w in set(t):
            df[w] = df.get(w, 0) + 1
    scores = []
    for t in toks:
        s = 0.0
        for w in q:
            f = t.count(w)
            if not f:
                continue
            idf = math.log(1 + (n - df.get(w, 0) + .5) / (df.get(w, 0) + .5))
            s += idf * f * (k1 + 1) / (f + k1 * (1 - b + b * len(t) / avg))
        scores.append(s)
    return scores


def rrf(rank_lists: list[list[int]], weights: list[float] | None = None,
        *, k: int = 60) -> dict[int, float]:
    """Weighted Reciprocal Rank Fusion (0022 §4): each list contributes
    w/(k+rank); an index absent from a list contributes nothing from it."""
    weights = weights or [1.0] * len(rank_lists)
    fused: dict[int, float] = {}
    for ranks, w in zip(rank_lists, weights):
        for pos, idx in enumerate(ranks):
            fused[idx] = fused.get(idx, 0.0) + w / (k + pos + 1)
    return fused


# the trust-weighted rerank: standing, not just relevance. `recalled` is DEAD.
STANDING = {"verified": 1.0, "trusted": 1.0, "human-confirmed": 1.0,
            "corroborated": .9, "promoted": .9, "distilled": .8,
            "untrusted": .6, "quarantined": .6, "distilled-raw-expired": .5,
            "investigating": .35, "recalled": 0.0}


def standing_weight(state: str) -> float:
    return STANDING.get(state, .6)


def _rank_of(scores: list[float]) -> list[int]:
    """Indexes ordered best-first, zero-scored entries left out."""
    return [i for i, _ in sorted(enumerate(scores), key=lambda x: -x[1])
            if scores[i] > 0]


def meaning_search(query: str, rows: list[dict], *, k: int = 5,
                   coordinate: set | None = None,
                   aperture_refs: set | None = None,
                   include_the_dead: bool = False,
                   vecs: list | None = None) -> list[dict]:
    """The hybrid (0022 §4): rows are {id, text, state, at?, tags?}. Fuses
    the vector rank (when the axis is lit), the lexical rank, the recency
    rank — and, when given, COORDINATE KINSHIP (rows sharing of:/via: tags
    with the asking work) and APERTURE PROXIMITY (rows already pinned by the
    active aperture) — then multiplies by STANDING. The dead (`recalled`)
    are excluded unless asked for, and then labeled. Every hit names why."""
    if not rows:
        return []
    texts = [str(r.get("text") or "") for r in rows]
    lists, weights, senses = [], [], []
    if vecs is None:
        allv = embed([query] + texts)
        qv, vecs = (allv[0], allv[1:]) if allv else (None, None)
    else:
        qv = (embed([query]) or [None])[0]
    if qv is not None and vecs is not None:
        sim = [cosine(qv, v) for v in vecs]
        lists.append(_rank_of(sim)); weights.append(1.0); senses.append("meaning")
    lex = bm25(query, texts)
    lists.append(_rank_of(lex)); weights.append(.8); senses.append("words")
    ats = [str(r.get("at") or "") for r in rows]
    lists.append([i for i, _ in sorted(enumerate(ats), key=lambda x: x[1],
                                       reverse=True) if ats[i]])
    weights.append(.3); senses.append("recency")
    if coordinate:
        kin = [len(coordinate & set(r.get("tags") or [])) for r in rows]
        lists.append(_rank_of([float(x) for x in kin]))
        weights.append(.6); senses.append("coordinate kinship")
    if aperture_refs:
        near = [1.0 if r.get("id") in aperture_refs else 0.0 for r in rows]
        lists.append(_rank_of(near))
        weights.append(.6); senses.append("aperture proximity")
    fused = rrf(lists, weights)
    out = []
    for i, base in fused.items():
        state = str(rows[i].get("state") or "")
        w = standing_weight(state)
        if w == 0.0 and not include_the_dead:
            continue                          # recalled ranks dead
        out.append({**rows[i], "score": base * (w if w else .0001),
                    "standing": w,
                    "why": " × ".join(senses)
                           + (f" × standing({state or '?'}={w})"),
                    **({"dead": True} if w == 0.0 else {})})
    out.sort(key=lambda h: -h["score"])
    return out[:k]


# ---------------------------------------------------------------- the consumers

def reactivate(query: str, rows: list[dict], aperture_refs: set,
               *, k: int = 5) -> list[dict]:
    """The reactivation rerank (0031 §5's stated wait, ended): when doubt
    lifts or fresh work opens, which knowledge to resurface FIRST — the
    hybrid, with the active aperture's pins pulling their neighbors up."""
    return meaning_search(query, rows, k=k, aperture_refs=aperture_refs)


_NUM = re.compile(r"-?\d[\d,]*\.?\d*")


def _numbers(text: str) -> list[str]:
    return [n.replace(",", "") for n in _NUM.findall(text or "")]


def contradiction_pairs(claims: list[dict], *, tau: float = 0.60,
                        vecs: list | None = None) -> list[dict]:
    """Cross-source contradiction, meaning-v1 (0032 §3's honest deferral,
    discharged as far as honesty allows): two claims from DIFFERENT sources
    whose texts share a subject (cosine ≥ tau — or identical normalized text
    when the axis is dark) but whose NUMBERS disagree. Numbers first because
    numbers are checkable; the general paraphrase-contradiction case stays
    deferred, stated plainly. claims: [{id, source, text}]."""
    if len(claims) < 2:
        return []
    texts = [str(c.get("text") or "") for c in claims]
    if vecs is None:
        vecs = embed(texts)
    pairs = []
    for i in range(len(claims)):
        for j in range(i + 1, len(claims)):
            if claims[i].get("source") == claims[j].get("source"):
                continue                      # one voice cannot contradict itself here
            ni, nj = _numbers(texts[i]), _numbers(texts[j])
            if not ni or not nj or ni == nj:
                continue                      # v1 speaks only where numbers disagree
            same_subject = (cosine(vecs[i], vecs[j]) >= tau if vecs
                            else _terms(texts[i]) == _terms(texts[j]))
            if same_subject:
                pairs.append({"a": claims[i], "b": claims[j],
                              "why": f"same subject by meaning, values "
                                     f"disagree: {ni} vs {nj}"})
    return pairs


def repeats_by_meaning(texts: list[str], *, tau: float = 0.80,
                       vecs: list | None = None) -> list[list[int]]:
    """The Mirror's meaning-aware clusters (0034 sp3's stated wait, ended):
    asks that mean the same thing though worded differently, grouped by
    cosine — greedy, order-stable, legible. Dark axis → identity clusters
    (exactly the v0 behavior, honestly kept)."""
    if vecs is None:
        vecs = embed(texts)
    clusters: list[list[int]] = []
    if vecs is None:
        seen: dict[str, int] = {}
        for i, t in enumerate(texts):
            key = re.sub(r"[^a-z0-9 ]+", "", (t or "").lower()).strip()
            if key in seen:
                clusters[seen[key]].append(i)
            else:
                seen[key] = len(clusters)
                clusters.append([i])
        return clusters
    for i in range(len(texts)):
        for c in clusters:
            if cosine(vecs[i], vecs[c[0]]) >= tau:
                c.append(i)
                break
        else:
            clusters.append([i])
    return clusters
