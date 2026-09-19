# PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P5 sp1, MEM-1 total recall · 2026-09-19
"""MEM-1 (canon 0003): acquire words through the door and recall every
one byte-exactly — by ref, by ask, by timeframe; the ask's window is a
lens the resident's recall honors (P6, "between X and Y")."""
import json
import secrets
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from orreth_spine import dispatch, envelope as ev, gateway, glass, resident, store, tools

from tests.test_mind import _rails_up  # noqa: E402

SPINE = Path(__file__).resolve().parents[1]
POLICY = SPINE / "policy" / "covenant-policy.v1.json"
ME = "did:orreth:person:test"
rails = pytest.mark.skipif(not _rails_up(), reason="the rails are not up")
TEXT = "Hempcrete cures for 28 days — «exactly», line one.\nLine two keeps its tabs\tand emoji 🌿."


def _lib(gw=None):
    r = resident.Resident(SPINE / "templates" / "librarian-resident.v0.json", gateway=gw)
    r.load_policy(POLICY)
    return r


def test_acquire_lands_every_word_with_its_event_and_recalls_byte_exact(pg, monkeypatch):
    monkeypatch.setenv("SPINE_SCOPE", "u:law-" + secrets.token_hex(3))
    lib = _lib()
    assert "tools:acquire" in lib.template["capabilities"]
    door = tools.ToolDoor(pg, did=lib.identity.did, capabilities=lib.template["capabilities"],
                          name=lib.name)
    out = door.call("acquire", {"key": "hempcrete", "text": TEXT})
    assert "acquired" in out and ev.content_hash(TEXT)[:16] in out
    st = store.OrrethStore(pg, by_did=lib.identity.did)
    assert st.get("librarian", "hempcrete") == TEXT                    # byte-exact, by ref
    assert glass.recall_view(pg, ref="librarian/hempcrete")["memory"]["body"] == TEXT
    cur = pg.cursor()
    cur.execute("SELECT body FROM spine_outbox WHERE convert_from(body, 'UTF8') LIKE %s",
                ("%librarian/hempcrete%",))
    events = [ev.decode(bytes(b)) for (b,) in cur.fetchall()]
    assert any(e["type"] == store.MEMORY_EVENT and e["payload"]["hash"] == ev.content_hash(TEXT)
               for e in events)                                       # with its event
    now = datetime.now(timezone.utc)
    win = lambda a, b: ((now - timedelta(hours=a)).isoformat(), (now - timedelta(hours=b)).isoformat())
    assert [m["key"] for m in st.within("librarian", *win(1, -1))] == ["hempcrete"]   # by timeframe
    assert st.within("librarian", *win(48, 24)) == []
    assert glass.recall_view(pg, window=win(48, 24))["memories"] == []
    assert glass.recall_view(pg, window=win(1, -1))["memories"][0]["body"] == TEXT


def test_recall_reads_the_asks_window_over_all_the_humans_worldlines(pg, monkeypatch):
    """P6 made real for the mind: an ask that wears "between X and Y" packs
    the human's asks in that window — across sessions, this world — and the
    words acquired in it; nothing outside the window comes along."""
    monkeypatch.setenv("SPINE_SCOPE", "u:law-" + secrets.token_hex(3))
    echo = resident.Resident(SPINE / "templates" / "echo-resident.v0.json"); echo.load_policy(POLICY); echo.join(pg)
    old_tok, new_tok = secrets.token_hex(3), secrets.token_hex(3)
    s1, s2 = glass.open_session(pg, ME), glass.open_session(pg, ME)
    old = dispatch.submit_ask(pg, f"the old ask {old_tok}", person=ME, session=s1)
    new = dispatch.submit_ask(pg, f"the new ask {new_tok}", person=ME, session=s2)
    cur = pg.cursor()
    for aid, days, tok in ((old, 3, old_tok), (new, 0, new_tok)):
        cur.execute("UPDATE spine_asks SET status = 'replied', served_by = %s, reply = %s,"
                    " replied_at = now(), asked_at = now() - make_interval(days => %s)"
                    " WHERE ask_id = %s", (echo.identity.did, f"reply {tok}", days, aid))
    gw = gateway.FakeGateway(reply="noted")
    lib = _lib(gw); lib._serve_conn = pg
    st = store.OrrethStore(pg, by_did=lib.identity.did)
    st.put("librarian", "in-window", "acquired inside the window")
    cur.execute("UPDATE spine_memories SET landed_at = now() - interval '2 days'"
                " WHERE namespace = 'librarian' AND key = 'in-window'")
    now = datetime.now(timezone.utc)
    win = {"from": (now - timedelta(days=4)).isoformat(), "to": (now - timedelta(days=1)).isoformat()}
    ask = dispatch.submit_ask(pg, "what happened between then and then?", person=ME,
                              session=s2, window=win)
    lib._current_ask = ask
    lib._graph.invoke({"text": "what happened between then and then?", "reply": "",
                       "steps": [], "notes": [], "hold": None, "read": []})
    prompt = gw.calls[0]["prompt"]
    notes = [l for l in prompt.splitlines() if l.startswith("- ")]
    assert notes[0].startswith("- THE WINDOW the human asked about")        # first, always
    assert "ARE the record of that window" in gw.calls[0]["system"]
    window_lines = [l for l in prompt.splitlines() if l.startswith("- in the window")]
    assert any(f"the old ask {old_tok}" in l for l in window_lines)             # across sessions
    assert not any(f"the new ask {new_tok}" in l for l in window_lines)         # outside: not in
    assert "acquired inside the window" in prompt                                # words landed in it


@rails
def test_the_recall_door_answers_verbatim_over_http(pg, rig):
    port = rig.port
    def get(q):
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{port}/recall?{q}", timeout=10) as r:
                return r.status, json.loads(r.read())
        except urllib.error.HTTPError as e:
            return e.code, json.loads(e.read())
    text = "keep these words exactly: ĝ 🌿 tab\there"
    with __import__("psycopg").connect(rig.dsn, autocommit=True) as conn:
        store.OrrethStore(conn, by_did=rig.resident.identity.did).put("librarian", "http-law", text)
    s, v = get("ref=librarian/http-law")
    assert s == 200 and v["memory"]["body"] == text
    s, v = get("ref=librarian/no-such")
    assert s == 404 and "one face" in v["error"]
    now = datetime.now(timezone.utc)
    from urllib.parse import urlencode                       # as a browser sends it
    s, v = get(urlencode({"from": (now - timedelta(minutes=5)).isoformat(),
                          "to": (now + timedelta(minutes=1)).isoformat()}))
    assert s == 200 and any(m["ref"] == "librarian/http-law" for m in v["memories"])
