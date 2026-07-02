# 0000 — Structure & Interoperability (the frame the dives hang in)

*Design draft for review — proposed by Fable (design owner). **Open decisions** flagged for JB (vision owner).
This is the meta-spec: how the repos, the runtime, the languages, and the deployments are structured so every
numbered dive lands somewhere real. It also discharges the findings from the 2026-07-01 design review.*

---

## 0. The one-sentence structure

> **Orreth ships as versioned contracts + one thin recursive node (`orrethd`).** UH and EH are the *same node*
> under different Tier Profiles, deployed in layers. EH lifts in as a **conformance suite** (its 61 tests become
> the spec the new plane must pass), the **Field is native Orreth** (CortexObserver is a *reference proof* — it
> may join through an optional adapter, it never drives the design), and cognition stays Python while the plane
> goes Rust.

Lightweight scaffolding means exactly this: we do **not** build three systems and wire them. We define the wire
contracts, build one small node that speaks them, and stack it.

---

## 1. The layering model — one node, three profiles, layered by deployment

Every tier is an instance of the same node kind:

```
orrethd  (one binary / one image)
  ├─ profile: universe    # apex — no parent; no time restriction; universal floors originate here
  ├─ profile: ecosystem   # EH semantics — governance loop, mid-horizon memory, prune & distill
  └─ profile: field       # leaf harness — recent memory; children are living Agents, not Harnesses
```

**The recursion contract.** A node knows three things: its **ScopePath**, its **parent endpoint** (absent = apex),
and its **joined children** (registered through the join flow). That's the whole tree. Depth-cap-3 is a *policy*
asserted at the Universe, not a structural constant — multiverse stays free, and a 2-tier customer is just a
depth-2 tree.

**Layered, not merged.** In dev, all tiers run co-located as separate containers on one machine (one compose file
= one universe). In prod, tiers separate across hosts/accounts with no code change — the same PUSH-up / PULL-down
direction EH proved (a child is never reachable *from* above; parents never poll in).

**The Custodian — the apex above the apex.** When Orreth is *hosted* (orreth.ai), the platform is itself a
Harness one tier above every customer Universe — the **Custodian** (`0013`). Its powers are deliberately
asymmetric: it can freeze (quarantine) and enforce non-overridable platform floors, but is **structurally
blinded to tenant content** (key custody). The safety architecture is Orreth recursed once more onto its own
operator, and governed harder than any tenant. Self-hosted deployments have no Custodian — the operator is it.

**Finding discharged (tier-hardcoding).** All contracts speak **ScopePath-relative** addressing. `0002`'s
`space: "own" | "field" | "ecosystem" | "universe"` amends to:

```
space : "self" | { ancestors: N } | "apex" | { scope: ScopePath }   # relative or explicit — never tier-named
```

The friendly tier names live in Tier Profiles and panes, not in the wire contract.

---

## 2. Node anatomy — what lives inside every Harness

Same organs at every tier; the Tier Profile sets their dials.

| Organ | Role | Plane/Cognition | Notes |
|---|---|---|---|
| **Gateway** | the *only* door — ingress (verify DID/sig/revocation/anti-spoof, ingest) and egress (retrieval authz, budget gating, access records) | Plane (Rust) | This is JB's agentic-gateway pattern made load-bearing: policy enforcement + steward hooks live at the boundary, centrally reusable |
| **Stores** | memory store (append-only, content-addressed) · standards store (versioned) · identity index (DID→key/status) · access-record log | Plane (Rust) | backed by Postgres+pgvector, object store for bodies |
| **Resolver** | composes Resolved Context from the inherited cascade — deterministic, fast | Plane (Rust) | the `0007` dive |
| **Retrieval Router** | serves-what-it-has + delegates the deeper-time remainder up; merge/dedup/ordering of multi-tier results | Plane (Rust) | the `0002` read path |
| **Memory Steward** | ingress cognition (dedup/summarize/distill = pruning execution) + egress cognition (source/verify assembly) | Cognition (Python/LangGraph) | resident, TCB |
| **Pane** | the tier's human window — subtree-down visibility via the same read path | Frontend (Next.js/TS) | §5 |
| **Model Gateway** | the layer's governed door to models — **LiteLLM / OpenRouter** routing, model-tier pinning (enforces `SkillStandard.model_tier`), per-identity token/cost budgets | Plane shell, Python routing | no agent calls a model ungoverned; this is where the cost dial actually turns |

**Every layer is staffed — agents are required inside every tier, not only Fields.** The **resident roster**
(TCB) *runs the layer itself*: the memory steward, the governance agents, the apex analysis agents, the
**Warden** (**vigil** — the security resident; floor **detection & advisory**, content-blind to the platform,
tenant-serving within; **enforcement is a separate HITL-gated control-plane act, never the Warden acting
alone**; `0013`), and **becky, the IAM agent** (resident; becky is an *agent*, not a human): one issuer of DIDs
root→leaf, the agentic half of every promotion gate. The **registered workforce** (LangGraph / AgentField / any SDK) does the domain
labor in Fields. Governance is **bidirectional at every layer**: each Harness governs its subtree down *and* is
governed from above — the same node is conductor to its children and instrument to its parent. Humans appear
only at the gates (HITL), as governed principals — the hierarchy runs entirely agentic.

**Reserved organs — named now, dived later** (we haven't designed these together yet; they get their own numbers
so they don't get lost): **AgentField** (the medium child processes live in and signals travel through),
**Factories** (how agent incarnations are stamped from archetypes — CO's farms generalized), and **HITL strategy**
(where the Governance Gate sits per tier, escalation queues, multi-party co-sign mechanics). Proposed as
`0010`–`0012` (§8).

---

## 3. Language strategy — where Rust, where Python, where TypeScript

JB's call: Rust where we can. My decisioning of *where and when*:

| Component | Language | Why |
|---|---|---|
| `orrethd` plane (gateway, verify, ingest, resolver, router, budget gating) | **Rust** | deterministic, hot-path, security-critical; greenfield so no port debt; this is also where the future brainstem lives — same process, same language |
| Crypto (Ed25519, content-addressing) | **Rust** | replaces EH's HMAC stand-in on day one — we never build the throwaway twice |
| Memory Steward, analysis agents, interview sandbox | **Python / LangGraph** | cognition is model-shaped and iterates fast; uv-managed |
| CO reference adapter *(optional)* | **Python** | lets an existing CortexObserver join as *one kind of* Field — a bridge for the reference proof, never the Field itself |
| Panes (recursive pane, EH cross-field pane) | **TypeScript / Next.js / Tailwind** | per JB's stack, dark+light, lifted from CO's visual language |

**The lift-vs-Rust tension, resolved: lift the contract, port the engine.**
EH does not lift in as *code* — it lifts in as **spec**. Its 61 tests get extracted into a language-neutral
**conformance suite** (fixture files: given these signed records in, expect this drift/attribution/canary/lane
behavior out). The Rust plane must pass the suite before it earns the word "lifted." EH's Python stays alive as
the reference implementation and simulator. This keeps EH's proof, gets Rust where JB wants it, and never
pretends a Python engine became a Rust plane by wishing.

**When Rust starts.** Not first. Sequence: contracts (§4) → Python harness *simulator* (days, validates the
contracts and the layering topology end-to-end) → then `orrethd` in Rust against the conformance suite. We
validate the design cheap, then build the plane once, properly.

---

## 4. Interoperability — the contracts are the product of design phase

A new top-level `contracts/` directory (JSON Schema now; protobuf when the Rust plane lands; semver from v0):

| Contract | What it carries | Source dive |
|---|---|---|
| `MemoryRecord` | the atom — append-only, content-addressed, DID-signed, visibility facets | 0001 + 0002 §2 |
| `Query` / `RetrievalResult` | the read path — ScopePath-relative space × time, budget, Sourced+Verified results | 0002 §3 (amended per §1, §7 here) |
| `SignedRecord` / `SignedBundle` | push-up / pull-down envelopes | lifted from EH |
| `Standard` / `SkillStandard` | the cascade payload | EH + 0001 |
| `TierProfile` | the tier dials: memory horizon, time budget, retention, objective vector, join level | 0004 |
| `Join` | how a child registers: scope, DID, join-spectrum level, floors acknowledgment | new (small) |
| `AgentSurface` | the interoperability contract for **any** agent SDK (LangGraph, AgentField, other): write memory, retrieve, receive skill bindings, call models via the layer's Model Gateway (LiteLLM/OpenRouter) | new — this is how "a field can be doing anything" stays true: the surface is SDK-neutral |
| `GraphSpec` | the governed graph IR — what dual-mode authoring produces (English and canvas are both projections of it), what governance diffs and canaries, what compiles to LangGraph or any SDK | new — locked 2026-07-01; the 0008 dive |

**How the two proofs connect:**

- **ecosystem.harness** → conformance suite + reference simulator (above). Its cohort key extends
  `(field_id, goal_hash)` → `(ScopePath, goal_hash)` once, depth-agnostically.
- **CortexObserver** → a **reference, not a component.** What we take from it is *lessons*: interoperability
  (humans using NLP to engineer complex LangGraph agent graphs), gateway-enforced governance, and what a
  Field-tier pane must feel like. **Orreth's Field is native** — its layouts, usability, and agent-graph
  engineering UX are designed fresh (Fable owns them; **locked by JB 2026-07-01**). An *optional* adapter
  (maps `agent_id` → becky-issued DID, emits signed records up, pulls Standards down) can let an existing CO
  join as one kind of Field — but CO never drives Orreth's design.

---

## 5. The 4D pane — humans occupy a coordinate, per layer

The vision's operating picture: **a human at each layer sees all data of the fields/agents at their layer and
below** — the spacetime window, bounded by entitlement.

- The pane is **a client of the retrieval contract. There is no privileged pane path.** Every render is a
  `Query` under the human's capability token; every view is an access record. The watchers stay watched.
- Entitlement is scoped/directional/separated exactly per `governed-human-oversight.md`: down/within by default,
  up/across by grant, read vs control never conflated.
- What the pane renders is a **cut**: the subtree hypersurface at T (default: the moving present), scrubbable
  backward — fidelity honestly degrading with depth, because pruning (0003) *is* the fidelity curve.
- Recursive by construction: click a child node → same pane, one ScopePath down. The design language is
  **native Orreth** — fresh, refined, dark+light — informed by what CO's pane proved, not lifted from it.

---

## 6. "Build My First Universe" — how orreth.ai hosts it

- **Template = data, not code**: a TierProfile bundle + starter Standards + skill archetypes + agent-template
  roster + retention config + the policy floors that set the tone (the wild-vs-REAL dial).
- **The provisioner renders a template into a deployment**: docker-compose for dev/self-host, CDK for the hosted
  cloud. Same topology description, two renderers — which is why dev-parity matters (§7).
- **Tenancy is an infrastructure boundary, not a filter**: one universe = one stack/namespace = its own stores.
  No shared database with a `tenant_id` column between paying universes. The isolation story that sells the
  spacetime window has to be true at the infra layer, not just the query layer.
- **Domain:** reserve `orreth.ai` / `.com` **now**, not at validation. It's the cost of a dinner; losing the name
  after publishing Article 1 with "Orreth" in it is the expensive branch. *(Recommendation, not a lock — JB's call.)*

---

## 7. Dev hosting & repo layout

```
orreth/
├── contracts/            # the wire contracts (§4) — versioned, language-neutral
├── backend/
│   ├── plane/            # Rust workspace: orrethd + crates (gateway, resolver, router, stores, crypto)
│   ├── cognition/        # Python (uv): stewards, analysis agents, interview sandbox
│   └── conformance/      # the EH-derived fixture suite + the Python reference simulator
├── frontend/             # Next.js/TS/Tailwind — the recursive pane
├── infrastructure/       # compose (dev) + CDK (cloud) + the template provisioner
└── docs/                 # as today
```

**Dev topology (one laptop = one universe):** a single compose file stands up `universe` (orrethd,
profile=universe) + `eco-a`, `eco-b` + a simulated Field (or CO behind its adapter) + Postgres/pgvector +
MinIO + Redis. One image, profile via config — proving the layering claim every single `docker compose up`.
CI runs `cargo test` + `pytest` + the conformance suite on every commit. CDK later mirrors the compose topology
1:1, so nothing is learned twice.

---

## 8. Findings from the 2026-07-01 review → resolutions

| # | Finding | Resolution | Lands in |
|---|---|---|---|
| 1 | Pruning is the least-designed hard problem; pruning vs provenance tension | Derived records carry `derived_from: ContentHash[]` + steward signature; **Verified(derived) = chain-verification**; tombstoned inputs leave verifiable stubs in the chain. Pruning executes in the Steward, under a policy Standard | **0003 — pulled forward, next dive** |
| 2 | 0002 Query hardcodes tier names, contradicting free recursion | ScopePath-relative addressing (§1) | 0002 amendment |
| 3 | Interview = adaptive-query re-identification surface | Interview sandbox gets a **query budget** + noised aggregates on portfolio stats; per-entry owner opt-out stays. If the anonymization guarantee can't be made crisp, fall back to owner-curated + auto-verified | 0002 open decision 1 |
| 4 | "Engine lifts in" vs "Rust runs the plane" | Lift the contract, port the engine (§3) | this spec |
| 5 | becky is load-bearing for everything and sequenced late | Pull **0006 → immediately after 0003**; capability tokens block 0002's authz from being real | dive re-sequencing (below) |
| 6 | Budget-exhaustion is a side channel (leaks existence of deeper memory) | Budget-miss and authz-miss are **indistinguishable to the caller**; distinguishable only in the (privileged) access log | 0002 §4 amendment |

**Proposed dive re-sequencing:** 0002-amendments → **0003 pruning** → **0006 becky** → 0004 Tier Profile →
0005 Run Record & roll-up → **0010 AgentField & Gateways** → **0011 Factories (archetype → incarnation
stamping)** → **0012 HITL strategy (gates, queues, multi-party co-sign)** → 0007 resolver → 0008 pane →
0009 Build My First Universe.

---

## 9. Decisions — **all locked by JB, 2026-07-01** (recorded in `../decisions/`)

1. **Contracts: JSON Schema now → protobuf at Rust-time.** Human-diffable while design churns; typed on the
   wire when the plane lands; JSON Schema kept as documentation after.
2. **Simulator-first: yes.** A throwaway Python harness sim validates the contracts and the three flows
   end-to-end before a line of Rust; Rust then builds against proven contracts + the EH conformance suite.
3. **The Field is native Orreth**; CortexObserver is a reference proof only (optional adapter, never a
   driver). Orreth's layouts/usability are designed fresh.
4. **Domain: reserve now.** becky's did:web roots and Article 1 both anchor to the name — JB to register
   `orreth.ai` / `.com` (+ trademark glance in parallel).
5. **Dive order blessed**, including reserved dives 0010–0012, with 0008 (pane & graph engineering) pulled
   forward as the next dive after the 0002 amendments.

---

*Structure proposed. The scaffold is contracts + one node + one compose file — everything else is a profile.* 🥃
