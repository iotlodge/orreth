# PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp6, the bodies' seam · 2026-09-24
"""THE SDK-SIDE BODY (canon 0004 · 0008 · P7 sp6): a body stands as ITS OWN
PROCESS — `python -m orreth_spine.body` — joins this world, keeps its lease,
serves an ask from its bench, runs the kernel's harness command through its
own graph and records the run under the kernel's run id, streams its words
to the kernel's door, and stops WHOLE on SIGINT (exit 0; the lease lapses);
a body without a policy never joins (a terminal exit the kernel never
restarts); the crew is one manifest both spines read."""
import json
import os
import secrets
import signal
import subprocess
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import psycopg
import pytest

from orreth_spine import body, dispatch, envelope as ev, harness
from orreth_spine.rails import PG_DSN
from orreth_spine.resident import SERVE_KEY  # noqa: F401 — the bench's law lives in resident

SPINE = Path(__file__).resolve().parents[1]
ECHO = SPINE / "templates" / "echo-resident.v0.json"
LIBRARIAN = SPINE / "templates" / "librarian-resident.v0.json"


def _rabbit_up() -> bool:
    try:
        import pika
        pika.BlockingConnection(pika.URLParameters(
            os.environ.get("SPINE_RABBIT", "amqp://orreth:orreth-dev@localhost:5672/%2F"))).close()
        return True
    except Exception:
        return False


rails = pytest.mark.skipif(not (os.environ.get("SPINE_REQUIRE_KAFKA") or _rabbit_up()),
                           reason="the rails are not up — start spine/compose.yaml")


class Spawned:
    """One body as a process, its stderr read on a thread (the kernel's view)."""

    def __init__(self, template, *args, env=None):
        e = dict(os.environ, SPINE_BODY_EPHEMERAL="1", PYTHONUNBUFFERED="1", **(env or {}))
        self.p = subprocess.Popen([sys.executable, "-m", "orreth_spine.body", "--template", str(template), *args],
                                  cwd=SPINE, env=e, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        self.lines: list[str] = []
        self._t = threading.Thread(target=self._read, daemon=True)
        self._t.start()

    def _read(self):
        for line in self.p.stderr:
            self.lines.append(line.rstrip("\n"))

    def wait_words(self, needle: str, timeout_s: float = 60.0) -> str:
        end = time.monotonic() + timeout_s
        while time.monotonic() < end:
            for line in list(self.lines):
                if needle in line:
                    return line
            if self.p.poll() is not None:
                break
            time.sleep(0.1)
        raise AssertionError(f"{needle!r} never appeared; exit={self.p.poll()}; said: {self.lines}")

    def stop(self, timeout_s: float = 20.0) -> int:
        if self.p.poll() is None:
            self.p.send_signal(signal.SIGINT)
        try:
            return self.p.wait(timeout_s)
        except subprocess.TimeoutExpired:
            self.p.kill()
            raise AssertionError(f"the body did not stop whole in {timeout_s}s; said: {self.lines}")


def _public():
    return psycopg.connect(PG_DSN, autocommit=True)


def _lease(conn, name: str):
    cur = conn.cursor()
    cur.execute("SELECT until > now(), renewed_at FROM spine_leases WHERE name = %s AND scope = %s", (name, ev.scope()))
    return cur.fetchone()


def _serve_command(ask_id: str, target: str) -> dict:
    """The dispatcher's law by hand: the serve command for a filed ask, to the body's own bench."""
    return ev.make_envelope(kind="command", type="orreth.resident.serve.v1", universe_id=ev.scope(),
                            scope_path=ev.scope(), payload={"ref": ask_id, "hash": "sha256:-", "target": target},
                            correlation_id=ask_id, authority_chain=["did:orreth:person:test"])


def _poll(conn, sql, args, pred, timeout_s=45.0):
    end = time.monotonic() + timeout_s
    cur = conn.cursor()
    while time.monotonic() < end:
        cur.execute(sql, args)
        row = cur.fetchone()
        if row and pred(row):
            return row
        time.sleep(0.2)
    raise AssertionError(f"never: {sql} {args}")


# ---- the crew is one manifest ----------------------------------------------------------------

def test_the_crew_is_one_manifest():
    seats = body.crew()
    names = [s["template"].name for s in seats]
    assert names[0].startswith("librarian") and names[1].startswith("echo")
    assert sum(1 for s in seats if s["binding"]) == 2                    # crew · monitor bindings
    assert all(s["template"].exists() and (s["binding"] is None or s["binding"].exists()) for s in seats)
    with pytest.raises(ValueError, match="not a crew manifest"):
        body.crew_seats({"format": "x"})
    with pytest.raises(ValueError, match="at least one seat"):
        body.crew_seats({"format": body.CREW_FORMAT, "seats": []})


def test_the_park_law_and_the_backoff():
    now = "2026-09-24T18:00:00+00:00"
    assert body.backoff_s(0) == 0.0 and body.backoff_s(1) == 1.0 and body.backoff_s(3) == 4.0 and body.backoff_s(9) == 30.0
    r = body.park_rule(["2026-09-24T17:59:00Z", "2026-09-24T17:58:30Z", "2026-09-24T17:57:00Z"], now)
    assert r == {"parked": True, "deaths": 3, "wait_s": None}
    r = body.park_rule(["2026-09-24T17:50:00Z", "2026-09-24T17:59:00Z"], now)
    assert r == {"parked": False, "deaths": 1, "wait_s": 1.0}
    words = body.parked_words("librarian", 3, 300, "KeyError: 'mind'")
    assert "died 3 times in 5 minutes" in words and "restart the librarian body" in words and "Nothing is deleted" in words
    f = body.parked_fact("echo", None, 3, 60, "x" * 700)
    assert f["type"] == body.PARKED and f["authority_chain"] == [body.KERNEL] and len(f["payload"]["last_words"]) == 600


# ---- the process ---------------------------------------------------------------------------------

@rails
def test_a_body_stands_as_its_own_process_and_stops_whole():
    b = Spawned(ECHO)
    try:
        line = b.wait_words("echo is alive")
        assert "did:orreth:agent:" in line and "life" in line
        with _public() as conn:
            _poll(conn, "SELECT until > now() FROM spine_leases WHERE name = 'echo' AND scope = %s", (ev.scope(),),
                  lambda r: r[0] is True)                               # M2: alive while it serves
            ids = dispatch.submit_ask(conn, "echo, the walk's word is HERON", to=["echo"])
            aid = ids[0]
            dispatch.publish_command(_serve_command(aid, "echo"))
            row = _poll(conn, "SELECT status, reply FROM spine_asks WHERE ask_id = %s", (aid,),
                        lambda r: r[0] == "replied")
            assert "HERON" in row[1]                                    # the full-reply law, from a process
            # the kernel's harness command over the SAME bench: the run lands under the kernel's id
            rid = "run_" + secrets.token_hex(5)
            cases = [{"ask": "say the word PELICAN", "expect": ["PELICAN"]}, {"ask": "say nothing of GULLS", "expect": ["ALBATROSS"]}]
            dispatch.publish_command(harness.command_for(rid, "echo", cases))
            run = _poll(conn, "SELECT passed, failed, template, details FROM spine_harness_runs WHERE run_id = %s", (rid,),
                        lambda r: True)
            assert (run[0], run[1], run[2]) == (1, 1, "echo")
            details = json.loads(run[3])
            assert details[0]["ok"] is True and details[1]["ok"] is False
            cur = conn.cursor()
            cur.execute("SELECT count(*) FROM spine_outbox WHERE convert_from(body, 'UTF8') LIKE %s", (f"%{rid}%",))
            assert cur.fetchone()[0] >= 1                                # the failing run is a fact on the rail
            # the same run asked twice is nothing new (the second guard behind the inbox's)
            dispatch.publish_command(harness.command_for(rid, "echo", cases))
            time.sleep(2.0)
            cur.execute("SELECT count(*) FROM spine_harness_runs WHERE run_id = %s", (rid,))
            assert cur.fetchone()[0] == 1
            # stopped whole on SIGINT: exit 0, the lease left to lapse (never deleted)
            assert b.stop() == body.EXIT_STOPPED
            assert any("stopped whole" in ln for ln in b.lines)
            assert _lease(conn, "echo") is not None
    finally:
        if b.p.poll() is None:
            b.p.kill()


@rails
def test_a_body_streams_its_words_to_the_kernels_door():
    got: list[dict] = []

    class H(BaseHTTPRequestHandler):
        def do_POST(self):
            n = int(self.headers.get("content-length") or 0)
            got.append(json.loads(self.rfile.read(n) or b"{}"))
            self.send_response(204); self.end_headers()

        def log_message(self, *a):                                     # quiet
            pass

    srv = ThreadingHTTPServer(("127.0.0.1", 0), H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    door = f"http://127.0.0.1:{srv.server_address[1]}"
    b = Spawned(LIBRARIAN, env={"SPINE_KERNEL_DOOR": door, "SPINE_GATEWAY": "http://127.0.0.1:1"})   # the gateway dark: the fake mind
    try:
        line = b.wait_words("librarian is alive")
        assert "fake mind" in line and f"words to {door}" in line
        with _public() as conn:
            ids = dispatch.submit_ask(conn, "librarian, in one word, who are you?", to=["librarian"])
            dispatch.publish_command(_serve_command(ids[0], "librarian"))
            _poll(conn, "SELECT status FROM spine_asks WHERE ask_id = %s", (ids[0],), lambda r: r[0] == "replied", 90.0)
        end = time.monotonic() + 5.0
        while time.monotonic() < end and not any(d.get("ref") == ids[0] for d in got):
            time.sleep(0.1)
        mine = [d for d in got if d.get("ref") == ids[0]]
        assert mine, f"no words reached the door: {got[:3]}"
        assert "fake mind" in "".join(d["text"] for d in mine)          # the words as they formed, coalesced
        assert b.stop() == body.EXIT_STOPPED
    finally:
        srv.shutdown(); srv.server_close()
        if b.p.poll() is None:
            b.p.kill()


@rails
def test_no_policy_no_join_the_exit_is_terminal():
    b = Spawned(ECHO, "--policy", str(SPINE / "policy" / "no-such-policy.json"))
    rc = b.p.wait(60)
    assert rc == body.EXIT_NO_POLICY
    assert any("wears no covenant policy" in ln for ln in b.lines)
