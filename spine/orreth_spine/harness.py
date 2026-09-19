# PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P4 sp4, the A/B harness v0 · 2026-09-18
"""The A/B harness v0 (canon 0004, AG-6): golden cases run against a body's
mind; every run is a record; a failing run is a FACT on the rail
(orreth.harness.failed.v1) that the feed carries to the chat as a soft
notice — the escalation the LLM-lifecycle watcher owes. The SCHEDULED
run waits for the scheduler (the named gap behind AG-4/AG-6)."""
from __future__ import annotations

import json
import secrets
from pathlib import Path

from . import envelope as ev, outbox

HARNESS_FAILED = "orreth.harness.failed.v1"
GOLDEN = Path(__file__).resolve().parents[1] / "golden"


def ensure_schema(conn) -> None:
    from .outbox import once
    if not once(conn, "harness"):
        return
    with conn.transaction():
        cur = conn.cursor()
        cur.execute("SELECT pg_advisory_xact_lock(742199)")  # DDL race guard
        cur.execute(
            "CREATE TABLE IF NOT EXISTS spine_harness_runs ("
            " run_id text PRIMARY KEY, template text NOT NULL,"
            " version text NOT NULL, passed int NOT NULL, failed int NOT NULL,"
            " details text NOT NULL, scope text NOT NULL,"
            " ran_at timestamptz NOT NULL DEFAULT now())")


def golden(template: str) -> list[dict]:
    p = GOLDEN / f"{template}.v0.json"
    return json.loads(p.read_text()) if p.exists() else []


def run(conn, body, cases: list[dict] | None = None,
        parent_marker: str | None = None) -> dict:
    """Run the golden cases through the body's own graph (its mind on the
    meter, its recall honestly empty of any ask) and record the run."""
    from .resident import ensure_schema as _ground   # lazily: no import cycle
    _ground(conn)
    ensure_schema(conn)
    outbox.ensure_schema(conn)
    cases = cases if cases is not None else golden(body.template["name"])
    body._serve_conn = conn
    body._current_ask = None
    details, passed = [], 0
    for c in cases:
        out = body._graph.invoke({"text": c["ask"], "reply": "", "steps": [],
                                  "notes": [], "hold": None, "read": []})
        reply = out.get("reply") or ""
        ok = all(x.lower() in reply.lower() for x in c.get("expect", []))
        passed += ok
        details.append({"ask": c["ask"], "expect": c.get("expect", []),
                        "reply": reply[:300], "ok": ok})
    failed = len(cases) - passed
    rid = "run_" + secrets.token_hex(5)
    version = body.template.get("version", "?")
    from . import markers
    markers.ensure_schema(conn)
    mid = markers.new_id()
    marker = {"kind": "observation", "id": mid, "parent": parent_marker,
              "by": body.identity.did}
    with conn.transaction():
        cur = conn.cursor()
        markers.insert(cur, mid, "observation", parent_marker, rid,
                       body.identity.did, f"harness: {passed} passed, {failed} failed")
        cur.execute(
            "INSERT INTO spine_harness_runs (run_id, template, version, passed,"
            " failed, details, scope) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (rid, body.template["name"], version, passed, failed,
             json.dumps(details), ev.scope()))
    if failed:
        e = ev.make_envelope(
            kind="event", type=HARNESS_FAILED, universe_id=ev.scope(),
            scope_path=ev.scope(),
            payload={"ref": rid, "hash": "sha256:-", "template": body.template["name"],
                     "version": version, "passed": passed, "failed": failed},
            correlation_id=rid, authority_chain=[body.identity.did], marker=marker)
        outbox.commit_with_outbox(conn, ev.encode(e), e["message_id"])
    return {"run_id": rid, "template": body.template["name"], "version": version,
            "passed": passed, "failed": failed, "details": details}
