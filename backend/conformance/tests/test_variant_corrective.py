# PROVENANCE: Claude Fable 5 (claude-fable-5) — 0065 sp4, Corrective's law suite · 2026-09-09
"""The four canonical laws (cited · rebuild-identical · purge-silent ·
one-truth) plus the one delta naming what Corrective does that naive cannot."""
from orreth_sim import provisioner, stacks, styles


def _floor():
    prov = provisioner.provision(provisioner.second_brain_template(), "t")
    fld = prov.fields["desk"]
    b = prov.beckys["u:t/e:life/f:desk"]
    lib, kp = b.issue_identity("instance", "u:t/e:life/f:desk", resident=True)
    stacks.plant_eco_assets(fld, lib, kp)
    stacks.ingest(fld, lib, kp, "ramming",
                  "Rammed earth walls are constructed by ramming moist "
                  "subsoil between formwork in thin lifts.")
    stacks.ingest(fld, lib, kp, "other",
                  "The garden path is gravel over compacted base.")
    return fld, lib, kp


def _ask(fld):
    return styles.RETRIEVERS["corrective"](fld, "formwork lifts budget costs schedule")


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


def test_delta_a_weak_catch_earns_a_visible_second_look():
    fld, _, _ = _floor()
    hits = _ask(fld)     # a one-word ask reads weak against the floor
    assert hits and "corrected" in hits[0], \
        "the second look is never a secret — served or not, it is on the hit"


def test_delta_a_strong_catch_is_left_alone():
    fld, _, _ = _floor()
    strong = styles.RETRIEVERS["corrective"](
        fld, "rammed earth walls constructed ramming subsoil formwork lifts")
    assert strong and "corrected" not in strong[0], \
        "faithful retrieval never triggers the correction round"