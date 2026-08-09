# The Objective Atlas — how the designs interoperate to serve an Objective

<!-- PROVENANCE: Fable 5 (claude-fable-5) — seeded 2026-08-09 at JB's word:
     "going forward I'll be giving you objectives and having something to
     reference that shows how the designs interoperate to support objectives."
     Deliberate shape: ONE standing atlas, not 47 retrofitted graphs — the
     interoperation lives BETWEEN the designs, so it gets one page that stays
     current, the way the-honest-boundary.md keeps the claims. -->

Forty-eight designs, one machine. Each dive doc holds its own organ's law;
this page holds the *wiring* — how those organs pass an Objective hand to
hand, which loops improve the machine between runs, and where in the code a
change lands when a proof says the base must move. Written for the
objective-giving era (JB, 2026-08-09): requests now enter Orreth through its
own doors and are completed by its own loops.

The per-design one-line index stays in [README.md](README.md)'s dive
sequence table — this page never duplicates it.

## 1. The spine — an Objective, end to end

Every ask is a governed request. Four vectors open the door (0047 §5, JB's
own naming); one queue carries everything; the mind reads before the law
disposes; consequence waits for a human; and the learning loops close behind
the resolution.

```mermaid
flowchart TB
  subgraph DOORS["THE FOUR VECTORS (0047 §5) — every ask is a governed request"]
    H["the human, live<br/>0030 the seat · 0020 the parlor"]
    S["the schedule — the machine's duty<br/>0027 standing incarnation · 0047 charter, approved ONCE"]
    T["the trigger — the reflex arc<br/>0047: observe · escalate · act"]
    A["agent-to-agent<br/>0027 dispatch — the queue IS the transport"]
  end
  H & S & T & A --> Q[/"THE REQUEST QUEUE (0012)<br/>tokened · budgeted · human-visible · one-faced refusal (0002 §4)"/]

  Q --> MIND["THE STUDIO (0047)<br/>COMPREHEND → PLAN → GAP<br/>typed at every boundary — a malformed word earns one re-ask, then parks"]
  MIND -.->|"a lack, NAMED"| GAP["THE GAP LOOP (0047 §6)<br/>librarian gathers 0014 → factory builds 0011/0045 →<br/>welcome at the gate 0012 → the shelf"]
  GAP -.->|"the craft waits on the shelf"| MIND

  MIND --> GATE["THE PLAN GATE (0030 · 0012)<br/>the card is the truth the human approves"]
  GATE --> F["THE FINGERTIP (0027)<br/>the ONLY executor — slivers ride the queue, never the whole"]
  F --> FLOORS["THE FLOORS — residents & workforce<br/>0017 flavors · 0023 the librarian · 0037 allen · 0038 the stacks"]
  FLOORS --> RV["REVIEW RIDES ALTITUDE (0027 §6)<br/>critic markers graded into the severity lanes (0024):<br/>low auto-accepts · high waits for the human"]
  RV --> RES["ASSEMBLE → RESOLVE (0030)<br/>the human's request is the ONLY completion confirmation —<br/>no orchestrator confirms itself"]
  RES --> LEARN["LEARN<br/>vera assays off-floor 0043 · the improver proposes 0028/0031 ·<br/>craft rides the lanes 0045 · the epoch names the machine 0041"]
  LEARN -.->|"better craft, next run"| MIND

  PLANE["THE MODEL PLANE (0016 · 0019)<br/>authorize → execute on the caller's own keys → meter<br/>NEVER sees the prompt"]
  FARM["THE TOOL FARM (0018)<br/>hash-pinned service identities — the rug-pull door"]
  MIND -. every thought .- PLANE
  FLOORS -. every thought .- PLANE
  FLOORS -. every tool call .- FARM
```

The states an Objective wears end to end are drawn once, in
[0047 §5](0047-the-universe-learns-to-think.md) (the stateDiagram) — this
atlas points there rather than forking the picture.

## 2. The trust spine — why any of it can be believed

Everything in §1 rides this chain. No organ acts outside it; that is the
whole product.

```mermaid
flowchart LR
  ROOT["the pinned root<br/>did:web (0006)"] --> BECKY["becky — the registrar (0006)<br/>ALONE mints leases"]
  BECKY --> JOIN["the join door (0012)<br/>a governed, human-visible request"]
  JOIN --> SELF["a SELF — an Ed25519 keypair (0002)<br/>survives the process, re-joins as itself;<br/>a new DID per run is a defect"]
  SELF --> CAP["capability tokens (0006)<br/>attenuation-only, chained to the root"]
  CAP --> LAW["the resolved law (0007)<br/>floors tighten-only · content-addressed context —<br/>every run pins the context_hash it ran under"]
  LAW --> ACT["EVERY ACT<br/>authorized · metered under its own DID (0019) ·<br/>scribe-signed, author ≠ agent (0005) —<br/>nothing grades its own yardstick"]
  ACT --> REF["refusal wears ONE face (0002 §4)<br/>authz-miss ≡ budget-miss ≡ missing record —<br/>a prober learns nothing"]
  ACT --> EPOCH["the machine has a NAME (0041)<br/>the CanonEpoch — drift is news,<br/>the revert is a sibling, never a deletion"]
  ACT --> DEED["external consequence (0042)<br/>never complete on the actor's word alone —<br/>effect classes price the ceremony"]
```

## 3. The one truth and its projections

Rule 7 — one world, one picture — is enforced by construction: there is one
signed log, and every view is a rebuildable projection over it. Seven RAG
flavors, the brain, the observatory, the registry: projections, never second
truths. The purge reaches all of them; drop any index and it rebuilds from
the log.

```mermaid
flowchart TB
  ORG["every organ — residents · minds · workers · humans at the glass"] -->|"signed records, canonical bytes (0000 §3) —<br/>lived time monotone (0004), backdating refused"| LOG[("THE ONE SIGNED LOG (0022)<br/>the truth · bi-temporal · content-addressed")]
  LOG --> P1["search & meaning<br/>pgvector + BM25 hybrid, standing-over-relevance (0022 Ph2)"]
  LOG --> P2["the rollup (0005)<br/>standings climb the tree; floors FLAG, never average away"]
  LOG --> P3["the registry & the shelf (0045)<br/>craft as versioned, releasable assets"]
  LOG --> P4["the observatory (0043)<br/>flight series distilling under declared retention, loss MEASURED"]
  LOG --> P5["the glass (0030 · 0036 · 0043)<br/>the seat · the living brain · the instrument room"]
  MET["the metabolism (0003 · 0033)<br/>distills under distortion CONTRACTS —<br/>must_preserve refused-at-save, never silent"] --- LOG
  PURGE["the purge (0026)<br/>crypto-shred + mandatory projection eviction —<br/>a restart never resurrects readability"] --> LOG
```

## 4. The loops — how the machine improves between runs

JB's phrase: *the loops of Orreth*. Five stand today; all converge on one
shelf, and every adoption in every loop waits for a human word — improvement
is proposed, never self-adopted (0031).

```mermaid
flowchart TB
  subgraph L1["the assay loop (0043)"]
    W["completed work"] --> V["vera — ANOTHER floor's mind<br/>signed verdicts · cards never levers ·<br/>her own cost metered under her own DID"]
    V --> ST["standings (0005)"]
  end
  subgraph L2["the craft loop (0028 · 0031 · 0045)"]
    ST --> IMP["the improver reads the receipts<br/>proposes a SIBLING version, evidence cited"]
    IMP --> LANE["the lanes (0024)<br/>a nudge adopts loud · a rewrite waits for the human"]
    LANE --> REL["the Canon release (0041 · 0045)<br/>firmware change = an epoch — the machine is RENAMED"]
  end
  subgraph L3["the gap loop (0047)"]
    RD["the studio reads an Objective"] --> GP["a lack, NAMED unprompted"]
    GP --> COMM["the commission: gather 0014 →<br/>build 0011/0045 → welcome 0012 → serve"]
  end
  subgraph L4["the freshness loop (0014 · 0032)"]
    SUB["the human's standing word —<br/>a subscription staged at the gate"] --> BEAT["the serials desk beat<br/>the DIFFERENCE is the news; a changed claim<br/>drops its old head to investigating"]
  end
  subgraph L5["the knowledge loop (0014)"]
    EXT["the world — sources AS identities"] --> QUAR["admitted QUARANTINED at 0.0000<br/>promoted only on receipts"]
  end
  subgraph L6["the thumb loop (0048 — CLOSED WHOLE 2026-08-09)"]
    THUMB["the human's thumb on every reply & resolved objective<br/>👍 a signed quiet verdict · 👎 + words quoted VERBATIM"] --> RTE["the studio ROUTES the words (typed lane, never guessed):<br/>craft → workshop evidence · gap → commission ·<br/>charter → referral · execution → repair objective<br/>wearing the human's words as its RUBRIC"]
    RTE --> CLOSEC["closure: the outcome named back<br/>on the author's own queue — always a card"]
  end
  THUMB --> V
  RTE --> IMP
  RTE --> COMM
  THUMB -.->|"human vs examiner on the SAME work —<br/>news behind min-n, cards never levers"| V
  REL & COMM & QUAR --> SHELF[("THE SHELF / THE REGISTRY (0045)<br/>craft served by REFERENCE, never copied — law 8")]
  BEAT --> SHELF
  SHELF -->|"the next run finds better hands"| NEXT["the next Objective"]
  HUM["THE HUMAN'S WORD — every loop's gate (0012 · 0030)<br/>improvement proposed, NEVER self-adopted (0031)"]
  HUM -.-> LANE
  HUM -.-> COMM
  HUM -.-> SUB
```

## 5. Where a change lands — the workshop map

For the proving era: when an objective walked through §1 exposes a base gap,
this table says where the change goes and what proves it. (The three latest
standing finds all landed this way: `u_port` in the worker, the unfueled
lease at becky's mint, the poisoned ledger parked at rule 9.)

| The organ | Design(s) | Code home | The proof |
|---|---|---|---|
| the plane — authorize · meter · serve · gates | 0016 · 0019 · 0012 | `backend/plane/crates/orrethd` | plane build + `/health`; **rule 9 guards** `orreth-node` · `orreth-store` · crypto crates · `contracts/v0` — JB's explicit word per change |
| the glass — seat · brain · observatory · parlor | 0030 · 0036 · 0043 · 0020 | `backend/plane/crates/orrethd/src/window.html` (`include_str!` — a glass change requires a **plane rebuild**) | Chrome on the rig, both lights, screenshots |
| the worker — doors · beats · composers · firmware reads | nearly every dive's wire face | `backend/conformance/console_worker.py` | live on the rig (`scripts/dev.sh`; worker doors at :4562) |
| the sim laws — the executable model | every dive | `backend/conformance/orreth_sim/` | `backend/conformance/tests/` — 311 green, **run from `backend/conformance`** (repo root mis-collects) |
| the SDK — chassis · client · the mind's jacket | 0015 · 0017 · 0047 | `agents/orreth-agent-sdk/` | its `tests/` (20) + `test_parity.py` — byte-parity is the contract (0000 §3) |
| the residents & flavors — incl. the studio | 0017 · 0037 · 0038 · 0047 | `agents/flavors/` (the studio: `03-mind/`) | joins at becky's gate as the same self; proves in the parlor/glass |
| floor profiles — tiers as data | 0004 · 0009 | `backend/plane/profiles/` | the shipyard grows them; the orrery shows them |
| the rig itself | — | `scripts/dev.sh` (Docker-first: universe :4500 · eco :4501 · field :4502) | the orrery agrees with the roster agrees with the rollup (rule 7) |

## 6. Maintenance law (STANDING — JB's word, 2026-08-09)

Mirroring the honest-boundary's law: **a dive or a proof that adds an organ,
opens a door, or reroutes the spine updates this atlas in its closing
commit.** An atlas that lags misleads with confidence — worse than no atlas.

JB's blessing carried the why, and it binds the proving era specifically:
*"we do need to be sure to keep these updated as we work the proofs that
will make alterations… nothing works perfectly out the gate; we're in new
industry space, and the reports, views, sustained active state is what does
the verification — outcome focused."* The proofs will move the base; the
atlas moves with them, in the same commit.
