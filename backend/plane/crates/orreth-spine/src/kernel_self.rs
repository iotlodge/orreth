// PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch P7 sp5, memory and the export · 2026-09-24
//! THE KERNEL'S OWN SELF (canon 0005 P7 sp5 · covenant rule 1): one Ed25519
//! keypair per rig, its seed at `<SPINE_KERNEL_HOME or ORRETH_HOME/kernel>/seed`,
//! minted once and read every boot after — the same self on EVERY bridge
//! over this ground (the Python spine's `Identity.kernel` reads the same
//! file). It signs the compliance export (`export::seal`); its DID is
//! `did:orreth:kernel:` + sha256(public)[..32], the same derivation as
//! every body's (`identity.py`). Signing lives here, in the spine, on the
//! same Ed25519 library the verifier already uses — the sacred crypto
//! crate is not touched (JB's lock, 2026-09-24).

use crate::canonical::canonical;
use crate::hash::sha256_hex;
use ed25519_dalek::{Signer, SigningKey};
use serde_json::Value;
use std::path::{Path, PathBuf};

pub struct KernelSelf {
    pub name: String,
    pub kind: String,
    key: SigningKey,
}

impl KernelSelf {
    /// A self from a 32-byte seed (any kind — the fixture's `did_of` derives agents and services too).
    pub fn from_seed(seed: &[u8; 32], kind: &str) -> KernelSelf {
        KernelSelf {
            name: "kernel".into(),
            kind: kind.into(),
            key: SigningKey::from_bytes(seed),
        }
    }

    /// The seed's directory: `SPINE_KERNEL_HOME`, else `ORRETH_HOME/kernel`, else `~/.orreth/kernel`.
    pub fn home() -> PathBuf {
        if let Ok(h) = std::env::var("SPINE_KERNEL_HOME") {
            if !h.is_empty() {
                return PathBuf::from(h);
            }
        }
        let base = std::env::var("ORRETH_HOME")
            .ok()
            .filter(|h| !h.is_empty())
            .map(PathBuf::from)
            .unwrap_or_else(|| {
                PathBuf::from(std::env::var("HOME").unwrap_or_else(|_| ".".into())).join(".orreth")
            });
        base.join("kernel")
    }

    /// The same self every life: the seed read from `<dir>/seed`, minted once if absent.
    pub fn load(dir: &Path) -> std::io::Result<KernelSelf> {
        let path = dir.join("seed");
        let seed: Vec<u8> = if path.exists() {
            std::fs::read(&path)?
        } else {
            std::fs::create_dir_all(dir)?;
            let mut buf = [0u8; 32];
            std::fs::File::open("/dev/urandom").and_then(|mut f| {
                use std::io::Read;
                f.read_exact(&mut buf)
            })?;
            std::fs::write(&path, buf)?;
            #[cfg(unix)]
            {
                use std::os::unix::fs::PermissionsExt;
                let _ = std::fs::set_permissions(&path, std::fs::Permissions::from_mode(0o600));
            }
            buf.to_vec()
        };
        let seed: [u8; 32] = seed.as_slice().try_into().map_err(|_| {
            std::io::Error::new(
                std::io::ErrorKind::InvalidData,
                "the kernel's seed is not 32 bytes",
            )
        })?;
        Ok(KernelSelf::from_seed(&seed, "kernel"))
    }

    /// An ephemeral self — tests only, never a rig.
    pub fn ephemeral() -> KernelSelf {
        let mut buf = [0u8; 32];
        if let Ok(mut f) = std::fs::File::open("/dev/urandom") {
            use std::io::Read;
            let _ = f.read_exact(&mut buf);
        }
        KernelSelf::from_seed(&buf, "kernel")
    }

    pub fn public_key(&self) -> [u8; 32] {
        self.key.verifying_key().to_bytes()
    }

    /// The public half, hex — what a stranger checks a signature with.
    pub fn verify_key_hex(&self) -> String {
        hex(&self.public_key())
    }

    /// `did:orreth:<kind>:` + sha256(public)[..32].
    pub fn did(&self) -> String {
        format!(
            "did:orreth:{}:{}",
            self.kind,
            &sha256_hex(&self.public_key())[..32]
        )
    }

    /// Sign the canonical bytes of a payload; hex signature (64 bytes → 128 hex).
    pub fn sign(&self, payload: &Value) -> String {
        hex(&self.key.sign(&canonical(payload)).to_bytes())
    }
}

pub fn hex(bytes: &[u8]) -> String {
    bytes.iter().map(|b| format!("{b:02x}")).collect()
}
