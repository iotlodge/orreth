# 0044 — The Bell

*Drafted 2026-08-02 · Fable 5 with JB · status: BLESSED — three locks taken,
build next*

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
| 1 | **The witness** — the daemon tracks the worker's last touch (the beats it already receives); silence past threshold → the signed silence record + a `witness` ring staged. Threshold declared, env-defaulted, visible in the room | kill the worker with the Console CLOSED; the silence record exists before any glass opens |
| 2 | **The bell service** — farm-kept, own DID, pinned transport manifest; JB's consent bundle in becky's ledger; ring door enforcing laws 3–6; sends on the record | a synthetic ring reaches JB's endpoint carrying nothing but scope · kind · age · pointer; a ring without consent refuses with the one face |
| 3 | **The subscribers** — gate-age rider on the worker's beat; the standing verify beat built (0042's deferral) with `tamper` ringing on a real swapped deed | the first-deed swap replayed: nobody at the glass, the bell says "a deed at u:demo fails verify — the Console has the card" |
| 4 | **The whole** — witness → ring end-to-end with the Console closed; cooldown proven (a second kill inside the window rings once); the room's header shows the bell's own state (rung · resting · refused) — the Observatory watches the bell too | JB receives one real message on a walk he didn't have the glass open for |

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

*found → written → homed.* Empty at design time — the build will fill it.
