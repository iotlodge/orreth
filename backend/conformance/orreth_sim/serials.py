# PROVENANCE: authored by Fable 5 (claude-fable-5), 2026-07-14 — 0032, the Serials Desk
"""The Serials Desk (0032 §1–§2): a subscription is the human's standing word,
and the delivery beat is the desk's standing duty.

Config-as-memory (R8): a signed, content-addressed record committing the universe
to standing spend — which is why it only ever mints FROM a human-approved ask
(consequence waits, 0012 — a recurring bill is a consequence). Cancellation is a
new version on the worldline, never an absence; out of fuel it will pause, never
vanish (0009).

The beat (spoonful 2): due subscriptions re-gather, DEDUP against the domain's
held claims (content match), admit only what is new — quarantined at 0.0000, the
subscription named in the lineage — and write one signed DELIVERY NOTE per sweep.
The desk delivers; it never decides: a repeat from the subscribed voice refreshes
nothing but the note (same voice twice is still one voice, 0014), and a quiet
delivery is log while news wears the medium marker (0024)."""
from __future__ import annotations

import json
import re

from . import crypto, markers
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


# ---------------------------------------------------------------- the delivery beat (0032 §2)

def is_due(sub: dict, waited_beats: int, delivered_before: bool) -> bool:
    """The cadence check, pure: a subscription in the deliver posture is due when
    its cadence has elapsed — and the FIRST issue arrives with the subscription
    itself (a serials desk starts you on the current issue, not the next one).
    Paused and cancelled desks are never due; hibernation is a posture (0009)."""
    if sub.get("posture") != "deliver":
        return False
    if not delivered_before:
        return True
    return waited_beats >= int(sub.get("cadence_beats", 100))


def dedup(findings: list[dict], held_claims: list[str]) -> dict:
    """0032 §2's sorting table, pure — content match against the domain's held
    claims. New goes to admission; a repeat goes only onto the note: the desk can
    never promote its own deliveries (same voice twice is still one voice, 0014).
    The changed and vanished columns arrive with spoonful 3 — the note already
    carries them, empty and honest."""
    held = {c.strip() for c in held_claims}
    parts: dict = {"new": [], "repeat": [], "changed": [], "vanished": []}
    for f in findings:
        parts["repeat" if str(f.get("claim", "")).strip() in held
              else "new"].append(f)
    return parts


def news(delivery: dict) -> bool:
    """The lane (0032 §2 rule 4): the difference is the news — anything in the
    changed or vanished columns wears a medium marker; a quiet delivery is log."""
    return bool(delivery.get("changed") or delivery.get("vanished"))


def make_delivery_note(agent: dict, kp, scope: str, sub: dict, *, issue: int,
                       parts: dict, calls: int) -> dict:
    """One signed record per sweep (0032 §2): what arrived, what repeated, what
    changed, what vanished, what it cost — deriving from the subscription, so the
    desk's worldline is auditable sweep by sweep."""
    body = {"delivery": {
        "topic": sub.get("topic", ""), "subscription": sub["id"], "issue": issue,
        "arrived": [str(f.get("claim", ""))[:120] for f in parts.get("new", [])],
        "repeated": len(parts.get("repeat", [])),
        "changed": [str(f.get("claim", ""))[:120] for f in parts.get("changed", [])],
        "vanished": [str(c)[:120] for c in parts.get("vanished", [])],
        "cost": {"calls": int(calls)},
    }}
    rec = make_memory(agent, kp, scope, body, kind="episodic",
                      tags=["delivery", slug(sub.get("topic", ""))])
    rec["derived_from"] = [sub["id"]]
    return rec


def deliveries(node, topic: str | None = None) -> list[dict]:
    """The desk's sweep history, oldest first — every note the beat ever wrote."""
    want = slug(topic) if topic else None
    rows = [(rid, r) for rid, r in node.records.items()
            if "delivery" in r.get("tags", [])
            and (want is None or want in r.get("tags", []))]
    rows.sort(key=lambda x: x[1]["received_at"])
    return [{"id": rid, **(_body(r).get("delivery") or {})} for rid, r in rows]


def held_claims(node, topic: str) -> list[str]:
    """The domain's live claims on a topic — heads only, the recalled excluded
    (the dead never answer, 0022 §4). What the dedup measures arrivals against."""
    rows = [(rid, r, _body(r)) for rid, r in node.records.items()
            if "knowledge" in r.get("tags", [])]
    superseded = {d for _, r, _ in rows for d in r.get("derived_from", [])}
    return [str(b.get("knowledge", "")) for rid, r, b in rows
            if rid not in superseded and b.get("intent") == topic
            and b.get("state") != "recalled"]


def sweep(node, agent: dict, kp, scope: str, *, topic: str,
          findings: list[dict], calls: int = 1) -> dict | None:
    """One delivery, whole (0032 §2): dedup against the shelf, admit the new
    quarantined with the subscription's lineage attached, write the note, and
    grade the lane — medium only when there is news. Returns the sweep's report;
    None when no deliverable subscription stands."""
    sub = find(node, topic)
    if sub is None or sub.get("posture") != "deliver":
        return None
    parts = dedup(findings, held_claims(node, topic))
    admitted, fresh = [], []
    for f in parts["new"]:
        body = {"knowledge": str(f.get("claim", "")),
                "source": {"did": str(f.get("source_did", "")),
                           "ref": str(f.get("ref", ""))},
                "state": "untrusted", "intent": topic,
                "subscription": sub["id"]}
        rec = make_memory(agent, kp, scope, body, kind="semantic",
                          tags=["knowledge", "delivered", slug(topic)],
                          provenance_class="ingested-archive")
        if rec["id"] in node.records:
            # content-addressed: the universe already holds this exact utterance
            # (a dead lineage's original, say) — a repeat, never a re-write
            parts["repeat"].append(f)
            continue
        rec["derived_from"] = [sub["id"]]
        fresh.append(f)
        admitted.append(node.write(rec))
    parts["new"] = fresh
    issue = len(deliveries(node, topic)) + 1
    note = make_delivery_note(agent, kp, scope, sub, issue=issue,
                              parts=parts, calls=calls)
    note_id = node.write(note)
    marker_id = None
    if news(_body(note).get("delivery") or {}):
        mk = markers.make_marker(agent, kp, scope, [note_id],
                                 reason=f"the desk delivered news on “{topic}”",
                                 change_severity="medium")
        marker_id = node.write(mk)
    return {"note": note_id, "issue": issue, "admitted": admitted,
            "arrived": len(parts["new"]), "repeated": len(parts["repeat"]),
            "marker": marker_id}
