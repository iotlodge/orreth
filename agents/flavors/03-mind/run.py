# PROVENANCE: Fable 5 (claude-fable-5) — 0047 sp3, the studio · 2026-08-07
"""Flavor 3 — the studio: the universe's comprehension seat (0047 sp3).

A mind wearing the 0047 sp2 jacket. It joins the field through becky's gate
as a persistent citizen (rule 1), benches where a medium mind serves — the
judge-bench pattern, 0043 law 2's shape — and tends the UNIVERSE queue's
`understand` legs: for every arriving Objective it returns a typed
Understanding (reading · domains · needs · gaps · confidence), grounded in
the registry — the universe's own library card — and nothing else. The
reading rides onto the plan card at the human's gate, so a human sees what
the universe UNDERSTOOD before a single leg runs.

Every thought is authorized and metered under the studio's own DID on its
own fueled lease; every method call leaves a scribe-signed RunRecord pinning
the exact craft version; a reading that fails its contract twice is PARKED
honestly and the card says so — never a guessed understanding.

    uv run agents/flavors/03-mind/run.py [--once]
    (from an env holding litellm, with the SDK on PYTHONPATH — or rely on
     the shim below)
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "orreth-agent-sdk"))

from orreth_agent.chassis import GovernedThink          # noqa: E402
from orreth_agent.client import FieldClient             # noqa: E402
from orreth_agent.mind import MindParked, OrrethMind, generation  # noqa: E402

UNIVERSE = "http://localhost:4500"     # the seat: where understand legs stage
FIELD = "http://localhost:4502"        # the bench: where a medium mind serves
REGISTRY = "http://localhost:4562"     # the library card (0045 sp1)


class StudioMind(OrrethMind):
    """One duty: read an Objective against the registry, typed."""

    @generation(klass="medium", craft="understand-objective",
                returns={"reading": str, "domains": list, "needs": list,
                         "gaps": list, "confidence": float})
    def understand(self, objective, rubric, registry):
        """The comprehension — the prompt is the shelf's (law 6)."""
        ...


def _get(url: str) -> dict:
    with urllib.request.urlopen(url, timeout=6) as r:
        return json.load(r)


def _post(base: str, path: str, payload: dict) -> dict:
    req = urllib.request.Request(base + path, method="POST",
                                 data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=8) as r:
        return json.load(r)


def registry_digest(*, limit: int = 1600) -> str:
    """The library card, bounded: every shelf object by category with its
    wearers, plus the declared rubrics — real names only, so the reading can
    ground itself (and name a gap when a name is absent)."""
    try:
        g = _get(REGISTRY + "/governance")
    except Exception:
        return "(the registry is dark — read the objective on its own words)"
    lines: list[str] = []
    by_cat: dict[str, list[str]] = {}
    for o in g.get("objects", []):
        by_cat.setdefault(o.get("category", "?"), []).append(
            o["name"] + (f" (worn by {o['wearers'][0]})" if o.get("wearers") else ""))
    for cat in sorted(by_cat):
        lines.append(f"{cat}: " + " · ".join(sorted(by_cat[cat])))
    if g.get("rubrics"):
        lines.append("declared rubrics: "
                     + " · ".join(r.get("goal", "?")[:24] for r in g["rubrics"]))
    return "\n".join(lines)[:limit]


def tend_once(mind: StudioMind, client: FieldClient) -> bool:
    """One pass of the studio's duty: answer the oldest unanswered
    understand leg. True when a leg was served (read or honestly parked)."""
    try:
        reqs = _get(UNIVERSE + "/requests").get("requests", [])
    except Exception:
        return False
    legs = [r for r in reqs
            if r.get("kind") == "understand" and r.get("status") == "pending"]
    if not legs:
        return False
    leg = legs[0]
    try:
        reading = mind.understand(str(leg.get("objective") or leg.get("text") or ""),
                                  str(leg.get("rubric") or ""),
                                  registry_digest())
        out = {**reading, "state": "read",
               "craft": mind._crafts["understand-objective"].ref,
               "by": client.did}
        print(f"· read {leg['id']}: “{reading['reading'][:72]}” "
              f"(confidence {reading['confidence']})")
    except MindParked as e:
        out = {"state": "parked", "why": str(e), "by": client.did}
        print(f"· PARKED {leg['id']}: {e}")
    _post(UNIVERSE, "/requests/resolve",
          {"id": leg["id"], "status": "done", "result": {"understanding": out}})
    return True


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--once", action="store_true",
                    help="serve one leg, then rest")
    a = ap.parse_args()
    client = FieldClient(FIELD, "studio", role="workforce")
    print(f"· the studio is {client.did[:28]}… (scribe {client.scribe_did[:24]}…)")
    print("· joining — the gate may wait for a human …")
    client.join()
    print(f"· lease held on {client.scope} — benching here, seat at u:demo")
    mind = StudioMind(client, GovernedThink(client, max_tokens=400))
    while True:
        served = tend_once(mind, client)
        if a.once and served:
            return 0
        time.sleep(3)


if __name__ == "__main__":
    sys.exit(main())
