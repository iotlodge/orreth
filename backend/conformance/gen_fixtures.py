"""Generate the language-neutral conformance fixtures (0000 §3: 'lift the contract, port the engine').

The Python simulator is the reference; these fixtures are the spec the Rust plane must pass.
Pure input → output pairs only — no clocks, no randomness (0007 §4 is what makes this possible).

Run from backend/conformance:  uv run python gen_fixtures.py
"""
from __future__ import annotations

import json
from pathlib import Path

from orreth_sim import crypto, rollup

OUT = Path(__file__).parent / "fixtures"


def _write(name: str, data: dict) -> None:
    OUT.mkdir(exist_ok=True)
    (OUT / name).write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    print(f"  fixtures/{name}")


# ---- crypto: canonicalization + content-addressing + a real signature vector ----------
def gen_crypto() -> None:
    objs = [
        {"b": 1, "a": 2},
        {"nested": {"z": [3, 1, 2], "a": {"y": None, "x": True}}, "s": "täst ⚡"},
        {"floats": [0.9, 0.81, 1.0, 0.001, 123456.789], "int": 42},
        {"empty": {}, "list": [], "zero": 0, "neg": -7},
    ]
    kp = crypto.KeyPair()
    payload = {"id": "sha256:abc", "kind": "episodic", "scope": "u:demo/e:x/f:y",
               "author": "did:key:zTEST", "occurred_at": "2026-07-01T00:00:00Z",
               "provenance_class": "lived"}
    sig = kp.sign("did:key:" + kp.public, payload)
    _write("crypto.json", {
        "description": "Canonical JSON (sorted keys, no whitespace, shortest-float) + sha256 "
                       "content-addressing + one real Ed25519 signature to verify.",
        "canonical_vectors": [
            {"input": o, "canonical": crypto.canonical(o).decode(), "hash": crypto.content_hash(o)}
            for o in objs
        ],
        "signature_vector": {
            "payload": payload, "public": kp.public, "sig": sig,
            "note": "verify sig.sig (urlsafe b64, no pad) over canonical(payload minus sig/signature)",
        },
    })


# ---- rollup: the monoid + the Bayesian report edge -------------------------------------
def _mk_run(score: float, outcome: str = "success", objective: str = "reliability",
            breach: bool = False, tokens: int = 100) -> dict:
    return {"outcome": outcome, "cost": {"tokens": tokens},
            "scores": [{"objective": objective, "score": score,
                        **({"floor_breached": True} if breach else {})}]}


def gen_rollup() -> None:
    cases = []
    runs_a = [_mk_run(s) for s in (0.9, 0.8, 0.7)]
    runs_b = [_mk_run(0.95), _mk_run(0.6, outcome="failure"),
              _mk_run(0.98, objective="compliance", breach=True)]
    for name, runs in (("simple", runs_a), ("mixed_with_breach", runs_a + runs_b)):
        merged = rollup.empty_bundle()
        for r in runs:
            merged = rollup.merge(merged, rollup.bundle_of(r))
        cases.append({
            "name": name, "runs": runs, "merged": merged,
            "report_reliability_uniform_prior": rollup.report(merged, "reliability"),
            "tier_score": rollup.tier_score(merged, [
                {"objective": "reliability", "weight": 1.0},
                {"objective": "compliance", "weight": 1.0, "floor": True}]),
        })
    _write("rollup.json", {
        "description": "The StatBundle monoid (0005): merge must be associative with empty as "
                       "identity; the Beta prior applies ONCE at report; floors flag, never average. "
                       "Floats compare to 1e-9.",
        "empty": rollup.empty_bundle(),
        "cases": cases,
    })


# ---- resolver: the fold (0007) — chain in, resolved content out ------------------------
def gen_resolver() -> None:
    # the resolver core as pure data: tiers root -> leaf, each (scope, soft, skills, version)
    tiers = [
        {"scope": "u:demo", "version": "0.0.1",
         "soft": {"tone": {"value": "wild", "version": "1.0.0"}},
         "skills": {"pitching": "1.0.0"}},
        {"scope": "u:demo/e:cloud", "version": "0.0.1",
         "soft": {}, "skills": {"scouting": "1.0.0"}},
        {"scope": "u:demo/e:cloud/f:prod", "version": "0.0.1",
         "soft": {"tone": {"value": "REAL", "version": "1.0.0"}},
         "skills": {"pitching": "2.0.0"}},
    ]
    floors = [{"match": {"outcome": "failure"}, "action": "keep-raw",
               "keep_for": "P90D", "reason": "failures survive"}]
    # expected output computed exactly as resolver.py folds (kept in lockstep by the sim tests)
    soft, skills = {}, {}
    for t in tiers:
        for k, std in t["soft"].items():
            soft[k] = {"value": std["value"], "from_scope": t["scope"], "version": std["version"]}
        for name, ver in t["skills"].items():
            skills[name] = max(skills.get(name, "0.0.0"), ver,
                               key=lambda v: [int(x) for x in v.split("-")[0].split(".")])
    sorted_floors = sorted(floors, key=crypto.content_hash)
    as_of = [{"scope": t["scope"], "version": t["version"]} for t in tiers]
    content = {"scope": tiers[-1]["scope"], "floors": sorted_floors,
               "soft": soft, "skills": skills, "as_of": as_of}
    _write("resolver.json", {
        "description": "The cascade fold (0007): soft = most-specific-wins (attributed) · skills = "
                       "additive, higher version wins · floors sorted by content hash · the id is the "
                       "content hash of the canonical resolved content. Deterministic — same chain, "
                       "same id, regardless of declaration order.",
        "cases": [{
            "name": "three_tier_chain",
            "tiers": tiers, "floors": floors,
            "expected": {**content, "id": crypto.content_hash(content)},
        }],
    })


# ---- flows: the node semantics (store + gateway checks + retrieval router) -------------
def gen_flows() -> None:
    """Script a deterministic scenario against the reference sim; dump inputs + expected
    outputs. Timestamps are pinned; the plane verifies signatures, never signs (the steward
    is cognition), so every record here is pre-signed by the reference."""
    from orreth_sim.node import ClockViolation, Refusal, make_memory
    from orreth_sim.world import build

    w = build()
    prod, pkp = w.agents["prod-1"]
    lab, lkp = w.agents["lab-1"]
    T = lambda d, h=0: f"2026-06-{d:02d}T{h:02d}:00:00Z"
    NOW_PIN = "2026-07-01T00:00:00Z"

    # flow 1: a floor published at the apex, pulled down the chain
    floor = {"match": {"outcome": "failure"}, "action": "keep-raw",
             "keep_for": "P90D", "reason": "failures survive"}
    w.universe.publish_floors([floor])
    w.eco_cloud.pull_standards()
    w.field_prod.pull_standards()
    w.field_lab.pull_standards()

    writes, records = [], {}

    def try_write(node, rec, expect=None):
        try:
            node.write(rec)
            outcome = {"expect": "ok", "expect_keep_class": node.records[rec["id"]]["keep_class"]}
        except ClockViolation:
            outcome = {"expect": "clock-violation"}
        except Exception as e:
            outcome = {"expect": str(e.__class__.__name__)}
        records[rec["id"]] = rec
        writes.append({"at_scope": node.scope, "record": rec, **(expect or outcome)})

    r1 = make_memory(prod, pkp, prod["scope"], {"n": 1}, occurred_at=T(10))
    r2 = make_memory(prod, pkp, prod["scope"], {"boom": 1}, tags=["failure"], occurred_at=T(12))
    r3 = make_memory(prod, pkp, prod["scope"], {"late": 1}, occurred_at=T(11))       # backdated
    r4 = make_memory(prod, pkp, prod["scope"], {"old": 1}, occurred_at=T(2),
                     provenance_class="ingested-archive")                            # archive OK
    r5 = make_memory(prod, pkp, prod["scope"], {"phi": 1}, occurred_at=T(14))        # tombstoned later
    bad = make_memory(prod, pkp, prod["scope"], {"t": 1}, occurred_at=T(15))
    bad["body"] = "dGFtcGVyZWQ"                                                      # body not signed;
    bad["kind"] = "semantic"                                                         # kind IS signed
    secret = make_memory(lab, lkp, lab["scope"], {"secret": 1}, occurred_at=T(10))
    folio = make_memory(lab, lkp, lab["scope"], {"portfolio": 1}, tenancy="portfolio",
                        occurred_at=T(11))
    for node, rec in ((w.field_prod, r1), (w.field_prod, r2), (w.field_prod, r3),
                      (w.field_prod, r4), (w.field_prod, r5), (w.field_prod, bad),
                      (w.field_lab, secret), (w.field_lab, folio)):
        try_write(node, rec)

    # flow 2's product arrives as a pre-signed record: the steward's distillation, pushed up
    dist = w.field_prod.run_distillation()
    w.field_prod.tombstone(r5["id"], by=prod["did"], reason="consent withdrawn")

    # flow 3: queries (tokens with far expiry; 'now' pinned for the plane's expiry check)
    def tok(agent, audience, grants=None, issuer=None):
        ident, _ = w.agents[agent]
        issuer = issuer or (w.becky if audience == "u:demo" else w.beckys[audience])
        return issuer.issue_token(ident["did"], audience,
                                  grants or [{"action": "retrieve", "space": "self"}])

    def q(agent, days_from="2026-01-01T00:00:00Z", cost=3, intent="recall", subject="self"):
        ident, _ = w.agents[agent]
        return {"requester": ident["did"], "subject": subject, "space": "self",
                "time": {"from": days_from}, "intent": intent,
                "budget": {"cost": cost}, "auth": "biscuit-sim"}

    queries = []

    def try_query(name, node, query, token, requester_scope):
        try:
            res = node.retrieve(query, token, requester_scope)
            expected = {"hit_refs": [h["ref"] for h in res["hits"]],
                        "fidelity": {h["ref"]: h["fidelity"] for h in res["hits"]},
                        "served_by": res["provenance"]["served_by"],
                        "verification": res["verification"],
                        "has_remainder": "remainder" in res}
        except Refusal:
            expected = {"refusal": True}
        queries.append({"name": name, "at_scope": node.scope, "query": query,
                        "token": token, "requester_scope": requester_scope,
                        "expect": expected})

    try_query("escalates_past_field_horizon", w.field_prod, q("prod-1"),
              tok("prod-1", "u:demo"), prod["scope"])
    try_query("budget_miss", w.field_prod, q("prod-1", cost=1),
              tok("prod-1", "u:demo"), prod["scope"])
    try_query("authz_miss_same_shape", w.field_prod, q("prod-1", cost=99),
              tok("prod-1", "u:demo/e:cloud/f:prod"), prod["scope"])
    try_query("sibling_raw_never", w.universe,
              q("prod-1", subject={"identity": lab["did"]}),
              tok("prod-1", "u:demo"), prod["scope"])
    try_query("interview_portfolio_only", w.field_lab,
              {**q("prod-1", subject={"identity": lab["did"]}, intent="interview", cost=2)},
              w.beckys["u:demo/e:dev/f:lab"].issue_token(
                  prod["did"], "u:demo/e:dev/f:lab",
                  [{"action": "retrieve", "space": {"scope": "u:demo/e:dev/f:lab"},
                    "visibility": ["portfolio"]},
                   {"action": "interview", "space": {"scope": "u:demo/e:dev/f:lab"}}]),
              prod["scope"])
    try_query("no_retrieve_grant_refused", w.field_prod, q("prod-1"),
              tok("prod-1", "u:demo", grants=[{"action": "write", "space": "self"}]),
              prod["scope"])
    try_query("tombstoned_raw_gone_dist_labeled", w.field_prod,
              q("prod-1", subject={"identity": w.field_prod.steward["did"]}),
              tok("prod-1", "u:demo"), prod["scope"])

    _write("flows.json", {
        "description": "The node semantics end-to-end (store + gateway ingress + retrieval "
                       "router), scripted against the reference. The plane verifies, never "
                       "signs. Pinned clocks; expected outputs are exact.",
        "now": NOW_PIN,
        "identities": {d: e["public"] for d, e in w.nanda._e.items()},
        "revoked": [],
        "topology": [{"scope": n.scope, "horizon": n.profile["retrieval"]["horizon"]}
                     for n in (w.universe, w.eco_cloud, w.field_prod)],
        "lab_chain": [{"scope": n.scope, "horizon": n.profile["retrieval"]["horizon"]}
                      for n in (w.universe, w.eco_dev, w.field_lab)],
        "floors": [floor],
        "writes": writes,
        "distillation_pushed_up": dist,
        "tombstones": [{"at_scope": w.field_prod.scope, "record_id": r5["id"]}],
        "queries": queries,
    })


if __name__ == "__main__":
    print("generating conformance fixtures:")
    gen_crypto()
    gen_rollup()
    gen_resolver()
    gen_flows()
