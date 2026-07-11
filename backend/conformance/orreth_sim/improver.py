# PROVENANCE: authored by Fable 5 (claude-fable-5), 2026-07-11 — 0028, the Improvement Engine
"""The Improvement Engine (0028 §2): one agent, always improving — from receipts.

The improver reads outcome evidence (rollups, critic markers, parked intents),
proposes a NEW VERSION of a behavioral asset (a sibling, never a silent successor —
0011's law applied to assets), and never grades itself: the governance seat computes
the change kind by DIFFING the versions and authors the critic marker (JB lock
2026-07-11); the R6 lanes route adoption — a nudge is medium (co-review + notify,
adopted with a loud record), a rewrite is high (waits for the human). The whole
chain is receipts: evidence → proposal → grade → adoption.
"""
from __future__ import annotations

from . import factory, markers
from .node import make_memory

# JB lock 2026-07-11: bounded parameters ride medium; anything else is a rewrite
NUDGE_KEYS = {"max_cycles", "max_obs", "ladder", "success_floor"}
LANES = {"nudge": "medium", "rewrite": "high"}


def make_asset(agent: dict, kp, scope: str, *, name: str, profile: dict,
               derived_from: list | None = None, tag: str = "asset",
               adopted_from: str | None = None) -> dict:
    """A behavioral asset as a versioned artifact in memory (R8): content-addressed
    body, lineage through derived_from, never rewritten. An ADOPTION names the
    proposal in its body — adoption is new content, so its id can never collide
    with the proposal it succeeds (ids cover the body alone)."""
    body: dict = {"asset": {"name": name, "profile": profile}}
    if adopted_from:
        body["asset"]["adopted_from"] = adopted_from
    rec = make_memory(agent, kp, scope, body, kind="semantic", tags=[tag, name])
    if derived_from:
        rec["derived_from"] = list(derived_from)
    return rec


def _asset_rows(node, name: str, tag: str) -> list[tuple[str, dict]]:
    rows = [(rid, r) for rid, r in node.records.items()
            if tag in r.get("tags", []) and name in r.get("tags", [])]
    return sorted(rows, key=lambda x: x[1]["received_at"])


def active_asset(node, name: str) -> tuple[str, dict] | None:
    """The newest adopted version — history stays whole behind it."""
    rows = _asset_rows(node, name, "asset")
    return rows[-1] if rows else None


def open_proposal(node, name: str) -> str | None:
    """One open proposal per asset (0028 §4 — no proposal storms): a proposal is
    open until an adopted version derives from it. A high-graded proposal waiting
    for the human HOLDS the lane — that is the rule working, not a bug."""
    adopted_from = {d for _, r in _asset_rows(node, name, "asset")
                    for d in r.get("derived_from", [])}
    for rid, _ in reversed(_asset_rows(node, name, "asset-proposal")):
        if rid not in adopted_from:
            return rid
    return None


def evidence(node, *, goal_hash: str | None = None, keep: int = 6) -> dict:
    """Receipts, never vibes (0005): the runs' success shape, the reviews that
    graded medium or worse, the breaker's parked intents — with the record refs
    a proposal must cite."""
    runs = [r for r in node.runs.values()
            if goal_hash is None or r["goal_hash"] == goal_hash]
    ok = sum(1 for r in runs if r["outcome"] == "success")
    refs, heavy = [], 0
    for rid, r in node.records.items():
        tags = r.get("tags", [])
        if "marker" in tags or ("parked" in tags and "knowledge-intent" in tags):
            refs.append(rid)
            if "marker" in tags:
                heavy += 1      # graded reviews count against health, whatever the lane
    parked = sum(1 for _, r in node.records.items()
                 if "parked" in r.get("tags", []) and "knowledge-intent" in r.get("tags", []))
    return {"runs": len(runs),
            "success_rate": int(100 * ok / len(runs)) if runs else 100,
            "reviews": heavy, "parked": parked, "refs": refs[-keep:]}


def classify_change(old_profile: dict, new_profile: dict) -> str:
    """Computed by diff, never declared by the proposer (JB lock 2026-07-11):
    touching only bounded parameters is a nudge; touching persona, prompts, or
    shape is a rewrite — the human's lane."""
    changed = {k for k in set(old_profile) | set(new_profile)
               if old_profile.get(k) != new_profile.get(k)}
    return "nudge" if changed and changed <= NUDGE_KEYS else "rewrite"


class Improver:
    """One improver on the universe floor (JB lock 2026-07-11): a standing
    incarnation (R8, 0027's machinery) with no completion condition, reading the
    subtree's risen evidence. It PROPOSES; it never grades, never adopts alone."""

    def __init__(self, home, becky, *, archetype: dict | None = None,
                 budget_tokens: int = 1200):
        arch = archetype or becky.issue_identity("archetype", home.scope)[0]
        [self.surface] = factory.stamp(home, becky, arch, 1,
                                       generation="standing-improver",
                                       budget_tokens=budget_tokens)
        self.home = home

    def beat(self, asset_name: str, *, success_floor: int = 90) -> str | None:
        """One look at the receipts: a healthy asset is left alone; a weak one
        earns a bounded parameter nudge, proposed as a sibling version citing the
        evidence. One open proposal per asset — the lane holds until it resolves."""
        found = active_asset(self.home, asset_name)
        if found is None or open_proposal(self.home, asset_name):
            return None
        rid, rec = found
        ev = evidence(self.home)
        if ev["success_rate"] >= success_floor and not ev["parked"]:
            return None                     # healthy assets are left alone
        import json

        from . import crypto
        profile = json.loads(crypto._b64d(rec["body"]).decode())["asset"]["profile"]
        nudged = dict(profile)
        nudged["max_cycles"] = min(int(profile.get("max_cycles", 2)) + 1, 5)
        if nudged == profile:
            return None                     # the dial is at its stop — nothing to propose
        me = {"did": self.surface.identity["did"], "scope": self.home.scope}
        proposal = make_asset(me, self.surface.kp, self.home.scope,
                              name=asset_name, profile=nudged,
                              derived_from=[rid, *ev["refs"]],
                              tag="asset-proposal")
        return self.home.write(proposal)


def grade(node, reviewer: dict, reviewer_kp, proposal_id: str) -> dict:
    """The governance seat's duty (author ≠ proposer): diff the proposal against
    the active version, compute the kind, grade the lane — a marker on the record
    (0024), amber in the glass when it waits."""
    import json

    from . import crypto
    prop = node.records[proposal_id]
    name = next(t for t in prop["tags"] if t != "asset-proposal")
    new_profile = json.loads(crypto._b64d(prop["body"]).decode())["asset"]["profile"]
    found = active_asset(node, name)
    old_profile = json.loads(crypto._b64d(found[1]["body"]).decode())["asset"]["profile"] \
        if found else {}
    if new_profile == old_profile:
        raise ValueError("an unchanged profile is not a proposal — nothing to grade")
    kind = classify_change(old_profile, new_profile)
    sev = LANES[kind]
    mk = markers.make_marker(reviewer, reviewer_kp, node.scope, [proposal_id],
                             reason=f"improvement proposal for {name}: {kind}",
                             change_severity=sev)
    node.write(mk)
    return {"kind": kind, "severity": sev, "marker": mk["id"], "asset": name}


def adopt(node, agent: dict, kp, proposal_id: str, graded: dict, *,
          human_approved: bool = False) -> str | None:
    """The lanes route (R6, JB lock): medium adopts with a loud record — the
    adoption derives from the proposal AND its grade, the whole chain receipted;
    high refuses until the human approves — consequence waits (0012)."""
    if graded["severity"] == "high" and not human_approved:
        return None                         # the human's lane — silence never adopts
    import json

    from . import crypto
    prop = node.records[proposal_id]
    profile = json.loads(crypto._b64d(prop["body"]).decode())["asset"]["profile"]
    adopted = make_asset(agent, kp, node.scope, name=graded["asset"],
                         profile=profile, adopted_from=proposal_id,
                         derived_from=[proposal_id, graded["marker"]])
    return node.write(adopted)
