# M0 — The Old World, Measured (the comparison contract)

**Status: BANKED (P0 sp2, measured live 2026-09-16).** The polling rig
(v0.72.520, 20 floors, the host worker) measured exactly as it runs,
without changing it — per SOL's M0 method. These are the numbers every
later proof is compared against. Raw data:
`spine/baseline/m0-results.json`; instrument:
`spine/baseline/measure_m0.py` (stdlib-only, re-runnable).

## What one poll costs (the unit the worker pays per floor every 2 s)

20 floors alive. The `/requests` door returns the WHOLE retained queue
every time:

| Floor | Latency | Bytes per poll | Rows retained |
|---|---:|---:|---:|
| :4500 `u:demo` (the universe) | 142.3 ms | **3,699,740 B** | 2,684 |
| :4520 `e:desk/f:charles` | 45.1 ms | 424,366 B | 400 |
| :4502 `e:cloud/f:prod` | 57.0 ms | 359,226 B | 363 |
| 17 other floors (median) | ~20 ms | ~57 kB | ~107 |

The universe's queue alone is **3.7 MB per fetch** — and the worker,
the glass, and every waiting SDK client each re-download it on every
poll. Retained history makes idle work grow with age, not with work.

## The ask walk — the human's own path

Six asks submitted exactly as the glass submits them (POST `/requests`,
then poll the whole queue once a second), sequential, on `:4502`:

| Ask | Outcome | Wait | Whole-queue polls | Bytes read just to wait |
|---|---|---:|---:|---:|
| 1 | done | 110.1 s | 106 | 38.1 MB |
| 2 | done | 222.3 s | 209 | 75.6 MB |
| 3 | **timeout** | >300 s | 260 | 94.6 MB |
| 4 | done | 120.0 s | 114 | 41.5 MB |
| 5 | **timeout** | >300 s | 284 | 104.5 MB |
| 6 | done | 57.8 s | 52 | 19.2 MB |

**Answered 4 of 6 · p50 120 s · worst answered 222 s · two asks never
answered within five minutes · 373 MB downloaded across six waits.**
One human, one conversation, no load. This corroborates the operate
room's own pre-halt reading (naive p50 1.3 s / p95 17.5 s measured at
the retrieval layer alone — the queue wait above it is 100× worse).

## The idle-load ladder (arithmetic projection from measured unit costs)

The worker pays 1 poll + 1 pulse per floor per 2 s even when nothing is
happening:

| Floors | Idle requests/s | Idle bandwidth | Worker-threads consumed by polling alone |
|---:|---:|---:|---:|
| 26 (today's shape) | 26 | 0.74 MB/s | 0.3 |
| 110 | 110 | 3.2 MB/s | 1.2 |
| 1,100 | 1,100 | 31.5 MB/s | 11.7 |
| 10,100 | 10,100 | **289 MB/s** | 107.8 |

A projection, not a benchmark — but the shape is structural: idle cost
is proportional to floors × retained history, unrelated to actual work.

## The comparison contract (what the new world must beat)

| Moment | Old world, measured | The bar (0002/0003, locked) |
|---|---:|---:|
| Ask submitted → answer begins | p50 120 s, 33% never | first token < 1 s |
| Work dispatch | 2 s poll floor (best case) | invocation p99 < 1 s (spine sp1 measured 16 ms) |
| Cost of waiting | ~360 kB/s per waiting client | one push notice (< 1 kB) |
| Idle transport cost | grows with floors × history | independent of both |
| Completion notice | none — the client must hunt | soft notice < 1 s after commit |

The spine's first breath (sp1) already moves a message through the
invocation rail in **16 ms** — the old world's *best-case* dispatch
latency is 125× slower, and its observed ask path is four orders of
magnitude off the locked bar.
