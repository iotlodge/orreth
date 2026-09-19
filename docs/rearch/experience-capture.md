# The Experience Deep Dive — capture

**Status:** NARRATION PAUSED 2026-09-16 (JB: "until we experience after
build, that's all I can recall now") — **DISTILLED into
[`0001-experience-charter.md`](0001-experience-charter.md)**, which is the
document under JB's review. This capture remains the raw record; held
blocks (Human↔Agent · two-sided Resident deep form · agent-on-behalf-of)
reopen it when JB is ready.

**Context:** the 2026-09-14 halt and hard refactor. Order of the rearchitecture:
1. EXPERIENCE → 2. TRANSPORT → 3. AGENTS. The experience defines what the
system must feel like; transport and agents are chosen to serve it. What
survives untouched: the Rust plane, embedded firmware agents, layered
governance/scope/control, the DID / Governance-as-Architecture / IaC strategy,
the SDK.

---

## Session 1 — 2026-09-14

### The frame (JB's words, essence preserved)

> "I see Orreth as an **Interface and point of Inference** for humans/identities
> interacting with an **autonomous governance execution state**. Can summarize
> by saying **Identities**."

- The UI is not a viewer over the system — it IS the interface and the point of
  inference. The kernel behind it is an autonomous governance execution state.
- The whole model summarizes to one word: **Identities**.

### Identity — the symmetry law

- **Two-step human provisioning:** a human must first be **provisioned an
  identity** (with support for enterprise identity stores — AWS/Azure), and then
  to access Orreth that identity must be **minted an Orreth identity** — becky's
  role. Enterprise IdP → becky mints the DID.
- **Humans and Residents are digitally the same construct:** a **DID with a
  profile, a name, a persona**. Residents get names, profiles, and personas
  because JB wants them to *feel human-like* — yet **adjustable by the Human
  Identity**. One identity shape, two kinds of wearer.

### The flow law — zero unneeded steps

> "We humans are lazy — or more accurately put, don't like to do unneeded steps
> over and over — and in the flow between Resident and Human should not."

No step a human doesn't need. Repetition of avoidable steps is an experience
defect, full stop.

### Examples given (each becomes a testable spec)

1. **Keyboard as a first-class citizen.** Windows, modals, pulls, panels, views
   are already closeable — but keyboard shortcuts are not leveraged. A simple
   **[Esc] always linked to the top-level view** gives easy rollback in
   usability, versus mousing around different areas of the screen.
2. **Chat is the container — everything renders inline.** Resident chat windows
   work like the ChatGPT / Claude UIs: graphs, canvas, and other supporting
   solutions keep the experience **in the interface the human is in**. Never
   navigate away to see a result.
3. **Long-running work is fire-and-continue, with soft completion.** Kernel
   elements support long-running transactions. JB asks a resident to start
   something new **in the same window** as the request he just submitted; he is
   **notified softly** that "request XX is completed"; if he clicks it, **it
   renders right there** — never someplace else that has to be managed.

### Narration block 2 — scope, governance, and the ask's journey

**The failure (JB: "it's BOTH our faults"):**

- The governance/scope of floors (ecosystem, field) created a drift: things
  kept getting attached to the universe, or a favored field/ecosystem, while
  the UI stayed mixed — until eventually asks just went to librarian
  regardless of scope.
- This doesn't scale, and it **decouples the ask from its fulfillment** at the
  cost of process, time, and experience.
- Most times JB didn't even know where a request went — **no soft text saying
  what's happening**.

**Decision (proposed by JB, seconded by Fable): DROP THE SPACETIME WINDOW.**

- JB's reasoning: it adds complexity and overhead while serving as eye candy.
- Replacement — everything the window supports, achieved as **soft scope
  toggles on the axes of the chat interface** (three placements: inside ·
  alongside · floating top). Example flow: select a resident → chat opens →
  pick ecosystem(s) on the right edge, field(s) on the left, a clock icon for
  time — **or just say "between X and Y" in the ask itself**.
- Net effect: a neat way to set scope based on what you're getting ready to
  do, anywhere in Orreth.
- Fable's read on what must be preserved in the absorption: the window's one
  unique power was time (replay/scrub) — kept, as a universal time-scope axis
  on any surface; the structural world-map role is already served better by
  the Atlas. Nothing of value is lost.

**Held for later:** other screens (inbox, objective, observatory, …) as tabs
across the top is "yesterday's admin" — JB will describe how to make it more
immersive in a coming block.

### Narration block 3 — two clarifications

**The clock icon, precisely:** clicking it *helps the human set* a timeframe
(an assist for explicit setting). The chat, on its own, simply **extracts the
"between X and Y" as part of the ask** — time scoping is intrinsic to reading
the ask, not a synced widget trick. (How an agent implements the extraction is
out of scope for the experience discussion.)

**Kernel vs scope — the layer law (JB: "important"):**

> "Kernels don't think in scope — humans and agents do. Kernel is about
> serving needs, but when kernel governs, it governs to the extents of the
> Orreth deployed architecture. From the lens of the Kernel supporting
> things, the idea of Experience is distinct."

- **Scope is a lens of identities** — the way humans and agents aim intent,
  address, and filter.
- **The kernel serves needs and governs uniformly** — its governance boundary
  is the deployment itself, not a scope selection. It does not "think in"
  ecosystem/field; it enforces law everywhere, the same.
- **Experience is a distinct layer** from kernel mechanics — the kernel
  supports; the experience is where scope lives and is felt.

### Narration block 4 — placement, operating risk, blast radius (dug now at JB's call)

**P9 vetting note:** JB 99% positive P9 is correct — **"Opt Out" is an
operating state that must be vetted against it** (open question below).

**Why dig now — Operating Risk:** circular dependencies, RTO verification,
and kin must be considered while the physical/logical split is on the table.

**The frame:** *an identity is life*, and every action has a result — wanted
(good) or not wanted (a bad event / incident). Risk architecture exists to
bound the unwanted results.

**The placement stance (JB):** if multi-agent deployment to a single
operating instance (ARN / container / etc.) can be supported **while ensuring
rigid control, governance, and risk**, then we SHOULD support it.

**The blast-radius law (JB's rule):** a skill applied to allen must know that
if 4 distinct LangGraph agents run on container.foo, **they all have to be in
the same field and ecosystem** — co-location bounded by scope. At scale,
unbounded co-location becomes high risk (JB: "I've been doing this a long
time").

**E-RAG hindsight:** this model would have let us *visualize decoupled* yet
*run distinct graphs and logic layers on a single container in dev* — while
prod may choose not to follow the single-instance shape at all.

**Fable's read-back generalization (seconded in-session):** three concerns the
old build welded together must separate —
1. **Logical scope** — the identity's lens (P9);
2. **Governance** — uniform, the kernel's, everywhere the same;
3. **Physical placement** — an operational choice, governed by declared
   placement policy.
A floor used to be all three at once (a scope AND a governance boundary AND a
process). The weld is why dev couldn't be dense and prod couldn't be spread.
The generalized blast-radius law: **physical failure domains must nest inside
logical scope boundaries** — an instance-level incident may never cross more
scope than one field/ecosystem. Placement profiles become per-environment
declared IaC artifacts (dev-dense / prod-spread) over the SAME logical world;
allen, wearing a loaded placement/risk policy, validates deploys against the
affinity laws, watches placement drift, and treats a violation as an incident.
Honest naming of the old failure: it was not dense placement — it was **no
placement model at all**; one process wore every identity in the world.

### Narration block 5 — Opt Out defined, secrets as fate-sharing, cost-aware metal

**Opt Out (JB's definition — vets CLEAN against P9):**

- The identity **declines observation/metering — governance still applies.**
- Humans can still talk to residents in Opt Out, but **what those identities
  do and remember stays inside the scope of Opt Out.**
- **Opting back in requires the human to do it**, and the human must be told
  (a good experience in itself): **no memories from the opt-out timeframe
  will be touched** — "frankly it could be bad data and we wouldn't want it."
  Opt-out memories are quarantined to that state forever; opt-in imports
  nothing.
- P9 verdict: HOLDS — what is declined is observation/metering (lens-level);
  the kernel's uniform governance is never declined.

**Fate-sharing includes secrets (JB: it MUST):** "same secret" is a
co-location, same as "same container" — secrets in prod cause catastrophic
incidents from a simple secret change. For advanced agent *what-if*
scenarios, **allen, security, and warden** all need to understand
**co-location atop location**.

**The compounding move:** this enables an **"Advanced LangGraph Allen Cloud
Architect"** that can reason and gap-detect, wearing his **'orreth' skill —
which Fable will be creating**. JB: "one decoupled Experience creates the
Human Experience."

**Placement profiles CONFIRMED (Q3 = YES)**, extended with cost: the agentic
kernel and residents should **manage to optimal operating-cost states** by
bringing in **cloud-provider billing** and allocating across the metal —
placement is affinity-lawful AND cost-aware.

**Tests mandate:** when built, this gets tests. If Orreth is globally
scalable/deployable and does advanced analytics/processing, **it must
understand all possible states between what's experienced and the metal for
which it runs.**

**Held for coming blocks (JB thinking):** two more Experience perspectives —
(a) **UI Fluidity/continuity**; (b) **Human↔Agent and the Resident
Experience** — preview captured: residents are **2-sided**: what they do for
the human in *direct inference*, and what they do as their *job as
automation* — scheduled by the human (what the identity schedules), by role
(agent schedule), and by kernel (kernel-role required, as embedded firmware).
Full treatment may land in the AGENTS dive.

### Narration block 6 — MFA, MITL, and the metal-as-state article seed

**Two more experience elements (JB: they drive overall understanding and
strengthen governance):**

- **MFA — Multi-Factor Authentication.** Fable's proposed reading (pending
  JB's correction): MFA lives at two moments — (a) identity provisioning /
  becky's mint, and (b) **step-up verification woven into the conversation**
  when an act's consequence demands more than the L2 click — the interlock
  escalates in-flow: soft confirm → deliberate click → MFA challenge, by
  consequence class. Governance felt, never administered.
- **MITL — "Master Mind In the Loop."** Named by JB; definition pending. Two
  candidate readings for JB to pick or correct: (a) **the L3 tier** — a
  designated master authority (manager-profile / senior human via the
  enterprise identity layer) in the loop for highest-consequence decisions;
  (b) **a supervisory intelligence** — the machine's own master mind in the
  loop for fleet-level acts. Either way it slots above the chat-native L1/L2.

**The article seed — "the metal becomes one target" (JB's words, verbatim
essence, banked until the outward freeze lifts):**

> "Ability to implement a kernel to not only create rigid control and
> governance but create a substrate by which the monolithic METAL becomes
> 1 target (it's one when it's understood as STATE) by which an Agentic
> global fleet can implement self and learned optimization and cost
> states… that's almost the holy grail."

Fable's note on why it holds: the kernel's founding trick is reducing the
world to governed, signed STATE. Pointing that same trick at infrastructure
makes the metal just another governed domain — one addressable target — so a
global agentic fleet can pursue cost/placement optimization as an objective
like any other, under the same laws, with learned improvement. The article
writes itself from P9 + P10 + the billing feed.

### Narration block 7 — L3 settled, MITL defined, ontology + factories named

**L3 = MFA, in addition to manager authority ("or something").** The top
escalation tier can demand step-up proof (MFA) and/or a master authority's
word. The ladder now reads: L1 = the ask itself · L2 = in-chat confirm
(cancel default, deliberate click) · L3 = MFA and/or master authority.

**MITL, refined (JB: "almost dead on right"):** a **specialist of Orreth that
serves agents** — governance and real-world risk both demand it. Its makeup:

- the **Orreth ontology** (JB's name, for now, for what was called the
  'orreth skill') — deep knowledge of Orreth itself;
- **its own brain (LLM)**;
- **access to the repos seen by Orreth**, for deep investigations;
- creation powers: it can **create skills, prompts, and agents through a
  "factories" feature** — and the results get leveraged.

**The MITL toggle:** possibly a simple **soft toggle** on the interface —
summoning the Master Mind explicitly rather than weaving it in by context
inference. Simple, and it negates context-guessing.

**Held dive (JB named it):** *the experience of the agent, and
agent-on-behalf-of* — required to finish the MITL/toggle thinking; queued
for when ready (likely the AGENTS dive or its own).

**Fable's note:** MITL is the [self-delivery seed] maturing into a named
identity — a frontier-class specialist resident inside Orreth: ontology +
own brain + repo access + factories. The seed's "frontier mind crystallizes
skills for lesser minds" becomes MITL's factories feature.

---

## Session 2 — 2026-09-16

### Narration block 8 — UI fluidity & continuity: THE BRIDGE

**The frame:** the human relies on Residents/Agents to facilitate ALL requests
and work; the kernel governs and provides services to residents and agents;
the UI is where humans **lifecycle (CRUD) the config/settings** of the
services the kernel, residents, and agents provide.

**The cockpit — THE BRIDGE CONCEPT (reference: `tmp/ui bridge concept.png`,
mockup by GPT-6 Astra; JB: "I LOVE IT"; ceiling crop: chat_pull_area.png):**

The image IS the spec: a first-person starship-bridge interior. A large
framed **main view window** (JB: "really like the frame and window") looks
out on the living universe — constellation clusters per world wearing live
counts (`allen · 1a · 544m · 2t`, `charles · 1a · 1992m · 5t`, `retail · 1a ·
3503m · 1t`, …), orbital rings around a golden sun (`u:demo`), graph nebulae
on the flanks. The hull frame carries the pulls, themed to the bridge:

- **Top ceiling tab: PULSE** (and the ORRETH nameplate on the window frame);
  chat descends from the upper-right ceiling (the crop).
- **Left wall panel: INBOX** — wearing a badge count, a door with a handle.
- **Right wall panel: WORKSPACE** — matching door, small status light.
- **Window sill, centered: ORRERY | BRAIN** — the main window's view toggle.
- **Floor console hatch, center: OBJECTIVES** — the foundation underfoot.

**The no-navigation law:** upon login the human never needs to know where
something is — **everything they will need can be seen/pulled/clicked from
the landing page.** Pulls match the theme of the experience.

**Pull 1 · Chat (Inference) — the great simplification. ONE chat interface
for the entire operating state.** It slides down from the upper-right ceiling
and **rolls over the landing page like it's coming out of the ceiling**, with
its own small frame like the main view window and a hint of glass
transparency. Load behavior is a profile setting (display-on-load vs pulled)
— and generally **the human's profile carries their Orreth UX settings**.
The chat's four edges carry soft toggles/links:

- **Right edge:** residents/agents by name — DYNAMIC soft links that adapt as
  the live operating state changes; scroll/search as the universe scales.
- **Left edge:** universe / ecosystems / fields, **multi-select** (everything
  spacetime supported); scroll/search at scale.
- **Top edge:** the includes — **'critic', 'gap analyzer', 'planner'**, and
  others to be thought of.
- Typed words always equal clicks: "ask @allen, @becky to …" works without
  touching a toggle.
- Selected scope **displays on/around the chat** so the human clearly sees
  the scope of applied inference (default: universe level).

Results of ad-hoc live requests **return in the active chat**, clearly
labeled with which Resident/Agent produced them (one chat window, always);
produced artifacts are downloadable; documents/images click open **larger in
the chat's view-results area** — the ChatGPT/Cursor/Claude pattern humans
already know. Humans never go somewhere else to do these things.

**Clear-display ≠ erase.** Clearing the chat display never purges data — the
respective resident still recalls everything (residents don't forget). ⇒
**Every resident is inherently chat-ready** (JB: "sure doesn't feel like it
today"). (All agents LangGraph/LangChain — out of scope for this block.)

**Pull 2 · Engineering:** Agent, Prompt, Policy, Skill engineering — really
nice, clean surfaces, worked through **factories or direct edit**. The
impact button: while tuning a policy/prompt/skill, a professional
"what's the expected impact of this change?" door — Orreth answers in detail,
routed through the **MITL flow** (ontology + repo access → full scope of the
requested change). The place to create new guardrails, or edit and assign
existing ones.

**Pull 3 · Monitoring:** everything monitoring/testing, with views per area
of focus — Residents, Agents, Kernel, E-RAG… **"if it's monitoring, it goes
here."**

**Pull 4 · Workspaces (Studios):** deliberately limited to **graph
engineering** — watching or replaying work requests; tuning prompts, skills,
policies, personas **in association to the graph**.

**Pull 5 · Gateways (LLMs):** similar to now, themed better.
**Pull 6 · Tools (Farm):** similar to now, themed better.
**Pull 7 · Controls (configs):** governance-like, themed better; two focus
areas: **kernel settings** AND **artifacts** (policies, skills, prompts).
**Pull 8 · Crew/Agents:** resident and agent cards; the place to add new
Agent packages (e.g., a machine-learning agent that brings a studio which
resides in Workspaces).

**Pull mechanics:** each pull is a category (CRUD) focus area that can become
a **new window like the landing page** (as in the image), holding its own
views across its categories; every pull wears the bridge theme.

**Schedules — the continuity of the two-sided resident:** residents serve
human requests AND autonomously run role-specific automation (scheduled
jobs) in course of maintaining their role or serving a request. The law:
**every schedule shows up in the resident that runs it** — kernel automation
included; if the kernel needs automation, its schedule appears in the
resident that runs it, and **if it's critical to the kernel's
objectives/state, it is IMMUTABLE** (visible, never editable). Residents CAN
schedule their own intentions, thoughts, observations (monitoring, a report,
research…). CRUD on a schedule = continuity between operating state and what
the human sees.

**The standing example:** the LLM-lifecycle watcher (the resident formerly of
the "stable" — **that name is RETIRED going forward**): escalates when a
provider retires an LLM; can roll all agents to prevent incidents; and will
eventually **TEST the harness** — A/B test each graph for compliant/passing
results. Real-world threat on record: a GPT model suddenly produced
completely incorrect results **without** a noticed/released update — test
harnesses are essential to catch silent model drift.

**Rendering & language:** editors, graphs, and read views always
professional and nicely rendered in formatted editors (the ascii/graph mix
ends). JB is a massive graph believer: as running technology federates
risks/threats/compute/data, **results must show graphs as part of assertion**
— flow, relationships, origins. All wording, results, inputs, outputs
**friendly and understandable by everyone, not just experts** — describe what
is happening AND the outcome ("what happens when you say yes, in addition to
how it happens"). A human's requested format is always honored.

**THE LIFECYCLE LAW (the block's heart, JB's words):** when a human executes
an action in the cockpit, they **see and feel the lifecycle of the request**.
**Nothing runs in Orreth — scheduled, asked, required, reflexed — without a
way to see what's in flight, completed (with the full docs/meta of that work
reviewable), queued.** Soft small wording informs; the human never wonders
what's going on. The named wound: today there is NO real lifecycle of
events, no replays, no graph/result views — despite having the features —
**"NO CONTINUITY IN OPERATIONS to the Felt Experience of the Kernel."**
And continuity across pulls: **if something is updated in one pull, it
reflects immediately, appropriately, everywhere in Orreth.**

**Naming:** "stable" retired. The whole of the known config/deployment
(currently "the rig") needs a plain, unthemed name — JB himself said
"Orreth operating state"; Fable proposes adopting **the Operating State**.
No themed phrases; every word for everyone.

### Fable's additions to block 8 (offered in-session, pending JB)

1. **The bottom pull is the missing lifecycle surface.** The mock already
   says it: OBJECTIVES is the floor hatch — the foundation underfoot. Propose
   the bottom pull = **Objectives/Operations**: the live band of everything
   in flight, queued, completed, scheduled — the place the lifecycle law is
   FELT — with every row a door that renders its result in place. This also
   gives the V1 razor (fulfill/monitor/analytics/lifecycle an objective) its
   home surface.
2. **INBOX (left panel in the mock) = the awaiting-you pull.** L2/L3
   confirms, MITL escalations, and resident proposals that arrive while the
   human is away land as chat messages from the resident (one-chat law) AND
   accumulate under the INBOX badge — nothing awaiting a human is ever only
   a toast that scrolled away.
3. **Allocation sharpening (Engineering vs Controls vs Workspaces):** same
   artifacts, three lenses — **Engineering AUTHORS** (create/edit/impact),
   **Controls CONFIGURES/ASSIGNS** (what's active where; kernel settings;
   dials), **Workspaces works IN-GRAPH** (prototype/replay/tune in graph
   context). P17 keeps the three agreeing instantly. Needs JB's confirm.
4. **One aggregate schedule view** in Monitoring ("everything automated, one
   view", filterable) alongside the per-resident law — at hundreds of agents
   the human needs both lenses of the same records.
5. **Every click has a sentence.** Generalize the chat-toggle equivalence:
   anything clickable in the cockpit has a plain-words spoken equivalent,
   and chat is the command palette of the whole bridge.
6. **PULSE (top tab) = the universe's heartbeat** — proposal: the soft
   status ribbon where journey text and soft completions breathe, feeding
   the INBOX when something needs the human.

### Narration block 9 — corrections and locks on block 8

**Fable's addition #2 CORRECTED (JB caught the conflict):** L2 approval lives
**in the chat window itself** ("are you sure…", cancel default) — as declared
in block 7 — never in a separate INBOX surface. Reconciled: approvals happen
in chat, full stop; anything awaiting the human arrives as a chat message
with the interlock inline. The mock's INBOX door survives at most as a
**badge/counter that points INTO chat threads awaiting response** — a
pointer, never a second place where approvals live.

**Naming LOCKED:** the whole of the known config/deployment = **the
Operating State** (JB: yes). Framing: **the kernel is reflective of an OS
kernel** — Orreth kernel :: OS kernel, the Operating State :: the running
system, the bridge and its pulls :: the shell the human inhabits.

**Multi-select residents = FAN-OUT (new spec, JB's clarification):**
selecting more than one resident in the chat sends the **same request to
each**. Example: ask the security architect AND the identity architect to
check on something — **each applies its own role lens**. The human can
**download each distinct result**, and can also **ask the chat to summarize
the results together**. The Operating State must keep this experience
correct and fluid with **how the human wants to collect results** — distinct
or synthesized, their choice, in the one chat.

**Pulls merged (JB accepting the overlap):** Engineering + Workspaces become
one pull — working name **Workspace Engineering** — with allocation INSIDE
the pull delegated to Fable/us. Proposed internal views (Fable, pending JB):
**Author** (agents/prompts/policies/skills · factories · the MITL impact
door) · **Graph Studio** (prototype, watch, replay, tune-in-graph) ·
artifacts flow freely between the two views, and Controls remains the
separate configure/assign pull. The bridge now carries **seven pulls**:
Chat · Workspace Engineering · Monitoring · Gateways · Tools · Controls ·
Crew (+ the Objectives/Operations floor hatch, pending JB).

### Narration block 10 — the Atlas remembered

**JB (2026-09-16, post-distillation): the Atlas was forgotten — "maybe that
is a pull? That is the strongest visualization we have of the architecture
in the Operating State."**

**Fable's recommendation (pending JB):** not a pull — the **third lens of
the main view window: ORRERY | BRAIN | ATLAS** on the window sill. Pulls
are CRUD focus areas; the Atlas is the view of the whole — exactly what the
main window is for. Two continuities follow: (1) **every box a door becomes
every box an aim** — clicking an Atlas node sets chat scope (P6 made
physical; the main window is a scope selector); (2) **universal
time-scoping on the Atlas lens replays the architecture's evolution**,
completing the Spacetime Window's absorption. Fallback if JB prefers a
pull: a full Atlas window, reachable from the sill toggle — nothing lost.

### Open questions ledger

- ~~**Opt Out**~~ ANSWERED (block 5): declines observation/metering only;
  governance always applies; opt-out memories quarantined forever; opt-in is
  a human act with honest disclosure. P9 holds.
- ~~**Blast-radius rule precision**~~ ANSWERED (block 5): fate-sharing is
  process AND credentials — "same secret" is a co-location. allen · security
  · warden must understand co-location atop location.
- ~~**Placement profiles**~~ ANSWERED (block 5): YES — per-environment IaC
  artifacts over one logical world; extended to be cost-aware via
  cloud-provider billing.
- ~~**MITL**~~ ANSWERED (block 7): a specialist-of-Orreth identity (ontology
  + own LLM + repo access + factories), summonable — possibly via a soft
  MITL toggle. Remaining: toggle semantics + what the factories feature
  governs, held for the agent-experience dive.
- ~~**MFA**~~ ANSWERED (block 7): L3 = MFA and/or master authority; step-up
  tiering by consequence class stands as proposed.
- **Circular dependencies**: adopt async-only messaging with deploy-time
  cycle detection on synchronous call chains? (The deadlock disease we lived
  was synchronous circular waiting on one thread.)
- **RTO verification**: declared RTO per agent/placement profile, verified by
  rehearsed kill-drills (the Testament matured into standing practice) — who
  runs the drill, and where does the human see the result?
- **Block-8 additions — block 9 outcomes**: ~~INBOX as awaiting-you pull~~
  CORRECTED (L2 lives in chat; INBOX at most a badge into chat) ·
  ~~lens split~~ RESOLVED (pulls merged: Workspace Engineering; internal
  allocation delegated to Fable) · ~~Operating State name~~ LOCKED (yes; and
  kernel :: OS kernel framing). STILL OPEN: bottom pull =
  Objectives/Operations lifecycle band? · aggregate schedule view in
  Monitoring? · PULSE = heartbeat ribbon? · "every click has a sentence"?
- **Chat includes list**: 'critic', 'gap analyzer', 'planner' named — what
  else belongs on the top edge? (Fable to propose in charter distillation.)

### Principles Fable derives from session 1 (pending JB confirmation)

- **P1 · One identity shape.** Human or resident, an identity is DID + name +
  profile + persona. Humans arrive via enterprise IdP → becky mints; residents
  are born with theirs; humans may adjust resident personas.
- **P2 · The conversation is the workspace.** Chat is not a feature among rooms;
  it is the container in which results, graphs, canvases, and controls render
  inline.
- **P3 · Zero unneeded steps.** Any avoidable repeated step is a defect the
  playwright agent can file.
- **P4 · Keyboard-first rollback.** [Esc] is the universal "back to top level";
  a hand never has to leave the keyboard to recover the main view.
- **P5 · Non-blocking by default, softly announced.** Submitting work never
  blocks the conversation; completion arrives as a soft, in-place notice; the
  result opens where the human already is.
- **P6 · Scope is set where intent forms.** Scope lives on the conversation
  itself (axes/toggles), defaulting to the current context; words and toggles
  are two doors to one scope state — saying "between X and Y" visibly updates
  the toggles, and touching a toggle needs no words.
- **P7 · Every ask wears its journey.** Soft text always says what's
  happening: where the ask went, who is fulfilling it, under what scope — and
  the reply wears where it was fulfilled. The human never wonders where a
  request went. (Direct cure for the librarian-catch-all failure.)
- **P8 · No surface exists for eye candy.** Every view must earn its overhead
  by serving intent. The Spacetime Window is retired; its powers are absorbed
  by scope axes + universal time scoping + the Atlas.
- **P9 · Scope is a lens of identities, never of the kernel.** Humans and
  agents think in scope; the kernel serves needs and governs uniformly to the
  extents of the deployed architecture. Scope rides the ask as intent; law is
  enforced everywhere the same. (Vet "Opt Out" operating state against this.)
- **P10 · Placement is policy, never accident.** Physical placement is an
  operational choice governed by declared placement policy: co-located agents
  share one field/ecosystem (failure domains — process AND secret — nest
  inside scope boundaries); dev and prod are placement PROFILES over the same
  logical world, allocated cost-aware against cloud billing; allen · security
  · warden wear the loaded policy — validate deploys, watch drift, treat
  violations as incidents. Tested: Orreth must understand all states between
  what's experienced and the metal it runs on.
- **P11 · Opt Out declines the meter, never the law.** An identity in Opt Out
  is unobserved and unmetered but fully governed; what it does and remembers
  stays inside that state forever; opting in is the human's act, met with the
  honest disclosure that nothing from the opt-out window comes along.
- **P12 (forming) · The proof demand rises to meet the consequence.** The
  escalation ladder lives inside the conversation: L1 = the ask · L2 =
  in-chat confirm (cancel default, deliberate click) · L3 = MFA and/or master
  authority. MITL — the specialist-of-Orreth (ontology + own brain + repo
  access + factories) — is summonable, possibly by a soft toggle, wherever
  governance or risk wants a master mind in the loop.
- **P13 · Nothing runs unseen (the lifecycle law).** Nothing runs in Orreth —
  scheduled, asked, required, reflexed — without a visible lifecycle: in
  flight, queued, completed with full docs/meta reviewable. Soft small words
  keep the human informed; the human never wonders. Operations and the felt
  experience of the kernel are ONE continuity.
- **P14 · One chat, every identity.** A single chat serves the whole
  Operating State: scope on its edges (residents right, universe/eco/field
  left, includes top), typed words equal to every click, results returning
  in-chat labeled by their producer, artifacts enlarging in place,
  clear-display never erasing (recall stands). Every resident is chat-ready
  by birthright. **Multi-select fans out**: the same request goes to each
  selected resident, each answers through its own role lens, results stay
  distinct (each downloadable) unless the human asks the chat to summarize
  them together — the human chooses how results are collected. Everything
  awaiting the human — L2/L3 confirms included — arrives IN the chat.
- **P15 · The bridge, not pages.** Login lands on the one landing page —
  the framed main view onto the living universe; focus areas are themed
  pulls that can become windows of their own; navigation does not exist.
- **P16 · Every schedule lives in its runner.** Automation shows in the
  resident that runs it — human-scheduled, role-scheduled, and
  kernel-scheduled alike; residents may schedule their own intentions;
  kernel-critical schedules are immutable (visible, never editable). CRUD on
  a schedule is CRUD on the operating state.
- **P17 · One state, many lenses.** A change made in any pull reflects
  immediately and appropriately everywhere in Orreth.
- **P18 · Professional surfaces, plain words.** Editors, graphs, and read
  views always formatted and professional; results carry graphs as part of
  assertion (flow, relationships, origins); every word understandable by
  everyone — say what is happening AND what saying yes does; honor the
  human's requested format.

### Architectural implications noted for later dives (not designed here)

- Soft in-place completion notices ⇒ a **push channel to the UI** is a hard
  transport requirement (feeds dive 2).
- "Renders right there" for a request submitted minutes/hours ago ⇒ results
  must be addressable and re-renderable inline from the durable record ⇒
  memory tiers must serve inline rendering (feeds the memory revamp).
- Enterprise IdP support ahead of becky's mint ⇒ identity architecture gains a
  federation seam (AWS/Azure identity stores) in front of the existing DID
  machinery.
- Asks routed BY scope + capability — never a catch-all resident — with each
  routing step emitted as an event the UI renders as the soft journey text ⇒
  routing topology + journey events are named transport-dive inputs.
- "Between X and Y" as a universal time-scope axis ⇒ time scoping is a
  first-class query dimension on every surface, preserving spacetime replay
  without a dedicated window.
- P9 (scope = identities' lens, kernel governs uniformly) ⇒ scope becomes
  LOGICAL addressing carried on intent over ONE governed substrate — it stops
  being physical partitioning. The floors-as-separate-processes/stores pattern
  (the very thing the one worker polled 26 of) is on notice; to be validated
  with JB in the architecture/transport dives.

---

## Fable's mid-dive synthesis (after blocks 1–5, pending JB's read)

**Thesis: the Experience is the felt surface of governance.** Every law has a
feeling, and the feeling is the proof it exists: scope feels like axes on your
conversation; routing feels like soft journey text; risk feels like a blast
radius that can never cross your scope; recovery feels like a resident coming
back as itself; honesty feels like the opt-in disclosure. The decoupling
(scope from metal, observation from governance, placement from logic) is what
lets the felt layer stay simple — "one decoupled Experience creates the Human
Experience."

**The thread, top to bottom:** a human is an identity (IdP → becky's mint)
talking to identities of the same digital shape. The conversation is the
workspace; scope and time ride its axes, defaulting to context, settable by
words. Every ask wears its journey and never blocks the next one; results
render where the human already is; Esc always comes home. Beneath the glass,
asks route by scope + capability on the bus; the kernel governs uniformly no
matter which container in which region serves; placement policy — affinity
laws, secret-fate-sharing, cost-awareness — decides the metal; incidents are
bounded inside one scope; identities survive the metal's death within a
rehearsed RTO. The human never sees the machinery — they feel its guarantees.

---

## Session 3 — 2026-09-18 (before P4 opens; P3 the Bridge v0 whole)

### Narration block 9 — THE FEEL: workspaces, focus, firmware agents, sessions

**The frame (JB's words, essence preserved):** "Orreth architects experience
and governance for reproducible outcomes and human experience." Experiences
create feelings, and feelings drive effectiveness, ENGAGEMENT, and perceived
value — not the active sentiment an agent can read off inference, but the
**strategic** feeling: an overall perceived personal value. The old glass
lost it: click a resident on the left, cross the screen to chat, click a
governance floor to apply scope — "painful and non-intuitive," an admin
interface where humans had to know Orreth before they could use it, unclear
how the kernel remediates threats, unclear what interoperability and changes
do to the running state of the agents. "We're heading the right direction
now" — and we must NEVER lose focus on how humans feel using Orreth: easy to
understand and use, fluid handoffs between chat and pulls, agent involvement
and human manual involvement both natural.

**The Orreth Skill → factories → compartmentalized skills:** the Orreth
Skill (the ontology of Orreth, built in massive detail) is what a Factory
allocates from: Resident/Firmware-specific skills built for that agent, each
a versioned artifact that MITL, through the factories, can generate, assert,
and assure against (the ontology of Orreth in focus allocation to the
Operating State). Some firmware needs the whole thing; some needs parts —
and for security not every DID should know everything (compartmentalization).

**Resident Firmware Agents:** as already narrated — inference (chat) with the
human PLUS their own book of work — now also wearing a nice human feeling
("thank you, and continue to improve where applicable").

**Firmware Agents (NEW — JB asks for the Good and the BAD):** the same class
as residents EXCEPT they have NO name (no "becky") and are function-based:
planner, gap analysis, critic, grader, analysis, debater. What makes them
resident-class is the human's ability to call on them directly; otherwise
the kernel uses them when needed, AND they live inside the chat window. Use
case: some humans prefer to control planning, gap analysis, critique,
grading, analysis themselves — as a single step over one or many datasets
retrieved by the residents/agents they are chatting with. An agent is a
reproducible graph; its role in Orreth decides when it is mutable (Prod/Dev
hard separation; Resident vs Installed-Agent differences).

**Workspace firmware agents — the chat follows the focus:** a dedicated
firmware agent INSIDE each workspace (the pulls: floor, ceiling, sides).
When a workspace loads — the human asks for it in natural language in the
bridge chat, asks to "load agent x in workspace", or activates the pull —
THE SAME chat window takes on the properties of that workspace: the
workspace's firmware agent is loaded into the session and the bridge's
active scopes are dropped. To the human this is a change of focus: to
engineer/work/view whatever was sent to the workspace, or the inventory of
agents/templates to begin focused work. Manual vs assist: close the chat
inside the workspace → the human has chosen to work manually; leave it open
→ talk ONLY with that pull's firmware resident. It could well be the SAME
workspace firmware agent with DISTINCT policy, prompt, and skills per
workspace, facilitating CRUD there — "totally up to you, but it needs to be
mature." Inside the engineering workspace: handy soft links for MITL actions
— an "Agent Assistance" link on each kind of metadata an agent wears
(skills, tools, prompts, persona, policies), all linked to the agent's
versioning.

**PROD/DEV decoupling of authoring:** nothing unversioned (templates,
skills, prompts) inside Orreth's brain/knowledge — before a thing is
versioned INTO the kernel it is higher risk. While a human is creating or
updating an agent, that data stays inside the User Profile (S3/local) until
final submission cuts a new version; only then does it join the template
inventory for reuse, linked by version to any active operating instance.

**Memory as the enabler:** Orreth's memory looks up the context of a given
point of inference (chats and flows) — the source of interoperability that
other foundations lack.

**A law — eager for the next helpful step:** all residents pursue the next
helpful step. Ask to see a resident's graph in the chat, and the agent might
ask: "would you like me to open template #x in the workspace?"

**Immersive experiences (JB's examples):**
- A. The chat window is resizable — the upper-right corner is the origin
  (0,0), locked; the other corners resize.
- 1. Fluid chat ↔ pulls ("workspaces" = whatever pull is the focus of the
  objective/intention). On load, the chat is driven by the human selecting
  scope and any number of agents (typed "ask e:name1, e:name2" too — already
  there). The chat DYNAMICALLY ADJUSTS to the focus the human selects.
- 2. Human decouple, on our memory: select several residents/agents with
  scopes → each brings results to the same chat → click a firmware soft link
  ("plan", "gap analysis", critic, grade) → a new result → unselect those
  agents, select a new one → it sees the previous results in its read of the
  session and asks "how can I help here?" The kernel manages a CHAT SESSION
  that stores the session's artifacts/intelligence to carry work along. The
  chat fills with lots of things; JB works several things at once and wants
  no overlap of intelligence — WHAT IF a "new session" / "new topic" rolled
  a fresh chat, pushing the current one to an archived/working (not active)
  session the HUMAN can recall and continue? A "previous sessions" link; and
  by words: "list/show me previous sessions", "load session x". The human
  experience never leaves the chat window.

**The main bridge view — WOW me:** keep the brain view; upgrade the orrery
toward the mock (`tmp/ui bridge concept.png`) or take a new direction. The
residents circle the floors (keep — residents are critical elements of
global architecture governance) but there is no way yet to show the firmware
agents (planner, critic, gap finder, debater…). A reference mood image
arrived with this narration: a violet lattice of nodes and lines over a
starfield with a few amber stars. **MARKERS — a deep dive is owed:** every
Objective, Intention, Observation, Thought/Action sets a 'marker' attribute
on the event being actioned; Orreth's inherent ontology then captures
everything by dependency, starting from thoughts or from
objectives/intentions depending on the request's origin. Markers give the
main view many things to toggle on and off in the Monitoring view — the
main window goes full screen and serves as the LIVE OBSERVABILITY of the
Operating State.

**The workspace agent in Monitoring:** build the monitoring Orreth needs,
and let a workspace agent in that pull allow MITL to build NEW monitoring —
the agent acquires, builds, tests, routes for the human's approval, and
implements. "Orreth is different now: it works on behalf of humans to create
for humans."

**JB's close:** "Almost all the heavy lifting is done, I think. Keep it real,
friend, and help me architect the future."

---

*Block 9 LANDED (session 3). Vetted against 0001/0003/0004 by Fable the same
day; the distillation (a focus law, sessions as worldlines, firmware agents as
an agent kind, the draft shelf, the markers dive) lands in canon on JB's
lock.*


---

## Session 4 — 2026-09-19 (before P6 opens; P4 whole · P5 built · markers sp1 built)

### Narration block 11 — INTENT: the origin of work, the firmware-rails, and the chat that follows

**The frame (JB's words, essence preserved):** "Kernel Interoperability and
Fluid Experience Through Infinite Horizon Intentions" — one more, final,
round of deep thinking on Experience and Continuity of Experience, so that
we fully understand Orreth, interoperability with humans, how the outputs
and the work done in Orreth are managed, and — given where we are — the
rails embedded in the kernel. Intentions drive resident/agent automation
in the focused scaling and fulfillment of their Objectives. Make the chat
smoother and keep it THE primary interface for inference across "the
Intents of Orreth" (a marketing idea and an article), seamless and
immersive, driving the sought-after feeling.

**Two principles.** UI: **the Principle of Least Energy** = fluid
experience = immersion between the kernel's flow and the human's focus,
in chat mode. Kernel: **Naturally Occurring State — "State is an outcome
of applied Intent."** JB's line for Orreth: a Rust-based, global,
self-learning, polymorphic architecture-governance kernel for running
agentic DIDs through a governed-by-humans control interface — 1, 5, 50, or
50,000 — a single binary.

**The ontology — work and act.** Maturing the ontology around humans'
origin of *work* AND agents' origin of *act* creates an "intelligence
transformation": the ontology's intelligence state, from data to act,
across the whole scope of the kernel. This closes how the kernel works,
thinks, and manages governance and policy — robust, reusable kernel rails
for every capability. Humans act through **Intention**, which creates
Observations. Orreth today treats Objective as the top level; introduce
**human Intention as the topmost human end-to-end process** — Orreth
creates Objectives for each "project" under it. Think a major enterprise
program with many flows and interdependencies that need effective
governing of the program, its sub-projects, and their tasks.

**The ANALYZER pull (new).** How humans see the progress of an Intention,
its projects, its completed and in-flight graphs. Mostly a view; the one
invoke is "follow up on this by …". With nothing sent to it, the Analyzer
opens all active | completed Objectives and Intentions AND the agents'
own Intentions — **simple lookups, never calls or fan-outs**: the idea of
the kernel is to use its brain and memories to know, report, and replay
the state of anything, and reach out to a running agent only when it HAS
to. What separates Workspace Engineering from Analyze is **CUD**: in the
workspace the assistant acts on the template or graph; in Analyze the
assistant is a planner, critic, or gap analyzer helping review whatever
is being analyzed. Both are about CRUD over templates and active agent
graphs (the live view).

**Intention templates.** In Workshop Engineering, "create intention" is a
toggle that changes the pull's mode; the firmware agents engineer
workflows; the human creates LangGraphs for objectives OR selects an
active agent they made "consumable" (imported or created from the
workspace). Intention templates are LangGraphs with distinct capabilities
that run many other LangGraphs and flows; the **Intention architect**
(human, or human + agent) designs the right HITL / on-the-loop / LLM-in-
the-loop gates into the template.

**The chat IS the interface.** A human with a real thought to check on
uses Chat (the default mode). Other modes: **Objective** — saying "create
/ start objective" in the chat flips a soft toggle close to or inside the
chat; in Objective mode a second vertical menu shows the kernel-firmware
toggles, ready to assist in planning; the same for MITL. The experience
the human sees and feels adapts to their changing focus. **Close the chat
= remove "assist"**; whatever pull is open auto-expands. **CORRECTION
(JB):** the rearch images keep showing "Objectives" as if it were a pull —
"this tells me you might not fully understand the importance of the chat
window." EVERYTHING a human asks for is done in the chat; *what* they ask
invokes the respective level, flow, or graph inside the kernel; simple
soft toggles in and around the chat, or NLP entered into it, change what
and how. A clean chat also makes orreth-voice easier and really powerful.

**Three words.** **On Behalf Of:** an Intention or an Observation/Request
submitted by a human and *owned* by the agents of Orreth through the
networks, loops, flows, and rails embedded in the kernel — **"firmware-
rails"** as the name for each embedded loop provided as a feature of the
Operating Kernel (worth capturing). **Chat:** the human working with the
minds, firmware agents, and agents of the kernel to *assist* in whatever
they do — a guided, capable helper. **Work:** automation scheduled, or
resident/agent intentions aligned to a role in service of the kernel's
goals — outputs and results organized so that all viewable work comes
from requests, objectives, and intentions, **grouped by origin**.

**Infinite Horizon Intention.** Human Intention feeds a new, HIGHER
embedded loop — think a policy of "Run Rate", "Resiliency", "Security",
"Monitoring": an uplift to long-horizon agents, leveraging the firmware
agents and intentions, in a kernel whose agents are always improving in a
kernel that is always improving — "I mean, might have something here."

**JB's close:** "Keep me honest and real. If you can make it even better,
put it in. If it is crap, tell me why and how you can make it better." In
JB's brain it creates an adaptive state machine that can learn itself,
create itself, and do anything you ask or architect it to do while keeping
**Strategic Eternal Line-of-Sight on Business, Security, Resiliency,
Compliance, and COST objectives.** "Oh, and it's a single binary. 'mic
drop'."

### Fable's vet of block 11 (same day) and JB's locks

**What holds, and is mostly poured.** Intention above Objective is right,
and the rail exists: the marker registry (0006) already roots `intention`
with objectives under it — today it means a schedule row; block 11 widens
it to *any standing purpose* (a schedule is the smallest intention). "State
is an outcome of applied Intent" is how the spine already works: every
fact wears the marker of the intent it served, every view is a projection
of the ground, the pulls read snapshots and never fan out. "On behalf of"
and "firmware-rails" need no new build — the authority chain and the
marker's `by` say who asked and who owns; the rails are relay · dispatcher
· scheduler · serve, and block 11 names them. The correction is accepted:
block 8 placed an OBJECTIVES floor hatch pending JB's verdict and P3 built
it as the band; the verdict is in — **the hatch is the ANALYZER**.

**Where Fable pushed back (ratified).** Chat *modes* are the one shape that
fights least energy: a hidden mode, soft-toggled or inferred from "create
objective", means a mis-read silently changes what the kernel does with
the words, and the human must know the mode to predict the outcome. Better
and cheaper: **there are no modes — the ask wears its kind** (the kernel
already mints a marker on every ask): the typed words propose the kind as
a chip before send, one click or one word flips it, the marker is minted
with the ask, and the interest law wakes the planner or the intention
architect — JB's "second vertical menu of firmware toggles" *is* the
INCLUDES strip showing who is interested. Same feel, zero new UI state,
auditable, voice-ready. Intention templates are real but sequenced under
the razor: no graph editor — the first templates are **declarations** like
the bindings, cut from the draft shelf; "LangGraphs that run LangGraphs"
is the intent loop itself (one engine, 0040's law). One ontology
correction: observations are born from *acts*, not from intentions — the
loop reads Intent → Objective → Act → Observation → Improvement, and the
intention reads observations to plan its next objective (what the registry
already encodes).

**Where Fable kept it honest.** *Single binary* and *Rust-based* are not
what we have: the spine is Python on Postgres · RabbitMQ · Kafka; the Rust
plane is the old world, sacred and untouched. The laws being poured are
language-independent and a Rust kernel could carry them later — but the
honest boundary cannot say "single binary" today, and the marketing line
must not until it is true; the honest end shape is one kernel that governs
and residents as processes it spawns. *Self-learning* is real only under a
human cut: improvement marker → critic → a proposed change on the draft
shelf → the human cuts the version (rule 11; the graded-learning
guardrail) — "self-improving under human cut" is the stronger enterprise
claim anyway. The Infinite Horizon Intention, made concrete: five standing
kernel intentions on the ground — Business · Security · Resiliency ·
Compliance · Cost — each with interests, a planner, and a stop; the first
wired is the one the kernel already breathes.

**JB's four locks (AskUserQuestion, 2026-09-19):**
1. **The floor hatch is the ANALYZER, grouped by origin** — intentions,
   objectives, thoughts, and acts, in flight and completed, read from the
   ground; the MARKERS view moves in from Monitoring; the one invoke is
   "follow up on this by …" in the chat.
2. **The ask wears its kind** — no mode state; the chip before send; the
   marker minted with the ask; the interest law re-dresses the chat.
3. **Widen `intention`; the first Infinite Horizon Intention is
   Resiliency** — an intention is a record (words · serves · interests ·
   planner · cadence · gates · stop); the intent loop is the fifth
   firmware-rail; a red watch births an objective under Resiliency.
4. **Canon now, then intent sp1 before P6** — 0001 (P22–P25), 0004 (the
   rails and the loop), 0007 (the dive); then build.

**Seeds recorded:** "Intents of Orreth" (article + marketing line — the
one chat across every intent) · orreth-voice (V2; P23 makes it a voice
over the same chip, no toggles to speak).

---

*Block 11 LANDED (session 4). Vetted against 0001/0004/0006 and the code
(markers.py · scheduler.py · dispatch.py · the glass) by Fable the same
day; the distillation (P22–P25, the firmware-rails and the intent loop,
the Analyzer, the 0007 dive) lands in canon on JB's lock.*
