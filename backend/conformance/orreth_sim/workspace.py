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


# ---- 0072 sp3 · the operate room's fold -------------------------------------------

def _pct(sorted_vals: list, q: float) -> float:
    """The nearest-rank percentile — deterministic, no interpolation
    surprises at tiny n (an operate room at n=2 must not invent numbers)."""
    if not sorted_vals:
        return 0.0
    i = min(len(sorted_vals) - 1, max(0, int(q * len(sorted_vals) + 0.5) - 1))
    return float(sorted_vals[i])


def monitor_fold(records: dict) -> dict:
    """The operate room (0072 sp3), as a function of the SAME records the
    scoreboard reads: per-style ask volume, latency percentiles (nearest
    rank), mean context spend, draft-run counts, and the recent strip —
    every row carrying its exchange ref so the room stays a hall of doors.
    Replay rows are the bench's, never operations — excluded."""
    import json as _json
    styles: dict = {}
    recent: list = []
    for rid, rec in (records or {}).items():
        tags = rec.get("tags") or []
        if "ask" not in tags or "replay" in tags:
            continue
        try:
            body = _json.loads(crypto._b64d(rec["body"]).decode())
        except Exception:
            continue
        b = body.get("ask") or {}
        style = variants.resolve(str(b.get("variant") or "")) or "naive"
        sig = b.get("signals") or {}
        lat = float(sig.get("latency_ms") or 0)
        chars = int(sig.get("cost_chars") or 0)
        at = str(rec.get("occurred_at") or rec.get("received_at") or "")
        s = styles.setdefault(style, {"asks": 0, "lats": [], "chars": 0,
                                      "drafts": 0, "last_at": ""})
        s["asks"] += 1
        s["lats"].append(lat)
        s["chars"] += chars
        if b.get("draft"):
            s["drafts"] += 1
        if at > s["last_at"]:
            s["last_at"] = at
        recent.append({"at": at, "style": style, "latency_ms": lat,
                       "chars": chars, "draft": bool(b.get("draft")),
                       "ref": rid, "asked": str(b.get("asked") or "")[:70]})
    out = {}
    for style, s in styles.items():
        lats = sorted(s["lats"])
        out[style] = {"asks": s["asks"],
                      "p50_ms": round(_pct(lats, 0.5), 1),
                      "p95_ms": round(_pct(lats, 0.95), 1),
                      "chars_mean": round(s["chars"] / s["asks"]) if s["asks"] else 0,
                      "drafts": s["drafts"], "last_at": s["last_at"]}
    recent.sort(key=lambda r: r["at"], reverse=True)
    return {"styles": out, "recent": recent[:15],
            "asks": sum(v["asks"] for v in out.values())}


# ---- 0072 sp5 · the enterprise folds ----------------------------------------------

def showback_fold(records: dict) -> list:
    """COST SHOWBACK (0072 sp5): who spent what, folded from the SAME ask
    records as everything else — per asker (the person's name when their
    signed ask carried one, the DID otherwise, the anonymous pool as
    itself): asks · context chars · summed walk latency. Sorted by spend,
    heaviest first — the operate room renders it, the Observatory judges
    it, nothing here is a bill (a bill needs a price sheet; this is the
    honest meter)."""
    import json as _json
    spend: dict = {}
    for rid, rec in (records or {}).items():
        tags = rec.get("tags") or []
        if "ask" not in tags or "replay" in tags:
            continue
        try:
            b = _json.loads(crypto._b64d(rec["body"]).decode()).get("ask") or {}
        except Exception:
            continue
        who = str(b.get("person") or "") or str(b.get("by") or "anonymous")
        sig = b.get("signals") or {}
        s = spend.setdefault(who, {"who": who, "asks": 0, "chars": 0,
                                   "latency_ms": 0.0,
                                   "person": bool(b.get("person"))})
        s["asks"] += 1
        s["chars"] += int(sig.get("cost_chars") or 0)
        s["latency_ms"] = round(s["latency_ms"]
                                + float(sig.get("latency_ms") or 0), 1)
    return sorted(spend.values(), key=lambda x: -x["chars"])


def quota_check(rows: list, who: str, now_iso: str, limit: int) -> str | None:
    """THE ASK QUOTA (0072 sp5 — a quota is a legible business rule, so its
    refusal TEACHES, never the one face): count this asker's asks in the
    trailing hour from the queue's own ledger (restart-surviving, no side
    counter) against the dial's word. None = within; a string = the
    teaching. limit 0 = the quota is off."""
    if not limit or limit <= 0:
        return None
    from datetime import datetime, timedelta
    try:
        now = datetime.fromisoformat(now_iso.replace("Z", "+00:00"))
    except ValueError:
        return None
    floor_t = (now - timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
    n = sum(1 for r in rows or []
            if r.get("kind") == "ask"
            and str(r.get("did") or "anonymous") == who
            and str(r.get("at") or "") >= floor_t)
    if n < limit:
        return None
    return (f"the ask quota for this seat is {limit} per hour and the hour "
            f"holds {n} already — the window slides; ask again shortly, or "
            f"the human can turn the “ask-quota-hourly” dial (a governed "
            f"value, not a wall)")

