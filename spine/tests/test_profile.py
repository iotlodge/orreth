# PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp8, the human profile (W58) · 2026-09-26
"""THE HUMAN PROFILE (P7 sp8, W58 — walk #15: the librarian answered the
weather for the wrong place). A person's own words about themselves land
as facts with the chain, provenance-labeled as the Mirror had it (you
told me · I observed · the mirror noticed); the newest word per field
wins; forgetting is a recorded withdrawal, never a deletion; every body
reads the profile first at the voiced answer; the weather tool defaults
to the asker's own place and says so when there is none; the human's
clock reads the profile ahead of the ground's dial; a routed ask's
carried slice wins on the far ground; the doors serve it."""
import json
import secrets
import urllib.request

import pytest

from orreth_spine import dispatch, envelope as ev, markers, profile, resident, tools

from tests.test_glass import _get, _post  # noqa: E402

ME = "did:orreth:person:jb"
BOULDER = {"lat": 40.01499, "lon": -105.27055, "zone": "America/Denver", "label": "Boulder, Colorado, United States"}


def _scope(monkeypatch):
    monkeypatch.setenv("SPINE_SCOPE", "u:law-" + secrets.token_hex(3))


def _facts(pg, type_):
    cur = pg.cursor()
    cur.execute("SELECT body FROM spine_outbox ORDER BY outbox_id")
    out = [ev.decode(bytes(b)) for (b,) in cur.fetchall()]
    return [e for e in out if e["type"] == type_ and e["universe_id"] == ev.scope()]


def _geo(place):
    return dict(BOULDER) if "boulder" in place.lower() else None


def _ask(pg, text, person=ME, zone=None):
    """An ask row without the rails: the row is what the profile reads."""
    profile.ensure_schema(pg)
    ask_id = "ask_" + secrets.token_hex(6)
    pg.execute("INSERT INTO spine_asks (ask_id, text, person, scope, zone) VALUES (%s, %s, %s, %s, %s)",
               (ask_id, text, person, ev.scope(), zone))
    return ask_id


def test_a_told_word_is_a_trusted_fact_with_the_chain_and_a_told_place_is_observed_beside_it(pg, monkeypatch):
    """"I live in Boulder, Colorado" lands TRUSTED under the person's own
    chain with an observation marker under their one profile root; the
    kernel's geocoding lands as a SECOND row and fact in the same motion,
    labeled "I observed", never in place of the told words."""
    _scope(monkeypatch)
    made = profile.say(pg, ME, "I live in Boulder, Colorado", geocoder=_geo)
    assert made["act"] == "tell" and made["told"]["field"] == "place" and made["told"]["value"] == "Boulder, Colorado"
    assert made["observed"] == {"lat": BOULDER["lat"], "lon": BOULDER["lon"], "zone": "America/Denver",
                                "label": BOULDER["label"], "marker": made["observed"]["marker"]}
    assert made["words"].startswith("Noted, in your own words — you live in Boulder, Colorado. I observed: Boulder, Colorado, United States is at 40.01,-105.27, its clock America/Denver")
    [told] = _facts(pg, profile.TOLD)
    assert told["authority_chain"] == [ME, "the kernel"] and told["correlation_id"] == ME
    assert told["payload"] == {"ref": ME, "by": ME, "field": "place", "value": "Boulder, Colorado",
                               "asserted_by": "human", "state": "trusted",
                               "hash": ev.content_hash({"field": "place", "value": "Boulder, Colorado"})}
    assert told["marker"]["kind"] == "observation" and told["marker"]["by"] == ME
    root = markers.get(pg, told["marker"]["id"])["parent"]
    assert markers.get(pg, root)["ref"] == f"the profile:{ME}" and markers.get(pg, root)["parent"] is None
    assert profile.profile_root(pg, ME) == root                          # one origin per person
    [seen] = _facts(pg, profile.OBSERVED)
    assert seen["authority_chain"] == ["the kernel"] and seen["payload"]["source"] == "open-meteo geocoder"
    assert seen["payload"]["evidence"] == "Boulder, Colorado" and seen["payload"]["lat"] == BOULDER["lat"]
    assert markers.get(pg, seen["marker"]["id"])["parent"] == told["marker"]["id"]   # the observation hangs under the telling
    rows = profile.claims(pg, ME)
    assert [(c["field"], c["asserted_by"], c["label"] if "label" in c else profile.LABELS[c["asserted_by"]]) for c in rows] == \
        [("place", "kernel", "I observed"), ("place", "human", "you told me")]
    p = profile.portrait(pg, ME)
    assert p["place"] == "Boulder, Colorado" and p["coordinates"]["lat"] == BOULDER["lat"] and p["clock"] == "America/Denver"
    assert p["words"] == ("you told me: you live in Boulder, Colorado — I observed: Boulder, Colorado, United States "
                          "is at 40.01,-105.27, its clock America/Denver")
    # a place the geocoder cannot find keeps the told words, and says so
    made2 = profile.say(pg, ME, "my place is Nowhere Special", geocoder=_geo)
    assert made2["observed"] is None and "could not find its coordinates" in made2["words"]
    assert profile.place_default(profile.claims(pg, ME)) == {"place": "Nowhere Special", "lat": None, "lon": None, "zone": None}
    assert len(_facts(pg, profile.OBSERVED)) == 1


def test_the_newest_word_wins_and_forgetting_is_a_recorded_withdrawal_never_a_deletion(pg, monkeypatch):
    _scope(monkeypatch)
    profile.say(pg, ME, "my name is Jonathan", geocoder=None)
    profile.say(pg, ME, "call me JB", geocoder=None)
    profile.say(pg, ME, "remember about me: I take my coffee black", geocoder=None)
    profile.say(pg, ME, "my time zone is America/Phoenix", geocoder=None)
    p = profile.portrait(pg, ME)
    assert p["name"] == "JB" and p["zone"] == "America/Phoenix" and p["clock"] == "America/Phoenix"
    assert p["words"] == "you told me: your name is JB · your clock is America/Phoenix · I take my coffee black"
    with pytest.raises(profile.ProfileRefused, match="not a clock I know"):
        profile.say(pg, ME, "my zone is Mars/Olympus", geocoder=None)
    gone = profile.say(pg, ME, "forget my name", geocoder=None)
    assert gone["act"] == "forget" and len(gone["withdrawn"]) == 2 and "Forgotten on your word" in gone["words"]
    assert profile.portrait(pg, ME)["name"] is None
    assert len(profile.claims(pg, ME, withdrawn=True)) == 4 and len(profile.claims(pg, ME)) == 2   # the rows stay
    [w] = _facts(pg, profile.WITHDRAWN)
    assert w["authority_chain"] == [ME, "the kernel"] and w["payload"]["what"] == "name" and len(w["payload"]["withdrawn"]) == 2
    gone2 = profile.say(pg, ME, "forget that I take my coffee black", geocoder=None)
    assert gone2["what"] == "I take my coffee black" and profile.portrait(pg, ME)["words"] == "you told me: your clock is America/Phoenix"
    with pytest.raises(profile.ProfileRefused, match="nothing to forget"):
        profile.say(pg, ME, "forget about me: my place", geocoder=None)
    with pytest.raises(profile.ProfileRefused, match="tell me nothing about you"):
        profile.say(pg, ME, "what is the temperature outside?", geocoder=None)


def test_every_body_reads_the_profile_first_and_a_carried_slice_wins(pg, monkeypatch):
    """Slot 1 of the pack: the seat words name the human and their own
    words; nothing told is said so plainly; an ask that came over the
    seam reads what rode with it, not this ground's rows."""
    _scope(monkeypatch)
    a0 = _ask(pg, "what is the weather?")
    words = profile.seat_words(pg, a0)
    assert words.startswith("THE HUMAN you serve is jb. They have told this ground nothing about themselves yet")
    profile.say(pg, ME, "I live in Boulder, Colorado", geocoder=_geo)
    profile.say(pg, ME, "my name is JB", geocoder=None)
    words = profile.seat_words(pg, a0)
    assert words.startswith("THE HUMAN you serve is jb — their own profile, in their own provenance: you told me: your name is JB · you live in Boulder, Colorado — I observed:")
    assert words.endswith("Sovereign: honor it, never recite it unasked; when the ask turns on their place or clock, use these.")
    # the carried slice (the seam's column) wins, and says it rode here
    stranger = "did:orreth:person:visitor"
    a1 = _ask(pg, "echo, say HERON", person=stranger)
    rode = profile.carry(pg, ME)
    assert rode == {"words": profile.slice_words(profile.claims(pg, ME)),
                    "place": {"place": "Boulder, Colorado", "lat": BOULDER["lat"], "lon": BOULDER["lon"], "zone": "America/Denver"},
                    "zone": "America/Denver"}
    pg.execute("UPDATE spine_asks SET carried_profile = %s WHERE ask_id = %s", (json.dumps(rode), a1))
    assert "(it rode here with the ask, from their home cell)" in profile.seat_words(pg, a1)
    assert profile.place_for_ask(pg, a1)["lat"] == BOULDER["lat"]
    assert profile.carry(pg, stranger) is None                            # nothing told, nothing carried


def test_the_clock_reads_the_profile_ahead_of_the_dial(pg, monkeypatch):
    _scope(monkeypatch)
    monkeypatch.setenv("SPINE_HUMAN_ZONE", "Europe/Paris")
    a = _ask(pg, "what time is it?")
    assert resident.human_zone(pg, a) == "Europe/Paris"                   # the dial, with nothing told
    profile.say(pg, ME, "I live in Boulder, Colorado", geocoder=_geo)
    assert resident.human_zone(pg, a) == "America/Denver"                 # the told place's clock, observed
    profile.say(pg, ME, "my clock is America/Phoenix", geocoder=None)
    assert resident.human_zone(pg, a) == "America/Phoenix"                # the told zone outranks the observed
    b = _ask(pg, "what time is it?", zone="Asia/Tokyo")
    assert resident.human_zone(pg, b) == "Asia/Tokyo"                     # the ask's own zone (the browser's) outranks all
    c = _ask(pg, "echo, say GULL", person="did:orreth:person:visitor")
    pg.execute("UPDATE spine_asks SET carried_profile = %s WHERE ask_id = %s", (json.dumps({"zone": "Europe/Rome"}), c))
    assert resident.human_zone(pg, c) == "Europe/Rome"                    # what rode with a routed ask


def test_the_weather_tool_reads_the_askers_own_place_and_says_so_when_there_is_none(pg, monkeypatch):
    _scope(monkeypatch)
    calls = []

    class _R:
        def __init__(self, url): self.url = url
        def __enter__(self): return self
        def __exit__(self, *a): return False
        def read(self): return json.dumps({"current": {"temperature_2m": 61.2, "apparent_temperature": 59.0}}).encode()

    monkeypatch.setattr(tools.urllib.request, "urlopen", lambda url, timeout=10: calls.append(url) or _R(url))
    a = _ask(pg, "what is the temperature outside?")
    door = tools.ToolDoor(pg, did="did:orreth:agent:test-librarian", capabilities=["tools:weather"], name="librarian", ask=a, chain=[ME])
    assert door.call("weather", {}) == tools.NO_PLACE_WORDS and calls == []
    profile.say(pg, ME, "I live in Boulder, Colorado", geocoder=_geo)
    out = door.call("weather", {})
    assert out == "Right now in Boulder, Colorado (your place, from your profile) it is 61.2°F outside (feels like 59.0°F)."
    assert "latitude=40.01499&longitude=-105.27055" in calls[-1]
    assert door.call("weather", {"latitude": 1.5, "longitude": 2.5}).startswith("Right now at 1.50,2.50 it is")
    profile.say(pg, ME, "my place is Nowhere Special", geocoder=_geo)
    assert door.call("weather", {}) == tools.NO_COORDS_WORDS.format(place="Nowhere Special")
    cur = pg.cursor()
    cur.execute("SELECT count(*) FROM spine_tool_calls WHERE ask = %s AND ok", (a,))
    assert cur.fetchone()[0] == 4                                          # every hop journaled, the refusals in words are honest answers


def test_the_doors_serve_the_profile(rig):
    """`GET /profile` is the portrait; `POST /profile` reads the words —
    a tell (201), a read (200), a forgetting (201), nothing (400)."""
    person = "did:orreth:person:door-" + secrets.token_hex(2)
    code, p = _post(rig.port, "/profile", {"person": person, "text": "my name is Door"})
    assert code == 201 and p["act"] == "tell" and p["portrait"]["name"] == "Door"
    code, p = _post(rig.port, "/profile", {"person": person, "text": "what do you know about me?"})
    assert code == 200 and p["act"] == "read" and p["words"] == "you told me: your name is Door"
    st, body = _get(rig.port, f"/profile?person={person}")
    assert st == 200 and json.loads(body)["name"] == "Door" and json.loads(body)["claims"][0]["label"] == "you told me"
    req = urllib.request.Request(f"http://127.0.0.1:{rig.port}/profile", data=json.dumps({"person": person, "text": "hello there"}).encode(),
                                 headers={"content-type": "application/json"}, method="POST")
    with pytest.raises(urllib.error.HTTPError) as e:
        urllib.request.urlopen(req, timeout=10)
    assert e.value.code == 400 and "tell me nothing about you" in json.loads(e.value.read())["error"]
    code, p = _post(rig.port, "/profile", {"person": person, "text": "forget my name"})
    assert code == 201 and p["act"] == "forget" and p["portrait"]["name"] is None
