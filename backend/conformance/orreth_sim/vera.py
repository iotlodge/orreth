# PROVENANCE: Fable 5 (claude-fable-5) — 0043 sp2, vera & the assay loop · 2026-07-30
"""vera, the astronomer (0043 §2 · §5 · §6 — LOCKED, JB 2026-07-30): the tenth
organ, named for Vera Rubin, who measured what galaxies actually did against
what their visible matter claimed. She keeps the Observatory.

Her laws, all four locked:

 1. **She is the inverse of vigil.** vigil is content-BLIND detection; vera is
    content-AWARE assay. The separation keeps vigil trustworthy and vera
    useful; the two never merge. And the Mirror keeps the conversations —
    vera assays WORK (intention and objective outcomes), never audiences.
 2. **She never grades her own floor's homework.** Her judges are always
    another floor's minds — the graduation pipeline's independence, made a
    standing law. Verdicts land as signed records under the JUDGE'S
    authorship (author ≠ executor, 0005), on the shelf of the floor whose
    work it is: institutional experience, feeding 0039's loop. Tier one of
    the storage law — these are Chronicle records, never pruned series.
 3. **Detection wears no levers** (0041 §4, inherited whole). A degrading
    standing becomes a CARD carrying its evidence; the human's gate decides.
    vera measures; humans move.
 4. **Her own cost is her first exhibit.** Every judgment she commissions
    rides the meter under her DID; `exhibit()` prices her curiosity from the
    verdicts' own cost lines — the Observatory's price is always one of its
    instruments.

The dial (§5) gates her beat: at **glance** and **watch** the examiner rests
(free depth, honestly named); only at **assay** does she sample completed
work and commission judges — quality costs money, and the dial says how much.

Her floor: the universe (the improver's and the Mirror's precedent — one
astronomer, staff of the whole world; builder's call at sp2, the pattern
already blessed). No hall of mirrors: assay records are never themselves
sampled, and work already under verdict is never re-assayed.
"""
from __future__ import annotations

import json as _json

from . import crypto, factory
from .agent_surface import BudgetExceeded
from .node import make_memory

DIAL = ("glance", "watch", "assay")

DEFAULT_RUBRIC = ("faithful to the record it served · complete against its "
                  "declared intent · honest about what is missing")

WORK_TAGS = ("intention-outcome", "objective-outcome")

EST_TOKENS = 120          # one commissioned judgment's metered estimate

# the degradation thresholds the cards cite — findings name their yardstick
FLOOR_MEAN = 0.55
TREND_DROP = 0.15


def _body(rec: dict) -> dict:
    return _json.loads(crypto._b64d(rec["body"]).decode()) if "body" in rec else {}


# ---- the shelf: what has been judged, what awaits judgment ------------------------------

def assayed_refs(node) -> set[str]:
    """Every work record already under a verdict — the dedup that keeps the
    examiner from drumming on the same door."""
    out: set[str] = set()
    for r in node.records.values():
        if "assay" in (r.get("tags") or []):
            out.update(r.get("derived_from") or [])
    return out


def sample_completed(node, *, limit: int = 3) -> list[tuple[str, dict]]:
    """Recent completed work (§6): intention and objective outcomes, newest
    first, minus anything already assayed — and NEVER an assay record itself
    (a mirror that assesses its own reflections is a hall of mirrors; the
    Mirror's law, kept here too)."""
    done = assayed_refs(node)
    rows = [(rid, r) for rid, r in node.records.items()
            if rid not in done
            and "assay" not in (r.get("tags") or [])
            and any(t in (r.get("tags") or []) for t in WORK_TAGS)]
    rows.sort(key=lambda x: x[1].get("received_at", ""), reverse=True)
    return rows[:limit]


def pick_bench(benches: dict[str, dict], *, work_floor: str) -> tuple[str, dict] | None:
    """A judge from ANOTHER floor's bench — never the floor whose work it is
    (law 2, structural). Deterministic: sorted scopes, first that differs.
    None when the universe holds no other bench: the assay must refuse
    honestly rather than let a floor grade its own homework."""
    for scope in sorted(benches):
        if scope != work_floor:
            return scope, benches[scope]
    return None


# ---- the verdict: tier one of the storage law -------------------------------------------

def make_verdict(judge_seat: dict, judge_kp, scope: str, *, of: str,
                 work_floor: str, judge_floor: str, rubric: str,
                 rubric_declared: bool, score: float, why: str,
                 cost: dict) -> dict:
    """A signed Chronicle record under the JUDGE'S authorship — author ≠
    executor by construction, the rubric named, the default rubric honestly
    labeled as default, the commission's cost on the record (law 4)."""
    body = {"assay": {
        "of": of, "work_floor": work_floor, "judge_floor": judge_floor,
        "rubric": rubric, "rubric_declared": rubric_declared,
        "score": round(max(0.0, min(1.0, float(score))), 4),
        "why": str(why)[:200], "cost": dict(cost),
    }}
    rec = make_memory(judge_seat, judge_kp, scope, body, kind="semantic",
                      tags=["assay", "verdict"])
    rec["derived_from"] = [of]
    return rec


def make_human_grading(human: dict, kp, scope: str, *, of: str,
                       score: float, word: str) -> dict:
    """The human's verdict enters the SAME shelf by the SAME shape (§6) — a
    card, a score, a signature; the annotation queue collapses into a gate we
    already have. Costs nothing and says so."""
    body = {"assay": {
        "of": of, "work_floor": scope, "judge_floor": "human",
        "rubric": "the human's own judgment", "rubric_declared": True,
        "score": round(max(0.0, min(1.0, float(score))), 4),
        "why": str(word)[:200], "cost": {"tokens": 0},
    }}
    rec = make_memory(human, kp, scope, body, kind="semantic",
                      tags=["assay", "verdict", "human-grading"])
    rec["derived_from"] = [of]
    return rec


def verdicts(node) -> list[dict]:
    """Every verdict on this shelf, oldest first — (id, assay, author, at)."""
    rows = [{"id": rid, "assay": _body(r).get("assay", {}),
             "author": r.get("author", ""), "at": r.get("received_at", "")}
            for rid, r in node.records.items()
            if "verdict" in (r.get("tags") or [])]
    rows.sort(key=lambda x: x["at"])
    return rows


# ---- standings and the cards (no levers) ------------------------------------------------

def standings(node) -> dict:
    """The floor's quality, aggregated from verdicts — judge and human alike.
    Trend speaks only once four verdicts stand (halves compared); before
    that it is honestly None, never a guess."""
    rows = verdicts(node)
    per: dict[str, dict] = {}
    for v in rows:
        a = v["assay"]
        s = per.setdefault(a.get("work_floor", "?"),
                           {"scores": [], "humans": 0, "refs": []})
        s["scores"].append(a.get("score", 0.0))
        s["refs"].append(v["id"])
        if a.get("judge_floor") == "human":
            s["humans"] += 1
    out = {}
    for floor, s in per.items():
        n = len(s["scores"])
        half = n // 2
        trend = None
        if n >= 4:
            earlier = sum(s["scores"][:half]) / half
            recent = sum(s["scores"][half:]) / (n - half)
            trend = round(recent - earlier, 4)
        out[floor] = {"n": n, "mean": round(sum(s["scores"]) / n, 4),
                      "trend": trend, "humans": s["humans"],
                      "refs": s["refs"]}
    return out


def degradations(stand: dict, *, floor_mean: float = FLOOR_MEAN,
                 trend_drop: float = TREND_DROP) -> list[dict]:
    """Detection wears no levers (law 3): a low mean or a falling trend
    becomes a CARD — the yardstick named, the evidence cited, the standing
    attached, nothing enacted. The human's gate decides what follows."""
    cards = []
    for floor, s in stand.items():
        why = None
        if s["mean"] < floor_mean:
            why = (f"mean assay score {s['mean']} sits under the {floor_mean} "
                   "floor")
        elif s["trend"] is not None and s["trend"] <= -trend_drop:
            why = (f"assay trend fell {abs(s['trend'])} across the window "
                   f"(≥ {trend_drop} stages)")
        if why:
            cards.append({"kind": "assay-degradation", "scope": floor,
                          "why": why, "standing": {k: s[k] for k in
                                                   ("n", "mean", "trend")},
                          "evidence": list(s["refs"])})
    return cards


# ---- the astronomer ---------------------------------------------------------------------

class Vera:
    """The tenth organ, standing at the universe floor. Her beat is the
    Examiner (§6): sample completed work → a judge from another floor's bench
    scores it against the rubric its objective declared (or the default,
    labeled) → the verdict lands signed on the work's shelf → standings
    aggregate → degradations become cards. Every commission is metered under
    her DID BEFORE the judge thinks — when the meter says no, the beat halts
    honestly and says where it stopped."""

    def __init__(self, home, becky, *, archetype: dict | None = None,
                 budget_tokens: int = 2400):
        arch = archetype or becky.issue_identity("archetype", home.scope)[0]
        [self.surface] = factory.stamp(home, becky, arch, 1,
                                       generation="standing-vera",
                                       budget_tokens=budget_tokens)
        self.home = home

    @property
    def did(self) -> str:
        return self.surface.identity["did"]

    def assay_beat(self, work_node, benches: dict[str, dict], *,
                   dial: str, rubrics: dict[str, str] | None = None,
                   sample: int = 3) -> dict:
        """One turn of the examiner, gated by the dial. benches:
        {floor_scope: {"seat": ident, "kp": kp, "think": fn(work, rubric) ->
        {"score", "why"}}} — the judge's floor signs, vera's meter pays."""
        if dial not in DIAL:
            raise ValueError(f"no dial position named '{dial}'")
        if dial != "assay":
            return {"dial": dial, "assayed": 0,
                    "note": "the examiner rests — series and counters only; "
                            "depth costs money and this depth is free"}
        out: dict = {"dial": dial, "assayed": 0, "verdicts": [],
                     "refused": [], "cost": {"tokens": 0}}
        for rid, work in sample_completed(work_node, limit=sample):
            bench = pick_bench(benches, work_floor=work_node.scope)
            if bench is None:
                # no other floor holds a bench — refusing beats a floor
                # grading its own homework (law 2, held structurally)
                out["refused"].append(
                    {"of": rid, "why": "no judge outside this floor — "
                                       "the assay refuses, never self-grades"})
                continue
            judge_floor, judge = bench
            try:
                # the meter FIRST (law 4): her DID, her budget, her exhibit —
                # and PINNED (0016's floor): a squeezed budget halts the beat
                # loudly rather than seat a silently cheaper judge
                charge = self.home.model_gateway.call(
                    self.surface, "standard", EST_TOKENS, pinned=True)
            except BudgetExceeded:
                out["halted"] = ("the meter said no — depth costs money, "
                                 "and the dial's budget is spent")
                break
            body = _body(work)
            goal = (body.get("outcome") or body.get("objective_outcome")
                    or {}).get("of") or ""
            rubric = (rubrics or {}).get(goal)
            declared = rubric is not None
            verdict_word = judge["think"](body, rubric or DEFAULT_RUBRIC)
            rec = make_verdict(
                judge["seat"], judge["kp"], work_node.scope, of=rid,
                work_floor=work_node.scope, judge_floor=judge_floor,
                rubric=rubric or DEFAULT_RUBRIC, rubric_declared=declared,
                score=verdict_word.get("score", 0.0),
                why=verdict_word.get("why", ""),
                cost={"tokens": charge["charged"]})
            out["verdicts"].append(work_node.write(rec))
            out["assayed"] += 1
            out["cost"]["tokens"] += charge["charged"]
        stand = standings(work_node)
        out["standings"] = stand
        out["findings"] = degradations(stand)
        return out

    def exhibit(self, work_node) -> dict:
        """Her first exhibit (law 4): the Observatory's own price, read from
        the verdicts' cost lines — assays commissioned, tokens spent, budget
        remaining, to the decimal the meter shows."""
        rows = verdicts(work_node)
        commissioned = [v for v in rows if v["assay"].get("judge_floor") != "human"]
        return {"assays": len(commissioned),
                "tokens": sum(v["assay"].get("cost", {}).get("tokens", 0)
                              for v in commissioned),
                "human_gradings": len(rows) - len(commissioned),
                "budget_left": self.surface.budget_left}
