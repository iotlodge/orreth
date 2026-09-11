# PROVENANCE: Claude Fable 5 (claude-fable-5) — 0070 sp5, the person · 2026-09-11
"""The person behind the seat (0070 §3.4) — 0012's oldest debt, paid.

In plain words: a HUMAN becomes an identity — their own seat key, minted at
becky's gate like every identity in this universe, persisting across lives
exactly as the covenant's first rule demands of every self. From then on a
profile stroke, a preference, a thumb belongs to a PERSON, signed under
their own key — not to whichever floor they happened to stand on.

The floor's shared human seat REMAINS, honestly: a walk-up human is still
served, still signed, still answered — and plainly labeled unattributed.
Anonymous is a state the machine respects, never a hole it papers over.

Custody, v1: the worker keeps each person's seed (the same custody it keeps
for residents) — the human speaks, the machine signs as them at their own
recorded request. Client-held keys are 0072's workspace affordance; the
registry built here is what they will plug into.

A person's name is NEVER reissued: the first registration owns it forever
(the roster's no-rename law, applied to people)."""
from __future__ import annotations

import json as _json
import re

from . import crypto
from .identity import NOW
from .node import make_memory

NAME_RX = re.compile(r"^[a-z][a-z0-9_-]{1,23}$")


def valid_name(name: str) -> bool:
    return bool(NAME_RX.match(str(name or "")))


def make_person_record(becky: dict, becky_kp, scope: str, name: str,
                       did: str) -> dict:
    """The registry row — becky signs (she keeps identity and every door):
    this NAME is this DID, registered at this moment, forever."""
    return make_memory(becky, becky_kp, scope,
                       {"person": {"name": name, "did": did,
                                   "registered": NOW()}},
                       kind="semantic", tags=["person", name])


def registry(node) -> dict[str, dict]:
    """name -> {did, ref} — FIRST registration wins (a person's name is
    never reissued; a later record under a taken name simply does not
    speak)."""
    out: dict[str, dict] = {}
    rows = sorted(node.records.items(),
                  key=lambda x: x[1].get("occurred_at")
                  or x[1].get("received_at") or "")
    for rid, rec in rows:
        if "person" not in (rec.get("tags") or []):
            continue
        try:
            p = _json.loads(crypto._b64d(rec["body"]).decode()).get("person") or {}
        except Exception:
            continue
        name = str(p.get("name") or "")
        if name and name not in out:
            out[name] = {"did": str(p.get("did") or ""), "ref": rid,
                         "registered": str(p.get("registered") or "")}
    return out
