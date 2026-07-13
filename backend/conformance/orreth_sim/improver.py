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

# 0031 §4 — the shelf made whole: the chassis prompts leave the code and live here
PROMPT_ASSETS = ("prompt-plan", "prompt-critic")


def _body(rec: dict) -> dict:
    import json

    from . import crypto
    return json.loads(crypto._b64d(rec["body"]).decode())


def _profile_of(rec: dict) -> dict:
    return (_body(rec).get("asset") or {}).get("profile") or {}


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
    open until an adoption OR a decline derives from it. A high-graded proposal
    waiting for the human HOLDS the lane — that is the rule working, not a bug;
    a declined one releases it (0031 §4 — a refusal never dams the river)."""
    closed = {d for tag in ("asset", "asset-decline")
              for _, r in _asset_rows(node, name, tag)
              for d in r.get("derived_from", [])}
    for rid, _ in reversed(_asset_rows(node, name, "asset-proposal")):
        if rid not in closed:
            return rid
    return None


def decline(node, agent: dict, kp, proposal_id: str, *,
            reason: str = "declined by the human") -> str:
    """The human's no is a record too (0031 §4): the decline derives from the
    proposal it closes, the reason rides in the body, and the asset's lane opens
    again. The proposal itself is never rewritten — history stays whole."""
    prop = node.records[proposal_id]
    name = next(t for t in prop["tags"] if t != "asset-proposal")
    rec = make_memory(agent, kp, node.scope,
                      {"decline": {"asset": name, "proposal": proposal_id,
                                   "reason": (reason or "")[:200]}},
                      kind="semantic", tags=["asset-decline", name])
    rec["derived_from"] = [proposal_id]
    return node.write(rec)


def feedback(node, agent: dict, kp, name: str, words: str) -> str:
    """The feedback door (0031 §4): the human's words land VERBATIM against the
    asset's active version (0024's quoting discipline), tagged so evidence() must
    carry them on the improver's next beat. Feedback is evidence, never an
    auto-trigger — the smith still decides on her own beat (v0, JB may re-lock)."""
    rec = make_memory(agent, kp, node.scope,
                      {"feedback": {"asset": name, "quoted": (words or "")[:400]}},
                      kind="semantic", tags=["asset-feedback", name])
    found = active_asset(node, name)
    if found:
        rec["derived_from"] = [found[0]]
    return node.write(rec)


def seed_prompts(node, agent: dict, kp) -> dict:
    """Genesis for the prompt shelf (0031 §4): the chassis constants leave the
    code as version one — from here every change is a sibling on the record, and
    a prompt is behavior the lanes can finally govern (a template change is not
    in NUDGE_KEYS: the diff grades it a rewrite, the human's lane)."""
    from .chassis import _CRITIC, _PLAN
    out = {}
    for name, text in (("prompt-plan", _PLAN), ("prompt-critic", _CRITIC)):
        if active_asset(node, name) is None:
            rid = node.write(make_asset(agent, kp, node.scope, name=name,
                                        profile={"template": text}))
            out[name] = rid
    return out


def resolve_behavior(node, name: str = "fingertip-default") -> dict:
    """The shelf speaks at dispatch (0031 §2·§4): the fingertip's chassis runs
    under the ACTIVE versions — profile dials and prompt templates — so an
    adoption changes the next run, not just the record. The versions resolved
    here are the aperture's behavior pins (spoonful 2 will sign them)."""
    out: dict = {"profile": {}, "plan_template": None, "critic_template": None,
                 "versions": {}}
    found = active_asset(node, name)
    if found:
        out["profile"] = _profile_of(found[1])
        out["versions"][name] = found[0]
    for pname, key in (("prompt-plan", "plan_template"),
                       ("prompt-critic", "critic_template")):
        f = active_asset(node, pname)
        if f:
            out[key] = _profile_of(f[1]).get("template") or None
            out["versions"][pname] = f[0]
    return out


def shelf(node) -> list[dict]:
    """One shelf, every behavioral asset (0031 §4): versions, the active head,
    the open proposal holding a lane, and the human's feedback count — the
    Workshop's list panel, composed from records alone."""
    names: dict[str, dict] = {}
    for _rid, r in node.records.items():
        tags = r.get("tags", [])
        kind = next((t for t in ("asset-proposal", "asset-feedback",
                                 "asset-decline", "asset") if t in tags), None)
        if kind is None:
            continue
        name = next((t for t in tags if t != kind), None)
        if name is None:
            continue
        row = names.setdefault(name, {"name": name, "versions": 0,
                                      "proposals": 0, "feedback": 0})
        key = {"asset": "versions", "asset-proposal": "proposals",
               "asset-feedback": "feedback"}.get(kind)
        if key:
            row[key] += 1
    for row in names.values():
        found = active_asset(node, row["name"])
        row["active"] = found[0] if found else None
        row["open"] = open_proposal(node, row["name"])
    return sorted(names.values(), key=lambda r: r["name"])


def version_walk(node, name: str) -> list[dict]:
    """The whole chain, oldest → active (0031 §4): every version, the keys it
    changed, the proposal it was adopted from, and the grade that judged it —
    evidence → proposal → grade → adoption, walked and readable."""
    marks = [(mid, m) for mid, m in node.records.items()
             if "marker" in m.get("tags", [])]
    walk, prev = [], {}
    for rid, r in _asset_rows(node, name, "asset"):
        body = _body(r).get("asset") or {}
        prof = body.get("profile") or {}
        changed = sorted(k for k in set(prev) | set(prof)
                         if prev.get(k) != prof.get(k))
        entry = {"id": rid, "at": r.get("received_at", ""),
                 "author": r.get("author", ""), "changed": changed}
        adopted_from = body.get("adopted_from")
        if adopted_from:
            entry["adopted_from"] = adopted_from
            for _mid, m in marks:
                if adopted_from in m.get("derived_from", []):
                    mk = _body(m).get("marker") or {}
                    entry["grade"] = {"severity": mk.get("change_severity"),
                                      "reason": mk.get("reason")}
                    break
        walk.append(entry)
        prev = prof
    return walk


def approval_package(node, proposal_id: str) -> dict:
    """What the human reads before signing (0031 §4): the computed diff (never
    the proposer's claim), the receipts resolved to readable lines, and the
    rollback that was never needed — the prior version stands, whatever you
    decide. HITL reviews a checked candidate, not raw output."""
    prop = node.records[proposal_id]
    name = next(t for t in prop["tags"] if t != "asset-proposal")
    new_prof = _profile_of(prop)
    found = active_asset(node, name)
    old_prof = _profile_of(found[1]) if found else {}
    changed = sorted(k for k in set(old_prof) | set(new_prof)
                     if old_prof.get(k) != new_prof.get(k))
    receipts = []
    for ref in prop.get("derived_from", []):
        r = node.records.get(ref)
        if r is None:
            receipts.append({"ref": ref, "what": "a record beyond this floor"})
            continue
        tags = r.get("tags", [])
        if "asset" in tags:
            what = "the version this proposal succeeds"
        elif "asset-feedback" in tags:
            fb = _body(r).get("feedback") or {}
            what = f"the human's words: “{fb.get('quoted', '')[:80]}”"
        elif "marker" in tags:
            mk = _body(r).get("marker") or {}
            what = f"a graded review — {mk.get('reason', '')[:80]}"
        elif "parked" in tags:
            what = "a parked intent — the breaker fired"
        else:
            what = "cited evidence"
        receipts.append({"ref": ref, "what": what})
    kind = classify_change(old_prof, new_prof) if changed else "no-op"
    return {"asset": name, "kind": kind,
            "lane": LANES.get(kind, "refused"),
            "changed": {k: {"from": old_prof.get(k), "to": new_prof.get(k)}
                        for k in changed},
            "receipts": receipts,
            "rollback": found[0] if found else None,
            "checks": {"no_op": not changed,
                       "cites_active": bool(found and found[0] in
                                            prop.get("derived_from", []))}}


def evidence(node, *, goal_hash: str | None = None, keep: int = 6) -> dict:
    """Receipts, never vibes (0005): the runs' success shape, the reviews that
    graded medium or worse, the breaker's parked intents — with the record refs
    a proposal must cite."""
    runs = [r for r in node.runs.values()
            if goal_hash is None or r["goal_hash"] == goal_hash]
    ok = sum(1 for r in runs if r["outcome"] == "success")
    refs, heavy, voices = [], 0, 0
    for rid, r in node.records.items():
        tags = r.get("tags", [])
        if "marker" in tags or "asset-feedback" in tags or \
                ("parked" in tags and "knowledge-intent" in tags):
            refs.append(rid)
            if "marker" in tags:
                heavy += 1      # graded reviews count against health, whatever the lane
            elif "asset-feedback" in tags:
                voices += 1     # the human spoke (0031 §4) — evidence, on the record
    parked = sum(1 for _, r in node.records.items()
                 if "parked" in r.get("tags", []) and "knowledge-intent" in r.get("tags", []))
    return {"runs": len(runs),
            "success_rate": int(100 * ok / len(runs)) if runs else 100,
            "reviews": heavy, "parked": parked, "feedback": voices,
            "refs": refs[-keep:]}


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
