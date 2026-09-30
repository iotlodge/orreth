# PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P4 sp4, Monitoring · leases · harness · 2026-09-18
# Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P6 cure sp1 (kernel): the watch's sense (W14) · 2026-09-21
# Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch row 4, PANEL sp3: the doors timed, the reference's null pool · 2026-09-28
# Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch row 4, the honest glass sp2 (W85 · W86): the roster folded one row per name · a watch's REST · the asks left waiting and a local ask's STOP · the ground's prune · the three doors on the rig · 2026-09-29
"""P4 sp4: presence leases (M2) — alive while serving, dormant never
deleted; the Monitoring ground — the snapshot and the WATCHES, added
through the interlock; the A/B harness v0 (AG-6's non-scheduled half) —
a failing run is a fact on the rail."""
import json
import secrets
import urllib.request

from tests import seats  # P7 sp8 row 3: every door reads the person from the SEAT — the test sits first
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
    judges it against the live value — RED when the condition holds (W14:
    the watch names what it catches), green otherwise."""
    monkeypatch.setenv("SPINE_SCOPE", "u:law-" + secrets.token_hex(3))
    mon = _body("workspace-firmware.v0.json", binding=SPINE / "bindings" / "monitor.v0.json")
    assert "tools:add-watch" in mon.template["capabilities"]   # the seat's tool
    door = tools.ToolDoor(pg, did=mon.identity.did, capabilities=mon.template["capabilities"])
    args = {"name": "asks left waiting", "metric": "asks_received", "op": ">", "threshold": 0}
    with pytest.raises(tools.ConsequentialHold):
        door.call("add-watch", args)                 # holds for the human's yes
    door.call("add-watch", args, confirmed=True)     # the yes: it lands
    snap = monitor.snapshot(pg, rails=False)
    [w] = snap["watches"]
    assert w["name"] == "asks left waiting" and w["ok"] is True and w["added_by"] == mon.identity.did
    assert w["state"] == "green" and w["reads"] == "red when asks_received > 0.0 · now 0 → green"
    dispatch.submit_ask(pg, "one ask, unserved", person="did:orreth:person:test")     # now a red watch: the condition holds
    [w] = monitor.snapshot(pg, rails=False)["watches"]
    assert w["value"] == 1 and w["ok"] is False and w["red"] is True and w["state"] == "red"
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
    import time
    end = time.monotonic() + 30
    while True:                       # the rig was parked for the tests before this one (lock 5): its bodies renew
        with seats.urlopen(f"http://127.0.0.1:{rig.port}/monitor", timeout=15) as r:   # their leases as they serve
            snap = json.loads(r.read())                                                 # again — the honest glass sp2's
        alive = {b["name"] for b in snap["bodies"] if b["alive"]}                        # fold shows each name's TRUE
        if {"librarian", "crew", "monitor"} <= alive or time.monotonic() > end:          # self (an earlier module's dead
            break                                                                       # crew no longer stands in for it)
        time.sleep(0.5)
    assert {"outbox", "asks", "bodies", "values", "watches", "benches", "topic_depth", "harness"} <= set(snap)
    assert snap["values"]["bodies_alive"] >= 7                    # leases renewed as they serve
    # row 4, panel sp3: the doors are timed — this knock lands after it answers, so a second read
    # shows the monitor door itself; the reference has no pool and says so (null), never a zero
    assert snap["pool"] is None and isinstance(snap["doors"], list) and snap["values"]["door_p95_ms"] >= 0
    with seats.urlopen(f"http://127.0.0.1:{rig.port}/monitor", timeout=15) as r:
        snap2 = json.loads(r.read())
    mon = [d for d in snap2["doors"] if d["door"] == "GET /monitor"]
    assert mon and mon[0]["n"] >= 1 and mon[0]["p95_ms"] >= mon[0]["p50_ms"] > 0
    assert snap2["values"]["door_p95_ms"] == max(d["p95_ms"] for d in snap2["doors"])
    # the version whisper (JB's ask): the reference says what it is through its health door
    with seats.urlopen(f"http://127.0.0.1:{rig.port}/health", timeout=15) as r:
        h = json.loads(r.read())
    assert h["kernel"] == "reference" and h["version"] and h["lit_at"].endswith("Z")
    assert {b["name"] for b in snap["bodies"] if b["alive"]} >= {"librarian", "crew", "monitor"}
    req = urllib.request.Request(f"http://127.0.0.1:{rig.port}/harness/run",
                                 data=json.dumps({"template": "librarian"}).encode(),
                                 headers={"content-type": "application/json"}, method="POST")
    with seats.urlopen(req, timeout=30) as r:
        run = json.loads(r.read())
    assert run["template"] == "librarian" and run["passed"] == 2 and run["failed"] == 0


def test_the_doors_are_named_timed_and_folded_the_slowest_first():
    """Row 4, panel sp3: the pure half — a door's name as the router spells it, the
    ring keeping the last KEEP samples, the reading the slowest first, the watch's
    metric the slowest p95 (the fixture doors-v0.json pins the fold on both kernels)."""
    from orreth_spine import doors
    assert doors.door_name("get", "/ask/ask_1a2b?x=1") == "GET /ask/:id"
    assert doors.door_name("GET", "/schedules/librarian") == "GET /schedules/:runner"
    assert doors.door_name("GET", "/wp-admin") == "GET other"
    d = doors.Doors()
    for i in range(doors.KEEP + 10):
        d.record("GET /monitor", i)
    d.record("GET /ask/:id", 5000.0)
    r = d.read()
    assert r[0]["door"] == "GET /ask/:id" and r[1]["n"] == doors.KEEP and r[1]["max_ms"] == doors.KEEP + 9
    assert doors.slowest_p95(r) == 5000.0
    d.clear()
    assert d.read() == [] and doors.slowest_p95([]) == 0.0
    assert doors.fold([]) == {"n": 0, "p50_ms": None, "p95_ms": None, "max_ms": None}


# ---- the honest glass sp2 (2026-09-29): W85 one name one self · W86 the watch's rest, the waiting stopped -----


def test_the_roster_folds_one_row_per_name_and_counts_the_earlier_selves(pg, monkeypatch):
    """W85: JB's BODIES card drew every body twice — a box's first crew of ten fresh selves
    beside the host's. The roster folds to the NAME: the living self first, else the
    latest; the earlier selves counted, never drawn; `bodies_dormant` counts names with no
    living self, not dead keypairs."""
    monkeypatch.setenv("SPINE_SCOPE", "u:law-" + secrets.token_hex(3))
    for did, name, alive in (("twin-old", "twin", False), ("twin-new", "twin", True),
                             ("gone-old", "gone", False), ("gone-new", "gone", False)):
        presence.renew(pg, "did:orreth:agent:" + did, name, "resident", ttl_s=3600)
        if not alive:
            pg.cursor().execute("UPDATE spine_leases SET until = now() - interval '1 second' WHERE did = %s",
                                ("did:orreth:agent:" + did,))
    roster = {b["name"]: b for b in presence.roster(pg)}
    assert set(roster) == {"twin", "gone"}                          # one row per name
    assert roster["twin"]["alive"] and roster["twin"]["did"].endswith("twin-new") and roster["twin"]["earlier_selves"] == 1
    assert not roster["gone"]["alive"] and roster["gone"]["earlier_selves"] == 1
    values = monitor.snapshot(pg, rails=False)["values"]
    assert (values["bodies_alive"], values["bodies_dormant"]) == (1, 1)   # names, not selves


def test_a_watch_rests_on_the_word_recorded_never_deleted_and_turns_nothing_after(pg, monkeypatch):
    """W86: there was no way to rest a watch (rule 11). `rest_watch` records the stop on
    the row; the snapshot draws the active alone and counts the rested; the judge turns
    nothing for a rested watch."""
    monkeypatch.setenv("SPINE_SCOPE", "u:law-" + secrets.token_hex(3))
    wid = monitor.add_watch(pg, "always red", "bodies_alive", ">=", 0, by="did:orreth:person:jb")
    snap = monitor.snapshot(pg, rails=False)
    assert [w["watch_id"] for w in snap["watches"]] == [wid] and snap["watches"][0]["red"] and snap["watches_rested"] == 0
    made = monitor.rest_watch(pg, wid, "did:orreth:person:jb")
    assert made == {"watch_id": wid, "name": "always red", "added_by": "did:orreth:person:jb",
                    "rested_by": "did:orreth:person:jb", "already": False}
    snap = monitor.snapshot(pg, rails=False)
    assert snap["watches"] == [] and snap["watches_rested"] == 1
    assert monitor.judge(pg) == []                                   # a rested watch turns nothing
    cur = pg.cursor()
    cur.execute("SELECT active, rested_by, rested_at IS NOT NULL FROM spine_watches WHERE watch_id = %s", (wid,))
    assert cur.fetchone() == (False, "did:orreth:person:jb", True)   # recorded, never deleted
    assert monitor.rest_watch(pg, wid, "did:orreth:person:jb")["already"] is True
    with pytest.raises(KeyError):
        monitor.rest_watch(pg, "watch_nope", "did:orreth:person:jb")


def test_the_asks_left_waiting_are_listed_and_a_local_one_is_stopped_with_its_facts(pg, monkeypatch):
    """W86: the ASKS card showed "received 9" with no way to reach them. The snapshot lists
    the asks left waiting; `dispatch.stop_ask` stops a local one on the asker's word (or a
    governing seat's — W69), recorded as cancelled with a journey line and a reply on the rail."""
    monkeypatch.setenv("SPINE_SCOPE", "u:law-" + secrets.token_hex(3))
    jb, quinn = "did:orreth:person:jb", "did:orreth:person:quinn"
    from orreth_spine import outbox
    outbox.ensure_schema(pg)
    aid = dispatch.submit_ask(pg, "left waiting for a body that never came", person=jb)
    waiting = monitor.snapshot(pg, rails=False)["waiting"]
    assert [w["ask_id"] for w in waiting] == [aid] and waiting[0]["person"] == jb
    with pytest.raises(PermissionError):                              # quinn holds no governing seat
        dispatch.stop_ask(pg, aid, quinn)
    with pytest.raises(KeyError):
        dispatch.stop_ask(pg, "ask_nope", jb)
    made = dispatch.stop_ask(pg, aid, jb)
    assert made["status"] == "cancelled" and made["words"] == dispatch.STOPPED_WORDS
    snap = monitor.snapshot(pg, rails=False)
    assert snap["waiting"] == [] and snap["asks"] == {"cancelled": 1}
    assert glass.ask_view(pg, aid)["reply"] == dispatch.STOPPED_WORDS
    cur = pg.cursor()
    cur.execute("SELECT convert_from(body, 'UTF8') FROM spine_outbox WHERE convert_from(body, 'UTF8')"
                " LIKE %s ORDER BY outbox_id", ('%"correlation_id":"' + aid + '"%',))
    assert {json.loads(r[0])["type"] for r in cur.fetchall()} >= {"orreth.journey.v1", "orreth.reply.v1"}
    assert dispatch.stop_ask(pg, aid, jb)["words"] == "it had already come to rest"


def test_the_grounds_prune_takes_one_test_shaped_world_and_leaves_a_persons(pg, monkeypatch):
    """The ground's prune (sp2): every row of a test-shaped world leaves every table with a
    scope column and the children by their parent; a world a person named is never touched."""
    from orreth_spine import prune, scheduler
    mine = "u:law-" + secrets.token_hex(3)
    monkeypatch.setenv("SPINE_SCOPE", mine)
    monitor.add_watch(pg, "w", "bodies_alive", ">=", 0, by="x")
    sid = scheduler.add(pg, "echo", "human", "x", 60, "did:orreth:person:jb")
    pg.cursor().execute("INSERT INTO spine_occurrences (occurrence_id, schedule_id) VALUES ('occ_x', %s)", (sid,))
    monkeypatch.setenv("SPINE_SCOPE", "u:person")                    # a person's world, not test-shaped
    monitor.add_watch(pg, "theirs", "bodies_alive", ">=", 0, by="x")
    out = prune.scope(pg, mine)
    assert out["spine_watches"] == 1 and out["spine_schedules"] == 1 and out["spine_occurrences"] == 1
    cur = pg.cursor()
    cur.execute("SELECT count(*) FROM spine_watches WHERE scope = %s", (mine,)); assert cur.fetchone() == (0,)
    cur.execute("SELECT count(*) FROM spine_watches WHERE scope = 'u:person'"); assert cur.fetchone() == (1,)
    got = prune.ground(pg)                                            # every test-shaped world; u:person stays
    assert got["worlds"] >= 0
    cur.execute("SELECT count(*) FROM spine_watches WHERE scope = 'u:person'"); assert cur.fetchone() == (1,)
    pg.cursor().execute("DELETE FROM spine_watches WHERE scope = 'u:person'")


@rails
def test_the_rest_the_stop_and_the_forget_doors_on_the_rig(pg, rig):
    """The three doors of sp2 over HTTP: the governing word is checked INSIDE the handler —
    a seated person who neither authored the watch nor governs is refused in words; the
    owner rests, stops and forgets; the words the glass draws come from the doors."""
    import psycopg
    from orreth_spine.rails import PG_DSN
    port = rig.port
    owner = seats.owner(port)
    pg = psycopg.connect(PG_DSN, autocommit=True)          # the rig's own ground (the fixture's is a throwaway schema)
    wid = monitor.add_watch(pg, "sp2 red", "bodies_alive", ">=", 0, by="did:orreth:person:monitor")
    s, b = seats.post(port, "/watches/rest", {"watch_id": wid, "person": "did:orreth:person:quinn"})     # quinn: seated, not governing
    assert s == 403 and "governing seat" in b["error"]
    s, b = seats.post(port, "/watches/rest", {"watch_id": "watch_nope"})
    assert s == 404
    s, b = seats.post(port, "/watches/rest", {"watch_id": wid})
    assert (s, b["rested"], b["already"]) == (202, wid, False)
    s, snap = seats.get(port, "/monitor")
    assert s == 200 and all(w["watch_id"] != wid for w in snap["watches"]) and snap["watches_rested"] >= 1
    pg.cursor().execute("INSERT INTO spine_asks (ask_id, text, person, scope, status) VALUES (%s, 'sp2 left waiting', %s, %s, 'received')",
                        ("ask_sp2" + secrets.token_hex(3), owner, ev.scope()))
    s, snap = seats.get(port, "/monitor")
    waiting = [a for a in snap["waiting"] if a["text"] == "sp2 left waiting"]
    assert len(waiting) == 1
    s, b = seats.post(port, "/asks/stop", {"id": waiting[0]["ask_id"], "person": "did:orreth:person:quinn"})
    assert s == 403
    s, b = seats.post(port, "/asks/stop", {"id": waiting[0]["ask_id"]})
    assert s == 200 and b["status"] == "cancelled" and b["words"] == dispatch.STOPPED_WORDS
    s, b = seats.post(port, "/asks/stop", {"id": "ask_nope"})
    assert s == 404
    pg.cursor().execute("INSERT INTO spine_peers (cell, scope, door, unreachable_since) VALUES ('ghost', %s, 'http://127.0.0.1:1', now() - interval '4 days')",
                        (ev.scope(),))
    s, card = seats.get(port, "/world")
    [ghost] = [p for p in card["peers"] if p["cell"] == "ghost"]
    assert ghost["words"].startswith("cell ghost · unreachable since 20") and len(ghost["words"]) > len("cell ghost · unreachable since HH:MM")
    s, b = seats.post(port, "/peers/forget", {"cell": "ghost", "person": "did:orreth:person:quinn"})
    assert s == 403 and "governing seat" in b["error"]
    s, b = seats.post(port, "/peers/forget", {"cell": "ghost"})
    assert (s, b["forgotten"]) == (202, "ghost")
    s, card = seats.get(port, "/world")
    assert all(p["cell"] != "ghost" for p in card["peers"])
    s, b = seats.post(port, "/peers/forget", {"cell": "ghost"})
    assert s == 404
    pg.close()
