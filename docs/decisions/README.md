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

### Trust & safety (design draft `0013`, 2026-07-01 — direction set, decisions open below)
- **The Custodian tier.** Hosted orreth.ai is a Harness one tier above every customer Universe, with
  **deliberately asymmetric powers**: it can *freeze* (quarantine) and *enforce platform floors*, but is
  **structurally blinded to tenant content**. The landlord can change the locks; it cannot read the mail.
  The safety architecture is Orreth recursed onto its own operator, and the Custodian is governed *harder*
  than any tenant (multi-party co-sign, fully audited — the watchers of the watchers are watched).
- **Platform floors (the meta-cascade)** — the most foundational, non-overridable rules cascade into every
  Universe and no Universe GOD can loosen them: no targeting non-consenting real people · illegal-content
  prohibition · PII/regulated-data consent · autonomy ceilings by trust tier · non-optional attribution.
- **Security Agent** — a resident (TCB) organ at every layer: tenant-serving within the customer's authority,
  **content-blind (behavioral/metadata only) to the platform**. Safety and reliability are the same instrument.
- **Quarantine** — one mechanism, three postures: commercial (reversible freeze, data retained) · abuse
  (freeze + preserve + multi-party review) · lawful process (freeze + preserve, disclose only what we hold).
  Freezes, never deletes; un-quarantine as gated as quarantine; no secret freezes.
- **Self-hosting has no Custodian** — the operator is it; our safety story is strongest for the hosted service.

### Locked 2026-07-01 (0013 close-out)
- **Key custody: split-key freeze-not-read.** Customer holds the read key; Custodian holds only a freeze key —
  "cannot read" is a mathematical fact. *Owed: customer-side lost-key recovery story (enterprise tier).*
- **Custodian read stance: structurally blinded** (public commitment) — floor enforcement behavioral-only;
  the readable-content capability does not exist to be subpoenaed, breached, or coerced.
- **Creation gate: invite-only now → trust-tiered later** (anonymous-sandbox / KYC-verified / regulated-high-
  assurance; dangerous powers unlock with verification).
- **First POC: Earth Mapper first** (safe showcase), **Agentic Enterprise designed in parallel** (northstar
  where governance is the product; forces the Custodian + audit build).
- *Honest limits on record: self-hosting escapes the Custodian; content-moderation + lawful-process + data law
  need real T&S and legal counsel (Fable is not a lawyer); attribution proves chain-of-custody, not right-to-hold.*
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

## 🟡 Open — remaining

### Open (carried from `design/0001`)
7. **Confidence statistic** — exact model *(lean: defer to the Run Record dive, `0005`)*

### Open (product / GTM — "Build My First Universe")
12. **Universe templates** = a Tier Profile + starter bundle (Standards, skill archetypes, agent-template roster,
    retention config, policy floors). What's in the first templates (Company / League / Game / Lab / Second Brain)?
13. **"Wild vs REAL is a policy dial."** Which policy floors define the tone spectrum, and what's the safe default?
14. **Provisioning / subscription** — self-serve spin-up of a Universe from a template.

### ✅ Governance / human oversight — locked 2026-07-01
15. **Human entitlement model locked:** down/within by default; up and across by explicit, logged grant;
    read-entitlement and control-entitlement never conflate.
16. **Multi-party apex authorization locked (via 0006):** 2 human co-signs for universe-wide raw reads,
    cross-tenant grants, and erasure; **3** for trust-root rotation.

---

## ADR convention (for individual decisions once we start logging them)

`NNNN-short-title.md` with: **Context · Decision · Consequences · Status (proposed / accepted / superseded)**.
