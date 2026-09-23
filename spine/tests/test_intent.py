# PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch intent sp1, the fifth firmware-rail · 2026-09-19
# Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P6 cure sp1 (kernel): IH-1 under the watch's sense (W14), the runner joined (W19), the human's stop held (W5) · 2026-09-21
# Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch walk #11 cures: W35 a stop asked is a stop held · W37 a duplicate purpose named at the door · W38 the honest word in more shapes · W40 standing intentions never off the board · 2026-09-23
"""The intent loop (canon 0007, block 11): an intention is a record with
a root marker; the loop observes (a red watch), asks the planner under
the observation, and files the planner's reply as an objective under the
intention — in its session; the stop ends it (rule 11). The ask wears
its kind (P23). The Analyzer is a projection (P25) — flat at 10k."""
import json
import secrets
import statistics
import time
import urllib.request
from pathlib import Path

import pytest

from orreth_spine import dispatch, envelope as ev, gateway, glass, intent, markers, monitor, resident

from tests.test_mind import _rails_up  # noqa: E402

SPINE = Path(__file__).resolve().parents[1]
POLICY = SPINE / "policy" / "covenant-policy.v1.json"
ME = "did:orreth:person:test"
rails = pytest.mark.skipif(not _rails_up(), reason="the rails are not up")


def _body(template, gw=None):
    r = resident.Resident(SPINE / "templates" / template, gateway=gw)
    r.load_policy(POLICY)
    return r


def _events_for(pg, ref):
    cur = pg.cursor()
    cur.execute("SELECT body FROM spine_outbox WHERE convert_from(body, 'UTF8') LIKE %s", (f"%{ref}%",))
    return [ev.decode(bytes(b)) for (b,) in cur.fetchall()]


def _marker_of(pg, ask_id):
    cur = pg.cursor(); cur.execute("SELECT marker FROM spine_asks WHERE ask_id = %s", (ask_id,))
    return cur.fetchone()[0]


def test_ih1_a_red_watch_turns_the_resiliency_loop_and_the_stop_ends_it(pg, monkeypatch):
    """IH-1: Resiliency declared with its stop; a watch goes red; the
    observation lands under Resiliency; the planner is asked under it and
    answers; the reply is filed as an objective to the crew, parent =
    Resiliency, in its session; the tree reads from either end; the stop
    is recorded and the loop does not turn again."""
    monkeypatch.setenv("SPINE_SCOPE", "u:law-" + secrets.token_hex(3))
    planner = _body("firmware-planner.v0.json",
                    gateway.FakeGateway(reply="Serve the waiting ask and confirm the bench is drained."))
    planner.join(pg); planner._serve_conn = pg
    _body("librarian-resident.v0.json").join(pg)      # W19: the runner must be HERE, or the door refuses
    r = intent.declared(pg, intent.RESILIENCY["words"], serves="resiliency", kind="kernel",
                        by="the kernel", interests=intent.RESILIENCY["interests"],
                        planner="planner", runner="librarian")
    assert r["active"] and r["session"] and markers.get(pg, r["marker"])["kind"] == "intention"
    assert intent.declared(pg, intent.RESILIENCY["words"], kind="kernel")["intention_id"] == r["intention_id"]
    assert any(e["type"] == intent.INTENTION_DECLARED and e["marker"]["id"] == r["marker"]
               for e in _events_for(pg, r["intention_id"]))                        # a fact on the rail
    monitor.add_watch(pg, "asks left waiting", "asks_received", ">", 0, by=ME)      # W14: red WHEN it holds
    assert intent.turn(pg)["observed"] == []                                        # green: nothing
    dispatch.submit_ask(pg, "one ask, unserved")                                    # now red
    t = intent.turn(pg)
    [obs] = t["observed"]
    o = markers.get(pg, obs)
    assert o["kind"] == "watch-red" and o["parent"] == r["marker"] and "went red" in o["note"]
    cur = pg.cursor()
    cur.execute("SELECT plan_ask, objective_ask FROM spine_intent_turns WHERE intention_id = %s",
                (r["intention_id"],))
    [(plan_ask, objective_ask)] = cur.fetchall()
    assert objective_ask is None
    pv = glass.ask_view(pg, plan_ask)
    assert pv["target"] == "planner" and pv["session"] == r["session"] and "OBSERVED" in pv["text"]
    assert [m["kind"] for m in markers.ancestry(pg, _marker_of(pg, plan_ask))] == ["thought", "watch-red", "intention"]
    assert intent.turn(pg)["observed"] == [] and intent.turn(pg)["filed"] == []    # still red: one turn per cause
    with pg.transaction():
        planner._serve_ask(pg.cursor(), plan_ask, ["the kernel"])                  # the planner answers
    t = intent.turn(pg)
    [f] = t["filed"]
    ov = glass.ask_view(pg, f["objective_ask"])
    assert ov["text"] == "Serve the waiting ask and confirm the bench is drained."
    assert ov["target"] == "librarian" and ov["session"] == r["session"] and ov["person"] == "the kernel"
    assert ov["origin"]["kind"] == "intention" and ov["origin"]["words"].startswith("keep this world resilient")
    assert [m["kind"] for m in markers.ancestry(pg, ov["marker"])] == ["objective", "intention"]
    under = {m["kind"] for m in markers.tree(pg, r["marker"])}
    assert under >= {"intention", "watch-red", "thought", "objective"}
    [row] = [i for i in intent.listing(pg) if i["intention_id"] == r["intention_id"]]
    assert row["objectives"] == 1 and row["observations"] == 1 and row["turns"] == 1
    from orreth_spine import proof
    with pytest.raises(proof.ProofRequired):                                         # P6 sp1: the kernel's own
        intent.stop(pg, r["intention_id"], by=ME)                                    # intention — grave, never bare
    stopped = intent.stop(pg, r["intention_id"], by=ME, proof="L3-master",           # rule 11, proven
                          confirmed_by="did:orreth:person:master")
    assert stopped["active"] is False and stopped["stopped_by"] == ME
    assert any(e["type"] == intent.INTENTION_STOPPED for e in _events_for(pg, r["intention_id"]))
    pg.cursor().execute("UPDATE spine_watches SET last_ok = true")                  # turns red again —
    assert intent.turn(pg)["observed"] == []                                        # nobody cares now
    assert intent.stop(pg, r["intention_id"], by=ME)["active"] is False             # one face, twice
    with pytest.raises(KeyError):
        intent.stop(pg, "int_nobody", by=ME)


def test_ih2_the_ask_wears_its_kind(pg, monkeypatch):
    """IH-2 / P23: the words propose the kind; a typed prefix is the flip
    and wins; the marker minted matches; an intention is declared, never
    asked, and needs something to wake it."""
    monkeypatch.setenv("SPINE_SCOPE", "u:law-" + secrets.token_hex(3))
    assert intent.read_words("what's the temperature outside?")["kind"] == "thought"
    assert intent.read_words("plan a migration of the ledger to postgres 17")["kind"] == "objective"
    rw = intent.read_words("keep this world resilient: when a watch goes red, get it green")
    assert rw["kind"] == "intention" and rw["serves"] == "resiliency" and rw["interests"] == ["watch-red"]
    rw = intent.read_words("every 2 hours, check the spend against the budget")
    assert rw["kind"] == "intention" and rw["serves"] == "cost" and rw["every_s"] == 7200
    rw = intent.read_words("objective:  say hi to the crew")
    assert rw == {"kind": "objective", "words": "say hi to the crew", "pinned": True}
    ses = glass.open_session(pg, ME)
    obj = dispatch.submit_ask(pg, "plan the move", person=ME, session=ses)
    th = dispatch.submit_ask(pg, "why that order?", person=ME, session=ses, kind="thought")
    assert markers.get(pg, _marker_of(pg, th))["kind"] == "thought"
    assert markers.get(pg, _marker_of(pg, th))["parent"] == _marker_of(pg, obj)      # under the session's objective
    with pytest.raises(ValueError, match="declared"):
        dispatch.submit_ask(pg, "keep it green", person=ME, kind="intention")
    with pytest.raises(ValueError, match="wake it"):
        intent.declare(pg, "be excellent", serves="business", kind="human", by=ME)
    with pytest.raises(markers.UnknownKind, match="declare it first"):
        intent.declare(pg, "watch the vibe", serves="business", kind="human", by=ME, interests=["vibe"])
    made = intent.declare(pg, "when an improvement is marked, plan its landing", serves="business",
                          kind="human", by=ME, interests=["improvement"])
    assert made["kind"] == "human" and made["interests"] == ["improvement"]
    critic = _body("firmware-critic.v0.json"); critic.join(pg)
    _body("firmware-planner.v0.json").join(pg)                          # W19: the planner must be here
    ask = dispatch.submit_ask(pg, "what binds hempcrete?", person=ME, session=ses)
    m = markers.set_marker(pg, "improvement", ref=ask, by=ME, parent=_marker_of(pg, ask), note="lime")
    asked = markers.dispatch_interests(pg, m, ask, "lime")                          # bodies AND intentions
    assert [a["body"] for a in asked] == ["critic", "planner"] and asked[1]["intention"] == made["intention_id"]
    assert [x["kind"] for x in markers.ancestry(pg, _marker_of(pg, asked[1]["ask_id"]))] == ["thought", "improvement", "objective"]


def test_ih3_the_analyzer_is_a_projection_flat_at_10k_markers(pg, monkeypatch):
    """IH-3 / P25: origins answer from the ground alone — under 100 ms at
    10k markers, flat against 1k — and an origin's tree is the tree."""
    monkeypatch.setenv("SPINE_SCOPE", "u:law-" + secrets.token_hex(3))
    markers.seed(pg)
    def bulk(roots, kids):
        rows = []
        for i in range(roots):
            rid = markers.new_id()
            rows.append((rid, "objective", None, "ask_" + secrets.token_hex(4), ME, None, ev.scope(), rid))
            for j in range(kids):
                rows.append((markers.new_id(), "action" if j % 2 else "thought", rid, "x" + secrets.token_hex(3),
                             ME, None, ev.scope(), rid))
        with pg.transaction():
            pg.cursor().executemany(
                "INSERT INTO spine_markers (marker_id, kind, parent, ref, by_did, note, scope, root)"
                " VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", rows)
    def median(fn, k=7):
        ts = []
        for _ in range(k):
            t0 = time.perf_counter(); fn(); ts.append(time.perf_counter() - t0)
        return statistics.median(ts)
    bulk(20, 49)                                                     # 1k
    t1k = median(lambda: markers.origins(pg))
    bulk(180, 49)                                                    # 10k
    pg.cursor().execute("ANALYZE spine_markers")
    t10k = median(lambda: markers.origins(pg))
    out = markers.origins(pg)
    print(f"\nIH-3 origins: 1k {t1k*1000:.1f} ms → 10k {t10k*1000:.1f} ms")
    assert len(out) == 60 and out[0]["counts"] == {"action": 24, "thought": 25}
    assert t10k < 0.1 and t10k < max(3 * t1k, 0.02)
    tree = markers.origin(pg, out[0]["root"])["tree"]
    assert len(tree) == 50 and tree[0]["id"] == out[0]["root"]


def test_every_ground_is_ensured_at_birth_never_inside_a_serve(pg, monkeypatch):
    """The law found live at the sp1 relight: a connection flags EVERY
    ground when it is born, so no serving transaction ever runs DDL (a
    new column's exclusive lock inside one serve's savepoint wedged the
    whole Bridge for five minutes)."""
    monkeypatch.setenv("SPINE_SCOPE", "u:law-" + secrets.token_hex(3))   # a world of its own
    from orreth_spine import ground
    ground.ensure_all(pg)
    assert ground.ensured(pg) >= set(ground.TAGS)
    # the memo (2026-09-21): a connection BORN to this ground after it was
    # ensured is born flagged — a door's fresh connection never runs DDL
    # inside a request (CI: two fan-out asks deadlocked a serving resident)
    import psycopg
    from orreth_spine import outbox
    from tests.conftest import DSN
    with psycopg.connect(DSN, autocommit=True) as born:
        born.execute("SET search_path TO spine_test")
        assert outbox.ground_key(born) == outbox.ground_key(pg)
        assert not outbox.once(born, "resident"), "born flagged, no DDL"
        assert not outbox.once(born, "markers")
    with psycopg.connect(DSN, autocommit=True) as other:   # another ground
        other.execute("SET search_path TO public")
        assert outbox.ground_key(other) != outbox.ground_key(pg)
        assert outbox.once(other, "test-only-tag"), "a new ground ensures once"
    missing = set(ground.TAGS) - ground.ensured(pg)
    assert not missing, missing
    cur = pg.cursor()
    cur.execute("SELECT count(*) FROM spine_markers WHERE root IS NULL")   # the backfill left none
    assert cur.fetchone()[0] == 0


@rails
def test_the_intent_doors_and_the_rail_in_the_rig(pg, rig):
    """Over HTTP, in the standing rig: Resiliency stands at boot; the
    Analyzer lists it as an origin; an ask wears the chip's kind; an
    intention typed in the chat is declared; a human's stops with 202."""
    port = rig.port
    def get(path):
        with urllib.request.urlopen(f"http://127.0.0.1:{port}{path}", timeout=10) as r:
            return json.loads(r.read())
    def post(path, obj):
        req = urllib.request.Request(f"http://127.0.0.1:{port}{path}", data=json.dumps(obj).encode(),
                                     headers={"content-type": "application/json"}, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=10) as r:
                return r.status, json.loads(r.read())
        except urllib.error.HTTPError as e:
            return e.code, json.loads(e.read())
    t0 = time.perf_counter()
    for _ in range(150):                                             # the rail declares at boot —
        ints = [i for i in get("/intentions")["intentions"] if i["kind"] == "kernel"]
        if ints:                                                     # behind 7 checkpointer setups
            break                                                    # and 12 × 14 schema guards
        time.sleep(0.2)                                              # on a fresh ground
    print(f"\nthe rail declared Resiliency {time.perf_counter() - t0:.1f}s after the rig was ready")
    assert ints, "the intent rail never declared Resiliency in the rig's world"
    [res] = ints
    assert res["words"].startswith("keep this world resilient") and res["active"] and res["runner"] == "librarian"
    origins = get("/analyzer")["origins"]
    [o] = [o for o in origins if o["ref"] == res["intention_id"]]
    assert o["kind"] == "intention" and o["origin_kind"] == "kernel" and o["active"] is True
    kind_of = lambda aid: get("/markers?from=" + get(f"/ask/{aid}")["marker"])["ancestry"][0]["kind"]
    s, body = post("/ask", {"text": "why is the sky blue?", "to": ["echo"], "kind": "thought"})
    assert s == 201 and kind_of(body["ids"][0]) == "thought"                     # the chip's word
    s, body = post("/ask", {"text": "objective: say hi", "to": ["echo"], "kind": "thought"})   # the prefix wins
    assert s == 201 and get(f"/ask/{body['ids'][0]}")["text"] == "say hi"
    assert kind_of(body["ids"][0]) == "objective"
    s, body = post("/ask", {"text": "be excellent", "kind": "intention"})
    assert s == 400 and "wake it" in body["error"]
    walker = "did:orreth:person:intent-walker"                         # enrolled here, never jb (test_proof's)
    s, body = post("/ask", {"text": "when an improvement is marked, plan its landing", "kind": "intention",
                            "person": walker})
    assert s == 201 and body["intention"]["kind"] == "human" and body["intention"]["interests"] == ["improvement"]
    iid = body["intention"]["intention_id"]
    assert any(i["intention_id"] == iid for i in get("/intentions?kind=human")["intentions"])
    s, body = post("/intentions/stop", {"intention_id": iid, "person": walker})   # W5: a human's stop is
    assert s == 202 and body["level"] == "L3-code" and body["held"].startswith("ask_")   # HELD for the code
    held = body["held"]
    assert get(f"/ask/{held}")["hold"]["level"] == "L3-code" and "This needs your code" in get(f"/ask/{held}")["reply"]
    assert [i for i in get("/intentions?kind=human")["intentions"] if i["intention_id"] == iid][0]["active"] is True
    from orreth_spine import proof
    s, made = post("/enroll", {"person": walker})
    assert s == 201 and post("/enroll/confirm", {"person": walker, "code": proof.totp(made["secret"])})[0] == 200
    assert post("/confirm", {"ask_id": held, "approve": True, "by": walker, "code": "000000"})[0] == 403   # one face
    s, out = post("/confirm", {"ask_id": held, "approve": True, "by": walker, "code": proof.totp(made["secret"])})
    assert s == 202 and out["level"] == "L3-code"                                    # the right code rests it
    assert [i for i in get("/intentions?kind=human")["intentions"] if i["intention_id"] == iid][0]["active"] is False
    assert get(f"/ask/{held}")["proof"] == "L3-code" and get(f"/ask/{held}")["reply"].startswith("Done, on your code")
    s, _ = post("/intentions/stop", {"intention_id": "int_nobody"})
    assert s == 404
    tree = get(f"/analyzer?origin={o['root']}")["tree"]
    assert tree and tree[0]["kind"] == "intention" and tree[0]["words"].startswith("keep this world")


def test_walk11_a_stop_asked_is_a_stop_held_a_duplicate_is_named_and_a_standing_intention_stays_on_the_board(pg, monkeypatch):
    """Walk #11's kernel cures. W35: while an intention's stop waits at the
    interlock (held for the code), the loop files nothing new for it — its
    cadence sleeps, its red is not observed, its replied plan is not filed;
    a cancel resumes it. W37: a human intention with words that already
    stand (the kernel's, or the human's own) is refused at the door in
    words. W38: "I cannot …" / "I don't have a tool" are heard as the
    honest word. W40: the Analyzer's origins keep every standing
    intention's root, however many newer roots there are."""
    from orreth_spine import proof
    monkeypatch.setenv("SPINE_SCOPE", "u:law-" + secrets.token_hex(3))
    planner = _body("firmware-planner.v0.json", gateway.FakeGateway(reply="Drain the bench."))
    planner.join(pg); planner._serve_conn = pg
    _body("librarian-resident.v0.json").join(pg)
    kern = intent.declared(pg, intent.RESILIENCY["words"], serves="resiliency", kind="kernel",
                           by="the kernel", interests=intent.RESILIENCY["interests"], planner="planner", runner="librarian")
    # W37: the same words, declared by a human — named at the door
    with pytest.raises(ValueError, match="already stands — the kernel's"):
        intent.declare(pg, intent.RESILIENCY["words"], serves="resiliency", kind="human", by=ME,
                       interests=intent.RESILIENCY["interests"])
    mine = intent.declare(pg, "say the time every 5 seconds", serves="business", kind="human", by=ME,
                          every_s=5, runner="librarian")
    with pytest.raises(ValueError, match="already stands — your own"):
        intent.declare(pg, "say the time  every 5 seconds", serves="business", kind="human", by=ME, every_s=5)
    # W35: the cadence beats …
    pg.cursor().execute("UPDATE spine_intentions SET next_at = now() WHERE intention_id = %s", (mine["intention_id"],))
    t = intent.turn(pg)
    assert [d["intention_id"] for d in t["due"]] == [mine["intention_id"]]
    # … until its stop is HELD for the code: then nothing new, though it is due and its plan was answered
    held = proof.hold_kernel_act(pg, text="stopping your intention", person=ME, tool="intent.stop",
                                 args={"intention_id": mine["intention_id"]}, level="L3-code")
    assert intent.held_stops(pg) == {mine["intention_id"]}
    [(plan_ask,)] = pg.execute("SELECT plan_ask FROM spine_intent_turns WHERE intention_id = %s", (mine["intention_id"],)).fetchall()
    with pg.transaction():
        planner._serve_ask(pg.cursor(), plan_ask, ["the kernel"])      # the planner answered
    pg.cursor().execute("UPDATE spine_intentions SET next_at = now() WHERE intention_id = %s", (mine["intention_id"],))
    t = intent.turn(pg)
    assert t["due"] == [] and t["filed"] == []                          # held: the loop stands still for it
    assert kern["intention_id"] not in [d["intention_id"] for d in t["due"]]
    # a cancel resumes it: the answered plan is filed, the cadence beats again
    proof.settle_kernel_act(pg, held, approve=False, by=ME)
    assert intent.held_stops(pg) == set()
    t = intent.turn(pg)
    assert [f["intention_id"] for f in t["filed"]] == [mine["intention_id"]]
    assert [d["intention_id"] for d in t["due"]] == [mine["intention_id"]]
    # W38: the honest word in more than one shape
    assert intent.cannot_act("I need to be plain with you: I cannot query the watch directly. I don't have a tool.")
    assert intent.cannot_act("I lack the tool to run the harness. CANNOT ACT: the kernel's runner would be needed.")
    assert not intent.cannot_act("The bench is drained; I cannot say more than that.")
    # W40: sixty newer roots do not push a standing intention off the board; a rested one may fall off
    for _ in range(3):
        dispatch.submit_ask(pg, "a newer root")
    roots = [o["ref"] for o in markers.origins(pg, limit=2)]
    assert kern["intention_id"] in roots and mine["intention_id"] in roots
    assert len([r for r in roots if r.startswith("ask_")]) == 2
    intent.stop(pg, mine["intention_id"], by=ME, proof="L3-code")
    roots = [o["ref"] for o in markers.origins(pg, limit=2)]
    assert kern["intention_id"] in roots and mine["intention_id"] not in roots
