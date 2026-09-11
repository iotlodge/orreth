# PROVENANCE: Claude Fable 5 (claude-fable-5) — 0070 sp4, the scrub · 2026-09-11
"""When-words (0070 §3.1) — a small deterministic relative-date parser.

In plain words: «last Tuesday», «yesterday», «three days ago» become real
dates, deterministically, so the scrub can ask the record a question the
record can actually answer. Ambiguous when-words («recently», «a while
back») are RECOGNIZED and named — never guessed at: the reply says what it
can parse instead of inventing a date (the 0066 escalation pattern joins
here the day a governed consult earns the seat; the honest park stands
until then).
"""
from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone

from .identity import NOW

_WEEKDAYS = ("monday", "tuesday", "wednesday", "thursday", "friday",
             "saturday", "sunday")
_NUMS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
         "seven": 7, "eight": 8, "nine": 9, "ten": 10, "a": 1, "an": 1}

AMBIGUOUS = ("recently", "a while back", "a while ago", "the other day",
             "some time ago", "earlier", "before")


def _today(now: str | None) -> datetime:
    s = now or NOW()
    return datetime.strptime(s[:10], "%Y-%m-%d").replace(tzinfo=timezone.utc)


def ambiguous(text: str) -> str | None:
    """The when-word this parser refuses to guess at — named, so the reply
    can say «give me a date or last-Tuesday-like words» instead of lying."""
    low = (text or "").lower()
    for p in AMBIGUOUS:
        if re.search(rf"\b{re.escape(p)}\b", low):
            return p
    return None


def parse(text: str, now: str | None = None) -> tuple[str | None, str | None]:
    """The first relative when-word in the text → (iso-date, the phrase
    matched), or (None, None). Deterministic against `now` (ISO, defaults
    to the clock)."""
    low = (text or "").lower()
    today = _today(now)

    m = re.search(r"\b(?:the\s+)?day\s+before\s+yesterday\b", low)
    if m:
        return (today - timedelta(days=2)).strftime("%Y-%m-%d"), m.group(0)
    m = re.search(r"\byesterday\b", low)
    if m:
        return (today - timedelta(days=1)).strftime("%Y-%m-%d"), "yesterday"
    m = re.search(r"\btoday\b", low)
    if m:
        return today.strftime("%Y-%m-%d"), "today"
    m = re.search(r"\b(last|this)\s+(" + "|".join(_WEEKDAYS) + r")\b", low)
    if m:
        which, day = m.group(1), _WEEKDAYS.index(m.group(2))
        back = (today.weekday() - day) % 7
        if which == "last" and back == 0:
            back = 7                          # «last Tuesday» ON a Tuesday
                                              # means a week back, always
        return (today - timedelta(days=back)).strftime("%Y-%m-%d"), m.group(0)
    m = re.search(r"\b(\d+|" + "|".join(_NUMS) + r")\s+(day|week|month)s?\s+ago\b",
                  low)
    if m:
        n = int(m.group(1)) if m.group(1).isdigit() else _NUMS[m.group(1)]
        unit = m.group(2)
        days = n * (7 if unit == "week" else 30 if unit == "month" else 1)
        return (today - timedelta(days=days)).strftime("%Y-%m-%d"), m.group(0)
    m = re.search(r"\blast\s+week\b", low)
    if m:
        return (today - timedelta(days=7)).strftime("%Y-%m-%d"), "last week"
    m = re.search(r"\blast\s+month\b", low)
    if m:
        return (today - timedelta(days=30)).strftime("%Y-%m-%d"), "last month"
    return None, None
