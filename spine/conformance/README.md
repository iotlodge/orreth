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
  - `offer` (watch-v0, walk #7 → W22) — `input.reply` (the monitor's words) → `expect.offer`:
    `{words, ask}` when the reply offers to propose a watch; the condition is read with
    or without backticks (`bodies_dormant > 0` → "propose a watch that bodies_dormant > 0");
    an offer that names no condition (or a metric this world does not measure) still
    offers — `words` null, `ask` tells the monitor to propose through add-watch; a bare
    condition with no offer is `null`. The glass draws "propose it" from any offer.
  - `restart_demand` (intent-v0, W20) — `input.intention_kind` → `expect.level` +
    `expect.needs_code`: the reverse of the stop climbs the stop's ladder. The `encode`
    cases carry `orreth.intention.restarted.v1` (`by` · `proof` · `confirmed_by` for the
    kernel's, the chain `[asker, master]`).
  - `duty_text` (intent-v0, W21) — `input.text` · `every_s` · `since` (the last run's
    clock or null) · `notes` (the runner's own earlier notes, newest first) →
    `expect.cadence` (hourly · daily · weekly · every N minutes/seconds) and `expect.text`:
    the occurrence FRAMED as a duty — `"<words>" — your <cadence> duty (every N s) ·
    since <time> | your first run · your earlier notes today: a · b · c | no earlier
    notes today` (at most three notes, each cut at 160).
  - `refused_words` (intent-v0, W21) — `input.reply` → `expect.refused`: a reply that
    OPENS as a refusal ("I will not …", "I am not answering …", "not answering this …",
    "I refuse/decline …"), markdown stripped; a mention inside a reply is not one.
  - `echo_reply` (intent-v0, W24) — `input.name` + `input.text` → `expect.reply`: the
    echoed words alone (whitespace folded); a QUESTION adds one plain line — "<name>
    repeats; ask the librarian for the date" (a date/time ask) or "… for an answer".
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
  - `rail_names` (rails-v0, P7 sp2) — `input.ns` (`SPINE_QUEUE_NS`) · `input.scope`
    (`SPINE_SCOPE`, null = unset) · `input.name` (a target, or null) → the serve
    queue and key wearing the namespace and the name in that order, the world
    (`u:dev` when unset), and the rails' fixed names (the command exchange, the
    heartbeat's queue · key · topic).
  - `outbox_row` — `input.env` → `expect.message_id` · `expect.body` (the
    canonical bytes) · `expect.topic` (the envelope's TYPE) · `expect.key` (the
    aggregate id when the envelope wears a truthy one, else the message id —
    `sinks.KafkaSink`'s two laws).
  - `inbox_key` — `input.env` → `expect.road` (`once` by message id, or
    `sequenced` per aggregate when it wears an id AND a positive sequence — the
    head of `inbox.apply_event`) with the aggregate id and sequence it rides.
  - `ladder_step` (services-v0, P6.5 sp1) — `input.state` (`registered` · `versioned` ·
    `healthy` · `unhealthy` · `retired`, or null = not registered) + `input.verb`
    (`register` · `version` · `healthy` · `unhealthy` · `retire` · `restore`) →
    `expect.ok` · `expect.to` (the state stepped to) · `expect.reason` (the refusal in
    words, naming the state and the step: "already registered — version it …", "retired —
    the ladder runs no version on a retired service; restore it first", "healthy, not
    retired — nothing to restore"). ONE ladder for tool · mcp · store · source · mind;
    retired is dormancy (restore returns it), never deletion.
  - `manifest_pin` — `input.manifest` (what a service declares: a tool's schema and class,
    a mind's route + model, an mcp server's listed tools, a store's locator by NAME) →
    `expect.bytes` (canonical) and `expect.hash` (`sha256:` over them) — the pin the
    registry keeps; a changed manifest is a new version, never a silent drift. The
    `encode` cases carry `orreth.service.registered.v1` (the kernel's chain, an
    observation marker, the pin and the placement) and `orreth.service.retired.v1`
    (released at the interlock: `[person, the kernel]`, an action under the held ask).
  - `mcp_request` (mcp-v0, P6.5 sp2) — `input.method` (`initialize` · `tools/list` ·
    `tools/call` with `input.tool` + `input.arguments`) → `expect.id` (FIXED: 1 · 2 · 3 —
    a session per act, so the ids never climb) and `expect.bytes`: the JSON-RPC 2.0
    request as canonical bytes (the protocol version, the client by name, the tool by
    its WIRE name, arguments an empty object never null).
  - `mcp_tool_manifest` — `input.server` + `input.tool` (an entry of a server's
    `tools/list`: `name` · `description` · `inputSchema` · `annotations`) →
    `expect.manifest` (the service a tool becomes: `name` = the shelf name — the wire
    name lowercased, made lawful; `tool` = the wire name; `input_schema`;
    `consequence` — `destructiveHint` → consequential, else routine; `server`),
    `expect.shelf_name`, `expect.consequence`, `expect.bytes`, `expect.hash` (the pin).
  - `mcp_server_manifest` — `input.locator` (a command line, or a URL) + `input.tools`
    → `expect.manifest` (`transport` stdio | http by the locator; `locator` BY NAME;
    `tools` = name · schema · class, SORTED by name so the pin reads the list alone)
    and `expect.hash`: a changed list is a changed pin — the server VERSIONS.
  - `mcp_transport` — `input.locator` → `expect.transport` (`http` for http(s)://,
    `stdio` for anything else).
  - `mcp_words` — the words a vanished tool's health wears ("gone from the server's
    list" — unhealthy, never retired by the machine), the strikes dial
    (`SPINE_TOOL_UNHEALTHY_STRIKES`, default 3), the protocol version, the fixed ids.
  - `beat_lock` (loops-v0, P7 sp4) — the loops' shadow law: the beat classes
    (`scheduler` 1 · `intent` 2 · `keeper` 3) counting up from 742200, the
    advisory-lock keys they make (`pg_try_advisory_lock(key, hashtext(scope))`),
    and the words a kernel says when another holds the beat.
  - `loop_words` — the loop's constants: the cadence's observation, the runner's
    honest opening (`cannot act`), the facts' names (`watch.turned` ·
    `harness.failed` · `intention.declared/stopped/restarted`), the `watch-red`
    kind, the lease's TTL, the Resiliency intention, W26's words and step.
  - `plan_words` — `input.serves` + `input.words` + `input.observed` → `expect.text`:
    what the kernel asks the planner under an observation.
  - `observed_words` — `input.kind` + `input.ref` + `input.note` → `expect.text`: the
    observation under a marker (the kind in Python's quotes).
  - `watch_note` — a red watch's note: the name in Python's `repr` quotes (double
    quotes when the name holds an apostrophe), the float threshold, the value.
  - `cannot_act` — `input.reply` → `expect.cannot`: only the OPENING counts (W8),
    markdown stripped; a reply that merely mentions the words is a reply.
  - `improvement_note` — `input.who` + `input.reply` → `expect.note`: the first 200
    characters of what the runner said.
  - `crew_hash` — `input.shape` (name · capabilities pairs, any order) → `expect.hash`:
    sorted by name, as canonical bytes of a list of lists.
  - `turned_fact` — the `orreth.watch.turned.v1` bytes for a fixed id and clock: the
    kernel's chain, the watch as correlation, `from` null when first judged.
