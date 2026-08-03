# PROVENANCE: Fable 5 (claude-fable-5) — 0045 sp5, the supply line · 2026-08-03
"""The supply line (0045 law 8): craft is SERVED, not copied.

An external flow — LangGraph or anything else, keeping its own shape —
acquires Orreth's governed craft by reference instead of embedding it. The
riders, kept here:

- **One run, one resolution**: `acquire()` returns a ResolvedCraft; hold it
  for the run and the version never moves under your feet. The run's own
  record should name `resolved.ref` — the exact word that drove it.
- **A consumer is a citizen**: pass a stable `did` (persist it like a self —
  the F1 mayfly lesson). Arm assignment and the serving log key on it.
- **Declared failure posture**: `on_dark="refuse"` (default) or `"stale"` —
  a dark registry serves the last signed copy LABELED (`resolved.stale`),
  never silently.
- **No secret experiments on strangers**: if an argument is running on the
  craft you acquired, `resolved.arm` says so — you can always see which
  side you drew.
"""
from __future__ import annotations

import json
import os
import urllib.parse
import urllib.request
from pathlib import Path


class ResolvedCraft:
    """One resolution, carried through the run."""

    def __init__(self, d: dict, *, stale: bool = False):
        self.name = d["name"]
        self.ref = d["ref"]
        self.version = d["version"]
        self.lifecycle = d.get("lifecycle")
        self.text = d.get("text")
        self.profile = d.get("profile")
        self.arm = d.get("arm")
        self.stale = stale

    def render(self, **slots) -> str:
        t = self.text or ""
        for k, v in slots.items():
            t = t.replace("⟦" + k + "⟧", str(v))
        return t

    def __repr__(self):
        return (f"<craft {self.name} v{self.version} {self.ref[:19]}…"
                + (f" arm={self.arm}" if self.arm else "")
                + (" STALE" if self.stale else "") + ">")


def acquire(name: str, *, did: str = "anonymous-consumer",
            base: str = "http://localhost:4562", pin: str | None = None,
            on_dark: str = "refuse",
            cache_home: str = "~/.orreth/craft-cache") -> ResolvedCraft:
    """Acquire craft by reference. Resolve ONCE per run and carry the
    returned object; `pin` asks for an exact version ref instead of head."""
    home = Path(os.path.expanduser(cache_home))
    home.mkdir(parents=True, exist_ok=True)
    cache = home / (urllib.parse.quote(name, safe="") + ".json")
    try:
        q = (f"{base}/craft?name={urllib.parse.quote(name)}"
             f"&did={urllib.parse.quote(did)}")
        if pin:
            q += f"&pin={urllib.parse.quote(pin)}"
        with urllib.request.urlopen(q, timeout=6) as resp:
            d = json.load(resp)
        if "error" in d:
            raise RuntimeError(d["error"])
        cache.write_text(json.dumps(d))
        return ResolvedCraft(d)
    except Exception:
        if on_dark == "stale" and cache.exists():
            return ResolvedCraft(json.loads(cache.read_text()), stale=True)
        raise
