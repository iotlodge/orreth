# 0052 — The Reading Room (season 0049 · B1 + B3 + A6)

<!-- PROVENANCE: Fable 5 (claude-fable-5) — designed 2026-08-11, opened on
     JB's word, promoted by his own walk: "Find myself clicking and
     scrolling reading this and that as I navigate between objective,
     requests, etc.. no reading panes in either and why should I bounce
     around and and and.. (frustration)." The dive's one promise: the
     bouncing ends. -->

**Status: 🟢 OPENED 2026-08-11 — three spoonfuls + the judge's walk; the
closing judge is JB's own hands.**

## 1. The one-line brief

The human stands in ONE place and the things come to them: a **reading
pane** on the right holds whatever they're attending to — click a card, a
row, an id, a name, anywhere, and it opens IN the pane while the list stays
put. Every mention is a door. Everything waiting on the human lives in ONE
inbox, decidable from the pane itself. No more tab-bouncing to answer a
question the machine could have brought to you.

## 2. The Reading Pane (B1's heart)

- A persistent right rail (the parlor's geometry, the reader's purpose):
  `paneOpen(kind, id)` from anywhere renders the thing WHOLE —
  an **objective** → its Journey strip, full card, plan, questions, words,
  thumbs, report; a **request** → its card with evidence, its gate buttons
  AND voice line working in-pane; a **record** → the human record-reader
  (§3). The list you clicked from never scrolls away.
- **One rail, one attention**: opening a resident's audience (the parlor)
  takes the rail; closing it returns the reader. You attend to one thing;
  the rail is where it stands.
- **Human titles (quinn's wound)**: every pane and card leads with the
  human text of the thing; ids demote to small metadata — that are
  themselves doors.
- Decide from the pane: approve/decline/cancel/rest + the voice line, all
  present where you read — deciding never requires going somewhere.

## 3. Every mention is a door (B3)

- A linkify pass over rendered text: `req-…` ids, `sha256:…` refs, seat
  scopes, resident names — each becomes a click → `paneOpen`.
- **The record-reader**: known shapes render as sentences (a feedback
  record reads as "the human said: …, routed as …"; a verdict as "scored
  0.1 by the examiner under rubric …"; a cancellation as "stopped by the
  human's word — left undone: …"); unknown shapes render as LABELED
  structure, never mistaken for prose. Shape-sentences live on the shelf
  (speech) like all the machine's words.
- A breadcrumb trail in the pane (each hop a step back) — reading is a
  walk, and walks can retrace.

## 4. The One Inbox (A6)

- A first-class **Inbox** view: EVERYTHING waiting on the human across all
  kinds — staged gates, pending questions — in one prioritized list
  (consequence class first, then age), each row opening in the pane,
  decided there. Plus a settled-with-you drawer (what your word touched
  recently).
- The Objectives and Requests tabs keep working unchanged this dive —
  **nothing is removed yet**: the tab audit (merge/remove, the full
  *Ask · Approve · Watch · Review · Govern* re-layering) belongs to the UAT
  personas' redundancy audit + JB's lived verdict, after the room proves
  itself.

## 5. The spoonfuls

1. **sp1 — the pane**: the right-rail reader, `paneOpen`, objective and
   request rendering in-pane, decisions + voice lines working from the
   pane, parlor precedence law.
   **LANDED + PROVEN LIVE 2026-08-12.** Rule 7 for the glass: ONE card
   builder (`objCard`) and one row builder (`reqRow`) serve both list and
   pane — the two surfaces can never disagree. The near-click law
   (`nearInput`) resolves every voice-line/answer input NEAREST the click,
   so the pane and the list coexist without id wars. Proven whole as the
   human: an objective clicked open in the pane (human title leading, id
   demoted to small metadata), a plan APPROVED from the pane (req-666 ran
   to done), and a second plan DECLINED WITH WORDS typed into the pane's
   own voice line — "the welcome note should be written by the humans…" —
   the words entering the 0048 loop from the pane itself. Two live finds,
   both fixed in the walk: the pane's busy-guard was too sticky (focus
   resting on a BUTTON froze the refresh — now only a typing hand holds
   the pane still), and pointer-fidelity taught the proof to target
   elements, not pixels. Parlor precedence held: one rail, one attention.
2. **sp2 — the doors**: linkify everywhere, the record-reader with its
   shape-sentences on the shelf, breadcrumbs.
   **LANDED + PROVEN LIVE 2026-08-12.** The linkify pass walks TEXT NODES
   only (attributes never touched — handler ids stay whole): every `req-…`
   and `sha256:…` in the queue, the objectives, the pane, and the parlor's
   lines is a door. Twelve reader sentences on the shelf (suite 334→335) —
   feedback, verdicts, cancellations, gate-words, rests, referrals, plans,
   close-outs, audiences — with the unknown shape CONFESSING ("no reader
   yet; the structure below is honest data, not prose") and the miss
   speaking both truths (shortened-for-display or another floor's shelf).
   A request read in the pane shows its RAW RESULT — full refs, every one
   a door — because display-truncated refs in card text open onto the
   honest miss (a named limit: the full-ref doors live where full refs
   live). Breadcrumbs: a list click starts a fresh walk, doors push, ←
   retraces. Proven whole as the human: queue → closure card in pane
   (where the walk found my sp1 decline had routed CHARTER → REFERRED —
   "Allen was the wrong keeper", the studio reading the words exactly) →
   the full feedback ref's door → **"THE HUMAN'S WORDS": the record read
   as a sentence**, the structure honest beneath, req-675 inside it a
   door onward, the breadcrumb ready back.
3. **sp3 — the inbox**: the Inbox view, priority order, ages, the
   settled-with-you drawer.
4. **The judge's walk**: quinn sweeps the cards for regressions, but the
   closing measure is **JB's own hands** — he felt the wound, so the dive
   closes only when the bouncing is gone for HIM. (quinn's eye cannot see
   the pane — her walker reads the wire, not the rendered room; teaching
   her to read the REAL glass is the named gap she already carries.)

## 6. Honest boundary

- No tab removed, no navigation renamed this dive (§4).
- The pane reads; it does not yet EDIT craft (the governance editors keep
  their room).
- The Lists (B2 — curated worklists) wait for the inbox to exist first.

## 7. Convergence

| Organ | What it supplies |
|---|---|
| 0051 | the Journey strip the pane leads with; the reins the pane carries |
| 0050 | the shelf the shape-sentences join; /sentences serving the reader |
| 0048/sp3 words | the voice lines the pane keeps beside every decision |
| 0020 | the right rail's geometry and its one-attention law |
| 0030 | the seat this room finally furnishes |
