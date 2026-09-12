# PROVENANCE: Claude Fable 5 (claude-fable-5) — 0072 sp2, the workspace engine · 2026-09-11
"""The Workspace engine's laws (0072 sp2): the roster is the registry's own
truth, drafts are held to the landed law, and the head-swap is traceable."""
from orreth_sim import improver, variants, workspace


def test_roster_is_the_menu_whole():
    """Eleven rows, the MENU's own order, each wearing declaration + config
    + built flag — the registry is the one truth, never a hand-kept list."""
    roster = workspace.build_roster({}, {}, ["naive", "graph"])
    assert [r["short"] for r in roster] == list(variants.MENU)
    by = {r["short"]: r for r in roster}
    assert by["naive"]["built"] and by["graph"]["built"]
    assert not by["hyde"]["built"]
    for r in roster:
        assert r["config"] == variants.VARIANTS_V1[r["short"]]["genesis"]
        assert r["tuned"] is False and r["score"] is None


def test_tuned_head_wears_the_dot_and_never_widens():
    """A shelf head moves a declared knob → the dot; an undeclared knob in
    a head is dropped at the read (the genesis serves beneath) — the same
    law the flows live by, so the roster can never lie about what runs."""
    roster = workspace.build_roster(
        {"naive": {"k": 9, "stowaway": 1}}, {}, ["naive"])
    naive = roster[0]
    assert naive["tuned"] is True
    assert naive["config"] == {"k": 9}
    assert "stowaway" not in naive["config"]
    assert naive["genesis"] == {"k": 4}


def test_scores_fold_n_weighted_across_question_kinds():
    cells = {"plain·naive": {"n": 3, "mean": 0.6},
             "exact·naive": {"n": 1, "mean": 1.0},
             "plain·hybrid": {"n": 0, "mean": 0.9}}   # no evidence, no score
    s = workspace.style_scores(cells)
    assert s["naive"] == {"n": 4, "mean": 0.7}
    assert "hybrid" not in s


def test_draft_held_to_the_landed_law():
    """Drafts get no wider door for being temporary: undeclared knobs
    refuse naming the declared ones; a clean draft lands canonical-typed."""
    err, _ = workspace.draft_check("naive", {"k": 4, "temperature": 2})
    assert err and "temperature" in err and "k" in err
    err, clean = workspace.draft_check("advanced", {"wide_factor": "3"})
    assert err is None and clean == {"wide_factor": 3}


def test_draft_hash_is_content_addressed():
    a = workspace.draft_hash({"k": 9})
    assert a == workspace.draft_hash({"k": 9})
    assert a != workspace.draft_hash({"k": 8})
    assert a.startswith("sha256:")


def test_synthetic_head_swaps_in_memory_and_reads_back():
    """The experiment's proven trick at the variant layer: the synthetic
    row outranks the landed head for one disposable node, and the profile
    reads back exactly — nothing written, nothing untraceable."""
    landed = dict(workspace.synthetic_head("naive", {"k": 6}),
                  received_at="2026-01-01T00:00:00Z")

    class _N:
        records = {}
    n = _N()
    n.records["real"] = landed
    n.records["synthetic:draft-head"] = workspace.synthetic_head(
        "naive", {"k": 2})
    row = improver.active_asset(n, "variant-naive")
    assert row and row[0] == "synthetic:draft-head"
    assert improver._profile_of(row[1]) == {"k": 2}
    assert variants.config("naive", improver._profile_of(row[1])) == {"k": 2}
