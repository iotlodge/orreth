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
  - `stop_demand` (proof-v0, W5) — `input.intention_kind` (`human` · `role` ·
    `kernel`) → `expect.level` + `expect.needs_code`: a human's or a role's
    intention rests on the asker's code (`L3-code`); the kernel's on the asker's
    code and THEN a declared master's click (`L3-master`, `needs_code`).
  - `watch_judge` (watch-v0, W14) — `input.op` · `input.value` · `input.threshold`
    → `expect.red` + `expect.state`: a watch is RED when `value op threshold`
    holds and green otherwise (`bodies_dormant > 0` is red the moment a body is
    dormant, green at 0). `watch_reads` — the watch's human sentence
    ("red when … · now … → …"). The `encode` case carries the wire shape of
    `orreth.watch.turned.v1` (`from` · `to` · the metric and value at the turn).
  - `absent_words` (ask-v0, W19) — `input.name` + `input.reason` → `expect.reply`:
    the door's plain refusal for an ask to a body that is not here ("<name> is
    not here — <reason>"); the `encode` case carries `orreth.ask.refused.v1`
    (`target` · `reason` · `session`, the chain `[person, "the kernel"]`).
  - `address` (ask-v0, W7) — `input.text` + `input.names` (the bodies of this world) →
    `expect.name`: a name at the HEAD of an ask ("echo, …" · "@echo …" · "librarian: …")
    selects that body alone, spelled as the body spells it; anything else is `null`
    and the fan-out stays.
  - `offer` (watch-v0, walk #7) — `input.reply` (the monitor's words) → `expect.offer`:
    `{words, ask}` when the reply offers to propose a watch AND names the condition in
    backticks (`bodies_dormant > 0` → "propose a watch that bodies_dormant > 0"), else
    `null` — the glass draws one click, "propose it", only from an honest offer.
  - `citation_name` (mitl-v0, W15) — `input.path` + `input.heading` (+ `input.rule`) →
    `expect.name`: the canon file's human title ("the covenant" · "the build plan" ·
    "the agent canon" …) and the passage's place — `rule N`, or the heading with its
    marks and its parenthetical tail dropped; the path stays in the record.
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
  - `verdict` (mitl-v0) — `input.touches` (what the kernel read from the ground:
    `kind` · `kernel` · `class` · `level` · `intentions` …) → `expect.verdict`: a
    kernel intention or any act held at L3 is `grave — needs L3`; a change touching
    a standing intention, a consequential act, or what bodies wear is `consider`;
    the rest is `low` — by rule, never by a brain. The impact answer's shape
    (`orreth.impact/1`) and the summoned/dismissed envelopes ride the `canonical`
    and `encode` kinds.
  - `profile` (placement-v0) — `input.template` → `expect.profile` (the placement with
    the defaults applied: `{cell: "local", affinity: [], secrets_with: [], metal: "any"}`
    fills every missing clause) and its canonical `expect.bytes`.
  - `honor` — `input.profile` + `input.ground` (`cell` · `metal` · the secret NAMES the
    ground can reach) → `expect.honored` and `expect.reasons` (every unmet clause in
    words, cell then metal then each secret: `cell 'X' is not this ground ('Y')` ·
    `metal gpu is not here (cpu)` · `secret S is not reachable here`) and `expect.why`
    (the card's line: `stands on local · cpu · reaches 1 of 1 secrets · beside echo
    (advisory)`, or `refused: …`). `metal any` is always honored; affinity never
    refuses (advisory in v0). The refused fact (`orreth.body.refused.v1`) rides `encode`.
- The law: every spoonful that changes a wire contract adds or extends a
  fixture in the same change. A fixture the reference fails is a wound,
  never a regeneration. `spine/tests/test_conformance.py` runs them all.
