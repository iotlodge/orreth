# PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P4 sp4, the Monitoring workspace · 2026-09-18
# Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P6 cure sp1 (kernel), walk #7's W14 · 2026-09-21
"""The Monitoring workspace's ground (canon 0001: "if it's monitoring, it
goes here"): the live snapshot of the Operating State — rails, benches,
bodies, asks, the last harness run — and the WATCHES: named checks the
human (or the monitor agent, through the interlock) adds; each is
evaluated against the snapshot, honestly green or red.

The sense of a watch (walk #7, W14): a watch names what it watches FOR —
its condition is the ALERT, red WHEN `metric op threshold` holds and
green otherwise (`bodies_dormant > 0` is red the moment a body is
dormant). This is how every human and every mind in the walk read a
watch; the kernel had judged the opposite (green while the condition
held), so a board of alerts stood red at value 0. The state is a pure
function of the metric NOW, judged on every beat; red → green and green
→ red are recorded TRANSITIONS — a fact on the rail with `since` — and
the intent loop wakes on the red transition alone, never on a standing
red."""
from __future__ import annotations

import json
import secrets

from . import envelope as ev, outbox, presence
from .rails import RABBIT_URL

WATCH_TURNED = "orreth.watch.turned.v1"     # a watch changed state: red ↔ green

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
        cur.execute("ALTER TABLE spine_watches ADD COLUMN IF NOT EXISTS"
                    " last_ok boolean")     # 0007: the intent rail sees a watch TURN red
        cur.execute("ALTER TABLE spine_watches ADD COLUMN IF NOT EXISTS"
                    " since timestamptz")   # W14: when the state last turned


def judge_one(op: str, value, threshold) -> bool:
    """The sense of a watch, in one place (conformance `watch_judge`):
    True = RED — the watched condition holds now."""
    return bool(OPS[op](value, threshold))


def reads(w: dict) -> str:
    """The watch in a human's sentence — the sense spelled out, never
    left to a bare `> 0`: 'red when bodies_dormant > 0.0 · now 0 → green'."""
    return (f"red when {w['metric']} {w['op']} {w['threshold']} · now {w['value']} → "
            f"{'RED' if w['red'] else 'green'}")


def add_watch(conn, name: str, metric: str, op: str, threshold: float,
              by: str) -> str:
    """A new watch on the ground — the act the interlock guards. The
    condition is what the watch catches: red WHEN it holds."""
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
    cur.execute("SELECT watch_id, name, metric, op, threshold, added_by, last_ok, since"
                " FROM spine_watches WHERE scope = %s ORDER BY added_at", (ev.scope(),))
    watches = []
    for w in cur.fetchall():
        red = judge_one(w[3], values[w[2]], w[4])
        # `since`: when the RECORDED state last turned (judge() writes it) —
        # shown only while the record agrees with the metric now; a watch
        # that flipped since the last beat says since = None until judged
        recorded_red = None if w[6] is None else (not w[6])
        d = {"watch_id": w[0], "name": w[1], "metric": w[2], "op": w[3],
             "threshold": w[4], "added_by": w[5], "value": values[w[2]],
             "red": red, "ok": not red, "state": "red" if red else "green",
             "since": w[7].isoformat() if w[7] is not None and recorded_red == red else None}
        d["reads"] = reads(d)
        watches.append(d)
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


def judge(conn) -> list[dict]:
    """Every watch judged against its metric NOW; the ones whose state
    CHANGED are recorded — `last_ok` and `since` on the row, and a
    `orreth.watch.turned.v1` fact through the outbox — and returned, each
    with `to` ('red' | 'green') and `from` ('red' | 'green' | None when
    first judged). A standing red records nothing and returns nothing;
    a watch first judged red is a red transition (born red is news)."""
    snap = snapshot(conn, rails=False)
    turned = []
    for w in snap["watches"]:
        cur = conn.cursor()
        cur.execute("SELECT last_ok FROM spine_watches WHERE watch_id = %s", (w["watch_id"],))
        row = cur.fetchone()
        was_ok = row[0] if row else None
        if was_ok is not None and bool(was_ok) == bool(w["ok"]):
            continue                                       # standing: nothing turned
        if was_ok is None and w["ok"]:
            with conn.transaction():                       # first judged green: recorded, no turn
                conn.cursor().execute(
                    "UPDATE spine_watches SET last_ok = true, since = clock_timestamp()"
                    " WHERE watch_id = %s", (w["watch_id"],))
            continue
        frm = None if was_ok is None else ("green" if was_ok else "red")
        to = w["state"]
        e = ev.make_envelope(
            kind="event", type=WATCH_TURNED, universe_id=ev.scope(), scope_path=ev.scope(),
            payload={"ref": w["watch_id"], "hash": ev.content_hash(w["name"]),
                     "name": w["name"], "metric": w["metric"], "op": w["op"],
                     "threshold": w["threshold"], "value": w["value"], "from": frm, "to": to},
            correlation_id=w["watch_id"], authority_chain=["the kernel"])

        def domain(cur, wid=w["watch_id"], ok=w["ok"]):
            cur.execute("UPDATE spine_watches SET last_ok = %s, since = clock_timestamp()"
                        " WHERE watch_id = %s RETURNING since", (bool(ok), wid))
            w["since"] = cur.fetchone()[0].isoformat()

        outbox.commit_with_outbox(conn, ev.encode(e), e["message_id"], domain)
        turned.append(dict(w, to=to, **{"from": frm}))
    return turned


def _has_table(conn, name: str) -> bool:
    cur = conn.cursor()
    cur.execute("SELECT to_regclass(%s) IS NOT NULL", (name,))
    return bool(cur.fetchone()[0])
