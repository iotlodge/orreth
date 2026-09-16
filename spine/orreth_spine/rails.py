# PROVENANCE: Claude Fable 5 (claude-fable-5) — rearch P0 sp1, the rig breathes · 2026-09-16
"""One breath through each rail (canon 0002).

Every breath is the same proof: an envelope goes in, comes back, and the
bytes match exactly. The ground (Postgres) writes the heartbeat AND its
outbox row in one transaction — the state-and-publish-intent-are-
inseparable law, honored from the very first breath. The invocation rail
(RabbitMQ) publishes with confirms and acknowledges only after the bytes
are verified. The events rail (Kafka) produces to a topic and reads it
back from the log.
"""
from __future__ import annotations

import os
import time

import pika
import psycopg
from confluent_kafka import Consumer, Producer

from . import envelope as ev

PG_DSN = os.environ.get(
    "SPINE_PG", "postgresql://orreth:orreth-dev@localhost:5433/spine")
RABBIT_URL = os.environ.get(
    "SPINE_RABBIT", "amqp://orreth:orreth-dev@localhost:5672/%2F")
KAFKA_BOOTSTRAP = os.environ.get("SPINE_KAFKA", "localhost:9092")

COMMAND_EXCHANGE = "orreth.command.v1"
HEARTBEAT_QUEUE = "spine.heartbeat"
HEARTBEAT_KEY = "cmd.dev.00.heartbeat"
HEARTBEAT_TOPIC = "orreth.heartbeat.v1"


def ground_breath(env: dict) -> float:
    """Postgres: heartbeat + outbox row in ONE transaction, read back exact."""
    raw = ev.encode(env)
    t0 = time.perf_counter()
    with psycopg.connect(PG_DSN) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "CREATE TABLE IF NOT EXISTS spine_heartbeat ("
                " message_id text PRIMARY KEY,"
                " body bytea NOT NULL,"
                " committed_at timestamptz NOT NULL DEFAULT now())")
            cur.execute(
                "CREATE TABLE IF NOT EXISTS spine_outbox ("
                " outbox_id bigserial PRIMARY KEY,"
                " message_id text NOT NULL,"
                " body bytea NOT NULL,"
                " published_at timestamptz)")
            cur.execute(
                "INSERT INTO spine_heartbeat (message_id, body)"
                " VALUES (%s, %s) ON CONFLICT DO NOTHING",
                (env["message_id"], raw))
            cur.execute(
                "INSERT INTO spine_outbox (message_id, body) VALUES (%s, %s)",
                (env["message_id"], raw))
        conn.commit()
        with conn.cursor() as cur:
            cur.execute("SELECT body FROM spine_heartbeat WHERE message_id=%s",
                        (env["message_id"],))
            back = cur.fetchone()[0]
    if bytes(back) != raw:
        raise AssertionError("the ground returned different bytes")
    return (time.perf_counter() - t0) * 1000.0


def invoke_breath(env: dict, timeout_s: float = 10.0) -> float:
    """RabbitMQ: publish with confirms on the command exchange, consume,
    verify the bytes, and only then acknowledge (the ACK law in miniature)."""
    raw = ev.encode(env)
    t0 = time.perf_counter()
    conn = pika.BlockingConnection(pika.URLParameters(RABBIT_URL))
    try:
        ch = conn.channel()
        ch.confirm_delivery()
        ch.exchange_declare(COMMAND_EXCHANGE, exchange_type="topic",
                            durable=True)
        ch.queue_declare(HEARTBEAT_QUEUE, durable=True)
        ch.queue_bind(HEARTBEAT_QUEUE, COMMAND_EXCHANGE, HEARTBEAT_KEY)
        ch.basic_publish(
            COMMAND_EXCHANGE, HEARTBEAT_KEY, raw,
            properties=pika.BasicProperties(delivery_mode=2,
                                            message_id=env["message_id"]),
            mandatory=True)
        deadline = time.monotonic() + timeout_s
        while time.monotonic() < deadline:
            method, _props, body = ch.basic_get(HEARTBEAT_QUEUE)
            if method is None:
                time.sleep(0.05)
                continue
            if body == raw:
                ch.basic_ack(method.delivery_tag)
                return (time.perf_counter() - t0) * 1000.0
            # someone else's heartbeat: put it back and keep looking
            ch.basic_nack(method.delivery_tag, requeue=True)
        raise TimeoutError("the invocation rail never returned the heartbeat")
    finally:
        conn.close()


def events_breath(env: dict, timeout_s: float = 30.0) -> float:
    """Kafka: produce to the heartbeat topic, read the log from the start
    with a fresh group, and verify our exact bytes came back."""
    raw = ev.encode(env)
    t0 = time.perf_counter()
    prod = Producer({"bootstrap.servers": KAFKA_BOOTSTRAP})
    prod.produce(HEARTBEAT_TOPIC, value=raw, key=env["message_id"])
    remaining = prod.flush(timeout_s)
    if remaining:
        raise TimeoutError("the events rail never confirmed the produce")
    cons = Consumer({
        "bootstrap.servers": KAFKA_BOOTSTRAP,
        "group.id": "spine-breath-" + env["message_id"][-8:],
        "auto.offset.reset": "earliest",
        "enable.auto.commit": False,
    })
    try:
        cons.subscribe([HEARTBEAT_TOPIC])
        deadline = time.monotonic() + timeout_s
        while time.monotonic() < deadline:
            msg = cons.poll(0.5)
            if msg is None or msg.error():
                continue
            if msg.value() == raw:
                return (time.perf_counter() - t0) * 1000.0
        raise TimeoutError("the events rail never returned the heartbeat")
    finally:
        cons.close()
