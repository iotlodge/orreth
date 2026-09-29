# PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch row 4, PANEL sp3: per-door latency in the Monitoring · 2026-09-28
# Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch row 4, re-base sp1: POISON-PARKING — the park once by its place, its fact, the HOLD until a person advances it, the advance · 2026-09-28
"""`orreth.doors/1` — how long every door takes, in the kernel's own words
(canon 0005 row 4, JB's lock 3 of "the kernel that lasts": *a p50 and p95
per door, judged by the same beat that judges watches, so the performance
law is watched before a walk finds it*). The reference half of
`backend/plane/crates/orreth-spine/src/doors.rs`, law for law.

The pure half, measured by `doors-v0.json` on both kernels: a door's NAME
(`door_name` — the method and the route as the router spells it, an id folded
to `:id`, a stranger's path folded to `other` so a scanner never grows the
table) and the FOLD (`fold` — nearest-rank p50 · p95 · the max over the
samples, in integer arithmetic so both languages pick the same sample). The
live half is the ring: every knock this process served lands as one sample
under its door's name, the last KEEP kept, the reading folded over the last
WINDOW_S seconds. The Monitoring reads it (`monitor.snapshot` → `doors` and
`values["door_p95_ms"]`), the judge judges it on the intent beat, the glass
draws it under PERFORMANCE. The ring is this PROCESS's — the doors it served.
"""
from __future__ import annotations

import threading
import time
from collections import deque

KEEP = 256          # samples kept per door
WINDOW_S = 600      # the reading's window: a sample older than this is not folded
SLOW_MS = 1000.0    # a door whose p95 crosses this is slow by the standing law (<= 1 s cold)

# the first path segments the kernel answers (both kernels' doors; anything else is `other`)
KNOWN = frozenset((
    "", "index.html", "feed", "health", "shadow", "ask", "fact", "asks", "residents", "crew",
    "sessions", "session", "recall", "export", "digest", "guide", "proof", "analyzer", "services",
    "intentions", "levers", "markers", "monitor", "profile", "world", "seam", "schedules",
    "harness", "delta", "bodies", "minds", "confirm", "enroll", "seat", "join", "mitl", "impact",
    "mark",
    "parked",           # re-base sp1: the poison events held at, and the advance
))
_ID_AFTER = frozenset(("ask", "fact", "session", "digest", "join"))


def door_name(method: str, path: str) -> str:
    """`METHOD /route` as the router spells it: the second segment folded to
    `:id` after ask · fact · session · digest · join and to `:runner` after
    schedules (except the fixed `/schedules/rest`); deeper segments dropped; a
    first segment the kernel does not answer is `other`. No query in a name."""
    path = path.split("?", 1)[0]
    segs = path.lstrip("/").split("/", 2)
    first = segs[0]
    second = segs[1] if len(segs) > 1 else ""
    method = method.upper()
    if first not in KNOWN:
        return f"{method} other"
    name = f"{method} /{first}"
    if second:
        if first in _ID_AFTER:
            second = ":id"
        elif first == "schedules" and second != "rest":
            second = ":runner"
        name += "/" + second
    return name


def percentile(sorted_ms: list[float], p: int) -> float | None:
    """Nearest rank over an ascending list: the sample at rank ceil(p*n/100),
    in integer arithmetic. None on no samples."""
    n = len(sorted_ms)
    if n == 0:
        return None
    rank = max(1, -(-(p * n) // 100))
    return sorted_ms[rank - 1]


def fold(samples_ms) -> dict:
    """One door's samples folded: how many, the p50, the p95 and the max —
    each an actual sample (no arithmetic on the values), None on none."""
    s = sorted(float(v) for v in samples_ms if v == v and v not in (float("inf"), float("-inf")))
    return {"n": len(s), "p50_ms": percentile(s, 50), "p95_ms": percentile(s, 95),
            "max_ms": s[-1] if s else None}


def door_view(door: str, samples_ms) -> dict:
    v = fold(samples_ms)
    v["door"] = door
    return v


def slowest_first(reads: list[dict]) -> list[dict]:
    """The readings ordered the slowest first (by p95, then by name)."""
    return sorted(reads, key=lambda r: (-(r.get("p95_ms") or 0.0), r["door"]))


def slowest_p95(reads: list[dict]) -> float:
    """The metric the watches read: the slowest door's p95 now (0 when none)."""
    return max((r["p95_ms"] for r in reads if r.get("p95_ms") is not None), default=0.0)


class Doors:
    """The ring of samples — this process's doors."""

    def __init__(self):
        self._rings: dict[str, deque] = {}
        self._lock = threading.Lock()

    def record(self, door: str, ms: float) -> None:
        with self._lock:
            self._rings.setdefault(door, deque(maxlen=KEEP)).append((time.monotonic(), float(ms)))

    def read(self) -> list[dict]:
        now = time.monotonic()
        with self._lock:
            reads = []
            for door, ring in self._rings.items():
                recent = [ms for at, ms in ring if now - at < WINDOW_S]
                if recent:
                    reads.append(door_view(door, recent))
        return slowest_first(reads)

    def clear(self) -> None:
        with self._lock:
            self._rings.clear()


DOORS = Doors()      # this process's ring


def record(method: str, path: str, ms: float) -> None:
    """One knock served by this process (the feed is a stream, never timed)."""
    DOORS.record(door_name(method, path), ms)


def read() -> list[dict]:
    return DOORS.read()
