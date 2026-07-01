# contracts/ — the wire contracts

**The contracts are the product of the design phase** (`docs/design/0000` §4). One thin recursive node
(`orrethd`) speaks them; everything else — simulator, Rust plane, panes, any-SDK agents — conforms to them.

## Rules (locked 2026-07-01)

- **Format:** JSON Schema (draft 2020-12) now — human-diffable while design churns. **Protobuf at Rust-time**
  becomes the wire format; JSON Schema stays as documentation.
- **Versioning:** `v0/` may churn freely until the simulator proves the flows; semver discipline begins at `v1`.
- **`$id` namespace:** `https://orreth.ai/contracts/v0/…` — the domain is owned (registered 2026-07-01).
  **Nothing needs to be live at these URLs**: validators resolve locally. Serving them is optional politeness,
  post-build.
- **Depth-agnostic:** no contract carries a tier name in a logic position. `ScopePath` + relative `Space`
  everywhere; `tier_label` is display-only.

## The v0 set

| File | Contract | Source spec |
|---|---|---|
| `v0/common.schema.json` | DID · ContentHash · Sig · ScopePath · Space · Selector · Budget · TimeWindow · StandardRef | 0000–0006 |
| `v0/memory-record.schema.json` | `MemoryRecord` + visibility + retention + **Distillation** + RedactionMarker + Promotion | 0001 §1–2, 0002 §2, 0003 §2 |
| `v0/skill-standard.schema.json` | `SkillStandard` + Scaffold + AcceptanceRubric + Evaluators | 0001 §3 |
| `v0/identity.schema.json` | `Identity` + Attachment + Transfer (source veto + ancestor override) | 0002 §1 |
| `v0/retrieval.schema.json` | `Query` + `RetrievalResult` (merge semantics, remainder-never-silent) | 0002 §3 as amended |
| `v0/capability-token.schema.json` | `CapabilityToken` (attenuation-only; biscuit on the wire) | 0006 §3 |
| `v0/pruning-policy.schema.json` | `PruningPolicy` + KeepRule + DistillDirective | 0003 §1 |
| `v0/tier-profile.schema.json` | `TierProfile` — every locked dial (retention, TTLs, QA sample, judge sampling, cadence, trust root) | 0003/0004/0006 |
| `v0/join.schema.json` | `Join` — the join spectrum, floors ack, lease terms | 0000 §1, decisions |
| `v0/signed-record.schema.json` | `SignedRecord` / `SignedBundle` — push-up / pull-down envelopes | EH (lifted) |

## Pending extraction

- **`Standard` / `RunRecord` roll-up envelope** — after `0005` (needs the confidence statistic pick and a
  reference pass over EH's cohort shapes).
- **`GraphSpec`** — the `0008` dive (dual-mode authoring IR; locked as the compile target).
- **`AgentSurface`** — an API contract (OpenAPI/proto service), not a document schema; lands with `0010`.

## Conformance

The EH test suite (61 tests) gets extracted into fixture files against these schemas; the Python simulator
must pass them first, the Rust plane second. Same fixtures, two implementations, one truth.
