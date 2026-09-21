# PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P6 sp1, L3: the proof demand rises · 2026-09-21
"""P6 sp1's laws (canon 0001 P12 · 0005): the code is RFC 6238 and
tolerates one step of drift; the ladder is routine < consequential <
grave → L1 < L2 < L3; an authenticator is enrolled once through the
chat and re-enrolling is grave (the old code); a grave tool holds for
the person's CODE — the right one executes and the record wears
L3-code, a wrong one refuses with ONE face, three wrongs REST the act
(a recorded cancel) and the chat says so; the kernel's own intention
holds for a MASTER — never the asker, a declared second person; cancel
is taken at every level; and the L2 path is untouched (test_soul)."""
import json
import os
import secrets
import time
import urllib.error
import urllib.request
from pathlib import Path

import pytest

from orreth_spine import dispatch, envelope as ev, gateway, intent, outbox, proof, resident, sinks, tools
from tests.test_mind import _rails_up
from tests.test_resident import _dispatch, _purge_queue, _serve_until_replied

SPINE = Path(__file__).resolve().parents[1]
LIBRARIAN = SPINE / "templates" / "librarian-resident.v0.json"
POLICY = SPINE / "policy" / "covenant-policy.v1.json"
SECRET = "GEZDGNBVGY3TQOJQGEZDGNBVGY3TQOJQ"          # base32 of "12345678901234567890"
ONE_FACE = {"error": "not confirmed"}

rails = pytest.mark.skipif(
    not (os.environ.get("SPINE_REQUIRE_KAFKA") or _rails_up()),
    reason="the rails are not up — start spine/compose.yaml")


def _person(tag: str) -> str:
    return f"did:orreth:person:{tag}-{secrets.token_hex(3)}"


def _enrolled(pg, person: str) -> str:
    """Enroll and confirm with the first code; returns the secret."""
    made = proof.enroll(pg, person)
    proof.confirm_enrollment(pg, person, proof.totp(made["secret"]))
    return made["secret"]


def _events_for(pg, ref: str) -> list[dict]:
    cur = pg.cursor()
    cur.execute("SELECT body FROM spine_outbox WHERE convert_from(body, 'UTF8') LIKE %s ORDER BY outbox_id",
                (f"%{ref}%",))
    return [ev.decode(bytes(b)) for (b,) in cur.fetchall()]


# ---- the code and the ladder (no ground) --------------------------------------------

def test_totp_is_rfc_6238_and_tolerates_one_step_of_drift():
    assert [proof.totp(SECRET, t) for t in (59, 1111111109, 1111111111, 1234567890, 2000000000)] \
        == ["287082", "081804", "050471", "005924", "279037"]
    t = 1111111111
    assert proof.verify(SECRET, "050471", t) and proof.verify(SECRET, "050471", t - 30) \
        and proof.verify(SECRET, "050471", t + 30)
    assert not proof.verify(SECRET, "050471", t - 60) and not proof.verify(SECRET, "050471", t + 60)
    assert not proof.verify(SECRET, "50471", t) and not proof.verify(SECRET, "", t) \
        and not proof.verify(SECRET, None, t) and not proof.verify(SECRET, "05047a", t)
    s = proof.mint_secret()
    assert len(s) == 32 and proof.verify(s, proof.totp(s))
    assert proof.otpauth_uri("did:orreth:person:jb", s).startswith("otpauth://totp/Orreth:jb?secret=" + s)
    qr = proof.qr_png_data_uri("otpauth://totp/Orreth:jb?secret=" + s)
    assert qr is None or qr.startswith("data:image/png;base64,iVBORw0KGgo")   # a real PNG, or honestly none


def test_the_ladder_routine_consequential_grave():
    assert sorted(["grave", "routine", "consequential"], key=proof.rank) == list(proof.CLASSES)
    assert [proof.level_for(c) for c in proof.CLASSES] == ["L1", "L2", "L3-code"]
    assert proof.level_for("grave", master=True) == "L3-master"
    with pytest.raises(ValueError):
        proof.rank("mild")
    assert tools.consequence_of(tools.TOOLS["weather"]) == "routine"
    assert tools.consequence_of(tools.TOOLS["seal-record"]) == "consequential"     # L2 keeps its class
    assert tools.consequence_of(tools.TOOLS["erase-record"]) == "grave"
    door = tools.ToolDoor.__new__(tools.ToolDoor)      # the door's hold names the level
    door.capabilities = ["tools:erase-record", "tools:seal-record"]
    with pytest.raises(tools.ConsequentialHold) as h:
        tools.ToolDoor.call(door, "erase-record", {"key": "k"})
    assert (h.value.consequence, h.value.level) == ("grave", "L3-code")
    with pytest.raises(tools.ConsequentialHold) as h2:
        tools.ToolDoor.call(door, "seal-record", {"key": "k"})
    assert (h2.value.consequence, h2.value.level) == ("consequential", "L2")


# ---- the authenticator and the masters (ground only) ----------------------------------

def test_enrollment_mints_confirms_and_re_enrolling_is_grave(pg):
    me = _person("enroll")
    assert not proof.enrolled(pg, me)
    made = proof.enroll(pg, me)
    assert made["uri"].startswith("otpauth://totp/Orreth:") and made["secret"] in made["uri"]
    assert not made["re_enrolled"] and not proof.enrolled(pg, me)          # pending until the first code
    with pytest.raises(proof.NotConfirmed):
        proof.confirm_enrollment(pg, me, "000000")
    proof.confirm_enrollment(pg, me, proof.totp(made["secret"]))
    assert proof.enrolled(pg, me) and proof.active_secret(pg, me) == made["secret"]
    with pytest.raises(proof.NotConfirmed):                                 # re-enrolling is grave:
        proof.enroll(pg, me)                                               # the OLD code, or the one face
    with pytest.raises(proof.NotConfirmed):
        proof.enroll(pg, me, code="123456")
    again = proof.enroll(pg, me, code=proof.totp(made["secret"]))
    assert again["re_enrolled"] and proof.active_secret(pg, me) == made["secret"]   # old stands until confirmed
    proof.confirm_enrollment(pg, me, proof.totp(again["secret"]))
    assert proof.active_secret(pg, me) == again["secret"]                  # the old one retired
    types = [e["type"] for e in _events_for(pg, me)]
    assert types.count(proof.AUTHENTICATOR_ENROLLED) == 2 and types.count(proof.AUTHENTICATOR_CONFIRMED) == 2
    assert not any(made["secret"] in json.dumps(e) for e in _events_for(pg, me))   # the secret never rides the rail


def test_masters_are_declared_on_the_ground_and_seeded_from_the_dial(pg, monkeypatch):
    a, b = _person("master"), _person("master")
    assert proof.declare_master(pg, a, by="did:orreth:person:jb") and not proof.declare_master(pg, a, by="x")
    assert proof.is_master(pg, a) and not proof.is_master(pg, b)
    monkeypatch.setenv("SPINE_MASTERS", f" {b}, {a} ,,")
    assert proof.seed_masters(pg) == [b]                                   # only the new one
    assert set(proof.masters(pg)) >= {a, b}
    assert any(e["type"] == proof.MASTER_DECLARED and e["payload"]["declared_by"] == "the SPINE_MASTERS dial"
               for e in _events_for(pg, b))


# ---- the kernel's own intention: L3-master, never the asker (ground only) -------------

def _kernel_intention(pg) -> dict:
    from orreth_spine import markers
    markers.seed(pg)                                                       # watch-red is the kernel's kind
    return intent.declared(pg, f"keep the {secrets.token_hex(2)} bench green", serves="resiliency",
                           kind="kernel", by="the kernel", interests=[intent.WATCH_RED],
                           planner="planner", runner="librarian")


def _hold_stop(pg, iid: str, person: str) -> str:
    with pytest.raises(proof.ProofRequired) as pr:                        # a bare stop refuses
        intent.stop(pg, iid, by=person)
    assert pr.value.level == "L3-master"
    return proof.hold_kernel_act(pg, text=pr.value.what, person=person, tool="intent.stop",
                                 args={"intention_id": iid}, level="L3-master")


def test_the_kernels_intention_holds_for_a_master_and_the_asker_is_never_their_own(pg):
    me, master, stranger = _person("asker"), _person("master"), _person("stranger")
    proof.declare_master(pg, master, by="did:orreth:person:jb")
    proof.declare_master(pg, me, by="did:orreth:person:jb")                # even a master cannot self-confirm
    r = _kernel_intention(pg)
    ask_id = _hold_stop(pg, r["intention_id"], me)
    cur = pg.cursor()
    cur.execute("SELECT status, served_by, held, reply FROM spine_asks WHERE ask_id = %s", (ask_id,))
    status, served_by, held, reply = cur.fetchone()
    assert status == "awaiting-confirm" and served_by == proof.KERNEL
    assert json.loads(held)["level"] == "L3-master" and "second named person" in reply
    hold_ev = [e for e in _events_for(pg, ask_id) if e["type"] == resident.CONFIRM_NEEDED]
    assert hold_ev and hold_ev[0]["payload"]["level"] == "L3-master" and hold_ev[0]["payload"]["class"] == "grave"
    assert not any(e["type"] == resident.ASK_RECEIVED for e in _events_for(pg, ask_id))   # never dispatched
    for who in (me, stranger):                                             # the asker · a stranger: one face
        with pytest.raises(proof.NotConfirmed):
            dispatch.confirm_ask(pg, ask_id, approve=True, person=who)
    assert intent.get(pg, r["intention_id"])["active"] is True             # nothing ran
    with pytest.raises(proof.NotConfirmed):                                # an ask nobody holds: the same face
        dispatch.confirm_ask(pg, "ask_nobody", approve=True, person=master)
    out = dispatch.confirm_ask(pg, ask_id, approve=True, person=master)    # the named second person
    assert out["level"] == "L3-master"
    stopped = intent.get(pg, r["intention_id"])
    assert stopped["active"] is False and stopped["stopped_by"] == me
    cur.execute("SELECT status, proof, reply FROM spine_asks WHERE ask_id = %s", (ask_id,))
    status, level, reply = cur.fetchone()
    assert (status, level) == ("replied", "L3-master") and "at rest" in reply
    evs = _events_for(pg, ask_id)
    assert any(e["type"] == resident.REPLY and e["payload"]["proof"] == "L3-master" for e in evs)
    assert any(e["type"] == resident.JOURNEY and "confirmed as master" in e["payload"]["note"] for e in evs)
    st = [e for e in _events_for(pg, r["intention_id"]) if e["type"] == intent.INTENTION_STOPPED]
    assert st and st[0]["payload"]["proof"] == "L3-master" and st[0]["payload"]["confirmed_by"] == master
    assert [a[2] for a in proof.attempts(pg, ask_id)] == [False, False, True]
    with pytest.raises(proof.NotConfirmed):                                # settled: nothing held any more
        dispatch.confirm_ask(pg, ask_id, approve=True, person=master)


def test_cancel_is_taken_at_l3_master_and_three_wrong_proofs_rest_the_act(pg):
    me, stranger = _person("asker"), _person("stranger")
    r = _kernel_intention(pg)
    ask_id = _hold_stop(pg, r["intention_id"], me)
    dispatch.confirm_ask(pg, ask_id, approve=False, person=me)             # cancel: always taken (rule 11)
    cur = pg.cursor()
    cur.execute("SELECT status, proof, reply FROM spine_asks WHERE ask_id = %s", (ask_id,))
    assert cur.fetchone() == ("cancelled", "L1", "Cancelled — nothing was done. Cancel is always the default here.")
    assert intent.get(pg, r["intention_id"])["active"] is True
    ask2 = _hold_stop(pg, r["intention_id"], me)                           # three wrong proofs
    for _ in range(3):
        with pytest.raises(proof.NotConfirmed):
            dispatch.confirm_ask(pg, ask2, approve=True, person=stranger)
    cur.execute("SELECT status, reply FROM spine_asks WHERE ask_id = %s", (ask2,))
    status, reply = cur.fetchone()
    assert status == "cancelled" and reply.startswith("Rested — three wrong proofs")
    assert intent.get(pg, r["intention_id"])["active"] is True             # the act never ran
    assert any(e["type"] == resident.JOURNEY and "three wrong proofs" in e["payload"]["note"]
               for e in _events_for(pg, ask2))
    with pytest.raises(proof.NotConfirmed):                                # a fourth: nothing held
        dispatch.confirm_ask(pg, ask2, approve=True, person=stranger)


# ---- a grave tool: L3-code through the whole road (rails) -----------------------------

def _keeper(tmp_path: Path, gw) -> resident.Resident:
    """A test body that declares the grave tool — no template of the
    house does; the librarian keeps its shelf."""
    t = json.loads(LIBRARIAN.read_text())
    t["name"] = "keeper"
    t["capabilities"] = ["ask", "tools:seal-record", "tools:erase-record"]
    t.pop("schedules", None)
    p = tmp_path / "keeper.v0.json"
    p.write_text(json.dumps(t))
    r = resident.Resident(p, gateway=gw)
    r.load_policy(POLICY)
    return r


def _serve_until(pg, r, ask_id, want, deadline_s=30.0):
    end = time.monotonic() + deadline_s
    cur = pg.cursor()
    while time.monotonic() < end:
        r.serve_once(pg, idle_s=1.5, max_commands=100)
        cur.execute("SELECT status, reply, proof FROM spine_asks WHERE ask_id = %s", (ask_id,))
        row = cur.fetchone()
        if row and row[0] == want:
            return row
    raise AssertionError(f"{ask_id} never reached {want}")


@rails
def test_l3_code_the_right_code_executes_and_the_record_wears_it(pg, tmp_path):
    me = _person("coder")
    secret = _enrolled(pg, me)
    gw = gateway.FakeActingGateway(script=[("tool", "erase-record", {"key": "note-{tok}"}),
                                           ("text", "erased: {result}")])
    r = _keeper(tmp_path, gw)
    r.join(pg)
    _purge_queue()
    tok = secrets.token_hex(3)
    gw.script[0] = ("tool", "erase-record", {"key": f"note-{tok}"})   # the key follows the ask
    [ask_id] = dispatch.submit_ask(pg, f"Erase the sealed note {tok}.", person=me, to=["keeper"])
    assert outbox.drain(pg, sinks.KafkaSink()) >= 1
    _dispatch(pg)
    r.serve_once(pg, idle_s=2.0, max_commands=100)
    cur = pg.cursor()
    cur.execute("SELECT status, reply, held FROM spine_asks WHERE ask_id = %s", (ask_id,))
    status, reply, held = cur.fetchone()
    assert status == "awaiting-confirm" and reply.startswith("This needs your code")
    assert json.loads(held)["level"] == "L3-code"
    hold_ev = [e for e in _events_for(pg, ask_id) if e["type"] == resident.CONFIRM_NEEDED]
    assert hold_ev[0]["payload"]["level"] == "L3-code" and hold_ev[0]["payload"]["class"] == "grave"
    with pytest.raises(proof.NotConfirmed):                                 # a wrong code: one face
        dispatch.confirm_ask(pg, ask_id, approve=True, person=me, code="000000")
    with pytest.raises(proof.NotConfirmed):                                 # a click with no code: the same
        dispatch.confirm_ask(pg, ask_id, approve=True, person=me)
    assert tools.journal(pg, r.identity.did) == []
    out = dispatch.confirm_ask(pg, ask_id, approve=True, person=me, code=proof.totp(secret))
    assert out["level"] == "L3-code"
    status, reply, level = _serve_until(pg, r, ask_id, "replied")
    assert "Done, on your word" in reply and "Erased" in reply and level == "L3-code"
    assert tools.journal(pg, r.identity.did) == [("erase-record", True)]
    evs = _events_for(pg, ask_id)
    assert any(e["type"] == resident.REPLY and e["payload"]["proof"] == "L3-code" for e in evs)
    assert any(e["type"] == resident.JOURNEY and "the code was right" in e["payload"]["note"]
               and "proof L3-code" in e["payload"]["note"] for e in evs)
    assert [a[2] for a in proof.attempts(pg, ask_id)] == [False, False, True]


@rails
def test_three_wrong_codes_rest_the_act_and_the_chat_says_so(pg, tmp_path):
    me = _person("fumbler")
    _enrolled(pg, me)
    tok = secrets.token_hex(3)
    gw = gateway.FakeActingGateway(script=[("tool", "erase-record", {"key": f"note-{tok}"}),
                                           ("text", "erased: {result}")])
    r = _keeper(tmp_path, gw)
    r.join(pg)
    _purge_queue()
    [ask_id] = dispatch.submit_ask(pg, f"Erase the sealed note {tok}.", person=me, to=["keeper"])
    assert outbox.drain(pg, sinks.KafkaSink()) >= 1
    _dispatch(pg)
    r.serve_once(pg, idle_s=2.0, max_commands=100)
    for _ in range(3):
        with pytest.raises(proof.NotConfirmed):
            dispatch.confirm_ask(pg, ask_id, approve=True, person=me, code="123456")
    status, reply, level = _serve_until(pg, r, ask_id, "cancelled")
    assert reply.startswith("Rested — three wrong proofs") and level == "L1"
    assert tools.journal(pg, r.identity.did) == []                          # the act never ran
    assert any(e["type"] == resident.JOURNEY and "three wrong proofs" in e["payload"]["note"]
               for e in _events_for(pg, ask_id))
    with pytest.raises(proof.NotConfirmed):                                 # rested: nothing held
        dispatch.confirm_ask(pg, ask_id, approve=True, person=me, code="123456")
    # a person with NO authenticator at all: the same face, and cancel still works
    nobody = _person("unenrolled")
    tok2 = secrets.token_hex(3)
    gw.script[0] = ("tool", "erase-record", {"key": f"note-{tok2}"})
    [ask2] = dispatch.submit_ask(pg, f"Erase the sealed note {tok2}.", person=nobody, to=["keeper"])
    assert outbox.drain(pg, sinks.KafkaSink()) >= 1
    _dispatch(pg)
    r.serve_once(pg, idle_s=2.0, max_commands=100)
    with pytest.raises(proof.NotConfirmed):
        dispatch.confirm_ask(pg, ask2, approve=True, person=nobody, code="000000")
    dispatch.confirm_ask(pg, ask2, approve=False, person=nobody)            # cancel at every level
    status, reply, _ = _serve_until(pg, r, ask2, "cancelled")
    assert "nothing was done" in reply.lower()


# ---- the doors, in the standing rig: ONE face over HTTP -------------------------------

def _post(port, path, obj):
    req = urllib.request.Request(f"http://127.0.0.1:{port}{path}", data=json.dumps(obj).encode(),
                                 headers={"content-type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())


def _get(port, path):
    with urllib.request.urlopen(f"http://127.0.0.1:{port}{path}", timeout=10) as r:
        return json.loads(r.read())


@rails
def test_the_doors_enroll_hold_the_kernels_intention_and_wear_one_face(pg, rig):
    port = rig.port
    me = "did:orreth:person:jb"
    assert _get(port, f"/proof?person={me}") == {"person": me, "enrolled": False, "masters": []}
    s, b = _post(port, "/enroll", {"person": me})
    assert s == 201 and b["uri"].startswith("otpauth://totp/Orreth:jb") and b["qr"].startswith("data:image/png;base64,")
    assert _post(port, "/enroll/confirm", {"person": me, "code": "000000"}) == (403, ONE_FACE)
    assert _post(port, "/enroll/confirm", {"person": me, "code": proof.totp(b["secret"])}) == (200, {"person": me, "enrolled": True})
    assert _get(port, f"/proof?person={me}")["enrolled"] is True
    assert _post(port, "/enroll", {"person": me}) == (403, ONE_FACE)          # re-enrolling is grave
    assert _post(port, "/confirm", {"ask_id": "ask_nobody", "approve": True}) == (403, ONE_FACE)
    for _ in range(150):                                                     # Resiliency, declared at boot
        ints = [i for i in _get(port, "/intentions")["intentions"] if i["kind"] == "kernel"]
        if ints:
            break
        time.sleep(0.2)
    [res] = ints
    s, b = _post(port, "/intentions/stop", {"intention_id": res["intention_id"], "person": me})
    assert s == 202 and b["level"] == "L3-master" and b["held"].startswith("ask_")
    view = _get(port, "/ask/" + b["held"])
    assert view["status"] == "awaiting-confirm" and view["served_by"] == "the kernel"
    assert view["hold"] == {"tool": "intent.stop", "class": "grave", "level": "L3-master"}
    assert "second named person" in view["reply"] and view["proof"] == "L1"
    assert _post(port, "/confirm", {"ask_id": b["held"], "approve": True, "by": me}) == (403, ONE_FACE)
    assert _post(port, "/confirm", {"ask_id": b["held"], "approve": True, "by": "did:orreth:person:nobody"}) == (403, ONE_FACE)
    s, c = _post(port, "/confirm", {"ask_id": b["held"], "approve": False})    # cancel, at every level
    assert s == 202 and c["level"] == "L3-master"
    view = _get(port, "/ask/" + b["held"])
    assert view["status"] == "cancelled" and view["hold"] is None and "nothing was done" in view["reply"].lower()
    assert [i for i in _get(port, "/intentions")["intentions"] if i["intention_id"] == res["intention_id"]][0]["active"] is True
