// PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp3, the ask road · 2026-09-22
// Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp4, the loops: the kernel HOLDS its own act (`hold_kernel_act`) · 2026-09-23
//! The proof ladder on the ground — mirrors the live half of
//! `orreth_spine.proof` (canon 0001 P12 · 0005 P6 sp1): the authenticator
//! enrolled once through the door and confirmed by its first code (re-enrolling
//! is grave — the OLD code first); the masters declared on the ground and
//! seeded from `SPINE_MASTERS`; every proof offered a recorded fact with its
//! event; the judgement at the door (L2 the click · L3-code the asker's own
//! code · L3-master a declared master, never the asker); and the ONE face for
//! every refusal (covenant rule 4) — three wrong proofs REST the act.
//! The tables are the Python spine's, word for word (`schema::PROOF_DDL`).

use crate::envelope::{self, Mint};
use crate::ground::Ground;
use crate::hash::content_hash;
use crate::outbox;
use crate::proof::{self, DRIFT};
use crate::rail_error::RailError;
use crate::world::{token_hex, RoadError, World};
use base64::Engine;
use serde_json::{json, Value};
use std::io::Write;
use std::time::{SystemTime, UNIX_EPOCH};

pub const AUTHENTICATOR_ENROLLED: &str = "orreth.authenticator.enrolled.v1";
pub const AUTHENTICATOR_CONFIRMED: &str = "orreth.authenticator.confirmed.v1";
pub const MASTER_DECLARED: &str = "orreth.master.declared.v1";
pub const PROOF_ATTEMPT: &str = "orreth.proof.attempt.v1";

/// The unix time now, as the code's clock.
pub fn now_unix() -> f64 {
    SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .map(|d| d.as_secs_f64())
        .unwrap_or(0.0)
}

fn event(w: &World, typ: &str, r#ref: &str, extra: Value, by: &str) -> Result<Value, RoadError> {
    let mut payload = json!({"ref": r#ref, "hash": "sha256:-"});
    if let Some(o) = extra.as_object() {
        for (k, v) in o {
            payload[k] = v.clone();
        }
    }
    Ok(Mint {
        kind: "event".into(),
        r#type: typ.into(),
        universe_id: w.scope.clone(),
        scope_path: w.scope.clone(),
        payload,
        correlation_id: Some(r#ref.to_string()),
        authority_chain: Some(vec![by.to_string()]),
        ..Default::default()
    }
    .mint()?)
}

// ---- the authenticator ------------------------------------------------------------

/// RFC 4648 base32 of twenty random bytes, unpadded — `mint_secret`.
pub fn mint_secret() -> String {
    const ALPHABET: &[u8; 32] = b"ABCDEFGHIJKLMNOPQRSTUVWXYZ234567";
    let hex = token_hex(20);
    let bytes: Vec<u8> = (0..hex.len())
        .step_by(2)
        .map(|i| u8::from_str_radix(&hex[i..i + 2], 16).unwrap())
        .collect();
    let mut out = String::new();
    let (mut buffer, mut bits) = (0u32, 0u32);
    for b in bytes {
        buffer = (buffer << 8) | b as u32;
        bits += 8;
        while bits >= 5 {
            bits -= 5;
            out.push(ALPHABET[((buffer >> bits) & 31) as usize] as char);
        }
    }
    if bits > 0 {
        out.push(ALPHABET[((buffer << (5 - bits)) & 31) as usize] as char);
    }
    out
}

/// The QR as a PNG data URI — the matrix drawn by `qrcode`, the PNG written
/// here by hand (8-bit grey, one filter-less row per module row, zlib), as the
/// Python does with `zlib` + `struct`. `None` when the text is too long for a QR.
pub fn qr_png_data_uri(text: &str, scale: usize, border: usize) -> Option<String> {
    let code = qrcode::QrCode::new(text.as_bytes()).ok()?;
    let width = code.width();
    let colors = code.to_colors();
    let n = width + 2 * border;
    let w = n * scale;
    let mut rows: Vec<u8> = Vec::with_capacity((w + 1) * w);
    for r in 0..n {
        let mut line = Vec::with_capacity(w + 1);
        line.push(0u8);
        for c in 0..n {
            let dark = r >= border
                && c >= border
                && r - border < width
                && c - border < width
                && colors[(r - border) * width + (c - border)] == qrcode::Color::Dark;
            let px = if dark { 0u8 } else { 255u8 };
            line.extend(std::iter::repeat_n(px, scale));
        }
        for _ in 0..scale {
            rows.extend_from_slice(&line);
        }
    }
    let mut z = flate2::write::ZlibEncoder::new(Vec::new(), flate2::Compression::best());
    z.write_all(&rows).ok()?;
    let idat = z.finish().ok()?;
    fn chunk(tag: &[u8; 4], body: &[u8]) -> Vec<u8> {
        let mut out = Vec::with_capacity(body.len() + 12);
        out.extend_from_slice(&(body.len() as u32).to_be_bytes());
        out.extend_from_slice(tag);
        out.extend_from_slice(body);
        let mut crc = flate2::Crc::new();
        crc.update(tag);
        crc.update(body);
        out.extend_from_slice(&crc.sum().to_be_bytes());
        out
    }
    let mut ihdr = Vec::new();
    ihdr.extend_from_slice(&(w as u32).to_be_bytes());
    ihdr.extend_from_slice(&(w as u32).to_be_bytes());
    ihdr.extend_from_slice(&[8, 0, 0, 0, 0]);
    let mut png = b"\x89PNG\r\n\x1a\n".to_vec();
    png.extend(chunk(b"IHDR", &ihdr));
    png.extend(chunk(b"IDAT", &idat));
    png.extend(chunk(b"IEND", &[]));
    Some(format!(
        "data:image/png;base64,{}",
        base64::engine::general_purpose::STANDARD.encode(png)
    ))
}

pub async fn active_secret(
    g: &Ground,
    scope: &str,
    person: &str,
) -> Result<Option<String>, RoadError> {
    let row = g
        .client()
        .query_opt(
            "SELECT secret FROM spine_authenticators WHERE person = $1 AND scope = $2 AND \
             confirmed_at IS NOT NULL AND retired_at IS NULL ORDER BY auth_id DESC LIMIT 1",
            &[&person, &scope],
        )
        .await?;
    Ok(row.map(|r| r.get(0)))
}

pub async fn enrolled(g: &Ground, scope: &str, person: &str) -> Result<bool, RoadError> {
    Ok(active_secret(g, scope, person).await?.is_some())
}

/// Mint a secret for the person: the URI and the QR come back once, the row
/// waits for its first code. A person who already holds a confirmed
/// authenticator is re-enrolling — grave — and must give the OLD code here,
/// or the one face answers.
pub async fn enroll(
    g: &mut Ground,
    w: &World,
    person: &str,
    code: Option<&str>,
) -> Result<Value, RoadError> {
    let old = active_secret(g, &w.scope, person).await?;
    if let Some(old) = &old {
        if !proof::verify(old, code, now_unix(), DRIFT) {
            return Err(RoadError::NotConfirmed { rest: false });
        }
    }
    let secret = mint_secret();
    let e = event(
        w,
        AUTHENTICATOR_ENROLLED,
        person,
        json!({"re_enrolled": old.is_some()}),
        person,
    )?;
    let raw = envelope::encode(&e)?;
    let mid = e["message_id"].as_str().unwrap_or_default().to_string();
    let (p, sc, s) = (person.to_string(), w.scope.clone(), secret.clone());
    outbox::commit_with_outbox(g, &raw, &mid, None, async move |tx| {
        tx.execute(
            "UPDATE spine_authenticators SET retired_at = now() WHERE person = $1 AND scope = $2 \
             AND confirmed_at IS NULL AND retired_at IS NULL",
            &[&p, &sc],
        )
        .await?;
        tx.execute(
            "INSERT INTO spine_authenticators (person, secret, scope) VALUES ($1, $2, $3)",
            &[&p, &s, &sc],
        )
        .await?;
        Ok(())
    })
    .await?;
    let uri = proof::otpauth_uri(person, &secret, "Orreth");
    Ok(json!({
        "person": person, "uri": uri, "secret": secret,
        "qr": qr_png_data_uri(&uri, 6, 2), "re_enrolled": old.is_some(),
    }))
}

/// The first code confirms the pending secret; an older confirmed one
/// retires in the same transaction. No pending row, wrong code: one face.
pub async fn confirm_enrollment(
    g: &mut Ground,
    w: &World,
    person: &str,
    code: Option<&str>,
) -> Result<Value, RoadError> {
    let row = g
        .client()
        .query_opt(
            "SELECT auth_id, secret FROM spine_authenticators WHERE person = $1 AND scope = $2 \
             AND confirmed_at IS NULL AND retired_at IS NULL ORDER BY auth_id DESC LIMIT 1",
            &[&person, &w.scope],
        )
        .await?;
    let Some(row) = row else {
        return Err(RoadError::NotConfirmed { rest: false });
    };
    let (auth_id, secret): (i64, String) = (row.get(0), row.get(1));
    if !proof::verify(&secret, code, now_unix(), DRIFT) {
        return Err(RoadError::NotConfirmed { rest: false });
    }
    let e = event(w, AUTHENTICATOR_CONFIRMED, person, json!({}), person)?;
    let raw = envelope::encode(&e)?;
    let mid = e["message_id"].as_str().unwrap_or_default().to_string();
    let (p, sc) = (person.to_string(), w.scope.clone());
    outbox::commit_with_outbox(g, &raw, &mid, None, async move |tx| {
        tx.execute(
            "UPDATE spine_authenticators SET retired_at = now() WHERE person = $1 AND scope = $2 \
             AND confirmed_at IS NOT NULL AND retired_at IS NULL AND auth_id <> $3",
            &[&p, &sc, &auth_id],
        )
        .await?;
        tx.execute(
            "UPDATE spine_authenticators SET confirmed_at = now() WHERE auth_id = $1",
            &[&auth_id],
        )
        .await?;
        Ok(())
    })
    .await?;
    Ok(json!({"person": person, "enrolled": true}))
}

// ---- the masters --------------------------------------------------------------------

pub async fn masters(g: &Ground, scope: &str) -> Result<Vec<String>, RoadError> {
    let rows = g
        .client()
        .query(
            "SELECT person FROM spine_masters WHERE scope = $1 ORDER BY declared_at, person",
            &[&scope],
        )
        .await?;
    Ok(rows.iter().map(|r| r.get(0)).collect())
}

pub async fn is_master(g: &Ground, scope: &str, person: &str) -> Result<bool, RoadError> {
    Ok(masters(g, scope).await?.iter().any(|m| m == person))
}

/// A named second person, declared on the ground with its event; a master
/// already standing is left as it is (`false`).
pub async fn declare_master(
    g: &mut Ground,
    w: &World,
    person: &str,
    by: &str,
) -> Result<bool, RoadError> {
    if person.is_empty() || is_master(g, &w.scope, person).await? {
        return Ok(false);
    }
    let e = event(w, MASTER_DECLARED, person, json!({"declared_by": by}), by)?;
    let raw = envelope::encode(&e)?;
    let mid = e["message_id"].as_str().unwrap_or_default().to_string();
    let (p, b, sc) = (person.to_string(), by.to_string(), w.scope.clone());
    outbox::commit_with_outbox(g, &raw, &mid, None, async move |tx| {
        tx.execute(
            "INSERT INTO spine_masters (person, declared_by, scope) VALUES ($1, $2, $3) ON \
             CONFLICT DO NOTHING",
            &[&p, &b, &sc],
        )
        .await?;
        Ok(())
    })
    .await?;
    Ok(true)
}

/// The `SPINE_MASTERS` dial (comma-separated person DIDs) declares this
/// world's masters at birth; returns the ones declared now.
pub async fn seed_masters(g: &mut Ground, w: &World, dial: &str) -> Result<Vec<String>, RoadError> {
    let mut made = Vec::new();
    for p in dial.split(',') {
        let p = p.trim();
        if !p.is_empty() && declare_master(g, w, p, "the SPINE_MASTERS dial").await? {
            made.push(p.to_string());
        }
    }
    Ok(made)
}

// ---- the judgement at the door ------------------------------------------------------

/// Every proof offered is a recorded fact with its event; returns how many
/// have been refused on this ask so far (this one included).
pub async fn record_attempt(
    g: &mut Ground,
    w: &World,
    ask_id: &str,
    by: &str,
    level: &str,
    ok: bool,
) -> Result<i64, RoadError> {
    let e = event(
        w,
        PROOF_ATTEMPT,
        ask_id,
        json!({"level": level, "ok": ok}),
        by,
    )?;
    let raw = envelope::encode(&e)?;
    let mid = e["message_id"].as_str().unwrap_or_default().to_string();
    let (a, b, l) = (ask_id.to_string(), by.to_string(), level.to_string());
    outbox::commit_with_outbox(g, &raw, &mid, None, async move |tx| {
        tx.execute(
            "INSERT INTO spine_proof_attempts (ask_id, by_did, level, ok) VALUES ($1, $2, $3, $4)",
            &[&a, &b, &l, &ok],
        )
        .await?;
        Ok(())
    })
    .await?;
    let n: i64 = g
        .client()
        .query_one(
            "SELECT count(*) FROM spine_proof_attempts WHERE ask_id = $1 AND NOT ok",
            &[&ask_id],
        )
        .await?
        .get(0);
    Ok(n)
}

/// The door's judgement of a proof for a held act. L2 needs no proof beyond
/// the click. L3-code: the asker's own authenticator, the code given.
/// L3-master: `by` is a declared master and never the asker. Refused →
/// recorded, then the ONE face (with the inward `rest` when it was the third).
pub async fn judge(
    g: &mut Ground,
    w: &World,
    ask_id: &str,
    level: &str,
    asker: &str,
    by: &str,
    code: Option<&str>,
) -> Result<(), RoadError> {
    let ok = match level {
        "L3-code" => match active_secret(g, &w.scope, asker).await? {
            Some(secret) => proof::verify(&secret, code, now_unix(), DRIFT),
            None => false,
        },
        "L3-master" => !by.is_empty() && by != asker && is_master(g, &w.scope, by).await?,
        _ => return Ok(()),
    };
    if !ok {
        let wrong = record_attempt(g, w, ask_id, by, level, false).await?;
        return Err(RoadError::NotConfirmed {
            rest: wrong >= proof::REST_AFTER,
        });
    }
    record_attempt(g, w, ask_id, by, level, true).await?;
    Ok(())
}

/// The proofs offered on an ask, in order — `(by, level, ok)`.
pub async fn attempts(g: &Ground, ask_id: &str) -> Result<Vec<(String, String, bool)>, RoadError> {
    let rows = g
        .client()
        .query(
            "SELECT by_did, level, ok FROM spine_proof_attempts WHERE ask_id = $1 ORDER BY \
             attempt_id",
            &[&ask_id],
        )
        .await?;
    Ok(rows
        .iter()
        .map(|r| (r.get(0), r.get(1), r.get(2)))
        .collect())
}

/// An act the KERNEL itself holds (no resident serves it — stopping one of
/// the kernel's intentions, retiring a service): the ask row is born held,
/// with its CONFIRM_NEEDED and its marker in one transaction. No
/// `ask.received` is filed — the dispatcher must never hand this to a
/// resident. Returns the held ask's id. `proof.hold_kernel_act`, law for law.
#[allow(clippy::too_many_arguments)]
pub async fn hold_kernel_act(
    g: &mut Ground,
    w: &World,
    text: &str,
    person: &str,
    tool: &str,
    args: Value,
    level: &str,
    session: Option<&str>,
    cls: &str,
    needs_code: bool,
) -> Result<String, RoadError> {
    use crate::asks::CONFIRM_NEEDED;
    use crate::markers_live;
    let ask_id = format!("ask_{}", token_hex(8));
    let mid = markers_live::new_id();
    let marker = json!({"kind": "objective", "id": mid, "parent": Value::Null, "by": person});
    let needs_code = needs_code && level == "L3-master"; // L3-code IS the code; the flag
    let mut held = json!({"tool": tool, "args": args, "class": cls, "level": level});
    if needs_code {
        held["needs_code"] = json!(true); // W5: the asker's code, then the master's click
        held["code_ok"] = json!(false);
    }
    let mut chars = text.chars();
    let capital = match chars.next() {
        Some(c) => c.to_uppercase().collect::<String>() + chars.as_str(),
        None => String::new(),
    };
    let question = crate::proof::question_for(level, &capital, needs_code);
    let mut payload = json!({"ref": ask_id, "hash": content_hash(&Value::String(text.into())),
                             "tool": tool, "class": cls, "level": level});
    if needs_code {
        payload["needs_code"] = json!(true);
    }
    let n = Mint {
        kind: "event".into(),
        r#type: CONFIRM_NEEDED.into(),
        universe_id: w.scope.clone(),
        scope_path: w.scope.clone(),
        payload,
        correlation_id: Some(ask_id.clone()),
        authority_chain: Some(vec![person.to_string(), crate::proof::KERNEL.to_string()]),
        aggregate: Some(json!({"type": "ask", "id": ask_id, "sequence": 1})),
        marker: Some(marker),
    }
    .mint()?;
    let raw = envelope::encode(&n)?;
    let message_id = n["message_id"].as_str().unwrap_or_default().to_string();
    let (scope, person2, ask2, mid2, text2, held_text) = (
        w.scope.clone(),
        person.to_string(),
        ask_id.clone(),
        mid.clone(),
        text.to_string(),
        held.to_string(),
    );
    let session = session.map(str::to_string);
    outbox::commit_with_outbox(g, &raw, &message_id, None, async move |tx| {
        markers_live::insert(tx, &mid2, "objective", None, &ask2, &person2, None, &scope)
            .await
            .map_err(|e| RailError::Refused(e.to_string()))?;
        tx.execute(
            "INSERT INTO spine_asks (ask_id, text, person, status, reply, served_by, held, scope, \
             session, marker) VALUES ($1, $2, $3, 'awaiting-confirm', $4, $5, $6, $7, $8, $9)",
            &[
                &ask2,
                &text2,
                &person2,
                &question,
                &crate::proof::KERNEL,
                &held_text,
                &scope,
                &session,
                &mid2,
            ],
        )
        .await?;
        Ok(())
    })
    .await?;
    Ok(ask_id)
}
