# 0022 — The Memory Construct (the brain under the universe)

*Design draft for review — proposed by Fable 5 (design owner), from JB's Universe-Brain
delegation (2026-07-10, `../vision/the-universe-brain.md` §2: storage is "entirely up to
you… 1, 2, 3 database architectures if you need… never design what can't deploy or operate
federated; the objective is FAST access across the Universe"). Inputs: a 2025-26 storage
research brief and a full access-pattern inventory of the running system (both 2026-07-10,
this session). Discharges the pgvector pre-stage (decisions ledger, 2026-07-08) — this is
the promised 0002-amendment dive. **All decisions closed: design-owner pass + JB's
bytes-local lock, 2026-07-10 (§10).** Mechanism lands per §8's phases.*

---

## Why this is a keystone

JB, closing the vision session: *"The brain is really the secret to making all this work."*
Every organ reads and writes through the store — the Librarian's all-knowledge, the
fingertip's sliver-feeding, the profile, the markers, the purge, recovery of a floor after
loss. And the inventory shows the current plane is **correct but unindexed**: `/retrieve`
is an O(n) scan that hits a wall near 10k records, presence aggregation full-scans three
collections every beat, runs are not persisted at all, and retention is classified but
never enforced. The design below keeps every invariant the plane already enforces and
gives it a spine that scales from one laptop to a federated enterprise **on the same
contracts**.

---

## 1. The frame — the log is the truth; every index is a projection

> **The signed, append-only record log is the sole source of truth. Every queryable
> structure — vector index, lexical index, lineage closure, rollup Parquet, presence
> cache — is a deterministic, rebuildable projection of that log.**

This one commitment (the event-sourcing lesson, arXiv 2605.21997) buys everything else:

- **Engine choices become dials, not marriages.** A projection can be rebuilt on a new
  engine from the log; the records, sync, and query *contracts* never couple to an index.
- **Recovery is replay.** A floor rebuilt from its log (+ object store) is the floor —
  the "recorded for recovery, resiliency" promise of the vision doc, made mechanical.
- **The purge interlock is definable**: crypto-shred the record, then **rebuild or evict
  the projections minus that record** — the hard rule that erasure must reach embeddings
  (§6) falls out of the frame instead of being a special case.
- **Federated merge is tractable**: two seats reconcile logs (content-addressed,
  signed), never indexes.

---

## 2. What the store must serve — the ground truth

The inventory maps **eight access families**, all essential (removing any breaks an
invariant):

| # | Family | Shape | Today | Design target |
|---|---|---|---|---|
| 1 | Point-hash | get record by ContentHash | O(1) ✓ | keep |
| 2 | Time-range | scoped `[from,to]`, newest-first | **O(n) scan** | B-tree `(scope, occurred_at DESC)` + partition pruning |
| 3 | Tag/kind | `tags @> [...]`, `kind =` | **O(n) scan** | GIN on tags; partial index on kind |
| 4 | Lineage | `derived_from` walks (recall, redaction) | **O(n·d)** | GIN on derived_from + recursive CTE (depth-guarded) |
| 5 | Cross-tier | escalate remainder up, merge/dedup | ✓ (contract) | unchanged; served by 2-4 per tier |
| 6 | Monoidal | rollups by (scope, goal_hash, bucket) | O(n) scan | index `(scope, goal_hash, occurred_at)`; Parquet for deep time |
| 7 | Presence | per-beat roster aggregation | **O(n+m+p)/beat** | incremental caches, invalidate-on-write |
| 8 | Queue | HITL request polling | small-n ✓ | keep |

**Invariants preserved by construction** (inventory §8): per-scope high-water
monotonicity · complete `derived_from` chains, annotate-never-rewrite · recall transitive
closure · monoid associativity with pointer-only contributors · authorization at the gate,
not per-record · **uniform refusal on every new path** (covenant rule 4) · budget-miss ≡
authz-miss.

**New consumers this dive must anticipate** (from the Universe Brain): config-as-memory
reads at thought-time (skills/prompts by tag+hash — families 1+3, hot) · the live Human
Profile (small, hot, personal-data class) · markers (annotation records — family 3+4) ·
the Librarian's whole-universe asks (families 2+3+4 + the new meaning axis, §4).

---

## 3. The shape — one node, one service, everything else embedded

**Per-tier node** (every tier, laptop or cloud, identical anatomy — tier profile turns
the dials):

| Component | Runs as | Role |
|---|---|---|
| **Postgres** | the node's one stateful service | system of record: `records`, `runs`, `meters` (append-only JSONB, partitioned by scope/time, indexed per §2) + **pgvector 0.8** (semantic) + **BM25-in-Postgres** (lexical, Tantivy-based `pg_search`-class extension) + recursive-CTE lineage |
| **Object store** | the node's bucket (MinIO dev / S3 prod) | content-addressed bodies (already shipped: `orreth-store`) + rollup **Parquet** (scope/time-partitioned, 128–512 MB files) |
| **DuckDB** | embedded library | deep-time/apex analytics over the Parquet rollups — the spacetime window's scrub engine; embeddable at every tier, all-time at the apex |
| **fastembed-rs / ort** | embedded library (Rust, ONNX, CPU) | local embeddings — bytes never leave the node (§5, §10) |
| **Iroh** | embedded library | tier-to-tier push-up sync (§7) |

**IaC footprint per federated node: one container + one bucket.** No second daemon, no
coordination cluster, no external control plane. This is the requirement "never design
what can't deploy or operate federated" taken literally — a second-brain laptop and an
enterprise tier run the same anatomy.

**Escape hatches, pre-named as dials (per §1 they are projection swaps, not rewrites):**
`pgvectorscale` (StreamingDiskANN, in-place extension) as a tier crosses ~10–50M vectors →
**LanceDB** (embedded Rust, immutable/append-only, S3-native) if the vector working set
outgrows Postgres comfort → Qdrant sidecar only if a proven deployment demands sub-20ms
filtered p99. Rejected: Weaviate (JVM footprint), Turbopuffer/managed-only (fails
federated-on-a-laptop), ClickHouse cluster (Keeper tax), Kuzu (archived 2025-10, dead).

---

## 4. Retrieval grows the meaning axis — the 0002 amendment

`Query` gains one facet; everything else in the 0002 contract stands:

```
Query.meaning? : { text: string, k: int }     # semantic intent — optional, additive
```

- **Hybrid is one SQL statement per tier**: BM25 rank-list × vector rank-list ×
  (optionally) lineage-proximity and recency rank-lists, fused with **weighted
  Reciprocal Rank Fusion** — trust/time/scope stay `WHERE` clauses. No second engine.
- **Trust-weighted rerank is ours alone**: final ordering weights relevance × Bayesian
  confidence (0005) × fidelity — `verified` > `distilled` > `distilled-raw-expired`;
  **`recalled` ranks dead** (surfaced only when the query asks for the dead, and then
  visibly labeled). The industry reranks by relevance; Orreth reranks by *standing*.
- **Same laws on the new path**: capability gating, per-tier budgets, serve-what-you-have
  + delegate the remainder, dedup by ContentHash, uniform refusal, budget-miss ≡
  authz-miss. A meaning query escalates by time-horizon exactly like a time query.
- **The faithfulness gate rides here**: a Librarian answer composed from retrieval
  carries the ContentHash citations of every claim — *no citation, no assertion*.

## 5. Ingestion discipline — Fetch → Ground → Distill → Curate, made mechanical

- **Chunk for meaning, not speed**: an ingested document lands as (a) one parent record
  (the artifact, body in the object store) + (b) meaning-grain child records
  (`derived_from` → parent), each a claim/section-sized KnowledgeEntry carrying source
  DID, generation depth, and state `untrusted @ 0.0000` (0014 unchanged).
- **Entity/relation extraction** enriches tags at ingest (the graph the lineage walks
  ride). Extraction is steward cognition under the model plane — metered, on the record.
- **Embeddings are computed where the bytes live** — at the ingesting tier, by the local
  model; a parent receives the pushed record's vector or recomputes locally. Bytes never
  travel for embedding. Matryoshka truncation (128–256 dims) for the index; full dims
  retained where a class warrants. **Embedding compute rides the steward's DID on the
  universal meter — honest zeros when local** (0019 posture).
- **Per-modality indexes** from day one in shape only (separate index per modality);
  image/OCR models arrive via the Stable per §12 of the vision doc — the door is open,
  nothing built early.

## 6. Partition & erasure — envelope keys, crypto-shred, evict-on-shred

- **Partition is enforced at the index, gated by capability**: each authorization class
  (e.g. `transaction-data`) lives in its own index partition; a query without the class
  grant never touches the partition — and the refusal is uniform. Per-class **envelope
  encryption** (KEK wraps per-class/per-scope DEKs; AES-256-GCM bodies) is a TierProfile
  dial per record class — regulated classes encrypted at rest, plain classes stay plain.
- **Crypto-shredding is the purge primitive** (locked purge semantics, 2026-07-10):
  destroy the DEK → the body is noise, irreversibly — and because **signatures compute
  over ciphertext, the signed stub still validates after key destruction.** Provably
  purged, never silently lost; EDPB-endorsed for GDPR Art. 17.
- **The hard rule: a shred fans out.** Embeddings are invertible enough to leak; a purge
  evicts the record's index entries and re-builds affected projections (§1 makes this a
  defined operation, not archaeology). The recall walk (0014 §4) supplies the blast
  radius, promotion boundary included.
- TEE-backed indexes (GPU confidential compute) noted as the opt-in upgrade for the
  single most sensitive class — reserved, not built.

## 7. Federation — children push up; the parent never reaches in

- **Iroh** (`iroh-blobs` + `iroh-docs`, pure Rust): every entry Ed25519-signed, values
  content-addressed, sync via range-based set reconciliation — for records already
  signed and content-addressed, resync reduces to "which hashes does the parent lack?"
  Verified resumable transfers serve big distillations to intermittent children;
  **peer-dials-key structurally enforces push-up-only.** The distillations-only policy
  (what rises) stays ours, applied above the transport. CDC/Debezium rejected (a parent
  reading a child's WAL is reach-in by definition). **NATS JetStream leaf nodes** stand
  as the named fallback if `iroh-docs` (pre-1.0) stalls — topology fits, hashing bolts on.
- **Bi-temporal semantics, adopted as canon** (the Zep/Graphiti lesson): `occurred_at`
  = valid-time, `received_at` = transaction-time — already our two clocks. **A
  contradiction closes the old fact's validity window with a new signed record; nothing
  deletes.** The Librarian reasons over current state; the window scrubs full history.

## 8. Mechanism — the build list this dive unlocks (after blessing)

Phase 1 (correctness debts, before any new capability — all from the inventory):
1. **Persist runs** (PG write-through + `(scope, agent, occurred_at)` index) — today
   they die with the daemon; presence stats and audit continuity break on restart.
2. **The five indexes** (§2: time, tags, author, kind-partial, derived_from-GIN).
3. **Retention enforcement**: daemon GC for `distilled-raw-dropped` bodies + orphaned
   body refs; meter rotation (30d hot, archive table).
4. **Presence caches**: incremental per-beat aggregates, invalidate-on-write.

Phase 2 (the meaning axis): pgvector live (`embedding_ref` populated at ingest via
fastembed-rs) · BM25 extension · hybrid RRF query + trust-weighted rerank behind
`Query.meaning` · conformance tests: uniform refusal + remainder honesty on the new path.
> **Phase 2 SIM-FIRST LANDED 2026-07-17 (Phase E of the build order — built last, as
> designed, so it consumes hard coordinates and aperture scores):**
> `orreth_sim/meaning.py` — fastembed local ONNX under the §10 bytes-local lock
> (`ORRETH_MEANING=off` darkens the axis; every consumer degrades to identity,
> honestly) · hybrid weighted-RRF (vector × BM25 × recency × coordinate kinship ×
> aperture proximity) · the trust-weighted rerank of §4, verbatim: standing over
> relevance, **`recalled` ranks dead** (surfaced only when asked, then labeled) ·
> three stated waits ENDED: the reactivation rerank (0031 §5) · cross-source
> contradiction at meaning-v1 (0032 §3 — same subject by cosine, values that
> disagree by the numbers; the paraphrase case stays honestly deferred) · **the
> Mirror hears meaning** (0034 sp3 — proven live on u:demo: three phrasings of the
> reading-glasses worry counted as one ask, 3×, in the portrait) · demo
> `scripts/demo.sh meaning` · 5 tests, 192/192. **THE RULE-9 GATE PASSED
> 2026-07-17 (JB, via AskUserQuestion): `Query.meaning` (optional `{text, k}`
> facet) + `embedding_ref` population are APPROVED into contracts/v0.**
> **THE WIRE LANDED the same day:** the contract facet (optional, additive —
> schema-tested both ways) · pgvector live (the image JB staged 2026-07-08,
> awake at last: `embeddings` table + HNSW cosine, an optional projection —
> a vector-less pg leaves the axis dark, never an error) · the becky-guarded
> `/embeddings` + `/embeddings/missing` doors (uniform refusal, absent ≡
> unauthorized) · the worker's projection sweep embeds where the bytes live
> and marks the bodyless NULL, never revisiting · **the meaning rerank runs
> in orrethd OVER EXACTLY THE HITS THE NODE AUTHORIZED AND SERVED** — the
> sacred core untouched: fused RRF (cosine × newest-first) × standing by
> fidelity, `recalled` ranks dead, after the cross-tier merge · **the purge
> reaches the projection** (0026 §1's hard rule: eviction rides the same
> breath as `/tombstone`) · a dark axis (door down, no vectors) leaves hit
> order untouched, honestly. **PROVEN ON THE WIRE**: "how do you build walls
> out of packed soil?" — zero shared words — surfaced the `rammed earth
> construction` self-dialog records from 1,207 hits at u:demo, and a forged
> token on the meaning path drew the one refusal sentence. 193/193.
> *Remaining, named: fastembed-rs in-process (the query embedder currently
> rides the node machine's worker door) · BM25 lexical rank at the wire ·
> vector-first candidate generation beyond the served set · the Hit.fidelity
> enum wart (the wire already speaks `untrusted`/`recalled`; the contract
> enum does not yet — a future JB cut).*

Phase 3 (federation): Iroh transport under the existing push-up flow; offline-child
resync test (kill a field for a day; watch it reconcile).

*orrethd/pg.rs is not core-sacred (rule 9 covers orreth-node, orreth-store, crypto,
contracts/v0) — but Phase 2's contract deltas (`Query.meaning`, `embedding_ref`
population) touch `contracts/v0` and land only with JB's explicit approval of this dive.*

## 9. Honest boundaries

- **pgvector bands are real**: ~1M vectors naive, ~10M with quantization+partitioning;
  pgvectorscale extends to ~100M on SSD. The escape hatches exist because the bands do.
- **Cold-S3 DuckDB is only fast with layout discipline** (file sizing, warm cache) — the
  apex scrub gets a latency budget and a cache, not a promise.
- **`iroh-docs` is pre-1.0.** The fallback is named. Transport choice is reversible
  because sync is below the contract line.
- **Embeddings leak; eviction is mandatory** — a purge that misses the vector index is
  not a purge. Tested, not assumed.
- **The light-cone stands**: a federated answer is eventually-consistent; every fused
  result carries its horizon (`remainder`, staleness) — never masquerading as complete.

## 10. Decisions

**Closed by the design owner** (mechanics; JB may veto any):
log-is-truth/index-is-projection (§1) · Shape A with named escape-hatch dials (§3) ·
hybrid + weighted-RRF in SQL, trust-weighted rerank, `recalled` ranks dead (§4) ·
meaning-grain chunking + entity extraction + embed-where-bytes-live + steward-DID
metering at honest zeros (§5) · per-class envelope encryption as a profile dial +
crypto-shred with mandatory projection eviction (§6) · Iroh with JetStream fallback +
bi-temporal close-the-window semantics (§7) · Phase 1 correctness debts first (§8) ·
EmbeddingGemma-300M default local model, Qwen3-0.6B as the quality dial, Matryoshka
128–256 index dims (§5).

**LOCKED by JB, 2026-07-10 (via AskUserQuestion; recorded in `../decisions/`):**

1. **The bytes-local posture: local-only by default.** Embeddings and reranking run
   in-process on each node; **record bytes never leave the node for indexing.** Hosted
   embedding/rerank APIs exist only as an explicit, per-universe, flagged opt-out that
   visibly changes that universe's published privacy posture. Discharges the
   embedding-source question pre-staged in the ledger 2026-07-08.

---

*One service per node, one truth per universe, every index a shadow the log can recast —
recent memory sharp and near, deep memory honest and high, and nothing the brain holds
beyond the reach of its own laws.* 🥂
