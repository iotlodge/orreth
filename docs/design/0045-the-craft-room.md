# 0045 — The Craft Room («Governance»)

*Drafted 2026-08-03 · Fable 5 with JB · status: DESIGN — three shaping locks
taken, blessing pending*

## 1. The seed (JB, 2026-08-03)

Orreth is a MACHINE of machines — 100% agentic, with residents as its
embedded firmware — and what makes anything agentic is its driving NLP:
prompts, skills, policies, rubrics, charters. The machine has already
authored much of its own craft. And here is what Orreth has COMPLETELY
MISSED about HITL trust: **the machine shows its work but hides its
craft.** Every answer, verdict, and deed is on the glass; the words that
DRIVE those behaviors are invisible to any human who isn't the builder.
Governance over work you can see, driven by words you can't, is trust
with a blindfold on.

JB's three asks, one dive:
1. **C.R.U.D across the driving NLP** for both Canon and Chronicle
   lifecycles — registry, nice readers and editors, version control, an
   applied-craft graph, and A/B–Blue/Green testing of policy/prompts/skills.
2. **The commission loop**: a human clicks *create* → the librarian
   gathers the knowledge → the factory builds the asset → the human is
   notified (the bell) → v1 stands in the registry.
3. **The Ask tab retires**; «Governance» takes its place — the logical
   room to CRUD what governs Canon and Chronicle.

This is the largest of the week's three items; Farm and Stable lifecycle
enhancements follow it, and together they close the loop: every working
organ of Orreth managed, visibly, from the human's seat.

## 2. The laws

1. **The registry is a projection, never a second truth** (rule 7). Every
   craft object already lives on the signed log with lineage; the room
   READS. Delete the room and nothing is lost; rebuild it and nothing
   drifts.
2. **Two lifecycles, one law of change.** Chronicle craft (the adaptive
   layer) changes through grace's proposal grammar — sibling versions,
   evidence, a word at a gate. Canon craft (the firmware) changes through
   a RELEASE that **cuts a new epoch**: 0041's ceremony IS the firmware
   lifecycle, the fingerprint IS the build-stamp, and the drift watchdog
   guards it (JB's lock, 2026-08-03). Nothing anywhere silently
   overwrites.
3. **The human's edit wears the same grammar** (JB's lock): an edit in
   the room lands as a versioned sibling with lineage and is approved by
   the human's own word in one motion — edit and word land together.
   Outsiders see ONE law of change, no privileged side door.
4. **What drives the machine is readable by the humans it serves.** Every
   prompt, skill, policy, rubric, and charter: visible, versioned,
   diffable, searchable. The trust gap closes by showing, not claiming.
5. **The argument is a first-class action.** From any craft object the
   room can open a 0043 experiment — arms as cryptographically named
   machines, the split on a human's word, standings by the log join. For
   Canon, Blue/Green = two named machines standing at once, and the
   cutover is a human gate.
6. **Creation may be commissioned.** "Create me a skill for X" rides the
   objective grammar: the librarian gathers, the factory builds, grace
   stages, the bell rings the human, and v1 stands in the registry with
   its whole birth on the record.
7. **Scale is a design constraint, not a hope.** Categories, lifecycle
   lenses, search, and collapsed worldlines keep the room legible at
   thousands of objects.
8. **The craft is served, not copied** (JB's addition, 2026-08-03).
   External flows — LangGraph and kin, keeping their own deterministic
   shape — ACQUIRE craft by reference through the SDK under a lease:
   `head` (moves with adoptions) or `pinned` (exact version; advancing a
   pin is a governed act — the Canon/Chronicle split as a consumer
   contract). The door may serve an experiment arm when an argument
   stands (deterministic split by caller DID — an external flow joins a
   governed A/B without changing shape). Every serving is on the record;
   refusals wear the one face; rule 5 holds — the craft is data on the
   log, and the thinking stays on the caller's side.
   **And the principle is general** (JB, same day): it applies to the
   Farm, the Stable, and Skills alike — the SDK serves Orreth's
   *gateways, inventories, and registries* as infrastructure à la carte.
   Nobody is forced onto `orreth.agent`; it is one honest consumer of
   the doors, not the toll booth. Wherever the consumer stands, the CRUD
   itself always lands in the one place — the firmware and the brain's
   signed shelves — which is exactly why every consumer inherits the
   governance for free.
   **Law 8's four riders** (the architect's what's-missing pass,
   2026-08-03):
   - *A consumer is a citizen*: an external flow persists its keypair and
     re-joins as the same self (rule 1 — the F1 mayfly lesson, kept at
     this door too). Identity is what makes "LangGraph agents live
     forever" true instead of ironic.
   - *One run, one resolution*: the SDK resolves craft at flow start and
     carries it through the run; the run's record names the version. We
     never inject nondeterminism into a deterministic flow.
   - *Declared failure posture*: unreachable registry → serve the cached
     signed copy LABELED stale, or refuse — the consumer declares which,
     per acquire. Never silent staleness.
   - *No secret experiments on strangers*: arm-serving is opt-in at the
     lease. Inside your own universe it is governance; across a boundary
     without consent it is something else.

## 3. The room (the glass)

«Governance» replaces Ask. Layout:

- **The category rail**: Prompts · Skills · Policies · Rubrics · Charters
  · Manifests — each with counts; a lifecycle lens (Canon | Chronicle |
  all) crossing every category; search over names, tags, and content.
- **The shelf view**: objects as collapsed worldlines — name, current
  head, version count, lifecycle badge, who wears it, last-changed; click
  to open.
- **The reader**: rendered + raw, with the lineage timeline (every
  sibling, its evidence, its word) and a diff view between any two
  versions.
- **The editor**: propose-a-sibling — the one-motion edit+word of law 3;
  refusals loud; nothing saved outside the grammar.
- **The actions**: propose edit · open an argument (A/B) · commission
  (the factory loop) · retire (a posture, never a deletion).
- **The machine panel**: the current epoch's name, its Canon manifest,
  any staged release, Blue/Green state, the watchdog's last word.
- **The applied-craft graph**: the brain's grammar turned on the craft —
  which floors and residents wear which words, adaptive applications
  flowing live. A projection, never a second truth.

## 4. The registry (the wire)

The worker composes `/governance` the way it composes `/observatory`:
one payload, cached briefly — the index built from the shelf
(`wire_assets` lineage chains), the Canon set from the epoch manifest,
charters and rubrics from their records. The parked write-time re-hash
question (rule 9) gets its formal revisit at sp2's authoring door — the
first place humans author records through the glass at volume.

## 5. The spoonfuls

| # | Spoonful | Proof |
|---|---|---|
| 1 | **The registry & the room** — `/governance` payload; the tab replaces Ask (gather/dispatch duties formally moved to residents/parlor); categories × lenses × search; readers + lineage timelines + diffs, scale-ready. **AND THE CANON EXTRACTION** (the architect's find, 2026-08-03): the residents' driving prompts live today as string literals in worker code — invisible firmware. They are lifted into signed Canon records the epoch manifest names, or the room reproduces the exact trust gap it exists to close, behind nicer glass · **LANDED 2026-08-03**: THE EXTRACTION RAN — the four LLM firmware prompts (assay-judge · graduation-judge · graduation-mentee · resident-voice) left the code as ⟦slotted⟧ templates, landed as becky-signed Canon records, and the worker now READS its own firmware from the shelf (`craft()`, the literal genesis-only); `/governance` serves the index (a projection, bodies read through the records door); the room stands where Ask stood — 12 objects, categories × lifecycle lenses × search, readers with worldlines · **PROVEN AS A HUMAN**: vera's judge prompt read in the glass wearing CANON; `fingertip-default` v1→v2 diffed — the improver's real adopted change (max_cycles 2→5, `adopted_from` named) readable line by line; the reel rehomed to Pulse, gathers to the Requests bands, nothing orphaned (two init breaks from the retirement caught by the glass's own errors and healed) | every prompt, skill, policy, rubric, and charter on the rig visible and diffable as a human — INCLUDING the residents' own firmware; the Ask tab gone with nothing orphaned — ✓ RAN |
| 2 | **The editors & the one law** — propose-a-sibling from the glass, one-motion human word; Canon objects refuse the Chronicle door and point to the release; the re-hash question revisited on the record · **LANDED 2026-08-03**: `craft-edit` rides the request queue (the click IS the word — no second gate); grace signs as the shelf's keeper with the human's authority named in the body; the sibling wears `adopted_from` + `derived_from` and becomes head; the room re-reads at once · **PROVEN AS A HUMAN**: fingertip-default edited in the glass (max_obs 3→4 + a worldline note) → v3 landed, the v2→v3 diff showing the authority line verbatim; Canon (assay-judge) refused with the release pointer; malformed JSON refused loudly — both ending "Nothing changed" · **THE RE-HASH REVISIT ON THE RECORD** (docs/decisions): the park HOLDS — glass edits are worker-minted, hash-correct by construction; the trigger stays external ingestion (0013) | edit a real Chronicle prompt as a human: sibling + lineage + word in one motion; the old version stands behind it; an attempted silent save refuses loudly — ✓ RAN |
| 3 | **The Canon release** — the release ceremony from the room: stage a Canon change → a new named machine cut on the human's word → attestation + watchdog stay honest; Blue/Green = two standing machines, gated cutover · **LANDED 2026-08-03**: the fingerprint now COVERS THE FIRMWARE (the machine's name cites its own driving words); `on_release` — pending stages with BLUE (the standing epoch) and GREEN (the would-be head) named on the card; the human's word lands the becky-signed sibling with `released_by` verbatim, the worker re-reads its shelf, and the next beat cuts the name with the word standing ("release" joined the adoption vocabulary, sim + wire, suite 291) · **PROVEN BOTH WAYS, JB'S OWN HAND**: the wordless widening was ACCUSED by the watchdog ("the Canon moved with no adoption behind it", req-416 — acknowledged with the story); then JB himself cut the first firmware release (req-417 — assay-judge learns to quote the yardstick it judged by, born from the 0.12 verdict) and the machine renamed ff728ca5 → a8c4cd1b with the watchdog SILENT · +JB's find: reqRow lacked the bell's approve/decline fallback for unknown staged kinds — one fallback now, both faces | change a Canon object as a human; watch the epoch's name move ONLY through the ceremony; the watchdog accuses any other path — ✓ RAN, both halves |
| 4 | **The applied graph & the argument** — the brain-grammar craft overlay (who wears what, live); "open an argument" from any object → a 0043 experiment with arms as named machines · **LANDED 2026-08-03**: the wearers map (declared from the code's own structure — every object names who wears its words) + the ⟟ applied-craft view (words left, wearers right, edges) · the ROWS' FLOOR JOINS THE REGISTRY (JB's "should I see skills?" found the coverage gap: the registry read one floor while skill-summarize-a-floor-s-week v2, routing-standard v11, record-classes, and distillation-dials lived at e:rag — Skills·1 and Policies·1 now real chips, the tournament's 11-version argument diffable) · the declared rubrics READ (JB's second find — rows now open a reader naming the yardstick's law) · ⚖ "open an argument" stages a real experiment (proven by probe: req-418 armed and staged, "the split waits for you — each arm is a NAMED machine") | the graph shows a real prompt's wearers; one click opens a real A/B on a real asset, split on JB's word — ✓ RAN (req-418 at the gate) |
| 5 | **The supply line** — the SDK acquire door (law 8): resolve craft by name under a lease, head or pinned, arm-serving when an argument stands, servings on the record; the applied graph gains EXTERNAL wearers | a real LangGraph flow acquires a governed prompt by reference — its shape unchanged — and wears an experiment arm without knowing; the run's record names the exact version that drove it |
| 6 | **The commission** — create-button → objective → librarian gathers → factory builds → grace stages → the bell rings → v1 in the registry | JB commissions a real skill from the glass and is rung when it stands, its whole birth walkable on the record |

## 6. Gap register (§11 law, standing)

*found → written → homed.* Empty at design time — the build will fill it.
