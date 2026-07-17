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


# ---------------------------------------------------------------- the testament (0035)

# 0035 §2 — the human's standing word about the end. The fates a domain may be
# told: seal (read-only legacy — the default, and the fate of the unnamed),
# pass (custody, never identity), shred (crypto-erasure through 0026's doors).
FATES = ("seal", "pass", "shred")


def make_testament(agent: dict, kp, scope: str, *, fates: dict,
                   executor: str = "", witnesses: list | None = None,
                   silence_days: int = 30, disclosure: dict | None = None,
                   escrow: dict | None = None, approved_ref: str = "",
                   posture: str = "standing") -> dict:
    """The testament (0035 §2): a config-as-memory record on the human's own
    worldline — per-domain fate map, roster, silence window, disclosure map —
    staged at 0012's gate while the human lives (arming future consequence IS
    a consequence), revised as siblings with the head winning, revocable to
    the last day. The §8 locks are validated at mint, loudly:
    an unescrowed vault cannot be sealed readable or passed (its keys die with
    their keeper — lock 5); a fate that must one day EXECUTE needs an executor,
    because only attested death executes (locks 1 · 3); and the executor never
    witnesses their own attestation (distinct signers, 0012 §3)."""
    witnesses = list(witnesses or [])
    for domain, fate in (fates or {}).items():
        if fate not in FATES:
            raise ValueError(f"unknown fate: {fate!r} for {domain!r} — a domain "
                             "may " + " · ".join(FATES))
    for domain, esc in (escrow or {}).items():
        if esc is False and (fates or {}).get(domain) != "shred":
            raise ValueError(f"{domain!r} is unescrowed — its keys die with "
                             "their keeper, so it can only shred (key "
                             "mortality); seal-readable and pass need escrow "
                             "(0035 §8 lock 5)")
    if any(f in ("pass", "shred") for f in (fates or {}).values()) and not executor:
        raise ValueError("a testament that passes or shreds needs an executor "
                         "— only attested death executes (0035 §3)")
    if executor and executor in witnesses:
        raise ValueError("the executor cannot witness their own attestation — "
                         "distinct signers (0012 §3)")
    body = {"testament": {
        "fates": dict(fates or {}),
        "executor": executor,
        "witnesses": witnesses,
        "silence_window": {"days": int(silence_days)},
        "disclosure": dict(disclosure or {}),
        "escrow": dict(escrow or {}),
        "posture": posture, "approved": approved_ref,
    }}
    return make_memory(agent, kp, scope, body, kind="semantic",
                       tags=["testament"])


def testament_heads(rows: list[dict]) -> list[dict]:
    """One worldline per human: the head from (id, testament, derived_from,
    at)-shaped rows, oldest first — a revoked head shown revoked, because a
    withdrawn word is a state, never an absence (the 0032 idiom, kept)."""
    superseded = {d for r in rows for d in r.get("derived_from") or []}
    return [{"id": r["id"], **r["testament"]} for r in rows
            if r["id"] not in superseded]


def revoke_testament_body(head: dict) -> dict:
    """Revocable to the last day (0035 §2): the revocation sibling — same
    worldline, posture revoked, immediate and ungated (withdrawing a future
    consequence is safe). Without a standing word, every domain seals — the
    least irreversible act (§8 lock 2)."""
    return {"testament": {**{k: v for k, v in head.items() if k != "id"},
                          "posture": "revoked"}}


def fate_of(head: dict | None, domain: str) -> str:
    """§8 locks 1 · 2, pure: no testament — or a revoked one — seals; a named
    domain speaks its fate; an unnamed domain seals. The universe assumes
    nothing about the unspoken, and silence may only contain."""
    if not head or head.get("posture") != "standing":
        return "seal"
    return (head.get("fates") or {}).get(domain, "seal")


def shred_method(head: dict | None, domain: str) -> str:
    """§8 lock 5, pure: an escrowed domain shreds GOVERNED (attested death +
    cooling-off + 0026's doors, stubs survive); an unescrowed one shreds by
    KEY MORTALITY — mathematics, no detector needs to be right about death."""
    if head and (head.get("escrow") or {}).get(domain) is False:
        return "key-mortality"
    return "governed"


def may_attest(head: dict | None, did: str) -> bool:
    """The roster gate: only the named may stage a death — the executor or a
    witness. Detection stages, never decides (0013 §3); this gate is about
    who may even STAGE."""
    if not head or head.get("posture") != "standing":
        return False
    return did == head.get("executor") or did in (head.get("witnesses") or [])


def attestation_met(head: dict | None, attestors: list, evidence_refs: list,
                    *, registry: bool = False) -> bool:
    """§8 lock 3, pure: quorum 2 turns SEALED into ATTESTED — the executor +
    an evidence artifact (0029) + one named witness, or registry evidence
    standing as the second voice. Below the bar nothing executes, ever
    (bars are absolute, 0012 §5) — and approval only STARTS the cooling-off,
    where any entitled voice aborts."""
    if not head or head.get("posture") != "standing":
        return False
    if not head.get("executor") or head["executor"] not in (attestors or []):
        return False
    if not evidence_refs:
        return False
    return registry or any(w in (attestors or [])
                           for w in head.get("witnesses") or [])


def may_read_legacy(head: dict | None, did: str, domain: str) -> bool:
    """The survivors' door (0035 §6): the disclosure map IS the dead's consent,
    fixed at close. Absent an entry, the door is closed — grief is not an
    entitlement (§5)."""
    if not head:
        return False
    return did in ((head.get("disclosure") or {}).get(domain) or [])


def narrowed_ok(old: dict, new: dict) -> bool:
    """§8 lock 4, pure: heirs narrow, never widen — every door the new map
    holds must already stand in the old. The dead's consent is not
    renegotiable (the testament is a floor; tighten-only, applied to
    inheritance)."""
    for domain, dids in (new or {}).items():
        if domain not in (old or {}):
            return False
        if not set(dids) <= set(old[domain]):
            return False
    return True


# ---------------------------------------------------------------- the passage (0035 §3)

# The states a universe walks when its human goes quiet. EXECUTED and LEGACY
# are declared here so the edges can be law today; the walk that reaches them
# is spoonful 3's. Silence may only CONTAIN (§8 lock 1): the only edges
# silence drives are living→unresponsive→sealed — everything past SEALED
# takes attested death, and everything before EXECUTED reverses.
PASSAGE_STATES = ("living", "unresponsive", "sealed", "attested",
                  "executed", "legacy")

# The legal edges. A missing pair is a refused transition — most notably
# nothing leaves EXECUTED or LEGACY toward the living (a closed worldline
# never reopens, §5) and nothing reaches ATTESTED except from SEALED (a
# living universe cannot be attested dead).
_PASSAGE_EDGES = {
    ("living", "unresponsive"),       # silence past the window — reach out
    ("unresponsive", "sealed"),       # still silent — contain, reversibly
    ("unresponsive", "living"),       # the reach-out was answered
    ("sealed", "living"),             # one heartbeat unseals
    ("sealed", "attested"),           # quorum 2 + evidence, at the gate
    ("attested", "sealed"),           # an entitled voice aborts — one voice saves
    ("attested", "living"),           # the loudest abort is a heartbeat
    ("attested", "executed"),         # cooling-off passed, no voice — sp3's walk
    ("executed", "legacy"),           # the standing state — sp4's door
}

# The cooling-off on an attested death (0012 §3: approved-but-held), a named
# default in days — probate-shaped. Design-owner call, JB may veto; a future
# testament field may carry it per-universe.
ATTESTATION_COOLING_DAYS = 7


def may_transition(current: str, nxt: str) -> bool:
    """The edge law, pure: the passage walks its machine and nothing else —
    no shortcut from living to sealed, no return from the closed states."""
    return (current, nxt) in _PASSAGE_EDGES


def silence_verdict(silence_days: int, last_act_at: str, now: str,
                    *, unit_secs: int = 86400) -> str:
    """§8 lock 1, pure: what silence alone may justify. Within the window —
    living; past it — unresponsive (the seats reach out, and the reach-out
    gets a full window of its own to be answered); past twice the window —
    sealed. Never more: execution is attestation's alone. `unit_secs` scales
    a testament-day for the rig (a dial, never law); no acts on record reads
    as living — a universe with no history has no basis to seal."""
    if not last_act_at:
        return "living"
    from datetime import datetime
    fmt = "%Y-%m-%dT%H:%M:%SZ"
    try:
        quiet = (datetime.strptime(now, fmt)
                 - datetime.strptime(last_act_at[:20].rstrip("Z") + "Z", fmt)
                 ).total_seconds()
    except ValueError:
        return "living"
    window = max(int(silence_days), 1) * int(unit_secs)
    if quiet < window:
        return "living"
    if quiet < 2 * window:
        return "unresponsive"
    return "sealed"


def make_passage(agent: dict, kp, scope: str, state: str, *, reason: str,
                 evidence: list | None = None, attestors: list | None = None,
                 cooling_until: str = "") -> dict:
    """A passage transition on the record (0035 §3): one worldline per
    universe, a sibling per transition, each naming what drove it — the
    machine is legible forever. Detection stages, never decides (0013 §3):
    every record here names a trigger a human can audit."""
    if state not in PASSAGE_STATES:
        raise ValueError(f"unknown passage state: {state!r}")
    body = {"passage": {
        "state": state, "reason": reason,
        **({"evidence": list(evidence)} if evidence else {}),
        **({"attestors": list(attestors)} if attestors else {}),
        **({"cooling_until": cooling_until} if cooling_until else {}),
    }}
    return make_memory(agent, kp, scope, body, kind="semantic",
                       tags=["passage"])


def passage_heads(rows: list[dict]) -> list[dict]:
    """The current head from (id, passage, derived_from, at)-shaped rows,
    oldest first — the worldline idiom, third organ this dive."""
    superseded = {d for r in rows for d in r.get("derived_from") or []}
    return [{"id": r["id"], **r["passage"]} for r in rows
            if r["id"] not in superseded]


def passage_state(head: dict | None) -> str:
    """No passage worldline yet — the universe is living."""
    return (head or {}).get("state", "living")


def seal_active(head: dict | None) -> bool:
    """0026 §3's semantics, worn by the passage: SEALED and ATTESTED are
    contained states — reversible, never conflated with destruction."""
    return passage_state(head) in ("sealed", "attested")


def may_stage_attestation(head: dict | None) -> bool:
    """A living universe cannot be attested dead: only SEALED may move to the
    attestation gate. The guard is structural, not procedural."""
    return passage_state(head) == "sealed"


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
