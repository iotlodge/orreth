"""The plane authorizes; cognition executes (0016 §6) — live against orrethd.

Budgets are enforced in the DAEMON's ledger now: authorize debits, meter reconciles,
usage rolls up at /model/usage, and a sunset model becomes unreachable plane-side.

    uv run python demo_model_plane_live.py [port]
"""
from __future__ import annotations

import json
import sys
import urllib.request
from pathlib import Path

from dotenv import load_dotenv

from orreth_sim import crypto
from orreth_sim.agent_surface import BudgetExceeded
from orreth_sim.identity import Becky, Nanda
from orreth_sim.model_plane import PlaneClient
from smoke_orrethd import root_keypair

load_dotenv(Path(__file__).resolve().parents[2] / ".env")
BASE = f"http://127.0.0.1:{sys.argv[1] if len(sys.argv) > 1 else 4800}"
SCOPE = "u:demo/e:cloud/f:prod"


def main() -> None:
    kp = crypto.KeyPair()
    did = crypto.did_key_for(kp.public)
    nanda = Nanda()
    root = Becky("u:demo", nanda, universe_name="demo", kp=root_keypair())
    token = root.issue_token(did, SCOPE, [{"action": "retrieve", "space": "self"}],
                             budget={"tokens": 800})
    client = PlaneClient(BASE, token)
    print("lease minted from the pinned root · budget 800 tokens (held by the PLANE)")

    r = client.call("low", [{"role": "user",
        "content": "One sentence: why should a model's retirement never surprise production?"}],
        max_tokens=120)
    print(f"\n[{r['class']} → {r['model']}]  {r['text'].strip()}")
    print(f"  metered by the daemon: {r['tokens']} tokens (${r['usd']}) · remaining {r['remaining']}")

    # the ledger is plane-side: a call the budget can't cover is refused BY THE DAEMON
    try:
        client.call("low", [{"role": "user", "content": "again"}], max_tokens=800)
    except BudgetExceeded as e:
        print(f"  over-budget authorize → refused by the plane: {e}")

    # lifecycle, plane-side: sunset the primary and watch authorization re-route
    def post(path, payload):
        req = urllib.request.Request(BASE + path, method="POST",
                                     data=json.dumps(payload).encode(),
                                     headers={"Content-Type": "application/json"})
        return json.loads(urllib.request.urlopen(req).read())

    post("/model/state", {"model": "anthropic/claude-haiku-4-5-20251001", "state": "sunset"})
    _, grant = client._post("/model/authorize",
                            {"token": token, "class": "low", "est_tokens": 10})
    print(f"\nsunset the primary → the plane now grants: {grant.get('model')}")

    usage = json.loads(urllib.request.urlopen(BASE + "/model/usage").read())
    print(f"usage (the Cortex view, from the daemon): {usage}")
    print("\nthe plane holds the ledger; cognition holds the keys; neither holds both. 🥂")


if __name__ == "__main__":
    main()
