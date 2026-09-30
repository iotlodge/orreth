# PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp7, cells · partition · isolation · hardening · 2026-09-25
# Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch row 4, the honest glass sp2 (W87): the unreachable time wears its date · a peer LET GO on a governing seat's word (`forget_peer`, schema 3) · 2026-09-29
"""CELLS (canon 0002 rule 8 · 0001 P9/P10 · 0005 P7 sp7 — JB's locks, 2026-09-25):
a CELL is one universe's physical home — its own kernel self, its own
ground (a database and a role that reaches no other), its own benches and
topics (the namespace), its own bodies with their own seed homes, its own
policy and meter. "Cells = worlds": a universe stands in exactly ONE home
cell, at an EPOCH that advances only when it is re-homed. Two cells may
name each other as PEERS; the seam between them is SIGNED by the kernels'
own selves (the DID pinned on first sight), commands ROUTE HOME to the
cell that homes their subject, selected facts REPLICATE with their lag
shown, and when a peer is cut the ask PARKS in plain words and resumes
when the peer answers — never lost, never doubled.

This module is the REFERENCE for the pure laws (the fixture
`spine/conformance/cells-v0.json` is generated from it and the Rust kernel
must pass it unchanged) plus the world's record on the ground and the
world card both doors serve (rule 7: one world, one picture). The seam's
LIVE half — peers, the relay, the parking — is the Rust kernel's (0008:
P7's scale work lands in the Rust kernel, built once).
"""
from __future__ import annotations

import hashlib
import os
import re
from datetime import datetime, timezone

from nacl.exceptions import BadSignatureError
from nacl.signing import VerifyKey

from . import envelope as ev, outbox

CONTRACT = "orreth.cells/1"
WORLD_HOMED = "orreth.world.homed.v1"        # a universe stands in its home cell at an epoch — a fact
SEAM = "orreth.seam/1"                       # the cross-cell message's own specversion
KERNEL = "the kernel"

CELL_DIAL = "SPINE_CELL"                     # this kernel's cell (the ground declares it — placement.py)
PEERS_DIAL = "SPINE_PEERS"                   # "two=http://127.0.0.1:4602,three=http://…" — the peers this cell names
DEFAULT_CELL = "local"

SEAM_WINDOW_S = 120                          # a seam message older (or newer) than this is refused: replay's first fence
CEILING_RATE = 5.0                           # knocks per second a caller may sustain at a door …
CEILING_BURST = 20.0                         # … and the burst it may spend at once (0071's knock ceilings)


# ---- the pure laws (the fixture's) ----------------------------------------------------------

def topic_name(base: str, ns: str | None) -> str:
    """The topic a fact rides on: the envelope's TYPE (schema families,
    never per-identity — canon 0002 rule 7) wearing the cell's namespace
    the way a bench does (`resident.serve_queue`): `orreth.ask.received.v1`
    alone in the first cell, `orreth.ask.received.v1.two` in cell two. One
    broker may carry many cells in dev; none reads another's log."""
    return f"{base}.{ns}" if ns else base


def peers_from(dial: str | None) -> list[dict]:
    """`SPINE_PEERS` → the peers this cell names: `name=door` pairs, comma
    separated, a door an http(s) origin. A malformed pair is dropped by
    name, never guessed."""
    out: list[dict] = []
    for pair in (dial or "").split(","):
        pair = pair.strip()
        if not pair or "=" not in pair:
            continue
        name, door = pair.split("=", 1)
        name, door = name.strip().lower(), door.strip().rstrip("/")
        if re.fullmatch(r"[a-z0-9_-]+", name) and re.match(r"^https?://\S+$", door):
            out.append({"cell": name, "door": door})
    return out


def address_home(text: str) -> dict | None:
    """Where an ask is addressed when it names a CELL: "librarian@two, …"
    · "two/librarian: …" · "@librarian@two …" → {cell, name}; a bare
    name at the head ("echo, …") is this world's own rule (`dispatch.address`)
    and reads None here. Cell and name come back lower-cased — the home
    cell spells its bodies' names itself."""
    m = re.match(r"^\s*@?([A-Za-z0-9_-]+)@([A-Za-z0-9_-]+)\s*[,:]\s*\S", text or "")
    if m:
        return {"cell": m.group(2).lower(), "name": m.group(1).lower()}
    m = re.match(r"^\s*([A-Za-z0-9_-]+)/([A-Za-z0-9_-]+)\s*[,:]\s*\S", text or "")
    if m:
        return {"cell": m.group(1).lower(), "name": m.group(2).lower()}
    return None


def strip_home(text: str) -> str:
    """The words the home cell serves: the ask with its cell address
    rewritten as a plain address ("librarian@two, hello" → "librarian, hello")."""
    m = re.match(r"^(\s*)@?([A-Za-z0-9_-]+)@([A-Za-z0-9_-]+)(\s*[,:]\s*)(\S.*)$", text or "", re.S)
    if m:
        return f"{m.group(2)}{m.group(4)}{m.group(5)}"
    m = re.match(r"^(\s*)([A-Za-z0-9_-]+)/([A-Za-z0-9_-]+)(\s*[,:]\s*)(\S.*)$", text or "", re.S)
    if m:
        return f"{m.group(3)}{m.group(4)}{m.group(5)}"
    return text


def epoch_check(mine: int, theirs: int) -> str:
    """The fencing law (canon 0002 rule 9, SOL §ordering): a message wearing
    my epoch is `current`; an older one is `stale` (its sender's home moved
    on — it may not commit); a newer one is `future` (I am the one behind —
    refresh my pin before I judge)."""
    if theirs == mine:
        return "current"
    return "stale" if theirs < mine else "future"


def world_fact(scope: str, cell: str, epoch: int, kernel_did: str, door: str, reason: str) -> dict:
    """`orreth.world.homed.v1` — the universe stands in `cell` at `epoch`,
    kept by the kernel `kernel_did` whose door is `door`; `reason` says why
    (`opened` at epoch 1; `re-homed` after). The kernel's own chain."""
    payload = {"ref": scope, "hash": ev.content_hash({"cell": cell, "epoch": int(epoch)}),
               "cell": cell, "epoch": int(epoch), "kernel": kernel_did, "door": door, "reason": reason}
    return ev.make_envelope(kind="event", type=WORLD_HOMED, universe_id=scope, scope_path=scope,
                            payload=payload, correlation_id=scope, authority_chain=[KERNEL])


def seam_message(*, from_cell: str, from_world: str, to_cell: str, epoch: int, kind: str,
                 body: dict, nonce: str, at: str) -> dict:
    """One message across the seam, unsigned: who sends (cell + world +
    epoch), who it is for, what kind (`ask` · `reply` · `stop` · `facts` ·
    `hello`), the body, a nonce that is never reused, the sender's clock."""
    return {"specversion": SEAM, "from": from_cell, "world": from_world, "to": to_cell,
            "epoch": int(epoch), "kind": kind, "body": body, "nonce": nonce, "at": at}


def seam_sign(msg: dict, signer) -> dict:
    """The message signed by a kernel self (Ed25519 over the canonical bytes
    of the message without its signature fields); the signer's DID and
    public key ride beside it so a peer that has PINNED the DID can check."""
    m = {k: v for k, v in msg.items() if k not in ("signer", "public_key", "signature")}
    return {**m, "signer": signer.did, "public_key": signer.verify_key_hex, "signature": signer.sign(m)}


def did_of_key(public_key_hex: str) -> str:
    return "did:orreth:kernel:" + hashlib.sha256(bytes.fromhex(public_key_hex)).hexdigest()[:32]


def seam_verify(signed: dict, *, pinned_did: str | None, now: str, seen_nonces, epoch: int | None = None,
                window_s: int = SEAM_WINDOW_S) -> str:
    """The seam's gate, one verdict in words: `ok`, or the first fence that
    refused — `unknown signer` (no pin, or a DID that is not this key's),
    `not for this cell`, `bad signature`, `replayed` (a nonce seen before),
    `too old` / `too new` (outside the window around my clock), `stale epoch`
    / `future epoch` (the sender's epoch against the one I hold for it)."""
    try:
        if signed.get("specversion") != SEAM:
            return "bad signature"
        pk = str(signed.get("public_key") or "")
        did = str(signed.get("signer") or "")
        if not pinned_did or did != pinned_did or did_of_key(pk) != did:
            return "unknown signer"
        m = {k: v for k, v in signed.items() if k not in ("signer", "public_key", "signature")}
        try:
            VerifyKey(bytes.fromhex(pk)).verify(ev.canonical(m), bytes.fromhex(str(signed.get("signature") or "")))
        except (BadSignatureError, ValueError):
            return "bad signature"
        if signed.get("nonce") in set(seen_nonces or ()):
            return "replayed"
        dt = (_parse(str(signed.get("at"))) - _parse(now)).total_seconds()
        if dt < -window_s:
            return "too old"
        if dt > window_s:
            return "too new"
        if epoch is not None:
            v = epoch_check(int(epoch), int(signed.get("epoch", 0)))
            if v != "current":
                return f"{v} epoch"
        return "ok"
    except (TypeError, ValueError, AttributeError):
        return "bad signature"


def _parse(iso: str) -> datetime:
    return datetime.strptime(iso, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)


def park_words(name: str, cell: str, since_hhmm: str) -> str:
    """The plain words on an ask whose home cell does not answer."""
    return (f"{name}@{cell} is out of reach — cell {cell} has not answered since {since_hhmm}; "
            f"your ask is parked and will go the moment it answers")


def resumed_words(name: str, cell: str) -> str:
    return f"cell {cell} answers again — your ask to {name}@{cell} is on its way"


def lag_words(cell: str, world: str | None, behind_s: float | None, unreachable_since: str | None) -> str:
    """A peer's one line in the glass: who it homes and how far behind my
    picture of it is — or since when it has not answered."""
    who = f"cell {cell}" + (f" · {world}" if world else "")
    if unreachable_since:
        return f"{who} · unreachable since {unreachable_since}"
    if behind_s is None:
        return f"{who} · not yet heard"
    if behind_s < 1:
        return f"{who} · live"
    return f"{who} · {int(round(behind_s))} s behind"


def sealed_words(role: str, own_db: str, reachable: list[str]) -> tuple[bool, str]:
    """The harness's tenth check: this cell's role reaches its own database
    and no other. The dev ground's owner reaches everything — said so,
    honestly, never hidden."""
    others = sorted(d for d in reachable if d != own_db)
    if not others:
        return True, f"the role {role} reaches only {own_db}"
    return False, (f"the role {role} reaches {len(others) + 1} databases: {own_db}, "
                   + ", ".join(others) + " — unsealed (the dev profile); seal it with scripts/dev.sh cell")


def ceiling(tokens: float, last_at: float, now: float, rate: float = CEILING_RATE,
            burst: float = CEILING_BURST) -> tuple[bool, float]:
    """A knock ceiling per caller (0071): a token bucket that refills `rate`
    a second up to `burst`; a knock spends one; an empty bucket refuses
    and the knock is not counted against the caller twice."""
    have = min(burst, float(tokens) + max(0.0, now - last_at) * rate)
    if have >= 1.0:
        return True, have - 1.0
    return False, have


def rehome_words(scope: str, from_cell: str, to_cell: str, epoch: int) -> str:
    return (f"{scope} is re-homed from cell {from_cell} to cell {to_cell} at epoch {epoch} — "
            f"a kernel still wearing epoch {epoch - 1} may not commit for it")


# ---- the record ------------------------------------------------------------------------

def ensure_schema(conn) -> None:
    if not outbox.once(conn, "cells"):
        return
    from . import resident
    resident.ensure_schema(conn)                 # spine_asks stands before its seam columns are added
    with conn.transaction():
        cur = conn.cursor()
        cur.execute("SELECT pg_advisory_xact_lock(742199)")  # DDL race guard
        cur.execute(
            "CREATE TABLE IF NOT EXISTS spine_world ("
            " scope text PRIMARY KEY, cell text NOT NULL, epoch int NOT NULL DEFAULT 1,"
            " kernel text NOT NULL, door text, opened_at timestamptz NOT NULL DEFAULT now(),"
            " rehomed_at timestamptz, rehomed_by text)")
        cur.execute(
            "CREATE TABLE IF NOT EXISTS spine_peers ("
            " cell text NOT NULL, scope text NOT NULL, door text NOT NULL, did text, world text,"
            " epoch int, pinned_at timestamptz, last_seen timestamptz, cursor bigint NOT NULL DEFAULT 0,"
            " unreachable_since timestamptz, PRIMARY KEY (cell, scope))")
        cur.execute(
            "CREATE TABLE IF NOT EXISTS spine_seam_nonces ("
            " nonce text PRIMARY KEY, scope text NOT NULL, seen_at timestamptz NOT NULL DEFAULT now())")
        # the seam's outbound queue and the routed ask's columns (the Rust kernel's to write;
        # declared here too so two spines on one ground never disagree about a column)
        cur.execute(
            "CREATE TABLE IF NOT EXISTS spine_seam_out ("
            " out_id bigserial PRIMARY KEY, cell text NOT NULL, scope text NOT NULL, kind text NOT NULL,"
            " body text NOT NULL, ref text, attempts int NOT NULL DEFAULT 0,"
            " next_at timestamptz NOT NULL DEFAULT now(), sent_at timestamptz, last_error text,"
            " added_at timestamptz NOT NULL DEFAULT now())")
        for ddl in ("ALTER TABLE spine_asks ADD COLUMN IF NOT EXISTS home_cell text",
                    "ALTER TABLE spine_asks ADD COLUMN IF NOT EXISTS remote_id text",
                    "ALTER TABLE spine_asks ADD COLUMN IF NOT EXISTS seam_side text",
                    "ALTER TABLE spine_asks ADD COLUMN IF NOT EXISTS seam_sent boolean NOT NULL DEFAULT false",
                    "ALTER TABLE spine_peers ADD COLUMN IF NOT EXISTS picture text",
                    # schema 3 (the honest glass sp2, W87): a peer LET GO — recorded on its row, never deleted;
                    # a kernel relit naming the cell (SPINE_PEERS) names it again
                    "ALTER TABLE spine_peers ADD COLUMN IF NOT EXISTS forgotten_by text",
                    "ALTER TABLE spine_peers ADD COLUMN IF NOT EXISTS forgotten_at timestamptz"):
            cur.execute(ddl)


class NotMyHome(RuntimeError):
    """The ground says this universe is homed in another cell: a kernel of
    a different cell may not light over it (the fencing law at the door)."""


def home(conn, kernel_did: str, door: str, cell: str | None = None) -> dict:
    """The universe's home, settled at light: absent → this cell, epoch 1,
    the `opened` fact; present in THIS cell → the row as it stands (the
    kernel's door refreshed); present in another cell → refused in words."""
    ensure_schema(conn); outbox.ensure_schema(conn)
    scope = ev.scope()
    cell = cell or os.environ.get(CELL_DIAL) or DEFAULT_CELL
    cur = conn.cursor()
    cur.execute("SELECT cell, epoch, kernel, opened_at, rehomed_at FROM spine_world WHERE scope = %s", (scope,))
    row = cur.fetchone()
    if row is None:
        e = world_fact(scope, cell, 1, kernel_did, door, "opened")

        def domain(c):
            c.execute("INSERT INTO spine_world (scope, cell, epoch, kernel, door) VALUES (%s, %s, 1, %s, %s)"
                      " ON CONFLICT (scope) DO NOTHING", (scope, cell, kernel_did, door))
        outbox.commit_with_outbox(conn, ev.encode(e), e["message_id"], domain)
        return card(conn, kernel_did)
    if row[0] != cell:
        raise NotMyHome(f"{scope} is homed in cell {row[0]} (epoch {row[1]}) — this kernel says it is cell {cell}; "
                        f"light it as cell {row[0]}, or re-home the universe first")
    cur.execute("UPDATE spine_world SET kernel = %s, door = %s WHERE scope = %s", (kernel_did, door, scope))
    return card(conn, kernel_did)


def card(conn, kernel_did: str | None = None) -> dict:
    """The world card (rule 7 — the same on both doors): the universe, its
    cell and epoch, the kernel that keeps it, its peers with their lag."""
    ensure_schema(conn)
    scope = ev.scope()
    cur = conn.cursor()
    cur.execute("SELECT cell, epoch, kernel, door, opened_at, rehomed_at, rehomed_by FROM spine_world WHERE scope = %s",
                (scope,))
    row = cur.fetchone()
    out = {"scope": scope, "cell": row[0] if row else (os.environ.get(CELL_DIAL) or DEFAULT_CELL),
           "epoch": row[1] if row else None, "kernel": row[2] if row else kernel_did,
           "door": row[3] if row else None, "opened_at": row[4].isoformat() if row else None,
           "rehomed_at": row[5].isoformat() if row and row[5] else None,
           "rehomed_by": row[6] if row else None, "homed": row is not None,
           "namespace": os.environ.get("SPINE_QUEUE_NS", ""), "peers": peers(conn)}
    return out


def _human(t):
    from zoneinfo import ZoneInfo
    from .digest import human_zone_name
    return t.astimezone(ZoneInfo(human_zone_name()))


def unreachable_clock(t) -> str:
    """The moment a peer stopped answering, on the human's clock — the time alone
    when it is today, the DATE before it when it is not (the honest glass sp2, W87:
    JB read "unreachable since 17:31" over a peer four DAYS gone)."""
    from datetime import datetime, timezone
    h = _human(t)
    today = _human(datetime.now(timezone.utc)).date()
    return h.strftime("%H:%M") if h.date() == today else h.strftime("%Y-%m-%d %H:%M")


def forget_peer(conn, cell: str, by: str) -> bool:
    """A peer LET GO on a governing seat's word (W87 · rule 11): recorded on its
    row — `forgotten_by` · `forgotten_at` — never a delete; the card stops drawing
    it and nothing is routed to it. A kernel relit naming the cell in SPINE_PEERS
    names it again. False when no such peer is named here (or it is already let go)."""
    ensure_schema(conn)
    with conn.transaction():
        cur = conn.cursor()
        cur.execute("UPDATE spine_peers SET forgotten_by = %s, forgotten_at = now()"
                    " WHERE cell = %s AND scope = %s AND forgotten_at IS NULL",
                    (by, cell, ev.scope()))
        return cur.rowcount == 1


def peers(conn) -> list[dict]:
    """Every peer this cell names, as the ground remembers it: pinned DID,
    the world it homes, when it was last heard, its lag in words."""
    cur = conn.cursor()
    cur.execute("SELECT cell, door, did, world, epoch, pinned_at, last_seen, cursor, unreachable_since,"
                " extract(epoch FROM (clock_timestamp() - last_seen)) FROM spine_peers"
                " WHERE scope = %s AND forgotten_at IS NULL ORDER BY cell",     # a peer let go is not drawn
                (ev.scope(),))
    out = []
    for r in cur.fetchall():
        since = unreachable_clock(r[8]) if r[8] else None                 # W52: the human's clock · W87: its date
        out.append({"cell": r[0], "door": r[1], "did": r[2], "world": r[3], "epoch": r[4],
                    "pinned_at": r[5].isoformat() if r[5] else None,
                    "last_seen": r[6].isoformat() if r[6] else None, "cursor": r[7],
                    "unreachable_since": r[8].isoformat() if r[8] else None,
                    "words": lag_words(r[0], r[3], float(r[9]) if r[9] is not None else None, since)})
    return out


def sealed(conn) -> dict:
    """The tenth check, read off the ground: which databases this
    connection's role may enter. Sealed iff only its own."""
    cur = conn.cursor()
    cur.execute("SELECT current_user, current_database()")
    role, own = cur.fetchone()
    cur.execute("SELECT datname FROM pg_database WHERE datallowconn AND NOT datistemplate"
                " AND has_database_privilege(current_user, datname, 'CONNECT') ORDER BY datname")
    reachable = [r[0] for r in cur.fetchall()]
    ok, words = sealed_words(role, own, reachable)
    return {"name": "this cell is sealed", "ok": ok, "detail": words, "role": role, "database": own,
            "reachable": reachable}
