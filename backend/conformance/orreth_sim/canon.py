# PROVENANCE: Fable 5 (claude-fable-5) — 0039, the Chronicle and the Canon · 2026-07-23
"""The Canon (0039) — spoonful 1: the two books stand.

The record-class registry is itself a Canon asset: every Chronicle class wears
the charter's attributes (RTO · RPO · criticality · classification · retention
min/max — the bridge: in prod, allen's IAC allocates stores per class), and
the PRIVACY FLOOR is data a human can read and gate — profile & consent,
testament & passage, purge stubs & key custody never enter a projection
(locked 2026-07-23). Dispatch and meter internals remain retrievable: "why did
this route there?" stays a stacks question.

The registry is versioned like every Canon entry: changing a class's fate is a
proposal on the lanes, never an edit to code.
"""
from __future__ import annotations

from . import improver

REGISTRY_NAME = "record-classes"

# v1 — the genesis registry. Attributes are the charter's own vocabulary; the
# `retrievable` flag IS the privacy floor, listed where humans can gate it.
CLASSES_V1 = {
    "version": "1",
    "classes": {
        # ---- the Chronicle -------------------------------------------------
        "chronicle-objective": {"criticality": "high", "classification": "internal",
                                "rto": "4h", "rpo": "15m",
                                "retention": {"min": "P7Y", "max": None},
                                "retrievable": True},
        "chronicle-intention": {"criticality": "high", "classification": "internal",
                                "rto": "4h", "rpo": "15m",
                                "retention": {"min": "P7Y", "max": None},
                                "retrievable": True},
        "chronicle-observation": {"criticality": "medium", "classification": "internal",
                                  "rto": "24h", "rpo": "1h",
                                  "retention": {"min": "P90D", "max": None},
                                  "retrievable": True},
        "chronicle-thought": {"criticality": "low", "classification": "internal",
                              "rto": "72h", "rpo": "24h",
                              "retention": {"min": "P30D", "max": "P1Y"},
                              "retrievable": True},
        "dispatch": {"criticality": "medium", "classification": "internal",
                     "rto": "24h", "rpo": "1h",
                     "retention": {"min": "P1Y", "max": None},
                     "retrievable": True},     # "why did this route there?" stays askable
        "knowledge": {"criticality": "medium", "classification": "internal",
                      "rto": "24h", "rpo": "1h",
                      "retention": {"min": "P1Y", "max": None},
                      "retrievable": True},
        "document": {"criticality": "medium", "classification": "internal",
                     "rto": "24h", "rpo": "1h",
                     "retention": {"min": "P1Y", "max": None},
                     "retrievable": True},
        "artifact-pointer": {"criticality": "high", "classification": "internal",
                             "rto": "4h", "rpo": "15m",
                             "retention": {"min": "P7Y", "max": None},
                             "retrievable": True},   # the pointer law: metadata in
                                                     # the mind, mass in the warehouse
        # ---- the privacy floor (locked 2026-07-23) — NEVER project ---------
        "profile": {"criticality": "critical", "classification": "sovereign",
                    "rto": "1h", "rpo": "0", "retention": {"min": None, "max": None},
                    "retrievable": False},
        "consent": {"criticality": "critical", "classification": "sovereign",
                    "rto": "1h", "rpo": "0", "retention": {"min": None, "max": None},
                    "retrievable": False},
        "testament": {"criticality": "critical", "classification": "sovereign",
                      "rto": "1h", "rpo": "0", "retention": {"min": None, "max": None},
                      "retrievable": False},
        "passage": {"criticality": "critical", "classification": "sovereign",
                    "rto": "1h", "rpo": "0", "retention": {"min": None, "max": None},
                    "retrievable": False},
        "purge-stub": {"criticality": "critical", "classification": "regulated",
                       "rto": "1h", "rpo": "0", "retention": {"min": None, "max": None},
                       "retrievable": False},
        "custody": {"criticality": "critical", "classification": "regulated",
                    "rto": "1h", "rpo": "0", "retention": {"min": None, "max": None},
                    "retrievable": False},
    },
}

# tag → class, first match wins (floors first — a record wearing a sovereign
# tag is sovereign no matter what else it wears)
_TAG_CLASS = (
    ("profile", "profile"), ("consent", "consent"),
    ("testament", "testament"), ("passage", "passage"),
    ("purge", "purge-stub"), ("tombstone", "purge-stub"),
    ("custody", "custody"), ("birth-certificate", "custody"),
    ("objective", "chronicle-objective"), ("intention", "chronicle-intention"),
    ("observation", "chronicle-observation"), ("thought", "chronicle-thought"),
    ("dispatch", "dispatch"), ("knowledge", "knowledge"),
    ("artifact-pointer", "artifact-pointer"), ("document", "document"),
)


def plant_registry(node, librarian: dict, librarian_kp) -> str | None:
    """Genesis: the registry enters the shelf as a Canon asset — from here a
    class's fate (its attributes, its floor) is a proposal on the lanes."""
    if improver.active_asset(node, REGISTRY_NAME):
        return None
    rec = improver.make_asset(librarian, librarian_kp, node.scope,
                              name=REGISTRY_NAME, profile=CLASSES_V1)
    return node.write(rec)


def registry(node) -> dict:
    row = improver.active_asset(node, REGISTRY_NAME)
    prof = improver._profile_of(row[1]) if row else {}
    return prof if prof.get("classes") else CLASSES_V1


def class_of(record: dict) -> str:
    """A record's class, read from its tags — floors first, always."""
    tags = [str(t) for t in (record.get("tags") or [])]
    for needle, cls in _TAG_CLASS:
        if any(needle in t for t in tags):
            return cls
    return "chronicle-observation"           # the honest default: it happened


def retrievable(node, record: dict) -> bool:
    """THE PRIVACY FLOOR (0039 §7, locked 2026-07-23): may this record ever
    enter a projection? The registry's word is law, and the registry is a
    Canon entry a human can read — and gate."""
    cls = registry(node).get("classes", {}).get(class_of(record))
    return bool(cls.get("retrievable")) if cls else True


def census(node) -> list[dict]:
    """The Canon census: every versioned asset on this floor's shelf — the
    genome, listed. (The shelf holds only Canon; the census is its roll call.)"""
    seen: dict = {}
    for rid, r in sorted(node.records.items(),
                         key=lambda x: x[1].get("received_at", "")):
        tags = r.get("tags") or []
        if "asset" not in tags:
            continue
        name = next((t for t in tags if t != "asset"), "?")
        seen.setdefault(name, {"name": name, "versions": 0, "head": rid})
        seen[name]["versions"] += 1
        seen[name]["head"] = rid
    return sorted(seen.values(), key=lambda e: e["name"])


# ---------------------------------------------------------------- the dials (0039 §3)
DIALS_NAME = "distillation-dials"

# v1 — the metabolism's dials as a Canon asset: per-class windows and postures.
# Human and Agent+HITL editable from day one (JB's requirement — nobody fully
# understands optimal cross-floor/time distillation yet, so the dials are DATA
# and 0033 measures what each setting costs).
DIALS_V1 = {
    "version": "1",
    "classes": {
        "chronicle-thought": {"rises": False, "recall_window_days": 7},
        "chronicle-observation": {"rises": True, "recall_window_days": 30},
        "chronicle-intention": {"rises": True, "recall_window_days": 90},
        "chronicle-objective": {"rises": True, "recall_window_days": 365},
        "knowledge": {"rises": True, "recall_window_days": 90},
        "document": {"rises": False, "recall_window_days": 90},
        "dispatch": {"rises": False, "recall_window_days": 14},
    },
    "note": "usage is evidence — recalled data stays warm and low (0039 §3, "
            "locked 2026-07-23); every distillation's loss is measured (0033)",
}


def plant_dials(node, librarian: dict, librarian_kp) -> str | None:
    if improver.active_asset(node, DIALS_NAME):
        return None
    rec = improver.make_asset(librarian, librarian_kp, node.scope,
                              name=DIALS_NAME, profile=DIALS_V1)
    return node.write(rec)


def dials(node) -> dict:
    row = improver.active_asset(node, DIALS_NAME)
    prof = improver._profile_of(row[1]) if row else {}
    return prof if prof.get("classes") else DIALS_V1


def _days_since(iso: str, now_iso: str) -> float:
    from datetime import datetime
    try:
        a = datetime.fromisoformat(iso.replace("Z", "+00:00"))
        b = datetime.fromisoformat(now_iso.replace("Z", "+00:00"))
        return (b - a).total_seconds() / 86400.0
    except Exception:
        return 0.0


def metabolism_beat(node, librarian: dict, librarian_kp) -> dict:
    """THE DIALED METABOLISM (0039 sp3): among the undistilled, a record whose
    class window has passed WITHOUT recall distills now — the recalled stay
    warm and low (usage is evidence, locked 2026-07-23). Every distillation's
    information loss is MEASURED (0033's reconstruction entropy) and the
    report lands on the record: tuning becomes evidence, never guesswork."""
    from .identity import NOW
    from .node import make_memory
    dl = dials(node).get("classes", {})
    recalls = getattr(node, "recalls", {})
    now = NOW()
    due, kept_warm = [], 0
    for rid in list(node.undistilled):
        r = node.records.get(rid)
        if r is None:
            continue
        d = dl.get(class_of(r))
        if d is None:
            continue
        window = float(d.get("recall_window_days", 30))
        age = _days_since(r.get("occurred_at", now), now)
        last = (recalls.get(rid) or {}).get("last")
        recent = last and _days_since(last, now) < window
        if age >= window and not recent:
            due.append(rid)
        elif recent:
            kept_warm += 1
    if not due:
        return {"distilled": 0, "kept_warm": kept_warm}
    dist = node._distill(due, push=False)
    for rid in due:
        if rid in node.undistilled:
            node.undistilled.remove(rid)
    from . import infotheory
    did = dist.get("id", "")
    loss = infotheory.reconstruction_entropy(node, did) if did else {}
    report = {"metabolism_report": {
        "distilled": len(due), "kept_warm": kept_warm,
        "distillation": did,
        "loss_bits": loss.get("bits", loss.get("entropy_bits", 0.0)),
        "dials_version": dials(node).get("version", "?"), "at": now}}
    node.write(make_memory(librarian, librarian_kp, node.scope, report,
                           kind="episodic", tags=["metabolism-report"]))
    return report["metabolism_report"]


# ------------------------------------------------- the graduation (0039 §4, sp4)

def crystallize(node, mentor: dict, mentor_kp, *, objective: str, craft: dict,
                rubric: dict, proven_tier: str = "high") -> str:
    """THE MENTOR'S CRAFT (0039 §4): an objective mastered at the smart tier
    becomes a skill on the Canon's shelf — 0001's crystallized memory, carrying
    its acceptance rubric and the tier it was PROVEN at. From here the 0010 law
    guards it: it never silently serves at a tier the rubric hasn't cleared."""
    import re as _re
    slug = _re.sub(r"[^a-z0-9]+", "-", objective.lower()).strip("-")[:40]
    rec = improver.make_asset(mentor, mentor_kp, node.scope,
                              name=f"skill-{slug}",
                              profile={"objective": objective, "craft": craft,
                                       "rubric": {"min_score": float(rubric.get("min_score", 0.8)),
                                                  "n": int(rubric.get("n", 3))},
                                       "proven_tier": proven_tier})
    node.write(rec)
    return f"skill-{slug}"


def canary_run(node, mentee: dict, mentee_kp, skill_name: str, *,
               tier: str, score: float) -> str:
    """One canary pass at the MENTEE's tier, on the record — full observation,
    0011's probation posture. The score arrives from the judge's grading (sim:
    the caller carries it; the wire rides the model gateway's judge). Each run
    carries its ORDINAL — two same-scored runs in the same second are two
    runs, not one (the content-address collision, caught live 2026-07-25 when
    a real judge scored 0.90 twice and the ceremony counted 2/3)."""
    from .identity import NOW
    from .node import make_memory
    prior = sum(1 for r in node.records.values()
                if skill_name in (r.get("tags") or [])
                and "canary" in (r.get("tags") or []))
    body = {"canary": {"skill": skill_name, "tier": tier,
                       "score": round(float(score), 4),
                       "run": prior + 1, "at": NOW()}}
    return node.write(make_memory(mentee, mentee_kp, node.scope, body,
                                  kind="episodic", tags=["canary", skill_name]))


def graduate(node, mentor: dict, mentor_kp, skill_name: str, *,
             mentee_tier: str) -> dict:
    """THE CEREMONY: the standings speak — canary runs at the mentee's tier
    against the rubric. Cleared → a NEW skill version proven at the cheap tier
    (a sibling, never a silent successor) + the graduation on the record.
    Short → an honest refusal; the mentor keeps the work. Never silently
    dumber — 0010's oldest promise, extended to lifecycles."""
    import json as _json

    from . import crypto as _c
    from .identity import NOW
    from .node import make_memory
    row = improver.active_asset(node, skill_name)
    if row is None:
        raise ValueError(f"no skill named {skill_name} on the shelf")
    prof = improver._profile_of(row[1])
    rubric = prof.get("rubric") or {}
    runs = []
    for r in node.records.values():
        if skill_name in (r.get("tags") or []) and "canary" in (r.get("tags") or []):
            b = _json.loads(_c._b64d(r["body"]).decode()).get("canary") or {}
            if b.get("tier") == mentee_tier:
                runs.append(float(b.get("score", 0)))
    need_n, floor_ = int(rubric.get("n", 3)), float(rubric.get("min_score", 0.8))
    mean = sum(runs) / len(runs) if runs else 0.0
    if len(runs) < need_n or mean < floor_:
        verdict = {"graduated": False, "tier": mentee_tier, "runs": len(runs),
                   "mean": round(mean, 4), "rubric": rubric,
                   "why": f"the mentee has not earned it — {len(runs)}/{need_n} "
                          f"run(s), mean {mean:.2f} vs floor {floor_:.2f}; the "
                          "mentor keeps the work (0010: never silently dumber)"}
    else:
        sibling = improver.make_asset(mentor, mentor_kp, node.scope,
                                      name=skill_name,
                                      profile={**prof, "proven_tier": mentee_tier},
                                      derived_from=[row[0]])
        node.write(sibling)
        verdict = {"graduated": True, "tier": mentee_tier, "runs": len(runs),
                   "mean": round(mean, 4), "rubric": rubric,
                   "version": sibling["id"],
                   "why": f"the rubric cleared at the mentee's tier — mean "
                          f"{mean:.2f} over {len(runs)} watched run(s); the "
                          "cheap tier serves, the graduation is on the record"}
    node.write(make_memory(mentor, mentor_kp, node.scope,
                           {"graduation": {**verdict, "skill": skill_name,
                                           "at": NOW()}},
                           kind="episodic", tags=["graduation", skill_name]))
    return verdict


# ------------------------------------------------- the pointer law's door (0039 §6)

def make_pointer(node, author: dict, author_kp, *, name: str, uri: str,
                 content_hash: str, meta: dict | None = None,
                 derived_from: list | None = None) -> str:
    """BULK NEVER ENTERS THE MIND (0039 §6): the artifact-pointer record —
    signed pointer + content hash + metadata + lineage; the mass rests in its
    class-allocated store. The hash is the handshake: the warehouse can never
    quietly swap the goods."""
    from .node import make_memory
    if not uri or not content_hash:
        raise ValueError("a pointer names its store AND its hash — or it points at fog")
    body = {"artifact_pointer": {"name": name, "uri": uri,
                                 "content_hash": content_hash,
                                 "meta": dict(meta or {})}}
    rec = make_memory(author, author_kp, node.scope, body, kind="semantic",
                      tags=["artifact-pointer", name])
    if derived_from:
        rec["derived_from"] = list(derived_from)
    return node.write(rec)


def verify_pointer(node, pointer_id: str, actual_hash: str) -> bool:
    """The handshake at fetch time: the goods must match the signed hash —
    a swap is a rug-pull, loud, never silent."""
    import json as _json

    from . import crypto as _c
    r = node.records.get(pointer_id)
    if r is None:
        return False
    b = _json.loads(_c._b64d(r["body"]).decode()).get("artifact_pointer") or {}
    return bool(actual_hash) and actual_hash == b.get("content_hash")


def demote(node, mentor: dict, mentor_kp, skill_name: str, *,
           evidence: str) -> dict:
    """DEMOTION BY EVIDENCE (0039 §4.4): drift at the mentee's tier re-opens
    the Canon entry — a sibling version proven back at the mentor's tier, the
    demotion on the record beside the graduation. The loop runs both ways,
    forever."""
    from .identity import NOW
    from .node import make_memory
    row = improver.active_asset(node, skill_name)
    if row is None:
        raise ValueError(f"no skill named {skill_name}")
    prof = improver._profile_of(row[1])
    sibling = improver.make_asset(mentor, mentor_kp, node.scope, name=skill_name,
                                  profile={**prof, "proven_tier": "high",
                                           "demoted_from": row[0]},
                                  derived_from=[row[0]])
    node.write(sibling)
    node.write(make_memory(mentor, mentor_kp, node.scope,
                           {"demotion": {"skill": skill_name,
                                         "evidence": evidence[:300],
                                         "back_to": "high", "at": NOW()}},
                           kind="episodic", tags=["demotion", skill_name]))
    return {"demoted": True, "back_to": "high", "version": sibling["id"]}
