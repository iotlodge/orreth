# PROVENANCE: Fable 5 (claude-fable-5) — 0039, the Chronicle and the Canon · 2026-07-23
"""The Canon (0039) sp1: the two books stand — under test.

Under test: the registry plants once as a versioned Canon asset wearing the
charter's attributes; classification reads tags floors-first; THE PRIVACY
FLOOR holds at projection time — a sovereign record never chunks no matter
what else it wears; dispatch stays retrievable; the census rolls the shelf."""
from orreth_sim import canon, provisioner, stacks
from orreth_sim.node import make_memory


def _floor():
    prov = provisioner.provision(provisioner.second_brain_template(), "t")
    fld = prov.fields["desk"]
    b = prov.beckys["u:t/e:life/f:desk"]
    lib, kp = b.issue_identity("instance", "u:t/e:life/f:desk", resident=True)
    return fld, lib, kp


def test_registry_is_a_canon_asset_with_charter_attributes():
    fld, lib, kp = _floor()
    assert canon.plant_registry(fld, lib, kp)
    assert canon.plant_registry(fld, lib, kp) is None      # genesis once
    reg = canon.registry(fld)
    obj = reg["classes"]["chronicle-objective"]
    assert obj["rto"] and obj["rpo"] and obj["retention"]["min"] == "P7Y"
    assert reg["classes"]["profile"]["retrievable"] is False
    assert reg["classes"]["dispatch"]["retrievable"] is True


def test_floors_first_classification():
    assert canon.class_of({"tags": ["profile", "stacks", "document"]}) == "profile"
    assert canon.class_of({"tags": ["testament"]}) == "testament"
    assert canon.class_of({"tags": ["dispatch", "naive", "get"]}) == "dispatch"
    assert canon.class_of({"tags": ["stacks", "document", "notes"]}) == "document"
    assert canon.class_of({"tags": ["something-else"]}) == "chronicle-observation"


def test_privacy_floor_holds_at_projection():
    """A sovereign record NEVER chunks — even wearing the stacks' own tags."""
    fld, lib, kp = _floor()
    stacks.plant_eco_assets(fld, lib, kp)
    canon.plant_registry(fld, lib, kp)
    stacks.ingest(fld, lib, kp, "walls", "Rammed earth walls breathe.")
    # a record dressed as a document AND marked profile — the floor wins
    smuggled = make_memory(lib, kp, fld.scope,
                           {"stacks_document": {"name": "diary",
                                                "text": "the human's private "
                                                        "medical notes"}},
                           kind="semantic",
                           tags=["stacks", "document", "diary", "profile"])
    fld.write(smuggled)
    proj = stacks.project(fld)
    texts = " ".join(c["text"] for c in proj["chunks"])
    assert "medical" not in texts                        # the floor held
    assert "breathe" in texts                            # the honest doc serves
    hits = stacks.retrieve(proj, "private medical notes diary")
    assert all("medical" not in h["text"] for h in hits)


def test_census_rolls_the_shelf():
    fld, lib, kp = _floor()
    stacks.plant_eco_assets(fld, lib, kp)
    canon.plant_registry(fld, lib, kp)
    names = {e["name"] for e in canon.census(fld)}
    assert {"record-classes", "stacks-chunking", "stacks-embedding",
            "stacks-prompt"} <= names
    assert all(e["versions"] >= 1 for e in canon.census(fld))