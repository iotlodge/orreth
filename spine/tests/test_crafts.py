# PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch Phase 8 THE WORKSHOP sp2, THE SHELF WIDENED · 2026-10-05
"""THE SHELF WIDENED on the reference (canon 0010 lock 3 · lock 6 · 0005 Phase 8 sp2): the craft kinds on
the one shelf — addressed, never minted, their health the declaration reading whole; the wear rows a body
writes at its join (in use by N, the previous life closed); the draft shelf under the person (only the
author's seat reads it; the cut held at the class's level and settled onto the shelf as the ladder's own
fact); the hull's three edges and the template's graph finally read; the golden set as a component the
harness reads first."""
import json
import secrets
from pathlib import Path

import pytest

from orreth_spine import crafts, envelope as ev, harness, levels, markers, proof, resident, services

SPINE = Path(__file__).resolve().parents[1]
POLICY = SPINE / "policy" / "covenant-policy.v1.json"
PERSON = "did:orreth:person:test"
OTHER = "did:orreth:person:other"


def _world(monkeypatch, mode=None):
    u = "u:law-" + secrets.token_hex(3)
    monkeypatch.setenv("SPINE_SCOPE", u)
    if mode is None:
        monkeypatch.delenv("SPINE_MODE", raising=False)
    else:
        monkeypatch.setenv("SPINE_MODE", mode)
    return u


def _body(template, **kw):
    r = resident.Resident(SPINE / "templates" / template, **kw)
    r.load_policy(POLICY)
    return r


def _facts(pg, type_):
    cur = pg.cursor()
    cur.execute("SELECT body FROM spine_outbox ORDER BY outbox_id")
    out = []
    for (body,) in cur.fetchall():
        try:
            e = ev.decode(bytes(body))
        except Exception:                       # noqa: BLE001
            continue
        if e.get("type") == type_:
            out.append(e)
    return out


def test_the_crafts_stand_on_the_one_shelf_addressed_never_minted(pg, monkeypatch):
    _world(monkeypatch)
    made = services.seed(pg)
    assert {"librarian.template", "echo.template", "crew.binding", "the-orreth-covenant.policy",
            "mind.v0.graph", "echo.v0.graph", "librarian.golden"} <= set(made["registered"])
    t = services.get(pg, "librarian.template")
    assert t["kind"] == "template" and t["did"] == "craft:librarian.template" and t["version"] == 1
    assert services.seed(pg)["registered"] == []                                 # the same shelf every boot
    # health is the declaration reading whole — a template's graph must stand on the shelf
    assert services.check(pg, "librarian.template")["ok"] is True
    assert "its graph mind.v0 stands on the shelf" in services.check(pg, "librarian.template")["detail"]
    assert "think" in services.check(pg, "mind.v0.graph")["detail"]
    services.register(pg, "ghost.template", "template",
                      {"format": "orreth-resident-template/1", "name": "ghost", "graph": "nowhere.v0"}, by=PERSON)
    out = services.check(pg, "ghost.template")
    assert out["ok"] is False and "names graph 'nowhere.v0', which is not on the shelf" in out["detail"]
    # the laws at the door, in words
    with pytest.raises(services.ServiceRefused, match=r"named <name>.template"):
        services.register(pg, "bare", "template", {"format": "orreth-resident-template/1", "name": "bare", "graph": "mind.v0"}, by=PERSON)
    with pytest.raises(services.ServiceRefused, match="does not read whole: a graph names its entry node"):
        services.register(pg, "broken.graph", "graph", {"format": "orreth-graph/1", "name": "broken", "nodes": [{"id": "a", "kind": "think"}]}, by=PERSON)
    # a source's second form: a repo'd origin — declared, not probed here
    src = services.register(pg, "bob-src", "source", {"repo": "https://github.com/x/bob", "commit": "a1b2c3d4e5f6", "entry": "bob.graph:build"}, by=PERSON)
    assert src["did"].startswith("did:orreth:service:")                          # a source IS an identity still
    out = services.check(pg, "bob-src")
    assert out["ok"] is None and "fetched at import" in out["detail"]
    with pytest.raises(services.ServiceRefused, match="pins a commit"):
        services.register(pg, "bad-src", "source", {"repo": "r", "entry": "e"}, by=PERSON)
    listing = {s["name"]: s for s in services.listing(pg)}
    assert listing["librarian.template"]["craft"] == "librarian" and listing["librarian.template"]["worn_by"] == 0
    assert "worn_by" not in listing["bob-src"]


def test_a_body_writes_what_it_wears_at_its_join_and_the_shelf_counts_it(pg, monkeypatch):
    _world(monkeypatch)
    services.seed(pg)
    lib = _body("librarian-resident.v0.json")
    j = lib.join(pg)
    worn = crafts.wears(pg, lib.identity.did)
    assert [(w["component"], w["kind"], w["version"]) for w in worn] == \
        [("librarian.template", "template", 1), ("the-orreth-covenant.policy", "policy", 1),
         ("mind.v0.graph", "graph", 1), ("librarian.golden", "golden", 1)]
    assert worn[0]["hash"] == lib.template_hash == services.get(pg, "librarian.template")["manifest_hash"]
    assert crafts.worn_by(pg, "librarian.template")[0]["life"] == j["life"]
    assert {s["name"]: s["worn_by"] for s in services.listing(pg, kind="template")}["librarian.template"] == 1
    j2 = lib.join(pg)                                                             # the next life: the old rows closed
    assert j2["life"] == j["life"] + 1
    assert [w["life"] for w in crafts.worn_by(pg, "librarian.template")] == [j2["life"]]
    assert crafts.wear_counts(pg)["mind.v0.graph"] == 1
    # a workspace seat wears its binding too; the echo wears no golden set and a graph of its own
    ws = _body("workspace-firmware.v0.json", binding=SPINE / "bindings" / "crew.v0.json"); ws.join(pg)
    assert [w["component"] for w in crafts.wears(pg, ws.identity.did)] == \
        ["workspace.template", "crew.binding", "the-orreth-covenant.policy", "mind.v0.graph"]
    echo = _body("echo-resident.v0.json"); echo.join(pg)
    assert [w["component"] for w in crafts.wears(pg, echo.identity.did)] == \
        ["echo.template", "the-orreth-covenant.policy", "echo.v0.graph"]
    assert crafts.wear_counts(pg)["mind.v0.graph"] == 2 and crafts.wear_counts(pg)["the-orreth-covenant.policy"] == 3
    assert "worn by 2 bodies" in crafts.worn_words("mind.v0.graph", crafts.worn_by(pg, "mind.v0.graph"))
    # a body whose component is not on the shelf wears it OFF the shelf — said, never hidden
    with pg.transaction():
        pg.cursor().execute("DELETE FROM spine_service_versions WHERE name = 'echo.v0.graph' AND scope = %s", (ev.universe(),))
    echo.join(pg)
    assert [w["version"] for w in crafts.wears(pg, echo.identity.did) if w["kind"] == "graph"] == [None]
    assert "off the shelf" in crafts.worn_words("echo.v0.graph", crafts.worn_by(pg, "echo.v0.graph"))


def test_the_draft_shelf_lives_under_the_person_and_the_cut_is_the_gate(pg, monkeypatch):
    u = _world(monkeypatch)
    levels.ensure_universe(pg, u)
    services.seed(pg)
    d = crafts.save_draft(pg, PERSON, "prompt", "greeting", {"text": "Greet the human by name."}, words="a warm opener")
    assert d["body"]["format"] == "orreth-prompt/1" and d["words"] == "a warm opener"
    assert [x["draft_id"] for x in crafts.drafts(pg, PERSON)] == [d["draft_id"]]
    assert crafts.drafts(pg, OTHER) == [] and crafts.draft(pg, OTHER, d["draft_id"]) is None   # AG-9: the author's seat alone
    assert services.get(pg, "greeting.prompt") is None                             # never on the shelf, never in the listing
    with pytest.raises(crafts.CraftRefused, match="no such draft of yours"):
        crafts.save_draft(pg, OTHER, "prompt", "greeting", {"text": "mine now"}, draft_id=d["draft_id"])
    # an unfinished draft refuses the cut in words; the same draft updated reads whole
    half = crafts.save_draft(pg, PERSON, "graph", "two", {"nodes": [{"id": "a", "kind": "think"}]})
    with pytest.raises(crafts.CraftRefused, match="does not read whole yet: a graph names its entry node"):
        crafts.cut_check(pg, PERSON, half["draft_id"])
    crafts.save_draft(pg, PERSON, "graph", "two", {"entry": "a", "nodes": [{"id": "a", "kind": "think"}, {"id": "b", "kind": "echo"}],
                                                   "edges": [{"from": "a", "to": "b"}]}, draft_id=half["draft_id"])
    assert crafts.cut_check(pg, PERSON, half["draft_id"])["verb"] == "register"
    # the cut: held at L2 as the kernel's own act; nothing on the shelf before the yes
    held = crafts.hold_cut(pg, PERSON, d["draft_id"])
    cur = pg.cursor()
    cur.execute("SELECT status, held, served_by, text FROM spine_asks WHERE ask_id = %s", (held,))
    status, h, served_by, text = cur.fetchone()
    assert status == "awaiting-confirm" and served_by == "the kernel" and json.loads(h)["tool"] == "craft.cut"
    assert json.loads(h)["level"] == "L2" and text.startswith("cutting the greeting prompt — version 1 onto the shelf")
    assert services.get(pg, "greeting.prompt") is None
    out = proof.settle_kernel_act(pg, held, approve=True, by=PERSON)
    assert out["status"] == "replied" and "greeting.prompt is on the shelf as version 1" in out["reply"]
    row = services.get(pg, "greeting.prompt")
    assert row["kind"] == "prompt" and row["did"] == "craft:greeting.prompt" and row["by"] == PERSON
    assert crafts.drafts(pg, PERSON) == [crafts.draft(pg, PERSON, half["draft_id"])]          # the cut draft is spent
    f = [f for f in _facts(pg, services.REGISTERED) if f["payload"]["name"] == "greeting.prompt"][0]
    assert f["authority_chain"] == [PERSON, "the kernel"] and f["payload"]["ref"] == "craft:greeting.prompt"
    # the same bytes again: nothing to cut; changed words: the next version, a sibling
    again = crafts.save_draft(pg, PERSON, "prompt", "greeting", {"text": "Greet the human by name."})
    with pytest.raises(crafts.CraftRefused, match="already stands on the shelf with these exact bytes"):
        crafts.cut_check(pg, PERSON, again["draft_id"])
    crafts.save_draft(pg, PERSON, "prompt", "greeting", {"text": "Greet the human by name, warmly."}, draft_id=again["draft_id"])
    held2 = crafts.hold_cut(pg, PERSON, again["draft_id"])
    proof.settle_kernel_act(pg, held2, approve=True, by=PERSON)
    assert services.get(pg, "greeting.prompt")["version"] == 2 and len(services.versions(pg, "greeting.prompt")) == 2
    # a no: nothing lands, the draft stays
    g2 = crafts.hold_cut(pg, PERSON, half["draft_id"])
    out = proof.settle_kernel_act(pg, g2, approve=False, by=PERSON)
    assert out["status"] == "cancelled" and services.get(pg, "two.graph") is None
    assert crafts.draft(pg, PERSON, half["draft_id"]) is not None
    # the demand by class: a resident's template asks the code; an agent's OPENS the Experiment (Phase 8 sp4) —
    # whose evidence, the golden set, is required
    res = crafts.save_draft(pg, PERSON, "template", "bob", {"graph": "mind.v0", "nature": "a test body"})
    assert crafts.cut_check(pg, PERSON, res["draft_id"])["level"] == "L3-code"
    ag = crafts.save_draft(pg, PERSON, "template", "bob2", {"graph": "mind.v0", "kind": "agent"})
    assert crafts.cut_demand("template", ag["body"], "dev") == {"ok": True, "level": "L2", "gate": "experiment", "reason": None}
    with pytest.raises(crafts.CraftRefused, match="bob2 has no golden set on the shelf"):
        crafts.cut_check(pg, PERSON, ag["draft_id"])
    fw = crafts.save_draft(pg, PERSON, "template", "chip", {"graph": "mind.v0", "kind": "firmware"})
    assert crafts.cut_check(pg, PERSON, fw["draft_id"])["level"] == "L2"                  # dev: cut
    assert crafts.discard_draft(pg, PERSON, fw["draft_id"]) is True
    assert crafts.discard_draft(pg, OTHER, res["draft_id"]) is False                       # not theirs


def test_firmware_is_cut_only_in_a_dev_universe(pg, monkeypatch):
    u = _world(monkeypatch, "prod")
    levels.ensure_universe(pg, u, "prod")
    fw = crafts.save_draft(pg, PERSON, "template", "chip", {"graph": "mind.v0", "kind": "firmware"})
    with pytest.raises(crafts.CraftRefused, match="firmware is cut only in a dev universe"):
        crafts.cut_check(pg, PERSON, fw["draft_id"])
    pr = crafts.save_draft(pg, PERSON, "prompt", "p", {"text": "x"})
    assert crafts.cut_check(pg, PERSON, pr["draft_id"])["level"] == "L2"                  # a prompt cuts in prod


def test_the_hull_routes_by_edge_and_the_work_node_runs_the_templates_graph(pg, monkeypatch, tmp_path):
    _world(monkeypatch)
    services.seed(pg)
    echo = _body("echo-resident.v0.json")
    out = echo._graph.invoke({"text": "hello there", "reply": "", "steps": [], "notes": [], "hold": None, "read": [], "edge": ""})
    assert out["edge"] == "chat" and out["reply"] == "hello there"
    assert "routed to the chat edge — a human's ask" in out["steps"]
    assert "the work node runs graph echo.v0: echo" in out["steps"]
    # an ask dispatched under an improvement marker takes the EVENT edge; under an intention, WORK
    echo._serve_conn = pg
    m = markers.set_marker(pg, "improvement", ref="ask_x", by="the kernel", note="a better way")
    echo._current_marker = {"kind": "objective", "id": "m_child", "parent": m["id"], "by": "the kernel"}
    out = echo._graph.invoke({"text": "act on it", "reply": "", "steps": [], "notes": [], "hold": None, "read": [], "edge": ""})
    assert out["edge"] == "event" and "routed to the event edge — a marker of kind improvement asked for a response" in out["steps"]
    mid = markers.new_id()
    with pg.transaction():
        markers.insert(pg.cursor(), mid, "intention", None, "int_x", PERSON, "a standing intention")
    echo._current_marker = {"kind": "objective", "id": "m_child2", "parent": mid, "by": PERSON}
    out = echo._graph.invoke({"text": "run the duty", "reply": "", "steps": [], "notes": [], "hold": None, "read": [], "edge": ""})
    assert out["edge"] == "work" and "routed to the work edge — assigned work under an intention" in out["steps"]
    echo._serve_conn = None
    echo._current_marker = None
    # the template's graph is READ: a template naming a graph the shelf does not hold cannot act, and says so
    t = tmp_path / "ghost.v0.json"
    t.write_text(json.dumps({"format": "orreth-resident-template/1", "name": "ghost", "graph": "nowhere.v0", "capabilities": ["ask"]}))
    ghost = resident.Resident(t)
    ghost.load_policy(POLICY)
    out = ghost._graph.invoke({"text": "hi", "reply": "", "steps": [], "notes": [], "hold": None, "read": [], "edge": ""})
    assert out["reply"].startswith("CANNOT ACT: my template names the graph 'nowhere.v0'")
    # the shelf's graph outranks the file: an echo graph re-cut as a think line reads from the shelf
    assert echo.graph_declaration(pg)["name"] == "echo.v0"
    services.version(pg, "echo.v0.graph", {"format": "orreth-graph/1", "name": "echo.v0", "entry": "e",
                                           "nodes": [{"id": "e", "kind": "echo"}], "edges": []}, by=PERSON)
    assert echo.graph_declaration(pg)["entry"] == "e"


def test_the_golden_set_is_a_component_the_harness_reads_first(pg, monkeypatch):
    _world(monkeypatch)
    services.seed(pg)
    assert [c["ask"][:6] for c in harness.golden("librarian", pg)] == ["Repeat", "In one"]
    doc = crafts.golden_document("librarian", harness.golden("librarian", pg) + [{"ask": "Say yes", "expect": ["yes"]}])
    services.version(pg, "librarian.golden", doc, by=PERSON)
    assert len(harness.golden("librarian", pg)) == 3 and len(harness.golden("librarian")) == 2   # the file stays the fallback
    assert harness.golden("nobody", pg) == []
