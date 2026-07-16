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

# §5 — the Brain Glass: the functional placement table, PROPOSED (JB tunes
# the anatomy). Brain layout is a template property (0009) and the glass's
# fourth projection under rule 7 — the same heartbeat data, never a second
# truth. The claim is legibility, not neuroscience.
BRAIN_REGIONS = {
    "prefrontal": "governance & consent — becky, governance, grace's gate",
    "temporal": "memory — the librarian, the steward, the record",
    "parietal": "environment — vigil's watch",
    "occipital": "sensory — charlotte's farm, the gathers",
    "cerebellar": "procedure — ada's stable, the routines",
    "limbic": "identity & relationships — the profile, the parlor",
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
            "objective": [dict(o) for o in OBJECTIVE_VECTOR],
            "memory": {**profile.get("memory", {}),
                       "raw_retention": "P30D",
                       "distilled_retention": "P3650D",
                       # 0031 §5's dial, landed at the Phase D gate: nothing
                       # stays trusted forever on a continuity floor
                       "review_interval": "P30D"},
            # the template block — contracts/v0-legal since the Phase D gate
            # (JB approval 2026-07-15): the declaration of record, one field
            "template": {"name": TEMPLATE,
                         "layout": "brain",
                         "brain_regions": dict(BRAIN_REGIONS),
                         "label_canon": dict(LABEL_CANON),
                         "distortion_contracts": {k: dict(v["contract"])
                                                  for k, v in RETENTION_REGIME.items()}}}


def apply(node) -> None:
    """The regime becomes law on a substrate node (0033 sp2's door): every
    class contract set, so a lossy distillation against the intolerables is
    refused at save — the template is physics, not preference."""
    for tag, row in RETENTION_REGIME.items():
        node.set_distortion_contract(tag, row["contract"])


# ---------------------------------------------------------------- consent & delegation (0034 §4)

# The role vocabulary: entitlement bundles over MEMORY DOMAINS — 0013's
# governed-principal machinery serves the enforcement; the bundles are the new
# artifact. A caregiver sees routines and medication support, never journals;
# NO role's bundle ever includes the sealed classes (0026's seal outranks
# every delegation), and no role decides AS the person (0030 — the human is
# the origin, in this universe above all).
ROLE_BUNDLES = {
    "partner": {"domains": ["routines", "medication", "episodic",
                            "relationships"],
                "note": "the fullest bundle short of the person's own"},
    "caregiver": {"domains": ["routines", "medication"],
                  "note": "coordination, never journals"},
    "clinician": {"domains": ["medication", "observations"],
                  "note": "the clinical slice only"},
    "guardian": {"domains": ["routines", "medication", "consents"],
                 "note": "may also read the consent ledger itself"},
    "emergency": {"domains": ["medication", "identity", "location"],
                  "note": "what a responder needs at the door, nothing more"},
    "technician": {"domains": ["telemetry"],
                   "note": "the machine's health, never memory content"},
}

MODALITIES = ("conversation", "photo", "audio", "location", "document")


def _slug(text: str) -> str:
    import re
    return "consent-" + re.sub(r"[^a-z0-9]+", "-", (text or "").lower()).strip("-")[:40]


def make_consent(agent: dict, kp, scope: str, *, purpose: str,
                 role: str | None = None, holder: str = "",
                 modalities: list | None = None, window_days: int = 30,
                 approved_ref: str = "", posture: str = "granted") -> dict:
    """Consent as dynamic state (0034 §4): purpose-, modality-, and time-bound,
    revocable — a signed record on its own worldline, minted only from the
    human's word (0012: access to a person's memory is a consequence). A role
    consent carries its bundle's domains verbatim, so the grant is legible on
    the record; the token becky later mints stays contracts/v0-exact — the
    consent ledger governs WHAT she may mint and UNTIL WHEN, never the token's
    shape (rule 9 untouched)."""
    if role is not None and role not in ROLE_BUNDLES:
        raise ValueError(f"unknown role: {role!r} — the vocabulary knows: "
                         + ", ".join(sorted(ROLE_BUNDLES)))
    for m in modalities or []:
        if m not in MODALITIES:
            raise ValueError(f"unknown modality: {m!r}")
    from datetime import datetime, timedelta, timezone
    frm = datetime.now(timezone.utc)
    body = {"consent": {
        "purpose": purpose,
        **({"role": role, "holder": holder,
            "domains": list(ROLE_BUNDLES[role]["domains"])} if role else {}),
        **({"modalities": list(modalities)} if modalities else {}),
        "window": {"from": frm.strftime("%Y-%m-%dT%H:%M:%SZ"),
                   "until": (frm + timedelta(days=int(window_days)))
                   .strftime("%Y-%m-%dT%H:%M:%SZ")},
        "posture": posture, "approved": approved_ref,
    }}
    return make_memory(agent, kp, scope, body, kind="semantic",
                       tags=["consent", _slug(role or "-".join(modalities or []))])


def consent_key(c: dict) -> str:
    """One worldline per subject: the role (+holder) or the modality set."""
    return _slug((c.get("role") or "") + (c.get("holder") or "")
                 or "-".join(c.get("modalities") or []))


def consent_heads(rows: list[dict]) -> list[dict]:
    """Current head per consent worldline from (id, consent, derived_from,
    at)-shaped rows, oldest first — revoked shown with its posture, because
    withdrawn is a state, never an absence (the 0032 idiom, kept)."""
    superseded = {d for r in rows for d in r.get("derived_from") or []}
    return [{"id": r["id"], **r["consent"]} for r in rows
            if r["id"] not in superseded]


def revoke_body(head: dict, reason: str = "") -> dict:
    """The revocation sibling: same worldline, posture revoked — immediate,
    ungated (stopping access is safe; the record keeps it honest)."""
    return {"consent": {**{k: v for k, v in head.items() if k != "id"},
                        "posture": "revoked",
                        **({"reason": reason} if reason else {})}}


def _in_window(c: dict, now: str) -> bool:
    w = c.get("window") or {}
    return str(w.get("from", "")) <= now <= str(w.get("until", "~"))


def recording_allowed(heads: list[dict], modality: str, now: str) -> bool:
    """Safer mode (0034 §4): degradation is a posture. The template's default
    consents recording (a second brain exists to remember); an explicit REVOKED
    head for the modality drops the organ to safer mode — recording stops. A
    later granted head (in window) restores it. Recall of already-consented
    history follows its own grant: nothing here erases; that door is 0026's."""
    verdict = True
    for c in heads:
        if modality not in (c.get("modalities") or []):
            continue
        if c.get("posture") == "revoked":
            verdict = False
        elif c.get("posture") == "granted" and _in_window(c, now):
            verdict = True
    return verdict


def may_read(heads: list[dict], role: str, domain: str, now: str) -> bool:
    """Delegated authority, checked: the role holds a granted, in-window
    consent whose bundle carries the domain. Sealed classes never delegate —
    structurally absent from every bundle."""
    return any(c.get("role") == role and c.get("posture") == "granted"
               and _in_window(c, now) and domain in (c.get("domains") or [])
               for c in heads)


def token_terms(heads: list[dict], role: str, scope: str, now: str) -> dict | None:
    """What becky MAY mint for a role holder (covenant 3: she alone mints):
    a contracts/v0-exact grant — retrieve on this scope — expiring with the
    consent window. None when no live consent stands: no consent, no token."""
    live = [c for c in heads
            if c.get("role") == role and c.get("posture") == "granted"
            and _in_window(c, now)]
    if not live:
        return None
    until = min(str((c.get("window") or {}).get("until", "~")) for c in live)
    return {"grants": [{"action": "retrieve", "space": {"scope": scope}}],
            "expiry": until,
            "domains": sorted({d for c in live for d in c.get("domains") or []})}


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
