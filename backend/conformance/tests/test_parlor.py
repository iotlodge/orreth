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


def test_profile_asks_route_sovereign_read_and_forget():
    """0025: assert (sovereign, verbatim), read (the portrait), forget (consent) —
    three asks, three actions, all flow-control."""
    a = parlor.answer("librarian", "my profile: I toast with cocoa, never whiskey", FACTS)
    assert a.get("action") == "profile-assert" and a.get("verbatim") is True
    assert a["claim"] == "I toast with cocoa, never whiskey"
    r = parlor.answer("librarian", "what do you know about me?", FACTS)
    assert r.get("action") == "profile-read"
    f = parlor.answer("librarian", "forget about me: whiskey", FACTS)
    assert f.get("action") == "profile-forget" and f["topic"] == "whiskey"


def test_remember_this_routes_to_a_life_event_marker():
    """0024 §4: the human's "remember this" becomes a quoted life-event marker on the
    auto lane — the ask IS the approval, the confirmation travels verbatim, and the
    human's own words pick the weight (default minor)."""
    r = parlor.answer("librarian", "remember this: the brain shipped today as substantial",
                      FACTS)
    assert r.get("action") == "remember" and r.get("verbatim") is True
    assert r["note"] == "the brain shipped today" and r["weight"] == "substantial"
    r2 = parlor.answer("librarian", "remember this: toast with cocoa", FACTS)
    assert r2["weight"] == "minor" and r2["note"] == "toast with cocoa"


def test_ask_the_universe_routes_to_the_self_dialog():
    """0023 §3: the librarian asks HERSELF at her other seats — and the staging
    confirmation is flow-control, so it travels verbatim, never voiced."""
    r = parlor.answer("librarian", "ask the universe about Leadville winters", FACTS)
    assert r.get("action") == "self-dialog" and r["topic"] == "Leadville winters"
    assert r.get("verbatim") is True
    c = parlor.card("librarian", FACTS)
    assert any(a.get("template", "").startswith("ask the universe") for a in c["asks"])


def test_librarian_tells_the_recall_ledger():
    """The immune system's ledger, in words — and an honest nothing when it's empty."""
    quiet = parlor.answer("librarian", "has anything been recalled?", FACTS)
    assert "nothing recalled" in quiet["reply"]
    facts = {**FACTS, "requests": FACTS["requests"] + [
        {"kind": "recall", "status": "done", "service": "local.demo/almanac",
         "source_did": "did:web:almanac.example",
         "result": "recalled 3 entr(ies) traced to did:web:almanac.example — "
                   "annotated, never rewritten; the lineage is intact"}]}
    told = parlor.answer("librarian", "has anything been recalled?", facts)
    assert "local.demo/almanac" in told["reply"] and "3 entr" in told["reply"]


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


# ---------------------------------------------------------------- 0028: the workspaces
def test_the_card_declares_the_room_and_only_the_embodied_have_one():
    """0028 §1: the glass shows the expand handle only when the card declares it —
    a new resident brings its room without a line of Console code."""
    for name in parlor.RESIDENTS:
        c = parlor.card(name, FACTS)
        assert c["workspace"] is (name in parlor.EMBODIED)
    assert parlor.workspace("vigil", FACTS) is None      # no room, honestly


def test_rooms_compose_typed_panels_rendered_blind():
    """Four rooms, four typed kinds — stat · bars · list · doc — composed from
    state the resident may read; the glass knows the kinds, never the residents."""
    kinds = {"stat", "bars", "list", "doc"}
    for name in parlor.EMBODIED:
        ws = parlor.workspace(name, FACTS)
        assert ws["resident"] == name and ws["panels"]
        for p in ws["panels"]:
            assert p["kind"] in kinds and p["title"]
            if p["kind"] == "doc":
                assert isinstance(p["text"], str)
            else:
                assert isinstance(p["items"], list)


def test_medium_and_above_wear_amber():
    """0024's badge, discharged: the severity chip rides the row; medium+ is
    amber so pending co-review is visible at a glance."""
    facts = dict(FACTS, markers=[
        {"text": "a quiet note", "meta": "moment · minor", "severity": ""},
        {"text": "a recall walked", "meta": "change · high", "severity": "high"}])
    ws = parlor.workspace("librarian", facts)
    moments = next(p for p in ws["panels"] if "moments" in p["title"])
    ambers = [i for i in moments["items"] if i.get("amber")]
    assert len(ambers) == 1 and ambers[0]["text"] == "a recall walked"
    # charlotte's quarantined service wears it too
    ws2 = parlor.workspace("charlotte", FACTS)
    roster = next(p for p in ws2["panels"] if p["title"] == "the roster")
    assert any(i.get("amber") for i in roster["items"])


# ---------------------------------------------------------------- grace (0031 §4)


def test_grace_wears_the_smiths_card():
    facts = {"scope": "u:demo",
             "shelf": [{"name": "prompt-plan", "versions": 1, "open": "p1",
                        "feedback": 0}]}
    c = parlor.card("grace", facts)
    assert c["voiced"] and c["workspace"] and c["role"] == "grace · the smith"
    labels = [a["label"] for a in c["asks"]]
    assert "show the shelf" in labels and "leave feedback…" in labels


def test_grace_walks_and_receives_feedback_verbatim():
    facts = {"scope": "u:demo", "shelf": []}
    walk = parlor.answer("grace", "show asset prompt-plan", facts)
    assert walk["action"] == "asset-walk" and walk["asset"] == "prompt-plan"
    assert walk["verbatim"] is True           # flow-control is never voiced
    fb = parlor.answer("grace", "feedback on prompt-plan: too wordy under pressure",
                       facts)
    assert fb["action"] == "asset-feedback" and fb["asset"] == "prompt-plan"
    assert fb["note"] == "too wordy under pressure" and fb["verbatim"] is True
    assert "too wordy under pressure" in fb["reply"]     # the words, quoted back


def test_grace_room_composes_the_workshop():
    facts = {"scope": "u:demo",
             "shelf": [{"name": "fingertip-default", "versions": 2, "open": "p1",
                        "feedback": 1, "active": "a2"}],
             "requests": [{"kind": "improvement", "status": "staged",
                           "text": "a rewrite waits"}],
             "package_text": "prompt-plan — a rewrite on the high lane."}
    ws = parlor.workspace("grace", facts)
    kinds = [p["kind"] for p in ws["panels"]]
    assert kinds == ["stat", "bars", "list", "doc"]
    stat = {i["label"]: i["value"] for i in ws["panels"][0]["items"]}
    assert stat["waiting for you"] == 1 and stat["your feedback"] == 1
    row = ws["panels"][2]["items"][0]
    assert row["amber"] is True               # a held lane wears amber (0024)
    assert "high lane" in ws["panels"][3]["text"]


def test_package_text_reads_the_gate():
    pkg = {"asset": "prompt-plan", "kind": "rewrite", "lane": "high",
           "changed": {"template": {"from": "a", "to": "b"}},
           "receipts": [{"ref": "r1", "what": "the human's words: “shorter”"}],
           "rollback": "aaaa1111", "checks": {"no_op": False, "cites_active": True}}
    text = parlor.package_text(pkg)
    assert "rewrite" in text and "WHAT CHANGED" in text and "ROLLBACK" in text
    assert "shorter" in text and "lineage cites the active version" in text


# ---------------------------------------------------------------- freshness (0031 §5)


def test_librarian_challenge_and_domain_doors():
    facts = {"scope": "u:demo"}
    ch = parlor.answer("librarian", "challenge pine joint spans", facts)
    assert ch["action"] == "challenge" and ch["topic"] == "pine joint spans"
    assert ch["verbatim"] is True and "doubted, not damned" in ch["reply"].lower()
    d = parlor.answer("librarian", "show domain packages", facts)
    assert d["action"] == "domain" and d["topic"] == ""
    one = parlor.answer("librarian", "show domain timber framing", facts)
    assert one["action"] == "domain" and one["topic"] == "timber framing"


def test_librarian_room_carries_the_domain_shelf():
    facts = {"scope": "u:demo", "residents": [],
             "domains": [{"topic": "timber framing",
                          "meta": "3 current of 5 version(s) · investigating 1",
                          "doubted": True}]}
    ws = parlor.workspace("librarian", facts)
    panel = next(p for p in ws["panels"] if "domain packages" in p["title"])
    assert panel["items"][0]["amber"] is True       # doubt wears amber (0024)
    assert "investigating 1" in panel["items"][0]["meta"]
