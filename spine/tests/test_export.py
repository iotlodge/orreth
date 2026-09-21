# PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P6 sp2, the compliance export · 2026-09-21
"""The compliance export's laws (0005 P6 sp2 · AG-7, JB's testing marker):
a planned request — residents answer, the planner and the grader read
them — exports with its authority chain UNBROKEN end to end on every
row, and the bundle verifies; a truncated chain fails; a bundle never
carries another person's asks; window and marker scopes hold; the CSV
cuts long words and says so; an opt-out session exports no words; the
kernel's own held stop exports hold · proof · reply · stop with the
master on the chain; a signed bundle verifies and a forged one does not."""
import copy
import json
import os
import secrets
import urllib.error
import urllib.request
from pathlib import Path

import pytest

from orreth_spine import dispatch, export, gateway, glass, identity, intent, markers, proof, resident

SPINE = Path(__file__).resolve().parents[1]
POLICY = SPINE / "policy" / "covenant-policy.v1.json"
ME = "did:orreth:person:export-tester"


def _body(template, gw=None):
    r = resident.Resident(SPINE / "templates" / template, gateway=gw)
    r.load_policy(POLICY)
    return r


def _serve(pg, body, ask_id, chain=(ME,)):
    body._serve_conn = pg
    with pg.transaction():
        body._serve_ask(pg.cursor(), ask_id, list(chain))


def _planned_request(pg):
    """AG-7's shape: the echo and the librarian answer in a session, then
    the planner and the grader are applied as includes over both."""
    echo = _body("echo-resident.v0.json")
    lib = _body("librarian-resident.v0.json", gateway.FakeGateway(reply="the librarian's view: shelves"))
    planner = _body("firmware-planner.v0.json", gateway.FakeGateway(reply="1. shelve (librarian) 2. echo it"))
    grader = _body("firmware-grader.v0.json", gateway.FakeGateway(reply="B+ — both answered"))
    for b in (echo, lib, planner, grader):
        b.join(pg)
    ses = glass.open_session(pg, ME)
    [a1] = dispatch.submit_ask(pg, "what is on the shelf?", person=ME, to=["echo"], session=ses)
    _serve(pg, echo, a1)
    [a2] = dispatch.submit_ask(pg, "and what does the librarian say?", person=ME, to=["librarian"], session=ses)
    _serve(pg, lib, a2)
    [a3] = dispatch.submit_ask(pg, "Plan the next steps from what was said here.", person=ME,
                               to=["planner"], session=ses)
    _serve(pg, planner, a3)
    [a4] = dispatch.submit_ask(pg, "Grade the answers in this session.", person=ME,
                               to=["grader"], session=ses)
    _serve(pg, grader, a4)
    return {"session": ses, "asks": [a1, a2, a3, a4],
            "echo": echo, "lib": lib, "planner": planner, "grader": grader}


def test_ag7_the_chain_survives_the_handoff_into_the_export(pg, monkeypatch):
    """AG-7: every row of a planned request wears its chain end to end —
    H on every ask; H → resident on every reply; H → the residents read →
    the firmware on every include — and the bundle verifies."""
    monkeypatch.setenv("SPINE_SCOPE", "u:law-" + secrets.token_hex(3))
    w = _planned_request(pg)
    b = export.build(pg, person=ME, session=w["session"])
    assert b["contract"] == "orreth.compliance/1" and b["scope"] == {"person": ME, "session": w["session"]}
    assert export.verify(b) and b["summary"]["chain_broken"] == 0
    assert b["summary"]["by_kind"] == {"ask": 4, "reply": 2, "include": 2}
    assert [r["at"] for r in b["rows"]] == sorted(r["at"] for r in b["rows"])   # chronological
    for r in b["rows"]:
        assert r["chain_status"] == "intact" and r["authority_chain"][0] == ME
        assert r["proof"] == "L1" and r["marker"]["kind"] in ("objective", "thought")
    asks = {r["ref"]: r for r in b["rows"] if r["kind"] == "ask"}
    assert all(asks[a]["authority_chain"] == [ME] for a in w["asks"])
    assert asks[w["asks"][0]]["words"] == {"ask": "what is on the shelf?"}
    replies = {r["ref"]: r for r in b["rows"] if r["kind"] == "reply"}
    assert replies[w["asks"][0]]["authority_chain"] == [ME, w["echo"].identity.did]
    lib_chain = replies[w["asks"][1]]["authority_chain"]          # the librarian READ the echo's
    assert lib_chain[0] == ME and lib_chain[-1] == w["lib"].identity.did   # result: it names it
    assert replies[w["asks"][1]]["words"]["reply"].startswith("the librarian's view")
    incl = {r["ref"]: r for r in b["rows"] if r["kind"] == "include"}
    read = {w["echo"].identity.did, w["lib"].identity.did}
    for a, fw in ((w["asks"][2], w["planner"]), (w["asks"][3], w["grader"])):
        chain = incl[a]["authority_chain"]
        assert chain[0] == ME and chain[-1] == fw.identity.did and read <= set(chain[1:-1])
        assert len(chain) >= 4 and incl[a]["served_by"] == fw.identity.did
        assert incl[a]["marker"]["kind"] == "thought" and incl[a]["marker"]["parent"]   # the WHY lineage
    assert b["signed_by"] is None and b["signature"] is None                        # honest: no kernel self yet
    assert len(b["hash_chain"]) == len(b["rows"]) and b["root_hash"] == b["hash_chain"][-1]


def test_a_truncated_chain_fails_the_bundle_and_is_counted_when_resealed(pg, monkeypatch):
    """AG-7's teeth: cut one hop off an include's chain and `verify` is
    false; reseal the cut rows and the break is COUNTED, never hidden."""
    monkeypatch.setenv("SPINE_SCOPE", "u:law-" + secrets.token_hex(3))
    w = _planned_request(pg)
    b = export.build(pg, person=ME, session=w["session"])
    cut = copy.deepcopy(b)
    row = next(r for r in cut["rows"] if r["kind"] == "include")
    row["authority_chain"] = row["authority_chain"][:-1]          # the firmware hop, gone
    assert not export.verify(cut)
    resealed = export.seal(cut["rows"], scope=cut["scope"], world=cut["world"])
    assert export.verify(resealed) and resealed["summary"]["chain_broken"] == 1
    assert next(r for r in resealed["rows"] if r["ref"] == row["ref"] and r["kind"] == "include")["chain_status"] == "broken"
    shorter = copy.deepcopy(b); shorter["rows"].pop()             # a truncated LOG fails too
    assert not export.verify(shorter)
    relabeled = copy.deepcopy(b); relabeled["rows"][0]["chain_status"] = "broken"   # a lie about a status fails
    assert not export.verify(relabeled)
    assert export.verify(b)


def test_a_bundle_never_carries_another_persons_asks(pg, monkeypatch):
    monkeypatch.setenv("SPINE_SCOPE", "u:law-" + secrets.token_hex(3))
    other = "did:orreth:person:someone-else"
    echo = _body("echo-resident.v0.json"); echo.join(pg)
    ses = glass.open_session(pg, ME)
    [mine] = dispatch.submit_ask(pg, "my words", person=ME, to=["echo"], session=ses)
    [theirs] = dispatch.submit_ask(pg, "their words", person=other, to=["echo"], session=ses)
    _serve(pg, echo, mine); _serve(pg, echo, theirs, chain=[other])
    b = export.build(pg, person=ME, session=ses)
    assert {r["ref"] for r in b["rows"]} == {mine} and b["scope"]["person"] == ME
    assert "their words" not in json.dumps(b)
    b2 = export.build(pg, person=other, session=ses)
    assert {r["ref"] for r in b2["rows"]} == {theirs} and export.verify(b2)


def test_the_window_and_marker_scopes_and_the_current_session_default(pg, monkeypatch):
    monkeypatch.setenv("SPINE_SCOPE", "u:law-" + secrets.token_hex(3))
    w = _planned_request(pg)
    cur = pg.cursor()
    cur.execute("SELECT min(asked_at) - interval '1 minute', now() + interval '1 minute'"
                " FROM spine_asks WHERE session = %s", (w["session"],))
    lo, hi = cur.fetchone()
    win = export.build(pg, person=ME, window=(lo.isoformat(), hi.isoformat()))
    assert win["scope"]["window"] == {"from": lo.isoformat(), "to": hi.isoformat()}
    assert {r["ref"] for r in win["rows"]} == set(w["asks"]) and export.verify(win)
    empty = export.build(pg, person=ME, window=("2001-01-01T00:00:00Z", "2001-01-02T00:00:00Z"))
    assert empty["rows"] == [] and empty["root_hash"] is None and export.verify(empty)
    # the marker scope: the FIRST objective and everything under it — the
    # echo's ask and reply; the includes hang under the LATEST objective
    cur.execute("SELECT marker FROM spine_asks WHERE ask_id = %s", (w["asks"][0],))
    root = cur.fetchone()[0]
    mk = export.build(pg, person=ME, marker=root)
    assert mk["scope"]["marker"] == root
    assert {r["ref"] for r in mk["rows"]} == {w["asks"][0]} and {r["kind"] for r in mk["rows"]} == {"ask", "reply"}
    assert all(r["marker"]["root"] == root for r in mk["rows"])
    cur.execute("SELECT marker FROM spine_asks WHERE ask_id = %s", (w["asks"][1],))
    under_latest = export.build(pg, person=ME, marker=cur.fetchone()[0])
    assert {r["ref"] for r in under_latest["rows"]} == set(w["asks"][1:])       # librarian + both includes
    dflt = export.build(pg, person=ME)                                          # no scope → the current session
    assert dflt["scope"]["session"] == w["session"] and len(dflt["rows"]) == 8


def test_the_csv_joins_the_chain_and_cuts_long_words_with_a_mark(pg, monkeypatch):
    monkeypatch.setenv("SPINE_SCOPE", "u:law-" + secrets.token_hex(3))
    echo = _body("echo-resident.v0.json"); echo.join(pg)
    ses = glass.open_session(pg, ME)
    long_words = "shelf " * 200                                                  # > 500 chars
    [a] = dispatch.submit_ask(pg, long_words.strip(), person=ME, to=["echo"], session=ses)
    _serve(pg, echo, a)
    b = export.build(pg, person=ME, session=ses)
    lines = export.to_csv(b).splitlines()
    assert lines[0].split(",") == list(export.CSV_COLUMNS)
    assert len(lines) == 1 + len(b["rows"])
    import csv as _csv
    rows = list(_csv.DictReader(lines))
    ask = next(r for r in rows if r["kind"] == "ask")
    assert ask["words_truncated"] == "yes" and ask["words"].endswith("…") and len(ask["words"]) == 501
    reply = next(r for r in rows if r["kind"] == "reply")
    assert reply["authority_chain"] == f"{ME} → {echo.identity.did}" and reply["chain_status"] == "intact"
    assert reply["marker_kind"] == "objective" and reply["marker_root"] == reply["marker_id"]


def test_an_opt_out_session_exports_no_words(pg, monkeypatch):
    monkeypatch.setenv("SPINE_SCOPE", "u:law-" + secrets.token_hex(3))
    echo = _body("echo-resident.v0.json"); echo.join(pg)
    ses = glass.open_session(pg, ME, opt_out=True)
    secret = "the words that stay in the opt-out " + secrets.token_hex(4)
    [a] = dispatch.submit_ask(pg, secret, person=ME, to=["echo"], session=ses)
    _serve(pg, echo, a)
    b = export.build(pg, person=ME, session=ses)
    assert len(b["rows"]) == 2 and all(r["words"] is None and r["words_withheld"] == "opt-out" for r in b["rows"])
    assert secret not in json.dumps(b) and secret not in export.to_csv(b)
    assert b["summary"]["words_withheld"] == 2 and export.verify(b)
    assert all(r["chain_status"] == "intact" for r in b["rows"])               # the chain still shows


def test_the_kernels_held_stop_exports_hold_proof_reply_and_the_stop(pg, monkeypatch):
    """The grave path on the ground (P6 sp1): a kernel intention's stop is
    held for L3-master; the master's yes settles it. The export shows the
    hold (H → the kernel · L3-master), the proof offered (by the master),
    the reply (H → master → the kernel) and the intention's stop."""
    monkeypatch.setenv("SPINE_SCOPE", "u:law-" + secrets.token_hex(3))
    master = "did:orreth:person:master-" + secrets.token_hex(3)
    proof.declare_master(pg, master, by="did:orreth:person:jb")
    markers.seed(pg)
    made = intent.declared(pg, f"keep the {secrets.token_hex(2)} bench green", serves="resiliency",
                           kind="kernel", by="the kernel", interests=[intent.WATCH_RED],
                           planner="planner", runner="librarian")
    ses = glass.open_session(pg, ME)
    with pytest.raises(proof.ProofRequired) as pr:
        intent.stop(pg, made["intention_id"], by=ME)
    ask_id = proof.hold_kernel_act(pg, text=pr.value.what, person=ME, tool="intent.stop",
                                   args={"intention_id": made["intention_id"]}, level="L3-master",
                                   session=ses)
    with pytest.raises(proof.NotConfirmed):                                    # the asker is never their own master
        dispatch.confirm_ask(pg, ask_id, approve=True, person=ME)
    dispatch.confirm_ask(pg, ask_id, approve=True, person=master)
    b = export.build(pg, person=ME, session=ses)
    kinds = [r["kind"] for r in b["rows"]]
    assert kinds == ["hold", "proof", "proof", "reply", "intention.stop"] or \
           kinds == ["hold", "proof", "proof", "intention.stop", "reply"]
    hold = b["rows"][0]
    assert hold["authority_chain"] == [ME, "the kernel"] and hold["served_by"] == "the kernel"
    assert hold["tool"] == "intent.stop" and hold["proof"] == "L3-master" and hold["class"] == "grave"
    p_no, p_yes = [r for r in b["rows"] if r["kind"] == "proof"]
    assert (p_no["ok"], p_no["authority_chain"]) == (False, [ME])
    assert (p_yes["ok"], p_yes["authority_chain"]) == (True, [master])
    reply = next(r for r in b["rows"] if r["kind"] == "reply")
    assert reply["authority_chain"] == [ME, master, "the kernel"] and reply["proof"] == "L3-master"
    assert reply["words"]["reply"].startswith("Done, on")
    stop = next(r for r in b["rows"] if r["kind"] == "intention.stop")
    assert stop["ref"] == made["intention_id"] and stop["authority_chain"] == [ME, master]
    assert stop["proof"] == "L3-master" and stop["words"]["intention"] == made["words"]
    assert stop["marker"] == {"kind": "intention", "id": made["marker"], "parent": None, "root": made["marker"]}
    assert b["summary"]["chain_broken"] == 0 and export.verify(b)
    assert b["summary"]["by_proof"] == {"L3-master": 5}           # every row of a grave act wears it


def test_the_tool_hop_wears_the_chain_end_to_end(pg, monkeypatch):
    """AG-7 cured: a served ask that calls a tool exports a `tool` row whose
    chain reads human → resident → tool:<name>, unbroken, hanging under the
    ask as an action; a body's own mark carries the human first; a held
    act released by the human's yes wears the same chain through the door."""
    monkeypatch.setenv("SPINE_SCOPE", "u:law-" + secrets.token_hex(3))
    gw = gateway.FakeActingGateway(script=[
        ("tool", "acquire", {"key": "hemp", "text": "lime binds hempcrete"}),
        ("tool", "mark", {"kind": "improvement", "note": "lime beats cement"}),
        ("text", "kept and marked: {result}")])
    lib = _body("librarian-resident.v0.json", gw); lib.join(pg)
    ses = glass.open_session(pg, ME)
    [a1] = dispatch.submit_ask(pg, "keep this: lime binds hempcrete", person=ME, to=["librarian"], session=ses)
    _serve(pg, lib, a1)
    held = _body("librarian-resident.v0.json", gateway.FakeActingGateway(script=[
        ("tool", "seal-record", {"key": "hemp"}), ("text", "sealed: {result}")]))
    held.join(pg)
    [a2] = dispatch.submit_ask(pg, "seal the hemp note forever", person=ME, to=["librarian"], session=ses)
    _serve(pg, held, a2)                                                       # holds at L2
    with pg.transaction():
        held._confirm_ask(pg.cursor(), a2, True, [ME], proof="L2")             # the human's yes
    b = export.build(pg, person=ME, session=ses)
    assert export.verify(b) and b["summary"]["chain_broken"] == 0
    assert b["summary"]["by_kind"] == {"ask": 2, "tool": 3, "marker.set": 1, "reply": 2, "hold": 1}
    tools_of = {(r["ref"], r["tool"]): r["authority_chain"] for r in b["rows"] if r["kind"] == "tool"}
    assert tools_of[(a1, "mark")] == [ME, lib.identity.did, "tool:mark"]         # the mark IS a tool call
    cur = pg.cursor(); cur.execute("SELECT marker FROM spine_asks WHERE ask_id = %s", (a1,))
    objective = cur.fetchone()[0]
    acq = next(r for r in b["rows"] if r["kind"] == "tool" and r["ref"] == a1)
    assert acq["authority_chain"] == [ME, lib.identity.did, "tool:acquire"]    # H → resident → tool
    assert acq["served_by"] == "tool:acquire" and acq["tool"] == "acquire" and acq["ok"] is True
    assert acq["marker"] == {"kind": "action", "id": acq["marker"]["id"], "parent": objective, "root": objective}
    mark = next(r for r in b["rows"] if r["kind"] == "marker.set")
    assert mark["authority_chain"] == [ME, lib.identity.did] and mark["served_by"] == lib.identity.did
    assert mark["person"] == ME and mark["marker"]["kind"] == "improvement" and mark["marker"]["parent"] == objective
    seal = next(r for r in b["rows"] if r["kind"] == "tool" and r["ref"] == a2)
    assert seal["authority_chain"] == [ME, held.identity.did, "tool:seal-record"]
    assert seal["proof"] == "L2" and seal["marker"]["kind"] == "action"
    hold = next(r for r in b["rows"] if r["kind"] == "hold")
    hc = hold["authority_chain"]                   # the hold names the librarian it READ (AG-8);
    assert hc[0] == ME and hc[-1] == held.identity.did and lib.identity.did in hc and hold["tool"] == "seal-record"
    # the released act wears the confirm command's chain — the human's word → the
    # body → the tool (the read hops live on the hold's row, the record keeps both)
    reply2 = next(r for r in b["rows"] if r["kind"] == "reply" and r["ref"] == a2)
    assert reply2["authority_chain"] == [ME, held.identity.did] and reply2["proof"] == "L2"
    cur.execute("SELECT authority_chain, ask FROM spine_tool_calls WHERE did = %s ORDER BY call_id",
                (lib.identity.did,))                                           # the row wears it too
    assert [(json.loads(c), k) for c, k in cur.fetchall()] == [
        ([ME, lib.identity.did, "tool:acquire"], a1), ([ME, lib.identity.did, "tool:mark"], a1)]
    cut = copy.deepcopy(b)
    next(r for r in cut["rows"] if r["kind"] == "tool")["authority_chain"] = [ME, lib.identity.did]
    assert not export.verify(cut)                                              # the tool hop cut → fails
    assert export.seal(cut["rows"], scope=cut["scope"], world=cut["world"])["summary"]["chain_broken"] == 1


def test_a_signed_bundle_verifies_and_a_forged_one_does_not(pg, monkeypatch):
    monkeypatch.setenv("SPINE_SCOPE", "u:law-" + secrets.token_hex(3))
    echo = _body("echo-resident.v0.json"); echo.join(pg)
    ses = glass.open_session(pg, ME)
    [a] = dispatch.submit_ask(pg, "sign this", person=ME, to=["echo"], session=ses)
    _serve(pg, echo, a)
    signer = identity.Identity("kernel-test", os.urandom(32))                  # ephemeral: tests only
    b = export.build(pg, person=ME, session=ses, signer=signer)
    assert b["signed_by"] == signer.did and b["signer_key"] == signer.verify_key_hex and export.verify(b)
    forged = copy.deepcopy(b); forged["rows"][0]["words"] = {"ask": "other words"}
    forged["hash_chain"] = export.hash_chain(forged["rows"]); forged["root_hash"] = forged["hash_chain"][-1]
    assert not export.verify(forged)                                           # the root moved under the signature
    stranger = copy.deepcopy(b); stranger["signer_key"] = identity.Identity("x", os.urandom(32)).verify_key_hex
    assert not export.verify(stranger)                                         # the key is not the DID's


# ---- the door (over HTTP, as the glass asks) ------------------------------------------

from tests.test_mind import _rails_up  # noqa: E402

rails = pytest.mark.skipif(
    not (os.environ.get("SPINE_REQUIRE_KAFKA") or _rails_up()),
    reason="the rails are not up — start spine/compose.yaml")


def _get(port, path):
    with urllib.request.urlopen(f"http://127.0.0.1:{port}{path}", timeout=10) as r:
        return r.status, r.headers, r.read()


def _post(port, path, obj):
    req = urllib.request.Request(f"http://127.0.0.1:{port}{path}", data=json.dumps(obj).encode(),
                                 headers={"content-type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        return r.status, json.loads(r.read())


@rails
def test_the_export_door_answers_json_and_csv_and_writes_nothing(rig):
    """GET /export — the current session by default, csv on request — over
    the glass's doors alone (the rig stands on its own ground); afterwards
    the outbox holds not one more row: an export is a READ."""
    import time
    import psycopg
    from tests.test_glass import _wait_status
    from tests.test_resident import _purge_queue
    _purge_queue()
    _s, made = _post(rig.port, "/sessions", {"person": ME})
    ses = made["session_id"]
    _s, filed = _post(rig.port, "/ask", {"text": "through the door", "to": ["echo"],
                                         "session": ses, "person": ME})
    [a] = filed["ids"]
    _wait_status(rig.port, a, ("replied",))
    time.sleep(0.3)                                       # the reply's fact lands with the row
    with psycopg.connect(rig.dsn, autocommit=True) as conn:
        cur = conn.cursor(); cur.execute("SELECT count(*) FROM spine_outbox"); before = cur.fetchone()[0]
        s, h, body = _get(rig.port, f"/export?person={ME}")
        b = json.loads(body)
        assert s == 200 and b["scope"] == {"person": ME, "session": ses} and export.verify(b)
        assert {r["ref"] for r in b["rows"]} == {a} and {r["kind"] for r in b["rows"]} == {"ask", "reply"}
        assert b["summary"]["chain_broken"] == 0
        s, h, body = _get(rig.port, f"/export?person={ME}&session={ses}&format=csv")
        assert s == 200 and h["content-type"].startswith("text/csv") and "attachment" in h["content-disposition"]
        assert body.decode("utf-8").splitlines()[0] == ",".join(export.CSV_COLUMNS)
        with pytest.raises(urllib.error.HTTPError) as e:
            _get(rig.port, f"/export?person={ME}&format=pdf")
        assert e.value.code == 400
        cur.execute("SELECT count(*) FROM spine_outbox"); assert cur.fetchone()[0] == before
