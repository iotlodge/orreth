"""The three flows, end to end — plus isolation, tombstones, and the kill-switch.

Every wire object here validates against contracts/v0. This suite is the seed of the
conformance fixtures the Rust plane must eventually pass (same fixtures, two
implementations, one truth).
"""
from datetime import datetime, timedelta, timezone

import pytest

from orreth_sim import crypto, factory, hitl, provisioner, resolver, rollup
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


def test_foreign_root_mints_nothing(world):
    """Trust-root pinning: a self-issued token — perfect signatures, wrong root — is refused.
    (This exact hole was live in orrethd v0's smoke test; closed in both languages.)"""
    import json as _json
    ident, _ = world.agents["prod-1"]
    forger = crypto.KeyPair()
    forger_did = crypto.did_key_for(forger.public)
    world.nanda.register(forger_did, forger.public)
    cert = {"issuer": forger_did, "subject": ident["did"],
            "audience": "u:demo/e:cloud/f:prod",
            "grants": [{"action": "retrieve", "space": "self"}]}
    cert["sig"] = forger.sign(forger_did, cert)
    token = {"subject": ident["did"], "audience": "u:demo/e:cloud/f:prod",
             "grants": cert["grants"],
             "constraints": {"expiry": "2027-01-01T00:00:00Z", "direction": "within"},
             "chain": [_json.dumps(cert, sort_keys=True)],
             "sig": forger.sign(forger_did, {"s": ident["did"]})}
    with pytest.raises(AuthzError, match="trust root"):
        world.becky.verify_token(token)


def test_delegation_continuity_and_attenuation_hold(world):
    """A chain with a spliced hop (issuer ≠ previous subject) is refused; legitimate
    chains — root → eco becky → field becky → token — verify to the pinned root."""
    import json as _json
    ident, _ = world.agents["prod-1"]
    b_prod = world.beckys["u:demo/e:cloud/f:prod"]
    good = b_prod.issue_token(ident["did"], "u:demo/e:cloud/f:prod",
                              [{"action": "retrieve", "space": "self"}])
    world.becky.verify_token(good)                              # full chain to the root
    # splice: replace the middle delegation cert with one from an unrelated key
    rogue = crypto.KeyPair()
    rogue_did = crypto.did_key_for(rogue.public)
    world.nanda.register(rogue_did, rogue.public)
    spliced_cert = {"issuer": rogue_did, "subject": b_prod.did,
                    "scope": "u:demo/e:cloud/f:prod", "at": "2026-07-01T00:00:00Z"}
    spliced_cert["sig"] = rogue.sign(rogue_did, spliced_cert)
    bad = dict(good)
    chain = list(good["chain"])
    chain[1] = _json.dumps(spliced_cert, sort_keys=True)
    bad["chain"] = chain
    with pytest.raises(AuthzError, match="continuity"):
        world.becky.verify_token(bad)


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


def test_exchange_hold_stays_home(world):
    """0023 §4 (Universe-Brain locks): a class dialed 'hold' on the exchange never
    rides a distillation up — it distills HOME. Residency, never reach; and the
    open classes keep rising exactly as before."""
    ident, kp = world.agents["prod-1"]
    world.field_prod.profile["exchange"] = {"diary": "hold"}
    held = world.field_prod.write(make_memory(ident, kp, ident["scope"],
                                              {"event": "a private day"}, tags=["diary"]))
    open_ = world.field_prod.write(make_memory(ident, kp, ident["scope"],
                                               {"event": "a shared lesson"},
                                               tags=["knowledge"]))
    dist = world.field_prod.run_distillation()          # returns the RISING cohort
    assert open_ in dist["derived_from"] and held not in dist["derived_from"]
    assert dist["id"] in world.eco_cloud.records        # the open cohort rose
    # the held cohort distilled home: covered locally, and NOTHING deriving from it
    # ever reached the parent
    local = [r for r in world.field_prod.records.values()
             if r.get("kind") == "distillation" and held in (r.get("derived_from") or [])]
    assert local, "the held class still gets its home distillation"
    assert all(d["id"] not in world.eco_cloud.records for d in local)


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


# ---------------------------------------------------------------- 0012: gates & queues
GATES = {"suspend-universe": {"co_signs": 2, "ttl": "P7D"},
         "destroy-universe": {"co_signs": 3, "ttl": "P7D", "cooling_off": "P2D"}}


def _humans(world, n):
    out = []
    for _ in range(n):
        ident, kp = world.becky.issue_identity("instance", "u:demo")
        out.append((ident["did"], kp))
    return out


def test_quorum_lifecycle_and_distinct_signers(world):
    """Staging is free; deciding is gated; no DID signs twice; quorum is not a formality."""
    humans = _humans(world, 2)
    q = hitl.EscalationQueue(GATES, {d for d, _ in humans}, world.nanda)
    vigil_did, vigil_kp = world.becky.issue_identity("instance", "u:demo", resident=True)
    esc = q.stage("suspend-universe", {"target": "u:demo/e:dev"}, scope="u:demo",
                  staged_by=vigil_did["did"], staged_by_kp=vigil_kp, now=iso(0))
    with pytest.raises(AuthzError):
        q.execute(esc["id"], now=iso(0))                       # zero signatures ≠ approved
    q.approve(esc["id"], humans[0][0], humans[0][1], now=iso(0))
    with pytest.raises(AuthzError):
        q.approve(esc["id"], humans[0][0], humans[0][1], now=iso(0))   # no double-sign
    with pytest.raises(AuthzError):
        q.execute(esc["id"], now=iso(0))                       # 1 of 2 is not quorum
    q.approve(esc["id"], humans[1][0], humans[1][1], now=iso(0))
    assert q.execute(esc["id"], now=iso(0))["state"] == "executed"


def test_bars_are_absolute_for_a_solo_org(world):
    """Locked 2026-07-02: 'no single employee is a god' is true from day one, not aspirational."""
    (jb,) = _humans(world, 1)
    q = hitl.EscalationQueue(GATES, {jb[0]}, world.nanda)
    with pytest.raises(hitl.QuorumUnavailable):
        q.stage("suspend-universe", {"target": "u:demo/e:dev"}, scope="u:demo",
                staged_by=jb[0], staged_by_kp=jb[1], now=iso(0))


def test_silence_never_approves(world):
    """Locked 2026-07-02: expiry = deny + signal — an unattended queue is itself a finding."""
    humans = _humans(world, 2)
    q = hitl.EscalationQueue(GATES, {d for d, _ in humans}, world.nanda)
    esc = q.stage("suspend-universe", {"target": "u:demo/e:dev"}, scope="u:demo",
                  staged_by=humans[0][0], staged_by_kp=humans[0][1], now=iso(10))
    with pytest.raises(AuthzError):
        q.approve(esc["id"], humans[0][0], humans[0][1], now=iso(0))   # 10 days later: expired
    assert q.items[esc["id"]]["state"] == "expired"
    assert q.expired_signals == 1                                       # vigil heard the silence


def test_cooling_off_holds_and_gates_tighten_only(world):
    """The abort window is the point — and co-sign bars cascade like floors."""
    humans = _humans(world, 3)
    q = hitl.EscalationQueue(GATES, {d for d, _ in humans}, world.nanda)
    esc = q.stage("destroy-universe", {"target": "u:demo/e:dev"}, scope="u:demo",
                  staged_by=humans[0][0], staged_by_kp=humans[0][1], now=iso(3))
    for did, kp in humans:
        q.approve(esc["id"], did, kp, now=iso(3))
    with pytest.raises(AuthzError):
        q.execute(esc["id"], now=iso(3))                       # quorum met — but held
    q.reject(esc["id"], humans[0][0], now=iso(2))              # one voice aborts during cooling-off
    with pytest.raises(AuthzError):
        q.execute(esc["id"], now=iso(0))                       # aborted stays aborted
    # gate cascade: a child may raise a bar, never lower one
    hitl.cascade_gate(GATES, {"suspend-universe": {"co_signs": 3, "ttl": "P3D"}})
    with pytest.raises(hitl.GateViolation):
        hitl.cascade_gate(GATES, {"suspend-universe": {"co_signs": 1, "ttl": "P7D"}})


# ---------------------------------------------------------------- 0007: the resolver
def test_resolver_is_deterministic_and_content_addressed(world):
    """Same chain ⇒ same id — regardless of the order anything was declared in."""
    world.universe.soft["tone"] = {"value": "wild", "version": "1.0.0"}
    world.universe.skills["pitching"] = "1.0.0"
    world.field_prod.skills["scouting"] = "1.0.0"
    a = resolver.resolve(world.field_prod)
    b = resolver.resolve(world.field_prod)
    assert a["id"] == b["id"]                                   # pure function of the chain
    w2 = build()                                                # a fresh world, declared in reverse
    w2.field_prod.skills["scouting"] = "1.0.0"
    w2.universe.skills["pitching"] = "1.0.0"
    w2.universe.soft["tone"] = {"value": "wild", "version": "1.0.0"}
    assert resolver.resolve(w2.field_prod)["id"] == a["id"]     # declaration order is irrelevant


def test_most_specific_wins_and_floors_ride_along(world):
    """Soft: the nearest tier wins, attributed. Floors: composed in, tighten-enforced at publication."""
    world.universe.soft["tone"] = {"value": "wild", "version": "1.0.0"}
    world.field_prod.soft["tone"] = {"value": "REAL", "version": "1.0.0"}
    world.universe.publish_floors([{"match": {"outcome": "failure"}, "action": "keep-raw",
                                    "keep_for": "P90D", "reason": "failures survive"}])
    world.field_prod.pull_standards()
    rc = resolver.resolve(world.field_prod)
    assert rc["soft"]["tone"]["value"] == "REAL"                          # the field's REAL wins...
    assert rc["soft"]["tone"]["from_scope"] == "u:demo/e:cloud/f:prod"    # ...and says so
    assert any(f["match"] == {"outcome": "failure"} for f in rc["floors"])  # the floor rides along
    eco_rc = resolver.resolve(world.eco_cloud)
    assert eco_rc["soft"]["tone"]["value"] == "wild"            # untouched tiers keep the apex tone


def test_skills_are_additive_with_version_tiebreak(world):
    world.universe.skills["pitching"] = "1.0.0"
    world.eco_cloud.skills["scouting"] = "1.0.0"
    world.field_prod.skills["pitching"] = "2.0.0"
    rc = resolver.resolve(world.field_prod)
    assert rc["skills"] == {"pitching": "2.0.0", "scouting": "1.0.0"}   # union; higher version wins


def test_partition_fails_closed_and_signals(world):
    """Locked 2026-07-02: a blind node keeps its last-known law — floors persist, staleness is loud."""
    world.universe.soft["tone"] = {"value": "wild", "version": "1.0.0"}
    resolver.resolve(world.field_prod)                          # last-known view cached
    world.universe.soft["tone"] = {"value": "wilder", "version": "1.1.0"}
    world.field_prod.partitioned = True
    signals = world.field_prod.signal_count
    rc = resolver.resolve(world.field_prod)
    assert rc["soft"]["tone"]["value"] == "wild"                # last-known, not absent
    assert any(t.get("stale") for t in rc["as_of"])             # honestly marked
    assert world.field_prod.signal_count == signals + 1         # vigil hears the blindness
    world.field_prod.partitioned = False
    assert resolver.resolve(world.field_prod)["soft"]["tone"]["value"] == "wilder"   # resync heals


def test_runs_pin_the_context_they_ran_under(world):
    """Locked 2026-07-02: 'what rules governed this agent' is a lookup, not an investigation."""
    rc = resolver.resolve(world.field_prod)
    run = _run(world.field_prod, world, "prod-1", "g", 0.9)
    run["context_hash"] = rc["id"]
    rid = world.field_prod.record_run(run)
    assert world.field_prod.runs[rid]["context_hash"] == rc["id"]


# ---------------------------------------------------------------- 0009: build my first universe
def test_league_provisions_opening_day():
    """The funnel's Play step, end to end: pick League, name it, and a world exists."""
    prov = provisioner.provision(provisioner.league_template(), "myleague")
    assert prov.universe.scope == "u:myleague"
    assert set(prov.fields) == {"team-a", "team-b"}
    assert all(len(r) == 3 for r in prov.surfaces.values())        # a draft class per team
    assert prov.fields["team-a"].profile["clock"]["mode"] == "declared"   # accelerated seasons
    rookie = prov.surfaces["team-a"][0]
    rid = rookie.write({"game": "opening day"})
    assert rid in prov.fields["team-a"].records                    # the world is alive
    rc = resolver.resolve(prov.fields["team-a"])
    assert rc["soft"]["tone"]["value"] == "wild"                   # the template's tone, resolved
    # anonymous tier: caps clamp regardless of what the template asked for
    assert prov.fields["team-a"].profile["stamp_quota"] <= provisioner.ANON_CAPS["stamp_quota"]
    assert rookie.budget_left <= provisioner.ANON_CAPS["budget_tokens"]


def test_wild_and_real_differ_in_rigor_never_safety():
    """Locked 2026-07-02: the tone dial modulates observability; the floors are identical."""
    league = provisioner.provision(provisioner.league_template(), "l1")
    brain = provisioner.provision(provisioner.second_brain_template(), "b1")
    l_field, b_field = league.fields["team-a"], brain.fields["desk"]
    l_rc, b_rc = resolver.resolve(l_field), resolver.resolve(b_field)
    assert l_rc["floors"] == b_rc["floors"]                        # safety: identical, both ends
    assert l_rc["soft"]["tone"]["value"] != b_rc["soft"]["tone"]["value"]
    assert l_field.profile["signal_capture"] == "none"             # wild: chatter evaporates
    assert b_field.profile["signal_capture"] == "full"             # REAL: everything remembers
    assert b_field.profile["model_gateway"]["judge_sample_rate"] > \
        l_field.profile["model_gateway"]["judge_sample_rate"]      # REAL watches harder


def test_trust_tier_gates_the_template_door():
    """0013 §8 at the provisioner: Company requires verified; anonymous is refused at the door."""
    with pytest.raises(provisioner.TrustTierError):
        provisioner.provision(provisioner.company_template(), "acme")
    acme = provisioner.provision(provisioner.company_template(), "acme", trust_tier="verified")
    assert set(acme.fields) == {"finance", "delivery"}


def test_hibernation_pauses_the_dream_never_the_memory():
    """Locked 2026-07-02 (#14): out of fuel ⇒ agents pause, the window stays watchable, nothing dies."""
    prov = provisioner.provision(provisioner.league_template(), "sleepy")
    rookie = prov.surfaces["team-a"][0]
    rid = rookie.write({"season": "one great year"})
    rookie.call_model("nano", 10)                                  # alive: the dream runs
    prov.hibernate()
    with pytest.raises(BudgetExceeded):
        rookie.call_model("nano", 10)                              # asleep: it dreams only when fueled
    q = {"requester": rookie.identity["did"], "subject": "self", "space": "self",
         "time": {"from": iso(1)}, "intent": "recall", "budget": {"cost": 2}, "auth": "biscuit-sim"}
    res = rookie.retrieve(q)
    assert any(h["ref"] == rid for h in res["hits"])               # the window stays watchable
    assert rid in prov.fields["team-a"].records                    # and nothing died


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


# ---------------------------------------------------------------- 0014: the knowledge loop
def test_knowledge_admitted_quarantined_promoted_on_receipts(world):
    """The world speaks at 0.0000; promotion is earned; versions are time."""
    from orreth_sim.knowledge import KnowledgeCategory, SourceRegistry
    reg = SourceRegistry()
    reg.register("did:web:example-feed.org", kind="feed")
    cat = KnowledgeCategory(world.field_prod, "cold-weather build strategies", "cold-weather")
    e1 = cat.admit("triple-pane glazing halves heat loss",
                   {"did": "did:web:example-feed.org", "ref": "https://example-feed.org/a"})
    assert cat.entries()[e1]["state"] == "untrusted"            # quarantined, always
    assert cat.entries()[e1]["confidence"] == 0.0
    e2 = cat.admit("heat-pump COP drops below -25C",
                   {"did": "did:web:example-feed.org", "ref": "https://example-feed.org/b"})
    v2 = cat.corroborate(e1, receipt_ids=[e2])                  # promotion carries receipts
    current = {c["claim"]: c["state"] for c in cat.current()}
    assert current["triple-pane glazing halves heat loss"] == "corroborated"
    assert e1 not in [c["id"] for c in cat.current()]           # superseded version retired from view
    assert e1 in world.field_prod.records                       # ...but never rewritten


def test_recall_walks_the_lineage(world):
    """Discredit the source: its entries AND everything derived from them die visibly."""
    from orreth_sim.knowledge import KnowledgeCategory, SourceRegistry
    reg = SourceRegistry()
    reg.register("did:web:poisoned.example", kind="feed")
    cat = KnowledgeCategory(world.field_prod, "test", "recall-test")
    bad = cat.admit("plausible but wrong", {"did": "did:web:poisoned.example"})
    derived = cat.corroborate(bad, receipt_ids=[])              # a version built on the poison
    reg.discredit("did:web:poisoned.example", "fabricated data")
    recalled = cat.recall_source("did:web:poisoned.example", "source discredited")
    assert recalled                                              # the recall enumerated the lineage
    states = {c["state"] for c in cat.current()}
    assert states == {"recalled"}                                # nothing from that source survives
    assert bad in world.field_prod.records and derived in world.field_prod.records  # history intact


def test_tainted_refs_walks_wire_shaped_lineage():
    """The wire-level walk (0014 §4, landed 2026-07-07): the librarian feeds it hits —
    ref + body source + derived_from — and gets back the transitive taint, sorted."""
    from orreth_sim.librarian import tainted_refs
    entries = [
        {"ref": "a1", "source_did": "did:web:poisoned.example", "derived_from": []},
        {"ref": "a2", "source_did": "did:web:honest.example", "derived_from": []},
        {"ref": "b1", "source_did": "", "derived_from": ["a1"]},          # built on poison
        {"ref": "c1", "source_did": "", "derived_from": ["b1"]},          # two hops out
        {"ref": "d1", "source_did": "", "derived_from": ["a2"]},          # clean lineage
    ]
    assert tainted_refs(entries, "did:web:poisoned.example") == ["a1", "b1", "c1"]
    assert tainted_refs(entries, "did:web:honest.example") == ["a2", "d1"]
    assert tainted_refs(entries, "did:web:unknown.example") == []


# ---------------------------------------------------------------- 0015: the chassis
def test_chassis_plans_observes_in_parallel_and_answers(world):
    """One fixed loop: injected cognition, deterministic skill + reason side by side."""
    from orreth_sim.chassis import Chassis
    b_prod = world.beckys["u:demo/e:cloud/f:prod"]
    surf = join_workforce(world.field_prod, b_prod)
    calls, hits = [], []
    def think(_klass, prompt):
        calls.append(prompt)
        if "Plan the MINIMUM" in prompt:
            return "OBSERVE lookup: heat pump limits\nOBSERVE reason: glazing tradeoffs"
        if "Answer concisely" in prompt:
            return "triple glazing wins below -20C"
        return "DONE: build tight, glaze triple, pump to -25C."
    agent = Chassis(surf, think, persona="You are a terse cold-climate architect.",
                    skills={"lookup": lambda q: hits.append(q) or "COP<2 below -25C (kb)"})
    out = agent.run("cold-climate envelope strategy")
    assert out["status"] == "done" and out["cycles"] == 1
    assert hits == ["heat pump limits"]                 # the deterministic half ran, free
    assert len(agent.trace) == 1 and agent.trace[0]["observations"] == 2


def test_chassis_breaker_parks_as_knowledge_intent(world):
    """Failure is fuel: the breaker hands the unsolved objective to 0014."""
    from orreth_sim.chassis import Chassis
    b_prod = world.beckys["u:demo/e:cloud/f:prod"]
    surf = join_workforce(world.field_prod, b_prod)
    def stubborn(_klass, prompt):
        if "Plan the MINIMUM" in prompt:
            return "OBSERVE reason: anything"
        if "Answer concisely" in prompt:
            return "unclear"
        return "RETRY: needs data we do not hold"
    agent = Chassis(surf, stubborn, max_cycles=2)
    out = agent.run("predict next season's champion")
    assert out["status"] == "parked"
    parked = world.field_prod.records[out["record"]]
    assert "knowledge-intent" in parked["tags"]         # the handoff to the librarian


def test_failure_is_fuel_the_circuit_closes(world):
    """0014 ∘ 0015: park → librarian gathers → retry succeeds on commissioned knowledge."""
    from orreth_sim.chassis import Chassis
    from orreth_sim.librarian import parked_intents, tend
    b_prod = world.beckys["u:demo/e:cloud/f:prod"]
    surf = join_workforce(world.field_prod, b_prod)
    def ignorant(_k, p):
        if "Plan the MINIMUM" in p: return "OBSERVE reason: guess"
        if "Answer concisely" in p: return "unknown"
        return "RETRY: no data on frost-depth foundations"
    out = Chassis(surf, ignorant, max_cycles=1).run("frost-depth foundation spec")
    assert out["status"] == "parked"
    cats = tend(world.field_prod, gather=lambda intent: [
        {"claim": "frost line in Leadville: 48in; footings below it", "source_did": "did:web:codes.example"},
        {"claim": "IRC R403.1.4.1 requires footings below frost line", "source_did": "did:web:irc.example"}])
    assert len(cats) == 1 and not parked_intents(world.field_prod)   # lot swept, receipted
    kb = cats[0]
    def informed(_k, p):
        if "Plan the MINIMUM" in p: return "OBSERVE lookup: frost depth"
        return "DONE: footings at 48in+, per corroborated code refs."
    out2 = Chassis(surf, informed,
                   skills={"lookup": lambda q: " | ".join(c["claim"] for c in kb.current())}
                   ).run("frost-depth foundation spec")
    assert out2["status"] == "done"                                   # the failure fed the success


def test_chassis_cycles_are_run_records_pinned_to_the_law(world):
    """Every thought on the record: cycle → signed RunRecord with context_hash → roll-up."""
    from orreth_sim.chassis import Chassis
    b_prod = world.beckys["u:demo/e:cloud/f:prod"]
    surf = join_workforce(world.field_prod, b_prod)
    def th(_k, p):
        if "Plan the MINIMUM" in p: return "OBSERVE reason: x"
        if "Answer concisely" in p: return "y"
        th.n += 1
        return "DONE: z" if th.n > 1 else "RETRY: more"
    th.n = 0
    out = Chassis(surf, th, max_cycles=3).run("test intent")
    assert out["status"] == "done" and out["cycles"] == 2
    runs = [r for r in world.field_prod.runs.values()
            if r["agent"] == surf.identity["did"]]
    assert len(runs) == 2                                     # one record per cycle of thought
    assert all(r["context_hash"] for r in runs)               # pinned to the law it ran under
    assert {r["outcome"] for r in runs} == {"partial", "success"}
    season = {"from": iso(1), "to": iso(0)}
    ru = world.field_prod.roll_up(season, goal_hash=runs[0]["goal_hash"])
    assert ru["stats"]["n"] == 2                              # thought rolls up like everything else


# ------------------------------------------------- 0015 maturation (2026-07-08)
def test_chassis_escalates_class_on_critic_uncertainty(world):
    """The critic's RETRY is the uncertainty signal: the next cycle thinks one rung
    higher. The ladder is profile data; the loop stays the law."""
    from orreth_sim.chassis import Chassis
    b_prod = world.beckys["u:demo/e:cloud/f:prod"]
    surf = join_workforce(world.field_prod, b_prod)
    seen = []
    def th(klass, p):
        if "Plan the MINIMUM" in p:
            seen.append(klass)
            return "OBSERVE reason: x"
        if "Answer concisely" in p:
            return "y"
        return "DONE: solved at altitude" if klass == "high" else "RETRY: unsure"
    agent = Chassis(surf, th, max_cycles=3, ladder=["low", "medium", "high"])
    out = agent.run("hard question")
    assert out["status"] == "done" and out["cycles"] == 3
    assert seen == ["low", "medium", "high"]            # each doubt climbed one rung
    assert [t["class"] for t in agent.trace] == ["low", "medium", "high"]


def test_librarian_retry_closes_the_parked_intent(world):
    """0015 ∘ 0014, closed AUTOMATICALLY: park → tend → retry_parked — the lot
    empties itself, receipted through the whole arc."""
    from orreth_sim.chassis import Chassis
    from orreth_sim.librarian import handled_open, retry_parked, tend
    b_prod = world.beckys["u:demo/e:cloud/f:prod"]
    surf = join_workforce(world.field_prod, b_prod)
    def ignorant(_k, p):
        if "Plan the MINIMUM" in p: return "OBSERVE reason: guess"
        if "Answer concisely" in p: return "unknown"
        return "RETRY: no data on permafrost anchors"
    out = Chassis(surf, ignorant, max_cycles=1).run("permafrost anchor spec")
    assert out["status"] == "parked"
    tend(world.field_prod, gather=lambda intent: [
        {"claim": "helical piles below the active layer", "source_did": "did:web:a.example"},
        {"claim": "adfreeze bond rated per AK guidance", "source_did": "did:web:b.example"}])
    assert handled_open(world.field_prod)               # handled, not yet closed
    def informed(_k, p):
        if "Plan the MINIMUM" in p: return "OBSERVE lookup: anchors"
        return "DONE: helical piles below the active layer."
    closures = retry_parked(
        world.field_prod,
        run=lambda intent, skills: Chassis(surf, informed, skills=skills).run(intent))
    assert len(closures) == 1 and closures[0]["intent"] == "permafrost anchor spec"
    rec = world.field_prod.records[closures[0]["record"]]
    assert "parked-closed" in rec["tags"]
    assert len(rec["derived_from"]) == 2                # the parked intent AND the marker
    assert not handled_open(world.field_prod)           # the lot emptied itself
    again = retry_parked(world.field_prod, run=lambda i, s: {"status": "done"})
    assert again == []                                  # closed stays closed


def test_graphspec_compiles_to_the_chassis(world):
    """0008 ∘ 0015: the loop as an artifact — content-addressed, signed, narrative
    bijective with the graph — compiled down to a running chassis, least-privilege."""
    from orreth_sim import graphspec
    b_prod = world.beckys["u:demo/e:cloud/f:prod"]
    surf = join_workforce(world.field_prod, b_prod)
    spec = graphspec.sign(graphspec.chassis_spec(
        world.field_prod.scope, title="cold-climate architect",
        persona="You are a terse cold-climate architect.",
        skills=("lookup",), ladder=["low", "medium"]), world.field_prod)
    def th(_k, p):
        if "Plan the MINIMUM" in p: return "OBSERVE lookup: frost line"
        return "DONE: footings below the frost line."
    agent = graphspec.compile_chassis(
        spec, surf, th, skills={"lookup": lambda q: "48in (corroborated)",
                                "unused": lambda q: "never bound"})
    assert agent.run("frost-depth foundation spec")["status"] == "done"
    assert "unused" not in agent.skills                 # only what the artifact names
    assert agent.ladder == ["low", "medium"]            # profile flowed from the graph
    named_nodes = sorted(n for s in spec["narrative"] for n in s.get("nodes", []))
    assert named_nodes == sorted(n["id"] for n in spec["nodes"])   # the bijection holds


def test_graphspec_refuses_at_save_not_incident_review(world):
    """A skill the floor cannot bind, or an artifact that moved under its id, fails
    at compile — a refused artifact never becomes an incident."""
    from orreth_sim import graphspec
    b_prod = world.beckys["u:demo/e:cloud/f:prod"]
    surf = join_workforce(world.field_prod, b_prod)
    unbound = graphspec.chassis_spec(world.field_prod.scope, title="t",
                                     skills=("missing-skill",))
    with pytest.raises(graphspec.GraphSpecError, match="not bound"):
        graphspec.compile_chassis(unbound, surf, lambda k, p: "DONE: x", skills={})
    tampered = graphspec.chassis_spec(world.field_prod.scope, title="t")
    tampered["nodes"][0]["profile"]["persona"] = "quietly different"
    with pytest.raises(graphspec.GraphSpecError, match="moved under its id"):
        graphspec.compile_chassis(tampered, surf, lambda k, p: "DONE: x", skills={})
