# 0059 — The Living Toolshed

<!-- PROVENANCE: Fable 5 (claude-fable-5) — seeded 2026-08-21 from JB's brief
     ("Farm facelift, FULL control, the human-lifecycle lens — like the Stable"). -->

**Seed (JB, 2026-08-21):** three lifecycle areas — (1) horizontal capability:
what the Farm can hold, with eyes on the emerging tool/MCP ecosystems; (2) the
verbs: onboard · stop · start · continue · stop-fully · retire, linked to
observability and the long tail of who-uses-what; (3) allocation across the
universe, the Stable's law applied to tools. Innovation welcomed (a warden in
the onboarding flow; policy-managed compliance). The proving ground: **the
Tavily MCP** (`TAVILY_MCP_LINK`, standing in .env). And one design-impacting
truth: **capabilities WILL manifest MCPs and tools for the universe's own
use** — the universe expanding its own capabilities — so a tool's *source*
is a first-class fact. Charlotte's presence matters: she is the playground,
testing MCPs beside the human and answering for her toolshed.

**What already stands (the honest map):** the Farm's state machine is
plane-guarded (proposed → probation → serving → dropped/quarantined →
decommissioned; the rug-pull hash check lives in the plane, never trusted
from the keeper); charlotte plants, probes, pins the manifest, attests,
heartbeats, ages leases out, replants after restarts, and writes every
transition as a signed worldline; `mcp_tools()` already speaks streamable
HTTP (initialize → tools/list, SSE unwrapped); the ONE invoke door already
meters-as-authorization before executing. 0059 connects organs more than it
grows them.

## 1. The taxonomy (the Stable's table, farm-tongued)

| Orreth | Industry | What it is |
|---|---|---|
| the seed catalog | tool/MCP registry inventory | intel about tools that EXIST — read-only, provenanced, never authority |
| a planting / a service | an onboarded tool / MCP server | identity (did:web from its domain), pinned manifest, lifecycle |
| the manifest pin | the tool contract | the tools/list charlotte SAW; a byte moving walks the rug-pull door |
| plant → attest → probation → serving | onboard → approve → verify → publish | birth is governed; service is earned by beats |
| **resting** (NEW) | stopped / paused | the human's word, lease kept — distinct from *dropped* (the wire's silence) |
| decommission (+discredit) | retire (+revoke trust) | terminal; discredit hands the knowledge recall to the librarian (0014 §4) |
| a tool allocation (NEW) | binding / preference | WHO uses which serving tool — the 0058 law, farm-shaped |
| the worldline | audit history | charlotte authors; a tool never self-attests |
| `source` (NEW) | provenance of onboarding | `human` · `seed:<registry>` · `capability:<key>` — the universe growing its own |

## 2. The laws of 0059

1. **Intel is never authority** (0058's law, kept whole): a seed can be
   searched, compared, selected — nothing serves until planted, probed,
   approved, and earned through probation. The catalog's eyes: the official
   MCP registry (live search, cached with TTL), the rig's own toolshed, and
   capability-declared tools. Provenance kept per seed.
2. **A secret never enters a record.** An endpoint may be an `env:NAME`
   indirection resolved only at probe/call time — the ledger, the plane, the
   worldline, and the glass hold the *name*, never the value. The Tavily MCP
   link (key-in-URL) is the proving case.
3. **The warden confesses at the gate; she never decides** (vigil, 0002's
   content-blind law): every staged planting wears her checks — credential
   smells in the URL, insecure scheme, declared-vs-probed manifest mismatch,
   the source's kind — as amber lines beside the human's buttons. Policy
   stays informative; the word stays the human's. (Policy-as-craft: a named
   seed — the check list as an editable Canon asset.)
4. **Resting is the human's word; dropped is the wire's.** `resting` joins
   the plane's state machine (serving|probation → resting → probation on
   resume; decommissionable). The gateway's meter-as-authorization refuses a
   resting service *for free* — no second enforcement point. The Tavily
   pause lever (the standing-spend law's old debt) is this posture.
5. **Spend rides one ledger.** A planting may declare a standing-spend guard
   (`spend_guard: "search"`); the invoke door counts those calls against the
   SAME declared daily ceiling the direct path uses (0054 L-A) — one
   ceiling, every road.
6. **A capability's tools are citizens, not shadows.** A capability manifest
   may declare tools; they enter through the SAME plant gate wearing
   `source: capability:<key>`, and the capability's retirement stages a
   confession on each of its tools. The universe expands its own hands —
   governed at every knuckle.
7. **Allocation is the 0058 law, farm-shaped**: subject → preferred serving
   service (optionally per tool), resolved subject → floor → universe;
   staged through charlotte's gate; the who-uses-what join (allocations +
   the farm meter's caller DIDs) is the blast radius on every rest, decom,
   and rug-pull card — the long tail visible at the decision.
8. **The invoke door is ONE door** for every transport: `POST {endpoint}/call`
   for local stalls, `tools/call` JSON-RPC for MCP — same meter, same
   refusal face, same pointer law (bulk results never become records here).

## 3. The spoonfuls

**sp1 — the seed catalog.** `orreth_sim/seeds.py`: the official MCP registry
searched live (`/v0/servers?search=`, remotes → candidate endpoints,
version/status kept), merged with the rig's toolshed and capability-declared
tools; per-query TTL cache, provenance, suite-held. Worker door `/seeds?q=`.
*Proof: search "tavily" and real registry entries answer with their remotes;
kill the network and the cache speaks, labeled.*

**sp2 — MCP becomes a whole transport + the Tavily proof.** `tool_invoke`
gains the MCP branch (tools/call, session-aware, SSE-unwrapped); `env:`
endpoint indirection everywhere an endpoint is touched; the spend guard on
the invoke door; vigil's confession on every staged planting. Then the
proof: plant `tavily-mcp` by its env name, watch charlotte enumerate its
tools, approve, watch probation earn serving, and make one governed
`tavily_search` call through the door — metered, ceilinged, the result in
hand. *Proof: the whole lifecycle live, and the ledger/records grep clean of
the key.*

**sp3 — postures + allocations + capability-born tools.** `resting` in the
plane's legality with rest/resume through charlotte's gate; the tool
allocation ledger with the 0058 resolution law; blast radius (allocations +
recent callers from the meter) on every rest/decom/reapprove card;
capability manifests may declare tools that enter as governed plantings
wearing their source. *Proof: rest tavily-mcp and watch the door refuse with
the one face; resume and watch probation re-earn; a capability-declared tool
arrives at the gate wearing its source.*

**sp4 — the glass earns its respect.** The Farm tab on the canon
master-detail: waiting · the toolshed by floor · allocations · the compost
(decommissioned, folded) left; the reading pane right — the pinned manifest
tool-by-tool, THE LIFE (beats, calls, misses), WHO USES IT, vigil's
confession, and the verbs (rest · resume · reapprove · decom ·
decom+discredit). THE SEEDS face: registry search + plant-from-seed (kind
and endpoint pre-filled, env-indirection offered when a credential smells) +
**ask charlotte** (plain words over seeds and shed, voiced under her DID) +
**the playground**: pick a serving tool, give it arguments, and charlotte
runs it through the ONE door — the result in the pane, the meter ticking.
*Proof: JB's own walk; the Tavily playground answering a real search.*

**sp5 — the rites.** Register row, road entry, era 0.59, taxonomy door,
memory. Named parks carried honestly.

## 4. Named parks

- **Container deploys for stdio/npx MCP servers** — allen's walk (the
  shipyard knows how to launch hulls; a seed that needs a body waits for
  him). Remote (streamable-HTTP) servers need no body and land in v1.
- **Policy-as-craft** — the warden's check list as an editable Canon asset.
- **Charlotte-crafted sample arguments** — the playground's v2: she reads
  the tool's schema and proposes the test herself.
- **Node-level fidelity** (0018's old open item) — carries JB's lock; it
  comes as a question, never assumed.
- **Registry publication** — Orreth PUBLISHING its capability-born MCPs to
  the official registry: the universe not just growing hands but offering
  them. A future dive with 0042's deed law all over it.
