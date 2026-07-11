# 0024 — Markers & the Severity Lanes (grading 100% of change)

*Design draft — proposed by Fable 5 (design owner), from the Universe-Brain session
(2026-07-10, `../vision/the-universe-brain.md` §6). Every governing decision was
**pre-locked that session** (R5: markers as first-class annotation records, two
orthogonal families · R6, JB lock: severity-routed plan lanes); this dive mechanizes
them. Builds on 0005 (the RunRecord — every achieved objective IS a change), 0012
(gates and quorums — the lanes' heavy end), 0022 (the tags index the markers ride),
and 0023 (the Librarian and her parlor, where "remember this" arrives).*

---

## Why this is a keystone

JB's requirement, verbatim in spirit: **the Universe understands 100% of change.**
Anything an agent achieves in an objective/intent is a change; anything the human says
to remember, or a resident deems memorable, gets a marker — and security's findings
mark too. The census already exists (every write is signed, every run diaried); what's
missing is the **grading**: which changes were consequential, which moments were
life-events, and — through R6 — which *plans* may proceed on which lane. Markers turn
the record into judgment without ever touching the record itself.

---

## 1. The Marker — a first-class annotation record

A marker is a **signed MemoryRecord** deriving from what it marks — never a mutation
(annotate-never-rewrite, the substrate's one grain):

```
Marker (a MemoryRecord, kind="semantic", tags include "marker") {
  derived_from : [ContentHash]          # the marked record(s) — REQUIRED, ≥1
  body.marker  : {
    change_severity? : "low" | "medium" | "high" | "critical"
    life_event?      : "minor" | "major" | "substantial"
    reason           : string            # every marker says why (0003's KeepRule rule)
    rubric           : StandardRef       # the grading standard version it applied
    quoted?          : string            # the human's words, when a human asked
  }
}
```

- **Two orthogonal families, one shape** (R5): `change_severity` for what agents and
  humans *did*; `life_event` for what the human-meaningful timeline *holds*. A marker
  may carry either or both. At least one family is required.
- **No contract change**: markers ride `kind: "semantic"` + the `marker` tag — the
  0022 Phase-1 tags GIN indexes them already. (A dedicated `kind: "marker"` is a
  possible contracts/v0 hardening later; it is not needed to be first-class — being a
  signed, derived, queryable record is what first-class means here.)
- Multiple markers accrue on one record; each is signed by whoever placed it. The
  marked record never changes.

## 2. Who grades (R5, mechanized)

| Grader | Places | Under |
|---|---|---|
| The authoring resident | `change_severity` on the changes its duty produces (charlotte on decoms, becky on leases, the shipyard on launches) | the cascaded grading Standard |
| The critic (0015) | `change_severity` on RunRecord outcomes | the chassis rubric |
| vigil | security markers (a finding is marker-worthy by definition) | its detection posture — stages, never enforces |
| Any resident receiving "remember this" | `life_event`, quoting the human | the human's own words pick the weight; default `minor` |

**Grading rubrics are Standards** — versioned, cascaded, diffable, canary-able
(behavior as data, 0001). "Why was Tuesday's decom graded high?" is a rubric-version
lookup, not an argument.

## 3. The Severity Lanes (R6 — JB lock, 2026-07-10)

The human's ask is the HITL on the **intent**; the **plan** routes by its severity:

```
lane(change_severity) =
  low              → auto-approve under the gate policy — signed, on the record, canary-able
  medium           → resident co-review + human NOTIFY (visible, not blocking)
  high | critical  → the human gate; 0012 quorum where the class demands it
```

- The lane table is a **cascaded gate policy** (0012 §2 — tighten-only: a child may
  raise a class's lane, never lower it).
- **No existing gate loosens by this dive**: joins, service plantings, mind saddlings,
  and ecosystem launches keep their human gates (their classes grade high/critical).
  The lanes' immediate wire use is the *low* end: a human's "remember this" is intent
  and plan in one breath — the marker writes on the auto lane, marked as such.
- Every lane decision is itself on the record: the resolution notes `lane` and the
  marker carries the rubric that graded it.

## 4. "Remember this" — the human's marker, through the parlor

The parlor law holds: the human never writes a record; they *ask*. `remember this:
<words>` (optionally `as major` / `as substantial`) to the Librarian:

1. The audience lands as usual — the exchange record, resident-signed, quoting the ask.
2. The Librarian places a **life_event marker deriving from that audience record**,
   `quoted` carrying the human's words, weight parsed from the ask (default `minor`).
3. The reply confirms verbatim (flow-control is protocol, never voiced).

This is the second-brain's write-path seed: the moments you tell the universe to keep
arrive graded, quoted, and signed — and the profile dive (next) will read them.

## 5. Mechanism — what this dive lands

1. **Reference (sim)**: `make_marker` (families validated, `derived_from` required,
   reason required) + `lane_for` (the R6 table) + conformance tests: marker derivation,
   family validation, lane routing, remember-this parlor routing.
2. **Wire (worker)**: the parlor `remember` route on the Librarian (audience → marker,
   auto lane) · change markers on the flows that already pass gates — a join completed
   (low), a service decommission/discredit (high), an ecosystem launch (critical) —
   each deriving from the record of the thing it grades, signed by the resident that
   did the duty.
3. **Deferred to the ledger**: vigil's security markers (vigil has no wire organ yet) ·
   critic markers on RunRecords (rides the chassis; lands with the fingertip dive) ·
   the medium lane's notify surface (Console badge — rides the workspace spoonful).

## 6. Decisions

**Pre-locked by JB (2026-07-10, recorded in `../decisions/`):** markers as first-class
annotation records, two orthogonal families with his ladders (R5) · severity-routed
plan lanes, low auto / medium co-review+notify / high+critical human (R6).

**Closed by the design owner (JB may veto):** markers ride `semantic` + `marker` tag —
no contract change · at least one family required, reason always required · the
remember-this weight defaults `minor`, parsed from the ask when given · no existing
gate class loosens in this dive — the auto lane's first resident is the human's own
"remember this."

---

*The record was already complete; now it can tell you what mattered. Change wears its
weight, moments wear their meaning, and the only thing that ever auto-approves is what
the human just asked for in plain words.* 🥂
