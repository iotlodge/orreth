# 0054 — The Desk (charles comes home)

<!-- PROVENANCE: Fable 5 (claude-fable-5) — designed 2026-08-12 on JB's word:
     "I would like you to recreate the Trading desk of CortexObserver using
     Orreth." Ground truth read first: the sample bundle at
     tmp/charles-NVDA-2026-05-11 (the report IS lock L3, resolved by his own
     zip) and a full architectural map of ~/PycharmProjects/CortexObserver
     (LangGraph desk, 16 nodes, 15 prompts, watchlist cron, reflection loop). -->

**Status: 🟢 OPENED 2026-08-12 — all four locks landed same day (AskUserQuestion,
JB's hand): L-A yfinance + Tavily ≤6/day · L-B NVDA, weekdays at market
close, refresh mode (first full run manual as sp3's proof) · L-C the
minimal Capabilities pull v1, the desk its first installed world · L-D
**sonnet carries balanced, opus carries the two reasoning stages**
(research manager + portfolio manager — full reference parity, 2 opus
calls/run). Building.**

## 1. The brief

Recreate CortexObserver's Trading desk **as Orreth objectives** — the
0049 §4 bar inherited: equal or better, never lift-and-shift. @charles
becomes a resident; his pipeline becomes a governed walk on the ladder;
his report becomes the first real Chronicle; his watchlist becomes a
standing word. The sample bundle (charles-NVDA-2026-05-11) is the
deliverable's exact shape — headers verbatim, files one-to-one.

**Boundary law restated: the desk observes and reports. It never executes
a trade. The compliance disclaimer rides every report as policy craft.**

## 2. What the reference taught (condensed)

- **The pipeline (16 stages)**: retrieve context → fetch data → four
  analysts (market/social/news/fundamentals) → bull/bear debate (cyclic)
  → research manager → trader → three-way risk debate (cyclic) →
  compare-to-prior → portfolio manager → persist. Two stages think at the
  reasoning tier; the rest balanced.
- **15 prompts**: 13 named skills + 2 inline ones (`compare_to_prior`,
  `format_report`) whose exact section headers the tabs and the bundle
  depend on. In CortexObserver the studio EDITS a DB prompt the code
  never reads back — a wart; in Orreth the worker reads its own shelf
  (0045), so editing craft IS editing behavior, structurally.
- **Data**: yfinance (free, no key; flaky — the port carries the
  one-snapshot-cache invariant, serial fetches, retry ladder, honest
  `data_quality_errors`) + Tavily (3 calls/run: company news, macro news,
  social sentiment) + optional Alpha Vantage (skipped v1).
- **Liveness**: partial-persist after every stage so the glass fills as
  the run breathes. In Orreth this is free and BETTER: every stage files
  a signed record; the view is a projection of records (rule 7), not a
  merged blob.
- **The learning loop**: decisions wait `outcome_pending`; 5 days later
  realized return vs SPY becomes a reflection; the next run recalls it.
- **The delta**: each run loads the prior report and reconciles — in
  Orreth this is a stacks retrieval with the time dial (0038/0039),
  which makes 23_delta_vs_prior the memory program's first live test.

## 3. The organ mapping (equal-or-better, named)

| CortexObserver | Orreth organ | Better because |
|---|---|---|
| @charles (LangGraph agent) | a resident: persistent DID, joins at becky's gate, persona on the shelf | a self that survives the process (0002/0006); metered under his own name |
| 15 prompts (13 file + 2 inline) | 15 craft assets on the shelf, per-desk named (`charles-…`) | versioned, gated, editable-with-history (0045/0031); the inline two become first-class |
| tier registry (reasoning/balanced/fast) | the Stable's classes via ada (0019) | deals, canaries, price-drift cards; F2's class seam kept |
| MCP tools (tradingdata, Tavily) | Farm services through the gateway (0018) | pinned manifests, worldlines, per-call meter; Tavily under the standing-spend law (0032 + the Tavily lesson) |
| Command.result partial merge | every stage = a signed Chronicle record, glass reads records live | rule 7; nothing can disagree; each partial is provenance, not cache |
| Memory Farm episodic + reflection | the Chronicle + scribe-signed observations (0005); reflections recalled next run | author ≠ agent on outcomes; the 0039 metabolism will digest it |
| compare-to-prior (loads prior blob) | stacks retrieval, time dial, prior report cited by ref | the delta names its evidence; this IS the retrieval test |
| watchlist cron (APScheduler) | 0032 standing subscription staged at 0012's gate | a recurring spend is the human's standing word — ceilinged, cancellable, visible |
| ZIP bundle endpoint | bundle door: records + artifact-pointers (charts ride the pointer law, 0022/0039) | the bundle cites its records; charts' bulk never enters the mind |
| report viewer (8 tabs) + workspace studio | the desk view in the glass; craft edits in Governance | tab shape ported verbatim; prompt tuning = craft-edit gates that actually bind |

## 4. The spoonfuls

1. **sp1 — charles joins**: the floor stands (proposed `u:demo/e:desk/
   f:charles`, siblings reserved for charlene/chad); charles a resident
   with persistent DID; his 15 prompts + disclaimer land as shelf craft;
   the pipeline as a versioned plan template. Proof: his calling card in
   the parlor, his craft in Governance, census clean.
   **LANDED + PROVEN LIVE 2026-08-12.** `e:desk :4511` + `f:charles
   :4520` grown through the shipyard gate on an approved word (req-701 —
   no file edited by hand; the dock crew wrote the profiles). The genesis
   module `orreth_sim/desk.py` holds all 20 assets (16 prompts extracted
   VERBATIM from the reference by AST + 3 schema hints + the persona);
   the improver's beat planted every one on the universe shelf ("the
   shelf takes «charles-…» v1" × 20) and the craft door serves them —
   they stand in the Governance room, editable at gates from day one.
   **The becky-per-floor law**: joins were hard-bound to f:prod
   (JOIN_PORT + a module-level scope); becky's desk is now a DELEGATE
   PER TENDED FLOOR, each chained to the same pinned root — same
   challenge, same human gate, same proof-not-claims, only the minted
   lease's floor changes (suite 330+5 green; JoinDesk untouched).
   charles joined HIS OWN floor — "welcome to u:demo/e:desk/f:charles" —
   the first lease this rig ever minted off f:prod, and his birth record
   cites the exact craft refs he woke with. L-D honored: sonnet-5
   (medium) + opus-5 (high) saddled at ada's gate on f:charles, deals
   pinned in-catalog, canaries earned `available` for both.
2. **sp2 — the supply line**: `tradingdata` (yfinance, the defensive
   machinery ported as intent) planted in the Farm; Tavily's three desk
   queries under the declared ceiling; every call a worldline record.
   Proof: 12 + 3 calls land metered on a real NVDA fetch.
   **LANDED + PROVEN LIVE 2026-08-12.** The reference's 742-line
   tradingdata became `orreth_sim/tradingdata.py` — the INTENT ported
   (one snapshot per ticker per half-hour, everything slices from it;
   retry ladder; honest darkness; indicators in plain pandas; the
   reference's 12 calls consolidated to 8 tools) — wrapped by a keyless
   local stall (`tradingdata_server.py` :4570) planted at charlotte's
   gate with a STABLE did (`did:web:desk.local:tradingdata` — the
   local-service DID-churn trap named by the map, dodged), manifest
   pinned, probation earning serving on live beats. **The Farm's invoke
   door finally exists** (`POST :4562/tool` — no such door anywhere
   before): resolve serving on the named floor → refuse the discredited
   at the threshold → METER FIRST (the plane's 403 is the authorization,
   not telemetry) → execute at the stall → return; bulk never becomes
   records (the pointer law); every miss wears the one refusal face
   (rule 4 — proven: off-manifest tool and unknown service answer
   identically). Proven live under charles's own DID: **8/8 tools
   metered on the plane** (the cache visible in the wire: 1420ms fetch,
   then 11ms slices); the desk's three Tavily queries via `gather` →
   9 findings quarantined at 0.0000 on f:charles, metered. **The L-A
   ceiling is law at the one chokepoint every caller passes**
   (`tavily()`): a durable line per live search since UTC midnight,
   default 6/day (`ORRETH_SEARCH_DAILY`); past it the placeholder
   speaks honestly and the ledger gains no line — proven: the seventh
   search spent nothing. Suite 330+5 green.
3. **sp3 — the first report**: "@charles analyze NVDA" as an objective —
   plan gate up front, stages as intentions, every artifact a signed
   record; the delta retrieved via the time dial; the polished report +
   decision.json + chart pointers; the bundle door serves the ZIP shape
   byte-compatible with the sample. Proof: JB downloads the twin of his
   own sample, every section citing its records.
   **LANDED + PROVEN LIVE 2026-08-12 — the first real Chronicle.** The
   sixteen stages as charles's OWN governed walk (`pipeline.py`): the
   plan gate up front (a `desk-run` card the human approves; silence is
   a no and says so), every prompt acquired from the shelf by ref, every
   thought authorized+metered under his lease (sonnet medium, opus for
   the two reasoning stages — L-D), every tool call through the Farm's
   door, every search through gather under the ceiling, EVERY STAGE a
   signed record on f:charles as it lands (rule 7 — no partial-persist
   blob; the floor went 11 → 65 records). The bundle is the sample's
   file-for-file twin (15 files, same names, same headers) at
   `tmp/charles-NVDA-2026-08-12/` + `.zip`; the delta says "This run
   establishes the baseline" honestly; `outcome_pending: true` on the
   report record awaits sp5's reflection loop. **The proof beyond the
   plan: the HONESTY CHAIN ran whole** — the day's search ceiling was
   already spent, so news/sentiment came back as labeled placeholders,
   the analysts declared thin ground, and the opus portfolio manager
   CAPPED ITS OWN CONVICTION below Buy for exactly that reason,
   prescribing a re-run after the UTC reset. The human's declared
   constraint became the machine's reasoned caution, end to end. Two
   live finds fixed in the walk: an empty model reply must retry once
   then confess (never ride into a debate as an empty section), and the
   queue's gather now returns TYPED findings beside its admission note
   (the analysts read content, not counts; the records stay
   quarantined). Deferred honestly: the delta reads his own recall (the
   stacks' time dial joins at the memory program); the bundle download
   button in the glass is sp4's.
4. **sp4 — the desk glass**: the eight tabs (Full Report · Overview ·
   Δ vs Prior · Market · Sentiment · News · Fundamentals · Debates),
   rating badge, price + indicator charts, per-stage progress strip
   riding real records, the meter visible. (Its HOME — plain view vs
   the first world in a minimal Capabilities pull — is JB's lock L-C.)
   **LANDED + SCREENSHOT-PROVEN 2026-08-12.** The Capabilities pull
   exists (L-C v1): a brass lever on the glass's right edge — "the
   Machine below, the worlds above" — sliding open the portal with the
   Trading Desk as its first installed world; `#…&cap=1` deep-links it
   open. The desk view drinks a NEW supply door (`GET :4562/desk`,
   the observatory/governance pattern): reports, stages, and charts
   composed from f:charles's OWN records via the librarian's seat
   (rule 7 — the glass never holds a second truth; charts dereference
   the artifact pointer at the door, their bulk never lived in a
   record). In the frame: report picker · rating badge (color by call)
   · target + horizon + the outcome-pending chip · the ⚠ dark-sources
   line when data_quality says so · the 15-stage strip, each ✓ a real
   record with its digest on hover · the price chart with 50/200-SMA
   overlays + RSI with 70/30 rails, hand-rolled SVG from the pointer's
   series · the eight tabs slicing the polished report's own sections ·
   **⬇ the bundle door** (`GET :4562/desk/bundle?name=…`, exact-name
   only, traversal refused 404) serving the 15-file ZIP. Build lesson
   on record: a cwd-relative edit inside a background task failed
   silently and the rebuild shipped without it — absolute paths in
   backgrounded file edits, always. Honest notes: the analyst tabs
   slice the POLISHED report (the full transcripts ride the bundle);
   the pull is one lever + one world by design — install/create and
   more worlds arrive with the pull's own dive.
5. **sp5 — the standing word + the loop**: the watchlist as a 0032
   subscription (default: market-close weekdays, refresh mode — news
   re-runs, the rest reuses, ~70% cheaper); the reflection beat (5-day
   outcome vs SPY → reflection records the next run recalls). This
   spoonful feeds 0053 sp3 — the memory program eats what it grows.
   **LANDED + PROVEN LIVE 2026-08-12, every law walked.** The watch is
   the human's STANDING WORD (0032 on the desk): staged with its terms
   readable ("charles walks NVDA every weekday at market close … ≤3
   searches under the ceiling … standing until you stop it"), approved
   once, minted as a signed record on f:charles; **stopping is
   immediate and gateless** (rule 11 — proven: cancel → posture
   `cancelled` on the wire in one motion → restored by a fresh staged
   word). The glass wears it: "🕰 the standing word … — stop it
   (stopping never needs a gate)". charles TENDS the word himself
   (`--tend`): due at the close on weekdays, walk under the standing
   consent — no per-run gate — and **the dedupe held live** ("already
   walked today — the standing word rests"). **The reflection beat
   ran whole**: the morning's Overweight graded against the tape
   through the Farm's own door (return vs SPY, alpha, `graded_early`
   flagged honestly on a same-day grade), ONE lesson on the record —
   and the very next walk's retrieve-context read **"prior report:
   yes · 1 lesson(s)"**: the learning loop is CLOSED. That walk also
   produced the first REAL delta — compare-to-prior fired against the
   prior report and reconciled like an analyst ("same-day re-run/
   refinement, not a new trading day"; caught a trailing-EPS
   discrepancy the first walk missed). Honest notes: the refresh-REUSE
   arm degrades to a full walk when the prior record predates
   `sections` (as it did) — tomorrow's standing walk is its first live
   exercise; the reflection craft is the 21st shelf asset
   (charles-trading-reflection), planted like all the rest.

## 5. The locks staged for JB

- **L-A — the supply line (0053 L2 made concrete)**: yfinance (free) +
  Tavily at a declared ceiling (recommended: ≤ 6 searches/day ≈ 3/run ×
  2 runs; hard dial stays). Alpha Vantage skipped v1. Ceiling number =
  JB's word.
- **L-B — the watchlist (0053 L1 made concrete)**: recommended start —
  NVDA alone, weekdays at market close, refresh mode on.
- **L-C — the desk's home in the glass**: a desk view now, the
  Capabilities pull later — or a minimal pull v1 with the desk as its
  first installed world. JB said he'd explain the pull's shape at its
  dive; this lock is where he does.
- **L-D — the desk's minds**: which saddled models carry `balanced` and
  `reasoning` classes (the rig currently saddles haiku + gpt-4o-mini;
  the reference used sonnet/opus tiers). Quality will show in the first
  report either way; ada's deal gate is the door.
- *(0053 L3 — the report's shape — RESOLVED by the sample bundle.
  0053 L4 — the ten questions — still open, wanted after a week of runs.)*

## 6. Honest boundary

- One desk, one ticker to start; charlene/chad are a prompt-set away by
  design (the agent-key seam kept), but not this dive.
- Reports only, forever, on this rig. The disclaimer is non-negotiable
  craft.
- yfinance is flaky by nature; honesty rides `data_quality` — an analyst
  with no data files the honest placeholder, never reasons over nothing.
- The debate cycles run fixed rounds (1 research, 1 risk) as the
  reference does; adaptive rounds are future craft.
- The first reports' quality depends on what's saddled (L-D); we ship
  honest, then tune craft at gates.

## 7. Convergence

| Organ | What it supplies |
|---|---|
| 0053 | the charter this dive serves — sp1 of the course correction |
| 0027/0030 | the plan gate, the ladder the stages walk |
| 0045/0050/0031 | the shelf his 15 prompts live on; craft-edit gates as the studio |
| 0018/0019 | the Farm stall for tradingdata; ada's deals for the desk's minds |
| 0032 | the watchlist as the human's standing word |
| 0038/0039 | the time-dial delta; the classes his records wear; the metabolism that will digest them |
| 0043/0005 | the yardstick when the ten questions arrive; scribe-signed outcomes |
