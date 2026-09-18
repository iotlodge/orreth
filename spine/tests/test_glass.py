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


def test_an_ask_wears_its_time_window(pg, monkeypatch):
    """P6 — scope set where intent forms: the window the human typed
    ("between last Monday and today") rides the ask onto the ground and
    into its committed event, so the scope is real, never eye candy."""
    monkeypatch.setenv("SPINE_SCOPE", "u:law-" + secrets.token_hex(3))
    win = {"from": "2026-09-14T00:00:00+00:00", "to": "2026-09-17T18:00:00+00:00"}
    ask_id = dispatch.submit_ask(pg, "what happened between last Monday and today?",
                                 window=win)
    assert glass.ask_view(pg, ask_id)["window"] == win
    cur = pg.cursor()
    cur.execute("SELECT body FROM spine_outbox WHERE convert_from(body, 'UTF8')"
                " LIKE %s", (f"%{ask_id}%",))
    events = [ev.decode(bytes(b)) for (b,) in cur.fetchall()]
    assert any(e["payload"].get("window") == win for e in events)
    plain = dispatch.submit_ask(pg, "and with no time words at all")
    assert glass.ask_view(pg, plain)["window"] is None


def test_sessions_roll_list_and_load_and_never_spill(pg, monkeypatch):
    """P20 / MEM-7's ground half: a session is the human's worldline —
    roll a fresh one, ask in it, roll again, ask again; the list is newest
    first with counts and last words; loading one returns exactly its
    asks in order; an ask wears its session; a stranger world sees none."""
    monkeypatch.setenv("SPINE_SCOPE", "u:law-" + secrets.token_hex(3))
    me = "did:orreth:person:test"
    first = glass.open_session(pg, me, title="the first topic")
    a1 = dispatch.submit_ask(pg, "first words", session=first)
    a2 = dispatch.submit_ask(pg, "second words", session=first)
    second = glass.open_session(pg, me)
    b1 = dispatch.submit_ask(pg, "a new topic entirely", session=second)
    listed = glass.sessions_view(pg, me)
    assert [x["session_id"] for x in listed] == [second, first]   # newest first
    assert listed[1]["asks"] == 2 and listed[1]["last_words"] == "second words"
    assert listed[0]["asks"] == 1 and listed[1]["title"] == "the first topic"
    loaded = glass.session_view(pg, first)
    assert [x["ask_id"] for x in loaded["asks"]] == [a1, a2]     # in order
    assert [x["ask_id"] for x in glass.session_view(pg, second)["asks"]] == [b1]
    assert glass.ask_view(pg, a1)["session"] == first
    monkeypatch.setenv("SPINE_SCOPE", "u:stranger-" + secrets.token_hex(3))
    assert glass.sessions_view(pg, me) == [] and glass.session_view(pg, first) is None


def test_a_resident_reads_only_this_sessions_results(pg, monkeypatch):
    """MEM-7's mind half: a resident selected into a session recalls THAT
    session's results — by any resident, labeled — and never another
    session's; nothing spills between topics."""
    monkeypatch.setenv("SPINE_SCOPE", "u:law-" + secrets.token_hex(3))
    SPINE = glass.Path(__file__).resolve().parents[1]
    tok_a, tok_b = secrets.token_hex(3), secrets.token_hex(3)
    me = "did:orreth:person:test"
    echo = resident.Resident(SPINE / "templates" / "echo-resident.v0.json")
    echo.load_policy(SPINE / "policy" / "covenant-policy.v1.json"); echo.join(pg)
    sa, sb = glass.open_session(pg, me), glass.open_session(pg, me)
    cur = pg.cursor()
    for ses, tok in ((sa, tok_a), (sb, tok_b)):            # a reply landed by
        aid = dispatch.submit_ask(pg, f"about {tok}", session=ses)  # the echo
        cur.execute("UPDATE spine_asks SET status = 'replied', served_by = %s,"
                    " reply = %s, replied_at = now() WHERE ask_id = %s",
                    (echo.identity.did, f"the echo said marker {tok}", aid))
    gw = gateway.FakeGateway(reply="noted")
    lib = resident.Resident(SPINE / "templates" / "librarian-resident.v0.json",
                            gateway=gw)
    lib.load_policy(SPINE / "policy" / "covenant-policy.v1.json")
    lib._serve_conn = pg
    lib._current_ask = dispatch.submit_ask(pg, "what was said here?", session=sb)
    out = lib._graph.invoke({"text": "what was said here?", "reply": "",
                             "steps": [], "notes": [], "hold": None})
    prompt = gw.calls[0]["prompt"]
    assert f"marker {tok_b}" in prompt and "echo replied" in prompt   # this session,
    assert f"marker {tok_a}" not in prompt                            # labeled — never
    assert any("recalled" in st for st in out["steps"])               # the other


@rails
def test_the_session_doors_answer_over_http_as_the_glass_asks(pg, rig):
    """The doors as a browser calls them — the person URL-encoded in the
    query (found by the Playwright: the door matched no one and every
    session read 'none yet'): roll, list, load, and an ask filed in the
    session, all over HTTP alone."""
    from urllib.parse import quote
    me = "did:orreth:person:" + secrets.token_hex(3)
    s, rolled = _post(rig.port, "/sessions", {"person": me, "title": "over http"})
    assert s == 201 and rolled["session_id"].startswith("ses_")
    _s, filed = _post(rig.port, "/ask", {"text": "a word in my session",
                                         "to": ["echo"], "session": rolled["session_id"]})
    s, body = _get(rig.port, "/sessions?person=" + quote(me, safe=""))
    listed = json.loads(body)["sessions"]
    assert s == 200 and [x["session_id"] for x in listed] == [rolled["session_id"]]
    assert listed[0]["asks"] == 1 and listed[0]["last_words"] == "a word in my session"
    s, body = _get(rig.port, "/session/" + rolled["session_id"])
    assert s == 200 and [a["ask_id"] for a in json.loads(body)["asks"]] == filed["ids"]
    s, body = _get(rig.port, "/sessions?person=" + quote("did:orreth:person:nobody", safe=""))
    assert s == 200 and json.loads(body)["sessions"] == []
