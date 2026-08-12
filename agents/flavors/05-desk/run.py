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
    args = ap.parse_args()

    client = FieldClient(args.field, "charles", role="workforce")
    print(f"· charles is {client.did[:28]}… — the same self, every morning")
    client.join()
    print(f"· lease held on {client.scope} — the desk's own floor")

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
                           GovernedThink(client, max_tokens=1600),
                           GovernedThink(client, max_tokens=2400),
                           ticker, date)
        print(f"· the walk is whole: {out['rating']} — bundle at {out['bundle']}")
        return 0

    persona = acquire("charles-trading-persona", did=client.did)
    pipeline = acquire("charles-trading-pipeline", did=client.did)
    disclaimer = acquire("charles-trading-compliance-disclaimer", did=client.did)
    print(f"· craft acquired from the shelf: persona v{persona.version} "
          f"({persona.ref[:18]}…), pipeline v{pipeline.version}, "
          f"disclaimer v{disclaimer.version}")

    client.remember(
        {"birth": "charles takes the desk",
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
