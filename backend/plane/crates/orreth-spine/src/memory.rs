// PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp5, memory and the export · 2026-09-24
//! `orreth.memory/1` — the pure half of `orreth_spine.store` and `digest`
//! (canon 0003 · MEM-1..MEM-6): recall's grammar (OR-shaped terms, the
//! word-match fallback), the landed and purged facts' payloads and bytes
//! for a fixed id and clock, and the short version's TEXT from its parts —
//! byte-equal to the Python reference (fixture `memory-v0.json`). The
//! ground's side (the sibling law, the intervals, the projection) is
//! `store.rs` and `digest.rs`, behind the rails.

use crate::envelope::SPECVERSION;
use crate::hash::content_hash;
use regex::Regex;
use serde_json::{json, Value};
use std::sync::OnceLock;

pub const MEMORY_EVENT: &str = "orreth.memory.landed.v1";
pub const PURGE_EVENT: &str = "orreth.memory.purged.v1";
pub const DIGEST_EVENT: &str = "orreth.digest.landed.v1";
pub const UNDERSTANDING: &str = "tsvector:english";
pub const HEAD: usize = 120;

fn word_re() -> &'static Regex {
    static RE: OnceLock<Regex> = OnceLock::new();
    RE.get_or_init(|| Regex::new(r"[A-Za-z0-9]+").unwrap())
}

/// The recall query in the projection's grammar: OR-shaped — any word of the
/// ask may find a memory, and the memory holding MORE of them ranks first
/// (websearch ANDs by default); a query with no word passes through whole.
pub fn search_terms(query: &str) -> String {
    let words: Vec<&str> = word_re().find_iter(query).map(|m| m.as_str()).collect();
    if words.is_empty() {
        query.to_string()
    } else {
        words.join(" or ")
    }
}

/// The word-match fallback's needles: the query's words of four letters or
/// more, the first six; the whole query when none.
pub fn fallback_words(query: &str) -> Vec<String> {
    let words: Vec<String> = word_re()
        .find_iter(query)
        .map(|m| m.as_str())
        .filter(|w| w.len() >= 4)
        .take(6)
        .map(str::to_string)
        .collect();
    if words.is_empty() {
        vec![query.to_string()]
    } else {
        words
    }
}

/// `orreth.memory.landed.v1`'s payload: the ref, the hash, the hash it supersedes.
pub fn landed_payload(namespace: &str, key: &str, hash: &str, supersedes: Option<&str>) -> Value {
    let mut p = json!({"ref": format!("{namespace}/{key}"), "hash": hash});
    if let Some(s) = supersedes.filter(|s| !s.is_empty()) {
        p["supersedes"] = json!(s);
    }
    p
}

/// The tombstone's payload (MEM-5): every version's hash, never the words,
/// and one hash over them all (`content_hash(",".join(hashes))`).
pub fn purge_payload(namespace: &str, key: &str, hashes: &[String]) -> Value {
    json!({
        "ref": format!("{namespace}/{key}"),
        "hashes": hashes,
        "hash": content_hash(&Value::String(hashes.join(","))),
    })
}

/// A memory fact for a fixed id and clock — the chain is the author's alone.
pub fn fact(
    r#type: &str,
    scope: &str,
    payload: Value,
    by: &str,
    correlation: Option<&str>,
    message_id: &str,
    occurred_at: &str,
) -> Value {
    let mut e = json!({
        "specversion": SPECVERSION,
        "message_id": message_id,
        "message_kind": "event",
        "type": r#type,
        "universe_id": scope,
        "scope_path": scope,
        "occurred_at": occurred_at,
        "payload": payload,
        "authority_chain": [by],
    });
    if let Some(c) = correlation {
        e["correlation_id"] = json!(c);
    }
    e
}

/// `digest._head`: the words folded to one line, cut at `n` with an ellipsis.
pub fn head(text: &str, n: usize) -> String {
    let folded: String = text.split_whitespace().collect::<Vec<_>>().join(" ");
    let chars: Vec<char> = folded.chars().collect();
    if chars.len() <= n {
        return folded;
    }
    let cut: String = chars[..n - 1].iter().collect();
    format!("{}…", cut.trim_end())
}

/// One ask as the digest reads it: (ask_id, text, reply, status, asked_at, replied_at, who).
pub struct DigestAsk {
    pub ask_id: String,
    pub text: String,
    pub reply: Option<String>,
    pub status: String,
    pub asked_at: Civil,
    pub replied_at: Option<Civil>,
    pub who: String,
}

/// A civil time (UTC — the ground's clock, the session the Python spine formats in).
#[derive(Clone, Copy, Debug)]
pub struct Civil {
    pub year: i64,
    pub month: u32,
    pub day: u32,
    pub hour: u32,
    pub minute: u32,
    pub second: u32,
}

impl Civil {
    /// Parse `YYYY-MM-DDTHH:MM[:SS[.ffffff]][+00:00|Z]` (the fixture's naive ISO times).
    pub fn parse(iso: &str) -> Option<Civil> {
        let s = iso.trim();
        let (date, rest) = s.split_once('T').or_else(|| s.split_once(' '))?;
        let mut d = date.split('-');
        let year: i64 = d.next()?.parse().ok()?;
        let month: u32 = d.next()?.parse().ok()?;
        let day: u32 = d.next()?.parse().ok()?;
        let time: String = rest
            .chars()
            .take_while(|c| c.is_ascii_digit() || *c == ':')
            .collect();
        let mut t = time.split(':');
        let hour: u32 = t.next()?.parse().ok()?;
        let minute: u32 = t.next()?.parse().ok()?;
        let second: u32 = t.next().and_then(|x| x.parse().ok()).unwrap_or(0);
        Some(Civil {
            year,
            month,
            day,
            hour,
            minute,
            second,
        })
    }

    /// From a unix time in seconds (UTC).
    pub fn from_unix(secs: i64) -> Civil {
        let (year, month, day) = civil_from_days(secs.div_euclid(86_400));
        let sod = secs.rem_euclid(86_400) as u32;
        Civil {
            year,
            month,
            day,
            hour: sod / 3600,
            minute: sod % 3600 / 60,
            second: sod % 60,
        }
    }

    /// Python's `%a` — the weekday's short name.
    pub fn weekday(&self) -> &'static str {
        let days = days_from_civil(self.year, self.month, self.day);
        // 1970-01-01 was a Thursday
        const NAMES: [&str; 7] = ["Thu", "Fri", "Sat", "Sun", "Mon", "Tue", "Wed"];
        NAMES[days.rem_euclid(7) as usize]
    }

    /// `%b` — the month's short name.
    pub fn month_name(&self) -> &'static str {
        const NAMES: [&str; 12] = [
            "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
        ];
        NAMES[(self.month.clamp(1, 12) - 1) as usize]
    }

    /// `strftime('%a %b %d %H:%M')`.
    pub fn opened_words(&self) -> String {
        format!(
            "{} {} {:02} {:02}:{:02}",
            self.weekday(),
            self.month_name(),
            self.day,
            self.hour,
            self.minute
        )
    }

    /// `strftime('%H:%M')`.
    pub fn hhmm(&self) -> String {
        format!("{:02}:{:02}", self.hour, self.minute)
    }
}

/// Howard Hinnant's civil-from-days (proleptic Gregorian, UTC).
pub fn civil_from_days(z: i64) -> (i64, u32, u32) {
    let z = z + 719_468;
    let era = z.div_euclid(146_097);
    let doe = z.rem_euclid(146_097);
    let yoe = (doe - doe / 1460 + doe / 36_524 - doe / 146_096) / 365;
    let y = yoe + era * 400;
    let doy = doe - (365 * yoe + yoe / 4 - yoe / 100);
    let mp = (5 * doy + 2) / 153;
    let d = (doy - (153 * mp + 2) / 5 + 1) as u32;
    let m = if mp < 10 { mp + 3 } else { mp - 9 } as u32;
    (if m <= 2 { y + 1 } else { y }, m, d)
}

/// Days since 1970-01-01 for a civil date.
pub fn days_from_civil(y: i64, m: u32, d: u32) -> i64 {
    let y = if m <= 2 { y - 1 } else { y };
    let era = y.div_euclid(400);
    let yoe = y.rem_euclid(400);
    let mp = if m > 2 { m - 3 } else { m + 9 } as i64;
    let doy = (153 * mp + 2) / 5 + d as i64 - 1;
    let doe = yoe * 365 + yoe / 4 - yoe / 100 + doy;
    era * 146_097 + doe - 719_468
}

/// `digest.compose_lines`: the short version's TEXT from its parts — the
/// session's head line, every ask's head with who replied and when, the
/// words acquired in the span. Returns (body, sources).
pub fn digest_lines(
    session_id: &str,
    title: Option<&str>,
    opened: Civil,
    asks: &[DigestAsk],
    memories: &[(String, String, String)],
) -> (String, Vec<String>) {
    let mut sources: Vec<String> = asks.iter().map(|a| a.ask_id.clone()).collect();
    let short: String = session_id.chars().skip(4).take(6).collect();
    let mut lines = vec![format!(
        "session {short}{} · opened {} · {} ask{}",
        title.map(|t| format!(" — {t}")).unwrap_or_default(),
        opened.opened_words(),
        asks.len(),
        if asks.len() == 1 { "" } else { "s" }
    )];
    for a in asks {
        lines.push(format!(
            "· {} asked: {}",
            a.asked_at.hhmm(),
            head(&a.text, HEAD)
        ));
        if a.status == "replied" && a.reply.as_deref().is_some_and(|r| !r.is_empty()) {
            lines.push(format!(
                "  {} replied ({}): {}",
                a.who,
                a.replied_at.map(|t| t.hhmm()).unwrap_or_else(|| "—".into()),
                head(a.reply.as_deref().unwrap_or(""), HEAD)
            ));
        } else if a.status != "received" {
            lines.push(format!("  {}", a.status));
        }
    }
    for (ns, key, body) in memories {
        sources.push(format!("{ns}/{key}"));
        lines.push(format!("· acquired [{ns}/{key}]: {}", head(body, HEAD)));
    }
    (lines.join("\n"), sources)
}

/// `orreth.digest.landed.v1`'s payload.
pub fn digest_payload(digest_id: &str, body: &str, session: &str, sources: usize) -> Value {
    json!({"ref": digest_id, "hash": content_hash(&Value::String(body.into())), "session": session, "sources": sources})
}
