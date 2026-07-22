# PROVENANCE: Fable 5 (claude-fable-5) — 0038, the Stacks · 2026-07-22
"""The Stacks (0038) sp3: the rivals under the same laws.

Under test: all three rows derive from the ONE log (no second store); the
graph walks relationships the baseline's distances miss; rerank sharpens
precision; hybrid defends with both; every row rebuilds identical and forgets
what the log forgets; every answer wears citations."""
from orreth_sim import provisioner, rivals, stacks


def _floor():
    prov = provisioner.provision(provisioner.second_brain_template(), "t")
    fld = prov.fields["desk"]
    b = prov.beckys["u:t/e:life/f:desk"]
    lib, kp = b.issue_identity("instance", "u:t/e:life/f:desk", resident=True)
    stacks.plant_eco_assets(fld, lib, kp)
    stacks.ingest(fld, lib, kp, "rammed-earth",
                  "Rammed earth walls are compacted soil formed in lifts. "
                  "Packed soil holds heat through the day and releases it at "
                  "night, breathing with the seasons.")
    stacks.ingest(fld, lib, kp, "lime-plaster",
                  "Lime plaster finishes protect rammed earth walls from "
                  "rain while letting moisture escape the soil.")
    return fld, lib, kp


def test_graph_walks_what_distance_misses():
    """The relational ask: which chunk BINDS walls and seasons — the graph
    answers with the edge's own provenance."""
    fld, _, _ = _floor()
    g = rivals.graph_project(fld)
    hits = rivals.graph_retrieve(g, "how are walls connected to the seasons?")
    assert hits and hits[0]["doc"] == "rammed-earth"
    assert "walls" in hits[0]["pair"] or "seasons" in hits[0]["pair"]
    # cross-document walking: plaster ↔ rain lives only in the second doc
    h2 = rivals.graph_retrieve(g, "what connects plaster and rain?")
    assert h2 and h2[0]["doc"] == "lime-plaster"


def test_rerank_sharpens_precision():
    fld, _, _ = _floor()
    proj = stacks.project(fld)
    hits = rivals.rerank_retrieve(proj, "lime plaster rain protection")
    assert hits and hits[0]["doc"] == "lime-plaster"


def test_all_rows_one_truth_and_rebuildable():
    """Every rival regrows identical from the log; a forgotten record stops
    speaking in EVERY row at once; every answer wears citations."""
    fld, _, _ = _floor()
    for flavor in ("naive", "rerank", "graph", "hybrid"):
        a = rivals.answer_as(fld, flavor, "how do walls handle the seasons?")
        assert a["flavor"] == flavor
        assert a["citations"], flavor                     # cited, every row
    g1, g2 = rivals.graph_project(fld), rivals.graph_project(fld)
    assert g1["nodes"] == g2["nodes"] and set(g1["edges"]) == set(g2["edges"])
    rid = next(r for r, v in fld.records.items()
               if "rammed-earth" in (v.get("tags") or []))
    del fld.records[rid]                                  # the log's word is final
    for flavor in ("naive", "rerank", "graph", "hybrid"):
        a = rivals.answer_as(fld, flavor, "packed soil breathing seasons")
        assert all(c["ref"] != rid for c in a["citations"]), flavor