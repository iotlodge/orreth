# PROVENANCE: Claude Fable 5 (claude-fable-5) — rearch P2 sp1, the body is born · 2026-09-16
"""The ask road (canon 0002's chain, in miniature): ONE write path.

A human's ask lands on the ground with its event in one transaction; the
DISPATCHER — an events-rail consumer — turns the committed fact into an
invocation command on RabbitMQ. No broker delivery alone changes truth;
a duplicated command is absorbed by the resident's inbox; the authority
chain (who asked) rides every hop (canon 0004: attribution is the
point)."""
from __future__ import annotations

import secrets

import pika

from . import envelope as ev
from . import outbox, projector
from .rails import COMMAND_EXCHANGE, RABBIT_URL
from .resident import ASK_RECEIVED, SERVE_KEY


def submit_ask(conn, text: str, *,
               person: str = "did:orreth:person:jb") -> str:
    """The glass's write: the ask row and its committed event, one
    transaction. The event is pointer-only; the words live on the
    ground."""
    from .resident import ensure_schema
    ensure_schema(conn)
    outbox.ensure_schema(conn)
    ask_id = "ask_" + secrets.token_hex(8)
    e = ev.make_envelope(
        kind="event", type=ASK_RECEIVED, universe_id="u:dev",
        scope_path="u:dev",
        payload={"ref": ask_id, "hash": ev.content_hash(text)},
        correlation_id=ask_id, authority_chain=[person],
        aggregate={"type": "ask", "id": ask_id, "sequence": 1})

    def domain(cur):
        cur.execute("INSERT INTO spine_asks (ask_id, text, person)"
                    " VALUES (%s, %s, %s)", (ask_id, text, person))

    outbox.commit_with_outbox(conn, ev.encode(e), e["message_id"], domain)
    return ask_id


def publish_command(env: dict, rabbit_url: str | None = None) -> None:
    """Publisher-side topology declaration is the law here: on a fresh
    broker a topic exchange DROPS messages with no bound queue, silently
    — so the publisher declares queue + binding too (idempotent), and
    publishes mandatory so an unroutable command fails LOUDLY instead of
    vanishing. (Found on CI's fresh broker; the dev rig's leftover
    bindings had been hiding it.)"""
    from .resident import SERVE_QUEUE
    raw = ev.encode(env)
    rc = pika.BlockingConnection(pika.URLParameters(rabbit_url or RABBIT_URL))
    try:
        ch = rc.channel()
        ch.confirm_delivery()
        ch.exchange_declare(COMMAND_EXCHANGE, exchange_type="topic",
                            durable=True)
        ch.queue_declare(SERVE_QUEUE, durable=True)
        ch.queue_bind(SERVE_QUEUE, COMMAND_EXCHANGE, SERVE_KEY)
        ch.basic_publish(COMMAND_EXCHANGE, SERVE_KEY, raw,
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
    e = ev.make_envelope(
        kind="command", type=CONFIRM_CMD, universe_id="u:dev",
        scope_path="u:dev",
        payload={"ref": ask_id, "hash": "sha256:-",
                 "approved": bool(approve)},
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
        **kw)
