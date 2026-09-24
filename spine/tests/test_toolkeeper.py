# PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P6.5 sp2, the Tools keeper · 2026-09-23
"""The Tools keeper (canon 0005 P6.5 sp2 · 0009 §1 · 0059's laws): MCP
through ONE door — a server registers over stdio and its tools land on
the shelf as identities; a call routes through tools/call with the chain
and the meter; a vanished tool goes unhealthy with the reason, never
retired; a changed list versions; a secret not reachable refuses by name;
the keeper proposes after N strikes and never retires alone; the harness
checks; the shelf door shows the nesting."""
import json
import secrets
import sys
import time
import urllib.request
from pathlib import Path

import pytest

from orreth_spine import dispatch, envelope as ev, gateway, glass, harness, markers, mcp, mitl, resident, services, tools

from tests.test_glass import _get, _post  # noqa: E402
from tests.test_mind import _rails_up  # noqa: E402

SPINE = Path(__file__).resolve().parents[1]
POLICY = SPINE / "policy" / "covenant-policy.v1.json"
ME = "did:orreth:person:test"
REF = mcp.ref_locator()
rails = pytest.mark.skipif(not _rails_up(), reason="the rails are not up")


def _scope(monkeypatch):
    monkeypatch.setenv("SPINE_SCOPE", "u:law-" + secrets.token_hex(3))


def _body(template, gw=None):
    r = resident.Resident(SPINE / "templates" / template, gateway=gw)
    r.load_policy(POLICY)
    return r


def _serve(pg, body, ask_id, chain=(ME,)):
    body._serve_conn = pg
    with pg.transaction():
        body._serve_ask(pg.cursor(), ask_id, list(chain))


def _facts(pg, needle, type_=None):
    cur = pg.cursor()
    cur.execute("SELECT body FROM spine_outbox WHERE convert_from(body, 'UTF8') LIKE %s ORDER BY outbox_id",
                (f"%{needle}%",))
    out = [ev.decode(bytes(b)) for (b,) in cur.fetchall()]
    return [e for e in out if type_ is None or e["type"] == type_]


def _clock(pg, monkeypatch, home, listing="now,echo"):
    monkeypatch.setenv("SPINE_MCP_REF_TOOLS", listing)
    return mcp.register_server(pg, "clock", REF, by=ME, secrets_with=["SPINE_MCP_REF_TOOLS"], home=home)


def test_the_ref_server_registers_over_stdio_and_its_tools_land_as_identities(pg, monkeypatch, tmp_path):
    """The reference clock answers initialize + tools/list over stdio; the
    server is a service of kind mcp (transport · locator BY NAME · the
    sorted list as its pin) and each listed tool a service of kind tool
    placed under it (affinity names the server; the manifest names it),
    the same DIDs across two registers (rule 1); the server's health
    says what it listed; the ref's own words about its tools stand."""
    _scope(monkeypatch)
    home = tmp_path / "services"
    made = _clock(pg, monkeypatch, home)
    srv = made["server"]
    assert srv["kind"] == "mcp" and srv["state"] == "healthy" and srv["did"].startswith("did:orreth:service:")
    assert srv["manifest"]["transport"] == "stdio" and srv["manifest"]["locator"] == REF
    assert [t["name"] for t in srv["manifest"]["tools"]] == ["echo", "now"]           # sorted: the pin reads the list
    assert srv["secrets_with"] == ["SPINE_MCP_REF_TOOLS"] and "now,echo" not in json.dumps(srv)   # names, never values
    assert made["tools"] == {"new": ["now", "echo"], "versioned": [], "present": [], "gone": [], "refused": []}
    assert made["info"]["name"] == "orreth-clock" and made["info"]["protocol"] == mcp.PROTOCOL
    assert srv["last_health"]["ok"] is True and srv["last_health"]["detail"].startswith(
        "initialize answered (orreth-clock 0.1.0, protocol 2025-06-18); 2 tools listed; new: now, echo")
    now, echo = services.get(pg, "now"), services.get(pg, "echo")
    for t in (now, echo):
        assert t["kind"] == "tool" and t["state"] == "healthy" and t["manifest"]["server"] == "clock"
        assert t["placement"]["affinity"] == ["clock"] and t["manifest"]["consequence"] == "routine"
        assert t["last_health"]["detail"] == "listed by its server; the schema matches the pin"
    assert now["manifest"]["input_schema"]["properties"] == {"zone": {"type": "string"}}
    assert now["manifest"]["tool"] == "now" and now["manifest_hash"] == services.pin(now["manifest"])
    assert mcp.tools_of(pg, "clock") and {t["name"] for t in mcp.tools_of(pg, "clock")} == {"now", "echo"}
    # the same selves, every register: the DIDs stand, no second register fact
    again = _clock(pg, monkeypatch, home)
    assert again["server"]["did"] == srv["did"] and again["tools"]["present"] == ["now", "echo"]
    assert services.get(pg, "now")["did"] == now["did"] and services.get(pg, "echo")["did"] == echo["did"]
    assert len(_facts(pg, srv["did"], services.REGISTERED)) == 1 and len(_facts(pg, now["did"], services.REGISTERED)) == 1
    [rf] = _facts(pg, now["did"], services.REGISTERED)
    assert rf["authority_chain"] == [ME, "the kernel"] and rf["payload"]["placement"]["affinity"] == ["clock"]
    # the listing card shows the nesting the glass draws: the tool's manifest names its server
    cards = {s["name"]: s for s in services.listing(pg)}
    assert cards["now"]["manifest"]["server"] == "clock" and cards["clock"]["placement"]["why"] == \
        "stands on local · cpu · reaches 1 of 1 secrets"
    # a server that does not answer refuses in words, and records nothing
    with pytest.raises(services.ServiceRefused, match="did not answer: the command could not be spawned"):
        mcp.register_server(pg, "ghost", "/no/such/server --x", by=ME, home=home)
    assert services.get(pg, "ghost") is None
    assert not [f for f in _facts(pg, ev.scope(), services.REGISTERED) if f["payload"]["name"] == "ghost"]
    monkeypatch.setattr(mcp, "TIMEOUT_S", 1.0)
    with pytest.raises(services.ServiceRefused, match="did not answer: no answer to initialize within 1s"):
        mcp.register_server(pg, "mute", f"{sys.executable} -c 'import time; time.sleep(30)'", by=ME, home=home)
    assert services.get(pg, "mute") is None


def test_a_secret_name_not_reachable_refuses_by_name_and_spawns_nothing(pg, monkeypatch, tmp_path):
    """The env-secrets law at the keeper's door: the named secret is
    checked FIRST — refused by name, no row, no fact, no seed, and no
    process spawned (a locator named by an unreachable env NAME refuses
    the same way); the child's environment is built from NAMES only."""
    _scope(monkeypatch)
    monkeypatch.delenv("NOT_SET_ANYWHERE", raising=False)
    spawned = []
    monkeypatch.setattr(mcp.Session, "open", lambda self: spawned.append(self.locator) or self)
    with pytest.raises(services.ServiceRefused) as e:
        mcp.register_server(pg, "clock", REF, by=ME, secrets_with=["NOT_SET_ANYWHERE"], home=tmp_path)
    assert str(e.value) == "clock is refused here: secret NOT_SET_ANYWHERE is not reachable here"
    assert spawned == [] and services.get(pg, "clock") is None and _facts(pg, ev.scope()) == []   # nothing in THIS world
    assert not (tmp_path / "clock").exists()
    with pytest.raises(services.ServiceRefused, match="secret CLOCK_URL is not reachable here"):
        mcp.register_server(pg, "remote", "env:CLOCK_URL", by=ME, home=tmp_path)
    assert spawned == []
    monkeypatch.setenv("A_KEY_OF_THIS_TEST", "hunter2")
    monkeypatch.setenv("UNRELATED_OF_THIS_TEST", "leak")
    env = mcp.spawn_env(["A_KEY_OF_THIS_TEST"])
    assert env["A_KEY_OF_THIS_TEST"] == "hunter2" and "UNRELATED_OF_THIS_TEST" not in env and "PATH" in env
    assert mcp.locator_words("env:CLOCK_URL") == "the locator named by CLOCK_URL"


def test_a_tool_call_routes_through_tools_call_with_the_chain_and_the_meter(pg, monkeypatch, tmp_path):
    """The librarian declares `tools:now`: the door lists it (the schema
    from the shelf), the acting mind calls it, tools/call answers with
    the real time in Denver; the tool-call row and the fact carry the
    SERVICE DID and the chain H → librarian → did:orreth:service:…; the
    mind's meter line lands as for any tool; a destructive tool
    (destructiveHint) is CONSEQUENTIAL — held at the interlock; an
    undeclared MCP tool is refused with the teaching."""
    _scope(monkeypatch)
    _clock(pg, monkeypatch, tmp_path, listing="now,echo,wipe")
    gw = gateway.FakeActingGateway(script=[("tool", "now", {"zone": "America/Denver"}), ("text", "the clock says: {result}")])
    lib = _body("librarian-resident.v0.json", gw); lib.join(pg)
    door = tools.ToolDoor(pg, did=lib.identity.did, capabilities=lib.template["capabilities"], name="librarian")
    assert [s["name"] for s in door.schemas()][-1] == "now"
    assert next(s for s in door.schemas() if s["name"] == "now")["input_schema"]["properties"] == {"zone": {"type": "string"}}
    ses = glass.open_session(pg, ME)
    [a1] = dispatch.submit_ask(pg, "what time is it in Denver?", person=ME, to=["librarian"], session=ses)
    _serve(pg, lib, a1)
    v = glass.ask_view(pg, a1)
    assert v["status"] == "replied" and v["reply"].startswith("the clock says: ") and " in America/Denver (UTC-0" in v["reply"]
    now_did = services.did_of(pg, "tool", "now")
    cur = pg.cursor()
    cur.execute("SELECT tool, ok, service, authority_chain, ask FROM spine_tool_calls WHERE did = %s", (lib.identity.did,))
    assert [(t, ok, s, json.loads(c), a) for t, ok, s, c, a in cur.fetchall()] == \
        [("now", True, now_did, [ME, lib.identity.did, now_did], a1)]
    [hop] = _facts(pg, a1, tools.TOOL_CALLED)
    assert hop["payload"]["service"] == now_did and hop["authority_chain"] == [ME, lib.identity.did, now_did]
    assert hop["marker"]["kind"] == "action" and hop["marker"]["parent"] == v["marker"]
    [(model, _tin, tout)] = gateway.meter_lines(pg, lib.identity.did)                          # metered like any
    assert (model, tout) == ("claude-haiku-4-5-20251001", 12)
    # a destructive tool is consequential: the interlock, never the first ask
    wipe = services.get(pg, "wipe")
    assert wipe["manifest"]["consequence"] == "consequential"
    door2 = tools.ToolDoor(pg, did=lib.identity.did, capabilities=["tools:wipe"], name="librarian")
    with pytest.raises(tools.ConsequentialHold) as h:
        door2.call("wipe", {})
    assert (h.value.tool, h.value.level) == ("wipe", "L2")
    assert door2.call("wipe", {}, confirmed=True) == "wiped nothing — there was nothing to wipe"
    # undeclared: refused with the teaching, before the wire
    with pytest.raises(tools.ToolRefused, match="never declared the 'echo' tool"):
        door.call("echo", {"text": "hi"})
    # an isError answer is an honest failure at the door (recorded ok=false)
    door3 = tools.ToolDoor(pg, did=lib.identity.did, capabilities=["tools:echo"], name="librarian")
    monkeypatch.setenv("SPINE_MCP_REF_TOOLS", "now")                  # echo vanished under it
    with pytest.raises(tools.ToolRefused, match="failed honestly: MCPUnreachable: no tool named 'echo' here"):
        door3.call("echo", {"text": "hi"})
    cur.execute("SELECT tool, ok FROM spine_tool_calls WHERE did = %s ORDER BY call_id", (lib.identity.did,))
    assert cur.fetchall() == [("now", True), ("wipe", True), ("echo", False)]


def test_a_vanished_tool_goes_unhealthy_with_the_reason_never_retired_and_a_changed_list_versions(pg, monkeypatch, tmp_path):
    """The same server, a changed list: the check VERSIONS the server
    (the pin reads the list), registers the NEW tool under it, and the
    vanished tool goes UNHEALTHY with the words "gone from the server's
    list" — its row, DID and facts stand, never retired by the machine;
    when the server lists it again it is healthy again, the same self;
    the tool's own probe reads its server; a changed schema re-pins."""
    _scope(monkeypatch)
    made = _clock(pg, monkeypatch, tmp_path)
    echo_did = services.get(pg, "echo")["did"]
    monkeypatch.setenv("SPINE_MCP_REF_TOOLS", "now,shout")
    out = services.check(pg, "clock", by=ME)
    assert out["ok"] is True and out["state"] == "healthy"
    assert out["detail"] == ("initialize answered (orreth-clock 0.1.0, protocol 2025-06-18); 2 tools listed; "
                             "new: shout; gone: echo")
    srv = services.get(pg, "clock")
    assert srv["version"] == 2 and [t["name"] for t in srv["manifest"]["tools"]] == ["now", "shout"]
    [vf] = _facts(pg, srv["did"], services.VERSIONED)
    assert vf["payload"]["previous_hash"] == made["server"]["manifest_hash"] and vf["payload"]["version"] == 2
    echo = services.get(pg, "echo")
    assert echo["state"] == "unhealthy" and echo["did"] == echo_did and echo["last_health"]["ok"] is False
    assert echo["last_health"]["detail"] == mcp.GONE == "gone from the server's list"
    assert services.get(pg, "shout")["state"] == "healthy" and services.get(pg, "shout")["manifest"]["server"] == "clock"
    assert _facts(pg, echo_did, services.RETIRED) == []                     # never retired by the machine
    assert services.check(pg, "echo")["detail"] == mcp.GONE               # the tool's own probe reads its server
    assert services.ladder_step("unhealthy", "retire")["ok"]              # the human's step, if they take it
    c = harness.services_healthy(pg)
    assert c["ok"] is False and c["unhealthy"] == ["echo"]
    # listed again: healthy again, the same self; the server versions back (its list changed again)
    monkeypatch.setenv("SPINE_MCP_REF_TOOLS", "now,echo,shout")
    services.check(pg, "clock", by=ME)
    echo = services.get(pg, "echo")
    assert echo["state"] == "healthy" and echo["did"] == echo_did and services.get(pg, "clock")["version"] == 3
    assert [h["ok"] for h in services.health(pg, "echo")] == [True, False, False, True]
    # a server that stops answering: unhealthy with the reason; its tools left as they stand
    monkeypatch.setattr(mcp, "listing_of", lambda *a, **k: (_ for _ in ()).throw(mcp.MCPUnreachable("the server closed its stdout before answering initialize")))
    out = services.check(pg, "clock", by=ME)
    assert out["ok"] is False and out["detail"] == "did not answer: the server closed its stdout before answering initialize"
    assert services.get(pg, "echo")["state"] == "healthy"
    assert harness.mcp_servers_answer(pg) == {"name": "every MCP server answers initialize", "ok": False,
                                              "detail": "0 of 1 answered initialize · silent: clock", "silent": ["clock"], "unprobed": []}


def test_the_keeper_proposes_after_n_strikes_and_never_retires_alone(pg, monkeypatch, tmp_path):
    """The strikes rule (rule 11): the keeper's beat probes every server;
    a tool unhealthy across N checks in a row (the dial, default 3) earns
    ONE proposal — a hold at the interlock under the keeper's own DID,
    cancel the default; while it waits, no second; a cancel resets the
    count; the human's yes retires it with the chain
    [toolkeeper, human, the kernel]; the harness check reads the rule."""
    _scope(monkeypatch)
    monkeypatch.delenv(mcp.STRIKES_DIAL, raising=False)
    keeper = _body("firmware-toolkeeper.v0.json"); keeper.join(pg)
    assert (keeper.kind, keeper.function, keeper.template["capabilities"]) == ("firmware", "tools", ["ask", "tools:services"])
    _clock(pg, monkeypatch, tmp_path)
    monkeypatch.setenv("SPINE_MCP_REF_TOOLS", "now")
    assert mcp.strikes_n() == 3
    for i in (1, 2):
        beat = mcp.keeper_beat(pg, keeper=keeper.identity.did)
        assert beat["proposed"] == [] and mcp.strikes(pg, "echo") == i
        assert harness.keeper_proposes(pg)["ok"] is True
    beat = mcp.keeper_beat(pg, keeper=keeper.identity.did)
    [p] = beat["proposed"]
    assert (p["name"], p["kind"], p["strikes"]) == ("echo", "tool", 3)
    v = glass.ask_view(pg, p["held"])
    assert v["status"] == "awaiting-confirm" and v["served_by"] == "the kernel" and v["person"] == keeper.identity.did
    assert v["hold"] == {"tool": "service.retire", "class": "consequential", "level": "L2"}
    assert v["text"] == ("the toolkeeper proposes retiring the echo tool — unhealthy across 3 checks in a row "
                         "(gone from the server's list)")
    assert v["reply"].startswith("Are you sure? The toolkeeper proposes retiring the echo tool — unhealthy across 3 checks")
    assert services.get(pg, "echo")["state"] == "unhealthy"           # proposed, not retired
    assert mcp.keeper_beat(pg, keeper=keeper.identity.did)["proposed"] == []   # one waits: no second
    assert harness.keeper_proposes(pg)["ok"] is True
    dispatch.confirm_ask(pg, p["held"], approve=False, person=ME)     # cancel: nothing ran; the count reads
    assert services.get(pg, "echo")["state"] == "unhealthy" and mcp.strikes(pg, "echo") == 1   # since the proposal
    assert mcp.keeper_beat(pg, keeper=keeper.identity.did)["proposed"] == []                    # (the beat that waited)
    monkeypatch.setenv(mcp.STRIKES_DIAL, "2")                          # the dial
    [p2] = mcp.keeper_beat(pg, keeper=keeper.identity.did)["proposed"]
    assert p2["strikes"] == 3
    out = dispatch.confirm_ask(pg, p2["held"], approve=True, person=ME)   # the human cuts
    assert out["level"] == "L2"
    echo = services.get(pg, "echo")
    assert echo["state"] == "retired"
    [rf] = _facts(pg, echo["did"], services.RETIRED)
    assert rf["authority_chain"] == [keeper.identity.did, ME, "the kernel"] and rf["marker"]["kind"] == "action"
    assert glass.ask_view(pg, p2["held"])["reply"].startswith("Done, on your word: the echo tool is retired")
    assert harness.keeper_proposes(pg) == {"name": "the keeper proposes after strikes, never retires alone", "ok": True,
                                           "detail": "strikes rule: 2 in a row · every strike proposed", "unproposed": [], "alone": 0}
    # a retired tool is left at rest by the sync (the human's stop stands), even when listed again
    monkeypatch.setenv("SPINE_MCP_REF_TOOLS", "now,echo")
    out = services.check(pg, "clock", by=ME)
    assert "refused: echo: retired by the human — left at rest" in out["detail"]
    assert services.get(pg, "echo")["state"] == "retired"
    # a body retiring ALONE (no ask, no hold) is what the harness names — the law's teeth
    services.retire(pg, "now", by=keeper.identity.did)
    assert harness.keeper_proposes(pg)["alone"] == 1 and harness.keeper_proposes(pg)["ok"] is False


def test_the_keeper_thinks_through_the_gateway_and_its_register_holds_while_check_runs_at_once(pg, monkeypatch, tmp_path):
    """The keeper's words: "toolkeeper, add the MCP server at <cmd>" → the
    `services` tool's register is CONSEQUENTIAL — held at the interlock;
    the human's yes registers the server and its tools (the facts under
    the keeper's DID, the meter line for the keeper's self); "check the
    tools" runs at once (routine by the arguments); "what changed on the
    shelf?" reads the ladder's facts; a retire on the keeper's word holds,
    and lands as an ACTION under the ask (never alone)."""
    _scope(monkeypatch)
    services.HOME = tmp_path                                            # the rig's home, the keeper's door
    try:
        gw = gateway.FakeActingGateway(script=[("tool", "services", {"action": "register", "name": "clock", "locator": REF}),
                                               ("text", "{result}")])
        keeper = _body("firmware-toolkeeper.v0.json", gw); keeper.join(pg)
        ses = glass.open_session(pg, ME)
        [a1] = dispatch.submit_ask(pg, f"toolkeeper, add the MCP server at {REF}", person=ME, to=["toolkeeper"], session=ses)
        _serve(pg, keeper, a1)
        v = glass.ask_view(pg, a1)
        assert v["status"] == "awaiting-confirm" and v["hold"] == {"tool": "services", "class": "consequential", "level": "L2"}
        assert services.get(pg, "clock") is None                        # held: nothing registered yet
        keeper._serve_conn = pg
        with pg.transaction():
            keeper._confirm_ask(pg.cursor(), a1, True, [ME], proof="L2", by=ME)
        v = glass.ask_view(pg, a1)
        assert v["status"] == "replied" and v["reply"].startswith(
            "Done, on your word: registered the clock MCP server (orreth-clock 0.1.0) at ")
        assert v["reply"].endswith("— 2 tools on the shelf under it: now, echo")
        assert services.get(pg, "clock")["by"] == keeper.identity.did and services.get(pg, "now")["by"] == keeper.identity.did
        assert (tmp_path / "clock" / "seed").exists() and (tmp_path / "now" / "seed").exists()
        assert gateway.meter_lines(pg, keeper.identity.did)[0][0] == "claude-haiku-4-5-20251001"
        # "toolkeeper, check the tools" — routine: no hold, the answer at once
        keeper.gateway = gateway.FakeActingGateway(script=[("tool", "services", {"action": "check"}), ("text", "{result}")])
        [a2] = dispatch.submit_ask(pg, "toolkeeper, check the tools", person=ME, to=["toolkeeper"], session=ses)
        _serve(pg, keeper, a2)
        v2 = glass.ask_view(pg, a2)
        assert v2["status"] == "replied" and v2["reply"].startswith("checked 1: clock (mcp) → healthy: initialize answered")
        # "toolkeeper, what changed on the shelf?" — the ladder's facts, in words
        keeper.gateway = gateway.FakeActingGateway(script=[("tool", "services", {"action": "changes"}), ("text", "{result}")])
        [a3] = dispatch.submit_ask(pg, "toolkeeper, what changed on the shelf?", person=ME, to=["toolkeeper"], session=ses)
        _serve(pg, keeper, a3)
        v3 = glass.ask_view(pg, a3)
        assert v3["reply"].startswith("9 changes on the shelf: ") and "clock (mcp) register: registered" in v3["reply"]
        assert "now (tool) healthy: healthy" in v3["reply"] and "echo (tool) healthy: healthy" in v3["reply"]
        # the keeper's own retire: held (consequential), then an ACTION under the ask — never alone
        keeper.gateway = gateway.FakeActingGateway(script=[("tool", "services", {"action": "retire", "name": "echo"}), ("text", "{result}")])
        [a4] = dispatch.submit_ask(pg, "toolkeeper, retire echo", person=ME, to=["toolkeeper"], session=ses)
        _serve(pg, keeper, a4)
        assert glass.ask_view(pg, a4)["status"] == "awaiting-confirm" and services.get(pg, "echo")["state"] == "healthy"
        with pg.transaction():
            keeper._confirm_ask(pg.cursor(), a4, True, [ME], proof="L2", by=ME)
        assert services.get(pg, "echo")["state"] == "retired"
        [rf] = _facts(pg, services.get(pg, "echo")["did"], services.RETIRED)
        assert rf["marker"]["kind"] == "action" and rf["correlation_id"] == a4 and rf["authority_chain"] == [keeper.identity.did, "the kernel"]
        assert harness.keeper_proposes(pg)["alone"] == 0
        # the class by the arguments: the pin on the shelf reads the declared class (consequential), the door reads the act
        spec = tools.TOOLS["services"]
        assert tools.consequence_of(spec) == "consequential" and tools.consequence_of(spec, {"action": "check"}) == "routine"
        assert tools.consequence_of(spec, {"action": "restore"}) == "consequential"
        assert tools.tool_manifest("services", spec)["consequence"] == "consequential"
    finally:
        services.HOME = None


def test_mitl_names_an_mcp_servers_tools_and_a_tools_server(pg, monkeypatch, tmp_path):
    """MITL's read_ground (kind service): a change on the server names
    every tool under it and the bodies that declared them; a change on an
    MCP-born tool names the server it came through."""
    _scope(monkeypatch)
    lib = _body("librarian-resident.v0.json"); lib.join(pg)
    _clock(pg, monkeypatch, tmp_path)
    t = mitl.read_ground(pg, {"kind": "service", "draft": {"name": "clock"}})
    assert [s["name"] for s in t["services"]] == ["clock", "echo", "now"]
    assert [b["name"] for b in t["bodies"]] == ["librarian"]            # declares tools:now
    assert any(n.startswith("clock is an MCP server (stdio, at ") and n.endswith("2 tools under it: echo (healthy), now (healthy)")
               for n in t["notes"])
    assert mitl.verdict(t) == "consider"
    t2 = mitl.read_ground(pg, {"kind": "service", "draft": {"name": "now"}})
    assert "now came through the clock MCP server (tools/call at the one door)" in t2["notes"]
    t3 = mitl.read_ground(pg, {"kind": "act", "draft": {"tool": "now"}})           # an act on an MCP-born tool reads its class
    assert t3["services"][0]["name"] == "now" and [b["name"] for b in t3["bodies"]] == ["librarian"]


@rails
def test_the_shelf_door_shows_the_nesting_and_the_keeper_stands_in_the_crew(pg, rig, monkeypatch):
    """The rig births the toolkeeper (third kind) beside mitl; the MCP door
    `POST /services/mcp` registers the reference clock and lists its tools
    under it; `GET /services` shows the server with its tools naming it
    (the glass nests them); the harness door carries the two checks."""
    end = time.monotonic() + 20
    while time.monotonic() < end:
        _s, body = _get(rig.port, "/crew")
        if "toolkeeper" in body.decode():
            break
        time.sleep(0.3)
    crew = json.loads(body)
    tk = next(b for b in crew["crew"] if b["name"] == "toolkeeper")
    assert tk["kind"] == "firmware" and "tools:services" in tk["capabilities"]
    _scope(monkeypatch)                     # the shelf of THIS test's world (the session's shelf stays as it was)
    st, r = _post(rig.port, "/services/mcp", {"name": "clock", "locator": REF, "person": ME})
    assert st == 201 and r["service"]["kind"] == "mcp" and r["tools"]["new"] == ["now", "echo"]
    _s, body = _get(rig.port, "/services?kind=tool")
    by_name = {s["name"]: s for s in json.loads(body)["services"]}
    assert by_name["now"]["manifest"]["server"] == "clock" and by_name["now"]["state"] == "healthy"
    _s, body = _get(rig.port, "/services?kind=mcp")
    [srv] = json.loads(body)["services"]
    assert srv["name"] == "clock" and srv["manifest"]["locator"] == REF and len(srv["manifest"]["tools"]) == 2
    with pytest.raises(urllib.error.HTTPError) as e:
        _post(rig.port, "/services/mcp", {"name": "ghost", "locator": "/no/such/server", "person": ME})
    assert e.value.code == 400 and b"did not answer" in e.value.read()
    _s, h = _get(rig.port, "/harness")
    checks = {c["name"]: c for c in json.loads(h)["checks"]}
    assert checks["every MCP server answers initialize"]["ok"] is True
    assert checks["the keeper proposes after strikes, never retires alone"]["ok"] is True


def test_a_proposal_whose_reason_passed_withdraws_itself(pg, monkeypatch, tmp_path):
    """W49 (walk #12): the keeper proposed retiring a tool for being
    unhealthy; the tool answers its next check — the kernel withdraws the
    waiting proposal in words (a recorded cancel), so no stale hold waits
    on the human; a human's own retire hold is never touched."""
    _scope(monkeypatch)
    monkeypatch.delenv(mcp.STRIKES_DIAL, raising=False)
    keeper = _body("firmware-toolkeeper.v0.json"); keeper.join(pg)
    _clock(pg, monkeypatch, tmp_path)
    monkeypatch.setenv("SPINE_MCP_REF_TOOLS", "now")
    for _ in range(3):
        beat = mcp.keeper_beat(pg, keeper=keeper.identity.did)
    [p] = beat["proposed"]
    assert glass.ask_view(pg, p["held"])["status"] == "awaiting-confirm"
    mine = services.hold_retire(pg, "now", person=ME)                # the human's own hold stands apart
    monkeypatch.setenv("SPINE_MCP_REF_TOOLS", "now,echo")             # echo is listed again
    services.check(pg, "clock", by=ME)
    assert services.get(pg, "echo")["state"] == "healthy"
    v = glass.ask_view(pg, p["held"])
    assert v["status"] != "awaiting-confirm"
    assert "Withdrawn — the echo service answered its check and is healthy again; nothing to retire" in (v["reply"] or "")
    assert glass.ask_view(pg, mine)["status"] == "awaiting-confirm"
    assert mcp.keeper_beat(pg, keeper=keeper.identity.did)["proposed"] == []