// PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch row 4, re-base sp1: the mark and markers/kinds doors cross — the kind-name law, pure · 2026-09-28
//! The markers' pure laws — the half of `orreth_spine.markers` that needs no
//! ground (the ground half is `markers_live`). Fixture `markers-v0.json`.

/// `markers.kind_name` (conformance `declare_kind`): a kind is a short lowercase
/// name — letters, digits, dashes — stripped and lowered; its group stripped and
/// lowered, `declared` when none is given. Refuses in the reference's words.
pub fn kind_name(kind: &str, grp: &str) -> Result<(String, String), String> {
    let kind = kind.trim().to_lowercase();
    let bare: String = kind.chars().filter(|c| *c != '-' && *c != '_').collect();
    if kind.is_empty() || bare.is_empty() || !bare.chars().all(char::is_alphanumeric) {
        return Err("a kind is a short lowercase name: letters, digits, dashes".into());
    }
    let grp = grp.trim().to_lowercase();
    Ok((
        kind,
        if grp.is_empty() {
            "declared".into()
        } else {
            grp
        },
    ))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn the_kind_name_law() {
        assert_eq!(
            kind_name(" Improvement ", "Quality").unwrap(),
            ("improvement".into(), "quality".into())
        );
        assert_eq!(
            kind_name("bug-report", "").unwrap(),
            ("bug-report".into(), "declared".into())
        );
        assert!(kind_name("", "x").is_err());
        assert!(kind_name("not a kind", "x").is_err());
        assert!(kind_name("--", "x").is_err()); // Python: "".isalnum() is False
    }
}
