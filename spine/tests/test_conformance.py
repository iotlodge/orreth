# PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch canon 0008, the conformance suite's first fixture · 2026-09-21
# Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P6 sp4, placement policy v0 · 2026-09-21
# Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P6 cure sp1 (kernel): watch · stop_demand · absent_words · 2026-09-21
# Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P6 cure sp2 (glass): address · offer · citation_name · 2026-09-21
# Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P6 cure sp3 (the re-walk's wounds): restart_demand · duty_text · refused_words · echo_reply · 2026-09-21
# Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp2, the ground and the rails: rail_names · outbox_row · inbox_key · 2026-09-22
# Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P6.5 sp1, the services ladder: ladder_step · manifest_pin · 2026-09-22
# Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp3, the ask road: ask_fact · refused_fact · ask_kind · otpauth · hold_words · 2026-09-22
# Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P6.5 sp2, MCP through one door: mcp_request · mcp_tool_manifest · mcp_server_manifest · mcp_transport · mcp_words · 2026-09-23
# Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp4, the loops: beat_lock · loop_words · plan_words · observed_words · watch_note · cannot_act · improvement_note · crew_hash · turned_fact · 2026-09-23
# Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P6.5 sp3, the Stable: route_for · usd · budget_duration · resolve · drift · eol_due · recommend · deal · deal_refuses · drained_words · act_words · server_name · 2026-09-24
# Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp5, memory and the export: search_terms · memory_fact · purge_fact · digest_text · digest_fact · signed_bundle · did_of · 2026-09-24
# Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp6, the bodies' seam: backoff · park_rule · parked_words · parked_fact · harness_verdict · harness_command · 2026-09-24
# Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp7, cells: topic_name · peers_from · address_home · epoch_check · world_fact · seam_sign · seam_verify · the words · sealed_words · ceiling · 2026-09-25
# Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp8, the profile's arms (W58) · 2026-09-26
# Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp8 row 3, the seat's arms: seat_mint · seat_verify · seat_grants · door_needs · origin_ok · bearer · seat_words · seat_did_of_key · 2026-09-26
# Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp8 row 3c, the rail's arms: lever_manifest · lever_remedies · lever_words · read_lever · dossier_words · remedy_words · outcome_words · ago_words · 2026-09-27
# Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp8 row 3 (b), the desk's arms: desk_transition · desk_challenge · desk_collect · desk_join_id · desk_prove · desk_collect_ok · desk_fuel · desk_lease · desk_words · desk_name · 2026-09-26
# Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch row 4, PANEL sp3, the doors' arms: door_name · door_fold · door_slowest · 2026-09-28
# Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch row 4, re-base sp1: schema_version · schema_tables (the migrator's contract) · 2026-09-28
# Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch row 4, the honest glass: watch_metrics · 2026-09-29
"""The conformance suite (canon 0008): language-neutral fixtures the
Python reference must pass today and `orrethd` must pass in Phase 7 — the
same files, unchanged. A fixture the reference fails is a wound."""
import json
import os
from contextlib import contextmanager
from pathlib import Path

import pytest

from orreth_spine import (body as _body, cells, desk, dispatch, doors, envelope as ev, export, ground, harness, intent, levers,
                          markers, mcp, mitl, monitor, placement, presence, profile, projector, proof, rails, resident, scheduler,
                          seat, services, stable, store, digest, tools)
from orreth_spine.identity import Identity

ROOT = Path(__file__).resolve().parents[1] / "conformance"
FIXTURES = sorted(ROOT.glob("*-v*.json"))


def _cases():
    for f in FIXTURES:
        doc = json.loads(f.read_text("ascii"))
        for c in doc["cases"]:
            yield pytest.param(doc["contract"], c, id=f"{f.stem}::{c['name']}")


@contextmanager
def _dials(**env):
    """Set the rails' dials for one case (None unsets), restoring them after —
    the session's own SPINE_QUEUE_NS / SPINE_SCOPE (conftest) stay untouched."""
    old = {k: os.environ.get(k) for k in env}
    for k, v in env.items():
        if v is None:
            os.environ.pop(k, None)
        else:
            os.environ[k] = v
    try:
        yield
    finally:
        for k, v in old.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


def test_the_suite_has_fixtures():
    assert FIXTURES, "spine/conformance holds no fixtures — the law says every wire change adds one"


@pytest.mark.parametrize("contract,case", list(_cases()))
def test_fixture(contract, case):
    kind, inp, exp = case["kind"], case["input"], case["expect"]
    if kind == "canonical":
        got = ev.canonical(inp["obj"])
        assert got.decode("ascii") == exp["bytes"]
        assert ev.content_hash(inp["obj"]) == exp["hash"]
    elif kind == "encode":
        assert ev.encode(inp["env"]).decode("ascii") == exp["bytes"]
        assert ev.decode(ev.encode(inp["env"])) == inp["env"]
    elif kind == "encode_refuses":
        with pytest.raises(ValueError) as e:
            ev.encode(inp["env"])
        for name in exp["names"]:
            assert name in str(e.value), f"refusal must name {name!r}: {e.value}"
    elif kind == "decode_preserves":
        assert ev.decode(inp["bytes"].encode("ascii")) == exp["obj"]
    # ---- orreth.profile/1 (P7 sp8, W58): the human's own words about themselves ----
    elif kind == "profile_words":                # what a sentence says about the person, or nothing
        assert profile.read_words(inp["text"]) == exp
    elif kind == "profile_label":                # the provenance label a read wears
        assert profile.label_of(inp["asserted_by"]) == exp["label"]
    elif kind == "profile_slice":                # slot 1 of the pack, in one paragraph
        assert profile.slice_words(inp["claims"]) == exp["words"]
    elif kind == "place_default":                # the weather tool's default, or null
        assert profile.place_default(inp["claims"]) == exp["place"]
    # ---- orreth.proof/1 (P6 sp1): the code, the ladder, the level a class demands ----
    elif kind == "totp":
        assert proof.totp(inp["secret"], inp["time"]) == exp["code"]
    elif kind == "totp_verify":
        assert [proof.verify(inp["secret"], inp["code"], t) for t in inp["at"]] == exp["ok"]
    elif kind == "ladder":
        got = sorted(inp["order"], key=proof.rank)
        assert got == exp["sorted"]
        assert [proof.LEVEL_OF_CLASS[c] for c in got] == exp["levels"]
    elif kind == "class_level":
        assert proof.level_for(inp["class"], master=bool(inp.get("master"))) == exp["level"]
    elif kind == "stop_demand":                  # W5: what the stop of an intention demands
        assert intent.stop_demand(inp["intention_kind"]) == exp
    # ---- orreth.intent/1 (walk #8): the restart's demand, the duty's framing, the refusal, echo's reply ----
    elif kind == "restart_demand":               # W20: the reverse of the stop climbs the same ladder
        assert intent.restart_demand(inp["intention_kind"]) == exp
    elif kind == "duty_text":                    # W21: a duty is framed as a duty
        assert scheduler.cadence_words(inp["every_s"]) == exp["cadence"]
        assert scheduler.duty_text(inp["text"], inp["every_s"], inp["since"], inp["notes"]) == exp["text"]
    elif kind == "refused_words":                # W21: a reply that OPENS as a refusal
        assert harness.refused_words(inp["reply"]) is exp["refused"]
    elif kind == "echo_reply":                   # W24: the echoed words alone; one plain line for a question
        assert resident.echo_reply(inp["name"], inp["text"]) == exp["reply"]
    # ---- orreth.doors/1 (row 4, panel sp3): a door's name and the fold of its latency ----
    elif kind == "joined_fact":                  # re-base sp1: orreth.body.joined.v1 — a body joined (a life), the roster's fact
        e = _body.joined_fact(inp["name"], inp["did"], inp["kind"], inp["life"], inp["nature"], scope=inp["scope"])
        e["message_id"], e["occurred_at"] = inp["message_id"], inp["occurred_at"]
        assert (e["payload"], e["type"], e["authority_chain"], e["correlation_id"]) == \
            (exp["payload"], exp["type"], exp["chain"], exp["correlation_id"])
        assert ev.encode(e).decode("ascii") == exp["bytes"]
    # ---- orreth.inbox/1 (re-base sp1): POISON-PARKING — the parked and the advanced facts, the words ----
    elif kind in ("inbox_parked_fact", "inbox_advanced_fact"):
        if kind == "inbox_parked_fact":
            e = projector.parked_fact(inp["parked_id"], inp["consumer"], inp["topic"], inp["partition"], inp["offset"],
                                      inp["body"].encode(), inp["reason"], scope=inp["scope"])
        else:
            e = projector.advanced_fact(inp["parked_id"], inp["consumer"], inp["topic"], inp["partition"], inp["offset"],
                                        inp["by"], scope=inp["scope"])
        e["message_id"], e["occurred_at"] = inp["message_id"], inp["occurred_at"]
        assert (e["payload"], e["type"], e["authority_chain"], e["correlation_id"]) == \
            (exp["payload"], exp["type"], exp["chain"], exp["correlation_id"])
        assert ev.encode(e).decode("ascii") == exp["bytes"]
    elif kind == "inbox_parked_words":
        assert projector.parked_words(inp["consumer"], inp["topic"], inp["partition"], inp["offset"], inp["reason"]) == exp["words"]
    elif kind == "body_hash":
        assert projector.body_hash(inp["body"].encode()) == exp["hash"]
    # ---- orreth.schema/1 (re-base sp1, lock 2): THE MIGRATOR's contract — the version and the tables ----
    elif kind == "schema_version":
        assert ground.SCHEMA_VERSION == exp["version"]
    elif kind == "schema_tables":
        assert sorted(ground.TABLES) == exp["tables"] and len(ground.TABLES) == exp["count"]
    elif kind == "door_name":
        assert doors.door_name(inp["method"], inp["path"]) == exp["door"]
    elif kind == "door_fold":
        assert doors.fold(inp["samples_ms"]) == exp
    elif kind == "door_slowest":
        assert [r["door"] for r in doors.slowest_first(inp["reads"])] == exp["order"]
        assert doors.slowest_p95(inp["reads"]) == exp["p95"]
    # ---- orreth.watch/1 (W14): the sense of a watch — red WHEN the condition holds ----
    elif kind == "watch_judge":
        red = monitor.judge_one(inp["op"], inp["value"], inp["threshold"])
        assert (red, "red" if red else "green") == (exp["red"], exp["state"])
    elif kind == "watch_reads":
        assert monitor.reads(inp) == exp["reads"]
    elif kind == "watch_metrics":                # the honest glass: one vocabulary on both kernels
        assert list(monitor.METRICS) == exp["metrics"]
    # ---- orreth.ask/1 (W19): the door's refusal for a body that is not here ----
    elif kind == "address":                      # W7: a name at the head selects that body
        assert dispatch.address(inp["text"], inp["names"]) == exp["name"]
    elif kind == "offer":                        # walk #7: the monitor's offer, read from its words
        assert monitor.offer_in(inp["reply"]) == exp["offer"]
    # ---- orreth.impact/1 (re-base sp1): the four doors cross — the ontology's passages, the metric in words,
    # the ground's lines, the impact ask's text; orreth.markers/1: the kind-name law ----
    elif kind == "passages":
        assert mitl.passages(inp["text"], inp["limit"]) == exp["passages"]
    elif kind == "metric_in":
        assert mitl._metric_in(inp["words"]) == exp["metric"]
    elif kind == "describe":
        assert mitl.describe(inp["touches"]) == exp["lines"]
    elif kind == "impact_text":
        assert mitl.ask_text(inp["touches"], inp["verdict"], inp["ground"]) == exp["text"]
    elif kind == "declare_kind":
        try:
            k, g = markers.kind_name(inp["kind"], inp["group"])
            assert exp == {"kind": k, "group": g}
        except ValueError as e:
            assert exp == {"error": str(e)}
    elif kind == "citation_name":                # W15: a citation in a human's name
        assert mitl.citation_name(inp["path"], inp["heading"], inp["rule"]) == exp["name"]
    elif kind == "absent_words":
        assert dispatch.refusal_words(inp["name"], inp["reason"]) == exp["reply"]
    # ---- orreth.minds/1 (P6.5 sp3): the Stable's laws — routes, dollars, the routing decision, drift, EOL, the swap ----
    elif kind == "route_for":
        assert stable.route_for(inp["provider"], inp["model"], inp.get("base")) == exp
    elif kind == "usd":
        assert stable.usd(inp["price"], inp["tokens_in"], inp["tokens_out"]) == exp["usd"]
    elif kind == "budget_duration":
        assert stable.budget_duration(inp["days"]) == exp["duration"]
    elif kind == "resolve":
        assert stable.resolve(inp["stalls"], inp["assignments"], subject=inp.get("subject"), klass=inp.get("klass"),
                              pin=inp.get("pin"), model=inp.get("model")) == exp
    elif kind == "drift":
        assert stable.drift(inp["pinned"], inp["seen"]) == exp["moved"]
    elif kind == "eol_due":
        from datetime import datetime
        assert stable.eol_due(inp["expires"], datetime.fromisoformat(inp["now"]), inp["horizon_days"]) == exp
    elif kind == "recommend":
        assert stable.recommend(inp["stalls"], inp["retiring"]) == exp
    elif kind == "deal":
        assert stable.deal(inp["model"], inp["provider"], base=inp.get("base"), klass=inp.get("klass", "standard"),
                           key=inp["key"] if "key" in inp else "auto") == exp
    elif kind == "deal_refuses":
        with pytest.raises(stable.StableRefused) as e:
            stable.deal(inp["model"], inp["provider"], klass=inp.get("klass", "standard"), key=inp["key"] if "key" in inp else "auto")
        assert str(e.value) == exp["words"]
    elif kind == "drained_words":
        assert stable.drained_words(inp["name"], inp["gauge"]) == exp["words"]
    elif kind == "act_words":
        assert stable.act_words(inp["tool"], inp["args"]) == exp["words"]
    elif kind == "server_name":                  # W28: a server names itself
        assert mcp.server_name(inp["info"], inp["locator"]) == exp["name"]
    # ---- orreth.bodies/1 (P7 sp6): the kernel governs the bodies it spawns; the harness rides the rail ----
    elif kind == "backoff":                     # the wait before the n-th restart
        assert _body.backoff_s(inp["deaths"]) == exp["wait_s"]
    elif kind == "park_rule":                   # deaths inside the window; at the strikes, PARKED
        assert _body.park_rule(inp["exits"], inp["now"], inp["window_s"], inp["strikes"]) == exp
    elif kind == "parked_words":                # the plain words of a parked body, with the human's lever
        assert _body.parked_words(inp["name"], inp["deaths"], inp["window_s"], inp["last_words"]) == exp["words"]
    elif kind == "parked_fact":                 # orreth.body.parked.v1 — the kernel's fact, its evidence cut
        e = _body.parked_fact(inp["name"], inp["did"], inp["deaths"], inp["window_s"], inp["last_words"], scope=inp["scope"])
        e["message_id"], e["occurred_at"] = inp["message_id"], inp["occurred_at"]
        assert (e["payload"], e["type"], e["authority_chain"]) == (exp["payload"], exp["type"], exp["chain"])
        assert ev.encode(e).decode("ascii") == exp["bytes"]
    elif kind == "harness_verdict":             # a case passes when every expected word is in the reply, case folded
        assert harness.verdict(inp["cases"], inp["replies"]) == exp
    elif kind == "harness_command":             # the kernel's ask of a body: run these cases as this run id
        e = harness.command_for(inp["run_id"], inp["target"], inp["cases"], arm=inp["arm"],
                               parent_marker=inp["parent_marker"], scope=inp["scope"])
        e["message_id"], e["occurred_at"] = inp["message_id"], inp["occurred_at"]
        assert (e["payload"], e["type"], e["correlation_id"], e["authority_chain"]) == \
            (exp["payload"], exp["type"], exp["correlation_id"], exp["chain"])
        assert e["payload"]["target"] == exp["queue_target"]        # routed to that body's own bench
        assert ev.encode(e).decode("ascii") == exp["bytes"]
    # ---- orreth.compliance/1 (P6 sp2): the hash chain, the chain's status, the verifier ----
    elif kind == "hash_chain":
        got = export.hash_chain(inp["rows"])
        assert got == exp["hashes"]
        assert (got[-1] if got else None) == exp["root_hash"]
    elif kind == "chain_status":
        assert [export.chain_status(r) for r in inp["rows"]] == exp["status"]
    elif kind == "verify":
        assert export.verify(inp["bundle"]) is exp["bundle"]
        assert export.verify(inp["truncated"]) is exp["truncated"]
        assert export.verify(inp["resealed"]) is exp["resealed"]
        assert inp["resealed"]["summary"]["chain_broken"] == exp["resealed_chain_broken"]
    # ---- orreth.impact/1 (P6 sp3): the verdict ladder — rules, never a brain ----
    elif kind == "verdict":
        assert mitl.verdict(inp["touches"]) == exp["verdict"]
    # ---- orreth.placement/1 (P6 sp4): the profile's defaults, the honor rule and its reasons ----
    elif kind == "profile":
        got = placement.profile(inp["template"])
        assert got == exp["profile"]
        assert ev.canonical(got).decode("ascii") == exp["bytes"]
    elif kind == "honor":
        ok, reasons = placement.honor(inp["profile"], inp["ground"])
        assert (ok, reasons) == (exp["honored"], exp["reasons"])
        assert placement.why_here(inp["profile"], inp["ground"]) == exp["why"]
    # ---- orreth.rails/1 (P7 sp2): the rails' NAMES and SHAPES the Rust ground and rails stand on ----
    elif kind == "rail_names":                   # queues wear the namespace, facts wear the world
        with _dials(SPINE_QUEUE_NS=inp["ns"], SPINE_SCOPE=inp["scope"]):
            got = {"serve_queue": resident.serve_queue(inp["name"]), "serve_key": resident.serve_key(inp["name"]),
                   "scope": ev.scope(), "command_exchange": rails.COMMAND_EXCHANGE,
                   "heartbeat_queue": rails.HEARTBEAT_QUEUE, "heartbeat_key": rails.HEARTBEAT_KEY,
                   "heartbeat_topic": rails.HEARTBEAT_TOPIC}
        assert got == exp
    elif kind == "outbox_row":                   # the row a fact becomes; sinks.KafkaSink's topic + key laws
        env = inp["env"]
        assert ev.encode(env).decode("ascii") == exp["body"]
        assert env["message_id"] == exp["message_id"]
        assert env["type"] == exp["topic"]      # topic = the TYPE (schema families, never per-identity)
        assert str((env.get("aggregate") or {}).get("id") or env["message_id"]) == exp["key"]
    elif kind == "inbox_key":                    # the head of inbox.apply_event: once, or sequenced per aggregate
        env = inp["env"]
        agg = env.get("aggregate") or {}
        aid = str(agg.get("id") or "")
        seq = int(agg.get("sequence") or 0)
        road = "once" if (not aid or seq <= 0) else "sequenced"
        assert {"road": road, "message_id": env["message_id"],
                "aggregate_id": aid if road == "sequenced" else None,
                "sequence": seq if road == "sequenced" else None} == exp
    # ---- orreth.services/1 (P6.5 sp1): the one ladder's legality; the manifest pin ----
    elif kind == "ladder_step":                  # from a state (null = unregistered), may a verb step, and to where?
        assert services.ladder_step(inp["state"], inp["verb"]) == exp
    elif kind == "manifest_pin":                 # canonical bytes → sha256, the pin every kind wears
        assert ev.canonical(inp["manifest"]).decode("ascii") == exp["bytes"]
        assert services.pin(inp["manifest"]) == exp["hash"]
    # ---- orreth.tools/1 (P7 sp8 row 2): the declarations as data — both kernels read tools.v0.json by name ----
    elif kind == "tool_manifest":               # the declaration → the registry's pin, byte-identical on both kernels
        t = tools.TOOLS[inp["name"]]
        m = tools.tool_manifest(inp["name"], t)
        assert ev.canonical(m).decode("ascii") == exp["bytes"]
        assert services.pin(m) == exp["hash"]
        assert {"consequence": tools.consequence_of(t), "ground": bool(t.get("ground")),
                "master": bool(t.get("master"))} == {k: exp[k] for k in ("consequence", "ground", "master")}
    elif kind == "tool_consequence":            # the class a CALL wears: held_by's rule by the arguments
        assert tools.consequence_of(tools.TOOLS[inp["name"]], inp["args"]) == exp["consequence"]
    # ---- orreth.askroad/1 (P7 sp3): the ask's fact, the door's refusal, the kind of an ask, the proof's words ----
    elif kind == "ask_fact":                    # submit_ask's law: the pointer-only payload, the human's chain, the ask at seq 1
        payload = {"ref": inp["ask_id"], "hash": ev.content_hash(inp["text"])}
        if inp["target"]:
            payload["target"] = inp["target"]
        if inp["session"]:
            payload["session"] = inp["session"]
        if inp["window"]:
            payload["window"] = {"from": str(inp["window"].get("from") or ""), "to": str(inp["window"].get("to") or "")}
        e = ev.make_envelope(kind="event", type=resident.ASK_RECEIVED, universe_id=inp["scope"], scope_path=inp["scope"],
                             payload=payload, correlation_id=inp["fanout"] or inp["ask_id"], authority_chain=[inp["person"]],
                             aggregate={"type": "ask", "id": inp["ask_id"], "sequence": 1}, marker=inp["marker"])
        e["message_id"], e["occurred_at"] = inp["message_id"], inp["occurred_at"]
        assert ev.encode(e).decode("ascii") == exp["bytes"]
        assert (payload, e["type"], e["aggregate"]["id"], e["correlation_id"]) == (exp["payload"], exp["topic"], exp["key"], exp["correlation_id"])
    elif kind == "refused_fact":                # W19: the row lands refused, the kernel as server, its own fact
        payload = {"ref": inp["ask_id"], "hash": ev.content_hash(inp["text"]), "target": inp["target"], "reason": inp["reason"],
                   **({"session": inp["session"]} if inp["session"] else {})}
        e = ev.make_envelope(kind="event", type=dispatch.ASK_REFUSED, universe_id=inp["scope"], scope_path=inp["scope"],
                             payload=payload, correlation_id=inp["fanout"] or inp["ask_id"],
                             authority_chain=[inp["person"], proof.KERNEL],
                             aggregate={"type": "ask", "id": inp["ask_id"], "sequence": 1}, marker=inp["marker"])
        e["message_id"], e["occurred_at"] = inp["message_id"], inp["occurred_at"]
        assert ev.encode(e).decode("ascii") == exp["bytes"]
        assert dispatch.refusal_words(inp["target"], inp["reason"]) == exp["reply"]
        assert (exp["status"], exp["served_by"], e["type"]) == ("refused", proof.KERNEL, exp["topic"])
    elif kind == "ask_kind":                    # P23: the words propose the kind; a typed prefix flips it
        assert intent.read_words(inp["text"]) == exp
    elif kind == "otpauth":                     # the URI an authenticator reads
        assert proof.otpauth_uri(inp["person"], inp["secret"]) == exp["uri"]
    elif kind == "hold_words":                  # the words the chat says when an act is held (P18 · W23)
        assert proof.question_for(inp["level"], inp["what"], needs_code=inp["needs_code"]) == exp["text"]
    # ---- orreth.mcp/1 (P6.5 sp2): the three requests' bytes, the pins an MCP server and its tools wear, the words ----
    elif kind == "mcp_request":                  # JSON-RPC 2.0 with FIXED ids: the bytes on the wire are canonical
        req = (mcp.initialize_request() if inp["method"] == "initialize" else mcp.list_request()
               if inp["method"] == "tools/list" else mcp.call_request(inp["tool"], inp["arguments"]))
        assert (req["id"], mcp.request_bytes(req).decode("ascii")) == (exp["id"], exp["bytes"])
    elif kind == "mcp_tool_manifest":            # an MCP listing entry → the service manifest a tool wears, pinned
        m = mcp.tool_manifest(inp["server"], inp["tool"])
        assert m == exp["manifest"] and (m["name"], m["consequence"]) == (exp["shelf_name"], exp["consequence"])
        assert ev.canonical(m).decode("ascii") == exp["bytes"] and services.pin(m) == exp["hash"]
    elif kind == "mcp_server_manifest":          # the server's manifest: transport · locator BY NAME · the list, sorted
        m = mcp.server_manifest(inp["locator"], inp["tools"])
        assert m == exp["manifest"] and m["transport"] == exp["transport"] and services.pin(m) == exp["hash"]
    elif kind == "mcp_transport":
        assert mcp.transport_of(inp["locator"]) == exp["transport"]
    elif kind == "mcp_words":                    # the transition words; the dials; the fixed ids
        assert (mcp.GONE, mcp.STRIKES_DIAL, mcp.STRIKES_DEFAULT, mcp.PROTOCOL) == \
            (exp["gone"], exp["strikes_dial"], exp["strikes_default"], exp["protocol"])
        assert {"initialize": mcp.INITIALIZE_ID, "tools/list": mcp.LIST_ID, "tools/call": mcp.CALL_ID} == exp["ids"]
    # ---- orreth.loops/1 (P7 sp4): the beat lock, the loop's words, the watch's turned fact ----
    elif kind == "beat_lock":                    # two kernels on one ground: one beat at a time, per world
        assert (ground.BEAT_LOCK, ground.BEATS, ground.HELD) == (exp["base"], exp["beats"], exp["held"])
        assert {k: ground.beat_key(k) for k in ground.BEATS} == exp["keys"]
    elif kind == "loop_words":
        assert (intent.CADENCE_DUE, intent.CANNOT_ACT, monitor.WATCH_TURNED, harness.HARNESS_FAILED) == \
            (exp["cadence_due"], exp["cannot_act"], exp["watch_turned"], exp["harness_failed"])
        assert (intent.INTENTION_DECLARED, intent.INTENTION_STOPPED, intent.INTENTION_RESTARTED, intent.WATCH_RED) == \
            (exp["intention_declared"], exp["intention_stopped"], exp["intention_restarted"], exp["watch_red"])
        assert (presence.TTL_S, intent.RESILIENCY, resident.W26_WORDS, resident.W26_STEP) == \
            (exp["lease_ttl_s"], exp["resiliency"], exp["w26_words"], exp["w26_step"])
    elif kind == "plan_words":                   # what the kernel asks the planner
        assert intent.plan_words(inp["serves"], inp["words"], inp["observed"]) == exp["text"]
    elif kind == "observed_words":
        assert intent.observed_words(inp["kind"], inp["ref"], inp["note"]) == exp["text"]
    elif kind == "watch_note":                   # the name in Python's quotes, the float threshold
        assert intent.watch_note(inp["name"], inp["metric"], inp["op"], inp["threshold"], inp["value"]) == exp["text"]
    elif kind == "cannot_act":                   # W8: only the opening counts
        assert intent.cannot_act(inp["reply"]) is exp["cannot"]
    elif kind == "hold_expiry":                  # W35's boundary: doing nothing cancels, after the window
        assert (proof.HOLD_TTL_MIN, proof.expired_words(), proof.EXPIRED_REPLY) == (exp["minutes"], exp["reason"], exp["reply"])
    elif kind == "duplicate_words":              # W37: a duplicate purpose is named at the door
        assert intent.duplicate_words(inp["kind"], inp["words"]) == exp["text"]
    elif kind == "improvement_note":
        assert intent.improvement_note(inp["who"], inp["reply"]) == exp["note"]
    # ---- orreth.levers/1 (P7 sp8 row 3c): THE REMEDIATION RAIL's pure laws ----
    elif kind == "lever_manifest":               # the declaration as data, both kernels read levers.v0.json by name
        d = levers.declared(levers.catalogue(), inp["name"])
        m = levers.lever_manifest(d)
        assert m == exp["manifest"]
        assert ev.canonical(m).decode("ascii") == exp["bytes"] and ev.content_hash(m) == exp["hash"]
    elif kind == "lever_remedies":               # served by the door, for the metric, never grave
        assert [d["name"] for d in levers.remedies(levers.catalogue(), inp["metric"], inp["door"])] == exp["names"]
    elif kind == "lever_words":                  # the catalogue as the planner reads it
        assert levers.lever_words(inp["levers"]) == exp["text"]
    elif kind == "read_lever":                   # the planner's answer read IN the catalogue
        assert levers.read_lever(inp["reply"]) == exp["read"]
    elif kind == "dossier_words":                # the forensic turn in plain words
        assert levers.dossier_words(inp["dossier"]) == exp["text"]
    elif kind == "remedy_words":                 # what the kernel asks the planner under a red watch
        assert levers.remedy_words(inp["serves"], inp["words"], inp["dossier_text"], inp["levers_text"]) == exp["text"]
    elif kind == "outcome_words":                # the attributed outcome's words
        o = inp["outcome"]
        got = (levers.cured_note(inp["watch"], inp["lever"], inp["args"], inp["because"]) if o == "cured"
               else levers.self_healed_note(inp["watch"]) if o == "self-healed"
               else levers.still_red_note(inp["watch"], inp["lever"], inp["args"], inp["settles_s"]) if o == "still-red"
               else levers.cancelled_note(inp["watch"], inp["lever"], inp["args"], inp["why"]) if o == "cancelled"
               else levers.no_lever_note(inp["watch"], inp["because"]) if o == "no-lever"
               else levers.unserved_note(inp["watch"], inp["lever"]) if o == "unserved"
               else levers.pulled_words(inp["lever"], inp["args"], inp["because"], inp["result"]) if o == "pulled"
               else levers.handed_words(inp["watch"], inp["tried"], inp["dossier_text"]) if o == "handed"
               else levers.notice_words(inp["watch"], inp["because"], inp["dossier_text"]))
        assert got == exp["text"]
    elif kind == "ago_words":
        assert levers.ago_words(inp["s"]) == exp["text"]
    elif kind == "pulled_fact":                  # panel sp2: orreth.lever.pulled.v1 — the kernel's pull, a fact on the feed
        e = levers.pulled_fact(inp["ask_id"], inp["lever"], inp["args"], inp["because"], inp["held"], inp["intention_id"],
                               inp["person"], scope=inp["scope"])
        e["message_id"], e["occurred_at"] = inp["message_id"], inp["occurred_at"]
        assert (e["payload"], e["type"], e["authority_chain"], e["correlation_id"]) == \
            (exp["payload"], exp["type"], exp["chain"], exp["correlation_id"])
        assert ev.encode(e).decode("ascii") == exp["bytes"]
    elif kind == "lease_fact":                   # panel sp2: orreth.lease.lapsed/seated.v1 — a lease crossing the line
        e = presence.lease_fact(inp["type"], inp["name"], inp["did"], inp["kind"], inp["until"], scope=inp["scope"])
        e["message_id"], e["occurred_at"] = inp["message_id"], inp["occurred_at"]
        assert (e["payload"], e["type"], e["authority_chain"], e["correlation_id"]) == \
            (exp["payload"], exp["type"], exp["chain"], exp["correlation_id"])
        assert ev.encode(e).decode("ascii") == exp["bytes"]
    elif kind == "crew_hash":                    # the crew's shape, sorted, as canonical bytes
        assert intent.crew_shape_hash([(n, c) for n, c in inp["shape"]]) == exp["hash"]
    # ---- orreth.memory/1 (P7 sp5): the Record's laws — recall's grammar, the landed and purged facts, the digest ----
    elif kind == "search_terms":
        assert store.search_terms(inp["query"]) == exp["terms"]
        assert store.fallback_words(inp["query"]) == exp["fallback"]
    elif kind == "memory_fact":                  # orreth.memory.landed.v1 for a fixed id and clock
        with _dials(SPINE_SCOPE=inp["scope"]):
            payload = store.landed_payload(inp["namespace"], inp["key"], ev.content_hash(inp["body"]), inp.get("supersedes"))
            e = ev.make_envelope(kind="event", type=store.MEMORY_EVENT, universe_id=ev.scope(), scope_path=ev.scope(),
                                 payload=payload, authority_chain=[inp["by"]])
        e["message_id"], e["occurred_at"] = inp["message_id"], inp["occurred_at"]
        assert payload == exp["payload"] and ev.encode(e).decode("ascii") == exp["bytes"]
    elif kind == "purge_fact":                   # the tombstone: hashes, never words
        with _dials(SPINE_SCOPE=inp["scope"]):
            payload = store.purge_payload(inp["namespace"], inp["key"], inp["hashes"])
            e = ev.make_envelope(kind="event", type=store.PURGE_EVENT, universe_id=ev.scope(), scope_path=ev.scope(),
                                 payload=payload, authority_chain=[inp["by"]])
        e["message_id"], e["occurred_at"] = inp["message_id"], inp["occurred_at"]
        assert payload == exp["payload"] and ev.encode(e).decode("ascii") == exp["bytes"]
    elif kind == "digest_text":                  # the short version's text from its parts
        from datetime import datetime
        asks = [(a[0], a[1], a[2], a[3], datetime.fromisoformat(a[4]), datetime.fromisoformat(a[5]) if a[5] else None, a[6])
                for a in inp["asks"]]
        body, sources = digest.compose_lines(inp["session_id"], inp.get("title"), datetime.fromisoformat(inp["opened"]),
                                             asks, [tuple(m) for m in inp["memories"]])
        assert body == exp["body"] and sources == exp["sources"]
    elif kind == "session_fact":                 # orreth.session.opened.v1 (W51): the roll is a fact, the person's chain
        with _dials(SPINE_SCOPE=inp["scope"]):
            from orreth_spine import glass as _glass
            payload = _glass.session_payload(inp["session_id"], inp["person"], inp.get("title"), inp.get("archived"), inp["state"])
            e = ev.make_envelope(kind="event", type=_glass.SESSION_OPENED, universe_id=ev.scope(), scope_path=ev.scope(),
                                 payload=payload, correlation_id=inp["session_id"], authority_chain=[inp["person"]])
        e["message_id"], e["occurred_at"] = inp["message_id"], inp["occurred_at"]
        assert payload == exp["payload"] and ev.encode(e).decode("ascii") == exp["bytes"]
    elif kind == "digest_fact":                  # orreth.digest.landed.v1: the session as correlation
        with _dials(SPINE_SCOPE=inp["scope"]):
            payload = {"ref": inp["digest_id"], "hash": ev.content_hash(inp["body"]), "session": inp["session"],
                       "sources": inp["sources"]}
            e = ev.make_envelope(kind="event", type=digest.DIGEST_EVENT, universe_id=ev.scope(), scope_path=ev.scope(),
                                 payload=payload, correlation_id=inp["session"], authority_chain=[inp["by"]])
        e["message_id"], e["occurred_at"] = inp["message_id"], inp["occurred_at"]
        assert payload == exp["payload"] and ev.encode(e).decode("ascii") == exp["bytes"]
    # ---- orreth.compliance/1 (P7 sp5): the bundle SIGNED by the kernel's own self ----
    elif kind == "signed_bundle":
        signer = Identity("kernel", bytes.fromhex(inp["seed_hex"]), kind="kernel")
        b = export.seal(inp["rows"], scope=inp["scope"], world=inp["world"], generated_at=inp["generated_at"], signer=signer)
        assert b == exp["bundle"] and export.verify(b) is True
    elif kind == "verify_signed":
        assert export.verify(inp["bundle"]) is exp["ok"]
    elif kind == "did_of":
        assert Identity("x", bytes.fromhex(inp["seed_hex"]), kind=inp["kind"]).did == exp["did"]
        assert Identity("x", bytes.fromhex(inp["seed_hex"]), kind=inp["kind"]).verify_key_hex == exp["public_key_hex"]
    # ---- orreth.cells/1 (P7 sp7): cells = worlds — the namespace, the home, the seam, the words, the ceiling ----
    elif kind == "topic_name":                   # the topic wears the cell's namespace as a bench does
        assert cells.topic_name(inp["base"], inp["ns"]) == exp["topic"]
    elif kind == "peers_from":                   # SPINE_PEERS → the peers this cell names; a malformed pair dropped by name
        assert cells.peers_from(inp["dial"]) == exp["peers"]
    elif kind == "address_home":                 # "librarian@two, …" · "two/librarian, …" → the home cell and the name
        assert cells.address_home(inp["text"]) == exp["home"]
        assert cells.strip_home(inp["text"]) == exp["served"]
    elif kind == "epoch_check":                  # current · stale · future
        assert cells.epoch_check(inp["mine"], inp["theirs"]) == exp["verdict"]
    elif kind == "world_fact":                   # orreth.world.homed.v1 — the kernel's chain, the world as correlation
        e = cells.world_fact(inp["scope"], inp["cell"], inp["epoch"], inp["kernel"], inp["door"], inp["reason"])
        e["message_id"], e["occurred_at"] = inp["message_id"], inp["occurred_at"]
        assert (e["payload"], e["type"], e["authority_chain"], e["correlation_id"]) == \
            (exp["payload"], exp["type"], exp["chain"], exp["correlation_id"])
        assert ev.encode(e).decode("ascii") == exp["bytes"]
    elif kind == "seam_sign":                    # Ed25519 over the message's canonical bytes; the signer's DID and key beside it
        signer = Identity("kernel", bytes.fromhex(inp["seed_hex"]), kind="kernel")
        assert cells.seam_sign(inp["message"], signer) == exp["signed"]
        assert ev.canonical(inp["message"]).decode("ascii") == exp["bytes"]
    elif kind == "seam_verify":                  # the seam's gate: one verdict in words
        assert cells.seam_verify(inp["signed"], pinned_did=inp["pinned_did"], now=inp["now"],
                                 seen_nonces=inp["seen_nonces"], epoch=inp["epoch"]) == exp["verdict"]
    elif kind == "park_words":
        assert cells.park_words(inp["name"], inp["cell"], inp["since"]) == exp["words"]
    elif kind == "resumed_words":
        assert cells.resumed_words(inp["name"], inp["cell"]) == exp["words"]
    elif kind == "lag_words":
        assert cells.lag_words(inp["cell"], inp["world"], inp["behind_s"], inp["unreachable_since"]) == exp["words"]
    elif kind == "sealed_words":
        assert cells.sealed_words(inp["role"], inp["own_db"], inp["reachable"]) == (exp["ok"], exp["words"])
    elif kind == "rehome_words":
        assert cells.rehome_words(inp["scope"], inp["from_cell"], inp["to_cell"], inp["epoch"]) == exp["words"]
    elif kind == "ceiling":                      # the token bucket: refills at rate up to burst; a knock spends one
        allowed, after = cells.ceiling(inp["tokens"], inp["last_at"], inp["now"], inp["rate"], inp["burst"])
        assert allowed == exp["allowed"] and abs(after - exp["tokens_after"]) < 1e-9
    elif kind == "turned_fact":                  # orreth.watch.turned.v1 — the kernel's chain, the watch as correlation
        with _dials(SPINE_SCOPE=inp["scope"]):
            e = ev.make_envelope(
                kind="event", type=monitor.WATCH_TURNED, universe_id=ev.scope(), scope_path=ev.scope(),
                payload={"ref": inp["watch_id"], "hash": ev.content_hash(inp["name"]), "name": inp["name"],
                         "metric": inp["metric"], "op": inp["op"], "threshold": inp["threshold"],
                         "value": inp["value"], "from": inp["from"], "to": inp["to"]},
                correlation_id=inp["watch_id"], authority_chain=["the kernel"])
        e["message_id"], e["occurred_at"] = inp["message_id"], inp["occurred_at"]
        assert ev.encode(e).decode("ascii") == exp["bytes"] and e["payload"] == exp["payload"]
        assert (e["type"], e["correlation_id"]) == (exp["topic"], exp["correlation_id"])
    # ---- orreth.seat/1 (P7 sp8 row 3a): THE HUMAN SEAT — the 0006 token from a seed, its verdicts, the doors' needs ----
    elif kind == "seat_mint":                    # the token's exact bytes from the root's seed; its id and its wire form
        signer = Identity("kernel", bytes.fromhex(inp["seed_hex"]), kind="kernel")
        t = seat.mint(signer, subject=inp["subject"], audience=inp["audience"], grants=inp["grants"],
                      expiry=inp["expiry"], direction=inp["direction"], budget=inp["budget"])
        assert t == exp["token"] and ev.canonical(t).decode("ascii") == exp["bytes"]
        assert seat.seat_id(t) == exp["seat_id"] and seat.wire(t) == exp["wire"] and seat.unwire(exp["wire"]) == t
    elif kind == "seat_verify":                  # ok · malformed · expired · foreign authority · broken chain · bad signature · amplified
        assert seat.verify(inp["token"], root_did=inp["root_did"], root_key_hex=inp["root_key_hex"], now=inp["now"]) == exp["verdict"]
    elif kind == "seat_grants":                  # a person reads and writes; the owner and a master also govern
        assert seat.grants_for(inp["role"], inp["scope"]) == exp["grants"]
    elif kind == "door_needs":                   # open · enroll · retrieve · write · govern
        assert seat.door_needs(inp["method"], inp["path"]) == exp["needs"]
    elif kind == "origin_ok":                    # the browser origin is closed
        assert seat.origin_ok(inp["origin"], inp["host"]) == exp["ok"]
    elif kind == "bearer":                       # authorization: Bearer <wire>
        assert seat.bearer(inp["header"]) == exp["wire"]
    elif kind == "seat_words":
        if inp["what"] == "busy":
            assert seat.BUSY_WORDS == exp["words"] and seat.busy() == exp["face"]
        elif inp["what"] == "not_seated":
            assert seat.NOT_SEATED == exp["face"]
        else:
            assert seat.taken_words(inp["person"], inp["role"], inp["hours"], inp["ceremony"]) == exp["words"]
    elif kind == "person_did":                   # the person grammar: a bare name or the DID, else None
        assert seat.person_did(inp["text"]) == exp["did"]
    elif kind == "seat_did_of_key":
        assert seat.did_of_key(inp["kind"], inp["public_key_hex"]) == exp["did"]
    # ---- orreth.desk/1 (P7 sp8 row 3b): THE MACHINE JOIN DESK — the statuses, the challenge, the proof, the lease, the words ----
    elif kind == "desk_transition":              # a settled word is never rewritten; proved answers only a challenge
        assert desk.transition_legal(inp["from"], inp["to"]) == exp["legal"]
    elif kind == "desk_challenge":               # the bytes the joiner signs: {did, join_nonce}
        assert desk.challenge_payload(inp["did"], inp["nonce"]) == exp["payload"]
        assert desk.canonical_bytes(exp["payload"]) == exp["bytes"]
    elif kind == "desk_collect":                 # the bytes that collect the lease: {did, join, join_nonce}
        assert desk.collect_payload(inp["did"], inp["join"], inp["nonce"]) == exp["payload"]
        assert desk.canonical_bytes(exp["payload"]) == exp["bytes"]
    elif kind == "desk_join_id":
        assert desk.join_id_of(inp["did"], inp["nonce"]) == exp["id"]
    elif kind == "desk_prove":                   # the declared key derives the DID; the signature stands over the desk's own nonce
        assert desk.prove(inp["did"], inp["public_key"], inp["nonce"], inp["sig"]) == exp["ok"]
        if inp.get("seed_hex"):                  # the proof's own bytes, from the seed
            assert desk.proof_of(Identity("body", bytes.fromhex(inp["seed_hex"]), kind="agent"), inp["nonce"]) == inp["sig"]
    elif kind == "desk_collect_ok":
        assert desk.collect_ok(inp["did"], inp["public_key"], inp["join"], inp["nonce"], inp["sig"]) == exp["ok"]
        if inp.get("seed_hex"):
            assert desk.collect_sig(Identity("body", bytes.fromhex(inp["seed_hex"]), kind="agent"), inp["join"], inp["nonce"]) == inp["sig"]
    elif kind == "desk_fuel":                    # dollars per window; 0 days is the lump
        assert desk.fuel_clause(inp["usd"], inp["renew_days"]) == exp["clause"]
    elif kind == "desk_lease":                   # the lease's exact bytes from the root's seed; it verifies at that root
        signer = Identity("kernel", bytes.fromhex(inp["seed_hex"]), kind="kernel")
        t = desk.lease(signer, did=inp["did"], scope=inp["scope"], expiry=inp["expiry"], usd=inp["usd"], renew_days=inp["renew_days"])
        assert t == exp["token"] and ev.canonical(t).decode("ascii") == exp["bytes"]
        assert seat.seat_id(t) == exp["lease_id"] and seat.wire(t) == exp["wire"] and t["grants"] == exp["grants"]
        assert seat.verify(t, root_did=signer.did, root_key_hex=signer.verify_key_hex, now="2026-10-01T00:00:00.000Z") == exp["verdict"]
    elif kind == "desk_words":
        if inp["what"] == "status":
            assert desk.words(inp["status"], inp["name"], inp["scope"], inp["by"]) == exp["words"]
        elif inp["what"] == "admitted":
            assert desk.admitted_by(ticket=inp["ticket"], welcome=inp["welcome"], person=inp["person"]) == exp["words"]
        elif inp["what"] == "hold":
            assert desk.hold_words(inp["name"], inp["kind"], inp["template_hash"], inp["days"]) == exp["words"]
        else:
            assert desk.REFUSED == exp["face"] and desk.REFUSED["error"] == exp["words"]
    elif kind == "desk_name":
        assert desk.name_ok(inp["name"]) == exp["ok"]
    else:
        pytest.fail(f"unknown case kind {kind!r} in {contract}")
