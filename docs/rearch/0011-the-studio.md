# 0011 — The Studio: the Workshop grown into one place that tells one story

<!-- PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — written on JB's word 2026-10-13 after THE WIZARD WALK (W124–W136) and the LangGraph Studio review; the locks marked JB's are his, the rest are Fable's recommendation for his lock through the question door -->

**Status: LOCKED — JB's four answers through the question door, 2026-10-13 (one Yes for the chain · a Yes on the bench's card too · Opus by stock · "Studio" at spoonful 11). Builds HELD until JB's word per spoonful.** JB's words that day: *"We clearly
need to redo this user experience"*, *"the kernel needs a Studio and that is our
objective with Workshop"*, *"I am REALLY focused on langchain/langgraph"*, *"fully
auto … the workshop agent will perform this for me"*, *"I want to avoid having a
decoupled dependency like langsmith"*. Three things are already his locks and are
not reopened here: **the Studio is in the kernel** (no LangSmith, no second
kernel); **the three modes law** (manual · assist · full auto is the human's dial;
a consequence holds for a person in every mode); **the interlock is the kernel's
one hold** — and by JB's lock of 2026-10-13 it wears TWO FACES: the chat's Yes
and the bench card's Yes answer the SAME hold (one wait list, two faces — the
Console gate bell's law of 0044); the chat remains the record.

---

## Why this document exists

THE WIZARD (0010, spoonful 7) fixed the steps and not the feeling. JB walked it
three times on 2026-10-12/13 as bob, imp, imp2 and jonathan, and every walk
found a wound in the same place: not in a door, but between the places. The
chat told the story in held acts, the feed told it in notices, the Workshop
told it in drafts and a card, and when one of the three fell silent (the feed
fell twice — W129, W133) the other two could not say where the agent stood.
The wizard's place lived in the page (W134); a draft of the wizard's did not
know it was the wizard's (W135); what rested stood beside what lived (W136);
and JB, who had done nothing wrong, read "already exists", "nothing to cut",
"running" and "say yes" as walls (W124, W130, W131, W132).

LangGraph's own answer to this is Studio: a page that draws a compiled graph,
runs it with an input, shows the thread's state per node, lets a human edit
and fork, and holds at an interrupt. It is the right shape. It is the wrong
dependency: Studio is served from smith.langchain.com and needs a LangSmith
key; its local half, the Agent Server (`langgraph dev`, port 2024, a
`langgraph.json` map of graphs), is open but is a second kernel with its own
threads, runs, assistants, store and auth. Two kernels would be two truths
(rule 7). Fleet, the no-code builder, is a hosted product. So: **take Studio's
shape, not Studio.** The Workshop becomes the kernel's own Studio.

## What stood before this document (the honest ground, 2026-10-13)

- **The doors are whole.** `/drafts` · `/drafts/cut` · `/experiments` ·
  `/experiments/promote` · `/experiments/decline` · `/services` ·
  `/services/mcp` · `/crew` · `/ask/<id>` served every step of every walk on
  both kernels. Not one wound of W124–W136 was a door's; thirteen were the
  glass's, and the glass cured them.
- **The experiment gate works.** jonathan's candidate passed 1 of 1, the four
  reviewers signed, the leaning was promote — in two minutes, while the glass
  said "running". imp2's candidate failed its one case and the gate held it.
  The gate is the Studio's judge; it needs a face, not a change.
- **The import node runs a repository's LangGraph.** `operating.run_import`
  fetches the repository at its commit, imports `module:attr`, calls the
  compiled graph's `invoke` with the ask — dev universes only. THE ONE WALK
  Part 5 and the wizard's Part B proved it (imp answers from the repository's
  own code). What it does NOT do: read the compiled graph's shape. The canvas
  draws one block, `run · a repository's code`.
- **The Workshop agent has one hand.** Its binding gives it one tool, `draft`,
  told to call it ONCE with the whole declaration, forbidden to cut. It
  searches, explains, edits one open draft on the human's words. It has never
  been asked to make an agent from a brief. JB's untested use case stands
  untested.
- **The minds are seated.** opus (claude-opus-5-5) and fable (claude-fable-5-1)
  stand healthy in the Stable beside haiku; the MIND chip picks them.
- **The docs are on the shelf.** `langchain-docs` (https://docs.langchain.com/mcp:
  a search and a virtual filesystem of the guides) and `langchain-reference`
  (https://reference.langchain.com/mcp: the API reference by package, symbol
  and language) are registered through the toolkeeper's door and healthy. No
  template names their tools yet, so no body can use them — the role gate is
  the template, by law.
- **The wizard's state is this browser's** (W134, `orreth.wz.<person>`), not
  the ground's. A second browser, a second seat, or the Workshop agent cannot
  see where an agent stands in its making.
- **The rails are lists.** The shelf list is every craft by kind; the chat's
  residents rail is every body on the crew. At six agents JB scrolls; the
  firmware of the house (identity · security · critic · grader · the three
  keepers · mitl · echo · the workspace) stands in the same list as the agent
  he is making.

## The locks

### 1. The name and the road (JB's lock, 2026-10-13: "the kernel needs a Studio and that is our objective with Workshop")

THE STUDIO is not a new pull. It is the Workshop's name once four things are
true: an agent's making has ONE PLACE (the bench); the canvas draws the TRUE
graph and lights it as a run goes; the ladder is ONE WORD; and the Workshop
agent can MAKE IT ALL from a brief. The word "Workshop" stays in the glass
until the fourth is proven; the book and the demo turn then (the
release-alignment law). LangGraph is the graph language of the agents Orreth
hosts; the kernel is their hull, their gate, their record and their Studio.

### 2. The bench — one effort, one place (recommended)

- A **bench** is a named effort under a person's seat: the agent's name is
  the bench's name. Every draft files ON a bench (`spine_drafts.bench`, the
  next schema on both kernels; a draft with no bench is "loose", today's
  drafts). The wizard makes one bench per agent. "+ new draft" asks which
  bench, or loose.
- The bench holds **the agent's whole story in one row of the ground**:
  its drafts, its step in the making (NAME · GRAPH · GOLDEN · SAVE · CUT ·
  CARD · PROMOTE · JOINED — the wizard's place, W134's named half), its
  experiments by id, its lives (the trial lives and the seated ones), its
  wounds in plain words ("the golden set is on the shelf as version 2; the
  template stands unchanged — nothing to experiment on"). The glass reads it
  through one door, `GET /benches/<name>`; the feed's notices refresh it,
  the glass re-reads it on a clock (W133's law: a wait on the feed alone is a
  wait for ever).
- **The bench's card** is what the wizard's inspector becomes: the strip of
  steps, the drafts under it, the experiment's card inline, the lives, and
  the one next act. Clicking a draft on the bench opens it IN the bench; the
  draft knows its bench (W135 made whole).
- A bench **closes** when its agent is joined or let go; closed benches fold.
  Letting a bench go is ROUTINE (L1), as discard and decline are: its drafts
  discarded, its open experiment declined through the experiments' own word;
  what reached the shelf stays (a version is never deleted). THE WORD: the
  dispatcher already has a "bench" — the asks' waiting bench (W91's sweep,
  `bench.rs` · `dispatch.py`). That one is the kernel's; this one is the
  Workshop's, in its own table; the two never meet in code.

### 3. The rails reorganized (JB, 2026-10-13: "this will be a zoo when there are lots")

- **The left rail:** YOUR BENCHES first (open ones, each with its step and
  its drafts under it), then LOOSE DRAFTS, then THE SHELF by kind **folded
  with counts** (`templates · 14`, open on a click; retired folded under the
  kind, W136), then THE HOUSE — the firmware's crafts folded under one row.
  The filter box still finds anything by name across every fold.
- **The chat's residents rail:** the agents JB made first, then the house
  folded under one chip, trial lives at rest folded (W136), a body's state
  worn (alive · dormant · at rest).
- **The hold wears two faces (JB's lock, 2026-10-13: "a Yes on the card too").**
  The bench's card shows the hold with its own Yes and cancel; the chat shows
  the same hold pinned above the composer as today. Either face answers the
  ONE hold through the one door (`/ask/<id>/confirm`); the other face settles
  the moment it does (the feed's notice, or the card's own re-read — W133's
  law). The chat remains the record: every answer lands there as a line
  whichever face took the click. A Yes is a click on either face, never Enter.

### 4. The true graph — one graph language for an agent's work (recommended; JB: "REALLY focused on langchain/langgraph")

- **LangGraph code is the agent's graph.** A repository at a commit with an
  entry `module:attr` that is a compiled LangGraph (`import` today). Echo
  and think stay as the two built-ins the wizard shapes without code; a
  hand-authored declaration of several nodes (today's canvas) remains
  possible and is no longer the road for a real agent.
- **The body reads the compiled graph's shape** at import (what LangGraph
  gives as `graph.get_graph()` — the same nodes-and-edges JSON Studio draws
  from its `GET /assistants/{id}/graph`) and the kernel records it on the
  graph craft as `shape` beside `source`. The canvas draws it INSIDE the
  hull's ring: hear → recall → route → [the agent's own nodes] → the reply.
  Nothing the kernel does is hidden behind the agent's nodes (0010 §6's law).
- **A run lights the graph.** An ask sent from the bench to the open agent
  lights its nodes on the canvas as the steps land (the body already records
  every hop as a checkpoint; the reply's journey carries them). The hull's
  hold is Studio's interrupt; the session is Studio's thread. Time travel
  and state forks are named, not built.
- **Python body first, Rust parity after**, as every operating-state piece
  went; the fixture carries a graph with a shape.

### 4b. The graph model and the replay (JB's lock, 2026-10-13: "How do we make it fluid … 20 node flows linking 10 sub graphs, advanced recursion, routing … a graph model that can be linked and used in ui and in kernel … watch experiment graph")

Spoonful 9 drew two pictures and parsed a sentence: the declared graph
(orreth-graph/1, forward only, no nesting) above, the true graph (a flat
reading of LangGraph's JSON) below, and a reply's hops read back out of the
journey's words by a pattern. That is why it was not fluid, and why it
would get worse at twenty nodes and ten subgraphs. The lock:

- **One model.** A graph is `{entry, nodes: [{id, kind, words?, graph?}],
  edges: [{from, to, when?}]}` on both kernels and in the glass. A node may
  CONTAIN a graph. The declared graph keeps its format on the shelf
  (orreth-graph/1 is not reopened: forward only at the cut stays a rule on
  the craft); the true graph is read in the same vocabulary, so an import
  node contains its true graph and a LangGraph subgraph is a node of kind
  `graph` with its own graph inside (`get_graph(xray=True)` names nested
  nodes `parent:child`; the reading folds them). A loop in the code is a
  loop in the reading — the true graph may cycle; the drawer bounds it.
- **A hop is a record, not a sentence.** Every hop a compiled graph takes
  lands as a row — `spine_hops`: the ask it served (or the harness run and
  its case), the agent, the source, the node's full path, its namespace, its
  step, when it started, how long it took, whether it ended well, and a hash
  of what went in and out (LangGraph's debug stream gives every one). The
  body writes them as it writes its wear rows and the shape; both kernels
  read them. One fact per run, `orreth.hops.v1`, is the feed's pointer.
  `GET /hops?ask=…` and `GET /hops?run=…&case=…` serve the record; the ask
  view carries `hops`. The journey keeps its plain words for people. The
  experiment room's record is now a real replay: every case's hops.
- **One drawer.** The glass draws any graph of the model with one drawer:
  the layout fits the canvas (no scrollbar for the ordinary case); a node
  that contains a graph is drawn FOLDED ("N nodes inside · open") until
  opened, in place of the canvas, with a breadcrumb (lang1.v0 › run); the
  hull's ring is said once, where the agent's own nodes begin. A run
  overlay PLAYS the hops in order at their recorded pace — a reply's hops as
  they arrive, the chat's replies too, and any recorded run from the card
  ("replay case 1"), so "watch the experiment" is the trial's hops lighting
  on the bench's card. Twenty nodes and ten subgraphs stay twenty nodes
  until you look inside one.
- **Named, not built:** the hops publish WITH the reply (the body serves in
  one transaction) and play at their recorded pace — a hop published while
  the run is still going (a second line for the watch) is a later line;
  time travel and forks (Studio's) stay named.

### 5. One word to work — the ladder folded (recommended)

- **"put <name> to work"** on the bench (a button and the chat's word, one
  door): the kernel cuts what changed on the bench in order (graph · golden
  · template), skips what stands with the same bytes (W124's law, said as a
  line not a wall), opens the Experiment on the agent's cut, and lands the
  card on the bench. Every refusal of the walks becomes a line on the card:
  "the template stands unchanged — change what jonathan is for, or its
  graph, then put it to work again".
- **The Yes — ONE for the chain (JB's lock, 2026-10-13).** "put <name> to
  work" is one consequential act held at L2; the card names every cut it will
  make BEFORE the hold ("the graph jonathan.v0 as version 2 · the golden set
  stands · the agent jonathan as version 1 → the experiment"); the experiment
  is the gate that judges the result and the promotion is a second, separate
  Yes. Each cut inside the chain is still its own recorded fact on the shelf.
- "promote <name>" and "decline the <name> experiment" stay the chat's
  words; the bench's card carries both as buttons through the same doors.

### 6. The agent makes it all — fully auto (JB, 2026-10-13: "fully auto means I as human can draft a prompt around an Agent, Skill, Prompt, Bindings, Graphs … and the workshop agent will perform this for me")

- **The brief.** JB writes one prompt in the chat with the Workshop open:
  "make an agent called greeter that answers hello in three languages, with
  a golden case per language, on the opus stall". The Workshop agent, **on
  Opus by stock (JB's lock, 2026-10-13)** — the MIND chip switches it to
  Fable when JB wants the measure taken against it; haiku stays for reading
  and explaining — **plans the set** — template · graph · prompts · skills · bindings · golden set —
  **opens a bench**, calls `draft` ONCE PER CRAFT (the one-call rule lifted;
  the whole declaration each time, as now), says what it made in plain
  words, and files ONE held act: "put greeter to work", for JB's single Yes
  in the chat. The experiment judges it; JB promotes or declines.
- **What the agent may never do** (the three modes law): cut, promote, seat,
  register a source or a server, or answer a hold. Full auto is JB's dial of
  involvement, never the machine running alone; the consequence holds for a
  person in every mode.
- **Its hands:** `draft` (today), `bench` (open · read · let go), the docs
  tools (langchain-docs · langchain-reference, named in its template), the
  shelf's read (today). Its binding's prompt is turned from "edit the open
  draft on the human's words" to "make what the brief asks, on a bench, and
  hand it to the gate".
- **The measure (JB's phase objective):** how well Orreth makes greeter from
  the brief versus how well Fable would. The proof is one walk, SPEC-STUDIO-01
  Part B, done by the agent.

### 7. The docs live in the kernel (JB: "the kernel [should] always host langchain/graph docs so that agents and humans can query/search if intent and role support")

- **Today:** the two LangChain MCP servers on the shelf, healthy. **Next:**
  the librarian's, allen's and the workshop agent's templates name their
  tools (the role gate), so "librarian, what does LangGraph say about
  interrupts?" answers from the docs; a human's "ask the docs …" is the same
  door. AWS and Azure docs follow the same road when allen wakes.
- **Later:** a local mirror of the docs repository (public) indexed by the
  librarian for offline use, refreshed by a beat; the live servers stay the
  source of truth while they answer.

### 8. What stays as it is (so nothing is reopened by accident)

The kernel's one hold per consequential act, the Yes a click never Enter, the
chat its record (the card's Yes is a second face of the same hold, §3). Drafts ordinary and
under the person. The experiment as the agent's gate with its four reviewers
under their own names. Where the next life stands as the promotion's one
field. The hull's laws never in the agent's graph. The chat's words as the
record and the walker's way. The guide turning with the glass.

## The four answers (JB, 2026-10-13, through the question door)

1. **One Yes for "put to work"** — the chain is one consequential act at L2,
   the card naming every cut before the hold (§5). *Recommended, taken.*
2. **A Yes on the bench's card TOO** — the same hold, two faces; the chat the
   record (§3). *Fable recommended "point at the chat only"; JB chose the
   second face — a faster Workshop, one more door to keep honest: the card's
   Yes goes through the chat's own confirm door, never a second path (W118).*
3. **Opus by stock** for the making; Fable on the chip when the measure is
   taken (§6). *Recommended, taken.*
4. **"Studio" at spoonful 11** — the word changes when the fourth claim is
   proven; the book and the demo turn with it (§1). *Recommended, taken.*

## The build — four spoonfuls and the proof

The spine that survives all four is the wizard's own: a name, a source, a
golden set, a Yes, joined. No walk of 2026-10-12/13 is wasted.

1. **THE BENCH — BUILT 2026-10-13 on JB's word ("start spoonful 8").** The
   ground, schema 10 on both kernels: `spine_benches` (bench_id · scope ·
   person · name · words · step · body — the wizard's state · hold · state ·
   at · updated_at · closed_at) and `spine_drafts.bench`; the doors `GET
   /benches` (each whole: its drafts · its experiments since it opened · its
   seat) · `GET /benches/<name>` · `POST /benches` (open, or the open one of
   that name handed back) · `POST /benches/<name>` (the place kept: step ·
   body · hold · words) · `POST /benches/<name>/close` (routine: drafts
   discarded, the open experiment declined, closed) — all under the seat's
   person (AG-9); `orreth.bench.opened.v1` · `closed.v1` on the feed; the
   door name folds to `/benches/:id`. The glass: the rails of §3 (YOUR
   BENCHES with the drafts under each · LOOSE DRAFTS · THE SHELF folded by
   kind with counts · THE HOUSE folded; the chat's residents rail folds the
   house under one chip), the bench's card as the wizard's inspector with THE
   HOLD'S SECOND FACE (`holdRow` through `decide`, the chat's own confirm
   door; the chat's line the record; the face reads the outcome itself after
   a reload), the wizard's place read from the bench (`wizKeep` → `POST
   /benches/<name>` on every redraw, W134's browser copy retired; "+ new
   agent" is always a new bench; typing an open bench's name at NAME opens
   it; a bench closes itself when its agent joins), a draft opened in its
   bench (W135 whole), "+ new draft" picks its bench; the chat's words "open
   the <name> bench" · "my benches" · "let the <name> bench go". The guide
   0.13.0. Proofs: `test_benches.py` ×3 · `benches-v0.json` ×23 on both
   kernels (`bench_step` · `bench_name` · two `door_name`) · `schema-v0` at 10
   with 51 tables · `tests/benches.rs` (the doors on a lit kernel, AG-9) ·
   `test_guide.py` · `test_workshop.py`. NAMED, NOT BUILT: THE HOUSE is told
   by the crew's names and a worn count (a wearers' list on the shelf row
   would make it exact); the bench's card re-reads the experiment and the
   join on a clock (W133) but not the bench row itself — a second browser
   sees the step on the rail at the next load.
2. **THE TRUE GRAPH — BUILT 2026-10-13 on JB's word ("start spoonful 9").**
   The body reads the compiled graph's own shape when it runs an import node
   (`get_graph().to_json()`, the same JSON Studio draws) and records it ON
   THE SOURCE'S ROW (`spine_services.shape`, schema 11 on both kernels — the
   source, not the graph craft: a craft is pinned by its bytes and the shape
   is a reading, not a declaration; the body writes it as it writes its wear
   rows, both kernels read it); the run STREAMS (`stream_mode` updates +
   values) so every hop is named in the journey's word — "ran the imported
   graph lang-src at … — entry … · hops: greet → shout" — and the last state
   is the reply; a plain callable's shape is one node. The canvas draws THE
   TRUE GRAPH under the drawn graph for every import node, inside the hull's
   ring (hear → recall → route → [the graph] → the reply), start and end as
   ghosts, a conditional way out dashed; a reply's journey lights the hops it
   took (the chat's own replies too); the bench's JOINED step asks the agent
   through the chat's door. Laws on both kernels: `shape_of` ·
   `import_words(…, hops)`; fixture operating-v0 +4 (`op_shape` ×3 ·
   `op_import_hops`); `test_operating.py`: a real compiled LangGraph in a
   temp repository streams its hops and leaves its shape. The guide 0.13.1.
   NAMED, NOT BUILT: the shape is read at the first RUN, not at the source's
   registration (the kernel runs no code of the repository; the trial run or
   the first ask reads it); time travel and forks; Rust reads and records,
   the Python body alone runs the code (the body is Python by design).
2b. **THE GRAPH MODEL AND THE REPLAY (§4b) — JB's lock 2026-10-13, built
   before spoonful 10.** Schema 12 on both kernels: `spine_hops`. Laws on
   both kernels: `shape_of` folds subgraphs into nodes that contain a graph;
   fixture operating-v0 grows a subgraph case. The Python body streams
   LangGraph's debug stream with subgraphs, records every hop and one
   `orreth.hops.v1` fact per run; the harness names its run and case on the
   body so a trial's hops are the room's replay. Doors on both kernels:
   `GET /hops` (by ask, or by run and case) and `hops` on the ask view. The
   glass: one drawer for the one model — fit to the canvas, folded nodes
   that open with a breadcrumb, the run overlay that plays hops at their
   recorded pace from the feed, the ask view and the card's "replay case
   N". W143 (the true graph off the right edge) is cured by the fit.
3. **ONE WORD TO WORK.** `POST /benches/<name>/work` (ONE hold at L2, JB's
   lock): cuts in order, skips what stands, opens the experiment; the
   card's lines for every refusal. The chat's word and the bench's button,
   one door. Proofs: the experiments fixture grows the chain; a walk of the
   four refusals as lines.
4. **THE AGENT MAKES IT ALL.** The workshop binding turned (§6), the `bench`
   tool, the docs tools named in three templates, the one-call rule lifted,
   the agent on Opus; SPEC-STUDIO-01 Part B walked BY THE AGENT on JB's one
   brief and one Yes. The word Studio, if JB locks it, lands here with the
   book and the demo.

**The proof — SPEC-STUDIO-01** (to be written in `experience-specs.md` when
spoonful 1 opens): **Part A, by hand** — JB makes an agent on a bench through
the wizard, reloads, changes browsers, finds it where it stood, puts it to
work with one Yes, reads the card, promotes, asks it. **Part B, by the
agent** — JB writes one brief; the workshop agent on Opus makes the bench,
every craft, and files "put it to work"; JB's one Yes on either face; the
gate judges; JB promotes and asks the agent it made. The measure is JB's: how well Orreth did
it versus Fable.

## What we do NOT claim

- Studio's time travel, state forks and dataset experiments are not built;
  the hull's hold is the interrupt and the session the thread, and that is
  all the parity claimed.
- The compiled graph's shape is READ from LangGraph code, never authored on
  the canvas as code; drag-to-wire for code is not this document.
- The docs are LangChain's live servers; an offline mirror is named, not
  built; AWS and Azure docs wait for allen.
- Fully auto makes DRAFTS and files ONE held act; it never passes the gate
  or the promotion by itself (rule 11, the three modes law).
- The Rust kernel's parity on the bench and the shape lands inside each
  spoonful, not after the phase.

## What this document amends

- **0010 §6** — the graph: LangGraph code is the agent's graph language for
  a real agent; the declaration remains the kernel's RECORD of a graph's
  shape (drawn, pinned, worn), read from the code for an import. §8 — the
  Workshop's agent: from one hand on one draft to the maker of a bench.
  Spoonful 7's "named, not in this spoonful" rows land here (the wizard
  walked by the Workshop agent; the wizard's place on the ground).
- **0005** — Phase 8 grows THE STUDIO (spoonfuls 8–11 of the Workshop); W134's
  and W136's "named, not cured" halves point here.
- **The honest boundary** — the Workshop row gains the Studio's four claims
  as DESIGNED · OWED; the LangChain docs row as BUILT (the servers on the
  shelf) · OWED (the templates naming them).
- **The seeds** — security-and-architect (allen's docs tools); the Costs
  Panel unchanged.
- **The guide** — turns at each spoonful with the glass (JB's law).
