# 0006 — The Markers Dive (SEED)

**Status: SEED — opened 2026-09-18 on JB's lock (block 9); designed before
Phase 5 (memory whole) projects it.** Markers were "super super important"
in the old world and are absent from the rearch canon; this document holds
the seat until the dive.

## JB's words (essence preserved)

Every **Objective, Intention, Observation, Thought/Action** sets a
**marker** attribute on the event being actioned. Orreth's inherent
ontology then captures everything in association to its dependency —
starting from thoughts, or starting from objectives/intentions, depending
on the origin of the request. Markers give the main view lots of things to
toggle on and off in the Monitoring view; the main window goes full screen
and serves as the **live observability of the Operating State**. Markers
are central to understanding, querying, and working with the Operating
State.

## The hooks already in canon

- **The envelope (0002)** carries `correlation_id`, `aggregate {type, id,
  sequence}`, and the `authority_chain`. A marker is a typed origin on the
  same envelope — a candidate shape: `marker: {kind: objective | intention
  | observation | thought | action, id, parent}` — so every fact on the
  rails names what it serves and what it descends from.
- **Understanding (0003)** is the entity/relationship/temporal projection
  over the Record; the marker dependency graph is one such projection —
  rebuildable, never truth.
- **The journey (0001 P7, 0004)** is emitted at every hop; a marker rides
  with it, so the journey text can say *what objective* an act serves.
- **The main view (0001)**: lenses on the sill; markers become the
  toggles of the Monitoring lens.

## The dive's questions

1. Who sets a marker, and when — the human (an objective typed in the
   chat), a resident (an intention it schedules), the kernel (an
   observation, a reflex), a firmware agent (a thought/action)?
2. Two origins, one graph: from a thought upward to the objective it
   serves, from an objective downward to every act it caused — is one
   `parent` link enough, or does a marker carry both its cause and its
   purpose?
3. Markers vs the authority chain: the chain says *who*; the marker says
   *why*. Never conflate; always render both.
4. Retention and purge: a marker is metadata on a Record entry — it
   follows the entry's fate (0003's governed erasure).
5. What the main view toggles: kinds, owners, worlds, time windows — and
   what "live" means (the Events rail, never a poll).
6. Cost: markers must not make the envelope heavier than a pointer; the
   words stay on the ground.

## Proof (to be named at the dive)

- **MK-1**: a chat objective causes a resident intention causes a
  firmware thought causes an act — four events, one marker lineage,
  queryable from either end, rendered in the journey and toggled in the
  main view.
