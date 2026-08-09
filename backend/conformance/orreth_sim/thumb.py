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

OUTCOMES = ("adopted", "commissioned", "referred", "repaired", "declined", "parked")
_NEEDS_REF = ("adopted", "commissioned", "referred", "repaired")
_NEEDS_WHY = ("declined", "parked")

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
