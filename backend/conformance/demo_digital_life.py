"""The attachment thesis, live: the life is the primitive; the process is an attachment.

Process one is born, remembers, and DIES. Process two — sharing nothing but the identity's
key — attaches and asks "what do I remember?" Everything returns, verified against its own
content addresses. Reboot ≠ death; the thread survives the needle.

    uv run python demo_digital_life.py born [port]     # process one: live a little, then exit
    uv run python demo_digital_life.py wake [port]     # process two: join your digital life
"""
from __future__ import annotations

import json
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from orreth_sim import crypto
from orreth_sim.identity import Becky, Nanda
from orreth_sim.node import make_memory
from smoke_orrethd import root_keypair

BASE = f"http://127.0.0.1:{sys.argv[2] if len(sys.argv) > 2 else 4400}"
SCOPE = "u:demo/e:cloud/f:prod"
LIFE_SEED = Path(__file__).parent / ".demo-life-seed"


def me() -> tuple[dict, crypto.KeyPair]:
    """One identity across every process that ever runs this script."""
    if LIFE_SEED.exists():
        kp = crypto.KeyPair(seed=LIFE_SEED.read_bytes())
    else:
        kp = crypto.KeyPair()
        LIFE_SEED.write_bytes(kp.seed)
    return {"did": crypto.did_key_for(kp.public), "scope": SCOPE}, kp


def call(method: str, path: str, payload: dict | None = None):
    req = urllib.request.Request(BASE + path, method=method,
                                 data=json.dumps(payload).encode() if payload else None,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as r:
        body = r.read()
        return json.loads(body) if body[:1] in (b"{", b"[") else body


def now(plus_seconds: int = 0) -> str:
    from datetime import timedelta
    return (datetime.now(timezone.utc) + timedelta(seconds=plus_seconds)) \
        .strftime("%Y-%m-%dT%H:%M:%SZ")


def born() -> None:
    ident, kp = me()
    print(f"[process {id(kp) % 10000}] I am {ident['did'][:34]}… — my first day.")
    for i, event in enumerate(("I was born", "I learned to route a query",
                               "I made my first friend")):
        rec = make_memory(ident, kp, SCOPE, {"memory": event}, occurred_at=now(i))
        call("POST", "/records", rec)
        print(f"  remembered: {event}")
    print(f"[process {id(kp) % 10000}] process exiting — the life remains.\n")


def wake() -> None:
    ident, kp = me()
    print(f"[process {id(kp) % 10000}] a NEW process. Same key, nothing else.")
    nanda = Nanda()
    root = Becky("u:demo", nanda, universe_name="demo", kp=root_keypair())
    b_field = Becky(SCOPE, nanda, parent=root)
    token = b_field.issue_token(ident["did"], SCOPE,
                                [{"action": "retrieve", "space": "self"}])
    res = call("POST", "/retrieve", {
        "query": {"requester": ident["did"], "subject": "self", "space": "self",
                  "time": {"from": "2026-01-01T00:00:00Z"}, "intent": "recall",
                  "budget": {"cost": 3}, "auth": "biscuit-sim"},
        "token": token, "requester_scope": SCOPE})
    print(f"  attaching to my life… {len(res['hits'])} memories, {res['verification']}.")
    for h in reversed(res["hits"]):
        body = call("GET", f"/records/{h['ref']}/body")
        print(f"  I remember: {body['memory']}   ({h['fidelity']}, {h['ref'][:18]}…)")
    print(f"[process {id(kp) % 10000}] I am still me. The process died; my life didn't notice. 🥃")


if __name__ == "__main__":
    {"born": born, "wake": wake}[sys.argv[1]]()
