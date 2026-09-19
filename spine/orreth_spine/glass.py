# PROVENANCE: Claude Fable 5 (claude-fable-5) — rearch P3 sp1, the glass exists · 2026-09-16
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
import threading
import time
from pathlib import Path

import psycopg

from . import bridgefeed, dispatch, envelope as ev, harness, monitor, outbox
from . import presence, projector, scheduler, sinks
from .rails import PG_DSN
from .resident import ASK_RECEIVED, CONFIRM_NEEDED, JOURNEY, REPLY, Resident

GLASS_DIR = Path(__file__).resolve().parents[1] / "glass"
FEED_TOPICS = [ASK_RECEIVED, JOURNEY, REPLY, CONFIRM_NEEDED,
               harness.HARNESS_FAILED]   # a failing run escalates to the chat


def ask_view(conn, ask_id: str) -> dict | None:
    """The Questions door: the ask row plus its journey notes, read from
    the ground (the outbox is the dev log; notes ride the events)."""
    cur = conn.cursor()
    # a glass serves ONLY its own world's ground: another world's ask is
    # "no such ask" here — the refusal wears one face (covenant rule 4)
    cur.execute("SELECT text, person, status, reply, served_by, target,"
                " scope, asked_at, replied_at, time_window, session"
                " FROM spine_asks WHERE ask_id = %s AND scope = %s",
                (ask_id, ev.scope()))
    row = cur.fetchone()
    if row is None:
        return None
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
    return {"ask_id": ask_id, "text": row[0], "person": row[1],
            "status": row[2], "reply": row[3], "served_by": row[4],
            "target": row[5],       # who the ask was routed to: a targeted
            "scope": row[6],        # command reaches only its target
            "asked_at": row[7].isoformat(),
            "replied_at": row[8].isoformat() if row[8] else None,
            "window": json.loads(row[9]) if row[9] else None,  # P6
            "session": row[10],                                 # P20
            "journey": [n for n in notes if n]}


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


def crew_view(conn) -> list[dict]:
    """The Crew workspace's door: one card per body in this world —
    who it is, what it wears, what it declared, and BOTH SIDES (canon
    0004): side A, the asks it served; side B, the duties it runs. The
    kernel-required duties are listed and immutable; human- and role-
    scheduled ones arrive with the scheduler (AG-4's CRUD half)."""
    cur = conn.cursor()
    cur.execute(
        "SELECT DISTINCT ON (name) name, kind, did, life, joined_at,"
        " policy_version, template_hash, capabilities FROM spine_joins"
        " WHERE scope = %s ORDER BY name, join_id DESC", (ev.scope(),))
    alive = {b["did"]: b["alive"] for b in presence.roster(conn)}
    cards = []
    for name, kind, did, life, joined, pv, th, caps in cur.fetchall():
        cur.execute("SELECT count(*), max(replied_at) FROM spine_asks"
                    " WHERE served_by = %s AND scope = %s AND status <> 'received'",
                    (did, ev.scope()))
        n, last = cur.fetchone()
        cards.append({
            "name": name, "kind": kind, "did": did, "lives": life,
            "joined_at": joined.isoformat(), "policy_version": pv,
            "alive": alive.get(did),        # M2: a fresh lease, or dormant
            "template": th[:12], "capabilities": json.loads(caps or "[]"),
            "side_a": {"asks_served": int(n),
                       "last_served": last.isoformat() if last else None},
            "side_b": {"kernel": [{"duty": d, "editable": False} for d in KERNEL_DUTIES],
                       "human": [], "role": []}})
    return cards


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


def open_session(conn, person: str, title: str | None = None) -> str:
    """Roll (P20): a fresh worldline for this human in this world. The
    previous session is not touched — archived means 'not active', never
    'gone' (every word stays in the Record)."""
    from .resident import ensure_schema
    ensure_schema(conn)
    sid = "ses_" + secrets.token_hex(6)
    with conn.transaction():
        conn.cursor().execute(
            "INSERT INTO spine_sessions (session_id, person, scope, title)"
            " VALUES (%s, %s, %s, %s)", (sid, person, ev.scope(), title))
    return sid


def sessions_view(conn, person: str, limit: int = 30) -> list[dict]:
    """List (P20): this human's worldlines in this world, newest first —
    each with its span, how many asks it holds, and its last words."""
    cur = conn.cursor()
    cur.execute(
        "SELECT s.session_id, s.title, s.opened_at,"
        " count(a.ask_id), max(a.asked_at),"
        " (SELECT text FROM spine_asks WHERE session = s.session_id"
        "  ORDER BY asked_at DESC LIMIT 1)"
        " FROM spine_sessions s LEFT JOIN spine_asks a"
        " ON a.session = s.session_id"
        " WHERE s.person = %s AND s.scope = %s"
        " GROUP BY s.session_id ORDER BY s.opened_at DESC LIMIT %s",
        (person, ev.scope(), limit))
    return [{"session_id": r[0], "title": r[1], "opened_at": r[2].isoformat(),
             "asks": int(r[3]), "last_at": r[4].isoformat() if r[4] else None,
             "last_words": (r[5] or "")[:140]} for r in cur.fetchall()]


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
        "SELECT DISTINCT ON (name) name, did, life, joined_at, kind"
        " FROM spine_joins WHERE scope = %s ORDER BY name, join_id DESC",
        (ev.scope(),))
    return [{"name": r[0], "did": r[1], "lives": r[2],
             "joined_at": r[3].isoformat(), "kind": r[4]}
            for r in cur.fetchall()]


def make_glass_handler(feed: bridgefeed.Feed, dsn: str, bodies: dict | None = None):
    Base = bridgefeed.make_handler(feed)
    bodies = bodies or {}            # the rig's bodies by name (the harness door)

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
                with psycopg.connect(dsn) as conn:
                    view = ask_view(conn, path.split("/ask/", 1)[1])
                if view is None:
                    return self._json(404, {"error": "no such ask"})
                return self._json(200, view)
            if path == "/asks":
                with psycopg.connect(dsn) as conn:
                    return self._json(200, {"asks": asks_view(conn)})
            if path == "/residents":
                with psycopg.connect(dsn) as conn:
                    return self._json(200,
                                      {"residents": residents_view(conn)})
            if path == "/crew":
                with psycopg.connect(dsn) as conn:
                    return self._json(200, {"crew": crew_view(conn)})
            if path == "/monitor":
                with psycopg.connect(dsn) as conn:
                    return self._json(200, monitor.snapshot(conn))
            if path.startswith("/schedules/"):           # the card's side B
                with psycopg.connect(dsn) as conn:
                    return self._json(200, scheduler.for_runner(
                        conn, path.split("/schedules/", 1)[1]))
            if path == "/recall":
                from urllib.parse import parse_qs
                qs = {k: v[0] for k, v in parse_qs(self.path.split("?", 1)[1]).items()} \
                    if "?" in self.path else {}
                try:
                    with psycopg.connect(dsn) as conn:
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
                with psycopg.connect(dsn) as conn:
                    return self._json(200, {"sessions": sessions_view(conn, person)})
            if path.startswith("/session/"):
                with psycopg.connect(dsn) as conn:
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
                with psycopg.connect(dsn) as conn:
                    out = dispatch.submit_ask(conn, text, person=person,
                                              to=to, window=window,
                                              session=session)
                if isinstance(out, list):
                    return self._json(201, {"ids": out})
                return self._json(201, {"id": out})
            if path == "/schedules":                  # a human schedule lands
                runner = str(p.get("runner") or "")
                text = str(p.get("text") or "").strip()
                every = int(p.get("every_s") or 0)
                if not (runner and text and every >= 5):
                    return self._json(400, {"error": "a schedule is {runner, text,"
                                                     " every_s >= 5}"})
                person = str(p.get("person") or "did:orreth:person:jb")
                with psycopg.connect(dsn) as conn:
                    sid = scheduler.add(conn, runner, "human", text, every, person)
                return self._json(201, {"schedule_id": sid})
            if path == "/schedules/rest":             # the human's stop
                person = str(p.get("person") or "did:orreth:person:jb")
                try:
                    with psycopg.connect(dsn) as conn:
                        scheduler.rest(conn, str(p.get("schedule_id") or ""), person)
                except scheduler.KernelRequired as e:
                    return self._json(403, {"error": str(e)})
                except KeyError:
                    return self._json(404, {"error": "no such schedule"})
                return self._json(202, {"rested": str(p.get("schedule_id"))})
            if path == "/harness/run":                # on demand (the
                name = str(p.get("template") or "librarian")   # scheduled
                body = bodies.get(name)                        # run waits
                if body is None:                               # for the
                    return self._json(404, {"error": "no such body"})  # scheduler)
                with psycopg.connect(dsn) as conn:
                    return self._json(200, harness.run(conn, body))
            if path == "/sessions":                   # roll a fresh one
                person = str(p.get("person") or "did:orreth:person:jb")
                with psycopg.connect(dsn) as conn:
                    sid = open_session(conn, person,
                                       title=str(p.get("title") or "") or None)
                return self._json(201, {"session_id": sid})
            if path == "/confirm":
                ask_id = str(p.get("ask_id") or "")
                approve = bool(p.get("approve", False))   # absent = cancel
                with psycopg.connect(dsn) as conn:
                    dispatch.confirm_ask(conn, ask_id, approve=approve,
                                         person=str(p.get("person")
                                                    or "did:orreth:person:jb"))
                return self._json(202, {"id": ask_id, "approve": approve})
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
        # the includes (0004's third kind): planner · critic · grader —
        # firmware bodies, same laws, no persona, called by the human as
        # includes over the session's results
        self.firmware: dict[str, Resident] = {}
        for fn in ("planner", "critic", "grader"):
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
                self.feed, self.dsn, {r.name: r for r in self.residents}))
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
            outbox.ensure_schema(conn)
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
                    for r in self.residents:      # AG-6's scheduled run:
                        if harness.golden(r.name): # every mind with a golden set
                            scheduler.declared(conn, r.name, "kernel",
                                               "run the harness against my golden set",
                                               1800, "the kernel")
                    break
                except Exception:
                    time.sleep(0.3)
            while not self._stop.is_set():
                try:
                    scheduler.tick(conn, bodies)
                except Exception:
                    pass
                time.sleep(5)

    def _serve_loop(self, resident):
        with psycopg.connect(self.dsn, autocommit=True) as conn:
            for _attempt in range(20):      # birth retries: a schema race
                try:                        # or slow ground never kills a
                    resident.join(conn)     # resident before it lives
                    break
                except Exception:
                    time.sleep(0.3)
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
    if os.environ.get("ANTHROPIC_API_KEY"):
        from .gateway import AnthropicGateway
        gw = AnthropicGateway()
        mind = "the librarian, thinking for real"
    else:
        from .gateway import FakeGateway
        gw = FakeGateway(reply="I am the fake mind — set ANTHROPIC_API_KEY "
                               "and restart me to think for real.")
        mind = "a fake mind (no key found)"
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
