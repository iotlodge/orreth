// PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp1, the bytes · 2026-09-22
// Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp2, the ground and the rails: rail_names · outbox_row · inbox_key · 2026-09-22
// Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp3, the ask road: ladder_step · manifest_pin · ask_fact · refused_fact · ask_kind · otpauth · hold_words · 2026-09-22
// Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp4, the loops: the five mcp kinds · beat_lock · loop_words · plan_words · observed_words · watch_note · cannot_act · improvement_note · crew_hash · turned_fact · 2026-09-23
// Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp6, the bodies' seam: the twelve minds kinds · backoff · park_rule · parked_words · parked_fact · harness_verdict · harness_command · 2026-09-24
//! The Rust conformance runner (canon 0008 · P7 sp1): every fixture under
//! `spine/conformance/*-v*.json` — the same files the Python reference
//! generated and passes, unchanged — dispatched by case kind exactly as
//! `spine/tests/test_conformance.py` dispatches it (same input fields, same
//! expected fields). A PORTED kind is checked; a kind not in `PORTED_KINDS`
//! is collected and named in the coverage report — never skipped silently.
//! The one test fails on any ported kind's mismatch, and on a ported kind the
//! runner has no arm for (the list and the dispatch must agree).

use orreth_spine::{
    ask, beat, body, canonical, content_hash, envelope, export, intent, kernel_self, mcp, memory,
    mitl, placement, proof, rails, services, stable, watch,
};
use serde_json::{json, Value};
use std::collections::BTreeMap;
use std::path::PathBuf;

/// The kinds this crate has ported — one explicit list, so the report is honest.
const PORTED_KINDS: &[&str] = &[
    "canonical",
    "encode",
    "encode_refuses",
    "decode_preserves",
    "totp",
    "totp_verify",
    "ladder",
    "class_level",
    "stop_demand",
    "restart_demand",
    "duty_text",
    "refused_words",
    "echo_reply",
    "watch_judge",
    "watch_reads",
    "address",
    "offer",
    "citation_name",
    "absent_words",
    "hash_chain",
    "chain_status",
    "verify",
    "verdict",
    "profile",
    "honor",
    "rail_names",
    "outbox_row",
    "inbox_key",
    "ladder_step",
    "manifest_pin",
    "ask_fact",
    "refused_fact",
    "ask_kind",
    "otpauth",
    "hold_words",
    "mcp_request",
    "mcp_tool_manifest",
    "mcp_server_manifest",
    "mcp_transport",
    "mcp_words",
    "beat_lock",
    "loop_words",
    "plan_words",
    "observed_words",
    "watch_note",
    "cannot_act",
    "improvement_note",
    "duplicate_words",
    "hold_expiry",
    "crew_hash",
    "turned_fact",
    // P7 sp5 — orreth.memory/1 and the signed export
    "search_terms",
    "memory_fact",
    "purge_fact",
    "digest_text",
    "digest_fact",
    "session_fact",
    "signed_bundle",
    "verify_signed",
    "did_of",
    // P7 sp6 — orreth.minds/1 (the Stable's laws) and orreth.bodies/1 (the bodies' seam)
    "route_for",
    "usd",
    "budget_duration",
    "resolve",
    "drift",
    "eol_due",
    "recommend",
    "deal",
    "deal_refuses",
    "drained_words",
    "act_words",
    "server_name",
    "backoff",
    "park_rule",
    "parked_words",
    "parked_fact",
    "harness_verdict",
    "harness_command",
];

fn fixture_dir() -> PathBuf {
    PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("../../../../spine/conformance")
}

fn fixtures() -> Vec<(String, Value)> {
    let dir = fixture_dir();
    let mut files: Vec<PathBuf> = std::fs::read_dir(&dir)
        .unwrap_or_else(|e| panic!("spine/conformance at {} — {e}", dir.display()))
        .map(|e| e.unwrap().path())
        .filter(|p| {
            p.file_name()
                .and_then(|n| n.to_str())
                .is_some_and(|n| n.ends_with(".json") && n.contains("-v"))
        })
        .collect();
    files.sort();
    assert!(
        !files.is_empty(),
        "spine/conformance holds no fixtures — the law says every wire change adds one"
    );
    files
        .into_iter()
        .map(|p| {
            let text = std::fs::read_to_string(&p).unwrap();
            assert!(
                text.is_ascii(),
                "{} is not ASCII — a fixture is language-neutral bytes",
                p.display()
            );
            (
                p.file_stem().unwrap().to_str().unwrap().to_string(),
                serde_json::from_str(&text).unwrap(),
            )
        })
        .collect()
}

fn s(v: &Value) -> &str {
    v.as_str()
        .unwrap_or_else(|| panic!("expected a string, got {v}"))
}

fn strings(v: &Value) -> Vec<String> {
    v.as_array()
        .unwrap()
        .iter()
        .map(|x| s(x).to_string())
        .collect()
}

fn hex_bytes(h: &str) -> [u8; 32] {
    let v: Vec<u8> = (0..h.len())
        .step_by(2)
        .map(|i| u8::from_str_radix(&h[i..i + 2], 16).unwrap())
        .collect();
    v.as_slice().try_into().unwrap()
}

fn opt_str(v: &Value) -> Option<&str> {
    v.as_str()
}

/// One case, checked as the Python runner checks it. `Err` carries what mismatched.
fn check(kind: &str, inp: &Value, exp: &Value) -> Result<(), String> {
    macro_rules! same {
        ($got:expr, $want:expr, $what:literal) => {{
            let (g, w) = (&$got, &$want);
            if g != w {
                return Err(format!("{}: got {:?}, fixture says {:?}", $what, g, w));
            }
        }};
    }
    match kind {
        "canonical" => {
            let bytes = canonical(&inp["obj"]);
            same!(
                String::from_utf8(bytes).unwrap(),
                s(&exp["bytes"]),
                "canonical bytes"
            );
            same!(content_hash(&inp["obj"]), s(&exp["hash"]), "content hash");
        }
        "encode" => {
            let bytes =
                envelope::encode(&inp["env"]).map_err(|e| format!("encode refused: {e}"))?;
            same!(
                String::from_utf8(bytes.clone()).unwrap(),
                s(&exp["bytes"]),
                "envelope bytes"
            );
            let back = envelope::decode(&bytes).map_err(|e| format!("decode refused: {e}"))?;
            same!(back, inp["env"], "decode(encode(env)) == env");
        }
        "encode_refuses" => match envelope::encode(&inp["env"]) {
            Ok(_) => return Err("encode did not refuse".into()),
            Err(e) => {
                let msg = e.to_string();
                for name in strings(&exp["names"]) {
                    if !msg.contains(&name) {
                        return Err(format!("refusal must name {name:?}: {msg}"));
                    }
                }
            }
        },
        "decode_preserves" => {
            let got = envelope::decode(s(&inp["bytes"]).as_bytes())
                .map_err(|e| format!("decode refused: {e}"))?;
            same!(got, exp["obj"], "decoded object");
        }
        // ---- orreth.proof/1: the code, the ladder, the level a class demands ----
        "totp" => {
            let got = proof::totp(s(&inp["secret"]), inp["time"].as_f64().unwrap())
                .map_err(|e| e.to_string())?;
            same!(got, s(&exp["code"]), "totp code");
        }
        "totp_verify" => {
            let got: Vec<bool> = inp["at"]
                .as_array()
                .unwrap()
                .iter()
                .map(|t| {
                    proof::verify(
                        s(&inp["secret"]),
                        opt_str(&inp["code"]),
                        t.as_f64().unwrap(),
                        proof::DRIFT,
                    )
                })
                .collect();
            let want: Vec<bool> = exp["ok"]
                .as_array()
                .unwrap()
                .iter()
                .map(|b| b.as_bool().unwrap())
                .collect();
            same!(got, want, "verify at each time");
        }
        "ladder" => {
            let order = strings(&inp["order"]);
            let refs: Vec<&str> = order.iter().map(String::as_str).collect();
            let sorted = proof::ladder(&refs).map_err(|e| e.to_string())?;
            let sorted: Vec<String> = sorted.iter().map(|c| c.to_string()).collect();
            same!(sorted, strings(&exp["sorted"]), "sorted classes");
            let levels: Vec<String> = sorted
                .iter()
                .map(|c| proof::level_of_class(c).unwrap().to_string())
                .collect();
            same!(levels, strings(&exp["levels"]), "levels");
        }
        "class_level" => {
            let master = inp
                .get("master")
                .map(orreth_spine::py::truthy)
                .unwrap_or(false);
            let got = proof::level_for(s(&inp["class"]), master).map_err(|e| e.to_string())?;
            same!(got, s(&exp["level"]), "level");
        }
        "stop_demand" => same!(
            proof::stop_demand(s(&inp["intention_kind"])).to_value(),
            *exp,
            "stop demand"
        ),
        // ---- orreth.intent/1: the restart's demand, the duty's framing, the refusal, echo ----
        "restart_demand" => same!(
            proof::restart_demand(s(&inp["intention_kind"])).to_value(),
            *exp,
            "restart demand"
        ),
        "duty_text" => {
            let every = inp["every_s"].as_i64().unwrap();
            same!(ask::cadence_words(every), s(&exp["cadence"]), "cadence");
            let notes = strings(&inp["notes"]);
            same!(
                ask::duty_text(s(&inp["text"]), every, opt_str(&inp["since"]), &notes),
                s(&exp["text"]),
                "duty text"
            );
        }
        "refused_words" => same!(
            ask::refused_words(opt_str(&inp["reply"])),
            exp["refused"].as_bool().unwrap(),
            "refused"
        ),
        "echo_reply" => same!(
            ask::echo_reply(s(&inp["name"]), s(&inp["text"])),
            s(&exp["reply"]),
            "echo reply"
        ),
        // ---- orreth.watch/1: the sense of a watch — red WHEN the condition holds ----
        "watch_judge" => {
            let red = watch::judge(
                s(&inp["op"]),
                inp["value"].as_f64().unwrap(),
                inp["threshold"].as_f64().unwrap(),
            )
            .ok_or_else(|| format!("unknown op {}", inp["op"]))?;
            same!(
                (red, watch::state(red)),
                (exp["red"].as_bool().unwrap(), s(&exp["state"])),
                "red · state"
            );
        }
        "watch_reads" => {
            let got = watch::reads(
                s(&inp["metric"]),
                s(&inp["op"]),
                &inp["threshold"],
                &inp["value"],
                inp["red"].as_bool().unwrap(),
            );
            same!(got, s(&exp["reads"]), "reads");
        }
        // ---- orreth.ask/1: the head of an ask, the offer, the citation, the door's refusal ----
        "address" => {
            let got = ask::address(s(&inp["text"]), &strings(&inp["names"]));
            same!(got.as_deref(), opt_str(&exp["name"]), "addressed name");
        }
        "offer" => {
            let got = watch::offer_in(opt_str(&inp["reply"]))
                .map(|o| o.to_value())
                .unwrap_or(Value::Null);
            same!(got, exp["offer"], "offer");
        }
        "citation_name" => {
            let rule = mitl::Rule::from_value(inp.get("rule").unwrap_or(&Value::Null));
            let got = mitl::citation_name(s(&inp["path"]), opt_str(&inp["heading"]), rule);
            same!(got, s(&exp["name"]), "citation name");
        }
        "absent_words" => same!(
            ask::refusal_words(s(&inp["name"]), s(&inp["reason"])),
            s(&exp["reply"]),
            "refusal words"
        ),
        // ---- orreth.compliance/1: the hash chain, the chain's status, the verifier ----
        "hash_chain" => {
            let got = export::hash_chain(inp["rows"].as_array().unwrap());
            same!(got, strings(&exp["hashes"]), "hashes");
            same!(
                export::root_hash(&got),
                opt_str(&exp["root_hash"]),
                "root hash"
            );
        }
        "chain_status" => {
            let got: Vec<String> = inp["rows"]
                .as_array()
                .unwrap()
                .iter()
                .map(|r| export::chain_status(r).to_string())
                .collect();
            same!(got, strings(&exp["status"]), "status per row");
        }
        "verify" => {
            for part in ["bundle", "truncated", "resealed"] {
                same!(
                    export::verify(&inp[part]),
                    exp[part].as_bool().unwrap(),
                    "verify"
                );
            }
            same!(
                inp["resealed"]["summary"]["chain_broken"],
                exp["resealed_chain_broken"],
                "resealed chain_broken"
            );
        }
        // ---- orreth.impact/1: the verdict ladder — rules, never a brain ----
        "verdict" => same!(
            mitl::verdict(&inp["touches"]),
            s(&exp["verdict"]),
            "verdict"
        ),
        // ---- orreth.placement/1: the profile's defaults, the honor rule and its reasons ----
        "profile" => {
            let got = placement::profile(&inp["template"]).map_err(|e| e.to_string())?;
            same!(got.to_value(), exp["profile"], "profile");
            same!(
                String::from_utf8(canonical(&got.to_value())).unwrap(),
                s(&exp["bytes"]),
                "profile bytes"
            );
        }
        "honor" => {
            let prof =
                placement::Profile::from_value(&inp["profile"]).map_err(|e| e.to_string())?;
            let ground =
                placement::Ground::from_value(&inp["ground"]).map_err(|e| e.to_string())?;
            let (ok, reasons) = placement::honor(&prof, &ground);
            same!(
                (ok, reasons),
                (exp["honored"].as_bool().unwrap(), strings(&exp["reasons"])),
                "honored · reasons"
            );
            same!(placement::why_here(&prof, &ground), s(&exp["why"]), "why");
        }
        // ---- orreth.rails/1 (P7 sp2): the rails' names and shapes — what the ground and rails stand on ----
        "rail_names" => {
            let (ns, name) = (s(&inp["ns"]), opt_str(&inp["name"]));
            let got = serde_json::json!({
                "serve_queue": rails::serve_queue(ns, name),
                "serve_key": rails::serve_key(ns, name),
                "scope": rails::scope_from(opt_str(&inp["scope"])),
                "command_exchange": rails::COMMAND_EXCHANGE,
                "heartbeat_queue": rails::HEARTBEAT_QUEUE,
                "heartbeat_key": rails::HEARTBEAT_KEY,
                "heartbeat_topic": rails::HEARTBEAT_TOPIC,
            });
            same!(got, *exp, "rail names");
        }
        "outbox_row" => {
            let row = rails::outbox_row(&inp["env"]).map_err(|e| e.to_string())?;
            same!(row.message_id, s(&exp["message_id"]), "message id");
            same!(
                String::from_utf8(row.body).unwrap(),
                s(&exp["body"]),
                "row body"
            );
            same!(
                rails::topic_for(&inp["env"]),
                opt_str(&exp["topic"]),
                "topic"
            );
            let key = rails::key_for(&inp["env"]);
            same!(key.as_deref(), opt_str(&exp["key"]), "key");
        }
        "inbox_key" => {
            let route = rails::inbox_route(&inp["env"]);
            let got = match &route {
                rails::InboxRoute::Once { message_id } => serde_json::json!({
                    "road": "once", "message_id": message_id, "aggregate_id": null, "sequence": null}),
                rails::InboxRoute::Sequenced {
                    message_id,
                    aggregate_id,
                    sequence,
                } => serde_json::json!({
                    "road": "sequenced", "message_id": message_id, "aggregate_id": aggregate_id, "sequence": sequence}),
            };
            same!(got, *exp, "inbox road");
        }
        // ---- orreth.services/1 (P6.5 sp1): the one ladder's legality; the manifest pin ----
        "ladder_step" => same!(
            services::ladder_step(opt_str(&inp["state"]), s(&inp["verb"])).to_value(),
            *exp,
            "ladder step"
        ),
        "manifest_pin" => {
            same!(
                canonical::canonical_string(&inp["manifest"]),
                s(&exp["bytes"]).to_string(),
                "manifest bytes"
            );
            same!(
                services::pin(&inp["manifest"]),
                s(&exp["hash"]).to_string(),
                "manifest pin"
            );
        }
        // ---- orreth.askroad/1 (P7 sp3): the ask's fact, the door's refusal, the kind, the proof's words ----
        "ask_fact" | "refused_fact" => {
            let window = inp["window"].as_object().map(|w| {
                (
                    orreth_spine::py::python_str(&w["from"]),
                    orreth_spine::py::python_str(&w["to"]),
                )
            });
            let (ask_id, text, scope, person) = (
                s(&inp["ask_id"]),
                s(&inp["text"]),
                s(&inp["scope"]),
                s(&inp["person"]),
            );
            let fanout = opt_str(&inp["fanout"]);
            let (typ, payload, chain): (&str, Value, Vec<&str>) = if kind == "ask_fact" {
                let payload = ask::received_payload(
                    ask_id,
                    text,
                    opt_str(&inp["target"]),
                    opt_str(&inp["session"]),
                    window.as_ref().map(|(f, t)| (f.as_str(), t.as_str())),
                );
                same!(payload, exp["payload"], "the ask's payload");
                (ask::ASK_RECEIVED, payload, vec![person])
            } else {
                same!(
                    ask::refusal_words(s(&inp["target"]), s(&inp["reason"])),
                    s(&exp["reply"]).to_string(),
                    "the door's reply"
                );
                same!(
                    exp["served_by"],
                    Value::String(ask::KERNEL.into()),
                    "the kernel serves the refusal"
                );
                same!(
                    exp["status"],
                    Value::String("refused".into()),
                    "the row's status"
                );
                let payload = ask::refused_payload(
                    ask_id,
                    text,
                    s(&inp["target"]),
                    s(&inp["reason"]),
                    opt_str(&inp["session"]),
                );
                (ask::ASK_REFUSED, payload, vec![person, ask::KERNEL])
            };
            let env = ask::ask_fact(
                typ,
                scope,
                ask_id,
                payload,
                fanout,
                &chain,
                &inp["marker"],
                s(&inp["message_id"]),
                s(&inp["occurred_at"]),
            );
            let bytes = envelope::encode(&env).map_err(|e| e.to_string())?;
            same!(
                String::from_utf8(bytes).unwrap(),
                s(&exp["bytes"]).to_string(),
                "the fact's bytes"
            );
            same!(env["type"], exp["topic"], "the topic");
            if kind == "ask_fact" {
                same!(env["aggregate"]["id"], exp["key"], "the key");
                same!(
                    env["correlation_id"],
                    exp["correlation_id"],
                    "the correlation"
                );
            }
        }
        "ask_kind" => same!(
            intent::read_words(s(&inp["text"])).to_value(),
            *exp,
            "the kind of an ask"
        ),
        "otpauth" => same!(
            proof::otpauth_uri(s(&inp["person"]), s(&inp["secret"]), "Orreth"),
            s(&exp["uri"]).to_string(),
            "otpauth uri"
        ),
        "hold_words" => same!(
            proof::question_for(
                s(&inp["level"]),
                s(&inp["what"]),
                inp["needs_code"].as_bool().unwrap_or(false)
            ),
            s(&exp["text"]).to_string(),
            "the hold's words"
        ),
        // ---- orreth.mcp/1 (P6.5 sp2, ported P7 sp4): the three requests' bytes, the pins, the words ----
        "mcp_request" => {
            let req = match s(&inp["method"]) {
                "initialize" => mcp::initialize_request(),
                "tools/list" => mcp::list_request(),
                _ => mcp::call_request(s(&inp["tool"]), &inp["arguments"]),
            };
            same!(req["id"], exp["id"], "the fixed id");
            same!(
                String::from_utf8(mcp::request_bytes(&req)).unwrap(),
                s(&exp["bytes"]).to_string(),
                "the request's bytes"
            );
        }
        "mcp_tool_manifest" => {
            let m = mcp::tool_manifest(s(&inp["server"]), &inp["tool"]);
            same!(m, exp["manifest"], "the tool's manifest");
            same!(m["name"], exp["shelf_name"], "the shelf name");
            same!(m["consequence"], exp["consequence"], "the class");
            same!(
                canonical::canonical_string(&m),
                s(&exp["bytes"]).to_string(),
                "the manifest's bytes"
            );
            same!(services::pin(&m), s(&exp["hash"]).to_string(), "the pin");
        }
        "mcp_server_manifest" => {
            let tools = inp["tools"].as_array().cloned().unwrap_or_default();
            let m = mcp::server_manifest(s(&inp["locator"]), &tools)?;
            same!(m, exp["manifest"], "the server's manifest");
            same!(m["transport"], exp["transport"], "the transport");
            same!(services::pin(&m), s(&exp["hash"]).to_string(), "the pin");
        }
        "mcp_transport" => same!(
            Value::String(mcp::transport_of(s(&inp["locator"])).into()),
            exp["transport"],
            "the transport"
        ),
        "mcp_words" => {
            same!(
                Value::String(mcp::GONE.into()),
                exp["gone"],
                "the gone words"
            );
            same!(
                Value::String(mcp::STRIKES_DIAL.into()),
                exp["strikes_dial"],
                "the dial"
            );
            same!(
                Value::from(mcp::STRIKES_DEFAULT),
                exp["strikes_default"],
                "the default"
            );
            same!(
                Value::String(mcp::PROTOCOL.into()),
                exp["protocol"],
                "the protocol"
            );
            same!(
                serde_json::json!({"initialize": mcp::INITIALIZE_ID, "tools/list": mcp::LIST_ID, "tools/call": mcp::CALL_ID}),
                exp["ids"],
                "the fixed ids"
            );
        }
        // ---- orreth.loops/1 (P7 sp4): the beat lock, the loop's words, the watch's turned fact ----
        "beat_lock" => {
            same!(Value::from(beat::BEAT_LOCK), exp["base"], "the base");
            let beats: BTreeMap<String, i64> = beat::BEATS
                .iter()
                .map(|(n, c)| (n.to_string(), *c))
                .collect();
            same!(
                serde_json::to_value(&beats).unwrap(),
                exp["beats"],
                "the classes"
            );
            let keys: BTreeMap<String, i32> = beat::BEATS
                .iter()
                .map(|(n, _)| (n.to_string(), beat::beat_key(n).unwrap()))
                .collect();
            same!(
                serde_json::to_value(&keys).unwrap(),
                exp["keys"],
                "the keys"
            );
            same!(
                Value::String(beat::HELD.into()),
                exp["held"],
                "the held words"
            );
        }
        "loop_words" => {
            for (got, want, what) in [
                (
                    intent::CADENCE_DUE,
                    "cadence_due",
                    "the cadence's observation",
                ),
                (intent::CANNOT_ACT, "cannot_act", "the runner's opening"),
                (
                    watch::WATCH_TURNED,
                    "watch_turned",
                    "the turned fact's name",
                ),
                (
                    ask::HARNESS_FAILED,
                    "harness_failed",
                    "the harness fact's name",
                ),
                (intent::INTENTION_DECLARED, "intention_declared", "declared"),
                (intent::INTENTION_STOPPED, "intention_stopped", "stopped"),
                (
                    intent::INTENTION_RESTARTED,
                    "intention_restarted",
                    "restarted",
                ),
                (intent::WATCH_RED, "watch_red", "the kind"),
                (ask::W26_WORDS, "w26_words", "W26's words"),
                (ask::W26_STEP, "w26_step", "W26's step"),
            ] {
                if exp[want] != Value::String(got.into()) {
                    return Err(format!("{what}: got {got:?}, fixture says {:?}", exp[want]));
                }
            }
            same!(
                Value::from(ask::LEASE_TTL_S),
                exp["lease_ttl_s"],
                "the lease"
            );
            same!(
                intent::resiliency(),
                exp["resiliency"],
                "the first intention"
            );
        }
        "plan_words" => same!(
            intent::plan_words(s(&inp["serves"]), s(&inp["words"]), s(&inp["observed"])),
            s(&exp["text"]).to_string(),
            "the planner's ask"
        ),
        "observed_words" => same!(
            intent::observed_words(s(&inp["kind"]), s(&inp["ref"]), opt_str(&inp["note"])),
            s(&exp["text"]).to_string(),
            "the observation"
        ),
        "watch_note" => same!(
            intent::watch_note(
                s(&inp["name"]),
                s(&inp["metric"]),
                s(&inp["op"]),
                &inp["threshold"],
                &inp["value"]
            ),
            s(&exp["text"]).to_string(),
            "the watch's note"
        ),
        "cannot_act" => same!(
            Value::Bool(intent::cannot_act(opt_str(&inp["reply"]))),
            exp["cannot"],
            "the opening"
        ),
        "improvement_note" => same!(
            intent::improvement_note(s(&inp["who"]), opt_str(&inp["reply"])),
            s(&exp["note"]).to_string(),
            "the note"
        ),
        "hold_expiry" => {
            same!(
                Value::from(proof::HOLD_TTL_MIN),
                exp["minutes"],
                "the window"
            );
            same!(
                proof::expired_words(proof::HOLD_TTL_MIN),
                s(&exp["reason"]).to_string(),
                "the reason"
            );
            same!(
                Value::String(proof::EXPIRED_REPLY.into()),
                exp["reply"],
                "the reply"
            );
        }
        "duplicate_words" => same!(
            intent::duplicate_words(s(&inp["kind"]), s(&inp["words"])),
            s(&exp["text"]).to_string(),
            "the duplicate's words"
        ),
        "crew_hash" => {
            let shape: Vec<(String, Value)> = inp["shape"]
                .as_array()
                .unwrap()
                .iter()
                .map(|p| (s(&p[0]).to_string(), p[1].clone()))
                .collect();
            same!(
                intent::crew_shape_hash(&shape),
                s(&exp["hash"]).to_string(),
                "the crew's hash"
            );
        }
        "search_terms" => {
            same!(
                memory::search_terms(s(&inp["query"])),
                s(&exp["terms"]).to_string(),
                "the terms"
            );
            let fb: Vec<String> = exp["fallback"]
                .as_array()
                .unwrap()
                .iter()
                .map(|v| s(v).to_string())
                .collect();
            same!(
                memory::fallback_words(s(&inp["query"])),
                fb,
                "the fallback words"
            );
        }
        "memory_fact" | "purge_fact" => {
            let payload = if kind == "memory_fact" {
                memory::landed_payload(
                    s(&inp["namespace"]),
                    s(&inp["key"]),
                    &content_hash(&inp["body"]),
                    opt_str(&inp["supersedes"]),
                )
            } else {
                let hashes: Vec<String> = inp["hashes"]
                    .as_array()
                    .unwrap()
                    .iter()
                    .map(|v| s(v).to_string())
                    .collect();
                memory::purge_payload(s(&inp["namespace"]), s(&inp["key"]), &hashes)
            };
            same!(payload, exp["payload"], "the payload");
            let env = memory::fact(
                if kind == "memory_fact" {
                    memory::MEMORY_EVENT
                } else {
                    memory::PURGE_EVENT
                },
                s(&inp["scope"]),
                payload,
                s(&inp["by"]),
                None,
                s(&inp["message_id"]),
                s(&inp["occurred_at"]),
            );
            let bytes = envelope::encode(&env).map_err(|e| e.to_string())?;
            same!(
                String::from_utf8(bytes).unwrap(),
                s(&exp["bytes"]).to_string(),
                "the fact's bytes"
            );
        }
        "digest_text" => {
            let asks: Vec<memory::DigestAsk> = inp["asks"]
                .as_array()
                .unwrap()
                .iter()
                .map(|a| memory::DigestAsk {
                    ask_id: s(&a[0]).into(),
                    text: s(&a[1]).into(),
                    reply: opt_str(&a[2]).map(str::to_string),
                    status: s(&a[3]).into(),
                    asked_at: memory::Civil::parse(s(&a[4])).unwrap(),
                    replied_at: opt_str(&a[5]).and_then(memory::Civil::parse),
                    who: s(&a[6]).into(),
                })
                .collect();
            let mems: Vec<(String, String, String)> = inp["memories"]
                .as_array()
                .unwrap()
                .iter()
                .map(|m| (s(&m[0]).into(), s(&m[1]).into(), s(&m[2]).into()))
                .collect();
            let (body, sources) = memory::digest_lines(
                s(&inp["session_id"]),
                opt_str(&inp["title"]),
                memory::Civil::parse(s(&inp["opened"])).unwrap(),
                &asks,
                &mems,
            );
            same!(body, s(&exp["body"]).to_string(), "the digest's text");
            let want: Vec<String> = exp["sources"]
                .as_array()
                .unwrap()
                .iter()
                .map(|v| s(v).to_string())
                .collect();
            same!(sources, want, "the sources");
        }
        "session_fact" => {
            let payload = memory::session_payload(
                s(&inp["session_id"]),
                s(&inp["person"]),
                opt_str(&inp["title"]),
                opt_str(&inp["archived"]),
                s(&inp["state"]),
            );
            same!(payload, exp["payload"], "the payload");
            let env = memory::fact(
                memory::SESSION_OPENED,
                s(&inp["scope"]),
                payload,
                s(&inp["person"]),
                Some(s(&inp["session_id"])),
                s(&inp["message_id"]),
                s(&inp["occurred_at"]),
            );
            let bytes = envelope::encode(&env).map_err(|e| e.to_string())?;
            same!(
                String::from_utf8(bytes).unwrap(),
                s(&exp["bytes"]).to_string(),
                "the fact's bytes"
            );
        }
        "digest_fact" => {
            let payload = memory::digest_payload(
                s(&inp["digest_id"]),
                s(&inp["body"]),
                s(&inp["session"]),
                inp["sources"].as_u64().unwrap_or(0) as usize,
            );
            same!(payload, exp["payload"], "the payload");
            let env = memory::fact(
                memory::DIGEST_EVENT,
                s(&inp["scope"]),
                payload,
                s(&inp["by"]),
                Some(s(&inp["session"])),
                s(&inp["message_id"]),
                s(&inp["occurred_at"]),
            );
            let bytes = envelope::encode(&env).map_err(|e| e.to_string())?;
            same!(
                String::from_utf8(bytes).unwrap(),
                s(&exp["bytes"]).to_string(),
                "the fact's bytes"
            );
        }
        "signed_bundle" => {
            let seed = hex_bytes(s(&inp["seed_hex"]));
            let signer = kernel_self::KernelSelf::from_seed(&seed, "kernel");
            let rows = inp["rows"].as_array().unwrap();
            let b = export::seal(
                rows,
                &inp["scope"],
                s(&inp["world"]),
                s(&inp["generated_at"]),
                Some(&signer),
            );
            same!(b, exp["bundle"], "the sealed bundle");
            same!(export::verify(&b), true, "the bundle verifies");
        }
        "verify_signed" => {
            same!(
                export::verify(&inp["bundle"]),
                exp["ok"].as_bool().unwrap(),
                "verify"
            );
        }
        "did_of" => {
            let seed = hex_bytes(s(&inp["seed_hex"]));
            let me = kernel_self::KernelSelf::from_seed(&seed, s(&inp["kind"]));
            same!(me.did(), s(&exp["did"]).to_string(), "the DID");
            same!(
                me.verify_key_hex(),
                s(&exp["public_key_hex"]).to_string(),
                "the public key"
            );
        }
        "turned_fact" => {
            let payload = watch::turned_payload(
                s(&inp["watch_id"]),
                s(&inp["name"]),
                s(&inp["metric"]),
                s(&inp["op"]),
                &inp["threshold"],
                &inp["value"],
                opt_str(&inp["from"]),
                s(&inp["to"]),
            );
            same!(payload, exp["payload"], "the payload");
            let env = watch::turned_fact(
                s(&inp["scope"]),
                s(&inp["watch_id"]),
                payload,
                s(&inp["message_id"]),
                s(&inp["occurred_at"]),
            );
            let bytes = envelope::encode(&env).map_err(|e| e.to_string())?;
            same!(
                String::from_utf8(bytes).unwrap(),
                s(&exp["bytes"]).to_string(),
                "the fact's bytes"
            );
            same!(env["type"], exp["topic"], "the topic");
            same!(
                env["correlation_id"],
                exp["correlation_id"],
                "the correlation"
            );
        }
        // ---- orreth.minds/1 (P6.5 sp3, ported P7 sp6): the Stable's laws ----
        "route_for" => same!(
            stable::route_for(s(&inp["provider"]), s(&inp["model"]), opt_str(&inp["base"])),
            *exp,
            "the route"
        ),
        "usd" => same!(
            json!(stable::usd(
                &inp["price"],
                inp["tokens_in"].as_i64().unwrap_or(0),
                inp["tokens_out"].as_i64().unwrap_or(0)
            )),
            exp["usd"],
            "the dollars"
        ),
        "budget_duration" => same!(
            stable::budget_duration(inp["days"].as_i64().unwrap_or(0)),
            s(&exp["duration"]).to_string(),
            "the window"
        ),
        "resolve" => {
            let stalls = inp["stalls"].as_array().cloned().unwrap_or_default();
            let assignments = inp["assignments"].as_array().cloned().unwrap_or_default();
            let got = stable::resolve(
                &stalls,
                &assignments,
                stable::ResolveAsk {
                    subject: opt_str(&inp["subject"]),
                    klass: opt_str(&inp["klass"]),
                    pin: opt_str(&inp["pin"]),
                    model: opt_str(&inp["model"]),
                },
            );
            same!(got, *exp, "the routing decision");
        }
        "drift" => same!(
            json!(stable::drift(&inp["pinned"], &inp["seen"])),
            exp["moved"],
            "what moved"
        ),
        "eol_due" => same!(
            stable::eol_due(
                opt_str(&inp["expires"]),
                s(&inp["now"]),
                inp["horizon_days"].as_i64().unwrap_or(30)
            ),
            *exp,
            "the appointment"
        ),
        "recommend" => {
            let stalls = inp["stalls"].as_array().cloned().unwrap_or_default();
            same!(
                stable::recommend(&stalls, s(&inp["retiring"])),
                *exp,
                "the swap"
            );
        }
        "deal" => {
            let got = stable::deal(
                s(&inp["model"]),
                s(&inp["provider"]),
                stable::DealAsk {
                    base: opt_str(&inp["base"]),
                    price: inp.get("price"),
                    context: inp.get("context"),
                    modalities: inp.get("modalities"),
                    klass: inp.get("klass").and_then(Value::as_str),
                    key: inp.get("key").map(|k| k.as_str()),
                    expires: opt_str(&inp["expires"]),
                },
            )
            .map_err(|e| format!("the deal refused: {e}"))?;
            same!(got, *exp, "the deal");
        }
        "deal_refuses" => {
            let got = stable::deal(
                s(&inp["model"]),
                s(&inp["provider"]),
                stable::DealAsk {
                    klass: inp.get("klass").and_then(Value::as_str),
                    key: inp.get("key").map(|k| k.as_str()),
                    ..Default::default()
                },
            );
            match got {
                Ok(d) => return Err(format!("the deal did not refuse: {d}")),
                Err(words) => same!(words, s(&exp["words"]).to_string(), "the refusal"),
            }
        }
        "drained_words" => same!(
            stable::drained_words(s(&inp["name"]), inp.get("gauge").filter(|g| !g.is_null())),
            s(&exp["words"]).to_string(),
            "out of fuel"
        ),
        "act_words" => same!(
            stable::act_words(s(&inp["tool"]), &inp["args"]),
            s(&exp["words"]).to_string(),
            "the act named"
        ),
        "server_name" => same!(
            mcp::server_name(&inp["info"], s(&inp["locator"])),
            s(&exp["name"]).to_string(),
            "the server's name"
        ),
        // ---- orreth.bodies/1 (P7 sp6): the kernel governs the bodies it spawns; the harness rides the rail ----
        "backoff" => same!(
            json!(body::backoff_s(inp["deaths"].as_i64().unwrap_or(0))),
            exp["wait_s"],
            "the wait"
        ),
        "park_rule" => {
            let exits: Vec<String> = strings(&inp["exits"]);
            same!(
                body::park_rule(
                    &exits,
                    s(&inp["now"]),
                    inp["window_s"].as_i64().unwrap_or(300),
                    inp["strikes"].as_i64().unwrap_or(3)
                ),
                *exp,
                "the park law"
            );
        }
        "parked_words" => same!(
            body::parked_words(
                s(&inp["name"]),
                inp["deaths"].as_i64().unwrap_or(0),
                inp["window_s"].as_i64().unwrap_or(300),
                opt_str(&inp["last_words"])
            ),
            s(&exp["words"]).to_string(),
            "the parked words"
        ),
        "parked_fact" => {
            let payload = body::parked_payload(
                s(&inp["name"]),
                opt_str(&inp["did"]),
                inp["deaths"].as_i64().unwrap_or(0),
                inp["window_s"].as_i64().unwrap_or(300),
                opt_str(&inp["last_words"]),
            );
            same!(payload, exp["payload"], "the payload");
            let env = body::parked_fact(
                s(&inp["scope"]),
                s(&inp["name"]),
                payload,
                s(&inp["message_id"]),
                s(&inp["occurred_at"]),
            );
            same!(env["type"], exp["type"], "the type");
            same!(env["authority_chain"], exp["chain"], "the chain");
            let bytes = envelope::encode(&env).map_err(|e| e.to_string())?;
            same!(
                String::from_utf8(bytes).unwrap(),
                s(&exp["bytes"]).to_string(),
                "the fact's bytes"
            );
        }
        "harness_verdict" => {
            let cases = inp["cases"].as_array().cloned().unwrap_or_default();
            let replies = inp["replies"].as_array().cloned().unwrap_or_default();
            same!(body::verdict(&cases, &replies), *exp, "the verdict");
        }
        "harness_command" => {
            let cases = inp["cases"].as_array().cloned().unwrap_or_default();
            let payload = body::harness_payload(
                s(&inp["run_id"]),
                s(&inp["target"]),
                &cases,
                opt_str(&inp["arm"]),
                opt_str(&inp["parent_marker"]),
            );
            same!(payload, exp["payload"], "the payload");
            same!(payload["target"], exp["queue_target"], "the bench");
            let env = body::harness_command(
                s(&inp["scope"]),
                s(&inp["run_id"]),
                payload,
                s(&inp["message_id"]),
                s(&inp["occurred_at"]),
            );
            same!(env["type"], exp["type"], "the type");
            same!(
                env["correlation_id"],
                exp["correlation_id"],
                "the correlation"
            );
            same!(env["authority_chain"], exp["chain"], "the chain");
            let bytes = envelope::encode(&env).map_err(|e| e.to_string())?;
            same!(
                String::from_utf8(bytes).unwrap(),
                s(&exp["bytes"]).to_string(),
                "the command's bytes"
            );
        }
        other => {
            return Err(format!(
                "kind {other:?} is listed in PORTED_KINDS but the runner has no arm for it"
            ))
        }
    }
    Ok(())
}

#[test]
fn every_fixture_every_case_by_kind() {
    let mut total = 0usize;
    let mut ported = 0usize;
    let mut ported_kinds: BTreeMap<&str, usize> = BTreeMap::new();
    let mut unported: BTreeMap<String, usize> = BTreeMap::new();
    let mut failures: Vec<String> = Vec::new();

    for (file, doc) in fixtures() {
        let contract = s(&doc["contract"]).to_string();
        for case in doc["cases"].as_array().unwrap() {
            total += 1;
            let kind = s(&case["kind"]);
            let id = format!("{file}::{}", s(&case["name"]));
            if let Some(k) = PORTED_KINDS.iter().find(|k| **k == kind) {
                ported += 1;
                *ported_kinds.entry(k).or_default() += 1;
                if let Err(why) = check(kind, &case["input"], &case["expect"]) {
                    failures.push(format!("  {id} [{kind} · {contract}]\n      {why}"));
                }
            } else {
                *unported.entry(kind.to_string()).or_default() += 1;
            }
        }
    }

    let kinds_line = ported_kinds
        .iter()
        .map(|(k, n)| format!("{k} ({n})"))
        .collect::<Vec<_>>()
        .join(" · ");
    let unported_line = if unported.is_empty() {
        "none".to_string()
    } else {
        unported
            .iter()
            .map(|(k, n)| format!("{k} ({n})"))
            .collect::<Vec<_>>()
            .join(" · ")
    };
    println!("orreth-spine conformance — ported {ported}/{total} cases · kinds ported: {kinds_line} · not yet ported: {unported_line}");
    for k in PORTED_KINDS {
        assert!(
            ported_kinds.contains_key(k),
            "PORTED_KINDS names {k:?} but no fixture carries that kind — the list lies"
        );
    }
    assert!(
        failures.is_empty(),
        "{} ported case(s) mismatched the reference:\n{}",
        failures.len(),
        failures.join("\n")
    );
}
