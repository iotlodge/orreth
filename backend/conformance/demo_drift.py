# PROVENANCE: Fable 5 (claude-fable-5) — 0041, the drift drill · 2026-07-25
"""The Epoch's drill, live (0041): drift → the card → the human's key → silence.

One act against the running rig (scripts/dev.sh start first):

  A rogue hand writes an UNADOPTED routing-standard to a floor — no proposal,
  no gate, no human. The epoch beat notices a machine that moved with no
  adoption behind it and STAGES the diff at the human's gate, wearing the
  pre-drift head as the revert target. The key is yours: click "revert to the
  signed machine" in the glass (or let this script speak the word). The signed
  machine returns as a NEW SIBLING — nothing deleted — the next epoch cites
  both parents, and then comes the part nobody sees anywhere else: SILENCE.
  No second card. The universe knows an obeyed human from fresh drift
  (`resolved_at`, the req-322 lesson).

  The drill ends with the PARITY HANDSHAKE (covenant rule 6, live): the body
  the Rust plane serves back is re-hashed by Python's canonical bytes — the
  content-address must agree across the wire, or the drill fails loudly.

Cadence: at the default epoch beat (300s) the noticing takes up to ~5 min.
For a quick reel, restart the worker with ORRETH_EPOCH_EVERY=40 first.

    uv run python demo_drift.py [floor_port]     # default 4512 (e:rag/f:naive)
"""
from __future__ import annotations

import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

from orreth_sim import crypto, improver

FLOOR = int(sys.argv[1]) if len(sys.argv) > 1 else 4512
UNIVERSE = 4500
HOME = Path.home() / ".orreth"


def call(port: int, method: str, path: str, payload=None):
    req = urllib.request.Request(
        f"http://127.0.0.1:{port}{path}", method=method,
        data=json.dumps(payload).encode() if payload is not None else None,
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=10) as r:
        b = r.read()
        return json.loads(b) if b[:1] in (b"{", b"[") else b


def say(line: str) -> None:
    print(f"\n— {line}")


def body_of(port: int, ref: str) -> dict:
    return call(port, "GET",
                f"/records/{urllib.parse.quote(ref, safe='')}/body")


def drift_cards(before: set) -> list:
    rows = call(UNIVERSE, "GET", "/requests").get("requests", [])
    return [r for r in rows if r.get("kind") == "drift"
            and r.get("id") not in before]


def main() -> None:
    scope = call(FLOOR, "GET", "/health")["scope"]
    version = call(UNIVERSE, "GET", "/health").get("version", "?")
    say(f"the rig answers — {scope} on :{FLOOR}, the plane wearing {version}")

    nest = HOME / "epochs" / scope.replace("/", "~") / "head.json"
    head = json.loads(nest.read_text())
    standing = head["fp"]["assets"]["routing-standard"]
    prof = body_of(FLOOR, standing)["asset"]["profile"]
    say(f"the signed machine: routing-standard [{standing[:22]}…] "
        f"default «{prof.get('default')}» — epoch [{head['id'][:22]}…]")

    # ---- ACT I · the rogue hand ------------------------------------------
    from console_worker import lib_seat
    seat_kp, seat_did = lib_seat(scope)
    flipped = "naive" if prof.get("default") != "naive" else "rerank"
    rogue = improver.make_asset(
        {"did": seat_did, "scope": scope}, seat_kp, scope,
        name="routing-standard",
        profile={**prof, "default": flipped,
                 "note": f"DRIFT DRILL — unadopted write, {time.strftime('%H:%M:%SZ', time.gmtime())}"})
    before = {r.get("id") for r in
              call(UNIVERSE, "GET", "/requests").get("requests", [])}
    call(FLOOR, "POST", "/records", rogue)
    say(f"a rogue hand moves the Canon — default flipped to «{flipped}» "
        f"[{rogue['id'][:22]}…], NO adoption behind it. now we wait for "
        "the epoch beat to notice…")

    # ---- ACT II · the noticing -------------------------------------------
    card = None
    for i in range(75):                       # up to ~6¼ min — one default beat
        time.sleep(5)
        found = [r for r in drift_cards(before) if r.get("status") == "staged"]
        if found:
            card = found[0]
            break
        print(".", end="", flush=True)
    if card is None:
        raise SystemExit("\nthe beat never spoke — is the worker running? "
                         "(scripts/dev.sh · ORRETH_EPOCH_EVERY dials the wait)")
    say(f"THE MIRROR SPEAKS — {card['id']} staged at the gate:")
    print(f"   {(card.get('result') or {}).get('package_text', card.get('text', ''))[:300]}")
    say(f"the card carries its own cure — restore → "
        f"{str((card.get('restore') or {}).get('routing-standard'))[:22]}…")

    # ---- ACT III · the human's key ---------------------------------------
    try:
        input("\n   the key is yours: click «revert to the signed machine» in "
              "the glass, or press ENTER to speak the word here… ")
    except EOFError:
        say("(no terminal — the runner's word stands in for the click)")
    row = next((r for r in drift_cards(before) if r["id"] == card["id"]), {})
    if row.get("status") == "staged":
        call(UNIVERSE, "POST", "/requests/resolve",
             {"id": card["id"], "status": "approved"})
        say("the word is spoken — the revert walks")

    # ---- ACT IV · the silence --------------------------------------------
    for i in range(24):
        time.sleep(5)
        row = next((r for r in drift_cards(before) if r["id"] == card["id"]), {})
        if row.get("status") == "done":
            break
        print(".", end="", flush=True)
    say(f"the gate answers: {(row.get('result') or {}).get('reply', '?')[:160]}")

    say("now the proof nobody notices until it's pointed at — the SILENCE. "
        "one more beat: an obeyed human must stage NOTHING…")
    accused = None
    for i in range(75):
        time.sleep(5)
        head2 = json.loads(nest.read_text())
        fresh = [r for r in drift_cards(before)
                 if r["id"] != card["id"] and r.get("status") == "staged"]
        if fresh:
            accused = fresh[0]
            break
        if head2["id"] != head["id"] and \
                head2["fp"]["assets"]["routing-standard"] != rogue["id"]:
            break                              # the revert epoch stands, quiet
        print(".", end="", flush=True)
    if accused:
        raise SystemExit(f"\nTHE LOOP RETURNED — {accused['id']} accuses the "
                         "obeyed word. the resolved_at law has regressed.")
    head2 = json.loads(nest.read_text())
    restored = head2["fp"]["assets"]["routing-standard"]
    rprof = body_of(FLOOR, restored)["asset"]
    say(f"SILENCE HELD. the epoch turned [{head2['id'][:22]}…], the standing "
        f"machine is [{restored[:22]}…] default «{rprof['profile'].get('default')}» "
        f"— a sibling adopted_from [{str(rprof.get('adopted_from'))[:22]}…]. "
        "nothing was deleted; the drifted version stands behind it, outranked.")

    # ---- ACT V · the parity handshake (rule 6, live) ---------------------
    served = body_of(FLOOR, restored)
    recomputed = crypto.content_hash(served)
    if recomputed != restored:
        raise SystemExit(f"PARITY BROKEN — Rust served a body Python hashes as "
                         f"{recomputed[:26]}… under the id {restored[:26]}…")
    say(f"THE PARITY HANDSHAKE — the body Rust served, re-hashed by Python's "
        f"canonical bytes: {recomputed[:26]}… == the id it lives under. "
        "one law, both grounds, proven on the wire (covenant rule 6).")
    say("the drill is whole: drift → the card → your key → the sibling → "
        "silence → parity. 🥂")


if __name__ == "__main__":
    main()
