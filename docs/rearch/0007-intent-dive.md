# 0007 — The Intent Dive: Infinite Horizon Intentions

**Status: DESIGNED — JB's lock, 2026-09-19 (seeded 2026-09-17 as the
"Infinite Horizon Initiative"; narrated as block 11) · intent sp1 BUILT the same day, walk owed.** Human Intention
becomes the topmost origin of work; the intent loop becomes the fifth
firmware-rail; the chat stays the one place a human begins anything; the
floor hatch becomes the Analyzer. Build: intent sp1 before P6.

## JB's direction (essence preserved)

Humans act through **Intention**. Orreth today treats Objective as the top
level; introduce human Intention as the topmost end-to-end process, and let
Orreth create Objectives for each "project" under it — a major enterprise
program with many flows and interdependencies, governed as program →
sub-projects → tasks. **"State is an outcome of applied Intent."** Human
Intention feeds a new, HIGHER embedded loop — Run Rate, Resiliency,
Security, Monitoring — the **Infinite Horizon Intention**, an uplift to
long-horizon agents, leveraging the firmware agents in a kernel whose
agents are always improving in a kernel that is always improving. Humans
see it in a new **ANALYZER** pull — progress of intentions, projects, and
graphs, in flight and completed — from the kernel's brain and memory,
*lookups, never fan-outs*. The chat is THE interface: everything a human
asks for is born there, and what they ask invokes the level, flow, or
graph inside the kernel; **Objectives is not a pull.** Keep it fluid: the
**Principle of Least Energy**. And keep Strategic Eternal Line-of-Sight on
Business, Security, Resiliency, Compliance, and Cost.

## The model (locked)

- **The ontology loop.** Intent (the human origin of work) → Objective (a
  bounded outcome) → Act (the agent origin) → Observation (what the world
  showed) → Improvement (what changes in us) → and the intention reads its
  observations to plan the next objective. This is the marker registry's
  structural vocabulary (0006), read as a loop. Observations are born of
  acts, not of intentions.
- **An intention is a record** (`spine_intentions`): `words · serves
  (business · security · resiliency · compliance · cost) · kind (human ·
  role · kernel) · interests (marker kinds) · planner (a firmware
  binding) · cadence · gates (HITL / on-the-loop) · stop · scope · by`.
  A schedule is the smallest intention — cadence only; the scheduler's
  rows fold in. The registry's `intention` kind widens to *any standing
  purpose*; the tree law is unchanged: an intention is a root, its
  objectives children, their acts and observations under them.
- **The intent loop — the fifth firmware-rail** (relay · dispatcher ·
  scheduler · serve · **intent**). Two triggers: a tick, or a marker set
  of a kind the intention is interested in (a red watch's observation, a
  `cost-anomaly`, an `improvement`). The kernel asks the intention's
  planner **under the intention's marker** — "here is what was observed;
  the next objective?" — and the planner's reply IS an objective: an ask
  to the crew with the intention as parent, filed in the intention's
  session so the human sees it in the chat as "on JB's word · owned by
  the kernel". The crew acts; observations land; the critic marks
  improvements; the loop turns. Gates ride the interlock (L2 in the chat);
  the stop is recorded, never a deletion (rule 11).
- **The ask wears its kind (P23).** No chat modes. The typed words propose
  the kind — thought · objective · intention — as a chip before send; one
  click or one word flips it; the marker is minted with the ask. The
  interest law re-dresses the chat: an objective wakes the planner, an
  intention wakes the intention architect; INCLUDES shows who is
  interested. Auditable, voice-ready, zero mode state.
- **The Analyzer (P25).** The floor hatch. Everything born in the chat,
  grouped by ORIGIN, in flight and completed, read from the ground —
  nothing sent → all active | completed intentions and objectives, human-
  and agent-owned; an origin sent from the chat → that tree. The MARKERS
  view lives here. The one invoke: "follow up on this by …" in the chat.
  Its assistant reviews; Workspace Engineering's makes — CUD is the line.
- **Infinite Horizon Intentions.** Five standing kernel intentions with no
  end — Business · Security · Resiliency · Compliance · Cost — declared
  at boot like kernel duties, each with interests, a planner, and its
  stop. **Resiliency first**: a red watch (an observation under it) births
  an objective under it. Cost next: the meter on the gateway, a
  `cost-anomaly` kind.
- **Templates are declarations, not graphs.** `intentions/<name>.v0.json`,
  cut from the draft shelf; the intention architect (a Workspace
  Engineering binding) helps a human fill one in the chat. The graph that
  runs an intention is the intent loop — one engine (0040): the planner
  emits objectives, objectives are asks, the crew's graphs run them. A
  human-authored LangGraph per intention waits for a proof that needs it.
- **Firmware-rails and on-behalf-of.** JB's names, adopted: the rails are
  the embedded loops the Operating Kernel provides as features; a human
  submits and the kernel's agents own the work through them — the chain
  says who, the marker says why, both rendered.

## What we do NOT claim (the honest boundary)

- **Not a single binary; not Rust.** The spine is Python on Postgres ·
  RabbitMQ · Kafka; the Rust plane (`orreth-node`) is the old world,
  sacred and untouched. The laws here are language-independent and a Rust
  kernel could carry them later. Until then the register does not say
  "single binary", and neither does the marketing line. The honest end
  shape: one kernel that governs; residents as processes it spawns.
- **Self-improving under human cut, not self-learning.** Improvement →
  critic → a proposed change on the draft shelf → the human cuts the
  version. Never raw feedback into a body.
- **Lookups, never fan-outs** is a promise the Analyzer must keep under
  measurement (P17's budget): the page paints from projections in under a
  second at 10k markers; a walk proves it or the line stops (IH-3: ~1 ms
  by law; walk #6: 0.02 s on the glass).
- **The loop's objectives need a crew that can act.** In sp1 the runner
  is the librarian — a conversationalist. Resiliency's objectives are
  real and lineaged but un-actionable until an acting resident exists
  (V1's infrastructure resident); sp2 binds the runner per `serves`.

## Where it lives and how it shows

- **The ground:** `spine_intentions` (the record) · `spine_markers` (the
  lineage; `intention` widened) · the scheduler's rows become intentions
  with cadence only. **The rail:** `orreth.intention.declared.v1` ·
  `orreth.intention.stopped.v1` · the planner's ask and the objective it
  births carry the intention's marker as parent.
- **Doors:** `/intentions` (list by serves · kind · state) · `POST
  /intentions` (declare — a human's) · `POST /intentions/stop` (rule 11:
  EVERY intention rests on the human's word, the kernel's included — an
  Infinite Horizon Intention is a managed program, not a body's duty;
  kernel DUTIES stay immutable as P4 sp5 locked; recorded on the row and
  on the rail, never deleted, and `declared` at the next boot leaves it
  at rest — JB may veto at sight) · `/analyzer` (origins with counts by
  kind, from the ground; `?origin=` for one tree) · the ask door accepts
  `kind` and `parent`.
- **The glass:** the floor hatch reads ANALYZER — origins grouped, each
  row a door to its tree; the MARKERS view moves in; the chat's chip
  before send; kernel-filed objectives render in the intention's session;
  the intention's stop is one click with a confirm.

## Proof

- **IH-1 — the loop turns.** Resiliency is declared at boot with its stop;
  a watch goes red; an observation lands under Resiliency; the planner is
  asked under it and answers an objective; the objective is an ask to the
  crew with Resiliency as parent, filed in its session; the crew's reply
  lands under the objective. The tree reads intention → observation ·
  objective → action; the ancestry from the reply names Resiliency. The
  stop is recorded and the loop does not turn again.
- **IH-2 — the ask wears its kind.** "keep this world resilient …" is
  proposed INTENTION; "plan a migration …" is proposed OBJECTIVE; a bare
  question is a THOUGHT; one word flips any; the marker minted matches
  the chip; the interest law wakes the planner for an objective.
- **IH-3 — the Analyzer is a projection.** With 10k markers on the ground,
  `/analyzer` answers in under 100 ms from projections alone (no body is
  asked); an origin's tree matches `/markers?root=`.

## Build

- **intent sp1 — the Analyzer, the kind of an ask, the fifth rail** ✅
  **BUILT 2026-09-19 — walk owed** (before P6; JB's lock): `intent.py`
  (the record · `read_words` · declare/declared/stop · the loop: watch
  transitions → `watch-red` under every interested intention → the
  interest law asks the planner under the observation → the replied plan
  filed as the objective to the runner, parent = the intention, in its
  session · cadence) · markers grow a ROOT column (the Analyzer is a
  GROUP BY, never a walk) and `origins`/`origin` · `dispatch_interests`
  asks intentions after bodies · the ask door takes `kind` (prefix >
  chip > the words' read) and `parent` · doors `/intentions` · `POST
  /intentions` · `/intentions/stop` · `/analyzer` · the rig's
  `_intent_loop` declares Resiliency at boot (runner: librarian — every
  body serves the shared bench, so an untargeted objective could land on
  a firmware body) and turns every 3 s · the glass: the ANALYZER hatch
  (INTENTIONS with stop · OBJECTIVES · an intention's tree in words · the
  MARKERS view moved in) · the KIND chip under the composer (the words
  propose; click flips; "objective: …" pins) · "follow up on this by …"
  files a child of the origin in focus · the chat says "on the kernel's
  word · <intention> → …" when an intention births work. Laws in
  `tests/test_intent.py`: IH-1 · IH-2 · IH-3 (origins at 10k: ~1 ms) ·
  the doors and the rail in the rig. **A wound found at the relight, cured
  the same hour:** the first `markers.ensure_schema` on a serving
  connection ran INSIDE a serve's transaction (the resident reading its
  ask's marker), so the new column's AccessExclusiveLock lived as long as
  the serve — one backend idle in transaction, every loop and door of the
  Bridge queued behind it for five minutes. Cure, and a law:
  `ground.ensure_all(conn)` flags EVERY ground the moment a rig connection
  is born (every loop, `serve_once`), door connections are autocommit too,
  and `tests/test_intent.py` pins it. **Not folded yet:** the scheduler's
  rows stay their own table (both mint `intention` markers; folding is
  sp3). Live on the dev ground within a minute of the relight: two red
  watches observed under Resiliency, the planner asked, its reply filed
  as an objective to the librarian, answered. **Walk #6 (2026-09-19,
  lean): SPEC-INTENT-01 PASS ×4 w/ friction · SPEC-ANALYZE-01 PASS ×2 w/
  friction** — the chip read INTENTION from the words; the declaration in
  0.05 s; a confirmed red watch woke the loop in 3–4 s (planner, then the
  objective to the librarian); the Analyzer painted origins in 0.02 s
  with no body asked, an intention's tree in words in 0.03 s. Ruled and
  cured the same hour: the crew's reply to a kernel-born objective now
  lands in the chat as a bubble (it was only in the tree, cut); the chat
  says WHOSE word ("on jb's word · owned by the kernel" for a human's
  intention, "on the kernel's word" for the kernel's); an open Analyzer
  row survives the feed's repaint; a twig is a door across its whole row
  and shows the reply whole. **Sp1's honest limit, recorded:** every
  objective Resiliency birthed today landed on the librarian, who has no
  tools for it — the loop turns, the crew that can act arrives with V1's
  infrastructure resident (intent sp2 names the runner per `serves`).
  Owed frictions: the two planner lines read alike when two intentions
  share words; the KIND chip is a three-click cycle; the kernel's
  intention session sits in "my sessions" for a human's intention; the
  stop was not walked (lean).
- **intent sp2** — the intention architect in the chat ("create an
  intention to …" fills a declaration; cut from the draft shelf) · Cost
  (the meter; `cost-anomaly`) · the Analyzer's review assistant.
- **intent sp3** — Business · Security · Compliance declared at boot; the
  line-of-sight face in the Analyzer (five rows, each its stop).

## Seeds this dive records

- **"Intents of Orreth"** — an article and a marketing line: one chat
  across every intent of the kernel.
- **orreth-voice** (V2) — a voice over the same chip; nothing to toggle.
