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


# ---- 0072 sp3 · the operate room's laws -------------------------------------------

def _ask_rec(rid, style, lat, at, draft=False, replay=False, asked="q"):
    from orreth_sim import crypto
    body = {"ask": {"asked": asked, "variant": style,
                    "signals": {"latency_ms": lat, "cost_chars": 100}}}
    if draft:
        body["ask"]["draft"] = {"hash": "sha256:d", "knobs": {"k": 9}}
    tags = ["ask", f"variant:{style}"] + (["replay"] if replay else [])
    return rid, {"tags": tags, "occurred_at": at,
                 "body": crypto._b64e(crypto.canonical(body))}


def test_monitor_folds_per_style_with_honest_percentiles():
    """Nearest-rank percentiles — at tiny n the room reports a real ask's
    number, never an interpolated invention; replay rows stay the bench's."""
    recs = dict([_ask_rec("a", "naive", 100, "2026-09-11T01:00:00Z"),
                 _ask_rec("b", "naive", 300, "2026-09-11T02:00:00Z"),
                 _ask_rec("c", "naive", 200, "2026-09-11T03:00:00Z"),
                 _ask_rec("d", "advanced", 500, "2026-09-11T04:00:00Z",
                          draft=True),
                 _ask_rec("e", "naive", 999, "2026-09-11T05:00:00Z",
                          replay=True)])
    m = workspace.monitor_fold(recs)
    assert m["asks"] == 4                       # the replay row never counted
    nv = m["styles"]["naive"]
    assert nv["asks"] == 3 and nv["p50_ms"] == 200.0 and nv["p95_ms"] == 300.0
    assert m["styles"]["advanced"]["drafts"] == 1
    assert nv["last_at"] == "2026-09-11T03:00:00Z"


def test_monitor_recent_is_newest_first_and_every_row_a_door():
    recs = dict([_ask_rec("a", "naive", 100, "2026-09-11T01:00:00Z"),
                 _ask_rec("b", "hybrid", 200, "2026-09-11T09:00:00Z"),
                 _ask_rec("c", "naive", 150, "2026-09-11T05:00:00Z")])
    m = workspace.monitor_fold(recs)
    assert [r["ref"] for r in m["recent"]] == ["b", "c", "a"]
    assert all(r["ref"] and r["at"] for r in m["recent"])


# ---- 0072 sp5 · the enterprise laws -----------------------------------------------

def test_showback_folds_by_person_then_did_then_anonymous():
    from orreth_sim import crypto
    def rec(rid, by, person, chars):
        b = {"ask": {"asked": "q", "by": by, "variant": "naive",
                     "signals": {"latency_ms": 10, "cost_chars": chars}}}
        if person:
            b["ask"]["person"] = person
        return rid, {"tags": ["ask"], "occurred_at": "2026-09-12T01:00:00Z",
                     "body": crypto._b64e(crypto.canonical(b))}
    recs = dict([rec("a", "did:key:zjb", "jb", 500),
                 rec("b", "did:key:zjb", "jb", 300),
                 rec("c", "did:key:zother", "", 100),
                 rec("d", "anonymous-consumer", "", 50)])
    s = workspace.showback_fold(recs)
    assert s[0] == {"who": "jb", "asks": 2, "chars": 800,
                    "latency_ms": 20.0, "person": True}
    assert [x["who"] for x in s] == ["jb", "did:key:zother",
                                     "anonymous-consumer"]


def test_quota_teaches_within_the_sliding_hour_and_zero_is_off():
    rows = [{"kind": "ask", "did": "d1", "at": "2026-09-12T10:30:00Z"},
            {"kind": "ask", "did": "d1", "at": "2026-09-12T10:40:00Z"},
            {"kind": "ask", "did": "d1", "at": "2026-09-12T09:00:00Z"},  # aged out
            {"kind": "ask", "did": "d2", "at": "2026-09-12T10:45:00Z"},
            {"kind": "parlor", "did": "d1", "at": "2026-09-12T10:50:00Z"}]
    now = "2026-09-12T11:00:00Z"
    assert workspace.quota_check(rows, "d1", now, 3) is None      # 2 of 3
    why = workspace.quota_check(rows, "d1", now, 2)               # 2 of 2
    assert why and "2 per hour" in why and "dial" in why
    assert workspace.quota_check(rows, "d1", now, 0) is None      # off
    assert workspace.quota_check(rows, "d2", now, 2) is None      # not d1's

