// PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp1, the bytes · 2026-09-22
//! The content hash — mirrors `orreth_spine.envelope.content_hash`:
//! sha256 over the canonical bytes, prefixed so the algorithm is named.

use crate::canonical::canonical;
use serde_json::Value;
use sha2::{Digest, Sha256};

/// Lowercase hex of sha256 over the bytes.
pub fn sha256_hex(bytes: &[u8]) -> String {
    format!("{:x}", Sha256::digest(bytes))
}

/// `"sha256:" + hex(sha256(canonical(v)))`.
pub fn content_hash(v: &Value) -> String {
    format!("sha256:{}", sha256_hex(&canonical(v)))
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;

    #[test]
    fn the_empty_object_hashes_as_python_says() {
        // hashlib.sha256(b"{}").hexdigest()
        assert_eq!(
            content_hash(&json!({})),
            "sha256:44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a"
        );
    }
}
