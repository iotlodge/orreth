// PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp1, the bytes · 2026-09-22
// Amended: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp4, the loops: `repr_str` · 2026-09-23
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

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;

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
