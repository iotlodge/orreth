# Provenance ledger — `agents/`

> **Quarantine lifted — 2026-07-06 (orrery residents).** A 2026-07-05 mid-session
> safeguard swap flipped the session **Fable 5 → Opus 4.8** partway through the
> Universe-view work; JB pinned the boundary from the session audit at the `main.rs`
> `summary()` edit adding `"residents": residents(app)`. The onward work was
> quarantined on `opus/orrery-residents` (`19b0597`, never pushed while unreviewed),
> reviewed line-by-line by Fable 5 (findings R1–R4 below — R1/R2 fixed and
> live-verified in `229d512`), and merged to `main` on JB's green light. Pre-swap
> Fable 5 work through `fac8c5e` needed no review.

> **Quarantine lifted — 2026-07-05.** This tree was built on branch
> `opus/lifeforce-agents` under quarantine (never pushed while unreviewed), reviewed
> line-by-line by Fable 5 (findings F1–F4 below, all fixed and live-verified), and
> merged to `main` on JB's green light (merge `5102ba9`). The protocol it pioneered is
> now the standing rule for every model — see `.claude/skills/orreth-covenant`.

## Why this file exists

On 2026-07-05 we confirmed the mechanism behind days of "silent model swaps":
**Fable 5's safeguards flag some content (broadly — including routine coding,
cybersecurity, and biology work) and auto-switch the runtime to Opus 4.8**, with a
console notice and a support link. The agent work — especially the AgentField-style
security/conformance flavor — trips that broad flag. Rather than fight it, JB chose to
**proceed on Opus 4.8 deliberately, with everything tagged**, so Fable 5 can review
every line once it's available again.

So: every file below carries a `# PROVENANCE:` banner naming its author-model, and this
ledger is the master map.

## Authorship map

| Area | File | Author model | Notes |
|---|---|---|---|
| SDK · crypto | `orreth-agent-sdk/orreth_agent/crypto.py` | **Fable 5** (16:09) | vendored Ed25519, byte-parity canonical JSON; `load_or_create` seed persistence (review fix F1) |
| SDK · client | `orreth-agent-sdk/orreth_agent/client.py` | **Fable 5** (16:09) | FieldClient: join/remember/recall/think/diary; persistent identity home (review fix F1) |
| SDK · chassis | `orreth-agent-sdk/orreth_agent/chassis.py` | **Fable 5** (16:09) | 0015 loop + RuleThink/GovernedThink; per-cycle cost fix (Fable) |
| SDK · init/pyproject | `orreth-agent-sdk/orreth_agent/__init__.py`, `pyproject.toml` | **Fable 5** | package surface |
| Join door (worker) | `../backend/conformance/console_worker.py` | **Opus 4.8** | becky grants root-chained lease on `kind:"join"`; restart-proof dedup + line-buffered log (Fable 5, review fix F3) |
| Named presence | `../backend/plane/crates/orrethd/src/main.rs` | **Opus 4.8** | `/presence` surfaces joined agent names; workforce rides the beat + subtree merge, restart-unique request ids (Fable 5, review fixes F2/F3) |
| Roster names (UI) | `../backend/plane/crates/orrethd/src/window.html` | **Fable 5** (16:09) | render `a.name` in roster/feed/spend; role chip shows home floor (F2) |
| Flavor 1 · prototype | `flavors/01-prototype/*` | **Opus 4.8** | agent.yaml-driven lifeforce |
| Flavor 2 · langgraph | `flavors/02-langgraph/*` | **Opus 4.8** | deterministic StateGraph |
| Flavor 3 · sentinel | `flavors/03-agentfield-sentinel/*` | **Opus 4.8** | AgentField-style conformance sentinel |
| Docs | `README.md`, `../docs/design/0017-*.md` | **Opus 4.8** | guides + dive |

### The Tool Farm (0018) — 2026-07-05, on main (no quarantine: Fable 5 authored)

| Area | File | Author model | Notes |
|---|---|---|---|
| Design | `../docs/design/0018-the-tool-farm.md` | **Fable 5** | services as identities with worldlines; lifecycle = the trust ladder's fourth application |
| Sim · farm | `../backend/conformance/orreth_sim/farm.py` | **Fable 5** | reference state machine; manifest hash pin; illegal moves refused |
| Sim · tests | `../backend/conformance/tests/test_farm.py` | **Fable 5** | lifecycle/worldline, rug-pull door (CVE-2025-54136 shape), decom→discredit→recall |
| Plane · farm | `../backend/plane/crates/orrethd/src/farm.rs` | **Fable 5** | registry + lifecycle legality + meter; rejoin hash check is plane-side |
| Plane · wiring | `../backend/plane/crates/orrethd/src/main.rs` | **Fable 5** | 5 `/farm/*` routes; farm rides the beat + rollup; egress hit enrichment (tags, honest `untrusted` fidelity) |
| Keeper | `../backend/conformance/console_worker.py` | **Fable 5** | charlotte: probe/attest/heartbeat/drop/rejoin/replant + worldline records; persistent resident seeds; gather routed through the Farm; all three floors tended |
| Console | `../backend/plane/crates/orrethd/src/window.html` | **Fable 5** | Farm tab (plant/approve/decom), orrery farm plots, worldline diamonds in the spacetime window, cohort-cut fix (the dead "add knowledge" repair), honest `submitAsk` |
| Demo · farm | `../backend/conformance/demo_farm.py` | **Fable 5** | the narrated reel: real remote MCP planted live + the rug-pull arc read off the worldline |
| Demo · index | `../scripts/demo.sh` | **Fable 5** | the growing demo reel (farm · life · spacetime · knowledge · chassis · model · window) |

### The Stable (0019) — 2026-07-06, on main (no quarantine: Fable 5 authored)

| Area | File | Author model | Notes |
|---|---|---|---|
| Design | `../docs/design/0019-the-stable.md` | **Fable 5** | minds as identities with worldlines; the manifest pins the DEAL (price drift = rug pull); EOL = appointment; JB's locks: the Stable + ada, LiteLLM-direct default |
| Sim · stable | `../backend/conformance/orreth_sim/stable.py` | **Fable 5** | reference state machine (0016 lifecycle + legality); drift door; EOL scan; recommendation ranking |
| Sim · tests | `../backend/conformance/tests/test_stable.py` | **Fable 5** | lifecycle/worldline, price-drift rug-pull, pasture calendar, deprecated-loud/sunset-never, recommendations |
| Plane · stalls | `../backend/plane/crates/orrethd/src/model.rs` | **Fable 5** | stalls beside the legacy registry (stalls win routing); saddle/transition/canary; legality enforced plane-side |
| Plane · meters | `../backend/plane/crates/orrethd/src/pg.rs` | **Fable 5** | `meters` table: write-through + boot restore — usage history survives the daemon |
| Plane · wiring | `../backend/plane/crates/orrethd/src/main.rs` | **Fable 5** | 4 `/stable/*` routes; `usage` + `stable` + `pulse` ride the beat; `/rollup` aggregates the subtree (Pulse == orrery); residents wear per-DID llm vitals incl. the honest zero; ada mined + gated like charlotte |
| Wrangler | `../backend/conformance/console_worker.py` | **Fable 5** | ada: catalog sync (OpenRouter public = intel, routing stays LiteLLM-direct), saddle probe/attest, canary (+ governed metered ping under her own DID when a key exists), drift + EOL staging, recommendations, `~/.orreth/stable/` ledger re-saddles |
| Console | `../backend/plane/crates/orrethd/src/window.html` | **Fable 5** | Stable tab: ladder, saddle-a-mind, pending HITL, pasture calendar, stalls, who-is-thinking (subtree usage, residents included); spend panel stops hardcoding residents to $0 |
| Demo | `../backend/conformance/demo_stable.py`, `../scripts/demo.sh` | **Fable 5** | the reel: real market mind earned by canary; the old pony retired by appointment with ada's recommendation |
| Covenant | `../.claude/skills/orreth-covenant/SKILL.md` | **Fable 5** | rule 5 gains: every resident thinks through the gateway — off-meter cognition is drift |
| Demo site · capture | `../backend/conformance/snapshot_console.py` | **Fable 5** | spectator snapshot: records the live rig's read surfaces as fixtures + bakes the demo page; the capture token is used once and never ships |
| Demo site · shim | `../backend/plane/crates/orrethd/src/window.html` | **Fable 5** | spectator mode (gated on injected flag, absent live): fixture reads, uniform refusal on writes, honest "captured moment" ribbon |
| Demo site · infra | `../infrastructure/cdk/` | **Fable 5** | S3 (private, OAC) + CloudFront static stack — no compute, no origin to probe; optional demo.orreth.ai alias |

### The Parlor (0020) — 2026-07-07, on main (no quarantine: Fable 5 authored)

| Area | File | Author model | Notes |
|---|---|---|---|
| Design | `../docs/design/0020-the-parlor.md` | **Fable 5** | JB's interoperability law made structural: agents (authorized) see data, humans must ask; calling cards = agent UX as data, decoupled from core; zero plane changes |
| Sim · parlor | `../backend/conformance/orreth_sim/parlor.py` | **Fable 5** | the parlor's brain: calling cards, grounded answers from readable state, gather routed to 0014's real duty, audience body for the signed record |
| Sim · tests | `../backend/conformance/tests/test_parlor.py` | **Fable 5** | every resident receives; answers ground in facts; unvoiced organs honest; gather routes; audiences land signed (9 tests) |
| Parlor desk | `../backend/conformance/console_worker.py` | **Fable 5** | `on_parlor`: facts fetch under resident authority, `governed_voice` (authorize→think→meter under the resident's own DID, join floor only, unfueled = grounded fallback), resident-signed audience records |
| Console | `../backend/plane/crates/orrethd/src/window.html` | **Fable 5** | the parlor drawer: click any resident (rail or orrery organ), card-driven chips (glass knows no resident by name), voiced/grounded labels, spectator door sealed with the uniform refusal |
| Demo | `../backend/conformance/demo_parlor.py`, `../scripts/demo.sh` | **Fable 5** | the reel: audiences with charlotte, ada, and vigil; the exchanges read back off the window |

### The recall walk (0014 §4 on the wire) — 2026-07-07, on main (no quarantine: Fable 5 authored)

| Area | File | Author model | Notes |
|---|---|---|---|
| Sim · walk | `../backend/conformance/orreth_sim/librarian.py` | **Fable 5** | `tainted_refs`: the pure wire-shaped lineage walk (source taint + transitive derived_from) |
| Worker | `../backend/conformance/console_worker.py` | **Fable 5** | charlotte hands discredit → queue (`kind: recall`, separation of duties); librarian's `recall_walk` retrieves under her own authority and writes recall versions, annotate-never-rewrite |
| Plane · egress | `../backend/plane/crates/orrethd/src/main.rs` | **Fable 5** | enrichment only (0018 §8 spot, node untouched): hits carry `derived_from`; `recalled`-tagged versions dress as `fidelity: recalled` |
| Parlor | `../backend/conformance/orreth_sim/parlor.py` | **Fable 5** | librarian's card gains "anything recalled?"; she answers with the recall ledger in words |
| Tests | `../backend/conformance/tests/test_flows.py`, `test_parlor.py` | **Fable 5** | wire-shape walk (transitive, clean lineages untouched); recall ledger told honestly (suite 68/68) |
| Demo | `../backend/conformance/demo_recall.py`, `../scripts/demo.sh` | **Fable 5** | the poisoned almanac: planted, cited, derived, discredited, walked, read back off the Window |
| Design | `../docs/design/0014-the-knowledge-loop.md` | **Fable 5** | §4 landing note — what shipped, where the pieces live |

### Organ-DID pinning at join (the stricter R1) — 2026-07-07, on main (no quarantine: Fable 5 authored)

| Area | File | Author model | Notes |
|---|---|---|---|
| Plane | `../backend/plane/crates/orrethd/src/main.rs` | **Fable 5** | `POST /organs/pin` verifies a becky-minted token's chain against the pinned root (reuses `verify_token`, node untouched) and pins organ→DID; `GET /organs` for transparency; `residents()` prefers pins — `pinned: true`, contested retired for pinned organs; mining stays as the honest fallback |
| Worker | `../backend/conformance/console_worker.py` | **Fable 5** | `pin_organs` each beat: idempotent re-pin after daemon restarts (the replant, for identity); refusals grumble once, mined fallback stands |
| Console | `../backend/plane/crates/orrethd/src/window.html` | **Fable 5** | organ hover card shows "· pinned at join" (green) beside the DID |

Closes the R1 follow-up from the orrery-residents review below: the field librarian's
`did_contested: 4` becomes a clean becky-chained pin; earliest-record mining survives
only where nobody has pinned.

### The join door, hardened (JB's lock 2026-07-07) — 2026-07-07, on main (no quarantine: Fable 5 authored)

| Area | File | Author model | Notes |
|---|---|---|---|
| Sim · desk | `../backend/conformance/orreth_sim/joindoor.py` | **Fable 5** | JoinDesk state machine: pending→challenged→proved→staged→done; verifies against the nonce becky ISSUED; approval without proof re-challenges, never mints; desk restart heals by re-challenging |
| Worker | `../backend/conformance/console_worker.py` | **Fable 5** | JOINDOOR replaces the auto-grant; the desk is its own dedup |
| SDK | `../agents/orreth-agent-sdk/orreth_agent/client.py` | **Fable 5** | join() speaks the handshake: signs the challenge, waits at the human gate, tolerates re-challenge; parity 10/10 untouched |
| Plane | `../backend/plane/crates/orrethd/src/main.rs` | **Fable 5** | roster names bind only to COMPLETED joins — a squatter's pending claim names nobody |
| Console | `../backend/plane/crates/orrethd/src/window.html` | **Fable 5** | Requests tab: staged joins show "key proven" + admit / turn away |
| Tests | `../backend/conformance/tests/test_joindoor.py` | **Fable 5** | 7 tests: full handshake mints once; wrong key & tampered nonce turned away; forged approve re-challenges; restart heals; idempotent between transitions |
| Demo | `../backend/conformance/demo_joindoor.py`, `../scripts/demo.sh` | **Fable 5** | `demo.sh gate`: the real SDK agent proves and is admitted visibly; an imposter wearing its DID is found out at the proof |

Known residual (documented, deferred to 0012's signer registry): queue statuses are
unsigned dev plumbing — "approved" is not yet a signed human act. The desk closes the
*identity* hole (key control proven, ungated admission ended); the *signature* on the
human's click lands with the signer registry, same as farm/stable approvals.

### The Shipyard (0021) — 2026-07-07, on main (no quarantine: Fable 5 authored)

| Area | File | Author model | Notes |
|---|---|---|---|
| Design | `../docs/design/0021-the-shipyard.md` | **Fable 5** | a universe that grows by conversation — 0009's provisioner, first wire landing, honest dev-rig limits named |
| Sim · brain | `../backend/conformance/orreth_sim/shipyard.py` | **Fable 5** | pure planning: slug validation, port allocation, TierProfiles with the rig's own dials |
| Sim · grammar | `../backend/conformance/orreth_sim/parlor.py` | **Fable 5** | `parse_grow` + becky's fields-question-first flow; `verbatim` flag — a governed voice phrases facts, never rewrites protocol (caught live: the voiced pass turned the fields QUESTION into an "as is" statement) |
| Dock crew | `../backend/conformance/console_worker.py` | **Fable 5** | stage → human gate → `docker run` on the rig network; `~/.orreth/shipyard/floors.json` ledger; replant at boot; worker tends every dynamic floor |
| Plane | `../backend/plane/crates/orrethd/src/main.rs` | **Fable 5** | CORS opened (capability stays the boundary); each floor's port rides the beat for one-glass steering |
| Console | `../backend/plane/crates/orrethd/src/window.html` | **Fable 5** | one glass, every floor: api() base, worlds are doors, breadcrumbs; launch/scrap gate for staged plans; orrery pauses on hover; spectator shim matches pathname |
| Rig | `../scripts/dev.sh` | **Fable 5** | stop removes dynamic hulls (replant restores on start); status lists them |
| Tests | `../backend/conformance/tests/test_shipyard.py` | **Fable 5** | plan/ports/profiles/name-safety + the grow grammar incl. the fields question (suite 80/80) |

Proven live end-to-end: "create ecosystem retail" → becky's question → "with fields
web, pos" → staged plan `e:retail on :4503 with web:4504, pos:4505` → LAUNCH → three
real containers, all healthy, beating into the apex orrery with their ports; one-glass
descent onto e:retail and breadcrumb ascent verified in Chrome, zero JS errors.

### Chassis maturation (0015 backlog) — 2026-07-08, on main (no quarantine: Fable 5 authored)

| Area | File | Author model | Notes |
|---|---|---|---|
| Sim · graphspec | `../backend/conformance/orreth_sim/graphspec.py` | **Fable 5** | NEW: GraphSpec v0 (0008 §2) sim-first — the chassis as a content-addressed, steward-signed artifact with a bijective narrative; `compile_chassis` binds only spec-named skills and refuses at save (unbound skill, tampered id, broken bijection); schema stays out of `contracts/` until 0008 is blessed |
| Sim · chassis | `../backend/conformance/orreth_sim/chassis.py` | **Fable 5** | class escalation on critic uncertainty: the `ladder` profile knob — every RETRY climbs one rung; no ladder = fixed class, unchanged |
| Sim · librarian | `../backend/conformance/orreth_sim/librarian.py` | **Fable 5** | `retry_parked` closes the parked→librarian→retry circuit automatically; `lookup_skill` hands back claims wearing their state; `handled_open` is the retry worklist |
| Tests | `../backend/conformance/tests/test_flows.py` | **Fable 5** | 4 new: escalation ladder, auto-close (idempotent, whole-arc lineage), GraphSpec compile (least privilege + bijection), refused-at-save (suite 86/86) |
| Design | `../docs/design/0015-orreth-agent-the-chassis.md` | **Fable 5** | "Matured (2026-07-08)" section; remaining: persona as cascaded soft standard |

### The crew (demo + reel) — 2026-07-08, on main (no quarantine: Fable 5 authored)

| Area | File | Author model | Notes |
|---|---|---|---|
| Demo | `../backend/conformance/demo_workforce.py` | **Fable 5** | NEW: three SDK agents join at the hardened gate (wren RETURNS — same seed, same DID; reboot ≠ death) and each works one chassis objective on RuleThink with a real floor-reading skill — scribe-signed RunRecords, ships in orbit, honest $0 vitals |
| Reel | `../scripts/demo.sh`, `../backend/conformance/console_worker.py`, `../backend/plane/crates/orrethd/src/window.html` | **Fable 5** | `crew` on the reel and the Console's 🎬 chips; window.html also gains spectator guards (a photograph never goes stale — heard_at dimming and beat-age lines skip under ORRETH_DEMO) |

### Orrery residents (Opus 4.8, quarantined) — 2026-07-05, branch `opus/orrery-residents`

**The swap boundary.** Everything below was authored by **Opus 4.8** after the safeguard
flipped the session mid-work. JB fixed the boundary from the session audit: the first
Opus edit was `summary()` in `main.rs` gaining `"residents": residents(app)` in the
upward beat. Two files were touched, both already-existing; no new files, no PROVENANCE
banners inside the code. **Quarantined on `opus/orrery-residents`, never pushed.**

| Area | File | Author model | Notes |
|---|---|---|---|
| Plane · residents | `../backend/plane/crates/orrethd/src/main.rs` | **Opus 4.8** | `residents(app)` builder mining charlotte/librarian DIDs from signed records; per-organ vitals; `vitals` map + `bump()` counters (refusals, beats_heard, beats_up); residents on the beat, presence, rollup |
| Console · orrery | `../backend/plane/crates/orrethd/src/window.html` | **Opus 4.8** | organ orbit shells (rigid evenly-spaced capped rings + `+N`), per-role colors, MCP recolor to amber diamonds, live-vitals hover, legend, dot sizing, and the render-signature fix (structure-only → orrery no longer resets its rotation each tick) |

**What Fable 5 should scrutinize in the onward (Opus's own flags):**
1. **Comment prose likely tripped the safeguard.** JB's hypothesis: the flowery NLP in
   code comments is a classifier trigger. The Opus edits kept that register. Fable may
   want to flatten comment tone repo-wide as a mitigation.
2. **`residents()` mines identities from record authorship** — confirm charlotte = the
   author of `service`-tagged records and librarian = `knowledge`-tagged is a sound,
   non-spoofable mapping, and that a workforce agent can never masquerade as an organ.
3. **New plane counters are process-local and unsigned** (`vitals`) — they reset on
   daemon restart and are display-only. Confirm that is acceptable (they never feed
   governance decisions), matching the `refusals`/`beats` intent.
4. **Render-signature change** drops `records`/vitals/`calls` from the redraw trigger.
   Confirm no view can now go stale in a way that violates one-world-one-picture.

### Fable 5 review findings — 2026-07-06 (orrery residents)

Full read of `19b0597` against the covenant, with the ingestion, beat, and render paths
traced in source. Verdict: on vision in intent; two of Opus's four flags confirmed as
real drift and **fixed by Fable 5 on this branch** before merge (the F1–F4 precedent).

**R1 · Flag 2 — organ DID mining was spoofable — FIXED (Fable 5).** Ingress verifies
every record's author signature ("Sourced or nothing", `orreth-node/src/lib.rs:124`),
so a mined DID is authentic — but tags are author-chosen, so *any* writer could tag a
record `service`/`knowledge` and surface its own DID as charlotte/the librarian.
Worse, the `.or()` fold made the last record in BTreeMap (content-hash) order win —
arbitrary under multiple authors. Fixed: the claim now anchors to the **earliest**
tagged record (deterministic, stable under later writes; ties break by author), and if
more than one DID has ever signed such records the entry carries `did_contested: N`
and the Console hover says so — honest display instead of a silent pick. A plane-side
config pin (organ DIDs granted at join, like becky = trust root) is the stricter
future alternative; residents stay display-only either way.

**R2 · Flag 4 — render-signature staleness — FIXED (Fable 5).** Confirmed real: world
and tool hover cards baked records/runs/usd/calls into the DOM at render time, the
"N memories" / "you" labels froze between structural changes, and agent counts above
the ships cap never refreshed the `+N` marker. Fixed by extending Opus's own `ocRes`
pattern: `oc`/`ocPlot` now read live from `topoCache` at hover time, and counter text
(records, field agent counts, ships `+N`) updates in place via `refreshCounters()`
every poll — the orbit keeps turning, and no orrery number can disagree with the rail.

**R3 · Flag 3 — vitals — ACCEPTED.** Process-local, unsigned, reset on restart, read
only by `residents()` (presence/beat/orrery) — display, never governance. All three
refusal arms that gained `bump()` keep a byte-identical status and body, so refusal
still wears one face (0002 §4). Known nits: the tally doesn't cover every refusal arm
(undercount only), and `residents()` scans all records per 5s beat — fine at demo scale.

**R4 · Flag 1 — comment prose — flattened in the two Opus-touched files only** (JB's
call, 2026-07-06): new-code comments neutralized; the rest of the repo keeps its voice.

Core integrity: the commit touches exactly `orrethd/src/main.rs`, `window.html`, and
this ledger — orreth-node, orreth-store, crypto crates, and contracts untouched; no
canonicalization changes, so parity is not implicated. No new files, ledger updated
in-commit, branch never pushed. The provenance protocol held end to end.

## What Fable 5 should scrutinize hardest (Opus's own flags)

1. **The join door is open.** `FieldClient.join()` treats a lease as granted the moment
   the worker resolves the request, and the worker (becky) mints a lease for *whatever DID
   asks*. That is fine for a demo, but it is **not** the governed, HITL-gated join JB's
   vision implies. A real join should verify the requester controls the DID (a signed
   nonce challenge) and, on governed floors, hold for human approval (0012 queues).
2. **Crypto parity is load-bearing.** The SDK's `canonical()` must produce byte-identical
   output to the Rust plane's canonicalization forever, or signatures silently fail. There
   is a parity test, but Fable should confirm it covers non-ASCII + nested ordering.
3. **The sentinel probes the universe's own refusals.** It is defensive self-testing of
   JB's own governance (does retrieval refuse uniformly? does the clock reject backdating?).
   Confirm the framing and the skills stay strictly on the "verify my own invariants" side.
4. **RuleThink is a stub cognition.** It is deterministic and keyless by design (so an
   agent runs anywhere), but it is not "smart" — the plans it makes are mechanical. The
   governed path (GovernedThink → model plane) is the real mind; RuleThink is the floor.

## Fable 5 review findings — 2026-07-05

Live-repro review on JB's rig: repeated `dev.sh agent 2 --once`/`--forever` runs, a
universe docker restart underneath a running worker, and a full read of the diff against
`main`. Verdict: the join path works and crypto parity holds, but the **living-identity
half of the lifeforce story is unimplemented**, presence aggregation stops one floor
down, and the join door goes deaf after a daemon restart. All three are now fixed —
F3 in the first review pass, F1/F2 on JB's green light (2026-07-05, same day).

### F1 · No identity persistence — every run mints a new agent (all three flavors) — FIXED

`FieldClient.__init__` defaults to a fresh keypair (`client.py:39`), and no runner passes
one — `01-prototype/run.py:33`, `02-langgraph/run.py:45`,
`03-agentfield-sentinel/run.py:29`. The scribe (`client.py:42`) is likewise reborn every
process. Each `dev.sh agent …` invocation therefore creates a new did:key → new join
request → new lease → new "birth" memory → one more permanently idle ghost in the
roster, and the orrery's agent count only ever grows (`summary()` counts distinct DIDs
across RunRecords).

The mechanism exists and is even tested — `KeyPair(seed)` round-trips, and
`test_parity.py:58-61` asserts "seed persists the identity" — it is simply never wired.

**Fixed (Fable 5):** `KeyPair.load_or_create(path)` in `crypto.py` (0600 perms), and
`FieldClient` now defaults `home=~/.orreth/agents` — agent + scribe seeds persist under
`home/<name>/`, so every flavor gets a stable DID with zero flavor-code changes
(`home=None` keeps the ephemeral path for tests). A re-join by the same DID lands on the
same workforce row (the roster keys by DID), and the "birth" memory dedups naturally
(content-addressed id). Persisting the *lease* to skip the queue entirely stays future
work — re-joining through becky keeps the names map warm after daemon restarts.

### F2 · Workforce roster is floor-local — the universe Console never shows leased agents — FIXED

`/presence` builds its workforce list purely from RunRecords held on the answering node
(`main.rs:484-508`). Agents join and diary at the field (:4502); the universe Console
(:4500) reads its own empty runs, so its Workforce panel stays empty forever — while the
orrery, fed by `/topology`'s cascaded child beats, shows those same agents as ships. One
world, two contradicting pictures.

**Fixed (Fable 5):** the per-agent aggregation is factored into `local_workforce()`
(each entry now carries its floor's `scope`), `summary()` sends it up the beat, and
`/presence` merges its own roster with every descendant beat's — so the universe Console
shows the whole subtree's leased agents, and the roster finally agrees with the orrery.
The Console's role chip shows the agent's home floor (`f:prod`) instead of a generic
"workforce".

### F3 · becky goes deaf after a daemon restart — FIXED (Fable 5, this pass)

`requests_submit` issues sequential ids (`req-{len+1}`, `main.rs:591-599`) from an
in-memory queue. A docker restart wipes the queue, so the first new join is `req-1`
again — an id the still-running host worker's `seen` set already holds. Becky silently
skips every recycled id; agents time out with "becky's join door is not tending".
Compounding it, the worker's stdout was block-buffered under nohup, so `worker.log` sat
at 0 bytes and becky *looked* dead even while alive (observed live: running worker,
empty log).

**Fixed in `console_worker.py`:** dedup keyed by `(id, at)` — the submission timestamp
makes keys unique across daemon restarts — and stdout reconfigured line-buffered so the
log breathes. Becky also now `os.setsid()`s into her own session at startup: `dev.sh
start/restart` can linger after printing status (background-worker exit quirk), and a
Ctrl-C aimed at that lingering script used to SIGINT the whole process group — becky
included. Verified live: a worker now survives an INT that kills its entire launch group. **Daemon follow-up — also done (Fable 5, with JB's green light):** request
ids now carry the submission second (`req-{n}-{ts}`), unique across restarts, so no
consumer can be fooled by recycled ids. `/presence`'s names map still rebuilds from the
in-memory queue, but persistent identities re-join on their next run, which re-warms it.

### F4 · Core-integrity audit — what this branch actually touches

Full `git diff main...HEAD` reviewed. Exactly **four** pre-existing files are modified,
all matching this ledger's claims; everything else is net-new under `agents/` plus
design doc 0017.

| File | Change | Assessment |
|---|---|---|
| `backend/conformance/console_worker.py` | join door: becky mints root-chained leases | as declared; F3 fix now also lands here |
| `backend/plane/crates/orrethd/src/main.rs` | +6 lines in `/presence` only (names map) | display-only; names come from **unsigned** join requests, so they are requester-chosen (consistent with flag 1) |
| `backend/plane/crates/orrethd/src/window.html` | 3 lines rendering `a.name` in roster/feed/spend | cosmetic |
| `scripts/dev.sh` | joindoor, `agent` subcommand, door status line | dev rig only |

**Untouched:** the `orreth-node`, `orreth-store`, and crypto crates, `contracts/`,
`orreth_sim` internals, `infrastructure/compose.yaml`. The governed core is unaltered.

### Status of Opus's own flags

1. **Open join door** — confirmed real: becky leases any DID that asks, and roster names
   ride unsigned requests. Acceptable for the demo floor only; a nonce challenge plus
   0012 HITL gating is required before any governed floor. **CLOSED 2026-07-07** —
   exactly that mechanism landed (JB's lock: HITL gate + nonce challenge; see "The
   join door, hardened" above).
2. **Crypto parity** — verified: the cases cover key order, non-ASCII, nesting, unicode,
   and a cross-verifier signature; suite run during this review, **10/10 green**.
3. **Sentinel framing** — read in full: every probe *attempts* a violation and passes
   only when the universe refuses it; it detects and files, never enforces. Framing holds.
4. **RuleThink stub** — acknowledged; fine as the keyless floor, `GovernedThink` is the mind.
