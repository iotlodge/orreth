# PROVENANCE: Claude Fable 5 (claude-fable-5) — 0071 sp4, the traffic law · 2026-09-09
"""The traffic law (0071 sp4): how often a caller may knock. The fuel clause meters
THINKING (model tokens); this meters KNOCKING (requests per window), per identity,
inside human-set ceilings.

The law is a fixed window, deliberately simple: N knocks per identity per window;
the window turns on the clock, and a refused knock names how long to wait. The
reference here is pure arithmetic — the plane carries its Rust twin, the worker
wires this one; both answer an over-limit caller the same way: a plain 'busy for
you' with a retry hint, never a leak about anyone else's traffic.
"""
from __future__ import annotations

WINDOW_S = 60


def tick(book: dict, key: str, now_s: float, limit: int,
         window_s: int = WINDOW_S) -> tuple[bool, int]:
    """One knock by `key` at `now_s`. Returns (allowed, retry_after_s).
    `book` is the caller's ledger: key -> [window_start_s, count] — mutated
    in place; a turned window resets the count. limit <= 0 means the door
    is unmetered (the operator's explicit choice, never a default)."""
    if limit <= 0:
        return True, 0
    entry = book.get(key)
    if entry is None or now_s - entry[0] >= window_s:
        book[key] = [now_s, 1]
        return True, 0
    if entry[1] < limit:
        entry[1] += 1
        return True, 0
    return False, max(1, int(entry[0] + window_s - now_s))


def sweep(book: dict, now_s: float, window_s: int = WINDOW_S) -> None:
    """Forget turned windows so the book never grows with dead callers."""
    for k in [k for k, v in book.items() if now_s - v[0] >= window_s]:
        book.pop(k, None)
