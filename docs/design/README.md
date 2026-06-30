# Design — the build-phase specs

The vision (`../vision/FUTURE-the-orreth.md`) is the *what* and the *why*. This folder is the *how* —
turned into buildable specs, one keystone at a time. Each doc is design-phase: schemas, contracts,
rationale, and open decisions. **No implementation code lives here** — that arrives only after a spec is blessed.

## The dive sequence

Ordered by leverage — each unlocks the next.

| # | Spec | Why it's the keystone | Status |
|---|---|---|---|
| **0001** | [Promoted Memory & Skill Standard + acceptance rubric](0001-promoted-memory-and-skill-standard.md) | Skills *are* promoted memories — one schema is the keystone for **both** reproducibility (teacher→skill→fleet) and the memory fabric. The genuinely new primitive. | 🟡 draft for review |
| 0002 | Tier Profile | What a Run Record + objective vector means at each of the 3 tiers (Universe / Ecosystem / Field). | ⏳ next |
| 0003 | The cascade resolver | How Resolved Context is composed from the inherited chain — deterministic, fast (Rust). | ⏳ |
| 0004 | Run Record & monoidal roll-up | The aggregatable observation envelope; how scoring/confidence/cost/tokens compose up the tree. | ⏳ |
| 0005 | Identity & capability chain | becky → DID delegation across tiers; resident (TCB) vs registered (workforce) agents. | ⏳ |
| 0006 | The recursive pane | The zoomable single-pane (Universe → Ecosystem → Field → Agent), role-scoped. | ⏳ |

## How we work a dive

1. Draft the spec here (schema + rationale + **open decisions** flagged explicitly).
2. JB reacts / pushes back on the open decisions (vision-owner's call).
3. Lock the decisions → record them in `../decisions/`.
4. Only then does code get written against the blessed spec.
