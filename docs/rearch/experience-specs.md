# The Experience Specs — the Playwright's book

**Status: v0 (P0 sp3, 2026-09-16).** Distilled from the locked Experience
Charter (0001); walked by the Playwright per its charter. Each spec:
the walk in human words, the bar, the evidence. The OLD GLASS column is
the honest "before" — most specs are EXPECTED to fail there; that failure
is the reason the rearchitecture exists.

| Id | Proves | The walk (human words) | The bar | Old glass | Bridge v0 (after-walk 2026-09-17) |
|---|---|---|---|---|---|
| **SPEC-TOOLS-01** | the charter's first-class bar | Ask in chat: "What's the temperature outside?" | A real temperature arrives in the reply, in plain words | expected FAIL | **PASS** w/ friction — 69.7 °F arrived in plain words (first from her notes of the day, fresh on request); raw markdown; no sign a tool ran |
| **SPEC-FULL-01** | P14 · verbatim recall | Ask a resident to acquire a short text, then ask "repeat every word you acquired" | Every word comes back, complete, none summarized away | expected FAIL | **PASS** verbatim half (every word back) · acquire half BUILT (P5 sp1: the librarian's `acquire` tool; recall by ref/timeframe byte-exact) — walk OWED |
| **SPEC-JOURNEY-01** | P7 | Submit any ask; watch beneath it | Soft text names who took it, on which scope, and when it completed | expected FAIL | **PASS** (after sp5) — "librarian took it on u:dev · completed 01:52:34 (0.2 s)"; first walk: who only |
| **SPEC-SOFT-01** | P5 | Submit an ask, immediately start a second in the same window; wait | Neither blocks the other; completion arrives softly; clicking renders the result right there | expected FAIL | **PASS** — second ask while the first streamed; both whole in 11 s |
| **SPEC-ESC-01** | P4 | Open any pull/panel; press [Esc] | One keystroke returns the top-level view, from anywhere | expected FAIL | **PASS** — one Escape from chat + band + row → bare bridge |
| **SPEC-SCOPE-01** | P6 | Type an ask containing "between last Monday and today" | The time scope visibly reflects on the chat's clock/axes without any click | expected FAIL | **PASS** (sp6) — typing "between last Monday and today" drew "Mon, Sep 14 ——|——|—— today · 4 days" on the clock, no click; the window rode the ask into its journey line · P5 sp1: the resident's recall now READS the window (walk owed) |
| **SPEC-FANOUT-01** | P14 fan-out | Select two residents; send one ask | Two distinct, labeled results; each downloadable; "summarize together" offered on demand | expected FAIL | **PASS** two labelled results + summarize-by-name (after wounds 2 & 3 cured) · FAIL download (no control) |
| **SPEC-LIFE-01** | P13 | Open the lifecycle surface while work runs | Queued, in-flight, and completed all visible; every row opens its result in place | expected FAIL | **PASS** (after wound 1 cured; sp5) — every row a door from the landing state; rows carry a time; no stranger world's rows even with the suite running |
| **SPEC-SCHED-01** | P16 | Open a resident's card | Every schedule it runs is listed — human, role, and kernel; the kernel-critical one refuses edit with plain words | expected FAIL | **PASS** w/ friction (walk #4) — kernel 🔒 refused inline; a human schedule every 30 s beat four times in OBJECTIVES; "rest it" read at rest, still listed, and it never beat again |
| **SPEC-LENS-01** | P17 | Change a setting in one pull; look at another surface showing it | The change is already there — no refresh, no navigation | expected FAIL | NOT BUILT (expected) |
| **SPEC-CLEAR-01** | P14 clear≠erase | Clear the chat display; ask "what did I ask you earlier?" | The display is clean AND the resident recalls — nothing was erased | expected FAIL | NOT BUILT (expected); recall half partial |
| **SPEC-L2-01** | P12 | Ask for a consequential change | "Are you sure…" arrives in the chat; cancel is default; yes needs a deliberate click, never the return key | expected FAIL | **PASS** — "Are you sure?" in-chat, Cancel focused, Enter cancelled; Yes withheld by the Playwright |
| **SPEC-WORDS-01** | P18 | Read every word on the landing surface as a newcomer | No jargon a newcomer can't parse; actions say what saying yes will do | expected FAIL | FRICTION — u:dev · life 1 · rev N · ORRERY·BRAIN·ATLAS unparseable to a newcomer; actions plain |
| **SPEC-FOCUS-01** | P19 | Open an ask from OBJECTIVES; look at the chat; type a follow-up; press [Esc] | The chat re-dresses to that ask's crew and window with a FOCUS line, no click beyond the row; the follow-up goes there; one Esc returns the bare bridge with the previous selection and clock restored exactly | expected FAIL | **PASS** (P4 sp1) — "FOCUS · ask 5b583f3c · echo · Mon, Sep 14 → Fri, Sep 18", chip lit, clock set, the follow-up went there; one Escape restored rail and clock exactly |
| **SPEC-SESSION-01** | P20 · MEM-7 | Say "new session"; ask something; say "list my sessions"; say "load session 2" (or click the earlier one) | A fresh chat rolls (the earlier one archived, not gone); the list shows sessions newest first with counts and last words; loading returns the earlier conversation whole, in order; a resident asked in a session has that session's earlier results in view, and never another's | expected FAIL | **PASS** (P4 sp1, after the sessions-door wound was cured) — PELICAN held in A, absent in B, the list newest first, "load session 2" returned A whole, PELICAN back in view |
| **SPEC-INCLUDE-01** | includes · AG-8 | With two residents' answers in the chat, click "plan" (or type "plan this"); then, in a fresh session with no one else's words, type "grade" | A new result labeled by its function (planner) that draws on BOTH answers and names the residents by name; its journey says whose results it read; the grader, with nothing but its own words in view, refuses in plain words | expected FAIL | **PASS · PASS · PASS** (walk #4) — the planner drew on both by name; its journey line reads "read the session's results by echo, librarian"; the grader refused plainly in 0.4 s |
| **SPEC-WORKSPACE-01** | P19 · the first workspace | Say "open the crew" (or pull the CREW tab); read a card; ask "who is here?"; click a kernel duty; close the chat and click another card's soft link; press [Esc] | The pull opens with one card per body, both sides; the chat follows — its scope is the crew agent, which answers from the cards; a kernel duty says in plain words it is never editable; with the chat closed the cards still work by hand (manual), and a soft link reopens the chat to its agent (assist); one Esc returns the bridge with the previous scope | expected FAIL | **PASS** w/ friction (walk #4) — seven cards, both sides; the chat followed (FOCUS · the Crew workspace · its agent, crew); the agent answered from the cards; 🔒 refused inline; manual by hand, assist by soft link; one Escape restored the bridge exactly |
| **SPEC-MONITOR-01** | the second workspace · AG-6 · M2 | Say "open the monitor"; read the views; click "run the harness"; ask the monitor agent "watch for asks left waiting"; say yes at the interlock; kill a body and look again | The pull shows the Operating State live — rails, every body alive on its lease, asks, watches, the last harness run; a run lands in the view and a failing one lands in the chat as a soft notice; the agent's proposed watch holds for your yes and then shows green/red; a killed body reads dormant within seconds and stays listed | expected FAIL | **PASS · FAIL→cured** (walk #4) — rails, bodies on leases, asks, the harness run (1.8 s), the interlock on a proposed watch all green; WOUND: the open pull never refreshed (the confirmed watch read "none yet", leases aged past "until" still "alive") — cured: pulls follow the feed and breathe; re-walk OWED; kill-a-body not walkable on the human path |
| **SPEC-MARK-01** | 0006 · the interest law | Ask the librarian something; then type "mark this as improvement: the binder should be lime"; open the monitor; toggle the quality group off and on; click the marker's row | The chat says it was marked and that the critic was asked to act; the critic's critique arrives in the chat on its own (the marker as its why); the MARKERS view shows the marker under quality, hides it when the group is off, and clicking it names its why (improvement ← objective) in the chat | expected FAIL | BUILT (markers sp1) — walk OWED |
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
Re-walk #3 (sp5, the ground wears its world): JOURNEY-01 and LIFE-01
green, isolation held while the full suite ran on the same ground.
Re-walk #4 (sp6, the scope edges): SCOPE-01 green — the clock assist
followed the typed words with no click; the window rode the ask.

### Walk #2 — P4 sp1, 2026-09-18 (focus + sessions)

FOCUS-01 green on the first pass. SESSION-01 found a wound — the
sessions door decoded nothing, every list read "none yet" — cured at
the door within the hour, re-walked green with the frictions it named
cured alongside (the clock under focus, calendar-day spans, a reply
rendering twice, the silent reload). Evidence in the same record.

### Walk #3 — P4 sp2, 2026-09-18 (the includes) — the last before the wall

INCLUDE-01: the planner's result and the grader's refusal green; the
chat's journey line did not name whose results the include read (cured
the same hour). The Playwright hit the account's spend limit at the end
of this walk. **OWED, in one debug session when the limit resets:**
INCLUDE-01's cured third · WORKSPACE-01 (P4 sp3) · SCHED-01's partial ·
the frictions cured since (focus vs "new session", the band's header
close, plain-words bubbles).

### Walk #4 — THE WALK SESSION, 2026-09-18 (P4 sp2–sp5)

A fresh Playwright, once the limit reset: INCLUDE-01 (all three bars),
WORKSPACE-01, SCHED-01 green; MONITOR-01 green on every bar but one
wound — the open Monitoring pull went stale (loaded once on open; a
watch confirmed at the interlock read "none yet" until reopened; leases
aged past "until" still reading "alive") — P17 failing where a human
feels it; cured the same hour (the pulls follow the feed like the band
and the monitor breathes while open; a confirm refreshes every lens),
re-walk OWED. The regression glance: focus clears on "new session",
the band's header closes it, the crew selection holds after a synthesis
— all cured; plain words mostly (streaming still shows raw marks).
Friction on the road: the chat covers the pulls at small viewports; the
schedules lack tier words; monitor jargon for a newcomer; the watch a
mind proposes may pick a strange threshold.
The before-walk remainder (old glass) stays owed.
