# PROVENANCE: Fable 5 (claude-fable-5) — 0042, the Deed · 2026-07-25
"""The Deed (0042) — spoonful 1: the shelf and the family.

No external consequence is complete merely because its executor says it is.
Every world-touching act belongs to an EFFECT CLASS — a versioned Canon asset
declaring reversibility, idempotency, its independent observer, its blast
radius, and its CEREMONY TIER (locked 2026-07-25: four tiers, T0–T3). A deed
of a witnessed class walks the family — intent → authorization → attempt →
receipt → observation → reconciliation → closure — each record signed and
chained, the observation authored by a seat that is NOT the actor (0005's law
grown into the world). The whisper floor is proven both directions: a T0 deed
carries no family, and a whisper-class deed that reaches for ceremony is
refused. Compensation waits at the gate (0041's refusal, mirrored): nothing
compensates without a fresh human word, and the compensating deed walks its
own family — the recursion is priced, never free.
"""
from __future__ import annotations

import json as _json

from . import crypto as _c
from . import improver
from .identity import NOW
from .node import make_memory

CLASSES_NAME = "effect-classes"

# v1 roster (locked 2026-07-25): the ceremony dial proven both directions.
CLASSES_V1 = {
    "version": "1",
    "classes": {
        "estate-apply": {
            "tier": "T3", "target": "the aws estate",
            "reversibility": "compensable",
            "idempotency": "one plan-hash, one apply",
            "observer": "allen's read-only observers (0037)",
            "observation_delay_s": 30, "timeout_posture": "contain (0035)",
            "compensation": "stage the reverse apply at the gate — nothing deleted, the stack walked back",
            "blast_radius": "one stack"},
        "outbound-publish": {
            "tier": "T2", "target": "the public web",
            "reversibility": "compensable",
            "idempotency": "one artifact-hash, one publish",
            "observer": "a distinct floor seat, fetch-back through the public door",
            "observation_delay_s": 10, "timeout_posture": "unobserved is a state, never success",
            "compensation": "stage the unpublish at the gate",
            "blast_radius": "one artifact"},
        "note": {
            "tier": "T0", "target": "the floor's own rollup",
            "reversibility": "reversible",
            "idempotency": "none needed", "observer": "none — a whisper",
            "compensation": "", "blast_radius": "none"},
    },
}

_ROLES = ("intent", "authorization", "attempt", "receipt",
          "observation", "reconciliation", "closure", "compensation")

# what each tier's closure demands on the record (T1 collapses, sp1 ships none)
_TIER_NEEDS = {
    "T2": ("authorization", "attempt", "receipt", "observation", "reconciliation"),
    "T3": ("authorization", "attempt", "receipt", "observation", "reconciliation"),
}


def plant_classes(node, agent: dict, kp) -> str | None:
    """Genesis: the effect classes enter the shelf as ONE Canon asset — from
    here a class's ceremony is a proposal on the lanes, never an edit."""
    if improver.active_asset(node, CLASSES_NAME):
        return None
    rec = improver.make_asset(agent, kp, node.scope,
                              name=CLASSES_NAME, profile=CLASSES_V1)
    return node.write(rec)


def classes(node) -> dict:
    row = improver.active_asset(node, CLASSES_NAME)
    prof = improver._profile_of(row[1]) if row else {}
    return prof if prof.get("classes") else CLASSES_V1


def effect_class(node, name: str) -> dict:
    cls = classes(node).get("classes", {}).get(name)
    if cls is None:
        raise ValueError(f"no effect class named {name} — the world's grammar "
                         "does not know this act (propose it on the lanes)")
    return cls


def _body(r: dict) -> dict:
    return _json.loads(_c._b64d(r["body"]).decode())


def _family(node, deed_id: str) -> dict:
    """role → (record_id, inner body), the walkable chain."""
    fam: dict = {}
    for rid, r in sorted(node.records.items(),
                         key=lambda x: x[1].get("received_at", "")):
        tags = r.get("tags") or []
        if "deed" not in tags:
            continue
        role = next((t for t in tags if t in _ROLES), None)
        if role is None:
            continue
        b = _body(r).get(role) or {}
        if rid == deed_id or b.get("deed") == deed_id:
            fam[role] = (rid, b, r)
    return fam


def walk(node, deed_id: str) -> list[tuple[str, str]]:
    """The auditor's walk: (role, record_id) in the family's order."""
    fam = _family(node, deed_id)
    return [(role, fam[role][0]) for role in _ROLES if role in fam]


# ------------------------------------------------------------- the family

def open_deed(node, actor: dict, kp, *, effect: str, change: str,
              objective: str) -> str:
    """INTENT — what change, for which Objective (0030: a human at the
    origin), under which class's law. A whisper class opens no family."""
    cls = effect_class(node, effect)
    if cls.get("tier") == "T0":
        raise ValueError("a whisper-class deed carries no family — "
                         "deed_note() is its whole ceremony (0042 §3)")
    body = {"intent": {"effect": effect, "change": change,
                       "objective": objective, "at": NOW()}}
    return node.write(make_memory(actor, kp, node.scope, body,
                                  kind="episodic", tags=["deed", "intent"]))


def authorize(node, authority: dict, kp, deed_id: str, *, budget: float,
              window_s: int, idempotency_key: str) -> str:
    """AUTHORIZATION — the gate record: authority, budget, validity window,
    the duplicate-detection key. A sworn (T3) deed names its way back BEFORE
    it steps: the class must declare compensation or the gate refuses."""
    fam = _family(node, deed_id)
    if "intent" not in fam:
        raise ValueError("no intent stands — a deed begins by saying what it means to do")
    cls = effect_class(node, fam["intent"][1]["effect"])
    if cls.get("tier") == "T3" and not cls.get("compensation"):
        raise ValueError("a sworn deed names its way back before it steps — "
                         "this class declares no compensation (0042 §3, T3)")
    body = {"authorization": {"deed": deed_id, "authority": authority["did"],
                              "budget": float(budget), "window_s": int(window_s),
                              "key": idempotency_key, "at": NOW()}}
    rec = make_memory(authority, kp, node.scope, body, kind="episodic",
                      tags=["deed", "authorization"])
    rec["derived_from"] = [deed_id]
    return node.write(rec)


def attempt(node, actor: dict, kp, deed_id: str, *, manifests: dict,
            epoch: str) -> str:
    """ATTEMPT — what the actuator did, under which machine (0041's clasp:
    the attempt cites the standing epoch, or it floats free of law). The
    idempotency key is the class's promise: inside this deed a repeat is the
    SAME attempt; across deeds the key remembers, and refuses."""
    fam = _family(node, deed_id)
    if "authorization" not in fam:
        raise ValueError("no authorization stands — the gate speaks before the hand moves")
    if not epoch:
        raise ValueError("the attempt names the machine that made it (0041) — no epoch, no deed")
    key = fam["authorization"][1].get("key", "")
    if "attempt" in fam:                       # same deed, same key: one attempt
        return fam["attempt"][0]
    for rid, r in node.records.items():        # the key remembers across deeds
        tags = r.get("tags") or []
        if "deed" in tags and "attempt" in tags:
            b = _body(r).get("attempt") or {}
            if key and b.get("key") == key and b.get("deed") != deed_id:
                raise ValueError(f"the key remembers — this change already rode "
                                 f"deed {b.get('deed', '?')[:18]}… (idempotency, 0042 §5)")
    body = {"attempt": {"deed": deed_id, "manifests": dict(manifests),
                        "key": key, "epoch": epoch, "at": NOW()}}
    rec = make_memory(actor, kp, node.scope, body, kind="episodic",
                      tags=["deed", "attempt"])
    rec["derived_from"] = [fam["authorization"][0]]
    return node.write(rec)


def receipt(node, actor: dict, kp, deed_id: str, *, acknowledged: dict) -> str:
    """RECEIPT — what the target acknowledged. Kept verbatim, trusted never."""
    fam = _family(node, deed_id)
    if "attempt" not in fam:
        raise ValueError("no attempt stands — a receipt without an attempt is a rumor")
    body = {"receipt": {"deed": deed_id, "acknowledged": dict(acknowledged),
                        "at": NOW()}}
    rec = make_memory(actor, kp, node.scope, body, kind="episodic",
                      tags=["deed", "receipt"])
    rec["derived_from"] = [fam["attempt"][0]]
    return node.write(rec)


def observe(node, observer: dict, kp, deed_id: str, *, found: dict) -> str:
    """OBSERVATION — what a DIFFERENT seat found true through a read-only
    door. The actor is not the sole witness of its own success: an observation
    authored by the attempt's own seat is refused (0005, grown up)."""
    fam = _family(node, deed_id)
    if "attempt" not in fam:
        raise ValueError("nothing to observe — no attempt stands")
    if observer["did"] == fam["attempt"][2].get("author"):
        raise ValueError("the actor is not the sole witness of its own success — "
                         "observation needs a seat that is not the doer (0042 §4)")
    body = {"observation": {"deed": deed_id, "found": dict(found), "at": NOW()}}
    rec = make_memory(observer, kp, node.scope, body, kind="episodic",
                      tags=["deed", "observation"])
    rec["derived_from"] = [fam["attempt"][0]]
    return node.write(rec)


def reconcile(node, author: dict, kp, deed_id: str, *, expected: dict) -> dict:
    """RECONCILIATION — expected against OBSERVED (never against the receipt:
    acknowledgment is not the world). A mismatch STAGES the class's declared
    compensation — detection wears no levers here either (0041 §4, extended)."""
    fam = _family(node, deed_id)
    if "observation" not in fam:
        raise ValueError("nothing to reconcile against — the witness has not spoken")
    observed = fam["observation"][1].get("found") or {}
    holds = all(observed.get(k) == v for k, v in expected.items())
    cls = effect_class(node, fam["intent"][1]["effect"])
    verdict = {"deed": deed_id, "holds": holds,
               "expected": dict(expected), "observed": observed, "at": NOW()}
    if not holds:
        verdict["staged"] = {"compensation": cls.get("compensation", ""),
                             "note": "staged, never enacted — a human's word "
                                     "turns the key (0042 §5, locked)"}
    rec = make_memory(author, kp, node.scope, {"reconciliation": verdict},
                      kind="episodic", tags=["deed", "reconciliation"])
    rec["derived_from"] = [fam["observation"][0]]
    node.write(rec)
    return verdict


def close(node, author: dict, kp, deed_id: str, *, uncertainty: str) -> str:
    """CLOSURE — the evidence-backed verdict AND the remaining uncertainty,
    named. The tier's roles must stand on the record; a wrong world does not
    close — compensation waits at the gate."""
    if not uncertainty:
        raise ValueError("closure names its remaining uncertainty — certainty is never a default")
    fam = _family(node, deed_id)
    cls = effect_class(node, fam["intent"][1]["effect"])
    for role in _TIER_NEEDS.get(cls.get("tier"), ()):
        if role not in fam:
            raise ValueError(f"a {cls.get('tier')} deed closes only with its "
                             f"{role} on the record — the family is the proof (0042 §2)")
    if not fam["reconciliation"][1].get("holds"):
        raise ValueError("a wrong world does not close — compensation waits at the gate (0042 §5)")
    body = {"closure": {"deed": deed_id, "holds": True,
                        "uncertainty": uncertainty, "at": NOW()}}
    rec = make_memory(author, kp, node.scope, body, kind="episodic",
                      tags=["deed", "closure"])
    rec["derived_from"] = [fam["reconciliation"][0]]
    return node.write(rec)


def compensate(node, actor: dict, kp, deed_id: str, *, human_word: bool,
               objective: str) -> str:
    """COMPENSATION — only on a fresh human word (locked 2026-07-25: nothing
    compensates unasked), and the reversal is ITSELF a deed of the same class,
    opened here, walking its own family — the recursion priced, never free."""
    if not human_word:
        raise ValueError("nothing compensates without a fresh human word — "
                         "the gate holds the diff (0042 §5, locked)")
    fam = _family(node, deed_id)
    if "reconciliation" not in fam or fam["reconciliation"][1].get("holds"):
        raise ValueError("nothing to compensate — the world holds, or was never reconciled")
    cls_name = fam["intent"][1]["effect"]
    comp_deed = open_deed(node, actor, kp, effect=cls_name,
                          change=f"compensate deed {deed_id[:18]}…: "
                                 + effect_class(node, cls_name).get("compensation", ""),
                          objective=objective)
    body = {"compensation": {"deed": deed_id, "opens": comp_deed, "at": NOW()}}
    rec = make_memory(actor, kp, node.scope, body, kind="episodic",
                      tags=["deed", "compensation"])
    rec["derived_from"] = [fam["reconciliation"][0]]
    node.write(rec)
    return comp_deed


# ------------------------------------------------------------- the whisper

def deed_note(node, actor: dict, kp, *, text: str) -> str:
    """T0 — the whisper: one record in the rollup's hearing, no family.
    The universe must not drown in receipts for trivialities (0042 §3)."""
    body = {"note": {"text": text[:200], "at": NOW()}}
    return node.write(make_memory(actor, kp, node.scope, body,
                                  kind="episodic", tags=["deed-note"]))
