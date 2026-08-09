# PROVENANCE: Fable 5 (claude-fable-5) — 0048 sp1, the record · 2026-08-09
"""The Thumb (0048 sp1) — the human answers back, under conformance.

Under test: the quiet word (👍) is loud on the record — a signed human
verdict on the SAME shelf as vera's, scored 1.0, costing nothing, and the
standings hear it; a thumb judges ONE record by hash and only a seated,
signing human may land one; the loud word (👎 + text) births a feedback
record quoting the human verbatim, deriving from what it marks and from its
own verdict, while the marked record never changes; a wordless no is a
verdict alone; feedback is a request and RESOLVES — a sibling names the
outcome, a consequence outcome names what it spawned, declined and parked
owe their why, and the unanswered-words inbox empties only on a real
resolution, never silently."""
import copy

import pytest

from orreth_sim import thumb, vera as vera_mod
from orreth_sim.node import make_memory
from orreth_sim.world import build


@pytest.fixture()
def world():
    return build()


def _reply(world, node):
    """A resident's reply on the shelf — the thing the human judges."""
    seat, kp = world.beckys[node.scope].issue_identity("instance", node.scope)
    rec = make_memory({"did": seat["did"], "scope": node.scope}, kp, node.scope,
                      {"exchange": {"reply": "the librarian's answer, voiced"}},
                      kind="episodic", tags=["parlor", "exchange"])
    node.write(rec)
    return rec["id"]


def _human(world):
    seat, kp = world.becky.issue_identity("instance", "u:demo")
    return seat, kp


def test_the_quiet_word_is_loud_on_the_record(world):
    """👍 fades from the glass but lands as a signed human verdict — same
    shelf, same shape (0043 §6), score 1.0, zero cost — and the standings
    count it beside the judges'."""
    node = world.field_prod
    rid = _reply(world, node)
    human, kp = _human(world)
    verdict, fb = thumb.make_thumb(human, kp, node.scope, of=rid, up=True)
    assert fb is None                                    # the quiet word is alone
    a = thumb._body(verdict)["assay"]
    assert a["score"] == 1.0 and a["judge_floor"] == "human"
    assert a["cost"] == {"tokens": 0} and a["why"] == thumb.UP_WORD
    assert verdict["derived_from"] == [rid]              # ONE record, by hash
    node.write(verdict)
    s = vera_mod.standings(node)[node.scope]
    assert s["humans"] == 1 and s["mean"] == 1.0


def test_no_anonymous_thumbs_and_one_record_only(world):
    human, kp = _human(world)
    with pytest.raises(ValueError):                      # judging nothing
        thumb.make_thumb(human, kp, "u:demo", of="", up=True)
    with pytest.raises(ValueError):                      # no seat, no thumb
        thumb.make_thumb({}, kp, "u:demo", of="sha256:x", up=True)


def test_the_loud_word_births_feedback_and_never_mutates(world):
    """👎 + text: the verdict lands scored 0.0 wearing the human's words, and
    the feedback record quotes them VERBATIM, deriving from the judged record
    and its own verdict — while the marked record never changes (0024)."""
    node = world.field_prod
    rid = _reply(world, node)
    before = copy.deepcopy(node.records[rid])
    human, kp = _human(world)
    said = "the answer ignored the deadline I set"
    verdict, fb = thumb.make_thumb(human, kp, node.scope, of=rid, up=False,
                                   text=said)
    assert thumb._body(verdict)["assay"]["score"] == 0.0
    f = thumb._body(fb)["feedback"]
    assert f["quoted"] == said and f["state"] == "open" and f["of"] == rid
    assert fb["derived_from"] == [rid, verdict["id"]]
    assert "feedback" in fb["tags"] and "thumb" in fb["tags"]
    assert node.records[rid] == before                   # marked, never touched


def test_a_wordless_no_is_a_verdict_alone(world):
    """An empty dialog leaves nothing to address: the verdict lands with the
    default word, and no feedback record is born."""
    human, kp = _human(world)
    verdict, fb = thumb.make_thumb(human, kp, "u:demo", of="sha256:r",
                                   up=False, text="  ")
    assert fb is None
    assert thumb._body(verdict)["assay"]["why"] == thumb.DOWN_WORD


def test_feedback_resolves_and_the_inbox_empties(world):
    """Feedback is a request, and a request resolves: the open-feedback inbox
    holds the unanswered word until a resolution sibling names the outcome —
    then, and only then, it empties."""
    node = world.field_prod
    rid = _reply(world, node)
    human, kp = _human(world)
    _, fb = thumb.make_thumb(human, kp, node.scope, of=rid, up=False,
                             text="it doesn't know our floor's record classes")
    node.write(fb)
    inbox = thumb.open_feedback(node)
    assert [row["id"] for row in inbox] == [fb["id"]]
    res = thumb.resolve_feedback(human, kp, node.scope, fb,
                                 outcome="commissioned", ref="req-901")
    b = thumb._body(res)["feedback"]
    assert b["outcome"] == "commissioned" and b["ref"] == "req-901"
    assert b["of"] == rid and res["derived_from"] == [fb["id"]]
    node.write(res)
    assert thumb.open_feedback(node) == []               # answered, not vanished


def test_the_route_contract_never_guesses():
    """sp3: the classify contract parses only a real route — prose refuses,
    an invented route refuses, and a good word types cleanly (trimmed,
    case-folded) with its why and target intact."""
    got = thumb.route_contract(
        ' {"route": " Gap ", "why": "the skill is missing", '
        '"target": "skill-translate-to-spanish"}')
    assert got == {"route": "gap", "why": "the skill is missing",
                   "target": "skill-translate-to-spanish"}
    with pytest.raises(ValueError):
        thumb.route_contract("I think this is probably a craft problem")
    with pytest.raises(ValueError):
        thumb.route_contract('{"route": "vibes", "why": "?", "target": ""}')
    with pytest.raises(ValueError):
        thumb.route_contract('{"why": "no route named"}')


def test_every_route_lands_an_honest_outcome(world):
    """sp3: the route map is total over ROUTES; every landing word is in the
    vocabulary AND must name what it spawned (no ref, no claim) — including
    the craft route's deliberately modest "evidenced" (0031 §4: feedback is
    never an auto-trigger, so "proposed" would overclaim)."""
    assert set(thumb.OUTCOME_FOR) == set(thumb.ROUTES)
    for word in thumb.OUTCOME_FOR.values():
        assert word in thumb.OUTCOMES and word in thumb._NEEDS_REF
    assert thumb.OUTCOME_FOR["craft"] == "evidenced"
    human, kp = _human(world)
    _, fb = thumb.make_thumb(human, kp, "u:demo", of="sha256:r", up=False,
                             text="the voice answered in the wrong shape")
    with pytest.raises(ValueError):                      # a landing names its ref
        thumb.resolve_feedback(human, kp, "u:demo", fb, outcome="evidenced")
    res = thumb.resolve_feedback(human, kp, "u:demo", fb,
                                 outcome="repair-staged", ref="req-7")
    assert thumb._body(res)["feedback"]["outcome"] == "repair-staged"


def test_the_wire_twin_row_resolves_too(world):
    """sp3: the worker sweeps DECODED rows off the wire — a {id, of} row
    resolves through the same law; a rowless dict still refuses."""
    human, kp = _human(world)
    res = thumb.resolve_feedback(human, kp, "u:demo",
                                 {"id": "sha256:fb", "of": "sha256:judged"},
                                 outcome="commissioned", ref="req-9")
    b = thumb._body(res)["feedback"]
    assert b["of"] == "sha256:judged" and res["derived_from"] == ["sha256:fb"]
    with pytest.raises(ValueError):
        thumb.resolve_feedback(human, kp, "u:demo", {"id": "x"},
                               outcome="commissioned", ref="req-9")


def test_resolution_refuses_dishonesty(world):
    """No silent discard: an unknown outcome refuses; a consequence outcome
    without what it spawned refuses; declined and parked without their why
    refuse; and a non-feedback record cannot be 'resolved' at all."""
    node = world.field_prod
    rid = _reply(world, node)
    human, kp = _human(world)
    _, fb = thumb.make_thumb(human, kp, node.scope, of=rid, up=False,
                             text="wrong resident answered")
    with pytest.raises(ValueError):
        thumb.resolve_feedback(human, kp, node.scope, fb, outcome="ignored")
    with pytest.raises(ValueError):                      # spawned what, exactly?
        thumb.resolve_feedback(human, kp, node.scope, fb, outcome="adopted")
    with pytest.raises(ValueError):                      # the human is owed a why
        thumb.resolve_feedback(human, kp, node.scope, fb, outcome="declined")
    with pytest.raises(ValueError):
        thumb.resolve_feedback(human, kp, node.scope, fb, outcome="parked")
    not_fb = node.records[rid]
    with pytest.raises(ValueError):
        thumb.resolve_feedback(human, kp, node.scope, not_fb, outcome="declined",
                               why="x")
