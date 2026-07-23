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
