# Governed Human Oversight
### Humans are principals too — entitlement is scoped, directional, and audited

*Private vision artifact. Captured 2026-06-30 from JB's governance insight. Companion to
`FUTURE-the-orreth.md` and `the-spacetime-window.md` (this is the observatory-vs-panopticon line, aimed at humans).*

> Since this is a tiered model, humans looking in are **authorized per entitlement**. Depending on the
> human's entitlement, the Universe controls whether they can see **up**, **across**, or only **down/within** —
> and how much **control** they may apply. That's more human command over the Universe. It's a feature —
> and yes, a powerful one, which is exactly why it must be governed. — JB

---

## The insight

Orreth's tiers aren't only for agents. **Humans look in too** — operators, compliance officers, auditors,
boards, regulators, the conductor. The question a governed system has to answer is not "can a human see the
system," but **"which human, into which layer, in which direction, to do what — and who authorized it?"**

The answer: a human is a **principal in the same identity + capability model** as an agent, with an
**entitlement** that the Universe governs. Nothing about human access is special-cased or ungoverned. The
watchers are watched.

---

## Humans are principals — even the watchers are in the memory

- A human has an **identity** (a DID via becky), an **entitlement** (a capability grant), and — critically —
  **every action they take is Sourced + Verified + logged** as a signed access record, exactly like an agent's.
- So the audit trail includes the humans: *who looked into which layer, when, under which entitlement, and what
  they changed.* **This is the answer to "bad things could be done":** the power is real, and so is the accountability.

---

## Entitlement is *directional*

Visibility isn't just "which tier" — it's **which direction from the human's seat**:

| Direction | What it grants | Default |
|---|---|---|
| **Down / within** | see (and, if control-entitled, act on) the layer you govern and everything beneath it | **granted** by role |
| **Up** | see toward the apex — higher tiers, the Universe's own state | **explicit grant** (rare, powerful) |
| **Across** | see into sibling tenants / other branches | **explicit, human-gated grant** — the *dangerous* one (cross-tenant) |

This is the agent read-path authorization (`0002`), applied to human principals: **down/within by default; up and
across must be granted.** Tenant isolation holds for humans exactly as it does for agents — a human in Ecosystem A
cannot see Ecosystem B's private state without a governed cross-tenant grant.

---

## Visibility is separate from control

Two distinct entitlements, never conflated:

- **Read-entitlement** — may *see* a layer (a scoped, audited window).
- **Control-entitlement** — may *act* on it: set policy, approve an escalation, promote a standard, authorize a
  transfer, invoke erasure.

An auditor may have deep read-entitlement and *zero* control. An operator may control their own Ecosystem but
have no read-entitlement up or across. Separating the two is what lets you hand a regulator total transparency
into their jurisdiction **without** handing them a lever.

---

## The dual-use reckoning (the panopticon line, aimed at humans)

Concentrated human visibility + control is genuinely powerful and genuinely dangerous — the same coin as the
spacetime window. Naming it plainly, and the four things that keep it a control surface rather than a tyranny:

1. **Every human action is audited** — Sourced, Verified, logged. No unlogged omniscience.
2. **Multi-party authorization for apex actions** — the most sensitive moves (universe-wide reads, cross-tenant
   grants, mass policy changes, erasure) require **more than one human co-sign.** No single god.
3. **Even the apex human is constrained** — tenant isolation and consent floors bind *everyone*; the conductor is
   entitled and audited, not exempt.
4. **The entitlement model is itself transparent and governed** — who can grant what, to whom, is a first-class,
   auditable policy, not a back room.

> The power is real; so is the accountability. That pairing is what turns "a live window into everything" into
> something a regulator will license instead of fear.

---

## Why this is a feature — not a liability

Governed, scoped, audited human oversight is a **product capability**, and a differentiator:

- **Compliance-grade transparency** — a regulator or auditor gets a *scoped, entitled, audited* window into exactly
  their jurisdiction. Not everything (that would be a leak); not nothing (that would be opacity). Exactly their slice.
- **Legitimate command** — the conductor keeps a real hand on the wheel across a system no human could watch by hand,
  *and* every touch of that wheel is on the record.
- **This is how the spacetime window gets sold** — the reason a buyer trusts a live cross-section of their world is
  that human access to it is entitled, directional, separated (read vs control), and audited end to end.

---

## How it rests on the primitives we already have

- **Principal + capability** — a human is an identity with a capability token; entitlement = a scoped, directional grant.
- **Retrieval authorization (`0002`, the #1 security surface)** — human reads flow through the *same* own/up/across gate,
  with tenant isolation and per-read access records.
- **The Governance Gate / HITL** — human control actions (approve, promote, transfer, erase) are the existing gate,
  now generalized into a full control-entitlement model with multi-party authorization for apex actions.
- **Memory as the audit substrate** — human actions are `MemoryRecord`s too: Sourced + Verified, append-only, never lost.

---

*Humans conduct; agents perform — and now the conducting itself is scoped, directional, and on the record. The
telescope has an operator's log, and the operator is in it too.* 🥃
