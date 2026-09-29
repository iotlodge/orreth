# backend/plane — the Rust kernel, `orrethd`

<!-- PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch row 4, re-base sp2: the plane re-based on orreth-spine · 2026-09-29 -->

The kernel is one crate, **`crates/orreth-spine`**, ported law for law from the Python reference
(`../../spine/orreth_spine`) against the conformance suite (canon `docs/rearch/0008`): a module is
ported only when its fixture (`../../spine/conformance/*.json`) passes unchanged on both kernels.

| Feature | What it holds |
|---|---|
| *(default)* | The pure laws — hermetic, no rig: canonical bytes · hashes · envelopes · the ask road · loops · markers · intent · memory · export · the desk · the seat · cells · levers · doors. `cargo test` runs them and the conformance runner (730 cases). |
| `rails` | The ground (tokio-postgres) and the rails (lapin for RabbitMQ, rdkafka for Kafka — librdkafka built from source by cmake): the schema migrator, the outbox, the inbox with poison-parking, the beats. `tests/rails.rs` needs the rig. |
| `bridge` | The doors and the SSE feed on axum, the bodies' seam (the crew spawned and governed as processes), the cells' seam, the gate, the pool, the clock at every door — and the **`orrethd`** binary. The proofs `askroad` · `loops` · `memory` · `bodies` · `cells` · `gate` · `desk` · `doors` need the rig and refuse beside a lit kernel. |

## Build and run

```bash
cargo test                                                      # hermetic: the laws and the fixtures
cargo build --release -p orreth-spine --features bridge --bin orrethd
SPINE_BRIDGE_PORT=4600 target/release/orrethd                   # or: scripts/dev.sh kernel
cargo test -p orreth-spine --features bridge --test doors -- --nocapture   # one proof on the rig
```

Dials: `SPINE_PG` · `SPINE_RABBIT` · `SPINE_KAFKA` (the rails) · `SPINE_GATEWAY` · `SPINE_BRIDGE_PORT`
(4600) · `SPINE_BIND` (127.0.0.1; the box binds 0.0.0.0) · `SPINE_SCOPE` · `SPINE_QUEUE_NS` · `SPINE_BODIES` (`crew` | `none`) · `ORRETH_SPINE` (the
spine home: crew, templates, tools, glass) · `ORRETH_HOME` (the seeds) · `SPINE_POOL` · `SPINE_PROFILE`.
The image is built from the repo root's `Dockerfile` (the binary beside the spine's venv, the crew
inside).

`serde_json` stays on default features in this workspace: its map is a BTreeMap (sorted keys), which
the canonicalization parity with the reference depends on. Never enable `preserve_order`.

## The old world's crates

`orreth-crypto` · `orreth-node` · `orreth-store` · `orreth-resolver` · `orreth-rollup` were the first
plane's crates (0.72). Each was read against the new kernel before it left (the crypto read
2026-09-28, the other four in re-base sp2 — canon `0005` row 4; verdicts on the honest boundary), and
on JB's word of 2026-09-29 all five left the workspace with the old `orrethd` crate and its tier
profiles. The new kernel depends on none of them; they rest whole at the tag `main-v0.72-old-world`,
and every law the new kernel lacks is named as a seed. The workspace has one member.
