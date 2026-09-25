// PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp6, the bodies' seam · 2026-09-24
//! `orreth.minds/1` — the pure laws of `orreth_spine.stable` (P6.5 sp3, THE
//! STABLE: LiteLLM executes; the registry knows and decides), ported word for
//! word against `spine/conformance/minds-v0.json`: the gateway's route for a
//! mind wherever it resides (`route_for`), the DEAL a stall pins (`deal`, the
//! key an env NAME — a VALUE is refused), the cost arithmetic (`usd`), the fuel
//! clause's window (`budget_duration`), THE ROUTING DECISION (`resolve`: pin →
//! the subject's assignment for the class → the world's → the template's model
//! → the cheapest standing stall of the class → a neighbouring class, confessed
//! — W44: the class asked wins, then the all-work one, then the newest, never
//! the alphabet), what moved under a pin (`drift`), EOL as an appointment
//! (`eol_due`), the swap for a mind on its way out (`recommend`), the honest
//! word when a body is out of fuel (`drained_words`) and the act NAMED in words
//! for the interlock (`act_words`, W30 · W42). The gateway's doors, the ground
//! and the keeper's beat are [`crate::stable_live`]'s.

use crate::py::{g_fmt, parse_iso_secs, python_str, thousands, truthy};
use regex::Regex;
use serde_json::{json, Value};
use std::sync::LazyLock;

pub const CLASSES: [&str; 3] = ["fast", "standard", "deep"];
/// An assignment for ALL of a body's work (W44).
pub const ANY: &str = "any";
pub const PROVIDERS: [&str; 5] = ["anthropic", "openrouter", "ollama", "openai", "compatible"];
/// A stall that may serve.
pub const STANDING: [&str; 3] = ["registered", "versioned", "healthy"];
pub const OLLAMA_DIAL: &str = "SPINE_OLLAMA_BASE";
pub const OLLAMA_DEFAULT: &str = "http://host.docker.internal:11434";

pub const REGISTER_TOOL: &str = "mind.register";
pub const ASSIGN_TOOL: &str = "mind.assign";
pub const UNASSIGN_TOOL: &str = "mind.unassign";
pub const REFILL_TOOL: &str = "mind.refill";
pub const REPIN_TOOL: &str = "mind.repin";
pub const RETIRE_TOOL: &str = "service.retire";
pub const HELD_TOOLS: [&str; 6] = [
    REGISTER_TOOL,
    ASSIGN_TOOL,
    UNASSIGN_TOOL,
    REFILL_TOOL,
    REPIN_TOOL,
    RETIRE_TOOL,
];
pub const ACT_LEVEL: &str = "L2";
pub const ACT_CLASS: &str = "consequential";

pub const ASSIGNED: &str = "orreth.mind.assigned.v1";
pub const UNASSIGNED: &str = "orreth.mind.unassigned.v1";
pub const FUELED: &str = "orreth.mind.fueled.v1";

static ENV_NAME: LazyLock<Regex> = LazyLock::new(|| Regex::new(r"^[A-Z][A-Z0-9_]{2,}$").unwrap());

/// The key's env NAME for a provider (`None`: a local mind needs no key).
pub fn key_of(provider: &str) -> Option<&'static str> {
    match provider {
        "anthropic" => Some("ANTHROPIC_API_KEY"),
        "openrouter" => Some("OPENROUTER_API_KEY"),
        "openai" => Some("OPENAI_API_KEY"),
        _ => None,
    }
}

fn s_of(v: &Value) -> String {
    match v {
        Value::Null => String::new(),
        Value::String(s) => s.clone(),
        other => python_str(other),
    }
}

fn f_of(v: &Value) -> f64 {
    match v {
        Value::Number(n) => n.as_f64().unwrap_or(0.0),
        Value::String(s) => s.trim().parse().unwrap_or(0.0),
        Value::Bool(true) => 1.0,
        _ => 0.0,
    }
}

fn opt_i64(v: &Value) -> Option<i64> {
    if !truthy(v) {
        return None;
    }
    v.as_i64()
        .or_else(|| v.as_f64().map(|f| f as i64))
        .or_else(|| v.as_str().and_then(|s| s.trim().parse().ok()))
}

fn refused(reason: String) -> Value {
    json!({"ok": false, "route": null, "base": null, "reason": reason})
}

/// `stable.route_for`: the gateway's model string for a mind wherever it
/// resides — and the base it needs, when it needs one. `{ok, route, base, reason}`.
pub fn route_for(provider: &str, model: &str, base: Option<&str>) -> Value {
    let p = provider.trim().to_lowercase();
    let m = model.trim();
    if !PROVIDERS.contains(&p.as_str()) {
        return refused(format!(
            "no provider named {} — the providers: {}",
            crate::py::repr_str(provider),
            PROVIDERS.join(", ")
        ));
    }
    if m.is_empty() {
        return refused("a mind needs a model id".into());
    }
    let base = base.filter(|b| !b.is_empty());
    if p == "compatible" && base.is_none() {
        return refused("an OpenAI-compatible mind needs its base URL".into());
    }
    if p == "ollama" {
        let b = base.map(str::to_string).unwrap_or_else(|| {
            std::env::var(OLLAMA_DIAL)
                .ok()
                .filter(|x| !x.is_empty())
                .unwrap_or_else(|| OLLAMA_DEFAULT.into())
        });
        return json!({"ok": true, "route": format!("ollama/{m}"), "base": b, "reason": null});
    }
    if p == "compatible" {
        return json!({"ok": true, "route": format!("openai/{m}"), "base": base, "reason": null});
    }
    json!({"ok": true, "route": format!("{p}/{m}"), "base": base, "reason": null})
}

/// What `deal` asks for.
#[derive(Debug, Clone, Default)]
pub struct DealAsk<'a> {
    pub base: Option<&'a str>,
    pub price: Option<&'a Value>,
    pub context: Option<&'a Value>,
    pub modalities: Option<&'a Value>,
    pub klass: Option<&'a str>,
    /// `None` = "auto" (the provider's env NAME); `Some(None)` = no key; `Some(Some(name))` = a named key.
    pub key: Option<Option<&'a str>>,
    pub expires: Option<&'a str>,
}

/// `stable.deal`: the DEAL a stall pins — the manifest. The key is an env
/// NAME (a value is refused: it never enters a record); prices are dollars
/// per MILLION tokens. Refuses in words.
pub fn deal(model: &str, provider: &str, ask: DealAsk<'_>) -> Result<Value, String> {
    let r = route_for(provider, model, ask.base);
    if r["ok"] != json!(true) {
        return Err(r["reason"].as_str().unwrap_or_default().to_string());
    }
    let p = provider.trim().to_lowercase();
    let klass = ask.klass.unwrap_or("standard");
    if !CLASSES.contains(&klass) {
        return Err(format!(
            "no class named {} — the classes: {}",
            crate::py::repr_str(klass),
            CLASSES.join(", ")
        ));
    }
    let k: Option<String> = match ask.key {
        None => key_of(&p).map(str::to_string),
        Some(k) => k.map(str::to_string),
    };
    if let Some(k) = &k {
        if !ENV_NAME.is_match(k) {
            return Err(
                "a key VALUE never enters a record — name the environment variable that holds \
                        it (like ANTHROPIC_API_KEY)"
                    .into(),
            );
        }
    }
    let price = ask.price.cloned().unwrap_or(Value::Null);
    let pin = f_of(price.get("in_per_m").unwrap_or(&Value::Null));
    let pout = f_of(price.get("out_per_m").unwrap_or(&Value::Null));
    if pin < 0.0 || pout < 0.0 {
        return Err("a price is never negative".into());
    }
    let context = ask.context.and_then(opt_i64);
    let mut mods: Vec<String> = match ask.modalities {
        Some(Value::Array(a)) if !a.is_empty() => a.iter().map(s_of).collect(),
        _ => vec!["text".into()],
    };
    mods.sort();
    mods.dedup();
    let mut d = json!({
        "model": model.trim(), "provider": p, "route": r["route"], "base": r["base"], "key": k,
        "price": {"in_per_m": pin, "out_per_m": pout}, "context": context,
        "modalities": mods, "class": klass,
    });
    if let Some(e) = ask.expires.filter(|e| !e.is_empty()) {
        d["expires"] = json!(e);
    }
    Ok(d)
}

/// `stable.usd`: dollars from the pin's price, never guessed — rounded to the
/// ten-millionth of a dollar (the gateway's own grain).
pub fn usd(price: &Value, tokens_in: i64, tokens_out: i64) -> f64 {
    let pin = f_of(price.get("in_per_m").unwrap_or(&Value::Null));
    let pout = f_of(price.get("out_per_m").unwrap_or(&Value::Null));
    let raw = tokens_in as f64 * pin / 1e6 + tokens_out as f64 * pout / 1e6;
    (raw * 1e10).round() / 1e10
}

/// `stable.budget_duration`: the fuel clause's window in the gateway's grammar.
pub fn budget_duration(days: i64) -> String {
    format!("{}d", days.max(1))
}

fn standing(s: &Value) -> bool {
    s["state"].as_str().is_some_and(|st| STANDING.contains(&st))
}

fn manifest(s: &Value) -> Value {
    match s.get("manifest") {
        Some(m) if truthy(m) => m.clone(),
        _ => json!({}),
    }
}

fn price_in(s: &Value) -> f64 {
    f_of(&manifest(s)["price"]["in_per_m"])
}

fn version_of(s: &Value) -> i64 {
    s["version"].as_i64().unwrap_or(0)
}

fn name_of(s: &Value) -> String {
    s_of(&s["name"])
}

/// `_cheapest`: by price in, then the newest version, then the name.
fn cheapest(cands: &[&Value]) -> Option<Value> {
    let mut v: Vec<&Value> = cands.to_vec();
    v.sort_by(|a, b| {
        price_in(a)
            .partial_cmp(&price_in(b))
            .unwrap_or(std::cmp::Ordering::Equal)
            .then(version_of(b).cmp(&version_of(a)))
            .then(name_of(a).cmp(&name_of(b)))
    });
    v.first().map(|s| (*s).clone())
}

fn decided(stall: &str, route: &Value, why: String, degraded: bool) -> Value {
    json!({"ok": true, "stall": stall, "route": route, "why": why, "degraded": degraded, "reason": null})
}

fn undecided(reason: String) -> Value {
    json!({"ok": false, "stall": null, "route": null, "why": null, "degraded": false, "reason": reason})
}

/// What `resolve` is asked with.
#[derive(Debug, Clone, Default)]
pub struct ResolveAsk<'a> {
    pub subject: Option<&'a str>,
    pub klass: Option<&'a str>,
    pub pin: Option<&'a str>,
    pub model: Option<&'a str>,
}

fn newest(rows: &[&Value]) -> Vec<Value> {
    let mut v: Vec<&Value> = rows.to_vec();
    v.sort_by(|a, b| s_of(&b["at"]).cmp(&s_of(&a["at"])));
    v.into_iter().cloned().collect()
}

/// `stable.resolve` — THE ROUTING DECISION, one law, the fixture's.
pub fn resolve(stalls: &[Value], assignments: &[Value], ask: ResolveAsk<'_>) -> Value {
    let by_name = |n: &str| stalls.iter().find(|s| name_of(s) == n);
    if let Some(pin) = ask.pin.filter(|p| !p.is_empty()) {
        let Some(s) = by_name(pin) else {
            return undecided(format!(
                "no LLM named {} stands in the Stable",
                crate::py::repr_str(pin)
            ));
        };
        if !standing(s) {
            return undecided(format!(
                "the {pin} LLM is {} — a pinned LLM that does not stand refuses, never climbs",
                s_of(&s["state"])
            ));
        }
        return decided(
            pin,
            &manifest(s)["route"],
            format!("pinned to {pin} for this ask"),
            false,
        );
    }
    let k = ask.klass.filter(|k| CLASSES.contains(k));
    let subjects: Vec<&str> = match ask.subject.filter(|s| !s.is_empty()) {
        Some(s) => vec![s, "*"],
        None => vec!["*"],
    };
    for who in subjects {
        let rows: Vec<&Value> = assignments
            .iter()
            .filter(|a| a["subject"].as_str() == Some(who))
            .collect();
        let is_wide = |a: &Value| {
            a.get("klass")
                .map(|kl| kl.is_null() || kl.as_str() == Some(ANY))
                .unwrap_or(true)
        };
        let exact: Vec<&Value> = rows
            .iter()
            .copied()
            .filter(|a| k.is_some() && a["klass"].as_str() == k)
            .collect();
        let wide: Vec<&Value> = rows.iter().copied().filter(|a| is_wide(a)).collect();
        let rest: Vec<&Value> = rows
            .iter()
            .copied()
            .filter(|a| !exact.iter().any(|e| std::ptr::eq(*e, *a)) && !is_wide(a))
            .collect();
        let mut ordered = newest(&exact);
        ordered.extend(newest(&wide));
        if k.is_none() {
            ordered.extend(newest(&rest));
        }
        for a in ordered {
            let stall = s_of(&a["stall"]);
            if let Some(s) = by_name(&stall) {
                if standing(s) {
                    let whom = if who == "*" { "every body" } else { who };
                    let why = if is_wide(&a) {
                        format!("assigned: {whom} uses {} for all work", name_of(s))
                    } else {
                        format!(
                            "assigned: {whom} uses {} for {} work",
                            name_of(s),
                            s_of(&a["klass"])
                        )
                    };
                    return decided(&name_of(s), &manifest(s)["route"], why, false);
                }
            }
        }
    }
    if let Some(model) = ask.model.filter(|m| !m.is_empty()) {
        for s in stalls {
            let m = manifest(s);
            if standing(s)
                && m["model"].as_str() == Some(model)
                && (k.is_none() || m["class"].as_str() == k)
            {
                return decided(
                    &name_of(s),
                    &m["route"],
                    format!("the template names {model} — the {} LLM", name_of(s)),
                    false,
                );
            }
        }
    }
    let standing_stalls: Vec<&Value> = stalls.iter().filter(|s| standing(s)).collect();
    if let Some(k) = k {
        let of_class = |kl: &str| -> Vec<&Value> {
            standing_stalls
                .iter()
                .copied()
                .filter(|s| manifest(s)["class"].as_str() == Some(kl))
                .collect()
        };
        if let Some(s) = cheapest(&of_class(k)) {
            return decided(
                &name_of(&s),
                &manifest(&s)["route"],
                format!("the cheapest standing {k} LLM"),
                false,
            );
        }
        let near: [&str; 2] = match k {
            "fast" => ["standard", "deep"],
            "standard" => ["fast", "deep"],
            _ => ["standard", "fast"],
        };
        for nk in near {
            if let Some(s) = cheapest(&of_class(nk)) {
                return decided(
                    &name_of(&s),
                    &manifest(&s)["route"],
                    format!(
                        "no {k} LLM stands — the {nk} LLM {} serves instead, confessed",
                        name_of(&s)
                    ),
                    true,
                );
            }
        }
    }
    if let Some(s) = cheapest(&standing_stalls) {
        let model = ask.model.filter(|m| !m.is_empty());
        return decided(
            &name_of(&s),
            &manifest(&s)["route"],
            format!(
                "the cheapest standing LLM{}",
                model
                    .map(|m| format!(" — none named {m}"))
                    .unwrap_or_default()
            ),
            model.is_some(),
        );
    }
    undecided(
        "no LLM stands in the Stable — add one (\"stablekeeper, add the LLM ollama gemma3:270m as gemma\")"
            .into(),
    )
}

/// `stable.drift`: what moved under the pin — the price in or out, the
/// context. Words, one per move; empty = the deal holds.
pub fn drift(pinned: &Value, seen: &Value) -> Vec<String> {
    let mut moved = Vec::new();
    let pp = pinned
        .get("price")
        .filter(|p| truthy(p))
        .cloned()
        .unwrap_or(json!({}));
    let sp = seen
        .get("price")
        .filter(|p| truthy(p))
        .cloned()
        .unwrap_or(json!({}));
    for (side, word) in [("in_per_m", "in"), ("out_per_m", "out")] {
        let a = f_of(pp.get(side).unwrap_or(&Value::Null));
        let b = sp.get(side).filter(|v| !v.is_null());
        if let Some(b) = b {
            let b = f_of(b);
            if (b - a).abs() > 1e-9 {
                moved.push(format!(
                    "the price {word} moved: ${} → ${} per million",
                    g_fmt(a),
                    g_fmt(b)
                ));
            }
        }
    }
    let pc = pinned.get("context").and_then(opt_i64);
    let sc = seen.get("context").and_then(opt_i64);
    if let (Some(pc), Some(sc)) = (pc, sc) {
        if pc != 0 && sc != 0 && sc != pc {
            moved.push(format!(
                "the context moved: {} → {} tokens",
                thousands(pc),
                thousands(sc)
            ));
        }
    }
    moved
}

fn date_of(iso: &str) -> String {
    let s = iso.trim();
    let date = s
        .split_once('T')
        .or_else(|| s.split_once(' '))
        .map(|(d, _)| d)
        .unwrap_or(s);
    date.to_string()
}

/// `stable.eol_due`: EOL is an appointment — an expiry inside the horizon is
/// due. `now` and `expires` are ISO texts; `{due, days, words}`.
pub fn eol_due(expires: Option<&str>, now: &str, horizon_days: i64) -> Value {
    let Some(exp) = expires.filter(|e| !e.is_empty()) else {
        return json!({"due": false, "days": null, "words": "no expiry named"});
    };
    let (Some(at), Some(now_s)) = (parse_iso_secs(exp), parse_iso_secs(now)) else {
        return json!({"due": false, "days": null,
                      "words": format!("an expiry the calendar cannot read: {}", crate::py::repr_str(exp))});
    };
    let days = (at - now_s).div_euclid(86_400);
    let date = date_of(exp);
    if days <= horizon_days {
        let words = if days >= 0 {
            format!(
                "expires in {days} day{} ({date})",
                if days != 1 { "s" } else { "" }
            )
        } else {
            format!(
                "expired {} day{} ago ({date})",
                -days,
                if -days != 1 { "s" } else { "" }
            )
        };
        return json!({"due": true, "days": days, "words": words});
    }
    json!({"due": false, "days": days,
           "words": format!("expires in {days} days — outside the {horizon_days}-day horizon")})
}

/// `stable.recommend`: the swap for a mind on its way out — same class →
/// fit (context no smaller, modalities covering) → nearest price → newest.
pub fn recommend(stalls: &[Value], retiring: &str) -> Value {
    let Some(old) = stalls.iter().find(|s| name_of(s) == retiring) else {
        return json!({"stall": null,
                      "why": format!("no LLM named {} to swap from", crate::py::repr_str(retiring))});
    };
    let om = manifest(old);
    let klass = om["class"].as_str().map(str::to_string);
    let cands: Vec<&Value> = stalls
        .iter()
        .filter(|s| {
            name_of(s) != retiring
                && standing(s)
                && manifest(s)["class"].as_str() == klass.as_deref()
        })
        .collect();
    if cands.is_empty() {
        return json!({"stall": null,
                      "why": format!("no other standing {} LLM — nothing to swap to",
                                     klass.clone().unwrap_or_else(|| "?".into()))});
    }
    let oc = om.get("context").and_then(opt_i64).unwrap_or(0);
    let mut omods: Vec<String> = om["modalities"]
        .as_array()
        .map(|a| a.iter().map(s_of).collect())
        .unwrap_or_default();
    omods.sort();
    let fit: Vec<&Value> = cands
        .iter()
        .copied()
        .filter(|s| {
            let m = manifest(s);
            let ctx_ok = oc == 0 || m.get("context").and_then(opt_i64).unwrap_or(0) >= oc;
            let smods: Vec<String> = m["modalities"]
                .as_array()
                .map(|a| a.iter().map(s_of).collect())
                .unwrap_or_default();
            ctx_ok && omods.iter().all(|x| smods.contains(x))
        })
        .collect();
    if fit.is_empty() {
        let kl = klass.clone().unwrap_or_default();
        return json!({"stall": null,
                      "why": format!("{} {kl} LLM{} stand but none fits the deal (context {}, {})",
                                     cands.len(), if cands.len() != 1 { "s" } else { "" },
                                     om.get("context").map(python_str).unwrap_or_else(|| "None".into()),
                                     omods.join(", "))});
    }
    let op = price_in(old);
    let mut best: Vec<&Value> = fit;
    best.sort_by(|a, b| {
        (price_in(a) - op)
            .abs()
            .partial_cmp(&(price_in(b) - op).abs())
            .unwrap_or(std::cmp::Ordering::Equal)
            .then(version_of(b).cmp(&version_of(a)))
            .then(name_of(a).cmp(&name_of(b)))
    });
    let b = best[0];
    json!({"stall": name_of(b),
           "why": format!("same class, fits the deal, nearest price (${} vs ${} per million in)",
                          g_fmt(price_in(b)), g_fmt(op))})
}

/// `stable.drained_words`: the honest word when a body is out of fuel.
pub fn drained_words(name: &str, gauge: Option<&Value>) -> String {
    let mut when = String::new();
    if let Some(g) = gauge {
        if let Some(r) = g.get("renews_at").filter(|v| truthy(v)) {
            let r = s_of(r);
            if let Some(c) = crate::memory::Civil::parse(&r) {
                when = format!(
                    " It renews on its own at {:04}-{:02}-{:02} {:02}:{:02} UTC.",
                    c.year, c.month, c.day, c.hour, c.minute
                );
            }
        }
    }
    let ceiling = match gauge
        .and_then(|g| g.get("max_usd"))
        .filter(|v| !v.is_null())
    {
        Some(m) => format!("${}", g_fmt(f_of(m))),
        None => "its allowance".into(),
    };
    format!(
        "I am out of fuel — {name}'s LLM allowance of {ceiling} for this window is spent, so I cannot \
         think until it renews or is refilled.{when} A refill is one word away: \"refill {name} by $1\"."
    )
}

/// `stable.act_words`: the act NAMED in words — the bare phrase the interlock
/// frames ONCE (W30 · W42).
pub fn act_words(tool: &str, args: &Value) -> String {
    let n = [&args["name"], &args["stall"]]
        .iter()
        .find(|v| truthy(v))
        .map(|v| s_of(v))
        .unwrap_or_else(|| "?".into());
    let who = || {
        if args["subject"].as_str() == Some("*") {
            "every body".to_string()
        } else {
            s_of(&args["subject"])
        }
    };
    let wide = || {
        args.get("klass")
            .map(|k| k.is_null() || k.as_str() == Some(ANY))
            .unwrap_or(true)
    };
    match tool {
        REGISTER_TOOL => {
            let d = args
                .get("deal")
                .filter(|d| truthy(d))
                .cloned()
                .unwrap_or(json!({}));
            let f = |k: &str| {
                d.get(k)
                    .filter(|v| truthy(v))
                    .map(s_of)
                    .unwrap_or_else(|| "?".into())
            };
            format!(
                "Adding the {n} LLM ({} {}) to the Stable and the gateway",
                f("provider"),
                f("model")
            )
        }
        ASSIGN_TOOL => {
            let work = if wide() {
                "all its work".to_string()
            } else {
                format!("{} work", s_of(&args["klass"]))
            };
            format!(
                "Pointing {} at the {} LLM for {work}",
                who(),
                s_of(&args["stall"])
            )
        }
        UNASSIGN_TOOL => {
            let work = if wide() {
                "all-work".to_string()
            } else {
                s_of(&args["klass"])
            };
            format!("Lifting {}'s {work} assignment", who())
        }
        REFILL_TOOL => {
            let whom = [&args["name"], &args["did"]]
                .iter()
                .find(|v| truthy(v))
                .map(|v| s_of(v))
                .unwrap_or_default();
            format!(
                "Refilling {whom} by ${} of real spending",
                g_fmt(f_of(args.get("usd").unwrap_or(&Value::Null)))
            )
        }
        REPIN_TOOL => {
            format!("Re-pinning the {n} LLM to its new deal (the old pin stays in its history)")
        }
        RETIRE_TOOL => format!("Retiring the {n} LLM (it rests, never deleted)"),
        other => format!("The {other} act"),
    }
}

/// `stable.stall_words`: one line for a stall on the shelf.
pub fn stall_words(s: &Value) -> String {
    let m = manifest(s);
    let pr = m
        .get("price")
        .filter(|p| truthy(p))
        .cloned()
        .unwrap_or(json!({}));
    let sp = s
        .get("spend")
        .filter(|p| truthy(p))
        .cloned()
        .unwrap_or(json!({}));
    let calls = sp["calls"].as_i64().unwrap_or(0);
    let mut out = format!(
        "{} — {} {} · {} · ${} in / ${} out per million",
        name_of(s),
        python_str(m.get("provider").unwrap_or(&Value::Null)),
        python_str(m.get("model").unwrap_or(&Value::Null)),
        python_str(m.get("class").unwrap_or(&Value::Null)),
        g_fmt(f_of(pr.get("in_per_m").unwrap_or(&Value::Null))),
        g_fmt(f_of(pr.get("out_per_m").unwrap_or(&Value::Null)))
    );
    if let Some(c) = m.get("context").and_then(opt_i64).filter(|c| *c != 0) {
        out.push_str(&format!(" · context {}", thousands(c)));
    }
    out.push_str(&format!(" · {}", s_of(&s["state"])));
    if calls > 0 {
        out.push_str(&format!(
            " · spent ${:.4} over {calls} call{}",
            f_of(&sp["usd"]),
            if calls != 1 { "s" } else { "" }
        ));
    } else {
        out.push_str(" · never called");
    }
    out
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn the_route_and_the_deal() {
        assert_eq!(
            route_for("anthropic", "x", None)["route"],
            json!("anthropic/x")
        );
        assert_eq!(route_for("compatible", "x", None)["ok"], json!(false));
        let d = deal("claude-haiku-4-5-20251001", "anthropic", DealAsk::default()).unwrap();
        assert_eq!(d["key"], json!("ANTHROPIC_API_KEY"));
        assert!(deal(
            "x",
            "anthropic",
            DealAsk {
                key: Some(Some("sk-ant-abc")),
                ..Default::default()
            }
        )
        .unwrap_err()
        .contains("a key VALUE"));
        assert_eq!(
            usd(&json!({"in_per_m": 1.0, "out_per_m": 5.0}), 13, 5),
            3.8e-05
        );
        assert_eq!(budget_duration(0), "1d");
    }
}
