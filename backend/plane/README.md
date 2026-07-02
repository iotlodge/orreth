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

Next, per 0000 §2: the store crates (append-only, content-addressed), the gateway pipeline
(ingress verify / egress authz), the retrieval router, and the `orrethd` binary that stacks them
under a Tier Profile.

## Run

```bash
cargo test
```

(Fixtures are committed; no Python needed. Regenerate them from `../conformance` with
`uv run python gen_fixtures.py` whenever the reference changes.)

> serde_json stays on default features — its `Map` is a `BTreeMap` (sorted keys), which the
> canonicalization parity depends on. Never enable `preserve_order` in this workspace.
