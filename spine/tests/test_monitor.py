# PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P4 sp4, Monitoring · leases · harness · 2026-09-18
"""P4 sp4: presence leases (M2) — alive while serving, dormant never
deleted; the Monitoring ground — the snapshot and the WATCHES, added
through the interlock; the A/B harness v0 (AG-6's non-scheduled half) —
a failing run is a fact on the rail."""
import json
import secrets
import urllib.request
from pathlib import Path

import pytest

from orreth_spine import (dispatch, envelope as ev, gateway, glass, harness,
                          monitor, presence, resident, tools)

from tests.test_mind import _rails_up  # noqa: E402

SPINE = Path(__file__).resolve().parents[1]
POLICY = SPINE / "policy" / "covenant-policy.v1.json"
rails = pytest.mark.skipif(not _rails_up(), reason="the rails are not up")


def _body(template, gw=None, binding=None):
    r = resident.Resident(SPINE / "templates" / template, gateway=gw, binding=binding)
    r.load_policy(POLICY)
    return r


def test_a_lease_makes_a_body_alive_and_its_lapse_makes_it_dormant(pg, monkeypatch):
    monkeypatch.setenv("SPINE_SCOPE", "u:law-" + secrets.token_hex(3))
    did = "did:orreth:agent:" + secrets.token_hex(8)
    presence.renew(pg, did, "echo", "resident", ttl_s=15)
    [b] = presence.roster(pg)
    assert b["alive"] is True and b["name"] == "echo"
    pg.cursor().execute("UPDATE spine_leases SET until = now() - interval '1 second'"
                        " WHERE did = %s", (did,))
    [b] = presence.roster(pg)                      # dormant — and still listed
    assert b["alive"] is False
    values = monitor.snapshot(pg, rails=False)["values"]
    assert {k: values[k] for k in ("asks_received", "bodies_alive", "bodies_dormant")} == {
        "asks_received": 0, "bodies_alive": 0, "bodies_dormant": 1}   # this world's
    assert {"outbox_pending", "oldest_outbox_age_s"} <= set(values)   # the ground's


def test_a_watch_holds_at_the_interlock_then_lands_and_is_judged(pg, monkeypatch):
    """The monitor agent PROPOSES a watch through the add-watch tool: the
    door holds it (consequential) until confirmed; landed, the snapshot
    judges it against the live value, green or red."""
    monkeypatch.setenv("SPINE_SCOPE", "u:law-" + secrets.token_hex(3))
    mon = _body("workspace-firmware.v0.json", binding=SPINE / "bindings" / "monitor.v0.json")
    assert "tools:add-watch" in mon.template["capabilities"]   # the seat's tool
    door = tools.ToolDoor(pg, did=mon.identity.did, capabilities=mon.template["capabilities"])
    args = {"name": "no asks left waiting", "metric": "asks_received", "op": "<=", "threshold": 0}
    with pytest.raises(tools.ConsequentialHold):
        door.call("add-watch", args)                 # holds for the human's yes
    door.call("add-watch", args, confirmed=True)     # the yes: it lands
    snap = monitor.snapshot(pg, rails=False)
    [w] = snap["watches"]
    assert w["name"] == "no asks left waiting" and w["ok"] is True and w["added_by"] == mon.identity.did
    dispatch.submit_ask(pg, "one ask, unserved")     # now a red watch
    [w] = monitor.snapshot(pg, rails=False)["watches"]
    assert w["value"] == 1 and w["ok"] is False
    with pytest.raises(ValueError):
        monitor.add_watch(pg, "bad", "no_such_metric", "<=", 1, by="x")


def test_the_harness_passes_a_sound_mind_and_fails_a_degraded_one_on_the_rail(pg, monkeypatch):
    """AG-6's non-scheduled half: golden cases against the librarian's mind;
    a sound mind passes; a degraded one fails, and the failure is a FACT in
    the outbox (orreth.harness.failed.v1) — the escalation the feed carries."""
    monkeypatch.setenv("SPINE_SCOPE", "u:law-" + secrets.token_hex(3))
    sound = _body("librarian-resident.v0.json", gateway.FakeGateway(
        reply="PELICAN — and I am the librarian, keeper of records."))
    out = harness.run(pg, sound)
    assert (out["passed"], out["failed"]) == (2, 0)
    degraded = _body("librarian-resident.v0.json", gateway.FakeGateway(reply="…"))
    out = harness.run(pg, degraded)
    assert (out["passed"], out["failed"]) == (0, 2)
    cur = pg.cursor()
    cur.execute("SELECT body FROM spine_outbox WHERE convert_from(body, 'UTF8') LIKE %s",
                (f"%{out['run_id']}%",))
    events = [ev.decode(bytes(b)) for (b,) in cur.fetchall()]
    assert any(e["type"] == harness.HARNESS_FAILED and e["payload"]["failed"] == 2
               for e in events)
    assert monitor.snapshot(pg, rails=False)["harness"]["failed"] == 2   # the last run


@rails
def test_the_monitor_door_and_the_harness_door_over_http(pg, rig):
    """The whole rig: seven bodies alive on fresh leases, the snapshot's
    every part, and a harness run on demand against the rig's librarian."""
    rig.resident.gateway = gateway.FakeGateway(reply="PELICAN, says the librarian")
    with urllib.request.urlopen(f"http://127.0.0.1:{rig.port}/monitor", timeout=15) as r:
        snap = json.loads(r.read())
    assert {"outbox", "asks", "bodies", "values", "watches", "benches", "topic_depth", "harness"} <= set(snap)
    assert snap["values"]["bodies_alive"] >= 7                    # leases renewed as they serve
    assert {b["name"] for b in snap["bodies"] if b["alive"]} >= {"librarian", "crew", "monitor"}
    req = urllib.request.Request(f"http://127.0.0.1:{rig.port}/harness/run",
                                 data=json.dumps({"template": "librarian"}).encode(),
                                 headers={"content-type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=30) as r:
        run = json.loads(r.read())
    assert run["template"] == "librarian" and run["passed"] == 2 and run["failed"] == 0
