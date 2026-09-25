// PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp6, the bodies' seam · 2026-09-24
//! MCP through ONE door, from the kernel's side — the live half of
//! `orreth_spine.mcp` (P6.5 sp2): the Model Context Protocol client by hand,
//! JSON-RPC 2.0 over **stdio** (a server command the kernel spawns; its
//! environment PATH and its kin plus the NAMED secrets, nothing else) and
//! **streamable HTTP** (a URL; SSE unwrapped) — `initialize` · `tools/list`
//! and nothing more here (the call rides the body's tool door). A session is
//! opened per act and closed after it. A server is a service of kind mcp; its
//! listed tools are services of kind tool under it: a changed list VERSIONS
//! the server, a new tool REGISTERS, a vanished one goes UNHEALTHY with the
//! words GONE — never retired by the machine (rule 11); after N unhealthy
//! checks in a row a keeper PROPOSES, one hold at the interlock, and the human
//! cuts. The requests' bytes, the pins and the words are [`crate::mcp`]'s.

use crate::ground::Ground;
use crate::harness::strikes;
use crate::mcp::{
    self, initialize_request, list_request, request_bytes, resolve_locator, server_manifest,
    strikes_n, tool_manifest, transport_of, GONE,
};
use crate::py::{python_str, truthy};
use crate::services_live::{self, FactWhere, KERNEL, RETIRE_CLASS, RETIRE_LEVEL, RETIRE_TOOL};
use crate::world::{isoformat, refused, RoadError, World};
use serde_json::{json, Value};
use std::process::Stdio;
use std::time::{Duration, SystemTime};
use tokio::io::{AsyncBufReadExt, AsyncWriteExt, BufReader};

pub const PASS_ENV: [&str; 8] = [
    "PATH",
    "HOME",
    "LANG",
    "LC_ALL",
    "TMPDIR",
    "PYTHONPATH",
    "PYTHONIOENCODING",
    "SYSTEMROOT",
];
pub const TIMEOUT: Duration = Duration::from_secs(15);
pub const INITIALIZED: &str = r#"{"jsonrpc":"2.0","method":"notifications/initialized"}"#;

/// The server did not answer — the reason in words (never a value).
#[derive(Debug, Clone)]
pub struct Unreachable(pub String);

impl std::fmt::Display for Unreachable {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        f.write_str(&self.0)
    }
}

/// The child's environment: PATH and its kin, then the NAMED secrets — nothing else leaks down.
pub fn spawn_env(secrets_with: &[String]) -> Vec<(String, String)> {
    let mut env: Vec<(String, String)> = PASS_ENV
        .iter()
        .filter_map(|k| {
            std::env::var(k)
                .ok()
                .filter(|v| !v.is_empty())
                .map(|v| (k.to_string(), v))
        })
        .collect();
    for name in secrets_with {
        if let Ok(v) = std::env::var(name) {
            if !v.is_empty() {
                env.push((name.clone(), v));
            }
        }
    }
    env
}

/// The locator as the shelf says it: by NAME — never a resolved value.
pub fn locator_words(locator: &str) -> String {
    let loc = locator.trim();
    match loc.strip_prefix("env:") {
        Some(n) => format!("the locator named by {}", n.trim()),
        None => loc.to_string(),
    }
}

/// initialize + tools/list in one short session: (server info, the tools).
pub async fn listing_of(
    locator: &str,
    secrets_with: &[String],
) -> Result<(Value, Vec<Value>), Unreachable> {
    let resolved = resolve_locator(locator).map_err(Unreachable)?;
    if transport_of(&resolved) == "http" {
        return listing_http(&resolved, secrets_with).await;
    }
    listing_stdio(&resolved, secrets_with).await
}

fn info_of(res: &Value) -> Value {
    let si = &res["serverInfo"];
    json!({"name": si["name"], "version": si["version"], "protocol": res["protocolVersion"]})
}

type OutLines = tokio::io::Lines<BufReader<tokio::process::ChildStdout>>;

/// One JSON-RPC exchange over stdio: the request's canonical bytes and a
/// newline down; the line whose id answers, up (a stray line is not the answer).
async fn rpc_stdio(
    stdin: &mut tokio::process::ChildStdin,
    lines: &mut OutLines,
    req: Value,
    notify: bool,
) -> Result<Value, Unreachable> {
    let mut raw = request_bytes(&req);
    raw.push(b'\n');
    stdin
        .write_all(&raw)
        .await
        .map_err(|_| Unreachable("the server closed its stdin".into()))?;
    stdin.flush().await.ok();
    if notify {
        return Ok(Value::Null);
    }
    let want = req["id"].clone();
    let method = python_str(&req["method"]);
    loop {
        let line = tokio::time::timeout(TIMEOUT, lines.next_line())
            .await
            .map_err(|_| {
                Unreachable(format!(
                    "no answer to {method} within {}s",
                    TIMEOUT.as_secs()
                ))
            })?
            .map_err(|e| Unreachable(e.to_string()))?
            .ok_or_else(|| {
                Unreachable(format!(
                    "the server closed its stdout before answering {method}"
                ))
            })?;
        let Ok(got) = serde_json::from_str::<Value>(&line) else {
            continue;
        };
        if got["id"] == want {
            if let Some(err) = got.get("error").filter(|e| truthy(e)) {
                return Err(Unreachable(format!(
                    "{method} refused: {}",
                    err["message"].as_str().unwrap_or("no words")
                )));
            }
            return Ok(got.get("result").cloned().unwrap_or(json!({})));
        }
    }
}

async fn listing_stdio(
    command: &str,
    secrets_with: &[String],
) -> Result<(Value, Vec<Value>), Unreachable> {
    let parts = shell_words(command);
    let Some((prog, args)) = parts.split_first() else {
        return Err(Unreachable("the locator names no command".into()));
    };
    let mut child = tokio::process::Command::new(prog)
        .args(args)
        .env_clear()
        .envs(spawn_env(secrets_with))
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::null())
        .kill_on_drop(true)
        .spawn()
        .map_err(|e| Unreachable(format!("the command could not be spawned: {e}")))?;
    let mut stdin = child
        .stdin
        .take()
        .ok_or_else(|| Unreachable("no stdin".into()))?;
    let mut lines = BufReader::new(
        child
            .stdout
            .take()
            .ok_or_else(|| Unreachable("no stdout".into()))?,
    )
    .lines();
    let init = rpc_stdio(&mut stdin, &mut lines, initialize_request(), false).await?;
    let _ = rpc_stdio(
        &mut stdin,
        &mut lines,
        serde_json::from_str(INITIALIZED).unwrap(),
        true,
    )
    .await;
    let listed = rpc_stdio(&mut stdin, &mut lines, list_request(), false).await?;
    drop(stdin);
    let _ = tokio::time::timeout(Duration::from_secs(2), child.wait()).await;
    let tools = listed["tools"].as_array().cloned().unwrap_or_default();
    Ok((info_of(&init), tools))
}

async fn listing_http(
    url: &str,
    secrets_with: &[String],
) -> Result<(Value, Vec<Value>), Unreachable> {
    let bearer = secrets_with
        .iter()
        .find_map(|n| std::env::var(n).ok().filter(|v| !v.is_empty()));
    let url = url.to_string();
    let post = |msg: Value, session: Option<String>, bearer: Option<String>, url: String| async move {
        tokio::task::spawn_blocking(
            move || -> Result<(Option<String>, String, String), Unreachable> {
                let agent = ureq::AgentBuilder::new().timeout(TIMEOUT).build();
                let mut req = agent
                    .post(&url)
                    .set("content-type", "application/json")
                    .set("accept", "application/json, text/event-stream")
                    .set("mcp-protocol-version", mcp::PROTOCOL);
                if let Some(s) = &session {
                    req = req.set("mcp-session-id", s);
                }
                if let Some(b) = &bearer {
                    req = req.set("authorization", &format!("Bearer {b}"));
                }
                let method = python_str(&msg["method"]);
                match req.send_string(&msg.to_string()) {
                    Ok(r) => {
                        let sid = r.header("mcp-session-id").map(str::to_string);
                        let ctype = r.header("content-type").unwrap_or("").to_lowercase();
                        let body = r.into_string().unwrap_or_default();
                        Ok((sid, ctype, body))
                    }
                    Err(ureq::Error::Status(code, _)) => Err(Unreachable(format!(
                        "the server answered HTTP {code} to {method}"
                    ))),
                    Err(ureq::Error::Transport(_)) => Err(Unreachable(
                        "the server could not be reached: URLError".into(),
                    )),
                }
            },
        )
        .await
        .map_err(|e| Unreachable(e.to_string()))?
    };
    let answer = |body: String, ctype: String, msg: &Value| -> Result<Value, Unreachable> {
        let method = python_str(&msg["method"]);
        let got: Value = if ctype.contains("text/event-stream") {
            let mut found = None;
            for chunk in body.split("\n\n") {
                let data: String = chunk
                    .lines()
                    .filter_map(|l| l.strip_prefix("data:"))
                    .map(str::trim)
                    .collect();
                if data.is_empty() {
                    continue;
                }
                if let Ok(v) = serde_json::from_str::<Value>(&data) {
                    if v["id"] == msg["id"] {
                        found = Some(v);
                        break;
                    }
                }
            }
            found.ok_or_else(|| {
                Unreachable(format!("the event stream carried no answer to {method}"))
            })?
        } else {
            serde_json::from_str(&body)
                .map_err(|_| Unreachable(format!("the answer to {method} was not JSON")))?
        };
        if let Some(err) = got.get("error").filter(|e| truthy(e)) {
            return Err(Unreachable(format!(
                "{method} refused: {}",
                err["message"].as_str().unwrap_or("no words")
            )));
        }
        Ok(got.get("result").cloned().unwrap_or(json!({})))
    };
    let init_req = initialize_request();
    let (sid, ctype, body) = post(init_req.clone(), None, bearer.clone(), url.clone()).await?;
    let init = answer(body, ctype, &init_req)?;
    let _ = post(
        serde_json::from_str(INITIALIZED).unwrap(),
        sid.clone(),
        bearer.clone(),
        url.clone(),
    )
    .await;
    let list_req = list_request();
    let (_, ctype, body) = post(list_req.clone(), sid, bearer, url).await?;
    let listed = answer(body, ctype, &list_req)?;
    Ok((
        info_of(&init),
        listed["tools"].as_array().cloned().unwrap_or_default(),
    ))
}

/// `shlex.split` for the plain case: whitespace, with single and double quotes.
pub fn shell_words(s: &str) -> Vec<String> {
    let mut out = Vec::new();
    let mut cur = String::new();
    let mut quote: Option<char> = None;
    let mut had = false;
    for c in s.chars() {
        match quote {
            Some(q) if c == q => quote = None,
            Some(_) => cur.push(c),
            None if c == '\'' || c == '"' => {
                quote = Some(c);
                had = true;
            }
            None if c.is_whitespace() => {
                if had || !cur.is_empty() {
                    out.push(std::mem::take(&mut cur));
                    had = false;
                }
            }
            None => cur.push(c),
        }
    }
    if had || !cur.is_empty() {
        out.push(cur);
    }
    out
}

/// `mcp.listing_words`.
pub fn listing_words(info: &Value, n: usize, synced: &Value) -> String {
    let mut words = format!(
        "initialize answered ({} {}, protocol {}); {n} tool{} listed",
        info["name"]
            .as_str()
            .filter(|s| !s.is_empty())
            .unwrap_or("unnamed"),
        info["version"]
            .as_str()
            .filter(|s| !s.is_empty())
            .unwrap_or("?"),
        info["protocol"]
            .as_str()
            .filter(|s| !s.is_empty())
            .unwrap_or("?"),
        if n != 1 { "s" } else { "" }
    );
    for k in ["new", "versioned", "gone", "refused"] {
        if let Some(a) = synced[k].as_array().filter(|a| !a.is_empty()) {
            let names: Vec<String> = a.iter().map(python_str).collect();
            words.push_str(&format!("; {k}: {}", names.join(", ")));
        }
    }
    words
}

/// The tools placed under a server (their manifest names it).
pub async fn tools_of(
    g: &Ground,
    scope: &str,
    server: &str,
    standing_only: bool,
) -> Result<Vec<Value>, RoadError> {
    Ok(services_live::rows(g.client(), scope, Some("tool"))
        .await?
        .into_iter()
        .filter(|s| s["manifest"]["server"].as_str() == Some(server))
        .filter(|s| !standing_only || s["state"] != json!("retired"))
        .collect())
}

/// `mcp.sync_tools`: the listing onto the shelf — a NEW tool registers, a
/// changed schema VERSIONS it, a present one is healthy, a tool the server
/// no longer lists is UNHEALTHY with the words GONE; a retired one is left at rest.
pub async fn sync_tools(
    g: &mut Ground,
    w: &World,
    server: &str,
    listed: &[Value],
    by: &str,
) -> Result<Value, RoadError> {
    let mut out = json!({"new": [], "versioned": [], "present": [], "gone": [], "refused": []});
    let mut seen = Vec::new();
    let push = |out: &mut Value, k: &str, v: String| out[k].as_array_mut().unwrap().push(json!(v));
    for t in listed {
        let m = tool_manifest(server, t);
        let name = python_str(&m["name"]);
        seen.push(name.clone());
        let row = services_live::get(g.client(), &w.scope, &name).await?;
        let step: Result<&str, RoadError> = match &row {
            None => services_live::register(
                g,
                w,
                &name,
                "tool",
                &m,
                by,
                Some(&json!({"affinity": [server]})),
                &[],
            )
            .await
            .map(|_| "new"),
            Some(r)
                if r["kind"] != json!("tool")
                    || r["manifest"]["server"].as_str() != Some(server) =>
            {
                let srv = r["manifest"]["server"].as_str();
                push(
                    &mut out,
                    "refused",
                    format!(
                        "{name}: the name is worn by a {}{}",
                        python_str(&r["kind"]),
                        srv.map(|s| format!(" under {s}"))
                            .unwrap_or_else(|| " of the kernel's own".into())
                    ),
                );
                continue;
            }
            Some(r) if r["state"] == json!("retired") => {
                push(
                    &mut out,
                    "refused",
                    format!("{name}: retired by the human — left at rest (restore brings it back)"),
                );
                continue;
            }
            Some(r)
                if r["manifest_hash"].as_str() != Some(crate::hash::content_hash(&m).as_str()) =>
            {
                services_live::version(g, w, &name, &m, by)
                    .await
                    .map(|_| "versioned")
            }
            Some(_) => Ok("present"),
        };
        match step {
            Ok(k) => push(&mut out, k, name.clone()),
            Err(RoadError::Refused(words)) => {
                push(&mut out, "refused", format!("{name}: {words}"));
                continue;
            }
            Err(e) => return Err(e),
        }
        services_live::record_health(
            g,
            w,
            &name,
            Some(true),
            "listed by its server; the schema matches the pin",
            by,
        )
        .await?;
    }
    for s in tools_of(g, &w.scope, server, true).await? {
        let name = python_str(&s["name"]);
        if !seen.contains(&name) {
            services_live::record_health(g, w, &name, Some(false), GONE, by).await?;
            push(&mut out, "gone", name);
        }
    }
    Ok(out)
}

/// `mcp.register_server`: the named secrets reachable FIRST, the server
/// answering initialize and list, then the server on the ladder with its
/// list as the pin and every listed tool under it.
pub async fn register_server(
    g: &mut Ground,
    w: &World,
    name: &str,
    locator: &str,
    by: &str,
    secrets_with: &[String],
    placement: Option<&Value>,
) -> Result<Value, RoadError> {
    let mut name = name.trim().to_lowercase();
    let mut raw = placement.cloned().unwrap_or(json!({}));
    if !raw.is_object() {
        raw = json!({});
    }
    let mut names: Vec<String> = raw["secrets_with"]
        .as_array()
        .map(|a| a.iter().map(python_str).collect())
        .unwrap_or_default();
    names.extend(secrets_with.iter().cloned());
    if let Some(n) = locator.trim().strip_prefix("env:") {
        names.push(n.trim().to_string());
    }
    names.sort();
    names.dedup();
    raw["secrets_with"] = json!(names);
    let prof = crate::placement::profile(&json!({"placement": raw}))
        .map_err(|e| refused(e.to_string()))?;
    let (ok, reasons) = crate::placement::honor(&prof, &crate::sessions::ground_declares());
    if !ok {
        return Err(refused(format!(
            "{name} is refused here: {}",
            reasons.join("; ")
        )));
    }
    let (info, listed) = listing_of(locator, &prof.secrets_with).await.map_err(|e| {
        refused(format!(
            "the server at {} did not answer: {e}",
            locator_words(locator)
        ))
    })?;
    if name.is_empty() {
        name = mcp::server_name(&info, locator); // W28: a server names itself
    }
    let manifest = server_manifest(locator, &listed).map_err(refused)?;
    let row = services_live::get(g.client(), &w.scope, &name).await?;
    let server = match row {
        Some(r)
            if r["kind"] == json!("mcp")
                && r["state"] != json!("retired")
                && r["manifest_hash"].as_str()
                    != Some(crate::hash::content_hash(&manifest).as_str()) =>
        {
            services_live::version(g, w, &name, &manifest, by).await?
        }
        _ => services_live::register(g, w, &name, "mcp", &manifest, by, Some(&raw), &[]).await?,
    };
    let synced = sync_tools(g, w, &name, &listed, by).await?;
    services_live::record_health(
        g,
        w,
        &name,
        Some(true),
        &listing_words(&info, listed.len(), &synced),
        by,
    )
    .await?;
    let _ = server;
    Ok(
        json!({"server": services_live::get(g.client(), &w.scope, &name).await?, "tools": synced, "info": info}),
    )
}

/// `mcp.probe`: the mcp kind's honest probe — initialize + tools/list; a
/// changed list VERSIONS the server; the listing synced; a silent server is
/// unhealthy with the reason.
pub async fn probe(g: &mut Ground, w: &World, row: &Value, by: &str) -> (Option<bool>, String) {
    let m = &row["manifest"];
    let locator = python_str(&m["locator"]);
    if locator.is_empty() {
        return (Some(false), "the manifest names no locator".into());
    }
    let secrets: Vec<String> = row["secrets_with"]
        .as_array()
        .map(|a| a.iter().map(python_str).collect())
        .unwrap_or_default();
    let (info, listed) = match listing_of(&locator, &secrets).await {
        Ok(x) => x,
        Err(e) => return (Some(false), format!("did not answer: {e}")),
    };
    let name = python_str(&row["name"]);
    if let Ok(manifest) = server_manifest(&locator, &listed) {
        if row["manifest_hash"].as_str() != Some(crate::hash::content_hash(&manifest).as_str())
            && row["state"] != json!("retired")
        {
            if let Err(e) = services_live::version(g, w, &name, &manifest, by).await {
                return (
                    Some(false),
                    format!("the list changed but could not be re-pinned: {e}"),
                );
            }
        }
    }
    match sync_tools(g, w, &name, &listed, by).await {
        Ok(synced) => (Some(true), listing_words(&info, listed.len(), &synced)),
        Err(e) => (Some(false), format!("the listing could not be synced: {e}")),
    }
}

/// `mcp.probe_tool`: an MCP-born tool's probe — its server lists it, or it is GONE.
pub async fn probe_tool(g: &mut Ground, w: &World, row: &Value) -> (Option<bool>, String) {
    let m = &row["manifest"];
    let server_name = python_str(&m["server"]);
    let server = match services_live::get(g.client(), &w.scope, &server_name).await {
        Ok(Some(s)) => s,
        Ok(None) => {
            return (
                Some(false),
                format!(
                    "its server {} is not on the shelf",
                    crate::py::repr_str(&server_name)
                ),
            )
        }
        Err(e) => return (Some(false), e.to_string()),
    };
    if server["state"] == json!("retired") {
        return (Some(false), format!("its server {server_name} is retired"));
    }
    let secrets: Vec<String> = server["secrets_with"]
        .as_array()
        .map(|a| a.iter().map(python_str).collect())
        .unwrap_or_default();
    let listed = match listing_of(&python_str(&server["manifest"]["locator"]), &secrets).await {
        Ok((_, l)) => l,
        Err(e) => {
            return (
                Some(false),
                format!("its server {server_name} did not answer: {e}"),
            )
        }
    };
    for t in &listed {
        if t["name"].as_str() == m["tool"].as_str() {
            let fresh = tool_manifest(&server_name, t);
            if row["manifest_hash"].as_str() != Some(crate::hash::content_hash(&fresh).as_str()) {
                if let Err(e) =
                    services_live::version(g, w, &python_str(&row["name"]), &fresh, KERNEL).await
                {
                    return (
                        Some(false),
                        format!("the schema moved but could not be re-pinned: {e}"),
                    );
                }
                return (
                    Some(true),
                    "listed by its server; the schema moved and was re-pinned (versioned)".into(),
                );
            }
            return (
                Some(true),
                "listed by its server; the schema matches the pin".into(),
            );
        }
    }
    (Some(false), GONE.into())
}

/// The keeper's newest proposal to retire this service (any status).
pub async fn last_proposal(
    g: &Ground,
    scope: &str,
    name: &str,
) -> Result<Option<(String, String, SystemTime)>, RoadError> {
    Ok(g
        .client()
        .query_opt(
            "SELECT ask_id, status, asked_at FROM spine_asks WHERE scope = $1 AND served_by = $2 AND held IS NOT \
             NULL AND held::json->>'tool' = $3 AND held::json->'args'->>'name' = $4 ORDER BY asked_at DESC LIMIT 1",
            &[&scope, &KERNEL, &RETIRE_TOOL, &name],
        )
        .await?
        .map(|r| (r.get(0), r.get(1), r.get(2))))
}

/// `mcp.propose_retire`: the keeper's proposal — a hold under ITS OWN DID.
pub async fn propose_retire(
    g: &mut Ground,
    w: &World,
    name: &str,
    keeper: &str,
    n: i64,
    who: &str,
) -> Result<String, RoadError> {
    let row = services_live::get(g.client(), &w.scope, name).await?;
    let Some(row) = row else {
        return Err(refused(format!(
            "no service named {} is registered here",
            crate::py::repr_str(name)
        )));
    };
    let step = crate::services::ladder_step(row["state"].as_str(), "retire");
    if !step.ok {
        return Err(refused(format!(
            "the {name} service is {}",
            step.reason.unwrap_or_default()
        )));
    }
    let why = row["last_health"]["detail"]
        .as_str()
        .filter(|d| !d.is_empty())
        .unwrap_or("no answer")
        .to_string();
    crate::proof_live::hold_kernel_act(
        g,
        w,
        &format!(
            "{who} proposes retiring the {name} {} — unhealthy across {n} check{} in a row ({why})",
            python_str(&row["kind"]),
            if n != 1 { "s" } else { "" }
        ),
        keeper,
        RETIRE_TOOL,
        json!({"name": name}),
        RETIRE_LEVEL,
        None,
        RETIRE_CLASS,
        false,
    )
    .await
}

/// `mcp.proposals`: every standing service unhealthy across N checks in a
/// row earns ONE proposal (none while one waits). Each keeper proposes for
/// ITS kinds — the toolkeeper for everything but minds, the stablekeeper for minds.
pub async fn proposals(
    g: &mut Ground,
    w: &World,
    keeper: &str,
    kinds: Option<&[&str]>,
    who: &str,
) -> Result<Vec<Value>, RoadError> {
    let n = strikes_n();
    let mut out = Vec::new();
    for s in services_live::rows(g.client(), &w.scope, None).await? {
        if s["state"] == json!("retired") {
            continue;
        }
        let kind = python_str(&s["kind"]);
        match kinds {
            Some(ks) if !ks.contains(&kind.as_str()) => continue,
            None if kind == "mind" => continue,
            _ => {}
        }
        let name = python_str(&s["name"]);
        let k = strikes(g, &w.scope, &name).await?;
        if k < n {
            continue;
        }
        if matches!(last_proposal(g, &w.scope, &name).await?, Some((_, st, _)) if st == "awaiting-confirm")
        {
            continue;
        }
        let held = propose_retire(g, w, &name, keeper, k, who).await?;
        out.push(json!({"name": name, "kind": kind, "strikes": k, "held": held}));
    }
    Ok(out)
}

/// `mcp.keeper_beat`: every standing MCP server probed, then the strikes rule.
pub async fn keeper_beat(g: &mut Ground, w: &World, keeper: &str) -> Result<Value, RoadError> {
    let checked = services_live::check_all(g, w, None, Some("mcp"), keeper).await?;
    let proposed = proposals(g, w, keeper, None, "the toolkeeper").await?;
    Ok(json!({"checked": checked, "proposed": proposed}))
}

/// The tools keeper's cadence (`SPINE_TOOL_CHECK_S`, default 300 s, at least 5).
pub fn tool_check_s() -> f64 {
    std::env::var("SPINE_TOOL_CHECK_S")
        .ok()
        .and_then(|v| v.trim().parse::<f64>().ok())
        .unwrap_or(300.0)
        .max(5.0)
}

/// A health row's time, for the doors that say "as of".
pub fn at_words(t: SystemTime) -> String {
    isoformat(t)
}

/// `FactWhere` re-exported for the keepers that settle.
pub fn nowhere<'a>() -> FactWhere<'a> {
    FactWhere::default()
}
