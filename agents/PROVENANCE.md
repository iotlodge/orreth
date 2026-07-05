# Provenance ledger — `agents/`

> **Quarantined for review.** This tree was built on branch `opus/lifeforce-agents`
> and is **NOT pushed to origin**. It awaits review by Fable 5 and JB before it
> merges to `main` or ships anywhere. — requested by JB, 2026-07-05.

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
| SDK · crypto | `orreth-agent-sdk/orreth_agent/crypto.py` | **Fable 5** (16:09) | vendored Ed25519, byte-parity canonical JSON |
| SDK · client | `orreth-agent-sdk/orreth_agent/client.py` | **Fable 5** (16:09) | FieldClient: join/remember/recall/think/diary |
| SDK · chassis | `orreth-agent-sdk/orreth_agent/chassis.py` | **Fable 5** (16:09) | 0015 loop + RuleThink/GovernedThink; per-cycle cost fix (Fable) |
| SDK · init/pyproject | `orreth-agent-sdk/orreth_agent/__init__.py`, `pyproject.toml` | **Fable 5** | package surface |
| Join door (worker) | `../backend/conformance/console_worker.py` | **Opus 4.8** | becky grants root-chained lease on `kind:"join"` |
| Named presence | `../backend/plane/crates/orrethd/src/main.rs` | **Opus 4.8** | `/presence` surfaces joined agent names |
| Roster names (UI) | `../backend/plane/crates/orrethd/src/window.html` | **Fable 5** (16:09) | render `a.name` in roster/feed/spend |
| Flavor 1 · prototype | `flavors/01-prototype/*` | **Opus 4.8** | agent.yaml-driven lifeforce |
| Flavor 2 · langgraph | `flavors/02-langgraph/*` | **Opus 4.8** | deterministic StateGraph |
| Flavor 3 · sentinel | `flavors/03-agentfield-sentinel/*` | **Opus 4.8** | AgentField-style conformance sentinel |
| Docs | `README.md`, `../docs/design/0017-*.md` | **Opus 4.8** | guides + dive |

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
