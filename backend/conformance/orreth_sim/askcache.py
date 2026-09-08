# PROVENANCE: Claude Fable 5 (claude-fable-5) — 0071 sp5, the ask-cache · 2026-09-08
"""The ask-cache's law (0071 §3.1, the charter's caching clause): an answer already
given may serve again — but only for the SAME words, under the SAME guardrails, on
the SAME floor, while the exchange record it came from still stands.

The cache is a PROJECTION, never a second truth (0065 §3.5's law): every entry
leans on a signed exchange record by whole ref, and an entry whose record has
left the world (purged, recalled) is dead the moment anyone looks — the caller
verifies the record read-side before serving a hit, exactly as dial bounds are
enforced read-side. Purge reaches the cache by construction, not by hooks.

Matching is SAME-WORDS today: the ask's text is canonicalized (case folded,
whitespace collapsed) and hashed with the variant, the floor, and the guardrail-set
version. Meaning-similar matching — serving one question's answer to a merely
similar question — is a named horizon, not a default: it is a correctness risk a
human must weigh, and it waits for its own lock.

A TTL of 0 is the operator's explicit closed cache (every ask answered fresh),
mirroring the traffic law's «limit 0 is the open door» idiom.
"""
from __future__ import annotations

import hashlib
import json


def key(scope: str, text: str, variant: str, guardrails_version: str) -> str:
    """The cache key: same words · same row · same floor · same guardrails.
    Text canonicalization folds case and collapses whitespace — «What is X?»
    and «what  is x?» are the same ask; «what is Y?» never is."""
    words = " ".join(str(text).split()).casefold()
    raw = json.dumps([scope, words, str(variant or "auto").casefold(),
                      str(guardrails_version)],
                     sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(raw.encode()).hexdigest()


def put(book: dict, k: str, envelope: dict, ref: str, now_s: float) -> None:
    """Remember a FRESH answer: the envelope as served, the exchange record it
    leans on (whole ref), and when. No-op without a ref — an answer with no
    record behind it has nothing to lean on and must not be replayed."""
    if not ref:
        return
    if len(book) > 2048:
        oldest = sorted(book, key=lambda x: book[x]["at"])[:len(book) // 2]
        for stale in oldest:
            del book[stale]
    book[k] = {"envelope": envelope, "ref": ref, "at": now_s, "hits": 0}


def get(book: dict, k: str, now_s: float, ttl_s: int) -> dict | None:
    """A fresh entry, or None. Staleness evicts on sight; ttl_s <= 0 is the
    closed cache. The caller still owes the read-side record-alive check
    before serving — a hit is a CANDIDATE, never yet an answer."""
    if ttl_s <= 0:
        return None
    e = book.get(k)
    if e is None:
        return None
    if now_s - e["at"] >= ttl_s:
        del book[k]
        return None
    e["hits"] += 1
    return e


def evict(book: dict, k: str) -> None:
    book.pop(k, None)


def evict_ref(book: dict, ref: str) -> int:
    """Purge reach: every entry leaning on a dead record dies with it."""
    doomed = [k for k, e in book.items() if e["ref"] == ref]
    for k in doomed:
        del book[k]
    return len(doomed)


def sweep(book: dict, now_s: float, ttl_s: int) -> int:
    """Forget the stale; keep the living."""
    doomed = [k for k, e in book.items() if now_s - e["at"] >= ttl_s]
    for k in doomed:
        del book[k]
    return len(doomed)
