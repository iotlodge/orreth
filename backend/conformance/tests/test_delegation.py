# PROVENANCE: Claude Fable 5 (claude-fable-5) — 0071 sp3, the delegate credential · 2026-09-08
"""The join door's key custody (0071 sp3): the root signs ONCE, offline; the door
holds only its own key — and everything it issues still verifies against the root."""
import pytest

from orreth_sim import crypto
from orreth_sim.identity import AuthzError, Becky, Nanda, mint_delegation


def _root(nanda):
    return Becky("u:t", nanda, universe_name="t", kp=crypto.KeyPair())


def test_minted_credential_carries_no_root_key():
    nanda = Nanda()
    root = _root(nanda)
    bundle = mint_delegation(root, "u:t/f:door")
    assert set(bundle) == {"scope", "seed", "cert", "root_did"}
    assert bundle["cert"]["issuer"] == root.did
    assert crypto._b64d(bundle["seed"]) != root.kp.seed


def test_adopted_door_issues_and_the_root_side_verifies():
    nanda = Nanda()
    root = _root(nanda)
    bundle = mint_delegation(root, "u:t/f:door")
    # the door's process: only the bundle — never the root's key
    door = Becky.adopt(bundle["scope"], nanda,
                       crypto.KeyPair(seed=crypto._b64d(bundle["seed"])),
                       [bundle["cert"]])
    agent_kp = crypto.KeyPair()
    agent_did = crypto.did_key_for(agent_kp.public)
    nanda.register(agent_did, agent_kp.public)
    lease = door.issue_token(agent_did, "u:t/f:door",
                             [{"action": "retrieve", "space": "self"}])
    root.verify_token(lease)   # the plane's stance: chain walks to the pinned root
    pen = door.issue_token(door.did, "u:t/f:door",
                           [{"action": "resolve", "space": "queue"}])
    root.verify_token(pen)


def test_foreign_root_credential_refused_at_verification():
    nanda = Nanda()
    root = _root(nanda)
    # a stranger's WORLD (its own registry) wearing the same universe name —
    # the victim's side knows the real root's key, exactly as the plane pins it
    stranger = Becky("u:t", Nanda(), universe_name="t", kp=crypto.KeyPair())
    bundle = mint_delegation(stranger, "u:t/f:door")
    door = Becky.adopt(bundle["scope"], Nanda(),
                       crypto.KeyPair(seed=crypto._b64d(bundle["seed"])),
                       [bundle["cert"]])
    agent_did = crypto.did_key_for(crypto.KeyPair().public)
    nanda.register(agent_did, agent_did[len("did:key:"):])
    lease = door.issue_token(agent_did, "u:t/f:door",
                             [{"action": "retrieve", "space": "self"}])
    with pytest.raises(AuthzError):
        root.verify_token(lease)


def test_adopt_refuses_a_cert_for_someone_elses_key():
    nanda = Nanda()
    root = _root(nanda)
    bundle = mint_delegation(root, "u:t/f:door")
    with pytest.raises(AuthzError):
        Becky.adopt(bundle["scope"], nanda, crypto.KeyPair(), [bundle["cert"]])


def test_only_the_root_mints_a_door():
    nanda = Nanda()
    root = _root(nanda)
    child = Becky("u:t/f:x", nanda, parent=root)
    with pytest.raises(AuthzError):
        mint_delegation(child, "u:t/f:x/deeper")