# PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P4 sp3, the Crew pull · 2026-09-18
"""The first workspace (0001 P19 · 0004 block 9): the Crew pull — one
card per body, both sides — and its agent: the ONE workspace-firmware
body wearing the crew binding (the binding schema's v0)."""
import json
import secrets
import urllib.request
from pathlib import Path

import pytest

from orreth_spine import dispatch, gateway, glass, resident

from tests.test_mind import _rails_up  # noqa: E402

SPINE = Path(__file__).resolve().parents[1]
POLICY = SPINE / "policy" / "covenant-policy.v1.json"
rails = pytest.mark.skipif(not _rails_up(), reason="the rails are not up")


def _body(template, gw=None, binding=None):
    r = resident.Resident(SPINE / "templates" / template, gateway=gw, binding=binding)
    r.load_policy(POLICY)
    return r


def test_the_crew_door_shows_every_body_and_both_sides(pg, monkeypatch):
    """One card per body in this world: kind, self, lives, the policy
    worn, what it DECLARED at its join; side A (asks served), side B
    (the kernel-required duties, immutable; human/role none yet)."""
    monkeypatch.setenv("SPINE_SCOPE", "u:law-" + secrets.token_hex(3))
    echo = _body("echo-resident.v0.json"); echo.join(pg)
    _body("librarian-resident.v0.json").join(pg)
    aid = dispatch.submit_ask(pg, "served once")
    pg.cursor().execute("UPDATE spine_asks SET status = 'replied', served_by = %s,"
                        " reply = 'x', replied_at = now() WHERE ask_id = %s",
                        (echo.identity.did, aid))
    cards = {c["name"]: c for c in glass.crew_view(pg)}
    assert set(cards) == {"echo", "librarian"}
    lib = cards["librarian"]
    assert lib["kind"] == "resident" and lib["policy_version"] == "1.1.0"
    assert "tools:weather" in lib["capabilities"]            # declared at the join
    assert cards["echo"]["side_a"]["asks_served"] == 1 and lib["side_a"]["asks_served"] == 0
    duties = lib["side_b"]
    assert duties["kernel"] and all(d["editable"] is False for d in duties["kernel"])
    assert duties["human"] == [] and duties["role"] == []   # the scheduler's half


def test_the_crew_binding_births_the_workspace_agent(pg, monkeypatch):
    """ONE workspace body, a binding per pull: born with the crew binding
    it is named 'crew', kind firmware, function workspace:crew — and its
    recall packs the crew's cards, so it answers from the workspace's own
    facts."""
    monkeypatch.setenv("SPINE_SCOPE", "u:law-" + secrets.token_hex(3))
    _body("echo-resident.v0.json").join(pg); _body("librarian-resident.v0.json").join(pg)
    gw = gateway.FakeGateway(reply="two residents and me")
    crew = _body("workspace-firmware.v0.json", gw, binding=SPINE / "bindings" / "crew.v0.json")
    assert (crew.name, crew.kind, crew.function) == ("crew", "firmware", "workspace:crew")
    crew.join(pg); crew._serve_conn = pg
    ses = glass.open_session(pg, "did:orreth:person:test")
    [aid] = dispatch.submit_ask(pg, "who is here?", to=["crew"], session=ses)
    crew._current_ask = aid
    crew._graph.invoke({"text": "who is here?", "reply": "", "steps": [],
                        "notes": [], "hold": None, "read": []})
    prompt, system = gw.calls[0]["prompt"], gw.calls[0]["system"]
    assert "crew card — librarian: resident" in prompt and "crew card — echo: resident" in prompt
    assert "tools:weather" in prompt and "CREW workspace" in system
    assert {x["name"]: x["kind"] for x in glass.residents_view(pg)}["crew"] == "firmware"


@rails
def test_the_crew_door_answers_over_http_with_the_whole_rig(pg, rig):
    """The rig seats residents, the includes, and the crew agent; the door
    a browser calls lists them all with their kinds."""
    with urllib.request.urlopen(f"http://127.0.0.1:{rig.port}/crew", timeout=10) as r:
        cards = {c["name"]: c["kind"] for c in json.loads(r.read())["crew"]}
    assert cards == {"librarian": "resident", "echo": "resident", "planner": "firmware",
                     "critic": "firmware", "grader": "firmware", "crew": "firmware", "stablekeeper": "firmware",
                     "monitor": "firmware",
                     "mitl": "firmware",      # P6 sp3: MITL, the fourth include, is born with the rig
                     "toolkeeper": "firmware"}   # P6.5 sp2: the Tools keeper, born with the rig
