# PROVENANCE: Claude Fable 5 (claude-fable-5) — 0068 sp4, the rails and the audit (SDK twin of orreth_sim/rails.py — parity-tested) · 2026-09-10
"""The rails bite (0068 §3.3) — content checks in the LiteLLM lane, firmware-side.

In plain words: the guardrail RULES are craft a human edits through a gated
door (guardrails.py, sp1); the DETECTORS here are firmware — the machinery
that cannot be quietly edited. This module is the warden's split promoted:
the Farm warden proved the pattern (checks are firmware, the pattern list is
governed craft), and these rails apply it to content itself.

Where this runs: in the one lane every thought already passes through — the
cognition side of the gateway split. Inputs are checked BEFORE the model
call; outputs are checked BEFORE they return. The plane never sees a prompt
(its oldest promise); it sees the PROOF — the context pin (sp3) — while the
checking itself happens here, beside the call.

What leaves this module about a hit: category, direction, action, count, and
the rule's own reason. NEVER the matched content. An audit that leaked the
SSN it masked would be the wound wearing a bandage.

The action ladder (weakest → strongest), enforced exactly:
    annotate   — the event is recorded; the text passes untouched
    mask       — each matched span becomes «[masked: <category>]»
    quarantine — masked AND flagged for human review (vigil stages the card)
    refuse     — the whole exchange refuses, loudly, with the rule's reason
"""
from __future__ import annotations

import re

# ---- the detectors: firmware, release-only --------------------------------------------

# Payment cards: 13–19 digits, spaces/dashes allowed, Luhn-checked so a
# random long number is not an incident
_PCI_CANDIDATE = re.compile(r"(?<![\d-])(?:\d[ -]?){12,18}\d(?![\d-])")

# PII, first roster: dashed SSNs (the unseparated 9-digit form collides with
# too much of the world — named honestly below), emails, separated US phones
_SSN = re.compile(r"\b(?!000|666|9\d{2})\d{3}-(?!00)\d{2}-(?!0000)\d{4}\b")
_EMAIL = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
_PHONE = re.compile(r"(?<!\d)(?:\+?1[ .-])?\(?\d{3}\)?[ .-]\d{3}[ .-]\d{4}(?!\d)")


def _luhn(digits: str) -> bool:
    total, alt = 0, False
    for ch in reversed(digits):
        d = int(ch)
        if alt:
            d *= 2
            if d > 9:
                d -= 9
        total += d
        alt = not alt
    return total % 10 == 0


def detect(text: str) -> dict[str, list[tuple[int, int]]]:
    """Every category's hit spans in the text — spans stay INSIDE this
    module's callers; only counts and categories ever leave."""
    hits: dict[str, list[tuple[int, int]]] = {"pii": [], "pci": []}
    for m in _PCI_CANDIDATE.finditer(text or ""):
        digits = re.sub(r"[ -]", "", m.group())
        if 13 <= len(digits) <= 19 and _luhn(digits):
            hits["pci"].append(m.span())
    for rx in (_SSN, _EMAIL, _PHONE):
        for m in rx.finditer(text or ""):
            if not any(a <= m.start() < b for a, b in hits["pci"]):
                hits["pii"].append(m.span())
    return hits


def _mask_spans(text: str, spans: list[tuple[int, int, str]]) -> str:
    """Replace each span right-to-left with «[masked: category]», skipping
    overlaps so a span never masks inside another's replacement."""
    out, taken = text, []
    for a, b, cat in sorted(spans, key=lambda s: -s[0]):
        if any(not (b <= ta or a >= tb) for ta, tb, _ in taken):
            continue
        taken.append((a, b, cat))
        out = out[:a] + f"[masked: {cat}]" + out[b:]
    return out


def _pattern_spans(text: str, rule: dict, patterns) -> tuple[list, str | None]:
    """A pattern rule's hits via its craft list (pattern_ref → regex list).
    An unresolvable list never silently passes — the caller gets a note."""
    ref = (rule.get("match") or {}).get("pattern_ref")
    rows = None
    if patterns is not None:
        try:
            rows = patterns(ref)
        except Exception:
            rows = None
    if not rows:
        return [], f"pattern list «{ref}» unresolved — the rule watched nothing"
    spans = []
    for rx in rows:
        try:
            spans.extend(m.span() for m in re.finditer(rx, text or ""))
        except re.error:
            return [], f"pattern list «{ref}» holds a broken expression"
    return spans, None


def enforce(composed: dict, direction: str, text: str, *,
            patterns=None) -> dict:
    """The composed rules applied to one text moving one DIRECTION
    (entering a model, or leaving toward a reader). Returns:
        text    — what may proceed (masked where rules said mask)
        events  — one per rule that saw content: category · action ·
                  direction · count · the rule's reason (never the content)
        refused — True when a refuse rule hit: nothing proceeds
        refusal — the loud, human sentence a refused exchange serves
        review  — True when a quarantine rule hit: vigil stages a human look
    """
    rules = (composed or {}).get("rules") or []
    live = [r for r in rules
            if r["match"]["direction"] in (direction, "both")]
    if not live or not (text or "").strip():
        return {"text": text, "events": [], "refused": False,
                "refusal": None, "review": False}
    found = detect(text)
    events, mask_spans, refused_reason, review = [], [], None, False
    for r in sorted(live, key=lambda x: -_strength(x["action"])):
        cat = r["match"]["category"]
        if cat == "pattern":
            spans, note = _pattern_spans(text, r, patterns)
            if note:
                events.append({"category": "pattern", "action": "annotate",
                               "direction": direction, "count": 0,
                               "reason": note})
                continue
        else:
            spans = found.get(cat) or []
        if not spans:
            continue
        events.append({"category": cat, "action": r["action"],
                       "direction": direction, "count": len(spans),
                       "reason": r["reason"]})
        if r["action"] == "refuse" and refused_reason is None:
            refused_reason = (cat, r["reason"])
        elif r["action"] in ("mask", "quarantine"):
            mask_spans.extend((a, b, cat) for a, b in spans)
            if r["action"] == "quarantine":
                review = True
    if refused_reason is not None:
        cat, why = refused_reason
        return {"text": None, "events": events, "refused": True,
                "refusal": f"⛔ refused by a guardrail ({cat}, {direction}) "
                           f"— {why}",
                "review": review}
    return {"text": _mask_spans(text, mask_spans) if mask_spans else text,
            "events": events, "refused": False, "refusal": None,
            "review": review}


ACTIONS = ("annotate", "mask", "quarantine", "refuse")   # the ladder, inlined


def _strength(action: str) -> int:
    return ACTIONS.index(action)


def outcome_of(*event_lists) -> str:
    """The one word an audit wears: the strongest thing that happened across
    both directions — clean · annotated · masked · quarantined · refused."""
    order = ("annotate", "mask", "quarantine", "refuse")
    worn = {"annotate": "annotated", "mask": "masked",
            "quarantine": "quarantined", "refuse": "refused"}
    top = -1
    for evs in event_lists:
        for e in evs or []:
            if e["count"] and order.index(e["action"]) > top:
                top = order.index(e["action"])
    return worn[order[top]] if top >= 0 else "clean"
