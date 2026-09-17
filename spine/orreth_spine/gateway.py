# PROVENANCE: Claude Fable 5 (claude-fable-5) — rearch P2 sp2, the mind arrives · 2026-09-16
"""The gateway lane v0 (canon 0004): no mind thinks off-meter.

Every model call in the new world goes through here: the thought runs,
and the meter line lands on the ground — who thought, with which model,
how many tokens, when. The kernel never sees the prompt (the covenant's
plane law); the meter sees only the count. A resident without a gateway
falls back to its deterministic graph — it never calls a model around
the meter, because there is no other door.
"""
from __future__ import annotations

import os


def ensure_schema(conn) -> None:
    with conn.transaction():
        conn.cursor().execute(
            "CREATE TABLE IF NOT EXISTS spine_meter ("
            " meter_id bigserial PRIMARY KEY,"
            " did text NOT NULL,"
            " model text NOT NULL,"
            " tokens_in int NOT NULL,"
            " tokens_out int NOT NULL,"
            " at timestamptz NOT NULL DEFAULT now())")


class AnthropicGateway:
    """The real lane: Claude models via the Anthropic SDK. The default
    resident mind is Haiku — small, fast, cheap; templates may declare
    another model and the gateway honors it."""

    DEFAULT_MODEL = "claude-haiku-4-5-20251001"

    def __init__(self, api_key: str | None = None):
        from anthropic import Anthropic
        self._client = Anthropic(
            api_key=api_key or os.environ.get("ANTHROPIC_API_KEY"))

    def think(self, conn, *, did: str, system: str, prompt: str,
              model: str | None = None, max_tokens: int = 1024) -> str:
        ensure_schema(conn)
        m = model or self.DEFAULT_MODEL
        msg = self._client.messages.create(
            model=m, max_tokens=max_tokens, system=system,
            messages=[{"role": "user", "content": prompt}])
        text = "".join(b.text for b in msg.content if b.type == "text")
        with conn.transaction():
            conn.cursor().execute(
                "INSERT INTO spine_meter (did, model, tokens_in, tokens_out)"
                " VALUES (%s, %s, %s, %s)",
                (did, m, msg.usage.input_tokens, msg.usage.output_tokens))
        return text


class FakeGateway:
    """The test lane: deterministic thoughts, REAL meter lines — the
    metering law is tested without a network."""

    def __init__(self, reply: str = "a thought from the fake mind"):
        self.reply = reply
        self.calls: list[dict] = []

    def think(self, conn, *, did: str, system: str, prompt: str,
              model: str | None = None, max_tokens: int = 1024) -> str:
        ensure_schema(conn)
        self.calls.append({"system": system, "prompt": prompt})
        with conn.transaction():
            conn.cursor().execute(
                "INSERT INTO spine_meter (did, model, tokens_in, tokens_out)"
                " VALUES (%s, %s, %s, %s)",
                (did, model or "fake-mind", len(prompt.split()),
                 len(self.reply.split())))
        return self.reply


def meter_lines(conn, did: str) -> list[tuple]:
    ensure_schema(conn)
    cur = conn.cursor()
    cur.execute("SELECT model, tokens_in, tokens_out FROM spine_meter"
                " WHERE did = %s ORDER BY meter_id", (did,))
    return cur.fetchall()
