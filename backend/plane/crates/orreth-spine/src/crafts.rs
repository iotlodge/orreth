// PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch Phase 8 THE WORKSHOP sp2, THE SHELF WIDENED: the craft kinds · the wear rows · the hull's edges · the cut's demand · 2026-10-05
//! THE SHELF WIDENED (canon 0010 lock 3 · lock 6 · 0004 AG-9), PURE — the laws
//! `orreth_spine.crafts` keeps, word for word (fixture `crafts-v0.json`): the craft
//! kinds a body is made of (`template · prompt · skill · policy · graph · binding ·
//! golden`) on the ONE shelf — a craft's shelf name `<name>.<kind>`, its ADDRESS
//! `craft:<name>.<kind>` (never a DID: a component is not a self), each kind's
//! declaration reading whole, the graph declaration v0 and its one path, the hull's
//! three edges read off an ask's marker, a source's two forms, what a cut demands by
//! class, and the rows a body wears at its join. The ground half is `crafts_live`.

use crate::hash::content_hash;
use crate::py::repr_str;
use serde_json::{json, Value};

pub const CONTRACT: &str = "orreth.crafts/1";
pub const CRAFT_KINDS: [&str; 7] = ["template", "prompt", "skill", "policy", "graph", "binding", "golden"];
pub const NODE_KINDS: [&str; 2] = ["think", "echo"];
/// Phase 8 sp3: what a way out may be conditioned on — the hull's edge · the ask's words · the last reply.
pub const WHEN_KEYS: [&str; 3] = ["edge", "ask", "reply"];
pub const EDGES: [&str; 3] = ["chat", "work", "event"];
pub const STRUCTURAL: [&str; 5] = ["objective", "intention", "thought", "action", "observation"];
pub const TEMPLATE_KINDS: [&str; 3] = ["resident", "firmware", "agent"];
pub const ADDRESS: &str = "craft:";
pub const CUT_TOOL: &str = "craft.cut";
pub const CUT_CLASS: &str = "consequential";
pub const KERNEL: &str = "the kernel";

pub fn format_of(kind: &str) -> &'static str {
    match kind {
        "template" => "orreth-resident-template/1",
        "binding" => "orreth-workspace-binding/1",
        "policy" => "orreth-covenant-policy/1",
        "graph" => "orreth-graph/1",
        "golden" => "orreth-golden/1",
        "prompt" => "orreth-prompt/1",
        _ => "orreth-skill/1",
    }
}

pub fn is_craft(kind: &str) -> bool {
    CRAFT_KINDS.contains(&kind)
}

/// `crafts.plain`: a service in the human's words — `greeting prompt` for a craft, `weather tool`
/// for an identity (W100, walk SPEC-SHELF-01).
pub fn plain(name: &str, kind: &str) -> String {
    match split_name(name) {
        Some((bare, k)) if k == kind => format!("{bare} {kind}"),
        _ => format!("{name} {kind}"),
    }
}

fn kinds_words() -> String {
    CRAFT_KINDS.join(", ")
}

/// `crafts.NAME_RX`: `^[a-z0-9][a-z0-9._-]{0,63}$`.
pub fn name_ok(n: &str) -> bool {
    let b = n.as_bytes();
    (1..=64).contains(&b.len())
        && (b[0].is_ascii_lowercase() || b[0].is_ascii_digit())
        && b.iter()
            .all(|c| c.is_ascii_lowercase() || c.is_ascii_digit() || matches!(*c, b'.' | b'_' | b'-'))
}

/// The shelf name a craft wears: `<name>.<kind>`.
pub fn craft_name(name: &str, kind: &str) -> Result<String, String> {
    if !is_craft(kind) {
        return Err(format!(
            "a craft kind is one of {} — not {}",
            kinds_words(),
            repr_str(kind)
        ));
    }
    let n = name.trim();
    if !name_ok(n) || n.ends_with(&format!(".{kind}")) {
        return Err("a craft name is a short lowercase name: letters, digits, dashes, dots, underscores".into());
    }
    Ok(format!("{n}.{kind}"))
}

/// `librarian.template` → ("librarian", "template"); None for a service that is no craft.
pub fn split_name(shelf_name: &str) -> Option<(String, String)> {
    for k in CRAFT_KINDS {
        let suffix = format!(".{k}");
        if shelf_name.ends_with(&suffix) && shelf_name.len() > suffix.len() {
            return Some((shelf_name[..shelf_name.len() - suffix.len()].to_string(), k.to_string()));
        }
    }
    None
}

/// What a craft's `did` column carries — a plain address, never a DID.
pub fn address(name: &str, kind: &str) -> Result<String, String> {
    Ok(format!("{ADDRESS}{}", craft_name(name, kind)?))
}

fn ok() -> Value {
    json!({"ok": true, "reason": null})
}
fn no(reason: String) -> Value {
    json!({"ok": false, "reason": reason})
}
fn s(v: &Value, k: &str) -> String {
    match v.get(k) {
        Some(Value::String(x)) => x.trim().to_string(),
        Some(Value::Null) | None => String::new(),
        Some(other) => crate::py::python_str(other).trim().to_string(),
    }
}
fn repr_of(v: Option<&Value>) -> String {
    match v {
        None | Some(Value::Null) => "None".into(),
        Some(Value::String(x)) => repr_str(x),
        Some(other) => crate::py::python_str(other),
    }
}

/// `crafts.validate`: the declaration reads whole, or the reason why not — one law per kind.
pub fn validate(kind: &str, manifest: &Value) -> Value {
    if !is_craft(kind) {
        return no(format!("a craft kind is one of {} — not {}", kinds_words(), repr_str(kind)));
    }
    let Some(m) = manifest.as_object().filter(|m| !m.is_empty()) else {
        return no(format!("a {kind} is a non-empty object — its declaration"));
    };
    let want = format_of(kind);
    if m.get("format").and_then(Value::as_str) != Some(want) {
        return no(format!(
            "a {kind} declares format {} — got {}",
            repr_str(want),
            repr_of(m.get("format"))
        ));
    }
    match kind {
        "template" => {
            if s(manifest, "name").is_empty() {
                return no("a template names its body (`name`)".into());
            }
            if s(manifest, "graph").is_empty() {
                return no("a template names its graph component (`graph`) — the hull's work node".into());
            }
            let tk = m.get("kind").cloned().unwrap_or(json!("resident"));
            if !tk.as_str().is_some_and(|t| TEMPLATE_KINDS.contains(&t)) {
                return no(format!(
                    "a template's kind is one of {} — got {}",
                    TEMPLATE_KINDS.join(", "),
                    repr_of(Some(&tk))
                ));
            }
            ok()
        }
        "binding" => {
            for k in ["pull", "name"] {
                if s(manifest, k).is_empty() {
                    return no(format!("a binding names its {k}"));
                }
            }
            ok()
        }
        "policy" => {
            if s(manifest, "version").is_empty() {
                return no("a policy wears a version".into());
            }
            let rules_ok = m.get("rules").and_then(Value::as_array).is_some_and(|r| {
                !r.is_empty() && r.iter().all(|x| x.as_str().is_some_and(|t| !t.trim().is_empty()))
            });
            if !rules_ok {
                return no("a policy is its rules — a non-empty list of plain sentences".into());
            }
            ok()
        }
        "golden" => {
            if s(manifest, "template").is_empty() {
                return no("a golden set names the template it proves (`template`)".into());
            }
            let Some(cases) = m.get("cases").and_then(Value::as_array).filter(|c| !c.is_empty()) else {
                return no("a golden set is its cases — a non-empty list of {ask, expect}".into());
            };
            for (i, c) in cases.iter().enumerate() {
                if !c.is_object() || s(c, "ask").is_empty() {
                    return no(format!("case {} asks something (`ask`)", i + 1));
                }
                let exp_ok = c.get("expect").and_then(Value::as_array).is_some_and(|e| {
                    !e.is_empty() && e.iter().all(|x| x.as_str().is_some_and(|t| !t.is_empty()))
                });
                if !exp_ok {
                    return no(format!("case {} expects words (`expect`, a non-empty list)", i + 1));
                }
            }
            ok()
        }
        "prompt" => {
            if s(manifest, "text").is_empty() {
                return no("a prompt is its text (`text`)".into());
            }
            ok()
        }
        "skill" => {
            for k in ["name", "words"] {
                if s(manifest, k).is_empty() {
                    let tail = if k == "words" { " — what it is, in one line" } else { "" };
                    return no(format!("a skill has a {k}{tail}"));
                }
            }
            if s(manifest, "text").is_empty() {
                return no("a skill is its text (`text`) — the words a body follows".into());
            }
            ok()
        }
        _ => validate_graph(manifest),
    }
}

/// The graph declaration v0, branching since Phase 8 sp3 (THE WORKSHOP v0): an entry; nodes
/// with unique ids, a known kind and typed refs (`prompt` · `skill` · `mind` a name; `tools` a
/// list of names); edges that name nodes, each wearing at most one `when` (edge · ask · reply);
/// at most ONE way out of a node without a `when` (the default); forward only — a loop refuses.
/// Law for law with `crafts.validate_graph` (the reference) — the fixture `crafts-v0.json` pins both.
pub fn validate_graph(g: &Value) -> Value {
    if g.get("format").and_then(Value::as_str) != Some(format_of("graph")) {
        return no(format!("a graph declares format {}", repr_str(format_of("graph"))));
    }
    let Some(nodes) = g.get("nodes").and_then(Value::as_array).filter(|n| !n.is_empty()) else {
        return no("a graph has nodes — a non-empty list of {id, kind}".into());
    };
    let mut ids: Vec<String> = Vec::new();
    for (i, n) in nodes.iter().enumerate() {
        if !n.is_object() || s(n, "id").is_empty() {
            return no(format!("node {} has an id", i + 1));
        }
        let id = crate::py::python_str(&n["id"]);
        if ids.contains(&id) {
            return no(format!("node ids are unique — {} appears twice", repr_str(&id)));
        }
        if !n.get("kind").and_then(Value::as_str).is_some_and(|k| NODE_KINDS.contains(&k)) {
            return no(format!(
                "node {}: a node's kind is one of {} — got {}",
                repr_str(&id),
                NODE_KINDS.join(", "),
                repr_of(n.get("kind"))
            ));
        }
        for r in ["prompt", "skill", "mind"] {
            if let Some(v) = n.get(r).filter(|v| !v.is_null()) {
                if !v.as_str().is_some_and(|t| !t.trim().is_empty()) {
                    let what = if r == "mind" { "stall" } else { r };
                    return no(format!("node {}: `{r}` names a {what} by name", repr_str(&id)));
                }
            }
        }
        if let Some(t) = n.get("tools").filter(|v| !v.is_null()) {
            let ok = t.as_array().is_some_and(|a| a.iter().all(|x| x.as_str().is_some_and(|y| !y.trim().is_empty())));
            if !ok {
                return no(format!("node {}: `tools` is a list of tool names", repr_str(&id)));
            }
        }
        ids.push(id);
    }
    let entry = g.get("entry");
    if !entry.and_then(Value::as_str).is_some_and(|e| ids.iter().any(|i| i == e)) {
        return no(format!("a graph names its entry node — {} is not a node", repr_of(entry)));
    }
    let edges = match g.get("edges") {
        None => Vec::new(),
        Some(Value::Array(a)) => a.clone(),
        Some(_) => return no("edges is a list of {from, to}".into()),
    };
    let mut defaults: Vec<String> = Vec::new();
    for e in &edges {
        let (from, to) = (e.get("from").and_then(Value::as_str), e.get("to").and_then(Value::as_str));
        let names = |x: Option<&str>| x.is_some_and(|v| ids.iter().any(|i| i == v));
        if !e.is_object() || !names(from) || !names(to) {
            let (fr, to) = if e.is_object() { (e.get("from"), e.get("to")) } else { (None, None) };
            return no(format!("an edge names two nodes — {} → {} does not", repr_of(fr), repr_of(to)));
        }
        let (from, to) = (from.unwrap_or_default().to_string(), to.unwrap_or_default().to_string());
        let Some(w) = e.get("when").filter(|w| !w.is_null()) else {
            if defaults.contains(&from) {
                return no(format!(
                    "node {} has two ways out and neither says when — one way out may be the default; every other wears a `when` (edge · ask · reply)",
                    repr_str(&from)
                ));
            }
            defaults.push(from);
            continue;
        };
        let Some(wm) = w.as_object().filter(|m| m.len() == 1) else {
            return no(format!("the way out of {} to {}: `when` is one of {{edge}}, {{ask}} or {{reply}}", repr_str(&from), repr_str(&to)));
        };
        let (k, v) = wm.iter().next().unwrap();
        if !WHEN_KEYS.contains(&k.as_str()) {
            return no(format!("the way out of {} to {}: `when` is one of {{edge}}, {{ask}} or {{reply}}", repr_str(&from), repr_str(&to)));
        }
        if k == "edge" && !v.as_str().is_some_and(|x| EDGES.contains(&x)) {
            return no(format!(
                "the way out of {} to {}: `when.edge` is one of {} — got {}",
                repr_str(&from),
                repr_str(&to),
                EDGES.join(", "),
                repr_of(Some(v))
            ));
        }
        if k != "edge" && !v.as_str().is_some_and(|x| !x.trim().is_empty()) {
            return no(format!("the way out of {} to {}: `when.{k}` is a pattern — the words to look for", repr_str(&from), repr_str(&to)));
        }
    }
    if let Some(at) = loops_at(g, &ids) {
        return no(format!("the graph loops at {} — v0 runs forward only", repr_str(&at)));
    }
    ok()
}

/// The first node (in declaration order) that can reach itself along ANY edges — None when
/// the graph runs forward only.
fn loops_at(g: &Value, ids: &[String]) -> Option<String> {
    let edges = g.get("edges").and_then(Value::as_array).cloned().unwrap_or_default();
    let outs = |from: &str| -> Vec<String> {
        edges
            .iter()
            .filter(|e| e.get("from").and_then(Value::as_str) == Some(from))
            .filter_map(|e| e.get("to").and_then(Value::as_str).map(str::to_string))
            .collect()
    };
    for start in ids {
        let mut seen: Vec<String> = Vec::new();
        let mut stack = outs(start);
        while let Some(cur) = stack.pop() {
            if &cur == start {
                return Some(start.clone());
            }
            if seen.contains(&cur) || !ids.contains(&cur) {
                continue;
            }
            seen.push(cur.clone());
            stack.extend(outs(&cur));
        }
    }
    None
}

/// THE DEFAULT LINE: the nodes a run visits from the entry along the edges that wear no `when`
/// (every node's "otherwise"), in order — the spine the canvas draws and the probe says; a loop
/// refuses. A node whose every way out is conditioned ends the line.
pub fn path(g: &Value) -> Result<Vec<String>, String> {
    let edges = g.get("edges").and_then(Value::as_array).cloned().unwrap_or_default();
    let next = |from: &str| -> Option<String> {
        edges
            .iter()
            .find(|e| e.get("from").and_then(Value::as_str) == Some(from) && e.get("when").is_none_or(Value::is_null))
            .and_then(|e| e.get("to").and_then(Value::as_str))
            .map(str::to_string)
    };
    let mut seen: Vec<String> = Vec::new();
    let mut cur = g.get("entry").and_then(Value::as_str).map(str::to_string);
    while let Some(c) = cur {
        if seen.contains(&c) {
            return Err(format!("the graph loops at {} — v0 runs forward only", repr_str(&c)));
        }
        seen.push(c.clone());
        cur = next(&c);
    }
    Ok(seen)
}

/// The nodes with more than one way out, in declaration order.
pub fn branches(g: &Value) -> Vec<String> {
    let edges = g.get("edges").and_then(Value::as_array).cloned().unwrap_or_default();
    g.get("nodes")
        .and_then(Value::as_array)
        .map(|nodes| {
            nodes
                .iter()
                .filter_map(|n| n.get("id").and_then(Value::as_str))
                .filter(|id| edges.iter().filter(|e| e.get("from").and_then(Value::as_str) == Some(id)).count() > 1)
                .map(str::to_string)
                .collect()
        })
        .unwrap_or_default()
}

/// Which of the hull's three edges an ask takes, read off its marker.
pub fn hull_edge(marker_kind: Option<&str>, parent_kind: Option<&str>) -> &'static str {
    // Phase 8 sp4: a THOUGHT under a non-structural parent is an EVENT — an include dispatched by interest
    match parent_kind {
        None | Some("") => "chat",
        Some(k) if STRUCTURAL.contains(&k) => {
            if marker_kind == Some("thought") {
                "chat"
            } else {
                "work"
            }
        }
        Some(_) => "event",
    }
}

/// The journey's line for the route — plain (rule 13).
pub fn edge_words(edge: &str, parent_kind: Option<&str>) -> String {
    match edge {
        "chat" => "routed to the chat edge — a human's ask".into(),
        "work" => "routed to the work edge — assigned work under an intention".into(),
        _ => format!(
            "routed to the event edge — a marker of kind {} asked for a response",
            parent_kind.filter(|k| !k.is_empty()).unwrap_or("unknown")
        ),
    }
}

/// A source's two forms: `{locator}` or a repo'd origin `{repo, commit, entry}` — `{ok, form, reason}`.
pub fn source_form(manifest: &Value) -> Value {
    if !manifest.as_object().is_some_and(|m| !m.is_empty()) {
        return json!({"ok": false, "form": null, "reason": "a source is a non-empty object"});
    }
    if crate::py::truthy(&manifest["locator"]) {
        return json!({"ok": true, "form": "locator", "reason": null});
    }
    let (repo, commit, entry) = (s(manifest, "repo"), s(manifest, "commit").to_lowercase(), s(manifest, "entry"));
    if repo.is_empty() {
        return json!({"ok": false, "form": null,
                      "reason": "a source names a locator by NAME, or a repo with its commit and entry point"});
    }
    let hex_ok = (7..=64).contains(&commit.len()) && commit.chars().all(|c| c.is_ascii_hexdigit() && !c.is_ascii_uppercase());
    if !hex_ok {
        return json!({"ok": false, "form": "repo", "reason": "a repo'd source pins a commit — 7 to 64 hex characters"});
    }
    if entry.is_empty() {
        return json!({"ok": false, "form": "repo",
                      "reason": "a repo'd source names its entry point (`entry`: the module or file the graph is built from)"});
    }
    json!({"ok": true, "form": "repo", "reason": null})
}

/// What a cut demands, by the craft's class (0010 lock 4) — `{ok, level, gate, reason}`; Phase 8 sp4: the
/// gate is `shelf` (the cut lands the version) or `experiment` (an agent's cut OPENS the Experiment, L2).
pub fn cut_demand(kind: &str, manifest: &Value, mode: &str) -> Value {
    if !is_craft(kind) {
        return json!({"ok": false, "level": null, "gate": null,
                      "reason": format!("a craft kind is one of {} — not {}", kinds_words(), repr_str(kind))});
    }
    if kind != "template" {
        return json!({"ok": true, "level": "L2", "gate": "shelf", "reason": null});
    }
    let tk = manifest
        .as_object()
        .and_then(|m| m.get("kind"))
        .and_then(Value::as_str)
        .unwrap_or("resident");
    match tk {
        "firmware" if mode == "prod" => json!({"ok": false, "level": null, "gate": null,
            "reason": "firmware is cut only in a dev universe — it reaches prod as a release"}),
        "firmware" => json!({"ok": true, "level": "L2", "gate": "shelf", "reason": null}),
        "agent" => json!({"ok": true, "level": "L2", "gate": "experiment", "reason": null}),
        _ => json!({"ok": true, "level": "L3-code", "gate": "shelf", "reason": null}),
    }
}

/// The components a body is made of at its join — `[{component, kind, hash}]` in the order
/// worn: template · binding · policy · graph · golden; `parts` names each by `{name, hash}`.
pub fn wear_of(parts: &Value) -> Result<Vec<Value>, String> {
    let mut out = Vec::new();
    for kind in ["template", "binding", "policy", "graph", "golden"] {
        let p = parts.get(kind).filter(|p| crate::py::truthy(p));
        let Some(p) = p else {
            if kind == "template" || kind == "policy" {
                return Err(format!("a body wears a {kind} — none named"));
            }
            continue;
        };
        out.push(json!({"component": craft_name(&s(p, "name"), kind)?, "kind": kind, "hash": s(p, "hash")}));
    }
    Ok(out)
}

/// A golden set as a component (the harness's bare list wrapped in its declaration).
pub fn golden_document(template: &str, cases: &[Value]) -> Value {
    json!({"format": format_of("golden"), "template": template, "cases": cases})
}

/// The held act's words: what the cut lands.
pub fn cut_words(name: &str, kind: &str, verb: &str, version: i64) -> String {
    if verb == "register" {
        format!("cutting the {name} {kind} — version 1 onto the shelf")
    } else {
        format!("cutting the {name} {kind} — version {version} onto the shelf")
    }
}

/// "in use by N", in words.
pub fn worn_words(component: &str, wearers: &[Value]) -> String {
    if wearers.is_empty() {
        return format!("{component} is worn by no body now");
    }
    let names: Vec<String> = wearers
        .iter()
        .map(|w| {
            let v = match w.get("version") {
                Some(Value::Number(n)) => format!(", v{n}"),
                _ => ", off the shelf".to_string(),
            };
            format!("{} (life {}{v})", crate::py::python_str(&w["body"]), crate::py::python_str(&w["life"]))
        })
        .collect();
    let n = wearers.len();
    format!(
        "{component} is worn by {n} bod{}: {}",
        if n == 1 { "y" } else { "ies" },
        names.join(", ")
    )
}

/// The pin a craft's manifest wears — the same content hash as every service.
pub fn pin(manifest: &Value) -> String {
    content_hash(manifest)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn names_edges_and_demands() {
        assert_eq!(craft_name("librarian", "template").unwrap(), "librarian.template");
        assert_eq!(address("mind.v0", "graph").unwrap(), "craft:mind.v0.graph");
        assert_eq!(split_name("mind.v0.graph"), Some(("mind.v0".into(), "graph".into())));
        assert!(craft_name("Librarian", "template").is_err());
        assert_eq!(hull_edge(Some("objective"), Some("watch-red")), "event");
        assert_eq!(hull_edge(Some("objective"), Some("intention")), "work");
        assert_eq!(hull_edge(Some("thought"), Some("objective")), "chat");
        assert_eq!(cut_demand("template", &json!({"kind": "firmware"}), "prod")["ok"], json!(false));
        let g = json!({"format": "orreth-graph/1", "name": "g", "entry": "a",
                       "nodes": [{"id": "a", "kind": "think"}, {"id": "b", "kind": "echo"}],
                       "edges": [{"from": "a", "to": "b"}]});
        assert_eq!(path(&g).unwrap(), vec!["a", "b"]);
        assert_eq!(validate("graph", &g)["ok"], json!(true));
        // Phase 8 sp3: a graph BRANCHES — one default way out, the rest wearing `when`; forward only
        let b = json!({"format": "orreth-graph/1", "name": "b", "entry": "r",
                       "nodes": [{"id": "r", "kind": "think"}, {"id": "c", "kind": "echo"},
                                 {"id": "w", "kind": "think", "tools": ["weather"], "mind": "haiku"}],
                       "edges": [{"from": "r", "to": "c", "when": {"edge": "chat"}}, {"from": "r", "to": "w"}]});
        assert_eq!(validate("graph", &b)["ok"], json!(true));
        assert_eq!(path(&b).unwrap(), vec!["r", "w"]);
        assert_eq!(branches(&b), vec!["r"]);
        let mut two = b.clone();
        two["edges"] = json!([{"from": "r", "to": "c"}, {"from": "r", "to": "w"}]);
        assert_eq!(validate("graph", &two)["reason"],
                   json!("node 'r' has two ways out and neither says when — one way out may be the default; every other wears a `when` (edge · ask · reply)"));
        let mut back = b.clone();
        back["edges"] = json!([{"from": "r", "to": "c", "when": {"edge": "chat"}}, {"from": "c", "to": "r"}]);
        assert_eq!(validate("graph", &back)["reason"], json!("the graph loops at 'r' — v0 runs forward only"));
    }
}
