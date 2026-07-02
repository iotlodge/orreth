"""The three flows, end to end — plus isolation, tombstones, and the kill-switch.

Every wire object here validates against contracts/v0. This suite is the seed of the
conformance fixtures the Rust plane must eventually pass (same fixtures, two
implementations, one truth).
"""
from datetime import datetime, timedelta, timezone

import pytest

from orreth_sim import crypto, factory, rollup
from orreth_sim.agent_surface import BudgetExceeded, join_workforce
from orreth_sim.identity import AuthzError, tenant_of
from orreth_sim.node import ClockViolation, FloorViolation, Refusal, make_memory
from orreth_sim.world import build


def iso(days_ago: float = 0) -> str:
    return (datetime.now(timezone.utc) - timedelta(days=days_ago)).strftime("%Y-%m-%dT%H:%M:%SZ")


@pytest.fixture()
def world():
    return build()


# ---------------------------------------------------------------- identity & trust
def test_identity_chain_and_lineage(world):
    ident, _ = world.agents["prod-1"]
    arch, _ = world.agents["architect-archetype"]
    assert ident["lineage"] == arch["did"]          # archetype -> incarnation
    assert ident["role"] == "instance" and arch["role"] == "archetype"
    assert ident["did"].startswith("did:key:")      # cheap leaves
    assert world.becky.did.startswith("did:web:orreth.ai:u:")  # anchored root


def test_no_amplification_and_ancestor_killswitch(world):
    b_prod = world.beckys["u:demo/e:cloud/f:prod"]
    ident, _ = world.agents["prod-1"]
    # a field becky cannot mint authority over the universe — no amplification exists
    with pytest.raises(AuthzError):
        b_prod.issue_token(ident["did"], "u:demo",
                           [{"action": "retrieve", "space": "apex"}])
    # revoke the ecosystem delegate -> everything beneath it dies
    tok = b_prod.issue_token(ident["did"], "u:demo/e:cloud/f:prod",
                             [{"action": "retrieve", "space": "self"}])
    world.becky.verify_token(tok)                    # valid before
    world.nanda.revoke(world.beckys["u:demo/e:cloud"].did)
    with pytest.raises(AuthzError):
        world.becky.verify_token(tok)                # ancestor revocation kills the subtree


# ---------------------------------------------------------------- flow 1: policy DOWN
def test_floors_cascade_and_never_loosen(world):
    rule = {"match": {"outcome": "failure"}, "action": "keep-raw",
            "keep_for": "P90D", "reason": "failures always survive"}
    world.universe.publish_floors([rule])
    world.eco_cloud.pull_standards()
    world.field_prod.pull_standards()  # grandparent floors cascade through
    assert len(world.eco_cloud.inherited_floors) == 1
    # loosen -> rejected; tighten -> accepted
    with pytest.raises(FloorViolation):
        world.eco_cloud.add_local_floor({"match": {"outcome": "failure"},
                                         "action": "drop-after-distill",
                                         "keep_for": "P7D", "reason": "loosen attempt"})
    world.eco_cloud.add_local_floor({"match": {"outcome": "failure"}, "action": "keep-raw",
                                     "keep_for": "P365D", "reason": "tighten is fine"})


# ---------------------------------------------------------------- flow 2: memory UP
def test_memory_rises_pruned_with_provenance(world):
    ident, kp = world.agents["prod-1"]
    ids = [world.field_prod.write(make_memory(ident, kp, ident["scope"],
                                              {"event": f"run-{i}"},
                                              tags=["failure"] if i == 0 else []))
           for i in range(5)]
    dist = world.field_prod.run_distillation()
    assert set(dist["derived_from"]) == set(ids)               # signed chain to every input
    assert dist["id"] in world.eco_cloud.records               # pushed UP, verified by parent
    eco_dist = world.eco_cloud.run_distillation()              # eco distills further
    assert eco_dist["id"] in world.universe.records            # the apex holds the distilled
    assert ids[0] not in world.universe.records                # raw never reached the apex
    # floors classified the failure as keep-raw (0003 §1)
    world.universe.publish_floors([{"match": {"outcome": "failure"}, "action": "keep-raw",
                                    "keep_for": "P90D", "reason": "failures survive"}])
    world.field_prod.pull_standards()
    fid = world.field_prod.write(make_memory(ident, kp, ident["scope"],
                                             {"event": "boom"}, tags=["failure"]))
    assert world.field_prod.records[fid]["keep_class"] == "keep-raw"


# ---------------------------------------------------------------- flow 3: retrieval UP
def _token(world, agent="prod-1", audience="u:demo", grants=None, **kw):
    ident, _ = world.agents[agent]
    issuer = world.becky if audience == "u:demo" else world.beckys[audience]
    return issuer.issue_token(ident["did"], audience,
                              grants or [{"action": "retrieve", "space": "self"}], **kw)


def _query(world, agent="prod-1", days=7, cost=3, intent="recall", subject="self"):
    ident, _ = world.agents[agent]
    return {"requester": ident["did"], "subject": subject, "space": "self",
            "time": {"from": iso(days)}, "intent": intent,
            "budget": {"cost": cost}, "auth": "biscuit-sim"}


def test_retrieval_escalates_and_merges(world):
    ident, kp = world.agents["prod-1"]
    world.field_prod.write(make_memory(ident, kp, ident["scope"], {"n": 1}))
    world.field_prod.run_distillation()
    tok = _token(world)
    res = world.field_prod.retrieve(_query(world, days=400), tok, ident["scope"])
    # deep window escalated past the field's P90D horizon: field AND eco served
    assert "u:demo/e:cloud/f:prod" in res["provenance"]["served_by"]
    assert "u:demo/e:cloud" in res["provenance"]["served_by"]
    assert all(h["source"] == ident["did"] for h in res["hits"])   # Sourced
    assert res["verification"] in ("verified", "partial")


def test_budget_miss_equals_authz_miss(world):
    ident, kp = world.agents["prod-1"]
    world.field_prod.write(make_memory(ident, kp, ident["scope"], {"n": 1}))
    # budget exhausted after one tier vs token that doesn't reach past the field:
    tok_wide = _token(world)
    r_budget = world.field_prod.retrieve(_query(world, days=400, cost=1), tok_wide, ident["scope"])
    tok_narrow = _token(world, audience="u:demo/e:cloud/f:prod")
    r_authz = world.field_prod.retrieve(_query(world, days=400, cost=99), tok_narrow, ident["scope"])
    # identical caller-visible shape: partial + remainder — the refusal leaks nothing
    for r in (r_budget, r_authz):
        assert r["verification"] == "partial" and "remainder" in r
    assert r_budget["remainder"].keys() == r_authz["remainder"].keys()
    # only the privileged access log knows there was a difference
    assert len(world.field_prod.access_log) >= 2


def test_refusal_shape_is_uniform(world):
    ident, _ = world.agents["prod-1"]
    bad_tok = _token(world, grants=[{"action": "write", "space": "self"}])  # no retrieve grant
    with pytest.raises(Refusal) as e:
        world.field_prod.retrieve(_query(world), bad_tok, ident["scope"])
    assert str(e.value) == Refusal.PUBLIC                       # no reason leaks to the caller


# ---------------------------------------------------------------- isolation & interview
def test_sibling_tenant_isolation(world):
    prod, pkp = world.agents["prod-1"]
    lab, lkp = world.agents["lab-1"]
    world.field_lab.write(make_memory(lab, lkp, lab["scope"], {"secret": "dev-playbook"}))
    world.field_lab.run_distillation()
    world.eco_dev.run_distillation()   # dev's distillation reaches the apex
    assert tenant_of(prod["scope"]) != tenant_of(lab["scope"])
    tok = _token(world)  # audience u:demo, but NO apex grant
    q = _query(world, days=400, subject={"identity": lab["did"]})
    res = world.universe.retrieve(q, tok, prod["scope"])
    assert res["hits"] == []                                    # sibling raw: never
    # the only cross-sibling window: anonymized aggregates at the common parent
    bench = world.universe.benchmark()
    assert set(bench) == {"cohort_size", "median_record_count"}  # no refs, no DIDs, no scopes


def test_interview_reads_portfolio_only(world):
    cand, ckp = world.agents["lab-1"]
    world.field_lab.write(make_memory(cand, ckp, cand["scope"], {"private": "client work"}))
    world.field_lab.write(make_memory(cand, ckp, cand["scope"],
                                      {"portfolio": "closed 400 tickets, 0.94 mean"},
                                      tenancy="portfolio"))
    buyer, _ = world.agents["prod-1"]
    b_lab = world.beckys["u:demo/e:dev/f:lab"]
    tok = b_lab.issue_token(buyer["did"], "u:demo/e:dev/f:lab",
                            [{"action": "retrieve", "space": {"scope": "u:demo/e:dev/f:lab"},
                              "visibility": ["portfolio"]},
                             {"action": "interview", "space": {"scope": "u:demo/e:dev/f:lab"}}])
    q = {"requester": buyer["did"], "subject": {"identity": cand["did"]}, "space": "self",
         "time": {"from": iso(7)}, "intent": "interview",
         "budget": {"cost": 2}, "auth": "biscuit-sim"}
    res = world.field_lab.retrieve(q, tok, buyer["scope"])
    assert len(res["hits"]) == 1                                # tenant-private is walled
    # the trace is owner-visible (access log), invisible to future buyers (not in results)
    assert any(e["intent"] == "interview" for e in world.field_lab.access_log)


# ---------------------------------------------------------------- the two clocks (0004 §1)
def test_lived_memory_cannot_be_backdated(world):
    ident, kp = world.agents["prod-1"]
    world.field_prod.write(make_memory(ident, kp, ident["scope"], {"event": "now"}))
    # a 'lived' record below the scope's high-water mark is rejected — no quietly written pasts
    with pytest.raises(ClockViolation):
        world.field_prod.write(make_memory(ident, kp, ident["scope"],
                                           {"event": "forged past"}, occurred_at=iso(30)))
    # and the record carries both clocks: the author's signed claim + the gateway's stamp
    rec = next(iter(world.field_prod.records.values()))
    assert "occurred_at" in rec and "received_at" in rec


def test_ingested_archive_carries_history_honestly(world):
    ident, kp = world.agents["prod-1"]
    world.field_prod.write(make_memory(ident, kp, ident["scope"], {"event": "now"}))
    # backfill below the high-water mark is legal ONLY as labeled archive (lived vs ingested)
    rid = world.field_prod.write(make_memory(ident, kp, ident["scope"],
                                             {"hurricane": "1850"}, occurred_at=iso(30),
                                             provenance_class="ingested-archive"))
    assert world.field_prod.records[rid]["provenance_class"] == "ingested-archive"
    # the archive did not move the frontier: lived writes at the present still land
    world.field_prod.write(make_memory(ident, kp, ident["scope"], {"event": "still now"}))
    # provenance_class is SIGNED — flipping lived→archive to smuggle a backdate breaks the signature
    forged = make_memory(ident, kp, ident["scope"], {"event": "flip"}, occurred_at=iso(30))
    forged["provenance_class"] = "ingested-archive"
    with pytest.raises(AuthzError):
        world.field_prod.write(forged)


# ---------------------------------------------------------------- 0005: the roll-up
def _run(node, world, agent_name, goal, score, *, outcome="success", breach=False,
         occurred_at=None, objective="reliability"):
    ident, _ = world.agents[agent_name]
    r = {
        "id": crypto.content_hash({"g": goal, "a": ident["did"], "s": score, "t": occurred_at or iso()}),
        "agent": ident["did"], "scope": ident["scope"], "goal_hash": goal,
        "occurred_at": occurred_at or iso(), "outcome": outcome,
        "scores": [{"objective": objective, "score": score,
                    **({"floor_breached": True} if breach else {})}],
        "cost": {"tokens": 100},
        "author": node.steward["did"],
    }
    r["sig"] = node.steward_kp.sign(node.steward["did"], {k: r[k] for k in
                                    ("id", "agent", "scope", "goal_hash", "occurred_at")})
    return r


def test_rollup_monoid_one_truth(world):
    """The monoid law: chunked merges == one shot — standings compose from any split.
    (Float sums compare via report, tolerance-free integers exactly; the Rust plane
    will use fixed-point so the bundle itself is bit-identical.)"""
    runs = [rollup.bundle_of(_run(world.field_prod, world, "prod-1", "g", s))
            for s in (0.9, 0.8, 0.7, 0.95, 0.6)]
    left = rollup.merge(rollup.merge(runs[0], runs[1]), rollup.merge(runs[2], rollup.merge(runs[3], runs[4])))
    right = rollup.merge(rollup.merge(rollup.merge(rollup.merge(runs[0], runs[1]), runs[2]), runs[3]), runs[4])
    assert left["n"] == right["n"] == 5
    assert left["outcomes"] == right["outcomes"] and left["cost"] == right["cost"]
    rl, rr = rollup.report(left, "reliability"), rollup.report(right, "reliability")
    assert rl["mean"] == pytest.approx(rr["mean"]) and rl["n"] == rr["n"]
    ident = rollup.merge(rollup.empty_bundle(), left)           # identity element
    assert ident["n"] == left["n"] and ident["outcomes"] == left["outcomes"]


def test_confidence_is_count_weighted(world):
    """Locked 2026-07-02: Bayesian posterior — a lucky n=2 is honestly wider than a proven n=50."""
    small = rollup.empty_bundle()
    for s in (0.94, 0.94):
        small = rollup.merge(small, rollup.bundle_of(_run(world.field_prod, world, "prod-1", "g", s)))
    big = rollup.empty_bundle()
    for _ in range(25):
        for s in (0.94, 0.94):
            big = rollup.merge(big, rollup.bundle_of(_run(world.field_prod, world, "prod-1", "g", s)))
    r_small, r_big = (rollup.report(b, "reliability") for b in (small, big))
    width = lambda r: r["ci95"][1] - r["ci95"][0]
    assert width(r_small) > width(r_big)          # same mean, honest uncertainty
    assert r_small["n"] == 2 and r_big["n"] == 50


def test_floor_breach_flags_never_averages(world):
    """Locked 2026-07-02: a 0.98 agent with one breach shows BOTH truths —
    the breach flips compliance, and the performance mean is untouched by it."""
    clean = rollup.empty_bundle()
    for _ in range(9):
        clean = rollup.merge(clean, rollup.bundle_of(_run(world.field_prod, world, "prod-1", "g", 0.98)))
    before = rollup.report(clean, "reliability")
    b = rollup.merge(clean, rollup.bundle_of(
        _run(world.field_prod, world, "prod-1", "g", 0.98, breach=True, objective="compliance")))
    rep = rollup.report(b, "reliability")
    assert rep["compliance"] == "breached"                        # the breach is unmissable
    assert rep["mean"] == pytest.approx(before["mean"])           # and it never averages away the score
    vec = [{"objective": "reliability", "weight": 1.0},
           {"objective": "compliance", "weight": 1.0, "floor": True}]
    ts = rollup.tier_score(b, vec)
    assert ts["compliance"] == "breached"                         # floors gate...
    assert ts["score"] == pytest.approx(before["mean"])           # ...they never dilute


def test_league_standings_roll_up_the_tree(world):
    """PG-1 in miniature: two teams' seasons roll to the league — raw runs never travel."""
    season = {"from": iso(30), "to": iso(0)}
    for s in (0.9, 0.8, 0.85):                                   # team prod: strong season
        world.field_prod.record_run(_run(world.field_prod, world, "prod-1", "season-1", s,
                                         occurred_at=iso(15)))
    for s in (0.5, 0.6):                                         # team lab: rebuilding year
        world.field_lab.record_run(_run(world.field_lab, world, "lab-1", "season-1", s,
                                        occurred_at=iso(15)))
    ru_prod = world.field_prod.roll_up(season, goal_hash="season-1")
    ru_lab = world.field_lab.roll_up(season, goal_hash="season-1")
    ru_cloud = world.eco_cloud.roll_up(season, goal_hash="season-1")   # conference: from child bundle
    ru_dev = world.eco_dev.roll_up(season, goal_hash="season-1")
    league = world.universe.roll_up(season, goal_hash="season-1")      # the league table
    assert league["stats"]["n"] == 5                              # every game counted once
    assert ru_cloud["stats"] == ru_prod["stats"]                  # composed, not recomputed
    # standings: the same bundles, read per team — count-weighted, honestly uncertain
    standing_prod = rollup.report(ru_prod["stats"], "reliability")
    standing_lab = rollup.report(ru_lab["stats"], "reliability")
    assert standing_prod["mean"] > standing_lab["mean"]
    # no raw run ever left its field — only signed pointers traveled
    assert all(rid in world.field_prod.runs for rid in ru_prod["contributors"])
    assert league["contributors"] and all(
        cid not in world.universe.runs for cid in league["contributors"])


def test_self_asserted_evaluation_rejected(world):
    """0001's rule, enforced: no agent grades its own yardstick."""
    ident, kp = world.agents["prod-1"]
    r = _run(world.field_prod, world, "prod-1", "g", 1.0)
    r["author"] = ident["did"]                                   # the agent grading itself
    r["sig"] = kp.sign(ident["did"], {k: r[k] for k in
                       ("id", "agent", "scope", "goal_hash", "occurred_at")})
    with pytest.raises(AuthzError):
        world.field_prod.record_run(r)


# ---------------------------------------------------------------- 0010: the gateway & the surface
def test_workforce_joins_and_holds_only_the_surface(world):
    """Any-SDK agent presents at the Gateway → leased identity + budgeted token + the surface."""
    b_prod = world.beckys["u:demo/e:cloud/f:prod"]
    surf = join_workforce(world.field_prod, b_prod, budget_tokens=5000)
    rid = surf.write({"observation": "joined and working"})
    assert rid in world.field_prod.records                     # the write landed, governed
    q = {"requester": surf.identity["did"], "subject": "self", "space": "self",
         "time": {"from": iso(1)}, "intent": "recall", "budget": {"cost": 2}, "auth": "biscuit-sim"}
    res = surf.retrieve(q)
    assert any(h["ref"] == rid for h in res["hits"])           # and reads back under the lease


def test_model_calls_degrade_where_pins_allow(world):
    """Locked 2026-07-02: budget dips degrade WITH a flag; a pinned tier fails honestly."""
    b_prod = world.beckys["u:demo/e:cloud/f:prod"]
    rich = join_workforce(world.field_prod, b_prod, budget_tokens=10_000)
    assert rich.call_model("premium", 100)["degraded"] is False
    poor = join_workforce(world.field_prod, b_prod, budget_tokens=500)
    r = poor.call_model("premium", 100)                        # premium costs 2000 — unaffordable
    assert r["served_tier"] == "standard" and r["degraded"] is True   # honest downgrade
    r2 = poor.call_model("standard", 100)                      # 400 > 100 left — degrades again
    assert r2["served_tier"] == "nano" and r2["degraded"] is True
    with pytest.raises(BudgetExceeded):
        poor.call_model("nano", 10, pinned=True)               # a pin is a floor: never silently dumber
    # every call — served or refused — is on the gateway log: vigil's tap, content-blind
    gw = world.field_prod.model_gateway
    assert len(gw.call_log) == 4 and all("caller" in e for e in gw.call_log)


def test_signals_are_transport_unless_state_changing(world):
    """Locked 2026-07-02: 'if it's not memory, it didn't happen' — the dial's default."""
    b_prod = world.beckys["u:demo/e:cloud/f:prod"]
    a, b = (join_workforce(world.field_prod, b_prod) for _ in range(2))
    before = len(world.field_prod.records)
    assert a.signal(b, {"chat": "how's the weather in season 3?"}) is None
    assert b.inbox and len(world.field_prod.records) == before          # delivered, not remembered
    rid = a.signal(b, {"handoff": "ticket-42 is yours"}, state_changing=True)
    assert rid in world.field_prod.records                              # a state-change HAPPENED
    assert world.field_prod.signal_count == 2                           # vigil saw both shapes
    world.field_prod.profile["signal_capture"] = "full"                 # the REAL/regulated dial
    assert a.signal(b, {"chat": "recorded now"}) is not None            # full capture keeps chatter too


# ---------------------------------------------------------------- 0011: the factory
def test_draft_class_stamps_through_the_gateway(world):
    """One archetype, a draft class of rookies — each leased, budgeted, certified; quota is a wall."""
    world.field_prod.profile["stamp_quota"] = 6
    arch, _ = world.agents["architect-archetype"]
    b_prod = world.beckys["u:demo/e:cloud/f:prod"]
    rookies = factory.stamp(world.field_prod, b_prod, arch, 5, generation="draft-s3")
    assert all(r.identity["lineage"] == arch["did"] for r in rookies)   # one template, five lives
    certs = [r for r in world.field_prod.records.values() if "draft-s3" in r.get("tags", [])]
    assert len(certs) == 5                                              # births are on the record
    rid = rookies[0].write({"first": "day at practice"})
    assert rid in world.field_prod.records                              # the surface works
    with pytest.raises(factory.QuotaExceeded):
        factory.stamp(world.field_prod, b_prod, arch, 2, generation="draft-s3b")   # 5+2 > 6
    factory.retire(world.field_prod, rookies[0].identity)               # a slot frees on retirement
    factory.stamp(world.field_prod, b_prod, arch, 2, generation="draft-s3b")


def test_upgrade_in_place_restamp_is_a_new_life(world):
    """Locked 2026-07-02: memory survives upgrades; a re-stamp is a sibling, never a silent successor."""
    arch, _ = world.agents["architect-archetype"]
    b_prod = world.beckys["u:demo/e:cloud/f:prod"]
    (veteran,) = factory.stamp(world.field_prod, b_prod, arch, 1, generation="gen-1")
    memory = veteran.write({"season": "hard-won experience"})
    # the archetype 'upgrades' — skills arrive via the Standards cascade; identity and memory persist
    (fresh,) = factory.stamp(world.field_prod, b_prod, arch, 1, generation="gen-2")
    assert fresh.identity["did"] != veteran.identity["did"]             # a new life...
    assert fresh.identity["lineage"] == veteran.identity["lineage"]     # ...same bloodline
    rec = world.field_prod.records[memory]
    assert rec["author"] == veteran.identity["did"]                     # the veteran keeps its past


def test_rookie_probation_full_grade_until_first_bundle(world):
    """Locked 2026-07-02: uncertainty pays for observation — nothing else does."""
    arch, _ = world.agents["architect-archetype"]
    b_prod = world.beckys["u:demo/e:cloud/f:prod"]
    (rookie,) = factory.stamp(world.field_prod, b_prod, arch, 1,
                              generation="gen-p", probation_runs=5)
    cert = rookie.birth_certificate                                     # provenance travels with the handle
    young = rollup.empty_bundle()
    for s in (0.9, 0.8):
        young = rollup.merge(young, rollup.bundle_of(_run(world.field_prod, world, "prod-1", "g", s)))
    assert factory.judge_rate(world.field_prod, cert, young) == 1.0     # n=2 < 5: full observation
    proven = dict(young)
    for _ in range(12):
        proven = rollup.merge(proven, rollup.bundle_of(_run(world.field_prod, world, "prod-1", "g", 0.9)))
    assert factory.judge_rate(world.field_prod, cert, proven) == \
        world.field_prod.profile["model_gateway"]["judge_sample_rate"]  # a track record earns 1-in-N


# ---------------------------------------------------------------- tombstones
def test_tombstone_annotates_never_rewrites(world):
    ident, kp = world.agents["prod-1"]
    rid = world.field_prod.write(make_memory(ident, kp, ident["scope"], {"phi": "sensitive"}))
    dist = world.field_prod.run_distillation()
    world.field_prod.tombstone(rid, by=ident["did"], reason="consent withdrawn")
    rec = world.field_prod.records[rid]
    assert "tombstoned" in rec["retention"] and "body" not in rec   # provably retired, body purged
    marked = world.field_prod.records[dist["id"]]
    assert marked["redactions"][0]["tombstone_ref"] == rid          # annotated, not rewritten
    assert rid in marked["derived_from"]                            # history didn't silently change
    # the distillation still serves — honestly labeled
    tok = _token(world)
    res = world.field_prod.retrieve(_query(world, subject={"identity": world.field_prod.steward["did"]}),
                                    tok, ident["scope"])
    fid = {h["ref"]: h["fidelity"] for h in res["hits"]}
    assert fid.get(dist["id"]) == "distilled-raw-expired"
    # and the purged raw itself is gone from results
    assert rid not in fid
