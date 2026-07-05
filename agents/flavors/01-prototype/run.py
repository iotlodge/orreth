# PROVENANCE: authored by Opus 4.8 (2026-07-05), pending Fable 5 review — see agents/PROVENANCE.md
"""Flavor 1 — the Prototype lifeforce agent.

The whole agent is `agent.yaml` + the SDK. This runner just wires them: spawn an
identity, join a field, and turn the Chassis loop — once, or forever at a cadence.
The architecture never changes; only the profile does.

    python run.py --field http://127.0.0.1:4970 --once
    python run.py --field http://127.0.0.1:4970 --forever
    python run.py --agent my-other-agent.yaml --field <url> --forever
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

# make the sibling SDK importable without an install step (dev ergonomics)
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "orreth-agent-sdk"))

import yaml  # noqa: E402  (after sys.path shim)

from orreth_agent import Chassis, FieldClient, GovernedThink, RuleThink  # noqa: E402
import skills as skillmod  # noqa: E402


def load(agent_path: str) -> dict:
    return yaml.safe_load(Path(agent_path).read_text())


def build(cfg: dict, field_url: str):
    client = FieldClient(field_url, name=cfg["name"], role=cfg.get("role", "workforce"))
    print(f"· spawned {cfg['name']} — {client.did[:32]}…")
    client.join(timeout=45)
    print(f"· joined {client.scope} — lease in hand")

    bound = skillmod.bind(cfg.get("skills", []), client)
    if cfg.get("cognition", "rule") == "governed":
        think = GovernedThink(client)
        print("· cognition: governed (model plane, metered)")
    else:
        think = RuleThink(bound)
        print("· cognition: rule (deterministic, keyless)")

    chassis = Chassis(client, think, persona=cfg.get("persona", ""), skills=bound,
                      max_cycles=cfg.get("max_cycles", 3), max_obs=cfg.get("max_obs", 3),
                      klass=cfg.get("klass", "low"))
    return client, chassis


def main() -> None:
    ap = argparse.ArgumentParser(description="Run a Flavor-1 lifeforce agent.")
    ap.add_argument("--field", default="http://127.0.0.1:4970", help="orrethd floor URL")
    ap.add_argument("--agent", default=str(Path(__file__).parent / "agent.yaml"))
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--once", action="store_true", help="run one loop and exit")
    g.add_argument("--forever", action="store_true", help="live: loop at the agent's cadence")
    args = ap.parse_args()

    cfg = load(args.agent)
    client, chassis = build(cfg, args.field)
    intent = cfg["objective"].strip()

    def one(n: int) -> None:
        r = chassis.run(intent)
        tail = r.get("answer", "")[:100] if r["status"] == "done" else "(parked as knowledge-intent)"
        print(f"  [{n}] {r['status']} in {r['cycles']} cycle(s) → {tail}")

    if args.forever:
        cadence = cfg.get("cadence_seconds", 20)
        print(f"· living — a loop every {cadence}s (ctrl-C to rest)")
        n = 0
        try:
            while True:
                n += 1
                one(n)
                time.sleep(cadence)
        except KeyboardInterrupt:
            print("\n· resting. the memories remain.")
    else:
        one(1)
        print("· done. see this agent in the Console roster and the orrery.")


if __name__ == "__main__":
    main()
