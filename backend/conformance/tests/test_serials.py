# PROVENANCE: authored by Fable 5 (claude-fable-5), 2026-07-14 — 0032, the Serials Desk
"""The subscription is the human's standing word (0032 §1): minted only from an
approved ask, cancelled as a sibling version, never an absence."""
import pytest

from orreth_sim import parlor, serials
from orreth_sim.world import build


@pytest.fixture()
def world():
    return build()


def test_subscription_mints_lists_and_cancels_on_the_record(world):
    f = world.field_prod
    me = {"did": f.steward["did"], "scope": f.scope}
    rec = serials.make_subscription(me, f.steward_kp, f.scope,
                                    topic="timber joinery standards",
                                    approved_ref="req-42")
    f.write(rec)
    subs = serials.subscriptions(f)
    assert len(subs) == 1
    s = subs[0]
    assert s["topic"] == "timber joinery standards"
    assert s["posture"] == "deliver" and s["approved"] == "req-42"
    assert s["cadence_beats"] == 100 and s["budget"] == {"calls": 4}
    # cancellation is a sibling on the worldline — retired, never absent
    new_id = serials.set_posture(f, me, f.steward_kp,
                                 "timber joinery standards", "cancelled",
                                 reason="the human closed it")
    assert new_id is not None
    subs = serials.subscriptions(f)
    assert len(subs) == 1 and subs[0]["posture"] == "cancelled"
    assert rec["id"] in f.records                         # history intact
    assert serials.set_posture(f, me, f.steward_kp, "never existed",
                               "cancelled") is None


def test_the_desk_doors_stage_and_cancel_verbatim():
    """0032 §1 through 0020: subscribing STAGES (a standing spend waits at the
    gate); unsubscribing acts (stopping a spend needs no gate)."""
    facts = {"scope": "u:demo"}
    sub = parlor.answer("librarian", "subscribe to building codes", facts)
    assert sub["action"] == "subscribe" and sub["topic"] == "building codes"
    assert sub["verbatim"] is True and "consequence waits" in sub["reply"]
    un = parlor.answer("librarian", "unsubscribe from building codes", facts)
    assert un["action"] == "unsubscribe" and un["topic"] == "building codes"
    desk = parlor.answer("librarian",
                         "show the desk",
                         {"scope": "u:demo",
                          "subscriptions": [{"topic": "building codes",
                                             "posture": "deliver",
                                             "cadence_beats": 100}]})
    assert "building codes — deliver" in desk["reply"]


def test_the_desk_panel_in_her_room():
    facts = {"scope": "u:demo", "residents": [],
             "subscriptions": [{"topic": "building codes", "posture": "deliver",
                                "cadence_beats": 100, "budget": {"calls": 4}}]}
    ws = parlor.workspace("librarian", facts)
    panel = next(p for p in ws["panels"] if "serials desk" in p["title"])
    assert panel["items"][0]["text"] == "building codes"
    assert "every 100 beats" in panel["items"][0]["meta"]
