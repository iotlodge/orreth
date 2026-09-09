# PROVENANCE: Claude Fable 5 (claude-fable-5) — 0065 sp4, Hierarchical's law suite · 2026-09-09
"""The four canonical laws (cited · rebuild-identical · purge-silent ·
one-truth) plus the one delta naming what Hierarchical does that naive cannot."""
from orreth_sim import provisioner, stacks, styles


def _floor():
    prov = provisioner.provision(provisioner.second_brain_template(), "t")
    fld = prov.fields["desk"]
    b = prov.beckys["u:t/e:life/f:desk"]
    lib, kp = b.issue_identity("instance", "u:t/e:life/f:desk", resident=True)
    stacks.plant_eco_assets(fld, lib, kp)
    long = ("Rammed earth walls are built in lifts. " * 12
            + "Curing rammed earth walls takes weeks of slow drying. " * 12
            + "Finish coats protect the cured walls. " * 12)
    stacks.ingest(fld, lib, kp, "earth-manual", long)
    stacks.ingest(fld, lib, kp, "note", "a short unrelated note on tools")
    return fld, lib, kp


def _ask(fld):
    return styles.RETRIEVERS["hierarchical"](fld, "how are rammed earth walls cured?")


def test_cited():
    fld, _, _ = _floor()
    hits = _ask(fld)
    assert hits and all(h.get("ref") for h in hits), \
        "every hit carries the record it stands on"


def test_rebuild_identical():
    fld, _, _ = _floor()
    assert _ask(fld) == _ask(fld), \
        "the same log answers the same, forever — no dice"


def test_one_truth():
    fld, _, _ = _floor()
    assert all(h["ref"] in fld.records for h in _ask(fld)), \
        "hits point only at records the node holds — never a second store"


def test_purge_silent():
    fld, _, _ = _floor()
    before = _ask(fld)
    assert before
    fld.records.pop(before[0]["ref"], None)
    after = _ask(fld)
    assert all(h["ref"] != before[0]["ref"] for h in after), \
        "a record gone from the log stops speaking everywhere"


def test_delta_a_hit_carries_its_section_not_just_its_chunk():
    fld, _, _ = _floor()
    hits = _ask(fld)
    top = hits[0]
    assert top.get("section"), "a long document's hit climbed to its section"
    s0, e0 = top["section"]
    assert (e0 - s0) > 280, "the section is wider than one chunk — context, " \
                            "not just the matching passage"