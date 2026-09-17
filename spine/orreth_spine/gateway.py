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

    def think_acting(self, conn, *, did: str, system: str, prompt: str,
                     door, model: str | None = None, max_tokens: int = 1024,
                     max_rounds: int = 3) -> tuple[str, list[str]]:
        """The acting mind: the model may use the door's DECLARED tools;
        every tool call goes through the door (journaled, interlocked),
        every model round through the meter. Returns (reply, act_notes).
        A ConsequentialHold propagates — the resident owns the L2 path."""
        from .tools import ConsequentialHold  # noqa: F401 (re-raise passes)
        m = model or self.DEFAULT_MODEL
        messages = [{"role": "user", "content": prompt}]
        notes: list[str] = []
        for _round in range(max_rounds):
            msg = self._client.messages.create(
                model=m, max_tokens=max_tokens, system=system,
                tools=door.schemas(), messages=messages)
            with conn.transaction():
                conn.cursor().execute(
                    "INSERT INTO spine_meter (did, model, tokens_in,"
                    " tokens_out) VALUES (%s, %s, %s, %s)",
                    (did, m, msg.usage.input_tokens, msg.usage.output_tokens))
            if msg.stop_reason != "tool_use":
                return ("".join(b.text for b in msg.content
                                if b.type == "text"), notes)
            messages.append({"role": "assistant", "content": msg.content})
            results = []
            for b in msg.content:
                if b.type != "tool_use":
                    continue
                result = door.call(b.name, dict(b.input))   # holds propagate
                notes.append(f"used the {b.name} tool through the door")
                results.append({"type": "tool_result",
                                "tool_use_id": b.id, "content": result})
            messages.append({"role": "user", "content": results})
        return ("I ran out of thinking rounds before finishing — "
                "that honesty beats a guess.", notes)


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


class FakeActingGateway:
    """The test lane for the acting mind: a scripted sequence of acts —
    ("tool", name, args) steps go through the REAL door (so capability,
    journaling, and interlock laws are exercised), then a ("text", ...)
    step answers, with {result} carrying the last tool result."""

    def __init__(self, script: list[tuple]):
        self.script = script

    def think_acting(self, conn, *, did: str, system: str, prompt: str,
                     door, model: str | None = None, max_tokens: int = 1024,
                     max_rounds: int = 3) -> tuple[str, list[str]]:
        ensure_schema(conn)
        with conn.transaction():
            conn.cursor().execute(
                "INSERT INTO spine_meter (did, model, tokens_in, tokens_out)"
                " VALUES (%s, %s, %s, %s)",
                (did, model or "fake-acting-mind", len(prompt.split()), 12))
        notes, last = [], ""
        for step in self.script:
            if step[0] == "tool":
                last = door.call(step[1], step[2])       # holds propagate
                notes.append(f"used the {step[1]} tool through the door")
            else:
                return (step[1].replace("{result}", last), notes)
        return ("the script ended without words", notes)


def meter_lines(conn, did: str) -> list[tuple]:
    ensure_schema(conn)
    cur = conn.cursor()
    cur.execute("SELECT model, tokens_in, tokens_out FROM spine_meter"
                " WHERE did = %s ORDER BY meter_id", (did,))
    return cur.fetchall()
