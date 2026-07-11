# PROVENANCE: authored by Fable 5 (claude-fable-5), 2026-07-10 — 0025, blessed same day
"""The Human Profile (0025): a living portrait, co-authored and consent-bound.

Human assertions enter TRUSTED (the subject is sovereign over their own preferences);
Librarian inferences enter UNTRUSTED (rookie probation applied to beliefs about you).
Withdrawal is lineage-death (0023's recalled semantics, reused): a withdrawn claim
never answers again — physical erasure rides the Purge (crypto-shred, 0022 §6).
"""

from .node import make_memory

_ASSERT = ("my profile:", "remember about me:", "about me:")
_READ = ("what do you know about me", "show my profile", "read my profile",
         "my profile?")
_FORGET = ("forget about me:", "forget that ")


def parse_assert(text: str):
    """“my profile: I toast with cocoa” → the claim — or None."""
    t = (text or "").strip()
    low = t.lower()
    for p in _ASSERT:
        if low.startswith(p):
            claim = t[len(p):].strip().strip(".!")
            return claim or None
    return None


def parse_read(text: str) -> bool:
    low = (text or "").strip().lower().rstrip("?.! ")
    return any(low.startswith(p.rstrip("?")) for p in _READ)


def parse_forget(text: str):
    """“forget about me: <topic>” → the topic — or None."""
    t = (text or "").strip()
    low = t.lower()
    for p in _FORGET:
        if low.startswith(p):
            topic = t[len(p):].strip().strip(".!?")
            return topic or None
    return None


def make_claim(agent: dict, kp, scope: str, claim: str, *, asserted_by: str,
               quoted: str | None = None, inferred_from: str | None = None) -> dict:
    """A profile claim with its provenance and its rung on the ladder (0025 §2):
    the human enters trusted, the Librarian enters untrusted — always."""
    if asserted_by not in ("human", "librarian"):
        raise ValueError(f"unknown asserter: {asserted_by!r}")
    if asserted_by == "librarian" and not inferred_from:
        raise ValueError("an inference names its evidence — inferred_from is required")
    body: dict = {"profile": {"claim": claim, "asserted_by": asserted_by,
                              "state": "trusted" if asserted_by == "human"
                                       else "untrusted"}}
    if quoted is not None:
        body["profile"]["quoted"] = quoted
    if inferred_from is not None:
        body["profile"]["inferred_from"] = inferred_from
    rec = make_memory(agent, kp, scope, body, kind="semantic",
                      tags=["profile", "creator"])
    if inferred_from is not None:
        rec["derived_from"] = [inferred_from]
    return rec


def make_withdrawal(agent: dict, kp, scope: str, claim_ref: str) -> dict:
    """Consent withdrawn (0025 §3): a withdrawal derives from the claim it silences.
    THAT you chose to forget stays on the record; WHAT was forgotten stops speaking."""
    rec = make_memory(agent, kp, scope,
                      {"profile": {"withdrawn": claim_ref,
                                   "reason": "consent withdrawn"}},
                      kind="semantic", tags=["profile", "withdrawn"])
    rec["derived_from"] = [claim_ref]
    return rec


def withdrawn_refs(bodies: dict) -> set:
    """The dead set: every claim ref any withdrawal names (lineage-death — a
    withdrawn claim never answers, whatever older versions exist)."""
    return {b["profile"]["withdrawn"] for b in bodies.values()
            if isinstance(b, dict) and "withdrawn" in (b.get("profile") or {})}
