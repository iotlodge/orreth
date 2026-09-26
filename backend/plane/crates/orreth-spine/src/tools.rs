// PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp8 row 2, the tool door moves · 2026-09-26
//! `orreth.tools/1` — the pure half of `orreth_spine.tools` (P7 sp8 row 2, THE
//! TOOL DOOR MOVES): the built-in tools' DECLARATIONS are data in
//! `spine/tools.v0.json`, beside the crew manifest, read by BOTH kernels — this
//! kernel seeds the shelf from it and probes a built-in by describe itself. A
//! tool's EXECUTION stays body-side by canon (0009 §"the Tools firmware": the
//! kernel authorizes, journals and meters; it never runs the call) — nothing
//! here runs anything. Measured by the conformance kinds `tool_manifest` ·
//! `tool_consequence` (`spine/conformance/tools-v0.json`).

use serde_json::{json, Value};
use std::path::{Path, PathBuf};

/// The manifest's format word.
pub const FORMAT: &str = "orreth-tools/1";
/// The file, beside `crew.v0.json`.
pub const FILE: &str = "tools.v0.json";
/// The spine home dial (`ORRETH_SPINE`); default beside the crate.
pub const SPINE_DIAL: &str = "ORRETH_SPINE";
/// What every declaration carries.
pub const DECLARED_KEYS: [&str; 4] = ["name", "description", "input_schema", "consequence"];
/// The classes an act can wear.
pub const CLASSES: [&str; 3] = ["routine", "consequential", "grave"];

/// The spine home: `ORRETH_SPINE`, else the crate's `../../../../spine`.
pub fn spine_dir() -> PathBuf {
    std::env::var(SPINE_DIAL)
        .ok()
        .filter(|p| !p.is_empty())
        .map(PathBuf::from)
        .unwrap_or_else(|| PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("../../../../spine"))
}

/// `tools.declarations` on a document already read: the format checked, every
/// declaration whole (name · words · schema · class), the class known, no name
/// twice. Refuses in words.
pub fn declarations_of(doc: &Value) -> Result<Vec<Value>, String> {
    if doc["format"].as_str() != Some(FORMAT) {
        return Err(format!(
            "not a tools manifest: format {}, expected {}",
            doc["format"],
            crate::py::repr_str(FORMAT)
        ));
    }
    let mut out = Vec::new();
    let mut seen = std::collections::HashSet::new();
    for d in doc["tools"].as_array().cloned().unwrap_or_default() {
        let name = d["name"].as_str().unwrap_or("?").to_string();
        let missing: Vec<&str> = DECLARED_KEYS
            .iter()
            .copied()
            .filter(|k| d.get(k).is_none())
            .collect();
        if !missing.is_empty() {
            return Err(format!(
                "the tool declaration {} lacks {}",
                crate::py::repr_str(&name),
                missing.join(", ")
            ));
        }
        let cls = d["consequence"].as_str().unwrap_or("");
        if !CLASSES.contains(&cls) {
            return Err(format!(
                "the {} tool declares an unknown class {} — the classes: {}",
                crate::py::repr_str(&name),
                crate::py::repr_str(cls),
                CLASSES.join(", ")
            ));
        }
        if !seen.insert(name.clone()) {
            return Err(format!(
                "the tool {} is declared twice",
                crate::py::repr_str(&name)
            ));
        }
        out.push(d);
    }
    Ok(out)
}

/// `tools.declarations`: the file beside the crew manifest, read and checked.
pub fn declarations(spine: &Path) -> Result<Vec<Value>, String> {
    let path = spine.join(FILE);
    let text = std::fs::read_to_string(&path).map_err(|e| {
        format!(
            "the tools manifest at {} could not be read: {e}",
            path.display()
        )
    })?;
    let doc: Value = serde_json::from_str(&text)
        .map_err(|e| format!("the tools manifest at {} is not JSON: {e}", path.display()))?;
    declarations_of(&doc)
}

/// One declaration by name.
pub fn declared<'a>(decls: &'a [Value], name: &str) -> Option<&'a Value> {
    decls.iter().find(|d| d["name"].as_str() == Some(name))
}

/// `tools.tool_manifest`: what a tool DECLARES — the manifest the registry pins:
/// its name, its words, its input schema, its consequence class. The flags
/// (ground · master · held_by) are the door's, never the pin's.
pub fn manifest(decl: &Value) -> Value {
    json!({
        "name": decl["name"],
        "description": decl["description"],
        "input_schema": decl["input_schema"],
        "consequence": decl["consequence"],
    })
}

/// `tools.consequence_of`: the class a call wears. With arguments in hand and a
/// `held_by` rule (the argument field and the values that HOLD at the
/// interlock), a held value wears the declared class and any other runs at
/// once (routine); with no arguments, or no rule, the declared class stands.
pub fn consequence_of(decl: &Value, args: Option<&Value>) -> String {
    let declared = decl["consequence"]
        .as_str()
        .unwrap_or("routine")
        .to_string();
    let (Some(args), Some(hb)) = (args, decl.get("held_by").filter(|h| h.is_object())) else {
        return declared;
    };
    let field = hb["field"].as_str().unwrap_or("");
    let value = match &args[field] {
        Value::Null => String::new(),
        Value::String(s) => s.clone(),
        other => crate::py::python_str(other),
    };
    let held = hb["held"]
        .as_array()
        .map(|a| a.iter().any(|v| crate::py::python_str(v) == value))
        .unwrap_or(false);
    if held {
        declared
    } else {
        "routine".into()
    }
}

/// Does the tool's executor take the ground (a `conn`)? The door's flag.
pub fn on_ground(decl: &Value) -> bool {
    decl["ground"] == json!(true)
}

/// Does the gravest act demand a master? The door's flag.
pub fn master(decl: &Value) -> bool {
    decl["master"] == json!(true)
}

#[cfg(test)]
mod tests {
    use super::*;

    fn weather() -> Value {
        json!({"name": "weather", "description": "the temperature", "input_schema": {"type": "object", "properties": {}},
               "consequence": "routine", "ground": true})
    }

    #[test]
    fn the_declarations_are_checked_in_words() {
        let ok = json!({"format": FORMAT, "tools": [weather()]});
        assert_eq!(declarations_of(&ok).unwrap().len(), 1);
        let bad = json!({"format": "orreth-crew/1", "tools": []});
        assert!(declarations_of(&bad)
            .unwrap_err()
            .starts_with("not a tools manifest"));
        let mut lacking = weather();
        lacking.as_object_mut().unwrap().remove("input_schema");
        assert_eq!(
            declarations_of(&json!({"format": FORMAT, "tools": [lacking]})).unwrap_err(),
            "the tool declaration 'weather' lacks input_schema"
        );
        let mut odd = weather();
        odd["consequence"] = json!("dire");
        assert!(declarations_of(&json!({"format": FORMAT, "tools": [odd]}))
            .unwrap_err()
            .contains("unknown class 'dire'"));
        assert_eq!(
            declarations_of(&json!({"format": FORMAT, "tools": [weather(), weather()]}))
                .unwrap_err(),
            "the tool 'weather' is declared twice"
        );
    }

    #[test]
    fn the_manifest_carries_the_pin_keys_only() {
        let m = manifest(&weather());
        assert_eq!(
            m.as_object().unwrap().keys().cloned().collect::<Vec<_>>(),
            ["consequence", "description", "input_schema", "name"]
        );
        assert!(m.get("ground").is_none());
    }

    #[test]
    fn the_class_is_by_the_arguments_when_the_declaration_says_so() {
        let services = json!({"name": "services", "description": "", "input_schema": {}, "consequence": "consequential",
                              "held_by": {"field": "action", "held": ["register", "retire"]}});
        assert_eq!(consequence_of(&services, None), "consequential");
        assert_eq!(
            consequence_of(&services, Some(&json!({"action": "list"}))),
            "routine"
        );
        assert_eq!(
            consequence_of(&services, Some(&json!({"action": "retire"}))),
            "consequential"
        );
        assert_eq!(consequence_of(&services, Some(&json!({}))), "routine");
        assert_eq!(
            consequence_of(&weather(), Some(&json!({"latitude": 1}))),
            "routine"
        );
        let grave = json!({"name": "erase-record", "description": "", "input_schema": {}, "consequence": "grave"});
        assert_eq!(consequence_of(&grave, Some(&json!({"key": "k"}))), "grave");
    }

    #[test]
    fn the_real_file_reads_and_pins_every_built_in() {
        let decls = declarations(&spine_dir()).unwrap();
        let names: Vec<&str> = decls.iter().map(|d| d["name"].as_str().unwrap()).collect();
        assert!(
            names.contains(&"weather") && names.contains(&"services") && names.contains(&"minds")
        );
        // the weather pin, as services-v0's manifest_pin case has carried it since P6.5 sp1
        assert_eq!(
            crate::services::pin(&manifest(declared(&decls, "weather").unwrap())),
            "sha256:845484c281d4eaa8fa9a303fb2c2861529938fb6e814f05bc825cf13d40d7503"
        );
    }
}
