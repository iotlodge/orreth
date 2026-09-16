# The Experience Specs — the Playwright's book

**Status: v0 (P0 sp3, 2026-09-16).** Distilled from the locked Experience
Charter (0001); walked by the Playwright per its charter. Each spec:
the walk in human words, the bar, the evidence. The OLD GLASS column is
the honest "before" — most specs are EXPECTED to fail there; that failure
is the reason the rearchitecture exists.

| Id | Proves | The walk (human words) | The bar | Old glass |
|---|---|---|---|---|
| **SPEC-TOOLS-01** | the charter's first-class bar | Ask in chat: "What's the temperature outside?" | A real temperature arrives in the reply, in plain words | expected FAIL |
| **SPEC-FULL-01** | P14 · verbatim recall | Ask a resident to acquire a short text, then ask "repeat every word you acquired" | Every word comes back, complete, none summarized away | expected FAIL |
| **SPEC-JOURNEY-01** | P7 | Submit any ask; watch beneath it | Soft text names who took it, on which scope, and when it completed | expected FAIL |
| **SPEC-SOFT-01** | P5 | Submit an ask, immediately start a second in the same window; wait | Neither blocks the other; completion arrives softly; clicking renders the result right there | expected FAIL |
| **SPEC-ESC-01** | P4 | Open any pull/panel; press [Esc] | One keystroke returns the top-level view, from anywhere | expected FAIL |
| **SPEC-SCOPE-01** | P6 | Type an ask containing "between last Monday and today" | The time scope visibly reflects on the chat's clock/axes without any click | expected FAIL |
| **SPEC-FANOUT-01** | P14 fan-out | Select two residents; send one ask | Two distinct, labeled results; each downloadable; "summarize together" offered on demand | expected FAIL |
| **SPEC-LIFE-01** | P13 | Open the lifecycle surface while work runs | Queued, in-flight, and completed all visible; every row opens its result in place | expected FAIL |
| **SPEC-SCHED-01** | P16 | Open a resident's card | Every schedule it runs is listed — human, role, and kernel; the kernel-critical one refuses edit with plain words | expected FAIL |
| **SPEC-LENS-01** | P17 | Change a setting in one pull; look at another surface showing it | The change is already there — no refresh, no navigation | expected FAIL |
| **SPEC-CLEAR-01** | P14 clear≠erase | Clear the chat display; ask "what did I ask you earlier?" | The display is clean AND the resident recalls — nothing was erased | expected FAIL |
| **SPEC-L2-01** | P12 | Ask for a consequential change | "Are you sure…" arrives in the chat; cancel is default; yes needs a deliberate click, never the return key | expected FAIL |
| **SPEC-WORDS-01** | P18 | Read every word on the landing surface as a newcomer | No jargon a newcomer can't parse; actions say what saying yes will do | expected FAIL |
| **SPEC-FEEL-01** | the cockpit itself | Sit down cold; find chat, results, and what's running | No navigation needed; everything reachable from the landing page; it feels like a place, not an admin panel | expected FAIL |

## Walk records

### Before-walk #1 — the old glass, 2026-09-16 (P0 sp3)

Walked by the Playwright against the old world (v0.72.520, the polling
rig) — results recorded in `baselines/before-walk-2026-09-16.md`.
