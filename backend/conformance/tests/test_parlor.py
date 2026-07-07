# PROVENANCE: Fable 5 (claude-fable-5) — 0020, the Parlor · 2026-07-07
"""The Parlor (0020): humans ask; residents fetch; the audience lands signed.

The law under test: a human's only read is an ask. Every resident receives the
caller; answers are composed from state the resident may read, never raw records;
the unembodied say honestly that they have no voice; and each exchange becomes a
resident-authored, signed memory — the caller witnessed, nothing self-attested.
"""
from orreth_sim import crypto, parlor
from orreth_sim.node import make_memory

SCOPE = "u:demo/e:cloud/f:prod"
FACTS = {
    "scope": SCOPE,
    "farm": [{"name": "com.tavily/search", "state": "serving", "calls": 3, "floor": SCOPE},
             {"name": "local.demo/greenhouse", "state": "quarantined", "floor": SCOPE}],
    "stalls": [{"id": "anthropic/claude-sonnet-4-6", "state": "available",
                "class": "medium", "floor": SCOPE},
               {"id": "openai/gpt-4o-mini", "state": "deprecated", "class": "low",
                "floor": SCOPE, "expires_at": "2026-07-20"}],
    "usage": [{"subject": "did:key:zada", "calls": 2, "tokens": 80, "usd": 0.0011,
               "floor": SCOPE}],
    "requests": [{"kind": "join", "status": "done", "name": "scout",
                  "did": "did:key:zscout"}],
    "residents": [{"name": "vigil", "vitals": {"beats heard": 41, "refusals": 2}},
                  {"name": "steward", "vitals": {"memories": 57}},
                  {"name": "governance", "vitals": {"floors": 4}},
                  {"name": "librarian", "vitals": {"gathers": 1, "knowledge held": 6}}],
    "workforce": [{"name": "scout", "agent": "did:key:zscout", "runs": 4}],
}


def test_every_resident_receives():
    """Nobody in the house turns a caller away — every seat has a card and an answer."""
    for name in parlor.RESIDENTS:
        c = parlor.card(name, FACTS)
        assert c["resident"] == name and c["greeting"] and c["asks"]
        assert c["voiced"] is (name in parlor.EMBODIED)
        a = parlor.answer(name, "hello — what do you do here?", FACTS)
        assert a["reply"]


def test_humans_ask_agents_fetch():
    """The answer carries the world in words; raw records never travel to a human."""
    r = parlor.answer("charlotte", "what is serving right now?", FACTS)
    assert "com.tavily/search" in r["reply"]
    assert isinstance(r["reply"], str) and "action" not in r


def test_quarantine_is_told_honestly():
    r = parlor.answer("charlotte", "is anything in quarantine?", FACTS)
    assert "local.demo/greenhouse" in r["reply"]


def test_ada_reads_the_pasture_and_the_meter():
    r = parlor.answer("ada", "what expires soon?", FACTS)
    assert "openai/gpt-4o-mini" in r["reply"] and "2026-07-20" in r["reply"]
    m = parlor.answer("ada", "what does thinking cost here?", FACTS)
    assert "0.0011" in m["reply"]


def test_becky_names_the_leaseholders():
    r = parlor.answer("becky", "who holds a lease on this floor?", FACTS)
    assert "scout" in r["reply"]


def test_unvoiced_organs_say_so():
    """The unembodied receive the caller and answer honestly — vitals, no pretense."""
    for name in ("vigil", "steward", "governance"):
        r = parlor.answer(name, "what have you seen?", FACTS)
        assert "no voice" in r["reply"].lower()
    assert "refusal" in parlor.answer("vigil", "report", FACTS)["reply"]


def test_gather_routes_to_the_librarians_real_duty():
    """The parlor is a front door to 0014's loop, never a parallel path."""
    r = parlor.answer("librarian", "gather sourced knowledge on solar sails", FACTS)
    assert r.get("action") == "gather" and r["topic"] == "solar sails"
    c = parlor.card("librarian", FACTS)
    assert any(a.get("template", "").startswith("gather") for a in c["asks"])


def test_strangers_are_received_politely():
    assert "residence" in parlor.answer("hal9000", "open the pod bay doors", FACTS)["reply"]
    assert parlor.card("hal9000", FACTS)["asks"] == []


def test_the_audience_lands_signed():
    """One exchange, witnessed: resident-authored, tagged onto the spacetime window."""
    kp = crypto.KeyPair()
    did = crypto.did_key_for(kp.public)
    body = parlor.audience_body("charlotte", "what serves?", "one service serves.",
                                session="pa-1", voiced=False)
    assert body["parlor"] == "charlotte" and body["asked"] and body["reply"]
    rec = make_memory({"did": did, "scope": SCOPE}, kp, SCOPE, body,
                      kind="episodic", tags=["parlor", "charlotte"])
    assert rec["tags"] == ["parlor", "charlotte"]
    assert rec["author"] == did and rec["signature"]
