# PROVENANCE: Claude Fable 5 (claude-fable-5) — rearch P2 sp3, the soul checkpoint · 2026-09-16
"""The tool door v0 (canon 0004): a resident acts only through a
governed door.

A tool is a declared thing: the template must name the capability
(`tools:<name>`) or the door refuses — and the refusal TEACHES (gates
teach inward; only the outer face is uniform). Every call is journaled:
who called, which tool, when, and whether it worked. A tool marked
CONSEQUENTIAL never runs on the first ask — the door raises the L2
interlock instead, and only the human's deliberate yes releases it
(cancel is the default, always).
"""
from __future__ import annotations

import json
import urllib.request


class ToolRefused(RuntimeError):
    """The door's teaching refusal — names what was missing."""


class ConsequentialHold(Exception):
    """The L2 interlock: this act waits for the human's deliberate yes.
    (The held arguments live in `tool_args` — never `args`, because
    Exception.__init__ OVERWRITES `.args` with the message tuple; found
    the hard way, in-hour.)"""

    def __init__(self, tool: str, tool_args: dict):
        super().__init__(f"the {tool} act is consequential — held for the "
                         "human's confirmation (cancel is the default)")
        self.tool = tool
        self.tool_args = dict(tool_args)


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
        "description": "Propose a new monitoring watch: a named check of one "
                       "metric (outbox_pending · oldest_outbox_age_s · "
                       "asks_received · bodies_alive · bodies_dormant) against "
                       "a threshold with an op (<= >= < > ==). It holds for "
                       "the human's yes before it lands.",
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


class ToolDoor:
    """One door per serving resident: capability-checked, journaled,
    interlocked."""

    def __init__(self, conn, *, did: str, capabilities: list[str],
                 name: str | None = None):
        self._conn = conn
        self.did = did
        self.name = name                  # the memory namespace (acquire)
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
        if tool["consequential"] and not confirmed:
            raise ConsequentialHold(name, args)
        try:
            if tool.get("ground"):        # an act on the ground rides the
                args = dict(args, _by=self.did, _name=self.name or self.did)
                result = tool["fn"](args, self._conn)
            else:
                result = tool["fn"](args)
            ok = True
        except Exception as e:
            result, ok = f"{type(e).__name__}: {e}"[:300], False
        with self._conn.transaction():
            self._conn.cursor().execute(
                "INSERT INTO spine_tool_calls (did, tool, args, ok, result)"
                " VALUES (%s, %s, %s, %s, %s)",
                (self.did, name, json.dumps(args), ok, result[:500]))
        if not ok:
            raise ToolRefused(f"the {name} tool failed honestly: {result}")
        return result


def journal(conn, did: str) -> list[tuple]:
    ensure_schema(conn)
    cur = conn.cursor()
    cur.execute("SELECT tool, ok FROM spine_tool_calls WHERE did = %s"
                " ORDER BY call_id", (did,))
    return cur.fetchall()
