# PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch Phase 8 THE WORKSHOP sp3, THE WORKSHOP v0 · 2026-10-06
"""THE WORKSHOP v0 on the reference (canon 0010 lock 6 · lock 8 · 0005 Phase 8 sp3): the graph declaration
BRANCHES (a way out wears `when`: the hull's edge · the ask's words · the last reply; one default at most;
forward only) and the hull picks the way out as the run goes, saying each pick in the journey; a node's refs
are executed — its skill joins the system words, its tools narrow the door (never past the template), its
mind pins the stall; the Workshop's agent is the workspace firmware wearing the `workshop` binding, seated by
the crew manifest, its one tool `draft` routine (L1) and writing under the human whose ask it serves (AG-9:
no human, nothing saved); the `workshop` skill and binding stand on the shelf at light."""
import json
import secrets
from pathlib import Path

import pytest

from orreth_spine import body, crafts, ground, resident, services, tools

SPINE = Path(__file__).resolve().parents[1]
POLICY = SPINE / "policy" / "covenant-policy.v1.json"
PERSON = "did:orreth:person:test"
G = "orreth-graph/1"


def _world(monkeypatch):
    u = "u:ws-" + secrets.token_hex(3)
    monkeypatch.setenv("SPINE_SCOPE", u)
    monkeypatch.delenv("SPINE_MODE", raising=False)
    return u


def _graph(nodes, edges, entry="route", name="b"):
    return {"format": G, "name": name, "entry": entry, "nodes": nodes, "edges": edges}


def test_the_graph_branches_one_default_at_most_forward_only():
    g = _graph([{"id": "route", "kind": "think"}, {"id": "greet", "kind": "echo"},
                {"id": "work", "kind": "think", "prompt": "weather-words", "skill": "shelf", "tools": ["weather"], "mind": "haiku"}],
               [{"from": "route", "to": "greet", "when": {"ask": "^(hi|hello)"}},
                {"from": "route", "to": "work", "when": {"edge": "work"}},
                {"from": "route", "to": "work"}])
    assert crafts.validate("graph", g) == {"ok": True, "reason": None}
    assert crafts.path(g) == ["route", "work"] and crafts.branches(g) == ["route"]
    # the run-time pick: the first `when` that holds, in declaration order; else the default; else the line ends
    assert crafts.next_node(g, "route", {"edge": "chat", "ask": "Hello there"}) == ("greet", "took the way out to 'greet' — when the ask says /^(hi|hello)/")
    assert crafts.next_node(g, "route", {"edge": "work", "ask": "run the duty"}) == ("work", "took the way out to 'work' — when the ask took the work edge")
    assert crafts.next_node(g, "route", {"edge": "chat", "ask": "weather?"}) == ("work", "took the default way out to 'work' — no `when` held")
    assert crafts.next_node(g, "work", {"edge": "chat"}) == (None, None)
    only = _graph([{"id": "route", "kind": "think"}, {"id": "a", "kind": "echo"}], [{"from": "route", "to": "a", "when": {"reply": "HOLD"}}])
    assert crafts.validate("graph", only)["ok"] and crafts.path(only) == ["route"]
    assert crafts.next_node(only, "route", {"reply": "nothing"}) == (None, "no way out of 'route' held — the line ends here")
    assert crafts.next_node(only, "route", {"reply": "we HOLD here"})[0] == "a"
    # a pattern that does not read is said and never matches
    broken = _graph([{"id": "route", "kind": "think"}, {"id": "a", "kind": "echo"}], [{"from": "route", "to": "a", "when": {"ask": "("}}, {"from": "route", "to": "route"}])
    assert "loops" in crafts.validate("graph", broken)["reason"]
    nxt, why = crafts.next_node(_graph([{"id": "route", "kind": "think"}, {"id": "a", "kind": "echo"}],
                                       [{"from": "route", "to": "a", "when": {"ask": "("}}]), "route", {"ask": "x"})
    assert nxt is None and "does not read" in why and "the line ends here" in why
    # the refusals, in words
    two = _graph([{"id": "route", "kind": "think"}, {"id": "a", "kind": "echo"}, {"id": "b", "kind": "echo"}],
                 [{"from": "route", "to": "a"}, {"from": "route", "to": "b"}])
    assert "two ways out and neither says when" in crafts.validate("graph", two)["reason"]
    bad = _graph([{"id": "route", "kind": "think"}, {"id": "a", "kind": "echo"}], [{"from": "route", "to": "a", "when": {"edge": "side"}}])
    assert "`when.edge` is one of chat, work, event" in crafts.validate("graph", bad)["reason"]
    assert "`tools` is a list of tool names" in crafts.validate("graph", _graph([{"id": "route", "kind": "think", "tools": "weather"}], []))["reason"]
    assert crafts.when_words({"from": "a", "to": "b"}) == "otherwise"
    assert crafts.when_words({"when": {"edge": "event"}}) == "when the ask took the event edge"


def test_the_hull_picks_the_way_out_as_the_run_goes(pg, monkeypatch, tmp_path):
    """A mindless body (no gateway) runs a branching graph of echo nodes: the way out is read off the hull's
    edge and the ask's words, each pick said in the journey; the default line is the spine."""
    _world(monkeypatch)
    ground.ensure_all(pg)                       # the ground birthed whole: the recall reads the asks
    services.seed(pg)
    g = _graph([{"id": "route", "kind": "echo"}, {"id": "greet", "kind": "echo", "words": "the greeting"},
                {"id": "rest", "kind": "echo"}, {"id": "tail", "kind": "echo"}],
               [{"from": "route", "to": "greet", "when": {"ask": "^hello"}},
                {"from": "route", "to": "rest"},
                {"from": "rest", "to": "tail", "when": {"edge": "event"}}], name="fork.v0")
    services.register(pg, "fork.v0.graph", "graph", g, by=PERSON)
    t = tmp_path / "fork.v0.json"
    t.write_text(json.dumps({"format": "orreth-resident-template/1", "name": "forky", "graph": "fork.v0", "capabilities": ["ask"]}))
    r = resident.Resident(t)
    r.load_policy(POLICY)
    r._serve_conn = pg
    blank = {"reply": "", "steps": [], "notes": [], "hold": None, "read": [], "edge": ""}
    out = r._graph.invoke(dict(blank, text="hello there"))
    assert out["edge"] == "chat" and out["reply"] == "hello there"
    assert "the work node runs graph fork.v0: route → rest · branches at route — the way out picked as the run goes" in out["steps"]
    assert "took the way out to 'greet' — when the ask says /^hello/" in out["steps"]
    assert not any("rest" in s and "took" in s for s in out["steps"])
    out = r._graph.invoke(dict(blank, text="what time is it"))
    assert "took the default way out to 'rest' — no `when` held" in out["steps"]
    assert "no way out of 'rest' held — the line ends here" in out["steps"]
    assert out["steps"].count("echoed every word — none summarized away (a plain-spoken echo)") == 2   # route, rest — never tail
    r._serve_conn = None


def test_a_nodes_refs_are_executed_by_the_hull(pg, monkeypatch, tmp_path):
    """With a gateway in hand the think node reads the node's skill and prompt into the system words, narrows
    the door to the node's tools (never past the template's), and pins the node's mind — each said in the
    journey."""
    _world(monkeypatch)
    ground.ensure_all(pg)                       # the ground birthed whole: the recall reads the asks
    services.seed(pg)
    services.register(pg, "greet.prompt", "prompt", {"format": "orreth-prompt/1", "text": "GREET WARMLY."}, by=PERSON)
    g = _graph([{"id": "think", "kind": "think", "prompt": "greet", "skill": "shelf", "tools": ["weather", "acquire"], "mind": "haiku"}], [], entry="think", name="refs.v0")
    services.register(pg, "refs.v0.graph", "graph", g, by=PERSON)
    t = tmp_path / "refs.v0.json"
    t.write_text(json.dumps({"format": "orreth-resident-template/1", "name": "reffy", "graph": "refs.v0", "persona": "a tester",
                             "mind": {"model": "m"}, "capabilities": ["ask", "tools:weather", "tools:mark"]}))
    seen = {}

    class Gw:
        def think(self, conn, *, did, system, prompt, model=None, on_delta=None, subject=None, klass=None, pin=None, ask=None):
            seen.update(system=system, pin=pin, model=model)
            return "a reply"

        def think_acting(self, conn, *, did, system, prompt, door, model=None, on_delta=None, subject=None, klass=None, pin=None, ask=None):
            seen.update(system=system, pin=pin, model=model, tools=[t["name"] for t in door.schemas()])
            return "a reply", ["called nothing"]

    r = resident.Resident(t, gateway=Gw())
    r.load_policy(POLICY)
    r._serve_conn = pg
    out = r._graph.invoke({"text": "hi", "reply": "", "steps": [], "notes": [], "hold": None, "read": [], "edge": ""})
    assert out["reply"] == "a reply"
    assert "GREET WARMLY." in seen["system"] and "THE SKILL you follow here" in seen["system"]
    assert seen["pin"] == "haiku" and seen["tools"] == ["weather"]           # acquire was never the template's: shut
    assert "node think: prompt greet · skill shelf · tools weather, acquire (acquire never declared by the template — the door stays shut) · mind pinned to the haiku stall" in out["steps"]
    r._serve_conn = None


def test_the_workshop_agent_is_seated_and_its_draft_tool_writes_under_the_asks_person(pg, monkeypatch):
    _world(monkeypatch)
    ground.ensure_all(pg)
    seats = body.crew(SPINE)
    ws = [s for s in seats if s["binding"] and s["binding"].name == "workshop.v0.json"]
    assert len(ws) == 1 and ws[0]["template"].name == "workspace-firmware.v0.json"
    r = resident.Resident(ws[0]["template"], binding=ws[0]["binding"])
    assert r.name == "workshop" and r.function == "workspace:workshop" and "tools:draft" in r.template["capabilities"]
    # the shelf at light carries the binding and the Orreth skill for the Workshop
    services.seed(pg)
    assert services.get(pg, "workshop.binding")["state"] != "retired"
    sk = services.get(pg, "workshop.skill")
    assert sk and "node inspector" in sk["manifest"]["text"].lower()
    # the draft tool: routine, under the ASK's person; no human behind the ask → nothing saved, said
    t = tools.TOOLS["draft"]
    assert tools.consequence_of(t) == "routine" and t["ground"] is True
    from orreth_spine import dispatch
    ask = dispatch.submit_ask(pg, "workshop, draft a greeting", person=PERSON, to=["workshop"])
    ask_id = ask[0] if isinstance(ask, list) else ask            # a fan-out answers its ids; one target, one id
    out = t["fn"]({"name": "greeting", "kind": "prompt", "body": {"text": "Greet warmly."}, "_ask": ask_id, "_by": r.identity.did}, pg)
    assert out.startswith("saved the greeting prompt draft (draft_") and "it reads whole" in out and "cut the greeting draft" in out
    mine = crafts.drafts(pg, PERSON)
    assert [d["name"] for d in mine] == ["greeting"] and mine[0]["body"]["text"] == "Greet warmly."
    out2 = t["fn"]({"name": "greeting", "kind": "prompt", "body": {"text": ""}, "_ask": ask_id}, pg)
    assert out2.startswith("updated the greeting prompt draft") and "not whole yet" in out2
    assert len(crafts.drafts(pg, PERSON)) == 1
    assert crafts.drafts(pg, "did:orreth:person:other") == []                          # AG-9: the author's seat alone
    with pytest.raises(RuntimeError, match="no human behind it"):
        t["fn"]({"name": "x", "kind": "prompt", "body": {"text": "y"}}, pg)
    # the workshop recall reads the shelf and ONLY the open draft the ask names, for its author — the whole
    # hull run of a mindless workspace body (no gateway: the firmware echo), its notes inspected
    cur = pg.cursor()
    cur.execute("UPDATE spine_asks SET text = %s WHERE ask_id = %s", (f"make it shorter\n[draft {mine[0]['draft_id']}]", ask_id))
    r.load_policy(POLICY)
    r._serve_conn = pg
    r._current_ask = ask_id
    out = r._graph.invoke({"text": f"make it shorter\n[draft {mine[0]['draft_id']}]", "reply": "", "steps": [], "notes": [], "hold": None, "read": [], "edge": ""})
    r._serve_conn = None
    r._current_ask = None
    notes = " ".join(out["notes"])
    assert "THE SHELF holds" in notes and "workshop.binding" in notes and "craft mind.v0.graph: entry think" in notes
    assert "THE OPEN DRAFT — the human's own greeting prompt" in notes and "call the `draft` tool ONCE" in notes
    # another person's draft named in the ask is never read
    cur.execute("UPDATE spine_asks SET person = %s WHERE ask_id = %s", ("did:orreth:person:other", ask_id))
    r._serve_conn = pg
    r._current_ask = ask_id
    out = r._graph.invoke({"text": f"show it\n[draft {mine[0]['draft_id']}]", "reply": "", "steps": [], "notes": [], "hold": None, "read": [], "edge": ""})
    r._serve_conn = None
    assert any("is not this human's — nothing read" in n for n in out["notes"]) and not any("THE OPEN DRAFT" in n for n in out["notes"])
