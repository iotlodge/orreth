# PROVENANCE: Claude Fable 5 (claude-fable-5) — 0071 sp5, the ask-cache's suite · 2026-09-08
"""An answer serves again only for the same words, same row, same floor, same
guardrails — and only while its exchange record still stands."""
from orreth_sim import askcache

ENV = {"reply": "the answer", "variant": "rerank"}


def test_same_words_fold_to_one_key():
    a = askcache.key("f:prod", "What  is rammed earth?", "auto", "pre-0068")
    b = askcache.key("f:prod", "what is rammed EARTH?", "auto", "pre-0068")
    assert a == b, "case and whitespace are not different questions"


def test_different_words_variant_floor_or_guardrails_never_share():
    base = askcache.key("f:prod", "what is x?", "auto", "pre-0068")
    assert askcache.key("f:prod", "what is y?", "auto", "pre-0068") != base
    assert askcache.key("f:prod", "what is x?", "graph", "pre-0068") != base
    assert askcache.key("f:eco", "what is x?", "auto", "pre-0068") != base
    assert askcache.key("f:prod", "what is x?", "auto", "v2") != base, \
        "a changed guardrail set must revalidate — old answers never ride new law"


def test_fresh_hit_serves_and_counts():
    book = {}
    askcache.put(book, "k", ENV, "rec-1", 100.0)
    e = askcache.get(book, "k", 150.0, ttl_s=300)
    assert e is not None and e["envelope"] == ENV and e["ref"] == "rec-1"
    assert e["hits"] == 1


def test_stale_evicts_on_sight():
    book = {}
    askcache.put(book, "k", ENV, "rec-1", 100.0)
    assert askcache.get(book, "k", 401.0, ttl_s=300) is None
    assert "k" not in book


def test_ttl_zero_is_the_closed_cache():
    book = {}
    askcache.put(book, "k", ENV, "rec-1", 100.0)
    assert askcache.get(book, "k", 100.0, ttl_s=0) is None


def test_no_ref_no_replay():
    book = {}
    askcache.put(book, "k", ENV, "", 100.0)
    assert "k" not in book, "an answer with no record behind it must not replay"


def test_purge_reach_kills_every_leaning_entry():
    book = {}
    askcache.put(book, "k1", ENV, "rec-dead", 100.0)
    askcache.put(book, "k2", ENV, "rec-dead", 100.0)
    askcache.put(book, "k3", ENV, "rec-live", 100.0)
    assert askcache.evict_ref(book, "rec-dead") == 2
    assert "k3" in book and "k1" not in book and "k2" not in book


def test_sweep_forgets_stale_only():
    book = {}
    askcache.put(book, "old", ENV, "r1", 100.0)
    askcache.put(book, "new", ENV, "r2", 350.0)
    assert askcache.sweep(book, 401.0, ttl_s=300) == 1
    assert "new" in book and "old" not in book
