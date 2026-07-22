# 0038 — The Stacks (seven rows of the library)

*Design draft — proposed by Fable 5 (design owner), from JB's 2026-07-22 session
(reference: `tmp/RAG Design Patterns.png` — the seven flavors). The second
create-something-using-Orreth, arriving the day 0037 closed WHOLE. **No new
resident**: the Stacks are the librarian's retrieval musculature, made governable.
Companions: `0022` (the law this dive must not break), `0023` (the librarian and her
planner), `0007` (the cascade that factors the commonality), `0005` (the standings
that judge the flavors), `0033` (the science that grades them), `0031` (the assets
the flavors are made of), `0037` (allen, who provisions the ground). Four decisions
settled in the seed discussion (§7).*

---

## Why this is a keystone

RAG is not a feature beside the universe — it is **how data enters and how it
returns**, for humans and agents alike, exactly as the O·I·O·T ladder prescribes: an
ask arrives, the universe decides where truth lives and which musculature recalls
it. Build this well and every future field inherits a governed mouth and a governed
memory. Build it as seven separate truths and governance ends. The design goal in
one sentence: *seven retrieval flavors compete on the record over one truth, a
mechanical organ routes every ask to the right one, and the winners earn their
place in the librarian's own planner.*

## 1. The one-truth law (0022, applied — the line this dive must not cross)

**The signed log is the truth; every index is a rebuildable projection.** Therefore:

- The seven flavors are **seven projections + seven flows over ONE truth — never
  seven stores.** Ingestion happens once, through the gateway: quarantine,
  provenance, the signed MemoryRecord. Each field *derives* its index (vectors,
  graph tables, multimodal embeddings) from the log, on its own beat.
- **The purge's projection-eviction reaches all seven** (0026 survives intact); a
  crypto-shredded record stops speaking in every stack at once.
- **Authorization stays one contract** (0002): a field reranks only what the asking
  token may see — the trust-weighted rerank's law (`recalled` ranks dead) applies
  in every flavor.
- A projection is **rebuildable, therefore disposable**: a field can be torn down
  and regrown from the log without losing a byte — which is exactly what makes
  seven experiments affordable.

## 2. The ecosystem — commonality factored up, deltas left behind

`e:rag`, seven fields (dev: one hull is fine — projections are light). The shared
anatomy lives at the **ecosystem tier and cascades down** (0007): chunking policy,
embedding standards, and prompt templates are **eco-level assets on grace's shelf**
(versioned, improvable, human-gated on rewrites); the embedding and generative
minds **saddle at ada's stable**; the reranker, web tools, and any earned stores
**plant at charlotte's farm**. A field is its *delta*, as data:

| Field | The delta it alone carries |
|---|---|
| `f:naive` | nothing — chunks → vectors → prompt. **The baseline control** every rival must beat on the record |
| `f:rerank` | the reranker model pass — wide retrieve, narrow re-rank |
| `f:multimodal` | the multimodal embedder; media rides the prompt (0029's artifacts finally read) |
| `f:graph` | the LLM graph generator → **a graph projection in Postgres** (node/edge tables, recursive CTEs — Shape A holds) |
| `f:hybrid` | vector + graph fused at query time |
| `f:router` | per-ask strategy choice *within* retrieval (self-routing between its own tactics) |
| `f:swarm` | the multi-agent decomposition — sub-asks fanned to engines and tools, composed with citations |

## 3. The Dispatcher — an organ of the universe, carrying a standard

JB's instinct, made structural: put/get is universal fabric, so the *choosing* is an
**unembodied organ** — but split the way the body splits:

- **The reflex (the Dispatcher).** A small deterministic organ in the put/get path,
  **after the gateway's authorization — never around it** — reading the ask's shape
  (rung of the ladder · modality · scope · meaning-need) and routing by the
  **current routing standard**. No thinking in the hot path. **Every choice is a
  record**: which flavor, why, what it cost, what came back — so the spacetime
  window answers *"why did this question go to the graph field?"* as a query.
- **The judgment (the librarian).** The routing standard is a **versioned asset**
  she tends from receipts; the improvement engine proposes revisions from the
  standings; governance grades the diff; JB holds the high lane. Ambiguous asks
  escalate to her seat for one governed thought. *The organ enforces; the resident
  learns* — vigil's detection/enforcement split, applied to retrieval. Nothing
  routes and grades its own routing.

On the PUT side the same organ decides **which projections index a new record**
(all applicable, by class) — placement itself stays the universe's law (bodies to
the object store, indexes as projections; 0022 unchanged).

## 4. The proving ground — flavors compete on the record

**Proving-ground-then-promote** (settled): the seven run as rivals, not as
permanent organs. Route real asks (and replayed corpus asks) through competitors;
grade each pass with **0033's science** — recall fidelity, context efficiency,
information gain — plus latency and metered cost; roll up **0005 standings**
(Bayesian, floors flag never average away). The Naive baseline is the yardstick;
a flavor that cannot beat it retires honorably, on the record. Winners are
**promoted into the librarian's planner** as named strategies; the routing
standard learns which asks deserve them. Infrastructure is earned the same way:
the graph field runs on the Postgres projection first, and only evidence (losses
traced to missing algorithms, not missing truth) brings allen a deal-fit case for
a dedicated store — an amendment at JB's gate, never a default.

## 5. allen provisions the ground

The Stacks are **allen's first agent customer**: the eco's hull, any earned
stores, and the teardown/regrow cycle arrive as Intentions carrying lineage to
JB's Objective — through the charter, the planned DAG, and the gate, exactly as
0037 built. This is the provisioning-lifecycle proving ground JB named at 0037's
close, with real stakes and disposable bodies.

## 6. What the human sees

The librarian's room grows **the Stacks panel**: the standings table (flavor ·
asks served · fidelity · efficiency · cost · trend), the routing standard's
current version, and per-ask walks — ask → dispatcher's choice → flavor's flow →
answer with citations. The reel gains a tournament: one question asked seven ways,
the receipts side by side.

## 7. Decisions

**Settled in the seed discussion, 2026-07-22** (JB agreed in dialog):

1. **Proving-ground-then-promote** — winners join the planner; losers retire on
   the record.
2. **Naive RAG is the baseline control**, not redundancy.
3. **Graph rides a Postgres projection first** (Shape A holds); dedicated graph
   infra must be earned by standings evidence and arrives via allen at JB's gate.
4. **The Dispatcher is an unembodied organ carrying a standard the librarian
   tends** — reflex and judgment split; choices are records; never an authz
   bypass.

**Locked by JB 2026-07-22** (via AskUserQuestion, all on the recommended paths):

5. **The corpus: both** — dogfood the universe's own records for truth, an
   imported reference set for comparability.
6. **Promotion = a named strategy in the routing standard** (versioned asset,
   human-gated); any code landing in the core retrieval path is a separate,
   later rule-9 gate with evidence attached.
7. **The spoonful cut stands as proposed** (§8).

## 8. The spoonfuls (proposed)

| # | Spoonful | Nature |
|---|---|---|
| 1 | **The stacks stand** — e:rag provisioned through allen's door (the Objective on record); eco assets planted (chunking · embedding standard · prompt templates); `f:naive` end-to-end over the one truth: ingest once → project → retrieve → answer with citations | ✅ landed 2026-07-22, the day of the blessing — **the one-truth law by construction**: `stacks.py` — ingest lands ONE signed record through the gateway (no stack holds a copy); `project()` regrows chunks+vectors from the log at ask-time (rebuildable = disposable = honest); cosine with a **relevance floor** (a baseline that answers everything answers nothing honestly); answers **extractive with citations** and an honest unknown · tests prove the LAWS: rebuild-identical projection · a record gone from the log **stops speaking** (the purge's reach) · citations walk to real refs — **210/210** · e:rag :4511 + f:naive :4512 launched by JB's key through the shipyard gate · the librarian's seat knows where she stands (*"this is a row of the stacks"* — shelve/ask chips) · **proven on the wire and in JB's hands**: *"shelve rammed-earth: …"* → one record; *"ask the stacks how do packed soil walls handle heat?"* → the passage back wearing `[sha256:962ec20…]` · honest warts caught en route: the sim embedder's hex-as-ASCII bucket collapse (512→~32 effective dims, phantom similarity — fixed) and **the Brain's silent newborn** (rule 7 in spirit: depth-1 tissue now whispers its name — the busy found by their fire, the quiet by their name) · JB's north star recorded: **Closed Loop Bi-Directional RAG** — the same governed musculature purifying data in and answering out, feedback closing the loop on the O·I·O·A ladder |
| 2 | **The Dispatcher** — the organ in the put/get path; the routing standard v1 as an asset; every choice a record; the librarian's escalation seat | ✅ landed 2026-07-22, same day — `dispatcher.py`: STANDARD_V1 as a **versioned asset** (rules are DATA: media→multimodal · relational→graph · multi-source→swarm · precision→rerank · default naive); `classify()` deterministic, no thinking in the hot path; an **unbuilt row falls to the baseline LOUDLY with both truths in the signed choice record** — the universe never pretends a row it does not have; `choices()` = the RL substrate accumulating · **two JB walk findings fixed same-day**: the doors gated to /e:rag floors broke 0023 (one mind, many seats — now universal at every librarian seat, foreign asks RIDE TO HER RAG SEAT with the origin pinned in the choice record, "carried from my seat at u:demo") · and the prefix ceremony removed — **a plain question at any seat flows through the Dispatcher by default** (put/get is universal); questions about HER stay hers · honest note on record: the hop is worker-synchronous today, every hop lands as memory; the record-driven time-flow progression (0023 self-dialog shape) is sp3's refinement, which the swarm requires anyway — **214/214** · proven in JB's hands from the default librarian: his own question, the ⚡ line, the loud fallback, the citation — and the baseline's mediocre answer to an off-corpus ask recorded as **the standings' first exhibit** |
| 3 | **The rivals** — `f:rerank` · `f:graph` (pg projection) · `f:hybrid`; same asks, competing receipts | ✅ landed 2026-07-22, same day — `rivals.py`: rerank (wide cosine, precision re-scored by term overlap) · **graph** (terms as nodes, whole-chunk co-occurrence edges that each REMEMBER the chunk that made them — the citation is the edge's provenance; walking, not measuring) · hybrid (both scores fused — ranking what both ways can defend) · one `answer_as` door for every row; same laws proven: one truth, rebuild-identical, a forgotten record silent in EVERY row, citations always — **217/217** · `dispatch()` learns the standing rows (the standard's v2 rides the lanes in sp4) · **THE BEFORE/AFTER ON THE RECORD**: the same relational ask that fell to the baseline in the morning routed to «graph» by evening — *"⚡ chose «graph» — walk edges, not distances · (rammed↔earth)"*, no fallback, both choices in the ledger — the universe visibly smarter about its own retrieval · proven in JB's hands; his note kept: the rivals run as FLOWS at the naive hull per his own dev allowance — **sp4 embodies them** (JB, 2026-07-22: hulls through the shipyard gate, each row its own heartbeat and meter) |
| 4 | **The tournament** — 0033 grading + 0005 standings + the Stacks panel; `f:multimodal` · `f:router` · `f:swarm` join; first promotion proposal from receipts | the winners earn their place |

---

*A library is not seven collections. It is one collection, seven ways of walking
the rows — and a librarian who knows, because she keeps the receipts, which row
answers which question.* 🥂
