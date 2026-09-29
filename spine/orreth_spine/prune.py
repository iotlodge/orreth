# PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch row 4, the perf cure before sp2 (JB's word 2026-09-29): the brokers' TEST RESIDUE pruned · 2026-09-29
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
"""
from __future__ import annotations

import os
import re
import sys

NS_RE = re.compile(r"^[a-z][0-9a-f]{6}$")                      # a test session's namespace
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


def namespace(ns: str) -> dict:
    """ONE session's residue: its topics, its queues, the empty test-prefixed groups."""
    admin = _kafka()
    topics = [t for t in admin.list_topics(timeout=30).topics if _topic_ns(t) == ns]
    out = {"topics": _delete_topics(admin, topics), "groups": _delete_groups(admin, _empty_test_groups(admin)),
           "queues": _delete_queues(lambda q: f".{ns}." in q or q.endswith(f".{ns}"))}
    return out


def residue() -> dict:
    """Every test-shaped namespace's residue, and the test-only bare topics."""
    admin = _kafka()
    all_topics = list(admin.list_topics(timeout=60).topics)
    topics = [t for t in all_topics if (lambda ns: ns is not None and NS_RE.match(ns))(_topic_ns(t)) or TOPIC_RESIDUE_RE.match(t)]
    out = {"topics": _delete_topics(admin, topics), "topics_kept": len(all_topics) - len(topics),
           "groups": _delete_groups(admin, _empty_test_groups(admin)),
           "queues": _delete_queues(lambda q: re.search(r"[.-][a-z][0-9a-f]{6}(?:[.-]|$)", q) is not None)}
    return out


def main() -> int:
    ns = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("SPINE_QUEUE_NS")
    out = namespace(ns) if ns and NS_RE.match(ns) else residue()
    print("· pruned " + " · ".join(f"{v} {k.replace('_', ' ')}" for k, v in out.items()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
