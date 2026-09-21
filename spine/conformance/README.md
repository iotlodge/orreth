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
- The law: every spoonful that changes a wire contract adds or extends a
  fixture in the same change. A fixture the reference fails is a wound,
  never a regeneration. `spine/tests/test_conformance.py` runs them all.
