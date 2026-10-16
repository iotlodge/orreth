# PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — Phase 8 sp8 THE BENCH (canon 0011 §2): one effort, one row of the ground · 2026-10-13
"""THE BENCH on the ground: a bench opens under a person (once per name while open), keeps its
step and the wizard's state, files drafts on itself, reads whole (its drafts · its experiments ·
its seat), and is let go with its drafts discarded — what reached the shelf untouched (AG-9: a
bench is its owner's alone)."""
import json
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
    assert ground.SCHEMA_VERSION >= 10 and "spine_benches" in ground.TABLES and "benches" in ground.TAGS
    cur = pg.cursor(); cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'spine_drafts' AND column_name = 'bench'")
    assert cur.fetchone(), "the drafts table wears its bench column"


def test_one_word_to_work_cuts_in_order_skips_what_stands_and_opens_the_experiment(pg, monkeypatch):
    """THE STUDIO sp10 ONE WORD TO WORK (canon 0011 §5): one hold for the chain — the card's lines
    BEFORE the hold, every cut its own fact on the Yes, the Experiment opened on the agent's own,
    the bench at THE CARD; what stands with the same bytes is skipped as a line; the refusals of
    the walks are lines, not walls."""
    from orreth_spine import envelope as ev, experiments, levels, proof, services
    _world(monkeypatch); ground.ensure_all(pg)
    levels.ensure_universe(pg, ev.universe()); levels.declare(pg, ev.universe(), {"levels": [{"at": "f:ops"}], "seats": []})   # the floor the room opens on
    name = "wk" + secrets.token_hex(2)
    benches.open_bench(pg, PERSON, name)
    with pytest.raises(benches.BenchRefused, match="no graph"):
        benches.work_check(pg, PERSON, name)                                             # an empty bench refuses in words
    graph = {"entry": "say", "nodes": [{"id": "say", "kind": "echo"}], "edges": []}
    crafts.save_draft(pg, PERSON, "graph", name + ".v0", graph, bench=name)
    crafts.save_draft(pg, PERSON, "template", name, {"kind": "agent", "name": name, "graph": name + ".v0", "nature": "answers hello", "capabilities": ["ask"]}, bench=name)
    with pytest.raises(benches.BenchRefused, match="no golden set"):
        benches.work_check(pg, PERSON, name)
    crafts.save_draft(pg, PERSON, "golden", name, {"template": name, "cases": [{"ask": "hello", "expect": ["HELLO"]}]}, bench=name)
    c = benches.work_check(pg, PERSON, name)
    assert c["plan"]["cuts"] == ["graph", "golden", "template"] and c["plan"]["lines"][2] == f"the agent {name} as version 1 -> the experiment"
    held = benches.hold_work(pg, PERSON, name)
    assert held["level"] == "L2" and held["lines"] == c["plan"]["lines"]
    b = benches.get(pg, PERSON, name)
    assert b["step"] == "cut" and b["hold"] == held["held"]                               # the bench keeps the ask it holds
    cur = pg.cursor()
    cur.execute("SELECT held, text FROM spine_asks WHERE ask_id = %s", (held["held"],))
    h, text = cur.fetchone()
    assert json.loads(h)["tool"] == "bench.work" and text.startswith(f"putting {name} to work - the graph {name}.v0 as version 1")
    assert services.get(pg, name + ".v0.graph") is None                                 # nothing lands before the Yes
    out = proof.settle_kernel_act(pg, held["held"], approve=True, by=PERSON)
    assert out["status"] == "replied" and f"{name}.v0.graph is on the shelf as version 1" in out["reply"] and "experiment room" in out["reply"]
    assert services.get(pg, name + ".v0.graph")["version"] == 1 and services.get(pg, name + ".golden")["version"] == 1
    xs = experiments.listing(pg, agent=name)
    assert len(xs) == 1 and xs[0]["state"] == "running"                                 # the Experiment opened on the agent's own cut
    b = benches.get(pg, PERSON, name)
    assert b["step"] == "card" and b["hold"] is None
    w = benches.whole(pg, PERSON, b)
    assert [d["kind"] for d in w["drafts"]] == ["template"] and len(w["experiments"]) == 1   # the cut drafts are spent; the agent's stays for the experiment
    # while the experiment runs the chain refuses in words before any hold; the same bytes are a skipped line (W124's law)
    crafts.save_draft(pg, PERSON, "graph", name + ".v0", graph, bench=name)
    with pytest.raises(benches.BenchRefused, match="already running"):
        benches.work_check(pg, PERSON, name)
    experiments.decline(pg, PERSON, xs[0]["experiment_id"], reason="the test starts over")
    c2 = benches.work_check(pg, PERSON, name)
    assert c2["plan"]["cuts"] == ["template"] and c2["plan"]["lines"][0] == f"the graph {name}.v0 stands (version 1) - unchanged, skipped"
    # W149 (JB's walk 2026-10-16): a graph naming a prompt that is neither a draft on the bench nor on the shelf refuses in
    # words before any hold; drafted on the bench, the prompt is the FIRST cut of the chain
    crafts.save_draft(pg, PERSON, "graph", name + ".v0", dict(graph, nodes=[{"id": "say", "kind": "echo", "prompt": name + "-words"}]), bench=name)
    with pytest.raises(benches.BenchRefused, match=f"the graph names prompt {name}-words, which is neither a draft on the bench nor on the shelf"):
        benches.work_check(pg, PERSON, name)
    crafts.save_draft(pg, PERSON, "prompt", name + "-words", {"text": "Say hello."}, bench=name)
    crafts.save_draft(pg, PERSON, "template", name, {"kind": "agent", "name": name, "graph": name + ".v0", "nature": "answers hello, warmly", "capabilities": ["ask"]}, bench=name)
    c3 = benches.work_check(pg, PERSON, name)
    assert c3["plan"]["cuts"] == [f"prompt:{name}-words", "graph", "template"] and c3["plan"]["lines"][0] == f"the prompt {name}-words as version 1"
    assert c3["drafts"][f"prompt:{name}-words"]
    # a changed graph with the template unchanged still refuses: an experiment needs a change to judge
    plan = benches.plan_work(name, {"draft": True, "same": False, "version": 1}, {"draft": False, "same": False, "version": 1}, {"draft": True, "same": True, "version": 1})
    assert not plan["ok"] and plan["cuts"] == ["graph"] and "stands unchanged" in plan["reason"]
