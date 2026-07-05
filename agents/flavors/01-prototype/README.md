<!-- PROVENANCE: authored by Opus 4.8 (2026-07-05), pending Fable 5 review — see agents/PROVENANCE.md -->
# Flavor 1 — the Prototype lifeforce

The reusable one. The agent **is** `agent.yaml`; `run.py` only wires it to the SDK.
Change the data, get a new agent — the chassis, the loop, and the governance never move.

```bash
uv run --with pyyaml --with cryptography python run.py --field http://127.0.0.1:4970 --once
uv run --with pyyaml --with cryptography python run.py --field http://127.0.0.1:4970 --forever
uv run --with pyyaml --with cryptography python run.py --agent other.yaml --field <url> --forever
```

## The loop (0015)

`prepare` (recall what this identity already lived) → `plan` (the minimum observations) →
**nucleus** (runs *only* what the planner asked, in parallel; deterministic skills answer free,
`reason` goes through the governed door) → `critic` (done, or what's missing) → `replan` →
until the objective is met or the breaker **parks** the intent as a knowledge-acquisition
assignment. Every cycle is a signed diary entry.

## Real-time agent allocation

The point of data-over-code: N agents from N YAMLs against one field, spun up and down on
demand. `scout.yaml`, `auditor.yaml`, `greeter.yaml` — same binary, same governance, different
lives. That is the "lifeforce of an Identity" — spawn, join the threads, do the work, remember.

## agent.yaml

| field | meaning |
|---|---|
| `name`, `role` | who joins, and how it appears in the roster |
| `persona` | the costume the cognition wears |
| `objective` | the intent the loop pursues each cycle |
| `cognition` | `rule` (keyless, anywhere) or `governed` (metered model plane) |
| `skills` | deterministic skills to bind (defined in `skills.py`) |
| `cadence_seconds` | rest between loops in `--forever` mode |
| `max_cycles`, `max_obs` | the loop's bounds — never wander, never stall |
