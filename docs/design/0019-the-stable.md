# 0019 — The Stable (the model plane gets a face)

*Design draft — proposed by Fable 5 from JB's 2026-07-06 ask ("I see NO UI for the LLM
Farm/Gateway… every agent should be able to use the gateway and the gateway needs to roll
up the metrics"). Completes `0016` (whose registry, ladder, and lifecycle this gives an
identity, a keeper, and a human face) with the moves `0018` proved on tools. JB's locks:
**The Stable + ada**, full dive, 2026-07-06.*

---

## Why this is the missing half of 0016

0016 built the gateway's spine: the class ladder (`low · medium · high · xhigh`), the
lifecycle (`candidate → canaried → available → deprecated → sunset`), plane-enforced
budgets, and the split that keeps the constitution intact — **the plane authorizes and
meters; cognition executes agent-side; orrethd never sees a prompt or holds a provider
key**. What it never got was what the Tool Farm got in 0018: an identity per entry, a
worldline, a keeper, a staged HITL door, and a tab a human can stand in front of.
`/model/state` is still a naked dev endpoint. And the cost truth JB named as *the* reason
universes exist — per-agent tokens/usd, every agent, every floor — stops at workforce
agents on a single floor: residents are hardcoded `$0` and filtered out of the spend
panel, `/rollup` (Pulse) is floor-local while the orrery shows the subtree, and the meter
log dies with the daemon.

The Stable ends all of that with the two 0018 moves, applied to minds: **a model is a
service an agent thinks through, and a service is an identity with a worldline.**

## 1. The stall — the registry entry

```
Stall {
  id            : "anthropic/claude-sonnet-4-6"   # canonical model id
  provider      : "anthropic" | "openai" | "openrouter" | …
  route         : "litellm-direct" | "openrouter" # WHO carries the call (keys stay env/KMS)
  did           : DID                             # vendor identity — did:web:anthropic.com,
                                                  #   the same 0014 source registry the Farm uses
  class         : "low" | "medium" | "high" | "xhigh"
  manifest      : {pricing, context_length, modalities, supported_params, effort}
  manifest_hash : ContentHash                     # canonical bytes (0000 §3) over the DEAL
  state         : 0016 lifecycle (§2)
  expires_at    : ISO date | null                 # announced EOL — the pasture calendar
  floor         : ScopePath                       # where saddled; cascades DOWN, tighten-only
  saddled_at / last_synced / attested_by          # the vitals
}
```

- **The manifest hash pins the deal, not just the definition.** Pricing, context window,
  modalities — canonical bytes over what was true when the human approved. A silent price
  hike or a quietly-halved context window is **manifest drift: the rug-pull door**
  (0018 §2), and the stall stops serving new authorizations until a human re-approves the
  new bytes. Nobody in the industry governs price drift; this substrate gets it for free.
- **Routing and intelligence are separate planes.** JB's constraint (2026-07-06): the dev
  default routes **LiteLLM-direct on Anthropic + OpenAI keys** (the 0016 §5 lock);
  OpenRouter is a supported route for whoever holds that key instead. But OpenRouter's
  *public catalog* (no key, 342 models, carrying `pricing`, `context_length`, and
  `expiration_date`) is an **intel source for every stall regardless of route** — the
  keeper reads the market even when the call goes direct.

## 2. The lifecycle — already law, now governed

0016 §3's ladder is already enforced in `model.rs` (sunset is never served; deprecated
serves loudly; misses climb to the parent). The Stable adds the governed door in front:

- **Saddling is a staged request, exactly like planting** (0018 §2): a `mind` request in
  the floor's queue; ada probes the catalog, pins the manifest, stages; **a human
  approves**; the stall enters `candidate → canaried`. Silence never approves (0012 §4).
- **Canary is probation for silicon** (0016 §3): the plane counts canary beats — ada's
  verified catalog syncs plus, where a key is present, a real one-token governed call
  **metered under ada's own DID** — and promotes `canaried → available` at the threshold,
  exactly as farm heartbeats earn `serving`.
- **Deprecation is an appointment, not an incident.** ada's sync sees `expires_at` (or a
  provider notice) → the stall flips `deprecated` (loud) → ada **stages a recommendation**:
  the nearest same-class stall or catalog candidate, with the price delta. Approving the
  swap canaries the replacement and schedules the sunset. The Console's **pasture
  calendar** shows every expiry as a diamond on a timeline; inside 30 days it burns.
- **Drift → decide.** Changed manifest bytes at sync → `deprecated` + a `reapprove`
  request showing exactly which bytes moved. Re-approval re-pins; denial retires.
- **Retirement is staged decom** (0012), and `sunset` remains structurally unservable.

## 3. ada — the wrangler

The Stable's agentic half is **ada, the wrangler** — the fourth resident duty in the
host-side worker, beside becky's door, charlotte's farm, and the librarian's gathers.
A persistent seed under `~/.orreth/residents/ada.seed` (a keypair is a self); becky's
issuance is unchanged (one issuer, 0006); vigil still only watches.

ada's duties: sync catalogs (OpenRouter public, provider lists) · probe + pin on saddle ·
detect EOL and drift · stage recommendations and reapprovals · canary through the gateway
· write the worldline. Every lifecycle transition lands as an **ada-signed MemoryRecord**
tagged `["mind", <id>]` — stalls appear on worldlines in the spacetime window, and *"what
minds served this floor last Tuesday, at what price"* is a cut, not archaeology. Nothing
self-attests: a model is `available` because ada said so and a human opened the gate,
never because a provider's status page said so.

**ada thinks through her own gateway.** Her canary calls authorize, execute, and meter
like any agent's — she is the first resident with honest nonzero usage, and the standing
proof of the rule below.

## 4. Usage is universe truth — the reason for the dive

JB's core ask, now structural:

1. **Every agent's cognition goes through the gateway — residents MUST.** An organ that
   thinks off-meter is drift (covenant addition, this dive).
2. **The meter rides the beat.** `summary()` gains a per-agent usage array (meter log
   joined with RunRecords, keyed by DID) beside `workforce`/`farm`/`residents` — the apex
   sees every agent's tokens · usd · calls on every floor, live (the F2 lesson, applied
   before the bug this time).
3. **Residents show their cost — including the honest zero.** Resident vitals gain
   `tokens/usd/calls` read from the meter by DID; the spend panel stops hardcoding `$0`
   and stops filtering organs out. An idle steward reads `0`, visibly.
4. **Pulse agrees with the orrery.** `/rollup` aggregates the subtree from child beats —
   one world, one picture, at the dashboard too.
5. **The meter survives the daemon.** Write-through to Postgres beside the records; usage
   history is memory, not vapor.

## 5. Floors — the 0016/0018 fractal, unchanged

| Flow | Direction | Mechanism |
|---|---|---|
| Stalls & ladder config | cascade DOWN | saddle at any floor; children may refuse (tighten), never conjure |
| Calls | serve LOCALLY | authorize + meter at the consuming floor; latency stays down |
| Usage & state | roll UP | stalls + per-agent usage ride the `/hello` beat beside workforce and farm |
| Saddle / swap / retire | stage WHERE SADDLED | each floor's queue, each floor's humans |

## 6. What lands with this dive (dev-rig scope)

1. **Sim first** (0000 §9): `orreth_sim/stable.py` — stall records, drift detection, EOL
   scan, recommendation choice; tests for the drift door and the swap flow.
2. **Plane** (`orrethd`, non-sacred): `model.rs` gains stalls (identity view) beside the
   class registry (routing view), canary beats, drift check on sync, pg write-through for
   the meter; routes `GET /stable`, `POST /stable/state` (keeper ops), `POST /stable/hello`
   (canary beat); `summary()` gains `stable` + `usage`; `/rollup` aggregates children;
   residents gain metered vitals + ada.
3. **Cognition** (`console_worker.py`): ada — seed, catalog sync, saddle probe/attest,
   EOL + drift staging, recommendations, canary, worldline, ledger under `~/.orreth/stable/`.
4. **Console** (`window.html`): the **Stable tab** — the ladder, saddle-a-mind (with
   presets from the 0016 dev defaults), pending decisions, the pasture calendar, the
   stalls, and *who is thinking* (per-agent usage, whole subtree, residents included);
   Pulse gains usage-by-agent/model/class; the spend panel tells the truth.
5. **Demo** (`demo_stable.py` + `demo.sh`): saddle → approve → canary → available →
   EOL notice → approved swap — read off the worldline.

## 7. Decisions

**Locked by the constitution (no new locks needed):** lifecycle + ladder + budgets (0016);
staged human-decided transitions (0012); keeper signs, nothing self-attests (0005 · 0018);
plane meters, never sees prompts or holds keys (0016 §6); floors tighten-only (0007);
identity ops are memory (0006 §4).

**JB's locks this dive (2026-07-06):** the name is **the Stable**; the keeper is **ada**;
full dive now; LiteLLM-direct default routing with OpenRouter as route option + free intel.

**Fable's calls (JB may overrule):**
1. **Manifest pins the deal** (pricing + context + modalities), so price drift walks the
   rug-pull door — the Stable's sharpest new tooth.
2. **Canary = ada's verified syncs, plus a real metered call when a key is present** —
   honest on rigs without keys, stronger with them.
3. **Covenant gains one sentence** under rule 5: *every resident's cognition goes through
   the gateway; an organ that thinks off-meter is drift.*
4. **Recommendations rank by same-class → nearest price → newest catalog entry** — simple,
   explainable, human-overridable; smarter ranking is a later dive.

**The wart pass (2026-07-08)** — the four known follow-ups from this dive, closed:

1. **The canary ping travels, and it exercises the mind it vouches for.**
   `/model/authorize` gains an optional `model` pin: the named stall serves or the grant
   refuses — a pinned miss never climbs, because the stall it names lives on this floor.
   `governed_ping` pins the rookie, honors the stall's route via `executable()` (0020's
   law: authorize is truth for routing, keys are truth for execution), refunds honestly
   when the floor holds no key, runs on any provider fuel including OpenRouter, and is no
   longer scoped to the join floor — becky's tokens chain to the pinned root everywhere,
   so every floor's stable earns its canary thought.
2. **`resolve()` serves veterans first.** Available before canaried, at the plane and in
   the sim — a rookie on canary never shadows a serving mind.
3. **The queue refuses a caller-supplied `id` loudly** (400) instead of clobbering it
   silently — name the subject in its own field (`mind`/`name`/`did`/`to`).
4. **Recommendations gained the deal fit** — call 4's "later dive", arrived: candidates
   must hold the pinned deal (context ≥ the pin's, modalities covering it) before price
   distance and recency rank them; no full fit anywhere is said honestly in the `why`.

---

*Saddled by request, pinned at the deal, canaried into service, deprecated by the
calendar instead of the outage, swapped with a recommendation instead of a scramble —
and every thought, by every agent and every organ, on one meter the whole universe can
read.* 🥂
