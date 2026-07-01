# 0008 — The Pane & Graph Engineering (interop/UX)

*Design draft for review — Fable owns design/usability (locked 2026-07-01: native Orreth, fresh; CO informs,
never drives). Locked inputs: **dual-mode authoring, equal weight** (both projections of GraphSpec) ·
**GraphSpec IR → compiles to any SDK** · **lane-routed Standards flow** for changes · **v1 hero = the Field
commander pane** · **the spacetime window is the north star** (concept: `../vision/Orreth-spacetime-window-concept.(svg|png)`).
**Open decisions** flagged at the end.*

---

## Why this is a keystone

For agents, Orreth is contracts. **For humans, Orreth is the pane** — and the differentiator JB named:
*people who can describe a workflow get a governed agent workforce, without learning a node palette.*
This dive designs three things as one system: the **GraphSpec** IR, the **dual-mode authoring** experience
over it, and the **Field commander pane** it lives in — with the recursive pane and the spacetime window
falling out of the same components.

---

## 1. Design principles (native Orreth)

1. **The pane is a governed window, not a dashboard.** Every widget is a `Query` under the viewer's
   capability token; every render writes an access record. There is no privileged pane path — the watchers
   stay watched, structurally.
2. **Provenance is UI.** Sourced + Verified isn't a backend property; it's a visible chip on every fact.
   Fidelity renders honestly: `verified` crisp · `distilled` softened · `distilled — raw expired` labeled.
   A `remainder` renders as a visible "not searched" band, never silence.
3. **Calm until drift.** The steady state is quiet; amber is information, pulse is escalation. The pane
   earns attention rather than demanding it.
4. **English is an equal citizen.** Text and canvas are two renderers of one GraphSpec — editing either
   diffs the artifact, and the other view re-renders. No sync problem exists because there is nothing to sync.
5. **Never guess silently.** When natural language is ambiguous, the authoring surface asks an inline
   clarifying question with concrete options. A guessed graph is a governance hole wearing a convenience mask.
6. **Dark and light, professional, fit to purpose** (JB's standing UI doctrine). Next.js · TypeScript ·
   Tailwind. Zero component lift from CO — lessons only.

---

## 2. GraphSpec v0 — the artifact both surfaces edit

Language-neutral IR; the schema lands in `contracts/` once this dive is blessed.

```
GraphSpec {
  id          : ContentHash            # content-addressed like everything else
  version     : SemVer                 # every change is a new version — the lane flow governs activation
  scope       : ScopePath              # where it runs (a Field, usually)
  title       : string
  nodes       : Node[]
  edges       : Edge[]
  objectives  : { vector: ObjectiveRef, floors: StandardRef[] }   # what "good" means for this graph
  narrative   : Sentence[]             # the English projection — sentence ↔ node/edge bijection (§3)
  signature   : Sig                    # authored + signed like any Standard
}

Node =
  | { kind: "agent",  role: RoleId, skills: StandardRef[], model_tier: string,
      identity?: DID }                 # bound to a living identity at instantiation (roster/lease/interview)
  | { kind: "gate",   gate: "hitl", queue: GateRef, co_sign?: N }              # a human decision point
  | { kind: "tool",   binding: ToolBinding }                                    # MCP/AgentSurface tool step
  | { kind: "memory", op: "retrieve" | "write", query_template?: QueryRef }     # substrate access, explicit

Edge = { from: NodeRef, to: NodeRef, when?: Condition }   # control flow; conditions are declarative
```

- **Policy-checkable before it runs:** floors validate against the GraphSpec statically — a graph that
  routes regulated data past its consent gate fails at *save*, not at incident review.
- **Compiles down, never leaks up:** LangGraph is compile target #1 (via AgentSurface); a customer SDK is a
  compiler, not a fork. Governance, canary, diff, and the pane speak GraphSpec only.
- **`memory` nodes make substrate access explicit** — retrieval in a workflow is visible, governable, and
  budgeted in the graph itself, not buried in agent code.

---

## 3. Dual-mode authoring — one artifact, two renderers

- **The narrative projection.** GraphSpec carries its own English: an ordered `Sentence[]` where each
  sentence maps to nodes/edges (bijection maintained by the editor). Free-prose input is accepted and
  *normalized* into the controlled narrative — the user speaks naturally; the artifact stays deterministic.
  > *"When a claim arrives, **Triage** (claims-triage skill, mid-tier model) scores severity. If severity ≥
  > high, route to **Senior-Adjuster**, else **Auto-Settle**. Every settlement is verified against
  > **policy-floor:claims-v3**; below 0.8 confidence, escalate to the **adjuster gate** (1 co-sign)."*
- **The canvas projection.** The same GraphSpec as a live graph — nodes typed by kind, gates as diamonds,
  memory nodes as cylinders, running instances animating along edges.
- **Edit protocol:** any edit (either surface) → GraphSpec diff → both surfaces re-render from the new
  version. Dragging an edge rewrites a sentence; rewording a sentence re-wires an edge — and the **diff is
  the reviewable object** in the change lane.
- **Ambiguity → inline elicitation** (§1.5): "route to the right specialist" yields a concrete question —
  *which of these three roster roles?* — options rendered, answer recorded in the narrative.

---

## 4. Change flow — the lane, reused (locked)

A GraphSpec edit is a **versioned Standard** in the existing lifecycle: `proposed → canary → promoted /
reverted / escalated`. Low-risk + high-confidence (prompt rewording, exemplar add) → **auto-apply lane**,
still signed + canaried + revertible. Structural changes (new edge past a gate, floor-adjacent wiring) →
**governed lane**, human gate, co-sign per policy. The canary compares the objective vector on a traffic
slice — *the same machinery EH proved*, pointed at UX.

---

## 5. The Field commander pane (v1 hero) — six regions

| Region | Content | It is literally |
|---|---|---|
| **Header strip** | field identity chip, drift state, gates pending, "coarse window" markers | roll-up + steward flags |
| **Graph canvas** *(center, hero)* | GraphSpecs live: instances flowing, per-node health, drift glow | GraphSpec render + Run Record stream |
| **Narrative dock** *(left, collapsible)* | the English projection; edit here = edit the graph | GraphSpec `narrative` |
| **Roster rail** *(right)* | residents pinned (steward · becky · governance) + workforce: attachment status, AgentFacts chips, lease terms; "add agent" → roster / marketplace / **interview** | Identity + AgentFacts queries |
| **Memory explorer** *(bottom, tabbed)* | worldlines per identity; time scrubber; fidelity honestly textured | the retrieval contract, visualized |
| **The Gate** *(right, docked)* | escalation queue: canary Δ-vector, approve / reject, co-sign state | the HITL queue |

**The recursive pane:** an Ecosystem pane is the same shell with field-cards in the canvas and cross-field
telemetry in the explorer; the Universe pane is ecosystem-cards plus **the window** (§6). One component set,
ScopePath-parametrized; drill-down = ScopePath descent. Entitlement decides what renders: down/within by
default, up/across only with the grant — the pane *cannot* show what the token cannot ask.

---

## 6. The spacetime window (north star — concept shipped with this dive)

The Universe pane's hero at full maturity: **occupy any (space × time) coordinate and perceive the verified
state of the world there.** Concretely it is *only* a Query — `space: apex-subtree, time: T` — rendered as:

- **The block:** the subtree's worldlines stacked through time; the selected instant is a **hypersurface
  slice** — the complete, verified cross-section at T.
- **The scrubber:** the present is live and pixel-sharp; scrubbing back, fidelity *visibly* softens
  (distilled texture) exactly as pruning dictates — the fidelity curve (0003) rendered, never hidden.
- **The cut readout:** every slice shows its provenance — Sourced count, verification mix, remainder,
  light-cone edge ("as risen and verified by T+Δ").
- **Entitlement-bounded:** the window shows the viewer's subtree, period. The telescope has an operator's
  log, and the operator is in it.

*Concept art: `../vision/Orreth-spacetime-window-concept.(svg|png)`.*

---

## 7. Open decisions — your call, JB

1. **Canvas engine.** React Flow (proven, fast to ship, styling fully ours) vs custom WebGL canvas (unbounded
   ceiling for the window's block-view later, much slower start). *Lean: React Flow for the Field pane now;
   the spacetime window's block-view gets its own renderer when it's built — different problems, different tools.*
2. **Narrative register.** Controlled-English narrative as the stored projection (deterministic round-trip,
   reads slightly formal) with free prose accepted at input and normalized — vs storing the user's raw prose
   and re-deriving structure per edit (natural, but round-trip drift risk). *Lean: controlled narrative stored,
   free prose in. Example: you type "if it's a big claim send it to a senior person" — the dock shows
   "If severity ≥ high, route to Senior-Adjuster" and asks once what "big" means, numerically.*
3. **Instantiation gate.** When a GraphSpec binds a `Node.kind=agent` to a real identity, is a lease/interview
   *always* required for non-resident agents (safest, most friction) or only when crossing tenancy (my lean —
   your own roster binds freely; marketplace agents interview first)? *Example: binding your own claims-triage
   agent is one click; leasing an external fraud-specialist walks through the interview room.*

---

*Unblocks: `GraphSpec` + `AgentSurface` contracts (`contracts/v1`), the frontend build plan, and `0009`'s
"Build My First Universe" flow (a template is, in large part, a starter set of GraphSpecs + roster).* 🥃
