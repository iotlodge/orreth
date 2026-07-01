# Orreth

**A security-first, identity-anchored memory across spacetime — Universes of Ecosystems of Fields of Agents.**

An agent today is only as good as its data, and its data is bounded by time. Orreth uses the running
universe as **memory that never fades** (configurable for years) and is **not lonely** (collective,
cross-agent, authorized). **Governance is its first application, not its purpose.**

> Three flows: **policy cascades down** (foundational, non-overridable) · **memory rises up** (pruned at
> every layer) · **retrieval escalates up by time-horizon** (Sourced + Verified). Identity is the immortal
> thread; the Universe is both the **foundation** (policy) and the **apex** (all-time memory).
> *Security first. Trust, but verify — at ecosystem scale.*

---

## Status

🟢 **Design decisions complete · the simulator runs.** The keystone specs are decision-complete (ledger
clean — see `docs/decisions/`). `contracts/v0/` holds ten validated JSON Schemas, and `backend/conformance/`
runs the **Python reference simulator**: all three flows end-to-end, 10 passing tests — policy cascades and
cannot be loosened, memory rises pruned with provenance intact, retrieval escalates by time-horizon with
uniform refusals and real Ed25519 throughout. Next: the `0008` pane/GraphSpec dive (design track) and EH
conformance extraction → the Rust plane (build track).

The brand name **Orreth** is locked. **`orreth.ai` was registered 2026-07-01 (AWS Route 53, confirmed)** —
the did:web trust root (`design/0006`) now has a real anchor. Still open: a trademark glance, and
`orreth.com` as an optional defensive registration.

**Path to build (roadmap owner: Fable · 2026-07-01).** The decision-heavy design work is **done** —
0000/0001/0002/0003/0006 are decision-complete and the ledger is clean. Before first code (2–3 sessions):
`0002` amendments → `contracts/` v0 (JSON Schema, extracted from the blessed specs) → minimal `0004`
(Tier Profile dials, already decided). **First code = the Python simulator** — the three flows end-to-end
on one compose stack (2–3 sessions). In parallel on the design track: `0008` (Field commander pane +
GraphSpec) with the spacetime-window concept. Rust begins once the sim proves the contracts and the EH
conformance fixtures are extracted; remaining dives interleave with the build.

**orreth.ai milestones — when something must actually be live on the domain:**
1. **Now → simulator: nothing.** Contract `$id`s are namespaced URIs resolved locally; the sim uses pinned
   trust roots. The domain just needs to stay registered.
2. **Rust plane / 0006 implementation: static `/.well-known/` hosting** — the first real did:web root
   resolution needs `https://orreth.ai/.well-known/…/did.json` served (S3+CloudFront-grade static, minutes
   of infra). *This is the first hard requirement.*
3. **"Build My First Universe" (0009): the real site** — provisioning, marketplace, interviews.

---

## The center, and the mechanism

**The center — what Orreth *is*.** A memory substrate for **Living Identities**. An agent's process is
ephemeral (online / offline / reboot); its **identity is the immortal thread**, universe-unique, and
**memory is keyed to the identity, not the process.** Reboot is not death. Governance (drift → tune) is
the *first application* the substrate powers, not the point.

**The mechanism — how it's built.** One recursive primitive — the **Harness** — with `tier` as a property
(a **Tier Profile**), not three codebases. Children are Harnesses until the leaf **Field**, whose children
are living **Agents**.

- **Multiverse is free** — a Harness above Universes is just another Harness.
- **A 2-tier customer is free** — "just an Ecosystem with Fields" is a depth-2 tree.
- Depth is **capped at 3** (Universe / Ecosystem / Field) until we prove it out; expandable by design.

> Harnesses all the way down, until agents. The only special node is the Field — where governance meets a life.

---

## The lineage — three projects, one fabric

| Layer | Project | Where it lives | Role |
|---|---|---|---|
| **Universe** (apex + recursive runtime) | **Orreth** | this repo | the recursive Harness runtime; tier = a profile |
| **Ecosystem** | **ecosystem.harness** (EH) | `../ecosystem.harness` | the governance loop, proven (61 tests, end-to-end). Its engine **lifts** into Orreth as the node core. |
| **Field** | **native Orreth** *(reference proof: CortexObserver)* | `../CortexObserver/CortexObserver` (reference) | the leaf Harness where agents live — designed fresh for Orreth. CO proved the pattern (commander, roster, farms, skills, memory) and informs interoperability; it does **not** drive the design |
| **Agents** | LangGraph · AgentField | (in each Field) | the workforce; DID-identified via becky → NANDA; built or leased |

---

## Repo map — so you never chase a file

```
orreth/
├── README.md                 ← you are here
├── docs/
│   ├── vision/                ← the north stars (private vision artifacts + hero mockups)
│   │   ├── FUTURE-the-orreth.md                    ← the canonical Orreth spec (memory-first)
│   │   ├── Orreth-spacetime-memory.(png|svg)       ← the hero: the memory pyramid
│   │   ├── use-cases.md                            ← the same machine, different costumes + "Build My First Universe"
│   │   ├── the-spacetime-window.md                 ← the apex payoff at its limit: a live cross-section of a world
│   │   ├── governed-human-oversight.md             ← humans as governed principals: scoped, directional, audited access
│   │   ├── Orreth-mockup.(png|svg)                 ← the orrery (pre-rebaseline · superseded by Orreth-agentic-hierarchy)
│   │   ├── Orreth-agentic-hierarchy.(png|svg)      ← the staffing view: agents run every layer; humans at the gates
│   │   ├── Orreth-spacetime-window-concept.(png|svg) ← the north star: the block, the hypersurface at T, the cut
│   │   ├── FUTURE-the-conductor-and-the-field.md   ← the EH-tier vision (+ image)
│   │   └── EH-FRONTEND-the-cross-field-pane.md     ← the EH single-pane sketch (+ image)
│   ├── design/                ← build-phase design specs (the keystone dives)
│   │   ├── README.md          ← the dive sequence + index
│   │   ├── 0001-promoted-memory-and-skill-standard.md
│   │   └── 0002-living-identity-and-retrieval.md   ← the substrate keystone
│   ├── decisions/             ← locked decisions / ADRs (made + to-be-made)
│   │   └── README.md
│   └── articles/              ← public thought-leadership pieces (LinkedIn)
│       └── 01-the-amnesiac-genius.md
└── (backend/ · frontend/ · infrastructure/  — reserved; added when we start building,
    mirroring ecosystem.harness's spec §9 layout)
```

**Start here:** `docs/vision/FUTURE-the-orreth.md` is the full vision. `docs/design/` is where
the vision becomes buildable, one schema at a time.

---

## Principles

- **Security first. Trust, but verify — foundationally, from the Universe down.** Universal policy is non-overridable; **retrieval is the #1 security surface.**
- **Identity is the thread; memory is the life.** The process is disposable; the identity and its memory are not.
- **The layers prune so the Universe holds only what matters.** Compression is the shape of the pyramid.
- **Skills are crystallized memory** — learn once, stop re-remembering.
- **Retrieval spans spacetime — Sourced and Verified, or not at all.**
- **Humans conduct; agents perform — and now, agents remember forever.**

---

*JB owns the vision. Claude owns the code and usability. We move at the speed of the ideas.* 🥃
