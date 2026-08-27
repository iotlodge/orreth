# PROVENANCE: Fable 5 (claude-fable-5) — 0059 sp1, the seed catalog · 2026-08-21
"""The seed catalog (0059): intel about tools that EXIST — never authority.

The Farm's registry half, the 0058 market's farm-tongued sibling. Laws:
  · INTEL IS NEVER AUTHORITY — a seed can be searched, compared, selected;
    nothing serves until planted, probed, approved, and earned through
    probation. These eyes never invoke a tool.
  · PROVENANCE KEPT — every seed names its eye (`mcp-registry` · `toolshed` ·
    `capability:<key>`); the official registry's status and latest-version
    flags ride along.
  · THE CACHE SPEAKS WHEN THE WIRE IS DOWN — per-query TTL'd cache on disk;
    a failed eye is a note, never an outage, and staleness is labeled.

The one live eye today is the OFFICIAL MCP REGISTRY
(registry.modelcontextprotocol.io — "an app store for MCP servers"), searched
on demand rather than mirrored: it is large, alive, and its search is the
authority on itself. Local seeds (the rig's own toolshed, capability-declared
tools) are merged by the caller — the worker knows the rig; this module knows
the market.
"""
from __future__ import annotations

import hashlib
import json
import os
import time
import urllib.parse
import urllib.request
from pathlib import Path

CACHE_TTL = float(os.environ.get("ORRETH_SEEDS_TTL", "3600"))
REGISTRY = "https://registry.modelcontextprotocol.io/v0/servers"


def _default_fetch(url: str) -> dict:
    with urllib.request.urlopen(urllib.request.Request(url), timeout=12) as r:
        return json.loads(r.read())


def registry_search(q: str, limit: int = 30, *, fetch=None) -> tuple[list, str]:
    """The official registry, asked in its own words. Entries arrive one row
    per VERSION; we keep one seed per server name, preferring the row the
    registry marks latest (else the last seen). Never raises — the caller
    reads the note."""
    fetch = fetch or _default_fetch
    url = REGISTRY + "?" + urllib.parse.urlencode(
        {"search": q, "limit": max(1, min(100, limit))})
    raw = fetch(url)
    by_name: dict[str, dict] = {}
    for row in raw.get("servers", []):
        s = row.get("server") or {}
        name = str(s.get("name") or "")
        if not name:
            continue
        meta = (row.get("_meta") or {}).get(
            "io.modelcontextprotocol.registry/official") or {}
        seed = {
            "id": name,
            "title": s.get("title") or name.split("/")[-1],
            "description": str(s.get("description") or "")[:280],
            "version": s.get("version"),
            "remotes": [{"type": rm.get("type"), "url": rm.get("url")}
                        for rm in (s.get("remotes") or []) if rm.get("url")],
            # 0062 sp2 — a package seed keeps its IDENTITY, not just a count:
            # the container walk needs the registry and the identifier to
            # form a body recipe (known image + declared command, JB's L3)
            "packages": [
                {"registry": (p.get("registryType") or p.get("registry_type")
                              or p.get("registry_name") or ""),
                 "id": p.get("identifier") or "",
                 "version": p.get("version") or ""}
                for p in (s.get("packages") or []) if p.get("identifier")],
            "status": meta.get("status"),
            "latest": bool(meta.get("isLatest")),
            "source": "mcp-registry",
        }
        held = by_name.get(name)
        if held is None or seed["latest"] or not held.get("latest"):
            by_name[name] = seed
    out = sorted(by_name.values(), key=lambda e: (not e["latest"], e["id"]))
    return out, f"{len(out)} seed(s) the registry knows for “{q}”"


def resolve_tool_assignment(assignments: dict, subject: str,
                            floor_scope: str = "") -> dict:
    """0059 §2.7 — the 0058 allocation law, farm-shaped: the most specific
    word wins (subject → floor → universe). A row is {service, tool?}; it
    names which SERVING tool a caller prefers. Pure — the worker owns the
    ledger, this owns the order."""
    for key in ([subject]
                + ([f"floor:{floor_scope}"] if floor_scope else [])
                + ["universe"]):
        row = assignments.get(key)
        if isinstance(row, dict) and row.get("service"):
            return {**row, "resolved_from": key}
    return {}


def _qkey(q: str) -> str:
    return hashlib.sha256(q.strip().lower().encode()).hexdigest()[:16]


def search(home: Path, q: str, *, local: list | None = None,
           fetch=None, force: bool = False, limit: int = 30) -> dict:
    """One question against the market and the rig together. `local` rows
    (the toolshed, capability-declared tools) are the caller's — merged in
    front, because what already stands OUTRANKS what could be planted.
    Registry answers are cached per query (CACHE_TTL); a downed wire serves
    the last good answer, labeled stale."""
    cache_p = Path(home) / "seeds-cache.json"
    cache: dict = {}
    if cache_p.exists():
        try:
            cache = json.loads(cache_p.read_text())
        except Exception:
            cache = {}
    key = _qkey(q)
    hit = cache.get(key) or {}
    entries: list = []
    note, stale = "", False
    if not force and hit and time.time() - float(hit.get("at", 0)) < CACHE_TTL:
        entries, note = hit.get("entries") or [], hit.get("note", "cached")
    else:
        try:
            entries, note = registry_search(q, limit, fetch=fetch)
            cache[key] = {"at": time.time(), "q": q, "entries": entries,
                          "note": note}
            cache_p.parent.mkdir(parents=True, exist_ok=True)
            try:
                cache_p.write_text(json.dumps(cache))
            except Exception:
                pass
        except Exception as ex:
            entries = hit.get("entries") or []
            note = f"the registry's wire is down ({str(ex)[:80]})" + (
                " — the last good answer stands" if entries else "")
            stale = True
    ql = q.strip().lower()
    mine = [e for e in (local or [])
            if not ql or ql in str(e.get("id", "")).lower()
            or ql in str(e.get("description", "")).lower()]
    return {"entries": (mine + entries)[:max(1, limit)],
            "local": len(mine), "registry": len(entries),
            "note": note, "stale": stale, "q": q}
