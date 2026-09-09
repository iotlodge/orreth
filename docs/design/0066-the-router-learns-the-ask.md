# 0066 — The Router Learns the Ask

*Drafted 2026-09-07 from the orreth-EnterpriseRAG proof's charter — the proofs era's second
kernel dive, demanded beside 0065 (the engine this router drives). Grounded in two
evidence passes the same day: a full survey of the kernel's feedback-and-improvement
machinery, and the licensed deep-research on learned retrieval routing (the proof repo's
`docs/research/rl-routing-report.md`).*

***Status: 🟡 DRAFTED · LOCKED — L1 (the learning ladder) and L3 (thumbs veto and calibrate,
never score) approved by JB 2026-09-07; L2 (the three-level rule) approved WITH A CONDITION
that is now a standing law: the language of every human-facing decision, section, and
question must be crystal human clear — plain words first, canon terms as labels only. "One
of the CORE objectives of E-RAG is human friendly terms and experience vs cryptic guessing"
(JB, verbatim). §3.8 rewritten under that law the same hour.***

## 1. The demand, verbatim (the proof's charter)

> "I want the Solution to agentically (hot when applicable) be able to read the request and
> understand what's happening to decide what RAG architecture is best for the Context of the
> ask. This will need RL and Feedback to improve, monitor etc." — charter addendum 1
>
> "Humans should reply to thumbs up and down with detail on down about improvements which
> should enter Kernel's self improvement (resulting in HITL approval). When a critic or judge
> does a review this is also a great place to apply at both request/objective as well as
> Intention and Observations." — addendum 2 §8 (the feedback law)
>
> Auto is the router itself (the menu lock, 2026-09-06); the selection is never a secret;
> two-tier judging locked; the router's explanation is human-persona-friendly by law.

## 2. The problem — what the surveys found

The Dispatcher (0038) declared the right aspiration — *"choices = actions · gradings =
reward · standard revisions = policy"* — and built the first third:

1. **The RL substrate has actions but cannot reach their rewards.** A dispatch choice is a
   leaf record — no `derived_from`, no coordinate (`dispatcher.py:117-127`). The ask lane
   returns prose; the choice id survives as eighteen truncated characters inside a routing
   note (`console_worker.py:6650-6656`). The exchange record, the yardstick row, the verdict,
   and the thumb all fail to carry a structured choice ref. The one working reward join in
   the codebase is the experiment's: verdict → work record → the `arm:` tag it wears
   (`experiment.py:165-185`).
2. **Query analysis is six regexes with no mind, no confidence, and no learning**
   (`dispatcher.py:45-60`) — and the escalation-on-ambiguity the module's own docstring
   promises was never implemented. The one governed-mind classifier in the retrieval-adjacent
   path classifies *feedback*, not queries (the 0048 classify leg — typed contract, one
   re-ask, parks honestly: the proven pattern to extend).
3. **The Observation rung is empty.** Verdicts land at Objective and Intention
   (`vera.py:48`); nothing signed exists per observation for any judge to grade
   (`chassis.py:113-123`). The proof's every-rung law needs a rung built, not just wired.
4. **Routing changes are structurally rewrites** — high lane, human signature, every time
   (`improver.py:18-19`): correct for rules, but it gives an adaptive router no lawful way to
   breathe between gates.
5. **The research's verdict is deflationary and Orreth-shaped**: the routing win comes from
   small, auditable, batch-updated classifiers over outcome-labeled data — not RL.
   Production bandits warm up offline and update on batch cadence; full offline RL is
   over-machinery (one ask is a one-step decision — definitionally a bandit, and not even
   that at first). And E-RAG holds a superpower ad systems lack: **its reward is computable
   offline** — an ask can be replayed through every arm the router did not choose, at zero
   serving risk.

## 3. The shape

### 3.1 The Analyzer — deterministic first, a mind when it earns one

The Understand module (0065's first contract) grows a **versioned featurizer**: the six
shapes become a declared feature extractor (firmware-versioned, its version pinned in every
choice record) emitting the charter's analysis dimensions — type, complexity, domain
signals, freshness need, modality, latency/cost preference. On low deterministic confidence
— and only where the ask's latency class permits — **the escalation the docstring always
promised finally exists**: a governed-mind classification leg on the 0048 pattern (typed
contract, cheap class, one re-ask, parks honestly). *Hot when applicable* means exactly
this: the mind consults when the features are ambiguous; the hot path never waits on a
thought it doesn't need.

### 3.2 The choice joins the world

The dispatch choice record stops being a leaf: it gains the coordinate and lineage, carries
`featurizer_version + features + standard_version`, and the **answer record carries the
choice ref** (beside the variant tag 0065 sp5 gives it). Verdicts and thumbs then reach the
choice through the same join the experiment already proved. The choice's `why` stays a
human-persona-friendly sentence — the router explaining itself is the same record that
trains it.

### 3.3 The signal vector, and reward as governed arithmetic

Every completed ask accretes a **signal vector on the record**: rung-decomposed judge
scores (retrieval quality · faithfulness · answer quality — two-tier bench per the lock),
citation coverage, latency, metered cost, and the thumb when one lands. **The combining
weights live in the routing standard** — so re-weighting the reward is a gated act, and
history is re-scorable under any future weights. Signals are data; the reward function is
law.

### 3.4 The learning ladder (staged; each stage a proposal, never a self-deployment)

- **Stage 0 — ship:** the hand-authored deterministic standard (0065 sp1's registry-derived
  version), enriched choice records, the signal vector. Nothing learns yet; everything logs.
- **Stage 1 — standings:** per-query-class × per-variant **Bayesian standings with credible
  intervals**, maintained as a projection over the signed records (rebuildable, purge-
  reachable — data, not policy). A **proposal generator** reads the standings and stages a
  new standard version whose evidence IS the standings table — through the independent grade
  and the human gate, on the existing improvement road.
- **Stage 2 — the supervised router:** when labeled volume earns it, a small classifier
  (trained on judge-labeled outcomes) proposes routing-standard versions with its evaluation
  as evidence. The classifier is a versioned asset; its adoption is a gate.
- **Stage 3 — contextual bandit:** the destination vocabulary, earned only by volume;
  the same proposal discipline holds.
- **Refused by design:** full offline RL (over-machinery for a one-step decision) and
  per-ask policy updates (the human-gate law forbids them; the research shows production
  never needed them).

### 3.5 Exploration — offline first, the experiment as the only live lane

- **The nightly replay:** completed asks re-run through every feasible non-chosen arm,
  judged by the cheap bench, standings updated — the full counterfactual panel at zero
  serving risk. (Latency and thumbs are the only signals replay cannot reach.)
- **The live ε-floor:** a small deterministic hash-split slice rides the **existing N-arm
  experiment machinery** — the arm is the fingerprint, standings by log join, conclude
  refuses thin evidence, adoption on the human's word. The graduation ladder is
  replay → live slice → gated proposal.

### 3.6 The feedback law, made mechanism (and the 0031 invariant honored)

The thumb machinery stands as built; this dive gives the 👎-with-detail its full road
**without ever making feedback an auto-trigger**:

- The words are **taxonomy-labeled** by the studio's classify leg (existing), become
  **replay-suite cases** (the ask re-runs forever with the complaint attached), and ride
  **verbatim on the next routing/craft proposal** as evidence — which then walks the
  existing grade → **HITL approval** road. The proof's law lands exactly as written:
  detail enters the kernel's self-improvement, resulting in HITL approval — and 0031 §4's
  "feedback is never an auto-trigger" survives intact, argued with rather than around.
- **Thumbs never become reward scalars.** Judges are the backbone; thumbs are a veto and
  calibration layer (the existing calibration beat already compares them). The research's
  canonical failure — reward-weighted thumbs breeding sycophancy — is refused by name.

### 3.7 The Observation rung gets built

Observations become signed **observation-outcome** records (coordinate-bearing, scribe-
authored, cheap — the chassis already holds the tuple it would sign), and vera's sampling
universe grows to all three rungs. The proof's every-rung law lands; the router gains
per-retrieval verdicts to learn retrieval quality from, not just answer quality.

### 3.8 What changes freely, and what waits for a human — the three-level rule

*(Stated plain-first by JB's L2 condition, 2026-09-07: the language must be crystal human
clear — the canon terms ride as labels only.)*

**In plain words: the router's scoreboard updates itself; the router's rulebook only
changes when a human approves; and a few pre-approved knobs sit in between.**

1. **The scoreboard** (canon: the standings projection) — the running tally of which
   architecture is winning for which kind of question. It updates continuously and
   automatically, because it is only a *summary of records that already exist* — like a
   scoreboard at a game, it reports, it never referees. Deleting it loses nothing; it
   rebuilds from the records.
2. **The rulebook** (canon: the routing standard and its policy assets — rules, defaults,
   reward weights, the featurizer, the exploration rate's meaning) — *how the router
   actually decides*. Every change is a written proposal carrying its evidence, reviewed
   independently, and **approved by a human before it takes effect**. The router can argue
   for a rule change; it can never make one.
3. **The knobs** (canon: router dials on the 0063 machinery) — a short, named list of
   numbers a human already put limits around (how often the nightly replay runs, how big
   the small live test slice is, within hard bounds set in advance). Turning one inside its
   limits doesn't need a fresh signature, because the human's word was given when the
   limits were set — and every turn is still recorded.

The test for which level something belongs to: *if changing it could change an answer a
user gets, it's rulebook. If it only measures or paces, it's scoreboard or knob.*

### 3.9 The PUT side (0065's parked stub, paid)

The registry's `requires` finally drives ingestion routing: a new record's modality and
kind determine which projections index it — deterministic, declared in the standard,
recorded like every GET choice. `dispatch_put` stops returning "everything."

## 4. The razor applied

| Layer | Class |
|---|---|
| Featurizer, module contracts, observation-outcome shape, standings-projection DDL | **Firmware** — release |
| Routing standard (rules, weights, ε policy), classifier assets, replay question sets | **Craft** — gated, versioned |
| Router dials (ε bounds, cadences) | **Dials** — medium lane, within firmware bounds |
| Standings, choice records, signal vectors | **Data** — projections and records, purge-reachable |

## 5. The locks (staged for JB, 2026-09-07)

- **L1 — the learning ladder** (§3.4): standings-first, supervised later, bandit only if
  volume earns it, offline RL refused.
- **L2 — the lane razor** (§3.8): standings update as data; every policy change is a gated
  proposal; bounded router dials on the medium lane.
- **L3 — thumbs as veto/calibration, never scalar reward** (§3.6); 👎-detail enters
  self-improvement as labeled evidence + replay seeds + proposal attachments through the
  existing gate.

## 6. The spoonfuls (proposed order)

1. **sp1 — The join.** ✅ **LANDED 2026-09-09 — the choice joins the world: every future
   reward can reach its action.** The dispatch record stops being a leaf: it DERIVES
   from the exact rulebook version that made it (`derived_from` → the routing-standard
   asset; a genesis-only world leaves lineage empty, honestly — never a fabricated
   ref), wears its coordinate as tags (0033 §4's idiom: `variant:<style>` matching
   0065 sp5's answer law, `origin:<who asked>`), and carries `featurizer_version:
   "shapes-v0"` + the whole `standard_ref` in the body — sp2's mind will replace a
   NAMED v0, never an anonymous regex. The answer's side: **the ask door's exchange
   record derives from the choice** (one GIN-indexed lineage hop — the same join the
   experiment's arm tags proved), the parlor's routing note stops truncating the
   choice to eighteen characters (refs are data, 0052's law — the recon's named
   wound), and **the yardstick rides the structured lane**, each row keeping the whole
   choice ref so a verdict on an answer reaches the routing decision it judges.
   *Proven live on the rig: an SDK ask, then ONE SQL join (`e.derived_from[0] = c.id`
   on the plane's standing GIN index) walked the exchange to its choice — the
   coordinate tags read back (`variant:naive · origin:ask:did:key:…`), the body
   through the governed door confessed flavor · featurizer `shapes-v0` · the spoken
   why · `standard_ref`, and the choice's own lineage resolved to the routing-standard
   asset version. Suite 450→454 (four join laws: rulebook lineage · coordinate +
   featurizer · honest-empty lineage · thumb→choice in one hop). Rust green.* *Honest
   remainders: the parlor's audience record carries the whole ref in TEXT — its
   structured `derived_from` rides when the parlor lane returns the ref (a small
   follow-on); bodies stay in the object store by law, so the one-query join is the
   LINEAGE walk (SQL) with content reads through the governed body door, as
   everywhere.*
2. **sp2 — The Analyzer.** ✅ **LANDED 2026-09-09 — "agentically, hot when applicable"
   is live.** The six shapes stopped being an anonymous regex pile:
   `orreth_sim/featurizer.py` is the DECLARED extractor (firmware `feat-v1`, pinned in
   every choice record) emitting the charter's dimensions in plain words — what kind of
   question · how many parts · length · domain words · how fresh the answer must be
   (historical/current/timeless off the standing time law) · modality · the asker's
   latency preference · and how CONFIDENT the deterministic read is. **The escalation
   the docstring promised in July finally exists**, on the 0048 pattern exactly: only a
   LOW-confidence read from an asker who did not demand speed earns one governed
   thought (the librarian's seat, the stable's judge mind, metered like every thought);
   the mind picks from the eleven-name menu under a typed contract — one re-ask, then
   an HONEST PARK with the deterministic read serving, the stumble on the record. The
   asker's own word (`force`) outranks the mind; the mind's choice obeys the built law
   like everyone. **The first honored attribute**: `latency: fast` gates the escalation
   and the envelope's `honored` list finally says so — attributes stop being
   received-and-ignored. The choice record carries `features` + `consulted` whole.
   *Proven live on the rig, three lanes: an AMBIGUOUS ask (four conflicting shapes)
   consulted a real governed mind that chose «multi-agent» with a plain sentence — the
   why, the features, and the consult all on the choice record; the same ambiguity with
   `latency: fast` spent NO thought and the envelope confessed `honored=['latency']`; a
   clear ask stayed HOT, routed by rule with no mind involved. And the park law proved
   itself unprompted: the first live consult hit a pin/class mismatch and served the
   deterministic read with the park spoken on the record — exactly the designed
   failure. Suite 454→463 (nine Analyzer laws). Rust green.* *Honest remainders: the
   consult rides the judge mind at medium class (a dedicated cheap router mind is an
   allocation decision for ada's market, not a code edit); confidence is a
   deterministic rule pair — its thresholds become tunable when the standings (sp4)
   show where it misjudges.*
3. **sp3 — Signals and the rungs.** The signal vector; observation-outcome records; vera's
   three-rung sampling; two-tier bench wiring. Suite: a verdict lands at every rung.
4. **sp4 — Standings and the proposal generator.** The standings projection; the nightly
   replay harness; the first standings-evidenced standard proposal walked to JB's gate.
5. **sp5 — The live slice and the dials.** The ε-floor experiment wiring; the router dials;
   the PUT-side registry routing; f:router's flow retires honorably on the record.

## 7. The honest boundary rows this dive moves

- The "RL substrate" claim becomes true (actions joined to rewards) — a new proven row with
  the join query as evidence.
- The Observation rung's emptiness — from unwritten to proven-or-partial, honestly.
- New parked row: Stage 2/3 learners wait for volume; the register says so.

## Appendix A — evidence trail

The feedback/improvement survey (2026-09-07): thumb law `thumb.py:63-110`, studio routing
`console_worker.py:11213-11365`, severity lanes `markers.py:18-31` + `improver.py:18-19`,
verdict shapes `vera.py:100-135`, WORK_TAGS `vera.py:48`, the empty Observation rung
`chassis.py:113-154`, the experiment's reward join `experiment.py:165-185`, the two-lane
fossil `console_worker.py:6739-6747`, the missing ask-lane join `console_worker.py:6650-6656`.
The routing research: the proof repo's `docs/research/rl-routing-report.md` (Adaptive-RAG ·
RouteLLM · RAGRouter-Bench · production bandit practice · the sycophancy counterexample).
