# PROVENANCE: Claude Fable 5 (claude-fable-5) — 0065 sp4, Memory-Augmented's law suite · 2026-09-09
"""The four canonical laws (cited · rebuild-identical · purge-silent ·
one-truth) plus the one delta naming what Memory-Augmented does that naive cannot."""
from orreth_sim import provisioner, stacks, styles


def _floor():
    prov = provisioner.provision(provisioner.second_brain_template(), "t")
    fld = prov.fields["desk"]
    b = prov.beckys["u:t/e:life/f:desk"]
    lib, kp = b.issue_identity("instance", "u:t/e:life/f:desk", resident=True)
    stacks.plant_eco_assets(fld, lib, kp)
    stacks.ingest(fld, lib, kp, "curing",
                  "Curing rammed earth walls takes weeks of slow drying.")
    from orreth_sim.node import make_memory
    conv = make_memory(lib, kp, fld.scope,
                       {"parlor": True,
                        "asked": "tell me about curing the rammed walls",
                        "reply": "curing takes weeks — the drying decision "
                                 "stands"},
                       kind="episodic", tags=["parlor"])
    fld.write(conv)
    return fld, lib, kp


def _ask(fld):
    return styles.RETRIEVERS["memory-augmented"](fld, "what did we decide about the walls?")


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


def test_delta_remembering_contributes_terms_the_raw_ask_lacked():
    fld, _, _ = _floor()
    hits = _ask(fld)
    assert hits and hits[0].get("memory"), \
        "the rewrite CONFESSES what remembering added"
    from orreth_sim import graphlaw
    raw = set(graphlaw.terms("what did we decide about the walls?"))
    assert any(t not in raw for t in hits[0]["memory"].split()), \
        "the chronicle contributed a term the raw ask never had"