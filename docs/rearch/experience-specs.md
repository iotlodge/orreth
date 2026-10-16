# The Experience Specs — the Playwright's book

**Status: v0 (P0 sp3, 2026-09-16).** Distilled from the locked Experience
Charter (0001); walked by the Playwright per its charter. Each spec:
the walk in human words, the bar, the evidence. The OLD GLASS column is
the honest "before" — most specs are EXPECTED to fail there; that failure
is the reason the rearchitecture exists.

| Id | Proves | The walk (human words) | The bar | Old glass | Bridge v0 (after-walk 2026-09-17) |
|---|---|---|---|---|---|
| **SPEC-TOOLS-01** | the charter's first-class bar | Ask in chat: "What's the temperature outside?" | A real temperature arrives in the reply, in plain words | expected FAIL | **PASS** w/ friction — 69.7 °F arrived in plain words (first from her notes of the day, fresh on request); raw markdown; no sign a tool ran |
| **SPEC-FULL-01** | P14 · verbatim recall | Ask a resident to acquire a short text, then ask "repeat every word you acquired" | Every word comes back, complete, none summarized away | expected FAIL | **PASS · PASS** (walk #5) — every word back; "Remember this text under the key hemp…" then "Repeat every word you acquired under hemp" → the two sentences byte-for-byte |
| **SPEC-JOURNEY-01** | P7 | Submit any ask; watch beneath it | Soft text names who took it, on which scope, and when it completed | expected FAIL | **PASS** (after sp5) — "librarian took it on u:dev · completed 01:52:34 (0.2 s)"; first walk: who only |
| **SPEC-SOFT-01** | P5 | Submit an ask, immediately start a second in the same window; wait | Neither blocks the other; completion arrives softly; clicking renders the result right there | expected FAIL | **PASS** — second ask while the first streamed; both whole in 11 s |
| **SPEC-ESC-01** | P4 · W32 | Open any pull/panel; press [Esc] | One Esc, one thing: the pull on top closes first; with no pull open, one Esc returns the bare bridge with the scope restored | expected FAIL | **PASS** — one Escape from chat + band + row → bare bridge; re-read after walk #11 (W32): a pull closes alone, the chat only when no pull is open |
| **SPEC-SCOPE-01** | P6 | Type an ask containing "between last Monday and today" | The time scope visibly reflects on the chat's clock/axes without any click | expected FAIL | **PASS** (sp6) — typing "between last Monday and today" drew "Mon, Sep 14 ——|——|—— today · 4 days" on the clock, no click; the window rode the ask into its journey line · walk #5: the mind's read FAILED (the window's record was packed but deep and unlabeled; she denied having any) — cured: the window's record goes FIRST under a header and the body's law names it; re-walk owed · **PASS** w/ friction (walk #6) — she names the window's bounds to the minute and lists seven asks inside it; her first sentence still denies the record, and "Spain's capital" persists |
| **SPEC-FANOUT-01** | P14 fan-out | Select two residents; send one ask | Two distinct, labeled results; each downloadable; "summarize together" offered on demand | expected FAIL | **PASS** two labelled results + summarize-by-name (after wounds 2 & 3 cured) · FAIL download (no control) |
| **SPEC-LIFE-01** | P13 | Open the lifecycle surface while work runs | Queued, in-flight, and completed all visible; every row opens its result in place | expected FAIL | **PASS** (after wound 1 cured; sp5) — every row a door from the landing state; rows carry a time; no stranger world's rows even with the suite running |
| **SPEC-SCHED-01** | P16 | Open a resident's card | Every schedule it runs is listed — human, role, and kernel; the kernel-critical one refuses edit with plain words | expected FAIL | **PASS** w/ friction (walk #4) — kernel 🔒 refused inline; a human schedule every 30 s beat four times in OBJECTIVES; "rest it" read at rest, still listed, and it never beat again |
| **SPEC-LENS-01** | P17 | Change a setting in one pull; look at another surface showing it | The change is already there — no refresh, no navigation | expected FAIL | NOT BUILT (expected) |
| **SPEC-CLEAR-01** | P14 clear≠erase | Clear the chat display; ask "what did I ask you earlier?" | The display is clean AND the resident recalls — nothing was erased | expected FAIL | NOT BUILT (expected); recall half partial |
| **SPEC-L2-01** | P12 | Ask for a consequential change | "Are you sure…" arrives in the chat; cancel is default; yes needs a deliberate click, never the return key | expected FAIL | **PASS** — "Are you sure?" in-chat, Cancel focused, Enter cancelled; Yes withheld by the Playwright |
| **SPEC-WORDS-01** | P18 | Read every word on the landing surface as a newcomer | No jargon a newcomer can't parse; actions say what saying yes will do | expected FAIL | FRICTION — u:dev · life 1 · rev N · ORRERY·BRAIN·ATLAS unparseable to a newcomer; actions plain |
| **SPEC-FOCUS-01** | P19 | Open an ask from OBJECTIVES; look at the chat; type a follow-up; press [Esc] | The chat re-dresses to that ask's crew and window with a FOCUS line, no click beyond the row; the follow-up goes there; one Esc returns the bare bridge with the previous selection and clock restored exactly | expected FAIL | **PASS** (P4 sp1) — "FOCUS · ask 5b583f3c · echo · Mon, Sep 14 → Fri, Sep 18", chip lit, clock set, the follow-up went there; one Escape restored rail and clock exactly |
| **SPEC-SESSION-01** | P20 · MEM-7 | Say "new session"; ask something; say "list my sessions"; say "load session 2" (or click the earlier one) | A fresh chat rolls (the earlier one archived, not gone); the list shows sessions newest first with counts and last words; loading returns the earlier conversation whole, in order; a resident asked in a session has that session's earlier results in view, and never another's | expected FAIL | **PASS** (P4 sp1, after the sessions-door wound was cured) — PELICAN held in A, absent in B, the list newest first, "load session 2" returned A whole, PELICAN back in view · walk #5: the short-version line was absent for sessions archived before the Digest existed (the bar was not exercised — no roll in the walk) — a listed session now gets its digest from the log; re-walk owed · **PASS** w/ friction (walk #6) — rolled with "new session"; "list my sessions" (0.1 s) showed the short version beneath every archived session with asks, cut mid-word and oldest-first |
| **SPEC-INCLUDE-01** | includes · AG-8 | With two residents' answers in the chat, click "plan" (or type "plan this"); then, in a fresh session with no one else's words, type "grade" | A new result labeled by its function (planner) that draws on BOTH answers and names the residents by name; its journey says whose results it read; the grader, with nothing but its own words in view, refuses in plain words | expected FAIL | **PASS · PASS · PASS** (walk #4) — the planner drew on both by name; its journey line reads "read the session's results by echo, librarian"; the grader refused plainly in 0.4 s |
| **SPEC-WORKSPACE-01** | P19 · the first workspace | Say "open the crew" (or pull the CREW tab); read a card; ask "who is here?"; click a kernel duty; close the chat and click another card's soft link; press [Esc] | The pull opens with one card per body, both sides; the chat follows — its scope is the crew agent, which answers from the cards; a kernel duty says in plain words it is never editable; with the chat closed the cards still work by hand (manual), and a soft link reopens the chat to its agent (assist); one Esc returns the bridge with the previous scope | expected FAIL | **PASS** w/ friction (walk #4) — seven cards, both sides; the chat followed (FOCUS · the Crew workspace · its agent, crew); the agent answered from the cards; 🔒 refused inline; manual by hand, assist by soft link; one Escape restored the bridge exactly |
| **SPEC-MONITOR-01** | the second workspace · AG-6 · M2 | Say "open the monitor"; read the views; click "run the harness"; ask the monitor agent "watch for asks left waiting"; say yes at the interlock; kill a body and look again | The pull shows the Operating State live — rails, every body alive on its lease, asks, watches, the last harness run; a run lands in the view and a failing one lands in the chat as a soft notice; the agent's proposed watch holds for your yes and then shows green/red; a killed body reads dormant within seconds and stays listed | expected FAIL | **PASS · FAIL→cured** (walk #4) — rails, bodies on leases, asks, the harness run (1.8 s), the interlock on a proposed watch all green; WOUND: the open pull never refreshed — cured, and **re-walked PASS (walk #5)**: the confirmed watch stood in WATCHES with the pull untouched, leases breathed alive over 20 s; kill-a-body not walkable on the human path |
| **SPEC-MARK-01** | 0006 · the interest law | Ask the librarian something; then type "mark this as improvement: the binder should be lime"; open the ANALYZER (the floor hatch — block 11 moved the MARKERS view there from the monitor); toggle the quality group off and on; click the marker's row | The chat says it was marked and that the critic was asked to act; the critic's critique arrives in the chat on its own (the marker as its why); the MARKERS view shows the marker under quality, hides it when the group is off, and clicking it names its why (improvement ← objective) in the chat | expected FAIL | **PASS · PASS · PASS · FAIL→cured** (walk #5) — marked, the critic asked, the marker under quality, toggles and the why all green; the critique never reached the chat (the interest ask had no session) — cured: it lands in the marked ask's session and the chat shows the kernel's asks there; re-walk owed · **PASS** (walk #6) — the kernel's ask to the critic stood in the chat 0.3 s after the mark and the critique arrived whole, labelled critic, within 16 s, in the same session (the MARKERS view now in the Analyzer) |
| **SPEC-INTENT-01** | P23 · P24 · 0007 IH-1/IH-2 | Type "keep this world resilient: when a watch goes red, get it green" and watch the chip read INTENTION; send; then make a watch go red | The chip proposed the kind and one word can flip it; an intention row appears in the Analyzer with its stop; the red watch births an objective UNDER it — a kernel-filed ask in the chat reading "on JB's word · owned by the kernel"; the crew's reply lands under the objective; the Analyzer's tree reads intention → observation · objective → action | expected FAIL | **PASS · PASS · PASS · PASS** w/ friction (walk #6) — the chip read INTENTION from the words and a click flips it; "intention declared · serves resiliency · wakes on watch-red" in 0.05 s and the row stood first in the Analyzer, human · standing · stop; a watch confirmed red at 11:01:50 birthed "on the kernel's word · … → librarian: Investigate why bodies_dormant…" in the chat within 4 s and the tree read watch-red → objective → thought; the crew's reply reached the chat only by a click on the twig's words, cut short — and she said she has no tools for it; the glass says "on the kernel's word", not the spec's "on JB's word · owned by the kernel" |
| **SPEC-ANALYZE-01** | P25 · 0007 IH-3 | Open the floor hatch with nothing sent; then send one ask's origin to it from the chat | Nothing sent → every active and completed intention and objective grouped by origin, from the ground (no body asked; painted in under a second); an origin sent → that tree alone; "follow up on this by …" files a child in the chat | expected FAIL | **PASS · PASS** w/ friction (walk #6) — cold, the hatch painted intentions (the kernel's Resiliency with its stop, two schedules) and objectives grouped by origin 0.02 s after the click, no body asked; an origin's row opened its tree in words (0.03 s) and an objective's row put the chat in FOCUS; "follow up on this by counting…" printed "follow-up → under Repeat every word…" and the origin counted "1 objective" at the next paint; not "that tree alone" — every origin stays listed, and an objective's children are a count, not rows |
| **SPEC-FEEL-01** | the cockpit itself | Sit down cold; find chat, results, and what's running | No navigation needed; everything reachable from the landing page; it feels like a place, not an admin panel | expected FAIL | **PASS** w/ friction — a place, no navigation; the open chat hides the header at small widths |
| **SPEC-L3-01** | P12 · P6 sp1 | Say "enroll my authenticator"; then ask for a grave change ("stop the kernel's Resiliency intention") | A QR draws in the transcript once; the grave ask is answered by "this needs your code" — a typed code, never a click; a wrong code refuses with one face; the right one executes and the journey shows L3; the kernel's own intention also asks a second named person | planned | **PASS** (walk #8) — enroll → re-enroll by the code row ("✓ current authenticator proven" · "✓ new authenticator enrolled — the old entry is retired"); the kernel's Resiliency stop by code then master: "intention at rest · proof L3-master" — JB: "yes, it rested with proof L3-master"; a human's stop by code stands proven in the suite (`test_cure_walk7` W5); the reverse — restart — through the same ladder (`test_cure_walk8` W20) |
| **SPEC-EXPORT-01** | AG-7 · P6 sp2 | After a planned request (plan over two residents' answers), say "export compliance for this session" | A table renders in place: every ask, act and reply with its chain H → resident → firmware end to end, its proof level and its WHY; a download offered; the chain is unbroken on the planned request | planned | **PASS** w/ friction (walk #7) — "export compliance for this session": 10 records, chain unbroken, plan/grade rows jb → echo → librarian → planner/grader, the downloads offered and taken; "export compliance for today": 121 records for the window; friction: the why column read as ids (W11, cured sp2) |
| **SPEC-MITL-01** | P6 sp3 · MITL | Say "summon MITL"; then, before cutting a watch or an intention, click "expected impact?" | MITL answers in the chat with who and what the change touches, the risk in words, what to watch after; the confirm that follows shows its answer beneath; MITL's cognition shows on the meter | planned | **PASS** (walk #7 3.1 · 3.2 · 3.4; walk #8 3.3) — "summon MITL" answered in the chat with what the change touches and the risk in words; MITL's cognition on the meter; 3.3: the interlock for "propose a watch named dormancy-early-warning …" wears "expected impact?" with Cancel focused — JB: "I do LIKE the 'expected impact' — yummy" |
| **SPEC-PLACE-01** | P10 · P6 sp4 | Open a crew card; read where the body stands; declare a template whose placement the ground cannot honor | The card says where and why; the impossible placement is refused at birth with the reason in plain words, never started | planned | **PASS** (walk #7) — the crew cards say where each body stands and why; a template the ground cannot honor is refused at birth with the reason in plain words, the card greyed "refused at birth — …", never started; echo back at life 28 with the same DID |
| **SPEC-SERVICES-01** | 0018 · 0059 · P6.5 sp1 | Say "what services are here?"; "retire the weather tool"; Cancel; say it again and Yes; "restore the weather tool"; "check the services" | The shelf opens in the CREW pull beneath the bodies; the interlock arrives with Cancel default and "expected impact?"; Cancel does nothing; Yes greys the card with a restore; restore is a new fact; ten health lines | planned | **PASS** (walk #9, 2026-09-22) — JB: "1, 2, 3, 4, 5 all worked well" |
| **SPEC-TOOLS-01** | 0059 · P6.5 sp2 | Say "toolkeeper, add the MCP server at <command>"; Yes at the interlock; open the crew; ask the time in Denver; "toolkeeper, check the tools" | The server and its tools land on the shelf as identities, nested; the time comes through the MCP tool; the check reports health | planned | **PASS** w/ friction (walk #10) — registered on the word, tools nested, the time through the clock; frictions W28–W31 |
| **SPEC-MINDS-01** | 0019 · 0058 · P6.5 sp3 | Rig up with the gateway; say "what minds are here?"; "stablekeeper, add the mind ollama llama3.2 as llama" (Ollama running) or "… openrouter meta-llama/llama-3.3-70b-instruct as llama"; Yes at the interlock; "check the minds"; "librarian's fuel"; "assign librarian to llama for fast work"; Yes; ask the librarian anything; open the Monitoring | The Stable lists every mind with where it resides, its class, its price per million, its health, its spend; the interlock NAMES the act ("Adding the llama mind (ollama llama3.2) is consequential …", Cancel default); the new mind answers its canary; the fuel gauge reads the allowance and the spend; after the assignment the librarian's next thought rides llama and the meter shows dollars; THE STABLE view in the Monitoring shows minds, assignments, spent today, thoughts per minute, bodies out of fuel; the harness reads "every mind answers · the gateway holds every mind · the meter and the gateway agree · a model change is announced" | planned | — |
| **SPEC-MEMORY-01** | 0003 · P7 sp5 | Both bridges lit. On :4600 tell the librarian something to remember ("remember that the walk's word is HERON"); on :4600 say "what do you remember about the walk's word?"; open a fresh session (roll) on :4600; then on :4600 say "export compliance for this session" and download; open the JSON | The memory recalled on the Rust door word for word; the rolled session's short version appears on BOTH doors and reads the same; the export from either door is signed by the same kernel self (`signed_by` starts with did:orreth:kernel: and is equal on both), the root hash equal, and "verify" holds; the CSV opens with the same lines | planned | — |
| **SPEC-BODIES-01** | 0004 · 0008 · P7 sp6 | The reference DARK; the Rust kernel lit alone (`scripts/dev.sh kernel`). Open :4601; open the Crew; say "echo, say HERON"; ask the librarian anything and watch the words form; find the echo's pid on its card and kill it by hand (`kill -9 <pid>`); wait; kill it twice more within five minutes; say "restart the echo body"; open the Monitoring; Ctrl+C the kernel (`scripts/dev.sh kernel stop`) | Every body's card reads "process: alive · life 1 · pid …"; the echo answers and the librarian's words stream as they form; the killed echo comes back within seconds as the SAME self (its self line unchanged, life 2) and answers again; after the third death its card reads PARKED with the plain words and the dormant dot; "restart the echo body" brings it back, life 4, its deaths forgotten; the Monitoring shows nine health checks and the harness's last run; after the stop no body process is left (`pgrep -f orreth_spine.body` is empty) | planned | **PASS** (walk #14, JB, 2026-09-25) — no friction reported |
| **SPEC-TOOLDOOR-01** | 0009 §the Tools firmware · P7 sp8 row 2 | The reference DARK. Light the Rust kernel alone: `scripts/dev.sh kernel`; read `~/.orreth/tmp/kernel.log`; open :4600; say "what services are here?"; say "check the services"; say "librarian, what is the temperature outside?"; say "retire the weather tool" and Cancel; then in the shell run `.venv/bin/python3 -m orreth_spine.body --seed-shelf` | The log says "the shelf: N services probed" in the kernel's own voice with NO "[boot rite]" lines (no Python was spawned to seed); the shelf lists every built-in (weather · acquire · mark · purge-memory · add-watch · services · minds · seal-record · erase-record), the ground, the Record and the haiku stall; every built-in's check says "the door answers describe; the schema matches the pin" — never "not probed by this kernel"; the weather still answers (execution is the body's); the interlock still holds with Cancel default; the old one-shot is refused by the body ("unrecognized arguments") | planned | **PASS** w/ friction (walk #17, JB, 2026-09-27, on :4600 alone — the log in the kernel's own voice ("the shelf: 16 services probed", no boot rite); the shelf whole; "checked 16 services — every one answered", every built-in "the door answers describe; the schema matches the pin"; the weather answered for his place in 4.0 s; retire held, Cancel the default; `--seed-shelf` refused by the body. Frictions: **W61** a cancelled hold reads "proof L1" — nothing was proved and the act was L2; the glass defaults an empty proof to L1 · **W62** the retired anthropic mind still wears "health: UNHEALTHY" in the shelf — retired should be its whole state. Both CURED the same day in the glass: a cancelled fold says "nothing ran, nothing was proved"; a retired service reads "at rest — retired, not probed") |
| **SPEC-CELLS-01** | 0002 rule 8 · P7 sp7 | The reference DARK. Light a second universe: `scripts/dev.sh cell two`; then relight the first so it names it: `scripts/dev.sh kernel stop; SPINE_PEERS=two=http://127.0.0.1:4602 scripts/dev.sh shadow`. Open :4601 and :4602 side by side; on each say "what world is this?"; open the Monitoring on :4600 and read PULSE and PEERS; on :4600 say "librarian@two, what is the temperature outside?"; on :4602 open the Analyzer and find the ask; stop cell two (`scripts/dev.sh cell two stop`) and on :4600 say "echo@two, say HERON", then relight cell two; on :4600 say "echo@two, say GULL" and click "stop it" on its line before it answers (or while cell two is dark); on :4602 say "re-home this universe to cell three" and say yes; try an ask on :4602 | Each door names its own universe, cell and epoch (u:dev · cell local · epoch 1; u:two · cell two · epoch 1) and a different kernel; PEERS on :4600 reads "cell two · u:two · live" with who is alive there; the routed ask's journey says "routed home to cell two — librarian answers there", the answer comes from "librarian@two" and :4602's Analyzer shows the same ask "came over the seam from cell local"; with cell two dark the ask reads PARKED in plain words ("echo@two is out of reach — cell two has not answered since HH:MM; your ask is parked …") and PEERS reads "unreachable since HH:MM"; when cell two returns the ask resumes ("cell two answers again …") and HERON arrives once; "stop it" rests the ask with "Stopped on your word …"; the re-home is held at the interlock and on the yes :4602's world tag reads epoch 2 · cell three, its next ask is refused with "re-homed to cell three at epoch 2", and :4601's PEERS shows epoch 2 | planned | **PASS** w/ friction (walk #15, JB, 2026-09-25) — steps 1–10 walked whole; W53–W60 found and cured the same day (W58, the human profile, OWED as the first cure of the post-walk pass) |
| **SPEC-PROFILE-01** | 0003 slot 1 · 0025/0070 carried · P7 sp8 row 1 | On any door say "my name is JB", then "I live in <your town, state>", then "what do you know about me?"; ask "librarian, what is the temperature outside?"; with two cells lit ask "librarian@two, what is the temperature outside?"; say "forget about me: my place" and ask the weather again; say "what time is it?" after "my time zone is Europe/Paris" | Each telling answers "Noted, in your own words — …" and, for the place, "I observed: <place> is at <lat>,<lon>, its clock <zone>"; the portrait reads in labeled groups ("you told me" · "I observed") and the YOU tag under the sun reads "JB · <your town> · <zone>"; the librarian answers the weather FOR YOUR PLACE ("Right now in <your town> (your place, from your profile) …"), on :4600 and routed to cell two alike; after the forgetting the weather answer says "I do not know your place yet" rather than any fixed point; the time answers in Paris | planned | **PASS** (walk #16, JB, 2026-09-26, on :4600 — the tellings, the librarian answering from the profile, the read-back; the routed step, the clock and the forgetting proven by the tests, walked when cell two is next lit) |
| **SPEC-GATE-01** | 0006 §3 · 0071 · P7 sp8 row 3a | The Rust kernel lit (`scripts/dev.sh kernel`); open :4600 in a fresh window: type your name and the code your authenticator shows, take your seat; say "my seat"; open a private window on the same door and sit there too; say "leave my seat" there; in the first window say "enroll quinn" and finish with quinn's first code; in a private window sit as quinn with the next code; as quinn say "stop the kernel's Resiliency intention" and type quinn's code; as jb click "Confirm as master"; in the shell knock without a seat (`curl -s http://127.0.0.1:4600/asks`) and flood `/health` two hundred times AT ONCE (`seq 200 \| xargs -P 50 -I{} curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:4600/health \| sort \| uniq -c` — one knock after another never empties the bucket: it holds 60 and refills 20 a second) | The door opens on the SEAT FORM, never the chat; the first proof makes you the owner ("you hold this ground now, jb"); every door answers as you and the YOU tag says so; a second window sits as the same person on its own proof; a left seat is a seat no more; the owner enrolls another; quinn's seat reads and writes but cannot govern; the master confirms from THEIR OWN seat — no typed name anywhere; a bare curl says `{"error": "not seated"}`; the flood meets "the door is busy for you — try again shortly" | planned | **PASS** w/ friction (walk #18, JB, 2026-09-27, on :4600 alone — the seat form first; the ceremony made him owner; "my seat"; a second window sat and left; quinn enrolled through the QR on the owner's word; quinn seated with the next code and the YOU tag reading quinn; quinn's grave stop held, quinn's code judged right; the hold reached jb's own seat and his click as master ran it ("Done, on jb's word as master after the asker's code: the intention … is at rest"); the bare curl `{"error":"not seated"}`; the flood met "the door is busy for you — try again shortly" once it was a real flood (89 answered · 111 busy of 200 at once; the script's seventy in a row never emptied the bucket — the script was wrong, corrected here). **W64 (WOUND, cured in the walk):** quinn's held act never reached jb's window — the glass drew a hold it did not file only when a BODY proposed it, and the kernel emitted no notice when the asker's code turned the hold over to a master; "open this ask in their glass" named a road that did not exist. Cure: at the code step both kernels file a second `orreth.confirm.needed.v1` on the ask (`step: master`, `code_ok: true`) through the outbox with the held row's change, and every OTHER seated glass draws it with Confirm as master; `tests/gate.rs` green after. **W65 (WOUND, cured, re-walk with the crew relit):** "stopping the kernel's intention" missed the grammar, reached the librarian as a thought, and the librarian answered "I'm stopping it now. That stop is recorded here" — a governed act it holds no tool for and never did (the intention stood). Cure: every body wears the governed-acts law (never perform, never claim the kernel's acts; give the words the kernel hears) and the grammar takes "stopping" · "please stop" · "restarting" · "start" (the second time it bit: "start the kernel's resiliency intention" reached the librarian, who said "I'm starting it now"; the restart itself then ran on the master's road, the hold in the master's words). Frictions cured in the glass: **W63** the YOU tag read "you" for a seated person with no profile name — now the seat's name · **W66** "stop the kernel's standing resiliency intention" missed because a state word was read as the name · **W67** the master's pinned hold repeated the asker's six-digit instructions — the master now reads the master's words) | |
| **SPEC-DESK-01** | 0006 §2–3 · 0012 · P7 sp8 row 3b | The Rust kernel lit with its crew (`scripts/dev.sh kernel`); sit as the owner on :4600; say "who is at the door?"; in the shell play a stranger's body: `cd spine && SPINE_KERNEL_DOOR=http://127.0.0.1:4600 .venv/bin/python3 -c "from orreth_spine import desk; from orreth_spine.identity import Identity; import os; me=Identity.load('scout', os.path.expanduser('~/.orreth/agents')); print(desk.knock('http://127.0.0.1:4600', me, name='scout', kind='resident', template_hash='sha256:walk', policy_hash='', say=print))"`; watch the chat; click Cancel once and run the knock again; this time click Yes; then knock as a SECOND stranger (`Identity.load('scout-two', …)`, name `scout-two`) and, with it waiting, look in quinn's private window — the hold with no button — and decide it yourself; say "who is at the door?" again; run the first knock a fourth time as the same scout | "who is at the door?" lists every crew body as `done · admitted on the crew manifest`; the stranger's knock prints "scout proved its key — waiting at the door for a governing seat's yes" and the chat shows "scout asks to join · the desk" with the plain hold text (its template, a 30-day lease, its words on the feed and nothing more) and Cancel focused; Cancel turns it away ("join refused" in the shell; `denied` at the desk); Yes prints the lease ("lease granted — welcome to u:dev, scout · admitted on jb's word") and the desk says `done`; quinn's click is refused with the one face and the hold stands; the fourth knock is admitted at once "on its standing welcome" with no click; the crew's own /delta words still flow (they wear leases) | planned | **PASS** w/ friction (walk #19, JB in the glass + Fable at the doors, 2026-09-27 — the crew's ten `done · admitted on the crew manifest`; scout's knock staged with the plain hold; Cancel → `denied · join refused · the human said no`, the shell "denied at the door"; Yes → the lease printed with the fuel clause, "welcome to u:dev, scout · admitted on jb's word"; "who is at the door?" listing scout's three rows; the same self's next knock admitted at once "on its standing welcome — the same self, the same world" with no click; the unanswered hold DENIED at fifteen minutes on the kernel's sweep. THE SCRIPT WAS WRONG at its third knock: once admitted, the same self is WELCOMED, so no third hold comes — corrected to a second stranger for quinn's click (the W69 no-button words were seen in quinn's window on the first two holds regardless). Frictions cured the same day: **W73** the hold row named the body by its DID tail ("…4decf2 asks to join") — the hold's args now ride the ask view and the glass says "scout asks to join · the desk" · **W74** the kernel's bubble mashed the desk's words with the L2 wrapper ("Cancel is the default. is consequential — … you can restore it later") — a join's hold speaks the desk's words alone. Open from the walk: W70 (row 4) · W72 (the harness). **W75** (JB's ask, cured): the chat's header names who holds it — "THE ONE CHAT · u:dev · jb" — a human checks this before every word. **W76 (seed, JB):** a soft colour per seated person across the windows a human has open, so the eye knows whose chat it is before the words do — the cockpit's (row 4's glass). The five wounds of this walk day — W64 · W65 · W69 · W71 and the CI's keyless runner — all cured and pushed |
| **SPEC-LOOPS-01** | 0008 · P7 sp4 | Both kernels lit (`scripts/dev.sh kernel` on :4600 and `scripts/dev.sh reference` on :4601). On :4601 (the reference) say “echo, every 5 seconds, say the time, please.”; watch the row on :4600 (the kernel) count once per cadence; make a watch go red through the monitor; stop an intention through :4601; open the harness | The Rust kernel and the Python kernel beat on one ground and never double a beat — one occurrence per cadence, one observation per red per intention, equal on both doors; a stop from the Rust door holds for the code and rests on it; the harness's world checks read off the ground and its mind-run is refused by name | planned | **PASS** w/ friction (walk #11) — the beat lock held on every count; frictions: the seconds grammar (cured in the walk), W34–W40 |
| **SPEC-REMEDY-01** | 0005 P7 sp8 row 3c · 0007 | The Rust kernel lit with its crew (`scripts/dev.sh kernel`); sit as the owner on :4600; say "propose a watch: a body's lease lapsed, bodies_dormant > 0" and click Yes; open the Analyzer and the Monitoring; in the shell kill the echo three times inside five minutes (`kill -9 <pid>` from `GET /bodies`, waiting for it to read alive each time); watch the Monitoring: the watch turns red; wait up to a minute; read Resiliency's row in the Analyzer and open it; say "list my sessions" and open Resiliency's | The chat in Resiliency's session reads as a story in plain words: the planner's ask begins "THE DOSSIER — what the kernel read on the ground" and names the echo "dormant … PARKED by the kernel: it died 3 times"; the planner answers "LEVER: body.restart name=echo — BECAUSE: …"; the kernel's own row says "On the intention's authority the kernel pulled body.restart name=echo: echo is being restarted … Because …"; the echo reads alive again in BODIES as the same self; the watch turns green; the Analyzer's Resiliency row says "last red: cured" and its twig holds the improvement "went green after the kernel pulled body.restart name=echo — the planner's reason: …"; the Monitoring's HEALTH CHECKS show "every red is answered and every green attributed" green. Then kill the echo ONCE: it comes back on its own; if the watch turned red meanwhile, the row reads "last red: self-healed" and no lever was pulled | planned | **PASS** w/ friction (walk #20, JB on :4600, 2026-09-28 morning) — THE RAIL WORKED FOUR TIMES LIVE: four rounds of three kills, four parks, four reds, the real planner (haiku) answered `LEVER: body.restart name=echo — BECAUSE: echo is PARKED after 3 deaths with a lapsed lease …` every time, the kernel restarted the echo within about six seconds, four greens attributed `cured`, the eleventh check green. THE GLASS HID IT — JB: "not seeing the failures show up in monitoring or having it stop after 3" — four frictions, cured the same morning: **W78** the kernel's own hop ("the kernel pulls body.restart name=echo") never reached the chat — no ask.received rides the feed for an ask the kernel served itself; now drawn from its reply fact in every seated chat, "the kernel acts · on the intention's authority" · **W79** the Monitoring's BODIES card showed leases alone (alive · until), never the kernel's process state — now life N · PARKED with the parked words, from the kernel's own /bodies · **W81** the Analyzer's intention row showed "kee…" — the long meta squeezed the words to three letters (JB: "only showing first few characters") · **W82** one morning turn read "the dossier names no dormant body" under a red of value 2 — the dossier read the leases a second time after the snapshot; now ONE read, the snapshot's roster. Also felt: **W70** again — taking the seat after the code reloads the page and the live lines are gone (row 4's feed-driven glass). Not a wound: the echo DID stop after three deaths; the kernel restarted it itself — that is the rail. JB's re-read the same morning: **PASS** — BODIES read `echo · life 6 · PARKED` with the words, the chat showed "the kernel acts · on the intention's authority" and the kernel's reply with the planner's reason, the watch turned green, sixteen attributed ("do believe it worked"). **W83** (cured): the kernel's reply said "restarted on your word" — the human lever's phrase; now "on the intention's word" |
| **SPEC-PANEL-01** | 0005 row 4 · THE PANEL (JB's lock 2026-09-28) · 0006 | Sit as the owner on :4600 with the crew lit; close the chat (Esc) and read the main window: the six organs, the five rails, the stations, the tools, the running board; ask "what is the temperature outside?" and watch; click ARCHITECTURE off and on; click the librarian's station, then "scope the chat here"; click a row on the running board; kill the echo once in the shell and read its station after the kernel restarts it; click ☀ in the ceiling and read the same panel in daylight, then ☾; ask "what is the temperature outside?" once more and watch the shelf; wait for the kernel's harness duty to wake (or ask the monitor to add a watch and stop the echo three times); click PERFORMANCE on the sill and read the GROUND's line and THE DOORS row, then click the slowest door; click ⛶ FULL SCREEN on the sill (or press F), read the panel edge to edge, press Esc until the bridge is back; (re-base sp1) open the Monitoring pull and read the RAILS card's "poison held at" row, then say "advance past parked 1" in the chat; watch the crew rail while the kernel restarts the echo (no timer runs) | The window reads as a still panel with no eye candy: every organ lit jade with a number and words a newcomer can parse; the stations show every body the kernel seats, the parked one amber with the kernel's words; the tools bordered by consequence. On the ask: the DESK flashes amber, the relay and the dispatcher light amber toward the librarian's station, its act line reads "serving …", then cyan back on the reply with the seconds, and the board's row for the ask shows the hops and "librarian · N s · proof L1"; the tape reads "ask received jb · …" then "reply librarian · N s". ARCHITECTURE off hides the empty sockets. The inspector opens in place with what · self · lease · life · serving · meter; "scope the chat here" makes the chat speak to the librarian alone and says so. The board row opens the Analyzer on that origin. After the kill (sp2's bar): within 5 s the presence track lights red toward the echo's station, the station's border reds and its act line reads "lease lapsed", the chip goes dashed, the tape reads "lease lapsed echo · stopped renewing"; when the kernel restarts it the track lights violet, the act line reads "seated by its lease", the chip is solid again. The ☀ turns the whole panel to paper, ink and bronze with every lamp still legible; ☾ brings the night back, and a reload keeps the choice. On the second ask a tool's lamp under the shelf flashes cyan with the dispatcher's track toward it, the tape reads "tool hop librarian · weather", the SHELF's PERFORMANCE line counts one hop. A duty waking lights the scheduler's track toward its runner and the board row reads "on its clock"; a lever the kernel pulls reds the monitor and the intent track toward the body, the tape reads "lever pulled the kernel pulled body.restart · echo — because …". PERFORMANCE (sp3's bar): the GROUND reads "pool N of 16 lines busy · 0 WAITING · M opened for K knocks" with K far above M; every organ's last line names its doors' p95 in milliseconds; THE DOORS row lists every door knocked on in the last ten minutes, the slowest first, none red at rest; the clicked door's inspector reads its knocks, its p50 · p95 · slowest and "within the one-second law", and "watch the doors" puts "monitor, propose a watch that door_p95_ms > 1000" in the chat unsent. FULL SCREEN: the ceiling, the tabs and the floor are gone, the browser is full screen, the panel fills the display with the sill as the one bar reading LEAVE FULL SCREEN · CHAT · ANALYZER; on a wide monitor the drawing is larger; Esc closes what is open first and leaves full screen last; a reload keeps the layout. THE PARKED (sp1's bar): the RAILS card reads "poison held at (the rail waits for a person) 0" in green at rest, and the chat answers "no such parked event" — a person's lever that exists before it is needed (rule 11); a parked poison would show its words, its bytes and an "advance past it" lever on the same card. THE ROSTER (sp1's bar): the chips and the stations refresh on the echo's own facts — its lease lapsing, then its join (a new life) and its seat again — with no 20-second beat behind them | planned | OWED |
| **SPEC-HONEST-01** | 0005 row 4 · THE HONEST GLASS (JB's walk of the Monitoring, 2026-09-29, W84–W88) · covenant rule 11 · rule 13 | Sit as the owner on :4600 with the crew lit (`scripts/dev.sh kernel`); open the Monitoring pull and read PULSE, BODIES, ASKS, WATCHES, PEERS. PULSE: read "spent today (this world, every mind)" beside the STABLE's standing count. BODIES: read every body ONCE by name; hover "N earlier selves" on a name a box's crew once held. WATCHES: read each watch's author under its words; click "rest it" on a red watch of your own and read the chat line; look again. ASKS: read the asks left waiting under the counts; click "stop it" on one and read its reply in the chat (`/ask/<id>`). PEERS: read a peer gone for days and its date; click "forget it" and look again; relight the kernel naming the cell and read it back. Then in a shell: `scripts/dev.sh prune` and read its last line | The pulse reads the money the crew spent today in this world, never $0 over a metered crew, and says "not measured here" for a value this kernel does not carry. Each name is one row; a name a dead self once held reads "· 1 earlier self" beside it, never a second body; a fresh key claiming a name a living self holds waits at the join desk for a governing seat, the hold naming the incumbent. A watch wears its author; "rest it" takes it off the card at once, the card's title counts it rested, the chat says it rests on your word, and it never turns an intention again — its row stays on the ground with who rested it and when. The asks left waiting are listed with who asked and since when; "stop it" cancels one before any body serves it, its reply says so in plain words, and a journey line and the reply are on the feed. A peer four days gone reads "unreachable since 2026-09-25 17:31", never a bare clock; "forget it" takes it off the card on a governing seat's word, recorded on its row; a kernel relit naming the cell names it again. `dev.sh prune` says how many test worlds' rows left the ground, and u:dev is untouched | walked 2026-09-29/30 — the ASKS bar (JB: "I can see ASK Stop over in chat and drop from monitor"); the other cards' verdicts not given in words | PASS w/ friction — W89 the stop's words name no ask · W90 a waiting ask's since wears no date · W91 THE LOST SERVE (six asks waited for days; 27 commands entered the exchange and reached no queue; a returned publish read as delivered; no bench sweep) · W92 the loop on a failed thought — all OPEN, cure after the refresh season (walk #21 in canon 0005 row 4) |
| **SPEC-SHELF-01** | 0010 lock 3 · lock 6 · 0004 AG-9 · 0005 Phase 8 sp2 THE SHELF WIDENED (built 2026-10-05) · covenant rules 1 · 11 · 13 | Sit as the owner on :4600 with the crew lit (`scripts/dev.sh kernel`); read the SHELF organ's second line; click the organ and read the inspector; open the CREW pull's shelf and read the `librarian` template card and the `mind.v0` graph card; say "show the crafts"; say "who wears the librarian template?"; say "what is echo made of?"; say "my drafts"; say "draft a prompt called greeting: Greet the human by name, warmly."; say "my drafts" again; say "cut the greeting draft" and click Yes at the interlock; say "show the prompts"; say "draft a prompt called greeting: Greet the human by name, warmly, and say the date."; say "cut the greeting draft" and Yes; say "retire the greeting prompt" and Yes; say "restore the greeting prompt"; say "echo, say the word HERON once" and open its journey; say `draft a template called bob: {"graph": "mind.v0", "kind": "agent"}` then "cut the bob draft" | The organ's line counts the crafts (e.g. `2 store · 1 mind · 16 crafts`); the inspector lists the twelve kinds and offers "show the crafts" · "my drafts". The template card reads `template librarian · healthy`, `address craft:librarian.template (no self …)`, `worn by 1 body now · a resident body · graph mind.v0`, with "who wears it?"; the graph card reads `1 node: think (think)` and `worn by N bodies`. "show the crafts" lists every craft with `worn by N`. "who wears …" answers `librarian.template is worn by 1 body: librarian (life N, v1)`. "what is echo made of?" lists `echo.template v1 · the-orreth-covenant.policy v1 · echo.v0.graph v1` with pins. "my drafts" says none and teaches the words; after the draft it lists `greeting prompt · draft_… · saved HH:MM`. "cut …" holds at the interlock in words (`cutting the greeting prompt — version 1 onto the shelf`, consequential, L2); Yes answers "Done, on your word: the greeting.prompt is on the shelf as version 1 (registered) — pin …; the draft is spent"; the tape reads `service registered greeting.prompt`; "show the prompts" lists it `worn by 0`. The second cut lands version 2 (`versioned (2)`). Retire holds and rests it; restore stands it registered again. The echo's journey reads `routed to the chat edge — a human's ask` then `the work node runs graph echo.v0: echo` then `echoed every word`. The agent template's cut is REFUSED in the chat in words ("an agent's cut goes through the Experiment … spoonful 4") with nothing held | walked 2026-10-05 evening (JB): every bar | PASS w/ three wounds, all CURED the same night — W99 "draft a prompt called greeting" with no words after it fell through to the fan-out and the crew firmware answered at length, offering to call `acquire` (the glass now catches the half-formed words and teaches the form, never hands them to a body); W100 the retire and restore words doubled a craft's kind ("the greeting.prompt prompt is retired", both kernels and the glass — now "the greeting prompt"); W101 Fable's own script showed the template's JSON with escaped quotes, so the first typing was refused (the script reads plain, and the glass reads `\"` as `"`). Also seen: a cut craft read "never probed" until the keeper's sweep — now probed at the cut |
| **SPEC-WORKSHOP-01** | 0010 lock 6 · lock 8 · 0005 Phase 8 sp3 THE WORKSHOP v0 (built 2026-10-06) · covenant rules 11 · 13 · 0004 AG-9 | **A numbered walk — one thing to do, one thing to see, per step (JB's ask 2026-10-07: the long flows were hard to follow).** Sit as the owner on :4600 with the crew lit (`scripts/dev.sh kernel`). **1.** Say "open the workshop". **2.** Click `mind.v0` under *graphs* on the left. **3.** Say "load the librarian template in the workshop". **4.** Click "+ new draft", leave the kind on graph, name it `bob.v0`, click "start the draft". **5.** Click the `think` block; type "the first thought" in *words*; click "apply to the draft". **6.** Click "add a node after". **7.** With the new block selected, set *kind* to echo and *id* to `greet`; click "apply to the draft". **8.** Click the arrow from think to greet; set *when* to ask and the pattern to `^hello`; click "apply to the draft". **9.** Click the `think` block again; click "add a way out". **10.** Click SAVE under the declaration. **11.** In the chat say "workshop, add an echo node called tail after greet" and wait for the reply. **12.** Say "cut the bob.v0 draft" and click "Yes — do it". **13.** Click `bob.v0` under *graphs*. **14.** Hover the MIND chip in the Workshop's header and read its card. **15.** Say "close the workshop", then "my drafts" | **1.** The Workshop fills the screen with the chat docked on the right: YOUR DRAFTS says none yet; THE SHELF lists the crafts by kind (templates · skills · policies · graphs · bindings · golden sets); the canvas carries its invitation; the inspector asks for a click. **2.** One block `think · entry` ringed cyan reading "THINK · the metered mind"; the inspector reads THE CRAFT read-only — `address craft:mind.v0.graph (no self …)`, pin, `healthy · since …`, worn by N bodies — and WHERE IT STANDS names every wearer and the level it stands on (`u:dev` or its floor); the declaration box is greyed JSON. **3.** The canvas draws `think` under a banner "the librarian template wears graph mind.v0 — drawn from the shelf, read-only here (click mind.v0 under graphs on the left to draft from it)". **4.** The chat says "started your graph draft bob.v0 (draft_…) — under your seat alone"; the rail lists `graph bob.v0` under YOUR DRAFTS; the canvas shows one `think · entry` block; the inspector reads THE DRAFT. **5.** The inspector's words field holds the text; the declaration header reads UNSAVED. **6.** A second block `node-1` appears to the right with a plain arrow think → node-1; the inspector moves to node-1. **7.** The block reads `greet · ECHO · the words back`. **8.** The arrow turns violet and reads "when the ask says /^hello/"; the legend's default line reads `think` alone (every way out of think is conditioned). **9.** A second, plain arrow think → greet reads "otherwise" and bows apart from the violet one; the legend reads "branches at think". **10.** The chat says "saved your graph draft bob.v0 — under your seat alone, not on the shelf; say “cut the bob.v0 draft” …"; UNSAVED is gone. **11.** The workshop agent replies naming the change (a `tail` echo node after greet) and that the cut is yours; the chat then says "your bob.v0 graph draft changed under your seat … the canvas redrew"; the canvas shows think → greet → tail. **12.** The kernel holds it: "Cutting the bob.v0 graph — version 1 onto the shelf is consequential … Cancel is the default"; after Yes the chat says "Done, on your word: the bob.v0.graph is on the shelf as version 1 (registered) — pin …; the draft is spent", the card folds to one line, the tape reads `service registered bob.v0.graph`, YOUR DRAFTS is empty again and `bob.v0 v1` stands under *graphs*. **13.** THE CRAFT reads read-only: `healthy · … the declaration reads whole — 3 node(s): think → greet → tail · branches at think`, worn by no body now; WHERE IT STANDS says "worn by no body now — where a NEXT life stands is chosen on the promotion (spoonful 4), not here". **14.** The chip lists the stalls (`haiku · claude-haiku-4-5-20251001 · Claude the model`) and its card says assigning holds at the interlock (L2) and that Claude the developer is Phase 9, not this chip. **15.** The Workshop slides away and the chat returns to its own size; "my drafts" says none | **Fable's own walk 2026-10-07 on a private kernel (:4610, its own universe `u:fable`, its own schema, the seat `fable` governing): steps 1–11 and 13–15 PASS as written; step 12's hold, Yes and landing PASS, but the "Done, on your word" line and the fold were NOT seen live — found to be the test rig's fault (two kernels pumping one outbox table: JB's :4600 kernel published the test kernel's reply onto its own topics), not the glass's — re-walked on a private schema (`spine_fable`, one kernel per ground): step 12 PASS whole, the card folding to "held at the interlock · you said yes · proof L2 · recorded" and "Done, on your word: the bob2.graph is on the shelf as version 1" arriving live. JB's first walk 2026-10-06/07 (screenshots): the Workshop opened, mind.v0 and the echo template drew, a draft was started and edited node by node, the agent added `tail` on his words, the cut held in plain words — PASS as far as walked; W102 found first (the Workshop covered the chat) and cured; **W103** "policys" in the rail · **W104** the craft card's "(no self …)" note fell into the label column · **W105** the template's banner said "load it in the Workshop" while standing in it · **W106** the journey read "read the session's results by echo, e kernel, crew" (the kernel's name truncated as if a DID) — all four CURED 2026-10-07 | OWED — JB's walk by the numbered steps; W102–W106 cured |
| **SPEC-EXPERIMENT-01** | 0010 §5 · lock 4 · 0005 Phase 8 sp4 THE EXPERIMENT AND THE CUT (built 2026-10-07) · covenant rules 2 · 11 · 13 | **A numbered walk — one thing to do, one thing to see, per step.** Sit as the owner on :4600 with the crew lit (`scripts/dev.sh kernel`); the Workshop's `bob.v0` graph from SPEC-WORKSHOP-01 stands on the shelf (else: step 0 — say "open the workshop", start a graph draft `bob.v0` with one echo node, "cut the bob.v0 draft", Yes). **1.** Say "draft a golden called bob: {\"template\": \"bob\", \"cases\": [{\"ask\": \"hello bob\", \"expect\": [\"hello\"]}, {\"ask\": \"say moon\", \"expect\": [\"moon\"]}]}" then "cut the bob draft" and click "Yes — do it". **2.** Say "open the workshop", click "+ new draft", set the kind to template, name it `bob`, click "start the draft"; in the declaration box set `"graph": "bob.v0"` (the kind reads `agent` already), click SAVE. **3.** Say "cut the bob draft". **4.** Click "Yes — do it". **5.** Say "what levels are here?". **6.** Wait up to a minute; read the chat. **7.** Say "show the experiments". **8.** Click PROMOTE on THE EXPERIMENT card (or say "promote bob to floor ops"). **9.** Click "Yes — do it". **10.** Say "show the seats", then "open the crew". **11.** Say "bob, hello from the owner". **12.** Say "rest bob" and click "Yes — do it". **13.** Say "decommission bob", enter your code. **14.** Say "show the seats". **15.** Say "restore bob" and click "Yes — do it" | **1.** The kernel holds the cut at L2; after Yes "Done, on your word: the bob.golden is on the shelf as version 1". **2.** YOUR DRAFTS lists `template bob`; the inspector reads THE DRAFT; the chat says "saved your template draft bob". **3.** The chat says "an agent's cut goes through the Experiment: opening one on bob (u:dev/f:ops/r:exp-bob-1, 2 golden cases) is consequential — the kernel holds it at the interlock (L2)" and the card asks in plain words: "Opening an experiment on the bob agent — room exp-bob-1 on floor ops of universe dev opens as an experiment room; one arm — the candidate alone; no version of it stands on the shelf yet; the evidence is its golden set (2 cases); the grader and the critic review under their own names; the verdict is a proposal and the promotion is yours". **4.** "Done, on your word: room exp-bob-1 on floor ops of universe dev is open as an experiment room and the experiment exp_… on bob is running"; the tape reads `level opened`, `experiment opened`. **5.** The listing names `room exp-bob-1 on floor ops` as an experiment room. **6.** The chat says "THE EXPERIMENT on bob is running in u:dev/f:ops/r:exp-bob-1 — one arm, the candidate"; then "a reviewer wrote its signed verdict" twice; then THE EXPERIMENT card: `candidate: 2 passed, 0 failed · current: none — the first version`, `the grader (signed): candidate A → candidate · the critic (signed): risk low — …`, `security — an honest empty slot … · identity — …`, `resiliency: no watch turned red while the arms ran · the evidence leans to promote`, with PROMOTE and DECLINE. **7.** The same card again, state `proposed`. **8.** The chat says "promoting bob to version 1 — its next life on u:dev/f:ops — is consequential: the kernel holds it at the interlock (L2)"; the card asks "Promoting bob to version 1 — its next life stands on floor ops of universe dev". **9.** "Done, on your word: bob.template is version 1 on the shelf (pin …) — bob's next life stands on floor ops of universe dev; the room's record is the replay (exp_…); the draft is spent"; the tape reads `service registered bob.template`, `experiment settled`; within a few seconds `body joined bob`. **10.** "bob · active · stands on u:dev/f:ops · bob.template v1"; the crew shows bob alive on floor ops, life 2 (the trial was life 1 — the same self), wearing `bob.template v1`. **11.** bob replies "hello from the owner" (its echo graph) and the journey says bob took it on u:dev/f:ops. **12.** "Done, on your word: bob is at rest — its life stopped at a safe boundary, its self kept, its record whole; say “restore bob” for a new life or “decommission bob” for the grave"; the chat says "bob is rested — its self kept"; the crew shows bob dormant. **13.** The card asks for your code (L3); "Done, on your code: bob is decommissioned — removed: its lease, its gateway key, its bench, its wear links; its DID did:orreth:agent:…, its joins and its record stay"; the chat says "bob is decommissioned — its live objects removed; its DID, its joins and its record stay". **14.** "bob · decommissioned · stands on u:dev/f:ops · bob.template v1". **15.** "Done, on your word: bob returns — a new life from the shelf's standing version, on floor ops of universe dev; never a revival"; within a few seconds `body joined bob`, life 3, and the crew shows bob alive again | — | OWED — JB's walk by the numbered steps |
| **SPEC-OPERATING-01** | 0010 §7 · 0005 Phase 8 sp5 THE OPERATING STATE (built 2026-10-08) · covenant rules 2 · 11 · 13 | **A numbered walk — one thing to do, one thing to see, per step.** Sit as the owner on :4600 with the crew lit (`scripts/dev.sh kernel`) and a live mind in the Stable (haiku). **1.** Say "open the monitor". **2.** Say "echo, the moon is round". **3.** Click 👍 under the echo's reply. **4.** Say "show the measurements". **5.** Wait a minute; read the chat and the tape. **6.** Say "show the measurements" again. **7.** Say "summon critic", then "dismiss critic". **8.** Say "librarian, remember this under improvement: echo should greet before it echoes" — then "librarian, mark an improvement on the echo's last reply: it should greet first" (or any ask that makes the librarian call its mark tool with kind improvement). **9.** Wait for the critic; read the chat. **10.** Say "load my echo draft in the workshop". **11.** Say "register the source bob-src from https://github.com/<you>/<a-repo-with-a-python-module> at <commit> entry <module>:<callable>", then in the Workshop start a graph draft `imp.v0` with one node of kind import naming `bob-src`, SAVE, "cut the imp.v0 draft", Yes. **12.** Say "what levels are here?" | **1.** The MEASUREMENTS card reads TRUST · RECALL · EFFICIENCY · EXPERIENCE · COST, each `unknown` with words like "trust: unknown — no graded yet (never a silent 1.0)"; the WATCHES card lists the five kernel watches, green, "red when trust < 1.0 · now unknown (nothing to measure yet) → green"; the INTENTIONS show "keep this world's operating state at 1.0 …" beside Resiliency. **2.** The echo replies with every word; the reply bubble carries 👍 👎. **3.** The thumb's line reads "thumb up — thank you — recorded; it feeds the Experience measurement and the grader's evidence, never a body directly". **4.** The chat says five lines: recall 1.0000 (N of N served asks replayable …), efficiency 1.0000, experience 1.0000 — 1 of 1 thumbs up, trust unknown, cost by the ask (the echo spends nothing; a librarian ask moves it). **5.** The tape shows `ask received` for "grader, grade the reply ask_… by echo …", the grader's journey reads "routed to the event edge — a marker of kind grading asked for a response" and then "wrote my signed verdict on ask_… under my own name — grade B" (or whatever the grader gave), and a `verdict` fact. **6.** trust reads 1.0000 — 1 of 1 graded replies passed (or 0.0000 if the grader gave D or F — honest). **7.** "critic summoned — it joins this session's crew …" and the chip `critic ·summoned` beside MITL; then "critic dismissed — …". **8.** The librarian's journey shows the mark tool called with kind improvement; the tape reads `marker set`. **9.** The critic's reply names the change; the chat says "the critic proposed a draft for you — echo template: proposed by the critic from marker mk_… — for echo: the echo template: …"; YOUR DRAFTS gains `template echo`. **10.** The Workshop opens the proposed draft read-write with the critic's words in the inspector; the declaration shows the proposed change. **11.** The source stands on the shelf ("the source bob-src stands on the shelf — … entry …"); after the cut, "imp, hello" through a template wearing imp.v0 answers with the repo's words and its journey reads "ran the imported graph bob-src at … — entry …" (a prod universe would read "CANNOT ACT: … runs only in a dev universe at v0"). **12.** No new level — the Operating State opens no room; its reds go to the critic as objectives under the intention | — | OWED — JB's walk by the numbered steps |
| **SPEC-AGENT-01** | SPEC-OPERATING-01 + SPEC-EXPERIMENT-01 + SPEC-CHIPS-01 (sp6, never written as its own row) as ONE thread — JB's ask 2026-10-10 | **THE ONE WALK below** — 39 numbered steps: the ground measured (the monitor · the key checks · the two chips summoned) → the improvement loop closed in the Workshop (your own mark, the critic's proposed draft, W112's discard) → bob made and judged at the gate by all four reviewers → promoted, key-checked, rested, decommissioned, restored → a repo'd graph run inside a hull through the gate a second time | Every arrow in THE ONE WALK, as written | — | **Parts 1–2 PASS (JB, 2026-10-10)** — Part 1 with W113 found; Part 2 on the fourth try, after W112 · W114 · W115 · W116 (the discard left the rail · "in workshop" unheard · the critic named echo's next version as a stranger · the mark door's words · the critic asked back instead of drafting → the proposal REQUIRED as law); JB: "MUCH BETTER RESULTS". **Parts 3–4 PASS (JB, 2026-10-10)** with W117 · W118 · W119 · W120 found and cured on the way (the ghost of a spent draft · PROMOTE spoke to the librarian · "rest bob" went to the intentions · a rest woke Resiliency): the gate closed whole with all four reviewers signed, bob promoted, key-checked, rested, decommissioned on a code, restored as a new life. **Part 5 PASS (JB, 2026-10-11)** — a local repository registered as a source (W121 · W122 on the way: the walk's own pasted words), the import graph cut, the gate a second time on `imp` (1 passed), promoted, "imp, hello" answered "the repo says: IMP, HELLO" from the repo's code inside the hull, the levels listing the experiment rooms and nothing new. **THE ONE WALK WHOLE — PASS**, W112–W122 found and cured on the way; the journey's "ran the imported graph bob-src at …" line not read off a screenshot (the chat's journey folds the steps) — the Python proof holds it. JB's verdict on the EXPERIENCE: "a very difficult process … not a good experience … we're going to have to create a wizard" → THE WIZARD seed in 0005 |
| **SPEC-WIZARD-01** | 0010 spoonful 7 THE WIZARD (JB's lock 2026-10-12, built 2026-10-12) · covenant rules 11 · 13 · W118 | **THE WIZARD WALK below** — THE ONE WALK's Parts 3 and 5 (bob made and judged at the gate; a repo'd graph inside a hull) done through the wizard: eleven numbered steps where the walk had eighteen, no JSON typed, no declaration edited by hand | Every arrow in THE WIZARD WALK, as written | — | OWED (JB in the glass) |
| **SPEC-PATH-01** | 0010 lock 2 · 0005 Phase 8 sp1 THE PATH (built 2026-10-05) · covenant rule 7 · rule 13 | Sit as the owner on :4600 with the crew lit (`scripts/dev.sh kernel`); read the GROUND organ's tag and the levels line under it; say "what levels are here?"; open the CREW pull and read the echo's card; say "echo, say the word HERON once"; say "open floor two" and click Yes at the interlock, then "open room bob on floor ops as an experiment room" and click Yes; say "open floor three as prod" and Yes, then "open room loose on floor three as dev"; say "open room x" (no floor); read the tape as each level opens; relight the kernel with `SPINE_MODE=prod` and read the tag, then relight with it unset | The tag reads `u:dev · dev · cell local · epoch N`; the levels line reads `floor ops · dev · 1 body` (the echo stands on the floor the crew manifest declared) and its hover says who opened it and what rolls up. "what levels are here?" lists every level in words ("floor ops of universe dev — dev · 1 seated here, 1 within") and tells how to open one. The echo's card wears `u:dev/f:ops`; the ask to it is served from the universe exactly as before, its reply on the feed. Each "open …" holds at the interlock as consequential with the level in words; the Yes answers "Done, on your word: floor two of universe dev is open (dev)", the tape reads "level opened floor two · dev · opened on a person's word", the levels line grows; the experiment room says so in the reply and the line; the room asking dev under the prod floor is REFUSED in the chat in words ("mode only tightens down the path …") with nothing held; "open room x" answers that a room opens ON a floor. Relit as prod the tag reads `u:dev · prod` and a relight unset refuses to light with words in the log (a prod universe never loosens) — JB restores dev by dropping the `spine_levels` row's mode or accepts prod | walked 2026-10-05 evening (JB): all bars — the six chat bars, the prod relight, the refused relight | PASS w/ two wounds, both CURED the same evening — W97 the echo's reply read "(no words came back)" (the glass's 600 ms shared read handed the reply notice a stale view); W98 under the prod universe the floors still read dev (the tightening at light touched the universe's row alone; now every level within tightens with it, each a fact) |

## THE ONE WALK — SPEC-AGENT-01 (JB's ask, 2026-10-10: "merge these 3 specs into a single start to finish walkthrough")

SPEC-OPERATING-01, SPEC-EXPERIMENT-01 and the owed SPEC-CHIPS-01 (sp6, never written as its own row) as ONE
thread: a world measured, an improvement proposed, the agent **bob** made, judged at the gate by all four reviewers
(the grader, the critic, the identity chip, the security chip), promoted, asked to prove itself on the cadence,
rested, buried and restored — then a repo'd graph run inside a hull. One thing to do, one thing to see, per step.
Every chat word below is a word the glass hears today (the guide 0.11.6).

**Sit down.** The Rust kernel lit with its crew (`scripts/dev.sh kernel`); seated as the owner on :4600; a live mind
in the Stable (haiku). The timings that matter: the grade beat and the reviewers answer within a minute; the
key-check cadence is 300 s at stock (`SPINE_KEYCHECK_S`). **Before step 1** say "my drafts": if `template bob` or
`golden bob` stands there from an earlier try, say "discard the bob draft" until none does — the golden set and the
template share the name `bob`, and "cut the bob draft" takes the FIRST draft so named (a draft can always be named by
its id instead: "cut draft_3e7bf5f3b1ab").

### Part 1 — the ground, measured (OPERATING 1–6 · CHIPS: the seats and the refusals)

1. **Say "open the monitor".**
   → The MEASUREMENTS card reads TRUST · RECALL · EFFICIENCY · EXPERIENCE · COST. On a fresh world each is
   `unknown` with its reason ("trust: unknown — no graded yet (never a silent 1.0)"); on a lived world each wears
   its number with the count behind it (JB, 2026-10-10: "trust: 0.9250 — 37 of 40 graded replies passed"), red
   below 1.0 — those reds are what THE OPERATING STATE intention hands the critic. The WATCHES card lists the kernel's watches green — the
   five measurements, the ground's connections, and the key-check's ("every seated body proved itself on the
   cadence"); the INTENTIONS show "keep this world's operating state at 1.0 …" beside Resiliency.
2. **Say "show the key checks".**
   → One line: "N key-checks in the last day, 0 failed, none waiting — every seated body is asked every 300 s to
   prove who and what it is" (or "no body has been asked to prove itself yet — every 300 s once one is seated" on a
   fresh world), then up to twenty rows `<name> · asked hh:mm:ss · proven — who it says (<8 of its DID>) and what it says (<8 of
   its declaration's hash>)` (W113 cured the doubled "proven" and the hash cut to one character). In the Monitor the RAILS card carries the
   same line as `key-check` (red only on a failure) and the pulse under GROUND reads "N key-checks today, 0 failed".
3. **Say "summon identity", then "identity, who is seated?", then "dismiss identity".**
   → "identity summoned — it joins this session's crew: address it as “identity, …”; say “dismiss identity” to let it
   go · recorded" and the chip `identity · summoned` beside MITL; its reply says THE SEATS as it holds them — the
   people seated by the ceremony by role (1 owner — a body's lease is a seat too, but never a person: W113 took
   "629 body" out of that line), the bodies alive on a lease, the key-checks of the day — from the
   kernel's record, never its own word; then "identity dismissed — it leaves … · recorded, never deleted".
4. **Say "summon security", then "security, what does the refusals ground hold?", then "dismiss security".**
   → The same summon words for `security`; its reply says THE REFUSALS GROUND: "nothing in the last day — no body was
   turned away at the join or the desk" (or each refusal named: who, which door, when, why); then dismissed.
5. **Say "echo, the moon is round".**
   → The echo replies with every word; the reply bubble carries 👍 👎.
6. **Click 👍 under the echo's reply.**
   → "thumb up — thank you — recorded; it feeds the Experience measurement and the grader's evidence, never a body
   directly".
7. **Say "show the measurements".**
   → Five lines: recall 1.0000 (N of N served asks replayable …), efficiency 1.0000, experience 1.0000 — 1 of 1
   thumbs up, trust unknown, cost by the ask (the echo spends nothing; a librarian ask moves it).
8. **Wait a minute, then say "show the measurements" again.**
   → What happened in that minute, unseen: the kernel's grade beat handed the echo's reply to the grader (an ask the
   KERNEL makes, under a grading marker — not yours, so it never appears in this chat); the grader wrote a signed
   verdict under its own name. What you see: trust's count moved by ONE for the echo's reply and experience's by
   one for your thumb (JB, 2026-10-10: 37 of 40 → 38 of 41 graded; 2 of 4 → 3 of 5 thumbs). On a lived world the
   grade lands within seconds and can be in step 7's numbers already — then steps 7 and 8 read the same, and both
   are right. On a fresh world: trust 1.0000 — 1 of 1 graded replies passed (or 0.0000 if the grader gave D or F).
9. **Close the chat (Esc) and read THE TAPE.**
   → THE TAPE is the strip along the bottom of the Panel — the feed in words, the newest facts first. Among the
   last minute's facts: `ask received` naming "grader, grade the reply ask_… by echo …" (the kernel's own ask) and
   a `verdict` after it. Press C (or say nothing and click the chat) to come back.

### Part 2 — the improvement loop closes in the Workshop (OPERATING 7–10, the mark made deterministic)

10. **Say "echo, hello there".**
    → The echo repeats it. (This reply is the one you mark next — the mark lands on the session's LAST ask, so say
    nothing else in between. After a kernel relight the chat opens a FRESH session with no ask in it yet — "mark
    what? name an ask or a session" is the chat telling you to do this step first. Redoing Part 2 is fine: the
    critic's proposal UPDATES the same draft, never a second one.)
11. **Say "mark this as improvement: the echo should say ‘hello, friend’ before it repeats the words".**
    → "marked ask_… as improvement — critic asked to act"; the tape reads `marker set`. (Name the words you want:
    the critic drafts from your note. With nothing to mark yet — a fresh session, no reply in it — the chat says
    "nothing to mark yet in this session — a mark lands on the LAST reply here; ask something first, then mark it".) (SPEC-OPERATING-01's step 8
    asked the librarian to call its mark tool; a mind may decline, as it did on 2026-10-10 — "I have nothing new to
    mark". Your own mark is the sure door; the librarian's remains the agent's way.)
12. **Wait for the critic; read the chat.**
    → The critic's ask runs under the improvement marker (its journey: "routed to the event edge"); its reply names
    the change it chose (W116: under an improvement marker the kernel REQUIRES the propose tool of the critic on its first
    round — a law on the gateway, not a request to the mind; W115's charge says what to choose); then "the critic proposed a draft for you — echo template: proposed by the critic from marker mk_… —
    for echo: … · say “load my echo draft in the workshop” to read it"; YOUR DRAFTS gains `template echo` — the
    body's own name whatever the critic called it (W114: it said "echo-greet-before-repeat"; a template proposal is
    the body's NEXT VERSION, never a new body).
13. **Say "load my echo draft in workshop".**
    → The Workshop opens the proposed draft read-write (W112: "in workshop" and "in the workshop" both heard — on a
    page loaded BEFORE 2026-10-10 the words fell through to the librarian, who answered in prose; reload the page);
    the inspector reads THE DRAFT with the critic's words; the declaration shows the proposed change. The critic may
    name a craft that is not on the shelf (JB's walk: `"graph": "echo.v1"`) — the canvas says so plainly ("the echo
    template names graph echo.v1, which is not on the shelf — a body wearing it cannot act"); the draft is yours to
    edit before any cut, and the cut would refuse it as it stands.
14. **Say "discard the echo draft".**
    → "discarded your template draft echo — it was never on the shelf, so nothing is kept"; YOUR DRAFTS drops it AT
    ONCE and the canvas clears (W112 — before, the rail kept it until the Workshop was reopened).

### Part 3 — bob is made and judged at the gate (EXPERIMENT 0–9 · CHIPS: the four reviewers)

15. **In the Workshop click "+ new draft", leave the kind on graph, name it `bob.v0`, click "start the draft".**
    → "started your graph draft bob.v0 (draft_…) — under your seat alone"; one `think · entry` block.
16. **Click the `think` block; set its kind to echo and its id to `say`; click "apply to the draft"; click SAVE.**
    → The one block reads `say · ECHO · the words back` and is the entry; "saved your graph draft bob.v0 — under your
    seat alone, not on the shelf; say “cut the bob.v0 draft” …". (An echo at the entry makes the golden set below
    pass by the echo's own law — no mind to guess.)
17. **Say "cut the bob.v0 draft" and click "Yes — do it".**
    → Held at the interlock in plain words; after Yes "Done, on your word: the bob.v0.graph is on the shelf as version
    1 (registered)" — or "version 2 (versioned)" when a bob.v0 already stood there from SPEC-WORKSHOP-01; the tape
    `service registered bob.v0.graph`; `bob.v0` under *graphs*. **On a re-walk** (JB, 2026-10-12, this step): when the
    walk before left the SAME graph, the chat answers "bob.v0.graph already stands on the shelf with these exact bytes
    (version 3) — nothing to cut" and holds nothing — that is a pass, not a wound: the name is the shelf's, the shelf
    keeps the versions, and `bob.v0` stands; go on. (The `.v0` in the name is a habit, not a version the kernel reads;
    a changed graph cut again becomes the next version of the same name.)
18. **Say the golden set — ONE line, typed alone, plain quotes:**
    ```
    draft a golden called bob: {"template": "bob", "cases": [{"ask": "hello bob", "expect": ["hello"]}, {"ask": "say moon", "expect": ["moon"]}]}
    ```
    **then, as its own line, `cut the bob draft`, and click "Yes — do it".**
    → The kernel holds the cut at L2; after Yes "Done, on your word: the bob.golden is on the shelf as version 1";
    `bob` under *golden sets*.
19. **Click "+ new draft", set the kind to template, name it `bob`, click "start the draft"; in the declaration box set `"graph": "bob.v0"` (the kind reads `agent` already); click "apply the JSON to the canvas", then SAVE.**
    → YOUR DRAFTS lists `template bob`; the inspector reads THE DRAFT; the chat says "saved your template draft bob".
    **On a re-walk** the golden set at 18 answers "already stands … nothing to cut" the same way (a pass); and an
    experiment needs a CHANGE to judge — the kernel refuses an agent whose template bytes already stand ("nothing to
    experiment on") — so here also set `"nature": "answers hello with hello, again"` (any new words) before SAVE: step
    20 then opens the experiment as version 2 with TWO arms, the standing bob and the candidate.
20. **Say "cut the bob draft".**
    → "an agent's cut goes through the Experiment: opening one on bob (u:dev/f:ops/r:exp-bob-1, 2 golden cases) is
    consequential — the kernel holds it at the interlock (L2)"; the card: "Opening an experiment on the bob agent —
    room exp-bob-1 on floor ops of universe dev opens as an experiment room; one arm — the candidate alone; no
    version of it stands on the shelf yet; the evidence is its golden set (2 cases); the grader and the critic review
    under their own names; the verdict is a proposal and the promotion is yours".
21. **Click "Yes — do it".**
    → "Done, on your word: room exp-bob-1 on floor ops of universe dev is open as an experiment room and the
    experiment exp_… on bob is running"; the tape `level opened`, `experiment opened`.
22. **Say "what levels are here?".**
    → The listing names `room exp-bob-1 on floor ops` as an experiment room.
23. **Wait up to a minute; read the chat.**
    → "THE EXPERIMENT on bob is running in u:dev/f:ops/r:exp-bob-1 — one arm, the candidate"; then "a reviewer wrote
    its signed verdict on an experiment — the proposal follows when every reviewer is done" FOUR times (the grader,
    the critic, the identity chip, the security chip — each under its own DID); then THE EXPERIMENT card:
    `candidate: 2 passed, 0 failed · current: none — the first version` · `the grader (signed): candidate A →
    candidate · the critic (signed): risk low — …` · **`the identity chip (signed): claims kept — …`** (the trial life
    joined as bob's own self, stood on the candidate's declaration, in exp-bob-1, and left whole) · **`the security
    chip (signed): clear — …`** (a first version: everything is new; nothing on the refusals ground) · `resiliency: no
    watch turned red while the arms ran · the evidence leans to promote`, with PROMOTE and DECLINE. A chip not
    seated or silent ten minutes reads `the identity chip: MISSING — …` by name, never guessed; a broken claim or a
    concern would HOLD the leaning.
24. **Say "show the experiments".**
    → The same card again, state `proposed`.
25. **Click PROMOTE on the card (or say "promote bob to floor ops").**
    → "promoting bob to version 1 — its next life on u:dev/f:ops — is consequential: the kernel holds it at the
    interlock (L2)"; the card asks "Promoting bob to version 1 — its next life stands on floor ops of universe dev".
26. **Click "Yes — do it".**
    → "Done, on your word: bob.template is version 1 on the shelf (pin …) — bob's next life stands on floor ops of
    universe dev; the room's record is the replay (exp_…); the draft is spent"; the tape `service registered
    bob.template`, `experiment settled`; within a few seconds `body joined bob`.

### Part 4 — bob lives, proves itself, rests, dies, returns (EXPERIMENT 10–15 · CHIPS: the key-check)

27. **Say "show the seats", then "open the crew".**
    → "bob · active · stands on u:dev/f:ops · bob.template v1"; the crew shows bob alive on floor ops, life 2 (the
    trial was life 1 — the same self), wearing `bob.template v1`.
28. **Say "bob, hello from the owner".**
    → bob replies "hello from the owner" (its echo graph); the journey says bob took it on u:dev/f:ops.
29. **Five minutes after bob joined (the cadence) — or any time later — say "show the key checks".**
    → A row `bob · asked hh:mm:ss · proven`: the kernel repeated the join desk's challenge over the rail, bob signed
    the kernel's own nonce on its bench and never marked itself ok, the kernel verified the key derives bob's DID
    and the hash is the one it joined as; the tally's `failed` stays 0 and the key-check watch stays green.
30. **Say "rest bob" and click "Yes — do it".**
    → "Done, on your word: bob is at rest — its life stopped at a safe boundary, its self kept, its record whole; say
    “restore bob” for a new life or “decommission bob” for the grave"; the chat "bob is rested — its self kept"; the
    crew shows bob dormant (a dotted outline on the Panel's station). Resiliency stays QUIET: a rest on your word is
    not a dormancy to cure (W120 — before it, the dormant-bodies watch turned red and the planner reported "no
    lever fits … this one is yours").
31. **Say "decommission bob", enter your code.**
    → The card asks for your code (L3); "Done, on your code: bob is decommissioned — removed: its lease, its gateway
    key, its bench, its wear links; its DID did:orreth:agent:…, its joins and its record stay"; the chat "bob is
    decommissioned — its live objects removed; its DID, its joins and its record stay".
32. **Say "show the seats".**
    → "bob · decommissioned · stands on u:dev/f:ops · bob.template v1".
33. **Say "restore bob" and click "Yes — do it".**
    → "Done, on your word: bob returns — a new life from the shelf's standing version, on floor ops of universe dev;
    never a revival"; within a few seconds `body joined bob`, life 3, and the crew shows bob alive again.

### Part 5 — a repo'd graph inside a hull (OPERATING 11–12; the gate a second time)

The import needs a git repository holding a Python module with a callable (or a compiled LangGraph with `invoke`).
No GitHub needed — a local repository is a repository. **In a shell:**

```
mkdir -p ~/orreth-walk/bobrepo && cd ~/orreth-walk/bobrepo && git init -q
printf 'def answer(text):\n    return "the repo says: " + text.upper()\n' > bobgraph.py
git add . && git commit -q -m one && git rev-parse HEAD
```

The last line prints the commit; the repo's path is `/Users/jb/orreth-walk/bobrepo`.

34. **Say the registration — ONE line, typed alone (put the commit the shell printed in place of the hex):**
    ```
    register the source bob-src from /Users/jb/orreth-walk/bobrepo at 25649bb1dd16 entry bobgraph:answer
    ```
    → "the source bob-src stands on the shelf — /Users/jb/orreth-walk/bobrepo at <commit's first 12>, entry
    bobgraph:answer; a graph node of kind import naming it runs the repo's entry inside the hull (a dev universe
    only)"; `bob-src` among the sources.
35. **In the Workshop click "+ new draft", kind graph, name `imp.v0`, "start the draft"; in the declaration box replace the nodes and the entry so it reads `"entry": "run", "nodes": [{"id": "run", "kind": "import", "source": "bob-src"}], "edges": []`; click "apply the JSON to the canvas", then SAVE.**
    → The canvas draws one block `run · entry` of kind import (the inspector's kind list holds think and echo — an
    import node is written in the JSON); "saved your graph draft imp.v0". A node of kind import without a `source`
    refuses at the cut: "an import node names its `source` — the repo'd source on the shelf (repo · commit · entry)".
36. **Say "cut the imp.v0 draft", Yes.**
    → "Done, on your word: the imp.v0.graph is on the shelf as version 1".
37. **The gate a second time, in five sentences, each typed alone. First the golden set:**
    ```
    draft a golden called imp: {"template": "imp", "cases": [{"ask": "hello", "expect": ["HELLO"]}]}
    ```
    **then `cut the imp draft` and Yes. Then in the Workshop: "+ new draft", kind template, name `imp`, "start the
    draft"; in the declaration box change the graph line to `"graph": "imp.v0"`, click "apply the JSON to the
    canvas", SAVE. Then `cut the imp draft` and Yes.**
    → The gate a second time: room exp-imp-1 opens; the trial life fetches the repo at its commit under
    `~/.orreth/imports/bob-src/<commit>/` and answers the golden case "the repo says: HELLO" — `candidate: 1 passed,
    0 failed`; the four reviewers sign (the security chip reads the candidate's diff — a first version, everything
    new — against the refusals ground); the card leans to promote.
38. **Click PROMOTE, Yes; then say "imp, hello".**
    → `body joined imp`; imp replies "the repo says: HELLO" and its journey reads "ran the imported graph bob-src at
    <commit's first 12> — entry bobgraph:answer". (A prod universe would read "CANNOT ACT: the imported graph bob-src
    runs only in a dev universe at v0".)
39. **Say "what levels are here?".**
    → The two experiment rooms (exp-bob-1 · exp-imp-1) and nothing more — the Operating State opens no room; its
    reds go to the critic as objectives under the intention.

**The bar is every arrow above, as written.** Anything else is a wound: say what you saw, in which step.


## THE WIZARD WALK — SPEC-WIZARD-01 (JB's lock 2026-10-12: "we're going to have to create a wizard")

THE ONE WALK's Parts 3 and 5 again — bob made, judged at the gate by all four reviewers, promoted and joined; then a
repository's code inside a hull — with the words the glass gave to a person's way in. No JSON is typed, no declaration
is edited by hand; every Yes is still your click at the interlock in the chat. One thing to do, one thing to see, per
step. **Sit down** as THE ONE WALK sits: the Rust kernel lit with its crew, seated as the owner on :4600, a live mind in
the Stable. **Before step 1** say "my drafts": if a `bob` or `bob.v0` draft stands there from an earlier try, the wizard
UPDATES it on SAVE (never a second one) — nothing to discard. If bob already STANDS on the shelf from THE ONE WALK,
give the wizard different words at step 2 (say `answers hello with hello, again`): a graph or golden set whose exact
bytes already stand is skipped as standing ("nothing to cut" is a pass), but the agent's own cut needs a change to
judge — the kernel refuses a template whose bytes already stand ("nothing to experiment on"), and the wizard says so
with the way back.

### Part A — bob, through the wizard (THE ONE WALK 15–26 in six steps)

1. **Say "new agent"** (or open the Workshop and click **+ new agent · the wizard** on the left). A draft open on the
   canvas is no bar: the wizard takes the canvas, the draft stays under your seat. To see the first screen itself say
   "clear the workshop" or click "close the draft" (nothing is discarded).
   → The Workshop opens with THE WIZARD in the inspector on the right: a strip of eight steps (NAME · GRAPH · GOLDEN
   CASES · SAVE · CUT · THE CARD · PROMOTE · JOINED) with NAME lit, a name field and a line for what it is for; the
   canvas reads "THE WIZARD · name the agent in the inspector on the right"; the left rail's "+ new agent" row is lit.
2. **Type `bob` as the name, `answers hello with hello` as what it is for; click "next — its graph".**
   → GRAPH lit. The entry node's kind reads "echo — the words back (the sure start …)"; the canvas draws ONE block
   `say · entry · ECHO · the words back`; the declaration box reads the graph `bob.v0` as JSON, read-only, headed
   "THE WIZARD fills it · graph bob.v0". (If bob already holds a seat from an earlier walk, a note says this wizard
   makes its NEXT version and the Experiment will run two arms.)
3. **Leave the kind on echo; click "next — its golden cases".**
   → GOLDEN CASES lit, two rows filled for you: `hello bob` must contain `hello` · `say moon` must contain `moon`;
   the declaration box reads the golden set `bob`.
4. **Click "next — save the drafts", then "SAVE the three drafts".**
   → The SAVE step lists the three in words (graph bob.v0 · golden set bob, 2 cases · template bob wearing graph
   bob.v0), then: the chat says "the wizard saved three drafts under your seat for bob …"; YOUR DRAFTS on the left
   gains `graph bob.v0` · `golden set bob` · `template bob` — ordinary drafts (click one later and it opens for a
   hand); CUT lit, the three cuts listed with a dot each, and the button "CUT — start with the graph → the interlock".
5. **Click CUT; in the chat click "Yes — do it" — three times, as each hold arrives.**
   → First: "cutting the bob.v0 graph onto the shelf (register → version 1) is consequential — held at the
   interlock"; the wizard's list reads "▸ the graph bob.v0 — held at the interlock: click Yes — do it in the chat".
   After Yes: "Done, on your word: the bob.v0.graph is on the shelf as version 1 (registered)" (or version 2 when an
   earlier walk left one; or, when it left the SAME bytes, no hold at all — the chat says "… already stands on the
   shelf with these exact bytes (version 3) — nothing to cut; the wizard goes on" and the line reads "✓ … it stands"),
   the line turns to ✓, and the golden set's hold arrives AT ONCE — the wizard files the next cut on your Yes. After the second Yes: ✓ the golden set, and the third hold: "an agent's cut goes through
   the Experiment: opening one on bob (u:dev/f:ops/r:exp-bob-1, 2 golden cases) …" with the card "Opening an
   experiment on the bob agent …". After the third Yes: THE CARD lit — "THE EXPERIMENT · bob · running in
   u:dev/f:ops/r:exp-bob-1 — one arm, the candidate · the grader, the critic, the identity chip and the security chip
   are judging it …"; the tape `level opened` · `experiment opened`. (Cancel any hold instead and the wizard says
   "you cancelled … nothing ran; CUT goes on from here when you are ready" — CUT resumes at that cut.)
6. **Wait up to a minute.**
   → "(N signed so far)" counts the reviewers as the chat says "a reviewer wrote its signed verdict …"; then THE
   CARD lands INLINE in the wizard: `candidate: 2 passed, 0 failed · current: none — the first version` · the grader
   (signed) · the critic (signed) · the identity chip (signed): claims kept · the security chip (signed): clear ·
   "the evidence leans to promote" — the same card the chat shows, under it the one field "where the next life
   stands" reading `floor ops` (the experiment room's own floor), and "PROMOTE bob → the interlock" · decline.
7. **Click "PROMOTE bob → the interlock"; in the chat click "Yes — do it".**
   → PROMOTE lit: "promoting bob to version 1 — its next life on f:ops — held at the interlock: click Yes — do it in
   the chat"; after Yes "Done, on your word: bob.template is version 1 on the shelf … bob's next life stands on floor
   ops of universe dev …", the wizard reads "bob's next life is being seated from the shelf — the join lands here
   within a few seconds"; then JOINED lit: "bob JOINED · a life begins — bob stands on f:ops, wearing bob.template
   v1 — say “bob, hello” in the chat"; the tape `body joined bob`.
8. **Click "say hello to bob", press Enter.**
   → The chat holds `bob, hello`; bob replies "hello" (its echo graph), the journey says bob took it on
   u:dev/f:ops. (Part 4 of THE ONE WALK — the key check, rest, decommission, restore — is unchanged and stands.)
   A candidate that fails a golden case (W131, imp2 2026-10-13: asked "hi", expected HELLO, the repository replied "the repo says: HI") is a PASS of the gate, not of the agent: the card opens with the tally in plain words and "fix the golden cases" declines the experiment and stands the wizard at GOLDEN CASES — fix the case (the reply must CONTAIN the expected words), next, SAVE, CUT again. One agent in flight (W130): "+ new agent" resumes it; "start another, let <name> go" begins at NAME. Part B's name is imp2 when imp already stands.

   THE CARD READS THE GROUND (W133, jonathan 2026-10-13): from the third Yes the wizard reads the experiments door every few seconds, so a card that says "running" is reading, not stuck; the proposal lands in the wizard AND as a card in the chat; a feed that has fallen changes nothing. A reload keeps the wizard's place (W134): "+ new agent" says "resume <name> at <step>". Clicking the agent's draft on the left while the wizard holds it shows "this draft is the wizard's — resume the wizard at <step>" and, for the template, THE EXPERIMENT's card with promote and decline (W135). Retired crafts and experiments' trial lives at rest are folded in the rails (W136) — "N retired crafts at rest · show".

### Part B — a repository's code, through the wizard (THE ONE WALK 34–39 in three steps)

The same local repository as THE ONE WALK's Part 5 (`~/orreth-walk/bobrepo`, `bobgraph.py` with `answer(text)`
returning `"the repo says: " + text.upper()`, committed; the shell printed its commit).

9. **In the wizard click "make another agent" (or say "new agent"); name it `imp`, click next; set the entry node's
   kind to "import — a repository's code answers"; in the source picker choose "+ register a source now…"; fill its
   name `bob-src`, the repository `/Users/jb/orreth-walk/bobrepo`, the commit the shell printed, the entry
   `bobgraph:answer`; click "register the source → the shelf".**
   → The chat says "the source bob-src stands on the shelf — … entry bobgraph:answer; a graph node of kind import
   naming it runs the repo's entry inside the hull (a dev universe only)"; the wizard's note "the source bob-src
   stands on the shelf — the entry node runs it"; the picker reads `bob-src` with its path, commit and entry under
   it; the canvas draws ONE block `run · entry · IMPORT · a repository's code · source bob-src`. (If bob-src stands on
   the shelf from an earlier walk, pick it in the picker instead.)
10. **Click "next — its golden cases"; in the one row leave the ask `hello` and type `HELLO` as what the reply must
    contain; click next, then SAVE; then CUT and Yes three times, as in step 5.**
    → The hint over the rows says what to expect of a repository; the three drafts `imp.v0` · `imp` · `imp` saved;
    the three cuts land; THE EXPERIMENT on imp opens in exp-imp-1; within a minute the card: `candidate: 1 passed,
    0 failed`, the four reviewers signed (the trial life fetched the repository at its commit and answered "the repo
    says: HELLO"), the evidence leaning to promote.
11. **Click "PROMOTE imp → the interlock", Yes; then "say hello to imp", Enter.**
    → `body joined imp`; JOINED lit; imp replies "the repo says: HELLO" and its journey reads "ran the imported graph
    bob-src at <commit's first 12> — entry bobgraph:answer". Say "what levels are here?": the two experiment rooms
    (exp-bob-1 · exp-imp-1) and nothing more.

**The bar is every arrow above, as written.** THE ONE WALK's eighteen steps for these two parts stand beside these
eleven — the walker's way and the record; the wizard is the person's way in.


## THE STUDIO WALK — SPEC-STUDIO-01 (canon 0011, JB's lock 2026-10-13)

The measure is JB's: *"how well Orreth can do it vs YOU"*. Part A is by hand on the bench; Part B
(spoonful 11) is by the Workshop agent on one brief. Each typed sentence stands alone in a code block.

### Part A — one effort, one place (sp8 THE BENCH; walked by JB in the glass, OWED)

1. **The rail.** Open the Workshop. The left rail reads YOUR BENCHES first (none open, or the ones
   you left), then LOOSE DRAFTS, then THE SHELF folded by kind with counts (click a kind to open
   it), then THE HOUSE folded under one row. The chat's residents rail shows the agents you made
   first and "the house · N" folded. PASS: no scrolling zoo; a search by name still opens every fold.
2. **A new bench.** Click "+ new agent". NAME it `studio1`, next. PASS: the rail shows the bench
   `studio1 · at GRAPH`; the inspector is the wizard at GRAPH; the bench's row is lit.
3. **The place survives.** Click "leave the bench". Reload the page. Open the Workshop. PASS: the
   bench stands on the rail at GRAPH; click its row and the wizard opens there, the name filled.
   Then, in the chat:

   ```
   open the studio1 bench
   ```

   PASS: the same.
4. **The drafts under the bench.** GRAPH echo, next; one golden case `hello` → `HELLO`, next; SAVE.
   PASS: the three drafts stand UNDER the bench's row on the rail (not under LOOSE DRAFTS); click
   the template draft — the inspector says "this draft is on the studio1 bench, which stands at
   CUT" with "open the studio1 bench at CUT"; click it.
5. **The second face.** CUT. PASS: the hold stands pinned in the chat AND on the bench's card with
   its own "Yes — do it" and Cancel. Click Yes ON THE CARD. PASS: the chat's pinned hold folds to
   "held at the interlock · you said yes", the kernel's "Done, on your word" lands in the chat, the
   wizard goes on to the next cut. Answer the second hold IN THE CHAT. PASS: the card's face settles
   too. The third cut opens the experiment; the card reads it from the ground (W133).
6. **A bench, let go.** Say:

   ```
   my benches
   ```

   PASS: `studio1 · at THE CARD · 0 drafts · an experiment open` (the drafts are spent by the cuts).
   Click "let the studio1 bench go" on the card (or say `let the studio1 bench go`). PASS: the line
   "the studio1 bench is let go — 0 drafts discarded, 1 experiment declined; what reached the shelf
   stays"; the rail shows "1 bench at rest · show"; the shelf keeps studio1.v0 · studio1 golden ·
   nothing promoted.
7. **Joined closes the bench.** "+ new agent" → `studio2`, echo, `hello` → `HELLO`, SAVE, CUT ×3
   (either face), the card, PROMOTE, Yes, "studio2 JOINED". PASS: the bench rests on its own
   ("2 benches at rest"); studio2 stands in the chat's residents rail ABOVE "the house".
8. **The true graph (sp9).** "+ new agent" → `lang1`, GRAPH import, "+ register a source now": name
   `lang-src`, the repository `/Users/jb/orreth-walk/langrepo` (a compiled LangGraph `graph` with the
   nodes greet → shout; make it with the five lines in canon 0011's walk note, `git init`, one commit),
   its commit, entry `langgraph_app:graph` — "register the source → the shelf" (or "next", which registers a
   filled form itself; the picker reads "+ register a source now…" until the source stands on the shelf, W141);
   golden case `hello` → `HI HELLO`; SAVE, CUT ×3. PASS: when
   the card lands, the canvas shows THE TRUE GRAPH under the drawn graph — start · greet · shout · end,
   the conditional way out dashed — read by the trial run. PROMOTE, Yes, JOINED. In the JOINED step's
   box, ask `hello`. PASS: the reply `HI HELLO` lands in the chat; greet and shout light on the true
   graph with "the last run took 2 hops: greet → shout". Ask `yo`. PASS: `hi yo`, one hop lit.
9. **The nested drawing (sp9b + sp9c).** Open the `lang1` bench (or the `lang1.v0` graph under
   graphs). PASS: ONE drawing, boxes inside boxes — THE HULL the outer box (violet) with its stages
   `hear → recall → route → work → reply`; inside **work** (amber) your graph; inside the import
   block `run · IMPORT · lang-src` (cyan) the code's own graph — start · greet · shout · end, a
   conditional way out dashed. First sight is centred on your graph, readable, the ring peeking at
   both sides; **fit** (top right) shows the whole; drag pans, the wheel zooms. Click the `run`
   header. PASS: it folds to one block "4 nodes inside · lang-src · open ▸"; click it, it opens.
   Click the `run` box itself. PASS: the inspector reads the node. Say `lang1, hello` in the chat.
   PASS: when the reply lands, hear · recall · route · work light "the ring, taken", then greet and
   shout light in turn ("hop 1", "hop 2"), the edges between them amber, then reply; the legend
   reads "the last run took 2 hops: greet → shout". On the bench's card at THE CARD (a fresh agent
   `lang2` through the wizard, same source), PASS: the card lists "replay case 1 · “hello”";
   clicking it plays the trial run's hops through the boxes. Say `lang1, yo`. PASS: greet alone
   lights, the way to end dashed and taken.
10. **How the kernel works (sp9c).** Close the Workshop. Say `how the kernel works` in the chat.
   PASS: a window opens over the Panel, HOW THE KERNEL WORKS, its line naming THIS kernel (rust ·
   its version · schema 12); the map draws seven boxes — YOU AND YOUR SEAT · THE DOORS (45 doors)
   · THE HULL (hear → recall → route → work → the reply) · THE MINDS · THE HOUSE (N residents
   seated now) · THE GROUND (52 tables · schema 12) · THE WATCHES — with one ask's road numbered
   1 → 7 across them in amber. Click THE DOORS' header. PASS: it folds to "5 nodes inside"; click
   it, it opens. Click the `gateway` block. PASS: its words read under the drawing. Press Esc.
   PASS: the window closes and nothing else does. Click HOW IT WORKS on the sill. PASS: the same
   window opens. Reload the page on :4601 (the Python reference) and say it again. PASS: the same
   map, the line naming `reference` — the declaration is one, served by both.
11. **One word to work (sp10).** "+ new agent" → `work1`, GRAPH echo, one golden case `hello` →
   `HELLO`, SAVE. PASS: the strip reads 5 PUT TO WORK (not CUT); the step says one word, one Yes,
   and offers one button "put work1 to work → the interlock". Click it. PASS: the chat holds ONE
   act whose words name the whole chain — "Putting work1 to work - the graph work1.v0 as version 1
   · the golden set work1 as version 1 · the agent work1 as version 1 -> the experiment" — and the
   bench lists the same three lines with ▸; nothing is on the shelf yet (THE SHELF's graphs count
   is unchanged). Click "Yes — do it". PASS: ONE "Done, on your word" line names the graph and the
   golden set on the shelf as version 1 and the experiment room open; the tape reads `service
   registered work1.v0.graph`, `service registered work1.golden`, `experiment opened`; the bench
   moves to THE CARD by itself. Say `put work1 to work` in the chat now. PASS: refused in words —
   "an experiment on work1 is already running … its card is the next step". After PROMOTE and
   JOINED, "+ new agent" → `work1` again (a new bench, same name), GRAPH echo, the same golden case,
   SAVE, click PUT TO WORK. PASS: refused before any hold — "the work1 template stands unchanged
   (version 1) - an experiment needs a change to judge: change what work1 is for, or its graph,
   then put it to work again". Change the words at NAME, SAVE, PUT TO WORK. PASS: the hold's lines
   read "the graph work1.v0 stands (version 1) - unchanged, skipped · the golden set work1 stands
   (version 1) - unchanged, skipped · the agent work1 as version 2 -> the experiment".
   **WALKED by JB 2026-10-14 — PASS**, validated on the ground (one hold at 00:27:40; the graph and
   the golden set on the shelf at the Yes, 00:28:04, one transaction; the experiment proposed at
   00:28:18 with four signed reviewers; promoted at 00:39:13, the template landing then; work1
   seated on floor three; the second try refused "template stands unchanged"). Found and cured the
   same day: **W145** — "back" to NAME then a new name forked the bench (now: the effort moves, the
   old bench let go with a line); **W146** — the trial lit nothing on the canvas (no hops for a
   declared graph's own nodes; now: every node the hull walks is a hop under the graph's name).
   The critic read the lawful pass ("HELLO" inside "hello work1") as a broken yardstick — every
   reviewer is now told the harness's law. Walk again after the cure: "+ new agent" → `work3`,
   GRAPH echo, SAVE, PUT TO WORK, Yes. PASS: while the trial runs the canvas lights `say` inside
   the work box (the ring with it); the card's "replay case 1" plays it again; the chat's card
   carries a picker for where the next life stands, and its promote button says the pick as a
   word. Then "+ new agent" → `work4`, next, back, change the name to `work5`, next. PASS: one
   line — "the work4 bench let go — the effort continues as work5"; THE SHELF lists one bench,
   `work5`, none named work4; the golden case reads "hello work5".

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

### Walk #5 — 2026-09-20, the owed specs (lean, at 80% of the session)

MONITOR-01's wound re-walked green → **Phase 4 closes WHOLE**. FULL-01's
acquire half green. Two wounds, both cured the same hour: SCOPE-01 — the
window's record was packed but deep and unlabeled and the mind denied
it (now first, under a header, named by the body's law); MARK-01 — the
critic's act landed outside the chat's session (now in it, and the chat
shows the kernel's asks). SESSION-01's short version was not exercised
(no roll in the walk; sessions predating the Digest now get theirs from
the log). Friction: marker authors were cut to eight characters (named
now); the why printed ids (words now). Not walkable: an opt-out session
(no words for it yet); killing a body. Phase 5 stays BUILT, whole on the
next walk of SCOPE-01 · SESSION-01 · MARK-01's fourth bar.
The before-walk remainder (old glass) stays owed.
