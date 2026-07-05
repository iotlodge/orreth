# PROVENANCE: authored by Opus 4.8 (2026-07-05), pending Fable 5 review — see agents/PROVENANCE.md
"""A pocket AgentField — the reasoner-network ergonomics, none of the infrastructure.

AgentField's real SDK (github.com/Agent-Field/agentfield) decorates functions as
`@app.reasoner` (AI judgment) and `@app.skill` (deterministic), auto-registers them with
a control plane, and executes them as an observable DAG. This ~40-line shim reproduces
just that *shape* so a sentinel written here would port to the real package by swapping
the import. The control plane it registers with, of course, is the Orreth floor itself.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from typing import Callable


@dataclass
class Finding:
    """A flat finding — AgentField's discipline: narrow task, 3-4 fields, no prose blobs."""
    invariant: str
    attempted: str
    expected: str
    observed: str
    verdict: str            # PASS (governance held) | FAIL (breach) | SKIP (not testable here)


@dataclass
class App:
    """A reasoner network. Reasoners are judgment steps; probes are the adversarial hunters."""
    node_id: str
    version: str = "0.1.0"
    _recon: Callable | None = None
    _probes: list[tuple[str, Callable]] = field(default_factory=list)
    _report: Callable | None = None

    def recon(self, fn: Callable) -> Callable:
        self._recon = fn
        return fn

    def probe(self, name: str) -> Callable:
        def deco(fn: Callable) -> Callable:
            self._probes.append((name, fn))
            return fn
        return deco

    def report(self, fn: Callable) -> Callable:
        self._report = fn
        return fn

    def audit(self, ctx) -> dict:
        """recon → probes in parallel (the hunters) → report. The AgentField audit shape,
        end to end, over one observable pass."""
        recon = self._recon(ctx) if self._recon else {}
        with ThreadPoolExecutor(max_workers=max(1, len(self._probes))) as pool:
            findings = list(pool.map(lambda np: _safe(np[1], ctx, recon), self._probes))
        return self._report(ctx, recon, findings) if self._report else {"findings": findings}


def _safe(fn: Callable, ctx, recon) -> Finding:
    try:
        return fn(ctx, recon)
    except Exception as e:                       # a probe that crashes is itself a finding
        return Finding(getattr(fn, "__name__", "probe"), "run probe", "a verdict",
                       f"probe crashed: {e}", "FAIL")
