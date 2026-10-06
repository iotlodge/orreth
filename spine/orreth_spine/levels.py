# PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch Phase 8 THE WORKSHOP sp1, THE PATH: universe · floor · room on one ScopePath · 2026-10-05
"""THE PATH (canon 0010 lock 2 · 0000's recursion contract carried back): one
kernel per cell serves three levels — the UNIVERSE (the cell itself), its
FLOORS and their ROOMS — on one ScopePath (`u:dev/f:ops/r:bob`). The `scope`
column every table carries IS the path: a row written at the universe wears
`u:dev` as it always did; a row written by or for a body seated on a floor
wears the floor's path. Governance tightens DOWN the path (mode: dev → prod,
never back); a listing at a level sees everything within it (the roll-up UP,
at its minimum: counts folded by the 0005 monoid); a body's shared reads
(the shelf, the Stable, the policy) resolve to its universe (recall escalates
UP — the floor's own shelf is a later spoonful).

The pure laws (both kernels, fixture `levels-v0.json`): the path grammar ·
the child law · the words · mode tighten-only · the experiment room · the
cascade fold (0007's resolver at its minimum: soft most-specific-wins and
attributed, skills additive with the higher version winning, floors sorted
by content hash, the resolved context CONTENT-ADDRESSED) · the roll-up
monoid (0005's StatBundle: merge associative with an identity, outcomes and
costs summed component-wise, a floor breach anywhere a breach of the whole,
the Beta prior applied ONCE at report) · the level fact.

The ground (schema 5): `spine_levels` — one row per level of this universe,
the universe's own row seeded at light with the cell's declared mode
(`SPINE_MODE`, default dev); a floor or room opened by the crew manifest at
light, or by a person through `POST /levels/open` — a governed act, held at
L2 (a level stands forever once opened; nothing here is deleted).
"""
from __future__ import annotations

import json
import math
import os
import re
from pathlib import Path

from . import envelope as ev

LETTERS = {"u": "universe", "f": "floor", "r": "room"}      # the three levels, in the order they nest
ORDER = ("u", "f", "r")
LEVELS = ("universe", "floor", "room")
NAME_RX = re.compile(r"^[a-z0-9_-]{1,48}$")
MODES = ("dev", "prod")                                      # dev < prod: mode only tightens
MODE_DIAL = "SPINE_MODE"                                     # the universe's mode, declared when its cell opens
MODE_DEFAULT = "dev"
LEVEL_OPENED = "orreth.level.opened.v1"                      # a level opened — at light, by the manifest, or on a person's word
OPEN_TOOL = "level.open"                                     # the kernel's own held act
OPEN_CLASS = "consequential"
OPEN_LEVEL = "L2"
KERNEL = "the kernel"
BY_MANIFEST = "the crew manifest"
GRAMMAR = "a scope path reads u:<universe>, u:<universe>/f:<floor>, or u:<universe>/f:<floor>/r:<room>"
_OUTCOMES = ("success", "failure", "partial", "aborted")
_COSTS = ("tokens", "model_calls", "usd", "wall_ms")


# ---- the path grammar -------------------------------------------------------------------------

def parse(path: str) -> list[tuple[str, str]]:
    """The path's levels, root to leaf — `[("u", "dev"), ("f", "ops"), ("r", "bob")]`; a
    path that does not read as the grammar refuses in words."""
    parts = str(path or "").split("/")
    if not parts or len(parts) > 3:
        raise ValueError(f"{GRAMMAR} — got {path!r}")
    out = []
    for i, part in enumerate(parts):
        letter, _, name = part.partition(":")
        if letter != ORDER[i] or not NAME_RX.match(name):
            raise ValueError(f"{GRAMMAR} — got {path!r}")
        out.append((letter, name))
    return out


def ok(path: str) -> bool:
    try:
        parse(path)
        return True
    except ValueError:
        return False


def level_of(path: str) -> str:
    """universe · floor · room."""
    return LETTERS[parse(path)[-1][0]]


def name_of(path: str) -> str:
    return parse(path)[-1][1]


def universe_of(path: str) -> str:
    """The universe a path stands in — its first segment (`u:dev` for `u:dev/f:ops/r:bob`)."""
    return "u:" + parse(path)[0][1]


def parent_of(path: str) -> str | None:
    """The level above (None at the universe)."""
    levels = parse(path)
    if len(levels) == 1:
        return None
    return "/".join(f"{k}:{v}" for k, v in levels[:-1])


def ancestors(path: str) -> list[str]:
    """Root to leaf, the path itself last — the tiers the cascade folds and the
    scopes a body's recall escalates through."""
    levels = parse(path)
    return ["/".join(f"{k}:{v}" for k, v in levels[:i + 1]) for i in range(len(levels))]


def within(path: str, ancestor: str) -> bool:
    """A path is within an ancestor when it is the ancestor or stands below it (the seat's law)."""
    return path == ancestor or path.startswith(ancestor + "/")


def child(parent: str, level: str, name: str) -> str:
    """The path a new level would have — the child law: a floor opens under a universe, a
    room on a floor, a universe only as a cell."""
    if level not in LEVELS:
        raise ValueError(f"a level is one of floor or room (a universe opens as a cell) — got {level!r}")
    if level == "universe":
        raise ValueError("a universe opens as a cell, never under another scope")
    if not NAME_RX.match(str(name or "")):
        raise ValueError("a level's name is lower-case letters, digits, - and _ (1 to 48)")
    up = level_of(parent)
    if level == "floor" and up != "universe":
        raise ValueError(f"a floor opens under a universe — {parent} is a {up}")
    if level == "room" and up != "floor":
        raise ValueError(f"a room opens on a floor — {parent} is a {up}")
    return f"{parent}/{'f' if level == 'floor' else 'r'}:{name}"


def words(path: str) -> str:
    """The path in the human's words: `universe dev` · `floor ops of universe dev` · `room
    bob on floor ops of universe dev`."""
    levels = parse(path)
    if len(levels) == 1:
        return f"universe {levels[0][1]}"
    if len(levels) == 2:
        return f"floor {levels[1][1]} of universe {levels[0][1]}"
    return f"room {levels[2][1]} on floor {levels[1][1]} of universe {levels[0][1]}"


# ---- mode: tighten-only ----------------------------------------------------------------------

def mode_of_dial(value: str | None) -> str:
    """The universe's declared mode from its dial: unset or empty → dev; anything but dev or
    prod refuses in words."""
    v = (value or "").strip().lower()
    if not v:
        return MODE_DEFAULT
    if v not in MODES:
        raise ValueError(f"a universe's mode is dev or prod — {MODE_DIAL} says {value!r}")
    return v


def tighten(parent_mode: str, asked: str | None) -> str:
    """The mode a level opens with: unasked → its parent's; asked the same or tighter (dev →
    prod) → as asked; asked looser (prod → dev) → refused — mode only tightens down the path."""
    if parent_mode not in MODES:
        raise ValueError(f"a mode is dev or prod — got {parent_mode!r}")
    if asked is None or str(asked).strip() == "":
        return parent_mode
    a = str(asked).strip().lower()
    if a not in MODES:
        raise ValueError(f"a mode is dev or prod — got {asked!r}")
    if MODES.index(a) < MODES.index(parent_mode):
        raise ValueError(f"mode only tightens down the path — under a {parent_mode} level every floor and room is "
                         f"{parent_mode}; {a} is looser")
    return a


def experiment_ok(level: str, experiment: bool) -> None:
    """Only a room opens as an experiment room (0010 lock 4) — the partition of human
    experiments from production, structurally."""
    if experiment and level != "room":
        raise ValueError("only a room opens as an experiment room")


# ---- the cascade fold (0007 at its minimum) ------------------------------------------------------

def _ver_key(v: str) -> list[int]:
    out = []
    for x in str(v).split("-")[0].split("."):
        try:
            out.append(int(x))
        except ValueError:
            out.append(0)
    return out


def cascade(tiers: list[dict]) -> dict:
    """The fold, root → leaf: later tiers are more specific. `soft` most-specific-wins and
    ATTRIBUTED (`from_scope` says which tier won); `skills` additive, the same name → the
    higher version; `floors` the union sorted by content hash; `mode` the tightest; `as_of`
    every tier's scope · version · mode in order. The id is the content hash of the resolved
    content — same chain, same id, regardless of declaration order."""
    if not tiers:
        raise ValueError("a cascade folds at least one tier")
    soft: dict[str, dict] = {}
    skills: dict[str, str] = {}
    floors: list = []
    mode = "dev"
    as_of = []
    for t in tiers:
        scope = str(t["scope"])
        for key, std in (t.get("soft") or {}).items():
            soft[key] = {"value": std["value"], "from_scope": scope,
                         **({"version": std["version"]} if "version" in std else {})}
        for name, ver in (t.get("skills") or {}).items():
            skills[name] = max(skills.get(name, "0.0.0"), str(ver), key=_ver_key)
        for fl in (t.get("floors") or []):
            if fl not in floors:
                floors.append(fl)
        m = str(t.get("mode") or "dev")
        if m in MODES and MODES.index(m) > MODES.index(mode):
            mode = m
        as_of.append({"scope": scope, "version": str(t.get("version") or "0"), "mode": m})
    floors = sorted(floors, key=ev.content_hash)
    content = {"scope": str(tiers[-1]["scope"]), "mode": mode, "floors": floors, "soft": soft,
               "skills": dict(sorted(skills.items())), "as_of": as_of}
    return {"id": ev.content_hash(content), **content}


# ---- the roll-up monoid (0005 §2–4 at its minimum) ------------------------------------------------

def empty_bundle() -> dict:
    return {"n": 0, "outcomes": {o: 0 for o in _OUTCOMES}, "per_objective": [],
            "cost": {k: 0 for k in _COSTS}, "compliance": "clean"}


def bundle_of(run: dict) -> dict:
    """Lift one run into the monoid."""
    b = empty_bundle()
    b["n"] = 1
    b["outcomes"][run["outcome"]] = 1
    for s in run.get("scores") or []:
        breached = 1 if s.get("floor_breached") else 0
        b["per_objective"].append({
            "objective": s["objective"], "n": 1, "sum": s["score"],
            "sum_sq": s["score"] ** 2, "min": s["score"], "max": s["score"],
            "floor_breaches": breached})
        if breached:
            b["compliance"] = "breached"
    for k, v in (run.get("cost") or {}).items():
        b["cost"][k] = v
    return b


def merge(a: dict, b: dict) -> dict:
    """Component-wise, associative, the empty bundle its identity; a breach anywhere is a
    breach of the whole (never averaged away)."""
    out = empty_bundle()
    out["n"] = a["n"] + b["n"]
    out["outcomes"] = {o: a["outcomes"].get(o, 0) + b["outcomes"].get(o, 0) for o in _OUTCOMES}
    stats = {s["objective"]: dict(s) for s in a["per_objective"]}
    for s in b["per_objective"]:
        if s["objective"] in stats:
            t = stats[s["objective"]]
            t["n"] += s["n"]; t["sum"] += s["sum"]; t["sum_sq"] += s["sum_sq"]
            t["min"] = min(t["min"], s["min"]); t["max"] = max(t["max"], s["max"])
            t["floor_breaches"] += s["floor_breaches"]
        else:
            stats[s["objective"]] = dict(s)
    out["per_objective"] = sorted(stats.values(), key=lambda s: s["objective"])
    out["cost"] = {k: a["cost"].get(k, 0) + b["cost"].get(k, 0) for k in _COSTS}
    out["compliance"] = "breached" if (a["compliance"] == "breached" or b["compliance"] == "breached") else "clean"
    return out


def report(bundle: dict, objective: str, prior: tuple[float, float] = (1.0, 1.0)) -> dict:
    """The read edge: the Beta posterior's mean, 95 % interval and n — the prior enters here
    and only here (merging posteriors would count it twice)."""
    stat = next((s for s in bundle["per_objective"] if s["objective"] == objective), None)
    if stat is None or stat["n"] == 0:
        a0, b0 = prior
        n = 0
    else:
        a0 = prior[0] + stat["sum"]
        b0 = prior[1] + (stat["n"] - stat["sum"])
        n = stat["n"]
    mean = a0 / (a0 + b0)
    var = (a0 * b0) / ((a0 + b0) ** 2 * (a0 + b0 + 1))
    half = 1.96 * math.sqrt(var)
    return {"mean": mean, "ci95": [max(0.0, mean - half), min(1.0, mean + half)],
            "n": n, "compliance": bundle["compliance"],
            "floor_breaches": stat["floor_breaches"] if stat else 0}


def tier_score(bundle: dict, objectives: list[dict], prior: tuple[float, float] = (1.0, 1.0)) -> dict:
    """The weighted mean over NON-floor objectives (weights renormalized); floors never enter
    the average — they gate compliance (flag, never average away)."""
    soft = [o for o in objectives if not o.get("floor")]
    total_w = sum(o["weight"] for o in soft) or 1.0
    score = sum(o["weight"] / total_w * report(bundle, o["objective"], prior)["mean"] for o in soft)
    return {"score": score, "compliance": bundle["compliance"]}


# ---- the fact ---------------------------------------------------------------------------------

def opened_payload(path: str, mode: str, experiment: bool, by: str, reason: str) -> dict:
    """The level fact's payload: the path as the pointer, its shape hashed, the level and
    name read from the path, its parent, its mode, whether it is an experiment room, whose
    word opened it and why."""
    shape = {"level": level_of(path), "name": name_of(path), "parent": parent_of(path), "mode": mode,
             "experiment": bool(experiment)}
    return {"ref": path, "hash": ev.content_hash(shape), **shape, "by": by, "reason": reason}


def opened_fact(path: str, mode: str, experiment: bool, by: str, reason: str) -> dict:
    """`orreth.level.opened.v1` — the universe as universe_id, the level's own path as
    scope_path, the path as correlation; the chain is the opener's (a person, then the
    kernel) or the kernel's alone."""
    chain = [by, KERNEL] if by not in (KERNEL, BY_MANIFEST) else [KERNEL]
    return ev.make_envelope(kind="event", type=LEVEL_OPENED, universe_id=universe_of(path), scope_path=path,
                            payload=opened_payload(path, mode, experiment, by, reason),
                            correlation_id=path, authority_chain=chain)


def opened_words(path: str, mode: str, experiment: bool) -> str:
    """The act's plain words: what stands now."""
    tail = " — an experiment room: nothing promotes out of it except through the Experiment gate" if experiment else ""
    return f"{words(path)} is open ({mode}){tail}"


# ---- the manifest's levels ----------------------------------------------------------------------

def manifest_levels(manifest: dict) -> list[dict]:
    """The levels a crew manifest declares — `{"at": "f:ops", "mode"?: , "experiment"?: ,
    "declares"?: }` each, `at` RELATIVE to the universe (`f:ops` · `f:ops/r:bob`), in
    order; a seat's `at` names one of them (or the universe when absent)."""
    out = []
    for lv in manifest.get("levels") or []:
        at = str(lv.get("at") or "").strip()
        if not at:
            raise ValueError("a declared level names where it stands (`at`: f:<floor> or f:<floor>/r:<room>)")
        out.append({"at": at, "mode": (str(lv["mode"]).strip() if lv.get("mode") else None),
                    "experiment": bool(lv.get("experiment")), "declares": lv.get("declares") or None,
                    "words": str(lv.get("words") or "")})
    return out


def absolute(universe: str, at: str | None) -> str:
    """A manifest's relative `at` under this universe (`f:ops` → `u:dev/f:ops`); absent or
    empty → the universe itself; a full path is taken as it is when it stands within."""
    a = str(at or "").strip()
    if not a:
        return universe
    if a.startswith("u:"):
        if not within(a, universe):
            raise ValueError(f"{a} does not stand in {universe}")
        parse(a)
        return a
    path = f"{universe}/{a}"
    parse(path)
    return path


# ---- the ground ---------------------------------------------------------------------------------

DDL = (
    "CREATE TABLE IF NOT EXISTS spine_levels ("
    " path text PRIMARY KEY, scope text NOT NULL, level text NOT NULL, name text NOT NULL, parent text,"
    " mode text NOT NULL, experiment boolean NOT NULL DEFAULT false, declares text,"
    " opened_by text NOT NULL, opened_at timestamptz NOT NULL DEFAULT now(), ask text, marker text)",
    "CREATE INDEX IF NOT EXISTS spine_levels_scope ON spine_levels (scope, parent)",
)


def ensure_schema(conn) -> None:
    from .outbox import once
    if not once(conn, "levels"):
        return
    with conn.transaction():
        cur = conn.cursor()
        cur.execute("SELECT pg_advisory_xact_lock(742199)")  # DDL race guard
        for ddl in DDL:
            cur.execute(ddl)


class LevelRefused(ValueError):
    """A level could not open — the reason in words."""


def row(conn, path: str) -> dict | None:
    cur = conn.cursor()
    cur.execute("SELECT path, scope, level, name, parent, mode, experiment, declares, opened_by, opened_at, ask"
                " FROM spine_levels WHERE path = %s", (path,))
    r = cur.fetchone()
    return _view(r) if r else None


def _view(r) -> dict:
    return {"path": r[0], "scope": r[1], "level": r[2], "name": r[3], "parent": r[4], "mode": r[5],
            "experiment": bool(r[6]), "declares": json.loads(r[7]) if r[7] else None, "opened_by": r[8],
            "opened_at": r[9].isoformat() if r[9] else None, "ask": r[10], "words": words(r[0])}


def _insert(cur, path: str, mode: str, experiment: bool, declares, by: str, reason: str,
            ask: str | None = None, marker: str | None = None) -> dict:
    from . import outbox
    e = opened_fact(path, mode, experiment, by, reason)
    cur.execute(
        "INSERT INTO spine_levels (path, scope, level, name, parent, mode, experiment, declares, opened_by, ask, marker)"
        " VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT (path) DO NOTHING",
        (path, universe_of(path), level_of(path), name_of(path), parent_of(path), mode, bool(experiment),
         json.dumps(declares) if declares else None, by, ask, marker))
    outbox.add_row(cur, ev.encode(e), e["message_id"])
    return e


def ensure_universe(conn, universe: str, dial: str | None = None) -> dict:
    """The universe's own row, settled at light: absent → opened with the cell's declared
    mode (`SPINE_MODE`, default dev) and said as a fact; present → the dial may TIGHTEN it
    (dev → prod, recorded) and never loosen it (a prod universe refuses to light as dev)."""
    from . import outbox
    ensure_schema(conn); outbox.ensure_schema(conn)
    parse(universe)
    if level_of(universe) != "universe":
        raise LevelRefused(f"a kernel stands at a universe — SPINE_SCOPE says {universe}")
    try:
        mode = mode_of_dial(dial if dial is not None else os.environ.get(MODE_DIAL))
    except ValueError as e:
        raise LevelRefused(str(e)) from None
    r = row(conn, universe)
    if r is None:
        with conn.transaction():
            _insert(conn.cursor(), universe, mode, False, None, KERNEL, "opened at light")
        return row(conn, universe)
    if r["mode"] != mode:
        try:
            tighten(r["mode"], mode)
        except ValueError as e:
            raise LevelRefused(f"{universe} is a {r['mode']} universe and {MODE_DIAL} asks {mode}: {e}") from None
        with conn.transaction():
            cur = conn.cursor()
            cur.execute("UPDATE spine_levels SET mode = %s WHERE path = %s", (mode, universe))
            e = opened_fact(universe, mode, False, KERNEL, "tightened at light")
            outbox.add_row(cur, ev.encode(e), e["message_id"])
            # W98 (SPEC-PATH-01, JB's relight 2026-10-05): a level looser than its parent is unlawful —
            # every floor and room within the universe tightens WITH it, each said as a fact
            cur.execute("UPDATE spine_levels SET mode = %s WHERE scope = %s AND path <> %s AND mode <> %s"
                        " RETURNING path, experiment", (mode, universe, universe, mode))
            for path, experiment in cur.fetchall():
                e = opened_fact(path, mode, bool(experiment), KERNEL, "tightened with the universe")
                outbox.add_row(cur, ev.encode(e), e["message_id"])
        return row(conn, universe)
    return r


def check_open(conn, parent: str, level: str, name: str, mode: str | None, experiment: bool) -> dict:
    """The pure laws over the ground's state — what a level would be, or the refusal in words:
    the parent stands here, the child law, mode tighten-only, the experiment room, not already
    open."""
    up = row(conn, parent)
    if up is None:
        raise LevelRefused(f"{parent} is not open here" if ok(parent) else GRAMMAR + f" — got {parent!r}")
    try:
        path = child(parent, level, name)
        m = tighten(up["mode"], mode)
        experiment_ok(level, experiment)
    except ValueError as e:
        raise LevelRefused(str(e)) from None
    if row(conn, path) is not None:
        raise LevelRefused(f"{words(path)} is already open")
    return {"path": path, "mode": m, "experiment": bool(experiment), "parent": parent}


def open_in(conn, args: dict, by: str, ask: str | None = None, marker: str | None = None) -> str:
    """The held act, settled: the row and its fact in the caller's transaction; the words."""
    made = check_open(conn, str(args.get("parent") or ""), str(args.get("level") or ""), str(args.get("name") or ""),
                      args.get("mode"), bool(args.get("experiment")))
    _insert(conn.cursor(), made["path"], made["mode"], made["experiment"], args.get("declares"), by,
            "opened on a person's word", ask, marker)
    return opened_words(made["path"], made["mode"], made["experiment"])


def hold_open(conn, args: dict, *, person: str, session: str | None = None) -> dict:
    """`POST /levels/open`: the laws checked NOW (a refusal is immediate, in words), then the
    act held at L2 for the person's yes — the kernel's own held act, `level.open`."""
    from . import proof
    made = check_open(conn, str(args.get("parent") or ""), str(args.get("level") or ""), str(args.get("name") or ""),
                      args.get("mode"), bool(args.get("experiment")))
    text = (f"open {words(made['path'])} as {made['mode']}"
            + (" — an experiment room" if made["experiment"] else ""))
    held = proof.hold_kernel_act(conn, text=text, person=person, tool=OPEN_TOOL,
                                 args={"parent": made["parent"], "level": level_of(made["path"]),
                                       "name": name_of(made["path"]), "mode": made["mode"],
                                       "experiment": made["experiment"],
                                       **({"declares": args["declares"]} if args.get("declares") else {})},
                                 level=OPEN_LEVEL, session=session, cls=OPEN_CLASS)
    return {"held": held, "level": OPEN_LEVEL, "class": OPEN_CLASS, "path": made["path"]}


def declare(conn, universe: str, manifest: dict) -> list[dict]:
    """The crew manifest's levels at light: each opened under the universe if it is not yet
    (mode tightened from its parent, `the crew manifest` the opener); one that would loosen
    refuses the light in words. Returns the rows that were opened now."""
    from . import outbox
    ensure_schema(conn); outbox.ensure_schema(conn)
    opened = []
    for lv in manifest_levels(manifest):
        path = absolute(universe, lv["at"])
        if row(conn, path) is not None:
            continue
        parent = parent_of(path)
        up = row(conn, parent) if parent else None
        if up is None:
            raise LevelRefused(f"the crew manifest declares {path} but {parent} is not open — declare the floor first")
        try:
            mode = tighten(up["mode"], lv["mode"])
            experiment_ok(level_of(path), lv["experiment"])
        except ValueError as e:
            raise LevelRefused(f"the crew manifest's level {path}: {e}") from None
        with conn.transaction():
            _insert(conn.cursor(), path, mode, lv["experiment"], lv["declares"], BY_MANIFEST,
                    "declared by the crew manifest")
        opened.append(row(conn, path))
    return opened


def listing(conn, universe: str) -> list[dict]:
    """Every level of this universe, root first, each with what stands HERE and what is ROLLED
    up from within it (the monoid at its minimum: bodies · asks served · spend)."""
    ensure_schema(conn)
    cur = conn.cursor()
    cur.execute("SELECT path, scope, level, name, parent, mode, experiment, declares, opened_by, opened_at, ask"
                " FROM spine_levels WHERE scope = %s ORDER BY path", (universe,))
    rows = [_view(r) for r in cur.fetchall()]
    # the bodies by the path they joined at (one per name, its latest join), the asks each served, its spend
    cur.execute("SELECT scope, count(*) FROM (SELECT DISTINCT ON (name) name, scope FROM spine_joins"
                " WHERE (scope = %s OR scope LIKE %s || '/%%') ORDER BY name, join_id DESC) j GROUP BY scope",
                (universe, universe))
    bodies = dict(cur.fetchall())
    cur.execute("SELECT j.scope, count(*) FROM spine_asks a JOIN (SELECT DISTINCT ON (did) did, scope FROM spine_joins"
                " WHERE (scope = %s OR scope LIKE %s || '/%%') ORDER BY did, join_id DESC) j ON a.served_by = j.did"
                " WHERE a.status <> 'received' GROUP BY j.scope", (universe, universe))
    served = dict(cur.fetchall())
    cur.execute("SELECT to_regclass('spine_meter') IS NOT NULL")
    usd: dict = {}
    if cur.fetchone()[0]:
        cur.execute("SELECT scope, coalesce(sum(usd), 0) FROM spine_meter WHERE (scope = %s OR scope LIKE %s || '/%%')"
                    " GROUP BY scope", (universe, universe))
        usd = {s: float(u) for s, u in cur.fetchall()}
    for r in rows:
        r["here"] = {"bodies": int(bodies.get(r["path"], 0)), "asks_served": int(served.get(r["path"], 0)),
                     "usd": usd.get(r["path"], 0.0)}
    for r in rows:
        b = empty_bundle()
        rolled = {"bodies": 0, "asks_served": 0}
        for o in rows:
            if within(o["path"], r["path"]):
                rolled["bodies"] += o["here"]["bodies"]; rolled["asks_served"] += o["here"]["asks_served"]
                b = merge(b, {**empty_bundle(), "cost": {**empty_bundle()["cost"], "usd": o["here"]["usd"]}})
        r["rolled"] = {**rolled, "usd": b["cost"]["usd"], "bundle": b}
    return rows


def policy_floors() -> list:
    """The universe tier's floors: the policy sheet's rules, each a floor — the fold's id
    changes when the law does."""
    from .body import SPINE
    p = Path(os.environ.get("SPINE_POLICY") or (SPINE / "policy" / "covenant-policy.v1.json"))
    try:
        doc = json.loads(p.read_text("utf-8"))
    except (OSError, ValueError):
        return []
    return list(doc.get("rules") or [])


def context(conn, path: str) -> dict:
    """The cascade at a path: the tiers are its ancestors' rows (the universe tier wearing
    the policy sheet's rules as floors; each level's `declares` its soft · skills · floors),
    folded root → leaf."""
    tiers = []
    for p in ancestors(path):
        r = row(conn, p)
        if r is None:
            raise LevelRefused(f"{p} is not open here")
        d = r["declares"] or {}
        tier = {"scope": p, "mode": r["mode"], "version": "0",
                "soft": d.get("soft") or {}, "skills": d.get("skills") or {},
                "floors": list(d.get("floors") or [])}
        if r["level"] == "universe":
            tier["floors"] = policy_floors() + tier["floors"]
        tiers.append(tier)
    out = cascade(tiers)
    out["words"] = words(path)
    return out
