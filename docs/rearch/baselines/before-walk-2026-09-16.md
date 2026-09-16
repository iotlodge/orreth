# Before-walk #1 — the old glass (PARTIAL)

**Status: PARTIAL (P0 sp3, 2026-09-16).** The Playwright's first walk
against the old glass (v0.72.520) ended early — the agent hit the
account's session spend limit mid-walk. What it observed before dying is
recorded; the remainder re-walks when budget allows (nothing downstream
blocks on it — the before-record only needs the old rig, revivable any
time).

## Confirmed findings

| Spec | Verdict | What the Playwright saw |
|---|---|---|
| **SPEC-ESC-01** | **FAIL** (confirmed) | Opened becky's drawer, pressed Escape — the drawer stayed open. The one-keystroke rollback bar fails on the old glass, exactly as the charter expected. |

## Instrument-corroborated (not browser-walked — M0's numbers)

| Spec | Reading |
|---|---|
| SPEC-TOOLS-01 / SPEC-SOFT-01 | The ask path measured p50 **120 s** with 2 of 6 asks never answered (M0) — no conversational bar survives that, before even reaching the tools question. Browser confirmation pending re-walk. |
| SPEC-JOURNEY-01 | The glass's wait line says only "the router is reading your ask…" — no who, no scope, no journey (known from the glass's own source; visual confirmation pending). |

## Context the walk ran in

The M0 measurement was queuing asks on the same worker during the walk —
contention that is itself the documented disease. The walk's waits are
therefore honest worst-cases of today's world, not artifacts.

## Remaining

Re-walk SPEC-FEEL-01, SPEC-TOOLS-01 (with the GIF for the article
carousel), SPEC-JOURNEY-01, SPEC-SOFT-01, and a second SPEC-ESC-01 panel
— one Playwright session, old rig revived (`infrastructure/` compose +
the host worker).
