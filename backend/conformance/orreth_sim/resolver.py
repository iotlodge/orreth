"""The cascade resolver (0007): the inherited chain, folded into one Resolved Context.

One resolver, per-field merge laws: floors tighten-only (enforced at publication, composed
here — floors always beat soft) · soft standards most-specific-wins · skills additive with
higher-version tiebreak. Deterministic and CONTENT-ADDRESSED: same chain ⇒ same id — policy
becomes cacheable, diffable, canary-able. A partitioned node fails closed on its last-known
view, honestly marked stale, and the staleness is a vigil signal (locked 2026-07-02).
"""
from __future__ import annotations

from . import crypto
from .identity import NOW
from .schemas import validate


def resolve(node, subject: str | None = None) -> dict:
    chain = list(node._lineage_up())[::-1]              # root -> leaf; self is chain[-1]
    ancestors = chain[:-1]
    if node.partitioned:
        if node._last_ancestor_view is None:
            raise RuntimeError("partitioned before any resolve — no last-known context exists")
        view, stale = node._last_ancestor_view, True
        node.signal_count += 1                          # resolving blind is a vigil signal
    else:
        # the resolver read IS a pull: child-initiated, tier by tier — a parent never reaches in
        view = [(n.scope, dict(n.soft), dict(n.skills), n.profile["version"]) for n in ancestors]
        node._last_ancestor_view = view
        stale = False

    tiers = view + [(node.scope, dict(node.soft), dict(node.skills), node.profile["version"])]

    soft: dict[str, dict] = {}
    skills: dict[str, str] = {}
    for scope, tier_soft, tier_skills, _v in tiers:     # root -> leaf: later = more specific
        for key, std in tier_soft.items():
            soft[key] = {"value": std["value"], "from_scope": scope,
                         **({"version": std["version"]} if "version" in std else {})}
        for name, ver in tier_skills.items():           # additive; same name -> higher version
            skills[name] = max(skills.get(name, "0.0.0"), ver,
                               key=lambda v: [int(x) for x in v.split("-")[0].split(".")])

    floors = sorted(node.all_floors().values(), key=crypto.content_hash)
    as_of = [{"scope": scope, "version": v, **({"stale": True} if stale and i < len(view) else {})}
             for i, (scope, _s, _k, v) in enumerate(tiers)]

    content = {"scope": node.scope, **({"subject": subject} if subject else {}),
               "floors": floors, "soft": soft, "skills": skills, "as_of": as_of}
    rc = {"id": crypto.content_hash(content), **content, "resolved_at": NOW()}
    rc["sig"] = node.steward_kp.sign(node.steward["did"], {"id": rc["id"], "scope": rc["scope"]})
    return validate(rc, "resolved-context.schema.json")
