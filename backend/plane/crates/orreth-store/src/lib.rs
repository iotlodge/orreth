//! The body store (0000 §2 "Stores", decision 2026-07-02): record bodies live in an
//! object store behind the S3 API — the backend is config, not architecture.
//!
//! Two properties fall out of content addressing:
//! - **Tamper-evident reads for free**: a record's id is the sha256 of its canonical body,
//!   so every read verifies the bytes against their own address.
//! - **Tombstones are PHYSICAL erasure**: deleting the object removes the bytes from disk
//!   (or bucket), while the signed record stub remains — provable retirement (0002 §6).

use base64::engine::general_purpose::URL_SAFE_NO_PAD;
use base64::Engine;
use object_store::memory::InMemory;
use object_store::path::Path as ObjPath;
use object_store::{local::LocalFileSystem, ObjectStore};
use sha2::{Digest, Sha256};
use std::sync::Arc;
use tokio::runtime::Runtime;

#[derive(Debug, PartialEq)]
pub enum StoreError {
    NotFound,
    /// The bytes do not hash to their own address — tampering or corruption.
    IntegrityViolation,
    Backend(String),
}

pub struct BodyStore {
    store: Arc<dyn ObjectStore>,
    rt: Runtime,
}

impl BodyStore {
    pub fn in_memory() -> Self {
        Self::new(Arc::new(InMemory::new()))
    }

    pub fn local(dir: &std::path::Path) -> Self {
        std::fs::create_dir_all(dir).expect("body store dir");
        Self::new(Arc::new(LocalFileSystem::new_with_prefix(dir).expect("local body store")))
    }

    fn new(store: Arc<dyn ObjectStore>) -> Self {
        let rt = tokio::runtime::Builder::new_current_thread()
            .build()
            .expect("body store runtime");
        Self { store, rt }
    }

    fn path(scope_root: &str, record_id: &str) -> ObjPath {
        // bodies/<universe>/<content-hash> — one prefix per tenant (the isolation story
        // must be true at the storage layer too, 0000 §6)
        ObjPath::from(format!("bodies/{}/{}", scope_root, record_id.replace(':', "_")))
    }

    /// Store a record's body (the urlsafe-b64 canonical bytes from the wire). Returns the body_ref.
    pub fn put_body(&self, scope_root: &str, record_id: &str, body_b64: &str) -> Result<String, StoreError> {
        let bytes = URL_SAFE_NO_PAD
            .decode(body_b64)
            .map_err(|e| StoreError::Backend(e.to_string()))?;
        let path = Self::path(scope_root, record_id);
        self.rt
            .block_on(self.store.put(&path, bytes.into()))
            .map_err(|e| StoreError::Backend(e.to_string()))?;
        Ok(format!("store://{path}"))
    }

    /// Fetch and VERIFY: the sha256 of the bytes must equal the record's content address.
    pub fn get_body(&self, scope_root: &str, record_id: &str) -> Result<Vec<u8>, StoreError> {
        let path = Self::path(scope_root, record_id);
        let bytes = self
            .rt
            .block_on(async { self.store.get(&path).await?.bytes().await })
            .map_err(|_| StoreError::NotFound)?;
        let expected = record_id.strip_prefix("sha256:").unwrap_or(record_id);
        if format!("{:x}", Sha256::digest(&bytes)) != expected {
            return Err(StoreError::IntegrityViolation);
        }
        Ok(bytes.to_vec())
    }

    /// Physical erasure — the tombstone's storage-layer twin. The stub stays; the bytes go.
    pub fn delete_body(&self, scope_root: &str, record_id: &str) -> Result<(), StoreError> {
        let path = Self::path(scope_root, record_id);
        self.rt
            .block_on(self.store.delete(&path))
            .map_err(|e| StoreError::Backend(e.to_string()))
    }

    pub fn exists(&self, scope_root: &str, record_id: &str) -> bool {
        let path = Self::path(scope_root, record_id);
        self.rt.block_on(self.store.head(&path)).is_ok()
    }
}
