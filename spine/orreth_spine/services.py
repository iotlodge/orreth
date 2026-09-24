# PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P6.5 sp1, the services registry · 2026-09-22
# Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P6.5 sp2, the Tools keeper: the mcp probe is real; record_health; the rig's HOME · 2026-09-23
# Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P6.5 sp3, the Stable keeper · 2026-09-24
"""The services registry v0 (canon 0005 P6.5 sp1 · 0009 §3 "one ladder, two
keepers" · 0018 services as identities · 0059 the env-secrets law).

ONE registry for every service the kernel governs — `tool · mcp · store ·
source · mind` — each an IDENTITY: a DID minted with identity.py's
machinery (`did:orreth:service:…`), its seed persisted under
`<home>/<name>/seed` so the same service re-registers as the SAME self in
every life (covenant rule 1; ephemeral only in tests), a MANIFEST PIN
(sha256 over the canonical bytes of what it declared: a tool's schema, a
mind's route + model, an MCP server's listed tools, a store's or source's
locator by NAME), a PLACEMENT profile honored at register exactly as a
body's is at birth (P6 sp4), and its secrets by NAME only — a key lives in
ZERO records; a named secret the ground cannot reach refuses the register
by name and records nothing.

One LADDER, one legality, for every kind:

    registered → versioned(n) → healthy | unhealthy → retired
                                                ↑ restore ┘

`ladder_step` is the pure law (fixture `services-v0.json`): a step the
ladder does not allow is refused with the reason in words. Retired is
DORMANCY, never deletion (the roster law): the row and every fact stay,
and the human's "restore" is a new fact. Every state change lands as a fact
through the outbox with the chain and a marker — `orreth.service.
registered.v1 · .versioned.v1 · .health.v1 · .retired.v1 · .restored.v1`.
Retiring is CONSEQUENTIAL (L2): the door holds it at the interlock as one
of the kernel's own acts (`proof.hold_kernel_act`, tool `service.retire`)
and the kernel settles it on the human's deliberate yes.

The meter reads the ladder (rule 5, one door): `spine_meter` rows and
`spine_tool_calls` rows carry the SERVICE DID when the mind or tool is
registered, and the export's tool hop reads that DID instead of
`tool:<name>` (which stays the honest fallback for an unregistered tool).
Health is the kind's honest probe: a tool — the door answers `describe`
and its schema matches the pin; a mind — the gateway answers a one-token
ping under the service's own DID, through the meter; a store or source —
its locator is reachable by NAME; an mcp — initialize + tools/list through
the one MCP door (mcp.py, P6.5 sp2), its listed tools synced onto the
shelf as services of kind tool placed under it.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

from . import envelope as ev, outbox, placement as _placement
from .identity import Identity

KINDS = ("tool", "mcp", "store", "source", "mind")
STATES = ("registered", "versioned", "healthy", "unhealthy", "retired")
VERBS = ("register", "version", "healthy", "unhealthy", "retire", "restore")
LADDER_WORDS = ("the ladder: registered → versioned(n) → healthy | unhealthy → retired; "
                "restore returns a retired service to registered")

REGISTERED = "orreth.service.registered.v1"
VERSIONED = "orreth.service.versioned.v1"
HEALTH = "orreth.service.health.v1"
RETIRED = "orreth.service.retired.v1"
RESTORED = "orreth.service.restored.v1"
FACT_OF = {"register": REGISTERED, "version": VERSIONED, "healthy": HEALTH,
           "unhealthy": HEALTH, "retire": RETIRED, "restore": RESTORED}

KERNEL = "the kernel"
_UNSET = object()                                # "use the rig's HOME" (P6.5 sp2: the keeper's door has no home of its own)
HOME: str | os.PathLike | None = None            # where the rig keeps the services' seeds; None = ephemeral (tests)
RETIRE_TOOL = "service.retire"                   # the kernel's own held act
RETIRE_CLASS, RETIRE_LEVEL = "consequential", "L2"
GROUND_LOCATOR = "SPINE_PG"                      # the ground's dial (rails.py); a default stands


class ServiceRefused(ValueError):
    """The registry's refusal — the reason in plain words (the owner's door)."""


# ---- the ladder (the pure law; the fixture's) ------------------------------------------

def ladder_step(state: str | None, verb: str) -> dict:
    """The one legality: from `state` (None = not registered) may `verb`
    step, and to where? {ok, to, reason} — the reason names the step and
    the state it was refused from, in words a newcomer reads."""
    if verb not in VERBS:
        return {"ok": False, "to": None,
                "reason": f"no step named {verb!r} on the ladder — the steps: " + ", ".join(VERBS)}
    if state is None:
        if verb == "register":
            return {"ok": True, "to": "registered", "reason": None}
        return {"ok": False, "to": None,
                "reason": f"not registered — {verb} is not a step from there; register it first"}
    if state not in STATES:
        return {"ok": False, "to": None, "reason": f"unknown state {state!r} — {LADDER_WORDS}"}
    if state == "retired":
        if verb == "restore":
            return {"ok": True, "to": "registered", "reason": None}
        if verb == "register":
            return {"ok": False, "to": None,
                    "reason": "retired — a retired service is restored, never registered twice"}
        if verb == "retire":
            return {"ok": False, "to": None, "reason": "already retired — nothing to retire"}
        return {"ok": False, "to": None,
                "reason": f"retired — the ladder runs no {verb} on a retired service; restore it first"}
    if verb == "register":
        return {"ok": False, "to": None,
                "reason": f"already {state} — version it when its manifest changes, never register it twice"}
    if verb == "restore":
        return {"ok": False, "to": None, "reason": f"{state}, not retired — nothing to restore"}
    if verb == "version":
        return {"ok": True, "to": "versioned", "reason": None}
    if verb in ("healthy", "unhealthy"):
        return {"ok": True, "to": verb, "reason": None}
    return {"ok": True, "to": "retired", "reason": None}        # retire


def pin(manifest: dict) -> str:
    """The manifest pin: sha256 over the canonical bytes (0000 §3)."""
    return ev.content_hash(manifest)


def _refuse_step(name: str, state: str | None, verb: str) -> None:
    st = ladder_step(state, verb)
    if not st["ok"]:
        raise ServiceRefused(f"the {name} service is {st['reason']}")


# ---- the record ------------------------------------------------------------------------

def ensure_schema(conn) -> None:
    if not outbox.once(conn, "services"):
        return
    with conn.transaction():
        cur = conn.cursor()
        cur.execute("SELECT pg_advisory_xact_lock(742199)")  # DDL race guard
        cur.execute(
            "CREATE TABLE IF NOT EXISTS spine_services ("
            " name text NOT NULL, scope text NOT NULL, kind text NOT NULL, did text NOT NULL,"
            " manifest text NOT NULL, manifest_hash text NOT NULL, version int NOT NULL DEFAULT 1,"
            " placement text NOT NULL, secrets_with text NOT NULL DEFAULT '[]',"
            " state text NOT NULL, by_did text NOT NULL,"
            " since timestamptz NOT NULL DEFAULT now(),"
            " registered_at timestamptz NOT NULL DEFAULT now(),"
            " last_ok boolean, last_detail text, last_checked_at timestamptz,"
            " marker text, root_marker text, PRIMARY KEY (name, scope))")
        cur.execute(
            "CREATE TABLE IF NOT EXISTS spine_service_versions ("
            " version_id bigserial PRIMARY KEY, name text NOT NULL, scope text NOT NULL,"
            " version int NOT NULL, manifest text NOT NULL, manifest_hash text NOT NULL,"
            " by_did text NOT NULL, at timestamptz NOT NULL DEFAULT now())")
        cur.execute(
            "CREATE TABLE IF NOT EXISTS spine_service_health ("
            " health_id bigserial PRIMARY KEY, name text NOT NULL, scope text NOT NULL,"
            " did text NOT NULL, ok boolean, detail text NOT NULL,"
            " at timestamptz NOT NULL DEFAULT now())")
        cur.execute("CREATE INDEX IF NOT EXISTS spine_services_kind ON spine_services (scope, kind)")
        # a ground born before the shelf had one origin grows the column (the public ground did)
        cur.execute("ALTER TABLE spine_services ADD COLUMN IF NOT EXISTS root_marker text")


def _row(r) -> dict:
    m = json.loads(r[4]); prof = json.loads(r[7]); secrets = json.loads(r[8] or "[]")
    return {"name": r[0], "kind": r[2], "did": r[3], "manifest": m, "manifest_hash": r[5],
            "version": int(r[6]), "placement": prof, "secrets_with": secrets, "state": r[9],
            "by": r[10], "since": r[11].isoformat(), "registered_at": r[12].isoformat(),
            "last_health": ({"ok": r[13], "detail": r[14], "at": r[15].isoformat()}
                            if r[15] is not None else None),
            "marker": r[16], "root_marker": r[17]}


_COLS = ("name, scope, kind, did, manifest, manifest_hash, version, placement, secrets_with,"
         " state, by_did, since, registered_at, last_ok, last_detail, last_checked_at, marker, root_marker")


def get(conn, name: str) -> dict | None:
    ensure_schema(conn)
    cur = conn.cursor()
    cur.execute(f"SELECT {_COLS} FROM spine_services WHERE name = %s AND scope = %s", (name, ev.scope()))
    r = cur.fetchone()
    return _row(r) if r else None


def did_of(conn, kind: str, name: str) -> str | None:
    """The service's DID by kind and name — retired or not (a self is a
    self; the ladder says its state). None when nothing is registered."""
    ensure_schema(conn)
    cur = conn.cursor()
    cur.execute("SELECT did FROM spine_services WHERE scope = %s AND kind = %s AND name = %s",
                (ev.scope(), kind, name))
    r = cur.fetchone()
    return r[0] if r else None


def state_of(conn, kind: str, name: str) -> str | None:
    ensure_schema(conn)
    cur = conn.cursor()
    cur.execute("SELECT state FROM spine_services WHERE scope = %s AND kind = %s AND name = %s",
                (ev.scope(), kind, name))
    r = cur.fetchone()
    return r[0] if r else None


def mind_did(conn, model: str) -> str | None:
    """The mind service whose manifest names this model — what a meter
    row carries (rule 5: the meter reads the ladder)."""
    ensure_schema(conn)
    cur = conn.cursor()
    cur.execute("SELECT did FROM spine_services WHERE scope = %s AND kind = 'mind'"
                " AND manifest::json->>'model' = %s ORDER BY registered_at LIMIT 1", (ev.scope(), model))
    r = cur.fetchone()
    return r[0] if r else None


def stall_did(conn, stall: str) -> str | None:
    """P6.5 sp3: the mind service by its stall NAME — what a dollar meter row carries."""
    ensure_schema(conn)
    cur = conn.cursor()
    cur.execute("SELECT did FROM spine_services WHERE scope = %s AND kind = 'mind' AND name = %s", (ev.scope(), stall))
    r = cur.fetchone()
    return r[0] if r else None


SHELF_REF = "the shelf"


def shelf_root(conn) -> str:
    """ONE origin per world for the shelf (P25's Analyzer reads roots):
    "the kernel keeps the shelf" — every service's register hangs under
    it, every later step under its service. Minted once; a health probe
    is never a new root (found in the suite: nine probes per rig boot
    pushed Resiliency off the Analyzer's newest-60)."""
    from . import markers
    markers.ensure_schema(conn)
    cur = conn.cursor()
    cur.execute("SELECT marker_id FROM spine_markers WHERE scope = %s AND parent IS NULL"
                " AND kind = 'observation' AND ref = %s AND by_did = %s ORDER BY at LIMIT 1",
                (ev.scope(), SHELF_REF, KERNEL))
    r = cur.fetchone()
    if r:
        return r[0]
    mid = markers.new_id()
    with conn.transaction():
        markers.insert(conn.cursor(), mid, "observation", None, SHELF_REF, KERNEL,
                       "the kernel keeps the shelf — every service it governs, on one ladder")
    return mid


def _fact(conn, verb: str, svc: dict, by: str, *, extra: dict | None = None,
          parent_marker: str | None = None, ask: str | None = None, domain=None,
          confirmed_by: str | None = None) -> dict:
    """Every state change is a fact: the envelope (the chain: the actor,
    then the kernel; a marker — an ACTION under the ask that released it,
    else an OBSERVATION under the service's own register, itself under
    the world's one shelf root) and the domain writes land in ONE
    transaction through the outbox."""
    from . import markers
    markers.ensure_schema(conn); outbox.ensure_schema(conn)
    mid = markers.new_id()
    kind = "action" if ask else "observation"
    parent_marker = parent_marker or svc.get("root_marker") or shelf_root(conn)
    marker = {"kind": kind, "id": mid, "parent": parent_marker, "by": by}
    chain = [by] if by == KERNEL else [by, KERNEL]
    if confirmed_by and confirmed_by != by:          # P6.5 sp2: a body proposed, the human cut — both on the chain
        chain = [by, confirmed_by, KERNEL]
    payload = {"ref": svc["did"], "hash": svc["manifest_hash"], "name": svc["name"],
               "kind": svc["kind"], "version": svc["version"], "state": svc["state"], "by": by}
    payload.update(extra or {})
    e = ev.make_envelope(
        kind="event", type=FACT_OF[verb], universe_id=ev.scope(), scope_path=ev.scope(),
        payload=payload, correlation_id=ask or svc["did"], authority_chain=chain, marker=marker)

    def _domain(cur):
        markers.insert(cur, mid, kind, parent_marker, ask or svc["did"], by,
                       f"{svc['name']} ({svc['kind']}) {verb}: {svc['state']}"
                       + (f" — {extra['detail']}" if extra and extra.get("detail") else ""))
        if domain is not None:
            domain(cur, mid)

    outbox.commit_with_outbox(conn, ev.encode(e), e["message_id"], _domain)
    return {"marker": mid, "message_id": e["message_id"]}


def _validate(name: str, kind: str, manifest) -> None:
    n = (name or "").strip()
    if not n or not n.replace("-", "").replace("_", "").replace(".", "").isalnum() or n != n.lower():
        raise ServiceRefused("a service name is a short lowercase name: letters, digits, dashes, dots")
    if kind not in KINDS:
        raise ServiceRefused(f"a service kind is one of {', '.join(KINDS)} — not {kind!r}")
    if not isinstance(manifest, dict) or not manifest:
        raise ServiceRefused("a manifest is a non-empty object: what the service declares "
                             "(a tool's schema, a mind's route and model, an mcp server's tools, "
                             "a store's or source's locator by NAME)")


def register(conn, name: str, kind: str, manifest: dict, *, by: str = KERNEL,
             placement: dict | None = None, secrets_with: list[str] | None = None,
             home: str | os.PathLike | None = _UNSET) -> dict:
    """The first rung: the service becomes an identity on this ground.
    Placement (with its secrets by NAME) is honored FIRST — a refusal
    records nothing (the env-secrets law: a key in ZERO records, and no
    row for a service the ground cannot seat). Registering the same
    service again with the same manifest is the same self, silently; a
    changed manifest is refused by name ("version it")."""
    _validate(name, kind, manifest)
    raw = dict(placement or {})
    raw["secrets_with"] = sorted(set(list(raw.get("secrets_with") or []) + list(secrets_with or [])))
    try:
        prof = _placement.profile({"placement": raw})
    except ValueError as e:
        raise ServiceRefused(str(e))
    ground = _placement.ground_declares()
    ok, reasons = _placement.honor(prof, ground)
    if not ok:
        raise ServiceRefused(f"{name} is refused here: " + "; ".join(reasons))
    ensure_schema(conn)
    h = pin(manifest)
    row = get(conn, name)
    if row is not None:
        if row["state"] != "retired" and row["kind"] == kind and row["manifest_hash"] == h:
            return row                              # the same self, every life (rule 1)
        if row["state"] != "retired" and row["kind"] != kind:
            raise ServiceRefused(f"the {name} service is already registered as a {row['kind']} — "
                                 f"a name wears one kind; {kind} needs its own name")
        _refuse_step(name, row["state"], "register")
    ident = Identity.load(name, HOME if home is _UNSET else home, kind="service")
    svc = {"name": name, "kind": kind, "did": ident.did, "manifest": manifest, "manifest_hash": h,
           "version": 1, "placement": prof, "secrets_with": prof["secrets_with"], "state": "registered"}

    def domain(cur, mid):
        cur.execute(
            "INSERT INTO spine_services (name, scope, kind, did, manifest, manifest_hash, version,"
            " placement, secrets_with, state, by_did, since, marker, root_marker)"
            " VALUES (%s, %s, %s, %s, %s, %s, 1, %s, %s, 'registered', %s, clock_timestamp(), %s, %s)",
            (name, ev.scope(), kind, ident.did, ev.canonical(manifest).decode("ascii"), h,
             ev.canonical(prof).decode("ascii"), json.dumps(prof["secrets_with"]), by, mid, mid))
        cur.execute(
            "INSERT INTO spine_service_versions (name, scope, version, manifest, manifest_hash, by_did)"
            " VALUES (%s, %s, 1, %s, %s, %s)",
            (name, ev.scope(), ev.canonical(manifest).decode("ascii"), h, by))

    _fact(conn, "register", svc, by, extra={"placement": prof, "secrets_with": prof["secrets_with"]},
          domain=domain)
    return get(conn, name)


def version(conn, name: str, manifest: dict, *, by: str = KERNEL) -> dict:
    """A changed manifest re-pins the service: version n+1, state
    versioned — the fact carries both hashes. An unchanged manifest is
    refused by name (nothing to version)."""
    row = get(conn, name)
    if row is None:
        raise ServiceRefused(f"no service named {name!r} is registered here — register it first")
    _validate(name, row["kind"], manifest)
    _refuse_step(name, row["state"], "version")
    h = pin(manifest)
    if h == row["manifest_hash"]:
        raise ServiceRefused(f"the {name} service's manifest is unchanged — nothing to version")
    n = row["version"] + 1
    svc = dict(row, manifest=manifest, manifest_hash=h, version=n, state="versioned")

    def domain(cur, mid):
        cur.execute(
            "UPDATE spine_services SET manifest = %s, manifest_hash = %s, version = %s,"
            " state = 'versioned', since = clock_timestamp(), marker = %s"
            " WHERE name = %s AND scope = %s",
            (ev.canonical(manifest).decode("ascii"), h, n, mid, name, ev.scope()))
        cur.execute(
            "INSERT INTO spine_service_versions (name, scope, version, manifest, manifest_hash, by_did)"
            " VALUES (%s, %s, %s, %s, %s, %s)",
            (name, ev.scope(), n, ev.canonical(manifest).decode("ascii"), h, by))

    _fact(conn, "version", svc, by, extra={"previous_hash": row["manifest_hash"]}, domain=domain)
    return get(conn, name)


# ---- health: the kind's honest probe ---------------------------------------------------

def _probe(conn, row: dict, gateway, by: str = KERNEL) -> tuple[bool | None, str]:
    kind, m = row["kind"], row["manifest"]
    if kind == "tool" and m.get("server"):          # P6.5 sp2: an MCP-born tool — its server lists it, or it is gone
        from . import mcp
        return mcp.probe_tool(conn, row)
    if kind == "tool":
        from .tools import TOOLS, tool_manifest
        spec = TOOLS.get(row["name"])
        if spec is None:
            return False, f"the door names no tool called {row['name']!r} on this shelf"
        h = pin(tool_manifest(row["name"], spec))
        if h != row["manifest_hash"]:
            return False, (f"the door describes a different schema than the pin "
                           f"({h[7:19]}… vs {row['manifest_hash'][7:19]}…) — version it")
        return True, "the door answers describe; the schema matches the pin"
    if kind == "mind":
        if gateway is None:
            return None, "not probed — no gateway was handed to the check"
        # P6.5 sp3: the canary ping under the KEEPER's DID (0009 §2), pinned to THIS stall —
        # a pinned mind that does not answer refuses, never climbs (0019); the honest word
        # the lane returns ("I cannot think …") is the verdict, never a stack
        who = by if str(by).startswith("did:") else row["did"]
        try:
            said = gateway.think(conn, did=who, system="Answer with one word.", prompt="ping",
                                 model=m.get("model"), max_tokens=1, pin=row["name"])
        except Exception as e:                       # noqa: BLE001 — the honest verdict
            return False, f"the gateway did not answer: {type(e).__name__}: {str(e)[:140]}"
        if str(said or "").lstrip().lower().startswith("i cannot think") or str(said or "").lstrip().lower().startswith("i am out of fuel"):
            return False, f"the mind did not answer: {str(said)[:160]}"
        return True, f"the gateway answered a one-token ping through the meter ({m.get('route') or m.get('model')})"
    if kind == "mcp":                                # P6.5 sp2: initialize + tools/list, the list synced onto the shelf
        from . import mcp
        return mcp.probe(conn, row, by=by)
    loc = str(m.get("locator") or "")                # store · source: the locator by NAME
    if not loc:
        return False, "the manifest names no locator"
    if loc != GROUND_LOCATOR and not os.environ.get(loc):
        return False, f"the locator {loc} is not reachable by name here"
    if loc == GROUND_LOCATOR:                        # v0: one ground; the record stands on it
        conn.execute("SELECT 1")
        table = m.get("table")
        if table:
            cur = conn.cursor()
            cur.execute("SELECT to_regclass(%s) IS NOT NULL", (str(table),))
            if not cur.fetchone()[0]:
                return False, f"the locator {loc} answers but table {table} does not stand"
            return True, f"the locator {loc} is reachable by name; table {table} stands"
        return True, f"the locator {loc} is reachable by name; the ground answers"
    return True, f"the locator {loc} is reachable by name"


def check(conn, name: str, *, gateway=None, by: str = KERNEL) -> dict:
    """The kind's probe, recorded: a health row and the fact; the ladder
    steps to healthy or unhealthy — or stays where it is when the kind
    is not yet probed (ok null, said honestly)."""
    row = get(conn, name)
    if row is None:
        raise ServiceRefused(f"no service named {name!r} is registered here — the shelf lists them")
    _refuse_step(name, row["state"], "healthy")
    ok, detail = _probe(conn, row, gateway, by)
    return record_health(conn, name, ok, detail, by=by)


def record_health(conn, name: str, ok: bool | None, detail: str, *, by: str = KERNEL) -> dict:
    """A health verdict recorded without a probe (P6.5 sp2: an MCP
    server's listing says which of its tools stand and which are gone —
    one session, every tool's verdict): the health row and the fact; the
    ladder steps to healthy or unhealthy. The row is re-read first — a
    probe may have versioned the service under its own feet."""
    row = get(conn, name)
    if row is None:
        raise ServiceRefused(f"no service named {name!r} is registered here — the shelf lists them")
    _refuse_step(name, row["state"], "healthy")
    verb = "healthy" if ok else "unhealthy" if ok is False else None
    state = ladder_step(row["state"], verb)["to"] if verb else row["state"]
    svc = dict(row, state=state)

    def domain(cur, mid):
        cur.execute(
            "INSERT INTO spine_service_health (name, scope, did, ok, detail) VALUES (%s, %s, %s, %s, %s)",
            (name, ev.scope(), row["did"], ok, detail))
        cur.execute(
            "UPDATE spine_services SET state = %s, since = CASE WHEN state = %s THEN since ELSE clock_timestamp() END,"
            " last_ok = %s, last_detail = %s, last_checked_at = clock_timestamp()"
            " WHERE name = %s AND scope = %s", (state, state, ok, detail, name, ev.scope()))

    _fact(conn, verb or "healthy", svc, by, extra={"ok": ok, "detail": detail}, domain=domain)
    if ok:
        withdraw_stale_proposals(conn, name)          # W49 (walk #12): a proposal whose reason passed withdraws itself
    return {"name": name, "kind": row["kind"], "did": row["did"], "ok": ok, "detail": detail, "state": state}


def withdraw_stale_proposals(conn, name: str) -> list[str]:
    """W49: a keeper proposed retiring this service for being unhealthy;
    it is healthy again — the kernel withdraws the waiting proposal with
    the reason in words (a recorded cancel, never a deletion), so no
    stale hold waits on the human."""
    from .proof import settle_kernel_act, NotConfirmed
    cur = conn.cursor()
    cur.execute("SELECT to_regclass('spine_asks') IS NOT NULL")
    if not cur.fetchone()[0]:
        return []
    cur.execute("SELECT ask_id FROM spine_asks WHERE scope = %s AND served_by = %s AND status = 'awaiting-confirm'"
                " AND held IS NOT NULL AND held::json->>'tool' = %s AND held::json->'args'->>'name' = %s"
                " AND person LIKE 'did:orreth:agent:%%'", (ev.scope(), KERNEL, RETIRE_TOOL, name))
    out = []
    for (aid,) in cur.fetchall():
        try:
            settle_kernel_act(conn, aid, approve=False, by=KERNEL,
                              reason=f"withdrawn — the {name} service answered its check and is healthy again; nothing to retire")
            out.append(aid)
        except NotConfirmed:
            pass
    return out


def check_all(conn, *, gateway=None, kind: str | None = None, by: str = KERNEL) -> list[dict]:
    """Every standing service probed (a retired one is left at rest)."""
    out = []
    for s in listing(conn, kind=kind):
        if s["state"] == "retired":
            continue
        out.append(check(conn, s["name"], gateway=gateway, by=by))
    return out


# ---- retire (dormancy, never deletion) and restore ---------------------------------------

def hold_retire(conn, name: str, *, person: str, session: str | None = None) -> str:
    """Retiring is consequential (L2): the kernel holds it at the
    interlock as its own act — the human's deliberate yes settles it
    (`proof.settle_kernel_act` → `retire`); cancel is the default."""
    from .proof import hold_kernel_act
    row = get(conn, name)
    _refuse_step(name, row["state"] if row else None, "retire")
    return hold_kernel_act(conn, text=f"retiring the {name} {row['kind']}", person=person,
                           tool=RETIRE_TOOL, args={"name": name}, level=RETIRE_LEVEL,
                           session=session, cls=RETIRE_CLASS)


def retire(conn, name: str, *, by: str, ask: str | None = None,
           parent_marker: str | None = None, confirmed_by: str | None = None) -> dict:
    """The rung down: state retired, since now — the row, its versions,
    its health and every fact STAY (the roster law: dormancy, never
    deletion). The fact hangs under the held ask's marker when the
    interlock released it."""
    row = get(conn, name)
    _refuse_step(name, row["state"] if row else None, "retire")
    svc = dict(row, state="retired")

    def domain(cur, mid):
        cur.execute("UPDATE spine_services SET state = 'retired', since = clock_timestamp(), marker = %s"
                    " WHERE name = %s AND scope = %s", (mid, name, ev.scope()))

    _fact(conn, "retire", svc, by, extra={"from": row["state"]}, parent_marker=parent_marker,
          ask=ask, domain=domain, confirmed_by=confirmed_by)
    return get(conn, name)


def restore(conn, name: str, *, by: str) -> dict:
    """The human's restore — a NEW fact: the service stands registered
    again (its version and its history whole); its stop stays in the record."""
    row = get(conn, name)
    _refuse_step(name, row["state"] if row else None, "restore")
    svc = dict(row, state="registered")

    def domain(cur, mid):
        cur.execute("UPDATE spine_services SET state = 'registered', since = clock_timestamp(),"
                    " marker = %s WHERE name = %s AND scope = %s", (mid, name, ev.scope()))

    _fact(conn, "restore", svc, by, domain=domain)
    return get(conn, name)


# ---- the shelf ---------------------------------------------------------------------------

def listing(conn, kind: str | None = None) -> list[dict]:
    """Every service in this world — the shelf's door: the ladder state
    with its since, the placement why-line, secrets by NAME reached or
    not, the last health."""
    ensure_schema(conn)
    here = _placement.ground_declares()
    cur = conn.cursor()
    cur.execute(f"SELECT {_COLS} FROM spine_services WHERE scope = %s AND (%s::text IS NULL OR kind = %s)"
                " ORDER BY kind, name", (ev.scope(), kind, kind))
    out = []
    for r in cur.fetchall():
        s = _row(r)
        s["placement"] = _placement.card(s["placement"], here)
        s["secrets"] = s["placement"]["secrets"]
        s["retirable"] = ladder_step(s["state"], "retire")["ok"]
        s["restorable"] = ladder_step(s["state"], "restore")["ok"]
        out.append(s)
    return out


def versions(conn, name: str) -> list[dict]:
    ensure_schema(conn)
    cur = conn.cursor()
    cur.execute("SELECT version, manifest_hash, by_did, at FROM spine_service_versions"
                " WHERE name = %s AND scope = %s ORDER BY version", (name, ev.scope()))
    return [{"version": r[0], "manifest_hash": r[1], "by": r[2], "at": r[3].isoformat()}
            for r in cur.fetchall()]


def health(conn, name: str, limit: int = 10) -> list[dict]:
    ensure_schema(conn)
    cur = conn.cursor()
    cur.execute("SELECT ok, detail, at FROM spine_service_health WHERE name = %s AND scope = %s"
                " ORDER BY health_id DESC LIMIT %s", (name, ev.scope(), limit))
    return [{"ok": r[0], "detail": r[1], "at": r[2].isoformat()} for r in cur.fetchall()]


# ---- the built-ins, at birth ---------------------------------------------------------------

def name_of(row: dict) -> str:
    return str(row.get("name") or "")


def mind_of(gateway) -> tuple[str, dict, list[str]] | None:
    """The mind service a gateway IS: the Anthropic route (its default
    model, the key by NAME), or the fake lane; None without a gateway.
    P6.5 sp3: the LiteLLM lane's minds are STALLS — stable.seed registers
    the rig's own (`haiku`) with the deal the gateway's price map reads."""
    if gateway is None:
        return None
    model = getattr(gateway, "DEFAULT_MODEL", None) or "fake-mind"
    if type(gateway).__name__ == "LiteLLMGateway":
        return None
    if type(gateway).__name__ == "AnthropicGateway":
        return ("anthropic", {"route": "anthropic", "model": model}, ["ANTHROPIC_API_KEY"])
    return (model, {"route": "fake", "model": model, "class": "fast", "price": {"in_per_m": 0.0, "out_per_m": 0.0}}, [])


def seed(conn, *, gateway=None, home: str | os.PathLike | None = _UNSET) -> dict:
    """The kernel registers what it was born with: every built-in tool
    (kind tool, its schema the pin), the ground and the Record (kind
    store, the locator by NAME), and the mind the gateway is (kind
    mind). Idempotent: the same self every boot; a service the ground
    cannot seat is named, never a crash."""
    from .tools import TOOLS, tool_manifest
    made, refused, versioned = [], [], []

    def one(name, kind, manifest, secrets=()):
        try:
            before = get(conn, name)
            if before is not None and before["kind"] == kind and before["state"] != "retired" \
                    and before["manifest_hash"] != pin(manifest):
                version(conn, name, manifest, by=KERNEL)      # W47 (walk #12): a built-in whose declaration
                versioned.append(name)                        # changed re-pins at boot — a fact, never unhealthy
                return
            register(conn, name, kind, manifest, by=KERNEL, secrets_with=list(secrets), home=home)
            if before is None:
                made.append(name)
        except ServiceRefused as e:
            refused.append(f"{name}: {e}")

    for name, spec in TOOLS.items():
        one(name, "tool", tool_manifest(name, spec))
    one("ground", "store", {"locator": GROUND_LOCATOR, "what": "postgres — the ground every organ stands on"})
    one("record", "store", {"locator": GROUND_LOCATOR, "table": "spine_memories",
                            "what": "the Record — every memory, content-hashed, with lineage"})
    mind = mind_of(gateway)
    if mind is not None:
        one(mind[0], "mind", mind[1], mind[2])
    if type(gateway).__name__ == "LiteLLMGateway":     # P6.5 sp3: the rig's own stall, through the Stable
        from . import stable
        st = stable.seed(conn, gateway.stable, home=home)
        made += st["registered"]; refused += st["refused"]
        for n in st.get("retired", []):
            refused.append(f"{n}: the old world's built-in mind, retired — the Stable's {stable.DEFAULT_STALL[0]} stall serves the same model through the gateway")
    return {"registered": made, "refused": refused, "versioned": versioned}


def services_home(agents_home: str | os.PathLike | None) -> Path | None:
    """Where the services' seeds live: beside the agents' (`~/.orreth/
    services/<name>/seed`); None (ephemeral) only when the agents' is."""
    return None if agents_home is None else Path(agents_home).parent / "services"
