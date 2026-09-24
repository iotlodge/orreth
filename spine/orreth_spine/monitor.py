# PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P4 sp4, the Monitoring workspace · 2026-09-18
# Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P6 cure sp1 (kernel), walk #7's W14 · 2026-09-21
# Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P6 cure sp3 (the re-walk's wounds): W22 an offer is a proposal · 2026-09-21
# Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P6.5 sp3, the farm's metrics: the Monitoring grows with the Stable · 2026-09-24
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
import re
import secrets

from . import envelope as ev, outbox, presence
from .rails import RABBIT_URL

WATCH_TURNED = "orreth.watch.turned.v1"     # a watch changed state: red ↔ green

METRICS = ("outbox_pending", "oldest_outbox_age_s", "asks_received",
           "bodies_alive", "bodies_dormant",
           # P6.5 sp3: the farm's metrics — the Monitoring grows with the Stable
           "minds_standing", "minds_unhealthy", "usd_today", "route_failures_1h", "meter_rate_10m",
           "bodies_drained")
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


OFFER_RE = re.compile(r"\bpropos(?:e|ing)\b[^.\n]{0,80}?\bwatch\b", re.I)
COND_RE = re.compile(r"`?\s*\b([a-z_]+)\s*(>=|<=|==|!=|>|<)\s*(-?\d+(?:\.\d+)?)\b\s*`?", re.I)
PROPOSE_BARE = "propose the watch you described — call add-watch with its name, metric, op and threshold"


def offer_in(reply: str | None) -> dict | None:
    """Walk #7's friction, walk #8's cure (W22): the monitor's OFFER, read
    honestly from its words. A reply that offers to propose a watch yields
    {words, ask} — the glass draws one click, "propose it", that sends
    `ask`; the interlock then arrives. The condition (`bodies_dormant > 0`)
    is read with or without backticks — W22: the button never depended on
    the mind's typography. An offer that names no condition still draws
    the button: `words` is None and the ask tells the monitor to propose
    the watch it described through the add-watch tool. No offer: None —
    a bare condition in a sentence is a reading, not an offer."""
    if not reply or not OFFER_RE.search(reply):
        return None
    m = COND_RE.search(reply)
    if not m or m.group(1).lower() not in METRICS:
        return {"words": None, "ask": PROPOSE_BARE}
    words = f"{m.group(1).lower()} {m.group(2)} {m.group(3)}"
    return {"words": words, "ask": f"propose a watch that {words}"}


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


def _farm(conn) -> dict:
    """P6.5 sp3: the Stable's numbers off the ground — minds standing and
    unhealthy, dollars today, route failures in the last hour, the
    meter's rate over ten minutes, bodies out of fuel."""
    out = {"minds_standing": 0, "minds_unhealthy": 0, "usd_today": 0.0, "route_failures_1h": 0,
           "meter_rate_10m": 0.0, "bodies_drained": 0}
    cur = conn.cursor()
    if _has_table(conn, "spine_services"):
        cur.execute("SELECT count(*) FILTER (WHERE state IN ('registered','versioned','healthy')),"
                    " count(*) FILTER (WHERE state = 'unhealthy') FROM spine_services WHERE scope = %s AND kind = 'mind'",
                    (ev.scope(),))
        r = cur.fetchone(); out["minds_standing"], out["minds_unhealthy"] = int(r[0]), int(r[1])
    if _has_table(conn, "spine_meter"):
        cur.execute("SELECT coalesce(sum(usd) FILTER (WHERE at >= date_trunc('day', now())), 0),"
                    " count(*) FILTER (WHERE ok = false AND at >= now() - interval '1 hour'),"
                    " count(*) FILTER (WHERE at >= now() - interval '10 minutes') FROM spine_meter")
        r = cur.fetchone()
        out["usd_today"] = round(float(r[0]), 6); out["route_failures_1h"] = int(r[1])
        out["meter_rate_10m"] = round(int(r[2]) / 10.0, 2)
    if _has_table(conn, "spine_mind_keys"):
        cur.execute("SELECT count(*) FROM spine_mind_keys WHERE scope = %s AND drained_at IS NOT NULL", (ev.scope(),))
        out["bodies_drained"] = int(cur.fetchone()[0])
    return out


def _stable(conn) -> dict:
    """The Stable's face: each mind's words and spend, the assignments."""
    if not _has_table(conn, "spine_services"):
        return {"minds": [], "assignments": []}
    from . import stable
    try:
        minds = [{"name": s["name"], "state": s["state"], "words": stable.stall_words(s),
                  "spend": s.get("spend"), "last": (s.get("last_health") or {}).get("detail")}
                 for s in stable.stalls(conn)]
        return {"minds": minds, "assignments": stable.assignments(conn)}
    except Exception as e:                            # noqa: BLE001 — the face never breaks the snapshot
        return {"minds": [], "assignments": [], "error": f"{type(e).__name__}: {e}"}


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
    values.update(_farm(conn))
    stable_view = _stable(conn)
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
        "stable": stable_view,                        # P6.5 sp3: the farm's face in the Monitoring
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
