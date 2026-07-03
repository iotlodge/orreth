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

## The tree — parent/child over the wire

`orrethd --parent <url>` makes a node a child (0000 §1: PUSH up / PULL down; a parent never
reaches in). At boot the child **PULLs** its parent's floors from `GET /standards` (inherited
floors dominate; a child tightens, never loosens). On a retrieval whose window outruns the local
horizon, the child **serves what it has and delegates the deeper remainder UP** (`0002 §3`) —
forwarding the query over HTTP with the spent budget deducted, then merging newest-first
(`occurred_at` travels with every hit for exactly this). A refusing or dead parent is
indistinguishable from budget exhaustion: un-served coverage, honest remainder, never an error
shape. Demo: `demo_spacetime_window.py` — two daemons, one query, 300 days scrubbed.

## Persistence — the daemon may die; the records don't

`orrethd --pg postgres://…` turns on write-through persistence: every **accepted** record
lands as JSONB (the stored form — body_ref, keep_class, received_at), and at boot the daemon
restores its records **and its high-water mark**, so the clock's monotonicity survives
restarts. Bodies already live in the object store; Postgres holds pointers, not blobs.
Dev database: `docker run -d --name orreth-pg -e POSTGRES_PASSWORD=orreth -p 5433:5432 postgres:16`.
The resurrection demo: run `demo_digital_life.py born`, kill the daemon, restart it, run
`wake` — the life outlives the process, the machine boundary, and now the daemon itself.

Next, per 0000 §7: pgvector for semantic retrieval, and the compose topology —
one laptop, one universe, one command.

## Run

```bash
cargo test
```

(Fixtures are committed; no Python needed. Regenerate them from `../conformance` with
`uv run python gen_fixtures.py` whenever the reference changes.)

> serde_json stays on default features — its `Map` is a `BTreeMap` (sorted keys), which the
> canonicalization parity depends on. Never enable `preserve_order` in this workspace.
