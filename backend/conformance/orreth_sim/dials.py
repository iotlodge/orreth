# PROVENANCE: Fable 5 (claude-fable-5) — the dial registry (0063 sp1) · 2026-08-28
"""The machine's operating values, DECLARED — 0063's first machinery.

The separation is L1's own condition (JB, 2026-08-28): a dial's SHAPE is
firmware and lives here — name, type, unit, bounds, what it governs, its
blast radius, and the why that chose it. Its VALUE is purpose and lives on
the shelf as a `dial-*` asset, turned through the one-motion craft-edit
door like any craft — versioned siblings, lineage kept, never a code edit.
Words steer minds; dials steer the machine — one shelf, two clearly
separate drawers.

Genesis honors the env (0063 §3.6 — env demotes to genesis): the ORRETH_*
variable seeds the FIRST value on a fresh rig, never the standing one.
The read-side law lives in parse(): a head that refuses its declaration
falls back to genesis LOUDLY, never silently.
"""
from __future__ import annotations

import os

# window.html carries this same map as ITS genesis fallback — the two must
# match byte-for-byte (rule 7: one world, one picture; the conformance
# suite holds the parity)
KINDRANK_GENESIS = {
    "attestation": 0, "testament": 1, "consent": 2, "passage": 2,
    "publish": 3, "drift": 3, "release": 3, "witness": 3, "fuel": 3,
    "objective": 4, "improvement": 4, "experiment": 4, "commission": 4,
    "subscription": 4,
    "design-change": 5, "calibration": 5, "estate-adopt": 5, "field-join": 5,
    "join": 6, "ecosystem": 6, "dial": 6, "question": 7,
}

def _cad(env, default, governs, blast, why, *, lo=30, hi=604800):
    """A cadence declaration (0063 sp6 wave 1 — the _EVERY family): one
    shape for the machine's rhythms. env=None means the code literal was
    the only genesis there ever was — the gate is its first tunability."""
    return {"type": "int", "unit": "seconds between beats", "min": lo,
            "max": hi,
            "genesis": (int(os.environ.get(env, str(default)))
                        if env else default),
            "home": "universe", "governs": governs, "blast": blast,
            "why": why, "horizon": "takes hold within a minute"}


# home (0063 sp3 — the ladder): "universe" = one value for the whole rig,
# turned only at the universe's own door; "ladder" = a floor may carry its
# OWN override on its own shelf, and the most specific word wins (the 0059
# allocation law: subject → floor → universe)
DIALS_V1 = {
    # ── the machine's rhythms (sp6 wave 1 — the cadence family) ──────────
    "passage-every": _cad("ORRETH_PASSAGE_EVERY", 60,
        "how often lived time is stamped into the record (0004)",
        "the machine's sense of time — too slow blurs the calendar",
        "one minute matched the demo's day"),
    "embed-every": _cad("ORRETH_EMBED_EVERY", 90,
        "how often new records earn their meaning vectors (0022)",
        "meaning lags the record when slow; churn when fast",
        "ninety seconds keeps pgvector warm without churn"),
    "mirror-every": _cad("ORRETH_MIRROR_EVERY", 600,
        "how often the Mirror assesses conversations (0034)",
        "reflection cost against staleness",
        "ten minutes was the reveal-era balance"),
    "monitor-every": _cad(None, 600,
        "how often the monitor sweeps standing objectives",
        "silent stalls found late",
        "the code's own 600 — it never had an env; the gate is its "
        "first tunability"),
    "improver-every": _cad("ORRETH_IMPROVER_EVERY", 600,
        "how often the improver reads the receipts (0028)",
        "proposal storms when fast, a frozen engine when slow",
        "ten minutes since 0028"),
    "epoch-every": _cad("ORRETH_EPOCH_EVERY", 300,
        "how often the machine checks its own name (0041)",
        "drift found late when slow, churn when fast",
        "five minutes names drift within a coffee"),
    "lag-window": _cad("ORRETH_LAG_WINDOW", 900,
        "how much heartbeat silence counts as a floor lagging",
        "false drift floods when tight (the 0052 lesson), blind lag "
        "when loose",
        "the drift-flood morning sized it"),
    "metabolism-every": _cad("ORRETH_METABOLISM_EVERY", 900,
        "how often ONE floor draws its metabolism breath (0057, "
        "round-robin)",
        "churn when fast, a constipated corpus when slow — rig-wide",
        "fifteen minutes rounds every floor within hours"),
    "assay-every": _cad("ORRETH_ASSAY_EVERY", 300,
        "how often vera samples finished work at the assay dial (0043)",
        "token spend against her declared ceiling",
        "five minutes at assay tier"),
    "verify-every": _cad("ORRETH_VERIFY_EVERY_S", 3600,
        "how often the deed watchman re-checks public deeds (0044)",
        "tampers found late when slow, wasted checks when fast",
        "the hour matched the bell's own cooldown"),
    "cal-every": _cad(None, 120,
        "how often calibration compares the human's thumbs to the "
        "examiner (0048)",
        "a stale calibration gauge",
        "the code's own 120 — it never had an env; the gate is its "
        "first tunability"),
    "brain-census-every": _cad("ORRETH_BRAIN_CENSUS_EVERY", 300,
        "how often the Brain's memory census refreshes",
        "a stale gauge in the glass",
        "five minutes suits a wall gauge"),
    # ── the desk's windows and the judgment bars (sp6 wave 5) ────────────
    "improver-success-floor": {
        "type": "int", "unit": "percent success", "min": 0, "max": 100,
        "genesis": 90, "home": "universe",
        "governs": "below this success rate the receipts earn the improver's "
                   "nudge (0028) — at or above, healthy assets are left alone",
        "blast": "proposal storms below a high bar, a frozen engine above "
                 "a low one",
        "why": "ninety kept the engine quiet on honest work",
        "horizon": "takes hold at the improver's next look",
    },
    "studio-dark": {
        "type": "int", "unit": "seconds of silence", "min": 10, "max": 3600,
        "genesis": int(os.environ.get("ORRETH_STUDIO_DARK_S", "90")),
        "home": "universe",
        "governs": "how long the studio's reading may stay silent before "
                   "the card confesses it dark (0047)",
        "blast": "false darkness below, a hung reading hidden above",
        "why": "ninety seconds outlasts a slow thought without hiding "
               "a dead one",
        "horizon": "takes hold within a minute",
    },
    "schedule-every-default": {
        "type": "int", "unit": "days between runs", "min": 1, "max": 90,
        "genesis": 7, "home": "universe",
        "governs": "the DEFAULT rhythm of a standing schedule when the "
                   "human's word names none — the word always wins",
        "blast": "a standing word becomes a spend loop when fast",
        "why": "weekly — the yardstick's own cadence (JB's)",
        "horizon": "takes hold at the next scheduling word",
    },
    "cal-min-n": {
        "type": "int", "unit": "overlapping pairs", "min": 1, "max": 100,
        "genesis": 5, "home": "universe",
        "governs": "the least human-vs-examiner pairs before calibration "
                   "speaks at all (0048 sp4)",
        "blast": "one thumb indicts vera below, calibration mute above",
        "why": "five pairs is the smallest honest sample",
        "horizon": "takes hold at the next calibration beat",
    },
    "cal-bar": {
        "type": "float", "unit": "mean gap, 0..1", "min": 0.0, "max": 1.0,
        "genesis": 0.4, "home": "universe",
        "governs": "the mean human-vs-examiner gap that becomes a card "
                   "(news, never a lever — 0043 law 3)",
        "blast": "noise below, a drifted examiner unreported above",
        "why": "0.4 separates taste from disagreement",
        "horizon": "takes hold at the next calibration beat",
    },
    "assay-floor-mean": {
        "type": "float", "unit": "mean score, 0..1", "min": 0.0, "max": 1.0,
        "genesis": 0.55, "home": "universe",
        "governs": "the mean assay score under which a floor's standing "
                   "becomes a degradation card (0043)",
        "blast": "alarm fatigue above, quiet decay below",
        "why": "0.55 caught the real degradations without crying wolf",
        "horizon": "takes hold at the next assay round",
    },
    "assay-trend-drop": {
        "type": "float", "unit": "score drop, 0..1", "min": 0.0, "max": 1.0,
        "genesis": 0.15, "home": "universe",
        "governs": "the falling-trend size that becomes a degradation card "
                   "even above the floor (0043)",
        "blast": "trend noise below, a slow slide unseen above",
        "why": "0.15 is a real slide, not jitter",
        "horizon": "takes hold at the next assay round",
    },
    # ── leases and fuel (sp6 wave 4 — the roster's breathing terms) ──────
    "join-lease-days": {
        "type": "int", "unit": "days a lease breathes", "min": 1, "max": 365,
        "genesis": int(float(os.environ.get("ORRETH_JOIN_LEASE_DAYS", "30"))),
        "home": "universe",
        "governs": "how long a join lease lives before re-join renews it — "
                   "a lapsed lease is dormancy, never death (2026-08-20)",
        "blast": "short churns renewals; long discovers dormancy late",
        "why": "thirty days — a month's honest tenancy",
        "horizon": "takes hold at the next join or renewal",
    },
    "join-lease-tokens": {
        "type": "int", "unit": "tokens of allowance per window", "min": 1000,
        "max": 2000000,
        "genesis": int(os.environ.get("ORRETH_JOIN_LEASE_TOKENS", "50000")),
        "home": "universe",
        "governs": "the fuel allowance a joining agent's lease carries "
                   "per renew window (0058)",
        "blast": "starves a mind mid-thought below, loosens the spend "
                 "guard above",
        "why": "the env seeds this genesis, so the shelf finally shows the "
               "STANDING truth — the old code default and the rig's real "
               "value were never the same number",
        "horizon": "takes hold at the next join or renewal",
    },
    "lease-renew-days": {
        "type": "int", "unit": "days per allowance window", "min": 0,
        "max": 90,
        "genesis": int(float(os.environ.get("ORRETH_LEASE_RENEW_DAYS", "1"))),
        "home": "universe",
        "governs": "the fuel clause's window — the allowance refills every "
                   "this-many days; 0 keeps the old lump posture (0058)",
        "blast": "the vera-419 wound's family — a lump drains silently "
                 "and nobody is told",
        "why": "daily, the search ceiling's own grain (0054 L-A)",
        "horizon": "takes hold at the next join or renewal",
    },
    "floor-capacity": {
        "type": "int", "unit": "seats declared present", "min": 1, "max": 500,
        "genesis": int(os.environ.get("ORRETH_FLOOR_CAPACITY", "20")),
        "home": "ladder",
        "governs": "the floor's declared capacity — INFORMS the join "
                   "gate's confession, never decides it: the human's word "
                   "stays the door (0012, rule 3)",
        "blast": "a false confession either way — the gate still asks",
        "why": "twenty seats read honestly on the demo rig; a floor may "
               "earn its own word (the roster's own seed, 2026-08-20)",
        "horizon": "takes hold at the next join confession",
    },
    "fuel-est-floor": {
        "type": "int", "unit": "tokens one thought needs", "min": 50,
        "max": 5000, "genesis": 500, "home": "universe",
        "governs": "the line under every lease: a remaining allowance "
                   "below this cannot clear one typical governed thought "
                   "and reads DRAINED, whatever dust remains",
        "blast": "drains confessed too late below, false alarms above",
        "why": "the worker's estimates run ~40 to ~500+; the wound's own "
               "number, 419, must fall on the drained side of this line",
        "horizon": "takes hold at the next drain watch",
    },
    # ── the bell (sp6 wave 3 — the highest consequence per dial) ─────────
    "bell-cooldown": {
        "type": "int", "unit": "seconds between rings", "min": 300,
        "max": 604800,
        "genesis": int(os.environ.get("ORRETH_BELL_COOLDOWN_S", "3600")),
        "home": "universe",
        "governs": "the least quiet between two rings of your REAL inbox — "
                   "a repeat inside the window ages into the standing email "
                   "(0044 law 6)",
        "blast": "spam below, a silenced second alarm above — your inbox's "
                 "peace either way",
        "why": "one hour matched the witness's own window",
        "horizon": "takes hold within a minute",
    },
    "bell-gate-age": {
        "type": "int", "unit": "hours a card may wait", "min": 1, "max": 720,
        "genesis": int(os.environ.get("ORRETH_BELL_GATE_AGE_H", "48")),
        "home": "universe",
        "governs": "how long a consequential card may wait at your gate "
                   "before the bell rings ONCE about it (0044 sp3)",
        "blast": "nagging below, a forgotten gate above — and turning it "
                 "DOWN on a rig with old cards standing rings the real "
                 "inbox at once",
        "why": "two days is a weekend's grace",
        "horizon": "takes hold at the next gate-age beat",
    },
    # ── money (sp6 wave 2 — the numbers that spend) ──────────────────────
    "subscription-cadence-beats": {
        "type": "int", "unit": "beats between issues", "min": 10,
        "max": 100800, "genesis": 100, "home": "universe",
        "governs": "the DEFAULT rhythm of a study line when the human's "
                   "ask names none — the ask's own word always wins (0032)",
        "blast": "standing spend frequency — every issue spends its calls",
        "why": "a hundred beats ≈ ten minutes on the demo rig's pulse",
        "horizon": "takes hold at the next subscription approval",
    },
    "subscription-budget-calls": {
        "type": "int", "unit": "governed calls per issue", "min": 1,
        "max": 50, "genesis": 4, "home": "universe",
        "governs": "how many source calls one issue of a study line "
                   "may spend (0032 §1)",
        "blast": "the Tavily family — standing spend per delivery",
        "why": "four covers a digest without a burn",
        "horizon": "takes hold at the next subscription approval",
    },
    "fanout-budget-tokens": {
        "type": "int", "unit": "tokens per fan-out", "min": 500,
        "max": 50000, "genesis": 2400, "home": "universe",
        "governs": "the DEFAULT thought budget an objective's fan-out "
                   "divides among its seats when the ask names none (0047)",
        "blast": "many seats × many tokens — the widest spend lever "
                 "in one place",
        "why": "2400 across a handful of seats kept the studio honest",
        "horizon": "takes hold within a minute",
    },
    "fanout-min-share": {
        "type": "int", "unit": "tokens floor per seat", "min": 10,
        "max": 2000, "genesis": 60, "home": "universe",
        "governs": "the least any seat receives from a fan-out split",
        "blast": "a starved seat mutes mid-thought",
        "why": "sixty tokens is one honest sentence",
        "horizon": "takes hold within a minute",
    },
    "search-daily": {
        "type": "int", "unit": "searches per UTC day", "min": 0, "max": 100,
        "genesis": int(os.environ.get("ORRETH_SEARCH_DAILY", "6")),
        "home": "universe",
        "governs": "live web searches the whole rig may spend in one day",
        "blast": "money — the family the Tavily thousand-credit burn came from",
        "why": "six covers a study day; sized after the Aug-2026 credit burn",
        "horizon": "takes hold within a minute",
    },
    "assay-ceiling": {
        "type": "int", "unit": "tokens per UTC day", "min": 0, "max": 1000000,
        "genesis": int(os.environ.get("ORRETH_ASSAY_DAILY_TOKENS", "25000")),
        "home": "universe",
        "governs": "vera's independent-judge budget per day (0043 G5)",
        "blast": "money and judgment — too low mutes the examiner, "
                 "too high spends unwatched",
        "why": "a day of assays at ~120 tokens each, with honest slack",
        "horizon": "takes hold within a minute",
    },
    "kindrank": {
        "type": "ordering", "unit": "request kind → rank, gravest first",
        "genesis": KINDRANK_GENESIS,
        "home": "universe",
        "governs": "which grievance reaches the human first in the one Inbox",
        "blast": "attention — a wrong order buries the gravest card",
        "why": "attestations and testaments before questions (0052 sp3's "
               "triage); unlisted kinds rank 8",
        "horizon": "takes hold at the glass's next dictionary fetch "
                   "(about a minute)",
    },
    "metabolism-batch": {
        "type": "int", "unit": "records per breath", "min": 10, "max": 2000,
        "genesis": int(os.environ.get("ORRETH_METABOLISM_BATCH", "200")),
        "home": "ladder",
        "governs": "how many undistilled records one floor chews per "
                   "metabolism breath (0057)",
        "blast": "churn or starvation — too small starves distillation, "
                 "too large spikes a breath",
        "why": "200 balanced the 0057 round on the demo rig; a busy floor "
               "may earn its own word",
        "horizon": "the floor's next breath after the minute",
    },
    "improver-cycle-cap": {
        "type": "int", "unit": "max_cycles ceiling", "min": 1, "max": 10,
        "genesis": 5, "home": "universe",
        "governs": "the ceiling the improver may nudge max_cycles toward — "
                   "the machine tunes INSIDE this word, never over it (L3)",
        "blast": "runaway self-tuning above, frozen self-improvement below",
        "why": "5 was the code's own stop since 0028; now it is the "
               "human's word the machine optimizes within",
        "horizon": "takes hold at the improver's next look",
    },
}


def teachings(short: str) -> dict:
    """The declaration's face for a record body and the glass: what the human
    reads BESIDE the value — every version carries its own teaching, so a
    dial record can never be a bare number with amnesia."""
    d = DIALS_V1[short]
    t = {k: d[k] for k in ("type", "unit", "governs", "blast", "why",
                           "horizon", "home")}
    if d["type"] in ("int", "float"):
        t["bounds"] = [d["min"], d["max"]]
    return t


def gate_check(asset_name: str, profile, *, at_floor: bool = False):
    """The DOOR's law (0063 sp2 — bounds are law, refused BEFORE landing):
    returns (flaw, normalized_profile). A flaw means nothing lands and the
    refusal teaches — the bounds, the unit, what the dial governs. A clean
    turn lands CANONICAL (\"2\" becomes 2): the head never carries a shape
    the declaration would refuse at read time. at_floor (sp3 — the ladder):
    a universe-homed dial refuses a floor's door; only a ladder-homed dial
    may carry a floor's own word."""
    short = asset_name[len("dial-"):]
    d = DIALS_V1.get(short)
    if d is None:
        return (f"no declared dial is named “{asset_name}” — a dial's SHAPE "
                f"is firmware, and the registry declares only: "
                + ", ".join(f"dial-{s}" for s in sorted(DIALS_V1)), None)
    if at_floor and d.get("home") != "ladder":
        return (f"this dial lives at the universe alone — “{asset_name}” is "
                "one word for the whole rig; turn it at the universe's own "
                "door. Only ladder-homed dials carry a floor's override", None)
    if not isinstance(profile, dict) or "value" not in profile:
        return ("a dial turns by its value alone — the body is "
                "{\"value\": …}, nothing else", None)
    v, flaw = parse(short, profile["value"])
    if flaw:
        return (f"{flaw} — the declaration holds ({d['unit']}); this dial "
                f"governs {d['governs']}, and its blast is {d['blast']}", None)
    return None, {"value": v}


def parse(short: str, raw):
    """The read-side law: (value, flaw). A flawed head never breaks an organ
    — genesis serves and the flaw is the caller's to confess out loud."""
    d = DIALS_V1[short]
    if d["type"] == "int":
        try:
            v = int(raw)
        except (TypeError, ValueError):
            return d["genesis"], f"not a whole number: {raw!r}"
        if not (d["min"] <= v <= d["max"]):
            return d["genesis"], (f"outside the declared bounds "
                                  f"[{d['min']}..{d['max']}]: {v}")
        return v, None
    if d["type"] == "float":                 # the judgment bars (sp6 w5)
        try:
            v = float(raw)
        except (TypeError, ValueError):
            return d["genesis"], f"not a number: {raw!r}"
        if not (d["min"] <= v <= d["max"]):
            return d["genesis"], (f"outside the declared bounds "
                                  f"[{d['min']}..{d['max']}]: {v}")
        return v, None
    if d["type"] == "ordering":
        if not isinstance(raw, dict) or not raw:
            return d["genesis"], "not a kind→rank map"
        try:
            return {str(k): int(v) for k, v in raw.items()}, None
        except (TypeError, ValueError):
            return d["genesis"], "every rank must be a whole number"
    return d["genesis"], f"unknown dial type {d['type']!r}"
