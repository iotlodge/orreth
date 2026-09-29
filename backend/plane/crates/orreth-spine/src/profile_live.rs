// PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp8, the human profile on the ground (W58) · 2026-09-26
//! The human profile on the ground — `orreth_spine.profile`'s record half
//! ported (P7 sp8, W58): one table of provenance-labeled claims per person,
//! every change a FACT through the outbox with the chain (`[person, the
//! kernel]` for a told word, `[the kernel]` for an observation) and a marker
//! (an ACTION under the ask that carried the words, else an OBSERVATION under
//! the person's one profile root); a told PLACE geocoded once (Open-Meteo, no
//! key, blocking HTTP off the runtime) and the coordinates landed beside it as
//! an OBSERVED row + fact in the same transaction; forgetting a recorded
//! withdrawal, never a deletion; the portrait the person sees; the clock the
//! ground would use for them; the slice a routed ask CARRIES over the seam.

use crate::envelope::{self, Mint};
use crate::ground::Ground;
use crate::hash::content_hash;
use crate::markers_live;
use crate::outbox;
use crate::profile::{
    label_of, place_default, read_words, row_words, short, slice_words, FIELDS, GEOCODER, KERNEL,
    NOTHING_WORDS, OBSERVED, PROFILE_REF, TOLD, WITHDRAWN,
};
use crate::rail_error::RailError;
use crate::world::{isoformat, refused, RoadError, World};
use serde_json::{json, Value};
use std::time::{Duration, SystemTime};
use tokio_postgres::Transaction;

/// `profile.ensure_schema`, word for word (the seam's column rides on `spine_asks`).
pub use crate::schema::PROFILE_DDL;

const GEOCODE_TIMEOUT: Duration = Duration::from_secs(6);

fn row_json(r: &tokio_postgres::Row) -> Value {
    let iso = |t: Option<SystemTime>| t.map(isoformat);
    let by: String = r.get(4);
    let mut v = json!({
        "claim_id": r.get::<_, i64>(0), "person": r.get::<_, String>(1), "field": r.get::<_, String>(2),
        "value": r.get::<_, String>(3), "asserted_by": by, "state": r.get::<_, String>(5),
        "quoted": r.get::<_, Option<String>>(6), "evidence": r.get::<_, Option<String>>(7),
        "lat": r.get::<_, Option<f64>>(8), "lon": r.get::<_, Option<f64>>(9), "zone": r.get::<_, Option<String>>(10),
        "by_did": r.get::<_, String>(11), "marker": r.get::<_, Option<String>>(12), "ask": r.get::<_, Option<String>>(13),
        "at": iso(Some(r.get::<_, SystemTime>(14))), "withdrawn_at": iso(r.get::<_, Option<SystemTime>>(15)),
        "withdrawn_by": r.get::<_, Option<String>>(16),
    });
    v["label"] = json!(label_of(&by).unwrap_or("you told me"));
    v["words"] = json!(row_words(&v));
    v
}

/// The person's rows on this ground, newest first — live ones unless `withdrawn` asks for the whole record.
pub async fn claims(
    g: &Ground,
    scope: &str,
    person: &str,
    withdrawn: bool,
) -> Result<Vec<Value>, RoadError> {
    let sql = format!(
        "SELECT claim_id, person, field, value, asserted_by, state, quoted, evidence, lat, lon, zone, by_did, \
         marker, ask, at, withdrawn_at, withdrawn_by FROM spine_profile WHERE scope = $1 AND person = $2{} \
         ORDER BY claim_id DESC",
        if withdrawn { "" } else { " AND withdrawn_at IS NULL" }
    );
    let rows = g.client().query(&sql, &[&scope, &person]).await?;
    Ok(rows.iter().map(row_json).collect())
}

/// ONE origin per person for their profile: "jb keeps their own profile".
pub async fn profile_root(
    tx: &Transaction<'_>,
    scope: &str,
    person: &str,
) -> Result<String, RoadError> {
    let r#ref = format!("{PROFILE_REF}:{person}");
    if let Some(r) = tx
        .query_opt(
            "SELECT marker_id FROM spine_markers WHERE scope = $1 AND parent IS NULL AND kind = 'observation' \
             AND ref = $2 AND by_did = $3 ORDER BY at LIMIT 1",
            &[&scope, &r#ref, &person],
        )
        .await?
    {
        return Ok(r.get(0));
    }
    let mid = markers_live::new_id();
    let note = format!(
        "{} keeps their own profile — every word theirs, provenance-labeled",
        short(person)
    );
    markers_live::insert(
        tx,
        &mid,
        "observation",
        None,
        &r#ref,
        person,
        Some(&note),
        scope,
    )
    .await?;
    Ok(mid)
}

/// Open-Meteo's geocoder, no key: the first match for a told place —
/// `{lat, lon, zone, label}` — or None when nothing matched or the road was dark.
pub async fn geocode(place: &str) -> Option<Value> {
    let q = place.to_string();
    tokio::task::spawn_blocking(move || {
        let agent = ureq::AgentBuilder::new().timeout(GEOCODE_TIMEOUT).build();
        let resp = agent
            .get(GEOCODER)
            .query("name", &q)
            .query("count", "1")
            .query("language", "en")
            .query("format", "json")
            .call()
            .ok()?;
        let doc: Value = serde_json::from_str(&resp.into_string().ok()?).ok()?;
        let hit = doc["results"].as_array()?.first()?.clone();
        let lat = hit["latitude"].as_f64()?;
        let lon = hit["longitude"].as_f64()?;
        let label: Vec<String> = ["name", "admin1", "country"]
            .iter()
            .filter_map(|k| hit[*k].as_str().filter(|s| !s.is_empty()).map(str::to_string))
            .collect();
        Some(json!({"lat": lat, "lon": lon, "zone": hit["timezone"].as_str().filter(|z| !z.is_empty()),
                    "label": label.join(", ")}))
    })
    .await
    .ok()
    .flatten()
}

/// A person's own word lands TRUSTED as a fact; a told PLACE is geocoded
/// once (`geocode: true`) and the coordinates land beside it as an OBSERVED
/// row + fact in the same motion. Returns `{told, observed, words}`.
#[allow(clippy::too_many_arguments)] // the reference's keyword signature, kept whole
pub async fn tell(
    g: &mut Ground,
    w: &World,
    person: &str,
    field: &str,
    value: &str,
    quoted: Option<&str>,
    ask: Option<&str>,
    parent_marker: Option<&str>,
    geocode_it: bool,
) -> Result<Value, RoadError> {
    if !FIELDS.contains(&field) {
        return Err(refused(format!(
            "a profile word is one of {}, not {:?}",
            FIELDS.join(", "),
            field
        )));
    }
    let value = crate::py::fold_ws(value);
    if value.is_empty() {
        return Err(refused("an empty word says nothing about you"));
    }
    if field == "zone" {
        let known: i64 = g
            .client()
            .query_one(
                "SELECT count(*) FROM pg_timezone_names WHERE name = $1",
                &[&value],
            )
            .await?
            .get(0);
        if known == 0 {
            return Err(refused(format!(
                "{:?} is not a clock I know — a time zone reads like America/Denver",
                value
            )));
        }
    }
    let seen = if field == "place" && geocode_it {
        geocode(&value).await
    } else {
        None
    };
    let mid = markers_live::new_id();
    let kind = if ask.is_some() {
        "action"
    } else {
        "observation"
    };
    let e = Mint {
        kind: "event".into(),
        r#type: TOLD.into(),
        universe_id: w.scope.clone(),
        scope_path: w.scope.clone(),
        payload: json!({"ref": person, "by": person, "hash": content_hash(&json!({"field": field, "value": value})),
                        "field": field, "value": value, "asserted_by": "human", "state": "trusted"}),
        correlation_id: Some(ask.unwrap_or(person).to_string()),
        authority_chain: Some(vec![person.to_string(), KERNEL.to_string()]),
        aggregate: None,
        marker: None, // set below once the parent is known
    };
    // the parent (the person's root) is minted inside the transaction, so the marker is filled there
    let (scope, person_s, field_s, value_s, quoted_s, ask_s, parent_s, mid_s, seen_c) = (
        w.scope.clone(),
        person.to_string(),
        field.to_string(),
        value.clone(),
        quoted.map(str::to_string).unwrap_or_else(|| value.clone()),
        ask.map(str::to_string),
        parent_marker.map(str::to_string),
        mid.clone(),
        seen.clone(),
    );
    let mut told_row: Option<i64> = None;
    let mut obs_marker: Option<String> = None;
    {
        let told_row = &mut told_row;
        let obs_marker = &mut obs_marker;
        let tx = g
            .client_mut()
            .transaction()
            .await
            .map_err(RailError::Ground)?;
        let parent = match parent_s {
            Some(p) => p,
            None => profile_root(&tx, &scope, &person_s).await?,
        };
        let mut e = e.mint()?;
        e["marker"] = json!({"kind": kind, "id": mid_s, "parent": parent, "by": person_s});
        let raw = envelope::encode(&e)?;
        let note = format!(
            "{} told the ground their {field_s}: {value_s}",
            short(&person_s)
        );
        markers_live::insert(
            &tx,
            &mid_s,
            kind,
            Some(&parent),
            ask_s.as_deref().unwrap_or(&person_s),
            &person_s,
            Some(&note),
            &scope,
        )
        .await?;
        let r = tx
            .query_one(
                "INSERT INTO spine_profile (scope, person, field, value, asserted_by, state, quoted, by_did, marker, ask) \
                 VALUES ($1, $2, $3, $4, 'human', 'trusted', $5, $2, $6, $7) RETURNING claim_id",
                &[&scope, &person_s, &field_s, &value_s, &quoted_s, &mid_s, &ask_s],
            )
            .await?;
        *told_row = Some(r.get::<_, i64>(0));
        outbox::add_row(&tx, &raw, e["message_id"].as_str().unwrap_or_default()).await?;
        if let Some(sn) = seen_c.as_ref() {
            let omid = markers_live::new_id();
            let label = sn["label"]
                .as_str()
                .filter(|l| !l.is_empty())
                .unwrap_or(&value_s)
                .to_string();
            let (lat, lon) = (
                sn["lat"].as_f64().unwrap_or_default(),
                sn["lon"].as_f64().unwrap_or_default(),
            );
            let zone = sn["zone"].as_str().map(str::to_string);
            let onote = format!("{KERNEL} observed: {label} is at {lat:.2},{lon:.2}");
            markers_live::insert(
                &tx,
                &omid,
                "observation",
                Some(&mid_s),
                ask_s.as_deref().unwrap_or(&person_s),
                KERNEL,
                Some(&onote),
                &scope,
            )
            .await?;
            tx.execute(
                "INSERT INTO spine_profile (scope, person, field, value, asserted_by, state, evidence, lat, lon, zone, \
                 by_did, marker, ask) VALUES ($1, $2, 'place', $3, 'kernel', 'trusted', $4, $5, $6, $7, $8, $9, $10)",
                &[&scope, &person_s, &label, &value_s, &lat, &lon, &zone, &KERNEL, &omid, &ask_s],
            )
            .await?;
            let oe = Mint {
                kind: "event".into(),
                r#type: OBSERVED.into(),
                universe_id: scope.clone(),
                scope_path: scope.clone(),
                payload: json!({"ref": person_s, "hash": content_hash(&json!({"place": value_s, "lat": lat, "lon": lon})),
                                "field": "place", "value": label, "asserted_by": "kernel", "state": "trusted",
                                "evidence": value_s, "lat": lat, "lon": lon, "zone": zone, "by": KERNEL,
                                "source": "open-meteo geocoder"}),
                correlation_id: Some(ask_s.clone().unwrap_or_else(|| person_s.clone())),
                authority_chain: Some(vec![KERNEL.to_string()]),
                aggregate: None,
                marker: Some(json!({"kind": "observation", "id": omid, "parent": mid_s, "by": KERNEL})),
            }
            .mint()?;
            outbox::add_row(
                &tx,
                &envelope::encode(&oe)?,
                oe["message_id"].as_str().unwrap_or_default(),
            )
            .await?;
            *obs_marker = Some(omid);
        }
        tx.commit().await.map_err(RailError::Ground)?;
    }
    let told = json!({"claim_id": told_row, "field": field, "value": value, "asserted_by": "human",
                      "state": "trusted", "marker": mid});
    let mut words = format!("Noted, in your own words — {}.", row_words(&told));
    if field == "place" {
        match seen.as_ref() {
            Some(sn) => {
                words.push_str(&format!(
                    " I observed: {} is at {:.2},{:.2}",
                    sn["label"].as_str().unwrap_or(&value),
                    sn["lat"].as_f64().unwrap_or_default(),
                    sn["lon"].as_f64().unwrap_or_default()
                ));
                if let Some(z) = sn["zone"].as_str() {
                    words.push_str(&format!(", its clock {z}"));
                }
                words.push('.');
            }
            None => words.push_str(
                " I could not find its coordinates just now — the weather tool will say so until it can.",
            ),
        }
    }
    let observed = seen.map(|sn| {
        json!({"lat": sn["lat"], "lon": sn["lon"], "zone": sn["zone"], "label": sn["label"], "marker": obs_marker})
    });
    Ok(json!({"told": told, "observed": observed, "words": words}))
}

/// "Forget about me: …" — the matching live rows are marked withdrawn on the
/// person's say (a fact with the chain), never deleted; nothing matching
/// refuses in words.
pub async fn withdraw(
    g: &mut Ground,
    w: &World,
    person: &str,
    field: Option<&str>,
    topic: Option<&str>,
    ask: Option<&str>,
    parent_marker: Option<&str>,
) -> Result<Value, RoadError> {
    let live = claims(g, &w.scope, person, false).await?;
    let hit: Vec<&Value> = match (field, topic) {
        (Some(f), _) => live.iter().filter(|c| c["field"] == json!(f)).collect(),
        (None, Some(t)) => {
            let t = t.to_lowercase();
            live.iter()
                .filter(|c| {
                    crate::py::python_str(&c["value"]).to_lowercase().contains(&t)
                        || c["evidence"].as_str().unwrap_or_default().to_lowercase().contains(&t)
                })
                .collect()
        }
        _ => {
            return Err(refused(
                "say what to forget — 'forget about me: my place' or 'forget that I take my coffee black'",
            ))
        }
    };
    let what = field.or(topic).unwrap_or_default().to_string();
    if hit.is_empty() {
        return Err(refused(format!(
            "nothing in your profile says {:?} — nothing to forget",
            what
        )));
    }
    let ids: Vec<i64> = hit.iter().filter_map(|c| c["claim_id"].as_i64()).collect();
    let mid = markers_live::new_id();
    let kind = if ask.is_some() {
        "action"
    } else {
        "observation"
    };
    let (scope, person_s, ask_s, parent_s, mid_s, ids_c, what_c) = (
        w.scope.clone(),
        person.to_string(),
        ask.map(str::to_string),
        parent_marker.map(str::to_string),
        mid.clone(),
        ids.clone(),
        what.clone(),
    );
    let e = Mint {
        kind: "event".into(),
        r#type: WITHDRAWN.into(),
        universe_id: w.scope.clone(),
        scope_path: w.scope.clone(),
        payload: json!({"ref": person, "by": person, "hash": content_hash(&json!({"withdrawn": ids})),
                        "withdrawn": ids, "what": what}),
        correlation_id: Some(ask.unwrap_or(person).to_string()),
        authority_chain: Some(vec![person.to_string(), KERNEL.to_string()]),
        aggregate: None,
        marker: None,
    };
    {
        let tx = g
            .client_mut()
            .transaction()
            .await
            .map_err(RailError::Ground)?;
        let parent = match parent_s {
            Some(p) => p,
            None => profile_root(&tx, &scope, &person_s).await?,
        };
        let mut e = e.mint()?;
        e["marker"] = json!({"kind": kind, "id": mid_s, "parent": parent, "by": person_s});
        let raw = envelope::encode(&e)?;
        let note = format!(
            "{} withdrew {} word(s) about themselves: {what_c}",
            short(&person_s),
            ids_c.len()
        );
        markers_live::insert(
            &tx,
            &mid_s,
            kind,
            Some(&parent),
            ask_s.as_deref().unwrap_or(&person_s),
            &person_s,
            Some(&note),
            &scope,
        )
        .await?;
        tx.execute(
            "UPDATE spine_profile SET withdrawn_at = now(), withdrawn_by = $1, withdrawn_marker = $2 WHERE claim_id = ANY($3)",
            &[&person_s, &mid_s, &ids_c],
        )
        .await?;
        outbox::add_row(&tx, &raw, e["message_id"].as_str().unwrap_or_default()).await?;
        tx.commit().await.map_err(RailError::Ground)?;
    }
    Ok(json!({"withdrawn": ids, "what": what, "marker": mid,
              "words": format!("Forgotten on your word — {} thing(s) about {what} no longer read; the record keeps that you said them once.", ids.len())}))
}

/// What the person sees of themselves.
pub async fn portrait(g: &Ground, w: &World, person: &str) -> Result<Value, RoadError> {
    let rows = claims(g, &w.scope, person, false).await?;
    let named = |f: &str| -> Option<String> {
        rows.iter()
            .find(|c| c["asserted_by"] == json!("human") && c["field"] == json!(f))
            .map(|c| crate::py::python_str(&c["value"]))
    };
    let clock = zone_of(g, w, person).await?;
    Ok(json!({
        "person": person, "name": named("name"), "place": named("place"), "zone": named("zone"),
        "coordinates": place_default(&rows), "claims": rows, "words": slice_words(&rows), "clock": clock,
    }))
}

/// The person's clock as this ground knows it: told, else the told place's observed clock, else None.
pub async fn zone_of(g: &Ground, w: &World, person: &str) -> Result<Option<String>, RoadError> {
    let rows = claims(g, &w.scope, person, false).await?;
    if let Some(c) = rows
        .iter()
        .find(|c| c["field"] == json!("zone") && c["asserted_by"] == json!("human"))
    {
        return Ok(Some(crate::py::python_str(&c["value"])));
    }
    let p = place_default(&rows);
    Ok(p["zone"].as_str().map(str::to_string))
}

/// The slice a routed ask carries over the seam — or None when nothing was told.
pub async fn carry(g: &Ground, w: &World, person: &str) -> Result<Option<Value>, RoadError> {
    let rows = claims(g, &w.scope, person, false).await?;
    if rows.is_empty() {
        return Ok(None);
    }
    let zone = zone_of(g, w, person).await?;
    Ok(Some(
        json!({"words": slice_words(&rows), "place": place_default(&rows), "zone": zone}),
    ))
}

/// The door's one verb: the words read by the law — a tell, a forgetting, a read; nothing refuses in words.
pub async fn say(
    g: &mut Ground,
    w: &World,
    person: &str,
    text: &str,
    ask: Option<&str>,
    geocode_it: bool,
) -> Result<(u16, Value), RoadError> {
    let rw = read_words(text);
    match rw["act"].as_str() {
        Some("tell") => {
            let field = rw["field"].as_str().unwrap_or_default().to_string();
            let value = rw["value"].as_str().unwrap_or_default().to_string();
            let mut made = tell(
                g,
                w,
                person,
                &field,
                &value,
                Some(text.trim()),
                ask,
                None,
                geocode_it,
            )
            .await?;
            made["act"] = json!("tell");
            made["portrait"] = portrait(g, w, person).await?;
            Ok((201, made))
        }
        Some("forget") => {
            let mut made = withdraw(
                g,
                w,
                person,
                rw["field"].as_str(),
                rw["value"].as_str(),
                ask,
                None,
            )
            .await?;
            made["act"] = json!("forget");
            made["portrait"] = portrait(g, w, person).await?;
            Ok((201, made))
        }
        Some("read") => {
            let p = portrait(g, w, person).await?;
            let words = p["words"].clone();
            Ok((200, json!({"act": "read", "portrait": p, "words": words})))
        }
        _ => Err(refused(NOTHING_WORDS)),
    }
}
