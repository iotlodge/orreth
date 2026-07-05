# PROVENANCE: authored by Opus 4.8 (2026-07-05), pending Fable 5 review — see agents/PROVENANCE.md
"""Flavor 2 runner — join a field, then turn the LangGraph loop.

    python run.py --field http://127.0.0.1:4970 --once
    python run.py --field http://127.0.0.1:4970 --forever
"""
from __future__ import annotations

import argparse
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "orreth-agent-sdk"))

from orreth_agent import FieldClient  # noqa: E402
from graph import build_graph  # noqa: E402

NAME = "graphling"
OBJECTIVE = "Report the field's state and the shape of the world, deterministically."


def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def skills_for(client: FieldClient) -> dict:
    return {
        "clock": lambda q: now(),
        "field_stats": lambda q: str(client._call("GET", "/rollup")[1]),
        "world_shape": lambda q: str(client._call("GET", "/topology")[1].get("children", [])),
    }


def main() -> None:
    ap = argparse.ArgumentParser(description="Run a Flavor-2 LangGraph agent.")
    ap.add_argument("--field", default="http://127.0.0.1:4970")
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--once", action="store_true")
    g.add_argument("--forever", action="store_true")
    ap.add_argument("--cadence", type=int, default=20)
    args = ap.parse_args()

    client = FieldClient(args.field, name=NAME)
    print(f"· spawned {NAME} — {client.did[:32]}…")
    client.join(timeout=45)
    print(f"· joined {client.scope} — lease in hand")

    app = build_graph(client, skills_for(client), persona="a deterministic graph agent")

    def one(n: int) -> None:
        final = app.invoke({"intent": OBJECTIVE})
        status = "done" if final.get("done") else "parked"
        tail = final.get("answer", "(parked)")[:100]
        print(f"  [{n}] {status} → {tail}")

    if args.forever:
        print(f"· living — a graph traversal every {args.cadence}s (ctrl-C to rest)")
        n = 0
        try:
            while True:
                n += 1
                one(n)
                time.sleep(args.cadence)
        except KeyboardInterrupt:
            print("\n· resting. the graph remembers.")
    else:
        one(1)
        print("· done. see graphling in the Console roster and the orrery.")


if __name__ == "__main__":
    main()
