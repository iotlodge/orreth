# PROVENANCE: Fable 5 (claude-fable-5) — the join door, hardened · 2026-07-07
"""The join door (JB's lock 2026-07-07): HITL gate + nonce challenge.

Under test: the door answers proof, not claims — a lease requires BOTH a signed
nonce (key control) and a human at the gate; approval without proof re-challenges;
a wrong key or a tampered nonce is turned away; a restarted desk heals by
challenging again; and nothing terminal is ever reprocessed.
"""
from orreth_sim import crypto
from orreth_sim.joindoor import JoinDesk

TOKENS: list[str] = []


def desk(nonces=None):
    TOKENS.clear()
    seq = iter(nonces or [])
    return JoinDesk(
        grant=lambda did: (TOKENS.append(did) or {"subject": did, "lease": "ok"}),
        nonce=(lambda: next(seq)) if nonces else None)


def joiner():
    kp = crypto.KeyPair()
    return kp, crypto.did_key_for(kp.public)


def prove(kp, did, nonce):
    return kp.sign(did, {"join_nonce": nonce, "did": did})


def req(rid, did, status, result=None, name="scout"):
    return {"id": rid, "kind": "join", "did": did, "name": name,
            "status": status, "result": result or {}}


def test_the_full_handshake_mints_exactly_once():
    d, (kp, did) = desk(), joiner()
    status, result = d.tend(req("j1", did, "pending"))
    assert status == "challenged" and result["nonce"]
    status, result2 = d.tend(req("j1", did, "proved",
                                 {"nonce": result["nonce"],
                                  "proof": prove(kp, did, result["nonce"])}))
    assert status == "staged"                      # key proven; the human holds the door
    assert TOKENS == []                            # proof alone mints nothing
    status, result3 = d.tend(req("j1", did, "approved"))
    assert status == "done" and result3["token"]["subject"] == did
    assert TOKENS == [did]
    assert d.tend(req("j1", did, "done")) is None  # terminal — the desk is clear
    assert d.desk == {}


def test_wrong_key_is_turned_away():
    d, (_, did) = desk(), joiner()
    imposter, _ = joiner()                         # holds a different key entirely
    _, result = d.tend(req("j2", did, "pending"))
    status, _ = d.tend(req("j2", did, "proved",
                           {"nonce": result["nonce"],
                            "proof": prove(imposter, did, result["nonce"])}))
    assert status == "denied" and TOKENS == []


def test_tampered_nonce_fails_against_the_desks_copy():
    """The desk verifies against what it ISSUED — an echoed nonce is not the truth."""
    d, (kp, did) = desk(), joiner()
    d.tend(req("j3", did, "pending"))
    status, _ = d.tend(req("j3", did, "proved",
                           {"nonce": "forged", "proof": prove(kp, did, "forged")}))
    assert status == "denied" and TOKENS == []


def test_approval_without_proof_rechallenges_never_mints():
    d, (_, did) = desk(), joiner()
    status, result = d.tend(req("j4", did, "approved"))    # forged straight to approved
    assert status == "challenged" and result["nonce"] and TOKENS == []


def test_a_restarted_desk_heals_by_challenging_again():
    d1, (kp, did) = desk(), joiner()
    _, result = d1.tend(req("j5", did, "pending"))
    proof = {"nonce": result["nonce"], "proof": prove(kp, did, result["nonce"])}
    d2 = desk()                                    # the desk dies; its nonces die with it
    status, fresh = d2.tend(req("j5", did, "proved", proof))
    assert status == "challenged" and fresh["nonce"] != result["nonce"]
    status, _ = d2.tend(req("j5", did, "proved",
                            {"nonce": fresh["nonce"],
                             "proof": prove(kp, did, fresh["nonce"])}))
    assert status == "staged"


def test_only_self_certifying_dids_may_knock():
    d = desk()
    status, _ = d.tend(req("j6", "did:web:sneaky.example", "pending"))
    assert status == "denied" and TOKENS == []


def test_the_desk_is_idempotent_between_transitions():
    d, (kp, did) = desk(), joiner()
    _, result = d.tend(req("j7", did, "pending"))
    assert d.tend(req("j7", did, "pending")) is None       # already challenged
    d.tend(req("j7", did, "proved", {"nonce": result["nonce"],
                                     "proof": prove(kp, did, result["nonce"])}))
    assert d.tend(req("j7", did, "proved", {"nonce": result["nonce"],
                                            "proof": prove(kp, did, result["nonce"])})) is None
    assert TOKENS == []                                     # still nothing minted
