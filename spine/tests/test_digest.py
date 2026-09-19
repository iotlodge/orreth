# PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P5 sp3, the Digest (MEM-3) · 2026-09-19
"""MEM-3 digest honesty (canon 0003): every digest cites its sources; an
answer served from a digest opens its verbatim; a rebuilt digest carries
the same substance — byte-identical when nothing changed, a sibling that
supersedes when the episode grew. The pack reads the short version first."""
import json
import secrets
import urllib.request
from pathlib import Path

import pytest

from orreth_spine import digest, dispatch, envelope as ev, gateway, glass, resident, store

from tests.test_mind import _rails_up  # noqa: E402

SPINE = Path(__file__).resolve().parents[1]
POLICY = SPINE / "policy" / "covenant-policy.v1.json"
ME = "did:orreth:person:test"
rails = pytest.mark.skipif(not _rails_up(), reason="the rails are not up")


def _echo(pg):
    e = resident.Resident(SPINE / "templates" / "echo-resident.v0.json")
    e.load_policy(POLICY); e.join(pg); return e


def _exchange(pg, echo, session, text, reply):
    aid = dispatch.submit_ask(pg, text, person=ME, session=session)
    pg.cursor().execute("UPDATE spine_asks SET status = 'replied', served_by = %s, reply = %s,"
                        " replied_at = now() WHERE ask_id = %s", (echo.identity.did, reply, aid))
    return aid


def test_a_digest_cites_every_source_and_rebuilds_the_same_or_as_a_sibling(pg, monkeypatch):
    monkeypatch.setenv("SPINE_SCOPE", "u:law-" + secrets.token_hex(3))
    echo = _echo(pg)
    ses = glass.open_session(pg, ME, title="hempcrete day")
    a1 = _exchange(pg, echo, ses, "How long does hempcrete cure?", "About 28 days, in dry air.")
    a2 = _exchange(pg, echo, ses, "And what binds it?", "Lime — never Portland cement.")
    st = store.OrrethStore(pg, by_did=echo.identity.did)
    st.put("echo", "hempcrete-note", "Hempcrete: hemp hurd + lime binder; cures ~28 days.")
    made = digest.build(pg, ses, by=ME)
    assert made["new"] and set(made["sources"]) == {a1, a2, "echo/hempcrete-note"}  # cites every source
    body = made["body"]
    assert "hempcrete day" in body and "2 asks" in body
    assert "How long does hempcrete cure?" in body and "About 28 days" in body       # the substance
    assert "echo replied" in body and "acquired [echo/hempcrete-note]" in body
    assert digest.build(pg, ses, by=ME)["new"] is False                         # unchanged: byte-identical
    assert digest.of_session(pg, ses)["hash"] == made["hash"] == ev.content_hash(body)
    a3 = _exchange(pg, echo, ses, "A third thing?", "A third answer.")           # the episode grew
    again = digest.build(pg, ses, by=ME)
    assert again["new"] and a3 in again["sources"] and again["hash"] != made["hash"]
    cur = pg.cursor()
    cur.execute("SELECT hash, valid_to IS NULL, supersedes FROM spine_digests WHERE ref = %s"
                " ORDER BY valid_from", (ses,))
    rows = cur.fetchall()
    assert [r[1] for r in rows] == [False, True] and rows[1][2] == made["hash"]  # a sibling, never an overwrite
    cur.execute("SELECT body FROM spine_outbox WHERE convert_from(body, 'UTF8') LIKE %s", (f"%{ses}%",))
    events = [ev.decode(bytes(b)) for (b,) in cur.fetchall()]
    assert sum(e["type"] == digest.DIGEST_EVENT for e in events) == 2          # each landing an event
    assert glass.ask_view(pg, a1)["reply"] == "About 28 days, in dry air."       # the source opens verbatim


def test_the_roll_is_an_episode_boundary_and_the_pack_reads_the_short_version_first(pg, monkeypatch):
    monkeypatch.setenv("SPINE_SCOPE", "u:law-" + secrets.token_hex(3))
    echo = _echo(pg)
    first = glass.open_session(pg, ME, title="first topic")
    _exchange(pg, echo, first, "Remember the word PELICAN.", "PELICAN, held.")
    second = glass.open_session(pg, ME, archive=first)                 # the roll digests the first
    d = digest.of_session(pg, first)
    assert d and "PELICAN" in d["body"] and d["by"] == ME
    assert [s["short_version"] is not None for s in glass.sessions_view(pg, ME)] == [False, True]
    gw = gateway.FakeGateway(reply="noted")
    lib = resident.Resident(SPINE / "templates" / "librarian-resident.v0.json", gateway=gw)
    lib.load_policy(POLICY); lib._serve_conn = pg
    lib._current_ask = dispatch.submit_ask(pg, "what did we talk about before?", person=ME, session=second)
    lib._graph.invoke({"text": "what did we talk about before?", "reply": "", "steps": [],
                       "notes": [], "hold": None, "read": []})
    notes = [l for l in gw.calls[0]["prompt"].splitlines() if l.startswith("- ")]
    assert notes and notes[0].startswith("- the short version of session " + first[4:10])   # FIRST
    assert "PELICAN" in notes[0] and f"digest {d['digest_id'][4:10]}" in notes[0]            # named


@rails
def test_the_digest_doors_over_http(pg, rig):
    port = rig.port
    def post(path, obj):
        req = urllib.request.Request(f"http://127.0.0.1:{port}{path}", data=json.dumps(obj).encode(),
                                     headers={"content-type": "application/json"}, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=15) as r:
                return r.status, json.loads(r.read())
        except urllib.error.HTTPError as e:
            return e.code, json.loads(e.read())
    me = "did:orreth:person:" + secrets.token_hex(3)
    _s, a = post("/sessions", {"person": me, "title": "over http"})
    _s, filed = post("/ask", {"text": "a word for the digest", "to": ["echo"], "session": a["session_id"]})
    import time
    for _ in range(40):                                                    # the echo answers
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/ask/{filed['ids'][0]}", timeout=10) as r:
            if json.loads(r.read())["status"] == "replied":
                break
        time.sleep(0.5)
    s, b = post("/sessions", {"person": me, "archive": a["session_id"]})     # the roll digests it
    assert s == 201
    with urllib.request.urlopen(f"http://127.0.0.1:{port}/digest/{a['session_id']}", timeout=10) as r:
        d = json.loads(r.read())
    assert "a word for the digest" in d["body"] and filed["ids"][0] in d["sources"]
    s, again = post("/digest", {"session": a["session_id"], "person": me})
    assert s == 200 and again["new"] is False                                # rebuilt: the same
    s, _ = post("/digest", {"session": "ses_nope", "person": me})
    assert s == 404
