# Provenance ledger — `agents/`

> **Quarantine lifted — 2026-07-05.** This tree was built on branch
> `opus/lifeforce-agents` under quarantine (never pushed while unreviewed), reviewed
> line-by-line by Fable 5 (findings F1–F4 below, all fixed and live-verified), and
> merged to `main` on JB's green light (merge `5102ba9`). The protocol it pioneered is
> now the standing rule for every model — see `.claude/skills/orreth-covenant`.

## Why this file exists

On 2026-07-05 we confirmed the mechanism behind days of "silent model swaps":
**Fable 5's safeguards flag some content (broadly — including routine coding,
cybersecurity, and biology work) and auto-switch the runtime to Opus 4.8**, with a
console notice and a support link. The agent work — especially the AgentField-style
security/conformance flavor — trips that broad flag. Rather than fight it, JB chose to
**proceed on Opus 4.8 deliberately, with everything tagged**, so Fable 5 can review
every line once it's available again.

So: every file below carries a `# PROVENANCE:` banner naming its author-model, and this
ledger is the master map.

## Authorship map

| Area | File | Author model | Notes |
|---|---|---|---|
| SDK · crypto | `orreth-agent-sdk/orreth_agent/crypto.py` | **Fable 5** (16:09) | vendored Ed25519, byte-parity canonical JSON; `load_or_create` seed persistence (review fix F1) |
| SDK · client | `orreth-agent-sdk/orreth_agent/client.py` | **Fable 5** (16:09) | FieldClient: join/remember/recall/think/diary; persistent identity home (review fix F1) |
| SDK · chassis | `orreth-agent-sdk/orreth_agent/chassis.py` | **Fable 5** (16:09) | 0015 loop + RuleThink/GovernedThink; per-cycle cost fix (Fable) |
| SDK · init/pyproject | `orreth-agent-sdk/orreth_agent/__init__.py`, `pyproject.toml` | **Fable 5** | package surface |
| Join door (worker) | `../backend/conformance/console_worker.py` | **Opus 4.8** | becky grants root-chained lease on `kind:"join"`; restart-proof dedup + line-buffered log (Fable 5, review fix F3) |
| Named presence | `../backend/plane/crates/orrethd/src/main.rs` | **Opus 4.8** | `/presence` surfaces joined agent names; workforce rides the beat + subtree merge, restart-unique request ids (Fable 5, review fixes F2/F3) |
| Roster names (UI) | `../backend/plane/crates/orrethd/src/window.html` | **Fable 5** (16:09) | render `a.name` in roster/feed/spend; role chip shows home floor (F2) |
| Flavor 1 · prototype | `flavors/01-prototype/*` | **Opus 4.8** | agent.yaml-driven lifeforce |
| Flavor 2 · langgraph | `flavors/02-langgraph/*` | **Opus 4.8** | deterministic StateGraph |
| Flavor 3 · sentinel | `flavors/03-agentfield-sentinel/*` | **Opus 4.8** | AgentField-style conformance sentinel |
| Docs | `README.md`, `../docs/design/0017-*.md` | **Opus 4.8** | guides + dive |

### The Tool Farm (0018) — 2026-07-05, on main (no quarantine: Fable 5 authored)

| Area | File | Author model | Notes |
|---|---|---|---|
| Design | `../docs/design/0018-the-tool-farm.md` | **Fable 5** | services as identities with worldlines; lifecycle = the trust ladder's fourth application |
| Sim · farm | `../backend/conformance/orreth_sim/farm.py` | **Fable 5** | reference state machine; manifest hash pin; illegal moves refused |
| Sim · tests | `../backend/conformance/tests/test_farm.py` | **Fable 5** | lifecycle/worldline, rug-pull door (CVE-2025-54136 shape), decom→discredit→recall |
| Plane · farm | `../backend/plane/crates/orrethd/src/farm.rs` | **Fable 5** | registry + lifecycle legality + meter; rejoin hash check is plane-side |
| Plane · wiring | `../backend/plane/crates/orrethd/src/main.rs` | **Fable 5** | 5 `/farm/*` routes; farm rides the beat + rollup; egress hit enrichment (tags, honest `untrusted` fidelity) |
| Keeper | `../backend/conformance/console_worker.py` | **Fable 5** | charlotte: probe/attest/heartbeat/drop/rejoin/replant + worldline records; persistent resident seeds; gather routed through the Farm; all three floors tended |
| Console | `../backend/plane/crates/orrethd/src/window.html` | **Fable 5** | Farm tab (plant/approve/decom), orrery farm plots, worldline diamonds in the spacetime window, cohort-cut fix (the dead "add knowledge" repair), honest `submitAsk` |
| Demo · farm | `../backend/conformance/demo_farm.py` | **Fable 5** | the narrated reel: real remote MCP planted live + the rug-pull arc read off the worldline |
| Demo · index | `../scripts/demo.sh` | **Fable 5** | the growing demo reel (farm · life · spacetime · knowledge · chassis · model · window) |

## What Fable 5 should scrutinize hardest (Opus's own flags)

1. **The join door is open.** `FieldClient.join()` treats a lease as granted the moment
   the worker resolves the request, and the worker (becky) mints a lease for *whatever DID
   asks*. That is fine for a demo, but it is **not** the governed, HITL-gated join JB's
   vision implies. A real join should verify the requester controls the DID (a signed
   nonce challenge) and, on governed floors, hold for human approval (0012 queues).
2. **Crypto parity is load-bearing.** The SDK's `canonical()` must produce byte-identical
   output to the Rust plane's canonicalization forever, or signatures silently fail. There
   is a parity test, but Fable should confirm it covers non-ASCII + nested ordering.
3. **The sentinel probes the universe's own refusals.** It is defensive self-testing of
   JB's own governance (does retrieval refuse uniformly? does the clock reject backdating?).
   Confirm the framing and the skills stay strictly on the "verify my own invariants" side.
4. **RuleThink is a stub cognition.** It is deterministic and keyless by design (so an
   agent runs anywhere), but it is not "smart" — the plans it makes are mechanical. The
   governed path (GovernedThink → model plane) is the real mind; RuleThink is the floor.

## Fable 5 review findings — 2026-07-05

Live-repro review on JB's rig: repeated `dev.sh agent 2 --once`/`--forever` runs, a
universe docker restart underneath a running worker, and a full read of the diff against
`main`. Verdict: the join path works and crypto parity holds, but the **living-identity
half of the lifeforce story is unimplemented**, presence aggregation stops one floor
down, and the join door goes deaf after a daemon restart. All three are now fixed —
F3 in the first review pass, F1/F2 on JB's green light (2026-07-05, same day).

### F1 · No identity persistence — every run mints a new agent (all three flavors) — FIXED

`FieldClient.__init__` defaults to a fresh keypair (`client.py:39`), and no runner passes
one — `01-prototype/run.py:33`, `02-langgraph/run.py:45`,
`03-agentfield-sentinel/run.py:29`. The scribe (`client.py:42`) is likewise reborn every
process. Each `dev.sh agent …` invocation therefore creates a new did:key → new join
request → new lease → new "birth" memory → one more permanently idle ghost in the
roster, and the orrery's agent count only ever grows (`summary()` counts distinct DIDs
across RunRecords).

The mechanism exists and is even tested — `KeyPair(seed)` round-trips, and
`test_parity.py:58-61` asserts "seed persists the identity" — it is simply never wired.

**Fixed (Fable 5):** `KeyPair.load_or_create(path)` in `crypto.py` (0600 perms), and
`FieldClient` now defaults `home=~/.orreth/agents` — agent + scribe seeds persist under
`home/<name>/`, so every flavor gets a stable DID with zero flavor-code changes
(`home=None` keeps the ephemeral path for tests). A re-join by the same DID lands on the
same workforce row (the roster keys by DID), and the "birth" memory dedups naturally
(content-addressed id). Persisting the *lease* to skip the queue entirely stays future
work — re-joining through becky keeps the names map warm after daemon restarts.

### F2 · Workforce roster is floor-local — the universe Console never shows leased agents — FIXED

`/presence` builds its workforce list purely from RunRecords held on the answering node
(`main.rs:484-508`). Agents join and diary at the field (:4502); the universe Console
(:4500) reads its own empty runs, so its Workforce panel stays empty forever — while the
orrery, fed by `/topology`'s cascaded child beats, shows those same agents as ships. One
world, two contradicting pictures.

**Fixed (Fable 5):** the per-agent aggregation is factored into `local_workforce()`
(each entry now carries its floor's `scope`), `summary()` sends it up the beat, and
`/presence` merges its own roster with every descendant beat's — so the universe Console
shows the whole subtree's leased agents, and the roster finally agrees with the orrery.
The Console's role chip shows the agent's home floor (`f:prod`) instead of a generic
"workforce".

### F3 · becky goes deaf after a daemon restart — FIXED (Fable 5, this pass)

`requests_submit` issues sequential ids (`req-{len+1}`, `main.rs:591-599`) from an
in-memory queue. A docker restart wipes the queue, so the first new join is `req-1`
again — an id the still-running host worker's `seen` set already holds. Becky silently
skips every recycled id; agents time out with "becky's join door is not tending".
Compounding it, the worker's stdout was block-buffered under nohup, so `worker.log` sat
at 0 bytes and becky *looked* dead even while alive (observed live: running worker,
empty log).

**Fixed in `console_worker.py`:** dedup keyed by `(id, at)` — the submission timestamp
makes keys unique across daemon restarts — and stdout reconfigured line-buffered so the
log breathes. Becky also now `os.setsid()`s into her own session at startup: `dev.sh
start/restart` can linger after printing status (background-worker exit quirk), and a
Ctrl-C aimed at that lingering script used to SIGINT the whole process group — becky
included. Verified live: a worker now survives an INT that kills its entire launch group. **Daemon follow-up — also done (Fable 5, with JB's green light):** request
ids now carry the submission second (`req-{n}-{ts}`), unique across restarts, so no
consumer can be fooled by recycled ids. `/presence`'s names map still rebuilds from the
in-memory queue, but persistent identities re-join on their next run, which re-warms it.

### F4 · Core-integrity audit — what this branch actually touches

Full `git diff main...HEAD` reviewed. Exactly **four** pre-existing files are modified,
all matching this ledger's claims; everything else is net-new under `agents/` plus
design doc 0017.

| File | Change | Assessment |
|---|---|---|
| `backend/conformance/console_worker.py` | join door: becky mints root-chained leases | as declared; F3 fix now also lands here |
| `backend/plane/crates/orrethd/src/main.rs` | +6 lines in `/presence` only (names map) | display-only; names come from **unsigned** join requests, so they are requester-chosen (consistent with flag 1) |
| `backend/plane/crates/orrethd/src/window.html` | 3 lines rendering `a.name` in roster/feed/spend | cosmetic |
| `scripts/dev.sh` | joindoor, `agent` subcommand, door status line | dev rig only |

**Untouched:** the `orreth-node`, `orreth-store`, and crypto crates, `contracts/`,
`orreth_sim` internals, `infrastructure/compose.yaml`. The governed core is unaltered.

### Status of Opus's own flags

1. **Open join door** — confirmed real: becky leases any DID that asks, and roster names
   ride unsigned requests. Acceptable for the demo floor only; a nonce challenge plus
   0012 HITL gating is required before any governed floor.
2. **Crypto parity** — verified: the cases cover key order, non-ASCII, nesting, unicode,
   and a cross-verifier signature; suite run during this review, **10/10 green**.
3. **Sentinel framing** — read in full: every probe *attempts* a violation and passes
   only when the universe refuses it; it detects and files, never enforces. Framing holds.
4. **RuleThink stub** — acknowledged; fine as the keyless floor, `GovernedThink` is the mind.
