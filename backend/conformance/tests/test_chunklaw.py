# PROVENANCE: Claude Fable 5 (claude-fable-5) — 0065 sp2, the chunk law's suite · 2026-09-09
"""Rebuildable therefore disposable: cutting is deterministic, spans are
lossless, the policy names its rows, the tree never invents structure, and
the purge reaches every row."""
import pytest

from orreth_sim import chunklaw

POL = {"chunk_chars": 280, "overlap_chars": 40}
TEXT = ("rammed earth walls breathe with the seasons and hold the day's heat "
        "for the night. " * 30)


def test_rebuild_identical():
    a = chunklaw.rows_for(TEXT, "document", POL)
    b = chunklaw.rows_for(TEXT, "document", POL)
    assert a == b and len(a) > 1, "the same text under the same policy is " \
                                  "byte-identical rows, forever"


def test_spans_are_lossless_and_overlap_by_policy():
    rows = chunklaw.rows_for(TEXT, "document", POL)
    assert rows[0]["span"][0] == 0 and rows[-1]["span"][1] == len(TEXT)
    for prev, cur in zip(rows, rows[1:]):
        assert cur["span"][0] == prev["span"][0] + (280 - 40), \
            "the step is size minus overlap — project()'s own walk"
        assert cur["span"][0] < prev["span"][1], "neighbors overlap by policy"


def test_the_hash_catches_reader_cutter_drift():
    rows = chunklaw.rows_for(TEXT, "document", POL)
    s, e = rows[3]["span"]
    import hashlib
    assert rows[3]["hash"] == hashlib.sha256(
        TEXT[s:e].encode()).hexdigest()[:16]


def test_a_turned_policy_wears_a_new_name():
    assert chunklaw.policy_hash(POL) != chunklaw.policy_hash(
        {"chunk_chars": 300, "overlap_chars": 40})
    assert chunklaw.policy_hash(POL) == chunklaw.policy_hash(dict(POL))


def test_unknown_lane_refuses_naming_the_lanes():
    with pytest.raises(ValueError, match="document"):
        chunklaw.rows_for(TEXT, "gossip", POL)


def test_tree_parents_cover_exactly_their_children():
    rows = chunklaw.rows_for(TEXT * 4, "document", POL)
    tree = chunklaw.tree_for(rows, levels=2)
    l1 = [t for t in tree if t["level"] == 1]
    assert l1, "a long text earns structure"
    covered = [s for t in l1 for s in t["covers"]]
    assert covered == [r["seq"] for r in rows], \
        "every leaf under exactly one parent, in order"
    for t in l1:
        assert t["span"] == [rows[t["covers"][0]]["span"][0],
                             rows[t["covers"][-1]]["span"][1]]


def test_a_short_text_earns_no_tree():
    rows = chunklaw.rows_for("one small note", "document", POL)
    assert chunklaw.tree_for(rows, levels=2) == [], \
        "structure that does not exist is never invented"


def test_purge_reaches_rows_and_tree_alike():
    book = {}
    rows = chunklaw.rows_for(TEXT * 4, "document", POL)
    ph = chunklaw.policy_hash(POL)
    chunklaw.put(book, "rec-1", ph, rows, chunklaw.tree_for(rows))
    assert chunklaw.evict(book, "rec-1") > len(rows), "rows AND tree died"
    assert "rec-1" not in book and chunklaw.evict(book, "rec-1") == 0


def test_worklist_lists_the_uncut_and_the_stale_never_the_purged():
    book = {}
    ph = chunklaw.policy_hash(POL)
    chunklaw.put(book, "cut", ph, chunklaw.rows_for(TEXT, "document", POL))
    chunklaw.put(book, "stale", "oldpolicy", [])
    live = ["cut", "stale", "uncut"]           # a purged id is not live
    assert chunklaw.missing(book, live, ph) == ["stale", "uncut"]
