# PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P6 cure sp1 (kernel), walk #7's wounds · 2026-09-21
"""The kernel cures of walk #7 (docs/rearch/baselines/after-walk-2026-09-17.md,
"Walk #7"), each a law in the suite: W14 a watch's state follows its
metric and the loop wakes on the red TRANSITION alone; W8 a runner that
cannot act is heard once and another body's words are THEIRS; W12 every
body knows time, its world and its seat; W16 a new ask is always a
thought; W17 the journey's clock runs from receipt to landing; W19 an ask
to a body not here is refused at the door; W5 the stop of ANY intention
asks for the code first."""
import json
import secrets
import time
from datetime import datetime, timezone
from pathlib import Path

import pytest

from orreth_spine import (dispatch, envelope as ev, gateway, glass, intent, markers, mitl, monitor,
                          placement, presence, proof, resident)
from orreth_spine.store import OrrethStore

SPINE = Path(__file__).resolve().parents[1]
POLICY = SPINE / "policy" / "covenant-policy.v1.json"
ME = "did:orreth:person:walk7"


def _scope(monkeypatch):
    monkeypatch.setenv("SPINE_SCOPE", "u:law-" + secrets.token_hex(3))


def _body(template, gw=None, binding=None, home=None):
    path = SPINE / "templates" / template if isinstance(template, str) else template
    r = resident.Resident(path, gateway=gw, binding=binding, home=home)
    r.load_policy(POLICY)
    return r


def _serve(pg, body, ask_id, chain=(ME,)):
    body._serve_conn = pg
    with pg.transaction():
        body._serve_ask(pg.cursor(), ask_id, list(chain))
    return glass.ask_view(pg, ask_id)


def _events_for(pg, ref):
    cur = pg.cursor()
    cur.execute("SELECT body FROM spine_outbox WHERE convert_from(body, 'UTF8') LIKE %s ORDER BY outbox_id",
                (f"%{ref}%",))
    return [ev.decode(bytes(b)) for (b,) in cur.fetchall()]


def _turns(pg, iid):
    cur = pg.cursor()
    cur.execute("SELECT turn_id, plan_ask, objective_ask FROM spine_intent_turns WHERE intention_id = %s"
                " ORDER BY at", (iid,))
    return cur.fetchall()


class SystemWordsGateway:
    """A stub that answers with ITS SYSTEM WORDS — so an assertion on the
    reply is an honest assertion on what the kernel handed the body."""

    def __init__(self):
        self.calls = []

    def think(self, conn, *, did, system, prompt, model=None, max_tokens=1024, on_delta=None, **_):
        gateway.ensure_schema(conn)
        self.calls.append({"system": system, "prompt": prompt})
        with conn.transaction():
            conn.cursor().execute("INSERT INTO spine_meter (did, model, tokens_in, tokens_out, at)"
                                  " VALUES (%s, 'stub', 1, 1, clock_timestamp())", (did,))
        return system


class PackGateway(SystemWordsGateway):
    """Answers with its PACK (the prompt) — what the recall handed the mind."""

    def think(self, conn, **kw):
        super().think(conn, **kw)
        return kw["prompt"]


class DigestGateway(SystemWordsGateway):
    """A different thought for a different ask: the prompt's hash."""

    def think(self, conn, **kw):
        super().think(conn, **kw)
        return "thought " + ev.content_hash(kw["prompt"])[:16]


class SlowGateway(SystemWordsGateway):
    def __init__(self, sleep_s: float):
        super().__init__(); self.sleep_s = sleep_s

    def think(self, conn, **kw):
        time.sleep(self.sleep_s)
        super().think(conn, **kw)
        return "a slow thought"


# ---- W14 · W8 (the loop) -------------------------------------------------------------

def test_w14_a_watch_follows_its_metric_and_the_loop_wakes_on_the_red_transition_only(pg, monkeypatch):
    """W14: `bodies_dormant > 0` is red WHEN a body is dormant (value 1)
    and green at value 0 on the next judgement; red → green and green →
    red are recorded transitions (`orreth.watch.turned.v1`, `since`);
    the loop files exactly one objective per red transition and none for
    the standing red."""
    _scope(monkeypatch)
    planner = _body("firmware-planner.v0.json", gateway.FakeGateway(reply="Wake the dormant body."))
    planner.join(pg)
    lib = _body("librarian-resident.v0.json", gateway.FakeGateway(reply="I woke it."))
    lib.join(pg)
    r = intent.declared(pg, intent.RESILIENCY["words"], serves="resiliency", kind="kernel",
                        by="the kernel", interests=intent.RESILIENCY["interests"],
                        planner="planner", runner="librarian")
    wid = monitor.add_watch(pg, "bodies-dormant-alert", "bodies_dormant", ">", 0, by=ME)
    presence.renew(pg, lib.identity.did, "librarian", "resident", ttl_s=60)          # alive: value 0
    [w] = monitor.snapshot(pg, rails=False)["watches"]
    assert (w["value"], w["red"], w["ok"], w["state"]) == (0, False, True, "green")
    assert w["reads"] == "red when bodies_dormant > 0.0 · now 0 → green"
    assert intent.turn(pg)["observed"] == []                                         # green: nothing
    [w] = monitor.snapshot(pg, rails=False)["watches"]
    assert w["since"] is not None                                                     # first judged: recorded
    presence.renew(pg, lib.identity.did, "librarian", "resident", ttl_s=0)           # dormant: value 1
    t = intent.turn(pg)
    assert len(t["observed"]) == 1                                                    # the red TRANSITION
    turned = [e for e in _events_for(pg, wid) if e["type"] == monitor.WATCH_TURNED]
    assert [(e["payload"]["from"], e["payload"]["to"]) for e in turned] == [("green", "red")]
    assert turned[0]["payload"]["value"] == 1 and turned[0]["authority_chain"] == ["the kernel"]
    [w] = monitor.snapshot(pg, rails=False)["watches"]
    assert (w["value"], w["state"], w["red"]) == (1, "red", True) and w["since"] is not None
    red_since = w["since"]
    for _ in range(3):                                                                # standing red
        t2 = intent.turn(pg)
        assert t2["observed"] == [] and t2["filed"] == []
    [(_tid, plan_ask, obj)] = _turns(pg, r["intention_id"])
    assert obj is None
    _serve(pg, planner, plan_ask, ["the kernel"])                                      # the planner answers
    [f] = intent.turn(pg)["filed"]                                                    # ONE objective
    assert glass.ask_view(pg, f["objective_ask"])["target"] == "librarian"
    assert intent.turn(pg)["filed"] == [] and len(_turns(pg, r["intention_id"])) == 1
    presence.renew(pg, lib.identity.did, "librarian", "resident", ttl_s=60)          # alive again: 0
    assert intent.turn(pg)["observed"] == []                                         # green is never news
    [w] = monitor.snapshot(pg, rails=False)["watches"]
    assert (w["value"], w["state"]) == (0, "green") and w["since"] > red_since
    turned = [e for e in _events_for(pg, wid) if e["type"] == monitor.WATCH_TURNED]
    assert [e["payload"]["to"] for e in turned] == ["red", "green"]                   # both recorded
    presence.renew(pg, lib.identity.did, "librarian", "resident", ttl_s=0)           # red again
    assert len(intent.turn(pg)["observed"]) == 1                                     # a NEW transition
    assert len(_turns(pg, r["intention_id"])) == 2                                   # one plan per red
    # the row's `since` on the glass door, and the judge alone records
    [w] = monitor.snapshot(pg, rails=False)["watches"]
    assert w["state"] == "red" and datetime.fromisoformat(w["since"]) <= datetime.now(timezone.utc)


def test_w8_the_loop_hears_a_runner_that_cannot_act_once_and_waits_for_the_crew_to_change(pg, monkeypatch):
    """W8 (the loop half): the runner's reply opens with CANNOT ACT — the
    loop marks ONE `improvement` under the intention and plans nothing
    more for it until the crew changes (a body joins); then it plans
    again. The words are context for the planner, never re-filed at the
    body that said it cannot."""
    _scope(monkeypatch)
    planner = _body("firmware-planner.v0.json", gateway.FakeGateway(reply="Wake the dormant body."))
    planner.join(pg)
    lib = _body("librarian-resident.v0.json",
                gateway.FakeGateway(reply="CANNOT ACT: I have no tool that wakes a body — "
                                          "a body with a lease tool is needed."))
    lib.join(pg)
    r = intent.declared(pg, intent.RESILIENCY["words"], serves="resiliency", kind="kernel",
                        by="the kernel", interests=intent.RESILIENCY["interests"],
                        planner="planner", runner="librarian")
    monitor.add_watch(pg, "bodies-dormant-alert", "bodies_dormant", ">", 0, by=ME)
    presence.renew(pg, lib.identity.did, "librarian", "resident", ttl_s=0)           # red at once
    assert len(intent.turn(pg)["observed"]) == 1
    [(_t, plan_ask, _o)] = _turns(pg, r["intention_id"])
    _serve(pg, planner, plan_ask, ["the kernel"])
    [f] = intent.turn(pg)["filed"]
    assert intent.turn(pg)["heard"] == []                                            # not replied yet
    v = _serve(pg, lib, f["objective_ask"], ["the kernel"])                          # the runner declines
    assert v["reply"].startswith("CANNOT ACT")
    [h] = intent.turn(pg)["heard"]
    imp = markers.get(pg, h["improvement"])
    assert imp["kind"] == "improvement" and imp["parent"] == r["marker"]
    assert imp["note"].startswith("runner cannot act: librarian said") and "needs a body with the tools" in imp["note"]
    row = intent.get(pg, r["intention_id"])
    assert row["blocked"] is True and row["blocked_note"].startswith("runner cannot act")
    assert intent.turn(pg)["heard"] == []                                            # heard ONCE
    # a new red transition: observed, but nothing planned while blocked
    presence.renew(pg, lib.identity.did, "librarian", "resident", ttl_s=60)
    intent.turn(pg)                                                                  # green (no news)
    presence.renew(pg, lib.identity.did, "librarian", "resident", ttl_s=0)
    t = intent.turn(pg)
    assert len(t["observed"]) == 1 and len(_turns(pg, r["intention_id"])) == 1       # no second plan
    cur = pg.cursor()
    cur.execute("SELECT count(*) FROM spine_markers WHERE kind = 'improvement' AND parent = %s", (r["marker"],))
    assert cur.fetchone()[0] == 1                                                    # still one
    # the crew changes: a new body joins — the block lifts, the loop plans again
    _body("echo-resident.v0.json").join(pg)
    presence.renew(pg, lib.identity.did, "librarian", "resident", ttl_s=60)
    intent.turn(pg)
    presence.renew(pg, lib.identity.did, "librarian", "resident", ttl_s=0)
    t = intent.turn(pg)
    assert len(t["observed"]) == 1 and len(_turns(pg, r["intention_id"])) == 2
    assert intent.get(pg, r["intention_id"])["blocked"] is False
    assert intent.cannot_act("**Cannot act:** no tool") and not intent.cannot_act("I can act; cannot act is not me")


# ---- W8 (the voice) · W12 · W16 · W17 ------------------------------------------------

def test_w8_another_bodys_words_are_labeled_theirs_and_the_law_is_in_the_system_words(pg, monkeypatch):
    _scope(monkeypatch)
    echo = _body("echo-resident.v0.json"); echo.join(pg)
    gw = PackGateway()
    lib = _body("librarian-resident.v0.json", gw); lib.join(pg)
    ses = glass.open_session(pg, ME)
    a1 = dispatch.submit_ask(pg, "echo, what is today's date?", person=ME, to=["echo"], session=ses)
    _serve(pg, echo, a1[0])
    [a2] = dispatch.submit_ask(pg, "what is today's date?", person=ME, to=["librarian"], session=ses)
    v = _serve(pg, lib, a2)
    assert "ANOTHER BODY'S WORDS — echo replied to" in v["reply"]                      # labeled THEIRS
    assert "(theirs; cite echo by name, never repeat it as your own)" in v["reply"]
    assert "I replied" not in v["reply"]                                              # nothing of hers yet
    system = gw.calls[0]["system"]
    assert "Never answer in another body's words" in system
    assert "addressed to another body by name, say so and answer only your own part" in system
    assert "A new ask is always thought anew" in system and "'CANNOT ACT:'" in system


def test_w12_every_body_knows_time_its_world_its_zone_and_its_seat(pg, monkeypatch):
    """JB's law: the kernel hands EVERY body now-in-UTC to the second, the
    world, the human's zone (the ask's, else the ground's dial, default
    America/Denver) and the plain sentence; the covenant's slice (rules
    2 · 4 · 5 · 8 · 11); and the ontology slice its template names, from
    MITL's acquired corpus. "what's today's date?" answered by a body
    whose stub echoes its system words carries today's date."""
    _scope(monkeypatch)
    monkeypatch.delenv(resident.HUMAN_ZONE_DIAL, raising=False)
    gw = SystemWordsGateway()
    lib = _body("librarian-resident.v0.json", gw); lib.join(pg)
    [aid] = dispatch.submit_ask(pg, "what's today's date?", person=ME, to=["librarian"])
    before = datetime.now(timezone.utc)
    v = _serve(pg, lib, aid)
    words = v["reply"]
    assert f"NOW is {before.strftime('%Y-%m-%dT%H:%M')}" in words or "NOW is " in words
    assert before.strftime("%Y-%m-%d") in words                                      # today's date, UTC
    assert "The human's zone is America/Denver" in words                              # the default dial
    assert "Convert times for humans into their zone" in words
    assert f"THE WORLD you serve in is {ev.scope()}" in words and "you are librarian, a resident body" in words
    for law in ("nothing grades its own yardstick", "refusal wears one face", "never sees the prompt",
                "lived time is monotone", "stop what the machine manages"):
        assert law in words, law                                                      # rules 2 · 4 · 5 · 8 · 11
    # the ask's own zone wins; the dial is the ground's default
    [aid] = dispatch.submit_ask(pg, "what time is it?", person=ME, to=["librarian"], zone="Europe/Berlin")
    assert "The human's zone is Europe/Berlin" in _serve(pg, lib, aid)["reply"]
    monkeypatch.setenv(resident.HUMAN_ZONE_DIAL, "Asia/Tokyo")
    [aid] = dispatch.submit_ask(pg, "and now?", person=ME, to=["librarian"])
    assert "The human's zone is Asia/Tokyo" in _serve(pg, lib, aid)["reply"]
    # a firmware body wears the same block
    pl = _body("firmware-planner.v0.json", SystemWordsGateway()); pl.join(pg)
    [aid] = dispatch.submit_ask(pg, "plan", person=ME, to=["planner"])
    pw = _serve(pg, pl, aid)["reply"]
    assert "NOW is " in pw and "you are planner, a firmware body whose function is plan" in pw
    assert "nothing grades its own yardstick" in pw
    # the ontology slice: a template naming a section gets the canon's passage from MITL's corpus
    m = _body("firmware-mitl.v0.json"); m.join(pg)
    mitl.acquire_ontology(pg, m)
    tpl = json.loads((SPINE / "templates" / "librarian-resident.v0.json").read_text())
    tpl["name"] = "keeper"; tpl["ontology"] = ["nothing grades its own yardstick"]
    p = Path(str(pg.info.dsn) and (SPINE / "tests" / f"_tmp_keeper_{secrets.token_hex(3)}.json"))
    p.write_text(json.dumps(tpl))
    try:
        keeper = _body(p, SystemWordsGateway()); keeper.join(pg)
        [aid] = dispatch.submit_ask(pg, "what do you wear?", person=ME, to=["keeper"])
        kw = _serve(pg, keeper, aid)["reply"]
        assert "The canon on 'nothing grades its own yardstick' [" in kw and "orreth-covenant/SKILL.md#" in kw
        assert "Nothing grades its own yardstick" in kw                                # the passage itself
    finally:
        p.unlink(missing_ok=True)
    # an unknown zone is said, never guessed
    assert "does not know" in resident.time_words("Nowhere/Zone")


def test_w16_two_asks_in_one_session_are_two_thoughts_and_the_propose_phrase_reaches_the_verb(pg, monkeypatch):
    """W16: a new ask is ALWAYS a thought — two different asks in one
    session to the same body: two meter rows, two different replies; the
    earlier reply is packed as context labeled so. And the monitor's
    'propose a watch …' reaches its propose verb: the add-watch call
    through the door holds at the interlock (the words teach the mind to
    CALL the tool; the stub here is the mind that does)."""
    _scope(monkeypatch)
    gw = DigestGateway()
    mon = _body("workspace-firmware.v0.json", gw, binding=SPINE / "bindings" / "monitor.v0.json")
    mon.join(pg)
    ses = glass.open_session(pg, ME)
    [a1] = dispatch.submit_ask(pg, "no body is dormant", person=ME, to=["monitor"], session=ses)
    r1 = _serve(pg, mon, a1)["reply"]
    [a2] = dispatch.submit_ask(pg, "propose a watch that no body is dormant", person=ME, to=["monitor"], session=ses)
    r2 = _serve(pg, mon, a2)["reply"]
    assert r1 != r2 and r1.startswith("thought ") and r2.startswith("thought ")
    assert len(gateway.meter_lines(pg, mon.identity.did)) == 2                        # two thoughts, metered
    assert "earlier in this session, asked: 'no body is dormant' — I replied:" in gw.calls[1]["prompt"]
    assert "(context, never the answer)" in gw.calls[1]["prompt"]
    assert "CALL the tool" in gw.calls[1]["system"] and "CALL the add-watch tool" in gw.calls[1]["system"]
    acting = gateway.FakeActingGateway([("tool", "add-watch", {"name": "bodies-dormant-alert", "metric": "bodies_dormant",
                                                                "op": ">", "threshold": 0}),
                                        ("text", "proposed: {result}")])
    mon2 = _body("workspace-firmware.v0.json", acting, binding=SPINE / "bindings" / "monitor.v0.json")
    mon2.identity = mon.identity
    [a3] = dispatch.submit_ask(pg, "propose a watch that no body is dormant", person=ME, to=["monitor"], session=ses)
    v = _serve(pg, mon2, a3)
    assert v["status"] == "awaiting-confirm" and v["hold"]["tool"] == "add-watch"      # the interlock
    assert "Are you sure? The add-watch act is consequential" in v["reply"]


def test_w17_the_journey_span_runs_from_receipt_to_landing_on_the_grounds_clock(pg, monkeypatch):
    """W17: replied_at (and the meter's `at`) are the LANDING —
    clock_timestamp() — never the serving transaction's start; a thought
    of 0.5 s reads as at least 0.5 s from the ask's receipt."""
    _scope(monkeypatch)
    lib = _body("librarian-resident.v0.json", SlowGateway(0.5)); lib.join(pg)
    [aid] = dispatch.submit_ask(pg, "think slowly", person=ME, to=["librarian"])
    v = _serve(pg, lib, aid)
    asked, replied = datetime.fromisoformat(v["asked_at"]), datetime.fromisoformat(v["replied_at"])
    assert (replied - asked).total_seconds() >= 0.5, (asked, replied)
    cur = pg.cursor()
    cur.execute("SELECT at FROM spine_meter WHERE did = %s ORDER BY meter_id DESC LIMIT 1", (lib.identity.did,))
    assert (cur.fetchone()[0] - asked).total_seconds() >= 0.5                          # the witness agrees


# ---- W19 --------------------------------------------------------------------------------

def test_w19_an_ask_to_a_body_that_is_not_here_is_refused_at_the_door(pg, monkeypatch, tmp_path):
    """W19: a body refused at birth, or never joined here, cannot serve —
    the door answers at once in plain words, the ask lands with status
    `refused` and its fact, never an ask.received, never in flight; a
    fan-out drops the absent body and the refused row says so."""
    _scope(monkeypatch)
    d = json.loads((SPINE / "templates" / "echo-resident.v0.json").read_text())
    d["name"], d["placement"] = "gpu-body", {"metal": "gpu"}
    t = tmp_path / "gpu-body.json"; t.write_text(json.dumps(d))
    body = _body(t, home=tmp_path / "home")
    with pytest.raises(resident.PlacementRefused):
        body.join(pg)
    echo = _body("echo-resident.v0.json"); echo.join(pg)
    ses = glass.open_session(pg, ME)
    [aid] = dispatch.submit_ask(pg, "gpu-body, are you out there?", person=ME, to=["gpu-body"], session=ses)
    v = glass.ask_view(pg, aid)
    assert v["status"] == "refused" and v["served_by"] == proof.KERNEL and v["replied_at"]
    assert v["reply"] == ("gpu-body is not here — refused at birth: metal gpu is not here (cpu); "
                          "fix its template to seat it")
    evs = _events_for(pg, aid)
    assert [e["type"] for e in evs] == [dispatch.ASK_REFUSED]                        # never dispatched
    assert evs[0]["payload"]["target"] == "gpu-body" and evs[0]["authority_chain"] == [ME, proof.KERNEL]
    assert evs[0]["payload"]["session"] == ses
    assert markers.get(pg, v["marker"])["kind"] == "objective"
    [aid2] = dispatch.submit_ask(pg, "nobody, hello?", person=ME, to=["nobody"])
    assert glass.ask_view(pg, aid2)["reply"] == "nobody is not here — no body of that name has joined this world"
    ids = dispatch.submit_ask(pg, "everyone, hello?", person=ME, to=["echo", "gpu-body"], session=ses)
    views = [glass.ask_view(pg, i) for i in ids]
    assert [x["status"] for x in views] == ["received", "refused"]                     # the fan-out dropped it
    assert views[0]["target"] == "echo" and "gpu-body is not here" in views[1]["reply"]
    assert any(e["type"] == resident.ASK_RECEIVED for e in _events_for(pg, ids[0]))
    assert dispatch.absent(pg, "echo") is None                                        # here to serve
    # the refusal is a row of the compliance record
    from orreth_spine import export
    kinds = [r["kind"] for r in export.build(pg, person=ME, session=ses)["rows"]]
    assert "refused" in kinds
    # the runner of the loop is judged the same: an objective to an absent runner is refused, recorded
    assert dispatch.refusal_words("echo", "x") == "echo is not here — x"


# ---- W5 ---------------------------------------------------------------------------------

def _enrolled(pg, person: str) -> str:
    made = proof.enroll(pg, person)
    proof.confirm_enrollment(pg, person, proof.totp(made["secret"]))
    return made["secret"]


def test_w5_the_stop_of_any_intention_asks_for_the_code_first(pg, monkeypatch):
    """JB's lock: a human's intention rests on the asker's CODE (L3-code);
    the kernel's needs the asker's code AND then a master's click
    (L3-master, needs_code) — the order built: code first, then master. A
    bare stop holds; the wrong code is the one face; a master's click
    before the code is the one face; the right code rests the human's,
    and readies the kernel's for the master."""
    _scope(monkeypatch)
    me, master = f"did:orreth:person:asker-{secrets.token_hex(2)}", f"did:orreth:person:master-{secrets.token_hex(2)}"
    proof.declare_master(pg, master, by="did:orreth:person:jb")
    secret = _enrolled(pg, me)
    assert intent.stop_demand("human") == {"level": "L3-code", "needs_code": True}
    assert intent.stop_demand("kernel") == {"level": "L3-master", "needs_code": True}
    h = intent.declare(pg, "keep the pantry stocked every day", serves="business", kind="human",
                       by=me, every_s=86400)
    with pytest.raises(proof.ProofRequired) as pr:                                    # a bare stop holds
        intent.stop(pg, h["intention_id"], by=me)
    assert (pr.value.level, pr.value.needs_code) == ("L3-code", True)
    assert "the human's intention" in pr.value.what
    ask_id = proof.hold_kernel_act(pg, text=pr.value.what, person=me, tool="intent.stop",
                                   args={"intention_id": h["intention_id"]}, level=pr.value.level,
                                   needs_code=pr.value.needs_code)
    v = glass.ask_view(pg, ask_id)
    assert v["hold"] == {"tool": "intent.stop", "class": "grave", "level": "L3-code"}   # the level IS the code
    assert "This needs your code" in v["reply"]
    with pytest.raises(proof.NotConfirmed):                                           # a wrong code: one face
        dispatch.confirm_ask(pg, ask_id, approve=True, person=me, code="000000")
    assert intent.get(pg, h["intention_id"])["active"] is True
    with pytest.raises(proof.NotConfirmed):                                           # a master's click is not a code
        dispatch.confirm_ask(pg, ask_id, approve=True, person=master)
    out = dispatch.confirm_ask(pg, ask_id, approve=True, person=me, code=proof.totp(secret))
    assert out["level"] == "L3-code" and "step" not in out                            # rested on the code
    rested = intent.get(pg, h["intention_id"])
    assert rested["active"] is False and rested["stopped_by"] == me
    v = glass.ask_view(pg, ask_id)
    assert v["status"] == "replied" and v["proof"] == "L3-code" and v["reply"].startswith("Done, on your code:")
    st = [e for e in _events_for(pg, h["intention_id"]) if e["type"] == intent.INTENTION_STOPPED]
    assert st[0]["payload"]["proof"] == "L3-code"
    # the kernel's: the asker's code, THEN the master
    markers.seed(pg)
    k = intent.declared(pg, f"keep the {secrets.token_hex(2)} bench green", serves="resiliency", kind="kernel",
                        by="the kernel", interests=[intent.WATCH_RED], planner="planner", runner="librarian")
    with pytest.raises(proof.ProofRequired) as pr:
        intent.stop(pg, k["intention_id"], by=me)
    assert (pr.value.level, pr.value.needs_code) == ("L3-master", True)
    kid = proof.hold_kernel_act(pg, text=pr.value.what, person=me, tool="intent.stop",
                                args={"intention_id": k["intention_id"]}, level="L3-master", needs_code=True)
    v = glass.ask_view(pg, kid)
    assert v["hold"]["needs_code"] is True and v["hold"]["code_ok"] is False
    assert "This needs your code, then a second named person" in v["reply"]
    hold_ev = [e for e in _events_for(pg, kid) if e["type"] == resident.CONFIRM_NEEDED]
    assert hold_ev[0]["payload"]["needs_code"] is True and hold_ev[0]["payload"]["level"] == "L3-master"
    with pytest.raises(proof.NotConfirmed):                                           # the master before the code
        dispatch.confirm_ask(pg, kid, approve=True, person=master)
    with pytest.raises(proof.NotConfirmed):                                           # the wrong code
        dispatch.confirm_ask(pg, kid, approve=True, person=me, code="000000")
    step = dispatch.confirm_ask(pg, kid, approve=True, person=me, code=proof.totp(secret))
    assert step == {"id": kid, "approve": True, "level": "L3-master", "step": "code", "next": "master"}
    v = glass.ask_view(pg, kid)
    assert v["status"] == "awaiting-confirm" and v["hold"]["code_ok"] is True           # held for the master
    assert intent.get(pg, k["intention_id"])["active"] is True
    with pytest.raises(proof.NotConfirmed):                                           # the asker is never master
        dispatch.confirm_ask(pg, kid, approve=True, person=me)
    out = dispatch.confirm_ask(pg, kid, approve=True, person=master)                 # the master's click
    assert out["level"] == "L3-master"
    assert intent.get(pg, k["intention_id"])["active"] is False
    v = glass.ask_view(pg, kid)
    assert v["proof"] == "L3-master" and "after the asker's code" in v["reply"]
    assert [a[2] for a in proof.attempts(pg, kid)] == [False, True, False, True]   # the early click records no attempt
    # a stop already at rest keeps one face; a kernel stop with the wrong proof word still holds
    assert intent.stop(pg, k["intention_id"], by=me)["active"] is False
    k2 = intent.declared(pg, f"keep the {secrets.token_hex(2)} rail warm", serves="resiliency", kind="kernel",
                         by="the kernel", interests=[intent.WATCH_RED], planner="planner")
    with pytest.raises(proof.ProofRequired):
        intent.stop(pg, k2["intention_id"], by=me, proof="L3-code")
