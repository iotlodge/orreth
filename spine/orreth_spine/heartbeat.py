# PROVENANCE: Claude Fable 5 (claude-fable-5) — rearch P0 sp1, the rig breathes · 2026-09-16
"""The rig's first breath: one envelope through each rail, bytes exact.

Run it with the spine rig up (`docker compose up -d` in spine/):

    uv run python -m orreth_spine.heartbeat

It prints a plain-words report and exits non-zero if any rail failed —
no silent success, no swallowed failure.
"""
from __future__ import annotations

import sys

from . import envelope as ev
from . import rails

UNIVERSE = "u:dev"
SCOPE = "u:dev"


def _beat(kind: str, rail_name: str) -> dict:
    return ev.make_envelope(
        kind=kind, type="orreth.heartbeat.v1",
        universe_id=UNIVERSE, scope_path=SCOPE,
        payload={"ref": f"heartbeat:{rail_name}",
                 "hash": ev.content_hash({"rail": rail_name})},
        authority_chain=["did:orreth:person:jb", "did:orreth:agent:fable"])


def main() -> int:
    checks = [
        ("ground", "postgres", rails.ground_breath, _beat("event", "ground"),
         "heartbeat + outbox in one transaction, bytes exact"),
        ("invoke", "rabbitmq", rails.invoke_breath, _beat("command", "invoke"),
         "published with confirms, consumed, acked, bytes exact"),
        ("events", "kafka", rails.events_breath, _beat("event", "events"),
         "produced, read back from the log, bytes exact"),
    ]
    print("the rig draws its first breath\n")
    failed = False
    for rail, product, fn, env, meaning in checks:
        try:
            ms = fn(env)
            print(f"  {rail:<7} {product:<9} ✓  {ms:7.1f} ms   ({meaning})")
        except Exception as e:  # noqa: BLE001 — the report IS the handler
            failed = True
            print(f"  {rail:<7} {product:<9} ✗  {type(e).__name__}: {e}")
    print()
    if failed:
        print("the rig is not breathing — fix the rail above before anything else")
        return 1
    print("the rig breathes.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
