# PROVENANCE: Fable 5 (claude-fable-5) — 0043 sp1, the flight recorder · 2026-07-30
"""The Flight Recorder (0043 sp1) — the Observatory's senses, under conformance.

Under test: the plane's meter becomes a flight recorder (latency, tokens, and a
refusal taxonomy that lives only in the gateway's own book — outside, refusal
keeps its one face); the farm meters errors per worldline; the fingertip wears
spans and the choreography carries them; gate-wait is a first-class metric with
the two-tier law applied honestly (a rejection's clock is an instrument, never
testimony); a metric wears one tier for life; the series distills with MEASURED
loss; retention is declared and sweep never eats what has not distilled; hourly
climbs to daily and lived time stays monotone even for instruments; log-truth
rebuilds from the log while instruments wear their label; and the assembled
recorder sweeps without double-counting."""
import sys
import types
from datetime import datetime, timedelta, timezone

import pytest

from orreth_sim import farm as farm_mod
from orreth_sim import fingertip, hitl, observatory
from orreth_sim.agent_surface import BudgetExceeded, join_workforce
from orreth_sim.identity import AuthzError
from orreth_sim.model_plane import LiveGateway, ModelSunset
from orreth_sim.world import build

BASE = datetime(2026, 7, 30, 12, 0, tzinfo=timezone.utc)


def iso(days_ago: float = 0) -> str:
    return (BASE - timedelta(days=days_ago)).strftime("%Y-%m-%dT%H:%M:%SZ")


@pytest.fixture()
def world():
    return build()


def _fake_litellm(monkeypatch, *, prompt_tokens=7, completion_tokens=5):
    m = types.ModuleType("litellm")

    def completion(model, messages, max_tokens):
        usage = types.SimpleNamespace(total_tokens=prompt_tokens + completion_tokens,
                                      prompt_tokens=prompt_tokens,
                                      completion_tokens=completion_tokens)
        msg = types.SimpleNamespace(content="pong")
        return types.SimpleNamespace(usage=usage,
                                     choices=[types.SimpleNamespace(message=msg)])

    m.completion = completion
    m.completion_cost = lambda completion_response: 0.00042
    monkeypatch.setitem(sys.modules, "litellm", m)


def _surface(budget=5000):
    return types.SimpleNamespace(identity={"did": "did:key:zObsTest"},
                                 budget_left=budget)


def _farm():
    f = farm_mod.Farm("u:demo/e:cloud/f:prod")
    f.plant("search", did="did:key:z6MkObsSvc", kind="search", endpoint="http://s")
    f.attest("search", [{"name": "q"}])
    for _ in range(farm_mod.PROBATION_BEATS):
        f.beat("search")
    return f


def _tidy_think(_klass, prompt):
    if "Plan the MINIMUM" in prompt:
        return "OBSERVE reason: the assigned sliver"
    if "Answer concisely" in prompt:
        return "considered"
    return "DONE: sliver satisfied."


# ------------------------------------------------------------------ the plane tap
def test_the_plane_meter_becomes_a_flight_recorder(monkeypatch):
    """0043 §4, rule 5: every governed thought already passes the gateway, so the
    meter extends into the recorder — latency joins tokens and dollars, and the
    projection sorts every number into its tier."""
    _fake_litellm(monkeypatch)
    gw = LiveGateway()
    r = gw.call(_surface(), "low", [{"role": "user", "content": "ping"}])
    assert r["tokens"] == 12 and "ms" in r and r["ms"] >= 0
    assert gw.call_log[-1]["ms"] == r["ms"]
    rs = observatory.plane_readings(gw)
    by_metric = {x["metric"]: x for x in rs}
    assert by_metric["plane.tokens"]["value"] == 12
    assert by_metric["plane.tokens"]["tier"] == "log-truth"
    assert by_metric["plane.usd"]["tier"] == "log-truth"
    assert by_metric["plane.thought_ms"]["tier"] == "instrument"
    assert by_metric["plane.thoughts"]["labels"]["model"].startswith("anthropic/")


def test_refusal_wears_one_face_outside_and_a_taxonomy_inside(monkeypatch):
    """Rule 4 kept, honestly: the exceptions that ride out are unchanged — the
    prober still learns nothing — while the gateway's own book names each
    refusal's kind, and the recorder reads it as an instrument, never testimony."""
    _fake_litellm(monkeypatch)
    gw = LiveGateway()
    with pytest.raises(BudgetExceeded):
        gw.call(_surface(budget=10), "low",
                [{"role": "user", "content": "x"}], pinned=True)
    with pytest.raises(BudgetExceeded):
        gw.call(_surface(budget=10), "low", [{"role": "user", "content": "x"}])
    gw_cls = LiveGateway(allowed_classes=["low"])
    with pytest.raises(BudgetExceeded):
        gw_cls.call(_surface(), "high", [{"role": "user", "content": "x"}])
    gw_sun = LiveGateway(registry={"low": [{"model": "m", "state": "sunset"}]},
                         allowed_classes=["low"])
    with pytest.raises(ModelSunset):
        gw_sun.call(_surface(), "low", [{"role": "user", "content": "x"}])

    def taxa(g):
        rs = [r for r in observatory.plane_readings(g)
              if r["metric"] == "plane.refusals"]
        assert {r["tier"] for r in rs} == {"instrument"}
        return {r["labels"]["taxon"] for r in rs}

    assert taxa(gw) == {"pinned-unaffordable", "budget-exhausted"}
    assert taxa(gw_cls) == {"class-outside-floors"}
    assert taxa(gw_sun) == {"model-sunset"}


# ------------------------------------------------------------------ the farm tap
def test_the_farm_meters_errors_per_worldline():
    """0043 §4: volume, latency, and now the OUTCOME per service worldline —
    error rate joins the lifecycle events the keeper already signs, and
    rug-pull correlation falls out for free (same service label)."""
    f = _farm()
    f.meter("search", "did:key:zCaller", ms=40)
    f.meter("search", "did:key:zCaller", ms=55)
    f.meter("search", "did:key:zCaller", ms=900, ok=False)
    rs = observatory.farm_readings(f)
    calls = [r for r in rs if r["metric"] == "farm.calls"]
    errors = [r for r in rs if r["metric"] == "farm.errors"]
    lat = [r for r in rs if r["metric"] == "farm.call_ms"]
    assert len(calls) == 3 and len(errors) == 1
    assert errors[0]["labels"] == {"service": "search"}
    assert errors[0]["tier"] == "log-truth"          # the keeper's book, on the record
    assert {r["tier"] for r in lat} == {"instrument"}
    assert any(r["metric"] == "farm.transitions"
               and r["labels"]["event"] == "serving" for r in rs)


# ------------------------------------------------------------------ the fingertip tap
def test_the_fingertip_wears_spans_and_the_choreography_carries_them(world):
    """0043 §4: span timing rides the choreography records that already exist —
    the branch gains started/ended/ms/status, the glass's record carries it,
    and the tap sorts outcome (log-truth) from stopwatch (instrument)."""
    spec = fingertip.workflow_template(
        "u:demo", name="span-proof",
        intentions=[{"id": "probe", "intent": "measure the thing",
                     "seat": "u:demo/e:cloud/f:prod"}])
    orch = fingertip.Orchestration(world.universe, world.becky, spec,
                                   "prove the span", budget_tokens=1200)
    seats = {n.scope: n for n in (world.field_prod, world.eco_cloud)}
    out = orch.run(seats, world.beckys, _tidy_think, plan_approved=True)
    assert out["verification"] == "complete"
    span = orch.branches["probe"]["span"]
    assert span["status"] == "done" and span["ms"] >= 0
    assert span["started"] <= span["ended"]
    choreo = fingertip.choreography(orch.plan(), list(orch.branches.values()))
    finger = next(n for n in choreo["nodes"] if n.get("role") == "fingertip")
    assert finger["span"] == span                     # the record carries the watch
    rs = observatory.span_readings(orch.branches.values())
    by_metric = {r["metric"]: r for r in rs}
    assert by_metric["flow.branches"]["tier"] == "log-truth"
    assert by_metric["flow.span_ms"]["tier"] == "instrument"
    assert by_metric["flow.span_ms"]["labels"]["status"] == "done"


# ------------------------------------------------------------------ the gate tap
GATES = {"suspend-universe": {"co_signs": 2, "ttl": "P7D"}}


def _humans(world, n):
    out = []
    for _ in range(n):
        ident, kp = world.becky.issue_identity("instance", "u:demo")
        out.append((ident["did"], kp))
    return out


def test_gate_wait_is_a_first_class_metric(world):
    """0043 §4: how long consequence waited for a human — pending age is a gauge,
    an approval's wait and an expiry's full TTL come from stamps the signed
    record already carries (log-truth), and a rejection's clock lives only in
    the queue's own book, so it rides as an instrument — the two-tier law,
    applied to the first metric it met."""
    humans = _humans(world, 2)
    q = hitl.EscalationQueue(GATES, {d for d, _ in humans}, world.nanda)
    approved = q.stage("suspend-universe", {"target": "a"}, scope="u:demo",
                       staged_by=humans[0][0], staged_by_kp=humans[0][1], now=iso(2))
    for did, kp in humans:
        q.approve(approved["id"], did, kp, now=iso(1))
    rejected = q.stage("suspend-universe", {"target": "b"}, scope="u:demo",
                       staged_by=humans[0][0], staged_by_kp=humans[0][1], now=iso(2))
    q.reject(rejected["id"], humans[0][0], now=iso(1))
    expired = q.stage("suspend-universe", {"target": "c"}, scope="u:demo",
                      staged_by=humans[0][0], staged_by_kp=humans[0][1], now=iso(10))
    with pytest.raises(AuthzError):
        q.approve(expired["id"], humans[0][0], humans[0][1], now=iso(0))
    pending = q.stage("suspend-universe", {"target": "d"}, scope="u:demo",
                      staged_by=humans[0][0], staged_by_kp=humans[0][1], now=iso(1))
    rs = {(r["labels"].get("outcome") or r["labels"].get("state")): r
          for r in observatory.gate_readings(q, now=iso(0))}
    day = 86400.0
    assert rs["approved"]["value"] == day and rs["approved"]["tier"] == "log-truth"
    assert rs["expired"]["value"] == 7 * day and rs["expired"]["tier"] == "log-truth"
    assert rs["rejected"]["value"] == day and rs["rejected"]["tier"] == "instrument"
    assert rs["pending"]["value"] == day and rs["pending"]["metric"] == "gate.wait_age_s"
    assert pending["state"] == "pending"              # the gauge accused no one


# ------------------------------------------------------------------ the series law
def test_a_metric_wears_one_tier_for_life():
    s = observatory.Series()
    s.ingest([observatory.reading(iso(0), "plane.tokens", 10, tier="log-truth")])
    with pytest.raises(observatory.TierConflict):
        s.ingest([observatory.reading(iso(0), "plane.tokens", 10, tier="instrument")])


def test_the_series_distills_with_measured_loss():
    """0043 §3 LOCKED: raw climbs to hourly with the loss MEASURED, like every
    other memory (0033) — constant readings distill losslessly and say so;
    spread costs, visibly."""
    s = observatory.Series()
    flat = [observatory.reading(f"2026-07-30T10:{m:02d}:00Z", "farm.calls", 1,
                                tier="log-truth") for m in (5, 20, 40)]
    spread = [observatory.reading(f"2026-07-30T11:{m:02d}:00Z", "plane.thought_ms", v,
                                  tier="instrument") for m, v in ((5, 0), (40, 10))]
    s.ingest(flat + spread)
    cut = s.distill(now="2026-07-30T12:00:00Z")
    assert cut == {"hourly": 2, "daily": 0}
    flat_h = s.read("farm.calls", resolution="hourly")["points"][0]
    assert flat_h["count"] == 3 and flat_h["sum"] == 3 and flat_h["loss"] == 0.0
    spread_h = s.read("plane.thought_ms", resolution="hourly")["points"][0]
    assert spread_h["mean"] == 5.0 and spread_h["loss"] == 0.5   # MAE 5 over range 10
    assert s.distill(now="2026-07-30T12:00:00Z") == {"hourly": 0, "daily": 0}


def test_retention_is_declared_and_sweep_never_eats_undistilled():
    """0043 §3: retention is DECLARED at construction and visible forever; the
    sweep distills FIRST and drops only what has both climbed and aged — a raw
    point in an unsealed hour survives any horizon."""
    s = observatory.Series(retention={"raw": 60})
    assert s.retention["raw"] == 60 and s.retention["daily"] == 90 * observatory.DAY
    s.ingest([observatory.reading("2026-07-30T10:30:00Z", "farm.calls", 1,
                                  tier="log-truth"),
              observatory.reading("2026-07-30T11:30:00Z", "farm.calls", 1,
                                  tier="log-truth")])
    dropped = s.sweep(now="2026-07-30T11:59:00Z")
    # the 10:30 point is aged AND its hour sealed → gone; 11:30 sits in the
    # OPEN hour — aged far past 60s, still untouchable
    assert dropped["raw"] == 1
    assert s.read("farm.calls")["points"][0]["at"] == "2026-07-30T11:30:00Z"
    assert s.read("farm.calls", resolution="hourly")["points"][0]["count"] == 1


def test_hourly_climbs_to_daily_and_lived_time_stays_monotone():
    """The pyramid's second climb: count/sum/min/max merge exactly, the
    hour-to-hour shape is priced as the day's loss — and a reading backdated
    into a sealed bucket is refused (rule 8 reaches the instruments)."""
    s = observatory.Series()
    s.ingest([observatory.reading(f"2026-07-30T{h:02d}:10:00Z", "plane.tokens", v,
                                  tier="log-truth") for h, v in ((9, 100), (10, 300))])
    cut = s.distill(now="2026-07-31T00:00:00Z")
    assert cut == {"hourly": 2, "daily": 1}
    day = s.read("plane.tokens", resolution="daily")["points"][0]
    assert day["count"] == 2 and day["sum"] == 400
    assert day["min"] == 100 and day["max"] == 300 and day["loss"] == 0.5
    with pytest.raises(observatory.BackdatedReading):
        s.ingest([observatory.reading("2026-07-30T09:59:00Z", "plane.tokens", 1,
                                      tier="log-truth")])


def test_log_truth_rebuilds_from_the_log_and_instruments_wear_their_label():
    """0043 §3 LOCKED, both halves: a log-truth series rebuilt from the same log
    is the same series — the projection is never a second truth (rule 7) — and
    an instrument metric's every answer carries its label in the payload."""
    rows = [observatory.reading(f"2026-07-30T10:{m:02d}:00Z", "plane.tokens", v,
                                tier="log-truth", labels={"class": "low"})
            for m, v in ((1, 50), (2, 70), (3, 90))]
    a, b = observatory.Series(), observatory.Series()
    a.ingest(rows)
    a.distill(now="2026-07-30T12:00:00Z")
    b.ingest(rows)                                     # the rebuild, from the log
    b.distill(now="2026-07-30T12:00:00Z")
    assert a.hourly == b.hourly and a.read("plane.tokens") == b.read("plane.tokens")
    assert "label" not in a.read("plane.tokens")       # testimony needs no disclaimer
    f = _farm()
    f.meter("search", "did:key:zCaller", ms=40)
    s = observatory.Series()
    s.ingest(observatory.farm_readings(f))
    assert s.read("farm.call_ms")["label"] == observatory.INSTRUMENT_LABEL


def test_watch_reads_deeper_from_the_same_shelf():
    """0043 §5: the watch depth is a deeper READ, never a new collection —
    percentiles over the raw points the glance already keeps, the tier and
    its label riding the answer like every other read."""
    s = observatory.Series()
    s.ingest([observatory.reading(f"2026-07-30T10:{m:02d}:00Z",
                                  "plane.thought_ms", v, tier="instrument")
              for m, v in ((1, 100), (2, 200), (3, 300), (4, 400))])
    d = observatory.percentiles(s, "plane.thought_ms")
    assert d["n"] == 4 and d["min"] == 100 and d["max"] == 400
    assert d["quantiles"] == {"p50": 250.0, "p95": 385.0}
    assert d["label"] == observatory.INSTRUMENT_LABEL


# ------------------------------------------------------------------ the recorder
def test_the_flight_recorder_sweeps_without_double_counting(world):
    """sp1 assembled: the four taps into one Series on the beat — a call metered
    once is counted once, a decided gate records once, a span records once, and
    only the pending gauge samples fresh every sweep."""
    gw = world.universe.model_gateway
    agent = join_workforce(world.field_prod, world.beckys["u:demo/e:cloud/f:prod"])
    world.field_prod.model_gateway.call(agent, "standard", 100)
    f = _farm()
    f.meter("search", "did:key:zCaller", ms=40)
    humans = _humans(world, 2)
    q = hitl.EscalationQueue(GATES, {d for d, _ in humans}, world.nanda)
    decided = q.stage("suspend-universe", {"target": "a"}, scope="u:demo",
                      staged_by=humans[0][0], staged_by_kp=humans[0][1], now=iso(2))
    for did, kp in humans:
        q.approve(decided["id"], did, kp, now=iso(1))
    q.stage("suspend-universe", {"target": "b"}, scope="u:demo",
            staged_by=humans[0][0], staged_by_kp=humans[0][1], now=iso(1))
    spec = fingertip.workflow_template(
        "u:demo", name="rec-proof",
        intentions=[{"id": "probe", "intent": "measure",
                     "seat": "u:demo/e:cloud/f:prod"}])
    orch = fingertip.Orchestration(world.universe, world.becky, spec,
                                   "prove the recorder", budget_tokens=1200)
    seats = {n.scope: n for n in (world.field_prod, world.eco_cloud)}
    orch.run(seats, world.beckys, _tidy_think, plan_approved=True)

    rec = observatory.FlightRecorder()
    taps = dict(gateways=[gw, world.field_prod.model_gateway], farms=[f],
                queues=[q], flights=[orch])
    rec.sweep(now=iso(0), **taps)
    rec.sweep(now=iso(0), **taps)                      # the second beat
    s = rec.series
    assert len(s.read("plane.thoughts")["points"]) == 1
    assert len(s.read("farm.calls")["points"]) == 1
    assert len(s.read("flow.span_ms")["points"]) == 1
    assert len(s.read("gate.wait_s")["points"]) == 1   # decided: once, ever
    assert len(s.read("gate.wait_age_s")["points"]) == 2   # the gauge breathes


def test_the_pyramid_survives_the_process():
    """G2 (0043 sp5): dump → load carries the distilled tiers whole — reads
    equal, tiers kept, and the monotone law survives the reload: a reloaded
    seal refuses a backdated reading exactly like a lived one, while the
    unsealed present ingests freely."""
    a = observatory.Series()
    a.ingest([observatory.reading(f"2026-07-30T{h:02d}:10:00Z", "plane.tokens",
                                  v, tier="log-truth")
              for h, v in ((9, 100), (10, 300))])
    a.distill(now="2026-07-31T00:00:00Z")
    b = observatory.Series.load(a.dump())
    assert b.read("plane.tokens", resolution="hourly") == \
        a.read("plane.tokens", resolution="hourly")
    assert b.read("plane.tokens", resolution="daily") == \
        a.read("plane.tokens", resolution="daily")
    assert b.tiers == a.tiers
    assert a.dump()["sealed_until"] == "2026-07-30T11:00:00Z"
    with pytest.raises(observatory.BackdatedReading):
        b.ingest([observatory.reading("2026-07-30T09:59:00Z", "plane.tokens",
                                      1, tier="log-truth")])
    b.ingest([observatory.reading("2026-07-31T00:05:00Z", "plane.tokens", 50,
                                  tier="log-truth")])       # the present flows on
    assert b.read("plane.tokens")["points"][0]["value"] == 50
