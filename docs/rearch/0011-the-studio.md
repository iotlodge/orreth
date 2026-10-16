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

### 4c. The nested drawing and the kernel map (JB's lock, 2026-10-14: "would it be better to show the invoke container/wrapper as a box around the flow? … If the graph is indeed nested, why not represent it … Orreth as a kernel needs one of these that we can manage and adjust as kernel does")

Spoonful 9b gave the model and the record but drew a graph that contains a
graph as one folded block with a tiny "open ▸", opening into a separate
view under a breadcrumb. JB's walk of step 9 (W144): the one thing the
Workshop exists to make clear — the kernel invokes your graph inside its
own ring — was hidden behind that block; "until you told me how it worked,
I didn't actually understand that the kernel was invoking the graph from a
shipping/invoke single node graph". The lock, through the question door
(boxes inside boxes · a declaration both kernels serve, lit live · spoonful
9c now, before 10):

- **Boxes inside boxes.** One drawer draws any graph of the model as nested
  boxes: a node that contains a graph is a GROUP — laid out inside first,
  its box a big node in its parent's layout — folded to one block ("N
  nodes inside · open ▸") by a click on its header or by depth (deeper than
  the code's own nodes starts folded, so twenty nodes and ten subgraphs
  stay readable). Layers are the longest road from the entry with back
  edges dropped (a loop is drawn, never layered); a graph with no ways out
  is a list, its blocks stacked. Every block has an absolute place, so an
  edge may join any two blocks at any depth. The view pans by drag and
  zooms by wheel; "fit" shows the whole, scaled down never up (W143's law).
  The breadcrumb drill-in is retired.
- **The hull is the outer box.** The agent's canvas draws THE HULL as the
  outermost box with the kernel's own stages as blocks — hear → recall →
  route → work → the reply, the ring every body runs (`resident.py`'s
  graph) — and the agent's declared graph as the box inside its work
  stage; an import node is a box inside that, holding the code's own
  graph. The drawing IS the architecture: the kernel's laws live in the
  ring, never in your nodes. First sight centres your graph, readable, the
  ring peeking at both sides. A run lights the hops it took wherever they
  are nested, the ring lit with them, the reply closing it.
- **The kernel map.** The kernel has one of these of itself: HOW THE
  KERNEL WORKS is a DECLARATION in the one graph model —
  `spine/guide/kernel-map.v0.json`, `orreth-map/1`, kept beside the guide
  and turned with every spoonful that changes a part named on it — served
  by both kernels at `GET /map` (a seated read; law for law), each kernel
  adding its LIVE numbers: which kernel, its version and schema, how many
  doors it answers, how many topics the feed carries, how many tables the
  ground holds; the glass adds the residents seated now from the crew. The
  regions are boxes (YOU AND YOUR SEAT · THE DOORS · THE HULL · THE MINDS ·
  THE HOUSE · THE GROUND · THE WATCHES) and one ask's road is numbered
  across them, 1 → 7. It opens in a window over the Panel on "how the
  kernel works" in the chat and from HOW IT WORKS on the sill, drawn by the
  same drawer, so the kernel's picture of itself and the picture of an
  agent cannot drift apart. A static picture would lie within a week; this
  one is lit by the kernel it is drawn on.
- **Named, not built:** the map's road played as a run (the story's edges
  lit in order); a block on the map opening the organ's inspector; the
  spectator's photograph carrying a map.

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
- **Built 2026-10-16 (JB's word: "commit spoonful 10 with all of this, then
  start spoonful 11").** The `bench` tool on the door (`spine/tools.v0.json`,
  both kernels read it; `tools.py` runs it body-side): open · read · work ·
  close, routine as a draft's save is — `work` files THE KERNEL'S OWN hold,
  `bench.work` at L2 under the human's seat in the ask's session
  (`benches.hold_work`, the same hold the bench's PUT TO WORK button files;
  one door, W118's law), for the human's single Yes; a governing seat's word
  like the door's (a reading seat's ask is refused in words); a bench not
  whole refuses in words before any hold; filed, the tool tells the mind
  "never answer it". The `draft` tool gains `bench`: a draft files ON the
  human's open bench of that name (a bench not open refuses in words — the
  agent opens it first); both declarations re-pinned on purpose (fixture
  tools-v0). The workshop binding turned (0.2.0): the maker's charge with the
  road in order (open the bench · the graph · a prompt when words are needed ·
  the golden set under THE HARNESS'S LAW · the template · `work`) and every
  format spelled out; **`mind` by stock on the binding** — `claude-opus-5-5`,
  standard — read by the body over the workspace template's haiku (the
  Stable's assignment, the MIND chip, still wins); **`rounds` 12** — the
  binding's (or a template's) rounds replace the gateway's stock of three for
  the acting mind, the one-call rule lifted; the docs tools named on the door
  (`search-docs-by-lang-chain` · `query-docs-filesystem-docs-by-lang-chain` ·
  `search-api` · `get-symbol`) and on the librarian's template — an MCP-born
  tool a template names is offered only while its server stands on the shelf
  (the door's own law since P6.5), so a ground without the servers loses
  nothing and says nothing false; allen's template waits for allen. The
  Workshop's recall grows THE STABLE (the standing stalls by name with their
  model — a think node pins one, a template wears its model) and YOUR BENCHES
  (the human's open benches and what stands on each, whole or not), under
  the ask's person alone (AG-9); THE OPEN DRAFT says its bench. The glass:
  a `bench.work` hold under YOUR seat that this chat did not type is drawn in
  the chat as the agent's ("workshop made greeter on your brief · files put it
  to work · your Yes") — the held act's args carry `filed_by`, the maker's
  DID, so the record says who filed it and the glass never guesses (the
  bench's own button files none) — with the hold's own Yes and Cancel, and
  the bench's card carries its second face as before; the Workshop's first
  screen names the brief; the guide 0.16.0 teaches it (test_guide names the
  brief as a body's sentence — the wizard's parser is anchored to the line's
  end, so "make an agent called …" reaches the agent). Proof:
  `test_workshop.py` — the maker's road through the two tools with a draft
  refused before its bench is open, a golden set not whole then fixed, the
  recall of the stalls and the benches, ONE hold under the kernel's name in
  the human's session with the chain's three lines and nothing on the shelf,
  the Yes through the kernel's own settle, the three modes law at the tool
  (no human → nothing; a reading seat → refused in words); W148 found by it
  and cured on both kernels — the chain filed twice refuses in words while its
  hold awaits the human (one act, one hold). W149 found by JB's first walk of
  Part B the same day and cured on both kernels: the chain cuts the prompts
  and skills the graph names BEFORE the graph (the maker's `greeter-words`
  had stayed a draft and the trial ran without it); one the graph names that
  is neither drafted nor standing refuses in words. Walked by the agent on
  JB's brief 2026-10-16 — SPEC-STUDIO-01 Part B PASS through step 6 on the
  second run (the prompt first, the trial's replies labelled as the prompt
  asked, opus on the meter, promoted, "greeter, hello" answered in three
  languages); step 7, the measure, is JB's; W150 · W151 named for the glass;
  the word Studio turns on his word (§1).

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

### 9. What the walk asked for (JB, SPEC-STUDIO-01 step 11, 2026-10-14) — seeds, not built

Step 11 passed, validated on the ground. While it passed JB named three things a
kernel that deploys and governs agentic lives will need. Each is a spoonful of
its own on his word; none is built; the plan (0005) places them after sp11.

1. **Floors and rooms made from the card, through the architect.** The
   promotion's one field picks WHERE the next life stands. It should also be
   able to MAKE the place — "a new floor", "a room on floor X", "a new floor
   and a room on it" — and that making is a deployment the architect (allen,
   the cloud-architect firmware of 0037, not yet slotted in the plan) carries
   out on the kernel's word: the levels door declares the level, the architect
   lays what the level needs, the seat follows. Until allen is built the
   levels door alone (`/levels/open`) makes the place; the card's word for it
   is the seed. JB: "that would tell our firmware architect (allen) how to
   deploy."
2. **Criticality and classification on every agent.** A kernel deploying
   agentic lives in a bank, a hospital, a ministry, an army needs each
   agent's CRITICALITY (how much harm its failure does) and CLASSIFICATION
   (what it may read and say) as fields of its template: declared at the
   bench, read by the gate (the hold's level rises with criticality), by the
   reviewers (the security chip judges the diff against the classification),
   by the promotion (a classified agent stands only on a floor that carries
   the classification), and worn on the card and the roster. The template
   contract gains two fields (`criticality` · `classification`) with a closed
   vocabulary; a template without them wears the lowest. This touches the
   contract (`contracts/v0`, rule 9): a spoonful of its own, on JB's explicit
   word. JB: "it will be necessary to define the criticality and
   classification of any agent as an attribute/schema of any agent."
3. **Guardrails as a layer of the hull.** The ring already has the stage for
   it: between recall and work the hull may refuse, narrow or rewrite — the
   KERNEL'S guardrails, declared on the floor and worn by every body on it,
   outside any graph — layered over the ones a LangGraph engineers in its own
   code. Two layers the record tells apart: a hop refused by the hull's rail
   wears the rail's name; a hop refused inside the code wears the code's
   (W146 made every hop a row, so the record is ready for it). The seed names
   the stage and the record; the rails themselves (what they read, who
   declares them, how a floor's rails and a room's compose) are a design of
   their own. JB: "this would allow for guardrails to be layered (kernel
   guardrails vs those engineered into the langgraph itself)."

Taken the same day, in sp10 (W145 · W146 · sp10b in 0005): a new name at NAME
moves the effort; the hull's own hops; the chat's card picks where the next life
stands; the declaration coloured; the reviewers told the harness's law.

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
2c. **THE NESTED DRAWING AND THE KERNEL MAP (§4c) — JB's lock 2026-10-14,
   built the same day, before spoonful 10.** The glass: one drawer for the
   model as boxes inside boxes (`layoutNested` · `drawGraph` · the view that
   pans, zooms, fits and focuses), THE HULL as the agent's outer box
   (`hullGraph`), folds by header and by depth, the run lit through the
   boxes; the breadcrumb retired (W144). The kernel map as a declaration
   (`spine/guide/kernel-map.v0.json`) served at `GET /map` by both kernels
   with their live numbers (`map_view` · `map_door`; `map` a known door,
   fixture doors-v0), drawn in a window over the Panel on "how the kernel
   works" and from HOW IT WORKS on the sill; the guide 0.14.0;
   `test_map.py`. No schema change.
3. **ONE WORD TO WORK — BUILT 2026-10-14 on JB's word ("commit it and
   start spoonful 10").** `POST /benches/<name>/work` on both kernels: ONE
   hold at L2 (`bench.work`), a governing seat's word like the cut. The
   pure law `plan_work` (fixture benches-v0, `bench_work_plan` ×7) reads
   the bench against the shelf — graph · golden · template, in order: a
   changed draft is a cut as the next version, the same bytes a line
   ("stands — unchanged, skipped"), a craft standing on the shelf with no
   draft a line, and a missing graph · golden set · template draft, an
   unchanged template, or an experiment already running on the agent a
   refusal in words BEFORE any hold. The hold's text names every cut; the
   Yes runs the chain in the settle's one transaction — each cut its own
   fact (`crafts.cut`), the Experiment opened on the agent's own
   (`experiments.open_in`), the bench moved to THE CARD with its hold
   cleared. The glass: the wizard's step is PUT TO WORK (one button, the
   lines read on the bench), "put <name> to work" in the chat, one door
   (`putToWork`); the guide 0.15.0. Proofs: `test_benches.py` (the chain
   through the Yes, the refusals, the skip) · `tests/benches.rs` (the
   doors, 403 to a reading seat, the Yes through `/confirm`) · conformance
   on both kernels. Named, not built: the agent's own PUT TO WORK (sp11).
4. **THE AGENT MAKES IT ALL — BUILT 2026-10-16 on JB's word ("commit
   spoonful 10 with all of this, then start spoonful 11").** The workshop
   binding turned (§6), the `bench` tool, the `draft` tool filing on a bench,
   the docs tools named on the workshop and the librarian (allen's template
   waits for allen), the one-call rule lifted (the binding's rounds), the
   agent on Opus by stock (the binding's mind; the MIND chip still wins); the
   kernel's own `bench.work` hold filed by the agent under the human's seat
   and drawn in the chat as the agent's; the guide 0.16.0; `test_workshop.py`
   (the maker's proof); conformance on both kernels (tools-v0 re-pinned:
   `draft` · `bench`). **SPEC-STUDIO-01 Part B walked BY THE AGENT on JB's
   one brief and one Yes — PASS 2026-10-16 through step 6** (the first run
   found W149, cured the same day; step 7, the measure, is JB's; W150 · W151
   named for the glass) — the fourth claim is proven: the word Studio turns
   on JB's word, with the book and the demo (§1).

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
