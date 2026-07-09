# PROVENANCE: Fable 5 (claude-fable-5) — the crew · 2026-07-08
"""The Crew: a field takes on hands, and every hand is a self.

Three agents of the REAL orreth-agent SDK join the floor through the hardened gate
(proof of key, then a human — in that order, every time). wren RETURNS — the same
seed on disk, the same DID as its first visit: reboot ≠ death, the covenant's first
rule made visible. moss and flint knock for the first time and become selves.

Once through the door each one works: a small chassis objective on RuleThink
(deterministic cognition — zero keys, zero dollars) with one REAL skill each,
reading the floor they stand on. Every cycle lands as a scribe-signed RunRecord —
so the orrery grows ships, the roster grows names, and the meter stays honest.

    uv run python demo_workforce.py [field_port]
"""
from __future__ import annotations

import json
import sys
import threading
import time
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1].parent / "agents" / "orreth-agent-sdk"))

from orreth_agent.chassis import Chassis, RuleThink  # noqa: E402
from orreth_agent.client import FieldClient  # noqa: E402

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 4502
BASE = f"http://127.0.0.1:{PORT}"


def call(method: str, path: str, payload=None):
    req = urllib.request.Request(BASE + path, method=method,
        data=json.dumps(payload).encode() if payload is not None else None,
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=8) as r:
        return json.loads(r.read() or b"{}")


def say(line: str = "", beat: float = 0.5):
    print(line)
    time.sleep(beat)


def find_join(did: str, want: set, patience: int = 45) -> dict:
    t0 = time.time()
    while time.time() - t0 < patience:
        for r in call("GET", "/requests")["requests"]:
            if r.get("kind") == "join" and r.get("did") == did and r.get("status") in want:
                return r
        time.sleep(1)
    raise SystemExit(f"\n  no join for {did[:22]}… reached {want}")


def admit(agent: FieldClient) -> None:
    """The knock, the proof, the human — the gate demo's flow, worn by the crew."""
    result: dict = {}
    t = threading.Thread(target=lambda: result.update(token=agent.join(timeout=90)),
                         daemon=True)
    t.start()
    staged = find_join(agent.did, {"staged"})
    say(f"  {agent.name} proved its key — the door waits; the human admits {agent.name}:")
    call("POST", "/requests/resolve", {"id": staged["id"], "status": "approved"})
    t.join(timeout=30)
    if not result.get("token"):
        raise SystemExit(f"  {agent.name} never got its lease — check the worker log")
    say(f"  ✓ {agent.name} is on the floor — {agent.did[:34]}…")


# ---- each hand carries one REAL skill: the floor itself, read governed & free ----------
def pulse_skill(_q: str) -> str:
    h = call("GET", "/health")
    return f"the floor holds {h.get('records', '?')} memories; high water {str(h.get('high_water', ''))[:19]}"


def toolshed_skill(_q: str) -> str:
    svcs = [s for s in call("GET", "/farm").get("services", []) if s.get("state") == "serving"]
    return ("tools serving: " + ", ".join(s["name"] for s in svcs)) if svcs else "the toolshed is quiet"


def stable_skill(_q: str) -> str:
    stalls = call("GET", "/stable").get("stalls", [])
    live = [s for s in stalls if s.get("state") in ("available", "canaried")]
    return (f"{len(live)} mind(s) serving: " + ", ".join(s["id"] for s in live)) \
        if live else "no minds saddled on this floor"


CREW = [
    ("wren", "take the floor's pulse", "pulse", pulse_skill),
    ("moss", "walk the toolshed and name what serves", "toolshed", toolshed_skill),
    ("flint", "read the stable's ladder", "stable", stable_skill),
]


def main() -> None:
    say("\n═══ THE CREW — a field takes on hands, and every hand is a self ═══\n")

    agents: list[tuple[FieldClient, str, str, object]] = []
    for name, objective, skill_name, skill in CREW:
        returning = (Path.home() / ".orreth" / "agents" / name).exists()
        agent = FieldClient(BASE, name, role="workforce")
        say(f"── {name} {'returns — the same seed, the same self (reboot ≠ death)' if returning else 'knocks for the first time'} ──")
        admit(agent)
        agents.append((agent, objective, skill_name, skill))
    say()

    say("── the crew works: one governed objective each, on deterministic cognition ──")
    for agent, objective, skill_name, skill in agents:
        think = RuleThink({skill_name: skill})
        out = Chassis(agent, think, persona=f"You are {agent.name}, workforce on {agent.scope}.",
                      skills={skill_name: skill}, max_cycles=2).run(objective)
        say(f"  {agent.name} · “{objective}” → {out['status'].upper()}"
            f" in {out.get('cycles', '?')} cycle(s)")
        if out.get("answer"):
            say(f"      {out['answer'][:96]}", 0.3)
    say()

    say("── the roster, read back off the floor ──")
    p = call("GET", "/presence")
    crew = [w for w in p.get("workforce", []) if w.get("name") in {c[0] for c in CREW}]
    for w in crew:
        say(f"  ◈ {w.get('name')} · {str(w.get('agent', ''))[:30]}… — on the roster, on the record")
    say(f"\n  {len(crew)} hands on deck. Ships in orbit — open the Console and watch them turn.")
    say("  Every join proven at the gate, every thought a signed RunRecord, every")
    say("  identity a seed that survives the process. The workforce is real. 🥂\n")


if __name__ == "__main__":
    main()
