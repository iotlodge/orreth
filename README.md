# Orreth

**A governed model of nested worlds — Universes of Ecosystems of Fields of Agents.**

An *orrery* is a clockwork model of a planetary system: nested worlds turning in governed,
predictable orbits, observed and tuned from outside and above. **Orreth** is that, for agents.

> Analysis rolls **up** (agent → field → ecosystem → universe). Standards cascade **down**
> (universe → ecosystem → field → agent). Humans conduct; agents perform.
> *Security first. Trust, but verify — at ecosystem scale.*

---

## Status

🟣 **Design phase.** No application code yet — this is deliberate. We are designing a
*lightweight architecture that can be expanded* before we build. The vision is captured; the
build-phase design specs are being written one keystone at a time (see `docs/design/`).

The brand name **Orreth** is locked. The domain (`orreth.ai` / `.com`) showed no DNS delegation at
capture time but is **not yet purchased** — confirm at a registrar + a trademark glance before spending.

---

## The one idea

Don't build three tiers as three codebases. Build **one recursive primitive — the Harness — and
make `tier` a property.** Its children are other Harnesses, until the leaf **Field**, whose children
are **Agents**. The same governance loop runs at every tier, parameterized by a **Tier Profile**.

- **Multiverse is free** — a Harness above Universes is just another Harness.
- **A 2-tier customer is free** — "just an Ecosystem with Fields" is a depth-2 tree.
- Depth is **capped at 3** (Universe / Ecosystem / Field) until we prove it out; expandable by design.

> Harnesses all the way down, until agents. The only special node is the Field.

---

## The lineage — three projects, one fabric

| Layer | Project | Where it lives | Role |
|---|---|---|---|
| **Universe** (apex + recursive runtime) | **Orreth** | this repo | the recursive Harness runtime; tier = a profile |
| **Ecosystem** | **ecosystem.harness** (EH) | `../ecosystem.harness` | the governance loop, proven (61 tests, end-to-end). Its engine **lifts** into Orreth as the node core. |
| **Field** | **CortexObserver** | `../CortexObserver/CortexObserver` | a full CortexObserver per line-of-business — commander, roster, farms, skills, memory |
| **Agents** | LangGraph · AgentField | (in each Field) | the workforce; DID-identified via becky → NANDA; built or leased |

---

## Repo map — so you never chase a file

```
orreth/
├── README.md                 ← you are here
├── docs/
│   ├── vision/                ← the north stars (private vision artifacts + hero mockups)
│   │   ├── FUTURE-the-orreth.md                    ← the canonical Orreth spec
│   │   ├── Orreth-mockup.(png|svg)                 ← the Orreth hero image
│   │   ├── FUTURE-the-conductor-and-the-field.md   ← the EH-tier vision (+ image)
│   │   └── EH-FRONTEND-the-cross-field-pane.md     ← the EH single-pane sketch (+ image)
│   ├── design/                ← build-phase design specs (the keystone dives)
│   │   ├── README.md          ← the dive sequence + index
│   │   └── 0001-promoted-memory-and-skill-standard.md
│   └── decisions/             ← locked decisions / ADRs
│       └── README.md
└── (backend/ · frontend/ · infrastructure/  — reserved; added when we start building,
    mirroring ecosystem.harness's spec §9 layout)
```

**Start here:** `docs/vision/FUTURE-the-orreth.md` is the full vision. `docs/design/` is where
the vision becomes buildable, one schema at a time.

---

## Principles

- **Security first. Trust, but verify — recursively.** DID-signed, capability-scoped, tenant-isolated at every tier.
- **Tuning is governance, and it's pulled, not pushed.** A tier pulls a signed Standard and verifies it before applying.
- **Bound outcomes, not paths.** Conform the result; never constrain the reasoning.
- **Skills are governed memories.** One substrate for reproducibility and remembering.
- **Humans conduct; agents perform.** A hand on the wheel even when no human could watch every world.

---

*JB owns the vision. Claude owns the code and usability. We move at the speed of the ideas.* 🥃
