# 0031 — The Aperture and the Workshop (context projection · the governed shelf · the visible mind)

*Design draft — proposed by Fable 5 (design owner), from JB's context/data/memory
session (2026-07-13), adapting an outside architecture review (ChatGPT 5.6, two
documents under `tmp/`, never tracked in git; no Orreth code or design was shared —
only the Librarian's name traveled). This document first AUDITS that review against
canon 0000–0030, then designs the three organs JB asked for: context that descends
with receipts, self-improvement the human can hold in their hands, and a mind the
human can finally see. Nothing here builds until JB reads and locks.*

---

## Why this dive

0030 gave the human their seat: the ladder (Objective · Intention · Observation ·
Thought), the plan gate, the ledger, the place-spine. What the seat still cannot
show is **the mind at work**. Today:

- A workforce agent's context is admirably minimal (0027's intention contract) —
  but the *proof* of that minimalism exists nowhere. Restraint without receipts.
- The universe improves its own assets (0028's improver) — but the human cannot
  see the shelf, walk a version's lineage, read an approval package, or leave
  feedback. The chassis's own prompts are still **code constants**, outside the
  proposal chain entirely — behavior that cannot be governed because it is not data.
- The thought.graph is concrete on the record (0027: templates with a checked
  narrative↔graph bijection; signed RunRecords every cycle) — and **zero surface
  renders it**. The human who owns the Objective cannot see how any seat thought.

JB (2026-07-13): *"As of today, human has NO ability to see how a Resident or
workforce agent thinks."* That is the wart this dive retires.

## 1. The outside review, audited

The strongest signal first: working from nothing but the Librarian's name, the
outside review **independently re-derived Orreth's architecture** — a five-layer
tiering, intentions delegated down, results distilled up, runtime-enforced (not
prompt-described) authority, provenance-preserving distillation, artifacts as
governed versions. Convergent evolution is evidence the skeleton is right.

| Verdict | The review proposed | Orreth's answer |
|---|---|---|
| **Already canon — stronger** | Memory states (active→working→consolidated→distilled→archetypal) | 0003 keep-classes + apex fidelity; "archetypal memory" is just a Skill (0001) — no fifth tier needed |
| **Already canon — stronger** | Decay affects retrieval, not truth | 0022 trust-weighted RRF; `recalled` ranks dead, visibly |
| **Already canon — stronger** | Distillation must preserve provenance | 0003 Distillation.`derived_from` — signed, cryptographic, QA-sampled |
| **Already canon — stronger** | HITL approval, staged promotion, canary | 0012 quorum + cooling-off + silence-never-approves; 0011 probation; 0001 canary |
| **Already canon — stronger** | Prompt-factory self-amplification controls | 0028: proposer never grades; change kind computed **by diff**, never declared |
| **Already canon — stronger** | Contamination controls on shared knowledge | 0014 quarantine-at-0.0000, promotion on receipts, the recall walk (live on the wire) |
| **Adopted** | Context projection: a signed, bounded, per-decision context envelope | **§2 — the aperture** |
| **Adopted** | Approval package: what the human sees before signing | **§4 — the Workshop's doc panel** |
| **Adopted** | Factory outputs as governed artifacts, prompts included | **§4 — the shelf made whole** (prompts leave the code) |
| **Adopted** | Knowledge freshness / revalidation triggers | **§5** |
| **Adopted** | Observation reactivates memory without changing its origin | **§5** — a rerank signal riding 0022's bi-temporal canon |
| **Adopted** | Self-improvement boundaries written as one rule | **§6 rule 5** |
| **Rejected** | Semantic versioning as artifact identity | Lineage IS identity (0011's sibling law; 0028 applied it to assets). A human-facing label may ride the body; `derived_from` remains the truth |
| **Rejected** | "HIVE Mind" — a global knowledge plane | Scope-governed knowledge is already canon (0001 promotion-to-ancestors, 0023 exchange); Orreth deliberately has no undifferentiated pool |
| **Rejected** | ~18 new resident agents | Zero new residents. Every proposed seat maps to an existing organ — **§3** |
| **Rejected** | Librarian owns prompt assembly | The plane never sees the prompt (covenant 5); assembly is the dispatching seat's. The librarian remains the read door — all knowledge, zero levers (0023) |
| **Rejected** | Fixed per-layer token tables | Budgets are already tier-profile dials + intention slices (0004, 0027); the aperture *records* the slice, it does not re-invent it |

## 2. The aperture — context descends with receipts

0027's intention contract is already more minimal than the review's "minimal
envelope": one intent, a budget slice, citation refs — never the plan, never the
siblings, never the why. What is missing is not restraint but **receipts of
restraint**. Today the chassis pins each RunRecord to `context_hash` — the
ResolvedContext, the *law* it ran under (0007). But the full envelope — persona,
prompt-template versions, pinned skills, class ladder, the intent itself, the refs
— is implicit in code. Nobody can open a thought and see what the mind could see.

**The aperture** is that envelope made first-class: assembled at dispatch, signed
by the dispatching seat, content-addressed, written as a record.

```yaml
aperture:                      # kind: semantic, tags: ["aperture"]
  of: ContentHash              # the intention it serves (→ objective, up the ladder)
  seat: DID                    # who assembled and signed it
  agent: DID                   # who it was cut for
  law: ContentHash             # the ResolvedContext (0007) — cascaded floors & standards
  task: {intent, budget: {tokens}, completion}
  behavior:                    # versions, not bodies — the shelf's pins (§4)
    profile: ContentHash       # chassis profile asset version
    prompts: [ContentHash]     # plan/critic template versions
    skills: {name: version}    # additive registry pins (0007)
    klass: str                 # + ladder, if granted
  knowledge: [ContentHash]     # citation refs — hashes, never bodies (0021 §21 kept)
  output: {shape?, escalation, ask_human?}
```

- **Everything by reference.** The aperture names hashes; the runtime resolves
  them. It is small, cacheable, diffable, canary-able — 0007's words for the law,
  extended to the whole opening.
- **RunRecords pin it.** `context_hash` widens its meaning: it points at the
  aperture, which cites the law within it. "What rules governed this thought"
  becomes "everything this thought could see." *(This widens 0005/0007 semantics —
  flagged as JB's approval moment, rule-9-adjacent.)*
- **Reproducibility.** Same aperture ⇒ the same run is re-cuttable. A misbehaving
  seat's exact worldview can be reconstructed and re-run under a candidate asset —
  the improvement engine's future test bench.
- **The downward mirror.** 0030's index climbs UP (thought → observation →
  intention → objective). The aperture is the same lineage looking DOWN: what the
  objective's authority projected into each seat. **JB holds the data scheme for
  the ladder's index — the aperture is designed to socket into it, never to preempt
  it: it only cites hashes and rides existing record kinds. Before this lands, it
  is checked against the scheme's reveal.**

## 3. The seats, mapped — zero new residents

The review proposed a nervous system of ~18 named residents. Orreth's law is few
seats, separated duties. Every proposed function already has an organ:

| The review's seat | Orreth's organ |
|---|---|
| Librarian (intake, plan presentation) | the librarian (0023) + the plan gate (0030 §3) |
| Governor / Change Governor | the governance seat + R6 lanes (0024) + gates (0012) |
| Sentinel | vigil (0013) — detection, never enforcement |
| Planner / Dispatcher | the orchestration incarnation (0027) |
| Critic / Judge | the chassis critic (0015) + the dispatching seat's markers (0024; nothing grades its own yardstick, 0005) |
| Archivist | the substrate itself — the signed log IS the archivist (0022) |
| Memory Curator / Knowledge Steward | the steward (0003) |
| Research Orchestrator | the fingertip fan under an approved plan (0027 · 0030) |
| Evidence Curator | charlotte (sources, discredit — 0018) + the librarian (admission, citations mandatory — 0023) |
| Artifact Architect / Factory Controller | the improver (0028) + the factories (0011) |
| Outcome Observer | rollups (0005) + the improver's evidence() |
| Executor | the governed gateways (0010 · 0016) |
| Reconciler | the review seat (0027 §6) |
| Teardown | the Purge (0026) + the pasture (0019) |

One seat gains a face: **the improver becomes embodied** — because JB asked to
*see* it (§4). The others stay as they are; an organ earns a room when a human
needs to stand in it.

## 4. The Workshop — the shelf made whole, the improver embodied

### The shelf

**All behavior is versioned assets on one shelf.** Workflow templates already are
(0027 `save_template`); chassis profiles already are (0028 `make_asset`); skills
are already version-pinned (0007). The stragglers come home: the chassis's `_PLAN`
and `_CRITIC` templates and every persona leave the code and become assets — the
chassis reads active versions at prepare. From that moment the improver *can*
propose a better prompt, the diff *will* classify it a rewrite, and the human's
lane *will* hold it — 0028's machinery finally covers what it was built for.
A prompt that lives in code is behavior that cannot be governed.

### The room

The improver gains a calling card and a name — **grace the smith** (JB's
christening, 2026-07-13; for Grace Hopper, who turned receipts into better
machinery her whole life). The fifth room in the glass, alongside the
librarian's, becky's, charlotte's, and ada's. Existing panel kinds suffice,
blind-rendered as ever (0028 §8):

- **stat** — assets under care · open proposals · **waiting for you** · adoptions this season
- **bars** — the evidence: success rate by asset, from the rollups
- **list** — the shelf: every asset, its active version, lineage depth, lane badge (amber when a proposal waits — 0024's badge, kept)
- **doc** — the **approval package** of the selected proposal:

```text
WHAT CHANGED   the computed diff (classify_change — never the proposer's claim)
WHY            the evidence refs, resolved to readable receipts (runs, markers, parked intents, human feedback)
BLAST RADIUS   which seats run this asset (its Selector / targets)
CHECKS         refused-at-save results — validation runs BEFORE the gate, the human reviews a candidate, never raw output
ROLLBACK       the sibling law IS the plan: the prior version never died; re-adopting it is one record
```

### The doors (parlor verbs, 0020's pattern — new flows, zero core changes)

- **`show asset <name>`** — the version walk: oldest → active, each version's diff
  summary, its evidence, its grade marker, its adoption record. The whole chain —
  evidence → proposal → grade → adoption — readable by the being it answers to.
- **`feedback on <asset>: <words>`** — the human's words land verbatim
  (0024's quoting discipline), resident-signed, derived from the active version,
  tagged so the improver's evidence() **must** carry them next beat. Human
  judgment becomes improvement fuel, on the record. v0: feedback is evidence,
  never an auto-trigger — the improver still decides on its own beat *(OPEN)*.
- **Approve / adjust / reject** — high-lane proposals already belong in the
  decision inbox (0030 §4: "waiting for you"); the Workshop is where you study
  before you sign. **A human's adjustment is a proposal with the human's DID as
  author** — same diff, same grade, same adoption record. One door for all
  change, whoever walks through it; the shelf never learns a silent edit.

## 5. The metabolism, tuned — three small adoptions

- **Trust wears a review date.** Knowledge categories gain revalidation triggers:
  a contradiction closing a validity window (0022 bi-temporal), a source's
  manifest change or expiry (charlotte, 0018), the failing-runs lens (0014 §4),
  a human challenge (parlor). A fired trigger mints a **new version at
  `investigating`** — annotate-never-rewrite, the trust ladder run in reverse.
  `review_interval` becomes a tier-profile dial. Nothing stays `trusted`
  unattended forever.
- **Observation reactivates without rewriting age.** Canon already splits
  `occurred_at` from `received_at` (0004/0022). Retrieval's rerank gains a
  reactivation signal — recently-retrieved, recently-cited memory rises — riding
  the presence caches (0022 family 7), never mutating records. Old memory newly
  relevant surfaces; its origin never moves.
- **The domain package is a view.** "Acquire knowledge of Y" is an Objective
  (0030); its completed report in the ledger — category versions, artifacts
  minted, sources admitted, provenance whole — **is** the review's "Knowledge
  Domain Package." Recallable forever, rendered from records that already exist.
  No new store (0030 SP2's law, kept).

## 6. The visible mind — the walk of the work

Everything below renders from records that already exist. This is a view, not a
store.

- **The choreography renders.** A workflow template carries nodes, edges, and a
  narrative whose bijection with the graph is **checked at save** (0027
  `check_workflow`). The glass gains a fifth panel kind — **`graph`** — nodes,
  edges, and the narrative's sentences side by side, guaranteed to agree because
  the save gate refused anything else. Live objectives light their template's
  seats as intentions land.
- **The work walk.** In the Objective ledger (0030 SP2), every intention opens:
  **the aperture** (everything this seat knew — and everything it could not see)
  → **the cycles** (each signed RunRecord: class, observations, cost, verdict)
  → **the grade** (the critic marker, its rubric, its author — never the agent
  itself) → **the outcome** → the assembled report. The ladder walked downward,
  thought by thought.
- **Scratch still evaporates (R7).** The human sees the record of thought — what
  it knew, what it cost, what it concluded, who judged it — not the working
  paper. If JB wants per-observation depth on the record, that is a cost dial
  and his to set *(OPEN)*; the law that scratch dies is not touched here.

Canon additions this dive writes:

1. **Context descends only as an aperture** — signed, content-addressed; a seat
   knows exactly what its aperture names, and the record proves it.
2. **Restraint leaves receipts** — every thought pins the aperture it ran under.
3. **One shelf, one door** — all behavior (prompts, procedures, skills, profiles)
   is versioned assets; every change, human-authored included, walks
   proposal → grade → adoption.
4. **The mind is visible from the record** — what it knew, what it did, who
   judged it; scratch still evaporates.
5. **The universe improves only its behavior** — assets, routing, retrieval,
   coverage; never root governance, the DID trust model, human approval
   requirements, tenancy boundaries, or audit duty. Those change only by
   privileged human hands (covenant + 0022 locks, written once as canon).
6. **Trust wears a review date** — freshness triggers demote to `investigating`;
   promotion is earned again, never assumed.

## 7. The spoonfuls

| # | Spoonful | Nature |
|---|---|---|
| 1 | **The shelf + the Workshop** — prompts/personas become assets; the improver embodied (fifth room); the shelf list + version walk; the approval package; the feedback door; high-lane proposals join the decision inbox | ✅ landed 2026-07-13 — proven as a human in the glass: grace's ember orb and roster row (pin-only residency) · the four-panel room (amber lane badges, the package readable) · feedback typed at the pane landed verbatim and rode into the next proposal's receipts · **adopt** at the gate made prompt-plan v2 the active version (the walk shows the whole chain) · **decline** at the gate wrote a decline record and released the lane. 126/126 tests. Walk findings: orrethd's presence roster was a fixed list (a pinned organ was not yet a resident row — grace added; a data-driven roster is a future cleanup) · the demo floor carried 15 stale improvement requests + 3 distinct open proposals from the pre-decline era — the missing decline record was exactly why; debt swept with honest reasons on the record |
| 2 | **The aperture** — assembled + signed at dispatch; the chassis pins it; the ledger shows it | flags a 0005/0007 semantics widen **and** the socket check against JB's held data scheme — both are JB's approval moments |
| 3 | **The visible mind** — the `graph` panel kind; the work walk in the ledger; template narrative rendered beside its graph | ✅ landed 2026-07-13 — proven as a human in the glass: the choreography is COMPOSED by the orchestration seat (`fingertip.choreography` — nodes · edges · narrative, the 0008 §3 bijection, test-checked) and rendered BLIND (0020's law); a staged plan shows "what you are approving" before a word fans; the done report shows the same picture lit (every seat's status, mid-flow legs included — rule 7), the narrative rewritten by what ran; clicking a seat opens the walk — what rode down (intent + budget, and nothing else), the cycles (R7 stands), the grade (marker reason fetched from the record body, author ≠ agent), the outcome — every line ending in a record hash. 128/128. Walk finding: the ledger pane ignores wheel-scroll where the Requests pane doesn't — a small wart for the next glass pass |
| 4 | **The metabolism** — freshness triggers + review_interval dial; reactivation rerank signal; the domain-package view on acquisition reports | ✅ landed 2026-07-13 (the event triggers + the package view) — proven as a human in the glass: **the revalidation walk** (`revalidate_source` / `revalidate_walk` — the recall's softer sibling: current heads drop to `investigating`, trigger named, medium lane, doubt never stacks, dead stays dead, promotion earned back through `corroborate`); **the rug-pull door now doubts** (a changed manifest fires `source-changed` — charlotte signals, the librarian walks); **the human's challenge** (`challenge <topic>` at the librarian's card → matching current claims to investigating, the marker quoting the doubt); **the domain packages** — a VIEW over records that already exist, per intent: every claim's state counted, every source named, doubt wearing amber in her room. 132/132. **Deferred honestly:** the reactivation rerank rides 0022 Phase 2 (the meaning-axis ranker it feeds does not exist yet); the `review_interval` clock dial needs a tier-profile field (contracts/v0 — rule 9, JB's approval moment) or config-as-memory; the failing-runs lens waits on outcome correlation (0014's third lens) |

## 8. Decisions

**Canon per JB (2026-07-13, his session):** the universe's self-improvement must
be human-governable in the glass — review, approve, adjust versions, leave
feedback · the human must be able to see how a resident or workforce agent thinks
· design before build · the outside review is raw material, adapted at the design
owner's discretion · **blessed same day** ("go with your recommendations as long
as benefit outcomes are maintained — let's begin") · **grace the smith** is the
improver embodied (the christening, locked via the gate) · **continuous
acquisition is core and needed** — it follows the design owner's lead as its own
dive, after the freshness triggers and the Workshop stand.

**Closed by the design owner (JB may veto):** zero new residents — the map in §3
· the improver owns the Workshop · semver rejected as identity (lineage is
identity; a display label may ride the body) · "HIVE Mind" dropped as term and
shape · human edits ride the same proposal chain as the improver's · the aperture
cites hashes, never bodies · prompts leave the code and join the shelf ·
Workshop feedback is evidence, not an auto-trigger (v0).

**OPEN (JB's locks, remaining):**
- **The aperture vs the held data scheme** — the socket check before spoonful 2;
  and the `context_hash` semantics widen touches 0005/0007 (rule-9-adjacent).
- **Per-observation record depth** — how much of the nucleus's work becomes
  record (cost/exhaust dial); R7 default stands until changed.
- **Feedback → proposal coupling** — v0 ships evidence-only per the blessed
  recommendation; JB may re-lock to same-beat coupling after living with it.

**Resolved 2026-07-13:** the improver's name (grace the smith) · continuous
acquisition confirmed core-and-needed, queued as its own dive.

---

*The seat let the human stand anywhere in time. The Workshop puts the levers in
their hands; the aperture proves what every mind was given; the walk shows what
every mind did with it. Nothing thinks in the dark anymore.* 🥂
