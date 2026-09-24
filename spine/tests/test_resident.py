# PROVENANCE: Claude Fable 5 (claude-fable-5) — rearch P2 sp1, the body is born · 2026-09-16
"""The body's laws (canon 0004): no policy no join (AG-3), the same self
in every life (AG-2), the full-reply law, one-transaction service with
absorbed duplicates, the authority chain riding every hop (AG-7's seed),
and the whole road walked live: ask → ground → rail → dispatcher →
invocation → the resident → journey + reply → the glass's feed."""
import os
import secrets
from pathlib import Path

import pytest

from orreth_spine import bridgefeed, dispatch, outbox, resident, sinks

SPINE = Path(__file__).resolve().parents[1]
TEMPLATE = SPINE / "templates" / "echo-resident.v0.json"
POLICY = SPINE / "policy" / "covenant-policy.v1.json"
BOOT = os.environ.get("SPINE_KAFKA", "localhost:9092")


def _rabbit_up() -> bool:
    try:
        import pika
        pika.BlockingConnection(pika.URLParameters(
            os.environ.get("SPINE_RABBIT",
                           "amqp://orreth:orreth-dev@localhost:5672/%2F")
        )).close()
        return True
    except Exception:
        return False


def _kafka_up() -> bool:
    try:
        from confluent_kafka.admin import AdminClient
        return bool(AdminClient({"bootstrap.servers": BOOT,
                                 "socket.timeout.ms": 3000}
                                ).list_topics(timeout=3))
    except Exception:
        return False


rails = pytest.mark.skipif(
    not (os.environ.get("SPINE_REQUIRE_KAFKA")
         or (_kafka_up() and _rabbit_up())),
    reason="the rails are not up — start spine/compose.yaml")


def _purge_queue():
    """Operator's act at test start: the shared dev queue may hold prior
    runs' stale commands; clear the bench before the walk."""
    import pika
    rc = pika.BlockingConnection(pika.URLParameters(
        os.environ.get("SPINE_RABBIT",
                       "amqp://orreth:orreth-dev@localhost:5672/%2F")))
    ch = rc.channel()
    q = resident.serve_queue()
    ch.queue_declare(q, durable=True)
    ch.queue_purge(q)
    rc.close()


def _dispatch(pg, **kw):
    """A FRESH group per call: reusing a group means every call waits on
    the previous member's departure (slow leaves stall the join); a
    fresh group joins once, replays the topic with the zero-cost scope
    skip, applies this world's facts, and closes. Same-session facts
    re-apply harmlessly — the settled-status guard refuses re-serves."""
    tok = secrets.token_hex(4)
    return dispatch.dispatch_once(pg, consumer=f"td-{tok}",
                                  group=f"td-{tok}", **kw)


def _serve_until_replied(pg, r, ask_id, deadline_s=60.0):
    import time as _t
    end = _t.monotonic() + deadline_s
    cur = pg.cursor()
    while _t.monotonic() < end:
        r.serve_once(pg, idle_s=1.5, max_commands=200)
        cur.execute("SELECT status, reply, served_by FROM spine_asks"
                    " WHERE ask_id = %s", (ask_id,))
        row = cur.fetchone()
        if row and row[0] == "replied":
            return row
    raise AssertionError(f"{ask_id} was never replied within {deadline_s}s")


# ---- birth laws (no rails needed beyond the ground) ------------------------------

def test_no_policy_no_join_ever(pg):
    r = resident.Resident(TEMPLATE)
    with pytest.raises(resident.PolicyRefused, match="never.*joins|joins"):
        r.join(pg)


def test_join_wears_the_policy_version(pg):
    r = resident.Resident(TEMPLATE)
    pol = r.load_policy(POLICY)
    assert pol["version"] == "1.1.0" and pol["rules"] == 13
    joined = r.join(pg)
    assert joined["policy_version"] == "1.1.0"
    cur = pg.cursor()
    cur.execute("SELECT policy_hash, template_hash, sig FROM spine_joins"
                " WHERE did = %s ORDER BY join_id DESC LIMIT 1",
                (r.identity.did,))
    policy_hash, template_hash, sig = cur.fetchone()
    assert policy_hash.startswith("sha256:") and len(sig) == 128
    assert template_hash == r.template_hash


def test_the_same_self_in_every_life(pg, tmp_path):
    """AG-2: two lives from one home wear ONE DID; the join ledger counts
    the lives; a different home is a different self."""
    a = resident.Resident(TEMPLATE, home=tmp_path)
    a.load_policy(POLICY)
    first = a.join(pg)
    b = resident.Resident(TEMPLATE, home=tmp_path)      # the respawn
    b.load_policy(POLICY)
    second = b.join(pg)
    assert a.identity.did == b.identity.did
    assert (first["life"], second["life"]) == (1, 2)
    stranger = resident.Resident(TEMPLATE, home=tmp_path / "elsewhere")
    assert stranger.identity.did != a.identity.did


def test_the_template_is_declared_or_refused():
    with pytest.raises(ValueError, match="not a resident template"):
        resident.Resident(POLICY)          # a policy is not a template


# ---- the road, walked live -------------------------------------------------------

@rails
def test_the_whole_road_ask_to_reply_to_feed(pg):
    """The spoonful's proof: submit → dispatch → serve → the reply row
    carries EVERY word; journey + reply events reach the glass's feed in
    order; the authority chain rides every hop."""
    tok = secrets.token_hex(4)
    bf = bridgefeed.BridgeFeed(
        [resident.ASK_RECEIVED, resident.JOURNEY, resident.REPLY],
        from_start=True).start()
    try:
        assert bf.wait_ready()
        q = bf.feed.attach()        # listen like a client, live — the ring
        _purge_queue()              # holds only the last 1024 and says so
        r = resident.Resident(TEMPLATE)
        r.load_policy(POLICY)
        r.join(pg)
        text = f"Marker {tok}: please repeat every single word of this ask."
        ask_id = dispatch.submit_ask(pg, text)
        assert outbox.drain(pg, sinks.KafkaSink()) >= 1
        d = _dispatch(pg)
        assert d["applied"] >= 1
        # the FULL-reply law: every word of the ask, verbatim, in the answer
        status, reply_text, served_by = _serve_until_replied(pg, r, ask_id)
        assert status == "replied" and served_by == r.identity.did
        assert text in reply_text
        cur = pg.cursor()
        # the events reach the rail: journey then reply, one aggregate
        assert outbox.drain(pg, sinks.KafkaSink()) >= 3
        import queue as _q
        import time as _t
        mine, end = [], _t.monotonic() + 30
        while _t.monotonic() < end and \
                resident.REPLY not in [n["kind"] for n in mine]:
            try:
                n = q.get(timeout=0.5)
            except _q.Empty:
                continue
            if n["ref"] == ask_id:
                mine.append(n)
        kinds = [n["kind"] for n in mine]
        assert resident.JOURNEY in kinds and resident.REPLY in kinds
        assert kinds[-1] == resident.REPLY     # completion arrives last
        # duplicate invocation absorbed: replay the whole command road
        # (deliberately a FRESH group — replaying history IS this test)
        d2 = dispatch.dispatch_once(pg, consumer=f"dupcheck-{tok}",
                                    group=f"dupcheck-{tok}")
        assert d2["applied"] >= 1              # the same fact re-dispatched
        r.serve_once(pg, idle_s=2.0, max_commands=200)
        cur.execute("SELECT reply, replied_at FROM spine_asks"
                    " WHERE ask_id = %s", (ask_id,))
        reply2, _at = cur.fetchone()
        assert reply2 == reply_text            # nothing double-served
    finally:
        bf.stop()


@rails
def test_the_authority_chain_rides_every_hop(pg):
    """AG-7's seed: who asked travels ask → command → journey → reply."""
    tok = secrets.token_hex(4)
    _purge_queue()
    r = resident.Resident(TEMPLATE)
    r.load_policy(POLICY)
    r.join(pg)
    person = f"did:orreth:person:jb-{tok}"
    ask_id = dispatch.submit_ask(pg, "who asked this?", person=person)
    assert outbox.drain(pg, sinks.KafkaSink()) >= 1
    _dispatch(pg)
    _serve_until_replied(pg, r, ask_id)
    from orreth_spine import envelope as ev
    cur = pg.cursor()
    cur.execute("SELECT body FROM spine_outbox"
                " WHERE convert_from(body, 'UTF8') LIKE %s",
                (f"%{ask_id}%",))
    chains = [ev.decode(bytes(b[0])).get("authority_chain") for b in
              cur.fetchall()]
    assert chains and all(c and c[0] == person for c in chains)
    finals = [c for c in chains if len(c) == 2]
    assert finals and all(c[1] == r.identity.did for c in finals)
