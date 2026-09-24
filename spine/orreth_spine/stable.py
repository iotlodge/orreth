# PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P6.5 sp3, the Stable keeper · 2026-09-24
"""The Stable v0 (canon 0005 P6.5 sp3 · 0009 §2 "the STABLE firmware" · 0019
the Stable · 0058 the market · JB's lock 2026-09-24: "LiteLLM executes; the
registry knows and decides").

THE GATEWAY is LiteLLM, run and managed by Orreth (spine/compose.yaml, the
`gateway` box on :4604). Every mind, wherever it resides — Anthropic direct ·
OpenRouter · Ollama on the host · any OpenAI-compatible base — is a STALL: a
service of kind `mind` on the one ladder (services.py) whose manifest is the
DEAL (model · provider · route · price per million in and out · context ·
modalities · class · the key by env NAME), and a model entry the Stable
writes into the gateway. Registering a stall writes it there; retiring
removes it. Every body thinks through the gateway with ITS OWN virtual key
wearing its budget and renewal window — the fuel clause (0058: allowance per
window, lazy renewal, the refill door) is the gateway's native ledger; every
answer wears its cost; the meter (gateway.py) lands dollars beside tokens.

Routing (0058: effort IS class): an ask's PIN → the subject's ASSIGNMENT for
the class → the template's own model → the cheapest standing stall of the
class → a neighbouring class, CONFESSED (`resolve`, the fixture's). Health
is the canary ping through the gateway under the keeper's DID, metered.
Drift (the price or the deal moved under the pin) marks the stall unhealthy
with what moved and the keeper proposes a re-pin; EOL (the catalog names an
expiry inside the horizon) earns a proposal to retire with a recommended
swap — same class → fit → nearest price → newest. The keeper never retires,
assigns, refills or re-pins alone: every such act is one of the kernel's
own held acts at the interlock (proof.hold_kernel_act), cancel the default.
A key VALUE lives in ZERO records (0059): the stall names the env variable;
the gateway box reads it from its own environment.
"""
from __future__ import annotations

import json
import os
import re
import time
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone

from . import envelope as ev, outbox, services

# ---- dials ---------------------------------------------------------------------------------------
GATEWAY_DIAL, GATEWAY_DEFAULT = "SPINE_GATEWAY", "http://127.0.0.1:4604"
GATEWAY_KEY_DIAL, GATEWAY_KEY_DEFAULT = "SPINE_GATEWAY_KEY", "sk-orreth-dev"
LEASE_USD_DIAL, LEASE_USD_DEFAULT = "SPINE_LEASE_USD", 1.0          # a body's allowance per window
LEASE_DAYS_DIAL, LEASE_DAYS_DEFAULT = "SPINE_LEASE_RENEW_DAYS", 1    # the window (budget.renew_days)
EOL_DIAL, EOL_DEFAULT = "SPINE_EOL_HORIZON_DAYS", 30                 # the pasture horizon
OLLAMA_DIAL, OLLAMA_DEFAULT = "SPINE_OLLAMA_BASE", "http://host.docker.internal:11434"  # as the BOX sees the host
MIND_CHECK_DIAL, MIND_CHECK_DEFAULT = "SPINE_MIND_CHECK_S", 600      # the keeper's cadence
CATALOG_TTL_S = 300.0
TIMEOUT_S = 60.0
OPENROUTER_CATALOG = "https://openrouter.ai/api/v1/models"           # keyless intel (0019)

CLASSES = ("fast", "standard", "deep")
ANY = "any"                                                          # an assignment for ALL of a body's work (W44)
PROVIDERS = ("anthropic", "openrouter", "ollama", "openai", "compatible")
KEY_OF = {"anthropic": "ANTHROPIC_API_KEY", "openrouter": "OPENROUTER_API_KEY",
          "openai": "OPENAI_API_KEY", "ollama": None, "compatible": None}
STANDING = ("registered", "versioned", "healthy")                    # a stall that may serve

ASSIGNED = "orreth.mind.assigned.v1"
UNASSIGNED = "orreth.mind.unassigned.v1"
FUELED = "orreth.mind.fueled.v1"

# the kernel's own held acts (L2, cancel the default; the keeper proposes, the human cuts)
REGISTER_TOOL, ASSIGN_TOOL, UNASSIGN_TOOL = "mind.register", "mind.assign", "mind.unassign"
REFILL_TOOL, REPIN_TOOL = "mind.refill", "mind.repin"
HELD_TOOLS = (REGISTER_TOOL, ASSIGN_TOOL, UNASSIGN_TOOL, REFILL_TOOL, REPIN_TOOL, services.RETIRE_TOOL)
ACT_LEVEL, ACT_CLASS = "L2", "consequential"

_ENV_NAME = re.compile(r"^[A-Z][A-Z0-9_]{2,}$")


class StableRefused(ValueError):
    """The Stable's refusal — the reason in plain words."""


class GatewayDark(RuntimeError):
    """The gateway did not answer — said in words, never a stack."""


def _dial(name: str, default, cast=float):
    try:
        return cast(os.environ.get(name) or default)
    except ValueError:
        return default


# ---- the pure laws (fixture minds-v0) --------------------------------------------------------------

def route_for(provider: str, model: str, base: str | None = None) -> dict:
    """The gateway's model string for a mind wherever it resides — and the
    base it needs, when it needs one. {ok, route, base, reason}."""
    p = (provider or "").strip().lower()
    m = (model or "").strip()
    if p not in PROVIDERS:
        return {"ok": False, "route": None, "base": None,
                "reason": f"no provider named {provider!r} — the providers: " + ", ".join(PROVIDERS)}
    if not m:
        return {"ok": False, "route": None, "base": None, "reason": "a mind needs a model id"}
    if p == "compatible" and not base:
        return {"ok": False, "route": None, "base": None,
                "reason": "an OpenAI-compatible mind needs its base URL"}
    if p == "ollama":
        return {"ok": True, "route": f"ollama/{m}", "base": base or OLLAMA_DEFAULT, "reason": None}
    if p == "compatible":
        return {"ok": True, "route": f"openai/{m}", "base": base, "reason": None}
    return {"ok": True, "route": f"{p}/{m}", "base": base, "reason": None}


def deal(model: str, provider: str, *, base: str | None = None, price: dict | None = None,
         context: int | None = None, modalities: list[str] | None = None, klass: str = "standard",
         key: str | None | object = "auto", expires: str | None = None) -> dict:
    """The DEAL a stall pins — the manifest. The key is an env NAME (a value
    is refused: it never enters a record). Prices are dollars per MILLION
    tokens, in and out. Refuses in words."""
    r = route_for(provider, model, base)
    if not r["ok"]:
        raise StableRefused(r["reason"])
    p = provider.strip().lower()
    if klass not in CLASSES:
        raise StableRefused(f"no class named {klass!r} — the classes: " + ", ".join(CLASSES))
    k = KEY_OF[p] if key == "auto" else key
    if k is not None and not _ENV_NAME.match(str(k)):
        raise StableRefused("a key VALUE never enters a record — name the environment variable "
                            "that holds it (like ANTHROPIC_API_KEY)")
    pr = {"in_per_m": float((price or {}).get("in_per_m", 0.0) or 0.0),
          "out_per_m": float((price or {}).get("out_per_m", 0.0) or 0.0)}
    if pr["in_per_m"] < 0 or pr["out_per_m"] < 0:
        raise StableRefused("a price is never negative")
    d = {"model": model.strip(), "provider": p, "route": r["route"], "base": r["base"], "key": k,
         "price": pr, "context": int(context) if context else None,
         "modalities": sorted(set(modalities or ["text"])), "class": klass}
    if expires:
        d["expires"] = expires
    return d


def usd(price: dict, tokens_in: int, tokens_out: int) -> float:
    """The cost arithmetic: dollars from the pin's price, never guessed.
    Rounded to the ten-millionth of a dollar (the gateway's own grain)."""
    p = price or {}
    return round(int(tokens_in) * float(p.get("in_per_m", 0.0)) / 1e6
                 + int(tokens_out) * float(p.get("out_per_m", 0.0)) / 1e6, 10)


def budget_duration(days: int) -> str:
    """The fuel clause's window in the gateway's grammar (`budget.renew_days`)."""
    return f"{max(1, int(days))}d"


def _standing(s: dict) -> bool:
    return s.get("state") in STANDING


def _cheapest(cands: list[dict]) -> dict | None:
    if not cands:
        return None
    return sorted(cands, key=lambda s: (float((s.get("manifest") or {}).get("price", {}).get("in_per_m", 0.0)),
                                        -(s.get("version") or 0), s["name"]))[0]


def resolve(stalls: list[dict], assignments: list[dict], *, subject: str | None,
            klass: str | None = None, pin: str | None = None, model: str | None = None) -> dict:
    """The routing decision — one law, the fixture's. In order: an ask's
    PIN (a stall by name; a pinned stall that does not stand REFUSES —
    never climbs, 0019); the subject's ASSIGNMENT for the class (then
    the world's, subject "*"); the template's own MODEL when a standing
    stall pins it; the cheapest standing stall of the class; a
    neighbouring class, confessed. {ok, stall, route, why, degraded,
    reason}."""
    by_name = {s["name"]: s for s in stalls}
    if pin:
        s = by_name.get(pin)
        if s is None:
            return {"ok": False, "stall": None, "route": None, "why": None, "degraded": False,
                    "reason": f"no LLM named {pin!r} stands in the Stable"}
        if not _standing(s):
            return {"ok": False, "stall": None, "route": None, "why": None, "degraded": False,
                    "reason": f"the {pin} LLM is {s['state']} — a pinned LLM that does not stand refuses, never climbs"}
        return {"ok": True, "stall": pin, "route": s["manifest"]["route"], "why": f"pinned to {pin} for this ask",
                "degraded": False, "reason": None}
    k = klass if klass in CLASSES else None
    for who in ((subject, "*") if subject else ("*",)):
        rows = [a for a in assignments if a["subject"] == who]
        # W44 (walk #12): "assign librarian to haiku" means the librarian uses haiku for ALL its work —
        # an assignment for the class asked wins, then the body-wide one, then the newest; never the alphabet
        exact = [a for a in rows if k is not None and a.get("klass") == k]
        wide = [a for a in rows if a.get("klass") in (ANY, None)]
        rest = [a for a in rows if a not in exact and a not in wide]
        newest = lambda xs: sorted(xs, key=lambda a: str(a.get("at") or ""), reverse=True)  # noqa: E731
        for a in newest(exact) + newest(wide) + (newest(rest) if k is None else []):
            s = by_name.get(a["stall"])
            if s is not None and _standing(s):
                whom = "every body" if who == "*" else who
                return {"ok": True, "stall": s["name"], "route": s["manifest"]["route"],
                        "why": (f"assigned: {whom} uses {s['name']} for all work" if a.get("klass") in (ANY, None)
                                else f"assigned: {whom} uses {s['name']} for {a['klass']} work"),
                        "degraded": False, "reason": None}
    if model:
        for s in stalls:
            if _standing(s) and (s.get("manifest") or {}).get("model") == model and (k is None or s["manifest"].get("class") == k):
                return {"ok": True, "stall": s["name"], "route": s["manifest"]["route"],
                        "why": f"the template names {model} — the {s['name']} LLM", "degraded": False, "reason": None}
    standing = [s for s in stalls if _standing(s)]
    if k is not None:
        s = _cheapest([s for s in standing if (s.get("manifest") or {}).get("class") == k])
        if s is not None:
            return {"ok": True, "stall": s["name"], "route": s["manifest"]["route"],
                    "why": f"the cheapest standing {k} LLM", "degraded": False, "reason": None}
        near = {"fast": ("standard", "deep"), "standard": ("fast", "deep"), "deep": ("standard", "fast")}[k]
        for nk in near:
            s = _cheapest([s for s in standing if (s.get("manifest") or {}).get("class") == nk])
            if s is not None:
                return {"ok": True, "stall": s["name"], "route": s["manifest"]["route"],
                        "why": f"no {k} LLM stands — the {nk} LLM {s['name']} serves instead, confessed",
                        "degraded": True, "reason": None}
    s = _cheapest(standing)
    if s is not None:
        return {"ok": True, "stall": s["name"], "route": s["manifest"]["route"],
                "why": f"the cheapest standing LLM" + (f" — none named {model}" if model else ""),
                "degraded": bool(model), "reason": None}
    return {"ok": False, "stall": None, "route": None, "why": None, "degraded": False,
            "reason": "no LLM stands in the Stable — add one (\"stablekeeper, add the LLM ollama gemma3:270m as gemma\")"}


def drift(pinned: dict, seen: dict) -> list[str]:
    """What moved under the pin (0019: price drift = rug pull): the price
    in or out, the context. Words, one per move; empty = the deal holds."""
    moved = []
    pp, sp = (pinned or {}).get("price") or {}, (seen or {}).get("price") or {}
    for side in ("in_per_m", "out_per_m"):
        a, b = float(pp.get(side, 0.0) or 0.0), sp.get(side)
        if b is not None and abs(float(b) - a) > 1e-9:
            moved.append(f"the price {'in' if side == 'in_per_m' else 'out'} moved: ${a:g} → ${float(b):g} per million")
    pc, sc = (pinned or {}).get("context"), (seen or {}).get("context")
    if pc and sc and int(sc) != int(pc):
        moved.append(f"the context moved: {int(pc):,} → {int(sc):,} tokens")
    return moved


def eol_due(expires: str | None, now: datetime, horizon_days: int) -> dict:
    """EOL is an appointment (0019): an expiry inside the horizon is due.
    {due, days, words}."""
    if not expires:
        return {"due": False, "days": None, "words": "no expiry named"}
    try:
        at = datetime.fromisoformat(str(expires).replace("Z", "+00:00"))
        if at.tzinfo is None:
            at = at.replace(tzinfo=timezone.utc)
    except ValueError:
        return {"due": False, "days": None, "words": f"an expiry the calendar cannot read: {expires!r}"}
    days = (at - now).days
    if days <= horizon_days:
        return {"due": True, "days": days,
                "words": (f"expires in {days} day{'s' if days != 1 else ''} ({at.date().isoformat()})" if days >= 0
                          else f"expired {-days} day{'s' if -days != 1 else ''} ago ({at.date().isoformat()})")}
    return {"due": False, "days": days, "words": f"expires in {days} days — outside the {horizon_days}-day horizon"}


def recommend(stalls: list[dict], retiring: str) -> dict:
    """The swap for a mind on its way out: same class → fit (context no
    smaller, modalities covering) → nearest price → newest. {stall, why}
    — no fit says so."""
    by_name = {s["name"]: s for s in stalls}
    old = by_name.get(retiring)
    if old is None:
        return {"stall": None, "why": f"no LLM named {retiring!r} to swap from"}
    om = old.get("manifest") or {}
    cands = [s for s in stalls if s["name"] != retiring and _standing(s)
             and (s.get("manifest") or {}).get("class") == om.get("class")]
    if not cands:
        return {"stall": None, "why": f"no other standing {om.get('class', '?')} LLM — nothing to swap to"}
    fit = [s for s in cands if (not om.get("context") or (s["manifest"].get("context") or 0) >= om["context"])
           and set(om.get("modalities") or []) <= set(s["manifest"].get("modalities") or [])]
    if not fit:
        return {"stall": None, "why": f"{len(cands)} {om.get('class')} LLM{'s' if len(cands) != 1 else ''} stand but none "
                                      f"fits the deal (context {om.get('context')}, {', '.join(om.get('modalities') or [])})"}
    op = float((om.get("price") or {}).get("in_per_m", 0.0))
    best = sorted(fit, key=lambda s: (abs(float(s["manifest"]["price"].get("in_per_m", 0.0)) - op),
                                      -(s.get("version") or 0), s["name"]))[0]
    return {"stall": best["name"], "why": f"same class, fits the deal, nearest price (${best['manifest']['price'].get('in_per_m', 0):g} "
                                          f"vs ${op:g} per million in)"}


# ---- the gateway's management door -------------------------------------------------------------------

class Gateway:
    """The gateway's own doors (LiteLLM's management API) — models, keys,
    spend — under the master key. Every miss is words (GatewayDark)."""

    def __init__(self, base: str | None = None, key: str | None = None):
        self.base = (base or os.environ.get(GATEWAY_DIAL) or GATEWAY_DEFAULT).rstrip("/")
        self.key = key or os.environ.get(GATEWAY_KEY_DIAL) or GATEWAY_KEY_DEFAULT

    def _call(self, method: str, path: str, body: dict | None = None, *, key: str | None = None,
              timeout: float = TIMEOUT_S) -> tuple[int, dict, dict]:
        data = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(self.base + path, data=data, method=method,
                                     headers={"Authorization": f"Bearer {key or self.key}",
                                              "content-type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                raw = r.read()
                return r.status, (json.loads(raw) if raw else {}), dict(r.headers)
        except urllib.error.HTTPError as e:
            raw = e.read()
            try:
                return e.code, json.loads(raw), dict(e.headers)
            except ValueError:
                return e.code, {"error": {"message": raw.decode(errors="replace")[:300]}}, dict(e.headers)
        except (urllib.error.URLError, OSError) as e:
            raise GatewayDark(f"the gateway at {self.base} did not answer: {getattr(e, 'reason', e)}")

    @staticmethod
    def _words(body: dict) -> str:
        err = body.get("error") if isinstance(body, dict) else None
        if isinstance(err, dict):
            return str(err.get("message") or err)
        return str(err or body)[:300]

    def ready(self) -> bool:
        try:
            st, _, _ = self._call("GET", "/health/readiness", timeout=5.0)
            return st == 200
        except GatewayDark:
            return False

    def models(self) -> dict[str, dict]:
        """Every model entry the gateway holds, by its id (the stall's name)."""
        st, body, _ = self._call("GET", "/model/info")
        if st != 200:
            raise GatewayDark(f"the gateway's model list refused: {self._words(body)}")
        return {str((m.get("model_info") or {}).get("id") or m.get("model_name")): m for m in body.get("data", [])}

    def add_stall(self, name: str, d: dict) -> dict:
        """The stall's model entry — idempotent by id; the key by env NAME
        (`os.environ/NAME`: the box resolves it, the value never travels).
        The entry names its BASE MODEL (the route) and, when the deal
        carries a price, the price per token — proven live 2026-09-24: an
        entry without them is charged $0 on every STREAMED answer (the
        gateway's stream path prices by the entry, not by the provider's
        reply), and the fuel clause would not bind. An entry already there
        without them is rewritten."""
        have = self.models().get(name)
        if have is not None:
            info = have.get("model_info") or {}
            if info.get("base_model") == d["route"]:
                return {"present": True}
            self.drop_stall(name)                    # an old entry that streams for free: rewritten
        params = {"model": d["route"]}
        if d.get("key"):
            params["api_key"] = f"os.environ/{d['key']}"
        if d.get("base"):
            params["api_base"] = d["base"]
        pr = d.get("price") or {}
        if pr.get("in_per_m") or pr.get("out_per_m"):   # the pin's price is the contract the gateway charges by
            params["input_cost_per_token"] = float(pr.get("in_per_m", 0.0)) / 1e6
            params["output_cost_per_token"] = float(pr.get("out_per_m", 0.0)) / 1e6
        st, body, _ = self._call("POST", "/model/new", {"model_name": name, "litellm_params": params,
                                                        "model_info": {"id": name, "base_model": d["route"]}})
        if st != 200:
            raise GatewayDark(f"the gateway refused the {name} LLM: {self._words(body)}")
        return {"present": have is not None}

    def drop_stall(self, name: str) -> bool:
        if name not in self.models():
            return False
        st, body, _ = self._call("POST", "/model/delete", {"id": name})
        if st != 200:
            raise GatewayDark(f"the gateway would not drop the {name} LLM: {self._words(body)}")
        return True

    def seen_deal(self, name: str) -> dict | None:
        """The deal as the gateway's own price map sees it: dollars per
        million in and out, the context, the modalities."""
        m = self.models().get(name)
        if m is None:
            return None
        info = m.get("model_info") or {}
        ci, co = info.get("input_cost_per_token"), info.get("output_cost_per_token")
        mods = ["text"] + (["vision"] if info.get("supports_vision") else [])
        return {"price": {"in_per_m": round(float(ci) * 1e6, 6) if ci is not None else None,
                          "out_per_m": round(float(co) * 1e6, 6) if co is not None else None},
                "context": info.get("max_input_tokens") or info.get("max_tokens"),
                "modalities": sorted(mods), "tools": bool(info.get("supports_function_calling"))}

    def key_new(self, *, did: str, alias: str, max_usd: float, renew_days: int,
                models: list[str] | None = None) -> dict:
        body = {"key_alias": alias, "user_id": did, "max_budget": float(max_usd),
                "budget_duration": budget_duration(renew_days), "metadata": {"orreth": "a body's lease"}}
        if models:
            body["models"] = models
        st, out, _ = self._call("POST", "/key/generate", body)
        if st != 200 or not out.get("key"):
            raise GatewayDark(f"the gateway would not mint a key for {alias}: {self._words(out)}")
        return out

    def key_info(self, key: str) -> dict:
        st, out, _ = self._call("GET", f"/key/info?key={key}")
        if st != 200:
            raise GatewayDark(f"the gateway would not read the key: {self._words(out)}")
        return out.get("info") or {}

    def key_update(self, key: str, **fields) -> dict:
        st, out, _ = self._call("POST", "/key/update", {"key": key, **fields})
        if st != 200:
            raise GatewayDark(f"the gateway would not update the key: {self._words(out)}")
        return out

    def key_delete(self, keys: list[str]) -> None:
        self._call("POST", "/key/delete", {"keys": list(keys)})

    def spend_logs(self, *, user_id: str | None = None, request_id: str | None = None) -> list[dict]:
        q = "&".join(f"{k}={v}" for k, v in (("user_id", user_id), ("request_id", request_id)) if v)
        st, out, _ = self._call("GET", "/spend/logs" + (f"?{q}" if q else ""))
        if st != 200:
            raise GatewayDark(f"the gateway's spend log refused: {self._words(out)}")
        return out if isinstance(out, list) else []


# ---- the ground -------------------------------------------------------------------------------------

def ensure_schema(conn) -> None:
    services.ensure_schema(conn)
    from .outbox import once
    if not once(conn, "stable"):
        return
    with conn.transaction():
        cur = conn.cursor()
        cur.execute("SELECT pg_advisory_xact_lock(742199)")  # DDL race guard
        cur.execute(
            "CREATE TABLE IF NOT EXISTS spine_mind_assignments ("
            " subject text NOT NULL, scope text NOT NULL, klass text NOT NULL,"
            " stall text NOT NULL, by_did text NOT NULL,"
            " at timestamptz NOT NULL DEFAULT now(),"
            " PRIMARY KEY (subject, scope, klass))")
        cur.execute(
            "CREATE TABLE IF NOT EXISTS spine_mind_keys ("
            " did text NOT NULL, scope text NOT NULL, alias text NOT NULL,"
            " key text NOT NULL, max_usd double precision NOT NULL,"
            " renew_days int NOT NULL, made_at timestamptz NOT NULL DEFAULT now(),"
            " drained_at timestamptz, refills int NOT NULL DEFAULT 0,"
            " PRIMARY KEY (did, scope))")


def stalls(conn) -> list[dict]:
    """Every mind in the Stable — the shelf's rows of kind mind, with its
    spend today and all time off the meter."""
    ensure_schema(conn)
    rows = services.listing(conn, kind="mind")
    from .gateway import ensure_schema as _meter
    _meter(conn)
    cur = conn.cursor()
    cur.execute("SELECT stall, count(*), coalesce(sum(usd), 0),"
                " coalesce(sum(usd) FILTER (WHERE at >= date_trunc('day', now())), 0),"
                " count(*) FILTER (WHERE ok = false)"
                " FROM spine_meter WHERE stall IS NOT NULL GROUP BY stall")
    spend = {r[0]: {"calls": int(r[1]), "usd": float(r[2]), "usd_today": float(r[3]), "failed": int(r[4])}
             for r in cur.fetchall()}
    for s in rows:
        s["spend"] = spend.get(s["name"], {"calls": 0, "usd": 0.0, "usd_today": 0.0, "failed": 0})
    return rows


def assignments(conn) -> list[dict]:
    ensure_schema(conn)
    cur = conn.cursor()
    cur.execute("SELECT subject, klass, stall, by_did, at FROM spine_mind_assignments WHERE scope = %s"
                " ORDER BY subject, klass", (ev.scope(),))
    return [{"subject": r[0], "klass": r[1], "stall": r[2], "by": r[3], "at": r[4].isoformat()} for r in cur.fetchall()]


def _mind_fact(conn, type_: str, ref: str, payload: dict, by: str, note: str, *, ask: str | None = None,
               parent_marker: str | None = None, confirmed_by: str | None = None, domain=None) -> dict:
    from . import markers
    markers.ensure_schema(conn); outbox.ensure_schema(conn)
    mid = markers.new_id()
    kind = "action" if ask else "observation"
    parent = parent_marker or services.shelf_root(conn)
    chain = [by] if by == services.KERNEL else [by, services.KERNEL]
    if confirmed_by and confirmed_by != by:
        chain = [by, confirmed_by, services.KERNEL]
    e = ev.make_envelope(kind="event", type=type_, universe_id=ev.scope(), scope_path=ev.scope(),
                         payload=dict(payload, ref=ref, by=by), correlation_id=ask or ref,
                         authority_chain=chain, marker={"kind": kind, "id": mid, "parent": parent, "by": by})

    def _domain(cur):
        markers.insert(cur, mid, kind, parent, ask or ref, by, note)
        if domain is not None:
            domain(cur, mid)

    outbox.commit_with_outbox(conn, ev.encode(e), e["message_id"], _domain)
    return {"marker": mid, "message_id": e["message_id"]}


def register_mind(conn, name: str, d: dict, *, by: str, gw: Gateway | None = None,
                  home=services._UNSET, placement: dict | None = None) -> dict:
    """A stall: the service registered on the ladder (the deal its
    manifest, the key by NAME its secret), then written into the gateway.
    A gateway that refuses leaves the ladder untouched — nothing recorded."""
    ensure_schema(conn)
    name = str(name or "").strip().lower()
    if not re.match(r"^[a-z][a-z0-9_.-]{0,63}$", name):
        raise StableRefused("an LLM needs a short lowercase name (letters, digits, . _ -)")
    if gw is not None:
        gw.add_stall(name, d)                        # words on refusal; the ladder untouched
    return services.register(conn, name, "mind", d, by=by, placement=placement,
                             secrets_with=[d["key"]] if d.get("key") else None, home=home)


def repin_mind(conn, name: str, d: dict, *, by: str, gw: Gateway | None = None, **kw) -> dict:
    """A changed deal re-pins the stall (services.version) and rewrites its
    entry in the gateway."""
    if gw is not None:
        gw.drop_stall(name)
        gw.add_stall(name, d)
    return services.version(conn, name, d, by=by)


def retire_mind(conn, name: str, *, by: str, gw: Gateway | None = None, **kw) -> dict:
    """Retired on the ladder (dormancy, never deletion) and dropped from the
    gateway — no body can think through a retired mind."""
    made = services.retire(conn, name, by=by, **kw)
    if gw is not None:
        try:
            gw.drop_stall(name)
        except GatewayDark:
            pass                                     # the ladder is the truth; the beat re-syncs
    return made


def restore_mind(conn, name: str, *, by: str, gw: Gateway | None = None) -> dict:
    made = services.restore(conn, name, by=by)
    if gw is not None:
        gw.add_stall(name, made["manifest"])
    return made


def assign(conn, subject: str, klass: str, stall: str, *, by: str, ask: str | None = None,
           parent_marker: str | None = None, confirmed_by: str | None = None) -> dict:
    """subject → {class: stall}: a body's (or "*", every body's) mind for a
    class, a fact. The stall must stand."""
    ensure_schema(conn)
    if klass not in CLASSES and klass != ANY:
        raise StableRefused(f"no class of work named {klass!r} — fast, standard, deep, or any")
    s = services.get(conn, stall)
    if s is None or s["kind"] != "mind":
        raise StableRefused(f"no LLM named {stall!r} stands in the Stable")
    if not _standing(s):
        raise StableRefused(f"the {stall} LLM is {s['state']} — assign an LLM that stands")

    def domain(cur, mid):
        cur.execute("INSERT INTO spine_mind_assignments (subject, scope, klass, stall, by_did, at)"
                    " VALUES (%s, %s, %s, %s, %s, clock_timestamp())"
                    " ON CONFLICT (subject, scope, klass) DO UPDATE SET stall = EXCLUDED.stall,"
                    " by_did = EXCLUDED.by_did, at = clock_timestamp()", (subject, ev.scope(), klass, stall, by))

    _mind_fact(conn, ASSIGNED, s["did"], {"subject": subject, "klass": klass, "stall": stall, "hash": s["manifest_hash"]},
               by, f"{subject} uses the {stall} LLM for {'all' if klass == ANY else klass} work", ask=ask, parent_marker=parent_marker,
               confirmed_by=confirmed_by, domain=domain)
    return {"subject": subject, "klass": klass, "stall": stall}


def unassign(conn, subject: str, klass: str, *, by: str, ask: str | None = None,
             parent_marker: str | None = None, confirmed_by: str | None = None) -> dict:
    ensure_schema(conn)
    cur = conn.cursor()
    cur.execute("SELECT stall FROM spine_mind_assignments WHERE subject = %s AND scope = %s AND klass = %s",
                (subject, ev.scope(), klass))
    r = cur.fetchone()
    if r is None:
        raise StableRefused(f"{subject} has no {klass} assignment to lift")
    s = services.get(conn, r[0])

    def domain(cur, mid):
        cur.execute("DELETE FROM spine_mind_assignments WHERE subject = %s AND scope = %s AND klass = %s",
                    (subject, ev.scope(), klass))

    _mind_fact(conn, UNASSIGNED, s["did"] if s else r[0], {"subject": subject, "klass": klass, "stall": r[0]},
               by, f"{subject} no longer pinned to {r[0]} ({klass})", ask=ask, parent_marker=parent_marker,
               confirmed_by=confirmed_by, domain=domain)
    return {"subject": subject, "klass": klass, "stall": r[0]}


def resolve_for(conn, *, subject: str | None, model: str | None = None, klass: str | None = None,
                pin: str | None = None) -> dict:
    return resolve(services.listing(conn, kind="mind"), assignments(conn), subject=subject,
                   klass=klass, pin=pin, model=model)


# ---- the fuel clause: a body's lease is its virtual key ------------------------------------------

def lease_defaults() -> tuple[float, int]:
    return _dial(LEASE_USD_DIAL, LEASE_USD_DEFAULT, float), _dial(LEASE_DAYS_DIAL, LEASE_DAYS_DEFAULT, int)


def key_for(conn, did: str, name: str, gw: Gateway, *, by: str = services.KERNEL) -> dict:
    """The body's own key at the gateway, minted once with the default
    lease (allowance per window, the window in days) — a fuel fact — and
    the SAME key every life after (the row on the ground; the value never
    in a record)."""
    ensure_schema(conn)
    cur = conn.cursor()
    cur.execute("SELECT key, alias, max_usd, renew_days FROM spine_mind_keys WHERE did = %s AND scope = %s",
                (did, ev.scope()))
    r = cur.fetchone()
    if r is not None:
        return {"key": r[0], "alias": r[1], "max_usd": r[2], "renew_days": r[3], "new": False}
    max_usd, days = lease_defaults()
    alias = f"{ev.scope()}:{name}"
    made = gw.key_new(did=did, alias=alias, max_usd=max_usd, renew_days=days)

    def domain(cur, mid):
        cur.execute("INSERT INTO spine_mind_keys (did, scope, alias, key, max_usd, renew_days)"
                    " VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT (did, scope) DO NOTHING",
                    (did, ev.scope(), alias, made["key"], max_usd, days))

    _mind_fact(conn, FUELED, did, {"max_usd": max_usd, "renew_days": days, "alias": alias, "first": True},
               by, f"{name} fueled: ${max_usd:g} every {days} day{'s' if days != 1 else ''}", domain=domain)
    return {"key": made["key"], "alias": alias, "max_usd": max_usd, "renew_days": days, "new": True}


def mark_drained(conn, did: str) -> None:
    conn.cursor().execute("UPDATE spine_mind_keys SET drained_at = clock_timestamp() WHERE did = %s AND scope = %s",
                          (did, ev.scope()))


def fuel(conn, did: str, gw: Gateway | None) -> dict | None:
    """A body's gauge: the allowance, the spend in this window, when it
    renews — read from the gateway's ledger (the source of the 100%)."""
    ensure_schema(conn)
    cur = conn.cursor()
    cur.execute("SELECT key, max_usd, renew_days, drained_at, refills FROM spine_mind_keys WHERE did = %s AND scope = %s",
                (did, ev.scope()))
    r = cur.fetchone()
    if r is None:
        return None
    out = {"max_usd": r[1], "renew_days": r[2], "drained_at": r[3].isoformat() if r[3] else None,
           "refills": r[4], "spend": None, "renews_at": None}
    if gw is not None:
        try:
            info = gw.key_info(r[0])
            out["spend"] = float(info.get("spend") or 0.0)
            out["max_usd"] = float(info.get("max_budget") or r[1])
            out["renews_at"] = info.get("budget_reset_at")
        except GatewayDark as e:
            out["gauge"] = str(e)
    return out


def refill(conn, did: str, add_usd: float, *, by: str, gw: Gateway, name: str | None = None,
           ask: str | None = None, parent_marker: str | None = None, confirmed_by: str | None = None) -> dict:
    """The refill door: the allowance for this window grows by add_usd at
    the gateway — a fuel fact; the drained mark lifted."""
    ensure_schema(conn)
    cur = conn.cursor()
    cur.execute("SELECT key, alias, max_usd FROM spine_mind_keys WHERE did = %s AND scope = %s", (did, ev.scope()))
    r = cur.fetchone()
    if r is None:
        raise StableRefused(f"{name or did} has no lease yet — it is fueled on its first thought")
    add = float(add_usd)
    if add <= 0:
        raise StableRefused("a refill adds a positive amount of dollars")
    info = gw.key_info(r[0])
    new_max = round(float(info.get("max_budget") or r[2]) + add, 6)
    gw.key_update(r[0], max_budget=new_max)

    def domain(cur, mid):
        cur.execute("UPDATE spine_mind_keys SET max_usd = %s, drained_at = NULL, refills = refills + 1"
                    " WHERE did = %s AND scope = %s", (new_max, did, ev.scope()))

    _mind_fact(conn, FUELED, did, {"max_usd": new_max, "added_usd": add, "alias": r[1], "first": False},
               by, f"{name or did} refilled by ${add:g} — allowance now ${new_max:g}", ask=ask,
               parent_marker=parent_marker, confirmed_by=confirmed_by, domain=domain)
    return {"did": did, "max_usd": new_max, "added_usd": add}


def drained_words(name: str, gauge: dict | None) -> str:
    """The honest word when a body is out of fuel (rule 13: plain, complete)."""
    when = ""
    if gauge and gauge.get("renews_at"):
        try:
            at = datetime.fromisoformat(str(gauge["renews_at"]).replace("Z", "+00:00"))
            when = f" It renews on its own at {at.strftime('%Y-%m-%d %H:%M')} UTC."
        except ValueError:
            pass
    ceiling = f"${gauge['max_usd']:g}" if gauge and gauge.get("max_usd") is not None else "its allowance"
    return (f"I am out of fuel — {name}'s LLM allowance of {ceiling} for this window is spent, so I cannot think "
            f"until it renews or is refilled.{when} A refill is one word away: \"refill {name} by $1\".")


# ---- the held acts: the keeper proposes, the human cuts --------------------------------------------

def hold(conn, tool: str, args: dict, *, text: str, person: str, session: str | None = None) -> str:
    from .proof import hold_kernel_act
    if tool not in HELD_TOOLS:
        raise StableRefused(f"no held act named {tool!r}")
    return hold_kernel_act(conn, text=text, person=person, tool=tool, args=args, level=ACT_LEVEL,
                           session=session, cls=ACT_CLASS)


def act_words(tool: str, args: dict) -> str:
    """The act NAMED in words (W30 · rule 13) — the bare phrase the
    interlock frames ONCE ("Are you sure? <phrase> is consequential — it is
    recorded, and you can restore it later"; W42: the frame is the kernel's
    or the door's, never doubled here)."""
    n = args.get("name") or args.get("stall") or "?"
    if tool == REGISTER_TOOL:
        d = args.get("deal") or {}
        return f"Adding the {n} LLM ({d.get('provider', '?')} {d.get('model', '?')}) to the Stable and the gateway"
    if tool == ASSIGN_TOOL:
        who = "every body" if args.get("subject") == "*" else args.get("subject")
        work = "all its work" if args.get("klass") in (ANY, None) else f"{args.get('klass')} work"
        return f"Pointing {who} at the {args.get('stall')} LLM for {work}"
    if tool == UNASSIGN_TOOL:
        who = "every body" if args.get("subject") == "*" else args.get("subject")
        work = "all-work" if args.get("klass") in (ANY, None) else args.get("klass")
        return f"Lifting {who}'s {work} assignment"
    if tool == REFILL_TOOL:
        return f"Refilling {args.get('name') or args.get('did')} by ${float(args.get('usd', 0)):g} of real spending"
    if tool == REPIN_TOOL:
        return f"Re-pinning the {n} LLM to its new deal (the old pin stays in its history)"
    if tool == services.RETIRE_TOOL:
        return f"Retiring the {n} LLM (it rests, never deleted)"
    return f"The {tool} act"


def settle(conn, held: dict, *, asker: str, ask_id: str, parent_marker: str | None,
           confirmed_by: str | None, gw: Gateway | None = None) -> str:
    """Run a Stable act the human said yes to (proof.settle_kernel_act's
    branch) — the words of what happened."""
    tool, a = held["tool"], held.get("args") or {}
    gw = gw if gw is not None else Gateway()
    if tool == REGISTER_TOOL:
        made = register_mind(conn, a["name"], a["deal"], by=asker, gw=gw)
        d = made["manifest"]
        return (f"the {made['name']} LLM stands in the Stable — {d['provider']} {d['model']}, "
                f"${d['price']['in_per_m']:g} in / ${d['price']['out_per_m']:g} out per million, class {d['class']}; "
                "say “check the minds” to hear it answer")
    if tool == ASSIGN_TOOL:
        made = assign(conn, a["subject"], a["klass"], a["stall"], by=asker, ask=ask_id,
                      parent_marker=parent_marker, confirmed_by=confirmed_by)
        who = "every body" if made["subject"] == "*" else made["subject"]
        return f"{who} now uses the {made['stall']} LLM for {'all its' if made['klass'] == ANY else made['klass']} work — recorded"
    if tool == UNASSIGN_TOOL:
        made = unassign(conn, a["subject"], a["klass"], by=asker, ask=ask_id, parent_marker=parent_marker,
                        confirmed_by=confirmed_by)
        return f"{made['subject']}'s {made['klass']} assignment to {made['stall']} is lifted — recorded"
    if tool == REFILL_TOOL:
        made = refill(conn, a["did"], float(a["usd"]), by=asker, gw=gw, name=a.get("name"), ask=ask_id,
                      parent_marker=parent_marker, confirmed_by=confirmed_by)
        return f"{a.get('name') or a['did']} refilled by ${made['added_usd']:g} — its allowance is now ${made['max_usd']:g}"
    if tool == REPIN_TOOL:
        made = repin_mind(conn, a["name"], a["deal"], by=asker, gw=gw)
        return f"the {made['name']} LLM is re-pinned to its new deal (version {made['version']}) — the old pin stays in its history"
    raise StableRefused(f"no Stable act named {tool!r}")


# ---- the market's eyes: drift and EOL off the catalog ----------------------------------------------------

_catalog_cache: dict = {"at": 0.0, "openrouter": None}


def openrouter_catalog(fetch=None) -> dict[str, dict]:
    """OpenRouter's public list, keyless (0019's intel plane) — by model id:
    price per million in and out, context, expiry when named. Cached 300 s."""
    now = time.monotonic()
    if _catalog_cache["openrouter"] is not None and now - _catalog_cache["at"] < CATALOG_TTL_S:
        return _catalog_cache["openrouter"]
    out: dict[str, dict] = {}
    try:
        if fetch is None:
            with urllib.request.urlopen(urllib.request.Request(OPENROUTER_CATALOG, headers={"accept": "application/json"}),
                                        timeout=15) as r:
                data = json.loads(r.read())
        else:
            data = fetch()
        for m in data.get("data", []):
            pr = m.get("pricing") or {}
            try:
                out[str(m.get("id"))] = {
                    "price": {"in_per_m": round(float(pr.get("prompt") or 0) * 1e6, 6),
                              "out_per_m": round(float(pr.get("completion") or 0) * 1e6, 6)},
                    "context": m.get("context_length"),
                    "expires": m.get("expiration_date") or m.get("deprecation_date")}
            except (TypeError, ValueError):
                continue
    except Exception:                                # noqa: BLE001 — intel never authority; missing ≠ dead
        return _catalog_cache["openrouter"] or {}
    _catalog_cache.update(at=now, openrouter=out)
    return out


def seen_deal(gw: Gateway | None, s: dict, catalog: dict | None = None) -> dict | None:
    """What the market says of this stall now: OpenRouter's catalog for an
    openrouter route (price, context, expiry); the gateway's own price map
    for the rest."""
    m = s.get("manifest") or {}
    if m.get("provider") == "openrouter":
        row = (catalog if catalog is not None else openrouter_catalog()).get(m.get("model"))
        return dict(row) if row else None
    if gw is None:
        return None
    try:
        return gw.seen_deal(s["name"])
    except GatewayDark:
        return None


def drift_scan(conn, gw: Gateway | None, *, by: str, catalog: dict | None = None) -> list[dict]:
    """Every standing stall's pin against the market: a move is recorded
    as UNHEALTHY with what moved (the rug-pull door, 0019) — never
    re-pinned by the machine."""
    out = []
    for s in services.listing(conn, kind="mind"):
        if s["state"] == "retired":
            continue
        seen = seen_deal(gw, s, catalog)
        if not seen:
            continue
        pin = s["manifest"]
        if not (pin.get("price") or {}).get("in_per_m") and not (pin.get("price") or {}).get("out_per_m"):
            continue                                  # a stall pinned without a price: nothing to drift from
        moved = drift(pin, seen)
        if moved:
            services.record_health(conn, s["name"], False, "the deal moved under the pin: " + "; ".join(moved), by=by)
            out.append({"name": s["name"], "moved": moved,
                        "deal": dict(pin, price={"in_per_m": seen["price"].get("in_per_m", pin["price"]["in_per_m"]),
                                                 "out_per_m": seen["price"].get("out_per_m", pin["price"]["out_per_m"])},
                                     context=seen.get("context") or pin.get("context"))})
    return out


def eol_scan(conn, gw: Gateway | None, *, now: datetime | None = None, catalog: dict | None = None) -> list[dict]:
    """Every standing stall whose catalog expiry is inside the horizon,
    with the swap the Stable recommends."""
    now = now or datetime.now(timezone.utc)
    horizon = _dial(EOL_DIAL, EOL_DEFAULT, int)
    rows = services.listing(conn, kind="mind")
    out = []
    for s in rows:
        if s["state"] == "retired":
            continue
        seen = seen_deal(gw, s, catalog) or {}
        exp = seen.get("expires") or (s["manifest"] or {}).get("expires")
        due = eol_due(exp, now, horizon)
        if due["due"]:
            out.append({"name": s["name"], "expires": exp, "words": due["words"], "swap": recommend(rows, s["name"])})
    return out


def _last_hold(conn, tool: str, name: str) -> dict | None:
    cur = conn.cursor()
    cur.execute("SELECT ask_id, status FROM spine_asks WHERE scope = %s AND served_by = %s AND held IS NOT NULL"
                " AND held::json->>'tool' = %s AND (held::json->'args'->>'name' = %s OR held::json->'args'->>'did' = %s)"
                " ORDER BY asked_at DESC LIMIT 1", (ev.scope(), services.KERNEL, tool, name, name))
    r = cur.fetchone()
    return {"ask_id": r[0], "status": r[1]} if r else None


def proposals(conn, *, keeper: str, gw: Gateway | None, catalog: dict | None = None,
              now: datetime | None = None) -> list[dict]:
    """The keeper's proposals, each ONE hold at the interlock (none while
    one waits): a drifted deal → re-pin; an expiring mind → retire, with
    the swap named; a drained body → refill; and the strikes rule for
    minds (mcp.proposals, the toolkeeper's law, the stablekeeper's word)."""
    from . import mcp
    out = []
    for d in drift_scan(conn, gw, by=keeper, catalog=catalog):
        prev = _last_hold(conn, REPIN_TOOL, d["name"])
        if prev and prev["status"] == "awaiting-confirm":
            continue
        out.append({"kind": "repin", "name": d["name"], "held": hold(
            conn, REPIN_TOOL, {"name": d["name"], "deal": d["deal"]}, person=keeper,
            text=f"the stablekeeper proposes re-pinning the {d['name']} LLM — " + "; ".join(d["moved"]))})
    for e in eol_scan(conn, gw, now=now, catalog=catalog):
        prev = _last_hold(conn, services.RETIRE_TOOL, e["name"])
        if prev and prev["status"] == "awaiting-confirm":
            continue
        swap = e["swap"]
        out.append({"kind": "retire", "name": e["name"], "held": hold(
            conn, services.RETIRE_TOOL, {"name": e["name"]}, person=keeper,
            text=f"the stablekeeper proposes retiring the {e['name']} LLM — it {e['words']}"
                 + (f"; the swap: the {swap['stall']} LLM ({swap['why']})" if swap.get("stall") else f"; {swap['why']}"))})
    cur = conn.cursor()
    cur.execute("SELECT k.did, k.alias, k.max_usd FROM spine_mind_keys k WHERE k.scope = %s AND k.drained_at IS NOT NULL",
                (ev.scope(),))
    for did, alias, max_usd in cur.fetchall():
        prev = _last_hold(conn, REFILL_TOOL, did)
        if prev and prev["status"] == "awaiting-confirm":
            continue
        name = alias.split(":")[-1]
        out.append({"kind": "refill", "name": name, "held": hold(
            conn, REFILL_TOOL, {"did": did, "name": name, "usd": max(1.0, float(max_usd))}, person=keeper,
            text=f"the stablekeeper proposes refilling {name} by ${max(1.0, float(max_usd)):g} — its allowance is spent and it cannot think")})
    for p in mcp.proposals(conn, keeper=keeper, kinds=("mind",), who="the stablekeeper"):
        out.append({"kind": "retire", "name": p["name"], "held": p["held"], "strikes": p["strikes"]})
    return out


def keeper_beat(conn, *, keeper: str, gateway=None, gw: Gateway | None = None, catalog: dict | None = None,
                now: datetime | None = None) -> dict:
    """The keeper's beat (the rig runs it on the scheduler's clock under
    the keeper's DID): every standing mind pinged through the gateway
    under the keeper's DID (metered), then the market's eyes, then the
    proposals."""
    checked = services.check_all(conn, kind="mind", gateway=gateway, by=keeper)
    return {"checked": checked, "proposed": proposals(conn, keeper=keeper, gw=gw, catalog=catalog, now=now)}


# ---- search and spend: the Stable's own doors ---------------------------------------------------------

def search(conn, q: str | None = None, *, klass: str | None = None, max_in_per_m: float | None = None,
           modality: str | None = None, standing_only: bool = False) -> list[dict]:
    """Which mind knows or does what: by words (name · model · provider),
    class, ceiling price, modality."""
    words = (q or "").strip().lower()
    out = []
    for s in stalls(conn):
        m = s["manifest"] or {}
        if standing_only and not _standing(s):
            continue
        if klass and m.get("class") != klass:
            continue
        if max_in_per_m is not None and float((m.get("price") or {}).get("in_per_m", 0.0)) > float(max_in_per_m):
            continue
        if modality and modality not in (m.get("modalities") or []):
            continue
        hay = " ".join([s["name"], m.get("model") or "", m.get("provider") or "", m.get("class") or "",
                        " ".join(m.get("modalities") or [])]).lower()
        if words and not all(w in hay for w in words.split()):
            continue
        out.append(s)
    return out


def stall_words(s: dict) -> str:
    m = s.get("manifest") or {}
    pr = m.get("price") or {}
    sp = s.get("spend") or {}
    return (f"{s['name']} — {m.get('provider')} {m.get('model')} · {m.get('class')} · "
            f"${pr.get('in_per_m', 0):g} in / ${pr.get('out_per_m', 0):g} out per million"
            + (f" · context {int(m['context']):,}" if m.get("context") else "")
            + f" · {s['state']}"
            + (f" · spent ${sp.get('usd', 0):.4f} over {sp.get('calls', 0)} call{'s' if sp.get('calls', 0) != 1 else ''}"
               if sp.get("calls") else " · never called"))


def spend(conn) -> dict:
    """The meter rolled up: per body, per mind — today and all time."""
    from .gateway import ensure_schema as _meter
    _meter(conn)
    cur = conn.cursor()
    cur.execute("SELECT did, coalesce(stall, model), count(*), coalesce(sum(usd), 0),"
                " coalesce(sum(usd) FILTER (WHERE at >= date_trunc('day', now())), 0), sum(tokens_in), sum(tokens_out),"
                " count(*) FILTER (WHERE ok = false)"
                " FROM spine_meter GROUP BY did, coalesce(stall, model) ORDER BY 4 DESC")
    rows = [{"did": r[0], "stall": r[1], "calls": int(r[2]), "usd": float(r[3]), "usd_today": float(r[4]),
             "tokens_in": int(r[5] or 0), "tokens_out": int(r[6] or 0), "failed": int(r[7])} for r in cur.fetchall()]
    return {"rows": rows, "usd": round(sum(r["usd"] for r in rows), 6),
            "usd_today": round(sum(r["usd_today"] for r in rows), 6)}


def reconcile(conn, gw: Gateway | None, n: int = 20, grace_s: int = 30) -> dict:
    """The 100%, thought by thought: the last N metered thoughts of each of
    this world's bodies against the gateway's ledger for the same request
    ids — every line must have its row there wearing the same dollars. A
    line younger than the grace is "not yet flushed" (the ledger lands
    asynchronously), never a wound. Named in words."""
    ensure_schema(conn)
    cur = conn.cursor()
    cur.execute("SELECT to_regclass('spine_mind_keys') IS NOT NULL AND to_regclass('spine_meter') IS NOT NULL")
    if not cur.fetchone()[0]:
        return {"checked": 0, "agreed": 0, "fresh": 0, "mismatched": [], "meter_usd": 0.0, "gateway_usd": 0.0,
                "words": "no lease and no meter on this ground yet"}
    cur.execute("SELECT did FROM spine_mind_keys WHERE scope = %s", (ev.scope(),))
    dids = [r[0] for r in cur.fetchall()]
    out = {"checked": 0, "agreed": 0, "fresh": 0, "unkeyed": 0, "mismatched": [], "meter_usd": 0.0, "gateway_usd": 0.0}
    if gw is None:
        return dict(out, words="no gateway to reconcile against")
    for did in dids:
        cur.execute("SELECT request_id, usd, stall, extract(epoch FROM (clock_timestamp() - at)) FROM spine_meter"
                    " WHERE did = %s AND ok AND request_id IS NOT NULL ORDER BY meter_id DESC LIMIT %s", (did, n))
        mine = cur.fetchall()
        if not mine:
            continue
        try:
            theirs = {r.get("request_id"): r for r in gw.spend_logs(user_id=did)}
        except GatewayDark as e:
            return dict(out, words=str(e))
        for rid, usd_, stall, age in mine:
            if not str(rid).startswith("chatcmpl-"):      # metered before the ledger's own id was kept (2026-09-24):
                out["unkeyed"] += 1                       # not comparable, said so — never a wound, never hidden
                continue
            out["checked"] += 1
            out["meter_usd"] += float(usd_ or 0.0)
            row = theirs.get(rid)
            if row is None:
                if float(age or 0) < grace_s:
                    out["fresh"] += 1
                else:
                    out["mismatched"].append({"request_id": rid, "stall": stall, "meter_usd": usd_, "gateway_usd": None,
                                              "why": "no row in the gateway's ledger"})
                continue
            gusd = float(row.get("spend") or 0.0)
            out["gateway_usd"] += gusd
            if abs(gusd - float(usd_ or 0.0)) <= 1e-6:
                out["agreed"] += 1
            else:
                out["mismatched"].append({"request_id": rid, "stall": stall, "meter_usd": usd_, "gateway_usd": gusd,
                                          "why": "the dollars differ"})
    out["meter_usd"], out["gateway_usd"] = round(out["meter_usd"], 6), round(out["gateway_usd"], 6)
    m = out["mismatched"]
    older = f" · {out['unkeyed']} older thought{'s' if out['unkeyed'] != 1 else ''} not comparable (metered before the ledger's id was kept)" if out["unkeyed"] else ""
    if not out["checked"]:
        out["words"] = "no thought metered yet" + older
    elif not m:
        out["words"] = (f"the meter and the gateway agree on {out['agreed']} of the last {out['checked']} thoughts"
                        + (f" ({out['fresh']} not yet flushed)" if out["fresh"] else "") + older)
    else:
        zero = [x for x in m if x["gateway_usd"] == 0.0]
        out["words"] = (f"{len(m)} of the last {out['checked']} thoughts disagree — "
                        + (f"{len(zero)} charged $0 by the gateway (streamed before the entry named its base model); " if zero else "")
                        + f"the meter reads ${out['meter_usd']:.4f}, the gateway ${out['gateway_usd']:.4f}" + older)
    return out


# ---- the built-in stall, at birth ------------------------------------------------------------------

DEFAULT_STALL = ("haiku", "claude-haiku-4-5-20251001", "anthropic")


def seed(conn, gw: Gateway | None, *, home=services._UNSET) -> dict:
    """The rig's own mind: the default model every template names,
    registered as the `haiku` stall with the deal the gateway's price map
    reads — the same self every boot; a gateway that refuses is named,
    never a crash."""
    name, model, provider = DEFAULT_STALL
    retired = []
    for s in services.listing(conn, kind="mind"):      # the old world's built-in mind (sp1: {route, model}, no deal)
        if s["state"] != "retired" and "provider" not in (s.get("manifest") or {}) and s["name"] != name:
            try:                                          # superseded by the Stable: at rest, recorded, never deleted
                services.retire(conn, s["name"], by=services.KERNEL)
                retired.append(s["name"])
            except services.ServiceRefused:
                pass
    try:
        d = deal(model, provider, klass="fast")
        if gw is not None:
            gw.add_stall(name, d)
            seen = gw.seen_deal(name) or {}
            if (seen.get("price") or {}).get("in_per_m") is not None:
                d = deal(model, provider, klass="fast", price=seen["price"], context=seen.get("context"),
                         modalities=seen.get("modalities"))
        row = services.get(conn, name)
        if row is not None and row["state"] != "retired" and row["manifest_hash"] != services.pin(d):
            services.version(conn, name, d, by=services.KERNEL)      # the price map moved since last boot
            return {"registered": [], "versioned": [name], "refused": [], "retired": retired}
        before = row is None
        services.register(conn, name, "mind", d, by=services.KERNEL, secrets_with=[d["key"]] if d.get("key") else None,
                          home=home)
        return {"registered": [name] if before else [], "versioned": [], "refused": [], "retired": retired}
    except (services.ServiceRefused, StableRefused, GatewayDark) as e:
        return {"registered": [], "versioned": [], "refused": [f"{name}: {e}"], "retired": retired}
