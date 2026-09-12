# PROVENANCE: Claude Fable 5 (claude-fable-5) — 0072 sp2, the workspace engine · 2026-09-11
"""The Workspace engine's pure half (0072 §sp2) — the roster and the draft,
as functions of records alone.

THE ONE LAW (workspace.md): the workspace is a better face on the same
doors, never a bypass. This module composes what the doors already hold —
the variant registry (0065, firmware), the shelf's variant-* heads (craft),
the standings cells (0066 sp4) — into the roster the glass renders blind.
Nothing here writes; every edit the workspace files travels the one-motion
craft-edit lane, and every draft run rides the experiment's own proven
in-memory head-swap (0043 sp4), wearing its draft-config hash so nothing
that ran is ever untraceable.
"""
from __future__ import annotations

from . import crypto, variants


def style_scores(cells: dict) -> dict:
    """The standings cells (keyed «qkind·style») folded to one judged score
    per style: the n-weighted mean over question-kinds, with the total
    evidence count carried so the glass can cap conviction the honesty
    chain's way (a mean over three asks is a hint, never a verdict)."""
    agg: dict = {}
    for key, c in (cells or {}).items():
        if "·" not in key:
            continue
        style = key.split("·", 1)[1]
        n = int(c.get("n") or 0)
        if n <= 0:
            continue
        a = agg.setdefault(style, {"n": 0, "wsum": 0.0})
        a["n"] += n
        a["wsum"] += float(c.get("mean") or 0.0) * n
    return {s: {"n": a["n"], "mean": round(a["wsum"] / a["n"], 4)}
            for s, a in agg.items() if a["n"]}


def build_roster(heads: dict, cells: dict, built: list) -> list:
    """The eleven, each wearing its declaration (firmware), its applied
    config (the shelf head under the genesis — the same read the flows
    make), its judged score, and the tuned dot (a head that moved off
    genesis). Order is the MENU's own — the registry is the one truth."""
    scores = style_scores(cells)
    built_set = set(built or ())
    out = []
    for short in variants.MENU:
        d = variants.VARIANTS_V1[short]
        head = heads.get(short) if isinstance(heads.get(short), dict) else None
        cfg = variants.config(short, head)
        out.append({
            "short": short, "title": d["title"],
            "cost_class": d["cost_class"], "delta": d["delta"],
            "why": d["why"], "blast": d["blast"],
            "stages": list(d["stages"]), "requires": list(d["requires"]),
            "built": short in built_set,
            "genesis": dict(d["genesis"]), "config": cfg,
            "tuned": cfg != d["genesis"],
            "score": scores.get(short),
        })
    return out


def heads_from_assets(rows) -> dict:
    """The shelf's variant-* heads out of a wire_assets sweep: newest row
    per name wins (the sweep arrives oldest-first, so the last write
    stands), profile only — the same head active_asset would serve."""
    heads: dict = {}
    for ref, body, _x, tags in rows or ():
        name = next((t for t in (tags or []) if str(t).startswith("variant-")),
                    None)
        if not name:
            continue
        prof = ((body or {}).get("asset") or {}).get("profile")
        if isinstance(prof, dict):
            heads[name[len("variant-"):]] = prof
    return heads


def draft_check(short: str, draft) -> tuple[str | None, dict | None]:
    """A draft is held to EXACTLY the law a landed edit is held to — the
    registry's own gate (undeclared style/knob/type refuses with the
    teaching). Drafts get no wider door for being temporary."""
    return variants.gate_check(f"variant-{short}", draft)


def draft_hash(draft: dict) -> str:
    """The draft-config hash every draft run wears (workspace.md §Compare):
    content-addressed over the knobs alone, so two identical drafts are the
    same experiment and nothing that ran is ever untraceable."""
    return crypto.content_hash({"draft": draft})


def synthetic_head(short: str, draft: dict) -> dict:
    """The in-memory head-swap row (the experiment's proven trick, 0043
    sp4): a record-shaped object active_asset() will pick as the newest
    variant-<short> head — never written to any wire, dead with the ask's
    disposable node. The far-future received_at is the whole mechanism."""
    body = {"asset": {"name": f"variant-{short}", "profile": dict(draft)}}
    return {"tags": ["asset", f"variant-{short}"],
            "received_at": "9999-12-31T00:00:00Z",
            "body": crypto._b64e(crypto.canonical(body))}
