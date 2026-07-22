# PROVENANCE: Fable 5 (claude-fable-5) — 0038, the Stacks · 2026-07-22
"""The Stacks (0038) spoonful 1: the baseline breathes — under the one-truth law.

Under test: ingestion happens ONCE (the document is a signed record, the stack
holds only a projection); the projection is REBUILDABLE (tear down, regrow, the
same answers return); a record that leaves the log stops speaking (the purge's
reach); answers carry citations to walkable refs; empty retrieval answers
honestly; the eco assets plant once, versioned on the shelf."""
from orreth_sim import improver, provisioner, stacks


def _floor():
    prov = provisioner.provision(provisioner.second_brain_template(), "t")
    fld = prov.fields["desk"]
    b = prov.beckys["u:t/e:life/f:desk"]
    lib, lib_kp = b.issue_identity("instance", "u:t/e:life/f:desk", resident=True)
    return fld, lib, lib_kp


def test_eco_assets_plant_once_versioned():
    fld, lib, kp = _floor()
    ids = stacks.plant_eco_assets(fld, lib, kp)
    assert len(ids) == 3
    assert stacks.plant_eco_assets(fld, lib, kp) == []      # genesis plants once
    row = improver.active_asset(fld, "stacks-chunking")
    assert row and improver._profile_of(row[1])["chunk_chars"] == 280


def test_one_truth_and_cited_answers():
    """One record per document; the answer's citations walk back to it."""
    fld, lib, kp = _floor()
    stacks.plant_eco_assets(fld, lib, kp)
    rid = stacks.ingest(fld, lib, kp, "rammed-earth",
                        "Rammed earth walls are compacted soil, formed in "
                        "lifts. Packed soil holds heat and breathes.")
    stacks.ingest(fld, lib, kp, "pipelines",
                  "CodePipeline moves artifacts between build stages.")
    docs = [r for r in fld.records.values()
            if "document" in (r.get("tags") or [])]
    assert len(docs) == 2                                    # ingested ONCE each
    proj = stacks.project(fld)
    a = stacks.answer(fld, proj, "how do packed soil walls hold heat?")
    assert a["citations"] and a["citations"][0]["ref"] == rid
    assert rid[:18] in a["answer"]                           # the claim wears its ref
    none = stacks.answer(fld, proj, "zzqx unrelated frobnication")
    assert none["citations"] == [] and "honest" in none["answer"]


def test_projection_rebuilds_and_purge_reaches():
    """Disposable by design: regrown equals original; a record gone from the
    log is gone from the next rebuild — the purge reaches every stack."""
    fld, lib, kp = _floor()
    stacks.plant_eco_assets(fld, lib, kp)
    rid = stacks.ingest(fld, lib, kp, "rammed-earth",
                        "Rammed earth walls are compacted soil in lifts.")
    p1 = stacks.project(fld)
    p2 = stacks.project(fld)                                 # torn down, regrown
    assert [c["ref"] for c in p1["chunks"]] == [c["ref"] for c in p2["chunks"]]
    assert [c["vec"] for c in p1["chunks"]] == [c["vec"] for c in p2["chunks"]]
    del fld.records[rid]                                     # the log's word is final
    p3 = stacks.project(fld)
    assert not p3["chunks"]                                  # it stopped speaking
    assert stacks.answer(fld, p3, "compacted soil walls")["citations"] == []
