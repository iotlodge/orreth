"""The monoidal roll-up (0005 §2–§4): sufficient statistics that compose up the tree.

merge() is associative with empty_bundle() as identity — standings, quarter-closes, and
AgentFacts are the same math. The Beta prior is applied ONCE, at report time (merging
posteriors would double-count it); confidence is count-weighted by construction.
"""
from __future__ import annotations

import math

_OUTCOMES = ("success", "failure", "partial", "aborted")
_COSTS = ("tokens", "model_calls", "usd", "wall_ms")


def empty_bundle() -> dict:
    return {"n": 0, "outcomes": {o: 0 for o in _OUTCOMES}, "per_objective": [],
            "cost": {k: 0 for k in _COSTS}, "compliance": "clean"}


def bundle_of(run: dict) -> dict:
    """Lift one RunRecord into the monoid."""
    b = empty_bundle()
    b["n"] = 1
    b["outcomes"][run["outcome"]] = 1
    for s in run["scores"]:
        breached = 1 if s.get("floor_breached") else 0
        b["per_objective"].append({
            "objective": s["objective"], "n": 1, "sum": s["score"],
            "sum_sq": s["score"] ** 2, "min": s["score"], "max": s["score"],
            "floor_breaches": breached,
        })
        if breached:
            b["compliance"] = "breached"
    for k, v in run.get("cost", {}).items():
        b["cost"][k] = v
    return b


def merge(a: dict, b: dict) -> dict:
    """Component-wise, associative; a breach anywhere is a breach of the whole (never averaged away)."""
    out = empty_bundle()
    out["n"] = a["n"] + b["n"]
    out["outcomes"] = {o: a["outcomes"][o] + b["outcomes"][o] for o in _OUTCOMES}
    stats = {s["objective"]: dict(s) for s in a["per_objective"]}
    for s in b["per_objective"]:
        if s["objective"] in stats:
            t = stats[s["objective"]]
            t["n"] += s["n"]; t["sum"] += s["sum"]; t["sum_sq"] += s["sum_sq"]
            t["min"] = min(t["min"], s["min"]); t["max"] = max(t["max"], s["max"])
            t["floor_breaches"] += s["floor_breaches"]
        else:
            stats[s["objective"]] = dict(s)
    out["per_objective"] = sorted(stats.values(), key=lambda s: s["objective"])
    out["cost"] = {k: a["cost"].get(k, 0) + b["cost"].get(k, 0) for k in _COSTS}
    out["compliance"] = "breached" if (a["compliance"] == "breached" or
                                       b["compliance"] == "breached") else "clean"
    return out


def report(bundle: dict, objective: str, prior: tuple[float, float] = (1.0, 1.0)) -> dict:
    """The read edge (0005 §3, locked 2026-07-02): Beta posterior, mean + 95% credible interval + n.

    Scores in [0,1] are mean-matched pseudo-counts: s successes, n-s failures; the tier's weak
    prior enters here and only here. Small n ⇒ honestly wide interval — the '3 engagements' case.
    """
    stat = next((s for s in bundle["per_objective"] if s["objective"] == objective), None)
    if stat is None or stat["n"] == 0:
        a0, b0 = prior
        n = 0
    else:
        a0 = prior[0] + stat["sum"]
        b0 = prior[1] + (stat["n"] - stat["sum"])
        n = stat["n"]
    mean = a0 / (a0 + b0)
    var = (a0 * b0) / ((a0 + b0) ** 2 * (a0 + b0 + 1))
    half = 1.96 * math.sqrt(var)  # normal approx of the Beta; the plane may use exact quantiles
    return {"mean": mean, "ci95": (max(0.0, mean - half), min(1.0, mean + half)),
            "n": n, "compliance": bundle["compliance"],
            "floor_breaches": stat["floor_breaches"] if stat else 0}


def tier_score(bundle: dict, objective_vector: list[dict],
               prior: tuple[float, float] = (1.0, 1.0)) -> dict:
    """The 0004 §3 debt paid: weighted mean over NON-floor objectives (weights renormalized);
    floors never enter the average — they gate compliance (flag, never average away)."""
    soft = [o for o in objective_vector if not o.get("floor")]
    total_w = sum(o["weight"] for o in soft) or 1.0
    score = sum(o["weight"] / total_w * report(bundle, o["objective"], prior)["mean"]
                for o in soft)
    return {"score": score, "compliance": bundle["compliance"]}
