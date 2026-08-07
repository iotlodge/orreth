# PROVENANCE: Fable 5 (claude-fable-5) — 0047 sp1, typed thoughts · 2026-08-07
"""Typed thoughts (0047 sp1 — law 2: typed thought or no thought).

The oldest seam in the universe is `think(klass, prompt) -> str`, and until
now every caller parsed its word leniently: the chassis treated any reply
that didn't open with DONE as a RETRY (a guess), and the wire judge VOIDED
an unparseable verdict outright — the LOST verdict, a word thrown away on
its first bad dressing. Both lanes now share one law:

    parse STRICTLY → on failure, ONE re-ask carrying the named error →
    on failure again, the honest breaker — voided or retry, attempts counted.

A typed return is a floor, not a verdict (0047 law 4): well-formed is not
true. Nothing here grades work; this module only refuses to lose a word
that was merely badly dressed — and refuses just as firmly to guess one
that never arrived.
"""
from __future__ import annotations

import json as _json
import re as _re

# What the re-ask says. The WIRE's re-ask is Canon firmware ("verdict-reask",
# genesis-seeded at its 0047 birth — changing it later takes the ceremony);
# this constant is the sim's reference wording, slots and all.
VERDICT_REASK = (
    "Your previous reply was not a valid verdict: ⟦error⟧. Reply again with "
    "STRICT JSON only — begin with the { character, no preamble, no code "
    "fences: {\"score\": 0.00, \"why\": \"one short sentence\"}.")

CRITIC_REASK = (
    "Your last reply wore neither face. Reply again with exactly one line — "
    "either: DONE: <the answer> or: RETRY: <what is missing>.")


# ---- the verdict lane (the judge's word) -------------------------------------------------

def parse_verdict(text: str):
    """The judge's word: strict JSON {"score", "why"} found anywhere in the
    reply. A truncated verdict may still carry its number (the 0041-era
    live-judge lesson, kept) — salvaged and LABELED, never guessed. None
    when no score survives at all."""
    try:
        got = _json.loads(_re.search(r"\{.*\}", text, _re.S).group(0))
        return (max(0.0, min(1.0, float(got.get("score", 0.0)))),
                str(got.get("why", ""))[:120])
    except Exception:
        m = _re.search(r'"score"\s*:\s*([0-9.]+)', text or "")
        if m:
            return (max(0.0, min(1.0, float(m.group(1)))),
                    "the judge's sentence was cut short; the score survived")
    return None


def typed_verdict(ask, *, attempts: int = 2) -> dict:
    """The verdict lane. `ask(feedback) -> str | None` performs one governed
    thought — feedback is empty on the first ask and names the error on each
    re-ask; None means the ground is missing. Returns, always:

      {"status": "typed", "score", "why", "asks"}  — the word, well-formed
      {"status": "void",  "asks"}                  — attempts spent honestly
      {"status": "dark",  "asks"}                  — the ground fell away

    Void survives only AFTER a real re-ask was tried — the breaker, never
    the first response to a badly dressed word."""
    feedback = ""
    asks = 0
    for _ in range(max(1, int(attempts))):
        raw = ask(feedback)
        if raw is None:
            return {"status": "dark", "asks": asks}
        asks += 1
        got = parse_verdict(raw)
        if got is not None:
            score, why = got
            return {"status": "typed", "score": score, "why": why,
                    "asks": asks}
        feedback = VERDICT_REASK.replace(
            "⟦error⟧", "the reply did not parse as the strict JSON verdict")
    return {"status": "void", "asks": asks}


# ---- the critic lane (the chassis's second thought) --------------------------------------

def parse_critic(text: str):
    """The critic's word wears exactly one of two faces — `DONE: <answer>`
    or `RETRY: <what is missing>` — and the word after the colon is the
    point. (done, word), or None when the reply wears neither face,
    INCLUDING a bare DONE with nothing after it: an answerless answer is
    not an answer."""
    m = _re.match(r"\s*(DONE|RETRY)\s*:\s*(\S.*)\s*$", text or "",
                  _re.I | _re.S)
    if not m:
        return None
    return m.group(1).upper() == "DONE", m.group(2).strip()


def typed_critic(ask, *, attempts: int = 2):
    """The critic lane. `ask(feedback) -> str` performs one governed thought.
    Returns (done, word, asks) — NEVER None and never a guessed DONE: after
    the attempts are spent, the honest breaker answers RETRY with the
    failure named, so the loop retries or parks but never lies."""
    feedback = ""
    for n in range(1, max(1, int(attempts)) + 1):
        got = parse_critic(ask(feedback))
        if got is not None:
            done, word = got
            return done, word, n
        feedback = CRITIC_REASK
    return (False,
            "the critic's word wore neither face twice — honest retry, "
            "never a guess", max(1, int(attempts)))
