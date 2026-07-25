# 0042 — The Deed

*Design draft — proposed by Fable 5 (design owner), seeded by the 2026-07-25 outside
review (`../outside/ORRETH_CHRONICLE_MIND_CANON_MACHINE.md`, loop 2 — "consequence
and world reconciliation"), triaged and locked for this slot by JB the same day.
Companions: `0005` (nothing grades its own yardstick — the instinct this dive grows
into the world), `0037` (allen's plan → deploy → observe → reconcile — the first
walker of the shape), `0041` (the Epoch — which machine attempted it), `0039` (the
Canon the effect classes live in), `0012` (gates — authorization and closure wait at
them), `0035` (silence law — timeout postures are the fates' vocabulary).*

---

## The question this dive answers

> **"Did the world actually change — and who besides the actor says so?"**

Producing an answer and changing the world are categorically different events. A
RunRecord saying "success" proves a mind finished a thought; it does not prove an
email sent, a stack deployed, a post published, a payment landed. The actor may be
mistaken, the target may acknowledge without applying, the effect may land twice, a
later process may undo it. Our own constitution already refuses self-graded
yardsticks inside the universe (0005: scribe-authored, `author ≠ agent`); the estate
already refuses self-graded deployments (0037: allen observes and SIGNS the
workforce's work — nothing self-attests). This dive makes that physics common to
**every** consequence the universe pushes into the world: infrastructure, publishing,
and everything a future tool gateway touches.

**The invariant, in one line: no external consequence is complete merely because its
executor says it is.**

## 1. The effect class — a Canon asset

Every kind of world-touching act belongs to an **effect class**, and an effect class
is a versioned Canon asset (0039's shelf, 0031's lanes, the gates' law), declaring:

| Field | What it holds |
|---|---|
| `target` | what part of the world this class touches, and its scope |
| `preconditions` / `postconditions` | what must hold before; what the world should look like after |
| `reversibility` | reversible · compensable · irreversible |
| `idempotency` | the duplicate-detection key and the retry posture |
| `observer` | which seat independently observes, and by what read-only door |
| `observation_delay` | how long the world gets to settle before observation counts |
| `timeout_posture` | what silence means, and when it becomes containment (0035) |
| `compensation` | the pre-declared safe reversal or containment for this class |
| `blast_radius` | the maximum authorized extent of one deed |
| `ceremony` | the tier — how much record family one deed of this class must carry (§3) |

Classes change only through the standing lanes — sibling proposals, evidence,
human gates. The law that governs change (0041) governs these too.

## 2. The record family — a deed is a walkable chain

One deed of a consequential class writes this family, each record signed,
content-addressed, derived from its predecessor:

**intent → authorization → attempt → external receipt → independent observation →
reconciliation → closure (or compensation → observation again…)**

- **intent** names the change, the Objective it serves (0030 — a human at the
  origin), and the effect class it claims;
- **authorization** is the gate record — authority, budget, validity window;
- **attempt** is what the actuator did, with which inputs and manifests;
- **receipt** is what the target system acknowledged — kept verbatim, trusted never;
- **observation** is what a *different seat* subsequently found true through a
  read-only door — `author ≠ attempt.author`, enforced the way scribes are (0005);
- **reconciliation** is expected-vs-observed, and it is diff-is-news (0037 §4);
- **closure** carries the evidence-backed verdict *and the remaining uncertainty,
  named honestly*; **compensation** is itself a deed of a declared class — the
  recursion is priced, never free.

**The clasp with 0041**: every attempt cites the standing CanonEpoch of its floor.
The auditor's two questions — *which machine were you?* and *what did you do to the
world?* — answer each other in one walk.

## 3. Ceremony priced by class

The universe must not drown in receipts for trivialities. Ceremony is a **dial the
class wears**, not a virtue applied uniformly:

| Tier | What one deed carries | For |
|---|---|---|
| T0 · whisper | attempt noted in the rollup; no family | reads, idempotent internal writes |
| T1 · receipt | intent + attempt + receipt, collapsed into one record | low-stakes reversible effects |
| T2 · witnessed | the full family, observation by a distinct seat | consequential effects (deploys, publishes) |
| T3 · sworn | full family + pre-declared compensation verified at authorization + human closure at the gate | irreversible or wide-blast effects |

A class's tier is Canon: raising or lowering ceremony is itself a gated change with
evidence. The pricing floor is proven both directions — sp1 ships a T0 class to show
the whisper stays a whisper.

## 4. The observer — separated today, independent someday

The observation seat is per-domain, read-only, and never the actuator's seat:
allen's describe-stack observers watch estate deeds (0037 already grants them);
a distinct floor seat fetches back what publishing claims to have published.

**Honest boundary (named in 0041 §7, still true here):** on one laptop, under one
process supervisor, observation is *separated bookkeeping*, not *adversarial
independence*. The schema leaves the seat pluggable — a prod observer on other
metal, a peer universe through 0013's descendants — and we say plainly which one we
are running.

## 5. Reconciliation, compensation, and the gate

- **postcondition holds** → closure, on the record; the rollup notes coverage.
- **uncertain or wrong** → a **staged finding at the human's gate** carrying the
  diff and the class's pre-declared compensation as the easiest yes — the 0041
  drift-card pattern, extended to the world. Compensation *stages*; a human signs;
  the compensating deed walks the same family it compensates.
- **silence** → the class's timeout posture, on the clock (0035): unobserved is a
  state, never assumed success.
- The only ceremony-free retry is the idempotent re-attempt inside the attempt's own
  validity window, under the same idempotency key — dedup is the class's promise.

## 6. Honest boundaries

- No `contracts/v0` cut in this dive — deed records ride as tagged MemoryRecords
  (the 0041 pattern); the hard schema awaits its own rule-9 gate.
- The family covers effects walked through the standard doors (allen's toolroom,
  the publish door); a rogue code path bypassing them is a code-review problem, and
  we say so.
- Dev observation is separated, not independent (§4). The glass will say which.

## 7. Decisions — LOCKED 2026-07-25 (JB, via AskUserQuestion; all recommended paths)

1. **The v1 class roster — LOCKED**: three classes — `estate-apply` (witnessed/sworn)
   · `outbound-publish` (witnessed) · a T0 whisper class — the ceremony dial proven
   BOTH directions: heavy deeds testify, trivial deeds stay silent.
2. **The ceremony ladder — LOCKED**: four tiers, T0–T3 as §3 draws them. Class
   changes are dial moves, not redesigns.
3. **The observer's seat — LOCKED**: per-domain seats — allen's read-only observers
   for estate deeds, a distinct floor seat fetch-backs publishes. No new organ;
   `author ≠ actor` held at seat level; the prod path pluggable, noted not built.
4. **Compensation authority — LOCKED**: nothing compensates without a fresh human
   word — every compensation stages as the easiest yes at the gate (0041's refusal,
   mirrored). Only the idempotent re-attempt inside the attempt's own validity
   window runs free.

*(Mechanism, design owner's call, noted not asked: deed records as tagged
MemoryRecords; per-floor deed staging through the existing request queue and gate
idiom; every attempt citing its floor's standing epoch.)*

## 8. The spoonfuls (proposed — JB may re-cut)

| # | Spoonful | Nature |
|---|---|---|
| 1 | **The shelf and the family** — effect classes as Canon assets; the record family writable and walkable; a T0 class proves the whisper floor | the world gets a grammar |
| 2 | **allen swears his deeds** — the estate apply emits the full family; planned-vs-deployed reconciliation (0037 §4) becomes the reference reconciliation; closure at the gate | the first walker formalized |
| 3 | **The second class: outbound publishing** — a real publish, the platform's receipt kept verbatim, fetch-back observation by a distinct seat, reconciliation, closure; the failure path proven too | the actor is not the sole witness |
| 4 | **Compensation and the priced ceremony** — a wrong reconciliation walks compensation → re-observation at the gate; the glass wears deeds; T0 stays quiet while T2 testifies | the recursion priced, the gate honored |

---

*Forty-one dives taught the universe to remember, argue, forget, teach, and name its
own machine. This one teaches it the oldest law of consequence: a deed is not done
because the doer says so — it is done when a witness who isn't the doer walks the
world and finds it changed.* 🥂
