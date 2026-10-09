# PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — THE GROUND CONNECTIONS CURE (JB's word 2026-10-08) · 2026-10-08
"""THE GROUND CONNECTIONS CURE (JB, 2026-10-08: "we must ensure that our architecture
continues to scale as we expand"). The finding: the crew of 11 lit and idle, the ground
held 37 connections — two per body (its serve line and its working memory's), whether it
served or slept — and the Python suite beside the lit kernel died three times of "too
many clients". The cure: a body holds a ground line only while it SERVES (taken when a
command lands on its bench, let go after a short idle, the working memory's line with it)
and keeps its lease on a cadence with a line it opens and closes; the ground DECLARES how
many bodies it can seat so that every one of them could serve at once, and placement
refuses the body past that budget at birth, in words, recorded; and the lines the ground
holds are a watchable metric with the kernel's own watch beside the five.

What this proves on the reference: an idle body holds no line and still renews; a served
command takes the line (two, named on the ground — the body's and its memory's) and the
idle release lets both go; the seat budget's law pure and at the join (the refusal in words,
the record, the same self never counting itself); the metric reads and the ground's card
says the budget; the kernel's sixth watch is the ground's."""
import secrets
import time
from pathlib import Path

import pytest

from orreth_spine import dispatch, ground, monitor, operating, outbox, placement, presence, resident, sinks
from orreth_spine.rails import PG_DSN

from tests.test_mind import _rails_up  # noqa: E402

SPINE = Path(__file__).resolve().parents[1]
POLICY = SPINE / "policy" / "covenant-policy.v1.json"
ECHO = SPINE / "templates" / "echo-resident.v0.json"
LIBRARIAN = SPINE / "templates" / "librarian-resident.v0.json"
ME = "did:orreth:person:test"
rails = pytest.mark.skipif(not _rails_up(), reason="the rails are not up")
# the suite's ground is the throwaway schema the `pg` fixture stands on; a line the body opens for itself
# must stand there too (in the world, every line shares the one search_path)
DSN = PG_DSN + ("&" if "?" in PG_DSN else "?") + "options=-c%20search_path%3Dspine_test"


def _scope(monkeypatch):
    monkeypatch.setenv("SPINE_SCOPE", "u:lines-" + secrets.token_hex(3))


def _body(template, home):
    r = resident.Resident(template, home=home)
    r.load_policy(POLICY)
    return r


def _lines_of(pg, name: str) -> int:
    """The ground's own count of the lines a body holds — every connection named for it."""
    cur = pg.cursor()
    cur.execute("SELECT count(*) FROM pg_stat_activity WHERE datname = current_database()"
                " AND application_name LIKE %s", (f"orreth body {name}%",))
    return int(cur.fetchone()[0])


# ---- the law, pure ----------------------------------------------------------------------

def test_the_seat_budget_is_the_ceiling_less_the_reserve_in_lines_per_serving_body(monkeypatch):
    """Postgres's stock 100, the kernel's 30, two lines a serving body: 35 seats. A ground
    narrower than the reserve seats none. The dial narrows the ground, never widens it;
    the refusal names the arithmetic in a newcomer's words."""
    assert placement.seats_budget(100, 30) == 35 and placement.seats_budget(20, 30) == 0
    assert placement.seats_budget(33, 30, 2) == 1
    c = placement.connections_declared({})
    assert c == {"ceiling": 100, "reserve": 30, "per_body": 2, "seats": 35}
    assert placement.connections_declared({"SPINE_GROUND_CONNECTIONS": "32"})["seats"] == 1
    assert placement.connections_declared({"SPINE_GROUND_CONNECTIONS": "-5", "SPINE_GROUND_RESERVE": "x"}) == c
    ok, reasons = placement.seat_honor(c, 34)
    assert ok and reasons == []
    ok, reasons = placement.seat_honor(c, 35)
    assert not ok and reasons == ["the ground seats 35 bodies at once — its ceiling of 100 connections less the "
                                  "kernel's 30, 2 lines per serving body — and 35 are seated already"]
    one = placement.connections_declared({"SPINE_GROUND_CONNECTIONS": "32"})
    assert placement.seat_honor(one, 1)[1] == ["the ground seats 1 body at once — its ceiling of 32 connections less "
                                              "the kernel's 30, 2 lines per serving body — and 1 is seated already"]
    # the ground declaring itself carries the budget; the honor rule is untouched by it
    g = placement.ground_declares({"SPINE_GROUND_CONNECTIONS": "40"})
    assert g["connections"]["seats"] == 5 and placement.honor(placement.profile({}), g) == (True, [])
    # the kernel's sixth watch: red at the ceiling less the reserve — the bodies' share spent
    assert operating.ground_watch(c) == {"name": "ground_connections", "metric": "ground_connections",
                                         "op": ">=", "threshold": 70.0}
    assert "ground_connections" in monitor.METRICS and len(monitor.METRICS) == 22      # Phase 8 sp6: key_checks_failed joined


# ---- the ground's own ceiling, the metric, the card ---------------------------------------

def test_the_ground_reads_its_own_ceiling_and_the_monitor_counts_its_lines(pg, monkeypatch):
    _scope(monkeypatch)
    ground.ensure_all(pg)                                                  # every ground, before the snapshot reads it
    monkeypatch.delenv("SPINE_GROUND_CONNECTIONS", raising=False)
    pg_max = placement.max_connections(pg)
    assert pg_max and pg_max >= 10
    declared = placement.connections_declared(conn=pg)
    assert declared["ceiling"] == min(pg_max, 100) and declared["seats"] == (declared["ceiling"] - 30) // 2
    monkeypatch.setenv("SPINE_GROUND_CONNECTIONS", str(pg_max + 500))     # a dial wider than the ground: the ground's word stands
    assert placement.connections_declared(conn=pg)["ceiling"] == pg_max
    monkeypatch.setenv("SPINE_GROUND_CONNECTIONS", "36")                   # a dial narrower: it narrows
    assert placement.connections_declared(conn=pg) == {"ceiling": 36, "reserve": 30, "per_body": 2, "seats": 3}
    monkeypatch.delenv("SPINE_GROUND_CONNECTIONS")
    snap = monitor.snapshot(pg, rails=False)
    assert snap["values"]["ground_connections"] >= 1                       # this test's own line, at least
    assert snap["ground"]["connections"] == snap["values"]["ground_connections"]
    assert snap["ground"]["seats"] == declared["seats"] and snap["ground"]["seated"] == 0
    # the kernel's watches at light: the five and the ground's, once
    made = operating.watches_at_light(pg)
    assert made[-2] == "ground_connections" and made[-1] == "key_checks_failed" and operating.watches_at_light(pg) == []   # Phase 8 sp6: the seventh after the sixth
    w = {x["metric"]: x for x in monitor.snapshot(pg, rails=False)["watches"]}["ground_connections"]
    assert (w["op"], w["threshold"], w["red"]) == (">=", float(declared["ceiling"] - 30), False)
    assert w["reads"].startswith("red when ground_connections >= ")


# ---- the seat budget at the join -------------------------------------------------------------

def test_a_body_past_the_seats_is_refused_at_birth_in_words_and_the_same_self_never_counts_itself(pg, monkeypatch, tmp_path):
    _scope(monkeypatch)
    monkeypatch.setenv("SPINE_GROUND_CONNECTIONS", "32")                   # 32 − 30 = 2 lines: ONE seat
    first = _body(ECHO, tmp_path / "a")
    assert first.join(pg)["life"] == 1
    presence.renew(pg, first.identity.did, first.name, first.kind)         # alive — the seat is taken
    assert presence.seated_now(pg) == 1 and presence.seated_now(pg, exclude_did=first.identity.did) == 0
    second = _body(LIBRARIAN, tmp_path / "b")
    with pytest.raises(resident.PlacementRefused) as e:
        second.join(pg)
    assert e.value.reasons == ["the ground seats 1 body at once — its ceiling of 32 connections less the kernel's 30, "
                               "2 lines per serving body — and 1 is seated already"]
    cur = pg.cursor()
    cur.execute("SELECT count(*) FROM spine_joins WHERE did = %s", (second.identity.did,))
    assert cur.fetchone()[0] == 0                                          # never joined, never started
    r = placement.refusals(pg)["librarian"]
    assert r["reasons"] == e.value.reasons and r["ground"] == {"cell": "local", "metal": "cpu", "seats": 1}
    # the first body's NEXT LIFE is not counted against itself (rule 1: the same self, life 2)
    again = _body(ECHO, tmp_path / "a")
    assert again.identity.did == first.identity.did and again.join(pg)["life"] == 2
    # the ground widened by its keeper: the second joins as the same self that was refused
    monkeypatch.setenv("SPINE_GROUND_CONNECTIONS", "34")
    assert second.join(pg)["life"] == 1
    assert len(placement.refusals(pg)) == 1                                # the record stays: never a deletion


# ---- the line, held only while serving ------------------------------------------------------

@rails
def test_a_body_holds_a_ground_line_only_while_it_serves_and_keeps_its_lease_without_one(pg, monkeypatch, tmp_path):
    _scope(monkeypatch)
    r = _body(ECHO, tmp_path / "home")
    r.join(pg)
    # born: no line; the lease kept on a cadence with a line opened and closed for it
    assert not r.holds_line() and _lines_of(pg, "echo") == 0
    assert r.keep_lease(DSN, every_s=0) is True and not r.holds_line()
    assert r.keep_lease(DSN) is False                                  # inside the cadence: nothing to do
    assert {b["name"]: b["alive"] for b in presence.roster(pg)} == {"echo": True}
    assert _lines_of(pg, "echo") == 0                                      # the renew's line is gone
    # an empty bench: polled with NO ground connection
    r.serve_once(None, idle_s=0.3, max_commands=10)
    assert not r.holds_line() and _lines_of(pg, "echo") == 0
    # a command lands: the line is taken — two on the ground, the body's and its working memory's
    text = f"Marker {secrets.token_hex(3)}: say this back."
    ask_id = dispatch.submit_ask(pg, text, person=ME)
    assert outbox.drain(pg, sinks.KafkaSink()) >= 1
    tok = secrets.token_hex(4)
    assert dispatch.dispatch_once(pg, consumer=f"tc-{tok}", group=f"tc-{tok}")["applied"] >= 1
    cur = pg.cursor()
    end = time.monotonic() + 60
    while time.monotonic() < end:
        r.serve_once(None, idle_s=1.5, max_commands=200)
        cur.execute("SELECT status, reply FROM spine_asks WHERE ask_id = %s", (ask_id,))
        row = cur.fetchone()
        if row and row[0] == "replied":
            break
    assert row and row[0] == "replied" and text in row[1]
    assert r.holds_line() and r._ckpt_conn is not None and r._serve_conn is r._line
    assert _lines_of(pg, "echo") == 2
    # warm for the idle window, then let go — the memory's line with it; the next serve opens afresh
    assert r.release_line(idle_s=60) is False and r.holds_line()
    assert r.release_line(idle_s=0) is True and not r.holds_line()
    assert r._ckpt_conn is None and r._ckpt_graph is None and r._serve_conn is None
    assert _lines_of(pg, "echo") == 0
    assert r.release_line() is False
    # the lease rides the held line while it stands
    r.hold_line(DSN)
    assert r.keep_lease(DSN, every_s=0) is True and _lines_of(pg, "echo") == 1
    r.release_line()
    assert _lines_of(pg, "echo") == 0
