# PROVENANCE: Claude Fable 5 (claude-fable-5) — rearch P3 sp2, the band and the fan-out · 2026-09-17
"""sp2's laws (canon 0001 P13 · P14): the Objectives band's door lists
everything running and run; a fan-out sends ONE request to EACH named
resident — each answers through its own role lens, results distinct,
served by different selves; a targeted ask reaches ONLY its target; the
crew door names who lives here."""
import json
import os
import secrets
import time
import urllib.request

import pytest

from orreth_spine import gateway, glass

from tests.test_mind import _rails_up  # noqa: E402

rails = pytest.mark.skipif(
    not (os.environ.get("SPINE_REQUIRE_KAFKA") or _rails_up()),
    reason="the rails are not up — start spine/compose.yaml")


def _get(port, path):
    with urllib.request.urlopen(f"http://127.0.0.1:{port}{path}",
                                timeout=10) as r:
        return json.loads(r.read())


def _post(port, path, obj):
    req = urllib.request.Request(
        f"http://127.0.0.1:{port}{path}", data=json.dumps(obj).encode(),
        headers={"content-type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read())


def _wait_replied(port, ids, deadline_s=60.0):
    end = time.monotonic() + deadline_s
    views = {}
    while time.monotonic() < end and len(views) < len(ids):
        for i in ids:
            if i in views:
                continue
            v = _get(port, f"/ask/{i}")
            if v["status"] in ("replied", "cancelled"):
                views[i] = v
        time.sleep(0.5)
    assert len(views) == len(ids), f"only {len(views)}/{len(ids)} replied"
    return views


@rails
def test_fanout_two_lenses_two_selves_and_the_band_sees_all(pg, rig):
    from tests.test_resident import _purge_queue
    _purge_queue()
    tok = secrets.token_hex(4)
    reply = f"The librarian's own lens on marker {tok}."
    rig.resident.gateway = gateway.FakeGateway(reply=reply)
    if True:
        crew = _get(rig.port, "/residents")["residents"]
        names = {r["name"] for r in crew}
        assert {"librarian", "echo"} <= names       # the crew door names them
        text = f"Both of you: consider marker {tok}."
        filed = _post(rig.port, "/ask",
                      {"text": text, "to": ["librarian", "echo"]})
        ids = filed["ids"]
        assert len(ids) == 2
        views = _wait_replied(rig.port, ids)
        replies = {v["reply"] for v in views.values()}
        servers = {v["served_by"] for v in views.values()}
        assert len(replies) == 2 and len(servers) == 2   # two lenses, two selves
        assert reply in replies                          # the librarian's lens
        assert any(text in r for r in replies)           # the echo's full-reply lens
        # the band's door: both rows present, replied, targets named
        rows = {a["ask_id"]: a for a in _get(rig.port, "/asks")["asks"]}
        for i in ids:
            assert rows[i]["status"] == "replied"
            assert rows[i]["target"] in ("librarian", "echo")
            assert rows[i]["fanout"]                     # each wears the group
        assert len({rows[i]["fanout"] for i in ids}) == 1   # one shared fanout


@rails
def test_a_targeted_ask_reaches_only_its_target(pg, rig):
    from tests.test_resident import _purge_queue
    _purge_queue()
    tok = secrets.token_hex(4)
    rig.resident.gateway = gateway.FakeGateway(
        reply=f"the librarian would have said {tok}")
    if True:
        text = f"Echo only, marker {tok}."
        filed = _post(rig.port, "/ask", {"text": text, "to": ["echo"]})
        views = _wait_replied(rig.port, filed["ids"])
        v = list(views.values())[0]
        assert text in v["reply"]                        # the echo's lens
        echo_did = next(r["did"] for r in
                        _get(rig.port, "/residents")["residents"]
                        if r["name"] == "echo")
        assert v["served_by"] == echo_did                # ONLY its target
