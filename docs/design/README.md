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
| **0002** | [**Living Identity + Retrieval — the substrate keystone**](0002-living-identity-and-retrieval.md) | Identity as universe-unique key; **memory keyed to identity**; the space×time **retrieval contract** (time-budget escalation, Sourced + Verified). Discharges all 6 requirements: **archetype→incarnation**, **memory portability scope**, **cross-tenant retrieval authz**, **showcase/portfolio scope**, **retention/consent**, **Sourced+Verified audit**. **All §8 decisions locked 2026-07-01**; amendments owed: ScopePath-relative addressing, merge semantics, budget-miss ≡ authz-miss. | 🟡 draft for review |
| **0003** | [Pruning Policy — the metabolism](0003-pruning-policy.md) | What each layer keeps vs distills vs tombstones; how "years" stays affordable. **Locked in:** hybrid floors+steward, apex = distilled + signed pointers, tombstones annotate. Distillation record makes provenance survive compression. | 🟡 draft for review |
| 0004 | Tier Profile | What memory + objective vector + **time-budget** mean at each of the 3 tiers. | ⏳ |
| 0005 | Run Record & monoidal roll-up | The aggregatable envelope; how scoring/confidence/cost/tokens compose up the tree. | ⏳ |
| **0006** | [becky — identity & capability chain](0006-becky-identity-and-capability-chain.md) | DID delegation root→leaf (**locked:** did:web roots + did:key leaves); resident (TCB) vs registered (workforce); archetype→incarnation issuance; attenuation-only CapabilityTokens; revocation kill-switch; AgentFacts. **Pulled forward** — 0002's authz assumes it. | 🟡 draft for review |
| 0007 | The cascade resolver | How Resolved Context is composed from the inherited chain — deterministic, fast (Rust). | ⏳ |
| 0008 | The pane & graph engineering (interop/UX) | **Pulled forward — next dive.** The Field commander pane (v1 hero) + dual-mode authoring (English ↔ canvas, both projections of **GraphSpec**) + lane-routed change flow. The recursive pane generalizes upward; the **spacetime window** is the declared north star, concept-designed in parallel. | ⏳ next |
| 0009 | "Build My First Universe" — templates · marketplace · interview | Tier-Profile templates; the agent **interview** (showcase scope); "wild vs REAL is a policy dial"; self-serve provisioning. | ⏳ |

## How we work a dive

1. Draft the spec here (schema + rationale + **open decisions** flagged explicitly).
2. JB reacts / pushes back on the open decisions (vision-owner's call).
3. Lock the decisions → record them in `../decisions/`.
4. Only then does code get written against the blessed spec.
