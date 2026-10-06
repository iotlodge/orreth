# PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch Phase 8 THE WORKSHOP sp1, THE PATH · 2026-10-05
"""THE PATH's laws on the reference (canon 0010 lock 2 · 0005 Phase 8 sp1): the universe's own
level row at light wearing the cell's declared mode, tightened on a relight and never loosened;
the crew manifest's floors and rooms declared at light; a floor or room opened on a person's
word through the kernel's held act (L2), its refusals in words; a body seated on a floor seen
from the universe (the crew door, the address, the roster — one world, one picture); the
listing's roll-up; the cascade at a path."""
import json
import secrets
from pathlib import Path

import pytest

from orreth_spine import dispatch, envelope as ev, glass, levels, outbox, presence, proof, resident

SPINE = Path(__file__).resolve().parents[1]
POLICY = SPINE / "policy" / "covenant-policy.v1.json"
PERSON = "did:orreth:person:test"


def _world(monkeypatch, mode=None):
    u = "u:law-" + secrets.token_hex(3)
    monkeypatch.setenv("SPINE_SCOPE", u)
    if mode is None:
        monkeypatch.delenv("SPINE_MODE", raising=False)
    else:
        monkeypatch.setenv("SPINE_MODE", mode)
    return u


def _body(template, scope=None):
    r = resident.Resident(SPINE / "templates" / template, scope=scope)
    r.load_policy(POLICY)
    return r


def _facts(pg, type_):
    cur = pg.cursor()
    cur.execute("SELECT body FROM spine_outbox ORDER BY outbox_id")
    out = []
    for (body,) in cur.fetchall():
        try:
            e = ev.decode(bytes(body))
        except Exception:                       # noqa: BLE001 — a non-envelope row is not a fact
            continue
        if e.get("type") == type_:
            out.append(e)
    return out


def test_the_universe_opens_at_light_in_its_declared_mode_and_only_tightens(pg, monkeypatch):
    u = _world(monkeypatch)
    row = levels.ensure_universe(pg, u)
    assert (row["level"], row["mode"], row["parent"], row["opened_by"]) == ("universe", "dev", None, "the kernel")
    assert [f["payload"]["reason"] for f in _facts(pg, levels.LEVEL_OPENED) if f["payload"]["ref"] == u] == ["opened at light"]
    assert levels.ensure_universe(pg, u)["mode"] == "dev"                    # a relight says nothing new
    levels.declare(pg, u, {"format": "orreth-crew/1", "seats": [], "levels": [{"at": "f:ops"}, {"at": "f:ops/r:lab", "experiment": True}]})
    assert levels.ensure_universe(pg, u, "prod")["mode"] == "prod"          # tightened, recorded
    assert [f["payload"]["reason"] for f in _facts(pg, levels.LEVEL_OPENED) if f["payload"]["ref"] == u] == \
        ["opened at light", "tightened at light"]
    # W98: the floor and the room tightened WITH the universe — a level looser than its parent never stands
    assert levels.row(pg, f"{u}/f:ops")["mode"] == "prod" and levels.row(pg, f"{u}/f:ops/r:lab")["mode"] == "prod"
    assert levels.row(pg, f"{u}/f:ops/r:lab")["experiment"] is True
    assert [f["payload"]["reason"] for f in _facts(pg, levels.LEVEL_OPENED) if f["payload"]["ref"] == f"{u}/f:ops"] == \
        ["declared by the crew manifest", "tightened with the universe"]
    with pytest.raises(levels.LevelRefused, match="mode only tightens down the path"):
        levels.ensure_universe(pg, u, "dev")                                 # a prod universe never lights as dev
    with pytest.raises(levels.LevelRefused, match="dev or prod"):
        levels.ensure_universe(pg, u, "staging")


def test_the_crew_manifest_declares_floors_and_rooms_at_light(pg, monkeypatch):
    u = _world(monkeypatch)
    levels.ensure_universe(pg, u)
    manifest = {"format": "orreth-crew/1", "seats": [{"template": "templates/echo-resident.v0.json", "at": "f:ops"}],
                "levels": [{"at": "f:ops", "words": "the operations floor"},
                           {"at": "f:ops/r:lab", "experiment": True, "mode": "prod"}]}
    opened = levels.declare(pg, u, manifest)
    assert [(o["path"], o["level"], o["mode"], o["experiment"], o["opened_by"]) for o in opened] == \
        [(f"{u}/f:ops", "floor", "dev", False, "the crew manifest"), (f"{u}/f:ops/r:lab", "room", "prod", True, "the crew manifest")]
    assert levels.declare(pg, u, manifest) == []                             # a relight declares nothing twice
    assert [f["payload"]["reason"] for f in _facts(pg, levels.LEVEL_OPENED) if f["payload"]["ref"] == f"{u}/f:ops"] == \
        ["declared by the crew manifest"]
    with pytest.raises(levels.LevelRefused, match="is not open — declare the floor first"):
        levels.declare(pg, u, {"format": "orreth-crew/1", "seats": [], "levels": [{"at": "f:two/r:x"}]})
    with pytest.raises(levels.LevelRefused, match="mode only tightens"):       # a dev room under a PROD floor loosens
        levels.declare(pg, u, {"format": "orreth-crew/1", "seats": [],
                               "levels": [{"at": "f:prod", "mode": "prod"}, {"at": "f:prod/r:loose", "mode": "dev"}]})
    assert levels.row(pg, f"{u}/f:prod")["mode"] == "prod"                       # the lawful floor stood before the refusal
    assert levels.context(pg, f"{u}/f:ops/r:lab")["mode"] == "prod"         # a prod room under a dev floor: tighter, lawful


def test_a_level_opens_on_a_persons_word_held_at_l2_and_refuses_in_words(pg, monkeypatch):
    u = _world(monkeypatch)
    levels.ensure_universe(pg, u)
    made = levels.hold_open(pg, {"parent": u, "level": "floor", "name": "ops"}, person=PERSON)
    assert (made["level"], made["class"], made["path"]) == ("L2", "consequential", f"{u}/f:ops")
    cur = pg.cursor()
    cur.execute("SELECT status, held, served_by FROM spine_asks WHERE ask_id = %s", (made["held"],))
    status, held, served_by = cur.fetchone()
    assert status == "awaiting-confirm" and served_by == "the kernel"
    assert json.loads(held)["tool"] == "level.open" and json.loads(held)["args"]["mode"] == "dev"
    assert levels.row(pg, f"{u}/f:ops") is None                             # nothing stands before the yes
    out = proof.settle_kernel_act(pg, made["held"], approve=True, by=PERSON)
    assert out["status"] == "replied" and out["proof"] == "L2"
    assert f"floor ops of universe {u[2:]} is open (dev)" in out["reply"]
    row = levels.row(pg, f"{u}/f:ops")
    assert (row["level"], row["mode"], row["opened_by"], row["ask"]) == ("floor", "dev", PERSON, made["held"])
    f = [f for f in _facts(pg, levels.LEVEL_OPENED) if f["payload"]["ref"] == f"{u}/f:ops"][0]
    assert f["payload"]["reason"] == "opened on a person's word" and f["authority_chain"] == [PERSON, "the kernel"]
    assert f["universe_id"] == u and f["scope_path"] == f"{u}/f:ops"
    # the refusals, in words, before anything is held
    with pytest.raises(levels.LevelRefused, match="is already open"):
        levels.hold_open(pg, {"parent": u, "level": "floor", "name": "ops"}, person=PERSON)
    with pytest.raises(levels.LevelRefused, match="a room opens on a floor"):
        levels.hold_open(pg, {"parent": u, "level": "room", "name": "bob"}, person=PERSON)
    with pytest.raises(levels.LevelRefused, match="only a room opens as an experiment room"):
        levels.hold_open(pg, {"parent": u, "level": "floor", "name": "lab", "experiment": True}, person=PERSON)
    with pytest.raises(levels.LevelRefused, match="is not open here"):
        levels.hold_open(pg, {"parent": f"{u}/f:nowhere", "level": "room", "name": "bob"}, person=PERSON)
    # a prod floor's room may not loosen to dev; an experiment room on it may open as prod
    made = levels.hold_open(pg, {"parent": u, "level": "floor", "name": "prodfloor", "mode": "prod"}, person=PERSON)
    proof.settle_kernel_act(pg, made["held"], approve=True, by=PERSON)
    with pytest.raises(levels.LevelRefused, match="mode only tightens down the path"):
        levels.hold_open(pg, {"parent": f"{u}/f:prodfloor", "level": "room", "name": "loose", "mode": "dev"}, person=PERSON)
    made = levels.hold_open(pg, {"parent": f"{u}/f:prodfloor", "level": "room", "name": "lab", "experiment": True}, person=PERSON)
    out = proof.settle_kernel_act(pg, made["held"], approve=True, by=PERSON)
    assert "an experiment room" in out["reply"]
    assert levels.row(pg, f"{u}/f:prodfloor/r:lab")["experiment"] is True
    # a no: nothing stands, recorded
    made = levels.hold_open(pg, {"parent": u, "level": "floor", "name": "never"}, person=PERSON)
    out = proof.settle_kernel_act(pg, made["held"], approve=False, by=PERSON)
    assert out["status"] == "cancelled" and levels.row(pg, f"{u}/f:never") is None


def test_a_body_on_a_floor_is_seen_from_the_universe_and_the_listing_rolls_up(pg, monkeypatch):
    u = _world(monkeypatch)
    levels.ensure_universe(pg, u)
    levels.declare(pg, u, {"format": "orreth-crew/1", "seats": [], "levels": [{"at": "f:ops"}, {"at": "f:ops/r:bob"}]})
    lib = _body("librarian-resident.v0.json"); lib.join(pg)                       # at the universe
    echo = _body("echo-resident.v0.json", scope=f"{u}/f:ops"); echo.join(pg)        # on the floor
    presence.renew(pg, echo.identity.did, echo.name, echo.kind, scope=echo.scope)
    cur = pg.cursor()
    cur.execute("SELECT scope FROM spine_joins WHERE did = %s", (echo.identity.did,))
    assert cur.fetchone()[0] == f"{u}/f:ops"                                        # the join wears the level
    joined = [f for f in _facts(pg, "orreth.body.joined.v1") if f["payload"]["did"] == echo.identity.did][0]
    assert (joined["universe_id"], joined["scope_path"]) == (u, f"{u}/f:ops")        # the fact: universe, and the path
    cards = {c["name"]: c for c in glass.crew_view(pg)}                             # the crew door sees both (rule 7)
    assert cards["echo"]["scope"] == f"{u}/f:ops" and cards["librarian"]["scope"] == u
    assert {r["name"]: r["scope"] for r in presence.roster(pg)} == {"echo": f"{u}/f:ops"}
    assert dispatch.absent(pg, "echo") is None                                       # addressable from the universe
    assert {r["name"] for r in glass.residents_view(pg)} == {"echo", "librarian"}
    # an ask the floor's body served counts on its level, and rolls up to the universe
    aid = dispatch.submit_ask(pg, "served once", person=PERSON)
    cur.execute("UPDATE spine_asks SET status = 'replied', served_by = %s, reply = 'x', replied_at = now() WHERE ask_id = %s",
                (echo.identity.did, aid))
    rows = {r["path"]: r for r in levels.listing(pg, u)}
    assert list(levels.listing(pg, u)[0].keys())[:3] == ["path", "scope", "level"]
    assert rows[u]["here"] == {"bodies": 1, "asks_served": 0, "usd": 0.0}
    assert rows[f"{u}/f:ops"]["here"] == {"bodies": 1, "asks_served": 1, "usd": 0.0}
    assert rows[f"{u}/f:ops/r:bob"]["here"]["bodies"] == 0
    assert (rows[u]["rolled"]["bodies"], rows[u]["rolled"]["asks_served"]) == (2, 1)
    assert (rows[f"{u}/f:ops"]["rolled"]["bodies"], rows[f"{u}/f:ops"]["rolled"]["asks_served"]) == (1, 1)
    assert rows[u]["rolled"]["bundle"]["compliance"] == "clean"
    # the seat words name the level
    assert f"THE WORLD you serve in is {u}/f:ops (floor ops of universe {u[2:]})" in echo.seat_words(pg, None)


def test_the_cascade_at_a_path_folds_the_levels_root_to_leaf(pg, monkeypatch):
    u = _world(monkeypatch)
    levels.ensure_universe(pg, u)
    levels.declare(pg, u, {"format": "orreth-crew/1", "seats": [],
                           "levels": [{"at": "f:ops", "declares": {"soft": {"tone": {"value": "wild", "version": "1"}}, "skills": {"pitching": "1.0.0"}}},
                                      {"at": "f:ops/r:bob", "mode": "prod",
                                       "declares": {"soft": {"tone": {"value": "REAL", "version": "1"}}, "skills": {"pitching": "2.0.0", "scouting": "1.0.0"}}}]})
    rc = levels.context(pg, f"{u}/f:ops/r:bob")
    assert [t["scope"] for t in rc["as_of"]] == [u, f"{u}/f:ops", f"{u}/f:ops/r:bob"]
    assert [t["mode"] for t in rc["as_of"]] == ["dev", "dev", "prod"] and rc["mode"] == "prod"
    assert rc["soft"]["tone"] == {"value": "REAL", "from_scope": f"{u}/f:ops/r:bob", "version": "1"}
    assert rc["skills"] == {"pitching": "2.0.0", "scouting": "1.0.0"}
    assert len(rc["floors"]) == len(levels.policy_floors()) >= 1                   # the policy sheet's rules are the universe's floors
    assert rc["id"].startswith("sha256:") and rc["id"] == levels.context(pg, f"{u}/f:ops/r:bob")["id"]
    assert levels.context(pg, f"{u}/f:ops")["soft"]["tone"]["value"] == "wild" and levels.context(pg, u)["soft"] == {}
    with pytest.raises(levels.LevelRefused, match="is not open here"):
        levels.context(pg, f"{u}/f:nowhere")
