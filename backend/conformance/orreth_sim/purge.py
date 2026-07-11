# PROVENANCE: authored by Fable 5 (claude-fable-5), 2026-07-10 — 0026, the Purge
"""Governed erasure (0026): the split model, the seal, and the door's immune memory.

Erasure is the gravest act an append-only universe can perform, so every path to it
is a gate on the record. The consent path rides the subject's own withdrawal — their
consent IS the quorum for their own data (R9). The operational path stages and
HOLDS: bars are absolute (0012 §5) — below two control-entitled humans nothing
executes; the seal contains at machine speed while destruction waits. The engine
itself lives in the core (tombstone); this module builds only the governance
around it.
"""

from .node import make_memory

QUORUM = 2   # humans, plural (R9) — destruction below this bar is structurally unavailable


def held_message(present: int = 1) -> str:
    """The honest hold (0026 §2), stated plainly — never a silent nothing."""
    return (f"held: quorum {present} of {QUORUM} — containment active; "
            "destruction waits for humans, plural")


def make_seal(agent: dict, kp, scope: str, refs: list, *, reason: str,
              request_id: str = "") -> dict:
    """Containment at machine speed (0026 §3): a seal record derives from the refs
    it darkens, resident-signed, and the read paths exclude what it names exactly
    as they exclude the recalled and the withdrawn (lineage-death, third use).
    Reversible by design — a seal must never conflate with the purged set, which
    is not."""
    if not refs:
        raise ValueError("a seal derives from what it contains — refs are required")
    if not reason:
        raise ValueError("every seal says why — reason is required")
    body: dict = {"seal": {"refs": list(refs), "reason": reason}}
    if request_id:
        body["seal"]["purge_request"] = request_id
    rec = make_memory(agent, kp, scope, body, kind="semantic",
                      tags=["seal", "purge"])
    rec["derived_from"] = list(refs)
    return rec


def sealed_refs(bodies: dict) -> set:
    """The dark set: every ref any seal names. Exclusion, not death — the sealed
    stop answering the moment a purge stages, however long the humans take."""
    return {ref for b in bodies.values() if isinstance(b, dict)
            for ref in (b.get("seal") or {}).get("refs", [])}


def discredited_dids(bodies: dict) -> set:
    """The door's immune memory (0026 §5): every source DID the recall walks left
    on the record. The librarian refuses new knowledge from any of them — loudly."""
    return {b["recalled_source"] for b in bodies.values()
            if isinstance(b, dict) and b.get("state") == "recalled"
            and b.get("recalled_source")}
