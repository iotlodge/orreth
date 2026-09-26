# PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp8 row 3, THE GATE (a): the seat at every test's door · 2026-09-26
"""The seat at the test's door (P7 sp8 row 3). Every door now reads the person from
the SEAT TOKEN, never the body — so a test that knocks must sit first. This helper
runs the same ceremony a human runs in the glass, through the doors alone: the
first person to prove an authenticator on the session's ground becomes its OWNER;
every other person is enrolled on the owner's word, confirms with the first code,
and takes a seat with the next. Secrets are learned at the door (an `/enroll` the
test itself posts is remembered too), seats are cached per (port, person) — a
rig's kernel self is ephemeral, so a seat never crosses rigs.

`urlopen` is a drop-in for `urllib.request.urlopen`: it reads the actor from the
request (the body's `by` or `person`, a query's `person`) and presents THAT
person's seat — the owner's when none is named; a named person not yet seated is
enrolled on the owner's word first. A test that means a STRANGER knocks with
`unseated`, and the door says so."""
from __future__ import annotations

import json
import secrets as _secrets
import threading
import urllib.error
import urllib.parse
import urllib.request

from orreth_spine import proof

_LOCK = threading.RLock()
_SECRETS: dict[tuple[str, str], str] = {}        # (scope, person) → the authenticator's secret, as the door gave it
_SEATS: dict[tuple[int, str, str], str] = {}     # (port, scope, person) → the wire
_OWNER: dict[str, str] = {}                      # scope → the owner, once that ground is held


def _scope() -> str:
    """The world the doors serve right now (a module may run its rig under its own scope)."""
    from orreth_spine import envelope as ev
    return ev.scope()
TARGET_DOORS = ("/enroll", "/enroll/confirm", "/seat")   # the body's `person` is a TARGET here, not the actor


def _raw(port: int, method: str, path: str, obj=None, headers=None, timeout: float = 10):
    data = json.dumps(obj).encode() if obj is not None else None
    h = {"content-type": "application/json", **(headers or {})}
    req = urllib.request.Request(f"http://127.0.0.1:{port}{path}", data=data, headers=h, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, json.loads(r.read() or b"null")
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read() or b"null")
        except ValueError:
            return e.code, None


def _bearer(wire: str) -> dict:
    return {"authorization": "Bearer " + wire}


def secret_of(person: str) -> str | None:
    return _SECRETS.get((_scope(), person))


def learn(path: str, status: int, body) -> None:
    """A secret the door handed the test (its own `/enroll`) is remembered for the seat."""
    if path == "/enroll" and status == 201 and isinstance(body, dict) and body.get("secret"):
        _SECRETS[(_scope(), body["person"])] = body["secret"]


def owner(port: int) -> str:
    """The session's owner — the ceremony run once, at the first door that asks."""
    with _LOCK:
        sc = _scope()
        if _OWNER.get(sc):
            return _OWNER[sc]
        person = f"did:orreth:person:owner-{_secrets.token_hex(3)}"
        s, b = _raw(port, "POST", "/enroll", {"person": person})          # the ceremony: the door stands open
        assert s == 201, f"the ceremony's enroll refused in {sc}: {s} {b}"
        _SECRETS[(sc, person)] = b["secret"]
        s, b = _raw(port, "POST", "/enroll/confirm", {"person": person, "code": proof.totp(b["secret"])})
        assert s == 200, f"the ceremony's confirm refused: {s} {b}"
        _OWNER[sc] = person
        seat(port, person)                                                 # the first PROOF makes the owner
        return person


def seat(port: int, person: str | None = None) -> str:
    """The person's seat at this port (the wire), taken once per (port, person)."""
    with _LOCK:
        sc = _scope()
        person = person or owner(port)
        key = (port, sc, person)
        if key in _SEATS:
            return _SEATS[key]
        if (sc, person) not in _SECRETS:
            if person == _OWNER.get(sc):
                raise AssertionError("the owner's secret was lost")
            own = owner(port)
            s, b = _raw(port, "POST", "/enroll", {"person": person}, _bearer(seat(port, own)))
            assert s == 201, f"enrolling {person} on the owner's word refused in {sc}: {s} {b}"
            _SECRETS[(sc, person)] = b["secret"]
            s, b = _raw(port, "POST", "/enroll/confirm", {"person": person, "code": proof.totp(b["secret"])})
            assert s == 200, f"confirming {person} refused: {s} {b}"
        s, b = _raw(port, "POST", "/seat", {"person": person, "code": proof.totp(_SECRETS[(sc, person)])})
        assert s == 201, f"the seat for {person} refused in {sc}: {s} {b}"
        _SEATS[key] = b["wire"]
        return b["wire"]


def govern(port: int, person: str) -> None:
    """A test names a MASTER: declared on the RIG's ground (its tables stand in `public`;
    the test's `pg` connection stands in `spine_test`, a ground of its own), the cached
    seat forgotten so the next knock re-seats with `govern` — the shelf's and the Stable's
    doors are the owner's or a master's word (P7 sp8 row 3a)."""
    import psycopg
    from orreth_spine.rails import PG_DSN
    with psycopg.connect(PG_DSN, autocommit=True) as conn:
        proof.declare_master(conn, person, by="the test's word")
    forget_seat(port, person)


def forget_seat(port: int, person: str) -> None:
    with _LOCK:
        for k in [k for k in _SEATS if k[0] == port and k[2] == person]:
            del _SEATS[k]


def headers(port: int, person: str | None = None) -> dict:
    return _bearer(seat(port, person))


def actor_for(port: int, path: str, obj=None, query: str = "") -> str | None:
    """Whose seat a knock presents: the body's `by`, else its `person` (except at the
    doors where `person` names a TARGET), else the query's `person`, else the owner.
    A named person not yet seated is enrolled on the owner's word and seated (a test
    that means a STRANGER knocks with `unseated`)."""
    named = None
    if isinstance(obj, dict):
        named = obj.get("by") or (obj.get("person") if path not in TARGET_DOORS else None)
    if not named and query:
        named = (urllib.parse.parse_qs(query).get("person") or [None])[0]
    if named and str(named).startswith("did:orreth:person:"):
        return str(named)
    return owner(port)


def urlopen(url_or_req, timeout: float = 10):
    """`urllib.request.urlopen`, seated."""
    req = url_or_req if isinstance(url_or_req, urllib.request.Request) else urllib.request.Request(url_or_req)
    u = urllib.parse.urlsplit(req.full_url)
    port = u.port or 80
    obj = None
    if req.data:
        try:
            obj = json.loads(req.data)
        except ValueError:
            obj = None
    who = actor_for(port, u.path, obj, u.query)
    if who and not req.has_header("Authorization"):
        req.add_header("authorization", "Bearer " + seat(port, who))
    try:
        r = urllib.request.urlopen(req, timeout=timeout)
    except urllib.error.HTTPError:
        raise
    if u.path == "/enroll" and req.get_method() == "POST":
        raw = r.read()
        try:
            learn(u.path, r.status, json.loads(raw))
        except ValueError:
            pass
        return _Replayed(r, raw)
    return r


class _Replayed:
    """A response whose body was read once for the helper — read again by the test."""

    def __init__(self, r, raw: bytes):
        self.status, self.headers, self._raw = r.status, r.headers, raw
        self.code = r.status

    def read(self) -> bytes:
        return self._raw

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def get(port: int, path: str, person: str | None = None):
    """A seated GET → (status, json) — errors as tuples, never raised."""
    u = urllib.parse.urlsplit(path)
    who = person or actor_for(port, u.path, None, u.query)
    return _raw(port, "GET", path, None, _bearer(seat(port, who)) if who else None)


def post(port: int, path: str, obj, person: str | None = None):
    """A seated POST → (status, json) — errors as tuples, never raised; an `/enroll` the
    test posts is remembered for the seat."""
    who = person or actor_for(port, path, obj)
    s, b = _raw(port, "POST", path, obj, _bearer(seat(port, who)) if who else None)
    learn(path, s, b)
    return s, b


def unseated(port: int, method: str, path: str, obj=None, headers=None):
    """A bare knock — no seat, or the headers given (a forged one, an origin) — for the gate's own tests."""
    return _raw(port, method, path, obj, headers)
