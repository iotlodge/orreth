# PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P6 sp4, placement policy v0 · 2026-09-21
"""Placement policy v0 (canon 0001 P10 · 0004 · 0005 P6 sp4): where a body
may run is a rule of the world, never an accident.

A template declares its PLACEMENT PROFILE — `{cell, affinity, secrets_with,
metal}` — and the kernel enforces it at BIRTH: the ground declares what it
is (its cell, its metal, the secret names it can reach) and a body whose
profile the ground cannot honor is REFUSED with the reason in plain words,
never started. The refusal is a recorded fact through the outbox
(`orreth.body.refused.v1`) with the kernel's chain and an observation
marker; the rig keeps running without that body and the crew card shows
the refused body greyed, the reason in words — never silently absent
(rule 7: one world, one picture). Placement never mints a self (rule 1):
the identity is loaded before the check and survives the refusal.

v0 is one host: the ground has exactly ONE cell (the `SPINE_CELL` dial,
default "local") and one metal (`SPINE_METAL`, default "cpu"); affinity is
ADVISORY (recorded and shown, not enforced — a second cell arrives with
P7); a secret is "reachable" iff its NAME is set in the ground's
environment — the only honest check one host can make — and a secret's
VALUE is printed nowhere, ever.
"""
from __future__ import annotations

import json
import os

from . import envelope as ev, outbox

REFUSED = "orreth.body.refused.v1"
METALS = ("any", "cpu", "gpu")
DEFAULT = {"cell": "local", "affinity": [], "secrets_with": [], "metal": "any"}
CELL_DIAL, METAL_DIAL = "SPINE_CELL", "SPINE_METAL"


class PlacementRefused(RuntimeError):
    """The ground cannot honor the body's placement — the reasons, in words."""

    def __init__(self, name: str, reasons: list[str]):
        self.name, self.reasons = name, list(reasons)
        super().__init__(f"{name} is refused here: " + "; ".join(reasons))


# ---- the profile (the wire shape; the fixture's law) ----------------------------------

def profile(template: dict) -> dict:
    """The template's placement with the defaults applied — canonical
    key order, every list a list of strings. A template that declares no
    placement wears the default and is born exactly as before."""
    raw = template.get("placement") or {}
    if not isinstance(raw, dict):
        raise ValueError("a placement is {cell, affinity, secrets_with, metal}")
    p = {
        "cell": str(raw.get("cell") or DEFAULT["cell"]),
        "affinity": [str(x) for x in (raw.get("affinity") or [])],
        "secrets_with": [str(x) for x in (raw.get("secrets_with") or [])],
        "metal": str(raw.get("metal") or DEFAULT["metal"]),
    }
    if p["metal"] not in METALS:
        raise ValueError(f"metal is one of {', '.join(METALS)} — not {p['metal']!r}")
    return p


def ground_declares(env: dict | None = None) -> dict:
    """What THIS ground is: its one cell, its metal, and the secret names
    it can reach (names only — the values never leave the environment)."""
    env = os.environ if env is None else env
    return {"cell": env.get(CELL_DIAL) or DEFAULT["cell"],
            "metal": env.get(METAL_DIAL) or "cpu",
            "secrets": sorted(k for k, v in env.items() if v)}


def honor(prof: dict, ground: dict) -> tuple[bool, list[str]]:
    """The rule: honored iff the cell is this ground's, the metal is here
    (or "any"), and every named secret is reachable. Every unmet clause is
    named in plain words — the owner learns why."""
    reasons: list[str] = []
    if prof["cell"] != ground["cell"]:
        reasons.append(f"cell '{prof['cell']}' is not this ground ('{ground['cell']}')")
    if prof["metal"] not in ("any", ground["metal"]):
        reasons.append(f"metal {prof['metal']} is not here ({ground['metal']})")
    have = set(ground.get("secrets") or ())
    for s in prof["secrets_with"]:
        if s not in have:
            reasons.append(f"secret {s} is not reachable here")
    return (not reasons), reasons


def why_here(prof: dict, ground: dict) -> str:
    """The card's one line: where the body stands and why."""
    ok, reasons = honor(prof, ground)
    if not ok:
        return "refused: " + "; ".join(reasons)
    have = set(ground.get("secrets") or ())
    n = len(prof["secrets_with"]); reached = sum(1 for s in prof["secrets_with"] if s in have)
    line = f"stands on {ground['cell']} · {ground['metal']}"
    if n:
        line += f" · reaches {reached} of {n} secrets"
    if prof["affinity"]:
        line += " · beside " + ", ".join(prof["affinity"]) + " (advisory)"
    return line


def card(prof: dict, ground: dict) -> dict:
    """What the crew card shows: the profile, each secret by NAME with a
    reached mark, the honor verdict and the why-line."""
    ok, reasons = honor(prof, ground)
    have = set(ground.get("secrets") or ())
    return {"cell": prof["cell"], "metal": prof["metal"], "affinity": list(prof["affinity"]),
            "secrets": [{"name": s, "reached": s in have} for s in prof["secrets_with"]],
            "ground": {"cell": ground["cell"], "metal": ground["metal"]},
            "honored": ok, "reasons": reasons, "why": why_here(prof, ground)}


# ---- the record ------------------------------------------------------------------------

def ensure_schema(conn) -> None:
    if not outbox.once(conn, "placement"):
        return
    with conn.transaction():
        cur = conn.cursor()
        cur.execute("SELECT pg_advisory_xact_lock(742199)")  # DDL race guard
        cur.execute(
            "CREATE TABLE IF NOT EXISTS spine_refusals ("
            " refusal_id bigserial PRIMARY KEY,"
            " did text NOT NULL, name text NOT NULL, kind text NOT NULL,"
            " template_hash text NOT NULL, placement text NOT NULL,"
            " ground text NOT NULL, reasons text NOT NULL, marker text,"
            " scope text NOT NULL, refused_at timestamptz NOT NULL DEFAULT now())")


def refuse(conn, body, prof: dict, ground: dict, reasons: list[str]) -> dict:
    """The refusal as a fact: its row and its envelope land in ONE
    transaction — `orreth.body.refused.v1` with the reasons, the profile,
    the kernel's chain and an observation marker (a root: the kernel
    observed a body it could not seat). Nothing is deleted; the human
    retires a refusal by fixing the template (rule 11)."""
    from . import markers
    ensure_schema(conn); outbox.ensure_schema(conn)
    markers.ensure_schema(conn); markers.seed(conn)
    mid = markers.new_id()
    marker = {"kind": "observation", "id": mid, "parent": None, "by": "the kernel"}
    ref = body.identity.did
    payload = {"ref": ref, "hash": ev.content_hash(prof), "name": body.name, "kind": body.kind,
               "template": body.template_hash, "placement": prof,
               "ground": {"cell": ground["cell"], "metal": ground["metal"]},
               "reasons": list(reasons)}
    e = ev.make_envelope(
        kind="event", type=REFUSED, universe_id=ev.scope(), scope_path=ev.scope(),
        payload=payload, correlation_id=ref, authority_chain=["the kernel"], marker=marker)

    def domain(cur):
        markers.insert(cur, mid, "observation", None, ref, "the kernel",
                       f"{body.name} refused at birth — " + "; ".join(reasons))
        cur.execute(
            "INSERT INTO spine_refusals (did, name, kind, template_hash, placement, ground,"
            " reasons, marker, scope) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (ref, body.name, body.kind, body.template_hash, ev.canonical(prof).decode("ascii"),
             ev.canonical(payload["ground"]).decode("ascii"), ev.canonical(reasons).decode("ascii"),
             mid, ev.scope()))

    outbox.commit_with_outbox(conn, ev.encode(e), e["message_id"], domain)
    return {"refused": True, "name": body.name, "did": ref, "reasons": list(reasons),
            "placement": prof, "marker": mid, "message_id": e["message_id"]}


def refusals(conn) -> dict[str, dict]:
    """The latest refusal per body name in this world."""
    cur = conn.cursor()
    cur.execute("SELECT to_regclass('spine_refusals')")
    if cur.fetchone()[0] is None:
        return {}
    cur.execute(
        "SELECT DISTINCT ON (name) name, did, kind, template_hash, placement, ground, reasons,"
        " marker, refused_at FROM spine_refusals WHERE scope = %s ORDER BY name, refusal_id DESC",
        (ev.scope(),))
    return {r[0]: {"name": r[0], "did": r[1], "kind": r[2], "template": r[3],
                   "placement": json.loads(r[4]), "ground": json.loads(r[5]),
                   "reasons": json.loads(r[6]), "marker": r[7], "refused_at": r[8]}
            for r in cur.fetchall()}
