# PROVENANCE: Fable 5 (claude-fable-5) — 0038, the Stacks · 2026-07-22
"""The Stacks (0038) sp4 part 2: the tournament under test.

Under test: all seven rows answer through one door; the grading is
deterministic and rewards cited coverage; the standings rank with floors
flagged never averaged away; the promotion is a PROPOSAL carrying evidence —
never an enactment; the swarm recomposes with citations; the multimodal row
is honest about its waiting eye."""
from orreth_sim import provisioner, stacks, tournament


def _floor():
    prov = provisioner.provision(provisioner.second_brain_template(), "t")
    fld = prov.fields["desk"]
    b = prov.beckys["u:t/e:life/f:desk"]
    lib, kp = b.issue_identity("instance", "u:t/e:life/f:desk", resident=True)
    stacks.plant_eco_assets(fld, lib, kp)
    stacks.ingest(fld, lib, kp, "rammed-earth",
                  "Rammed earth walls are compacted soil formed in lifts. "
                  "Packed soil holds heat through the day and releases it at "
                  "night, breathing with the seasons.")
    stacks.ingest(fld, lib, kp, "lime-plaster",
                  "Lime plaster finishes protect rammed earth walls from rain "
                  "while letting moisture escape the soil.")
    return fld, lib, kp


QS = ["how are walls connected to the seasons?",
      "what exactly protects walls from rain?",
      "compare rammed earth and lime plaster"]


def test_seven_rows_one_door():
    fld, _, _ = _floor()
    for f in tournament.FLAVORS:
        a = tournament.answer_as(fld, f, QS[0])
        assert a["flavor"] == f and "answer" in a
    # the honest eye: no media on the shelf, and the row says so
    mm = tournament.answer_as(fld, "multimodal", QS[0])
    assert mm["citations"] == [] and "vision mind" in mm["answer"]
    # the swarm recomposes WITH citations
    sw = tournament.answer_as(fld, "swarm", QS[2])
    assert sw["citations"]


def test_grading_is_deterministic_and_rewards_coverage():
    fld, _, _ = _floor()
    a = tournament.answer_as(fld, "hybrid", QS[0])
    g1, g2 = (tournament.grade(fld, QS[0], a) for _ in range(2))
    assert g1 == g2                                    # flows, not dice
    empty = {"answer": "an honest unknown", "citations": [], "flavor": "x"}
    assert tournament.grade(fld, QS[0], empty)["score"] == 0.0
    assert g1["score"] > 0.0


def test_standings_rank_and_floors_flag():
    fld, _, _ = _floor()
    r = tournament.run(fld, QS)
    assert [s["flavor"] for s in r["standings"]][0] == r["champion"]
    means = [s["mean"] for s in r["standings"]]
    assert means == sorted(means, reverse=True)
    mm = next(s for s in r["standings"] if s["flavor"] == "multimodal")
    assert mm["floors"] and "uncited" in mm["floors"][0]   # flagged, not hidden
    assert all(len(rd["entries"]) == 7 for rd in r["rounds"])


def test_promotion_is_a_proposal_with_evidence():
    fld, _, _ = _floor()
    r = tournament.run(fld, QS)
    p = tournament.promotion_proposal(r)
    assert p["version"] == "2-proposed" and p["default"] == r["champion"]
    assert set(p["built"]) == set(tournament.FLAVORS)
    assert "consequence waits at the gate" in p["evidence"]["note"]