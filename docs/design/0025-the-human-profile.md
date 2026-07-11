# 0025 — The Human Profile (the second brain's heart)

*Design draft — proposed by Fable 5 (design owner), from the Universe-Brain session
(2026-07-10, `../vision/the-universe-brain.md` §5, R4). Pre-locked there: the profile
is co-authored by the Human and the Librarian; the human may update it but the
Librarian maintains it as events occur; every claim carries provenance; the human
corrects and withdraws — always THROUGH the Librarian. Builds on 0023 (her seats and
her parlor), 0024 (the markers that feed inference), 0002 §2/§6 (personal-data class,
consent, tombstone), and 0014 (the trust ladder, now applied to beliefs about you).*

---

## Why this is a keystone

JB: *"the Universe should maintain LIVE PROFILES… both the Human and Librarian work to
create a detailed profile of the Human as time progresses, to ensure that Universe
always understands and can personalize the experience."* This is the second-brain use
case's heart — and the most intimate record class the substrate will ever hold. Its
constitution must be exactly right: provenance on every claim, the subject's authority
over assertions about themselves, inference on probation, and a working right to be
forgotten from day one.

---

## 1. The profile — a Knowledge Category about the human

- **One profile per creator**, keyed to the human's identity; record class
  **`personal-data`** (0004 retention min/max; consent facets live, 0002 §2).
- **A claim is a record** (`kind: semantic`, tags `["profile", "creator"]`), body:

```
profile {
  claim         : string                  # the belief about the human
  asserted_by   : "human" | "librarian"   # provenance — who says so
  quoted?       : string                  # the human's words, when the human asserted
  inferred_from?: ContentHash             # the evidence, when the Librarian inferred
  state         : "trusted" | "untrusted" # the ladder (§2)
}
```

## 2. Provenance and the ladder (R4, mechanized)

- **Human-asserted claims enter `trusted`** — the subject is the sovereign authority
  on their own preferences. They arrive only as parlor asks (`my profile: …`), quoted,
  landed by the Librarian's seat — the no-direct-input law holds even here.
- **Librarian-inferred claims enter `untrusted`** — rookie probation applied to
  *beliefs about you*. v1's inference is deterministic and honest: a `major` or
  `substantial` life-event marker (0024 §4) yields an observation deriving from that
  marker. Corroboration through further observation promotes on the 0014 ladder;
  synthesis-grade inference waits for the governed mind.
- **Reads label provenance**: "you told me …" vs "I observed …" — the human always
  sees which claims are theirs and which are the Librarian's beliefs.

## 3. Correct and forget — always through the Librarian

- **Correct by superseding**: a new assertion outranks; history stays (append-only).
- **Withdraw by consent** (`forget about me: <topic>`): a **withdrawal record**
  derives from each matching claim — the lineage-death pattern (0023's recalled
  semantics, reused): a withdrawn claim, and every version of it, never answers
  again. **Physical erasure of the bytes rides the Purge dive (crypto-shred, 0022
  §6)** — the right to be forgotten works at the annotate level today and at the
  physics level with spoonful 5. The withdrawal itself is on the record: *that* you
  chose to forget is never lost; *what* was forgotten stops speaking.

## 4. The personalization surface

- `what do you know about me?` — the Librarian composes the live profile: human
  assertions first, then her observations, provenance labeled, citations riding
  (0023's faithfulness gate).
- The parlor facts gain a `profile` slice so **every resident's** replies may
  personalize (v1 wires the surface; residents adopt it as their dives mature).

## 5. Mechanism — what this dive lands

1. **Reference (sim)**: `profile.py` — ask parsing (assert · read · forget), claim
   bodies with provenance→state, withdrawal-death (`withdrawn_refs`) — tested.
2. **Wire (worker)**: the three parlor routes on the Librarian · assertions derive
   from their audience record · inference from major/substantial remember-markers ·
   the composed profile read with provenance labels + refs · withdrawal versions.
3. **Deferred to the ledger**: physical erasure via crypto-shred (spoonful 5) ·
   topic-level supersession dedup (needs the meaning axis, 0022 Phase 2) · governed
   LLM inference (the psychologist skill, behind the model plane) · per-resident
   personalization adoption.

## 6. Decisions

**Pre-locked by JB (2026-07-10):** co-authored live profile · human updates through
the Librarian, Librarian maintains as events occur · provenance per claim · consent
withdrawal honored (R4).

**Closed by the design owner (JB may veto):** human assertions enter `trusted`
(self-sovereignty), inferences `untrusted` (probation) · v1 inference =
major/substantial markers only, deterministic · withdrawal = lineage-death now,
crypto-shred at the Purge · reads label provenance in plain words.

---

*The universe keeps a living portrait: the strokes you paint enter sovereign, the
strokes it paints enter humble, every stroke signed — and any stroke you disown goes
silent forever, on the record.* 🥂
