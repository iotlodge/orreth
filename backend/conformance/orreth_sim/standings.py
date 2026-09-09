# PROVENANCE: Claude Fable 5 (claude-fable-5) — 0066 sp4, the standings · 2026-09-09
"""The standings (0066 §3.4, Stage 1) — the SCOREBOARD, in the three-level
rule's plain words: the running tally of which style is winning for which
kind of question. It updates continuously and automatically because it is
only a summary of records that already exist — it reports, it never
referees. Deleting it loses nothing; it rebuilds from the records, and a
purged record leaves it in the same breath (purge reach by construction).

The arithmetic is Bayesian and honest about its approximation: each
(question-kind × style) cell keeps a Beta posterior over reward
(a = 1 + Σreward, b = 1 + Σ(1 − reward)) and reports its mean with a 95%
credible interval by the NORMAL APPROXIMATION of that Beta — named as such;
at the volumes where the approximation strains, the intervals are wide and
the conservative test below refuses anyway.

L3 continues here: a VETOED sample (the human's 👎) is REFUSED from the
cell's arithmetic and counted aside — the standings never average away a
human's veto.

THE PROPOSAL GENERATOR is the scoreboard's only voice: when a challenger's
credible LOW clears the incumbent's credible HIGH — both with enough
samples — it STAGES a routing-standard revision whose evidence IS the
standings table, onto the existing improvement road (independent grade, the
human's gate). It refuses thin evidence by design; it never applies
anything itself.

THE NIGHTLY REPLAY (§3.5) feeds the counterfactual side: a completed ask
re-runs through every arm the router did not choose, graded by the cheap
bench at zero serving risk — one signed replay record per ask. Latency and
thumbs are the only signals replay cannot reach, and the cells built from
replay rows carry bench-only rewards, exactly as confessed.
"""
from __future__ import annotations

import json as _json
import math

from . import crypto, signals, variants

MIN_N = 8            # the least samples before a cell may argue (sp5 may dial)
Z95 = 1.96           # the 95% band's z — the approximation, named


def _body(rec: dict) -> dict:
    return _json.loads(crypto._b64d(rec["body"]).decode()) \
        if rec and "body" in rec else {}


def _cell():
    return {"n": 0, "a": 1.0, "b": 1.0, "vetoed": 0}


def _finish(c: dict) -> dict:
    n, a, b = c["n"], c["a"], c["b"]
    mean = a / (a + b)
    var = a * b / ((a + b) ** 2 * (a + b + 1))
    half = Z95 * math.sqrt(var)
    return {**c, "mean": round(mean, 4),
            "low": round(max(0.0, mean - half), 4),
            "high": round(min(1.0, mean + half), 4)}


def build(records: dict, weights: dict | None = None) -> dict:
    """The scoreboard, rebuilt whole from the records: real exchanges (the
    chosen arm, full signals) and replay records (every counterfactual arm,
    bench-only). Key: (question-kind, style)."""
    cells: dict = {}
    # the real lane: ask exchanges joined to their choices
    for rid, rec in records.items():
        tags = rec.get("tags") or []
        if "ask" in tags and "replay" not in tags:
            b = _body(rec).get("ask") or {}
            if not b.get("signals"):
                continue
            choice = records.get((rec.get("derived_from") or [None])[0])
            feats = ((_body(choice).get("dispatch") or {}).get("features")
                     or {}) if choice else {}
            qkind = feats.get("type", "plain")
            style = variants.resolve(str(b.get("variant") or "")) or "naive"
            vec = signals.vector_for(records, rid)
            r = signals.reward(vec, weights)
            c = cells.setdefault((qkind, style), _cell())
            if r.get("vetoed"):
                c["vetoed"] += 1          # the human's veto — never averaged
                continue
            c["n"] += 1
            c["a"] += r["score"]
            c["b"] += 1.0 - r["score"]
        elif "replay" in tags:
            rb = _body(rec).get("replay") or {}
            qkind = rb.get("kind", "plain")
            for style, arm in (rb.get("arms") or {}).items():
                canon = variants.resolve(style) or style
                r = signals.reward({"bench": arm}, weights)
                c = cells.setdefault((qkind, canon), _cell())
                c["n"] += 1
                c["a"] += r["score"]
                c["b"] += 1.0 - r["score"]
    return {f"{k[0]}·{k[1]}": _finish(c) for k, c in sorted(cells.items())}


def counterfactual(node, asked: str, qkind: str, chosen: str,
                   answer_fn, rows: list[str],
                   of: str | None = None) -> dict:
    """One ask's replay panel: every arm answers the SAME question over the
    same shelf, graded by the cheap bench — zero serving risk. Returns the
    replay record body (naming the exchange it replays, so a panel is never
    an orphan and never runs twice); the caller signs and lands it."""
    arms = {}
    for row in rows:
        try:
            a = answer_fn(node, row, asked)
            arms[row] = signals.bench(asked, a)
        except Exception:
            continue                      # a stumbling arm scores nothing
    return {"replay": {"asked": asked[:200], "kind": qkind,
                       "chosen": chosen, "arms": arms,
                       **({"of": of} if of else {})}}


def propose(board: dict, standard: dict,
            min_n: int | None = None) -> dict | None:
    """The scoreboard's one voice: for each question kind, find the style the
    CURRENT rulebook would route it to, and every challenger whose credible
    LOW clears the incumbent's credible HIGH with enough samples on both
    sides — the conservative test. One winner per kind at most; thin
    evidence refuses (None). The result is a STAGED standard revision plus
    the evidence rows — never an applied change."""
    floor_n = int(min_n) if min_n else MIN_N
    routes = {r["when"]: variants.resolve(r["route"]) or r["route"]
              for r in standard.get("rules", [])}
    default = standard.get("default", "naive")
    changes, evidence = {}, {}
    kinds = {key.split("·", 1)[0] for key in board}
    for kind in sorted(kinds):
        incumbent = routes.get(kind, default)
        inc = board.get(f"{kind}·{incumbent}")
        best = None
        for key, cell in board.items():
            k, style = key.split("·", 1)
            if k != kind or style == incumbent or cell["n"] < floor_n:
                continue
            if best is None or cell["low"] > best[1]["low"]:
                best = (style, cell)
        if best is None:
            continue
        inc_high = inc["high"] if inc and inc["n"] >= floor_n else None
        if inc_high is None:
            continue                      # the incumbent unmeasured — refuse
        if best[1]["low"] > inc_high:
            changes[kind] = best[0]
            evidence[kind] = {"incumbent": {incumbent: inc},
                              "challenger": {best[0]: best[1]}}
    if not changes:
        return None
    rules = [dict(r) for r in standard.get("rules", [])]
    seen = set()
    for r in rules:
        if r["when"] in changes:
            r["route"] = changes[r["when"]]
            r["why"] = (f"the standings' word: «{changes[r['when']]}» beat "
                        f"the old route with its credible floor above the "
                        f"incumbent's ceiling")
            seen.add(r["when"])
    for kind, style in changes.items():
        if kind not in seen and kind != "plain":
            rules.append({"when": kind, "route": style,
                          "why": "the standings' word — a kind the rulebook "
                                 "never routed now has a measured winner"})
        elif kind == "plain" and kind not in seen:
            pass                          # 'plain' is the default's ground —
                                          # a default change is its own, rarer
                                          # argument (refused here by design)
    version = str(standard.get("version", "1"))
    staged = dict(standard, version=f"{version}+standings", rules=rules)
    return {"standard": staged, "changes": changes, "evidence": evidence}
