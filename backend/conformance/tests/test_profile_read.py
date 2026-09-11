# PROVENANCE: Claude Fable 5 (claude-fable-5) — 0070 sp2, the profile read · 2026-09-11
"""The profile-read laws (0070 §3.2): the privacy floor holds (no profile
record ever enters a projection), the slice speaks provenance-labeled, a
withdrawn claim stops speaking mid-thread, and preferences are typed —
sovereign, latest-wins, never settable by an inference."""
import pytest

from orreth_sim import canon, profile, stacks
from orreth_sim.world import build


@pytest.fixture()
def ground():
    w = build()
    ident, kp = w.becky.issue_identity("instance", "u:demo", resident=True)
    return {"w": w, "n": w.universe, "me": ident, "kp": kp}


def _claim(g, text, by="human", evidence=None, prefers=None):
    rec = profile.make_claim(g["me"], g["kp"], "u:demo", text,
                             asserted_by=by, inferred_from=evidence,
                             prefers=prefers)
    return g["n"].write(rec)


def test_the_privacy_floor_holds_in_every_projection(ground):
    """The suite law verbatim: no profile in any projection — the one gate
    (derived_text) returns None, and the registry's own word says why."""
    g = ground
    rid = _claim(g, "I toast with cocoa, never spirits")
    rec = g["n"].records[rid]
    assert canon.retrievable(g["n"], rec) is False       # the registry's word
    assert stacks.derived_text(g["n"], rid, rec, set()) is None  # the one gate


def _live_claims(g):
    import json

    from orreth_sim import crypto
    bodies = {r: json.loads(crypto._b64d(g["n"].records[r]["body"]).decode())
              for r in g["n"].records
              if "profile" in (g["n"].records[r].get("tags") or [])}
    dead = profile.withdrawn_refs(bodies)
    return [(r, b["profile"]) for r, b in bodies.items()
            if "claim" in (b.get("profile") or {}) and r not in dead]


def test_the_slice_is_provenance_labeled(ground):
    g = ground
    _claim(g, "I am relocating to Colorado")
    ev = _claim(g, "a note to infer from")
    _claim(g, "asks about wall materials often", by="librarian", evidence=ev)
    _claim(g, "worries repeat about the reading glasses", by="mirror",
           evidence=ev)
    s = profile.slice_text(_live_claims(g))
    assert "you told me: I am relocating to Colorado" in s
    assert "I observed: asks about wall materials" in s
    assert "the mirror noticed: worries repeat" in s


def test_a_withdrawn_claim_stops_speaking_mid_thread(ground):
    g = ground
    rid = _claim(g, "my favorite color is teal")
    assert "teal" in profile.slice_text(_live_claims(g))
    g["n"].write(profile.make_withdrawal(g["me"], g["kp"], "u:demo", rid))
    assert "teal" not in profile.slice_text(_live_claims(g))  # silent, mid-thread


def test_preferences_are_typed_sovereign_and_latest_wins(ground):
    g = ground
    assert profile.parse_prefs("I prefer answers in Spanish") == \
        {"language": "spanish"}
    assert profile.parse_prefs("keep replies brief please") == \
        {"verbosity": "brief"}
    assert profile.parse_prefs("I like hempcrete walls") == {}
    c1 = _claim(g, "I prefer answers in Spanish",
                prefers={"language": "spanish"})
    c2 = _claim(g, "answer me in French now", prefers={"language": "french"})
    claims = [(c1, {"asserted_by": "human", "prefers": {"language": "spanish"}}),
              (c2, {"asserted_by": "human", "prefers": {"language": "french"}})]
    assert profile.live_prefs(claims) == {"language": "french"}  # latest wins
    # an inference may NEVER set a preference — sovereignty
    with pytest.raises(ValueError):
        profile.make_claim(g["me"], g["kp"], "u:demo", "seems to like German",
                           asserted_by="librarian", inferred_from=c1,
                           prefers={"language": "german"})
