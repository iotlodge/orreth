// PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp5, memory and the export · 2026-09-24
//! The compliance export's ground half — `orreth_spine.export.build` ported:
//! the bundle for ONE scope (session · window · marker root) of the
//! requester's own asks, read off the outbox (the outbox IS the audit
//! trail: every fact with its event, in commit order), each fact shaped
//! into a row exactly as the reference shapes it, the why in words (W11),
//! a body's placement, the withheld words of an opt-out session (P11) —
//! then sealed and SIGNED by the kernel's own self (`export::seal`).

use crate::ask::{ASK_RECEIVED, ASK_REFUSED};
use crate::asks::{CONFIRM_NEEDED, REPLY};
use crate::envelope;
use crate::export::seal;
use crate::ground::Ground;
use crate::intent::INTENTION_STOPPED;
use crate::kernel_self::KernelSelf;
use crate::markers_live::{self, INCLUDES, MARKER_SET};
use crate::proof_live::PROOF_ATTEMPT;
use crate::py::{get, truthy};
use crate::schema::has_table;
use crate::world::RoadError;
use serde_json::{json, Map, Value};
use std::collections::{BTreeSet, HashMap, HashSet};

pub const TOOL_CALLED: &str = "orreth.tool.called.v1";
pub const KERNEL: &str = "the kernel";

fn kind_of(t: &str) -> Option<&'static str> {
    Some(match t {
        x if x == ASK_RECEIVED => "ask",
        x if x == CONFIRM_NEEDED => "hold",
        x if x == PROOF_ATTEMPT => "proof",
        x if x == REPLY => "reply",
        x if x == INTENTION_STOPPED => "intention.stop",
        x if x == MARKER_SET => "marker.set",
        x if x == TOOL_CALLED => "tool",
        x if x == ASK_REFUSED => "refused",
        _ => return None,
    })
}

pub async fn current_session(
    g: &Ground,
    scope: &str,
    person: &str,
) -> Result<Option<String>, RoadError> {
    let row = g
        .client()
        .query_opt(
            "SELECT session_id FROM spine_sessions WHERE person = $1 AND scope = $2 ORDER BY opened_at DESC \
             LIMIT 1",
            &[&person, &scope],
        )
        .await?;
    Ok(row.map(|r| r.get(0)))
}

struct Ask {
    text: String,
    reply: Option<String>,
    person: String,
    served_by: Option<String>,
    target: Option<String>,
    state: String,
    proof: String,
    held: Option<Value>,
    root: Option<String>,
}

fn s(v: &Value) -> Option<String> {
    v.as_str().map(str::to_string)
}

#[allow(clippy::too_many_arguments)]
fn row(
    e: &Value,
    kind: &str,
    oid: i64,
    asks: &HashMap<String, Ask>,
    intentions: &BTreeSet<String>,
    marker_ids: &HashSet<String>,
    firmware: &HashSet<String>,
    iwords: &HashMap<String, String>,
) -> Option<Value> {
    let p = get(e, "payload");
    let r#ref = s(get(p, "ref"));
    let mk = e.get("marker").filter(|m| m.is_object());
    let a = r#ref.as_ref().and_then(|r| asks.get(r));
    let mut kind = kind.to_string();
    let (person, served, proof, words): (Value, Value, Value, Value);
    if kind == "intention.stop" {
        let r = r#ref.clone()?;
        if !intentions.contains(&r) {
            return None;
        }
        person = get(p, "by").clone();
        served = Value::Null;
        proof = if truthy(get(p, "proof")) {
            get(p, "proof").clone()
        } else {
            json!("L1")
        };
        words = match iwords.get(&r) {
            Some(w) => json!({"intention": w}),
            None => Value::Null,
        };
    } else if kind == "marker.set" {
        let in_scope = a.is_some()
            || mk.is_some_and(|m| s(get(m, "id")).is_some_and(|id| marker_ids.contains(&id)));
        if !in_scope {
            return None;
        }
        served = mk.map(|m| get(m, "by").clone()).unwrap_or(Value::Null);
        person = match a {
            Some(a) => json!(a.person),
            None => e
                .get("authority_chain")
                .and_then(Value::as_array)
                .and_then(|c| c.first())
                .cloned()
                .unwrap_or_else(|| served.clone()),
        };
        proof = Value::Null;
        words = Value::Null;
    } else {
        let a = a?;
        person = json!(a.person);
        let mut served_v = Value::Null;
        let (pr, wd) = match kind.as_str() {
            "ask" => (json!(a.proof), json!({"ask": a.text})),
            "refused" => {
                served_v = json!(KERNEL);
                (json!(a.proof), json!({"ask": a.text, "reply": a.reply}))
            }
            "hold" => {
                served_v = json!(a.served_by);
                (
                    if truthy(get(p, "level")) {
                        get(p, "level").clone()
                    } else {
                        json!("L2")
                    },
                    Value::Null,
                )
            }
            "proof" => (get(p, "level").clone(), Value::Null),
            "tool" => {
                served_v = if truthy(get(p, "service")) {
                    get(p, "service").clone()
                } else {
                    json!(format!(
                        "tool:{}",
                        get(p, "tool").as_str().unwrap_or_default()
                    ))
                };
                (json!(a.proof), Value::Null)
            }
            _ => {
                served_v = json!(a.served_by);
                let pr = if truthy(get(p, "proof")) {
                    get(p, "proof").clone()
                } else {
                    json!(a.proof)
                };
                let is_include = a.served_by.as_ref().is_some_and(|d| firmware.contains(d))
                    || a.target
                        .as_ref()
                        .is_some_and(|t| INCLUDES.contains(&t.as_str()));
                if is_include {
                    kind = "include".into();
                }
                (pr, json!({"reply": a.reply}))
            }
        };
        served = served_v;
        proof = pr;
        words = wd;
    }
    let marker = mk.map(|m| {
        let parent_none = get(m, "parent").is_null();
        json!({
            "kind": get(m, "kind"), "id": get(m, "id"), "parent": get(m, "parent"),
            "root": a.and_then(|a| a.root.clone()).map(Value::String)
                .unwrap_or_else(|| if parent_none { get(m, "id").clone() } else { Value::Null }),
        })
    });
    let mut out = json!({
        "at": e["occurred_at"], "kind": kind, "ref": r#ref, "person": person,
        "authority_chain": e.get("authority_chain").cloned().unwrap_or(json!([])), "chain_status": Value::Null,
        "proof": proof, "target": a.and_then(|a| a.target.clone()),
        "marker": marker.unwrap_or(Value::Null), "words": words, "served_by": served,
        "message_id": e.get("message_id").cloned().unwrap_or(Value::Null), "_order": oid,
    });
    if kind == "hold" {
        out["tool"] = get(p, "tool").clone();
        out["class"] = get(p, "class").clone();
    }
    if kind == "proof" {
        out["ok"] = json!(truthy(get(p, "ok")));
    }
    if kind == "tool" {
        out["tool"] = get(p, "tool").clone();
        out["ok"] = json!(truthy(get(p, "ok")));
    }
    if let Some(a) = a {
        if a.state != "in" {
            out["words"] = Value::Null;
            out["words_withheld"] = json!(a.state);
        }
    }
    Some(out)
}

/// W11: the WHY in words — for each marker, the words of the objective it
/// serves (its parent's when it has one, its own when it is a root), read
/// through `markers_live::with_words`; an opt-out session's words withheld.
async fn marker_words(
    g: &Ground,
    scope: &str,
    ids: &BTreeSet<String>,
) -> Result<HashMap<String, Option<String>>, RoadError> {
    let mut out = HashMap::new();
    if ids.is_empty() {
        return Ok(out);
    }
    let idv: Vec<String> = ids.iter().cloned().collect();
    let rows = g
        .client()
        .query(
            "SELECT marker_id, parent FROM spine_markers WHERE marker_id = ANY($1)",
            &[&idv],
        )
        .await?;
    let parent: HashMap<String, Option<String>> =
        rows.iter().map(|r| (r.get(0), r.get(1))).collect();
    let want: Vec<String> = ids
        .iter()
        .map(|i| {
            parent
                .get(i)
                .cloned()
                .flatten()
                .unwrap_or_else(|| i.clone())
        })
        .collect::<BTreeSet<_>>()
        .into_iter()
        .collect();
    let rows = g
        .client()
        .query(
            "SELECT marker_id, kind, parent, ref, by_did, note, at, 0 FROM spine_markers WHERE marker_id = ANY($1)",
            &[&want],
        )
        .await?;
    let found =
        markers_live::with_words(g, rows.iter().map(markers_live::row_of).collect()).await?;
    let mut found: HashMap<String, Value> = found
        .into_iter()
        .map(|m| (s(get(&m, "id")).unwrap_or_default(), m))
        .collect();
    let refs: Vec<String> = found
        .values()
        .filter_map(|m| s(get(m, "ref")))
        .filter(|r| r.starts_with("ask_"))
        .collect();
    if !refs.is_empty() {
        let withheld = g
            .client()
            .query("SELECT ask_id FROM spine_asks WHERE ask_id = ANY($1) AND coalesce(state, 'in') <> 'in'", &[&refs])
            .await?;
        for w in withheld {
            let id: String = w.get(0);
            for m in found.values_mut() {
                if s(get(m, "ref")).as_deref() == Some(&id) {
                    m["words"] = Value::Null;
                    m["note"] = Value::Null;
                }
            }
        }
    }
    let _ = scope;
    for i in ids {
        let key = parent
            .get(i)
            .cloned()
            .flatten()
            .unwrap_or_else(|| i.clone());
        let words = found.get(&key).and_then(|m| {
            s(get(m, "words"))
                .filter(|w| !w.is_empty())
                .or_else(|| s(get(m, "note")).filter(|w| !w.is_empty()))
        });
        out.insert(i.clone(), words);
    }
    Ok(out)
}

/// `export.build`: the bundle for ONE scope of the requester's own asks;
/// none given → the current session. Signed when a signer is handed in.
pub async fn build(
    g: &Ground,
    world: &str,
    person: &str,
    session: Option<&str>,
    window: Option<(&str, &str)>,
    marker: Option<&str>,
    signer: Option<&KernelSelf>,
) -> Result<Value, RoadError> {
    let session: Option<String> = match (session, window, marker) {
        (None, None, None) => current_session(g, world, person).await?,
        (s, _, _) => s.map(str::to_string),
    };
    let mut scope = Map::new();
    scope.insert("person".into(), json!(person));
    let mut wheres: Vec<String> = vec!["a.person = $1".into(), "a.scope = $2".into()];
    let mut params: Vec<Box<dyn tokio_postgres::types::ToSql + Sync + Send>> =
        vec![Box::new(person.to_string()), Box::new(world.to_string())];
    if let Some(sid) = &session {
        scope.insert("session".into(), json!(sid));
        params.push(Box::new(sid.clone()));
        wheres.push(format!("a.session = ${}", params.len()));
    }
    if let Some((f, t)) = window {
        scope.insert("window".into(), json!({"from": f, "to": t}));
        params.push(Box::new(f.to_string()));
        params.push(Box::new(t.to_string()));
        wheres.push(format!(
            "a.asked_at BETWEEN ${}::timestamptz AND ${}::timestamptz",
            params.len() - 1,
            params.len()
        ));
    }
    if let Some(m) = marker {
        scope.insert("marker".into(), json!(m));
        params.push(Box::new(m.to_string()));
        wheres.push(format!("m.root = ${}", params.len()));
    }
    let sql = format!(
        "SELECT a.ask_id, a.text, a.reply, a.person, a.served_by, a.target, a.state, a.proof, a.session, \
         a.marker, a.held, m.root FROM spine_asks a LEFT JOIN spine_markers m ON m.marker_id = a.marker WHERE \
         {} ORDER BY a.asked_at",
        wheres.join(" AND ")
    );
    let refs: Vec<&(dyn tokio_postgres::types::ToSql + Sync)> = params
        .iter()
        .map(|p| p.as_ref() as &(dyn tokio_postgres::types::ToSql + Sync))
        .collect();
    let rows = g.client().query(&sql, &refs).await?;
    let mut asks: HashMap<String, Ask> = HashMap::new();
    let mut order: Vec<String> = Vec::new();
    for r in &rows {
        let id: String = r.get(0);
        order.push(id.clone());
        asks.insert(
            id,
            Ask {
                text: r.get(1),
                reply: r.get(2),
                person: r.get(3),
                served_by: r.get(4),
                target: r.get(5),
                state: r.get::<_, Option<String>>(6).unwrap_or_else(|| "in".into()),
                proof: r.get::<_, Option<String>>(7).unwrap_or_else(|| "L1".into()),
                held: r
                    .get::<_, Option<String>>(10)
                    .and_then(|h| serde_json::from_str(&h).ok()),
                root: r.get(11),
            },
        );
    }
    let mut intentions: BTreeSet<String> = BTreeSet::new();
    if has_table(g, "spine_intentions").await? {
        if let Some((f, t)) = window {
            let rs = g
                .client()
                .query(
                    "SELECT intention_id FROM spine_intentions WHERE scope = $1 AND stopped_by = $2 AND stopped_at \
                     BETWEEN $3::timestamptz AND $4::timestamptz",
                    &[&world, &person, &f, &t],
                )
                .await?;
            intentions.extend(rs.iter().map(|r| r.get::<_, String>(0)));
        }
        if let Some(m) = marker {
            let rs = g
                .client()
                .query(
                    "SELECT intention_id FROM spine_intentions WHERE scope = $1 AND marker = $2 AND stopped_by = $3",
                    &[&world, &m, &person],
                )
                .await?;
            intentions.extend(rs.iter().map(|r| r.get::<_, String>(0)));
        }
    }
    for a in asks.values() {
        if let Some(h) = &a.held {
            if get(h, "tool").as_str() == Some("intent.stop") {
                if let Some(id) = s(get(get(h, "args"), "intention_id")) {
                    intentions.insert(id);
                }
            }
        }
    }
    let mut marker_ids: HashSet<String> = HashSet::new();
    if let Some(m) = marker {
        let rs = g
            .client()
            .query(
                "SELECT marker_id FROM spine_markers WHERE scope = $1 AND root = $2",
                &[&world, &m],
            )
            .await?;
        marker_ids.extend(rs.iter().map(|r| r.get::<_, String>(0)));
    }
    let firmware: HashSet<String> = g
        .client()
        .query(
            "SELECT did FROM spine_joins WHERE scope = $1 AND kind = 'firmware'",
            &[&world],
        )
        .await?
        .iter()
        .map(|r| r.get(0))
        .collect();
    let mut stands: HashMap<String, Value> = HashMap::new();
    for r in g
        .client()
        .query(
            "SELECT DISTINCT ON (did) did, placement FROM spine_joins WHERE scope = $1 ORDER BY did, join_id DESC",
            &[&world],
        )
        .await?
    {
        let did: String = r.get(0);
        let prof: Value = r
            .get::<_, Option<String>>(1)
            .and_then(|p| serde_json::from_str(&p).ok())
            .unwrap_or(json!({"cell": "local", "metal": "any"}));
        stands.insert(did, json!({"cell": prof["cell"], "metal": prof["metal"]}));
    }
    let mut iwords: HashMap<String, String> = HashMap::new();
    if !intentions.is_empty() {
        let ids: Vec<String> = intentions.iter().cloned().collect();
        for r in g
            .client()
            .query(
                "SELECT intention_id, words FROM spine_intentions WHERE intention_id = ANY($1)",
                &[&ids],
            )
            .await?
        {
            iwords.insert(r.get(0), r.get(1));
        }
    }
    let mut needles: Vec<String> = order.clone();
    needles.extend(intentions.iter().cloned());
    let mut mids: Vec<String> = marker_ids.iter().cloned().collect();
    mids.sort();
    needles.extend(mids);
    let mut rows_out: Vec<Value> = Vec::new();
    if !needles.is_empty() {
        let like: Vec<String> = needles.iter().map(|n| format!("%{n}%")).collect();
        let rs = g
            .client()
            .query(
                "SELECT outbox_id, body FROM spine_outbox WHERE convert_from(body, 'UTF8') LIKE ANY($1) ORDER BY \
                 outbox_id",
                &[&like],
            )
            .await?;
        for r in &rs {
            let oid: i64 = r.get(0);
            let body: Vec<u8> = r.get(1);
            let Ok(e) = envelope::decode(&body) else {
                continue;
            };
            let Some(kind) = e.get("type").and_then(Value::as_str).and_then(kind_of) else {
                continue;
            };
            if e.get("scope_path").and_then(Value::as_str) != Some(world) {
                continue;
            }
            if let Some(mut row) = row(
                &e,
                kind,
                oid,
                &asks,
                &intentions,
                &marker_ids,
                &firmware,
                &iwords,
            ) {
                let served = s(get(&row, "served_by"));
                row["placement"] = served
                    .and_then(|d| stands.get(&d).cloned())
                    .unwrap_or(Value::Null);
                rows_out.push(row);
            }
        }
    }
    rows_out.sort_by(|x, y| {
        let ax = get(x, "at").as_str().unwrap_or_default();
        let ay = get(y, "at").as_str().unwrap_or_default();
        ax.cmp(ay)
            .then(get(x, "_order").as_i64().cmp(&get(y, "_order").as_i64()))
    });
    let ids: BTreeSet<String> = rows_out
        .iter()
        .filter_map(|r| s(get(get(r, "marker"), "id")))
        .collect();
    let served = marker_words(g, world, &ids).await?;
    for r in rows_out.iter_mut() {
        if let Some(o) = r.as_object_mut() {
            o.remove("_order");
        }
        let mid = s(get(get(r, "marker"), "id"));
        r["marker_words"] = if truthy(get(r, "words_withheld")) {
            Value::Null
        } else {
            mid.and_then(|m| served.get(&m).cloned().flatten())
                .map(Value::String)
                .unwrap_or(Value::Null)
        };
    }
    Ok(seal(
        &rows_out,
        &Value::Object(scope),
        world,
        &envelope::now_iso(),
        signer,
    ))
}
