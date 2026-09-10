# PROVENANCE: Claude Fable 5 (claude-fable-5) — 0067 sp1, the format's suite · 2026-09-09
"""One graph language: every node a door, the narrative a bijection, the
walk's dialect converted with nothing lost."""
from orreth_sim import actgraph, fingertip


def _walk():
    plan = {"objective": "tend the garden",
            "intentions": [{"seat": "u:t/e:life/f:desk", "intent": "water",
                            "budget": {"tokens": 200}},
                           {"seat": "u:t/e:life/f:yard", "intent": "prune",
                            "budget": {"tokens": 100}}]}
    branches = [{"seat": "u:t/e:life/f:desk", "status": "done",
                 "severity": "low", "cycles": 1, "outcome": "sha256:out1",
                 "answer": "watered"},
                {"seat": "u:t/e:life/f:yard", "status": "done",
                 "cycles": 2, "outcome": "sha256:out2"}]
    return fingertip.choreography(plan, branches)


def test_every_node_is_a_door_or_the_picture_is_refused():
    g = actgraph.from_choreography(_walk(), objective="sha256:obj",
                                   request="req-1")
    assert actgraph.validate(g) == [], "a whole picture has no flaws"
    g["nodes"][0].pop("door")
    flaws = actgraph.validate(g)
    assert flaws and "no door" in flaws[0], \
        "a box with nothing behind it is refused (0052)"


def test_the_narrative_is_a_bijection():
    g = actgraph.from_choreography(_walk(), objective="sha256:obj",
                                   request="req-1")
    assert g["narrative"], "the walk reads aloud"
    g["narrative"][0]["nodes"] = ["ghost"]
    assert any("unknown node" in f for f in actgraph.validate(g))
    g2 = actgraph.from_choreography(_walk(), objective="sha256:obj",
                                    request="req-1")
    g2["nodes"].append({"id": "silent", "label": "?", "kind": "seat",
                        "door": {"kind": "view", "target": "objectives"}})
    assert any("silent boxes" in f for f in actgraph.validate(g2)), \
        "every node must be covered by a sentence"


def test_edges_bind_existing_nodes_and_keep_the_glow_law():
    g = actgraph.from_choreography(_walk(), objective="sha256:obj",
                                   request="req-1")
    assert all("kinds" in e for e in g["edges"]), \
        "every edge carries the glow list — empty means structural"
    g["edges"].append({"from": "i1", "to": "nowhere", "kinds": []})
    assert any("does not exist" in f for f in actgraph.validate(g))


def test_the_walk_converts_with_nothing_lost():
    raw = _walk()
    g = actgraph.from_choreography(raw, objective="sha256:obj",
                                   request="req-1")
    assert g["format"] == actgraph.VERSION and g["kind"] == "act-graph"
    assert {n["id"] for n in g["nodes"]} == {n["id"] for n in raw["nodes"]}
    assert g["narrative"] == raw["narrative"], "the story rides verbatim"
    assert g["coordinate"] == {"objective": "sha256:obj"}, \
        "the aperture is one governed fetch away"
    fingers = [n for n in g["nodes"] if n.get("role") == "fingertip"]
    assert all(n["door"]["kind"] == "record" and
               n["door"]["target"].startswith("sha256:") for n in fingers), \
        "a finished seat opens its own outcome record"
    human = next(n for n in g["nodes"] if n.get("role") == "human")
    assert human["door"] == {"kind": "record", "target": "req-1"}
    assert all(n.get("intent") == m.get("intent")
               for n, m in zip(g["nodes"], raw["nodes"])), \
        "the detail's fields survive — the glass loses nothing"


def test_conversion_is_deterministic():
    a = actgraph.from_choreography(_walk(), objective="o", request="r")
    b = actgraph.from_choreography(_walk(), objective="o", request="r")
    assert a == b


def test_the_capability_flow_converts_and_every_run_stage_is_a_record_door():
    spec = {"label": "the walk", "nodes": ["gather", {"id": "judge",
            "kind": "mind", "label": "the judge"}],
            "edges": [["gather", "judge"]],
            "groups": [{"label": "intake", "nodes": ["gather"]}]}
    stages = [{"stage": "gather", "digest": "found 3 filings",
               "ref": "sha256:stagerec1", "at": "t1"}]
    g = actgraph.from_manifest_flow(spec, stages, capability="trading-desk")
    assert g["format"] == actgraph.VERSION and g["layout"] == "pipeline"
    assert actgraph.validate(g) == [], "a pipeline needs no narrative"
    gather = next(n for n in g["nodes"] if n["id"] == "gather")
    assert gather["door"] == {"kind": "record", "target": "sha256:stagerec1"}
    assert gather["status"] == "done" and gather["digest"] == "found 3 filings"
    judge = next(n for n in g["nodes"] if n["id"] == "judge")
    assert judge["door"] == {"kind": "room", "target": "trading-desk"}, \
        "an unrun stage opens the capability's room — honestly, never a fake ref"
    assert judge["status"] == "pending" and judge["label"] == "the judge"
    assert g["groups"][0]["label"] == "intake", "the bands survive"
    assert actgraph.from_manifest_flow(spec, stages, capability="trading-desk") \
        == g, "deterministic"
