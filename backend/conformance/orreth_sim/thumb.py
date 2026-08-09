# PROVENANCE: Fable 5 (claude-fable-5) — 0048 sp1, the record · 2026-08-09
"""The Thumb (0048): the human answers back — the records and their laws.

A thumb is judgment, not authorship: it judges ONE record by hash, is signed
by the human's own seat (no anonymous thumbs), and never mutates what it
marks (0024's grammar). The quiet word (👍) lands as a human verdict on
0043's shelf — the SAME shape as vera's, costing nothing. The loud word
(👎 + text) lands its verdict AND births a feedback record carrying the
human's words verbatim. And feedback is a request, so it RESOLVES: a sibling
names the outcome on the worldline — what it spawned when the answer moved,
the why when it did not. A wordless no is a verdict alone; there is nothing
to address, and the record holds only what was said.
"""
import json as _json

from . import crypto, vera
from .node import make_memory

OUTCOMES = ("adopted", "evidenced", "commissioned", "referred",
            "repair-staged", "repaired", "declined", "parked")
_NEEDS_REF = ("adopted", "evidenced", "commissioned", "referred",
              "repair-staged", "repaired")
_NEEDS_WHY = ("declined", "parked")

# sp3 — the four routes and what a landing may honestly claim: the craft
# route lands EVIDENCE in the workshop (0031 §4: feedback is never an
# auto-trigger, so "proposed" would overclaim); the gap route lands a real
# commission; the charter route lands a referral; the execution route lands
# a repair objective STAGED at the human's gate, not a repair done.
ROUTES = ("craft", "gap", "charter", "execution")
OUTCOME_FOR = {"craft": "evidenced", "gap": "commissioned",
               "charter": "referred", "execution": "repair-staged"}


def route_contract(raw: str) -> dict:
    """The classify leg's typed contract (0048 sp3): {"route": one of
    ROUTES, "why": one sentence the human will read, "target": the object,
    skill, keeper, or objective the route needs}. Strict — a malformed word
    earns the jacket's one re-ask upstream, then parks; this law never
    guesses a route."""
    import re as _re
    m = _re.search(r"\{.*\}", raw or "", _re.S)
    if not m:
        raise ValueError("no JSON object found in the reply")
    try:
        got = _json.loads(m.group(0))
    except Exception as e:
        raise ValueError(f"the JSON did not parse ({e})") from e
    route = str(got.get("route") or "").strip().lower()
    if route not in ROUTES:
        raise ValueError(f'"route" must be one of {ROUTES}')
    return {"route": route, "why": str(got.get("why") or ""),
            "target": str(got.get("target") or "")}

UP_WORD = "the human's quiet yes — 👍"
DOWN_WORD = "the human's no — 👎"


def _body(rec: dict) -> dict:
    return _json.loads(crypto._b64d(rec["body"]).decode()) if "body" in rec else {}


def make_thumb(human: dict, kp, scope: str, *, of: str, up: bool,
               text: str = "") -> tuple[dict, dict | None]:
    """The thumb lands (0048 §2–§3): one judged record, one signed seat.
    Returns (verdict, feedback) — feedback is None on 👍 and on a wordless 👎;
    the judged record itself is never touched."""
    if not isinstance(of, str) or not of.strip():
        raise ValueError("a thumb judges ONE record by hash — of is required")
    if not (isinstance(human, dict) and human.get("did")):
        raise ValueError("no anonymous thumbs — the human's seat signs, or nothing lands")
    text = str(text or "").strip()
    word = UP_WORD if up else (text or DOWN_WORD)
    verdict = vera.make_human_grading(human, kp, scope, of=of,
                                      score=1.0 if up else 0.0, word=word)
    if up or not text:
        return verdict, None
    fb = make_memory(human, kp, scope,
                     {"feedback": {"of": of, "quoted": text, "state": "open",
                                   "verdict": verdict["id"]}},
                     kind="semantic", tags=["feedback", "thumb"])
    fb["derived_from"] = [of, verdict["id"]]
    return verdict, fb


def resolve_feedback(seat: dict, kp, scope: str, feedback: dict, *, outcome: str,
                     ref: str = "", why: str = "") -> dict:
    """Feedback is a request, and a request resolves (0048 §2): a SIBLING
    record derives from the feedback and names the outcome — a consequence
    outcome names what it spawned, a declined or parked one owes its why.
    Never a mutation, never silence."""
    fbody = _body(feedback).get("feedback") or {}
    if not fbody and feedback.get("id") and feedback.get("of"):
        fbody = {"of": feedback["of"]}     # a decoded row from the wire twin
    if not fbody:
        raise ValueError("only a feedback record resolves — this is not one")
    if outcome not in OUTCOMES:
        raise ValueError(f"unknown outcome: {outcome!r} — one of {OUTCOMES}")
    if outcome in _NEEDS_REF and not ref:
        raise ValueError(f"outcome {outcome!r} names what it spawned — ref is required")
    if outcome in _NEEDS_WHY and not why:
        raise ValueError(f"outcome {outcome!r} owes the human its why")
    body = {"feedback": {"of": fbody.get("of", ""), "state": "resolved",
                         "outcome": outcome,
                         **({"ref": ref} if ref else {}),
                         **({"why": why} if why else {})}}
    res = make_memory(seat, kp, scope, body, kind="semantic",
                      tags=["feedback", "thumb", "resolution"])
    res["derived_from"] = [feedback["id"]]
    return res


# sp4 — the calibration (L2, JB's lock): the human's thumbs are ground
# truth for the examiner, but ONE thumb never indicts vera — the law holds
# its tongue below the declared minimum of overlapping pairs, and speaks
# only when the mean gap crosses the declared bar. News is a card, never
# a lever (0043 law 3, inherited whole).
MIN_CAL_N = 5
CAL_BAR = 0.4


def calibration(rows: list[dict], *, min_n: int = MIN_CAL_N,
                bar: float = CAL_BAR) -> dict:
    """Human vs examiner on the SAME work: rows are decoded verdicts
    {of, score, human}. A pair is a work judged by BOTH; scores on the same
    side average first. Returns {pairs, mean_gap, news, sample} — news only
    at min_n pairs AND mean gap >= bar; the sample names the widest gaps so
    the card can cite its evidence."""
    hum: dict[str, list[float]] = {}
    mach: dict[str, list[float]] = {}
    for r in rows:
        of = str(r.get("of") or "")
        if not of:
            continue
        side = hum if r.get("human") else mach
        side.setdefault(of, []).append(float(r.get("score") or 0.0))
    pairs = []
    for of, hs in hum.items():
        ms = mach.get(of)
        if not ms:
            continue
        h, m = sum(hs) / len(hs), sum(ms) / len(ms)
        pairs.append({"of": of, "human": round(h, 4), "examiner": round(m, 4),
                      "gap": round(abs(h - m), 4)})
    n = len(pairs)
    mean_gap = round(sum(p["gap"] for p in pairs) / n, 4) if n else 0.0
    return {"pairs": n, "min_n": int(min_n), "bar": float(bar),
            "mean_gap": mean_gap,
            "news": bool(n >= min_n and mean_gap >= bar),
            "sample": sorted(pairs, key=lambda p: -p["gap"])[:5]}


def open_feedback(node) -> list[dict]:
    """The unanswered words: every open feedback record with no resolution
    deriving from it — oldest first, nothing silently dropped. This list is
    the routing loop's inbox (sp3) and the honesty check before it exists."""
    resolved = {d for r in node.records.values()
                if "resolution" in (r.get("tags") or [])
                and _body(r).get("feedback", {}).get("state") == "resolved"
                for d in (r.get("derived_from") or [])}
    rows = [{"id": rid, "feedback": _body(r).get("feedback", {}),
             "author": r.get("author", ""), "at": r.get("occurred_at", "")}
            for rid, r in node.records.items()
            if "feedback" in (r.get("tags") or [])
            and "resolution" not in (r.get("tags") or [])
            and _body(r).get("feedback", {}).get("state") == "open"
            and rid not in resolved]
    rows.sort(key=lambda x: x["at"])
    return rows
