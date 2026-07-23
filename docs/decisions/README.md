# Decisions

The decision ledger — what's **locked**, and what's **open** (to be made in a `design/` dive and then moved up here).
Full rationale for locked items lives in `../vision/FUTURE-the-orreth.md`; use cases that drive the open ones live in
`../vision/use-cases.md`.

---

## ✅ Locked

### The center (rebaselined 2026-06-30 — memory-first)
- **Orreth is a memory substrate**, security-first and identity-anchored, across spacetime. **Governance is its first
  application, not its purpose.**
- **The Living Identity is the primary primitive** — universe-unique, used at every layer, decoupled from the process
  (online / offline / reboot; reboot ≠ death). **Memory is keyed to the identity, not the process.**
- **The Universe is Foundation *and* Apex** — universal policy rests on it (down), all memory rises to it (up).
- **Three flows:** policy **DOWN** (foundational, non-overridable) · memory **UP** (pruned at every layer) · retrieval
  **UP** by time-horizon (Sourced + Verified).
- **The layers are filters** — prune / dedup / summarize / compress to protect the Universe's space (makes "years" affordable).
- **Skills are crystallized memory** — versioned across the universe; they reduce the need to trawl raw memory.
- **Retrieval is the #1 security surface** — an authorized capability, tenant-isolated on read.

### Trust & safety (design draft `0013`, direction locked 2026-07-01; all §12 decisions JB-locked — see below)
> **Correction & provenance (Fable 5, 2026-07-02):** an earlier auto pass recorded a "0013 close-out — locked
> by JB" block **JB never made**; a same-evening pass caught that and reopened them — but that pass, though it
> signed itself "Fable 5," was **also Opus 4.8** (JB's prompt routed to Fable 5 twice, aborted twice, and the
> desktop app silently fell back; the model self-attributed from the prompt). Verified 2026-07-02 by genuine
> Fable 5 against the desktop session's HMAC-signed audit log (per-message model IDs). The direction below is
> sound and was JB-relocked for real (audit-confirmed AskUserQuestion answers). The mislabel is the case study:
> **non-optional attribution — this platform's own floor — is what makes "who did this work" a checkable fact
> instead of a claim.** Exactly the not-good-thing the dual-use review exists to catch.

- **The Custodian tier.** Hosted orreth.ai is a Harness one tier above every customer Universe, joined
  floors-only/observe-only, with **deliberately asymmetric powers**: it can *freeze* (quarantine) and *enforce
  platform floors*, but is **structurally blinded to tenant content**. Landlord, not spy. The Custodian is
  governed *harder* than any tenant (multi-party co-sign, fully audited — the watchers of the watchers watched).
- **Platform floors (the meta-cascade)** — foundational, tighten-only rules cascade into every Universe, no GOD
  can loosen: no targeting non-consenting real people · illegal-content prohibition · PII/regulated consent ·
  no autonomy designed to evade governance · non-optional attribution · autonomy ceilings by trust tier.
- **The Warden (`vigil`, christened 2026-07-02) — detection, NOT enforcement** *(the HITL correction)*. A resident (TCB) organ at every layer:
  tenant-serving within, content-blind (behavioral/metadata only) to the platform. It observes/alerts/rate-
  limits-in-bounds and *stages* actions; it **never** quarantines, reads plaintext, or acts on another tenant
  alone. Enforcement is a separate HITL-gated control-plane act.
- **HITL placement rule:** *if an action can affect a party who did not initiate it, it escalates to a human.*
  Machine speed for detection; human judgment for consequence. (See `0013` §7 for the full map.)
- **Quarantine — graded, control-plane, HITL-gated:** throttle (autonomous, bounded) · suspend/freeze
  (2 Custodian co-signs, reversible, preserves) · destroy (3 + cooling-off, irreversible). Freezes never
  delete; legal-hold overrides erasure (preserve-then-adjudicate); customer notice default unless lawfully gagged.
- **Lawful access — no backdoor:** due-process-gated, 3-co-sign + legal sign-off for plaintext, scope-minimized,
  audited; BYOK/split tiers make unilateral operator read technically impossible.
- **Self-hosting has no Custodian** — the operator is it; the safety story is strongest for the hosted service.

### Locked 2026-07-01 (0013 — genuinely by JB this time, via AskUserQuestion)
- **Key custody: tiered.** Platform-managed default (self-serve) + BYOK (privacy-serious) + split/escrow
  (regulated/defense). "We structurally cannot read you" is a true, sellable promise at the higher tiers.
- **Quarantine bars: 2 to freeze, 3 to destroy.** Throttle autonomous (bounded); suspend/freeze = 2 Custodian
  co-signs, reversible, preserves state, customer notice unless lawfully gagged; destroy = 3 + cooling-off.
  Active child-safety harm freezes first, notice after. No single employee is a god.
- **Onboarding: risk-tiered.** Benign domains self-serve instantly; flagged domains (health, finance,
  PII-at-scale, bio/cyber dual-use, population-scale observation, influence ops) → human review + KYC before a
  key issues; published refuse-to-host list.
- **POC order: Earth Mapper first** (public/consented data, near-zero regulatory surface, exercises collective
  memory + skills cascade + the window literally), **Agentic Enterprise second** (compliance floors + full HITL
  map built in parallel, then the C-suite/regulator showcase). *(Amended 2026-07-02 — see "Proving grounds"
  below: The League joins as the time axis; League first if serialized; Enterprise in parallel throughout.)*

### Locked 2026-07-02 (0013 — the genuine Fable 5 pass, via AskUserQuestion)
- **Platform-floor changes: asymmetric bars.** Tighten = 2 Custodian co-signs + versioned publication (safety
  moves at safety speed); loosen or remove = **3 co-signs + cooling-off + published changelog** (floors never
  loosen quietly). The floors are versioned, published artifacts; changing them is the highest-blast-radius act
  in the system and now has its own §7 HITL rows.
- **Custodian telemetry: published contract + tenant mirror.** The platform-facing telemetry schema
  (behavioral/metadata, never content) is a **versioned public contract** in `contracts/`, and every tenant's
  pane renders a **live mirror of exactly what their Universe reports up**. "Just metadata" is the surveiller's
  oldest defense; Orreth publishes what it can see and lets the tenant watch it seeing.
- **The Warden is christened `vigil`** — becky says *who you are*; vigil watches *what you do*. Its
  non-removability is a **contract, not magic**: presence + telemetry are terms of the hosting join credential,
  backed by a signed dead-man heartbeat (silence is a floor breach; the quarantine ladder answers).
- **Proving grounds: twin axes + northstar** *(amends the POC-order lock)*. The spacetime window has two axes.
  **The League** ("Create Your Sports League") proves **time**: accelerated universe-time yields decades of
  lived, identity-keyed memory in weeks — the only honest proof of "no limit" depth on a young platform —
  with pruning-as-fidelity-curve made legible (games → box scores → legends) and a near-1:1 costume for locked
  0002 decisions (transfer veto/compel, interview-as-scouting, archetype→incarnation, sibling walls, roll-up
  standings). Cost shape: cheap cognition, rich identity. **Earth Mapper** proves **space** (the live-globe
  poster; dogfooded first tenant). The **Agentic Enterprise** northstar is built **in parallel** throughout.
  If serialization is forced: League first.
- **Funnel: Watch → Play → Build → Buy.** Every article ends at a public, read-only spacetime window on a
  living demo universe (no signup — scrub a league's history in the browser) → create-your-league self-serve →
  dev docker eco → enterprise track.
- **New 0004 input — universe-time vs wall-clock (the time-dilation dial)**, surfaced by the League: memory
  horizons, retention, and pruning cadence run on universe-time; security TTLs and co-signs stay on wall-clock.
  Owned by the Tier Profile dive.

### The mechanism
- **Name** Orreth; repo `orreth`; "Harness" = the architectural primitive; tiers Universe / Ecosystem / Field / Agents.
- **One recursive primitive**, `tier` = a Tier Profile (config, not code). **Depth capped at 3**; expandable by SDK/CDK.
- **Roll-up** = monoidal sufficient statistics + signed content-addressed pointers; count-weighted confidence.
- **Cascade** = inherited Standards; floors non-overridable (lexicographic); soft = most-specific-wins; skills additive.
- **Consent = the join spectrum** (fully-joined / floors-only / observe-only / decoupled): **floors compelled for the
  joined, everything else offered**; a leased agent's floor is enforced by its lease/capability credential.
- **Targeting** = one Selector (`all` / `role` / `ecosystem` / `field` / `selection`); target at-or-below only.
- **Security** = recursive DID chain; **resident (TCB) vs registered (workforce)** agents; tenant isolation recurses.
- **Rust** for the plane (identity-verify, ingestion, cascade/pruning resolver, retrieval routing + time-budget gating,
  brainstem); **Python / LangGraph** for cognition (memory stewards, analysis agents).
- **Headroom** adopted as the byte substrate (compression · CacheAligner · CCR reversible store · cross-agent memory);
  governance/pruning *policy* stays ours; vendor / pin / review.
- **Memory records** = append-only + content-addressed + DID-signed; promoted-up-as-pointers; **governed-tombstone erasure**.

### Locked 2026-07-01 (the structure dive, `design/0000`)
- **becky is an IAM *agent*** — resident (TCB), the identity issuer root→leaf and the agentic half of every
  promotion gate. becky is never a human; humans are separate governed principals who appear only at the gates.
- **Every layer is staffed by resident agents** (steward, governance, analysis, becky). The hierarchy runs
  entirely agentically; humans conduct at the gates, they do not operate the layers.
- **CortexObserver is a reference, not a component.** The Field tier is **native Orreth**. CO proved the pattern
  and taught interoperability (humans using NLP to engineer complex LangGraph agent graphs); it may join via an
  optional adapter, but it never drives Orreth's design. Orreth's layouts and usability are designed fresh
  (Fable owns design/UX/build; JB owns vision/objectives).
- **The Field is native Orreth's only special node** — where governance meets a life; children are Agents.

### Locked 2026-07-01 (pruning pre-decisions, JB's calls — drive `design/0003`)
- **Pruning brain = hybrid.** Deterministic policy **floors** keep the non-negotiables (failures, floor-breaches,
  outliers); the resident **steward** distills the rest under a governed rubric, within budgets.
- **Apex fidelity = distilled + signed pointers.** The Universe holds distillations plus signed pointers to raw
  retained below per retention dial; deep queries re-fetch surviving raw. Expired raw resolves to a tombstone-stub —
  results say so honestly.
- **Tombstones: annotate, don't rewrite.** A consent tombstone purges raw; derived aggregates *stand*, carrying a
  signed redaction marker in their `derived_from` chain. History never silently changes.
- **Dive order: 0003 (pruning) → 0006 (becky) → interop/UX** (NLP-driven agent-graph engineering + the pane).
- **QA sample: yes, per-tier dial.** Sealed 1-in-N raw survives past horizon purely to measure distillation
  loss; distillation quality is a measured, driftable objective.
- **Budget exhaustion: degrade to floors + flag.** Floors never stop, nothing is dropped, surges distill
  coarsely with an honest "coarse window" marker. The steward never backpressures the workforce.
- **Distillation timing: cadence + event triggers.** Predictable base cost; novelty/cohort spikes fire extra passes.
- **becky's trust root (anchors 0006): did:web universe roots + did:key leaves.** Universe roots anchored under
  `orreth.ai` (KMS/HSM-held, multi-party rotation); agents get cheap did:key identities chained to the root.
  Self-hosted / air-gapped universes use a pinned root distributed out-of-band — a policy dial, not a fork.

### Locked 2026-07-01 (0006 close-out)
- **Capability tokens are biscuit-style** — the delegation chain travels in the token; attenuation and
  verification are fully offline; no introspection callbacks in the trust path.
- **Apex co-signs: 2 humans; root rotation: 3.** Urgent apex acts stay workable at 3 a.m.; the root of the
  trust fabric — scheduled, never urgent — survives a compromised pair.
- **Token TTLs are Tier Profile dials** (0004) — starting values workforce 24h · resident 30d · session keys
  per-session. Shape locked in 0006; numbers are policy.

### Locked 2026-07-02 (0004 close-out — the two clocks)
- **The clock model: declared + monotonic high-water + lived-vs-ingested.** Meaning runs on **universe-time**;
  security and money run on **wall-clock**. A universe asserts its own now (`occurred_at`, signed) and the
  gateway stamps physics (`received_at`); lived memory below the scope's high-water mark is rejected —
  **memory-backdating is structurally detectable** — and backfilled history enters only as signed
  `ingested-archive` (biography vs data, never blurred). Surfaced by the League; general to every sim universe.
- **Queries speak universe-time by default.** The scrubber and the retrieval contract speak the time the
  memory means; `clock: "wall"` is the explicit ops/forensics escape hatch.
- **Retention is min AND max per record class.** Keep-at-least (SOX) and keep-at-most (GDPR) cascade
  independently, tighten-only; legal hold = a governed `min: forever` — no longer a special case.
- **Objective vector: shape in 0004, scoring in 0005.** Weighted objectives with never-trade-off floors live
  in the TierProfile; how they're scored lands with the roll-up monoids.
- *Schema deltas landed same day (UniverseTime/WallClock split, occurred_at/received_at, provenance_class,
  TimeWindow.clock, TierProfile clock/objective/retention_classes); simulator enforces + proves: 12/12 tests.*

### Locked 2026-07-02 (0005 close-out — the score that composes)
- **Confidence = Bayesian posterior** (discharges open #7, the last carried from 0001). Scores mean-match into
  Beta pseudo-counts; a weak per-tier prior (`confidence_prior`, Tier Profile dial, default uniform) is applied
  **once at the report edge** — bundles store pure evidence, merging them can never double-count opinion.
  Reported as mean + 95% credible interval + n: count-weighted by construction, honest at tiny n.
- **Floor breaches: flag, never average away.** Any breach in a window sets `compliance: breached` —
  unmissable, undilutable by volume — and the performance mean is untouched. A 0.98 agent with one compliance
  breach shows both truths.
- **Portfolio/interview shows mean + interval + n** ("0.94 ± 0.03 across 47 runs") — honest uncertainty is the
  anti-star-rating differentiator; the 0002 noise defense applies on top.
- *Mechanism landed same day: `run-record.schema.json` (RunRecord · StatBundle · RollUp), simulator
  `rollup.py` + `record_run`/`roll_up` (push-up, pointers only — raw runs never travel), 5 new tests incl. the
  monoid one-truth law and a League-standings tree roll-up: 17/17.*

### Locked 2026-07-02 (0010 close-out — the doors)
- **Model budget exhaustion: degrade where pins allow.** A squeezed call routes to a cheaper tier with an
  honest `degraded` flag (drift/canary can tell budget-dips from skill rot); a **pinned `model_tier` is a
  floor** — unaffordable pinned calls fail honestly, never silently dumber. Same shape as the steward's
  degrade-to-floors-and-flag: Orreth degrades loudly or not at all.
- **Signals: Tier Profile dial (`none | state-changing | full`), default state-changing.** Signals are
  transport; a state-change **must land as a MemoryRecord to have happened** — "if it's not memory, it didn't
  happen." `full` for REAL/regulated universes (the first concrete wild-vs-REAL dial); vigil sees volume/shape
  as metadata regardless of the dial.
- *Mechanism landed same day: `agent-surface.schema.json` (five verbs + ModelCall/Signal), the `signal_capture`
  dial, simulator `agent_surface.py` (ModelGateway · AgentSurface · join_workforce): 20/20 tests.*

### Locked 2026-07-02 (0011 close-out — the factory)
- **Upgrade in place; re-stamp is a new life.** Archetype upgrades reach running incarnations through the
  normal Standards cascade — **identity and memory persist** (the League's player improves in the offseason;
  the Enterprise's accountant keeps its quarters of context). An explicit re-stamp mints a new DID with the
  same lineage — a sibling, never a silent successor. Memory is the asset; upgrades don't destroy it by default.
- **Rookie probation: full-grade until the first bundle.** Fresh incarnations run at judge sampling 1.0 until
  their first roll-up reaches the birth certificate's probation n, then the tier's steady 1-in-N. A mis-stamped
  draft class is caught in its first runs; judge tokens go exactly where uncertainty is highest.
- *Mechanism landed same day: `factory.schema.json` (StampOrder + BirthCertificate — identity ops are memory;
  generations are roll-up cohorts), the `stamp_quota` dial (0013 §8 scale caps made mechanical), simulator
  `factory.py` (stamp · retire · judge_rate): 23/23 tests.*

### Locked 2026-07-02 (0012 close-out — consequence waits for humans)
- **Expiry = deny + signal.** A pending escalation past its wall-clock TTL is denied by default (re-staging
  needs fresh evidence), and the expiry is itself a vigil signal — an unattended queue is a finding about the
  org. Silence never approves; queues cannot rot into ambient authority.
- **Bars are absolute — no solo-org clamping.** Co-sign bars never bend to headcount: below quorum, the action
  is structurally unavailable (staging refuses, loudly), and the trust-tier gate must not admit tenants whose
  obligations require unavailable quorums — no regulated tier before a legal-process quorum exists. "No single
  employee is a god" is true from day one; staffing is a published launch gate.
- *Also structural, from the dive: gate policies cascade tighten-only like floors (co_signs rise, cooling_off
  lengthens, ttl shortens — never the reverse) · cooling-off is approved-but-held with a one-voice abort
  (three to destroy a universe, one to save it) · no break-glass exists, deliberately (the 2-bar was sized
  for 3 a.m.; a bypass would be the backdoor 0013 §6 forbids).*
- *Mechanism landed same day: `escalation.schema.json` (Escalation + GateRule), simulator `hitl.py`
  (EscalationQueue + cascade_gate): 27/27 tests.*

### Locked 2026-07-02 (0007 close-out — one fold, every law)
- **RunRecords pin their `context_hash`.** The ResolvedContext is content-addressed (same chain ⇒ same id —
  policy is cacheable, diffable, canary-able), and every run records which context it executed under: "what
  rules governed this agent when it did X" is a lookup, not an investigation. Memory records stay lighter —
  their governance is derivable from scope + time.
- **Partition: fail-closed continue + signal.** A node blind to its parent keeps enforcing its last-known
  resolved context (floors persist; rules are never absent), marks stale tiers honestly in `as_of`, and the
  blindness is a vigil signal that escalates with staleness (0012). Availability is never hostage to a blip;
  a wall-clock partition never freezes a simulated season.
- *Also structural, from the dive: merge laws travel with the field's contract (floor-tighten ·
  most-specific-wins-attributed · additive · monotone dials), so new cascaded dials never touch resolver code.*
- *Mechanism landed same day: `resolved-context.schema.json`, `run-record.context_hash`, simulator
  `resolver.py`: 32/32 tests (incl. reverse-declaration-order ⇒ identical hash).*

### Locked 2026-07-02 (0009 close-out — the design phase's last three)
- **Templates (#12): League · Second Brain · Company** — one per funnel stage (play / keep / buy). Game folds
  into League; Lab waits honestly behind the regulated tier, whose quorum (0012 — bars absolute) doesn't exist
  yet: a greyed-out template is the lock made visible.
- **Tone (#13): blank universes default REAL; templates override.** Wild is a visible choice, never an
  accident — and **the dial modulates rigor (signal capture, judge sampling, retention classes), never
  safety: platform floors are identical at both ends** (tested — a wild League and a REAL Second Brain
  resolve to equal floor sets).
- **Subscription (#14): fuel + hibernation + BYO-key.** Free = a one-time fuel allotment (worst-case cost per
  signup is a constant the operator sets — metered marketing, not a bleed). Out of fuel or idle ⇒
  **hibernate, never delete**: agents pause, the read-only window stays watchable — *your universe never
  dies; it dreams only when fueled.* Wake by subscription or bring-your-own model key (the hobbyist pays
  their own LLM bill and stays a zero-cost evangelist). Anonymous-tier caps bound every free universe: the
  safety architecture IS the free-tier economics.
- *Mechanism landed same day: `universe-template.schema.json`, simulator `provisioner.py` (provision ·
  hibernate · the three templates as validated data): 36/36 tests.*

### Locked 2026-07-01 (interop/UX pre-decisions — drive the 0008 dive)
- **Authoring is dual-mode, equal weight** — JB's call: English and canvas are both first-class surfaces.
  Tractable because of the next lock: both are *projections of one IR* — there is no text↔canvas sync
  problem, only two renderers of one artifact.
- **NLP authoring produces Orreth GraphSpec** — a governed, versionable, diffable intermediate representation,
  policy-checkable before anything runs. LangGraph is the first compile target (via AgentSurface); any SDK can
  be a target. Governance, canary, and the pane speak GraphSpec, never SDK internals.
- **Graph changes ship via the lane-routed Standards flow** — low-risk/high-confidence → auto-apply lane
  (signed, canaried, revertible); the rest → governed lane with a human gate. One mechanism, no new machinery.
- **v1 hero = the Field commander pane.** The **Universe spacetime window** is the declared north star —
  concept-designed in parallel (a live window assembled from operating state; likely the revolutionary
  screen), built once the field pane proves the design language.

### Locked 2026-07-01 (0000 close-out — the build gates)
- **Contracts: JSON Schema now → protobuf at Rust-time** (JSON Schema stays as documentation).
- **Simulator-first: yes** — a throwaway Python sim proves the contracts + three flows before Rust begins.
- **Domain: reserve now** — ✅ **done: `orreth.ai` registered 2026-07-01 by JB (AWS Route 53).** becky's
  did:web roots have a real anchor. Remaining: trademark glance; `orreth.com` optional defensive.
- **Dive order blessed**: 0002-amendments → **0008 (pane & GraphSpec, next)** → 0004 → 0005 → 0010 → 0011 →
  0012 → 0007 → 0009. (0000, 0001, 0003, 0006 closed.)

### Locked 2026-07-01 (0002 close-out, part 1)
- **Portfolio: auto-projection + per-entry owner opt-out**, governed by an anonymization Standard — defensible
  because the interview sandbox carries a query budget + noised aggregates.
- **Memory mobility: branch-bound by default.** Nothing follows an identity unless explicitly marked portable;
  skills travel by nature (they're cascaded Standards, not memory).
- **Escalation: serve-what-you-have + delegate the deeper-time remainder** — the L1→L2→L3 model, with
  cross-tier merge/dedup semantics owed by the 0002 amendments.
- *(Cross-agent collective reads confirmed as core design — an authorized agent reads ecosystem/universe
  records subject to visibility. The sibling question was distinct, and is locked below.)*

### Locked 2026-07-01 (0002 close-out, part 2)
- **Sibling walls: anonymized benchmarks only.** Sibling tenant-private memory is never readable raw by a
  sibling; governed, anonymized, aggregated projections (computed at the common parent) may flow. Raw
  whole-universe reads remain conductor + resident analysis agents (2 co-signs). *Collective reads up the
  ancestor chain remain a core, capability-gated right.*
- **Transfer: source veto, overridable by a common ancestor** as a governed, signed action. A team must
  release a player; the league can compel under its rules; every override is on the record.
- **Interview footprint: owner-visible, buyer-invisible.** Every interview writes a minimal signed access
  record the identity's owner can see; future buyers cannot — audit without market chill.

### Locked 2026-07-01 (0001 close-out)
- **One store.** Skills are typed views of promoted procedural memories — one `MemoryRecord` lineage;
  promotion is a state transition, never a copy; provenance never forks.
- **Rubric authority: workforce proposes, residents/humans ratify.** No agent grades its own yardstick.
- **`model_judge` cost: sample steady-state (1-in-N, a Tier Profile dial); full-grade every canary.**
  Promotion decisions never rest on a sample.
- **Scaffold portability: compatible-family tag + canary measurement; block only on hard-floor fail.**
  Soft drift is measured and arbitrated by the Objective Model, not guessed.

---

## ✅ Discharged 2026-07-01 — the six use-case requirements

Surfaced by the use cases (`../vision/use-cases.md`); discharged by `design/0002` (schemas) and now locked as
decisions: **identity lineage** (archetype → incarnation; shared skills, isolated memory) · **mobility**
(branch-bound by default; portable by explicit marking) · **cross-branch authorization** (collective reads up
the chain are capability-gated rights; sibling walls = anonymized benchmarks only) · **portfolio/interview**
(auto-projection + owner opt-out; query-budgeted sandbox; owner-visible footprint) · **retention/consent**
(governed tombstone; derived memories annotate, never rewrite) · **Sourced + Verified** (first-class,
including derived-memory chain verification).

## ✅ Open — **none. The ledger closed 2026-07-02.**

> Every question this ledger ever carried has been answered and locked by JB. The design phase (0000–0013)
> is complete; new questions belong to the build phase and will be logged here as they arise.

---

## 🔧 Build phase — decisions as they arise

### Locked 2026-07-23 (0039 — the Chronicle and the Canon: Phase 2's constitution)
- **Two books, one mind — the house names**: the Chronicle (JB's Purpose Data — the
  O·I·O·T ladder, DAG-hard, walkable forever) and the Canon (JB's Orreth Data —
  policies/prompts/skills/standards as forever-versioned assets); coupled in THE loop
  (Chronicle evidence → Canon proposals → human gates → the Canon governs the next
  Chronicle).
- **The charter IS the storage map**: Chronicle record classes carry allen's charter
  attributes (RTO · RPO · Criticality · DataClassification · retention min/max); in
  prod the IAC allocates stores per class — records retention as provisioned physics.
- **The metabolism hears usage**: recall-frequency joins 0005 scores as a distillation
  input; the dials (thresholds, windows, cadence) are Canon assets, Human and
  Agent+HITL editable, tuned on 0033's measured information loss.
- **Graduation requires the canary**: mentor crystallizes at the smart tier; the
  toolbox proves its rubric AT the mentee's tier under full observation before the
  cheap tier serves — 0010's never-silently-dumber, extended to lifecycles.
- **Memory, not RPC**: cross-field/eco sharing reads risen records at the common
  ancestor (provenance, trust, and score ride along); monitoring and future telemetry
  are Chronicle readers.
- **The pointer law**: bulk never enters the mind — the artifact-pointer class holds
  signed pointer+hash+metadata+lineage; mass rests in class-allocated stores.
- **The projection privacy floor**: profile & consent · testament & passage · purge
  stubs & key custody never enter a projection; dispatch/meter internals remain
  retrievable. The exclusion list itself lives in the Canon, human-gated.

### Locked 2026-07-22 (0038 — the Stacks: seven rows of the library — seed dialog + AskUserQuestion, all recommended)
- **Proving-ground-then-promote**: the seven RAG flavors compete on the record; winners
  join the librarian's planner, losers retire honorably. **Naive is the baseline control.**
- **One truth, seven projections**: ingestion once through the gateway; every field derives
  its index from the signed log; the purge's projection-eviction reaches all seven.
- **Graph rides a Postgres projection first** (0022 Shape A holds); dedicated graph infra
  must be EARNED by standings evidence and arrives via allen at JB's gate.
- **The Dispatcher**: an unembodied organ in the put/get path — after the gateway, never
  around it — routing by a versioned standard the librarian tends; the organ enforces,
  the resident learns; every choice a record.
- **Corpus: both** (dogfood + reference set) · **promotion = a named strategy in the
  routing standard** (code-landing = separate rule-9 gate) · **spoonful cut as proposed**.

### Locked 2026-07-22 (0037 — the Estate: allen, the cloud architect — AskUserQuestion, all on the recommended paths)
- **allen is an embodied tier: a universe-parented FIELD.** The provisioner gains the
  allowance (fields may parent directly off the universe); no decorative one-field eco.
  He joins becky and vigil as staff of the universe — control plane above, incarnation
  workforce below, master of cloud only.
- **Charter gaps route to the human seat** while specialist residents don't yet exist —
  prod never blocks; answers land as memory and are reused on later asks; every
  hand-answered gap is evidence for which resident to design next.
- **Plan-and-propose first.** Every Apply is human-fired at the gate. Graduating low
  blast-radius classes to auto-apply is a LATER, revisable lock — earned by record,
  never by declaration.
- **Co-sign classes: all four.** IAM changes · network topology · data-store
  delete/replace · cross-account stack sets — distinct-signer quorum (0012) on Apply.
- **Spend rides the lease token.** The dollar budget lives in
  `CapabilityToken.constraints.budget` — authority and allowance one artifact,
  attenuation-only, budget-miss ≡ authz-miss kept uniform.
- **Brownfield adoption is the acceptance gate.** The read-only walk (OrrethDemoStack +
  jsbarth-pipeline observed, attested, deployed-DAG rendered, templates registered as
  assets) must complete before greenfield Create unlocks.
- *Earlier in the same session (the seed):* charter-gap routing (above) and
  draft-now sequencing — 0037 drafted ahead of design 2 (the seven RAG variants),
  which becomes allen's first agent customer.

### Locked 2026-07-10 (the Universe Brain session — Fable closed the design pass, JB locked four)
*Vision capture: `../vision/the-universe-brain.md` (Memory · the Librarian · the Human · the
Orreth-Agent). Eleven parked questions closed by the design-owner pass (R1–R11 in the doc);
these four were JB-level and locked via AskUserQuestion:*

- **Librarian identity: one lineage, per-seat keys.** A Librarian root chained to the universe
  root, scope-bound did:key per seat, lineage proving sameness (becky's root→leaf pattern).
  Per-seat compromise containment and revocation; the self-dialog signs which seat asked and
  which answered.
- **Plan approval: severity-routed lanes.** The human's ask is HITL on the *intent*; the *plan*
  routes by marker severity — low auto-approves under a signed, canary-able gate policy;
  medium = resident co-review + notify; high/critical = human gate (0012 quorum per class).
- **Opt-out of exchange: future flow only.** Already-risen records stay; the apex's past never
  rewrites. True pull-back is a governed tombstone action, never a toggle. (Companion
  design-owner fix: composed answers over opted-out scopes are `derived-from-opted-out` —
  short-TTL, excluded from distillation — so opt-out can't be defeated by asking.)
- **Purge: the split model.** Personal-data purge rides consent machinery (solo-capable).
  Operational poison purge = 2 co-signs + cooling-off, bars absolute — a solo universe can
  quarantine instantly and forever but destroys only when quorum exists. Containment is never
  blocked; destruction waits for humans, plural. The purge walk crosses the promotion boundary
  (skills/distillations/profile claims revert or re-anchor — R10).

### Landed 2026-07-10 (covenant rule 9 — the TierProfile `exchange` block)
- **contracts/v0/tier-profile.schema.json gains the optional `exchange` dial** (per-class
  `up`/`hold`), specified verbatim in `design/0023 §4` which JB read and blessed the same
  day ("Dive looks right — give the Librarian her seats") — the blessing is the rule-9
  approval trail. Backward compatible (optional property); enforced in the reference
  simulator (hold distills home, never rides up); wire steward + Console toggles on the
  build ledger.

### Locked 2026-07-10 (covenant rule 9 — orreth-store, the governed delete's census)
- **Orphan-sweep scope approved by JB** (AskUserQuestion): `orreth-store` gains a read-only
  `list_bodies(scope_root)` census; deletion uses the crate's existing `delete_body` (built
  2026-07-02 as the tombstone's storage-layer twin). The sweep erases ONLY bodies no live
  record references, is **opt-in per node** (`--sweep-orphans`) because a shared bucket
  would make another tier's bodies look like orphans, and is enabled on the dev rig's
  per-container volumes. Expired drop-class bodies + the tombstone-stub read path land
  with the Purge dive (spoonful 5), where they belong.

### Locked 2026-07-12 (0030 — The Human's Seat; JB's interoperability session, in his words)
- **The ladder is canon: Objective · Intention · Observation · Thought.** Humans are
  the ONLY origin of Objectives; residents originate Intentions inside approved
  plans; workforce originates Observations; minds originate Thoughts. Tiered like
  the real world; each rung reviews the rung below.
- **The plan gate**: an Objective is curated into a plan and **HITL-approved before
  any intention fans**. V0: origin plans always wait for their human.
- **An Objective is an artifact of artifacts** — everything done, made, decisioned,
  discovered — with live status and a full report recallable forever (30 days later
  is one click, because it was never anything but signed records).
- **The glass is the human's seat**: every surface renders FROM the human's place
  and says so; humans don't multithread and never should have to.
- **The data scheme (OIOT indexing) is JB's — held, no action** until he reveals
  and locks it; contracts/record-shape changes are a rule-9 approval moment.
- **Standing rule**: every spoonful is proven as a human in the glass (browser
  walk) before it is called done. Curl proofs are no longer the finish line.

### Locked 2026-07-11 (0029 — Multimodal Capability, AskUserQuestion)
- **Upload bars, v0**: 256KB · txt/md/json/csv/pdf/png/jpg — oversized or foreign
  types get the uniform refusal. Bars are floor policy and may loosen later.
- **Dark formats: admit + park.** An artifact needing an eye lands signed and
  honestly dark, and the Librarian parks an extraction intent (0014 — failure is
  fuel): when a vision mind saddles on the Stable, the parked list IS the retry
  list. The universe keeps what you hand it and remembers it owes you the reading.
- **The keyless floor ships now; the eye saddles at JB's gate.** Deterministic
  extraction for text-bearing formats this spoonful; a real vision/OCR mind is
  JB's staging act through ada (0019), on his spend, whenever he chooses.

### Locked 2026-07-11 (0028 — Workspaces & the Improvement Engine, AskUserQuestion)
- **All four embodied residents get workspaces** (librarian, becky, charlotte, ada) —
  the card declares the room, the glass renders four typed panel kinds blind, and the
  room is fetched via the parlor queue like any ask (never a privileged path).
- **Improvement lanes grade by kind, and the improver never grades itself**: a
  parameter nudge (cycles, rungs, thresholds) grades **medium** — co-review + notify,
  adopted with a loud record; a persona/prompt/shape rewrite grades **high** — it
  waits for the human. The change kind is COMPUTED by diffing versions (the governance
  seat authors the grade), never declared by the proposer.
- **One improver stands on the universe floor** — a single standing incarnation
  (R8/0027 machinery) reading the subtree's risen evidence; one open proposal per
  asset, no proposal storms.

### Locked 2026-07-11 (0027 — the Fingertip, AskUserQuestion)
- **The human's request IS the top node.** A human-submitted objective rides the request
  queue; the assembled outcome resolves that request, and the human reading it is the
  completion confirmation. No orchestration incarnation ever confirms its own completion
  — nothing grades its own yardstick, at the top least of all (0005).
- **Cross-ecosystem dispatch-miss: refuse AND ask.** A dispatch whose becky-chained
  authority does not cover the target is refused uniformly (a prober learns nothing,
  0002 §4) — and the orchestration stages a human-visible entitlement ask in the
  target's queue. The branch parks until granted or expired; silence is denial
  (locked 2026-07-02). The flow degrades honestly instead of dying.
- **The first standing incarnation is the portfolio monitor** on the universe floor
  (R8's immortal job, beating like an organ): it reviews the floors' rollups each
  beat-window and writes observation memories. Its factory-RL duty waits for
  spoonful 7 (0011's improvement engine), where the boundary with vigil gets designed.

### Locked 2026-07-10 (0022 — the Memory Construct close-out)
- **The bytes-local posture: local-only by default.** Embeddings and reranking run
  in-process on each node (local ONNX models, honest zeros on the steward's meter);
  **record bytes never leave the node for indexing.** Hosted embedding/rerank APIs are an
  explicit, per-universe, flagged opt-out that changes the universe's published privacy
  posture. Discharges the embedding-source question pre-staged 2026-07-08. The dive's
  design-owner closures (log-is-truth/index-is-projection · Shape A one-service-per-node
  with named escape hatches · hybrid weighted-RRF in SQL + trust-weighted rerank ·
  crypto-shred with mandatory projection eviction · Iroh push-up sync w/ JetStream
  fallback · bi-temporal close-the-window) stand as `design/0022` §10.

### Locked 2026-07-08 (pgvector — Fable staged the options, JB locked)
- **Prep now, design dive later.** The compose pg image moves `postgres:16` →
  `pgvector/pgvector:pg16` (same postgres, the `vector` extension present but dormant;
  the `pg-data` volume carries over untouched). Semantic retrieval itself waits for a
  **0002-amendment dive** — a new query shape deserves the contract pass: fidelity,
  remainder honesty, and the uniform refusal on the new path. **Open inside that dive:**
  the embedding source — local model (free, keyless, bodies never leave the rig; weaker)
  vs API embeddings (stronger; but record bodies would leave the plane to a third party —
  a privacy-posture change needing its own explicit lock) — and which organ's DID the
  embedding cost rides on the meter. **Mechanism (image swap) landed 2026-07-08.**

### Locked 2026-07-07 (the join door — Fable staged the options, JB locked)
- **Join-door hardening: HITL gate + nonce challenge.** Joins stage in the human queue
  like plants and saddles (0012 — consequence waits); becky additionally challenges the
  joiner to sign a nonce, proving key control before the request stages, so roster
  names bind to proven keys. Demos show the gate (the narrated reel auto-approves,
  visibly). Flagged at the 0017 review ("the join door is open"); the accepted-risk
  era ends with this lock. If the mechanism turns out to need a `contracts/v0` change,
  work stops and returns to JB — the sacred zone stays sacred. **Mechanism landed
  2026-07-07, same day** (`orreth_sim/joindoor.py` + worker + SDK + Console gate;
  `contracts/v0` untouched — the Sig shape and lease token were already enough).
  Residual, documented: queue statuses stay unsigned until 0012's signer registry.

### Locked 2026-07-02 (object store — JB asked, Fable advised, JB accepted)
- **The object-store contract is the S3 API; the backend is config, not architecture.** Rust plane uses the
  `object_store` crate (one trait: S3 · GCS · Azure · local FS · in-memory). Hosted default = **AWS S3**
  (content-addressed immutable bodies at `bodies/<universe>/<hash>`; SSE-KMS with the per-universe key for the
  platform-managed tier, client-side envelope encryption for BYOK/split — the blind tiers stay blind at the
  storage layer; lifecycle policies = the pruning metabolism's physical twin, and a hibernated universe is
  pennies of cold storage). Dev/self-host = **MinIO** in compose (per 0000 §7) or local FS; air-gap = any
  S3-compatible. **Cloudflare R2 (zero egress, S3-compatible) noted as a launch-time cost swap** for the
  read-heavy public window — a config decision to make with real traffic numbers.

### ✅ Trust & safety (`0013`) — nothing open
21. ~~The Warden's name~~ — **christened `vigil` by JB, 2026-07-02.** 0013 has no remaining open items.

### ✅ Carried from `design/0001` — discharged
7. ~~Confidence statistic~~ — **locked 2026-07-02 in the 0005 close-out: Bayesian posterior** (see above).

### ✅ Product / GTM ("Build My First Universe") — discharged in the 0009 close-out
12. ~~Universe templates~~ — **League · Second Brain · Company, locked 2026-07-02.**
13. ~~Wild vs REAL~~ — **default REAL, templates override; rigor never safety, locked 2026-07-02.**
14. ~~Provisioning / subscription~~ — **fuel + hibernation + BYO-key, locked 2026-07-02.**

### ✅ Governance / human oversight — locked 2026-07-01
15. **Human entitlement model locked:** down/within by default; up and across by explicit, logged grant;
    read-entitlement and control-entitlement never conflate.
16. **Multi-party apex authorization locked (via 0006):** 2 human co-signs for universe-wide raw reads,
    cross-tenant grants, and erasure; **3** for trust-root rotation.

---

## ADR convention (for individual decisions once we start logging them)

`NNNN-short-title.md` with: **Context · Decision · Consequences · Status (proposed / accepted / superseded)**.
