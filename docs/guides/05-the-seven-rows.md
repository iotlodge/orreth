# Guide 05 — The Seven Rows of the Library

*How the Stacks work: seven RAG variants over one truth, the organ that routes
between them, and how Objectives, Intentions, Observations, and thought:actions
live in time so knowledge can be stored and retrieved in ways a single database
never could. Companion to `../design/0038-the-stacks.md` (the spec) — this is
the working explanation, for humans at the glass and builders of agents alike.
Guides 03–04 remain reserved (Resident Field Guide · Building Agents/SDK).*

---

## 1. Why the Stacks exist

Everything that enters the universe, and everything anyone asks of it, passes
through two motions: **data in** and **knowledge out**. The Stacks are how
Orreth governs both with the same musculature — what JB named **Closed-Loop
Bi-Directional RAG**:

- **In**: every document, observation, and finding is *purified at the door* —
  it lands exactly once as a signed record: provenanced, quarantined until
  corroborated, owned by the universe. No copy anywhere. Ever.
- **Out**: every question — human or agent — is routed to the retrieval flavor
  its *shape* deserves, answered **with citations that walk back to real
  records**, or with an honest unknown.
- **The loop closes**: every routing choice, every answer, and every piece of
  feedback is itself a record — so the universe *learns which ways of
  remembering work*, from its own receipts, through time.

RAG here is not a feature beside the universe. It **is** the universe's data
metabolism.

## 2. The one law everything rests on

> **The signed log is the truth; every index is a rebuildable projection.**
> *(0022 — and the line 0038 must never cross.)*

The seven rows are **seven projections plus seven flows over ONE truth — never
seven stores**. Consequences, each load-bearing:

| Law | What it means in practice |
|---|---|
| **Ingest once** | A document becomes one signed MemoryRecord through the gateway. The rows never hold copies — they *derive* their indexes (vectors, graph edges, multimodal embeddings) from the log, each on its own beat. |
| **The purge reaches everywhere** | A crypto-shredded record stops speaking in every row at once — because every row rebuilds from the log, and the log no longer says it. |
| **One authorization contract** | A row may only rank what the asking token may see. Seven flavors, one gate — retrieval never becomes a side door. |
| **Rebuildable = disposable** | Any row can be torn down and regrown without losing a byte. That is what makes seven *experiments* affordable — and what makes the tournament honest. |

## 3. The seven rows, one by one

All seven share the eco-level commons — the chunking policy, the embedding
standard, the prompt template — versioned assets on the shelf that grace may
improve through the lanes. **A row is only its delta.**

### Row 1 — `f:naive` · the baseline control
Chunks → vectors → cosine similarity → cited answer. Deliberately *nothing
else*. A relevance floor keeps it honest (a baseline that answers everything
answers nothing), and an off-corpus question gets an honest unknown. Its job
is to be **the yardstick**: every other row must beat it *on the record*, or
retire honorably. Its mediocre answers are not bugs — they are the standings'
evidence.

### Row 2 — `f:rerank` · precision earns a second pass
Retrieves *wide* with the same vectors (3× the candidates), then **re-scores
narrow** with a precision criterion before answering. Cheap first net, careful
second look. Chosen when the ask is exactness-shaped — quoted phrases,
"exactly", "verbatim". The classic fix for "the right answer was rank #7."

### Row 3 — `f:multimodal` · the eye of the library *(flow lands in the tournament)*
A multimodal embedder projects images, diagrams, and media into the same
searchable space as text, and media rides the answer's context. This is where
0029's honestly-dark artifacts ("admitted, awaiting an eye") finally get read.
Chosen when the ask names media.

### Row 4 — `f:graph` · walking, not measuring
An extraction pass derives **entities as nodes and their co-occurrences as
edges** — and every edge *remembers the chunk that made it*: the citation IS
the edge's provenance. A relationship-shaped ask ("how is X connected to Y?")
is answered by **walking** the edges that bind its terms, not by measuring
which chunk sits nearest in vector space — a fundamentally different question,
which distance often gets wrong. The graph lives as a **Postgres projection**
(Shape A holds); a dedicated graph store must be *earned* by standings
evidence, arriving through allen at JB's gate.

### Row 5 — `f:hybrid` · what both ways can defend
Vector similarity finds *the like*; graph walking finds *the bound*. The
hybrid fuses the two scores at query time and ranks what **both** ways can
defend — the strongest general-purpose row when a question is partly about
likeness and partly about connection.

### Row 6 — `f:router` · strategy within the row *(flow lands in the tournament)*
Where the Dispatcher chooses *between* rows, the router row chooses *within*
itself — per-ask tactics (which sub-strategy, how wide, whether to iterate)
before answering. Self-routing retrieval, useful when one row must serve mixed
workloads.

### Row 7 — `f:swarm` · many hands, one cited answer *(flow lands in the tournament)*
The multi-agent row: a coordinator **decomposes** a broad ask into sub-asks,
fans them to engines and tools (other rows, web search, the farm's services),
and **recomposes** one answer whose every claim still carries its citation.
Chosen for cross-source asks ("compare X and Y across sources"). This row is
why the record-driven seat progression matters: its fan-out rides requests
through time, not function calls.

## 4. The Dispatcher — the organ that chooses

Choosing is universal fabric, so it is an **unembodied organ** — split the way
the body splits:

- **The reflex.** In the put/get path, *after* the gateway's authorization —
  never around it. It reads the ask's **shape** deterministically (no LLM in
  the hot path): media words → multimodal · relationship words ("between",
  "connected", "depends on") → graph · cross-source words → swarm · exactness
  words → rerank · otherwise → the baseline.
- **The standard.** The rules above are **data, not code** — a versioned asset
  the librarian tends. Revisions ride the improvement lanes: proposed from
  receipts, graded by governance, human-gated on rewrites.
- **Every choice is a record.** Which flavor, which rule, why, what was wanted
  — signed, walkable. *"Why did this question go to the graph row?"* is a
  spacetime query, not a shrug.
- **The loud fallback.** A row that is chosen but not yet built **falls to the
  baseline loudly, with both truths in the record**. The universe never
  pretends a row it does not have — and the day f:graph came alive, the same
  question's before/after lived in the ledger: the morning's fallback became
  the evening's route. The universe visibly got smarter, on the record.

## 5. One door for humans, one door for agents — the same organ

**Humans** ask in the parlor, in plain words. A question at *any* of the
librarian's seats (one mind, many seats — same DID lineage) flows through the
Dispatcher **by default**: no ceremony, no travel. The ask is carried to her
rag seat with its **origin pinned into the choice record** ("carried from my
seat at u:demo"). Questions about *her* stay hers.

**Agents** speak the typed ladder (0030): an agent's retrieval or storage ask
is an **Intention carrying lineage to a human Objective** — the same law
allen's door enforces for infrastructure. No ancestry, no entry. Both kinds of
caller pass the same gateway, the same authorization, the same Dispatcher, and
receive the same cited-or-honest answer. Interoperability is not a feature
here; it is the shape of the door.

## 6. O·I·O·T in time — why this enables what databases cannot

Everything above stands on one architectural bet: **Objectives, Intentions,
Observations, and thought:actions are all records on one timeline**, each
knowing its lineage up the ladder. That yields capabilities that no
conventional store-and-index stack has:

1. **Provenance as a walk.** Any answer's citation walks to a record; any
   record walks up its ladder — *which Intention wrote this, descending from
   whose Objective, observed by whom, when*. "Why do we believe this?" is a
   query with a complete answer.
2. **Placement is the universe's law, not the caller's guess.** A human or
   agent says *store this* / *find this*; the universe decides where truth
   lives (object store for bodies, the log for records) and **which
   projections should index it** — the Dispatcher's PUT side. Callers speak
   intent; the substrate owns physics.
3. **Time is an axis of retrieval.** Records carry both clocks (lived
   universe-time and wall-clock); the spacetime window scrubs them. "What did
   we believe *then*?" and "what changed *since*?" are first-class asks — and
   the serials desk turns *difference over time* into news.
4. **Memory has a metabolism.** Raw records distill upward (0003's pyramid),
   consent withdraws (the purge, reaching every projection), sources get
   recalled (lineage walks) — and the rows *inherit all of it for free*
   because they are projections of the governed log, not parallel stores.
5. **The retrieval system learns itself.** Choices are actions on the record;
   gradings and feedback (human and agent) are the reward; routing-standard
   revisions are the policy update. The tournament's standings feed the
   librarian's proposals — reinforcement learning wearing Orreth's clothes,
   with a human gate on every rewrite. The seven rows aren't just seven ways
   to answer; they are **seven hypotheses the universe tests against its own
   history, forever**.

## 7. What breathes today, what arrives with the tournament

**Standing now**: the one-truth ingest (`shelve …`) · the baseline, rerank,
graph, and hybrid flows, cited and law-proven (217/217) · the Dispatcher with
its v1 standard, universal at every librarian seat, plain questions routed by
default · the choice ledger accumulating · the field-join door (moons for a
standing eco, nothing doubled) · six rival hulls staged at the human's gate.

**The tournament brings**: the multimodal, router, and swarm flows · 0033's
science grading every pass (recall fidelity, context efficiency, information
gain) · 0005 standings ranking the rows · the Stacks panel in the librarian's
room · the routing standard's v2 through the proper lanes · and the first
**promotion** — a winning row earning its place as a named strategy in the
librarian's own planner, on evidence, at the human's gate.

---

*A library is not seven collections. It is one collection, seven ways of
walking the rows — and a librarian who knows, because she keeps the receipts,
which row answers which question.* 🥂
