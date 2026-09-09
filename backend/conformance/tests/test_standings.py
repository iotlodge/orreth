# PROVENANCE: Claude Fable 5 (claude-fable-5) — 0066 sp4, the standings' suite · 2026-09-09
"""The scoreboard reports and never referees: rebuildable, purge-reachable,
veto-refusing; the replay panels every arm; the generator stages on clear
evidence and refuses thin — it never applies anything."""
import json

from orreth_sim import (crypto, dispatcher, provisioner, stacks, standings,
                        tournament, variants)
from orreth_sim.node import make_memory


def _floor():
    prov = provisioner.provision(provisioner.second_brain_template(), "t")
    fld = prov.fields["desk"]
    b = prov.beckys["u:t/e:life/f:desk"]
    lib, kp = b.issue_identity("instance", "u:t/e:life/f:desk", resident=True)
    stacks.plant_eco_assets(fld, lib, kp)
    stacks.ingest(fld, lib, kp, "rammed-earth",
                  "Rammed earth walls breathe with the seasons and hold "
                  "the day's heat through the night.")
    return fld, lib, kp


_SEQ = [0]


def _replay_rec(lib, kp, scope, kind, arms):
    _SEQ[0] += 1                       # distinct asks — content-addressed ids
    return make_memory(lib, kp, scope,
                       {"replay": {"asked": f"q{_SEQ[0]}", "kind": kind,
                                   "chosen": "naive", "arms": arms}},
                       kind="episodic", tags=["replay", "ask"])


def _exchange(lib, kp, scope, *, variant="naive", score=0.6, thumb=None,
              fld=None, choice=None):
    body = {"ask": {"asked": "q", "reply": "a", "variant": variant,
                    "signals": {"retrieval": score, "faithfulness": score,
                                "answer": score, "coverage": score}}}
    rec = make_memory(lib, kp, scope, body, kind="episodic",
                      tags=["ask", f"variant:{variant}"])
    if choice:
        rec["derived_from"] = [choice]
    return rec


def test_the_board_rebuilds_identical_and_purge_reaches():
    fld, lib, kp = _floor()
    fld.write(_replay_rec(lib, kp, fld.scope, "relational",
                          {"graph": {"retrieval": .8, "faithfulness": .8,
                                     "answer": .8, "coverage": .8}}))
    b1 = standings.build(fld.records)
    b2 = standings.build(fld.records)
    assert b1 == b2 and "relational·graph" in b1
    doomed = next(r for r in fld.records
                  if "replay" in (fld.records[r].get("tags") or []))
    fld.records.pop(doomed)
    assert "relational·graph" not in standings.build(fld.records), \
        "a purged record leaves the board in the same breath"


def test_intervals_are_ordered_and_narrow_with_volume():
    fld, lib, kp = _floor()
    for _ in range(3):
        fld.write(_replay_rec(lib, kp, fld.scope, "plain",
                              {"hyde": {"retrieval": .7, "faithfulness": .7,
                                        "answer": .7, "coverage": .7}}))
    thin = standings.build(fld.records)["plain·hyde"]
    for _ in range(30):
        fld.write(_replay_rec(lib, kp, fld.scope, "plain",
                              {"hyde": {"retrieval": .7, "faithfulness": .7,
                                        "answer": .7, "coverage": .7}}))
    thick = standings.build(fld.records)["plain·hyde"]
    assert thin["low"] <= thin["mean"] <= thin["high"]
    assert (thick["high"] - thick["low"]) < (thin["high"] - thin["low"]), \
        "the credible band narrows as the evidence grows"


def test_a_vetoed_sample_is_refused_never_averaged():
    fld, lib, kp = _floor()
    d = dispatcher.dispatch(fld, lib, kp, "a plain question")
    ex = _exchange(lib, kp, fld.scope, score=0.9, choice=d["record"])
    fld.write(ex)
    from orreth_sim import thumb as thumb_mod
    verdict, _ = thumb_mod.make_thumb(lib, kp, fld.scope, of=ex["id"],
                                      up=False, text="wrong")
    fld.write(verdict)
    cell = standings.build(fld.records).get("plain·naive")
    assert cell and cell["n"] == 0 and cell["vetoed"] == 1, \
        "the human's veto is counted aside — never in the arithmetic (L3)"


def test_the_replay_panels_every_arm_deterministically():
    fld, lib, kp = _floor()
    rows = [variants.row_for(s) for s in ("naive", "advanced", "graph")]
    body = standings.counterfactual(fld, "how do walls hold heat?", "plain",
                                    "naive", tournament.answer_as, rows)
    again = standings.counterfactual(fld, "how do walls hold heat?", "plain",
                                     "naive", tournament.answer_as, rows)
    assert body == again, "zero serving risk, zero dice"
    arms = body["replay"]["arms"]
    assert set(arms) == set(rows)
    for bench in arms.values():
        assert set(bench) == {"retrieval", "faithfulness", "answer",
                              "coverage"}, "bench-only — latency and thumbs "\
                                           "are honestly out of replay's reach"


def _clear_winner_board(fld, lib, kp):
    for _ in range(standings.MIN_N + 2):
        fld.write(_replay_rec(lib, kp, fld.scope, "relational",
                              {"hybrid": {"retrieval": .9, "faithfulness": .9,
                                          "answer": .9, "coverage": .9},
                               "graph": {"retrieval": .2, "faithfulness": .2,
                                         "answer": .2, "coverage": .2}}))
    return standings.build(fld.records)


def test_the_generator_stages_on_clear_evidence_and_never_applies():
    fld, lib, kp = _floor()
    board = _clear_winner_board(fld, lib, kp)
    p = standings.propose(board, dispatcher.STANDARD_V1)
    assert p and p["changes"] == {"relational": "hybrid"}
    staged = p["standard"]
    assert staged["version"].endswith("+standings")
    route = next(r for r in staged["rules"] if r["when"] == "relational")
    assert route["route"] == "hybrid" and "standings" in route["why"]
    assert p["evidence"]["relational"]["challenger"]["hybrid"]["low"] > \
        p["evidence"]["relational"]["incumbent"]["graph"]["high"], \
        "the conservative test: the challenger's floor above the " \
        "incumbent's ceiling"
    assert dispatcher.STANDARD_V1["rules"][1]["route"] == "graph", \
        "NOTHING was applied — the proposal is a staged argument, only"


def test_the_generator_refuses_thin_evidence():
    fld, lib, kp = _floor()
    fld.write(_replay_rec(lib, kp, fld.scope, "relational",
                          {"hybrid": {"retrieval": .9, "faithfulness": .9,
                                      "answer": .9, "coverage": .9},
                           "graph": {"retrieval": .2, "faithfulness": .2,
                                     "answer": .2, "coverage": .2}}))
    assert standings.propose(standings.build(fld.records),
                             dispatcher.STANDARD_V1) is None, \
        "one sample argues nothing — thin evidence refuses"


def test_an_unmeasured_incumbent_refuses_too():
    fld, lib, kp = _floor()
    for _ in range(standings.MIN_N + 2):
        fld.write(_replay_rec(lib, kp, fld.scope, "media",
                              {"hyde": {"retrieval": .9, "faithfulness": .9,
                                        "answer": .9, "coverage": .9}}))
    assert standings.propose(standings.build(fld.records),
                             dispatcher.STANDARD_V1) is None, \
        "a challenger cannot beat an incumbent nobody measured"
