# PROVENANCE: Fable 5 (claude-fable-5) — 0042, the Deed · 2026-07-25
"""The Deed (0042) sp1: the shelf and the family — under test.

Under test: the class shelf plants once as Canon; the whisper floor holds both
directions (T0 carries no family, and refuses one); a witnessed deed walks the
whole family in order; the actor may never witness its own success; closure
demands the tier's roles and refuses a wrong world; the idempotency key
remembers across deeds; compensation moves only on a fresh human word and is
itself a deed."""
import pytest
from orreth_sim import deed, provisioner


def _floor():
    prov = provisioner.provision(provisioner.second_brain_template(), "t")
    fld = prov.fields["desk"]
    b = prov.beckys["u:t/e:life/f:desk"]
    actor, akp = b.issue_identity("instance", "u:t/e:life/f:desk", resident=True)
    witness, wkp = b.issue_identity("instance", "u:t/e:life/f:desk", resident=True)
    return fld, (actor, akp), (witness, wkp)


def _walk_to_observed(fld, actor, akp, witness, wkp, *, key="plan-hash-1"):
    d = deed.open_deed(fld, actor, akp, effect="outbound-publish",
                       change="publish the 0.41 moment", objective="obj-1")
    deed.authorize(fld, witness, wkp, d, budget=1.0, window_s=600,
                   idempotency_key=key)
    deed.attempt(fld, actor, akp, d, manifests={"artifact": "post-7"},
                 epoch="sha256:feedfacecafe")
    deed.receipt(fld, actor, akp, d, acknowledged={"status": "201"})
    return d


def test_the_shelf_plants_once_and_carries_the_roster():
    fld, (actor, akp), _ = _floor()
    assert deed.plant_classes(fld, actor, akp)
    assert deed.plant_classes(fld, actor, akp) is None        # genesis once
    cs = deed.classes(fld)["classes"]
    assert cs["estate-apply"]["tier"] == "T3" and cs["estate-apply"]["compensation"]
    assert cs["outbound-publish"]["tier"] == "T2"
    assert cs["note"]["tier"] == "T0"
    with pytest.raises(ValueError):
        deed.effect_class(fld, "world-domination")            # unknown grammar


def test_the_whisper_floor_holds_both_directions():
    fld, (actor, akp), _ = _floor()
    before = len(fld.records)
    deed.deed_note(fld, actor, akp, text="tidied the shelf")
    assert len(fld.records) == before + 1                     # ONE record, no family
    with pytest.raises(ValueError):                           # whisper refuses ceremony
        deed.open_deed(fld, actor, akp, effect="note",
                       change="x", objective="obj-1")


def test_a_witnessed_deed_walks_the_whole_family_in_order():
    fld, (actor, akp), (witness, wkp) = _floor()
    d = _walk_to_observed(fld, actor, akp, witness, wkp)
    deed.observe(fld, witness, wkp, d, found={"live": True})
    v = deed.reconcile(fld, witness, wkp, d, expected={"live": True})
    assert v["holds"]
    deed.close(fld, actor, akp, d, uncertainty="cache propagation unverified")
    roles = [r for r, _ in deed.walk(fld, d)]
    assert roles == ["intent", "authorization", "attempt", "receipt",
                     "observation", "reconciliation", "closure"]


def test_the_actor_is_not_the_sole_witness():
    fld, (actor, akp), (witness, wkp) = _floor()
    d = _walk_to_observed(fld, actor, akp, witness, wkp)
    with pytest.raises(ValueError):                           # 0005, grown up
        deed.observe(fld, actor, akp, d, found={"live": True})
    deed.observe(fld, witness, wkp, d, found={"live": True})  # the distinct seat may


def test_closure_demands_the_tier_and_refuses_a_wrong_world():
    fld, (actor, akp), (witness, wkp) = _floor()
    d = _walk_to_observed(fld, actor, akp, witness, wkp)
    with pytest.raises(ValueError):                           # no observation yet
        deed.close(fld, actor, akp, d, uncertainty="none named")
    deed.observe(fld, witness, wkp, d, found={"live": False})
    v = deed.reconcile(fld, witness, wkp, d, expected={"live": True})
    assert not v["holds"] and v["staged"]["compensation"]     # staged, never enacted
    with pytest.raises(ValueError):                           # a wrong world won't close
        deed.close(fld, actor, akp, d, uncertainty="the world disagrees")


def test_the_hand_moves_only_after_the_gate_and_under_an_epoch():
    fld, (actor, akp), (witness, wkp) = _floor()
    d = deed.open_deed(fld, actor, akp, effect="outbound-publish",
                       change="x", objective="obj-1")
    with pytest.raises(ValueError):                           # no authorization
        deed.attempt(fld, actor, akp, d, manifests={}, epoch="sha256:aa")
    deed.authorize(fld, witness, wkp, d, budget=1.0, window_s=600,
                   idempotency_key="k1")
    with pytest.raises(ValueError):                           # no epoch, no deed (0041)
        deed.attempt(fld, actor, akp, d, manifests={}, epoch="")


def test_the_key_remembers():
    fld, (actor, akp), (witness, wkp) = _floor()
    d1 = _walk_to_observed(fld, actor, akp, witness, wkp, key="one-change")
    fam_attempt = deed.attempt(fld, actor, akp, d1, manifests={"again": True},
                               epoch="sha256:bb")             # same deed: same attempt
    assert fam_attempt == dict(deed.walk(fld, d1))["attempt"]
    d2 = deed.open_deed(fld, actor, akp, effect="outbound-publish",
                        change="the same change again", objective="obj-1")
    deed.authorize(fld, witness, wkp, d2, budget=1.0, window_s=600,
                   idempotency_key="one-change")
    with pytest.raises(ValueError):                           # across deeds: refused
        deed.attempt(fld, actor, akp, d2, manifests={}, epoch="sha256:cc")


def test_compensation_waits_for_the_human_and_is_itself_a_deed():
    fld, (actor, akp), (witness, wkp) = _floor()
    d = _walk_to_observed(fld, actor, akp, witness, wkp)
    deed.observe(fld, witness, wkp, d, found={"live": False})
    deed.reconcile(fld, witness, wkp, d, expected={"live": True})
    with pytest.raises(ValueError):                           # no word, no lever
        deed.compensate(fld, actor, akp, d, human_word=False, objective="obj-1")
    comp = deed.compensate(fld, actor, akp, d, human_word=True, objective="obj-1")
    assert dict(deed.walk(fld, d))["compensation"]            # on the record
    assert dict(deed.walk(fld, comp))["intent"] == comp       # a fresh family opens
