# PROVENANCE: Claude Fable 5 (claude-fable-5) — rearch P1 sp2, the events shadow (M4-lite) · 2026-09-16
"""The relay's real sinks (canon 0002).

KafkaSink publishes an outbox row to the events rail: the TOPIC is the
envelope's type (topics are schema families, never per-identity), the
KEY is the aggregate id when the envelope wears one — so order holds
exactly where it matters, per aggregate, and nowhere it doesn't. A
refused publish raises, the relay records the attempt, and the row
stays unpublished — at-least-once, honestly.
"""
from __future__ import annotations

import os

from confluent_kafka import Producer

from . import envelope as ev

KAFKA_BOOTSTRAP = os.environ.get("SPINE_KAFKA", "localhost:9092")


class KafkaSink:
    def __init__(self, bootstrap: str | None = None):
        self._p = Producer({"bootstrap.servers": bootstrap or KAFKA_BOOTSTRAP})

    def publish(self, message_id: str, body: bytes) -> None:
        env = ev.decode(body)
        topic = env["type"]
        key = str((env.get("aggregate") or {}).get("id") or message_id)
        errors: list = []
        self._p.produce(topic, value=body, key=key,
                        on_delivery=lambda e, _m: errors.append(e) if e else None)
        remaining = self._p.flush(10)
        if remaining or errors:
            raise ConnectionError(
                f"the events rail refused the publish: "
                f"{errors[0] if errors else 'flush timed out'}")
