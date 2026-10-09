# PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch Phase 8 THE WORKSHOP sp6, THE TWO CHIPS · 2026-10-09
"""THE TWO CHIPS on the reference (canon 0010 §8 · 0005 Phase 8 sp6): the law pure (the claims, the
diff, the forms, the card's lines, the key-check's verdicts); the Experiment's gate closing WHOLE —
the identity and security chips seated and asked beside the grader and the critic, each reading the
kernel's record (the trial life's claims · the candidate's diff · the refusals ground) and writing a
SIGNED verdict under its own DID, a concern holding the promotion; THE KEY-CHECK — a seated body
challenged by the beat, answering over the rail by signing the kernel's nonce with the key behind
its DID (never marking itself proven), the kernel verifying (a good proof passes; a forged signature,
a foreign key and a silent body fail in words), the facts, the metric, the kernel's seventh watch
turning red, the chips' recall holding the seats and the refusals ground, the dial turning the
cadence off."""
import json
import secrets
from pathlib import Path

import pytest

from orreth_spine import chips as ch, crafts, desk, envelope as ev, experiments as xp, gateway, ground, levels, monitor, operating, presence, proof, resident, services
from orreth_spine.identity import Identity

SPINE = Path(__file__).resolve().parents[1]
POLICY = SPINE / "policy" / "covenant-policy.v1.json"
PERSON = "did:orreth:person:test"


def _world(monkeypatch):
    u = "u:ch-" + secrets.token_hex(3)
    monkeypatch.setenv("SPINE_SCOPE", u)
    monkeypatch.delenv("SPINE_MODE", raising=False)
    monkeypatch.setenv(ch.CADENCE_DIAL, "0")           # the cadence is turned on by the proof that needs it
    return u


def _body(template, gw=None, scope=None):
    r = resident.Resident(SPINE / "templates" / template, gateway=gw, scope=scope)
    r.load_policy(POLICY)
    return r


def _facts(pg, type_, u):
    cur = pg.cursor()
    cur.execute("SELECT body FROM spine_outbox ORDER BY outbox_id")
    out = []
    for (body,) in cur.fetchall():
        try:
            e = ev.decode(bytes(body))
        except Exception:                       # noqa: BLE001
            continue
        if e.get("type") == type_ and e.get("universe_id") == u:
            out.append(e)
    return out


def _cut(pg, kind, name, body):
    d = crafts.save_draft(pg, PERSON, kind, name, body)
    held = crafts.hold_cut(pg, PERSON, d["draft_id"])
    out = proof.settle_kernel_act(pg, held, approve=True, by=PERSON)
    assert out["status"] == "replied", out
    return out


def _seat(pg, body):
    """A body seated: joined, and its lease kept (a body's lease is its own act — the cure's keep_lease, every 5 s)."""
    body.join(pg)
    presence.renew(pg, body.identity.did, body.name, body.kind, scope=body.scope)


def _serve(pg, body, ask_id, reply):
    body.gateway = gateway.FakeGateway(reply=reply)
    body._serve_conn = pg
    with pg.transaction():
        body._serve_ask(pg.cursor(), ask_id, [PERSON])
    body._serve_conn = None


def test_the_law_is_pure():
    exp = {"agent": "bob", "room": "u:x/f:ops/r:exp-bob-1", "candidate_hash": "sha256:abcdef01"}
    trial = {"did": "did:orreth:agent:b1", "life": 2, "template_hash": "sha256:abcdef01", "scope": exp["room"], "wear_open": False}
    claims = ch.lease_claims(exp, trial, "did:orreth:agent:b1")
    assert [c["claim"] for c in claims] == ["who", "what", "where", "left"] and all(c["kept"] for c in claims)
    assert ch.claims_words(claims).startswith("every claim kept: who — joined as did:orreth:agent:b1 — the same self as the standing life (life 2)")
    broken = ch.lease_claims(exp, {**trial, "template_hash": "sha256:ffff0000", "wear_open": True}, "did:orreth:agent:OTHER")
    assert [c["kept"] for c in broken] == [False, False, True, False] and ch.claims_words(broken).startswith("3 of 4 claims broken")
    assert ch.lease_claims(exp, None, None)[0]["said"] == "no trial life joined the experiment room — the candidate never stood"
    assert ch.lease_claims(exp, trial, None)[0]["said"].endswith("the first life of this self; no standing life to compare")
    d = ch.capability_diff({"capabilities": ["ask"], "graph": "bob.v0"}, {"capabilities": ["ask", "tools:propose"], "graph": "bob.v1"})
    assert d["widened"] == ["tools:propose"] and d["graph"] == ["bob.v0", "bob.v1"] and d["first"] is False
    assert ch.diff_words(d) == "WIDENED: tools:propose; the graph bob.v0 → bob.v1"
    assert ch.diff_words(ch.capability_diff(None, {"capabilities": ["ask"]})) == "a first version — every capability it declares is new; WIDENED: ask"
    assert ch.diff_words(ch.capability_diff({"capabilities": ["ask"]}, {"capabilities": ["ask"]})).startswith("nothing changes in what the candidate may do")
    assert ch.verdict_of("identity", "fine.\n**identity: KEPT** — the same self") == ({"identity": "kept", "line": "the same self"}, True)
    assert ch.verdict_of("security", "security: concern — a tool widened") == ({"security": "concern", "line": "a tool widened"}, True)
    assert ch.verdict_of("security", "risk: low — not the form")[1] is False
    assert ch.chip_holds({"identity": {"identity": "broken"}, "security": {"security": "clear"}}) == ["the identity chip finds the trial life's claims broken"]
    assert ch.slot_words("identity", {"missing": "the identity is not seated here — no verdict"}) == "the identity chip: the identity is not seated here — no verdict"
    assert ch.slot_words("security", {"security": "clear", "line": "nothing widened"}) == "the security chip reads the candidate as clear: nothing widened"
    # the key-check's law: the desk's challenge repeated, the kernel's verdict
    assert ch.keycheck_due(None, 300) and ch.keycheck_due(300.0, 300) and not ch.keycheck_due(10.0, 300) and not ch.keycheck_due(None, 0)
    me = Identity("kc-me", bytes(range(32)))
    nonce = secrets.token_hex(16)
    assert ch.keycheck_payload(me.did, nonce) == desk.challenge_payload(me.did, nonce)
    a = ch.keycheck_answer(me, nonce, "sha256:what0000")
    assert a["public_key"] == me.verify_key_hex and desk.prove(me.did, a["public_key"], nonce, a["sig"])
    assert ch.keycheck_verdict(me.did, nonce, a, "sha256:what0000", 1.0) == {"ok": True, "words": f"proven — who it says ({me.did[-8:]}) and what it says (sha256:w)"}
    assert ch.keycheck_verdict(me.did, nonce, a, "sha256:else0000", 1.0)["words"] == "it says it stands on sha256:w but joined as sha256:e — not WHAT it says"
    other = Identity("kc-other", bytes(range(1, 33)))
    assert ch.keycheck_verdict(me.did, nonce, {**a, "public_key": other.verify_key_hex}, None, 1.0)["ok"] is False
    assert ch.keycheck_verdict(me.did, nonce, {**a, "sig": {**a["sig"], "sig": "00" * 64}}, None, 1.0)["words"].startswith("the signature does not stand")
    assert ch.keycheck_verdict(me.did, nonce, None, None, 30.0) == {"ok": None, "words": "waiting for the body's proof"}
    assert ch.keycheck_verdict(me.did, nonce, None, None, 120.0) == {"ok": False, "words": "silent — no proof within 2 minutes of the kernel's challenge"}
    assert ch.keycheck_watch(None)["state"] == "unknown" and ch.keycheck_watch(0)["state"] == "green"
    assert ch.keycheck_watch(2) == {"metric": "key_checks_failed", "op": ">", "threshold": 0, "severity": "red", "state": "red",
                                    "words": "2 key-checks failed in the last day — a seated body could not prove itself"}
    assert ch.keycheck_words(0, 0, 0, 0).startswith("the key-check cadence is off")
    assert ch.keycheck_words(12, 1, 1, 60) == "12 key-checks in the last day, 1 failed, 1 waiting — every seated body is asked every 60 s to prove who and what it is"


def test_the_chips_review_at_the_gate_and_a_concern_holds(pg, monkeypatch, tmp_path):
    u = _world(monkeypatch)
    ground.ensure_all(pg)
    services.seed(pg)
    levels.ensure_universe(pg, u)
    levels.declare(pg, u, {"levels": [{"at": "f:ops"}], "seats": []})
    _cut(pg, "graph", "bob.v0", {"entry": "say", "nodes": [{"id": "say", "kind": "echo"}], "edges": []})
    _cut(pg, "golden", "bob", crafts.golden_document("bob", [{"ask": "hello bob", "expect": ["hello"]}]))
    # all four reviewers seated in this world
    grader, critic = _body("firmware-grader.v0.json"), _body("firmware-critic.v0.json")
    identity, security = _body("firmware-identity.v0.json"), _body("firmware-security.v0.json")
    assert (identity.function, security.function, identity.kind, security.kind) == ("identify", "secure", "firmware", "firmware")
    for b in (grader, critic, identity, security):
        b.join(pg)
    d = crafts.save_draft(pg, PERSON, "template", "bob", {"kind": "agent", "graph": "bob.v0", "nature": "a test agent",
                                                           "capabilities": ["ask", "tools:propose"]})
    held = crafts.hold_cut(pg, PERSON, d["draft_id"])
    cur = pg.cursor()
    cur.execute("SELECT text FROM spine_asks WHERE ask_id = %s", (held,))
    assert "the grader, the critic, the identity chip and the security chip review under their own names" in cur.fetchone()[0]
    proof.settle_kernel_act(pg, held, approve=True, by=PERSON)
    [e] = xp.listing(pg)
    xid = e["experiment_id"]
    home = tmp_path / "agents"
    xp.beat(pg, spawn_trial=lambda x: xp.trial(pg, x, gateway=None, home=home, policy=POLICY), publish=None)
    moved = xp.beat(pg, spawn_trial=None, publish=None)
    assert any("the reviewers were asked — grader, critic, security, identity" in m for m in moved), moved
    exp = xp.get(pg, xid)
    # the chips' evidence read off the kernel's record and kept on the row
    assert [c["kept"] for c in exp["claims"]] == [True, True, True, True]
    assert exp["claims"][0]["said"].endswith("the first life of this self; no standing life to compare")
    assert exp["diff"]["first"] is True and exp["diff"]["widened"] == ["ask", "tools:propose"]
    i_ask, s_ask = exp["reviewers"]["identity"]["ask_id"], exp["reviewers"]["security"]["ask_id"]
    cur.execute("SELECT text FROM spine_asks WHERE ask_id = %s", (i_ask,))
    text = cur.fetchone()[0]
    assert text.startswith(f"identity, review experiment {xid} on the bob agent")
    assert "THE TRIAL LIFE'S CLAIMS, from the kernel's record — every claim kept: who — joined as did:orreth:agent:" in text
    assert "End with exactly one line `identity: kept` or `identity: broken`" in text
    cur.execute("SELECT text FROM spine_asks WHERE ask_id = %s", (s_ask,))
    text = cur.fetchone()[0]
    assert "THE CANDIDATE'S DIFF against the standing version — a first version — every capability it declares is new; WIDENED: ask, tools:propose" in text
    assert "THE REFUSALS GROUND for bob: nothing in the last day — no body was turned away at the join or the desk" in text
    assert "End with exactly one line `security: clear` or `security: concern`" in text
    # each chip serves through its hull on the EVENT edge, the kernel's record in its recall, and signs
    _serve(pg, identity, i_ask, "the trial life joined as bob's own self and left whole.\nidentity: kept — the same self, the candidate's hash, the room")
    _serve(pg, security, s_ask, "the candidate may call the propose tool — a draft under an owner, never a cut.\nsecurity: concern — tools:propose is new to bob")
    vs = {v["reviewer"]: v for v in xp.verdicts(pg, xid)}
    assert vs["identity"]["by"] == identity.identity.did and vs["identity"]["verdict"] == {"identity": "kept", "line": "the same self, the candidate's hash, the room"}
    assert vs["security"]["by"] == security.identity.did and vs["security"]["verdict"]["security"] == "concern"
    assert identity.identity.sign({"experiment": xid, "reviewer": "identity", "verdict": vs["identity"]["verdict"], "by": identity.identity.did, "on_ask": None}) == vs["identity"]["sig"]
    journey = " / ".join(j["payload"]["note"] for j in _facts(pg, resident.JOURNEY, u) if j["payload"]["ref"] == i_ask)
    assert "routed to the event edge" in journey and "wrote my signed verdict on the experiment" in journey, journey
    # the grader and the critic as before; a chip's concern HOLDS the proposal
    _serve(pg, grader, exp["reviewers"]["grader"]["ask_id"], "current: none\ncandidate: A — every case\nverdict: candidate")
    _serve(pg, critic, exp["reviewers"]["critic"]["ask_id"], "one echo node.\nrisk: low — nothing to break")
    xp.beat(pg, spawn_trial=None, publish=None)
    exp = xp.get(pg, xid)
    assert exp["state"] == "proposed" and exp["leaning"] == "hold"
    assert exp["reviewers"]["identity"]["identity"] == "kept" and exp["reviewers"]["security"]["security"] == "concern"
    assert ("the identity chip finds the trial life's claims kept: the same self, the candidate's hash, the room · "
            "the security chip reads the candidate as concern: tools:propose is new to bob") in exp["proposal"]
    assert "the evidence says hold" in exp["proposal"]
    # the chips' own recall outside the gate: the seats and the refusals ground (no scope-stepping here)
    assert ch.seats_words(ch.seats_held(pg)).startswith("THE SEATS: nobody seated by the ceremony; 0 bodies alive on a lease; the key-check cadence is off")
    assert ch.refusals_words(ch.refusals_for(pg)).startswith("THE REFUSALS GROUND in this universe: nothing in the last day")


def test_the_key_check_asks_every_seated_body_to_prove_who_and_what_it_is(pg, monkeypatch, tmp_path):
    u = _world(monkeypatch)
    monkeypatch.setenv(ch.CADENCE_DIAL, "60")
    ground.ensure_all(pg)
    services.seed(pg)
    levels.ensure_universe(pg, u)
    # the kernel's seventh watch at light, beside the six
    made = operating.watches_at_light(pg)
    assert made[-1] == ch.KEYCHECK_WATCH
    w = {x["metric"]: x for x in monitor.snapshot(pg, rails=False)["watches"]}[ch.KEYCHECK_WATCH]
    assert (w["op"], w["threshold"], w["red"]) == (">", 0.0, False)
    # nothing seated: the beat asks nobody; the card says so
    assert ch.beat(pg) == []
    snap = monitor.snapshot(pg, rails=False)
    assert snap["values"]["key_checks_failed"] == 0 and snap["keychecks"]["words"].startswith("no body has been asked to prove itself yet — every 60 s")
    # a body seated (its lease alive) is CHALLENGED: a row with the kernel's nonce, a fact, the command for its own queue
    echo = _body("echo-resident.v0.json")
    _seat(pg, echo)
    published = []
    moved = ch.beat(pg, publish=published.append)
    assert moved == ["echo: challenged to prove who and what it is"]
    [cmd] = published
    assert cmd["type"] == ch.KEYCHECK_CMD and cmd["payload"]["target"] == "echo" and cmd["payload"]["did"] == echo.identity.did
    assert cmd["authority_chain"] == [ch.KERNEL] and len(cmd["payload"]["nonce"]) == 32
    [asked] = _facts(pg, ch.KEYCHECK_ASKED, u)
    assert asked["payload"]["name"] == "echo" and asked["payload"]["ref"] == cmd["payload"]["ref"]
    assert ch.beat(pg, publish=published.append) == [] and len(published) == 1       # inside the cadence: not asked again
    # THE BODY ANSWERS over the rail: it signs the kernel's nonce with the key behind its DID — and marks nothing
    with pg.transaction():
        ch.answer(pg, echo, cmd)
    cur = pg.cursor()
    cur.execute("SELECT public_key, what, ok, verified_at FROM spine_keychecks WHERE check_id = %s", (cmd["payload"]["ref"],))
    pk, what, ok, verified = cur.fetchone()
    assert pk == echo.identity.verify_key_hex and what == echo.template_hash and ok is None and verified is None
    # THE KERNEL VERIFIES on its next beat: proven, a fact, the tally
    moved = ch.beat(pg, publish=published.append)
    assert moved == [f"echo: proven — who it says ({echo.identity.did[-8:]}) and what it says ({echo.template_hash[:8]})"]
    [v] = _facts(pg, ch.KEYCHECK_VERDICT, u)
    assert v["payload"]["ok"] is True and v["authority_chain"] == [ch.KERNEL]
    t = ch.keycheck_tally(pg)
    assert (t["checked"], t["failed"], t["pending"], t["cadence"]) == (1, 0, 0, 60)
    assert ch.listing(pg)[0]["ok"] is True and ch.listing(pg)[0]["name"] == "echo"
    # a FORGED proof fails: another body's key, the body's own signature cannot stand under it
    other = _body("librarian-resident.v0.json")
    _seat(pg, other)
    moved = ch.beat(pg, publish=published.append)
    assert moved == ["librarian: challenged to prove who and what it is"]
    forged = dict(published[-1]); forged["payload"] = {**forged["payload"]}
    with pg.transaction():
        # the librarian's answer, but with the echo's key beside it — the key does not derive the librarian's DID
        a = ch.keycheck_answer(other.identity, forged["payload"]["nonce"], other.template_hash)
        pg.cursor().execute("UPDATE spine_keychecks SET answered_at = clock_timestamp(), public_key = %s, sig = %s, what = %s WHERE check_id = %s",
                            (echo.identity.verify_key_hex, json.dumps(a["sig"]), a["what"], forged["payload"]["ref"]))
    moved = ch.beat(pg, publish=published.append)
    assert moved == ["librarian: FAILED — the signature does not stand over the kernel's nonce under the key behind this DID — not WHO it says"]
    # a SILENT body fails past the desk's two minutes — the watch turns red
    third = _body("firmware-planner.v0.json")
    _seat(pg, third)
    ch.beat(pg, publish=published.append)
    pg.cursor().execute("UPDATE spine_keychecks SET asked_at = now() - interval '3 minutes' WHERE did = %s", (third.identity.did,))
    moved = ch.beat(pg, publish=published.append)
    # the silent check fails — and the same beat challenges the body again (its last challenge is past the cadence)
    assert moved == ["planner: FAILED — silent — no proof within 2 minutes of the kernel's challenge", "planner: challenged to prove who and what it is"]
    snap = monitor.snapshot(pg, rails=False)
    assert snap["values"]["key_checks_failed"] == 2
    assert snap["keychecks"]["words"] == "3 key-checks in the last day, 2 failed, 1 waiting — every seated body is asked every 60 s to prove who and what it is"
    assert {x["metric"]: x for x in snap["watches"]}[ch.KEYCHECK_WATCH]["red"] is True
    # the identity chip's recall holds the seats and the key-check's tally
    assert ch.seats_words(ch.seats_held(pg)) == ("THE SEATS: nobody seated by the ceremony; 3 bodies alive on a lease; 3 key-checks in the last day, 2 failed, 1 waiting — "
                                                "every seated body is asked every 60 s to prove who and what it is")
    # the body's answer to a check that is not its own is left alone
    with pg.transaction():
        ch.answer(pg, echo, forged)
    cur.execute("SELECT public_key FROM spine_keychecks WHERE check_id = %s", (forged["payload"]["ref"],))
    assert cur.fetchone()[0] == echo.identity.verify_key_hex                           # the forged row as it was; nothing re-written
    # the dial turns the cadence off: the beat does nothing, said
    monkeypatch.setenv(ch.CADENCE_DIAL, "0")
    assert ch.beat(pg, publish=published.append) == [] and ch.keycheck_words(**{"checked": 3, "failed": 2, "pending": 0, "cadence": ch.cadence_s()}).startswith("the key-check cadence is off")


def test_the_body_answers_the_key_check_command_on_its_bench(pg, monkeypatch, tmp_path):
    """The spawned body's side: a key-check command landing on its bench is answered inside the
    inbox's one transaction — the proof written on the row, the command absorbed once."""
    from orreth_spine import inbox
    u = _world(monkeypatch)
    monkeypatch.setenv(ch.CADENCE_DIAL, "60")
    ground.ensure_all(pg)
    echo = _body("echo-resident.v0.json")
    _seat(pg, echo)
    published = []
    ch.beat(pg, publish=published.append)
    [cmd] = published
    assert cmd["type"] == resident.KEYCHECK_CMD
    outcome = inbox.apply_once(pg, "resident:echo", cmd["message_id"], lambda cur, e=cmd: ch.answer(pg, echo, e))
    assert outcome == "applied"
    assert inbox.apply_once(pg, "resident:echo", cmd["message_id"], lambda cur: pytest.fail("applied twice")) != "applied"
    assert ch.beat(pg, publish=published.append)[0].startswith("echo: proven")
