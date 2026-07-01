# 0003 — Pruning Policy (the metabolism)

*Design draft for review. Schemas are language-neutral shapes, not code. Builds on `0001` (MemoryRecord),
`0002` (identity + retrieval), `0000` (structure). **All governing decisions locked by JB 2026-07-01**
(see `../decisions/`): hybrid pruning brain · apex = distilled + signed pointers · tombstones annotate ·
QA sample per-tier · degrade-to-floors on budget exhaustion · cadence + event triggers.*

---

## Why this is a keystone

Pruning is the **only irreversible operation** in an otherwise append-only system. Everything else can be
audited backward; a bad pruner silently destroys "memory that never fades" and you cannot retroactively
unprune. It is also the economics of the whole substrate: **the layers are filters** — pruning is what makes
"years" affordable — and it is the **fidelity curve of the spacetime window**: the present is pixel-sharp, the
deep past is a distillation, and this spec decides exactly how that softening happens, on the record.

> Context rises so the world can learn. Pruning is the discipline that keeps learning from drowning in what
> it lived through.

---

## 1. The pruning brain — floors + steward (locked)

Every layer prunes with two cooperating mechanisms:

- **Deterministic floors (the plane, Rust).** Non-negotiable `KeepRule`s evaluated on ingest — cheap,
  predictable, auditable. They guarantee that what *must* survive, survives, no matter what the steward thinks.
- **Steward distillation (cognition, Python).** The resident memory steward compresses everything the floors
  didn't pin, under a governed rubric, on a cadence, within budgets — and is free to *notice* what no rule
  anticipated and pin it.

```
PruningPolicy {
  scope      : ScopePath              # the layer this binds; cascades — lower layers may tighten, never loosen
  floors     : KeepRule[]             # deterministic; inherited floors are non-overridable (lexicographic)
  distill    : DistillDirective[]     # what the steward compresses: cohort, cadence, target ratio, rubric ref
  budgets    : { storage: Bytes, steward_tokens: Budget }   # the metabolism's cost dial (per Tier Profile, 0004)
  version    : SemVer                 # a PruningPolicy is a Standard — versioned, signed, reversible
  signature  : Sig
}

KeepRule {
  match      : Predicate              # kind / tags / outcome (failure, floor-breach) / outlier (top-bottom N%)
  action     : "keep-raw" | "distill" | "drop-after-distill"
  keep_for   : Duration | "promote"   # how long raw survives at this tier, or promote up (0001 Promotion)
  reason     : string                 # every rule says why — the audit trail starts in the policy itself
}
```

**Keep-classes.** Every record at every tier is in exactly one class at any time — and every class transition
is a **signed pruning record** (who/what moved it, under which policy version). Nothing is ever *silently* lost:

`keep-raw` → `distilled (raw retained)` → `distilled (raw dropped on schedule)` → `tombstoned (governed, 0002 §6)`

---

## 2. The Distillation record — provenance survives compression

This discharges the pruning-vs-provenance finding (review 2026-07-01). A distillation is a **new memory** whose
truth chain stays verifiable:

```
Distillation extends MemoryRecord {
  kind         : "distillation"
  derived_from : ContentHash[]        # the signed chain to every input
  method       : { steward: DID, rubric: StandardRef, model: ModelId, prompt_version: SemVer }
  window       : TimeWindow           # the spacetime slice it compresses
  cohort       : Selector?            # whose memories it summarizes
  redactions   : RedactionMarker[]    # tombstoned inputs — annotate, don't rewrite (locked)
}

RedactionMarker { tombstone_ref: ContentHash, at: EcosystemClock, policy_ref: StandardId, sig: Sig }
```

- **Verified(derived) = chain verification.** A distillation is Verified when its own signature checks *and*
  its `derived_from` pointers resolve — to live records, to retained-but-deep raw, or to tombstone stubs.
- **Tombstones annotate (locked).** When a source is tombstoned, the distillation *stands*, gaining a
  `RedactionMarker`. The clinic's monthly stats survive the patient's erasure — marked, auditable, honest.
  History never silently changes; auditors see exactly what was removed, when, under which policy.
- **The method is pinned.** Steward DID + rubric version + model — a distillation's grader can't drift
  invisibly (same rule as `model_judge` in 0001).

---

## 3. Apex fidelity — distilled + signed pointers (locked)

What each tier physically holds, and what a deep query gets:

| Tier | Holds | Raw retention (default dial — final numbers in 0004) |
|---|---|---|
| **Field** | raw, hot | 30–90 days raw, then distill-and-drop per class |
| **Ecosystem** | distillations + `keep-raw` classes + signed pointers down | ~13 months distilled; pinned raw per floors |
| **Universe** | all-time distillations + promoted raw + signed pointers down | forever (distilled); promoted raw indefinitely |

- A deep-time query answers **from distillations first**, then **re-fetches surviving raw** through the normal
  retrieval contract (0002) where the moment needs to be sharp — the pointer *is* `body_ref` from 0001.
- When lower-tier raw has lapsed, the pointer resolves to a **tombstone-stub** and the result says so:
  `verification: "verified (distilled; raw expired <date>, policy <ref>)"`. The window never pretends.
- **Fidelity-with-depth is now a contract, not a metaphor**: sharpness = f(keep-class, retention dial, tier).

---

## 4. The steward's ingress loop

Per cadence (Tier Profile), the steward: **dedup** (content-hash — free) → **cluster** (embedding
neighborhoods) → **distill** (per `DistillDirective`, scored against its rubric) → **pin** (anything it judges
keep-worthy that floors missed — its judgment is *additive* to floors, never subtractive) → **sign & emit**.
Budgets are enforced by the plane (steward model calls flow through the layer's Model Gateway like everyone
else's). Steward rubrics are **Standards authored by residents/humans only** — the 0001 rule; a workforce agent
never grades what survives of its own history.

**Skills are the pressure-release valve** (0001): once a lesson is promoted into a versioned skill, its raw
teacher runs become expendable — pruning *accelerates* behind promotion. Learning is what permits forgetting.

---

## 5. Security & audit properties

- Every class transition, distillation, and drop is a **signed record** — pruning has a worldline of its own.
- PruningPolicy **is a Standard**: versioned, canaried where meaningful, reversible, cascaded with
  non-overridable floors — a lower tier can keep *more*, never less, than an inherited floor demands.
- **No steward self-dealing**: rubric authorship resident/human-only; steward outputs signed by the steward's
  own DID (Sourced), method-pinned (Verified).
- Erasure remains **only** via governed tombstone (0002 §6) — pruning drops bodies on schedule, never identity,
  never the audit stub.

---

## 6. The honest edge — measuring what pruning loses

A distillation rubric can be confidently, reproducibly mediocre. The mitigation is empirical: retain a random
**QA sample** of raw past its horizon (sealed, excluded from normal retrieval) and periodically score
distillations against the ground truth they claim to compress. Distillation quality becomes a *measured*
objective in the layer's vector — drift in it is drift like any other, and the loop we already have tunes it.

---

## 7. Decisions — **all locked by JB, 2026-07-01** (recorded in `../decisions/`)

1. **QA sample: yes, per-tier dial.** A sealed 1-in-N raw sample survives past horizon (excluded from normal
   retrieval), used only to score distillations against ground truth. Distillation quality is a measured
   objective; drift in it is drift like any other. N set in the Tier Profile (0004; starting lean: 1% Field,
   0.1% Ecosystem).
2. **Budget exhaustion: degrade to floors + flag.** Floors never stop; everything lands; the surge distills
   coarsely; the layer raises a quality-drift signal and the pane marks the window "coarse." Ingestion is
   never backpressured by its own librarian.
3. **Cadence + event triggers.** A slow, predictable floor cadence per tier, plus cohort-size / novelty
   triggers that fire an extra pass — the hot window stays sharp while it still matters.

---

*Unblocks: `0004` (Tier Profile — the retention/budget dials this spec parameterizes), `0006` (becky — next),
and it makes `the-spacetime-window.md`'s fidelity-with-depth edge a designed contract instead of a caveat.* 🥃
