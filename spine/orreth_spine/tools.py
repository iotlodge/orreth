# PROVENANCE: Claude Fable 5 (claude-fable-5) — rearch P2 sp3, the soul checkpoint · 2026-09-16
# Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P6 sp2, the tool hop wears the chain (AG-7) · 2026-09-21
# Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P6.5 sp1, the hop wears the SERVICE DID; a retired tool refuses · 2026-09-22
# Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P6.5 sp2, the Tools keeper: MCP-born tools through the one door; the `services` tool; a class by the arguments · 2026-09-23
# Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P6.5 sp3, the Stable keeper's `minds` tool · the interlock names the act (W30) · 2026-09-24
# Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp8, the weather tool reads the asker's own place (W58) · 2026-09-26
# Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp8 row 2, the tool door moves: the declarations are DATA (`spine/tools.v0.json`) both kernels read; the executors bind to them here · 2026-09-26
"""The tool door v0 (canon 0004): a resident acts only through a
governed door.

A tool is a declared thing: the template must name the capability
(`tools:<name>`) or the door refuses — and the refusal TEACHES (gates
teach inward; only the outer face is uniform). Every call is journaled:
who called, which tool, when, and whether it worked. A tool marked
CONSEQUENTIAL never runs on the first ask — the door raises the L2
interlock instead, and only the human's deliberate yes releases it
(cancel is the default, always).

P6 sp2 (AG-7): the tool hop is ON THE WIRE. Every call lands with the
calling body's authority chain plus the tool's own name (`tool:<name>`)
on its row, and files `orreth.tool.called.v1` through the outbox — an
envelope carrying that chain end to end and the action marker — so a
compliance row reads H → resident → firmware → tool from the record.

P6.5 sp1: a tool is a SERVICE on the registry's ladder (services.py) — the
hop wears the service's DID (`did:orreth:service:…`) when the tool is
registered, `tool:<name>` only for an unregistered one (the honest
fallback), and a RETIRED tool refuses at the door with a teaching:
retirement is the human's stop (rule 11), restore brings it back.

P7 sp8 row 2 — THE TOOL DOOR MOVES: what a built-in tool DECLARES (name ·
words · input schema · consequence class · the ground and master flags ·
which arguments hold at the interlock) is DATA in `spine/tools.v0.json`,
beside the crew manifest, read by BOTH kernels — the Rust kernel seeds the
shelf from it and probes a built-in by describe itself. What a tool DOES
stays here, body-side (0009: the kernel authorizes, journals and meters;
it never runs the call): `_BODIES` binds each declared name to its
executor, and the door's table `TOOLS` is the join — a declaration with no
executor, or an executor with no declaration, refuses at import.
"""
from __future__ import annotations

import json
import urllib.request
from pathlib import Path

TOOL_CALLED = "orreth.tool.called.v1"

# ---- the declarations: data both kernels read (P7 sp8 row 2) -------------------------

TOOLS_FORMAT = "orreth-tools/1"
DECLARATIONS = Path(__file__).resolve().parents[1] / "tools.v0.json"      # beside crew.v0.json
DECLARED_KEYS = ("name", "description", "input_schema", "consequence")
CLASSES = ("routine", "consequential", "grave")


def declarations(path: str | Path | None = None) -> list[dict]:
    """The built-in tools' declarations, read from the one file beside the
    crew manifest (`spine/tools.v0.json`) — the SAME file the Rust kernel
    reads to seed the shelf and probe a built-in. Refuses in words: a wrong
    format, a tool missing its name · words · schema · class, an unknown
    class, a name declared twice."""
    p = Path(path) if path is not None else DECLARATIONS
    doc = json.loads(p.read_text("utf-8"))
    if doc.get("format") != TOOLS_FORMAT:
        raise ValueError(f"not a tools manifest ({p}): format {doc.get('format')!r}, expected {TOOLS_FORMAT!r}")
    out, seen = [], set()
    for d in doc.get("tools") or []:
        missing = [k for k in DECLARED_KEYS if k not in d]
        if missing:
            raise ValueError(f"the tool declaration {d.get('name', '?')!r} lacks {', '.join(missing)}")
        if d["consequence"] not in CLASSES:
            raise ValueError(f"the {d['name']!r} tool declares an unknown class {d['consequence']!r} — "
                             f"the classes: {', '.join(CLASSES)}")
        if d["name"] in seen:
            raise ValueError(f"the tool {d['name']!r} is declared twice")
        seen.add(d["name"])
        out.append(d)
    return out


def held_by_of(decl: dict):
    """The class-by-the-arguments rule a declaration carries (`held_by`: the
    argument field and the values that HOLD at the interlock), as the
    callable `consequence_of` reads: a held value wears the declared class,
    any other runs at once (routine). None when the class stands for every
    call."""
    hb = decl.get("held_by")
    if not hb:
        return None
    field, held, cls = str(hb["field"]), tuple(str(v) for v in hb["held"]), decl["consequence"]
    return lambda args: cls if str(args.get(field) or "") in held else "routine"


def bind(decls: list[dict], bodies: dict[str, dict]) -> dict[str, dict]:
    """The door's table: every declaration joined to its body-side executor
    (`fn`; `words_by` for the interlock's words). A declaration without an
    executor, or an executor without a declaration, refuses at import — the
    shelf never declares a tool this body cannot run, and a body never runs
    an undeclared one."""
    declared = {d["name"] for d in decls}
    undeclared = sorted(set(bodies) - declared)
    if undeclared:
        raise RuntimeError(f"this body carries executors the shelf never declared: {', '.join(undeclared)} — "
                           f"declare them in {DECLARATIONS.name} or drop them")
    out = {}
    for d in decls:
        b = bodies.get(d["name"])
        if b is None:
            raise RuntimeError(f"the shelf declares the {d['name']!r} tool but this body has no executor for it — "
                               "a declaration without its body is a defect")
        t = dict(d, **b)
        cb = held_by_of(d)
        if cb is not None:
            t["consequence_by"] = cb
        out[d["name"]] = t
    return out


_DECLARED: dict[str, dict] = {d["name"]: d for d in declarations()}


def _acts_of(name: str) -> tuple[str, ...]:
    return tuple(_DECLARED[name]["input_schema"]["properties"]["action"]["enum"])


def _held_of(name: str) -> tuple[str, ...]:
    return tuple(_DECLARED[name]["held_by"]["held"])


# the keepers' acts and which of them hold at the interlock — ONE truth, the declaration's
SERVICES_ACTS, SERVICES_HELD = _acts_of("services"), _held_of("services")
MINDS_ACTS, MINDS_HELD = _acts_of("minds"), _held_of("minds")


class ToolRefused(RuntimeError):
    """The door's teaching refusal — names what was missing."""


class ConsequentialHold(Exception):
    """The L2 interlock: this act waits for the human's deliberate yes.
    (The held arguments live in `tool_args` — never `args`, because
    Exception.__init__ OVERWRITES `.args` with the message tuple; found
    the hard way, in-hour.)"""

    def __init__(self, tool: str, tool_args: dict, *,
                 consequence: str = "consequential", level: str = "L2"):
        super().__init__(f"the {tool} act is {consequence} — held for the "
                         f"human's confirmation at {level} (cancel is the default)")
        self.tool = tool
        self.tool_args = dict(tool_args)
        self.consequence = consequence    # P6 sp1: the class the act wears
        self.level = level                # and the proof it demands


def consequence_of(tool: dict, args: dict | None = None) -> str:
    """The class a tool declared: `consequence` by name, or the older
    `consequential` flag read as consequential/routine. P6.5 sp2: a tool
    of several acts may class them BY THE ARGUMENTS (`consequence_by`) —
    the keeper's `services` tool holds a register and runs a check; with
    no arguments in hand the declared class stands (the pin, the shelf)."""
    if args is not None and callable(tool.get("consequence_by")):
        return str(tool["consequence_by"](args))
    return tool.get("consequence") or ("consequential" if tool.get("consequential") else "routine")


def tool_manifest(name: str, tool: dict) -> dict:
    """What a tool DECLARES — the manifest the registry pins (P6.5 sp1):
    its name, its words, its input schema, its consequence class. The flags
    (ground · master · held_by) are the door's, never the pin's — the Rust
    kernel's `tools::manifest` builds the same bytes from the same file."""
    return {"name": name, "description": tool["description"],
            "input_schema": tool["input_schema"], "consequence": consequence_of(tool)}


# ---- the tools themselves ---------------------------------------------------------

NO_PLACE_WORDS = ("I do not know your place yet — nothing in your profile says where you are, so I "
                  "read no weather rather than someone else's. Say \"I live in <town, region>\" and ask again.")
NO_COORDS_WORDS = ("your profile says you live in {place}, but I could not find its coordinates when you "
                   "told me and cannot read its weather yet — tell me the place again when the road is up.")


def _weather(args: dict, conn=None) -> str:
    """The temperature outside — Open-Meteo, no key, plain words. With no
    lat/lon given it reads THE ASKER'S OWN PLACE from their profile (P7
    sp8, W58: the fixed Arizona point answered the weather for the wrong
    place); a person who has told the ground no place is told so, never
    someone else's weather."""
    where = None
    if args.get("latitude") is not None and args.get("longitude") is not None:
        lat, lon = float(args["latitude"]), float(args["longitude"])
    else:
        from . import profile
        where = profile.place_for_ask(conn, args.get("_ask")) if conn is not None else None
        if where is None:
            return NO_PLACE_WORDS
        if where.get("lat") is None:
            return NO_COORDS_WORDS.format(place=where["place"])
        lat, lon = float(where["lat"]), float(where["lon"])
    url = ("https://api.open-meteo.com/v1/forecast"
           f"?latitude={lat}&longitude={lon}"
           "&current=temperature_2m,apparent_temperature"
           "&temperature_unit=fahrenheit")
    with urllib.request.urlopen(url, timeout=10) as r:
        cur = json.loads(r.read())["current"]
    at = f"in {where['place']} (your place, from your profile)" if where else f"at {lat:.2f},{lon:.2f}"
    return (f"Right now {at} it is "
            f"{cur['temperature_2m']}°F outside "
            f"(feels like {cur['apparent_temperature']}°F).")


GATEWAY = None          # P6.5 sp3: the rig's gateway lane, set at boot — the keepers' checks ping through it


def _services_words(args: dict) -> str:
    """W30: the interlock names the act in words — never "The services act"."""
    act, name = str(args.get("action") or ""), str(args.get("name") or "the")
    if act == "register":
        return (f"Are you sure? Registering the {name or 'new'} MCP server at {args.get('locator') or '?'} is consequential — "
                "it is recorded, and you can rest it later")
    if act == "retire":
        return f"Are you sure? Retiring the {name} service is consequential — it rests, recorded, never deleted; you can restore it later"
    if act == "restore":
        return f"Are you sure? Restoring the {name} service is consequential — it stands again, recorded"
    if act == "version":
        return f"Are you sure? Re-pinning the {name} service to its changed manifest is consequential — recorded; the old pin stays in its history"
    return f"Are you sure? The {act or 'services'} act is consequential — it is recorded, and you can rest it later"


def interlock_words_for(tool: str, args: dict | None = None) -> str:
    """The L2 interlock's words for a tool act (W23 · W30 · rule 13): the
    act NAMED — what happens, that it is recorded, that it can be rested —
    when the tool declares `words_by`; the plain default otherwise."""
    spec = TOOLS.get(tool) or {}
    if callable(spec.get("words_by")):
        return spec["words_by"](args or {}) + ". Cancel is the default; a deliberate click confirms."
    from .resident import interlock_words
    return interlock_words(tool)


def _gw():
    """The gateway's management door when the gateway is lit; None when dark."""
    from . import stable
    gw = stable.Gateway()
    return gw if gw.ready() else None


def _minds_words(args: dict) -> str:
    return "Are you sure? " + _minds_phrase(args) + " is consequential — it is recorded, and you can rest it later"


def _minds_phrase(args: dict) -> str:
    from . import stable
    act = str(args.get("action") or "")
    a = dict(args)
    if act == "register":
        a["deal"] = {"provider": args.get("provider"), "model": args.get("model")}
        return stable.act_words(stable.REGISTER_TOOL, a)
    if act == "assign":
        return stable.act_words(stable.ASSIGN_TOOL, {"subject": args.get("subject") or "*", "klass": args.get("klass") or stable.ANY,
                                                     "stall": args.get("stall") or args.get("name")})
    if act == "unassign":
        return stable.act_words(stable.UNASSIGN_TOOL, {"subject": args.get("subject") or "*", "klass": args.get("klass") or stable.ANY})
    if act == "refill":
        return stable.act_words(stable.REFILL_TOOL, {"name": args.get("subject") or args.get("name"), "usd": args.get("usd") or 1})
    if act == "retire":
        return stable.act_words(__import__("orreth_spine.services", fromlist=["RETIRE_TOOL"]).RETIRE_TOOL, {"name": args.get("name")})
    if act == "restore":
        return f"Restoring the {args.get('name')} LLM (it stands again in the Stable and the gateway)"
    if act == "repin":
        return stable.act_words(stable.REPIN_TOOL, {"name": args.get("name")})
    return f"The {act or 'minds'} act"


def _minds_tool(args: dict, conn) -> str:
    """The Stable keeper's one tool (P6.5 sp3): the Stable tended on the
    human's word — every act through stable.py / services.py, every step a
    fact under the keeper's DID, the answer in words."""
    from . import services, stable
    act = str(args.get("action") or "").strip().lower()
    name = str(args.get("name") or "").strip().lower()
    by = args.get("_by") or "the stablekeeper"
    if act not in MINDS_ACTS:
        raise ValueError(f"the minds tool's acts: {', '.join(MINDS_ACTS)} — not {act!r}")
    gw = _gw()
    if act == "register":
        provider, model = str(args.get("provider") or "").strip().lower(), str(args.get("model") or "").strip()
        if not name or not provider or not model:
            raise ValueError("register needs a short name, the provider (anthropic · openrouter · ollama · openai · compatible) and the model id")
        price = None
        if args.get("price_in_per_m") is not None or args.get("price_out_per_m") is not None:
            price = {"in_per_m": args.get("price_in_per_m") or 0, "out_per_m": args.get("price_out_per_m") or 0}
        d = stable.deal(model, provider, base=args.get("base") or None, price=price, context=args.get("context"),
                        modalities=args.get("modalities"), klass=str(args.get("klass") or "standard"),
                        key=args["key"] if args.get("key") else "auto")
        if gw is not None and price is None:                # the price from the gateway's own map, never guessed
            gw.add_stall(name, d)
            seen = gw.seen_deal(name) or {}
            if (seen.get("price") or {}).get("in_per_m") is not None:
                d = stable.deal(model, provider, base=d.get("base"), price=seen["price"], context=d.get("context") or seen.get("context"),
                                modalities=seen.get("modalities") if not args.get("modalities") else d["modalities"],
                                klass=d["class"], key=d.get("key"))
        made = stable.register_mind(conn, name, d, by=by, gw=gw)
        return (f"the {made['name']} LLM stands in the Stable — {stable.stall_words(dict(made, spend=None))}"
                + ("" if gw is not None else " (the gateway is dark: written to the ladder, not yet into the gateway — the keeper's beat syncs it)"))
    if act == "check":
        out = [services.check(conn, name, gateway=GATEWAY, by=by)] if name else \
              services.check_all(conn, kind="mind", gateway=GATEWAY, by=by)
        if not out:
            return "nothing to check — no LLM is in the Stable; \"stablekeeper, add the LLM <provider> <model id> as <name>\""
        return "checked " + str(len(out)) + ": " + " · ".join(
            f"{c['name']} → {'healthy' if c['ok'] else 'UNHEALTHY' if c['ok'] is False else 'not probed'}: {c['detail']}" for c in out)
    if act in ("search", "list"):
        rows = stable.search(conn, args.get("q") if act == "search" else None, klass=args.get("klass") or None,
                             max_in_per_m=args.get("max_in_per_m"), modality=args.get("modality") or None)
        if not rows:
            return "no LLM matches" if act == "search" else "the Stable is empty — no LLM stands yet"
        asg = stable.assignments(conn)
        return (f"{len(rows)} mind{'s' if len(rows) != 1 else ''}: " + " · ".join(stable.stall_words(s) for s in rows)
                + ("; assignments: " + ", ".join(f"{a['subject']} uses {a['stall']} for {'all' if a['klass'] == stable.ANY else a['klass']} work" for a in asg) if asg else "; no assignments — every body uses its template's LLM"))
    if act == "assign":
        subject = str(args.get("subject") or "*").strip()
        made = stable.assign(conn, subject, str(args.get("klass") or stable.ANY), str(args.get("stall") or name), by=by)
        return f"{'every body' if made['subject'] == '*' else made['subject']} now uses the {made['stall']} LLM for {'all its' if made['klass'] == stable.ANY else made['klass']} work — recorded"
    if act == "unassign":
        made = stable.unassign(conn, str(args.get("subject") or "*").strip(), str(args.get("klass") or stable.ANY), by=by)
        return f"{made['subject']}'s {made['klass']} assignment to {made['stall']} is lifted — recorded"
    if act in ("refill", "fuel"):
        subject = str(args.get("subject") or name or "").strip()
        did = _did_of_body(conn, subject)
        if did is None:
            raise ValueError(f"no body named {subject!r} is joined here")
        if act == "fuel":
            g = stable.fuel(conn, did, gw)
            if g is None:
                return f"{subject} has no lease yet — it is fueled on its first thought (${stable.lease_defaults()[0]:g} every {stable.lease_defaults()[1]} day(s))"
            return (f"{subject}: ${g['spend'] if g['spend'] is not None else '?'} spent of ${g['max_usd']:g} this window"
                    + (f", renews at {g['renews_at']}" if g.get('renews_at') else "") + (" — DRAINED" if g.get("drained_at") else ""))
        if gw is None:
            raise ValueError("the gateway is dark — a refill needs it lit (scripts/dev.sh up)")
        made = stable.refill(conn, did, float(args.get("usd") or 1.0), by=by, gw=gw, name=subject)
        return f"{subject} refilled by ${made['added_usd']:g} — its allowance is now ${made['max_usd']:g}"
    if act == "spend":
        sp = stable.spend(conn)
        if not sp["rows"]:
            return "the meter is empty — no thought has been billed yet"
        return (f"${sp['usd_today']:.4f} today, ${sp['usd']:.4f} all time: "
                + " · ".join(f"{r['did'].rsplit(':', 1)[-1]} on {r['stall']}: ${r['usd']:.4f} over {r['calls']} calls"
                             + (f" ({r['failed']} failed)" if r['failed'] else "") for r in sp["rows"][:12]))
    if act == "retire":
        made = stable.retire_mind(conn, name, by=by, gw=gw)
        return f"the {made['name']} LLM is retired — at rest in the Stable, dropped from the gateway, recorded, never deleted"
    if act == "restore":
        made = stable.restore_mind(conn, name, by=by, gw=gw)
        return f"the {made['name']} LLM stands again ({made['state']}) — a new fact; its rest stays in the record"
    if act == "repin":
        s_ = services.get(conn, name)
        if s_ is None:
            raise ValueError(f"no mind named {name!r}")
        seen = stable.seen_deal(gw, s_) or {}
        if not seen:
            raise ValueError(f"the market has no word on {name} to re-pin from")
        d = dict(s_["manifest"], price=seen.get("price") or s_["manifest"]["price"], context=seen.get("context") or s_["manifest"].get("context"))
        made = stable.repin_mind(conn, name, d, by=by, gw=gw)
        return f"the {made['name']} LLM is re-pinned (version {made['version']}) — the old pin stays in its history"
    since = args.get("since")
    cur = conn.cursor()
    cur.execute("SELECT name, ok, detail, at FROM spine_service_health WHERE scope = %s AND name IN"
                " (SELECT name FROM spine_services WHERE scope = %s AND kind = 'mind')"
                " AND (%s::timestamptz IS NULL OR at > %s::timestamptz) ORDER BY health_id DESC LIMIT 20",
                (__import__("orreth_spine.envelope", fromlist=["scope"]).scope(),
                 __import__("orreth_spine.envelope", fromlist=["scope"]).scope(), since, since))
    rows = cur.fetchall()
    return ("nothing changed in the Stable" if not rows else
            "; ".join(f"{r[3].strftime('%H:%M')} {r[0]} {'healthy' if r[1] else 'UNHEALTHY' if r[1] is False else 'noted'} — {r[2]}" for r in rows))


def _did_of_body(conn, name: str) -> str | None:
    from . import envelope as _ev
    cur = conn.cursor()
    cur.execute("SELECT did FROM spine_joins WHERE scope = %s AND lower(name) = lower(%s) ORDER BY join_id DESC LIMIT 1",
                (_ev.scope(), name))
    r = cur.fetchone()
    return r[0] if r else None


def _services_tool(args: dict, conn) -> str:
    """The keeper's one tool (P6.5 sp2): the shelf tended on the human's
    word — every act through services.py / mcp.py, every step a fact under
    the keeper's DID, the answer in words."""
    from . import mcp, services
    act = str(args.get("action") or "").strip().lower()
    name = str(args.get("name") or "").strip().lower()
    by = args.get("_by") or "the toolkeeper"
    if act not in SERVICES_ACTS:
        raise ValueError(f"the services tool's acts: {', '.join(SERVICES_ACTS)} — not {act!r}")
    if act == "register":
        locator = str(args.get("locator") or "").strip()
        if not name or not locator:
            raise ValueError("register needs a short name and the server's locator (its command or URL)")
        made = mcp.register_server(conn, name, locator, by=by,
                                   secrets_with=[str(s) for s in (args.get("secrets_with") or [])])
        t = made["tools"]
        listed = t["new"] + t["versioned"] + t["present"]
        return (f"registered the {name} MCP server ({made['info'].get('name') or 'unnamed'} "
                f"{made['info'].get('version') or '?'}) at {mcp.locator_words(locator)} — "
                f"{len(listed)} tool{'s' if len(listed) != 1 else ''} on the shelf under it"
                + (": " + ", ".join(listed) if listed else "")
                + (f"; gone: {', '.join(t['gone'])}" if t["gone"] else "")
                + (f"; refused: {'; '.join(t['refused'])}" if t["refused"] else ""))
    if act in ("check", "version"):
        if name:
            out = [services.check(conn, name, by=by)]
        else:
            out = services.check_all(conn, kind="mcp", by=by)       # each server's listing verdicts its tools
        if not out:
            return "nothing to check — no MCP server is on the shelf; \"toolkeeper, add the MCP server at <command or url>\""
        lines = [f"{c['name']} ({c['kind']}) → {'healthy' if c['ok'] else 'UNHEALTHY' if c['ok'] is False else 'not probed'}: {c['detail']}"
                 for c in out]
        return f"checked {len(out)}: " + " · ".join(lines)
    if act == "retire":
        made = services.retire(conn, name, by=by, ask=args.get("_ask"), parent_marker=args.get("_parent"))
        return f"the {made['name']} {made['kind']} is retired — at rest on the shelf, recorded, never deleted; restore brings it back"
    if act == "restore":
        made = services.restore(conn, name, by=by)
        return f"the {made['name']} {made['kind']} stands registered again — a new fact; its stop stays in the record"
    if act == "changes":
        since = str(args.get("since") or "").strip() or mcp.last_ask_at(conn, by)
        rows = mcp.changes(conn, since)
        if not rows:
            return "nothing changed on the shelf" + (f" since {since[:16]}" if since else "")
        return (f"{len(rows)} change{'s' if len(rows) != 1 else ''} on the shelf"
                + (f" since {since[:16]}" if since else "") + ": "
                + " · ".join(f"{r['at'][11:16]} {r['note']}" for r in rows))
    rows = [s for s in services.listing(conn) if s["kind"] in ("mcp", "tool")]
    return "on the shelf: " + " · ".join(
        f"{s['name']} ({s['kind']}{', under ' + s['manifest']['server'] if s['manifest'].get('server') else ''}) {s['state']}"
        for s in rows) if rows else "nothing on the shelf"


def _seal_record(args: dict) -> str:
    """A deliberately consequential test act: 'seal' a note so it can
    never be edited — the interlock's proving ground."""
    return f"Sealed the note {args.get('key', '?')!r} — it is now permanent."


# ---- the executors: what a declared tool DOES, body-side (never the kernel) -----------------

_BODIES: dict[str, dict] = {
    "weather": {"fn": _weather},
    "acquire": {
        "fn": lambda args, conn: (lambda h: f"acquired {len(args['text'])} characters "
                                            f"under {args['key']!r} — hash {h[:16]}")(
              __import__("orreth_spine.store", fromlist=["OrrethStore"])
              .OrrethStore(conn, by_did=args["_by"]).put(args["_name"], args["key"], args["text"])),
    },
    "mark": {
        "fn": lambda args, conn: (lambda mk: (lambda m: (lambda asked:
              f"marked {m['ref']} as {m['kind']!r} ({m['id']}); "
              f"{len(asked)} interested bod{'y' if len(asked) == 1 else 'ies'} asked to act")(
              mk.dispatch_interests(conn, m, m["ref"], m["note"])))(
              mk.set_marker(conn, args["kind"], ref=(mk.get(conn, args["_parent"]) or {}).get("ref", args["_by"]) if args.get("_parent") else args["_by"],
                            by=args["_by"], parent=args.get("_parent"), note=args["note"],
                            chain=args.get("_chain"))))(
              __import__("orreth_spine.markers", fromlist=["set_marker"])),
    },
    "purge-memory": {
        "fn": lambda args, conn: (lambda st, dg: (lambda out: (lambda n:
              f"purged {out['versions']} version(s) of {out['ref']!r}; {n} digest(s) rebuilt; "
              f"tombstone keeps the hashes")(dg.rebuild_citing(conn, out["ref"])))(
              st.OrrethStore(conn, by_did=args["_by"]).purge(args["_name"], args["key"])))(
              __import__("orreth_spine.store", fromlist=["OrrethStore"]),
              __import__("orreth_spine.digest", fromlist=["rebuild_citing"])),
    },
    "add-watch": {
        "fn": lambda args, conn: __import__("orreth_spine.monitor", fromlist=["add_watch"])
              .add_watch(conn, args["name"], args["metric"], args["op"],
                         args["threshold"], by=args.get("_by", "the monitor")),
    },
    # P6.5 sp2: the Tools keeper's one tool — the shelf tended on the human's word
    "services": {"fn": _services_tool, "words_by": _services_words},        # W30: the interlock names the act
    # P6.5 sp3: the Stable keeper's one tool — the minds tended on the human's word
    "minds": {"fn": _minds_tool, "words_by": _minds_words},
    "seal-record": {"fn": _seal_record},
    # P6 sp1's proving ground for GRAVE: a test-only act that demands the person's code
    # (L3-code) — no template of the house declares it; a test template does
    "erase-record": {"fn": lambda args: f"Erased the sealed note {args.get('key', '?')!r} — no trace remains."},
}

# the door's table: the declarations (data) joined to their executors (code)
TOOLS: dict[str, dict] = bind(list(_DECLARED.values()), _BODIES)

def ensure_schema(conn) -> None:
    from .outbox import once
    if not once(conn, "tools"):
        return
    with conn.transaction():
        cur = conn.cursor()
        cur.execute("SELECT pg_advisory_xact_lock(742199)")  # DDL race guard
        cur.execute(
            "CREATE TABLE IF NOT EXISTS spine_tool_calls ("
            " call_id bigserial PRIMARY KEY,"
            " did text NOT NULL, tool text NOT NULL,"
            " args text NOT NULL, ok boolean NOT NULL,"
            " result text, at timestamptz NOT NULL DEFAULT now())")
        # P6 sp2: the hop wears its chain and names its ask (AG-7)
        cur.execute("ALTER TABLE spine_tool_calls ADD COLUMN IF NOT EXISTS authority_chain text")
        cur.execute("ALTER TABLE spine_tool_calls ADD COLUMN IF NOT EXISTS ask text")
        # P6.5 sp1: the hop names the SERVICE it called (the registry's DID)
        cur.execute("ALTER TABLE spine_tool_calls ADD COLUMN IF NOT EXISTS service text")
        cur.execute("CREATE INDEX IF NOT EXISTS spine_tool_calls_did ON spine_tool_calls (did, call_id DESC)")   # schema 2 (the perf cure)


class ToolDoor:
    """One door per serving resident: capability-checked, journaled,
    interlocked."""

    def __init__(self, conn, *, did: str, capabilities: list[str],
                 name: str | None = None, marker: str | None = None,
                 ask: str | None = None, chain: list[str] | None = None):
        self._conn = conn
        self.did = did
        self.name = name                  # the memory namespace (acquire)
        self.marker = marker              # the serving ask's marker (0006)
        self.ask = ask                    # the serving ask (the fact's ref)
        # the chain the body wears while it serves (AG-7): the origin human
        # first, then every self whose results it read, then itself
        self.chain = list(chain) if chain else []
        if did not in self.chain:
            self.chain.append(did)
        self.capabilities = capabilities
        ensure_schema(conn)

    def schemas(self) -> list[dict]:
        """The declared tools only — the mind never even sees a tool the
        body may not use."""
        out = []
        for name, t in TOOLS.items():
            if f"tools:{name}" in self.capabilities:
                out.append({"name": name, "description": t["description"],
                            "input_schema": t["input_schema"]})
        for cap in self.capabilities:            # P6.5 sp2: a declared MCP-born tool, when its server listed it
            name = cap[6:] if cap.startswith("tools:") else None
            if name and name not in TOOLS:
                t = self._shelf_tool(name)
                if t is not None:
                    out.append({"name": name, "description": t["description"], "input_schema": t["input_schema"]})
        return out

    def _shelf_tool(self, name: str) -> dict | None:
        """An MCP-born tool on the shelf (kind tool, its manifest naming
        its server), as a door spec: words · schema · class · the row —
        None when the shelf has no such standing tool (a retired one is
        returned so the door can teach)."""
        conn = getattr(self, "_conn", None)
        if conn is None:
            return None
        from . import services
        row = services.get(conn, name)
        if row is None or row["kind"] != "tool" or not (row["manifest"] or {}).get("server"):
            return None
        m = row["manifest"]
        return {"description": m.get("description") or f"the {name} tool of the {m['server']} server",
                "input_schema": m.get("input_schema") or {"type": "object", "properties": {}},
                "consequence": m.get("consequence") or "routine", "mcp": row}

    def call(self, name: str, args: dict, *, confirmed: bool = False) -> str:
        if f"tools:{name}" not in self.capabilities:
            raise ToolRefused(
                f"this body never declared the {name!r} tool — a template "
                "declares its tools, or the door stays shut")
        tool = TOOLS.get(name) or self._shelf_tool(name)   # P6.5 sp2: or an MCP-born tool on the shelf
        if tool is None:
            raise ToolRefused(f"no tool named {name!r} lives on this shelf")
        from . import services                   # P6.5 sp1: the door reads the ladder
        conn = getattr(self, "_conn", None)      # (a door without a ground — the pure hold test — reads none)
        service = services.did_of(conn, "tool", name) if conn is not None else None
        if service and services.state_of(conn, "tool", name) == "retired":
            raise ToolRefused(f"the {name} tool is retired on this shelf — at rest, never deleted; "
                              f"the human restores it (\"restore the {name} tool\") before it serves again")
        cls = consequence_of(tool, args)
        if cls != "routine" and not confirmed:
            # the proof demand rises to meet the consequence (P12):
            # consequential → L2 · grave → L3 (a code; or a master when
            # the tool says so — the seam for the gravest acts)
            from .proof import level_for
            raise ConsequentialHold(name, args, consequence=cls,
                                    level=level_for(cls, master=bool(tool.get("master"))))
        try:
            if tool.get("mcp"):           # P6.5 sp2: tools/call through the one MCP door
                from . import mcp
                result = mcp.call(self._conn, tool["mcp"], args)
            elif tool.get("ground"):      # an act on the ground rides the
                args = dict(args, _by=self.did, _name=self.name or self.did,
                            _parent=self.marker, _chain=self.chain, _ask=self.ask)
                result = tool["fn"](args, self._conn)
            else:
                result = tool["fn"](args)
            ok = True
        except Exception as e:
            result, ok = f"{type(e).__name__}: {e}"[:300], False
        from . import envelope as ev, markers, outbox
        public = {k: v for k, v in args.items() if not k.startswith("_")}
        chain = self.chain + [service or f"tool:{name}"]   # the hop, end to end: the service's
        markers.ensure_schema(self._conn); outbox.ensure_schema(self._conn)   # DID when registered
        with self._conn.transaction():
            cur = self._conn.cursor()
            cur.execute(
                "INSERT INTO spine_tool_calls (did, tool, args, ok, result, authority_chain, ask, service)"
                " VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                (self.did, name, json.dumps(public), ok, result[:500], json.dumps(chain), self.ask, service))
            marker = markers.as_env(self._conn, self.marker)
            if ok and name != "mark":            # an ACTION under the ask's
                mid = markers.new_id()           # marker (0006); `mark` sets
                markers.insert(cur, mid, "action", self.marker,   # its own
                               f"{name}:{self.marker or self.did}", self.did, name)
                marker = {"kind": "action", "id": mid, "parent": self.marker, "by": self.did}
            e = ev.make_envelope(                # the fact: the hop on the wire (AG-7)
                kind="event", type=TOOL_CALLED, universe_id=ev.scope(), scope_path=ev.scope(),
                payload={"ref": self.ask or self.did, "hash": ev.content_hash(public),
                         "tool": name, "ok": ok, "by": self.did,
                         **({"service": service} if service else {})},
                correlation_id=self.ask, authority_chain=chain, marker=marker)
            outbox.add_row(cur, ev.encode(e), e["message_id"])
        if not ok:
            raise ToolRefused(f"the {name} tool failed honestly: {result}")
        return result


def journal(conn, did: str) -> list[tuple]:
    ensure_schema(conn)
    cur = conn.cursor()
    cur.execute("SELECT tool, ok FROM spine_tool_calls WHERE did = %s"
                " ORDER BY call_id", (did,))
    return cur.fetchall()
