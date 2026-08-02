# 0044 — The Bell

*Drafted 2026-08-02 · Fable 5 with JB · status: **CLOSED WHOLE 2026-08-02,
era 0.44** — designed, locked, and all four spoonfuls proven in one day*

## 1. The seed

Committed by JB 2026-07-31 (`../decisions/README.md`, "the Bell, and the
rubric's field"): G1's remainder and G8 from the Observatory's gap register
are ONE dive. The glass can say "THE WATCHER HAS NO PULSE" — but only to a
human already looking at it. A degradation card staged at an unopened
Console is a tree falling in an empty forest. Monitoring exists "to assess
the Universes we are going to create," and a bell nobody hears is not
monitoring.

Two organs, one dive:

- **The witness** — a dead-man's watch that does not live inside the thing
  it watches. The worker carries the Observatory; the daemon must notice
  the worker's silence and say so without the glass being open.
- **The bell** — a governed out-of-band notification door: the one organ
  allowed to reach a human who is NOT at the Console, under consent, on
  the record, content-minimal.

Timing lock (standing): before any universe runs unattended for someone
who is not JB.

## 2. The laws

1. **The witness observes absence; it never invents.** It knows one fact —
   "the worker last touched me at T" — and speaks only when the silence
   exceeds the declared threshold. Its statement is a signed record naming
   T and the threshold, authored by the daemon's scribe about the worker
   (author ≠ subject; rule 2 holds even for obituaries).
2. **The bell is a resident, not a side door.** A farm service with its own
   DID and a pinned manifest naming its transport. Its sends are metered
   under its DID like any other resident's work (0019 — no organ thinks or
   speaks off-meter).
3. **No send without standing consent.** A consent bundle in becky's ledger
   (0034 grammar) names the human, the endpoint, and the ring kinds
   permitted. No bundle, no ring — the bell refuses with the one face
   (0002 §4). Revocation is one word and takes effect on the next ring.
4. **Content-minimal, pointers never payloads.** A ring carries scope,
   kind, age, and a pointer to the Console — never record bodies, never
   prompt content (0016 extends out-of-band), never memory. The endpoint's
   operator learning a ring happened must learn nothing else.
5. **The record precedes the wire.** Every ring lands as a signed record
   BEFORE transport is attempted; the transport's outcome (sent · failed)
   lands as a second record. A bell that rang off the record never rang.
6. **The bell must not become noise.** One ring per (kind · subject) per
   declared cooldown window; repeats age into the existing ring's record.
   Alarm fatigue is the monitoring organ's own failure mode — a bell
   ignored is a bell broken.
7. **A ring never moves a clock.** Silence at a gate stays denial (0012);
   the bell notifies that consequence waits — it never extends the wait,
   approves, or escalates. The human's seat is not delegable.

## 3. The ring grammar

Any organ may REQUEST a ring by staging a `ring` intent at the bell's
door: `{kind, scope, subject, age, pointer}`. The bell enforces consent,
cooldown, and the content-minimal shape — the requester's words never pass
through verbatim. Founding kinds:

| kind | speaks when | first subscriber |
|---|---|---|
| `witness` | the worker's pulse is gone past threshold | the daemon (sp1) |
| `gate-age` | a staged gate has waited past a declared age | the worker's beat |
| `tamper` | the standing verify beat finds a published deed altered | the verify beat (fold, JB's lock) |

vera's degradation cards deliberately do NOT ring in v1 — they stage at
the gate as ever. Quality news can wait for the glass; absence and tamper
cannot. (Widening the kinds is a one-row change behind consent.)

## 4. The spoonfuls

| # | Spoonful | Proof |
|---|---|---|
| 1 | **The witness** — the daemon tracks the worker's last touch (the beats it already receives); silence past threshold → the signed silence record + a `witness` ring staged. Threshold declared, env-defaulted, visible in the room · **LANDED 2026-08-02**: `POST /worker/pulse` (the touch, carrying nothing) · the watch loop in orrethd (10s tick, 90s threshold, env may lengthen never silence, one card per episode, a returning pulse closes it) · the finding staged in the daemon's book with pg write-through · the two-tier completion: the returned worker TRANSCRIBES the daemon-stamped card into a signed Chronicle record (vera as the observatory's scribe, body naming its source — the 0043 decisions-book precedent), the card left STAGED for the human · `witness` gate words in the glass · **PROVEN BY KILL, CONSOLE CLOSED**: killed 19:50:29Z → the book spoke at 19:52:14Z on its own (98s silence ≥ 90s), no glass open — then the risen worker transcribed it. One first-tick bug caught live: the sync pg write-through on the async runtime poisoned the requests lock (the submit door's own law, violated); healed with its `spawn_blocking` pattern and named in a comment | kill the worker with the Console CLOSED; the silence record exists before any glass opens — ✓ RAN |
| 2 | **The bell service** — farm-kept, own DID, pinned transport manifest; JB's consent bundle in becky's ledger; ring door enforcing laws 3–6; sends on the record · **LANDED 2026-08-02**: `orreth_sim/bell.py` (laws 2–6 executable, 8 stories, suite 291) + the wire (BELL seeded, SES manifest pinned, `ring_bell`/`bell_beat`, cooldown book on the ledger-seeds pattern, the grant riding 0034's own consent gate with a `bell` marker) · **PROVEN LIVE, BOTH FACES**: a consent-less ring carrying a smuggled instruction got the one face and SES never stirred; then JB's click opened the grant and THE FIRST RING LANDED IN HIS INBOX — from bell@jsbarth.com, subject req-403 (a real death, 2.6h old), carrying kind·scope·subject·age·pointer and not one word more; ring + delivery records on the shelf, consent head granted, bell.json holding the cooldown | a synthetic ring reaches JB's endpoint carrying nothing but scope · kind · age · pointer; a ring without consent refuses with the one face — ✓ RAN, JB's inbox the witness |
| 3 | **The subscribers** — gate-age rider on the worker's beat; the standing verify beat built (0042's deferral) with `tamper` ringing on a real swapped deed · **LANDED 2026-08-02**: `verify_beat` (observation-only, no word asked just to LOOK — every standing deed fetched back against its sworn attempt key, the observation landing either way; a wrong world stages the walk-back AND rings) + `gate_age_beat` (the OLDEST over-threshold card on ANY floor, one ring, daily cap — the pointer leads to the queue; law 6 by design) · **PROVEN LIVE**: the outside hand swapped first-deed.json on the open web → the beat caught it inside its window ("observed found [7da99904…]"), the walk-back staged (req-407), the tamper ring reached JB's inbox, the true bytes restored; then gate-age rang for req-16 at f:prod — a gate 22 DAYS old, the rig's oldest waiting consequence, rung once | the first-deed swap replayed: nobody at the glass, the bell says the deed fails verify — ✓ RAN, all three kinds now in JB's inbox |
| 4 | **The whole** — witness → ring end-to-end with the Console closed; cooldown proven (a second kill inside the window rings once); the room's header shows the bell's own state (rung · resting · refused) — the Observatory watches the bell too · **LANDED 2026-08-02, THE DIVE CLOSES WHOLE**: the risen worker RINGS the death it could not ring while dead (once per rise, subject = the floor so law 6 bites across episodes) · the room's payload + header carry the bell's state, and an aged repeat now outlives the process · **PROVEN BY TWO DEATHS**: killed 23:17:30Z, Console closed → the witness spoke at 23:18:59Z (89s) → the rise rang JB's inbox (sha256:2dd5bc6b…); killed again 23:19:04Z inside the window → the witness spoke, the rise attempted the ring, and THE BELL HELD — "aged into the standing ring (+1), the wire stays quiet." Two deaths, one email. Era → 0.44 | JB receives one real message on a walk he didn't have the glass open for — ✓ RAN: one email for two deaths, the law the proof |

## 5. The locks (JB, 2026-08-02 — all three on the recommended path)

- **L-A · transport v1 = email via SES** (orreth.ai — allen's country):
  true out-of-band; no third party beyond AWS learns a ring happened. The
  pinned manifest stays pluggable for later channels.
- **L-B · the verify-beat FOLDS IN**: sp3 builds 0042's deferred standing
  verify beat, and `tamper` is its voice — a swapped deed on the open web
  rings a human nobody's glass would have told. The 0042 deferral clears
  in this dive.
- **L-C · witness threshold = 3 missed beats (≈ 90s)**; the env may
  lengthen it, never silence it.

## 6. Gap register (§11 law, standing)

*found → written → homed.*

| # | Gap | Why it matters | Home |
|---|---|---|---|
| B1 | **The witness watched every floor but the pulse touched one.** Every floor's daemon runs the watch (one binary); sp1's pulse reached only the universe — 19 honest obituaries staged for a worker that lived | a witness that cries wolf teaches the human to ignore the bell (law 6's spirit) | ✓ **CLOSED sp3, same sitting**: the pulse touches EVERY tended door each pass; the 18 stale cards settled with the truth named ("a wiring gap, not a death"), their transcriptions kept |
| B2 | **The first gate-age read one queue.** The rig's aged consequence lives on the floors (the 22-day purge at f:prod); the universe's own queue is young | the bell must agree with the room's gate-wait panel — rule 7, one picture | ✓ **CLOSED sp3, same sitting**: the rider sweeps every tended floor, subject carries the place ("req-16 at u:demo/e:cloud/f:prod") |
| B3 | **The bell rides the worker.** The witness's finding exists without any reader (the daemon's book, pg-held) — but the RING waits for a resurrection, because keys and transport live worker-side by design (0016's separation). A universe that never rises again is silent beyond the glass | the dead-man's dead-man | **OPEN, boundary NAMED** (guide 06 §7): the absence of expected rings is the residual signal. Home: a fully external watcher (or daemon-side minimal transport) rides the multiverse/ops era — it touches key custody, not just plumbing |
