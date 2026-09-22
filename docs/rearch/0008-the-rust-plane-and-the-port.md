# 0008 — The Rust Plane and the Port

**Status: LOCKED 2026-09-21 (JB's lock, three calls in one sitting).** This
document decides the one thing the locked canon 0001–0005 never said aloud:
**what language the kernel is written in, and when.**

## Why this document exists

JB's direction on 2026-09-14 named Rust first among what survives the
rearchitecture. His original call in design 0000 §3 was *"Rust where we
can"*, with a sequence: contracts → a Python simulator that validates the
design cheap → the Rust plane built once, properly, against a
language-neutral conformance suite. 0000's own words: *never pretend a
Python engine became a Rust plane by wishing.*

The rearch canon 0001–0005 chose transport, memory, agents and experience.
It chose no language. Fable built the spine in Python at Phase 1 without
putting the kernel's language in front of JB, then wrote "not a single
binary; not Rust" into 0007 and the capture as an honest-register boundary.
JB read it as an architecture flip he never agreed to. He was right to:
a kernel's language is his call, and it was made by default and footnoted.
This document puts it right, in the open, as canon.

## The decision

| Body | Language | Why |
|---|---|---|
| **The kernel** — the spine's rails (outbox · inbox · invoke · events · intent), the envelope, markers, projections, the doors, the Bridge feed, the scheduler, the harness, presence and leases, the ground | **Rust — `orrethd`** | deterministic, hot-path, security-critical; one binary to deploy and govern; JB's standing call |
| **The residents' bodies** — the LangGraph template, covenant-as-policy, tools | **Python / LangGraph** | JB's 2026-09-14 lock; cognition is model-shaped and iterates fast; the kernel spawns and governs them as processes |
| **The glass** — the Bridge's page | **HTML / JS, served by the kernel** | one page, no build step, embedded in the binary |
| **The SDK** | Python first, TypeScript next | "continue SDK for sure" — the seams are the doors, language-neutral |

**The honest end shape:** one Rust kernel that governs; residents as
processes it spawns. *Single binary* is true of the kernel. A resident's
brain is a LangGraph process the kernel starts, meters, and stops — and
that is the right shape, not a compromise: the trust plane never runs a
prompt in its own address space (0016's law: the plane authorizes and
meters; it never sees the prompt).

## The sequence — by phase, not by wish

- **Phase 6 — GOVERNANCE FELT — builds in Python.** The Python spine is the
  simulator stage of JB's sequence: it validates the laws cheap, in front
  of JB, in the glass. Nothing about P6 is language-shaped.
- **Phase 7 — SCALE & SEAL — IS the port.** `orrethd` grows the spine's
  modules one by one against the conformance suite (below); the Python
  spine retires to reference implementation and simulator, alive for the
  fixtures; the release wave that replaces main ships the Rust kernel.
  P7's scale work (cells, partition, isolation, hardening) lands IN the
  Rust kernel — it is built once, properly.
- **Between now and P7, the conformance suite grows with every spoonful.**
  This is the law that makes the port a measured walk instead of a big
  bang.

## The conformance-suite law

1. **Fixtures are language-neutral files** under `spine/conformance/`:
   `<contract>-v<N>.json`, each a list of cases — *given this input, expect
   these bytes / this hash / this refusal by name*. No code in a fixture.
2. **The Python spine is the reference that generates and must pass them.**
   `spine/tests/test_conformance.py` runs every fixture against the
   Python modules on every CI run. A fixture the reference fails is a
   fixture bug or a wound — never silently regenerated.
3. **Every spoonful that changes a wire contract adds or extends a
   fixture** in the same change (the envelope, a rail's message types, a
   marker's shape, a projection's read, a door's response shape). The
   close checklist asks for it by name.
4. **A module is "ported" only when `orrethd` passes its fixtures** — the
   same files, unchanged. Until then the word is not used (0000 §3: the
   Rust plane must pass the suite before it earns the word "lifted").
5. **The Rust plane stays sacred** (covenant rule 9): every change under
   `backend/plane/` in P7 carries JB's explicit approval for that change.
   This document is JB's approval of the LINE, not of any change in it.

**The first fixture — `envelope-v0.json`, 2026-09-21:** canonical bytes
and content hashes of the transport envelope (`orreth.transport/1`), a
fixed envelope's byte form round-tripped, and the refusals by name — the
contract every rail already rides. The existing 4,966 lines of Rust in
`backend/plane/crates` (crypto · rollup · resolver · node · store ·
`orrethd`) are the seed the port grows from; its canonicalization already
matches the Python reference by the serde_json BTreeMap rule.

**The Rust runner — P7 sp1, 2026-09-22:** `orreth-spine` is born
(`backend/plane/crates/orreth-spine`) with `tests/conformance.rs`, which
reads every fixture file and dispatches by kind — at sp1 it reports
**ported 105/105 cases, all 25 kinds, not yet ported: none**; the crate's
canonical form is byte-identical to Python on every case, the `\uXXXX`
escaper and the float `repr` written by hand rather than trusted to serde.

## What this document binds

The kernel is Rust by Phase 7; the bodies are LangGraph processes it
spawns; the glass is one page it serves. The Python spine is the simulator
of JB's own sequence, never the destination. The register says "not yet"
and names the phase; it never says "not". The conformance suite grows from
this day, one fixture per wire change, and the port is measured against
it — module by module, in the open, on JB's per-change word.
