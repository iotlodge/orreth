# Seed — Embedded Graded Learning (the third loop)

**Status: SEED (JB, 2026-09-16) — deep dive proposed after Phase 3.**
JB's idea, captured with Fable's first mapping onto the locked canon.
No build until the dive.

## JB's idea, faithfully

- Agents — residents AND installed agents — leverage their own
  **near-live graded feedback**: a **decoupled grader flow** applies
  thumb up/down WITH feedback to their work, and that graded feedback is
  **exposed back to the agent** (a skill lookup, a feedback topic or
  subscription) — "a new way of third-level reinforced learning we could
  apply to every agent in Active Orreth."
- Direction refinement captured: the heavy capability integration
  changes — **installed agents will look and work much the same way
  residents do; their MUTABILITY is what changes.**
- **The guardrail law (JB's own):** never raw human feedback — "that
  would open an attack vector and could override governance." An
  **embedded agentic grader** provides the feedback that reaches the
  agent directly.
- Likely doesn't apply to sub-agents — **but does apply to the agents
  that create them** (the creators absorb the lessons).
- "A wicked demo of the embedded feature would be neat."

## Fable's mapping (why the substrate makes this nearly free)

- **The grader is an events-rail consumer** — decoupled by construction.
  It reads reply/outcome events, grades against its rubric, and commits
  **verdict records** through the outbox like any other fact.
- **The grader is an IDENTITY** — own DID, own policy, metered, assigned
  to agents through Controls like a guardrail. Verdicts are signed by the
  grader, never the graded: covenant rule 2 ("nothing grades its own
  yardstick") generalized into a living organ.
- **Lessons are a digest family (0003).** Consolidation distills an
  agent's verdicts into a per-agent "lessons digest," packed at context
  assembly — the "skill lookup" is simply recall. Near-live = events-rail
  latency (seconds).
- **The two-speed loop keeps it governable:**
  - *Fast lane:* lessons ride the context pack — ephemeral, rebuildable,
    visible, and instantly revocable (unassign the grader, the lessons
    stop packing).
  - *Slow lane:* a lesson that deserves permanence (a persona/prompt/
    template change) goes through the **craft gate as a versioned edit
    and must pass the A/B harness before promotion** — the "learned
    behavior is never silent" law (0003) already binds this.
- **The three levels, named:** L1 = in-graph self-critique (the critic
  include) · L2 = the scheduled A/B harness (template-level, offline) ·
  **L3 = this: near-live graded experience folded into working
  knowledge** — reinforcement through context, not weights.

## The attack-vector answer (sharpening JB's concern)

1. **Provenance or nothing:** an agent ingests only verdicts signed by
   graders it is ASSIGNED. Unsigned or unassigned feedback never packs.
2. **Lessons shape style and strategy, NEVER authority:** they enter the
   context lane only; gates, capabilities, and policies never read them
   — structurally, a lesson cannot widen a permission.
3. **Human thumbs route THROUGH the grader,** as evidence it weighs
   under its own rubric and rate limits — never raw-piped to the agent.
   (The 0048 thumbs survive; their teeth get governed.)
4. **Grade the grader:** golden-set checks distinguish "the agent got
   worse" from "the grader got weird"; a verdict flood on one agent is
   an incident (blast-radius thinking applied to opinion).

## The creator's loop (JB's "hummmmm", amplified)

Sub-agents are ephemeral and carry no lessons — but their CREATOR
absorbs the graded outcomes of everything it spawns. Applied to the
factories: MITL's templates improve from field grades, each improvement
a versioned, harness-proven sibling. The self-delivery road grows a
learning gradient.

## The demo (banked)

A resident answers; the grader's verdict lands on the feed seconds
later; the next answer is visibly better AND says why ("feedback taught
me…"); the Playwright captures before/after for the carousel — the
embedded experience that always helps to improve, watchable.
