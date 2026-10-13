# PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — Phase 8 sp8 THE BENCH (canon 0011 §2): one effort, one row of the ground · 2026-10-13
"""THE BENCH on the ground: a bench opens under a person (once per name while open), keeps its
step and the wizard's state, files drafts on itself, reads whole (its drafts · its experiments ·
its seat), and is let go with its drafts discarded — what reached the shelf untouched (AG-9: a
bench is its owner's alone)."""
import secrets

import pytest

from orreth_spine import benches, crafts, ground

PERSON = "did:orreth:person:test"
OTHER = "did:orreth:person:other"


def _world(monkeypatch):
    monkeypatch.setenv("SPINE_SCOPE", "u:bench-" + secrets.token_hex(3))
    monkeypatch.delenv("SPINE_MODE", raising=False)


def test_a_bench_opens_once_per_name_and_keeps_its_place(pg, monkeypatch):
    _world(monkeypatch); ground.ensure_all(pg)
    b = benches.open_bench(pg, PERSON, "jonathan", words="answers hello")
    assert b["state"] == "open" and b["step"] == "name" and b["body"] == {} and b["hold"] is None
    assert benches.open_bench(pg, PERSON, "jonathan")["bench_id"] == b["bench_id"]      # the open one is handed back
    m = benches.move(pg, PERSON, "jonathan", step="golden", body={"shape": "echo", "cases": [{"ask": "hello", "expect": ["HELLO"]}]}, hold="ask_1")
    assert m["step"] == "golden" and m["body"]["shape"] == "echo" and m["hold"] == "ask_1"
    assert benches.move(pg, PERSON, "jonathan", hold="")["hold"] is None                 # "" clears the hold
    with pytest.raises(benches.BenchRefused):
        benches.move(pg, PERSON, "jonathan", step="experiment")
    with pytest.raises(benches.BenchRefused):
        benches.open_bench(pg, PERSON, "Bob.v0")
    assert benches.get(pg, OTHER, "jonathan") is None                                     # AG-9
    assert [x["name"] for x in benches.listing(pg, PERSON)] == ["jonathan"]


def test_drafts_file_on_a_bench_and_go_with_it(pg, monkeypatch):
    _world(monkeypatch); ground.ensure_all(pg)
    benches.open_bench(pg, PERSON, "imp2")
    g = crafts.save_draft(pg, PERSON, "graph", "imp2.v0", {"entry": "say", "nodes": [{"id": "say", "kind": "echo"}], "edges": []}, bench="imp2")
    loose = crafts.save_draft(pg, PERSON, "prompt", "greeting", {"text": "hi"})
    assert g["bench"] == "imp2" and loose["bench"] is None
    assert crafts.save_draft(pg, PERSON, "graph", "imp2.v0", g["body"], draft_id=g["draft_id"])["bench"] == "imp2"   # an update keeps the bench
    w = benches.whole(pg, PERSON, benches.get(pg, PERSON, "imp2"))
    assert [d["name"] for d in w["drafts"]] == ["imp2.v0"] and w["experiments"] == [] and w["seat"] is None
    out = benches.close(pg, PERSON, "imp2")
    assert out["discarded"] == 1 and out["declined"] == [] and out["bench"]["state"] == "closed" and out["bench"]["closed_at"]
    names = [d["name"] for d in crafts.drafts(pg, PERSON)]
    assert "greeting" in names and "imp2.v0" not in names                                 # the loose draft stays
    with pytest.raises(benches.BenchRefused):
        benches.close(pg, PERSON, "imp2")                                                 # closed is closed
    again = benches.open_bench(pg, PERSON, "imp2")                                        # a new effort under the same name
    assert again["bench_id"] != out["bench"]["bench_id"] and again["state"] == "open"
    assert [x["state"] for x in benches.listing(pg, PERSON)] == ["open", "closed"]


def test_the_schema_counts_the_bench(pg, monkeypatch):
    _world(monkeypatch); ground.ensure_all(pg)
    assert ground.SCHEMA_VERSION == 10 and "spine_benches" in ground.TABLES and "benches" in ground.TAGS
    cur = pg.cursor(); cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'spine_drafts' AND column_name = 'bench'")
    assert cur.fetchone(), "the drafts table wears its bench column"
