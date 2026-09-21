# The conformance suite (canon 0008)

Language-neutral fixtures that the Python spine (the reference) generates
and must pass, and that `orrethd` (the Rust kernel, Phase 7) must pass —
the same files, unchanged — before any module earns the word "ported".

- One file per wire contract and version: `<contract>-v<N>.json`.
- Shape: `{"contract", "version", "generated_by", "generated_at", "cases": [...]}`;
  each case is `{"name", "kind", "input", "expect"}`.
- Case kinds so far:
  - `canonical` — `input.obj` → `expect.bytes` (ASCII string) and `expect.hash`.
  - `encode` — `input.env` (a complete envelope) → `expect.bytes`.
  - `encode_refuses` — `input.env` (incomplete or wrong specversion) → every
    name in `expect.names` appears in the refusal's message.
  - `decode_preserves` — `input.bytes` → `expect.obj` (unknown fields survive).
  - `totp` (proof-v0) — `input.secret` (base32) + `input.time` (unix s) →
    `expect.code` (RFC 6238: SHA-1, 30 s, 6 digits).
  - `totp_verify` — `input.code` checked at each `input.at` → `expect.ok`
    (the step before and after pass; two away refuse).
  - `ladder` — `input.order` (consequence classes, shuffled) → `expect.sorted`
    and the levels each demands (`routine < consequential < grave` →
    `L1 < L2 < L3`).
  - `class_level` — `input.class` (+ `master`) → `expect.level`
    (`L1` · `L2` · `L3-code` · `L3-master`).
  - `hash_chain` (export-v0) — `input.rows` → `expect.hashes` and `expect.root_hash`:
    `h0 = sha256(canonical(row0))`, `h_i = sha256(ascii_hex(h_{i-1}) || canonical(row_i))`
    (the previous digest's lowercase hex, as ASCII bytes, prepended to the row's
    canonical bytes); the root is the last; an empty bundle has none.
  - `chain_status` — `input.rows` → `expect.status` per row (`intact` · `broken`):
    a chain is intact when it exists, begins with the row's `person` (the origin
    human) and, where `served_by` names a body, ends with that body; a `proof`
    row is intact when its chain exists (the prover is never the asker).
  - `verify` — `input.bundle` verifies, `input.truncated` (one hop cut, hashes
    unchanged) does not, `input.resealed` (the cut rows re-sealed) verifies with
    `summary.chain_broken` counting the cut.
- The law: every spoonful that changes a wire contract adds or extends a
  fixture in the same change. A fixture the reference fails is a wound,
  never a regeneration. `spine/tests/test_conformance.py` runs them all.
