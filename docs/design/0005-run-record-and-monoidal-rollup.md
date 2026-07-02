# 0005 — Run Record & the Monoidal Roll-up (how the tree keeps score)

*Design draft for review — proposed by Fable 5 (design owner). Discharges open decision **#7** (the confidence
statistic, carried from `0001`) and pays `0004 §3`'s debt (objective **scoring** semantics). **All decisions
locked by JB 2026-07-02** (via AskUserQuestion, §8). Contract + simulator landed with the dive — the monoid
laws are tested, not asserted.*

---

## Why this is a keystone

Every number anyone trusts in Orreth is a roll-up: the League's **standings**, the Enterprise's
**quarter-close**, the marketplace's **"0.94 across 47 runs"** (AgentFacts, `0006 §5`), the sibling
**benchmarks**, the drift signal the governance loop steers by. One mechanism serves them all — and it must
compose *up the tree without raw records traveling*, because tenant isolation and the pruning metabolism both
forbid hauling raw runs to the apex. The answer is the oldest trick in distributed aggregation: **monoidal
sufficient statistics** (locked in the mechanism block of `../decisions/`), now given their contract.

---

## 1. The RunRecord — the aggregatable envelope

One unit of work, scored. The shape (`contracts/v0/run-record.schema.json`):

- **`agent` vs `author`** — the subject did the work; a **resident** (steward/judge) wrote the record.
  `0001`'s rule is enforced at ingest: **a self-asserted evaluation is rejected** (no agent grades its own
  yardstick — tested).
- **`(scope, goal_hash)`** — the cohort key, lifted straight from EH and made depth-agnostic (0000 §4).
- **Two clocks** (0004): `occurred_at` (universe-time — what bucket this belongs to: the season, the quarter)
  and `received_at` (wall). **Cost is physical** — tokens, model calls, dollars, wall-ms live on the wall side.
- **`scores[]`** — per-objective, against the tier's objective vector (0004 §3), each optionally
  `floor_breached`.

---

## 2. The StatBundle — the monoid

The sufficient statistics per cohort × bucket: `n`, outcome counts, per-objective
`{n, sum, sum_sq, min, max, floor_breaches}`, cost totals, and a `compliance` state.

- **`merge` is component-wise and associative; the empty bundle is the identity.** Chunk the runs any way —
  by team, by day, by tier — and the merged result is the same. *This is the "one truth" property:* a
  conference table is the merge of team bundles; the league table is the merge of conference bundles; nobody
  ever recomputes from raw. (Tested: chunked merges ≡ one-shot; the Rust plane will use fixed-point sums so
  bundles are bit-identical, not just statistically identical.)
- **The prior is applied once, at the report edge — never stored in the bundle.** Merging posteriors would
  double-count the prior; merging sufficient statistics can't. The bundle is pure evidence; opinion (the
  prior) enters exactly once, where a human reads.

---

## 3. Confidence — the Bayesian posterior (open #7, resolved)

**Locked 2026-07-02:** scores in [0,1] are mean-matched into pseudo-counts (`s = Σscore` successes,
`n − s` failures); the report edge computes a **Beta posterior** under a weak per-tier prior
(`confidence_prior`, a Tier Profile dial, default uniform (1,1)) and reports **mean + 95% credible
interval + n**.

- **Count-weighted by construction** — the locked mechanism's requirement falls out of the math instead of
  being bolted on.
- **Honest at tiny n** — the marketplace's "3 engagements" agent reads `0.94 ± wide`, not falsely precise;
  a proven n=200 reads tight. (Tested: same mean, n=2 vs n=50 — the small interval is strictly wider.)
- The simulator uses the closed-form normal approximation of the Beta; the plane may use exact quantiles.

---

## 4. Objective scoring — floors gate, weights average (0004 §3's debt, paid)

The tier score is the **weighted mean over non-floor objectives** (weights from the objective vector,
renormalized), under the tier's prior. **Floor objectives never enter the average** — they gate:

> **Locked 2026-07-02: flag, never average away.** Any floor breach in the window sets the bundle's
> `compliance: breached` — unmissable, undilutable by volume — and the performance mean is *untouched by it*.
> A 0.98 agent with one compliance breach shows **both truths**: 0.98, and breached. Regulators read the flag;
> buyers read both. (Tested: the breach flips compliance and moves the reliability mean by exactly nothing.)

---

## 5. Buckets are universe-time — standings and quarter-closes are the same monoid

A RollUp aggregates a **cohort × TimeWindow bucket**, and the bucket speaks universe-time (0004): the League's
season, the Enterprise's fiscal quarter, Earth Mapper's observation day. Bucket boundaries are policy
(a Standard / Tier Profile dial), not structure. **Late arrivals re-aggregate by superseding** — a RollUp is
content-addressed and immutable; a corrected one carries `supersedes`, and history never silently changes
(the same annotate-never-rewrite posture as tombstones).

The flow mirrors distillation: each tier rolls its own runs + its children's bundles, signs the RollUp with
**content-addressed pointers to every contributor** (the locked mechanism), and **pushes up**. Raw runs never
leave their field — the League test pins this: five games across two teams roll to a league table of `n=5`
while every raw run stays home.

---

## 6. Where the numbers surface

| Surface | What it reads |
|---|---|
| **AgentFacts** (`0006 §5`) | an identity's rolled bundles per skill/goal — "0.94 mean across 3 engagements" resolves to a becky-chained VC over a StatBundle |
| **Portfolio / interview** (`0002 §5`) | **locked 2026-07-02: mean + interval + n** — the anti-star-rating story made visible; `0002`'s noise defense applies on top for adaptive-query safety |
| **Sibling benchmarks** | bundles anonymized at the common parent (cohort aggregates only — the sim's `benchmark()` grows into this) |
| **The pane** (`0008`) | standings, trends, quarter-closes — the scrubber renders bucket sequences over universe-time |
| **Drift & canary** (`0001`, EH) | canary cohorts are full-graded (judge sampling 1.0) and their bundles compared against steady-state — same monoid, adversarial read |

---

## 7. Contract & simulator (landed with the dive)

`contracts/v0/run-record.schema.json` — RunRecord + `$defs` ObjectiveStat / StatBundle / RollUp.
Simulator: `orreth_sim/rollup.py` (empty · bundle_of · merge · report · tier_score) + `HarnessNode.record_run`
/ `roll_up` (push-up, distillation-style). **Five new tests, 17/17 passing:** monoid one-truth ·
count-weighted confidence · floor-flag-never-average · League standings up the tree · self-assertion rejected.

---

## 8. Decisions — **all locked by JB, 2026-07-02** (via AskUserQuestion; recorded in `../decisions/`)

1. **Confidence = Bayesian posterior** (Beta over mean-matched pseudo-counts, weak per-tier prior, mean + 95%
   credible interval). Discharges open decision #7 — the last one carried from `0001`.
2. **Floor breaches: flag, never average away.** `compliance: breached` at any breach; the mean stays honest;
   no gaming by volume.
3. **Portfolio shows mean + interval + n.** Honest uncertainty is the trust differentiator — a lucky n=2 and a
   proven n=200 are visibly different animals.

---

*Unblocks: AgentFacts get real substance (`0006 §5`), the League's standings engine exists before the League
does, the pane has numbers worth rendering (`0008`), and the next dives in the blessed order — `0010`
(AgentField & Gateways) → `0011` (Factories) → `0012` (HITL mechanics). The tree keeps score the way it keeps
memory: signed, composed, and never silently rewritten.* 🥃
