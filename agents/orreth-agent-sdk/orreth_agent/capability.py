# PROVENANCE: Fable 5 (claude-fable-5) — 0055, the SDK's side · 2026-08-13
"""The Capability Contract, SDK-side (0055).

A capability is five signed declarations and never code: floors · crew ·
craft · Chronicle · THE MANIFEST. This module builds manifests that the
Foundation's portal renders blind — eleven panel kinds (JB's L1), the
lifecycle verbs on the tile (L3), the whole world one card.

Install, v1 (JB's L4): repo-local — a genesis module under the repo holds
CRAFT (the prompts) and MANIFEST (this builder's output); the Foundation's
planting beat puts both on the shelf, and the portal lists the world the
moment its crew stands. Crew commands execute from GENESIS ONLY — the
shelf's editable copy of a manifest never runs a command. Bring-your-own-
package is a named cloud-phase commitment riding the deed/trust machinery
(0042); when it lands, `declare()` grows a wire form.
"""
from __future__ import annotations

PANEL_KINDS = {"tabs", "markdown", "chart", "strip", "controls", "download",
               "stat", "bars", "list", "doc", "table"}


def manifest(*, key: str, name: str, emoji: str, resident: str, floor: str,
             port: int, law: str, view: list, door: str | None = None,
             group: str | None = None, crew: list | None = None,
             verbs: dict | None = None, collection: dict | None = None) -> dict:
    """Build a capability manifest. Raises on a panel kind beyond the canon
    vocabulary — the glass renders blind, so the contract checks here."""
    for p in view:
        if p.get("kind") not in PANEL_KINDS:
            raise ValueError(f"panel kind «{p.get('kind')}» is beyond the "
                             f"canon vocabulary {sorted(PANEL_KINDS)}")
    out = {"key": key, "name": name, "emoji": emoji, "resident": resident,
           "floor": floor, "port": port, "law": law, "door": door or key,
           "view": view}
    if group:
        out["group"] = group
    if crew:
        out["crew"] = crew
    if verbs:
        out["verbs"] = verbs
    if collection:
        out["collection"] = collection
    return out
