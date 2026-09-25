// PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp4, the loops · 2026-09-23
// Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp6, the bodies' seam: `server_name` (W28) · 2026-09-24
//! `orreth.mcp/1` — the pure half of `orreth_spine.mcp` (P6.5 sp2, MCP through
//! ONE door): the three JSON-RPC 2.0 requests with FIXED ids (so the bytes on
//! the wire are canonical), the transport a locator names, the pin a tool and
//! a server wear on the shelf (`tool_manifest` · `server_manifest`), the
//! transition words and the dials. Measured by `mcp-v0.json` (five kinds).
//! Spawning a server, the session over stdio or HTTP, and the keeper's beat
//! stay the Python organ's until the bodies' seam (P7 sp6).

use crate::canonical::canonical;
use crate::py::{python_str, truthy};
use regex::Regex;
use serde_json::{json, Value};
use std::sync::LazyLock;

pub const PROTOCOL: &str = "2025-06-18";
pub const CLIENT_NAME: &str = "orreth-spine";
pub const CLIENT_VERSION: &str = "0.1.0";
/// Fixed ids: the request bytes are canonical.
pub const INITIALIZE_ID: i64 = 1;
pub const LIST_ID: i64 = 2;
pub const CALL_ID: i64 = 3;
/// The transition words when a server no longer lists a tool (never retired by the machine).
pub const GONE: &str = "gone from the server's list";
pub const STRIKES_DIAL: &str = "SPINE_TOOL_UNHEALTHY_STRIKES";
pub const STRIKES_DEFAULT: i64 = 3;

// ---- the wire: JSON-RPC 2.0, three methods -------------------------------------------

pub fn request(method: &str, params: Value, id: i64) -> Value {
    json!({"jsonrpc": "2.0", "id": id, "method": method, "params": params})
}

pub fn initialize_request() -> Value {
    request(
        "initialize",
        json!({"protocolVersion": PROTOCOL, "capabilities": {},
               "clientInfo": {"name": CLIENT_NAME, "version": CLIENT_VERSION}}),
        INITIALIZE_ID,
    )
}

pub fn list_request() -> Value {
    request("tools/list", json!({}), LIST_ID)
}

pub fn call_request(tool: &str, arguments: &Value) -> Value {
    let args = if arguments.is_object() {
        arguments.clone()
    } else {
        json!({})
    };
    request(
        "tools/call",
        json!({"name": tool, "arguments": args}),
        CALL_ID,
    )
}

/// What goes on the wire: the canonical bytes (0000 §3).
pub fn request_bytes(req: &Value) -> Vec<u8> {
    canonical(req)
}

static HTTP_RE: LazyLock<Regex> = LazyLock::new(|| Regex::new(r"(?i)^https?://").unwrap());

/// `http` for a URL, `stdio` for a command line.
pub fn transport_of(locator: &str) -> &'static str {
    if HTTP_RE.is_match(locator.trim()) {
        "http"
    } else {
        "stdio"
    }
}

/// `env:NAME` → the value from the environment, at the moment of use only;
/// refused in words when the name is not reachable here.
pub fn resolve_locator(locator: &str) -> Result<String, String> {
    let loc = locator.trim();
    if let Some(name) = loc.strip_prefix("env:") {
        let name = name.trim();
        return match std::env::var(name) {
            Ok(v) if !v.is_empty() => Ok(v),
            _ => Err(format!(
                "the locator is named by {name} and {name} is not reachable here"
            )),
        };
    }
    Ok(loc.to_string())
}

// ---- what the ladder pins ----------------------------------------------------------

static NOT_NAME: LazyLock<Regex> = LazyLock::new(|| Regex::new(r"[^a-z0-9.-]+").unwrap());

/// A tool's name on the shelf: the registry's law (lowercase; letters,
/// digits, dashes, dots) applied to the wire name.
pub fn shelf_name(wire: &str) -> String {
    let n = NOT_NAME
        .replace_all(&wire.trim().to_lowercase(), "-")
        .trim_matches('-')
        .to_string();
    if n.is_empty() {
        "tool".into()
    } else {
        n
    }
}

pub fn consequence_of_annotations(t: &Value) -> &'static str {
    if truthy(&t["annotations"]["destructiveHint"]) {
        "consequential"
    } else {
        "routine"
    }
}

fn str_or_empty(v: &Value) -> String {
    if truthy(v) {
        python_str(v)
    } else {
        String::new()
    }
}

fn schema_or_default(v: &Value) -> Value {
    if truthy(v) {
        v.clone()
    } else {
        json!({"type": "object", "properties": {}})
    }
}

/// The service manifest of an MCP tool (the pin): its shelf name, the wire
/// name, its words, its input schema, its class, its server.
pub fn tool_manifest(server: &str, t: &Value) -> Value {
    let wire = str_or_empty(&t["name"]);
    json!({
        "name": shelf_name(&wire), "tool": wire,
        "description": str_or_empty(&t["description"]),
        "input_schema": schema_or_default(&t["inputSchema"]),
        "consequence": consequence_of_annotations(t), "server": server,
    })
}

/// The server's manifest: its transport, its locator BY NAME, and the list it
/// offers (name + schema + class) — sorted, so the pin reads the list and
/// nothing else; a changed list is a changed pin.
pub fn server_manifest(locator: &str, tools: &[Value]) -> Result<Value, String> {
    let mut listed: Vec<(String, Value)> = tools
        .iter()
        .map(|t| {
            let name = str_or_empty(&t["name"]);
            (
                name.clone(),
                json!({"name": name, "input_schema": schema_or_default(&t["inputSchema"]),
                       "consequence": consequence_of_annotations(t)}),
            )
        })
        .collect();
    listed.sort_by(|a, b| a.0.cmp(&b.0));
    Ok(json!({
        "transport": transport_of(&resolve_locator(locator)?), "locator": locator,
        "tools": listed.into_iter().map(|(_, v)| v).collect::<Vec<_>>(),
    }))
}

/// W28 (P6.5 sp3, ported P7 sp6): the shelf name a server gives itself — the
/// last word of its initialize name (`orreth-clock` → `clock`), lowercased;
/// else the last word of its locator that is not a `.py`; else `server`.
pub fn server_name(info: &Value, locator: &str) -> String {
    let split = |text: &str| -> Vec<String> {
        text.to_lowercase()
            .split(|c: char| !c.is_ascii_lowercase() && !c.is_ascii_digit())
            .filter(|w| !w.is_empty())
            .map(str::to_string)
            .collect()
    };
    let raw = info
        .get("name")
        .and_then(Value::as_str)
        .unwrap_or("")
        .trim()
        .to_string();
    let mut words = split(&raw);
    if words.is_empty() {
        words = split(locator)
            .into_iter()
            .filter(|w| !w.ends_with("py"))
            .collect();
    }
    let name = words.last().cloned().unwrap_or_else(|| "server".into());
    name.chars().take(40).collect()
}

/// The strikes dial: `SPINE_TOOL_UNHEALTHY_STRIKES`, at least 1, default 3.
pub fn strikes_n() -> i64 {
    std::env::var(STRIKES_DIAL)
        .ok()
        .filter(|s| !s.is_empty())
        .and_then(|s| s.parse::<i64>().ok())
        .map(|n| n.max(1))
        .unwrap_or(STRIKES_DEFAULT)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn the_wire_and_the_pins() {
        assert_eq!(
            String::from_utf8(request_bytes(&list_request())).unwrap(),
            r#"{"id":2,"jsonrpc":"2.0","method":"tools/list","params":{}}"#
        );
        assert_eq!(transport_of("HTTPS://h/mcp"), "http");
        assert_eq!(transport_of("/usr/bin/server --flag"), "stdio");
        assert_eq!(shelf_name("Wipe_All"), "wipe-all");
        assert_eq!(shelf_name("---"), "tool");
        let m = tool_manifest("clock", &json!({"name": "echo"}));
        assert_eq!(
            m["input_schema"],
            json!({"type": "object", "properties": {}})
        );
        assert_eq!(m["consequence"], json!("routine"));
        let s =
            server_manifest("python x.py", &[json!({"name": "b"}), json!({"name": "a"})]).unwrap();
        assert_eq!(s["tools"][0]["name"], json!("a"));
        assert!(resolve_locator("env:ORRETH_NO_SUCH_NAME_X").is_err());
    }
}
