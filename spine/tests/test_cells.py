# PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp7, cells · partition · isolation · hardening · 2026-09-25
# Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp8 row 3c: the eleventh check follows the tenth · 2026-09-27
"""CELLS (P7 sp7): the universe's home on the ground, the world card on
the door, the tenth check, the meter wearing its world, the topics
wearing the cell's namespace. The seam itself (peers · route home ·
replicate · park) is the Rust kernel's and is proven by
`backend/plane/crates/orreth-spine/tests/cells.rs`."""
import json
import os
import urllib.request

from tests import seats  # P7 sp8 row 3: every door reads the person from the SEAT — the test sits first

import pytest

from orreth_spine import cells, envelope as ev, gateway, ground, harness, rails
from orreth_spine.identity import Identity


def _world_facts(pg):
    cur = pg.cursor()
    cur.execute("SELECT body FROM spine_outbox ORDER BY outbox_id")
    out = []
    for (body,) in cur.fetchall():
        e = ev.decode(bytes(body))
        if e["type"] == cells.WORLD_HOMED:
            out.append(e)
    return out


def test_the_home_is_settled_once_and_said_as_a_fact(pg):
    """The first light writes the row AND the `opened` fact in one
    transaction; the second light refreshes the door and says nothing new;
    a kernel of ANOTHER cell may not light over this universe."""
    ground.ensure_all(pg)
    k = Identity("kernel", os.urandom(32), kind="kernel")
    before = len(_world_facts(pg))
    card = cells.home(pg, k.did, "http://127.0.0.1:1", cell="local")
    assert card["homed"] and card["cell"] == "local" and card["epoch"] == 1 and card["kernel"] == k.did
    facts = _world_facts(pg)
    assert len(facts) == before + 1
    f = facts[-1]
    assert f["payload"]["reason"] == "opened" and f["payload"]["epoch"] == 1 and f["payload"]["cell"] == "local"
    assert f["correlation_id"] == ev.scope() and f["authority_chain"] == ["the kernel"]
    k2 = Identity("kernel", os.urandom(32), kind="kernel")
    again = cells.home(pg, k2.did, "http://127.0.0.1:2", cell="local")
    assert again["epoch"] == 1 and again["kernel"] == k2.did and again["door"] == "http://127.0.0.1:2"
    assert len(_world_facts(pg)) == before + 1                 # no second `opened`
    with pytest.raises(cells.NotMyHome) as e:
        cells.home(pg, k2.did, "http://127.0.0.1:3", cell="two")
    assert "homed in cell local" in str(e.value) and "cell two" in str(e.value)


def test_the_tenth_check_reads_the_role_and_its_reach(pg):
    """The harness's tenth check names the role and every database it
    can enter; the dev ground's owner reaches more than its own and says
    so — never hidden."""
    ground.ensure_all(pg)
    checks = harness.checks(pg)
    assert [c["name"] for c in checks][-2] == "this cell is sealed" and len(checks) == 11   # row 3c: the eleventh follows
    c = checks[-2]
    assert c["role"] and c["database"] and c["database"] in c["reachable"]
    ok, words = cells.sealed_words(c["role"], c["database"], c["reachable"])
    assert c["ok"] == ok and c["detail"] == words
    if len(c["reachable"]) > 1:
        assert not c["ok"] and "unsealed" in c["detail"]


def test_the_meter_wears_its_world(pg):
    gateway.ensure_schema(pg)
    gateway.meter(pg, "did:orreth:agent:test", "fake", 1, 1)
    cur = pg.cursor()
    cur.execute("SELECT scope FROM spine_meter WHERE did = 'did:orreth:agent:test' ORDER BY meter_id DESC LIMIT 1")
    assert cur.fetchone()[0] == ev.scope()


def test_the_topics_wear_the_namespace():
    ns = os.environ.get("SPINE_QUEUE_NS", "")
    assert rails.topic("orreth.ask.received.v1") == cells.topic_name("orreth.ask.received.v1", ns)
    assert cells.topic_name("orreth.ask.received.v1", "") == "orreth.ask.received.v1"
    assert cells.topic_name("orreth.ask.received.v1", "two") == "orreth.ask.received.v1.two"


def test_the_world_card_on_the_door(rig):
    """`/world` — the universe, its cell and epoch, the kernel that keeps it, its peers."""
    with seats.urlopen(f"http://127.0.0.1:{rig.port}/world", timeout=10) as r:
        card = json.loads(r.read())
    assert card["scope"] == ev.scope() and card["homed"] and card["epoch"] >= 1
    assert card["kernel"] == rig.kernel.did and card["door"] == f"http://127.0.0.1:{rig.port}"
    assert card["cell"] == (os.environ.get("SPINE_CELL") or "local") and card["peers"] == []
    with seats.urlopen(f"http://127.0.0.1:{rig.port}/monitor", timeout=10) as r:
        snap = json.loads(r.read())
    assert snap["home"]["cell"] == card["cell"] and snap["home"]["epoch"] == card["epoch"]


def test_the_seam_laws_hold_end_to_end():
    """Sign with one kernel self, verify against its pin; every fence in turn."""
    a = Identity("kernel", os.urandom(32), kind="kernel")
    b = Identity("kernel", os.urandom(32), kind="kernel")
    now = ev.now_iso()
    m = cells.seam_message(from_cell="local", from_world="u:dev", to_cell="two", epoch=1, kind="hello",
                           body={"door": "http://127.0.0.1:4601"}, nonce="n1", at=now)
    s = cells.seam_sign(m, a)
    assert cells.seam_verify(s, pinned_did=a.did, now=now, seen_nonces=()) == "ok"
    assert cells.seam_verify(s, pinned_did=b.did, now=now, seen_nonces=()) == "unknown signer"
    assert cells.seam_verify(s, pinned_did=a.did, now=now, seen_nonces=("n1",)) == "replayed"
    assert cells.seam_verify(s, pinned_did=a.did, now=now, seen_nonces=(), epoch=2) == "stale epoch"
    assert cells.address_home("librarian@two, hello") == {"cell": "two", "name": "librarian"}
    assert cells.strip_home("librarian@two, hello") == "librarian, hello"
    assert cells.address_home("echo, say HERON") is None
