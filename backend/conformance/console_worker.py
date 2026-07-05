"""The console worker — cognition behind the human's queue (0014 · 0006, human-initiated).

Polls orrethd's request queue and answers two kinds of intent, keys staying here in cognition:

  · gather X  — runs the librarian: searches an identified source (Tavily), admits the
    findings as signed memories (quarantined at 0.0000); knowledge appears in the Window.
  · join      — becky's door: an agent (from anywhere) asks to join this floor; becky mints
    a root-chained retrieve lease for its DID and resolves the request with the token. The
    agent's first signed memory then lights it up in the roster and the orrery.

    uv run python console_worker.py [field_port]     (leave running while you use the Console)
"""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.request
from pathlib import Path

from dotenv import load_dotenv

from orreth_sim import crypto
from orreth_sim.identity import NOW, Becky, Nanda
from orreth_sim.node import make_memory
from smoke_orrethd import root_keypair

load_dotenv(Path(__file__).resolve().parents[2] / ".env")
sys.stdout.reconfigure(line_buffering=True)  # nohup'd by dev.sh — block-buffering leaves the log empty
try:
    os.setsid()  # own session: a Ctrl-C aimed at the launching script must not kill becky
except OSError:
    pass
BASE = f"http://127.0.0.1:{sys.argv[1] if len(sys.argv) > 1 else 4502}"
SCOPE = "u:demo/e:cloud/f:prod"
LIB = crypto.KeyPair()                       # the librarian's identity (cognition holds keys)
LIB_DID = crypto.did_key_for(LIB.public)

# becky, chained from the pinned root — the only authority that can mint a joining lease
_NANDA = Nanda()
_ROOT = Becky("u:demo", _NANDA, universe_name="demo", kp=root_keypair())
_BECKY = Becky(SCOPE, _NANDA, parent=_ROOT)


def grant_lease(did: str) -> dict:
    """A retrieve-self lease for a joining agent — attenuated to this floor, root-chained."""
    return _BECKY.issue_token(did, SCOPE, [{"action": "retrieve", "space": "self"}])


def call(method, path, payload=None):
    req = urllib.request.Request(BASE + path, method=method,
        data=json.dumps(payload).encode() if payload else None,
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as r:
        b = r.read()
        return json.loads(b) if b[:1] in (b"{", b"[") else b


def tavily(q, n=3):
    if not os.environ.get("TAVILY_API_KEY"):
        return [{"title": f"(no TAVILY_API_KEY) placeholder finding on {q}",
                 "content": "set the key to gather real sourced knowledge", "url": "local://demo"}]
    req = urllib.request.Request("https://api.tavily.com/search", method="POST",
        data=json.dumps({"api_key": os.environ["TAVILY_API_KEY"], "query": q,
                         "max_results": n}).encode(), headers={"Content-Type": "application/json"})
    return json.loads(urllib.request.urlopen(req).read())["results"]


def gather(text):
    agent = {"did": LIB_DID, "scope": SCOPE}
    for r in tavily(text):
        body = {"knowledge": f"{r['title']} — {r['content'][:120]}",
                "source": {"did": "did:web:tavily.com", "ref": r.get("url", "")},
                "state": "untrusted", "intent": text}
        rec = make_memory(agent, LIB, SCOPE, body, kind="semantic",
                          tags=["knowledge", "gathered"],
                          provenance_class="ingested-archive")
        call("POST", "/records", rec)


def main():
    print(f"console worker · librarian+becky {LIB_DID[:24]}… · watching {BASE}/requests")
    seen = set()
    while True:
        try:
            for r in call("GET", "/requests").get("requests", []):
                # key by (id, at): the daemon's queue is in-memory with sequential ids, so a
                # restarted daemon reissues req-1… — the timestamp keeps stale ids from
                # deafening becky to new joins
                key = (r.get("id"), r.get("at", ""))
                if r.get("status") != "pending" or key in seen:
                    continue
                if r.get("kind") == "gather":
                    seen.add(key)
                    print(f"  ↳ dispatch {r['id']}: gather “{r['text']}”")
                    gather(r["text"])
                    call("POST", "/requests/resolve",
                         {"id": r["id"], "status": "done", "result": "admitted to the Window"})
                    print(f"    ✓ knowledge admitted — check the Window")
                elif r.get("kind") == "join" and r.get("did"):
                    seen.add(key)
                    print(f"  ↳ join {r['id']}: {r.get('name','?')} ({r['did'][:22]}…) as {r.get('role','workforce')}")
                    lease = grant_lease(r["did"])
                    call("POST", "/requests/resolve",
                         {"id": r["id"], "status": "done",
                          "result": {"token": lease, "scope": SCOPE, "granted_by": _BECKY.did}})
                    print(f"    ✓ lease granted — welcome to {SCOPE}")
        except Exception as e:
            print("  (waiting for daemon…)", e)
        time.sleep(2)


if __name__ == "__main__":
    main()
