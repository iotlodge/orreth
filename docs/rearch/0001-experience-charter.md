# 0001 — The Experience Charter

**Status: LOCKED — JB approved 2026-09-16.** The first document of the new
canon. Distilled from the Experience Deep Dive (sessions 2026-09-14 and
2026-09-16, raw narration in `experience-capture.md`). The Experience
defines what Orreth must feel like; transport and agents are chosen to
serve it — never the other way around.

---

## What Orreth is

Orreth is an **interface and point of inference** for identities interacting
with an **autonomous governance execution state**. The whole model
compresses to one word: **identities**.

The kernel is Orreth's OS kernel: it serves needs and governs, beneath
everything, never seen directly. **The Operating State** is the running
whole — every known piece of config and deployment, alive. **The Bridge** is
the shell the human inhabits.

## The thesis

**The Experience is the felt surface of governance.** Every law has a
feeling, and the feeling is the proof the law exists: scope feels like axes
on your conversation; routing feels like soft journey text; risk feels like
a blast radius that never crosses your scope; recovery feels like a resident
coming back as itself; honesty feels like a disclosure before you say yes.
The human never sees the machinery — they feel its guarantees. One decoupled
Experience creates the Human Experience.

---

## Identities — the one shape

- A human arrives in two steps: **provisioned** an identity (enterprise
  identity stores supported — AWS/Azure), then **minted** an Orreth identity
  by becky.
- Humans and residents are digitally the **same construct**: a DID wearing a
  name, a profile, a persona. Residents feel human-like; their personas are
  adjustable by the human identity.
- The human's profile carries their **Orreth experience settings** (e.g.,
  chat open on load vs pulled).
- **Opt Out** is an operating state: the identity declines observation and
  metering — **never governance**. What it does and remembers stays inside
  that state forever; opting in is the human's act, met with the honest
  disclosure that nothing from the opt-out window comes along.

## The Bridge — the cockpit

Reference image: `tmp/ui bridge concept.png` (mockup by GPT-6 Astra; the
image is the spec). A starship-bridge interior: a framed **main view
window** onto the living universe (orrery / brain views), hull panels
carrying the pulls, warm light, glass.

- **No navigation, ever.** Login lands on the one landing page; everything
  the human will need can be seen, pulled, or clicked from it.
- **The main view window has lenses** on its sill: ORRERY | BRAIN — and
  (Fable's proposal, pending JB) **ATLAS** as the third: the strongest
  visualization of the Operating State's architecture, where clicking a box
  sets chat scope and time-scoping replays the architecture's evolution.
- **Pulls** are the focus areas. Each is themed to the bridge and can open
  into a window of its own with views across its categories.
- **[Esc] always returns to the top-level view** — recovery without hunting.
- The pulls: **Chat (Inference)** · **Workspace Engineering** ·
  **Monitoring** · **Gateways (LLMs)** · **Tools** · **Controls** ·
  **Crew/Agents** — plus the **Objectives** floor hatch (pending JB's
  verdict as the lifecycle band).

| Pull | What lives there |
|---|---|
| Chat (Inference) | The one conversation with the whole Operating State |
| Workspace Engineering | Authoring (agents, prompts, policies, skills, guardrails; factories; the MITL impact door) and the Graph Studio (prototype, watch, replay, tune-in-graph) — two views, one artifact shelf |
| Monitoring | Everything monitoring/testing, views per focus area — "if it's monitoring, it goes here" |
| Gateways | LLM providers and models |
| Tools | The tool estate |
| Controls | Configure and assign: kernel settings, artifact activation, dials |
| Crew/Agents | Resident and agent cards; install agent packages |

## The One Chat

One chat interface serves the entire Operating State. It slides down from
the ceiling, rolls over the landing page in its own small frame, a hint of
glass.

- **Scope rides the edges**: residents/agents by name on the right
  (dynamic — they change as the Operating State changes); universe /
  ecosystems / fields multi-select on the left; **includes** on top
  (critic, gap analyzer, planner, …); a clock assist for time. Both edges
  scroll and search as the universe scales.
- **Typed words equal every click**: "ask @allen, @becky to …" works without
  a toggle; "between X and Y" sets time from the ask itself.
- **Selected scope displays on and around the chat** — the human always sees
  the scope of applied inference. Default: current context.
- **Multi-select fans out**: the same request goes to every selected
  resident; each answers through its own role lens; results stay distinct
  (each downloadable) unless the human asks the chat to summarize them
  together. The human chooses how results are collected.
- **Results return in the chat**, labeled by producer. Documents and images
  click open larger in place (the pattern humans already know). Nothing ever
  requires going somewhere else.
- **Fire-and-continue**: submitting work never blocks the conversation;
  completion arrives as a soft notice; clicking it renders the result right
  there.
- **Every ask wears its journey**: soft text says where it went, who is
  fulfilling it, under what scope — and the reply says where it was
  fulfilled.
- **Clear-display never erases**: residents don't forget; recall of every
  acquired word is guaranteed. Every resident is chat-ready by birthright,
  and the human can always see a FULL reply.
- **Approvals live in the chat**: L1 = the ask · L2 = in-chat confirm
  ("are you sure…", cancel default, yes requires a deliberate click, never
  the return key) · L3 = MFA and/or master authority. The proof demand rises
  to meet the consequence.
- **MITL — Master Mind In the Loop** — is summonable (a soft toggle): a
  specialist of Orreth wearing the **Orreth ontology**, its own LLM brain,
  access to the repos Orreth sees, and **factories** that create skills,
  prompts, and agents whose results get leveraged. The "expected impact of
  this change?" door in Workspace Engineering routes through MITL.

## Scope and governance

- **Scope is a lens of identities, never of the kernel.** Humans and agents
  think in scope; the kernel governs uniformly to the extents of the
  deployed architecture. Scope rides the ask as intent; law is enforced
  everywhere the same.
- The Spacetime Window is **retired**: its powers are absorbed by the chat's
  scope axes, universal time scoping ("between X and Y", anywhere), and the
  Atlas. No surface exists for eye candy.
- Asks route by scope and capability — never to a catch-all resident.

## The lifecycle law — nothing runs unseen

**Nothing runs in Orreth — scheduled, asked, required, reflexed — without a
visible lifecycle**: in flight, queued, completed, with the full docs and
meta of the work reviewable. Soft small wording keeps the human informed;
the human never wonders what's happening. Operations and the felt experience
of the kernel are one continuity.

- **Every schedule lives in its runner**: automation appears in the resident
  that runs it — whether the human scheduled it, the role did, or the kernel
  requires it. Residents may schedule their own intentions, thoughts, and
  observations. **Kernel-critical schedules are immutable** — visible, never
  editable.
- **One state, many lenses**: a change made in any pull reflects
  immediately, appropriately, everywhere.
- **Standing test harnesses are essential**: the LLM-lifecycle watcher
  escalates provider retirements, can roll all agents to prevent incidents,
  and A/B tests each graph for compliant results — because models have
  produced wrong results with no announced change. Drift is caught by
  rehearsal, not luck.

## Placement, risk, and the metal

- **Placement is policy, never accident.** Co-located agents share one
  field/ecosystem; failure domains — the process AND the secret — nest
  inside scope boundaries. "Same secret" is a co-location.
- Dev and prod are **placement profiles** over the same logical world
  (dev-dense, prod-spread), declared as IaC, **cost-aware** against
  cloud-provider billing. allen · security · warden wear the loaded
  placement/risk policy: validate deploys, watch drift, treat violations as
  incidents, and reason what-if across co-location atop location.
- Identities outlive the metal: recovery is respawn, re-join as the same
  self, resume — with **declared RTOs verified by rehearsed drills**.
- The horizon: the metal understood as STATE becomes one target a global
  agentic fleet can optimize for cost and placement — under the same laws as
  everything else.

## Language and rendering

- **Every word for everyone.** All wording, results, inputs, and outputs are
  friendly and understandable by non-experts. Say what is happening AND what
  happens when you say yes. No themed jargon; the terminology reset is part
  of this charter. ("Stable" is retired; "the rig" is now the Operating
  State.)
- **Professional surfaces, always**: formatted editors, nicely rendered
  graphs and read views — never an ascii/graph mix.
- **Graphs are part of assertion**: results show flow, relationships, and
  origins as graphs, because federated risk, compute, and data demand it.
- A human's requested format is always honored.

## The Orreth Laws (seed)

1. **A human must approve the creation of new Observation and DID.**

(The list grows deliberately. The covenant becomes a loadable policy that
every agent — subagents included — and every resident must load; governance
is worn, not remembered.)

## How this charter is enforced

The **playwright agent** proves the Experience: specs are authored from JB's
narration (the human authors the experience; the agent enforces and
explores, filing "this felt wrong" friction reports — never authoring).
Every principle below maps to a walkable spec; screenshots and walk outputs
are captured once and serve three masters — experience proof, the new main's
docs, and the article carousel.

**The principles (P1–P18)** — the testable index, detailed in
`experience-capture.md`:
P1 one identity shape · P2 conversation is the workspace · P3 zero unneeded
steps · P4 Esc-rollback · P5 non-blocking, softly announced · P6 scope set
where intent forms · P7 every ask wears its journey · P8 no surface for eye
candy · P9 scope is a lens of identities · P10 placement is policy · P11
Opt Out declines the meter, never the law · P12 proof demand rises to meet
consequence · P13 nothing runs unseen · P14 one chat, every identity · P15
the bridge, not pages · P16 every schedule lives in its runner · P17 one
state, many lenses · P18 professional surfaces, plain words.

## Explicitly open

- Held narration: **Human↔Agent** · the **two-sided Resident** in deep form
  · the **agent / agent-on-behalf-of** dive (gates MITL toggle semantics and
  factories governance).
- Awaiting JB's verdict: the Objectives floor hatch as the lifecycle band ·
  the Atlas as the main window's third lens (vs its own pull) · aggregate
  schedule view in Monitoring · PULSE as the heartbeat ribbon · "every
  click has a sentence."
- To be designed against this charter: the transport (Kafka + RabbitMQ),
  the memory architecture (working / verbatim / semantic tiers), the
  LangGraph resident template, and the V1 build scope — all in their own
  dives.

## What this charter binds

The V1 razor: **everything Orreth needs to fulfill a human objective
multiple times, monitor it, provide analytics on it, and manage its
lifecycle.** Experience precedes transport precedes agents. Anything that
cannot be felt through the Bridge as this charter describes is not done —
however well it runs.
