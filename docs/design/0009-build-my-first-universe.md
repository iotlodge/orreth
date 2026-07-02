# 0009 — Build My First Universe (the design phase's closing brace)

*Design draft for review — proposed by Fable 5 (design owner). The last dive of the sequence. **All decisions
locked by JB 2026-07-02** (via AskUserQuestion, §5) — including the final three open items in the entire
ledger (#12 templates · #13 tone default · #14 subscription). Contract + simulator landed with the dive.*

---

## Why this is the closing brace

Everything the week built converges here. A **template** is: a pre-authored chain for the resolver to fold
(`0007`), TierProfiles with a clock (`0004`), a roster of StampOrders (`0011`), starter floors under the
platform's (`0013`), a tone position (`0010`'s dials among them) — **a universe as data, not code**
(`0000 §6`). The **provisioner** renders it: root ceremony, tiers stood up staff-first (`0006`), floors
published, tone seeded, roster stamped through the Gateway (`0010`), trust tier checked at the door
(`0013 §8`, with `0012`'s bars making a regulated template *structurally* unavailable below quorum). This is
the funnel's **Play** step (0013 §11): pick League, name it, and a world exists.

## 1. The first templates — **League · Second Brain · Company** *(locked, #12)*

One per funnel stage: **League** = the flagship and the playable proof (declared clock, wild-leaning, a draft
class per team); **Second Brain** = the personal hook, the cheapest world, everyone's first *mine*; **Company**
= the Enterprise seed, REAL-toned, `verified`-tier gated. Game waits (the League *is* a game with cleaner
metrics); Lab waits honestly — it requires the regulated tier, which the quorum rule makes unavailable until
the Custodian org is staffed. A greyed-out Lab template is the bars-are-absolute lock, visible in the storefront.

## 2. Wild-vs-REAL — rigor, never safety *(locked, #13)*

The dial's members: `signal_capture` (wild: chatter evaporates · REAL: everything remembers), judge sampling
(REAL watches harder), retention classes, gate strictness. **The platform floors are identical at both ends —
the spectrum never touches safety** (tested: a wild League and a REAL Second Brain resolve to *equal* floor
sets). **Blank universes default REAL; templates override** — wild is a choice you make visibly, and nobody
discovers at audit time that their real work ran loose.

## 3. Fuel, hibernation, and the honest free tier *(locked, #14)*

Charge by **fuel, not time**: the free tier is a one-time allotment — worst-case cost per signup is a constant
the operator sets, a metered marketing spend, not a bleed. Out of fuel (or idle past the timer):

> **Hibernate, never delete.** Agents pause; the memory-first promise holds; the read-only window stays
> watchable — *your universe never dies; it dreams only when fueled.* Wake it by subscribing, or bring your
> own model key (the hobbyist pays their own LLM bill and stays a zero-cost evangelist). The upgrade lever is
> the strongest one that exists: a person's own living world, asking to live again.

The anonymous tier's caps (`stamp_quota`, model budgets — `0013 §8` made mechanical in `0011`/`0010`) bound
the blast radius of every free universe: **the safety architecture *is* the free-tier economics.**

## 4. The provisioner — template → world

`provision(template, name, trust_tier)`: tier check at the door → root becky (did:web under `orreth.ai`) →
tiers rendered from profile fragments (completed, clamped for anonymous, validated against
`tier-profile.schema.json`) → platform + template floors published, pulled down the chain → tone and skills
seeded at the apex → roster stamped per field (birth certificates and probation included, `0011`). Dev and
cloud are two renderers of the same artifact (compose / CDK, `0000 §6`); the sim is the third, and it proves
the semantics: **provision(league) yields a living, writable, resolvable, roll-up-able world in one call.**

## 5. Decisions — **all locked by JB, 2026-07-02** (via AskUserQuestion; recorded in `../decisions/`)

1. **Templates (#12): League + Second Brain + Company.** One per funnel stage; Game folded into League; Lab
   honestly gated behind the regulated tier's quorum.
2. **Tone (#13): blank universes default REAL; templates carry their own.** Wild is visible choice, never
   accident; the dial modulates rigor, never floors.
3. **Subscription (#14): fuel + hibernation + BYO-key.** One-time free allotment · hibernate-never-delete ·
   wake by subscription or your own model key · idle hibernation regardless. Bounded spend per user; the
   memory promise intact; conversion powered by attachment to one's own world.

## 6. Contract & simulator (landed with the dive)

`universe-template.schema.json` · simulator `provisioner.py` (provision · ProvisionedUniverse.hibernate ·
the three templates as validated data). **Four new tests, 36/36 passing:** league-provisions-opening-day
(with anonymous caps clamping) · wild-and-REAL-differ-in-rigor-never-safety (identical floors, different
dials) · trust-tier-gates-the-template-door · hibernation-pauses-the-dream-never-the-memory.

---

*With this dive, the sequence 0000–0013 is fully drafted and **every decision in the ledger is locked** —
the design phase closes. What begins now is the build phase, in the order 0000 blessed: the Rust plane
(`orrethd`) against the conformance suite these 36 tests seed, the pane (`0008`) that makes the window real,
and the League — clock, scoreboard, door, draft, law, and template all waiting for it. Pick a template.
Name your world. That was always the point.* 🥃
