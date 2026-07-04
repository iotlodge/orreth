# 0015 — Orreth.agent: the Chassis (running)

*Design + first implementation — from JB's Topic-2 dialog (`../vision/orreth-agent-the-chassis.md`
holds the vision). The founding move applied to cognition: one loop whose architecture never
changes; Policy, Prompts, Skills, Persona are the profile.*

## The loop (implemented: `orreth_sim/chassis.py`)

**prepare → plan → NUCLEUS → reflect/critic → replan → … → objective | breaker**

- **Cognition is injected** (`think(class, prompt)`) — the same chassis runs on a stub in tests
  and the governed model plane (0016) in production. The loop never knows which.
- **The nucleus holds the plan and executes ONLY the planner's observations — in parallel**
  (least-privilege attention). Each observation is either a **deterministic skill** (instant,
  free — e.g., a 0014 KnowledgeCategory lookup) or a **reason** call through the governed door.
  The becky-shaped duality, visible in one fan-out.
- **The breaker doesn't fail — it PARKS**: the unsolved intent lands in memory tagged
  `knowledge-intent`, a handoff to the librarian (0014). Failure is fuel.
- **Every cycle is on the record** (trace now; RunRecords with context_hash as the loop matures)
  and every token is metered through the plane.

## Proven (2026-07-04)

Hermetic: parallel skill+reason observation, single-cycle completion, breaker-parks-as-intent
(42/42 suite). Live: persona "frost" answered a Leadville envelope question in one cycle —
3 parallel observations, the corroborated 0014 claim flowing verbatim into the answer at $0,
836 metered tokens total. The two loops met.

## What matures next

Chassis-as-GraphSpec (0008 compile target) · RunRecords per cycle with context_hash · persona
as cascaded soft standard · the parked-intent → librarian → retry circuit closed automatically ·
Master/swarm class escalation on critic uncertainty.

*One chassis, many costumes, one immortal thread each.* 🥂
