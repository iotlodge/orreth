# 0026 — The Purge (the poison protocol)

*Design draft — proposed by Fable 5 (design owner), from the Universe-Brain session
(2026-07-10, `../vision/the-universe-brain.md` §11; JB locks R9–R11 + the split
model). The reconnaissance finding that shapes this dive: **the destruction engine
already lives in the sacred core, complete and uncalled** — `Universe::tombstone`
strips body and pointer from the stub, physically deletes the bytes, and the purged
set hides the record from retrieval while distillations over purged sources already
label `distilled-raw-expired`. This dive builds the GOVERNANCE around it: the doors,
the quorum, the seal, the walk, and the immunity. The core is not touched.*

---

## Why this is a keystone

JB: *"Humans — through Librarian + Warden — must be able to PURGE a poison (bad)
memory which could, in theory, corrupt the whole Universe. BAD BAD."* And the locked
split model: personal-data purge rides consent, solo-capable; operational poison purge
takes two humans and a cooling-off, bars absolute — a solo universe can contain
forever but destroy only when quorum exists. Destruction is the gravest act an
append-only universe can perform; every path to it must be a gate, and every gate
must be on the record.

---

## 1. The engine (already built, now doored)

- **`/tombstone`** (the plane, orrethd): token-guarded — a becky-chained capability
  verified against the pinned root, or the uniform refusal. Strips the stub, deletes
  the bytes, adds to the purged set, **persists the purge** (a `purged` table +
  boot-restore — a restart must never resurrect readability), and write-updates the
  stub row (the pg record drops `body`/`body_ref` too).
- **The stub survives** (0002 §6): *that* it existed, *who* signed it, *when*, and
  that it was purged — forever. Provably retired, never silently lost.
- **Projection eviction** (0022 §6's hard rule): today's projections are the pg row
  (stripped) and the presence memo (epoch-bumped); the vector index joins the eviction
  list the day embeddings land — the rule is stated here so it cannot be forgotten.

## 2. The split model on the wire (JB lock)

- **The consent path — solo, personal-data**: `forget about me:` (0025) gains its
  physical step. After the withdrawal silences a claim, the worker tombstones it —
  the subject's own consent IS the quorum for their own data. Lineage-death at the
  read, physics at the store, the stub and the withdrawal on the record.
- **The operational path — humans, plural**: a `purge` request (kind `purge`, naming
  refs or a source) **stages and holds**. Bars are absolute (0012 §5): below two
  control-entitled humans the resolution states it plainly — *"held: quorum 1 of 2 —
  containment active; destruction waits for humans, plural"* — and nothing executes.
  With quorum (future signer registry), approval starts the cooling-off
  (approved-but-held; one voice aborts), then the walk executes through the same
  `/tombstone` door.

## 3. The seal — containment at machine speed

Staging an operational purge immediately writes **seal records** (tags
`["seal", "purge"]`, deriving from the sealed refs, resident-signed). The cognition
layer's read paths exclude sealed refs exactly as they exclude the recalled and the
withdrawn — lineage-death, third use. Detection fast, destruction slow: the poison
stops answering the moment a purge stages, however long the humans take. *(Plane-level
seal enforcement at `/retrieve` rides the ledger — the seal is reversible, so it must
never conflate with the purged set, which is not.)*

## 4. The walk — the blast radius, promotion boundary included

| Crystallized as | Handled by | Status |
|---|---|---|
| Knowledge versions | the recall walk (0014 §4) + its high marker (0024) | live |
| Distillations | core `fidelity`: `distilled-raw-expired` over purged sources | live (core) |
| Profile claims | withdrawal + tombstone (0025 + §2) | this dive |
| Skills | lifecycle `reverted` to last-clean (0001) | ledger — no wire skills yet |

## 5. Immunity — the door remembers the infection

A discredited source's DID (read from the recall records it left behind) is **refused
at gather admission**: the librarian will not admit new knowledge from a source the
universe has recalled — loudly, on the record. The origin signature became a floor at
the door (the-first-questions immune loop, first wire tooth).

## 6. Decisions

**Pre-locked by JB (2026-07-10):** the split model (R9) · the walk crosses the
promotion boundary (R10) · the seal rides as tighten-only containment (R11) ·
crypto-shred as the erasure primitive with mandatory projection eviction (0022 §6 —
today's bodies live solely in the object store, so `delete_body` IS complete erasure;
per-class envelope encryption joins when regulated classes demand it).

**Closed by the design owner (JB may veto):** `/tombstone` guarded by becky-chained
token (the organs-pin guard, reused) · purged set persisted + boot-restored · the
consent path auto-tombstones what the withdrawal silenced · the operational path holds
with the honest quorum message and seals immediately · gather refuses discredited
sources by their recall trail.

---

*Three ways a memory ends: recalled, it stays visible and dead; withdrawn, it goes
silent by consent; purged, its bytes stop existing — and all three leave the same
thing behind: a signed stub that says the universe once knew, and chose, and can
prove both.* 🥂
