# PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P6 sp3, MITL v0 + the impact door · 2026-09-21
"""MITL v0 (canon 0001 · 0004 · 0005 P6 sp3): the Master Mind In the Loop
is a firmware body of the third kind that thinks only through the gateway
(rule 5), wears the Orreth ontology v0 acquired through the librarian's
own door with provenance on every passage, is summoned and dismissed as
recorded facts with the human's chain (rule 11), answers the impact door
with the ground read and the verdict judged by sp1's ladder — filed under
the change's marker — and never confirms (rule 2: it weighs, the human
cuts). Ground only: no rails, no real mind."""
import json
import secrets
from pathlib import Path

import pytest

from orreth_spine import dispatch, envelope as ev, gateway, glass, intent, markers, mitl, proof, resident, tools
from orreth_spine.store import OrrethStore

SPINE = Path(__file__).resolve().parents[1]
POLICY = SPINE / "policy" / "covenant-policy.v1.json"
ME = "did:orreth:person:test"


def _body(template, gw=None, binding=None):
    r = resident.Resident(SPINE / "templates" / template, gateway=gw, binding=binding)
    r.load_policy(POLICY)
    return r


def _events_for(pg, ref):
    cur = pg.cursor()
    cur.execute("SELECT body FROM spine_outbox WHERE convert_from(body, 'UTF8') LIKE %s"
                " ORDER BY outbox_id", (f"%{ref}%",))
    return [ev.decode(bytes(b)) for (b,) in cur.fetchall()]


def _serve(pg, body, ask_id, chain):
    body._serve_conn = pg
    with pg.transaction():
        body._serve_ask(pg.cursor(), ask_id, chain)


def _kernel_intention(pg) -> dict:
    markers.seed(pg)
    return intent.declared(pg, f"keep the {secrets.token_hex(2)} bench green", serves="resiliency",
                           kind="kernel", by="the kernel", interests=[intent.WATCH_RED],
                           planner="planner", runner="librarian")


def _scope(monkeypatch):
    monkeypatch.setenv("SPINE_SCOPE", "u:law-" + secrets.token_hex(3))


def test_mitl_is_born_of_the_third_kind_and_thinks_only_through_the_gateway(pg, monkeypatch):
    """The same body of laws as planner · critic · grader: kind firmware,
    named by its function; its ask is a thought (an include); every
    thought lands a meter line for ITS self with the model its template
    declares; without a gateway it never finds an unmetered door."""
    _scope(monkeypatch)
    gw = gateway.FakeGateway(reply="WHO AND WHAT IT TOUCHES: nothing yet. THE RISK: none. "
                                   "WHAT TO WATCH AFTER: the meter. low")
    m = _body("firmware-mitl.v0.json", gw)
    m.join(pg)
    assert (m.name, m.kind, m.function) == ("mitl", "firmware", "impact")
    assert "tools:acquire" in m.template["capabilities"]
    assert m.identity.did.startswith("did:orreth:agent:")
    kinds = {x["name"]: x["kind"] for x in glass.residents_view(pg)}
    assert kinds == {"mitl": "firmware"}
    ses = glass.open_session(pg, ME)
    [aid] = dispatch.submit_ask(pg, "what does the canon say about the meter?", to=["mitl"], session=ses)
    assert markers.get(pg, glass.ask_view(pg, aid)["marker"])["kind"] == "thought"   # an include
    _serve(pg, m, aid, [ME])
    v = glass.ask_view(pg, aid)
    assert v["status"] == "replied" and v["reply"] == gw.reply and v["served_by"] == m.identity.did
    [(model, t_in, t_out)] = gateway.meter_lines(pg, m.identity.did)          # ONE line, its model
    assert model == "claude-haiku-4-5-20251001" and t_in > 0 and t_out > 0
    assert gw.calls[0]["system"] == mitl.SYSTEM and "the human cuts" in gw.calls[0]["system"]
    assert any("metered gateway" in n for n in v["journey"])
    reply_ev = [e for e in _events_for(pg, aid) if e["type"] == resident.REPLY]
    assert reply_ev[0]["authority_chain"] == [ME, m.identity.did]                   # AG-7: H → mitl
    bare = _body("firmware-mitl.v0.json", None)                                    # no gateway:
    bare.join(pg)                                                                  # the deterministic
    [aid2] = dispatch.submit_ask(pg, "and now?", to=["mitl"], session=ses)         # graph, no meter,
    _serve(pg, bare, aid2, [ME])                                                   # no model, ever
    assert glass.ask_view(pg, aid2)["status"] == "replied"
    assert gateway.meter_lines(pg, bare.identity.did) == []


def test_the_ontology_is_acquired_with_provenance_and_re_acquire_lands_nothing(pg, monkeypatch):
    """The canon lands passage by passage through the SAME acquire door
    the librarian uses — journaled, the hop on the wire, under one action
    marker — every row wearing its source path (the key), its sha256 (the
    hash) and when it was acquired; the words are exact; recall over the
    corpus answers from the covenant; acquiring again lands nothing."""
    _scope(monkeypatch)
    m = _body("firmware-mitl.v0.json")
    m.join(pg)
    made = mitl.acquire_ontology(pg, m)
    assert made["acquired"] > 0 and made["files"] == len(mitl.ONTOLOGY) and made["missing"] == []
    rows = mitl.ontology(pg)
    assert len(rows) == made["acquired"]
    assert {r["path"] for r in rows} == set(mitl.ONTOLOGY)
    assert all(r["hash"].startswith("sha256:") and r["acquired_at"] and r["passage"] >= 1 for r in rows)
    st = OrrethStore(pg, by_did=m.identity.did)
    covenant = mitl.REPO / ".claude/skills/orreth-covenant/SKILL.md"
    first = next(r for r in rows if r["path"].endswith("SKILL.md") and r["passage"] == 1)
    assert st.get("mitl", first["key"]) == mitl.passages(covenant.read_text("utf-8"))[0]
    assert first["hash"] == ev.content_hash(st.get("mitl", first["key"]))               # sha256 of the words
    calls = tools.journal(pg, m.identity.did)                                            # the librarian's door
    assert len(calls) == made["acquired"] and all(t == "acquire" and ok for t, ok in calls)
    hops = [e for e in _events_for(pg, m.identity.did) if e["type"] == tools.TOOL_CALLED]
    assert len(hops) == made["acquired"]
    assert all(e["authority_chain"] == [m.identity.did, "tool:acquire"] for e in hops)   # the hop on the wire
    assert all(e["marker"]["kind"] == "action" and e["marker"]["parent"] == made["marker"] for e in hops)
    assert "ontology v0" in markers.get(pg, made["marker"])["note"]
    hits = st.search("mitl", "nothing grades its own yardstick", limit=3)
    assert hits and any("orreth-covenant/SKILL.md" in h["key"] for h in hits)
    again = mitl.acquire_ontology(pg, m)                                                 # idempotent
    assert again == {"acquired": 0, "files": len(mitl.ONTOLOGY), "missing": [], "marker": None}
    assert len(mitl.ontology(pg)) == len(rows) and len(tools.journal(pg, m.identity.did)) == len(calls)
    assert mitl.acquire_ontology(pg, m, root="/nowhere")["missing"] == list(mitl.ONTOLOGY)   # honest


def test_summon_and_dismiss_are_recorded_facts_with_the_chain(pg, monkeypatch):
    """The soft toggle (rule 11): summoned and dismissed are both facts on
    the rail wearing the human's chain and an action marker under the
    session's latest objective — rows that stay, never a deletion."""
    _scope(monkeypatch)
    ses = glass.open_session(pg, ME)
    obj = dispatch.submit_ask(pg, "an objective first", session=ses)
    obj_marker = glass.ask_view(pg, obj)["marker"]
    assert mitl.summoned(pg, ses) is False
    s = mitl.summon(pg, ME, ses)
    assert s["summoned"] and s["expansion"] == "the Master Mind In the Loop" and mitl.summoned(pg, ses)
    [e] = [e for e in _events_for(pg, ses) if e["type"] == mitl.SUMMONED]
    assert e["authority_chain"] == [ME] and e["payload"]["by"] == ME and e["payload"]["body"] == "mitl"
    assert e["marker"] == {"kind": "action", "id": s["marker"], "parent": obj_marker, "by": ME}
    assert markers.get(pg, s["marker"])["note"].startswith("MITL summoned")
    d = mitl.summon(pg, ME, ses, on=False)
    assert d["summoned"] is False and mitl.summoned(pg, ses) is False
    [e2] = [e for e in _events_for(pg, ses) if e["type"] == mitl.DISMISSED]
    assert e2["authority_chain"] == [ME] and e2["marker"]["parent"] == obj_marker
    cur = pg.cursor()
    cur.execute("SELECT state FROM spine_mitl WHERE session = %s ORDER BY row_id", (ses,))
    assert [r[0] for r in cur.fetchall()] == ["summoned", "dismissed"]           # both stay
    assert mitl.summoned(pg, None, ME) is False                                   # outside any session
    mitl.summon(pg, ME, None)
    assert mitl.summoned(pg, None, ME) is True and mitl.summoned(pg, ses) is False


def test_impact_on_a_kernel_intention_stop_is_grave_and_files_under_its_marker(pg, monkeypatch):
    """The ladder is law, not opinion: a change to one of the kernel's
    intentions — named directly, or through the held stop — is 'grave —
    needs L3' before any brain speaks; MITL's ask is a thought under the
    intention's own marker (or the held ask's), in the session, to mitl;
    a human's standing intention is 'consider'."""
    _scope(monkeypatch)
    _body("firmware-planner.v0.json").join(pg)
    r = _kernel_intention(pg)
    ses = glass.open_session(pg, ME)
    out = mitl.impact(pg, {"kind": "intention", "ref": r["intention_id"]}, person=ME, session=ses)
    assert out["contract"] == "orreth.impact/1" and out["served_by"] == "mitl"
    assert out["verdict"] == "grave — needs L3"
    t = out["touches"]
    assert t["kernel"] is True and (t["class"], t["level"]) == ("grave", "L3-master")
    assert {"planner", "librarian"} <= set(t["bodies"]) and t["intentions"][0]["kind"] == "kernel"
    assert out["marker"] == r["marker"]                                            # filed under it
    v = glass.ask_view(pg, out["ask_id"])
    assert v["target"] == "mitl" and v["session"] == ses and v["status"] == "received"
    mk = markers.get(pg, v["marker"])
    assert mk["kind"] == "thought" and mk["parent"] == r["marker"]
    assert "VERDICT BY THE LADDER: grave — needs L3" in v["text"] and "THE GROUND" in v["text"]
    assert [m["kind"] for m in markers.ancestry(pg, v["marker"])] == ["thought", "intention"]
    with pytest.raises(proof.ProofRequired) as pr:                                 # the held stop
        intent.stop(pg, r["intention_id"], by=ME)
    held = proof.hold_kernel_act(pg, text=pr.value.what, person=ME, tool="intent.stop",
                                 args={"intention_id": r["intention_id"]}, level="L3-master", session=ses)
    out2 = mitl.impact(pg, {"kind": "intention", "ref": held, "words": "stop it"}, person=ME, session=ses)
    assert out2["verdict"] == "grave — needs L3" and out2["touches"]["kernel"] is True
    held_marker = glass.ask_view(pg, held)["marker"]
    assert out2["marker"] == held_marker
    assert markers.get(pg, glass.ask_view(pg, out2["ask_id"])["marker"])["parent"] == held_marker
    assert "H → a master → the kernel (the stop)" in out2["touches"]["chains"]
    h = intent.declare(pg, "keep the pantry stocked every day", serves="business", kind="human",
                       by=ME, every_s=86400)
    out3 = mitl.impact(pg, {"kind": "intention", "ref": h["intention_id"]}, person=ME, session=ses)
    assert out3["verdict"] == "consider" and out3["touches"]["kernel"] is False
    assert mitl.verdict({"kind": "act", "class": "grave", "level": "L3-code"}) == "grave — needs L3"
    assert mitl.verdict({"kind": "act", "class": "routine", "level": "L1"}) == "low"
    with pytest.raises(ValueError):
        mitl.read_ground(pg, {"kind": "wish"})


def test_impact_on_a_new_watch_names_the_monitor_body_and_the_metric(pg, monkeypatch):
    """A watch about to be declared: the ground names the monitor body,
    the metric, the chain through the add-watch door, the intentions
    that wake on watch-red and their planners, the cost so far; the class
    is consequential (L2) so the verdict is 'consider'; MITL's words come
    through the gateway with the canon packed in, and land as the reply."""
    _scope(monkeypatch)
    mon = _body("workspace-firmware.v0.json", binding=SPINE / "bindings" / "monitor.v0.json")
    mon.join(pg)
    planner = _body("firmware-planner.v0.json", gateway.FakeGateway(reply="plan"))
    planner.join(pg)
    [pa] = dispatch.submit_ask(pg, "warm the meter", to=["planner"])
    _serve(pg, planner, pa, [ME])                                                  # a cost to name
    r = _kernel_intention(pg)
    gw = gateway.FakeGateway(reply="WHO AND WHAT IT TOUCHES: the monitor body, the Resiliency "
                                   "intention. THE RISK: a red watch wakes the loop. WHAT TO WATCH "
                                   "AFTER: the planner's objectives. consider")
    m = _body("firmware-mitl.v0.json", gw)
    m.join(pg)
    mitl.acquire_ontology(pg, m)
    ses = glass.open_session(pg, ME)
    out = mitl.impact(pg, {"kind": "watch", "words": "no body is dormant",
                           "draft": {"name": "no body is dormant", "metric": "bodies_dormant",
                                     "op": "<=", "threshold": 0}}, person=ME, session=ses)
    t = out["touches"]
    assert "monitor" in t["bodies"] and t["metric"] == "bodies_dormant"
    assert (t["class"], t["level"]) == ("consequential", "L2") and out["verdict"] == "consider"
    assert "H → monitor → tool:add-watch" in t["chains"]
    assert t["intentions"][0]["intention_id"] == r["intention_id"] and "planner" in t["bodies"]
    assert t["cost"]["planner"]["thoughts"] == 1 and t["cost"]["planner"]["tokens"] > 0
    assert out["marker"] is None                                                   # no objective yet:
    _serve(pg, m, out["ask_id"], [ME])                                             # a root thought
    v = glass.ask_view(pg, out["ask_id"])
    assert v["status"] == "replied" and v["served_by"] == m.identity.did and v["reply"] == gw.reply
    assert len(gateway.meter_lines(pg, m.identity.did)) == 1                       # on the meter
    prompt = gw.calls[0]["prompt"]
    assert "THE GROUND" in prompt and "monitor (firmware)" in prompt and "metric: bodies_dormant" in prompt
    assert "the canon says [" in prompt and "docs/rearch/" in prompt              # the ontology, recalled
    words = mitl.read_ground(pg, {"kind": "watch", "words": "when bodies_alive drops"})
    assert words["metric"] == "bodies_alive"                                       # the metric from words
    assert mitl.read_ground(pg, {"kind": "watch", "words": "no body is dormant"})["metric"] == "bodies_dormant"
    assert mitl.read_ground(pg, {"kind": "watch", "words": "the outbox never backs up"})["metric"] == "outbox_pending"
    assert mitl.read_ground(pg, {"kind": "watch", "words": "the sky is blue"})["metric"] is None
    low = mitl.impact(pg, {"kind": "act", "draft": {"tool": "weather"}}, person=ME, session=ses)
    assert low["verdict"] == "low" and low["touches"]["level"] == "L1"
    grave = mitl.read_ground(pg, {"kind": "act", "draft": {"tool": "erase-record"}})
    assert mitl.verdict(grave) == "grave — needs L3" and grave["level"] == "L3-code"
    place = mitl.read_ground(pg, {"kind": "placement", "ref": "monitor"})
    assert [b["name"] for b in place["bodies"]] == ["monitor"]       # P6 sp4 replaced the "not
    assert place["notes"][0].startswith("this ground honors it: stands on ")   # built yet" note
    assert (place["class"], place["level"]) == ("consequential", "L2")   # by the rule itself


def test_mitl_never_confirms_its_identity_wears_the_one_face_at_the_door(pg, monkeypatch):
    """Scribe-class (rule 2): MITL weighs, the human cuts. Its self at the
    confirm door — as a yes or a cancel, at L2 or L3, even declared a
    master — is refused with the ONE face, and nothing ran."""
    _scope(monkeypatch)
    m = _body("firmware-mitl.v0.json")
    m.join(pg)
    r = _kernel_intention(pg)
    with pytest.raises(proof.ProofRequired) as pr:
        intent.stop(pg, r["intention_id"], by=ME)
    held = proof.hold_kernel_act(pg, text=pr.value.what, person=ME, tool="intent.stop",
                                 args={"intention_id": r["intention_id"]}, level="L3-master")
    proof.declare_master(pg, m.identity.did, by=ME)                              # even as a master
    for approve in (True, False):
        with pytest.raises(proof.NotConfirmed):
            dispatch.confirm_ask(pg, held, approve=approve, person=m.identity.did)
    assert intent.get(pg, r["intention_id"])["active"] is True
    assert glass.ask_view(pg, held)["status"] == "awaiting-confirm"
    l2 = "ask_" + secrets.token_hex(8)                                            # an L2 hold, by hand
    with pg.transaction():
        pg.cursor().execute(
            "INSERT INTO spine_asks (ask_id, text, person, status, held, scope)"
            " VALUES (%s, 'seal it', %s, 'awaiting-confirm', %s, %s)",
            (l2, ME, json.dumps({"tool": "seal-record", "args": {"key": "k"},
                                 "class": "consequential", "level": "L2"}), ev.scope()))
    with pytest.raises(proof.NotConfirmed):
        dispatch.confirm_ask(pg, l2, approve=True, person=m.identity.did)
    assert glass.ask_view(pg, l2)["status"] == "awaiting-confirm"
    assert proof.attempts(pg, held) == [] and proof.attempts(pg, l2) == []         # no proof was even judged
