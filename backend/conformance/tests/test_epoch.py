# PROVENANCE: Fable 5 (claude-fable-5) — 0041 sim-lift (road step 2) · 2026-07-26
"""The Epoch (0041) — the machinery, under conformance.

Under test: the machine takes its first name without accusing (genesis); a
held machine cuts no epoch; the epoch turns behind a word and stays quiet; a
Canon that moved with no adoption yields a staged finding wearing no levers;
the word is dated by its landing, never its submission second (the req-322
lesson); an unreadable gate never accuses in the dark; the revert restores a
sibling and erases nothing; THE SILENCE after a cited revert (the drill's
assertion); lag is amber, loud once, never wearing the revert's label; the
universe's epoch cites its floors' heads."""
import pytest
from datetime import datetime, timezone

from orreth_sim import epoch, improver, provisioner


def _iso(ts: float) -> str:
    return datetime.fromtimestamp(ts, tz=timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%SZ")


def _floor():
    prov = provisioner.provision(provisioner.second_brain_template(), "t")
    fld = prov.fields["desk"]
    b = prov.beckys["u:t/e:life/f:desk"]
    seat, kp = b.issue_identity("instance", "u:t/e:life/f:desk", resident=True)
    return fld, seat, kp


def _plant(fld, seat, kp, *, name="routing-standard", default="naive"):
    rec = improver.make_asset(seat, kp, fld.scope, name=name,
                              profile={"default": default})
    return fld.write(rec)


def _word(kind="improvement", *, submitted=100, landed=None):
    r = {"id": f"req-3-{int(submitted)}", "kind": kind, "status": "done",
         "result": {}}
    if landed is not None:
        r["result"]["resolved_at"] = _iso(landed)
    return r


def test_the_machine_takes_its_first_name():
    fld, seat, kp = _floor()
    _plant(fld, seat, kp)
    cut = epoch.cut_epoch(fld, seat, kp, requests=[], now=1000.0)
    assert cut["turned"]
    assert cut["drift"] is None                      # genesis never accuses
    eid, body = epoch.standing_epoch(fld)
    assert eid == cut["id"] and body["parent"] is None
    assert "routing-standard" in body["assets"]


def test_a_held_machine_cuts_no_epoch():
    fld, seat, kp = _floor()
    _plant(fld, seat, kp)
    first = epoch.cut_epoch(fld, seat, kp, requests=[], now=1000.0)
    before = len(fld.records)
    held = epoch.cut_epoch(fld, seat, kp, requests=[], now=1100.0)
    assert not held["turned"] and held["id"] == first["id"]
    assert len(fld.records) == before                # no news, no record


def test_the_epoch_turns_behind_a_word_and_stays_quiet():
    fld, seat, kp = _floor()
    _plant(fld, seat, kp)
    epoch.cut_epoch(fld, seat, kp, requests=[], now=1000.0)
    _plant(fld, seat, kp, default="router")          # the Canon moves…
    cut = epoch.cut_epoch(fld, seat, kp, now=1500.0,
                          requests=[_word(landed=1400)])   # …behind a word
    assert cut["turned"] and cut["drift"] is None
    assert "assets.routing-standard" in cut["changed"]


def test_drift_wears_no_levers():
    fld, seat, kp = _floor()
    v1 = _plant(fld, seat, kp)
    epoch.cut_epoch(fld, seat, kp, requests=[], now=1000.0)
    rogue = _plant(fld, seat, kp, default="rogue")   # no adoption behind it
    cut = epoch.cut_epoch(fld, seat, kp, requests=[], now=2000.0)
    assert cut["turned"] and cut["drift"] is not None
    assert cut["drift"]["restore"] == {"routing-standard": v1}
    fp = epoch.machine_fingerprint(fld)              # staged, never enacted:
    assert fp["assets"]["routing-standard"] == rogue  # the rogue head stands


def test_the_word_is_dated_by_its_landing():
    slow = _word(submitted=100, landed=1900)         # the gate waited (req-322)
    assert epoch.gate_word_recent([slow], now=2000.0)
    legacy = _word(submitted=100)                    # pre-stamp: submission second
    assert not epoch.gate_word_recent([legacy], now=2000.0)
    assert epoch.gate_word_recent([legacy], now=500.0)
    stale = _word(submitted=100, landed=200)
    assert not epoch.gate_word_recent([stale], now=2000.0)
    ask = _word(kind="ask", submitted=1990)          # conversation never hides drift
    assert not epoch.gate_word_recent([ask], now=2000.0)


def test_the_dark_gate_accuses_no_one():
    assert epoch.gate_word_recent(None, now=1e9)
    fld, seat, kp = _floor()
    _plant(fld, seat, kp)
    epoch.cut_epoch(fld, seat, kp, requests=[], now=1000.0)
    _plant(fld, seat, kp, default="rogue")
    cut = epoch.cut_epoch(fld, seat, kp, requests=None, now=2000.0)
    assert cut["turned"] and cut["drift"] is None    # never in the dark


def test_the_revert_restores_a_sibling_never_erases():
    fld, seat, kp = _floor()
    v1 = _plant(fld, seat, kp)
    rogue = _plant(fld, seat, kp, default="rogue")
    with pytest.raises(ValueError):                  # auto-revert stays refused
        epoch.revert_to_sibling(fld, seat, kp, name="routing-standard",
                                from_ref=v1, human_word=False)
    sib = epoch.revert_to_sibling(fld, seat, kp, name="routing-standard",
                                  from_ref=v1, human_word=True)
    assert improver._profile_of(fld.records[sib])["default"] == "naive"
    assert epoch._body(fld.records[sib])["asset"]["adopted_from"] == v1
    assert rogue in fld.records                      # outranked, never erased
    assert epoch.machine_fingerprint(fld)["assets"]["routing-standard"] == sib


def test_the_silence_after_the_revert():
    fld, seat, kp = _floor()
    v1 = _plant(fld, seat, kp)
    epoch.cut_epoch(fld, seat, kp, requests=[], now=1000.0)
    _plant(fld, seat, kp, default="rogue")
    cut = epoch.cut_epoch(fld, seat, kp, requests=[], now=2000.0)
    assert cut["drift"] is not None                  # the finding staged
    epoch.revert_to_sibling(fld, seat, kp, name="routing-standard",
                            from_ref=v1, human_word=True)
    word = _word(kind="drift", submitted=2000, landed=2100)
    after = epoch.cut_epoch(fld, seat, kp, requests=[word], now=2110.0,
                            pending_revert={"routing-standard": v1})
    assert after["turned"] and after["drift"] is None      # THE SILENCE
    _, body = epoch.standing_epoch(fld)
    assert body["revert_of"] == {"routing-standard": v1}   # the citation kept


def test_lag_is_amber_then_loud_once():
    st: dict = {}
    lag = dict(declared="sha256:law", sworn="sha256:old", state=st)
    assert epoch.reconcile_lag(**lag, now=0.0) == "amber"
    assert epoch.reconcile_lag(**lag, now=500.0) == "amber"
    assert epoch.reconcile_lag(**lag, now=1000.0) == "stage"
    assert epoch.reconcile_lag(**lag, now=2000.0) == "amber"   # loud ONCE
    assert epoch.reconcile_lag(declared="sha256:law", sworn="sha256:law",
                               state=st, now=2100.0) == "converged"
    assert not st                                    # the slate wiped for next time


def test_the_universe_cites_its_floors():
    fld, seat, kp = _floor()
    floors = {"u:t/e:life/f:desk": "sha256:aaa"}
    epoch.cut_epoch(fld, seat, kp, requests=[], now=100.0, floors=floors)
    held = epoch.cut_epoch(fld, seat, kp, requests=[], now=200.0, floors=floors)
    assert not held["turned"]
    cut = epoch.cut_epoch(fld, seat, kp, requests=[], now=300.0,
                          floors={"u:t/e:life/f:desk": "sha256:bbb"})
    assert cut["turned"]
    assert "floors.u:t/e:life/f:desk" in cut["changed"]
    assert cut["drift"] is None      # a floor's turn is never asset drift here


def test_the_epoch_knows_the_experiments_word():
    """0043 sp4's lesson, made law: an experiment's promotion IS an adoption —
    the Canon moving behind an approved rollout accuses no one. The first
    live rollout was falsely accused because this word was missing; JB left
    the honest accusation on record and the vocabulary grew."""
    fld, seat, kp = _floor()
    _plant(fld, seat, kp)
    epoch.cut_epoch(fld, seat, kp, requests=[], now=1000.0)
    _plant(fld, seat, kp, default="hybrid")          # the Canon moves…
    word = _word(kind="experiment", landed=1400)     # …behind a clicked rollout
    cut = epoch.cut_epoch(fld, seat, kp, now=1500.0, requests=[word])
    assert cut["turned"] and cut["drift"] is None    # recognized, quiet
    assert "assets.routing-standard" in cut["changed"]


def test_the_epoch_knows_the_craft_edits_word():
    """0050 sp2's lesson, made law: a craft-edit through the one-motion door
    IS an adoption — the request is the human's word (0045 sp2), so thirteen
    plain-speech sentence siblings must accuse no one. The first plain-speech
    pass was honestly accused because this word was missing; the accusation
    stayed on record and the vocabulary grew — «experiment»'s exact lesson,
    relearned for speech."""
    fld, seat, kp = _floor()
    _plant(fld, seat, kp)
    epoch.cut_epoch(fld, seat, kp, requests=[], now=1000.0)
    _plant(fld, seat, kp, default="hybrid")          # the Canon moves…
    word = _word(kind="craft-edit", landed=1400)     # …behind a one-motion edit
    cut = epoch.cut_epoch(fld, seat, kp, now=1500.0, requests=[word])
    assert cut["turned"] and cut["drift"] is None    # recognized, quiet
