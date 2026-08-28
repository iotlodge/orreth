# PROVENANCE: Fable 5 (claude-fable-5) — the dial registry (0063 sp1) · 2026-08-28
"""The machine's operating values, DECLARED — 0063's first machinery.

The separation is L1's own condition (JB, 2026-08-28): a dial's SHAPE is
firmware and lives here — name, type, unit, bounds, what it governs, its
blast radius, and the why that chose it. Its VALUE is purpose and lives on
the shelf as a `dial-*` asset, turned through the one-motion craft-edit
door like any craft — versioned siblings, lineage kept, never a code edit.
Words steer minds; dials steer the machine — one shelf, two clearly
separate drawers.

Genesis honors the env (0063 §3.6 — env demotes to genesis): the ORRETH_*
variable seeds the FIRST value on a fresh rig, never the standing one.
The read-side law lives in parse(): a head that refuses its declaration
falls back to genesis LOUDLY, never silently.
"""
from __future__ import annotations

import os

# window.html carries this same map as ITS genesis fallback — the two must
# match byte-for-byte (rule 7: one world, one picture; the conformance
# suite holds the parity)
KINDRANK_GENESIS = {
    "attestation": 0, "testament": 1, "consent": 2, "passage": 2,
    "publish": 3, "drift": 3, "release": 3, "witness": 3, "fuel": 3,
    "objective": 4, "improvement": 4, "experiment": 4, "commission": 4,
    "subscription": 4,
    "design-change": 5, "calibration": 5, "estate-adopt": 5, "field-join": 5,
    "join": 6, "ecosystem": 6, "dial": 6, "question": 7,
}

DIALS_V1 = {
    "search-daily": {
        "type": "int", "unit": "searches per UTC day", "min": 0, "max": 100,
        "genesis": int(os.environ.get("ORRETH_SEARCH_DAILY", "6")),
        "governs": "live web searches the whole rig may spend in one day",
        "blast": "money — the family the Tavily thousand-credit burn came from",
        "why": "six covers a study day; sized after the Aug-2026 credit burn",
        "horizon": "takes hold within a minute",
    },
    "assay-ceiling": {
        "type": "int", "unit": "tokens per UTC day", "min": 0, "max": 1000000,
        "genesis": int(os.environ.get("ORRETH_ASSAY_DAILY_TOKENS", "25000")),
        "governs": "vera's independent-judge budget per day (0043 G5)",
        "blast": "money and judgment — too low mutes the examiner, "
                 "too high spends unwatched",
        "why": "a day of assays at ~120 tokens each, with honest slack",
        "horizon": "takes hold within a minute",
    },
    "kindrank": {
        "type": "ordering", "unit": "request kind → rank, gravest first",
        "genesis": KINDRANK_GENESIS,
        "governs": "which grievance reaches the human first in the one Inbox",
        "blast": "attention — a wrong order buries the gravest card",
        "why": "attestations and testaments before questions (0052 sp3's "
               "triage); unlisted kinds rank 8",
        "horizon": "takes hold at the glass's next dictionary fetch "
                   "(about a minute)",
    },
}


def teachings(short: str) -> dict:
    """The declaration's face for a record body and the glass: what the human
    reads BESIDE the value — every version carries its own teaching, so a
    dial record can never be a bare number with amnesia."""
    d = DIALS_V1[short]
    t = {k: d[k] for k in ("type", "unit", "governs", "blast", "why",
                           "horizon")}
    if d["type"] == "int":
        t["bounds"] = [d["min"], d["max"]]
    return t


def gate_check(asset_name: str, profile):
    """The DOOR's law (0063 sp2 — bounds are law, refused BEFORE landing):
    returns (flaw, normalized_profile). A flaw means nothing lands and the
    refusal teaches — the bounds, the unit, what the dial governs. A clean
    turn lands CANONICAL (\"2\" becomes 2): the head never carries a shape
    the declaration would refuse at read time."""
    short = asset_name[len("dial-"):]
    d = DIALS_V1.get(short)
    if d is None:
        return (f"no declared dial is named “{asset_name}” — a dial's SHAPE "
                f"is firmware, and the registry declares only: "
                + ", ".join(f"dial-{s}" for s in sorted(DIALS_V1)), None)
    if not isinstance(profile, dict) or "value" not in profile:
        return ("a dial turns by its value alone — the body is "
                "{\"value\": …}, nothing else", None)
    v, flaw = parse(short, profile["value"])
    if flaw:
        return (f"{flaw} — the declaration holds ({d['unit']}); this dial "
                f"governs {d['governs']}, and its blast is {d['blast']}", None)
    return None, {"value": v}


def parse(short: str, raw):
    """The read-side law: (value, flaw). A flawed head never breaks an organ
    — genesis serves and the flaw is the caller's to confess out loud."""
    d = DIALS_V1[short]
    if d["type"] == "int":
        try:
            v = int(raw)
        except (TypeError, ValueError):
            return d["genesis"], f"not a whole number: {raw!r}"
        if not (d["min"] <= v <= d["max"]):
            return d["genesis"], (f"outside the declared bounds "
                                  f"[{d['min']}..{d['max']}]: {v}")
        return v, None
    if d["type"] == "ordering":
        if not isinstance(raw, dict) or not raw:
            return d["genesis"], "not a kind→rank map"
        try:
            return {str(k): int(v) for k, v in raw.items()}, None
        except (TypeError, ValueError):
            return d["genesis"], "every rank must be a whole number"
    return d["genesis"], f"unknown dial type {d['type']!r}"
