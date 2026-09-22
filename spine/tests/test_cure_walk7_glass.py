# PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P6 cure sp2 (glass), walk #7's wounds · 2026-09-21
"""The door and shape laws behind walk #7's GLASS cures (docs/rearch/
baselines/after-walk-2026-09-17.md, "Walk #7"): W1–W4 the re-enroll takes
the current code as a field and the NEW secret finishes it; W7 a name at
the head reaches one body and every body says what it is; W11 the export
rows carry the marker's words, the ask's target and the refused kind;
W15 citations wear human names; W18 a refused body is refused on the card
the rail reads; W6 the Analyzer row carries `blocked` and the impact ask
starts with the change; the monitor's offer is read from its words. The
glass behaviour itself is JB's to walk."""
import json
import secrets
from pathlib import Path

import pytest

from orreth_spine import dispatch, export, glass, intent, markers, mitl, monitor, proof, resident

SPINE = Path(__file__).resolve().parents[1]
POLICY = SPINE / "policy" / "covenant-policy.v1.json"
ME = "did:orreth:person:walk7g"


def _scope(monkeypatch):
    monkeypatch.setenv("SPINE_SCOPE", "u:law-" + secrets.token_hex(3))


def _body(template, binding=None, home=None):
    path = SPINE / "templates" / template if isinstance(template, str) else template
    r = resident.Resident(path, binding=binding, home=home)
    r.load_policy(POLICY)
    return r


def _serve(pg, body, ask_id):
    body._serve_conn = pg
    with pg.transaction():
        body._serve_ask(pg.cursor(), ask_id, [ME])


# ---- W1 · W3 · W4: the re-enroll flow ---------------------------------------------------

def test_w1_w4_the_re_enroll_takes_the_current_code_as_a_field_and_the_new_secret_finishes(pg):
    """The grave re-enroll: the CURRENT code as a field on /enroll (never
    parsed from a sentence) mints a pending NEW secret while the old one
    stands; the finish step verifies the NEW entry's code — the OLD
    entry's code refuses there (one face), the new one confirms and
    retires the old. The door's shape carries the QR and the URI to the
    live request alone."""
    me = f"did:orreth:person:reenroll-{secrets.token_hex(2)}"
    first = proof.enroll(pg, me)
    assert set(first) >= {"uri", "secret", "qr", "re_enrolled"} and first["re_enrolled"] is False
    proof.confirm_enrollment(pg, me, proof.totp(first["secret"]))
    assert proof.enrolled(pg, me)
    with pytest.raises(proof.NotConfirmed):                 # a wrong current code: one face
        proof.enroll(pg, me, code="000000")
    with pytest.raises(proof.NotConfirmed):                 # no code at all: one face (the glass asks first)
        proof.enroll(pg, me)
    again = proof.enroll(pg, me, code=proof.totp(first["secret"]))
    assert again["re_enrolled"] is True and again["secret"] != first["secret"]
    assert again["qr"].startswith("data:image/png;base64,") and again["secret"] in again["uri"]
    assert proof.active_secret(pg, me) == first["secret"]  # the old stands until the new is finished
    with pytest.raises(proof.NotConfirmed):                 # W4: the OLD entry's code refuses at the finish step
        proof.confirm_enrollment(pg, me, proof.totp(first["secret"]))
    assert proof.active_secret(pg, me) == first["secret"]
    proof.confirm_enrollment(pg, me, proof.totp(again["secret"]))   # the NEW entry's code finishes it
    assert proof.active_secret(pg, me) == again["secret"] and proof.enrolled(pg, me)
    with pytest.raises(proof.NotConfirmed):                 # the old code is dead now, everywhere
        proof.enroll(pg, me, code=proof.totp(first["secret"]))


# ---- W7: a name at the head; what a body is --------------------------------------------

def test_w7_a_name_at_the_head_reaches_one_body_and_the_fan_out_stays_for_the_unaddressed(pg, monkeypatch):
    _scope(monkeypatch)
    echo = _body("echo-resident.v0.json"); echo.join(pg)
    lib = _body("librarian-resident.v0.json"); lib.join(pg)
    assert dispatch.address("echo, what is today's date?", ["echo", "librarian"]) == "echo"
    assert dispatch.address("@Librarian: what do you recall?", ["echo", "librarian"]) == "librarian"
    assert dispatch.address("librarian , hi", ["librarian"]) == "librarian"
    assert dispatch.address("what is echo, really?", ["echo"]) is None
    assert dispatch.address("nobody, hello", ["echo"]) is None
    assert dispatch.address("echo,", ["echo"]) is None                  # a name and nothing asked
    both = ["echo", "librarian"]
    assert glass.address_to(pg, "echo, what is today's date?", both) == ["echo"]
    assert glass.address_to(pg, "@librarian what?", both) == both       # no separator: unaddressed
    assert glass.address_to(pg, "what is today's date?", both) == both  # the fan-out stays
    assert glass.address_to(pg, "planner, plan this", both) == both     # not a body of this world
    assert glass.address_to(pg, "Echo: are you there?", None) == ["echo"]
    ids = dispatch.submit_ask(pg, "echo, what is today's date?", person=ME,
                              to=glass.address_to(pg, "echo, what is today's date?", both))
    assert len(ids) == 1 and glass.ask_view(pg, ids[0])["target"] == "echo"


def test_w7_every_body_says_what_it_is_through_the_crew_door_and_the_rails_door(pg, monkeypatch):
    _scope(monkeypatch)
    for t in sorted((SPINE / "templates").glob("*.json")):
        assert json.loads(t.read_text())["nature"].strip(), f"{t.name} has no nature"
    for b in sorted((SPINE / "bindings").glob("*.json")):
        assert json.loads(b.read_text())["nature"].strip(), f"{b.name} has no nature"
    echo = _body("echo-resident.v0.json"); echo.join(pg)
    mon = _body("workspace-firmware.v0.json", binding=SPINE / "bindings" / "monitor.v0.json"); mon.join(pg)
    assert echo.nature == "repeats your words back; no mind"
    assert mon.nature.startswith("reads the Operating State live")            # the binding's word wins
    cards = {c["name"]: c for c in glass.crew_view(pg)}
    assert cards["echo"]["nature"] == "repeats your words back; no mind"
    assert cards["monitor"]["nature"] == mon.nature
    rail = {r["name"]: r for r in glass.residents_view(pg)}
    assert rail["echo"]["nature"] == cards["echo"]["nature"]                    # one picture (rule 7)


# ---- W18: the rail tells the truth ------------------------------------------------------

def test_w18_a_refused_body_is_refused_on_the_card_the_rail_reads(pg, monkeypatch, tmp_path):
    _scope(monkeypatch)
    d = json.loads((SPINE / "templates" / "echo-resident.v0.json").read_text())
    d["name"] = "picky"
    t = tmp_path / "picky.json"; t.write_text(json.dumps(d))
    _body(t, home=tmp_path / "home").join(pg)                                  # seated once, cpu
    d["placement"] = {"metal": "gpu"}; t.write_text(json.dumps(d))
    with pytest.raises(resident.PlacementRefused):
        _body(t, home=tmp_path / "home").join(pg)                              # the same self, refused
    cards = {c["name"]: c for c in glass.crew_view(pg)}
    c = cards["picky"]
    assert c["refused"] is True and c["alive"] is False and c["lives"] == 0
    assert c["placement"]["reasons"] == ["metal gpu is not here (cpu)"]
    assert c["nature"] == "repeats your words back; no mind"                   # what it IS, still said
    assert dispatch.absent(pg, "picky") is not None                            # and the door refuses an ask to it


# ---- W11: the export table's words -----------------------------------------------------

def test_w11_export_rows_carry_the_markers_words_the_target_and_the_refused_kind(pg, monkeypatch):
    _scope(monkeypatch)
    echo = _body("echo-resident.v0.json"); echo.join(pg)
    ses = glass.open_session(pg, ME)
    [obj] = dispatch.submit_ask(pg, "stock the pantry for the week", person=ME, to=["echo"], session=ses)
    _serve(pg, echo, obj)
    [th] = dispatch.submit_ask(pg, "# Notes\n**what** did we say?", person=ME, to=["echo"], session=ses, kind="thought")
    ids = dispatch.submit_ask(pg, "everyone, hello?", person=ME, to=["echo", "ghost"], session=ses)
    b = export.build(pg, person=ME, session=ses)
    rows = b["rows"]
    by_ref = {}
    for r in rows:
        by_ref.setdefault((r["ref"], r["kind"]), r)
    assert by_ref[(obj, "ask")]["marker_words"] == "stock the pantry for the week"   # a root serves itself
    assert by_ref[(obj, "ask")]["target"] == "echo"
    assert by_ref[(th, "ask")]["marker_words"] == "stock the pantry for the week"    # the objective it serves
    assert by_ref[(obj, "reply")]["marker_words"] == "stock the pantry for the week"
    ghost = by_ref[(ids[1], "refused")]
    assert ghost["target"] == "ghost" and ghost["served_by"] == export.KERNEL
    assert "marker_words" in ghost and ghost["words"]["reply"].startswith("ghost is not here")
    assert export.CSV_COLUMNS[-2:] == ("target", "marker_words")
    import csv as _csv
    lines = export.to_csv(b).splitlines()
    assert lines[0].split(",") == list(export.CSV_COLUMNS)
    import io as _io
    csv_rows = {(r["ref"], r["kind"]): r for r in _csv.DictReader(_io.StringIO(export.to_csv(b)))}   # a quoted newline stays
    assert csv_rows[(th, "ask")]["marker_words"] == "stock the pantry for the week"
    assert csv_rows[(th, "ask")]["words"] == "ask: Notes\nwhat did we say?"       # W10: the marks fall away
    assert csv_rows[(ids[1], "refused")]["target"] == "ghost"
    assert export.verify(b)                                                         # the seal still holds
    assert export._plain("- a\n* **b** `c`") == "· a\n· b c"
    # P11: an opt-out session's words never ride marker_words either — the old export law, kept
    out = glass.open_session(pg, ME, opt_out=True)
    secret = "the words that stay in the opt-out " + secrets.token_hex(4)
    [o2] = dispatch.submit_ask(pg, secret, person=ME, to=["echo"], session=out)
    [t2] = dispatch.submit_ask(pg, "a thought under it", person=ME, to=["echo"], session=out, kind="thought")
    b2 = export.build(pg, person=ME, session=out)
    assert all(r["marker_words"] is None for r in b2["rows"]) and secret not in json.dumps(b2)


# ---- the monitor's offer ------------------------------------------------------------------

def test_the_monitors_offer_is_read_from_its_words_and_rides_the_ask_view(pg, monkeypatch):
    _scope(monkeypatch)
    assert monitor.offer_in("I can propose a watch: `bodies_dormant > 0` would catch a dormant body.") == \
        {"words": "bodies_dormant > 0", "ask": "propose a watch that bodies_dormant > 0"}
    assert monitor.offer_in("Shall I propose a watch on `asks_received >= 5`?")["words"] == "asks_received >= 5"
    assert monitor.offer_in("I could propose a watch for that.") is None          # no condition: no button
    assert monitor.offer_in("The value is `bodies_dormant > 0` right now.") is None   # no offer: no button
    assert monitor.offer_in(None) is None
    mon = _body("workspace-firmware.v0.json", binding=SPINE / "bindings" / "monitor.v0.json"); mon.join(pg)
    ses = glass.open_session(pg, ME)
    [aid] = dispatch.submit_ask(pg, "no body is dormant", person=ME, to=["monitor"], session=ses)
    assert glass.ask_view(pg, aid)["offer"] is None                                  # not replied yet
    with pg.transaction():
        pg.cursor().execute("UPDATE spine_asks SET status = 'replied', served_by = %s, replied_at = clock_timestamp(),"
                            " reply = %s WHERE ask_id = %s",
                            (mon.identity.did, "All bodies are alive. I can propose a watch: `bodies_dormant > 0` — red when one goes dormant.", aid))
    v = glass.ask_view(pg, aid)
    assert v["offer"] == {"words": "bodies_dormant > 0", "ask": "propose a watch that bodies_dormant > 0"}
    echo = _body("echo-resident.v0.json"); echo.join(pg)
    [eid] = dispatch.submit_ask(pg, "propose a watch `x > 1`", person=ME, to=["echo"], session=ses)
    _serve(pg, echo, eid)
    assert glass.ask_view(pg, eid)["offer"] is None                                  # only the monitor offers


# ---- W15: citations in human names ------------------------------------------------------

def test_w15_citations_wear_human_names_and_the_path_stays():
    assert mitl.citation_name(".claude/skills/orreth-covenant/SKILL.md", None, 5) == "the covenant, rule 5"
    assert mitl.citation_name("docs/rearch/0005-v1-scope-and-build-plan.md",
                              "## Phase 6 — GOVERNANCE FELT (opened 2026-09-21 — Fable's slicing)") == \
        "the build plan, Phase 6 — GOVERNANCE FELT"
    assert mitl.citation_name("docs/rearch/0004-agent-architecture.md", "## The third kind — firmware agents (block 9 — JB's lock)") == \
        "the agent canon, The third kind — firmware agents"
    assert mitl.citation_name("docs/rearch/0005-v1-scope-and-build-plan.md", "# 0005 — V1 Scope and the Build Plan") == \
        "the build plan, V1 Scope and the Build Plan"
    assert mitl.citation_name("somewhere/else.md", "## A heading") == "else, A heading"
    c = mitl.citations()
    assert c["SKILL.md#3"].startswith("the covenant, rule") and c[".claude/skills/orreth-covenant/SKILL.md#3"] == c["SKILL.md#3"]
    assert any(v == "the build plan, Phase 6 — GOVERNANCE FELT" for k, v in c.items() if k.startswith("docs/rearch/0005"))
    for rel in mitl.ONTOLOGY:
        assert f"{rel}#1" in c and c[f"{rel}#1"].startswith(mitl.TITLES[rel])
    assert mitl.citations() is c                                                    # cached


# ---- W6: the Analyzer's payload ---------------------------------------------------------

def test_w6_the_analyzer_row_carries_blocked_and_the_impact_ask_starts_with_the_change(pg, monkeypatch):
    _scope(monkeypatch)
    markers.seed(pg)
    h = intent.declare(pg, "keep the pantry stocked every day", serves="business", kind="human", by=ME, every_s=86400)
    row = next(o for o in markers.origins(pg) if o["ref"] == h["intention_id"])
    assert row["kind"] == "intention" and row["blocked"] is False and row["blocked_note"] is None
    with pg.transaction():
        pg.cursor().execute("UPDATE spine_intentions SET blocked_crew = 'x', blocked_note = %s WHERE intention_id = %s",
                            ("runner cannot act: librarian said CANNOT ACT — needs a body with the tools for it", h["intention_id"]))
    row = next(o for o in markers.origins(pg) if o["ref"] == h["intention_id"])
    assert row["blocked"] is True and row["blocked_note"].startswith("runner cannot act")
    lst = {i["intention_id"]: i for i in intent.listing(pg)}[h["intention_id"]]
    assert lst["blocked"] is True and lst["blocked_note"] == row["blocked_note"]     # one picture
    ses = glass.open_session(pg, ME)
    out = mitl.impact(pg, {"kind": "intention", "ref": h["intention_id"]}, person=ME, session=ses)
    v = glass.ask_view(pg, out["ask_id"])
    assert v["text"].startswith("the change: keep the pantry stocked every day — expected impact?")
    assert markers.get(pg, v["marker"])["kind"] == "thought"                          # a thought, never an objective
    tw = next(m for m in markers.origin(pg, h["marker"])["tree"] if m["ref"] == out["ask_id"])
    assert tw["words"].startswith("the change: keep the pantry stocked")              # the twig reads the change
