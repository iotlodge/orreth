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
  - `route_for` · `usd` · `budget_duration` · `resolve` · `drift` · `eol_due` ·
    `recommend` · `deal` · `deal_refuses` · `drained_words` · `act_words` (minds-v0,
    P6.5 sp3) — the Stable's laws: the gateway's model string for a mind wherever it
    resides; dollars from the pin's price; the fuel window in the gateway's grammar;
    the routing decision (pin → assignment → the template's model → the cheapest of
    the class → a neighbour confessed); what moved under a pin; an expiry inside the
    horizon; the swap (same class → fit → nearest price → newest); the DEAL and its
    refusals (a key VALUE never enters a record); the honest words of a drained
    body; the interlock's words for each Stable act.
  - `server_name` (minds-v0, W28) — `input.info` (a server's initialize) + `input.locator`
    → `expect.name`: the last word of the server's own name, lowercased.
  - `search_terms` · `memory_fact` · `purge_fact` · `digest_text` · `digest_fact`
    (memory-v0, P7 sp5) — recall's grammar (OR-shaped terms; the word-match
    fallback's needles); the landed and purged facts' payloads and bytes for a
    fixed id and clock; the short version's text from its parts (`%a %b %d %H:%M`
    in UTC); the digest's fact with the session as correlation.
  - `signed_bundle` · `verify_signed` · `did_of` (export-v0, P7 sp5) — a bundle
    sealed and SIGNED by the kernel's own self from a fixed seed (Ed25519 is
    deterministic: the same bytes, the same signature); the verifier's yes and its
    two refusals (a forged signature; a signer whose DID is not its key's); the DID
    of a kernel, an agent, a service from one public key.
  - `backoff` · `park_rule` · `parked_words` · `parked_fact` (bodies-v0, P7 sp6) — the
    kernel governs the bodies it spawns: the wait before the n-th restart (1 s, doubling,
    capped at 30); the PARK law (`input.exits` ISO times · `input.now` · `input.window_s`
    · `input.strikes` → `expect.parked` · `deaths` inside the window · `wait_s`); the plain
    words of a parked body with the human's lever ("Say “restart the <name> body” to try
    again"); the `orreth.body.parked.v1` payload and bytes for a fixed id and clock (the
    last words cut at 600, the kernel's chain, the body's name as correlation).
  - `harness_verdict` · `harness_command` (bodies-v0, P7 sp6) — the run over the rail: a
    case passes when every expected word is in the reply, case folded (the details keep
    the reply's first 300 characters; the marker's note "harness: N passed, M failed");
    the kernel's ask of a body, `orreth.resident.harness.v1` — the run id as ref, the
    cases' hash, the target (the body's own bench), the cases whole, the arm and the
    parent marker only when given, the kernel's chain — for a fixed id and clock.
  - `topic_name` · `peers_from` · `address_home` · `epoch_check` · `world_fact` (cells-v0,
    P7 sp7) — cells = worlds: the topic a fact rides on wears the cell's namespace as a
    bench does; `SPINE_PEERS` read into the peers a cell names (a malformed pair dropped by
    name); an ask that names a CELL at its head ("librarian@two, …" · "two/librarian, …")
    → the home cell and the name, both lower-cased, and the words the home serves (the
    cell address rewritten plain); the fencing law (`current` · `stale` · `future`); the
    `orreth.world.homed.v1` payload and bytes for a fixed id and clock (the world as the
    pointer, the (cell, epoch) hashed, the kernel's chain).
  - `seam_sign` · `seam_verify` (cells-v0, P7 sp7) — the seam's message signed by a kernel
    self from a fixed seed (Ed25519 over the canonical bytes of the message without its
    signature fields; the signer's DID and key beside it) and the seam's gate, one verdict
    in words: `ok`, or the first fence that refused — `unknown signer` (no pin, another
    pin, a DID that is not its key's) · `bad signature` (forged, tampered, another
    specversion) · `replayed` · `too old` / `too new` (the 120 s window, both edges) ·
    `stale epoch` / `future epoch`.
  - `park_words` · `resumed_words` · `lag_words` · `sealed_words` · `rehome_words` · `ceiling`
    (cells-v0, P7 sp7) — the plain words on an ask whose home does not answer, on its
    resuming, on a peer's line ("live" · "N s behind" · "unreachable since HH:MM" · "not
    yet heard"), on the tenth check (sealed, or unsealed with every database named), on a
    re-homing; and the knock ceiling — a token bucket that refills `rate` a second up to
    `burst`, a knock spending one.
  - `profile_words` · `profile_label` · `profile_slice` · `place_default` (profile-v0, P7
    sp8 row 1 — W58) — the human's own words about themselves: what a sentence says (a
    tell of name · place · zone · claim in the person's own spelling; a read; a forgetting
    by field or topic; or nothing — the ask goes on untouched); the provenance label a read
    wears (`you told me` · `I observed` · `the mirror noticed`); the profile as one paragraph
    for the pack's first slot (the newest word per named field, name · place · zone · then
    the claims, the kernel's observation only beside the told place it explains, the whole
    capped at 700); and the weather tool's default — the newest observed coordinates beside
    a live told place, or null.
  - `tool_manifest` · `tool_consequence` (tools-v0, P7 sp8 row 2 — THE TOOL DOOR MOVES) —
    the built-in tools' declarations as DATA: both runners read `spine/tools.v0.json`
    (beside the crew manifest) by `input.name` and must build the same manifest (name ·
    description · input_schema · consequence — `expect.bytes` canonical, `expect.hash` the
    registry's pin, byte-identical to services-v0's `manifest_pin` for the weather tool),
    read the same flags (`expect.ground` · `expect.master`) and the same declared class; and
    class the same CALL the same way (`input.args` → `expect.consequence`: a declaration's
    `held_by` names the argument field and the values that hold at the interlock — a held
    value wears the declared class, any other runs at once, routine). Execution is not
    measured: it is the body's, never the kernel's.
  - `seat_mint` · `seat_verify` · `seat_grants` · `door_needs` · `origin_ok` · `bearer` ·
    `seat_words` · `seat_did_of_key` · `person_did` (seat-v0, P7 sp8 row 3a — THE HUMAN
    SEAT) — the 0006 capability token from a root seed (the exact bytes: the hop with the
    issuer's key and Sig, the chain as canonical strings, the outer Sig over the content;
    the seat's id `seat_<sha256[..16]>`; the wire as unpadded base64url and back); the
    verdicts in fence order (`ok` · `malformed` · `expired` · `foreign authority` · `broken
    chain` · `bad signature` · `amplified` — a widened hop, a child outliving its parent, a
    hop issued by a self that is not the hop above's subject); what a role may do (a person
    reads and writes within the world; the owner and a master also govern); what each door
    asks (open · enroll · retrieve · write · govern); the closed origin; the bearer header;
    the busy and the unseated faces and the words on a seat taken; the person grammar (a
    bare name or the DID, never reissued); a key-bearing self's DID from its key.
  - `desk_transition` · `desk_challenge` · `desk_collect` · `desk_join_id` · `desk_prove` ·
    `desk_collect_ok` · `desk_fuel` · `desk_lease` · `desk_words` · `desk_name` (desk-v0, P7 sp8
    row 3b — THE MACHINE JOIN DESK) — the five statuses and every legal move between them (a
    settled word is never rewritten; `proved` answers only a `challenged`; a challenge may be
    re-issued from any open status); the bytes a joiner signs (`{did, join_nonce}`, the old
    SDK's shape) and the bytes that collect a lease (`{did, join, join_nonce}`); the join's
    id (`join_` + sha256(did · "\n" · nonce)[..12]); the proof's verdict — the declared key
    must derive the DID it claims (a hash), a service's or a person's DID may not knock, the
    signature must stand over the desk's OWN nonce, and the proof's own bytes from a seed; the
    fuel clause (dollars per window; 0 days is the lump); the lease's exact bytes from the
    root's seed (`seat.mint` to the body's DID with grants `retrieve self · write self` and
    the clause in its budget), its id and wire, `ok` at its root, `expired` past its day and
    `foreign authority` at another's; the words (each status, whose word admitted — the crew
    manifest · the standing welcome · a person — the hold's text, the one face); a body's
    name grammar. The `door_needs` cases carry the desk's doors: `/join` · `/join/prove` ·
    `/join/lease` and a join's status are open, the desk's list is a read, and `POST /delta`
    now needs a body's LEASE (seat-v0's one `/delta` case amended the same day).
  - `lever_manifest` · `lever_remedies` · `lever_words` · `read_lever` · `dossier_words` ·
    `remedy_words` · `outcome_words` · `ago_words` (levers-v0, P7 sp8 row 3c — THE REMEDIATION
    RAIL) — the lever catalogue as DATA: both runners read `spine/levers.v0.json` (beside the
    tools') by `input.name` and must build the same manifest (name · description · needs ·
    consequence · for · doors · settles_s — `expect.bytes` canonical, `expect.hash` the pin);
    the remedies a door offers for a watch's metric (served by the door, declared for the
    metric or for any, never grave); the catalogue as the planner reads it; the planner's
    answer read IN the catalogue ("LEVER: <name> <needs>=<value> — BECAUSE: …" · "LEVER: none
    — BECAUSE: …" · a sentence is `null`, the crew's road; marks and one short preface
    forgiven); the dossier in six plain lines (the watch, what it saw lately, who it names,
    the last acts on them, the last time it went red, what was tried this time — every clock
    and every "ago" already in the input, so the law is pure); the planner's ask under a red
    watch; every outcome's words (cured with its cause · self-healed · still-red · cancelled
    · no lever · unserved · pulled · handed to the human · the notice); and `ago_words`.
  - `schema_version` · `schema_tables` (schema-v0, re-base sp1 — THE MIGRATOR's contract): both
    kernels carry the same `SCHEMA_VERSION` and declare the same sorted set of tables (the
    version table among them); a kernel that changes any DDL bumps the number in BOTH kernels
    (2 on 2026-09-29: the indexes — the perf cure; 3 the same day: a watch's rest
    `spine_watches.active` · `rested_by` · `rested_at` and a peer's forgetting
    `spine_peers.forgotten_by` · `forgotten_at` — the honest glass sp2, rule 11's levers recorded).
  - `inbox_parked_fact` · `inbox_advanced_fact` · `inbox_parked_words` · `body_hash` (inbox-v0,
    re-base sp1 — POISON-PARKING): the fact a consumer mints when it parks a poison with its
    evidence (`ref: parked:<id>` · the place on the rail · the evidence's sha256 · the reason,
    the kernel's chain) and the fact a person's advance mints (their chain); the park in plain
    words; the evidence's hash.
  - `joined_fact` (bodies-v0, re-base sp1 — lock 4's last poll): `orreth.body.joined.v1` — a
    body joined this world (a life), the body by name as the pointer, its self as correlation
    and chain.
  - `passages` · `metric_in` · `describe` · `impact_text` (mitl-v0, re-base sp1 — the four doors
    cross): the canon split into passages the pack can carry whole; the metric a watch's words
    name; the ground in lines; the impact ask's text. `declare_kind` (markers-v0): the kind-name
    law — a short lowercase name, its group lowered (`declared` when none), the refusal's words.
