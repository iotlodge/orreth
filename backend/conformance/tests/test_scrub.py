# PROVENANCE: Claude Fable 5 (claude-fable-5) — 0070 sp4, the scrub · 2026-09-11
"""The scrub's laws (0070 §3.1): when-words resolve deterministically or
refuse by name — never a guess; the temporal clause finally speaks human;
and beliefs replay by versions-as-time — believed THEN, retracted SINCE,
from the worldlines alone."""
import pytest

from orreth_sim import basket, stacks, whenwords, wiki
from orreth_sim.world import build

NOW = "2026-09-11T12:00:00Z"          # a Friday, fixed — the laws are exact


def test_when_words_resolve_deterministically():
    assert whenwords.parse("what happened yesterday", now=NOW) == \
        ("2026-09-10", "yesterday")
    assert whenwords.parse("as of last tuesday please", now=NOW) == \
        ("2026-09-08", "last tuesday")
    assert whenwords.parse("three days ago", now=NOW)[0] == "2026-09-08"
    assert whenwords.parse("two weeks ago", now=NOW)[0] == "2026-08-28"
    # «last Friday» ON a Friday is a week back, always
    assert whenwords.parse("last friday", now=NOW)[0] == "2026-09-04"
    assert whenwords.parse("this friday", now=NOW)[0] == "2026-09-11"
    assert whenwords.parse("day before yesterday", now=NOW)[0] == "2026-09-09"
    assert whenwords.parse("no time here at all", now=NOW) == (None, None)


def test_ambiguity_is_named_never_guessed():
    assert whenwords.ambiguous("what did we believe recently?") == "recently"
    assert whenwords.ambiguous("a while back we said") == "a while back"
    assert whenwords.parse("recently", now=NOW) == (None, None)
    assert whenwords.ambiguous("last tuesday") is None


def test_the_temporal_clause_speaks_human():
    mode, iso, cleaned = stacks.parse_time(
        "as of last Tuesday what powered the walls?", now=NOW)
    assert (mode, iso) == ("asof", "2026-09-08")
    assert "last Tuesday" not in cleaned and "walls" in cleaned
    mode2, iso2, _ = stacks.parse_time("since yesterday, any drift?", now=NOW)
    assert (mode2, iso2) == ("since", "2026-09-10")
    # the ISO form stays first-class
    mode3, iso3, _ = stacks.parse_time("as of 2026-08-01 what stood?")
    assert (mode3, iso3) == ("asof", "2026-08-01")


def test_beliefs_replay_by_versions_as_time(monkeypatch):
    """Mint a claim on day 1; retract it on day 3. As of day 2 it was
    BELIEVED (and the reply may say «retracted since»); as of day 0 it did
    not exist; as of day 4 it no longer answers. The worldlines alone."""
    w = build()
    ident, kp = w.becky.issue_identity("instance", "u:demo", resident=True)
    n = w.universe
    import pathlib
    import tempfile
    store = pathlib.Path(tempfile.mkdtemp()) / "objects"
    monkeypatch.setattr(wiki, "NOW", lambda: "2026-09-01T10:00:00Z")
    r = basket.import_bytes(n, ident, kp,
                            data=b"Rammed earth walls hold thermal mass.",
                            name="earth.md", origin={"path": "/x/earth.md"},
                            store_root=store)
    claims = wiki.mint_claims(n, ident, kp, r["extraction"])
    assert len(claims) == 1
    monkeypatch.setattr(wiki, "NOW", lambda: "2026-09-03T10:00:00Z")
    out = wiki.cascade(n, ident, kp, r["extraction"])
    assert out["retracted"] == claims
    day0 = wiki.claims_asof(n, "2026-08-31")
    assert day0["held"] == {}                     # not yet believed
    day2 = wiki.claims_asof(n, "2026-09-02")
    assert set(day2["held"]) == set(claims)       # believed THEN
    assert day2["since_retracted"][claims[0]].startswith("2026-09-03")
    day4 = wiki.claims_asof(n, "2026-09-04")
    assert day4["held"] == {}                     # dead by then, honestly
