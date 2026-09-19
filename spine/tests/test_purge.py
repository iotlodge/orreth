# PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P5 sp4, MEM-5 quarantine & purge · 2026-09-19
"""MEM-5 (canon 0003 · P11): opt-out words never leak into the 'in'
state — opting in imports nothing; a governed purge reaches every
version, the projection, and every digest that cited it, and leaves a
tombstone with the hashes, never the words."""
import secrets
from pathlib import Path

import pytest

from orreth_spine import digest, dispatch, envelope as ev, gateway, glass, resident, store, tools

SPINE = Path(__file__).resolve().parents[1]
POLICY = SPINE / "policy" / "covenant-policy.v1.json"
ME = "did:orreth:person:test"


def _lib(gw=None):
    r = resident.Resident(SPINE / "templates" / "librarian-resident.v0.json", gateway=gw)
    r.load_policy(POLICY)
    return r


def _serve(pg, lib, ask):
    lib._current_ask = ask
    lib._graph.invoke({"text": "what do you remember?", "reply": "", "steps": [],
                       "notes": [], "hold": None, "read": []})


def test_opt_out_words_never_leak_and_opting_in_imports_nothing(pg, monkeypatch):
    monkeypatch.setenv("SPINE_SCOPE", "u:law-" + secrets.token_hex(3))
    lib = _lib(gateway.FakeGateway(reply="noted")); lib.join(pg); lib._serve_conn = pg
    private = glass.open_session(pg, ME, opt_out=True)
    aid = dispatch.submit_ask(pg, "the private word is HERON", person=ME, session=private)
    assert glass.ask_view(pg, aid)["session"] == private
    pg.cursor().execute("UPDATE spine_asks SET status = 'replied', served_by = %s, reply = 'HERON, kept here',"
                        " replied_at = now() WHERE ask_id = %s", (lib.identity.did, aid))
    store.OrrethStore(pg, by_did=lib.identity.did, state="opt-out").put("librarian", "heron-note", "HERON nests in the reeds")
    assert digest.build(pg, private, by=ME)["new"]
    assert {s["session_id"]: s["state"] for s in glass.sessions_view(pg, ME)}[private] == "opt-out"
    public = glass.open_session(pg, ME)                                   # opting in: a fresh 'in' session
    _serve(pg, lib, dispatch.submit_ask(pg, "what do you remember?", person=ME, session=public))
    prompt = lib.gateway.calls[-1]["prompt"]
    assert "HERON" not in prompt                                           # nothing came along
    assert store.OrrethStore(pg, by_did=lib.identity.did).get("librarian", "heron-note") is None
    assert digest.for_person(pg, ME, exclude=public) == []                 # the opt-out digest stays out
    _serve(pg, lib, dispatch.submit_ask(pg, "what do you remember?", person=ME, session=private))
    assert "HERON" in lib.gateway.calls[-1]["prompt"]                      # inside its state, it remembers


def test_a_governed_purge_reaches_every_version_and_every_digest_and_leaves_a_tombstone(pg, monkeypatch):
    monkeypatch.setenv("SPINE_SCOPE", "u:law-" + secrets.token_hex(3))
    lib = _lib(); lib.join(pg)
    ses = glass.open_session(pg, ME)
    aid = dispatch.submit_ask(pg, "keep this, then forget it", person=ME, session=ses)
    pg.cursor().execute("UPDATE spine_asks SET status = 'replied', served_by = %s, reply = 'kept',"
                        " replied_at = now() WHERE ask_id = %s", (lib.identity.did, aid))
    st = store.OrrethStore(pg, by_did=lib.identity.did)
    h1 = st.put("librarian", "doomed", "the first secret words")
    h2 = st.put("librarian", "doomed", "the second secret words")            # two versions
    made = digest.build(pg, ses, by=ME)
    assert "librarian/doomed" in made["sources"] and "secret" in made["body"]
    door = tools.ToolDoor(pg, did=lib.identity.did, capabilities=lib.template["capabilities"], name="librarian")
    with pytest.raises(tools.ConsequentialHold):
        door.call("purge-memory", {"key": "doomed"})                       # holds for the human's yes
    out = door.call("purge-memory", {"key": "doomed"}, confirmed=True)
    assert "purged 2 version(s)" in out and "1 digest(s) rebuilt" in out
    assert st.get("librarian", "doomed") is None and st.history("librarian", "doomed") == []
    assert st.search("librarian", "secret words") == []                     # the projection went with the rows
    assert glass.recall_view(pg, ref="librarian/doomed") is None
    after = digest.of_session(pg, ses)
    assert "librarian/doomed" not in after["sources"] and "secret" not in after["body"]
    assert after["supersedes"] == made["hash"]                               # a sibling, the citation gone
    cur = pg.cursor()
    cur.execute("SELECT body FROM spine_outbox WHERE convert_from(body, 'UTF8') LIKE %s", ("%librarian/doomed%",))
    events = [ev.decode(bytes(b)) for (b,) in cur.fetchall()]
    stone = [e for e in events if e["type"] == store.PURGE_EVENT]
    assert stone and set(stone[0]["payload"]["hashes"]) == {h1, h2}           # the hashes, never the words
    assert "secret" not in ev.encode(stone[0]).decode()
