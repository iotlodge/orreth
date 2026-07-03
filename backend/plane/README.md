# backend/plane — `orrethd`, the Rust plane

The deterministic, security-critical half of Orreth (0000 §3): gateway, resolver, router, stores,
crypto. Built **against the conformance suite** — the Python simulator in `../conformance` is the
reference; the fixtures in `../conformance/fixtures` are the contract between the two.

## Crates

| Crate | What it proves today |
|---|---|
| `orreth-crypto` | canonical JSON **byte-for-byte** with the Python reference (sorted keys, `ensure_ascii` escaping, ryu floats) · sha256 content-addressing · Ed25519 verification of Python-produced signatures |
| `orreth-rollup` | the StatBundle monoid (0005): merge/report/tier_score match the reference to 1e-9; monoid laws tested |
| `orreth-resolver` | the cascade fold (0007): resolved content matches the reference **including the content-addressed id** — same chain, same hash, either language |
| `orreth-node` | the node semantics: store (append-only, high-water clock), gateway ingress (signature/revocation/scope — the plane verifies, never signs), and the retrieval router (escalation, budget-miss ≡ authz-miss, interview firewall, tombstone fidelity). Replays the reference's full three-flow scenario from `fixtures/flows.json`, exactly |
| `orreth-store` | the body store on the `object_store` trait (S3 API as contract, backend as config — decision 2026-07-02): bodies leave the record at ingress (`store://` refs), reads are **verified against their own content address** (tampering on disk is caught), and a tombstone is **physical erasure** — bytes gone, signed stub remains. In-memory + local FS now; the `aws` feature flag turns on S3 at hosted-deploy time |

| `orrethd` | **the binary — one node, tier as a profile.** Loads a TierProfile, stands up the node with the body store behind it, and serves the gateway over HTTP: `POST /records` (ingress — verify, clock, store), `GET /records/:id/body` (hash-verified), `POST /retrieve` (the router, uniform 403 refusal), `GET /health`. **Trust-root pinned from the profile**: token chains must start at `trust_root.root`, hop continuity and scope attenuation verified at presentation — a self-issued token, however well signed, is refused. The plane verifies, never signs |

## Run a node

```bash
# mint/print the persistent demo root (Python side — cognition holds keys, the plane never does)
cd ../conformance && uv run python smoke_orrethd.py root-pub
# start the daemon with the pinned root's public key
cargo run -p orrethd -- --profile profiles/demo-field.json \
  --store-dir /tmp/orreth-bodies --root-pub <that key>
# then: Python signs, Rust verifies, on the wire — and only the pinned root mints authority
cd ../conformance && uv run python smoke_orrethd.py
```

Next, per 0000 §2/§7: the parent PUSH-up / child PULL-down flows between processes,
Postgres/pgvector behind the record store, and the compose topology — one laptop, one universe.

## Run

```bash
cargo test
```

(Fixtures are committed; no Python needed. Regenerate them from `../conformance` with
`uv run python gen_fixtures.py` whenever the reference changes.)

> serde_json stays on default features — its `Map` is a `BTreeMap` (sorted keys), which the
> canonicalization parity depends on. Never enable `preserve_order` in this workspace.
