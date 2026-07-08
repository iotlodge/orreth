# PROVENANCE: console worker by Fable 5; charlotte's farm duties added by
# Fable 5 (claude-fable-5) — 0018, the Tool Farm · 2026-07-05;
# ada's stable duties added by Fable 5 (claude-fable-5) — 0019, the Stable · 2026-07-06;
# the parlor desk added by Fable 5 (claude-fable-5) — 0020, the Parlor · 2026-07-07
"""The console worker — cognition behind the human's queue (0014 · 0006 · 0018 · 0019 · 0020).

Watches every floor's request queue and carries the residents' duties, keys staying
here in cognition (the plane verifies, never signs):

  · gather X  — the librarian: finds a SERVING search source on the Farm, meters the
    call, admits the findings as signed memories (quarantined at 0.0000) under the
    service's DID. No serving source → an honest refusal, never a silent nothing.
  · recall    — the librarian's 0014 §4 walk: when a source is discredited at the
    gate, charlotte hands the recall to the queue and the librarian re-versions
    every entry from that source — and everything derived from those — to
    'recalled'. Annotate-never-rewrite; the poison visibly dead in the Window.
  · join      — becky's door, HARDENED (JB's lock 2026-07-07): an agent asks to
    join; becky challenges it to sign a nonce (key control proven, names bind to
    real keys), stages the join for the HUMAN gate (0012 — consequence waits), and
    mints the root-chained lease only after both. Approval without proof earns a
    fresh challenge, never a token.
  · service   — charlotte, the farm keeper (0018): verifies staged plantings (probe,
    fetch manifest, pin hash), attests on human approval, heartbeats the toolshed,
    ages leases out, guards the rug-pull door on rejoin, and writes every lifecycle
    event as a signed MemoryRecord — the service's worldline. Nothing self-attests:
    the tool never wrote "SOME PIG" about itself.
  · mind      — ada, the wrangler (0019): probes the catalog on a staged saddle and
    pins the DEAL (pricing/context bytes), attests on human approval, canaries rookie
    minds through the governed gateway (metered under her own DID — residents think
    on-meter too), syncs the market for price drift and announced expiries, and
    stages recommendations instead of letting a sunset become an outage.
  · parlor    — the audience room (0020): humans never read the world, they ask it.
    A resident receives the caller, fetches with its OWN authority, answers grounded
    (voiced through one governed, metered thought when the floor is fueled), and
    signs the exchange onto the spacetime window. Unembodied organs receive too,
    and say honestly that they have no voice yet.

Residents persist their seeds under ~/.orreth/residents/ — a keypair is a self, and
a self survives the process (0002 §1). Charlotte's ledger (~/.orreth/farm/) replants
the toolshed after a daemon restart, ada's (~/.orreth/stable/) re-saddles the stable:
the ledger seeds, the daemon holds live state, the worldline in the record store is
the history that outlives both.

    uv run python console_worker.py [join_port]      (leave running while you use the Console)
"""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from dotenv import load_dotenv

from orreth_sim import crypto, parlor
from orreth_sim.identity import NOW, Becky, Nanda
from orreth_sim.joindoor import JoinDesk
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
ADA = _seed("ada")                           # ada, the wrangler (0019 §3)
ADA_DID = crypto.did_key_for(ADA.public)

# becky, chained from the pinned root — the only authority that can mint a joining lease
_NANDA = Nanda()
_ROOT = Becky("u:demo", _NANDA, universe_name="demo", kp=root_keypair())
_BECKY = Becky(SCOPE, _NANDA, parent=_ROOT)


def grant_lease(did: str) -> dict:
    """A retrieve-self lease for a joining agent — attenuated to this floor, root-chained."""
    return _BECKY.issue_token(did, SCOPE, [{"action": "retrieve", "space": "self"}])


# the desk at the door: challenge → prove → human gate → lease (JB's lock 2026-07-07)
JOINDOOR = JoinDesk(grant=grant_lease)


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
                    # separation of duties: charlotte discredits the SOURCE; the
                    # KNOWLEDGE recall is the librarian's walk (0014 §4). The handoff
                    # rides the queue — visible, auditable, no second gate (the human
                    # already approved the discredit).
                    worldline(port, scope, svc, "discredited",
                              note="recall handed to the librarian (0014 §4)")
                    call(port, "POST", "/requests",
                         {"kind": "recall", "source_did": svc.get("did", ""),
                          "service": name,
                          "reason": r.get("reason", "") or "source discredited",
                          "text": f"recall knowledge from discredited {name}"})
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


# ---------------------------------------------------------------- the wrangler (0019)

CATALOG_TTL = 300                            # seconds the market snapshot stays fresh
EOL_HORIZON_DAYS = 30                        # inside this window an expiry burns
MIND_DIDS = {"anthropic": "did:web:anthropic.com", "openai": "did:web:openai.com",
             "openrouter": "did:web:openrouter.ai", "google": "did:web:google.com",
             "mistralai": "did:web:mistral.ai"}


def stable_ledger_path(scope: str) -> Path:
    nest = HOME / "stable" / scope.replace("/", "~")
    nest.mkdir(parents=True, exist_ok=True)
    return nest / "minds.json"


def stable_ledger_load(scope: str) -> dict:
    p = stable_ledger_path(scope)
    return json.loads(p.read_text()) if p.exists() else {}


def stable_ledger_save(scope: str, data: dict) -> None:
    stable_ledger_path(scope).write_text(json.dumps(data, indent=1, sort_keys=True))


def openrouter_catalog() -> list[dict]:
    """The market, read freely: OpenRouter's public list is INTEL for every stall,
    whatever route carries the call (0019 §1). Routing stays LiteLLM-direct on the
    floor's own keys by default. Cached on disk; a stale snapshot beats none."""
    cache = HOME / "stable" / "catalog.json"
    cache.parent.mkdir(parents=True, exist_ok=True)
    if cache.exists() and time.time() - cache.stat().st_mtime < CATALOG_TTL:
        return json.loads(cache.read_text())
    try:
        raw = json.loads(urllib.request.urlopen(urllib.request.Request(
            "https://openrouter.ai/api/v1/models"), timeout=15).read())
        cat = [{"id": m["id"], "provider": m["id"].split("/")[0],
                "pricing": m.get("pricing", {}),
                "context_length": m.get("context_length"),
                "modalities": (m.get("architecture") or {}).get("input_modalities", []),
                "created": m.get("created"),
                "expires_at": m.get("expiration_date")}
               for m in raw.get("data", [])]
        cache.write_text(json.dumps(cat))
        return cat
    except Exception:
        return json.loads(cache.read_text()) if cache.exists() else []


def deal(entry: dict) -> dict:
    """The manifest ada pins: the DEAL, not the name — pricing, context, modalities.
    Any byte of it moving under the pin is drift, and drift walks the rug-pull door."""
    return {"pricing": entry.get("pricing", {}),
            "context_length": entry.get("context_length"),
            "modalities": entry.get("modalities", [])}


def mind_did(provider: str) -> str:
    return MIND_DIDS.get(provider, f"did:web:{provider}")


def mindline(port: int, scope: str, stall: dict, event: str, **extra) -> None:
    """Every lifecycle transition is a signed MemoryRecord — the stall's worldline.
    Ada authors; the model (and its provider) never self-attests."""
    body = {"mind": stall.get("id", ""), "did": stall.get("did", ""), "event": event,
            "state": stall.get("state", ""), "manifest_hash": stall.get("manifest_hash", ""),
            "at": NOW(), **extra}
    rec = make_memory({"did": ADA_DID, "scope": scope}, ADA, scope, body,
                      kind="episodic", tags=["mind", stall.get("id", "")])
    try:
        call(port, "POST", "/records", rec)
    except Exception as e:
        print(f"    (mindline write failed: {e})")


def recommend(old: dict, stalls: list, catalog: list) -> dict | None:
    """The replacement pick: a stall already serving the class wins outright; else the
    catalog ranks by price distance then recency, never the next casualty (0019 §7)."""
    for s in stalls:
        if s["id"] != old["id"] and s.get("class") == old.get("class") \
                and s.get("state") == "available":
            return {"id": s["id"], "why": "already serving this class", "in_stable": True}
    old_p = float((old.get("manifest") or {}).get("pricing", {}).get("prompt") or 0)
    live = [c for c in catalog if c["id"] != old["id"] and not c.get("expires_at")]
    if not live:
        return None
    best = min(live, key=lambda c: (
        abs(float((c.get("pricing") or {}).get("prompt") or 0) - old_p),
        -(c.get("created") or 0)))
    return {"id": best["id"], "provider": best.get("provider", ""),
            "why": "nearest price, newest catalog entry", "in_stable": False,
            "pricing": best.get("pricing", {}),
            "context_length": best.get("context_length"),
            "modalities": best.get("modalities", []), "created": best.get("created")}


def governed_ping(port: int, klass: str) -> dict | None:
    """One tiny real thought through ada's OWN gateway — authorize, call, meter, all
    under her DID. Residents think on-meter too (0019 §4); silently skipped when no
    provider key or litellm is around (canary then rests on verified syncs alone)."""
    try:
        import litellm  # noqa: F401
    except Exception:
        return None
    if not (os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("OPENAI_API_KEY")):
        return None
    try:
        token = _BECKY.issue_token(ADA_DID, SCOPE, [{"action": "retrieve", "space": "self"}],
                                   budget={"tokens": 50000})
        est = 40
        grant = call(port, "POST", "/model/authorize",
                     {"token": token, "class": klass, "est_tokens": est})
        import litellm
        resp = litellm.completion(model=grant["model"],
                                  messages=[{"role": "user", "content": "ping"}],
                                  max_tokens=1)
        tokens = resp.usage.total_tokens
        try:
            usd = litellm.completion_cost(completion_response=resp)
        except Exception:
            usd = 0.0
        call(port, "POST", "/model/meter",
             {"subject": grant["subject"], "est_tokens": est, "tokens": tokens,
              "usd": round(usd, 6), "model": grant["model"], "class": klass})
        return {"model": grant["model"], "tokens": tokens}
    except Exception:
        return None


class Wrangler:
    """Ada's round: probe staged saddles, attest approvals, canary rookie minds,
    sync the market for drift and expiries, stage recommendations, re-saddle after
    restarts. The plane refuses illegal moves; ada only ever proposes legal ones."""

    def __init__(self) -> None:
        self.pinged: set[str] = set()         # one governed canary thought per mind

    def _local(self, port: int, scope: str) -> list[dict]:
        return [s for s in call(port, "GET", "/stable")["stalls"]
                if s.get("floor") == scope]

    # ---- the queue: saddle · reapprove · retire · swap ---------------------------------
    def on_mind_request(self, port: int, scope: str, r: dict) -> bool:
        """Returns True when the request reached a resting state (done/denied)."""
        action, status, mid = r.get("action", "saddle"), r.get("status"), r.get("mind", "")
        if status == "pending" and action in ("reapprove", "retire", "swap"):
            # nothing to probe — consequence waits for the human (0012)
            call(port, "POST", "/requests/resolve", {"id": r["id"], "status": "staged"})
            return False
        if status == "pending" and action == "saddle":
            entry = next((c for c in openrouter_catalog() if c["id"] == mid), None)
            manifest = deal(entry) if entry else (r.get("manifest") or {})
            provider = r.get("provider") or mid.split("/")[0]
            stall = call(port, "POST", "/stable/saddle", {
                "id": mid, "provider": provider,
                "route": r.get("route", "litellm-direct"),
                "did": mind_did(provider), "class": r.get("class", "medium"),
                "manifest": manifest,
                "expires_at": (entry or {}).get("expires_at") or r.get("expires_at")})
            mindline(port, scope, stall, "saddled",
                     in_catalog=bool(entry),
                     pricing=manifest.get("pricing", {}))
            call(port, "POST", "/requests/resolve",
                 {"id": r["id"], "status": "staged",
                  "result": {"manifest_hash": stall["manifest_hash"],
                             "in_catalog": bool(entry),
                             "expires_at": stall.get("expires_at"),
                             "pricing": manifest.get("pricing", {})}})
            print(f"  ↳ staged saddle {mid}: catalog={bool(entry)}, "
                  f"pinned {stall['manifest_hash'][:18]}…")
            return False
        if status == "approved":
            if action == "saddle":
                stall = next((s for s in self._local(port, scope) if s["id"] == mid), {})
                out = call(port, "POST", "/stable/state",
                           {"id": mid, "op": "attest",
                            "manifest": stall.get("manifest", {}),
                            "expires_at": stall.get("expires_at")})
                mindline(port, scope, out, "attested")
                led = stable_ledger_load(scope)
                led[mid] = {k: out.get(k) for k in ("id", "provider", "route", "class",
                                                    "did", "manifest", "manifest_hash",
                                                    "expires_at")}
                stable_ledger_save(scope, led)
                print(f"  ↳ attested {mid} — canary begins (governed beats earn available)")
            elif action == "reapprove":
                out = call(port, "POST", "/stable/state", {"id": mid, "op": "reapprove"})
                mindline(port, scope, out, "re-approved", pinned=out.get("manifest_hash"))
                led = stable_ledger_load(scope)
                if mid in led:
                    led[mid]["manifest"] = out.get("manifest")
                    led[mid]["manifest_hash"] = out.get("manifest_hash")
                    stable_ledger_save(scope, led)
                print(f"  ↳ re-approved {mid} — the new deal is the pin now")
            elif action == "swap":
                rep = r.get("replacement") or {}
                rep_id = rep.get("id", "")
                if rep_id and not rep.get("in_stable"):
                    provider = rep.get("provider") or rep_id.split("/")[0]
                    new = call(port, "POST", "/stable/saddle", {
                        "id": rep_id, "provider": provider,
                        "route": r.get("route", "litellm-direct"),
                        "did": mind_did(provider),
                        "class": r.get("class") or "medium",
                        "manifest": deal(rep), "expires_at": rep.get("expires_at")})
                    mindline(port, scope, new, "saddled", reason=f"succeeds {mid}")
                    out = call(port, "POST", "/stable/state",
                               {"id": rep_id, "op": "attest", "manifest": deal(rep)})
                    mindline(port, scope, out, "attested")
                    led = stable_ledger_load(scope)
                    led[rep_id] = {k: out.get(k) for k in ("id", "provider", "route",
                                                           "class", "did", "manifest",
                                                           "manifest_hash", "expires_at")}
                    stable_ledger_save(scope, led)
                old = call(port, "POST", "/stable/state",
                           {"id": mid, "op": "retire",
                            "reason": f"superseded by {rep_id or 'its class'}"})
                mindline(port, scope, old, "retired", superseded_by=rep_id)
                led = stable_ledger_load(scope)
                led.pop(mid, None)
                stable_ledger_save(scope, led)
                print(f"  ↳ swapped {mid} → {rep_id or '(existing stall)'} — no outage, by appointment")
            elif action == "retire":
                out = call(port, "POST", "/stable/state",
                           {"id": mid, "op": "retire", "reason": r.get("reason", "")})
                mindline(port, scope, out, "retired", reason=r.get("reason", ""))
                led = stable_ledger_load(scope)
                led.pop(mid, None)
                stable_ledger_save(scope, led)
                print(f"  ↳ retired {mid} — sunset; never served again")
            call(port, "POST", "/requests/resolve", {"id": r["id"], "status": "done"})
            return True
        if status == "denied":
            try:
                out = call(port, "POST", "/stable/state",
                           {"id": mid, "op": "retire", "reason": "denied at the gate"})
                mindline(port, scope, out, "denied")
            except Exception:
                pass
            led = stable_ledger_load(scope)
            led.pop(mid, None)
            stable_ledger_save(scope, led)
            call(port, "POST", "/requests/resolve", {"id": r["id"], "status": "done"})
            print(f"  ↳ denied {mid} — never served")
            return True
        return False

    # ---- the round: canary beats, market sync, EOL scan, re-saddles ---------------------
    def sync(self, port: int, scope: str) -> None:
        try:
            stalls = self._local(port, scope)
        except Exception:
            return
        led = stable_ledger_load(scope)
        if not stalls and not led:
            return                            # a floor with no stable stays quiet
        self.restable(port, scope, {s["id"] for s in stalls})
        cat = openrouter_catalog()
        by_id = {c["id"]: c for c in cat}
        from datetime import date, timedelta
        edge = (date.fromisoformat(NOW()[:10]) + timedelta(days=EOL_HORIZON_DAYS)).isoformat()
        for s in stalls:
            mid, state = s["id"], s["state"]
            if state == "canaried":
                beat = call(port, "POST", "/stable/hello", {"id": mid})
                if beat.get("transition", {}).get("to") == "available":
                    mindline(port, scope, beat, "available",
                             earned_after=beat.get("canary_beats"))
                    print(f"  ↳ {mid} earned its place — available")
                if port == JOIN_PORT and mid not in self.pinged:
                    ping = governed_ping(port, s.get("class", "medium"))
                    if ping:
                        self.pinged.add(mid)
                        mindline(port, scope, s, "canary-thought", **ping)
                state = beat.get("state", state)
            if state in ("canaried", "available") and mid in by_id:
                c = by_id[mid]
                out = call(port, "POST", "/stable/state",
                           {"id": mid, "op": "sync", "manifest": deal(c),
                            "expires_at": c.get("expires_at")})
                if out.get("transition", {}).get("to") == "deprecated":
                    mindline(port, scope, out, "manifest-drift",
                             pinned=out.get("manifest_hash"),
                             seen=out.get("proposed_hash"))
                    call(port, "POST", "/requests",
                         {"kind": "mind", "action": "reapprove", "mind": mid,
                          "text": f"{mid}'s deal moved under its pin — re-approve the new terms?"})
                    print(f"  ↳ {mid} drifted — the deal changed; held for your decision")
                    continue
                s = out                        # freshest expires_at for the EOL check
                state = s.get("state", state)
            exp = s.get("expires_at")
            if exp and state in ("canaried", "available") and str(exp)[:10] <= edge:
                out = call(port, "POST", "/stable/state",
                           {"id": mid, "op": "eol", "expires_at": exp})
                rec = recommend(s, stalls, cat)
                mindline(port, scope, out, "expiring", expires_at=exp,
                         recommends=(rec or {}).get("id"))
                text = f"{mid} expires {str(exp)[:10]}"
                text += f" — ada recommends {rec['id']} ({rec['why']})" if rec \
                    else " — no replacement found yet"
                call(port, "POST", "/requests",
                     {"kind": "mind", "action": "swap", "mind": mid,
                      "class": s.get("class"), "replacement": rec, "text": text})
                print(f"  ↳ {mid} is expiring — recommendation staged")

    def restable(self, port: int, scope: str, present: set) -> None:
        """The daemon may die; the stable doesn't. The ledger re-saddles live state."""
        for mid, stall in stable_ledger_load(scope).items():
            if mid in present:
                continue
            try:
                call(port, "POST", "/stable/saddle", stall)
                call(port, "POST", "/stable/state",
                     {"id": mid, "op": "attest", "manifest": stall.get("manifest", {}),
                      "expires_at": stall.get("expires_at")})
                mindline(port, scope, stall, "re-saddled",
                         note="daemon restarted; approval is durable in the ledger")
                print(f"  ↳ re-saddled {mid} after a daemon restart")
            except Exception as e:
                print(f"    (re-saddle {mid} failed: {e})")


WRANGLER = Wrangler()


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


def recall_walk(port: int, scope: str, source_did: str, reason: str) -> str:
    """The librarian's 0014 §4 duty, on the wire: fetch the floor's knowledge under
    her OWN authority (humans never read; organs do), walk source + derived_from
    lineage, and version every tainted entry to 'recalled' — annotate-never-rewrite,
    the poison visibly dead in the Window."""
    from datetime import datetime, timedelta, timezone

    from orreth_sim.librarian import tainted_refs

    if not source_did:
        return "nothing to recall — the discredited service carried no source DID"
    token = _ROOT.issue_token(LIB_DID, "u:demo", [{"action": "retrieve", "space": "self"}])
    frm = (datetime.now(timezone.utc) - timedelta(days=365)).strftime("%Y-%m-%dT%H:%M:%SZ")
    r = call(port, "POST", "/retrieve", {
        "query": {"requester": LIB_DID, "subject": {"cohort": {"scope": scope}},
                  "space": "self", "time": {"from": frm}, "intent": "recall",
                  "budget": {"cost": 8}, "auth": "biscuit-sim"},
        "token": token, "requester_scope": scope})
    entries, bodies, tags_of = [], {}, {}
    for h in r.get("hits", []):
        tags = h.get("tags") or []
        if "knowledge" not in tags:
            continue
        try:
            body = call(port, "GET", f"/records/{urllib.parse.quote(h['ref'], safe='')}/body")
        except Exception:
            continue
        if not isinstance(body, dict):
            continue
        entries.append({"ref": h["ref"],
                        "source_did": (body.get("source") or {}).get("did", ""),
                        "derived_from": h.get("derived_from") or []})
        bodies[h["ref"]] = body
        tags_of[h["ref"]] = tags
    # refs already annotated by a prior recall version stay annotated — idempotent
    already = {d for e in entries if bodies[e["ref"]].get("state") == "recalled"
               for d in e["derived_from"]}
    recalled = 0
    for ref in tainted_refs(entries, source_did):
        if ref in already or bodies[ref].get("state") == "recalled":
            continue
        new_body = {**bodies[ref], "state": "recalled", "recall_reason": reason,
                    "recalled_source": source_did, "at": NOW()}
        tags = sorted({*tags_of.get(ref, []), "knowledge", "recalled"} - {"gathered"})
        rec = make_memory({"did": LIB_DID, "scope": scope}, LIB, scope, new_body,
                          kind="semantic", tags=list(tags))
        rec["derived_from"] = [ref]
        call(port, "POST", "/records", rec)
        recalled += 1
    return (f"recalled {recalled} entr(ies) traced to {source_did} — "
            "annotated, never rewritten; the lineage is intact")


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


# ---------------------------------------------------------------- the organ pins (R1)

_PIN_FAILED: set = set()                     # (port, organ): grumble once, not every beat


def pin_organs(port: int) -> None:
    """Authority beats archaeology (the stricter R1): becky mints each organ an
    identity token, the floor verifies its chain against the pinned root, and the
    roster stops mining records for that organ's DID. Idempotent every beat, so a
    restarted daemon is re-pinned within seconds — like the replant, for identity."""
    try:
        pins = call(port, "GET", "/organs").get("pins", {})
    except Exception:
        return
    for organ, did in (("charlotte", CHA_DID), ("librarian", LIB_DID), ("ada", ADA_DID)):
        if pins.get(organ) == did:
            continue
        try:
            token = _BECKY.issue_token(did, SCOPE, [{"action": "retrieve", "space": "self"}])
            call(port, "POST", "/organs/pin", {"organ": organ, "token": token})
            _PIN_FAILED.discard((port, organ))
            print(f"  ↳ pinned {organ} → {did[:22]}… on :{port} (becky-chained)")
        except Exception as e:
            if (port, organ) not in _PIN_FAILED:
                _PIN_FAILED.add((port, organ))
                print(f"    (pin {organ} on :{port} refused: {e} — mined fallback stands)")


# ---------------------------------------------------------------- the parlor (0020)

RESIDENT_KEYS = {"charlotte": (CHA, CHA_DID), "ada": (ADA, ADA_DID),
                 "librarian": (LIB, LIB_DID)}


def resident_key(name: str):
    """The signing self behind a parlor seat — becky's door and her parlor chair are
    one identity. Unembodied organs return (None, None): they receive, never sign."""
    if name == "becky":
        return _BECKY.kp, _BECKY.did
    return RESIDENT_KEYS.get(name, (None, None))


def parlor_facts(port: int, scope: str) -> dict:
    """What the resident may read before it answers — its floor's governed state.
    The human never sees any of this raw; only the composed answer travels."""
    facts: dict = {"scope": scope}
    try:
        facts["farm"] = [s for s in call(port, "GET", "/farm").get("services", [])
                         if s.get("floor") == scope]
    except Exception:
        pass
    try:
        st = call(port, "GET", "/stable")
        facts["stalls"] = [s for s in st.get("stalls", []) if s.get("floor") == scope]
        facts["usage"] = st.get("usage", [])
    except Exception:
        pass
    try:
        p = call(port, "GET", "/presence")
        facts["residents"] = p.get("residents", [])
        facts["workforce"] = p.get("workforce", [])
    except Exception:
        pass
    try:
        facts["requests"] = call(port, "GET", "/requests").get("requests", [])
    except Exception:
        pass
    return facts


def executable(port: int, model: str) -> str | None:
    """The litellm string cognition can actually call — or None when this floor holds
    no key for the routed model. Authorize is truth for routing; keys are truth for
    execution (0016 §6): a stall's route decides which key the call needs."""
    route = "litellm-direct"
    try:
        for s in call(port, "GET", "/stable").get("stalls", []):
            if s.get("id") == model:
                route = s.get("route", route)
                break
    except Exception:
        pass
    if route == "openrouter":
        return f"openrouter/{model}" if os.environ.get("OPENROUTER_API_KEY") else None
    keys = {"anthropic": "ANTHROPIC_API_KEY", "openai": "OPENAI_API_KEY"}
    need = keys.get(model.split("/")[0])
    return model if need and os.environ.get(need) else None


def governed_voice(port: int, name: str, did: str, question: str, grounded: str) -> str | None:
    """The resident phrases its grounded answer with one governed thought —
    authorize, think, meter, all under its own DID (0019 §4). The facts travel INTO
    the prompt; the prompt never touches the plane (0016 §6). Classes are tried
    cheap→rich, degrade-where-pins-allow (0010): a grant this floor cannot execute
    is refunded and the next class asked. Unfueled floors fall back to the grounded
    reply — deterministic, never silent, never faked."""
    try:
        import litellm
    except Exception:
        return None
    if not (os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("OPENAI_API_KEY")
            or os.environ.get("OPENROUTER_API_KEY")):
        return None
    if port != JOIN_PORT:
        return None                       # tokens chain to becky's floor, like the canary
    est = 260
    for klass in ("low", "medium", "high"):
        try:
            token = _BECKY.issue_token(did, SCOPE, [{"action": "retrieve", "space": "self"}],
                                       budget={"tokens": 50000})
            grant = call(port, "POST", "/model/authorize",
                         {"token": token, "class": klass, "est_tokens": est})
            model = executable(port, grant["model"])
            if model is None:             # honest refund: authorized, but no key to execute
                call(port, "POST", "/model/meter",
                     {"subject": did, "est_tokens": est, "tokens": 0, "usd": 0,
                      "model": grant["model"], "class": klass})
                continue
            resp = litellm.completion(
                model=model, max_tokens=160,
                messages=[{"role": "system", "content":
                           f"You are {name}, a resident organ of the Orreth floor {SCOPE}. "
                           "Answer the caller in at most three short sentences, grounded ONLY "
                           "in the facts below. Never invent numbers or names.\n\nFACTS:\n"
                           + grounded},
                          {"role": "user", "content": question}])
            tokens = resp.usage.total_tokens
            try:
                usd = litellm.completion_cost(completion_response=resp)
            except Exception:
                usd = 0.0
            call(port, "POST", "/model/meter",
                 {"subject": did, "est_tokens": est, "tokens": tokens,
                  "usd": round(usd, 6), "model": grant["model"], "class": klass})
            out = (resp.choices[0].message.content or "").strip()
            if out:
                return out
        except Exception:
            continue
    return None


def on_parlor(port: int, scope: str, r: dict) -> None:
    """An audience: the caller asks, the resident fetches with its own authority,
    and the exchange lands signed in the Window. Humans never read; they are answered."""
    name = str(r.get("to") or "").strip().lower()
    facts = parlor_facts(port, scope)
    if r.get("verb") == "card":
        c = parlor.card(name, facts)
        _, did = resident_key(name)
        if did:
            c["did"] = did
        call(port, "POST", "/requests/resolve",
             {"id": r["id"], "status": "done", "result": {"card": c}})
        print(f"  ↳ parlor · {name}'s card handed to the caller")
        return
    asked = str(r.get("text") or "").strip()
    ans = parlor.answer(name, asked, facts)
    reply = ans["reply"]
    if ans.get("action") == "gather":     # the librarian's real duty (0014), front-doored
        reply = gather(port, scope, ans["topic"])
    kp, did = resident_key(name)
    voiced = None
    if kp is not None and ans.get("action") != "gather":
        voiced = governed_voice(port, name, did, asked, reply)
    final = voiced or reply
    call(port, "POST", "/requests/resolve",
         {"id": r["id"], "status": "done",
          "result": {"reply": final, "voiced": bool(voiced), "by": did}})
    if kp is not None:                    # embodied residents sign the audience
        body = parlor.audience_body(name, asked, final,
                                    session=str(r.get("session") or ""),
                                    voiced=bool(voiced))
        rec = make_memory({"did": did, "scope": scope}, kp, scope, body,
                          kind="episodic", tags=["parlor", name])
        try:
            call(port, "POST", "/records", rec)
        except Exception as e:
            print(f"    (audience write failed: {e})")
    print(f"  ↳ parlor · {name} received “{asked[:48]}”" + (" · voiced" if voiced else ""))


# ---------------------------------------------------------------- the round

def main() -> None:
    print(f"console worker · librarian {LIB_DID[:20]}… · charlotte {CHA_DID[:20]}… "
          f"· ada {ADA_DID[:20]}… · becky's door on :{JOIN_PORT} · tending floors {FLOORS}")
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
                    elif r.get("kind") == "join" and port == JOIN_PORT:
                        # the desk is its own dedup — it acts only on real transitions
                        act = JOINDOOR.tend(r)
                        if act:
                            status, result = act
                            if status == "done":
                                result = {**result, "scope": SCOPE,
                                          "granted_by": _BECKY.did}
                            call(port, "POST", "/requests/resolve",
                                 {"id": r["id"], "status": status, "result": result})
                            who = r.get("name") or (r.get("did") or "?")[:22] + "…"
                            print({"challenged": f"  ↳ join {r['id']}: challenged {who} at the door",
                                   "staged": f"  ↳ join {r['id']}: {who} proved its key — the door waits for you",
                                   "done": f"    ✓ lease granted — welcome to {SCOPE}, {who}",
                                   "denied": f"  ↳ join {r['id']}: {who} turned away — proof failed",
                                   }.get(status, f"  ↳ join {r['id']} → {status}"))
                    elif r.get("kind") == "service":
                        if KEEPER.on_service_request(port, scope, r) or r.get("status") == "staged":
                            handled.add(key)
                    elif r.get("kind") == "mind":
                        if WRANGLER.on_mind_request(port, scope, r) or r.get("status") == "staged":
                            handled.add(key)
                    elif r.get("kind") == "parlor" and r.get("status") == "pending":
                        handled.add(key)
                        on_parlor(port, scope, r)
                    elif r.get("kind") == "recall" and r.get("status") == "pending":
                        handled.add(key)
                        print(f"  ↳ recall {r['id']}: walking knowledge from "
                              f"{r.get('source_did', '?')[:32]}…")
                        result = recall_walk(port, scope, r.get("source_did", ""),
                                             r.get("reason", "source discredited"))
                        call(port, "POST", "/requests/resolve",
                             {"id": r["id"], "status": "done", "result": result})
                        print(f"    ✓ {result}")
                if beat_due:
                    KEEPER.tend(port, scope)
                    WRANGLER.sync(port, scope)
                    pin_organs(port)
            except Exception as e:
                scopes.pop(port, None)
                print(f"  (floor :{port} unreachable…)", e)
        if beat_due:
            KEEPER.last_beat = time.time()
        time.sleep(2)


if __name__ == "__main__":
    main()
