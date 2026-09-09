# PROVENANCE: Claude Fable 5 (claude-fable-5) — 0066 sp2, the Analyzer · 2026-09-09
"""The Analyzer (0066 §3.1) — the versioned featurizer, and the escalation the
Dispatcher's docstring promised in July and never grew.

The six shapes stop being an anonymous regex pile: this module is a DECLARED
feature extractor, firmware-versioned, its version pinned in every choice
record — so when a smarter analyzer lands, history says exactly which eyes
read each ask. It emits the charter's analysis dimensions in plain words:
what KIND of question, how MANY parts, which DOMAIN words, how FRESH the
answer must be, what MODALITY, the asker's LATENCY preference, and how
CONFIDENT the deterministic read is.

«Hot when applicable» made law: when the deterministic read is confident, no
thought is spent — the hot path never waits on a mind it doesn't need. Only
an AMBIGUOUS ask, from an asker who did not demand speed, earns the governed
classification leg (the 0048 pattern: a typed contract, a cheap class, one
re-ask, and an honest park — the deterministic path serves whenever the mind
stumbles, on the record, never silently).
"""
from __future__ import annotations

import re

from . import graphlaw, stacks, variants

VERSION = "feat-v1"          # pinned in every choice record — firmware

_FRESH_NOW = re.compile(r"\b(latest|today|now|current(?:ly)?|this (?:week|"
                        r"month|year)|right now|so far)\b")
_MEDIA = re.compile(r"\b(image|photo|picture|video|audio|diagram|png|jpg)\b")
_PART_SEAMS = re.compile(r",| and | then | versus | vs\.? |;")


def featurize(ask: str, attributes: dict | None = None) -> dict:
    """The deterministic read — same ask, same features, forever."""
    from . import dispatcher      # runtime — dispatcher imports us back
    low = (ask or "").lower().strip()
    shapes = dispatcher.classify(low)
    parts = [p for p in _PART_SEAMS.split(low.rstrip("?")) if p.strip()]
    words = low.split()
    mode, _iso, _clean = stacks.parse_time(low)
    freshness = ("historical" if mode else
                 "current" if _FRESH_NOW.search(low) else "timeless")
    latency_pref = str((attributes or {}).get("latency") or "normal").lower()
    if latency_pref not in ("fast", "normal", "patient"):
        latency_pref = "normal"
    # confidence, deterministically: one clear shape (or a plainly simple
    # ask) reads HIGH; conflicting shapes, or a long many-part ask that
    # matched nothing, reads LOW — the only gate the escalation has
    if len(shapes) >= 3:
        confidence = "low"
    elif len(shapes) == 0 and (len(parts) >= 3 or len(words) > 24):
        confidence = "low"
    else:
        confidence = "high"
    return {
        "shapes": shapes,
        "type": shapes[0] if shapes else "plain",
        "parts": max(1, len(parts)),
        "length": ("short" if len(words) <= 8 else
                   "medium" if len(words) <= 24 else "long"),
        "domain": graphlaw.terms(low)[:6],
        "freshness": freshness,
        "modality": "media" if _MEDIA.search(low) else "text",
        "latency_pref": latency_pref,
        "confidence": confidence,
    }


def should_consult(features: dict) -> bool:
    """The escalation gate — the whole of «hot when applicable»: only an
    ambiguous ask, from an asker who did not demand speed."""
    return (features.get("confidence") == "low"
            and features.get("latency_pref") != "fast")


def consult(mind, ask: str, features: dict) -> dict:
    """The governed classification leg (the 0048 pattern): a typed contract
    over the MENU, one re-ask, an honest park. `mind` is a callable
    (prompt -> reply text or None) — the wire injects a governed thought
    under the librarian's seat at a cheap class; the suite injects a stub.
    Returns {"style", "why", "asks"} on success or {"parked": <why>} — the
    caller's deterministic path serves whenever this parks."""
    menu = "\n".join(f"- {s}: {variants.VARIANTS_V1[s]['delta']}"
                     for s in variants.MENU)
    prompt = (
        "A retrieval router needs one decision. The question below was "
        "ambiguous to its deterministic reader.\n\n"
        f"QUESTION: {ask[:300]}\n"
        f"WHAT THE READER SAW: shapes={features.get('shapes')} · "
        f"{features.get('parts')} part(s) · {features.get('length')} · "
        f"freshness={features.get('freshness')}\n\n"
        "THE MENU (pick exactly one name):\n" + menu + "\n\n"
        'Reply with STRICT JSON only: {"style": "<one menu name>", '
        '"why": "<one plain sentence a person understands>"}')
    error = ""
    for attempt in (1, 2):                    # one typed re-ask, then park
        raw = mind(prompt + error)
        if raw is None:
            return {"parked": "the mind was unreachable — the deterministic "
                              "read served"}
        try:
            import json
            j = json.loads(str(raw).strip().strip("`").lstrip("json").strip())
            style = variants.resolve(str(j.get("style", "")))
            why = str(j.get("why", "")).strip()
            if style and why:
                return {"style": style, "why": why[:200], "asks": attempt}
            error = ("\n\nYour last reply named a style not on the menu or "
                     "gave no why — reply with the strict JSON only.")
        except Exception:
            error = ("\n\nYour last reply did not parse as the strict JSON "
                     "— reply with the JSON object only.")
    return {"parked": "the mind's reply failed its contract twice — the "
                      "deterministic read served"}
