# PROVENANCE: Fable 5 (claude-fable-5) — the lease learns to renew · 2026-08-22
"""The fuel law's judgment half — reading the plane's usage rows for postures.

The plane enforces (orrethd model.rs: the window refills the allowance, on the
meter_log); this module JUDGES — which subject is drained, what the card at the
human's gate should say, and what key keeps one card per subject per window.
Born of 0058's named wound: vera drained to 419 of 50k tokens and the
examiner's refusals wore the uniform face for days — "the ground is missing"
was "the examiner is broke". The silence must be loud at the gate, never
discovered by archaeology.
"""
from __future__ import annotations

# A lease that cannot clear one typical governed thought is drained, whatever
# positive dust remains — the worker's own estimates run ~40 (a canary ping)
# to ~500+ (a voiced reply carrying its prompt freight). The wound's own
# number, 419, must fall on the drained side of this line.
EST_FLOOR = 500


def posture(row: dict, now: str | None = None, *,
            est_floor: int = EST_FLOOR) -> str:
    """One /model/usage row -> its fuel posture.

    fueled   — the lease clears a typical thought, OR its window has already
               turned (the plane renews lazily at the next debit: a past
               renews_at means the next ask refills — nothing to card)
    drained  — a renewing lease out of allowance mid-window (rests until
               renews_at; early drain is NEWS, not physics)
    lump-dry — the old clause: no window, out forever without a human word
    unknown  — no ledger entry yet (never carded; nothing to say)
    """
    remaining = row.get("remaining")
    if remaining is None:
        return "unknown"
    if remaining >= est_floor:      # the human's word may move the line (0063)
        return "fueled"
    fuel = row.get("fuel") or {}
    if (fuel.get("renew_days") or 0) > 0:
        renews_at = str(fuel.get("renews_at") or "")
        if now and renews_at and renews_at <= now:
            return "fueled"      # already healed — the ledger just hasn't been asked
        return "drained"
    return "lump-dry"


def drain_cards(rows: list[dict], names: dict[str, str] | None = None,
                now: str | None = None, *,
                est_floor: int = EST_FLOOR) -> list[dict]:
    """The cards a drain watch should file — one per dry subject, keyed by its
    window so a NEW window's early drain cards again while the old decline
    stays honored. The card informs; the human's word stays the door (0012)."""
    names = names or {}
    cards = []
    for row in rows:
        p = posture(row, now=now, est_floor=est_floor)
        if p not in ("drained", "lump-dry"):
            continue
        fuel = row.get("fuel") or {}
        did = str(row.get("subject") or "")
        who = names.get(did) or f"{did[:22]}…"
        spent = row.get("tokens") or 0
        if p == "drained":
            text = (f"{who} drained its {fuel.get('allowance', '?')}-token "
                    f"window early ({spent} spent all-time) — replenish now, "
                    f"or it rests until the window turns at "
                    f"{fuel.get('renews_at', '?')}")
        else:
            text = (f"{who} is dry on a lump lease ({fuel.get('allowance', '?')}"
                    f" tokens, no renewal window) — it stays silent until a "
                    f"human word replenishes it")
        cards.append({"kind": "fuel", "action": "replenish", "did": did,
                      "name": names.get(did, ""), "posture": p,
                      "window": fuel.get("window_started", ""), "text": text})
    return cards
