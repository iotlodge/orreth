# Design — the constitution (0000–0017) and the standing registers

<!-- PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — rearch row 4, re-base sp2: the design road re-based on the new world · 2026-09-29 -->

The vision (`../vision/FUTURE-the-orreth.md`) is the *what* and the *why*. The fourteen
design dives `0000`–`0013` plus `0014`–`0017` are the **constitution** the covenant
(`.claude/skills/orreth-covenant/SKILL.md`) enforces: identity that survives the process,
canonical bytes, the capability chain, uniform refusal, the two clocks, the cascade of
policy, the run record, HITL gates, the custodian tier, the knowledge loop, the chassis, the
model plane, the lifeforce agents. They are design-phase documents — schemas, contracts,
rationale, locked decisions — and they still bind.

**Where the build lives now.** The new world's canon is `../rearch/0001`–`0009` (the
experience charter · transport · memory · agent · the build plan · markers · intent · the
Rust plane and the port · the old world carried). The build plan (`../rearch/0005`) is the
one road; a spoonful is planned, built, proven and walked there. **The honest boundary**
(`the-honest-boundary.md`) is the standing register of what is proven, partial or parked,
with the evidence named — a claim not on that page is a claim we do not make.

**Where the old world lives.** The dive docs `0018`–`0073` (the Tool Farm through the
Whole Journey Judged), their decisions, the sim in `backend/conformance`, the old `orrethd`
crate and the 0.72 rig are kept whole — never deleted, never force-moved — at the tag
`main-v0.72-old-world` and the branch `old-world/main-v0.72`. `../rearch/0009` is the
ledger of what each old organ became on the new kernel (carried · re-seated · capability ·
parked · dropped). A stranger learns Orreth from the book (docs.orreth.ai), rewritten for
the new world at the release wave; never from a dive doc.

## The constitution

| # | Dive | What it locks |
|---|---|---|
| **0000** | [Structure and interoperability](0000-structure-and-interoperability.md) | The shape: universe → ecosystem → field → agent; canonical bytes as the contract (§3); the plane and the cognition side |
| **0001** | [Promoted memory and the skill standard](0001-promoted-memory-and-skill-standard.md) | Memory rises by promotion; skills are crystallized memory |
| **0002** | [Living identity and retrieval](0002-living-identity-and-retrieval.md) | A keypair is a self; retrieval escalates by time-horizon; refusal wears one face (§4) |
| **0003** | [Pruning policy](0003-pruning-policy.md) | Floors classify what is kept raw and what distills |
| **0004** | [Tier profile and the two clocks](0004-tier-profile-and-the-two-clocks.md) | Occurred vs received; lived time is monotone |
| **0005** | [Run record and the monoidal rollup](0005-run-record-and-monoidal-rollup.md) | Nothing grades its own yardstick; the stat bundle merges up |
| **0006** | [becky, identity and the capability chain](0006-becky-identity-and-capability-chain.md) | Joining is governed; leases chain to a pinned root; scopes only narrow |
| **0007** | [The cascade resolver](0007-cascade-resolver.md) | Policy cascades down, floors never loosen, the resolved context is content-addressed |
| **0008** | [Pane and graph engineering](0008-pane-and-graph-engineering.md) | The first glass (superseded by the Bridge and THE PANEL, `../rearch/0001`) |
| **0009** | [Build my first universe](0009-build-my-first-universe.md) | The first world from three small files |
| **0010** | [AgentField and gateways](0010-agentfield-and-gateways.md) | Agents as identities behind gateways |
| **0011** | [Factories](0011-factories.md) | Worlds stamped from templates |
| **0012** | [HITL gates, queues and co-sign](0012-hitl-gates-queues-and-cosign.md) | A consequence waits for a human; the queue is visible |
| **0013** | [Custodian tier and responsible universes](0013-custodian-tier-and-responsible-universes.md) | Hosted custody; federation's handshake (parked) |
| **0014** | [The knowledge loop](0014-the-knowledge-loop.md) | Sources as identities; knowledge versioned by universe-time |
| **0015** | [Orreth.agent, the chassis](0015-orreth-agent-the-chassis.md) | One governed loop; behavior as a profile |
| **0016** | [The model plane](0016-the-model-plane.md) | The plane authorizes and meters; it never sees the prompt |
| **0017** | [The lifeforce agents](0017-the-lifeforce-agents.md) | Agents that persist and re-join as the same self |

## The registers

- [`the-honest-boundary.md`](the-honest-boundary.md) — proven · partial · parked, evidence named.
- `../decisions/` — the ADRs (`0001` the proofs era) and the locked-decision ledger.
- `../rearch/0009` — the old world carried: every old organ's seat on the new kernel.

## How we work a spoonful (the standing rhythm)

1. The build plan (`../rearch/0005`) names the spoonful: scope at open, review at close.
2. Fable builds it on both kernels (the Python reference and the Rust kernel), the
   conformance fixture grows with every wire change (`../rearch/0008`).
3. JB walks it in the glass; the friction register keeps every wound; a performance or
   experience wound stops the line.
4. The closing commit updates canon `0005`, the honest boundary, the conformance README
   and `agents/PROVENANCE.md` — in the same commit, never later.
5. `VERSION` wears the world's era; the glass whispers it.
