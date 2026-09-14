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

### Architectural implications noted for later dives (not designed here)

- Soft in-place completion notices ⇒ a **push channel to the UI** is a hard
  transport requirement (feeds dive 2).
- "Renders right there" for a request submitted minutes/hours ago ⇒ results
  must be addressable and re-renderable inline from the durable record ⇒
  memory tiers must serve inline rendering (feeds the memory revamp).
- Enterprise IdP support ahead of becky's mint ⇒ identity architecture gains a
  federation seam (AWS/Azure identity stores) in front of the existing DID
  machinery.

---

*More narration coming — sections append per exchange; distillation into the
Experience Charter happens when JB closes the dive.*
