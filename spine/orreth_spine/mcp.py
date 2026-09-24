# PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P6.5 sp2, the Tools keeper · 2026-09-23
# Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P6.5 sp3, the Stable keeper · 2026-09-24
# Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P6.5 sp3, the Stable keeper · 2026-09-24
"""MCP through ONE door (canon 0005 P6.5 sp2 · 0009 §1 the Tools firmware ·
0059 the Toolshed's laws · 0018 services as identities).

The kernel's Model Context Protocol client — JSON-RPC 2.0 over **stdio**
(a server command the kernel spawns) and **streamable HTTP** (a URL) —
three methods and nothing more: `initialize`, `tools/list`, `tools/call`.
Written by hand (the official `mcp` package drags a second web stack in;
these three calls are small). A session is opened per act and closed
after it: no standing child, no standing socket — the honest v0.

**A server is a service of kind `mcp` on the ladder** (services.py):
registered with its LOCATOR BY NAME — the command line or the URL, or
`env:NAME` when even the locator is a secret — and its `secrets_with`
names. **The env-secrets law** (0059): the child's environment is built
from NAMES at spawn (PATH and the named secrets, nothing else); an HTTP
server's bearer rides a named secret as a header; a VALUE touches no
record, no fact, no log — ever. A server whose named secret the ground
cannot reach refuses BY NAME and records nothing.

**Its listed tools are services of kind `tool`**, one self each
(`did:orreth:service:…`, the same DID across two registers — rule 1),
the manifest = the tool's JSON schema + its consequence class (an MCP
`destructiveHint` is CONSEQUENTIAL — the interlock, never the first
ask) + the server's name, pinned by hash, placed under the server
(`placement.affinity` names it). The server's own manifest carries the
tool list, so **a changed list VERSIONS the server**; a new tool
REGISTERS; a tool that vanished goes UNHEALTHY with the reason "gone from
the server's list" — never retired by the machine (rule 11).

**The Tools keeper** (`templates/firmware-toolkeeper.v0.json`) tends the
ladder: it registers, checks, versions, retires and restores on the
human's word through the `services` tool at the door (register · retire
· restore hold at the interlock; check · changes run at once). It NEVER
retires alone: after N unhealthy checks in a row (the dial
`SPINE_TOOL_UNHEALTHY_STRIKES`, default 3) it PROPOSES — a hold at the
interlock under its own DID, cancel the default — and the human cuts.

**The tool door dispatches** an MCP-born tool through `tools/call`
(tools.py `ToolDoor`): journaled with the service DID and the chain
(AG-7), metered like any tool, the result whole.
"""
from __future__ import annotations

import json
import os
import re
import select
import shlex
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

from . import envelope as ev, placement as _placement, services

PROTOCOL = "2025-06-18"
CLIENT = {"name": "orreth-spine", "version": "0.1.0"}
INITIALIZE_ID, LIST_ID, CALL_ID = 1, 2, 3            # fixed ids: the request bytes are canonical
GONE = "gone from the server's list"                  # the transition words (never retired by the machine)
STRIKES_DIAL, STRIKES_DEFAULT = "SPINE_TOOL_UNHEALTHY_STRIKES", 3
REF_DIAL = "SPINE_MCP_REF"                            # the rig registers the reference clock when set
REF_NAME = "clock"
REF_SERVER = Path(__file__).resolve().parents[1] / "mcp_ref" / "clock_server.py"
PASS_ENV = ("PATH", "HOME", "LANG", "LC_ALL", "TMPDIR", "PYTHONPATH", "PYTHONIOENCODING", "SYSTEMROOT")
TIMEOUT_S = 15.0


class MCPUnreachable(RuntimeError):
    """The server did not answer — the reason in words (never a value)."""


# ---- the wire: JSON-RPC 2.0, three methods (the fixture's) ---------------------------------

def request(method: str, params: dict | None, rid: int) -> dict:
    return {"jsonrpc": "2.0", "id": rid, "method": method, "params": params if params is not None else {}}


def initialize_request() -> dict:
    return request("initialize", {"protocolVersion": PROTOCOL, "capabilities": {},
                                  "clientInfo": dict(CLIENT)}, INITIALIZE_ID)


def list_request() -> dict:
    return request("tools/list", {}, LIST_ID)


def call_request(tool: str, arguments: dict) -> dict:
    return request("tools/call", {"name": tool, "arguments": dict(arguments or {})}, CALL_ID)


INITIALIZED = {"jsonrpc": "2.0", "method": "notifications/initialized"}


def request_bytes(req: dict) -> bytes:
    """What goes on the wire: the canonical bytes (0000 §3)."""
    return ev.canonical(req)


def transport_of(locator: str) -> str:
    loc = locator.strip()
    return "http" if re.match(r"^https?://", loc, re.I) else "stdio"


def resolve_locator(locator: str) -> str:
    """`env:NAME` → the value from the ground's environment, at the moment
    of use only; the value is returned to the caller that spawns or
    connects and lands nowhere else."""
    loc = locator.strip()
    if loc.startswith("env:"):
        name = loc[4:].strip()
        val = os.environ.get(name)
        if not val:
            raise MCPUnreachable(f"the locator is named by {name} and {name} is not reachable here")
        return val
    return loc


def spawn_env(secrets_with: list[str]) -> dict:
    """The child's environment: PATH and its kin, then the NAMED secrets —
    nothing else of the kernel's environment leaks down."""
    env = {k: os.environ[k] for k in PASS_ENV if os.environ.get(k)}
    for name in secrets_with:
        val = os.environ.get(name)
        if val:
            env[name] = val
    return env


class Session:
    """One MCP session over stdio or streamable HTTP: open, initialize,
    list, call, close. Nothing here ever prints a value: the reasons name
    the locator by NAME and the failure's kind."""

    def __init__(self, locator: str, secrets_with: list[str] | None = None, *, timeout: float | None = None):
        self.locator = locator
        self.transport = transport_of(resolve_locator(locator))
        self.secrets_with = list(secrets_with or [])
        self.timeout = TIMEOUT_S if timeout is None else timeout
        self._proc = None
        self._session_id = None
        self.server_info: dict = {}
        self.protocol: str | None = None

    def __enter__(self):
        return self.open()

    def __exit__(self, *exc):
        self.close()

    def open(self) -> "Session":
        if self.transport == "stdio":
            cmd = shlex.split(resolve_locator(self.locator))
            try:
                self._proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                              stderr=subprocess.DEVNULL, env=spawn_env(self.secrets_with),
                                              text=True, bufsize=1)
            except OSError as e:
                raise MCPUnreachable(f"the command could not be spawned: {type(e).__name__}: {e}")
        return self

    def close(self) -> None:
        p, self._proc = self._proc, None
        if p is not None:
            try:
                p.stdin.close()
                p.wait(timeout=2)
            except Exception:                  # noqa: BLE001
                p.kill()

    # -- the two wires --
    def _stdio(self, msg: dict, *, notify: bool = False) -> dict | None:
        p = self._proc
        if p is None or p.poll() is not None:
            raise MCPUnreachable("the server's process is not running")
        try:
            p.stdin.write(json.dumps(msg, separators=(",", ":")) + "\n")
            p.stdin.flush()
        except (BrokenPipeError, OSError):
            raise MCPUnreachable("the server closed its stdin")
        if notify:
            return None
        want = msg["id"]
        while True:
            ready, _, _ = select.select([p.stdout], [], [], self.timeout)
            if not ready:
                raise MCPUnreachable(f"no answer to {msg['method']} within {self.timeout:.0f}s")
            line = p.stdout.readline()
            if not line:
                raise MCPUnreachable(f"the server closed its stdout before answering {msg['method']}")
            try:
                got = json.loads(line)
            except ValueError:
                continue                       # a stray line is not the answer
            if got.get("id") == want:
                return got

    def _http(self, msg: dict, *, notify: bool = False) -> dict | None:
        url = resolve_locator(self.locator)
        headers = {"content-type": "application/json", "accept": "application/json, text/event-stream",
                   "mcp-protocol-version": PROTOCOL}
        if self._session_id:
            headers["mcp-session-id"] = self._session_id
        for name in self.secrets_with:          # a bearer by NAME: the first reachable secret is the token
            val = os.environ.get(name)
            if val:
                headers["authorization"] = f"Bearer {val}"
                break
        req = urllib.request.Request(url, data=json.dumps(msg).encode("utf-8"), headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as r:
                sid = r.headers.get("mcp-session-id")
                if sid:
                    self._session_id = sid
                ctype = (r.headers.get("content-type") or "").lower()
                body = r.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            raise MCPUnreachable(f"the server answered HTTP {e.code} to {msg['method']}")
        except (urllib.error.URLError, OSError, TimeoutError) as e:
            raise MCPUnreachable(f"the server could not be reached: {type(e).__name__}")
        if notify:
            return None
        if "text/event-stream" in ctype:        # SSE: the answer is the data line whose id matches
            for chunk in body.split("\n\n"):
                data = "".join(ln[5:].strip() for ln in chunk.splitlines() if ln.startswith("data:"))
                if not data:
                    continue
                try:
                    got = json.loads(data)
                except ValueError:
                    continue
                if isinstance(got, dict) and got.get("id") == msg["id"]:
                    return got
            raise MCPUnreachable(f"the event stream carried no answer to {msg['method']}")
        try:
            got = json.loads(body)
        except ValueError:
            raise MCPUnreachable(f"the answer to {msg['method']} was not JSON")
        return got

    def _rpc(self, msg: dict, *, notify: bool = False) -> dict | None:
        got = self._stdio(msg, notify=notify) if self.transport == "stdio" else self._http(msg, notify=notify)
        if got is None:
            return None
        if "error" in got:
            err = got["error"] or {}
            raise MCPUnreachable(f"{msg['method']} refused: {err.get('message', 'no words')}")
        return got.get("result") or {}

    # -- the three methods --
    def initialize(self) -> dict:
        res = self._rpc(initialize_request())
        self.server_info = dict(res.get("serverInfo") or {})
        self.protocol = res.get("protocolVersion")
        self._rpc(INITIALIZED, notify=True)
        return res

    def list_tools(self) -> list[dict]:
        res = self._rpc(list_request())
        return list(res.get("tools") or [])

    def call_tool(self, tool: str, arguments: dict) -> dict:
        return self._rpc(call_request(tool, arguments))


def listing_of(locator: str, secrets_with: list[str] | None = None, *, timeout: float | None = None) -> tuple[dict, list[dict]]:
    """initialize + tools/list in one short session: (server info, the tools)."""
    with Session(locator, secrets_with, timeout=timeout) as s:
        s.initialize()
        return {"name": s.server_info.get("name"), "version": s.server_info.get("version"),
                "protocol": s.protocol}, s.list_tools()


def result_words(res: dict) -> str:
    """A tools/call result as words: every text part, whole."""
    parts = []
    for c in res.get("content") or []:
        if isinstance(c, dict) and c.get("type") == "text":
            parts.append(str(c.get("text", "")))
        elif isinstance(c, dict):
            parts.append(f"[{c.get('type', 'part')}]")
    return "\n".join(parts) if parts else json.dumps(res.get("structuredContent") or {}, sort_keys=True)


# ---- what the ladder pins -------------------------------------------------------------------

def shelf_name(wire: str) -> str:
    """A tool's name on the shelf: the registry's law (lowercase; letters,
    digits, dashes, dots) applied to the wire name — the wire name itself
    rides the manifest for the call."""
    n = re.sub(r"[^a-z0-9.-]+", "-", wire.strip().lower()).strip("-")
    return n or "tool"


def consequence_of_annotations(t: dict) -> str:
    ann = t.get("annotations") or {}
    return "consequential" if ann.get("destructiveHint") else "routine"


def tool_manifest(server: str, t: dict) -> dict:
    """The service manifest of an MCP tool (the pin): its shelf name, the
    wire name, its words, its input schema, its class, its server."""
    return {"name": shelf_name(str(t.get("name") or "")), "tool": str(t.get("name") or ""),
            "description": str(t.get("description") or ""),
            "input_schema": t.get("inputSchema") or {"type": "object", "properties": {}},
            "consequence": consequence_of_annotations(t), "server": server}


def server_manifest(locator: str, tools: list[dict]) -> dict:
    """The server's manifest: its transport, its locator BY NAME, and the
    list it offers (name + schema + class) — sorted, so the pin reads the
    list and nothing else; a changed list is a changed pin."""
    listed = sorted(({"name": str(t.get("name") or ""), "input_schema": t.get("inputSchema") or {"type": "object", "properties": {}},
                      "consequence": consequence_of_annotations(t)} for t in tools), key=lambda x: x["name"])
    return {"transport": transport_of(resolve_locator(locator)), "locator": locator, "tools": listed}


# ---- the server and its tools on the ladder -------------------------------------------------

def tools_of(conn, server: str, *, standing_only: bool = False) -> list[dict]:
    """The tools placed under a server (their manifest names it)."""
    out = [s for s in services.listing(conn, kind="tool") if (s["manifest"] or {}).get("server") == server]
    return [s for s in out if s["state"] != "retired"] if standing_only else out


def sync_tools(conn, server: str, listed: list[dict], *, by: str, home=services._UNSET) -> dict:
    """The listing onto the shelf: a NEW tool registers (placed under the
    server), a changed schema VERSIONS it, a present one is healthy, a
    tool the server no longer lists is UNHEALTHY with the words GONE —
    never retired by the machine; a retired one is left at rest (the
    human's stop stands); a name another service wears is refused by
    name. Every step a fact."""
    out = {"new": [], "versioned": [], "present": [], "gone": [], "refused": []}
    seen = set()
    for t in listed:
        m = tool_manifest(server, t)
        name = m["name"]
        seen.add(name)
        row = services.get(conn, name)
        try:
            if row is None:
                services.register(conn, name, "tool", m, by=by, placement={"affinity": [server]}, home=home)
                out["new"].append(name)
            elif row["kind"] != "tool" or (row["manifest"] or {}).get("server") != server:
                srv = (row["manifest"] or {}).get("server")
                out["refused"].append(f"{name}: the name is worn by a {row['kind']}"
                                      + (f" under {srv}" if srv else " of the kernel's own"))
                continue
            elif row["state"] == "retired":
                out["refused"].append(f"{name}: retired by the human — left at rest (restore brings it back)")
                continue
            elif row["manifest_hash"] != services.pin(m):
                services.version(conn, name, m, by=by)
                out["versioned"].append(name)
            else:
                out["present"].append(name)
        except services.ServiceRefused as e:
            out["refused"].append(f"{name}: {e}")
            continue
        services.record_health(conn, name, True, "listed by its server; the schema matches the pin", by=by)
    for s in tools_of(conn, server, standing_only=True):
        if s["name"] not in seen:
            services.record_health(conn, s["name"], False, GONE, by=by)
            out["gone"].append(s["name"])
    return out


def register_server(conn, name: str, locator: str, *, by: str, secrets_with: list[str] | None = None,
                    placement: dict | None = None, home=services._UNSET) -> dict:
    """The keeper's register: the named secrets must be reachable FIRST
    (refused by name, nothing recorded, nothing spawned), then the server
    must answer initialize and list (else refused with the reason), then
    the server registers as kind mcp with its list as the pin and every
    listed tool lands under it."""
    name = str(name or "").strip().lower()
    if name:
        services._validate(name, "mcp", {"locator": locator})
    raw = dict(placement or {})
    raw["secrets_with"] = sorted(set(list(raw.get("secrets_with") or []) + list(secrets_with or [])))
    if locator.strip().startswith("env:"):
        raw["secrets_with"] = sorted(set(raw["secrets_with"] + [locator.strip()[4:].strip()]))
    try:
        prof = _placement.profile({"placement": raw})
    except ValueError as e:
        raise services.ServiceRefused(str(e))
    ok, reasons = _placement.honor(prof, _placement.ground_declares())
    if not ok:
        raise services.ServiceRefused(f"{name} is refused here: " + "; ".join(reasons))
    try:
        info, listed = listing_of(locator, prof["secrets_with"])
    except MCPUnreachable as e:
        raise services.ServiceRefused(f"the server at {locator_words(locator)} did not answer: {e}")
    if not name:                                          # W28 (walk #10): a server names itself —
        name = server_name(info, locator)                 # the last word of its own name, lowercased
        services._validate(name, "mcp", {"locator": locator})
    manifest = server_manifest(locator, listed)
    row = services.get(conn, name)
    if row is not None and row["kind"] == "mcp" and row["state"] != "retired" and row["manifest_hash"] != services.pin(manifest):
        server = services.version(conn, name, manifest, by=by)       # the same server, a changed list
    else:
        server = services.register(conn, name, "mcp", manifest, by=by, placement=raw, home=home)
    synced = sync_tools(conn, name, listed, by=by, home=home)
    services.record_health(conn, name, True, listing_words(info, listed, synced), by=by)
    return {"server": services.get(conn, name), "tools": synced, "info": info}


def locator_words(locator: str) -> str:
    """The locator as the shelf says it: by NAME — never a resolved value."""
    loc = locator.strip()
    if loc.startswith("env:"):
        return f"the locator named by {loc[4:].strip()}"
    return loc


def server_name(info: dict, locator: str = "") -> str:
    """W28: the shelf name a server gives itself — the last word of its
    initialize name ("orreth-clock" → "clock"), lowercased; else the last
    word of its locator."""
    import re as _re
    raw = str((info or {}).get("name") or "").strip()
    words = [w for w in _re.split(r"[^a-z0-9]+", raw.lower()) if w]
    if not words:
        words = [w for w in _re.split(r"[^a-z0-9]+", str(locator).lower()) if w and not w.endswith("py")]
    return (words[-1] if words else "server")[:40]


def listing_words(info: dict, listed: list[dict], synced: dict) -> str:
    n = len(listed)
    words = (f"initialize answered ({info.get('name') or 'unnamed'} {info.get('version') or '?'}, "
             f"protocol {info.get('protocol') or '?'}); {n} tool{'s' if n != 1 else ''} listed")
    for k in ("new", "versioned", "gone", "refused"):
        if synced.get(k):
            words += f"; {k}: " + ", ".join(synced[k])
    return words


def probe(conn, row: dict, *, by: str = services.KERNEL) -> tuple[bool, str]:
    """The mcp kind's honest probe (services.check calls it): initialize +
    tools/list; a changed list VERSIONS the server and its tools; a
    vanished tool goes unhealthy with the reason; a server that does not
    answer is unhealthy with the reason — its tools are left as they
    stand (the next answer says)."""
    m = row["manifest"] or {}
    locator = str(m.get("locator") or "")
    if not locator:
        return False, "the manifest names no locator"
    try:
        info, listed = listing_of(locator, row.get("secrets_with") or [])
    except MCPUnreachable as e:
        return False, f"did not answer: {e}"
    manifest = server_manifest(locator, listed)
    if services.pin(manifest) != row["manifest_hash"] and row["state"] != "retired":
        services.version(conn, row["name"], manifest, by=by)
    synced = sync_tools(conn, row["name"], listed, by=by)
    return True, listing_words(info, listed, synced)


def probe_tool(conn, row: dict) -> tuple[bool, str]:
    """An MCP-born tool's probe: its server lists it (the schema matching
    the pin, or re-pinned), or it is GONE."""
    m = row["manifest"] or {}
    server = services.get(conn, str(m.get("server") or ""))
    if server is None:
        return False, f"its server {m.get('server')!r} is not on the shelf"
    if server["state"] == "retired":
        return False, f"its server {server['name']} is retired"
    try:
        _info, listed = listing_of(str(server["manifest"].get("locator") or ""), server.get("secrets_with") or [])
    except MCPUnreachable as e:
        return False, f"its server {server['name']} did not answer: {e}"
    for t in listed:
        if str(t.get("name") or "") == m.get("tool"):
            fresh = tool_manifest(server["name"], t)
            if services.pin(fresh) != row["manifest_hash"]:
                services.version(conn, row["name"], fresh, by=services.KERNEL)
                return True, "listed by its server; the schema moved and was re-pinned (versioned)"
            return True, "listed by its server; the schema matches the pin"
    return False, GONE


def call(conn, row: dict, args: dict) -> str:
    """tools/call through the one door: the server named by the tool's
    manifest, a session per act, the result whole; an isError result is
    a failure the door records honestly."""
    m = row["manifest"] or {}
    server = services.get(conn, str(m.get("server") or ""))
    if server is None or server["state"] == "retired":
        raise MCPUnreachable(f"the {row['name']} tool's server {m.get('server')!r} is "
                             + ("retired" if server else "not on the shelf"))
    with Session(str(server["manifest"].get("locator") or ""), server.get("secrets_with") or []) as s:
        s.initialize()
        res = s.call_tool(str(m.get("tool") or row["name"]), args)
    words = result_words(res)
    if res.get("isError"):
        raise MCPUnreachable(words or "the server said isError with no words")
    return words


# ---- what changed on the shelf ----------------------------------------------------------------

def changes(conn, since=None, *, limit: int = 40) -> list[dict]:
    """The ladder's facts since a moment — every marker under the world's
    one shelf root (each fact hangs its marker there): at · by · the note
    in words."""
    from . import markers
    root = services.shelf_root(conn)
    cur = conn.cursor()
    cur.execute(
        "SELECT at, by_did, note FROM spine_markers WHERE scope = %s AND root = %s AND marker_id <> %s"
        " AND (%s::timestamptz IS NULL OR at > %s::timestamptz) ORDER BY at DESC LIMIT %s",
        (ev.scope(), root, root, since, since, limit))
    return [{"at": r[0].isoformat(), "by": r[1], "note": r[2] or ""} for r in cur.fetchall()][::-1]


def last_ask_at(conn, keeper_did: str, words: str = "changed") -> str | None:
    """"Since the last ask": the keeper's PREVIOUS ask of that shape (the
    newest is the one being served)."""
    cur = conn.cursor()
    cur.execute("SELECT asked_at FROM spine_asks WHERE scope = %s AND served_by = %s AND text ILIKE %s"
                " ORDER BY asked_at DESC OFFSET 1 LIMIT 1", (ev.scope(), keeper_did, f"%{words}%"))
    r = cur.fetchone()
    return r[0].isoformat() if r else None


# ---- the strikes rule: the keeper proposes, the human cuts ---------------------------------------

def strikes_n() -> int:
    try:
        return max(1, int(os.environ.get(STRIKES_DIAL) or STRIKES_DEFAULT))
    except ValueError:
        return STRIKES_DEFAULT


def last_proposal(conn, name: str) -> dict | None:
    """The keeper's newest proposal to retire this service (any status)."""
    cur = conn.cursor()
    cur.execute("SELECT ask_id, status, asked_at FROM spine_asks WHERE scope = %s AND served_by = %s"
                " AND held IS NOT NULL AND held::json->>'tool' = %s AND held::json->'args'->>'name' = %s"
                " ORDER BY asked_at DESC LIMIT 1", (ev.scope(), services.KERNEL, services.RETIRE_TOOL, name))
    r = cur.fetchone()
    return {"ask_id": r[0], "status": r[1], "asked_at": r[2].isoformat()} if r else None


def strikes(conn, name: str) -> int:
    """Unhealthy checks IN A ROW, newest first, counted since the keeper's
    last proposal about this service (a proposal resets the count — the
    human already heard it)."""
    prop = last_proposal(conn, name)
    cur = conn.cursor()
    cur.execute("SELECT ok FROM spine_service_health WHERE name = %s AND scope = %s"
                " AND (%s::timestamptz IS NULL OR at > %s::timestamptz) ORDER BY health_id DESC LIMIT 50",
                (name, ev.scope(), prop["asked_at"] if prop else None, prop["asked_at"] if prop else None))
    n = 0
    for (ok,) in cur.fetchall():
        if ok is False:
            n += 1
        else:
            break
    return n


def propose_retire(conn, name: str, *, keeper: str, n: int, session: str | None = None,
                   who: str = "the toolkeeper") -> str:
    """The keeper's proposal: a hold at the interlock under ITS OWN DID
    (the kernel's `service.retire` act, L2, cancel the default). The
    keeper never retires alone."""
    from .proof import hold_kernel_act
    row = services.get(conn, name)
    services._refuse_step(name, row["state"] if row else None, "retire")
    why = (row.get("last_health") or {}).get("detail") or "no answer"
    return hold_kernel_act(
        conn, text=f"{who} proposes retiring the {name} {row['kind']} — unhealthy across "
                   f"{n} check{'s' if n != 1 else ''} in a row ({why})",
        person=keeper, tool=services.RETIRE_TOOL, args={"name": name},
        level=services.RETIRE_LEVEL, session=session, cls=services.RETIRE_CLASS)


def proposals(conn, *, keeper: str, n: int | None = None, kinds: tuple | None = None,
              who: str = "the toolkeeper") -> list[dict]:
    """Every standing service unhealthy across N checks in a row earns ONE
    proposal (none while one waits at the interlock). P6.5 sp3: each
    keeper proposes for ITS kinds — the toolkeeper for everything but
    minds, the stablekeeper (`who`) for minds."""
    n = n or strikes_n()
    out = []
    for s in services.listing(conn):
        if s["state"] == "retired":
            continue
        if kinds is not None and s["kind"] not in kinds:
            continue
        if kinds is None and s["kind"] == "mind":
            continue
        k = strikes(conn, s["name"])
        if k < n:
            continue
        prop = last_proposal(conn, s["name"])
        if prop and prop["status"] == "awaiting-confirm":
            continue
        out.append({"name": s["name"], "kind": s["kind"], "strikes": k,
                    "held": propose_retire(conn, s["name"], keeper=keeper, n=k, who=who)})
    return out


def keeper_beat(conn, *, keeper: str, n: int | None = None) -> dict:
    """The keeper's beat (the rig runs it on the scheduler's clock under
    the keeper's DID): every standing MCP server probed — its tools
    synced, the gone named — then the strikes rule."""
    checked = services.check_all(conn, kind="mcp", by=keeper)
    return {"checked": checked, "proposed": proposals(conn, keeper=keeper, n=n)}


# ---- the reference server, on the rig by the dial ---------------------------------------------

def ref_locator() -> str:
    return f"{sys.executable} {REF_SERVER}"


def ref_on(env: dict | None = None) -> bool:
    return str((os.environ if env is None else env).get(REF_DIAL) or "").strip().lower() in ("1", "true", "yes", "on")


def seed_ref(conn, *, by: str = services.KERNEL, home=services._UNSET) -> dict:
    """The reference clock registered as the `clock` server (its `now`
    and `echo` on the shelf) — idempotent: the same selves every boot."""
    return register_server(conn, REF_NAME, ref_locator(), by=by, secrets_with=["SPINE_MCP_REF_TOOLS"]
                           if os.environ.get("SPINE_MCP_REF_TOOLS") else None, home=home)
