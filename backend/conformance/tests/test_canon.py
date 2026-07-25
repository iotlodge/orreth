# PROVENANCE: Fable 5 (claude-fable-5) — 0039, the Chronicle and the Canon · 2026-07-23
"""The Canon (0039) sp1: the two books stand — under test.

Under test: the registry plants once as a versioned Canon asset wearing the
charter's attributes; classification reads tags floors-first; THE PRIVACY
FLOOR holds at projection time — a sovereign record never chunks no matter
what else it wears; dispatch stays retrievable; the census rolls the shelf."""
from orreth_sim import canon, improver, provisioner, stacks
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


def test_same_second_same_score_canaries_are_distinct_runs():
    """Caught live 2026-07-25: a REAL judge scored 0.90 twice in one second —
    identical bodies content-addressed to one record and the ceremony counted
    2/3. Each canary carries its ordinal now; three runs are three records."""
    fld, lib, kp = _floor()
    stacks.plant_eco_assets(fld, lib, kp)
    canon.plant_registry(fld, lib, kp)
    sk = canon.crystallize(fld, lib, kp, objective="fold the week",
                           craft={"steps": ["fold"]},
                           rubric={"min_score": 0.8, "n": 3},
                           proven_tier="high")
    ids = {canon.canary_run(fld, lib, kp, sk, tier="low", score=0.9)
           for _ in range(3)}
    assert len(ids) == 3                       # three runs, three records
    v = canon.graduate(fld, lib, kp, sk, mentee_tier="low")
    assert v["runs"] == 3 and v["graduated"]   # the count is honest now


def test_the_mentor_graduates_the_mentee():
    """0039 sp4 — the finale: crystallize at the smart tier, canary at the
    cheap one under full observation, the standings speak, and graduation is
    EARNED — or refused honestly. Never silently dumber."""
    fld, lib, kp = _floor()
    stacks.plant_eco_assets(fld, lib, kp)
    canon.plant_registry(fld, lib, kp)
    skill = canon.crystallize(fld, lib, kp,
                              objective="summarize a floor's week",
                              craft={"steps": ["gather the week's records",
                                               "distill by score", "cite"]},
                              rubric={"min_score": 0.8, "n": 3},
                              proven_tier="high")
    # a short canary refuses — the mentor keeps the work
    canon.canary_run(fld, lib, kp, skill, tier="low", score=0.9)
    early = canon.graduate(fld, lib, kp, skill, mentee_tier="low")
    assert early["graduated"] is False and "not earned" in early["why"]
    # the full canary clears the rubric — the ceremony
    canon.canary_run(fld, lib, kp, skill, tier="low", score=0.85)
    canon.canary_run(fld, lib, kp, skill, tier="low", score=0.88)
    verdict = canon.graduate(fld, lib, kp, skill, mentee_tier="low")
    assert verdict["graduated"] is True and verdict["mean"] > 0.8
    row = improver.active_asset(fld, skill)
    assert improver._profile_of(row[1])["proven_tier"] == "low"   # the sibling serves
    grads = [r for r in fld.records.values()
             if "graduation" in (r.get("tags") or [])]
    assert len(grads) == 2                        # the refusal AND the ceremony,
    # both on the record — graduation by evidence, demotion by evidence, forever


def test_pointer_law_and_demotion_close_the_constitution():
    """0039 §6 + §4.4 made real before WHOLE: the pointer's hash handshake
    catches a swapped warehouse; drift demotes the skill back to the mentor —
    both on the record."""
    fld, lib, kp = _floor()
    stacks.plant_eco_assets(fld, lib, kp)
    canon.plant_registry(fld, lib, kp)
    pid = canon.make_pointer(fld, lib, kp, name="ml-training-set",
                             uri="s3://orreth-ml/train-v1.parquet",
                             content_hash="sha256:abc123",
                             meta={"rows": 1000000, "class": "artifact-pointer"})
    assert canon.verify_pointer(fld, pid, "sha256:abc123")
    assert not canon.verify_pointer(fld, pid, "sha256:SWAPPED")   # the rug-pull, caught
    # bulk never enters the mind: the pointer projects (metadata), not a corpus
    sk = canon.crystallize(fld, lib, kp, objective="tag the corpus",
                           craft={"steps": ["read", "tag"]},
                           rubric={"min_score": 0.8, "n": 1})
    canon.canary_run(fld, lib, kp, sk, tier="low", score=0.9)
    assert canon.graduate(fld, lib, kp, sk, mentee_tier="low")["graduated"]
    d = canon.demote(fld, lib, kp, sk, evidence="drift: scores fell to 0.55 "
                                                "over the last cohort")
    assert d["demoted"] and improver._profile_of(
        improver.active_asset(fld, sk)[1])["proven_tier"] == "high"
    assert any("demotion" in (r.get("tags") or []) for r in fld.records.values())
