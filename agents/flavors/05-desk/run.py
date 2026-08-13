# PROVENANCE: Fable 5 (claude-fable-5) — 0054 sp1, charles is born · 2026-08-12
"""charles — the Trading desk resident (0054: The Desk).

sp1 is the birth walk: charles joins HIS OWN floor (u:demo/e:desk/f:charles —
the first field whose join door mints a lease for its own scope, 0054's
becky-per-floor law), proves his key at the gate, waits for the human, and
then acquires his persona and his pipeline FROM THE SHELF — the words live
on the universe shelf as versioned craft, never in this file. His first
Chronicle record is his birth, citing the exact craft refs he woke with.

The pipeline itself (analysts → debates → decisions → report) is sp3.

    uv run --with cryptography python agents/flavors/05-desk/run.py --once
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "orreth-agent-sdk"))

from orreth_agent.client import FieldClient            # noqa: E402
from orreth_agent.craft import acquire                 # noqa: E402

UNIVERSE = "http://localhost:4500"
FIELD_DEFAULT = "http://localhost:4520"                # f:charles (shipyard-allocated)


def _gate(client, ticker: str, date: str, timeout: float = 600.0) -> bool:
    """The plan gate up front (0027/0030): the walk is staged as a request in
    the human's queue and NOTHING runs until a human approves — silence past
    the timeout is a no, and says so."""
    import time
    _, made = client._call("POST", "/requests", {
        "kind": "desk-run",
        "text": (f"charles will walk {ticker} ({date}) — 8 data calls through the "
                 f"Farm's door · ≤3 searches under the daily ceiling · ~15 governed "
                 f"thoughts (2 at high) · the report lands as records + a bundle. "
                 f"Reports only; never a trade.")})
    rid = made.get("id")
    print(f"· the walk waits at the gate ({rid}) — a human decides")
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        for r in client._call("GET", "/requests")[1].get("requests", []):
            if r.get("id") == rid:
                if r.get("status") == "approved":
                    return True
                if r.get("status") == "denied":
                    print("· the human said no — the desk rests")
                    return False
        time.sleep(4)
    print("· no answer at the gate — silence is a no; the desk rests")
    return False


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--field", default=FIELD_DEFAULT)
    ap.add_argument("--once", action="store_true")
    ap.add_argument("--analyze", metavar="TICKER")
    ap.add_argument("--date", default=None)
    ap.add_argument("--refresh", action="store_true",
                    help="analyze in refresh mode (reuse the prior walk's analysts)")
    ap.add_argument("--name", default="charles")
    ap.add_argument("--world", default="trading-desk")
    ap.add_argument("--tend", action="store_true",
                    help="tend the standing word: walk when due, reflect when ripe")
    args = ap.parse_args()

    client = FieldClient(args.field, args.name, role="workforce")
    print(f"· {args.name} is {client.did[:28]}… — the same self, every morning")
    if args.tend:
        # a standing crew member outlives a slow gate with ONE patient card,
        # never a flood: a single join request held open for hours, polled
        # until a human welcomes him (the 41-card lesson, 2026-08-13)
        while True:
            try:
                client.join(timeout=6 * 3600)
                break
            except Exception as e:
                print(f"· the gate has not answered in hours ({str(e)[:60]}…) — "
                      "one fresh card, and the wait goes on")
    else:
        client.join()
    print(f"· lease held on {client.scope} — the desk's own floor")

    if args.tend:
        # ── sp5: the standing word, tended (0032 on the desk) ──────────
        # The human approved the watch ONCE at the gate; each due walk runs
        # UNDER that standing consent — no fresh gate, cancellable anytime
        # (rule 11), and every walk still lands as records like any other.
        import json as _j
        import os as _o
        import time as _t
        import urllib.request as _u
        from orreth_agent.chassis import GovernedThink
        import pipeline
        tm, th, tf = (GovernedThink(client, max_tokens=1500),
                      GovernedThink(client, max_tokens=3200),
                      GovernedThink(client, max_tokens=2400))
        def _world():
            try:
                with _u.urlopen(f"http://localhost:4562/desk?key={args.world}", timeout=8) as r:
                    d = _j.load(r)
                me = next((w for w in d.get("worlds", []) if w.get("key") == args.world), {})
                return d.get("watches", []), (me.get("posture") or "standing")
            except Exception:
                return [], "standing"
        def _walked_today(tk, day):
            for h in client.recall(days=7).get("hits", []):
                b = client.body_of(h["ref"]) or {}
                if b.get("report") and b.get("ticker") == tk and b.get("date") == day:
                    return True
            return False
        said_paused = False
        while True:
            today = _t.strftime("%Y-%m-%d")
            due_now = bool(_o.environ.get("ORRETH_DESK_DUE_NOW"))
            watches, posture = _world()
            if posture == "paused":
                # stopped by the human's word — the desk rests WHOLE: no
                # walks, no asks, the watchlist preserved for continue
                if not said_paused:
                    print("· the desk is stopped by the human's word — resting "
                          "whole; continue recovers everything")
                    said_paused = True
                if args.once:
                    return 0
                _t.sleep(60)
                continue
            said_paused = False
            for w in watches:
                if w.get("posture") != "walk":
                    continue
                tk = w.get("ticker")
                weekday = _t.gmtime().tm_wday < 5
                at_close = _t.gmtime().tm_hour >= 20
                if not (due_now or (weekday and at_close)):
                    continue
                if _walked_today(tk, today):
                    print(f"· {tk} already walked today — the standing word rests")
                    continue
                print(f"· the standing word ({w.get('approved', '?')}) is due — "
                      f"walking {tk} in refresh mode, no fresh gate needed")
                out = pipeline.run(client, tm, th, tf, tk, today,
                                   refresh=bool(w.get("refresh")), agent=args.name)
                print(f"· the walk is whole: {out['rating']} — {out['bundle']}")
            # the human's own asks ride the queue: kind desk-ask, no second
            # gate — the ask IS the human's word; duplicates for the same
            # symbol FOLD into one walk (an unanswered card breeds re-asks —
            # learned from the human's own double-click, 2026-08-13)
            pend = [r for r in client._call("GET", "/requests")[1].get("requests", [])
                    if r.get("kind") == "desk-ask" and r.get("status") == "pending"]
            seen_tk = set()
            for r in pend:
                tk = str(r.get("ticker") or "").upper()[:8]
                if not tk:
                    continue
                if tk in seen_tk:
                    client._call("POST", "/requests/resolve",
                                 {"id": r["id"], "status": "done",
                                  "result": f"folded — one walk answers {tk} for "
                                            f"every ask standing"})
                    continue
                seen_tk.add(tk)
                if True:
                    client._call("POST", "/requests/resolve",
                                 {"id": r["id"], "status": "riding",
                                  "result": f"charles is walking {tk} on your word — "
                                            f"the report lands in the Capabilities pull"})
                    print(f"· the human asked — walking {tk} now (no second gate)")
                    out = pipeline.run(client, tm, th, tf, tk, today, agent=args.name)
                    client._call("POST", "/requests/resolve",
                                 {"id": r["id"], "status": "done",
                                  "result": f"{tk}: {out['rating']} — the report is in "
                                            f"the Capabilities pull; the bundle is one "
                                            f"click down"})
                    print(f"· the ask is answered: {tk} {out['rating']}")
            graded = pipeline.grade_pending(client, tm)
            if graded:
                print(f"· {graded} lesson(s) written to the record")
            if args.once:
                return 0
            _t.sleep(60)          # a human's ask deserves a minute, not five

    if args.analyze:
        import time as _t
        from orreth_agent.chassis import GovernedThink
        import pipeline
        ticker = args.analyze.upper()
        date = args.date or _t.strftime("%Y-%m-%d")
        if not _gate(client, ticker, date):
            return 1
        out = pipeline.run(client,
                           GovernedThink(client, max_tokens=1500),
                           GovernedThink(client, max_tokens=3200),
                           GovernedThink(client, max_tokens=2400),
                           ticker, date, refresh=args.refresh, agent=args.name)
        print(f"· the walk is whole: {out['rating']} — bundle at {out['bundle']}")
        return 0

    persona = acquire(f"{args.name}-trading-persona", did=client.did)
    pipeline = acquire(f"{args.name}-trading-pipeline", did=client.did)
    disclaimer = acquire(f"{args.name}-trading-compliance-disclaimer", did=client.did)
    print(f"· craft acquired from the shelf: persona v{persona.version} "
          f"({persona.ref[:18]}…), pipeline v{pipeline.version}, "
          f"disclaimer v{disclaimer.version}")

    client.remember(
        {"birth": f"{args.name} takes the desk",
         "floor": client.scope,
         "persona_ref": persona.ref,
         "pipeline_ref": pipeline.ref,
         "disclaimer_ref": disclaimer.ref,
         "law": "the desk observes and reports; it never executes a trade"},
        kind="episodic", tags=["birth", "desk"])
    print("· the birth is on the record — the desk stands")
    return 0


if __name__ == "__main__":
    sys.exit(main())
