# PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P4 sp2, the includes edge · 2026-09-18
"""The third kind (0004 · block 9): firmware agents — same body of laws,
no persona, named by function — called as INCLUDES over the residents'
results in a session. AG-8: the include wears the chain (H → the residents
whose results it read → the firmware); the grader is scribe-class and
never grades its own yardstick (covenant rule 2)."""
import json
import secrets
from pathlib import Path

from orreth_spine import dispatch, envelope as ev, gateway, glass, resident

SPINE = Path(__file__).resolve().parents[1]
POLICY = SPINE / "policy" / "covenant-policy.v1.json"
ME = "did:orreth:person:test"


def _body(template, gw=None):
    r = resident.Resident(SPINE / "templates" / template, gateway=gw)
    r.load_policy(POLICY)
    return r


def _landed(pg, ask_id, by, text, reply, session):
    """A reply on the ground as if served: the material an include reads."""
    pg.cursor().execute(
        "UPDATE spine_asks SET status = 'replied', served_by = %s, reply = %s,"
        " replied_at = now() WHERE ask_id = %s", (by, reply, ask_id))


def _journey_chains(pg, ask_id):
    cur = pg.cursor()
    cur.execute("SELECT body FROM spine_outbox WHERE convert_from(body, 'UTF8')"
                " LIKE %s", (f"%{ask_id}%",))
    out = []
    for (b,) in cur.fetchall():
        e = ev.decode(bytes(b))
        if e["type"] == resident.JOURNEY:
            out.append((e["payload"]["note"], e.get("authority_chain") or []))
    return out


def test_the_include_wears_the_chain_and_reads_the_session(pg, monkeypatch):
    """AG-8: the planner, asked as an include in a session where the echo
    and the librarian answered, reads BOTH results (labeled) and lands a
    journey whose chain is H → the residents read → the planner."""
    monkeypatch.setenv("SPINE_SCOPE", "u:law-" + secrets.token_hex(3))
    echo, lib = _body("echo-resident.v0.json"), _body("librarian-resident.v0.json")
    echo.join(pg); lib.join(pg)
    ses = glass.open_session(pg, ME)
    tok_e, tok_l = secrets.token_hex(3), secrets.token_hex(3)
    _landed(pg, dispatch.submit_ask(pg, "what is the plan?", session=ses),
            echo.identity.did, "", f"the echo's view: marker {tok_e}", ses)
    _landed(pg, dispatch.submit_ask(pg, "and the risk?", session=ses),
            lib.identity.did, "", f"the librarian's view: marker {tok_l}", ses)
    gw = gateway.FakeGateway(reply="1. do the first thing (librarian) 2. then the second (echo)")
    planner = _body("firmware-planner.v0.json", gw)
    planner.join(pg); planner._serve_conn = pg
    [ask_id] = dispatch.submit_ask(pg, "Plan the next steps from what was said here.",
                                   to=["planner"], session=ses)   # targeted: a list
    with pg.transaction():
        planner._serve_ask(pg.cursor(), ask_id, [ME])
    view = glass.ask_view(pg, ask_id)
    assert view["status"] == "replied" and view["served_by"] == planner.identity.did
    prompt = gw.calls[0]["prompt"]
    assert f"marker {tok_e}" in prompt and f"marker {tok_l}" in prompt      # both read,
    assert "echo replied" in prompt and "librarian replied" in prompt      # labeled
    assert "firmware agent" in gw.calls[0]["system"] and "no persona" in gw.calls[0]["system"]
    chains = _journey_chains(pg, ask_id)
    assert any("read the session's results by" in n for n, _ in chains)
    for _note, chain in chains:                                             # H → read → me
        assert chain[0] == ME and chain[-1] == planner.identity.did
        assert {echo.identity.did, lib.identity.did} <= set(chain[1:-1])
    assert planner.kind == "firmware" and planner.function == "plan"


def test_the_grader_never_grades_its_own_yardstick(pg, monkeypatch):
    """Scribe-class (covenant rule 2): with nothing in the session but its
    own words, the grader refuses — before any thinking — and says so; the
    refusal is a reply, the journey says why."""
    monkeypatch.setenv("SPINE_SCOPE", "u:law-" + secrets.token_hex(3))
    gw = gateway.FakeGateway(reply="A — should never be reached")
    grader = _body("firmware-grader.v0.json", gw)
    grader.join(pg); grader._serve_conn = pg
    ses = glass.open_session(pg, ME)
    _landed(pg, dispatch.submit_ask(pg, "grade this", to=["grader"], session=ses)[0],
            grader.identity.did, "", "B — my own earlier grade", ses)
    [ask_id] = dispatch.submit_ask(pg, "Grade the answers in this session.",
                                   to=["grader"], session=ses)
    with pg.transaction():
        grader._serve_ask(pg.cursor(), ask_id, [ME])
    view = glass.ask_view(pg, ask_id)
    assert view["status"] == "replied"
    assert "never grade my own yardstick" in view["reply"]
    assert gw.calls == []                                   # no thinking spent
    assert any("scribe-class" in n for n, _ in _journey_chains(pg, ask_id))


def test_the_crew_door_tells_the_kinds(pg, monkeypatch):
    """The rail shows residents; the includes edge shows firmware — the
    crew door says which is which."""
    monkeypatch.setenv("SPINE_SCOPE", "u:law-" + secrets.token_hex(3))
    _body("echo-resident.v0.json").join(pg)
    _body("firmware-critic.v0.json").join(pg)
    kinds = {x["name"]: x["kind"] for x in glass.residents_view(pg)}
    assert kinds == {"echo": "resident", "critic": "firmware"}
