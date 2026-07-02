# 0004 — Tier Profile & the Two Clocks (the dials that make a tier)

*Design draft for review — proposed by Fable 5 (design owner). Builds on the `contracts/v0/tier-profile.schema.json`
head start (every dial locked by prior decisions already ships there; this spec **refines, not redefines**). The
centerpiece is new: **the two-clock model**, surfaced by The League (0013 §11 PG-1) — the first universe whose
internal time outruns ours. **Open decisions** flagged for JB at the end. Schema deltas land in `contracts/` only
after blessing, per the dive rhythm.*

---

## Why this is a keystone

"Tier = a profile, not code" is the recursion promise (0000 §1): one node, dials turned differently. Every
decision we've locked — retention leans, TTLs, QA sampling, judge sampling, steward exhaustion behavior — needs
one governed home, and this is it. And the proving grounds just raised the stakes: the League cannot be built
until the profile can say *whose clock this universe runs on*.

---

## 1. The two clocks — meaning vs security

`EcosystemClock` in v0 is a UTC timestamp — "the universal index." That quietly assumes a universe lives at the
speed of the real world. The League breaks the assumption on day one: thirty seasons of lived history simulated
in weeks. Two different times are being conflated:

- **Wall-clock** — physical, shared, unforgeable-by-consensus time. Keys expire in it; money is spent in it;
  humans co-sign in it.
- **Universe-time** — the universe's own lived timeline: season 12, game 47; fiscal Q3; "the moment the
  championship was won." Memory *means* things in this time.

> **The rule: meaning runs on universe-time; security and money run on wall-clock.**
> Memory horizons, retention, pruning cadence, the spacetime window's scrubber — universe-time.
> Token TTLs, co-sign windows, vigil's dead-man heartbeat, rate limits, steward token budgets — wall-clock.
> A universe may dream at any speed; its locks rust at ours.

### The declared clock (proposed model)

Universe-time is not a dilation factor — simulations run in bursts, pause overnight, and resume. It is a
**declared, monotonic coordinate**: the universe (its simulation driver, or reality itself) *asserts* its own
now, and the substrate enforces honesty about it.

- Every `MemoryRecord` carries **two timestamps**: `occurred_at` (universe-time — part of the signed content;
  the author's claim about *when in the universe's life* this happened) and `received_at` (wall-clock — stamped
  by the Gateway on ingest; nobody's claim, just physics).
- **Monotonic high-water enforcement per scope**: `occurred_at` must be ≥ the scope's high-water mark, or the
  record is rejected as lived memory. **You cannot quietly write yourself a past.** Retroactive memory forgery
  — the substrate's version of backdating a document — becomes structurally detectable, not just detectable
  by audit.
- **Lived vs ingested** — the legal way to carry history below the high-water mark: records labeled
  `ingested-archive` (a `provenance_class` facet). Earth Mapper's 170 years of hurricane data enters as
  *ingested archive*, honestly distinct from what its agents lived. The window can render both; it never
  confuses them. *(This formalizes the distinction that drove the proving-grounds decision: backfilled archives
  are data; lived memory is biography.)*
- For real-time universes (Enterprise, Earth Mapper), the declared clock simply tracks wall-clock — the model
  costs nothing when dilation is 1:1.

### Which dial runs on which clock

| Universe-time (meaning) | Wall-clock (security & money) |
|---|---|
| `memory.raw_retention` / `distilled_retention` | `tokens.workforce_ttl` / `resident_ttl` |
| `retrieval.horizon` (how far back a tier serves) | co-sign windows, cooling-off periods (0006/0013) |
| `Query.time` windows; the pane's scrubber | vigil's heartbeat + dead-man window (0013 §3) |
| pruning/distillation *triggers* (season-end, quarter-close) | steward `token_budget` + base `cadence` (compute is physical) |
| roll-up buckets (0005 — standings, quarters) | rate limits, ingest quotas, Custodian telemetry cadence |

*(Steward scheduling is both: cadence in wall-clock because compute costs real money; event triggers in
universe-time because "season just ended" is when distillation is meaningful — 0003's cadence + event-trigger
lock, now with each leg on its proper clock.)*

### Schema delta (lands on blessing)

`EcosystemClock` generalizes to **`UniverseTime`** (it was always the lived clock; now it says so) ·
`MemoryRecord.created_at` splits into `occurred_at` + `received_at` · records gain
`provenance_class: "lived" | "ingested-archive"` · `TierProfile` gains a `clock` block:

```
clock {
  mode              : "wall" | "declared"     # declared ⇒ the universe asserts its own now
  high_water_scope  : ScopePath               # monotonicity enforced per this scope
  dilation_hint     : number?                 # display/ops only (pane scrubber, cost projection) — never logic
}
```

---

## 2. The dial catalog — what v0 already carries

The v0 schema groups, their meaning, and the locked starting leans (already in the schema descriptions):

| Group | The dial, in one line | Leans |
|---|---|---|
| `memory` | how long raw and distilled live before the metabolism (0003) takes them; sealed QA sample past horizon | P90D raw field · P13M distilled eco · forever at apex · QA 1-in-100 field |
| `retrieval` | the per-tier time budget (escalation gate, 0002 §3) + horizon before delegating up | apex horizon = `forever` — all of spacetime |
| `steward` | ingest cognition's token budget, cadence, and the locked exhaustion behavior | degrade-to-floors-and-flag, never backpressure |
| `tokens` | becky's TTL dials (0006) | workforce P1D · resident P30D |
| `model_gateway` | judge sampling (0001), default model tier, governed routing | 1-in-N steady · 1.0 during canary |
| `join_default` | the join-spectrum default for children | hosted tenants: floors-only to the Custodian (0013 §1) |
| `trust_root` | did-web vs pinned (0006) | did:web hosted · pinned air-gapped |

New in 0004: the `clock` block (§1) and the `objective` block (§3). One correction of omission: 0000 §4
promised the TierProfile carries an **objective vector**; v0 shipped without it.

---

## 3. The objective vector — what "good" means at this tier

The dial the whole governance loop steers by: a small, versioned set of weighted objectives
(`{objective, weight, floor?}[]` — e.g. League field: `win-rate 0.4 · fan-engagement 0.3 · player-development
0.3`; Enterprise eco: `accuracy 0.5 · compliance floor · cost 0.2`). The steward distills *toward* it (what's
worth keeping is what the objective says matters), drift is measured *against* it, and the Objective Model
arbitrates soft conflicts (0001's scaffold-portability lock already assumes it exists). **Shape lands here;
scoring semantics land in 0005** (Run Record & roll-up), where objectives meet the monoidal statistics they're
computed from. Floors inside the vector are floors: a compliance objective at `floor` never trades off.

---

## 4. Retention is a minimum *and* a maximum

v0 treats retention as one duration. The Enterprise exemplar exposes the truth: regulated memory has
**keep-at-least** obligations (books-and-records: SOX, tax — deletion before N years is the violation) *and*
**keep-at-most** obligations (consent, GDPR — retention past purpose is the violation). So:

- `retention` becomes `{ min?, max? }` **per record class** (a small enum of classes: `operational`,
  `financial-record`, `personal-data`, …, extensible by Standard).
- The cascade enforces **each direction independently, tighten-only**: a parent's `min` may be raised by a
  child, never lowered; a parent's `max` may be lowered, never raised. (Same resolver, two monotone lattices.)
- Legal hold (0013 §5) is a governed, temporary `min: ∞` on a scope — and the tombstone-suspension rule
  ("preserve, then adjudicate") falls out of the same mechanism instead of being a special case.

---

## 5. Profiles are cascade artifacts

A TierProfile is signed, versioned, and **cascaded like any Standard**: the parent's profile floors bind the
child's (tighten-only, per-dial monotonicity as in §4); the friendly `tier_label` stays display-only. Profile
*changes* ship through the lane-routed Standards flow (0008): low-risk dial turns (QA sample rate) ride the
auto-apply lane, signed and canaried; consequential ones (retention, clock mode, join default) take the
governed lane with a human gate. For hosted universes, the **Custodian's join credential pins the floor bundle
at onboarding** (0013 §8) — trust-tier autonomy ceilings arrive as profile floors, not as prose.

---

## 6. The three proving-ground profiles (worked examples)

| Dial | **The League** (time axis) | **Earth Mapper** (space axis) | **Agentic Enterprise** (northstar) |
|---|---|---|---|
| `clock` | **declared**, bursty (a season per wall-night); scrubber in seasons | wall (1:1) + `ingested-archive` backfill | wall (1:1); fiscal calendar as universe-time annotations |
| `memory` | raw: 2 seasons · distilled: forever ("legends") — universe-time | raw: P30D (imagery is huge) · distilled: P10Y | per §4 min/max by record class (SOX min · GDPR max) |
| `retrieval` | deep-time cheap to demo: generous apex budget | breadth-heavy queries; modest depth | strict budgets; every read an access record regulators can see |
| `model_gateway` | **cheap cognition**: sims are code; LLM only for scouting/commentary | mid: analysis agents on ingest | premium tiers, full judge sampling on anything customer-facing |
| `join_default` | floors-only to Custodian; teams fully-joined to league | floors-only to Custodian | floors-only + regulator observe-only entitlements |
| objective (§3) | win-rate · fan-engagement · development | coverage · freshness · discovery | accuracy · compliance (floor) · cost |

*The League profile is the first one the provisioner (0009) should learn to render — it is the funnel's "Play"
step (0013 §11) wearing config.*

---

## 7. Decisions — **all locked by JB, 2026-07-02** (via AskUserQuestion; recorded in `../decisions/`)

1. **Clock model: declared + monotonic high-water + lived-vs-ingested labeling.** Bursty sims work honestly;
   memory-backdating is structurally detectable; archives never masquerade as biography. The general answer
   for every future game/sim universe, not a League special.
2. **Query default: universe-time.** `Query.time` windows and the pane's scrubber speak the universe's lived
   time; `clock: "wall"` is the explicit ops/forensics escape hatch.
3. **Retention is min *and* max, per record class.** Keep-at-least and keep-at-most cascade independently,
   tighten-only; legal hold = a governed `min: forever`, no longer a special case.
4. **Objective vector: shape here, scoring semantics in 0005** — where objectives meet the roll-up statistics
   that score them.

**Schema deltas landed on blessing** (same day): `UniverseTime` + `WallClock` replace `EcosystemClock`
(data plane speaks UniverseTime; control plane speaks WallClock) · `MemoryRecord.created_at` →
`occurred_at` (signed) + `received_at` (gateway-stamped) + signed `provenance_class` · `TimeWindow.clock`
defaulting to `universe` · TierProfile `clock` / `objective` / `retention_classes` blocks. The reference
simulator enforces the high-water rule and proves it: **12/12 tests**, including backdating-rejected and
archive-honesty (flipping `lived → ingested-archive` to smuggle a backdate breaks the author's signature).

---

*Unblocks: `0005` (roll-up buckets are universe-time buckets — standings and quarter-closes are the same
monoid), the League build (first declared-clock universe, the funnel's "Play" step), the provisioner's first
template (0009), and honest archives for Earth Mapper. The universe dreams at any speed; the locks rust at
ours.* 🥃
