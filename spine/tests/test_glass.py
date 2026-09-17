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

from orreth_spine import gateway, glass, tools

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
def test_the_human_path_runs_over_http_alone(pg):
    """POST an ask, read the journey, receive the full reply — nothing
    but the glass's own doors, exactly as a browser would."""
    from tests.test_resident import _purge_queue
    _purge_queue()
    tok = secrets.token_hex(4)
    reply = f"The whole answer, every word of it, marker {tok}."
    rig = glass.BridgeRig(gateway=gateway.FakeGateway(reply=reply),
                          port=0).start()
    try:
        assert rig.feed_ready.wait(20)
        s, page = _get(rig.port, "/")
        assert s == 200
        html = page.decode()
        assert 'id="chat' in html and "Escape" in html   # the chat + Esc law
        assert "Cancel (default)" in html                # the interlock's face
        s, filed = _post(rig.port, "/ask",
                         {"text": f"Say the whole answer (marker {tok})."})
        assert s == 201 and filed["id"].startswith("ask_")
        view = _wait_status(rig.port, filed["id"], ("replied",))
        assert view["reply"] == reply                    # the FULL reply
        assert view["journey"]                           # the ask wore its way
        assert any("librarian" in n for n in view["journey"])
    finally:
        rig.stop()


@rails
def test_cancel_over_http_means_the_act_never_ran(pg):
    """The interlock through the glass: the held act waits, the human's
    cancel arrives over HTTP, and the journal proves nothing ran."""
    from tests.test_resident import _purge_queue
    _purge_queue()
    tok = secrets.token_hex(4)
    gw = gateway.FakeActingGateway(
        script=[("tool", "seal-record", {"key": f"note-{tok}"}),
                ("text", "sealed: {result}")])
    rig = glass.BridgeRig(gateway=gw, port=0).start()
    try:
        assert rig.feed_ready.wait(20)
        _s, filed = _post(rig.port, "/ask",
                          {"text": f"Seal note {tok} forever."})
        view = _wait_status(rig.port, filed["id"], ("awaiting-confirm",))
        assert "Are you sure" in view["reply"]
        assert tools.journal(pg, rig.resident.identity.did) == []
        _post(rig.port, "/confirm", {"ask_id": filed["id"]})  # no approve key
        view = _wait_status(rig.port, filed["id"], ("cancelled",))
        assert "nothing was done" in view["reply"].lower()
        assert tools.journal(pg, rig.resident.identity.did) == []
    finally:
        rig.stop()
