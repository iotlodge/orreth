# PROVENANCE: Claude Fable 5 (claude-fable-5) — rearch P1 sp2, the events shadow (M4-lite) · 2026-09-16
"""M4-lite's laws: committed facts flow ground → events rail; a
projection rebuilt from the rail alone equals the domain truth; wire
duplicates and redeliveries fold to zero extra effect; poison parks
visibly and never advances. Needs the events rail (skips politely when
it's down; SPINE_REQUIRE_KAFKA makes absence a FAILURE — CI sets it)."""
import os
import secrets
import time

import pytest

from orreth_spine import envelope as ev
from orreth_spine import inbox, outbox, projector, rails, sinks

BOOT = os.environ.get("SPINE_KAFKA", "localhost:9092")


def _kafka_up() -> bool:
    try:
        from confluent_kafka.admin import AdminClient
        return bool(AdminClient({"bootstrap.servers": BOOT,
                                 "socket.timeout.ms": 3000}
                                ).list_topics(timeout=3))
    except Exception:
        return False


pytestmark = pytest.mark.skipif(
    not (os.environ.get("SPINE_REQUIRE_KAFKA") or _kafka_up()),
    reason="the events rail is not up — start spine/compose.yaml")


@pytest.fixture(scope="module", autouse=True)
def _schema(pg):
    outbox.ensure_schema(pg)
    inbox.ensure_schema(pg)
    projector.ensure_schema(pg)
    with pg.transaction():
        cur = pg.cursor()
        cur.execute(
            "CREATE TABLE IF NOT EXISTS spine_counter ("
            " aggregate_id text PRIMARY KEY, value int NOT NULL DEFAULT 0)")
        cur.execute(
            "CREATE TABLE IF NOT EXISTS spine_counter_view ("
            " consumer text NOT NULL, aggregate_id text NOT NULL,"
            " value int NOT NULL DEFAULT 0,"
            " PRIMARY KEY (consumer, aggregate_id))")


def _env(typ, aid, seq):
    return ev.make_envelope(
        kind="event", type=typ, universe_id="u:dev", scope_path="u:dev",
        payload={"ref": f"{aid}#{seq}", "hash": "sha256:x"},
        aggregate={"type": "counter", "id": aid, "sequence": seq})


def _view_apply(consumer):
    def apply(cur, env):
        cur.execute(
            "INSERT INTO spine_counter_view (consumer, aggregate_id, value)"
            " VALUES (%s, %s, 1) ON CONFLICT (consumer, aggregate_id)"
            " DO UPDATE SET value = spine_counter_view.value + 1",
            (consumer, env["aggregate"]["id"]))
    return apply


def _view(pg, consumer, aid):
    cur = pg.cursor()
    cur.execute("SELECT value FROM spine_counter_view"
                " WHERE consumer = %s AND aggregate_id = %s", (consumer, aid))
    row = cur.fetchone()
    return row[0] if row else 0


def _commit_and_relay(pg, typ, aid, n):
    def bump(cur):
        cur.execute(
            "INSERT INTO spine_counter (aggregate_id, value) VALUES (%s, 1)"
            " ON CONFLICT (aggregate_id)"
            " DO UPDATE SET value = spine_counter.value + 1", (aid,))
    envs = []
    for seq in range(1, n + 1):
        e = _env(typ, aid, seq)
        outbox.commit_with_outbox(pg, ev.encode(e), e["message_id"], bump)
        envs.append(e)
    assert outbox.drain(pg, sinks.KafkaSink()) >= n
    return envs


def _project(pg, typ, consumer, token=None):
    return projector.run_once(
        pg, group=f"g-{consumer}-{token or secrets.token_hex(3)}",
        topics=[rails.topic(typ)], consumer_name=consumer, apply=_view_apply(consumer))


def test_committed_facts_flow_and_the_projection_rebuilds(pg):
    """The heart of M4: project the stream, replay it into a second empty
    view, rebuild a third — all three equal the domain's own truth."""
    tok = secrets.token_hex(4)
    typ, aid = f"orreth.test-{tok}.counter.v1", f"agg-{tok}"
    _commit_and_relay(pg, typ, aid, 5)
    t1 = _project(pg, typ, f"proj1-{tok}")
    assert t1["applied"] == 5 and t1["parked"] == 0
    cur = pg.cursor()
    cur.execute("SELECT value FROM spine_counter WHERE aggregate_id=%s", (aid,))
    domain = cur.fetchone()[0]
    assert _view(pg, f"proj1-{tok}", aid) == domain == 5
    # replay from offset zero into a second, empty consumer
    t2 = _project(pg, typ, f"proj2-{tok}")
    assert t2["applied"] == 5 and _view(pg, f"proj2-{tok}", aid) == 5
    # burn a view down and rebuild it fresh from the rail alone
    t3 = _project(pg, typ, f"proj3-{tok}")
    assert t3["applied"] == 5 and _view(pg, f"proj3-{tok}", aid) == 5


def test_wire_duplicate_folds_to_one_effect(pg):
    """Fault: the relay died after publish and published again — the wire
    carries the message twice; the projection moves once."""
    tok = secrets.token_hex(4)
    typ, aid = f"orreth.test-{tok}.counter.v1", f"agg-{tok}"
    envs = _commit_and_relay(pg, typ, aid, 1)
    sinks.KafkaSink().publish(envs[0]["message_id"], ev.encode(envs[0]))
    t = _project(pg, typ, f"dup-{tok}")
    assert t["applied"] == 1 and t["absorbed"] == 1
    assert _view(pg, f"dup-{tok}", aid) == 1


def test_crash_between_apply_and_offset_redelivers_harmlessly(pg):
    """Fault: the consumer applied, then died before committing its
    offset. The restart re-reads from earliest; the inbox absorbs."""
    tok = secrets.token_hex(4)
    typ, aid = f"orreth.test-{tok}.counter.v1", f"agg-{tok}"
    envs = _commit_and_relay(pg, typ, aid, 1)
    consumer = f"crash-{tok}"
    # the pre-crash life: database applied, offset never committed
    assert inbox.apply_event(pg, consumer, envs[0],
                             lambda cur: _view_apply(consumer)(cur, envs[0])
                             ) == "applied"
    t = _project(pg, typ, consumer)      # the restarted life, from earliest
    assert t["applied"] == 0 and t["absorbed"] == 1
    assert _view(pg, consumer, aid) == 1


def test_poison_parks_visibly_and_never_advances(pg):
    """An undecodable body parks with its evidence and stops the
    projector at the poison — no silent loss, no guessing past it."""
    tok = secrets.token_hex(4)
    typ = f"orreth.test-{tok}.counter.v1"
    from confluent_kafka import Producer
    p = Producer({"bootstrap.servers": BOOT})
    p.produce(rails.topic(typ), value=b"this is not an envelope")    # P7 sp7: the cell's topic
    p.flush(10)
    consumer = f"poison-{tok}"
    t = _project(pg, typ, consumer)
    assert t["parked"] == 1 and t["applied"] == 0
    assert projector.parked_count(pg, consumer) == 1
    cur = pg.cursor()
    cur.execute("SELECT reason, body FROM spine_parked WHERE consumer=%s",
                (consumer,))
    reason, body = cur.fetchone()
    assert "undecodable" in reason and bytes(body) == b"this is not an envelope"


def test_another_worlds_facts_cost_nothing_against_the_cap(pg):
    """The growing-corpus disease, pinned (found twice: P3 sp1 and P3
    sp5 — a fresh group replaying a 539-fact topic hit the 500 cap on
    skips alone and never reached its own world's fact): the cap bounds
    THIS world's work; another world's facts are skipped for free."""
    typ = f"orreth.test.cap.{secrets.token_hex(3)}.v1"
    sink = sinks.KafkaSink()
    for seq in range(1, 4):                     # three strangers ahead of us
        e = _env(typ, "agg-elsewhere", seq)
        e["scope_path"] = "u:elsewhere"
        sink.publish(e["message_id"], ev.encode(e))
    aid = "agg-" + secrets.token_hex(3)
    _commit_and_relay(pg, typ, aid, 1)          # then ONE of ours
    consumer = "cap-" + secrets.token_hex(3)
    out = projector.run_once(
        pg, group=f"g-{consumer}", topics=[rails.topic(typ)], consumer_name=consumer,
        apply=_view_apply(consumer), max_messages=1,
        skip=lambda env: env.get("scope_path") != "u:dev")  # _env's world
    assert out["applied"] == 1                  # ours, past three free skips
    assert _view(pg, consumer, aid) == 1


def test_the_standing_consumer_holds_at_a_poison_until_a_person_advances(pg):
    """Re-base sp1 — the same law on both kernels: the standing consumer parks
    a poison once by its place, with its fact, and HOLDS at it (nothing behind
    it applies) until a person's word advances it; then it goes on."""
    import threading
    import psycopg
    from conftest import DSN
    tok = secrets.token_hex(4)
    typ, aid = f"orreth.test-{tok}.counter.v1", f"agg-{tok}"
    from confluent_kafka import Producer
    p = Producer({"bootstrap.servers": BOOT})
    p.produce(rails.topic(typ), value=b"this is not an envelope")
    p.flush(10)
    envs = _commit_and_relay(pg, typ, aid, 1)               # a good fact BEHIND the poison
    consumer, applied, stop = f"hold-{tok}", [], threading.Event()

    def consume():
        with psycopg.connect(DSN, autocommit=True) as own:  # its own line: a connection is one thread's
            own.execute("SET search_path TO spine_test")
            projector.run_forever(own, group=f"g-{consumer}", topics=[rails.topic(typ)],
                                  consumer_name=consumer, apply=lambda cur, env: applied.append(env["message_id"]),
                                  stop=stop, offset="earliest")

    t = threading.Thread(target=consume, daemon=True)
    t.start()
    try:
        deadline = time.monotonic() + 40
        while projector.parked_count(pg, consumer) == 0:
            assert time.monotonic() < deadline, "the poison was never parked"
            time.sleep(0.3)
        [row] = projector.parked(pg, consumer)
        assert row["reason"].startswith("undecodable body:") and row["bytes"] == 23
        assert row["hash"] == projector.body_hash(b"this is not an envelope")
        cur = pg.cursor()
        cur.execute("SELECT body FROM spine_outbox ORDER BY outbox_id DESC LIMIT 5")
        facts = [ev.decode(bytes(b)) for (b,) in cur.fetchall()]
        fact = next(e for e in facts if e["type"] == projector.PARKED)
        assert fact["payload"]["ref"] == f"parked:{row['parked_id']}" and fact["authority_chain"] == ["the kernel"]
        time.sleep(3)
        assert applied == [], "the consumer went past the poison"
        made = projector.advance(pg, row["parked_id"], "did:orreth:person:jb")
        assert made["advanced"] and not made["already"]
        deadline = time.monotonic() + 20
        while not applied:
            assert time.monotonic() < deadline, "the consumer never went on after the advance"
            time.sleep(0.3)
        assert applied == [envs[0]["message_id"]]
        assert projector.parked_count(pg, consumer) == 0
        assert projector.advance(pg, row["parked_id"], "did:orreth:person:jb")["already"] is True
        assert projector.advance(pg, 999_999, "x") is None
    finally:
        stop.set()
        t.join(15)
