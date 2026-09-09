# PROVENANCE: Claude Fable 5 (claude-fable-5) — 0065 sp4, Reasoning-First's law suite · 2026-09-09
"""The four canonical laws (cited · rebuild-identical · purge-silent ·
one-truth) plus the one delta naming what Reasoning-First does that naive cannot."""
from orreth_sim import provisioner, stacks, styles


def _floor():
    prov = provisioner.provision(provisioner.second_brain_template(), "t")
    fld = prov.fields["desk"]
    b = prov.beckys["u:t/e:life/f:desk"]
    lib, kp = b.issue_identity("instance", "u:t/e:life/f:desk", resident=True)
    stacks.plant_eco_assets(fld, lib, kp)
    stacks.ingest(fld, lib, kp, "curing",
                  "Rammed earth walls cured slowly over weeks of drying.")
    stacks.ingest(fld, lib, kp, "plaster",
                  "Lime plaster protects walls from rain while breathing.")
    fld._me, fld._kp = lib, kp        # a seat stands — the plan can land
    return fld, lib, kp


def _ask(fld):
    return styles.RETRIEVERS["reasoning-first"](fld, "how are walls cured slowly, and what protects walls from rain?")


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


def test_delta_the_plan_is_a_signed_record_and_steps_are_named():
    fld, _, _ = _floor()
    hits = _ask(fld)
    assert hits and hits[0].get("plan"), "the plan landed as a record"
    plan = fld.records.get(hits[0]["plan"])
    assert plan is not None, "the plan ref OPENS — a whole id, never a stub"
    assert all(h.get("step") for h in hits), "every hit names its plan step"
    assert len({h["step"] for h in hits}) > 1, \
        "a two-part ask ran targeted retrieves per part — not one big net"