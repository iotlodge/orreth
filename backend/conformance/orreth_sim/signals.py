# PROVENANCE: Claude Fable 5 (claude-fable-5) — 0066 sp3, the signal vector · 2026-09-09
"""The signal vector (0066 §3.3) — signals are data; the reward function is law.

Every completed ask accretes signals: the cheap bench's rung scores computed
the moment the answer exists (deterministic PROXIES, named as such —
retrieval · faithfulness · answer · coverage), latency and context cost from
the act itself, then the richer tier as it arrives — vera's governed verdicts
and the human's thumb, each joined to the exchange by the refs they already
carry. Nothing here is a second store: `vector_for` is a walk over signed
records.

THE REWARD IS GOVERNED ARITHMETIC: the combining weights live in the routing
standard (changing them is a gated act like any rule change), genesis serves
when a standing world's shelf standard predates them, and history is
re-scorable under any future weights because the signals never left the
records.

L3 IS LAW HERE: **a thumb is never a reward scalar.** It rides the vector as
the human's word — a 👎 marks the sample VETOED (the standings will refuse
it, never average it) and feeds calibration; it never tilts the sum. The
research's canonical failure — reward-weighted thumbs breeding sycophancy —
is refused by name, in code.
"""
from __future__ import annotations

import re

from . import graphlaw

# genesis — the same block rides STANDARD_V1["weights"]; the shelf standard's
# word wins when one stands (a GATED change, like every rule)
WEIGHTS_GENESIS = {"retrieval": 0.3, "faithfulness": 0.3,
                   "answer": 0.25, "coverage": 0.15}

_QUOTE = re.compile(r"[“\"]([^”\"]+)[”\"]")


def bench(query: str, answer: dict, k: int = 4) -> dict:
    """The cheap bench — tier one, deterministic, at answer time. Every score
    is a NAMED PROXY in [0, 1]; vera's governed tier refines what these can
    only approximate:
    - retrieval: how strongly the best citation matched (its own score);
    - faithfulness: how much of the reply stands inside quoted record text;
    - answer: the standing science (0033's fidelity·efficiency·gain fold);
    - coverage: how much of the asked-for depth the citations filled."""
    from . import tournament
    cites = answer.get("citations") or []
    reply = str(answer.get("answer") or "")
    retrieval = max(0.0, min(1.0, float(cites[0]["score"]))) if cites else 0.0
    quoted = " ".join(_QUOTE.findall(reply))
    rt = set(graphlaw.terms(reply))
    faithfulness = (len(rt & set(graphlaw.terms(quoted))) / len(rt)
                    if rt else 0.0)
    answer_score = tournament.grade(None, query, answer)["score"]
    coverage = min(1.0, len(cites) / max(1, k))
    return {"retrieval": round(retrieval, 4),
            "faithfulness": round(faithfulness, 4),
            "answer": round(answer_score, 4),
            "coverage": round(coverage, 4)}


def vector_for(records: dict, exchange_id: str) -> dict:
    """The accreted vector, assembled by walking the records: the exchange's
    own written signals, every governed verdict that judges it, and the
    human's thumb when one landed. Data, never a second truth."""
    import json as _json

    from . import crypto

    def _body(rec):
        return _json.loads(crypto._b64d(rec["body"]).decode()) \
            if rec and "body" in rec else {}
    exch = records.get(exchange_id)
    own = ((_body(exch).get("ask") or {}).get("signals")
           or _body(exch).get("signals") or {})
    judge, thumb = [], None
    for rec in records.values():
        b = _body(rec)
        g = b.get("assay") or {}
        if g.get("of") != exchange_id:
            continue
        if g.get("judge_floor") == "human":
            thumb = float(g.get("score", 0.0))       # the human's word
        else:
            judge.append(float(g.get("score", 0.0)))  # vera's tier
    return {"bench": {k: v for k, v in own.items()
                      if k in WEIGHTS_GENESIS},
            "latency_ms": own.get("latency_ms"),
            "cost_chars": own.get("cost_chars"),
            "judge": judge, "thumb": thumb}


def reward(vector: dict, weights: dict | None = None) -> dict:
    """Governed arithmetic: the weighted fold of the bench rungs — with
    vera's judged score REPLACING the answer proxy when her tier has spoken
    (the richer tier outranks the approximation, on the record). The thumb
    NEVER enters the sum (L3): a 👎 returns the same arithmetic wearing
    `vetoed: true` — the standings refuse a vetoed sample, they never
    average it away."""
    w = dict(WEIGHTS_GENESIS)
    for k, v in (weights or {}).items():
        if k in w:
            try:
                w[k] = float(v)
            except (TypeError, ValueError):
                pass
    total = sum(w.values()) or 1.0
    bench_scores = dict(vector.get("bench") or {})
    if vector.get("judge"):
        bench_scores["answer"] = sum(vector["judge"]) / len(vector["judge"])
    score = sum(w[k] * float(bench_scores.get(k, 0.0)) for k in w) / total
    out = {"score": round(score, 4), "weights": {k: round(w[k] / total, 4)
                                                 for k in w}}
    if vector.get("thumb") is not None and vector["thumb"] < 0.5:
        out["vetoed"] = True                 # the human's word — never a scalar
    return out
