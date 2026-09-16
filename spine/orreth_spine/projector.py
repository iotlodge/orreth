# PROVENANCE: Claude Fable 5 (claude-fable-5) — rearch P1 sp2, the events shadow (M4-lite) · 2026-09-16
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
    with conn.transaction():
        conn.cursor().execute(
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


def run_once(conn, *, group: str, topics: list[str], consumer_name: str,
             apply, bootstrap: str | None = None, max_messages: int = 500,
             idle_s: float = 8.0) -> dict:
    """Consume until idle or the cap: for each message decode → apply
    through the durable inbox (`apply(cur, env)` is the read-model
    effect) → commit the offset ONLY after the database has. Returns the
    honest tally: applied, absorbed (duplicate/stale), parked."""
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
            if msg is None or msg.error():
                continue
            seen += 1
            deadline = time.monotonic() + idle_s
            try:
                env = ev.decode(msg.value())
            except Exception as e:
                park(conn, consumer_name, msg,
                     f"undecodable body: {type(e).__name__}: {e}")
                tally["parked"] += 1
                break              # never advance past a poison event
            outcome = inbox.apply_event(
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
