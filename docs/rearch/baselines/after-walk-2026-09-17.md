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

## Re-walk #4 — 2026-09-17, sp6 (the scope edges)

**Status: WHOLE (P3 sp6 pass, one spec).** Same Bridge, same browser, page
reloaded fresh after the relight (crew chips read `echo · life 4` /
`librarian · life 4`). The chat now carries a TIME strip under its header.
Note on the clock: this browser lives in a UTC container where it was
already past midnight, so its "today" is Fri, Sep 18 while the host sits on
Thu, Sep 17 — every date below is the browser's own; a human at their own
machine sees their own day.

| Spec | Verdict | What the Playwright saw |
|---|---|---|
| **SPEC-SCOPE-01** | **PASS** | **Resting:** the strip read `TIME · now · type "between X and Y" or "since …" to set it`. **Typing** "What happened between last Monday and today?" character by character, no click, no send: the strip became **`Mon, Sep 14 ——|——|——|—— today · 4 days`** — both edges named, a ticked axis between them — as the words landed. **Sent:** the reply was whole within the 5-s script (the glass's own count 0.2 s); the journey line under it names the window: **"librarian took it on u:dev · Mon, Sep 14 → Fri, Sep 18 · completed 02:33:37 AM (0.2 s)"**. The strip kept the window after the send with the box empty. **Typed** "since yesterday": the strip followed at once — **`Thu, Sep 17 … today · 27 h`**. **Cleared the box** (select-all, backspace): the strip returned to **`now`** with its hint. |
| **SPEC-SCOPE-01** (re-check, after the cure) | **PASS** | Reloaded fresh (no relight). Typed "What has changed since yesterday?" character by character: the strip followed — `Thu, Sep 17 … today · 27 h`. Sent: the reply was whole within the 5-s script (the glass's own count 0.2 s); the strip read **`now`** with its hint, the box empty, while the reply's journey line still names the window: **"librarian took it on u:dev · Thu, Sep 17 → Fri, Sep 18 · completed 02:36:29 AM (0.2 s)"**. The after-send friction below is cured. Evidence: `after-walk-rw4-03-recheck-strip-now-after-send.png`. |

Friction, small: after a send the strip keeps the sent window over an empty
box until the next keystroke — a human may wonder whether the next ask is
still scoped (not walked; out of this pass). "4 days" and "27 h" are the
browser-clock spans and read as the strip's arithmetic, fine. The
librarian's reply itself had nothing to say about the window ("I don't have
any record of what happened between last Monday and today") — content, not
the clock's bar. Nothing in this pass is wound-grade; the chat reacted to
typing and replied.

**Re-walk #4 evidence** (same folder): `after-walk-rw4-01-scope-typed-no-click.png`
(the strip showing Mon, Sep 14 → today · 4 days with the ask still unsent
in the box); `after-walk-rw4-02-scope-journey-window.png` (the journey line
naming the window under the reply; the strip still holding it).

## Walk #2 — 2026-09-18, P4 sp1 (focus + sessions)

**Status: WHOLE (P4 sp1, two new specs).** Same Bridge, same browser, page
reloaded fresh after the relight (crew chips read `echo · life 5` /
`librarian · life 5`). The chat header now reads "sessions · new session ·
[Esc] returns to the bridge", and a resize grip sits at the chat's
lower-left corner. Waits are the deliberate waits I took; every reply was
whole inside its 5-s wait (the glass's own counts: 0.1–0.2 s). Clock stamps
are the browser's own.

| Spec | Verdict | What the Playwright saw |
|---|---|---|
| **SPEC-FOCUS-01** | **PASS** (with friction) | *Setup:* with echo selected, sent "Between last Monday and today, both of you: say hello in one sentence." (both replied under the window "Mon, Sep 14 → Fri, Sep 18"), then deselected echo. Resting state recorded: crew rail **librarian alone**, clock **now**. *Walk:* Escape to the bare bridge; opened OBJECTIVES; clicked that ask's row (echo's). The chat opened by itself and re-dressed with a FOCUS strip — **"FOCUS · ask 5b583f3c · echo · Mon, Sep 14 → Fri, Sep 18 · [Esc] returns the bridge, scope restored"** — the clock read **"Mon, Sep 14 … today · 5 days"** and echo's chip lit; no click beyond the row. Typed the follow-up "And now say goodbye in one sentence.": it went there — **"echo took it on u:dev · Mon, Sep 14 → Fri, Sep 18 · completed 07:14:00 PM (0.2 s)"**. One Escape: the bare bridge (orrery, sun, "librarian · alive"). Reopened the chat: FOCUS strip gone, clock **now**, rail **librarian alone** — the previous selection and clock restored exactly (rail screenshots before and after match). |
| **SPEC-SESSION-01** | **FAIL — wound-grade** (isolation half PASS) | *Session A* (the chat as found): "Remember the word PELICAN." → "I've got it. I'm writing down right now: PELICAN … If you ask me later in this session … it was the word PELICAN." (0.1 s). Typed **"new session"**: a fresh chat rolled with the line **"a fresh session · 086d98 — the previous one is archived, not gone: say “list my sessions” to return to it"**. *Session B:* "What word did I ask you to remember?" → **"I haven't been given any word to remember from you yet. This is the start of our conversation…"** (0.2 s) — no PELICAN: the isolation bar holds. Typed **"list my sessions"**: **"sessions · newest first · click one to load it — none yet"**. Retry by the header's "sessions" link: **"none yet"** again. Typed "load session 1": **"no session called “1” — say “list my sessions”"**. *Second pass from a session "new session" itself created:* "Remember the word HERON." → new session **aaeff3** (same promise) → the word question → no HERON ("I don't find any note or word you've asked me to remember") → "list my sessions" → **"none yet"**. **Every earlier conversation is unreachable from the glass**: the fresh-session line promises "archived, not gone" and the list never shows anything, so "loading returns the earlier conversation whole" and "has that session's earlier results in view" could not be walked. A human who says "new session" loses what they were saying. |
| **SPEC-SESSION-01** (re-walk, after the sessions-door cure) | **PASS** (with friction) — wound CLOSED | Fresh load after the relight (chips `life 6`). *A:* "Remember the word PELICAN." → "I hear you clear and plain: PELICAN. I'm holding that word now…" (0.2 s). **"new session"** → "a fresh session · 02eb31 — the previous one is archived, not gone…". *B:* "What word did I ask you to remember?" → **"I haven't been given any word to remember from you yet…"** (0.2 s) — no PELICAN. **"list my sessions"** → **"sessions · newest first · click one to load it — 1. 07:27:03 PM · 1 ask · “What word did I ask you to remember?” · (this one) — 2. 07:26:57 PM · 2 asks · “Remember the word PELICAN.” — 3. 07:17:33 PM · 2 asks · “Remember the word HERON.” — 4. 07:15:06 PM · 4 asks · “Remember the word PELICAN.”"** — newest first, counts, last words, the first pass's sessions present. **"load session 2"** → the conversation returned whole, in order (the 07:17:40 word question and its reply, then the 07:26:57 PELICAN ask and its reply), closing with **"session aaeff3 loaded · 2 asks · continue here"** — which also revealed that the relit chat had silently continued session aaeff3 from the first pass (its log looked empty on load), so "2 asks" was right. Asked the word question there → **"The word PELICAN appears in my notes from earlier in this session"** (0.2 s) — she has PELICAN in view and nothing of any other session; she also reads her own earlier in-session "no memory" reply as a contradiction and says so at length. |
| **SPEC-FOCUS-01** (re-walk, cheap check of the cures) | **PASS** | Escape → OBJECTIVES → the windowed ask's row: "FOCUS · ask 5b583f3c · echo · Mon, Sep 14 → Fri, Sep 18" with the clock **"Mon, Sep 14 … today · 4 days"** (calendar days now). Sent "Say goodbye once more, in one sentence.": after the send the TIME strip **still read "Mon, Sep 14 … today · 4 days"** with the FOCUS strip held — cured; the reply went to echo with the window ("echo took it on u:dev · Mon, Sep 14 → Fri, Sep 18 · completed 07:28:35 PM (0.2 s)") and **rendered once**. The grip is now announced as a separator, "resize the chat". |
| **SPEC-SESSION-01** (re-check, reload continues the session visibly) | **PASS** | Reloaded fresh after the relight (chips `life 7`). The chat rendered the last session's four asks whole and in order on load — the word question, "Remember the word PELICAN.", the word question again, "Say goodbye once more…" — each with its reply, closing with **"session aaeff3 loaded · 4 asks · continue here"**. The replayed journey lines carry the world like live ones: **"librarian took it on u:dev · completed 07:17:40 PM (0.1 s)"** (and echo's with its window, "echo took it on u:dev · Mon, Sep 14 → Fri, Sep 18 · completed 07:28:35 PM (0.2 s)"). Both frictions cured. Evidence: `after-walk-p4s1-rw-04-recheck-reload-continues-session.png`. |

**Friction (FOCUS-01 and around it):**
- Under focus, after the follow-up was sent, the TIME strip dropped back to
  "now" while the FOCUS strip still named the window — the two disagree
  while focus is held (whether a second follow-up still rides the window
  was not walked).
- The focus strip's span read "5 days" for Mon, Sep 14 → Fri, Sep 18 where
  the typed clock had read "4 days" for the same window — two arithmetics.
- In the setup fan-out, **echo's reply rendered twice** in the chat: two
  identical "echo" bubbles, each with its own identical journey line
  (`echo took it on u:dev · … · completed 07:12:49 PM (0.1 s)`), while the
  band listed echo's reply once. A human sees a stutter.
- The librarian, asked "both of you", still answers "I'm just one person
  here" (already filed).
- The band now lists every ask of this world back to yesterday evening
  (all mine — no strangers; isolation still holds).

**The resize grip (not a spec):** one drag from the lower-left grip,
120 px left and 100 px down: the chat grew from 560×355 to 671×446 and
tracked the pointer within ~10 px; the upper-right corner stayed put
(right edge 733, top 0). It feels right. The grip is a 16×16 px target —
small, but findable by its hover title.

**Wound call:** SPEC-SESSION-01 — the earlier session is gone from the
human's seat despite the glass's own promise "archived, not gone" (list
always "none yet"; load by ordinal refused). Wound-grade, for the lead's
ruling. FOCUS-01's items are friction only.

**Walk #2 evidence** (same folder): `after-walk-p4s1-00-rail-before-focus.png`
(librarian alone, before focus); `after-walk-p4s1-01-focus-strip.png`
(FOCUS strip, re-dressed clock, echo lit, band open); `after-walk-p4s1-02-esc-bare-bridge.png`
(one Escape → bare bridge); `after-walk-p4s1-03-rail-after-esc.png`
(librarian alone again); `after-walk-p4s1-04-session-list.png` (session B:
no PELICAN; list "none yet"); `after-walk-p4s1-05-session-list-retry-none-yet.png`
(second pass: list "none yet" again).


**Walk #2 re-walk evidence** (same folder): `after-walk-p4s1-rw-01-session-list.png`
(the list: four sessions newest first with counts and last words; B's reply below
it); `after-walk-p4s1-rw-02-loaded-session-pelican.png` (the loaded session's answer:
PELICAN in view); `after-walk-p4s1-rw-03-focus-time-held-after-send.png` (FOCUS and
TIME both holding the window after a follow-up send; the reply once).

Re-walk friction, small: the session list bubble landed *above* the reply it
followed (the ask, then the list, then the librarian's answer); a reloaded page
shows an empty chat while silently continuing the last session; re-rendered
journey lines read "librarian · completed …" without the scope the live lines
carry; the chat remembered its dragged size across the reload.
## Walk #3 — 2026-09-18, P4 sp2 (the includes)

**Status: WHOLE (P4 sp2, one new spec; one walk, no re-checks — JB's
cadence).** Same Bridge, same browser, page reloaded fresh after the relight
(crew chips read `echo · life 8` / `librarian · life 8`). Under the chat's
header an INCLUDES strip reads **"INCLUDES · plan · critique · grade · one
step over what the residents brought into this session"**; the crew rail
still lists residents only. Waits are the deliberate waits I took; the
glass's own counts in brackets.

| Spec | Verdict | What the Playwright saw |
|---|---|---|
| **SPEC-INCLUDE-01** | **PASS** on the planner's result and the grader's refusal · **FAIL** on "its journey says whose results it read" | *Setup:* "new session" → fresh session 401933; echo selected beside the librarian; asked "Both of you: in one sentence, what is the best way to keep a record safe?" — echo (verbatim) and the librarian ("store it somewhere dry and cool … seal it so no one can alter what's written") both whole inside 6 s (0.2 s). *Plan:* clicked **plan** in the strip; my side shows **"plan — on your word → planner"**; inside 10 s a bubble labelled **"planner"** (0.1 s) — "# PLAN: Next Steps … 1. Clarify what "safe" means — Ask both echo and the librarian … 2. Test the librarian's method — The librarian named dry, cool, dark storage and sealing … 3. Ask echo what "safe" means to echo — Echo mirrored back the question itself … Gap left open: …" — it draws on BOTH answers and names both residents by name. Its journey line: **"planner took it on u:dev · completed 07:41:43 PM (0.1 s)"** — it does not say whose results it read; the band's row for the step reads "Plan the next steps from what was said in this session. · planner · replied · 07:41:43 PM", no fuller line seen. *Critique:* typed "critique"; inside 10 s a result whose journey reads **"critic took it on u:dev · completed 07:43:03 PM (0.2 s)"** — "What is thin: Echo's answer gives us nothing to work with … What contradicts: The librarian and echo are not contradicting each other … The one thing most worth fixing: Ask echo again, directly…" — both residents by name, the planner's words weighed too (the bubble's own label line was not separately captured; the journey names the critic). *Grade:* "new session" (936d86) then typed "grade" with no one else's words in it: my side **"grade — on your word → grader"**, bubble labelled **"grader"**: **"Nothing here to grade but my own words — I never grade my own yardstick. Bring a resident's answer into this session and ask me again."** — journey **"grader took it on u:dev · completed 07:43:42 PM (0.3 s)"**. A plain refusal, no grade, no thinking. |

**Friction:**
- **A held focus survives "new session".** A click on the planner's row in
  the band (to read its journey) set "FOCUS · ask 2e835044 · planner" —
  and the fresh session 936d86 opened still wearing it ("FOCUS · ask
  2e835044 · planner · now"). A new session should not carry the old
  session's focus; the grade step ran under it.
- **With a band row expanded, the floor's OBJECTIVES toggle is covered** by
  the expanded row, so the band cannot be closed by its own toggle (the
  click lands on the expansion); Escape still clears everything.
- The planner's bubble shows raw markdown ("# PLAN: Next Steps", `**…**`)
  — the standing raw-markdown friction, now on headings too.
- The crew selection stayed as I left it (both chips lit) after the plan
  and critique steps; the "summarize these together?" case was not
  re-tested (it would have cost a round).
- The includes' journey lines name the include and the world only; a human
  cannot see from the chat which residents' results the include read.

Nothing wound-grade: every include answered as labelled, both residents
were named in the plan and the critique, and the grader refused cleanly.

**Walk #3 evidence** (same folder): `after-walk-p4s2-01-planner-result.png`
(the planner's bubble and its journey line under the INCLUDES strip; both
chips lit); `after-walk-p4s2-02-grader-refuses.png` (the fresh session with
the grader's refusal — and the carried-over FOCUS strip above it).

## Walk #4 — 2026-09-18, THE WALK SESSION (P4 sp2–sp5)

**Status: WHOLE (P4 sp2–sp5; four specs and a regression glance, each
walked once, one retry on the one failure — the walk owed since the
spend wall).** Same Bridge (`http://host.docker.internal:4600/` from the
browser's container), same browser (Playwright MCP, Chromium, viewport
780×493 css px). The page loaded on the last session (936d86, the grader's
refusal from walk #3); crew chips read `echo · life 11` / `librarian ·
life 11`. Two pull tabs stand on the left hull wall — C R E W and
M O N I T O R. Waits are measured on the browser's own clock around each
submit (the glass's own counts in brackets); clock stamps are the
browser's (its clock reads ~03:00 AM). One deliberate change of state
mid-walk: during WORKSPACE-01 I shrank the chat by one grip drag (to
402×289) to reach its tab, and it stayed that size for the rest of the
walk.

| Spec | Verdict | What the Playwright saw |
|---|---|---|
| **SPEC-INCLUDE-01** | **PASS · PASS · PASS** — the cured third green | *Setup:* "new session" → fresh session f41f93 (0.03 s); echo selected beside the librarian; "Both of you: in one sentence, what makes a good map?" → both whole in **4.4 s** (echo 0.2 s, librarian 0.2 s), each labelled with its journey line. *Plan:* clicked **plan**; my side "plan — on your word → planner"; a bubble labelled **"planner"** inside ≤14 s (completed 02:58:58, 0.2 s): "NEXT STEPS 1. Clarify what "plain enough" means — Ask Librarian to give an example… whether Echo will mirror the response back unchanged… 2. Ask Echo to answer the map question in Echo's own words, not as a mirror… 3. Name the gap: What counts as "truly are"? — Librarian said…" — drawn on BOTH answers, both residents by name. Its journey line: **"planner took it on u:dev · read the session's results by echo, librarian · completed 02:58:58 AM (0.2 s)"** — it says whose results it read. *Grade:* "new session" → 445676; typed "grade": my side "grade — on your word → grader"; bubble labelled **"grader"**: **"Nothing here to grade but my own words — I never grade my own yardstick. Bring a resident's answer into this session and ask me again."** in **0.4 s** (0.1 s). A plain refusal. |
| **SPEC-WORKSPACE-01** | **PASS** (with friction) | Typed "open the crew": the pull rose in **0.05 s** with **seven cards** — crew · critic · echo · grader · librarian · monitor · planner — each "name · firmware/resident · life N", "self …e5bd50ef · wearing covenant v1.0.0 · template sha256:0a6e1", capability chips (`ask`, and for the librarian `tools:weather` · `tools:seal-record`, for the monitor `tools:add-watch`), **SIDE A · INFERENCE** ("asks served: 15 · last 02:58:38 AM") and **SIDE B · THE JOB** (four 🔒 duties, the schedules, a "schedule an ask for librarian…" form, "ask the crew agent about librarian"). The chat followed: **"FOCUS · the Crew workspace · its agent, crew · [Esc] returns the bridge, scope restored"**; both chips unlit under it. Asked "who is here?": a bubble labelled **"crew"** listed all seven from the cards — "Firmware agents: · crew (self 241daf07) — life 3, covenant policy v1.0.0, capabilities: ask · … Residents: · echo … · librarian (self e5bd50ef) — life 11 … tools: weather, tools: seal-record … The grader has already spoken once in this session, declining to grade their own yardstick." — journey "crew took it on u:dev · read the session's results by grader · completed 03:00:49 AM (0.1 s)" (my wait was not captured — the script's later step failed — the reply was in place at the next read). Clicked the librarian's **🔒 serve the invocation rail**: the row itself grew the words **"kernel-required — visible, never editable"**; nothing opened to edit. *Closing the chat:* the C H A T ▾ tab sits at the header's right, under the open chat's own header at this viewport — the click never reached it (two tries); I dragged the grip to shrink the chat and clicked the tab's exposed "▾" sliver, and the chat slid away. With the chat closed, echo's 🔒 "think only on the meter" refused the same way by hand (manual). Clicked **"ask the crew agent about librarian"**: the chat reopened to its agent in **0.4 s** (FOCUS crew again) and sent "about librarian — on your word → crew"; the crew answered whole (completed 03:03:25, 0.2 s) — what the librarian is, wears, carries, its two sides, in plain words. One Escape: the bare bridge (orrery, sun, "librarian · alive"); the rail's two chips **both lit again** — exactly as before "open the crew" (screenshot 02 shows both lit then); reopening the chat by its tab showed no FOCUS and TIME "now". |
| **SPEC-SCHED-01** | **PASS** (with friction) | The librarian's SIDE B, read with the chat shrunk: four 🔒 duties; **"🔒 run the harness against my golden set (every 30 min · 0×)"**; **"Review what was asked of you today and note one thing worth remembering. (every 1 h · 0×) rest it"**; the form "schedule an ask for librarian…" · "every N seconds" (3600) · "schedule". Beats are there; **no word on the card says which schedule is the kernel's, the role's or the human's** — the lock is the only tier mark. Clicked the 🔒 harness schedule: **"kernel-required — visible, never editable"**, inline, no editor. Typed "Say the word HERON once, in one sentence.", set 30, clicked schedule: the row **"Say the word HERON once, in one sentence. (every 30 s · 0×) rest it"** listed in **0.15 s**, among the other schedules (no "human" heading to land under). Opened OBJECTIVES (its toggle sat clear of the shrunk chat): rows **"Say the word HERON once, in one sentence. · librarian · replied"** at **03:05:08**, 03:05:39, 03:06:09, 03:06:39 — the first ~2 s after scheduling, then on the 30-s beat (my 50-s watch missed them across a line break; the band read at 03:05:57 already held two). *Rest:* the row's "rest it" was covered by the open band; closed the band by its header, clicked **rest it** at 03:06:49 → the row now reads **"Say the word HERON once, in one sentence. (every 30 s · last 03:06:38 AM · 4×) · at rest since 03:06:49 AM"** — drawn struck-through, still listed, never gone. 42 s later (03:07:33) the band still held exactly four occurrences; none since. The card's count read **"0×"** the whole time the four were landing and jumped to "4×" only at the rest. |
| **SPEC-MONITOR-01** | **PASS** rails · bodies · asks · harness · interlock · **FAIL — wound-grade** "live" and "the watch shows after yes" (the watch showed only after closing and reopening the pull) · **NOT WALKABLE** kill a body | Typed "open the monitor": the pull in **0.02 s** — **PULSE** (feed revision 197 · world u:dev), **RAILS** (outbox pending 0 · oldest unpublished — · ask.received topic depth 965 · bench 0 for each of the seven), **BODIES** (all seven "alive · until 03:08:15 AM" — leases), **ASKS** (cancelled 7 · replied 68 · awaiting-confirm 4), **WATCHES** ("none yet — ask the monitor agent to propose one"), **HARNESS** ("no run yet" · "run the harness against the librarian now"); the chat's FOCUS "the Monitoring workspace · its agent, monitor". Clicked **run the harness**: **1.8 s** → **"librarian v0.1.0 · 03:08:23 AM · 2 passed · 0 failed"** in the view; it passed, so no chat notice (the failing-run notice was not exercised). Asked the monitor agent **"propose a watch that catches asks left waiting"**: **3.7 s** → in the chat, labelled "monitor": **"Are you sure? The add-watch act is consequential and cannot be undone. Confirming takes a deliberate yes — cancel is the default, and doing nothing cancels."** with **Cancel (default)** holding focus, **Yes — do it**, and "held at the interlock — your word decides". Clicked Yes: **"Done, on your word: watch_19ee89f5e9"** (journey "monitor took it on u:dev · read the session's results by crew, grader · completed 03:08:56 AM (4.6 s)"). **WATCHES still read "none yet" 60 s later** (03:09:58) — and the pull had stopped following the world: its "feed revision" still 197 while the page's own footer read `PULSE · rev 203` at the interlock and `rev 205` at 03:09:58; its leases read "alive · until 03:08:39 AM" at 03:10:00. *Retry (the one allowed):* Escape, "open the monitor" again → **WATCHES: "asks-left-waiting — asks_received > 72 · 0 · RED"**, feed revision 205 — the watch existed; the open pull had not shown it. Over the next 20 s (03:11:23 → 03:11:43) the reopened pull's revision and the footer both stayed 205 while the lease shown, "until 03:10:48 AM", aged 55 s into the past still reading "alive". Kill a body: nothing in the glass kills one — NOT WALKABLE on the human path. |
| **Regression glance** | 4 lines | *Held focus vs "new session":* CURED — with "FOCUS · ask 708d35f3 · crew · now" held from a band row, "new session" (35ae48) opened with no FOCUS strip, TIME "now", both chips lit. *OBJECTIVES header closes the band:* CURED — one click on the header closed it (it slid below the floor). *Plain-words bubbles:* MOSTLY — the crew's finished bubbles rendered "About librarian" and "What librarian is:" without "#" or "**" (the streaming text showed both raw until it finished); the planner's bubble still shows "*Why: …*" with its asterisks. *Crew selection after "summarize these together?":* HELD — after a fan-out ("Both of you: name one color", both whole in 2.4 s) and the summarize click, the summary landed 3 s later labelled "librarian" with every point attributed by name ("echo gave back the exact words of the ask itself… librarian (that's me) noticed…", journey "read the session's results by echo") and both chips stayed lit. |

**Friction — what felt wrong, in human words:**
- **The Monitoring pull goes stale while open.** It opened live and then stopped following the world: the footer's PULSE kept counting (197 → 203 → 205) while the pull's own "feed revision" sat at 197, its leases fell into the past still reading "alive", and the watch I had just said yes to was "none yet" for a full minute. Closing and reopening it showed everything. A human who says "Yes — do it", reads "Done", and then reads "none yet" feels lied to — this is the wound-grade item.
- **The chat covers the workspace it serves.** At this viewport the open chat (670 px wide, from the ceiling) hides most of the Crew and Monitoring pulls' cards; the pulls' text is there but a human reads it only after shrinking the chat by the grip or closing it.
- **The chat's own tab is under the chat.** C H A T ▾ lives at the header's right and the open chat covers all but its trailing "▾"; the click lands on the chat's header. There is no close control inside the chat, and Escape closes every layer — so "close the chat and keep the pull" takes a grip drag first. (WORKSPACE-01's manual half was walked only after that drag.)
- **Layers stack over the card's links.** With OBJECTIVES open, the librarian card's "rest it" sat under the band; the band had to be closed first.
- **The pull snaps back to its first card when it re-renders.** Twice I had scrolled the Crew pull to the librarian's card and the screenshot a moment later shows the crew card at the top (evidence 09 and the first 11 were retaken for that reason). A human reading a lower card loses their place whenever the world moves.
- **No tier words on the schedules.** The lead's brief says kernel · role · human; the card shows a lock or no lock and nothing else. "Review what was asked of you today…" carries "rest it" — a human cannot tell whether that is the role's schedule or someone's human one.
- **The schedule's count lags.** "0×" while four occurrences landed in the band; "4×" only once rested.
- **The watch's words are not a human's.** "asks-left-waiting — asks_received > 72 · 0 · RED": asked to catch asks left waiting, the rule is about asks received, its value is 0, and it is red — a newcomer cannot say whether red means "waiting" or "broken".
- **Newcomer words in the monitor:** "outbox pending", "oldest unpublished", "ask.received topic depth 965", "bench". Rails words, not human ones.
- The soft link "ask the crew agent about librarian" both reopens the chat and sends the ask at once — fine, but a human expecting to type gets an answer instead.
- The librarian, asked "both of you", still answers "there's only me here" (standing).
- Raw markdown: the finished bubbles are mostly clean now; "*Why: …*" italics still show their asterisks, and every bubble shows raw "#"/"**" while it streams.

**Wound call:** SPEC-MONITOR-01 — the pull that promises "the Operating State, live" stopped following the world while open (footer 205 · pull 197 · leases in the past reading "alive"), and the watch confirmed at the interlock did not appear in WATCHES until the pull was closed and reopened. Wound-grade, for the lead's ruling. Everything else is friction; INCLUDE-01, WORKSPACE-01 and SCHED-01 are green.

**Not walkable on the human path:** killing a body (MONITOR-01's last step) — nothing in the glass does it; the failing-harness notice in the chat (the run passed).

**Walk #4 evidence** (same folder): `after-walk-p4ws-01-planner-journey-names-both.png`
(the planner's bubble and the journey line naming echo, librarian; both chips
lit); `after-walk-p4ws-02-grader-refuses.png` (fresh session 445676, the
grader's refusal, no FOCUS strip); `after-walk-p4ws-03-crew-pull-cards-focus.png`
(the Crew pull behind the open chat; FOCUS "the Crew workspace · its agent,
crew"); `after-walk-p4ws-04-crew-agent-who-is-here.png` (the crew's answer from
the cards); `after-walk-p4ws-05-chat-closed-cards-manual-kernel-refuses.png`
(chat closed; echo's card with "think only on the meter — kernel-required —
visible, never editable"); `after-walk-p4ws-06-soft-link-reopens-chat-to-crew-agent.png`
(the chat back, shrunk, the crew's "about librarian" whole);
`after-walk-p4ws-07-esc-bare-bridge-scope-restored.png` (one Escape → the bare
bridge); `after-walk-p4ws-08-sched-card-side-b-kernel-refuses.png` (the Crew
pull after the kernel schedule's refusal); `after-walk-p4ws-10-sched-occurrence-in-objectives.png`
(the band with the HERON occurrences under the librarian); `after-walk-p4ws-11-sched-rested-still-listed.png`
(retaken after the walk: the librarian's card with the rested row, "4× · at rest
since 03:06:49 AM"); `after-walk-p4ws-12-monitor-pull-views.png` (the five
views, watches "none yet", harness "no run yet"); `after-walk-p4ws-13-monitor-harness-run-landed.png`
("2 passed · 0 failed"); `after-walk-p4ws-14-monitor-interlock-are-you-sure.png`
("held at the interlock — your word decides" in the shrunk chat; footer rev 203,
pull rev 197); `after-walk-p4ws-15-monitor-after-yes-watches-none-yet.png`
(after Yes: WATCHES "none yet", footer rev 205); `after-walk-p4ws-16-monitor-watch-after-reopen.png`
(after reopening: "asks-left-waiting — asks_received > 72 · 0 · RED");
`after-walk-p4ws-17-regress-focus-vs-new-session.png` (fresh session 35ae48, no
FOCUS); `after-walk-p4ws-18-regress-summarize-selection-held.png` (the summary
with both chips lit). Screenshot 09 (the row as first listed) was dropped — the
pull had snapped to its top card and the frame showed nothing of the bar.

## Walk #5 — 2026-09-20, the owed specs (lean)

**Status: WHOLE (five specs, each once, one retry on each failure, one
screenshot per spec — the account at 80% of its session).** Same Bridge,
relit (the page loaded first time on session 35ae48; crew chips `echo ·
life 18` / `librarian · life 18`); same browser (780×493). The chat header
now carries its own **"▾ close"** — walk #4's hidden-tab friction cured.
Waits are the browser's own clock around each submit (the glass's counts
in brackets); stamps are the browser's (~05:30 PM). Echo was deselected
before the librarian's asks so only she answered.

| Spec | Verdict | What the Playwright saw |
|---|---|---|
| **SPEC-MONITOR-01** (re-walk of the cured wound) | **PASS** — wound CLOSED | "open the monitor" → the pull in **0.09 s** (feed revision "—" then counting; seven bodies "alive · until 05:31:32 PM"; walk #4's watch still listed). Asked "propose a watch that catches asks left waiting": the interlock in **2.7 s**, Cancel (default) holding focus. Clicked Yes at 05:31:22: without touching the pull, **"asks-awaiting-confirm — asks_received > 4 · 0 · RED"** stood in WATCHES beneath the older watch by the 05:31:42 read (the MARKERS list logged "05:31:22 PM · action · b3df0b5a · add-watch" at once). The leases kept breathing: "until 05:31:32" → **05:31:37** (05:31:22) → **05:31:47** (05:31:32) → **05:31:57** (05:31:42), all "alive", the pull's revision 11 → 13 in step with the footer. |
| **SPEC-FULL-01** (acquire half) | **PASS** — both halves now green | "Remember this text under the key hemp: The hemp rope held the ferry to the pier all winter. By spring its fibers had gone grey but not one strand had parted." → **2.7 s** (0.1 s): "Done. I've kept that text under the key "hemp" — every word exactly as you gave it…". "Repeat every word you acquired under hemp" → **1.0 s** (0.1 s): **"Here are the exact words I acquired under the key hemp: The hemp rope held the ferry to the pier all winter. By spring its fibers had gone grey but not one strand had parted."** — byte-for-byte the two sentences, none summarized away. |
| **SPEC-SCOPE-01** (the mind reads the window) | **FAIL** — the assist half still green | Typing "What did I ask you between yesterday and today?" drew the clock **"Fri, Sep 18 … today"** with no click, and the window rode the ask ("librarian took it on u:dev · **Fri, Sep 18 → Sat, Sep 19** · … (0.2 s)"). Her reply (**2.9 s**): **"I need to be plain with you: I don't have any record of what you asked me between yesterday and today. Looking at my notes, I can see the conversation we've had in this session — starting from when you first asked me about Spain's capital, then about colors, then about words to remember like PELICAN and HERON. But I have no notes about what happened between yesterday and today specifically. I won't invent a memory I wasn't given…"** — an apology, and "Spain's capital" was never asked (France was, two days ago). *Retry* (same words, **4.7 s**): the same denial, the same Spain, plus the hemp text. She does not answer from the window the glass drew for her. |
| **SPEC-SESSION-01** (short version only) | **FAIL** | "list my sessions" (**0.02 s**): ten sessions newest first — "1. 05:32:33 PM · 7 asks · "What did I ask you between yesterday and today?" · (this one) — 2. 03:12:00 AM · 0 asks — 3. 03:08:52 AM · 4 asks · "propose a watch…" — …" — time, count, last words; **no short-version line beneath any earlier session**. *Retry* after the mark step: the same list, still none. |
| **SPEC-MARK-01** | **PASS · PASS · PASS · FAIL** (the critique never reached the chat) | Typed "mark this as improvement: the binder should be lime": the chat printed the soft line **"marked ask_f63f1cccdccbd9f4 as improvement — critic asked to act"** (in place at the next read; my words are not echoed as a bubble). "open the monitor": the **MARKERS · the open vocabulary of why** view (groups quality · improvement · structural; kinds action intention objective observation thought) listed **"05:33:28 PM · improvement · erson:jb · ask_f63f1cccdccbd9f4 — the binder should be lime · why?"**. Clicked **quality**: the row vanished (the others stayed); clicked it again: the row returned. Clicked the row: the chat printed **"why · improvement (ask_f63f1cccdccbd9f4) ← objective (ask_f63f1cccdccbd9f4)"** in **0.06 s**. The critique: **nothing arrived in the chat** in 3 min 40 s (05:33:28 → 05:37:07). The OBJECTIVES band shows the critic did act — a row "A marker of kind 'improvement' was set on ask_f63f1ccc… by did:orreth:person:jb: the binder should be lime. Act on it as your role re… · critic · replied · 05:33:28 PM" — so the critique exists one door away, but the chat that promised "critic asked to act" never showed it. |

**Friction, one line each:**
- Marker authors are cut to eight characters: "erson:jb" (person:jb), "e kernel" (the kernel).
- The marker's why prints as ids — "improvement (ask_f63f…) ← objective (ask_f63f…)" — not the objective's words.
- The scope journey line carries the window the reply then denies.
- The sessions list carries an empty session ("2. 03:12:00 AM · 0 asks") with nothing to load.
- The MARKERS view sits between WATCHES and HARNESS with no gap of its own.
- The librarian's journey lines read "read the session's results by monitor, echo" even for a plain acquire.

**Wound calls, for the lead's ruling:** SCOPE-01 — a human asks what they asked between yesterday and today; the glass draws the window, and the mind answers "I don't have any record" and names an ask never made, twice. MARK-01's fourth bar — "critic asked to act" and then silence in the chat while the critique sits in the band. MONITOR-01's walk-#4 wound is closed.

**Not walkable on the human path:** an opt-out session (no typed words for it in the glass); kill a body (as before).

**Walk #5 evidence** (same folder): `after-walk-p5w-01-monitor-watch-live-leases.png`
(both watches in view, leases fresh, the pull untouched); `after-walk-p5w-02-full-acquire-repeat-verbatim.png`
(the two sentences back exactly); `after-walk-p5w-03-scope-recall-reads-window.png`
(the clock window drawn; the denial beneath); `after-walk-p5w-04-sessions-short-versions.png`
(the list without short versions); `after-walk-p5w-05-mark-markers-view-and-why.png`
(the marker under quality; the why line in the chat).
