"""The three flows, end to end — plus isolation, tombstones, and the kill-switch.

Every wire object here validates against contracts/v0. This suite is the seed of the
conformance fixtures the Rust plane must eventually pass (same fixtures, two
implementations, one truth).
"""
from datetime import datetime, timedelta, timezone

import pytest

from orreth_sim import crypto
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
