# PROVENANCE: authored by Opus 4.8 (2026-07-05), pending Fable 5 review — see agents/PROVENANCE.md
"""Deterministic skills — the free, instant half of the nucleus's duality (0015).

A skill is a plain callable `(question, client) -> str`. Deterministic, keyless, and
fast: the planner reaches for these before it ever spends a model token. Register a new
one here and name it in agent.yaml — that is the whole extension surface for Flavor 1.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone


def clock(question: str, client) -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def field_stats(question: str, client) -> str:
    """The floor's living numbers, straight from the roll-up (0005)."""
    ro = client._call("GET", "/rollup")[1]
    return (f"{ro.get('memories', 0)} memories · {ro.get('runs', 0)} thoughts · "
            f"{ro.get('success_rate', 0)}% success · {ro.get('tokens', 0)} tokens")


def recent_memory(question: str, client) -> str:
    """What the agent itself has lived lately — its own biography through the window."""
    hits = client.recall(days=30).get("hits", [])[:3]
    if not hits:
        return "no memories yet in the last 30 days"
    return "; ".join(f"{h['occurred_at'][:10]} {h.get('fidelity','?')}" for h in hits)


def world_shape(question: str, client) -> str:
    """What this floor knows below it — ecosystems, fields, agents (presence rolls up)."""
    t = client._call("GET", "/topology")[1]

    def count(node, acc):
        for c in node.get("children", []):
            depth = c["scope"].count("/")
            acc["eco" if depth == 1 else "field"] = acc.get("eco" if depth == 1 else "field", 0) + 1
            acc["agents"] = acc.get("agents", 0) + c.get("agents", 0)
            count(c, acc)
        return acc

    acc = count(t, {})
    return f"{acc.get('eco',0)} ecosystems · {acc.get('field',0)} fields · {acc.get('agents',0)} agents below"


REGISTRY = {
    "clock": clock,
    "field_stats": field_stats,
    "recent_memory": recent_memory,
    "world_shape": world_shape,
}


def bind(names: list[str], client) -> dict:
    """Turn a list of skill names into the `{name: callable(question)}` dict the Chassis wants."""
    out = {}
    for n in names:
        fn = REGISTRY.get(n)
        if fn is not None:
            out[n] = (lambda f: lambda q: f(q, client))(fn)
    return out
