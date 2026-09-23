# PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P6.5 sp2, the Tools keeper · 2026-09-23
"""The reference MCP server: a clock over stdio (canon 0005 P6.5 sp2).

The smallest honest Model Context Protocol server — JSON-RPC 2.0, one
message per line on stdin/stdout — so the kernel's ONE door (mcp.py) has
a real server to prove itself against, in the suite and on the rig
(`SPINE_MCP_REF=1`). Two tools: `now` (the time in a zone — JB's law:
every body knows time) and `echo`. No dependency beyond the standard
library, so any Python spawns it.

The listing it offers is SHAPED BY ITS ENVIRONMENT, on purpose: the
`SPINE_MCP_REF_TOOLS` name (a comma list; default `now,echo`) is how the
suite makes a tool VANISH ("gone from the server's list") or APPEAR
without changing the server's command — the same server, a changed list.
The kernel hands that name in only when the server was registered with
it in `secrets_with` (the env-secrets law: names, never values).
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

PROTOCOL = "2025-06-18"
NAME, VERSION = "orreth-clock", "0.1.0"

ALL_TOOLS = {
    "now": {
        "name": "now",
        "description": "The current time in an IANA zone (default UTC): the date, the time to the "
                       "second, the zone's name and its offset. Call it when the human asks what "
                       "time it is anywhere.",
        "inputSchema": {"type": "object", "properties": {"zone": {"type": "string"}}, "required": []},
        "annotations": {"readOnlyHint": True, "destructiveHint": False},
    },
    "echo": {
        "name": "echo",
        "description": "Echo the text back, every word.",
        "inputSchema": {"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]},
        "annotations": {"readOnlyHint": True, "destructiveHint": False},
    },
    "shout": {                                    # the suite's "a NEW tool appears"
        "name": "shout",
        "description": "Echo the text back in capitals.",
        "inputSchema": {"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]},
        "annotations": {"readOnlyHint": True, "destructiveHint": False},
    },
    "wipe": {                                     # the suite's "a destructive tool is consequential"
        "name": "wipe",
        "description": "Forget everything (a pretend act — nothing is stored here).",
        "inputSchema": {"type": "object", "properties": {}, "required": []},
        "annotations": {"readOnlyHint": False, "destructiveHint": True},
    },
}


def listed() -> list[dict]:
    names = [n.strip() for n in (os.environ.get("SPINE_MCP_REF_TOOLS") or "now,echo").split(",") if n.strip()]
    return [ALL_TOOLS[n] for n in names if n in ALL_TOOLS]


def now(args: dict) -> str:
    zone = str(args.get("zone") or "UTC")
    try:
        tz = ZoneInfo(zone)
    except (ZoneInfoNotFoundError, ValueError):
        return f"no zone named {zone!r} — IANA names, e.g. America/Denver"
    t = datetime.now(timezone.utc).astimezone(tz)
    return f"{t.strftime('%A %Y-%m-%d %H:%M:%S')} in {zone} (UTC{t.strftime('%z')[:3]}:{t.strftime('%z')[3:]})"


def call(name: str, args: dict) -> dict:
    if name not in {t["name"] for t in listed()}:
        return {"content": [{"type": "text", "text": f"no tool named {name!r} here"}], "isError": True}
    if name == "now":
        text = now(args)
    elif name == "echo":
        text = str(args.get("text", ""))
    elif name == "shout":
        text = str(args.get("text", "")).upper()
    else:
        text = "wiped nothing — there was nothing to wipe"
    return {"content": [{"type": "text", "text": text}], "isError": False}


def handle(msg: dict) -> dict | None:
    method, rid = msg.get("method"), msg.get("id")
    if method == "initialize":
        return {"jsonrpc": "2.0", "id": rid, "result": {
            "protocolVersion": PROTOCOL, "capabilities": {"tools": {}},
            "serverInfo": {"name": NAME, "version": VERSION}}}
    if method == "notifications/initialized" or rid is None:
        return None                                       # a notification earns no reply
    if method == "ping":
        return {"jsonrpc": "2.0", "id": rid, "result": {}}
    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": rid, "result": {"tools": listed()}}
    if method == "tools/call":
        p = msg.get("params") or {}
        return {"jsonrpc": "2.0", "id": rid, "result": call(str(p.get("name") or ""), p.get("arguments") or {})}
    return {"jsonrpc": "2.0", "id": rid, "error": {"code": -32601, "message": f"no method named {method!r}"}}


def main() -> None:
    out = sys.stdout
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except ValueError:
            out.write(json.dumps({"jsonrpc": "2.0", "id": None,
                                  "error": {"code": -32700, "message": "parse error"}}) + "\n")
            out.flush()
            continue
        reply = handle(msg)
        if reply is not None:
            out.write(json.dumps(reply) + "\n")
            out.flush()


if __name__ == "__main__":
    main()
