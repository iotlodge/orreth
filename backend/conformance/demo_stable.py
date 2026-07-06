# PROVENANCE: Fable 5 (claude-fable-5) — 0019, the Stable · 2026-07-06
"""The Stable, live (0019): a mind's whole life in ninety seconds.

Two acts against the running rig (scripts/dev.sh start first):

  I.  A REAL mind from the open market — picked out of OpenRouter's public catalog —
      is saddled, its DEAL (pricing · context · modalities) pinned by ada, approved,
      and earns `available` through governed canary beats.
  II. An old pony walks the calendar: saddled with an announced expiry a few days
      out, it serves — until ada's sync sees the date inside the horizon, flips it
      deprecated (loud, never silent), and STAGES A RECOMMENDATION: the nearest
      replacement by price, already waiting in the queue. The human approves the
      swap; the successor canaries in; the pony sets. No outage — an appointment.

Nothing here talks to the stable directly except as a human would: intents go through
the request queue, ada (the wrangler) does the work, every transition lands as a
signed MemoryRecord on the mind's worldline, and every governed thought — ada's own
included — shows on one meter. Run it, then open the Console (scripts/dev.sh window)
and look at the Stable tab: the ladder, the pasture calendar, and who is thinking.

    uv run python demo_stable.py [field_port]
"""
from __future__ import annotations

import json
import sys
import time
import urllib.request
from datetime import date, timedelta

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 4502
BASE = f"http://127.0.0.1:{PORT}"


def call(method: str, path: str, payload=None):
    req = urllib.request.Request(BASE + path, method=method,
        data=json.dumps(payload).encode() if payload is not None else None,
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read())


def say(s: str) -> None:
    print(s, flush=True)


def submit(payload: dict) -> str:
    return call("POST", "/requests", payload)["id"]


def wait_status(rid: str, statuses: set[str], timeout: int = 40) -> dict:
    for _ in range(timeout * 2):
        for r in call("GET", "/requests")["requests"]:
            if r["id"] == rid and r["status"] in statuses:
                return r
        time.sleep(0.5)
    raise SystemExit(f"  ✗ request {rid} never reached {statuses} — is the worker up? "
                     "(scripts/dev.sh start)")


def approve(rid: str) -> None:
    call("POST", "/requests/resolve", {"id": rid, "status": "approved"})


def stall(mid: str) -> dict | None:
    return next((s for s in call("GET", "/stable")["stalls"] if s["id"] == mid), None)


def wait_state(mid: str, states: set[str], timeout: int = 60) -> dict:
    for _ in range(timeout * 2):
        s = stall(mid)
        if s and s["state"] in states:
            return s
        time.sleep(0.5)
    raise SystemExit(f"  ✗ {mid} never reached {states}")


def market_pick() -> str:
    """A real mind off the open market — first Anthropic entry with no expiry."""
    raw = json.loads(urllib.request.urlopen(urllib.request.Request(
        "https://openrouter.ai/api/v1/models"), timeout=15).read())["data"]
    for m in raw:
        if m["id"].startswith("anthropic/") and not m.get("expiration_date"):
            return m["id"]
    return raw[0]["id"]


say("\n═══ THE STABLE (0019) · a mind's whole life ═══\n")

# ---- ACT I · a real mind, saddled and earned -------------------------------------------
say("ACT I · the market's mind\n")
real = market_pick()
say(f"  the market offers {real} — saddle it (medium):")
rid = submit({"kind": "mind", "action": "saddle", "mind": real, "route": "litellm-direct",
              "class": "medium", "text": f"saddle {real} (medium)"})
r = wait_status(rid, {"staged"})
v = r.get("result") or {}
say(f"  ↳ ada probed the catalog: in_catalog={v.get('in_catalog')}, "
    f"deal pinned {str(v.get('manifest_hash',''))[:22]}…")
say("  the human approves — the gate opens:")
approve(rid)
s = wait_state(real, {"canaried", "available"})
say(f"  ↳ {real} is {s['state']} — canary beats now earn its place")
s = wait_state(real, {"available"})
say(f"  ✓ {real} is AVAILABLE — earned after {s.get('canary_beats')} governed beats\n")

# ---- ACT II · the pasture calendar ------------------------------------------------------
say("ACT II · the old pony and the calendar\n")
PONY = "local.demo/old-pony"
soon = (date.today() + timedelta(days=10)).isoformat()
say(f"  an old pony is saddled, its expiry already announced: {soon}")
rid = submit({"kind": "mind", "action": "saddle", "mind": PONY, "route": "litellm-direct",
              "class": "low", "expires_at": soon,
              "manifest": {"pricing": {"prompt": "0.000001", "completion": "0.000004"},
                           "context_length": 32000, "modalities": ["text"]},
              "text": f"saddle {PONY} (low) — expires {soon}"})
wait_status(rid, {"staged"})
approve(rid)
wait_state(PONY, {"canaried", "available"})
say("  ↳ the pony serves… and ada reads the calendar on her next sync:")
s = wait_state(PONY, {"deprecated"}, timeout=30)
say(f"  ↳ {PONY} flipped DEPRECATED — expiry {str(s.get('expires_at'))[:10]} is inside "
    "the 30-day horizon. Loud, never silent.")
say("  ada stages her recommendation — the human finds it waiting:")
swap = None
for _ in range(40):
    swap = next((r for r in call("GET", "/requests")["requests"]
                 if r.get("kind") == "mind" and r.get("action") == "swap"
                 and r.get("mind") == PONY and r["status"] == "staged"), None)
    if swap:
        break
    time.sleep(0.5)
if not swap:
    raise SystemExit("  ✗ no swap recommendation staged")
say(f"  ↳ “{swap['text']}”")
say("  the human approves the swap — an appointment, not an outage:")
approve(swap["id"])
rep = (swap.get("replacement") or {}).get("id")
for _ in range(40):
    s = stall(PONY)
    if s and s["state"] == "sunset":
        break
    time.sleep(0.5)
say(f"  ✓ {PONY} has SET — retired, remembered" +
    (f"; {rep} canaries in its place" if rep and not (swap.get('replacement') or {}).get('in_stable') else ""))

# ---- the meter and the worldline ---------------------------------------------------------
say("\nTHE METER · who is thinking, on one meter")
usage = call("GET", "/stable").get("usage", [])
if usage:
    for u in usage:
        say(f"  {u['subject'][:34]:<36} {u['calls']:>3} call(s) · "
        f"{u['tokens']:>6} tok · ${u['usd']}")
else:
    say("  (no governed thoughts metered on this rig — no provider key; the canary "
        "rested on verified syncs, which is the honest fallback)")

say("\nTHE WORLDLINE · open the Console (scripts/dev.sh window) → Stable tab:")
say("  the ladder shows who answers each class; the pasture calendar shows what")
say("  expires; and every move above is a signed memory in the spacetime window. 🥂\n")
