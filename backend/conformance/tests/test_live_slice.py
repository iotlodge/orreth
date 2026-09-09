# PROVENANCE: Claude Fable 5 (claude-fable-5) — 0066 sp5, the slice's suite · 2026-09-09
"""The live slice explores deterministically inside the human's hard bound,
always confessed; the put side derives; the router row rests."""
import json

from orreth_sim import (crypto, dials, dispatcher, provisioner, stacks,
                        tournament, variants)

BUILT = variants.built(tournament.ALL_RETRIEVERS)


def _floor():
    prov = provisioner.provision(provisioner.second_brain_template(), "t")
    fld = prov.fields["desk"]
    b = prov.beckys["u:t/e:life/f:desk"]
    lib, kp = b.issue_identity("instance", "u:t/e:life/f:desk", resident=True)
    stacks.plant_eco_assets(fld, lib, kp)
    return fld, lib, kp


def _explored(fld, d):
    body = json.loads(crypto._b64d(
        fld.records[d["record"]]["body"]).decode())["dispatch"]
    return body.get("exploration")


def test_the_slice_is_deterministic_and_always_confessed():
    fld, lib, kp = _floor()
    seen_explored = seen_plain = 0
    for i in range(30):
        ask = f"a plain question number {i}"
        d1 = dispatcher.dispatch(fld, lib, kp, ask, built=BUILT, slice_pct=20)
        d2 = dispatcher.dispatch(fld, lib, kp, ask, built=BUILT, slice_pct=20)
        e1, e2 = _explored(fld, d1), _explored(fld, d2)
        assert (e1 is None) == (e2 is None) and d1["flavor"] == d2["flavor"], \
            "same ask, same slice decision, forever"
        if e1:
            seen_explored += 1
            assert e1["instead_of"] and d1["flavor"] != e1["instead_of"]
            assert "exploration slice" in d1["why"], "always confessed"
            assert f"variant:{d1['flavor']}" in \
                fld.records[d1["record"]]["tags"]
        else:
            seen_plain += 1
    assert seen_explored and seen_plain, \
        "a 20% slice explores some and spares most"


def test_the_hard_bound_holds_whatever_the_dial_says():
    fld, lib, kp = _floor()
    explored = sum(1 for i in range(100)
                   if _explored(fld, dispatcher.dispatch(
                       fld, lib, kp, f"bounded ask {i}", built=BUILT,
                       slice_pct=99)))
    assert explored <= 35, \
        "99 behaves as the pre-set 20 — the dial can never widen the bound"
    assert dials.DIALS_V1["live-slice-pct"]["max"] == 20, \
        "the registry's own ceiling is the human's word, set in advance"


def test_the_slice_never_overrides_the_asker_and_zero_closes_it():
    fld, lib, kp = _floor()
    for i in range(30):
        d = dispatcher.dispatch(fld, lib, kp, f"forced ask {i}", built=BUILT,
                                force="hyde", slice_pct=20)
        assert d["flavor"] == "hyde" and not _explored(fld, d), \
            "the asker's word outranks exploration"
    for i in range(30):
        d = dispatcher.dispatch(fld, lib, kp, f"closed ask {i}", built=BUILT,
                                slice_pct=0)
        assert not _explored(fld, d), "0 is the closed slice"


def test_the_put_side_derives_by_modality():
    fld, lib, kp = _floor()
    dispatcher.plant_standard(fld, lib, kp)
    text_rows = dispatcher.dispatch_put(fld, ["stacks", "document"])
    media_rows = dispatcher.dispatch_put(fld, ["stacks", "media:image"])
    assert "multimodal" not in text_rows and "naive" in text_rows, \
        "text never feeds the media shelf"
    assert set(media_rows) <= {"multimodal", "naive"} and media_rows, \
        "media feeds the media style and the baseline, nothing else"


def test_the_router_row_rests_and_the_swarm_keeps_its_tactic():
    assert "router" not in tournament.ALL_RETRIEVERS, \
        "Auto absorbed the row — a switch position, never a contestant"
    fld, lib, kp = _floor()
    stacks.ingest(fld, lib, kp, "rammed-earth",
                  "Rammed earth walls breathe with the seasons.")
    hits = tournament.swarm_retrieve(fld, "how are walls connected to "
                                          "seasons, and what protects them?")
    assert hits is not None, "the tactic-picker lives on inside the fan-out"


def test_the_retirement_stands_once_and_only_once():
    fld, lib, kp = _floor()
    rid = dispatcher.plant_router_retirement(fld, lib, kp)
    assert rid, "the honorable rest lands as a signed record"
    assert dispatcher.plant_router_retirement(fld, lib, kp) is None, \
        "one rest per world — dormancy is never re-announced"
    body = json.loads(crypto._b64d(
        fld.records[rid]["body"]).decode())["retirement"]
    assert body["row"] == "router" and "Auto" in body["absorbed_by"]
