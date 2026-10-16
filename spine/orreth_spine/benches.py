# PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch Phase 8 THE STUDIO sp8, THE BENCH (canon 0011 §2) · 2026-10-13
"""THE BENCH (canon 0011 §2, JB's lock 2026-10-13).

One effort, one place. A bench is a named effort under a person's seat — the agent's name is
the bench's name — and it holds the agent's whole story in ONE ROW of the ground: the step of
its making (NAME · GRAPH · GOLDEN · SAVE · CUT · CARD · PROMOTE · JOINED — the wizard's place,
which until this spoonful lived in the page and then in one browser, W134), the wizard's own
state as `body`, the ask it holds at the interlock (`hold`), and by name everything else:
its drafts (`spine_drafts.bench`), its experiments (`spine_experiments.agent` since the bench
opened), its seat (`spine_body_seats`). The glass reads the bench through one door and
re-reads it on a clock (W133's law: a wait on the feed alone is a wait for ever).

The doors are ROUTINE (L1) like a draft's save and discard: opening a bench, moving its step,
keeping its state. CLOSING a bench lets the effort go — its drafts discarded, its open
experiment declined through the experiments' own word — routine too, as discard and decline
are today; what reached the shelf stays (a version is never deleted). Opening and closing
are facts on the feed; a step moved is not (the glass reads the row).

THE WORD. "bench" already names the dispatcher's waiting bench for asks (`dispatch.py`, the
BENCH SWEEP beat, W91). That bench is the kernel's; this one is the Workshop's and lives in
its own table. The two never meet in code; the canon names both.
"""
from __future__ import annotations

import json
import re
import secrets

from . import envelope as ev, outbox

KERNEL = "the kernel"
BENCH_OPENED = "orreth.bench.opened.v1"
BENCH_CLOSED = "orreth.bench.closed.v1"
STEPS = ("name", "graph", "golden", "save", "cut", "card", "promote", "joined")
WORK_TOOL = "bench.work"                                   # THE STUDIO sp10 ONE WORD TO WORK (canon 0011 §5): the kernel's own held act — the chain
WORK_LEVEL = "L2"
WORK_CLASS = "consequential"
WORK_ORDER = ("graph", "golden", "template")               # the cuts, in order; the agent's own cut opens the Experiment
STATES = ("open", "closed")
NAME_RX = re.compile(r"^[a-z0-9][a-z0-9_-]{0,63}$")     # an agent's name — no dots (a craft's name may carry one; a bench is the agent)

DDL = (
    "CREATE TABLE IF NOT EXISTS spine_benches ("
    " bench_id text PRIMARY KEY, scope text NOT NULL, person text NOT NULL, name text NOT NULL, words text,"
    " step text NOT NULL DEFAULT 'name', body text NOT NULL DEFAULT '{}', hold text,"
    " state text NOT NULL DEFAULT 'open', at timestamptz NOT NULL DEFAULT now(),"
    " updated_at timestamptz NOT NULL DEFAULT now(), closed_at timestamptz)",
    "CREATE INDEX IF NOT EXISTS spine_benches_person ON spine_benches (scope, person, state, updated_at DESC)",
    "ALTER TABLE spine_drafts ADD COLUMN IF NOT EXISTS bench text",       # a draft files ON a bench, or loose (NULL)
)


class BenchRefused(RuntimeError):
    """Refused in plain words — the bench does not stand, the name is not a name, the step is not a step."""


def ensure_schema(conn) -> None:
    from . import crafts
    crafts.ensure_schema(conn)                  # the drafts table stands before its column is added
    if not outbox.once(conn, "benches"):
        return
    with conn.transaction():
        cur = conn.cursor()
        cur.execute("SELECT pg_advisory_xact_lock(742199)")
        for stmt in DDL:
            cur.execute(stmt)


def step_ok(step: str) -> bool:
    return step in STEPS


def name_ok(name: str) -> bool:
    return bool(NAME_RX.match(str(name or "")))


def _fact(cur, type_: str, ref: str, payload: dict, by: list[str]) -> None:
    e = ev.make_envelope(kind="event", type=type_, universe_id=ev.universe(), scope_path=ev.universe(),
                         payload={"ref": ref, "hash": ev.content_hash(payload), **payload},
                         correlation_id=ref, authority_chain=by)
    outbox.add_row(cur, ev.encode(e), e["message_id"])


_COLS = "bench_id, person, name, words, step, body, hold, state, at, updated_at, closed_at"


def _row(r) -> dict:
    return {"bench_id": r[0], "person": r[1], "name": r[2], "words": r[3], "step": r[4],
            "body": json.loads(r[5] or "{}"), "hold": r[6], "state": r[7],
            "at": r[8].isoformat(), "updated_at": r[9].isoformat(), "closed_at": r[10].isoformat() if r[10] else None}


def get(conn, person: str, name: str) -> dict | None:
    """The OPEN bench of this name under the person; a closed one if no open one stands (the newest)."""
    ensure_schema(conn)
    cur = conn.cursor()
    cur.execute(f"SELECT {_COLS} FROM spine_benches WHERE scope = %s AND person = %s AND name = %s"
                " ORDER BY (state = 'open') DESC, updated_at DESC LIMIT 1", (ev.universe(), person, name))
    r = cur.fetchone()
    return _row(r) if r else None


def listing(conn, person: str, *, state: str | None = None) -> list[dict]:
    """This person's benches, the open ones first, newest first — and ONLY this person's (AG-9)."""
    ensure_schema(conn)
    cur = conn.cursor()
    cur.execute(f"SELECT {_COLS} FROM spine_benches WHERE scope = %s AND person = %s"
                + (" AND state = %s" if state else "") + " ORDER BY (state = 'open') DESC, updated_at DESC LIMIT 200",
                (ev.universe(), person) + ((state,) if state else ()))
    return [_row(r) for r in cur.fetchall()]


def open_bench(conn, person: str, name: str, *, words: str | None = None) -> dict:
    """Routine (L1): a bench opens under the person — or the open one of that name is handed back
    (one open bench per name per person: an effort is one place). A fact on the feed."""
    n = str(name or "").strip().lower()
    if not name_ok(n):
        raise BenchRefused("a bench is named for its agent: a short lowercase name — letters, digits, dashes, underscores")
    ensure_schema(conn)
    have = get(conn, person, n)
    if have and have["state"] == "open":
        return have
    bid = "bench_" + secrets.token_hex(6)
    with conn.transaction():
        cur = conn.cursor()
        cur.execute("INSERT INTO spine_benches (bench_id, scope, person, name, words) VALUES (%s, %s, %s, %s, %s)",
                    (bid, ev.universe(), person, n, words))
        _fact(cur, BENCH_OPENED, bid, {"name": n, "person": person, "words": words or ""}, [person, KERNEL])
    return get(conn, person, n)


def move(conn, person: str, name: str, *, step: str | None = None, body: dict | None = None,
         hold: str | None = None, words: str | None = None) -> dict:
    """Routine (L1): the bench keeps its place — the step, the wizard's state, the ask it holds.
    `hold=""` clears the hold. No fact: the glass reads the row."""
    b = get(conn, person, name)
    if b is None or b["state"] != "open":
        raise BenchRefused(f"no open bench named {name!r} under your seat")
    sets, args = [], []
    if step is not None:
        if not step_ok(step):
            raise BenchRefused(f"a bench's step is one of {', '.join(STEPS)}, not {step!r}")
        sets.append("step = %s"); args.append(step)
    if body is not None:
        if not isinstance(body, dict):
            raise BenchRefused("a bench's body is an object — the wizard's state as it stands")
        sets.append("body = %s"); args.append(json.dumps(body))
    if hold is not None:
        sets.append("hold = %s"); args.append(hold or None)
    if words is not None:
        sets.append("words = %s"); args.append(words or None)
    if not sets:
        return b
    with conn.transaction():
        cur = conn.cursor()
        cur.execute("UPDATE spine_benches SET " + ", ".join(sets) + ", updated_at = clock_timestamp() WHERE bench_id = %s",
                    (*args, b["bench_id"]))
    return get(conn, person, name)


def whole(conn, person: str, bench: dict) -> dict:
    """The bench with everything that stands under its name: its drafts, its experiments since it
    opened, its seat on the shelf (where the agent's life stands, if promoted)."""
    from . import crafts, experiments
    cur = conn.cursor()
    cur.execute(f"SELECT {crafts._DRAFT_COLS} FROM spine_drafts WHERE scope = %s AND person = %s AND bench = %s"
                " ORDER BY updated_at DESC", (ev.universe(), person, bench["name"]))
    drafts = [crafts._draft_row(r) for r in cur.fetchall()]
    xs = [x for x in experiments.listing(conn, agent=bench["name"]) if x["opened_at"] >= bench["at"]]
    seat = experiments.seat_of(conn, bench["name"])
    return dict(bench, drafts=drafts,
                experiments=[{k: x.get(k) for k in ("experiment_id", "state", "leaning", "room", "opened_at", "proposed_at", "settled_at")} for x in xs],
                seat=seat)


def close(conn, person: str, name: str, *, reason: str | None = None) -> dict:
    """Routine (L1), like discard and decline: the effort is let go — its drafts discarded, its open
    experiment declined (the experiments' own word), the bench closed. What reached the shelf
    stays. A fact on the feed."""
    from . import experiments, proof
    b = get(conn, person, name)
    if b is None or b["state"] != "open":
        raise BenchRefused(f"no open bench named {name!r} under your seat")
    w = whole(conn, person, b)
    open_x = [x for x in w["experiments"] if x["state"] in ("running", "proposed")]
    if open_x and not proof.governs(conn, person):      # declining is a governing seat's act at the experiments door — the same here
        raise BenchRefused(f"the {name} bench holds an open experiment — declining it is a governing seat's act; yours reads and writes")
    declined = []
    for x in w["experiments"]:
        if x["state"] in ("running", "proposed"):
            experiments.decline(conn, person, x["experiment_id"], reason=reason or f"the {name} bench was let go")
            declined.append(x["experiment_id"])
    with conn.transaction():
        cur = conn.cursor()
        cur.execute("DELETE FROM spine_drafts WHERE scope = %s AND person = %s AND bench = %s", (ev.universe(), person, name))
        discarded = cur.rowcount
        cur.execute("UPDATE spine_benches SET state = 'closed', hold = NULL, closed_at = clock_timestamp(),"
                    " updated_at = clock_timestamp() WHERE bench_id = %s", (b["bench_id"],))
        _fact(cur, BENCH_CLOSED, b["bench_id"],
              {"name": name, "person": person, "discarded": discarded, "declined": declined, "reason": reason or ""},
              [person, KERNEL])
    return {"bench": get(conn, person, name), "discarded": discarded, "declined": declined,
            "words": f"the {name} bench is let go — {discarded} draft{'' if discarded == 1 else 's'} discarded"
                     + (f", {len(declined)} experiment{'' if len(declined) == 1 else 's'} declined" if declined else "")
                     + "; what reached the shelf stays"}


# ---- THE STUDIO sp10 — ONE WORD TO WORK (canon 0011 §5, JB's lock 2026-10-13: ONE Yes for the chain; built on his word 2026-10-14) ----
# "put <name> to work" is one consequential act held at L2: the kernel cuts what changed on the bench in order
# (graph · golden · template), skips what stands with the same bytes (W124's law, said as a line not a wall),
# opens the Experiment on the agent's cut, and the card lands on the bench. The card names every cut it will
# make BEFORE the hold; each cut inside the chain is still its own recorded fact on the shelf.

def _plain_of(name: str, kind: str) -> str:
    return {"graph": f"the graph {name}.v0", "golden": f"the golden set {name}", "template": f"the agent {name}"}[kind]


def plan_work(name: str, graph, golden, template) -> dict:
    """The pure law of the chain (fixture `bench_work_plan`). Each of graph · golden · template is
    None (nothing of that kind under the bench or on the shelf) or {draft: bool, same: bool, version:
    int|None} — whether a draft lies on the bench, whether its bytes equal the shelf's, and the
    shelf's standing version. Returns {ok, cuts, lines, reason, text}: the cuts in order, a line per
    craft for the card, the one reason when the chain refuses, and the held act's words."""
    lines, cuts, reason = [], [], None
    for kind in WORK_ORDER:
        c = {"graph": graph, "golden": golden, "template": template}[kind]
        c = c if isinstance(c, dict) else {}
        has, same, ver = bool(c.get("draft")), bool(c.get("same")), c.get("version")
        what = _plain_of(name, kind)
        if kind == "template":
            if not has:
                reason = reason or f"no template draft for {name} - SAVE first"
                lines.append(f"{what}: no draft")
            elif same:
                reason = reason or (f"the {name} template stands unchanged (version {ver}) - an experiment needs a change to judge: "
                                    f"change what {name} is for, or its graph, then put it to work again")
                lines.append(f"{what} stands unchanged (version {ver})")
            else:
                cuts.append(kind); lines.append(f"{what} as version {(ver or 0) + 1} -> the experiment")
            continue
        if has and not same:
            cuts.append(kind); lines.append(f"{what} as version {(ver or 0) + 1}")
        elif has and same:
            lines.append(f"{what} stands (version {ver}) - unchanged, skipped")
        elif ver:
            lines.append(f"{what} stands (version {ver})")
        else:
            need = "SAVE the graph first" if kind == "graph" else "every engineered agent is born with one; SAVE its cases first"
            reason = reason or f"no {what[4:]} - {need}"
            lines.append(f"{what}: none")
    ok = reason is None and "template" in cuts
    return {"ok": ok, "cuts": cuts, "lines": lines, "reason": reason,
            "text": f"putting {name} to work - " + " · ".join(lines) if ok else ""}


def work_check(conn, person: str, name: str) -> dict:
    """What "put <name> to work" would do, read off the bench and the shelf — or why it refuses, in
    words. The drafts of the chain are validated here (a draft that does not read whole refuses
    before the hold, as a cut would)."""
    from . import crafts, services
    b = get(conn, person, name)
    if b is None or b["state"] != "open":
        raise BenchRefused(f"no open bench named {name!r} under your seat")
    w = whole(conn, person, b)
    open_x = [x for x in w["experiments"] if x["state"] in ("running", "proposed")]
    if open_x:
        raise BenchRefused(f"an experiment on {name} is already {open_x[0]['state']} ({open_x[0]['experiment_id']}) — "
                           f"its card is the next step; decline it to start over")
    by_kind = {}
    for d in w["drafts"]:
        by_kind.setdefault(d["kind"], d)            # newest first
    ins, drafts = {}, {}
    for kind in WORK_ORDER:
        cname = name + ".v0" if kind == "graph" else name
        row = services.get(conn, crafts.craft_name(cname, kind))
        d = by_kind.get(kind)
        if d is not None and d["name"] != cname:
            raise BenchRefused(f"the {kind} draft on the {name} bench is named {d['name']!r} — a bench's crafts wear the agent's name ({cname})")
        if row is not None and row["kind"] != kind:
            raise BenchRefused(f"{row['name']} is on the shelf as a {row['kind']} — a name wears one kind")
        if row is not None and row["state"] == "retired":
            raise BenchRefused(f"{row['name']} is retired — restore it first, then put {name} to work")
        if d is not None:
            v = crafts.validate(kind, d["body"])
            if not v["ok"]:
                raise BenchRefused(f"the {_plain_of(name, kind)} draft does not read whole yet: {v['reason']}")
            drafts[kind] = d
        ins[kind] = {"draft": d is not None, "same": bool(d and row and row["manifest_hash"] == services.pin(d["body"])),
                     "version": int(row["version"]) if row else None}
    plan = plan_work(name, ins["graph"], ins["golden"], ins["template"])
    if not plan["ok"]:
        raise BenchRefused(plan["reason"] or "nothing to put to work")
    t = drafts["template"]["body"]
    if not isinstance(t, dict) or t.get("kind") != "agent" or t.get("name") != name:
        raise BenchRefused(f"the {name} template is not an agent of that name — the wizard writes it so; fix the draft")
    if t.get("graph") != name + ".v0":
        raise BenchRefused(f"the {name} template names graph {t.get('graph')!r} — a bench's agent wears its own graph, {name}.v0")
    return {"bench": b, "plan": plan, "drafts": {k: d["draft_id"] for k, d in drafts.items()}}


def hold_work(conn, person: str, name: str, *, session: str | None = None) -> dict:
    """ONE hold for the chain (L2): the card's lines are the held act's words; the bench keeps the
    ask it holds at the step CUT."""
    from .proof import hold_kernel_act
    c = work_check(conn, person, name)
    held = hold_kernel_act(conn, text=c["plan"]["text"], person=person, tool=WORK_TOOL,
                           args={"bench": name, "person": person}, level=WORK_LEVEL, session=session, cls=WORK_CLASS)
    move(conn, person, name, step="cut", hold=held)
    return {"held": held, "level": WORK_LEVEL, "class": WORK_CLASS, "lines": c["plan"]["lines"], "cuts": c["plan"]["cuts"]}


def work_in(conn, args: dict, by: str, ask: str | None = None, marker: str | None = None) -> str:
    """The settled chain, in the settle's transaction: the cuts in order — each its own fact on
    the shelf (`crafts.cut`) — then the Experiment opened on the agent's own (`experiments.open_in`);
    the bench moves to THE CARD with its hold cleared. The words name every landing."""
    from . import crafts, experiments
    person, name = str(args.get("person") or by), str(args.get("bench") or "")
    c = work_check(conn, person, name)
    said = []
    for kind in c["plan"]["cuts"]:
        if kind == "template":
            said.append(experiments.open_in(conn, {"draft_id": c["drafts"][kind], "person": person}, by, ask, marker))
        else:
            made = crafts.cut(conn, person, c["drafts"][kind], by=by, ask=ask, parent_marker=marker, confirmed_by=by)
            said.append(f"the {made['name']} is on the shelf as version {made['version']}")
    skipped = [l for l in c["plan"]["lines"] if "stands" in l]
    cur = conn.cursor()
    cur.execute("UPDATE spine_benches SET step = 'card', hold = NULL, updated_at = clock_timestamp() WHERE bench_id = %s", (c["bench"]["bench_id"],))
    return f"{name} is put to work — " + "; ".join(said) + (" (" + "; ".join(skipped) + ")" if skipped else "")

