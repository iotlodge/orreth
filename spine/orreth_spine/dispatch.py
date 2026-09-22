# PROVENANCE: Claude Fable 5 (claude-fable-5) — rearch P2 sp1, the body is born · 2026-09-16
# Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P6 sp3, a body never confirms (one face) · 2026-09-21
# Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P6 cure sp1 (kernel), walk #7's W5 · W12 · W19 · 2026-09-21
"""The ask road (canon 0002's chain, in miniature): ONE write path.

A human's ask lands on the ground with its event in one transaction; the
DISPATCHER — an events-rail consumer — turns the committed fact into an
invocation command on RabbitMQ. No broker delivery alone changes truth;
a duplicated command is absorbed by the resident's inbox; the authority
chain (who asked) rides every hop (canon 0004: attribution is the
point)."""
from __future__ import annotations

import json
import re
import secrets

import pika

from . import envelope as ev
from . import outbox, projector
from .rails import COMMAND_EXCHANGE, RABBIT_URL
from .resident import ASK_RECEIVED, SERVE_KEY

ASK_REFUSED = "orreth.ask.refused.v1"     # W19: an ask to a body that is not here


def absent(conn, name: str) -> str | None:
    """Is the body named here to serve? None when it is (a join row in
    this world, not refused since); else the reason in words (W19): a
    body refused at birth says its reasons and the cure; a name that
    never joined says so. Presence (alive/dormant) is not absence — a
    dormant body may still wake to its bench."""
    from . import placement
    cur = conn.cursor()
    cur.execute("SELECT max(joined_at) FROM spine_joins WHERE name = %s AND scope = %s",
                (name, ev.scope()))
    joined = cur.fetchone()[0]
    r = placement.refusals(conn).get(name)
    if r is not None and (joined is None or r["refused_at"] > joined):
        return "refused at birth: " + "; ".join(r["reasons"]) + "; fix its template to seat it"
    if joined is None:
        return "no body of that name has joined this world"
    return None


def address(text: str, names) -> str | None:
    """W7 (walk #7): a name at the HEAD of an ask selects that body —
    "echo, what is today's date?" · "@echo …" · "librarian: …" — when the
    name is a body of this world (`names`). Anything else is unaddressed
    and the fan-out stays. Case does not matter; the name comes back as
    the body spells it."""
    m = re.match(r"^\s*@?([A-Za-z0-9_-]+)\s*[,:]\s*\S", text or "")
    if not m:
        return None
    want = m.group(1).lower()
    for n in names or ():
        if str(n).lower() == want:
            return str(n)
    return None


def refusal_words(name: str, reason: str) -> str:
    """The door's plain reply for an ask to a body that is not here
    (conformance `absent_words`)."""
    return f"{name} is not here — {reason}"


def submit_ask(conn, text: str, *, person: str = "did:orreth:person:jb",
               to: list[str] | None = None, window: dict | None = None,
               session: str | None = None, parent_marker: str | None = None,
               kind: str | None = None, zone: str | None = None):
    """The glass's write: the ask row and its committed event, one
    transaction. The event is pointer-only; the words live on the ground.
    `to` names residents for a FAN-OUT (canon 0001 P14): the same request
    becomes one ask PER named resident — each answers through its own
    role lens, results stay distinct, and they share a fanout id so the
    glass can offer 'summarize together' on demand. Untargeted asks keep
    returning one id (any resident serves); a fan-out returns the list.
    An ask to a body that is NOT HERE (W19: refused at birth, or never
    joined this world) is answered at the door: its row lands with status
    `refused` and the reply in plain words, its fact `orreth.ask.refused.v1`
    — never an ask.received, never left in flight; a fan-out drops the
    absent body and the refused row says so in the chat. `zone` (W12) is
    the human's time zone for this ask, an IANA name."""
    from . import markers
    from .resident import ensure_schema
    ensure_schema(conn)
    outbox.ensure_schema(conn)
    markers.ensure_schema(conn)
    fanout = ("fan_" + secrets.token_hex(6)) if to and len(to) > 1 else None
    state = "in"
    if session:                        # an ask is born in its session's state
        cur0 = conn.cursor()
        cur0.execute("SELECT coalesce(state, 'in') FROM spine_sessions"
                     " WHERE session_id = %s", (session,))
        row0 = cur0.fetchone()
        state = row0[0] if row0 else "in"
    ids = []
    for target in (to or [None]):
        ask_id = "ask_" + secrets.token_hex(8)
        # the ask's marker (0006): an include's ask is a THOUGHT under the
        # session's latest objective; anything else is an OBJECTIVE — a root,
        # or a child of the marker it was dispatched under (an occurrence
        # of an intention, an act of interest)
        # P23 (block 11): the ask wears its kind — the chip's word, when
        # given, says thought or objective; an intention is declared at the
        # door, never asked
        if kind not in (None, "thought", "objective"):
            raise ValueError("an ask is a thought or an objective — an intention is declared")
        ask_kind, parent = (kind or "objective"), parent_marker
        if target in markers.INCLUDES or ask_kind == "thought":
            ask_kind = "thought"
            if parent is None and session:
                cur0 = conn.cursor()
                cur0.execute(
                    "SELECT a.marker FROM spine_asks a JOIN spine_markers m ON m.marker_id = a.marker"
                    " WHERE a.session = %s AND m.kind = 'objective' ORDER BY a.asked_at DESC LIMIT 1",
                    (session,))
                r0 = cur0.fetchone(); parent = r0[0] if r0 else None
        marker_id = markers.new_id()
        marker = {"kind": ask_kind, "id": marker_id, "parent": parent, "by": person}
        why = absent(conn, target) if target else None
        if why is not None:                       # W19: refused at the door, recorded — the
            ids.append(_refuse_at_door(conn, ask_id, text, person, target, why,   # same marker
                                       marker=marker, fanout=fanout, session=session, state=state))
            continue
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
            aggregate={"type": "ask", "id": ask_id, "sequence": 1},
            marker=marker)

        def domain(cur, a=ask_id, t=target, w=payload.get("window"),
                   mk=marker_id, kd=ask_kind, pa=parent):
            markers.insert(cur, mk, kd, pa, a, person)     # the fact and its
            cur.execute(                                   # marker, together
                "INSERT INTO spine_asks (ask_id, text, person, target,"
                " fanout, scope, time_window, session, state, marker, zone)"
                " VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (a, text, person, t, fanout, ev.scope(),     # asked in
                 json.dumps(w) if w else None, session, state, mk,   # THIS world
                 zone or None))

        outbox.commit_with_outbox(conn, ev.encode(e), e["message_id"],
                                  domain)
        ids.append(ask_id)
    return ids if to else ids[0]


def _refuse_at_door(conn, ask_id: str, text: str, person: str, target: str, why: str,
                    *, marker: dict, fanout: str | None, session: str | None, state: str) -> str:
    """The refused ask: its row (status `refused`, the reply, the kernel
    as server, replied at the landing) and its fact in one transaction —
    wearing the marker the ask would have worn (its kind, its parent), so
    the lineage records the refusal where the act was meant to hang."""
    from . import markers
    from .proof import KERNEL
    reply = refusal_words(target, why)
    marker_id = marker["id"]
    e = ev.make_envelope(
        kind="event", type=ASK_REFUSED, universe_id=ev.scope(), scope_path=ev.scope(),
        payload={"ref": ask_id, "hash": ev.content_hash(text), "target": target,
                 "reason": why, **({"session": session} if session else {})},
        correlation_id=fanout or ask_id, authority_chain=[person, KERNEL],
        aggregate={"type": "ask", "id": ask_id, "sequence": 1}, marker=marker)

    def domain(cur):
        markers.insert(cur, marker_id, marker["kind"], marker["parent"], ask_id, person)
        cur.execute(
            "INSERT INTO spine_asks (ask_id, text, person, target, fanout, scope, session,"
            " state, marker, status, reply, served_by, replied_at)"
            " VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'refused', %s, %s, clock_timestamp())",
            (ask_id, text, person, target, fanout, ev.scope(), session, state, marker_id,
             reply, KERNEL))

    outbox.commit_with_outbox(conn, ev.encode(e), e["message_id"], domain)
    return ask_id


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
                code: str | None = None,
                rabbit_url: str | None = None) -> dict:
    """The human's word at the interlock (canon 0001 L2 · P6 sp1 L3):
    only an explicit approve releases the act — anything else, including
    silence, is a cancel, and a cancel is ALWAYS taken (rule 11). An
    approve is judged here for the proof the hold demands: L2 the click
    alone; L3-code the asker's authenticator code; L3-master `person` a
    declared master and never the asker. Every refusal — wrong code,
    a stranger, the asker as master, an ask nobody holds — is the ONE
    face (rule 4): `proof.NotConfirmed` — and so is any BODY of this
    ground offering the word (P6 sp3: MITL weighs, the human cuts). The
    third refusal RESTS the act (a recorded cancel) before the face is
    shown. The decision rides a
    command wearing the human's own authority; an act the kernel holds
    itself is settled on the ground, no rail."""
    from . import proof
    proof.ensure_schema(conn)
    cur = conn.cursor()
    # P6 sp3 (covenant rule 2, MITL's law): a BODY never confirms — MITL
    # weighs, the human cuts. A self that ever joined this ground offering
    # a yes or a no at the door is refused with the one face, at every level
    cur.execute("SELECT 1 FROM spine_joins WHERE did = %s LIMIT 1", (person,))
    if cur.fetchone():
        raise proof.NotConfirmed()
    cur.execute("SELECT target, served_by, held, person, status FROM spine_asks"
                " WHERE ask_id=%s AND scope=%s", (ask_id, ev.scope()))
    row = cur.fetchone()
    held = json.loads(row[2]) if row and row[2] else {}
    level = held.get("level") or "L2"
    reason = None
    if approve:
        if row is None or row[4] != "awaiting-confirm":
            raise proof.NotConfirmed()          # nothing held: the one face
        if level == "L3-master" and held.get("needs_code") and not held.get("code_ok"):
            # W5: the kernel's intention — the ASKER's code comes first; the
            # master's click counts only after it. A master clicking before
            # the code, a stranger, or a wrong code: the one face
            if person != row[3]:
                raise proof.NotConfirmed()
            try:
                proof.judge(conn, ask_id, level="L3-code", asker=row[3], by=person, code=code)
            except proof.NotConfirmed as nc:
                if nc.rest:
                    _settle(conn, row, ask_id, approve=False, person=person, level=level,
                            reason="three wrong proofs — the kernel rested this act",
                            rabbit_url=rabbit_url)
                raise
            held["code_ok"] = True
            with conn.transaction():
                conn.cursor().execute("UPDATE spine_asks SET held = %s WHERE ask_id = %s",
                                      (json.dumps(held), ask_id))
            return {"id": ask_id, "approve": True, "level": level, "step": "code",
                    "next": "master"}          # held still: the master's click is owed
        try:
            proof.judge(conn, ask_id, level=level, asker=row[3], by=person, code=code)
        except proof.NotConfirmed as nc:
            if nc.rest:                         # three wrong proofs: the act rests
                _settle(conn, row, ask_id, approve=False, person=person, level=level,
                        reason="three wrong proofs — the kernel rested this act",
                        rabbit_url=rabbit_url)
            raise
    _settle(conn, row, ask_id, approve=approve, person=person, level=level,
            reason=reason, rabbit_url=rabbit_url)
    return {"id": ask_id, "approve": bool(approve), "level": level}


def _settle(conn, row, ask_id: str, *, approve: bool, person: str, level: str,
            reason: str | None, rabbit_url: str | None) -> None:
    from . import proof
    from .resident import CONFIRM_CMD
    if row and row[1] == proof.KERNEL:          # the kernel holds its own acts
        proof.settle_kernel_act(conn, ask_id, approve=approve, by=person,
                                level=level, reason=reason)
        return
    payload = {"ref": ask_id, "hash": "sha256:-", "approved": bool(approve),
               "proof": level, "by": person}
    if reason:
        payload["reason"] = reason
    if row:
        target = row[0]
        if not target and row[1]:
            # the holder set served_by at the hold — route to that name
            cur = conn.cursor()
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
