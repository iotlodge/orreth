# PROVENANCE: Claude Fable 5 (claude-fable-5) — 0065 sp3, the graph law's suite · 2026-09-09
"""Every edge carries its witness, the walk never leaves the authorized set,
and the purge forgets what only the dead record knew."""
from orreth_sim import graphlaw, rivals

POL = {"chunk_chars": 280, "overlap_chars": 40}
LAW = graphlaw.law_hash(POL)


def _rows(text, doc):
    spans = [(0, len(text))]
    return graphlaw.extract(text, spans, "document", doc, 1.0)


def test_one_term_law_for_rebuild_and_sweep():
    assert rivals._terms is graphlaw.terms, \
        "one definition — the two graphs can never disagree"
    assert graphlaw.terms("The Walls breathe with the seasons!") == [
        "walls", "breathe", "seasons"]


def test_extraction_is_deterministic_and_witnessed():
    n1, e1 = _rows("rammed earth walls breathe with the seasons", "d1")
    n2, e2 = _rows("rammed earth walls breathe with the seasons", "d1")
    assert (n1, e1) == (n2, e2)
    assert e1 and all(ed["span"] and ed["hash"] and ed["doc"] == "d1"
                      for ed in e1), "every edge names its witness"


def test_edges_bind_within_one_span_only():
    text = "alpha beside beta." + " filler words here. " * 30 + "alpha near gamma."
    spans = [(0, 18), (len(text) - 17, len(text))]
    _, edges = graphlaw.extract(text, spans, "document", "d", 1.0)
    pairs = {(e["a"], e["b"]) for e in edges}
    assert ("alpha", "beta") in pairs and ("alpha", "gamma") in pairs
    assert ("beta", "gamma") not in pairs, \
        "terms in different spans never bind — co-occurrence is the law"


def test_one_edge_per_pair_per_span_never_an_echo():
    _, edges = graphlaw.extract("wall wall seasons wall seasons",
                                [(0, 30)], "document", "d", 1.0)
    assert len([e for e in edges
                if (e["a"], e["b"]) == ("seasons", "wall")]) == 1


def test_the_cross_document_edge_found_by_the_walk():
    book = {}
    n1, e1 = _rows("rammed earth walls breathe with the seasons", "rammed")
    n2, e2 = _rows("lime plaster protects walls from rain", "lime")
    graphlaw.put(book, "rec-1", LAW, n1, e1)
    graphlaw.put(book, "rec-2", LAW, n2, e2)
    hits = graphlaw.walk(book, ["rec-1", "rec-2"],
                         graphlaw.terms("how are walls tied to the seasons?"))
    assert hits and hits[0]["ref"] == "rec-1" and "walls" in hits[0]["pair"]
    h2 = graphlaw.walk(book, ["rec-1", "rec-2"],
                       graphlaw.terms("what connects plaster and rain?"))
    assert h2 and h2[0]["ref"] == "rec-2", "the second document's own edge"


def test_the_walk_never_leaves_the_authorized_set():
    book = {}
    n, e = _rows("secret walls bound to secret seasons", "hidden")
    graphlaw.put(book, "rec-x", LAW, n, e)
    assert graphlaw.walk(book, [], ["walls", "seasons"]) == [], \
        "a matching edge outside the authorized ids contributes NOTHING"


def test_purge_forgets_what_only_the_dead_record_knew():
    book = {}
    n, e = _rows("walls breathe with seasons", "d")
    graphlaw.put(book, "rec-1", LAW, n, e)
    assert graphlaw.evict(book, "rec-1") == len(n) + len(e)
    assert graphlaw.walk(book, ["rec-1"], ["walls", "seasons"]) == []


def test_worklist_lists_unextracted_and_law_stale_only():
    book = {}
    graphlaw.put(book, "done", LAW, [], [])
    graphlaw.put(book, "stale", "old-law", [], [])
    assert graphlaw.missing(book, ["done", "stale", "new"], LAW) == [
        "stale", "new"]
    assert graphlaw.law_hash(POL) != graphlaw.law_hash(
        {"chunk_chars": 300, "overlap_chars": 40}), \
        "a turned chunk policy re-cuts the graph too — edges live in spans"
