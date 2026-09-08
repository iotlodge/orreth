# PROVENANCE: Claude Fable 5 (claude-fable-5) — 0071 sp4, the traffic law's suite · 2026-09-09
"""Knocking is metered per identity inside a turning window — laws, not scores."""
from orreth_sim import traffic


def test_under_the_ceiling_every_knock_serves():
    book = {}
    for i in range(5):
        ok, wait = traffic.tick(book, "did:key:zA", 100.0 + i, limit=5)
        assert ok and wait == 0


def test_the_sixth_knock_waits_and_names_how_long():
    book = {}
    for i in range(5):
        traffic.tick(book, "did:key:zA", 100.0, limit=5)
    ok, wait = traffic.tick(book, "did:key:zA", 130.0, limit=5)
    assert not ok and wait == 30


def test_identities_never_share_a_ledger_line():
    book = {}
    for _ in range(5):
        traffic.tick(book, "did:key:zA", 100.0, limit=5)
    ok, _ = traffic.tick(book, "did:key:zB", 100.0, limit=5)
    assert ok, "one caller's flood must never slow another"


def test_the_window_turns_and_the_count_resets():
    book = {}
    for _ in range(5):
        traffic.tick(book, "did:key:zA", 100.0, limit=5)
    ok, _ = traffic.tick(book, "did:key:zA", 161.0, limit=5)
    assert ok


def test_zero_limit_is_the_operators_open_door():
    book = {}
    for i in range(1000):
        ok, _ = traffic.tick(book, "x", float(i), limit=0)
        assert ok


def test_sweep_forgets_dead_callers_only():
    book = {}
    traffic.tick(book, "old", 100.0, limit=5)
    traffic.tick(book, "live", 150.0, limit=5)
    traffic.sweep(book, 165.0)
    assert "old" not in book and "live" in book