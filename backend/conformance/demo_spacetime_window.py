"""The spacetime window's time axis, across processes: two orrethd daemons form a tree.

Recent memory is cheap and local (the field); deep time lives at the apex (the universe).
One query at the field scrubs 300 days: the field serves what it has and delegates the
deeper remainder UP over the wire — one merged, ordered, Sourced + Verified answer.

    uv run python demo_spacetime_window.py [field_port] [universe_port]
"""
from __future__ import annotations

import json
import sys
import urllib.request
from datetime import datetime, timedelta, timezone

from orreth_sim import crypto
from orreth_sim.identity import Becky, Nanda
from orreth_sim.node import make_memory
from smoke_orrethd import root_keypair

FIELD = f"http://127.0.0.1:{sys.argv[1] if len(sys.argv) > 1 else 4400}"
UNIVERSE = f"http://127.0.0.1:{sys.argv[2] if len(sys.argv) > 2 else 4500}"
WINDOW_DAYS = int(sys.argv[3]) if len(sys.argv) > 3 else 300   # >395 exercises a 3-tier hop
OLD_DAYS = int(sys.argv[4]) if len(sys.argv) > 4 else 200
SCOPE = "u:demo/e:cloud/f:prod"


def call(base: str, method: str, path: str, payload: dict | None = None):
    req = urllib.request.Request(base + path, method=method,
                                 data=json.dumps(payload).encode() if payload else None,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())


def days_ago(n: int) -> str:
    return (datetime.now(timezone.utc) - timedelta(days=n)).strftime("%Y-%m-%dT%H:%M:%SZ")


def main() -> None:
    kp = crypto.KeyPair()
    agent = {"did": crypto.did_key_for(kp.public), "scope": SCOPE}

    # the child pulled the apex floor at boot — flow 1, over the wire
    std = call(FIELD, "GET", "/standards")
    print(f"field's floors (pulled from the apex at boot): "
          f"{[f['reason'][:28] for f in std['floors']]}")

    # deep time lives at the apex: a 200-day-old memory, long since risen to the universe
    old = make_memory(agent, kp, SCOPE, {"season": "the championship, long ago"},
                      occurred_at=days_ago(OLD_DAYS))
    call(UNIVERSE, "POST", "/records", old)
    # recent memory is cheap and local: yesterday, at the field
    new = make_memory(agent, kp, SCOPE, {"game": "yesterday's win"}, occurred_at=days_ago(1))
    call(FIELD, "POST", "/records", new)
    print("wrote: deep memory at the UNIVERSE, recent memory at the FIELD")

    # one token, chained from the pinned root, audience = the whole universe
    nanda = Nanda()
    root = Becky("u:demo", nanda, universe_name="demo", kp=root_keypair())
    token = root.issue_token(agent["did"], "u:demo",
                             [{"action": "retrieve", "space": "self"}])

    # one question at the FIELD, scrubbing 300 days back
    res = call(FIELD, "POST", "/retrieve", {
        "query": {"requester": agent["did"], "subject": "self", "space": "self",
                  "time": {"from": days_ago(WINDOW_DAYS)}, "intent": "recall",
                  "budget": {"cost": 3}, "auth": "biscuit-sim"},
        "token": token, "requester_scope": SCOPE})

    print(f"\none query at the field, window = {WINDOW_DAYS} days:")
    print(f"  served_by: {res['provenance']['served_by']}   (every tier the remainder crossed — over the wire)")
    for h in res["hits"]:
        print(f"  {h['occurred_at']}  {h['fidelity']:>8}  {h['ref'][:18]}…")
    print(f"  verification: {res['verification']}  ·  hits newest-first across two processes")
    assert [h["ref"] for h in res["hits"]] == [new["id"], old["id"]]
    assert len(res["provenance"]["served_by"]) >= 2

    print(f"\nthe window scrubbed {WINDOW_DAYS} days across "
          f"{len(res['provenance']['served_by'])} daemons — "
          "recent stayed local, deep time answered from the apex. 🥂")


if __name__ == "__main__":
    main()
