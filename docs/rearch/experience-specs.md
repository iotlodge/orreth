# The Experience Specs — the Playwright's book

**Status: v0 (P0 sp3, 2026-09-16).** Distilled from the locked Experience
Charter (0001); walked by the Playwright per its charter. Each spec:
the walk in human words, the bar, the evidence. The OLD GLASS column is
the honest "before" — most specs are EXPECTED to fail there; that failure
is the reason the rearchitecture exists.

| Id | Proves | The walk (human words) | The bar | Old glass | Bridge v0 (after-walk 2026-09-17) |
|---|---|---|---|---|---|
| **SPEC-TOOLS-01** | the charter's first-class bar | Ask in chat: "What's the temperature outside?" | A real temperature arrives in the reply, in plain words | expected FAIL | **PASS** w/ friction — 69.7 °F arrived in plain words (first from her notes of the day, fresh on request); raw markdown; no sign a tool ran |
| **SPEC-FULL-01** | P14 · verbatim recall | Ask a resident to acquire a short text, then ask "repeat every word you acquired" | Every word comes back, complete, none summarized away | expected FAIL | **PASS** verbatim half (every word back) · NOT BUILT acquire half |
| **SPEC-JOURNEY-01** | P7 | Submit any ask; watch beneath it | Soft text names who took it, on which scope, and when it completed | expected FAIL | **FAIL** — who is named; scope never; completion time never (sp5) |
| **SPEC-SOFT-01** | P5 | Submit an ask, immediately start a second in the same window; wait | Neither blocks the other; completion arrives softly; clicking renders the result right there | expected FAIL | **PASS** — second ask while the first streamed; both whole in 11 s |
| **SPEC-ESC-01** | P4 | Open any pull/panel; press [Esc] | One keystroke returns the top-level view, from anywhere | expected FAIL | **PASS** — one Escape from chat + band + row → bare bridge |
| **SPEC-SCOPE-01** | P6 | Type an ask containing "between last Monday and today" | The time scope visibly reflects on the chat's clock/axes without any click | expected FAIL | NOT BUILT (expected) |
| **SPEC-FANOUT-01** | P14 fan-out | Select two residents; send one ask | Two distinct, labeled results; each downloadable; "summarize together" offered on demand | expected FAIL | **PASS** two labelled results + summarize-by-name (after wounds 2 & 3 cured) · FAIL download (no control) |
| **SPEC-LIFE-01** | P13 | Open the lifecycle surface while work runs | Queued, in-flight, and completed all visible; every row opens its result in place | expected FAIL | **PASS** (after wound 1 cured) — every row a door from the landing state; no times on rows |
| **SPEC-SCHED-01** | P16 | Open a resident's card | Every schedule it runs is listed — human, role, and kernel; the kernel-critical one refuses edit with plain words | expected FAIL | NOT BUILT (expected) |
| **SPEC-LENS-01** | P17 | Change a setting in one pull; look at another surface showing it | The change is already there — no refresh, no navigation | expected FAIL | NOT BUILT (expected) |
| **SPEC-CLEAR-01** | P14 clear≠erase | Clear the chat display; ask "what did I ask you earlier?" | The display is clean AND the resident recalls — nothing was erased | expected FAIL | NOT BUILT (expected); recall half partial |
| **SPEC-L2-01** | P12 | Ask for a consequential change | "Are you sure…" arrives in the chat; cancel is default; yes needs a deliberate click, never the return key | expected FAIL | **PASS** — "Are you sure?" in-chat, Cancel focused, Enter cancelled; Yes withheld by the Playwright |
| **SPEC-WORDS-01** | P18 | Read every word on the landing surface as a newcomer | No jargon a newcomer can't parse; actions say what saying yes will do | expected FAIL | FRICTION — u:dev · life 1 · rev N · ORRERY·BRAIN·ATLAS unparseable to a newcomer; actions plain |
| **SPEC-FEEL-01** | the cockpit itself | Sit down cold; find chat, results, and what's running | No navigation needed; everything reachable from the landing page; it feels like a place, not an admin panel | expected FAIL | **PASS** w/ friction — a place, no navigation; the open chat hides the header at small widths |

## Walk records

### Before-walk #1 — the old glass, 2026-09-16 (P0 sp3)

Walked by the Playwright against the old world (v0.72.520, the polling
rig) — results recorded in `baselines/before-walk-2026-09-16.md`.

### After-walk #1 — the Bridge v0, 2026-09-17 (P3 sp4)

Walked by the Playwright against the Bridge v0 (rearch line, c732985+),
all 14 specs, human path only — `baselines/after-walk-2026-09-17.md`
(18 screenshots alongside). Three wound-grade findings ruled wounds,
cured, and re-walked green the same day (re-walks #1 and #2 appended to
the record): the band's doors shut behind the open chat · the synthesis
misattributing the echo's words · every reply labelled "orreth" once the
roster turned over (the Bridge's residents had been ephemeral selves).
The before-walk remainder (old glass) stays owed.
