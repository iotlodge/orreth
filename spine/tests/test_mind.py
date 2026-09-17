# PROVENANCE: Claude Fable 5 (claude-fable-5) — rearch P2 sp2, the mind arrives · 2026-09-16
"""The mind's laws (canon 0003 · 0004): no mind thinks off-meter (every
thought lands a meter line); recall packs the worldline and the
memories into the prompt (verbatim, provenance-carrying); a mindless
template never touches the gateway; and — live, when a key is present —
the real librarian answers a real ask through the metered lane."""
import os
import secrets
from pathlib import Path

import pytest

from orreth_spine import dispatch, gateway, outbox, resident, sinks
from orreth_spine.store import OrrethStore

SPINE = Path(__file__).resolve().parents[1]
LIBRARIAN = SPINE / "templates" / "librarian-resident.v0.json"
ECHO = SPINE / "templates" / "echo-resident.v0.json"
POLICY = SPINE / "policy" / "covenant-policy.v1.json"


def _rails_up() -> bool:
    try:
        import pika
        pika.BlockingConnection(pika.URLParameters(
            os.environ.get("SPINE_RABBIT",
                           "amqp://orreth:orreth-dev@localhost:5672/%2F")
        )).close()
        from confluent_kafka.admin import AdminClient
        AdminClient({"bootstrap.servers":
                     os.environ.get("SPINE_KAFKA", "localhost:9092"),
                     "socket.timeout.ms": 3000}).list_topics(timeout=3)
        return True
    except Exception:
        return False


rails = pytest.mark.skipif(
    not (os.environ.get("SPINE_REQUIRE_KAFKA") or _rails_up()),
    reason="the rails are not up — start spine/compose.yaml")


def _walk(pg, r, text, tok):
    from tests.test_resident import _purge_queue, _serve_until_replied
    _purge_queue()
    ask_id = dispatch.submit_ask(pg, text)
    assert outbox.drain(pg, sinks.KafkaSink()) >= 1
    dispatch.dispatch_once(pg, consumer=f"mc-{tok}", group=f"mg-{tok}")
    return ask_id, _serve_until_replied(pg, r, ask_id)


# ---- store laws (ground only) ----------------------------------------------------

def test_the_store_lands_memories_with_events(pg):
    st = OrrethStore(pg, by_did="did:orreth:agent:test")
    h = st.put("libtest", "hempcrete", "Hempcrete cures for 28 days.")
    assert h.startswith("sha256:")
    assert st.get("libtest", "hempcrete") == "Hempcrete cures for 28 days."
    assert st.search("libtest", "cures")[0]["key"] == "hempcrete"
    cur = pg.cursor()
    cur.execute("SELECT count(*) FROM spine_outbox"
                " WHERE convert_from(body,'UTF8') LIKE '%libtest/hempcrete%'")
    assert cur.fetchone()[0] >= 1          # the memory carried its event


# ---- the metered mind, end to end (fake gateway — no network) --------------------

@rails
def test_no_mind_thinks_off_meter_and_recall_packs_the_prompt(pg):
    tok = secrets.token_hex(4)
    gw = gateway.FakeGateway(reply=f"The fake mind answers ask {tok} fully.")
    r = resident.Resident(LIBRARIAN, gateway=gw)
    r.load_policy(POLICY)
    r.join(pg)
    st = OrrethStore(pg, by_did=r.identity.did)
    st.put("librarian", f"fact-{tok}",
           f"The marker fact {tok}: hempcrete cures for 28 days.")
    ask_id, (status, reply, _by) = _walk(
        pg, r, f"Tell me about hempcrete (marker {tok}).", tok)
    assert status == "replied" and reply == gw.reply
    # the meter law: the thought landed its line
    lines = gateway.meter_lines(pg, r.identity.did)
    assert lines and lines[-1][0] == "claude-haiku-4-5-20251001" or \
        lines[-1][0] == "fake-mind"
    assert lines[-1][1] > 0 and lines[-1][2] > 0
    # recall packed the memory into the prompt, verbatim
    assert gw.calls and f"marker fact {tok}" in gw.calls[0]["prompt"]
    # a second ask recalls the FIRST exchange (the worldline)
    tok2 = secrets.token_hex(4)
    _ask2, (_s2, reply2, _b2) = _walk(
        pg, r, f"What did I ask you before? (marker {tok2})", tok2)
    assert f"marker {tok}" in gw.calls[-1]["prompt"]   # worldline recalled


@rails
def test_a_mindless_template_never_touches_the_gateway(pg):
    tok = secrets.token_hex(4)
    gw = gateway.FakeGateway()
    r = resident.Resident(ECHO, gateway=gw)     # echo declares no mind
    r.load_policy(POLICY)
    r.join(pg)
    text = f"Echo this exactly (marker {tok})."
    _ask, (status, reply, _by) = _walk(pg, r, text, tok)
    assert status == "replied" and text in reply
    assert gw.calls == []                        # the gateway never rang


# ---- the live mind (needs the real key; skipped where absent) --------------------

@rails
@pytest.mark.skipif(not os.environ.get("ANTHROPIC_API_KEY"),
                    reason="no ANTHROPIC_API_KEY — the live mind sleeps")
def test_the_librarian_thinks_for_real(pg):
    tok = secrets.token_hex(4)
    gw = gateway.AnthropicGateway()
    r = resident.Resident(LIBRARIAN, gateway=gw)
    r.load_policy(POLICY)
    r.join(pg)
    st = OrrethStore(pg, by_did=r.identity.did)
    st.put("librarian", f"cure-{tok}",
           f"Hempcrete walls cure for about 28 days (marker {tok}).")
    _ask, (status, reply, _by) = _walk(
        pg, r, "How long does hempcrete cure? Use what you recall.", tok)
    assert status == "replied" and len(reply) > 40
    assert "28" in reply                         # the memory reached the mind
    lines = gateway.meter_lines(pg, r.identity.did)
    assert lines[-1][0].startswith("claude-haiku-4-5")
    assert lines[-1][1] > 0 and lines[-1][2] > 0
    print(f"\nthe librarian, live: {reply[:200]}…"
          f"\nmetered: {lines[-1][1]} in / {lines[-1][2]} out")
