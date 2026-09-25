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

## Walk #6 — 2026-09-19, intent sp1 + the P5 owed specs (lean)

**Status: WHOLE (five specs, each once, one retry on the one bar that
failed first, one screenshot per spec).** Same Bridge, relit (the page
loaded first time and restored session 35ae48 with its eight asks; crew
chips `echo · life 22` / `librarian · life 22`); the browser at
**1180×760** this walk so the Analyzer and the chat could stand side by
side. Waits are the browser's own clock around each click or submit;
stamps are the browser's (~11:00 PM; the host's clock read 16:00). The
librarian alone was lit for her asks (the restored selection). Human
path only: click, type, read, wait; no door, no database.

| Spec | Verdict | What the Playwright saw |
|---|---|---|
| **SPEC-ANALYZE-01** | **PASS · PASS** w/ friction | One Escape to the bare bridge, then the floor hatch "A N A L Y Z E R ▴": the words were painted **0.02 s** after the click (the pull still sliding up) and nothing in the chat moved — no body asked. **INTENTIONS · standing purposes — the kernel's and yours**: "keep this world resilient: when a watch goes red, get it green · resiliency · kernel · standing · 1 objective · 2 thoughts · 2 watch-reds · 10:38:31 PM · **stop**" (title "rule 11: recorded, never deleted"), then two schedules folded in as intentions ("Review what was asked of you today… · schedule · role · 6 objectives"; "run the harness against my golden set · schedule · kernel · 12 observations"). **OBJECTIVES · everything asked**: five asks with their kind counts ("1 improvement · 1 thought", "1 action"). The MARKERS view beneath, groups and kinds as before. An origin: the Resiliency row opened its tree in words in **0.03 s** (watch-red · watch-red · objective · thought · thought). An objective row ("Repeat every word you acquired under hemp") opened the chat in **FOCUS · ask 093fe799 · librarian · now** with the reply and its journey chain inline in the row. Typed **"follow up on this by counting how many words that hemp text had"** (chip read OBJECTIVE): the chat printed **"follow-up → under Repeat every word you acquired under hemp"** and the librarian counted **24 words** in **1.95 s**; the origin's row read "librarian · replied · **1 objective**" at the next paint and the MARKERS view listed "10:58:46 PM · objective · jb · ask_4b06f14e…" at once. Not "that tree alone": the pull keeps every origin listed with the one opened; an objective's door shows its reply, not its children (the follow-up is a count, not a row). |
| **SPEC-INTENT-01** | **PASS · PASS · PASS · PASS** w/ friction (the crew's reply is one click deep and cut) | Typed slowly **"keep this world resilient: when a watch goes red, get it green"**: the KIND chip read **INTENTION** from the words ("reads as an intention · click to flip · or type “thought: …”"); one click flipped it to THOUGHT, the next to OBJECTIVE, the third back to INTENTION; sent as INTENTION. In **0.05 s**: **"intention declared · serves resiliency · wakes on watch-red — its objectives will show here and in the ANALYZER · stop it there, any time"**. The Analyzer listed it first: "keep this world resilient… · resiliency · **human** · standing · 11:00:36 PM · **stop**", above the kernel's own row of the same words. "open the monitor" → the pull in **0.03 s**, the chat re-dressed to "FOCUS · the Monitoring workspace · its agent, monitor". "propose a watch that no body is dormant" → **"Are you sure? The add-watch act is consequential…"** in **11.2 s**, Cancel (default) holding focus. Clicked **Yes — do it** at **11:01:50 PM**: "Done, on your word: watch_a44ed3b2a5" at once. **3.0 s** after the Yes the chat printed, twice, **"on the kernel's word · “keep this world resilient: when a watch goes red, get it green” → planner: the next objective? · the ANALYZER shows the rest"**, and within **~4 s** two more: "… → **librarian: Get bodies_dormant below the alert threshold on watch_a44ed3b2a5 to restore the watch to green.**" and "… → **librarian: Investigate why bodies_dormant has exceeded its threshold on watch_a44ed3b2a5 and restore it to safe levels.**" The Analyzer: my row grew "**1 objective · 1 thought · 1 watch-red**", the kernel's "2 objectives · 3 thoughts · 3 watch-reds"; my tree read **watch-red** "watch 'bodies-dormant-alert' went red: bodies_dormant > 0.0, value 0 · the kernel · 11:01:52 PM" → **objective** "Investigate why bodies_dormant… · librarian · replied · 11:01:55 PM" → **thought** "INTENTION (serves resiliency): … · planner · replied · 11:01:52 PM". The crew's reply: **not in the chat**, and a click on the objective's twig did nothing. *Retry*, a click on the twig's words: the chat printed **"librarian · replied — I need to tell you plainly: I don't have the tools to investigate system metrics, watch states, or dormant bodies in your infrastructure. The ask you've named… is a directive for your operations crew, not a task I can execute. Wh"** — cut there. Not on the glass: the spec's words "on JB's word · owned by the kernel" (every line reads "on the kernel's word", the human's intention included); an "action" row under the objective (the tree reads intention → watch-red · objective → thought). |
| **SPEC-SCOPE-01** (the mind reads the window) | **PASS** w/ friction — walk #5's wound CLOSED | Typed "What did I ask you between yesterday and today?": TIME drew **"Fri, Sep 18 ——\|—— today · 47 h"** with no click. Her reply in **4.3 s**: **"I need to be plain with you: I don't have any record of what you asked me between yesterday and today. Looking at my notes, the window you're asking about runs from 2026-09-18T00:00 to 2026-09-19T23:04 — that's yesterday and today both. And I can see everything that happened in that window clearly written down: · You asked me about Spain's capital · … between last Monday and today … · … since yesterday … · … say hello and goodbye · … remember the words PELICAN and HERON · … count the words in the hemp text · … what you'd asked between yesterday and today … So here's the truth: what you did ask me between yesterday and today is all written right here in my notes."** Journey: "librarian took it on u:dev · **Fri, Sep 18 → Sat, Sep 19** · read the session's results by monitor · completed 11:04:32 PM (0.1 s)". She reads the window now — its bounds to the minute, seven asks inside it — but her first sentence still denies it, and "Spain's capital" is still listed (walk #5: never asked). |
| **SPEC-SESSION-01** (short version only) | **PASS** w/ friction | "new session" in the chat's header at **11:06:38 PM**: the transcript emptied in **0.9 s**. "list my sessions" (**0.1 s**): "**1.** 11:06:38 PM · 0 asks · (this one) — **2.** 11:01:55 PM · 2 asks · keep this world resilient… · “Investigate why bodies_dormant…” · **23:01 asked: INTENTION (serves resiliency): keep this world resilient… OBSERVED: a marker of kin… / planner replied (23:01): In** — **3.** 11:05:40 PM · 12 asks · “A marker of kind 'improvement' was set on ask_40a9…” · **03:12 asked: Both of you: name one color, in one sentence. / librarian replied (03:12): I'm a librarian, and I keep records… / 03:12 asked: Bot** — 4. 03:12:00 AM · 0 asks — 5. 03:08:52 AM · 4 asks · “propose a watch…” · 02:59 asked: Grade the answers… / grader replied (02:59): Nothing here to grade… — …" Every archived session with asks carries its short version beneath it, sessions predating the Digest included. |
| **SPEC-MARK-01** (fourth bar) | **PASS** — walk #5's wound CLOSED | After the scope ask, typed "mark this as improvement: the binder should be lime" at **11:05:40 PM**: **"marked ask_40a9450dd854cc18 as improvement — critic asked to act"** in **0.1 s**; at **0.3 s** the kernel's ask stood in this chat — **"A marker of kind 'improvement' was set on ask_40a9450dd854cc18 by did:orreth:person:jb: the binder should be lime. Act on it as your role requires. → critic — on its way…"** — and the critique arrived whole, labelled **critic**, on its own: **"CRITIQUE · What the residents brought into this session: The librarian was asked three times… The contradiction: … Both cannot be true. What holds: The hemp text itself is consistent — 24 words… The one thing most worth fixing: The librarian needs to give one true account of whether it holds a record…"** — by my next read at 11:05:56 PM (**≤ 16 s** after the mark); journey "critic took it on u:dev · read the session's results by librarian, monitor · completed 11:05:40 PM (0.2 s)". |

**Friction, one line each:**
- The chat's transcript is a sliver (two lines) at 1180×760 once FOCUS, INCLUDES and TIME stack; the resize handle rescues it (334 → 660 px by a drag) but nothing points a newcomer to it.
- The KIND chip keeps its last read after a send — an empty composer reads OBJECTIVE.
- The chip's click cycles three kinds; "one click flips it" is three clicks back to where you were.
- The two "on the kernel's word … → planner" lines are identical — nothing says which intention (the human's or the kernel's) each serves; a human's intention is credited to "the kernel's word".
- The red watch's words read green: "bodies_dormant > 0.0, value 0" for a watch that went red.
- A tree twig shows the pointer across its whole row but only its words are the door; the reply it prints is cut at about 300 characters.
- The interlock on "propose a watch that no body is dormant" took 11.2 s to arrive (walk #5: 2.7 s).
- An open Analyzer row closes at the next feed repaint (every few seconds).
- The sessions' short version cuts mid-word ("planner replied (23:01): In", "asked: Bot") and shows a 12-ask session's two oldest asks; the empty "03:12:00 AM · 0 asks" session is still listed; the kernel's intention session sits in "my sessions" as #2 with the planner's prompt as its digest.
- The librarian's journey still reads "read the session's results by monitor" for plain asks, and "(0.0 s)" for a follow-up that took 2 s.
- The critic's chronology is reversed (today's full accounting is "the first asking", walk #5's denials "the second and third"); its journey stamps "completed (0.2 s)" while the words are still streaming; the marker's own words ("the binder should be lime") appear nowhere in the critique.
- The scope reply's first sentence denies the record its next paragraph lists.

**Wound calls, for the lead's ruling:** INTENT-01 — the objective a red watch births lands on the librarian, who answers she has no tools for it: the loop turns, and every objective it birthed today is un-actionable by its runner. INTENT-01 — the crew's reply to a kernel-filed objective never reaches the chat; a human finds it only by clicking a twig's words, and then cut short (the spec says it "lands under the objective"). SCOPE-01 — she reads the window now, but opens by denying it and still lists "Spain's capital"; the lead rules whether a self-contradicting reply passes P6. The spec's "on JB's word · owned by the kernel" is not on the glass — "on the kernel's word" is; the spec or the glass must agree. SCOPE-01's and MARK-01's walk-#5 wounds are closed.

**Not walkable on the human path:** IH-3's 10k-marker budget (the ground holds dozens); the stop (one click with a confirm — withheld, lean).

**Walk #6 evidence** (same folder): `after-walk-i1w-01-intent-declared-red-watch-births-objective.png`
(the human's intention first under INTENTIONS with its stop, its tree watch-red → objective → thought; the monitor pull live; the chat in FOCUS · the intention); `after-walk-i1w-02-analyzer-origin-follow-up.png`
(the Analyzer cold-painted, the hemp origin opened with the follow-up counted under it; the chat in FOCUS · ask 093fe799); `after-walk-i1w-03-scope-mind-reads-window.png`
(her reply's close and the journey line carrying Fri, Sep 18 → Sat, Sep 19); `after-walk-i1w-04-sessions-short-versions.png`
(the list newest first, the short-version lines beneath sessions 2 and 3); `after-walk-i1w-05-mark-critique-arrives-in-chat.png`
(the critic's critique whole in the chat, its journey beneath).

## Walk #7 — 2026-09-21, JB walks Phase 6 (the human walk; the Playwright is retired)

**Who walked:** JB, in the glass, narrating; Fable keeps the register. Bridge relit at
1f63e31 with `SPINE_MASTERS=did:orreth:person:master`. SPEC-L3-01 first.

| Bar | What JB saw | Verdict |
|---|---|---|
| Enroll (1.1) | "enroll my authenticator": the QR drew, the first code took — "authenticator enrolled". "Pretty smooth up to that point." | **PASS** |
| Re-enroll is grave (1.2) | "enroll my authenticator" answered *not confirmed — you already hold an authenticator; re-enrolling is grave: say "enroll my authenticator with code 123456"* — JB typed that sentence with 123456 literally, then with a real code; the kernel then drew a NEW QR **with the otpauth URI and the secret in plain text in the transcript**, kept the "First 6-digit / Finish enrolling" inputs open, and two later codes answered *not confirmed — nothing changed · type the code your app shows now*. JB: "part of 1.2 seemed to not take"; "if it was successful it is confusing to show another input field on the success". | **FRICTION ×4 (wounds)** — see W1–W4 |
| Stop an intention (1.3) | In the ANALYZER JB clicked **stop** on the FIRST row — his own human intention — and got *sure? click again to rest it*; the second click rested it (*intention at rest — recorded, never deleted*). JB: "you have effectively got 2nd level human confirm down. However, would have been better to receive the input field to provide my 3rd Level MFA, BEFORE it disabled the Intention." The kernel's row (second) still stands with its stop; the L3-master half was not reached. | **JB's CALL → W5** |
| The Analyzer under the intention | A wall of repeated `watch-red → objective` pairs (the loop's 30-minute churn, the librarian's un-actionable objectives), "EXPECTED IMPACT? … THE CHANGE: … THE GROUND …" raw prompt text as an OBJECTIVES row, "MITL acquired the Orreth ontology v0" as an objective per relight. JB: "rest of these I can't tell what's going on." | **FRICTION → W6** |

**Wounds and calls (the line stops here until cured — 0005's wound rule):**
- **W1 — the re-enroll asks in the wrong voice.** A guidance message wears the refusal's words ("not confirmed") and asks the human to retype a sentence with a placeholder code. Cure: the grave re-enroll asks for the CURRENT code in the chat's code row (sp1's L3-code row: typed code, click, Cancel default) — words equal links, no sentence to retype.
- **W2 — the secret on the glass.** The otpauth URI with the secret printed in the transcript and stays there. Cure: the QR only; the URI/secret behind a "can't scan? reveal the secret" click that masks again on the next repaint, never in the transcript's record.
- **W3 — success keeps its inputs open.** After the new QR, the "First 6-digit / Finish enrolling" row stays after the step succeeds and the two "not confirmed — nothing changed" lines do not say WHICH step refused. Cure: each step collapses on success; every refusal names its step ("finishing the NEW authenticator: that code is not the new entry's — type the code the new Orreth entry shows").
- **W4 — did the re-enroll finish?** Two "nothing changed" replies after the new QR: either JB typed the OLD entry's code or the finish step verifies against the wrong secret. Cure: a law in the suite — re-enroll → new QR → finish with the NEW secret's code → confirmed; the old secret refuses by name.
- **W5 — JB's lock: stopping ANY intention asks for the code BEFORE it rests.** The two-click "sure? click again" in the Analyzer is not governance felt in the chat (P12: approvals live in the chat). Cure: the stop of a human's intention is L3-code (the code row in the chat, the intention rests only when the code is right); the kernel's intention is L3-master AND the code; the Analyzer's stop opens that row instead of a second click.
- **W6 — the intention tree is a wall.** Cure: fold repeats ("watch 'bodies-dormant-alert' went red ×8 · latest 03:44 PM" as one twig with a count), objectives under their watch-red, thoughts folded; the OBJECTIVES band shows objectives only — the impact ask is a thought under its change (its words start with the change, not the prompt), the ontology acquisition is an observation, never an objective.

**Walks 2–4 continue on the same Bridge; cures land after "down", then SPEC-L3-01 is re-walked.**

### Walk #7, continued — SPEC-EXPORT-01 (walk 2)

| Bar | What JB saw | Verdict |
|---|---|---|
| Two answers, plan, grade (2.1–2.2) | With both residents lit, "echo, what is today's date?" fanned out to BOTH: echo echoed the question (it is an echo — the body proven before the mind), and **the librarian answered in echo's voice** — her reply was echo's words verbatim plus a parenthetical about the window. Alone, echo echoed again. "plan" produced a real plan naming the three gaps (the librarian lacks tools for the loop's objectives; echo's role is ambiguous); "grade" gave the planner an A and every date answer an F — "the grader seemed to be SPOT ON." | plan/grade **PASS**; the date **FAIL** (W7 · W8 · W12) |
| The export (2.3) | "export compliance for this session": 10 records · the chain of who acted for whom unbroken on every record · proof L1 ×10 · unsigned (hash-chained); the plan row's chain read jb → echo → librarian → planner, the grade row's jb → planner → echo → librarian → grader; both downloads saved; "for between Friday and today" gave 121 records. | **PASS** w/ friction (W10 · W11) |

**Wounds and frictions from walk 2:**
- **W7 — "echo, …" should reach echo alone.** A name at the head of the ask (or @name) selects that resident; the fan-out stays for an unaddressed ask with several lit. And a resident's nature shows on its chip/card ("echo — repeats your words back; no mind" — P18): JB: "I may not know how you have echo setup."
- **W8 — the librarian wore echo's voice.** In a fan-out her recall packed echo's fresh result and she returned it as her own. The pack must label another body's result as THEIRS and the system words must say "never answer in another body's words"; the earlier "I'm done." reply (a fifth identical objective from the loop) shows the un-actionable-objective loop wearing her down — the loop must not re-file an objective its runner said it cannot act on (0007's honest limit, now a felt wound).
- **W10 — a copy for humans.** Every reply (plan, grade, any answer) gets a copy button; the export's words column strips markdown marks (it showed "# PLAN … **What:**" raw) and keeps the first line whole.
- **W11 — the export table's words.** The "why" column read "thought" ten times — it should carry the marker's WORDS (the objective it serves), and an ask row in a fan-out names its target ("jb → echo (ask)").
- **W12 — every body knows the clock.** "what's today's date?" earned an F from the grader and it should be unanswerable only by an echo: the kernel gives every body the time and the world in its system words (the charter's first bar is "the temperature outside"; the date is the floor of it).

**JB's law, spoken before walk 3 (2026-09-21) — binds every body, not one cure:**
- **Every resident and firmware agent wears the Orreth ontology** — the part that serves its
  prescribed role, so the body knows the risks of its own seat (what it may not do, what it
  must ask for). MITL's corpus is the seed; each body gets its role's slice, not the whole.
- **Every body MUST know TIME.** Time is the backbone of Orreth's origin assertion (lived time
  is monotone — covenant rule 8; every fact wears occurred_at); a body that cannot say the
  date cannot reason about origin. The kernel gives every body now-in-UTC, the world, and the
  human's zone; bodies convert zones for humans in plain words. Part of the fluid, immersive
  experience — never a tool a body has to remember to call.

### Walk #7, continued — SPEC-MITL-01 (walk 3, first half)

| Bar | What JB saw | Verdict |
|---|---|---|
| Summon (3.1) | "summon MITL": the chip turned on, the sysline expanded the name and said what to do next. JB: "oh that's cute and I like; correct behavior and feeling." | **PASS** |
| The canon answers (3.2) | "what does the canon say about the meter?": a whole, correct answer citing the covenant and the canon, with its meter line — JB: "my vision of an 'energy-packet'." Citations read as file paths ("SKILL.md#3", "0005-…md#10"). | **PASS** w/ friction (W15) |
| The monitor and the impact door (3.3) | With the chat resized above default and the MONITOR pull open, the chat covered the pull; clicking the pull behind did not raise it. Typing "no body is dormant" to the monitor: a full, honest reply — it found **the watch `bodies-dormant-alert` RED while its metric reads 0 (0 > 0.0 is false)** and offered to propose a watch, but proposed none — so no hold row, no "expected impact?" to click. The same board shows `asks-left-waiting — asks_received > 72` at value 5 · RED. | **BLOCKED by W13 · W14** |

**Wounds and frictions from walk 3 (first half):**
- **W13 — pulls and the chat share the width.** When the human has resized the chat wider than its default and a pull opens, the two must stand side by side — the chat yields on the x-axis (never covers the pull), and a click on any pull raises it above the chat. "You're the pro friend."
- **W14 — WATCH STATES ARE STUCK RED (kernel wound).** `bodies-dormant-alert` is RED with value 0 against `> 0.0`; `asks-left-waiting` is RED at 5 against `> 72`. The watch's state does not follow its metric: it went red once and never returned to green. This is the root of the Analyzer's wall (walk 1, W6) and of the librarian's exhaustion (walk 2, W8): the resiliency loop fires on a red that is not real, every thirty minutes. Cure: a watch's state is a pure function of its metric NOW (re-evaluated on every beat); red → green is a recorded transition; the intent loop wakes on the red TRANSITION only, never on a standing red; a red that has not changed re-files nothing.
- **W15 — citations in human names.** MITL cites "SKILL.md#3" and "0005-v1-scope-and-build-plan.md#10"; the glass should say "the covenant, rule 5" and "the build plan, Phase 6 sp2" — the path stays in the record.
- **Friction — a bare phrase to the monitor.** "no body is dormant" reads as a statement; the monitor answered well and offered the watch, but the offer needs a "yes" the walk did not give. The monitor's offer should end with a one-click "propose it" (the interlock then arrives) so the human is never asked to type "yes" to a question.
- **W16 — a new ask got an old reply, unthought.** "propose a watch that no body is dormant" (ask_2a70fe659a36b88a) replied in 0.2 s with the previous ask's reply verbatim under a new first line; the ground shows NO meter row for that serve (the earlier ask, ask_1af97728d8292ba7, has one: Haiku, 1591 in / 202 out). Something on the serve path answered from the record instead of thinking — and the monitor's "propose" verb (the interlock, 11 s in walk #6) never ran. The builder finds the shortcut by reading the serve path for a repeated ask in one session and removes it: a new ask is ALWAYS a thought (the meter is the proof), the record is context never the answer. Blocks 3.3 until cured.

### Walk #7, continued — SPEC-MITL-01 (walk 3, second half) and SPEC-PLACE-01 (walk 4)

| Bar | What JB saw | Verdict |
|---|---|---|
| Stop the kernel's intention + impact (3.4) | "stop the kernel's resiliency intention": the kernel held it — "This needs a second named person … a declared master — never you — confirms it with a click. Cancel is the default" — with "expected impact?" on the row. Clicking it drew the ground at once (bodies planner · librarian; chains; the intention's 25 markers; cost so far 24,825 + 334,548 tokens; consequence grave → L3-master) and MITL's words beneath: who and what it touches, chains, intentions, cost, no recovery path but a human re-cut, four things to watch after, VERDICT BY THE LADDER: grave — needs L3. Cancel stayed default. "dismiss MITL" left the crew, recorded. | **PASS** w/ friction (W5 · W15 · W17) |
| Where a body stands (4.1) | "crew": every card reads "stands on local · cpu · cell local · metal any" with its self, covenant, template hash, tools; "where does the librarian stand?" → "where · librarian stands on local · cpu" in place, no click. The pull and the chat stood side by side. | **PASS** |
| A refusal at birth (4.2) | Fable set `"placement": {"metal": "gpu"}` on the echo template and relit: stderr "echo refused at birth — metal gpu is not here (cpu) (recorded; the rig runs without it)"; the crew door shows echo `alive false · refused true · lives 0 · why: refused: metal gpu is not here (cpu)`; the other seven bodies seated. | **PASS** on the door — JB reads the glass next |

- **W17 — the journey's clock lies.** MITL's long impact reply and the crew agent's reply both read "completed (0.2 s)" — a real thought of that length is not 0.2 s. The journey's completed span measures the wrong interval (walk #6 saw "(0.0 s)" for a 2 s follow-up). Cure: the span runs from the ask's receipt to the reply's landing, on the ground's clock, and the meter row is its witness.
| The refused card and the words (4.2–4.3) | "crew": echo greyed — "refused at birth — metal gpu is not here (cpu) · recorded 06:02:46 PM · never started · the rig runs without it · fix its template to seat it (nothing to stop)". "where does echo stand?" → "echo is refused here — metal gpu is not here (cpu) · recorded; fix its template to seat it". The librarian answered as usual. BUT the residents rail still listed echo, green and selectable, and "echo, are you out there?" sat at "the ask is on its way…" forever. | card + words **PASS**; the rail and the door **W18 · W19** |

- **W18 — the rail must tell the truth (rule 7).** A refused body still stands green and selectable in the residents rail while the crew card says refused. One picture: the rail shows it greyed with "refused — not here", never selectable; a refused body cannot be lit.
- **W19 — an ask to a body that is not here refuses at the door.** The ask to echo went "on its way…" and nothing will ever serve it. The door answers in plain words at once ("echo is not here — refused at birth: metal gpu is not here (cpu); fix its template to seat it"), the ask is recorded as refused, never left in flight.
| Echo comes home (4.4) | Template reverted, Bridge relit: echo seated again — same self `did:orreth:agent:4af83d08…`, life 27 → 28, "stands on local · cpu"; the refusal row stays. JB: "echo is back, life 28." | **PASS** |

**Walk #7 — the close.** Four specs walked by the human they are for. **EXPORT-01 PASS** (w/ friction) · **PLACE-01 PASS** (W18 · W19 owed) · **MITL-01 PASS on 3.1 · 3.2 · 3.4, BLOCKED on 3.3** (W14 · W16) · **L3-01 FRICTION** (W1–W5; re-walk owed after the cures). Nineteen wounds and frictions, one law spoken (ontology + time for every body). JB's verdict: *"the interoperability and flow is vastly better. Clearly heading into the right direction."* The line stops here until the wounds are cured (0005's wound rule); the cure spoonful reads this section as its spec.

**Cures landed (kernel) — 2026-09-21:**
- **W5k — the stop asks for the code first, for ANY intention.** `intent.stop_demand(kind)`: a human's or a role's intention is **L3-code** (the code row; it rests only when the code is right); the kernel's is **L3-master with `needs_code`** — the ORDER BUILT: the asker's code first (`/confirm` with `code` → `{step: "code", next: "master"}`, the hold stays), then the master's click settles it; a master clicking before the code, the asker clicking as master, a wrong code: the one face. `intent.stop` raises `ProofRequired(level, what, needs_code)` for a bare stop of ANY intention; `/intentions/stop` holds it (`{held, level, needs_code}`); the hold on `/ask/<id>` wears `level` (+ `needs_code` · `code_ok` on the kernel's). Fixture: `proof-v0.json` `stop_demand` ×3. Law: `test_cure_walk7.py::test_w5_the_stop_of_any_intention_asks_for_the_code_first` (+ `test_proof.py`'s kernel-stop tests replaced by name: code before master).
- **W8 (loop) — the loop hears a runner that cannot act, once.** The seat words teach every body: an objective it lacks the tools for is answered opening with `CANNOT ACT:`. `intent._hear_runners` reads each objective's reply once (`spine_intent_turns.heard`); a decline marks ONE `improvement` under the intention ("runner cannot act: librarian said … — needs a body with the tools for it") and records the crew's shape (`blocked_crew` = hash of every body's name + capabilities); `plan()` plans nothing for a blocked intention until the crew changes (a body joins or declares a tool), then plans again. `/intentions` rows carry `blocked` · `blocked_note`. Law: `test_w8_the_loop_hears_a_runner_that_cannot_act_once_and_waits_for_the_crew_to_change`.
- **W8 (voice) — another body's words are THEIRS.** The pack labels every other body's reply `ANOTHER BODY'S WORDS — echo replied to '…': '…' (theirs; cite echo by name, never repeat it as your own)`; a body's own earlier replies read `(context, never the answer)`; the seat words carry the law ("never answer in another body's words … when the ask is addressed to another body by name, say so and answer only your own part"). Law: `test_w8_another_bodys_words_are_labeled_theirs_and_the_law_is_in_the_system_words`.
- **W12 + JB's law — every body knows time and its seat.** `Resident.seat_words` is appended to EVERY body's system words (residents, firmware, MITL): `NOW is <UTC to the second>`, the human's zone (the ask's `zone` → the session's `zone` → the dial `SPINE_HUMAN_ZONE`, default **America/Denver**) with the local time and today's date there, "convert times for humans into their zone, and say the zone", the world (`ev.scope()`) and the body's kind/function, the covenant's slice (rules 2 · 4 · 5 · 8 · 11 in one paragraph), and the ontology slice the template names (`"ontology": ["…"]` — v0: the best-matching passage from MITL's acquired corpus per entry; "not acquired on this ground yet" said plainly when the corpus is empty). `/ask` accepts `zone`. Law: `test_w12_every_body_knows_time_its_world_its_zone_and_its_seat` (a stub gateway that answers with its system words; "what's today's date?" returns today's date).
- **W14 — WATCH STATES (the root wound): the sense of a watch was inverted.** Found: the state WAS a pure function of the metric — but the kernel judged a watch GREEN while its condition held, and every watch on the board was authored by the monitor mind (and read by JB) as an ALERT: `bodies_dormant > 0` meant "red when a body is dormant". So `> 0` at value 0 read RED, and the 15-second presence lease flipping made real transitions every few minutes — the Analyzer's wall and the librarian's exhaustion. Cure: a watch's condition is what it catches — **RED when `metric op threshold` holds, green otherwise**; judged on every beat (`monitor.judge`); red ↔ green are recorded transitions (`last_ok` + `since` on the row, the fact `orreth.watch.turned.v1` with `from` · `to` · the value); the loop wakes on the red transition alone, a standing red re-files nothing. `/monitor` watches carry `red` · `state` · `since` · `reads` ("red when bodies_dormant > 0.0 · now 0 → green"); the add-watch tool and the monitor's binding say the sense. Fixture: `watch-v0.json` (new, 10 cases). Law: `test_w14_a_watch_follows_its_metric_and_the_loop_wakes_on_the_red_transition_only` (+ `test_intent.py::test_ih1…` and `test_monitor.py`'s watch law replaced by name under the sense). **Relit:** the three live watches read green · red · green for values 5 > 72 · 5 > 4 · 0 > 0 — the board follows its metrics.
- **W16 — the record corrected: the second ask WAS thought.** Found on the ground: `ask_2a70fe659a36b88a` has its meter row (Haiku, 3259 in / 338 out, `at` 00:42:36.878Z — the walk's "no meter row" was a misread); there is NO shortcut on the serve path. The reply looked verbatim because the pack handed the mind its own earlier reply and it wore it again; the "0.2 s" was W17. Cure: the seat words say "a new ask is always thought anew: your earlier replies are context, never the answer" and "when the human asks you to propose … CALL the tool — never describe it"; the monitor's binding and the add-watch tool say it too. Law: `test_w16_two_asks_in_one_session_are_two_thoughts_and_the_propose_phrase_reaches_the_verb` (two asks → two meter rows, two thoughts; the phrase through a stub acting mind reaches add-watch and holds at the interlock). Honest: whether the REAL mind calls the tool is the walk's to prove — the words teach it, the suite cannot force it.
- **W17 — the journey's clock: `now()` was the transaction's START.** Found: `replied_at = now()` and the meter's `at` land inside the serve's one transaction, and Postgres `now()` is the transaction start — so the span read ~0 s whatever the thought took (the meter row's `at` equalled `replied_at` to the microsecond). Cure: `clock_timestamp()` for `replied_at` (resident, proof's kernel acts, the refused ask) and the meter's `at` (both gateways); the glass's `secs(asked_at, replied_at)` now reads receipt → landing on the ground's clock. Law: `test_w17_the_journey_span_runs_from_receipt_to_landing_on_the_grounds_clock` (a 0.5 s stub thought reads ≥ 0.5 s; the meter agrees).
- **W19 — an ask to a body that is not here refuses at the door.** `dispatch.absent(conn, name)` (refused at birth since its last join, or never joined this world) → `submit_ask` lands the row with status **`refused`**, the reply `"<name> is not here — refused at birth: metal gpu is not here (cpu); fix its template to seat it"` (or "no body of that name has joined this world"), `served_by` the kernel, `replied_at` at once, the fact `orreth.ask.refused.v1` (`target` · `reason` · `session`; chain `[person, "the kernel"]`), the marker the ask would have worn — never an `ask.received`, never in flight; a fan-out drops the absent body and its refused row says so; the export carries it as kind `refused`. Fixture: `ask-v0.json` (new). Law: `test_w19_an_ask_to_a_body_that_is_not_here_is_refused_at_the_door`. Tests that asked bodies never joined (`test_intent` ih2 · `test_markers` · `test_mitl`'s impact) now join them first — by name.

**Cures landed (glass) — 2026-09-21:**
- **W1 · W3 · W4 — the re-enroll flow.** `enrollWords` reads `/proof` first: when an authenticator is held, the SAME code row the L3 confirm uses opens (`codeRow`: typed code · click · Cancel default · Enter never submits) asking for the CURRENT code — no sentence to retype, no "not confirmed" voice for guidance (the old words "… with code 123456" still work as an alias). On a right code the row COLLAPSES to one line (`stepDone`: "✓ current authenticator proven · HH:MM"), the new QR draws (`drawEnroll`) with ONLY the "Finish the new authenticator" row; on its code that folds to "✓ new authenticator enrolled — the old entry is retired". Every refusal names its step (`stepRefused`: "proving the CURRENT authenticator: …" · "finishing the NEW authenticator: that code is not the new entry's — type the code the new Orreth entry shows now"). Kernel: `/enroll` already took `code` as a field; the W4 law `test_cure_walk7_glass.py::test_w1_w4_…` proves re-enroll → pending new secret → the OLD entry's code refuses at the finish → the NEW entry's code confirms and retires the old.
- **W2 — the secret off the glass.** The QR alone; the otpauth URI sits behind "can't scan? reveal the secret" (`.reveal`), masked again on the next repaint (`el()` hides every open `.copy`), never in the transcript's record (the enroll reply is a door answer, not an ask row — a reload re-draws nothing of it).
- **W5g — the stop asks for the code first.** `stopIntention` has no second click: the Analyzer's stop and "stop … intention" open the code row in the chat (`renderOutcome` → `holdRow("code")` for L3-code, and for L3-master with `needs_code` and `code_ok` false); `decide` reads `/confirm`'s `{step: "code", next: "master"}` and swaps in the master row ("✓ your code is right" · "now a declared master confirms with a click · cancel is the default"); the outcome line reads "intention at rest · “…” · proof L3-code". Cancel default at both steps; Enter never confirms.
- **W6 — the tree folds.** `foldTree`: consecutive `watch-red` twigs for the same watch fold into one twig with a count and the latest stamp ("watch “bodies-dormant-alert” went red ×8 · latest 03:44 PM"); an objective sits under its watch-red; thoughts fold under their objective ("▸ 3 thoughts under it · click to open"). The OBJECTIVES band shows kind=objective roots only; actions, observations and loose thoughts sit under a folded OBSERVATIONS head; a blocked intention wears "waiting for a crew that can act: …" (`/analyzer` rows carry `blocked` · `blocked_note`). Kernel: MITL's impact ask now STARTS with the change ("the change: keep the pantry stocked … — expected impact?") so the twig reads the change, never the prompt.
- **W7 — a name at the head selects the resident; every body says what it is.** `dispatch.address` + `glass.address_to` at the `/ask` door and `addressed()` in the glass: "echo, …" · "@echo …" · "librarian: …" reach that body alone (the label says "→ echo · by name"); the fan-out stays for an unaddressed ask. Every template and binding carries a one-line `nature`; `Resident.nature` lands on the join row (`spine_joins.nature`) and rides `/crew` and `/residents`; the rail chip and the crew card say it ("echo — repeats your words back; no mind").
- **W10 — a copy for humans.** `copyBtn` on every reply bubble (includes too) and on the export table (TSV); `stripMarks` gives the plain text. Kernel: the CSV's words column is plain (`export._plain`), the first line kept whole.
- **W11 — the export table's words.** Rows carry `marker_words` (the words of the objective the marker serves — its parent's, its own for a root; withheld with the row, and never borrowed from an opt-out session — P11) and `target`; the table's why column reads the words, an ask in a fan-out reads "jb → echo (ask)", the `refused` kind reads "refused at the door". CSV grows `target` · `marker_words` (test_placement's last-column assertion loosened to presence, by name).
- **W13 — pulls and the chat share the width.** `layoutChat` on every pull open/close and resize: a chat wider than the room left beside an open CREW/MONITOR pull yields on the x-axis (its chosen width remembered in `CHAT_YIELD`, restored when the last pull closes); a pointerdown on any pull raises it above the chat (`.raised`), a pointerdown on the chat lowers them. The grip stays.
- **W15 — citations in human names.** `mitl.TITLES` + `mitl.citation_name` + `mitl.citations()` (every passage key → "the covenant, rules 1–9" · "the build plan, Phase 6 — GOVERNANCE FELT" · "the agent canon, The third kind — firmware agents"), served on `/mitl` as `citations`; the glass's `cite()` renders `path#n` as the name with the path on hover.
- **W18 — the rail tells the truth.** `loadRoster` reads `/crew` (the cards' door, rule 7): a refused body's chip is greyed, disabled, "refused — not here · metal gpu is not here (cpu)", never lit (`SELECTED` drops it).
- **The monitor's offer gets a button.** `monitor.offer_in(reply)` reads an honest offer (the words "propose … watch" AND a backticked condition) → `{words, ask}` on `/ask/<id>` as `offer` when the monitor served; the glass draws "propose it" under the reply, which sends "propose a watch that <condition>" to the monitor — the interlock ("expected impact?", Cancel default) then arrives; the human never types "yes".
- **Feed wiring.** `onNotice` handles `orreth.watch.turned.v1` (sysline "watch “x” turned red · value v · since HH:MM · red when …"; the MONITOR pull's watch rows read `reads` · state · since) and `orreth.ask.refused.v1` (the kernel's words in the chat, "refused at the door", never "on its way…" — in a fan-out the refused reply counts toward the summarize offer); every `/ask` carries `zone` (the browser's IANA zone).
- **Conformance (0008):** `ask-v0.json` +4 `address`, `watch-v0.json` +3 `offer`, `mitl-v0.json` +3 `citation_name`. Laws: `spine/tests/test_cure_walk7_glass.py` (8). Suite **220** (202 → 220). Honest: the glass behaviour is JB's to walk (re-walk L3-01 and MITL 3.3); whether the REAL monitor mind writes its offer with the condition in backticks is the walk's to prove — no backticks, no button, the words still stand.

## Walk #8 — 2026-09-21 evening, JB re-walks Phase 6 after the cures (d6508fa · f5710f0)

| Bar | What JB saw | Verdict |
|---|---|---|
| Re-enroll (L3-01, 1.2 re-walked) | "enroll my authenticator": the code row asked for the current code; "✓ current authenticator proven · 08:00:10 PM" collapsed to one line; the new QR drew alone; the new entry's first code: "✓ new authenticator enrolled — the old entry is retired · 08:02:42 PM"; sysline "authenticator re-enrolled — grave acts will ask for its code". JB: "very smooth and clean." | **PASS** — W1 · W2 · W3 · W4 CLOSED |
| Stop the kernel's intention (3) | "stop the kernel's resiliency intention": the code row first — "✓ your code is right · 08:05:38 PM" — then the master row; the intention stands until the master clicks (as built: code, then master). JB read the standing state as "no change" — the hold's words should say the intention stands UNTIL the master's click. JB's own intention still shows "at rest" from walk #7's wrong stop: "looks wrong". | code half **PASS**; W20 · friction |
| Layout (4) | The chat yielded to the open pull. | **PASS** — W13 CLOSED (raise-on-click unreported) |

- **W20 — the reverse of a stop.** A rested intention cannot be brought back; JB's own resiliency intention sits at rest from a stop made under the wrong law. Rule 11 keeps the stop recorded; the cure is the reverse ACT: "restart" on a rested intention (the Analyzer row and the words "restart my resiliency intention"), grave through the same code row, recorded as its own fact, the intention standing again with its history whole.
- **W21 — a standing duty felt like harassment (the reasoning wound).** The librarian's role schedule "Review what was asked of you today and note one thing worth remembering" has fired hourly since 10:00 (12 objectives). Her pack carries her own prior replies as if a human re-asked the same question; she refused six times and wrote "I will not answer it a seventh time … This is a librarian keeping her word." JB: "important feature but feels like it didn't have the right level of reasoning — this being an agentic and understanding kernel, it shouldn't feel like automation." Cure: (1) a duty is FRAMED as a duty — the scheduler's objective text carries its cadence and its window ("your hourly review · since 07:00 PM · your earlier notes today are in your record: …"), never the bare sentence; (2) the pack labels prior runs as "your own notes from earlier runs" (hers, not a human's question); (3) seat words: a duty is served, never refused — when nothing is new the answer is one line ("nothing new since 07:12 PM"); (4) the human's chat shows a duty's reply folded to one line with the note, not the whole bubble, unless the human opens it; (5) the schedule's cadence shows on the Analyzer row ("hourly · 12 runs · last 08:12 PM"). A body that refuses its duty is a wound the harness should catch: add a harness check — "the duty answered, not refused".
| The monitor and the offer (5) | "no body is dormant": a FRESH thought (2.8 s, the clock true — W16 · W17 CLOSED): the board read true behind it (bodies-dormant-alert green since 07:55 PM — W14 CLOSED), and the monitor offered a watch again — but wrote no backticked condition, so no "propose it" button drew. "propose" alone earned a good "that's incomplete — name the metric, the operator, the threshold, the name" with an example. JB: "still NO button … did get a nice 'I need more data' which I do like." | reasoning **PASS**; the button **W22** |

- **W22 — an offer is a proposal, not a question.** The "propose it" button depended on the mind writing its condition in backticks — the wrong dependency. Cure: the monitor's seat words say: when a watch would help, PROPOSE it — call the add-watch tool with name · metric · op · threshold — the interlock hold arrives with Cancel as the default and "expected impact?" on it; the human's no is the cancel; never ask "would you like me to". The glass keeps a fallback: any reply containing "propose a watch" draws "propose it" (no backticks required). The harness gains a check: the monitor's offers arrive as holds.
| The interlock with the impact door (5, second half) | "propose a watch named dormancy-early-warning on bodies_dormant with >= and threshold 1": the interlock — "Are you sure? The add-watch act is consequential … cancel is the default, and doing nothing cancels" — with "expected impact?" on the row, Cancel focused. JB: "Must say I do LIKE the 'expected impact' — yummy." | **PASS** — MITL-01 3.3 CLOSED (W23 words) |

- **W23 — the interlock's words contradict rule 11.** "cannot be undone" — a watch can be rested later (recorded, never deleted). The words: "Are you sure? Adding a watch is consequential — it is recorded, and you can rest it later. Cancel is the default."
| Addressing by name (6) | "echo, what is today's date?" → "→ echo · by name": echo alone answered; the librarian silent. Echo echoed (its nature). JB: "not really a fan of all the assertion" — echo's self-narration ("I am echo — a plain-spoken echo — the body proven before the mind arrives … none summarized away") is noise when the chip already says what it is; the journey's "Mon, Sep 21 → Mon, Sep 21" read like the answer below the reply. | **PASS** — W7 CLOSED (W24) |

- **W24 — a body says its nature once, on its chip, not in every reply.** Echo's reply is the echoed words alone; the journey line shows a window only when the human named one (a bare ask shows none); when a body cannot answer by its nature, one plain line says so ("echo repeats; ask the librarian for the date") — the assertion belongs to the record (audit · replay · origin lineage), never to the bubble.
| Stop the kernel's intention — the master's click (3, finished) | The master's name typed, "Confirm as master" clicked: the kernel's Resiliency intention rested — "intention at rest · proof L3-master". JB: "yes, it rested with proof L3-master." | **PASS** — W5 CLOSED |

**Walk #8 — the close.** L3-01 re-walked GREEN on every bar (enroll · re-enroll by the code row · the kernel's stop by code then master; a human's stop by code stands proven in the suite — JB's own intention was already at rest, W20). MITL-01's blocked 3.3 CLOSED (the interlock with "expected impact?" — "yummy"). W7 · W13 · W14 · W16 · W17 CLOSED on the glass. Five small wounds remain for one cure (W20 restart · W21 the duty framing · W22 the offer as a proposal · W23 the interlock's words · W24 the bubble), plus the hold's words "stands until the master's click". After that cure: the four P6 rows move to PASS and Phase 6 closes.

**Cures landed (close) — 2026-09-21:**
- **W20** — `intent.restart`: a rested intention stands again with its history whole — a NEW fact `orreth.intention.restarted.v1` under the intention's marker with its proof level, the stop's fact and `stopped_by` kept; grave through the stop's own ladder (`restart_demand`: a human's L3-code, the kernel's L3-master with the asker's code first); the kernel settles it (`intent.restart` in `settle_kernel_act`); the door `POST /intentions/restart` answers `{held, level, needs_code}` like the stop's; the Analyzer row shows "restart" where "stop" was; "restart my resiliency intention" / "restart the kernel's resiliency intention" route to it; the sysline says "intention standing again · proof …"; the cadence counts from the restart and the loop wakes on the NEXT red transition, never a standing red. Laws: `test_cure_walk8` W20 ×2; fixture `intent-v0` (`restart_demand` ×3, the wire ×2).
- **W21** — a duty is framed as a duty: the scheduler files `“<words>” — your hourly duty (every 3600 s) · since <last run> · your earlier notes today: …` (`scheduler.duty_text` · `cadence_words` · `notes_for`); the pack labels earlier runs of the same duty `YOUR OWN NOTES from earlier runs of this duty` and a declined run "an earlier run you declined; do not decline again"; every body's seat carries `DUTY_LAW` ("a duty is served, never refused … one line: nothing new since <time>"); the glass folds a duty's reply to one line (body · the note's first line · the stamp; click to open); the schedule row reads "hourly · N runs · last HH:MM". Laws: W21 ×2; fixture `duty_text` ×5, `refused_words` ×9. The old `test_scheduler` line that encoded the bare text was replaced by name.
- **W22** — an offer is a proposal: the monitor's binding says PROPOSE it (call add-watch with name · metric · op · threshold; never "would you like me to"; cancel is the default); `offer_in` reads the condition with or without backticks, and an offer that names no condition still draws "propose it" (the ask tells the monitor to propose through add-watch). Law: W22; fixture `watch-v0` `offer` +2, one case replaced by name ("no condition, no button" → W22); the `test_cure_walk7_glass` line likewise.
- **W23** — `resident.interlock_words`: "Are you sure? The <act> act is consequential — it is recorded, and you can rest it later. Cancel is the default; a deliberate click confirms." — and `proof.question_for` at L3 likewise; "cannot be undone" is gone from the questions and the page (the purge-memory TOOL's own description keeps the phrase — a purge is the one act that truly cannot be undone). Law: W23.
- **W24** — echo's reply is the echoed words alone (`resident.echo_reply`; "hello" → "hello"); a question it cannot answer by nature earns one plain line ("echo repeats; ask the librarian for the date"); the assertion (a plain-spoken echo · none summarized away) lives in the journey — the record — never the bubble; a firmware body without a gateway keeps its plain name (P6 sp4's cure stands); on the glass "today's date" and an ask for the date/time itself name NO window, so the journey line draws none. Law: W24; fixture `echo_reply` ×6.
- **The hold's words for the kernel's stop** — after the right code the sysline and the step line say "your code is right — the intention STANDS until a declared master confirms with a click · cancel is the default" (a restart: "stays AT REST until …"); the wire's `{step: "code", next: "master"}` is unchanged.
- **The two harness checks** — `harness.checks`: "a duty answered, not refused" (the latest duty reply per runner does not open as a refusal — `refused_words`) and "the monitor's offers arrive as holds" (the latest 5 monitor replies that speak of proposing a watch each have an add-watch hold behind them); listed on the new door `GET /harness` with the last golden run. Laws: W21 harness · W22 harness. Relit on the dev ground 2026-09-21: `POST /intentions/restart` on JB's rested Resiliency intention → `{held, level: "L3-code", needs_code: true}` (the hold stands on the ground for JB's code or cancel); `/harness` → both checks ok (1 runner answered, none refused · 4 offers, every offer held).

**The close:** suite **254** green (220 → 254). The four P6 rows move to PASS in `experience-specs.md`; Phase 6 CLOSED WHOLE in 0005 (VERSION bump in the closing commit).

## Walk #9 — 2026-09-22, JB walks the shelf (P6.5 sp1, SPEC-SERVICES-01)

| Bar | What JB saw | Verdict |
|---|---|---|
| The shelf · retire · cancel · yes · restore · check (1–5) | "what services are here?" opened the shelf; "retire the weather tool" held at the interlock with "expected impact?"; Cancel did nothing; Yes greyed the card; "restore the weather tool" brought it back; "check the services" gave the health lines. JB: "1, 2, 3, 4, 5 all worked well." | **PASS** — no friction filed |
| The chat on a smaller screen (JB, after sp3's review) | Moving from the big monitor to the laptop: the browser restored the chat's remembered size, and the composer and the resize grip stood beyond the laptop's edge; Esc closed it, reopening restored the same. "If human goes to smaller screen, chat interface should adjust." | **W25 — cured the same hour** |

- **W25 — the remembered size is the wish, the screen is the law.** The chat is fitted to the viewport it wakes on and on every resize (`fitChat`): width and height clamped to the screen less a margin, the composer and the grip always on screen; the stored wish is kept untouched for the big screen's return.

- **W26 — an empty reply must never land as "replied" (seen 2026-09-23 in the suite's live-mind law, once in three runs).** The librarian, thinking for real, landed status `replied` with an EMPTY reply; the same ask answered whole on two reruns. Cure (owed to P7 sp4 / the serve path): when the mind returns no words, the serve retries ONCE, then lands the reply in words — "the mind returned nothing; asked again, nothing" — with status `replied` and a journey step naming it, never an empty bubble. **CURED 2026-09-23 (P7 sp4, the serve path):** a silence is asked again ONCE — words on the second try land with a journey step naming the retry; a second silence lands as “the mind returned nothing; asked again, nothing” with status `replied`, every thought metered (`resident.py` W26_WORDS · W26_STEP; a scripted silent mind proves both branches; the words are in `loops-v0.json`).

## Walk #10 — 2026-09-23, JB walks the Rust bridge, the toolkeeper and the laptop screen (sp3 · P6.5 sp2 · W25)

| Bar | What JB saw | Verdict |
|---|---|---|
| The Rust bridge (1) | "hello from the Rust bridge" on :4601: the ground shows it served by the librarian in 4 s (asked 15:56:48, replied 15:56:52) — but NOTHING showed on :4600's chat. Cause: the page keeps its session in browser storage, which is per ORIGIN, and a port is an origin — two pages, two sessions; the doors agreed, the chats did not. | road **PASS** · **W27** |
| The toolkeeper (2) | "toolkeeper, add the MCP server at <command>" → the keeper asked for a NAME; "clock" alone and "toolkeeper" alone went to the librarian ("that's a name, not a question"); with `named "clock"` in a fresh session: the interlock ("The services act is consequential…"), Yes, "registered the clock MCP server (orreth-clock 0.1.0) … 2 tools on the shelf under it: now, echo"; THE SHELF card: clock (mcp · stdio · healthy · initialize answered · 2 tools listed) with now and echo nested; "show the tools please" went to the LIBRARIAN, who answered from recalled notes and listed `now` twice; the time through the clock works. JB: "mixed behavior … otherwise it did add and I can use the tool." | **PASS** w/ friction — W28 · W29 · W30 · W31 |
| The laptop screen (3) | The chat fitted the smaller screen. | **PASS** — W25 CLOSED |

- **W27 — a session belongs to the person, not the browser's origin.** The page restores the person's latest session from the ground (`/sessions?person=` newest) and writes browser storage only as a hint; two bridges, two browsers, one chat.
- **W28 — a server names itself.** `initialize` returns the server's name ("orreth-clock"); the keeper derives the shelf name from it (the last word, lowercased) when the human gives none; a name is optional.
- **W29 — a follow-up stays with the body that asked.** When the keeper asks for something (a name), the next bare words in that session are the ANSWER to it, routed to the keeper, never to the lit crew; a bare "toolkeeper" opens the keeper ("toolkeeper here — say what to add, check or retire"), never a librarian's aside.
- **W30 — the interlock names the act in words.** "Are you sure? Registering the clock MCP server is consequential — recorded, you can rest it later" — never "The services act".
- **W31 — shelf questions are the keeper's, answered from the registry.** "show the tools" · "what tools are here?" route to the toolkeeper (or the registry door) — the source of truth — and every tool appears ONCE with its home ("now — through the clock MCP server"); a body's recalled notes never stand in for the shelf.

## Walk #11 — 2026-09-23, JB walks the loops in SHADOW (P7 sp4 · SPEC-LOOPS-01) — both bridges lit, :4600 and :4601 side by side

| Bar | What JB saw | Verdict |
|---|---|---|
| The beat shared (W.1) | "echo, every 5 seconds, say the time, please." on :4601 was first an OBJECTIVE echo repeated (the cadence grammar knew minutes · hours · days · weeks, never seconds); flipped to intention by hand, the door said "an intention needs something to wake it". CURED IN THE WALK: both spines read seconds (`askroad-v0` grew one case with JB's sentence); relit. Then: the same objective to echo every 5 s, ONCE per beat, the same rows on :4600 and :4601 though both kernels turned. "echo, stop" only made echo repeat "stop" (W34); the Analyzer's `stop` worked but the loop kept filing while the hold waited for the code, the code row scrolled away (W35); "stop my say the time intention" needed the exact words (W39). | **PASS** — the beat lock held; frictions W34 · W35 · W39 |
| A red turns once (W.2) | "monitor, propose a watch that bodies_alive >= 0" → the monitor argued the SENSE backwards (red = falls below zero, "useless"), offered twice, held nothing; the harness door on :4601 read "the monitor's offers arrive as holds: not ok — 2 without a hold" (the world check caught it from the Rust door). Told plainly it is a test and a watch is red while its condition holds, it held `add-watch`; Yes; "watch always red turned red · value 9". The ground: ONE turned fact; TWO watch-red markers — one under the kernel's Resiliency and one under JB's human copy of the same words (restarted since walk #8), each planned once and filed one objective (W37, a duplicate purpose let in without a word). The librarian answered the planner's impossible objective "I cannot query … I don't have a tool" — honest, but not in the taught opening, so not heard (W38). | **PASS** — one red, one turn per intention, equal on both doors; frictions W36 · W37 · W38 |
| The stop through the Rust door (W.3) | "stop my say the time intention" on :4601 → the code row; the right code → "Done, on your code: … is at rest"; :4600 read at rest; restart the same way. | **PASS** |
| The human's stop, cancelled (W.4) | The Analyzer's `stop` on the HUMAN Resiliency row (JB meant the kernel's): held L3-code with "expected impact?" · Cancel default · Yes greyed; Cancel → "Cancelled — nothing was done". Then the kernel's row was GONE from the Analyzer on both ports while both `/intentions` doors listed it standing with all its counts: the Analyzer draws intentions from the newest-60 ROOTS, and the walk's own asks pushed the 19th's root out of the window (W40). | **PASS** on the ladder; W40 |
| The harness door (W.5) | The Monitoring pull on :4601: the librarian's last run (the Python kernel's scheduled duty at 11:46, 2 passed · 0 failed) and the five world checks off the ground. Typed "run the harness against the librarian now" → the MONITOR answered in the taught shape: "I lack the tool to run the harness. CANNOT ACT: the kernel's harness runner would be needed" and named the last real run — the honest word, live, from a firmware body; the card's own link hits the door, which refuses by name on :4601. | **PASS** |

**JB's law (walk #11): every word aimed at a human is plain.** "You're using 'port to purpose', interlock, feed … cryptic to a human of lower intelligence." My walk script named the machinery. Proposed as covenant rule 13 (JB's lock owed): every word aimed at a human — in the glass, in a walk script, in a register row — is plain enough for a newcomer; a machinery name appears only beside its plain words.

- **W32 — the Crew pull has no close of its own, and Esc closes the Crew and the chat together.** One Esc, one thing.
- **W33 — a pull does not retract when focus moves.** The Crew stayed open when the Analyzer took focus; what focus leaves, retracts.
- **W34 — a bare stop addressed to the body that runs an intention stops it.** "echo, stop" made echo repeat "stop". It should rest the standing intention echo runs, or ask which when there are several.
- **W35 — a stop asked is a stop held.** While an intention's stop waits at the interlock the loop must file nothing new for it (cancel resumes; the code rests it), and the code row stays pinned above the composer until it settles — the objectives scrolled the row off the screen.
- **W36 — the monitor argued a watch's sense backwards and offered instead of proposing.** Its binding says RED while the condition holds; its mind read the opposite, called the watch useless and asked twice. The harness's world check caught the two unheld offers.
- **W37 — a duplicate purpose is named at the door.** A human intention with the kernel's own words and interests was declared without a word; every red then reacted twice, once per copy, and the Analyzer showed two rows with the same words and different counts. Declaring words the kernel already keeps should say so.
- **W38 — the runner's honest word is heard in more than one shape.** "I cannot query … I don't have a tool" is `cannot act` in other words; the reader hears only the exact opening, so no improvement was marked and the loop plans the same again.
- **W39 — a stop never needs the exact words.** `stop` alone or "echo, stop" lists the standing intentions to click; "stop my time intention" matches loosely (a word in common, the runner, what it serves) — one match acts, several offer the choice, none says what stands.
- **W40 — a standing intention is never off the board.** The Analyzer's intentions band reads the newest-60 roots; the kernel's Resiliency (declared 09-19) fell out of the window under the walk's own asks while both `/intentions` doors listed it standing. Read the intentions door, or pin every standing intention above the window.
- Noted, not a wound yet: "please" contains "lease", so the serves guess read resiliency for "say the time, please".

### Walk #11's cures — 2026-09-23 (the same day; JB: "let's start applying cures so we can continue build on next session")

- **W27 CURED (glass):** on load the page asks the ground for the person's newest session (`/sessions?person=`) and continues it; the browser's memory is only a hint when the ground lists none. Two bridges, two browsers, one chat.
- **W32 CURED (glass):** the Crew and the Monitoring pulls wear their own `▾ close`; Esc is ONE keystroke, ONE thing — the pull on top closes first (Analyzer, then Monitoring, then Crew), and only with no pull open does Esc return the bridge (the chat closed, the focus popped). SPEC-ESC-01 now reads "one Esc, one layer".
- **W33 CURED (glass):** one pull at a time — opening the Analyzer, the Crew or the Monitoring retracts the other two.
- **W34 · W39 CURED (glass):** a stop never needs the exact words. `stop` alone lists the standing intentions to click; `echo, stop` lists what runs on echo (one → straight to the code row); `stop my time intention` matches loosely — the words contain it, a word in common (noise words dropped), the runner, or what it serves; one match acts, several offer the choice as rows, none says what stands and offers those. `restart` / `resume` the same over the rested ones.
- **W35 CURED (kernel, both spines + glass):** a stop asked is a stop held — while an intention's `intent.stop` waits at the interlock the loop files nothing new for it (its cadence sleeps, its red is not observed, its answered plan is not filed: `intent.held_stops` in Python, `intent_live::held_stops` in Rust); a cancel resumes it, the code rests it. On the glass the hold's bubble (the code row) is PINNED above the composer until it settles, then rejoins the log in order — the crew's bubbles can no longer scroll it away.
- **W36 CURED (the monitor's words):** its binding now says the sense of a watch is the kernel's — RED while the condition holds — never to read it the other way, never to call a watch useless or argue its purpose, and to propose EXACTLY the condition the human names; a question back is not a proposal.
- **W37 CURED (kernel, both spines):** a human intention whose words already stand in the world is refused at the door in words — "an intention with these words already stands — the kernel's “…” is at work; stop it first, or say what is different" (`duplicate_words`, conformance `duplicate_words`); the kernel's own idempotent declaration is untouched.
- **W38 CURED (kernel, both spines):** the honest word is heard in more shapes — a reply that OPENS with "cannot act", "I cannot …", "I can't …", "I lack the tool …", "I don't have a tool …", after at most one short preface ending in a colon ("I need to be plain with you: I cannot …"); only the opening counts (four `cannot_act` cases more in `loops-v0`).
- **W40 CURED (kernel, both spines):** the Analyzer's origins are the newest N roots AND every standing intention's root, whatever its age — a standing purpose is never off the board; a rested one may fall off with time.
- Re-walk OWED: JB in the glass, both bridges lit.
- **Re-walk (JB, the same afternoon, both bridges lit):** "echo, restart intention 'every 5 seconds'" first went to echo — the stop/restart grammar knew no name at the head with words after the verb; WIDENED (a name at the head, "intention" anywhere, quotes stripped). The restart then held for the code and stood the intention again — but no new occurrences came: **W35's boundary found** — three stale stop holds nobody had answered (two on the kernel's Resiliency from 09-22, one on the echo intention from the walk) were pausing their intentions for good, though the interlock's words had always said "doing nothing cancels". CURED in both spines: a kernel-held act with no word for 15 minutes is cancelled by the default on the next beat (`proof.expire_holds` · `proof_live::expire_holds`, riding the intent beat under the beat lock; conformance `hold_expiry`) — the first beat after the relight cancelled all four stale holds and the echo intention turned again. Then "echo, stop": the hold, the code row pinned above the composer, the objectives halted while it waited — JB: "The stop worked nicely!" The restart's closing line read "at rest" — the verb was not carried into the hold's line; fixed ("standing again").
- **JB verified (evening):** the pulls' own close and that pulls no longer collide (W32 · W33 PASS). **Rule 13 LOCKED by JB** — written into the covenant card.

## Walk #12 — the Stable (P6.5 sp3, built 2026-09-24; JB's walk OWED)

**What was built (plain words):** Orreth now runs its own gateway for every mind — a LiteLLM box in the rig on port 4604 that Orreth manages. Every mind the bodies think with, wherever it lives (Anthropic, OpenRouter, a local Ollama, any OpenAI-compatible server), is a stall in the Stable and an entry in that gateway. Every body has its own key at the gateway with a daily allowance (the fuel clause); when the allowance is spent the body says so in words and the stablekeeper proposes a refill. Every thought lands on the meter with its cost in dollars. The stablekeeper pings every mind, watches for a price that moved under its pin or a mind the market says is expiring, and proposes; it never retires, assigns, refills or re-pins alone.

**Walk #10's frictions, cured in this spoonful:**
- **W28 CURED:** a server names itself — "toolkeeper, add the MCP server at <command>" with no name takes the last word of the server's own name (the clock server → "clock"); a name is optional.
- **W29 CURED:** a keeper's question keeps the next bare words — when the toolkeeper or the stablekeeper ends a reply with a question, the next words in that session go to that keeper, never to the whole crew; a bare "toolkeeper" or "stablekeeper" opens that keeper.
- **W30 CURED:** the interlock names the act — "Are you sure? Registering the clock MCP server at … is consequential — it is recorded, and you can rest it later" · "Adding the llama mind (ollama llama3.2) is consequential — it is written into the gateway and recorded; you can retire it later" — never "The services act".
- **W31 CURED:** "show the tools" · "what tools do we have?" · "show the minds" · "what is in the Stable?" answer from the registry, every tool once with its home; every mind with its deal.

**The script (JB in the glass, `scripts/dev.sh up` then `scripts/dev.sh bridge` from a login shell so the keys ride in):**
1. Say "what minds are here?" — expect one mind, haiku, with where it lives, its class, $1 in / $5 out per million, its health, and "the gateway answers".
2. Say "librarian's fuel" — expect the allowance ($1 a day by default), the spend so far, when it renews.
3. Ask the librarian anything ("what is the temperature outside?") — then say "librarian's fuel" again: the spend grew by a fraction of a cent. Open the Crew: the haiku card reads what it has cost.
4. Add a mind. With Ollama running on the laptop: "stablekeeper, add the mind ollama llama3.2 as llama". Without: "stablekeeper, add the mind openrouter meta-llama/llama-3.3-70b-instruct as llama". Expect the interlock to NAME the act (W30), Cancel focused. Click Yes. Expect "the llama mind stands in the Stable — …".
5. Say "check the minds" — expect both minds healthy (the new one answered its canary through the gateway). If the new mind cannot answer (no Ollama, no OpenRouter key in the box), expect the honest word, never a stack.
6. Say "assign librarian to llama for fast work" — expect the interlock in words; Yes. Ask the librarian anything — open the Monitoring: THE STABLE view shows "librarian thinks with llama (fast)" and spent today moved; the Crew's llama card reads its cost.
7. Say "refill librarian by $2" — expect the interlock ("real spending, recorded"); Cancel — nothing changes; say it again, Yes — "librarian's fuel" reads the larger allowance.
8. Open the harness (the Monitoring's world checks) — expect nine checks, the last four: every mind answers · the gateway answers and holds every mind · the meter and the gateway agree · a model change is announced.
**Walk #12, JB, 2026-09-24 (steps 1–3 PASS):** "what minds are here?" · "librarian's fuel" · the Crew opened and the librarian's cost moved between asks — incremental tracking seen. **Step 4 FRICTION → W41:** "stablekeeper, add the mind ollama gemma3:270m as gemma" — the keeper DESCRIBED the act ("Let me show you what I would add … give me the ollama base URL") and asked for a base URL instead of calling its tool; no interlock arrived. Cause: the tool's words read "base: a URL for ollama or compatible" as a requirement. **W41 CURED the same hour:** the tool's words say every field but name · provider · model has a default and must never be asked for; the keeper's charge says CALL the tool at once and let the interlock ask; and the exact words "[stablekeeper,] add the mind <provider> <model> as <name> [for fast|standard|deep work] [at <base>]" go straight to the Stable's door — held at the interlock, no mind in the loop.

**Steps 4–6 PASS (JB, after W41's cure):** the interlock arrived, gemma stood in the Stable, "check the minds" read both healthy through the gateway (ollama/gemma3:270m · anthropic/claude-haiku-4-5-20251001), the assignment held and landed ("librarian now thinks with the gemma mind for fast work — recorded"). **Frictions:** **W42 — the interlock's words doubled** ("Are you sure? Are you sure? Adding the gemma mind … you can retire it later is consequential — it is recorded, and you can restore it later") — the kernel frames a held act's words itself and the Stable handed it a sentence already framed. **CURED:** the Stable's act words are the bare phrase ("Adding the gemma mind (ollama gemma3:270m) to the Stable and the gateway"); the kernel or the door frames it once. **W43 — JB's callout: a body's card does not say which mind it thinks with.** **CURED:** every Crew card with a mind reads "thinks with **gemma** · ollama gemma3:270m · standard — assigned to gemma for librarian (fast) · last thought rode gemma ($0.0000)" — the Stable's decision for that body, its why, and the last thought's cost.

**Step 7 PASS** (refill held, Cancel did nothing, Yes grew the allowance). **Step 9 skipped by JB** (no CPU for local inference; Ollama stays available). **Three more frictions from JB's reading:**
- **W44 — an assignment per class made the card lie.** "assign librarian to gemma for fast work" then "assign librarian to haiku for standard work" left BOTH rows standing (one per class); the librarian's template names no class, so the picker took the first row alphabetically — gemma — while JB had just said haiku. JB: "this shouldn't be possible if rails/loops/inventories have continuity". It was one ledger with two rows; the law was wrong, not the continuity. **CURED:** an assignment without a class is for ALL the body's work and replaces the body's all-work assignment; the class asked wins, then the all-work one, then the newest — never the alphabet. "assign librarian to haiku" now means haiku, full stop; "unassign librarian" lifts it (fixture minds-v0 +3 cases).
- **W45 — "world checks" was machinery, and the Monitoring never showed them.** JB: "I don't see world checks; only the word 'world' … not even sure what a world check is". **CURED:** the Monitoring gains **HEALTH CHECKS · what must be true of this world, read from the ground now** — nine rows, each "holds" or "BROKEN" with its words.
- **W46 — say LLM.** JB: "If it's an LLM say LLM vs mind." **CURED:** every word a human reads says LLM (the Crew card: "LLM: gemma · ollama gemma3:270m — assigned: …"; THE STABLE · LLMs; the interlock: "Adding the gemma LLM …"; the kernel's replies); `mind` stays only as the service kind's machinery name beside its plain word.
- **SEED (JB's question): a LangGraph body with SEVERAL distinct LLMs in one flow.** Today a template names ONE model and every LLM call carries the body's DID and the stall — so a graph that called two LLMs would already show two stalls on its meter lines, but a template cannot yet declare LLMs by ROLE (a planner node deep, a writer node fast) and an assignment cannot name a role. The seed: `mind` becomes roles → {class | model}; the gateway's `think` takes the role; assignments are per (body, role); the card lists one LLM line per role. It lands with the versioned LangGraph templates (the workshop), not before — JB has no workspace to see a graph yet.

**Step 8 (JB): the HEALTH CHECKS read, two BROKEN.** "every service healthy or retired — unhealthy: minds" and "the keeper proposes after strikes — unproposed: minds": the built-in `minds` TOOL's words changed during the day, its schema no longer matched the pin from an earlier boot, and the kernel refused to re-register a changed built-in instead of versioning it (the toolkeeper then counted strikes). **W47 CURED:** a built-in whose declaration changed is re-pinned at boot — a version fact, said in the boot line ("re-pinned (their words changed): minds"); all nine checks hold again. **W48 — the Monitoring flashed and reloaded every five seconds** (JB: "looks and feels a bit broken/fragile"): the whole pull was repainted on every beat, with the nine health checks fetched each time. **CURED:** the pull is painted off-screen and swapped in only when something changed; the health checks are read every 30 s and say "as of HH:MM".

**After the walk (JB): a stale proposal waited in the chat** — "The toolkeeper proposes retiring the minds tool — unhealthy across 3 checks in a row" — the beat had counted its strikes before W47's re-pin, and the tool had been healthy since. JB asked whether to action it; the answer was Cancel (Yes would have retired the stablekeeper's own tool). **W49 CURED:** a keeper's proposal whose reason has passed withdraws itself — when the service answers its next check, the kernel cancels the waiting hold in words ("Withdrawn — the minds service answered its check and is healthy again; nothing to retire. Nothing was done; the proposal is at rest, recorded."); a human's own retire hold is never touched.

9. (Optional) Stop Ollama, wait a beat of the stablekeeper (ten minutes, or set SPINE_MIND_CHECK_S=30 before the bridge) — expect llama to turn UNHEALTHY with the reason; after three beats, a proposal to retire it arrives in the chat as a hold; Cancel it.

## Walk #13 — memory and the export (P7 sp5, built 2026-09-24; JB's walk OWED)

**What was built (plain words):** the Rust kernel now keeps the same memory the Python kernel keeps — one Record on one ground — writes the same session summaries (the digests) byte for byte, answers recall, and signs the compliance export as the kernel's own self: one keypair per rig, the same on both bridges, its seed kept beside the bodies' seeds. The Python bridge signs its export with the same self.

**The script (JB in the glass; `scripts/dev.sh bridge` and `scripts/dev.sh shadow` both lit):**
1. On :4600 tell the librarian something to keep: "remember that the walk's word is HERON". Expect it to say it kept it.
2. On :4601 (the Rust door) ask "what do you remember about the walk's word?" — expect HERON, word for word.
3. On :4601 open a fresh session (the roll). Expect the old session's short version to appear in the sessions list on BOTH doors, reading the same.
4. On :4600 say "export compliance for this session" and take the download; do the same on :4601. Expect both files to carry the same root hash and the same signer, `did:orreth:kernel:…`, and "verify" to hold. Open the CSV: the same lines.
**Found by sp5's shadow proof — W50 (kernel, Rust): the Rust intent loop's turn had stumbled on EVERY beat since walk #11's hold-expiry cure** — `make_interval(mins => $3::float8)` (Postgres takes whole minutes there); the words "the ground refused: db error" hid it. **CURED:** seconds × 60; and a ground's refusal is now said in the ground's own words with its code (rule 13), never a bare "db error".

5. (Optional) Ask the librarian to forget the walk's word — expect the recall to come back empty on both doors and the session's short version to lose the line.

**Walk #13, JB, 2026-09-24 (steps 1–3 PASS; step 4 compared by Fable from both doors):** the librarian kept "I went to the trailer today for about 3 hours" on :4600 and the Rust door recalled it; a roll on :4600 archived that session and its short version listed on BOTH doors, reading the same; the export of the trailer session (`ses_f7d2a9ca43e0`) taken from :4600 and :4601: 11 rows each, the same signer `did:orreth:kernel:fa789bd1…`, the same root hash, both verify, the CSV 12 lines on both. **Frictions:**
- **W51 — the other door's sessions list did not refresh.** JB: "nothing happened on shadow until I started a new session on it". The sessions list is painted when the chat opens and on a roll; a roll on ONE door is not seen on the OTHER until that page acts. Cure owed: the sessions list refreshes when the feed announces a session (the roll's fact), on both doors.
- **W52 — the digest's clock is UTC while the session list's is the human's.** "19:25 asked" sits beside "04:56:38 PM" — two clocks on one screen. Cure owed: the digest's text formats in the human's zone (`SPINE_HUMAN_ZONE`) on BOTH spines — a fixture change (`digest_text` gains the zone) and a port of the zone shift in `memory.rs`.
- **My words (rule 13):** JB "totally lost" the rest of the script — the export step said "take the download" without naming the words to say ("export compliance for this session") or where the download appears (two links under the table in the chat).

**Walk #13's cures (the same evening):**
- **W51 CURED (both spines):** a roll is a FACT — `orreth.session.opened.v1` through the outbox in the roll's transaction (payload: the session, its person, its title, the session it archived, its state; fixture `session_fact`, memory-v0 +3); the feed carries it and every door that showed its sessions list re-reads the list. Found on the way: the roll built the archived session's digest BEFORE the new row stood, so its span ended at "now" and a memory landing in the gap changed the rebuild (test_digest caught it once the digest moved) — the digest is built AFTER the new row on both spines.
- **W52 CURED (both spines):** the digest's clock is the human's — `SPINE_HUMAN_ZONE` (America/Denver by default): the Python spine shifts with ZoneInfo, the Rust spine lets the ground shift (`to_char(… AT TIME ZONE $zone)`) — the same tzdata, the same words; the fixture's `digest_text` stays zone-free (its parts arrive already shifted).
- **THE GUIDE (JB's seed, built):** say "guide", "help" or "?" in the chat and a sheet opens over everything, kept by the kernel (`spine/guide/guide.v0.json`, served by `/guide` on BOTH doors) — what you can say and what happens, section by section: the chat · the kind of an ask · when the kernel asks "Are you sure?" · the Crew and the shelf · the Monitoring · the Analyzer · memory, sessions and the export; the section for where you are comes first and reads "you are here"; a click on any words puts them in the composer, never sends them; Esc closes it. Fable keeps the guide current with each spoonful.
- **Found by the memory proof while curing W51/W52:** a kernel booting beside another's inserts DEADLOCKED on the Rust store DDL (an `ALTER TABLE … ADD COLUMN IF NOT EXISTS` takes an exclusive lock even with nothing to add) — cured: the column is added only when missing. And an OPEN session's summary moves as memories land in its span (MITL's 166 passages at boot land in every open session's span) — the proof now rolls the session before it reads, as the reference's own episode boundary does. **SEED:** a session's "acquired" lines are every body's memories in the world during the span, not the human's session's — the digest should cite only what the session's asks acquired; a later spoonful.

## Walk #14 — the bodies' seam (P7 sp6, built 2026-09-24; JB's walk OWED)

**What was built (plain words):** until now the Rust kernel on :4601 had no bodies of its own — every body (librarian, echo, the keepers, the workspace agents) lived as a thread inside the Python Bridge's one process. Now the Rust kernel starts each body as its own process, watches it, restarts it if it dies (the same self, the same keys), parks it if it keeps dying (three times in five minutes) and says so, and brings every body down when it goes dark. The harness runs from the Rust kernel too: it asks the body to run its golden cases and reads the result off the ground. The Stable's doors, the shelf's doors, both keepers' beats and all nine health checks are the Rust kernel's now. The one crew list both kernels read is `spine/crew.v0.json`.

**The script (JB in the glass; the Python Bridge DARK — `scripts/dev.sh bridge stop` if it is lit; then `scripts/dev.sh shadow` from a login shell so the keys ride in):**
1. Light the Rust kernel alone: `scripts/dev.sh shadow`. Expect the line "the Rust bridge is lit … bodies: crew" and, in `~/.orreth/tmp/shadow.log`, ten lines "<name> is alive: did:orreth:agent:… · life N" within about a minute (the boot rite's shelf line comes first).
2. Open http://127.0.0.1:4601/ and open the Crew. Expect every card to read "process: alive · life N · pid …" under its self line, and the librarian's card to say which LLM it thinks with.
3. Say "echo, say HERON". Expect HERON back. Ask the librarian anything ("what is the temperature outside?") — expect the words to form live in the chat, then the whole reply.
4. Kill the echo by hand: read its pid from its card and run `kill -9 <pid>` in a terminal. Wait a few seconds and reopen the Crew (or say "show the crew"). Expect the echo's card to read life 2, the same self line as before, and "echo, say GULL" to be answered.
5. Kill the echo twice more within five minutes (its new pid each time). Expect its card to read PARKED with the plain words ("echo is PARKED — it died 3 times in 5 minutes, so the kernel stopped restarting it … Say “restart the echo body” to try again") and the Monitoring's BODIES to show the echo dormant after fifteen seconds.
6. Say "restart the echo body". Expect "echo is being restarted on your word — its deaths are forgotten …" and, a few seconds later, its card alive at life 4 with the same self line.
7. Open the Monitoring. Expect HEALTH CHECKS to read nine rows (the Stable's four included) and the HARNESS to show the librarian's last run. Click "run the harness against the librarian now" — expect the run to land within a minute (the Rust kernel asks the librarian over the rail).
8. Say "what minds are here?" and "librarian's fuel" — expect the Stable's answer from the Rust door, the gateway's word included.
9. Stop the kernel: `scripts/dev.sh shadow stop`. Expect "the Rust bridge is dark" and `pgrep -f orreth_spine.body` to print nothing — no body outlived the kernel.
