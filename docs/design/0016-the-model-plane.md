# 0016 — The Model Plane (LiteLLM through the floors)

*Design draft — proposed by Fable 5 from JB's 2026-07-04 gateway dialog; JB's directional locks
arrived in the dialog and are recorded in §5. The governed door to models, made real — the
foundation both `0014` (Knowledge Loop) and `0015` (Orreth.agent chassis) stand on.*

---

## 1. The fractal gateway (placement, resolved)

The Model Gateway is an **organ at every tier** (it already lives in every TierProfile), and its
four flows split the way everything in Orreth splits:

| Flow | Direction | Mechanism |
|---|---|---|
| **Config** | cascades DOWN | the resolver (0007) folds allowed providers, class ladders, spend caps — floors tighten-only: an apex caps what a field may spend, never the reverse |
| **Calls** | serve LOCALLY | no universe-wide token chokepoint; latency stays at the field |
| **Model-misses** | escalate UP | a tier lacking a key/class/model delegates the *call* to its parent gateway — the retrieval pattern applied to cognition |
| **Usage** | rolls UP | tokens · cost · model_calls already ride the StatBundle monoid (0005); the universe's usage view is a standings query, per ecosystem/field/agent |

**Governance locus defaults to the topmost joined tier** (JB's instinct): keys and floors live at
the apex of whatever is joined, granted downward as capabilities (0013 custody). A standalone
field is self-contained with its own keys; join a universe and the apex governs while local
gateways keep serving. *Where the gateway is served from is a policy dial* — resolved like any
other cascaded config.

## 2. Model classes — the ladder

`low · medium · high · xhigh` are **first-class policy objects** mapping to provider model
groups (OpenRouter-style groupings). The universe-level selector is a **soft standard**
(most-specific-wins: a field may run hotter where policy allows); **skills pin classes, not
models** (0010: pinned tiers fail honestly, never silently dumber); humans/agents may assign
specific models or groups to an agent within policy. Class→model mappings are versioned config —
behavior is a diff, not an investigation.

## 3. The model lifecycle — the trust ladder's third application

Knowledge has states; rookies have probation; **models do too**:

`candidate → canaried → available → deprecated → sunset`

- The gateway **polls providers** for catalog and deprecation notices; a deprecation flips state.
- **Sunset re-routing stages through the lanes**: auto-apply for same-class substitutions
  (canaried, revertible), HITL gate where quality could move (judge full-grade on the
  replacement's canary — 0001).
- **No call ever lands on a retired model** — the "provider sunset broke production" outage
  genre becomes structurally impossible. vigil signals on every lifecycle transition.
- New models enter as **candidates** and earn class membership through canary — rookie
  probation for silicon.

## 4. Visibility & the non-LLM truth

Every call is metered (tokens, usd, model, class, latency) into RunRecords → bundles → the
Window. Agents carry an **`llm_dependent`** fact — JB has built agents that need no model — so
the pane can render *which agents survive a model outage*: availability engineering applied to
cognition. Cost roll-ups are visible at every tier to entitled humans and agents (the Cortex
usage view, now with provenance).

## 5. Directional locks (JB, 2026-07-04, in dialog)

1. **LiteLLM is the router.** OpenRouter is a supported provider-set with plumbing ready —
   **never the default**. Dev default: **Anthropic (Max) for heavy lifting + OpenAI** for
   cheap-smart; both ladders populated from these first.
2. **Tokens and cost must always be visible as they roll up** — per agent, field, ecosystem,
   universe; UI toggles per floor for customers of Orreth / orreth.ai.
3. **Tuning agents (model class, skills) is a core intention** — the ladder + per-agent
   assignment machinery above serves it.
4. **Provider lifecycle management is mandatory** (§3) — query providers, tombstone/sunset
   expiring models, re-route before incidents.
5. Keys live in env/KMS per custody tier — never in contracts, never in git.

## 6. Build sequence

1. **Cognition-side gateway (now):** `orreth_sim/model_plane.py` — registry with lifecycle
   states, ladder resolution from the resolved context, LiteLLM routing, real metering into
   RunRecords; first governed live call proven end-to-end.
2. **Plane-side enforcement:** orrethd gains the gateway sidecar contract — budgets from lease
   tokens enforced in Rust (the 0010 machinery), metering written through the same ingress.
3. **Contracts:** `model-registry.schema.json` (classes, lifecycle states, provider maps) once
   the shape survives contact with real usage.
4. **The pane:** usage view over the cost roll-ups; the outage-survival view (`llm_dependent`).

---

*One door to every mind, governed like everything else: config falls, calls stay local, misses
climb, usage rises — and no agent ever discovers at 3 a.m. that its brain was turned off last
Tuesday.* 🥂
