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


def test_the_atlas_converts_and_its_grammar_becomes_the_formats():
    flow = {"nodes": [{"id": "becky", "label": "becky", "lane": "organs",
                       "sub": "signs every join", "door": {"res": "becky"}},
                      {"id": "you", "label": "you", "lane": "human",
                       "door": {"view": "inbox"}}],
            "edges": [{"from": "you", "to": "becky", "label": "asks to join",
                       "kinds": ["join"]}]}
    g = actgraph.from_atlas(flow)
    assert g["layout"] == "schematic" and actgraph.validate(g) == []
    b = next(n for n in g["nodes"] if n["id"] == "becky")
    assert b["door"]["kind"] == "resident" and b["door"]["target"] == "becky"
    assert b["door"]["opens"] == {"res": "becky"}, \
        "the legacy key rides beside — the standing sheet loses nothing (L1)"
    assert g["edges"][0]["kinds"] == ["join"], "the glow law is the format's"
    assert actgraph.from_atlas(flow) == g


def test_the_estate_converts_and_every_card_opens_its_deed():
    dag = {"layout": "dag", "subject": "the estate",
           "nodes": [{"id": "vpc", "category": "network",
                      "type": "AWS::EC2::VPC", "role": "fingertip",
                      "template_ref": "sha256:tmpl1"},
                     {"id": "orphan", "category": "compute",
                      "type": "AWS::EC2::Instance", "role": "fingertip"}],
           "edges": [{"from": "vpc", "to": "orphan", "kind": "depends"}],
           "narrative": [{"text": "two resources", "nodes": ["vpc", "orphan"],
                          "edges": ["vpc→orphan"]}]}
    g = actgraph.from_estate_dag(dag)
    assert g["layout"] == "dag" and actgraph.validate(g) == []
    vpc = next(n for n in g["nodes"] if n["id"] == "vpc")
    assert vpc["door"] == {"kind": "record", "target": "sha256:tmpl1"}, \
        "what you can click is what you signed — the deed"
    assert vpc["category"] == "network" and vpc["type"] == "AWS::EC2::VPC", \
        "the colors and types survive — the drawer keeps drawing them"
    orphan = next(n for n in g["nodes"] if n["id"] == "orphan")
    assert orphan["door"]["kind"] == "view", \
        "an unknown template doors the view, honestly — never a fake ref"


def _ask_world():
    from orreth_sim import dispatcher, provisioner, stacks
    from orreth_sim.node import make_memory
    prov = provisioner.provision(provisioner.second_brain_template(), "t")
    fld = prov.fields["desk"]
    b = prov.beckys["u:t/e:life/f:desk"]
    lib, kp = b.issue_identity("instance", "u:t/e:life/f:desk", resident=True)
    stacks.plant_eco_assets(fld, lib, kp)
    dispatcher.plant_standard(fld, lib, kp)
    d = dispatcher.dispatch(fld, lib, kp, "how are walls connected to seasons?")
    exch = make_memory(lib, kp, fld.scope,
                       {"ask": {"asked": "how are walls connected to seasons?",
                                "reply": "they breathe", "variant": d["flavor"],
                                "citations": [{"ref": "sha256:c1", "doc": "d",
                                               "score": 0.5}],
                                "signals": {"retrieval": 0.5}}},
                       kind="episodic", tags=["ask"])
    exch["derived_from"] = [d["record"]]
    fld.write(exch)
    return fld, lib, kp, exch["id"], d


def test_the_act_accretes_from_records_alone():
    fld, lib, kp, xid, d = _ask_world()
    g = actgraph.accrete_ask(fld.records, xid)
    assert g == actgraph.accrete_ask(fld.records, xid), "rebuilt from nothing"
    assert actgraph.validate(g) == [], "whole — every node a door"
    ids = {n["id"] for n in g["nodes"]}
    assert {"you", "choice", "style", "answer"} <= ids, \
        "the chain: asker → the router's choice → the style → the answer"
    choice = next(n for n in g["nodes"] if n["id"] == "choice")
    assert choice["door"]["target"] == d["record"] and choice.get("features"), \
        "the router's node opens its record and wears its features (0066)"
    style = next(n for n in g["nodes"] if n["id"] == "style")
    assert style["variant"] == d["flavor"], "the answer wears its style (0065)"
    assert any(d["why"][:40] in s_["text"] for s_ in g["narrative"]), \
        "the story reads the router's why aloud"


def test_a_landed_verdict_grows_the_picture():
    from orreth_sim import vera
    fld, lib, kp, xid, d = _ask_world()
    before = len(actgraph.accrete_ask(fld.records, xid)["nodes"])
    v = vera.make_verdict(lib, kp, fld.scope, of=xid, work_floor=fld.scope,
                          judge_floor="u:t", rubric=vera.DEFAULT_RUBRIC,
                          rubric_declared=False, score=0.8,
                          why="faithful", cost={"tokens": 50})
    fld.write(v)
    g = actgraph.accrete_ask(fld.records, xid)
    assert len(g["nodes"]) == before + 1, \
        "the picture GREW because a record landed — never an edit"
    judge = next(n for n in g["nodes"] if n["kind"] == "verdict")
    assert judge["door"]["target"] == v["id"] and judge["score"] == 0.8
    assert actgraph.validate(g) == []


def test_a_purged_choice_degrades_the_picture_honestly():
    fld, lib, kp, xid, d = _ask_world()
    fld.records.pop(d["record"])
    g = actgraph.accrete_ask(fld.records, xid)
    assert "choice" not in {n["id"] for n in g["nodes"]}, \
        "a missing record's node is simply absent"
    assert any("no longer stands" in s_["text"] for s_ in g["narrative"]), \
        "and the story says so — the projection degrades honestly"
    assert actgraph.validate(g) == []
