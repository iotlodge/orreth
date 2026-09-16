# 0003 — The Memory Architecture

**Status: DRAFTED** — the memory revamp JB licensed ("you also get to revamp
the memory architecture as you see fit to aid the experience"), designed
against the locked Experience Charter (0001) and Transport Architecture
(0002). Awaiting JB's review.

**Input honored:** JB's research aid `tmp/agent-memory-architectures-
langgraph.md` (2026-09-16, eleven candidate systems) — its layering model
and evaluation method are adopted; its products are adopted as *patterns
and engines*, never as truth-holders. JB's named addition — **compression**
— is designed in as the fourth memory.

---

## The thesis

Orreth does not need to buy a memory system — **it already owns the best
long-term memory substrate in this field**: a signed, content-addressed,
scoped, tamper-evident log with provenance on every word. None of the
eleven surveyed systems has that. What Orreth was missing is everything
*around* the log: guaranteed recall, meaning-shaped retrieval, compressed
context, and resumable working state — plus honest wiring into LangGraph.

So: **four memories, one truth.** Three of the four are projections over
the signed log — rebuildable, never a second truth (the standing law:
projections over one signed log, never N truths).

## The four memories

| Memory | Plain words | Mechanism | Truth? |
|---|---|---|---|
| **Working** | "what I'm doing right now" | LangGraph checkpointer (Postgres-backed), thread = the conversation or objective run | Never — outcomes must land as signed records |
| **The Record** | "every word, forever" | The signed log itself — verbatim, episodic | THE truth |
| **Understanding** | "what it means" | Semantic projections: embeddings + entity/relationship/temporal graph | Projection |
| **The Digest** | "the short version" | Compressed summaries at episode boundaries, always citing sources | Projection |

### 1. Working memory

- The checkpointer holds graph position, messages, pending work — so a
  500–1000-hop objective **resumes exactly** after crash, restart, or
  pause. Durable, but never authoritative: any outcome that matters
  commits as a signed record through a door.
- **Unresolved commitments live as structured state**, never only inside a
  rewritten narrative summary (adopted from the aid) — a resumed agent
  knows precisely what it owes.
- Compaction happens at task/episode boundaries (see the Digest), so the
  model's context stays inside budget while the thread lives for months.

### 2. The Record — verbatim memory, the charter's hard promise

- **Verbatim recall is a guaranteed operation.** Every acquired word,
  every full reply, every conversation worldline is recallable
  byte-exactly, by reference, by thread, and by time ("between X and Y").
  This is the charter's bar: *a human who asked a resident to acquire
  knowledge can recall every single word that was acquired.*
- **Clear-display never touches it** (P14). Purge exists — but as governed
  erasure that **cascades to every projection**: embeddings, digests,
  caches (the proven purge-reaches-the-projection law stands).
- **Opt Out (P11):** records born in an opt-out state are quarantined to
  that state's scope forever; opting in imports nothing.

### 3. Understanding — semantic memory

- Embeddings and an entity/relationship projection over the log; **vectors
  wear their model** (the standing embedding-truth law).
- **Temporal honesty comes nearly free**: records are immutable,
  timestamped, and lineage-chained, so "what is true now" vs "what was
  true then" are both answerable — the capability Graphiti/Zep exists to
  provide, here as a projection. Graphiti remains a candidate *engine* for
  this projection if building it ourselves proves expensive; either way it
  is rebuildable from the log and holds no independent truth.

### 4. The Digest — compression (JB's addition)

The pattern is the one Fable itself runs on: **compact the working view,
keep the full transcript.**

- Rolling digests are produced at episode/task boundaries by background
  consumers on the Events rail (stable event ids ⇒ retries never duplicate
  a memory).
- **A digest always cites its sources** (record refs). It accelerates; it
  never replaces. Any answer served from a digest can open the verbatim
  beneath it — every word a door.
- Digests are rebuildable from the log; a rebuilt digest must carry the
  same substance (a provable property, tested below).
- Profile distillation (what the human likes, how they work) is a digest
  family written to the human's profile — visible and adjustable by them.

## Packing the mind — context assembly

When an agent begins or continues work it packs, in priority order, within
a declared token budget: persona + profile → working state and unresolved
commitments → the relevant digests → semantic hits → verbatim excerpts on
demand. Hot digests are cached; the pack must meet the charter's
sub-second feel. **This is where compression pays**: context cost stays
bounded as history grows for years.

## The LangGraph seam

- **Checkpointer:** standard Postgres checkpointer, namespaced by agent
  identity; thread ids = conversation worldlines / objective runs.
- **The OrrethStore:** an implementation of LangGraph's Store interface
  backed by the kernel's doors. `put` → a signed, scoped record with
  provenance; `get` → verbatim by ref; `search` → the Understanding
  projection. Agents get native LangGraph memory ergonomics; the kernel
  keeps governance, metering, scope, opt-out, and purge. **A namespace is
  a label; the door is the enforcement** (access is capability-checked at
  read time, never by namespace convention alone).
- **Extraction/consolidation** (LangMem-style) runs as background Events
  consumers writing THROUGH the OrrethStore — governed, deduplicated,
  provenance-carrying.
- **Learned behavior is never silent.** Any "learned instruction" or
  prompt refinement lands as a versioned craft-edit through the gate —
  visible in Workspace Engineering, never a quiet mutation of a persona.

## Verdicts on the surveyed systems

| System | Verdict |
|---|---|
| LangGraph Store + LangMem | **Adopt the interfaces and patterns** — Store backed by Orreth; LangMem-style extraction as governed consumers |
| Graphiti / Zep | Candidate **engine** for the temporal-graph projection; never a truth-holder; hosted Zep rejected (unsigned external truth) |
| Hindsight | Adopt the **retain / recall / reflect distinction** as vocabulary for memory operations; adapter itself not needed |
| Mem0 / Supermemory | Rejected as stores; their extraction ideas inform profile distillation |
| Letta / MemFS | Reference architecture only (a second runtime) |
| Deep Agents file memory | The instinct is right, but Orreth already has governed procedural memory: **skills/prompts/playbooks are craft artifacts** on the shelf, versioned — not loose files |
| Cognee / MemOS / EverOS / A-MEM | Watch list; nothing they hold that the log + projections cannot |

## Who remembers what

- **A resident** recalls its own worldline and whatever its scope and
  capabilities grant — never more (the privacy floor stands: profile reads
  proven by eviction).
- **A human** recalls everything they were ever shown, verbatim, from the
  Bridge — and their profile is theirs to see and adjust.
- **MITL** carries the Orreth ontology as a curated digest + understanding
  over the repos and canon — the deepest reader, same laws.
- **The kernel** remembers uniformly for everyone — it is the memory, and
  it thinks in none of it (P9).

## Performance obligations (from the charter)

| Operation | Target |
|---|---|
| Verbatim recall by ref | < 100 ms |
| Semantic recall, scoped | p95 < 500 ms |
| Context pack, hot | < 300 ms (inside the 1 s first-token budget) |
| Consolidation lag (word acquired → semantically findable) | p95 < 30 s, honestly reported until indexed |
| Recall latency vs corpus growth | flat — indexes and digests absorb growth; NO sweep ever reads the whole log |

The old metabolism disease (O(floors × records) sweeps) is cured
structurally: memory work rides the Events rail; nothing polls the corpus.

## Memory proofs (the roadmap)

- **MEM-1 Total recall:** acquire a document through chat; recall every
  word byte-exactly — by ref, by ask, by timeframe.
- **MEM-2 Resume:** kill an agent mid-objective at hop N; it resumes as
  itself, at N, owing what it owed, duplicating nothing.
- **MEM-3 Digest honesty:** every digest cites sources; an answer served
  from a digest opens its verbatim; a rebuilt digest carries the same
  substance.
- **MEM-4 Changing facts:** "what is true now" and "what was true then"
  both answered correctly (the aid's test, on our temporal projection).
- **MEM-5 Quarantine & purge:** opt-out memories never leak on opt-in;
  a governed purge reaches embeddings, digests, and caches — proven.
- **MEM-6 Growth:** corpus ×10, recall latency flat.
- Plus the aid's remaining dimensions: distant dependencies, concurrent
  writers, learning-from-failure — folded into the harness.

## Explicitly open (for JB)

- **Purge policy:** residents never forget, yet governed erasure exists —
  who may purge what, and with which escalation (L2? L3? MITL)?
- **Cross-human recall:** a resident serving two humans — the privacy
  floor's exact shape in the new chat (today: profile reads are scoped;
  confirm this survives fan-out and shared scopes).
- **Graphiti build-vs-adopt** for the temporal projection — decide by
  proof cost, behind the projection contract.
- **Retention defaults** per record class (chat, acquired sources, hop
  events) — the log keeps all; the question is index and digest depth.

## What this document binds

Memory serves the charter's promises: nothing acquired is ever lost,
nothing recalled is ever partial unless it says so, nothing learned is
ever silent, and nothing grows slower as it grows older. The log is the
only truth; every other memory is an honest, rebuildable acceleration of
it.
