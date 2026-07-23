# 0039 — The Chronicle and the Canon (Phase 2's constitution)

*Design draft — proposed by Fable 5 (design owner), from JB's 2026-07-23 vision
session: "Phase 2 could be the most important element of Orreth." This doc names
the two kinds of data the universe lives by, the loop that couples them, and the
laws that let memory be the interface for everything while physics allocates
honestly beneath it. Companions: `0030` (the ladder this formalizes), `0031`/`0028`
(the shelf and the improver — the Canon's existing half), `0003`/`0005` (the
metabolism and the scores that drive distillation), `0004` (retention classes,
here extended), `0001` (skills as crystallized memory — the mentor's craft),
`0022` (bodies external, meaning internal — the pointer law's parent), `0033`
(the science that tunes the dials), `0037` (allen — the charter becomes the
storage map), `0038` (the rows that serve both books).*

---

## Why this is the keystone's keystone

Every organ built so far writes records and reads records. This dive answers the
question underneath all of them: **what kinds of records are there, how long does
each live, where does each physically rest, and how does one kind teach the
other?** Get this right and the universe becomes what JB named it: an adaptive,
self-improving, living harness where permanent lifecycles — resident, human,
service, every DID — genuinely learn. Get it wrong and we have either an
amnesiac (Chronicle lost) or an institution that no longer knows how to be
itself (Canon lost). The design goal in one sentence: *one mind, two books —
the Chronicle records what happened, the Canon records how we do things, the
Chronicle's evidence evolves the Canon through human gates, and the Canon
governs how the next Chronicle is written.*

## 1. The two books

**The Chronicle (JB: Purpose Data).** The O·I·O·T ladder — Objectives ·
Intentions · Observations · thought:actions — DAG-hard, both clocks stamped,
lineage complete, propagating up the tiers by the three flows. The Chronicle is
*what happened and why*, forever walkable: any answer's citation walks to a
record; any record walks its ladder to a human's sentence.

**The Canon (JB: Orreth Data).** Policies · prompts · skills · standards ·
charters · routing standards · distillation dials — everything the universe
relies on to *meet* objectives. Already half-built as the shelf (0031): every
Canon entry is a **versioned asset** — siblings never silent successors,
adoption through the lanes, rewrites human-gated, rollback structural.

**The coupled loop (the thesis).** The Chronicle's distilled evidence — scores,
standings, markers, friction — drives **proposals** against the Canon; the
lanes grade them; humans sign the consequential ones; the adopted Canon governs
how the next Chronicle is written. Run once already without its name: the
tournament (Chronicle) argued routing-standard v2 (Canon); JB signed; the Canon
now routes every ask. Phase 2 makes this loop the architecture.

## 2. One substrate, two retention regimes

Both books are MemoryRecords in one mind — governance opens ONE thing to the
universe. But they age differently:

- **The Canon retains forever and is never distilled — only versioned.** It is
  small, precious, and is the universe's genome. Every version kept; history is
  the rollback. "Forever" is cheap here and anything less is dishonest.
- **The Chronicle retains by RECORD CLASS** — and the class carries the same
  attributes allen's deployment charter interrogates: **RTO · RPO · Criticality
  · DataClassification · retention (min AND max, 0004)**. This is the bridge
  JB named: *in prod, the charter is the storage map* — allen's IAC allocates
  physical stores per class, so a `compliance-critical` class rests on
  infrastructure that actually delivers its RPO, and "infra failure = memory
  loss = compliance failure" is answered structurally, not by hope. Records
  retention stops being paperwork; it becomes provisioned physics.

## 3. Locality and the metabolism — how the Chronicle ages

- **The how-it-was-done stays close to the operating floor** (JB's law): fields
  keep the workforce's detailed records per their class retention; the detail
  does not travel. What RISES under 0003's metabolism is the distilled result —
  and among competing observations of the same thing, **the highest-scoring
  survives** (0005's scores as the metabolism's taste).
- **Recall-frequency joins the distillation inputs** (new, from JB's seed):
  data no observation calls on distills sooner; data under active recall stays
  warm and low. Usage is evidence about value; the metabolism should hear it.
- **The distillation dials are Canon assets** — per-class: what rises, score
  thresholds, recall-frequency windows, cadence. Human and Agent+HITL editable
  from day one (JB's explicit requirement — nobody fully understands optimal
  cross-floor/cross-time distillation yet, so the dials must be data, not
  code), and **0033's harness measures the information loss each setting
  causes**: distillation tuning becomes the same evidence→proposal→gate loop
  as everything else. The universe learns HOW to remember the way it learned
  how to retrieve.

## 4. The mentor and the mentee — permanent lifecycles that learn

The must-work use case, mechanized from existing locks:

1. An Objective executes under an **expensive, smart mind** (the mentor); the
   Chronicle records the full walk, the feedback, the effectiveness score.
2. A human or agent **crystallizes the craft**: a skill set / toolbox for that
   objective-shape — 0001's skills-as-crystallized-memory, with its acceptance
   rubric, onto the Canon's shelf through the gate.
3. The next cycle assigns to an **inexpensive mind (the mentee)** — but 0010's
   lock holds: *a skill never silently runs dumber than the tier its rubric was
   proven at*. So the toolbox **canaries at the mentee's tier**; the standings
   confirm the rubric clears; only then does the cheap tier serve steady-state.
4. Drift or failure at the mentee tier is Chronicle evidence that re-opens the
   Canon entry — escalate back to the mentor, revise the craft, re-canary.

Graduation by evidence, demotion by evidence, forever — for every DID class.

## 5. Memory, not network calls — the sharing law

A field needing another field's or ecosystem's results **reads risen records at
their common ancestor** — through the librarian's seats and the stacks — never
by lateral RPC. Three reasons this is law and not preference: the result
arrives **with provenance, trust state, and score attached** (a network call
strips all three); authorization stays the one retrieval contract; and the
same feed drives **observability for free** — the future Telemetry views (not
yet designed) are readers of the Chronicle: monitors are standing queries,
anomaly triggers are markers and the serials desk's difference-is-news aimed at
operational records. Monitoring is retrieval wearing a uniform.

## 6. The pointer law — bulk never enters the mind

Massive datasets (the ML ecosystem's training corpora, media libraries, model
weights) are **never stored in memory**. Memory holds the **artifact-pointer
class**: a signed record carrying the pointer, content hash, metadata, lineage,
and class attributes — the bulk rests in its class-allocated store (allen
provisions it; the charter maps it). 0022's bodies-external pattern,
generalized: *meaning lives in the mind; mass lives in the warehouse; the
pointer is signed so the warehouse can never quietly swap the goods.*

## 7. What the rows may serve — the privacy floor

As the stacks widen to the Chronicle (0038's Phase 2 of "the rows meet the real
memory"), **exclusion is by class, at projection time**: profile and consent
classes, testament machinery, purge stubs, and key/custody material never enter
a projection at all — floors apply before trust-weighting ever sees them. The
retrievable Chronicle is the governed subset, and the excluded classes are
listed in the Canon where humans can read — and gate — the list itself.

## 8. Decisions — **all eight locked 2026-07-23**

*Settled in JB's seed dialog (his own laws, formalized):*

2. **The bridge**: record classes carry charter attributes; in prod allen's IAC
   allocates stores per class — the charter IS the storage map.
5. **Memory-not-RPC as law** (§5), monitoring as a Chronicle reader.
6. **The pointer law** (§6) with the artifact-pointer class.
8. **Distillation dials as Canon assets** tuned on 0033 evidence (§3).

*Locked via AskUserQuestion, all on the recommended paths:*

1. **Chronicle & Canon are the house names** (Purpose Data / Orreth Data kept
   beside them in this doc as JB's originals).
3. **Recall-frequency joins distillation inputs** — usage is evidence; the
   window is a per-class Canon dial.
4. **Graduation requires the canary**: the crystallized toolbox proves its
   rubric AT the mentee's tier under full observation before steady-state —
   never silently dumber.
7. **The privacy floor excludes**: profile & consent · testament & passage ·
   purge stubs & key custody. Dispatch and meter internals remain retrievable —
   "why did this route there?" stays a stacks question.

## 9. The spoonfuls (proposed — JB may re-cut)

| # | Spoonful | Nature |
|---|---|---|
| 1 | **The two books stand** — record classes gain charter attributes; the Canon census (every existing shelf asset formally a Canon entry); the projection privacy floor enforced by class | ✅ landed 2026-07-23 — `canon.py`: the registry itself a Canon asset (every class wearing RTO·RPO·criticality·classification·retention — the bridge to allen's IAC is data from day one) · classification reads tags FLOORS-FIRST · the floor guards `project()` before anything chunks, **genesis-fallback so sovereignty never depends on setup order** · proven by the smuggle test: a record dressed as a document but wearing `profile` never chunked · *"show the canon"* rolled the live genome: 8 entries including the routing standard at both its versions — **226/226**, proven in JB's glass |
| 2 | **The Chronicle joins the rows** — ladder records retrievable through the stacks (class-gated, trust intact); TIME as a Dispatcher shape ("as of…", "what changed since") — the spacetime window and the stacks join hands | ✅ landed 2026-07-23 — the ladder speaks in its own words (the flattener keeps meaning-fields; names matter); every chronicle chunk stamped with its moment; **the time dial** ("as of / since / before / after" — timeless chunks stand aside) + the temporal shape on the record · four warts earned live: an ask never cites its own routing · machinery-talk never chunks into world-answers (dispatch stays retrievable via the routing door) · the stratified cap (conversations board before the run-record flood) · rule 8 refused my backdated tests and archives were the honest path — **227/227** · **proven in JB's glass: "what has the human asked allen to do?" answered with his own words from the estate session — "I approve the adoption · allen · the acceptance gate stands…" — cited to the audience record.** The universe remembers itself |
| 3 | **The metabolism gets its dials** — distillation policies as Canon assets (per-class dials); recall-frequency wired in; 0033 loss measurement on every distillation | learning how to remember |
| 4 | **The mentor graduates the mentee** — the crystallize→canary→confirm walk run live: an objective mastered at the expensive tier, its toolbox proven at the cheap tier, the graduation on the record | the lifecycle learns |

---

*One mind, two books. The Chronicle so the universe can answer for what it did;
the Canon so it knows how to be itself; the loop between them so tomorrow's
universe is better than today's — and a human's hand on every consequential
page.* 🥂
