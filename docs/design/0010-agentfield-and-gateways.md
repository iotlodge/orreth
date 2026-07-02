# 0010 — AgentField & Gateways (the medium, and the doors)

*Design draft for review — proposed by Fable 5 (design owner). The first of the reserved dives (0000 §2/§8).
**All decisions locked by JB 2026-07-02** (via AskUserQuestion, §6). Contract + simulator landed with the dive.
Companions: `0006` (the join flow and lease tokens this dive presents at the door), `0005` (the RunRecords the
surface emits), `0013` (vigil's tap and the content-transit surfaces).*

---

## Why this is a keystone

Every promise about governance assumes a chokepoint: **there is exactly one way in, one way out, and one way to
a model.** The AgentField is the medium child processes live in; the Gateway is its only door; the AgentSurface
is the only handle a workforce agent ever holds. "A field can be doing anything" (LangGraph, AgentField-SDK,
anything) stays true *because* governance binds to the surface, never to the SDK — the same reason the pane
binds to the retrieval contract and not to a database.

---

## 1. The AgentField — the medium

The runtime substrate of a Field: **lifecycle** (spawn from archetype → attach → detach → retire; reboot ≠
death because memory keys to the DID, `0002 §1`), **supervision** (a crashed process re-attaches to its
identity — the thread survives the needle), and **signals** — the intra-field transport agents coordinate over.

> **Signals are transport, not memory — until they change state.** *(Locked 2026-07-02.)* A decision, a
> handoff, an artifact **must land as a MemoryRecord to have happened: if it's not memory, it didn't happen.**
> Chatter evaporates. The Tier Profile's `signal_capture` dial (`none | state-changing | full`, default
> `state-changing`) is **the first concrete member of the wild-vs-REAL spectrum**: a game universe runs cheap,
> a regulated universe turns on `full` and can reconstruct *why the fleet decided X*. Either way, **vigil sees
> volume and shape as metadata** — the tap is content-blind and dial-independent (0013 §3).

---

## 2. The Gateway — one door, both directions

The `0000 §2` organ, staged:

| Direction | Pipeline |
|---|---|
| **Ingress** | DID resolution → signature verify → revocation check (the NANDA index; ancestor kill-switch) → anti-spoof/freshness → floors-acknowledgment (join) → high-water clock check (0004) → ingest |
| **Egress** | token verify (chain, expiry, subject alive) → covering-grant check → visibility filter (tenancy/portfolio/consent) → **budget gate** (budget-miss ≡ authz-miss, `0002 §4`) → signed access record |

The Gateway is also where the **content-transit enforcement** for cryptographically blind tenants lives
(0013 §10): ingress/egress and the Model Gateway are the platform-operated surfaces where content-level floors
can act at all for BYOK/split universes.

**The workforce join flow** (`0006 §2`, now concrete): any-SDK agent presents with a sponsor → becky verifies
and issues a **scoped DID + a lease token** (grants attenuated to the lease; the join-spectrum floor and the
**per-identity model budget ride the token's `constraints`**) → the Gateway hands back an **AgentSurface**.
Never raw store access; never a key; never an unmetered model.

---

## 3. The AgentSurface — five verbs, SDK-neutral

`contracts/v0/agent-surface.schema.json`: **write · retrieve · standards · call_model · signal.** That is the
entire world an agent can touch, and each verb is the existing contract wearing a handle: write = the
`MemoryRecord` ingress, retrieve = the `Query` egress, standards = the cascade PULL, call_model = §4,
signal = §1. GraphSpec (`0008`) compiles onto these verbs; AgentFacts' runtime evaluations (`0006 §5`) and
RunRecords (`0005`) are emitted *about* the agent by residents observing the surface — never by the agent
about itself.

---

## 4. The Model Gateway — the cost dial with a conscience

No agent calls a model ungoverned (`0000 §2`). The layer's Model Gateway routes (LiteLLM/OpenRouter/direct per
profile), meters against the lease budget, and enforces `SkillStandard.model_tier` pins:

> **Locked 2026-07-02: degrade where pins allow.** A budget-squeezed call routes to a cheaper tier **with an
> honest `degraded` flag** — the fleet keeps working at 3 a.m., and drift/canary can tell a budget-dip from
> skill rot because the flag lands in the RunRecord. **But a pinned tier is a floor: an unaffordable pinned
> call fails honestly.** A skill never silently runs dumber than the tier its rubric was proven at. (The same
> shape as the steward's degrade-to-floors-and-flag, `0003` — Orreth degrades loudly or not at all.)

Every call — served or refused — lands on the gateway log with caller, tiers, and charge: **vigil's tap**,
volume and shape, never content. Judge sampling (`0001`) hooks here too: 1-in-N steady, 1.0 during canary.

---

## 5. Contract & simulator (landed with the dive)

`agent-surface.schema.json` (AgentSurface + ModelCall / ModelCallResult / Signal) · `tier-profile` gains the
`signal_capture` dial · simulator `agent_surface.py` (ModelGateway, AgentSurface, `join_workforce`) wired into
the node. **Three new tests, 20/20 passing:** join-and-hold-only-the-surface · degrade-where-pins-allow (incl.
the honest pinned failure and the content-blind gateway log) · signals-are-transport-unless-state-changing
(incl. the `full` dial flip).

---

## 6. Decisions — **all locked by JB, 2026-07-02** (via AskUserQuestion; recorded in `../decisions/`)

1. **Budget exhaustion: degrade where pins allow.** Cheaper tier + honest flag; pinned tiers are floors that
   fail honestly; no silent dumbing-down, no 3 a.m. fleet stalls.
2. **Signals: Tier Profile dial, default state-changing.** Transport by default; state-changes must land as
   memory to have happened; `full` capture for REAL/regulated universes; vigil's metadata tap sees shape
   regardless.

---

*Unblocks: `0011` (Factories — archetype → incarnation stamping is a Gateway client: every stamped incarnation
walks through this door), `0012` (HITL mechanics — the escalation queues these gates feed), and the League's
workforce (players join a team the way any agent joins a field: leased, budgeted, surfaced). One door in, one
door out, one door to a model — and vigil watching all three, blind to content, awake to shape.* 🥃
