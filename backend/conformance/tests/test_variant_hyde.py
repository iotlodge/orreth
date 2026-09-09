# PROVENANCE: Claude Fable 5 (claude-fable-5) — 0065 sp4, HyDE's law suite · 2026-09-09
"""The four canonical laws (cited · rebuild-identical · purge-silent ·
one-truth) plus the one delta naming what HyDE does that naive cannot."""
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
    stacks.ingest(fld, lib, kp, "lifts",
                  "Formwork lifts and thin subsoil layers give the ramming "
                  "its strength and its striped face.")
    return fld, lib, kp


def _ask(fld):
    return styles.RETRIEVERS["hyde"](fld, "ramming moist subsoil approaches")


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


def test_delta_search_rides_the_imagined_answer_not_the_ask():
    fld, _, _ = _floor()
    hits = _ask(fld)
    assert hits and hits[0].get("hypothesis"), \
        "the search confesses the hypothesis it rode"
    seed = stacks.retrieve(stacks.project(fld), "ramming moist subsoil approaches",
                           k=1)[0]
    assert any(h["ref"] != seed["ref"] or h["text"] != seed["text"]
               for h in hits), \
        "the hypothesis found NEIGHBORS of the answer's shape — not the seed"