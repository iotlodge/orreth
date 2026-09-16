# PROVENANCE: Claude Fable 5 (claude-fable-5) — rearch P1 sp3, the Bridge feed v0 (M6-lite) · 2026-09-16
"""M6-lite's laws: the glass gets pointer-only notices over one SSE
stream; reconnects repair their gap through SSE's own Last-Event-ID;
a gap the ring no longer holds says `resync` honestly; and the notice
arrives fast enough to FEEL soft. Ring/resync laws run pure; the
end-to-end laws need both rails (same skip/require discipline)."""
import http.client
import json
import os
import secrets
import time

import pytest

from orreth_spine import bridgefeed, envelope as ev, outbox, sinks

BOOT = os.environ.get("SPINE_KAFKA", "localhost:9092")


# ---- pure Feed laws (no rails needed) --------------------------------------------

def test_revisions_are_monotone_and_ring_replays_the_gap():
    f = bridgefeed.Feed(ring=10)
    for i in range(5):
        f.publish("k", f"r{i}", f"m{i}")
    assert [n["rev"] for n in f.since(2)] == [3, 4, 5]
    assert f.since(5) == []


def test_gap_beyond_the_ring_demands_resync():
    f = bridgefeed.Feed(ring=2)
    for i in range(6):
        f.publish("k", f"r{i}", f"m{i}")
    assert f.since(1) is None          # rev 2..4 already forgotten — resync
    assert [n["rev"] for n in f.since(4)] == [5, 6]


def test_notices_are_pointer_only():
    f = bridgefeed.Feed()
    n = f.publish("orreth.thing.done.v1", "rec_x", "msg_1")
    assert set(n) == {"rev", "kind", "ref", "message_id", "at"}


# ---- end-to-end over the real rails ----------------------------------------------

def _kafka_up() -> bool:
    try:
        from confluent_kafka.admin import AdminClient
        return bool(AdminClient({"bootstrap.servers": BOOT,
                                 "socket.timeout.ms": 3000}
                                ).list_topics(timeout=3))
    except Exception:
        return False


rails = pytest.mark.skipif(
    not (os.environ.get("SPINE_REQUIRE_KAFKA") or _kafka_up()),
    reason="the events rail is not up — start spine/compose.yaml")


class SSEClient:
    """A minimal human-shaped client: one GET, a stream of events."""

    def __init__(self, port: int, last_event_id: int | None = None):
        self._c = http.client.HTTPConnection("127.0.0.1", port, timeout=15)
        headers = {"accept": "text/event-stream"}
        if last_event_id is not None:
            headers["last-event-id"] = str(last_event_id)
        self._c.request("GET", "/feed", headers=headers)
        self._r = self._c.getresponse()

    def next_event(self, deadline_s: float = 20.0):
        """Returns (event, data|None, id|None) for the next non-keepalive
        frame, or None on deadline."""
        end = time.monotonic() + deadline_s
        event, data, eid = "message", None, None
        while time.monotonic() < end:
            line = self._r.readline().decode().rstrip("\n")
            if line.startswith(":"):
                continue
            if line.startswith("event:"):
                event = line[6:].strip()
            elif line.startswith("data:"):
                data = line[5:].strip()
            elif line.startswith("id:"):
                eid = int(line[3:].strip())
            elif line == "" and data is not None:
                return event, json.loads(data), eid
        return None

    def close(self):
        self._c.close()


def _fact(pg, typ, ref):
    e = ev.make_envelope(kind="event", type=typ, universe_id="u:dev",
                         scope_path="u:dev",
                         payload={"ref": ref, "hash": "sha256:x"})
    outbox.commit_with_outbox(pg, ev.encode(e), e["message_id"])
    assert outbox.drain(pg, sinks.KafkaSink()) >= 1
    return e


@rails
def test_a_committed_fact_reaches_the_glass_softly(pg):
    """The charter's soft notice, end to end: ground → rail → feed →
    the client — pointer-only, and fast enough to feel."""
    outbox.ensure_schema(pg)
    tok = secrets.token_hex(4)
    typ = f"orreth.test-{tok}.done.v1"
    bf = bridgefeed.BridgeFeed([typ], from_start=True).start()
    try:
        assert bf.wait_ready(), "the rail consumer never got its assignment"
        client = SSEClient(bf.port)
        t0 = time.perf_counter()
        fact = _fact(pg, typ, f"rec-{tok}")
        got = client.next_event()
        latency = time.perf_counter() - t0
        assert got is not None, "no notice arrived"
        event, data, eid = got
        assert event == "message" and eid == data["rev"]
        assert data["kind"] == typ and data["ref"] == f"rec-{tok}"
        assert data["message_id"] == fact["message_id"]
        assert set(data) == {"rev", "kind", "ref", "message_id", "at"}
        print(f"\ncommit → glass notice: {latency*1000:.0f} ms")
        assert latency < 5.0                  # SLO bar is 1 s; CI gets slack
        client.close()
    finally:
        bf.stop()


@rails
def test_reconnect_repairs_the_gap_by_last_event_id(pg):
    """The human closes the laptop, facts keep landing, the glass
    reconnects with Last-Event-ID and misses NOTHING."""
    outbox.ensure_schema(pg)
    tok = secrets.token_hex(4)
    typ = f"orreth.test-{tok}.done.v1"
    bf = bridgefeed.BridgeFeed([typ], from_start=True).start()
    try:
        assert bf.wait_ready(), "the rail consumer never got its assignment"
        client = SSEClient(bf.port)
        _fact(pg, typ, "before-sleep")
        _evt = client.next_event()
        assert _evt and _evt[1]["ref"] == "before-sleep"
        last_seen = _evt[2]
        client.close()                        # the laptop lid closes
        _fact(pg, typ, "while-away-1")
        _fact(pg, typ, "while-away-2")
        deadline = time.monotonic() + 15
        while bf.feed.rev < last_seen + 2 and time.monotonic() < deadline:
            time.sleep(0.2)
        back = SSEClient(bf.port, last_event_id=last_seen)
        refs = [back.next_event()[1]["ref"] for _ in range(2)]
        assert refs == ["while-away-1", "while-away-2"]
        back.close()
    finally:
        bf.stop()


@rails
def test_a_gap_beyond_the_ring_says_resync_honestly(pg):
    """Gone longer than the ring remembers → the feed says so plainly
    instead of pretending continuity."""
    outbox.ensure_schema(pg)
    tok = secrets.token_hex(4)
    typ = f"orreth.test-{tok}.done.v1"
    bf = bridgefeed.BridgeFeed([typ], ring=2, from_start=True).start()
    try:
        assert bf.wait_ready(), "the rail consumer never got its assignment"
        for i in range(5):
            _fact(pg, typ, f"r{i}")
        deadline = time.monotonic() + 15
        while bf.feed.rev < 5 and time.monotonic() < deadline:
            time.sleep(0.2)
        back = SSEClient(bf.port, last_event_id=1)
        event, data, _ = back.next_event()
        assert event == "resync" and "snapshot" in data["reason"]
        back.close()
    finally:
        bf.stop()
