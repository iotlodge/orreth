# PROVENANCE: Fable 5 (claude-fable-5) — 0038, the Stacks · 2026-07-22
"""The Stacks (0038) spoonful 4, part 2: the tournament.

One question asked seven ways, the receipts side by side — then the science
grades every pass (0033: recall fidelity · context efficiency · information
gain, all deterministic), the standings rank the rows (0005: mean + n, floors
flag never average away), and the first PROMOTION is proposed from receipts —
a winner named in a routing-standard revision that rides the lanes to the
human's gate. Nothing promotes itself; the tournament argues, the human signs.

The last three flows arrive honest: multimodal reads captions (the real eye
still awaits a vision mind at ada's gate — 0029's parked-eye truth, kept);
the router chooses tactics WITHIN the row by shape; the swarm decomposes,
fans to the other rows, and recomposes one cited answer. The swarm's fan-out
is synchronous in the sim — the record-driven seat progression (0023's async
self-dialog) remains honestly deferred, on the record.
"""
from __future__ import annotations

import re

from . import dispatcher, rivals, stacks

FLAVORS = ("naive", "rerank", "graph", "hybrid", "multimodal", "router", "swarm")


# ---------------------------------------------------------------- the last three

def multimodal_retrieve(node, query: str, k: int = 4) -> list[dict]:
    """The eye's honest stand-in: media-tagged documents searched by caption.
    A real vision mind saddles at ada's gate (0029); until then the row serves
    captions and says so."""
    proj = stacks.project(node)
    media = [c for c in proj["chunks"]
             if any(str(t).startswith("media") for t in
                    (node.records.get(c["ref"], {}).get("tags") or []))]
    if not media:
        return []
    return stacks.retrieve({"chunks": media, "flavor": "multimodal"}, query, k)


def router_retrieve(node, query: str, k: int = 4) -> list[dict]:
    """Strategy WITHIN the row: the router reads its own ask's shape and picks
    a tactic — graph for the bound, rerank for the exact, naive otherwise."""
    shapes = dispatcher.classify(query)
    tactic = ("graph" if "relational" in shapes else
              "rerank" if "precision" in shapes else "naive")
    hits = rivals.RETRIEVERS[tactic](node, query, k)
    for h in hits:
        h["tactic"] = tactic
    return hits


def swarm_retrieve(node, query: str, k: int = 4) -> list[dict]:
    """Decompose · fan · recompose: split the ask on its seams, hand each
    sub-ask to the row the Dispatcher's shapes suggest, merge the receipts —
    every claim still cited. (Synchronous fan-out in the sim; the async seat
    progression is deferred, on the record.)"""
    parts = [p.strip() for p in re.split(r",| and | versus | vs\.? |\?",
                                         (query or "").lower()) if p.strip()]
    parts = parts[:4] or [query]
    merged: dict = {}
    for part in parts:
        for h in router_retrieve(node, part, k=2):
            key = h["ref"] + h["text"][:24]
            e = merged.setdefault(key, {**h, "score": 0.0, "parts": []})
            e["score"] = round(e["score"] + h["score"], 4)
            e["parts"].append(part[:32])
    return sorted(merged.values(), key=lambda h: -h["score"])[:k]


ALL_RETRIEVERS = {**rivals.RETRIEVERS,
                  "multimodal": lambda n, q, k=4: multimodal_retrieve(n, q, k),
                  "router": lambda n, q, k=4: router_retrieve(n, q, k),
                  "swarm": lambda n, q, k=4: swarm_retrieve(n, q, k)}


def answer_as(node, flavor: str, query: str) -> dict:
    """One door for all SEVEN rows now — the tournament's contestants."""
    if flavor in rivals.RETRIEVERS:
        return rivals.answer_as(node, flavor, query)
    hits = ALL_RETRIEVERS[flavor](node, query)
    stacks.record_recalls(node, hits)   # the flow rows warm the tap too (sp1)
    if not hits:
        note = (" (no media on the shelf — the eye awaits a vision mind, 0029)"
                if flavor == "multimodal" else "")
        return {"answer": "the stacks hold nothing on this — an honest unknown"
                          + note, "citations": [], "flavor": flavor}
    lines = [f"“{h['text'][:140].strip()}” [{h['ref'][:18]}…]" for h in hits[:2]]
    cites = [{"ref": h["ref"], "doc": h["doc"], "score": h["score"]}
             for h in hits]
    if hits[0]["score"] < rivals.CONFESSION_FLOOR:   # the noise law (0053 sp3)
        return {"answer": "the shelves hold no strong answer to this — the "
                          "NEAREST records, named as nearest and not as "
                          "answers: " + " · ".join(lines),
                "flavor": flavor, "citations": cites, "confessed": True}
    return {"answer": " · ".join(lines), "flavor": flavor,
            "citations": cites}


# ---------------------------------------------------------------- the science (0033)

def grade(node, query: str, a: dict) -> dict:
    """Deterministic grading, 0033's axes made runnable:
    recall fidelity — how much of the ask the cited text actually covers;
    context efficiency — signal carried per character retrieved;
    information gain — distinct ask-terms the answer resolves beyond noise."""
    qt = set(rivals._terms(query))
    if not a["citations"] or not qt:
        return {"fidelity": 0.0, "efficiency": 0.0, "gain": 0.0, "score": 0.0}
    cited_text = " ".join(c.get("doc", "") for c in a["citations"]) + " " + a["answer"]
    ct = set(rivals._terms(cited_text))
    fidelity = len(qt & ct) / len(qt)
    efficiency = round(min(1.0, 220 / max(1, len(a["answer"]))), 4)
    gain = len(qt & ct) / max(1, len(ct)) * 3
    score = round(0.5 * fidelity + 0.2 * efficiency + 0.3 * min(1.0, gain), 4)
    return {"fidelity": round(fidelity, 4), "efficiency": efficiency,
            "gain": round(min(1.0, gain), 4), "score": score}


# ---------------------------------------------------------------- the standings (0005)

def run(node, questions: list[str]) -> dict:
    """THE TOURNAMENT: every question through every row, every pass graded,
    the standings composed — mean + n, floors flagged (a row that ever
    answered uncited when rivals cited is marked, never averaged away)."""
    rounds = []
    tally: dict = {f: {"n": 0, "total": 0.0, "uncited": 0} for f in FLAVORS}
    for q in questions:
        entries = []
        for f in FLAVORS:
            a = answer_as(node, f, q)
            g = grade(node, q, a)
            tally[f]["n"] += 1
            tally[f]["total"] += g["score"]
            if not a["citations"]:
                tally[f]["uncited"] += 1
            entries.append({"flavor": f, "graded": g,
                            "cited": len(a["citations"]),
                            "answer": a["answer"][:160]})
        entries.sort(key=lambda e: -e["graded"]["score"])
        rounds.append({"question": q, "entries": entries,
                       "winner": entries[0]["flavor"]})
    standings = sorted(
        ({"flavor": f, "n": t["n"],
          "mean": round(t["total"] / max(1, t["n"]), 4),
          "floors": ([f"{t['uncited']} uncited round(s)"] if t["uncited"]
                     else [])}
         for f, t in tally.items()),
        key=lambda s: -s["mean"])
    return {"rounds": rounds, "standings": standings,
            "champion": standings[0]["flavor"]}


def promotion_proposal(result: dict) -> dict:
    """The first promotion, ARGUED from receipts — never enacted here: a
    routing-standard revision naming the champion as default and growing the
    built list to every row that scored. It rides the lanes; the human signs
    (locked 2026-07-22: promotion = a named strategy in the standard)."""
    std = dict(dispatcher.STANDARD_V1)
    champion = result["champion"]
    scored = [s["flavor"] for s in result["standings"] if s["mean"] > 0]
    return {"version": "2-proposed", "rules": std["rules"],
            "default": champion, "built": list(FLAVORS),
            "evidence": {"champion": champion,
                         "standings": result["standings"],
                         "rounds": len(result["rounds"]),
                         "note": f"{champion} led {len(scored)} scoring row(s) "
                                 "across the tournament — proposal only; "
                                 "consequence waits at the gate (0012)"}}
