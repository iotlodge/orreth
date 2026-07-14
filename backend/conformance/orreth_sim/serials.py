# PROVENANCE: authored by Fable 5 (claude-fable-5), 2026-07-14 — 0032, the Serials Desk
"""The Serials Desk (0032 §1): a subscription is the human's standing word.

Config-as-memory (R8): a signed, content-addressed record committing the universe
to standing spend — which is why it only ever mints FROM a human-approved ask
(consequence waits, 0012 — a recurring bill is a consequence). Cancellation is a
new version on the worldline, never an absence; out of fuel it will pause, never
vanish (0009 — the beat arrives with spoonful 2)."""
from __future__ import annotations

import json
import re

from . import crypto
from .node import make_memory

POSTURES = ("deliver", "paused", "cancelled")


def slug(topic: str) -> str:
    """A stable tag for the topic — the desk's index key."""
    return "sub-" + re.sub(r"[^a-z0-9]+", "-", (topic or "").lower()).strip("-")[:48]


def make_subscription(agent: dict, kp, scope: str, *, topic: str,
                      approved_ref: str, sources: str | list = "any-serving",
                      cadence_beats: int = 100, budget_calls: int = 4) -> dict:
    """The record the human's approval mints (0032 §1): terms visible, posture
    deliver, the approving ask named — a subscription never self-mints."""
    body = {"subscription": {
        "topic": topic, "sources": sources,
        "cadence_beats": int(cadence_beats),
        "budget": {"calls": int(budget_calls)},
        "posture": "deliver", "approved": approved_ref,
    }}
    return make_memory(agent, kp, scope, body, kind="semantic",
                       tags=["subscription", slug(topic)])


def _body(rec: dict) -> dict:
    return json.loads(crypto._b64d(rec["body"]).decode()) if "body" in rec else {}


def subscriptions(node) -> list[dict]:
    """The desk's ledger: the current head per topic — cancelled ones shown with
    their posture, because retired is a state, not an absence."""
    rows = [(rid, r) for rid, r in node.records.items()
            if "subscription" in r.get("tags", [])]
    rows.sort(key=lambda x: x[1]["received_at"])
    superseded = {d for _, r in rows for d in r.get("derived_from", [])}
    out = []
    for rid, r in rows:
        if rid in superseded:
            continue
        sub = _body(r).get("subscription") or {}
        out.append({"id": rid, **sub})
    return sorted(out, key=lambda s: s.get("topic", ""))


def find(node, topic: str) -> dict | None:
    """The current head for a topic, by its slug."""
    want = slug(topic)
    heads = [s for s in subscriptions(node)
             if slug(s.get("topic", "")) == want]
    return heads[-1] if heads else None


def set_posture(node, agent: dict, kp, topic: str, posture: str, *,
                reason: str = "") -> str | None:
    """A posture change is a sibling version deriving from the head (0011's law
    applied to the desk): cancel · pause · resume — the worldline keeps every
    state the subscription ever held."""
    if posture not in POSTURES:
        raise ValueError(f"unknown posture: {posture!r}")
    head = find(node, topic)
    if head is None:
        return None
    body = {"subscription": {**{k: v for k, v in head.items() if k != "id"},
                             "posture": posture,
                             **({"reason": reason} if reason else {})}}
    rec = make_memory(agent, kp, node.scope, body, kind="semantic",
                      tags=["subscription", slug(head.get("topic", ""))])
    rec["derived_from"] = [head["id"]]
    return node.write(rec)
