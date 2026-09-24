# PROVENANCE: Claude Fable 5 (claude-fable-5) — rearch P2 sp2, the mind arrives · 2026-09-16
# Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P6 cure sp1 (kernel), walk #7's W17 (the meter's clock) · 2026-09-21
# Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P6.5 sp1, the meter reads the ladder (the mind's service DID) · 2026-09-22
# Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P6.5 sp3, THE GATEWAY: every mind through LiteLLM with the body's own key; the meter in dollars · 2026-09-24
"""The gateway lane v0 (canon 0004): no mind thinks off-meter.

Every model call in the new world goes through here: the thought runs,
and the meter line lands on the ground — who thought, with which model,
how many tokens, when (W17: `at` is the landing on the ground's clock,
clock_timestamp(), never the serving transaction's start). The kernel never sees the prompt (the covenant's
plane law); the meter sees only the count. A resident without a gateway
falls back to its deterministic graph — it never calls a model around
the meter, because there is no other door.

P6.5 sp1: the meter reads the ladder — every meter row carries the DID of
the MIND SERVICE the model belongs to (services.py, kind mind) when one is
registered; null honestly when none is.

P6.5 sp3 (JB's lock, 2026-09-24): THE GATEWAY is LiteLLM, run and managed
by Orreth (stable.py). `LiteLLMGateway` is the one real lane: the Stable
resolves WHICH mind serves (an ask's pin → the body's assignment → the
template's model → the class), the body thinks through the gateway with
ITS OWN virtual key (its lease: the fuel clause), and the meter lands
DOLLARS beside tokens — the cost the gateway's answer wears
(`x-litellm-response-cost`), else the pin's price, never a guess. A
drained lease, a dark gateway, a mind that does not stand: said in words
to the human, metered as a failed line (ok = false, the reason), never a
stack. The Anthropic SDK left the think path: no mind is called around
the gateway (rule 5). The Anthropic lane below stays only as the fallback
a test may aim at directly.
"""
from __future__ import annotations

import json
import os


def ensure_schema(conn) -> None:
    from .outbox import once
    if not once(conn, "gateway"):
        return
    with conn.transaction():
        cur = conn.cursor()
        cur.execute("SELECT pg_advisory_xact_lock(742199)")  # DDL race guard
        cur.execute(
            "CREATE TABLE IF NOT EXISTS spine_meter ("
            " meter_id bigserial PRIMARY KEY,"
            " did text NOT NULL,"
            " model text NOT NULL,"
            " tokens_in int NOT NULL,"
            " tokens_out int NOT NULL,"
            " at timestamptz NOT NULL DEFAULT now())")
        # P6.5 sp1: the mind's service DID on every line (null when unregistered)
        cur.execute("ALTER TABLE spine_meter ADD COLUMN IF NOT EXISTS service text")
        # P6.5 sp3: dollars, the stall that served, the gateway's request id, the
        # honest failure (ok = false with its reason), and a confessed degrade
        cur.execute("ALTER TABLE spine_meter ADD COLUMN IF NOT EXISTS usd double precision")
        cur.execute("ALTER TABLE spine_meter ADD COLUMN IF NOT EXISTS stall text")
        cur.execute("ALTER TABLE spine_meter ADD COLUMN IF NOT EXISTS request_id text")
        cur.execute("ALTER TABLE spine_meter ADD COLUMN IF NOT EXISTS ok boolean NOT NULL DEFAULT true")
        cur.execute("ALTER TABLE spine_meter ADD COLUMN IF NOT EXISTS note text")


def meter(conn, did: str, model: str, tokens_in: int, tokens_out: int, *,
          usd: float | None = None, stall: str | None = None, request_id: str | None = None,
          ok: bool = True, note: str | None = None) -> None:
    """ONE meter line, the same for every lane: who thought, which model,
    how many tokens, when (W17: the landing on the ground's clock) — and
    which mind service the model is, read from the ladder. P6.5 sp3: the
    dollars, the stall, the gateway's request id, the honest failure."""
    from . import services
    service = services.mind_did(conn, model) if stall is None else services.stall_did(conn, stall)
    with conn.transaction():
        conn.cursor().execute(
            "INSERT INTO spine_meter (did, model, tokens_in, tokens_out, at, service, usd, stall, request_id, ok, note)"
            " VALUES (%s, %s, %s, %s, clock_timestamp(), %s, %s, %s, %s, %s, %s)",
            (did, model, tokens_in, tokens_out, service, usd, stall, request_id, ok, note))


class MindUnavailable(RuntimeError):
    """No mind could serve — the reason in plain words (the reply the
    human reads; the meter's failed line carries it too)."""


class LiteLLMGateway:
    """THE lane (P6.5 sp3): every thought through the gateway box with the
    body's own key; the Stable decides which mind; the meter in dollars."""

    DEFAULT_MODEL = "claude-haiku-4-5-20251001"          # the model every template names by default
    STREAM_TIMEOUT_S = 120.0

    def __init__(self, base: str | None = None, key: str | None = None):
        from . import stable
        self.stable = stable.Gateway(base, key)
        self.base = self.stable.base

    # -- the door --------------------------------------------------------------------
    def _decide(self, conn, *, did: str, subject: str | None, model: str | None, klass: str | None,
                pin: str | None) -> dict:
        from . import stable
        d = stable.resolve_for(conn, subject=subject or did, model=model, klass=klass, pin=pin)
        if not d["ok"]:
            raise MindUnavailable(d["reason"])
        return d

    def _key(self, conn, did: str, subject: str | None) -> str:
        """The body's own key — its alias wears the body's NAME (the join's
        name for a DID handed in bare, the DID's tail as the last resort)."""
        from . import stable
        name = subject
        if not name:
            cur = conn.cursor()
            cur.execute("SELECT name FROM spine_joins WHERE did = %s ORDER BY join_id DESC LIMIT 1", (did,))
            r = cur.fetchone()
            name = r[0] if r else did.rsplit(":", 1)[-1]
        return stable.key_for(conn, did, name, self.stable)["key"]

    def _post(self, path: str, body: dict, key: str, *, stream: bool = False):
        import urllib.error
        import urllib.request
        req = urllib.request.Request(self.base + path, data=json.dumps(body).encode(), method="POST",
                                     headers={"Authorization": f"Bearer {key}", "content-type": "application/json"})
        try:
            return urllib.request.urlopen(req, timeout=self.STREAM_TIMEOUT_S)
        except urllib.error.HTTPError as e:
            raw = e.read()
            try:
                err = json.loads(raw).get("error") or {}
            except ValueError:
                err = {"message": raw.decode(errors="replace")[:300]}
            if e.code == 429 and "budget" in str(err.get("type") or err.get("message") or "").lower():
                raise Drained(str(err.get("message") or "the budget is spent"))
            raise GatewayRefused(e.code, str(err.get("message") or err)[:300])
        except (urllib.error.URLError, OSError) as e:
            raise GatewayRefused(0, f"the gateway at {self.base} did not answer: {getattr(e, 'reason', e)}")

    def _complete(self, body: dict, key: str, on_delta) -> tuple[str, list[dict], dict, dict]:
        """One round: (text, tool_calls, usage, headers) — streamed to
        `on_delta` when asked (the usage rides the last chunk)."""
        if on_delta is None:
            with self._post("/chat/completions", body, key) as r:
                headers = {k.lower(): v for k, v in r.headers.items()}
                out = json.loads(r.read())
            msg = (out.get("choices") or [{}])[0].get("message") or {}
            return (msg.get("content") or "", msg.get("tool_calls") or [], out.get("usage") or {},
                    dict(headers, id=out.get("id")))
        body = dict(body, stream=True, stream_options={"include_usage": True})
        text, usage, calls, rid = [], {}, {}, None
        with self._post("/chat/completions", body, key, stream=True) as r:
            headers = {k.lower(): v for k, v in r.headers.items()}
            for raw in r:
                line = raw.decode(errors="replace").strip()
                if not line.startswith("data:"):
                    continue
                data = line[5:].strip()
                if data == "[DONE]":
                    break
                try:
                    chunk = json.loads(data)
                except ValueError:
                    continue
                rid = rid or chunk.get("id")
                if chunk.get("usage"):
                    usage = chunk["usage"]
                for ch in chunk.get("choices") or []:
                    delta = ch.get("delta") or {}
                    if delta.get("content"):
                        text.append(delta["content"]); on_delta(delta["content"])
                    for tc in delta.get("tool_calls") or []:
                        i = tc.get("index", 0)
                        slot = calls.setdefault(i, {"id": None, "type": "function", "function": {"name": "", "arguments": ""}})
                        slot["id"] = slot["id"] or tc.get("id")
                        f = tc.get("function") or {}
                        slot["function"]["name"] = slot["function"]["name"] or f.get("name") or ""
                        slot["function"]["arguments"] += f.get("arguments") or ""
        return "".join(text), [calls[i] for i in sorted(calls)], usage, dict(headers, id=rid)

    def _land(self, conn, *, did: str, decision: dict, usage: dict, headers: dict) -> float:
        from . import stable
        tin, tout = int(usage.get("prompt_tokens") or 0), int(usage.get("completion_tokens") or 0)
        cost = headers.get("x-litellm-response-cost")
        if cost is not None:
            usd = float(cost)
        else:                                            # streaming: the pin's price, never a guess
            row = __import__("orreth_spine.services", fromlist=["get"]).get(conn, decision["stall"])
            usd = stable.usd((row or {}).get("manifest", {}).get("price") or {}, tin, tout)
        meter(conn, did, decision["stall"], tin, tout, usd=usd, stall=decision["stall"],
              request_id=headers.get("id") or headers.get("x-litellm-call-id"),   # the ledger keys on the answer's id
              note=decision["why"] if decision.get("degraded") else None)
        return usd

    def _fail(self, conn, *, did: str, stall: str | None, note: str) -> None:
        meter(conn, did, stall or "-", 0, 0, usd=0.0, stall=stall, ok=False, note=note[:300])

    def _honest(self, conn, *, did: str, subject: str | None, e: Exception, stall: str | None) -> str:
        """The words a body says when it cannot think — and the failed line."""
        from . import stable
        name = subject or did.rsplit(":", 1)[-1]
        if isinstance(e, Drained):
            stable.mark_drained(conn, did)
            words = stable.drained_words(name, stable.fuel(conn, did, self.stable))
        elif isinstance(e, MindUnavailable):
            words = f"I cannot think right now — {e}."
        elif isinstance(e, GatewayRefused) and e.code == 0:
            words = f"I cannot think right now — {e.words}. Someone must light the gateway (scripts/dev.sh up)."
        else:
            words = f"I cannot think right now — the gateway refused: {getattr(e, 'words', e)}."
        self._fail(conn, did=did, stall=stall, note=words)
        return words

    def think(self, conn, *, did: str, system: str, prompt: str,
              model: str | None = None, max_tokens: int = 1024,
              on_delta=None, subject: str | None = None, klass: str | None = None,
              pin: str | None = None) -> str:
        ensure_schema(conn)
        stall = None
        try:
            d = self._decide(conn, did=did, subject=subject, model=model, klass=klass, pin=pin)
            stall = d["stall"]
            key = self._key(conn, did, subject)
            text, _calls, usage, headers = self._complete(
                {"model": stall, "max_tokens": max_tokens,
                 "messages": [{"role": "system", "content": system}, {"role": "user", "content": prompt}]},
                key, on_delta)
        except (MindUnavailable, Drained, GatewayRefused) as e:
            return self._honest(conn, did=did, subject=subject, e=e, stall=stall)
        self._land(conn, did=did, decision=d, usage=usage, headers=headers)
        return text

    def think_acting(self, conn, *, did: str, system: str, prompt: str,
                     door, model: str | None = None, max_tokens: int = 1024,
                     max_rounds: int = 3, on_delta=None, subject: str | None = None,
                     klass: str | None = None, pin: str | None = None) -> tuple[str, list[str]]:
        """The acting mind through the gateway: the door's DECLARED tools in
        the OpenAI shape; every tool call through the door (journaled,
        interlocked — a ConsequentialHold propagates); every round metered."""
        ensure_schema(conn)
        stall = None
        try:
            d = self._decide(conn, did=did, subject=subject, model=model, klass=klass, pin=pin)
            stall = d["stall"]
            key = self._key(conn, did, subject)
        except (MindUnavailable, Drained, GatewayRefused) as e:
            return self._honest(conn, did=did, subject=subject, e=e, stall=stall), []
        tools = [{"type": "function", "function": {"name": t["name"], "description": t.get("description", ""),
                                                    "parameters": t.get("input_schema") or {"type": "object", "properties": {}}}}
                 for t in door.schemas()]
        messages = [{"role": "system", "content": system}, {"role": "user", "content": prompt}]
        notes: list[str] = []
        for _round in range(max_rounds):
            try:
                text, calls, usage, headers = self._complete(
                    {"model": stall, "max_tokens": max_tokens, "messages": messages, "tools": tools}, key, on_delta)
            except (Drained, GatewayRefused) as e:
                return self._honest(conn, did=did, subject=subject, e=e, stall=stall), notes
            self._land(conn, did=did, decision=d, usage=usage, headers=headers)
            if not calls:
                return text, notes
            messages.append({"role": "assistant", "content": text or None, "tool_calls": calls})
            for c in calls:
                f = c.get("function") or {}
                try:
                    args = json.loads(f.get("arguments") or "{}")
                except ValueError:
                    args = {}
                result = door.call(f.get("name"), dict(args))   # holds propagate
                notes.append(f"used the {f.get('name')} tool through the door")
                messages.append({"role": "tool", "tool_call_id": c.get("id"), "content": str(result)})
        return ("I ran out of thinking rounds before finishing — that honesty beats a guess.", notes)


class Drained(RuntimeError):
    """The body's lease is spent (the gateway's 429): the fuel clause holds."""


class GatewayRefused(RuntimeError):
    def __init__(self, code: int, words: str):
        super().__init__(words)
        self.code, self.words = code, words


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
              model: str | None = None, max_tokens: int = 1024,
              on_delta=None, subject: str | None = None, klass: str | None = None,
              pin: str | None = None) -> str:
        """`on_delta(text)` streams the words as they form — display
        only, glass-bound; the durable truth is always the final reply
        landed through the door."""
        ensure_schema(conn)
        m = model or self.DEFAULT_MODEL
        if on_delta is not None:
            with self._client.messages.stream(
                    model=m, max_tokens=max_tokens, system=system,
                    messages=[{"role": "user", "content": prompt}]) as st:
                for t in st.text_stream:
                    on_delta(t)
                msg = st.get_final_message()
        else:
            msg = self._client.messages.create(
                model=m, max_tokens=max_tokens, system=system,
                messages=[{"role": "user", "content": prompt}])
        text = "".join(b.text for b in msg.content if b.type == "text")
        meter(conn, did, m, msg.usage.input_tokens, msg.usage.output_tokens)
        return text

    def think_acting(self, conn, *, did: str, system: str, prompt: str,
                     door, model: str | None = None, max_tokens: int = 1024,
                     max_rounds: int = 3, on_delta=None, subject: str | None = None,
                     klass: str | None = None, pin: str | None = None) -> tuple[str, list[str]]:
        """The acting mind: the model may use the door's DECLARED tools;
        every tool call goes through the door (journaled, interlocked),
        every model round through the meter. Returns (reply, act_notes).
        A ConsequentialHold propagates — the resident owns the L2 path.
        `on_delta` streams each round's words as they form."""
        from .tools import ConsequentialHold  # noqa: F401 (re-raise passes)
        m = model or self.DEFAULT_MODEL
        messages = [{"role": "user", "content": prompt}]
        notes: list[str] = []
        for _round in range(max_rounds):
            if on_delta is not None:
                with self._client.messages.stream(
                        model=m, max_tokens=max_tokens, system=system,
                        tools=door.schemas(), messages=messages) as st:
                    for t in st.text_stream:
                        on_delta(t)
                    msg = st.get_final_message()
            else:
                msg = self._client.messages.create(
                    model=m, max_tokens=max_tokens, system=system,
                    tools=door.schemas(), messages=messages)
            meter(conn, did, m, msg.usage.input_tokens, msg.usage.output_tokens)
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

    DEFAULT_MODEL = "fake-mind"

    def __init__(self, reply: str = "a thought from the fake mind"):
        self.reply = reply
        self.calls: list[dict] = []

    def think(self, conn, *, did: str, system: str, prompt: str,
              model: str | None = None, max_tokens: int = 1024,
              on_delta=None, subject: str | None = None, klass: str | None = None,
              pin: str | None = None) -> str:
        ensure_schema(conn)
        self.calls.append({"system": system, "prompt": prompt, "subject": subject, "pin": pin})
        if on_delta is not None:
            for w in self.reply.split(" "):
                on_delta(w + " ")
        meter(conn, did, model or self.DEFAULT_MODEL, len(prompt.split()), len(self.reply.split()))
        return self.reply


class FakeActingGateway:
    """The test lane for the acting mind: a scripted sequence of acts —
    ("tool", name, args) steps go through the REAL door (so capability,
    journaling, and interlock laws are exercised), then a ("text", ...)
    step answers, with {result} carrying the last tool result."""

    DEFAULT_MODEL = "fake-acting-mind"

    def __init__(self, script: list[tuple]):
        self.script = script

    def think_acting(self, conn, *, did: str, system: str, prompt: str,
                     door, model: str | None = None, max_tokens: int = 1024,
                     max_rounds: int = 3, on_delta=None, subject: str | None = None,
                     klass: str | None = None, pin: str | None = None) -> tuple[str, list[str]]:
        ensure_schema(conn)
        meter(conn, did, model or self.DEFAULT_MODEL, len(prompt.split()), 12)
        notes, last = [], ""
        for step in self.script:
            if step[0] == "tool":
                last = door.call(step[1], step[2])       # holds propagate
                notes.append(f"used the {step[1]} tool through the door")
            else:
                text = step[1].replace("{result}", last)
                if on_delta is not None:
                    for w in text.split(" "):
                        on_delta(w + " ")
                return (text, notes)
        return ("the script ended without words", notes)


def meter_lines(conn, did: str) -> list[tuple]:
    ensure_schema(conn)
    cur = conn.cursor()
    cur.execute("SELECT model, tokens_in, tokens_out FROM spine_meter"
                " WHERE did = %s ORDER BY meter_id", (did,))
    return cur.fetchall()


def meter_rows(conn, did: str) -> list[dict]:
    """P6.5 sp3: the lines with their dollars, stall, and honest failures."""
    ensure_schema(conn)
    cur = conn.cursor()
    cur.execute("SELECT model, tokens_in, tokens_out, usd, stall, request_id, ok, note, at FROM spine_meter"
                " WHERE did = %s ORDER BY meter_id", (did,))
    return [{"model": r[0], "tokens_in": r[1], "tokens_out": r[2], "usd": r[3], "stall": r[4], "request_id": r[5],
             "ok": r[6], "note": r[7], "at": r[8].isoformat()} for r in cur.fetchall()]
