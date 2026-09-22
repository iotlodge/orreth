// PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp1, the bytes · 2026-09-22
//! The one true byte form (rule 6) — mirrors `orreth_spine.envelope.canonical`:
//!
//! ```python
//! json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")
//! ```
//!
//! byte for byte. Sorted keys at every depth come from serde_json's `Map`
//! (a `BTreeMap` — the workspace never enables `preserve_order`); the rest is
//! written here by hand, because serde_json's own serializer emits raw UTF-8
//! and ryu's float spelling is not Python's:
//!
//! - **strings** — Python's `ensure_ascii` escaper: `"` `\` and the five
//!   short escapes (`\n \r \t \b \f`), every other character outside
//!   `' '..='~'` as `\uXXXX` (lowercase hex; that includes DEL, 0x7f), and
//!   characters beyond the BMP as a UTF-16 surrogate pair. `/` is never
//!   escaped.
//! - **numbers** — integers plain; floats as Python's `repr`: the shortest
//!   round-trip digits, fixed notation while the decimal point sits in
//!   `-4 < decpt <= 16` (`1.5` · `0.0001` · `1000000000000000.0`), otherwise
//!   scientific with a signed two-digit exponent (`1e+16` · `1e-05`).
//! - `true` · `false` · `null`, compact separators, nothing else.

use serde_json::{Number, Value};
use std::fmt::Write as _;

/// The canonical bytes of a value — ASCII, so `Vec<u8>` and the string agree.
pub fn canonical(v: &Value) -> Vec<u8> {
    canonical_string(v).into_bytes()
}

/// The canonical form as a `String` (pure ASCII by construction).
pub fn canonical_string(v: &Value) -> String {
    let mut out = String::new();
    write_value(v, &mut out);
    out
}

fn write_value(v: &Value, out: &mut String) {
    match v {
        Value::Null => out.push_str("null"),
        Value::Bool(b) => out.push_str(if *b { "true" } else { "false" }),
        Value::Number(n) => write_number(n, out),
        Value::String(s) => write_escaped(s, out),
        Value::Array(items) => {
            out.push('[');
            for (i, item) in items.iter().enumerate() {
                if i > 0 {
                    out.push(',');
                }
                write_value(item, out);
            }
            out.push(']');
        }
        Value::Object(map) => {
            out.push('{');
            for (i, (k, val)) in map.iter().enumerate() {
                if i > 0 {
                    out.push(',');
                }
                write_escaped(k, out);
                out.push(':');
                write_value(val, out);
            }
            out.push('}');
        }
    }
}

/// A number as Python prints it: integers plain, floats as `repr(float)`.
pub fn write_number(n: &Number, out: &mut String) {
    if let Some(i) = n.as_i64() {
        let _ = write!(out, "{i}");
    } else if let Some(u) = n.as_u64() {
        let _ = write!(out, "{u}");
    } else if let Some(f) = n.as_f64() {
        out.push_str(&python_float_repr(f));
    } else {
        // serde_json on default features holds nothing else.
        out.push_str(&n.to_string());
    }
}

/// `repr(float)` — CPython's `float_repr_style == "short"`: the shortest digits
/// that round-trip, then Python's choice of fixed vs. exponent notation.
/// Finite values only (serde_json cannot hold `inf` or `nan`).
pub fn python_float_repr(f: f64) -> String {
    if f == 0.0 {
        return if f.is_sign_negative() {
            "-0.0".into()
        } else {
            "0.0".into()
        };
    }
    // Rust's `{:e}` gives the shortest round-trip digits in `d.ddde±x` form.
    let sci = format!("{:e}", f.abs());
    let (mantissa, exp) = sci
        .split_once('e')
        .expect("f64 `{:e}` always carries an exponent");
    let exp: i32 = exp.parse().expect("f64 `{:e}` exponent is an integer");
    let digits: String = mantissa.chars().filter(|c| *c != '.').collect();
    let decpt = exp + 1; // value = 0.<digits> × 10^decpt
    let mut out = String::new();
    if f.is_sign_negative() {
        out.push('-');
    }
    if decpt <= -4 || decpt > 16 {
        // Python: d[.ddd]e±XX — no ".0" is added in exponent form.
        out.push_str(&digits[..1]);
        if digits.len() > 1 {
            out.push('.');
            out.push_str(&digits[1..]);
        }
        let e = decpt - 1;
        let _ = write!(out, "e{}{:02}", if e < 0 { '-' } else { '+' }, e.abs());
    } else if decpt <= 0 {
        out.push_str("0.");
        for _ in 0..(-decpt) {
            out.push('0');
        }
        out.push_str(&digits);
    } else if (decpt as usize) >= digits.len() {
        out.push_str(&digits);
        for _ in 0..(decpt as usize - digits.len()) {
            out.push('0');
        }
        out.push_str(".0");
    } else {
        out.push_str(&digits[..decpt as usize]);
        out.push('.');
        out.push_str(&digits[decpt as usize..]);
    }
    out
}

/// Python's `ensure_ascii` string escaper, quotes included.
pub fn write_escaped(s: &str, out: &mut String) {
    out.push('"');
    for c in s.chars() {
        match c {
            '"' => out.push_str("\\\""),
            '\\' => out.push_str("\\\\"),
            '\n' => out.push_str("\\n"),
            '\r' => out.push_str("\\r"),
            '\t' => out.push_str("\\t"),
            '\u{08}' => out.push_str("\\b"),
            '\u{0c}' => out.push_str("\\f"),
            ' '..='~' => out.push(c),
            c => {
                let cp = c as u32;
                if cp > 0xFFFF {
                    let v = cp - 0x10000;
                    let _ = write!(
                        out,
                        "\\u{:04x}\\u{:04x}",
                        0xd800 + (v >> 10),
                        0xdc00 + (v & 0x3ff)
                    );
                } else {
                    let _ = write!(out, "\\u{:04x}", cp);
                }
            }
        }
    }
    out.push('"');
}

#[cfg(test)]
mod tests {
    //! Every expected string below was produced by CPython 3 (`json.dumps(...,
    //! sort_keys=True, separators=(",", ":"), ensure_ascii=True)` / `repr`) and
    //! pasted in — the Rust side is measured against the reference, never the reverse.
    use super::*;
    use serde_json::json;

    fn c(v: Value) -> String {
        canonical_string(&v)
    }

    #[test]
    fn empty_and_nested_unsorted() {
        assert_eq!(c(json!({})), "{}");
        assert_eq!(c(json!([])), "[]");
        assert_eq!(
            c(json!({"b": 1, "a": [2, {"z": "ü", "y": 3}], "c": {"d": {"f": 1, "e": 2}}})),
            r#"{"a":[2,{"y":3,"z":"\u00fc"}],"b":1,"c":{"d":{"e":2,"f":1}}}"#
        );
    }

    #[test]
    fn scalars() {
        assert_eq!(
            c(json!({"n": 1.5, "i": 10, "t": true, "f": false, "z": null, "s": "a b"})),
            r#"{"f":false,"i":10,"n":1.5,"s":"a b","t":true,"z":null}"#
        );
        assert_eq!(c(json!(-7)), "-7");
        assert_eq!(c(json!(18446744073709551615u64)), "18446744073709551615");
    }

    #[test]
    fn non_ascii_beyond_bmp_control_and_del() {
        assert_eq!(c(json!("naïve café")), r#""na\u00efve caf\u00e9""#);
        assert_eq!(c(json!("🥂")), r#""\ud83e\udd42""#); // beyond the BMP: a surrogate pair
        assert_eq!(c(json!("a\"b\\c/d")), r#""a\"b\\c/d""#); // `/` is never escaped
        assert_eq!(
            c(json!("\n\r\t\u{08}\u{0c}\u{01}\u{1f}")),
            r#""\n\r\t\b\f\u0001\u001f""#
        );
        assert_eq!(c(json!("\u{7f}")), r#""\u007f""#); // DEL is outside ' '..'~' — Python escapes it
        assert_eq!(c(json!("—·“”→")), r#""\u2014\u00b7\u201c\u201d\u2192""#);
        assert_eq!(
            c(json!({"ключ": "значение"})),
            r#"{"\u043a\u043b\u044e\u0447":"\u0437\u043d\u0430\u0447\u0435\u043d\u0438\u0435"}"#
        );
    }

    #[test]
    fn floats_as_python_repr() {
        // (value, repr) pairs from CPython 3.12.
        let cases: [(f64, &str); 16] = [
            (1.5, "1.5"),
            (0.0, "0.0"),
            (-0.0, "-0.0"),
            (1.0, "1.0"),
            (72.0, "72.0"),
            (0.1, "0.1"),
            (0.0001, "0.0001"),
            (0.00001, "1e-05"),
            (1e15, "1000000000000000.0"),
            (1e16, "1e+16"),
            (1.5e16, "1.5e+16"),
            (123456789.125, "123456789.125"),
            (-2.5e-7, "-2.5e-07"),
            (1e100, "1e+100"),
            (std::f64::consts::PI, "3.141592653589793"),
            (1e-300, "1e-300"),
        ];
        for (f, want) in cases {
            assert_eq!(python_float_repr(f), want, "repr({f})");
        }
        // Through serde_json: a parsed "1.0" stays a float and prints "1.0".
        let v: Value = serde_json::from_str(r#"{"x": 1.0, "y": 1, "z": 1e16}"#).unwrap();
        assert_eq!(c(v), r#"{"x":1.0,"y":1,"z":1e+16}"#);
    }

    #[test]
    fn keys_sort_bytewise_like_python() {
        // Python sorts str keys by code point; BTreeMap<String> sorts by UTF-8 bytes — the
        // same order (UTF-8 preserves code-point order).
        assert_eq!(
            c(json!({"b": 1, "B": 2, "a": 3, "_": 4, "é": 5, "1": 6})),
            r#"{"1":6,"B":2,"_":4,"a":3,"b":1,"\u00e9":5}"#
        );
    }
}
