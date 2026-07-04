# Orreth.agent — the Chassis
### One agent architecture, forever: behavior as a profile

*Private vision artifact. Captured 2026-07-03 from JB's Topic-2 dialog (the operating state).
Companion to `the-knowledge-loop.md`. Queues the build-phase dive **0015 — Orreth.agent, the
chassis**. The founding move applied to cognition: orrethd is one binary where tier is a
profile; Orreth.agent is one chassis where **behavior is a profile — Policy, Prompts, Skills,
Persona — and the architecture never changes.***

---

## The chassis (the reusable workflow)

A fixed, compiled loop — authored as **GraphSpec** (0008; LangGraph the first compile target,
per the locked interop decision), executing through the **AgentSurface** (0010):

**prepare** (analyze / check / improve the human-or-agent request against its *intent*) →
**plan** → fan out to the **adaptive process nucleus** — the nucleus *holds the plan* but
executes through **parallel observations**, each shaped by the skill applied at that node →
results feed back → **reflect · audit · critic** (0001's judge machinery) → **replan** →
the nucleus makes *only the observations the replanner asked for* → rinse and repeat until
**objective met or circuit breaker** (the degrade-loudly posture).

Properties that fall out:

- **Behavior is governed data.** An unchanging chassis means everything that varies — prompts,
  skills, personas, policies — is versioned, cascadeable, diffable content riding the
  lane-routed change flow: canaried, revertible, auditable. *"Why did the agent act differently
  Tuesday?" is a diff, not an investigation.*
- **Least-privilege attention.** The nucleus cannot wander: observations are scoped by the
  replanner, budgeted by the lease, logged as RunRecords. The agent's thinking is on the record,
  scored.
- **Dual heritage per Topic-2's correction:** Orreth.agent is *becky-shaped* — **agent and
  infrastructure at once**. Deterministic retrieval when an agent asks; LLM synthesis when a
  human asks; the core optimizing between modes by context.

## The parking lot — failure is fuel

Breaker trips or feedback is bad → the unsolved objective is **parked in memory** → and becomes
an **intent handed to knowledge acquisition** (Topic 1's loop): a research assignment, not an
error log. Knowledge category built → skill improved → parked problem retried. The universe
converts defeats into curriculum.

## Master + swarm — asymptotic replication with a measured gap

One expensive Master + 100–1000 cheap executors: the Master's judgment distills into skills the
swarm runs at commodity cost. **Honest calibration (and the stronger claim):** convergence is
asymptotic, not perfect — novelty still needs the expensive mind — but in this machinery *the
gap is measured continuously* (judge sampling, full-grade canaries, Bayesian confidence per
skill). The Master matures into **teacher and auditor**: it grades canaries, takes the
escalations the model-tier pins demand, and its expertise amortizes into assets. Not "the cheap
agents became the Master" — *"the Master's judgment became an asset, and we know its current
fidelity."*

## Persona — the costume, never the thread

Persona is a **soft standard** (most-specific-wins, like the tone dial) layered on the fixed
chassis and the immortal identity: it can evolve without breaking the biography. Humans play
with personalities in wild universes; professionals compose temperaments into enterprise teams
(the meticulous-skeptic reviewer, the bold-first-drafter designer). Same chassis, same
governance, different costume — wild and REAL, again.

## The operating state — two loops, two clocks

The **Orreth.agent loop** (plan → observe → reflect → replan; seconds-to-minutes) spins inside
the **Universe loop** (record → score → distill → crystallize → cascade; days-to-seasons).
The inner loop optimizes the task. The outer loop optimizes the optimizer. That is the operating
state of a self-correcting Agentic+HITL universe — and both loops run on Policy, Prompts, and
Skills, forever.

---

*One chassis, many costumes, one immortal thread each — planning centrally, observing in
parallel, failing into curriculum, and improving under governance. Build your universe; the
agents build themselves.* 🥂
