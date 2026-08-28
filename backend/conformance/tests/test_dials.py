# PROVENANCE: Fable 5 (claude-fable-5) — the dial registry (0063 sp1) · 2026-08-28
"""The Dynamic Universe's first machinery: the machine's operating values,
declared as firmware, valued on the shelf.

Under test: the read-side law (a head that refuses its declaration falls back
to genesis with the flaw NAMED, never silently), the bounds, the ordering
dial's parse — and rule 7 held across the glass boundary: window.html's
KINDRANK genesis literal must match orreth_sim.dials.KINDRANK_GENESIS
byte-for-byte, because a fallback that disagrees with the registry would
show two different triage orders for one Inbox.
"""
import json
import re
from pathlib import Path

from orreth_sim import dials


def test_int_dial_parses_and_holds_bounds():
    v, flaw = dials.parse("search-daily", "3")
    assert v == 3 and flaw is None
    v, flaw = dials.parse("search-daily", 101)
    assert v == dials.DIALS_V1["search-daily"]["genesis"]
    assert "bounds" in flaw
    v, flaw = dials.parse("assay-ceiling", "not-a-number")
    assert v == dials.DIALS_V1["assay-ceiling"]["genesis"]
    assert "whole number" in flaw


def test_ordering_dial_parses_a_map_and_refuses_junk():
    v, flaw = dials.parse("kindrank", {"attestation": 0, "question": 9})
    assert v == {"attestation": 0, "question": 9} and flaw is None
    v, flaw = dials.parse("kindrank", "gravest-first")
    assert v == dials.KINDRANK_GENESIS and flaw is not None
    v, flaw = dials.parse("kindrank", {"question": "first"})
    assert v == dials.KINDRANK_GENESIS and "whole number" in flaw


def test_every_declaration_wears_its_teaching():
    for short, d in dials.DIALS_V1.items():
        for key in ("type", "unit", "genesis", "governs", "blast", "why",
                    "horizon"):
            assert d.get(key) not in (None, ""), f"dial {short} lacks {key}"
        if d["type"] == "int":
            assert d["min"] <= d["genesis"] <= d["max"], \
                f"dial {short}'s genesis falls outside its own bounds"


def test_glass_kindrank_genesis_matches_the_registry():
    """Rule 7 — one world, one picture: the glass's fallback literal and the
    registry's genesis are the same map, or the Inbox could triage two ways."""
    glass = (Path(__file__).resolve().parents[2] / "plane" / "crates"
             / "orrethd" / "src" / "window.html").read_text()
    m = re.search(r"let KINDRANK=\{(.*?)\};", glass, re.S)
    assert m, "window.html no longer declares its KINDRANK genesis literal"
    body = "{" + m.group(1) + "}"
    body = re.sub(r"([{,]\s*)([A-Za-z-]\w*(?:-\w+)*)(\s*:)", r'\1"\2"\3', body)
    assert json.loads(body) == dials.KINDRANK_GENESIS
