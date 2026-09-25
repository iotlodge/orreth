# PROVENANCE: Claude Fable 5 (claude-fable-5) — rearch P3 sp1, the glass exists · 2026-09-16
# Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P6.5 sp1, the shelf's doors (`/services…`); the built-ins registered and probed at boot · 2026-09-22
# Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P6.5 sp2, the Tools keeper born with the rig; its beat; the reference clock by the dial · 2026-09-23
# Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P6 cure sp3 (the re-walk's wounds): W20 `/intentions/restart` · the harness door `GET /harness` · 2026-09-21
# Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P6 sp3, MITL born · the toggle and the impact doors · 2026-09-21
# Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P6 sp4, placement policy v0 · 2026-09-21
# Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P6 cure sp1 (kernel), walk #7's W5 · W12 · W14 · W19 doors · 2026-09-21
# Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P6.5 sp3, the Stable keeper: the gateway is the bridge's lane; the Stable's doors (/minds …); the keeper's beat; W29 · 2026-09-24
# Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp5, memory and the export: the pure laws factored for the fixture; the kernel's own self signs the export · 2026-09-24
# Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch walk #13 cures: W51 a roll is a fact the feed carries · W52 the digest in the human's zone · THE GUIDE (JB's seed) · 2026-09-24
"""The glass server v0 (canon 0001): the one place a human connects.

It serves the Bridge page, the live feed (SSE), and the human-path
doors — ask, read, confirm. The browser touches nothing else: no
broker, no ground, no resident directly. Every door opens a short-lived
connection of its own (the handler is threaded), reads or writes
through the same laws as everything else, and answers in plain JSON.

BridgeRig is the whole dev Operating State in one object: the relay
breathing the outbox onto the rail, the dispatcher turning facts into
invocations, the librarian serving, and the glass on top. One command:

    python -m orreth_spine.glass        # http://127.0.0.1:4600/

(a real mind when ANTHROPIC_API_KEY is present; a fake one otherwise —
the laws are identical either way).
"""
from __future__ import annotations

import json
import os
import secrets
import sys
import threading
import time
from pathlib import Path

import psycopg

from . import bridgefeed, digest, dispatch, envelope as ev, export, ground, harness, intent, markers, mitl, monitor, outbox
from . import placement, presence, projector, proof, scheduler, services, sinks
from .rails import PG_DSN
from .resident import ASK_RECEIVED, CONFIRM_NEEDED, JOURNEY, REPLY, PlacementRefused, Resident

GLASS_DIR = Path(__file__).resolve().parents[1] / "glass"
SESSION_OPENED = "orreth.session.opened.v1"     # W51: a roll is a fact — every door's sessions list follows
GUIDE = Path(__file__).resolve().parents[1] / "guide" / "guide.v0.json"   # THE GUIDE, kept by the kernel
FEED_TOPICS = [ASK_RECEIVED, JOURNEY, REPLY, CONFIRM_NEEDED, SESSION_OPENED,
               harness.HARNESS_FAILED,   # a failing run escalates to the chat
               markers.MARKER_SET,       # a marker set is seen where it lands
               dispatch.ASK_REFUSED,     # W19: an ask to a body not here, answered at the door
               monitor.WATCH_TURNED]     # W14: a watch turned red or green


def ask_view(conn, ask_id: str) -> dict | None:
    """The Questions door: the ask row plus its journey notes, read from
    the ground (the outbox is the dev log; notes ride the events)."""
    cur = conn.cursor()
    # a glass serves ONLY its own world's ground: another world's ask is
    # "no such ask" here — the refusal wears one face (covenant rule 4)
    cur.execute("SELECT text, person, status, reply, served_by, target,"
                " scope, asked_at, replied_at, time_window, session, marker,"
                " proof, held"
                " FROM spine_asks WHERE ask_id = %s AND scope = %s",
                (ask_id, ev.scope()))
    row = cur.fetchone()
    if row is None:
        return None
    origin = None                    # block 11: what this ask serves — its root
    if row[11]:
        cur.execute("SELECT r.marker_id, r.kind, r.parent, r.ref, r.by_did, r.note, r.at, 0"
                    " FROM spine_markers m JOIN spine_markers r ON r.marker_id = m.root"
                    " WHERE m.marker_id = %s", (row[11],))
        r0 = cur.fetchone()
        if r0 and r0[0] != row[11]:
            [o] = markers.with_words(conn, [markers._row(r0)])
            origin = {"marker": o["id"], "kind": o["kind"], "ref": o["ref"], "by": o["by"],
                      "words": o.get("words") or o.get("note")}
    cur.execute("SELECT body FROM spine_outbox"
                " WHERE convert_from(body, 'UTF8') LIKE %s"
                " ORDER BY outbox_id", (f"%{ask_id}%",))
    notes = []
    for (body,) in cur.fetchall():
        try:
            e = ev.decode(bytes(body))
        except Exception:
            continue
        if e.get("type") == JOURNEY:
            notes.append(e.get("payload", {}).get("note", ""))
    offer = None                     # walk #7: the monitor's OFFER, one click
    if row[2] == "replied" and row[3] and (row[5] == "monitor" or _name_of(conn, row[4]) == "monitor"):
        offer = monitor.offer_in(row[3])
    return {"ask_id": ask_id, "text": row[0], "person": row[1],
            "status": row[2], "reply": row[3], "served_by": row[4],
            "offer": offer,         # {words, ask} when the monitor offered a watch
            "target": row[5],       # who the ask was routed to: a targeted
            "scope": row[6],        # command reaches only its target
            "asked_at": row[7].isoformat(),
            "replied_at": row[8].isoformat() if row[8] else None,
            "window": json.loads(row[9]) if row[9] else None,  # P6
            "session": row[10],                                 # P20
            "marker": row[11], "origin": origin,                # 0006 · 0007
            "proof": row[12] or "L1",                           # P6 sp1: the level the act wore
            "hold": ({"tool": h.get("tool"), "class": h.get("class", "consequential"),
                      "level": h.get("level", "L2"),                 # what the hold demands
                      **({"needs_code": True, "code_ok": bool(h.get("code_ok"))}   # W5: the asker's
                         if h.get("needs_code") else {})}            # code, then the master
                     if row[2] == "awaiting-confirm" and (h := json.loads(row[13] or "{}")) else None),
            "journey": [n for n in notes if n]}


def _name_of(conn, did: str | None) -> str | None:
    if not did or not did.startswith("did:"):
        return None
    cur = conn.cursor()
    cur.execute("SELECT name FROM spine_joins WHERE did = %s AND scope = %s ORDER BY join_id DESC LIMIT 1",
                (did, ev.scope()))
    r = cur.fetchone()
    return r[0] if r else None


def asks_view(conn, limit: int = 30) -> list[dict]:
    """The Objectives band's door (canon 0001 P13): everything running,
    everything run — newest first, every row a door."""
    cur = conn.cursor()
    cur.execute(
        "SELECT ask_id, text, person, status, served_by, target, fanout,"
        " asked_at, replied_at FROM spine_asks WHERE scope = %s"
        " ORDER BY asked_at DESC LIMIT %s", (ev.scope(), limit))
    return [{"ask_id": r[0], "text": r[1][:140], "person": r[2],
             "status": r[3], "served_by": r[4], "target": r[5],
             "fanout": r[6], "asked_at": r[7].isoformat(),
             "replied_at": r[8].isoformat() if r[8] else None}
            for r in cur.fetchall()]


KERNEL_DUTIES = [                # every body runs these — kernel-required,
    "serve the invocation rail",   # visible in its card, never editable (P16)
    "emit the journey at every hop",
    "think only on the meter",
    "wear the covenant policy it joined with",
]


def mind_line(conn, name: str, did: str, template: dict | None) -> dict | None:
    """P6.5 sp3 (walk #12, JB's callout): which mind this body thinks with
    NOW and why — the Stable's decision for it (a pin · an assignment ·
    the template's model · the class), and the last thought it rode."""
    mind = (template or {}).get("mind") or {}
    if not mind:
        return None
    from . import stable
    d = stable.resolve_for(conn, subject=name, model=mind.get("model"), klass=mind.get("class"), pin=mind.get("pin"))
    out = {"stall": d.get("stall"), "why": d.get("why") or d.get("reason"), "degraded": bool(d.get("degraded"))}
    if d.get("stall"):
        s = services.get(conn, d["stall"]) or {}
        m = s.get("manifest") or {}
        out["route"] = f"{m.get('provider', '?')} {m.get('model', '?')}"; out["klass"] = m.get("class")
    cur = conn.cursor()
    cur.execute("SELECT to_regclass('spine_meter') IS NOT NULL")
    if cur.fetchone()[0]:
        cur.execute("SELECT stall, usd, at, ok FROM spine_meter WHERE did = %s AND stall IS NOT NULL ORDER BY meter_id DESC LIMIT 1", (did,))
        r = cur.fetchone()
        if r:
            out["last"] = {"stall": r[0], "usd": r[1], "at": r[2].isoformat(), "ok": r[3]}
    return out


def crew_view(conn, bodies: dict | None = None) -> list[dict]:
    """The Crew workspace's door: one card per body in this world —
    who it is, what it wears, what it declared, and BOTH SIDES (canon
    0004): side A, the asks it served; side B, the duties it runs. The
    kernel-required duties are listed and immutable; human- and role-
    scheduled ones arrive with the scheduler (AG-4's CRUD half)."""
    cur = conn.cursor()
    cur.execute(
        "SELECT DISTINCT ON (name) name, kind, did, life, joined_at,"
        " policy_version, template_hash, capabilities, placement, nature FROM spine_joins"
        " WHERE scope = %s ORDER BY name, join_id DESC", (ev.scope(),))
    alive = {b["did"]: b["alive"] for b in presence.roster(conn)}
    here = placement.ground_declares()      # P6 sp4: where this ground is
    refused = placement.refusals(conn)      # the bodies it could not seat
    cards = []
    for name, kind, did, life, joined, pv, th, caps, plc, nature in cur.fetchall():
        cur.execute("SELECT count(*), max(replied_at) FROM spine_asks"
                    " WHERE served_by = %s AND scope = %s AND status <> 'received'",
                    (did, ev.scope()))
        n, last = cur.fetchone()
        prof = json.loads(plc) if plc else dict(placement.DEFAULT)
        r = refused.pop(name, None)
        if r is not None and r["refused_at"] > joined:   # refused SINCE its last join:
            cards.append(_refused_card(r, nature)); continue   # the picture says so (rule 7)
        body = (bodies or {}).get(name)
        cards.append({
            "mind": mind_line(conn, name, did, getattr(body, "template", None)) if body is not None else None,
            "name": name, "kind": kind, "did": did, "lives": life,
            "nature": nature or "",         # W7: what it IS, one line
            "joined_at": joined.isoformat(), "policy_version": pv,
            "alive": alive.get(did),        # M2: a fresh lease, or dormant
            "template": th[:12], "capabilities": json.loads(caps or "[]"),
            "placement": placement.card(prof, here),    # where it stands, and why
            "side_a": {"asks_served": int(n),
                       "last_served": last.isoformat() if last else None},
            "side_b": {"kernel": [{"duty": d, "editable": False} for d in KERNEL_DUTIES],
                       "human": [], "role": []}})
    for r in refused.values():              # never joined here at all: refused at birth
        cards.append(_refused_card(r))
    return cards


def _refused_card(r: dict, nature: str | None = None) -> dict:
    """A body the ground could not seat: greyed, the reason in words —
    never silently absent (rule 7). Nothing to stop (rule 11): the human
    retires the refusal by fixing the template."""
    prof = r["placement"]
    ground = {"cell": r["ground"]["cell"], "metal": r["ground"]["metal"], "secrets": []}
    c = placement.card(prof, ground)
    c["honored"], c["reasons"], c["why"] = False, list(r["reasons"]), "refused: " + "; ".join(r["reasons"])
    return {"name": r["name"], "kind": r["kind"], "did": r["did"], "lives": 0, "nature": nature or "",
            "joined_at": None, "policy_version": None, "alive": False, "refused": True,
            "refused_at": r["refused_at"].isoformat(), "marker": r["marker"],
            "template": r["template"][:12], "capabilities": [], "placement": c,
            "side_a": {"asks_served": 0, "last_served": None},
            "side_b": {"kernel": [], "human": [], "role": []}}


def recall_view(conn, *, ref: str | None = None, ask: str | None = None,
                session: str | None = None, window: tuple[str, str] | None = None,
                person: str = "did:orreth:person:jb", at: str | None = None,
                history: bool = False) -> dict | None:
    """Verbatim recall (MEM-1, canon 0003): every word, byte-exact — by
    ref (a memory), by ask, by session (the worldline), or by timeframe
    (the human's lens over all their worldlines in this world)."""
    from .resident import ensure_schema as _ground
    from .store import ensure_schema as _mem
    _ground(conn); _mem(conn)
    cur = conn.cursor()
    if ref:
        ns, _, key = ref.partition("/")
        from .store import OrrethStore
        st = OrrethStore(conn, by_did=person)
        if history:                        # the lineage, never an overwrite
            versions = st.history(ns, key)
            return {"ref": ref, "history": versions} if versions else None
        body = st.get(ns, key, at=at)      # true now — or true then (MEM-4)
        if body is None:
            return None
        cur.execute("SELECT hash, by_did, landed_at, valid_from, valid_to FROM spine_memories"
                    " WHERE namespace = %s AND key = %s AND scope = %s AND body = %s"
                    " ORDER BY valid_from DESC LIMIT 1", (ns, key, ev.scope(), body))
        r = cur.fetchone()
        return {"memory": {"ref": ref, "body": body, "hash": r[0], "by": r[1],
                           "landed_at": r[2].isoformat(), "valid_from": r[3].isoformat(),
                           "valid_to": r[4].isoformat() if r[4] else None,
                           "as_of": at}}
    if ask:
        v = ask_view(conn, ask)
        return {"ask": v} if v else None
    if session:
        v = session_view(conn, session)
        return {"session": v} if v else None
    if window:
        cur.execute(
            "SELECT ask_id, text, reply, asked_at, replied_at, served_by FROM spine_asks"
            " WHERE person = %s AND scope = %s AND asked_at BETWEEN %s AND %s"
            " ORDER BY asked_at", (person, ev.scope(), window[0], window[1]))
        asks = [{"ask_id": r[0], "text": r[1], "reply": r[2], "asked_at": r[3].isoformat(),
                 "replied_at": r[4].isoformat() if r[4] else None, "served_by": r[5]}
                for r in cur.fetchall()]
        cur.execute(
            "SELECT namespace, key, body, hash, landed_at FROM spine_memories"
            " WHERE scope = %s AND landed_at BETWEEN %s AND %s ORDER BY landed_at",
            (ev.scope(), window[0], window[1]))
        memories = [{"ref": f"{r[0]}/{r[1]}", "body": r[2], "hash": r[3],
                     "landed_at": r[4].isoformat()} for r in cur.fetchall()]
        return {"window": {"from": window[0], "to": window[1]}, "asks": asks,
                "memories": memories}
    return None


def open_session(conn, person: str, title: str | None = None,
                 archive: str | None = None, opt_out: bool = False) -> str:
    """Roll (P20): a fresh worldline for this human in this world. The
    previous session is not touched — archived means 'not active', never
    'gone' (every word stays in the Record) — and its roll is an EPISODE
    BOUNDARY: the archived session gets its digest (MEM-3)."""
    from .resident import ensure_schema
    ensure_schema(conn)
    sid = "ses_" + secrets.token_hex(6)
    outbox.ensure_schema(conn)
    e = ev.make_envelope(kind="event", type=SESSION_OPENED, universe_id=ev.scope(), scope_path=ev.scope(),
                         payload=session_payload(sid, person, title, archive, "opt-out" if opt_out else "in"),
                         correlation_id=sid, authority_chain=[person])
    with conn.transaction():
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO spine_sessions (session_id, person, scope, title, state)"
            " VALUES (%s, %s, %s, %s, %s)",
            (sid, person, ev.scope(), title, "opt-out" if opt_out else "in"))
        outbox.add_row(cur, ev.encode(e), e["message_id"])     # W51: the roll is a fact the feed carries
    if archive:                # AFTER the new row stands: the archived span ends at this opening, so the
        digest.build(conn, archive, by=person)                 # digest built here is the one a rebuild finds
    return sid                 # P11: what happens in an opt-out state stays there


def session_payload(session_id: str, person: str, title: str | None, archived: str | None, state: str) -> dict:
    """`orreth.session.opened.v1`'s payload (fixture `session_fact`): the
    session as ref, its person, its title, the session it archived, its state."""
    return {"ref": session_id, "hash": ev.content_hash(session_id), "person": person,
            "title": title or None, "archived": archived or None, "state": state}


def sessions_view(conn, person: str, limit: int = 30) -> list[dict]:
    """List (P20): this human's worldlines in this world, newest first —
    each with its span, how many asks it holds, and its last words."""
    cur = conn.cursor()
    digest.ensure_schema(conn)
    # a listed session without its short version gets it from the log — the
    # Digest is a projection, rebuildable at any time (walk #5: sessions
    # archived before the Digest existed showed none)
    cur.execute("SELECT s.session_id FROM spine_sessions s WHERE s.person = %s AND s.scope = %s"
                " AND EXISTS (SELECT 1 FROM spine_asks a WHERE a.session = s.session_id)"
                " AND NOT EXISTS (SELECT 1 FROM spine_digests d WHERE d.kind = 'session'"
                "  AND d.ref = s.session_id AND d.scope = s.scope AND d.valid_to IS NULL)"
                " ORDER BY s.opened_at DESC LIMIT %s", (person, ev.scope(), limit))
    for (sid,) in cur.fetchall():
        digest.build(conn, sid, by="the digest builder")
    cur.execute(
        "SELECT s.session_id, s.title, s.opened_at,"
        " count(a.ask_id), max(a.asked_at), coalesce(s.state, 'in'),"
        " (SELECT text FROM spine_asks WHERE session = s.session_id"
        "  ORDER BY asked_at DESC LIMIT 1),"
        " (SELECT body FROM spine_digests d WHERE d.kind = 'session'"
        "  AND d.ref = s.session_id AND d.scope = s.scope AND d.valid_to IS NULL)"
        " FROM spine_sessions s LEFT JOIN spine_asks a"
        " ON a.session = s.session_id"
        " WHERE s.person = %s AND s.scope = %s"
        " GROUP BY s.session_id ORDER BY s.opened_at DESC LIMIT %s",
        (person, ev.scope(), limit))
    return [{"session_id": r[0], "title": r[1], "opened_at": r[2].isoformat(),
             "asks": int(r[3]), "last_at": r[4].isoformat() if r[4] else None,
             "state": r[5], "last_words": (r[6] or "")[:140],
             "short_version": (r[7] or "")[:280] or None}   # MEM-3, at a glance
            for r in cur.fetchall()]


def session_view(conn, session_id: str) -> dict | None:
    """Load (P20): the session and its asks in the order they were asked
    — the chat re-renders them whole; another world's session is 'no
    such session' (one face)."""
    cur = conn.cursor()
    cur.execute("SELECT session_id, person, title, opened_at FROM spine_sessions"
                " WHERE session_id = %s AND scope = %s", (session_id, ev.scope()))
    row = cur.fetchone()
    if row is None:
        return None
    cur.execute(
        "SELECT ask_id, text, status, reply, served_by, target, asked_at,"
        " replied_at, time_window FROM spine_asks WHERE session = %s"
        " ORDER BY asked_at", (session_id,))
    asks = [{"ask_id": r[0], "text": r[1], "status": r[2], "reply": r[3],
             "served_by": r[4], "target": r[5], "asked_at": r[6].isoformat(),
             "replied_at": r[7].isoformat() if r[7] else None,
             "window": json.loads(r[8]) if r[8] else None}
            for r in cur.fetchall()]
    return {"session_id": row[0], "person": row[1], "title": row[2],
            "opened_at": row[3].isoformat(), "scope": ev.scope(), "asks": asks}


def residents_view(conn) -> list[dict]:
    """The chat's right edge: who lives here — name, self, lives."""
    cur = conn.cursor()
    cur.execute(
        "SELECT DISTINCT ON (name) name, did, life, joined_at, kind, nature"
        " FROM spine_joins WHERE scope = %s ORDER BY name, join_id DESC",
        (ev.scope(),))
    return [{"name": r[0], "did": r[1], "lives": r[2],
             "joined_at": r[3].isoformat(), "kind": r[4], "nature": r[5] or ""}
            for r in cur.fetchall()]


KEEPERS = ("toolkeeper", "stablekeeper")     # the bodies whose question the next bare words answer (W29)


def follow_up_to(conn, text: str, session: str | None, names: list[str]) -> str | None:
    """W29 (walk #10): when a keeper ASKED for something ("what name shall
    it wear?"), the next bare words in that session are the ANSWER —
    routed to the keeper, never fanned out; and a bare keeper name opens
    the keeper. Otherwise None."""
    bare = (text or "").strip().lower().rstrip("?.! ")
    for n in names:
        if n.lower() in KEEPERS and bare == n.lower():
            return n
    if not session:
        return None
    cur = conn.cursor()
    cur.execute("SELECT a.served_by, a.reply, j.name FROM spine_asks a JOIN spine_joins j ON j.did = a.served_by"
                " AND j.scope = a.scope WHERE a.scope = %s AND a.session = %s AND a.status = 'replied'"
                " ORDER BY a.replied_at DESC LIMIT 1", (ev.scope(), session))
    r = cur.fetchone()
    if r is None or str(r[2]).lower() not in KEEPERS:
        return None
    reply = " ".join(str(r[1] or "").split())
    return r[2] if reply.rstrip().endswith("?") else None


def address_to(conn, text: str, to: list[str] | None, session: str | None = None) -> list[str] | None:
    """W7: a name at the head of the ask selects THAT body alone — when
    it is a body of this world (joined here, by name); the fan-out stays
    for an unaddressed ask. The door's rule, the glass's too. W29: a
    keeper's question keeps the next bare words."""
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT name FROM spine_joins WHERE scope = %s", (ev.scope(),))
    names = [r[0] for r in cur.fetchall()]
    who = dispatch.address(text, names)
    if who:
        return [who]
    if to is None:
        who = follow_up_to(conn, text, session, names)
        if who:
            return [who]
    return to


def make_glass_handler(feed: bridgefeed.Feed, dsn: str, bodies: dict | None = None,
                       gateway=None, services_home=None, kernel=None):
    Base = bridgefeed.make_handler(feed)
    bodies = bodies or {}            # the rig's bodies by name (the harness door)
    # P6.5 sp1: the shelf's doors probe a mind through the rig's gateway and
    # seat a new service's seed beside the agents' (None: ephemeral, tests)

    # every door connection is AUTOCOMMIT (the rig-loop law, now for doors
    # too): a door's bare read must never open an implicit transaction that
    # a later DDL guard or lock rides until the door returns
    class Handler(Base):
        def _json(self, code: int, obj) -> None:
            body = json.dumps(obj).encode()
            self.send_response(code)
            self.send_header("content-type", "application/json")
            self.send_header("access-control-allow-origin", "*")
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            path = self.path.split("?")[0]
            if path in ("/feed", "/health"):
                return Base.do_GET(self)
            if path in ("/", "/index.html"):
                html = (GLASS_DIR / "index.html").read_bytes()
                self.send_response(200)
                self.send_header("content-type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write(html)
                return
            if path.startswith("/ask/"):
                with psycopg.connect(dsn, autocommit=True) as conn:
                    view = ask_view(conn, path.split("/ask/", 1)[1])
                if view is None:
                    return self._json(404, {"error": "no such ask"})
                return self._json(200, view)
            if path == "/asks":
                with psycopg.connect(dsn, autocommit=True) as conn:
                    return self._json(200, {"asks": asks_view(conn)})
            if path == "/residents":
                with psycopg.connect(dsn, autocommit=True) as conn:
                    return self._json(200,
                                      {"residents": residents_view(conn)})
            if path == "/crew":
                with psycopg.connect(dsn, autocommit=True) as conn:
                    return self._json(200, {"crew": crew_view(conn, bodies)})
            if path == "/monitor":
                with psycopg.connect(dsn, autocommit=True) as conn:
                    return self._json(200, monitor.snapshot(conn))
            if path.startswith("/schedules/"):           # the card's side B
                with psycopg.connect(dsn, autocommit=True) as conn:
                    return self._json(200, scheduler.for_runner(
                        conn, path.split("/schedules/", 1)[1]))
            if path == "/recall":
                from urllib.parse import parse_qs
                qs = {k: v[0] for k, v in parse_qs(self.path.split("?", 1)[1]).items()} \
                    if "?" in self.path else {}
                try:
                    with psycopg.connect(dsn, autocommit=True) as conn:
                        view = recall_view(
                            conn, ref=qs.get("ref"), ask=qs.get("ask"),
                            session=qs.get("session"),
                            window=(qs["from"], qs["to"]) if qs.get("from") and qs.get("to") else None,
                            person=qs.get("person") or "did:orreth:person:jb",
                            at=qs.get("at"), history=qs.get("history") == "1")
                except psycopg.DataError:
                    return self._json(400, {"error": "the window is two ISO times, from and to"})
                if view is None:
                    return self._json(404, {"error": "nothing recalled — one face"})
                return self._json(200, view)
            if path == "/sessions":
                from urllib.parse import parse_qs
                qs = parse_qs(self.path.split("?", 1)[1]) if "?" in self.path else {}
                person = (qs.get("person") or ["did:orreth:person:jb"])[0]
                with psycopg.connect(dsn, autocommit=True) as conn:
                    return self._json(200, {"sessions": sessions_view(conn, person)})
            if path == "/mitl":                           # P6 sp3: is MITL in the lit crew? what does it wear?
                from urllib.parse import parse_qs
                qs = {k: v[0] for k, v in parse_qs(self.path.split("?", 1)[1]).items()} \
                    if "?" in self.path else {}
                person = qs.get("person") or "did:orreth:person:jb"
                with psycopg.connect(dsn, autocommit=True) as conn:
                    ont = mitl.ontology(conn)
                    return self._json(200, {
                        "name": mitl.NAME, "expansion": mitl.EXPANSION,
                        "summoned": mitl.summoned(conn, qs.get("session") or None, person),
                        "ontology": {"passages": len(ont),
                                     "files": sorted({o["path"] for o in ont})},
                        "citations": mitl.citations()})      # W15: path#n → a human name
            if path == "/proof":                          # P6 sp1: enrolled? who are the masters?
                from urllib.parse import parse_qs
                qs = parse_qs(self.path.split("?", 1)[1]) if "?" in self.path else {}
                person = (qs.get("person") or ["did:orreth:person:jb"])[0]
                with psycopg.connect(dsn, autocommit=True) as conn:
                    return self._json(200, {"person": person, "enrolled": proof.enrolled(conn, person),
                                            "masters": proof.masters(conn)})
            if path == "/analyzer":                      # P25: origins, from the ground
                from urllib.parse import parse_qs
                qs = {k: v[0] for k, v in parse_qs(self.path.split("?", 1)[1]).items()} \
                    if "?" in self.path else {}
                with psycopg.connect(dsn, autocommit=True) as conn:
                    if qs.get("origin"):
                        return self._json(200, markers.origin(conn, qs["origin"]))
                    return self._json(200, {"origins": markers.origins(conn)})
            if path == "/intentions":                    # 0007: the standing purposes
                from urllib.parse import parse_qs
                qs = {k: v[0] for k, v in parse_qs(self.path.split("?", 1)[1]).items()} \
                    if "?" in self.path else {}
                with psycopg.connect(dsn, autocommit=True) as conn:
                    return self._json(200, {"intentions": intent.listing(
                        conn, serves=qs.get("serves"), kind=qs.get("kind"))})
            if path in ("/minds", "/minds/spend", "/minds/fuel", "/minds/search"):   # P6.5 sp3: the Stable's doors
                from urllib.parse import parse_qs
                from . import stable
                qs = {k: v[0] for k, v in parse_qs(self.path.split("?", 1)[1]).items()} \
                    if "?" in self.path else {}
                with psycopg.connect(dsn, autocommit=True) as conn:
                    if path == "/minds/spend":
                        return self._json(200, stable.spend(conn))
                    if path == "/minds/fuel":                 # a body's gauge, by name
                        from .tools import _did_of_body
                        did = _did_of_body(conn, str(qs.get("name") or ""))
                        if did is None:
                            return self._json(404, {"error": f"no body named {qs.get('name')!r} is joined here"})
                        gw = stable.Gateway()
                        return self._json(200, {"name": qs.get("name"), "fuel": stable.fuel(conn, did, gw if gw.ready() else None)})
                    if path == "/minds/search":
                        rows = stable.search(conn, qs.get("q"), klass=qs.get("klass"),
                                             max_in_per_m=float(qs["max_in_per_m"]) if qs.get("max_in_per_m") else None,
                                             modality=qs.get("modality"))
                        return self._json(200, {"minds": [dict(r, words=stable.stall_words(r)) for r in rows]})
                    gw = stable.Gateway()
                    return self._json(200, {"minds": [dict(r, words=stable.stall_words(r)) for r in stable.stalls(conn)],
                                            "assignments": stable.assignments(conn),
                                            "gateway": {"base": gw.base, "ready": gw.ready()}})
            if path == "/guide":                         # THE GUIDE (JB's seed, walk #13): kept by the kernel, the same on every door
                try:
                    return self._json(200, json.loads(GUIDE.read_text("utf-8")))
                except (OSError, ValueError) as e:
                    return self._json(500, {"error": f"the guide is not at {GUIDE} — {e}"})
            if path == "/harness":                       # walk #8: the world checks, off the ground
                with psycopg.connect(dsn, autocommit=True) as conn:
                    ch = harness.checks(conn)
                    return self._json(200, {"checks": ch, "ok": all(c["ok"] for c in ch),
                                            "last": monitor.snapshot(conn, rails=False)["harness"]})
            if path == "/markers/kinds":                 # the registry
                with psycopg.connect(dsn, autocommit=True) as conn:
                    return self._json(200, {"kinds": markers.kinds(conn)})
            if path == "/services":                      # P6.5 sp1: the shelf — every service, its ladder state
                from urllib.parse import parse_qs
                qs = {k: v[0] for k, v in parse_qs(self.path.split("?", 1)[1]).items()} \
                    if "?" in self.path else {}
                kind = qs.get("kind") or None
                if kind and kind not in services.KINDS:
                    return self._json(400, {"error": f"a kind is one of {', '.join(services.KINDS)}"})
                with psycopg.connect(dsn, autocommit=True) as conn:
                    here = placement.ground_declares()
                    return self._json(200, {"services": services.listing(conn, kind=kind),
                                            "kinds": list(services.KINDS),
                                            "ground": {"cell": here["cell"], "metal": here["metal"]}})
            if path == "/markers":                       # the tree · the ancestry · the stream
                from urllib.parse import parse_qs
                qs = {k: v[0] for k, v in parse_qs(self.path.split("?", 1)[1]).items()} \
                    if "?" in self.path else {}
                with psycopg.connect(dsn, autocommit=True) as conn:
                    if qs.get("root"):
                        return self._json(200, {"root": qs["root"], "tree": markers.with_words(conn, markers.tree(conn, qs["root"]))})
                    if qs.get("from"):
                        return self._json(200, {"from": qs["from"], "ancestry": markers.with_words(conn, markers.ancestry(conn, qs["from"]))})
                    return self._json(200, {"markers": markers.stream(
                        conn, kind=qs.get("kind"), grp=qs.get("group"))})
            if path == "/export":                        # P6 sp2: the compliance export — a READ
                from urllib.parse import parse_qs
                qs = {k: v[0] for k, v in parse_qs(self.path.split("?", 1)[1]).items()} \
                    if "?" in self.path else {}
                person = qs.get("person") or "did:orreth:person:jb"
                fmt = qs.get("format") or "json"
                if fmt not in ("json", "csv"):
                    return self._json(400, {"error": "format is json or csv"})
                try:
                    with psycopg.connect(dsn, autocommit=True) as conn:
                        bundle = export.build(          # the requester's OWN asks only;
                            conn, person=person,        # another's words are a named seam
                            session=qs.get("session"),
                            window=(qs["from"], qs["to"]) if qs.get("from") and qs.get("to") else None,
                            marker=qs.get("marker"), signer=kernel)   # P7 sp5: SIGNED by the kernel's own self
                except psycopg.DataError:
                    return self._json(400, {"error": "the window is two ISO times, from and to"})
                if fmt == "csv":
                    body = export.to_csv(bundle).encode("utf-8")
                    self.send_response(200)
                    self.send_header("content-type", "text/csv; charset=utf-8")
                    self.send_header("content-disposition",
                                     'attachment; filename="orreth-compliance.csv"')
                    self.send_header("access-control-allow-origin", "*")
                    self.end_headers()
                    self.wfile.write(body)
                    return
                return self._json(200, bundle)
            if path.startswith("/digest/"):            # the short version, and
                with psycopg.connect(dsn, autocommit=True) as conn:        # every source it cites
                    view = digest.of_session(conn, path.split("/digest/", 1)[1])
                if view is None:
                    return self._json(404, {"error": "no digest yet — one face"})
                return self._json(200, view)
            if path.startswith("/session/"):
                with psycopg.connect(dsn, autocommit=True) as conn:
                    view = session_view(conn, path.split("/session/", 1)[1])
                if view is None:
                    return self._json(404, {"error": "no such session"})
                return self._json(200, view)
            self.send_response(404)
            self.end_headers()

        def do_POST(self):
            path = self.path.split("?")[0]
            ln = int(self.headers.get("content-length") or 0)
            try:
                p = json.loads(self.rfile.read(ln) or b"{}")
            except Exception:
                p = {}
            if path == "/ask":
                text = str(p.get("text") or "").strip()
                if not text:
                    return self._json(400, {"error": "an empty ask asks "
                                                     "nothing"})
                person = str(p.get("person") or "did:orreth:person:jb")
                to = p.get("to") or None
                if to is not None and not (isinstance(to, list) and
                                           all(isinstance(t, str)
                                               for t in to) and to):
                    return self._json(400, {"error": "'to' names residents "
                                                     "as a list of names"})
                window = p.get("window") or None
                if window is not None and not (
                        isinstance(window, dict) and window.get("from")
                        and window.get("to")):
                    return self._json(400, {"error": "'window' is "
                                                     "{from, to} in ISO time"})
                session = str(p.get("session") or "") or None
                zone = str(p.get("zone") or "") or None      # W12: the human's zone, IANA
                # P23: the ask wears its kind — a typed prefix is the human's
                # flip and wins; else the chip's word; else the words' own read
                rw = intent.read_words(text)
                kind = rw["kind"] if rw["pinned"] else (str(p.get("kind") or "") or rw["kind"])
                if kind not in intent.ASK_KINDS:
                    return self._json(400, {"error": "'kind' is thought, objective, or intention"})
                text = rw["words"] if rw["pinned"] else text
                parent = str(p.get("parent") or "") or None   # "follow up on this by …"
                with psycopg.connect(dsn, autocommit=True) as conn:
                    if kind == "intention":               # declared, never asked (0007)
                        r2 = intent.read_words("intention: " + text)
                        try:
                            made = intent.declare(
                                conn, text, serves=str(p.get("serves") or r2["serves"]),
                                kind="human", by=person,
                                interests=p.get("interests") or r2["interests"],
                                every_s=p.get("every_s") or r2["every_s"],
                                runner=(to or [None])[0])
                        except (ValueError, markers.UnknownKind) as e:
                            return self._json(400, {"error": str(e)})
                        return self._json(201, {"intention": made})
                    to = address_to(conn, text, to, session)   # W7: "echo, …" reaches echo alone · W29: a keeper's follow-up
                    out = dispatch.submit_ask(conn, text, person=person,
                                              to=to, window=window,
                                              session=session, kind=kind,
                                              parent_marker=parent, zone=zone)
                if isinstance(out, list):
                    return self._json(201, {"ids": out})
                return self._json(201, {"id": out})
            if path == "/intentions":                 # declared by a human
                words = str(p.get("words") or p.get("text") or "").strip()
                person = str(p.get("person") or "did:orreth:person:jb")
                rw = intent.read_words("intention: " + words) if words else {}
                try:
                    with psycopg.connect(dsn, autocommit=True) as conn:
                        made = intent.declare(
                            conn, words, serves=str(p.get("serves") or rw.get("serves") or "business"),
                            kind="human", by=person,
                            interests=p.get("interests") or rw.get("interests") or [],
                            every_s=p.get("every_s") or rw.get("every_s"),
                            runner=str(p.get("runner") or "") or None)
                except (ValueError, markers.UnknownKind) as e:
                    return self._json(400, {"error": str(e)})
                return self._json(201, {"intention": made})
            if path in ("/intentions/stop", "/intentions/restart"):   # rule 11: the stop — and its reverse (W20)
                person = str(p.get("person") or "did:orreth:person:jb")
                iid = str(p.get("intention_id") or p.get("ref") or "")
                verb, act = (("stop", intent.stop) if path.endswith("/stop")
                             else ("restart", intent.restart))
                try:
                    with psycopg.connect(dsn, autocommit=True) as conn:
                        try:
                            made = act(conn, iid, person)
                        except proof.ProofRequired as pr:      # W5 · W20: ANY intention's stop — and
                            held = proof.hold_kernel_act(          # its restart — is grave, held for the code
                                conn, text=pr.what, person=person, tool=f"intent.{verb}",
                                args={"intention_id": iid}, level=pr.level,
                                session=str(p.get("session") or "") or None,
                                needs_code=pr.needs_code)          # the kernel's: code, then master
                            return self._json(202, {"held": held, "level": pr.level,
                                                    "needs_code": pr.needs_code})
                except KeyError:
                    return self._json(404, {"error": "no such intention"})
                return self._json(202, {"intention": made})
            if path == "/schedules":                  # a human schedule lands
                runner = str(p.get("runner") or "")
                text = str(p.get("text") or "").strip()
                every = int(p.get("every_s") or 0)
                if not (runner and text and every >= 5):
                    return self._json(400, {"error": "a schedule is {runner, text,"
                                                     " every_s >= 5}"})
                person = str(p.get("person") or "did:orreth:person:jb")
                with psycopg.connect(dsn, autocommit=True) as conn:
                    sid = scheduler.add(conn, runner, "human", text, every, person)
                return self._json(201, {"schedule_id": sid})
            if path == "/schedules/rest":             # the human's stop
                person = str(p.get("person") or "did:orreth:person:jb")
                try:
                    with psycopg.connect(dsn, autocommit=True) as conn:
                        scheduler.rest(conn, str(p.get("schedule_id") or ""), person)
                except scheduler.KernelRequired as e:
                    return self._json(403, {"error": str(e)})
                except KeyError:
                    return self._json(404, {"error": "no such schedule"})
                return self._json(202, {"rested": str(p.get("schedule_id"))})
            if path == "/harness/ab":                 # P6.5 sp3: the same golden cases against two minds
                name = str(p.get("template") or "librarian")
                body = bodies.get(name)
                if body is None:
                    return self._json(404, {"error": "no such body"})
                arms = [str(a) for a in (p.get("arms") or []) if str(a).strip()]
                if len(arms) < 2:
                    return self._json(400, {"error": "an A/B run names two or more minds as arms"})
                try:
                    with psycopg.connect(dsn, autocommit=True) as conn:
                        return self._json(200, harness.ab(conn, body, arms))
                except ValueError as e:
                    return self._json(400, {"error": str(e)})
            if path in ("/minds", "/minds/assign", "/minds/unassign", "/minds/refill", "/minds/check",
                        "/minds/retire", "/minds/restore"):      # P6.5 sp3: the Stable's doors — held acts hold
                from . import stable
                person = str(p.get("person") or "did:orreth:person:jb")
                session = str(p.get("session") or "") or None
                name = str(p.get("name") or "").strip().lower()
                try:
                    with psycopg.connect(dsn, autocommit=True) as conn:
                        if path == "/minds/check":
                            out = [services.check(conn, name, gateway=gateway, by=person)] if name else \
                                  services.check_all(conn, gateway=gateway, kind="mind", by=person)
                            return self._json(200, {"checked": out, "ok": all(c["ok"] for c in out)})
                        if path == "/minds/restore":
                            gw = stable.Gateway()
                            made = stable.restore_mind(conn, name, by=person, gw=gw if gw.ready() else None)
                            return self._json(201, {"service": made})
                        if path == "/minds/retire":
                            held = services.hold_retire(conn, name, person=person, session=session)
                            return self._json(202, {"held": held, "level": services.RETIRE_LEVEL, "class": services.RETIRE_CLASS})
                        if path == "/minds":                  # register — held
                            d = stable.deal(str(p.get("model") or ""), str(p.get("provider") or ""),
                                            base=p.get("base") or None, price=p.get("price"), context=p.get("context"),
                                            modalities=p.get("modalities"), klass=str(p.get("klass") or "standard"),
                                            key=p["key"] if p.get("key") else "auto")
                            args = {"name": name, "deal": d}
                            tool = stable.REGISTER_TOOL
                        elif path == "/minds/assign":
                            args = {"subject": str(p.get("subject") or "*"), "klass": str(p.get("klass") or stable.ANY),
                                    "stall": str(p.get("stall") or name)}
                            tool = stable.ASSIGN_TOOL
                        elif path == "/minds/unassign":
                            args = {"subject": str(p.get("subject") or "*"), "klass": str(p.get("klass") or stable.ANY)}
                            tool = stable.UNASSIGN_TOOL
                        else:                                 # refill
                            from .tools import _did_of_body
                            who = str(p.get("subject") or name)
                            did = _did_of_body(conn, who)
                            if did is None:
                                return self._json(404, {"error": f"no body named {who!r} is joined here"})
                            args = {"did": did, "name": who, "usd": float(p.get("usd") or 1.0)}
                            tool = stable.REFILL_TOOL
                        held = stable.hold(conn, tool, args, text=stable.act_words(tool, args), person=person, session=session)
                        return self._json(202, {"held": held, "level": stable.ACT_LEVEL, "class": stable.ACT_CLASS})
                except (services.ServiceRefused, stable.StableRefused, stable.GatewayDark, ValueError) as e:
                    return self._json(400, {"error": str(e)})
            if path == "/harness/run":                # on demand (the
                name = str(p.get("template") or "librarian")   # scheduled
                body = bodies.get(name)                        # run waits
                if body is None:                               # for the
                    return self._json(404, {"error": "no such body"})  # scheduler)
                with psycopg.connect(dsn, autocommit=True) as conn:
                    return self._json(200, harness.run(conn, body))
            if path == "/sessions":                   # roll a fresh one —
                person = str(p.get("person") or "did:orreth:person:jb")   # and
                with psycopg.connect(dsn, autocommit=True) as conn:                        # digest
                    sid = open_session(conn, person,                      # the one
                                       title=str(p.get("title") or "") or None,
                                       archive=str(p.get("archive") or "") or None,
                                       opt_out=bool(p.get("opt_out", False)))
                return self._json(201, {"session_id": sid})               # archived
            if path == "/markers/kinds":              # declare a kind
                try:
                    with psycopg.connect(dsn, autocommit=True) as conn:
                        made = markers.declare(conn, str(p.get("kind") or ""),
                                               str(p.get("group") or ""),
                                               str(p.get("description") or ""),
                                               str(p.get("person") or "did:orreth:person:jb"))
                except ValueError as e:
                    return self._json(400, {"error": str(e)})
                return self._json(201, made)
            if path == "/mark":                       # a human marks from the chat
                person = str(p.get("person") or "did:orreth:person:jb")
                ref = str(p.get("ref") or "")
                with psycopg.connect(dsn, autocommit=True) as conn:
                    if not ref and p.get("session"):
                        cur = conn.cursor()
                        cur.execute("SELECT ask_id FROM spine_asks WHERE session = %s"
                                    " ORDER BY asked_at DESC LIMIT 1", (str(p["session"]),))
                        row = cur.fetchone(); ref = row[0] if row else ""
                    if not ref:
                        return self._json(400, {"error": "mark what? name an ask or a session"})
                    cur = conn.cursor()
                    cur.execute("SELECT marker FROM spine_asks WHERE ask_id = %s", (ref,))
                    row = cur.fetchone(); parent = row[0] if row else None
                    try:
                        m = markers.set_marker(conn, str(p.get("kind") or ""), ref=ref,
                                               by=person, parent=parent,
                                               note=str(p.get("note") or "") or None)
                    except markers.UnknownKind as e:
                        return self._json(400, {"error": str(e)})
                    asked = markers.dispatch_interests(conn, m, ref, m.get("note"))
                return self._json(201, {"marker": m, "asked": asked})
            if path == "/digest":                     # on demand, or rebuild
                sid = str(p.get("session") or "")
                with psycopg.connect(dsn, autocommit=True) as conn:
                    made = digest.build(conn, sid, by=str(p.get("person") or "did:orreth:person:jb"))
                if made is None:
                    return self._json(404, {"error": "no such session"})
                return self._json(200 if not made["new"] else 201, made)
            if path == "/confirm":
                ask_id = str(p.get("ask_id") or "")
                approve = bool(p.get("approve", False))   # absent = cancel
                by = str(p.get("by") or p.get("person") or "did:orreth:person:jb")
                try:
                    with psycopg.connect(dsn, autocommit=True) as conn:
                        out = dispatch.confirm_ask(conn, ask_id, approve=approve, person=by,
                                                   code=str(p.get("code") or "") or None)
                except proof.NotConfirmed:                # rule 4: ONE face, every refusal
                    return self._json(403, dict(proof.ONE_FACE))
                return self._json(202, out)
            if path == "/mitl":                           # P6 sp3: the soft toggle — a recorded fact
                person = str(p.get("person") or "did:orreth:person:jb")
                with psycopg.connect(dsn, autocommit=True) as conn:
                    made = mitl.summon(conn, person, str(p.get("session") or "") or None,
                                       on=bool(p.get("summon", True)))
                return self._json(201, made)
            if path == "/impact":                         # P6 sp3: "expected impact of this change?"
                change = p.get("change")
                if not isinstance(change, dict):
                    return self._json(400, {"error": "a change is {kind, ref or draft, words}"})
                person = str(p.get("person") or "did:orreth:person:jb")
                try:
                    with psycopg.connect(dsn, autocommit=True) as conn:
                        made = mitl.impact(conn, change, person=person,
                                           session=str(p.get("session") or "") or None)
                except ValueError as e:
                    return self._json(400, {"error": str(e)})
                return self._json(201, made)
            if path in ("/services", "/services/version", "/services/check",
                        "/services/retire", "/services/restore", "/services/mcp"):   # P6.5 sp1: the shelf's doors — the owner's, plain words
                person = str(p.get("person") or "did:orreth:person:jb")
                name = str(p.get("name") or "").strip()
                try:
                    with psycopg.connect(dsn, autocommit=True) as conn:
                        if path == "/services/mcp":                   # P6.5 sp2: an MCP server through the one door —
                            from . import mcp                         # listed, its tools onto the shelf under it
                            made = mcp.register_server(
                                conn, name, str(p.get("locator") or ""), by=person,
                                secrets_with=p.get("secrets_with") or None,
                                placement=p.get("placement") or None, home=services_home)
                            return self._json(201, {"service": made["server"], "tools": made["tools"],
                                                    "info": made["info"]})
                        if path == "/services":                       # register
                            made = services.register(
                                conn, name, str(p.get("kind") or ""), p.get("manifest"), by=person,
                                placement=p.get("placement") or None,
                                secrets_with=p.get("secrets_with") or None, home=services_home)
                            return self._json(201, {"service": made})
                        if path == "/services/version":
                            made = services.version(conn, name, p.get("manifest"), by=person)
                            return self._json(200, {"service": made})
                        if path == "/services/check":                 # one by name, or every standing one
                            if name:
                                out = [services.check(conn, name, gateway=gateway, by=person)]
                            else:
                                out = services.check_all(conn, gateway=gateway,
                                                         kind=str(p.get("kind") or "") or None, by=person)
                            return self._json(200, {"checked": out, "ok": all(c["ok"] for c in out)})
                        if path == "/services/retire":                # held at the interlock (L2)
                            held = services.hold_retire(conn, name, person=person,
                                                        session=str(p.get("session") or "") or None)
                            return self._json(202, {"held": held, "level": services.RETIRE_LEVEL,
                                                    "class": services.RETIRE_CLASS})
                        made = services.restore(conn, name, by=person)   # a new fact
                        return self._json(201, {"service": made})
                except services.ServiceRefused as e:
                    return self._json(400, {"error": str(e)})
            if path == "/enroll":                         # P6 sp1: "enroll my authenticator"
                person = str(p.get("person") or "did:orreth:person:jb")
                try:
                    with psycopg.connect(dsn, autocommit=True) as conn:
                        made = proof.enroll(conn, person, code=str(p.get("code") or "") or None)
                except proof.NotConfirmed:                # re-enrolling is grave: the old code
                    return self._json(403, dict(proof.ONE_FACE))
                return self._json(201, made)
            if path == "/enroll/confirm":                 # the first code confirms it
                person = str(p.get("person") or "did:orreth:person:jb")
                try:
                    with psycopg.connect(dsn, autocommit=True) as conn:
                        made = proof.confirm_enrollment(conn, person, str(p.get("code") or ""))
                except proof.NotConfirmed:
                    return self._json(403, dict(proof.ONE_FACE))
                return self._json(200, made)
            self.send_response(404)
            self.end_headers()

    return Handler


class BridgeRig:
    """The whole dev Operating State: relay + dispatcher + one resident +
    the glass, breathing together; stopped together."""

    def __init__(self, *, gateway=None, template=None, port: int = 4600,
                 dsn: str | None = None, policy=None, second: bool = True,
                 home: str | os.PathLike | None = None):
        """`home` is where the residents' seeds live (covenant rule 1: a
        keypair is a self, and a self survives the process — the SAME
        librarian in every life of the Bridge). None mints ephemeral
        selves: tests only, never a resident (found by the Playwright:
        every relight had been a stranger wearing the librarian's name)."""
        spine = Path(__file__).resolve().parents[1]
        self.dsn = dsn or PG_DSN
        self._stop = threading.Event()
        self.feed = bridgefeed.Feed()
        self.gateway = gateway                       # P6.5 sp1: the mind the shelf probes
        from .identity import Identity
        self.kernel = Identity.kernel(home)          # P7 sp5: the kernel's own self — the export's signer
        self.services_home = services.services_home(home)   # the services' seeds, beside the agents'
        services.HOME = self.services_home           # P6.5 sp2: the keeper's door registers into the same home

        policy_path = policy or spine / "policy" / "covenant-policy.v1.json"
        self.resident = Resident(
            template or spine / "templates" / "librarian-resident.v0.json",
            gateway=gateway, home=home)
        self.resident.load_policy(policy_path)
        self.residents = [self.resident]
        if second:
            # the crew's second seat: the echo — mindless, honest, and
            # exactly what a fan-out needs to show two distinct lenses
            echo = Resident(spine / "templates" / "echo-resident.v0.json",
                            home=home)
            echo.load_policy(policy_path)
            self.residents.append(echo)
        # the includes (0004's third kind): planner · critic · grader — and
        # MITL (P6 sp3), the specialist of Orreth wearing the canon —
        # firmware bodies, same laws, called by the human as includes over
        # the session's results (MITL by the soft toggle and the impact door)
        self.firmware: dict[str, Resident] = {}
        # — and the TOOLS KEEPER (P6.5 sp2), the third-kind body that tends the
        # shelf on the human's word (its beat runs on the scheduler's clock)
        # — and the STABLE KEEPER (P6.5 sp3), the third-kind body that tends the minds
        from . import tools as _tools
        _tools.GATEWAY = gateway                     # the keepers' checks ping through the rig's lane
        for fn in ("planner", "critic", "grader", "mitl", "toolkeeper", "stablekeeper"):
            fw = Resident(spine / "templates" / f"firmware-{fn}.v0.json",
                          gateway=gateway, home=home)
            fw.load_policy(policy_path)
            self.residents.append(fw); self.firmware[fn] = fw
        # the first workspace: the Crew pull's agent — the ONE workspace
        # body wearing the crew binding (0004: one body, per-pull bindings)
        crew = Resident(spine / "templates" / "workspace-firmware.v0.json",
                        gateway=gateway, home=home,
                        binding=spine / "bindings" / "crew.v0.json")
        crew.load_policy(policy_path)
        monitor_agent = Resident(spine / "templates" / "workspace-firmware.v0.json",
                                 gateway=gateway, home=home,
                                 binding=spine / "bindings" / "monitor.v0.json")
        monitor_agent.load_policy(policy_path)
        self.residents += [crew, monitor_agent]
        self.workspaces = {"crew": crew, "monitor": monitor_agent}
        for r in self.residents:
            r.on_delta = self.feed.publish_delta
        from http.server import ThreadingHTTPServer
        self._httpd = ThreadingHTTPServer(
            ("127.0.0.1", port), make_glass_handler(
                self.feed, self.dsn, {r.name: r for r in self.residents},
                gateway=gateway, services_home=self.services_home, kernel=self.kernel))
        self.port = self._httpd.server_address[1]
        self.feed_ready = threading.Event()
        self.dispatcher_ready = threading.Event()
        self._threads = [
            threading.Thread(target=self._httpd.serve_forever, daemon=True),
            threading.Thread(target=bridgefeed.consume_rail,
                             args=(self.feed, FEED_TOPICS,
                                   f"glass-feed-{self.port}", self._stop),
                             kwargs={"ready": self.feed_ready}, daemon=True),
            threading.Thread(target=self._relay_loop, daemon=True),
            threading.Thread(target=self._dispatch_loop, daemon=True),
            threading.Thread(target=self._schedule_loop, daemon=True),
            threading.Thread(target=self._intent_loop, daemon=True),
        ] + [threading.Thread(target=self._serve_loop, args=(r,),
                              daemon=True) for r in self.residents]

    # Every long-lived rig connection is AUTOCOMMIT: a bare execute on a
    # non-autocommit connection opens an implicit transaction that never
    # commits, and the next ensure_schema inside it holds the xact-scoped
    # DDL lock forever — every door then queues behind it (found live in
    # the test fixture yesterday, then in the schedule loop today).
    def _relay_loop(self):
        sink = sinks.KafkaSink()
        with psycopg.connect(self.dsn, autocommit=True) as conn:
            ground.ensure_all(conn)         # every ground at birth
            while not self._stop.is_set():
                try:
                    outbox.relay_once(conn, sink)
                except Exception:
                    pass
                time.sleep(0.2)

    def _dispatch_loop(self):
        import secrets as _sec
        gid = f"glass-dispatcher-{_sec.token_hex(3)}"   # a group per life:
        with psycopg.connect(self.dsn, autocommit=True) as conn:          # a wedged ghost
            ground.ensure_all(conn)                      # every ground at birth
            while not self._stop.is_set():               # dies with its rig
                try:
                    dispatch.run_dispatcher(
                        conn, consumer="glass-dispatcher", group=gid,
                        stop=self._stop, ready=self.dispatcher_ready,
                        offset="earliest")  # no produce/assign race:
                    # replay is cheap (skips) and re-serves refuse
                except Exception:
                    time.sleep(0.5)

    def _schedule_loop(self):
        """The scheduler as a kernel organ: the kernel's duties registered
        at boot (immutable), then a beat every few seconds."""
        bodies = {r.name: r for r in self.residents}
        with psycopg.connect(self.dsn, autocommit=True) as conn:
            for _attempt in range(20):
                try:
                    ground.ensure_all(conn)       # every ground at birth
                    for r in self.residents:      # AG-6's scheduled run:
                        if harness.golden(r.name): # every mind with a golden set
                            scheduler.declared(conn, r.name, "kernel",
                                               "run the harness against my golden set",
                                               1800, "the kernel")
                    self._seed_shelf(conn)        # P6.5 sp1: the built-ins on the shelf, probed
                    self._seed_ref(conn)          # P6.5 sp2: the reference clock, by the dial
                    break
                except Exception:
                    time.sleep(0.3)
            next_beat = time.monotonic() + self._tool_check_s()
            next_stable = time.monotonic() + self._mind_check_s()
            while not self._stop.is_set():
                try:
                    scheduler.tick(conn, bodies)
                except Exception:
                    pass
                if time.monotonic() >= next_beat:     # P6.5 sp2: the keeper's beat — every MCP server
                    next_beat = time.monotonic() + self._tool_check_s()   # probed, its tools synced,
                    self._keeper_beat(conn)           # the strikes rule → a proposal the human cuts
                if time.monotonic() >= next_stable:   # P6.5 sp3: the Stable keeper's beat — every mind
                    next_stable = time.monotonic() + self._mind_check_s()   # pinged, the market's eyes,
                    self._stable_beat(conn)           # drift · EOL · drained · strikes → proposals
                time.sleep(5)

    @staticmethod
    def _tool_check_s() -> float:
        """The keeper's cadence (`SPINE_TOOL_CHECK_S`, default 300 s): a
        beat spawns every stdio server once — five minutes is the honest
        default for a dev rig."""
        try:
            return max(5.0, float(os.environ.get("SPINE_TOOL_CHECK_S") or 300))
        except ValueError:
            return 300.0

    @staticmethod
    def _mind_check_s() -> float:
        """The Stable keeper's cadence (`SPINE_MIND_CHECK_S`, default 600 s):
        a beat pings every mind once — real spending, so ten minutes."""
        from . import stable
        try:
            return max(5.0, float(os.environ.get(stable.MIND_CHECK_DIAL) or stable.MIND_CHECK_DEFAULT))
        except ValueError:
            return float(stable.MIND_CHECK_DEFAULT)

    def _stable_beat(self, conn) -> None:
        from . import stable
        keeper = self.firmware.get("stablekeeper")
        if keeper is None:
            return
        try:
            gw = stable.Gateway()
            out = stable.keeper_beat(conn, keeper=keeper.identity.did, gateway=self.gateway,
                                     gw=gw if gw.ready() else None)
            bad = [c["name"] for c in out["checked"] if c["ok"] is False]
            if bad or out["proposed"]:
                print(f"the Stable keeper's beat: {len(out['checked'])} minds pinged"
                      + (f", UNHEALTHY: {', '.join(bad)}" if bad else "")
                      + (f", proposed: {', '.join(p['kind'] + ' ' + p['name'] for p in out['proposed'])}" if out["proposed"] else ""),
                      file=sys.stderr, flush=True)
        except Exception as e:                       # noqa: BLE001
            print(f"the Stable keeper's beat stumbled: {type(e).__name__}: {e}", file=sys.stderr, flush=True)

    def _seed_ref(self, conn) -> None:
        """P6.5 sp2: with `SPINE_MCP_REF=1` the rig registers the reference
        clock server (`clock`: its `now` and `echo` land under it) — the
        librarian's `tools:now` then answers "what time is it in Denver?"
        through a real MCP tool. Off by default on the rig: a server is
        the human's to add. A refusal is said, never a crash."""
        from . import mcp
        if not mcp.ref_on():
            return
        try:
            made = mcp.seed_ref(conn, home=self.services_home)
            t = made["tools"]
            print(f"the shelf: the reference clock server registered at {mcp.locator_words(mcp.ref_locator())}"
                  f" — tools {', '.join(t['new'] + t['present'] + t['versioned']) or 'none'}", file=sys.stderr, flush=True)
        except Exception as e:                       # noqa: BLE001 — the rig runs on
            print(f"the reference clock could not be registered: {type(e).__name__}: {e}", file=sys.stderr, flush=True)

    def _keeper_beat(self, conn) -> None:
        from . import mcp
        keeper = self.firmware.get("toolkeeper")
        if keeper is None:
            return
        try:
            out = mcp.keeper_beat(conn, keeper=keeper.identity.did)
            bad = [c["name"] for c in out["checked"] if c["ok"] is False]
            if bad or out["proposed"]:
                print(f"the keeper's beat: {len(out['checked'])} servers probed"
                      + (f", UNHEALTHY: {', '.join(bad)}" if bad else "")
                      + (f", proposed retiring: {', '.join(p['name'] for p in out['proposed'])}" if out["proposed"] else ""),
                      file=sys.stderr, flush=True)
        except Exception as e:                       # noqa: BLE001
            print(f"the keeper's beat stumbled: {type(e).__name__}: {e}", file=sys.stderr, flush=True)

    def _seed_shelf(self, conn) -> None:
        """P6.5 sp1: the kernel registers what it was born with — every
        built-in tool, the ground and the Record, the mind the gateway is
        — the same selves every boot (seeds beside the agents'), then
        probes each once so the shelf and the harness read true. A
        refusal is said, never a crash."""
        try:
            made = services.seed(conn, gateway=self.gateway, home=self.services_home)
            for line in made["refused"]:
                print(f"the shelf refused a built-in: {line}", file=sys.stderr, flush=True)
            checked = services.check_all(conn, gateway=self.gateway)
            bad = [c["name"] for c in checked if c["ok"] is False]
            if made["registered"] or made.get("versioned") or bad:
                print(f"the shelf: {len(checked)} services probed"
                      + (f", registered now: {', '.join(made['registered'])}" if made["registered"] else "")
                      + (f", re-pinned (their words changed): {', '.join(made['versioned'])}" if made.get("versioned") else "")
                      + (f", UNHEALTHY: {', '.join(bad)}" if bad else ""), file=sys.stderr, flush=True)
        except Exception as e:                       # noqa: BLE001 — the rig runs on; the harness will say
            print(f"the shelf could not be seeded: {type(e).__name__}: {e}", file=sys.stderr, flush=True)

    def _intent_loop(self):
        """The intent rail (0007, the fifth): the kernel's Infinite Horizon
        Intentions declared at boot — Resiliency first, once per world, a
        stopped one left at rest — then a turn every few seconds: watches
        judged, the newly red observed under every intention that cares,
        the planner asked under the observation, its reply filed as the
        objective to the crew in the intention's session."""
        with psycopg.connect(self.dsn, autocommit=True) as conn:
            for _attempt in range(20):
                try:
                    ground.ensure_all(conn)       # every ground at birth
                    intent.declared(conn, intent.RESILIENCY["words"],
                                    serves=intent.RESILIENCY["serves"], kind="kernel",
                                    by="the kernel", interests=intent.RESILIENCY["interests"],
                                    planner=intent.RESILIENCY["planner"], runner="librarian")
                    break
                except Exception as e:
                    if _attempt == 19:            # the last try says why, never silent
                        print(f"the intent rail could not declare at boot: {type(e).__name__}: {e}",
                              file=sys.stderr, flush=True)
                    time.sleep(0.3)
            while not self._stop.is_set():
                try:
                    intent.turn(conn)
                except Exception:
                    pass
                time.sleep(3)

    def _serve_loop(self, resident):
        with psycopg.connect(self.dsn, autocommit=True) as conn:
            for _attempt in range(20):      # birth retries: a schema race
                try:                        # or slow ground never kills a
                    ground.ensure_all(conn) # resident before it lives —
                    resident.join(conn)     # every ground at birth, then join
                    break
                except PlacementRefused as e:   # P6 sp4: the ground cannot seat
                    print(f"{resident.name} refused at birth — " + "; ".join(e.reasons)
                          + " (recorded; the rig runs without it)", file=sys.stderr, flush=True)
                    return                  # never started; the others serve
                except Exception:
                    time.sleep(0.3)
            if resident.name == mitl.NAME:  # P6 sp3: MITL wears the canon from
                try:                        # birth — acquired through the door,
                    made = mitl.acquire_ontology(conn, resident)   # idempotent
                    if made["acquired"] or made["missing"]:
                        print(f"mitl wears the Orreth ontology v0: {made['acquired']} passages "
                              f"acquired from {made['files']} files"
                              + (f"; missing {made['missing']}" if made["missing"] else ""),
                              file=sys.stderr, flush=True)
                except Exception as e:      # a body that cannot read the canon
                    print(f"mitl could not acquire the ontology: {type(e).__name__}: {e}",
                          file=sys.stderr, flush=True)      # still serves — and says so
            while not self._stop.is_set():
                try:
                    presence.renew(conn, resident.identity.did, resident.name,
                                   resident.kind)         # M2: alive while I serve
                    resident.serve_once(conn, idle_s=1.0, max_commands=50)
                except Exception:
                    pass

    def _sweep_benches(self) -> None:
        """Operator's act at the rig's own start: clear THIS world's
        queues of any prior life's leftovers."""
        import pika as _pika
        from .rails import RABBIT_URL as _RU
        from .resident import serve_queue as _sq
        try:
            rc = _pika.BlockingConnection(_pika.URLParameters(_RU))
            ch = rc.channel()
            for q in [_sq()] + [_sq(r.name) for r in self.residents]:
                ch.queue_declare(q, durable=True)
                ch.queue_purge(q)
            rc.close()
        except Exception:
            pass

    def start(self) -> "BridgeRig":
        self._sweep_benches()
        for t in self._threads:
            t.start()
        return self

    def wait_ready(self, timeout_s: float = 25.0) -> bool:
        """Both listeners hold assignments: the feed AND the dispatcher.
        Submit nothing before this — a fact published pre-assignment is
        only caught by a later catch-up, which the dev rig doesn't run."""
        return (self.feed_ready.wait(timeout_s)
                and self.dispatcher_ready.wait(timeout_s))

    def stop(self) -> None:
        """Stopped WHOLE: the flag, the door, then every thread joined —
        a resident mid-poll or a consumer mid-close outliving stop() by
        a second still holds the benches, and whoever walks next on the
        same benches is raced by a ghost (found live in the suite)."""
        self._stop.set()
        self._httpd.shutdown()
        self._httpd.server_close()
        for t in self._threads:
            t.join(timeout=10)


def main() -> int:
    gw = None
    from . import stable as _stable                      # P6.5 sp3: THE GATEWAY — every mind through LiteLLM
    if _stable.Gateway().ready():
        from .gateway import LiteLLMGateway
        gw = LiteLLMGateway()
        mind = f"every mind through the gateway at {gw.base}"
    else:
        from .gateway import FakeGateway
        gw = FakeGateway(reply="I am the fake mind — the gateway is dark; run scripts/dev.sh up "
                               "and restart me to think for real.")
        mind = f"a fake mind (the gateway at {_stable.Gateway().base} is dark)"
    home = Path(os.environ.get("ORRETH_HOME", Path.home() / ".orreth")) / "agents"
    rig = BridgeRig(gateway=gw, home=home).start()   # the same selves, every life
    print(f"the Bridge is lit: http://127.0.0.1:{rig.port}/  ({mind})")
    print("crew: " + " · ".join(f"{r.name} {r.identity.did}"
                                for r in rig.residents) + f"  (home {home})")
    print("Ctrl+C brings it down whole.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        rig.stop()
        print("\nthe Bridge is dark — stopped whole, nothing left running.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
