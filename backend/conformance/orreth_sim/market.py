# PROVENANCE: Fable 5 (claude-fable-5) — 0058 sp1, the market grows eyes · 2026-08-20
"""The market (0058): a multi-source catalog of minds — intel, never authority.

The Stable's registry half. Laws (0058 §3):
  · INTEL IS NEVER AUTHORITY — read-only adapters; nothing serves until
    saddled, attested, and earned through the canary. These adapters never
    execute application inference.
  · A MISSING MODEL IS NOT A DEAD MODEL — one refresh omitting an entry marks
    it missing and counts consecutive misses; only past MISS_LIMIT does the
    intel retire (the metabolism's instinct, applied to the market).
  · FIELD PRECEDENCE — provider's own API > serving router (OpenRouter / HF)
    > litellm's local map; every source kept in `sources`, never discarded.
  · AWS IS READ, NOT WIRED (JB's pin, 2026-08-20) — bedrock-family entries
    wear `read_only: true`; the live adapter is a named future dive.

Sources, lowest authority first (later folds overwrite non-null fields):
  litellm-map    — litellm's LOCAL model_cost (≈3k minds incl. Bedrock);
                   zero network, zero spend; pricing/context/capabilities.
  hf-router      — Hugging Face's public serving router (what is actually
                   served, by which inference providers).
  openrouter     — the existing intel eye, passed in by the worker (its cache
                   and TTL stay the wrangler's own).
  anthropic-api  — GET /v1/models, key-scoped: presence in the answer IS the
                   access proof (`access: "available"`).
  openai-api     — GET /v1/models, same law.
"""
from __future__ import annotations

import json
import os
import time
import urllib.request
from pathlib import Path

CACHE_TTL = float(os.environ.get("ORRETH_MARKET_TTL", str(6 * 3600)))
MISS_LIMIT = 3
READ_ONLY_PROVIDERS = {"bedrock", "bedrock_converse", "sagemaker", "sagemaker_chat"}


# ---------------------------------------------------------------- the adapters

def _src_litellm_map() -> tuple[dict, str]:
    import litellm
    out: dict[str, dict] = {}
    for mid, info in litellm.model_cost.items():
        if not isinstance(info, dict):
            continue
        prov = str(info.get("litellm_provider") or "")
        if not prov or info.get("mode") not in ("chat", "responses"):
            continue
        cid = mid if mid.startswith(prov + "/") else f"{prov}/{mid}"
        mods = ["text"] + (["image"] if info.get("supports_vision") else []) \
            + (["audio"] if info.get("supports_audio_input") else [])
        out[cid] = {
            "provider": prov,
            "pricing": {"prompt": info.get("input_cost_per_token"),
                        "completion": info.get("output_cost_per_token")},
            "context_length": info.get("max_input_tokens") or info.get("max_tokens"),
            "modalities": mods,
            "capabilities": {
                "tools": bool(info.get("supports_function_calling")),
                "vision": bool(info.get("supports_vision")),
                "structured": bool(info.get("supports_response_schema")),
                "reasoning": bool(info.get("supports_reasoning")),
            },
            "mode": info.get("mode"),
            "read_only": prov in READ_ONLY_PROVIDERS,
        }
    return out, f"{len(out)} minds from the local map"


def _src_hf_router() -> tuple[dict, str]:
    raw = json.loads(urllib.request.urlopen(urllib.request.Request(
        "https://router.huggingface.co/v1/models"), timeout=15).read())
    out: dict[str, dict] = {}
    for m in raw.get("data", []):
        mid = str(m.get("id") or "")
        if not mid:
            continue
        provs = m.get("providers") or []
        e: dict = {"provider": "huggingface", "serving_providers": len(provs)}
        best = next((p for p in provs if isinstance(p, dict)), {})
        if best.get("context_length"):
            e["context_length"] = best["context_length"]
        pr = best.get("pricing") or {}
        if pr:
            # HF router prices arrive per-million; the market speaks per-token
            e["pricing"] = {"prompt": _per_token(pr.get("input")),
                            "completion": _per_token(pr.get("output"))}
        if best.get("supports_tools") is not None:
            e["capabilities"] = {"tools": bool(best.get("supports_tools")),
                                 "structured": bool(best.get("supports_structured_output"))}
        out[f"huggingface/{mid}"] = e
    return out, f"{len(out)} minds actually served"


def _per_token(v) -> float | None:
    try:
        return float(v) / 1e6
    except (TypeError, ValueError):
        return None


def _src_anthropic() -> tuple[dict, str]:
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        return {}, "no key — skipped; access unproven"
    raw = json.loads(urllib.request.urlopen(urllib.request.Request(
        "https://api.anthropic.com/v1/models?limit=100",
        headers={"x-api-key": key, "anthropic-version": "2023-06-01"}),
        timeout=15).read())
    out = {f"anthropic/{m['id']}": {"provider": "anthropic",
                                    "display_name": m.get("display_name"),
                                    "created": m.get("created_at"),
                                    "access": "available"}
           for m in raw.get("data", []) if m.get("id")}
    return out, f"{len(out)} minds this key can reach"


def _src_openai() -> tuple[dict, str]:
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        return {}, "no key — skipped; access unproven"
    raw = json.loads(urllib.request.urlopen(urllib.request.Request(
        "https://api.openai.com/v1/models",
        headers={"Authorization": f"Bearer {key}"}), timeout=15).read())
    out = {f"openai/{m['id']}": {"provider": "openai",
                                 "created": m.get("created"),
                                 "access": "available"}
           for m in raw.get("data", []) if m.get("id")}
    return out, f"{len(out)} minds this key can reach"


def _openrouter_entries(catalog: list | None) -> tuple[dict, str]:
    out: dict[str, dict] = {}
    for c in catalog or []:
        mid = str(c.get("id") or "")
        if not mid:
            continue
        e = {"provider": c.get("provider") or mid.split("/")[0],
             "context_length": c.get("context_length"),
             "modalities": c.get("modalities") or [],
             "created": c.get("created"), "expires_at": c.get("expires_at")}
        pr = c.get("pricing") or {}
        if pr:
            e["pricing"] = {"prompt": _f(pr.get("prompt")),
                            "completion": _f(pr.get("completion"))}
        out[mid] = e
    return out, f"{len(out)} minds from the router"


def _f(v) -> float | None:
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


# ---------------------------------------------------------------- the fold

def _fold(merged: dict, cid: str, entry: dict, source: str, now: str) -> None:
    """Later sources are higher authority: non-null fields overwrite; the
    sources list remembers every eye that saw this mind (never discarded)."""
    e = merged.setdefault(cid, {"id": cid, "sources": [], "misses": 0,
                                "access": "unknown", "seen_at": now})
    for k, v in entry.items():
        if v is None or v == {} or v == []:
            continue
        if k == "pricing" and isinstance(e.get("pricing"), dict):
            e["pricing"] = {**e["pricing"],
                            **{pk: pv for pk, pv in v.items() if pv is not None}}
        elif k == "capabilities" and isinstance(e.get("capabilities"), dict):
            e["capabilities"] = {**e["capabilities"], **v}
        else:
            e[k] = v
    e["seen_at"] = now
    e["misses"] = 0
    e.pop("missing", None)
    if source not in e["sources"]:
        e["sources"].append(source)


ADAPTERS = [("litellm-map", _src_litellm_map),
            ("hf-router", _src_hf_router),
            ("anthropic-api", _src_anthropic),
            ("openai-api", _src_openai)]


def refresh(home: Path, openrouter: list | None = None, *,
            sources: list | None = None, force: bool = False) -> dict:
    """The market, refreshed if stale (CACHE_TTL) — otherwise the cache
    answers. Per-source failure is a note, never an outage: the last good
    intel stands, labeled. `sources` is injectable for the suite."""
    cache = Path(home) / "market.json"
    cache.parent.mkdir(parents=True, exist_ok=True)
    prev = {}
    if cache.exists():
        try:
            prev = json.loads(cache.read_text())
        except Exception:
            prev = {}
        if not force and time.time() - cache.stat().st_mtime < CACHE_TTL:
            prev["stale"] = False
            return prev
    now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    merged: dict[str, dict] = {}
    notes: dict[str, dict] = {}
    ok_sources: set[str] = set()
    pool = list(sources) if sources is not None else (
        [("openrouter", lambda: _openrouter_entries(openrouter))] + list(ADAPTERS))
    # authority order: litellm-map first, provider APIs last (the fold's law)
    order = {"litellm-map": 0, "hf-router": 1, "openrouter": 2,
             "anthropic-api": 3, "openai-api": 4}
    pool.sort(key=lambda s: order.get(s[0], 9))
    for name, fn in pool:
        try:
            entries, note = fn()
            notes[name] = {"ok": True, "note": note, "count": len(entries), "at": now}
            ok_sources.add(name)
            for cid, e in entries.items():
                _fold(merged, cid, e, name, now)
        except Exception as ex:
            notes[name] = {"ok": False, "note": str(ex)[:120], "at": now}
    # a missing model is not a dead model: entries the refresh did not see,
    # whose sources DID answer, age by one miss; the rest carry forward as-is
    for cid, old in (prev.get("entries") or {}).items():
        if cid in merged:
            continue
        e = dict(old)
        if any(s in ok_sources for s in e.get("sources", [])):
            e["misses"] = int(e.get("misses", 0)) + 1
            e["missing"] = True
        if int(e.get("misses", 0)) <= MISS_LIMIT:
            merged[cid] = e
    doc = {"entries": merged, "sources": notes, "refreshed_at": now,
           "stale": not ok_sources, "total": len(merged)}
    try:
        cache.write_text(json.dumps(doc))
    except Exception:
        pass
    return doc


# ---------------------------------------------------------------- the search

def search(doc: dict, q: str = "", provider: str = "", capability: str = "",
           max_price: float | None = None, min_context: int | None = None,
           source: str = "", limit: int = 100) -> dict:
    """The human's question against the merged intel. `max_price` speaks
    USD per MILLION prompt tokens (the human unit); pricing is per-token."""
    ql = q.lower()
    hits = []
    for e in (doc.get("entries") or {}).values():
        if ql and ql not in e["id"].lower() \
                and ql not in str(e.get("display_name") or "").lower():
            continue
        if provider and provider.lower() not in str(e.get("provider") or "").lower():
            continue
        if capability and not (e.get("capabilities") or {}).get(capability):
            continue
        if source and source not in e.get("sources", []):
            continue
        if max_price is not None:
            p = (e.get("pricing") or {}).get("prompt")
            if p is None or p * 1e6 > max_price:
                continue
        if min_context is not None:
            if (e.get("context_length") or 0) < min_context:
                continue
        hits.append(e)
    hits.sort(key=lambda e: (e.get("missing", False),
                             -(len(e.get("sources", []))),
                             ((e.get("pricing") or {}).get("prompt") or 9e9)))
    return {"entries": hits[:limit], "total": len(hits),
            "served": min(len(hits), limit),
            "sources": doc.get("sources", {}),
            "refreshed_at": doc.get("refreshed_at"),
            "stale": bool(doc.get("stale"))}
