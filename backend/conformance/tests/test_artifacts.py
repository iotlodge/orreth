# PROVENANCE: authored by Fable 5 (claude-fable-5), 2026-07-11 — 0029, Multimodal Capability
"""Multimodal admission (0029): upload is an ask, the bars wear one face, text
extracts quarantined, dark formats park their eye, and agents reach documents
through a skill."""
import pytest

from orreth_sim import artifacts
from orreth_sim.librarian import parked_intents
from orreth_sim.node import Refusal
from orreth_sim.world import build


@pytest.fixture()
def world():
    return build()


def _lib(world):
    ident, kp = world.becky.issue_identity("instance", "u:demo", resident=True)
    return ident, kp


def test_the_bars_wear_one_face():
    """JB lock: 256KB · known types. Oversize and foreign type refuse with the
    SAME face — a prober learns nothing about which bar it hit."""
    with pytest.raises(Refusal) as big:
        artifacts.check_policy("notes.txt", b"x" * (artifacts.MAX_BYTES + 1))
    with pytest.raises(Refusal) as alien:
        artifacts.check_policy("payload.exe", b"tiny")
    assert str(big.value) == str(alien.value) == Refusal.PUBLIC


def test_text_upload_extracts_quarantined_with_lineage(world):
    ident, kp = _lib(world)
    receipt = artifacts.admit_upload(world.universe, ident, kp,
                                     "notes.md", "text/markdown",
                                     b"# Cold-weather builds\ntriple glazing wins")
    assert receipt["status"] == "extracted"
    art = world.universe.records[receipt["artifact"]]
    assert "artifact" in art["tags"]
    assert art["provenance_class"] == "ingested-archive"   # an archive, never lived
    ext = world.universe.records[receipt["extraction"]]
    assert receipt["artifact"] in ext["derived_from"]      # the reading cites the page
    assert "knowledge" in ext["tags"] and "document" in ext["tags"]


def test_dark_formats_admit_and_park_the_eye(world):
    """JB lock: the universe keeps what you hand it and remembers it owes you the
    reading — the parked list IS the retry list when a vision mind saddles."""
    ident, kp = _lib(world)
    png = b"\x89PNG\r\n\x1a\n" + b"\x00" * 64
    receipt = artifacts.admit_upload(world.universe, ident, kp,
                                     "diagram.png", "image/png", png)
    assert receipt["status"] == "dark"
    parked = world.universe.records[receipt["parked"]]
    assert receipt["artifact"] in parked["derived_from"]
    assert "knowledge-intent" in parked["tags"]
    # ...and it sits on the librarian's real worklist (0014's lot)
    lot = parked_intents(world.universe)
    assert any(rid == receipt["parked"] for rid, _ in lot)


def test_agents_reach_documents_through_a_skill(world):
    ident, kp = _lib(world)
    artifacts.admit_upload(world.universe, ident, kp, "notes.md", "text/markdown",
                           b"triple glazing wins below -20C")
    artifacts.admit_upload(world.universe, ident, kp, "dark.png", "image/png",
                           b"\x89PNG....")
    read = artifacts.document_skill(world.universe)
    hit = read("what wins for glazing?")
    assert "triple glazing" in hit and "untrusted" in hit   # provenance is UI (0008)
    assert "dark.png" not in hit                            # the unread never pretends
