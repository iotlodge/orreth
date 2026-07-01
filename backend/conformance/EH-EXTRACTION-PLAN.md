# EH → conformance fixtures — extraction plan

*Surveyed 2026-07-01 (agent pass over `../ecosystem.harness`). "Lift the contract, port the engine"
(0000 §3): EH's 61 tests become language-neutral fixtures; the Python sim passes them first, the Rust
plane second. Same fixtures, two implementations, one truth.*

## Survey results

- **61 tests across 10 files.** **58 are pure-logic** (given records in → expect drift/lane/promotion out)
  and fixture-ize directly; only **3 are HTTP-bound** (FastAPI TestClient) and get re-expressed against the
  gateway contract instead.
- **Core shapes confirmed in code:** RunRecord (provenance + outcome + process + risk blocks, derived
  metrics), Standard (versioned, scope/lane/status lifecycle), cohort key `(field_id, goal_hash)`,
  ObjectiveModel (lexicographic hard floors + weighted soft objectives + arbitration), DriftSignal
  (dead-band threshold + persistence counter), Candidate (config-diff bisect seam attribution with
  confidence), IndexEntry + DID checks (HMAC spike — unknown/revoked/spoofed/tampered all rejected).
- **~15 coverage gaps worth new fixtures:** exact boundary at `(window + persistence_k)` data points,
  concurrent proposals, soft-weight refinement after human escalation, very large cohorts.

## Translation table (EH → Orreth)

| EH | Orreth |
|---|---|
| `field_id` | `ScopePath` (depth-agnostic) |
| cohort key `(field_id, goal_hash)` | `(ScopePath, goal_hash)` |
| HMAC signing spike | Ed25519 (`contracts/v0/common.schema.json#Sig`) |
| Standard scope `field`/`global` | `Selector` targeting (at-or-below) |
| RunRecord | `RunRecord` contract — lands with `0005` (confidence statistic picked there) |

## Fixture format (agreed sketch)

JSON per case: `{"name", "given": {records: [...], objective_model, config_history}, "expect":
{drift?, seam?, lane?, lifecycle?, rejection_reason?}}` — ten templates cover the highest-value behaviors:
drift detection, bisect attribution, lane routing, hard-floor lexicographic blocks, auto-apply lifecycle,
governed lifecycle, canary promotion, escalation + weight refinement, DID verification (all four rejection
modes), tenancy isolation.

## Sequencing

1. **After `0005`** (RunRecord contract needs the confidence statistic): extract the 58 pure-logic tests
   into `backend/conformance/fixtures/` + a fixture-runner in the sim.
2. Add the ~15 gap fixtures while extracting (cheapest moment).
3. The 3 HTTP tests re-express against the Gateway contract when the Rust plane's API lands (`0010`).
