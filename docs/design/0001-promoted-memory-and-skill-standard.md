# 0001 — Promoted Memory & Skill Standard (+ acceptance rubric)

*Design draft for review. Schemas are language-neutral shapes, not code. **Open decisions** are flagged
for JB — the vision-owner's call. Rationale: `../vision/FUTURE-the-orreth.md`.*

---

## Why this is the keystone

Two things we promised collapse into one primitive:

> **A Skill Standard is a procedural memory that got promoted up the stack and handed an acceptance rubric.**

So we do **not** build a "memory system" and a separate "skills system." We build **one governed
memory fabric**, and a *skill* is a privileged, rubric-bearing kind of promoted memory. Get this schema
right and we've laid the foundation for **both** the reproducibility proof (teacher → skill → fleet)
**and** the "no loss ever" memory fabric.

The chain this doc has to close:

```
teacher run ──capture──▶ Memory(procedural) ──promote──▶ Skill Standard(+rubric)
                                                              │
                                                      cascade DOWN (targeted)
                                                              ▼
                                              cheap fleet pulls + verifies + applies
                                                              │
                                                       run + score by the SAME rubric
                                                              ▼
                                         Run Record{score, confidence, cost…} ──roll UP──▶ verify vs baseline
```

---

## 1. The base unit — `MemoryRecord`

Append-only, content-addressed, DID-signed. The atom of the fabric. *Everything* (episodic, semantic,
procedural, and skills) is a `MemoryRecord` or a specialization of one.

```
MemoryRecord {
  id            : ContentHash          # sha256 of canonical(body) — content-addressed ⇒ dedup + tamper-evidence
  kind          : "episodic" | "semantic" | "procedural"
  scope         : ScopePath            # who owns it: e.g. universe/eco:cloud/field:prod-aws  (tenant isolation)
  author        : DID                  # the agent/harness that wrote it
  signature     : Sig                  # author's DID signature over canonical(body)  ⇒ no memory without provenance
  created_at    : EcosystemClock       # UTC, the universal index
  supersedes    : ContentHash?         # append-only versioning — never mutate, never delete
  body          : CompressedBlob       # headroom CCR: compressed for transit/cost, ORIGINAL retrievable
  body_ref      : URI                  # signed pointer to full detail at the owning tier (roll-up holds this, not the blob)
  embedding_ref : VectorRef?           # for semantic retrieval (Qdrant/pgvector)
  provenance    : { run_id?, model?, source_record?, ... }
  retention     : RetentionState       # see §5 (active | tombstoned{...})
  tags          : Tag[]                # role/capability tags — fuel for targeting selectors (§4)
}
```

**Why these choices**
- **`id = ContentHash`** gives dedup (headroom already dedups; we make it cryptographic) and integrity for free.
- **`supersedes` not `delete`** is what makes *"never lose a memory"* literally true: history is a chain, not a mutable cell.
- **`body` compressed + `body_ref` pointer** is the lightweight-at-the-top rule: a higher tier stores the
  pointer and (for promoted items) the compressed body; raw detail stays where it was written and is fetched on demand.
- **`signature` + `scope`** are the security spine: every byte attributable to a DID, every record tenant-scoped.

---

## 2. Promotion — moving a memory up a tier

Promotion is a **governed action**, never an automatic copy. It re-scopes a memory upward (Field →
Ecosystem → Universe), producing a signed promotion record so the lineage is auditable.

```
Promotion {
  memory        : ContentHash          # what got promoted
  from_scope    : ScopePath
  to_scope      : ScopePath            # strictly an ancestor of from_scope
  lane          : "auto" | "human"     # auto only if low-risk + high-confidence; else human-gated
  approved_by   : DID                  # becky / a human / a resident governance agent
  evidence      : { confidence, supporting_records[], ... }
  signature     : Sig
  created_at    : EcosystemClock
}
```

**Isolation rule (non-negotiable):** a promotion can only move a memory to an **ancestor** scope, and
crossing into a *sibling* tenant's governance requires an explicit human-gated `scope=global` step
(proven across ≥2 tenants). *One tenant's memories never shape another's unless a human promotes them.*

---

## 3. The `SkillStandard` — a promoted procedural memory with a rubric

A Skill Standard **is** a `MemoryRecord{kind:"procedural"}` that has been promoted **and** carries the
three things that make it executable-by-others and verifiable: a **scaffold**, an **acceptance rubric**,
and **targeting + lifecycle**.

```
SkillStandard extends MemoryRecord(kind="procedural") {
  version       : SemVer               # versioned; supersedes prior versions via MemoryRecord.supersedes
  scaffold      : Scaffold             # the captured "how" (§3.1)
  rubric        : AcceptanceRubric     # the captured "what good looks like" (§3.2) — the hard part
  target        : Selector             # who this binds to when it cascades down (§4)
  model_tier    : { teacher: ModelId, intended_floor: ModelTier }   # the cost dial it's meant to lift
  lifecycle     : "proposed" | "canary" | "promoted" | "reverted" | "escalated"
  baseline      : ObjectiveVector      # the teacher's measured result — the bar the fleet must meet
}
```

### 3.1 `Scaffold` — what the teacher actually did

```
Scaffold {
  prompt_template : Template            # the system/context block (the "meaty context" held high)
  procedure       : Step[]              # ordered reasoning/tool steps the teacher used
  exemplars       : Example[]           # few-shot input→output pairs distilled from the teacher run
  tool_recipe     : ToolBinding[]       # which tools, with which arg shapes (MCPFarm-scoped)
  notes           : Markdown?           # rationale / gotchas, for the human reviewer
}
```

### 3.2 `AcceptanceRubric` — the keystone of the keystone

This is where reproducibility actually lives. **A vague rubric makes "reproducible" mean "reproducibly
mediocre."** It is also the function that turns a raw run into a roll-up-able Run Record (§6) — so its
output shape *must* match the monoidal roll-up metrics.

```
AcceptanceRubric {
  dimensions : Dimension[]
  aggregate  : {
    pass  : "all floors pass AND weighted_score ≥ pass_threshold"
    score : "weighted mean of scored dimensions, 0..1"
    confidence : ConfidenceModel       # count-weighted; NOT a bare average (see roll-up §6)
    pass_threshold : 0..1
  }
}

Dimension {
  name           : string              # e.g. "correctness", "security", "format_conformance"
  type           : "floor" | "scored"  # floor = hard, lexicographic, pass/fail; scored = weighted 0..1
  evaluator      : Evaluator           # HOW it's measured (below)
  weight         : 0..1?               # scored only
  threshold      : number?             # floor pass bar / scored min
  evidence_required : string[]         # what the Run Record must carry to evaluate this dimension
}

Evaluator =
  | { kind: "programmatic", check: Ref }        # a test/assertion/linter — cheapest, most reproducible
  | { kind: "assertion",    match: Pattern }    # exact/structured equality
  | { kind: "model_judge",  judge_prompt: Template, judge_model: ModelId }   # LLM-graded; itself governed
  | { kind: "human",        queue: GateRef }    # escalation to a person
```

**Design stances (recommended):**
- **Prefer `programmatic`/`assertion` evaluators over `model_judge`** wherever the dimension allows.
  Deterministic checks are cheaper *and* more reproducible — and a `model_judge` is itself a non-determinism
  you'd then have to govern. Use `model_judge` only for genuinely subjective dimensions, and pin its model + prompt as part of the rubric version.
- **Floors are lexicographic and inherited** (security, compliance) — a Skill can *raise* a floor, never lower an inherited one (mirrors the cascade rule).
- **The `baseline` is the teacher's vector**, captured at promotion time. Fleet conformance = *fleet
  cohort's rolled score ≥ baseline within a dead-band*, not "identical output."

---

## 4. Targeting — one `Selector`, for "mandate to all" and "hand-pick" alike

```
Selector =
  | "all"                    # everyone at-or-below the issuing tier  (guardrails / mandated floors)
  | { role: RoleId }         # all agents with role Y, anywhere below  ("a skill for every Cloud Architect")
  | { ecosystem: Id } | { field: Id }   # a subtree
  | { selection: DID[] }     # hand-picked agents
```

A tier can only target **at or below itself**. `all` + a floor `SkillStandard` = the guardrail broadcast;
`selection:[…]` = the surgical assignment. **One mechanism, both uses.**

---

## 5. Erasure — the honest reconciliation with "no loss ever"

"Never lose a memory" collides with GDPR right-to-erasure and data-residency. We resolve it with
**immutability by default; erasure only via a governed, audited tombstone:**

```
RetentionState =
  | "active"
  | { tombstoned: { by: DID, policy_ref: StandardId, reason: string, at: EcosystemClock, signature: Sig } }
```

A tombstoned memory is **provably retired** — not silently lost. The record of *that it existed and was
retired, by whom, under which policy, when* survives; the body is purged on the schedule the policy
dictates. That distinction is exactly what auditors require and what makes the fabric enterprise-sellable.

---

## 6. The tie that closes the loop — rubric output **is** the roll-up metric

When a fleet agent runs under a Skill Standard, the rubric evaluates the run and emits the very vector
that rolls **up**:

```
RunRecord (excerpt) {
  skill         : ContentHash + SemVer
  scope         : ScopePath
  metrics       : { cost, tokens, score, confidence, floors_passed }   # ← monoidal: sums + count-weighted stats
  signature     : Sig
}
```

Because `metrics` are **sufficient statistics** (sums for cost/tokens; count + sum for averages;
count-weighted confidence), they aggregate associatively at every hop — the Universe sees the fleet's
*trajectory* against `baseline` without ingesting a single raw run. **The rubric is the bridge between
reproducibility (does the fleet meet the bar?) and roll-up (what does the Universe see?).** They are the
same number, measured once.

---

## 7. Security properties (carried from the spine)

- **Every record DID-signed + content-addressed** ⇒ attributable + tamper-evident.
- **Scope-path tenant isolation** ⇒ no cross-tenant leakage; promotion only to ancestors; global only by human gate.
- **Capability-scoped access** ⇒ an agent reads/writes memory only at-or-below its granted scope, and only if opted-in.
- **Resident vs registered authorship** ⇒ guardrail Skills are authored by resident (TCB) agents; a leased/registered agent can produce *workforce* memories but **cannot author a floor Skill** — it can never govern its own tuning.
- **`model_judge` evaluators are pinned + versioned** ⇒ a rubric's grader can't silently drift.

---

## 8. Decisions — **locked by JB, 2026-07-01** (recorded in `../decisions/`; one deferral)

1. **One store, one `MemoryRecord` lineage.** `SkillStandard` is a typed view/extension; "promote a memory
   into a skill" is a state transition, never a copy — provenance never forks.
2. **Rubric authority: workforce proposes, residents/humans ratify.** A rubric grades nothing until a
   resident or human signs it. The fox never guards the henhouse; its expertise still gets used.
3. **Confidence statistic — deferred to `0005` (Run Record & roll-up)**, picked per-objective there. Shape
   remains locked: count-weighted, never a bare average.
4. **`model_judge` cost: sample steady-state (1-in-N, a Tier Profile dial), full-grade on canary.**
   Promotion bars are measured, not estimated.
5. **Scaffold portability: compatible-family tag + canary measurement; block only on hard-floor fail.**
   Soft drift goes to the Objective Model to arbitrate the cost-vs-quality trade.

---

*Extracted to `contracts/v0/` (memory-record, skill-standard schemas). Successors: `0004` (Tier Profile —
the dials) and `0005` (Run Record & roll-up — where the deferred confidence statistic gets picked).*
