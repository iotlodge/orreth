# PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P6 sp1, L3: the proof demand rises · 2026-09-21
# Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P6.5 sp1, the kernel holds and settles `service.retire` at L2 · 2026-09-22
# Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P6 cure sp3 (the re-walk's wounds): W20 the kernel settles a restart · W23 the words (rule 11) · 2026-09-21
"""The proof demand rises to meet the consequence (canon 0001 P12 · 0005 P6 sp1).

Every act wears a CONSEQUENCE CLASS — routine · consequential · grave —
and the class names the proof the kernel demands before the act runs:
L1 (the ask itself) · L2 (the in-chat interlock: a deliberate click) ·
L3 (a one-time code from the person's own authenticator — or, for the
gravest, a second NAMED person: the master, never the asker). The word
"sure" never passes L3: a code is typed, a master clicks.

The code is TOTP (RFC 6238: SHA-1, 30 s step, 6 digits), pure Python —
the secret lives on the ground, enrolled once through the chat and
confirmed by the first code; re-enrolling is itself grave (the old code).
Every refusal wears ONE face (covenant rule 4): wrong code, a stranger
as master, the asker as their own master, an ask nobody held — the same
words, the same status. Three wrong proofs REST the act — a recorded
cancel, never a deletion (rule 11) — and the chat says so. Every act's
record carries its proof level; sp2's export reads it plain.
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import secrets
import struct
import time
import zlib
from urllib.parse import quote

from . import envelope as ev
from . import outbox

CLASSES = ("routine", "consequential", "grave")        # the ladder, in order
LEVEL_OF_CLASS = {"routine": "L1", "consequential": "L2", "grave": "L3"}
LEVELS = ("L1", "L2", "L3-code", "L3-master")
KERNEL = "the kernel"                                   # the holder of its own acts
STEP_S, DIGITS, DRIFT, REST_AFTER = 30, 6, 1, 3         # RFC 6238 · ±1 step · three wrongs rest

AUTHENTICATOR_ENROLLED = "orreth.authenticator.enrolled.v1"
AUTHENTICATOR_CONFIRMED = "orreth.authenticator.confirmed.v1"
MASTER_DECLARED = "orreth.master.declared.v1"
PROOF_ATTEMPT = "orreth.proof.attempt.v1"

ONE_FACE = {"error": "not confirmed"}                   # rule 4: the outer face, always


class NotConfirmed(PermissionError):
    """The one face. `rest` is the inward fact that this refusal was the
    third — the door rests the act; the caller never learns which."""

    def __init__(self, rest: bool = False):
        super().__init__("not confirmed")
        self.rest = rest


class ProofRequired(RuntimeError):
    """The teaching inward: a grave act was asked bare — it must be HELD
    at the level named, never run on the first word. `needs_code` (W5):
    an L3-master hold that also wants the asker's code before the
    master's click counts."""

    def __init__(self, level: str, what: str, needs_code: bool = False):
        super().__init__(f"{what} is grave — it needs {level}, never a bare word")
        self.level = level
        self.what = what
        self.needs_code = bool(needs_code)


# ---- the ladder --------------------------------------------------------------------

def rank(cls: str) -> int:
    if cls not in CLASSES:
        raise ValueError(f"a consequence class is one of {', '.join(CLASSES)}")
    return CLASSES.index(cls)


def level_for(cls: str, *, master: bool = False) -> str:
    """The proof a class demands: routine → L1 · consequential → L2 ·
    grave → L3-code, or L3-master for the gravest (a second named person)."""
    base = LEVEL_OF_CLASS[CLASSES[rank(cls)]]
    if base != "L3":
        return base
    return "L3-master" if master else "L3-code"


# ---- the code (RFC 6238 over RFC 4226) --------------------------------------------

def hotp(key: bytes, counter: int, digits: int = DIGITS) -> str:
    mac = hmac.new(key, struct.pack(">Q", counter), hashlib.sha1).digest()
    offset = mac[-1] & 0x0F
    code = struct.unpack(">I", mac[offset:offset + 4])[0] & 0x7FFFFFFF
    return str(code % (10 ** digits)).zfill(digits)


def _key(secret_b32: str) -> bytes:
    s = secret_b32.strip().replace(" ", "").upper()
    return base64.b32decode(s + "=" * (-len(s) % 8))


def totp(secret_b32: str, t: float | None = None, step: int = STEP_S,
         digits: int = DIGITS) -> str:
    t = time.time() if t is None else t
    return hotp(_key(secret_b32), int(t // step), digits)


def verify(secret_b32: str, code: str | None, t: float | None = None,
           drift: int = DRIFT) -> bool:
    """The current step and ±drift steps; constant-time compares; a
    malformed code is simply wrong."""
    if not code or not str(code).strip().isdigit() or len(str(code).strip()) != DIGITS:
        return False
    given = str(code).strip()
    t = time.time() if t is None else t
    key = _key(secret_b32)
    ok = False
    for d in range(-drift, drift + 1):
        ok |= hmac.compare_digest(hotp(key, int(t // STEP_S) + d), given)
    return ok


def mint_secret() -> str:
    return base64.b32encode(secrets.token_bytes(20)).decode("ascii").rstrip("=")


def otpauth_uri(person: str, secret_b32: str, issuer: str = "Orreth") -> str:
    label = person.split(":")[-1] if person.startswith("did:") else person
    return (f"otpauth://totp/{quote(issuer)}:{quote(label)}?secret={secret_b32}"
            f"&issuer={quote(issuer)}&algorithm=SHA1&digits={DIGITS}&period={STEP_S}")


def qr_png_data_uri(text: str, scale: int = 6, border: int = 2) -> str | None:
    """The QR as a PNG data URI — `qrcode` draws the matrix, and the PNG
    is written here by hand (zlib + struct): no image library on the
    spine. None when qrcode is not installed; the URI still teaches."""
    try:
        import qrcode
    except Exception:
        return None
    q = qrcode.QRCode(border=border)
    q.add_data(text)
    q.make(fit=True)
    matrix = q.get_matrix()
    n = len(matrix)
    w = n * scale
    rows = bytearray()
    for r in range(n):
        line = bytearray([0])                             # filter: none
        for c in range(n):
            line += bytes([0 if matrix[r][c] else 255]) * scale
        rows += line * scale

    def chunk(tag: bytes, body: bytes) -> bytes:
        return (struct.pack(">I", len(body)) + tag + body
                + struct.pack(">I", zlib.crc32(tag + body) & 0xFFFFFFFF))
    png = (b"\x89PNG\r\n\x1a\n"
           + chunk(b"IHDR", struct.pack(">IIBBBBB", w, w, 8, 0, 0, 0, 0))   # 8-bit gray
           + chunk(b"IDAT", zlib.compress(bytes(rows), 9))
           + chunk(b"IEND", b""))
    return "data:image/png;base64," + base64.b64encode(png).decode("ascii")


# ---- the ground --------------------------------------------------------------------

def ensure_schema(conn) -> None:
    if not outbox.once(conn, "proof"):
        return
    with conn.transaction():
        cur = conn.cursor()
        cur.execute("SELECT pg_advisory_xact_lock(742199)")  # DDL race guard
        cur.execute(
            "CREATE TABLE IF NOT EXISTS spine_authenticators ("
            " auth_id bigserial PRIMARY KEY, person text NOT NULL,"
            " secret text NOT NULL, scope text NOT NULL,"
            " enrolled_at timestamptz NOT NULL DEFAULT now(),"
            " confirmed_at timestamptz, retired_at timestamptz)")
        cur.execute(
            "CREATE TABLE IF NOT EXISTS spine_masters ("
            " person text NOT NULL, declared_by text NOT NULL, scope text NOT NULL,"
            " declared_at timestamptz NOT NULL DEFAULT now(),"
            " PRIMARY KEY (person, scope))")
        cur.execute(
            "CREATE TABLE IF NOT EXISTS spine_proof_attempts ("
            " attempt_id bigserial PRIMARY KEY, ask_id text NOT NULL,"
            " by_did text NOT NULL, level text NOT NULL, ok boolean NOT NULL,"
            " at timestamptz NOT NULL DEFAULT now())")


def _event(type_: str, ref: str, payload: dict, by: str) -> dict:
    return ev.make_envelope(
        kind="event", type=type_, universe_id=ev.scope(), scope_path=ev.scope(),
        payload={"ref": ref, "hash": "sha256:-", **payload},
        correlation_id=ref, authority_chain=[by])


# -- the authenticator --

def active_secret(conn, person: str) -> str | None:
    ensure_schema(conn)
    cur = conn.cursor()
    cur.execute("SELECT secret FROM spine_authenticators WHERE person = %s AND scope = %s"
                " AND confirmed_at IS NOT NULL AND retired_at IS NULL"
                " ORDER BY auth_id DESC LIMIT 1", (person, ev.scope()))
    row = cur.fetchone()
    return row[0] if row else None


def enrolled(conn, person: str) -> bool:
    return active_secret(conn, person) is not None


def enroll(conn, person: str, *, code: str | None = None) -> dict:
    """Mint a secret for the person: the URI and the QR come back once,
    the row waits for its first code. A person who already holds a
    confirmed authenticator is re-enrolling — grave — and must give the
    OLD code here, or the one face answers."""
    ensure_schema(conn); outbox.ensure_schema(conn)
    old = active_secret(conn, person)
    if old is not None and not verify(old, code):
        raise NotConfirmed()
    secret = mint_secret()
    e = _event(AUTHENTICATOR_ENROLLED, person, {"re_enrolled": old is not None}, person)

    def domain(cur):
        cur.execute("UPDATE spine_authenticators SET retired_at = now() WHERE person = %s"
                    " AND scope = %s AND confirmed_at IS NULL AND retired_at IS NULL",
                    (person, ev.scope()))                  # one pending at a time
        cur.execute("INSERT INTO spine_authenticators (person, secret, scope) VALUES (%s, %s, %s)",
                    (person, secret, ev.scope()))

    outbox.commit_with_outbox(conn, ev.encode(e), e["message_id"], domain)
    uri = otpauth_uri(person, secret)
    return {"person": person, "uri": uri, "secret": secret, "qr": qr_png_data_uri(uri),
            "re_enrolled": old is not None}


def confirm_enrollment(conn, person: str, code: str | None) -> dict:
    """The first code confirms the pending secret; an older confirmed one
    retires in the same transaction. No pending row, wrong code: one face."""
    ensure_schema(conn); outbox.ensure_schema(conn)
    cur = conn.cursor()
    cur.execute("SELECT auth_id, secret FROM spine_authenticators WHERE person = %s AND scope = %s"
                " AND confirmed_at IS NULL AND retired_at IS NULL ORDER BY auth_id DESC LIMIT 1",
                (person, ev.scope()))
    row = cur.fetchone()
    if row is None or not verify(row[1], code):
        raise NotConfirmed()
    e = _event(AUTHENTICATOR_CONFIRMED, person, {}, person)

    def domain(cur):
        cur.execute("UPDATE spine_authenticators SET retired_at = now() WHERE person = %s AND scope = %s"
                    " AND confirmed_at IS NOT NULL AND retired_at IS NULL AND auth_id <> %s",
                    (person, ev.scope(), row[0]))
        cur.execute("UPDATE spine_authenticators SET confirmed_at = now() WHERE auth_id = %s", (row[0],))

    outbox.commit_with_outbox(conn, ev.encode(e), e["message_id"], domain)
    return {"person": person, "enrolled": True}


# -- the masters --

def masters(conn) -> list[str]:
    ensure_schema(conn)
    cur = conn.cursor()
    cur.execute("SELECT person FROM spine_masters WHERE scope = %s ORDER BY declared_at, person",
                (ev.scope(),))
    return [r[0] for r in cur.fetchall()]


def is_master(conn, person: str) -> bool:
    return person in masters(conn)


def declare_master(conn, person: str, *, by: str) -> bool:
    """A named second person, declared on the ground with its event; a
    master already standing is left as it is (False)."""
    ensure_schema(conn); outbox.ensure_schema(conn)
    if not person or is_master(conn, person):
        return False
    e = _event(MASTER_DECLARED, person, {"declared_by": by}, by)

    def domain(cur):
        cur.execute("INSERT INTO spine_masters (person, declared_by, scope) VALUES (%s, %s, %s)"
                    " ON CONFLICT DO NOTHING", (person, by, ev.scope()))

    outbox.commit_with_outbox(conn, ev.encode(e), e["message_id"], domain)
    return True


def seed_masters(conn) -> list[str]:
    """The SPINE_MASTERS dial (comma-separated person DIDs; default empty)
    declares this world's masters at birth — the seam where a directory
    will one day stand (not in P6)."""
    made = []
    for p in (os.environ.get("SPINE_MASTERS") or "").split(","):
        p = p.strip()
        if p and declare_master(conn, p, by="the SPINE_MASTERS dial"):
            made.append(p)
    return made


# -- the judgement at the door --

def record_attempt(conn, ask_id: str, *, by: str, level: str, ok: bool) -> int:
    """Every proof offered is a recorded fact with its event; returns how
    many have been refused on this ask so far (this one included)."""
    ensure_schema(conn); outbox.ensure_schema(conn)
    e = _event(PROOF_ATTEMPT, ask_id, {"level": level, "ok": ok}, by)

    def domain(cur):
        cur.execute("INSERT INTO spine_proof_attempts (ask_id, by_did, level, ok) VALUES (%s, %s, %s, %s)",
                    (ask_id, by, level, ok))

    outbox.commit_with_outbox(conn, ev.encode(e), e["message_id"], domain)
    cur = conn.cursor()
    cur.execute("SELECT count(*) FROM spine_proof_attempts WHERE ask_id = %s AND NOT ok", (ask_id,))
    return cur.fetchone()[0]


def judge(conn, ask_id: str, *, level: str, asker: str, by: str,
          code: str | None = None) -> None:
    """The door's judgement of a proof for a held act. L2 needs no proof
    beyond the click. L3-code: the asker's own authenticator, the code
    given. L3-master: `by` is a declared master and never the asker.
    Refused → recorded, then the ONE face (with the inward `rest` when
    it was the third)."""
    if level == "L3-code":
        secret = active_secret(conn, asker)
        ok = secret is not None and verify(secret, code)
    elif level == "L3-master":
        ok = bool(by) and by != asker and is_master(conn, by)
    else:
        return
    wrong = 0 if ok else record_attempt(conn, ask_id, by=by, level=level, ok=False)
    if not ok:
        raise NotConfirmed(rest=wrong >= REST_AFTER)
    record_attempt(conn, ask_id, by=by, level=level, ok=True)


def attempts(conn, ask_id: str) -> list[tuple]:
    ensure_schema(conn)
    cur = conn.cursor()
    cur.execute("SELECT by_did, level, ok FROM spine_proof_attempts WHERE ask_id = %s"
                " ORDER BY attempt_id", (ask_id,))
    return cur.fetchall()


# ---- the kernel's own held acts ------------------------------------------------------

def question_for(level: str, what: str, needs_code: bool = False) -> str:
    """The words the chat says when an act is held — plain, for a newcomer
    (charter P18). L2 keeps its own words in the resident."""
    if level == "L3-master" and needs_code:
        return (f"This needs your code, then a second named person. {what} is grave: "
                "type the six digits from your authenticator and confirm; then a "
                "declared master — never you — confirms it with a click. Cancel is the "
                "default, and doing nothing cancels. Three wrong codes put this act to rest.")
    if level == "L3-master":
        return (f"This needs a second named person. {what} is grave: a declared "
                "master — never you — confirms it with a click. Cancel is the "
                "default, and doing nothing cancels.")
    if level == "L2":                     # P6.5 sp1: the kernel's consequential act (rule 11's words)
        return (f"Are you sure? {what} is consequential — it is recorded, and you can restore "
                "it later. Cancel is the default; a deliberate click confirms.")
    # W23 (rule 11): the question never claims the act is beyond undoing — a
    # grave act is recorded, and the human can rest what it started later
    return (f"This needs your code. {what} is grave — it is recorded, and you can rest "
            "it later. Type the six digits from your authenticator, then confirm — cancel "
            "is the default, and doing nothing cancels. Three wrong codes put this act to rest.")


def hold_kernel_act(conn, *, text: str, person: str, tool: str, args: dict,
                    level: str, session: str | None = None,
                    cls: str = "grave", needs_code: bool = False) -> str:
    """An act the KERNEL itself holds (no resident serves it — stopping one
    of the kernel's intentions): the ask row is born held, with its
    CONFIRM_NEEDED and its marker in one transaction. No ask.received is
    filed — the dispatcher must never hand this to a resident."""
    from . import markers
    from .resident import CONFIRM_NEEDED, ensure_schema as _asks
    _asks(conn); ensure_schema(conn); outbox.ensure_schema(conn); markers.ensure_schema(conn)
    ask_id = "ask_" + secrets.token_hex(8)
    mid = markers.new_id()
    marker = {"kind": "objective", "id": mid, "parent": None, "by": person}
    held = {"tool": tool, "args": dict(args), "class": cls, "level": level}
    needs_code = bool(needs_code) and level == "L3-master"   # L3-code IS the code; the flag
    if needs_code:                       # W5: the asker's code, then the master's click
        held["needs_code"], held["code_ok"] = True, False
    question = question_for(level, text[:1].upper() + text[1:], needs_code=needs_code)
    n = ev.make_envelope(
        kind="event", type=CONFIRM_NEEDED, universe_id=ev.scope(), scope_path=ev.scope(),
        payload={"ref": ask_id, "hash": ev.content_hash(text), "tool": tool,
                 "class": cls, "level": level, **({"needs_code": True} if needs_code else {})},
        correlation_id=ask_id, authority_chain=[person, KERNEL],
        aggregate={"type": "ask", "id": ask_id, "sequence": 1}, marker=marker)

    def domain(cur):
        markers.insert(cur, mid, "objective", None, ask_id, person)
        cur.execute(
            "INSERT INTO spine_asks (ask_id, text, person, status, reply, served_by, held,"
            " scope, session, marker) VALUES (%s, %s, %s, 'awaiting-confirm', %s, %s, %s, %s, %s, %s)",
            (ask_id, text, person, question, KERNEL, json.dumps(held), ev.scope(), session, mid))

    outbox.commit_with_outbox(conn, ev.encode(n), n["message_id"], domain)
    return ask_id


def settle_kernel_act(conn, ask_id: str, *, approve: bool, by: str,
                      level: str | None = None, reason: str | None = None) -> dict:
    """The kernel settles its own held act after the door judged the
    proof: yes → the held act runs and the record wears its level;
    anything else → a recorded cancel, the act never ran (rule 11)."""
    from . import intent, markers
    from .resident import JOURNEY, REPLY, _next_seq
    with conn.transaction():
        cur = conn.cursor()
        cur.execute("SELECT status, held, person, marker FROM spine_asks WHERE ask_id = %s"
                    " AND served_by = %s FOR UPDATE", (ask_id, KERNEL))
        row = cur.fetchone()
        if row is None or row[0] != "awaiting-confirm" or not row[1]:
            raise NotConfirmed()
        held = json.loads(row[1]); asker = row[2]
        level = level or held.get("level") or "L3-master"
        marker = markers.as_env(conn, row[3]) if row[3] else None
        chain = [asker, by, KERNEL] if by != asker else [asker, KERNEL]

        def note(text: str) -> None:
            j = ev.make_envelope(
                kind="event", type=JOURNEY, universe_id=ev.scope(), scope_path=ev.scope(),
                payload={"ref": ask_id, "hash": "sha256:-", "note": f"{KERNEL}: {text}"},
                correlation_id=ask_id, authority_chain=chain,
                aggregate={"type": "ask", "id": ask_id, "sequence": _next_seq(cur, ask_id)},
                marker=marker)
            outbox.add_row(cur, ev.encode(j), j["message_id"])

        if approve:
            if held["tool"] == "intent.stop":
                made = intent.stop(conn, held["args"]["intention_id"], by=asker,
                                   proof=level, confirmed_by=by)
                result = f"the intention “{made['words']}” is at rest — recorded, never deleted"
            elif held["tool"] == "intent.restart":       # W20: the reverse act, its own fact
                made = intent.restart(conn, held["args"]["intention_id"], by=asker,
                                      proof=level, confirmed_by=by)
                result = (f"the intention “{made['words']}” stands again — its stop stays in "
                          "the record, its history whole")
            elif held["tool"] == "service.retire":       # P6.5 sp1: the shelf's stop, at L2
                from . import services
                made = services.retire(conn, held["args"]["name"], by=asker, ask=ask_id,
                                       parent_marker=row[3])
                result = (f"the {made['name']} {made['kind']} is retired — at rest on the shelf, "
                          f"recorded, never deleted; say “restore the {made['name']} {made['kind']}” "
                          "to bring it back")
            else:
                raise NotConfirmed()                     # no other kernel act yet
            if level == "L2":
                note(f"the human said yes — the {held['tool']} act ran · proof {level}")
                reply = f"Done, on your word: {result}."
            elif level == "L3-code":
                note(f"the code was right — the {held['tool']} act ran · proof {level}")
                reply = f"Done, on your code: {result}."
            else:
                word = " after the asker's code" if held.get("needs_code") else ""
                note(f"{by} confirmed as master{word} — the {held['tool']} act ran · proof {level}")
                reply = f"Done, on {by.split(':')[-1]}'s word as master{word}: {result}."
            status, proof = "replied", level
        else:
            why = reason or "the human cancelled"
            note(f"{why} — the {held['tool']} act never ran (cancel is always the default)")
            reply = ("Rested — three wrong proofs were given, so nothing was done. The act "
                     "is at rest, recorded; ask again when you are ready." if reason
                     else "Cancelled — nothing was done. Cancel is always the default here.")
            status, proof = "cancelled", "L1"
        cur.execute("UPDATE spine_asks SET status = %s, reply = %s, proof = %s,"
                    " replied_at = clock_timestamp() WHERE ask_id = %s",   # W17: the landing, not the start
                    (status, reply, proof, ask_id))
        r = ev.make_envelope(
            kind="event", type=REPLY, universe_id=ev.scope(), scope_path=ev.scope(),
            payload={"ref": ask_id, "hash": ev.content_hash(reply), "proof": proof},
            correlation_id=ask_id, authority_chain=chain, marker=marker,
            aggregate={"type": "ask", "id": ask_id, "sequence": _next_seq(cur, ask_id)})
        outbox.add_row(cur, ev.encode(r), r["message_id"])
    return {"ask_id": ask_id, "status": status, "proof": proof, "reply": reply}
