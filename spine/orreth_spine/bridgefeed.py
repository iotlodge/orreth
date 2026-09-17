# PROVENANCE: Claude Fable 5 (claude-fable-5) — rearch P1 sp3, the Bridge feed v0 (M6-lite) · 2026-09-16
"""The Bridge feed (canon 0002): the one place the glass connects.

The browser NEVER touches a broker. It opens one SSE stream here and
receives small, pointer-only notices — {rev, kind, ref, message_id, at}
— never bodies, never prompts, never credentials. Authoritative state is
fetched through governed doors; the feed only says "something you can
see has changed."

Recovery is honest: every notice wears a monotone revision, a
reconnecting client sends SSE's own Last-Event-ID, and the feed replays
what the ring still holds — or says `resync` plainly when the client has
been gone longer than the ring remembers, so the glass fetches a fresh
snapshot instead of trusting a gap.
"""
from __future__ import annotations

import json
import os
import queue
import threading
import time
from collections import deque
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from confluent_kafka import Consumer

from . import envelope as ev

KAFKA_BOOTSTRAP = os.environ.get("SPINE_KAFKA", "localhost:9092")
KEEPALIVE_S = 15.0


class Feed:
    """The fan-out heart: a monotone revision, a bounded ring of recent
    notices, and one queue per connected client."""

    def __init__(self, ring: int = 1024):
        self._lock = threading.Lock()
        self._rev = 0
        self._ring: deque = deque(maxlen=ring)
        self._clients: set[queue.Queue] = set()

    def publish(self, kind: str, ref: str, message_id: str) -> dict:
        with self._lock:
            self._rev += 1
            notice = {"rev": self._rev, "kind": kind, "ref": ref,
                      "message_id": message_id, "at": ev.now_iso()}
            self._ring.append(notice)
            clients = list(self._clients)
        for q in clients:
            q.put(notice)
        return notice

    def publish_delta(self, ref: str, text: str) -> None:
        """Ephemeral streaming: a delta goes to CONNECTED clients only —
        never the ring, never a revision, never a broker. The words form
        live in the glass; the durable truth stays the reply behind the
        door."""
        with self._lock:
            clients = list(self._clients)
        n = {"delta": True, "ref": ref, "text": text}
        for q in clients:
            q.put(n)

    def attach(self) -> queue.Queue:
        q: queue.Queue = queue.Queue()
        with self._lock:
            self._clients.add(q)
        return q

    def detach(self, q: queue.Queue) -> None:
        with self._lock:
            self._clients.discard(q)

    def since(self, rev: int) -> list[dict] | None:
        """Notices after `rev` — or None when the gap outlives the ring
        (the caller must resync from an authoritative snapshot)."""
        with self._lock:
            ring = list(self._ring)
            current = self._rev
        if rev >= current:
            return []
        if not ring or ring[0]["rev"] > rev + 1:
            return None
        return [n for n in ring if n["rev"] > rev]

    @property
    def rev(self) -> int:
        with self._lock:
            return self._rev

    @property
    def clients(self) -> int:
        with self._lock:
            return len(self._clients)


def consume_rail(feed: Feed, topics: list[str], group: str,
                 stop: threading.Event, bootstrap: str | None = None,
                 ready: threading.Event | None = None,
                 from_start: bool = False) -> None:
    """The rail-side of the gateway: read committed facts, publish
    pointer-only notices. Position loss here is harmless — revisions are
    gateway-local and the glass fetches truth through doors anyway.
    `ready` fires once the broker has actually assigned partitions (a
    fresh group joins in seconds, not instantly); `from_start` reads the
    topic from its beginning — for tests and replay demos, not the
    production default. The gateway DECLARES its topics before
    subscribing — a topic that exists only after its first fact would
    leave the consumer assignment-less forever."""
    try:
        from confluent_kafka.admin import AdminClient, NewTopic
        admin = AdminClient({"bootstrap.servers": bootstrap or KAFKA_BOOTSTRAP})
        futures = admin.create_topics(
            [NewTopic(t, num_partitions=1, replication_factor=1)
             for t in topics])
        for f in futures.values():
            try:
                f.result(10)
            except Exception:
                pass                          # already exists — fine
    except Exception:
        pass                                  # broker down: poll loop reports
    cons = Consumer({
        "bootstrap.servers": bootstrap or KAFKA_BOOTSTRAP,
        "group.id": group,
        "auto.offset.reset": "earliest" if from_start else "latest",
        "enable.auto.commit": True,
    })
    try:
        cons.subscribe(topics)
        while not stop.is_set():
            msg = cons.poll(0.3)
            if ready is not None and not ready.is_set() and cons.assignment():
                ready.set()
            if msg is None or msg.error():
                continue
            try:
                env = ev.decode(msg.value())
            except Exception:
                continue                      # the feed never carries poison
            feed.publish(env["type"],
                         str((env.get("payload") or {}).get("ref") or ""),
                         env["message_id"])
    finally:
        cons.close()


def _sse_frame(notice: dict) -> bytes:
    return (f"id: {notice['rev']}\ndata: {json.dumps(notice)}\n\n"
            ).encode()


def make_handler(feed: Feed):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_a):           # quiet; the feed is the log
            pass

        def do_GET(self):
            path = self.path.split("?")[0]
            if path == "/health":
                body = json.dumps({"rev": feed.rev,
                                   "clients": feed.clients}).encode()
                self.send_response(200)
                self.send_header("content-type", "application/json")
                self.end_headers()
                self.wfile.write(body)
                return
            if path != "/feed":
                self.send_response(404)
                self.end_headers()
                return
            self.send_response(200)
            self.send_header("content-type", "text/event-stream")
            self.send_header("cache-control", "no-cache")
            self.send_header("access-control-allow-origin", "*")
            self.end_headers()
            q = feed.attach()
            try:
                last = self.headers.get("last-event-id")
                if last is not None:
                    missed = feed.since(int(last))
                    if missed is None:
                        self.wfile.write(
                            b'event: resync\ndata: {"reason": "the gap '
                            b'outlived the ring - fetch a fresh snapshot '
                            b'through the doors"}\n\n')
                        self.wfile.flush()
                    else:
                        for n in missed:
                            self.wfile.write(_sse_frame(n))
                        self.wfile.flush()
                while True:
                    try:
                        n = q.get(timeout=KEEPALIVE_S)
                        if n.get("delta"):
                            self.wfile.write(
                                b"event: delta\ndata: "
                                + json.dumps(n).encode() + b"\n\n")
                        else:
                            self.wfile.write(_sse_frame(n))
                    except queue.Empty:
                        self.wfile.write(b": keepalive\n\n")
                    self.wfile.flush()
            except (BrokenPipeError, ConnectionResetError, OSError):
                pass                          # the client left; that's fine
            finally:
                feed.detach(q)

    return Handler


class BridgeFeed:
    """The whole gateway: HTTP server + rail consumer, started together,
    stopped together. `port=0` picks a free port (tests)."""

    def __init__(self, topics: list[str], *, port: int = 0,
                 group: str | None = None, ring: int = 1024,
                 bootstrap: str | None = None, from_start: bool = False):
        self.feed = Feed(ring=ring)
        self._stop = threading.Event()
        self.ready = threading.Event()
        self._httpd = ThreadingHTTPServer(("127.0.0.1", port),
                                          make_handler(self.feed))
        self.port = self._httpd.server_address[1]
        self._threads = [
            threading.Thread(target=self._httpd.serve_forever, daemon=True),
            threading.Thread(
                target=consume_rail,
                args=(self.feed, topics,
                      group or f"bridgefeed-{self.port}", self._stop),
                kwargs={"bootstrap": bootstrap, "ready": self.ready,
                        "from_start": from_start}, daemon=True),
        ]

    def start(self) -> "BridgeFeed":
        for t in self._threads:
            t.start()
        return self

    def wait_ready(self, timeout_s: float = 20.0) -> bool:
        """True once the rail consumer holds a partition assignment."""
        return self.ready.wait(timeout_s)

    def stop(self) -> None:
        self._stop.set()
        self._httpd.shutdown()
        self._httpd.server_close()
