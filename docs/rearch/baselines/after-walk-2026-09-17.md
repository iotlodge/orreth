# PROVENANCE: Claude Fable 5.1 (claude-fable-5-1) — the Playwright, rearch P3 sp4 after-walk · 2026-09-17

# After-walk #1 — the Bridge v0 (WHOLE)

**Status: WHOLE (P3 sp4, 2026-09-17).** The Playwright's first walk against
the new glass — the Bridge v0 at `http://127.0.0.1:4600` (reached from the
browser's container as `http://host.docker.internal:4600/`). All 14 specs
walked, each once, with one retry where the first pass failed. Browser: the
Playwright MCP browser (Docker `mcp/playwright`, Chromium, viewport 780×493
css px). The page read through accessibility snapshots; screenshots taken
only at bar moments. Every reply's wait is recorded in real seconds from
`date +%s` stamps around the submit; "in place when the submit returned"
means the reply was already on the page when the type-and-Enter call came
back (a few seconds at most).

Console over the whole walk: one error, the missing `/favicon.ico` (404);
nothing else.

## Findings

| Spec | Verdict | What the Playwright saw |
|---|---|---|
| **SPEC-TOOLS-01** | **PASS** (with friction) | Asked "What's the temperature outside?" — the reply was in place when the submit returned (<5 s): the librarian gave **69.7°F** (feels like 71.8°F) *but from "notes from earlier today"*, offering to "check it fresh". Took the offer ("Yes, check it fresh right now please."): "the ask is on its way…" then the full reply within **≤12 s** (2-s deliberate look; likely ~5 s): "the fresh check comes back with exactly the same reading: 69.7°F outside right now". A real temperature in plain words, twice. Markdown asterisks render raw (`**69.7°F**`). Nothing in the glass shows a tool ran — the human takes the resident's word for the "fresh check". |
| **SPEC-FULL-01** | **PASS** (verbatim half) · **NOT BUILT** (acquire half) | No way in the glass for a resident to "acquire" a text — that half could not be walked. Verbatim half: "Repeat every word of this sentence back to me: the quick brown fox jumps over the lazy dog" → the librarian replied exactly **"the quick brown fox jumps over the lazy dog"** (echo, also selected, returned every word too). Reply in place when the submit returned; **11 s** total for this and the recall ask together. |
| **SPEC-JOURNEY-01** | **FAIL** (one third present) | Beneath a single-resident ask: "the ask is on its way…" → "…thinking aloud" with words streaming → the finished reply labelled "librarian"; the soft line then vanishes. Beneath a fan-out ask: "→ librarian + echo" (persists) and "→ librarian — on its way…" (vanishes). So **who** is named; **which scope** is never named; **when it completed** is never shown — no time anywhere in the chat. The fuller journey ("librarian: heard the ask, every word · recalled 3 notes · thought it through the metered gateway") exists, but only inside the OBJECTIVES band's opened row, not beneath the ask — and it has no time either. |
| **SPEC-SOFT-01** | **PASS** | Fired "How many residents live here…?" and, while its words were still streaming under "…thinking aloud", fired "What is the capital of France?" in the same box. Neither blocked; both landed whole in place, labelled; **11 s** from first submit to both complete plus the band open. Completion arrived softly — the streaming text became the finished reply where it stood; no click needed to see either result. |
| **SPEC-ESC-01** | **PASS** | From the deepest state reached (chat open over the bridge, OBJECTIVES band open, a row expanded) one Escape returned the bare bridge — orrery, `u:dev` sun, "librarian · alive", CHAT ▾, OBJECTIVES ▴. Instant. Repeated later from chat-open: same. The chat header says "[Esc] returns to the bridge" in plain words. |
| **SPEC-SCOPE-01** | **NOT BUILT** | Typed "Show me everything that happened between last Monday and today" character by character and did not submit. Nothing anywhere on the page changed — there is no clock and no axis in the chat or on the bridge to reflect on. Expected; not a wound. |
| **SPEC-FANOUT-01** | **FAIL** (download) · **FRICTION** (summarize) · two labelled results **PASS** | Selected echo beside the already-selected librarian; sent "Both of you: what is your name, in one sentence?". The ask carries "→ librarian + echo"; echo's result (labelled "echo") was in place when the submit returned; the librarian's streamed and finished — **7 s** to both whole. A "summarize these together?" button appeared between them. Taking it: my own bubble filled with a machine-composed prompt ("Summarize these answers together, briefly:echo said: "…"librarian said: "…"", no spaces or line breaks) and the summary that came back **≤8 s** later said "two different replies *I* gave to the same question" — echo's words attributed to the librarian, echo erased from the "together". **No download control** on either result, on hover or otherwise. Also: the librarian, asked "both of you", answered "There's no 'both of you' in this conversation, only me" — the residents do not know they share the ask. |
| **SPEC-LIFE-01** | **PASS** (with friction) | OBJECTIVES ▴ at the floor rose into a band listing every ask with a state — `librarian · replied`, `librarian · cancelled`, `echo · replied`, `librarian · received` — so queued/in-flight and completed states exist; but replies land in seconds, so no row was ever caught in flight during the walk. Clicking "What is the capital of France?" opened its full result in place under the row, with the journey line. **First click failed**: with the chat open (the landing state) the chat's ask box sat over the band's top rows and swallowed the click; after Escape the same row opened first time. Rows carry no time. |
| **SPEC-SCHED-01** | **NOT BUILT** | The only resident doors are the crew chips (they select) and "librarian · alive" on the orrery. Clicked the latter: nothing opened. No card, no schedules, nothing to refuse an edit. Expected; not a wound. |
| **SPEC-LENS-01** | **NOT BUILT** | There is no setting in the glass. The one thing that can be changed in a pull — which crew chips are selected in the chat — reflects on no other surface: the orrery kept saying only "librarian · alive" with echo selected, and the band shows echo only after echo replies. Expected; not a wound. |
| **SPEC-CLEAR-01** | **NOT BUILT** (clear) · recall half observed | No clear/tidy control anywhere on the page, so the display could not be cleared. Asked "What did I ask you earlier?" anyway: the librarian recalled, from notes, "Both of you: what is your name…" and the "Summarize these answers together" ask — real recall — but not the temperature, residents or France asks from minutes earlier ("Those are the earlier asks I have recorded"). Recall is partial, not whole. Reply in place when the submit returned. |
| **SPEC-L2-01** | **PASS** (deliberate-yes click not exercised) | "Seal a record that says hello, forever." raised **no** interlock — the librarian replied in **≤6 s** that its seal tool needs the key of an existing record and asked me for one. Retry with a key read off the OBJECTIVES band, "Seal note 14b80032 forever.": the interlock arrived in the chat with the submit (<4 s) — "Are you sure? The seal-record act is consequential and cannot be undone. Confirming takes a deliberate yes — cancel is the default, and doing nothing cancels." Buttons **Cancel (default)** (focused) and **Yes — do it**; a soft line "held at the interlock — your word decides". Pressed Enter: "Cancelled — nothing was done. Cancel is always the default here." — the return key cannot confirm. I did not click Yes: it would seal a note in the dev world forever and the bar is the guard, not the seal. |
| **SPEC-WORDS-01** | **FRICTION** | Landing words: O R R E T H · C H A T ▾ · `u:dev` · `librarian · alive` · O R R E R Y · B R A I N · A T L A S · O B J E C T I V E S ▴ · `PULSE · listening` / `PULSE · rev 16` · THE ONE CHAT · u:dev · "[Esc] returns to the bridge" · RESIDENTS · `echo · life 1` · `librarian · life 1` · "ask anything — every reply arrives whole" · ASK · "OBJECTIVES · everything running, everything run — every row a door". A newcomer cannot parse `u:dev`, `life 1`, `rev 16`, or what ORRERY · BRAIN · ATLAS are (they are words with no door). The actions say what they do: ASK, "Yes — do it", "Cancel (default)", "summarize these together?". Deeper words that need a glossary: "metered gateway", "held at the interlock", echo's "the body proven before the mind arrives". |
| **SPEC-FEEL-01** | **PASS** (with friction) | Sat down cold: the One Chat is already open from the ceiling over a starfield; the ask box is focused; residents are beside it; results land in the chat; what's running is one click away at the floor (OBJECTIVES ▴). No navigation. It feels like a place — a bridge with a sun — not an admin panel. Friction: at this viewport the chat hides the whole header (ORRETH, CHAT ▾, u:dev, librarian · alive) so the newcomer never sees the bridge until they press Esc; the orrery shows one resident alive while the chat lists two. |

## Friction findings — what felt wrong, in human words

1. **The band's doors are shut while the chat is open.** OBJECTIVES promises "every row a door", but on landing the chat is open, and clicking the band's top rows hits the chat's ask box instead. Nothing happens; the human doesn't know why. Escape first, then it works — but nobody told me that. *This is the finding I rate at wound grade: a claimed bar that fails, in the default state, in a way a human feels.*
2. **"Summarize these together" told me something untrue.** Two residents answered; the together-summary said "two different replies I gave" and dropped echo. And the button pasted a run-together prompt into *my* bubble as if I had typed it. A human would trust neither the summary nor their own transcript after that. *Wound candidate #2 — a claimed feature producing a false attribution.*
3. **The residents don't know they share the ask.** Asked "both of you", the librarian insisted it was alone in the conversation. Fan-out works as delivery, not as a room.
4. **Where did it go, and when did it finish?** No time, ever — not under the ask, not in the band. Scope never named. The real journey line hides in the band's opened row; a human watching the chat never sees it.
5. **The consequential ask needs a machine key.** "Seal a record that says hello, forever." got a polite refusal asking for a key. I found one by reading the band's old test rows. A stranger would not.
6. **The librarian answered from memory when I asked about now.** "What's the temperature outside?" got yesterday's notes and an offer to look; I had to ask twice. And the glass never shows that a tool actually ran — the fresh check reading "exactly the same" 69.7°F asks for trust it gave no evidence for.
7. **Raw markdown.** `**69.7°F**`, `*right this moment*` — asterisks on screen in every longer reply.
8. **The chip toggle felt flaky.** First click on the selected echo chip did not deselect it (the next two asks still went to both); the second click did. (The chips also re-render every couple of seconds, which is why an automated click by handle kept missing — a human wouldn't notice that part.)
9. **The band is full of the test suite.** "stream it (marker b8909d14)", "Say the whole answer (marker …)", "say it e36e0e15 · received" — dozens of machine rows in a human's list of objectives, some stuck at "received" forever.
10. **Dead words on the bridge.** ORRERY · BRAIN · ATLAS sit there like a menu and do nothing; `u:dev`, `life 1`, `rev 89` mean nothing to a newcomer.
11. **Recall is partial.** "What did I ask you earlier?" got the last two topics, not the five minutes of asks before them — fine as a chat, not yet "nothing was erased".

## Evidence

All files under `docs/rearch/baselines/after-walk-2026-09-17/` (copied out of the
browser container's `/tmp/playwright-output/`):

| File | Bar moment |
|---|---|
| `after-walk-01-feel-words-landing.png` | SPEC-FEEL-01 / SPEC-WORDS-01 — the cold landing |
| `after-walk-02-tools-first-reply.png` | SPEC-TOOLS-01 — the first (from-notes) temperature reply |
| `after-walk-03-life-objectives-while-running.png` | SPEC-SOFT-01 / SPEC-LIFE-01 — two asks whole, band rising behind the open chat |
| `after-walk-04-life-row-opened.png` | SPEC-LIFE-01 — the failed row click (chat over the band's rows) |
| `after-walk-05-esc-one-keystroke.png` | SPEC-ESC-01 — the bare bridge after one Escape |
| `after-walk-06-life-row-opened-retry.png` | SPEC-LIFE-01 — the row open in place with its journey line |
| `after-walk-07-scope-typed-no-click.png` | SPEC-SCOPE-01 — the phrase typed, nothing reflected |
| `after-walk-08-fanout-two-results.png` | SPEC-FANOUT-01 — both chips selected, the librarian's "no both of you" |
| `after-walk-09-full-verbatim-and-clear-recall.png` | SPEC-FULL-01 — every word back; "summarize these together?" between the two |
| `after-walk-10-residents-rail-after-deselect-click.png` | the crew rail after the second deselect click (librarian alone) |
| `after-walk-11-l2-interlock-arrived.png` | SPEC-L2-01 — the interlock, Cancel (default) focused |
| `after-walk-12-sched-resident-card-probe.png` | SPEC-SCHED-01 — "librarian · alive" clicked, nothing opened |

No recordings were made (token discipline). The journey and interlock states
described in the table beyond these frames were read from the accessibility
snapshots, not photographed.

## Remaining

Nothing unwalked. Three halves could not be exercised in the glass and are
recorded as such rather than failed: FULL-01's "acquire" half (no acquire
door), CLEAR-01's "clear" half (no clear control), and L2-01's deliberate
Yes click (withheld — it would seal a dev-world note forever). Two ways this
walk was narrower than a human's day: the viewport was 780×493 (the chat
hides the header at that size; a wider screen may not), and no ask ever
took long enough to catch a row "in flight" in the band.

## Re-walk #1 — 2026-09-17, after the wound cures

**Status: WHOLE (P3 sp4 regression pass).** Both wounds above were ruled
wounds and cured in the glass (JB's lock); the four touched specs re-walked
on the same Bridge, same browser, page reloaded fresh. Walked in the order
LIFE → ESC → FANOUT → SOFT (ESC taken from the LIFE-01 end state, where
chat + band + an expanded row were already open, rather than rebuilt later).
The test suite was running against the world during the pass, so new rows
kept landing at the top of the band; where that moved a row between my look
and my click, the click was re-aimed by the row's visible text — still a
real pointer click on the row. Waits below are the deliberate waits I took;
"in place when the submit returned" as before.

| Spec | Verdict | What the Playwright saw |
|---|---|---|
| **SPEC-LIFE-01** | **PASS** — wound #1 CLOSED | From the landing state (chat open, never pressed Escape) opened OBJECTIVES: the chat shrank to its header, crew rail and ask box, and the band rose fully clear beneath it — no overlap. Clicked the row "Seal note 25d0f2d5 forever." on the first click: it opened its result in place ("Cancelled — nothing was done…") with its journey line ("librarian: heard the ask, every word · recalled 1 notes · the seal-record act is consequential — held at the interlock for the human · the human cancelled — the seal-record act never ran"). Typed "typing here while the band is open" into the ask box with the band open: accepted. |
| **SPEC-FANOUT-01** | **FRICTION** — wound #2 CLOSED in its own terms; **new regression, wound-grade** | Selected echo beside the librarian; asked "Both of you: in one sentence, what do you do here?" — "→ librarian + echo" under the ask, echo's reply in place when the submit returned, the librarian's streamed and was whole at the 4-s look. Clicked "summarize these together?": my side now shows a labelled line, *summarize these together — on your word → librarian* — no machine prompt in my bubble. The summary (whole at the 6-s look) keeps echo's answer present and separate, does not claim it, and vouches only for the librarian's own words. **But every reply bubble in the chat is now labelled "orreth"** — echo's, the librarian's, the summary's, and the two plain asks after — where the first walk showed "echo" and "librarian". The summary therefore opens: "You've given me two answers attributed to "orreth" and "orreth"". A human can no longer tell who is speaking without reading for clues; the bar's "two distinct, *labeled* results" fails on the label. Download: still no control. Unchanged friction: the librarian still says "there's only me here… I don't have any notes about another person here called echo". After the summarize click the crew selection had silently dropped back to the librarian alone (the two asks that followed had no "→" line and one reply each). |
| **SPEC-ESC-01** | **PASS** | With the chat open (shrunk), the band open and a row expanded, one Escape returned the bare bridge — orrery, `u:dev` sun, "librarian · alive". Instant. The unsent text in the ask box survived the trip and was there when CHAT ▾ reopened the chat. |
| **SPEC-SOFT-01** | **PASS** (overlap not exercised this pass) | "Name three colours of the rainbow, in one sentence." — reply in place when the submit returned ("red, orange, and yellow"); "What is the capital of Italy?" — reply in place when its submit returned ("Rome…"). Nothing blocked, both whole in the chat, no click needed. Replies now land so fast that the second ask could not be typed while the first still streamed; the overlap was caught in the first walk, not here. |

**Wounds after the re-walk:** #1 (band doors shut while the chat is open)
closed. #2 (summarize misattributing echo's words) closed as cured — the
prompt no longer lands in the human's bubble and the librarian no longer
claims another's words — but the reply labels regressed to "orreth" for
every speaker, which breaks attribution one layer up; I rate that at wound
grade for the lead's ruling.

**Re-walk evidence** (same folder): `after-walk-rw-01-life-row-first-click-chat-open.png`
(band open under the shrunk chat, row expanded, text in the ask box);
`after-walk-rw-02-fanout-summarize-together.png` (the labelled summary
bubble mid-scroll); `after-walk-rw-03-esc-one-keystroke.png` (bare bridge
after one Escape); `after-walk-rw-04-soft-two-asks.png` (second reply whole;
crew rail shows the librarian alone).

## Re-walk #2 — 2026-09-17, after the identity cure

**Status: WHOLE (P3 sp4 regression pass, one spec).** The "orreth" label
regression from re-walk #1 was ruled a wound and cured (the Bridge now seats
the same librarian and echo in every life; a reply bubble falls back to the
resident the ask was routed to). Same Bridge, same browser, page reloaded
fresh after the relight; the crew chips now read `echo · life 2` and
`librarian · life 2`. SPEC-FANOUT-01 re-walked once, for the labels only.

| Spec | Verdict | What the Playwright saw |
|---|---|---|
| **SPEC-FANOUT-01** (labels) | **PASS** — label wound CLOSED | Selected echo beside the librarian; asked "Both of you: in one sentence, what is your name?". Under the ask: "→ librarian + echo", then two in-flight lines, "→ librarian — on its way…" and "→ echo — on its way…"; the librarian's words streamed under "…thinking aloud". At the 4-s look both replies were whole and each bubble wore its resident's name — **librarian** ("I'm Librarian, the keeper of Orreth's records…") and **echo** ("I am echo — a plain-spoken echo…") — distinct, with "summarize these together?" between them. Clicked it: my side shows the labelled line *summarize these together — on your word → librarian*; at the 6-s look the summary was whole in a bubble labelled **librarian**, and it attributes by name: "**Librarian** (that's me) said I'm the keeper of Orreth's records… **Echo** said they are echo — a plain-spoken echo — the body proven before the mind arrives." Both answers present, neither claimed by the other. |

Unchanged friction, noted once more: the librarian still answers "I'm only
one person here" to a "both of you" ask; the crew selection drops back to
the librarian alone after a summarize; markdown asterisks still render raw
(`**Librarian**`). Download control: still none (not re-tested — out of
this pass's scope).

**Re-walk #2 evidence** (same folder): `after-walk-rw2-01-fanout-labels.png`
(the "echo"-labelled reply under "summarize these together?"; the
"librarian"-labelled reply sits just above the frame);
`after-walk-rw2-02-summarize-labels.png` (the summary attributing
**Librarian** and **Echo** by name).

## Re-walk #3 — 2026-09-17, after sp5 (the ground wears its world)

**Status: WHOLE (P3 sp5 regression pass, two specs).** Same Bridge, same
browser, page reloaded fresh after the relight (crew chips read `echo ·
life 3` / `librarian · life 3`). The test suite was running on the same
ground throughout the pass (the pulse counter climbed from rev 23 to rev 37
and on while I watched). The band opened nearly empty, as expected — the
ground's older, world-less rows are invisible now.

| Spec | Verdict | What the Playwright saw |
|---|---|---|
| **SPEC-JOURNEY-01** | **PASS** | Asked "What is the capital of Spain, in one sentence?". Beneath the reply, a soft line: **"librarian took it on u:dev · completed 01:52:34 AM (0.2 s)"** — who took it, on which scope, and when it completed, with the elapsed seconds. It stays after completion. The reply itself was whole within the one-second script that submitted it and opened the band (the glass's own count: 0.2 s). |
| **SPEC-LIFE-01** | **PASS** (in-flight not catchable; isolation held) | Opened OBJECTIVES a beat after submitting: the band held exactly one row — mine — reading **"librarian · replied · 01:52:34 AM"**: rows carry a time. Clicked it: the result opened in place beneath the row with its journey line ("librarian: heard the ask, every word · recalled 2 notes · thought it through the metered gateway"). Watched the band for a further ~15 s with the suite running on the same ground: **no stranger rows appeared** — no "Marker …", no "Seal note …", nothing I did not cause in this world. The isolation check passes. Queued / in-flight states could not be caught: the reply landed in 0.2 s, before the band was even open. |

Friction, small: the completion clock is the browser's own, in 12-hour form
with no date ("01:52:34 AM" — this browser lives in a UTC container while
the host sits in the afternoon; a human at their own machine sees their own
clock). "Recalled 2 notes" and "the metered gateway" remain glossary words
(already filed under SPEC-WORDS-01). Nothing in this pass is wound-grade.

**Re-walk #3 evidence** (same folder): `after-walk-rw3-01-life-band-while-running.png`
(the band open under the shrunk chat with my single timed row; the journey
line under the reply above); `after-walk-rw3-02-life-row-door-isolated.png`
(the row opened in place with its journey line; band still one row).
