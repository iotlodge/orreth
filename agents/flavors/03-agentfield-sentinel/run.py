# PROVENANCE: authored by Opus 4.8 (2026-07-05), pending Fable 5 review — see agents/PROVENANCE.md
"""Flavor 3 runner — the sentinel joins a floor and audits its governance from inside.

    python run.py --field http://127.0.0.1:4970 --once
    python run.py --field http://127.0.0.1:4970 --forever
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "orreth-agent-sdk"))

from orreth_agent import FieldClient  # noqa: E402
from sentinel import app  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser(description="Run the Flavor-3 conformance sentinel.")
    ap.add_argument("--field", default="http://127.0.0.1:4502")
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--once", action="store_true")
    g.add_argument("--forever", action="store_true")
    ap.add_argument("--cadence", type=int, default=30)
    args = ap.parse_args()

    client = FieldClient(args.field, name="sentinel", role="warden")
    print(f"· spawned sentinel — {client.did[:32]}…")
    client.join(timeout=45)
    print(f"· joined {client.scope} — auditing from inside\n")

    def one(n: int) -> None:
        out = app.audit(client)
        for f in out["findings"]:
            mark = "✓" if f.verdict == "PASS" else ("—" if f.verdict == "SKIP" else "✗")
            print(f"  {mark} {f.invariant:<22} {f.observed}")
        s = out["summary"]
        print(f"  ═ audit {n}: {s['passed']}/{s['invariants']} held → {s['verdict']}\n")

    if args.forever:
        print(f"· watching — an audit every {args.cadence}s (ctrl-C to rest)")
        n = 0
        try:
            while True:
                n += 1
                one(n)
                time.sleep(args.cadence)
        except KeyboardInterrupt:
            print("· resting. the findings remain in the Window.")
    else:
        one(1)
        print("· done. the sentinel and its findings are in the Console.")


if __name__ == "__main__":
    main()
