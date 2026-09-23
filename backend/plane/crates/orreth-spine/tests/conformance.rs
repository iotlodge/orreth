// PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp1, the bytes · 2026-09-22
// Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp2, the ground and the rails: rail_names · outbox_row · inbox_key · 2026-09-22
// Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp3, the ask road: ladder_step · manifest_pin · ask_fact · refused_fact · ask_kind · otpauth · hold_words · 2026-09-22
//! The Rust conformance runner (canon 0008 · P7 sp1): every fixture under
//! `spine/conformance/*-v*.json` — the same files the Python reference
//! generated and passes, unchanged — dispatched by case kind exactly as
//! `spine/tests/test_conformance.py` dispatches it (same input fields, same
//! expected fields). A PORTED kind is checked; a kind not in `PORTED_KINDS`
//! is collected and named in the coverage report — never skipped silently.
//! The one test fails on any ported kind's mismatch, and on a ported kind the
//! runner has no arm for (the list and the dispatch must agree).

use orreth_spine::{
    ask, canonical, content_hash, envelope, export, intent, mitl, placement, proof, rails,
    services, watch,
};
use serde_json::Value;
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
