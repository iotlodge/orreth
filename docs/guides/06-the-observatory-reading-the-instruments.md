# Guide 06 — The Observatory: reading the instruments

<!-- PROVENANCE: Fable 5 (claude-fable-5) — first edition 2026-07-31, written the
     night 0043 closed whole, while every instrument was still warm. -->

*Guide 02 taught you to run the world; this one teaches you to READ it. What
the universe measures about itself, where each number comes from, what it is
telling you — and what it will never tell you without saying so.*

---

## 0. What the Observatory is (and refuses to be)

Every monitoring product you have ever used is a third person: an external
witness watching your system through exported, unsigned trace blobs, judged in
someone else's court. Orreth refuses the sidecar, because it holds an advantage
no sidecar can copy: **the trace already exists, and it is signed.** An
Objective decomposing into Intentions, every Thought metered, every consequence
gated — that *is* the trace. The Observatory is not a second system watching
the first; it is a **projection over the signed log** (rule 7 — never a second
truth), read by a resident whose own cost is on the meter like everyone else's.

The short version of everything below: **other stacks film the robot; here,
the world remembers — and the Observatory reads.**

## 1. The one law to read everything by: the two tiers

Every panel in the room wears a small chip, and the chip is the most important
thing on the page:

- **`log-truth`** (green) — this number is *rebuildable from signed books*.
  Tokens, dollars, verdicts, gate-waits, epochs, standings: delete the panel,
  re-derive it from the record, get the same number. This is testimony.
- **`instrument reading, not testimony`** (violet) — this number came from a
  stopwatch or a private book: latencies, the refusal taxonomy, the recorder's
  own pulse. Honest, useful, and *not* something the universe swears to.

When a number surprises you, check its chip first. Testimony you can act on at
a gate; an instrument reading you treat as a good witness with no oath.

## 2. The dial: how much watching costs

The room's header always opens with the dial: **glance · watch · assay.**

| Position | What runs | What it costs |
|---|---|---|
| **glance** | counters and series only — the flight recorder's passive tap | free |
| **watch** | glance + deeper reads: distributions, percentiles | free (a deeper *read*, never a new collection) |
| **assay** | the Examiner beats: vera samples completed work and commissions independent judges | **real tokens, metered under vera's DID**, bounded by a declared daily ceiling |

Three things to know:

1. **Depth costs money and says so.** At assay, the header shows the spend
   against the ceiling to the token: `spent 8.6k/25.0k tok today (the declared
   ceiling, G5)`. When the ceiling closes, the examiner rests loudly.
2. **Turning the dial is a governed act.** Say to vera in the parlor: *"set
   the dial to assay."* She stages a card — *"the gate waits for you, and I
   hold no levers"* — and only your click turns it.
3. **The word persists.** A turned dial survives worker restarts (`dial.json`
   in the observatory's nest). The environment default (`ORRETH_OBS_DIAL`,
   glance) is genesis only — your word outranks it until your next word.

## 3. The room, panel by panel (the 🔭 tab)

### The header — and the watcher's own pulse

`the observatory · dial at ASSAY · … · watching 19 floor(s), whole`

On the right breathes a dot: **the recorder's pulse.** The flight recorder
lives inside the console worker, and a monitoring organ's one unforgivable
failure is going dark *silently* — so this room refuses to. Brass and slow:
healthy. Amber and quick: the recorder hasn't beaten in >45s. Dark red — the
whole room collapses into a single card, **"THE WATCHER HAS NO PULSE"**, naming
the remedy (`scripts/dev.sh start`). If you see stale panels *without* that
card, distrust the guide, not the room — that would be a bug worth a drift
card.

### Cognition — the flight recorder *(instrument)*

Every governed thought in the universe passes the model plane's gateway to be
metered — so coverage here is total *by construction*, never by diligence.

- **governed thoughts / tokens / metered spend** — every LLM call by every
  resident, canary, judge, and voice.
- **ms p50·p95** — thought latency percentiles (the watch depth).
- **flow span ms** — how long intentions take to carry, read off the *signed*
  outcome records (this one is log-truth even inside an instrument panel).
- **the sparkline** — tokens per hour. Double-click any canvas to keep its PNG.
- **the refusal chips** — `no-local-key ×4 · stumbled ×1`, beside the standing
  reminder **"one face outside."** This is the taxonomy rule 4 forbids the
  world from seeing: outside, every refusal is identical so a prober learns
  nothing; *inside the recorder's own book*, refusals wear names so **you**
  can see what's actually failing. If `no-local-key` climbs, a floor is
  authorizing thoughts it has no key to execute — an honest refund each time,
  and a configuration you may want to fix.

### The assay — vera's standings *(log-truth)*

vera, the astronomer (the tenth organ, named for Vera Rubin) samples completed
work and commissions **a judge from another floor's stable** — never the floor
whose work it is; a universe with only one bench gets a refusal, not a
self-grade. Verdicts land as signed records under the *judge's* authorship.

- **the bars** — mean assay score per floor, `n` verdicts, trend arrow, red
  below the **.55 floor**.
- **the score strip** — every verdict as a dot on 0→1, the .55 floor marked.
- **"her own cost"** — the assay's price to the token and cent, metered under
  vera's DID. The Observatory's cost is always one of its own instruments.

Read low scores honestly: when the judges scored the old deterministic
scaffold outcomes at 0.1–0.2, that was the system *correctly measuring* what
the honest-boundary register had admitted in prose. A low mean is a fact about
the work, staged at your gate — never an automatic consequence.

### The experiment — arms are machines *(log-truth)*

When an A/B runs, each arm is shown by its **machine name** — the content-hash
of the floor's whole fingerprint with that variant standing as the asset's
head. Not a label somebody remembered to write down; the arm *is* the config.

`arm a · d0f89ae8d… ▮▮▮ 0.10 · n3 · 50%` reads: arm a, its machine hash, mean
verdict score, verdicts counted, declared traffic share. The state line shows
`running` → `concluded · winner: arm b` → `adopted`. The conclusion is never
enacted here — it is a promotion card at your gate, and the adoption writes
full lineage (`adopted_from` the winning variant, `derived_from` the variant
*and* the experiment). The loser stays on the shelf, outranked, never deleted.

### Gate-wait — how long consequence has waited *(log-truth)*

The panel almost nobody in the industry has, computed from stamps the signed
records already carry: every pending and staged request, oldest first, red
past a day. The first time this panel ever rendered it surfaced a purge that
had waited **19 days** — present in the queue all along, invisible as an *age*
until the panel existed. This is the panel that tells you whether you are
being the human your gates are waiting for. Silence is denial by law — but an
old age here is the universe telling you something asked and nobody answered.

### The seven rows — the RAG observatory *(log-truth)*

The Stacks' standings ladder: each retrieval flavor's tournament mean, the
leader in brass, a dark row honestly dark (a flavor with no wins is shown at
0.000, not hidden). The footnote is dense with governance: `standard v92 ·
default «hybrid» · epoch aea6ed32 · 0m · metabolism kept 10 warm, distilled 0
(loss 0.00 bits)` — which standard serves, which machine fingerprint the floor
currently *is*, how fresh that name is, and what the memory metabolism did
with measured loss.

### Farm & stable — the keepers' books *(log-truth)*

Charlotte's services (state and call counts per worldline) and ada's stalls
(mind, class, lifecycle state). Rug-pull correlation falls out for free here:
a service that came back changed sits quarantined beside its own call history.

### Governance — the machine's names *(log-truth)*

Every floor's current **epoch** (the short hash of its machine fingerprint)
and its age. When the Canon moves behind a recognized word — an improvement,
an estate adoption, a field join, a drift decision, an experiment promotion —
the epoch turns *quietly*. When it moves with **no word behind it**, a drift
card stages at your gate with the diff and a revert target. The footnote
counts every open card by kind, ending with the standing law: **detection
wears no levers; the gate decides.**

## 4. What comes to your gate (and what your click does)

The Observatory *never acts*. Everything it finds becomes a card in Requests:

| Card | What it means | Approve does | Deny/leave does |
|---|---|---|---|
| `dial` | someone asked vera to turn the dial | turns it (and the word persists) | the dial holds |
| `assay` (degradation) | a floor's mean fell below .55 or the trend broke | acknowledgment only — there are no levers; you decide what follows (often: ask grace for an improvement) | the finding stays on record |
| `experiment` (open) | a split wants to run, arms previewed as named machines | the split goes live | nothing ever serves |
| `experiment` (promotion) | an experiment concluded with min-n evidence per arm | the winner becomes the head, full lineage written | history remains, the standing Canon serves |
| `drift` | the Canon moved with no recognized word behind it | reverts to the signed machine as a new sibling (nothing deleted) — **check first that no legitimate act explains it** | keeps the change AND the finding on record |

A worked example of that last row, from the night this guide was written: the
first live experiment adoption was itself accused of drift — the watchdog's
vocabulary didn't yet include the experiment's word. The right click was
**"leave it"** (the change was legitimate; the accusation stays on record as
an honest false alarm), and the fix was teaching the watchdog the word — not
weakening the watchdog. When a drift card names a change you recognize,
leave it and ask why the watcher didn't recognize it. When it names one you
*don't* — that is the card doing exactly what it exists for.

## 5. The cast: three watchers, deliberately separate

- **vigil** is content-*blind*: shape, volume, refusal counts — never words.
- **vera** is content-*aware*: she reads completed work and commissions
  judgment. The separation is what keeps vigil trustworthy and vera useful;
  they never merge.
- **the Mirror** assesses *conversations* (Human↔Resident audiences); vera
  assays *work*. Neither grades itself, nothing grades its own floor, and
  every verdict is authored by someone other than the actor (0005, always).

Ask vera directly in the parlor — her card offers: *the standings · your own
cost · the dial · turn the dial… · what do you measure?* Her answers are
grounded in the same numbers the room draws, phrased by a governed, metered
voice.

## 6. Where it all lives, and how it ages

`~/.orreth/observatory/` is the recorder's nest:

- **`flight.jsonl`** — the raw book: one row per governed thought or refusal.
- **`summaries.json`** — the distilled pyramid: raw seals into hourly, hourly
  into daily, each climb with **measured loss** on the record. The moment an
  hour seals, its raw rows leave the book (they are redundant with their own
  distillate). *Even the monitoring ages honestly* — the same metabolism law
  as every other memory in the universe.
- **`dial.json`** — your standing word on the dial.
- **`rubrics.json`** — declared yardsticks by objective (state an objective
  with a `rubric` and the assay judges by *it*, marked `rubric_declared`).
- **`experiments.json`** — every experiment's state, arms, and standings.

All of it survives restarts; the ledger seeds, the worker holds live state,
and anything log-truth is re-derivable from the floors' signed records even
if the nest burned.

## 7. What the Observatory does NOT tell you (on purpose, on the record)

The gap register (`../design/0043-the-observatory.md` §11) is standing law:
*found → written → homed*. The honest edges as of this edition:

- **No out-of-band alerting.** A card at an unopened Console notifies no one;
  gate-expiry-is-denial bounds the harm. The push channel is its own future
  dive (it touches identity and consent, not just plumbing).
- **The daemon does not notice a dead worker** — only the glass does (the
  pulse, loudly). A second witness rides the same future dive.
- **Declared rubrics are landed but young** — until an objective states one,
  every verdict honestly says `rubric_declared: false`.

If you find a gap not on that register, it goes there first — a gap without a
named home is a gap being chosen, and we don't.

---

*The room's whole ethic in one line: every number names its source, every
finding stages where a human holds the key, and the watcher shows its own
pulse — because an observatory you cannot audit is just another camera.* 🔭
