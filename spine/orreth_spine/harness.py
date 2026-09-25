# PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P4 sp4, the A/B harness v0 · 2026-09-18
# Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P6 cure sp3 (the re-walk's wounds): the world checks — a duty answered · offers arrive as holds · 2026-09-21
# Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P6.5 sp1, the world check: every service healthy or retired · 2026-09-22
# Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P6.5 sp2, two checks: every MCP server answers initialize · the keeper proposes after strikes, never retires alone · 2026-09-23
# Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P6.5 sp3, model ARMS on a run (the same golden cases against two minds) · three checks: every mind answers · the gateway answers and holds every stall · the meter and the gateway agree · a model change is announced · 2026-09-24
# Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp6, the bodies' seam: the run over the invoke rail (`orreth.resident.harness.v1`) · the verdict factored (fixture bodies-v0) · 2026-09-24
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
# P7 sp6: the run asked of a body over the invoke rail — a kernel with no body of its
# own in its process (the Rust kernel) publishes this on the body's bench; the body runs
# its golden cases through its own graph and records the run under the kernel's run id
HARNESS_CMD = "orreth.resident.harness.v1"
KERNEL = "the kernel"
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
        cur.execute("ALTER TABLE spine_harness_runs ADD COLUMN IF NOT EXISTS arm text")   # P6.5 sp3: the mind this run rode


def golden(template: str) -> list[dict]:
    p = GOLDEN / f"{template}.v0.json"
    return json.loads(p.read_text()) if p.exists() else []


def verdict(cases: list[dict], replies: list[str]) -> dict:
    """The shared law of a run (fixture `harness_verdict`, P7 sp6): a case
    passes when every expected word appears in the reply, case folded; the
    details keep the reply's first 300 characters; the note is the marker's."""
    details, passed = [], 0
    for c, reply in zip(cases, replies):
        reply = reply or ""
        ok = all(str(x).lower() in reply.lower() for x in c.get("expect", []))
        passed += ok
        details.append({"ask": c["ask"], "expect": list(c.get("expect", [])), "reply": reply[:300], "ok": bool(ok)})
    failed = len(cases) - passed
    return {"passed": passed, "failed": failed, "details": details,
            "note": f"harness: {passed} passed, {failed} failed"}


def command_for(run_id: str, target: str, cases: list[dict], *, arm: str | None = None,
                parent_marker: str | None = None, scope: str | None = None) -> dict:
    """The kernel's ask of a body: run these cases through your own graph and
    record the run as `run_id` (the Rust door polls for it). The cases ride
    the command whole — a golden set is the kernel's, not the body's — and
    the payload wears their hash; the chain is the kernel's."""
    sc = scope or ev.scope()
    payload = {"ref": run_id, "hash": ev.content_hash(cases), "target": target, "cases": list(cases)}
    if arm:
        payload["arm"] = arm
    if parent_marker:
        payload["parent_marker"] = parent_marker
    return ev.make_envelope(kind="command", type=HARNESS_CMD, universe_id=sc, scope_path=sc,
                            payload=payload, correlation_id=run_id, authority_chain=[KERNEL])


def run(conn, body, cases: list[dict] | None = None,
        parent_marker: str | None = None, arm: str | None = None,
        run_id: str | None = None) -> dict:
    """Run the golden cases through the body's own graph (its mind on the
    meter, its recall honestly empty of any ask) and record the run.
    P6.5 sp3: `arm` names a stall — the body thinks through THAT mind for
    the run (its template's model set aside for the run, restored after)."""
    from .resident import ensure_schema as _ground   # lazily: no import cycle
    _ground(conn)
    ensure_schema(conn)
    outbox.ensure_schema(conn)
    cases = cases if cases is not None else golden(body.template["name"])
    body._serve_conn = conn
    body._current_ask = None
    details, passed = [], 0
    mind_was = dict(body.template.get("mind") or {})
    if arm:
        from . import services
        s = services.get(conn, arm)
        if s is None or s["kind"] != "mind":
            raise ValueError(f"no mind named {arm!r} stands in the Stable — an arm is a mind by name")
        body.template["mind"] = dict(mind_was, pin=arm)     # the run PINS the arm — nothing outranks a pin
    try:
        return _run(conn, body, cases, parent_marker, arm, run_id)
    finally:
        body.template["mind"] = mind_was


def _run(conn, body, cases, parent_marker, arm, run_id=None):
    replies = []
    for c in cases:
        out = body._graph.invoke({"text": c["ask"], "reply": "", "steps": [],
                                  "notes": [], "hold": None, "read": []})
        replies.append(out.get("reply") or "")
    v = verdict(cases, replies)
    passed, failed, details = v["passed"], v["failed"], v["details"]
    rid = run_id or ("run_" + secrets.token_hex(5))
    version = body.template.get("version", "?")
    from . import markers
    markers.ensure_schema(conn)
    mid = markers.new_id()
    marker = {"kind": "observation", "id": mid, "parent": parent_marker,
              "by": body.identity.did}
    # one transaction: the marker, the run's row and (a failing run) its fact — nested
    # inside a serve's own transaction when the run rides the rail (a savepoint)
    with conn.transaction():
        cur = conn.cursor()
        markers.insert(cur, mid, "observation", parent_marker, rid,
                       body.identity.did, v["note"])
        cur.execute(
            "INSERT INTO spine_harness_runs (run_id, template, version, passed,"
            " failed, details, scope, arm) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
            (rid, body.template["name"], version, passed, failed,
             json.dumps(details), ev.scope(), arm))
        if failed:
            e = ev.make_envelope(
                kind="event", type=HARNESS_FAILED, universe_id=ev.scope(),
                scope_path=ev.scope(),
                payload={"ref": rid, "hash": "sha256:-", "template": body.template["name"],
                         "version": version, "passed": passed, "failed": failed},
                correlation_id=rid, authority_chain=[body.identity.did], marker=marker)
            outbox.add_row(cur, ev.encode(e), e["message_id"])
    return {"run_id": rid, "template": body.template["name"], "version": version,
            "passed": passed, "failed": failed, "details": details}


def run_command(conn, body, env: dict) -> dict:
    """A body serves the kernel's harness command (P7 sp6): the cases from
    the payload, the arm and the parent marker as given, the run recorded
    under the kernel's run id. A run id already on the ground is the same
    run asked twice — nothing is run again (the inbox's footprint is the
    first guard; this is the second)."""
    pl = env.get("payload") or {}
    rid = str(pl.get("ref") or "")
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM spine_harness_runs WHERE run_id = %s", (rid,))
    if cur.fetchone() is not None:
        return {"run_id": rid, "repeated": True}
    return run(conn, body, list(pl.get("cases") or []), parent_marker=pl.get("parent_marker"),
               arm=pl.get("arm"), run_id=rid)


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


def mcp_servers_answer(conn) -> dict:
    """P6.5 sp2: every standing MCP server answered initialize at its LAST
    probe (the keeper's beat and "check the tools" probe; this reads) —
    the silent named, the never-probed named; no server on the shelf
    passes honestly."""
    from . import services
    rows = [r for r in services.listing(conn, kind="mcp") if r["state"] != "retired"]
    silent = [r["name"] for r in rows if r["last_health"] and r["last_health"]["ok"] is False]
    unprobed = [r["name"] for r in rows if not r["last_health"]]
    detail = ("no MCP server on the shelf" if not rows else
              f"{len(rows) - len(silent) - len(unprobed)} of {len(rows)} answered initialize"
              + (f" · silent: {', '.join(silent)}" if silent else "")
              + (f" · never probed: {', '.join(unprobed)}" if unprobed else ""))
    return {"name": "every MCP server answers initialize", "ok": not silent and not unprobed,
            "detail": detail, "silent": silent, "unprobed": unprobed}


def keeper_proposes(conn) -> dict:
    """P6.5 sp2, the strikes rule (rule 11): a service unhealthy across N
    checks in a row has a PROPOSAL at the interlock (or the human has
    heard one since) — and no service was ever retired by a body's own
    hand: every retire fact names a human's ask or a hold."""
    from . import mcp, services
    n = mcp.strikes_n()
    unproposed = []
    for s in services.listing(conn):
        if s["state"] == "retired":
            continue
        if mcp.strikes(conn, s["name"]) >= n:
            unproposed.append(s["name"])            # strikes count since the last proposal: ≥ n = none heard
    cur = conn.cursor()
    cur.execute("SELECT count(*) FROM spine_markers WHERE scope = %s AND kind = 'observation'"
                " AND note LIKE '%% retire: retired%%' AND by_did LIKE 'did:orreth:agent:%%'", (ev.scope(),))
    alone = int(cur.fetchone()[0])                  # a body retiring by its own hand = an observation, not an act under an ask
    detail = (f"strikes rule: {n} in a row" + (f" · unproposed: {', '.join(unproposed)}" if unproposed else " · every strike proposed")
              + (f" · {alone} retired by a body alone" if alone else ""))
    return {"name": "the keeper proposes after strikes, never retires alone", "ok": not unproposed and not alone,
            "detail": detail, "unproposed": unproposed, "alone": alone}


def ab(conn, body, arms: list[str], cases: list[dict] | None = None, parent_marker: str | None = None) -> dict:
    """P6.5 sp3, the A/B harness with model ARMS (0058): the same golden
    cases against each named mind, one run each; the verdict names the
    arm that passed most — a PROPOSAL for the human's cut, never an
    assignment made by the machine."""
    runs = {}
    for a in arms:
        runs[a] = run(conn, body, cases, parent_marker=parent_marker, arm=a)
    best = sorted(runs.items(), key=lambda kv: (-kv[1]["passed"], kv[0]))[0][0] if runs else None
    words = " · ".join(f"{a}: {r['passed']} passed, {r['failed']} failed" for a, r in runs.items())
    return {"template": body.template["name"], "arms": {a: {"run_id": r["run_id"], "passed": r["passed"], "failed": r["failed"]}
                                                       for a, r in runs.items()},
            "best": best, "words": f"{body.template['name']} over {len(arms)} arms — {words}"
                                   + (f"; {best} did best — say \"assign {body.template['name']} to {best}\" to make it so" if best else "")}


def minds_answer(conn) -> dict:
    """P6.5 sp3: every standing mind answered its canary at its LAST check
    (the keeper's beat); the silent named; the never-checked named."""
    from . import services
    rows = [r for r in services.listing(conn, kind="mind") if r["state"] != "retired"]
    silent = [r["name"] for r in rows if r["last_health"] and r["last_health"]["ok"] is False]
    unprobed = [r["name"] for r in rows if not r["last_health"]]
    detail = ("no mind in the Stable" if not rows else
              f"{len(rows) - len(silent) - len(unprobed)} of {len(rows)} answered"
              + (f" · silent: {', '.join(silent)}" if silent else "")
              + (f" · never checked: {', '.join(unprobed)}" if unprobed else ""))
    return {"name": "every mind answers", "ok": not silent and not unprobed, "detail": detail,
            "silent": silent, "unprobed": unprobed}


def gateway_holds(conn, gw=None) -> dict:
    """P6.5 sp3: the gateway answers, and holds a model entry for every
    standing mind (a stall the ladder has that the gateway lacks is named)."""
    from . import services, stable
    gw = gw or stable.Gateway()
    rows = [r for r in services.listing(conn, kind="mind") if r["state"] != "retired"
            and (r.get("manifest") or {}).get("provider")]        # a DEAL: the test lane's fake mind is never in the gateway
    if not gw.ready():
        return {"name": "the gateway answers and holds every mind", "ok": not rows,
                "detail": f"the gateway at {gw.base} is dark" + (f" — {len(rows)} minds cannot think" if rows else ""),
                "missing": [r["name"] for r in rows]}
    try:
        held = set(gw.models().keys())
    except stable.GatewayDark as e:
        return {"name": "the gateway answers and holds every mind", "ok": False, "detail": str(e), "missing": []}
    missing = [r["name"] for r in rows if r["name"] not in held]
    return {"name": "the gateway answers and holds every mind", "ok": not missing,
            "detail": f"the gateway answers · {len(rows) - len(missing)} of {len(rows)} minds held"
                      + (f" · missing: {', '.join(missing)}" if missing else ""),
            "missing": missing}


def meter_agrees(conn, gw=None) -> dict:
    """P6.5 sp3, the 100%: the meter's dollars for this world's bodies
    against the gateway's ledger for their keys — within a tenth of a cent."""
    from . import stable
    r = stable.reconcile(conn, gw if gw is not None else stable.Gateway())
    return {"name": "the meter and the gateway agree", "ok": not r.get("mismatched"), "detail": r["words"],
            "meter_usd": r["meter_usd"], "gateway_usd": r["gateway_usd"], "mismatched": r.get("mismatched", [])}


def changes_announced(conn) -> dict:
    """P6.5 sp3 ("model changed without an announcement"): every meter line
    that rode a mind other than the one asked for carries the why (a
    confessed degrade) — a silent swap is a wound."""
    from .gateway import ensure_schema as _meter
    _meter(conn)
    cur = conn.cursor()
    cur.execute("SELECT to_regclass('spine_meter') IS NOT NULL")
    if not cur.fetchone()[0]:                     # no meter on this ground yet: nothing swapped, nothing silent
        return {"name": "a model change is announced", "ok": True, "detail": "no thought metered yet", "silent": 0}
    cur.execute("SELECT count(*) FROM spine_meter WHERE ok AND stall IS NOT NULL AND note IS NULL"
                " AND model <> stall AND at >= now() - interval '1 day'")
    silent = int(cur.fetchone()[0])
    cur.execute("SELECT count(*) FROM spine_meter WHERE ok AND note IS NOT NULL AND at >= now() - interval '1 day'")
    confessed = int(cur.fetchone()[0])
    return {"name": "a model change is announced", "ok": silent == 0,
            "detail": f"{confessed} confessed swap{'s' if confessed != 1 else ''} today"
                      + (f" · {silent} SILENT" if silent else " · none silent"),
            "silent": silent}


def checks(conn) -> list[dict]:
    """Every world check, read off the ground — the harness door lists
    them; a failed check is a wound named in words."""
    from .resident import ensure_schema as _ground
    _ground(conn)
    from . import monitor, scheduler, services
    scheduler.ensure_schema(conn); monitor.ensure_schema(conn); services.ensure_schema(conn)
    return [duty_answered(conn), offers_are_holds(conn), services_healthy(conn),
            mcp_servers_answer(conn), keeper_proposes(conn),
            minds_answer(conn), gateway_holds(conn), meter_agrees(conn), changes_announced(conn)]
