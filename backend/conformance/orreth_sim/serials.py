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
delivery is log while news wears the medium marker (0024).

The difference is the news (spoonful 3, §3): a subscribed ref re-speaking with
CHANGED content is a contradiction candidate detected by identity, never meaning —
the new claim admits quarantined, the old head drops to 'investigating' with the
trigger 'superseded-at-source' and the pair named; a ref the sweep no longer
carries is VANISHED — absence is a finding, noted and never acted on."""
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


# ---------------------------------------------------------------- the charter coupling (0032 §4)

_ACQUIRE = ("acquire knowledge of ", "acquire knowledge on ",
            "acquire knowledge about ")


def keep_fresh_offer(objective_text: str) -> dict | None:
    """0032 §4: an acquisition-shaped objective (0030's ladder — "acquire
    knowledge of Y") may carry the offer "…and keep it fresh" on its staged
    plan, plainly worded, unchecked by default (§8's proposal). None for every
    other shape — the offer is never pressed on a plan it doesn't fit."""
    t = (objective_text or "").strip()
    low = t.lower()
    for p in _ACQUIRE:
        if low.startswith(p):
            topic = t[len(p):].strip().strip("?.!")
            if topic:
                return {"topic": topic,
                        "terms": "every 100 beats · 4 call(s) per delivery"}
    return None


def named_supply(subs: list[dict], domain_topic: str) -> str:
    """0032 §4: the domain package names its subscription — the package and its
    supply line, one picture. Empty when no deliver-posture subscription stands
    for the topic (a paused desk is not a supply line)."""
    want = slug(domain_topic)
    for s in subs:
        if s.get("posture") == "deliver" and slug(s.get("topic", "")) == want:
            return f" · kept fresh — every {s.get('cadence_beats', '?')} beats"
    return ""


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


def dedup(findings: list[dict], held: list[dict],
          source_did: str | None = None) -> dict:
    """0032 §2–§3's sorting table, pure — by identity, never meaning. A content
    match is a repeat (same voice twice is still one voice, 0014); a finding at
    a ref the shelf already cites, saying something else, is CHANGED — the
    contradiction candidate (§3), its old heads named in `supersedes`; everything
    else is new. Held claims from the subscribed voice whose refs this sweep no
    longer carries are VANISHED — absence is a finding, noted and never acted on.
    `held` rows are {id, claim, ref, source_did}."""
    by_claim: dict = {}
    for h in held:
        by_claim.setdefault(str(h.get("claim", "")).strip(), []).append(h)
    parts: dict = {"new": [], "repeat": [], "changed": [], "vanished": []}
    seen_refs, matched = set(), set()
    for f in findings:
        claim, ref = str(f.get("claim", "")).strip(), str(f.get("ref", ""))
        if ref:
            seen_refs.add(ref)
        if claim in by_claim:
            parts["repeat"].append(f)
            matched.update(h.get("id") for h in by_claim[claim])
            continue
        olds = [h for h in held if h.get("ref") and h["ref"] == ref
                and str(h.get("claim", "")).strip() != claim]
        if olds:
            parts["changed"].append({**f, "supersedes": [h["id"] for h in olds]})
            matched.update(h["id"] for h in olds)
        else:
            parts["new"].append(f)
    for h in held:
        if h.get("id") in matched or not h.get("ref"):
            continue
        if source_did and h.get("source_did") != source_did:
            continue                          # only the subscribed voice can go quiet
        if h["ref"] not in seen_refs:
            parts["vanished"].append({"claim": str(h.get("claim", "")),
                                      "ref": h["ref"], "id": h.get("id")})
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
        "changed": [{"claim": str(f.get("claim", ""))[:120],
                     "supersedes": list(f.get("supersedes") or [])}
                    for f in parts.get("changed", [])],
        "vanished": [{"claim": str(v.get("claim", ""))[:120],
                      "ref": str(v.get("ref", ""))}
                     for v in parts.get("vanished", [])],
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


def held_claims(node, topic: str) -> list[dict]:
    """The domain's live claims on a topic — heads only, the recalled excluded
    (the dead never answer, 0022 §4). What the dedup measures arrivals against:
    {id, claim, ref, source_did} rows, the identity the §3 detection runs on."""
    rows = [(rid, r, _body(r)) for rid, r in node.records.items()
            if "knowledge" in r.get("tags", [])]
    superseded = {d for _, r, _ in rows for d in r.get("derived_from", [])}
    return [{"id": rid, "claim": str(b.get("knowledge", "")),
             "ref": str((b.get("source") or {}).get("ref", "")),
             "source_did": str((b.get("source") or {}).get("did", ""))}
            for rid, r, b in rows
            if rid not in superseded and b.get("intent") == topic
            and b.get("state") != "recalled"]


def _admit(node, agent: dict, kp, scope: str, topic: str, sub_id: str,
           f: dict) -> str | None:
    """One arrival through the door: quarantined at 0.0000, the subscription in
    its lineage. None when the universe already holds this exact utterance —
    content-addressed, a repeat is never a re-write."""
    body = {"knowledge": str(f.get("claim", "")),
            "source": {"did": str(f.get("source_did", "")),
                       "ref": str(f.get("ref", ""))},
            "state": "untrusted", "intent": topic,
            "subscription": sub_id}
    rec = make_memory(agent, kp, scope, body, kind="semantic",
                      tags=["knowledge", "delivered", slug(topic)],
                      provenance_class="ingested-archive")
    if rec["id"] in node.records:
        return None
    rec["derived_from"] = [sub_id]
    return node.write(rec)


def supersede(node, agent: dict, kp, scope: str, topic: str, old_id: str,
              new_id: str, ref: str) -> str | None:
    """0032 §3: change at the source is doubt at the shelf. The old head drops
    to 'investigating' — the revalidation walk's own shape (0031 §5), trigger
    'superseded-at-source', the pair named. Idempotent: doubt never stacks, the
    dead stay dead, and nothing auto-supersedes — residents and humans resolve
    which version earns corroboration."""
    old = node.records.get(old_id)
    if old is None:
        return None
    ob = _body(old)
    if ob.get("state") in ("recalled", "investigating"):
        return None
    from .identity import NOW
    nb = {**ob, "state": "investigating",
          "revalidation": {"trigger": "superseded-at-source",
                           "reason": f"“{topic}” changed at its source ({ref}) — "
                                     f"superseded by {new_id}",
                           "at": NOW()}}
    sib = make_memory(agent, kp, scope, nb, kind="semantic",
                      tags=sorted({*old.get("tags", []), "knowledge"}))
    sib["derived_from"] = [old_id]
    return node.write(sib)


def sweep(node, agent: dict, kp, scope: str, *, topic: str,
          findings: list[dict], calls: int = 1,
          source_did: str | None = None) -> dict | None:
    """One delivery, whole (0032 §2–§3): dedup against the shelf, admit the new
    quarantined with the subscription's lineage attached, admit the CHANGED the
    same way while their old heads drop to investigating (the pair named), note
    the vanished, write the note, and grade the lane — medium only when there is
    news. Returns the sweep's report; None when no deliverable subscription
    stands."""
    sub = find(node, topic)
    if sub is None or sub.get("posture") != "deliver":
        return None
    parts = dedup(findings, held_claims(node, topic), source_did=source_did)
    admitted, fresh = [], []
    for f in parts["new"]:
        rid = _admit(node, agent, kp, scope, topic, sub["id"], f)
        if rid is None:
            parts["repeat"].append(f)
            continue
        fresh.append(f)
        admitted.append(rid)
    parts["new"] = fresh
    dropped, changed = [], []
    for f in parts["changed"]:
        rid = _admit(node, agent, kp, scope, topic, sub["id"], f)
        if rid is None:
            parts["repeat"].append(f)
            continue
        admitted.append(rid)
        changed.append(f)
        for old_id in f.get("supersedes") or []:
            sib = supersede(node, agent, kp, scope, topic, old_id, rid,
                            str(f.get("ref", "")))
            if sib:
                dropped.append(sib)
    parts["changed"] = changed
    issue = len(deliveries(node, topic)) + 1
    note = make_delivery_note(agent, kp, scope, sub, issue=issue,
                              parts=parts, calls=calls)
    note_id = node.write(note)
    marker_id = None
    if news(_body(note).get("delivery") or {}):
        mk = markers.make_marker(
            agent, kp, scope, [note_id],
            reason=f"the desk delivered news on “{topic}”: "
                   f"{len(parts['changed'])} changed at source · "
                   f"{len(parts['vanished'])} vanished",
            change_severity="medium")
        marker_id = node.write(mk)
    return {"note": note_id, "issue": issue, "admitted": admitted,
            "arrived": len(parts["new"]), "repeated": len(parts["repeat"]),
            "changed": len(parts["changed"]), "vanished": len(parts["vanished"]),
            "dropped": dropped, "marker": marker_id}
