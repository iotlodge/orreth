<!-- PROVENANCE: authored by Opus 4.8 (2026-07-05), pending Fable 5 review — see agents/PROVENANCE.md -->
# Flavor 2 — the LangGraph agent

The same governed loop as Flavor 1, drawn as an explicit `StateGraph` you can read and audit
edge by edge. Deterministic by default — the nodes reason with rules, not a model — so the
same inputs trace the same path through the graph every time.

```bash
pip install -r requirements.txt        # langgraph + cryptography
python run.py --field http://127.0.0.1:4970 --once
python run.py --field http://127.0.0.1:4970 --forever
```

## The graph

```
prepare ─▶ plan ─▶ execute ─▶ review ─┬─(objective met)──▶ persist ─▶ END
                     ▲                 ├─(cycles remain)───▶ replan ─▶ plan
                     └─────────────────┘ └─(breaker)────────▶ park ───▶ END
```

- **prepare** — recall this identity's memory through the window
- **plan** — deterministic: one observation per bound skill, then a reason step
- **execute** — the nucleus, running the chosen observations
- **review** — the critic; writes a diary RunRecord every cycle
- **route** — `persist` (remember the answer), `replan` (next cycle), or `park` (fuel)

Every node speaks to the universe through the SDK's `FieldClient`, so this agent joins,
remembers, and appears in the Console exactly like any other — it just thinks in a shape you
can put under glass. Swap the deterministic nodes for `GovernedThink` calls and the same graph
becomes a governed-model agent without changing its topology.
