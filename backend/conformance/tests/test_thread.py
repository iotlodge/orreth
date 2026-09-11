# PROVENANCE: Claude Fable 5 (claude-fable-5) — 0070 sp1, the thread · 2026-09-10
"""The conversation worldline's laws (0070 §3.1): a thread rebuilds from
records ALONE, turn N cites turn N−1, the head is a first-class record,
and the truncation caps are the human's dials — never constants."""
import json

from orreth_sim import crypto, dials, parlor
from orreth_sim.world import build


def _mk(w):
    ident, kp = w.becky.issue_identity("instance", "u:demo", resident=True)
    return ident, kp


def test_the_head_is_a_first_class_record():
    w = build()
    ident, kp = _mk(w)
    head = parlor.make_thread_head(ident, kp, "u:demo", "librarian")
    w.universe.write(head)
    assert "parlor-thread" in head["tags"]
    b = json.loads(crypto._b64d(head["body"]).decode())
    assert b["parlor_thread"]["resident"] == "librarian"


def test_caps_are_the_callers_dials_and_the_thread_rides_the_body():
    b = parlor.audience_body("ada", "q" * 999, "a" * 9999,
                             thread="sha256:head", ask_cap=150, reply_cap=300)
    assert len(b["asked"]) == 150 and len(b["reply"]) == 300
    assert b["thread"] == "sha256:head"
    b2 = parlor.audience_prior(b, "sha256:prev")
    assert b2["prior"] == "sha256:prev"
    for d in ("thread-ask-chars", "thread-reply-chars", "thread-turns"):
        assert d in dials.DIALS_V1


def _turn(w, ident, kp, head, prior, asked, reply):
    from orreth_sim.node import make_memory
    body = parlor.audience_prior(
        parlor.audience_body("librarian", asked, reply, thread=head), prior)
    rec = make_memory(ident, kp, "u:demo", body, kind="episodic",
                      tags=["parlor", "librarian"])
    rec["derived_from"] = [x for x in (head, prior) if x]
    return w.universe.write(rec)


def test_a_thread_rebuilds_from_records_alone_in_chain_order():
    """The suite law verbatim: rebuild from records; turn N cites N−1."""
    w = build()
    ident, kp = _mk(w)
    head = parlor.make_thread_head(ident, kp, "u:demo", "librarian")
    w.universe.write(head)
    t1 = _turn(w, ident, kp, head["id"], "", "first ask", "first answer")
    t2 = _turn(w, ident, kp, head["id"], t1, "second ask", "second answer")
    t3 = _turn(w, ident, kp, head["id"], t2, "third ask", "third answer")
    # a stranger's turn on ANOTHER thread never leaks in
    other = parlor.make_thread_head(ident, kp, "u:demo", "ada")
    w.universe.write(other)
    _turn(w, ident, kp, other["id"], "", "elsewhere", "elsewhere")
    turns = parlor.thread_turns(w.universe, head["id"])
    assert [t["asked"] for t in turns] == ["first ask", "second ask",
                                           "third ask"]
    assert turns[1]["prior"] == t1 and turns[2]["prior"] == t2
    # the lineage law holds on the records themselves
    assert w.universe.records[t2]["derived_from"] == [head["id"], t1]
    assert w.universe.records[t3]["derived_from"] == [head["id"], t2]


def test_a_stray_turn_rides_the_clock_honestly():
    w = build()
    ident, kp = _mk(w)
    head = parlor.make_thread_head(ident, kp, "u:demo", "librarian")
    w.universe.write(head)
    t1 = _turn(w, ident, kp, head["id"], "", "chained ask", "chained answer")
    _turn(w, ident, kp, head["id"], "sha256:" + "ab" * 32,
          "stray ask", "stray answer")
    turns = parlor.thread_turns(w.universe, head["id"])
    assert [t["asked"] for t in turns] == ["chained ask", "stray ask"]
