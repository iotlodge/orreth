# PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp8 row 3, THE GATE (b): the machine join desk · 2026-09-26
"""THE MACHINE JOIN DESK (canon 0005 sp8 row 3b · 0006 §2–3 · 0012 · covenant rule 3).

A BODY joins a world the way the old world's desk let it (`orreth_sim/joindoor.py`,
JB's lock 2026-07-07), carried onto the new kernel: the five-status desk

    pending → challenged → proved → staged → done | denied
     the body   the kernel  the body  the kernel   the kernel (after a governing seat's yes)

The door answers PROOF, not claims: the kernel challenges the joiner with a nonce it
issued itself, the joiner signs `{did, join_nonce}` with the key behind its DID, and
the kernel verifies against the public key the joiner declared — which must derive the
DID it claims (`did:orreth:agent:` + sha256(public)[..32]; a DID here is a hash, so
the key rides beside it). A proven key is STAGED for the human: the kernel holds
`join.admit` at the interlock as its own act (the hold appears in the chat like a
keeper's proposal; cancel is the default; only a GOVERNING seat — the owner or a
master — may click yes; a hold nobody answers in fifteen minutes is denied and
recorded, 0012's "expire = deny + signal"). The yes mints a LEASE: the 0006 token
(`seat.mint`, the kernel's own self the root) to the body's DID with the FUEL CLAUSE
in its budget (the Stable's allowance per window — `cost` and `renew_days`), for
`SPINE_JOIN_LEASE_DAYS` (30). The lease is COLLECTED by the same key (a signature over
`{did, join, join_nonce}` — an id alone collects nothing) and stands on the ground as
a SEAT with the role `body`: one gate law for people and bodies. A lease opens the
body's own words on the feed (`POST /delta`) and the desk's doors, nothing more.

Two words stand for the human's: THE CREW MANIFEST — a body this kernel spawned
carries a one-time SPAWN TICKET the kernel handed it, and its proven key is admitted
at once (the manifest is the human's word) — and THE STANDING WELCOME — a self once
admitted to this world is admitted again on its next proof with no second click.
Every lapse is dormancy, never death: the same self re-joins and renews.

JB's pin (2026-09-26, the STANDING KEY-CHECK): the kernel asking a body every so
often to prove it is WHAT and WHO it says — this desk's challenge is that act. A
re-join by a leased body proves the key again and is admitted on its welcome in
silence; a cadence dial that asks for it is not built until a proof asks (rule 12).

The pure law here (the statuses and their transitions, the challenge's bytes, the
proof's verdict, the lease and its fuel clause, the collect's bytes, the words) is
measured by `spine/conformance/desk-v0.json` on both kernels. The doors and the
ground live on the Rust kernel alone (JB's lock 7, 2026-09-26: the Python reference
grows no new doors); this file also carries the BODY'S side of the knock — what a
spawned or stranger body does at the kernel's door (`knock`).
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import time

from . import envelope as ev
from . import seat

SPEC = "orreth.desk/1"
STATUSES = ("pending", "challenged", "proved", "staged", "done", "denied")
KINDS = ("agent",)                                    # what may knock: a body (a service is the keeper's to register)

JOIN_ASKED = "orreth.join.asked.v1"                   # a body asked, and was challenged
JOIN_PROVED = "orreth.join.proved.v1"                 # its key is proven — staged, or admitted on a standing word
JOIN_ADMITTED = "orreth.join.admitted.v1"             # the lease minted
JOIN_DENIED = "orreth.join.denied.v1"                 # turned away — a bad proof, a no, a hold nobody answered

ADMIT_TOOL = "join.admit"                             # the kernel-held act (the human's yes)
ADMIT_CLASS, ADMIT_LEVEL = "consequential", "L2"      # a click; cancel is the default
REFUSED = {"error": "join refused"}                   # the desk's one face (a prober learns nothing)
BY_MANIFEST = "the crew manifest"                     # who admitted a body the kernel spawned
KERNEL = "the kernel"

LEASE_DAYS_DIAL, LEASE_DAYS_DEFAULT = "SPINE_JOIN_LEASE_DAYS", 30
NONCE_S = 120                                         # a challenge is answered within two minutes, else re-challenged
SPAWN_TICKET_DIAL = "SPINE_SPAWN_TICKET"              # the kernel's one-time word to a body it spawned
NAME_RX = re.compile(r"^[a-z][a-z0-9_-]{1,31}$")      # a body's name (the templates' grammar)

# ---- the pure half ----------------------------------------------------------------------


def transition_legal(from_: str, to: str) -> bool:
    """May `to` follow `from_`? A settled word (done · denied) is never rewritten; a
    challenge may be re-issued from any open status; `proved` answers only a
    `challenged`; the human's word lands on a `staged` join; the same status again is
    an idempotent update."""
    if from_ not in STATUSES or to not in STATUSES:
        return False
    if from_ in ("done", "denied"):
        return False
    if from_ == to:
        return True
    return {"challenged": from_ in ("pending", "proved", "staged"),
            "proved": from_ == "challenged",
            "staged": from_ == "proved",
            "done": from_ in ("proved", "staged"),
            "denied": True,
            "pending": False}[to]


def challenge_payload(did: str, nonce: str) -> dict:
    """The bytes the joiner signs — the old SDK's exact shape, carried."""
    return {"did": did, "join_nonce": nonce}


def collect_payload(did: str, join_id: str, nonce: str) -> dict:
    """The bytes that collect the lease: the same key, a different sentence."""
    return {"did": did, "join": join_id, "join_nonce": nonce}


def proof_of(signer, nonce: str) -> dict:
    """The body's answer to a challenge — the contract's Sig over the challenge bytes."""
    return seat._sig(signer, challenge_payload(signer.did, nonce))


def collect_sig(signer, join_id: str, nonce: str) -> dict:
    return seat._sig(signer, collect_payload(signer.did, join_id, nonce))


def prove(did: str, public_key_hex: str, nonce: str, sig) -> bool:
    """The desk's verdict on a proof: the declared key derives the DID it claims (the
    kind read from the DID), and the signature stands over the desk's OWN nonce."""
    kind = seat._kind_of(did)
    try:
        if kind not in KINDS or seat.did_of_key(kind, public_key_hex) != did:
            return False
    except ValueError:
        return False
    return seat._sig_ok(sig, challenge_payload(did, nonce), public_key_hex)


def collect_ok(did: str, public_key_hex: str, join_id: str, nonce: str, sig) -> bool:
    return seat._sig_ok(sig, collect_payload(did, join_id, nonce), public_key_hex)


def lease_grants() -> list:
    """What a lease may do here: the body reads and writes what is its own — its words
    on the feed, its own join. Never govern; never another's."""
    return [{"action": "retrieve", "space": "self"}, {"action": "write", "space": "self"}]


def fuel_clause(usd: float, renew_days: int) -> dict:
    """The lease's fuel (0058's clause on the new kernel): an allowance in dollars per
    window — the Stable's own terms for the body's virtual key; `renew_days` 0 is the
    old lump, spent once."""
    clause = {"cost": float(usd)}
    if int(renew_days) > 0:
        clause["renew_days"] = int(renew_days)
    return clause


def lease(signer, *, did: str, scope: str, expiry: str, usd: float, renew_days: int) -> dict:
    """The body's lease: `seat.mint` to its DID, this world the audience, the fuel clause
    the budget — the kernel's own self the root, one hop."""
    return seat.mint(signer, subject=did, audience=scope, grants=lease_grants(), expiry=expiry,
                     direction="within", budget=fuel_clause(usd, renew_days))


def lease_days() -> int:
    try:
        return max(1, int(float(os.environ.get(LEASE_DAYS_DIAL) or LEASE_DAYS_DEFAULT)))
    except ValueError:
        return LEASE_DAYS_DEFAULT


def join_id_of(did: str, nonce: str) -> str:
    """`join_` + sha256(did · nonce)[..12] — the join's name on the ground and in its facts."""
    return "join_" + hashlib.sha256(f"{did}\n{nonce}".encode("ascii")).hexdigest()[:12]


def name_ok(name: str | None) -> bool:
    return bool(NAME_RX.match(str(name or "")))


def words(status: str, name: str, scope: str = "", by: str | None = None) -> str:
    """The desk's plain words at each status — what the body reads at the door and what
    the feed says."""
    if status == "challenged":
        return "sign this nonce with the key behind your DID — the door answers proof, not claims"
    if status == "staged":
        return f"{name} proved its key — the door waits for a governing seat's yes"
    if status == "done":
        tail = f" · {by}" if by else ""
        return f"lease granted — welcome to {scope}, {name}{tail}"
    if status == "denied":
        return REFUSED["error"]
    return f"{name} asks to join {scope}"


def admitted_by(*, ticket: bool = False, welcome: str | None = None, person: str | None = None) -> str:
    """Whose word admitted a proven key: the crew manifest (a spawn ticket), the standing
    welcome (an earlier admission of the same self), or a governing seat's."""
    if ticket:
        return f"admitted on {BY_MANIFEST} — this kernel spawned this body"
    if welcome:
        return f"admitted on its standing welcome ({welcome}) — the same self, the same world"
    who = (person or "").split(":")[-1] or "a governing seat"
    return f"admitted on {who}'s word"


def hold_words(name: str, kind: str, template_hash: str, days: int) -> str:
    """The text the kernel's hold carries — plain, for the person who will click."""
    short = template_hash.split(":")[-1][:8] or "unknown"
    return (f"{name} (a {kind}) asks to join this world — its key is proven, its template {short}. "
            f"A yes gives it a LEASE for {days} days: its own words on the feed and nothing more, "
            f"fueled by the Stable's allowance; a no turns it away. Cancel is the default.")


# ---- the body's side of the knock -------------------------------------------------------


def knock(door: str, identity, *, name: str, kind: str, template_hash: str, policy_hash: str,
          ticket: str | None = None, wait_s: float = 600.0, poll_s: float = 1.0, say=None) -> dict | None:
    """One body at the kernel's door: ask (challenged) → prove → wait for the word
    (a spawn ticket or a standing welcome answers at once; else a governing seat's
    click) → collect the lease with the same key. Returns `{lease, wire, lease_id,
    expiry, admitted_by, join}` or None when the door turned this body away (or never
    answered within `wait_s`)."""
    import http.client
    from urllib.parse import urlsplit
    u = urlsplit(door.rstrip("/"))
    say = say or (lambda _w: None)

    def call(method: str, path: str, obj=None):
        conn = http.client.HTTPConnection(u.hostname, u.port or 80, timeout=10.0)
        try:
            body = json.dumps(obj).encode() if obj is not None else None
            conn.request(method, path, body, {"content-type": "application/json"} if body else {})
            r = conn.getresponse()
            raw = r.read()
            try:
                return r.status, json.loads(raw or b"null")
            except ValueError:
                return r.status, None
        finally:
            conn.close()

    ask = {"did": identity.did, "name": name, "role": kind, "public_key": identity.verify_key_hex,
           "template_hash": template_hash, "policy_hash": policy_hash}
    if ticket:
        ask["ticket"] = ticket
    st, a = call("POST", "/join", ask)
    if st != 201 or not isinstance(a, dict) or not a.get("nonce"):
        say(f"{name} was not challenged at the door ({st}: {a})")
        return None
    jid, nonce = a["id"], a["nonce"]
    st, p = call("POST", "/join/prove", {"id": jid, "did": identity.did, "sig": proof_of(identity, nonce)})
    if st != 200 or not isinstance(p, dict):
        say(f"{name} was turned away at the door ({st}: {p})")
        return None
    if p.get("status") == "challenged":                 # a stale nonce — prove the fresh one
        nonce = p["nonce"]
        st, p = call("POST", "/join/prove", {"id": jid, "did": identity.did, "sig": proof_of(identity, nonce)})
        if st != 200 or not isinstance(p, dict):
            say(f"{name} was turned away at the door ({st}: {p})")
            return None
    status = p.get("status")
    if status == "staged":
        say(f"{name} proved its key — waiting at the door for a governing seat's yes")
    deadline = time.monotonic() + wait_s
    while status not in ("done", "denied") and time.monotonic() < deadline:
        time.sleep(poll_s)
        st, v = call("GET", f"/join/{jid}")
        status = v.get("status") if isinstance(v, dict) else status
    if status != "done":
        say(f"{name} did not join: {status or 'no answer'} at the door")
        return None
    st, c = call("POST", "/join/lease", {"id": jid, "did": identity.did, "sig": collect_sig(identity, jid, nonce)})
    if st != 200 or not isinstance(c, dict) or not c.get("wire"):
        say(f"{name} could not collect its lease ({st}: {c})")
        return None
    return {"lease": c.get("lease"), "wire": c["wire"], "lease_id": c.get("lease_id"), "expiry": c.get("expiry"),
            "admitted_by": c.get("admitted_by"), "join": jid}


def canonical_bytes(obj) -> str:
    """The fixture's helper: the canonical bytes of a payload as ASCII."""
    return ev.canonical(obj).decode("ascii")


# ---- the record (re-base sp1) ----------------------------------------------------------

DESK_DDL = (      # word for word with the Rust kernel's `desk_live::DESK_DDL` — the desk is the
    "CREATE TABLE IF NOT EXISTS spine_desk ( join_id text PRIMARY KEY, scope text NOT NULL, did text NOT NULL, "
    "name text NOT NULL, kind text NOT NULL, public_key text NOT NULL, template_hash text NOT NULL DEFAULT '', "
    "policy_hash text NOT NULL DEFAULT '', status text NOT NULL, nonce text NOT NULL, nonce_at timestamptz NOT "
    "NULL DEFAULT now(), ticket text, ask_id text, admitted_by text, lease_id text, lease text, expiry "
    "timestamptz, asked_at timestamptz NOT NULL DEFAULT now(), updated_at timestamptz NOT NULL DEFAULT now())",
    "CREATE INDEX IF NOT EXISTS spine_desk_did ON spine_desk (scope, did)",
)     # Rust kernel's to write; declared here too so one migrator serves both kernels


def ensure_schema(conn) -> None:
    from .outbox import once
    if not once(conn, "desk"):
        return
    with conn.transaction():
        cur = conn.cursor()
        cur.execute("SELECT pg_advisory_xact_lock(742199)")  # DDL race guard
        for ddl in DESK_DDL:
            cur.execute(ddl)
