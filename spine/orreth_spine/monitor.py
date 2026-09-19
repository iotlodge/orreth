# PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P4 sp4, the Monitoring workspace · 2026-09-18
"""The Monitoring workspace's ground (canon 0001: "if it's monitoring, it
goes here"): the live snapshot of the Operating State — rails, benches,
bodies, asks, the last harness run — and the WATCHES: named checks the
human (or the monitor agent, through the interlock) adds; each is
evaluated against the snapshot, honestly green or red."""
from __future__ import annotations

import json
import secrets

from . import envelope as ev, outbox, presence
from .rails import RABBIT_URL

METRICS = ("outbox_pending", "oldest_outbox_age_s", "asks_received",
           "bodies_alive", "bodies_dormant")
OPS = {"<=": lambda v, t: v <= t, ">=": lambda v, t: v >= t,
       "<": lambda v, t: v < t, ">": lambda v, t: v > t, "==": lambda v, t: v == t}


def ensure_schema(conn) -> None:
    from .outbox import once
    if not once(conn, "monitor"):
        return
    with conn.transaction():
        cur = conn.cursor()
        cur.execute("SELECT pg_advisory_xact_lock(742199)")  # DDL race guard
        cur.execute(
            "CREATE TABLE IF NOT EXISTS spine_watches ("
            " watch_id text PRIMARY KEY, name text NOT NULL, metric text NOT NULL,"
            " op text NOT NULL, threshold double precision NOT NULL,"
            " added_by text NOT NULL, scope text NOT NULL,"
            " added_at timestamptz NOT NULL DEFAULT now())")


def add_watch(conn, name: str, metric: str, op: str, threshold: float,
              by: str) -> str:
    """A new watch on the ground — the act the interlock guards."""
    if metric not in METRICS:
        raise ValueError(f"no metric named {metric!r}; the metrics are "
                         + ", ".join(METRICS))
    if op not in OPS:
        raise ValueError(f"the op is one of {', '.join(OPS)}")
    ensure_schema(conn)
    wid = "watch_" + secrets.token_hex(5)
    with conn.transaction():
        conn.cursor().execute(
            "INSERT INTO spine_watches (watch_id, name, metric, op, threshold,"
            " added_by, scope) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (wid, name, metric, op, float(threshold), by, ev.scope()))
    return wid


def _benches(names: list[str]) -> dict:
    try:
        import pika
        from .resident import serve_queue
        rc = pika.BlockingConnection(pika.URLParameters(RABBIT_URL))
        ch = rc.channel()
        out = {}
        for q in [serve_queue()] + [serve_queue(n) for n in names]:
            try:
                out[q] = ch.queue_declare(q, durable=True, passive=True).method.message_count
            except Exception:
                ch = rc.channel()          # a passive miss closes the channel
                out[q] = None
        rc.close()
        return out
    except Exception as e:
        return {"error": type(e).__name__}


def _topic_depth() -> int | None:
    try:
        from confluent_kafka import Consumer, TopicPartition
        from .projector import KAFKA_BOOTSTRAP
        from .resident import ASK_RECEIVED
        c = Consumer({"bootstrap.servers": KAFKA_BOOTSTRAP,
                      "group.id": "monitor-" + secrets.token_hex(3)})
        lo, hi = c.get_watermark_offsets(TopicPartition(ASK_RECEIVED, 0), timeout=3)
        c.close()
        return hi - lo
    except Exception:
        return None


def snapshot(conn, *, rails: bool = True) -> dict:
    """The Operating State, live, for this world."""
    from .resident import ensure_schema as _ground   # lazily: no import cycle
    _ground(conn)
    ensure_schema(conn)
    outbox.ensure_schema(conn)
    cur = conn.cursor()
    cur.execute("SELECT status, count(*) FROM spine_asks WHERE scope = %s"
                " GROUP BY status", (ev.scope(),))
    asks = {s: int(n) for s, n in cur.fetchall()}
    bodies = presence.roster(conn)
    alive = [b for b in bodies if b["alive"]]
    lag = outbox.outbox_lag(conn)
    cur.execute("SELECT template, version, passed, failed, ran_at FROM spine_harness_runs"
                " WHERE scope = %s ORDER BY ran_at DESC LIMIT 1", (ev.scope(),)) \
        if _has_table(conn, "spine_harness_runs") else None
    last = cur.fetchone() if _has_table(conn, "spine_harness_runs") else None
    values = {
        "outbox_pending": int(lag["pending"]),
        "oldest_outbox_age_s": float(lag["oldest_age_s"] or 0.0),
        "asks_received": asks.get("received", 0),
        "bodies_alive": len(alive),
        "bodies_dormant": len(bodies) - len(alive),
    }
    cur.execute("SELECT watch_id, name, metric, op, threshold, added_by FROM spine_watches"
                " WHERE scope = %s ORDER BY added_at", (ev.scope(),))
    watches = [{"watch_id": w[0], "name": w[1], "metric": w[2], "op": w[3],
                "threshold": w[4], "added_by": w[5], "value": values[w[2]],
                "ok": OPS[w[3]](values[w[2]], w[4])} for w in cur.fetchall()]
    return {
        "world": ev.scope(),
        "outbox": lag,
        "asks": asks,
        "bodies": bodies,
        "values": values,
        "watches": watches,
        "benches": _benches([b["name"] for b in bodies]) if rails else {},
        "topic_depth": _topic_depth() if rails else None,
        "harness": ({"template": last[0], "version": last[1], "passed": last[2],
                     "failed": last[3], "ran_at": last[4].isoformat()} if last else None),
    }


def _has_table(conn, name: str) -> bool:
    cur = conn.cursor()
    cur.execute("SELECT to_regclass(%s) IS NOT NULL", (name,))
    return bool(cur.fetchone()[0])
