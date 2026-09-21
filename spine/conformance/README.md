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
- The law: every spoonful that changes a wire contract adds or extends a
  fixture in the same change. A fixture the reference fails is a wound,
  never a regeneration. `spine/tests/test_conformance.py` runs them all.
