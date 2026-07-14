# PROVENANCE: authored by Fable 5 (claude-fable-5), 2026-07-14 — 0034, the Continuity Universe
"""The Cognitive Continuity template (0034 §2 · §3 · §6): the second brain's
most humane form, as 0009 template work — no core changes.

A governed personal universe that preserves orientation, autonomy,
communication, and access to one's own history — including for the person whose
biological recall is becoming unreliable. Three things make it a template and
not a product fork: the OBJECTIVE VECTOR (0004's dial with its noblest values —
the improver in this universe optimizes for dignity, measurably), the RETENTION
REGIME (0033 §5 distortion contracts per record class — identity at λ≈0,
medication zero-distortion, location allowed to fade), and the LABEL CANON
(§3 — honest confidence spoken structurally from record state; a mind cannot
upgrade confidence the substrate doesn't hold).

Same binary, same physics, same covenant as the enterprise floor — that it
serves both is the whole point of Orreth."""
from __future__ import annotations

from .node import make_memory

TEMPLATE = "continuity"

# §6 — the template's objective vector (0004's dial): what this universe calls
# success. unsupported-memory-rate is the one that must be ~zero — it carries
# the most weight; the vector sums to 1.0 like every tier objective.
OBJECTIVE_VECTOR = [
    {"objective": "unsupported-memory-rate", "weight": 0.25},
    {"objective": "correct-recall-rate", "weight": 0.20},
    {"objective": "consent-adherence", "weight": 0.15},
    {"objective": "successful-orientation-events", "weight": 0.10},
    {"objective": "caregiver-burden", "weight": 0.10},
    {"objective": "correction-rate", "weight": 0.05},
    {"objective": "reduced-repeated-questioning", "weight": 0.05},
    {"objective": "false-alarm-rate", "weight": 0.05},
    {"objective": "provenance-completeness", "weight": 0.05},
]

# §2 — the retention regime: what forgetting is allowed to cost, per record
# class (0033 §5's contract shape, enforced by the substrate's save-gate).
# `retention` rows are the DECLARED posture — per-class TTL enforcement waits
# on the plane; the contracts are law today.
RETENTION_REGIME = {
    "identity": {                     # who people are never distills away (λ≈0)
        "contract": {"must_preserve": ["name", "relationship"],
                     "prohibited_loss": ["identity"], "distortion_bound": 0.0},
        "retention": "forever",
    },
    "medication": {                   # zero-distortion, high-review
        "contract": {"must_preserve": ["dosage", "timing"],
                     "prohibited_loss": ["prescriber"],
                     "may_compress": ["narrative"], "distortion_bound": 0.0},
        "retention": "forever",
    },
    "location": {                     # where you are matters for minutes
        "contract": {"may_compress": ["location", "narrative"]},
        "retention": "PT10M",
    },
    "episodic": {                     # the day distills; the meaningful is vaulted
        "contract": {"must_preserve": ["moment"], "may_compress": ["narrative"]},
        "retention": "vaulted-raw",
    },
}

# §3 — authority types ride as tags on existing claims; no new schema, the
# GIN indexes already serve them (0022).
AUTHORITY_TYPES = ("human-stated", "human-confirmed", "caregiver-supplied",
                   "document-verified", "clinician-verified", "inferred")

# §3 — the label canon: the fidelity ladder's SPOKEN presentation. The shapes
# are data so the charter can carry them and the glass can show the law.
LABEL_CANON = {
    "verified": "said plainly",
    "trusted": "said plainly — the human's own word",
    "corroborated": "shown with its receipts",
    "untrusted": "hedged honestly — may, never definitely",
    "investigating": "doubted out loud",
    "recalled": "never spoken as memory",
}


def speak_claim(state: str, claim: str, *, hints: int = 0,
                sources: list | None = None) -> str | None:
    """§3, structural: the sentence shape comes off the record's state — a mind
    cannot upgrade confidence the substrate doesn't hold. Returns None for a
    recalled claim: the dead are never spoken as memory (only as "something I
    was told and later learned was wrong", on request — a different door)."""
    c = (claim or "").strip()
    if state in ("verified", "trusted", "human-confirmed"):
        return c                                    # say it plainly
    if state == "corroborated":
        named = ", ".join(str(s) for s in (sources or [])[:3]) or "the record"
        return f"{c} — {named} show(s) this"        # show the receipts
    if state == "investigating":
        return f"I'm re-checking this one: {c}"     # doubt out loud
    if state == "recalled":
        return None
    n = max(int(hints), 1)                          # untrusted / inferred / unknown
    return f"this MAY be so — {c} ({n} hint(s), not proof)"


def overlay(profile: dict) -> dict:
    """The template rendered onto a tier profile (0009): the objective vector,
    the retention regime, the label canon, and the template's own memory dials —
    generous distill, vault the meaningful, keep the distilled for a life.
    Everything rides the profile JSON; the plane reads it as data (no core
    changes), and the charter on the floor makes it legible in the record."""
    return {**profile,
            "template": TEMPLATE,
            "objective": [dict(o) for o in OBJECTIVE_VECTOR],
            "memory": {**profile.get("memory", {}),
                       "raw_retention": "P30D",
                       "distilled_retention": "P3650D"},
            "distortion_contracts": {k: dict(v["contract"])
                                     for k, v in RETENTION_REGIME.items()},
            "label_canon": dict(LABEL_CANON)}


def apply(node) -> None:
    """The regime becomes law on a substrate node (0033 sp2's door): every
    class contract set, so a lossy distillation against the intolerables is
    refused at save — the template is physics, not preference."""
    for tag, row in RETENTION_REGIME.items():
        node.set_distortion_contract(tag, row["contract"])


def make_charter(agent: dict, kp, scope: str) -> dict:
    """Config-as-memory (R8): the floor's own record carries its law — the
    template named, the vector, the regime, the canon. The glass reads the
    charter; nothing about this universe's posture is invisible."""
    body = {"continuity_charter": {
        "template": TEMPLATE,
        "objective": [dict(o) for o in OBJECTIVE_VECTOR],
        "regime": {k: {"contract": dict(v["contract"]),
                       "retention": v["retention"]}
                   for k, v in RETENTION_REGIME.items()},
        "label_canon": dict(LABEL_CANON),
    }}
    return make_memory(agent, kp, scope, body, kind="semantic",
                       tags=["template", "continuity-charter"])
