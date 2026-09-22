# PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P6 sp4, placement policy v0 · 2026-09-21
"""Placement policy v0 (canon 0001 P10 · 0004 · 0005 P6 sp4): a template
declares where its body may run; the kernel enforces it at BIRTH. A body
whose placement the ground cannot honor is refused with the reason in
plain words — a recorded fact, never started — and the rig runs without
it; the crew card says where every body stands and why (a refused body
greyed, never absent — rule 7); the join and the export carry the
placement; MITL reads a placement change as consequential (L2); and the
same self stands refused or seated (rule 1: placement never mints a DID).
Plus sp3's wound: a firmware body without a gateway echoes without a
persona."""
import json
import secrets
import time
from pathlib import Path

import pytest

from orreth_spine import dispatch, envelope as ev, export, glass, markers, mitl, placement, resident

from tests.test_glass import _get, _post, _wait_status  # noqa: E402
from tests.test_mind import _rails_up  # noqa: E402

SPINE = Path(__file__).resolve().parents[1]
POLICY = SPINE / "policy" / "covenant-policy.v1.json"
ME = "did:orreth:person:test"
rails = pytest.mark.skipif(not _rails_up(), reason="the rails are not up")


def _body(template, gw=None, binding=None, home=None):
    r = resident.Resident(SPINE / "templates" / template if isinstance(template, str) else template,
                          gateway=gw, binding=binding, home=home)
    r.load_policy(POLICY)
    return r


def _template(tmp_path, base: str, name: str, **placement_) -> Path:
    """A copy of a template of the house wearing a placement — what JB
    does in the walk (copy, set `metal: "gpu"`, relight)."""
    d = json.loads((SPINE / "templates" / base).read_text())
    d["name"] = name
    d["placement"] = placement_
    p = tmp_path / f"{name}.v0.json"
    p.write_text(json.dumps(d))
    return p


def _scope(monkeypatch):
    monkeypatch.setenv("SPINE_SCOPE", "u:law-" + secrets.token_hex(3))


def _serve(pg, body, ask_id, chain=(ME,)):
    body._serve_conn = pg
    with pg.transaction():
        body._serve_ask(pg.cursor(), ask_id, list(chain))


def _events(pg, needle):
    cur = pg.cursor()
    cur.execute("SELECT body FROM spine_outbox WHERE convert_from(body, 'UTF8') LIKE %s"
                " ORDER BY outbox_id", (f"%{needle}%",))
    return [ev.decode(bytes(b)) for (b,) in cur.fetchall()]


def test_a_template_without_a_placement_wears_the_default_and_the_ground_declares_itself(monkeypatch):
    """Defaults applied: every existing body is born exactly as today —
    cell local, no affinity, no secrets, metal any. The ground declares
    its cell and metal from the dials and its secrets by NAME only."""
    assert placement.profile({"name": "echo"}) == {"cell": "local", "affinity": [], "secrets_with": [],
                                                   "metal": "any"}
    assert placement.profile({"placement": {"metal": "gpu", "affinity": ["librarian"]}}) == {
        "cell": "local", "affinity": ["librarian"], "secrets_with": [], "metal": "gpu"}
    with pytest.raises(ValueError, match="metal is one of"):
        placement.profile({"placement": {"metal": "quantum"}})
    monkeypatch.setenv("SPINE_CELL", "gpu-east"); monkeypatch.setenv("SPINE_METAL", "gpu")
    monkeypatch.setenv("A_SECRET_OF_THIS_TEST", "hunter2")
    g = placement.ground_declares()
    assert (g["cell"], g["metal"]) == ("gpu-east", "gpu") and "A_SECRET_OF_THIS_TEST" in g["secrets"]
    assert "hunter2" not in json.dumps(g)                # a value never leaves the environment
    monkeypatch.delenv("SPINE_CELL"); monkeypatch.delenv("SPINE_METAL")
    assert (placement.ground_declares()["cell"], placement.ground_declares()["metal"]) == ("local", "cpu")
    for b in ("echo-resident", "librarian-resident", "firmware-planner", "firmware-critic",
              "firmware-grader", "firmware-mitl", "workspace-firmware"):   # the house declares none
        assert "placement" not in json.loads((SPINE / "templates" / f"{b}.v0.json").read_text())


def test_an_honorable_body_joins_as_before_and_is_the_same_self_in_every_life(pg, monkeypatch, tmp_path):
    """A profile the ground honors: the join lands as today with the
    placement on its row; born twice from the same home it is the SAME
    self (rule 1) — placement never mints a DID."""
    _scope(monkeypatch)
    monkeypatch.setenv("A_SECRET_OF_THIS_TEST", "set")
    t = _template(tmp_path, "echo-resident.v0.json", "keeper", metal="any",
                  secrets_with=["A_SECRET_OF_THIS_TEST"], affinity=["librarian"])
    first = _body(t, home=tmp_path / "home"); made = first.join(pg)
    assert made["placement"] == {"cell": "local", "affinity": ["librarian"],
                                 "secrets_with": ["A_SECRET_OF_THIS_TEST"], "metal": "any"}
    again = _body(t, home=tmp_path / "home"); made2 = again.join(pg)
    assert again.identity.did == first.identity.did and made2["life"] == 2
    cur = pg.cursor()
    cur.execute("SELECT placement FROM spine_joins WHERE did = %s ORDER BY join_id", (first.identity.did,))
    rows = [json.loads(r[0]) for r in cur.fetchall()]
    assert len(rows) == 2 and rows[0] == rows[1] == made["placement"]
    assert placement.refusals(pg) == {}                 # nothing refused here
    card = {c["name"]: c for c in glass.crew_view(pg)}["keeper"]["placement"]
    assert card["why"] == "stands on local · cpu · reaches 1 of 1 secrets · beside librarian (advisory)"
    assert card["secrets"] == [{"name": "A_SECRET_OF_THIS_TEST", "reached": True}] and card["honored"]


def test_a_body_the_ground_cannot_seat_is_refused_with_the_reason_and_the_rest_still_join(pg, monkeypatch, tmp_path):
    """The refusal: cell, metal and secret each named in words; the fact
    on the outbox with the kernel's chain, the profile and an observation
    marker; the same self across two refusals (rule 1); no join row; the
    other bodies join and the crew card shows the refused one greyed with
    its reason — never silently absent (rule 7)."""
    _scope(monkeypatch)
    monkeypatch.delenv("NOT_SET_ANYWHERE", raising=False)
    t = _template(tmp_path, "echo-resident.v0.json", "gpu-body", cell="gpu-east", metal="gpu",
                  secrets_with=["NOT_SET_ANYWHERE"])
    body = _body(t, home=tmp_path / "home")
    with pytest.raises(resident.PlacementRefused) as e:
        body.join(pg)
    assert e.value.reasons == ["cell 'gpu-east' is not this ground ('local')",
                               "metal gpu is not here (cpu)",
                               "secret NOT_SET_ANYWHERE is not reachable here"]
    assert "gpu-body is refused here: cell 'gpu-east'" in str(e.value)
    cur = pg.cursor()
    cur.execute("SELECT count(*) FROM spine_joins WHERE did = %s", (body.identity.did,))
    assert cur.fetchone()[0] == 0                        # never joined, never started
    [fact] = _events(pg, body.identity.did)
    assert fact["type"] == placement.REFUSED and fact["authority_chain"] == ["the kernel"]
    assert fact["payload"]["reasons"] == e.value.reasons and fact["payload"]["name"] == "gpu-body"
    assert fact["payload"]["placement"] == body.placement and fact["payload"]["ground"] == {"cell": "local", "metal": "cpu"}
    assert fact["marker"]["kind"] == "observation" and fact["marker"]["by"] == "the kernel"
    assert markers.get(pg, fact["marker"]["id"])["note"].startswith("gpu-body refused at birth — cell")
    # the same self stands refused twice (rule 1) — two facts, one DID
    with pytest.raises(resident.PlacementRefused):
        _body(t, home=tmp_path / "home").join(pg)
    assert len(_events(pg, body.identity.did)) == 2
    # the rest of the crew joins and the picture stays whole
    echo = _body("echo-resident.v0.json"); echo.join(pg)
    cards = {c["name"]: c for c in glass.crew_view(pg)}
    assert set(cards) == {"echo", "gpu-body"}
    r = cards["gpu-body"]
    assert r["refused"] is True and r["did"] == body.identity.did and r["alive"] is False
    assert r["placement"]["why"] == "refused: " + "; ".join(e.value.reasons)
    assert r["placement"]["secrets"] == [{"name": "NOT_SET_ANYWHERE", "reached": False}]
    assert cards["echo"]["placement"]["why"] == "stands on local · cpu" and "refused" not in cards["echo"]
    # a stranger's target rail never lists a refused body: it cannot be asked
    assert [x["name"] for x in glass.residents_view(pg)] == ["echo"]
    # fixed template, honored birth: the refusal is retired by the join that follows (rule 11: nothing to stop)
    monkeypatch.setenv("NOT_SET_ANYWHERE", "now-set")
    fixed = _template(tmp_path, "echo-resident.v0.json", "gpu-body", secrets_with=["NOT_SET_ANYWHERE"])
    seated = _body(fixed, home=tmp_path / "home"); seated.join(pg)
    assert seated.identity.did == body.identity.did
    c = {c["name"]: c for c in glass.crew_view(pg)}["gpu-body"]
    assert "refused" not in c and c["placement"]["why"] == "stands on local · cpu · reaches 1 of 1 secrets"
    assert len(placement.refusals(pg)) == 1              # the record stays: never a deletion


def test_the_export_rows_carry_the_placement_the_body_was_born_under(pg, monkeypatch, tmp_path):
    """A body's act in the bundle wears cell · metal from its join; an
    ask row (no body acted yet) wears none; the CSV grows the column."""
    _scope(monkeypatch)
    echo = _body(_template(tmp_path, "echo-resident.v0.json", "echo", metal="cpu")); echo.join(pg)
    ses = glass.open_session(pg, ME)
    [a1] = dispatch.submit_ask(pg, "say it back", person=ME, to=["echo"], session=ses)
    _serve(pg, echo, a1)
    b = export.build(pg, person=ME, session=ses)
    by_kind = {r["kind"]: r for r in b["rows"]}
    assert by_kind["ask"]["placement"] is None
    assert by_kind["reply"]["placement"] == {"cell": "local", "metal": "cpu"}
    assert by_kind["reply"]["served_by"] == echo.identity.did
    assert export.verify(b)
    lines = export.to_csv(b).splitlines()
    assert ",placement," in lines[0] and ",local · cpu," in lines[-1]   # W11 grew target · marker_words after it


def test_impact_on_a_placement_change_reads_the_profile_and_answers_consequential(pg, monkeypatch):
    """MITL's door on a placement change: the profile read (the draft's,
    else the body's own), judged against THIS ground, class consequential
    → L2, verdict consider; the answer's shape carries the placement."""
    _scope(monkeypatch)
    lib = _body("librarian-resident.v0.json"); lib.join(pg)
    mitl_body = _body("firmware-mitl.v0.json"); mitl_body.join(pg)
    ses = glass.open_session(pg, ME)
    out = mitl.impact(pg, {"kind": "placement", "ref": "librarian", "words": "move the librarian to gpu-east",
                           "draft": {"placement": {"cell": "gpu-east", "metal": "gpu"}}}, person=ME, session=ses)
    t = out["touches"]
    assert (t["class"], t["level"], out["verdict"]) == ("consequential", "L2", "consider")
    assert t["bodies"] == ["librarian"]
    assert t["placement"] == {"cell": "gpu-east", "affinity": [], "secrets_with": [], "metal": "gpu"}
    assert any(n.startswith("this ground would REFUSE it at birth: refused: cell 'gpu-east' is not this ground")
               for n in t["notes"])
    assert any(n.startswith("librarian stands today on cell 'local' · metal any") for n in t["notes"])
    assert any(l.startswith("placement asked: cell 'gpu-east' · metal gpu") for l in out["ground"])
    # no draft: the body's own placement, honored here
    own = mitl.read_ground(pg, {"kind": "placement", "ref": "librarian"})
    assert own["placement"]["cell"] == "local" and own["notes"][0].startswith("this ground honors it: stands on local · cpu")
    assert (own["class"], own["level"], mitl.verdict(own)) == ("consequential", "L2", "consider")
    # affinity is advisory: said so, never a refusal
    adv = mitl.read_ground(pg, {"kind": "placement", "draft": {"placement": {"affinity": ["echo"]}}})
    assert adv["notes"][0].startswith("this ground honors it") and any("advisory" in n for n in adv["notes"])


def test_a_firmware_body_without_a_gateway_echoes_without_a_persona(pg, monkeypatch, tmp_path):
    """sp3's wound: planner · critic · grader carried no persona and the
    echo fallback raised KeyError. Cured: each firmware template wears a
    one-line persona, and a template that still has none is named
    plainly ('the X, a firmware body')."""
    _scope(monkeypatch)
    for fn in ("planner", "critic", "grader"):
        assert json.loads((SPINE / "templates" / f"firmware-{fn}.v0.json").read_text())["persona"].startswith(f"the {fn}, a firmware body")
    planner = _body("firmware-planner.v0.json"); planner.join(pg)     # no gateway
    ses = glass.open_session(pg, ME)
    [a] = dispatch.submit_ask(pg, "plan it", person=ME, to=["planner"], session=ses)
    _serve(pg, planner, a)
    cur = pg.cursor(); cur.execute("SELECT reply FROM spine_asks WHERE ask_id = %s", (a,))
    assert cur.fetchone()[0].startswith("I am planner — the planner, a firmware body of Orreth")
    bare = json.loads((SPINE / "templates" / "firmware-planner.v0.json").read_text())
    bare.pop("persona"); bare["name"] = "nameless"
    p = tmp_path / "nameless.v0.json"; p.write_text(json.dumps(bare))
    body = _body(p); body.join(pg)
    [a2] = dispatch.submit_ask(pg, "plan it", person=ME, to=["nameless"], session=ses)
    _serve(pg, body, a2)
    cur.execute("SELECT reply FROM spine_asks WHERE ask_id = %s", (a2,))
    assert cur.fetchone()[0].startswith("I am nameless — the nameless, a firmware body. You asked:")


@rails
def test_the_rig_stays_up_without_a_refused_body_and_the_crew_door_says_why(pg, monkeypatch, tmp_path):
    """The whole rig with a librarian that asks for gpu on a cpu ground:
    the librarian is refused at birth and never serves; the echo and the
    rest breathe and answer; GET /crew shows the why-line on every seated
    card and the refused card for the librarian; the refusal is on the
    outbox with the kernel's chain."""
    _scope(monkeypatch)
    monkeypatch.delenv("SPINE_METAL", raising=False)
    t = _template(tmp_path, "librarian-resident.v0.json", "librarian", metal="gpu")
    rig = glass.BridgeRig(gateway=None, port=0, home=None, template=t).start()
    try:
        assert rig.wait_ready(30)
        s, filed = _post(rig.port, "/ask", {"text": "are you there?", "to": ["echo"], "person": ME})
        assert s == 201
        view = _wait_status(rig.port, filed["ids"][0], ("replied",))
        assert "are you there?" in view["reply"]
        for _ in range(40):                              # the refusal lands at birth
            _s, body = _get(rig.port, "/crew")
            cards = {c["name"]: c for c in json.loads(body)["crew"]}
            if "librarian" in cards and cards["librarian"].get("refused"):
                break
            time.sleep(0.25)
        assert cards["librarian"]["refused"] is True
        assert cards["librarian"]["placement"]["why"] == "refused: metal gpu is not here (cpu)"
        assert cards["librarian"]["did"] == rig.resident.identity.did
        assert cards["echo"]["placement"]["why"] == "stands on local · cpu"
        assert all(cards[n]["placement"]["why"] == "stands on local · cpu"
                   for n in ("planner", "critic", "grader", "mitl", "crew", "monitor"))
        import psycopg
        with psycopg.connect(rig.dsn, autocommit=True) as conn:   # the rig's OWN ground (not the
            cur = conn.cursor()                                    # session's test schema)
            cur.execute("SELECT count(*) FROM spine_joins WHERE did = %s", (rig.resident.identity.did,))
            assert cur.fetchone()[0] == 0                # never joined
            facts = [e for e in _events(conn, rig.resident.identity.did) if e["type"] == placement.REFUSED]
        assert facts and facts[0]["authority_chain"] == ["the kernel"]
        assert facts[0]["payload"]["reasons"] == ["metal gpu is not here (cpu)"]
        assert sum(t.is_alive() for t in rig._threads) == len(rig._threads) - 1   # one seat empty, the rest breathe
    finally:
        rig.stop()
