# PROVENANCE: Fable 5 (claude-fable-5) — 0038, the Stacks · 2026-07-22
"""The Dispatcher (0038 §3) sp2: the reflex under test.

Under test: the standard plants once, versioned, as data; classification is
deterministic; the first matching rule routes; an unbuilt row falls to the
baseline LOUDLY on the record; every choice lands as a signed record the
window can walk; the PUT side names only rows that breathe."""
from orreth_sim import dispatcher, provisioner


def _floor():
    prov = provisioner.provision(provisioner.second_brain_template(), "t")
    fld = prov.fields["desk"]
    b = prov.beckys["u:t/e:life/f:desk"]
    lib, kp = b.issue_identity("instance", "u:t/e:life/f:desk", resident=True)
    return fld, lib, kp


def test_standard_plants_once_as_data():
    fld, lib, kp = _floor()
    assert dispatcher.plant_standard(fld, lib, kp)
    assert dispatcher.plant_standard(fld, lib, kp) is None   # genesis once
    std = dispatcher.standard(fld)
    assert std["version"] == "1" and std["default"] == "naive"
    assert {r["route"] for r in std["rules"]} == {"multimodal", "graph",
                                                  "swarm", "rerank"}


def test_shapes_read_deterministically():
    assert dispatcher.classify("how do the pipeline stages connect between "
                               "stacks?") == ["relational"]
    assert "precision" in dispatcher.classify('what is the "exact" wording?')
    assert "multi-source" in dispatcher.classify("compare the care and retail "
                                                 "floors across sources")
    assert dispatcher.classify("how do packed soil walls hold heat?") == []


def test_dispatch_routes_and_falls_back_loudly():
    """A relational ask wants the graph row; the row is not yet built — the
    baseline serves, and the record keeps BOTH truths."""
    fld, lib, kp = _floor()
    dispatcher.plant_standard(fld, lib, kp)
    d = dispatcher.dispatch(fld, lib, kp, "how do the stages connect between "
                                          "the two stacks?")
    assert d["flavor"] == "naive" and d["wanted"] == "graph"
    assert "not yet built" in d["why"] and "on the record" in d["why"]
    plain = dispatcher.dispatch(fld, lib, kp, "how do walls hold heat?")
    assert plain["flavor"] == "naive" and "wanted" not in plain
    # the organ's ledger: every choice walkable (same-second ties don't order)
    led = dispatcher.choices(fld)
    assert len(led) == 2
    assert {e["rule"] for e in led} == {"relational", "default"}
    assert any(e.get("wanted") == "graph" for e in led)
    recs = [r for r in fld.records.values()
            if "dispatch" in (r.get("tags") or [])]
    assert all(r["author"] == lib["did"] for r in recs)      # signed, always


def test_put_side_names_only_breathing_rows():
    fld, lib, kp = _floor()
    dispatcher.plant_standard(fld, lib, kp)
    assert dispatcher.dispatch_put(fld, ["stacks", "document"]) == ["naive"]
