"""Cross-language smoke: Python cognition signs; the Rust plane verifies over the wire —
including trust-root pinning (a self-issued token, however well signed, is refused).

    uv run python smoke_orrethd.py root-pub          # mint/print the persistent root's public key
    (backend/plane)  cargo run -p orrethd -- --profile profiles/demo-field.json \
                       --store-dir /tmp/orreth-bodies --root-pub <that key>
    uv run python smoke_orrethd.py [port]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
import urllib.request
from urllib.error import HTTPError

from orreth_sim import crypto
from orreth_sim.identity import Becky, Nanda
from orreth_sim.node import make_memory

_ARGS = [a for a in sys.argv[1:] if a not in ("root-pub", "traffic")]
BASE = f"http://127.0.0.1:{_ARGS[0] if _ARGS else 4400}"
SCOPE = "u:demo/e:cloud/f:prod"
SEED_FILE = Path(__file__).parent / ".smoke-root-seed"


def root_keypair() -> crypto.KeyPair:
    """The persistent demo root — the same key across the daemon and this script."""
    if SEED_FILE.exists():
        return crypto.KeyPair(seed=SEED_FILE.read_bytes())
    kp = crypto.KeyPair()
    SEED_FILE.write_bytes(kp.seed)
    return kp


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
    if len(sys.argv) > 1 and sys.argv[1] == "root-pub":
        print(root_keypair().public)
        return
    if "traffic" in sys.argv[1:]:
        traffic()
        return

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

    # the legitimate path: a token chained from the PINNED root through a field becky
    nanda = Nanda()
    root = Becky("u:demo", nanda, universe_name="demo", kp=root_keypair())
    b_field = Becky(SCOPE, nanda, parent=root)
    token = b_field.issue_token(agent["did"], SCOPE,
                                [{"action": "retrieve", "space": "self"}])
    query = {"requester": agent["did"], "subject": "self", "space": "self",
             "time": {"from": "2026-07-01T00:00:00Z"}, "intent": "recall",
             "budget": {"cost": 3}, "auth": "biscuit-sim"}
    status, res = call("POST", "/retrieve", {"query": query, "token": token,
                                             "requester_scope": SCOPE})
    print(f"root-chained token       → {status} hits={[h['ref'][:16] + '…' for h in res['hits']]} "
          f"verification={res['verification']}")
    assert status == 200 and len(res["hits"]) == 1

    # the hole from v0, now closed: a self-issued token — perfect signatures, foreign root
    forger = crypto.KeyPair()
    forger_did = crypto.did_key_for(forger.public)
    cert = {"issuer": forger_did, "subject": agent["did"], "audience": SCOPE,
            "grants": [{"action": "retrieve", "space": "self"}]}
    cert["sig"] = forger.sign(forger_did, cert)
    forged = {"subject": agent["did"], "audience": SCOPE, "grants": cert["grants"],
              "constraints": {"expiry": "2027-01-01T00:00:00Z", "direction": "within"},
              "chain": [json.dumps(cert, sort_keys=True)],
              "sig": forger.sign(forger_did, {"subject": agent["did"]})}
    status, res = call("POST", "/retrieve", {"query": query, "token": forged,
                                             "requester_scope": SCOPE})
    print(f"foreign-root token       → {status} {res['error']}")
    assert status == 403

    bad_token = dict(token, grants=[{"action": "write", "space": "self"}])
    status, res = call("POST", "/retrieve", {"query": query, "token": bad_token,
                                             "requester_scope": SCOPE})
    print(f"no retrieve grant        → {status} {res['error']}")
    assert status == 403

    # ---- 0071 sp1: THE RESOLVE DOOR LOCKS — the forgery suite -------------------------
    # a staged card sits at the gate; a stranger reaches for the pen
    status, req_row = call("POST", "/requests", {"kind": "join", "did": agent["did"],
                                                 "name": "smoke-imposter"})
    assert status == 201
    rid = req_row["id"]
    # (1) the forged approval: no token — the one face, and the card unmoved
    status, res = call("POST", "/requests/resolve", {"id": rid, "status": "approved"})
    print(f"forged approval          → {status} {res['error']}")
    assert status == 403
    # (2) the forged lease: tokenless 'done' smuggling a token into the result
    status, res = call("POST", "/requests/resolve",
                       {"id": rid, "status": "done", "result": {"token": forged}})
    print(f"forged lease result      → {status} {res['error']}")
    assert status == 403
    # (3) a retrieve-only lease is not the pen — verified chain, wrong grant
    status, res = call("POST", "/requests/resolve",
                       {"id": rid, "status": "approved", "token": token})
    print(f"lease without the pen    → {status} {res['error']}")
    assert status == 403
    _, q = call("GET", "/requests")
    row = next(r for r in q["requests"] if r["id"] == rid)
    assert row["status"] == "pending", "the card must not have moved"
    # (4) the resolver credential opens the door — and transitions are law
    pen = root.issue_token(root.did, SCOPE, [{"action": "resolve", "space": "queue"}])
    status, res = call("POST", "/requests/resolve",
                       {"id": rid, "status": "challenged", "token": pen,
                        "result": {"nonce": "abc"}})
    print(f"the pen resolves         → {status} {res}")
    assert status == 200
    # (5) the tokenless lane exists for exactly one step: answering the challenge
    proof = kp.sign(agent["did"], {"join_nonce": "abc", "did": agent["did"]})
    status, res = call("POST", "/requests/resolve",
                       {"id": rid, "status": "proved",
                        "result": {"nonce": "abc", "proof": proof}})
    print(f"tokenless proved lane    → {status} {res}")
    assert status == 200
    # (6) a settled word is never rewritten — terminal states are immutable
    status, _ = call("POST", "/requests/resolve",
                     {"id": rid, "status": "denied", "token": pen})
    assert status == 200
    status, res = call("POST", "/requests/resolve",
                       {"id": rid, "status": "approved", "token": pen})
    print(f"rewriting a settled word → {status} {res['error']}")
    assert status == 409

    # ---- 0071 sp1: THE METER DOOR LOCKS ------------------------------------------------
    meter_line = {"subject": agent["did"], "est_tokens": 5, "tokens": 5,
                  "usd": 0.0, "model": "smoke", "class": "low"}
    status, res = call("POST", "/model/meter", meter_line)
    print(f"tokenless meter          → {status} {res['error']}")
    assert status == 403
    status, res = call("POST", "/model/meter",
                       {**meter_line, "subject": "did:key:zSomeoneElse", "token": token})
    print(f"metering another's line  → {status} {res['error']}")
    assert status == 403
    status, res = call("POST", "/model/meter", {**meter_line, "token": token})
    print(f"your own line, your key  → {status} {res}")
    assert status == 200

    # ---- 0068 sp3: THE GATEWAY PIN ----------------------------------------------------
    ctx = call("GET", "/context")[1]["context"]["id"]
    auth_body = {"token": token, "class": "low", "est_tokens": 5}
    status, res = call("POST", "/model/authorize", auth_body)
    print(f"thought without its law   → {status} {res.get('error', res)}")
    assert status == 403
    status, res = call("POST", "/model/authorize",
                       {**auth_body, "context": "sha256:stale"})
    print(f"thought under a STALE law → {status} (the same face)")
    assert status == 403
    status, res = call("POST", "/model/authorize", {**auth_body, "context": ctx})
    print(f"thought naming its law    → {status} model={res.get('model')} "
          f"context pinned={res.get('context') == ctx}")
    assert status in (200, 403)   # 403 only when the demo registry is keyless
    if status == 200:
        assert res.get("context") == ctx, "the grant carries the pin verbatim"

    print("\nsmoke: Python signed, Rust verified — only the pinned root mints authority, "
          "only its pen resolves, and no thought serves without naming its law. 🥂")




def traffic() -> None:
    """0071 sp4 — the traffic-law smoke: run against a plane launched with
    ORRETH_RATE_PER_MIN=5 and ORRETH_BODY_LIMIT_BYTES=2000. Knocking is
    metered per identity; one caller's ceiling never slows another; an
    oversized body refuses loudly."""
    kp = crypto.KeyPair()
    agent = {"did": crypto.did_key_for(kp.public), "scope": SCOPE}
    nanda = Nanda()
    root = Becky("u:demo", nanda, universe_name="demo", kp=root_keypair())
    b_field = Becky(SCOPE, nanda, parent=root)
    token = b_field.issue_token(agent["did"], SCOPE,
                                [{"action": "retrieve", "space": "self"}])
    query = {"requester": agent["did"], "subject": "self", "space": "self",
             "time": {"from": "2026-07-01T00:00:00Z"}, "intent": "recall",
             "budget": {"cost": 3}, "auth": "biscuit-sim"}
    codes = []
    for _ in range(8):
        status, _res = call("POST", "/retrieve",
                            {"query": query, "token": token,
                             "requester_scope": SCOPE})
        codes.append(status)
    print(f"eight knocks at ceiling 5 → {codes}")
    assert codes[:5] == [200] * 5 and codes[5:] == [429] * 3
    # another identity is never slowed by the first one's flood
    kp2 = crypto.KeyPair()
    other = crypto.did_key_for(kp2.public)
    tok2 = b_field.issue_token(other, SCOPE,
                               [{"action": "retrieve", "space": "self"}])
    status, _res = call("POST", "/retrieve",
                        {"query": {**query, "requester": other},
                         "token": tok2, "requester_scope": SCOPE})
    print(f"the other identity        → {status}")
    assert status == 200
    # the retry hint is honest, and leaks nothing about anyone else
    status, res = call("POST", "/retrieve", {"query": query, "token": token,
                                             "requester_scope": SCOPE})
    print(f"the busy face             → {status} retry in {res.get('retry_after_s')}s")
    assert status == 429 and res.get("retry_after_s", 0) >= 1
    # the deliberate body ceiling refuses loudly
    big = make_memory(agent, kp, SCOPE, {"bulk": "x" * 4000},
                      occurred_at="2026-07-02T20:00:00Z")
    status, _res = call("POST", "/records", big)
    print(f"an oversized body         → {status}")
    assert status == 413
    print("\nsmoke: knocking is metered, per identity, inside the operator's ceilings. 🥂")


if __name__ == "__main__":
    main()
