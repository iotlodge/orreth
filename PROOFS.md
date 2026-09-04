# The Proofs

*The era declared in [ADR 0001](docs/decisions/0001-the-proofs-era.md), 2026-09-04: from here on
out, the work is proofs.*

## What a proof is

Sixty-five design dives built the kernel: identity that survives the process, one signed log,
governed admission, metered minds, gates where consequence waits for a human. The standing risk
after a foundation season is speculative surface — machinery built because it *could* be, not
because a purpose demanded it.

A **proof** is the antidote: a purpose world installed on the kernel and exercised end to end.
Each proof matures the kernel by *using* it, and verifies it the only way that counts — against
a real purpose, walked by a human, with the receipts on the record.

## The discipline

1. **Proofs consume the published seams.** `pip install orreth-agent` · `docker pull
   ghcr.io/iotlodge/orrethd` · the [book's](https://docs.orreth.ai) walked examples. Where a
   proof is forced back inside the repository, that dependence is named honestly — and becomes
   evidence that a seam needs cutting.
2. **Kernel and firmware changes land only for wounds a proof actually hit.** "It would be a
   nice capability" is not a wound. The demand a proof makes is the evidence the change was real
   (covenant rule 12).
3. **Every proof keeps an honest register** of what its walk demanded, what was proven, what
   stayed partial, and what was parked — the same standard the
   [honest boundary](docs/design/the-honest-boundary.md) holds the kernel itself to.
4. **The razor stands throughout:** what you can change in production is purpose; what takes a
   release is firmware.

## The proof worlds

Six proof worlds are seeded as private repositories — each opens publicly as it earns a
stranger's read. They share one architecture: a purpose world on the same kernel, governed by
the same resident firmware, with no kernel change unless a wound demands it.

| Proof | What it proves |
|---|---|
| **orreth-body** | Three $15 computers become one body — the zero-new-code proof that Orreth's laws run an embodied machine: joints as persistent selves, admission through a human gate, honest dormancy when a limb dies. |
| **orreth-fleet** | A building that knows itself — every robot an Orreth floor under one site universe; fleet-scale memory with provenance, where a lesson learned by one machine is a *cited* lesson when another retrieves it. |
| **orreth-blackbox** | Flight-recorder provenance for certifiable robots — every actuation leased, every anomaly witnessed and signed by a seat that is never the actor; an incident record an auditor can actually trust. |
| **orreth-genuine** | Genuine-parts attestation — a replacement part *asks to join*; a counterfeit knocks and is refused with one face, learning nothing; supply-chain trust as a human-legible gate. |
| **orreth-ota** | Governed firmware updates with honest rollback — publish, swap, caught, walked back; every step a signed deed, the human gate in the middle, history never rewritten. |
| **orreth-fuel** | Energy as a governed budget — leases denominated in watt-hours, starvation as the enforcement mechanism, and the emergency stop as a first-class recorded act. |

These six wear one lens — the kernel as the trust plane around embodied machines — and they are
**held** deliberately: the value across that space deserves its own season.

## The first proof: orreth-EnterpriseRAG

The program opens with **orreth-EnterpriseRAG** — enterprise retrieval built as a living
capability on the kernel: every mainstream document format (and zip archives of them), cloud and
on-premise data sources onboarded through the Tool Farm as governed identities, full human
dialog, and the kernel's own Librarian retrieving the capability's answers — *through kernel*,
demonstrated. Its second proof rides in the same world: **Orreth as the API of the capability**
— application integration with a governed prompt-in, answer-out surface, guardrails included.
Unlike the held six, this proof is *expected* to upgrade the kernel's own RAG architecture —
every change paid as a design dive, citing the requirement that demanded it. In progress,
private, and it opens when it earns a stranger's read.

---

*The kernel matures by being used. Watch it live at [demo.orreth.ai](https://demo.orreth.ai);
read how it works in [the book](https://docs.orreth.ai) and the
[README's anatomy](README.md#how-the-kernel-works--the-anatomy-in-six-pictures).*
