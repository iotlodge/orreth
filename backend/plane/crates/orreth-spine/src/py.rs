// PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp1, the bytes · 2026-09-22
// Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp4, the loops: `repr_str` · 2026-09-23
// Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp6, the bodies' seam: `g_fmt` (`:g`) · `thousands` (`:,`) · `parse_iso_secs` · 2026-09-24
//! Python's idiom, where a law was written in it: truthiness (`or` · `if x`)
//! and `str(x)` over a JSON value. Kept in one place so every ported module
//! reads a record the way the reference does.

use crate::canonical::write_number;
use serde_json::Value;

/// Python truth over a JSON value: `None`, `False`, `0`, `0.0`, `""`, `[]`, `{}` are false.
pub fn truthy(v: &Value) -> bool {
    match v {
        Value::Null => false,
        Value::Bool(b) => *b,
        Value::Number(n) => n.as_f64().map(|f| f != 0.0).unwrap_or(true),
        Value::String(s) => !s.is_empty(),
        Value::Array(a) => !a.is_empty(),
        Value::Object(o) => !o.is_empty(),
    }
}

/// `row.get(key)` — a missing key reads as `None`.
pub fn get<'a>(row: &'a Value, key: &str) -> &'a Value {
    row.get(key).unwrap_or(&Value::Null)
}

/// `str(x)` for the scalars a record carries: a string as itself, a number as
/// Python prints it, `True`/`False`/`None`; containers as their canonical bytes.
pub fn python_str(v: &Value) -> String {
    match v {
        Value::String(s) => s.clone(),
        Value::Number(n) => {
            let mut out = String::new();
            write_number(n, &mut out);
            out
        }
        Value::Bool(true) => "True".into(),
        Value::Bool(false) => "False".into(),
        Value::Null => "None".into(),
        other => crate::canonical::canonical_string(other),
    }
}

/// Python's `repr()` of a str (`f"{name!r}"`): single quotes unless the text
/// holds a single quote and no double quote; backslash, the quote, `\n` `\r`
/// `\t` escaped; other control characters as `\xNN`; printable unicode kept.
pub fn repr_str(s: &str) -> String {
    let q = if s.contains('\'') && !s.contains('"') {
        '"'
    } else {
        '\''
    };
    let mut out = String::with_capacity(s.len() + 2);
    out.push(q);
    for c in s.chars() {
        match c {
            '\\' => out.push_str("\\\\"),
            '\n' => out.push_str("\\n"),
            '\r' => out.push_str("\\r"),
            '\t' => out.push_str("\\t"),
            c if c == q => {
                out.push('\\');
                out.push(c);
            }
            c if (c as u32) < 0x20 || c as u32 == 0x7f => {
                out.push_str(&format!("\\x{:02x}", c as u32))
            }
            c => out.push(c),
        }
    }
    out.push(q);
    out
}

/// `" ".join(text.split())` — whitespace folded to single spaces, ends trimmed.
pub fn fold_ws(text: &str) -> String {
    text.split_whitespace().collect::<Vec<_>>().join(" ")
}

/// Python's `format(x, "g")`: six significant digits, trailing zeros dropped,
/// exponent form below 1e-4 or from 1e6 (`3.0` → `3` · `3.5` → `3.5` · `1e-06`).
pub fn g_fmt(x: f64) -> String {
    if x == 0.0 {
        return "0".into();
    }
    if !x.is_finite() {
        return if x.is_nan() {
            "nan".into()
        } else if x > 0.0 {
            "inf".into()
        } else {
            "-inf".into()
        };
    }
    let sci = format!("{:.5e}", x.abs());
    let (mant, exp) = sci.split_once('e').expect("`{:e}` carries an exponent");
    let exp: i32 = exp.parse().expect("an integer exponent");
    let sign = if x < 0.0 { "-" } else { "" };
    if !(-4..6).contains(&exp) {
        let mant = mant.trim_end_matches('0').trim_end_matches('.');
        return format!(
            "{sign}{mant}e{}{:02}",
            if exp < 0 { '-' } else { '+' },
            exp.abs()
        );
    }
    let decimals = (5 - exp).max(0) as usize;
    let fixed = format!("{:.*}", decimals, x.abs());
    let fixed = if fixed.contains('.') {
        fixed
            .trim_end_matches('0')
            .trim_end_matches('.')
            .to_string()
    } else {
        fixed
    };
    format!("{sign}{fixed}")
}

/// Python's `f"{n:,}"` for an integer.
pub fn thousands(n: i64) -> String {
    let digits = n.abs().to_string();
    let mut out = String::new();
    for (i, c) in digits.chars().enumerate() {
        if i > 0 && (digits.len() - i).is_multiple_of(3) {
            out.push(',');
        }
        out.push(c);
    }
    if n < 0 {
        format!("-{out}")
    } else {
        out
    }
}

/// `datetime.fromisoformat(s.replace("Z", "+00:00"))` as unix seconds (UTC) —
/// a date alone reads as midnight; a naive time reads as UTC; an offset is
/// honoured. `None` when the calendar cannot read it.
pub fn parse_iso_secs(s: &str) -> Option<i64> {
    let s = s.trim();
    if s.is_empty() {
        return None;
    }
    let (date, rest) = match s.split_once('T').or_else(|| s.split_once(' ')) {
        Some((d, r)) => (d, Some(r)),
        None => (s, None),
    };
    let mut d = date.split('-');
    let year: i64 = d.next()?.parse().ok()?;
    let month: u32 = d.next()?.parse().ok()?;
    let day: u32 = d.next()?.parse().ok()?;
    if d.next().is_some() || !(1..=12).contains(&month) || !(1..=31).contains(&day) {
        return None;
    }
    let mut secs = crate::memory::days_from_civil(year, month, day) * 86_400;
    if let Some(rest) = rest {
        let rest = rest.trim_end_matches('Z');
        let (time, off) = match rest.rfind(['+', '-']) {
            Some(i) => (&rest[..i], Some(&rest[i..])),
            None => (rest, None),
        };
        let time: String = time
            .chars()
            .take_while(|c| c.is_ascii_digit() || *c == ':')
            .collect();
        let mut t = time.split(':');
        let h: i64 = t.next()?.parse().ok()?;
        let mi: i64 = t.next().and_then(|x| x.parse().ok()).unwrap_or(0);
        let sec: i64 = t.next().and_then(|x| x.parse().ok()).unwrap_or(0);
        secs += h * 3600 + mi * 60 + sec;
        if let Some(off) = off {
            let sign = if off.starts_with('-') { 1 } else { -1 };
            let mut o = off[1..].split(':');
            let oh: i64 = o.next()?.parse().ok()?;
            let om: i64 = o.next().and_then(|x| x.parse().ok()).unwrap_or(0);
            secs += sign * (oh * 3600 + om * 60);
        }
    }
    Some(secs)
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;

    #[test]
    fn g_is_pythons() {
        assert_eq!(g_fmt(3.0), "3");
        assert_eq!(g_fmt(3.5), "3.5");
        assert_eq!(g_fmt(0.15), "0.15");
        assert_eq!(g_fmt(15.0), "15");
        assert_eq!(g_fmt(1e-6), "1e-06");
        assert_eq!(g_fmt(1234567.0), "1.23457e+06");
        assert_eq!(g_fmt(200000.0), "200000");
        assert_eq!(g_fmt(0.0), "0");
        assert_eq!(thousands(200000), "200,000");
        assert_eq!(thousands(999), "999");
        assert_eq!(thousands(1000), "1,000");
        assert_eq!(parse_iso_secs("2026-10-01"), Some(1790812800));
        assert_eq!(parse_iso_secs("2026-10-01T00:00:00Z"), Some(1790812800));
        assert_eq!(
            parse_iso_secs("2026-10-01T02:00:00+02:00"),
            Some(1790812800)
        );
        assert_eq!(parse_iso_secs("yesterday-ish"), None);
    }

    #[test]
    fn repr_is_pythons() {
        assert_eq!(repr_str("asks left waiting"), "'asks left waiting'");
        assert_eq!(repr_str("a body's lease"), "\"a body's lease\"");
        assert_eq!(repr_str("it's \"both\""), "'it\\'s \"both\"'");
        assert_eq!(repr_str("tab\there"), "'tab\\there'");
    }

    #[test]
    fn truth_and_str() {
        for v in [
            json!(null),
            json!(false),
            json!(0),
            json!(0.0),
            json!(""),
            json!([]),
            json!({}),
        ] {
            assert!(!truthy(&v), "{v}");
        }
        for v in [
            json!(true),
            json!(1),
            json!(-0.5),
            json!("x"),
            json!([0]),
            json!({"a": null}),
        ] {
            assert!(truthy(&v), "{v}");
        }
        assert_eq!(python_str(&json!(0.0)), "0.0");
        assert_eq!(python_str(&json!(0)), "0");
        assert_eq!(python_str(&json!("s")), "s");
        assert_eq!(python_str(&json!(null)), "None");
        assert_eq!(fold_ws("  hello   there  "), "hello there");
    }
}
