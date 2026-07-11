# 0028 — Workspaces & the Improvement Engine

*Design draft — proposed by Fable 5 (design owner), from the Universe-Brain session
(2026-07-10, `../vision/the-universe-brain.md` §8–§9). Two organs of one idea: the
resident authors its own room in the glass, and one agent never stops improving the
universe's behavioral assets from outcome evidence. Discharges 0024's deferred
medium-lane Console badge and 0027's deferred factory-RL-over-templates.*

---

## Why this is a keystone

The Console's law since 0020: *decoupling is the card, not the code* — the glass
renders whatever a card declares. §8 completes it: the parlor dialog grows to full
screen and becomes the resident's **workspace**, with room for actions and rich
output — the resident the author of its own room, the glass still generic. And §9
closes the oldest loop in the vision: *"one agent is always improving them"* — the
factory (0011) is not just where incarnations are stamped; it is where skills,
prompts, and templates are **continuously refined from outcome evidence** (0005's
rollups feeding an improvement loop). The forever-improving agent, made mechanism.

---

## 1. The workspace — the resident's own room (§8)

- **The card declares it** (0020 §2 grown): a calling card gains `workspace: true`.
  The glass shows the expand handle only when declared — a new resident brings its
  room without a line of Console code.
- **The room is an ask, like everything else.** Expanding posts `verb:"workspace"`
  to the parlor queue; the resident composes its panels **from state it may read**
  (parlor facts — its own authority) and resolves `{workspace:{panels:[…]}}`.
  Humans never read the world; the workspace is fetched FOR them, on the record.
- **Panels are typed data, rendered blind**: `stat` (number tiles) · `bars`
  (label+value bars — the chart, CSS-only) · `list` (rows with meta) · `doc`
  (formatted text — the librarian's rich output). The glass knows the four kinds;
  the resident owns the content.
- **The parlor's move**: ⛶ pulls the pane to full width (the drawer's cycle,
  sideways); the thread and chips stay live below the panels — the workspace is
  the dialog grown up, not a different place.
- **The marker lane badge (0024 discharged)**: workspace panels carry severity
  chips; medium+ wear amber — pending co-review is visible at a glance.

## 2. The improvement engine — one agent, always (§9)

- **The improver is a standing incarnation** (R8, 0027's machinery reused): no
  completion condition, beating on its floor, factory-stamped with a birth
  certificate. Its job: read the outcome evidence and keep the behavioral assets
  honest.
- **Evidence is receipts, never vibes**: RunRecord rollups (success rate, cost),
  critic markers (0024/0027 — where review graded medium/high), and parked intents
  (0014/0015 — where the breaker fired). Every proposal derives from the evidence
  records it cites (ContentHash refs, 0023's discipline).
- **A proposal is a new VERSION, never an edit**: the improver produces a new
  content-addressed artifact (chassis profile, workflow template, prompt), lineage
  through `derived_from` to the version it would succeed plus the evidence — the
  old version is never rewritten (a sibling, never a silent successor — 0011's
  locked law, applied to assets).
- **Nothing grades its own yardstick**: the improver PROPOSES; the reviewing organ
  grades the proposal with a critic marker (author ≠ proposer); the R6 lanes route
  adoption. Refused-at-save checks run before anything stages — a malformed
  proposal never reaches the queue.
- **Adoption is on the record**: an adopted version becomes the active asset via
  an adoption record deriving from the proposal; the ledger shows the whole chain
  — evidence → proposal → grade → adoption.

## 3. What lands this spoonful

| Piece | Where | Status |
|---|---|---|
| Card `workspace` flag + four panel kinds | sim `parlor.py` + `window.html` | this dive |
| Workspace composition for the embodied residents | worker (`parlor_facts` reuse) | this dive |
| Full-screen parlor move + blind panel renderer | `window.html` | this dive |
| Marker severity chips (medium+ amber) | workspace panels | this dive |
| Improver: evidence → proposal → grade → lanes → adoption | sim `improver.py` | this dive |
| The improver standing on the wire (kind `improvement` in the queue) | worker | this dive |
| Skill/prompt assets beyond templates | ledger — with the SDK flavor | deferred |
| True RL (learned policy, not rules) | model plane, when fueled | deferred |

## 4. Decisions

**Pre-locked by JB:** R6 lanes route everything graded · R8 standing incarnations ·
0011's sibling-never-successor · 0020's card-is-the-decoupling.

**Closed by the design owner (JB may veto):** panels are four typed kinds rendered
blind · the workspace is fetched via the parlor queue (never a privileged path) ·
the improver's v0 policy is deterministic rules over evidence (thresholds), the
learned policy waits for the model plane · one open proposal at a time per asset —
no proposal storms.

**Locked by JB (2026-07-11, AskUserQuestion):** all four embodied residents get
rooms this spoonful (librarian · becky · charlotte · ada) · improvement lanes are
graded by kind — a parameter **nudge grades medium** (co-review + notify, adopted
with a loud record) and a persona/prompt/shape **rewrite grades high** (waits for
the human), the grade authored by the governance seat, never the improver · **one
improver stands on the universe floor** — one mind for the universe's assets,
reading the subtree's risen evidence.

---

*The glass stays dumb, the residents get rooms, and somewhere on the universe
floor an agent that never sleeps reads every receipt the work leaves behind —
and quietly proposes the universe's next self.* 🥂
