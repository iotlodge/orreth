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
