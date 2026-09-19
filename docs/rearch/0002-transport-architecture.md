# 0002 — The Transport Architecture

**Status: LOCKED — JB approved 2026-09-16.** The Transport Deep Dive's
design, derived from the Experience Charter (0001) and JB's direction
(2026-09-16: "MQ is ideal for agent invocation and management while Kafka
serves as a great way to build and subscribe to topics for fan-outs… maybe
Redis has a place also… we should partition effectively").

**Input honored:** the six-document SOL review (`tmp/orreth-messaging-
architecture/`, 2026-09-09, pre-halt). Verdict: rigorous and largely
correct — its contracts, outbox discipline, presence redesign, regional
cells, and proof method are ADOPTED below. Its one dead assumption is
re-based: it made AgentField the cognitive rail; **LangGraph is now the
default agent framework**, so the cognitive plane moves inside the
LangGraph resident template and its bake-off (old proof M3) is retired.

---

## What the Experience demands of transport

The charter is the requirements document. Read as transport obligations:

| Charter demand | Transport obligation |
|---|---|
| Soft completions, fire-and-continue (P5) | Push channel to the Bridge; results announced by event, never by polling |
| Every ask wears its journey (P7) | Journey events emitted at each routing/fulfillment step, streamed to the glass |
| Nothing runs unseen (P13) | Every lifecycle transition (queued → in flight → completed) is a published event feeding the Objectives band and Monitoring |
| One chat fan-out (P14) | One ask becomes N addressed invocations; N labeled results return independently; optional summary is a new ask |
| One state, many lenses (P17) | Change events invalidate every open view instantly |
| Time scoping / replay ("between X and Y") | A replayable event stream with real retention; graph/work replay reads it |
| Scope is a lens, not the kernel's (P9) | Routing by scope+capability carried ON the message; no scope-per-port physical addressing |
| Placement is policy (P10) | Brokers deployed per placement profile, per cell; universe isolation is physical |
| Sub-second feel | Invocation dispatch measured in milliseconds; the queue never sits behind a 2-second poll |
| Hundreds→thousands of agents; 500–1000-hop objectives | Idle cost independent of population; work cost proportional to actual work |

## The rails — plain words first

Four kinds of message, four mechanisms. A message never changes kind
without crossing a durable, signed state transition first.

| Rail | Plain words | Mechanism | Never |
|---|---|---|---|
| **Invocation** | "Please attempt this now" — one winner claims it | **RabbitMQ** quorum queues, topic exchanges, acks, priorities, deadlines, dead-letter parking | Never proof the work was authorized or done |
| **Events** | "This already happened — verifiably" | **Kafka** topics, keyed partitions, consumer groups, retention, replay | Never the record itself; never a second truth beside the signed log |
| **Questions** | "Show me the authorized answer now" | HTTP/gRPC through the kernel's governed doors, service discovery (no user-visible floor ports) | Never bypassed by a broker shortcut |
| **Thinking** | "The agent reasons through its graph" | **LangGraph** inside the resident (checkpointer = working memory only) | Never a hidden runtime: every cross-agent hop rides Invocation and emits Events |

Plus **the Bridge feed**: one authenticated WebSocket/SSE endpoint per
human session at the gateway. It carries small notices (revision, kind,
ref); the glass fetches authorized read models through the Questions rail.
**The browser never touches a broker.**

This matches JB's instinct exactly — RabbitMQ for agent invocation and
management, Kafka for topics and fan-out subscription — with the SOL
package's discipline underneath.

## Who carries what — the partition

| Communication | Rail |
|---|---|
| Human ask from the Bridge | Questions (gateway door) → kernel stages it → Invocation |
| Chat fan-out to N residents | N invocation messages, one per resident, sharing a correlation id |
| Agent invokes another agent | Invocation, through the door (envelope, authority, meter) |
| Hops INSIDE one agent's graph | Thinking (in-process LangGraph; checkpointed) — hop events published to Events for replay/monitoring |
| "Request XX completed" soft notice | Events → Bridge feed |
| Journey text ("routed to allen on …") | Events (journey family) → Bridge feed |
| Lifecycle band / Objectives hatch | Events (request.transitioned) → Bridge feed + Monitoring |
| Schedules firing (human/role/kernel) | Scheduler commits occurrence → Invocation claim |
| Cancellation / contain / rest | Durable state transition → high-priority Invocation control message; fencing epoch blocks stale workers |
| Presence / topology | Self-only lease events (compacted Kafka topic) → one projector builds the tree — nested heartbeat snapshots END |
| Monitoring, analytics, meters, showback | Events consumers with their own offsets |
| Graph/work replay in Workspace Engineering | Events retention + the signed log |
| Standards/policy distribution | Events announce availability (pointer+hash); child still PULLS and verifies through a door |
| Record/body retrieval | Questions only — events carry pointer + hash, never bodies or prompts |

**Redis — a narrow maybe (JB's "maybe Redis has a place"):** candidate for
ephemeral presence bits, hot read-model cache, and sliding-window
quota/rate counters. It is NOT a third message rail. Deferred until a
proof shows Postgres + the two brokers genuinely need it.

## The laws (adopted from the SOL contracts, all retained)

1. **Transport never becomes authority.** Identity, capability, policy
   head, budget, and fencing epoch are re-verified at the action boundary.
   The signed record/deed/receipt is the evidence; broker metadata is
   operational only.
2. **Transactional outbox, always.** Domain state + outbox row commit in
   ONE Postgres transaction; a relay publishes after commit. No dual
   writes. A committed record cannot lack its event; a rolled-back one
   cannot emit.
3. **At-least-once, idempotent effects.** Stable message ids, durable
   consumer inbox/effect ledger, aggregate sequence + fencing checks.
   "Exactly once" is never claimed of external effects.
4. **The ACK law.** Acknowledge only after a durable outcome, a proven
   duplicate, a durable terminal refusal, or a confirmed handoff.
5. **Pointer-only payloads.** Events carry ref + hash + scope + ids —
   never prompts, bodies, or bearer credentials. Bodies come through
   governed doors with current authorization (a revoked consumer holding
   an event pointer gets uniform refusal).
6. **One shared, broker-neutral envelope** (canonical bytes; versioned
   schema; correlation/causation/trace ids) — Orreth owns the schema, the
   brokers only carry it.
7. **Bounded pools, never per-identity queues/topics.** Sharded queue
   families keyed by stable scope/aggregate hash; topic families keyed by
   aggregate — population growth never grows broker metadata.
8. **Regional cells, physical universe isolation.** No stretched broker
   quorums across WAN; every subject has a home cell + epoch; commands
   route home; selected signed facts replicate asynchronously; a
   production universe gets its own accounts/networks/keys/stores/brokers
   (P10's blast-radius law at the infrastructure layer).
9. **Cancellation is a state transition plus a fast wake-up** — never a
   queue deletion. Workers check at safe boundaries; stale epochs cannot
   commit. "The human can always stop" gets a measured propagation SLO.

- **The marker rides every envelope** (0006, JB's lock 2026-09-19):
  `marker {kind, id, parent, by}` — the typed origin the fact serves; a
  root fact mints it, a new beginning under it mints a child. Kinds come
  from a governed, expandable registry (the kernel seeds objective ·
  intention · thought · action · observation). A marker set is itself a
  fact on the rail (`orreth.marker.set.v1`), so interested bodies act on
  it and Understanding rebuilds the lineage from the log. The chain says
  who; the marker says why; never conflated. Four short fields — the
  words stay on the ground.

## The LangGraph re-base (what changed since the SOL review)

- The SOL package's warning stands, transposed: **no invisible second
  runtime.** The resident template therefore emits journey/trace events
  for every cross-agent hop and every significant in-graph transition, so
  the act graph and the Bridge can draw the whole story.
- **The checkpointer is working memory, never truth.** Durable outcomes
  land as signed records through doors; hop events reference them.
- Cross-agent invocation ALWAYS rides the Invocation rail through a
  governed door — a LangGraph node never opens a socket to another agent.
- The old M3 "AgentField vs RabbitMQ bake-off" is retired. Its replacement
  proof: **the LangGraph resident template driven by RabbitMQ invocation,
  end to end, emitting its journey** (see roadmap).

## SLOs (first written targets — JB adjusts)

| Experience moment | Target |
|---|---|
| Ask leaves the Bridge → first journey text visible | < 300 ms |
| Invocation queue delay, healthy cell | p99 < 1 s |
| Chat first token (streaming reply begins) | < 1 s |
| Completion event → soft notice in the glass | < 1 s |
| Cancellation propagation to queued work | p99 < 2 s |
| Event commit → projection/Monitoring visibility | p99 < 5 s |
| Idle transport cost | independent of floors/agents/retained requests |

## Proof roadmap (SOL's method, re-based)

Adopted as-is: **M0** baseline the current rig · **M1** outbox/inbox +
broker-neutral envelope (Postgres only — no broker yet) · **M2** self-only
presence leases + topology projector · **M4** Kafka fact rail with replay
parity · **M5** one reflex event-driven end to end · **M6** the Bridge
feed (SSE/WebSocket, gap repair, 10k clients) · **M7** two regional cells
under partition · **M8** adversarial universe isolation.

Changed: **M3 becomes "the resident speaks"** — one LangGraph resident,
invoked through RabbitMQ, streaming a full reply to the Bridge feed, with
journey events, cancellation, and the L2 interlock — the charter's "a
resident can actually chat" bar as a transport proof. Every proof keeps
shadow-run + rollback discipline; polling is removed flow by flow only
after replay parity is proven.

## Explicitly open (for JB / later dives)

- Redis: earn or reject by proof (presence, cache, quota counters).
- Managed vs self-run brokers per cloud (Amazon MQ / MSK vs containers) —
  a placement-profile decision, behind the broker-neutral contracts.
- The scheduler's home (kernel organ vs resident duty) — lands with the
  AGENTS dive; its occurrences ride Invocation regardless.
- Streaming token transport for chat replies (gateway-relayed from the
  agent vs chunked events) — decide inside proof M3.
- SLO numbers above are Fable's first writing of JB's felt bar — JB
  confirms or tightens.

## What this document binds

Transport serves the charter — never the reverse. Any transport behavior
the human can feel (journey, completion, cancellation, replay) is an
experience obligation with an SLO, proven by the playwright agent against
the Bridge, not asserted. The signed log remains the only truth; the
brokers are how the truth travels, never where it lives.
