# PROVENANCE: Claude Fable 5 (claude-fable-5) — rearch P2 sp3, the soul checkpoint · 2026-09-16
# Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P6 sp2, the tool hop wears the chain (AG-7) · 2026-09-21
# Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P6.5 sp1, the hop wears the SERVICE DID; a retired tool refuses · 2026-09-22
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
"""
from __future__ import annotations

import json
import urllib.request

TOOL_CALLED = "orreth.tool.called.v1"


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


def consequence_of(tool: dict) -> str:
    """The class a tool declared: `consequence` by name, or the older
    `consequential` flag read as consequential/routine."""
    return tool.get("consequence") or ("consequential" if tool.get("consequential") else "routine")


def tool_manifest(name: str, tool: dict) -> dict:
    """What a tool DECLARES — the manifest the registry pins (P6.5 sp1):
    its name, its words, its input schema, its consequence class."""
    return {"name": name, "description": tool["description"],
            "input_schema": tool["input_schema"], "consequence": consequence_of(tool)}


# ---- the tools themselves ---------------------------------------------------------

def _weather(args: dict) -> str:
    """The temperature outside — Open-Meteo, no key, plain words.
    Defaults to Payson, Arizona; any lat/lon welcome."""
    lat = float(args.get("latitude", 34.2308))
    lon = float(args.get("longitude", -111.3251))
    url = ("https://api.open-meteo.com/v1/forecast"
           f"?latitude={lat}&longitude={lon}"
           "&current=temperature_2m,apparent_temperature"
           "&temperature_unit=fahrenheit")
    with urllib.request.urlopen(url, timeout=10) as r:
        cur = json.loads(r.read())["current"]
    return (f"Right now at {lat:.2f},{lon:.2f} it is "
            f"{cur['temperature_2m']}°F outside "
            f"(feels like {cur['apparent_temperature']}°F).")


def _seal_record(args: dict) -> str:
    """A deliberately consequential test act: 'seal' a note so it can
    never be edited — the interlock's proving ground."""
    return f"Sealed the note {args.get('key', '?')!r} — it is now permanent."


TOOLS: dict[str, dict] = {
    "weather": {
        "description": "Read the real temperature outside right now. Call "
                       "it with NO arguments to use the operator's own "
                       "town (the default) — never ask the human where "
                       "they are first.",
        "input_schema": {"type": "object", "properties": {
            "latitude": {"type": "number"}, "longitude": {"type": "number"}},
            "required": []},
        "consequential": False,
        "fn": _weather,
    },
    "acquire": {
        "description": "Acquire a text into your memory under a short key: "
                       "every word is kept exactly, with its provenance, and "
                       "the human can recall every word later — by key, by "
                       "ask, or by timeframe. Use it when the human asks you "
                       "to remember, keep, acquire, or take in a text.",
        "input_schema": {"type": "object", "properties": {
            "key": {"type": "string"}, "text": {"type": "string"}},
            "required": ["key", "text"]},
        "consequential": False,
        "ground": True,
        "fn": lambda args, conn: (lambda h: f"acquired {len(args['text'])} characters "
                                            f"under {args['key']!r} — hash {h[:16]}")(
              __import__("orreth_spine.store", fromlist=["OrrethStore"])
              .OrrethStore(conn, by_did=args["_by"]).put(args["_name"], args["key"], args["text"])),
    },
    "mark": {
        "description": "Set a marker on what you are executing: a declared "
                       "kind (e.g. 'improvement') and a short note. Other "
                       "bodies that declared interest in that kind will be "
                       "asked to act on it. A kind must be declared first.",
        "input_schema": {"type": "object", "properties": {
            "kind": {"type": "string"}, "note": {"type": "string"}},
            "required": ["kind", "note"]},
        "consequential": False,
        "ground": True,
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
        "description": "Permanently erase a memory you acquired, every "
                       "version of it, under a key — the words leave the "
                       "Record, the projection, and every digest that cited "
                       "them; only a tombstone with the hashes remains. This "
                       "cannot be undone; it holds for the human's yes.",
        "input_schema": {"type": "object", "properties": {
            "key": {"type": "string"}}, "required": ["key"]},
        "consequential": True,
        "ground": True,
        "fn": lambda args, conn: (lambda st, dg: (lambda out: (lambda n:
              f"purged {out['versions']} version(s) of {out['ref']!r}; {n} digest(s) rebuilt; "
              f"tombstone keeps the hashes")(dg.rebuild_citing(conn, out["ref"])))(
              st.OrrethStore(conn, by_did=args["_by"]).purge(args["_name"], args["key"])))(
              __import__("orreth_spine.store", fromlist=["OrrethStore"]),
              __import__("orreth_spine.digest", fromlist=["rebuild_citing"])),
    },
    "add-watch": {
        "description": "Propose a new monitoring watch: a named ALERT on one "
                       "metric (outbox_pending · oldest_outbox_age_s · "
                       "asks_received · bodies_alive · bodies_dormant) — the "
                       "watch turns RED when `metric op threshold` holds and is "
                       "green otherwise (ops: <= >= < > ==). To catch dormant "
                       "bodies: bodies_dormant > 0. To catch asks left waiting: "
                       "asks_received > 0. It holds for the human's yes before "
                       "it lands. When the human asks you to propose a watch, "
                       "call this tool — never describe the watch in words instead.",
        "input_schema": {"type": "object", "properties": {
            "name": {"type": "string"}, "metric": {"type": "string"},
            "op": {"type": "string"}, "threshold": {"type": "number"}},
            "required": ["name", "metric", "op", "threshold"]},
        "consequential": True,
        "ground": True,
        "fn": lambda args, conn: __import__("orreth_spine.monitor", fromlist=["add_watch"])
              .add_watch(conn, args["name"], args["metric"], args["op"],
                         args["threshold"], by=args.get("_by", "the monitor")),
    },
    "seal-record": {
        "description": "Permanently seal a note so it can never be edited "
                       "again. This cannot be undone.",
        "input_schema": {"type": "object", "properties": {
            "key": {"type": "string"}}, "required": ["key"]},
        "consequential": True,
        "fn": _seal_record,
    },
    "erase-record": {
        # P6 sp1's proving ground for GRAVE: a test-only act that demands
        # the person's code (L3-code) — no template of the house declares
        # it; a test template does, so the path is walkable and testable
        "description": "Permanently erase a sealed note — every trace of "
                       "it. This is grave and cannot be undone.",
        "input_schema": {"type": "object", "properties": {
            "key": {"type": "string"}}, "required": ["key"]},
        "consequential": True,
        "consequence": "grave",
        "fn": lambda args: f"Erased the sealed note {args.get('key', '?')!r} — no trace remains.",
    },
}


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
        return out

    def call(self, name: str, args: dict, *, confirmed: bool = False) -> str:
        if f"tools:{name}" not in self.capabilities:
            raise ToolRefused(
                f"this body never declared the {name!r} tool — a template "
                "declares its tools, or the door stays shut")
        tool = TOOLS.get(name)
        if tool is None:
            raise ToolRefused(f"no tool named {name!r} lives on this shelf")
        from . import services                   # P6.5 sp1: the door reads the ladder
        conn = getattr(self, "_conn", None)      # (a door without a ground — the pure hold test — reads none)
        service = services.did_of(conn, "tool", name) if conn is not None else None
        if service and services.state_of(conn, "tool", name) == "retired":
            raise ToolRefused(f"the {name} tool is retired on this shelf — at rest, never deleted; "
                              f"the human restores it (\"restore the {name} tool\") before it serves again")
        cls = consequence_of(tool)
        if cls != "routine" and not confirmed:
            # the proof demand rises to meet the consequence (P12):
            # consequential → L2 · grave → L3 (a code; or a master when
            # the tool says so — the seam for the gravest acts)
            from .proof import level_for
            raise ConsequentialHold(name, args, consequence=cls,
                                    level=level_for(cls, master=bool(tool.get("master"))))
        try:
            if tool.get("ground"):        # an act on the ground rides the
                args = dict(args, _by=self.did, _name=self.name or self.did,
                            _parent=self.marker, _chain=self.chain)
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
