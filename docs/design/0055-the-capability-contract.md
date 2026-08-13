# 0055 — The Capability Contract (worlds that bring their own rooms)

<!-- PROVENANCE: Fable 5 (claude-fable-5) — drafted 2026-08-13 from JB's
     vision, given the night the desk finished: "something along sdk lines
     that brings its own UI elements to join capabilities when started..
     the Capability tile used as a start, stop, continue.. Orreth as a
     product foundation can then agentically manage elements like
     infrastructure and the feature elements." -->

**Status: 🟢 OPENED 2026-08-13 — all four locks landed (AskUserQuestion,
JB's hand): L1 ELEVEN panel kinds — the desk's six + 0028's four + a
sortable TABLE (BI worlds will want it early) · L2 manifest = chronicle
craft, the vocabulary canon · L3 stop rests the words always, processes
on "fully" · L4 repo-local v1 — with JB's emphasis VERBATIM: "Orreth must
be able to support bring your own package, it's kind of one of the big
ones. We should track this when we start moving orreth to cloud" — BYOP
is a first-class cloud-phase commitment on the 0042 trust machinery, not
a footnote. His word on pace: "Let's NOT wait long on proving this out."
Building.**

## 1. The frame — the Foundation and the worlds

JB's product line, made canon: **Orreth is the Foundation** — identity,
memory, governance, the Farm, the Stable, the meters, the glass. A
**Capability** is an applied agentic world that leverages it: its own
residents, craft, Chronicle, and purpose. The Capabilities pull is the
portal where installed worlds live; the Machine below, the worlds above.
This is 0053's two-book separation at the product level — the Foundation
is Orreth; the capabilities are what Orreth *does*.

## 2. The decoupling today (honest)

The Trading Desk proved every organ a capability needs, but its seams are
hand-tied: its view is coded INTO the glass (`renderDesk`), its supply
door (`/desk`) is worker code, its crew is named in `dev.sh`, its
lifecycle controls are bespoke (`desk-watch`/`desk-ask`). Perfect as a
prototype; wrong as a pattern — a second capability today would mean
editing the Foundation. The contract ends that.

## 3. The contract — what a Capability IS

A capability is a **signed package of five declarations**, and nothing in
the Foundation names it:

1. **Identity & floors** — its ecosystem + fields, grown through the
   shipyard gate like any floor (`e:desk/f:charles` is the pattern);
   its residents join at their own gates (becky-per-floor).
2. **Crew** — the host processes it needs (agents, stalls). Declared,
   not hard-wired: the Foundation's crew-keeper starts/stops them from
   the declaration (dev.sh's `deskcrew` generalized).
3. **Craft** — its prompts/personas/policies on the shelf, planted from
   its own genesis module, edited only at gates (0045's law).
4. **Chronicle** — its records on its own floors, classed (0039), read
   by projection only.
5. **THE CAPABILITY MANIFEST** — the new piece: one signed record
   declaring the world to the portal:
   - the **card**: name, emoji, resident, law line, landing chip;
   - the **view**: its rooms as TYPED PANELS the glass renders blind —
     0028's workspace vocabulary (stat · bars · list · doc) extended
     with the desk's proven kinds: `tabs`, `markdown`, `chart`
     (price/series specs → the chart engine), `strip` (stage checks),
     `controls` (reins: inputs + governed-request buttons), `download`;
   - the **doors**: which supply routes serve its data (composed
     worker-side from its records, the `/desk` pattern generalized to
     `/capability/<key>`);
   - the **lifecycle verbs** (§4).

**The law that makes this safe**: a capability brings *declarations*,
never code. The glass renders typed panels blind (0028); foreign JS
never loads into the Console. "Brings its own UI" means bringing the
*description* of its rooms — the Foundation owns the rendering, so every
capability inherits the glass's laws (one truth, honest confessions,
rule 11) for free.

## 4. The tile as the lifecycle lever — start · stop · continue

JB's ask, made mechanism: the world's card carries its lifecycle.

- **States — CORRECTED TO JB'S MODEL (2026-08-13, his words the law)**:
  the state is the SERVICE'S, never the schedule's — "the watchlist is
  content; it must never drive the state of the architecture."
  `running` (crew up, answering; the watchlist is an annotation — "· N
  walks" or "· watchlist empty") · `stopped` (paused by the human's
  word; the watchlist PRESERVED whole) · `shut down` (crew halted;
  every record survives). The original tending/resting law conflated
  service with schedule — worse, it read cancelled-watch TOMBSTONES as
  state; JB caught it live.
- **Verbs**: **stop** (pause — gateless, rule 11; nothing walks, nothing
  lost) · **continue** (resume continuous operation, RECOVERING the
  preserved watchlist — staged with terms, resuming spend is a
  consequence) · **stop fully** (shut down — gateless; the crew halts)
  · **start** (raise a shut-down desk — staged). A no-op verb answers
  honestly on the spot. The world's posture is its own record
  (`desk_world`, head wins) on its own floor; the tend loop rests WHOLE
  while paused and recovers everything on continue.
- **Shut down reaches the INFRASTRUCTURE (JB's correction, 2026-08-13:
  "the idea behind shut down is to save on infrastructure costs")**: a
  capability declares its FLOORS like its crew — the eco shared, each
  field its own — and stop-fully halts the world's own hulls (docker
  stop; at cloud, the instance) while shared floors stand for the
  siblings. Records survive by construction (pg + volumes); start raises
  the hull first, waits for its health, then the crew, and the keepers
  re-earn their stalls over the next beats. The janitor never outranks
  the word: replant leaves an exited hull resting. Two ordering laws
  earned live: a resolution must never die with the floor it rides
  (resolve first, then stop), and **lifecycle words live on ground that
  survives the world** — the universe floor — because a shut-down world
  must still hear its start.
- Verbs are governed requests riding the UNIVERSE floor, and their
  gates SURFACE ON THE TILE (the staged verb with its terms and the
  decision beside it) — a gate in a room the human never visits is
  indistinguishable from a broken button (JB's find).

## 5. The Foundation manages the rest, agentically

- **Infrastructure**: a capability's declared infra (stores, floors,
  stalls, later cloud pieces) is an ESTATE concern — allen's charter
  interrogates the declaration the same way it interrogates a
  deployment (0037/0039: the charter IS the storage map). In cloud
  phase, capability install = allen provisioning from the manifest.
- **Feature elements**: a capability's craft evolves through the same
  loop as the Foundation's — thumbs, craft-edits, commissions, the
  studio (0047/0048). A capability that wants a new skill asks; the
  machine researches, drafts, and waits at the gate.

## 6. The SDK's side

`orreth-agent-sdk` grows a `capability` module: `declare(manifest)` files
the signed manifest at install; `panels(...)` helpers compose typed-panel
declarations; the existing `FieldClient`/`GovernedThink`/`acquire` carry
the rest (they already do — charles uses nothing else). A capability
built against the SDK **joins the pull when its crew starts**: the
manifest lands, the portal lists it, the doors serve it. Uninstall =
the manifest's `retired` sibling; the Chronicle stays (append-only).

## 7. The migration proof (when built)

**sp1 LANDED + THE ACCEPTANCE PASSED 2026-08-13.** The manifest exists as
chronicle craft on the shelf (`capability-trading-desk` v1 — the first
dict-bodied asset, planted by the same beat as every sentence); the
portal's world list is composed FROM manifests (genesis fallback so the
portal is never blank); the supply door serves panel-ready fields; and
THE PANEL WALKER renders the desk's declared rooms blind — screenshot
against the bespoke version: pixel-for-pixel, picker to charts to tabs.
`renderDesk` no longer exists in the glass. Live lesson on the record:
a "patient retry" that files a new join per cycle is a 41-card flood —
patience is ONE long-lived request, held open and polled. **sp2 LANDED + PROVEN LIVE 2026-08-13 — the tile is the lever.** The crew
is declared in GENESIS (commands never execute from the shelf's editable
copy — a craft-edit must never become command injection; the repo is the
trust boundary). The verbs ran their whole cycle in one sitting: stop
(gateless, words rested) → continue (staged with terms, approved, words
re-stood) → stop-fully (crew HALTED, tile honestly DARK) → start (staged,
approved, crew raised, charles back at his gate on one patient card) →
the human's chosen state restored. The tile and the world header wear the
state chip (tending · resting · stopped · dark) and exactly the verbs
that state allows. **sp3 LANDED — THE SECOND WORLD PROVED THE CONTRACT, 2026-08-13.** charlene
arrived as exactly what the contract promised: a prompt set (13 reference
prompts, AST-verbatim) + a manifest + a field — **not one line of glass**.
Her floor grew through the field-join door (:4521, the port her manifest
predicted); her minds saddled and her stalls planted at four gates; her
craft planted by the same beat as every sentence; her tend joined through
HER OWN gate (becky-per-floor's second resident); and her first walk —
"the human asks: charlene, walk BTC-USD" — ran the whole sixteen stages
to an Overweight with her charts, her stages, her tabs all INHERITED.
The landing groups the two tiles under THE TRADING DESKS; the door is
per-world (?key=); the SDK's `capability.manifest()` guards the eleven
kinds at build (suite 23). The human drove her within minutes (his own
ETH ask on her queue). Live lesson: a GENERATED Python module must
IMPORT-EXECUTE in its check, never merely parse — json.dumps spells
`true`, and the worker crashed on it until caught. chad (options) is now
a third prompt set away; ML/BI/ProdDev worlds have their pattern.

The Trading Desk re-declared UNDER the contract — its view expressed as
typed panels, its crew as a declaration, its verbs on the tile — with
zero behavior change. The desk stops being a special case the day the
contract can carry it; that is the acceptance test. charlene and chad
then arrive as manifests + prompt sets, never as glass edits.

## 8. The locks staged for JB

- **L1 — the panel vocabulary**: which kinds ship in v1 (proposed: the
  desk's six — tabs · markdown · chart · strip · controls · download —
  plus 0028's four).
- **L2 — manifest class**: Canon asset (a release changes it) vs
  Chronicle asset (craft-edit at will, history kept). Proposed: the
  MANIFEST is chronicle-class craft; the PANEL VOCABULARY is canon.
- **L3 — lifecycle semantics**: does **stop** halt the crew processes,
  or only the standing words (processes idle)? Proposed: words always;
  processes too when the human says "fully".
- **L4 — install source**: v1 = repo-local packages only; signed
  third-party packages wait for the deed/trust machinery (0042) at the
  cloud phase.

## 9. Honest boundary

- This is DESIGN; nothing here is built. The desk stays hand-tied until
  the migration proof runs under JB's locks.
- Multi-login / per-human capability visibility rides the identity work
  (0054 §5b) — cloud phase.
- Agentic infra management beyond the dev rig is allen's cloud-phase
  charter; on this laptop it is process supervision, honestly.

## 10. Convergence

| Organ | What it supplies |
|---|---|
| 0028 | typed panels rendered blind — the UI law this contract extends |
| 0040 | the Faculty: installable signed packages — the same idea, whole-universe scale |
| 0054 | the prototype and every proven seam (floors, crew, craft, doors, reins) |
| 0037/0039 | allen's charter as the infra interrogation; record classes |
| 0042 | signed packages from outside, when install opens beyond the repo |
| 0049 §C2 | the Capabilities pull this contract fills |
