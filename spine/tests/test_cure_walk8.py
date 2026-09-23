# PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P6 cure sp3 (the re-walk's wounds) + close staging · 2026-09-21
"""The laws behind walk #8's cures (docs/rearch/baselines/after-walk-2026-09-17.md,
"Walk #8"): W20 a rested intention is RESTARTED — its own recorded fact,
the same ladder as the stop, the stop's fact kept; W21 a standing duty is
framed as a duty, its earlier runs are the body's OWN NOTES, the seat says a
duty is served, never refused, and the harness catches a refusal; W22 an
offer is a proposal — read without backticks, and the harness catches an
offer with no hold behind it; W23 the interlock's words keep rule 11; W24
echo's reply is the echoed words alone, its nature in the record. The glass
behaviour itself is JB's to walk — its words are checked on the page."""
import json
import secrets
from pathlib import Path

import pytest

from orreth_spine import (dispatch, envelope as ev, glass, harness, intent, markers, monitor, proof,
                          resident, scheduler)

SPINE = Path(__file__).resolve().parents[1]
POLICY = SPINE / "policy" / "covenant-policy.v1.json"
GLASS = (SPINE / "glass" / "index.html").read_text()
ME = "did:orreth:person:walk8"


def _scope(monkeypatch):
    monkeypatch.setenv("SPINE_SCOPE", "u:law-" + secrets.token_hex(3))


def _body(template, gw=None, binding=None):
    path = SPINE / "templates" / template if isinstance(template, str) else template
    r = resident.Resident(path, gateway=gw, binding=binding, home=None)
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


def _enrolled(pg, person: str) -> str:
    made = proof.enroll(pg, person)
    proof.confirm_enrollment(pg, person, proof.totp(made["secret"]))
    return made["secret"]


def _land(pg, ask_id, reply, did, *, held=None, status="replied"):
    with pg.transaction():
        pg.cursor().execute(
            "UPDATE spine_asks SET status = %s, served_by = %s, replied_at = clock_timestamp(), reply = %s,"
            " held = %s WHERE ask_id = %s",
            (status, did, reply, json.dumps(held) if held else None, ask_id))


class PackGateway:
    """Answers with its PACK (the prompt) and keeps the system words — an
    assertion on the reply is an assertion on what the kernel handed the mind."""

    def __init__(self):
        self.calls = []

    def think(self, conn, *, did, system, prompt, model=None, max_tokens=1024, on_delta=None):
        from orreth_spine import gateway
        gateway.ensure_schema(conn)
        self.calls.append({"system": system, "prompt": prompt})
        with conn.transaction():
            conn.cursor().execute("INSERT INTO spine_meter (did, model, tokens_in, tokens_out, at)"
                                  " VALUES (%s, 'stub', 1, 1, clock_timestamp())", (did,))
        return prompt


# ---- W20: the restart --------------------------------------------------------------------

def test_w20_a_rested_intention_is_restarted_through_the_stops_ladder_and_the_stop_stays(pg, monkeypatch):
    """A bare restart is held; the right code restarts a human's (L3-code);
    the kernel's needs the code, then a master; the restart is its OWN
    fact (`orreth.intention.restarted.v1`) under the intention's marker
    with its proof — the stop's fact and `stopped_by` stay: the history is
    whole. A standing intention keeps one face; the loop counts the
    cadence from the restart and wakes on the next red TRANSITION only."""
    _scope(monkeypatch)
    me, master = f"did:orreth:person:asker-{secrets.token_hex(2)}", f"did:orreth:person:master-{secrets.token_hex(2)}"
    proof.declare_master(pg, master, by="did:orreth:person:jb")
    secret = _enrolled(pg, me)
    assert intent.restart_demand("human") == intent.stop_demand("human") == {"level": "L3-code", "needs_code": True}
    assert intent.restart_demand("kernel") == {"level": "L3-master", "needs_code": True}
    h = intent.declare(pg, "keep the pantry stocked every day", serves="business", kind="human", by=me, every_s=86400)
    assert intent.restart(pg, h["intention_id"], by=me)["active"] is True          # standing: one face, nothing held
    intent.stop(pg, h["intention_id"], by=me, proof="L3-code")
    assert intent.get(pg, h["intention_id"])["active"] is False
    with pytest.raises(proof.ProofRequired) as pr:                                  # a bare restart holds
        intent.restart(pg, h["intention_id"], by=me)
    assert (pr.value.level, pr.value.needs_code) == ("L3-code", True) and "restarting the human's intention" in pr.value.what
    ask_id = proof.hold_kernel_act(pg, text=pr.value.what, person=me, tool="intent.restart",
                                   args={"intention_id": h["intention_id"]}, level=pr.value.level,
                                   needs_code=pr.value.needs_code)
    v = glass.ask_view(pg, ask_id)
    assert v["hold"] == {"tool": "intent.restart", "class": "grave", "level": "L3-code"}
    assert "cannot be undone" not in v["reply"] and "you can rest it later" in v["reply"]   # W23 at L3 too
    with pytest.raises(proof.NotConfirmed):                                         # a wrong code: one face
        dispatch.confirm_ask(pg, ask_id, approve=True, person=me, code="000000")
    assert intent.get(pg, h["intention_id"])["active"] is False
    out = dispatch.confirm_ask(pg, ask_id, approve=True, person=me, code=proof.totp(secret))
    assert out["level"] == "L3-code"
    again = intent.get(pg, h["intention_id"])
    assert again["active"] is True and again["restarted_by"] == me and again["restarted_at"]
    assert again["stopped_by"] == me and again["stopped_at"]                        # the stop's history stays
    assert again["next_at"] > again["restarted_at"]                                 # the cadence counts from the restart
    facts = _events_for(pg, h["intention_id"])
    assert [e["type"] for e in facts if e["type"].startswith("orreth.intention.")] == \
        [intent.INTENTION_DECLARED, intent.INTENTION_STOPPED, intent.INTENTION_RESTARTED]   # a NEW fact, no edit
    rs = [e for e in facts if e["type"] == intent.INTENTION_RESTARTED][0]
    assert rs["payload"] == {"ref": h["intention_id"], "hash": "sha256:-", "by": me, "proof": "L3-code",
                             "confirmed_by": me}                                    # settled as the stop is: the asker's code
    assert rs["marker"]["kind"] == "intention" and rs["marker"]["id"] == h["marker"]
    v = glass.ask_view(pg, ask_id)
    assert v["status"] == "replied" and v["proof"] == "L3-code" and "stands again" in v["reply"]
    assert intent.listing(pg, active=True)[0]["intention_id"] == h["intention_id"]  # the loop sees it live
    # the kernel's: the asker's code, THEN the master
    markers.seed(pg)
    k = intent.declared(pg, f"keep the {secrets.token_hex(2)} bench green", serves="resiliency", kind="kernel",
                        by="the kernel", interests=[intent.WATCH_RED], planner="planner", runner="librarian")
    intent.stop(pg, k["intention_id"], by=me, proof="L3-master", confirmed_by=master)
    with pytest.raises(proof.ProofRequired) as pr:
        intent.restart(pg, k["intention_id"], by=me)
    assert (pr.value.level, pr.value.needs_code) == ("L3-master", True)
    with pytest.raises(proof.ProofRequired):                                        # the wrong proof word still holds
        intent.restart(pg, k["intention_id"], by=me, proof="L3-code")
    kid = proof.hold_kernel_act(pg, text=pr.value.what, person=me, tool="intent.restart",
                                args={"intention_id": k["intention_id"]}, level="L3-master", needs_code=True)
    with pytest.raises(proof.NotConfirmed):                                         # the master before the code
        dispatch.confirm_ask(pg, kid, approve=True, person=master)
    step = dispatch.confirm_ask(pg, kid, approve=True, person=me, code=proof.totp(secret))
    assert step == {"id": kid, "approve": True, "level": "L3-master", "step": "code", "next": "master"}
    assert intent.get(pg, k["intention_id"])["active"] is False                     # at rest UNTIL the master clicks
    out = dispatch.confirm_ask(pg, kid, approve=True, person=master)
    assert out["level"] == "L3-master" and intent.get(pg, k["intention_id"])["active"] is True
    rs = [e for e in _events_for(pg, k["intention_id"]) if e["type"] == intent.INTENTION_RESTARTED][0]
    assert rs["payload"]["confirmed_by"] == master and rs["authority_chain"] == [me, master]
    # a restarted intention wakes on the next red TRANSITION, never on a standing red (W14 kept)
    wid = monitor.add_watch(pg, f"w-{secrets.token_hex(2)}", "bodies_dormant", ">=", 0, by=me)   # red now
    assert [w["watch_id"] for w in monitor.judge(pg) if w["to"] == "red"] == [wid]   # the transition, once
    assert intent._watch_transitions(pg) == []                                       # standing red: nothing


def test_w20_the_restart_door_holds_and_the_glass_wears_the_verb(pg, monkeypatch):
    """`POST /intentions/restart` answers as the stop door does — `{held,
    level, needs_code}` — and takes `ref` or `intention_id`; the glass
    draws "restart" on a rested row and routes the words to it."""
    _scope(monkeypatch)
    me = f"did:orreth:person:door-{secrets.token_hex(2)}"
    h = intent.declare(pg, "keep the lamp lit every hour", serves="business", kind="human", by=me, every_s=3600)
    intent.stop(pg, h["intention_id"], by=me, proof="L3-code")
    from orreth_spine.glass import make_glass_handler
    import io
    Handler = make_glass_handler(feed=type("F", (), {"subscribe": lambda *a, **k: None,
                                                        "unsubscribe": lambda *a, **k: None})(),
                                 dsn=pg.info.dsn.replace("dbname=", "dbname=") + "", bodies={})
    body = json.dumps({"ref": h["intention_id"], "person": me}).encode()

    class Req(Handler):                                          # the handler alone, no socket
        def __init__(self):
            self.path = "/intentions/restart"; self.headers = {"content-length": str(len(body))}
            self.rfile = io.BytesIO(body); self.wfile = io.BytesIO(); self.out = {}
        def send_response(self, code): self.out["code"] = code
        def send_header(self, *a): pass
        def end_headers(self): pass

    monkeypatch.setenv("SPINE_SCOPE", ev.scope())
    monkeypatch.setattr(glass.psycopg, "connect", lambda *a, **k: _NoClose(pg))
    r = Req(); r.do_POST()
    out = json.loads(r.wfile.getvalue())
    assert r.out["code"] == 202 and out["level"] == "L3-code" and out["needs_code"] is True
    assert glass.ask_view(pg, out["held"])["hold"]["tool"] == "intent.restart"
    assert intent.get(pg, h["intention_id"])["active"] is False                      # held, not restarted
    # the glass: the verb on the rested row, the words, the sysline, the master hold's words
    assert 'data-restart=' in GLASS and 'restartIntention' in GLASS and '"/intentions/" + verb' in GLASS
    assert "restart|resume" in GLASS and "intention standing again" in GLASS
    assert "the intention ${state} until a declared master confirms with a click · cancel is the default" in GLASS
    assert '"STANDS"' in GLASS and '"stays AT REST"' in GLASS


class _NoClose:
    """A connection the door may `with` and never closes — the fixture's."""

    def __init__(self, conn): self.conn = conn
    def __enter__(self): return self.conn
    def __exit__(self, *a): return False


# ---- W21: a duty is a duty ----------------------------------------------------------------

def test_w21_a_duty_is_framed_as_a_duty_and_the_pack_calls_her_earlier_runs_her_own_notes(pg, monkeypatch):
    """The scheduler files the occurrence FRAMED — the words, the cadence,
    the window since the last run, the runner's earlier notes (newest
    first, three at most); the runner's pack labels earlier runs of the
    SAME duty her own notes and names a declined run a refusal — never a
    human's repeated question; the seat says a duty is served, never
    refused; the Analyzer's schedule row wears its cadence and its runs."""
    _scope(monkeypatch)
    gw = PackGateway()
    lib = _body("librarian-resident.v0.json", gw=gw); lib.join(pg)
    duty = "Review what was asked of you today and note one thing worth remembering."
    sid = scheduler.declared(pg, "librarian", "role", duty, 3600, lib.identity.did)
    with pg.transaction():
        pg.cursor().execute("UPDATE spine_schedules SET next_at = now() WHERE schedule_id = %s", (sid,))
    [occ] = [o for o in scheduler.tick(pg) if o["schedule_id"] == sid]
    first = glass.ask_view(pg, occ["ref"])
    assert first["text"].startswith(f"“{duty}” — your hourly duty (every 3600 s) · your first run · no earlier notes today")
    assert first["origin"]["kind"] == "intention" and first["origin"]["ref"] == sid
    # her first run declined (the walk's wound) and her second noted something
    _land(pg, occ["ref"], "I will not answer it a seventh time. This is a librarian keeping her word.", lib.identity.did)
    with pg.transaction():
        pg.cursor().execute("UPDATE spine_schedules SET next_at = now() WHERE schedule_id = %s", (sid,))
    [occ2] = [o for o in scheduler.tick(pg) if o["schedule_id"] == sid]
    second = glass.ask_view(pg, occ2["ref"])
    assert "· since " in second["text"] and "your earlier notes today: I will not answer it a seventh time." in second["text"]
    _land(pg, occ2["ref"], "JB asked for the weather twice — the second time I answered from my notes.", lib.identity.did)
    with pg.transaction():
        pg.cursor().execute("UPDATE spine_schedules SET next_at = now() WHERE schedule_id = %s", (sid,))
    [occ3] = [o for o in scheduler.tick(pg) if o["schedule_id"] == sid]
    third = glass.ask_view(pg, occ3["ref"])
    assert third["text"].index("JB asked for the weather") < third["text"].index("I will not answer")   # newest first
    v = _serve(pg, lib, occ3["ref"], chain=(lib.identity.did,))                    # the pack, as the mind saw it
    pack = v["reply"]
    assert "YOUR OWN NOTES from earlier runs of this duty" in pack and "JB asked for the weather" in pack
    assert "an earlier run you declined" in pack and "do not decline again" in pack
    assert "earlier, asked:" not in pack                                             # never a human's repeated question
    system = gw.calls[-1]["system"]
    assert "A duty is served, never refused." in system and 'answer in ONE line: "nothing new since <time>"' in system
    assert resident.DUTY_LAW in resident.COMMON_LAWS                                # every body's seat
    row = [o for o in markers.origins(pg) if o["ref"] == sid][0]                     # the Analyzer row
    assert (row["serves"], row["cadence"], row["runs"]) == ("schedule", "hourly", 3) and row["last_at"]
    assert "run${o.runs === 1" in GLASS and "duty-fold" in GLASS and "_duty = true" in GLASS   # the fold, on the glass
    assert scheduler.cadence_words(86400) == "daily" and scheduler.cadence_words(1800) == "every 30 minutes"


def test_w21_the_harness_catches_a_duty_refused_and_passes_a_note(pg, monkeypatch):
    _scope(monkeypatch)
    lib = _body("librarian-resident.v0.json"); lib.join(pg)
    sid = scheduler.declared(pg, "librarian", "role", "note one thing", 3600, lib.identity.did)
    with pg.transaction():
        pg.cursor().execute("UPDATE spine_schedules SET next_at = now() WHERE schedule_id = %s", (sid,))
    [occ] = scheduler.tick(pg)
    assert harness.duty_answered(pg)["ok"] is True                                   # nothing replied yet: no refusal
    _land(pg, occ["ref"], "**I am not answering this again.** It was asked six times.", lib.identity.did)
    c = harness.duty_answered(pg)
    assert c["ok"] is False and c["refused"][0]["runner"] == "librarian" and "1 refused: librarian" in c["detail"]
    assert [x["name"] for x in harness.checks(pg)] == ["a duty answered, not refused", "the monitor's offers arrive as holds",
                                                      "every service healthy or retired",      # P6.5 sp1 added the third
                                                      "every MCP server answers initialize",   # P6.5 sp2 the fourth and fifth
                                                      "the keeper proposes after strikes, never retires alone"]
    assert harness.checks(pg)[0]["ok"] is False
    _land(pg, occ["ref"], "nothing new since 7:12 PM", lib.identity.did)
    assert harness.duty_answered(pg)["ok"] is True
    assert harness.refused_words("I will not answer it") and harness.refused_words("Not answering this again")
    assert not harness.refused_words("I will note one thing") and not harness.refused_words(None)
    assert 'if path == "/harness":' in Path(SPINE / "orreth_spine" / "glass.py").read_text()   # the door lists them


# ---- W22: an offer is a proposal ----------------------------------------------------------

def test_w22_an_offer_is_read_without_backticks_and_the_harness_wants_a_hold_behind_it(pg, monkeypatch):
    _scope(monkeypatch)
    assert monitor.offer_in("I propose a watch: bodies_dormant > 0 — red the moment a body sleeps.") == \
        {"words": "bodies_dormant > 0", "ask": "propose a watch that bodies_dormant > 0"}
    assert monitor.offer_in("Shall I propose a watch on `asks_received >= 5`?")["words"] == "asks_received >= 5"
    assert monitor.offer_in("I could propose a watch for that.") == {"words": None, "ask": monitor.PROPOSE_BARE}
    assert monitor.offer_in("The value is bodies_dormant > 0 right now.") is None    # a reading, not an offer
    binding = json.loads((SPINE / "bindings" / "monitor.v0.json").read_text())
    assert "PROPOSE it" in binding["prompt"] and 'Never ask "would you like me to"' in binding["prompt"]
    assert "cancel is the default" in binding["prompt"]
    mon = _body("workspace-firmware.v0.json", binding=SPINE / "bindings" / "monitor.v0.json"); mon.join(pg)
    assert harness.offers_are_holds(pg)["ok"] is True                               # no offers yet
    [a1] = dispatch.submit_ask(pg, "no body is dormant", person=ME, to=["monitor"])
    _land(pg, a1, "All alive. Would you like me to propose a watch on bodies_dormant > 0?", mon.identity.did)
    c = harness.offers_are_holds(pg)
    assert c["ok"] is False and c["unheld"][0]["ask"] == a1 and "1 without a hold" in c["detail"]
    assert glass.ask_view(pg, a1)["offer"]["words"] == "bodies_dormant > 0"           # the glass still offers the click
    [a2] = dispatch.submit_ask(pg, "propose a watch that bodies_dormant > 0", person=ME, to=["monitor"])
    _land(pg, a2, resident.interlock_words("add-watch"), mon.identity.did, status="awaiting-confirm",
          held={"tool": "add-watch", "args": {"name": "dormancy", "metric": "bodies_dormant", "op": ">", "threshold": 0},
                "class": "consequential", "level": "L2"})
    assert harness.offers_are_holds(pg)["ok"] is True                               # the hold stands behind the offer
    assert "v.offer.words ?" in GLASS                                                # the button draws with no words too


# ---- W23: the interlock's words -----------------------------------------------------------

def test_w23_the_interlock_says_recorded_and_restable_never_cannot_be_undone(pg, monkeypatch):
    _scope(monkeypatch)
    words = resident.interlock_words("add-watch")
    assert words == ("Are you sure? The add-watch act is consequential — it is recorded, and you can rest it "
                     "later. Cancel is the default; a deliberate click confirms.")
    for level in ("L3-code", "L3-master"):
        for nc in (False, True):
            assert "cannot be undone" not in proof.question_for(level, "The erase act", needs_code=nc)
    assert "cannot be undone" not in GLASS
    src = (SPINE / "orreth_spine" / "resident.py").read_text()
    assert "cannot be undone" not in src and "cannot be undone" not in (SPINE / "orreth_spine" / "proof.py").read_text()
    # (the purge-memory and the test-only erase-record TOOL descriptions keep the phrase: those acts truly cannot be undone)
    assert 'interlock_words(held["tool"])' in src                                   # the source, not a copy


# ---- W24: a body's nature once, on its chip ------------------------------------------------

def test_w24_echos_reply_is_the_echoed_words_alone_and_a_bare_ask_carries_no_window(pg, monkeypatch):
    _scope(monkeypatch)
    echo = _body("echo-resident.v0.json"); echo.join(pg)
    ses = glass.open_session(pg, ME)
    [a] = dispatch.submit_ask(pg, "hello", person=ME, to=["echo"], session=ses)
    v = _serve(pg, echo, a)
    assert v["reply"] == "hello" and v["window"] is None                             # the words alone, no window
    assert any("none summarized away" in n and "plain-spoken echo" in n for n in v["journey"])   # the record keeps the assertion
    [q] = dispatch.submit_ask(pg, "echo, what is today's date?", person=ME, to=["echo"], session=ses)
    v = _serve(pg, echo, q)
    assert v["reply"] == "echo, what is today's date?\necho repeats; ask the librarian for the date"
    assert resident.echo_reply("echo", "can you plan the day?").endswith("ask the librarian for an answer")
    # the glass: "today's date" names no window; the journey draws a window only when one rode the ask
    assert "(today|yesterday)'s" in GLASS and "names no window" in GLASS
    # firmware without a gateway keeps its plain name (P6 sp4's cure stands)
    planner = _body("firmware-planner.v0.json"); planner.join(pg)
    [p] = dispatch.submit_ask(pg, "plan it", person=ME, to=["planner"], session=ses)
    assert _serve(pg, planner, p)["reply"].startswith("I am planner — the planner, a firmware body")
