# PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P4 sp5, the scheduler · 2026-09-18
# Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P6 cure sp3: the bare occurrence text replaced by W21's duty framing (walk #8) · 2026-09-21
# Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp4: the beat lock — two kernels on one ground, one beat at a time · 2026-09-23
"""The scheduler (0004: three schedulers, one body; P16 every schedule
lives in its runner; covenant rule 11: the human can always stop what
the machine manages). AG-4: a kernel duty and a role intention both in
the card; the kernel one refuses edit; CRUD on the human one changes
the Operating State. AG-6's scheduled half: the kernel runs the harness."""
import json
import secrets
import urllib.request
from pathlib import Path

import pytest

from orreth_spine import dispatch, gateway, glass, harness, resident, scheduler

from tests.test_conformance import _dials  # noqa: E402
from tests.test_mind import _rails_up  # noqa: E402

SPINE = Path(__file__).resolve().parents[1]
POLICY = SPINE / "policy" / "covenant-policy.v1.json"
ME = "did:orreth:person:test"
rails = pytest.mark.skipif(not _rails_up(), reason="the rails are not up")


def _body(template, gw=None):
    r = resident.Resident(SPINE / "templates" / template, gateway=gw)
    r.load_policy(POLICY)
    return r


def test_a_human_schedule_occurs_as_an_ask_on_the_rail_and_rests_on_record(pg, monkeypatch):
    monkeypatch.setenv("SPINE_SCOPE", "u:law-" + secrets.token_hex(3))
    sid = scheduler.add(pg, "echo", "human", "say the time, please", every_s=60, by=ME)
    occurred = scheduler.tick(pg)
    assert [o["schedule_id"] for o in occurred] == [sid]
    ask = glass.ask_view(pg, occurred[0]["ref"])         # the occurrence IS an ask
    # W21 (walk #8): the occurrence is FRAMED as a duty — the words, the cadence, the window, the notes
    assert ask["text"].startswith("“say the time, please” — your duty every 1 minute (every 60 s) · your first run")
    assert ask["target"] == "echo" and ask["person"] == ME
    assert scheduler.tick(pg) == []                      # not due again yet
    card = scheduler.for_runner(pg, "echo")
    [h] = card["human"]
    assert h["occurrences"] == 1 and h["active"] and h["editable"] and h["last_at"]
    scheduler.rest(pg, sid, by=ME)                       # the human's stop:
    [h] = scheduler.for_runner(pg, "echo")["human"]      # recorded, never deleted
    assert h["active"] is False and h["rested_by"] == ME and h["rested_at"]
    pg.cursor().execute("UPDATE spine_schedules SET next_at = now() WHERE schedule_id = %s", (sid,))
    assert scheduler.tick(pg) == []                      # at rest, it never occurs


def test_the_beat_belongs_to_one_kernel_at_a_time(pg, monkeypatch):
    """P7 sp4, the loops' shadow law: two kernels stand on one ground (the
    Python Bridge and the Rust bridge, in shadow) and both run the
    scheduler's tick and the intent rail's turn. A beat is CLAIMED on the
    ground first — `pg_try_advisory_lock(class, hashtext(scope))` — so
    while one kernel's beat holds, the other's tick returns nothing and
    the other's turn says so; the lock is per world (another scope beats
    freely) and per class (the intent beat is not the scheduler's); a
    dropped connection drops the lock."""
    import psycopg
    from orreth_spine import ground, intent
    from tests.conftest import DSN
    monkeypatch.setenv("SPINE_SCOPE", "u:law-" + secrets.token_hex(3))
    sid = scheduler.add(pg, "echo", "human", "say the time, please", every_s=60, by=ME)
    other = psycopg.connect(DSN, autocommit=True)                     # the other kernel's connection
    other.execute("SET search_path TO spine_test")
    try:
        assert ground.try_beat(other, "scheduler")                    # the other kernel holds the beat
        assert scheduler.tick(pg) == []                               # ours steps back: nothing occurred
        [h] = scheduler.for_runner(pg, "echo")["human"]
        assert h["occurrences"] == 0 and h["last_at"] is None         # the row untouched, still due
        assert intent.turn(pg)["observed"] == []                      # the intent beat is its own class:
        assert "beat" not in intent.turn(pg)                          # ours to run while they hold the scheduler's
        assert ground.try_beat(other, "intent")
        assert intent.turn(pg) == {"observed": [], "due": [], "filed": [], "heard": [], "beat": ground.HELD}
        ground.end_beat(other, "intent")
        with _dials(SPINE_SCOPE="u:law-elsewhere"):                  # another world beats freely
            assert ground.try_beat(pg, "scheduler") and ground.end_beat(pg, "scheduler") is None
        ground.end_beat(other, "scheduler")                           # released: the beat is ours again
        occurred = scheduler.tick(pg)
        assert [o["schedule_id"] for o in occurred] == [sid]
        assert scheduler.for_runner(pg, "echo")["human"][0]["occurrences"] == 1
        assert ground.try_beat(other, "scheduler")                    # a dying kernel drops its lock
        other.close()
        assert scheduler.tick(pg) == []                               # (not due again — nothing to do)
        assert ground.try_beat(pg, "scheduler")                       # but the beat is claimable at once
        ground.end_beat(pg, "scheduler")
    finally:
        if not other.closed:
            other.close()


def test_a_kernel_schedule_refuses_edit_with_one_plain_face(pg, monkeypatch):
    monkeypatch.setenv("SPINE_SCOPE", "u:law-" + secrets.token_hex(3))
    sid = scheduler.declared(pg, "librarian", "kernel", "run the harness against my golden set", 1800, "the kernel")
    assert scheduler.declared(pg, "librarian", "kernel", "run the harness against my golden set", 1800, "the kernel") == sid
    [k] = scheduler.for_runner(pg, "librarian")["kernel"]
    assert k["editable"] is False
    with pytest.raises(scheduler.KernelRequired, match="never editable"):
        scheduler.rest(pg, sid, by=ME)
    assert scheduler.for_runner(pg, "librarian")["kernel"][0]["active"] is True


def test_a_role_schedule_declared_by_the_template_lives_in_the_card_and_the_kernel_runs_the_harness(pg, monkeypatch):
    """AG-4 + AG-6's scheduled half, together: the librarian's template
    declares a role intention (registered once at every join); the kernel
    declares the harness duty; a beat runs the harness through the body
    and records the run as the occurrence."""
    monkeypatch.setenv("SPINE_SCOPE", "u:law-" + secrets.token_hex(3))
    lib = _body("librarian-resident.v0.json", gateway.FakeGateway(
        reply="PELICAN — I am the librarian."))
    lib.join(pg); lib.join(pg)                           # two lives, one intention
    card = scheduler.for_runner(pg, "librarian")
    assert len(card["role"]) == 1 and "worth remembering" in card["role"][0]["text"]
    scheduler.declared(pg, "librarian", "kernel", "run the harness against my golden set", 1800, "the kernel")
    pg.cursor().execute("UPDATE spine_schedules SET next_at = now() WHERE runner = 'librarian'")
    occurred = {o["kind"]: o for o in scheduler.tick(pg, {"librarian": lib})}
    assert set(occurred) == {"role", "kernel"}
    assert occurred["kernel"]["ref"].startswith("run_")   # the harness ran
    assert glass.ask_view(pg, occurred["role"]["ref"])["target"] == "librarian"
    cur = pg.cursor()
    cur.execute("SELECT passed, failed FROM spine_harness_runs WHERE run_id = %s", (occurred["kernel"]["ref"],))
    assert cur.fetchone() == (2, 0)


@rails
def test_the_schedule_doors_over_http_and_the_organ_beats_in_the_rig(pg, rig):
    """CRUD on the human schedule through the door; the kernel one refuses
    with 403 and plain words; the card's side B over HTTP."""
    port = rig.port
    def post(path, obj):
        req = urllib.request.Request(f"http://127.0.0.1:{port}{path}", data=json.dumps(obj).encode(),
                                     headers={"content-type": "application/json"}, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=10) as r:
                return r.status, json.loads(r.read())
        except urllib.error.HTTPError as e:
            return e.code, json.loads(e.read())
    s, made = post("/schedules", {"runner": "echo", "text": "echo the hour", "every_s": 3600})
    assert s == 201 and made["schedule_id"].startswith("sch_")
    with urllib.request.urlopen(f"http://127.0.0.1:{port}/schedules/librarian", timeout=10) as r:
        card = json.loads(r.read())
    assert card["kernel"] and card["kernel"][0]["editable"] is False       # the rig declared it
    assert card["role"] and "worth remembering" in card["role"][0]["text"]  # the template's
    s, body = post("/schedules/rest", {"schedule_id": card["kernel"][0]["schedule_id"]})
    assert s == 403 and "never editable" in body["error"]
    s, body = post("/schedules/rest", {"schedule_id": made["schedule_id"]})
    assert s == 202
