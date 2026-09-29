# PROVENANCE: Claude Fable 5 (claude-fable-5) — rearch P1 sp2, the events shadow (M4-lite) · 2026-09-16
# Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp8 lock 5: run_once ends at the topic's end, never by waiting out a silence · 2026-09-27
# Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch row 4, re-base sp1: POISON-PARKING — the park once by its place, its fact, the HOLD until a person advances it, the advance · 2026-09-28
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

Re-base sp1 (the same law on both kernels): a poison is parked ONCE by its
place on the rail — the row and its fact (`orreth.inbox.parked.v1`) in one
transaction — and the standing consumer HOLDS at it: the offset is never
committed past, nothing after it is applied, and every two seconds it asks
the ground whether a person advanced it (`advance` — `POST /parked/advance`,
a governing seat; `orreth.inbox.advanced.v1` in their name). A fact that can
never apply (a gap in its aggregate's sequence, a shape the effect refuses)
is poison too; the rail's own refusals are not.
"""
from __future__ import annotations

import hashlib
import os
import time

from confluent_kafka import Consumer

from . import envelope as ev
from . import inbox

KAFKA_BOOTSTRAP = os.environ.get("SPINE_KAFKA", "localhost:9092")
PARKED = "orreth.inbox.parked.v1"          # the consumer parked a poison event with its evidence and holds at it
ADVANCED = "orreth.inbox.advanced.v1"      # a person let the consumer advance past it — their explicit decision
KERNEL = "the kernel"
HOLD_POLL_S = 2.0                          # how often a holding consumer asks the ground whether a person advanced it
POISON = (inbox.GapDetected, KeyError, ValueError, TypeError)   # the fact's own refusals — never the rail's


def body_hash(body: bytes) -> str:
    """The evidence's hash: `sha256:` + hex over the body's bytes as delivered."""
    return "sha256:" + hashlib.sha256(bytes(body or b"")).hexdigest()


def parked_ref(parked_id: int) -> str:
    return f"parked:{int(parked_id)}"


def parked_payload(parked_id: int, consumer: str, topic: str, partition: int, offset: int,
                   body_hash_: str, reason: str) -> dict:
    """Where on the rail, whose consumer, the evidence's hash, why (conformance `inbox_parked_fact`)."""
    return {"ref": parked_ref(parked_id), "hash": body_hash_, "consumer": consumer, "topic": topic,
            "partition": int(partition), "offset": int(offset), "reason": reason}


def advanced_payload(parked_id: int, consumer: str, topic: str, partition: int, offset: int, by: str) -> dict:
    """The same place, and who decided (conformance `inbox_advanced_fact`)."""
    return {"ref": parked_ref(parked_id), "hash": ev.content_hash(by), "consumer": consumer, "topic": topic,
            "partition": int(partition), "offset": int(offset), "by": by}


def parked_fact(parked_id: int, consumer: str, topic: str, partition: int, offset: int, body: bytes,
                reason: str, scope: str | None = None) -> dict:
    sc = scope or ev.scope()
    return ev.make_envelope(kind="event", type=PARKED, universe_id=sc, scope_path=sc,
                            payload=parked_payload(parked_id, consumer, topic, partition, offset,
                                                   body_hash(body), reason),
                            correlation_id=parked_ref(parked_id), authority_chain=[KERNEL])


def advanced_fact(parked_id: int, consumer: str, topic: str, partition: int, offset: int, by: str,
                  scope: str | None = None) -> dict:
    sc = scope or ev.scope()
    return ev.make_envelope(kind="event", type=ADVANCED, universe_id=sc, scope_path=sc,
                            payload=advanced_payload(parked_id, consumer, topic, partition, offset, by),
                            correlation_id=parked_ref(parked_id), authority_chain=[by])


def parked_words(consumer: str, topic: str, partition: int, offset: int, reason: str) -> str:
    """The park in plain words (the log, the tape, the monitor; conformance `parked_words`)."""
    return (f"{consumer} parked the event at {topic}/{partition}@{offset} — {reason} — and holds there"
            " until a person advances it")


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
        # re-base sp1: the operator's word that let a consumer advance past a poison
        cur.execute("ALTER TABLE spine_parked ADD COLUMN IF NOT EXISTS advanced_by text")
        cur.execute("ALTER TABLE spine_parked ADD COLUMN IF NOT EXISTS advanced_at timestamptz")


def park(conn, consumer: str, msg, reason: str) -> tuple[int, bool]:
    """PARK a poison event with its evidence — the row and its fact in one
    transaction, once per PLACE on the rail (a restart that re-reads the same
    offset finds the row and parks nothing twice). Returns the parked id and
    whether this call wrote it; the reason is cut at 500 characters."""
    from . import outbox
    reason = reason[:500]
    topic, partition, offset = msg.topic(), msg.partition(), msg.offset()
    cur = conn.cursor()
    cur.execute("SELECT parked_id FROM spine_parked WHERE consumer = %s AND topic = %s AND partition = %s"
                " AND kafka_offset = %s ORDER BY parked_id LIMIT 1", (consumer, topic, partition, offset))
    row = cur.fetchone()
    if row:
        return int(row[0]), False
    body = bytes(msg.value() or b"")
    with conn.transaction():
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO spine_parked (consumer, topic, partition, kafka_offset, body, reason)"
            " VALUES (%s, %s, %s, %s, %s, %s) RETURNING parked_id",
            (consumer, topic, partition, offset, body, reason))
        pid = int(cur.fetchone()[0])
        e = parked_fact(pid, consumer, topic, partition, offset, body, reason)
        outbox.add_row(cur, ev.encode(e), e["message_id"])
    return pid, True


def advanced(conn, parked_id: int) -> bool:
    """The hold's question: has a person advanced past this parked event?"""
    cur = conn.cursor()
    cur.execute("SELECT advanced_at IS NOT NULL FROM spine_parked WHERE parked_id = %s", (int(parked_id),))
    row = cur.fetchone()
    return bool(row and row[0])


def advance(conn, parked_id: int, by: str) -> dict | None:
    """THE OPERATOR'S WORD: advance past a parked event — recorded on the row with
    who and when, said as `orreth.inbox.advanced.v1`; the holding consumer commits
    the offset on its next look. None when no such event; one already advanced
    answers `already: True` and mints nothing twice."""
    from . import outbox
    cur = conn.cursor()
    cur.execute("SELECT consumer, topic, partition, kafka_offset, advanced_by, advanced_at FROM spine_parked"
                " WHERE parked_id = %s", (int(parked_id),))
    row = cur.fetchone()
    if row is None:
        return None
    consumer, topic, partition, offset, adv_by, adv_at = row
    if adv_at is not None:
        return {"parked_id": int(parked_id), "advanced": True, "already": True,
                "advanced_by": adv_by, "advanced_at": adv_at.isoformat()}
    with conn.transaction():
        cur = conn.cursor()
        cur.execute("UPDATE spine_parked SET advanced_by = %s, advanced_at = now() WHERE parked_id = %s"
                    " RETURNING advanced_at", (by, int(parked_id)))
        at = cur.fetchone()[0]
        e = advanced_fact(int(parked_id), consumer, topic or "", partition or 0, offset or 0, by)
        outbox.add_row(cur, ev.encode(e), e["message_id"])
    return {"parked_id": int(parked_id), "advanced": True, "already": False, "advanced_by": by,
            "advanced_at": at.isoformat(), "message_id": e["message_id"]}


def parked(conn, consumer: str | None = None, limit: int = 20) -> list[dict]:
    """The parked events still HELD (not advanced), newest first — of one consumer
    or of every consumer; each with its place, its reason, the evidence's size and
    hash, and plain words."""
    cur = conn.cursor()
    cur.execute("SELECT parked_id, consumer, topic, partition, kafka_offset, body, reason, parked_at"
                " FROM spine_parked WHERE advanced_at IS NULL AND (%s::text IS NULL OR consumer = %s)"
                " ORDER BY parked_id DESC LIMIT %s", (consumer, consumer, int(limit)))
    out = []
    for pid, cons, topic, partition, offset, body, reason, at in cur.fetchall():
        body = bytes(body or b"")
        topic, partition, offset = topic or "", partition or 0, offset or 0
        out.append({"parked_id": int(pid), "ref": parked_ref(pid), "consumer": cons, "topic": topic,
                    "partition": int(partition), "offset": int(offset), "reason": reason,
                    "parked_at": at.isoformat(), "bytes": len(body), "hash": body_hash(body),
                    "words": parked_words(cons, topic, partition, offset, reason)})
    return out


def parked_count(conn, consumer: str) -> int:
    """How many parked events a consumer still holds at (the watchable `parked`)."""
    cur = conn.cursor()
    cur.execute("SELECT count(*) FROM spine_parked WHERE consumer = %s AND advanced_at IS NULL",
                (consumer,))
    return int(cur.fetchone()[0])


def _hold(conn, cons, msg, consumer_name: str, reason: str, stop) -> bool:
    """The park and the hold: parked once with its evidence, then standing at it —
    never committing past — until a person's word advances it (True: the offset
    is committed, the loop goes on) or the consumer stops (False: uncommitted, so
    a relit consumer re-reads the same poison, finds its row, and holds again)."""
    pid, _fresh = park(conn, consumer_name, msg, reason)
    print(f"  [kernel] {parked_words(consumer_name, msg.topic(), msg.partition(), msg.offset(), reason[:500])}"
          f" (parked:{pid})", flush=True)
    while not stop.is_set():
        if advanced(conn, pid):
            cons.commit(message=msg)
            print(f"  [kernel] advanced past parked:{pid} on a person's word — the consumer goes on", flush=True)
            return True
        time.sleep(HOLD_POLL_S)
    return False


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
            except Exception as e:                       # noqa: BLE001 — the poison's words are the evidence
                _hold(conn, cons, msg, consumer_name,     # re-base sp1: parked, and the rail HOLDS
                      f"undecodable body: {type(e).__name__}: {e}", stop)
                continue
            if skip is not None and skip(env):
                cons.commit(message=msg)  # not ours: advance, no inbox work
                continue
            try:
                inbox.apply_event(conn, consumer_name, env,
                                  lambda cur, _e=env: apply(cur, _e))
            except POISON as e:                           # the fact's own refusal: poison, parked, held
                _hold(conn, cons, msg, consumer_name, f"could not apply: {type(e).__name__}: {e}", stop)
                continue
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
            except Exception as e:                       # noqa: BLE001 — the poison's words are the evidence
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
