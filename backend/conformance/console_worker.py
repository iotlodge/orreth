"""The console worker — cognition behind the human's Ask (0014, human-initiated).

Polls orrethd's request queue; when a human dispatches "gather X" from the Console,
this runs the librarian: searches an identified source (Tavily), admits the findings as
signed memories (quarantined at 0.0000), and marks the request done — so the knowledge
appears as stars in the Window seconds after the human asked. Keys stay here, in cognition.

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
from orreth_sim.identity import NOW
from orreth_sim.node import make_memory

load_dotenv(Path(__file__).resolve().parents[2] / ".env")
BASE = f"http://127.0.0.1:{sys.argv[1] if len(sys.argv) > 1 else 4502}"
SCOPE = "u:demo/e:cloud/f:prod"
LIB = crypto.KeyPair()                       # the librarian's identity (cognition holds keys)
LIB_DID = crypto.did_key_for(LIB.public)


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
    print(f"console worker · librarian {LIB_DID[:30]}… · watching {BASE}/requests")
    seen = set()
    while True:
        try:
            for r in call("GET", "/requests").get("requests", []):
                if r.get("kind") == "gather" and r["status"] == "pending" and r["id"] not in seen:
                    seen.add(r["id"])
                    print(f"  ↳ dispatch {r['id']}: gather “{r['text']}”")
                    gather(r["text"])
                    call("POST", "/requests/resolve",
                         {"id": r["id"], "status": "done", "result": "admitted to the Window"})
                    print(f"    ✓ knowledge admitted — check the Window")
        except Exception as e:
            print("  (waiting for daemon…)", e)
        time.sleep(2)


if __name__ == "__main__":
    main()
