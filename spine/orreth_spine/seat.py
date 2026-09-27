# PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp8 row 3, THE GATE (a): the human seat · 2026-09-26
"""THE HUMAN SEAT (canon 0005 sp8 row 3 · 0006 §3 · covenant rules 3 and 4).

Until this row every door read the person from the request body and
defaulted to one name; the loopback bind was the only gate. Now a person
holds a SEAT TOKEN — the 0006 shape (subject · audience · grants ·
constraints{expiry, direction} · chain · sig; attenuation-only; the
contract `contracts/v0/capability-token.schema.json`), minted at the door
after their proof (the code from the authenticator they enrolled) and
chained to the kernel's own self as this universe's root. EVERY door reads
the person from the token, never the body (`door_needs` says which doors
stand open — the page, the health, the guide, the world checks, the proof
doors whose code IS the proof, the seam with its own signature, the join
desk's doors whose proof is a signature — and which need `retrieve` ·
`write` · `govern`; since row 3b a body's own words at `/delta` need its
LEASE — a seat with the role `body`, minted by the desk, `desk.py`).

THE CEREMONY: on a ground no one holds, the first person to PROVE an
authenticator becomes its OWNER — declared once as a fact, a master from
that moment — and enrolling anyone else is the owner's (or a master's)
act; a person may always re-enroll themselves with their old code. The
seat rides `authorization: Bearer <base64url of the canonical token>`
(the live feed, which a browser cannot send headers to, carries it as a
query parameter); it lasts `SPINE_SEAT_HOURS` (24) and a person may leave
it early — recorded, never deleted. The unseated wear one face (401 "not
seated": no seat, a forged one, an expired one, a left one — the same
words); a seated person lacking a grant wears the proof's one face (403).
The browser origin is CLOSED: a request wearing an Origin that is not this
door's is refused before the body is read. The knock ceiling (0071, once
only at `/seam`) stands at EVERY door per person — or per address at an
open door — with the plain words «the door is busy for you — try again
shortly» (429).

The pure half (mint · verify · attenuate · wire · seat_id · door_needs ·
origin_ok · grants_for) is measured by `spine/conformance/seat-v0.json`
on both kernels; the ground half (the owner, the seats, the facts) is the
reference the Rust `seat_live` mirrors.
"""
from __future__ import annotations

import base64
import hashlib
import json
import os
import re
import threading
import time
from datetime import datetime, timedelta, timezone

from nacl.exceptions import BadSignatureError
from nacl.signing import VerifyKey

from . import envelope as ev
from . import outbox, proof
from .cells import ceiling as _bucket

SPEC = "orreth.seat/1"
ACTIONS = ("retrieve", "write", "distill", "interview", "govern", "transfer", "issue", "resolve")
DIRECTIONS = ("down", "within", "up", "across")
HOURS_DEFAULT = 24.0                                  # JB's lock, 2026-09-26: one proof a day
CEILING_RATE_DEFAULT, CEILING_BURST_DEFAULT = 20.0, 60.0   # the doors' bucket (the seam keeps 5 · 20)

SEAT_TAKEN = "orreth.seat.taken.v1"
SEAT_LEFT = "orreth.seat.left.v1"
OWNER_DECLARED = "orreth.owner.declared.v1"

NOT_SEATED = {"error": "not seated"}                  # the unseated's one face (401)
BUSY_WORDS = "the door is busy for you — try again shortly"   # 0071's words (429)
CEREMONY = "the ceremony"                             # who declares the owner

# ---- the pure half ----------------------------------------------------------------------


def did_of_key(kind: str, public_key_hex: str) -> str:
    """`did:orreth:<kind>:` + sha256(public)[..32] — every key-bearing self's DID."""
    return f"did:orreth:{kind}:" + hashlib.sha256(bytes.fromhex(public_key_hex)).hexdigest()[:32]


def _kind_of(did: str) -> str:
    parts = did.split(":")
    return parts[2] if len(parts) >= 4 and parts[0] == "did" and parts[1] == "orreth" else ""


def _sig(signer, payload: dict) -> dict:
    """The contract's Sig: `{alg, by, sig}` — Ed25519 over the canonical bytes, hex."""
    return {"alg": "ed25519", "by": signer.did, "sig": signer.sign(payload)}


def _sig_ok(sig, payload: dict, public_key_hex: str) -> bool:
    try:
        if not isinstance(sig, dict) or sig.get("alg") != "ed25519":
            return False
        VerifyKey(bytes.fromhex(public_key_hex)).verify(ev.canonical(payload), bytes.fromhex(str(sig.get("sig") or "")))
        return True
    except (BadSignatureError, ValueError, TypeError):
        return False


def within(scope: str, ancestor: str) -> bool:
    """A scope path is within an ancestor when it is the ancestor or stands below it."""
    return scope == ancestor or scope.startswith(ancestor + "/")


def _space_within(space, parent_space) -> bool:
    if space == parent_space:
        return True
    if isinstance(space, dict) and isinstance(parent_space, dict) and "scope" in space and "scope" in parent_space:
        return within(str(space["scope"]), str(parent_space["scope"]))
    return False


def _grants_within(grants: list, parent: list) -> bool:
    """Every grant of a hop must stand within one of its parent's — the same action, a space
    that is the parent's or below it (attenuation-only, 0006 §3)."""
    for g in grants:
        if not any(g.get("action") == p.get("action") and _space_within(g.get("space"), p.get("space")) for p in parent):
            return False
    return True


def _parse(iso: str) -> datetime:
    for fmt in ("%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%dT%H:%M:%SZ"):
        try:
            return datetime.strptime(iso, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    raise ValueError(iso)


def _content(token: dict) -> dict:
    return {k: token[k] for k in ("subject", "audience", "grants", "constraints")}


def mint(signer, *, subject: str, audience: str, grants: list, expiry: str,
         direction: str = "within", budget: dict | None = None, chain: list | None = None) -> dict:
    """A capability token in the 0006 shape, one hop appended to `chain` (none: the
    signer is the root and this is the first hop). The hop carries the issuer's DID
    and public key (so a stranger verifies the chain offline), the four content
    fields and the issuer's Sig over them; the chain is the hops as canonical
    strings, root first; the outer Sig is the last issuer's over the content."""
    if direction not in DIRECTIONS:
        raise ValueError(f"direction is one of {', '.join(DIRECTIONS)}")
    for g in grants:
        if g.get("action") not in ACTIONS:
            raise ValueError(f"a grant's action is one of {', '.join(ACTIONS)}")
    constraints = {"expiry": expiry, "direction": direction}
    if budget:
        constraints["budget"] = budget
    hop = {"issuer": signer.did, "public_key": signer.verify_key_hex, "subject": subject,
           "audience": audience, "grants": grants, "constraints": constraints}
    hop = {**hop, "sig": _sig(signer, hop)}
    content = {"subject": subject, "audience": audience, "grants": grants, "constraints": constraints}
    return {**content,
            "chain": list(chain or []) + [ev.canonical(hop).decode("ascii")],
            "sig": _sig(signer, content)}


def attenuate(token: dict, signer, *, subject: str, grants: list | None = None,
              expiry: str | None = None, audience: str | None = None) -> dict:
    """A narrower token below this one, issued by the self that holds it (the signer
    must BE the token's subject — a key-bearing self; a person's name has no key and
    cannot delegate). `verify` refuses any widening as `amplified`."""
    return mint(signer, subject=subject, audience=audience or token["audience"],
                grants=grants if grants is not None else token["grants"],
                expiry=expiry or token["constraints"]["expiry"],
                direction=token["constraints"]["direction"],
                budget=token["constraints"].get("budget"), chain=token["chain"])


def verify(token, *, root_did: str, root_key_hex: str, now: str) -> str:
    """The verdict, in one word: `ok`, or the first fence that refused —
    `malformed` (not the shape) · `expired` · `foreign authority` (a chain that does not
    start at this root) · `broken chain` (a hop whose issuer is not the previous subject,
    a key that is not the issuer's, or a last hop that does not bind the token) · `bad
    signature` · `amplified` (a hop wider than the one above it)."""
    try:
        if not isinstance(token, dict) or set(token) != {"subject", "audience", "grants", "constraints", "chain", "sig"}:
            return "malformed"
        c = token["constraints"]
        if not (isinstance(token["grants"], list) and token["grants"] and isinstance(c, dict)
                and isinstance(token["chain"], list) and token["chain"]):
            return "malformed"
        if c.get("direction") not in DIRECTIONS:
            return "malformed"
        if _parse(str(c["expiry"])) <= _parse(now):
            return "expired"
        hops = [json.loads(h) for h in token["chain"]]
        first = hops[0]
        if first.get("issuer") != root_did or first.get("public_key") != root_key_hex:
            return "foreign authority"
        prev = None
        for hop in hops:
            issuer, pk = str(hop.get("issuer") or ""), str(hop.get("public_key") or "")
            if prev is not None:
                if issuer != prev["subject"] or did_of_key(_kind_of(issuer), pk) != issuer:
                    return "broken chain"
            body = {k: v for k, v in hop.items() if k != "sig"}
            if not _sig_ok(hop.get("sig"), body, pk):
                return "bad signature"
            if prev is not None:
                pc, hc = prev["constraints"], hop["constraints"]
                if (not within(str(hop["audience"]), str(prev["audience"]))
                        or not _grants_within(hop["grants"], prev["grants"])
                        or _parse(str(hc["expiry"])) > _parse(str(pc["expiry"]))
                        or hc.get("direction") != pc.get("direction")):
                    return "amplified"
            prev = hop
        last = hops[-1]
        if any(last.get(k) != token[k] for k in ("subject", "audience", "grants", "constraints")):
            return "broken chain"
        if not _sig_ok(token["sig"], _content(token), str(last.get("public_key") or "")):
            return "bad signature"
        return "ok"
    except (TypeError, ValueError, KeyError, AttributeError):
        return "malformed"


def seat_id(token: dict) -> str:
    """`seat_` + sha256(canonical token)[..16] — the seat's name on the ground and in its facts."""
    return "seat_" + hashlib.sha256(ev.canonical(token)).hexdigest()[:16]


def wire(token: dict) -> str:
    """The token on the wire: base64url of its canonical bytes, unpadded."""
    return base64.urlsafe_b64encode(ev.canonical(token)).decode("ascii").rstrip("=")


def unwire(s: str | None) -> dict | None:
    try:
        raw = base64.urlsafe_b64decode(str(s or "") + "=" * (-len(str(s or "")) % 4))
        tok = json.loads(raw.decode("ascii"))
        return tok if isinstance(tok, dict) else None
    except (ValueError, TypeError, UnicodeDecodeError):
        return None


def bearer(header: str | None) -> str | None:
    """`authorization: Bearer <wire>` → the wire, or None."""
    if not header:
        return None
    parts = header.strip().split(None, 1)
    if len(parts) == 2 and parts[0].lower() == "bearer" and parts[1].strip():
        return parts[1].strip()
    return None


def grants_for(role: str, scope: str) -> list:
    """What a seat may do here: a person reads and writes within this world; the
    owner and a master may also GOVERN (enroll another, re-home, the shelf and the
    Stable, the bodies' levers)."""
    space = {"scope": scope}
    out = [{"action": "retrieve", "space": space}, {"action": "write", "space": space}]
    if role in ("owner", "master"):
        out.append({"action": "govern", "space": space})
    return out


OPEN_GET = ("/", "/index.html", "/health", "/guide", "/harness", "/seat")
OPEN_POST = ("/seat", "/enroll/confirm", "/seam", "/join", "/join/prove", "/join/lease")   # P7 sp8 row 3b: the desk's doors answer proof, not seats
LEASE_POST = ("/delta",)                              # P7 sp8 row 3b: a body's own words wear its LEASE (a seat with the role `body`)
GOVERN_POST = ("/world/rehome", "/bodies/restart",
               "/services", "/services/version", "/services/retire", "/services/restore", "/services/mcp",
               "/minds", "/minds/assign", "/minds/unassign", "/minds/refill", "/minds/retire", "/minds/restore")


def door_needs(method: str, path: str) -> str:
    """What a door asks of the one who knocks: `open` (no seat — the page, the health,
    the guide, the world checks, the seat door itself, the enrollment's confirm whose code
    is the proof, the seam with its own signature, the join desk's doors whose proof is a
    signature, a join's own status) · `enroll` (the ceremony while no one holds the
    ground; else the owner's word, or one's own old code) · `lease` (a body's own words
    on the feed — its lease, never a person's seat) · `retrieve` (every other read) ·
    `write` (every other act) · `govern` (re-home, the bodies' lever, the shelf's and the
    Stable's changes)."""
    m = method.upper()
    if m == "GET":
        return "open" if path in OPEN_GET or path.startswith("/join/") else "retrieve"
    if m == "POST":
        if path == "/enroll":
            return "enroll"
        if path in OPEN_POST:
            return "open"
        if path in LEASE_POST:
            return "lease"
        if path in GOVERN_POST:
            return "govern"
        return "write"
    return "write"


def origin_ok(origin: str | None, host: str | None) -> bool:
    """The browser origin is closed: a request that names an Origin is served only when
    that origin IS this door (`http://<host>` for the Host it was asked at); no Origin
    (a script, a test, curl) is the same-origin case."""
    if not origin:
        return True
    o, h = origin.strip().lower(), (host or "").strip().lower()
    return bool(h) and o in (f"http://{h}", f"https://{h}")


NAME_RX = re.compile(r"^[a-z][a-z0-9_-]{1,23}$")     # persons.py's grammar (the old world's law carried)


def person_did(text: str | None) -> str | None:
    """A person named at the door: their DID as given (`did:orreth:person:<name>`) or a
    bare name in the person grammar (lower-case, 2–24 of a-z 0-9 _ -, a letter first)
    — None for anything else. The name is never reissued to another: it IS the DID."""
    t = str(text or "").strip()
    if t.startswith("did:orreth:person:"):
        name = t[len("did:orreth:person:"):]
        return t if NAME_RX.match(name) else None
    return f"did:orreth:person:{t}" if NAME_RX.match(t) else None


def busy() -> dict:
    return {"error": BUSY_WORDS, "retry_after_s": 1}


def taken_words(person: str, role: str, hours: float, ceremony: bool) -> str:
    name = person.split(":")[-1]
    base = (f"you hold this ground now, {name} — the first to prove an authenticator here is its owner"
            if ceremony else f"seated, {name}")
    r = "the owner" if role == "owner" else "a master" if role == "master" else "a person"
    h = int(hours) if float(hours).is_integer() else hours
    return f"{base} · your seat is {r}'s for {h} hours; say “leave my seat” to end it sooner"


# ---- the ground -----------------------------------------------------------------------


def hours() -> float:
    try:
        return float(os.environ.get("SPINE_SEAT_HOURS") or HOURS_DEFAULT)
    except ValueError:
        return HOURS_DEFAULT


def ensure_schema(conn) -> None:
    if not outbox.once(conn, "seat"):
        return
    proof.ensure_schema(conn)
    with conn.transaction():
        cur = conn.cursor()
        cur.execute("SELECT pg_advisory_xact_lock(742199)")  # DDL race guard
        cur.execute(
            "CREATE TABLE IF NOT EXISTS spine_owner ("
            " scope text PRIMARY KEY, person text NOT NULL,"
            " declared_at timestamptz NOT NULL DEFAULT now())")
        cur.execute(
            "CREATE TABLE IF NOT EXISTS spine_seats ("
            " seat_id text PRIMARY KEY, person text NOT NULL, scope text NOT NULL,"
            " role text NOT NULL, expiry timestamptz NOT NULL,"
            " taken_at timestamptz NOT NULL DEFAULT now(), left_at timestamptz, left_by text)")


def _event(type_: str, ref: str, payload: dict, chain: list) -> dict:
    return ev.make_envelope(
        kind="event", type=type_, universe_id=ev.scope(), scope_path=ev.scope(),
        payload={"ref": ref, "hash": "sha256:-", **payload},
        correlation_id=ref, authority_chain=chain)


def owner(conn) -> str | None:
    ensure_schema(conn)
    cur = conn.cursor()
    cur.execute("SELECT person FROM spine_owner WHERE scope = %s", (ev.scope(),))
    row = cur.fetchone()
    return row[0] if row else None


def declare_owner(conn, person: str) -> bool:
    """THE CEREMONY: the first person to prove an authenticator on a ground no one
    holds becomes its owner — one fact, one row, and a master from that moment. A
    ground already held is left as it is (False)."""
    ensure_schema(conn); outbox.ensure_schema(conn)
    if owner(conn) is not None:
        return False
    e = _event(OWNER_DECLARED, person, {"person": person, "by": CEREMONY}, [person, proof.KERNEL])

    def domain(cur):
        cur.execute("INSERT INTO spine_owner (scope, person) VALUES (%s, %s) ON CONFLICT DO NOTHING",
                    (ev.scope(), person))

    outbox.commit_with_outbox(conn, ev.encode(e), e["message_id"], domain)
    proof.declare_master(conn, person, by=CEREMONY)
    return True


def role_of(conn, person: str) -> str:
    if owner(conn) == person:
        return "owner"
    return "master" if proof.is_master(conn, person) else "person"


def take(conn, person: str, code: str | None, signer, *, hours_: float | None = None) -> dict:
    """The seat door: the person's code from their enrolled authenticator, or the one
    face; on a ground no one holds, this proof is the ceremony. The token is minted
    by the kernel's own self as the root, its row and its fact land in one transaction."""
    ensure_schema(conn); outbox.ensure_schema(conn)
    secret = proof.active_secret(conn, person)
    if secret is None or not proof.verify(secret, code):
        raise proof.NotConfirmed()
    ceremony = declare_owner(conn, person)
    role = role_of(conn, person)
    h = hours() if hours_ is None else float(hours_)
    expiry = (datetime.now(timezone.utc) + timedelta(hours=h)).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
    token = mint(signer, subject=person, audience=ev.scope(), grants=grants_for(role, ev.scope()), expiry=expiry)
    sid = seat_id(token)
    e = _event(SEAT_TAKEN, sid, {"hash": ev.content_hash(token), "person": person, "role": role,
                                 "expiry": expiry, "ceremony": ceremony}, [person, proof.KERNEL])

    def domain(cur):
        cur.execute("INSERT INTO spine_seats (seat_id, person, scope, role, expiry) VALUES (%s, %s, %s, %s, %s)",
                    (sid, person, ev.scope(), role, expiry))

    outbox.commit_with_outbox(conn, ev.encode(e), e["message_id"], domain)
    return {"seat": token, "wire": wire(token), "seat_id": sid, "person": person, "role": role,
            "expiry": expiry, "owner": ceremony, "words": taken_words(person, role, h, ceremony)}


def offline(wire_s: str | None, signer, now: str | None = None) -> dict | None:
    """The seat's offline half: the token from the wire, verified against this kernel's
    root — `{person, seat_id, grants, govern, expiry}` — or None. No ground is touched:
    the ceiling is spent on this before the ground is ever asked, so a flood of knocks
    never reaches it."""
    tok = unwire(wire_s)
    if tok is None:
        return None
    if verify(tok, root_did=signer.did, root_key_hex=signer.verify_key_hex, now=now or ev.now_iso()) != "ok":
        return None
    return {"person": tok["subject"], "seat_id": seat_id(tok), "grants": tok["grants"],
            "govern": any(g.get("action") == "govern" for g in tok["grants"]),
            "expiry": tok["constraints"]["expiry"]}


def read(conn, wire_s: str | None, signer, now: str | None = None) -> dict | None:
    """Who sits here: the token verified offline against this kernel's root, then
    its row on the ground (a seat left is a seat no more). None for every other case
    — the door says "not seated" and nothing more."""
    off = offline(wire_s, signer, now)
    if off is None:
        return None
    return on_ground(conn, off)


def on_ground(conn, off: dict) -> dict | None:
    """The seat's row: its role, and that it was not left."""
    ensure_schema(conn)
    sid = off["seat_id"]
    tok = None
    cur = conn.cursor()
    cur.execute("SELECT role FROM spine_seats WHERE seat_id = %s AND scope = %s AND left_at IS NULL", (sid, ev.scope()))
    row = cur.fetchone()
    if row is None:
        return None
    return {**off, "role": row[0]}


def leave(conn, seat_id_: str, person: str) -> dict:
    """The person ends their own seat early — recorded, never deleted."""
    ensure_schema(conn); outbox.ensure_schema(conn)
    e = _event(SEAT_LEFT, seat_id_, {"person": person}, [person, proof.KERNEL])

    def domain(cur):
        cur.execute("UPDATE spine_seats SET left_at = now(), left_by = %s WHERE seat_id = %s AND person = %s"
                    " AND left_at IS NULL", (person, seat_id_, person))

    outbox.commit_with_outbox(conn, ev.encode(e), e["message_id"], domain)
    return {"left": seat_id_, "person": person, "words": "your seat is ended — prove your authenticator to sit again"}


def may_enroll(conn, actor: dict | None, target: str) -> bool:
    """Who may enroll an authenticator for `target`: anyone while the ground has no owner
    (the ceremony — the first to PROVE becomes the owner); afterwards the person
    themselves (re-enrolling with the old code, grave) or a seat that governs."""
    if owner(conn) is None:
        return True
    if actor is None:
        return False
    return actor["person"] == target or bool(actor.get("govern"))


def seats(conn, person: str) -> list[dict]:
    ensure_schema(conn)
    cur = conn.cursor()
    cur.execute("SELECT seat_id, role, expiry, taken_at, left_at FROM spine_seats WHERE person = %s AND scope = %s"
                " ORDER BY taken_at DESC LIMIT 20", (person, ev.scope()))
    return [{"seat_id": r[0], "role": r[1], "expiry": r[2].isoformat(), "taken_at": r[3].isoformat(),
             "left_at": r[4].isoformat() if r[4] else None} for r in cur.fetchall()]


SEEN_S = 5.0                                          # how long the gate remembers a seat it checked on the ground


class Ceilings:
    """The knock ceiling at every door (0071, generalized from the seam): one token
    bucket per person — per address at an open door — refilling `SPINE_CEILING_RATE`
    a second up to `SPINE_CEILING_BURST`; a knock spends one; an empty bucket refuses
    with the busy words. Per process, swept of the long-quiet."""

    def __init__(self, rate: float | None = None, burst: float | None = None):
        def dial(name, default):
            try:
                return float(os.environ.get(name) or default)
            except ValueError:
                return default
        self.rate = rate if rate is not None else dial("SPINE_CEILING_RATE", CEILING_RATE_DEFAULT)
        self.burst = burst if burst is not None else dial("SPINE_CEILING_BURST", CEILING_BURST_DEFAULT)
        self._buckets: dict[str, tuple[float, float]] = {}
        self._seen: dict[str, tuple[dict, float]] = {}   # seat_id → (who, checked_at): the ground asked once per SEEN_S
        self._lock = threading.Lock()

    def remembered(self, seat_id_: str, now: float | None = None) -> dict | None:
        """The seat as the ground answered within the last SEEN_S seconds, or None."""
        now = time.time() if now is None else now
        with self._lock:
            hit = self._seen.get(seat_id_)
            return dict(hit[0]) if hit and hit[1] > now - SEEN_S else None

    def remember(self, who: dict, now: float | None = None) -> None:
        now = time.time() if now is None else now
        with self._lock:
            self._seen[who["seat_id"]] = (dict(who), now)
            if len(self._seen) > 10000:
                for k in [k for k, (_, t) in self._seen.items() if t < now - SEEN_S]:
                    del self._seen[k]

    def forget(self, seat_id_: str) -> None:
        with self._lock:
            self._seen.pop(seat_id_, None)

    def knock(self, who: str, now: float | None = None) -> bool:
        now = time.time() if now is None else now
        with self._lock:
            tokens, last = self._buckets.get(who, (self.burst, now))
            ok, after = _bucket(tokens, last, now, self.rate, self.burst)
            self._buckets[who] = (after, now)
            if len(self._buckets) > 10000:
                for k in [k for k, (_, t) in self._buckets.items() if t < now - 600]:
                    del self._buckets[k]
            return ok
