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
"""The conformance suite (canon 0008): language-neutral fixtures the
Python reference must pass today and `orrethd` must pass in Phase 7 — the
same files, unchanged. A fixture the reference fails is a wound."""
import json
import os
from contextlib import contextmanager
from pathlib import Path

import pytest

from orreth_spine import (dispatch, envelope as ev, export, ground, harness, intent, mcp, mitl, monitor, placement,
                          presence, proof, rails, resident, scheduler, services)

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
    # ---- orreth.watch/1 (W14): the sense of a watch — red WHEN the condition holds ----
    elif kind == "watch_judge":
        red = monitor.judge_one(inp["op"], inp["value"], inp["threshold"])
        assert (red, "red" if red else "green") == (exp["red"], exp["state"])
    elif kind == "watch_reads":
        assert monitor.reads(inp) == exp["reads"]
    # ---- orreth.ask/1 (W19): the door's refusal for a body that is not here ----
    elif kind == "address":                      # W7: a name at the head selects that body
        assert dispatch.address(inp["text"], inp["names"]) == exp["name"]
    elif kind == "offer":                        # walk #7: the monitor's offer, read from its words
        assert monitor.offer_in(inp["reply"]) == exp["offer"]
    elif kind == "citation_name":                # W15: a citation in a human's name
        assert mitl.citation_name(inp["path"], inp["heading"], inp["rule"]) == exp["name"]
    elif kind == "absent_words":
        assert dispatch.refusal_words(inp["name"], inp["reason"]) == exp["reply"]
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
    elif kind == "improvement_note":
        assert intent.improvement_note(inp["who"], inp["reply"]) == exp["note"]
    elif kind == "crew_hash":                    # the crew's shape, sorted, as canonical bytes
        assert intent.crew_shape_hash([(n, c) for n, c in inp["shape"]]) == exp["hash"]
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
    else:
        pytest.fail(f"unknown case kind {kind!r} in {contract}")
