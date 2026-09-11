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
               quoted: str | None = None, inferred_from: str | None = None,
               prefers: dict | None = None, person: str | None = None) -> dict:
    """A profile claim with its provenance and its rung on the ladder (0025 §2):
    the human enters trusted; the Librarian — and the Mirror (0034 sp3) —
    enter untrusted, always, and every inference names its evidence.
    `prefers` (0070 sp2): the typed preference shape a HUMAN's words carry —
    only sovereignty may set one; an inference offering prefers refuses."""
    if asserted_by not in ("human", "librarian", "mirror"):
        raise ValueError(f"unknown asserter: {asserted_by!r}")
    if asserted_by != "human" and not inferred_from:
        raise ValueError("an inference names its evidence — inferred_from is required")
    if prefers and asserted_by != "human":
        raise ValueError("only the human's own word sets a preference (0025 "
                         "sovereignty — an inference never steers the voice)")
    body: dict = {"profile": {"claim": claim, "asserted_by": asserted_by,
                              "state": "trusted" if asserted_by == "human"
                                       else "untrusted",
                              **({"prefers": dict(prefers)} if prefers else {})}}
    if quoted is not None:
        body["profile"]["quoted"] = quoted
    if inferred_from is not None:
        body["profile"]["inferred_from"] = inferred_from
    # 0070 sp5 — whose stroke: a registered person's claim wears their name
    # (and, at the call sites, their OWN signature); the floor's anonymous
    # strokes stay exactly as they were — unattributed, honestly
    tags = ["profile", "creator"] + ([f"person:{person}"] if person else [])
    rec = make_memory(agent, kp, scope, body, kind="semantic", tags=tags)
    if inferred_from is not None:
        rec["derived_from"] = [inferred_from]
    return rec


# ---- typed preferences (0070 sp2 — 0069's language hook lands here) -------------------

_PREF_LANG = (r"(?:prefer(?:s)?\s+(?:answers?\s+)?in|answer\s+(?:me\s+)?in|"
              r"reply\s+in|respond\s+in|language\s*[:=]?)\s+([a-zA-Z]+)")
_PREF_VERBOSITY = {"brief": ("brief", "short", "concise", "terse"),
                   "detailed": ("detailed", "thorough", "verbose", "long")}


def parse_prefs(claim: str) -> dict:
    """The typed shape inside a human's own words — deterministic, never a
    guess dressed as knowledge: «I prefer answers in Spanish» →
    {"language": "spanish"}; «keep replies brief» → {"verbosity": "brief"}.
    Empty when the words carry no preference."""
    import re
    out: dict = {}
    low = (claim or "").lower()
    m = re.search(_PREF_LANG, low)
    if m and m.group(1) not in ("a", "an", "the", "my", "your"):
        out["language"] = m.group(1)
    for level, words in _PREF_VERBOSITY.items():
        if any(w in low for w in words) and (
                "answer" in low or "repl" in low or "response" in low
                or "verbosity" in low):
            out["verbosity"] = level
            break
    return out


def live_prefs(claims: list[tuple[str, dict]]) -> dict:
    """The standing preferences: HUMAN-asserted only (sovereignty — an
    inference never sets a preference), latest assertion per key wins
    (correctable by re-assertion), withdrawn already dead upstream."""
    out: dict = {}
    for _ref, c in claims:                    # oldest-first rows; last wins
        if c.get("asserted_by") != "human":
            continue
        for k, v in (c.get("prefers") or {}).items():
            out[k] = v
    return out


def slice_text(claims: list[tuple[str, dict]], *, cap: int = 700) -> str:
    """0070 sp2 — THE SLICE the voice finally reads: provenance-labeled
    (you told me / I observed / the mirror noticed), sovereign-door-only —
    this text is injected structurally and NEVER enters a projection.
    Empty portrait, empty slice — a stranger stays a stranger."""
    label = {"human": "you told me", "librarian": "I observed",
             "mirror": "the mirror noticed"}
    rows = [f"{label.get(c.get('asserted_by'), '?')}: "
            f"{str(c.get('claim') or '')[:120]}"
            for _r, c in claims if c.get("claim")]
    if not rows:
        return ""
    text = " · ".join(rows)
    return text[:max(200, int(cap))]


def make_withdrawal(agent: dict, kp, scope: str, claim_ref: str) -> dict:
    """Consent withdrawn (0025 §3): a withdrawal derives from the claim it silences.
    THAT you chose to forget stays on the record; WHAT was forgotten stops speaking."""
    rec = make_memory(agent, kp, scope,
                      {"profile": {"withdrawn": claim_ref,
                                   "reason": "consent withdrawn"}},
                      kind="semantic", tags=["profile", "withdrawn"])
    rec["derived_from"] = [claim_ref]
    return rec


def stroke_visible(tags: list, person: str = "") -> bool:
    """0070 sp5 — WHOSE portrait a stroke belongs to: a named person sees
    exactly their own person-tagged strokes; the anonymous portrait sees
    only unattributed ones (a person's strokes never leak into it);
    withdrawals always count wherever they land."""
    ptag = next((t for t in tags or [] if str(t).startswith("person:")), None)
    if person:
        return ptag == f"person:{person}"
    return ptag is None or "withdrawn" in (tags or [])


def withdrawn_refs(bodies: dict) -> set:
    """The dead set: every claim ref any withdrawal names (lineage-death — a
    withdrawn claim never answers, whatever older versions exist)."""
    return {b["profile"]["withdrawn"] for b in bodies.values()
            if isinstance(b, dict) and "withdrawn" in (b.get("profile") or {})}
