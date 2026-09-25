// PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp6, the bodies' seam · 2026-09-24
//! THE GATEWAY's doors from the kernel's side — `orreth_spine.stable.Gateway`
//! (the LiteLLM management API under the master key: models · keys · spend)
//! and the one chat door for the CANARY (`services._probe`, kind mind: a
//! one-token ping under the keeper's DID, pinned to THIS stall, through the
//! meter — the honest verdict). The plane never sees a prompt (rule 5): the
//! only words this module sends are "Answer with one word." / "ping". Every
//! miss is words (`GatewayDark`), never a stack. HTTP is blocking (`ureq`)
//! and runs on tokio's blocking pool.

use crate::ground::Ground;
use crate::stable::{budget_duration, usd as usd_of};
use crate::world::RoadError;
use serde_json::{json, Value};
use std::time::Duration;

pub const GATEWAY_DIAL: &str = "SPINE_GATEWAY";
pub const GATEWAY_DEFAULT: &str = "http://127.0.0.1:4604";
pub const GATEWAY_KEY_DIAL: &str = "SPINE_GATEWAY_KEY";
pub const GATEWAY_KEY_DEFAULT: &str = "sk-orreth-dev";
pub const TIMEOUT_S: u64 = 60;

/// The gateway did not answer — said in words.
#[derive(Debug, Clone)]
pub struct GatewayDark(pub String);

impl std::fmt::Display for GatewayDark {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        f.write_str(&self.0)
    }
}

impl From<GatewayDark> for RoadError {
    fn from(e: GatewayDark) -> Self {
        RoadError::Refused(e.0)
    }
}

/// A management door's answer: status · body · headers (lowercased names).
pub type Answer = (u16, Value, Vec<(String, String)>);

#[derive(Debug, Clone)]
pub struct Gateway {
    pub base: String,
    key: String,
}

fn words_of(body: &Value) -> String {
    match body.get("error") {
        Some(Value::Object(e)) => e
            .get("message")
            .map(crate::py::python_str)
            .unwrap_or_else(|| Value::Object(e.clone()).to_string()),
        Some(other) => crate::py::python_str(other),
        None => crate::py::python_str(body).chars().take(300).collect(),
    }
}

impl Gateway {
    /// `SPINE_GATEWAY` (http://127.0.0.1:4604) · `SPINE_GATEWAY_KEY` (sk-orreth-dev).
    pub fn from_env() -> Gateway {
        let dial = |n: &str, d: &str| {
            std::env::var(n)
                .ok()
                .filter(|v| !v.is_empty())
                .unwrap_or_else(|| d.into())
        };
        Gateway {
            base: dial(GATEWAY_DIAL, GATEWAY_DEFAULT)
                .trim_end_matches('/')
                .to_string(),
            key: dial(GATEWAY_KEY_DIAL, GATEWAY_KEY_DEFAULT),
        }
    }

    /// One call to a management door (blocking): status · body · headers.
    fn call_sync(
        &self,
        method: &str,
        path: &str,
        body: Option<Value>,
        key: Option<&str>,
        timeout: Duration,
    ) -> Result<Answer, GatewayDark> {
        let url = format!("{}{}", self.base, path);
        let agent = ureq::AgentBuilder::new().timeout(timeout).build();
        let req = agent
            .request(method, &url)
            .set(
                "Authorization",
                &format!("Bearer {}", key.unwrap_or(&self.key)),
            )
            .set("content-type", "application/json");
        let res = match body {
            Some(b) => req.send_string(&b.to_string()),
            None => req.call(),
        };
        let resp = match res {
            Ok(r) => r,
            Err(ureq::Error::Status(_, r)) => r,
            Err(ureq::Error::Transport(t)) => {
                return Err(GatewayDark(format!(
                    "the gateway at {} did not answer: {}",
                    self.base,
                    t.message().unwrap_or("no route")
                )))
            }
        };
        let status = resp.status();
        let headers: Vec<(String, String)> = resp
            .headers_names()
            .into_iter()
            .filter_map(|n| resp.header(&n).map(|v| (n.to_lowercase(), v.to_string())))
            .collect();
        let text = resp.into_string().unwrap_or_default();
        let body = if text.is_empty() {
            json!({})
        } else {
            serde_json::from_str(&text).unwrap_or_else(
                |_| json!({"error": {"message": text.chars().take(300).collect::<String>()}}),
            )
        };
        Ok((status, body, headers))
    }

    async fn call(
        &self,
        method: &str,
        path: &str,
        body: Option<Value>,
        key: Option<String>,
        timeout: Duration,
    ) -> Result<Answer, GatewayDark> {
        let me = self.clone();
        let (method, path) = (method.to_string(), path.to_string());
        tokio::task::spawn_blocking(move || {
            me.call_sync(&method, &path, body, key.as_deref(), timeout)
        })
        .await
        .map_err(|e| GatewayDark(format!("the gateway call was lost: {e}")))?
    }

    /// Does the box answer at all?
    pub async fn ready(&self) -> bool {
        matches!(
            self.call(
                "GET",
                "/health/readiness",
                None,
                None,
                Duration::from_secs(5)
            )
            .await,
            Ok((200, _, _))
        )
    }

    /// Every model entry the gateway holds, by its id (the stall's name).
    pub async fn models(&self) -> Result<serde_json::Map<String, Value>, GatewayDark> {
        let (st, body, _) = self
            .call(
                "GET",
                "/model/info",
                None,
                None,
                Duration::from_secs(TIMEOUT_S),
            )
            .await?;
        if st != 200 {
            return Err(GatewayDark(format!(
                "the gateway's model list refused: {}",
                words_of(&body)
            )));
        }
        let mut out = serde_json::Map::new();
        for m in body["data"].as_array().cloned().unwrap_or_default() {
            let id = m["model_info"]["id"]
                .as_str()
                .or_else(|| m["model_name"].as_str())
                .unwrap_or_default()
                .to_string();
            out.insert(id, m);
        }
        Ok(out)
    }

    /// The stall's model entry — idempotent by id; the key by env NAME; the
    /// base model and the pin's price on the entry (a streamed answer is
    /// priced by the entry, proven live 2026-09-24). `Ok(present)`.
    pub async fn add_stall(&self, name: &str, d: &Value) -> Result<bool, GatewayDark> {
        let have = self.models().await?;
        let present = have.contains_key(name);
        if let Some(h) = have.get(name) {
            if h["model_info"]["base_model"] == d["route"] {
                return Ok(true);
            }
            self.drop_stall(name).await?;
        }
        let mut params = json!({"model": d["route"]});
        if let Some(k) = d["key"].as_str().filter(|k| !k.is_empty()) {
            params["api_key"] = json!(format!("os.environ/{k}"));
        }
        if let Some(b) = d["base"].as_str().filter(|b| !b.is_empty()) {
            params["api_base"] = json!(b);
        }
        let pin = d["price"]["in_per_m"].as_f64().unwrap_or(0.0);
        let pout = d["price"]["out_per_m"].as_f64().unwrap_or(0.0);
        if pin != 0.0 || pout != 0.0 {
            params["input_cost_per_token"] = json!(pin / 1e6);
            params["output_cost_per_token"] = json!(pout / 1e6);
        }
        let (st, body, _) = self
            .call(
                "POST",
                "/model/new",
                Some(json!({"model_name": name, "litellm_params": params,
                            "model_info": {"id": name, "base_model": d["route"]}})),
                None,
                Duration::from_secs(TIMEOUT_S),
            )
            .await?;
        if st != 200 {
            return Err(GatewayDark(format!(
                "the gateway refused the {name} LLM: {}",
                words_of(&body)
            )));
        }
        Ok(present)
    }

    pub async fn drop_stall(&self, name: &str) -> Result<bool, GatewayDark> {
        if !self.models().await?.contains_key(name) {
            return Ok(false);
        }
        let (st, body, _) = self
            .call(
                "POST",
                "/model/delete",
                Some(json!({"id": name})),
                None,
                Duration::from_secs(TIMEOUT_S),
            )
            .await?;
        if st != 200 {
            return Err(GatewayDark(format!(
                "the gateway would not drop the {name} LLM: {}",
                words_of(&body)
            )));
        }
        Ok(true)
    }

    /// The deal as the gateway's own price map sees it.
    pub async fn seen_deal(&self, name: &str) -> Result<Option<Value>, GatewayDark> {
        let Some(m) = self.models().await?.get(name).cloned() else {
            return Ok(None);
        };
        let info = &m["model_info"];
        let per_m = |v: &Value| v.as_f64().map(|c| (c * 1e6 * 1e6).round() / 1e6);
        let mut mods = vec!["text"];
        if info["supports_vision"].as_bool() == Some(true) {
            mods.push("vision");
        }
        mods.sort();
        Ok(Some(json!({
            "price": {"in_per_m": per_m(&info["input_cost_per_token"]), "out_per_m": per_m(&info["output_cost_per_token"])},
            "context": if info["max_input_tokens"].is_null() { info["max_tokens"].clone() } else { info["max_input_tokens"].clone() },
            "modalities": mods, "tools": info["supports_function_calling"].as_bool() == Some(true),
        })))
    }

    pub async fn key_new(
        &self,
        did: &str,
        alias: &str,
        max_usd: f64,
        renew_days: i64,
    ) -> Result<Value, GatewayDark> {
        let (st, out, _) = self
            .call(
                "POST",
                "/key/generate",
                Some(json!({"key_alias": alias, "user_id": did, "max_budget": max_usd,
                            "budget_duration": budget_duration(renew_days), "metadata": {"orreth": "a body's lease"}})),
                None,
                Duration::from_secs(TIMEOUT_S),
            )
            .await?;
        if st != 200 || out["key"].as_str().is_none() {
            return Err(GatewayDark(format!(
                "the gateway would not mint a key for {alias}: {}",
                words_of(&out)
            )));
        }
        Ok(out)
    }

    pub async fn key_info(&self, key: &str) -> Result<Value, GatewayDark> {
        let (st, out, _) = self
            .call(
                "GET",
                &format!("/key/info?key={key}"),
                None,
                None,
                Duration::from_secs(TIMEOUT_S),
            )
            .await?;
        if st != 200 {
            return Err(GatewayDark(format!(
                "the gateway would not read the key: {}",
                words_of(&out)
            )));
        }
        Ok(out.get("info").cloned().unwrap_or(json!({})))
    }

    pub async fn key_update(&self, key: &str, fields: Value) -> Result<Value, GatewayDark> {
        let mut body = fields;
        body["key"] = json!(key);
        let (st, out, _) = self
            .call(
                "POST",
                "/key/update",
                Some(body),
                None,
                Duration::from_secs(TIMEOUT_S),
            )
            .await?;
        if st != 200 {
            return Err(GatewayDark(format!(
                "the gateway would not update the key: {}",
                words_of(&out)
            )));
        }
        Ok(out)
    }

    pub async fn spend_logs(&self, user_id: &str) -> Result<Vec<Value>, GatewayDark> {
        let (st, out, _) = self
            .call(
                "GET",
                &format!("/spend/logs?user_id={user_id}"),
                None,
                None,
                Duration::from_secs(TIMEOUT_S),
            )
            .await?;
        if st != 200 {
            return Err(GatewayDark(format!(
                "the gateway's spend log refused: {}",
                words_of(&out)
            )));
        }
        Ok(out.as_array().cloned().unwrap_or_default())
    }

    /// The CANARY (`services._probe`, kind mind — the one thought the kernel
    /// itself asks): a one-token ping under `did` through `stall`, with the
    /// body's own key, metered like every thought. `Ok(text)`, or the
    /// honest refusal in words.
    pub async fn ping(
        &self,
        g: &mut Ground,
        scope: &str,
        did: &str,
        name: &str,
        stall: &str,
        route: &str,
    ) -> Result<String, String> {
        let key = crate::stable_live::key_for(g, scope, self, did, name)
            .await
            .map_err(|e| e.to_string())?;
        let body = json!({"model": stall, "max_tokens": 1,
                          "messages": [{"role": "system", "content": "Answer with one word."}, {"role": "user", "content": "ping"}]});
        let out = self
            .call(
                "POST",
                "/chat/completions",
                Some(body),
                Some(key),
                Duration::from_secs(TIMEOUT_S),
            )
            .await;
        match out {
            Err(GatewayDark(w)) => {
                crate::stable_live::meter_failed(g, scope, did, Some(stall), &w)
                    .await
                    .ok();
                Err(w)
            }
            Ok((st, body, headers)) if st != 200 => {
                let w = words_of(&body);
                let words = if st == 429 && w.to_lowercase().contains("budget") {
                    crate::stable_live::mark_drained(g, scope, did).await.ok();
                    format!("I am out of fuel — {w}")
                } else {
                    format!("I cannot think right now — the gateway refused: {w}")
                };
                crate::stable_live::meter_failed(g, scope, did, Some(stall), &words)
                    .await
                    .ok();
                let _ = headers;
                Err(words)
            }
            Ok((_, body, headers)) => {
                let text = body["choices"][0]["message"]["content"]
                    .as_str()
                    .unwrap_or_default()
                    .to_string();
                let usage = &body["usage"];
                let tin = usage["prompt_tokens"].as_i64().unwrap_or(0);
                let tout = usage["completion_tokens"].as_i64().unwrap_or(0);
                let cost = headers
                    .iter()
                    .find(|(k, _)| k == "x-litellm-response-cost")
                    .and_then(|(_, v)| v.parse::<f64>().ok());
                let usd = match cost {
                    Some(c) => c,
                    None => {
                        let price = crate::services_live::get(g.client(), scope, stall)
                            .await
                            .ok()
                            .flatten()
                            .map(|r| r["manifest"]["price"].clone())
                            .unwrap_or(json!({}));
                        usd_of(&price, tin, tout)
                    }
                };
                let rid = body["id"].as_str().map(str::to_string).or_else(|| {
                    headers
                        .iter()
                        .find(|(k, _)| k == "x-litellm-call-id")
                        .map(|(_, v)| v.clone())
                });
                crate::stable_live::meter(
                    g,
                    scope,
                    did,
                    stall,
                    tin,
                    tout,
                    usd,
                    Some(stall),
                    rid.as_deref(),
                    true,
                    None,
                )
                .await
                .map_err(|e| e.to_string())?;
                let _ = route;
                Ok(text)
            }
        }
    }
}
