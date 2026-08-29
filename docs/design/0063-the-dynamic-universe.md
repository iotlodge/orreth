# 0063 — The Dynamic Universe

*Reserved 2026-08-27 from JB's seed; draft opened 2026-08-28; all four
locks landed by JB's hand the same morning.*
***Status: PLANNED — locked, build not yet opened.***

## 1. JB's seed, verbatim (2026-08-27)

> "do add a dive for orreth to address Dynamic attributes/settings of the
> universe (I suspect there's a large dive for this one and will need
> planning). We will need a way for Humans to tune the resident and universe
> values that are likely hard coded or in config files now."

## 2. The problem — the machine's words left the code; its numbers never did

0050 taught the machine to keep its **sentences** on the shelf: governed,
versioned, hash-named, tunable at the gates. Its **numbers** never learned
the same trick. Today the universe's whole temperament — how often it
breathes, what it may spend, how long it remembers, when it gives up —
lives in three ungoverned places:

- **Python constants** in the worker and the sim (`BEAT_EVERY`, memo TTLs,
  probation lengths, throttles — the recon appendix below inventories them);
- **35 `ORRETH_*` env defaults** (`ASSAY_EVERY`, `SEARCH_DAILY`,
  `FLOOR_CAPACITY`, `MIRROR_EVERY`, `BELL_COOLDOWN_S`, …) — invisible to the
  glass, unversioned, no lineage, changed only by editing a file and
  restarting the rig;
- **Contract fields** only a release (or a rule-9 word) can move.

A human who wants the mirror hourly instead of its hardcoded cadence must
edit code. That is the exact wound 0050 closed for words.

**The exhibit is two adjacent lines** — `console_worker.py:9024–9025`:

```python
OBS = {"dial": _dial_load() or os.environ.get("ORRETH_OBS_DIAL", "glance")}
ASSAY_EVERY = int(os.environ.get("ORRETH_ASSAY_EVERY", "300"))
```

Line one is the future: the 0043 observability dial — durable word in the
nest (`dial.json`), env as **genesis default only**, turned through a
governed request, surviving restarts. Line two is the past: a cadence
nobody can see or turn. **0063 makes line one the law of every line two.**

Prior art that already walked pieces of this road, to be reconciled whole:
the 0043 dial (the one governed value that exists) · the 0058 fuel clause
(`budget.renew_days` — the one number that left the code by JB's rule-9
word, and it carried its own bound: `minimum: 0`) · 0059 allocations
(subject → floor → universe, most specific wins) · the machine-task cadence
editor (a re-staged sibling through the gate = the editing idiom) · the
warden's policy list (0059 policy-as-craft — the first comma-separated
VALUES on the speech shelf).

**The sweep's measure (2026-08-28 recon, Appendix A): ~165 dials** — 39
env-backed, ~90 bare literals, ~12 Rust-side, ~9 glass timers, ~15 in
profile JSON — and, more telling than the count, **five different tuning
mechanisms already in production** that disagree about who owns a number:

1. env vars read at boot (operator-tunable, restart required, invisible);
2. bare code literals (release-only, some repeated — the recall window
   `timedelta(days=365)` appears at TWENTY sites);
3. profile JSON the plane already reads (`backend/plane/profiles/*.json` —
   policy outside the code, but hardcoded a SECOND time in the
   world-minting path, so editing it changes existing floors and not
   future ones);
4. **shelf craft through the 0050 door — already prod-tunable by a human**;
5. the improver's `NUDGE_KEYS` — **the machine already tunes four of its
   own dials autonomously** (`max_cycles`, `max_obs`, `ladder`,
   `success_floor`).

The asymmetry is the dive's whole thesis: **a desk's *words* can be
retuned by a human at 2 a.m., but its *holding period* needs a release.**
And subscription cadence is the proof the road works — the "every N beats"
of a study line already arrives from the human's own sentence at the
parlor, parsed and clamped; 0063 generalizes that win.

## 3. The shape (proposed, not locked)

**A dial is a governed value: its shape declared in code, its value living
on the shelf.**

1. **The declaration is firmware.** Code declares each dial's name, type,
   unit, bounds, default, home scope, effect horizon, and razor side. The
   dial's *shape* belongs to the machine — changing what a dial *is* is a
   release. Genesis plants v1 values from the declarations (the 0045/0050
   planting idiom: the shelf is seeded by the code, then owned by the gates).
2. **The value is purpose.** The current value is a shelf record —
   versioned, hash-named, lineage kept — and changes through the same
   one-motion craft-edit door as a sentence: staged at the gate wearing its
   blast radius, landed by the human's word, the old version standing
   behind it. Cancel/revert is first-class (rule 11). And the shelf keeps
   **two clearly separate drawers** (L1's condition): dials wear their own
   `dial-*` name family and category — machine operating VALUES, never
   interleaved with the NLP craft (sentences, prompts, personas) that
   steers minds.
3. **Bounds are law.** The gate refuses a value outside the declaration's
   bounds — a human may not set `BEAT_EVERY` to 0.01s and melt the rig; the
   refusal says the bounds and why. The card states blast radius in plain
   speech (the 0058 idiom: "leaned on by …").
4. **Reading is memoized.** Organs read dials through ONE accessor wearing
   the memo + warm-loop pattern (the performance law — a dial read on every
   beat must not touch the shelf on every beat). A turn takes effect at the
   next warm cycle, and the accessor's card confesses the horizon honestly
   ("takes hold within a minute" / "at next worker boot").
5. **The scope ladder.** Subject → floor → universe, most specific wins
   (0059's allocation law, reused verbatim). A universe dial may carry
   per-floor or per-resident overrides where its declaration allows it.
6. **Env demotes to genesis.** Every `ORRETH_*` dial becomes the *first*
   value on a fresh rig, never the standing one. Three families never
   become dials: **secrets** (keys live in env and process only — the 0059
   env-secrets law), **identity** (`ORRETH_ROOT_PUB`, `ORRETH_VERSION` —
   these are the machine's name, not its temperament), and **wiring**
   (`ORRETH_MODE`, embed URL/port — the rig's body, which belongs to the
   infra lane's story, not the dial shelf). The sweep found no
   `.env.example` despite `.gitignore` whitelisting one — 0063 creates it
   as the honest catalogue of what stays env-side.
7. **The clamp is the contract.** The template already stands twice in the
   machine: a scheduled ask's `every_days` arrives *from the human's own
   request record* and firmware clamps it `max(1, min(90, …))`; the
   witness-silence window is env-tunable but the plane refuses below
   `.max(90)`. **The human tunes within a floor the firmware refuses to go
   below** — every dial declaration carries that floor, and the gate speaks
   it when it refuses.
8. **A dial carries its why.** The fuel-estimate floor's comment — *"the
   wound's own number, 419, must fall on the drained side of this line"* —
   is a value that remembers the incident that chose it. A dial turn
   records value AND reasoning; lineage without the why is a number with
   amnesia.
9. **The human's word is the machine's ceiling.** Where the improver
   already nudges a dial autonomously, the human's turned value becomes the
   BOUND the improver tunes *within* — the machine optimizes inside the
   human's word, never over it (the 0057 rhyme: authority lives where the
   subject lives). *(Lock L3 confirms or reshapes this.)*
10. **The plane tunes through the profile, never through its code.** The
    Rust side already reads policy from `backend/plane/profiles/*.json` and
    env; plane-side dials flow through the profile the plane already
    trusts. The core crates go untouched — rule 9 never even wakes.

## 4. The razor applied (the taxonomy law, extended to numbers)

*Prod-changeable = purpose; release-required = firmware* — already enforced
in `on_craft_edit`; the dial shelf rides the same gate.

- **PURPOSE (prod-tunable through the gates, ~85 rows):** organ cadences,
  spend ceilings and budgets, retention windows and tier profiles, lease
  and fuel terms, floor capacity, bell cooldowns, throttles, judgment
  bars (calibration min-n, confession floors), the desk's holding period,
  quinn's walk cadence — and `KINDRANK`, the Inbox's gravest-first
  ordering: not a number but pure policy in a code-literal costume
  ("which grievance reaches me first" is the definition of a human's call).
- **FIRMWARE (release-only, ~60 rows):** the substrate's pulse
  (`BEAT_EVERY`, the queue tick), memo/cache TTLs (cache-coherency is
  debugging, not governing — this family is *deliberately excluded*),
  UI poll timers and walk settle times, refusal shapes, canonical bytes,
  per-intent meter prices — and three constitutional values the sweep
  found already carrying their own locks: `purge.QUORUM` ("destruction
  below this bar is structurally unavailable" — a tunable quorum is no
  quorum), the anonymous-caps table (0013 §8, mechanical), and
  `artifacts.MAX_BYTES` (JB's lock, 2026-07-11). `ATTEST_EVERY` wears an
  inline "locked" — it stays where JB put it.
- **NEVER A DIAL (~20 rows):** secrets, identity, ports/wiring (see §3.6);
  `SILENCE_UNIT` stays an env dev-dial ("a RIG dial for proving the
  machine, never law" — compressing a testament-day belongs to no prod
  human).

Each row of the appendix inventory wears its proposed side; JB's locks may
move rows.

**Defects the sweep found — unify before you dial (sp0's charge):**
`PROBATION_BEATS`, `CANARY_BEATS`, and `EOL_HORIZON_DAYS` are duplicated
across the Python/Rust boundary with no shared source of truth — a
glass-tuned probation would move the sim's copy while the plane keeps
enforcing 3; these stay FIRMWARE until unified (or are formally declared
release-only). The tier-profile values are hardcoded a second time in the
world-minting path (`shipyard.py` / `provisioner.py`) — editing the JSON
changes existing floors, not future ones. The 365-day recall window is a
bare literal at twenty sites — it becomes ONE named constant first, a dial
second; skipping the middle step invites twenty-way drift. And two
cadences (`MONITOR_EVERY`, `CAL_EVERY`) lack even the env escape hatch
their siblings have.

## 5. The rooms — where a human meets a dial

The Commander laws govern: **command-first, ≤2 clicks, edited in place.**

- **In place:** a dial surfaces on the card of the thing it tunes — a
  resident's study cadence on the resident card, a tool's daily ceiling in
  the Farm, the mirror's rhythm in the machine's-tasks room. Edit opens the
  same staged-card flow the machine-task cadence editor proved.
- **One inventory room:** the machine's settings, grouped by organ, every
  row showing value · bounds · scope · last turn's lineage — the glass twin
  of the appendix below, drawn live from the shelf, never from this paper.
- **The Atlas infra lane** (the planned thread, road row 0063): the 🔩 body
  lens — compose spine, shipyard floors, tool bodies, worker + keeper, each
  box beside its governing ledger, glow measured, every box a door. It
  lives in this dive because the dials live in that body: a machine whose
  body is legible is a machine whose numbers can be tuned.

## 6. Spoonfuls (proposed order)

- **sp0 — unify before you dial** — ✅ **LANDED 2026-08-28, the locks'
  own morning**: `RECALL_DAYS = 365` named once beside the beat, twenty
  sites ride it · the shipyard now MINTS FROM THE PROFILES it plants
  (demo-eco/demo-field JSON the source, the old literals demoted to
  fallback — byte-identical today, honest forever) · `EOL_HORIZON_DAYS`
  is one truth (the worker imports the pasture's own) · the
  PROBATION/CANARY twins wear the release-only word on BOTH sides of the
  Python/Rust boundary, each naming the other · the provisioner's twin
  rows named in place. *Honest remainder:* `.env.example` is blocked by
  the operator's own env deny rule (`Read(.env.*)` protects secrets and
  catches the template) — its content stands ready; where it lives is
  JB's word.
- **sp1 — the registry** — ✅ **LANDED 2026-08-28, the same day as its
  locks**: `orreth_sim/dials.py` (declaration = firmware: type, unit,
  bounds, blast, why, horizon; env demoted to genesis), `dial_seed` at
  boot (becky signs the genesis values as `dial-*` assets in their own
  shelf drawer), the ONE memoized accessor `dial_value()` (the
  `sentence()` idiom, 60 s), the three locked dials wired
  (`search-daily`, `assay-ceiling` live at every enforcement and
  confession site; `kindrank` rides the pre-warmed /sentences door and
  the glass literal demoted to genesis fallback, rule-7 parity
  suite-held). **The walk, live:** the first governed turn (6→2) took
  hold in 45 seconds; a 999 head outside [0..100] was refused ALOUD and
  genesis served while the rig kept breathing; the ordering dial put
  questions first in the Inbox and reverted, the sibling chain keeping
  every step. Suite 365. *Honest remainder → sp2: the door is untyped —
  a flawed head may STAND (the read refuses it); sp2 teaches the gate to
  refuse before landing.*
- **sp2 — the gate** — ✅ **LANDED 2026-08-28, hours behind sp1**: the door
  refuses BEFORE landing — `dials.gate_check()` (pure, suite-held)
  validates type and bounds at `on_craft_edit`, a clean turn lands
  CANONICAL ("2" becomes 2), and the refusal TEACHES (bounds, unit,
  governs, blast — the blast-radius card as words). The prod razor learned
  dials are PURPOSE (`dial-*` joins the prod-editable set — a value the
  human cannot change in prod is not a value the human owns). Every
  landed sibling carries `teachings()` in its body — no dial record is a
  bare number with amnesia — and the glass's craft room renders the
  teaching strip (value · unit · bounds · governs · blast · why ·
  horizon) beside the versions. **Proven through the real glass by hand:**
  the dials drawer (`dials · 3`, own category chip), a 999 turn refused
  in the editor with the full teaching and NOTHING landed (v4 stood),
  the clean turn 6→4 landed as v5 wearing its teachings, the accessor
  served it within the horizon, canon restored as v6. Suite 368.
- **sp3 — the ladder** — ✅ **LANDED 2026-08-28, the same day as sp1 and
  sp2**: declarations wear a HOME (`universe` = one word for the rig;
  `ladder` = a floor's own shelf may outrank it, the 0059 resolution),
  the accessor walks floor-shelf → universe-shelf → genesis with every
  rung's refusal confessed, the door refuses a universe dial at a floor's
  gate with the lesson, and a floor's FIRST override lands fresh (no
  local head to chain — the registry is its existence). Two new dials:
  `metabolism-batch` (the ladder's first citizen — a floor's breath is a
  floor's business) and `improver-cycle-cap` (§3.9 PAID: the literal 5
  that capped the improver's self-tuning since 0028 is now the human's
  word, threaded to both nudge sites, sim and live; at the cap, nothing
  proposes — suite-held). **Proven live:** a universe dial refused
  f:prod's door («this dial lives at the universe alone»); f:prod's
  `metabolism-batch: 50` landed on its own shelf and its next breath
  read «the floor's own word (50) outranks the universe» while the
  universe door still served 200 — two truths, most specific wins; the
  improver's ceiling turned 5→3 and back, the machine bounded by the
  human's word both ways. Suite 370. *Per-resident rungs wait for a
  resident-homed enforcement site — named, not faked.*
- **sp4 — the rooms** — ✅ **LANDED 2026-08-28, the day's fourth**: THE
  SETTINGS ROOM lives in the Brain pull beside the machine's tasks —
  "the machine's dials — its operating values: numbers and settings,
  never words" — every dial's LIVE value, unit, bounds, home
  (ladder rows say "any floor — most specific wins"), governs, and a ✎
  door (blast + why + horizon in its title). The `dial_registry` block
  rides the /brain door, drawn from the shelf, never from paper. IN
  PLACE: the Observatory's ceiling line ("…of the ceiling you set")
  grew ✎ TURN IT, and the Farm's ⛽ search-guarded band grew ✎ the
  ceiling — a dial's mention is a door wherever its subject lives.
  `goDial()` is the one door: any mention → the craft room's dials
  drawer with the record open, the editor one click further — the
  Commander's ≤2 clicks held. **Proven in the glass:** the table
  rendered all five live; ✎ from the Brain landed on dial-search-daily
  v6 with the teaching strip; the Observatory line carries its door.
  *En route: a local `dials` variable in compose_brain shadowed the
  module and the /brain door served only an error — caught live, the
  registry re-enters under its own name.* Suite 370.
- **sp5 — the infra lane** — ✅ **LANDED 2026-08-28, the day's fifth**:
  the Atlas grew its fourth lens, **🔩 the body** — the machine's
  physical anatomy as the schematic's basement band. Four families each
  beside the ledger that governs it (the spine — compose.yaml · grown
  floors — floors.json, the worker replants · tool bodies — bodies.json,
  stop rests, start wakes · the host pair — dev.sh + the keeper); the
  FAMILY shape declared in `_atlas_infra`, the members and their glow
  MEASURED (one memo'd `docker ps` + the ledgers the worker already
  reads); the rig-down word renders as the operator's word in red when
  it stands. Every box a door: a hull steps onto its floor (`floorGo`),
  a body opens the Farm, postgres and the keeper open the Brain — where
  the keeper now also stands as a named rhythm. **Proven in the glass:**
  the band rendered 4/4 spine · 17/20 floors · 3/3 bodies · 2/2 host —
  and the three red floors were exactly the down-ledger's own words
  (f:probe's grave, charlene, chad), red by measurement, never
  declaration; e:desk's hull clicked and the console stood on
  u:demo/e:desk. The morning's question — "where's the view that
  correlates infra to Orreth objects?" — now has its glass answer.
  Suite 370.
- **sp6 — the sweep** (the long labor, paced across sessions) —
  **WAVE 1 LANDED 2026-08-28, the day's sixth: THE CADENCE FAMILY.**
  Twelve rhythms left the code in one motion — passage, embed, mirror,
  monitor, improver, epoch, lag-window, metabolism, assay, verify,
  calibration, brain-census — every `_EVERY` constant demoted to genesis
  (env where one existed; `monitor` and `cal` never had one — the gate
  is their first tunability), each declared with bounds [30‥604800],
  blast, and why. **The sweep's own economy came first:** ONE drawer
  read (`_dial_shelf_build` — tags first, bodies only for dial heads,
  memo'd 60 s and pre-warmed) so seventeen dials never cost seventeen
  retrieves. Proven live: twelve planted at boot, and
  `metabolism-every` turned 900→300 — the Brain's own rhythm row read
  «every 300s» within the horizon — then canon restored. **Deliberately
  left:** `ATTEST_EVERY` (JB's inline lock — it stays where he put it)
  and `SILENCE_UNIT` (a dev rig-dial, never prod). Suite 370.
  **WAVE 2 LANDED 2026-08-29: THE MONEY FAMILY** — four dials for the
  numbers that spend: `subscription-cadence-beats` (100) and
  `subscription-budget-calls` (4) — the study lines' defaults, the ask's
  own word always winning — plus `fanout-budget-tokens` (2400) and
  `fanout-min-share` (60), the widest spend lever and the floor beneath
  every seat. The worker's terms string stopped hardcoding «4 call(s)»
  and now speaks the dial. **Proven live end to end:** the dial turned
  4→2, a fresh study line was filed and approved, and its minted terms
  read «every 100 beats · 2 call(s) per delivery» — inheritance from
  the turned dial — then the proof-line was CANCELLED through the
  parlor's own unsubscribe (the Tavily law: no proof-planted spend ever
  left standing) and canon restored. *Honest notes:* `vera.EST_TOKENS`
  turned out to be a sim-only constant, not a live operating value —
  skipped, not swept; the chassis's agent-side `max_tokens` is a named
  horizon (agent-side dials need the supply-line path). **WAVE 3 LANDED 2026-08-29: THE BELL PAIR** — the highest consequence
  per dial in the inventory. `bell-cooldown` (3600 s, floor **300**: the
  least quiet between two rings of the human's REAL inbox) and
  `bell-gate-age` (48 h: how long a card may wait before the bell rings
  once about it). The cooldown's three scattered env reads became one
  dial, and the bell SINGLETON hears the word live — `_bell_service`
  refreshes `cooldown_s` on every service, so a turn never waits for a
  restart. **Proven:** turned 3600→900 and the Observatory's own bell
  view read `cooldown_s: 900` within the horizon; a 60 s turn below the
  floor was REFUSED at the door with the full teaching; canon restored.
  **The walk's own safety, on the record:** `bell-gate-age` was
  deliberately never lowered live — cards weeks old stand at the gate,
  and a lowered age would ring the real inbox once per card; that risk
  is written into the dial's own blast line. The Rust-side witness
  floor (`.max(90)`) stays firmware — it is the clamp pattern's home,
  not a dial. **WAVE 4 LANDED 2026-08-29: LEASES AND FUEL** — five dials for the
  roster's breathing terms: `join-lease-days` (30) · `join-lease-tokens`
  · `lease-renew-days` (1; 0 keeps the old lump posture) ·
  `floor-capacity` (20, **the ladder's second citizen** — a floor may
  declare its own room, paying the seed named the day the roster
  learned to breathe) · `fuel-est-floor` (500, threaded through
  `fuel.posture`/`drain_cards` the improver's way — "the wound's own
  number, 419, must fall on the drained side"). **The two-truths trap
  CURED:** the code said 50000 while the rig ran 400000 by dev.sh's
  env; env now seeds genesis, and the shelf finally shows the standing
  truth — the planted dial reads 400000. **Proven:** 28 dials at boot;
  f:prod's capacity override landed on its own shelf and reverted; a
  −1 renew-days refused at the door with the teaching; the universe's
  word untouched throughout. `ORRETH_DORMANT_DAYS` stays a named
  Rust-side boundary case (release-only in practice). **WAVE 5 LANDED 2026-08-29: THE DESK'S WINDOWS AND THE JUDGMENT BARS**
  — seven dials, and the registry learned **float**, because the bars
  are fractions: `improver-success-floor` (90) · `studio-dark` (90 s) ·
  `schedule-every-default` (7 d — six scattered `or 7` fallbacks became
  one truth) · `cal-min-n` (5) · `cal-bar` (0.4) · `assay-floor-mean`
  (0.55) · `assay-trend-drop` (0.15). The sim's own signatures had
  anticipated their dials — `calibration(min_n=, bar=)` and
  `degradations(floor_mean=, trend_drop=)` were already threaded; the
  worker now passes the human's words. **Proven:** 35 dials at boot;
  the first FLOAT turn (`cal-bar` 0.4→0.25) served within the horizon;
  a 1.5 above the ceiling refused with the teaching; canon restored.
  **Named, not swept:** `ORRETH_DESK_HOLDING_DAYS` is CAPABILITY
  territory — the desk is a packaged purpose, and by the razor its
  numbers belong on the desk's own craft lane (0055), not the kernel
  drawer; `rivals.CONFESSION_FLOOR` and the infotheory bit-costs
  confessed sim-only; the constitutional trio (`purge.QUORUM`,
  `ANON_CAPS`, `MAX_BYTES`) keeps its locks. **Wave owed:**
  retention/tier profiles (A.7, the profile-JSON path) — the sweep's
  last named wave.

## 7. The locks (JB, 2026-08-28)

- **L1 · The home of values: THE CRAFT SHELF — with the separation named.**
  Dials ride 0050's proven machinery (versioning, lineage, hash names, the
  one-motion door). JB's condition, part of the lock: *"the
  attributes/settings separation should be clear in identification and how
  these are machine/kernel/operating values vs NLP to manage agentic
  functions."* So: dials wear their own name family (`dial-*`, the
  `gloss-*` precedent) and their own shelf category with a plain tail
  ("dials — the machine's operating values; numbers and settings, never
  words"), every dial card says plainly that it is a MACHINE OPERATING
  VALUE, and no room ever lists dials interleaved with speech, prompt, or
  persona craft. Words steer minds; dials steer the machine — one shelf,
  two clearly separate drawers.
- **L2 · The razor's default: FIRMWARE UNTIL NAMED.** An unclassified
  value stays release-only; becoming tunable takes a deliberate word.
- **L3 · The machine's own hand: THE HUMAN'S WORD IS THE CEILING.** Where
  the improver nudges a dial, a human-turned value becomes the bound the
  improver optimizes within (§3.9) — self-tuning survives, inside the
  human's word, never over it.
- **L4 · The first walk: `SEARCH_DAILY` + `ASSAY_CEILING` + `KINDRANK`.**
  Two spend ceilings whose display half already stands in the glass, plus
  the Inbox's gravest-first ordering — proving from day one that a dial is
  any tunable VALUE, not just a number.

*Standing recommendation, adopted with the locks:* the effect horizon —
live-read via the memoized accessor, taking hold within ~a minute, the
horizon confessed on the card (never restart-required).

## Appendix A — the dial inventory (recon, 2026-08-28)

*Swept by a read-only recon agent under Fable 5's direction: the worker,
the sim, the capabilities, the agents, the glass, the env surface, and
(read-only, rule-9 respected) the plane's crates. ~165 dials. The
`YARDSTICK_V1` comment at `console_worker.py:11711` is the precedent this
dive copies verbatim: "The set is GENESIS ONLY here: it plants as shelf
craft and JB's red ink is a craft-edit from then on — versioned siblings,
never a code change." All paths repo-relative; the proposed razor side on
each group is the recon's word, moved only by JB's locks.*

### A.1 The beat and the worker's loop clocks

| dial | value | site |
|---|---|---|
| `BEAT_EVERY` | 6 s | `backend/conformance/console_worker.py:148` |
| main-loop tick | `time.sleep(2)` | `console_worker.py:14106` |
| `MISSES_TO_DROP` | 3 | `console_worker.py:149` |
| `FLOORS` | `[4500, 4501, 4502]` | `console_worker.py:144` |
| `JOIN_PORT` | 4502 (argv override) | `console_worker.py:145` |
| `SCOPE` | `u:demo/e:cloud/f:prod` | `console_worker.py:146` |

Blast: mistuning the pulse melts CPU across all floors; `MISSES_TO_DROP`
too low evicts healthy agents, too high lets the dead hold leases.
Razor: `BEAT_EVERY` + tick **FIRMWARE** (the substrate's pulse);
`MISSES_TO_DROP` **PURPOSE** (a policy about tolerance for silence);
ports/`SCOPE` **FIRMWARE/ENV** (topology).

### A.2 Organ cadences — the `_EVERY` family (all PURPOSE)

Identical shape throughout (`if now - _LAST < EVERY: return`) — the
cleanest candidate set for one generalized dial surface.

| dial | value | env | site |
|---|---|---|---|
| `PASSAGE_EVERY` | 60 s | `ORRETH_PASSAGE_EVERY` | `console_worker.py:952` |
| `SILENCE_UNIT` | 86400 s | `ORRETH_SILENCE_UNIT` | `:954` — **dev-only, never prod** |
| `EMBED_EVERY` | 90 s | `ORRETH_EMBED_EVERY` | `:1345` |
| `MIRROR_EVERY` | 600 s | `ORRETH_MIRROR_EVERY` | `:2458` |
| `MONITOR_EVERY` | 600 s | **none — hardcoded** | `:4749` |
| `IMPROVER_EVERY` | 600 s | `ORRETH_IMPROVER_EVERY` | `:5233` |
| `EPOCH_EVERY` | 300 s | `ORRETH_EPOCH_EVERY` | `:6679` |
| `ATTEST_EVERY` | 21600 s | `ORRETH_ATTEST_EVERY` | `:6953` — inline "locked" (JB) |
| `METABOLISM_EVERY` | 900 s | `ORRETH_METABOLISM_EVERY` | `:7220` |
| `METABOLISM_BATCH` | 200 records | `ORRETH_METABOLISM_BATCH` | `:7221` |
| `ASSAY_EVERY` | 300 s | `ORRETH_ASSAY_EVERY` | `:9025` |
| `VERIFY_EVERY` | 3600 s | `ORRETH_VERIFY_EVERY_S` | `:10179` |
| `CAL_EVERY` | 120 s | **none — hardcoded** | `:11094` |
| `BRAIN_CENSUS_EVERY` | 300 s | `ORRETH_BRAIN_CENSUS_EVERY` | `:12548` |
| `LAG_WINDOW` | 900 s | `ORRETH_LAG_WINDOW` | `:6769` |
| scheduled-ask cooldown | 3600 s | none | `:11995` |
| lag-note throttle | 3600 s (1/scope/hr) | none | `:6858` |
| gate-age ring dedup | 86400 s | none | `:10289` |
| epoch "recent" window | `2 × EPOCH_EVERY` | derived | `:11085` |

Blast: mostly money and noise — the two throttles exist because JB
drowned in his own Inbox once; loosening them re-floods it.

### A.3 Memos, caches, and the room-warm loop (all FIRMWARE — excluded)

Warm-loop boot delay 20 s (`:11321`), period 45 s (`:11334`), refresh at
`ttl × 0.8` (`:11331`). `_memo` TTLs: one-inbox 10 s (`:7485`) ·
cap-manifests 30 s (`:1810`,`:2064`) · sched-heads 30 s (`:11904`,`:12439`)
· atlas-act 30 s (`:7510`) · verdicts 60 s (`:12375`) · interop 60 s
(`:12247`) · craft-heads 120 s (`:12417`) · sentences-door 120 s
(`:11314`, carrying the quinn-v3 cold-build scar). `SENTENCE_TTL` 60 s
(`:5242`) · `_CRAFT_CACHE` 60 s (`:3603`) · `CATALOG_TTL` 300 s (`:3150`)
· `market.CACHE_TTL` 6 h (`orreth_sim/market.py:35`) · `seeds.CACHE_TTL`
3600 s (`seeds.py:31`) · `tradingdata._TTL` 1800 s (`tradingdata.py:23`).
Blast: stale glass showing wrong governance state — correctness, not
preference. A human tuning cache coherency is debugging, not governing.

### A.4 Money — spend ceilings and budget slices (PURPOSE, emphatically)

| dial | value | site |
|---|---|---|
| `SEARCH_DAILY` | 6/day | `console_worker.py:4036` (`ORRETH_SEARCH_DAILY`) |
| `ASSAY_CEILING` | 25000 tok/day | `:9076` (`ORRETH_ASSAY_DAILY_TOKENS`) |
| `ORRETH_SEARCH_OFF` | flag (thrift lever) | `:4012`, `:4627` |
| subscription `cadence_beats` default | 100 | `orreth_sim/serials.py:41` |
| subscription `budget_calls` default | 4 | `orreth_sim/serials.py:41` |
| fan-out budget | 2400 tok, min share 60 | `console_worker.py:4780` |
| governed intent cost | 8 (64 heavy) | `:346`, `:1975`, ~20 sites — **FIRMWARE** (plane's own prices) |
| `vera.EST_TOKENS` | 120 | `orreth_sim/vera.py:38` |
| chassis `max_tokens` | 400 | `agents/orreth-agent-sdk/orreth_agent/chassis.py:161` |

Blast: real money — the Tavily 1000-credit burn was this family.
`SEARCH_DAILY` + `ASSAY_CEILING` already confess themselves in the glass
(`:13607`, `:13650` publish `ceiling_tokens` beside `spent_today`) — the
natural first customers; the display half stands. A budget the human
cannot change is not a budget. (The remembered 14400/100800 cadences are
NOT in code — they are live per-subscription record values parsed from
the human's own "every N beats" at the parlor: the success case, already
generalizing.)

### A.5 Leases, fuel, and capacity (PURPOSE)

| dial | value | site |
|---|---|---|
| `ORRETH_JOIN_LEASE_DAYS` | 30 | `console_worker.py:207` |
| `ORRETH_JOIN_LEASE_TOKENS` | 50000 (dev.sh forces 400000) | `:225`, `scripts/dev.sh:37` — **the stated default is nowhere the observed one** |
| `ORRETH_LEASE_RENEW_DAYS` | 1 | `:226` |
| `ORRETH_FLOOR_CAPACITY` | 20 present | `:13718` (informs the gate; the human's word decides) |
| `fuel.EST_FLOOR` | 500 tok | `orreth_sim/fuel.py:18` — "the wound's own number, 419, must fall on the drained side" |
| `ORRETH_DORMANT_DAYS` | 7.0 | `orrethd/src/main.rs:304` — Rust-side policy, release-only in practice: boundary case |
| `resident_ttl` / `workforce_ttl` | P30D / P1D | `backend/plane/profiles/*.json` |
| `budget.renew_days` | schema (`minimum: 0`) | `contracts/v0/common.schema.json:117` |

Blast: starves residents mid-thought or removes the spend guard whole.

### A.6 Probation and promotion (FIRMWARE until unified — the duplication IS the finding)

`PROBATION_BEATS` 3 (`orreth_sim/farm.py:30` **and** `orrethd/src/farm.rs:12`) ·
`CANARY_BEATS` 3 (`orreth_sim/stable.py:32` **and** `orrethd/src/model.rs:11`) ·
`EOL_HORIZON_DAYS` 30 (`orreth_sim/stable.py:33` **and** `console_worker.py:3151`) ·
`market.MISS_LIMIT` 3 (`market.py:36`) · `VERIFY_BLIND_LOOKS` 3
(`console_worker.py:10207`). Three of five duplicated across the
Python/Rust boundary with no shared truth — a glass-tuned probation would
move the sim's copy while the plane keeps enforcing 3.

### A.7 Retention and horizons — the easiest win (PURPOSE; already in config)

Tier profiles (`backend/plane/profiles/`): demo-universe raw `P395D` /
distilled forever / horizon forever / qa 0.001 / failure floor `P90D`;
demo-eco `P395D`×3, qa 0.001; demo-field raw `P90D` / distilled `P395D` /
horizon `P90D` / qa 0.01. Shared: `retrieval.time_budget`
`{time_ms:500, cost:3}` · `steward.token_budget` 100000 @ `P1D` ·
`judge_sample_rate` 0.1 · `join_default: floors-only`. **Hardcoded a
second time** in `shipyard.py:42,49,60-65` + `provisioner.py:76-82` (the
minting path). Adjacent regimes: `observatory.py:30` raw 6 h / hourly 7 d /
daily 90 d · `continuity.py:42-60,123-127` (`forever`/`PT10M`/vaulted;
overlay raw `P30D`, distilled `P3650D`) · `canon.py:29-77` per-class
minima `P7Y`/`P1Y`/`P90D` · `ATTESTATION_COOLING_DAYS` 7
(`continuity.py:450`). **The worst single case in the repo:** the recall
window `timedelta(days=365)` repeated bare at TWENTY sites
(`console_worker.py:341,400,497,712,839,970,1775,2469,2503,2631,4068,
4141,4174,4457,5290,5646,6052,7266,11262,12566`), plus `days=3650` (`:1185`),
`days=120` (`:1970`), `days=90` (`:10874`). Blast: too short silently
starves recall; too long grows the corpus into the performance disease.

### A.8 Judgment thresholds (PURPOSE, three constitutional exceptions)

`SUCCESS_FLOOR` 90 (`console_worker.py:5234`; `improver.py:288`, cycle cap
5 at `:304`) · chassis `max_cycles`/`max_obs` 3/3 (`chassis.py:55`) ·
fingertip defaults 2/3 (`fingertip.py:510-511`) · `thumb.MIN_CAL_N` 5 /
`CAL_BAR` 0.4 (`thumb.py:118-119`) · `vera.FLOOR_MEAN` 0.55 /
`TREND_DROP` 0.15 / sample 3 (`vera.py:53-54,73`) ·
`rivals.CONFESSION_FLOOR` 0.3 (`rivals.py:126`) · `infotheory`
MISSING/STUB bits 32/8 (`infotheory.py:32,35`) · `provisioner.ANON_CAPS`
stamp 12 / budget 2000 (`provisioner.py:20`) — **FIRMWARE, 0013 §8
mechanical** · `PLATFORM_FLOORS` quotas/allotments/hibernation
(`provisioner.py:162-190`) · `artifacts.MAX_BYTES` 256 KB
(`artifacts.py:20`) — **FIRMWARE, JB's lock 2026-07-11** · `purge.QUORUM`
2 humans (`purge.py:15`) — **FIRMWARE, constitutional**. And
`improver.NUDGE_KEYS = {max_cycles, max_obs, ladder, success_floor}`
(`improver.py:18`) — **the machine's own hand; lock L3 decides who wins.**

### A.9 The bell (PURPOSE; the clamp pattern's home)

`ORRETH_BELL_COOLDOWN_S` 3600 (`console_worker.py:9734`,`:11691`, display
`:9835` — read at three sites, unbound to a constant) ·
`ORRETH_BELL_GATE_AGE_H` 48 (`:10180`, `×3600` at `:10302`) ·
`bell.py:95` default 3600 · `ORRETH_WITNESS_SILENCE_S` 90 with the
**`.max(90)` firmware floor** (`orrethd/src/main.rs:382-383`) — the
pattern §3.7 canonizes. Highest per-dial consequence in the inventory:
spams JB's real inbox or silences a real tamper alarm.

### A.10 Scheduled asks, the desk, the studio (PURPOSE; the template's home)

`every_days` default 7, **clamped `max(1, min(90,…))`** (`console_worker.py:11923`);
`at_hour` clamped 0–23 (`:11926`); re-read `or 7` at five sites ·
`ORRETH_DESK_HOLDING_DAYS` 7 (`agents/flavors/05-desk/pipeline.py:387`) ·
`STUDIO_DARK_S` 90 (`console_worker.py:10422`) · desk gate timeout 600 s
(`05-desk/run.py:51`), join 6 h (`:100`) · `YARDSTICK_V1` ten questions,
genesis-only-then-craft (`console_worker.py:11711`) · run-now override
flags `ORRETH_YARDSTICK_NOW` / `ORRETH_DESK_GRADE_NOW` /
`ORRETH_DESK_DUE_NOW`. Blast: holding period too short grades calls
before their window closes — the reflection loop learns from noise.

### A.11 Ports and rig topology (FIRMWARE/ENV — 0063 does not sprawl here)

`EMBED_PORT` 4562 · `ALLEN_FIELD_PORT` 4510 · `shipyard.BASE_PORT` 4503 ·
f:charles `FIELD_DEFAULT` 4520 · `CDP_PORT` 9339 · orrethd default 4400 ·
demo stubs 9917/9923 · `RIG_IMAGE`/`RIG_NET`/`RIG_PG`
(`console_worker.py:7643-7645`) · compose pg healthcheck 2 s/2 s/15
(dev-only password in-file). Breaks the rig outright, no governance gain.

### A.12 The glass (FIRMWARE timers; one PURPOSE ordering)

`staleNote` 12 s (`window.html:3323`) · meter `hotUntil` 12 s (`:2308`) ·
`loadForeign` 15 s (`:3502`) · `parlorPoll` 1.5 s (`:4448`) · `capFresh` /
`brnFresh` 10 s (`:5221`,`:5768`) · scrub 300 ms · search debounce
400/350 ms — all FIRMWARE. **`KINDRANK`** (`:3510`) — gravest-first
ordering (attestation 0, testament 1, consent/passage 2, … default 8) —
**PURPOSE**: which grievance reaches the human first is the human's call.

### A.13 Agents and quinn's walk

`WALK_EVERY` 86400 (`04-uat/run.py:34`, "one real walk a day (JB's
cadence)") — **PURPOSE by name**. Settle times 2000–6000 ms
(`04-uat/clicks.py:87` + ~12 sites), screenshot timeout 45 s — **FIRMWARE**
(Playwright timing; the mute-vs-clean law rides on them). Flavor cadences
20/20/30 s, SDK `wait_online`/`join` timeouts (`client.py:78,93`).

### A.14 Env and mode dials (names only; ENV forever)

Operational: `ORRETH_MODE` · `ORRETH_VERSION` · `ORRETH_OBS_DIAL` ·
`ORRETH_MEANING` · `ORRETH_EMBED_URL` · `ORRETH_DEMO` / `ORRETH_DEMO_CFG`.
Secret-adjacent (0059 law, never records): `ORRETH_ROOT_PUB`,
`ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `OPENROUTER_API_KEY`,
`TAVILY_API_KEY`. **No `.env.example` exists** though `.gitignore:34`
whitelists one — sp0 births it.

### A.15 The Rust core (read-only recon; rule-9 territory)

`farm.rs:12` PROBATION 3 · `model.rs:11` CANARY 3 · `model.rs:10`
LIFECYCLE states · `model.rs:269` `renew_s = renew_days × 86400` (the
fuel window's real enforcement) · `main.rs:112` port 4400 · `main.rs:304`
DORMANT 7.0 · `main.rs:382-383` witness `.max(90)` · `main.rs:111`
retrieval horizon **read from the profile** (fallback "forever").
**Load-bearing:** the plane already reads policy from profile JSON and
env — plane-side dials flow through the profile; the core never opens
(§3.10).

### A.16 Count and the honest remainder

**~165 dials**: 39 env-backed · ~90 bare Python literals · ~12 Rust-side ·
~9 glass timers · ~15 profile/config JSON. Proposed razor split:
**~85 PURPOSE · ~60 FIRMWARE · ~20 ENV/secret-adjacent.**

Not swept, named honestly: `infrastructure/cdk/` (deploy constants) ·
`backend/conformance/tests/` (48 files — test literals aren't dials, but
a few JB locks may live only there) · `contracts/v0` beyond
`common.schema.json:117` (other schemas may carry bounds) · the store and
crypto crates (rule 3) · `window.html` CSS/pixels (timers + KINDRANK
only) · ten `orreth_sim` modules sampled at ALL_CAPS depth, inline
literals unhunted (`estate`, `stacks`, `experiment`, `tournament`,
`graphspec`, `dispatcher`, `hitl`, `markers`, `resolver`, `world`) ·
`docs/design/0000–0017` cross-check (the intended OWNER of several of
these numbers is likely written there — the natural pre-build step).
