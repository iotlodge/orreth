# PROVENANCE: console worker by Fable 5; charlotte's farm duties added by
# Fable 5 (claude-fable-5) — 0018, the Tool Farm · 2026-07-05
"""The console worker — cognition behind the human's queue (0014 · 0006 · 0018).

Watches every floor's request queue and carries three residents' duties, keys staying
here in cognition (the plane verifies, never signs):

  · gather X  — the librarian: finds a SERVING search source on the Farm, meters the
    call, admits the findings as signed memories (quarantined at 0.0000) under the
    service's DID. No serving source → an honest refusal, never a silent nothing.
  · join      — becky's door: an agent asks to join the field; becky mints a
    root-chained retrieve lease for its DID and resolves the request with the token.
  · service   — charlotte, the farm keeper (0018): verifies staged plantings (probe,
    fetch manifest, pin hash), attests on human approval, heartbeats the toolshed,
    ages leases out, guards the rug-pull door on rejoin, and writes every lifecycle
    event as a signed MemoryRecord — the service's worldline. Nothing self-attests:
    the tool never wrote "SOME PIG" about itself.

Residents persist their seeds under ~/.orreth/residents/ — a keypair is a self, and
a self survives the process (0002 §1). Charlotte's ledger (~/.orreth/farm/) replants
the toolshed after a daemon restart: the ledger seeds, the daemon holds live state,
the worldline in the record store is the history that outlives both.

    uv run python console_worker.py [join_port]      (leave running while you use the Console)
"""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

from dotenv import load_dotenv

from orreth_sim import crypto
from orreth_sim.identity import NOW, Becky, Nanda
from orreth_sim.node import make_memory
from smoke_orrethd import root_keypair

load_dotenv(Path(__file__).resolve().parents[2] / ".env")
sys.stdout.reconfigure(line_buffering=True)  # nohup'd by dev.sh — block-buffering leaves the log empty
try:
    os.setsid()  # own session: a Ctrl-C aimed at the launching script must not kill becky
except OSError:
    pass

FLOORS = [4500, 4501, 4502]                  # every floor's queue and toolshed
JOIN_PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 4502
SCOPE = "u:demo/e:cloud/f:prod"              # becky's floor — joins bind here
HOME = Path.home() / ".orreth"
BEAT_EVERY = 6                               # seconds between heartbeat rounds
MISSES_TO_DROP = 3                           # silence ages the lease out (SPIFFE's lesson)


def _seed(name: str) -> crypto.KeyPair:
    """A resident's key survives the process — load_or_create under ~/.orreth/residents/."""
    nest = HOME / "residents"
    nest.mkdir(parents=True, exist_ok=True)
    path = nest / f"{name}.seed"
    if path.exists():
        return crypto.KeyPair(path.read_bytes())
    kp = crypto.KeyPair()
    path.write_bytes(kp.seed)
    path.chmod(0o600)
    return kp


LIB = _seed("librarian")                     # the librarian's identity
LIB_DID = crypto.did_key_for(LIB.public)
CHA = _seed("charlotte")                     # charlotte, the farm keeper (0018 §5)
CHA_DID = crypto.did_key_for(CHA.public)

# becky, chained from the pinned root — the only authority that can mint a joining lease
_NANDA = Nanda()
_ROOT = Becky("u:demo", _NANDA, universe_name="demo", kp=root_keypair())
_BECKY = Becky(SCOPE, _NANDA, parent=_ROOT)


def grant_lease(did: str) -> dict:
    """A retrieve-self lease for a joining agent — attenuated to this floor, root-chained."""
    return _BECKY.issue_token(did, SCOPE, [{"action": "retrieve", "space": "self"}])


def call(port: int, method: str, path: str, payload=None):
    req = urllib.request.Request(f"http://127.0.0.1:{port}{path}", method=method,
        data=json.dumps(payload).encode() if payload is not None else None,
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=8) as r:
        b = r.read()
        return json.loads(b) if b[:1] in (b"{", b"[") else b


# ---------------------------------------------------------------- the farm keeper (0018)

def ledger_path(scope: str) -> Path:
    nest = HOME / "farm" / scope.replace("/", "~")
    nest.mkdir(parents=True, exist_ok=True)
    return nest / "services.json"


def ledger_load(scope: str) -> dict:
    p = ledger_path(scope)
    return json.loads(p.read_text()) if p.exists() else {}


def ledger_save(scope: str, data: dict) -> None:
    ledger_path(scope).write_text(json.dumps(data, indent=1, sort_keys=True))


def probe(endpoint: str) -> bool:
    """Alive = the server ANSWERED (any HTTP status); dead = the wire went quiet."""
    try:
        urllib.request.urlopen(urllib.request.Request(endpoint, method="GET"), timeout=4)
        return True
    except urllib.error.HTTPError:
        return True
    except Exception:
        return False


def mcp_tools(endpoint: str) -> list | None:
    """Enumerate a streamable-HTTP MCP server's tools — the manifest we pin (0018 §1)."""
    session = None

    def rpc(body: dict):
        nonlocal session
        headers = {"Content-Type": "application/json",
                   "Accept": "application/json, text/event-stream"}
        if session:
            headers["Mcp-Session-Id"] = session
        req = urllib.request.Request(endpoint, method="POST",
                                     data=json.dumps(body).encode(), headers=headers)
        with urllib.request.urlopen(req, timeout=8) as r:
            session = r.headers.get("Mcp-Session-Id") or session
            raw = r.read().decode()
        for line in raw.splitlines():            # unwrap SSE framing if the server streams
            if line.startswith("data:"):
                raw = line[5:].strip()
                break
        return json.loads(raw) if raw else {}

    try:
        rpc({"jsonrpc": "2.0", "id": 1, "method": "initialize",
             "params": {"protocolVersion": "2025-03-26", "capabilities": {},
                        "clientInfo": {"name": "orreth-charlotte", "version": "0.1"}}})
        try:
            rpc({"jsonrpc": "2.0", "method": "notifications/initialized"})
        except Exception:
            pass
        tools = rpc({"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}})
        return sorted(
            [{"name": t["name"], "description": t.get("description", ""),
              "schema": t.get("inputSchema", {})} for t in tools["result"]["tools"]],
            key=lambda t: t["name"])
    except Exception:
        return None


def fetch_manifest(svc: dict) -> list | None:
    """MCP servers are enumerated live; declared manifests stand for plain HTTP tools."""
    if svc.get("kind") == "mcp":
        return mcp_tools(svc["endpoint"])
    return svc.get("manifest") or []


def service_did(req: dict) -> str:
    """Vendor-anchored did:web from the endpoint's domain (0014 §2); explicit did wins."""
    if req.get("did"):
        return req["did"]
    host = req.get("endpoint", "").split("//")[-1].split("/")[0].split(":")[0]
    if host and "." in host and not host.replace(".", "").isdigit():
        return f"did:web:{host.removeprefix('api.').removeprefix('mcp.')}"
    kp = crypto.KeyPair()                        # a local tool with no domain: cheap leaf
    return crypto.did_key_for(kp.public)


def worldline(port: int, scope: str, svc: dict, event: str, **extra) -> None:
    """Every lifecycle transition is a signed MemoryRecord — the identity tells the
    universe, in time (0018 §4). Charlotte authors; the service never self-attests."""
    body = {"service": svc["name"], "did": svc.get("did", ""), "event": event,
            "state": svc.get("state", ""), "manifest_hash": svc.get("manifest_hash", ""),
            "at": NOW(), **extra}
    rec = make_memory({"did": CHA_DID, "scope": scope}, CHA, scope, body,
                      kind="episodic", tags=["service", svc["name"]])
    try:
        call(port, "POST", "/records", rec)
    except Exception as e:
        print(f"    (worldline write failed: {e})")


class FarmKeeper:
    """Charlotte's round: verify staged plantings, attest approvals, heartbeat the
    toolshed, age silent leases out, guard the rug-pull door, replant after restarts."""

    def __init__(self) -> None:
        self.misses: dict[tuple[int, str], int] = {}
        self.last_beat = 0.0

    # ---- the queue: plant · decom · reapprove -----------------------------------------
    def on_service_request(self, port: int, scope: str, r: dict) -> bool:
        """Returns True when the request reached a resting state (done/denied)."""
        action, status, name = r.get("action", "plant"), r.get("status"), r.get("name", "")
        if status == "pending" and action in ("decom", "reapprove"):
            # nothing to probe — consequence waits for the human (0012)
            call(port, "POST", "/requests/resolve", {"id": r["id"], "status": "staged"})
            return False
        if status == "pending" and action == "plant":
            svc = {"name": name, "did": service_did(r), "kind": r.get("svc_kind", "http"),
                   "endpoint": r.get("endpoint", ""), "transport": r.get("transport", "rest"),
                   "manifest": r.get("manifest") or []}
            manifest = fetch_manifest(svc)
            alive = probe(svc["endpoint"]) if svc["endpoint"] else False
            svc["manifest"] = manifest or svc["manifest"]
            planted = call(port, "POST", "/farm/plant", svc)
            worldline(port, scope, planted, "planted",
                      probed={"alive": alive, "tools": len(svc["manifest"])})
            call(port, "POST", "/requests/resolve",
                 {"id": r["id"], "status": "staged",
                  "result": {"did": planted["did"], "manifest_hash": planted["manifest_hash"],
                             "alive": alive, "tools": len(svc["manifest"])}})
            print(f"  ↳ staged planting {name}: alive={alive}, "
                  f"{len(svc['manifest'])} tool(s), pinned {planted['manifest_hash'][:18]}…")
            return False
        if status == "approved":
            if action in ("plant", "reapprove"):
                op = "attest" if action == "plant" else "reapprove"
                farm = {s["name"]: s for s in call(port, "GET", "/farm")["services"]}
                manifest = farm.get(name, {}).get("manifest", [])
                svc = call(port, "POST", "/farm/state",
                           {"name": name, "op": op, "manifest": manifest})
                worldline(port, scope, svc, "attested" if op == "attest" else "re-attested")
                led = ledger_load(scope)
                led[name] = {k: svc[k] for k in ("name", "did", "kind", "endpoint",
                                                 "transport", "manifest", "manifest_hash")}
                ledger_save(scope, led)
                print(f"  ↳ attested {name} — probation begins (beats earn serving)")
            elif action == "decom":
                discredit = bool(r.get("discredit"))
                svc = call(port, "POST", "/farm/state",
                           {"name": name, "op": "decom",
                            "reason": r.get("reason", ""), "discredit": discredit})
                worldline(port, scope, svc, "decommissioned",
                          reason=r.get("reason", ""), discredit=discredit)
                if discredit:
                    # the source registry flip + 0014 §4 lineage walk land with the
                    # librarian organ (0015); the discredit is on the record TODAY
                    worldline(port, scope, svc, "discredited",
                              note="knowledge recall staged (0014 §4)")
                led = ledger_load(scope)
                led.pop(name, None)
                ledger_save(scope, led)
                print(f"  ↳ decommissioned {name}" + (" · source discredited" if discredit else ""))
            call(port, "POST", "/requests/resolve", {"id": r["id"], "status": "done"})
            return True
        if status == "denied":
            try:
                svc = call(port, "POST", "/farm/state", {"name": name, "op": "decom",
                                                         "reason": "denied at the gate"})
                worldline(port, scope, svc, "denied")
            except Exception:
                pass
            # a denied service leaves the ledger too — replant must never resurrect
            # what a human refused (the ledger seeds only the approved)
            led = ledger_load(scope)
            led.pop(name, None)
            ledger_save(scope, led)
            call(port, "POST", "/requests/resolve", {"id": r["id"], "status": "done"})
            print(f"  ↳ denied {name} — never served")
            return True
        return False

    # ---- the round: heartbeats, drops, rejoins, replants -------------------------------
    def tend(self, port: int, scope: str) -> None:
        try:
            farm = call(port, "GET", "/farm")["services"]
        except Exception:
            return
        local = [s for s in farm if s.get("floor") == scope]
        self.replant(port, scope, {s["name"] for s in local})
        for svc in local:
            key, state = (port, svc["name"]), svc["state"]
            if state in ("probation", "serving"):
                if probe(svc["endpoint"]):
                    self.misses[key] = 0
                    beat = call(port, "POST", "/farm/hello", {"name": svc["name"]})
                    if beat.get("transition", {}).get("to") == "serving":
                        worldline(port, scope, beat, "serving",
                                  earned_after=beat.get("beats"))
                        print(f"  ↳ {svc['name']} earned its place — serving")
                else:
                    self.misses[key] = self.misses.get(key, 0) + 1
                    if self.misses[key] >= MISSES_TO_DROP:
                        dropped = call(port, "POST", "/farm/state",
                                       {"name": svc["name"], "op": "expire"})
                        worldline(port, scope, dropped, "dropped",
                                  reason=f"{self.misses[key]} missed heartbeats")
                        print(f"  ↳ {svc['name']} dropped — the lease aged out")
            elif state == "dropped" and probe(svc["endpoint"]):
                manifest = fetch_manifest(svc)
                if manifest is None:
                    continue                     # answered but not enumerable yet
                back = call(port, "POST", "/farm/state",
                            {"name": svc["name"], "op": "rejoin", "manifest": manifest})
                if back["state"] == "serving":
                    worldline(port, scope, back, "rejoined")
                    print(f"  ↳ {svc['name']} rejoined — same manifest, same self")
                else:                            # the rug-pull door (0018 §2)
                    worldline(port, scope, back, "manifest-changed",
                              pinned=back["manifest_hash"], seen=back.get("proposed_hash"))
                    call(port, "POST", "/requests",
                         {"kind": "service", "action": "reapprove", "name": svc["name"],
                          "text": f"{svc['name']} came back CHANGED — re-approve its new manifest?"})
                    print(f"  ↳ {svc['name']} quarantined — its manifest changed while it was gone")

    def replant(self, port: int, scope: str, present: set) -> None:
        """The daemon may die; the toolshed doesn't. The ledger re-seeds live state,
        and the worldline shows the restart honestly."""
        for name, svc in ledger_load(scope).items():
            if name in present:
                continue
            try:
                call(port, "POST", "/farm/plant", svc)
                call(port, "POST", "/farm/state",
                     {"name": name, "op": "attest", "manifest": svc.get("manifest", [])})
                worldline(port, scope, svc, "replanted",
                          note="daemon restarted; approval is durable in the ledger")
                print(f"  ↳ replanted {name} after a daemon restart")
            except Exception as e:
                print(f"    (replant {name} failed: {e})")


KEEPER = FarmKeeper()


# ---------------------------------------------------------------- the librarian (0014)

def farm_search_source(port: int) -> dict | None:
    """The Farm's serving search source, if any — gather consumes governed resources."""
    try:
        for s in call(port, "GET", "/farm")["services"]:
            if s["state"] == "serving" and any(
                    "search" in t.get("name", "") for t in s.get("manifest", [])):
                return s
    except Exception:
        pass
    return None


def tavily(q: str, n: int = 3) -> list:
    if not os.environ.get("TAVILY_API_KEY"):
        return [{"title": f"(no TAVILY_API_KEY) placeholder finding on {q}",
                 "content": "set the key to gather real sourced knowledge", "url": "local://demo"}]
    req = urllib.request.Request("https://api.tavily.com/search", method="POST",
        data=json.dumps({"api_key": os.environ["TAVILY_API_KEY"], "query": q,
                         "max_results": n}).encode(), headers={"Content-Type": "application/json"})
    return json.loads(urllib.request.urlopen(req).read())["results"]


def gather(port: int, scope: str, text: str) -> str:
    src = farm_search_source(port)
    if src is None:
        return ("nothing gathered — the Farm has no serving search source. "
                "Plant one in the Farm tab (Tavily preset).")
    t0 = time.time()
    results = tavily(text)
    call(port, "POST", "/farm/meter", {"name": src["name"], "caller": LIB_DID,
                                       "ms": int((time.time() - t0) * 1000)})
    agent = {"did": LIB_DID, "scope": scope}
    for r in results:
        body = {"knowledge": f"{r['title']} — {r['content'][:120]}",
                "source": {"did": src["did"], "ref": r.get("url", "")},
                "state": "untrusted", "intent": text}
        rec = make_memory(agent, LIB, scope, body, kind="semantic",
                          tags=["knowledge", "gathered"],
                          provenance_class="ingested-archive")
        call(port, "POST", "/records", rec)
    return f"admitted to the Window — {len(results)} finding(s) via {src['name']}, quarantined at 0.0000"


# ---------------------------------------------------------------- the round

def main() -> None:
    print(f"console worker · librarian {LIB_DID[:20]}… · charlotte {CHA_DID[:20]}… "
          f"· becky's door on :{JOIN_PORT} · tending floors {FLOORS}")
    handled: set[tuple] = set()               # (port, id, at, status): each step acted once
    scopes: dict[int, str] = {}
    while True:
        beat_due = time.time() - KEEPER.last_beat >= BEAT_EVERY
        for port in FLOORS:
            try:
                if port not in scopes:
                    scopes[port] = call(port, "GET", "/health")["scope"]
                scope = scopes[port]
                for r in call(port, "GET", "/requests").get("requests", []):
                    key = (port, r.get("id"), r.get("at", ""), r.get("status"))
                    if key in handled:
                        continue
                    if r.get("kind") == "gather" and r.get("status") == "pending":
                        handled.add(key)
                        print(f"  ↳ dispatch {r['id']}: gather “{r['text']}” on {scope}")
                        result = gather(port, scope, r["text"])
                        call(port, "POST", "/requests/resolve",
                             {"id": r["id"], "status": "done", "result": result})
                        print(f"    ✓ {result}")
                    elif (r.get("kind") == "join" and r.get("did")
                          and r.get("status") == "pending" and port == JOIN_PORT):
                        handled.add(key)
                        print(f"  ↳ join {r['id']}: {r.get('name','?')} "
                              f"({r['did'][:22]}…) as {r.get('role','workforce')}")
                        lease = grant_lease(r["did"])
                        call(port, "POST", "/requests/resolve",
                             {"id": r["id"], "status": "done",
                              "result": {"token": lease, "scope": SCOPE,
                                         "granted_by": _BECKY.did}})
                        print(f"    ✓ lease granted — welcome to {SCOPE}")
                    elif r.get("kind") == "service":
                        if KEEPER.on_service_request(port, scope, r) or r.get("status") == "staged":
                            handled.add(key)
                if beat_due:
                    KEEPER.tend(port, scope)
            except Exception as e:
                scopes.pop(port, None)
                print(f"  (floor :{port} unreachable…)", e)
        if beat_due:
            KEEPER.last_beat = time.time()
        time.sleep(2)


if __name__ == "__main__":
    main()
