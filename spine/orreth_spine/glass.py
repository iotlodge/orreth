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
import threading
import time
from pathlib import Path

import psycopg

from . import bridgefeed, dispatch, envelope as ev, outbox, projector, sinks
from .rails import PG_DSN
from .resident import ASK_RECEIVED, CONFIRM_NEEDED, JOURNEY, REPLY, Resident

GLASS_DIR = Path(__file__).resolve().parents[1] / "glass"
FEED_TOPICS = [ASK_RECEIVED, JOURNEY, REPLY, CONFIRM_NEEDED]


def ask_view(conn, ask_id: str) -> dict | None:
    """The Questions door: the ask row plus its journey notes, read from
    the ground (the outbox is the dev log; notes ride the events)."""
    cur = conn.cursor()
    # a glass serves ONLY its own world's ground: another world's ask is
    # "no such ask" here — the refusal wears one face (covenant rule 4)
    cur.execute("SELECT text, person, status, reply, served_by, target,"
                " scope, asked_at, replied_at"
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


def residents_view(conn) -> list[dict]:
    """The chat's right edge: who lives here — name, self, lives."""
    cur = conn.cursor()
    cur.execute(
        "SELECT DISTINCT ON (name) name, did, life, joined_at"
        " FROM spine_joins WHERE scope = %s ORDER BY name, join_id DESC",
        (ev.scope(),))
    return [{"name": r[0], "did": r[1], "lives": r[2],
             "joined_at": r[3].isoformat()} for r in cur.fetchall()]


def make_glass_handler(feed: bridgefeed.Feed, dsn: str):
    Base = bridgefeed.make_handler(feed)

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
                with psycopg.connect(dsn) as conn:
                    out = dispatch.submit_ask(conn, text, person=person,
                                              to=to)
                if isinstance(out, list):
                    return self._json(201, {"ids": out})
                return self._json(201, {"id": out})
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
        for r in self.residents:
            r.on_delta = self.feed.publish_delta
        from http.server import ThreadingHTTPServer
        self._httpd = ThreadingHTTPServer(
            ("127.0.0.1", port), make_glass_handler(self.feed, self.dsn))
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
        ] + [threading.Thread(target=self._serve_loop, args=(r,),
                              daemon=True) for r in self.residents]

    def _relay_loop(self):
        sink = sinks.KafkaSink()
        with psycopg.connect(self.dsn) as conn:
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
        with psycopg.connect(self.dsn) as conn:          # a wedged ghost
            while not self._stop.is_set():               # dies with its rig
                try:
                    dispatch.run_dispatcher(
                        conn, consumer="glass-dispatcher", group=gid,
                        stop=self._stop, ready=self.dispatcher_ready,
                        offset="earliest")  # no produce/assign race:
                    # replay is cheap (skips) and re-serves refuse
                except Exception:
                    time.sleep(0.5)

    def _serve_loop(self, resident):
        with psycopg.connect(self.dsn) as conn:
            for _attempt in range(20):      # birth retries: a schema race
                try:                        # or slow ground never kills a
                    resident.join(conn)     # resident before it lives
                    break
                except Exception:
                    time.sleep(0.3)
            while not self._stop.is_set():
                try:
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
