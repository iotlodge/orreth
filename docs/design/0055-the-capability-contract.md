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

- **States**: `tending` (crew up, standing words active) · `resting`
  (crew up, nothing due) · `stopped` (the human's word) · `dark` (crew
  down — honest, never hidden).
- **Verbs on the tile**: **start** (stage the crew + standing words —
  gated, it's a spend) · **stop** (rule 11 — immediate, gateless, the
  whole purpose rests) · **continue** (resume from the stopped word —
  gated once, then standing again).
- Verbs are governed requests to the capability's own floor — the
  desk-watch cancel pattern generalized to the whole world. The
  Foundation's crew-keeper enacts them on processes; the capability's
  residents enact them on standing words.

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
that state allows. Remaining in this dive: the SDK's `capability` module
+ a SECOND WORLD to prove generality (charlene is the natural one).

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
