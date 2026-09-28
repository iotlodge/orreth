# PROVENANCE: Claude Fable 5 (claude-fable-5) — rearch P1 sp2, the events shadow (M4-lite) · 2026-09-16
# Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp8 lock 5: run_once ends at the topic's end, never by waiting out a silence · 2026-09-27
"""The projector (canon 0002 · 0003): a consumer that folds committed
facts into a rebuildable read model.

The laws it lives by: the Kafka offset commits ONLY after the database
transaction — a crash between the two redelivers, and the inbox absorbs
the replay into zero extra effect. A body that cannot be decoded is
PARKED visibly with its evidence and the projector stops at it —
advancing past a poison event is an operator's explicit decision, never
a silent loss. Delete the read model, replay from offset zero, and the
same truth rebuilds — that property is what makes every projection an
honest acceleration of the log rather than a second truth.
"""
from __future__ import annotations

import os
import time

from confluent_kafka import Consumer

from . import envelope as ev
from . import inbox

KAFKA_BOOTSTRAP = os.environ.get("SPINE_KAFKA", "localhost:9092")


def ensure_schema(conn) -> None:
    from .outbox import once
    if not once(conn, "projector"):
        return
    with conn.transaction():
        cur = conn.cursor()
        cur.execute("SELECT pg_advisory_xact_lock(742199)")  # DDL race guard
        cur.execute(
            "CREATE TABLE IF NOT EXISTS spine_parked ("
            " parked_id bigserial PRIMARY KEY,"
            " consumer text NOT NULL,"
            " topic text,"
            " partition int,"
            " kafka_offset bigint,"
            " body bytea,"
            " reason text NOT NULL,"
            " parked_at timestamptz NOT NULL DEFAULT now())")


def park(conn, consumer: str, msg, reason: str) -> None:
    with conn.transaction():
        conn.cursor().execute(
            "INSERT INTO spine_parked"
            " (consumer, topic, partition, kafka_offset, body, reason)"
            " VALUES (%s, %s, %s, %s, %s, %s)",
            (consumer, msg.topic(), msg.partition(), msg.offset(),
             msg.value(), reason[:500]))


def parked_count(conn, consumer: str) -> int:
    cur = conn.cursor()
    cur.execute("SELECT count(*) FROM spine_parked WHERE consumer = %s",
                (consumer,))
    return int(cur.fetchone()[0])


def run_forever(conn, *, group: str, topics: list[str], consumer_name: str,
                apply, stop, bootstrap: str | None = None,
                poll_s: float = 0.5, offset: str = "earliest",
                ready=None, skip=None) -> None:
    """The standing consumer: ONE membership for its whole life — never
    the join/leave churn of repeated run_once calls, which litters the
    group with ghost members until the coordinator wedges (found live:
    a 297-second ghost join blocked every dispatcher behind it)."""
    ensure_schema(conn)
    inbox.ensure_schema(conn)
    cons = Consumer({
        "bootstrap.servers": bootstrap or KAFKA_BOOTSTRAP,
        "group.id": group,
        "auto.offset.reset": offset,
        "enable.auto.commit": False,
    })
    try:
        cons.subscribe(topics)
        while not stop.is_set():
            msg = cons.poll(poll_s)
            if ready is not None and not ready.is_set() and                     cons.assignment():
                ready.set()
            if msg is None or msg.error():
                continue
            try:
                env = ev.decode(msg.value())
            except Exception:
                park(conn, consumer_name, msg, "undecodable body")
                continue                  # a dispatcher skips bad bytes
            if skip is not None and skip(env):
                cons.commit(message=msg)  # not ours: advance, no inbox work
                continue
            inbox.apply_event(conn, consumer_name, env,
                              lambda cur, _e=env: apply(cur, _e))
            cons.commit(message=msg)
    finally:
        cons.close()


def _caught_up(cons) -> bool:
    """True once every assigned partition has been read to its end (the
    high watermark): the fresh group's replay is over and nothing waits.
    Lock 5 (2026-09-27): this is the honest end of a run_once — the
    suite's every test-side dispatch used to wait out `idle_s` of
    silence (8 s × ~30 calls: most of the suite's minutes, measured), for
    facts a synchronous sink had long since flushed to the topic."""
    tps = cons.assignment()
    if not tps:
        return False                       # not joined yet: nothing is known
    try:
        for tp in tps:
            low, high = cons.get_watermark_offsets(tp, timeout=1.0)
            if high <= low:
                continue                   # an empty partition: nothing to read
            pos = cons.position([tp])[0].offset
            if pos < 0 or pos < high:
                return False               # not yet fetched, or behind the end
        return True
    except Exception:                      # noqa: BLE001 — unknown is not caught up
        return False


def run_once(conn, *, group: str, topics: list[str], consumer_name: str,
             apply, bootstrap: str | None = None, max_messages: int = 500,
             idle_s: float = 8.0, skip=None) -> dict:
    """Consume until the topic's end, the cap, or `idle_s` of silence:
    for each message decode → apply through the durable inbox
    (`apply(cur, env)` is the read-model effect) → commit the offset ONLY
    after the database has. Returns the honest tally: applied, absorbed
    (duplicate/stale), parked. The end of the topic (every assigned
    partition read to its high watermark, then one empty poll) ends the
    call; `idle_s` is the fallback for a consumer the broker never
    assigns."""
    ensure_schema(conn)
    inbox.ensure_schema(conn)
    cons = Consumer({
        "bootstrap.servers": bootstrap or KAFKA_BOOTSTRAP,
        "group.id": group,
        "auto.offset.reset": "earliest",
        "enable.auto.commit": False,
    })
    tally = {"applied": 0, "absorbed": 0, "parked": 0}
    try:
        cons.subscribe(topics)
        deadline = time.monotonic() + idle_s
        seen = 0
        while time.monotonic() < deadline and seen < max_messages:
            msg = cons.poll(0.5)
            if msg is None:
                if _caught_up(cons):       # lock 5: read to the end — done, not "quiet for 8 s"
                    break
                continue
            if msg.error():
                continue
            deadline = time.monotonic() + idle_s
            try:
                env = ev.decode(msg.value())
            except Exception as e:
                park(conn, consumer_name, msg,
                     f"undecodable body: {type(e).__name__}: {e}")
                tally["parked"] += 1
                break              # never advance past a poison event
            if skip is not None and skip(env):
                cons.commit(message=msg)   # not ours: advance, no inbox work
                continue                   # — and it costs NOTHING against
            seen += 1                      # the cap: the cap bounds THIS
            outcome = inbox.apply_event(   # world's work (a fresh group
                                           # replaying a 539-fact topic hit
                                           # 500 skips and never reached
                                           # its own fact: the growing-
                                           # corpus disease, second time)
                conn, consumer_name, env,
                lambda cur, _env=env: apply(cur, _env))
            if outcome == "applied":
                tally["applied"] += 1
            else:
                tally["absorbed"] += 1
            cons.commit(message=msg)   # only AFTER the database transaction
    finally:
        cons.close()
    return tally
