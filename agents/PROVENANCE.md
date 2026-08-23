# Provenance ledger — `agents/`

> **Swap recorded — 2026-07-25 (0041 sp3/sp4, the Epoch).** Safeguards flagged the
> sp3 drift-detection work repeatedly and the session ran on as **Opus 4.8**. Opus
> completed sp3 and — deviating from the covenant's quarantine rule — committed it
> straight to `main` and pushed (`4bc2b08`, untagged), then drafted sp4 (the revert
> door) in the working tree. Recorded here, not erased. Fable 5 reviewed both
> line-by-line the same afternoon (findings D1–D4, end of this file — all fixed;
> D1 was caught **standing live in the rig**: the accusation loop had already
> re-adopted the very drift it was built to catch). The sp4 commit lands with the
> fixes on JB's word.

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

### The Universe Brain, spoonfuls 1–8 (0022–0029) — 2026-07-10/11, on main (no quarantine: Fable 5 authored)

One dive, eight spoonfuls, all Fable 5: the Memory Construct's Phase 1 (0022 §8 —
runs/requests persistence, presence memo, meter metabolism, orphan sweep), the
Librarian's seats + self-dialog + exchange dial + citations (0023), markers & the
severity lanes (0024), the Human Profile (0025), the Purge's governance (0026),
the Fingertip (0027 — thought.graph made concrete), Workspaces & the Improvement
Engine (0028 — rooms in the glass, a gardener for the assets), and Multimodal
Capability (0029 — upload-is-an-ask, the parked eye, the pinned-organ roster fix).

| Area | File | Author model | Notes |
|---|---|---|---|
| Design | `../docs/design/0022…0026-*.md` | **Fable 5** | five design docs, all citing the Universe-Brain session's JB locks (R1–R11) |
| Sim · markers | `../backend/conformance/orreth_sim/markers.py` | **Fable 5** | NEW (0024): marker records derive-from-what-they-mark; R6 lane table; "remember this" parser |
| Sim · profile | `../backend/conformance/orreth_sim/profile.py` | **Fable 5** | NEW (0025): claims trusted/untrusted by asserter; withdrawal = lineage-death; parsers |
| Sim · purge | `../backend/conformance/orreth_sim/purge.py` | **Fable 5** | NEW (0026): seal records (dark, reversible), the honest quorum hold, the door's immune memory |
| Plane | `../backend/plane/crates/orrethd/src/main.rs`, `pg.rs` | **Fable 5** | 0022 §8 persistence + `/tombstone` door (token-guarded, uniform refusal) + `purged` table with boot-restore |
| Worker | `../backend/conformance/console_worker.py` | **Fable 5** | seats, self-dialog legs, profile routes, marker writes, consent-path shred, purge stage-and-hold+seal, gather immunity |
| Sim · fingertip | `../backend/conformance/orreth_sim/fingertip.py` | **Fable 5** | NEW (0027): workflow templates (refused-at-save, human-at-the-top gate), Orchestration (stamp → dispatch → review → assemble), sliver contract, PortfolioMonitor standing job |
| Sim · improver | `../backend/conformance/orreth_sim/improver.py` | **Fable 5** | NEW (0028): versioned assets (siblings, never successors), evidence with receipts, kind-by-diff grading, lanes route adoption, no-op refused |
| Sim · workspaces | `../backend/conformance/orreth_sim/parlor.py` | **Fable 5** | (0028) card declares the room; four rooms compose typed panels (stat · bars · list · doc); medium+ wears amber (0024 badge) |
| Glass | `../backend/plane/crates/orrethd/src/window.html` | **Fable 5** | (0028) ⛶ full-screen parlor, blind panel renderer with escaping, amber chips |
| Worker | `../backend/conformance/console_worker.py` | **Fable 5** | (0027) objective/sliver kinds, HITL question leg, entitlement asks, review markers, monitor beat · (0028) workspace verb, improver beat, governance grading, lane routing |
| Sim · artifacts | `../backend/conformance/orreth_sim/artifacts.py` | **Fable 5** | NEW (0029): upload bars (one refusal face), artifact + extraction records with lineage, the parked eye, `read-document` skill |
| Plane · roster | `../backend/plane/crates/orrethd/src/main.rs` | **Fable 5** | (0029) pinned organs always show their row — honest zeros on quiet floors (rule-7 fix, JB 2026-07-11) |
| Glass · drop zone | `../backend/plane/crates/orrethd/src/window.html` | **Fable 5** | (0029) card-declared drop zone; client precheck mirrors the floor's bars |
| Tests | `../backend/conformance/tests/test_flows.py`, `test_parlor.py`, `test_fingertip.py`, `test_improver.py`, `test_artifacts.py` | **Fable 5** | suite 114/114 through spoonful 8 |

### The Human's Seat (0030) — 2026-07-12, on main (no quarantine: Fable 5 authored)

| Area | File | Author model | Notes |
|---|---|---|---|
| Design | `../docs/design/0030-the-humans-seat.md` | **Fable 5** | the vision-sync dive: O·I·O·T ladder canon, the plan gate, the seat |
| Sim + worker | `../backend/conformance/orreth_sim/fingertip.py`, `console_worker.py` | **Fable 5** | sp1: plan gate (curate → stage → human approves → fan; plan lands as a signed record), sliver→intention rename w/ wire read-compat |
| Glass | `../backend/plane/crates/orrethd/src/window.html` | **Fable 5** | sp1: the objective gate — plan summary + "fan the plan"/"decline" at the human's queue · sp2: the Objectives tab — state it, staged plans, answer-in-the-card, reports with severity chips; renders only from /requests; mid-answer outranks the refresh · sp3: place-as-spine — URL carries floor+tab (popstate honored), the parlor pins its floor and survives navigation, every surface names its place, Farm/Stable sectioned by floor, cascade-below checkboxes |
| Tests | `../backend/conformance/tests/test_fingertip.py` | **Fable 5** | gate test (nothing fans unapproved); suite 115/115 |
| Plane · window cfg | `../backend/plane/crates/orrethd/src/main.rs` | **Fable 5** | sp4: `/window/cfg` GET + chain-verified pin POST — the glass's read-only viewer capability, organ-pin pattern |
| Worker · charter | `../backend/conformance/console_worker.py` | **Fable 5** | sp4: `window_charter` pins the viewer cfg per floor on the beat (persistent window-viewer seed); sp2: the human's answer rides into the assembly |
| Glass · the window | `../backend/plane/crates/orrethd/src/window.html` | **Fable 5** | sp4: self-healing cfg, subtree lanes (ancestry+self+descendants), beads on their own scope's lane, kind-binned clusters (markers/milestones never fold), click-pins-the-card, legend, hashchange reloads only on a NEW token |

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

## Fable 5 net-new files — 2026-07-14 (0034 sp1, the continuity template)

| File | Author | Note |
|---|---|---|
| `backend/conformance/orreth_sim/continuity.py` | Fable 5 (claude-fable-5) | 0034 §2/§3/§6 — the continuity template's organs (dignity vector, retention regime as 0033 §5 contracts, label canon composer); banner in file |
| `backend/conformance/tests/test_continuity.py` | Fable 5 (claude-fable-5) | the template's conformance tests; banner in file |

## Fable 5 net-new files — 2026-07-14 (0034 sp3, the Mirror)

| File | Author | Note |
|---|---|---|
| `backend/conformance/orreth_sim/mirror.py` | Fable 5 (claude-fable-5) | 0034 sp3 — the assessment flow over audiences (assess/observations/friction_note/interop ledger); assessor ≠ assessed (0005); banner in file |
| `backend/conformance/tests/test_mirror.py` | Fable 5 (claude-fable-5) | the Mirror's conformance tests; banner in file |

## Fable 5 net-new files — 2026-07-17 (0022 Phase 2, the meaning axis — Phase E)

| File | Author | Note |
|---|---|---|
| `backend/conformance/orreth_sim/meaning.py` | Fable 5 (claude-fable-5) | 0022 §4 — the meaning axis: local fastembed ONNX (bytes-local, JB's §10 lock), hybrid weighted-RRF, trust-weighted rerank (`recalled` ranks dead), coordinate/aperture pulls, cross-source contradiction v1, repeats-by-meaning; banner in file |
| `backend/conformance/demo_meaning_axis.py` | Fable 5 (claude-fable-5) | the meaning demo — retrieval's second sense, five scenes, pure sim; banner in file |
| `backend/conformance/tests/test_meaning.py` | Fable 5 (claude-fable-5) | the axis's conformance tests (skip honestly when the axis is dark); banner in file |

## Fable 5 net-new files — 2026-07-22 (0037 sp1, the Estate — the resident stands)

| File | Author | Note |
|---|---|---|
| `backend/conformance/orreth_sim/estate.py` | Fable 5 (claude-fable-5) | 0037 §1–§2 — allen's typed door (0030 enforced: agent objectives refused, lineage walkable or no entry) + the acceptance gate (adopts before he creates, locked 2026-07-22); banner in file |
| `backend/conformance/tests/test_estate.py` | Fable 5 (claude-fable-5) | sp1 conformance: universe-parent allowance (one-hop chain), the teaching refusals, the gate, the parlor seat; banner in file |

## Fable 5 net-new files — 2026-07-22 (0038 sp1, the Stacks — the baseline breathes)

| File | Author | Note |
|---|---|---|
| `backend/conformance/orreth_sim/stacks.py` | Fable 5 (claude-fable-5) | 0038 §1–§2 — the one-truth law by construction: ingest once, project (rebuildable/disposable), retrieve with a relevance floor, answer with citations; eco assets planted versioned; banner in file |
| `backend/conformance/tests/test_stacks.py` | Fable 5 (claude-fable-5) | sp1 conformance: one record per document · rebuild-identical projection · the purge's reach · cited answers · honest unknowns; banner in file |

## Fable 5 net-new files — 2026-07-22 (0038 sp2, the Dispatcher)

| File | Author | Note |
|---|---|---|
| `backend/conformance/orreth_sim/dispatcher.py` | Fable 5 (claude-fable-5) | 0038 §3 — the reflex: deterministic classify, rules-as-data standard, loud fallback, choices-as-records (the RL substrate); banner in file |
| `backend/conformance/tests/test_dispatcher.py` | Fable 5 (claude-fable-5) | sp2 conformance: standard plants once · shapes deterministic · loud fallback with both truths · signed choice ledger; banner in file |

## Fable 5 net-new files — 2026-07-22 (0038 sp3, the rivals)

| File | Author | Note |
|---|---|---|
| `backend/conformance/orreth_sim/rivals.py` | Fable 5 (claude-fable-5) | 0038 §2 — rerank · graph (edges carry their chunk's provenance) · hybrid; one answer_as door; banner in file |
| `backend/conformance/tests/test_rivals.py` | Fable 5 (claude-fable-5) | sp3 conformance: walking beats distance on relational asks · precision sharpens · one truth across every row; banner in file |

## Fable 5 net-new files — 2026-07-22 (0038 sp4 part 2, the tournament)

| File | Author | Note |
|---|---|---|
| `backend/conformance/orreth_sim/tournament.py` | Fable 5 (claude-fable-5) | 0038 §4/§6 — the last three flows (honest eye · tactic-within · decompose-recompose) · 0033 grading · 0005 standings · promotion as PROPOSAL; banner in file |
| `backend/conformance/tests/test_tournament.py` | Fable 5 (claude-fable-5) | sp4 conformance: seven rows one door · deterministic grading · floors flagged · promotion carries evidence never enactment; banner in file |

## Fable 5 net-new files — 2026-07-23 (0039 sp1, the two books stand)

| File | Author | Note |
|---|---|---|
| `backend/conformance/orreth_sim/canon.py` | Fable 5 (claude-fable-5) | 0039 §2/§7 — the record-class registry as a Canon asset (charter attributes per class); floors-first classification; the privacy floor; the census; banner in file |
| `backend/conformance/tests/test_canon.py` | Fable 5 (claude-fable-5) | sp1 conformance: registry once · floors-first · the smuggle test · the census; banner in file |

## 0041 sp3/sp4 — the swap mid-dive (2026-07-25), Fable 5 review findings D1–D4

Safeguards flagged the sp3 work repeatedly; the session ran on as **Opus 4.8**.
Boundary: sp1/sp2 (`25d05e8`, `cb0020a`) are Fable 5; sp3 (`4bc2b08`) and the sp4
working tree are Opus 4.8, modifying `backend/conformance/console_worker.py` and
`backend/plane/crates/orrethd/src/window.html` (no net-new files). Deviation
recorded honestly: sp3 was committed straight to `main` and pushed, untagged — no
quarantine branch. Fable 5 reviewed both spoonfuls line-by-line the same afternoon.

| # | Finding | Fate |
|---|---|---|
| D1 | `_recent_gate_word` dated an adoption by the card's **submission second** (`req-N-<ts>`), not the human's click — a gate is allowed to wait for its human, so a slow click made the next epoch cut accuse the obeyed revert as fresh drift; the false card's `restore` was the **drifted** head wearing the "revert to the signed machine" label. **Witnessed standing in the rig**: req-320 (honest revert) → req-322 (false accusation, clicked in good faith, re-adopted the drift as `282856f6…`) → req-326 (third card). | **Fixed by Fable 5**: every Canon-moving resolution now stamps `result.resolved_at` (rides the queue verbatim, survives worker restarts); `_recent_gate_word` prefers it, falling back to the submission second only for pre-stamp cards. Stamped: drift revert, improvement high+medium adoptions, standard promotion, estate adoption. |
| D2 | An approved revert whose floor was dark resolved the card `done` ("try again when it beats") — but a done card has no button: the human's word was eaten (the no-op-button law, 2026-07-23). | **Fixed**: the approval stands unresolved; the round retries each pass (print-once) until the floor beats and the revert lands. |
| D3 | `_PENDING_REVERT` was popped before the epoch record's write — a refused wire lost the revert citation forever. | **Fixed**: re-stashed on refusal. |
| D4 | Lag cards (nothing to restore) wore the "revert to the signed machine" button in the glass. | **Fixed**: label reads "acknowledge the lag" when `restore` is empty (needs the next orrethd rebuild to serve — `window.html` is `include_str!`). |

Flagged, not fixed (pre-existing, 0038 sp4): `on_standard_promotion` plants v2
without `adopted_from`/`derived_from` — an orphan in the lineage walk; queued for a
later pass. sp3's detection core (fingerprint, cut, lag/reconcile, staged findings)
reviewed sound. 232/232 conformance tests green after the fixes.

## Fable 5 net-new files — 2026-07-25 (0042 sp1, the Deed — the shelf and the family)

| File | Author | Note |
|---|---|---|
| `backend/conformance/orreth_sim/deed.py` | Fable 5 (claude-fable-5) | 0042 §1–§5 — effect classes as one Canon asset (T0–T3 ceremony locked); the record family intent→authorization→attempt→receipt→observation→reconciliation→closure, chained and signed; observer ≠ actor refused (0005 grown up); the epoch clasp on every attempt (0041); idempotency remembers across deeds; compensation only on a fresh human word, itself a deed; banner in file |
| `backend/conformance/tests/test_deed.py` | Fable 5 (claude-fable-5) | sp1 conformance: shelf plants once · whisper floor both directions · full family in order · sole-witness refusal · wrong world won't close · gate-then-epoch · the key remembers · priced compensation; banner in file |

## Fable 5 — 2026-07-25 (0042 sp2, allen swears his deeds)

| File | Author | Note |
|---|---|---|
| `backend/conformance/orreth_sim/estate.py` | Fable 5 (claude-fable-5) | sp2 — `apply_deed`: the estate create walks the family (gate + charter refusals unchanged · human word opens consequence · template hash = the idempotency key · epoch clasp · distinct-seat observation · 0037 §4 diff = the reference reconciliation · wrong world stays open, compensation staged) |
| `backend/conformance/orreth_sim/deed.py` | Fable 5 (claude-fable-5) | sp2 fix — intent carries its OPENING ordinal (two same-worded intents in one second are two deeds; the content-address collision, canary's lesson applied) — caught by sp2's own conformance test before it ever ran live |

## Fable 5 — 2026-07-25 (0042 sp3, the second class — outbound publishing, live)

| File | Author | Note |
|---|---|---|
| `backend/conformance/console_worker.py` | Fable 5 (claude-fable-5) | sp3 — `on_publish`: the T2 witnessed walk on the wire (card stages with the intent pinned · the human's word = authorization citing the request · allen's seat attempts ONE gated write via the toolroom hand under the standing epoch · receipt verbatim · the LIBRARIAN's seat fetch-backs through the public door · hashes reconcile · closure or the unpublish STAGED as another publish card walking the same family). PROVEN LIVE: req-330 → https://demo.orreth.ai/deeds/first-deed.json, witnessed, closed whole. Honest boundary: the live failure/compensation walk is sp4's subject (machinery coded, sim-proven). |
| `backend/plane/crates/orrethd/src/window.html` | Fable 5 (claude-fable-5) | sp3 — pgate: "publish it / walk it back / not this" + the card's package readable at the gate (serves on next rebuild) |

## Fable 5 — 2026-07-25 (0042 sp4, compensation and the priced ceremony — the dive closes whole)

| File | Author | Note |
|---|---|---|
| `backend/conformance/console_worker.py` | Fable 5 (claude-fable-5) | sp4 — the VERIFY door (`verify: true` on the publish card: re-observe a standing deed through the public door, no hand moves) + the mismatch reply names the differing bytes. PROVEN LIVE, the full loop: first-deed.json SWAPPED out-of-band by an outside hand → verify walk CAUGHT the differing hashes → unpublish STAGED (req-332) → JB's fresh word → walked back, absence witnessed, comp deed closed → published anew (fresh family) on JB's second word. T0's quiet floor sim-proven (sp1); the glass wears the deed's gates (pgate). |

## Fable 5 net-new files — 2026-07-25 (the drift drill joins the reel)

| File | Author | Note |
|---|---|---|
| `backend/conformance/demo_drift.py` | Fable 5 (claude-fable-5) | The 0041 drill, repeatable: rogue write → the epoch beat stages the card → the human's key (glass click or the runner's word) → the sibling restored → THE SILENCE asserted (an obeyed word must stage nothing — fails loudly if the accusation loop returns) → THE PARITY HANDSHAKE (rule 6 live: Rust-served body re-hashed by Python's canonical bytes must equal its id). First run 2026-07-25: whole, exit 0. Banner in file. Companion: the parked rule-9 question (write-time re-hashing in orreth-node) recorded in docs/decisions. |

## Fable 5 — 2026-07-26 (road step 2 — the epoch's laws enter the sim; the 0038 orphan ends)

| File | Author | Note |
|---|---|---|
| `infrastructure/cdk/stacks/orreth_demo_stack.py` | Fable 5 (claude-fable-5) | The demo deploy stops eating the world's memory: `exclude=["deeds/*", "media/*"]` on the BucketDeployment — what the universe published (first-deed.json, the campaign films) rides out every prune. First protected deploy verified live 2026-07-26. |
| `backend/conformance/console_worker.py` | Fable 5 (claude-fable-5) | The orphan-lineage fix (0038-era, flagged at 0041's close): the tournament's improvement card now carries `proposal_ref` — the standings record it argued from — and `on_standard_promotion` plants v2 with `adopted_from`/`derived_from` naming it. A promoted standard is never an orphan; legacy cards without the ref plant as before, their resolved words untouched. |
| `backend/conformance/orreth_sim/epoch.py` | Fable 5 (claude-fable-5) | NET-NEW — 0041's machinery as the executable spec: the fingerprint, the cut (genesis/turned/held), the gate word dated by its landing (the req-322 law), drift-wears-no-levers, revert-to-sibling on a human's word only, lag amber-then-loud-once, the roll-up citing its floors. The head lives on the shelf itself; every clock is explicit. Banner in file. |
| `backend/conformance/tests/test_epoch.py` | Fable 5 (claude-fable-5) | NET-NEW — ten conformance tests, THE SILENCE after a cited revert among them (the drill's assertion, now suite-held). Suite 244→254. Banner in file. |

## Fable 5 — 2026-07-26 (the room reads as a human's again; the boundary gets one page)

| File | Author | Note |
|---|---|---|
| `backend/plane/crates/orrethd/src/window.html` | Fable 5 (claude-fable-5) | JB's catch: the librarian's room rendered text-on-text. Root cause measured live (computed styles, not guessed): the 0037 sp4 scroll fix made `.wsp` a flex column with `min-height:0` children — every stat tile and list row was blockified into a shrinkable flex item, and cards stretched to the tallest row crushed their children. Fix: each panel body wraps in ONE flex item (`.pb`) that scrolls when squeezed; tiles flow inline again; docs scroll in-card. Proven injected in the live DOM first, then rebuilt and re-proven from the served bytes. |
| `docs/design/the-honest-boundary.md` | Fable 5 (claude-fable-5) | NET-NEW — the standing register of claims, proofs, and parks, seeded from the outside poster's §12 at JB's word; every claim names its evidence or its gate; maintenance law: a dive that moves a row updates the register in its closing commit. Linked from the design README road and the outside shelf. |

## Fable 5 — 2026-07-26 (the Daylight Glass — one glass, two lights)

| File | Author | Note |
|---|---|---|
| `backend/plane/crates/orrethd/src/window.html` | Fable 5 (claude-fable-5) | JB's 2026-07-22 ask built: a light theme for the whole Console INCLUDING the orrery and the Brain. Never an inversion — the night view is additive light (`lighter`), the day view is ink-wash on warm paper (`multiply`): indigo glass, bronze embers, sepia orbit lines, pigment-shaded bodies (`shade()` deepens the night's glow-hues — pastels that burn on black smudge on paper). Architecture: 13 CSS vars gain a `[data-theme="light"]` twin + ~20 targeted overrides; every canvas color lifted into ONE `THEMES` object (`PAL`), read at frame time so the flip is live mid-orbit; ☀/☾ in the header, choice kept in localStorage. Self-tested in Chrome view by view (brain · orrery · spacetime drawer · requests · rooms), night regression confirmed pixel-faithful. |

## Fable 5 — 2026-07-26 (bodies with faces — the orrery grows planets)

| File | Author | Note |
|---|---|---|
| `backend/plane/crates/orrethd/src/window.html` | Fable 5 (claude-fable-5) | JB's verdict on the daylight orrery ("just ok — objects should be realistic, like the original's planets and moons") answered: canvas bodies are now lit SPHERES — upper-left key light matching the rail's CSS marbles, limb darkening, one specular breath (`drawPlanet`); the core is a radiant center-lit sun (`drawSun`) that is NEVER pigment-shaded — it is the light (`PAL.osun`: gold by night, rich gold by day). Atmospheric glow rides a per-theme dial (`oglowA`). Verified in Chrome both lights; night core renders byte-identical values. |

## Fable 5 — 2026-07-30 (0043 sp1 — the flight recorder: the universe grows its senses)

| File | Author | Note |
|---|---|---|
| `backend/conformance/orreth_sim/observatory.py` | Fable 5 (claude-fable-5) | NET-NEW — the Observatory's senses as the executable spec: the reading normal form (every number declares its TIER at birth), four taps over books that already exist (plane meter · farm meter+worldline · fingertip spans · gate-wait ages), the Series projection with DECLARED retention and MEASURED distillation loss (raw→hourly→daily, sweep distills before it drops, lived time monotone even for instruments — BackdatedReading), and the FlightRecorder (cursor-honest sweeps: counters once, gauges every beat). Banner in file. |
| `backend/conformance/tests/test_observatory.py` | Fable 5 (claude-fable-5) | NET-NEW — eleven conformance stories: refusal wears one face outside and a taxonomy inside; a rejection's clock rides as an instrument because the escalation contract holds no decided stamp (the two-tier law, applied honestly); log-truth rebuilds from the log; sweep never eats the undistilled. Suite 254→265. Banner in file. |
| `backend/conformance/orreth_sim/model_plane.py` | Fable 5 (claude-fable-5) | The meter becomes a flight recorder: latency (`ms`) rides every metered call; refusals land in the gateway's own book with a taxonomy (`pinned-unaffordable` · `budget-exhausted` · `class-outside-floors` · `model-sunset`) while the exceptions that ride out are byte-identical — rule 4 kept. |
| `backend/conformance/orreth_sim/farm.py` | Fable 5 (claude-fable-5) | The meter entry gains `ok` — error rate per service worldline; rug-pull correlation falls out for free. |
| `backend/conformance/orreth_sim/fingertip.py` | Fable 5 (claude-fable-5) | Branches gain a span (started/ended/ms/status) and the choreography record carries it — the glass's picture gains a stopwatch it never had. |
| `backend/conformance/orreth_sim/hitl.py` | Fable 5 (claude-fable-5) | The queue's own book (`decisions`) stamps rejections — the escalation contract (`additionalProperties: false`, rule 9) holds no decided field, so the Observatory reads a rejection's wait as an instrument reading, never testimony. |
| `backend/conformance/console_worker.py` | Fable 5 (claude-fable-5) | The wire twin: `FlightBook` taps all three governed-thought sites (canary · working thought · the parlor's voice), seeds from `~/.orreth/observatory/flight.jsonl` like charlotte's ledger, AGES its own file by the declared horizon, and beats on the universe scope (🔭). First live flight caught a real `no-local-key` refusal AND its successful thought (claude-sonnet-5 · 301 tok · 2447 ms) from charlotte's voiced reply. |

## Fable 5 — 2026-07-30 (0043 sp2 — vera & the assay loop: the universe gains its astronomer)

| File | Author | Note |
|---|---|---|
| `backend/conformance/orreth_sim/vera.py` | Fable 5 (claude-fable-5) | NET-NEW — the tenth organ as the executable spec, all four locked laws structural: the bench is never the work's floor (and no outside bench → REFUSAL, never self-grading); verdicts are signed Chronicle records under the JUDGE'S authorship (tier one of the storage law); degradations become CARDS naming their yardstick and evidence — no levers; every commission metered under her DID, PINNED so a squeezed budget halts loudly instead of seating a silently cheaper judge. Human gradings enter the same shelf by the same shape. The dial gates the beat: glance and watch rest free; only assay spends. Banner in file. |
| `backend/conformance/tests/test_vera.py` | Fable 5 (claude-fable-5) | NET-NEW — eight conformance stories, the refusal edges among them (no outside bench; the meter's loud halt; no hall of mirrors, no re-drumming; the parlor's conversations are not hers to grade). Suite 265→274 (with the watch-depth read). Banner in file. |
| `backend/conformance/orreth_sim/observatory.py` | Fable 5 (claude-fable-5) | `percentiles()` — the WATCH depth (§5): distributions read from the raw shelf the glance already keeps; a deeper read, never a new collection; tier and label ride the answer. |
| `backend/conformance/orreth_sim/parlor.py` | Fable 5 (claude-fable-5) | vera seated: RESIDENTS/EMBODIED/ROLES, her calling card, her grounded answers (standings · her own cost · the dial), and her room (typed panels; the instrument GLASS remains sp3's canvas). First live audience denied her own residence — the roster she wasn't on grounded the voice honestly; the seat fixed it. |
| `backend/conformance/console_worker.py` | Fable 5 (claude-fable-5) | The wire: vera seeded (`~/.orreth/residents/vera.seed`) and pinned at the universe floor (the improver's precedent — builder's call, sp2); `governed_thought` gains `as_did` so her commissions ride HER meter; `assay_beat` dial-gated (ORRETH_OBS_DIAL, default glance) — samples unjudged outcomes, commissions sonnet-5 from f:prod's stable, the judge's floor seat signs, one degradation card per floor stages pending. First live beats: 13 real works judged (mean 0.14 — the deterministic-scaffold outcomes measured, the register's prose given a number), card staged at u:demo, every judge thought on sp1's flight book. |

## Fable 5 — 2026-07-30 (0043 sp3 — the instrument room: the universe measured, in both lights)

| File | Author | Note |
|---|---|---|
| `backend/plane/crates/orrethd/src/window.html` | Fable 5 (claude-fable-5) | The 🔭 Observatory tab: six hand-rolled panels — cognition/flight-recorder (tokens-per-hour sparkline, ms percentiles, refusal taxa beside the "one face outside" reminder) · vera's standings (score-distribution strip with the .55 floor marked) · gate-wait ages (oldest-first, red past a day) · the seven rows' ladder (leader in brass, a dark row honestly dark) · farm & stable · governance/epochs. Every panel wears a TIER chip; canvases read PAL at draw time (both lights, self-proven in Chrome); double-click keeps a PNG (G9). The dead-man is first-class (G1): the recorder's pulse breathes in the header, and an unreachable door turns the whole room into "THE WATCHER HAS NO PULSE". One TDZ lesson: deep-linked #v=obs clicks the tab before the script's `let` line runs — `var`, deliberately, with the comment saying why. |
| `backend/conformance/console_worker.py` | Fable 5 (claude-fable-5) | The room's supply line: `compose_observatory()` — ONE payload (recorder pulse · flight series with hourly buckets and percentiles · verdicts/standings via the shared `_wire_verdict_standings` · gate ages across every tended floor · farm/stable books · per-floor epoch heads · the seven rows via `wire_stacks_panel`), cached 5s; served at GET `/observatory` on the worker's own embed door (:4562, CORS-open) — instrument data behind cognition's door, the plane untouched (rule 9). First live compose showed a purge 19 days pending — the gate-wait panel earned its keep before the paint dried. |
| `docs/design/0043-the-observatory.md` | Fable 5 (claude-fable-5) | §11 THE GAP REGISTER (JB's directive: "really don't want gaps in monitoring and visibility") — nine gaps the build found, each with why-it-matters and a NAMED home; the law: found → written → homed. G1/G3/G4/G5/G9 closed by sp3 and annotated so. |

## Fable 5 — 2026-07-30 (0043 sp4 — the experiment: arms are machines, the rollout is a word)

| File | Author | Note |
|---|---|---|
| `backend/conformance/orreth_sim/experiment.py` | Fable 5 (claude-fable-5) | NET-NEW — the executable spec of §7's crown jewel, six laws: the arm IS the floor's fingerprint with the variant as the asset's head (differing from its sibling in exactly the asset under test, provably); a proposed experiment serves NOTHING; the split is a deterministic hash ladder (no coin anyone must trust); standings ride the LOG JOIN (verdict → work → arm tag — never a side-table); min_n holds against thin evidence; the conclusion is a card and the adoption names the variant AND the experiment (the 0038 orphan law), the loser outranked, never gone. Banner in file. |
| `backend/conformance/tests/test_experiment.py` | Fable 5 (claude-fable-5) | NET-NEW — seven conformance stories, the word-may-be-no at every door among them. Suite 274→281. Banner in file. |
| `backend/conformance/console_worker.py` | Fable 5 (claude-fable-5) | The wire loop whole: `on_experiment` (stage-with-arms-previewed → open on the word → promotion staged → adopt with lineage), `experiment_beat` (the wire log join, the card at min_n), the arm serving as the PROJECTION's head per ask (the shelf untouched; answers wear `arm:<fp12>` tags), `assay_beat` generalized to floors with running experiments. The riders: G4 (`on_dial` — vera stages the turn, the glass button flips runtime `OBS["dial"]`), G5 (`ORRETH_ASSAY_DAILY_TOKENS` declared/enforced/shown, spend computed log-truth from the flight book), G6 (the objective's `rubric` field → `rubrics.json` → `rubric_declared: true` verdicts). `wire_assets`/`_wire_verdict_standings` gain scope — the assay reads where the work lives. |
| `backend/plane/crates/orrethd/src/window.html` | Fable 5 (claude-fable-5) | The gates grow buttons: experiment ("open the split" / "adopt the winner" / decline) and dial ("turn it" / "leave it") join the request queue's gate grammar; the Observatory gains the experiment panel (arms as machine-named bars with n·mean·share) and the header shows the declared ceiling (G5). |
| `backend/conformance/orreth_sim/parlor.py` | Fable 5 (claude-fable-5) | vera's "set the dial to …" — protocol words, verbatim, staging an action; the card gains the turn template. |
| `docs/design/0043-the-observatory.md` | Fable 5 (claude-fable-5) | §11: G4/G5 closed, G6 landed (honest caveat: first rubric'd objective still to run), G10 FOUND at the close — the turned dial does not survive the worker's restart; homed to sp5. |

## Fable 5 — 2026-07-31 (0043 sp5 — the whole rig: the dive closes WHOLE, era 0.43)

| File | Author | Note |
|---|---|---|
| `backend/conformance/orreth_sim/observatory.py` | Fable 5 (claude-fable-5) | G2's law: `Series.sealed_until()/dump()/load()` — the distilled pyramid as portable state; a reloaded seal refuses backdated readings exactly like a lived one (the monotone law survives the process). |
| `backend/conformance/tests/test_observatory.py` | Fable 5 (claude-fable-5) | "the pyramid survives the process" — dump→load reads equal, tiers kept, seals honored, the present flows on. Suite 282→283. |
| `backend/conformance/console_worker.py` | Fable 5 (claude-fable-5) | THE WHOLE RIG: the examiner round-robins every tended floor (ceiling closing mid-round, G5 at rig scale) · `_judge_bench` (G7 — chosen among serving medium stalls, f:prod first, never the work's floor) · `_persist_summaries`/replant reload + book compaction (G2 live: 22 sealed hours, the book trimmed to unsealed rows, the recorder's cursor kept honest) · `dial.json` (G10 — proven by kill-restart both ways) · the wire flow's stopwatch riding the SIGNED intention-outcome record · the rollup + flow blocks in the observatory payload — the Observatory watching the Observatory's own cost, always. |
| `backend/plane/crates/orrethd/src/window.html` | Fable 5 (claude-fable-5) | The room's header carries the rig whole: "watching 19 floor(s), whole (sp5)" beside the declared ceiling; cognition gains the flow-span percentiles (log-truth). |
| `VERSION` | Fable 5 (claude-fable-5) | 0.42 → 0.43 in the closing commit — the glass whispers the true era (the covenant's line, kept). |

## Fable 5 — 2026-07-31 (guide 06 — the Observatory's companion)

| File | Author | Note |
|---|---|---|
| `docs/guides/06-the-observatory-reading-the-instruments.md` | Fable 5 (claude-fable-5) | NET-NEW — the human's guide to what the universe measures and what it is telling them: the two-tier chips as the one law to read everything by, the dial and its price, the room panel by panel (with the live stories that proved each — the 19-day purge, the scaffold scores, the false drift accusation and why "leave it" was right), the gate cards and what each click does, vigil/vera/Mirror kept separate, the nest and its honest aging, and the on-the-record list of what is NOT watched. Written the night 0043 closed, while the instruments were warm. |

## Fable 5 — 2026-07-31 (the Console/UI pass — the gates come to the glass)

| File | Author | Note |
|---|---|---|
| `backend/plane/crates/orrethd/src/window.html` | Fable 5 (claude-fable-5) | JB's usability pass, built and proven live: (1) the orrery gains its ⛶ (fullscreens the whole sky; hidden in brain projection, which has its own); (2) THE GATE BELL — one wait list, three faces: the Requests badge, a breathing brass chip floating in the sky (both projections, rides into fullscreen), and mini-cards INSIDE the parlor while you talk; (3) the bell's popover and the audience strip carry the same approve/deny doors (joinDecide) plus inline answer inputs for the flow's questions — deciding never costs the living view. Proven end-to-end: asked vera "set the dial to watch" in her audience, the staged card arrived IN the dialog seconds later, one click in the strip turned the dial ("«glance» → «watch» — and the word persists"), the strip count breathed down, the sky never left the screen; both lights checked. One diagnostic detour honestly logged: the "empty orrery" during automated capture was Chrome's occlusion throttling (document.hidden gates the draw loop), not a regression — a human at the glass always had planets. |

## Fable 5 — 2026-08-02 (the gate bell learns 0030's oldest lesson — the refresh must never eat the words)

| File | Author | Note |
|---|---|---|
| `backend/plane/crates/orrethd/src/window.html` | Fable 5 (claude-fable-5) | BUGFIX, found by JB's hand: typing an answer into the bell popover or the audience strip emptied within seconds — the console's breath (`tick()` → `loadReq()` → `renderGates()`) rebuilt both surfaces' innerHTML unconditionally, destroying the focused input. The repo already kept the law at the objectives' `qa-` inputs ("a human mid-answer outranks the refresh", 0030's standing rule) — the new faces never got the guard. Now each face guards its own prefix: a `document.activeElement` id starting `gq-` holds the popover still, `pq-` holds the parlor strip still, and typing in one never freezes the other. Proven deterministically in live glass: focused field + two FORCED breaths in each face → words and focus held; Enter then carried the answer through the real door (req settled `done`, queue breathed 3→2). The proof gap owned: the original pass clicked the gate buttons live but never typed — a button survives a rebuild it sits through between clicks; a focused input does not. |

## Fable 5 — 2026-08-02 (spoon 1 of the standing list — the rubric's field, the bell's polish, and the astronomer seated)

| File | Author | Note |
|---|---|---|
| `backend/plane/crates/orrethd/src/window.html` | Fable 5 (claude-fable-5) | **G6 closed whole**: the "judge this by…" field under the objective composer — the yardstick rides the request record, shows on the staged card ("judged by — …"), Enter submits; typed as a human, it produced the first real `rubric_declared: true` verdict (0.12 — the declared standard measurably changed the judgment). **One grammar, one door**: `GATE_WORDS`/`gateWords`/`gateGo` replace GOKNO and reqRow's 13-branch button ladder — every face (Requests row, bell popover, audience strip) reads the same verbs, and the objective's word now rides `objDecide` from ALL faces (the bell had been silently dropping the keep-fresh coupling through the plain resolve); healed live drift: subscription's two wordings, assay cards buttonless in the Requests tab. **The chime**: the bell flashes when the count RISES (`bellring` — first shipped as `.ring` and it inherited the orrery alert-ring's screen-size geometry: the 0020 one-namespace lesson, relearned and named in a comment). **The bell boards the brain**: on `fullscreenchange` the bell + popover reparent into brainwrap for the stay and come home after — proven in, proven home. vera's glass identity: key, night-indigo, dome-and-star medallion, anatomy order. |
| `backend/plane/crates/orrethd/src/main.rs` | Fable 5 (claude-fable-5) | **G11 (JB's find, 2026-08-02)**: vera has been becky-pinned to the universe floor since 0043 sp2, but the roster never got her row — the one resident who answers performance questions was undiscoverable in the glass. Her pin-only residency block (the grace/allen pattern): "vera · the astronomer · measuring — keeps the observatory; measures the work, never grades her own floor." Proven the human way: rail row clicked cold, audience opened, the dial turned «assay» → «watch» through it. |
| `docs/design/0043-the-observatory.md` | Fable 5 (claude-fable-5) | §11: G6 closed whole with the proof quoted; G11 entered and closed same sitting (found → written → homed, the law kept). |
| `docs/decisions/README.md` · `docs/design/the-honest-boundary.md` · `docs/guides/06-...` | Fable 5 (claude-fable-5) | The G6 decision's proof clause satisfied on the record; the register row moves in the same commit (JB's lock); the guide now names the composer field and the proven path. |

## Fable 5 — 2026-08-02 (0044 The Bell — designed and blessed in one sitting)

| File | Author | Note |
|---|---|---|
| `docs/design/0044-the-bell.md` | Fable 5 (claude-fable-5) | NET-NEW — the dive design: the witness (daemon-side dead-man, absence-only, signed obituaries with author ≠ subject) + the bell (farm resident with a DID, consent in becky's ledger, content-minimal, record-before-wire, cooldown, never moves a clock) + the ring grammar and founding subscribers. JB's three locks taken same sitting, all recommended paths: SES email v1 · 0042's verify beat folds in as `tamper` · 90s witness threshold. |
| `docs/design/README.md` | Fable 5 (claude-fable-5) | The road gains 0044's row — designed + blessed, four spoonfuls queued. |

## Fable 5 — 2026-08-02 (0044 sp1 — the witness takes its watch)

| File | Author | Note |
|---|---|---|
| `backend/plane/crates/orrethd/src/main.rs` | Fable 5 (claude-fable-5) | The witness: `worker_pulse` (the touch, carrying nothing; a return closes the open episode) + the watch loop (10s tick; 90s threshold, env may lengthen never silence; one card per episode; the finding staged in the daemon's own book with pg write-through — it exists whether or not any glass ever opens). First-tick bug caught by the kill test: the sync pg client on the async runtime poisoned the requests lock; healed with the submit door's `spawn_blocking` law, violation named in a comment. |
| `backend/conformance/console_worker.py` | Fable 5 (claude-fable-5) | `witness_pulse` on every universe pass; `witness_transcribe` — the two-tier completion: the daemon's stamped card IS the testimony, the risen worker transcribes it verbatim into a signed Chronicle record (vera as the observatory's scribe, source named in the body), the card left staged for the human. |
| `backend/plane/crates/orrethd/src/window.html` | Fable 5 (claude-fable-5) | `witness` gate words — "acknowledge — seen" / "leave it standing". |
| `docs/design/0044-the-bell.md` | Fable 5 (claude-fable-5) | sp1 landing note with the kill-proof timeline (19:50:29Z killed → 19:52:14Z the book spoke, Console closed → the risen worker transcribed). |

## Fable 5 — 2026-08-02 (0044 sp2 — the bell service: the first ring reaches its human)

| File | Author | Note |
|---|---|---|
| `backend/conformance/orreth_sim/bell.py` | Fable 5 (claude-fable-5) | NET-NEW — laws 2–6 executable: the pinned manifest (content-hash IS the pin) · the consent grammar wearing 0034's shape (endpoint + kinds + window, revocation a posture never an absence) · the one face at EVERY miss (absence, revocation, lapse, wrong kind — indistinguishable) · content-minimal by construction (nothing smuggled survives the door) · record-before-wire with the outcome always landing · cooldown per (kind·subject), repeats aging into the standing ring. Transport injected — the sim never touches a wire. Banner in file. |
| `backend/conformance/tests/test_bell.py` | Fable 5 (claude-fable-5) | NET-NEW — 8 stories incl. the one-face indistinguishability sweep and record-precedes-a-failing-wire. Suite 283→291. Banner in file. |
| `backend/conformance/console_worker.py` | Fable 5 (claude-fable-5) | The wire: BELL seeded (persistent DID, rule 1) · `_ses_send` (L-A as amended: bell@jsbarth.com, production-mode SES, profile jb_support) · `_bell_service` (manifest landed idempotently; cooldown book reloaded — law 6 survives the process) · `_bell_consent_head` off the shelf · `ring_bell` (records land, state saves) · `bell_beat` (no grant + no open card → the bell ASKS) · `on_bell_consent` riding 0034's consent gate behind a `bell` marker — staged with terms, opened ONLY on the human's word, `first_sound` answering the grant with real news (the oldest standing witness card). |
| `docs/design/0044-the-bell.md` | Fable 5 (claude-fable-5) | sp2 landing note: both faces proven live — the one-faced refusal (with a smuggled instruction, SES never stirred), then JB's click and the first ring IN HIS INBOX: req-403, a real death 2.6h old, five fields and nothing more. |

## Fable 5 — 2026-08-02 (0044 sp3 — the subscribers: three voices, and the deed watchman stands at last)

| File | Author | Note |
|---|---|---|
| `backend/conformance/console_worker.py` | Fable 5 (claude-fable-5) | `verify_beat` — 0042's deferral standing (L-B): observation-only, every standing deed (last attempt per path off the shelf) fetched back against its sworn key on a declared cadence; the observation lands either way; a wrong world stages the walk-back (0042 §5 — staged, never enacted) AND rings `tamper`. `gate_age_beat` — the OLDEST over-threshold card across EVERY tended floor rings once, daily cap, subject naming the place. Two gaps found by the build and closed in the sitting (B1 the universe-only pulse that staged 19 honest obituaries for a living worker — the pulse now touches every tended door, stale cards settled with the truth named; B2 the one-queue gate-age — now rig-wide, agreeing with the room's panel per rule 7). |
| `docs/design/0044-the-bell.md` | Fable 5 (claude-fable-5) | sp3 landing note + the dive's gap register begun (B1 · B2, both closed same sitting). |

Proven live, JB's inbox the witness thrice over: the outside hand swapped first-deed.json on the open web and the watchman caught it inside one window ("observed found [7da99904…]"), staged req-407, rang tamper, and the true bytes were restored; gate-age rang for req-16 at f:prod — twenty-two days of waiting, rung exactly once.

## Fable 5 — 2026-08-02 (0044 sp4 — the whole: the dive closes, era 0.44)

| File | Author | Note |
|---|---|---|
| `backend/conformance/console_worker.py` | Fable 5 (claude-fable-5) | The risen worker RINGS the death it could not ring while dead — once per rise, subject = the floor so law 6 bites across episodes; the aged-repeat now persists (a held ring's +1 outlives the process); `_bell_room_view` in the observatory payload — the room watches its own alarm. |
| `backend/plane/crates/orrethd/src/window.html` | Fable 5 (claude-fable-5) | The room's header carries the bell's state: "the bell: rung — last ring Nm ago (+N aged in)". |
| `VERSION` | Fable 5 (claude-fable-5) | 0.43 → 0.44 in the closing commit — the covenant's line, kept. |
| `docs/design/0044-the-bell.md` · `docs/design/README.md` · `docs/design/the-honest-boundary.md` · `docs/guides/06-...` | Fable 5 (claude-fable-5) | The dive CLOSED WHOLE with its receipts; the register's stale bullets struck through honestly (the daemon DOES notice a dead worker now; out-of-band alerting STANDS); B3 named open — the ring waits for a resurrection, the dead-man's dead-man is a deferral with a home. |

The closing proof, verbatim: killed 23:17:30Z (Console closed) → the witness spoke 23:18:59Z → the rise rang JB's inbox; killed again 23:19:04Z → the witness spoke → THE BELL HELD ("aged into the standing ring (+1), the wire stays quiet"). Two deaths, one email. Designed, locked, and proven in one day.

## Fable 5 — 2026-08-03 (0045 The Craft Room — designed on JB's CRUD objectives)

| File | Author | Note |
|---|---|---|
| `docs/design/0045-the-craft-room.md` | Fable 5 (claude-fable-5) | NET-NEW — the week's largest item designed from JB's machine-of-machines brief: the trust gap named (the machine shows its work but hides its craft), seven laws (registry-as-projection · two lifecycles one law of change · the human's edit wears grace's grammar · readable craft · the argument first-class · commissioned creation · scale as constraint), the «Governance» room replacing Ask, five spoonfuls. Three JB locks taken at design time, all recommended: Canon change = epoch release (0041's ceremony IS the firmware lifecycle) · human edits = one-motion sibling proposals · Ask retires. |

## Fable 5 — 2026-08-03 (0045 sp1 — the registry: the machine's craft becomes readable)

| File | Author | Note |
|---|---|---|
| `backend/conformance/console_worker.py` | Fable 5 (claude-fable-5) | THE CANON EXTRACTION: the four LLM firmware prompts leave the code as ⟦slotted⟧ templates (FIRMWARE = genesis seeds only), land as becky-signed Canon records on first beat (`canon_seed`, idempotent), and the worker READS its own firmware from the shelf (`craft()` + `craft_render`, 60s cache, literal fallback only when the shelf cannot answer) — all four call sites refit. `compose_governance` — the registry as a light index (worldlines collapsed per name across firmware · grace's assets · charters · manifests · declared rubrics), served CORS-open at `/governance` beside `/observatory`. |
| `backend/plane/crates/orrethd/src/window.html` | Fable 5 (claude-fable-5) | «Governance» replaces Ask: category chips × lifecycle lenses (canon · the firmware / chronicle · the adaptive craft) × live search; the shelf as worldline rows; the reader (record hash, version chips, rendered text) and the diff (the lines that moved, adds green, removals struck). The reel rehomed to Pulse ids-intact; submitAsk/asklog/qchips retired with comments naming the successor; two init breaks from the retirement (the tab array's dead "ask", a top-level write to a removed element) surfaced by the glass's own errors and healed. |

Proven as a human: vera's actual judge prompt read in the glass wearing CANON — the firmware no longer hidden; fingertip-default v1→v2 diffed showing the improver's real adopted change (max_cycles 2→5, adopted_from named). 12 objects · 7 prompts · 1 charter · 4 manifests · JB's declared yardstick under its own heading.

## Fable 5 — 2026-08-03 (0045 sp2 — the editors & the one law of change)

| File | Author | Note |
|---|---|---|
| `backend/conformance/console_worker.py` | Fable 5 (claude-fable-5) | `on_craft_edit` — the one law at the glass door: the human's edit rides a `craft-edit` request (the click IS the word), grace signs the sibling with the human's authority named in the body (`"the human's word at req-…"`), `adopted_from` + `derived_from` carry the lineage, and the head moves. Canon names refuse toward the release (sp3); malformed bodies refuse loudly; every refusal ends "Nothing changed." `_craft_heads` maps the shelves for the door. |
| `backend/plane/crates/orrethd/src/window.html` | Fable 5 (claude-fable-5) | The editor: "✎ propose an edit — lands on your word" on Chronicle objects only (Canon shows the release pointer instead); textarea + worldline note + one-motion land button; polls the word home and re-opens the object with its new head. |
| `docs/decisions/README.md` | Fable 5 (claude-fable-5) | The write-time re-hash park REVISITED on the record as promised: the park holds — glass-authored records are worker-minted and hash-correct by construction; the trigger stays external ingestion (0013). |

Proven as a human in the glass: fingertip-default v2→v3 (max_obs 3→4, note carried), the diff showing the authority line verbatim; assay-judge refused with the release pointer; a malformed body refused loudly.

## Fable 5 — 2026-08-03 (0045 sp3 — the Canon release: the machine renamed by the human's hand)

| File | Author | Note |
|---|---|---|
| `backend/conformance/console_worker.py` | Fable 5 (claude-fable-5) | The fingerprint covers the FIRMWARE (the machine's name cites its own driving words — the widening deliberately drew the watchdog's accusation as the negative proof); `on_release` — Canon's only change door: staged with BLUE and GREEN named on the card, the human's word lands the becky-signed sibling (`released_by` verbatim), the craft cache flushes, and the forced beat cuts the new name with the word standing; "release" joins `_ADOPTION_KINDS`. |
| `backend/conformance/orreth_sim/epoch.py` | Fable 5 (claude-fable-5) | "release" joins the sim's adoption vocabulary — Canon change = epoch release (JB's lock). Suite 291 green. |
| `backend/plane/crates/orrethd/src/window.html` | Fable 5 (claude-fable-5) | "⚑ stage a release" on Canon objects (the chronicle editor stays refused there); `release` gate words; +JB's find mid-proof: reqRow now shares the bell's approve/decline FALLBACK for staged kinds outside the map — staged means waiting on a word, and a card with no way to answer is a gate with no handle. |

Proven both ways with JB at the glass: the wordless fingerprint widening ACCUSED (req-416, acknowledged); the first firmware release CUT BY JB'S OWN CLICK (req-417 — assay-judge learns to quote the yardstick it judged by), the machine renamed ff728ca5 → a8c4cd1b, the watchdog silent on the ceremony path alone.

## Fable 5 — 2026-08-03 (0045 sp4 — the applied graph, the argument, and the rows' shelf)

| File | Author | Note |
|---|---|---|
| `backend/conformance/console_worker.py` | Fable 5 (claude-fable-5) | The wearers map (declared, the code's own structure); the ROWS' floor joins the registry — JB's "should I see skills?" exposed the one-floor read while the crystallized skill (v2), the 11-version routing standard, record-classes, and distillation-dials lived at e:rag; objects carry their floor and port, arguable there. |
| `backend/plane/crates/orrethd/src/window.html` | Fable 5 (claude-fable-5) | The ⟟ applied-craft view (words → wearers, edges); the declared rubrics open a reader (JB's find); ⚖ "open an argument" stages a real 0043 experiment from the object; cross-floor bodies fetched from the object's own port. |

Probe-proven: req-418 ("does the router still deserve the head?") armed and staged at the gate — arms as named machines, the split waiting on the human.

## Fable 5 — 2026-08-03 (0045 sp5 — the supply line: LangGraph drinks from the registry)

| File | Author | Note |
|---|---|---|
| `agents/orreth-agent-sdk/orreth_agent/craft.py` | Fable 5 (claude-fable-5) | NET-NEW — `acquire()` under law 8's riders: one resolution carried through the run; the citizen DID; `on_dark="refuse"|"stale"` with stale servings LABELED; ⟦slot⟧ rendering; the arm always visible. Banner in file. |
| `agents/orreth-agent-sdk/examples/langgraph_supply_line.py` | Fable 5 (claude-fable-5) | NET-NEW — a real LangGraph StateGraph whose only Orreth touch is the acquire call; its run record names the exact word that drove it. Banner in file. |
| `backend/conformance/console_worker.py` | Fable 5 (claude-fable-5) | The `/craft` door: head or pinned (off-worldline pins refuse), arm by DID hash when an argument runs (visible — no secret splits), servings on the instrument tier (servings.jsonl, the flight recorder's precedent). Lease enforcement = named hardening gap. |

Proven: the flow's record named v2 — the sha of the release JB cut — and a darkened registry served the cached copy LABELED stale: true.

## Fable 5 — 2026-08-03 (the farm becomes visible in the sky and the mind — JB's find)

| File | Author | Note |
|---|---|---|
| `backend/plane/crates/orrethd/src/window.html` | Fable 5 (claude-fable-5) | JB: "active services in Farm but not in brain or orrery." The data always flowed (all four f:prod MCP stalls ride the heartbeat chain); the 3D sky drew farm diamonds only when a moon faced the camera (the depth gate) and the brain drew none. Now: diamonds UNGATED on every body ("a tool that serves deserves to be seen from anywhere"), tool counts in the body labels (`· Nt`), a hover card naming service · state · calls · pinned manifest, and brass diamonds orbiting each ember in the brain. |

## Fable 5 — 2026-08-03 (0045 sp6 — the commission: the dive closes whole, era 0.45)

| File | Author | Note |
|---|---|---|
| `backend/conformance/console_worker.py` | Fable 5 (claude-fable-5) | `on_commission` — the human's click births craft through the machine's own organs: librarian gathers (live tavily), factory drafts at a chosen bench (metered; one honest redraft when a draft comes back empty — printed, never silent; the debug pass also caught my own local-import typo hiding behind the void message), grace lands v1 with `commissioned_by` + `born_of` named, the card waits at the gate. |
| `backend/plane/crates/orrethd/src/window.html` | Fable 5 (claude-fable-5) | 🏭 the commission composer (kind chips · objective · one-word button) + `commission` gate words. |
| `VERSION` · docs | Fable 5 (claude-fable-5) | 0.44 → 0.45 in the closing commit; the road, the register, and the design closed with their receipts — the covenant's lines, kept. |

The closing proof: skill-orreth-langgraph-onboard v1 STANDS — the first wire-born skill of the universe floor, its whole birth walkable, its welcome click left standing for JB's own hand.

## Fable 5 — 2026-08-03 (the reader unfolds — JB's find on the template soup)

| File | Author | Note |
|---|---|---|
| `backend/plane/crates/orrethd/src/window.html` | Fable 5 (claude-fable-5) | JB: the CRUD reader renders JSON fine until an embedded yaml string turns to escaped soup. Now: `govPretty` lifts long/multiline string fields out of the structure as labeled unfolded blocks with real newlines, display-unescaping double-encoded payloads; the editor, release, and diff read the TRUE raw body (`GOVRAW`), never a scrape of the pretty view — the one-law parse holds. |

## Fable 5 — 2026-08-03 (0046 The Residents Learn to Listen — designed, prioritized by JB)

| File | Author | Note |
|---|---|---|
| `docs/design/0046-the-residents-learn-to-listen.md` | Fable 5 (claude-fable-5) | NET-NEW — the little dive from JB's own testing: the parlor routes keywords, it does not listen. The efficient shape reuses everything: the voiced lane becomes the default ear, grounding kits ride the cached composers (/governance is the cross-scope library card), scope-honesty ships as a resident-voice firmware RELEASE through 0045's own ceremony, persona waits for Profiles at zero future cost. Two spoonfuls; JB's exact failing questions are the proof script. |
| `docs/design/README.md` | Fable 5 (claude-fable-5) | The road gains 0046's row — prioritized ahead of Farm/Stable on JB's word: core interoperability before tuning. |

## Fable 5 — 2026-08-04 (article 07 press-ready + the era file catches up)

| File | Author | Note |
|---|---|---|
| `docs/articles/07-the-library-that-argues.md` | Fable 5 (claude-fable-5) | The dangling question answered with a minutes-fresh receipt (a real gather run for the sentence: 3 findings quarantined at 0.0000); the live successor argument named (routing-ab-2, running — "the library doesn't stop arguing because it won once"). |
| `docs/articles/07-img-the-rag-observatory.png` | Fable 5 (claude-fable-5) | NET-NEW hero image: the night-glass Observatory — the seven rows scored, routing-ab adopted beside routing-ab-2 RUNNING, vera's standings with her own metered cost, the machines' names, the gate-waits. The article in one frame. |
| `VERSION` | Fable 5 (claude-fable-5) | The 0045 closing commit's bump wrote to the wrong directory (a cwd slip); the era file catches up to 0.45 — the whisper corrects on the next rig restart. |

## Fable 5 — 2026-08-04 (0046 sp1 — the default ear: the residents listen)

| File | Author | Note |
|---|---|---|
| `backend/conformance/console_worker.py` | Fable 5 (claude-fable-5) | The root cause was one line: `governed_voice` returned None on every floor but one — the parlors never HAD a voice, they had a single-floor privilege. The gate fell (authorization stays per-floor and honest); `_listen_kit` grounds every resident from the cached composers — the 0045 registry first (the cross-scope library card), vera's observatory numbers, charlotte's farm roster, allen's estate — with the old status card demoted to labeled context; the resident-voice firmware reads from the universe floor; the voice breathes at 240 tokens. Proven with JB's exact failing questions: both residents named both real skills across two floors, in their own voices, metered under their own DIDs. |

## Fable 5 — 2026-08-04 (0046 sp2 — the referral release: the dive closes whole, era 0.46)

| File | Author | Note |
|---|---|---|
| `backend/conformance/console_worker.py` | Fable 5 (claude-fable-5) | The kit gains the charters roster — sp2's first proof showed the released sentence aiming at organs instead of residents; a resident can only refer BY NAME if it knows who keeps what. |
| `VERSION` · docs | Fable 5 (claude-fable-5) | 0.45 → 0.46 in the closing commit; design, road, and register closed with the receipts. The release itself (resident-voice v2, req-446) was cut by JB's own click — the machine renamed, the watchdog silent. |

The closing proof, verbatim: "That's charlotte's charter — she keeps the FARM and its services… you'll want to ask her directly."

## Fable 5 — 2026-08-09 (0048 sp1 — the record: the thumb's shapes and laws, sim-first)

| File | Author | Note |
|---|---|---|
| `backend/conformance/orreth_sim/thumb.py` | Fable 5 (claude-fable-5) | The human answers back, as records: the 👍 verdict IS a 0043 human grading (same shelf, same shape — zero new verdict machinery), the 👎's words become a feedback record quoting the human verbatim under 0024's derives-never-mutates grammar, and feedback is a request that RESOLVES — outcomes named, whys owed, nothing silently dropped. |
| `backend/conformance/tests/test_thumb.py` | Fable 5 (claude-fable-5) | Six laws under conformance (suite 311→317): quiet-word-loud-on-record · no anonymous thumbs · verbatim feedback + marked-record-never-changes · wordless no · the inbox empties only on resolution · resolution refuses dishonesty. |

## Fable 5 — 2026-08-09 (0048 sp2 — the chips: both surfaces wear the thumb, proven live)

| File | Author | Note |
|---|---|---|
| `backend/conformance/console_worker.py` | Fable 5 (claude-fable-5) | `human_seat(scope)` (persistent per-floor key — no anonymous thumbs in v0) + the `on_thumb` door (gateless — a thumb IS the human's word) + the parlor builds its exchange record before the resolve so the judged id rides the result; safer-mode and unembodied answers honestly offer no thumb. |
| `backend/plane/crates/orrethd/src/window.html` | Fable 5 (claude-fable-5) | The chips on both L1 surfaces: parlor replies (append-once DOM, 👍 fades in .85s) and resolved Objectives (view-state map surviving the 4s tick; `td-` inputs join the qa- busy-guard so the re-render never eats the human's words). Proven in Chrome: fade, dialog, and "heard — on the record · req-534" in place. |

## Fable 5 — 2026-08-09 (0048 sp3 — the routing: the words go back into the machine)

| File | Author | Note |
|---|---|---|
| `backend/conformance/orreth_sim/thumb.py` + `tests/test_thumb.py` | Fable 5 (claude-fable-5) | ROUTES/OUTCOME_FOR (the craft route lands EVIDENCE — "proposed" would overclaim under 0031 §4) · route_contract (a real route or a named error) · the wire-twin row resolves through the same law; suite 317→320. |
| `backend/conformance/console_worker.py` | Fable 5 (claude-fable-5) | classify-feedback firmware (genesis) · CHARTERS_ROSTER one source for both ears · wire_open_feedback + feedback_beat: read → route → land → resolution sibling; repair objectives carry the human's words as their RUBRIC (0043 G6); dark studio = open words, said once, never dropped. |
| `agents/flavors/03-mind/run.py` | Fable 5 (claude-fable-5) | The studio's third duty: classify(quoted, context, charters) under the typed route contract, served on the same tend loop. |

## Fable 5 — 2026-08-09 (0048 sp4 — the closure & the calibration: the dive closes whole, era 0.48)

| File | Author | Note |
|---|---|---|
| `backend/conformance/orreth_sim/thumb.py` + `tests/test_thumb.py` | Fable 5 (claude-fable-5) | calibration() under L2's law — one thumb never indicts the examiner; proven in suite (322) and LIVE at the exact boundary: 4 pairs at gap 0.8625 held their tongue, the 5th made news. |
| `backend/conformance/console_worker.py` | Fable 5 (claude-fable-5) | The closure card on every routed 👎 (L3: cards always; the bell refused one-faced under the existing grant's kinds — consent never invented) + the whole-rig calibration_beat (throttled, one open finding, cards never levers). |
| `backend/plane/crates/orrethd/src/window.html` | Fable 5 (claude-fable-5) | The sp2 wart closed: THUMBED reads the queue's own thumb requests, so a reload shows "heard — on the record" where the human already judged — the record decides, not session memory. |
| `VERSION` · register · road · atlas | Fable 5 (claude-fable-5) | 0.47 → 0.48 in the closing commit; the honest-boundary gained the 0048 row with its named gaps; the atlas's thumb loop went seeded → standing under its own now-standing maintenance law. |

## Fable 5 — 2026-08-11 (0050 sp1 — the shelf: the machine's sentences leave the code)

| File | Author | Note |
|---|---|---|
| `backend/conformance/orreth_sim/speech.py` + `tests/test_speech.py` | Fable 5 (claude-fable-5) | 13 wave-1 sentence templates (gate cards + parlor notes) with ⟦slot⟧ facts, parity-tested byte-for-byte against the literals they replace; strict render refuses unfilled slots by name; the refusal family structurally absent (0002 §4). Suite 322→328. |
| `backend/conformance/console_worker.py` | Fable 5 (claude-fable-5) | `sentence()` — one voice from the universe shelf (cached, genesis fallback that speaks loudly, never silently); the improver plants sentences beside the prompts; seven call sites (calibration · verify pair · closure · reflex escalation · thumb reply · dispatcher note) now speak from the shelf. Proven live: 13 plantings, registry family at v1, byte-identical render. |

## Fable 5 — 2026-08-11 (0050 sp2 — the plain-speech pass: the machine's new voice, and the watchdog's honest accusation)

| File | Author | Note |
|---|---|---|
| `backend/conformance/orreth_sim/speech.py` + `tests/test_speech.py` | Fable 5 (claude-fable-5) | OUTCOME_SPOKEN (total over the thumb's outcomes, suite-held) + the born-human pair fragment; 13 v2 rewrites landed as shelf siblings via the door, never code. |
| `backend/conformance/console_worker.py` | Fable 5 (claude-fable-5) | `_work_glimpse` — the calibration card shows the judged WORK, not the hash; closure speaks OUTCOME_SPOKEN. |
| `orreth_sim/epoch.py` + `tests/test_epoch.py` + worker `_ADOPTION_KINDS` | Fable 5 (claude-fable-5) | The find: the pass drew two honest drift accusations — `craft-edit` was the missing adoption word. Vocabulary grown in sim and worker with the lesson-test (suite 328→330); both accusations LEFT ON RECORD, 0043's precedent honored. |

## Fable 5 — 2026-08-11 (0050 sp3 — quinn, the first UAT persona: the dive closes whole, era 0.50)

| File | Author | Note |
|---|---|---|
| `agents/flavors/04-uat/run.py` | Fable 5 (claude-fable-5) | quinn the newcomer — persistent self, persona acquired from the shelf by reference, walks real objectives through the human's own doors, judges every screen as a stranger under a typed contract, files frictions through the thumb. Her first walk: both cards CONFUSING, 12 frictions, incl. JB's own lock-4 label. First triage found the first defect in her own reporter (the 480-char cap) — fixed. |
| `orreth_agent/craft.py` + `tests/test_craft_profile.py` | Fable 5 (claude-fable-5) | The supply line learns the persona shelf: a chronicle asset whose profile IS a template renders like firmware (SDK 20→22). |
| `orreth_sim/speech.py` + `tests/test_speech.py` · worker | Fable 5 (claude-fable-5) | PERSONAS on the shelf beside the sentences — the tester is craft too, tuned at the same gates. |
| `VERSION` · register · road · atlas | Fable 5 (claude-fable-5) | 0.48 → 0.50 in the closing commit; the register row with its named gaps; the atlas's loops gain the walking persona. |

## Fable 5 — 2026-08-11 (0051 sp1 — the Journey: the objective's life in plain words)

| File | Author | Note |
|---|---|---|
| `orreth_sim/speech.py` + `tests/test_speech.py` | Fable 5 (claude-fable-5) | Fourteen journey sentences (suite 332): the lock-4 label retired by JB's word (req-622) — no "arithmetic, not a mind" survives the test; journey-word explains both buttons; journey-declined extracted parity-true. |
| `backend/conformance/console_worker.py` | Fable 5 (claude-fable-5) | PLAN_FALLBACK_LABEL constant deleted — five use sites speak from the shelf; the /sentences door serves active heads over genesis so the glass and the worker share ONE voice. |
| `backend/plane/crates/orrethd/src/window.html` | Fable 5 (claude-fable-5) | say()/journey()/leafName() + the monitor line: the state ladder as a strip with the current stage glowing, floors leaf-named with paths on hover, the report line human. Proven live on req-624, staged through resolved. |

## Fable 5 — 2026-08-11 (0051 sp2 — the Reins: covenant rule 11, proven on all four vectors)

| File | Author | Note |
|---|---|---|
| `.claude/skills/orreth-covenant/SKILL.md` | Fable 5 (claude-fable-5), at JB's lock | RULE 11: the human can always stop what the machine manages — cancel/rest governed and recorded, never a deletion; stop at the next safe boundary with what-was-left-undone said. A lever the human lacks is a defect. |
| `backend/conformance/console_worker.py` | Fable 5 (claude-fable-5) | on_objective_cancel (legs stopped at the boundary, finished answers kept and labeled, the cancellation record under the HUMAN seat) + on_standing_rest (charters and reflexes rest reversibly). Proven: 18 legs stopped mid-flight; the charter and a reflex rested — the reflex from the glass lever itself. |
| `orreth_sim/speech.py` + `tests/test_speech.py` · `window.html` | Fable 5 (claude-fable-5) | Six rein sentences (suite 333) · the stop button on working objectives · rest levers on standing duties and watchers. |

## Fable 5 — 2026-08-11 (0051 sp3 — the words back: every gate takes a reply)

| File | Author | Note |
|---|---|---|
| `backend/conformance/console_worker.py` | Fable 5 (claude-fable-5) | The gate-word door: words land signed under the HUMAN seat with either decision; a decline's words birth open feedback into 0048's loop — no verdict minted (a request is not a graded record). |
| `orreth_sim/speech.py` + `tests/test_speech.py` · `window.html` | Fable 5 (claude-fable-5) | Three voice-line sentences (suite 334) · gw-/gwo- inputs on every staged gate, joined to the busy-guard law on all surfaces. Proven whole: a declined plan's reason was read true by the studio, evidenced, and the closure returned. |

## Fable 5 — 2026-08-11 (0051 sp4 — the studio's face + quinn's grade: the dive closes whole, era 0.51)

| File | Author | Note |
|---|---|---|
| `orreth_sim/parlor.py` · worker | Fable 5 (claude-fable-5) | The studio joins the residents: card, grounded audience from its own readings, pinned with the DID its own join proved — the worker never touches its key (rule 1); its voiced seat a named gap. |
| `agents/flavors/04-uat/run.py` | Fable 5 (claude-fable-5) | The instrument-honesty lesson: quinn's first re-walk graded a stale mirror; her eye now reads from the SAME /sentences shelf the glass renders from. Her grade: the original wounds HEALED — «staged» became her delight — and the next layer threaded into the season. |
| `VERSION` · register · road · atlas · 0049 | Fable 5 (claude-fable-5) | 0.50 → 0.51; the reins row with named gaps; rule 11 in the atlas's trust spine; thread B promoted by JB's own frustration — the reading-room dive is next. |

## Fable 5 — 2026-08-12 (0052 sp1 — the pane: one place to stand)

| File | Author | Note |
|---|---|---|
| `backend/plane/crates/orrethd/src/window.html` | Fable 5 (claude-fable-5) | The reading pane: paneOpen/renderPane on the parlor's geometry with one-rail-one-attention precedence; objCard extracted so ONE builder serves list and pane (rule 7 for the glass); nearInput resolves inputs nearest the click so duplicate surfaces never steal words. Proven live: approve-from-pane and decline-with-words-from-pane both landed; the too-sticky busy-guard found and fixed in the walk. |

## Fable 5 — 2026-08-12 (0052 sp2 — the doors: every mention opens in the pane)

| File | Author | Note |
|---|---|---|
| `orreth_sim/speech.py` + `tests/test_speech.py` | Fable 5 (claude-fable-5) | Twelve reader sentences (suite 335): known record shapes read as prose; the unknown shape confesses; the miss speaks both truths. |
| `backend/plane/crates/orrethd/src/window.html` | Fable 5 (claude-fable-5) | Text-node-only linkify (attributes never touched); the record-reader pane; breadcrumbs (fresh walk on list click, ← retraces); requests read in-pane show their raw result — full refs, every one a door. Proven live: queue → closure → full ref → "THE HUMAN'S WORDS" as a sentence. |

## Fable 5 — 2026-08-12 (0052 sp3 — the one inbox)

| File | Author | Note |
|---|---|---|
| `backend/plane/crates/orrethd/src/window.html` | Fable 5 (claude-fable-5) | The Inbox tab: everything waiting on the human in one place, gravest first then oldest, riding the Requests tab's own fetch (one wire read, one truth); rows compact — title, id-door, waited-age, voice line, levers — because deciding where you stand must never mean scrolling through evidence the pane already holds. Proven live: 29→28 on a decision from the row. |

## Fable 5 — 2026-08-12 (the judge's walk — JB's verdict, three defects dead)

| File | Author | Note |
|---|---|---|
| `window.html` | Fable 5 (claude-fable-5) | JB's three finds: map(reqRow) passed the array INDEX as inPane — raw JSON polluted every list card after the first (fixed); #v-inbox had no overflow rule in a window that never scrolls — frozen under his hand (fixed); rows verified clean. |
| `console_worker.py` | Fable 5 (claude-fable-5) | The drift flood: a lag with NOTHING to restore asked the human for a word anyway. Now a lag is a NOTE — self-resolved, one per scope per hour; true drift (a restore exists) alone stages. Fourteen standing lag cards swept; zero true drift was found beneath them. |

## Fable 5 — 2026-08-12 (0052 sp4 — the room rebuilt to the judge's eye, at JB's two locks)

| File | Author | Note |
|---|---|---|
| `window.html` | Fable 5 (claude-fable-5) | Master-detail (JB's lock): compact list LEFT, the reading pane RIGHT in-flow, both always visible — select a row, read and decide beside it; questions answer right in the pane. The Requests tab RETIRED (JB's lock): the full queue lives as the Inbox's archive drawer; the Objectives tab keeps composing and reports but its waiting cards point at the one home. Tabs 9→8. |

## Fable 5 — 2026-08-12 (the judge's second walk — two wounds, one root)

| File | Author | Note |
|---|---|---|
| `window.html` | Fable 5 (claude-fable-5) | JB's finds: archive clicks opened the OVERLAY while the in-flow pane kept the old selection — two surfaces, stale views. Inside the Inbox every request click now lands in the one in-flow pane, and a chosen archive item is never overridden by the waiting-list default. The tiny inputs grew to multi-line textareas — a human answer takes the room it needs. |

## Fable 5 — 2026-08-12 (quinn's eyes — the UAT persona looks at the REAL glass)

| File | Author | Note |
|---|---|---|
| `orreth_agent/chassis.py` | Fable 5 (claude-fable-5) | GovernedThink accepts content parts — a governed EYE is metered like a governed thought; same authorize→execute→meter, image or not. |
| `agents/flavors/04-uat/web.py` | Fable 5 (claude-fable-5) | quinn-web: headless Chrome renders each Console view; her shelf persona judges the SCREENSHOT under her own DID and lease; the whole list lands as one uat-report. First walk: 8 rooms, 25 findings — including the class only rendered pages show (truncated text, dev-console leakage, identical rows, insider vocabulary across Farm/Stable/Governance) and the uni view timing out for a headless eye (a finding in itself). |
| `console_worker.py` · `window.html` | Fable 5 (claude-fable-5) | The uat-report door; JB's three finds fixed: tab switches close the overlay, the Objectives twin-pane redundancy removed, ONE decision layout everywhere (words above, buttons beneath, inside the card) with the answer box multi-line. |

## Fable 5 — 2026-08-12 (quinn's 25 worked — the machine speaks plain where she pointed)

| File | Author | Note |
|---|---|---|
| `orreth_sim/fingertip.py` · `console_worker.py` | Fable 5 (claude-fable-5) | The deployment question reborn plain at BOTH composers ("Before this work runs, one thing needs your answer: where should the results be delivered? … the plan treats silence as a no and moves on without it"), and the iac waiting labels with it. Old records keep their old words — the log is append-only; the fix speaks in every question from now on. |
| `window.html` | Fable 5 (claude-fable-5) | Her list, worked: the dev-console leak sealed (staleNote no longer names a script); Farm, Stable, and Governance speak plain (headers say what the room manages, "Add this tool →" / "Connect this model →", the three steps in human words, lifecycle lenses named firmware/everyday-craft, "who uses what →", the empty reader wears a hint); the world rail explains itself on hover (what a row is, memories, agents); the "silence is denial" placeholder now says what silence actually does. |
| `agents/flavors/04-uat/web.py` | Fable 5 (claude-fable-5) | Her eye learned patience: the Universe view animates forever, so a timed-out screenshot retries without the virtual-time budget — the uni room rendered and was judged for the first time. And her report card confesses its edge instead of silently cutting the tail; every finding prints to her own log as found. |

Her second walk (req-694): **Stable 0 findings, Pulse 0 findings** (both were all-jargon rooms); the uni view rendered; the dev leak, "Plant"/"Saddle", charlotte/ada by name, worldline/manifest-hash all gone from her list. What remains is the deeper layer — Universe/Objectives/Observatory vocabulary and a VISIBLE sidebar legend (tooltips are hover-only; a screenshot can't see them, and neither does a newcomer until told) — named for the season's organ dives.

## Fable 5 — 2026-08-12 (the course correction — Orreth, and what Orreth does)

| File | Author | Note |
|---|---|---|
| `docs/design/0053-the-first-purpose.md` | Fable 5 (claude-fable-5) | The season's course correction, landed on JB's word ("we have to do something different before we trash Orreth"). One line: a real purpose writing a real Chronicle, the two books visible on every card, memory proven against it. Three steps — one thin Trading Desk (reports only, never execution) · Chronicle/Machine chips from 0039's own classes with a purpose-first Inbox · the memory program (census, the live metabolism beat, JB's ten questions scored weekly). Four locks staged. |
| `0049` · `0052` · `VERSION` · register · road | Fable 5 (claude-fable-5) | 0049 suspended to a reference map; 0052 closed AS-IS at era 0.52 with the honest verdict on its face ("rather unusable" — legible furniture atop an undifferentiated card soup); the register carries the one-seat claim as an intentional partial gated on 0053. |

## Fable 5 — 2026-08-12 (0054 sp1 — charles is born on his own floor)

| File | Author | Note |
|---|---|---|
| `orreth_sim/desk.py` | Fable 5 (claude-fable-5) | The desk's genesis: 16 reference prompts (AST-extracted verbatim, never retyped; the two inline ones made first-class) + 3 schema hints + the persona — 20 assets the improver's beat plants on the shelf; code literal is genesis and fallback, never the living word. |
| `console_worker.py` | Fable 5 (claude-fable-5) | Becky-per-floor: a join-desk delegate per tended floor, each chained to the pinned root — grant_lease mints for the floor that was asked, not f:prod always. The planting loop takes desk craft beside sentences and personas. JoinDesk untouched; its proof-not-claims tests hold. |
| `agents/flavors/05-desk/run.py` | Fable 5 (claude-fable-5) | charles's birth walk: joins u:demo/e:desk/f:charles through his own gate, acquires persona/pipeline/disclaimer from the shelf by ref, files his birth record citing them. |

## Fable 5 — 2026-08-12 (0054 sp2 — the supply line: the Farm learns to serve a call)

| File | Author | Note |
|---|---|---|
| `orreth_sim/tradingdata.py` | Fable 5 (claude-fable-5) | The reference's market-data machinery ported as INTENT: one snapshot per ticker per half-hour, retry ladder, honest darkness, six indicators in plain pandas, chart series in the bundle's exact shape; 12 reference calls consolidated to 8 tools. Pure machinery — no wire, no signing. |
| `tradingdata_server.py` | Fable 5 (claude-fable-5) | The desk's keyless local stall: GET answers the keeper's heartbeats, POST /call executes the eight declared tools. |
| `console_worker.py` | Fable 5 (claude-fable-5) | The Farm's FIRST invoke door (POST :4562/tool): serving-on-the-named-floor → discredit refused at the threshold → meter-first as the gate → execute at the stall; bulk never becomes records; every miss wears the one refusal face. And the L-A ceiling at tavily()'s chokepoint: durable per-day search ledger, default 6/day, honest placeholder past it — the Tavily lesson institutionalized. |

## Fable 5 — 2026-08-12 (0054 sp3 — the first report: the desk walks whole)

| File | Author | Note |
|---|---|---|
| `agents/flavors/05-desk/pipeline.py` | Fable 5 (claude-fable-5) | The sixteen stages as charles's governed walk: shelf craft by ref, sonnet/opus per L-D, the Farm's door for data, gather under the ceiling for news, a signed record per stage, the bundle in the sample's exact shape. An empty reply retries once then confesses. |
| `agents/flavors/05-desk/run.py` | Fable 5 (claude-fable-5) | --analyze: the desk-run plan gate up front — the walk waits for a human's word; silence is a no and says so. |
| `console_worker.py` | Fable 5 (claude-fable-5) | gather() speaks typed findings on the queue path (note + title/content/url) — the desk's analysts read content, not admission counts; parlor prose and quarantine unchanged. |

## Fable 5 — 2026-08-12 (0054 sp4 — the desk's glass: the first world atop Orreth)

| File | Author | Note |
|---|---|---|
| `window.html` | Fable 5 (claude-fable-5) | The Capabilities pull (L-C v1): a right-edge lever sliding open the portal of applied-purpose worlds — one lever, one world, the Trading Desk. Report picker, rating badge, outcome-pending chip, the 15-stage strip from real records, hand-rolled SVG price/RSI charts from the pointer's series, eight tabs slicing the polished report, the bundle download. Deep-link #…&cap=1. |
| `console_worker.py` | Fable 5 (claude-fable-5) | The desk's supply door (GET :4562/desk): reports, stages (deduped latest-per-stage), and charts composed from f:charles's records via the librarian's seat — rule 7, no second truth; charts dereference the pointer at the door. The bundle door (GET :4562/desk/bundle) serves the ZIP by exact name only; traversal 404s. |

## Fable 5 — 2026-08-12 (0054 sp5 — the standing word and the loop)

| File | Author | Note |
|---|---|---|
| `console_worker.py` | Fable 5 (claude-fable-5) | The desk-watch doors: starting a standing walk stages with its terms readable and waits for the human; STOPPING is immediate and gateless (rule 11) — a cancelled posture is a sibling record, never an erasure. The supply door carries the watches; the world names its port. |
| `orreth_sim/desk.py` | Fable 5 (claude-fable-5) | The 21st asset: charles-trading-reflection — the bookkeeper's words, on the shelf like all the rest. |
| `agents/flavors/05-desk/pipeline.py` | Fable 5 (claude-fable-5) | Refresh mode (reuse under an honest banner; news always re-runs; degrades to full when the prior predates sections) · the report record carries its sections · grade_pending: outcome_pending reports graded against realized return vs SPY through the Farm's door, one lesson per report, graded_early said plainly. |
| `agents/flavors/05-desk/run.py` | Fable 5 (claude-fable-5) | --tend: read the standing word from the wire, walk when due UNDER it (no per-run gate), rest when already walked, reflect when ripe. |
| `window.html` | Fable 5 (claude-fable-5) | The standing word on the desk's wall with one-click stop — rule 11 visible in the room. |

## Fable 5 — 2026-08-12/13 (0054 — the reins, and the tabs made whole)

| File | Author | Note |
|---|---|---|
| `window.html` | Fable 5 (claude-fable-5) | The desk's reins: watch ANY symbol (stages at the human's gate), stop it gateless, ask for a report now (the human's word is the approval) — JB's corrected law made glass. Tabs render the FULL artifacts from the record first, polished slices as fallback for old walks. |
| `agents/flavors/05-desk/pipeline.py` · `run.py` | Fable 5 (claude-fable-5) | The record carries debates + delta beside its sections; the walk waits for its stall after a rig restart (the replant race caught live — refusals were the meter-gate working); dq list uncapped to 9; the tend loop answers desk-asks with no second gate and resolves them pointing home. |
| `console_worker.py` | Fable 5 (claude-fable-5) | The supply door passes sections/debates/delta. |

Proof from the human's own hands: JB typed PYPL into the reins and asked; charles walked it on his word alone (Hold), then the NVDA ask fully fed — 0 data-quality errors, complete artifacts on the wire.

## Fable 5 — 2026-08-13 (0054 — the desk finished: real charts, the crew, the landing)

| File | Author | Note |
|---|---|---|
| `window.html` | Fable 5 (claude-fable-5) | The reference's charts hand-rolled (Recharts is React-bound; the glass stays dependency-free): dashed grid, price axis, date axis, close line + translucent high/low band, the three indicator panes (Trend · Momentum & Volatility · Bollinger), legends, and a live crosshair TOOLTIP carrying OHLCV and every series at the cursor — the reference's exact hues. The price stands large in the hero. The pull opens onto a WORLDS LANDING (cards, organized for growth); deep-links #cap=1 and #capw=trading-desk. The rating pill is the reference's gauge tones, filled. |
| `scripts/dev.sh` | Fable 5 (claude-fable-5) | The desk crew is rig law: start/restart stand up the stall (:4570) and charles --tend beside the join door; stop sweeps them; status names them. The join door carries the desk-sized lease default. |
| `agents/flavors/05-desk/run.py` | Fable 5 (claude-fable-5) | A standing crew member outlives a slow gate: tend mode retries the join until a human welcomes him — every retry a fresh challenge, never a claim. |

## Fable 5 — 2026-08-13 (0055 sp1 — the manifest carries the desk: the acceptance passes)

| File | Author | Note |
|---|---|---|
| `orreth_sim/desk.py` | Fable 5 (claude-fable-5) | The capability MANIFEST joins the genesis (22nd asset, the first dict-bodied craft): the card, the door, the lifecycle words, and the desk's rooms declared as typed panels — controls · download · stat · strip · chart · tabs. |
| `console_worker.py` | Fable 5 (claude-fable-5) | The planting loop takes dict assets; the supply door composes PANEL-READY fields (derived tab markdown, last price) so the glass renders blind; the portal's world list reads capability-* manifests from the shelf, genesis as fallback — never a blank portal. |
| `window.html` | Fable 5 (claude-fable-5) | THE PANEL WALKER: eleven kinds (JB's L1, table included, sortable) rendering any world's declared rooms; generic controls wire declared inputs/buttons to governed requests. `renderDesk` is RETIRED — the manifest carries the desk pixel-for-pixel; the acceptance test passes. |
| `run.py` · `dev.sh` | Fable 5 (claude-fable-5) | The 41-card lesson: patience is ONE long-lived join request, not a retry flood — a single card held open for hours, polled; the stale flood swept as superseded. Crew logs unbuffered. |

## Fable 5 — 2026-08-13 (0055 sp2 — the tile is the lifecycle lever)

| File | Author | Note |
|---|---|---|
| `orreth_sim/desk.py` · `console_worker.py` | Fable 5 (claude-fable-5) | The crew declared in GENESIS (commands never run from the shelf's editable copy — a craft-edit must never become command injection); the capability-verb doors: stop/stop-fully immediate and gateless (rule 11 over a whole world), continue/start staged with terms and enacted on approval — words re-stood, dead crew raised; the door names each world's state (tending · resting · stopped · dark) from crew liveness + standing words. |
| `window.html` | Fable 5 (claude-fable-5) | The tile wears its state chip and its verbs; the world header too. Proven live in one sitting: stop → continue → stop → stop-fully (crew halted, tile DARK, honest) → start (staged, approved, crew raised, charles back on one patient card) → restored to the human's chosen state. |

## Fable 5 — 2026-08-13 (0055 sp3 — the second world: charlene proves the contract)

| File | Author | Note |
|---|---|---|
| `orreth_sim/crypto_desk.py` | Fable 5 (claude-fable-5) | charlene's genesis: 13 reference prompts (AST-verbatim), the shared machinery words carried from charles's, her persona, her MANIFEST — the desk's rooms inherited by contract. NOT ONE LINE OF GLASS. Lesson on record: json.dumps writes `true` — a generated Python module must IMPORT-EXECUTE in its check, not merely parse (the crash JB caught live). |
| `console_worker.py` · `orreth_sim/desk.py` | Fable 5 (claude-fable-5) | Two-world genesis registry; the /desk door parameterized per world (?key=); worlds grouped (genesis overlay when a shelf head predates the field); the bundle door serves any resident's exact-shaped name. |
| `pipeline.py` · `run.py` · `dev.sh` | Fable 5 (claude-fable-5) | One runner, any desk resident (--name/--world; craft prefix, bundle name); charlene joins the standing crew. |
| `window.html` | Fable 5 (claude-fable-5) | The landing groups worlds under their headers; opening a world drinks its own door (?key=); reloads stay world-aware. |
| `orreth_agent/capability.py` (+test) | Fable 5 (claude-fable-5) | The SDK's manifest builder: eleven canon panel kinds guarded at build; repo-local install documented; BYOP named as the cloud-phase door. SDK suite 23. |

## Fable 5 — 2026-08-13 (0055 — the manifest's governed door, proven whole)

| File | Author | Note |
|---|---|---|
| `console_worker.py` | Fable 5 (claude-fable-5) | The discovery: the craft-edit door already took dict bodies, and craft-edit was already an adoption kind — last night's drift card fired because I never filed one. The landing: the canon vocabulary now GUARDS the door (a capability-* edit must stay a manifest the walker can render; a foreign panel kind refuses loudly — "changing what the glass can render is a RELEASE, not an edit"). Proven in three acts: the iframe refusal · the trading-desk head gaining its group THROUGH the gate with lineage · the epoch turning 21 changes later with ZERO drift cards — the governed path leaves no accusation behind. |

## Fable 5 — 2026-08-13 (0055 — the third world, and the walk that learned to finish)

| File | Author | Note |
|---|---|---|
| `orreth_sim/options_desk.py` | Fable 5 (claude-fable-5) | chad's genesis: 13 reference prompts AST-verbatim, shared machinery carried, his persona, his manifest (⛓ · never a trade, never an exercise) — the third world, import-execute checked. |
| `agents/flavors/05-desk/pipeline.py` · `run.py` | Fable 5 (claude-fable-5) | Three walk lessons from chad's verbosity: the FIRST complete JSON object wins (raw_decode, trailing braces ignored) · strict=False (a literal newline inside a model's string is prose, not poison) · the reasoning cap raised to 3200 — and a walk NEVER DIES RICH: a lease-refused thought lands as a confessed dark stage, the walk carries on with what it has. |
| `window.html` | Fable 5 (claude-fable-5) | JB's landing find fixed: verb notes land NEAREST the click (the 0052 duplicate-id law — every card had the same note id, so every answer spoke on charles's card); verbs are state-honest (resting offers only stop-fully — no words walk to stop); stop-fully says what comes next. |
| `console_worker.py` · `scripts/dev.sh` | Fable 5 (claude-fable-5) | Three-world registry + planting; chad joins the crew; the join door's default lease grows desk-sized (400k — chad's fourth walk died at its LAST thought on 250k). |

## Fable 5 — 2026-08-13 (0055 — the gate comes to the tile)

| File | Author | Note |
|---|---|---|
| `console_worker.py` | Fable 5 (claude-fable-5) | JB's find: start/continue staged on the WORLD'S floor — a gate in a room the human never visits, so "nothing starts." The door now carries each world's staged verb; and a start with nothing to do (no stopped words, no dead crew) answers honestly on the spot instead of solemnly staging a no-op. |
| `window.html` | Fable 5 (claude-fable-5) | The tile wears its staged verb with the TERMS and the decision beside it — let it stand / not now — the 0052 law (decide where you stand) applied to the portal; a tile with a pending verb offers no other verbs until the word lands. |

## Fable 5 — 2026-08-13 (0055 — the states learn the human's language)

| File | Author | Note |
|---|---|---|
| `console_worker.py` · `window.html` | Fable 5 (claude-fable-5) | JB's find: "resting" undersold a desk that answers asks instantly — the state is READY, said in blue, with the card explaining itself ("answers asks now · no standing walks — watch a symbol inside to schedule one"); tending wears its walk count; every chip carries a plain-words hover. quinn's "stopped vs resting unexplained" finding, closed by the human who hit it. |

## Fable 5 — 2026-08-13 (0055 — the states corrected to JB's model)

| File | Author | Note |
|---|---|---|
| `console_worker.py` · `run.py` · `window.html` · doc §4 | Fable 5 (claude-fable-5) | JB's correction, made law: "the watchlist is content; it must never drive the state of the architecture." The old law read cancelled-watch TOMBSTONES as state. Now: running / stopped (paused — watchlist PRESERVED, the tend loop rests whole, continue recovers everything) / shut down (crew halted, records survive) — the world's posture is its own record on its own floor; the watchlist is an annotation on the chip, never the chip. |

## Fable 5 — 2026-08-13 (0055 — one desk's off-switch, one desk's silence)

| File | Author | Note |
|---|---|---|
| `desk.py` · `crypto_desk.py` · `options_desk.py` · `dev.sh` | Fable 5 (claude-fable-5) | JB's find: shut down ONE desk killed all three. Two flaws stacked — charles's crew match ("05-desk/run.py") was a SUBSTRING of every sibling's command line, and pkill -f is a substring gun; and the shared data stall was halted by a single world's word, aging out every floor's lease. Now every tender's match is exclusive (proven pairwise: no match hides inside another) and the stall is marked SHARED. |
| `console_worker.py` | Fable 5 (claude-fable-5) | The law: a shared crew member belongs to the RIG, never to one world — stop-fully halts only the world's own crew and says who stayed up for the siblings. Isolation proven live: crypto shut down alone; trading and options untouched; the stall breathing. |

## Fable 5 — 2026-08-13 (0055 — shut down reaches the infrastructure)

| File | Author | Note |
|---|---|---|
| the three geneses · `console_worker.py` · `window.html` · doc §4 | Fable 5 (claude-fable-5) | JB's correction: shut down that leaves the Docker count unchanged isn't shut down — the point is reclaiming infrastructure cost. Floors are now DECLARED like crew (the eco shared, each field its own); stop-fully halts the world's own hulls, start raises hull→health→crew; the janitor's replant bows to an exited hull (a shutdown outranks recovery). Two ordering laws from the live proof: resolve before you stop the floor the resolution rides, and lifecycle words live on the universe floor — ground that survives the world, so a shut-down desk can still hear its start. Proven whole: 4 hulls → 3 → 4, siblings untouched, records intact, charlene home through her gate. |

## Fable 5 — 2026-08-13 (0055 — the reclaim made whole: the word outlives the hull)

| File | Author | Note |
|---|---|---|
| `console_worker.py` | Fable 5 (claude-fable-5) | JB's two finds closed: the stumble spam (a worker knocking forever on a floor shut by the word) and the unreclaimed container (docker stop keeps the row — not his cost model). Now: THE DOWN-LEDGER — "shut by the human's word," durable on disk; stop-fully stops AND REMOVES the hull (docker ps -a drops); the round skips worded-down floors in silence; the janitor honors the ledger; start lifts the word, RECREATES an absent hull from the shipyard's spec (volumes + pg carry the memory), waits for health, then raises the crew. Proven whole: ps -a 4→3→4, zero stumbles, charlene home on recreated ground with both her reports intact. Mid-proof, JB's own start on the trading tile was honored by the same machinery — the system worked under his hand while it was being proven. |

## Fable 5 — 2026-08-13 (0055 — one log, and a printer that knows the word)

| File | Author | Note |
|---|---|---|
| `console_worker.py` | Fable 5 (claude-fable-5) | JB's report resolved as two truths: the stumbles he saw were a FROZEN log — my manual restarts had forked the worker's output to /tmp while he watched the rig's true file (~/.orreth/tmp/worker.log); and the quiet-skip guarded only the main round while other sweeps could still knock on a worded-down floor. Now the stumble PRINTER itself consults the down-ledger (one guard, every sweep), and the worker logs to the one true file again. Operational law on record: the worker's log is ~/.orreth/tmp/worker.log, always. |

## Fable 5 — 2026-08-13 (0055 — the portal breathes)

| File | Author | Note |
|---|---|---|
| `window.html` | Fable 5 (claude-fable-5) | JB's find: a start's journey (approve → hull recreated → health → crew → the resident proving his key) outlives any one-shot refresh, so the tile froze mid-transition until a manual reload. The open portal now drinks fresh every ten seconds — the glass's standing law applied to the pull — held still only by a typing hand (0052), so the reins never lose a keystroke. The tile walks its own states now: shut down → running, no reload, ever. |

## Fable 5 — 2026-08-13 (0055 — THE DISCOVERER: the Foundation forgets the worlds' names)

| File | Author | Note |
|---|---|---|
| `capabilities/*/genesis.py` (moved) · `console_worker.py` · `dev.sh` | Fable 5 (claude-fable-5) | The final seam: geneses moved OUT of the Machine into capabilities/; the Foundation sweeps the directory at boot — import-execute, vocabulary check, craft to the planting, crew raised with down-words honored and shared members deduped. ZERO by-name references remain in the worker (grep-proven); dev.sh names no world; watches resolve by the arriving door (a hardcoded-floor bug died in the refactor). The folder proof ran live: options-desk out → two discovered, the shelf's memory a faint declared card; home → three governed. Install is a dropped folder; the Machine below never learns who lives above. |

## Fable 5 — 2026-08-13 (0055 — the final verb, and the eye that follows discovery)

| File | Author | Note |
|---|---|---|
| `web.py` | Fable 5 (claude-fable-5) | quinn's capability views derive from the portal's own door — a dropped folder is under the UAT walk from birth; nothing hardcoded again. |
| `console_worker.py` · `window.html` | Fable 5 (claude-fable-5) | THE RETIRE DOOR: staged with honest terms → crew halts, floors reclaimed, the manifest's retired sibling planted — the card moves to the landing's retired shelf and the Chronicle keeps everything forever. The boot honors the shelf over the folder ("the folder installs, the shelf governs" — proven through a restart). REINSTATE returns the world whole: sibling, hulls, health, crew, the resident through the gate. Proven live: retire → 3 hulls, boot-honored, reinstate → 4 hulls, chad home. The lifecycle template is complete: install → running → stop/continue → shut down/start → retire/reinstate. |

## Fable 5 — 2026-08-13 (0054 + 0055 — CLOSED WHOLE by JB's own hands, era 0.55)

The closing proof was the human's: retire → reinstate on the Trading Desk, clean, no drift. The rites in this commit: both dive docs sealed with their eras · the road rows · VERSION 0.52 → 0.55 · two rows in the honest-boundary register (the purpose-through-Orreth claim with its named yardstick gate; the decoupling claim with its named entry fee) · the Capabilities layer added to the objective atlas. Nine human finds across the two dives, nine laws in the machine.

## Fable 5 — 2026-08-13 (0053 sp2 — every card wears its book)

| File | Author | Note |
|---|---|---|
| `window.html` | Fable 5 (claude-fable-5) | The two books on every card face: 📖 chronicle / ⚙ machine chips (inbox rows, archive, the pane). The polarity is the design: the Machine enumerates its OWN housekeeping kinds; everything else is Chronicle by default — a new world's words are purpose-side untaught. The Inbox splits: purposes first, the machine's housekeeping folded into a counted drawer. The soup JB named in the course correction ("so many cards that I am not sure what area they are focused") now labels itself. |

## Fable 5 — 2026-08-13 (0053/0054 — the in-flight truth: a silent card breeds re-asks)

| File | Author | Note |
|---|---|---|
| `run.py` · `console_worker.py` · `window.html` | Fable 5 (claude-fable-5) | JB asked for MSFT and saw nothing — three gaps, all real: the tend beat was five minutes (now one — a human's ask deserves a minute); duplicate asks for one symbol now FOLD into a single walk (his own double-click taught it); and the desk shows the IN-FLIGHT truth — every ask's state (⏳ asked / 🚶 riding) and the walking strip filling live from stage records on the breathing glass, N/16 as they land. A card that says nothing breeds re-asks; now it never says nothing. |

## Fable 5 — 2026-08-14 (0053 sp3 — the desks join the library: the wire that was never run)

| File | Author | Note |
|---|---|---|
| `console_worker.py` | Fable 5 (claude-fable-5) | The projection now drinks every DISCOVERED world's chronicle (reports and reflections first, per-world cap, dark worlds skipped) unless its manifest opts out — JB's law: the librarian is the universe's obtainer; isolation (the risky-experiment door) is the one honored exception. |
| `orreth_sim/stacks.py` | Fable 5 (claude-fable-5) | THE FIND, exposed by the human's own question: _chronicle_text flattens a KEEP-LIST of field names, and the desk's names (report · reflection · digest · rating · ticker · delta …) were never on it — a whole report flattened to NOTHING, admitted, classed, retrievable, and silent. Names matter, twice over. The desk's words join the list; his NVDA question now returns the actual decision text at score 1.0, cited. |

## Fable 5 — 2026-08-14 (0053 sp3 — the brain pull: state is telemetry, never an NLP paraphrase)

| File | Author | Note |
|---|---|---|
| `console_worker.py` | Fable 5 (claude-fable-5) | GET :4562/brain — the state of the active brain from its own instruments, JB's law verbatim: observability and telemetry, aggregation AND partitions. Partitioned by the ARCHITECTURE (universe → ecosystem → floor, off the heartbeat chain, rule 7), never by a baked capability name — worlds appear only as data ("tended by …" from their manifests; shared floors attributed to no one; isolate worn as a chip). Census = health totals beside a cached classified sweep that confesses its window; cognition grouped by mind across live AND sealed hours; metabolism wears its one-floor boundary honestly; the yardstick panel reads scored recall runs generically — recall stays NLP's one earned seat, because it is the inherent ability gauges cannot fake. |
| `window.html` | Fable 5 (claude-fable-5) | The 🧠 brain pull — second lever beside 📈 capabilities ("Capabilities = what the machine does; Brain = what the machine IS"). Class bars per partition, ecosystem subtotals, the by-mind meter table, the dials table, the yardstick panel empty-honest until the first scored run. Deep-link #brain=1; the two pulls are mutually exclusive; 10s breathing. |

## Fable 5 — 2026-08-14 (the afternoon of reins: breathing, cache truth, and the witness's gate)

| File | Author | Note |
|---|---|---|
| `window.html` | Fable 5 (claude-fable-5) | The brain pull breathes at the human's hand: manual by default (each breath reads every floor; a lapsed census re-sweeps them all — the cost and the CPU spike spend at the ↻, once), the 10s schedule an opt-in remembered in his own glass, the footer confessing which mode the numbers were read under. |
| `main.rs` (orrethd) | Fable 5 (claude-fable-5) | /window serves Cache-Control: no-cache — a browser held a stale shell through two rebuilds while fresh data breathed inside it, misleading the human twice in one day. Every load revalidates now; a plain reload is always the truth. |
| `console_worker.py` | Fable 5 (claude-fable-5) | The witness's gate amended on JB's word (the recycle-noise find): the risen worker still transcribes the silence into the signed Chronicle and still rings once per rise — the testimony lives in three books — but the card no longer stands staged after the pulse has returned. A gate must wait only while its condition holds; recycle cards left standing were teaching the human's eye to skip witness cards, law 6's own definition of noise. Proven live: four lingering cards across the floors withdrew themselves on the next round. |

## Fable 5 — 2026-08-15 (0053 sp3 — the yardstick: recall becomes a standing, not an anecdote)

| File | Author | Note |
|---|---|---|
| `console_worker.py` | Fable 5 (claude-fable-5) | L4 closed on JB's word with his adjustment as law: no question names a symbol — "the most-walked symbol" forces the machine to know its own recent work before it can answer. The ten questions are GENESIS ONLY in code: they plant as shelf craft (the-memory-yardstick v1) and JB's red ink is a craft-edit from then on. yardstick_run rides the REAL ask lane the parlor uses; vera judges each answer from an outside bench (rule 2), metered under her did inside the assay's declared ceiling; the run lands as ONE memory-standing record the Brain pull already reads. Manual only (ORRETH_YARDSTICK_NOW, one pass per life; a resting pass never eats the word) — the weekly schedule arrives as a governed standing word in the scheduled-asks build. FIRST RUN ON THE RECORD: 10/10 scored, mean 0.375 — honesty strong (0.85–0.95 where the lane confessed absence), recall power weak, and the weakness LOCATED: the dispatcher's shape-match misses these question forms and the naive default row serves lexical noise instead of confessing. The yardstick did its job on its first breath. |

## Fable 5 — 2026-08-15 (0053 sp3 — the lane learns: confession, self-knowledge, and the governed revision)

| File | Author | Note |
|---|---|---|
| `orreth_sim/rivals.py` · `orreth_sim/tournament.py` | Fable 5 (claude-fable-5) | THE CONFESSION FLOOR: a best hit under 0.3 never wears the answer's clothes — the reply leads with the honest miss and the hits ride demoted, named as nearest. Served noise scored zero on the yardstick; a true confession scores high. |
| `orreth_sim/dispatcher.py` | Fable 5 (claude-fable-5) | The comparative sense: each-and-which asks now classify — the shape is the organ's sense (code); the rule that routes it rides the standard's own governed lane. |
| `console_worker.py` | Fable 5 (claude-fable-5) | THE SELF-KNOWLEDGE STEP: machine-state and indirect references resolve from the machine's own record BEFORE retrieval — the isolation roster from the manifests, the most-walked symbol counted off report records (standing aside for comparative asks, vera's find), provenance read from record metadata (author·floor·clock now ride the projection), the locality sweep answering "outside the desk floors" by attribution. Replies speak ANSWER FIRST, the routing diary at the tail. The judge earns one typed re-ask before any void. And the routing revision (temporal→rerank · comparative→swarm) rides the standard's own lane to the human's gate with the yardstick's standing as evidence — a routing change is a proposal, never an edit to code. Run 3 measured the climb mid-work: mean 0.375 → 0.526. |

## Fable 5 — 2026-08-15 (0053 sp3 — scheduled asks are born, the memory program their first customer)

| File | Author | Note |
|---|---|---|
| `console_worker.py` | Fable 5 (claude-fable-5) | SCHEDULED ASKS — the feature JB named, built on the desk-watch's exact standing-word law: staging waits at the gate with its terms (weekly · ten questions · vera's declared ceiling · ~15k tokens), approval writes the signed word, resting is gateless and a sibling on the record. The beat honors the word using the standings as their own clock (last run + cadence = due), single-flight in its own thread, hourly cooldown so a closed ceiling never becomes a busy loop. v1 knows one ask — the yardstick — and residents' own scheduled asks extend `what` when the Studio lands. The brain door serves the schedule's face (standing · cadence · next due). |
| `window.html` | Fable 5 (claude-fable-5) | The yardstick panel wears the reins: ⏰ stage-the-weekly-schedule (one approval in the Inbox starts the rhythm) or the standing chip with next-due beside a gateless rest button. |

## Fable 5 — 2026-08-16 (the kernel's mode + the flows — JB's two items before the Studio)

| File | Author | Note |
|---|---|---|
| `console_worker.py` · `scripts/dev.sh` | Fable 5 (claude-fable-5) | DEV vs PROD (JB's kernel law): Orreth is the kernel, residents are embedded firmware. ORRETH_MODE rides the machine — dev keeps the studios' gated edit doors open; prod makes resident firmware READ-ONLY at every edit door, changes riding only the release ceremony (0045 sp3). The brain payload wears the mode; the craft-edit lane enforces it. Also: the ask lane's last walk joins the brain payload for the flow graph. |
| `window.html` | Fable 5 (claude-fable-5) | THE FLOW ENGINE — a hand-rolled, dependency-free SVG DAG renderer (layered by longest-path, curves with arrowheads, live state joined from records: ✓ done · pulsing live · dim pending). One engine, every flow: worlds declare theirs in manifests (the panel walker's twelfth kind), and the machine's own ask lane draws with the same hand in the Brain pull — the ask → dispatcher → seven arms → answer, the chosen arm lit. The mode chip leads the brain strip, red in prod. |
| `capability.py` (SDK) · `capabilities/*/genesis.py` | Fable 5 (claude-fable-5) | "flow" joins the canon panel vocabulary (twelve kinds; SDK guard + suite grown). All three desks declare the sixteen-stage walk as one governed DAG — fetch fans to four analysts, the debate joins to the research manager, the trader fans to three risk voices beside compare-to-prior, all meeting at the portfolio manager — live as records land. |

## Fable 5 — 2026-08-16 (0056 sp1 — the rooms stand)

| File | Author | Note |
|---|---|---|
| `console_worker.py` · `window.html` | Fable 5 (claude-fable-5) | The family's rooms, one renderer: compose_resident answers by THREE truths in order — the presence roster (organs with live vitals), the architecture (a field wears its resident's name; seats on f:charles aggregate into charles's own room), and the manifests (family with no lease gets a room that says exactly what it waits for — JB's PYPL lesson made permanent law). The vitals a parent asks first lead; every deferral stands on the wall in plain words; the view travels as DATA through the same twelve-kind walker the worlds use. Doors: the ⌂ on every named rail row, the parlor's header, and addresses (#res=vera) because a room is a place. |

## Fable 5 — 2026-08-16 (0056 sp2+sp3 — the rooms grow whole, at click speed)

| File | Author | Note |
|---|---|---|
| `console_worker.py` · `window.html` | Fable 5 (claude-fable-5) | sp2: THE WORK (the desk residents' latest walk on the flow engine, vera's verdicts, the librarian's lane; the rest confess) and THE WORDS (the shelf by name and by the wearer registry, the mode law speaking — dev editable, prod read-only). sp3: THE SCHEDULES — the standing-word machinery grown to identities (what·resident·question): any question a resident answers repeats on a cadence (JB's L4), staged for one approval, fired down the parlor's own lane so the answer is a real audience on the record, the word itself the clock, rested gateless; THE MINDS from each floor's stable; THE RELATIONS as one small map on the flow engine. And the perf laws that kept it honest: the read law (tags first, bodies only for needed rows), the memo, the warming thread — a 45-second room and a 30-second landing both became a breath. |

## Fable 5 — 2026-08-17 (0056v2 — the Commander correction, three spoonfuls whole)

| File | Author | Note |
|---|---|---|
| `window.html` | Fable 5 (claude-fable-5) | JB's tough feedback ("your views are like reading documents") became the correction, judged every pass against his tmp/CO references and the live CortexObserver he opened for me. sp-A THE CANVAS: a pannable dotted-grid workspace of node cards (kind eyebrow · name · description · status chip), serpentine bands so sixteen stages read like a page, direction-aware elbows, dashed group boxes, minimap, zoom/fit/fullscreen/lock. sp-B THE MODAL: compact and tabbed (Info · Graph · Prompts · Model · Metrics · Schedule) — prompts edited in place through the one-motion craft-edit lane with canon and prod refusing honestly; the Schedule tab wears the cron face (objective textarea, cadence and at-hour with a live echo, job cards with next-due, gateless rest) — jobs seen and edited THROUGH the resident that owns them, because the views are for humans and agents just run code. One ⚙ door per roster row on his correction. sp-C THE COMMAND-FIRST ROOM: NEW ANALYSIS leads, how-it-works folds into a genesis-declared story map, past reports become the pill-row INDEX (the thirteenth canon kind) opening a report's detail on demand. His verdict: "oh that's so much nicer." Lessons paid for: let-globals never attach to window (window.DESK blinded the index and the live pulse); a genesis dict's key order can sit after the view (bracket-walk, never rindex). |
| `capability.py` (SDK) · `capabilities/*/genesis.py` · `console_worker.py` | Fable 5 (claude-fable-5) | "reports" joins the canon (thirteen kinds); the desks declare rich flow nodes, the story map, and detail-flagged panels — worlds bring their whole room, the Machine still knows no world by name; scheduled asks carry their hour and the beat honors the clock. |

## Fable 5 — 2026-08-22 (the lease learns to renew — 0058's named wound, half-paid at the rule-9 gate)

| File | Author | Note |
|---|---|---|
| `orrethd/src/model.rs` · `main.rs` | Fable 5 (claude-fable-5) | The fuel clause: a lease's budget becomes an ALLOWANCE per declared window (`Fuel {remaining, allowance, renew_s, window_started}`); terms adopted from every VERIFIED token (the or_insert-once ledger that ignored vera's fresh mints is dead); the window's refill lands on the meter_log, quiet windows fold to one refill; `/model/replenish` = the human's refill door; usage() serves the fuel posture and every ledger subject even at zero metered calls. orrethd's FIRST unit tests (6) hold the law. |
| `orreth_sim/fuel.py` · `tests/test_fuel.py` | Fable 5 (claude-fable-5) | The judgment half: posture (fueled · drained · lump-dry · unknown, EST_FLOOR=500 — the wound's own 419 falls drained), drain cards keyed one-per-subject-per-window. 6 tests; conformance 350→356. |
| `console_worker.py` · `window.html` | Fable 5 (claude-fable-5) | fuel_clause() at every mint; the drain watch (fuel_beat) files cards deduped across their whole fate (a decline holds for its window); on_fuel_request stages-with-evidence / replenishes / rests; Inbox ranks fuel beside witness. RULE-9 GATE HELD: budget.renew_days needs contracts/v0's Budget to learn one optional field — minting reverted to schema-legal lumps until JB's word (ORRETH_LEASE_RENEW_DAYS=0 default). |
| `contracts/v0/common.schema.json` · `fuel.py` · `console_worker.py` | Fable 5 (claude-fable-5) | THE GATE ANSWERED (same day): JB's explicit word (AskUserQuestion, recommended path) added ONE optional field — Budget.renew_days — and the wound closed whole: daily default (ORRETH_LEASE_RENEW_DAYS=1), self-renewal proven live (a 30s proof window refused mid-window then renewed ITSELF at the turn; charlotte's real thought minted under the daily clause, 399,034 of 400k). The walk's find became law: drained + past renews_at = fueled (lazy renewal — never card what heals on its next ask). Suites: conformance 357 · SDK 23 (parity green) · orrethd 6. |

## Fable 5 — 2026-08-22 (the backlog day, continued: the machine's tasks + the meter-log door)

| File | Author | Note |
|---|---|---|
| `console_worker.py` · `window.html` | Fable 5 (claude-fable-5) | THE MACHINE'S TASKS (JB's tabled 2026-08-17 seed, built now that the UI season it waited on has closed): `_machine_tasks()` composes every no-resident standing word (+ known runners, next-due) and the machine's fixed rhythms into the /brain payload; the Brain pull's yardstick reins grew into one kernel-tasks table — run-now · a cadence editor whose edit is a RE-STAGED sibling through the same scheduled-ask gate · rest/schedule generalized to any what. Proven by the human path in the glass. |
| `orrethd/src/farm.rs` · `main.rs` · `console_worker.py` | Fable 5 (claude-fable-5) | The meter-log door (0059's recent-callers park): `Farm::recent_callers()` folds the meter_log per service → caller DID with calls + last-seen (suite-held, 2 farm tests — the plane suite is 8); GET /farm/callers serves it; `_farm_blast` reads it so every rest/decom/reapprove card says WHO LEANED, organ names where known. |
| `console_worker.py` (denied branch) | Fable 5 (claude-fable-5) | THE WALK'S FIND: the farm's denied branch decommissioned a service on ANY denied action — a declined REST killed com.microsoft/learn live. Fixed farm-shaped like 0058's mind-branch lesson: a denial of rest/resume/decom/reapprove/allocate moves NOTHING ("your word was about the verb, never the service"); only a denied PLANT decoms. Proven: replanted through the gate, rest declined, the service stayed serving. |
| `console_worker.py` (feedback_beat → _feedback_floor) | Fable 5 (claude-fable-5) | THE WHOLE-RIG FEEDBACK SWEEP (0048's named gap paid): the sweep walks every tended floor — universe every beat plus ONE floor per beat round-robin (flat cost, the perf law held); one studio reads every word (legs + organ doors at the universe), the resolution and closure land at the feedback's OWN floor. Proven: a 👎 on f:prod found within a beat, routed repair-staged with the human's words as rubric, closure home at f:prod. En-route ops: the Docker recycle that darkened every shipyard floor was healed by hand (docker start, the grave f:probe excepted) and f:probe's lost dark-word restored to the down ledger; SEED NAMED: a shipyard self-replant that honors the down-ledger. |
| `console_worker.py` (capability_tools_intake V2) | Fable 5 (claude-fable-5) | JB's three-restart find: the intake asked at u:demo while the real tool SERVED on f:charles, and its idempotency was in-memory-only, so every boot re-carded a settled question. V2: the ask lands at the capability's OWN floor (genesis names floor+port); standing reads the floor's durable ledger; «settled» is any plant ask in the surviving queue whatever its fate; the beat retries floors that wake after the worker. The u:demo ghost denied into decommission (history kept); a fresh boot logged the skip and filed nothing. |

## Fable 5 — 2026-08-23 (the messaging pass — "we can't leave humans wondering what's going on")

| File | Author | Note |
|---|---|---|
| `console_worker.py` · `orreth_sim/fingertip.py` | Fable 5 (claude-fable-5) | THE HONEST QUESTION: the plan's delivery question told two lies (the work was NOT waiting; the 3-minute clock was unnamed) — both twins now name the request, quote the born-words where they exist, give a concrete floor example, and tell the truth about silence and the clock. QUESTIONS DIE WITH THEIR PARENTS: _tend_objective withdraws its unanswered question at assembly with the whole story; question_reaper sweeps orphans whose machinery state died in a restart, naming the settled parent when it can be found. Proven live twice: JB's stale card withdrew itself within a beat; a fresh objective asked honest → expired → withdrew at assembly. |
| `console_worker.py` · `window.html` | Fable 5 (claude-fable-5) | REFS ARE DATA, NEVER PROSE: the reflex card destroyed record ids at authorship (`ref[:22]…` baked into the sentence, no field) — full refs now ride text AND field there, in the feedback loop's cards, and the version walk. THE CROSS-FLOOR RECORD DOOR (0052's named gap paid): GET :4562/record hunts every tended floor and names the record's home; a shortened ref confesses it can never open; a whole-rig miss explains the two honest departures (distilled · purged); the glass reader falls through the door before shrugging, and says where the work happened. |
| `orreth_sim/speech.py` · `console_worker.py` · `tests/test_speech.py` | Fable 5 (claude-fable-5) | POLICY-AS-CRAFT (0059's named park paid, 2026-08-23): the warden's CHECKS stay firmware — vigil never stops looking because someone edited a line — but her eight WORDS (seven confessions + the credential-pattern list her nose runs on) join the 0050 speech shelf, planted as v1 assets at boot and tunable through the one-motion craft-edit door. Two suite laws added (slot honesty on the mismatch counts; the editable nose). Proven live: a dirty plant confessed from the shelf; «warden-dead-probe» was rewritten through the door and the next dirty plant spoke the human's words, the old version behind it with lineage. Conformance 359. |
| `console_worker.py` · `orreth_sim/identity.py` · SDK `craft.py`/`mind.py` · `window.html` | Fable 5 (claude-fable-5) | THE 0045 GAPS + PLAYGROUND V2 (2026-08-23): the /craft supply door takes the SAME becky-chained lease that fuels a citizen's thoughts (POST lane; chain to the pinned root, subject must BE the claimant, did:key registers on first sight — Nanda.known() keeps a revoked did dead; prod refuses tokenless one-faced, dev serves confessing); SDK acquire() grew token + the mind presents client.token (SDK 24, stub-door test); the eco floor joins compose_governance wearing its floor (first sweep surfaced distillation-dials at e:cloud); the playground's «✎ propose a test» fills required fields from the PINNED schema (deterministic, free) and FPARGS keeps proposed AND hand-typed args through the tick (a pre-existing wipe found by the walk). Proven live: scout's standing-welcome re-join → leased acquire leased:true; forged-subject + foreign-chain refused one-faced. |
