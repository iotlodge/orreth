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
    cur.execute("SELECT text, person, status, reply, served_by"
                " FROM spine_asks WHERE ask_id = %s", (ask_id,))
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
            "journey": [n for n in notes if n]}


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
                with psycopg.connect(dsn) as conn:
                    ask_id = dispatch.submit_ask(conn, text, person=person)
                return self._json(201, {"id": ask_id})
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
                 dsn: str | None = None, policy=None):
        spine = Path(__file__).resolve().parents[1]
        self.dsn = dsn or PG_DSN
        self._stop = threading.Event()
        self.feed = bridgefeed.Feed()
        self.resident = Resident(
            template or spine / "templates" / "librarian-resident.v0.json",
            gateway=gateway)
        self.resident.load_policy(
            policy or spine / "policy" / "covenant-policy.v1.json")
        from http.server import ThreadingHTTPServer
        self._httpd = ThreadingHTTPServer(
            ("127.0.0.1", port), make_glass_handler(self.feed, self.dsn))
        self.port = self._httpd.server_address[1]
        self.feed_ready = threading.Event()
        self._threads = [
            threading.Thread(target=self._httpd.serve_forever, daemon=True),
            threading.Thread(target=bridgefeed.consume_rail,
                             args=(self.feed, FEED_TOPICS,
                                   f"glass-feed-{self.port}", self._stop),
                             kwargs={"ready": self.feed_ready}, daemon=True),
            threading.Thread(target=self._relay_loop, daemon=True),
            threading.Thread(target=self._dispatch_loop, daemon=True),
            threading.Thread(target=self._serve_loop, daemon=True),
        ]

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
        with psycopg.connect(self.dsn) as conn:
            while not self._stop.is_set():
                try:
                    dispatch.dispatch_once(
                        conn, consumer="glass-dispatcher",
                        group="glass-dispatcher", idle_s=1.0)
                except projector.inbox.GapDetected:
                    pass
                except Exception:
                    pass

    def _serve_loop(self):
        with psycopg.connect(self.dsn) as conn:
            self.resident.join(conn)
            while not self._stop.is_set():
                try:
                    self.resident.serve_once(conn, idle_s=1.0,
                                             max_commands=50)
                except Exception:
                    pass

    def start(self) -> "BridgeRig":
        for t in self._threads:
            t.start()
        return self

    def stop(self) -> None:
        self._stop.set()
        self._httpd.shutdown()
        self._httpd.server_close()


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
    rig = BridgeRig(gateway=gw).start()
    print(f"the Bridge is lit: http://127.0.0.1:{rig.port}/  ({mind})")
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
