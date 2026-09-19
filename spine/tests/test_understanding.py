# PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P5 sp2, Understanding v0 · 2026-09-19
"""MEM-4 changing facts (canon 0003): a memory never overwrites — a new
one under the same key is a sibling that supersedes it, each with a
validity interval, so "true now" and "true then" both answer; and the
Understanding projection v0: full-text, stemmed, ranked, wearing its
kind on the row."""
import json
import secrets
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

import pytest

from orreth_spine import dispatch, envelope as ev, gateway, glass, resident, store

from tests.test_mind import _rails_up  # noqa: E402

SPINE = Path(__file__).resolve().parents[1]
POLICY = SPINE / "policy" / "covenant-policy.v1.json"
rails = pytest.mark.skipif(not _rails_up(), reason="the rails are not up")


def _now():
    return datetime.now(timezone.utc).isoformat()


def test_a_changed_fact_is_a_sibling_and_both_truths_answer(pg, monkeypatch):
    monkeypatch.setenv("SPINE_SCOPE", "u:law-" + secrets.token_hex(3))
    st = store.OrrethStore(pg, by_did="did:orreth:agent:test")
    h60 = st.put("librarian", "temp", "The temperature outside is 60°F.")
    time.sleep(0.05); then = _now(); time.sleep(0.05)
    h70 = st.put("librarian", "temp", "The temperature outside is 70°F.")
    assert st.put("librarian", "temp", "The temperature outside is 70°F.") == h70  # same words: nothing new
    assert st.get("librarian", "temp") == "The temperature outside is 70°F."           # true now
    assert st.get("librarian", "temp", at=then) == "The temperature outside is 60°F."  # true then
    hist = st.history("librarian", "temp")
    assert [v["hash"] for v in hist] == [h60, h70]                                    # never an overwrite
    assert hist[0]["valid_to"] and hist[1]["valid_to"] is None and hist[1]["supersedes"] == h60
    assert all(v["understanding"] == store.UNDERSTANDING for v in hist)
    cur = pg.cursor()
    cur.execute("SELECT body FROM spine_outbox WHERE convert_from(body, 'UTF8') LIKE %s", ("%librarian/temp%",))
    events = [ev.decode(bytes(b)) for (b,) in cur.fetchall()]
    assert any(e["payload"].get("supersedes") == h60 and e["payload"]["hash"] == h70 for e in events)


def test_search_is_stemmed_and_ranked(pg, monkeypatch):
    monkeypatch.setenv("SPINE_SCOPE", "u:law-" + secrets.token_hex(3))
    st = store.OrrethStore(pg, by_did="did:orreth:agent:test")
    st.put("librarian", "hempcrete", "Hempcrete cures for 28 days before it bears load.")
    st.put("librarian", "cat", "The cat sat on the mat, curing nothing.")
    hits = st.search("librarian", "how long does hempcrete take to cure")
    assert hits[0]["key"] == "hempcrete" and hits[0]["rank"] > 0        # stemmed: cure ~ cures; ranked first
    assert st.search("librarian", "the mat")[0]["key"] == "cat"
    assert st.search("librarian", "zebra quantum") == []
    assert st.search("librarian", "the of and") == []                    # stopwords alone: honestly nothing
    partial = st.search("librarian", "hempc")                             # a token the stemmer can't hold:
    assert partial[0]["key"] == "hempcrete" and partial[0]["rank"] == 0.0   # the word-match fallback finds it
    st.put("librarian", "hempcrete", "Hempcrete now cures in 14 days with the new lime.")
    then = _now()
    assert "14 days" in st.search("librarian", "hempcrete cure")[0]["body"]          # now
    assert "14 days" in st.search("librarian", "hempcrete cure", at=then)[0]["body"]


def test_recall_in_a_window_reads_what_was_true_then(pg, monkeypatch):
    """MEM-4 in the chat: an ask wearing a window packs the memories as
    they stood at the window's end — what we knew then, not now."""
    monkeypatch.setenv("SPINE_SCOPE", "u:law-" + secrets.token_hex(3))
    gw = gateway.FakeGateway(reply="noted")
    lib = resident.Resident(SPINE / "templates" / "librarian-resident.v0.json", gateway=gw)
    lib.load_policy(POLICY); lib._serve_conn = pg
    st = store.OrrethStore(pg, by_did=lib.identity.did)
    st.put("librarian", "temp", "The temperature was 60 degrees.")
    time.sleep(0.05); then = _now(); time.sleep(0.05)
    st.put("librarian", "temp", "The temperature is 70 degrees.")
    win = {"from": datetime(2020, 1, 1, tzinfo=timezone.utc).isoformat(), "to": then}
    ask = dispatch.submit_ask(pg, "what was the temperature?", window=win)
    lib._current_ask = ask
    lib._graph.invoke({"text": "what was the temperature?", "reply": "", "steps": [],
                       "notes": [], "hold": None, "read": []})
    prompt = gw.calls[0]["prompt"]
    assert "as of" in prompt and "60 degrees" in prompt and "70 degrees" not in prompt
    ask2 = dispatch.submit_ask(pg, "what is the temperature?")
    lib._current_ask = ask2
    lib._graph.invoke({"text": "what is the temperature?", "reply": "", "steps": [],
                       "notes": [], "hold": None, "read": []})
    assert "70 degrees" in gw.calls[1]["prompt"]


@rails
def test_the_recall_door_serves_then_and_the_lineage_over_http(pg, rig):
    port = rig.port
    with __import__("psycopg").connect(rig.dsn, autocommit=True) as conn:
        st = store.OrrethStore(conn, by_did=rig.resident.identity.did)
        st.put("librarian", "http-fact", "first words")
        time.sleep(0.05); then = _now(); time.sleep(0.05)
        st.put("librarian", "http-fact", "second words")
    def get(q):
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/recall?{q}", timeout=10) as r:
            return json.loads(r.read())
    from urllib.parse import urlencode
    assert get("ref=librarian/http-fact")["memory"]["body"] == "second words"
    assert get(urlencode({"ref": "librarian/http-fact", "at": then}))["memory"]["body"] == "first words"
    hist = get("ref=librarian/http-fact&history=1")["history"]
    assert [v["body"] for v in hist] == ["first words", "second words"] and hist[1]["supersedes"] == hist[0]["hash"]
