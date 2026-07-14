# PROVENANCE: authored by Fable 5 (claude-fable-5), 2026-07-14 — 0032, the Serials Desk
"""The subscription is the human's standing word (0032 §1): minted only from an
approved ask, cancelled as a sibling version, never an absence. The delivery
beat (§2): dedup admits only the new — quarantined, lineage attached — one note
per sweep, and same voice twice is still one voice."""
import pytest

from orreth_sim import parlor, serials
from orreth_sim.node import make_memory
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
    # the ledger travels verbatim — a governed thought never rewrites the lane
    assert desk["verbatim"] is True
    # the cadence is a dial on the record (0032 §8): the human's own words set it
    dial = parlor.answer("librarian",
                         "subscribe to bitcoin price every 10 beats", facts)
    assert dial["topic"] == "bitcoin price" and dial["cadence"] == 10
    assert "every 10 beats" in dial["reply"]


def test_the_desk_panel_in_her_room():
    facts = {"scope": "u:demo", "residents": [],
             "subscriptions": [{"topic": "building codes", "posture": "deliver",
                                "cadence_beats": 100, "budget": {"calls": 4}}],
             "deliveries": [{"topic": "building codes", "issue": 2,
                             "arrived": ["a new clause"], "repeated": 3}]}
    ws = parlor.workspace("librarian", facts)
    panel = next(p for p in ws["panels"] if "serials desk" in p["title"])
    assert panel["items"][0]["text"] == "building codes"
    assert "every 100 beats" in panel["items"][0]["meta"]
    assert "issue 2 landed: 1 new · 3 repeated" in panel["items"][0]["meta"]


def _open_sub(f, topic: str) -> dict:
    """A subscription on the record, as the human's approval would mint it."""
    me = {"did": f.steward["did"], "scope": f.scope}
    f.write(serials.make_subscription(me, f.steward_kp, f.scope,
                                      topic=topic, approved_ref="req-7"))
    return me


def test_the_sweep_dedups_admits_quarantined_and_notes_the_issue(world):
    """0032 §2: new is admitted with the subscription's lineage; a repeat lands
    only on the note — same voice twice is still one voice (0014)."""
    f = world.field_prod
    topic = "timber joinery standards"
    me = _open_sub(f, topic)
    held = make_memory(me, f.steward_kp, f.scope,
                       {"knowledge": "mortise depth is one third the stile",
                        "source": {"did": "did:web:codes.example", "ref": "u://1"},
                        "state": "untrusted", "intent": topic},
                       kind="semantic", tags=["knowledge"])
    f.write(held)
    findings = [
        {"claim": "mortise depth is one third the stile",         # the repeat
         "ref": "u://1", "source_did": "did:web:codes.example"},
        {"claim": "dovetail pins now taper at 1:8",                # the news-stand's new
         "ref": "u://2", "source_did": "did:web:codes.example"},
    ]
    report = serials.sweep(f, me, f.steward_kp, f.scope,
                           topic=topic, findings=findings)
    assert report["issue"] == 1
    assert report["arrived"] == 1 and report["repeated"] == 1
    assert report["marker"] is None                # quiet — log, never a lane
    admitted = f.records[report["admitted"][0]]
    assert admitted["derived_from"] == [serials.find(f, topic)["id"]]
    import json as _json
    from orreth_sim import crypto as _crypto
    body = _json.loads(_crypto._b64d(admitted["body"]).decode())
    assert body["state"] == "untrusted"            # quarantined at 0.0000, always
    assert body["subscription"] == serials.find(f, topic)["id"]
    # the repeat promoted NOTHING: the held claim has no new version
    assert not any(held["id"] in r.get("derived_from", [])
                   for r in f.records.values())
    notes = serials.deliveries(f, topic)
    assert len(notes) == 1 and notes[0]["repeated"] == 1
    assert notes[0]["arrived"] == ["dovetail pins now taper at 1:8"]
    assert notes[0]["cost"] == {"calls": 1}
    # the same issue again: everything repeats, the note still lands — issue 2
    report2 = serials.sweep(f, me, f.steward_kp, f.scope,
                            topic=topic, findings=findings)
    assert report2["issue"] == 2
    assert report2["arrived"] == 0 and report2["repeated"] == 2


def test_the_cadence_and_postures_rule_the_due_check():
    """0032 §1–§2: the first issue arrives with the subscription; then cadence
    holds; paused and cancelled are never due — hibernation is a posture."""
    sub = {"posture": "deliver", "cadence_beats": 100}
    assert serials.is_due(sub, 0, False)           # the current issue starts you
    assert not serials.is_due(sub, 99, True)
    assert serials.is_due(sub, 100, True)
    assert not serials.is_due({"posture": "paused", "cadence_beats": 100}, 1000, True)
    assert not serials.is_due({"posture": "cancelled", "cadence_beats": 100}, 1000, False)


def test_news_wears_medium_and_the_note_carries_every_column():
    """0032 §2 rule 4: a quiet delivery is log; anything in the changed or
    vanished columns is news. The note carries all four columns from day one —
    spoonful 3 fills the last two."""
    assert not serials.news({"changed": [], "vanished": []})
    assert serials.news({"changed": ["the code moved"]})
    assert serials.news({"vanished": ["a clause is gone"]})
    parts = serials.dedup([{"claim": "x"}], [])
    assert set(parts) == {"new", "repeat", "changed", "vanished"}


def test_changed_at_source_admits_and_drops_the_old_head(world):
    """0032 §3: same source, same ref, different content — the new claim admits
    quarantined (its own record), the OLD head drops to 'investigating' with
    trigger superseded-at-source and the pair named. Nothing auto-supersedes."""
    f = world.field_prod
    topic = "timber joinery standards"
    me = _open_sub(f, topic)
    old = make_memory(me, f.steward_kp, f.scope,
                      {"knowledge": "the code allows 12mm dowels",
                       "source": {"did": "did:web:codes.example", "ref": "u://1"},
                       "state": "untrusted", "intent": topic},
                      kind="semantic", tags=["knowledge"])
    f.write(old)
    report = serials.sweep(f, me, f.steward_kp, f.scope, topic=topic,
                           findings=[{"claim": "the code now requires 16mm dowels",
                                      "ref": "u://1",
                                      "source_did": "did:web:codes.example"}],
                           source_did="did:web:codes.example")
    assert report["changed"] == 1 and report["arrived"] == 0
    assert report["marker"] is not None           # news — the medium lane
    # the new word stands as its own quarantined record
    import json as _json
    from orreth_sim import crypto as _crypto
    new_id = report["admitted"][0]
    nb = _json.loads(_crypto._b64d(f.records[new_id]["body"]).decode())
    assert nb["state"] == "untrusted"
    # the old head dropped — the walk's shape, the pair named
    assert len(report["dropped"]) == 1
    sib = f.records[report["dropped"][0]]
    assert sib["derived_from"] == [old["id"]]
    sb = _json.loads(_crypto._b64d(sib["body"]).decode())
    assert sb["state"] == "investigating"
    assert sb["revalidation"]["trigger"] == "superseded-at-source"
    assert new_id in sb["revalidation"]["reason"]
    # the note names the pair too
    note = serials.deliveries(f, topic)[-1]
    assert note["changed"][0]["supersedes"] == [old["id"]]


def test_vanished_is_a_finding_never_an_action(world):
    """0032 §2: a ref the sweep no longer carries is noted on the delivery —
    absence is a finding; no head drops, nothing is touched."""
    f = world.field_prod
    topic = "timber joinery standards"
    me = _open_sub(f, topic)
    old = make_memory(me, f.steward_kp, f.scope,
                      {"knowledge": "scarf joints span the ridge",
                       "source": {"did": "did:web:codes.example", "ref": "u://gone"},
                       "state": "untrusted", "intent": topic},
                      kind="semantic", tags=["knowledge"])
    f.write(old)
    report = serials.sweep(f, me, f.steward_kp, f.scope, topic=topic,
                           findings=[{"claim": "a fresh clause on purlins",
                                      "ref": "u://new",
                                      "source_did": "did:web:codes.example"}],
                           source_did="did:web:codes.example")
    assert report["vanished"] == 1 and report["marker"] is not None
    note = serials.deliveries(f, topic)[-1]
    assert note["vanished"][0]["claim"] == "scarf joints span the ridge"
    # noted, never acted on: the old head has no new version
    assert not any(old["id"] in r.get("derived_from", [])
                   for r in f.records.values())
    # and a voice from ANOTHER source never counts vanished (only the
    # subscribed voice can go quiet)
    other = make_memory(me, f.steward_kp, f.scope,
                        {"knowledge": "an unrelated word",
                         "source": {"did": "did:web:elsewhere", "ref": "u://x"},
                         "state": "untrusted", "intent": topic},
                        kind="semantic", tags=["knowledge"])
    f.write(other)
    report2 = serials.sweep(f, me, f.steward_kp, f.scope, topic=topic,
                            findings=[{"claim": "a fresh clause on purlins",
                                       "ref": "u://new",
                                       "source_did": "did:web:codes.example"}],
                            source_did="did:web:codes.example")
    vanished2 = [v["claim"] for v in serials.deliveries(f, topic)[-1]["vanished"]]
    assert "an unrelated word" not in vanished2


def test_doubt_never_stacks_on_an_investigating_head(world):
    """The walk's idempotence, kept (0031 §5): a head already investigating is
    not re-dropped when its ref changes again — the new word still admits."""
    f = world.field_prod
    topic = "timber joinery standards"
    me = _open_sub(f, topic)
    first = serials.sweep(f, me, f.steward_kp, f.scope, topic=topic,
                          findings=[{"claim": "v1 of the clause", "ref": "u://1",
                                     "source_did": "did:web:codes.example"}],
                          source_did="did:web:codes.example")
    assert first["arrived"] == 1
    second = serials.sweep(f, me, f.steward_kp, f.scope, topic=topic,
                           findings=[{"claim": "v2 of the clause", "ref": "u://1",
                                      "source_did": "did:web:codes.example"}],
                           source_did="did:web:codes.example")
    assert second["changed"] == 1 and len(second["dropped"]) == 1
    third = serials.sweep(f, me, f.steward_kp, f.scope, topic=topic,
                          findings=[{"claim": "v3 of the clause", "ref": "u://1",
                                     "source_did": "did:web:codes.example"}],
                          source_did="did:web:codes.example")
    # v3 contradicts v2 (a live head) — one drop; the v1 head, already
    # investigating, is never doubted twice
    assert third["changed"] == 1 and len(third["dropped"]) == 1


def test_a_dead_lineages_utterance_repeats_never_rewrites(world):
    """Content-addressed admission: the exact utterance the universe already
    holds (a recalled lineage's original) counts as a repeat — never a
    colliding re-write, and never a resurrection."""
    f = world.field_prod
    topic = "timber joinery standards"
    me = _open_sub(f, topic)
    sub_id = serials.find(f, topic)["id"]
    claim = "biscuit joints are out of the code"
    original = make_memory(me, f.steward_kp, f.scope,
                           {"knowledge": claim,
                            "source": {"did": "did:web:codes.example", "ref": "u://9"},
                            "state": "untrusted", "intent": topic,
                            "subscription": sub_id},
                           kind="semantic", tags=["knowledge", "delivered"],
                           provenance_class="ingested-archive")
    f.write(original)
    recall = make_memory(me, f.steward_kp, f.scope,
                         {"knowledge": claim, "state": "recalled", "intent": topic},
                         kind="semantic", tags=["knowledge", "recalled"])
    recall["derived_from"] = [original["id"]]
    f.write(recall)
    report = serials.sweep(f, me, f.steward_kp, f.scope, topic=topic,
                           findings=[{"claim": claim, "ref": "u://9",
                                      "source_did": "did:web:codes.example"}])
    assert report["arrived"] == 0 and report["repeated"] == 1
    assert report["admitted"] == []                # the dead stay dead (0022 §4)
