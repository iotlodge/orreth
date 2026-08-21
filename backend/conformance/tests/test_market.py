# PROVENANCE: Fable 5 (claude-fable-5) — 0058 sp1, the market grows eyes · 2026-08-20
"""The Market (0058 sp1) — a multi-source catalog of minds, under conformance.

Under test: the fold's field precedence (a provider's own API outranks the
serving routers, which outrank the local map — and no source is ever
discarded); access is proven only by a key-scoped adapter; a missing model is
not a dead model (consecutive misses, the missing label, retirement only past
the limit); a source that stumbles is a note, never an outage — the last good
intel stands; the read-only band on the unwired providers; and the search door
speaking the human's units (USD per million prompt tokens)."""
import json

from orreth_sim import market


def _src(entries):
    return lambda: (entries, f"{len(entries)} for the suite")


def _doc(home, sources, force=True):
    return market.refresh(home, sources=sources, force=force)


MIND = "acme/see-far-1"


def test_fold_precedence_and_provenance(tmp_path):
    """The map claims one price; the provider's API another — the API's word
    stands, and both eyes stay on the record."""
    doc = _doc(tmp_path, [
        ("litellm-map", _src({MIND: {"provider": "acme",
                                     "pricing": {"prompt": 1e-6, "completion": 2e-6},
                                     "context_length": 8000,
                                     "capabilities": {"tools": True}}})),
        ("acme-api", _src({MIND: {"provider": "acme",
                                  "pricing": {"prompt": 3e-6},
                                  "access": "available"}})),
    ])
    e = doc["entries"][MIND]
    assert e["pricing"]["prompt"] == 3e-6          # the API's word stands
    assert e["pricing"]["completion"] == 2e-6      # the map's half survives the fold
    assert e["context_length"] == 8000
    assert e["access"] == "available"              # key-scoped proof, nothing else
    assert e["sources"] == ["litellm-map", "acme-api"]  # no eye discarded


def test_missing_is_not_dead(tmp_path):
    """One refresh omitting a mind marks it missing and counts; only past the
    limit does the intel retire."""
    both = [("litellm-map", _src({MIND: {"provider": "acme"}}))]
    gone = [("litellm-map", _src({}))]
    _doc(tmp_path, both)
    for i in range(1, market.MISS_LIMIT + 1):
        doc = _doc(tmp_path, gone)
        assert doc["entries"][MIND]["misses"] == i
        assert doc["entries"][MIND]["missing"] is True
    doc = _doc(tmp_path, gone)                     # past the limit — retired
    assert MIND not in doc["entries"]


def test_return_clears_the_misses(tmp_path):
    seen = [("litellm-map", _src({MIND: {"provider": "acme"}}))]
    _doc(tmp_path, seen)
    _doc(tmp_path, [("litellm-map", _src({}))])
    doc = _doc(tmp_path, seen)                     # the mind returns
    e = doc["entries"][MIND]
    assert e["misses"] == 0 and "missing" not in e


def test_a_stumbling_source_is_a_note_never_an_outage(tmp_path):
    """The adapter throws; the prior intel stands un-aged (its eye did not
    answer, so its absence proves nothing) and the note confesses."""
    _doc(tmp_path, [("acme-api", _src({MIND: {"provider": "acme"}}))])

    def boom():
        raise RuntimeError("the wire is down")
    doc = _doc(tmp_path, [("acme-api", boom)])
    assert doc["sources"]["acme-api"]["ok"] is False
    assert "wire is down" in doc["sources"]["acme-api"]["note"]
    e = doc["entries"][MIND]
    assert e["misses"] == 0 and "missing" not in e  # absence proved nothing
    assert doc["stale"] is True                     # no eye answered — labeled


def test_search_speaks_human_units_and_bands(tmp_path):
    doc = _doc(tmp_path, [("litellm-map", _src({
        "acme/cheap": {"provider": "acme",
                       "pricing": {"prompt": 0.5e-6}, "context_length": 100000,
                       "capabilities": {"vision": True}},
        "acme/dear": {"provider": "acme", "pricing": {"prompt": 20e-6}},
        "bedrock/far-away": {"provider": "bedrock", "read_only": True,
                             "pricing": {"prompt": 1e-6}},
    }))])
    out = market.search(doc, capability="vision", max_price=1.0)
    assert [e["id"] for e in out["entries"]] == ["acme/cheap"]  # $/M prompt
    out = market.search(doc, provider="bedrock")
    assert out["entries"][0]["read_only"] is True   # read, not wired (JB's pin)
    out = market.search(doc, q="acme")
    assert out["total"] == 2 and out["served"] == 2


def test_cache_answers_inside_ttl(tmp_path):
    _doc(tmp_path, [("litellm-map", _src({MIND: {"provider": "acme"}}))])
    calls = {"n": 0}

    def counting():
        calls["n"] += 1
        return {}, "0"
    doc = market.refresh(tmp_path, sources=[("litellm-map", counting)])  # no force
    assert calls["n"] == 0 and MIND in doc["entries"] and doc["stale"] is False


def test_cache_is_json_on_disk(tmp_path):
    _doc(tmp_path, [("litellm-map", _src({MIND: {"provider": "acme"}}))])
    raw = json.loads((tmp_path / "market.json").read_text())
    assert MIND in raw["entries"]
