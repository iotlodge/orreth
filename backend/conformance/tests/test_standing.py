# PROVENANCE: Fable 5 (claude-fable-5) — 0047 sp6, the standing doors · 2026-08-07
"""The standing doors (0047 sp6) — the two senders, under conformance.

Under test: a charter fires on its cadence and never before it; a
never-yet-fired charter is due at once; the declared instance ceiling RESTS
the charter honestly (never a silent continuation); an inactive charter is
mute; the reflex matches only its declared tag and scope, and a condition
the law cannot read never fires; the response wears exactly one of three
shapes, an act-reflex declares its governed request at declaration time, and
an unreadable response refuses loudly."""
import pytest

from orreth_sim import standing


def test_the_charter_owns_its_cadence():
    ch = {"active": True, "every_s": 60, "fired": 0, "max_instances": 3}
    assert standing.charter_due(ch, 1000.0)              # never fired → due now
    ch["last_fired_s"], ch["fired"] = 1000.0, 1
    assert not standing.charter_due(ch, 1030.0)          # mid-cadence: not due
    assert standing.charter_due(ch, 1060.0)              # the beat arrives
    assert not standing.charter_due({**ch, "active": False}, 9999.0)


def test_the_ceiling_rests_the_charter_honestly():
    ch = {"active": True, "every_s": 1, "fired": 3, "max_instances": 3,
          "last_fired_s": 0.0}
    assert not standing.charter_due(ch, 9999.0)          # never past the ceiling
    assert standing.charter_resting(ch)                  # and it SAYS so
    assert not standing.charter_resting({**ch, "fired": 2})


def test_the_reflex_matches_only_its_declared_condition():
    rx = {"when": {"kind": "record-tagged", "tag": "asset", "scope": "u:demo"}}
    assert standing.reflex_matches(rx, {"tags": ["asset"], "scope": "u:demo"})
    assert not standing.reflex_matches(rx, {"tags": ["asset"], "scope": "u:x"})
    assert not standing.reflex_matches(rx, {"tags": ["verdict"], "scope": "u:demo"})
    # scope-free reflex hears the tag anywhere
    wide = {"when": {"kind": "record-tagged", "tag": "asset"}}
    assert standing.reflex_matches(wide, {"tags": ["asset"], "scope": "u:x"})
    # a condition the law cannot read NEVER fires
    assert not standing.reflex_matches({"when": {"kind": "moon-phase"}},
                                       {"tags": ["asset"]})


def test_the_response_wears_exactly_three_shapes():
    obs = standing.reflex_response(
        {"id": "rx1", "then": {"shape": "observe", "note": "seen"}}, "sha256:r")
    assert obs["shape"] == "observe" and obs["of"] == "sha256:r"
    esc = standing.reflex_response(
        {"then": {"shape": "escalate", "text": "a craft was born"}}, "sha256:r")
    assert esc["shape"] == "escalate" and "born" in esc["text"]
    act = standing.reflex_response(
        {"then": {"shape": "act",
                  "request": {"kind": "gather", "text": "study it"}}}, "sha256:r")
    assert act["request"]["kind"] == "gather"
    with pytest.raises(ValueError):                      # unreadable shape
        standing.reflex_response({"then": {"shape": "explode"}}, "x")
    with pytest.raises(ValueError):                      # act without its request
        standing.reflex_response({"then": {"shape": "act"}}, "x")
