# 0065 — The Engine on the Chassis

*Drafted 2026-09-06 from the orreth-EnterpriseRAG proof's charter — the first kernel dive of
the proofs era (ADR 0001, covenant rule 12): every change below cites the proof requirement
that demanded it. Recon: two full code surveys of the Stacks, the projections, the gateway,
and the test estate, 2026-09-06 (Appendix A).*

***Status: 🟡 DRAFTED · LOCKED — L1 (flows, not floors) and L2 (the rule-9 gate for the two
plane projections) both taken by JB's word, 2026-09-06, with the options' outcomes spelled
out; spoonfuls awaiting the build season.***

## 1. The demand, verbatim (the proof's charter)

The orreth-EnterpriseRAG proof (private repo; publicly announced in `PROOFS.md`) demands:

> "We are integrating 11 RAG architectures and the ability for the Agentic flow to reason the
> correct flow … through 'auto' AND the ability to select the RAG Architecture to use in the
> request(s) for humans, residents, and agents." — charter addendum 4
>
> "When retrieve runs and selects the architecture to collect data, it should reflect the
> selected architecture somewhere so the user can see what was selected." — addendum 4
>
> "This Proof … will replace our current RAG after we complete." — addendum 4 (the endgame)
>
> Full GraphRAG — knowledge graphs built from ingested corpora — locked 2026-09-06; the
> selector menu locked the same day: Auto is its own switch position, Modular is the chassis,
> and the eleven selectable styles are **Naive · Advanced · Hierarchical · Multimodal ·
> Multi-Agent · Reasoning-First · Memory-Augmented · Graph · Hybrid · HyDE · Corrective**.
>
> "We will want to test as each type (monitoring)." — addendum 2

This dive designs the engine those demands run on. It deliberately does **not** design the
Router's brain (Dive II), guardrail content (Dive IV), the ingest/extraction matrix (Dive V),
or any surface (Dives VII–VIII). It designs the chassis, the variants as declarations, the two
missing projections, the identity of every act, and the harness that tests each type from its
first breath.

## 2. The problem — what the recon found

The Stacks (0038) built the right laws and honest scaffolds; the proof's demands land on four
walls:

1. **The rows are functions, not an engine.** All seven rows execute in the worker process as
   Python lambdas over a projection **rebuilt from scratch on every ask**
   (`orreth_sim/stacks.py:141-205`), fed by a shim that makes 1+N+M REST calls per question
   (`console_worker.py:6196-6360` — its own comment confesses: *"the cap is honest: a standing
   projection with a rebuild beat is sp3+"*). No row calls a model; no row touches pgvector;
   the embedder is a hashed word-bag (`stacks.py:76-86`). Eleven variants on a per-ask rebuild
   is a cost wall, not an engine.
2. **The graph was promised and never built.** 0038 locked *"graph rides a Postgres projection
   first (Shape A holds)"* (`0038:117-119`); what exists is an in-memory term-co-occurrence
   dict, quadratic in chunk length, discarded per call (`rivals.py:48-87`). Full GraphRAG —
   entity/relation extraction at ingest — has no extraction, no tables, no door.
3. **Variants have no declaration.** The routing standard's `built` list is a hand-maintained
   array in three places (`dispatcher.py:42`, `tournament.py:74`, `console_worker.py:6610`);
   a malformed standard lands unvalidated and is caught only at read time. There is no
   registry a selector menu, a workshop, or a gate can trust.
4. **The harness under-measures.** The tournament grades three 0033 axes by string arithmetic
   and computes **neither latency nor cost** despite 0038 §4 naming both
   (`tournament.py:103-118`); the ask lane and the yardstick lane can read **different routing
   standards** (ask lane at f:naive, promotions planted at the universe whose asset tags the
   stacks pull filters out — `console_worker.py:8965` vs `:6752-6760`); `temporal` and
   `comparative` classify but route to default (`dispatcher.py:45-60` vs `STANDARD_V1`); and
   the recall-warmth tap lives in `~/.orreth/stacks/*/recalls.json` — a projection the purge
   does not reach.

## 3. The shape

### 3.1 The chassis — six module contracts, one law

The engine is the Modular-RAG pattern made Orreth-native: **six module boundaries**, each a
typed contract, each boundary emitting a signed act-graph node (KCR-0004's format, designed in
Dive III; until then, the existing record grammar carries it):

```
understand → retrieve → refine → construct → generate → enhance
```

- **Cognitive modules** (understand, refine-by-mind, generate, enhance) execute cognition-side
  — worker or capability — through the governed gateway, exactly as today
  (`console_worker.py:3629-3684`; the plane never sees the prompt).
- **Retrieval primitives** (retrieve, refine-by-rank) execute over **plane projections** under
  the one-truth law: authorized ids first, projection math second — the invariant
  `cosine_for` already models (`pg.rs:184-197`: score only what the node served).
- Every module invocation pins its assets (craft ref via `context_hash` — the mechanism
  `mind.py:199` already uses) and, from this dive on, **its variant**.

### 3.2 Variants as declarations — the 0063 pattern, applied

A variant is **data on two layers**, following the dials exactly
(`orreth_sim/dials.py:49-433`):

- **The registry (firmware, in code):** `orreth_sim/variants.py` — for each of the eleven:
  `name`, `stages` (its composition over the six modules), `requires` (capabilities: meaning
  axis, graph projection, vision mind, decomposition mind…), `cost_class`, `blast`, `why`,
  and its `delta` sentence (what this style does that naive does not). Changing the registry
  is a release.
- **The configuration (craft, on the shelf):** `variant-*` assets in their **own drawer**
  (one new `_craft_category` branch — `console_worker.py:11727-11746`): per-variant dials
  (k, thresholds, fusion weights, hop depth) — prod-editable through the one door, gate-checked
  **before landing** (`gate_check` refuses an undeclared stage or an unavailable capability at
  the door, with a teaching on every sibling), falling back to genesis **loudly** on a flawed
  head. This is what the proof's Workshop edits and versions.
- **The routing standard becomes a consumer**: its `built` list derives from the registry ×
  the floor's actual capabilities — never hand-maintained again.

The razor holds: *declaration = firmware; configuration = purpose.* And the selector
requirement is discharged at the record layer: the standard's `built` + the registry ARE the
menu every channel renders.

### 3.3 The seven grow into the eleven — row by row, nothing thrown away

| Menu style | Grows from | What it gains (and the demand that pays it) |
|---|---|---|
| **Naive** | `f:naive` | Nothing — the baseline control stays the yardstick (0038 law). |
| **Advanced** | `f:rerank` | A real reranker mind via the Stable + query rewriting (charter: professional retrieval beyond baseline). |
| **Multimodal** | `f:multimodal` | Per-modality embeddings; the eye still honestly awaits ada's vision mind — the refusal text stays until it doesn't have to. |
| **Graph** | `f:graph` | **Pays 0038's Shape-A debt**: the Postgres graph projection + extraction at ingest (Full GraphRAG lock). |
| **Hybrid** | `f:hybrid` | Real fusion: pgvector × BM25 × graph via RRF with standing weights (the machinery `meaning.py:127-177` + `main.rs:600-651` already model). |
| **Multi-Agent** | `f:swarm` | Governed decomposition minds; the async fan-out stays parked (0038's park stands until a proof demand pays it). |
| *(Auto)* | `f:router` + Dispatcher | **Dissolves into the Router** — not a menu item; Dive II's subject. The f:router flow retires honorably, on the record. |
| **Hierarchical** | *new* | A tree-index projection for long documents (page/section ranges — the wiki research's short/long split, seam-replaceable). |
| **Reasoning-First** | *new* | Decompose → structured retrieval plan (a signed record) → targeted retrieves → evidence pack. |
| **Memory-Augmented** | *new* | Memory retriever + query rewriter over conversation worldlines before external retrieval. |
| **HyDE** | *new* | Hypothetical document generation → meaning-axis search with the hypothesis's vector. |
| **Corrective** | *new* | Post-retrieval faithfulness check → targeted re-retrieve — the critic's three moves entering the retrieval loop. |

New variants land **scaffold-first** (deterministic, law-tested, conformance-green — the house
method) and gain their minds through the Stable as each saddles; a variant whose `requires`
are dark serves the honest refusal, one face.

### 3.4 The projection estate grows by two (the embeddings pattern, copied)

The plane's `embeddings` lifecycle is complete and copyable (~90 lines of `pg.rs` + three
handlers): optional DDL → tokened write door → tokened worklist door → purge eviction in the
same tombstone handler → **reads only over ids the node already authorized**. Two new
projections ride it:

1. **The chunk/tree projection** — kills the per-ask rebuild wall and carries Hierarchical:
   standing chunk rows (`node_scope, record_id, seq, span, hash`, pointers never blobs — the
   `pg.rs:1-9` law) with chunk-grain vectors, plus tree nodes (section → page-range) for long
   bodies. Rebuildable from the log; evicted at tombstone; the sweep beat mirrors
   `embed_beat` (`console_worker.py:2423-2461`).
2. **The graph projection** — `graph_nodes` / `graph_edges` (`node_scope`-partitioned, witness
   refs on every edge: *the citation IS the edge's provenance*, as `rivals.py:50-51` already
   teaches); extraction runs cognition-side as an `extract_beat` (scaffold extractor first,
   governed mind when saddled); traversal reads **only within the authorized id set** or it
   would become a second read path — refused by design.

Purge reach is non-negotiable for both: the tombstone handler that already does `save_purged`
+ `evict_embedding` (`main.rs:521-531`) gains two evictions beside them. And the dive pays a
found wound while it's here: the recalls warmth tap moves from `~/.orreth` JSON into
purge-reachable, declared-retention territory (the observatory's instrument tier or a PG
projection — spoonful decision).

### 3.5 Variant identity on every act (the reflect-the-selection demand)

Three seams, zero new stores:

- **The meter already keeps whatever we say**: `/model/meter` persists the verbatim request
  body (`main.rs:864`); `variant`, `pipeline`, and `arm` fields land in `meters.entry` today —
  three call sites gain a field; per-variant cost becomes a query (aggregation fold in
  `model.rs:325-358` grows when the Observatory wants it).
- **The answer record wears the variant** exactly as A/B answers wear their arm tag
  (`console_worker.py:6622-6634`) — every channel (canvas, API reply, librarian) reads the
  selection off the record, never from a side channel.
- **Per-call override follows `_klass`**: `_variant=` rides the same kwarg seam
  (`mind.py:174`), so residents and agents pass a variant per call; absent = Auto.

### 3.6 The harness from the first breath ("test as each type")

- **Per-variant law suite**: one `tests/test_variant_<name>.py` per style, asserting the four
  canonical laws (cited · rebuild-identical · purge-silent · one-truth) plus **one delta
  assertion** naming what the style does that naive cannot (the `test_rivals.py:27-38` graph
  edge is the model). Scores never in assertions; determinism always
  (`test_tournament.py:46-53`). Optional capabilities skip with `needs_axis`-style markers,
  matching the plane's stays-dark posture.
- **The tournament grows honest axes**: `grade()` gains latency and metered cost (0038 §4's
  unpaid promise), `FLAVORS` derives from the registry, and the one hard-coded 7
  (`test_tournament.py:64`) dies.
- **The eleven-arm experiment is free**: `experiment.py` already handles N arms
  (`:102-109`, `:75-88`); the eleven-arm tournament and the eleven-arm A/B are the same
  object at different confidence levels.
- **Two-tier judging** (proof lock): deterministic grades in conformance; vera's live bench
  for standings that humans act on (`yardstick_run`'s pattern, `console_worker.py:12090-12194`).
- **Benchmark evidence lives in the proof repo** (the Hybrid's split); the harness lives here.
- And the **two-lane wound closes**: one routing standard readable by both the ask lane and
  the yardstick lane, with `temporal`/`comparative` finally routed (the staged v2 pays).

## 4. The razor applied

| Layer | Class | Changed how |
|---|---|---|
| `variants.py` registry, module contracts, projection DDL/doors | **Firmware** | Release only |
| `variant-*` configuration, routing standard, per-variant question sets | **Craft** | Prod, through the one gate, versioned siblings |
| Selection per ask (`_variant`, menu picks) | **Runtime** | Free, always recorded |

## 5. The locks (JB, 2026-09-06)

- **L1 — Flows, not floors.** The eleven variants are **flows over one log per world** —
  declarations + compositions — not eleven embodied hulls. The seven existing e:rag hulls:
  f:naive keeps the log; the six empty hulls retire honorably on the record (dormancy, never
  deletion), and embodiment is reserved for experiment arms when a standings fight needs a
  named machine. *(0038 already blessed "dev: one hull is fine — projections are light".)*
- **L2 — The rule-9 gate for the plane's two projections.** Chunk/tree and graph tables +
  doors land in `pg.rs`/`main.rs` following the embeddings pattern verbatim — with the
  0038 lock honored: this is the *separate, evidence-carrying gate* that lock demanded for
  code entering the core retrieval path. Evidence attached: the recon's cost-wall and
  Shape-A-debt findings (§2), and the proof charter's Full-GraphRAG + production-grade
  demands.

## 6. The spoonfuls (proposed order)

1. **sp1 — The registry and the drawer.** ✅ **LANDED 2026-09-09 — the eleven are
   declared, the menu speaks, the gate teaches.** `orreth_sim/variants.py`: the charter's
   eleven as firmware declarations (title · executing row · stages over the six module
   boundaries · requires · cost class · delta · why · blast · genesis knobs); `resolve()`
   speaks both vocabularies (legacy flow names map — rerank→advanced, swarm→multi-agent;
   router resolves to none, Auto being a switch position, never a style); **`built()`
   DERIVES from registry × standing flows — the three hand-kept arrays retire**. The
   routing standard's genesis moved to v2: canonical route names, and the recon's two
   classified-unrouted shapes finally routed (comparative→multi-agent serves TODAY;
   temporal→memory-augmented names the right row and falls loudly until sp4 — the
   Dispatcher's own law, never a special case); `dispatch()` normalizes both vocabularies
   so no honest choice falls over a name. The `variants` craft drawer stands: variant-*
   is PURPOSE by the razor (prod-editable), may land fresh like a dial, is gate-checked
   BEFORE landing (undeclared style → the menu; undeclared knob → the declared ones +
   the blast; wrong type/negative → the declaration; clean turns land CANONICAL), and
   every sibling carries the style's teachings. The two-lane wound's first stitch: the
   universe pull keeps routing-standard rows, so a promotion planted above reaches both
   lanes' node. *Proven live on the rig: «advanced» (a menu name that never existed
   before) served with the envelope confessing `variant: advanced` while the rerank flow
   ran underneath; «hyde» (declared, unbuilt) fell LOUDLY to the baseline; «quantum»
   refused naming the menu; the craft door refused `turbo` with the teaching and landed
   `{"hops": "2"}` canonical as 2 with teachings on the sibling. Suite 398→407 (nine
   registry laws); Rust green.* *Honest remainders: a landed config head is real craft
   but takes EFFECT when sp4 threads `config()` through each flow — named, never silent;
   the live rig's shelf standard stays v1 until the promotion lane argues v2 (genesis
   plants once — fresh worlds get v2); the universe-pull stitch is wire-postured, its
   live proof rides the first real promotion.*
2. **sp2 — The chunk/tree projection.** ✅ **LANDED 2026-09-09 — the ask stops rebuilding
   the shelf.** The plane grew the standing projection under L2's gate, the embeddings
   lifecycle copied verbatim: the `chunks` table (POINTERS into derived text, never blobs
   — level 0 leaves with chunk-grain vectors, level ≥ 1 tree parents for Hierarchical,
   every row wearing the policy hash that cut it), three tokened doors (`/chunks` write —
   landing replaces a record's rows whole; `/chunks/missing` worklist — material first,
   and answering ONLY for the ids the caller sends; `/chunks/search` — chunk-grain cosine
   over exactly the ids the caller's retrieve authorized, cosine_for's law at chunk
   grain), and eviction in the same tombstone breath as the vector's. **One knife**: the
   lane law extracted from `project()` into `stacks.derived_text()` + `lane_spans()` so
   the rebuild and the sweep cut identically BY CONSTRUCTION; the pure law lives in
   `orreth_sim/chunklaw.py` (deterministic cut · lossless spans · piece hashes · policy
   naming · tree parents covering exactly their children · a short text earns no tree).
   The worker's `chunk_beat` sweeps on a new dial (`chunk-every` 120) — per-floor clocks —
   and the naive row's PRODUCTION path became the standing read: query embedded once,
   plane-side search, spans sliced from text already in hand, every hash re-checked (a
   mismatched row falls the whole ask back to the rebuild, loudly); the in-process
   rebuild stands behind as the dev fallback. *Proven live on the rig: f:prod's sweep cut
   253 material records in one beat (material-first ordering); the next sweep touched 1;
   an SDK ask answered FROM the shelf — «standing shelf served 4 hit(s) — no rebuild»,
   3.1 s end to end, citations riding, the confession floor's honesty intact. And the
   FIRST live sweep caught a real wound the design had missed: the global worklist let
   the sweep mark records its capped pull had never seen — a lie that would poison the
   projection; fixed in the hour (the sweep judges ONLY what its own pull authorized; the
   poisoned rows truncated — the projection is rebuildable by design). Suite 407→416
   (nine chunk laws) + Rust green.* *Honest remainders: only the baseline row reads
   standing today — the other flows thread at sp4 with `config()`; temporal asks
   deliberately take the rebuild (its time law); the confession floor is
   embedder-relative and the standing lane's fastembed scores read lower than the
   hashed-bag's — sp4's harness measures before any floor turns; tree rows STAND but
   nothing walks them until Hierarchical's scaffold; a live purge-reach walk awaits an
   ungated purge (the suite holds the law).*
3. **sp3 — The graph projection.** ✅ **LANDED 2026-09-09 — 0038's Shape-A debt paid: the
   graph lives in Postgres, and every edge carries its witness.** The plane grew
   `graph_nodes` + `graph_edges` in the ALWAYS-ON DDL (walking is pure SQL — the graph
   stands even where the meaning axis is dark): terms as nodes with per-record mention
   counts, within-span co-occurrence as edges, each edge naming its record · span ·
   lane · the piece's hash (the citation IS the edge's provenance, the sim's own law
   kept), and every row wearing the extraction law's version (extractor name × the chunk
   policy — either turning re-cuts the world visibly). Three tokened doors (`/graph`
   write — replaces a record's rows whole; `/graph/missing` — answering ONLY for the
   caller's own ids, sp2's live lesson born into this door; `/graph/walk` — witnesses
   binding the ask's terms scored by pairs bound, a one-term ask falling to touching
   edges dampened, all inside EXACTLY the authorized set or it would be a second read
   path); eviction rides the tombstone breath beside the chunk and vector evictions —
   what only the dead record knew is forgotten with it. **One term law**:
   `graphlaw.terms()` owns the definition and `rivals` delegates by identity, so the
   rebuild's graph and the standing graph can never disagree about what a term is. The
   worker's `extract_beat` (new dial `extract-every` 180, per-floor clocks, driving from
   its own pull) runs the scaffold extractor — deterministic co-occurrence, the law
   version ready for a saddled extraction mind to bump; and the graph row's PRODUCTION
   path became the standing walk with the same hash drift-catch as the shelf, the
   in-process rebuild standing behind. *Proven live on the rig: f:prod extracted 253
   records in one sweep (floors with nothing confessed honestly — «0 extracted · N
   marked non-material»); an SDK ask with `variant: graph` answered from Postgres —
   «the graph walked 4 witness(es) in Postgres — no rebuild», 3.0 s, the envelope
   confessing `graph`, the reply carrying the binding pair and the witnessing chunk.
   Suite 416→424 (eight graph laws: one term law by identity · deterministic witnessed
   extraction · within-span binding only · no echoes · the cross-document edge found by
   the walk · the walk never leaves the authorized set · purge forgets what only the
   dead record knew · worklist honesty). Rust green.* *Honest remainders: the extractor
   is the SCAFFOLD (term co-occurrence — real entities and typed relations arrive when a
   governed extraction mind saddles, bumping the law version; Full GraphRAG's
   ingest-side extraction matures with 0069's minded eyes); hop depth stays 1 (the
   variant's `hops` knob threads at sp4); the graph and chunk sweeps share the pull's
   cost — a shared per-beat pull is a small optimization when it itches.*
4. **sp4 — The five new styles + the eleven-arm tournament.** ✅ **LANDED 2026-09-09 —
   THE MENU ANSWERS WHOLE: eleven declared, eleven serving.** The five new compositions
   (`orreth_sim/styles.py`), scaffold-first by the house method, each built from
   machinery that already stands: **Hierarchical** climbs from the best chunk to its
   SECTION via sp2's tree law — a long document answers from the right floor of the
   building; **Reasoning-First** decomposes the ask, lands the retrieval PLAN as a
   signed record where a seat stands (the audit door opens on a whole ref), and runs
   targeted retrieves per step; **Memory-Augmented** reads the chronicle lane first and
   confesses what remembering added to the ask (worldlines arrive with 0070);
   **HyDE** searches by the imagined answer — the strongest seed's text stands in for
   the drafting mind's hypothesis (pseudo-relevance feedback, named honestly);
   **Corrective** checks its catch against a faithfulness floor and takes a VISIBLE
   second look, `corrected` on every hit either way. **The hand-kept tuple dies**:
   `FLAVORS` derives from the registry (eleven rows, menu order; the router row retires
   from the standings — Auto is a switch, never a contestant), and the 0038 §4 promise
   is paid — the tournament grades **latency (measured, never exactly asserted — the
   determinism law) and cost** (the context a style asks a reader to consume,
   deterministic) beside the three science axes, per entry and in the standings.
   **config() finally threads**: every row — the six old and five new, the standing
   lanes included — reads its style's craft at the door (`variants.config_for`), so the
   Workshop's knobs take effect where the work happens. *Proven live on the rig: all
   FIVE new styles served AS THEMSELVES through the SDK (no baseline falls); the knob
   walk — `variant-naive` k turned 4→2 through the one-motion door, the very next ask
   served exactly 2 citations, canon restored. Two finds the walks earned: a retrieval
   PLAN echoed into its own projection and answered the ask it planned (machinery-talk
   is not memory — the lane law now excludes retrieval plans), and the stacks pull
   never carried `variant-*` craft so a turned knob was silently inert on the wire —
   both paid in the hour. Suite 424→450 (five per-variant law files: the four canonical
   laws + one delta each; the tournament's eleven-arm + axes assertions; built() now
   expects the whole menu). Rust green.* *Honest remainders: the scaffolds confess
   their stand-ins (HyDE's drafting mind, Reasoning-First's planner, Memory-Augmented's
   worldlines — each saddles through the Stable and 0070/0069 in their dives); graph
   `hops` stays declared-unthreaded until the walk earns multi-hop demand — named, not
   silent; the five new styles ride the in-process projection (their standing-lane
   reads follow the naive/graph pattern as each earns it).*
5. **sp5 — Identity everywhere.** ✅ **LANDED 2026-09-09 — the selection is never a
   secret, anywhere.** Three seams, zero new stores, exactly as designed: **the meter
   wears the variant** — `client.meter()` grew `variant=`, `GovernedThink` threads it,
   and the plane keeps the line verbatim, so per-style cost became a query the moment
   the first line landed; **`_variant` rides the `_klass` seam** — a mind's caller
   attributes any thought to a style per call, absent = Auto; **the answer record wears
   its selection as a TAG** (`variant:<style>` — the 0043 arm-tag pattern at the style
   layer): the glass and any query read it off the record, never a side channel. And
   the **warmth tap earned declared retention**: entries expire at save by the
   `recall-days` dial (the same word that bounds every governed look-back), so a purged
   record's residue dies on the dial's clock — the metabolism's reader was always
   alive-gated, and the tap stops being the one file no law reached. *Proven live: the
   meter line `hyde · sp5-walk · 5` read back FROM POSTGRES; the exchange record's tags
   `["ask", "variant:graph"]` read back from the records table; and THE GLASS SPOKE THE
   SELECTION in its own sentence — the parlor's reply to a human carried «the
   dispatcher chose "naive" — no shape matched — the default row serves» with the whole
   choice ref, the reflect-the-selection demand discharged where a human actually
   reads. Suites 450 + SDK 24 (parity held) + Rust green.* *Honest remainders: the
   per-variant cost AGGREGATION fold (the Observatory's view) waits for the Observatory
   to want it — the data is in the ledger now; diary/run records deliberately untouched
   (their schema is validated — a variant annotation there is its own small motion).*

Each spoonful closes 371+-green with the honest-boundary rows it moves updated in the same
commit; the dive closes WHOLE only when the eleven serve, the harness grades them all, and
the selection shows in the glass.

## 7. The honest boundary rows this dive moves

- `the-honest-boundary.md:64` (retrieval rows are deterministic scaffolds; sim judge) — moves
  per-variant as minds saddle and axes land.
- `the-honest-boundary.md:67` (pgvector projection live; production-scale rebuild unproven) —
  the standing chunk projection is the rebuild story's first real test.
- New rows at close: the graph projection (proven or partial, honestly), the eleven-variant
  registry, the retired hulls.

## Appendix A — recon summary (2026-09-06, two survey reports; full citations in the surveys)

Load-bearing facts this design stands on: only f:naive holds a log (`console_worker.py:8965`);
projection rebuilt per ask over REST (`:6196-6360`); no row uses LLM/SQL/pgvector; the
embeddings lifecycle is the copyable plane pattern (`pg.rs:93-197`, `main.rs:521-651`);
`/model/meter` persists arbitrary fields verbatim (`main.rs:864`); `_klass` is the per-call
override precedent (`mind.py:174`); craft pinning + `context_hash` already pin asset versions
(`mind.py:199`, `console_worker.py:11773-11861`); the dials are the declaration-class
precedent (`dials.py:49-433`); experiment arms generalize to N (`experiment.py:75-109`); the
privacy floor gates every projection first (`canon.py:121-126`, `stacks.py:158`); found
wounds: two-lane standards, unrouted temporal/comparative, missing latency/cost axes,
purge-unreachable warmth tap, PUT-side dispatch stub (parked to the Router dive).
