# PROVENANCE: Fable 5 (claude-fable-5) — 0043 sp1, the flight recorder · 2026-07-30
"""The Flight Recorder (0043 sp1): the Observatory's senses.

Observability is a PROJECTION over the signed log — never a second truth (rule 7),
never a sidecar. The taps are the choke points that already exist: the model-plane
gateway (every governed thought — coverage total by construction, rule 5), the
farm's meter (every tool call, per worldline), the fingertip's branches (span
timing riding the choreography records), and the gates (how long consequence
waited for a human — a first-class metric almost nobody measures).

Two tiers (LOCKED, JB 2026-07-30): assay records are signed Chronicle records
(they arrive with vera, sp2); instrument SERIES — what this module keeps — are a
projection with DECLARED retention, rebuildable from the log wherever they claim
log-truth, and labeled "instrument reading, not testimony" where they are
performance-derived. The metabolism applies to its own telemetry: raw distills
to hourly, hourly to daily, each climb with MEASURED loss (0033's discipline),
and nothing undistilled is ever swept — even the monitoring ages honestly.
Lived time stays monotone (rule 8): a reading backdated into a sealed bucket is
refused, loudly.
"""
from __future__ import annotations

from datetime import datetime, timezone

TIERS = ("log-truth", "instrument")
INSTRUMENT_LABEL = "instrument reading, not testimony"

HOUR, DAY = 3600, 86400
# the declared retention law — visible on every Series, never implicit
DEFAULT_RETENTION = {"raw": 6 * HOUR, "hourly": 7 * DAY, "daily": 90 * DAY}


class BackdatedReading(Exception):
    """A reading aimed at a bucket already distilled — lived time is monotone (0004),
    and the instruments keep the same law as the memory they watch."""


class TierConflict(Exception):
    """A metric wears one tier for life: a number cannot be log-truth in one
    breath and an instrument reading in the next."""


def _epoch(iso: str) -> float:
    return datetime.fromisoformat(iso.replace("Z", "+00:00")).timestamp()


def _iso(epoch: float) -> str:
    return datetime.fromtimestamp(epoch, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def reading(at: str, metric: str, value: float, *, tier: str,
            labels: dict | None = None) -> dict:
    """The normal form every tap emits: when, what, how much, under which labels —
    and which TIER the number belongs to, declared at birth, never inferred."""
    assert tier in TIERS, f"unknown tier '{tier}'"
    return {"at": at, "metric": metric, "value": float(value), "tier": tier,
            "labels": dict(labels or {})}


# ---- the taps: pure extractors over books that already exist ---------------------------

def _plane_rows(rows: list[dict], floor: str | None) -> list[dict]:
    lbl_floor = {"floor": floor} if floor else {}
    out: list[dict] = []
    for e in rows:
        at = e.get("at", "")
        taxon = e.get("refusal") or e.get("refused")
        if taxon:
            out.append(reading(at, "plane.refusals", 1, tier="instrument",
                               labels={"taxon": taxon, **lbl_floor}))
            continue
        if "lifecycle_warning" in e:
            out.append(reading(at, "plane.lifecycle_warnings", 1, tier="instrument",
                               labels={"model": e["lifecycle_warning"], **lbl_floor}))
            continue
        labels = {"model": e.get("model") or e.get("served_tier", ""),
                  "class": e.get("class") or e.get("requested_tier", ""), **lbl_floor}
        out.append(reading(at, "plane.thoughts", 1, tier="log-truth", labels=labels))
        tokens = e.get("tokens", e.get("charged"))
        if tokens is not None:
            out.append(reading(at, "plane.tokens", tokens, tier="log-truth",
                               labels=labels))
        if "usd" in e:
            out.append(reading(at, "plane.usd", e["usd"], tier="log-truth",
                               labels=labels))
        if "ms" in e:
            out.append(reading(at, "plane.thought_ms", e["ms"], tier="instrument",
                               labels=labels))
    return out


def plane_readings(gateway, *, floor: str | None = None) -> list[dict]:
    """The flight recorder's first tap (0043 §4): the model plane's own meter.
    Reads BOTH doors — the residents' LiveGateway and the workforce ModelGateway —
    because every governed thought passes one of them (rule 5): coverage is total
    by construction. Tokens, dollars, and thought counts are log-truth (the meter
    rolls up via RunRecords, 0005); latency and the refusal taxonomy are the
    gateway's own clock and book — instrument readings, and labeled so. The
    taxonomy lives HERE only: outside, refusal wears one face (rule 4)."""
    return _plane_rows(gateway.call_log, floor)


def _farm_rows(meter_rows: list[dict], event_rows: list[dict]) -> list[dict]:
    out: list[dict] = []
    for m in meter_rows:
        labels = {"service": m["service"]}
        out.append(reading(m["at"], "farm.calls", 1, tier="log-truth", labels=labels))
        if not m.get("ok", True):
            out.append(reading(m["at"], "farm.errors", 1, tier="log-truth",
                               labels=labels))
        out.append(reading(m["at"], "farm.call_ms", m.get("ms", 0),
                           tier="instrument", labels=labels))
    for e in event_rows:
        out.append(reading(e["at"], "farm.transitions", 1, tier="log-truth",
                           labels={"service": e["service"], "event": e["event"]}))
    return out


def farm_readings(farm) -> list[dict]:
    """The second tap: charlotte's meter and the worldline's raw material. Call
    volume and outcomes are log-truth (the keeper's book — on the wire, worldline
    events land as signed records); per-call latency is the meter's stopwatch —
    an instrument reading. Rug-pull correlation falls out for free: transitions
    and error rates share a service label."""
    return _farm_rows(farm.meter_log, farm.events)


def span_readings(branches) -> list[dict]:
    """The third tap: span timing riding the choreography (0043 §4 — the records
    already exist; sp1 just gave them a stopwatch). The branch outcome is
    log-truth (intention-outcome records land signed); the milliseconds are the
    dispatcher's clock — instrument."""
    out: list[dict] = []
    for b in branches:
        span = b.get("span")
        if not span:
            continue
        labels = {"intention": b.get("intention", ""),
                  "seat": b.get("seat", ""), "status": span.get("status", "")}
        out.append(reading(span["ended"], "flow.branches", 1, tier="log-truth",
                           labels=labels))
        out.append(reading(span["ended"], "flow.span_ms", span.get("ms", 0),
                           tier="instrument", labels=labels))
    return out


def gate_reading(esc: dict, *, now: str,
                 rejected_at: dict | None = None) -> dict | None:
    """One escalation's wait, from stamps the record already carries (log-truth):
    a pending item's age (a gauge against now), an approval's staged→approved,
    an expiry's full TTL — silence is denial AT expires_at, by law. A rejection's
    clock lives only in the queue's own book (the contract holds no decided
    stamp), so it rides as an instrument reading — the two-tier law, honestly."""
    staged = _epoch(esc["staged_at"])
    labels = {"action_class": esc["action_class"]}
    if esc["state"] == "pending":
        return reading(now, "gate.wait_age_s", _epoch(now) - staged,
                       tier="log-truth", labels={**labels, "state": "pending"})
    if esc["state"] in ("approved", "executed"):
        return reading(esc["approved_at"], "gate.wait_s",
                       _epoch(esc["approved_at"]) - staged,
                       tier="log-truth", labels={**labels, "outcome": "approved"})
    if esc["state"] == "expired":
        return reading(esc["expires_at"], "gate.wait_s",
                       _epoch(esc["expires_at"]) - staged,
                       tier="log-truth", labels={**labels, "outcome": "expired"})
    if esc["state"] == "rejected" and esc["id"] in (rejected_at or {}):
        at = rejected_at[esc["id"]]
        return reading(at, "gate.wait_s", _epoch(at) - staged,
                       tier="instrument", labels={**labels, "outcome": "rejected"})
    return None


def gate_readings(queue, *, now: str) -> list[dict]:
    """The fourth tap: gate-wait ages across a whole queue — how long consequence
    waited for a human (0043 §4: first-class, and almost nobody measures it)."""
    rejected = {d["id"]: d["at"] for d in getattr(queue, "decisions", [])
                if d.get("outcome") == "rejected"}
    out = [gate_reading(esc, now=now, rejected_at=rejected)
           for esc in queue.items.values()]
    return [r for r in out if r is not None]


# ---- the series: a projection with a declared retention law -----------------------------

def _summarize(points: list[tuple[float, float]]) -> dict:
    """One bucket's distillate — and its MEASURED loss: the mean absolute error
    of standing every point on the bucket mean, normalized by the bucket's range.
    Constant readings distill losslessly and say so; spread costs, visibly."""
    vals = [v for _, v in points]
    n, s = len(vals), sum(vals)
    lo, hi, mean = min(vals), max(vals), s / len(vals)
    loss = round(sum(abs(v - mean) for v in vals) / n / (hi - lo), 4) if hi > lo else 0.0
    return {"count": n, "sum": round(s, 6), "min": lo, "max": hi,
            "mean": round(mean, 6), "loss": loss}


class Series:
    """Tier two of the storage law (0043 §3, LOCKED): the instrument series.

    A projection, never a record store: raw points bucket by hour; complete hours
    distill to hourly summaries, complete days to daily — each climb carrying its
    measured loss like every other memory (0033). Retention is DECLARED at
    construction and visible forever after; sweep distills BEFORE it drops, so
    nothing undistilled is ever lost; and a metric wears one tier for life."""

    def __init__(self, retention: dict | None = None):
        r = dict(DEFAULT_RETENTION, **(retention or {}))
        assert set(r) == {"raw", "hourly", "daily"} and all(v > 0 for v in r.values())
        self.retention = r
        self.tiers: dict[str, str] = {}                  # metric -> its one tier
        self.raw: dict[tuple, list[tuple[float, float]]] = {}
        self.hourly: dict[tuple, dict[float, dict]] = {}
        self.daily: dict[tuple, dict[float, dict]] = {}

    @staticmethod
    def _key(metric: str, labels: dict) -> tuple:
        return (metric, tuple(sorted(labels.items())))

    def ingest(self, readings: list[dict]) -> int:
        """Append readings to the raw shelf. A metric that arrives wearing a
        different tier than it wore before is refused (TierConflict); a reading
        aimed at an hour this series already sealed is refused (BackdatedReading
        — rule 8 reaches the instruments too)."""
        n = 0
        for r in readings:
            metric, tier = r["metric"], r["tier"]
            worn = self.tiers.setdefault(metric, tier)
            if worn != tier:
                raise TierConflict(f"{metric} wears '{worn}', not '{tier}'")
            key = self._key(metric, r["labels"])
            at = _epoch(r["at"])
            hour = at // HOUR * HOUR
            if hour in self.hourly.get(key, {}):
                raise BackdatedReading(
                    f"{metric} at {r['at']}: that hour is already distilled")
            self.raw.setdefault(key, []).append((at, r["value"]))
            n += 1
        return n

    def distill(self, *, now: str) -> dict:
        """The metabolism, applied to the telemetry itself: every COMPLETE hour's
        raw points become one summary with measured loss; every complete day's
        hourly summaries merge upward — count/sum/min/max carried exactly, the
        hour-to-hour shape priced as the day's loss. Idempotent on a quiet shelf."""
        t = _epoch(now)
        cut = {"hourly": 0, "daily": 0}
        for key, pts in self.raw.items():
            by_hour: dict[float, list] = {}
            for at, v in pts:
                by_hour.setdefault(at // HOUR * HOUR, []).append((at, v))
            for hour, hpts in sorted(by_hour.items()):
                if hour + HOUR <= t and hour not in self.hourly.get(key, {}):
                    self.hourly.setdefault(key, {})[hour] = _summarize(hpts)
                    cut["hourly"] += 1
        for key, hours in self.hourly.items():
            by_day: dict[float, list[float]] = {}
            for hour in hours:
                by_day.setdefault(hour // DAY * DAY, []).append(hour)
            for day, hlist in sorted(by_day.items()):
                if day + DAY <= t and day not in self.daily.get(key, {}):
                    hs = [hours[h] for h in sorted(hlist)]
                    means = [h["mean"] for h in hs]
                    lo, hi = min(means), max(means)
                    count = sum(h["count"] for h in hs)
                    total = sum(h["sum"] for h in hs)
                    dmean = total / count
                    loss = round(sum(abs(m - dmean) for m in means) / len(means)
                                 / (hi - lo), 4) if hi > lo else 0.0
                    self.daily.setdefault(key, {})[day] = {
                        "count": count, "sum": round(total, 6),
                        "min": min(h["min"] for h in hs),
                        "max": max(h["max"] for h in hs),
                        "mean": round(dmean, 6), "loss": loss}
                    cut["daily"] += 1
        return cut

    def sweep(self, *, now: str) -> dict:
        """Retention, enforced in the declared order: distill FIRST, then drop
        what has both climbed and aged out. Raw survives until its hour is
        sealed; hourly survives until its day is; daily simply ages by its
        declared horizon. The report says what left — no silent caps."""
        self.distill(now=now)
        t = _epoch(now)
        dropped = {"raw": 0, "hourly": 0, "daily": 0}
        for key, pts in self.raw.items():
            keep = [(at, v) for at, v in pts
                    if not (at // HOUR * HOUR in self.hourly.get(key, {})
                            and t - at > self.retention["raw"])]
            dropped["raw"] += len(pts) - len(keep)
            self.raw[key] = keep
        for key, hours in self.hourly.items():
            gone = [h for h in hours
                    if h // DAY * DAY in self.daily.get(key, {})
                    and t - h > self.retention["hourly"]]
            for h in gone:
                del hours[h]
            dropped["hourly"] += len(gone)
        for key, days in self.daily.items():
            gone = [d for d in days if t - d > self.retention["daily"]]
            for d in gone:
                del days[d]
            dropped["daily"] += len(gone)
        return dropped

    def read(self, metric: str, *, resolution: str = "raw",
             labels: dict | None = None) -> dict:
        """What the glass will drink (sp3): every answer declares its tier, and
        an instrument metric wears its label in the payload — the panel never
        has to remember to say it."""
        assert resolution in ("raw", "hourly", "daily")
        want = set((labels or {}).items())
        tier = self.tiers.get(metric, "instrument")
        shelf = {"raw": self.raw, "hourly": self.hourly, "daily": self.daily}[resolution]
        points: list[dict] = []
        for (m, lbl), data in shelf.items():
            if m != metric or not want <= set(lbl):
                continue
            if resolution == "raw":
                points += [{"at": _iso(at), "value": v, "labels": dict(lbl)}
                           for at, v in data]
            else:
                points += [{"at": _iso(b), **s, "labels": dict(lbl)}
                           for b, s in sorted(data.items())]
        points.sort(key=lambda p: p["at"])
        return {"metric": metric, "tier": tier, "resolution": resolution,
                **({"label": INSTRUMENT_LABEL} if tier == "instrument" else {}),
                "points": points}


def percentiles(series: "Series", metric: str, *, labels: dict | None = None,
                qs: tuple = (0.5, 0.95)) -> dict:
    """The WATCH depth (0043 §5): distributions and percentiles read from the
    raw shelf the glance already keeps — a deeper read, never a new
    collection, so turning the dial up costs reading, not gathering. Linear
    interpolation between ranks; the answer carries the series' tier and
    label like every other read."""
    base = series.read(metric, labels=labels)
    vals = sorted(p["value"] for p in base["points"])
    out = dict(base, resolution="percentiles")
    del out["points"]
    if not vals:
        return {**out, "n": 0, "quantiles": {}}
    quant = {}
    for q in qs:
        pos = q * (len(vals) - 1)
        lo, hi = int(pos), min(int(pos) + 1, len(vals) - 1)
        quant[f"p{int(q * 100)}"] = round(
            vals[lo] + (vals[hi] - vals[lo]) * (pos - lo), 4)
    return {**out, "n": len(vals), "min": vals[0], "max": vals[-1],
            "quantiles": quant}


class FlightRecorder:
    """sp1's assembled face: the four taps, swept on the beat into one Series.
    Cursors keep counters honest across sweeps (a call metered once is a call
    counted once); pending gate ages are gauges and sample fresh every beat; a
    decided gate and a branch's span each record exactly once. The wire twin
    mirrors this shape."""

    def __init__(self, series: Series | None = None):
        self.series = series or Series()
        self._cursor: dict[tuple, int] = {}      # (source id, book) -> rows consumed
        self._graded: set[str] = set()           # escalations whose wait is recorded
        self._spanned: set[tuple] = set()        # (goal, intention) spans recorded

    def _fresh(self, source, book: str, rows: list) -> list:
        key = (id(source), book)
        seen = self._cursor.get(key, 0)
        self._cursor[key] = len(rows)
        return rows[seen:]

    def sweep(self, *, now: str, gateways: list | None = None,
              farms: list | None = None, queues: list | None = None,
              flights: list | None = None) -> int:
        """One beat: drain every tap's fresh rows, sample the gauges, distill."""
        batch: list[dict] = []
        for g in gateways or []:
            batch += _plane_rows(self._fresh(g, "calls", g.call_log), None)
        for f in farms or []:
            batch += _farm_rows(self._fresh(f, "meter", f.meter_log),
                                self._fresh(f, "events", f.events))
        for q in queues or []:
            rejected = {d["id"]: d["at"] for d in getattr(q, "decisions", [])
                        if d.get("outcome") == "rejected"}
            for esc_id, esc in q.items.items():
                r = gate_reading(esc, now=now, rejected_at=rejected)
                if r is None:
                    continue
                if r["metric"] == "gate.wait_s":     # decided: once, ever
                    if esc_id in self._graded:
                        continue
                    self._graded.add(esc_id)
                batch.append(r)
        for orch in flights or []:
            fresh = [b for iid, b in orch.branches.items()
                     if b.get("span") and (orch.goal, iid) not in self._spanned]
            for b in fresh:
                self._spanned.add((orch.goal, b["intention"]))
            batch += span_readings(fresh)
        n = self.series.ingest(batch)
        self.series.distill(now=now)
        return n
