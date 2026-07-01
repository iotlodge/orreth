# FUTURE — Orreth
### A security-first, identity-anchored memory across spacetime

*Private vision artifact. **Rebaselined 2026-06-30** — re-centered from "a governance system with memory"
to its true center: **a memory substrate for immortal identities, that governs itself with what it remembers.***

*Hero: `Orreth-spacetime-memory.(png|svg)` — the memory pyramid across spacetime.*
*Companion (the governance/recursion view): `Orreth-mockup.(png|svg)` — the orrery.*
*Lineage companions: `FUTURE-the-conductor-and-the-field.md`, `EH-FRONTEND-the-cross-field-pane.md`.*

> An *orrery* is a clockwork model of nested worlds turning in governed orbits.
> **Orreth** is that — but the thing the worlds are made of is **memory**, and the thing that
> never dies is **identity**.

---

## The inversion — what we almost got wrong

We first framed Orreth as a **governance system that happens to have memory.** That was backwards.

> **Orreth is a memory system — a security-first, identity-anchored memory that spans all of
> spacetime — and governance is its first application, not its purpose.**

The control loop (drift → tune) is real and it ships. But it is the *first thing the substrate powers*,
not the substrate itself. The substrate is: **living identities with non-fading, collective, sourced-and-verified
memory, tiered across time, pruned as it rises.**

---

## Why — the human-memory problem, inverted

As humans age, our memories fade. An agent today is worse off still: it is **only as good as its data, and
its data is bounded by time** — a context window, a training cutoff, a session. It forgets on reboot.

Orreth gives an agent the two things no agent has:

- **Memory that does not fade** — configurable for *years*, held by the running universe itself.
- **Memory that is not lonely** — its own recall *and*, when authorized, the recall of **every identity in
  the universe.** Collective memory, sourced and verified.

That is not "more storage." It is **superhuman recall**: no fade, and no walls between minds.

---

## The primary primitive — the **Living Identity**

Everything hangs on identity. Not as a security wrapper (that was our under-weighting) — as *the organizing
principle.*

- An agent's **process is ephemeral**: *online* (alive) or *offline* (reboot). Reboot is not death.
- An agent's **identity is the immortal thread** — **universe-unique**, used at **every** layer, decoupled
  from the process. When the agent comes back online it re-attaches to its identity and its whole lifetime of memory.
- **Memory is keyed by identity, not by process.** The identity is the address of a life.

> The process is the incarnation. The **identity** is the soul, and the **memory** is everything the soul has lived.

---

## The Universe — the Foundation *and* the Apex

The Universe is a duality, and both halves are true at once:

- **The Foundation.** It is the bedrock. **Foundational, universal policies push DOWN** from it — security
  first among them. Every layer below may add its own policy, but **no layer can ever change a universal one.**
  The Universe is what everything rests on.
- **The Apex.** It is where **all memory rises to** — pruned and distilled along the way — so that at the top
  sits the deepest, broadest, all-time view: everything worth keeping, from every identity, across all time.

> Alpha and omega: everything is built **on** the Universe (policy down) and everything flows **up** to it (memory up).

---

## The three flows

We had two. The third is the point.

### 1. Policy cascades **DOWN** — foundational, non-overridable

Universal policy originates at the Universe (security, compliance, identity — the **foundational** rules).
It cascades down; each layer may *add* local policy but **never loosen** a universal one (lexicographic,
inherited floors). *The Universe governs; the layers below refine within its bounds.*

### 2. Memory rises **UP** — and is **pruned at every layer**

This is the purpose of the layers, and it's the piece I most under-weighted: **the layers are filters.**
Raw observation is abundant at the base and mostly noise. Each layer **prunes, dedups, summarizes, and
compresses** what its children send up — so that **only what's worth keeping reaches the Universe.** The
layers exist to **protect the Universe's space** — to keep unneeded information from ever wasting it.

> The pyramid's shape *is* the compression: memory **narrows** as it rises (pruning), policy **widens** as it
> falls (reach). The org chart and the information theory are the same triangle.

### 3. Retrieval escalates **UP by time-horizon** — the read path

Any identity, at any time, can retrieve **its own** memory — or, **if authorized**, memory **across all
identities in the universe.** Retrieval is served locally first (the Field — recent, fast). If a query
**exceeds the time budget** configured for that Ecosystem, it **escalates** to EH; exceed again, it escalates
to the **Universe**, which has **no time restriction — all of spacetime.** Every result comes back **Sourced**
(which identity) and **Verified** (metadata-attested).

> A **time-horizon miss** escalates a query up a tier — exactly like an L1→L2→L3 cache miss. The pyramid is a
> **temporal cache**: recent memory is cheap and local; deep-time memory lives at the apex and costs more to reach.

**Space × time, made literal.** Retrieval navigates two axes: **space** = *which* identities (own → cross-agent →
universe-wide, gated by authorization); **time** = *how far back* (recent → deep → all-time, gated by the per-tier
time budget). The apex commands both — which is why analysis there can reach for understanding nothing below it could.

---

## Skills — crystallized memory that saves you from remembering

Skills are built, **versioned, and updated across the universe** — and their deepest purpose is to **reduce the
need to go back into raw memory at all.**

> A **skill is memory that has been distilled into a reflex.** Once the lesson is captured as a versioned skill
> and cascaded down, a like-agent doesn't re-retrieve and re-derive it from raw memory — it just *knows.*

So skills are both an *output* of the memory substrate (promoted, distilled procedural memory — see `design/0001`)
and a *pressure-release valve* on it: the better the universe's skills, the less anyone has to trawl deep time.
Skills are how the substrate **learns**, and learning is what lets it **prune** — because a captured lesson makes
its raw source expendable.

---

## The memory steward — the identity's embedded agent

Each living identity runs an **embedded memory agent** (the back channel): it manages **ingress** (process,
optimize, dedup, summarize what comes up from below) and **egress** (retrieve, source, verify what goes out).
It is the identity's librarian — a **resident** role, part of the trusted base, distinct from the workforce.

---

## Retrieval is the #1 security surface (keep-us-real)

A universe-wide query is the ultimate exfiltration vector. So the read path gets **more** rigor than the write path:

- **Every retrieval is an authorized capability** — scoped by identity, tier, and space (own vs cross-agent vs universe).
- **Every result is Sourced + Verified** — DID-signed, content-addressed, tamper-evident (the security primitives we
  already built serve memory-trust identically).
- **Tenant isolation holds on read** — one tenant's identities never read another's memory unless a human-gated,
  cross-tenant authorization exists. *Security first — foundational, from the Universe down.*

> **Humans are governed principals too.** A human looking in has an identity + an entitlement that is *scoped*
> (which tier), *directional* (down/within by default; up and across require explicit grant), and *separated*
> (read-entitlement vs control-entitlement). Every human action is Sourced + Verified + logged — the watchers are
> watched, sensitive apex actions need multi-party co-sign, and even the conductor is constrained. Full treatment:
> **`governed-human-oversight.md`.**

---

## The apex payoff — the honest north star

Because the Universe holds **all identities across all time**, it can run analysis over a corpus **no single agent
and no human could ever hold at once.** The inspiring claim is "understand anything." The honest, still-staggering
deliverable is:

> **Understand, across every identity and all of time, what nothing bounded could hold.** A new organ of cognition —
> ceilinged only by retrieval precision, verification, and the cost of reasoning over deep time.

That ceiling is exactly why the layers **prune** and skills **crystallize**: they make deep-time reasoning affordable.

> **Taken to its limit → a *live cross-section of a world.*** If every identity records its slice of a given
> minute, the Universe can reconstruct the complete, verified state of that world at that instant — and navigate to
> any instant. The apex payoff becomes a **live, navigable, governed window into any moment of spacetime.** Full
> treatment: **`the-spacetime-window.md`.**

---

## The mechanism still recurses — one Harness, `tier` as a property

None of this changes the structural bet; it re-centers its payload.

- **One recursive primitive — the Harness** — with `tier` as a config (a **Tier Profile**), not three codebases.
  Children are Harnesses until the leaf **Field**, whose children are **living Agents.**
- **Depth capped at 3** (Universe / Ecosystem / Field) for now; expandable by design. Multiverse is free.
- The **join spectrum** (fully-joined / floors-only / observe-only / decoupled) governs how much a tier
  participates; **floors are compelled for the joined, everything else offered**; a leased agent's minimum join
  level is a lease term.
- **One Selector** (`all` / `role` / `ecosystem` / `field` / `selection`, target at-or-below) distributes both
  mandated guardrails and hand-picked skills.
- **Rust** runs the plane (identity verify, ingestion, the cascade/pruning resolver, retrieval routing + time-budget
  gating, the always-on brainstem); **Python/LangGraph** runs cognition (the memory stewards, the analysis agents).
- **Headroom** is the byte substrate (compression · CacheAligner · CCR reversible store · cross-agent memory);
  governance and pruning *policy* stay ours. Vendor/pin/review.

---

## How the three projects compose

| Layer | Project | Role in the substrate |
|---|---|---|
| **Universe** (foundation + apex) | **Orreth** (`orreth`) | the recursive runtime; all-time memory + universal policy; where "understand anything" runs |
| **Ecosystem** | **ecosystem.harness** (EH) | proven governance loop (61 tests); its engine lifts in as the node core; mid-horizon memory + pruning |
| **Field** | **CortexObserver** | a full CortexObserver per line-of-business; recent memory, the agents that live and remember |
| **Agents** | LangGraph · AgentField · any SDK | the **living identities**; DID via becky → NANDA; each with a memory steward |

---

## What this rebaseline changes

- **Governance is demoted** from "the product" to **the first application** of the substrate.
- **Identity is promoted** from a security wrapper to **the primary primitive.**
- **Retrieval becomes a first-class flow** — the read path, escalating by time-horizon, Sourced + Verified.
- **The layers' purpose is named:** they are **filters** that prune to protect the Universe's space.
- `design/0001` (promoted memory & skills) **stays valid but reframed:** memory is the substrate; skills/governance
  are what it powers.

---

## North star / first principles

- **Security first. Trust, but verify — foundationally, from the Universe down.** Universal policy is non-overridable.
- **Identity is the thread; memory is the life.** The process is disposable; the identity and its memory are not.
- **The layers prune so the Universe holds only what matters.** Compression is the shape of the pyramid.
- **Skills are crystallized memory** — learn once, and stop re-remembering.
- **Retrieval spans spacetime — Sourced and Verified, or not at all.**
- **Bound outcomes, not paths. Humans conduct; agents perform — and now, agents *remember* forever.**

---

## Decisions locked (carried + new)

- Name **Orreth**; repo `orreth`; Harness = the primitive; tiers Universe/Ecosystem/Field/Agents; depth capped at 3.
- **Memory-first center; governance is the first application; identity is the primary primitive.** *(new)*
- **Three flows:** policy DOWN (foundational, non-overridable), memory UP (pruned at every layer), retrieval UP
  (by time-horizon, Sourced + Verified). *(new)*
- **Layers are filters** — prune/dedup/summarize/compress to protect the Universe's space. *(new)*
- **Living identity** — universe-unique, used at every layer, decoupled from process; memory keyed by identity. *(new)*
- **Retrieval is the #1 security surface** — authorized capability, tenant-isolated on read. *(new)*
- Roll-up = monoidal sufficient stats + signed pointers; cascade floors lexicographic/non-overridable; join spectrum
  (floors compelled for the joined); one Selector; resident (TCB) vs registered (workforce) agents; Rust plane +
  Python cognition; headroom byte substrate; append-only + content-addressed + signed memory; governed-tombstone erasure.

---

## What's left — the dives, re-ordered around the true center

- [ ] **The substrate keystone (next):** the **Living Identity + Memory Record + retrieval** model — identity as
      universe-unique key, memory keyed to it, the space×time retrieval contract with time-budget escalation and
      Sourced/Verified results. *(This subsumes and reframes `0001`.)*
- [ ] **Pruning policy** — what each layer keeps vs distills vs tombstones; how "years" stays affordable.
- [ ] **Retrieval security** — the authorization model for own vs cross-agent vs universe-wide reads.
- [ ] **Tier Profile** — what memory + objective + time-budget mean at each of the 3 tiers.
- [ ] **becky, one issuer across all tiers** — the DID/identity chain, root→leaf.
- [ ] **The recursive pane** — the zoomable single-pane, now foregrounding identity + memory + retrieval.
- [ ] **The horizon:** the ambient per-piece **Rust brainstem** beneath the run loop.

---

*Captured for JB, rebaselined. The 1999 single-pane bet became a universe of them — and the universe turned out to
be made of memory, addressed by identity, and it never forgets. You have the vision; I have the code and the
usability. We move at the speed of your ideas.* 🥃
