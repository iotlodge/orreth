# PROVENANCE: Claude Fable 5 (claude-fable-5) — rearch P2 sp3, the soul checkpoint · 2026-09-16
"""The soul checkpoint's laws (canon 0001 · 0004): a resident acts only
through the governed tool door (undeclared tools refuse WITH a
teaching); every act is journaled; a consequential act HOLDS at the L2
interlock — a deliberate yes releases it, anything else cancels and the
act NEVER ran; and — live, key present — the librarian tells JB the
temperature outside, through the whole road."""
import json
import os
import secrets
from pathlib import Path

import pytest

from orreth_spine import dispatch, gateway, resident, tools
from tests.test_resident import _purge_queue, _serve_until_replied

SPINE = Path(__file__).resolve().parents[1]
LIBRARIAN = SPINE / "templates" / "librarian-resident.v0.json"
POLICY = SPINE / "policy" / "covenant-policy.v1.json"

from tests.test_mind import _rails_up, _walk  # noqa: E402

rails = pytest.mark.skipif(
    not (os.environ.get("SPINE_REQUIRE_KAFKA") or _rails_up()),
    reason="the rails are not up — start spine/compose.yaml")


# ---- the door's laws (ground only) -----------------------------------------------

def test_undeclared_tools_refuse_with_a_teaching(pg):
    door = tools.ToolDoor(pg, did="did:orreth:agent:t1",
                          capabilities=["ask"])
    assert door.schemas() == []                # the mind never sees them
    with pytest.raises(tools.ToolRefused, match="never declared"):
        door.call("weather", {})
    assert tools.journal(pg, "did:orreth:agent:t1") == []


def test_consequential_holds_without_confirmation(pg):
    door = tools.ToolDoor(pg, did="did:orreth:agent:t2",
                          capabilities=["tools:seal-record"])
    with pytest.raises(tools.ConsequentialHold) as h:
        door.call("seal-record", {"key": "k1"})
    assert h.value.tool == "seal-record"
    assert tools.journal(pg, "did:orreth:agent:t2") == []   # NEVER ran
    out = door.call("seal-record", {"key": "k1"}, confirmed=True)
    assert "Sealed" in out
    assert tools.journal(pg, "did:orreth:agent:t2") == [("seal-record", True)]


# ---- the interlock, end to end (fake acting mind, real door) ---------------------

@rails
def test_the_interlock_holds_then_the_yes_releases(pg):
    tok = secrets.token_hex(4)
    gw = gateway.FakeActingGateway(
        script=[("tool", "seal-record", {"key": f"note-{tok}"}),
                ("text", "sealed: {result}")])
    r = resident.Resident(LIBRARIAN, gateway=gw)
    r.load_policy(POLICY)
    r.join(pg)
    _purge_queue()
    ask_id = dispatch.submit_ask(pg, f"Seal my note {tok} forever.")
    from orreth_spine import outbox, sinks
    assert outbox.drain(pg, sinks.KafkaSink()) >= 1
    dispatch.dispatch_once(pg, consumer="test-dispatcher", group="test-dispatcher")
    r.serve_once(pg, idle_s=2.0, max_commands=100)
    cur = pg.cursor()
    cur.execute("SELECT status, reply, held FROM spine_asks"
                " WHERE ask_id = %s", (ask_id,))
    status, reply, held = cur.fetchone()
    assert status == "awaiting-confirm"
    assert "Are you sure" in reply and "cancel is the default" in reply.lower()
    assert json.loads(held)["tool"] == "seal-record"
    assert tools.journal(pg, r.identity.did) == []          # held = never ran
    # the deliberate yes
    dispatch.confirm_ask(pg, ask_id, approve=True)
    status, reply, _by = _serve_until_replied(pg, r, ask_id)
    assert status == "replied" and "Done, on your word" in reply
    assert tools.journal(pg, r.identity.did) == [("seal-record", True)]


@rails
def test_cancel_is_the_default_and_the_act_never_ran(pg):
    tok = secrets.token_hex(4)
    gw = gateway.FakeActingGateway(
        script=[("tool", "seal-record", {"key": f"note-{tok}"}),
                ("text", "sealed: {result}")])
    r = resident.Resident(LIBRARIAN, gateway=gw)
    r.load_policy(POLICY)
    r.join(pg)
    _purge_queue()
    ask_id = dispatch.submit_ask(pg, f"Seal my other note {tok} forever.")
    from orreth_spine import outbox, sinks
    assert outbox.drain(pg, sinks.KafkaSink()) >= 1
    dispatch.dispatch_once(pg, consumer="test-dispatcher", group="test-dispatcher")
    r.serve_once(pg, idle_s=2.0, max_commands=100)
    dispatch.confirm_ask(pg, ask_id, approve=False)    # the default: cancel
    import time as _t
    cur = pg.cursor()
    end = _t.monotonic() + 30
    while _t.monotonic() < end:
        r.serve_once(pg, idle_s=1.5, max_commands=100)
        cur.execute("SELECT status, reply FROM spine_asks WHERE ask_id=%s",
                    (ask_id,))
        status, reply = cur.fetchone()
        if status == "cancelled":
            break
    assert status == "cancelled" and "nothing was done" in reply.lower()
    assert tools.journal(pg, r.identity.did) == []     # the act NEVER ran


# ---- THE SOUL CHECKPOINT, LIVE ---------------------------------------------------

@rails
@pytest.mark.skipif(not os.environ.get("ANTHROPIC_API_KEY"),
                    reason="no ANTHROPIC_API_KEY — the live mind sleeps")
def test_the_librarian_tells_the_temperature_outside(pg):
    """The sentence that started the halt, made a passing test: the whole
    road — ask → dispatch → invoke → recall → the acting mind → the
    governed weather tool → journey → a full, plain-words reply with the
    REAL temperature in it."""
    tok = secrets.token_hex(4)
    gw = gateway.AnthropicGateway()
    r = resident.Resident(LIBRARIAN, gateway=gw)
    r.load_policy(POLICY)
    r.join(pg)
    _ask, (status, reply, _by) = _walk(
        pg, r, "What's the temperature outside?", tok)
    assert status == "replied"
    assert any(ch.isdigit() for ch in reply)            # a real number
    assert "°F" in reply or "degrees" in reply.lower() or "F" in reply
    assert tools.journal(pg, r.identity.did)[-1] == ("weather", True)
    lines = gateway.meter_lines(pg, r.identity.did)
    assert lines and lines[-1][1] > 0
    print(f"\n🌡️  THE SOUL CHECKPOINT — the librarian, live:\n{reply}\n"
          f"(tool journaled: weather ✓ · metered: {lines[-1][1]} in / "
          f"{lines[-1][2]} out)")
