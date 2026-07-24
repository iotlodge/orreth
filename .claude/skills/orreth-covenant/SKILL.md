---
name: orreth-covenant
description: MANDATORY before writing or modifying ANY code in the Orreth repo (agents/, backend/, contracts/, scripts/, docs/design/). The non-negotiable invariants of the Universe / identity / governance vision, plus the provenance-and-quarantine protocol for non-Fable models. Invoke at the START of any Orreth coding task, before the first edit.
---

# The Orreth Covenant — hard rules for every model that codes here

The vision lives in `docs/design/0000–0017` and `docs/vision/`. Those documents are the
constitution; this card is the enforcement summary. It exists because drift has already
happened once: a 2026-07-05 pass built lifeforce agents whose identities died with the
process — mayflies in a universe designed for living things. Review caught it
(`agents/PROVENANCE.md`, findings F1–F4). Do not make Fable 5 catch it twice.

## The rules — non-negotiable

1. **A keypair is a self, and a self survives the process** (0002 · 0006).
   Every lifeforce agent persists its seeds — agent *and* scribe — under
   `~/.orreth/agents/<name>/` (the `FieldClient` default). The same agent re-joins across
   runs. A new DID per run is a defect, never a feature. Ephemeral identity
   (`home=None`) is for tests only.

2. **Nothing grades its own yardstick** (0005).
   RunRecords are scribe-authored, `author ≠ agent`, signed. Never let an agent
   self-attest an outcome; never weaken `record_run`'s checks.

3. **Joining is a governed request** (0006 · 0012).
   The join queue is human-visible; becky alone mints leases, chained to the pinned
   root. Never mint tokens client-side, never bypass the queue, never grant a broader
   scope than was asked.

4. **Refusal wears one face** (0002 §4).
   Authz-miss, budget-miss, missing record — identical error shape, always. Never add a
   distinguishable failure path to `/retrieve` or its kin; a prober must learn nothing.

5. **The plane authorizes and meters; it never sees the prompt** (0016).
   Cognition executes on the agent's side. Never route prompt content through orrethd.
   And the meter is universal (0019): every resident's cognition goes through the
   gateway — an organ that thinks off-meter is drift.

6. **Canonical bytes are the contract** (0000 §3).
   Sorted keys, compact separators, ensure_ascii — byte-identical across the SDK, the
   Python sim, and the Rust plane. Any touch to canonicalization or signing runs
   `agents/orreth-agent-sdk/tests/test_parity.py` green before it lands.

7. **One world, one picture.**
   Roster, orrery, rollup, and Console must agree. Anything a floor shows about the
   world below comes from the heartbeat chain (`/hello` beats cascading up), never from
   invention. If a view can disagree with another view, the change is wrong.

8. **Lived time is monotone** (0004).
   The universe rejects backdated lived memory. Keep it that way.

9. **The core is sacred.**
   `backend/plane/crates/orreth-node`, `orreth-store`, the crypto crates, and
   `contracts/v0` change only with JB's explicit, stated approval for that specific
   change. "It would be convenient" is not approval.

10. **Provenance or nothing.**
    Every new source file opens with a `# PROVENANCE:` banner naming its author model;
    `agents/PROVENANCE.md` is the ledger and must be updated in the same change. Work by
    any model other than Fable 5 goes to a quarantined branch (`opus/...`), commits
    tagged `[<MODEL> · QUARANTINED]`, is **never pushed to origin**, and awaits Fable 5 +
    JB review before merging. Never claim another model's authorship — JB verifies
    attribution against audit logs, and false records get corrected publicly.

## Before you finish — the drift checklist

- Do identities persist and re-join as the same self?
- Does anything self-attest? Are refusals still uniform?
- Crypto or canonicalization touched → is `test_parity.py` green?
- Does roster == orrery == rollup, at every floor?
- PROVENANCE banner on new files, ledger updated?
- Right branch? Quarantined work unpushed?
- README / design docs updated where behavior changed?
- Dive closed WHOLE (built + proven)? → `VERSION` bumped to that dive's era **in the
  closing commit** (0.39 for 0039). `dev.sh` derives the console's version whisper from
  it; a stale era means the glass lies about what world it is. Caught out-of-band three
  times before this line existed (last: 2026-07-24, v0.35 worn by a forty-dive world).

## When unsure

Read the design doc the rule cites. Still unsure → ask JB (AskUserQuestion) with the
outcomes of each option spelled out — JB locks decisions, and the mechanism lands with
the lock. Do not invent new architecture to route around a question.
