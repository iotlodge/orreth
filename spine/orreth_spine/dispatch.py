# PROVENANCE: Claude Fable 5 (claude-fable-5) — rearch P2 sp1, the body is born · 2026-09-16
"""The ask road (canon 0002's chain, in miniature): ONE write path.

A human's ask lands on the ground with its event in one transaction; the
DISPATCHER — an events-rail consumer — turns the committed fact into an
invocation command on RabbitMQ. No broker delivery alone changes truth;
a duplicated command is absorbed by the resident's inbox; the authority
chain (who asked) rides every hop (canon 0004: attribution is the
point)."""
from __future__ import annotations

import json
import secrets

import pika

from . import envelope as ev
from . import outbox, projector
from .rails import COMMAND_EXCHANGE, RABBIT_URL
from .resident import ASK_RECEIVED, SERVE_KEY


def submit_ask(conn, text: str, *, person: str = "did:orreth:person:jb",
               to: list[str] | None = None, window: dict | None = None,
               session: str | None = None):
    """The glass's write: the ask row and its committed event, one
    transaction. The event is pointer-only; the words live on the ground.
    `to` names residents for a FAN-OUT (canon 0001 P14): the same request
    becomes one ask PER named resident — each answers through its own
    role lens, results stay distinct, and they share a fanout id so the
    glass can offer 'summarize together' on demand. Untargeted asks keep
    returning one id (any resident serves); a fan-out returns the list."""
    from .resident import ensure_schema
    ensure_schema(conn)
    outbox.ensure_schema(conn)
    fanout = ("fan_" + secrets.token_hex(6)) if to and len(to) > 1 else None
    ids = []
    for target in (to or [None]):
        ask_id = "ask_" + secrets.token_hex(8)
        payload = {"ref": ask_id, "hash": ev.content_hash(text)}
        if target:
            payload["target"] = target
        if session:
            payload["session"] = session   # P20: the ask names its session
        if window:                      # P6: the time scope rides the ask —
            payload["window"] = {       # set by typed words, no click
                "from": str(window.get("from") or ""),
                "to": str(window.get("to") or "")}
        e = ev.make_envelope(
            kind="event", type=ASK_RECEIVED, universe_id=ev.scope(),
            scope_path=ev.scope(), payload=payload,
            correlation_id=fanout or ask_id, authority_chain=[person],
            aggregate={"type": "ask", "id": ask_id, "sequence": 1})

        def domain(cur, a=ask_id, t=target, w=payload.get("window")):
            cur.execute(
                "INSERT INTO spine_asks (ask_id, text, person, target,"
                " fanout, scope, time_window, session)"
                " VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                (a, text, person, t, fanout, ev.scope(),     # asked in
                 json.dumps(w) if w else None, session))     # THIS world

        outbox.commit_with_outbox(conn, ev.encode(e), e["message_id"],
                                  domain)
        ids.append(ask_id)
    return ids if to else ids[0]


def publish_command(env: dict, rabbit_url: str | None = None) -> None:
    """Publisher-side topology declaration is the law here: on a fresh
    broker a topic exchange DROPS messages with no bound queue, silently
    — so the publisher declares queue + binding too (idempotent), and
    publishes mandatory so an unroutable command fails LOUDLY instead of
    vanishing. (Found on CI's fresh broker; the dev rig's leftover
    bindings had been hiding it.) A targeted command routes to the named
    resident's own queue; an untargeted one to the shared any-resident
    queue."""
    from .resident import serve_key, serve_queue
    target = (env.get("payload") or {}).get("target")
    queue = serve_queue(target)
    key = serve_key(target)
    raw = ev.encode(env)
    rc = pika.BlockingConnection(pika.URLParameters(rabbit_url or RABBIT_URL))
    try:
        ch = rc.channel()
        ch.confirm_delivery()
        ch.exchange_declare(COMMAND_EXCHANGE, exchange_type="topic",
                            durable=True)
        ch.queue_declare(queue, durable=True)
        ch.queue_bind(queue, COMMAND_EXCHANGE, key)
        ch.basic_publish(COMMAND_EXCHANGE, key, raw,
                         properties=pika.BasicProperties(
                             delivery_mode=2, message_id=env["message_id"]),
                         mandatory=True)
    finally:
        rc.close()


def confirm_ask(conn, ask_id: str, *, approve: bool,
                person: str = "did:orreth:person:jb",
                rabbit_url: str | None = None) -> None:
    """The human's click at the interlock (canon 0001 L2): only an
    explicit approve releases the act — anything else, including
    silence, is a cancel. The decision is a command wearing the human's
    own authority."""
    from .resident import CONFIRM_CMD
    payload = {"ref": ask_id, "hash": "sha256:-", "approved": bool(approve)}
    cur = conn.cursor()
    cur.execute("SELECT target, served_by FROM spine_asks WHERE ask_id=%s",
                (ask_id,))
    row = cur.fetchone()
    if row:
        target = row[0]
        if not target and row[1]:
            # the holder set served_by at the hold — route to that name
            cur.execute("SELECT name FROM spine_joins WHERE did = %s"
                        " ORDER BY join_id DESC LIMIT 1", (row[1],))
            j = cur.fetchone()
            target = j[0] if j else None
        if target:
            payload["target"] = target
    e = ev.make_envelope(
        kind="command", type=CONFIRM_CMD, universe_id=ev.scope(),
        scope_path=ev.scope(), payload=payload,
        correlation_id=ask_id, authority_chain=[person])
    publish_command(e, rabbit_url)


def _command_for(event_env: dict) -> dict:
    return ev.make_envelope(
        kind="command", type="orreth.resident.serve.v1",
        universe_id=event_env["universe_id"],
        scope_path=event_env["scope_path"],
        payload=dict(event_env["payload"]),
        correlation_id=event_env.get("correlation_id"),
        authority_chain=event_env.get("authority_chain"))


def dispatch_once(conn, *, consumer: str, group: str,
                  rabbit_url: str | None = None, **kw) -> dict:
    """Consume committed ask.received facts and enqueue one serve command
    each. A redelivered fact enqueues a duplicate command — harmless: the
    resident's inbox absorbs it (proven in the suite)."""
    return projector.run_once(
        conn, group=group, topics=[ASK_RECEIVED], consumer_name=consumer,
        apply=lambda _cur, env: publish_command(_command_for(env),
                                                rabbit_url),
        skip=lambda env: env.get("scope_path") != ev.scope(), **kw)


def run_dispatcher(conn, *, consumer: str, group: str, stop,
                   rabbit_url: str | None = None, ready=None,
                   offset: str = "latest") -> None:
    """The standing dispatcher (the rig's shape): one consumer for its
    whole life, dispatching only its own world's NEW facts (latest —
    a rig dispatches what happens while it lives; another world's facts
    cost nothing)."""
    projector.run_forever(
        conn, group=group, topics=[ASK_RECEIVED], consumer_name=consumer,
        apply=lambda _cur, env: publish_command(_command_for(env),
                                                rabbit_url),
        skip=lambda env: env.get("scope_path") != ev.scope(),
        stop=stop, ready=ready, offset=offset)
