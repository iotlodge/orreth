# backend/conformance — the reference simulator

**Orreth's first code.** A throwaway-by-design Python simulator (0000 §3, locked 2026-07-01) that stands up a
universe in-process — one node kind, three Tier Profiles — and proves the three flows against `contracts/v0`.
Every wire object is schema-validated; every signature is real Ed25519 (the HMAC stand-in was never built).

## Run it

```bash
cd backend/conformance
uv venv && uv pip install -e ".[dev]"
uv run pytest
```

## What the suite proves (10 tests)

| Flow / property | Proven by |
|---|---|
| Identity: archetype → incarnation lineage; did:web root + did:key leaves | `test_identity_chain_and_lineage` |
| No amplification exists; ancestor revocation kills the subtree | `test_no_amplification_and_ancestor_killswitch` |
| **Policy DOWN**: pulled + verified, tier-by-tier; floors tighten, never loosen | `test_floors_cascade_and_never_loosen` |
| **Memory UP**: distillations carry `derived_from` provenance; raw never reaches the apex; floors pin failures | `test_memory_rises_pruned_with_provenance` |
| **Retrieval UP**: time-horizon miss escalates; serve-what-you-have + delegate; Sourced hits | `test_retrieval_escalates_and_merges` |
| Budget-miss ≡ authz-miss (side-channel fix): identical caller-visible shape | `test_budget_miss_equals_authz_miss` |
| Refusals are uniform — no reason leaks to the caller, only to the access log | `test_refusal_shape_is_uniform` |
| Sibling tenant-private is walled; the only cross-sibling window is anonymized aggregates | `test_sibling_tenant_isolation` |
| Interview reads portfolio only; trace is owner-visible, buyer-invisible | `test_interview_reads_portfolio_only` |
| Tombstones annotate, never rewrite; purged raw vanishes; distillations label `distilled-raw-expired` | `test_tombstone_annotates_never_rewrites` |

## Contract bugs it already caught

- `tier-profile.schema.json`: retrieval `horizon` didn't allow `"forever"` — the apex has no time restriction.
  Found on the first run, fixed in the contract. *(This is exactly why the simulator exists.)*

## What it deliberately is not

No LLM steward (distillation is deterministic), no real biscuits (logical attenuation with signed hops), no
network (in-process tree; compose arrives with the plane), no persistence. The **Rust plane** replaces this —
same fixtures, two implementations, one truth. When these tests are ported to conformance fixtures, this
package's job is done.

## The conformance fixtures — the spec the Rust plane must pass

`gen_fixtures.py` derives language-neutral fixtures (`fixtures/*.json`) from this reference:
pure input → output pairs (0007's determinism is what makes them possible). `crypto.json` pins
canonicalization **byte-for-byte** (sorted keys, compact, Python `ensure_ascii` escaping, ryu floats)
plus a real Ed25519 vector; `rollup.json` pins the monoid and the Bayesian report edge;
`resolver.json` pins the fold **including the content hash** — one truth, two implementations.
Regenerate after any reference change: `uv run python gen_fixtures.py` (commit the fixtures; the
Rust suite reads them directly and needs no Python).
