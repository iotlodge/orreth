# The Attachment Thesis
### The industry manages context. Orreth raises lives.

*Private vision artifact. Captured 2026-07-03 from JB's articulation, mid-build, the day trust-root
pinning landed: "The life lives forever, and every time you start the agent it is, in essence,
joining its digital life." Companion to `FUTURE-the-orreth.md` and `the-spacetime-window.md`.*

---

## The reframe

Today's industry answer to long-running agents is **context management**: compaction windows,
summarization chains, session handoffs, RAG bolted to the side of a process. All of it shares one
assumption — **the agent IS the process.** When the window fills or the process dies, heroics begin,
and every heroic is lossy, ungoverned, and invisible to audit.

Orreth inverts the assumption. **The life is the primitive; the process is an attachment** (`0002 §1`).
Memory keys to the identity, never to the runtime. Starting an agent is not booting software —
it is a life *waking up*: reconnecting to everything it has ever done, everything it is entitled
to know, and nothing it isn't.

> Reboot ≠ death. The thread survives the needle.

## Why this dissolves the long-running-agent problem instead of managing it

- **"Context management" becomes a retrieval policy, not a survival strategy.** What an agent
  "remembers" at any moment is a governed, time-budgeted, Sourced + Verified query (`0002 §3`)
  against a memory that never fades — recent and cheap nearby, deep and honest above. The
  metabolism (`0003`) does what compaction pretends to: distills with provenance, under policy,
  with the loss *measured*.
- **The concern about long-running agents is answered structurally, not managed.** What has it
  seen? — Sourced + Verified, every atom. What rules was it under when it acted? — pinned on every
  run (`context_hash`, `0007`). Who's watching it? — vigil, from birth (`0013`). Where did it come
  from? — a **birth certificate** (`0011`): archetype, generation, skills at stamp, probation term.
  What if it must forget? — provable, physical erasure (`0002 §6`; the store deletes the bytes,
  the signed stub remains). The industry's anxiety inventory becomes a features list.
- **"If authorized, much much more."** A life's reach is a capability token chained to a pinned
  root (`0006`) — its access to deeper memory, other lives, other worlds is a grant, not a hope.
  Foreign roots mint nothing.
- **And the world is a primitive too.** A universe carries its own clock (`0004`): lives can be
  lived at simulation speed — decades of biography in weeks — with the window (`0008`) able to
  occupy any moment of it. Not just digital lives: digital *histories*.

## The demo that says it all

Process one writes a life's first memories through the plane and exits. Process two — later,
elsewhere, sharing nothing but the identity's key — attaches and asks *"what do I remember?"*
Everything comes back, verified against its own content addresses. The process died; the life
didn't notice. (`backend/conformance/demo_digital_life.py` — runnable today against `orrethd`.)

---

*The pitch in one breath: everyone else is trying to keep a process alive long enough to matter.
Orreth lets it die — because the life was never in the process.* 🥃
