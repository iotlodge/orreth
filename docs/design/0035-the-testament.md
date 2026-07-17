# 0035 — The Testament (the universe that outlives its human)

*Design draft — proposed by Fable 5 (design owner), commissioned by JB's 2026-07-15
lock in 0034 §8: survivorship gets its own dive, for gravity. The 0034 §4 slate
(seal · succession · crypto-shred · per-domain mix) is the starting ground, studied
here against 0012's quorum thinking and 0026's erasure doors. **All five §8
decisions locked by JB 2026-07-17** (via AskUserQuestion, deliberately, every one
on the recommended path) — the spoonfuls may begin.*

---

## Why this dive

A continuity universe exists because a human's biological recall is failing. It
follows — and the design must say it plainly — that this universe will likely
outlive its human. Every other dive answers *what does the universe do while its
human lives?* This one answers the other question. It is the gravest lock in the
canon because it is the only one where the root authority — the origin of every
Objective (0030) — cannot be consulted at execution time. The whole design
reduces to one move: **let the human answer while they can, on the record, and
let nothing else presume to answer for them.**

## 1. The ground already laid — nothing here starts from nothing

| Canon | What it gives mortality |
|---|---|
| 0026 — the split model | consent path (the subject's own word IS the quorum for their own data) vs operational path (humans plural + cooling-off). Death splits identically: **the testament is the consent path, executed late**; everything absent a testament is operational |
| 0026 §3 — the seal | containment at machine speed, reversible, never conflated with destruction |
| 0012 — gates & quorum | silence never approves · bars absolute · cooling-off = approved-but-held, one voice aborts · no break-glass, deliberately |
| 0022 — crypto-shred | the erasure primitive + mandatory projection eviction; bi-temporal close-the-window |
| 0004 — clocks & retention | death is a wall-clock event; legal hold = governed `min: ∞` and it outranks any shred order while it stands |
| 0006 — becky | attenuation-only tokens with validity windows — a pre-signed grant is dormant paper |
| 0009 — fuel | hibernate-never-delete: a sealed legacy universe costs almost nothing to keep forever |
| 0034 — the continuity organs | consent as dynamic state · role bundles (executor joins the vocabulary) · the label canon (the dead get a register of their own, §5/§6) |

## 2. The testament — the human's standing word about the end

0032 made a subscription "the human's standing word" for acquisition. The
testament is the same shape at final stakes: a **config-as-memory record on the
human's own worldline**, class personal-data, sovereign — staged at 0012's gate
while the human lives (arming future consequence IS a consequence), revised as
sibling versions with the head winning, revocable to the last day. It carries:

- **The fate map** — per memory domain (0034's role-bundle domains), one of
  `seal · pass · shred`. The §4 "governed mix" is not a fourth option beside the
  other three — it is *the shape of the record*. One fate for everything is just
  a map with one entry.
- **The roster** — executor and optional witnesses, named as DIDs through becky.
  The executor role bundle exists from 0034 §4's vocabulary but stays
  **dormant** until the passage (§3).
- **The silence window** — how long unresponsive before the universe seals. The
  human tunes their own dead-man clock.
- **The disclosure map** — who may read what in legacy. This is the dead's
  consent, fixed at close; §5's floor law governs it thereafter.
- **Pre-signed succession grants** — becky-chained attenuations whose validity
  window opens only when the attested-death record exists. Dormant paper,
  springing at attestation; never a private key, never the identity (§4).

## 3. The passage — a state machine where silence can only contain

> **The dead-man reconciliation.** 0012 §4 is law: *silence never approves.* A
> dead-man protocol that **executes** on absence would be silence approving the
> gravest act in the canon. So silence gets exactly one power — the one 0026 §3
> already grants machine speed: **containment. Silence seals; only attestation
> executes.**

```text
living ──(silence past the window)──▶ UNRESPONSIVE   the seats reach out; the
                                                     absence is staged, loudly
UNRESPONSIVE ──(still silent)───────▶ SEALED         machine-speed, reversible;
                                                     every entitled party told
SEALED ──(the human returns)────────▶ living         one heartbeat unseals;
                                                     nothing was lost
SEALED ──(executor stages evidence)─▶ ATTESTED       death certificate as a 0029
                                                     artifact + attestations;
                                                     quorum per §8; approval
                                                     starts the cooling-off
ATTESTED ──(cooling-off, no voice)──▶ EXECUTED       the fate map walks, domain
                                                     by domain, on the record
EXECUTED ───────────────────────────▶ LEGACY         standing state: the sealed
                                                     remainder + the survivors'
                                                     door (§6)
```

- Detection **stages, never decides** (0013 §3): a caregiver's report, the
  Mirror noticing absence, the silence timer — all of them stage; none executes.
- Cooling-off on ATTESTED is deliberate probate: **any entitled voice aborts —
  and the loudest abort is a heartbeat.** It takes quorum to bury a universe and
  one pulse to save it.
- A wrong death is survivable **by construction**: before EXECUTED nothing
  irreversible has happened; the seal lifts, and the record shows the universe
  held the door.
- Incapacity is a named neighbor, not this dive: the guardian bundle, consent
  postures, and safer modes (0034 §4/sp2) already govern the living-but-unable.
  The SEALED state doubles as their containment; only death crosses further.

## 4. The four fates, studied

**Seal — read-only legacy.** 0026's seal made a *standing* state (the Vaulted
Brain already names sealed classes; this is the whole universe wearing one).
Reads pass through the survivors' door only, per the disclosure map. Economics
are 0009's: a legacy universe doesn't dream, it *keeps* — hibernated, sealed,
nearly free, forever. The default fate, and the fate of everything a testament
leaves unnamed.

**Pass — succession.** What passes is **custody, never identity.** The worldline
closes at EXECUTED (0022's bi-temporal close): the sovereign `trusted` class
dies with its sovereign — no new record may ever again enter as the dead's
assertion, and the portrait freezes. The successor receives: read per the
disclosure map · stewardship of the legacy universe (fuel, floors,
tighten-only) · **graft rights** — copying granted records into their own
universe with lineage (`derived_from` crossing universes, provenance
`inherited`; 0002's portability scope, finally exercised). Continuation is by
graft, not possession: the child carries the parent's memory forward inside
their own living universe; the parent's universe stays whole, closed, provable.

**Shred — crypto-erasure.** Two honest forms, only one of which requires a
detector to be right about death:

- **Governed shred:** the testament orders it; ATTESTED + cooling-off; the walk
  goes through 0026's doors — `/tombstone`, projection eviction, stubs survive.
  The estate can prove what it destroyed.
- **Mathematical shred — the vault that dies with its keeper:** Vaulted-Brain
  domains under user-held keys with **no escrow**, elected in the testament. No
  trigger, no quorum, no detector: the keys die with the human and the
  ciphertext is a gravestone. This is the only defensible "dead-man
  crypto-shred" — enforced by mathematics, not by a machine deciding someone is
  dead.

**The mix** is §2's fate map — the record's shape, not a separate option:
journals shred, identity and relationship claims pass to the family, the care
record seals for whoever must one day prove the care was good.

## 5. What never happens (design-owner laws; JB may veto)

- **The archive speaks about, never as.** First person dies with the person.
  The label canon (0034 §3) grows a legacy register: *"On May 12th, 2024, she
  wrote…"* — past tense, receipts shown, never "I remember."
- **Silence never destroys.** It contains — reversibly, loudly. (0012 §4,
  applied to mortality.)
- **Detection stages, never decides.** No organ, timer, or model ever concludes
  death. Humans attest; the universe holds the door.
- **The testament is a floor.** Heirs may narrow the disclosure map, never
  widen it. The dead's consent is not renegotiable. (Tighten-only, applied to
  inheritance.)
- **A closed worldline never reopens.** No resurrection; a wrong death caught
  in cooling-off means the worldline never closed at all.
- **Stubs survive the shred** (0026): the universe can prove it once knew, and
  chose.
- **Legal hold outranks the shred order while it stands** (0004): the order
  queues behind the hold; it does not die.
- **The Mirror never assesses the dead.** Assessment serves a living
  relationship; in legacy it stops, and its ledger seals with the rest.
- **No break-glass into a sealed universe.** The disclosure map plus 0012's
  operational path are the only doors; grief is not an entitlement.

## 6. The survivors' door

Legacy is not a tomb with the lights cut. The parlor stays open to the entitled:
a widow asks, the librarian answers in the legacy register — about, never as,
with receipts, through the same label canon that kept the living honest. And the
Brain Glass of a legacy universe renders the quietest state in the canon: the
full anatomy in glass, embers cooled to a constellation of what was kept, no
fire — **the shape of a mind, held.** The two-brains contrast gains its third:
the enterprise burns, the continuity mind breathes, the legacy keeps.

## 7. The spoonfuls (proposed — none begins before §8 locks)

| # | Spoonful | Nature |
|---|---|---|
| 1 | **The testament record** — `continuity.py` organs: fate map · roster · silence window · disclosure map; sibling revisions, head wins; becky's card doors (staging at the gate; revocation acts now); pure gates `fate_of` / `may_attest` / `may_read_legacy` | ✅ landed 2026-07-17 — `continuity.py` grows the §2 organs with every §8 lock refused at mint, loudly (unknown fate by name · unescrowed-only-shreds · pass/shred need an executor · the executor never witnesses their own attestation) · pure gates: `fate_of` (no testament, a revoked one, and the unnamed all SEAL — locks 1·2) · `shred_method` (governed vs key-mortality — lock 5) · `attestation_met` (quorum 2: executor + evidence + witness-or-registry — lock 3) · `may_read_legacy`/`narrowed_ok` (heirs narrow, never widen — lock 4) · becky's card gains the doors: the standing word STAGES verbatim with its fates readable, a word that must execute refuses without an executor, revocation acts NOW, the ledger speaks the head or the honest default · wire: kind `testament` staged→approved mints becky-signed on one worldline / declined records the choice · glass tgate "let it stand" · **proven as a human on u:demo**: spoke the word at becky's card → the gate held it ("silence may only contain; only attested death executes") → let it stand → asked for the ledger and the record answered: "your testament stands … revocable to your last day." 5 tests, 176/176 |
| 2 | **The passage** — the worker's silence watch (reach-out → seal, reversible, loud) · the heartbeat unseal · the attestation door (0029 evidence artifact + entitled attestations → staged escalation, quorum + cooling-off per the lock) | worker + wire |
| 3 | **The execution walks** — per domain: seal-standing · succession grant springs + graft-with-lineage · governed shred through 0026's doors · the worldline close, the portrait frozen | the gravest code |
| 4 | **The survivors' door** — the legacy register in the label canon · parlor read-only for the entitled · the legacy Brain Glass (the constellation) · hibernated economics | glass + canon |

## 8. Decisions — **all five locked by JB, 2026-07-17** (via AskUserQuestion; every lock on the recommended path)

1. **Silence's one power → seal only.** Reversible containment; execution
   always requires attestation. 0012 §4 stays whole at final stakes; a
   machine never decides a death.
2. **The default absent a testament → seal forever, hibernated.** The least
   irreversible act; assumes nothing about the unspoken. An executor-shaped
   petition may later ride the operational path (0026 §2: humans plural,
   cooling-off).
3. **The attestation bar → quorum 2, then cooling-off.** Executor + evidence
   artifact + one named witness (or registry evidence standing as the second
   voice). 0012's spirit at final stakes, reachable for a small family; any
   entitled voice aborts during the window.
4. **Succession passes custody, never identity.** The worldline closes, the
   portrait freezes, heirs narrow and never widen the disclosure map;
   continuation is by graft-with-lineage into the heir's own living universe.
   Full root transfer rejected by name: impersonation by inheritance.
5. **The vault's mortality → per-domain election.** The testament chooses per
   domain: escrowed (all governed fates available) vs unescrowed (mathematical
   shred — no detector needs to be right). The continuity template defaults
   escrowed — its human is the person most likely to lose a passphrase in
   life; the Vaulted Brain offers both.

---

*Every universe in the canon answers to its human. This is the one place the
canon must answer for them — and it refuses to, until they have spoken. A
testament is the last standing word: the universe holds it, holds the door, and
when the day comes, keeps — passes — or forgets, exactly as told, and can prove
which.* 🥂
