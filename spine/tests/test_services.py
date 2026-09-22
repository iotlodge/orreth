# PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P6.5 sp1, the services registry · 2026-09-22
"""The services registry, one ladder (canon 0005 P6.5 sp1 · 0009 §3): every
service the kernel governs — tool · mcp · store · source · mind — is an
identity on one lifecycle ladder; the meter reads the ladder; retire is
dormancy held at the interlock, never deletion; the env-secrets law (a
key in ZERO records); placement honored at register like a body's birth."""
import json
import secrets
import time
import urllib.request
from pathlib import Path

import pytest

from orreth_spine import (dispatch, envelope as ev, export, gateway, glass, harness, markers, mitl, proof,
                          resident, services, tools)

from tests.test_glass import _get, _post  # noqa: E402
from tests.test_mind import _rails_up  # noqa: E402

SPINE = Path(__file__).resolve().parents[1]
POLICY = SPINE / "policy" / "covenant-policy.v1.json"
ME = "did:orreth:person:test"
rails = pytest.mark.skipif(not _rails_up(), reason="the rails are not up")

WEATHER = tools.tool_manifest("weather", tools.TOOLS["weather"])
MIND = {"route": "anthropic", "model": "claude-haiku-4-5-20251001"}
MCP = {"server": "weather-mcp", "url_secret": "WEATHER_MCP_URL",
       "tools": [{"name": "forecast", "input_schema": {"type": "object", "properties": {}}}]}


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
    cur.execute("SELECT body FROM spine_outbox WHERE convert_from(body, 'UTF8') LIKE %s"
                " ORDER BY outbox_id", (f"%{needle}%",))
    out = [ev.decode(bytes(b)) for (b,) in cur.fetchall()]
    return [e for e in out if type_ is None or e["type"] == type_]


def test_register_mints_a_persistent_self_and_the_same_manifest_is_the_same_self(pg, monkeypatch, tmp_path):
    """Rule 1 for services: the seed lives under <home>/<name>/seed; two
    registers (and a second life from the same home) wear the SAME
    service DID; the fact carries the pin, the placement, the chain
    [person, the kernel] and an observation marker; the pin is sha256
    over the manifest's canonical bytes."""
    _scope(monkeypatch)
    home = tmp_path / "services"
    made = services.register(pg, "weather", "tool", WEATHER, by=ME, home=home)
    assert made["did"].startswith("did:orreth:service:") and made["state"] == "registered"
    assert made["version"] == 1 and made["manifest_hash"] == ev.content_hash(WEATHER) == services.pin(WEATHER)
    assert (home / "weather" / "seed").exists()
    again = services.register(pg, "weather", "tool", WEATHER, by=ME, home=home)
    assert again["did"] == made["did"] and again["version"] == 1          # the same self, silently
    assert len(_facts(pg, made["did"], services.REGISTERED)) == 1        # one register, one fact
    # a second life (another process would read the same seed): the same DID
    from orreth_spine.identity import Identity
    assert Identity.load("weather", home, kind="service").did == made["did"]
    assert Identity.load("weather", home).did != made["did"]             # an agent of that name is another self
    [fact] = _facts(pg, made["did"], services.REGISTERED)
    assert fact["authority_chain"] == [ME, "the kernel"] and fact["payload"]["hash"] == made["manifest_hash"]
    assert fact["payload"]["placement"] == {"cell": "local", "affinity": [], "secrets_with": [], "metal": "any"}
    assert fact["marker"]["kind"] == "observation" and fact["marker"]["by"] == ME
    assert markers.get(pg, fact["marker"]["id"])["note"] == "weather (tool) register: registered"
    root = markers.get(pg, fact["marker"]["id"])["parent"]          # ONE origin per world: the shelf
    assert markers.get(pg, root)["ref"] == "the shelf" and markers.get(pg, root)["parent"] is None
    assert services.shelf_root(pg) == root
    assert services.versions(pg, "weather") == [{"version": 1, "manifest_hash": made["manifest_hash"],
                                                 "by": ME, "at": services.versions(pg, "weather")[0]["at"]}]
    # a changed manifest is not a second register — the ladder says "version it"
    with pytest.raises(services.ServiceRefused, match="already registered — version it"):
        services.register(pg, "weather", "tool", dict(WEATHER, description="other words"), by=ME, home=home)
    v2 = services.version(pg, "weather", dict(WEATHER, description="other words"), by=ME)
    assert (v2["state"], v2["version"], v2["did"]) == ("versioned", 2, made["did"])
    [vf] = _facts(pg, made["did"], services.VERSIONED)
    assert vf["payload"]["previous_hash"] == made["manifest_hash"] and vf["payload"]["version"] == 2
    with pytest.raises(services.ServiceRefused, match="unchanged — nothing to version"):
        services.version(pg, "weather", dict(WEATHER, description="other words"), by=ME)


def test_the_ladder_refuses_a_skipped_step_by_name(pg, monkeypatch):
    """The pure law and the record agree: restore from a standing state,
    version or check on a retired one, retire twice, register twice, a
    step that is not on the ladder — each refused with the reason words."""
    assert services.ladder_step(None, "register") == {"ok": True, "to": "registered", "reason": None}
    assert services.ladder_step("registered", "version")["to"] == "versioned"
    assert services.ladder_step("versioned", "healthy")["to"] == "healthy"
    assert services.ladder_step("healthy", "unhealthy")["to"] == "unhealthy"
    assert services.ladder_step("unhealthy", "retire")["to"] == "retired"
    assert services.ladder_step("retired", "restore")["to"] == "registered"
    assert services.ladder_step("retired", "version")["reason"] == \
        "retired — the ladder runs no version on a retired service; restore it first"
    assert services.ladder_step("healthy", "restore")["reason"] == "healthy, not retired — nothing to restore"
    assert services.ladder_step(None, "retire")["reason"].startswith("not registered")
    assert services.ladder_step("registered", "fly")["reason"].startswith("no step named 'fly'")
    _scope(monkeypatch)
    services.register(pg, "record", "store", {"locator": "SPINE_PG", "table": "spine_memories"}, by=ME)
    with pytest.raises(services.ServiceRefused, match="registered, not retired — nothing to restore"):
        services.restore(pg, "record", by=ME)
    services.retire(pg, "record", by=ME)
    with pytest.raises(services.ServiceRefused, match="already retired — nothing to retire"):
        services.retire(pg, "record", by=ME)
    with pytest.raises(services.ServiceRefused, match="runs no version on a retired service"):
        services.version(pg, "record", {"locator": "SPINE_PG"}, by=ME)
    with pytest.raises(services.ServiceRefused, match="runs no healthy on a retired service"):
        services.check(pg, "record")
    with pytest.raises(services.ServiceRefused, match="restored, never registered twice"):
        services.register(pg, "record", "store", {"locator": "SPINE_PG"}, by=ME)
    with pytest.raises(services.ServiceRefused, match="no service named 'ghost'"):
        services.check(pg, "ghost")
    with pytest.raises(services.ServiceRefused, match="one of tool, mcp, store, source, mind"):
        services.register(pg, "x", "organ", {"a": 1}, by=ME)
    with pytest.raises(services.ServiceRefused, match="already registered as a store"):
        services.restore(pg, "record", by=ME) and services.register(pg, "record", "tool", WEATHER, by=ME)


def test_a_secret_not_reachable_refuses_by_name_and_records_nothing_and_placement_is_honored(pg, monkeypatch):
    """The env-secrets law at register: a named secret the ground cannot
    reach refuses BY NAME — no row, no fact, no seed; a value never
    appears anywhere. Placement is honored like a body's birth: metal
    gpu on a cpu ground refuses in words; a reachable secret is shown
    on the shelf by NAME with a reached mark."""
    _scope(monkeypatch)
    monkeypatch.delenv("NOT_SET_ANYWHERE", raising=False)
    with pytest.raises(services.ServiceRefused) as e:
        services.register(pg, "weather-mcp", "mcp", MCP, by=ME, secrets_with=["NOT_SET_ANYWHERE"])
    assert str(e.value) == "weather-mcp is refused here: secret NOT_SET_ANYWHERE is not reachable here"
    assert services.get(pg, "weather-mcp") is None and _facts(pg, "weather-mcp") == []   # nothing recorded
    with pytest.raises(services.ServiceRefused, match="metal gpu is not here \\(cpu\\)"):
        services.register(pg, "cuda-mind", "mind", {"route": "local", "model": "llama"}, by=ME,
                          placement={"metal": "gpu"})
    assert services.listing(pg) == []
    monkeypatch.setenv("A_SECRET_OF_THIS_TEST", "hunter2")
    made = services.register(pg, "weather-mcp", "mcp", MCP, by=ME, secrets_with=["A_SECRET_OF_THIS_TEST"])
    assert made["secrets_with"] == ["A_SECRET_OF_THIS_TEST"]
    [card] = services.listing(pg, kind="mcp")
    assert card["secrets"] == [{"name": "A_SECRET_OF_THIS_TEST", "reached": True}]
    assert card["placement"]["why"] == "stands on local · cpu · reaches 1 of 1 secrets"
    assert "hunter2" not in json.dumps(card) and "hunter2" not in json.dumps(_facts(pg, made["did"]))
    # the mcp's health is honestly "not yet probed" — the ladder does not move
    out = services.check(pg, "weather-mcp")
    assert out["ok"] is None and out["detail"].startswith("not yet probed") and out["state"] == "registered"
    assert services.get(pg, "weather-mcp")["last_health"]["ok"] is None


def test_retire_is_held_then_rested_never_deleted_and_restore_is_a_new_fact(pg, monkeypatch):
    """Retiring is consequential: the door holds it as the kernel's own
    act at L2 (cancel the default; a cancel runs nothing); MITL reads
    the held act and names the service and the bodies that declared it;
    the human's yes retires it — the row, its versions and its facts
    stay; the door refuses a retired tool with a teaching; restore is a
    NEW fact and the tool serves again."""
    _scope(monkeypatch)
    lib = _body("librarian-resident.v0.json"); lib.join(pg)
    made = services.register(pg, "weather", "tool", WEATHER, by=ME)
    ses = glass.open_session(pg, ME)
    held = services.hold_retire(pg, "weather", person=ME, session=ses)
    v = glass.ask_view(pg, held)
    assert v["status"] == "awaiting-confirm" and v["served_by"] == "the kernel"
    assert v["hold"] == {"tool": "service.retire", "class": "consequential", "level": "L2"}
    assert v["reply"] == ("Are you sure? Retiring the weather tool is consequential — it is recorded, and "
                          "you can restore it later. Cancel is the default; a deliberate click confirms.")
    t = mitl.read_ground(pg, {"kind": "service", "ref": held})
    assert t["services"] == [{"name": "weather", "kind": "tool", "did": made["did"], "state": "registered", "version": 1}]
    assert [b["name"] for b in t["bodies"]] == ["librarian"] and (t["class"], t["level"]) == ("consequential", "L2")
    assert mitl.verdict(t) == "consider"
    dispatch.confirm_ask(pg, held, approve=False, person=ME)                   # cancel: nothing ran
    assert glass.ask_view(pg, held)["status"] == "cancelled"
    assert services.get(pg, "weather")["state"] == "registered"
    held2 = services.hold_retire(pg, "weather", person=ME, session=ses)
    out = dispatch.confirm_ask(pg, held2, approve=True, person=ME)             # the deliberate yes
    assert out == {"id": held2, "approve": True, "level": "L2"}
    v2 = glass.ask_view(pg, held2)
    assert v2["status"] == "replied" and v2["proof"] == "L2"
    assert v2["reply"].startswith("Done, on your word: the weather tool is retired — at rest on the shelf, recorded, never deleted")
    row = services.get(pg, "weather")
    assert row["state"] == "retired" and row["did"] == made["did"] and row["version"] == 1   # never deleted
    [rf] = _facts(pg, made["did"], services.RETIRED)
    assert rf["authority_chain"] == [ME, "the kernel"] and rf["payload"]["from"] == "registered"
    assert rf["marker"]["kind"] == "action" and rf["marker"]["parent"] == v2["marker"]     # under the held ask
    assert rf["correlation_id"] == held2
    with pytest.raises(services.ServiceRefused, match="already retired"):
        services.hold_retire(pg, "weather", person=ME)
    door = tools.ToolDoor(pg, did=lib.identity.did, capabilities=["tools:weather"], name="librarian")
    with pytest.raises(tools.ToolRefused, match="the weather tool is retired on this shelf"):
        door.call("weather", {})
    assert tools.journal(pg, lib.identity.did) == []                          # refused before the door
    [card] = services.listing(pg, kind="tool")
    assert card["state"] == "retired" and card["restorable"] and not card["retirable"]
    back = services.restore(pg, "weather", by=ME)
    assert back["state"] == "registered" and back["did"] == made["did"]
    [sf] = _facts(pg, made["did"], services.RESTORED)
    assert sf["authority_chain"] == [ME, "the kernel"] and sf["marker"]["kind"] == "observation"
    assert len(_facts(pg, made["did"], services.RETIRED)) == 1               # its stop stays in the record
    assert [m["kind"] for m in markers.tree(pg, v2["marker"])] == ["objective", "action"]
    # the export of the session reads the hold, the retire's L2 proof, intact chains
    b = export.build(pg, person=ME, session=ses)
    kinds = [(r["kind"], r["proof"]) for r in b["rows"] if r["ref"] == held2]
    assert ("hold", "L2") in kinds and ("reply", "L2") in kinds and export.verify(b)
    assert b["summary"]["chain_broken"] == 0


def test_the_meter_and_tool_rows_carry_the_service_did_and_the_export_reads_it(pg, monkeypatch):
    """The meter reads the ladder: with the built-ins seeded, a served
    ask's meter row carries the MIND service's DID, its tool-call row and
    the tool-called fact carry the TOOL service's DID, and the export's
    tool hop reads H → resident → did:orreth:service:… (intact); an
    unregistered tool keeps `tool:<name>` as the honest fallback."""
    _scope(monkeypatch)
    gw = gateway.FakeActingGateway(script=[
        ("tool", "acquire", {"key": "hemp", "text": "lime binds hempcrete"}),
        ("text", "kept: {result}")])
    seeded = services.seed(pg, gateway=gw)
    assert seeded["refused"] == [] and set(seeded["registered"]) >= {"weather", "acquire", "ground", "record",
                                                                       "fake-acting-mind"}
    assert services.seed(pg, gateway=gw)["registered"] == []               # idempotent: the same selves
    kinds = {s["name"]: s["kind"] for s in services.listing(pg)}
    assert kinds["acquire"] == "tool" and kinds["ground"] == "store" and kinds["fake-acting-mind"] == "mind"
    acquire, fake = services.did_of(pg, "tool", "acquire"), services.did_of(pg, "mind", "fake-acting-mind")
    assert services.mind_did(pg, "fake-acting-mind") == fake
    # the librarian's template names Haiku: the meter names the model the body ASKED for,
    # so the line carries the DID of the mind service that model belongs to — none, honestly,
    # until that mind is on the shelf (the rig seeds the Anthropic route when its key is reachable)
    mind = services.register(pg, "anthropic", "mind", MIND, by=ME)["did"]
    lib = _body("librarian-resident.v0.json", gw); lib.join(pg)
    ses = glass.open_session(pg, ME)
    [a1] = dispatch.submit_ask(pg, "keep this: lime binds hempcrete", person=ME, to=["librarian"], session=ses)
    _serve(pg, lib, a1)
    cur = pg.cursor()
    cur.execute("SELECT service, model FROM spine_meter WHERE did = %s", (lib.identity.did,))
    assert cur.fetchall() == [(mind, "claude-haiku-4-5-20251001")]
    cur.execute("SELECT service, authority_chain FROM spine_tool_calls WHERE did = %s", (lib.identity.did,))
    assert [(s, json.loads(c)) for s, c in cur.fetchall()] == [(acquire, [ME, lib.identity.did, acquire])]
    [hop] = _facts(pg, a1, tools.TOOL_CALLED)
    assert hop["payload"]["service"] == acquire and hop["authority_chain"] == [ME, lib.identity.did, acquire]
    b = export.build(pg, person=ME, session=ses)
    row = next(r for r in b["rows"] if r["kind"] == "tool")
    assert row["served_by"] == acquire and row["authority_chain"][-1] == acquire and row["chain_status"] == "intact"
    assert export.verify(b) and b["summary"]["chain_broken"] == 0
    # the mind's own canary ping is metered under the SERVICE's DID, the service naming itself
    out = services.check(pg, "fake-acting-mind", gateway=gateway.FakeGateway(reply="pong"))
    assert out["ok"] is True and "one-token ping" in out["detail"]
    cur.execute("SELECT did, service, model FROM spine_meter WHERE did = %s", (fake,))
    assert cur.fetchall() == [(fake, fake, "fake-acting-mind")]    # the mind's own line names itself
    # an unregistered tool in another world keeps the fallback
    monkeypatch.setenv("SPINE_SCOPE", "u:law-" + secrets.token_hex(3))
    lib2 = _body("librarian-resident.v0.json", gateway.FakeActingGateway(script=[
        ("tool", "acquire", {"key": "k", "text": "t"}), ("text", "ok")]))
    lib2.join(pg)
    [a2] = dispatch.submit_ask(pg, "keep k", person=ME, to=["librarian"])
    _serve(pg, lib2, a2)
    [hop2] = _facts(pg, a2, tools.TOOL_CALLED)
    assert "service" not in hop2["payload"] and hop2["authority_chain"][-1] == "tool:acquire"


def test_the_harness_check_names_an_unhealthy_service_and_a_retired_one_passes(pg, monkeypatch):
    """A tool registered that the door does not describe is unhealthy —
    the harness names it; a schema that moved under the pin is unhealthy
    ("version it"); the store's locator is reachable by name; retiring
    the unhealthy one lets the check pass; a service never probed is
    named as not yet probed."""
    _scope(monkeypatch)
    assert harness.services_healthy(pg) == {"name": "every service healthy or retired", "ok": True,
                                            "detail": "no services on the shelf", "unhealthy": [], "unprobed": []}
    services.register(pg, "ghost", "tool", {"name": "ghost", "input_schema": {}}, by=ME)
    services.register(pg, "weather", "tool", dict(WEATHER, description="stale words"), by=ME)
    services.register(pg, "ground", "store", {"locator": "SPINE_PG"}, by=ME)
    services.register(pg, "record", "store", {"locator": "SPINE_PG", "table": "spine_memories"}, by=ME)
    monkeypatch.delenv("NOT_SET_ANYWHERE", raising=False)
    services.register(pg, "lake", "source", {"locator": "NOT_SET_ANYWHERE"}, by=ME)
    c = harness.services_healthy(pg)
    assert c["ok"] is False and c["unprobed"] == ["lake", "ground", "record", "ghost", "weather"]   # by kind, name
    checked = {x["name"]: x for x in services.check_all(pg)}
    assert checked["ghost"]["ok"] is False and "names no tool called 'ghost'" in checked["ghost"]["detail"]
    assert checked["weather"]["ok"] is False and checked["weather"]["detail"].endswith("— version it")
    assert checked["ground"]["ok"] is True and checked["record"]["detail"].endswith("table spine_memories stands")
    assert checked["lake"]["ok"] is False and checked["lake"]["detail"] == "the locator NOT_SET_ANYWHERE is not reachable by name here"
    c = harness.services_healthy(pg)
    assert c["ok"] is False and c["unhealthy"] == ["lake", "ghost", "weather"] and c["unprobed"] == []
    assert c["detail"] == "2 healthy · 0 retired · unhealthy: lake, ghost, weather"
    assert [x["name"] for x in harness.checks(pg)][-1] == "every service healthy or retired"
    services.version(pg, "weather", WEATHER, by=ME)                          # the pin follows the door
    assert services.check(pg, "weather")["ok"] is True
    for name in ("ghost", "lake"):
        services.retire(pg, name, by=ME)
    c = harness.services_healthy(pg)
    assert c["ok"] is True and c["detail"] == "3 healthy · 2 retired"
    # a probe is never a new root: every step hangs under its service, under the one shelf origin
    roots = [o for o in markers.origins(pg) if o["ref"] == "the shelf"]
    assert len(roots) == 1 and roots[0]["counts"]["observation"] >= 5 + 5    # 5 registers + the probes
    hist = services.health(pg, "weather")
    assert [h["ok"] for h in hist] == [True, False] and len(_facts(pg, services.did_of(pg, "tool", "weather"), services.HEALTH)) == 2


@rails
def test_the_built_ins_register_at_birth_and_the_shelf_door_lists_every_kind(pg, rig):
    """The rig's birth puts the built-ins on the shelf (seven tools, the
    ground, the Record) and probes them; `GET /services` lists them with
    kind · did · ladder state · placement why-line · secrets · last
    health; `?kind=` filters; a stranger's kind is refused in words;
    `/services/retire` holds at L2 and `/confirm` retires; `/services/restore`
    is a new fact; the harness door carries the check."""
    end = time.monotonic() + 20
    shelf = []
    while time.monotonic() < end:
        _s, body = _get(rig.port, "/services")
        shelf = json.loads(body)["services"]
        if len(shelf) >= 9 and all(s["last_health"] for s in shelf):
            break
        time.sleep(0.3)
    by_name = {s["name"]: s for s in shelf}
    assert set(by_name) == {"weather", "acquire", "mark", "purge-memory", "add-watch", "seal-record",
                            "erase-record", "ground", "record"}       # no gateway: no mind seeded (honest)
    assert {s["kind"] for s in shelf} == {"tool", "store"}
    assert all(s["did"].startswith("did:orreth:service:") and s["state"] == "healthy" for s in shelf)
    assert by_name["weather"]["placement"]["why"] == "stands on local · cpu" and by_name["weather"]["secrets"] == []
    assert by_name["record"]["last_health"]["ok"] is True
    _s, body = _get(rig.port, "/services?kind=store")
    assert {s["name"] for s in json.loads(body)["services"]} == {"ground", "record"}
    with pytest.raises(urllib.error.HTTPError) as e:
        _get(rig.port, "/services?kind=organ")
    assert e.value.code == 400
    _s, h = _get(rig.port, "/harness")
    assert {c["name"]: c["ok"] for c in json.loads(h)["checks"]}["every service healthy or retired"] is True
    st, r = _post(rig.port, "/services/retire", {"name": "seal-record", "person": ME})
    assert st == 202 and r["level"] == "L2" and r["held"].startswith("ask_")
    st, v = _get(rig.port, f"/ask/{r['held']}")
    assert json.loads(v)["hold"]["tool"] == "service.retire"
    st, out = _post(rig.port, "/confirm", {"ask_id": r["held"], "approve": True, "person": ME})
    assert st == 202 and out["level"] == "L2"
    _s, body = _get(rig.port, "/services?kind=tool")
    assert {s["name"]: s["state"] for s in json.loads(body)["services"]}["seal-record"] == "retired"
    st, back = _post(rig.port, "/services/restore", {"name": "seal-record", "person": ME})
    assert st == 201 and back["service"]["state"] == "registered"
    st, chk = _post(rig.port, "/services/check", {"name": "seal-record", "person": ME})
    assert st == 200 and chk["ok"] is True and chk["checked"][0]["state"] == "healthy"
    st, reg = _post(rig.port, "/services", {"name": "weather-mcp", "kind": "mcp", "manifest": MCP, "person": ME})
    assert st == 201 and reg["service"]["kind"] == "mcp"
    with pytest.raises(urllib.error.HTTPError) as e:
        _post(rig.port, "/services", {"name": "weather-mcp", "kind": "mcp", "manifest": dict(MCP, tools=[]),
                                      "person": ME})
    assert e.value.code == 400 and b"version it" in e.value.read()
