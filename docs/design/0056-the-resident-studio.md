# 0056 — The Resident Studio (the family gets rooms)

<!-- PROVENANCE: Fable 5 (claude-fable-5) — drafted 2026-08-16 on JB's word:
     "extend the EXISTING workspaces, not modals" (2026-08-14), "cost metrics,
     performance — really show us humans you are aware of this resident…
     they are family after all", and the Objectives musing of 2026-08-16:
     "if humans can just ask for these things through a Resident, why have
     this?" This charter is the answer to all three. -->

**Status: 🔨 OPEN — all four locks landed by JB 2026-08-16:**
**L1 = ALL TEN residents at once (his word over the recommended three:
"the family whole from day one" — thinner rooms each, one template) ·
L2 = both doors (rail card + parlor) · L3 = spend · runs/success ·
last verdict · age · L4 = ANY question a resident answers (the standing
word carries the question as data).**

## 1. The wound

Residents have workspaces (0028) but they are thin rooms: a human meets
charles's *reports* in the capability portal, vera's *verdicts* in the
Observatory, the librarian's *answers* in the parlor — but never the
resident whole. CortexObserver set the bar JB expects: one room per agent
where its prompts, skills, schedules, minds, and work are all visible and
governable. Meanwhile the Objectives view scrolls forever — machinery-era
UI from when watching cards *was* the product — and JB has named the
deeper truth: in a conversational universe, "Objectives" is not a place.

## 2. The shape — one renderer, every room

A resident's workspace is a ROOM rendered by the **same twelve-kind panel
vocabulary as capabilities** (0055's walker; the flow engine of
2026-08-16). Residents and worlds converge on one glass grammar — no new
renderer, no per-resident code. Sections, each an ordinary panel:

| Section | Panel kinds | Source of truth |
|---|---|---|
| **THE VITALS** — the family truth | stat · bars | the universal meter (0019, per-DID): lifetime tokens/usd · runs + success · vera's verdicts where judged · age and worldline highlights · lessons learned |
| **THE WORK** — what I am pursuing | flow · list | active objective drawn LIVE by the flow engine; recent walks with citations |
| **THE WORDS** — my firmware | list + craft-edit doors | prompts/skills/personas from the shelf. **Mode-gated at the door** (already enforced): dev = editable siblings; prod = read-only, change rides the release ceremony (0045) |
| **THE SCHEDULES** — my standing words | controls | scheduled-ask CRUD (machinery live since 2026-08-15; the yardstick was its first customer — residents extend `what`) |
| **THE MINDS** — what I think with | table | ada's stalls this resident may saddle; active mind per class |
| **THE RELATIONS** — where I stand | flow | resident ↔ floor ↔ craft ↔ minds ↔ recent objectives, on the same DAG engine |

Entry: the resident's card (rail and parlor) grows a door into the room —
no modals (JB's correction, on record).

## 3. The Objectives transplant — not a demolition

Objectives stay **records forever** — they are the Chronicle's spine. The
standalone *view* demotes as its three duties move to better homes:

- *what waits on me* → the Inbox already owns it;
- *what a resident is pursuing* → THE WORK section, drawn live;
- *what happened* → the Chronicle, walkable from any citation.

The Objectives tab survives this dive untouched; it retires only when JB
notices he has not opened it in weeks — disuse is the verdict, never a
redesign's opinion (his own word: "not saying remove just yet").

## 4. The locks staged for JB

- **L1 — the first residents**: which rooms build first? (Proposed:
  charles — richest vitals; the librarian — the ask lane's face; vera —
  the yardstick's judge. The rest follow the proven template.)
- **L2 — the door**: where the human enters — the resident card on the
  left rail, the parlor header, or both?
- **L3 — the vitals' spine**: which numbers lead? (Proposed: lifetime
  spend · runs/success · last verdict · age — the four a parent would ask.)
- **L4 — schedules' reach at v1**: yardstick-style asks only, or any
  parlor question a resident can answer? (Proposed: any question — the
  machinery already carries `what` as data.)

## 5. Honest boundary

- v1 rooms read from instruments that exist today; no new collection.
- Prod read-only is enforced at the craft-edit door, not per panel — a
  panel forgetting the law cannot break it.
- The relations graph draws what the records already know; inferred
  edges are labeled inferred.

## 6. Convergence

| Organ | What it supplies |
|---|---|
| 0028 | the workspaces this dive grows into rooms |
| 0055 | the panel vocabulary and walker — one renderer, every room |
| 0019 | the universal per-DID meter under THE VITALS |
| 0045 + mode (2026-08-16) | the edit doors and the prod read-only law |
| scheduled asks (2026-08-15) | THE SCHEDULES' machinery, first customer proven |
| the flow engine (2026-08-16) | THE WORK and THE RELATIONS, drawn live |
