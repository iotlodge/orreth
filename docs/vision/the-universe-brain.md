# The Universe Brain
### Memory, the Librarian, the Human, and the Orreth-Agent — the closed loop

*Private vision artifact. Captured live 2026-07-10 from JB's dialog (the deep design
session: "Memory, The Librarian, The Human, and the Orreth-Agent"). **Drop complete**
(JB: "I'm sure I missed something" — held open for his corrections before any design
begins). Scribe: Fable 5 (claude-fable-5). Companion to `the-knowledge-loop.md`,
`orreth-agent-the-chassis.md`, and the 2026-07-07 drops (multiverse · thought.graph ·
nervous system). Questions for JB are gathered at the bottom.*

---

## 1. The closed loop, and where a memory is born

- **Orreth is a closed-loop architecture**: operating ecosystems built on closed
  loops over the **Protected/Governed Memory of the Universe**. The memory is the
  loop's substrate; nothing operates outside it.
- **Memories have layers — Universe, Ecosystem, Field — set by the input layer.**
  A record belongs to the layer where the inserting agent (or human, via a resident)
  wrote it. **Time does the rest**: once inserted, the existing machinery — the
  metabolism (0003), the rise, retention per class, the two clocks (0004) — carries
  the record through its life. Placement is a birth fact; lifecycle is physics.

## 2. The Memory Construct — delegated to Fable 5, with constraints

JB's delegation, verbatim in spirit: *"THIS IS UP TO YOU when you fully understand
how data is Stored, Accessed, and Used across the Universe. Entirely up to you — if
you need 1, 2, 3 database architectures to support it, do it."*

The constraints that bound the delegation:

- **Deployability is a design input, not an afterthought**: think IaC and real-world
  deployments from the first sketch. *Never design what cannot deploy or operate
  **federated*** — tiers on separate hosts/accounts/regions must remain first-class
  (0000 §1's layered-not-merged rule; JB closed the drop naming a universe "spread
  all over the world").
- **The objective is FAST access across the Universe** — research, design, and
  create whatever storage/index/replication shapes that requires.
- **Partitioned memory is a requirement, not an optimization**: some record classes
  (e.g., transaction data) must be readable only by authorized agents — the
  partition is an authorization boundary that the storage design must honor.
- Everything already promised still binds: append-only, content-addressed,
  DID-signed, tenant-isolated, budget-gated, uniform refusal (covenant rules 4, 6, 8).

*(Status: research assignment accepted; design begins only after JB reviews this
capture.)*

## 3. The Librarian — the human's counterpart inside the universe

- **The Librarian is the Human of the Universe** — and the most knowledgeable
  Resident at any floor. It interacts with three constituencies: **other Agents, the
  data, and the Human.** Humans do NOT input or extract data anywhere in the
  universe — all data movement is by residents, and the knowledge resident is the
  Librarian. (The Parlor law, 0020, universalized into a single named organ.)
- **The Universe-floor Librarian sees ALL data — regardless of opt-in or opt-out.**
  *(Corrected by JB 2026-07-10, second pass.)* Opt-out changes the **mechanism and
  residency**, never the access: if a Field or Ecosystem opts out (many use cases
  where you wouldn't want results residing at Universe), its data does not flow up —
  the Universe Librarian instead goes **Librarian-to-Librarian to pull it on
  request**. **Fields and ecosystems can NEVER refuse requested data to the
  Librarian.** The pairing is the governed floor: total visibility is safe
  *because* the Librarian can deliver nothing alone — all-seeing, zero levers.
- **One Librarian, confirmed by identity; only the scope differs.** The Librarian at
  the ecosystem or field is *the same* Librarian — same identity — authorized
  differently. The difference between Librarians is never who they are; it is what
  their seat lets them know. *(Mirrors becky's root→leaf delegation chain, 0006 §1 —
  same self, attenuated authority.)*
- **The self-dialog (the federation mechanism):** the Human asks the Librarian in
  the **Universe view** — full view of memory — about all or any element of the
  universe. When the Universe Librarian lacks access (**time-bound** or
  **opt-out**), it engages **LIBRARIAN — itself — at the scope it cannot directly
  read**. Like talking to yourself: the same mind, but what it holds in memory at
  that seat produces a different answer, for lack of the universe's correlative
  material. Answers compose upward; **raw data never crosses the wall** — a synapse,
  not a hole (the nervous-system drop, 2026-07-07, now mechanized through one
  identity).
- **Opt-in / opt-out is governed and bounded:**
  - An Ecosystem **may opt out of exchange** — diaries and future experiential
    classes are in scope for opt-out.
  - **NEVER opt-out-able**: cost, token, performance, and other operational or
    security events. These **always flow up and escalate accordingly**. Two lanes:
    the mandatory operational/security lane (floors — 0019's universal meter,
    vigil's signals) and the optional experiential/knowledge lane (the exchange).
  - **Console build item:** opt-in/out configuration UI per ecosystem/field.
- **GOVERNANCE — the Librarian has NO change capability.** All knowledge, zero
  levers. The Librarian alone can deliver no change of any kind. A human may hand a
  change *request* to the Librarian, but the Librarian **hands it to the specific
  resident that owns that change** (becky for identity, charlotte for the farm, ada
  for the stable, …). Knowledge and power are structurally separated — the same
  posture as vigil's detect-never-enforce (0013), applied to the knowing organ.
- **vigil watches the Librarian** *(JB lock, 2026-07-10)*: the warden watches what
  the Librarian does. Every Librarian read — above all the self-dialog pulls across
  opted-out walls — is a signed access record under vigil's eye. The organ that
  sees everything is itself the most-watched thing in the universe.

## 4. The floor knowledge-request loop — agents ask their floor

- **By design, when a Resident or Workforce agent lacks information it needs, it
  "requests" to the Floor it resides on.** The Floor's residents **analyze the
  request**; if **low risk**, they can obtain the knowledge and put it **into the
  Floor's memory**.
- **Roll-up follows the exchange rules**: if the floor is opted in, the acquired
  knowledge eventually rolls up — *unless it started at the universe level* (born at
  the apex, already there; nothing to rise).
- *(Relation to canon: this generalizes the parked-intent circuit — 0015's
  park → librarian → retry was failure-driven; this is **need-driven**: an agent may
  ask before it fails. The risk analysis at the floor is the governance gate on
  acquisition; higher-risk requests presumably escalate rather than auto-acquire.)*

## 5. The Human Profile — a live profile, co-authored with the Librarian

- **The Universe maintains LIVE PROFILES of its operating Human** (JB, in this
  universe; every build-your-own-universe creator in theirs). **Critical for the
  "my second brain" use case.**
- In memory there is a **'creator' profile** (name open) that **matches the Human
  Identity using the Universe** — bound to the human's DID (0006 human enrollment).
- **Both the Human and the Librarian work to create a detailed profile of the Human
  as time progresses** — so the Universe always understands the human and can
  **personalize the experience across the universe** whenever the human interacts
  with any resident.
- **The human may update it directly, but the expectation is the Librarian
  maintains and alters it as events occur.** The profile is living memory, not a
  settings page — the Librarian is its steward, the human its subject and editor.

## 6. Markers — understanding 100% of change

- **The requirement: the Universe understands 100% of change.** Anything an agent
  *achieves* in an objective/intent **is a change**. Anything the human says to
  remember, or a Resident considers a Memorable event, **gets a marker.**
- **Markers are placed in memories** as Diaries and Humans communicate with
  Residents — and when **security finds something strange** (vigil's findings are
  marker-worthy events too).
- **Two grading families sketched by JB (naming open):**
  - **Change severity** — low · medium · high · critical — for changes made by an
    agent *or* a human.
  - **Life events** — minor · major · substantial — for the human-meaningful
    moments (the second-brain axis).
- **HITL governance is honored, two-stage:** where governance says HITL is
  required, it holds. **When the human asks, that IS the HITL on the intent — but
  the plan still needs approval.** Asking authorizes the *pursuit*; the *plan of
  change* is approved separately (0012's staged escalations; 0008's lane-routed
  change flow).
- **The second-brain payoff:** marked memories enable comparing and reasoning over
  previous decisions — a psychologist skill, decision retrospectives — *the second
  brain would truly understand you.*
- *(Relation to canon: "100% of change" is the census-not-sampling posture of
  the-first-questions.md applied to memory itself; markers ride the
  annotate-never-rewrite grain — a marker should be a signed annotation deriving
  from the marked record, never a mutation of it.)*

## 7. The Orreth Agent — the fingertip of Objective and Intent

**The closing frame: at the fingertip is the Orreth Agent (the prototype).**

- **Implementation latitude:** may start with LangGraph so input/output nodes carry
  security/governance from day one, or build an original reproducible/deterministic
  flow. The requirement is the properties, not the framework.
- **No Field, no action.** If a human spawns an Orreth agent and there is no Field
  to attach to, **it does nothing — by design (for now)**. The agent *requires a
  field* to receive its Objective/Intent **and the data needed to achieve it**. All
  information comes from the Universe it is attached to. An unattached agent is
  inert: no seat, no purpose, no data, no act. *(The attachment thesis completed:
  the process was never the life — and now the loop is not even the mission. The
  universe is.)*
- **The Universe construct IS the agent's node graph.** The universe architecture is
  LAYERED, and the layers are workflow seats: **Project Management, Product
  Development, Enterprise Architecture, Business Intelligence are Universe-level
  workflows** — the kind that take many intents/objectives (detailed planning,
  execution and delivery order, dependency management, …).
- **The agent is a canned loop** that receives **instructions, review, grading, and
  completion confirmation via the universe** — exactly like today's complex
  LangGraph workflows where each task moves up a layer to a node with a wider view
  or different purpose. **Our Universe allows as many layers to roll up as needed.**
- **The worked example — "build me a Product that does FOO":**
  - The Universe feeds the request into a product-designing workflow — but because
    **Agents do EVERYTHING in the universe**, the request fans into many
    sub-projects: end-to-end testing, **IaC (after asking where to deploy — a HITL
    question inside the flow)**, a test environment, a release pipeline,
    monitoring, telemetry — and transaction data, which lands in memory
    **partitioned**, because not every agent is authorized to see it.
  - **A field, an ecosystem, or the universe itself can be a NODE** for the
    original Objective/Intent — executed at the bottom by **fingertip agents fed
    only enough information to achieve the sliver of work assigned**, reporting
    back up to the right level for accuracy/approval against the original
    objective.
  - **Cross-ecosystem dispatch** *(added by JB, second pass)*: whatever level the
    orchestration occurs at **can send a sub-objective/intent into another
    Ecosystem/Field** to perform the action. Example: the universe has a custom
    **Machine Learning Ecosystem**, and the Product needs ML as part of its
    delivery — the ML sub-objective rides into that ecosystem's seats. Specialist
    ecosystems are callable organs of any sufficiently-entitled orchestration.
  - **The big picture stays higher in the stack** — planning, strategy, step
    creation live up there. The fingertip never holds the whole.
  - The Orreth agent uses **local memory during execution**, but **the Field or
    above ensures delivery is correct.**
- **JB's own analogy:** *"kind of like how YOU operate"* — an orchestrator holding
  the big picture, spawning scoped workers with slivers of context, reviewing what
  returns — **but across a closed-loop universe that might be spread all over the
  world.**
- *(Relation to canon: this is the thought.graph (2026-07-07) made concrete — nodes
  with altitude are now seats of the universe itself; "remote-controlled at the
  thought of intent and objective" means the plan/review/grade organs live in the
  tiers, and the chassis at the fingertip executes. Least-privilege attention,
  promoted from a loop property (0015) to the organizing principle of work itself.)*

## 8. The Console — resident workspaces

- The parlor dialog grows the spacetime window's move: **pull the dialog to full
  screen**. Full screen is the resident's **workspace** — room for toggles and
  built-in actions the resident wants to expose, and room for the agent (the
  Librarian, in the driving use case) to generate **rich output: charts, images,
  formatted documents.**
- **Each resident gets a workspace as it needs it** — the calling card (0020 §2)
  presumably grows to declare it, keeping the glass generic and the resident the
  author of its own room.

## 9. Factories — the improvement engine for skills and prompts

- **The intent of factories (0011) is to build and maintain skills and prompts.**
- **One agent is always improving them** — learning from failed/successful jobs —
  **part of distill and RL.** The factory is not only where incarnations are
  stamped; it is where the universe's behavioral assets are continuously refined
  from outcome evidence (0005's rollups feeding an improvement loop).

## 10. The frontier frame & the reference images (JB, closing pass 2026-07-10)

- **Core objective, restated:** the ability to create *a Universe of anything
  agentic* that governs and protects its agents and data — **scoped and scored
  data.** Orreth must process incoming data of three ingress classes: **knowledge
  requests · agent results · what humans send to the Librarian.**
- **The frontier claim:** a global brain that forever increases skills, knowledge,
  and abilities through the **Universe as a Graph Intent** — a graph that executes
  thoughts of intent to achieve local and project objectives. **Jobs can live
  forever** (standing objectives: monitor all products, run risk assessments,
  never "done" — only beating). Change reporting: every write is already on the
  record; the *grading* of change (markers, §6) is what completes the 100% claim.
- **The umbrella (image 2):** Orreth is attempting to **BE the umbrella** — and
  **the Librarian is the AI in the umbrella** (the general-intelligence surface
  humans and agents meet). The panels map to organs we already have: ML → the ML
  Ecosystem (callable organ, §7) · LLMs → the Stable (0019) · RAG → the Librarian +
  the Memory Construct · Agentic AI → the chassis + workforce (0015/0017) · AI
  Safety → vigil, floors, the Custodian (0012/0013). We host the categories under
  governance; we do not rebuild them — the moat is governed memory, not model
  research. Agents, through HITL, can build ecosystems and fields if the
  objective/intent needs them.
- **The RAG pipeline (image 1) held against the design** — what maps, what's
  missing NOW (feeds the Memory Construct delegation, §2):
  - *Strong by construction:* metadata (we exceed the bar — DIDs, signatures,
    lineage, occurred_at, provenance_class, generation depth) · guardrails =
    floors · generation = the model plane (0016) · sources-as-identities (0014).
  - *Missing NOW — the meaning axis:* embeddings + vector index (the empty
    `embedding_ref`), **hybrid retrieval** (semantic × lexical × **lineage ×
    time × trust-state** — Orreth's hybrid is richer than the industry's), and
    **trust-weighted reranking**: relevance × Bayesian confidence (0005) ×
    fidelity (verified > distilled; `recalled` ranks dead-or-labeled).
  - *Missing NOW — ingestion discipline:* the chunk grain (chunks built for
    meaning, not speed) and entity/relation extraction inside
    Fetch → Grounding → Distill → Curation. Garbage-in governs everything.
  - *Missing NOW — the faithfulness gate:* evaluation after generation. Orreth's
    native form: **the Librarian never asserts without a ContentHash citation** —
    every claim in a composed answer resolves to a Sourced+Verified hit
    ("Sourced or nothing," applied to generation itself).
- **The RAG patterns (image 3) → Orreth mechanisms:** CRAG (low-relevance →
  re-acquire) = the floor knowledge-request loop (§4), already designed ·
  Self-RAG = the chassis critic + parked intents (0015) · Agentic RAG = the
  nucleus · **Fusion RAG = the self-dialog** — the same question asked at many
  seats, fused at the top; Orreth's fusion axis is *jurisdiction*, not phrasing ·
  **Graph RAG = lineage + worldlines + ScopePath neighborhoods** (the recall walk
  is already a graph traversal; make graph retrieval a first-class mode) ·
  Adaptive RAG = the Librarian's query planner (classify the ask, route to the
  right mode(s) — the becky-shaped duality generalized) · Multimodal RAG = later;
  the store is already modality-blind (opaque content-addressed bodies), so the
  door stays open without work now.

## 11. The Purge — the Poison Protocol (JB requirement, 2026-07-10)

- **The requirement:** Humans — **through Librarian + Warden** — must be able to
  **PURGE a poison (bad) memory** which could, in theory, corrupt the whole
  Universe. "BAD BAD."
- **The shape latent in existing canon** (assessment, not yet design): quarantine
  → walk → purge → immunity.
  1. **Quarantine at machine speed**: vigil/librarian seal the record(s) from all
     retrieval the moment poison is suspected (a containment state; uniform
     refusal hides the seal from probers). Detection fast, destruction slow.
  2. **The recall walk enumerates the blast radius** (0014 §4) — source +
     `derived_from` descendants — **and must cross the promotion boundary**:
     poison that crystallized into a *skill*, a *distillation*, or a *profile
     claim* is in scope, not just raw records.
  3. **Purge is a gravest-class HITL act** (0012): co-signed, cooling-off,
     staged by machine, decided by humans. Bodies are physically destroyed;
     **signed stubs remain** (provably purged, never silently lost — the
     tombstone machinery already promises exactly this, 0002 §6).
  4. **Immunity**: the poison's origin signature becomes a floor at ingest
     (the-first-questions.md immune loop) — the same infection never enters
     twice.
- Distinct from ordinary recall: **recall marks knowledge visibly dead
  (annotate-never-rewrite); purge destroys the body under human quorum.** Two
  rungs of the same ladder — discredit beats delete by default, delete exists
  for corruption.

## 12. Multimodal capability — documents and images (JB addition, 2026-07-10)

- **The requirement:** the Universe must be able to **upload documents and images
  in many formats**, **create documents and images**, and give agents **image
  recognition, OCR, and similar model capabilities.** (JB: build can defer; the
  requirement is on the record now.)
- **Placement (design-owner call — JB's Stable instinct confirmed, split by
  nature):**
  - **Models are minds → the Stable (0019).** OCR, vision/recognition, embedding,
    and image/document *generation* models are saddled like any mind: DEAL pinned,
    metered per agent, price-drift watched, **EOL on the pasture calendar** —
    exactly why JB thought Stable. A vision model is not a tool; it is a mind with
    a lifecycle.
  - **Converters are services → the Farm (0018).** Deterministic format work
    (parse/convert/render pipelines) joins as manifest-pinned, keeper-tended
    tools.
  - **Agents reach both through skills** — a `read-document` / `describe-image` /
    `generate-figure` skill binds to whichever organ serves it; the chassis never
    knows the difference (least-privilege attention holds).
- **Upload is an ask.** Even a file enters through the parlor law: the human hands
  a document to the Librarian (Console workspace drop zone = the ask); the
  Librarian admits it as `ingested-archive` provenance, **quarantined at 0.0000**
  like all outside knowledge (0014). No side door for files.
- **Ties to the Memory Construct:** the store is already modality-blind
  (content-addressed opaque bodies) — uploads land today. What the ingestion
  discipline adds: OCR/vision *extraction* feeding the meaning axis (text,
  entities, embeddings per modality), so a scanned PDF becomes retrievable
  knowledge, not a dark blob. Multimodal RAG (image 3, pattern 10) lands here
  when built.

---

## Questions for JB — as originally parked
*(Preserved for the record. Resolved in the design-owner pass below; only four
confirmations remained JB-level and were brought to him via AskUserQuestion.)*

1. **The Librarian's sameness**: one DID present at every seat, or one archetype
   with scope-bound incarnations whose lineage proves sameness (0002 §1)? The
   self-dialog is recordable either way, but identity, revocation, and the meter
   read differently in each.
2. **Opt-out granularity**: per record class, per direction (up vs lateral), or
   whole-exchange — and does opting out sever future flow only, or seal previously
   exchanged records too? *(Partially answered, second pass: opt-out governs
   residency/roll-up, never Librarian access — the pull is non-refusable. Remaining:
   class granularity, and what retention class the Librarian's **composed answer**
   over opted-out data carries at Universe — see "leak-by-synthesis" note below.)*
3. **Floor request risk**: which resident(s) grade a knowledge request's risk, and
   what does higher-than-low risk trigger — tier escalation, a 0012 gate, or both?
4. **The Human Profile's class**: personal data with consent facets (0002 §2)? Does
   each profile claim carry provenance (asserted by the human vs inferred by the
   Librarian), and can the human tombstone parts of their own profile?
5. **Markers**: facets on the record or first-class annotation records deriving
   from it? Who assigns severity — the authoring resident, a critic, or a policy
   rubric? Are change-severity and life-event two orthogonal families on one marker
   shape?
6. **Plan approval lanes**: is plan approval always human, or can low-severity
   plans auto-approve under a cascaded gate policy, with marker severity picking
   the lane?
7. **The fingertip's local memory**: does it flush to the Field on completion
   (journal → floor), or is some of it ephemeral by design (scratch that never
   becomes biography)?
8. **Universe-level workflows**: are PM/ProductDev/EA/BI seats *standing residents*
   of the universe tier, or *workflow templates* instantiated per objective?
9. **Purge quorum**: what gate class does purge carry (2 co-signs like apex acts,
   3 like root rotation)? Does cooling-off apply (approved-but-held, one voice
   aborts), and is a solo-operator universe honestly *unable* to purge (bars
   absolute, 0012 §5) — or does self-hosted get a different bar?
10. **Purge reach**: when poison crystallized into a skill that fleets already
    run, does purge auto-revert the skill to its last clean version (0001
    lifecycle "reverted"), and who re-anchors dependents?
11. **The quarantine seal**: while a purge escalation is pending, sealed records
    must vanish from retrieval without leaking that they exist (uniform refusal).
    Does the seal itself ride the beat to every seat holding copies/distillations?

### Flagged by Fable (second pass — the "what you missed" lens, standing instruction)

- **Leak-by-synthesis**: the Librarian's composed answer over opted-out data is
  itself a record, authored at the asking seat. If that answer resides at Universe
  with ordinary retention, opt-out is quietly defeated by asking. Likely needs a
  retention/visibility class for answers derived from opted-out scopes (ephemeral,
  or marked `derived-from-opted-out` with the source seat's policy riding along).
- **The never-refuse rule is intra-universe.** Within one universe, a field can
  never refuse its Librarian. At the Custodian/multiverse boundary the opposite
  holds: sibling universes and hosted tenants stay sealed (0002 §4, 0013). The rule
  needs its boundary stated so it can never be read as crossing it.

## The design-owner pass — gaps closed, asks adjusted (Fable 5, 2026-07-10)

*JB's license: "YOU CAN adjust my asks as they are not written in stone and this is
a partnership." Adjusted asks are marked ⚙; everything else resolves from locked
canon. Four items were JB-level and **all four locked 2026-07-10 via
AskUserQuestion** (recorded in `../decisions/README.md`, build-phase section):
Librarian = one lineage/per-seat keys (R1) · plan approval = severity-routed lanes
(R6) · opt-out = future flow only (R2) · purge = the split model (R9).*

**R1 · The Librarian's sameness ⚙ — one mind, many seats, per-seat keys.**
One Librarian **lineage**: a Librarian root identity (chained to the universe root
via becky) with a **scope-bound did:key per seat**, lineage proving sameness —
exactly becky's root→leaf pattern (0006 §1). *Adjustment rationale:* a literal
single key at every seat of a world-spread universe means one compromise owns every
seat and revocation is all-or-nothing; per-seat keys keep the self institutionally
and cryptographically ONE (the chain confirms it) while staying federated-safe and
severable seat-by-seat (the nervous-system revocation rule). The self-dialog gains
honest signatures: which seat asked, which seat answered — talking to yourself, on
the record.

**R2 · Opt-out — per record class, future-flow only ⚙, synthesis made ephemeral.**
The TierProfile gains an `exchange` block: per-record-class opt-in/out (diary,
knowledge, …), rendered in the Console per ecosystem/field. Opt-out severs
**future** roll-up only — already-risen records stay (append-only history never
rewrites; a true pull-back is a governed tombstone action, not a toggle). The
leak-by-synthesis fix: a composed answer over opted-out data is classed
**`derived-from-opted-out`** — resident-signed, short-TTL at the asking seat,
**excluded from distillation cohorts**, so opted-out substance never accretes at
the apex through Q&A. The access record (that the ask happened) is permanent; the
content evaporates. Non-refusable access + real opt-out, both true.

**R3 · Floor request risk — the Librarian seat grades, vigil sees, severity routes.**
The floor's Librarian seat grades each knowledge request against a cascaded risk
rubric (a Standard; dimensions: source class, cost, scope touched, external
egress). Low → auto-acquire (the CRAG loop). Above-low → staged through 0012:
medium = resident co-review, high/critical = human gate. One severity taxonomy
(the marker ladder, R5) reused everywhere.

**R4 · The Human Profile — a Knowledge Category about the human.**
Class `personal-data`, consent facets live, retention min/max honored (0004 §4).
**Every claim carries provenance**: human-asserted (via parlor, human's words in
the body) vs Librarian-inferred (Librarian-authored, `derived_from` → evidence).
Inferences enter low on the trust ladder and corroborate through observation —
rookie probation applied to *beliefs about you*. The human sees every inferred
claim, corrects by superseding, and may tombstone parts (consent withdrawal) —
always *through* the Librarian, so the no-direct-input law holds even here.

**R5 · Markers — first-class annotation records, two orthogonal families.**
A marker is a signed record deriving from what it marks (`derived_from`) — never a
mutation (annotate-never-rewrite). One shape, two optional families:
`change_severity: low|medium|high|critical` and `life_event:
minor|major|substantial`, plus reason + rubric ref. Graders: the authoring
resident proposes per a cascaded grading Standard; the critic grades RunRecord
changes; vigil places security markers; a human's "remember this" becomes a
life-event marker authored by the receiving resident, quoting the human. Severity
rubrics are Standards — versioned, diffable, canaried.

**R6 · Plan approval — severity-routed lanes ⚙.**
The human's ask is the HITL on the *intent*; the *plan* routes by its marker
severity: low → auto-approved under a cascaded gate policy (signed, on the record,
canary-able — 0008's auto-apply lane); medium → resident co-review + human notify;
high/critical → human gate, 0012 quorum where the class demands it. *Adjustment
rationale:* "always human on every plan" would re-create the friction 0008/0012
already solved; the locked lane-routing extends to plans unchanged.
**[JB-confirmed — see locks]**

**R7 · Fingertip local memory — journal-with-grain.**
During execution the fingertip works in scratch (computation, not biography). What
lands on the floor: per-cycle RunRecords (already law, scribe-signed), the outcome
memory, and observations the floor's KeepRules pin. Raw scratch **evaporates by
design** — *if it informed a decision or changed the world, it lands; if it was
scaffolding, it was never memory.* Sourced-or-nothing applies to what remains.

**R8 · Universe-level workflows — templates + standing incarnations.**
PM/ProductDev/EA/BI are **GraphSpec templates** (versioned artifacts in memory,
factory-maintained like all behavioral assets). An arriving objective instantiates
a template as an orchestration incarnation (factory-stamped, birth certificate,
budget from the intent) living the objective's life. **Standing jobs** ("the job
could live forever" — monitor all products, run risk assessments) are the same
incarnations with no completion condition — immortal jobs, beating like organs.

**R9 · Purge quorum — the split model ⚙.**
Two purges, two laws: **personal-data purge** (your own profile/memories) rides
the consent machinery — single-owner, solo-capable, already promised (0002 §6).
**Operational poison purge** is a gravest-class act: 2 co-signs + cooling-off (one
voice aborts), bars absolute — a solo-operator universe can **seal forever but
destroy only when quorum exists**. Containment is never blocked; destruction waits
for humans, plural. **[JB-confirmed — see locks]**

**R10 · Purge reach — the walk crosses the promotion boundary.**
The enumeration follows `derived_from` **through** distillations, skills, and
profile claims. Tainted skills revert to the last clean version (0001 lifecycle
`reverted`); no clean ancestor → `escalated`, pulled, and parked as a
knowledge-intent to rebuild clean (failure is fuel, again). Distillations gain
RedactionMarkers or re-distill over surviving inputs. Profile claims supersede
with a recall note. Re-anchoring rides the same Selector cascade that distributed
the asset.

**R11 · The quarantine seal — a floor that rides the beat.**
The seal is a floor-class signed record (tighten-only — no seat may decline it),
cascaded to every seat holding copies or derivatives; each seat's egress refuses
sealed refs under uniform refusal. Propagation is light-cone honest: seats
acknowledge on the beat; unacknowledged seats show amber in the Console until the
seal lands.

**Also folded into the Memory Construct requirements (from the image assessment):**
the meaning axis (embeddings, hybrid retrieval semantic × lexical × lineage ×
time × trust-state, trust-weighted rerank) · ingestion discipline (meaning-grain
chunking + entity/relation extraction inside Fetch→Grounding→Distill→Curation) ·
the faithfulness gate (no Librarian assertion without a ContentHash citation) ·
self-dialog answers always carry their horizon (0002 remainder semantics) ·
markers complete the 100%-of-change claim.

---

*The library got a face, the face got a scope, the scope keeps your profile and
marks what mattered — and at the very tip of the whole layered mind, a small fixed
loop does exactly the sliver it was fed, while the universe above it thinks.* 🥂
