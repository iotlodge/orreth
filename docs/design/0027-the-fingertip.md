# 0027 — The Fingertip (thought.graph made concrete)

*Design draft — proposed by Fable 5 (design owner), from the Universe-Brain session
(2026-07-10, `../vision/the-universe-brain.md` §7; JB locks R7–R8 + the severity
lanes R6). The 2026-07-07 thought.graph drop lands here as mechanism: nodes with
altitude are now seats of the universe itself. This dive also discharges 0024's
deferral — critic markers on RunRecords ride the chassis.*

---

## Why this is a keystone

JB's closing frame: *"at the fingertip is the Orreth Agent"* — and his own analogy:
*"kind of like how YOU operate."* An orchestrator holds the big picture, spawns scoped
workers with slivers of context, reviews what returns — but across a closed-loop
universe that might be spread all over the world. Least-privilege attention, promoted
from a loop property (0015) to **the organizing principle of work itself**. And the
attachment thesis completes: the process was never the life, and now the loop is not
even the mission. **The universe is.**

---

## 1. The attachment law — no Field, no action

An Orreth agent without a universe attachment is **inert by design**: no seat, no
purpose, no data, no act. The agent requires a field to receive its Objective/Intent
AND the data needed to achieve it — all information comes from the universe it is
attached to. (The SDK's `FieldClient` already half-enforces this; the flow makes it
law: a fingertip's chassis binds only what its sliver names, and a sliver exists only
inside an attachment.)

## 2. The universe construct IS the node graph

The layers are workflow seats. An objective arrives at a tier; the orchestration
incarnation AT that tier plans; sub-intents ride **the request queue** to floors below
or beside — the queue is already the universe's dispatch medium (self-dialog legs,
0023 §3), human-visible, vigil-seen, restart-safe (0022 §8). A field, an ecosystem,
or the universe itself can be a NODE for the original Objective/Intent. No new
transport: **dispatch is a governed request, like everything else.**

## 3. The sliver contract — what rides down

A fingertip receives exactly: the **sub-intent** (one sentence of work), a **budget
slice** (tokens from the objective's grant, 0010), and **just-enough refs**
(ContentHash citations to the records it may read, 0023's citation discipline).
Never the plan, never the sibling slivers, never the objective's why. The big picture
stays higher in the stack — planning, strategy, step creation live up there.
**The fingertip never holds the whole.**

## 4. The orchestration incarnation (R8, locked)

PM / ProductDev / EA / BI are **GraphSpec templates** — versioned artifacts in memory,
factory-maintained like all behavioral assets (0011 ∘ 0008). An arriving objective
instantiates a template as an **orchestration incarnation**: factory-stamped, birth
certificate, budget from the intent, living the objective's life. **Standing jobs**
are the same incarnations with no completion condition — immortal jobs, beating like
organs. The template registry is memory (config IS memory); the factory's improvement
loop (0011 · §9 of the vision) refines templates from outcome evidence.

## 5. Journal-with-grain (R7, locked)

During execution the fingertip works in scratch — computation, not biography. What
lands on the floor: per-cycle **RunRecords** (already law, scribe-signed, 0005), the
**outcome memory**, and observations the floor's **KeepRules pin**. Raw scratch
evaporates by design: *if it informed a decision or changed the world, it lands; if
it was scaffolding, it was never memory.*

## 6. Review rides altitude — and grades on the record

Results ride UP: the seat that dispatched a sliver reviews what returns against the
original objective (nothing grades its own yardstick — the reviewer is the seat
above, author ≠ agent, 0005). The review lands as a **critic marker** (0024,
deferral discharged): a marker record deriving from the sliver's outcome record,
`change_severity` graded by the reviewing seat, reason mandatory — and the R6 lanes
route what happens next (low auto-accepts into the objective's assembly; high waits
for the human). Completion confirmation happens at the objective's home tier: for a
human-submitted objective, the resolution of their request IS the confirmation.

## 7. Cross-ecosystem dispatch

Whatever level the orchestration occurs at can send a sub-objective into ANOTHER
ecosystem's seats — specialist ecosystems are callable organs of any
sufficiently-entitled orchestration. Entitlement is the token: a dispatch whose
becky-chained authority covers the target floor posts the leg; one that does not is
refused uniformly (0002 §4) — and may stage a governed ask instead (0012).

## 8. HITL inside the flow

A flow node can stage a human question mid-objective (the worked example: IaC asks
*"where to deploy?"*). Mechanism: the branch parks as a pending request in the human
queue (0012 — consequence waits), the rest of the flow proceeds, and the answered
request resumes the branch on a later beat — exactly the self-dialog's
stage-now-compose-later shape. Silence never approves: expiry is denial (locked
2026-07-02).

## 9. What lands this spoonful

| Piece | Where | Status |
|---|---|---|
| Orchestration templates (registry + instantiate via factory) | sim `fingertip.py` | this dive |
| Objective fan-out, sliver contracts, review + critic markers | sim `fingertip.py` | this dive |
| Standing incarnation (no completion condition) | sim | this dive |
| `kind:"objective"` on the wire: instantiate → legs → compose → resolve | worker | this dive |
| Fingertip execution at the floor (chassis + sliver) | sim/worker | this dive (chassis exists) |
| HITL-inside-flow (question leg in the human queue) | worker | this dive |
| Cross-ecosystem dispatch (leg into another floor's queue, token-checked) | worker | this dive |
| LangGraph flavor of the fingertip | `agents/flavors/02-langgraph` | ledger — after sim proves shape |
| Factory RL loop over templates | spoonful 7 (workspaces & factory) | deferred |

## 10. Decisions

**Pre-locked by JB (2026-07-10):** R7 journal-with-grain · R8 templates + standing
incarnations · R6 severity lanes route review outcomes · implementation latitude
(*"the requirement is the properties, not the framework"*).

**Closed by the design owner (JB may veto):** the request queue is the dispatch
medium (no new transport) · the sliver contract is intent + budget slice + citation
refs, nothing else · critic-marker severity mapping: DONE-and-verified → low,
DONE-with-corrections → medium, RETRY exhausted / parked → high · sim proves the
shape before any framework flavor (0000 §9).

**Locked by JB (2026-07-11, AskUserQuestion):** the human's request IS the top node —
the assembled outcome resolves the objective's request, and no orchestrator ever
confirms its own completion · cross-ecosystem dispatch-miss = uniform refusal PLUS a
staged governed ask in the target's queue (the branch parks; silence = denial) · the
first standing incarnation is the **portfolio monitor** on the universe floor (its
factory-RL duty waits for spoonful 7).

---

*A thought is a graph now: the universe plans high, works low, and reviews on the
way back up — and the fingertip, fed one sliver, never needs to be trusted with the
whole to be excellent at its part.* 🥂
