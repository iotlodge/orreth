# PROVENANCE: Fable 5 (claude-fable-5) — 0047 sp2, the capability bench · 2026-08-07
"""The capability bench (0047 sp2) — does a mind wearing the jacket obey the
laws? Deterministic on stubs; the live-fire twin is examples/mind_livefire.py.

Under bench: a typed thought lands first ask with the craft's version pinned
on the scribe's line; a malformed reply earns ONE re-ask naming the error and
the contract's shape; a twice-failed thought PARKS honestly and raises —
never a guessed value, and the failure is on the record; craft resolves once
per run and rides by reference (law 8); a craft slot the method cannot fill
refuses loudly at call time, not in the model's face; the identity is the
client's and survives the process (rule 1); engines that cannot stand refuse
honestly, naming their gate."""
import pytest

from orreth_agent.craft import ResolvedCraft
from orreth_agent.mind import (Generation, MindEngineUnavailable, MindParked,
                               OrrethMind, generation)

CRAFT_TEXT = ('You are an independent judge. Rubric: ⟦rubric⟧. Reply with '
              'STRICT JSON {"score": 0.00, "why": "..."}.\n\nWORK:\n⟦work⟧')


class StubThink:
    """The governed seam, stubbed: klass and prompt recorded, tokens counted
    the way GovernedThink counts them."""

    def __init__(self, replies):
        self.replies = list(replies)
        self.asked: list[tuple[str, str]] = []
        self.last_tokens = 0
        self.last_calls = 0

    def __call__(self, klass, prompt):
        self.asked.append((klass, prompt))
        self.last_tokens += 100
        self.last_calls += 1
        return self.replies.pop(0)


class StubClient:
    did, scribe_did, scope = "did:key:agent", "did:key:scribe", "u:test"

    def __init__(self):
        self.runs: list[dict] = []
        self.parks: list[tuple[str, str]] = []

    def diary(self, intent, *, cycle, done, tokens=0, model_calls=0,
              score=None, context_hash=None):
        self.runs.append({"intent": intent, "cycle": cycle, "done": done,
                          "tokens": tokens, "model_calls": model_calls,
                          "context_hash": context_hash})
        return True

    def park(self, intent, missing):
        self.parks.append((intent, missing))
        return "sha256:parked"


class Scout(OrrethMind):
    """The bench's mind: one judge method, craft by reference."""

    @generation(klass="medium", craft="assay-judge",
                returns={"score": float, "why": str})
    def judge(self, rubric, work):
        """Judge the work against the rubric."""
        ...


def _mind(replies, *, text=CRAFT_TEXT, fetches=None):
    client, think = StubClient(), StubThink(replies)
    fetches = fetches if fetches is not None else []

    def fetch(name):
        fetches.append(name)
        return ResolvedCraft({"name": name, "ref": "sha256:craft-v3",
                              "version": 3, "text": text})
    return Scout(client, think, craft_fetch=fetch), client, think


def test_a_typed_thought_lands_first_ask_with_the_craft_pinned():
    mind, client, think = _mind(['{"score": 0.8, "why": "held"}'])
    got = mind.judge("cites its records", "the work under test")
    assert got == {"score": 0.8, "why": "held"}
    klass, prompt = think.asked[0]
    assert klass == "medium"                       # the declared class rode
    assert "cites its records" in prompt and "the work under test" in prompt
    [run] = client.runs                            # one scribe line per call
    assert run["done"] and run["cycle"] == 1 and run["model_calls"] == 1
    assert run["context_hash"] == "sha256:craft-v3"  # the words, pinned


def test_the_reask_names_the_error_and_the_shape_then_lands():
    mind, client, think = _mind(["I admire this work greatly.",
                                 '{"score": 0.4, "why": "second dressing"}'])
    got = mind.judge("r", "w")
    assert got["score"] == 0.4 and len(think.asked) == 2
    reask = think.asked[1][1]
    assert "was not valid" in reask and "no JSON object" in reask
    assert '"score": float' in reask               # the contract's shape, named
    [run] = client.runs
    assert run["done"] and run["cycle"] == 2 and run["model_calls"] == 2


def test_twice_failed_parks_honestly_and_never_guesses():
    mind, client, think = _mind(["prose", "still prose"])
    with pytest.raises(MindParked) as e:
        mind.judge("r", "w")
    assert e.value.record == "sha256:parked"       # the failure is on the record
    [(intent, missing)] = client.parks
    assert intent == "mind.judge" and "no JSON object" in missing
    [run] = client.runs
    assert run["done"] is False and run["model_calls"] == 2


def test_the_contract_holds_field_by_field():
    # int serves float; a missing field is named for the re-ask
    mind, _, think = _mind(['{"score": 1, "why": "integer dressed"}'])
    assert mind.judge("r", "w") == {"score": 1.0, "why": "integer dressed"}
    mind, _, think = _mind(['{"score": 0.5}',
                            '{"score": 0.5, "why": "found it"}'])
    got = mind.judge("r", "w")
    assert got["why"] == "found it"
    assert '"why" is missing' in think.asked[1][1]


def test_one_run_one_resolution_law_8():
    fetches: list = []
    mind, _, _ = _mind(['{"score": 0.1, "why": "a"}',
                        '{"score": 0.2, "why": "b"}'], fetches=fetches)
    mind.judge("r", "w1")
    mind.judge("r", "w2")
    assert fetches == ["assay-judge"]              # resolved once, carried


def test_an_unfilled_slot_refuses_loudly_before_any_model():
    mind, _, think = _mind([], text=CRAFT_TEXT + "\n⟦yardstick⟧")
    with pytest.raises(ValueError) as e:
        mind.judge("r", "w")
    assert "yardstick" in str(e.value)
    assert think.asked == []                       # no thought was spent


def test_a_dark_shelf_propagates_the_declared_posture():
    def dark(name):
        raise RuntimeError("the registry is dark and on_dark=refuse")
    client, think = StubClient(), StubThink([])
    mind = Scout(client, think, craft_fetch=dark)
    with pytest.raises(RuntimeError):
        mind.judge("r", "w")
    assert think.asked == []


def test_plain_text_and_callable_contracts():
    class Prose(OrrethMind):
        @generation(klass="low", craft="resident-voice", returns=str)
        def speak(self, name, scope, facts):
            ...

    def fetch(name):
        return ResolvedCraft({"name": name, "ref": "sha256:v1", "version": 1,
                              "text": "You are ⟦name⟧ at ⟦scope⟧.\n⟦facts⟧"})
    mind = Prose(StubClient(), StubThink(["three short sentences"]),
                 craft_fetch=fetch)
    assert mind.speak("vera", "u:demo", "the dial rests") == \
        "three short sentences"


def test_identity_is_the_clients_and_survives_the_process(tmp_path):
    from orreth_agent.client import FieldClient
    a = FieldClient("http://x", "scout-mind", home=tmp_path)
    b = FieldClient("http://x", "scout-mind", home=tmp_path)
    c = FieldClient("http://x", "other-mind", home=tmp_path)
    assert a.did == b.did and a.scribe_did == b.scribe_did   # rule 1
    assert a.did != a.scribe_did                   # author ≠ agent (0005)
    assert c.did != a.did                          # a name is not a self; a seed is


def test_engines_refuse_honestly_naming_their_gate():
    client, think = StubClient(), StubThink([])
    with pytest.raises(MindEngineUnavailable) as e:
        Scout(client, think, engine="nooa")
    assert "lock 1" in str(e.value) or "lock 3" in str(e.value)
    with pytest.raises(MindEngineUnavailable):
        Scout(client, think, engine="martian")
