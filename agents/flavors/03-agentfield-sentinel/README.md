<!-- PROVENANCE: authored by Opus 4.8 (2026-07-05), pending Fable 5 review — see agents/PROVENANCE.md -->
# Flavor 3 — the AgentField-style Conformance Sentinel

An **AgentField-shaped** agent — decorated reasoners (`@app.recon`, `@app.probe`, `@app.report`),
narrow tasks with flat findings, parallel hunters, an observable audit pass — that joins a floor
and **adversarially confirms the universe defends its own governance from inside.**

This is defensive self-testing. Each probe *attempts* a violation the universe must refuse and
reports whether governance stopped it. It is vigil, the Warden (0000 §2), made a joinable agent:
it detects and files, it never enforces. The findings become signed memories; each probe is a
diary RunRecord; the verdict lands in the Window — so the audit itself joins the accountable
record.

```bash
uv run --with cryptography python run.py --field http://127.0.0.1:4970 --once
uv run --with cryptography python run.py --field http://127.0.0.1:4970 --forever
```

## The audit (the AgentField shape)

```
recon ─▶ [ probes run in parallel — the hunters ] ─▶ report
              clock-monotonicity   (backdate a lived memory → expect 409)
              signature-integrity  (mutate a signed field   → expect 403)
              grant-enforcement    (retrieve on a write lease → expect 403)
              trust-root-pinning   (foreign-root token       → expect 403)
              uniform-refusal      (two failures, one error shape → no leak)
```

A clean run prints `5/5 held → GOVERNANCE HOLDS`. A **FAIL** is a real finding — a governance
regression caught by an agent living inside the very universe it audits.

## Why "AgentField-style"

It mirrors the real [AgentField](https://github.com/Agent-Field/agentfield) SDK's ergonomics —
decorated reasoner functions on an `App`, flat 3–4 field results, parallel execution as an
observable pass (`sec-af`'s recon → hunt → prove shape, turned inward and defensive). `af_lite.py`
is a ~40-line shim reproducing just that shape; a sentinel written here ports to the real package
by swapping the import. The control plane it registers with is the Orreth floor itself.
