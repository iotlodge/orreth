# PROVENANCE: Claude Fable 5 (claude-fable-5) — rearch P0 sp1, the rig breathes · 2026-09-16
"""The envelope's laws (canon 0002): canonical bytes are the contract,
required fields refuse by name, unknown fields survive, the authority
chain rides in order."""
import json

import pytest

from orreth_spine import envelope as ev


def _mint(**over):
    kw = dict(kind="event", type="orreth.heartbeat.v1", universe_id="u:dev",
              scope_path="u:dev", payload={"ref": "r", "hash": "sha256:x"})
    kw.update(over)
    return ev.make_envelope(**kw)


def test_canonical_is_order_blind_compact_ascii():
    a = ev.canonical({"b": 1, "a": [2, {"z": "ü", "y": 3}]})
    b = ev.canonical({"a": [2, {"y": 3, "z": "ü"}], "b": 1})
    assert a == b
    assert b" " not in a and a.decode("ascii")  # compact and pure ASCII
    assert b"\\u00fc" in a                       # non-ASCII escaped, never raw


def test_content_hash_stable_and_change_sensitive():
    assert ev.content_hash({"k": 9}) == ev.content_hash({"k": 9})
    assert ev.content_hash({"k": 9}) != ev.content_hash({"k": 8})
    assert ev.content_hash({"k": 9}).startswith("sha256:")


def test_round_trip_is_byte_identical():
    env = _mint(authority_chain=["did:orreth:person:jb", "did:orreth:agent:a"])
    raw = ev.encode(env)
    back = ev.decode(raw)
    assert back == env
    assert ev.encode(back) == raw


def test_kinds_wear_their_prefix_and_bad_kind_refuses():
    assert _mint(kind="event")["message_id"].startswith("msg_")
    assert _mint(kind="command")["message_id"].startswith("cmd_")
    with pytest.raises(ValueError, match="message_kind"):
        _mint(kind="signal")


def test_missing_required_fields_refuse_by_name():
    env = _mint()
    del env["scope_path"], env["occurred_at"]
    with pytest.raises(ValueError) as e:
        ev.encode(env)
    assert "scope_path" in str(e.value) and "occurred_at" in str(e.value)
    with pytest.raises(ValueError, match="specversion"):
        ev.encode(dict(_mint(), specversion="orreth.transport/9"))


def test_unknown_additive_fields_survive_the_round_trip():
    env = _mint()
    env["future_field"] = {"a": 1}
    assert ev.decode(ev.encode(env))["future_field"] == {"a": 1}


def test_authority_chain_keeps_its_order():
    chain = ["did:orreth:person:jb", "did:orreth:resident:allen",
             "did:orreth:agent:worker-3"]
    env = _mint(authority_chain=chain)
    assert ev.decode(ev.encode(env))["authority_chain"] == chain


def test_aggregate_rides_the_wire_intact():
    env = _mint(aggregate={"type": "counter", "id": "c1", "sequence": 7})
    back = ev.decode(ev.encode(env))
    assert back["aggregate"] == {"type": "counter", "id": "c1", "sequence": 7}
    assert "aggregate" not in _mint()  # optional: absent unless declared


def test_message_ids_are_unique():
    assert len({_mint()["message_id"] for _ in range(200)}) == 200


def test_decode_refuses_incomplete_wire_bytes():
    raw = json.dumps({"specversion": ev.SPECVERSION}).encode()
    with pytest.raises(ValueError, match="missing required"):
        ev.decode(raw)
