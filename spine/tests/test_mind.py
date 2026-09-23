# PROVENANCE: Claude Fable 5 (claude-fable-5) — rearch P2 sp2, the mind arrives · 2026-09-16
# Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp4, W26: a silent mind is asked again once, then the silence is said in words · 2026-09-23
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
    from tests.test_resident import (_dispatch, _purge_queue,
                                 _serve_until_replied)
    _purge_queue()
    ask_id = dispatch.submit_ask(pg, text)
    assert outbox.drain(pg, sinks.KafkaSink()) >= 1
    _dispatch(pg)
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


class _Silences(gateway.FakeGateway):
    """A mind that answers from a script — "" is a silence."""

    def __init__(self, *replies):
        super().__init__(reply="")
        self.script = list(replies)

    def think(self, conn, **kw):
        self.reply = self.script.pop(0) if self.script else ""
        return super().think(conn, **kw)


@rails
def test_w26_an_empty_reply_never_lands_as_replied_asked_again_once_then_said_in_words(pg):
    """W26 (seen 2026-09-23 in the live-mind law, once in three runs): the
    mind returned NO words and the row landed `replied` with an empty
    bubble. The cure, on the serve path: a silence is asked again ONCE —
    words on the second try land as the reply, with a journey step naming
    the retry; a second silence lands as words that say so, status
    `replied`, never an empty bubble. Every thought is metered."""
    tok = secrets.token_hex(4)
    gw = _Silences("", f"On the second asking: hempcrete cures for 28 days (marker {tok}).")
    r = resident.Resident(LIBRARIAN, gateway=gw)
    r.load_policy(POLICY)
    r.join(pg)
    ask_id, (status, reply, _by) = _walk(pg, r, f"How long does hempcrete cure? (marker {tok})", tok)
    assert status == "replied" and reply.startswith("On the second asking")
    assert len(gw.calls) == 2                                    # asked twice, no more
    cur = pg.cursor()
    cur.execute("SELECT count(*) FROM spine_meter WHERE did = %s", (r.identity.did,))
    assert cur.fetchone()[0] >= 2                                # both thoughts metered
    from orreth_spine import glass
    view = glass.ask_view(pg, ask_id)
    assert any(resident.W26_STEP in j for j in view["journey"])  # the retry is in the record
    gw2 = _Silences("", "", "never reached")
    r2 = resident.Resident(LIBRARIAN, gateway=gw2)
    r2.load_policy(POLICY)
    r2.join(pg)
    tok2 = secrets.token_hex(4)
    _a2, (status2, reply2, _b2) = _walk(pg, r2, f"Say nothing twice (marker {tok2})", tok2)
    assert (status2, reply2) == ("replied", resident.W26_WORDS)   # words, never an empty bubble
    assert len(gw2.calls) == 2 and gw2.script == ["never reached"]


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
