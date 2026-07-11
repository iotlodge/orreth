# 0023 — The Librarian (one mind, many seats, no levers)

*Design draft — proposed by Fable 5 (design owner), from the Universe-Brain session
(2026-07-10, `../vision/the-universe-brain.md` §3–§4). The organ 0020 §4 reserved a seat
for, incarnated. Nearly every governing decision was **pre-locked in that session** (R1
identity · R2 opt-out · no-change · vigil-watched · the JB locks of 2026-07-10); this
dive mechanizes them. Builds on 0014 (the knowledge loop — the librarian's existing
duties stay her duties), 0020 (the parlor — her front door), and 0022 (the Memory
Construct — the brain she is the face of).*

---

## Why this is a keystone

JB's law: **the Librarian is the Human of the Universe** — the most knowledgeable
resident at any floor, and the only door through which a human's questions reach the
data. Humans never input or extract; the Librarian receives the ask, fetches under her
own authority, and answers on the record. She is "the AI in the umbrella": the
general-intelligence surface every other capability is reached through. Get her identity,
her limits, and her federation protocol right, and the interoperability law (0020 §0)
scales from one floor to a world-spread universe.

---

## 1. One mind, many seats — the lineage (JB lock, 2026-07-10)

- **One Librarian root identity**, chained to the universe root via becky (0006), with a
  **scope-bound did:key per seat** — one seat per floor, issued at floor provisioning
  with the resident roster (a layer is born with its staff, 0006 §2). **Lineage proves
  sameness**: the chain, not a shared key, is what makes every seat *the same
  Librarian*.
- **Per-seat blast radius**: a compromised seat loses one floor; revocation severs one
  nerve (the nervous-system rule) — the seat's partition goes cold, archived, never
  erased. The mind survives its wounded limb.
- The existing wire identity (`~/.orreth/residents/librarian.seed`, one key) becomes the
  **field-seat** key; the root and sibling seats issue from becky as floors provision.
  Migration is additive — no record rewrites.

## 2. All knowledge, zero levers — the capability shape

- **The read side is the widest token in the universe**: at her own seat, every class
  and partition; across seats, the **non-refusable pull** (below). This is exactly why
  the write side is nearly empty.
- **"No change" means no operational change.** Her CapabilityToken carries `retrieve`
  (wide) and `write` scoped to **her own duties' record kinds only**: knowledge
  admission (0014 gather, quarantined at 0.0000), corroboration/recall versions, profile
  stewardship (the Human Profile dive), markers she is entitled to place (0024), and her
  parlor answers. **No `govern`, no `transfer`, no `issue`, no standard-authoring** —
  ever. A human's change request rides *through* her to the owning resident (becky ·
  charlotte · ada · steward) as a queue entry she stages but cannot decide.
- **vigil watches the Librarian** (JB lock): every read she makes — above all the
  cross-seat pulls — is a signed access record under the warden's eye. The all-seeing
  organ is the most-watched thing in the universe. The pairing *is* the governed floor:
  total visibility is safe because she can deliver nothing alone.

## 3. The self-dialog — Librarian-to-Librarian federation

The Universe-seat Librarian sees ALL data regardless of opt-in/opt-out (JB, second
pass). Opt-out changes **residency and mechanism**, never access:

- **Opted-in scopes**: their distillations rose; the asking seat answers from its own
  floor's memory (0022 retrieval, meaning axis included).
- **Opted-out or time-bound scopes**: the asking seat engages **itself at the seat that
  holds the data**. On the wire this is a queue entry at the target floor —

  ```json
  {"kind": "librarian-ask", "from_seat": "u:demo", "session": "ld-x1",
   "text": "<the sub-question>", "budget": {...}, "token": {...}}
  ```

  — authored by the asking seat's DID, resolved by the target seat fetching under **its
  own** capability and answering with a resident-signed record at its own floor. **A
  floor can never refuse its Librarian** (JB lock): the ask-handling is a floor-class
  obligation, tighten-only, cascaded — but the *boundary is the universe wall*: the
  never-refuse rule stops at the Custodian line; sibling universes and hosted tenants
  stay sealed (0002 §4, 0013).
- **The composed answer at the asking seat** is classed by its sources: any leg that
  crossed an opted-out wall makes the composition **`derived-from-opted-out`** —
  short-TTL at the asking seat (a TierProfile dial, default P7D), **excluded from
  distillation cohorts**, so opted-out substance never accretes at the apex through
  Q&A. The *access record* of the ask is permanent; the content evaporates (JB lock:
  leak-by-synthesis, killed).
- **Every answer carries its horizon**: seats not yet heard from ride `remainder`
  (0002); a fused answer never masquerades as complete. The light-cone stays honest.

## 4. The exchange block — opt-in/out as a TierProfile dial

```
exchange {
  <record_class>: "up" | "hold"       # per class: rolls up · stays home (default: up)
}
```

- **Opt-out is future-flow only** (JB lock): already-risen records stay; the apex's
  past never rewrites. A true pull-back is a governed tombstone action, never a toggle.
- **NEVER opt-out-able** (floors, not dials): cost, tokens, performance, operational
  and security events — the meter and vigil's signals always flow up and escalate.
  Two lanes, structurally distinct: the mandatory ops/security lane and the optional
  experiential lane.
- **Console build item**: the opt-in/out configuration UI per ecosystem/field — the
  exchange block rendered as switches, changes riding the lane-routed Standards flow
  (0008): experiential toggles auto-apply signed; anything touching a floor refuses.

## 5. The query planner — the becky-shaped duality, routed

The Librarian's answer path classifies the ask and routes (adaptive retrieval —
industry's pattern, our jurisdiction):

1. **Deterministic first** (agent asks, simple lookups): tag/hash/time queries against
   the floor — instant, free, grounded.
2. **Meaning queries** (0022 §4): hybrid semantic × lexical × lineage × time ×
   trust-state, trust-weighted rerank, `recalled` ranks dead.
3. **Cross-seat** (§3): sub-questions fan to the seats that hold the data; fusion at
   the asking seat with dedup by ContentHash and per-seat provenance.
4. **Acquisition** (nothing held anywhere): the ask becomes a gather — the 0014 loop,
   admitted quarantined, the floor knowledge-request path (need-driven CRAG).

**The faithfulness gate on every composed answer**: no assertion without a ContentHash
citation. Grounded always; **voiced** (one governed, metered thought under her seat's
DID) only when the floor is fueled — 0020 §4 unchanged, now with citations mandatory.

## 6. The front door — the parlor face grows, the core does not

- Her calling card (0020 §2) stays the contract; the asks grow: "ask the universe…"
  (routes the planner), "collect knowledge on…" (gather), "update my profile…"
  (0024). New flows arrive as card data — zero glass changes.
- The full-screen **workspace** (spoonful 7) is where her rich answers render — charts,
  documents, the citations expandable to their records in the Window.

## 7. Mechanism — the build phases this dive unlocks

1. **Seats + the no-levers token** ✅ *landed 2026-07-10 (7ed945d)*: librarian root +
   per-floor did:key seats, becky-chained; field seed grandfathered; root-signed seat
   charter on the record; Shipyard-grown floors seat themselves on discovery.
2. **The self-dialog on the wire** ✅ *landed 2026-07-10 (48d2112)*: `librarian-ask`
   legs across every floor, async composition with per-seat provenance + honest
   horizon; **lineage-death enforced** — a recalled claim's older versions never
   speak. *(The `derived-from-opted-out` synthesis class activates when an exchange
   opt-out first exists on a live floor — the wire's next step.)*
3. **The exchange block** ✅ *reference landed 2026-07-10*: TierProfile `exchange`
   schema delta (rule 9, covered by this dive's blessing) + sim distillation
   enforcement — a `hold` class distills HOME and never rides up
   (`test_exchange_hold_stays_home`). *Remaining on the build ledger: the wire
   steward honoring the dial + the Console opt-in/out toggles.*
4. **Planner v1** ✅ *landed 2026-07-10*: deterministic routing
   (local → cross-seat → gather), citations at answer assembly (each seat's segment
   wears its refs); the meaning axis arrives with 0022 Phase 2.

## 8. Honest boundaries

- **The planner is rules before it is cognition** — v1 routes deterministically; the
  becky-shaped LLM synthesis stays optional polish over mandatory grounded answers.
- **Cross-seat latency is real**: a self-dialog across a world-spread universe is
  seconds, not milliseconds; the parlor thread shows the legs as they land (the
  Console's amber-pending grammar, reused).
- **The non-refusable pull needs its quotas**: a floor must answer its Librarian, but
  budgets still bound each ask (budget-miss ≡ authz-miss to *outsiders*; to the
  Librarian's own seats, a budget-miss is visible and re-askable — she is inside the
  trust boundary, and vigil sees every retry).
- **Seat migration touches nothing sacred**: no orreth-node/store/crypto changes; the
  queue and tokens carry it.

## 9. Decisions

**Pre-locked by JB (2026-07-10, the Universe-Brain session — recorded in
`../decisions/`):** one lineage, per-seat keys (R1) · Universe seat sees all; opt-out =
residency, pull non-refusable, intra-universe only · opt-out future-flow only +
`derived-from-opted-out` ephemeral class (R2) · Librarian has no change capability ·
vigil watches her every read.

**Closed by the design owner (this dive; JB may veto):** the `librarian-ask` queue kind
rides the existing request queue (no new doors — the 0020 precedent) · the exchange
block shape (§4) and its default P7D synthesis TTL · the planner's 1→4 fallthrough
order · the field seed grandfathered as the field seat · answer citations mandatory at
assembly (the faithfulness gate lands here, not in the plane).

---

*She knows everything and can change nothing; she is one mind wearing as many seats as
the universe has floors; and when she cannot see, she asks herself — on the record,
under the warden's eye, with every claim wearing its receipt.* 🥂
