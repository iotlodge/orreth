<!-- PROVENANCE: authored by Opus 4.8 (2026-07-05), pending Fable 5 review — see agents/PROVENANCE.md -->
# Make your agent run in a universe

> **The pitch:** you already have an agent — a prompt, a LangGraph, an AgentField reasoner
> network, a cron script. Give it an Orreth **identity** and it gains a home floor, a signed
> memory that outlives the process, a governed mind it draws through a metered door, and a
> diary that makes it *appear, live, in the universe* — roster, orrery, spend, all of it.
> The architecture is a governed loop. So is the agent. They fit.

This directory is that kit.

```
agents/
  orreth-agent-sdk/        the lifeforce SDK — identity, join, memory, mind, diary
  flavors/
    01-prototype/          agent.yaml-driven lifeforce (change data, not code)
    02-langgraph/          the same loop as an explicit, deterministic StateGraph
    03-agentfield-sentinel/ an AgentField-style reasoner network — a conformance sentinel
  PROVENANCE.md            authorship ledger (this tree is under review)
```

## The five verbs

Every flavor is the same five verbs from `orreth_agent`, in the same order:

| verb | what it is | governs |
|---|---|---|
| **spawn** | a keypair is a self (`did:key`, resolvable offline) | 0006 |
| **join** | a *governed request*; becky answers with a scoped, root-chained lease | 0006 |
| **remember** / **recall** | signed memory in; tokened retrieval out (escalates up the tree) | 0002 · 0004 |
| **think** | the plane authorizes + meters; your code executes; the plane never sees the prompt | 0016 |
| **diary** | every cycle is a signed RunRecord — which is *why the agent shows up in the Console* | 0005 |

```python
from orreth_agent import FieldClient, Chassis, RuleThink

client = FieldClient("http://127.0.0.1:4970", name="scout")
client.join()                               # a lease, minted by becky, chained to the pinned root
Chassis(client, RuleThink()).run("say hello to the universe")
# within one tick: scout is in the roster, a ship in the orrery, a line in the diary.
```

That is the whole adaptation surface. Wrap *any* existing agent — your LangChain chain, your
crew, your bespoke loop — by giving it a `FieldClient` and calling `diary()` at the end of each
turn. It joins the universe without changing how it thinks.

## Run one (30 seconds)

Bring the universe up — `start` now also opens **becky's join door** on the field (`:4502`),
so a freshly-started (or restarted) universe is joinable out of the box — then run a flavor:

```bash
# terminal 1 — the universe + its join door (from repo root)
scripts/dev.sh start             # docker up + becky on :4502; `status` shows "join door: OPEN"

# terminal 2 — a lifeforce agent (defaults to the field on :4502)
scripts/dev.sh agent 2 --forever         # convenience: runs flavor 02 into the field
# …or directly, from anywhere that can reach the floor:
cd agents/flavors/01-prototype
uv run --with pyyaml --with cryptography python run.py --field http://127.0.0.1:4502 --forever
```

Open the Console (`scripts/dev.sh window` prints the URL). Watch the agent arrive in the roster
and become a ship in the orrery. Point `--field` at a floor across the network and it works
identically — **an agent joins from anywhere.**

### When the universe restarts

A restart is transient, not a denial. `join()` **waits** for its floor to come back online (up
to `wait_for_floor`, default 30s) before asking for a lease, so an agent launched against a
restarting universe rejoins the moment the floor returns — no crash, no manual retry. If the
floor is up but no lease arrives, the error tells you becky's door is closed (`dev.sh start`
opens it). The two failure modes are named and distinct:

- `ConnectionError: … did not come online within 30s` → the **daemon** isn't running there.
- `JoinRefused: … no lease … becky's join door is not tending …` → the **worker** isn't running.

## The three flavors

- **[01 · Prototype](flavors/01-prototype/)** — the reusable lifeforce. The agent *is*
  `agent.yaml` (name, persona, objective, skills, cadence). Change the data, get a different
  agent; the chassis, the loop, and the governance never move. This is real-time agent
  allocation: spin up N identities from N YAMLs against one field.
- **[02 · LangGraph](flavors/02-langgraph/)** — the same governed loop drawn as an explicit,
  deterministic `StateGraph` (prepare → plan → execute → review → replan|park|persist). For
  teams who want to *see and audit* the graph, and who need the same inputs to trace the same
  path every time.
- **[03 · AgentField Sentinel](flavors/03-agentfield-sentinel/)** — an AgentField-style
  reasoner network (`@app.probe` decorators, parallel hunters, flat findings) that joins a
  floor and **adversarially confirms the universe defends its own governance** — clock
  monotonicity, signature integrity, grant enforcement, trust-root pinning, uniform refusal.
  vigil, the Warden, made joinable. Defensive self-testing; it detects and files, never enforces.

## Cognition: runs anywhere, gets smart on demand

`think(klass, prompt)` is injected, so the same agent runs two ways:

- **`RuleThink`** — deterministic, keyless. The floor of capability; runs on a laptop, a CI
  box, an edge device, with zero credentials. The plans are mechanical, but the agent is real.
- **`GovernedThink`** — real model calls through the plane (`pip install orreth-agent[governed]`).
  `/model/authorize` picks the model and debits the lease; you call it; `/model/meter`
  reconciles. Cost rolls up to the Console. The plane authorizes and meters; it never sees the
  prompt.

## Docker (modular, run-from-anywhere)

`Dockerfile` builds a minimal agent image. An agent is a client — it needs only network reach
to a floor, so it runs beside the universe, in another cluster, or on a partner's machine:

```bash
docker build -t orreth-agent -f agents/Dockerfile agents
docker run --rm --network host orreth-agent \
  flavors/01-prototype/run.py --field http://127.0.0.1:4970 --once
```

## Write your own

1. Copy `flavors/01-prototype/agent.yaml`, change the fields.
2. Add deterministic skills to `skills.py` (a skill is `(question, client) -> str`).
3. Run it. It joins, remembers, and appears. That is the whole ceremony.

See **[docs/design/0017 — the Lifeforce Agents](../docs/design/0017-the-lifeforce-agents.md)**
for the architecture and the design decisions.
