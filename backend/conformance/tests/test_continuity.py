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


def test_the_testament_is_the_standing_word(world):
    """0035 §2: the human's word about the end — a worldline whose head rules,
    revisable to the last day; the §8 locks refuse at mint, loudly."""
    f = world.field_prod
    me = {"did": f.steward["did"], "scope": f.scope}
    rec = continuity.make_testament(me, f.steward_kp, f.scope,
                                    fates={"journals": "shred",
                                           "identity": "pass",
                                           "medication": "seal"},
                                    executor="did:key:zExec",
                                    heir="did:key:zKid",
                                    witnesses=["did:key:zWit"],
                                    silence_days=21,
                                    escrow={"journals": False},
                                    approved_ref="req-35")
    f.write(rec)

    def heads():
        rows = [{"id": rid, "testament": _body(r)["testament"],
                 "derived_from": r.get("derived_from") or [],
                 "at": r["received_at"]}
                for rid, r in f.records.items()
                if "testament" in r.get("tags", [])]
        rows.sort(key=lambda x: x["at"])
        return continuity.testament_heads(rows)

    h = heads()
    assert len(h) == 1 and h[0]["posture"] == "standing"
    assert h[0]["silence_window"]["days"] == 21
    assert h[0]["escrow"] == {"journals": False}
    # a revision is a sibling — the head flips, history stays
    rev = continuity.make_testament(me, f.steward_kp, f.scope,
                                    fates={"journals": "shred",
                                           "identity": "pass"},
                                    executor="did:key:zExec",
                                    heir="did:key:zKid",
                                    witnesses=["did:key:zWit"],
                                    silence_days=45, escrow={"journals": False})
    rev["derived_from"] = [h[0]["id"]]
    f.write(rev)
    h = heads()
    assert len(h) == 1 and h[0]["silence_window"]["days"] == 45
    assert rec["id"] in f.records                        # history intact
    # the §8 locks, refused at mint by name
    with pytest.raises(ValueError):                      # unknown fate
        continuity.make_testament(me, f.steward_kp, f.scope,
                                  fates={"journals": "burn"})
    with pytest.raises(ValueError):                      # lock 5: unescrowed only shreds
        continuity.make_testament(me, f.steward_kp, f.scope,
                                  fates={"journals": "pass"},
                                  executor="did:key:zE",
                                  escrow={"journals": False})
    with pytest.raises(ValueError):                      # execution needs an executor
        continuity.make_testament(me, f.steward_kp, f.scope,
                                  fates={"identity": "pass"})
    with pytest.raises(ValueError):                      # custody needs hands (0035 §4)
        continuity.make_testament(me, f.steward_kp, f.scope,
                                  fates={"identity": "pass"},
                                  executor="did:key:zE")
    with pytest.raises(ValueError):                      # distinct signers (0012 §3)
        continuity.make_testament(me, f.steward_kp, f.scope,
                                  fates={"identity": "pass"},
                                  executor="did:key:zE", heir="did:key:zKid",
                                  witnesses=["did:key:zE"])


def test_fates_default_to_seal_and_the_unnamed_seal():
    """0035 §8 locks 1 · 2: no testament seals, an unnamed domain seals, a
    revoked word seals — the universe assumes nothing about the unspoken; and
    the only dead-man shred is key mortality."""
    assert continuity.fate_of(None, "journals") == "seal"
    head = {"posture": "standing", "fates": {"journals": "shred"},
            "escrow": {"journals": False}}
    assert continuity.fate_of(head, "journals") == "shred"
    assert continuity.fate_of(head, "identity") == "seal"      # unnamed seals
    assert continuity.fate_of({**head, "posture": "revoked"},
                              "journals") == "seal"            # withdrawn word
    assert continuity.shred_method(head, "journals") == "key-mortality"
    assert continuity.shred_method(head, "episodic") == "governed"
    assert continuity.shred_method(None, "journals") == "governed"


def test_the_attestation_bar_is_quorum_two():
    """0035 §8 lock 3: executor + evidence + one named witness (or registry
    evidence as the second voice) — below the bar nothing executes, ever."""
    head = {"posture": "standing", "executor": "did:key:zE",
            "witnesses": ["did:key:zW"]}
    assert continuity.may_attest(head, "did:key:zE")
    assert continuity.may_attest(head, "did:key:zW")
    assert not continuity.may_attest(head, "did:key:zX")
    assert not continuity.may_attest(None, "did:key:zE")
    ev = ["artifact-death-certificate"]
    assert not continuity.attestation_met(head, ["did:key:zE"], ev)   # alone
    assert not continuity.attestation_met(head, ["did:key:zE",
                                                 "did:key:zW"], [])   # no evidence
    assert not continuity.attestation_met(head, ["did:key:zW"], ev)   # no executor
    assert continuity.attestation_met(head, ["did:key:zE", "did:key:zW"], ev)
    assert continuity.attestation_met(head, ["did:key:zE"], ev, registry=True)
    assert not continuity.attestation_met({**head, "posture": "revoked"},
                                          ["did:key:zE", "did:key:zW"], ev)


def test_heirs_narrow_never_widen():
    """0035 §8 lock 4: the disclosure map is the dead's consent, fixed — heirs
    may close doors, never open them; absent an entry, the door is closed."""
    old = {"episodic": ["did:key:zKid", "did:key:zSib"],
           "identity": ["did:key:zKid"]}
    assert continuity.narrowed_ok(old, {"episodic": ["did:key:zKid"]})
    assert continuity.narrowed_ok(old, {})                     # closing narrows
    assert not continuity.narrowed_ok(old, {"journals": ["did:key:zKid"]})
    assert not continuity.narrowed_ok(old, {"identity": ["did:key:zKid",
                                                         "did:key:zNew"]})
    head = {"posture": "standing", "disclosure": old}
    assert continuity.may_read_legacy(head, "did:key:zKid", "episodic")
    assert not continuity.may_read_legacy(head, "did:key:zNew", "episodic")
    assert not continuity.may_read_legacy(head, "did:key:zKid", "journals")
    assert not continuity.may_read_legacy(None, "did:key:zKid", "episodic")


def test_beckys_testament_doors():
    """0035 §2 at the card: the standing word STAGES verbatim with its fates
    readable; a word that must execute refuses without an executor; revocation
    acts NOW; the ledger speaks the head — or the honest default."""
    ans = parlor.answer(
        "becky",
        "testament: journals shred, identity pass, medication seal "
        "— executor did:key:zExec, heir did:key:zKid, witness did:key:zWit, "
        "silence 21 days",
        {"scope": "u:demo"})
    assert ans["action"] == "testament-stage" and ans["verbatim"] is True
    assert ans["fates"] == {"journals": "shred", "identity": "pass",
                            "medication": "seal"}
    assert ans["executor"] == "did:key:zExec"        # case kept — a DID is a self
    assert ans["heir"] == "did:key:zKid"
    assert ans["witnesses"] == ["did:key:zWit"] and ans["silence_days"] == 21
    assert "the gate waits" in ans["reply"]
    assert "unnamed domains seal" in ans["reply"]
    naked = parlor.answer("becky", "testament: journals shred",
                          {"scope": "u:demo"})
    assert "action" not in naked and "executor" in naked["reply"]
    handless = parlor.answer("becky",
                             "testament: identity pass — executor did:key:zE",
                             {"scope": "u:demo"})
    assert "action" not in handless and "heir" in handless["reply"]
    rev = parlor.answer("becky", "revoke my testament", {"scope": "u:demo"})
    assert rev["action"] == "testament-revoke" and rev["verbatim"] is True
    assert "seals" in rev["reply"]
    shown = parlor.answer("becky", "show testament",
                          {"scope": "u:demo",
                           "testament": [{"posture": "standing",
                                          "fates": {"journals": "shred"},
                                          "executor": "did:key:zExec",
                                          "witnesses": ["did:key:zWit"],
                                          "silence_window": {"days": 21}}]})
    assert shown["verbatim"] is True
    assert "journals shred" in shown["reply"] and "21-day" in shown["reply"]
    assert "only attested death executes" in shown["reply"]
    empty = parlor.answer("becky", "show testament", {"scope": "u:demo"})
    assert "no testament stands" in empty["reply"]


def test_silence_only_contains():
    """0035 §8 lock 1: silence justifies living within the window,
    unresponsive past it, sealed past twice it — and NEVER more; a universe
    with no history has no basis to seal."""
    v = continuity.silence_verdict
    base = "2026-07-01T00:00:00Z"
    assert v(21, base, "2026-07-10T00:00:00Z") == "living"       # day 9
    assert v(21, base, "2026-07-25T00:00:00Z") == "unresponsive"  # day 24
    assert v(21, base, "2026-08-20T00:00:00Z") == "sealed"        # day 50
    # the rig dial scales a testament-day; the LAW stays days
    assert v(2, "2026-07-01T00:00:00Z", "2026-07-01T00:00:25Z",
             unit_secs=10) == "unresponsive"                      # 25s ≈ day 2.5
    assert v(2, "2026-07-01T00:00:00Z", "2026-07-01T00:00:45Z",
             unit_secs=10) == "sealed"                            # 45s ≈ day 4.5
    assert v(21, "", "2026-08-20T00:00:00Z") == "living"          # no history


def test_the_passage_walks_legal_edges():
    """0035 §3: the machine takes no shortcuts and the closed states never
    reopen — sealed is reversible, attested aborts to sealed (one voice) or
    living (a heartbeat), and only sealed reaches the attestation gate."""
    ok = continuity.may_transition
    assert ok("living", "unresponsive") and ok("unresponsive", "sealed")
    assert ok("unresponsive", "living") and ok("sealed", "living")
    assert ok("sealed", "attested")
    assert ok("attested", "sealed") and ok("attested", "living")
    assert ok("attested", "executed") and ok("executed", "legacy")
    assert not ok("living", "sealed")          # no shortcut past the reach-out
    assert not ok("living", "attested")        # a living universe is never dead
    assert not ok("unresponsive", "attested")
    assert not ok("executed", "living")        # a closed worldline never reopens
    assert not ok("legacy", "living")
    assert not ok("sealed", "executed")        # nothing executes without attestation
    assert continuity.passage_state(None) == "living"
    assert continuity.seal_active({"state": "sealed"})
    assert continuity.seal_active({"state": "attested"})
    assert not continuity.seal_active({"state": "living"})
    assert continuity.may_stage_attestation({"state": "sealed"})
    assert not continuity.may_stage_attestation({"state": "living"})
    assert not continuity.may_stage_attestation(None)


def test_passage_records_ride_one_worldline(world):
    """0035 §3: every transition a sibling naming its trigger — the machine
    is legible forever; an unknown state is refused by name."""
    f = world.field_prod
    me = {"did": f.steward["did"], "scope": f.scope}
    first = continuity.make_passage(me, f.steward_kp, f.scope, "unresponsive",
                                    reason="silence past the window")
    f.write(first)

    def heads():
        rows = [{"id": rid, "passage": _body(r)["passage"],
                 "derived_from": r.get("derived_from") or [],
                 "at": r["received_at"]}
                for rid, r in f.records.items()
                if "passage" in r.get("tags", [])]
        rows.sort(key=lambda x: x["at"])
        return continuity.passage_heads(rows)

    h = heads()
    assert len(h) == 1 and h[0]["state"] == "unresponsive"
    sealed = continuity.make_passage(me, f.steward_kp, f.scope, "sealed",
                                     reason="still silent — contained")
    sealed["derived_from"] = [h[0]["id"]]
    f.write(sealed)
    h = heads()
    assert len(h) == 1 and h[0]["state"] == "sealed"
    att = continuity.make_passage(me, f.steward_kp, f.scope, "attested",
                                  reason="quorum 2 at the gate",
                                  evidence=["artifact-cert"],
                                  attestors=["did:key:zE", "did:key:zW"],
                                  cooling_until="2026-08-01T00:00:00Z")
    att["derived_from"] = [h[0]["id"]]
    f.write(att)
    h = heads()
    assert h[0]["state"] == "attested"
    assert h[0]["evidence"] == ["artifact-cert"]
    assert h[0]["cooling_until"] == "2026-08-01T00:00:00Z"
    assert first["id"] in f.records            # every transition kept
    with pytest.raises(ValueError):
        continuity.make_passage(me, f.steward_kp, f.scope, "buried",
                                reason="no such state")


def test_beckys_passage_doors():
    """0035 §3 at the card: the passage speaks its state; an attestation
    STAGES with evidence and roster readable (never on words alone); the
    abort acts NOW — one voice saves."""
    living = parlor.answer("becky", "show the passage", {"scope": "u:demo"})
    assert living["verbatim"] is True and "LIVING" in living["reply"]
    sealed = parlor.answer("becky", "show the passage",
                           {"scope": "u:demo",
                            "passage": [{"state": "sealed",
                                         "reason": "still silent"}]})
    assert "SEALED" in sealed["reply"] and "one heartbeat unseals" \
        in sealed["reply"]
    att = parlor.answer("becky", "show the passage",
                        {"scope": "u:demo",
                         "passage": [{"state": "attested",
                                      "reason": "quorum 2 at the gate",
                                      "cooling_until": "2026-08-01T00:00:00Z"}]})
    assert "ATTESTED" in att["reply"] and "cooling until 2026-08-01" \
        in att["reply"]
    ask = parlor.answer(
        "becky",
        "attest death: evidence artifact-death-certificate — "
        "executor did:key:zExec, witness did:key:zWit",
        {"scope": "u:demo"})
    assert ask["action"] == "attest-death" and ask["verbatim"] is True
    assert ask["evidence"] == ["artifact-death-certificate"]
    assert ask["attestors"] == ["did:key:zExec", "did:key:zWit"]
    assert ask["registry"] is False
    assert "cooling-off" in ask["reply"] and "heartbeat" in ask["reply"]
    naked = parlor.answer("becky", "attest death: executor did:key:zExec",
                          {"scope": "u:demo"})
    assert "action" not in naked and "evidence" in naked["reply"]
    ab = parlor.answer("becky", "abort the attestation", {"scope": "u:demo"})
    assert ab["action"] == "attestation-abort" and "one voice saves" \
        in ab["reply"]


def test_the_walk_names_every_fate():
    """0035 §4: named domains speak their fates; a heirless pass degrades to
    seal, loudly; a shred under legal hold QUEUES (0004); key mortality is
    named as its own method; the unnamed seal closes every walk."""
    head = {"posture": "standing", "heir": "did:key:zKid",
            "fates": {"journals": "shred", "identity": "pass",
                      "medication": "seal", "vault": "shred"},
            "escrow": {"vault": False}}
    steps = {s["domain"]: s for s in continuity.execution_walk(
        head, holds={"journals"})}
    assert steps["journals"]["fate"] == "shred" and steps["journals"]["held"]
    assert steps["vault"]["method"] == "key-mortality"
    assert steps["identity"]["fate"] == "pass"
    assert steps["medication"]["fate"] == "seal"
    assert steps["*"]["fate"] == "seal"            # the unnamed seal, always
    handless = {s["domain"]: s for s in continuity.execution_walk(
        {**head, "heir": ""})}
    assert handless["identity"]["fate"] == "seal"  # custody without hands
    assert "no hands" in handless["identity"]["note"]


def test_succession_springs_only_at_the_close():
    """0035 §2/§4, lock 4: dormant paper until EXECUTED — and what springs is
    custody, never identity: retrieve + graft over the pass domains, never
    govern, never the keys."""
    head = {"posture": "standing", "heir": "did:key:zKid",
            "fates": {"identity": "pass", "relationships": "pass",
                      "journals": "shred"}}
    for state in ("living", "unresponsive", "sealed", "attested"):
        assert continuity.succession_terms(head, state, "u:x") is None
    terms = continuity.succession_terms(head, "executed", "u:x")
    assert terms["holder"] == "did:key:zKid"
    assert terms["domains"] == ["identity", "relationships"]
    assert terms["grants"] == [{"action": "retrieve", "space": {"scope": "u:x"}}]
    assert all(g["action"] == "retrieve" for g in terms["grants"])  # never govern
    assert terms["graft"] is True
    assert continuity.succession_terms({**head, "heir": ""},
                                       "legacy", "u:x") is None
    assert continuity.succession_terms({**head, "fates": {"j": "shred"}},
                                       "legacy", "u:x") is None


def test_the_graft_carries_lineage(world):
    """0035 §4: continuation is by graft, not possession — the copy lives in
    the heir's own universe with `derived_from` crossing scopes and the
    `inherited` tag; the parent record stays whole and untouched."""
    f = world.field_prod
    me = {"did": f.steward["did"], "scope": f.scope}
    src = make_memory(me, f.steward_kp, f.scope,
                      {"name": "Anna", "relationship": "your sister"},
                      kind="semantic", tags=["identity"])
    f.write(src)
    heir_scope = "u:heir/e:home/f:mind"
    g = continuity.make_graft(me, f.steward_kp, heir_scope,
                              source_ref=src["id"], source_scope=f.scope,
                              body={"name": "Anna",
                                    "relationship": "your sister"})
    assert g["derived_from"] == [src["id"]]        # lineage crosses universes
    assert "inherited" in g["tags"]
    assert g["space"]["scope"] == heir_scope if "space" in g else True
    body = json.loads(crypto._b64d(g["body"]).decode())
    assert body["inherited"]["ref"] == src["id"]
    assert body["inherited"]["scope"] == f.scope
    assert body["body"]["name"] == "Anna"
    assert src["id"] in f.records                  # the parent stays whole


def test_the_portrait_freezes():
    """0035 §4, lock 4: past EXECUTED the sovereign class dies with its
    sovereign — the librarian's assert door refuses, structurally; while the
    human lives (sealed included — reversible), the stroke still lands."""
    assert continuity.sovereign_alive(None)
    assert continuity.sovereign_alive({"state": "sealed"})
    assert continuity.sovereign_alive({"state": "attested"})
    assert not continuity.sovereign_alive({"state": "executed"})
    assert not continuity.sovereign_alive({"state": "legacy"})
    frozen = parlor.answer("librarian", "my profile: I love the coast",
                           {"scope": "u:x",
                            "passage": [{"state": "legacy",
                                         "reason": "the walk is complete"}]})
    assert "action" not in frozen
    # sp4's read-only guard speaks first; the frozen-portrait law stands
    # behind it for any assert shape the broad guard misses
    assert "read-only" in frozen["reply"] or "frozen" in frozen["reply"]
    assert "about, never as" in frozen["reply"]
    alive = parlor.answer("librarian", "my profile: I love the coast",
                          {"scope": "u:x",
                           "passage": [{"state": "sealed", "reason": "quiet"}]})
    assert alive["action"] == "profile-assert"     # reversible states still speak


def test_the_archive_speaks_about_never_as():
    """0035 §5: the legacy register — first person dies with the person;
    every shape opens from the record, none from a voice; the recalled stay
    unspoken, doubly."""
    say = continuity.speak_legacy
    assert say("trusted", "she loved the coast") \
        == "the record holds: she loved the coast"
    corr = say("corroborated", "the trip happened in May",
               sources=["the photos"])
    assert corr.startswith("the record holds:") and "the photos" in corr
    hedged = say("untrusted", "the address changed", hints=2)
    assert hedged.startswith("the record suggests, unproven:")
    assert "never confirmed" in hedged
    assert say("investigating", "the dosage moved") \
        .startswith("the record was re-checking this when it closed:")
    assert say("recalled", "a poisoned claim") is None
    for state in ("trusted", "corroborated", "untrusted", "investigating"):
        spoken = say(state, "a fact", sources=["s"])
        assert not spoken.startswith(("I ", "you ", "You "))


def test_the_survivors_door_composes_from_the_word():
    """0035 §6: custody first, the disclosure map's named doors second, and
    the honest close for everything else — grief is not an entitlement; while
    the human lives, consent governs."""
    head = {"posture": "standing", "heir": "did:key:zKid",
            "fates": {"identity": "pass", "journals": "shred"},
            "disclosure": {"medication": ["did:key:zDoc"], "episodic": []}}
    alive = continuity.survivors_door(head, "sealed", "u:x")
    assert "opens only in legacy" in alive
    door = continuity.survivors_door(head, "legacy", "u:x")
    assert "custody stands for did:key:zKid" in door
    assert "identity" in door and "never govern" in door
    assert "medication — readable to did:key:zDoc" in door
    assert "episodic" not in door                 # an empty entry is no door
    assert "heirs narrow, never widen" in door
    closed = continuity.survivors_door({"posture": "standing", "fates": {}},
                                       "legacy", "u:x")
    assert "grief is not an entitlement" in closed


def test_legacy_is_read_only():
    """0035 §6: past EXECUTED every mutating door answers with one sentence —
    the archive keeps, never spends, admits nothing new; the read doors still
    answer, because legacy is not a tomb with the lights cut."""
    legacy_facts = {"scope": "u:x",
                    "passage": [{"state": "legacy",
                                 "reason": "the walk is complete"}],
                    "testament": [{"posture": "standing",
                                   "heir": "did:key:zKid",
                                   "fates": {"identity": "pass"},
                                   "executor": "did:key:zE",
                                   "silence_window": {"days": 6}}]}
    for ask in ("testament: journals shred — executor did:key:zE",
                "grant caregiver access to help", "resume recording conversation",
                "create ecosystem again"):
        r = parlor.answer("becky", ask, legacy_facts)
        assert "read-only" in r["reply"] and "action" not in r, ask
    for ask in ("subscribe to the news", "gather knowledge on tides",
                "remember this: a moment", "my profile: I love the coast",
                "challenge the address"):
        r = parlor.answer("librarian", ask, legacy_facts)
        assert "read-only" in r["reply"] and "action" not in r, ask
    # the read doors stay open
    shown = parlor.answer("becky", "show testament", legacy_facts)
    assert "identity pass" in shown["reply"]
    door = parlor.answer("becky", "the survivors' door", legacy_facts)
    assert "custody stands for did:key:zKid" in door["reply"]
    passage = parlor.answer("becky", "show the passage", legacy_facts)
    assert "LEGACY" in passage["reply"]


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
