# 0063 — The Dynamic Universe

*Reserved 2026-08-27 from JB's seed; draft opened 2026-08-28.*
***Status: DRAFT — JB's locks awaited before any build.***

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
   behind it. Cancel/revert is first-class (rule 11).
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

- **sp0 — unify before you dial:** the twenty `days=365` literals become
  one named constant; the minting path reads the profile it plants; the
  Python/Rust duplicates get one source of truth or a formal release-only
  word; `.env.example` is born. No new machinery — honest ground for it.
- **sp1 — the registry:** dial declarations + genesis planting + the ONE
  memoized accessor; three dials walked live end-to-end. Candidates
  (lock L4): `SEARCH_DAILY` and `ASSAY_CEILING` — the two the machine
  *already confesses* in the glass beside `spent_today`, so the display
  half stands — plus `MIRROR_EVERY` (a pure cadence) or `KINDRANK` (an
  ordering, proving a dial is any tunable VALUE, not just a number).
- **sp2 — the gate:** the craft-edit door learns typed validation + bounds +
  blast-radius cards; a turn proven live through the glass; refusal-outside-
  bounds proven live.
- **sp3 — the ladder:** per-floor / per-resident overrides by the 0059
  resolution; the improver's nudges re-homed inside the human's bound (§3.9).
- **sp4 — the rooms:** in-place dials on owner cards + the settings room.
- **sp5 — the infra lane** in the Atlas.
- **sp6 — the sweep:** the appendix inventory migrated dial by dial, env
  demoted to genesis, each landing with its bounds and blast radius; the
  long labor of the dive, paced across sessions.

## 7. Open locks (JB's calls — the draft stands until these land)

- **L1 · The home of values.** Extend the existing craft shelf (dials as a
  typed craft kind riding all of 0050's machinery — versioning, lineage,
  hash names, the one-motion door) **[recommended]**, or a new first-class
  record kind with its own doors.
- **L2 · The razor's default.** When a value's side is unclear:
  FIRMWARE-until-named-PURPOSE (conservative; a value stays release-only
  until a human classifies it) **[recommended]**, or PURPOSE-by-default.
- **L3 · The machine's own hand.** The improver already tunes four dials
  autonomously. When a human turns one: the human's value becomes the
  BOUND the improver optimizes within (§3.9) **[recommended]**, or the
  improver loses those keys entirely, or the improver's nudge outranks
  and the card confesses it.
- **L4 · The first walk.** `SEARCH_DAILY` + `ASSAY_CEILING` +
  `MIRROR_EVERY` (two ceilings with the display half built, one cadence)
  **[recommended]**, or swap the third for `KINDRANK` (prove the
  non-numeric dial early), or JB names his own.

*Standing recommendation not raised to a lock:* the effect horizon —
live-read via the memoized accessor, taking hold within ~a minute, the
horizon confessed on the card (never restart-required). Objection welcome;
silence adopts it.

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
