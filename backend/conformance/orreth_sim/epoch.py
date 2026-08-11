# PROVENANCE: Fable 5 (claude-fable-5) — 0041 sim-lift (road step 2) · 2026-07-26
"""The Epoch (0041) — the machinery, lifted into the sim.

Which machine is this floor right now? — answered by a hash, on a chain. The
CanonEpoch is a noticing, never a ceremony: cut only when the fingerprint
moved, held silently when it holds. Drift wears no levers — a Canon that moved
with no adoption behind it becomes a STAGED finding carrying its own revert
target; the human's gate decides, and the yes restores the signed machine as a
new SIBLING (nothing deleted, the drifted head outranked). Two lessons ride as
law: the word is dated by its LANDING, never its submission second (the
req-322 self-accusation, 2026-07-25 — a gate is allowed to wait for its
human), and an unreadable gate is never grounds to accuse in the dark. A point
swearing under an older epoch is LAG — amber and expected to converge, loud at
the gate only when it will not.

Wire twin: console_worker's `_cut_epoch` family (live-proven 2026-07-25); the
sim is the executable spec — same laws, explicit clocks, the head kept on the
shelf itself where every projection can rebuild it.
"""
from __future__ import annotations

import json as _json

from . import crypto as _c
from . import improver
from .identity import NOW
from .node import make_memory

EPOCH_TAG = "canon-epoch"
_ZONES = ("assets", "plane", "worldlines", "floors")

#  the gates that actually move Canon (0041 sp3): improvement (standards,
#  dials, skills, prompts), estate-adopt, field-join, a human's word on a
#  drift card, and the experiment's promotion (0043 sp4 — learned the hard
#  way: the first live rollout was falsely accused because the watchdog's
#  vocabulary was one word short) — a parlor ask is NOT an adoption, so a
#  busy universe never hides drift behind ordinary conversation
ADOPTION_KINDS = ("improvement", "estate-adopt", "field-join", "drift",
                  "experiment",
                  "release",     # Canon change = epoch release (0045 sp3, JB's lock)
                  "craft-edit")  # the one-motion door: the request IS the
#  human's word (0045 sp2), so a sentence/asset edit through it is an
#  adoption by definition — learned 0050 sp2, when thirteen plain-speech
#  siblings drew an honest accusation exactly as «experiment» once did


def _body(r: dict) -> dict:
    return _json.loads(_c._b64d(r["body"]).decode())


def machine_fingerprint(node, *, plane_version: str = "sim",
                        worldlines: dict | None = None) -> dict:
    """The scope's machine, as content (0041 §1): active Canon asset heads +
    the plane's edition + worldline POINTERS — the farm and stable keep their
    own books; the epoch cites where they stood."""
    heads: dict = {}
    for rid, r in sorted(node.records.items(),
                         key=lambda x: x[1].get("received_at", "")):
        tags = r.get("tags") or []
        if "asset" not in tags:
            continue
        name = next((t for t in tags if t != "asset"), None)
        if name:
            heads[name] = rid            # oldest-first — last write is head
    return {"assets": heads, "plane": {"version": plane_version},
            "worldlines": dict(worldlines or {})}


def standing_epoch(node) -> tuple[str, dict] | None:
    """The newest canon-epoch on the shelf — the head is a projection of the
    log, never a side-file only the daemon can read."""
    rows = [(rid, r) for rid, r in node.records.items()
            if EPOCH_TAG in (r.get("tags") or [])]
    if not rows:
        return None
    # stable sort: same-second cuts break toward the later write (lived time
    # is monotone within the log even when the clock's second is not)
    rid, r = sorted(rows, key=lambda x: x[1].get("received_at", ""))[-1]
    return rid, _body(r).get("canon_epoch", {})


def gate_word_recent(requests: list | None, *, now: float,
                     window_s: float = 900.0) -> bool:
    """A CANON ADOPTION resolved near the change. The word is dated by
    `result.resolved_at` — the moment it LANDED — never by the card's
    submission second (the req-322 lesson: dating the word by submission
    turned one slow click into a self-accusing loop that re-adopted the very
    drift it was born to catch). Cards from before the stamp fall back to the
    submission second. An unreadable gate NEVER accuses in the dark."""
    if requests is None:
        return True                      # the dark gate accuses no one
    for r in requests:
        if not isinstance(r, dict) or r.get("status") != "done":
            continue
        if r.get("kind") not in ADOPTION_KINDS:
            continue
        ts = None
        landed = (r.get("result") or {}).get("resolved_at")
        if landed:
            try:
                from datetime import datetime
                ts = datetime.fromisoformat(
                    str(landed).replace("Z", "+00:00")).timestamp()
            except Exception:
                ts = None
        if ts is None:
            try:
                ts = int(str(r.get("id", "")).rsplit("-", 1)[1])
            except Exception:
                continue
        if now - ts < window_s:
            return True
    return False


def cut_epoch(node, agent: dict, kp, *, requests: list | None = None,
              now: float = 0.0, window_s: float = 900.0,
              plane_version: str = "sim", worldlines: dict | None = None,
              floors: dict | None = None,
              pending_revert: dict | None = None) -> dict:
    """THE CUT (0041 §2) — a noticing, never a ceremony. Held when the
    fingerprint holds; a fresh epoch when it moved, its diff on the record.
    Drift class 2: a standing chain whose Canon moved with no adoption near it
    yields a STAGED finding (diff + the pre-drift heads as the revert target)
    — detection wears no levers, the epoch still turns, the gate decides.
    Genesis cuts never accuse (no chain stood before). A revert that just
    landed rides the new epoch as `revert_of` — the citation, kept."""
    fp = machine_fingerprint(node, plane_version=plane_version,
                             worldlines=worldlines)
    if floors is not None:
        fp["floors"] = dict(floors)      # the roll-up cites the floors' heads
    fp_hash = _c.content_hash(fp)
    head = standing_epoch(node)
    old = head[1] if head else {}
    if old.get("fp_hash") == fp_hash:
        return {"id": head[0], "turned": False, "changed": {}, "drift": None}
    changed: dict = {}
    for zone in _ZONES:
        a, b = old.get(zone) or {}, fp.get(zone) or {}
        for k in sorted(set(a) | set(b)):
            if a.get(k) != b.get(k):
                changed[f"{zone}.{k}"] = {"from": a.get(k), "to": b.get(k)}
    body = {"canon_epoch": {"scope": node.scope, "organ": "governance",
                            "parent": head[0] if head else None,
                            "rollback_parent": head[0] if head else None,
                            **({"revert_of": dict(pending_revert)}
                               if pending_revert else {}),
                            **fp, "fp_hash": fp_hash,
                            "changed": changed, "cut_at": NOW()}}
    rec = make_memory(agent, kp, node.scope, body,
                      kind="semantic", tags=[EPOCH_TAG])
    eid = node.write(rec)
    drift = None
    if head and any(k.startswith("assets.") for k in changed) \
            and not gate_word_recent(requests, now=now, window_s=window_s):
        drift = drift_finding(node.scope, changed,
                              "the Canon moved with no adoption behind it")
    return {"id": eid, "turned": True, "changed": changed, "drift": drift}


def drift_finding(scope: str, changed: dict, why: str) -> dict:
    """DRIFT stages a finding (0041 §4, locked: detection wears no levers) —
    the diff rides the card; the `from` head of each changed asset IS the
    pre-drift head, riding as the revert target so the human's yes restores
    the signed machine without walking a single chain."""
    restore = {k.split(".", 1)[1]: (v or {}).get("from")
               for k, v in changed.items()
               if k.startswith("assets.") and (v or {}).get("from")}
    return {"kind": "drift", "scope": scope, "why": why,
            "changed": dict(changed), "restore": restore}


def revert_to_sibling(node, agent: dict, kp, *, name: str, from_ref: str,
                      human_word: bool) -> str:
    """The pre-authorized easy yes (0041 sp4) — on a human's word ONLY, the
    signed head returns as a new SIBLING: adopted_from names the restored
    record, the drifted version stays on the shelf outranked, nothing is
    deleted. Auto-revert was refused at the design gate; it stays refused."""
    if not human_word:
        raise ValueError("the revert moves only on a human's word — "
                         "the gate holds the diff (0041, locked)")
    r = node.records.get(from_ref)
    if r is None:
        raise ValueError("no such head to restore — the revert target must "
                         "stand on the shelf")
    prof = improver._profile_of(r)
    if not prof:
        raise ValueError(f"the target [{from_ref[:18]}…] carries no asset "
                         "profile — nothing to restore")
    sib = improver.make_asset(agent, kp, node.scope, name=name, profile=prof,
                              adopted_from=from_ref, derived_from=[from_ref])
    return node.write(sib)


def reconcile_lag(*, declared: str | None, sworn: str | None, state: dict,
                  now: float, window_s: float = 900.0) -> str:
    """LAG vs convergence (0041 §4): the point swearing under an older epoch
    is amber and expected to converge; a lag that will not converge inside its
    window gets loud at the gate — ONCE, wearing the lag label, never the
    revert's (the D4 lesson: a lag card offers acknowledgment, not levers)."""
    if not declared or not sworn:
        return "silent"
    if sworn == declared:
        state.pop("t", None)
        state.pop("staged", None)
        return "converged"
    st_t = state.setdefault("t", now)
    if now - st_t < window_s:
        return "amber"
    if state.get("staged"):
        return "amber"                   # already loud once — no drumbeat
    state["staged"] = True
    return "stage"
