# PROVENANCE: authored by Fable 5 (claude-fable-5), 2026-07-14 — 0034, the Continuity Universe
"""The continuity template (0034 §7 sp1): the label canon is structural, the
retention regime is law on the substrate, and the provisioner renders the
template — a floor is born wearing its dignity."""
import json

import pytest

from orreth_sim import continuity, crypto, parlor, shipyard
from orreth_sim.node import make_memory
from orreth_sim.world import build


@pytest.fixture()
def world():
    return build()


def _body(rec):
    return json.loads(crypto._b64d(rec["body"]).decode())


def test_the_label_canon_speaks_from_the_state():
    """0034 §3: honest confidence in human words — the sentence shape comes off
    the record's state; a mind cannot upgrade confidence the substrate doesn't
    hold, and the recalled are never spoken as memory."""
    say = continuity.speak_claim
    assert say("verified", "on May 12th you visited Anna") \
        == "on May 12th you visited Anna"               # say it plainly
    assert say("trusted", "my sister is Anna") == "my sister is Anna"
    corr = say("corroborated", "you were at the coast in May",
               sources=["the photos", "your calendar"])
    assert "the photos, your calendar" in corr           # show the receipts
    hedged = say("untrusted", "this trip happened in May 2024", hints=2)
    assert hedged.startswith("this MAY be so") and "not proof" in hedged
    assert say("investigating", "the address changed") \
        .startswith("I'm re-checking")                   # doubt out loud
    assert say("recalled", "a poisoned claim") is None   # the dead never speak


def test_the_regime_is_law_on_the_substrate(world):
    """0034 §2 through 0033 §5: identity at λ≈0 and medication zero-D — the
    intolerables ride every distillation with their sources cited, while the
    narrative compresses away. The template is physics, not preference."""
    f = world.field_prod
    continuity.apply(f)
    me = {"did": f.steward["did"], "scope": f.scope}
    ids = []
    for who, rel in (("Michael", "your neighbor"), ("Anna", "your sister")):
        rec = make_memory(me, f.steward_kp, f.scope,
                          {"name": who, "relationship": rel,
                           "narrative": "a long visit remembered warmly " * 10},
                          kind="semantic", tags=["identity"])
        ids.append(f.write(rec))
    dist = f._distill(ids, push=False)
    body = _body(dist)
    assert {e["value"] for e in body["preserved"]["name"]} == {"Michael", "Anna"}
    assert {e["value"] for e in body["preserved"]["relationship"]} \
        == {"your neighbor", "your sister"}
    assert "narrative" not in body["preserved"]          # the compressible compresses
    assert dist["method"]["contract"]["distortion_bound"] == 0.0   # λ≈0, pinned in METHOD (the gate)


def test_the_provisioner_renders_the_template():
    """0034 §7 sp1: plan(template="continuity") dresses every profile — the
    dignity vector (summing to 1.0, unsupported-memory heaviest), the regime,
    the canon; an unknown template is refused by name."""
    from orreth_sim.schemas import validate
    p = shipyard.plan("u:demo", "care", ["home"], set(), "did:web:test",
                      template="continuity")
    assert p["summary"].startswith("a continuity e:care")
    for spec in (p["eco"], p["fields"][0]):
        prof = spec["profile"]
        assert spec["template"] == "continuity"
        weights = [o["weight"] for o in prof["objective"]]
        assert abs(sum(weights) - 1.0) < 1e-9
        assert prof["objective"][0]["objective"] == "unsupported-memory-rate"
        assert prof["memory"]["distilled_retention"] == "P3650D"
        # the Phase D gate (JB 2026-07-15): the dials and the template block
        # are contracts/v0-LEGAL — the overlaid profile validates whole
        validate(prof, "tier-profile.schema.json")
        assert prof["memory"]["review_interval"] == "P30D"
        t = prof["template"]
        assert t["name"] == "continuity" and t["layout"] == "brain"
        assert t["distortion_contracts"]["identity"]["distortion_bound"] == 0.0
        assert t["label_canon"]["recalled"] == "never spoken as memory"
        assert set(t["brain_regions"]) == {"prefrontal", "temporal",
                                           "parietal", "occipital",
                                           "cerebellar", "limbic"}
    # a plain plan is untouched — the template never leaks
    plain = shipyard.plan("u:demo", "plain", [], set(), "did:web:test")
    assert "template" not in plain["eco"]
    assert "template" not in plain["eco"]["profile"]
    validate(plain["eco"]["profile"], "tier-profile.schema.json")
    with pytest.raises(ValueError):
        shipyard.plan("u:demo", "x", [], set(), "did:web:test", template="bogus")


def test_the_parlor_hears_the_template():
    """0034 §7 sp1 at becky's door: "create continuity ecosystem …" stages with
    the template named, verbatim; plain grows keep their shape."""
    tpl, plain = parlor.grow_template(
        "create continuity ecosystem care with fields home")
    assert tpl == "continuity"
    assert parlor.parse_grow(plain) == ("care", ["home"])
    assert parlor.grow_template("create ecosystem care") == (None,
                                                             "create ecosystem care")
    ans = parlor.answer("becky",
                        "create continuity ecosystem care with fields home", {})
    assert ans["action"] == "ecosystem" and ans["template"] == "continuity"
    assert ans["verbatim"] is True and "continuity template" in ans["reply"]
    ans2 = parlor.answer("becky", "create ecosystem plain as is", {})
    assert ans2["action"] == "ecosystem" and "template" not in ans2


def test_the_role_bundles_hold_the_law():
    """0034 §4: six roles, domain-scoped — a caregiver sees routines and
    medication, never journals; NO bundle ever carries the sealed classes, and
    the technician never touches memory content."""
    assert set(continuity.ROLE_BUNDLES) == {"partner", "caregiver", "clinician",
                                            "guardian", "emergency", "technician"}
    care = continuity.ROLE_BUNDLES["caregiver"]["domains"]
    assert care == ["routines", "medication"] and "journals" not in care
    for role, b in continuity.ROLE_BUNDLES.items():
        assert "sealed" not in b["domains"]
    assert continuity.ROLE_BUNDLES["technician"]["domains"] == ["telemetry"]


def test_consent_is_dynamic_windowed_and_revocable(world):
    """0034 §4: purpose-, modality-, time-bound, revocable — a worldline whose
    head rules; the token gate mints nothing without a live consent."""
    f = world.field_prod
    me = {"did": f.steward["did"], "scope": f.scope}
    rec = continuity.make_consent(me, f.steward_kp, f.scope,
                                  purpose="help with medication",
                                  role="caregiver", holder="did:key:zCare",
                                  window_days=30, approved_ref="req-9")
    f.write(rec)
    rows = [{"id": rid, "consent": _body(r)["consent"],
             "derived_from": r.get("derived_from") or [], "at": r["received_at"]}
            for rid, r in f.records.items() if "consent" in r.get("tags", [])]
    heads = continuity.consent_heads(rows)
    assert len(heads) == 1 and heads[0]["posture"] == "granted"
    now = heads[0]["window"]["from"]
    assert continuity.may_read(heads, "caregiver", "medication", now)
    assert not continuity.may_read(heads, "caregiver", "journals", now)
    terms = continuity.token_terms(heads, "caregiver", f.scope, now)
    assert terms["expiry"] == heads[0]["window"]["until"]
    assert terms["grants"] == [{"action": "retrieve", "space": {"scope": f.scope}}]
    # past the window, the same consent mints nothing — time bounds the word
    assert continuity.token_terms(heads, "caregiver", f.scope,
                                  "2099-01-01T00:00:00Z") is None
    # revocation: a sibling on the worldline — the head flips, nothing vanishes
    sib = make_memory(me, f.steward_kp, f.scope,
                      continuity.revoke_body(heads[0], "circumstances changed"),
                      kind="semantic", tags=["consent"])
    sib["derived_from"] = [heads[0]["id"]]
    f.write(sib)
    rows = [{"id": rid, "consent": _body(r)["consent"],
             "derived_from": r.get("derived_from") or [], "at": r["received_at"]}
            for rid, r in f.records.items() if "consent" in r.get("tags", [])]
    heads = continuity.consent_heads(rows)
    assert len(heads) == 1 and heads[0]["posture"] == "revoked"
    assert continuity.token_terms(heads, "caregiver", f.scope, now) is None
    assert rec["id"] in f.records                        # history intact


def test_safer_mode_is_a_posture():
    """0034 §4: the template's default consents recording; an explicit revoked
    head drops the organ to safer mode; a later granted head restores it."""
    now = "2026-07-14T00:00:00Z"
    win = {"from": "2026-07-01T00:00:00Z", "until": "2026-08-01T00:00:00Z"}
    assert continuity.recording_allowed([], "conversation", now)      # default on
    revoked = {"modalities": ["conversation"], "posture": "revoked"}
    assert not continuity.recording_allowed([revoked], "conversation", now)
    assert continuity.recording_allowed([revoked], "photo", now)      # scoped
    regranted = {"modalities": ["conversation"], "posture": "granted",
                 "window": win}
    assert continuity.recording_allowed([revoked, regranted], "conversation", now)
    assert not continuity.recording_allowed(
        [revoked, regranted], "conversation", "2099-01-01T00:00:00Z")  # window ends


def test_beckys_consent_doors():
    """0034 §4 at the card: a grant STAGES verbatim with its bundle readable;
    revocation and safer mode act NOW; the ledger speaks its worldlines."""
    grant = parlor.answer("becky",
                          "grant caregiver access to help with medication for 14 days",
                          {"scope": "u:demo"})
    assert grant["action"] == "consent-grant" and grant["role"] == "caregiver"
    assert grant["days"] == 14 and grant["purpose"] == "help with medication"
    assert grant["verbatim"] is True
    assert "routines · medication" in grant["reply"]
    assert "the sealed never delegates" in grant["reply"]
    rev = parlor.answer("becky", "revoke caregiver access", {"scope": "u:demo"})
    assert rev["action"] == "consent-revoke" and rev["role"] == "caregiver"
    stop = parlor.answer("becky", "stop recording conversations", {"scope": "u:demo"})
    assert stop["action"] == "consent-revoke" and stop["modality"] == "conversation"
    assert "safer mode" in stop["reply"]
    resume = parlor.answer("becky", "resume recording conversations",
                           {"scope": "u:demo"})
    assert resume["action"] == "consent-grant" and resume["modality"] == "conversation"
    assert "gate" in resume["reply"]      # resuming a recording is a consequence
    ledger = parlor.answer("becky", "show consents",
                           {"scope": "u:demo",
                            "consents": [{"role": "caregiver", "holder": "did:key:zC",
                                          "posture": "granted",
                                          "window": {"until": "2026-08-13T00:00:00Z"},
                                          "domains": ["routines", "medication"],
                                          "purpose": "help with medication"}]})
    assert ledger["verbatim"] is True
    assert "caregiver" in ledger["reply"] and "granted" in ledger["reply"]
    assert "until 2026-08-13" in ledger["reply"]


def test_the_charter_is_config_as_memory(world):
    """R8: the floor's law on its own record — template, vector, regime, canon,
    legible to the glass and to every resident."""
    f = world.field_prod
    me = {"did": f.steward["did"], "scope": f.scope}
    rec = continuity.make_charter(me, f.steward_kp, f.scope)
    assert "continuity-charter" in rec["tags"]
    ch = _body(rec)["continuity_charter"]
    assert ch["template"] == "continuity"
    assert ch["regime"]["medication"]["contract"]["must_preserve"] \
        == ["dosage", "timing"]
    assert ch["regime"]["location"]["retention"] == "PT10M"
    assert ch["label_canon"]["untrusted"] == "hedged honestly — may, never definitely"
