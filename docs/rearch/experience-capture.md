# The Experience Deep Dive — capture

**Status:** LIVE CAPTURE — JB narrating, Fable capturing. This working document
accumulates the narration faithfully and will be distilled into the new canon's
0001 (the Experience Charter) when the dive completes. Nothing here is final
until JB confirms the read-back.

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
- **MITL**: which reading — L3 master authority, supervisory intelligence,
  or a third? Where does it sit relative to chat-native L1/L2, and what
  classes of acts summon it?
- **MFA**: mint-time only, or also step-up in-conversation for
  high-consequence acts (Fable proposes both, tiered by consequence class)?
- **Circular dependencies**: adopt async-only messaging with deploy-time
  cycle detection on synchronous call chains? (The deadlock disease we lived
  was synchronous circular waiting on one thread.)
- **RTO verification**: declared RTO per agent/placement profile, verified by
  rehearsed kill-drills (the Testament matured into standing practice) — who
  runs the drill, and where does the human see the result?

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

*More narration coming — held next: UI fluidity/continuity · Human↔Agent ·
the two-sided Resident Experience. Distillation into the Experience Charter
happens when JB closes the dive.*
