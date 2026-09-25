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
- **P7 sp2 (2026-09-22) — the first SHADOW:** the Rust ground and rails
  (`orreth-spine`, feature `rails`) stood on the PUBLIC dev ground beside the
  Python spine — same tables, same advisory lock — and a fact each spine
  committed was relayed, read and absorbed by the OTHER (Rust → Python relay
  + projector; Python → Rust relay + reader + inbox, in sequence): two
  spines, one ground, one truth. The rail tests run by name with the rig up
  and skip BY NAME without it (`tests/rails.rs`); `rails-v0.json` measures
  the names and shapes both spines share.
- **P7 sp3 (2026-09-22) — the ask road in SHADOW:** the Rust bridge
  (`spine-bridge`, feature `bridge`, :4601) serves the SAME glass page and
  the ask road's doors beside the Python Bridge on :4600; one ground, one
  truth — an ask through the Rust door, dispatched by the Rust dispatcher
  (the inbox footprint hands each fact to exactly one), served by the Python
  librarian, read equal at both doors; `askroad-v0.json` + `ladder_step` ·
  `manifest_pin` bring the Rust runner to 157/157, not yet ported: none.
- **P7 sp4 (2026-09-23) — the loops in SHADOW, and THE BEAT LOCK:** the
  Rust bridge beats beside the Python Bridge — the scheduler's tick, the
  intent rail's turn (watches judged, the red observed, the planner asked,
  the objective filed, runners heard), the stop and its reverse settled by
  the Rust kernel on the proof. Two kernels on one ground taught the port
  its second shadow law (the first was the inbox footprint for dispatch): a
  BEAT is claimed on the ground before it runs — `pg_try_advisory_lock(742200
  + class, hashtext(scope))`, per world, per class — so one world is never
  ticked or turned twice at once; the kernel that finds the beat held steps
  back and says so. The law is written in BOTH spines (the Python reference
  gained `ground.beat`) and measured by `loops-v0.json` (`beat_lock`); the
  five mcp kinds are ported; the runner reads 195/195 across 49 kinds, not
  yet ported: none. What a kernel without bodies cannot run it LEAVES DUE
  (the harness's mind-run), never claims and drops.
- **P7 sp6 (2026-09-24) — THE BODIES' SEAM, the end shape reached:** the
  Rust kernel SPAWNS the crew — every seat of `spine/crew.v0.json` its own
  Python process, `python -m orreth_spine.body` (the SDK-side body) — and
  GOVERNS it: a body that dies is restarted after a backoff, one that dies
  three times in five minutes is PARKED as a fact with its last words and
  restarted only on the human's word, a refusal at birth is never restarted,
  and at dark every body is stopped whole. The kernel never runs a prompt in
  its own address space (0016): the one thought it asks is the canary's
  one-token ping, metered; the harness's run rides the invoke rail to the
  body and lands under the kernel's run id. The Stable's and the shelf's
  registries, the held acts, both keepers' beats and the nine health checks
  are the Rust kernel's too. `bodies-v0.json` measures the park law and the
  harness's command; minds-v0's twelve are ported; the runner reads 328/328
  across 78 kinds, not yet ported: none. Standing alone, the Rust kernel is
  whole but for the built-in tools' door (their schemas live in `tools.py` —
  the boot rite runs as a Python one-shot until sp8 moves the door).

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
