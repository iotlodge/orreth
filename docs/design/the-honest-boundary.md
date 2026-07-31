# The Honest Boundary — the standing register of claims, proofs, and parks

<!-- PROVENANCE: Fable 5 (claude-fable-5) — seeded 2026-07-26 from the outside
     poster's §12 (ORRETH_POSTER.md, Sol 5.6's evidence-based reading), at JB's
     word: "these sound like solid ways to help prove claims of orreth when we
     start creating universes." -->

Orreth's credibility is not that everything is built — it is that the line
between proven and promised is **written down, witnessed, and kept current**.
This register is that line, in one place. Every claim an outsider might test
gets a row: what stands proven and *where the evidence lives*, what is
reference-proven or deliberately partial, and what is designed but parked
behind a named gate. When a universe is created for someone else, this page is
what we hand them before the demo.

Maintenance law: **a dive that moves a row updates this page in its closing
commit** — a register that lags is worse than no register, because it lies
with confidence.

## 1. Proven, with the evidence named

| Claim | Evidence |
|---|---|
| One recursive binary runs any tier; profiles supply behavior | the dev rig: universe :4500 · eco :4501 · field :4502 + shipyard-grown floors, one `orrethd` |
| Python reference and Rust plane agree byte-for-byte on canonical content | `agents/orreth-agent-sdk/tests/test_parity.py` (10/10) + the drill's parity handshake (`demo.sh drift`) |
| The full sim model is executable and conformance-held | `backend/conformance/tests/` — 274 tests green (2026-07-30) |
| Identity survives the process; joining is governed; leases chain to a pinned root | 0002/0006/0012 machinery + covenant rules 1/3; the join door on the reel |
| Refusal wears one face; the plane meters but never sees the prompt | covenant rules 4/5; uniform-refusal fixtures in the conformance suite |
| The Canon has a fingerprint on a chain; drift stages, never enacts; the revert is a sibling | 0041 live proof (req-326) + `orreth_sim/epoch.py` / `tests/test_epoch.py` (THE SILENCE suite-held) + `demo.sh drift` repeatable; universe-scope lag reconciles after the roll-up cut (`_reconcile(UNIVERSE_SCOPE)`, verified in-code 2026-07-30 — the 0041 road's "no port to stage at" gap closed with the road-step-2 work) |
| No external consequence is complete on the executor's word alone | 0042 live proof: https://demo.orreth.ai/deeds/first-deed.json — published, tampered, caught, walked back, restored; the artifact carries its own story |
| Improvement is proposed, never self-adopted; promotions keep lineage | 0031 lanes + tournament promotion receipts (req-287); orphan-lineage fix 2026-07-26 (`proposal_ref` on the card) |
| Every governed thought — and every refusal — lands on a flight recorder: latency, model, tokens, cost, taxonomy; series distill with MEASURED loss under a declared retention law, log-truth rebuildable, instrument readings labeled as such | 0043 sp1 (2026-07-30): `orreth_sim/observatory.py` + `tests/test_observatory.py` (12 tests); live: charlotte's voiced reply put a real `no-local-key` refusal AND the successful thought (301 tok · 2447 ms) on `~/.orreth/observatory/flight.jsonl` on its first flight |
| Completed work is assayed by another floor's mind — verdicts signed author ≠ executor, degradations stage as cards wearing no levers, and the examiner's own cost is metered under its own DID (pinned: never a silently cheaper judge) | 0043 sp2 (2026-07-30): `orreth_sim/vera.py` + `tests/test_vera.py` (8 tests); live: sonnet-5 (f:prod's stable) judged 13 real completed works — mean 0.14, correctly measuring the deterministic-scaffold outcomes this register already named in prose — a degradation card staged pending at the gate, and vera's parlor voice priced her own watching: 7,239 tokens, $0.02131, under her DID |
| The universe is VISIBLE measured, not claimed: an instrument room renders every panel with its tier declared (log-truth vs "instrument reading, not testimony"), the watcher's own pulse is first-class (a dark recorder turns the room dark loudly, never silently), and gate-wait ages surface how long consequence has waited for a human | 0043 sp3 (2026-07-30): the Console's 🔭 Observatory tab (`window.html`) + the worker's `/observatory` door (`compose_observatory`); proven in Chrome in both lights; the first live render surfaced a purge waiting 19d 17h at its gate — invisible before the panel existed. The standing gap register: `0043-the-observatory.md` §11 (found → written → homed) |
| A/B testing where each arm is a cryptographically named machine and the rollout is a signed constitutional act: the arm IS the floor's fingerprint with the variant as head; the split waits for a human and assigns deterministically; standings ride the log join; the conclusion is a promotion card whose adoption names the variant AND the experiment, the loser kept on the shelf | 0043 sp4 (2026-07-30): `orreth_sim/experiment.py` + `tests/test_experiment.py` (7 tests); PROVEN LIVE WHOLE on the seven rows — routing-ab (router vs hybrid): split opened by a glass click, 5 real asks wore their arms, sonnet-5 judged each under vera's declared daily ceiling, concluded at min-2, adopted by a glass click with full lineage (`adopted_from` + `derived_from` = [variant, declaration]) — and the epoch beat cut the machine's new name within the minute, quiet behind the word. The dial itself turned glance→assay as a governed staged act the same night |

## 2. Reference-proven or intentionally partial (from the poster's §12, now ours)

| Boundary | Where it stands | The gate that moves it |
|---|---|---|
| Several cognition paths are deterministic scaffolds or simulated judges; the plane correctly authorizes and meters while execution stays cognition-side | intentional v0 posture; the LIVE judge exists (mentee haiku · judge sonnet, another floor's mind) but falls back to the honestly-labeled sim judge when ground is thin | widen live-judge coverage; keep the fallback labeled |
| The wire objective fingertip proves choreography + receipts more strongly than open-ended autonomous work | true; the walks are real but the flows are composed | harder, less-scripted Objectives through the fingertip, receipts unchanged |
| Request-status transitions are persisted but unsigned — signer-registry work unfinished | named in the worker itself ("by the human seat (v0 — unsigned until 0012's registry)") | 0012 registry build |
| Embedder and projections degrade honestly when unavailable; production-scale rebuild unproven | pgvector projection live (0022 Phase 2); purge reaches the projection | a rebuild drill: drop a projection, rebuild from the log, diff |
| The dev rig proves the institution on one machine; federation, hosted custody, DR, multi-tenant need their own operational evidence | honest; nothing pretends otherwise | 0013 handshake + custodian tier + an operational runbook with receipts |
| Write-time re-hash: orreth-node trusts the author-signed id at ingest, never recomputes hash(body) | OPEN rule-9 question, parked in `../decisions/` | revisit BEFORE 0013 or any external ingestion door |

## 3. Designed or deliberately parked (each behind a named gate)

| Parked | Design home | Gate |
|---|---|---|
| Hosted Custodian tier; blindness/BYOK/split-key proof on production infrastructure | 0011/0013 | the hosting decision + a partner's real custody need |
| Federation and transport beyond parent-HTTP dev topology | 0013 | rule-9 re-hash decision first, then the handshake dive |
| Class-allocated storage provisioned from the Canon's retention/RTO/RPO map | 0039 (the Chronicle & the Canon) + allen's charter | the storage-map spoonful, allen provisions |
| Live-judge mentor/mentee graduation across real model tiers at sustained scale | 0040-era graduation pipeline (first graduation is a receipt) | sustained-scale runs with cost receipts |
| The Faculty package + Agent Lab | 0040, triaged and reserved | **JB's stamp: built only when Orreth is "stamped ready to test it"** |
| Dynamic "missing capability → gather → crystallize → canary → serve" as a general product capability | 0028/0031/0032 prove the organs separately | a dive that runs the whole loop on an arbitrary flow |
| Long-duration human-gate ergonomics, operational quorum, memory-metabolism tuning at scale | scattered (0030 gates · 0033 dials) | the playing phase, with real universes |

## 4. Shelf note

The poster itself stays verbatim in `../outside/` (nothing there is canon).
This register is the canon-side absorption of its §12 — the outside mind's
inventory, adopted as our own proof obligations. Sections 1–3 above supersede
memory of "what's honest" scattered across dive docs: when in doubt, a claim
not on this page with evidence named is a claim we do not make.
