# 0006 — The Markers Dive

**Status: DESIGNED — JB's lock, 2026-09-19 (seeded 2026-09-18 on block 9).**
Markers were "super super important" in the old world; here they become
the kernel's open vocabulary of *why* — set by agents as they work, used
by agents to act, toggled by humans to see.

## JB's direction (essence preserved)

Every Objective, Intention, Observation, Thought/Action sets a marker on
the event being actioned; the ontology captures everything by dependency,
from either origin. Markers do two serious things: **immediate
observability** across dashboards (the bridge's main viewport with a
toggle per marker or per group), and **markers agents apply across every
context** — an agent policy may say "capture improvements IF observed and
mark them with respect to whatever was being executed", so that other
agents (security, the cloud architect) check on markers of X, Y, or Z to
drive further autonomous action. **Setting AND using markers drives
automation.** The vocabulary must be expandable.

## The model (locked)

- **A marker is a typed origin on a fact:** `marker {kind, id, parent, by}`
  on the envelope (0002). A root fact *mints* its marker; every fact that
  serves it carries the same `id`; a fact that begins something new under
  it mints a child with `parent` set. Markers are nodes; facts attach to
  them; parents form the dependency — queryable from either end.
- **The vocabulary is open and governed.** Kinds live in a **registry**
  (`kind · group · description · declared by`), declared before use; an
  unknown kind is refused with a teaching. Kinds carry a **group**
  (structural · quality · security · cost · …) so a dashboard toggles a
  kind or a whole group. The kernel seeds the structural kinds:
  objective (a human's ask, root) · intention (a schedule — human, role,
  kernel — root; its occurrences are objectives under it; **widened by
  0007 to any standing purpose — the schedule is its smallest form**) · thought (an
  include's ask, under the session's latest objective) · action (a tool
  call, a purge, a watch added — on the serving ask's marker) ·
  observation (a harness run, a red watch, a lease lapse — under the
  kernel intention that scheduled it). Everything else is declared as it
  arrives: `improvement`, `security-finding`, `cost-anomaly`, …
- **Setting.** The kernel mints structural markers on the write path,
  with the fact, in one transaction. Any body sets a marker on **whatever
  it is executing** through the **`mark` door** (kind · note · the ref it
  is about → a child of the current marker); **its policy says when** —
  every body carries the line *"if you observe an improvement to what you
  are executing, mark it `improvement`"*, and a template may add its own.
  Humans mark from the chat ("mark this as an improvement").
- **Using — the interest law.** A body's template declares the kinds it
  cares about (`interests`). Every marker set is a **fact on the rail**
  (`orreth.marker.set.v1`); a kernel consumer dispatches an ask to every
  interested body — *"a marker of kind X was set on Y by Z: act on it"*
  — **with that marker as the parent**, so the lineage records who acted,
  on what, because of which marker. Watches may count marker kinds.
- **Chain vs marker.** The authority chain says *who*; the marker says
  *why*. Both on the envelope, never conflated, both rendered.
- **Retention.** A marker is metadata on a Record entry and follows its
  fate; the lineage table keeps ids, kinds, and pointers — never words —
  so a purge leaves the tree's shape and empties its content.
- **Cost.** Four short fields; the words stay on the ground.

## Where it lives and how it shows

- **The ground:** `spine_markers` (marker_id · kind · parent · ref · by ·
  note · scope · at) written with the fact; `spine_marker_kinds` the
  registry. **The rail:** every event carries its marker; marker.set is
  itself an event — Understanding (0003) can rebuild the tree from the log.
- **Doors:** the tree under a marker · the ancestry above a marker · the
  stream by kind or group · the registry (read, declare).
- **The glass:** a MARKERS view — in the Monitoring pull first (sp1);
  **block 11 moves it to the ANALYZER** (lineage is history; Monitoring
  stays *now*) — live,
  toggles per kind and per group, every row a door; the bridge's main
  viewport inherits the toggles with the orrery work.

## Proof

- **MK-1 (revised):** the librarian, serving a human's ask (objective),
  observes an improvement and sets an `improvement` marker (a child); the
  critic, declaring interest in `improvement`, is dispatched an ask with
  that marker as parent and lands its critique under it — one lineage
  from the human's objective to an autonomous act, queryable from either
  end, rendered in the journey, toggled in the view. An undeclared kind is
  refused with a teaching.

## Build

- **markers sp1** ✅ **BUILT 2026-09-19** (walk owed): the registry with
  the structural seed · the write path minting structural markers · the
  `mark` door and the policy line · the interest consumer · the doors ·
  the MARKERS view · MK-1 proven by law (`tests/test_markers.py`).
