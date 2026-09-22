# 0009 — The Old World, Carried

*Status: **DRAFT for JB's lock (2026-09-22).** Author: Claude Fable 5.1
(claude-fable-5-1). Docs only — nothing in the spine moved for this page.*

## Why this page exists

JB, 2026-09-22, verbatim: *"When it comes to replacing main, I don't want to
lose the previous arch or codebase. We have so many features in the first
arch design and although we went the wrong admin direction I still don't see
RAG, Farms, or Gateway (the Stable) that the previous arch embedded. I assumed
you would make a Tools Agent/Firmware for lifecycle management of Tools used
by the Operating Kernel, and the same for the LLMs with respective Firmware to
manage LLMs regardless of where they reside — our LiteLLM and OpenRouter
objective of the first arch build. Not sure how you want to proceed on old vs
new features, but as a kernel we're still missing these."*

He is right on every count. The rearch line (`docs/rearch/0001–0008`, the
Python spine under `spine/`, the Rust port opened in P7) carries the old
world's LAWS almost whole and its ORGANS only in part. Seventy-four dives
built the first architecture; the spine today is 28 modules and seven
templates. This page is the ledger that makes "ready to replace main" an
honest sentence: every organ, dive, and capability of the old world, and the
seat it holds in the new one, or a named park with a reason. **Nothing is
lost by silence.**

## The law this page proposes

**`main` is replaced only when every row of this ledger reads CARRIED,
RE-SEATED (with its spoonful built), CAPABILITY (with its proof re-walked),
or PARKED by JB's word. The old `main` stays reachable forever: tagged
`main-v0.72-old-world` (main's head is `3f88cb4`, VERSION 0.72) and kept as
the branch `old-world/main`, never deleted, never force-moved — the record
of the first architecture, and the reference the ledger's evidence column
points into.**

## How to read a seat

| Seat | Means |
|---|---|
| **CARRIED** | exists in the spine today; the module is named. "partial" names what is missing. |
| **RE-SEATED** | planned in the rearch canon; the phase/spoonful is named. Built nowhere yet unless said. |
| **CAPABILITY** | lives ATOP the kernel as a purpose or proof, not inside it (the taxonomy's razor). Its proof is named. |
| **PARKED** | not in V1, with the reason. Unparked only by JB's word. |

The evidence column is blunt on purpose. A row that reads well and is wrong
is the exact thing this page exists to prevent.

## The ledger

### Identity & joining

| Old organ (dive) | What it did | Seat | Evidence / gap |
|---|---|---|---|
| A keypair is a self (0002 · 0006) | persistent DID per agent, seeds under `~/.orreth`, same self re-joins | CARRIED — `identity.py` | seed persists under the body's home; ephemeral only for tests. Rule 1 holds. |
| becky's join door + leases (0006 · 0012) | governed join queue, root-chained attenuation-only tokens, revocation | RE-SEATED — P7 sp3 (doors) · sp6 (the bodies' seam) | `resident.py` carries a **dev gate v0** only ("the governed becky gate arrives with kernel"). No token chain, no revocation, no queue a human sees. |
| The doors that answer (0071) | publishable join door, signed machine asks, per-DID knock ceilings, ask-cache | RE-SEATED — P7 sp3 · sp8 | none of it in the spine; the glass's doors are unauthenticated dev doors. KCR-0001 must be re-paid on the new kernel. |
| The Person (0070) | humans as identities: own key, signed acts, name never reissued | CARRIED partial — `proof.py` | persons enroll TOTP and can be masters; no person keypair, no signed human act. |
| Factories + BirthCertificate (0011) | archetype → incarnation, upgrade in place, rookie probation | RE-SEATED — 0004 "the factories" + the draft shelf | `spine/templates/*.v0.json` are versioned templates; no birth record, no probation, no factory body. |
| Roster breathes (dormancy, leases) | present vs remembered, 30-day leases, never deletion | CARRIED — `presence.py` | leases renew while serving; dormant in seconds; stays listed. |

### Governance & policy

| Old organ (dive) | What it did | Seat | Evidence / gap |
|---|---|---|---|
| The cascade resolver (0007) | floors tighten-only, ResolvedContext content-addressed, every thought names its law | RE-SEATED — P7 sp7 (cells) | `spine/policy/covenant-policy.v1.json` is ONE flat policy worn by every body. No floors, no cascade, no context hash on a thought. |
| HITL gates, quorum, cooling-off (0012) | consequence waits for humans; silence never approves | CARRIED partial — `proof.py` · `tools.py` · `mitl.py` | L1/L2/L3 ladder, ConsequentialHold, MFA. No distinct-signer quorum, no cooling-off, no expiry law. |
| The Reins — rule 11 (0051) | cancel/rest as recorded acts on everything managed | CARRIED — `intent.py` stop · `scheduler.py` rest · `proof.py` stop_demand | walked green in P6. |
| Markers & severity lanes (0024) | signed annotations deriving from what they mark | CARRIED — `markers.py` (0006) | the open vocabulary of WHY; severity lanes not modeled. |
| The Epoch (0041) | which machine was in force: signed canon fingerprint, revert = sibling | PARKED — awaits a proof's need | versioned templates + the conformance suite stand in; no fingerprint record. |
| The Deed (0042) | effect classes: reversibility, independent observer, ceremony by class | CARRIED partial — `tools.py` consequence classes | routine / consequential / grave gate the ladder; no independent-observer walk-back. |
| The Craft Room + the machine speaks + the dictionary (0045 · 0050 · 0060) | prompts/skills/policies as governed, editable shelf-craft | RE-SEATED — 0004 draft shelf, cut-a-version gate | templates are JSON on disk; no craft-edit door, no gloss shelf. |
| The Dynamic Universe — 36 dials (0063) | declaration = firmware, value = craft; humans tune values | RE-SEATED — no spoonful named (see locks) | the spine tunes by env var. A dial drawer belongs beside Controls. |
| The Rail and the Stamp — guardrails (0068) | PII/PCI firmware detectors in the one lane; audits never leak; stamps before weakening | RE-SEATED — P6.5 sp6c (RAG) | absent from the spine. KCR-0003 re-paid when E-RAG re-walks. |
| The Custodian tier (0013) | apex-above-apex, vigil, quarantine grades | PARKED — was parked in the old world too | gate unchanged: the hosting decision. |

### The Stable — LLMs

| Old organ (dive) | What it did | Seat | Evidence / gap |
|---|---|---|---|
| The Model Plane (0016) | LiteLLM through the floors; degrade-where-pins-allow; plane meters, never sees the prompt | RE-SEATED — P6.5 sp6b | `gateway.py` = `AnthropicGateway` + two fakes. **No LiteLLM, no OpenRouter, no local route, no pins, no degrade rule.** The prompt law holds. |
| The universal meter (0019, rule 5) | every resident's cognition metered under its own DID; honest zeros | CARRIED — `gateway.py` `spine_meter` | per DID · model · tokens in/out · landed-at. **No dollars** (no price known), no per-floor rollup. |
| The Stable registry (0019) | minds as identities: stalls pin the DEAL, price drift = rug-pull, EOL calendar, ada | RE-SEATED — sp6b | no registry of minds anywhere; a template names a model string and the gateway honors it. |
| The market + effort=class + assignments + allocation A/B (0058) | five-eyed catalog, class routing, subject→pin ledger, arms as signed records | RE-SEATED — sp6b | `harness.py` runs golden cases per TEMPLATE; there are no model arms, no assignment ledger, no class. |
| The fuel clause (0058 wound, `budget.renew_days`) | allowance-per-window, lazy renewal, refill door | RE-SEATED — sp6b | the spine has **no budgets at all**; a body can think without a ceiling. |
| The LLM-lifecycle watcher (0004) | watches retirements and drift; rolls assignments; owns the A/B harness | RE-SEATED — sp6b | designed in canon, no template exists. The harness it should own exists without an owner. |

### The Tool Farm & the Toolshed — tools, MCP, services as identities

| Old organ (dive) | What it did | Seat | Evidence / gap |
|---|---|---|---|
| Services are identities (0018) | DID'd tools/MCPs, manifest hash pin, lifecycle ladder, drop = lease expiry, charlotte | RE-SEATED — P6.5 sp6a | `tools.py` = a Python dict of seven built-ins (weather · acquire · mark · purge-memory · add-watch · seal-record · erase-record). No registry, no DID, no manifest, no ladder. |
| The governed tool door (0059's ONE door) | every call metered, journaled, authorized | CARRIED — `tools.py` `ToolDoor` | declared per template or refused (teaching); journaled; AG-7 chain on the wire (`orreth.tool.called.v1`); L2 interlock. |
| MCP as a whole transport (0059) | `tools/call` through the one door, session, SSE | RE-SEATED — sp6a | **no MCP client in the spine.** |
| The env-secrets law (0059) | `env:NAME` indirection; a key in ZERO records | RE-SEATED — sp6a | no endpoints, so no secrets yet; the law must land with the first remote tool. |
| Seed catalog, RESTING, allocations, warden checks, playground (0059) | registry searched live; rest/resume; per-floor allocation; credential sniffer | RE-SEATED — sp6a (catalog last) | none present. |
| The Estate / allen (0037) | the infrastructure resident; charters stores and cloud | RE-SEATED — 0004 allen-class resident · `placement.py` | placement policy stands (P6 sp4); no allen body. |
| Residents keep themselves + the Serials Desk (0062 · 0032) | standing supply lines, subscriptions as standing word | PARKED — rule 12 | `scheduler.py` gives the standing-duty half; the supply line waits for a proof that needs it. |
| AgentField & the AgentSurface (0010) | five-verb SDK-neutral surface | RE-SEATED — 0004 (LangGraph body) · P7 sp6 | superseded by the body; the SDK-side `Resident` is the new surface. |

### Memory & RAG

| Old organ (dive) | What it did | Seat | Evidence / gap |
|---|---|---|---|
| The signed log is the truth; every index a projection (0022) | one Postgres, pgvector + BM25 hybrid, trust-weighted rerank | CARRIED in law (0003) · partial in code — `store.py` · `projector.py` | Understanding v0 is **lexical only** (`tsvector:english`); **no pgvector, no embedding lane**. Lineage + validity intervals stand. |
| The Knowledge Loop (0014) | sources as identities, quarantined at 0.0000, promotion with receipts, recall by lineage | CARRIED partial — `store.py` state + lineage | quarantine state and lineage exist; source identities go with FARMS (sp6a). |
| The Purge (0026) | tombstones carry hashes never words; purge reaches every projection | CARRIED — `store.py` `PURGE_EVENT` · `tools.py` purge-memory | test_purge green. |
| Pruning + the universal metabolism (0003 · 0057) | every floor breathes; forgetting measured | CARRIED partial — `digest.py` | the Digest compresses citing every record; no sweep, no measured loss. |
| The Estate of Sources (0069) | the Basket + byte law, store/database kinds, extraction line, grounded wiki, ONE embedding truth | CAPABILITY — sp6c, re-proven by E-RAG | none in the spine. `store.put` is already content-hashed: the byte law's seed. |
| The Stacks — seven RAGs as projections (0038) | seven projections over one log, never seven truths | CARRIED in law — 0003 | the law binds; no projection beyond lexical exists. |
| The engine on the chassis — eleven styles (0065) | typed module contracts, standing projections, graded harness | CAPABILITY — E-RAG's engine, re-proven on the new kernel | PARKED in the kernel by rule 12. |
| The router learns the ask (0066) | choices = actions, gradings = reward, scoreboard | CAPABILITY — E-RAG | markers + the grader firmware are the seed of reward reaching action. |
| Multimodal upload (0029) | upload as an ask, artifact content-addressed | CAPABILITY — with the Basket (sp6c) | no upload door. |
| The Aperture (0031) | context projection as a signed record | RE-SEATED — 0003 "packing the mind" | context assembly exists in the body; not a signed record. |
| The Human Profile + the Mirror + personas (0025 · 0070) | sovereign profile, provenance-labeled; persona craft | RE-SEATED — 0003 "who remembers what"; sessions carried (`glass.py`) | sessions per person stand; no profile, no persona slot. |
| orreth-EnterpriseRAG (the first proof, 8/9 closed, 4 KCRs paid) | enterprise retrieval as a capability; Orreth as the API | CAPABILITY — re-walked after sp6c on the new kernel | held at the halt in its own repo; its register is the acceptance list for sp6c. |

### The Console, the orrery, the brain views

| Old organ (dive) | What it did | Seat | Evidence / gap |
|---|---|---|---|
| The admin Console: tabs, rooms, reel, drawer, master-detail (0021 · 0052 · 0056 · UI dives) | manage the universe as an administrator | **DROPPED on purpose** → the Bridge (0001) | JB's "180° wrong." One Chat + seven pulls replace it. Nothing here returns. |
| The Parlor + residents listen (0020 · 0046) | click a resident, be received; it fetches with its own authority, answers on the record | CARRIED — the One Chat: `glass.py` · `resident.py` | fan-out, includes, streamed replies; walked green P3–P6. |
| The Living Brain, the orrery, the spacetime window (0036 · 0008 · 0061) | physiology of the universe drawn live | RE-SEATED — 0004 "where they show": the firmware in flight, the WOW work | no live picture of bodies and floors in the glass; the Crew pull lists them. |
| The fingertip + the chassis + thinking (0027 · 0015 · 0047) | objectives planned high, slivers dispatched, typed thoughts | RE-SEATED — 0004 body + 0007 intent loop | CARRIED as the LangGraph body and the fifth rail; the parking lot → knowledge intents is not. |
| The Faculty & Agent Lab (0040) | skills gathered, crystallized, canaried, served | PARKED — JB's stamp ("built only when stamped ready") | the factories (0004) are its successor seat. |
| The Thumb (0048) | 👍/👎 as signed human verdicts on the exact record | RE-SEATED — no spoonful named | the critic's marks arrive in chat; the human's verdict door does not exist. |
| The One Place + the capability contract + the package (0053 · 0055 · 0072) | worlds bring their rooms; sealed signed package a stranger installs | RE-SEATED — P7 sp8; the One Chat is the one place | KCR-0002's package (`orreth-package-v1`) not in the spine; a capability has no install door. |
| The Act draws itself (0067) | one graph language, every box a door | CARRIED partial — `export.py` AG-7 chains | the chain is on every row; nothing draws it. |

### Observability

| Old organ (dive) | What it did | Seat | Evidence / gap |
|---|---|---|---|
| The Observatory + vera (0043) | observability as a projection; the examiner grades under its own DID | CARRIED partial — `monitor.py` · `harness.py` · `templates/firmware-grader.v0.json` | watches, snapshot, judge; the grader is scribe-class. No per-floor tour, no daily ceiling. |
| The Bell + the witness (0044) | dead-man notices silence; the one organ that reaches a human off-glass | CARRIED half — `presence.py` (the witness) | dormancy is noticed and listed. **No bell: nothing reaches a human beyond the glass.** |
| Run record + monoidal roll-up (0005) | aggregatable envelope composed up the tree | RE-SEATED — P7 sp7 (cells, partition) | one ground, one world today. |
| A/B with signed arms (0043 · 0058) | arms as records, deterministic split, promotion as a stamped act | CARRIED partial — `harness.py` | template goldens only; arms and promotion go with sp6b. |
| The Epoch drill / drift stages never enacts (0041) | | PARKED — see governance | |

### Templates, universes, dials

| Old organ (dive) | What it did | Seat | Evidence / gap |
|---|---|---|---|
| A template is a universe as data; the Shipyard (0009 · 0021) | League · Second Brain · Company; floors launched by conversation | RE-SEATED — P7 sp7 (cells = worlds) | the spine is ONE world ("a memory wears its world" is a column, not a floor). |
| One binary, tier = profile, two clocks (0000 · 0004-old) | universe-time monotone, wall-clock for money | CARRIED partial — validity intervals, the meter's clock (W17) | no declared universe-time; rule 8's rejection of backdating not modeled. |
| The Continuity Universe + the Testament (0034 · 0035) | the personal universe; survivorship | PARKED — template-shaped, waits for worlds | the standing grave law (never revive f:probe:4509) belongs to the old rig. |
| Dials (0063) | | RE-SEATED — see governance | |

### The SDK & the doors

| Old organ (dive) | What it did | Seat | Evidence / gap |
|---|---|---|---|
| orreth-agent SDK 0.4.0 (PyPI) + the join door (0017 · 0071) | a stranger's world joins with published artifacts alone | RE-SEATED — P7 sp6 (Python `Resident` = the SDK-side body) · sp8 | "continue SDK for sure" (0008). Not cut on the new line. |
| Machines ask and are answered (0071); Orreth as the API (E-RAG) | signed `ask` kind for agents | RE-SEATED — P7 sp3 doors; CAPABILITY for the API face | the glass's ask door is a dev door. |
| The Desk / charles (0054) | a purpose world through Orreth end to end | CAPABILITY — re-proof after release | untouched. |

### Docs, demo, campaign

| Old organ (dive) | What it did | Seat | Evidence / gap |
|---|---|---|---|
| The Open Book — docs.orreth.ai (0064) | Learn · Build · Reference | RE-SEATED — P7 sp8 (docs in every close loop) | FROZEN under the halt; the book teaches the old doors. |
| demo.orreth.ai | the spectator site | PARKED — until release (0005) | frozen at era 0.60. |
| Articles 01–08, the campaign, Show HN | | PARKED — until release (0005) | |
| The six embodied proof repos | body · fleet · blackbox · genuine · ota · fuel | PARKED — 0005's out-of-V1 list | held deliberately; their own season. |
| The multiverse portal · voice · enterprise IdP federation | | PARKED — 0005 (voice V2; federation seam declared, minimal) | |

**Tally (63 rows):** CARRIED 8 · CARRIED partial 12 · RE-SEATED 29 ·
CAPABILITY 6 · PARKED 7 · DROPPED 1. The honest reading: the LAWS crossed; the
ORGANS that made the old world a product mostly wait on the four bodies
below and the port's sp7–sp8.

## The two firmware bodies the kernel still lacks

JB's assumption was the right one. Bodies are Python/LangGraph by canon
(0004 · 0008), so the keepers can be built NOW in the spine without
touching the Rust port; only their kernel seams — the registries, the
routing tables, the meter — are port work. Each keeper is a firmware body
of the third kind: a DID with no persona, named by function, wearing the
covenant, acting on the markers it cares about (the interest law).

### 1. The TOOLS firmware — the Toolshed's lifecycle as a body

- **Exists to build on:** `tools.py` (declared-or-refused door, journal,
  consequence classes, the L2 interlock, the AG-7 chain on the wire);
  `presence.py` (drop = lease expiry, the SPIFFE lesson already the rail's
  law); `scheduler.py` (standing duties); `harness.py` (checks as duties);
  `markers.py`.
- **New:** a **registry of tools as identities** — DID + manifest hash pin,
  the ladder proposed → probation → serving ⇄ resting · dropped ·
  quarantined · decommissioned (0018), a changed manifest → quarantined (the
  rug-pull door); **MCP as a transport inside the one door** (`tools/call`,
  session, SSE) so a remote server's tools are declared like built-ins;
  **the env-secrets law** on the first remote endpoint (`env:NAME`, a key in
  zero records); **a meter line per tool call** beside the mind's meter;
  **allocations** per body and per world; **the warden's checks at
  onboarding** (dead probe, declared-vs-probed, credential-in-URL) run by
  the harness as duties; **the keeper** (function name: toolkeeper —
  charlotte's job, no persona) tending the ladder on the scheduler's beat
  and staging every transition as an ask the human sees. The seed catalog
  (the MCP registry searched live) comes last.
- **Where it slots:** body + door + registry as Python spine modules with
  fixtures (`tools-v0.json`); the port carries the registry, the ladder's
  legality, and the meter row into `orreth-spine` under the law of a ported
  module. Execution of a tool stays body-side (rule 5's shape: the kernel
  authorizes and journals; it never runs the call).

### 2. The STABLE firmware — the LLM lifecycle, wherever a mind resides

- **Exists to build on:** `gateway.py` (one door, `spine_meter`, streaming,
  templates naming a model); `harness.py` (golden cases per template);
  `monitor.py` (watches); the intent loop with Cost named next (a
  `cost-anomaly` kind); `templates/firmware-grader.v0.json` (a scribe-class
  judge).
- **New:** a **registry of minds** — a stall pins the DEAL (model id ·
  provider · route · price · context · modalities · hash); **routes**:
  anthropic-direct · LiteLLM · OpenRouter · local, one gateway resolving a
  route per call (0016's "LiteLLM executes, the registry knows and
  decides"); **routing policy** per body and per ask (effort = class →
  assignment → pin; degrade only where pins allow, confessed); **dollars on
  the meter** (price from the pin, never guessed); **health** (the canary
  ping under the keeper's own DID, metered); **drift and EOL** (catalog
  sync against the pin → deprecated + a staged reapprove naming what moved;
  the pasture horizon); **budgets** (allowance-per-window with lazy
  renewal, the refill door — the fuel clause); **the A/B harness with model
  ARMS** (the same golden cases against two stalls, verdicts by the grader,
  promotion = an assignment change under the human's cut); and **the
  keeper** = 0004's LLM-lifecycle watcher (ada's job).
- **Where it slots:** as above — Python body, doors, registry tables with
  fixtures (`stable-v0.json`); the port carries registry · assignment ·
  meter-in-dollars · route resolution. The SDK call stays body-side; the
  kernel never sees the prompt (rule 5, unchanged).

### 3. The FARMS — one ladder, two keepers (a simplification to lock)

0018 built the ladder for tools; 0069 proved the same ladder carries
stores and databases; 0019 gave minds their own copy. Proposal: **one
registry of services with worldlines** (`kind ∈ tool · mcp · store ·
source · mind`), one lifecycle legality, one meter, two keeper bindings on
the one workspace-firmware template (0004's "seven pulls are seven
bindings"). The Farm stops being a second organ and becomes the registry
both keepers tend. Sources (0014's "external sources as identities") join
here, which is what RAG needs next.

### 4. RAG as a capability on the four memories

- **Exists to build on:** `store.py` (content-hashed put, lineage,
  validity, quarantine state, the lexical projection wearing its kind);
  `projector.py` (the events-rail consumer that folds facts into
  rebuildable read models); `digest.py`; the purge.
- **New, kernel-side (small):** an **embedding lane** as a second
  Understanding projection built by a projector — vectors wear their model
  (0003 · 0069's one-truth law), pgvector on the same ground, purge-reached
  by construction. **Sources** as services (§3). That is all the kernel
  owes.
- **New, capability-side:** the Basket (objects + signed pointers with
  origins), the extraction line, the grounded wiki, the eleven-style engine,
  the router and its scoreboard, the guardrails in the body's lane — the
  E-RAG program re-installed as a capability package on the new kernel and
  re-walked against its own register. Rule 12 holds: E-RAG's re-walk is the
  proof that pays sp6c.

## Where they slot — the trade-off and the recommendation

| Option | Shape | Costs | Gains |
|---|---|---|---|
| **A. P7 sp6 expansion** — sp6a TOOLS · sp6b STABLE · sp6c FARMS + RAG, inside the port after sp5 | organs built once, Rust seams first, Python keepers beside | JB's ask waits behind sp2–sp5 (weeks); every organ commit under `backend/plane` is his to review; the Python spine is "retired to reference" before the organs exist in it, so the fixtures are written against nothing | no double build |
| **B. A parallel Python track — "P6.5 the organs"** — beside the port, now | the four organs land in the Python spine as P6 modules did (module + doors + fixtures + JB's walk); the port's sp3 (doors) · sp4 (loops) · sp5 (meter) carry them like any other module | two builders on one ground; sp3–sp5 grow; discipline needed so the port never ports an organ that has not closed | JB's gaps close first and visibly; the reference implementation holds the organs before the port does (0008's law); rule 12 stays honest (E-RAG's re-walk is the proof) |

**Recommend B.** The port's law is that a module is ported only when its
fixture file passes unchanged; a fixture needs a reference, and the
reference is the Python spine. Building the organs in Python first is not a
detour, it is the order 0008 already binds. sp6 keeps its name (the bodies'
seam) and gains a line: *"the keepers are bodies; their registries are
ported at sp3–sp5."* P6.5 closes the way every phase closes: JB in the
glass, the Crew pull showing tools and minds as bodies, the meter in
dollars, one remote MCP tool serving by env name.

## What stays parked, and why

- **The multiverse portal · voice · IdP federation** — 0005's out-of-V1
  list, unchanged.
- **The six embodied proof repos and the campaign** — held for their own
  season; the sites stay frozen until release (the release-alignment law).
- **The Custodian tier, federation transport, the Faculty** — parked in the
  old world behind the same gates; nothing moved them.
- **The Epoch, the Deed's observer walk, the supply lines** — rule 12:
  each waits for a proof that hits the wound.
- **The Continuity Universe and the Testament** — templates need worlds
  (P7 sp7) before a personal universe can exist.

## What the old world had that the new deliberately dropped

Drawn on purpose, so the line is visible:

- **The admin-interface Console** — tabs, rooms, the reel, the drawer,
  master-detail everywhere. JB's "180° wrong." The Bridge and the One Chat
  replace it; nothing of that direction returns.
- **The polling request queue and the `/hello` beat** — replaced by the
  rails (outbox → RabbitMQ + Kafka → the Bridge feed). The worker's
  `:4562` doors do not return.
- **The Objectives band** — replaced by the Analyzer (0007, block 11).
- **The executable sim (`orreth_sim`) as a separate model** — the Python
  spine IS the reference implementation now (0008).
- **The demo reel (`scripts/demo.sh`)** — JB's walks in the glass, with the
  friction register, are the proof; the reel's stories become docs
  screenshots at the release wave.
- **Shelf-craft speech in the glass (⟦slot⟧ gate cards)** — the chat renders
  the body's words; craft returns through the draft shelf, not the glass.
- **Hand-rolled graph drawers** — nothing draws today; when a picture
  returns it is the firmware-in-flight view, one language.

## What this document binds

1. **`main` is replaced only when every row above reads CARRIED, RE-SEATED
   with its spoonful built, CAPABILITY with its proof re-walked, or PARKED
   by JB's word.** A row without a seat blocks the release wave.
2. **The old main is kept forever**: tag `main-v0.72-old-world` at
   `3f88cb4`, branch `old-world/main`, never deleted, never force-moved.
   Evidence in this ledger points into it by dive number.
3. **The four organs are V1 kernel work**, not capabilities: TOOLS firmware,
   STABLE firmware, the services registry (FARMS), and the embedding lane.
   RAG above the lane is a capability, re-proven by E-RAG.
4. **This ledger updates in the closing commit of every spoonful that moves
   a row** — the same law the honest boundary held (JB's lock, 2026-07-26).
   A ledger that lags lies with confidence.

## JB's locks owed

1. **A or B** — the P7 sp6 expansion, or the parallel Python track "P6.5 the
   organs" beside the port. Recommended: B.
2. **One ladder, two keepers** — one services registry (tool · mcp · store ·
   source · mind) with two keeper bindings, or the Stable and the Farm kept
   as two organs as the old world had them. Recommended: one ladder.
3. **Which parked rows he wants unparked** for V1 — candidates he may feel
   the lack of first: the Bell's outward reach (email), the dials drawer,
   the Thumb, the Epoch.
4. **The tag and branch names** — `main-v0.72-old-world` and
   `old-world/main`, or his own.
5. **The proof that pays sp6c** — E-RAG's re-walk on the new kernel
   (recommended), or a new proof world.
