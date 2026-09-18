# PROVENANCE: Claude Fable 5 (claude-fable-5) — rearch P3 sp1, the glass exists · 2026-09-16
"""The glass's laws (canon 0001): the human path runs over HTTP alone —
ask through the door, journey readable, the full reply in place; the
interlock renders with cancel as the default and a cancel over HTTP
means the act never ran; the page itself carries the Esc law and the
one chat. The whole rig breathes as one object and stops whole."""
import json
import os
import secrets
import time
import urllib.request

import pytest

from orreth_spine import dispatch, envelope as ev, gateway, glass, resident, tools

from tests.test_mind import _rails_up  # noqa: E402

rails = pytest.mark.skipif(
    not (os.environ.get("SPINE_REQUIRE_KAFKA") or _rails_up()),
    reason="the rails are not up — start spine/compose.yaml")


def _get(port, path):
    with urllib.request.urlopen(f"http://127.0.0.1:{port}{path}",
                                timeout=10) as r:
        return r.status, r.read()


def _post(port, path, obj):
    req = urllib.request.Request(
        f"http://127.0.0.1:{port}{path}", data=json.dumps(obj).encode(),
        headers={"content-type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        return r.status, json.loads(r.read())


def _wait_status(port, ask_id, want, deadline_s=45.0):
    end = time.monotonic() + deadline_s
    view = None
    while time.monotonic() < end:
        _s, body = _get(port, f"/ask/{ask_id}")
        view = json.loads(body)
        if view["status"] in want:
            return view
        time.sleep(0.5)
    raise AssertionError(f"{ask_id} never reached {want}; last: "
                         f"{view and view['status']}")


@rails
def test_the_human_path_runs_over_http_alone(pg, rig):
    """POST an ask, read the journey, receive the full reply — nothing
    but the glass's own doors, exactly as a browser would."""
    from tests.test_resident import _purge_queue
    _purge_queue()
    tok = secrets.token_hex(4)
    reply = f"The whole answer, every word of it, marker {tok}."
    rig.resident.gateway = gateway.FakeGateway(reply=reply)
    if True:
        s, page = _get(rig.port, "/")
        assert s == 200
        html = page.decode()
        assert 'id="chat' in html and "Escape" in html   # the chat + Esc law
        assert "Cancel (default)" in html                # the interlock's face
        s, filed = _post(rig.port, "/ask",
                         {"text": f"Say the whole answer (marker {tok}).",
                          "to": ["librarian"]})
        assert s == 201 and filed["ids"][0].startswith("ask_")
        view = _wait_status(rig.port, filed["ids"][0], ("replied",))
        assert view["reply"] == reply                    # the FULL reply
        assert view["journey"]                           # the ask wore its way
        assert any("librarian" in n for n in view["journey"])
        assert view["scope"] == ev.scope()               # P7: on which scope,
        assert view["replied_at"] and view["asked_at"]   # and when it completed


@rails
def test_cancel_over_http_means_the_act_never_ran(pg, rig):
    """The interlock through the glass: the held act waits, the human's
    cancel arrives over HTTP, and the journal proves nothing ran."""
    from tests.test_resident import _purge_queue
    _purge_queue()
    tok = secrets.token_hex(4)
    gw = gateway.FakeActingGateway(
        script=[("tool", "seal-record", {"key": f"note-{tok}"}),
                ("text", "sealed: {result}")])
    rig.resident.gateway = gw
    if True:
        _s, filed = _post(rig.port, "/ask",
                          {"text": f"Seal note {tok} forever.",
                           "to": ["librarian"]})
        ask_id = filed["ids"][0]
        view = _wait_status(rig.port, ask_id, ("awaiting-confirm",))
        assert "Are you sure" in view["reply"]
        assert tools.journal(pg, rig.resident.identity.did) == []
        _post(rig.port, "/confirm", {"ask_id": ask_id})  # no approve key
        view = _wait_status(rig.port, ask_id, ("cancelled",))
        assert "nothing was done" in view["reply"].lower()
        assert tools.journal(pg, rig.resident.identity.did) == []


def test_the_bridge_seats_the_same_selves_in_every_life(tmp_path):
    """Covenant rule 1 at the rig layer: a relit Bridge seats the SAME
    librarian and echo (seeds under `home`), never strangers wearing
    their names — found by the Playwright when a roster turned over
    and every reply bubble lost its speaker."""
    first = glass.BridgeRig(gateway=None, port=0, home=tmp_path)
    again = glass.BridgeRig(gateway=None, port=0, home=tmp_path)
    try:
        assert [r.identity.did for r in first.residents] == \
               [r.identity.did for r in again.residents]
        stranger = glass.BridgeRig(gateway=None, port=0, home=None)
        assert stranger.resident.identity.did != first.resident.identity.did
    finally:
        for rig in (first, again, stranger):
            rig._httpd.server_close()          # never started: just the socket


def test_a_world_sees_only_its_own_ground(pg, monkeypatch):
    """The isolation law at the doors (canon 0002; felt by the Playwright
    when the band and the roster showed every world's rows): an ask and
    a join made in THIS world are served by this world's doors, and to
    a stranger world they do not exist — the same face as never asked."""
    SPINE = glass.Path(__file__).resolve().parents[1]
    mine = "u:law-" + secrets.token_hex(3)       # a world of this law's own:
    monkeypatch.setenv("SPINE_SCOPE", mine)      # nothing here is ever
    r = resident.Resident(SPINE / "templates" / "echo-resident.v0.json")
    r.load_policy(SPINE / "policy" / "covenant-policy.v1.json")  # dispatched
    r.join(pg)                                   # by the session's world
    ask_id = dispatch.submit_ask(pg, "a word for my own world")
    assert ask_id in {a["ask_id"] for a in glass.asks_view(pg)}
    assert glass.ask_view(pg, ask_id)["scope"] == mine
    assert "echo" in {x["name"] for x in glass.residents_view(pg)}
    monkeypatch.setenv("SPINE_SCOPE", "u:stranger-" + mine[-6:])
    assert ask_id not in {a["ask_id"] for a in glass.asks_view(pg)}
    assert glass.ask_view(pg, ask_id) is None            # one face: no such ask
    assert "echo" not in {x["name"] for x in glass.residents_view(pg)}
