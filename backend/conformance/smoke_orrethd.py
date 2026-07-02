"""Cross-language smoke: Python cognition signs; the Rust plane verifies over the wire.

Start the daemon, then run this from backend/conformance:
    (backend/plane)        cargo run -p orrethd -- --profile profiles/demo-field.json --store-dir /tmp/orreth-bodies
    (backend/conformance)  uv run python smoke_orrethd.py [port]
"""
from __future__ import annotations

import json
import sys
import urllib.request
from urllib.error import HTTPError

from orreth_sim import crypto
from orreth_sim.node import make_memory

BASE = f"http://127.0.0.1:{sys.argv[1] if len(sys.argv) > 1 else 4400}"
SCOPE = "u:demo/e:cloud/f:prod"


def call(method: str, path: str, payload: dict | None = None):
    req = urllib.request.Request(BASE + path, method=method,
                                 data=json.dumps(payload).encode() if payload else None,
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as r:
            body = r.read()
            return r.status, json.loads(body) if body[:1] in (b"{", b"[") else body
    except HTTPError as e:
        body = e.read()
        return e.code, json.loads(body) if body[:1] in (b"{", b"[") else body


def main() -> None:
    kp = crypto.KeyPair()
    agent = {"did": crypto.did_key_for(kp.public), "scope": SCOPE}
    print(f"agent (Python-side, did:key): {agent['did'][:40]}…")

    ok = make_memory(agent, kp, SCOPE, {"game": "opening day"}, occurred_at="2026-07-02T18:00:00Z")
    status, res = call("POST", "/records", ok)
    print(f"signed record            → {status} {res}")
    assert status == 201

    back = make_memory(agent, kp, SCOPE, {"forged": "past"}, occurred_at="2026-07-01T00:00:00Z")
    status, res = call("POST", "/records", back)
    print(f"backdated lived record   → {status} {res['error']}")
    assert status == 409

    tampered = make_memory(agent, kp, SCOPE, {"n": 1}, occurred_at="2026-07-02T19:00:00Z")
    tampered["kind"] = "procedural"  # kind is signed — this breaks the signature
    status, res = call("POST", "/records", tampered)
    print(f"tampered record          → {status} {res['error']}")
    assert status == 403

    status, body = call("GET", f"/records/{ok['id']}/body")
    print(f"body (verified by hash)  → {status} {body}")
    assert status == 200 and body == {"game": "opening day"}

    # a self-issued did:key token (v0: the daemon pins no root yet — that lands with the join flow)
    issuer = crypto.KeyPair()
    issuer_did = crypto.did_key_for(issuer.public)
    cert = {"issuer": issuer_did, "subject": agent["did"], "audience": SCOPE,
            "grants": [{"action": "retrieve", "space": "self"}]}
    cert["sig"] = issuer.sign(issuer_did, cert)
    token = {"subject": agent["did"], "audience": SCOPE, "grants": cert["grants"],
             "constraints": {"expiry": "2027-01-01T00:00:00Z", "direction": "within"},
             "chain": [json.dumps(cert, sort_keys=True)],
             "sig": issuer.sign(issuer_did, {"subject": agent["did"]})}
    query = {"requester": agent["did"], "subject": "self", "space": "self",
             "time": {"from": "2026-07-01T00:00:00Z"}, "intent": "recall",
             "budget": {"cost": 3}, "auth": "biscuit-sim"}
    status, res = call("POST", "/retrieve", {"query": query, "token": token,
                                             "requester_scope": SCOPE})
    print(f"retrieve under token     → {status} hits={[h['ref'][:16] + '…' for h in res['hits']]} "
          f"verification={res['verification']}")
    assert status == 200 and len(res["hits"]) == 1

    bad_token = dict(token, grants=[{"action": "write", "space": "self"}])
    status, res = call("POST", "/retrieve", {"query": query, "token": bad_token,
                                             "requester_scope": SCOPE})
    print(f"no retrieve grant        → {status} {res['error']}")
    assert status == 403

    print("\nsmoke: Python signed, Rust verified — the two halves met on the wire. 🥃")


if __name__ == "__main__":
    main()
