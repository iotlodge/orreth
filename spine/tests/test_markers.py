# PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch markers sp1 · 2026-09-19
"""Markers (canon 0006): an open, governed vocabulary of WHY. The write
path mints the structural kinds with the fact; any body marks what it
executes through the door; the interest law asks interested bodies to
act, the marker as parent; the lineage answers from either end."""
import json
import secrets
import urllib.request
from pathlib import Path

import pytest

from orreth_spine import dispatch, envelope as ev, gateway, glass, harness, markers, resident, scheduler, tools

from tests.test_mind import _rails_up  # noqa: E402

SPINE = Path(__file__).resolve().parents[1]
POLICY = SPINE / "policy" / "covenant-policy.v1.json"
ME = "did:orreth:person:test"
rails = pytest.mark.skipif(not _rails_up(), reason="the rails are not up")


def _body(template, gw=None):
    r = resident.Resident(SPINE / "templates" / template, gateway=gw)
    r.load_policy(POLICY)
    return r


def _events_for(pg, ref):
    cur = pg.cursor()
    cur.execute("SELECT body FROM spine_outbox WHERE convert_from(body, 'UTF8') LIKE %s", (f"%{ref}%",))
    return [ev.decode(bytes(b)) for (b,) in cur.fetchall()]


def test_the_registry_and_the_write_paths_lineage(pg, monkeypatch):
    monkeypatch.setenv("SPINE_SCOPE", "u:law-" + secrets.token_hex(3))
    seeded = {k["kind"]: k["group"] for k in markers.kinds(pg)}
    assert {"objective", "intention", "thought", "action", "observation"} <= set(seeded)
    assert seeded["improvement"] == "quality"
    with pytest.raises(markers.UnknownKind, match="declare it first"):
        markers.mint(pg, "cost-anomaly", "x", ME)                      # declared before use
    markers.declare(pg, "cost-anomaly", "cost", "spend above the plan", ME)
    assert markers.mint(pg, "cost-anomaly", "x", ME)["kind"] == "cost-anomaly"
    ask = dispatch.submit_ask(pg, "a human's ask", person=ME)          # an OBJECTIVE, a root
    mk = glass.ask_view(pg, ask)
    cur = pg.cursor(); cur.execute("SELECT marker FROM spine_asks WHERE ask_id = %s", (ask,))
    obj = markers.get(pg, cur.fetchone()[0])
    assert obj["kind"] == "objective" and obj["parent"] is None and obj["ref"] == ask and obj["by"] == ME
    assert any(e.get("marker", {}).get("id") == obj["id"] for e in _events_for(pg, ask))  # on the rail
    lib = _body("librarian-resident.v0.json", gateway.FakeGateway(reply="PELICAN, the librarian"))
    sid = scheduler.add(pg, "librarian", "human", "say the time", 3600, ME)   # an INTENTION
    cur.execute("SELECT marker FROM spine_schedules WHERE schedule_id = %s", (sid,))
    intention = markers.get(pg, cur.fetchone()[0])
    assert intention["kind"] == "intention" and intention["ref"] == sid
    ksid = scheduler.declared(pg, "librarian", "kernel", "run the harness against my golden set", 1800, "the kernel")
    pg.cursor().execute("UPDATE spine_schedules SET next_at = now() WHERE runner = 'librarian'")
    occurred = {o["kind"]: o for o in scheduler.tick(pg, {"librarian": lib})}
    cur.execute("SELECT marker FROM spine_asks WHERE ask_id = %s", (occurred["human"]["ref"],))
    occ = markers.get(pg, cur.fetchone()[0])
    assert occ["kind"] == "objective" and occ["parent"] == intention["id"]     # an occurrence under it
    cur.execute("SELECT marker FROM spine_schedules WHERE schedule_id = %s", (ksid,))
    kint = cur.fetchone()[0]
    kids = markers.tree(pg, kint)
    assert kids[0]["kind"] == "intention" and any(m["kind"] == "observation" and m["ref"] == occurred["kernel"]["ref"]
                                                    for m in kids)              # the harness run, under it
    assert [m["kind"] for m in markers.ancestry(pg, occ["id"])] == ["objective", "intention"]


def test_mk1_an_improvement_marked_by_the_librarian_makes_the_critic_act(pg, monkeypatch):
    """MK-1: the librarian, serving a human's ask, marks an improvement;
    the critic — interested — is asked to act, the marker as parent; the
    lineage runs from the human's objective to the critic's thought."""
    monkeypatch.setenv("SPINE_SCOPE", "u:law-" + secrets.token_hex(3))
    critic = _body("firmware-critic.v0.json"); critic.join(pg)
    assert markers.interested(pg, "improvement") == ["critic"]
    gw = gateway.FakeActingGateway(script=[
        ("tool", "mark", {"kind": "improvement", "note": "lime beats cement for the binder"}),
        ("text", "noted, and marked: {result}")])
    lib = _body("librarian-resident.v0.json", gw); lib.join(pg); lib._serve_conn = pg
    ses = glass.open_session(pg, ME)
    ask = dispatch.submit_ask(pg, "what binds hempcrete?", person=ME, session=ses)
    with pg.transaction():
        lib._serve_ask(pg.cursor(), ask, [ME])
    view = glass.ask_view(pg, ask)
    assert view["status"] == "replied" and "marked" in view["reply"] and "1 interested body" in view["reply"]
    cur = pg.cursor(); cur.execute("SELECT marker FROM spine_asks WHERE ask_id = %s", (ask,))
    objective = cur.fetchone()[0]
    under = markers.tree(pg, objective)
    imp = [m for m in under if m["kind"] == "improvement"]
    assert len(imp) == 1 and imp[0]["parent"] == objective and imp[0]["by"] == lib.identity.did
    assert "lime beats cement" in imp[0]["note"]
    assert any(e["type"] == markers.MARKER_SET and e["marker"]["id"] == imp[0]["id"]
               for e in _events_for(pg, ask))                                      # a fact on the rail
    cur.execute("SELECT ask_id, text, marker FROM spine_asks WHERE target = 'critic' AND person = %s",
                (lib.identity.did,))
    [(cask, ctext, cmarker)] = cur.fetchall()                                       # the critic was asked
    assert "improvement" in ctext and "lime beats cement" in ctext
    assert [m["kind"] for m in markers.ancestry(pg, cmarker)] == ["thought", "improvement", "objective"]
    journeys = [e for e in _events_for(pg, ask) if e["type"] == resident.JOURNEY]
    assert journeys and all(e["marker"]["id"] == objective for e in journeys)      # every hop says why
    door = tools.ToolDoor(pg, did=lib.identity.did, capabilities=lib.template["capabilities"],
                          name="librarian", marker=objective)
    with pytest.raises(tools.ToolRefused, match="declare it first"):
        door.call("mark", {"kind": "vibe", "note": "undeclared"})                  # the teaching


@rails
def test_the_marker_doors_over_http(pg, rig):
    port = rig.port
    def get(path):
        with urllib.request.urlopen(f"http://127.0.0.1:{port}{path}", timeout=10) as r:
            return json.loads(r.read())
    def post(path, obj):
        req = urllib.request.Request(f"http://127.0.0.1:{port}{path}", data=json.dumps(obj).encode(),
                                     headers={"content-type": "application/json"}, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=10) as r:
                return r.status, json.loads(r.read())
        except urllib.error.HTTPError as e:
            return e.code, json.loads(e.read())
    assert {k["kind"] for k in get("/markers/kinds")["kinds"]} >= {"objective", "improvement"}
    _s, filed = post("/ask", {"text": "mark me", "to": ["echo"]})
    aid = filed["ids"][0]
    s, body = post("/mark", {"kind": "vibe", "ref": aid})
    assert s == 400 and "declare it first" in body["error"]
    s, _ = post("/markers/kinds", {"kind": "vibe", "group": "quality", "description": "a felt thing"})
    assert s == 201
    s, body = post("/mark", {"kind": "improvement", "ref": aid, "note": "from the glass"})
    assert s == 201 and [a["body"] for a in body["asked"]] == ["critic"]          # the interest law
    stream = get("/markers?kind=improvement")["markers"]
    assert stream and stream[0]["ref"] == aid and stream[0]["group"] == "quality"
    anc = get(f"/markers?from={body['marker']['id']}")["ancestry"]
    assert [m["kind"] for m in anc] == ["improvement", "objective"]
