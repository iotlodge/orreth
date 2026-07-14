# PROVENANCE: authored by Fable 5 (claude-fable-5), 2026-07-10 — 0024, blessed same day
"""Markers & the severity lanes (0024): grade the record without touching it.

A marker is a first-class annotation record — signed, deriving from what it marks,
carrying at least one of the two orthogonal families (R5, Universe-Brain locks
2026-07-10) and always a reason. The lanes (R6, JB lock): a plan routes by its graded
severity — low auto-approves under the gate policy, medium takes resident co-review
plus a human notify, high and critical wait for the human (0012 quorum per class).
"""

from . import crypto
from .node import make_memory

CHANGE_SEVERITIES = ("low", "medium", "high", "critical")
LIFE_EVENTS = ("minor", "major", "substantial")

# R6, verbatim: the lane table is a cascaded gate policy — tighten-only downstream
LANES = {"low": "auto",
         "medium": "co-review+notify",
         "high": "human",
         "critical": "human+quorum"}

RUBRIC = {"id": crypto.content_hash({"rubric": "markers-v0"}), "version": "0.0.1"}


def lane_for(change_severity: str) -> str:
    """The plan's lane from its graded severity (R6). Unknown severities refuse —
    an ungraded plan never rides the auto lane by accident."""
    if change_severity not in CHANGE_SEVERITIES:
        raise ValueError(f"unknown change severity: {change_severity!r}")
    return LANES[change_severity]


def make_marker(agent: dict, kp, scope: str, derived_from: list, *, reason: str,
                change_severity: str | None = None, life_event: str | None = None,
                quoted: str | None = None, extra_tags: list | None = None) -> dict:
    """A marker record (0024 §1): derives from ≥1 marked record, carries at least one
    family, and always says why. Rides kind=semantic + the 'marker' tag — no contract
    change; the 0022 tags index already serves it. The marked record never changes.
    extra_tags (0033 §4): the coordinate rides along — a review marker knows which
    objective and intention it graded."""
    if not derived_from:
        raise ValueError("a marker derives from what it marks — derived_from is required")
    if change_severity is None and life_event is None:
        raise ValueError("a marker carries at least one family (change_severity | life_event)")
    if change_severity is not None and change_severity not in CHANGE_SEVERITIES:
        raise ValueError(f"unknown change severity: {change_severity!r}")
    if life_event is not None and life_event not in LIFE_EVENTS:
        raise ValueError(f"unknown life event weight: {life_event!r}")
    if not reason:
        raise ValueError("every marker says why — reason is required")
    marker: dict = {"reason": reason, "rubric": RUBRIC}
    if change_severity is not None:
        marker["change_severity"] = change_severity
    if life_event is not None:
        marker["life_event"] = life_event
    if quoted is not None:
        marker["quoted"] = quoted
    rec = make_memory(agent, kp, scope, {"marker": marker},
                      kind="semantic", tags=["marker", *(extra_tags or [])])
    rec["derived_from"] = list(derived_from)
    return rec


def parse_remember(text: str):
    """“remember this: <words> [as minor|major|substantial]” → (words, weight) — or
    None when the ask is not a remember. The human's own words pick the weight;
    unweighted moments default minor (0024 §4)."""
    t = (text or "").strip()
    low = t.lower()
    for p in ("remember this:", "remember this,", "remember this —", "remember:",
              "remember this ", "remember that "):
        if low.startswith(p):
            words = t[len(p):].strip()
            weight = "minor"
            for w in LIFE_EVENTS:
                for suffix in (f" as {w}", f" ({w})"):
                    if words.lower().endswith(suffix):
                        weight = w
                        words = words[: -len(suffix)].strip()
                        break
            return (words, weight) if words else None
    return None
