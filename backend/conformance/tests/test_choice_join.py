# PROVENANCE: Claude Fable 5 (claude-fable-5) — 0066 sp1, the join's suite · 2026-09-09
"""The choice joins the world: it derives from the rulebook version that made
it, the answer derives from the choice, and a thumb walks to the routing
decision it judges in one lineage hop."""
from orreth_sim import dispatcher, provisioner, stacks, thumb
from orreth_sim.node import make_memory


def _floor():
    prov = provisioner.provision(provisioner.second_brain_template(), "t")
    fld = prov.fields["desk"]
    b = prov.beckys["u:t/e:life/f:desk"]
    lib, kp = b.issue_identity("instance", "u:t/e:life/f:desk", resident=True)
    stacks.plant_eco_assets(fld, lib, kp)
    stacks.ingest(fld, lib, kp, "rammed-earth",
                  "Rammed earth walls breathe with the seasons.")
    return fld, lib, kp


def test_the_choice_derives_from_the_rulebook_version():
    fld, lib, kp = _floor()
    assert dispatcher.plant_standard(fld, lib, kp)
    d = dispatcher.dispatch(fld, lib, kp, "how are walls tied to seasons?")
    choice = fld.records[d["record"]]
    lineage = choice.get("derived_from") or []
    assert lineage, "the choice is no longer a leaf"
    import json
    from orreth_sim import crypto
    parent = json.loads(crypto._b64d(fld.records[lineage[0]]["body"]).decode())
    assert (parent.get("asset") or {}).get("name") == "routing-standard", \
        "lineage points at the exact policy version that made the choice"


def test_the_choice_wears_its_coordinate_and_featurizer():
    fld, lib, kp = _floor()
    dispatcher.plant_standard(fld, lib, kp)
    d = dispatcher.dispatch(fld, lib, kp, "walls and seasons?",
                            origin="ask:did:key:zSomeone")
    tags = fld.records[d["record"]]["tags"]
    assert f"variant:{d['flavor']}" in tags, "the style tag — 0065 sp5's law"
    assert any(t.startswith("origin:") for t in tags), "who asked rides too"
    import json
    from orreth_sim import crypto
    body = json.loads(crypto._b64d(
        fld.records[d["record"]]["body"]).decode())["dispatch"]
    from orreth_sim import featurizer
    assert body["featurizer_version"] == featurizer.VERSION, \
        "the analyzer's version pins to its one source of truth"
    assert body.get("standard_ref"), "the whole rulebook ref rides in the body"


def test_an_unplanted_rulebook_leaves_lineage_empty_honestly():
    fld, lib, kp = _floor()          # genesis only — nothing on the shelf
    d = dispatcher.dispatch(fld, lib, kp, "anything?")
    assert not (fld.records[d["record"]].get("derived_from") or []), \
        "no shelf version, no lineage — never a fabricated ref"


def test_thumb_to_choice_in_one_lineage_hop():
    fld, lib, kp = _floor()
    dispatcher.plant_standard(fld, lib, kp)
    d = dispatcher.dispatch(fld, lib, kp, "how are walls tied to seasons?")
    # the answer record derives from the choice (the worker's exchange law)
    exch = make_memory(lib, kp, fld.scope,
                       {"ask": {"asked": "walls?", "reply": "they breathe",
                                "choice": d["record"]}},
                       kind="episodic", tags=["ask", f"variant:{d['flavor']}"])
    exch["derived_from"] = [d["record"]]
    fld.write(exch)
    # a human's thumb lands on the EXCHANGE — and walks to the choice
    verdict, _ = thumb.make_thumb(lib, kp, fld.scope, of=exch["id"], up=False,
                                  text="wrong shelf")
    fld.write(verdict)
    import json
    from orreth_sim import crypto
    judged = json.loads(crypto._b64d(verdict["body"]).decode())
    of = judged["grading"]["of"] if "grading" in judged else \
        next(v["of"] for v in judged.values() if isinstance(v, dict) and "of" in v)
    hop = (fld.records[of].get("derived_from") or [None])[0]
    assert hop == d["record"], "thumb → judged answer → ONE hop → the choice"
    choice_body = json.loads(crypto._b64d(
        fld.records[hop]["body"]).decode())["dispatch"]
    assert choice_body["flavor"] == d["flavor"] and choice_body["why"], \
        "the decision a reward now reaches: which style, and the spoken why"
