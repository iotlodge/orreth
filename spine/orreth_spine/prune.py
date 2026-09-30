# PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch row 4, the perf cure before sp2 (JB's word 2026-09-29): the brokers' TEST RESIDUE pruned · 2026-09-29
# Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch row 4, the honest glass sp2: THE GROUND'S PRUNE — every row whose world is test-shaped, across every table with a scope column (`ground` · `scope`) · 2026-09-29
"""The brokers' housekeeping (the perf cure, 2026-09-29): every test session and every proof
names its own namespace (`t<6 hex>`, `a…` · `b…` · `p…` for the cells' and the poison's
proofs) and the brokers keep every topic, queue and consumer group it made — found live: a
dev broker holding 5,288 topics, 2,687 groups and 2,336 queues after six days, a fresh client's
metadata fetch at 400–700 ms, the broker at 90–200 % CPU with two live consumers.

Three prunes, each honest about what it touches:
- `namespace(ns)` — ONE session's residue: its topics (`….<ns>`), its queues (`….<ns>.…`),
  and every EMPTY consumer group wearing a test prefix (a live kernel's groups are Stable and
  never touched). The suite calls it at its end.
- `residue()` — every namespace that LOOKS like a test's (a letter and six hex digits), the
  test-only topics (`orreth.test-…` · `orreth.shadow-…` · `orreth.test.cap.…`), and the empty
  test-prefixed groups. The rig's `scripts/dev.sh prune` verb.
- Nothing here touches a namespace a person named (`two`, `perf`, the dev world's bare topics).

THE GROUND'S PRUNE (the honest glass sp2, 2026-09-29): the same residue on the GROUND — every
test session and every proof names its world `u:<word>-<6 hex>` (`u:test-t1a2b3c` · `u:loops-…` ·
`u:doors-…` · `u:law-…`), and the ground kept every row it wrote (found live: 388 test worlds; the
dev world's WATCHES card counted twenty-three watch rows in dead proof scopes it could never rest).
- `scope(conn, world)` — ONE world's rows, across every table with a `scope` column and the
  three child tables that hang off one (`spine_intent_turns` · `spine_occurrences` ·
  `spine_proof_attempts`, by their parent). A proof calls it for its own world at its end.
- `ground(conn)` — every world whose name is test-shaped. The suite's teardown and the rig's
  `scripts/dev.sh prune` call it. A world a person named (`u:dev`, `u:acme`) is never touched:
  the shape is the law, not a list.
"""
from __future__ import annotations

import os
import re
import sys

NS_RE = re.compile(r"^[a-z][0-9a-f]{6}$")                      # a test session's namespace
SCOPE_RE = r"^u:[a-z]+-[0-9a-f]{6}$"                             # a test session's or a proof's WORLD (Postgres regex)
CHILDREN = (                                                    # tables without a scope, hung off a parent that has one
    ("spine_intent_turns", "intention_id", "spine_intentions", "intention_id"),
    ("spine_occurrences", "schedule_id", "spine_schedules", "schedule_id"),
    ("spine_proof_attempts", "ask_id", "spine_asks", "ask_id"),
)
TOPIC_RESIDUE_RE = re.compile(r"^orreth\.(test-|shadow-|test\.cap\.)")
GROUP_PREFIXES = ("glass-dispatcher-", "glass-feed-", "g-", "td-", "shadow-", "probe-", "monitor-")


def _kafka():
    from confluent_kafka.admin import AdminClient
    from .projector import KAFKA_BOOTSTRAP
    return AdminClient({"bootstrap.servers": KAFKA_BOOTSTRAP})


def _rabbit_api() -> tuple[str, tuple[str, str]]:
    from .rails import RABBIT_URL
    from urllib.parse import urlparse
    u = urlparse(RABBIT_URL)
    return f"http://{u.hostname or 'localhost'}:15672", (u.username or "guest", u.password or "guest")


def _topic_ns(topic: str) -> str | None:
    """The namespace a topic wears — the last segment after `.v<N>.`, else None (a bare topic)."""
    m = re.search(r"\.v\d+\.([^.]+)$", topic)
    return m.group(1) if m else None


def _delete_topics(admin, names: list[str]) -> int:
    if not names:
        return 0
    done = 0
    for i in range(0, len(names), 200):                            # the broker takes a batch at a time
        for _t, f in admin.delete_topics(names[i:i + 200], operation_timeout=30).items():
            try:
                f.result(); done += 1
            except Exception:                                      # noqa: BLE001 — a topic already gone is not a wound
                pass
    return done


def _empty_test_groups(admin) -> list[str]:
    from confluent_kafka import ConsumerGroupState
    try:
        listing = admin.list_consumer_groups(states={ConsumerGroupState.EMPTY}, request_timeout=30).result()
    except Exception:                                              # noqa: BLE001 — an old broker: nothing pruned
        return []
    return [g.group_id for g in listing.valid if g.group_id.startswith(GROUP_PREFIXES)]


def _delete_groups(admin, names: list[str]) -> int:
    if not names:
        return 0
    done = 0
    for i in range(0, len(names), 100):
        for _g, f in admin.delete_consumer_groups(names[i:i + 100], request_timeout=30).items():
            try:
                f.result(); done += 1
            except Exception:                                      # noqa: BLE001
                pass
    return done


def _delete_queues(match) -> int:
    import json
    import urllib.request
    base, (user, pw) = _rabbit_api()
    mgr = urllib.request.build_opener(urllib.request.HTTPBasicAuthHandler(_pw(base, user, pw)))
    try:
        with mgr.open(base + "/api/queues?columns=name,vhost", timeout=30) as r:
            queues = json.loads(r.read())
    except Exception:                                              # noqa: BLE001 — no management plane: nothing pruned
        return 0
    from urllib.parse import quote
    done = 0
    for q in queues:
        if not match(q["name"]):
            continue
        req = urllib.request.Request(f"{base}/api/queues/{quote(q['vhost'], safe='')}/{quote(q['name'], safe='')}", method="DELETE")
        try:
            mgr.open(req, timeout=30); done += 1
        except Exception:                                          # noqa: BLE001
            pass
    return done


def _pw(base, user, pw):
    import urllib.request
    m = urllib.request.HTTPPasswordMgrWithDefaultRealm(); m.add_password(None, base, user, pw); return m


def _scoped_tables(conn) -> list[str]:
    """Every spine table on this ground with a `scope` column — read from the catalogue,
    so a table born after this file is pruned too."""
    cur = conn.cursor()
    cur.execute("SELECT table_name FROM information_schema.columns WHERE table_schema = current_schema()"
                " AND column_name = 'scope' AND table_name LIKE 'spine\\_%' ORDER BY 1")
    return [r[0] for r in cur.fetchall()]


def _prune_where(conn, where: str, params: tuple) -> dict:
    out: dict = {}
    with conn.transaction():
        cur = conn.cursor()
        for child, key, parent, pkey in CHILDREN:
            cur.execute("SELECT to_regclass(%s) IS NOT NULL AND to_regclass(%s) IS NOT NULL", (child, parent))
            if not cur.fetchone()[0]:
                continue
            cur.execute(f"DELETE FROM {child} WHERE {key} IN (SELECT {pkey} FROM {parent} WHERE {where})", params)
            if cur.rowcount:
                out[child] = cur.rowcount
        for t in _scoped_tables(conn):
            cur.execute(f"DELETE FROM {t} WHERE {where}", params)
            if cur.rowcount:
                out[t] = cur.rowcount
    return out


def scope(conn, world: str) -> dict:
    """ONE world's rows, gone — every table with a scope column, the children by their
    parent. `{table: rows}` for what was touched."""
    return _prune_where(conn, "scope = %s", (world,))


def ground(conn=None) -> dict:
    """Every TEST-SHAPED world's rows (`u:<word>-<6 hex>`), gone. A person's world is
    never touched. `{table: rows}` for what was touched, plus `worlds` counted first."""
    if conn is None:
        import psycopg
        from .rails import PG_DSN
        with psycopg.connect(PG_DSN, autocommit=True) as c:
            return ground(c)
    cur = conn.cursor()
    worlds = 0
    for t in _scoped_tables(conn):
        cur.execute(f"SELECT count(DISTINCT scope) FROM {t} WHERE scope ~ %s", (SCOPE_RE,))
        worlds = max(worlds, int(cur.fetchone()[0]))
    out = {"worlds": worlds}
    out.update(_prune_where(conn, "scope ~ %s", (SCOPE_RE,)))
    return out


def namespace(ns: str) -> dict:
    """ONE session's residue: its topics, its queues, the empty test-prefixed groups."""
    admin = _kafka()
    topics = [t for t in admin.list_topics(timeout=30).topics if _topic_ns(t) == ns]
    out = {"topics": _delete_topics(admin, topics), "groups": _delete_groups(admin, _empty_test_groups(admin)),
           "queues": _delete_queues(lambda q: f".{ns}." in q or q.endswith(f".{ns}"))}
    return out


def residue() -> dict:
    """Every test-shaped namespace's residue, the test-only bare topics — and (sp2) every
    test-shaped world's rows on the ground."""
    admin = _kafka()
    all_topics = list(admin.list_topics(timeout=60).topics)
    topics = [t for t in all_topics if (lambda ns: ns is not None and NS_RE.match(ns))(_topic_ns(t)) or TOPIC_RESIDUE_RE.match(t)]
    out = {"topics": _delete_topics(admin, topics), "topics_kept": len(all_topics) - len(topics),
           "groups": _delete_groups(admin, _empty_test_groups(admin)),
           "queues": _delete_queues(lambda q: re.search(r"[.-][a-z][0-9a-f]{6}(?:[.-]|$)", q) is not None)}
    try:
        g = ground()
        out["ground_worlds"] = g.pop("worlds", 0)
        out["ground_rows"] = sum(g.values())
    except Exception as e:                                         # noqa: BLE001 — a dark ground prunes nothing, said
        out["ground_error"] = type(e).__name__
    return out


def main() -> int:
    ns = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("SPINE_QUEUE_NS")
    out = namespace(ns) if ns and NS_RE.match(ns) else residue()
    print("· pruned " + " · ".join(f"{v} {k.replace('_', ' ')}" for k, v in out.items()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
