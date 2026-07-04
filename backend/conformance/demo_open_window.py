"""Open the Window: seed a life across deep time, mint its capability, print the URL.

    uv run python demo_open_window.py [field_port] [universe_port]

Then open the printed URL — the daemon serves its own glass at /window, and every
render is a governed, tokened query (0008: no privileged pane path).
"""
from __future__ import annotations

import base64
import json
import sys
import webbrowser
import urllib.request
from datetime import datetime, timedelta, timezone

from orreth_sim import crypto
from orreth_sim.identity import Becky, Nanda
from orreth_sim.node import make_memory
from smoke_orrethd import root_keypair

FIELD_PORT = sys.argv[1] if len(sys.argv) > 1 else "4502"
UNI_PORT = sys.argv[2] if len(sys.argv) > 2 else "4500"
SCOPE = "u:demo/e:cloud/f:prod"


def post(port: str, rec: dict) -> None:
    req = urllib.request.Request(f"http://127.0.0.1:{port}/records", method="POST",
                                 data=json.dumps(rec).encode(),
                                 headers={"Content-Type": "application/json"})
    try:
        urllib.request.urlopen(req).read()
    except Exception:
        pass  # duplicates on re-run are fine — content-addressed ids make replays harmless


def ago(days: float) -> str:
    return (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ")


def main() -> None:
    kp = crypto.KeyPair()
    agent = {"did": crypto.did_key_for(kp.public), "scope": SCOPE}

    # a biography scattered across spacetime: deep memories at the apex, recent at the field
    # backfilled biography enters as labeled archive (0004: lived memory never backdates)
    post(UNI_PORT, make_memory(agent, kp, SCOPE, {"chapter": "the founding season"},
                               occurred_at=ago(420), provenance_class="ingested-archive"))
    post(UNI_PORT, make_memory(agent, kp, SCOPE, {"chapter": "the championship"},
                               occurred_at=ago(180), provenance_class="ingested-archive"))
    post(FIELD_PORT, make_memory(agent, kp, SCOPE, {"chapter": "spring training"},
                                 occurred_at=ago(45), provenance_class="ingested-archive"))
    post(FIELD_PORT, make_memory(agent, kp, SCOPE, {"chapter": "yesterday's win"},
                                 occurred_at=ago(0.001)))

    # seed a little LIFE so the roster rail breathes (v3): two steward-signed run records
    from orreth_sim.identity import NOW as _NOW
    steward = crypto.KeyPair(); s_did = crypto.did_key_for(steward.public)
    for i, (oc, sc) in enumerate([("partial", 0.0), ("success", 1.0)]):
        run = {"id": crypto.content_hash({"c": i, "t": _NOW(), "a": agent["did"]}),
               "agent": agent["did"], "scope": SCOPE, "goal_hash": "sha256:demo-intent",
               "occurred_at": _NOW(), "outcome": oc,
               "scores": [{"objective": "objective-met", "score": sc}],
               "cost": {"tokens": 55 + i}, "author": s_did}
        run["sig"] = steward.sign(s_did, {k: run[k] for k in ("id","agent","scope","goal_hash","occurred_at")})
        req = urllib.request.Request(f"http://127.0.0.1:{FIELD_PORT}/runs", method="POST",
            data=json.dumps(run).encode(), headers={"Content-Type": "application/json"})
        try: urllib.request.urlopen(req).read()
        except Exception: pass

    nanda = Nanda()
    root = Becky("u:demo", nanda, universe_name="demo", kp=root_keypair())
    token = root.issue_token(agent["did"], "u:demo",
                             [{"action": "retrieve", "space": "self"}])
    cfg = {"token": token, "requester": agent["did"], "requester_scope": SCOPE,
           "tiers": [SCOPE, "u:demo/e:cloud", "u:demo"]}
    frag = base64.b64encode(json.dumps(cfg).encode()).decode()
    url = f"http://127.0.0.1:{FIELD_PORT}/window#t={frag}"
    uni_url = f"http://127.0.0.1:{UNI_PORT}/window#t={frag}"   # same capability, apex floor
    print("the console is ready — opening your browser…\n")
    print(f"  field console (your biography, all lanes):  {url}\n")
    print(f"  universe console (the whole world in orbit): {uni_url}\n")
    webbrowser.open(url)
    webbrowser.open(uni_url)     # the turning universe deserves its own tab
    print("drag the brass handle into deep time and watch the tiers light up. 🥂")


if __name__ == "__main__":
    main()
