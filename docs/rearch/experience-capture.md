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
  enforced everywhere the same.

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

*More narration coming — sections append per exchange; distillation into the
Experience Charter happens when JB closes the dive.*
