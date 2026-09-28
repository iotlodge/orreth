# PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp8 row 3c, THE REMEDIATION RAIL · 2026-09-27
"""THE REMEDIATION RAIL's laws on the Python reference (canon 0005, P7 sp8
row 3c): (a) the FORENSIC TURN hands the planner a dossier read off the
ground, and the levers this door serves, in place of a marker id; (b) the
LEVER CATALOGUE is data both kernels read, and the planner answers IN it;
(c) the KERNEL pulls the lever — routine at once, consequential held for
a person's click — as a recorded hop in the intention's session, and a
resident never receives a job it cannot do; (d) the OUTCOME is
ATTRIBUTED: green after our act is an improvement with its cause, green
with no act is self-healed, red past the lever's settle plans once more
with what was tried and then hands the human the dossier, a cancelled
hold is recorded; the drift harness grades it (the eleventh check)."""
import json
import secrets
from pathlib import Path

import pytest

from orreth_spine import (envelope as ev, gateway, glass, harness, intent, levers, markers, monitor, presence,
                          proof, resident, services, tools)

SPINE = Path(__file__).resolve().parents[1]
POLICY = SPINE / "policy" / "covenant-policy.v1.json"
ME = "did:orreth:person:remedy"
WEATHER = tools.tool_manifest("weather", tools.TOOLS["weather"])


def _scope(monkeypatch):
    monkeypatch.setenv("SPINE_SCOPE", "u:law-" + secrets.token_hex(3))


def _body(template, gw=None):
    r = resident.Resident(SPINE / "templates" / template, gateway=gw, home=None)
    r.load_policy(POLICY)
    return r


def _serve(pg, body, ask_id, chain=("the kernel",)):
    body._serve_conn = pg
    with pg.transaction():
        body._serve_ask(pg.cursor(), ask_id, list(chain))
    return glass.ask_view(pg, ask_id)


def _turn_rows(pg, iid):
    cur = pg.cursor()
    cur.execute("SELECT turn_id, plan_ask, objective_ask, dossier, watch, episode, tries, lever, lever_args,"
                " because, lever_ask, pulled_at, outcome, outcome_note FROM spine_intent_turns"
                " WHERE intention_id = %s ORDER BY at", (iid,))
    cols = ("turn_id", "plan_ask", "objective_ask", "dossier", "watch", "episode", "tries", "lever",
            "lever_args", "because", "lever_ask", "pulled_at", "outcome", "outcome_note")
    return [dict(zip(cols, r)) for r in cur.fetchall()]


def _red_world(pg, planner_reply: str):
    """Resiliency standing, a planner that answers with ONE scripted line, a
    librarian, a watch on dormant bodies — and the librarian's lease lapsed:
    the watch is born red on the first turn."""
    planner = _body("firmware-planner.v0.json", gateway.FakeGateway(reply=planner_reply))
    planner.join(pg)
    lib = _body("librarian-resident.v0.json", gateway.FakeGateway(reply="I read it."))
    lib.join(pg)
    r = intent.declared(pg, intent.RESILIENCY["words"], serves="resiliency", kind="kernel",
                        by="the kernel", interests=intent.RESILIENCY["interests"],
                        planner="planner", runner="librarian")
    wid = monitor.add_watch(pg, "a body's lease lapsed", "bodies_dormant", ">", 0, by=ME)
    presence.renew(pg, lib.identity.did, "librarian", "resident", ttl_s=0)      # dormant: red
    return r, wid, planner, lib


def _markers(pg, kind, parent):
    cur = pg.cursor()
    cur.execute("SELECT note FROM spine_markers WHERE kind = %s AND parent = %s ORDER BY at", (kind, parent))
    return [n for (n,) in cur.fetchall()]


# ---- (b) the catalogue and the planner's answer, pure ----------------------------------------

def test_the_catalogue_is_data_and_the_planner_answers_in_it():
    cat = levers.catalogue()
    names = [d["name"] for d in cat]
    assert "body.restart" in names and "service.check" in names and "service.retire" in names
    assert [d["name"] for d in levers.remedies(cat, "bodies_dormant", "rust")] == \
        ["body.restart", "service.check", "service.restore"]
    assert [d["name"] for d in levers.remedies(cat, "bodies_dormant", "python")] == \
        ["service.check", "service.restore"]                                  # the reference seats no processes
    assert all(d["consequence"] != "grave" for d in levers.remedies(cat, "asks_received", "rust"))
    assert levers.remedies(cat, "route_failures_1h", "python")[-1]["name"] == "service.retire"   # holds
    words = levers.lever_words(levers.remedies(cat, "bodies_dormant", "rust"))
    assert words.startswith("LEVERS this kernel can pull for this watch") and "body.restart name=<" in words
    assert "Runs at once." in words
    assert levers.lever_words([]) == "LEVERS this kernel can pull for this watch: none."
    assert levers.read_lever("LEVER: body.restart name=echo — BECAUSE: echo is parked after three deaths.") == \
        {"lever": "body.restart", "args": {"name": "echo"}, "because": "echo is parked after three deaths"}
    assert levers.read_lever("**LEVER:** none - because the waiting ask needs a body") == \
        {"lever": None, "args": {}, "because": "the waiting ask needs a body"}
    assert levers.read_lever("My answer: lever: Service.Check name=\"weather\" : it reads unhealthy")["args"] == \
        {"name": "weather"}
    assert levers.read_lever("Restart the echo body.") is None                # a sentence: the crew's road
    assert levers.read_lever(None) is None
    with pytest.raises(ValueError):
        levers.catalogue(SPINE / "tools.v0.json")                              # not a lever catalogue


def test_the_dossier_reads_in_plain_words():
    d = {"watch": {"name": "a body's lease lapsed", "metric": "bodies_dormant", "op": ">", "threshold": 0.0,
                   "value": 1, "state": "red", "since": "2026-09-27T20:11:03.120+00:00", "since_s": 40},
         "readings": [{"at": "2026-09-27T20:11:03.120+00:00", "to": "red", "value": 1},
                      {"at": "2026-09-27T19:58:10+00:00", "to": "green", "value": 0}],
         "subjects": [{"kind": "body", "name": "echo", "state": "dormant — its lease lapsed 40 seconds ago"}],
         "acts": [{"at": "2026-09-27T20:10:59+00:00", "words": "the kernel parked echo after 3 deaths"}],
         "last_red": {"at": "2026-09-27T19:57:40+00:00", "lever": "body.restart", "args": {"name": "echo"},
                      "outcome": "cured", "note": None},
         "tried": [{"lever": "service.check", "args": {"name": "weather"}, "outcome": "still-red"}]}
    text = levers.dossier_words(d)
    assert text.splitlines() == [
        "THE WATCH: \"a body's lease lapsed\" is red — red when bodies_dormant > 0.0, now 1, since 20:11:03 (40 seconds ago).",
        "WHAT IT SAW LATELY: red at 20:11:03 (value 1) · green at 19:58:10 (value 0).",
        "WHO IT NAMES: echo (body) — dormant — its lease lapsed 40 seconds ago.",
        "THE LAST ACTS ON THEM: 20:10:59 the kernel parked echo after 3 deaths.",
        "THE LAST TIME IT WENT RED: 19:57:40 — the kernel pulled body.restart name=echo; cured.",
        "TRIED THIS TIME: service.check name=weather → still-red."]
    bare = levers.dossier_words({"watch": dict(d["watch"], since=None, since_s=None), "readings": [],
                                 "subjects": [], "acts": [], "last_red": None, "tried": []})
    assert "nothing before this." in bare and "no one by name" in bare and "never before." in bare \
        and bare.endswith("TRIED THIS TIME: nothing yet.")
    assert levers.ago_words(0) == "0 seconds ago" and levers.ago_words(61) == "1 minute ago" \
        and levers.ago_words(7300) == "2 hours ago"


# ---- (a) the forensic turn ---------------------------------------------------------------------

def test_the_forensic_turn_hands_the_planner_the_dossier_and_the_levers_this_door_serves(pg, monkeypatch):
    _scope(monkeypatch)
    r, wid, planner, lib = _red_world(pg, "LEVER: none — BECAUSE: nothing here restarts a body.")
    t = intent.turn(pg)
    assert len(t["observed"]) == 1
    [row] = _turn_rows(pg, r["intention_id"])
    d = json.loads(row["dossier"])
    assert row["watch"] == wid and row["episode"] == row["turn_id"] and row["tries"] == 1
    assert d["watch"]["name"] == "a body's lease lapsed" and d["watch"]["state"] == "red" and d["watch"]["value"] == 1
    assert [x["to"] for x in d["readings"]] == ["red"]                        # born red: the one turn so far
    assert d["subjects"][0]["kind"] == "body" and d["subjects"][0]["name"] == "librarian"
    assert d["subjects"][0]["state"].startswith("dormant — its lease lapsed")
    assert d["last_red"] is None and d["tried"] == []
    pv = glass.ask_view(pg, row["plan_ask"])
    assert pv["target"] == "planner"
    text = pv["text"]
    assert text.startswith("INTENTION (serves resiliency): keep this world resilient")
    assert "THE DOSSIER — what the kernel read on the ground" in text
    assert "WHO IT NAMES: librarian (body) — dormant" in text
    assert "- service.check name=<" in text and "- service.restore name=<" in text
    assert "body.restart" not in text                                         # not this door's lever
    assert text.rstrip().endswith("or, when no lever fits: LEVER: none — BECAUSE: <one plain sentence>")
    assert "a marker of kind" not in text                                     # the marker id is gone


# ---- (c) · (d) no lever fits → the human, with the dossier; green on its own → self-healed -------

def test_no_lever_fits_tells_the_human_with_the_dossier_and_a_green_on_its_own_is_self_healed(pg, monkeypatch):
    _scope(monkeypatch)
    r, wid, planner, lib = _red_world(pg, "LEVER: none — BECAUSE: the dormant body is a thread of the Bridge.")
    intent.turn(pg)
    [row] = _turn_rows(pg, r["intention_id"])
    _serve(pg, planner, row["plan_ask"])                                       # the planner answers
    [f] = intent.turn(pg)["filed"]
    assert f["lever"] is None and f["notice"].startswith("ask_")
    [row] = _turn_rows(pg, r["intention_id"])
    assert row["lever"] == "none" and row["objective_ask"] == "-" and row["lever_ask"] == f["notice"]
    assert row["outcome"] is None                                              # the red still stands
    n = glass.ask_view(pg, f["notice"])
    assert n["served_by"] == "the kernel" and n["status"] == "replied" and n["session"] == r["session"]
    assert n["reply"].startswith("Watch \"a body's lease lapsed\" is red and no lever the kernel holds fits it")
    assert "the dormant body is a thread of the Bridge" in n["reply"] and "This one is yours." in n["reply"]
    assert "WHO IT NAMES: librarian (body) — dormant" in n["reply"]            # the dossier attached
    assert _markers(pg, "observation", r["marker"]) == \
        ["no lever fits watch \"a body's lease lapsed\" — the planner's reason: the dormant body is a thread of the Bridge"]
    cur = pg.cursor()
    cur.execute("SELECT count(*) FROM spine_asks WHERE target = 'librarian' AND scope = %s", (ev.scope(),))
    assert cur.fetchone()[0] == 0                                              # the crew got no job it cannot do
    assert intent.turn(pg)["attributed"] == []                                 # still red: nothing to say
    presence.renew(pg, lib.identity.did, "librarian", "resident", ttl_s=60)   # the body comes back on its own
    [a] = intent.turn(pg)["attributed"]
    assert a["outcome"] == "self-healed"
    [row] = _turn_rows(pg, r["intention_id"])
    assert row["outcome"] == "self-healed" and row["outcome_note"] == \
        "watch \"a body's lease lapsed\" went green on its own — the kernel pulled no lever; recorded as self-healed"
    imp = markers.get(pg, a["improvement"])
    assert imp["kind"] == "improvement" and imp["parent"] == r["marker"] and imp["ref"] == wid
    [i] = [i for i in intent.listing(pg, kind="kernel") if i["intention_id"] == r["intention_id"]]
    assert i["last_outcome"].startswith("self-healed — watch")
    assert intent.turn(pg)["attributed"] == []                                 # attributed ONCE


# ---- (c) · (d) a routine lever is pulled by the kernel; the green is attributed to it ----------------

def test_a_routine_lever_is_pulled_by_the_kernel_and_the_green_wears_its_cause(pg, monkeypatch):
    _scope(monkeypatch)
    services.register(pg, "weather", "tool", WEATHER, by=ME)
    r, wid, planner, lib = _red_world(pg, "LEVER: service.check name=weather — BECAUSE: the shelf may be stale.")
    intent.turn(pg)
    [row] = _turn_rows(pg, r["intention_id"])
    _serve(pg, planner, row["plan_ask"])
    [f] = intent.turn(pg)["filed"]
    assert (f["lever"], f["args"], f["held"]) == ("service.check", {"name": "weather"}, False)
    [row] = _turn_rows(pg, r["intention_id"])
    assert row["lever"] == "service.check" and json.loads(row["lever_args"]) == {"name": "weather"}
    assert row["because"] == "the shelf may be stale" and row["pulled_at"] is not None
    hop = glass.ask_view(pg, f["ask_id"])
    assert hop["served_by"] == "the kernel" and hop["status"] == "replied" and hop["session"] == r["session"]
    assert hop["text"] == "the kernel pulls service.check name=weather"
    assert hop["reply"].startswith("On the intention's authority the kernel pulled service.check name=weather: "
                                   "weather was probed — it reads healthy")
    assert hop["reply"].endswith("Because the shelf may be stale.")
    assert services.get(pg, "weather")["state"] == "healthy"                   # the lever really ran
    cur = pg.cursor()
    cur.execute("SELECT kind, parent, note FROM spine_markers WHERE ref = %s", (f["ask_id"],))
    [(kind, parent, note)] = cur.fetchall()
    assert kind == "action" and parent is not None and note.startswith("pulled service.check name=weather")
    assert intent.turn(pg)["attributed"] == []                                 # red, within the settle
    presence.renew(pg, lib.identity.did, "librarian", "resident", ttl_s=60)
    [a] = intent.turn(pg)["attributed"]
    assert a["outcome"] == "cured"
    assert markers.get(pg, a["improvement"])["note"] == \
        "watch \"a body's lease lapsed\" went green after the kernel pulled service.check name=weather" \
        " — the planner's reason: the shelf may be stale"
    [row] = _turn_rows(pg, r["intention_id"])
    assert row["outcome"] == "cured"
    [c] = [c for c in harness.checks(pg) if c["name"] == "every red is answered and every green attributed"]
    assert c["ok"] and c["detail"].startswith("1 attributed")


def test_a_lever_this_door_does_not_serve_is_said_honestly(pg, monkeypatch):
    _scope(monkeypatch)
    r, wid, planner, lib = _red_world(pg, "LEVER: body.restart name=librarian — BECAUSE: it is dormant.")
    intent.turn(pg)
    [row] = _turn_rows(pg, r["intention_id"])
    _serve(pg, planner, row["plan_ask"])
    [f] = intent.turn(pg)["filed"]
    assert f["lever"] is None
    assert _markers(pg, "observation", r["marker"]) == \
        ["the planner named body.restart for watch \"a body's lease lapsed\" — a lever this door does not serve"]
    assert "This one is yours." in glass.ask_view(pg, f["notice"])["reply"]


# ---- (c) · (d) a consequential lever holds; a cancel is recorded; a green withdraws the hold ------------

def test_a_consequential_lever_holds_for_a_person_and_a_cancel_is_recorded(pg, monkeypatch):
    _scope(monkeypatch)
    services.register(pg, "weather", "tool", WEATHER, by=ME)
    r, wid, planner, lib = _red_world(pg, "LEVER: service.retire name=weather — BECAUSE: it keeps failing.")
    intent.turn(pg)
    [row] = _turn_rows(pg, r["intention_id"])
    _serve(pg, planner, row["plan_ask"])
    [f] = intent.turn(pg)["filed"]
    assert f["held"] is True and f["lever"] == "service.retire"
    h = glass.ask_view(pg, f["ask_id"])
    assert h["status"] == "awaiting-confirm" and h["served_by"] == "the kernel"
    assert h["hold"]["tool"] == "service.retire" and h["hold"]["level"] == "L2" and h["hold"]["args"] == {"name": "weather"}
    assert h["reply"].startswith("Are you sure? Service.retire name=weather — the kernel proposes it for the intention")
    assert "because it keeps failing" in h["reply"] and "Cancel is the default" in h["reply"]
    assert services.get(pg, "weather")["state"] == "registered"               # nothing ran
    [row] = _turn_rows(pg, r["intention_id"])
    assert row["pulled_at"] is None and row["lever_ask"] == f["ask_id"]
    assert intent.turn(pg)["attributed"] == []                                 # holding: the kernel waits
    proof.settle_kernel_act(pg, f["ask_id"], approve=False, by=ME)             # the person says no
    [a] = intent.turn(pg)["attributed"]
    assert a["outcome"] == "cancelled"
    [row] = _turn_rows(pg, r["intention_id"])
    assert row["outcome"] == "cancelled" and row["outcome_note"].startswith(
        "the service.retire name=weather lever for watch \"a body's lease lapsed\" never ran — Cancelled")
    assert _markers(pg, "observation", r["marker"])[-1] == row["outcome_note"]


def test_a_green_while_the_hold_waits_withdraws_it_and_is_self_healed(pg, monkeypatch):
    _scope(monkeypatch)
    services.register(pg, "weather", "tool", WEATHER, by=ME)
    r, wid, planner, lib = _red_world(pg, "LEVER: service.retire name=weather — BECAUSE: it keeps failing.")
    intent.turn(pg)
    [row] = _turn_rows(pg, r["intention_id"])
    _serve(pg, planner, row["plan_ask"])
    [f] = intent.turn(pg)["filed"]
    presence.renew(pg, lib.identity.did, "librarian", "resident", ttl_s=60)
    [a] = intent.turn(pg)["attributed"]
    assert a["outcome"] == "self-healed"
    h = glass.ask_view(pg, f["ask_id"])
    assert h["status"] == "cancelled" and h["reply"].startswith("Withdrawn — the watch went green on its own")
    assert services.get(pg, "weather")["state"] == "registered"


# ---- (d) still red after the lever: once more with what was tried, then the human ----------------------

def test_still_red_plans_once_more_with_what_was_tried_then_hands_the_human_the_dossier(pg, monkeypatch):
    _scope(monkeypatch)
    services.register(pg, "weather", "tool", WEATHER, by=ME)
    r, wid, planner, lib = _red_world(pg, "LEVER: service.check name=weather — BECAUSE: the shelf may be stale.")
    intent.turn(pg)
    [row] = _turn_rows(pg, r["intention_id"])
    _serve(pg, planner, row["plan_ask"])
    [f] = intent.turn(pg)["filed"]
    assert intent.turn(pg)["attributed"] == []                                 # within the settle window
    cur = pg.cursor()
    cur.execute("UPDATE spine_intent_turns SET pulled_at = now() - interval '20 seconds' WHERE turn_id = %s",
                (row["turn_id"],))
    [a] = intent.turn(pg)["attributed"]
    assert a["outcome"] == "still-red" and a["again"].startswith("turn_")
    first, second = _turn_rows(pg, r["intention_id"])
    assert first["outcome"] == "still-red" and first["outcome_note"] == \
        "watch \"a body's lease lapsed\" is still red 10 seconds after the kernel pulled service.check name=weather"
    assert second["episode"] == first["turn_id"] and second["tries"] == 2 and second["outcome"] is None
    d = json.loads(second["dossier"])
    assert d["tried"] == [{"lever": "service.check", "args": {"name": "weather"}, "outcome": "still-red"}]
    text = glass.ask_view(pg, second["plan_ask"])["text"]
    assert "TRIED THIS TIME: service.check name=weather → still-red." in text
    assert "THE LAST ACTS ON THEM: none recorded." in text                    # the check touched weather, not the body
    assert "THE LAST TIME IT WENT RED: never before." in text                  # this episode is not the last
    _serve(pg, planner, second["plan_ask"])                                    # the same answer again
    [f2] = intent.turn(pg)["filed"]
    assert f2["turn_id"] == second["turn_id"] and f2["lever"] == "service.check"
    cur.execute("UPDATE spine_intent_turns SET pulled_at = now() - interval '20 seconds' WHERE turn_id = %s",
                (second["turn_id"],))
    [a2] = intent.turn(pg)["attributed"]
    assert a2["outcome"] == "still-red" and a2["handed"].startswith("ask_")
    handed = glass.ask_view(pg, a2["handed"])
    assert handed["served_by"] == "the kernel" and handed["session"] == r["session"]
    assert handed["reply"].startswith("Watch \"a body's lease lapsed\" is still red after the kernel tried "
                                      "service.check name=weather · service.check name=weather. "
                                      "The kernel has no other lever for it — this one is yours.")
    assert "WHO IT NAMES: librarian (body) — dormant" in handed["reply"]
    assert intent.turn(pg)["attributed"] == [] and len(_turn_rows(pg, r["intention_id"])) == 2   # no third
    [c] = [c for c in harness.checks(pg) if c["name"] == "every red is answered and every green attributed"]
    assert c["ok"] and c["detail"].startswith("2 attributed")


def test_the_harness_names_a_red_nobody_answered(pg, monkeypatch):
    _scope(monkeypatch)
    r, wid, planner, lib = _red_world(pg, "LEVER: none — BECAUSE: no.")
    intent.turn(pg)                                                            # planned, never answered
    [c] = [c for c in harness.checks(pg) if c["name"] == "every red is answered and every green attributed"]
    assert c["ok"]                                                             # young: still the planner's turn
    pg.cursor().execute("UPDATE spine_intent_turns SET at = now() - interval '5 minutes' WHERE intention_id = %s",
                        (r["intention_id"],))
    c = harness.reds_answered(pg)
    assert not c["ok"] and c["unanswered"] == ["a body's lease lapsed"]
    assert "unanswered past 2 min: a body's lease lapsed" in c["detail"]
