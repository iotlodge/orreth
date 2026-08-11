# PROVENANCE: Fable 5 (claude-fable-5) — 0050 sp1, the shelf · 2026-08-11
"""The machine's speech (0050 sp1) — sentences as craft, under conformance.

Under test: the PARITY law — every genesis template, rendered with real
facts, reproduces the code literal it replaced byte-for-byte (sp1 moves
where the words live, never what they say); the strict render refuses an
unfilled slot BY NAME and never guesses; fragments carry their own words so
conditional logic stays code while punctuation stays shelf; and the refusal
family is structurally absent from the shelf (0002 §4 — one face, one
guarded object, later)."""
import pytest

from orreth_sim import speech


def test_parity_the_calibration_card():
    got = speech.render(speech.SENTENCES["card-calibration"],
                        pairs=5, mean_gap=0.806, bar=0.4,
                        examples="[sha256:ea097f2…] human 1.0 vs examiner 0.1")
    assert got == ("⚖ the human and the examiner disagree — 5 shared "
                   "work(s), mean gap 0.806 (bar 0.4): "
                   "[sha256:ea097f2…] human 1.0 vs examiner 0.1")
    assert speech.render(speech.SENTENCES["card-calibration-held"]) == \
        "the yardsticks argue — a card, never a lever; the word is yours"


def test_parity_the_verify_pair():
    got = speech.render(speech.SENTENCES["card-verify-blind"],
                        path="deeds/first-deed.json", looks=3,
                        error="The read operation timed out")
    assert got == ("👁 the standing verify cannot SEE /deeds/first-deed.json "
                   "(3 looks — last: The read operation timed out). The "
                   "observer is blind, NOT the deed altered — check the "
                   "wire; the watchman keeps looking.")
    got = speech.render(speech.SENTENCES["card-verify-tamper"],
                        path="deeds/first-deed.json")
    assert got == ("the standing verify found /deeds/first-deed.json altered "
                   "— the walk-back waits for your word (0042 · 0044 sp3)")


def test_parity_the_closure_and_its_fragments():
    base = speech.render(speech.SENTENCES["card-feedback-closure"],
                         outcome="repair-staged")
    ref = speech.render(speech.SENTENCES["card-feedback-closure-ref"],
                        ref="req-559-1786305522")
    why = speech.render(speech.SENTENCES["card-feedback-closure-why"],
                        why="The health report skipped the core requirement")
    assert base + ref + why == (
        "💬 your 👎 was heard — repair-staged → req-559-1786305522…: "
        "The health report skipped the core requirement")
    assert base == "💬 your 👎 was heard — repair-staged"  # fragments optional


def test_parity_reflex_thumb_and_dispatcher():
    got = speech.render(speech.SENTENCES["card-reflex-escalation"],
                        event="a standing duty delivered its outcome",
                        ref="sha256:bf8fc15397f4b3")
    assert got == ("⚡ a standing duty delivered its outcome — "
                   "[sha256:bf8fc15397f4b3…]")
    assert speech.render(speech.SENTENCES["reply-thumb-heard"]) == \
        "heard — on the record"
    got = speech.render(speech.SENTENCES["note-dispatcher"],
                        flavor="hybrid", why="no shape matched — the "
                        "default row serves", choice="sha256:f8a2debdc1")
    assert got == ("⚡ the dispatcher chose «hybrid» — no shape matched — "
                   "the default row serves [choice sha256:f8a2debdc1…]")


def test_an_unfilled_slot_refuses_by_name():
    with pytest.raises(ValueError) as e:
        speech.render(speech.SENTENCES["card-calibration"], pairs=5)
    msg = str(e.value)
    assert "bar" in msg and "examples" in msg and "mean_gap" in msg
    # extra slots are harmless — facts offered but unused never break speech
    assert speech.render("plain words", unused="x") == "plain words"


def test_every_outcome_has_its_spoken_sentence():
    """sp2: the closure card never mumbles machine-speak — OUTCOME_SPOKEN is
    total over the thumb's outcome vocabulary, and the pair fragment (born
    human) renders a stranger-readable line."""
    from orreth_sim import thumb
    assert set(speech.OUTCOME_SPOKEN) == set(thumb.OUTCOMES)
    got = speech.render(speech.SENTENCES["card-calibration-pair"],
                        work="the week's health note", human=1.0, examiner=0.1)
    assert got == ("«the week's health note» — you said 1.0, "
                   "the examiner said 0.1")


def test_the_refusal_family_is_structurally_absent():
    """0002 §4: refusal wears ONE face. No sentence on this shelf may be a
    refusal — it arrives later as a single guarded object, never piecemeal."""
    for name in speech.SENTENCES:
        assert "refus" not in name.lower()
    assert not any("cannot be served" in t for t in speech.SENTENCES.values())
