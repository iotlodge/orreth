# 0010 — The Workshop: the Engineered Agents of Orreth

<!-- PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — the Agent Engineering phase, session 1: JB's scope notes vetted against the canon and the kernel on disk, eight discussions locked by JB through the question door · 2026-10-05 -->

**Status: LOCKED — JB's eight locks, 2026-10-05 (session 1 of the Agent
Engineering phase).** This is the rails document JB said he would write after
wound day; he wrote its substance as notes and we vetted them together in one
sitting. It rewrites Phase 8 of 0005 as THE WORKSHOP, pulled ahead of row 5.
**Builds are HELD until JB's word**; the push to origin, the demo and the book
turn together when this phase closes (the release-alignment law).

---

## Why this document exists

JB, 2026-10-05, his scope in his words: *"Continuity of Operations in Kernel
for the Engineering and Lifecycle Management of Engineered Agents. This
requires a professional and efficient Workspace/Workshop that will allow for
all configuration, testing, experimentation, minting, etc. of all associated
settings, minds, flows, etc. Fully featured."* And the measure of the phase:
*"your success is based on 'how well Orreth can do it' vs YOU … To get to V1
Orreth will need to be able to take a prompt and create what was asked and
provide the ability to manage and oversight it."*

Everything in this phase is for the kernel. The thing a human engineers here
is an **Engineered Agent**: a graph wearing an Orreth identity, born from
versioned components on the shelf, tested in a room, promoted by a human's
stamped word, chatted with, summoned, graded, improved through the critic's
proposal, and one day rested and decommissioned with its record kept.

## What stood before this document (the honest ground)

**The canon had already designed most of it under other names.** 0001 locked
a pull called "Workspace Engineering" with two views and one artifact shelf,
a firmware agent per pull, and an "Agent Assistance" link from every piece of
metadata into its versioning. 0004 holds the draft-shelf law (a draft lives
with the person; cutting a version is the gate; AG-9) and the factories. 0005
Phase 8 owed skills, prompts and graph templates as versioned objects and an
Experiment with two arms graded by the grader identity. The seeds hold the
third loop (graded learning), the identity chip, the security and architect
residents, and the Costs Panel.

**The kernel on disk (0.1.0 + wound day) already does part of it.** Every
body is a LangGraph process the kernel spawns, joined through the desk with a
keypair, a lease and a template hash. A name at the head of an ask selects a
body. The event-response loop is wired end to end (a red watch → a marker →
a plan → an objective → a runner → the levers → an attributed outcome). The
impact door names every body that wears a template or binding. The A/B
harness runs golden cases against two minds and returns a proposal. The
services shelf has the exact ladder components need: registered →
versioned(n) → healthy | unhealthy → retired → restored, a content hash as
the pin, a version history. The Stable assigns a mind per subject and class.

**The foundation that was missing.** No table for templates, prompts, skills,
policies or graphs: templates are files on disk, the ground records only
their hash. The template's `graph` field was read by nothing; every body ran
one fixed graph (hear → recall → think). Grades and improvements had no
store. No dev/prod mode. No agent class beyond firmware and resident. No
decommission for an agent. No door for a graph the kernel did not spawn. And
the recursion of 0000 (universe → ecosystem → field, every layer staffed) was
carried only at the top: a universe is a cell; inside it one flat scope. The
inner levels had been deferred as seeds at P7 sp7 (0009 row "the cascade
resolver": *"No floors, no cascade"*), not replaced — JB's alarm on reading
"Floor = cell" was answered with those rows, and the mapping withdrawn.

## The locks

### 1. The name and the road

- **THE WORKSHOP** is the one place where all mutability occurs. 0001's
  "Workspace Engineering" is amended to it. "Workspace" stays the generic
  word for any pull's working surface; Floor and Room are the scope words.
- **Phase 8 pulled ahead of row 5.** This phase is THE FACTORIES with the
  Workshop as its face. It absorbs row 6a's grader verdicts (below). Import
  means a repo'd graph the kernel runs; row 5's running STRANGER stays after
  this phase, as do RAG, the embedding lane and the architect resident.

### 2. The levels — Universe · Floor · Room

JB's correction, verbatim: *"In original Kernel 0.72 a universe has many
ecosystems and ecosystems have fields. Each of these allow for instance of
firmware/resident aligned to scope and governance of respective level."*

- **Three levels, each staffed.** **Universe** = the CELL (its own database,
  role, benches, topics, kernel self and policy sheet; cells speak over the
  signed seam). **Floor** (was *ecosystem*) and **Room** (was *field*) are
  scopes inside it. Each level may declare its own firmware and resident
  instances by manifest. Governance tightens DOWN the path; recall escalates
  and metrics and grades fold UP. This is 0000's recursion contract, carried
  back.
- **Mechanism: a ScopePath in one kernel per cell.** The `scope` column
  every table already carries becomes a path (`u:dev/f:ops/r:bob`). The
  cell's one `orrethd` serves every level — never a process per floor, which
  was the polling disease that caused the halt. Schema v5. Two seeds unpark
  at their minimum: the cascade fold (0007's resolver) and the roll-up
  monoid (the honest boundary's `orreth-rollup` row).
- The words *ecosystem* and *field* retire from every people-facing surface.
  Code renames only on JB's word per surface.

### 3. The Inventory

Laws, JB's: *every Agent is a sum of its versioned components; an Agent
cannot exist outside versioned components; a versioned component knows
whether it is in use and by how many agents.*

- **The one shelf, widened.** The services shelf gains the craft kinds:
  `template · prompt · skill · policy · graph · binding · golden`. Same
  ladder, same pin (the content hash over canonical bytes), same version
  history, same retire and restore, same door family. A component is
  addressed by name and hash and **mints no DID of its own** (Orreth Law 1:
  a human approves every new DID). The plain word in the glass is still
  "the shelf".
- **The wear table.** Which body wears which component at which version,
  written at every join and every re-cut, closed at decom. It is "in use by
  N", the blast radius the impact door reads, the decom refusal, and the
  repo-to-running correlation for forensics.
- **Source origin.** An agent that is not firmware or resident is repo'd: a
  component of kind `source` carries the repository, the commit and the
  entry point; the wear table ties it to every running life.
- **Golden is a component.** Every engineered agent is born with its golden
  set (ask → expect pairs, the harness's format) on the shelf beside it.
- **The draft shelf lives in the ground, under the person.** A drafts table
  beside the profile. The law of 0004 holds unchanged: a draft never appears
  in the inventory nor in any recall (AG-9); only its author's seat reads
  it; it survives a closed browser; no other person's session can pull it.
  0004's "S3/local" is amended to this.

### 4. Classes and mutability

- **Four classes, three selves.** Firmware, resident and agent are selves: a
  DID that survives the process (covenant rule 1). A **sub-agent is a LIFE,
  not a self**: it runs a versioned template under its creator's DID as a
  numbered life with a narrower lease, mints no DID, has no chat, and its
  grades fold to its creator. Its graph is still a component on the shelf,
  managed in the Workshop. The plain word in the glass is **helper**
  ("Bob's helpers"); "sub-agent" stays in canon and code.
- **Mode lives on every scope of the path, tighten-only.** A universe is
  declared dev or prod when its cell opens. A prod universe's floors and
  rooms inherit prod. A room may be opened as an **experiment room** by a
  governed act. Nothing promotes out of an experiment room except through
  the Experiment gate: that is the partition of human experiments from
  production, structurally.
- **Mutability by class.** Firmware is cut only in a dev universe and
  reaches prod as a release. A resident's cut needs L3 (TOTP) and lands as a
  sibling version. An agent's cut needs the Experiment. Kernel-critical
  schedules and kernel tools stay immutable in prod (0004).

### 5. The Experiment, the cut, and decom

- **The Experiment.** A candidate cut on the draft shelf opens an experiment
  room on the path. Two arms run there: the current version and the
  candidate, instantiated as a life in the room. Evidence: the agent's
  **golden set (required)** and a **shadow replay of recent real asks into
  the room (optional)**. The **grader grades both arms under its own DID**
  (rule 2: nothing grades its own yardstick). Reviewers come by the interest
  law: **grader and critic now; security and identity as honest empty slots**
  named on the card until lock 8 builds them. Resiliency is the room's
  watches staying green through the run. **The verdict is a proposal.**
- **The cut.** Promotion is the human's stamped act: L2 for an agent, L3
  for a resident. The new version is a sibling; the wear table re-points;
  the body restarts into its next life; the room's full marker chain is the
  replay. Nothing leaves the room any other way.
- **Decom, a ladder.** Active → **rested** (the stop, rule 11, L2) →
  **decommissioned** (grave, L3). Decom removes the role's live objects:
  seats, leases, bench and topics, gateway key, its schedules, watches and
  intentions, and closes its wear links. The DID, the joins and the Record
  stay. Components nobody else wears are pruned by a **beat sweep, never at
  request time**; the impact door refuses while another workforce still
  depends on it. **Restore is a new life from a shelf version, never a
  revival.**

### 6. The hull, import, chat and summon, the graph

- **The hull.** The body's fixed graph becomes the hull: hear → recall →
  **route** → one of three entry edges — **chat** (a human's ask), **work**
  (an objective from the intent loop), **event** (a marker dispatched by
  interest) — into the **work node**, which is the template's `graph`
  component from the shelf, finally read (`mind.v0` = today's think). JB's
  three modes of agent interoperability ARE those three edges. The kernel's
  laws live in the hull and never in the agent's graph: the seat words, the
  covenant slice, the metered gateway, the checkpoint per hop, the stop at a
  safe boundary. That is how the kernel alters the call stack without
  touching an agent's own nodes.
- **Import.** Two births, one door. *Create* authors the graph in the
  Workshop. *Import* registers a repo'd LangGraph as `source` + `graph`
  (repo, commit, entry point) and the hull wraps it. Both go draft → cut →
  experiment → promote. A body running outside the kernel's spawn is row 5's
  stranger, after this phase.
- **Chat and summon.** "Bob, investigate …" works through the address law
  once Bob is a body. **Summon** generalizes the MITL toggle: the includes
  list opens from four names to any resident or agent whose template
  declares `summonable` (firmware by declaration; **helpers never**), with
  summoned and dismissed facts per session.
- **The graph: one format, one renderer, three uses.** Authoring a
  component with a node inspector; watching a live body through its
  checkpoints (every hop is already recorded); replaying a finished
  intention through its marker chain (the Analyzer already groups by
  origin). Two graphs that talk are two bodies with a bench between them,
  drawn as an edge. **No second execution engine** (0040's law holds).
- **Authoring v0 is declaration first, canvas as the view.** The graph
  component is a declaration (nodes, edges, per-node prompt, skill, tool and
  mind references); the canvas renders it; the node inspector edits node
  settings; the Workshop agent edits it on the human's words. Drag-to-wire
  is a later spoonful.

### 7. The Operating State — the measurements and the improvement loop

JB's Kernel Strategic Measurements (his notes, 2026-10-05): **Trust** (the
ability to do the right thing) · **Recall** (the ability to replay) ·
**Efficiency** (use of Orreth) · **Experience** (feedback) · **Cost** (Layer
7 through Layer 1 correlation and itemisation), each 1.0000 at the ideal.

- **Five watch metrics, target 1.0, v0 coverage ratios adopted now and
  named v0** in the glass and the book: Trust = graded replies that passed
  over all graded replies · Recall = served asks whose journey and reply
  both landed and replay over all served asks · Efficiency = serves finished
  inside their latency class over all serves · Experience = non-negative
  human feedback over all feedback given, **"unknown" when none, never a
  silent 1.0** · Cost = spend attributable to an intention, objective or ask
  over all spend, until the Costs Panel brings itemisation to the metal.
- **One kernel intention, THE OPERATING STATE**, declared at boot beside
  Resiliency, interested in all five; a red is a watch-red event on the loop
  that exists; its planner routes the objective to the right crew.
- **The improvement loop closes in the Workshop.** Improvement marker → the
  critic proposes → a draft on the draft shelf **under the agent's owner**,
  marked "proposed by the critic from marker X" → the owner opens it in the
  Workshop → cut → Experiment → promote. Raw feedback never reaches a body.
- **Row 6a in this phase:** the grader becomes the events-rail consumer
  writing **signed verdicts on Experiment arms and on live replies**; Trust
  reads them. The lessons digest (the fast lane) is the next row.

### 8. The Workshop's agent, the mind chip, the two chips

- **The Workshop's agent** is the workspace firmware with a third binding,
  `workshop`: it searches the shelf, loads and explains a template, and
  edits a draft's declaration on the human's words. **Its writes to the
  draft shelf are routine (L1)** — drafts are unversioned, under the human's
  seat, never in inventory. **The cut stays the human's.**
- **The mind chip.** One chip in the Workshop assigns the workshop body's
  mind from the Stable's standing stalls through the existing assign door; a
  frontier Claude stall among the choices is **Claude the model**, metered
  like everything else. MITL stays its own summon. **Claude the developer**
  (repo access, the factories' hands) is Phase 9 and is named as such on the
  chip's card so nobody mistakes one for the other.
- **The two chips.** v0 of **identity** (holds the ceremony and the seats;
  reviews a candidate's lease claims; re-challenges bodies on the cadence)
  and **security** (reviews a candidate's capability and policy diff; reads
  the refusals ground; the key-check cadence) are built in the last spoonful
  so Bob's gate closes whole. Both are firmware of the third kind on the crew
  manifest. **Architect stays held with RAG.**

## The continuity notes (JB's first paste, kept here so they are never lost)

- **Applied Intentions (infinite horizon):** Resiliency, Security,
  Compliance, Regulatory — with RTO, RPO, Compliance, Audit and External
  Regulations as their measures. Extends 0007's five serves.
- **Three modes of human interoperability:** Chat · Objective [chat or
  workshop] · Intention [chat or workshop] — the ask's kind (P23) seen from
  the human's side. Distinct from the manual · assist · full-auto dial of
  how much the human engineers.
- **Three modes of agent interoperability:** helping humans in chat · doing
  assigned work · responding to events in operations (triggers, queues,
  assessed state). They are the hull's three edges.

## The build — six spoonfuls and the proof

Each spoonful is a thing a human proves in the glass before the next opens
(the walk law). Each grows its conformance fixture on both kernels.

1. **THE PATH.** Universe, floor, room on one ScopePath in one kernel per
   cell; mode tighten-only; crews per level by manifest; the cascade and
   roll-up seeds at their minimum; schema v5. **BUILT 2026-10-05 (JB's word:
   "spoonful 1, THE PATH"); WALKED the same evening (SPEC-PATH-01 PASS, W97 ·
   W98 cured).** What landed: the
   grammar and the child law · `SPINE_MODE` at the cell's open, tighten-only
   down the path, a prod universe refusing to light as dev · the experiment
   room (rooms only) · `spine_levels` (schema 5) with the universe's row seeded
   at light and the crew manifest's `levels` declared at light · a seat's `at`
   seating its body on a level, the body born with the level as its scope,
   joining AT the level · the `scope` column a path: listings at a level see
   everything within it, a body's shared reads resolve at its universe, its
   memories recall UP the path · `GET /levels` with HERE and ROLLED (the 0005
   monoid) · `GET /levels/context` (the 0007 fold) · `POST /levels/open` held
   at L2 · the glass's mode tag, levels line, chat words and notice · 0009 and
   0010 in MITL's corpus · fixture `levels-v0.json` (69), 818/818 on both
   kernels. Named, not in sp1: a floor's own shelf, Stable and policy (the
   shared reads escalate to the universe); the Rust kernel's own reads stand
   at the universe (one kernel per cell is always at depth 1); `context_hash`
   on a thought; the Costs Panel's fold; the book's `SPINE_MODE` pin.
2. **THE SHELF WIDENED.** The craft kinds, the wear table, the draft shelf
   under the person, golden as a component, source with repo and commit;
   the hull with its three edges, the template's graph finally read. **BUILT
   2026-10-05 (JB's word: "spoonful 2, THE SHELF WIDENED"); WALKED the same
   evening (SPEC-SHELF-01 PASS; W99 · W100 · W101 cured).** What landed, both kernels law for law: the
   one shelf's kinds widened to twelve — the five identities and the seven
   crafts (`template · prompt · skill · policy · graph · binding · golden`), a
   craft named `<name>.<kind>` on the shelf and ADDRESSED (`craft:<name>.<kind>`
   in the `did` column — a component is not a self, no DID minted), its health
   its declaration reading whole (a template's graph must stand on the shelf) ·
   the crafts the spine ships registered at light (nine templates, two
   bindings, the covenant policy, the graphs `mind.v0` and `echo.v0`, the
   librarian's golden set, the `shelf` skill) · a `source`'s second form
   (`repo · commit · entry`, "not probed here" until import) · THE WEAR TABLE
   (`spine_wear`, schema 6): the body writes one row per component in its
   join's transaction, the previous life's rows closed; `GET /wear` answers
   who wears what ("in use by N" on every craft card) · THE DRAFT SHELF
   (`spine_drafts`): under the person, the author's seat alone, routine to
   save (L1, no fact); THE CUT (`POST /drafts/cut` → the kernel's held act
   `craft.cut`) at the class's level — L2, a resident's template L3-code,
   firmware refused in a prod universe, an agent's template refused until
   the Experiment — settled as the ladder's register or version with the
   person on the chain, the draft spent · THE HULL in `resident.py`: hear →
   recall → route → `edge-chat · edge-work · edge-event` → `work`, the edge
   read off the ask's marker and said in the journey; the work node runs the
   template's `graph` component from the shelf (the file as fallback), node
   by node — `think` the metered mind (a node's `prompt` component joins the
   system words), `echo` the words back; a template naming a graph the shelf
   lacks CANNOT ACT and says so · the golden set a component the harness reads
   first · the glass: craft cards (address, worn by N, what it declares, "who
   wears it?"), the organ's crafts count, the chat's "show the crafts" · "who
   wears the librarian template?" · "what is echo made of?" · "my drafts" ·
   "draft a prompt called …: …" · "cut the … draft" (held) · "discard …" ·
   fixture `crafts-v0.json` ×86 (eleven kinds), conformance on both kernels ·
   `test_crafts.py` (6) · `tests/crafts.rs` on the rig. Named, not in sp2: the
   wear row's `until` at decom (sp4); a re-cut re-pointing the wear table
   (sp4's promotion); the sub-agent's code noun (no life is minted before
   sp4); branching graphs and per-node tools and skills executed (the Workshop's
   authoring, sp3 — v0 reads `prompt` only); a floor's own shelf.
3. **THE WORKSHOP v0.** The full-screen pull (like THE PANEL), the
   declaration-to-canvas renderer, the node inspector, draft editing, the
   `workshop` binding and the mind chip, "load Y in the Workshop" from chat,
   finding earlier work. **BUILT 2026-10-06 (JB's word: "Spoonful 3, THE
   WORKSHOP v0"); the walk in the glass OWED (SPEC-WORKSHOP-01).** JB's lock
   at the open: Floor and Room are deploy-step fields — the Workshop shows
   where a craft's wearers stand; the choice rides sp4's promotion. What
   landed: THE GRAPH BRANCHES on both kernels — an edge wears `when` (one of
   `{edge: chat | work | event}` · `{ask: pattern}` · `{reply: pattern}`), at
   most one default way out per node, typed node refs, forward only;
   `path(g)` the default line, `branches(g)` the forks (fixture `crafts-v0`
   86 → 99, conformance 918/918) · THE HULL picks the way out as the run goes
   and says each pick; a node's `skill` joins the system words, its `tools`
   narrow the door (never past the template), its `mind` pins the stall ·
   THE WORKSHOP'S AGENT: the `workshop` binding (the third workspace seat),
   its recall the shelf and the ONE open draft the author's ask names (AG-9
   kept), its one tool `draft` (routine, under the ask's person; the cut
   stays the human's) · THE MIND CHIP through `/minds/assign` (subject
   `workshop`, L2; "Claude the model" named, Claude the developer named as
   Phase 9) · THE GLASS: the full-screen pull with the rail (drafts · the
   shelf by kind · filter · new draft), the SVG canvas (layered by the
   longest road, the entry ringed, `when` arrows violet, the legend's
   default line), the node and way-out inspectors, the JSON declaration box,
   SAVE · CUT · discard, read-only crafts with WHERE IT STANDS and "draft
   from this", the agent's hand redrawing the open draft, "open the
   workshop" · "load Y in the workshop" · the `workshop` skill and guide
   section. Named, not in sp3: drag-to-wire; a frontier Claude stall seeded
   (no invented price); the live-watch and replay uses of the renderer; a
   graph compiled to its own LangGraph (the hull interprets the declaration
   inside one hop — one engine).
4. **THE EXPERIMENT AND THE CUT.** Experiment rooms, two arms, the grader's
   signed verdicts on arms and live replies, the proposal, the stamped
   promotion into a next life, the decom ladder and its prune beat.
5. **THE OPERATING STATE.** The five measurement watches at v0, the kernel
   intention, the improvement loop landing proposals on the owner's draft
   shelf, summon generalized, import from a repo.
6. **THE TWO CHIPS.** Identity and security v0 as the gate's reviewers.

**The proof is Bob.** One engineered agent walked create → cut → experiment
→ promote → chat and summon → driven red → improved through the critic's
proposal → re-cut → rested → decommissioned, with the record kept. Then the
same walk done again **by the Workshop agent on JB's words**.

**The Orreth-skill law (JB's phase objective).** Every spoonful ships the
Orreth skill for what Fable built — the ontology slice and the skill
component on the shelf — so that the measure at the walk is how well Orreth
does it, not how well Fable did.

**Release discipline (JB).** Push to GitHub when this phase succeeds; the
demo and the book turn with the push; jsbarth.com only when key architecture
evolves.

## What we do NOT claim

- The five measurements' v0 formulas are coverage ratios, not the measures
  JB ultimately means; each is refined when its richer source lands (the
  grader's verdicts, human feedback, itemised cost).
- Security and identity are empty slots at the gate until spoonful 6; the
  card says so.
- A body running outside the kernel's spawn (the stranger) is not chat-able
  in this phase; import means a repo'd graph the kernel runs.
- The lessons digest, the architect resident, RAG and the embedding lane,
  drag-to-wire authoring, and Claude the developer are after this phase.

## Open, carried (not locked)

- ~~Whether Floor and Room appear as **standing selectors** in the Workshop
  or as **fields on the deploy step** of a lifecycle (JB named both; decide
  at spoonful 3's open).~~ **LOCKED by JB 2026-10-06 at sp3's open: fields on
  the deploy step.** The Workshop v0 shows WHERE a craft's wearers stand
  (read-only, from the wear table and the crew's levels); where a body's
  next life stands is a field on sp4's promotion. No standing selector — a
  draft has no level (it lives under the person) and the shelf resolves at
  the universe (a floor's own shelf is named, not built).
- ~~The exact declaration shape of the `graph` component (0004's open
  "template schema v0"); lands with spoonful 2's fixture.~~ **ANSWERED in
  spoonful 2:** `orreth-graph/1` — `entry` · `nodes: [{id, kind: think | echo,
  prompt?, skill?, tools?, mind?}]` · `edges: [{from, to}]`, one path from the
  entry (fixture `crafts-v0.json`, `craft_manifest` · `graph_path`).
- Agent-created resources and "kernel tools" protected in prod — JB's own
  dive, later.
- Sub-agent words in code (`helper` in the glass is locked; the code's noun
  is spoonful 2's call).

## What this document amends

- **0001** — the pull "Workspace Engineering" → **the Workshop**; the draft
  shelf line (in the ground, under the person).
- **0004** — the hull and the graph component (the `graph` field is read);
  the draft shelf's home; helpers as lives; the levels.
- **0005** — Phase 8 rewritten as THE WORKSHOP, pulled ahead of row 5; row
  6a's verdicts absorbed.
- **0007** — "a human-authored LangGraph waits for a proof that needs it":
  this phase is that proof; the one-engine law holds.
- **0009** — the cascade resolver and the universe-as-data rows point here.
- **The honest boundary** — a DESIGNED · OWED row for the Workshop; the
  Faculty + Agent Lab row absorbed; the resolver and rollup rows unparked
  into spoonful 1.
- **Seeds** — graded learning (verdicts here, digest after); identity and
  security (v0 here, architect held); the Costs Panel (Cost v0 here).
