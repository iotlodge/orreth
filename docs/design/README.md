# Design — the build-phase specs

The vision (`../vision/FUTURE-the-orreth.md`) is the *what* and the *why*. This folder is the *how* —
turned into buildable specs, one keystone at a time. Each doc is design-phase: schemas, contracts,
rationale, and open decisions. **No implementation code lives here** — that arrives only after a spec is blessed.

**Rebaselined 2026-06-30 — memory-first.** The center is the *memory substrate for living identities*; governance is its
first application. The dives below are re-ordered around that center. The 6 use-case-derived requirements
(`../decisions/README.md` → Open) are hard inputs to the substrate keystone.

## The dive sequence

Ordered by leverage — each unlocks the next.

| # | Spec | Why it's a keystone | Status |
|---|---|---|---|
| **0000** | [Structure & Interoperability — the frame](0000-structure-and-interoperability.md) | One node (`orrethd`), tier = profile, layered deployment; contracts as the product; Rust/Python/TS split ("lift the contract, port the engine"); Field is native Orreth (CO = reference proof, optional adapter); dev compose topology; discharges the 2026-07-01 review findings; proposes re-sequencing + reserved dives 0010–0012 (AgentField/Gateways · Factories · HITL). | 🟡 draft for review |
| **0001** | [Promoted Memory & Skill Standard + acceptance rubric](0001-promoted-memory-and-skill-standard.md) | The `MemoryRecord` atom + skills as promoted memories + the rubric. **Reframed:** memory is the substrate; skills/governance are what it powers. | 🟡 draft for review |
| **0002** | [**Living Identity + Retrieval — the substrate keystone**](0002-living-identity-and-retrieval.md) | Identity as universe-unique key; **memory keyed to identity**; the space×time **retrieval contract** (time-budget escalation, Sourced + Verified). Discharges all 6 requirements: **archetype→incarnation**, **memory portability scope**, **cross-tenant retrieval authz**, **showcase/portfolio scope**, **retention/consent**, **Sourced+Verified audit**. **All §8 decisions locked 2026-07-01**; amendments **landed** 2026-07-01: ScopePath-relative addressing, merge semantics, budget-miss ≡ authz-miss, interview query budget. | 🟡 draft for review |
| **0003** | [Pruning Policy — the metabolism](0003-pruning-policy.md) | What each layer keeps vs distills vs tombstones; how "years" stays affordable. **Locked in:** hybrid floors+steward, apex = distilled + signed pointers, tombstones annotate. Distillation record makes provenance survive compression. | 🟡 draft for review |
| **0004** | [Tier Profile & the Two Clocks](0004-tier-profile-and-the-two-clocks.md) | The dials that make a tier — refines the `contracts/v0` head start. **Centerpiece: the two-clock model** (surfaced by The League): *meaning runs on universe-time; security and money run on wall-clock* — declared, monotonic universe-time with high-water enforcement (memory-backdating becomes structurally detectable) + **lived vs ingested-archive** provenance. Adds the owed **objective vector**, retention as **min *and* max** per record class (SOX keep-at-least vs GDPR keep-at-most; legal hold = governed `min: ∞`), profiles as tighten-only cascade artifacts, and the three proving-ground profiles as worked examples. **All §7 decisions locked 2026-07-02**; schema deltas landed (UniverseTime/WallClock, occurred_at/received_at, provenance_class, TierProfile clock/objective/retention_classes); simulator enforces the high-water rule — 12/12 tests. | 🟡 draft for review |
| **0005** | [Run Record & the Monoidal Roll-up](0005-run-record-and-monoidal-rollup.md) | The aggregatable envelope + the monoid that composes it up the tree — standings, quarter-closes, AgentFacts, and benchmarks are one mechanism; raw runs never travel, signed pointers do. **Confidence = Bayesian posterior** (mean + 95% CI + n; per-tier prior applied once at the report edge) — discharges open #7. **Floors flag, never average away** (a 0.98 agent with one breach shows both truths). Portfolio shows **mean + interval + n**. Buckets are universe-time (0004). Contract + simulator landed; **all decisions locked 2026-07-02**; 17/17 tests. | 🟡 draft for review |
| **0006** | [becky — identity & capability chain](0006-becky-identity-and-capability-chain.md) | DID delegation root→leaf (**locked:** did:web roots + did:key leaves); resident (TCB) vs registered (workforce); archetype→incarnation issuance; attenuation-only CapabilityTokens; revocation kill-switch; AgentFacts. **Pulled forward** — 0002's authz assumes it. | 🟡 draft for review |
| 0007 | The cascade resolver | How Resolved Context is composed from the inherited chain — deterministic, fast (Rust). | ⏳ |
| **0008** | [The pane & graph engineering (interop/UX)](0008-pane-and-graph-engineering.md) | The Field commander pane (v1 hero, six regions) + dual-mode authoring (English ↔ canvas, both projections of **GraphSpec v0**, sentence↔node bijection, never-guess-silently) + lane-routed change flow. Recursive pane = same components, ScopePath-parametrized. **Spacetime window concept art shipped** (`../vision/Orreth-spacetime-window-concept`). | 🟡 draft for review |
| 0009 | "Build My First Universe" — templates · marketplace · interview | Tier-Profile templates; the agent **interview** (showcase scope); "wild vs REAL is a policy dial"; self-serve provisioning. | ⏳ |
| **0013** | [The Custodian Tier & Responsible-Universe Architecture](0013-custodian-tier-and-responsible-universes.md) | The dual-use reckoning, made structural. Custodian = apex-above-apex (freeze-not-read) · platform floors (meta-cascade, asymmetric change bars) · **vigil**, the Warden resident organ (**detection, not enforcement**; dead-man heartbeat as floor term) · graded quarantine w/ **HITL placement map** · key custody as the fork · governed telemetry (published contract + tenant mirror) · trust-tiered onboarding · abuse taxonomy · **proving grounds** (The League = time axis, playable · Earth Mapper = space axis, dogfooded first tenant · Agentic Enterprise northstar in parallel; funnel **Watch → Play → Build → Buy**). **Provenance corrected 2026-07-02:** both 2026-07-01 passes were Opus 4.8 (the second mislabeled itself "Fable 5" after a silent model fallback — caught via the signed session audit log, the doc's own attribution thesis in action); genuinely reviewed & amended by **Fable 5** 2026-07-02. All §12 decisions JB-locked. Amends `0000`. | 🟡 draft for review |

## How we work a dive

1. Draft the spec here (schema + rationale + **open decisions** flagged explicitly).
2. JB reacts / pushes back on the open decisions (vision-owner's call).
3. Lock the decisions → record them in `../decisions/`.
4. Only then does code get written against the blessed spec.
