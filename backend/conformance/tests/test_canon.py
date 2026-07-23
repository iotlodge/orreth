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

def test_chronicle_joins_the_rows_with_time():
    """0039 sp2: the universe's own life is retrievable — class-gated, cited,
    each chunk stamped with its moment; the time dial walks the timeline and
    timeless chunks stand aside; the floor still wins over everything."""
    from orreth_sim import dispatcher
    fld, lib, kp = _floor()
    stacks.plant_eco_assets(fld, lib, kp)
    canon.plant_registry(fld, lib, kp)
    old = make_memory(lib, kp, fld.scope,
                      {"objective": {"text": "adopt the estate stacks and open "
                                             "the acceptance gate"}},
                      kind="episodic", tags=["objective", "estate"],
                      occurred_at="2026-07-20T10:00:00Z",
                      provenance_class="ingested-archive")
    fld.write(old)
    new = make_memory(lib, kp, fld.scope,
                      {"observation": {"note": "the estate stacks tournament "
                                               "crowned the graph row"}},
                      kind="episodic", tags=["observation", "estate"],
                      occurred_at="2026-07-22T22:00:00Z",
                      provenance_class="ingested-archive")
    fld.write(new)
    proj = stacks.project(fld)
    hits = stacks.retrieve(proj, "what happened with the estate stacks?")
    assert {h["doc"] for h in hits} >= {"objective", "observation"}
    # the time dial: since excludes the old; as-of excludes the new
    since = stacks.retrieve(proj, "estate stacks since 2026-07-21")
    assert since and all(h["doc"] == "observation" for h in since)
    asof = stacks.retrieve(proj, "estate stacks as of 2026-07-21")
    assert asof and all(h["doc"] == "objective" for h in asof)
    assert "temporal" in dispatcher.classify("estate since 2026-07-21")


def test_metabolism_hears_usage_and_measures_loss():
    """0039 sp3: the dialed metabolism — a cold record past its class window
    distills; a RECALLED record stays warm and low; the distillation's
    information loss is measured (0033) and the report lands on the record."""
    fld, lib, kp = _floor()
    stacks.plant_eco_assets(fld, lib, kp)
    canon.plant_registry(fld, lib, kp)
    canon.plant_dials(fld, lib, kp)
    fld.undistilled.clear()                       # only our subjects on the bench
    cold = make_memory(lib, kp, fld.scope,
                       {"observation": {"note": "the retail floor idled all "
                                                "spring"}},
                       kind="episodic", tags=["observation", "retail"],
                       occurred_at="2026-05-01T10:00:00Z",
                       provenance_class="ingested-archive")
    warm = make_memory(lib, kp, fld.scope,
                       {"observation": {"note": "the care floor greets its "
                                                "human each morning"}},
                       kind="episodic", tags=["observation", "care"],
                       occurred_at="2026-05-01T11:00:00Z",
                       provenance_class="ingested-archive")
    fld.write(cold)
    fld.write(warm)
    # the tap: retrieval warms the warm one
    proj = stacks.project(fld)
    stacks.answer(fld, proj, "care floor greets its human each morning")
    assert fld.recalls and warm["id"] in fld.recalls
    r = canon.metabolism_beat(fld, lib, kp)
    assert r["distilled"] >= 1 and r["kept_warm"] >= 1
    assert cold["id"] not in fld.undistilled      # the cold rose
    assert warm["id"] in fld.undistilled          # the recalled stays low
    assert "loss_bits" in r and r["distillation"]
    reports = [x for x in fld.records.values()
               if "metabolism-report" in (x.get("tags") or [])]
    assert reports                                 # tuning is evidence now
