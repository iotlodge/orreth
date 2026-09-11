# PROVENANCE: Claude Fable 5 (claude-fable-5) — 0070 sp3, the personas · 2026-09-11
"""The persona laws (0070 §3.3): the honesty floor is tighten-only, the
gate refuses shapeless voices, every genesis passes its own gate, and the
worn text is what a model actually reads."""
import pytest

from orreth_sim import persona


def test_the_honesty_floor_rides_every_composed_persona():
    base = persona.GENESIS_UNIVERSE["honesty"]
    # a resident with no honesty of its own inherits the base verbatim
    c1 = persona.compose(persona.GENESIS_UNIVERSE, {"disposition": "dry"})
    assert c1["honesty"] == base
    # a resident TRYING to replace honesty only ADDS after the base
    c2 = persona.compose(persona.GENESIS_UNIVERSE,
                         {"honesty": "and cites twice when unsure"})
    assert c2["honesty"].startswith(base)
    assert "cites twice" in c2["honesty"]
    # even an empty universe input falls to the genesis floor
    c3 = persona.compose({}, {"disposition": "x"})
    assert c3["honesty"] == base


def test_the_gate_refuses_shapeless_voices_and_lands_canonical():
    flaw, _ = persona.gate_check("persona-ada", {"mood": "sassy"})
    assert flaw and "unknown persona field" in flaw
    flaw2, _ = persona.gate_check("persona-ada", {"disposition": 42})
    assert flaw2 and "plain sentence" in flaw2
    flaw3, clean = persona.gate_check(
        "persona-ada", {"disposition": "  an old-west wrangler  ",
                        "voice_note": "x" * 999})
    assert flaw3 is None
    assert clean["disposition"] == "an old-west wrangler"
    assert len(clean["voice_note"]) == 400        # honest length, canonical


def test_every_genesis_passes_its_own_gate():
    for who, prof in persona.GENESIS.items():
        flaw, _ = persona.gate_check(f"persona-{who}", prof)
        assert flaw is None, f"{who}: {flaw}"
    flaw, _ = persona.gate_check(persona.UNIVERSE_NAME,
                                 persona.GENESIS_UNIVERSE)
    assert flaw is None


def test_the_worn_text_is_what_a_model_reads():
    t = persona.worn_text(persona.compose(persona.GENESIS_UNIVERSE,
                                          persona.GENESIS["ada"]))
    assert "stable-keeper" in t
    assert "grounded ONLY in the facts given" in t   # the floor, verbatim
    assert "wrangler speaks of" in t                  # the voice note rides
    # an absent field never renders as an empty clause
    bare = persona.worn_text({"disposition": "calm"})
    assert "Your register: ." not in bare
