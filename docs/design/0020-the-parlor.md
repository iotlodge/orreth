# 0020 — The Parlor: humans speak through the institution

*Drafted 2026-07-07 by Fable 5 (claude-fable-5), from JB's interoperability objective
(2026-07-07): "Humans always interact through an Agentic Flow… users can't see data
directly and must go through either a resident or a workforce agent… Agents, if
authorized, are able to see data within the universe; humans must ask for it."*

---

## §0 The law

**Agents, when authorized, see data inside the universe. Humans never do.**

A human's only read is an *ask*: received by a resident, who fetches with its **own**
authority under its **own** capability, and answers on the record. The parlor is the
room where that happens — the audience room of the estate that already has a farm
(0018), a stable (0019), and a pasture. Callers are received here; nobody wanders
the stacks.

This inverts nothing — it *completes* 0000 §2's staffing picture. The Console was
already agentic underneath (every render a tokened query; asks through the request
queue since 0014). The parlor makes the human-facing half of that explicit,
conversational, and extensible without touching the core.

## §1 The transport — no new doors

The parlor rides the request queue exactly as every other human intent does
(`main.rs`: "a human submits an intent; cognition picks it up and acts with
authority"). One new kind:

```json
{"kind": "parlor", "to": "charlotte", "session": "pa-x1", "verb": "card"}
{"kind": "parlor", "to": "charlotte", "session": "pa-x1", "text": "what is serving?"}
```

The worker resolves each with `result: {card}` or `result: {reply, voiced, by}`.
**Zero plane changes.** That is the decoupling proof, not just a convenience: an
entire human-facing capability landed without a line of Rust, because the
architecture already routes every human touch through governed cognition.

## §2 The calling card — interoperability as data

Each resident publishes a **calling card**: greeting, role, DID, and the *asks* it
offers — its own collection flows, declared as data:

```json
{"resident": "librarian", "greeting": "…", "role": "librarian · knowledge",
 "did": "did:key:z…", "voiced": true,
 "asks": [{"label": "gather knowledge on…", "template": "gather sourced knowledge on "},
          {"label": "what do you hold?", "ask": "what knowledge do you hold?"}]}
```

The Console renders cards **generically** — chips from `asks`, `ask` sends
immediately, `template` prefills the input. The glass knows no resident by name. A
new resident with entirely new flows changes *nothing* in core Orreth: it brings its
card, and the parlor renders it. This is the contract that keeps agent UX decoupled
from the architecture — the card, not the code.

## §3 The audience is on the record

Every answered exchange becomes a signed MemoryRecord, **authored by the resident**,
tags `["parlor", <name>]` — a brass-visible event in the spacetime window. Humans at
the gates, signatures on the record. The caller's words ride inside the body until
humans carry signatures of their own (0012's signer registry — future work); the
resident witnesses, and nothing self-attests an outcome that isn't its own.

## §4 Voiced and unvoiced — the honest ladder

- **Embodied residents** (becky, charlotte, librarian, ada — persistent seeds, real
  DIDs) always answer **grounded**: the deterministic reply is composed from state
  they are authorized to read (their ledgers, the farm, the stable, the queue).
  When the floor is fueled (provider key + litellm, join floor only — the same rule
  as ada's canary), the resident *phrases* that grounded answer through one governed
  thought: authorize → think → meter, under its own DID, facts riding in the prompt,
  the prompt never touching the plane (0016 §6, 0019 §4). The dialog labels which
  path answered: "a governed thought · metered under my DID" vs "answered from the
  record". Unfueled is never silent and never fakes.
- **Unembodied organs** (vigil, steward, governance) still receive the caller — the
  parlor never shows a dead door — but say honestly that they have no voice yet,
  answering with their structural vitals. Their seats are reserved; each one's
  incarnation is its own dive (the librarian organ is next, per the build ledger).
- The librarian's `gather …` ask routes to its **real** 0014 duty — the parlor is a
  front door to existing loops, not a parallel path.

## §5 The glass — the resident's workspace

Click a resident — in the rail or on its organ dot in the orrery — and the parlor
slides in from the right: a drawer, not a page, so the universe keeps turning behind
it. Header carries name · role · floor (the parlor is floor-respective: you are
received by *this* floor's resident, and the scope says so). Thread below; card
chips; one input. On a phone it takes the full glass. In spectator mode the door is
sealed with the uniform refusal, phrased honestly: *a spectator may watch this world
turn, never speak into it.*

## §6 Decisions taken (design-owner calls, JB may override)

1. **Name: the Parlor** — the estate receives its callers where estates always have.
2. Transport = the existing request queue; no `/parlor` routes, no plane edits.
3. The card is resident-published data; the Console renders it blind.
4. Exchanges land as resident-signed MemoryRecords tagged `["parlor", <name>]`.
5. LLM voicing is optional polish over a mandatory grounded answer — never the
   other way round.

## §7 Deferred

- Human signatures on the ask itself (needs 0012's signer registry).
- Workforce-agent parlors (same card contract; their cards arrive at join time —
  pairs naturally with the join-door hardening on the ledger).
- Typed multi-field card inputs (the schema field exists; v1 renders label +
  template only).
- Cross-floor audiences (asking the apex's steward from a field console) — waits on
  governed escalation lanes (0012).
