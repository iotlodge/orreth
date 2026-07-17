# PROVENANCE: authored by Fable 5 (claude-fable-5), 2026-07-14 — 0034 sp3, the Mirror
"""The Mirror (0034 §7 sp3 — JB's 2026-07-13 seed, the review's third
convergence): the assessment flow over Human↔Resident audiences already on
the record. It looks at how the person and their residents actually talk, and
updates BOTH sides of the glass:

  · the human's PROFILE gains observations — untrusted, evidenced (0025):
    what the person keeps asking, what they return to. Their memory, noticed.
  · the residents' ASSETS gain friction evidence — grace's stream (0031 §4):
    where the conversations failed the person, the smith's next beat must read.

The INTEROPERABILITY PROFILE is its ledger: one worldline per resident, the
relationship measured sweep by sweep.

The 0005 law is absolute: ASSESSOR ≠ ASSESSED. The Mirror is its own self —
its own keypair, its own DID — with no parlor seat and no voice; it authors
every assessment and is the subject of none, and it never reads a record it
authored (a mirror that assesses its own reflections is a hall of mirrors).
Exchanges answered under safer mode (0034 §4) were never written — the Mirror
honestly cannot see them; consent bounds the reflection too.

The sorting was identity and counting alone until 0022 Phase 2 landed the
meaning axis (Phase E): `assess` now takes an optional `meaning` module and
clusters differently-worded asks that mean the same thing before counting
repeats — and when the axis is dark it degrades to identity, exactly the v0
behavior, honestly kept."""
from __future__ import annotations

import re

from .node import make_memory

# words too common to be an interest — the sorting stays legible, not clever
_STOP = {"what", "where", "when", "does", "this", "that", "have", "with",
         "about", "your", "know", "show", "tell", "the", "and", "you", "how",
         "who", "did", "them", "then", "there", "here", "from", "into",
         "please", "could", "would", "will", "want", "need", "find", "them"}

# the honest shapes of an unmet ask — friction is counted, never judged
_EMPTY = ("nothing held", "nothing gathered", "no serving", "nothing on the",
          "the desk is empty", "no domains yet", "no one by the name",
          "nothing waiting", "a blank page")


def norm_ask(text: str) -> str:
    """One ask, one identity: case, punctuation, and whitespace folded away."""
    return re.sub(r"[^a-z0-9 ]+", "", (text or "").lower()).strip()


def assess(audiences: list[dict], *, mirror_did: str = "",
           meaning=None) -> dict:
    """The sweep's sorting, pure: per resident — exchanges counted, repeated
    asks found (the same question returning is the signal continuity care
    runs on), recurring words surfaced, unmet replies tallied as friction.
    With the meaning axis (0022 Phase 2), asks that MEAN the same thing are
    one ask however they are worded — the most-asked phrasing speaks for the
    cluster. Rows the Mirror itself authored are ignored (0005).
    audiences: [{ref, resident, asked, reply, author?}]."""
    per: dict[str, dict] = {}
    for a in audiences:
        if mirror_did and a.get("author") == mirror_did:
            continue                          # never its own reflection
        name = str(a.get("resident") or "?")
        row = per.setdefault(name, {"exchanges": 0, "asks": {}, "words": {},
                                    "friction": [], "refs": []})
        row["exchanges"] += 1
        row["refs"].append(a.get("ref", ""))
        ask = norm_ask(a.get("asked", ""))
        if ask:
            row["asks"][ask] = row["asks"].get(ask, 0) + 1
            for w in set(ask.split()):
                if len(w) >= 4 and w not in _STOP:
                    row["words"][w] = row["words"].get(w, 0) + 1
        reply = str(a.get("reply") or "").lower()
        if any(m in reply for m in _EMPTY):
            row["friction"].append(a.get("ref", ""))
    out = {}
    for name, row in per.items():
        asks = row["asks"]
        if meaning is not None and len(asks) > 1:
            keys = list(asks)
            merged: dict[str, int] = {}
            for c in meaning.repeats_by_meaning(keys, tau=0.75):
                rep = max((keys[i] for i in c), key=lambda a: asks[a])
                merged[rep] = sum(asks[keys[i]] for i in c)
            asks = merged
        out[name] = {
            "exchanges": row["exchanges"],
            "repeats": sorted(((a, n) for a, n in asks.items() if n >= 2),
                              key=lambda x: -x[1]),
            "topics": sorted(((w, n) for w, n in row["words"].items() if n >= 3),
                             key=lambda x: -x[1]),
            "friction": [r for r in row["friction"] if r],
            "refs": [r for r in row["refs"] if r],
        }
    return out


def observations(name: str, stats: dict) -> list[str]:
    """The profile strokes a sweep earns — plain sentences, each one hedgeable
    by the label canon (they enter UNTRUSTED, 0025; the human corroborates or
    withdraws — their portrait, their word)."""
    out = []
    for ask, n in stats.get("repeats", [])[:3]:
        out.append(f"asked {name} “{ask[:60]}” {n} times this period — "
                   "may want this remembered or resolved")
    for w, n in stats.get("topics", [])[:3]:
        out.append(f"returns often to “{w}” with {name} ({n} mentions)")
    return out


def friction_note(name: str, stats: dict) -> str | None:
    """The smith's evidence when the room failed the person — a count and the
    plainest sentence, never a verdict (the Mirror marks; grace proposes;
    humans decide)."""
    n = len(stats.get("friction", []))
    if not n:
        return None
    return (f"{n} of {stats.get('exchanges', 0)} exchange(s) with {name} came "
            "back empty this period — the person asked for what the floor "
            "does not hold")


def make_interop(agent: dict, kp, scope: str, resident: str, stats: dict, *,
                 window: dict, prev: str | None = None) -> dict:
    """The interoperability profile (0034 §7 sp3): the relationship's ledger —
    one worldline per resident, a sibling per sweep, every number citing the
    audiences it was read from. The Mirror authors; the resident never
    self-reports its own rapport (0005)."""
    body = {"interop": {
        "resident": resident,
        "exchanges": stats.get("exchanges", 0),
        "repeats": [{"ask": a[:80], "times": n}
                    for a, n in stats.get("repeats", [])[:5]],
        "topics": [{"word": w, "mentions": n}
                   for w, n in stats.get("topics", [])[:5]],
        "friction": len(stats.get("friction", [])),
        "evidence": [r for r in stats.get("refs", [])][:12],
        "window": dict(window),
    }}
    rec = make_memory(agent, kp, scope, body, kind="semantic",
                      tags=["mirror", f"interop-{resident}"])
    if prev:
        rec["derived_from"] = [prev]
    return rec


def interop_heads(rows: list[dict]) -> list[dict]:
    """Current head per resident worldline from (id, interop, derived_from,
    at)-shaped rows, oldest first — the 0032 idiom, once more."""
    superseded = {d for r in rows for d in r.get("derived_from") or []}
    return [{"id": r["id"], **r["interop"]} for r in rows
            if r["id"] not in superseded]
