# PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch Phase 8 THE WORKSHOP sp3, THE WORKSHOP v0 · 2026-10-06
# Amended: Claude Fable 5.1 (claude-fable-5-1) — THE WIZARD held to the kernel's laws and to W118's (JB's lock 2026-10-12) · 2026-10-12
# Amended: Claude Fable 5.1 (claude-fable-5-1) — THE STUDIO sp11 THE AGENT MAKES IT ALL: the maker's proof (canon 0011 §6) · 2026-10-16
"""THE WORKSHOP v0 on the reference (canon 0010 lock 6 · lock 8 · 0005 Phase 8 sp3): the graph declaration
BRANCHES (a way out wears `when`: the hull's edge · the ask's words · the last reply; one default at most;
forward only) and the hull picks the way out as the run goes, saying each pick in the journey; a node's refs
are executed — its skill joins the system words, its tools narrow the door (never past the template), its
mind pins the stall; the Workshop's agent is the workspace firmware wearing the `workshop` binding, seated by
the crew manifest, its one tool `draft` routine (L1) and writing under the human whose ask it serves (AG-9:
no human, nothing saved); the `workshop` skill and binding stand on the shelf at light."""
import json
import re
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

        def think_acting(self, conn, *, did, system, prompt, door, model=None, on_delta=None, subject=None, klass=None, pin=None, ask=None, require=None):   # W116: the hull may REQUIRE a tool first
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


# ---- THE WIZARD (JB's lock 2026-10-12, after THE ONE WALK): glass-only, held here to the kernel's laws and to W118's ----
GLASS = SPINE / "glass" / "index.html"


def test_the_wizards_drafts_are_ordinary_drafts_the_kernel_cuts():
    """What the wizard writes (wizGraphDecl · wizGoldenDecl · wizTemplateDecl in the glass) is the SAME shape a hand
    writes — one entry node of the chosen kind, a golden set for the template, a template wearing <name>.v0 — and
    each validates on the reference law for law; an import node without its source refuses in the words the glass
    teaches, so the wizard refuses it first."""
    for shape, nid, extra in (("echo", "say", {}), ("think", "think", {"prompt": "greet", "mind": "haiku"}), ("import", "run", {"source": "bob-src"})):
        g = {"format": G, "name": "bob.v0", "version": "0.1.0", "words": "", "entry": nid, "nodes": [{"id": nid, "kind": shape, **extra}], "edges": []}
        assert crafts.validate("graph", g) == {"ok": True, "reason": None}, shape
    bare = {"format": G, "name": "imp.v0", "version": "0.1.0", "words": "", "entry": "run", "nodes": [{"id": "run", "kind": "import"}], "edges": []}
    assert "names its `source`" in crafts.validate("graph", bare)["reason"]
    gold = {"format": "orreth-golden/1", "template": "bob", "cases": [{"ask": "hello bob", "expect": ["hello"]}, {"ask": "say moon", "expect": ["moon"]}]}
    assert crafts.validate("golden", gold) == {"ok": True, "reason": None}
    tpl = {"format": "orreth-resident-template/1", "name": "bob", "version": "0.1.0", "nature": "answers hello", "kind": "agent",
           "graph": "bob.v0", "mind": {"model": "claude-haiku-4-5-20251001"}, "capabilities": ["ask"]}
    assert crafts.validate("template", tpl) == {"ok": True, "reason": None}
    # the inspector offers every kind the hull runs, and only those
    html = GLASS.read_text("utf-8")
    assert 'const NODE_KINDS = ["think", "echo", "import"]' in html, "the glass's node kinds drifted from the kernel's"
    assert tuple(crafts.NODE_KINDS) == ("think", "echo", "import")


def test_the_wizard_stands_on_the_first_screen_and_goes_through_the_chats_own_doors():
    """JB's lock: "+ new agent" beside "+ new draft"; the wizard fills the canvas, the inspector and the declaration;
    its cut, its promotion and a source's registration go through ONE door each with the typed word (W118: a button's
    word goes where a typed word goes); the chat still hears "new agent"; the kernel's facts drive its last steps."""
    html = GLASS.read_text("utf-8")
    assert "data-new-agent" in html and 'data-new title' in html
    assert html.index("data-new-agent") < html.index('data-new title'), "+ new agent stands beside (before) + new draft"
    for door in ("async function cutDraft(", "async function promoteAgent(", "async function registerSource("):
        assert html.count(door) == 1, door
    assert html.count("fetch(\"/drafts/cut\"") == 1 and html.count("fetch(\"/experiments/promote\"") == 1, "one door for the cut and the promotion"
    assert html.count('kind: "source", manifest: {repo') == 1, "one door for a source"
    for hook in ("wizOutcome(id, v)", "wizExperiment(n, x)", "wizJoined(n.ref)", "wizVerdict()"):
        assert hook in html, hook
    assert 'WS.open.source === "wizard"' in html and "function wizInspector(" in html and "function wizDecl(" in html
    assert "wsNewAgent" in html and re.search(r"new\\s\+agent", html), "the chat hears “new agent”"
    for words in ("held at the interlock: click Yes — do it in the chat", "where the next life stands", "JOINED · a life begins"):
        assert words in html, words

# ---- THE STUDIO sp11 — THE AGENT MAKES IT ALL (canon 0011 §6, JB's lock 2026-10-13: "fully auto means I as human can draft a prompt
# around an Agent, Skill, Prompt, Bindings, Graphs … and the workshop agent will perform this for me"; Opus by stock) ----


def test_the_workshop_agent_makes_an_agent_whole_from_a_brief_and_files_one_held_act(pg, monkeypatch):
    """One brief, one bench, every craft a draft ON the bench, ONE held act — the kernel's own `bench.work`
    hold at L2 (the SAME hold the bench's button files) under the human's seat for the human's single Yes;
    nothing on the shelf before it; the Yes cuts in order and opens the Experiment. The maker's hands are
    `draft` (now filing on a bench) and `bench` (open · read · work · close), both routine; the three modes law
    holds: the tool never cuts, never answers, and `work` is a governing seat's word."""
    from orreth_spine import benches, dispatch, envelope as ev, experiments, levels, proof, seat, services
    _world(monkeypatch)
    ground.ensure_all(pg); services.seed(pg)
    levels.ensure_universe(pg, ev.universe()); levels.declare(pg, ev.universe(), {"levels": [{"at": "f:ops"}], "seats": []})
    seats = body.crew(SPINE)
    ws = [s for s in seats if s["binding"] and s["binding"].name == "workshop.v0.json"][0]
    r = resident.Resident(ws["template"], binding=ws["binding"])
    # the binding by stock: Opus for the making, twelve rounds, the bench and the docs tools on the door, the maker's charge
    assert r.template["mind"]["model"] == "claude-opus-5-5" and r.rounds == 12
    for cap in ("tools:draft", "tools:bench", "tools:search-docs-by-lang-chain", "tools:search-api"):
        assert cap in r.template["capabilities"]
    assert "MAKE: when the human gives you a BRIEF" in r.charge and "never answer it" in r.charge and "THE HARNESS'S LAW" in r.charge
    draft, bench = tools.TOOLS["draft"], tools.TOOLS["bench"]
    assert tools.consequence_of(bench) == "routine" and bench["ground"] is True and "bench" in draft["input_schema"]["properties"]
    # the human behind the ask governs (the ceremony's owner); `work` is a governing seat's word, like the door's
    assert seat.declare_owner(pg, PERSON) and proof.governs(pg, PERSON)
    cur = pg.cursor()
    [ask_id] = dispatch.submit_ask(pg, "make an agent called greeter that answers hello, with one golden case, on the haiku stall",
                                   person=PERSON, to=["workshop"])
    by = r.identity.did
    name = "greeter"
    # (1) the bench opens under the ask's person; a draft on a bench not open refuses in words first
    with pytest.raises(RuntimeError, match="no open bench named 'greeter'"):
        draft["fn"]({"name": "greeter.v0", "kind": "graph", "body": {"entry": "say", "nodes": [{"id": "say", "kind": "echo"}], "edges": []}, "bench": name, "_ask": ask_id, "_by": by}, pg)
    out = bench["fn"]({"action": "open", "name": name, "_ask": ask_id, "_by": by}, pg)
    assert out.startswith("the greeter bench is open under the human's seat, at NAME")
    assert benches.get(pg, PERSON, name)["state"] == "open" and benches.get(pg, "did:orreth:person:other", name) is None   # AG-9
    # work before the bench is whole: refused in words, no hold filed
    out = bench["fn"]({"action": "work", "name": name, "_ask": ask_id, "_by": by}, pg)
    assert out.startswith("refused — ") and "no graph" in out
    # (2)–(5) every craft ONE draft call, on the bench; a draft not whole is said, then fixed with another call
    # W149 (JB's walk, 2026-10-16): the graph NAMES a prompt the maker wrote — it is cut with the chain, before the graph
    g = {"format": G, "name": "greeter.v0", "entry": "say", "nodes": [{"id": "say", "kind": "echo", "prompt": "greeter-words"}], "edges": []}
    out = draft["fn"]({"name": "greeter.v0", "kind": "graph", "body": g, "bench": name, "_ask": ask_id, "_by": by}, pg)
    assert out.startswith("saved the greeter.v0 graph draft") and "on the greeter bench" in out and "it reads whole" in out and "action=work" in out
    out = draft["fn"]({"name": "greeter-words", "kind": "prompt", "body": {"text": "Greet in three languages."}, "bench": name, "_ask": ask_id, "_by": by}, pg)
    assert "it reads whole" in out
    out = draft["fn"]({"name": "greeter", "kind": "golden", "body": {"template": "greeter", "cases": []}, "bench": name, "_ask": ask_id, "_by": by}, pg)
    assert "not whole yet" in out
    out = draft["fn"]({"name": "greeter", "kind": "golden", "body": {"template": "greeter", "cases": [{"ask": "hello", "expect": ["HELLO"]}]}, "bench": name, "_ask": ask_id, "_by": by}, pg)
    assert out.startswith("updated the greeter golden draft") and "it reads whole" in out
    out = draft["fn"]({"name": "greeter", "kind": "template", "bench": name, "_ask": ask_id, "_by": by,
                       "body": {"name": "greeter", "kind": "agent", "graph": "greeter.v0", "nature": "answers hello", "mind": {"model": "claude-haiku-4-5-20251001"}, "capabilities": ["ask"]}}, pg)
    assert "it reads whole" in out
    out = bench["fn"]({"action": "read", "name": name, "_ask": ask_id, "_by": by}, pg)
    assert out.startswith("the greeter bench is open, at NAME — drafts: ") and "greeter template (reads whole)" in out and "no experiment" in out
    w = benches.whole(pg, PERSON, benches.get(pg, PERSON, name))
    assert sorted(d["kind"] for d in w["drafts"]) == ["golden", "graph", "prompt", "template"] and all(d["bench"] == name for d in w["drafts"])
    # the maker's recall: THE STABLE's stalls and YOUR BENCHES, under the ask's person alone
    r.load_policy(POLICY); r._serve_conn = pg; r._current_ask = ask_id
    notes = " ".join(r._graph.invoke({"text": "what stands on my bench?", "reply": "", "steps": [], "notes": [], "hold": None, "read": [], "edge": ""})["notes"])
    r._serve_conn = None; r._current_ask = None
    assert "THE STABLE's standing stalls" in notes and "YOUR BENCHES — the human's open benches: greeter at NAME · drafts:" in notes and "greeter template (whole)" in notes
    # (6) ONE held act — the kernel's own bench.work hold under the human, in the ask's session; nothing on the shelf
    out = bench["fn"]({"action": "work", "name": name, "_ask": ask_id, "_by": by}, pg)
    assert out.startswith("filed ONE held act for the human's Yes in the chat — put greeter to work: the prompt greeter-words as version 1; the graph greeter.v0 as version 1; the golden set greeter as version 1; the agent greeter as version 1 -> the experiment")
    assert "never answer it" in out
    b = benches.get(pg, PERSON, name)
    assert b["step"] == "cut" and b["hold"]
    cur.execute("SELECT status, served_by, held, person, text FROM spine_asks WHERE ask_id = %s", (b["hold"],))
    status, served_by, held, person, text = cur.fetchone()
    assert (status, served_by, person) == ("awaiting-confirm", proof.KERNEL, PERSON)
    assert {k: json.loads(held)[k] for k in ("tool", "args")} == {"tool": "bench.work", "args": {"bench": name, "person": PERSON, "filed_by": by}}   # the record says who filed it
    assert text.startswith("putting greeter to work - the prompt greeter-words as version 1 · the graph greeter.v0 as version 1")
    assert services.get(pg, "greeter.v0.graph") is None and services.get(pg, "greeter.golden") is None and services.get(pg, "greeter-words.prompt") is None
    # W148 (found by this proof): filed twice is refused in words, never doubled — one chain, ONE hold
    out = bench["fn"]({"action": "work", "name": name, "_ask": ask_id, "_by": by}, pg)
    assert out.startswith(f"refused — put greeter to work is already held ({b['hold']})")
    cur.execute("SELECT count(*) FROM spine_asks WHERE status = 'awaiting-confirm' AND served_by = %s AND scope = %s", (proof.KERNEL, ev.universe()))
    assert cur.fetchone()[0] == 1                                                          # this world's holds alone: the suite's other worlds keep theirs
    # the Yes is the human's: through the kernel's own settle — the cuts in order, the Experiment opened, the bench at THE CARD
    settled = proof.settle_kernel_act(pg, b["hold"], approve=True, by=PERSON)
    assert settled["status"] == "replied" and "greeter.v0.graph is on the shelf as version 1" in settled["reply"]
    assert services.get(pg, "greeter.v0.graph")["version"] == 1 and services.get(pg, "greeter.golden")["version"] == 1
    assert services.get(pg, "greeter-words.prompt")["version"] == 1 and "greeter-words.prompt is on the shelf as version 1" in settled["reply"]   # W149: the prompt landed first
    assert [x["state"] for x in experiments.listing(pg, agent=name)] == ["running"]
    assert benches.get(pg, PERSON, name)["step"] == "card"
    # the three modes law at the tool: no human behind the ask → nothing done; a reading seat's ask → work refused in words
    with pytest.raises(RuntimeError, match="no human behind it"):
        bench["fn"]({"action": "open", "name": "x", "_by": by}, pg)
    [other] = dispatch.submit_ask(pg, "put it to work", person="did:orreth:person:reader", to=["workshop"])
    assert bench["fn"]({"action": "open", "name": "mine", "_ask": other, "_by": by}, pg).startswith("the mine bench is open")
    out = bench["fn"]({"action": "work", "name": "mine", "_ask": other, "_by": by}, pg)
    assert out.startswith("refused — put to work is a governing seat's word")
    assert bench["fn"]({"action": "close", "name": "mine", "_ask": other, "_by": by}, pg).startswith("the mine bench is let go — 0 drafts discarded")
    assert bench["fn"]({"action": "sing", "name": "mine", "_ask": other, "_by": by}, pg) == "a bench act is one of open · read · work · close"
