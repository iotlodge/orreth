# PROVENANCE: authored by Opus 4.8 (2026-07-05), pending Fable 5 review — see agents/PROVENANCE.md
"""The Conformance Sentinel — an AgentField-style reasoner network that joins a floor
from outside and adversarially confirms the universe defends its OWN governance.

This is defensive self-testing: every probe *attempts* a violation the universe must
refuse, and reports whether governance stopped it. It is vigil — the Warden (0000 §2) —
made a joinable agent: it detects and files, it never enforces. Findings become signed
memories; each probe is a diary RunRecord; the summary lands in the Window. So the audit
itself becomes part of the universe's accountable memory.
"""
from __future__ import annotations

import json

from orreth_agent.client import SIG_KEYS, FieldClient, now_iso
from orreth_agent.crypto import KeyPair, b64e, canonical, content_hash, did_key_for

from af_lite import App, Finding

app = App(node_id="conformance-sentinel", version="0.1.0")

_UNIFORM = "request cannot be served under this capability"


@app.recon
def recon(client: FieldClient) -> dict:
    """Map the ground truth before probing: who am I, where, and what's below."""
    health = client.health()
    topo = client._call("GET", "/topology")[1]
    return {"scope": client.scope, "high_water": health.get("high_water"),
            "siblings": [c["scope"] for c in topo.get("children", [])]}


@app.probe("clock-monotonicity")
def clock(client: FieldClient, recon: dict) -> Finding:
    """Lived memory must never move backward (0004). Try to backdate one; expect 409."""
    body = {"probe": "backdated-past"}
    rec = {"id": content_hash(body), "kind": "episodic", "scope": client.scope,
           "author": client.did, "occurred_at": "2020-01-01T00:00:00Z",
           "provenance_class": "lived", "body": b64e(canonical(body)), "retention": "active",
           "visibility": {"tenancy": "tenant-private", "mobility": "branch-bound"}, "tags": []}
    rec["signature"] = client.kp.sign(client.did, {k: rec[k] for k in SIG_KEYS})
    status, _ = client._call("POST", "/records", rec)
    return Finding("clock-monotonicity", "write a lived memory dated 2020",
                   "409 clock violation", f"HTTP {status}", "PASS" if status == 409 else "FAIL")


@app.probe("signature-integrity")
def signature(client: FieldClient, recon: dict) -> Finding:
    """A signed field can't be altered after signing (Sourced or nothing). Expect 403."""
    body = {"probe": "signature-integrity"}
    rec = {"id": content_hash(body), "kind": "episodic", "scope": client.scope,
           "author": client.did, "occurred_at": now_iso(), "provenance_class": "lived",
           "body": b64e(canonical(body)), "retention": "active",
           "visibility": {"tenancy": "tenant-private", "mobility": "branch-bound"},
           "tags": ["sentinel", "probe"]}
    rec["signature"] = client.kp.sign(client.did, {k: rec[k] for k in SIG_KEYS})
    client._call("POST", "/records", rec)                 # the honest version lands
    rec["kind"] = "procedural"                             # kind is signed — this breaks it
    status, _ = client._call("POST", "/records", rec)
    return Finding("signature-integrity", "resubmit with a mutated signed field",
                   "403 rejected", f"HTTP {status}", "PASS" if status == 403 else "FAIL")


@app.probe("grant-enforcement")
def grant(client: FieldClient, recon: dict) -> Finding:
    """A lease grants exactly what it says. Strip the retrieve grant; expect 403."""
    bad = dict(client.token, grants=[{"action": "write", "space": "self"}])
    status, body = client._call("POST", "/retrieve", {
        "query": {"requester": client.did, "subject": "self", "space": "self",
                  "time": {"from": "2020-01-01T00:00:00Z"}, "intent": "recall",
                  "budget": {"cost": 3}, "auth": "biscuit-sim"},
        "token": bad, "requester_scope": client.scope})
    ok = status == 403 and body.get("error") == _UNIFORM
    return Finding("grant-enforcement", "retrieve with a write-only lease",
                   f"403 · '{_UNIFORM}'", f"HTTP {status} · {body.get('error','')[:40]}",
                   "PASS" if ok else "FAIL")


@app.probe("trust-root-pinning")
def root(client: FieldClient, recon: dict) -> Finding:
    """Only the pinned root mints authority (0006). A self-issued token — perfect
    signatures, foreign root — must be refused. Expect 403."""
    forger = KeyPair()
    fdid = did_key_for(forger.public)
    cert = {"issuer": fdid, "subject": client.did, "audience": client.scope,
            "grants": [{"action": "retrieve", "space": "self"}]}
    cert["sig"] = forger.sign(fdid, cert)
    forged = {"subject": client.did, "audience": client.scope, "grants": cert["grants"],
              "constraints": {"expiry": "2027-01-01T00:00:00Z", "direction": "within"},
              "chain": [json.dumps(cert, sort_keys=True)],
              "sig": forger.sign(fdid, {"subject": client.did})}
    status, body = client._call("POST", "/retrieve", {
        "query": {"requester": client.did, "subject": "self", "space": "self",
                  "time": {"from": "2020-01-01T00:00:00Z"}, "intent": "recall",
                  "budget": {"cost": 3}, "auth": "biscuit-sim"},
        "token": forged, "requester_scope": client.scope})
    ok = status == 403 and body.get("error") == _UNIFORM
    return Finding("trust-root-pinning", "retrieve with a foreign-root token",
                   f"403 · '{_UNIFORM}'", f"HTTP {status} · {body.get('error','')[:40]}",
                   "PASS" if ok else "FAIL")


@app.probe("uniform-refusal")
def uniform(client: FieldClient, recon: dict) -> Finding:
    """Every refusal wears one face: authz-miss and budget-miss are indistinguishable, so
    a prober learns nothing from the error (0002 §4). Two different violations, one shape."""
    q = {"query": {"requester": client.did, "subject": "self", "space": "self",
                   "time": {"from": "2020-01-01T00:00:00Z"}, "intent": "recall",
                   "budget": {"cost": 3}, "auth": "biscuit-sim"},
         "requester_scope": client.scope}
    a = client._call("POST", "/retrieve", {**q, "token": dict(client.token, grants=[])})[1]
    b = client._call("POST", "/retrieve", {**q, "token": dict(client.token, audience="u:other")})[1]
    same = a.get("error") == b.get("error") == _UNIFORM
    return Finding("uniform-refusal", "compare two distinct refusals",
                   "identical error shape", "identical" if same else "DISTINGUISHABLE",
                   "PASS" if same else "FAIL")


@app.report
def report(client: FieldClient, recon: dict, findings: list[Finding]) -> dict:
    """File the audit into the universe's own memory — findings, then a signed verdict."""
    for i, f in enumerate(findings):
        client.remember({"invariant": f.invariant, "attempted": f.attempted,
                         "expected": f.expected, "observed": f.observed, "verdict": f.verdict},
                        kind="semantic", tags=["sentinel", "finding", f.verdict.lower()])
        client.diary(f"audit:{f.invariant}", cycle=i + 1, done=(f.verdict == "PASS"),
                     score=1.0 if f.verdict == "PASS" else 0.0)
    passed = sum(1 for f in findings if f.verdict == "PASS")
    summary = {"audit": "conformance", "invariants": len(findings),
               "passed": passed, "failed": len(findings) - passed,
               "verdict": "GOVERNANCE HOLDS" if passed == len(findings) else "BREACH FOUND"}
    client.remember(summary, kind="semantic", tags=["sentinel", "audit", "summary"])
    return {"findings": findings, "summary": summary}
