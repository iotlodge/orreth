# PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P6.5 sp3, the Stable keeper · 2026-09-24
"""The Stable keeper (canon 0005 P6.5 sp3 · 0009 §2 · 0019 · 0058 · JB's
lock 2026-09-24: LiteLLM executes, the registry knows and decides): a
mind is a stall on the one ladder AND a model entry in the gateway; a
body thinks through the gateway with its OWN key wearing its lease; the
meter lands dollars; a drained lease speaks in words and the keeper
proposes a refill; the market's eyes (drift → re-pin proposal, EOL →
retire proposal with the swap); the keeper never acts alone; the harness
runs model arms and reads four new world checks; the keeper's tool holds
what is consequential and names the act at the interlock (W30); a server
names itself (W28); a keeper's follow-up stays with the keeper (W29)."""
import json
import secrets
from datetime import datetime, timezone
from pathlib import Path

import pytest

from orreth_spine import dispatch, envelope as ev, gateway, glass, harness, mcp, monitor, resident, services, stable, tools
from tests.fake_gateway import MASTER, FakeLiteLLM

SPINE = Path(__file__).resolve().parents[1]
POLICY = SPINE / "policy" / "covenant-policy.v1.json"
ME = "did:orreth:person:test"
HAIKU, SONNET = "claude-haiku-4-5-20251001", "claude-sonnet-5"
PRICES = {f"anthropic/{HAIKU}": (1e-6, 5e-6), f"anthropic/{SONNET}": (3e-6, 15e-6), "ollama/llama3.2": (0.0, 0.0),
          "openrouter/meta-llama/llama-3.3-70b-instruct": (0.1e-6, 0.3e-6)}


@pytest.fixture
def fake(monkeypatch):
    f = FakeLiteLLM(prices=PRICES)
    monkeypatch.setenv(stable.GATEWAY_DIAL, f.base)
    monkeypatch.setenv(stable.GATEWAY_KEY_DIAL, MASTER)
    monkeypatch.setenv("SPINE_SCOPE", "u:stable-" + secrets.token_hex(3))
    yield f
    f.close()


def _body(template, gw=None):
    r = resident.Resident(SPINE / "templates" / template, gateway=gw)
    r.load_policy(POLICY)
    return r


def _facts(pg, needle, type_=None):
    cur = pg.cursor()
    cur.execute("SELECT body FROM spine_outbox WHERE convert_from(body, 'UTF8') LIKE %s ORDER BY outbox_id", (f"%{needle}%",))
    out = [ev.decode(bytes(b)) for (b,) in cur.fetchall()]
    return [e for e in out if type_ is None or e["type"] == type_]


def _serve(pg, body, ask_id, chain=(ME,)):
    body._serve_conn = pg
    with pg.transaction():
        body._serve_ask(pg.cursor(), ask_id, list(chain))


def test_a_stall_is_a_service_on_the_ladder_and_a_model_entry_in_the_gateway(pg, fake):
    """register_mind: the deal pinned (key by NAME, price per million),
    the same self every life, the gateway holding the entry by the
    stall's name with `os.environ/NAME` — the value never travels; a
    key VALUE refused before anything is recorded; retire drops the
    entry and restore rewrites it; the seed registers the rig's own."""
    gw = gateway.LiteLLMGateway()
    seeded = services.seed(pg, gateway=gw, home=None)
    assert "haiku" in seeded["registered"] and seeded["refused"] == []
    h = services.get(pg, "haiku")
    assert h["kind"] == "mind" and h["manifest"]["route"] == f"anthropic/{HAIKU}" and h["manifest"]["key"] == "ANTHROPIC_API_KEY"
    assert h["manifest"]["price"] == {"in_per_m": 1.0, "out_per_m": 5.0} and h["manifest"]["class"] == "fast"   # read off the gateway's map
    assert fake.models["haiku"]["litellm_params"] == {"model": f"anthropic/{HAIKU}", "api_key": "os.environ/ANTHROPIC_API_KEY"}
    assert services.seed(pg, gateway=gw, home=None)["registered"] == []          # the same selves, every boot
    d = stable.deal("llama3.2", "ollama", klass="fast")
    made = stable.register_mind(pg, "llama", d, by=ME, gw=gw.stable)
    assert made["state"] == "registered" and fake.models["llama"]["litellm_params"] == {"model": "ollama/llama3.2", "api_base": stable.OLLAMA_DEFAULT}
    assert stable.register_mind(pg, "llama", d, by=ME, gw=gw.stable)["did"] == made["did"]
    with pytest.raises(stable.StableRefused) as e:
        stable.deal(SONNET, "anthropic", key="sk-ant-secret")
    assert "a key VALUE never enters a record" in str(e.value)
    [rf] = _facts(pg, made["did"], services.REGISTERED)
    assert "sk-" not in json.dumps(rf) and rf["payload"]["secrets_with"] == []
    out = stable.retire_mind(pg, "llama", by=ME, gw=gw.stable)
    assert out["state"] == "retired" and "llama" not in fake.models
    back = stable.restore_mind(pg, "llama", by=ME, gw=gw.stable)
    assert back["state"] == "registered" and "llama" in fake.models
    assert [s["name"] for s in stable.stalls(pg)] == ["haiku", "llama"]
    assert stable.stall_words(stable.stalls(pg)[0]).startswith("haiku — anthropic claude-haiku-4-5-20251001 · fast · $1 in / $5 out per million · context 200,000 · registered · never called")


def test_a_body_thinks_through_the_gateway_with_its_own_key_and_the_meter_lands_dollars(pg, fake):
    """think: the Stable resolves the mind (the template's model → the
    haiku stall), the body's key is minted ONCE with the default lease
    (a fuel fact), the call rides that key, the meter line carries the
    dollars the answer wore, the stall, the request id; the acting mind
    calls a tool through the door in the OpenAI shape; a pinned mind that
    does not stand refuses in words, metered as a failed line."""
    gw = gateway.LiteLLMGateway()
    services.seed(pg, gateway=gw, home=None)
    did = "did:orreth:agent:" + secrets.token_hex(4)
    said = gw.think(pg, did=did, system="Answer with one word.", prompt="ping", model=HAIKU, subject="librarian")
    assert said == "pong"
    [row] = gateway.meter_rows(pg, did)
    assert (row["model"], row["stall"], row["ok"], row["note"]) == ("haiku", "haiku", True, None)
    assert row["usd"] == pytest.approx(13 * 1e-6 + 5 * 5e-6) and row["request_id"].startswith("chatcmpl-")
    [k] = [k for k, v in fake.keys.items() if v["user_id"] == did]
    assert fake.keys[k]["key_alias"].endswith(":librarian") and fake.keys[k]["max_budget"] == stable.LEASE_USD_DEFAULT
    assert fake.keys[k]["budget_duration"] == "1d" and fake.calls[-1]["key"] == k
    [ff] = _facts(pg, did, stable.FUELED)
    assert ff["payload"]["first"] is True and ff["payload"]["max_usd"] == 1.0 and "sk-" not in json.dumps(ff)
    gw.think(pg, did=did, system="s", prompt="again", model=HAIKU, subject="librarian")
    assert len([k for k, v in fake.keys.items() if v["user_id"] == did]) == 1          # the same key every thought
    assert stable.fuel(pg, did, gw.stable)["spend"] == pytest.approx(2 * (13e-6 + 25e-6))
    # the acting mind: the door's tools in the OpenAI shape, the call through the door
    fake.reply = 'TOOL:weather:{"latitude": 1, "longitude": 2}'

    class Door:
        def schemas(self):
            return [{"name": "weather", "description": "the weather", "input_schema": {"type": "object", "properties": {}}}]

        def call(self, name, args):
            return f"called {name} with {args}"
    reply, notes = gw.think_acting(pg, did=did, system="s", prompt="weather?", door=Door(), model=HAIKU, subject="librarian")
    assert reply == "the tool said: called weather with {'latitude': 1, 'longitude': 2}" and notes == ["used the weather tool through the door"]
    assert fake.calls[-2]["body"]["tools"][0]["function"]["name"] == "weather"
    fake.reply = "pong"
    # a pin to a mind that does not stand
    said = gw.think(pg, did=did, system="s", prompt="p", subject="librarian", pin="ghost")
    assert said == "I cannot think right now — no mind named 'ghost' stands in the Stable."
    bad = [r for r in gateway.meter_rows(pg, did) if not r["ok"]]
    assert len(bad) == 1 and bad[0]["note"].startswith("I cannot think right now") and bad[0]["usd"] == 0.0
    # the gateway dark: words, never a stack
    fake.dark = True
    said = gw.think(pg, did=did, system="s", prompt="p", model=HAIKU, subject="librarian")
    assert said.startswith("I cannot think right now — the gateway at") and "scripts/dev.sh up" in said
    fake.dark = False


def test_a_drained_lease_speaks_in_words_and_the_keeper_proposes_a_refill_the_human_cuts(pg, fake, monkeypatch):
    """The fuel clause: the lease is the gateway's budget with its window;
    spent → the gateway's 429 → the body's honest words (the ceiling, the
    renewal, the refill door), a failed meter line, the drained mark; the
    keeper's beat proposes a refill — ONE hold at the interlock under the
    keeper's DID, cancel the default, none while one waits; the human's
    yes grows the allowance at the gateway (a fuel fact, the chain
    keeper → human → kernel) and the body thinks again."""
    monkeypatch.setenv(stable.LEASE_USD_DIAL, "0.00003")
    gw = gateway.LiteLLMGateway()
    services.seed(pg, gateway=gw, home=None)
    keeper = _body("firmware-stablekeeper.v0.json", gw); keeper.join(pg)
    assert (keeper.kind, keeper.function, keeper.template["capabilities"]) == ("firmware", "minds", ["ask", "tools:minds"])
    lib = _body("librarian-resident.v0.json", gw); lib.join(pg)
    did = lib.identity.did
    assert gw.think(pg, did=did, system="s", prompt="p", model=HAIKU, subject="librarian") == "pong"   # $0.000038 spent of $0.00003: the next refuses
    said = gw.think(pg, did=did, system="s", prompt="p", model=HAIKU, subject="librarian")
    assert said.startswith("I am out of fuel — librarian's allowance of $3e-05 for this window is spent, so I cannot think until it renews or is refilled.")
    assert "It renews on its own at 2099-01-01 00:00 UTC." in said and 'A refill is one word away: "refill librarian by $1".' in said
    g = stable.fuel(pg, did, gw.stable)
    assert g["drained_at"] is not None and g["max_usd"] == 3e-05
    fake.tokens = (1, 1)                                                        # the keeper's pings stay under ITS lease
    beat = stable.keeper_beat(pg, keeper=keeper.identity.did, gateway=gw, gw=gw.stable)
    assert [c["name"] for c in beat["checked"]] == ["haiku"] and beat["checked"][0]["ok"] is True
    assert [v["key_alias"] for v in fake.keys.values() if v["user_id"] == keeper.identity.did][0].endswith(":stablekeeper")
    [p] = beat["proposed"]
    assert (p["kind"], p["name"]) == ("refill", "librarian")
    v = glass.ask_view(pg, p["held"])
    assert v["status"] == "awaiting-confirm" and v["served_by"] == "the kernel" and v["person"] == keeper.identity.did
    assert v["hold"] == {"tool": stable.REFILL_TOOL, "class": "consequential", "level": "L2"}
    assert v["text"] == "the stablekeeper proposes refilling librarian by $1 — its allowance is spent and it cannot think"
    assert stable.keeper_beat(pg, keeper=keeper.identity.did, gateway=gw, gw=gw.stable)["proposed"] == []   # one waits
    dispatch.confirm_ask(pg, p["held"], approve=False, person=ME)                 # cancel: nothing ran
    assert stable.fuel(pg, did, gw.stable)["max_usd"] == 3e-05
    [p2] = stable.keeper_beat(pg, keeper=keeper.identity.did, gateway=gw, gw=gw.stable)["proposed"]
    out = dispatch.confirm_ask(pg, p2["held"], approve=True, person=ME)
    assert out["level"] == "L2"
    assert glass.ask_view(pg, p2["held"])["reply"].startswith("Done, on your word: librarian refilled by $1 — its allowance is now $1.00003")
    g = stable.fuel(pg, did, gw.stable)
    assert g["max_usd"] == pytest.approx(1.00003) and g["drained_at"] is None and g["refills"] == 1
    ff = _facts(pg, did, stable.FUELED)
    assert ff[-1]["payload"]["added_usd"] == 1.0 and ff[-1]["authority_chain"] == [keeper.identity.did, ME, "the kernel"]
    assert ff[-1]["marker"]["kind"] == "action"
    assert gw.think(pg, did=did, system="s", prompt="p", model=HAIKU, subject="librarian") == "pong"
    # the monitor's farm metrics
    snap = monitor.snapshot(pg, rails=False)
    assert snap["values"]["minds_standing"] == 1 and snap["values"]["bodies_drained"] == 0 and snap["values"]["usd_today"] > 0
    assert snap["values"]["route_failures_1h"] >= 1 and snap["stable"]["minds"][0]["name"] == "haiku"
    monitor.add_watch(pg, "spend-ceiling", "usd_today", ">", 5.0, by=ME)     # a watch over the farm
    assert [w["red"] for w in monitor.snapshot(pg, rails=False)["watches"]] == [False]


def test_the_market_eyes_drift_and_eol_and_the_keeper_proposes_never_acts(pg, fake):
    """Drift: the catalog's price moved under the pin → the stall is
    UNHEALTHY with what moved and the keeper proposes a RE-PIN (held);
    the human's yes versions the stall and rewrites the gateway's entry.
    EOL: an expiry inside the horizon → a proposal to retire naming the
    swap (same class, fits, nearest price). Routing honors an
    assignment, and an arm PINS."""
    gw = gateway.LiteLLMGateway()
    services.seed(pg, gateway=gw, home=None)
    keeper = _body("firmware-stablekeeper.v0.json", gw); keeper.join(pg)
    llama_route = "openrouter/meta-llama/llama-3.3-70b-instruct"
    d = stable.deal("meta-llama/llama-3.3-70b-instruct", "openrouter", klass="fast", price={"in_per_m": 0.1, "out_per_m": 0.3}, context=128000)
    stable.register_mind(pg, "llama", d, by=ME, gw=gw.stable)
    d2 = stable.deal(SONNET, "anthropic", klass="standard", price={"in_per_m": 3.0, "out_per_m": 15.0}, context=200000)
    stable.register_mind(pg, "sonnet", d2, by=ME, gw=gw.stable)
    catalog = {"meta-llama/llama-3.3-70b-instruct": {"price": {"in_per_m": 0.2, "out_per_m": 0.3}, "context": 128000, "expires": None}}
    beat = stable.keeper_beat(pg, keeper=keeper.identity.did, gateway=gw, gw=gw.stable, catalog=catalog)
    assert services.get(pg, "llama")["state"] == "unhealthy"
    assert services.get(pg, "llama")["last_health"]["detail"] == "the deal moved under the pin: the price in moved: $0.1 → $0.2 per million"
    [p] = [p for p in beat["proposed"] if p["kind"] == "repin"]
    v = glass.ask_view(pg, p["held"])
    assert v["text"] == "the stablekeeper proposes re-pinning the llama mind — the price in moved: $0.1 → $0.2 per million"
    assert v["hold"]["tool"] == stable.REPIN_TOOL and services.get(pg, "llama")["version"] == 1
    dispatch.confirm_ask(pg, p["held"], approve=True, person=ME)
    ll = services.get(pg, "llama")
    assert ll["version"] == 2 and ll["manifest"]["price"]["in_per_m"] == 0.2 and fake.models["llama"]["litellm_params"]["model"] == llama_route
    assert glass.ask_view(pg, p["held"])["reply"].startswith("Done, on your word: the llama mind is re-pinned to its new deal (version 2)")
    # EOL inside the horizon → retire proposed with the swap named
    now = datetime(2026, 9, 24, tzinfo=timezone.utc)
    catalog2 = {"meta-llama/llama-3.3-70b-instruct": {"price": {"in_per_m": 0.2, "out_per_m": 0.3}, "context": 128000, "expires": "2026-10-10"}}
    beat = stable.keeper_beat(pg, keeper=keeper.identity.did, gateway=gw, gw=gw.stable, catalog=catalog2, now=now)
    [p] = [p for p in beat["proposed"] if p["kind"] == "retire"]
    v = glass.ask_view(pg, p["held"])
    assert v["text"] == ("the stablekeeper proposes retiring the llama mind — it expires in 16 days (2026-10-10); "
                         "the swap: the haiku mind (same class, fits the deal, nearest price ($1 vs $0.2 per million in))")
    assert services.get(pg, "llama")["state"] != "retired"                      # proposed, never acted
    dispatch.confirm_ask(pg, p["held"], approve=True, person=ME)
    assert services.get(pg, "llama")["state"] == "retired" and "llama" not in fake.models
    # routing: an assignment for the class, an arm's pin outranks it
    stable.assign(pg, "librarian", "fast", "sonnet", by=ME)
    assert stable.resolve_for(pg, subject="librarian", model=HAIKU)["stall"] == "sonnet"
    assert stable.resolve_for(pg, subject="echo", model=HAIKU)["stall"] == "haiku"
    assert stable.resolve_for(pg, subject="librarian", model=HAIKU, pin="haiku")["stall"] == "haiku"
    [af] = _facts(pg, services.get(pg, "sonnet")["did"], stable.ASSIGNED)
    assert af["payload"]["stall"] == "sonnet"
    assert [s["name"] for s in stable.search(pg, "anthropic", klass="standard")] == ["sonnet"]
    assert [s["name"] for s in stable.search(pg, max_in_per_m=1.0)] == ["haiku", "llama"]
    assert stable.reconcile(pg, gw.stable)["words"].startswith("the meter and the gateway agree on ")


def test_the_harness_runs_model_arms_and_reads_the_stables_world_checks(pg, fake):
    """ab: the same golden cases against two stalls, each run pinned to
    its arm, the verdict a proposal in words; checks: every mind answers
    · the gateway answers and holds every mind · the meter and the
    gateway agree · a model change is announced (a confessed degrade
    passes, a silent swap is a wound)."""
    gw = gateway.LiteLLMGateway()
    services.seed(pg, gateway=gw, home=None)
    stable.register_mind(pg, "sonnet", stable.deal(SONNET, "anthropic", klass="standard", price={"in_per_m": 3, "out_per_m": 15}), by=ME, gw=gw.stable)
    lib = _body("librarian-resident.v0.json", gw); lib.join(pg)
    cases = [{"ask": "say pong", "expect": ["pong"]}, {"ask": "say ping", "expect": ["ping"]}]
    out = harness.ab(pg, lib, ["haiku", "sonnet"], cases=cases)
    assert out["arms"]["haiku"]["passed"] == 1 and out["arms"]["sonnet"]["passed"] == 1 and out["best"] == "haiku"
    assert out["words"] == 'librarian over 2 arms — haiku: 1 passed, 1 failed · sonnet: 1 passed, 1 failed; haiku did best — say "assign librarian to haiku" to make it so'
    assert lib.template["mind"] == {"model": HAIKU}                                # restored after the run
    rows = gateway.meter_rows(pg, lib.identity.did)
    assert sorted({r["stall"] for r in rows if r["ok"]}) == ["haiku", "sonnet"]   # each arm rode its own mind
    cur = pg.cursor(); cur.execute("SELECT arm, passed FROM spine_harness_runs WHERE scope = %s ORDER BY ran_at", (ev.scope(),))
    assert cur.fetchall() == [("haiku", 1), ("sonnet", 1)]
    with pytest.raises(ValueError):
        harness.run(pg, lib, cases=cases, arm="ghost")
    names = [c["name"] for c in harness.checks(pg)]
    assert names[-4:] == ["every mind answers", "the gateway answers and holds every mind", "the meter and the gateway agree", "a model change is announced"]
    assert harness.minds_answer(pg)["unprobed"] == ["haiku", "sonnet"] and harness.minds_answer(pg)["ok"] is False
    services.check_all(pg, kind="mind", gateway=gw, by=ME)
    assert harness.minds_answer(pg) == {"name": "every mind answers", "ok": True, "detail": "2 of 2 answered", "silent": [], "unprobed": []}
    assert harness.gateway_holds(pg)["ok"] is True
    saved = fake.models.pop("sonnet")
    assert harness.gateway_holds(pg)["missing"] == ["sonnet"] and harness.gateway_holds(pg)["ok"] is False
    fake.models["sonnet"] = saved
    assert harness.meter_agrees(pg)["ok"] is True
    assert harness.changes_announced(pg)["ok"] is True
    stable.retire_mind(pg, "haiku", by=ME, gw=gw.stable)                          # the template's model gone: the cheapest stands in, confessed
    gw.think(pg, did=lib.identity.did, system="s", prompt="p", model=HAIKU, subject="librarian")
    last = gateway.meter_rows(pg, lib.identity.did)[-1]
    assert last["stall"] == "sonnet" and last["note"] == "the cheapest standing mind — none named claude-haiku-4-5-20251001"
    assert harness.changes_announced(pg)["ok"] is True and harness.changes_announced(pg)["detail"].startswith("1 confessed swap")


def test_the_keepers_tool_holds_what_is_consequential_and_names_the_act(pg, fake, monkeypatch):
    """"stablekeeper, add the mind ollama llama3.2 as llama" → the `minds`
    tool's register is CONSEQUENTIAL — held; the interlock NAMES the act
    (W30: "Adding the llama mind (ollama llama3.2) is consequential …",
    never "The minds act"); the human's yes registers it into the Stable
    and the gateway; "what minds are here?" runs at once from the
    registry (W31); a bare "stablekeeper" opens the keeper and its
    question keeps the next bare words (W29); a server names itself (W28)."""
    services.HOME = None
    gw = gateway.LiteLLMGateway()
    services.seed(pg, gateway=gw, home=None)
    act = gateway.FakeActingGateway(script=[("tool", "minds", {"action": "register", "name": "llama", "provider": "ollama", "model": "llama3.2", "klass": "fast"}),
                                            ("text", "{result}")])
    keeper = _body("firmware-stablekeeper.v0.json", act); keeper.join(pg)
    lib = _body("librarian-resident.v0.json", gateway.FakeGateway()); lib.join(pg)
    ses = glass.open_session(pg, ME)
    [a1] = dispatch.submit_ask(pg, "stablekeeper, add the mind ollama llama3.2 as llama", person=ME, to=["stablekeeper"], session=ses)
    _serve(pg, keeper, a1)
    v = glass.ask_view(pg, a1)
    assert v["status"] == "awaiting-confirm" and v["hold"] == {"tool": "minds", "class": "consequential", "level": "L2"}
    assert v["reply"] == ("Are you sure? Adding the llama mind (ollama llama3.2) is consequential — it is written into the gateway "
                          "and recorded; you can retire it later. Cancel is the default; a deliberate click confirms.")
    assert services.get(pg, "llama") is None
    keeper._serve_conn = pg
    with pg.transaction():
        keeper._confirm_ask(pg.cursor(), a1, True, [ME], proof="L2", by=ME)
    ll = services.get(pg, "llama")
    assert ll is not None and ll["kind"] == "mind" and fake.models["llama"]["litellm_params"]["model"] == "ollama/llama3.2"
    assert glass.ask_view(pg, a1)["reply"].startswith("Done, on your word: the llama mind stands in the Stable — llama — ollama llama3.2 · fast · $0 in / $0 out per million")
    # the routine acts run at once: list (W31 — from the registry), fuel, spend
    words = tools._minds_tool({"action": "list", "_by": keeper.identity.did}, pg)
    assert words.startswith("2 minds: haiku — anthropic") and "llama — ollama llama3.2" in words and "no assignments" in words
    assert tools._minds_tool({"action": "fuel", "subject": "librarian"}, pg).startswith("librarian has no lease yet")
    assert tools._minds_tool({"action": "spend"}, pg).startswith("the meter is empty") or "$" in tools._minds_tool({"action": "spend"}, pg)
    # W30 for the toolkeeper's tool too
    assert tools.interlock_words_for("services", {"action": "register", "name": "clock", "locator": "python clock.py"}) == \
        "Are you sure? Registering the clock MCP server at python clock.py is consequential — it is recorded, and you can rest it later. Cancel is the default; a deliberate click confirms."
    assert tools.interlock_words_for("seal-record", {}) == resident.interlock_words("seal-record")
    # W28: a server names itself
    assert mcp.server_name({"name": "orreth-clock"}) == "clock" and mcp.server_name({}, "/x/weather-server.py") == "server"
    # W29: a keeper's question keeps the next bare words; a bare keeper name opens the keeper
    assert glass.address_to(pg, "stablekeeper", None, ses) == ["stablekeeper"]
    assert glass.address_to(pg, "what is the time?", None, ses) is None
    [a2] = dispatch.submit_ask(pg, "stablekeeper, which mind?", person=ME, to=["stablekeeper"], session=ses)
    with pg.transaction():
        pg.cursor().execute("UPDATE spine_asks SET status = 'replied', reply = 'Which class of work — fast, standard or deep?', "
                            "served_by = %s, replied_at = clock_timestamp() WHERE ask_id = %s", (keeper.identity.did, a2))
    assert glass.address_to(pg, "fast, please", None, ses) == ["stablekeeper"]
    assert glass.address_to(pg, "librarian, the weather?", None, ses) == ["librarian"]   # a name at the head still wins
    with pg.transaction():
        pg.cursor().execute("UPDATE spine_asks SET reply = 'Done — llama serves fast work.' WHERE ask_id = %s", (a2,))
    assert glass.address_to(pg, "thanks", None, ses) is None                        # no question stands: the fan-out


@pytest.mark.skipif(not __import__("tests.test_mind", fromlist=["_rails_up"])._rails_up(), reason="the rails are not up")
def test_the_stables_doors_hold_and_the_shelf_shows_the_deal(rig, fake):
    """The glass doors: GET /minds (the stalls with their words, the
    assignments, the gateway's readiness); POST /minds and /minds/assign
    hold at the interlock (202, the kernel's act); GET /minds/search;
    /harness/ab refuses one arm; /monitor carries the farm's values."""
    from tests.test_glass import _get, _post
    import urllib.error
    st, out = _post(rig.port, "/minds", {"name": "sonnet", "provider": "anthropic", "model": SONNET, "klass": "standard",
                                          "price": {"in_per_m": 3, "out_per_m": 15}, "person": ME})
    assert st == 202 and out["level"] == "L2" and out["class"] == "consequential"
    v = json.loads(_get(rig.port, "/ask/" + out["held"])[1])
    assert v["status"] == "awaiting-confirm" and v["text"].startswith("Are you sure? Adding the sonnet mind (anthropic claude-sonnet-5) is consequential")
    st, out = _post(rig.port, "/minds/assign", {"subject": "librarian", "klass": "standard", "stall": "haiku", "person": ME})
    assert st == 202
    st, body = _get(rig.port, "/minds")
    d = json.loads(body)
    assert st == 200 and "gateway" in d and isinstance(d["minds"], list) and isinstance(d["assignments"], list)
    st, body = _get(rig.port, "/minds/search?klass=deep")
    assert st == 200 and json.loads(body)["minds"] == []
    with pytest.raises(urllib.error.HTTPError) as e:
        _post(rig.port, "/harness/ab", {"template": "librarian", "arms": ["haiku"]})
    assert e.value.code == 400
    st, body = _get(rig.port, "/monitor")
    vals = json.loads(body)["values"]
    assert {"minds_standing", "usd_today", "route_failures_1h", "meter_rate_10m", "bodies_drained"} <= set(vals)
