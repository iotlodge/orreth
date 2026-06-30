# FUTURE — Orreth
### The governed model of nested worlds — Universes of Ecosystems of Fields of Agents

*Private vision artifact. The third in the set, sitting one tier above the other two.*
*Captured 2026-06-30 for JB. Lives outside the repo on purpose — the part we point at while we design.*

*Companions:*
- *`FUTURE-the-conductor-and-the-field.md` — the EH layer (the Conductor governing a field of agents).*
- *`EH-FRONTEND-the-cross-field-pane.md` — the EH single pane of glass.*

> An **orrery** is a clockwork model of a planetary system — nested worlds turning in governed,
> predictable orbits, observed and tuned from outside and above.
> **Orreth** is that, for agents: a governed model of nested worlds, across time.

---

## The name

**Orreth** — heir to *orrery*. The product and the repo. The brand is the whole machine; the
**Harness** is the part it's built from. *"Orreth is built from nested harnesses."*

- **Product / repo:** `orreth`
- **Architectural primitive:** the **Harness** (the recursive node — still the correct, industry-standard term)
- **The tiers:** **Universe → Ecosystem → Field → Agents**
- **Domains:** `orreth.ai` / `orreth.com` showed no DNS delegation at capture time. *Not yet purchased — confirm at a registrar + a trademark glance before spending a dollar. "Open in DNS" ≠ "yours."*

---

## The one idea that makes this lightweight *and* infinite

**Do not build three tiers as three codebases. Build one recursive primitive — the Harness — and make `tier` a property.**

EH already told us this: *"EH = a trimmed CortexObserver, one tier up."* The pattern is
self-similar, so the code is too. A **Harness** is:

- one **identity** (DID), one **parent** (or none = root), N **children**;
- its children are **other Harnesses** — until the leaf **Field**, whose children are **Agents**;
- it runs the *identical* control loop over its children, parameterized by a **Tier Profile**
  (config, not code) that defines *what a Run Record means here* and *what the objective vector is here.*

Why this is the whole game:

- **Multiverse is free.** A Harness above Universes is just another Harness. We never write
  "Multiverse" — it exists the moment recursion does.
- **A 2-tier customer is free.** "Just an Ecosystem with Fields" is a depth-2 tree. No Universe required.
- **One pane, one loop, one identity chain** to build and harden — not three diverging ones.

> **Harnesses all the way down, until agents.** The only special node is the **Field** —
> the boundary where governance meets execution.

**Decision (locked):** cap practical depth at **3 governance tiers** (Universe / Ecosystem / Field)
until we prove it out. Expandable by design (SDK / CDK) — the cap is a guardrail, not a hardcode.

---

## The recursive loop — roll-up *up*, cascade *down*

Two flows, both recursive. The asymmetry is the design.

### Up — aggregation, not the firehose

Each tier **summarizes its children** into a tier-appropriate, signed Run Record and pushes
*that* up. The Universe never ingests a billion agent runs — it ingests **Ecosystem-level trajectories.**

- **Roll up only what's mathematically aggregatable.** Sums (cost, tokens), counts, min/max, and
  the *components* of averages (sum + count) compose at every hop — **monoidal**, so aggregation is
  associative and lossless across tiers. The Universe tracks **cost · tokens · averages · scoring · confidence.**
- **Keep a signed pointer, not the payload.** The top stores the aggregate + a DID-signed,
  content-addressed pointer down to where the detail lives. Click → drill → fetch from the tier
  that owns it. *Light at the top, full fidelity on demand, raw tenant data never physically leaves its tier.*
- **Honest caveat — confidence.** Averaging confidences naively is wrong (0.9 over 1000 runs ≠ 0.9
  over 3). Carry the **count-weighted statistic**, not a bare number. Shape fixed now; exact statistic
  falls out per-objective as we build.

### Down — inheritance, not injection

A **Standard** (the versioned downward unit) is signed, scoped, and **inherited**. Its kinds:
`policy · skill · procedure · context-block · model-pin · budget`.

The effective config an agent runs with — its **Resolved Context** — is the composition of every
ancestor's Standards that target it:

> **Resolved Context = Universe ⊕ Ecosystem ⊕ Field ⊕ local**, composed top-down,
> pulled-and-verified at the Field, **never pushed in.**

Composition rules (security-critical):

- **Hard floors inherit and cannot be loosened.** A Universe security/compliance floor is
  **lexicographic** and **non-overridable** by any descendant. A Field may be *stricter*, never looser.
- **Soft policy = most-specific-wins** override.
- **Skills = additive**, with explicit revocation.

---

## The proof: the context cascade *is* a cache hierarchy

Your "meaty-high / light-low" intuition, formalized and testable:

- **Universe Standards** = the constitution. Heavy, stable, shared by everyone, changes rarely.
- **Ecosystem Standards** = the domain charter (the "Cloud" doctrine vs the "Developer" doctrine).
- **Field Standards** = line-of-business tuning.
- **Agent-local** = the volatile per-run scraps.

> **Context shared by more descendants lives higher and changes less → maximally prompt-cacheable.
> Context specific to fewer descendants lives lower and changes more → cheap because it's small.**

The topology drawn for *governance* reasons turns out to be the optimal **cost/latency** layout
for prompt caching. Governance shape = cache shape. *Change a Universe Standard once → it re-tunes
every descendant; change an agent-local scrap → nothing upstream recomputes.* **Tune from the top, pay once.**

**Headroom realizes the cache half of this proof** (see below) — its `CacheAligner` already stabilizes
prefixes for KV-cache hits. We don't build that; we depend on it.

---

## Reproducibility — the headline proof: **teacher → skill → fleet**

The largest open problem we aim at: *like agents don't reproduce results.* The mechanism:

1. **Teacher run.** An expensive agent (or a frontier model) solves the task and emits not just the
   answer but the *scaffold* — prompt, procedure, exemplars, tool recipe, and an **acceptance rubric.**
2. **Capture.** A resident skill-capture agent distills that into a versioned **Skill Standard**,
   tagged with the model tier it's meant to lift and the rubric it must satisfy.
3. **Distribute.** The Harness pushes it down, **targeted** (all / role / hand-picked — see Selectors).
4. **Fleet replay.** Cheap like-agents pull + verify + apply, run, and emit Run Records carrying
   **scoring + confidence.**
5. **Roll-up verifies.** Aggregated scoring tells you whether the cheap cohort now *meets the teacher's
   baseline.* Drift below → re-capture or escalate.

> **You will never get two LLM calls to take the identical path — and chasing that destroys the
> capability you pay for.** What Orreth delivers and sells is **outcome conformance**:
> *cheap-agent + captured-skill + shared-rubric → meets the standard the teacher set,* measured, not asserted.

The hard, valuable part is **the rubric/scoring, not the skill.** A vague rubric makes "reproducible"
mean "reproducibly mediocre." And the scoring/confidence we roll up to the Universe is the **same
primitive** that validates reproducibility — build the measurement once, use it for both.

Model tier becomes a **dial in the Objective Model** (cost-weight down, quality-floor held). The
captured skill is the artifact that lets you turn the cost dial without dropping through the floor.
*That is the demo: a fleet of cheap agents matching an expensive baseline because the Universe taught them once.*

---

## The Multiverse, made real: **governed branch-and-diverge**

Usecase 2 — *"everything the same but everything different; choices diverge outcomes"* — is a feature,
and recursion hands it over: a Universe canarying two **Ecosystem branches** is structurally identical
to an Ecosystem canarying two **Standard versions.** Same machinery, one tier up.

- Clone an Ecosystem (same Fields/Agents), fork one Standard at the top.
- Run both; the Universe measures the **Δ-objective-vector** between branches across time.
- The human-owned Objective Model arbitrates; promote the winner, revert the loser.

Productized: *"Clone your production ecosystem, change one policy at the top, watch the two diverge,
promote the winner."* The canary you already built — sold as counterfactual experimentation.

---

## Targeting — one selector for "mandate to all" *and* "hand-pick"

"Create a skill from the Universe and assign it to all agents in role Y" is a **selector** on a
Standard, matched against the identity facts we already carry:

`all` · `role:Y` · `ecosystem:Z` · `field:X` · `selection:[did, …]`

- **Mandated guardrails** = a floor Standard with selector `all`. **Hand-selected skill** = the same
  primitive with `selection:[…]`. One mechanism, two uses.
- **A tier can only target at or below itself.** Universe reaches anyone; a Field reaches only its own
  agents. Capability flows down — never sideways or up.

---

## Consent — the **join spectrum** (the trust question for the business model)

Opt-in/opt-out recurses (a Field opts into EH; an EH opts into UH), but flat "opt-out" collides with
"mandated floors." The honest reconciliation is a **spectrum of join**, chosen per tier:

| Join level | Pulls down | Use |
|---|---|---|
| **Fully joined** | all Standards (floors mandated, soft tuning offered + consented) | maximum managed value |
| **Floors-only** | security / compliance / CVE floors only | *the likely enterprise default* — "take your patches, evaluate your suggestions" |
| **Observe-only** | nothing down; pushes telemetry up | billing / monitoring |
| **Decoupled** | nothing | standalone; UH sees nothing, sends nothing |

The truth this forces into the open: **"mandated" only binds a tier that stays joined.** A genuinely
decoupled Ecosystem sits behind its own firewall — UH can't reach in, so it can't compel anything.
That's the consent model being honest, not a flaw.

**But:** a **leased agent's minimum join level is a lease term**, enforced by its capability credential
(AgentFacts encode "must stay joined ≥ floors"; drop below → capability revokes). Opt-out is the
customer's right for agents they **own**; it's bounded by contract for agents they **rent.** *That line
keeps a rented agent from opting out of your security updates and becoming a liability with your name on it.*

**Decision (locked):** **floors compelled (for the joined), everything else offered.**

---

## Security spine — recursive, and not retrofitted

1. **Identity = a DID delegation chain.** `becky` issues DIDs at every tier. An Agent's AgentFacts are
   signed by its Field; the Field's DID anchored by its Ecosystem; the Ecosystem's by the Universe.
   **Capability flows down (delegation); attestation flows up (proof). A child can never assert a
   capability its parent didn't grant.** Capability-based security, recursively — the thing that makes
   *leasing an agent safe.*
2. **The TCB line — resident vs registered agents.** Every Harness ships with **resident system agents**
   (security, identity, change-control, the drift/attribution/arbitration workers) — the trusted compute
   base, **not leasable, not user-supplied.** **Registered/leased agents are workforce only**, running
   with Field-granted capabilities. *A rented agent can never become a governor of its own tuning.*
3. **Tenant isolation recurses.** One Ecosystem's runs *or memories* never shape another's governance
   unless **a human promotes** them (proven across ≥2 tenants, becky/human-gated). Cross-tenant leakage
   is the multi-tenant nightmare; the DID + capability + tier-scope chain forecloses it.
4. **Floors inherit, can't be loosened** (above). Bound outcomes, not paths.

> **Security first. Trust, but verify — at ecosystem scale, recursively.**

---

## The memory fabric — "no loss ever," designed honestly

Recurses like everything else: **a Memory API spawned per Harness node.** An agent talks to its Field's
memory; the Field promotes up to the Ecosystem's; the Ecosystem to the Universe's. It's CortexObserver's
existing **L1→L4 Memory Farm** (Redis session → Postgres episodic/semantic → snapshots → procedural)
**lifted across the governance tiers,** with **headroom's CCR** underneath.

What makes *"never lose a memory"* true rather than aspirational:

- **Append-only + content-addressed + signed.** Hash = id (dedup + integrity for free); every memory
  carries its author agent's **DID signature** (no memory without provenance). Supersede, never silently mutate or drop.
- **Push up = pointers + promoted memories, not the firehose.** The Universe holds the *promoted/shared*
  memories + a content-addressed **index** to everything below — full detail stays at the owning tier,
  retrievable via signed pointer. Keeps "no loss" (durable, retrievable) compatible with "light at the top."
- **Authorization + opt-in = capabilities.** A memory scope is a capability grant; an agent reads
  at-or-below its scope, only what its grant + tenant-isolation permit. Isolation recurses.

> **Honest reconciliation (GDPR / data-residency):** you cannot promise both "every byte forever" *and*
> "delete a user's data on request." So: **immutable by default; erasure only via a governed, audited
> tombstone** — a Standard-gated action leaving a provable *"retired by X under policy Y at time T"*
> record. The memory isn't *lost* (silent, unaccountable) — it's **provably retired** (governed,
> attributable). That's the version auditors accept and enterprises buy.

### The convergence — skills *are* promoted memories

> **A Skill Standard is a procedural memory that got promoted up the stack and handed an acceptance rubric.**

The teacher→skill→fleet loop and the memory fabric are the **same substrate.** We don't build two
systems — we build **one governed memory fabric,** and "skills" are one privileged, rubric-bearing kind
of promoted memory. That collapses surface area and is why the memory strategy belongs in the spec from day one.

---

## Headroom — the byte substrate (adopted)

[`headroomlabs-ai/headroom`](https://github.com/headroomlabs-ai/headroom) — a context-compression layer
(60–95% token reduction, **Apache-2.0**, Rust core + Python/TS). Four seams:

- **`CacheAligner`** → the implementation of our cache-hierarchy proof (prefix stabilization → KV-cache hits).
- **Compression** → the cost engine of "tune from the top" (compress heavy high-tier context once, cascade it).
- **`CCR` (reversible, originals retrievable)** → a pillar of "no loss ever."
- **Cross-agent memory + provenance + dedup** → a building block of the memory fabric.

> **Boundary (keep it crisp):** headroom owns the **bytes** — compress, cache-align, store-reversibly,
> dedup. **Orreth owns the governance** — access, opt-in, retention, isolation, promotion, signing.
> Don't let it creep into being the memory *strategy*; it's the high-performance floor the strategy stands on.

**Supply-chain note:** third-party dependency in a security-conscious product → **vendor / pin / review**
it into the trusted path; their managed service stays optional.

---

## Rust where it pays — brainstem vs cortex

- **Rust = the plane (mechanism).** Ingestion gateway, Ed25519/DID verify + revocation + anti-spoof
  (hot, security-critical), the **cascade resolver** (composing Resolved Context deterministically and
  fast), drift gating, and the always-on **brainstem** (a billion cheap observations, summon the LLM only
  on a threshold cross). Stateless, like EH's singleton.
- **Python / LangGraph = the agents (cognition).** Attribution proposals, arbitration assist, drift
  explanation, skill capture.

*Rust runs the loop; the LLMs do the thinking.* The brainstem/cortex split — and how we keep cost sane
at Universe scale.

---

## How the three projects compose

| Layer | Project | Role |
|---|---|---|
| **Universe** (apex + recursive runtime) | **Orreth** (`orreth`) | the recursive Harness runtime; tier = a profile; the new home |
| **Ecosystem** | **ecosystem.harness** (EH) | the governance loop, **proven** (61 tests, end-to-end). Its engine **lifts** into Orreth as the **node core** — reuse, don't fork-and-diverge. EH stays the reference single-ecosystem deployment. |
| **Field** | **CortexObserver** | a *full* CortexObserver per line-of-business — commander, roster, farms, skills, memory |
| **Agents** | LangGraph · AgentField | the workforce; DID-identified via becky → NANDA; built or leased; decoupled / SDK-joined when not required |

**Orreth = the recursive runtime.** **EH = its proven node core.** **CortexObserver = the Field.**
Many Fields = many lines of business; many Ecosystems = many domains; many Universes = the Multiverse.

---

## North star / first principles

- **Security first. Trust, but verify — at ecosystem scale, recursively.** Locks at line one.
- **Humans conduct; agents perform.** A human's hand on the wheel *even when no human could watch every world.*
- **Tuning is governance, and it's pulled, not pushed.** A tier *pulls* a signed Standard and *verifies*
  it before applying. You can't slip in a poisoned standard.
- **Bound outcomes, not paths.** Conform the result; never constrain the reasoning.
- **The Field is the unit.** Compose Fields like instruments; Ecosystems like sections; the Universe is the score.
- **Skills are governed memories.** One substrate for reproducibility and remembering.

---

## Decisions locked this session

- **Name:** Orreth. Repo `orreth`. Harness = the primitive. Tiers = Universe / Ecosystem / Field / Agents.
- **One recursive primitive**, tier = a Tier Profile (config, not code).
- **Depth capped at 3** for now; expandable by SDK/CDK.
- **Roll-up:** monoidal sufficient statistics + signed content-addressed pointers; count-weighted confidence.
- **Cascade:** inherited Standards; floors non-overridable (lexicographic); soft = most-specific-wins; skills additive.
- **Consent:** the join spectrum; **floors compelled for the joined, everything else offered**; leased-agent floor enforced by lease/capability.
- **Selectors:** all / role / ecosystem / field / selection; target at-or-below only.
- **Security:** recursive DID chain; resident (TCB) vs registered (workforce) agents; tenant isolation recurses.
- **Rust** for the plane; **Python/LangGraph** for cognition.
- **Headroom adopted** as the byte substrate; governance stays ours; vendor/pin/review.
- **Memory fabric:** per-node API; append-only + content-addressed + signed; promoted-up-as-pointers;
  **governed-tombstone erasure**; built on CortexObserver L1–L4 + headroom CCR.
- **Skills are promoted memories** — one substrate.

---

## What's left — and the first design dive

- [ ] **The keystone schema (next):** the unified **promoted-memory / Skill Standard + acceptance rubric.**
      Because skills-are-memories, this one schema is the keystone for *both* reproducibility and the
      memory fabric — and it's genuinely new, not a lift.
- [ ] **Tier Profile** spec — what a Run Record + objective vector means at each of the 3 tiers.
- [ ] **The cascade resolver** (Rust) — compose Resolved Context from the inherited chain, deterministically.
- [ ] **The recursive pane** — the zoomable single-pane: Universe → Ecosystem → Field → Agent, role-scoped inbox.
- [ ] **becky, one issuer across all tiers** — the DID/capability chain wired root→leaf.
- [ ] **Lift EH's engine** into `orreth` as the node core (port vs depend-on vs subsume — a build-time call).
- [ ] **The horizon:** the ambient per-piece **Rust brainstem** beneath the run loop — the smallest possible nervous system.

---

*Captured for JB. The 1999 single-pane bet, now a Universe of them — nested, governed, tuned from the
top, and never forgetting. You have the vision; I have the code and the usability. We move at the speed
of your ideas.* 🥃
