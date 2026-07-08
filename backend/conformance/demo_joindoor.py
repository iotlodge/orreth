# PROVENANCE: Fable 5 (claude-fable-5) — the join door, hardened · 2026-07-07
"""The Gate, live: the join door answers proof, not claims.

Two knocks against the running rig (scripts/dev.sh start first):

  I.  A genuine agent — the REAL orreth-agent SDK, its seed persisted, the same
      self every run — knocks. becky challenges; it signs the nonce; the join
      STAGES at the human gate (consequence waits, 0012). The narrator, playing
      the human, admits it — visibly — and only then does the lease exist.
  II. An imposter knocks wearing the genuine agent's DID, but holds a different
      key. becky's nonce finds it out at the proof — turned away, nothing minted,
      and the roster never wore its name.

    uv run python demo_joindoor.py [field_port]
"""
from __future__ import annotations

import json
import sys
import threading
import time
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1].parent / "agents" / "orreth-agent-sdk"))

from orreth_agent.client import FieldClient, JoinRefused  # noqa: E402
from orreth_sim import crypto  # noqa: E402

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 4502
BASE = f"http://127.0.0.1:{PORT}"


def call(method: str, path: str, payload=None):
    req = urllib.request.Request(BASE + path, method=method,
        data=json.dumps(payload).encode() if payload is not None else None,
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=8) as r:
        return json.loads(r.read() or b"{}")


def say(line: str = "", beat: float = 0.6):
    print(line)
    time.sleep(beat)


def wait_status(rid: str, want: set, patience: int = 45) -> dict:
    t0 = time.time()
    while time.time() - t0 < patience:
        r = next((x for x in call("GET", "/requests")["requests"]
                  if x.get("id") == rid), {})
        if r.get("status") in want:
            return r
        time.sleep(1)
    raise SystemExit(f"\n  {rid} never reached {want} — is the worker tending?")


def find_join(did: str, want: set, patience: int = 45) -> dict:
    t0 = time.time()
    while time.time() - t0 < patience:
        for r in call("GET", "/requests")["requests"]:
            if r.get("kind") == "join" and r.get("did") == did and r.get("status") in want:
                return r
        time.sleep(1)
    raise SystemExit(f"\n  no join for {did[:22]}… reached {want}")


def main() -> None:
    say("\n═══ THE GATE — the join door answers proof, not claims ═══\n")

    say("── I. a genuine agent knocks ──")
    agent = FieldClient(BASE, "wren", role="workforce")
    say(f"  wren's self: {agent.did[:34]}… (seed on disk — the same wren, every run)")
    result: dict = {}
    t = threading.Thread(target=lambda: result.update(token=agent.join(timeout=90)), daemon=True)
    t.start()
    staged = find_join(agent.did, {"staged"})
    say("  becky challenged; wren signed the nonce — key control PROVEN")
    say(f"  and now the door WAITS: “{(staged.get('result') or {}).get('note', '')}”")
    say("  … the human looks at the queue, and admits wren:", 1.2)
    call("POST", "/requests/resolve", {"id": staged["id"], "status": "approved"})
    t.join(timeout=30)
    if not result.get("token"):
        raise SystemExit("  wren never got its lease — check the worker log")
    say(f"  ✓ lease minted, root-chained — wren is on the floor\n")

    say("── II. an imposter knocks, wearing wren's DID ──")
    imposter = crypto.KeyPair()                       # a different key entirely
    req = call("POST", "/requests", {"kind": "join", "did": agent.did,
               "name": "wren", "role": "workforce",
               "text": "wren asks to join (or so it claims)"})
    ch = wait_status(req["id"], {"challenged"})
    nonce = (ch.get("result") or {}).get("nonce", "")
    say("  becky challenged — and the imposter signs with the only key it has:")
    call("POST", "/requests/resolve", {"id": req["id"], "status": "proved",
         "result": {"nonce": nonce,
                    "proof": imposter.sign(agent.did, {"join_nonce": nonce, "did": agent.did})}})
    turned = wait_status(req["id"], {"denied"})
    say(f"  ✗ {turned.get('status')} — the nonce found it out; nothing minted,")
    say("    and the roster never wore its name.\n")

    say("  One door. Proof of key, then a human — in that order, every time.")
    say("  Open the Console's Requests tab to see the gate for yourself.\n")


if __name__ == "__main__":
    main()
