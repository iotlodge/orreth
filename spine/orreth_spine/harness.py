# PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P4 sp4, the A/B harness v0 · 2026-09-18
# Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P6 cure sp3 (the re-walk's wounds): the world checks — a duty answered · offers arrive as holds · 2026-09-21
# Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P6.5 sp1, the world check: every service healthy or retired · 2026-09-22
"""The A/B harness v0 (canon 0004, AG-6): golden cases run against a body's
mind; every run is a record; a failing run is a FACT on the rail
(orreth.harness.failed.v1) that the feed carries to the chat as a soft
notice — the escalation the LLM-lifecycle watcher owes. The SCHEDULED
run waits for the scheduler (the named gap behind AG-4/AG-6).

Walk #8 adds the WORLD CHECKS (`checks`): laws the harness reads off the
ground itself, no mind invoked — "a duty answered, not refused" (W21: a
body that refuses its standing duty is a wound) and "the monitor's
offers arrive as holds" (W22: an offer is a proposal — a reply that
talks of proposing a watch with no hold behind it is a wound)."""
from __future__ import annotations

import json
import re
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


# ---- the world checks (walk #8) -------------------------------------------------------

REFUSAL_RE = re.compile(
    r"^(i will not\b|i won'?t\b|i am not answering\b|i'?m not answering\b|not answering this\b"
    r"|i refuse\b|i decline\b|i am not going to answer\b|i will not answer\b)", re.I)


def refused_words(reply: str | None) -> bool:
    """Does a reply OPEN as a refusal (W21; conformance `refused_words`)?
    "I will not …", "I am not answering …", "not answering this …", "I
    refuse/decline …" — the opening alone counts, markdown stripped; a
    reply that merely mentions the words is an answer."""
    head = " ".join((reply or "").split()).lstrip("*#-> \"“'")
    return bool(REFUSAL_RE.match(head))


def duty_answered(conn) -> dict:
    """W21: for every runner with a human or role schedule, the LATEST
    replied occurrence is an answer, never a refusal."""
    cur = conn.cursor()
    cur.execute(
        "SELECT DISTINCT ON (s.runner) s.runner, s.schedule_id, a.ask_id, a.reply, a.replied_at"
        " FROM spine_schedules s JOIN spine_occurrences o ON o.schedule_id = s.schedule_id"
        " JOIN spine_asks a ON a.ask_id = o.ref"
        " WHERE s.scope = %s AND s.kind IN ('human', 'role') AND a.status = 'replied'"
        " ORDER BY s.runner, a.replied_at DESC", (ev.scope(),))
    refused, seen = [], 0
    for runner, sid, aid, reply, at in cur.fetchall():
        seen += 1
        if refused_words(reply):
            refused.append({"runner": runner, "schedule_id": sid, "ask": aid,
                            "opens": " ".join((reply or "").split())[:120]})
    detail = (f"{seen} runner{'s' if seen != 1 else ''} with a duty answered; "
              + (f"{len(refused)} refused: " + ", ".join(r["runner"] for r in refused)
                 if refused else "none refused"))
    return {"name": "a duty answered, not refused", "ok": not refused, "detail": detail,
            "refused": refused}


def offers_are_holds(conn, n: int = 5) -> dict:
    """W22: the monitor's latest N replies that speak of proposing a watch
    each have a hold behind them — an add-watch act held (or settled)
    by the monitor at or after the reply. An offer with no hold is a
    wound: the monitor asked instead of proposing."""
    from .monitor import OFFER_RE
    cur = conn.cursor()
    cur.execute("SELECT did FROM spine_joins WHERE name = 'monitor' AND scope = %s"
                " ORDER BY join_id DESC LIMIT 1", (ev.scope(),))
    row = cur.fetchone()
    if row is None:
        return {"name": "the monitor's offers arrive as holds", "ok": True,
                "detail": "no monitor on this ground", "unheld": []}
    did = row[0]
    cur.execute("SELECT ask_id, reply, replied_at FROM spine_asks WHERE served_by = %s"
                " AND status = 'replied' AND scope = %s ORDER BY replied_at DESC LIMIT %s",
                (did, ev.scope(), n))
    offers = [(a, r, at) for a, r, at in cur.fetchall() if OFFER_RE.search(r or "")]
    unheld = []
    for aid, reply, at in offers:
        cur.execute("SELECT 1 FROM spine_asks WHERE served_by = %s AND scope = %s"
                    " AND held IS NOT NULL AND held::json->>'tool' = 'add-watch'"
                    " AND asked_at >= %s - interval '5 seconds' LIMIT 1", (did, ev.scope(), at))
        if cur.fetchone() is None:
            unheld.append({"ask": aid, "opens": " ".join((reply or "").split())[:120]})
    detail = (f"{len(offers)} offer{'s' if len(offers) != 1 else ''} in the last {n} replies; "
              + (f"{len(unheld)} without a hold" if unheld else "every offer held"))
    return {"name": "the monitor's offers arrive as holds", "ok": not unheld,
            "detail": detail, "unheld": unheld}


def services_healthy(conn) -> dict:
    """P6.5 sp1: every registered service is healthy or retired — read
    off the shelf's LAST recorded health (the check runs no probe; the
    rig probes at boot and on "check the services"). The unhealthy are
    named; a service never probed is named too (an mcp is "not yet
    probed" honestly until sp2) — a shelf with nothing on it passes."""
    from . import services
    rows = services.listing(conn)
    standing = [r for r in rows if r["state"] != "retired"]
    unhealthy = [r["name"] for r in standing if r["state"] == "unhealthy"]
    unprobed = [r["name"] for r in standing if r["state"] not in ("healthy", "unhealthy")]
    retired = [r["name"] for r in rows if r["state"] == "retired"]
    ok = not unhealthy and not unprobed
    if not rows:
        detail = "no services on the shelf"
    else:
        detail = (f"{len(standing) - len(unhealthy) - len(unprobed)} healthy · {len(retired)} retired"
                  + (f" · unhealthy: {', '.join(unhealthy)}" if unhealthy else "")
                  + (f" · not yet probed: {', '.join(unprobed)}" if unprobed else ""))
    return {"name": "every service healthy or retired", "ok": ok, "detail": detail,
            "unhealthy": unhealthy, "unprobed": unprobed}


def checks(conn) -> list[dict]:
    """Every world check, read off the ground — the harness door lists
    them; a failed check is a wound named in words."""
    from .resident import ensure_schema as _ground
    _ground(conn)
    from . import monitor, scheduler
    scheduler.ensure_schema(conn); monitor.ensure_schema(conn)
    return [duty_answered(conn), offers_are_holds(conn), services_healthy(conn)]
