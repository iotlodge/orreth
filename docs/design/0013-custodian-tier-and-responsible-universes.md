# 0013 — The Custodian Tier & Responsible-Universe Architecture

*Design draft for review — the dual-use reckoning, made structural. Prompted by JB's 2026-07-01 discussion:
"this is both AWESOME and SCARY." Fable owns the design; JB owns the vision and the ethical intent. **Open
decisions** flagged at the end. Not legal advice — the legal-process and content-obligation parts named here
need real trust-and-safety and legal counsel before launch; this spec makes the architecture ready for them.*

---

## Why this exists (named plainly)

Orreth lets anyone build a **secure, scoped, identity-aware world** — an agentic workforce you tune and govern,
with a window that can occupy any point in its spacetime. Every legitimate use (fleet management, running a
company's whole digital lifecycle, drug studies, prototypes, a personal second brain) shares its machinery with
every illegitimate one. The spacetime window is a **telescope or a wiretap**; the identity fabric is a
**capability chain or a dossier engine**; the self-tuning loop makes an agent workforce **better at its job —
whatever that job is.** JB is right to be scared. The honest answer is not to make the power smaller; it is to
make the **governance inescapable**, and to make it inescapable *the same way Orreth governs everything else —
by recursing the architecture one tier up onto its own creator.*

> Orreth's own law is: policy cascades down, floors never loosen, security first, the watchers are watched.
> **The safety architecture is Orreth applied to Orreth.ai.** The platform is just the apex above every
> customer's apex — and it is governed harder than any tenant.

---

## 1. The Custodian tier — the apex above the apex

Recursion already permits "a Harness above Universes is just another Harness" (0000). The **hosted platform
(orreth.ai) is that Harness** — the **Custodian**. Every customer Universe is its child. But the Custodian's
powers are **deliberately asymmetric** — this asymmetry is the entire safety design:

| The Custodian **can** | The Custodian **cannot** |
|---|---|
| **Freeze** a Universe (quarantine — §4) | **Read** a Universe's tenant-private memory (§5 key custody) |
| **Enforce platform floors** that cascade into every Universe (§2) | Author or alter a tenant's own governance |
| **Sense floor-compliance via behavioral signatures** (§3) | Inspect content, prompts, or memory bodies |
| **Preserve** state under lawful process | Silently surveil — every Custodian action is Sourced + Verified + logged |

> The Custodian is a **landlord of worlds, not a spy in them.** It can shut off power and change the locks;
> it cannot read the mail. That single asymmetry is what separates "the most responsible infrastructure company"
> from "the most dangerous one." If the Custodian could read every Universe, Orreth.ai would be the largest
> surveillance apparatus ever built. It is architecturally forbidden from being that.

**The Custodian is itself governed — the watchers of the watchers are watched.** No single Orreth employee is a
god: quarantine and un-quarantine take **multi-party co-sign** (the 0006 rule, applied to staff); every Custodian
action writes a signed, immutable access record; and the Custodian's own entitlement model is transparent and
audited. The apex-above-apex is the *most* constrained node in the system, not the least.

---

## 2. Platform floors — the meta-cascade

Orreth already has **universal, non-overridable floors** that cascade down from a Universe. The Custodian sets
the floors *above* those — the most foundational rules in the system, cascading into **every** Universe, and
**no Universe GOD can loosen them.** This is where the ethical line lives, expressed as policy, not prose:

- **No targeting of non-consenting real-world identities.** A Universe may model its own agents and consented
  principals; it may not turn the substrate into surveillance or profiling of real people who never opted in.
- **Illegal-content prohibition** (CSAM foremost) — hard floor, no exceptions, mandatory action on detection.
- **PII / regulated-data consent floors** — GDPR/health/financial data requires consent + honors erasure
  (already the 0002/0003 tombstone machinery, elevated to a platform floor).
- **Autonomy ceilings by trust tier** (§6) — the most dangerous capabilities are gated, not default-on.
- **Attribution is non-optional** — a Universe cannot disable Sourced+Verified on its own records; deniability
  is not a product feature.

These are `PruningPolicy`/`Standard`-shaped artifacts issued at the Custodian scope; the existing cascade
resolver enforces "tighten-only" — a tenant can be *stricter* than a platform floor, never looser.

---

## 3. The Security Agent — a resident organ at every layer

Add a resident (TCB) agent to the roster at **every** tier: the **Security Agent**. It is the sensing-and-enforcement
organ for floors — and it serves two masters cleanly separated by scope:

- **Tenant-facing (inside the customer's authority):** the customer's own security agent may read within the
  Universe it serves — it is *their* watchdog, helping the Universe GOD secure their own world (anomaly
  detection, capability misuse, insider threat, their own compliance). This is a **feature** the customer wants.
- **Platform-facing (the Custodian's signal):** what rises to the Custodian is **behavioral and metadata only,
  never content** — volume/velocity patterns, targeting-shape signatures, known-bad indicators, floor-breach
  events. The Custodian learns *that* a Universe is behaving like a disinformation farm or a scraper of real
  identities **without reading a single memory body.** "Telescope, not wiretap" holds at the platform level too.

> The security agent is how a floor stops being a sentence in a policy and becomes a reflex in the plane.
> It is also, frankly, **helpful to us as we innovate**: it is the same organ that catches a runaway agent,
> a cost blowout, or a prompt-injection cascade — safety and reliability are the same instrument.

---

## 4. Quarantine — graded, auditable, reversible where it should be

One mechanism, three triggers, deliberately different consequences:

| Trigger | Action | Reversible? | Gate |
|---|---|---|---|
| **Commercial** (non-payment) | freeze compute; **retain data** per retention policy; grace + notice | **Yes** — pay, resume | automated + appeal |
| **Abuse** (platform-floor breach) | freeze + **preserve** + notify + human review | Case-by-case | **multi-party** Custodian co-sign; no single employee acts |
| **Lawful process** ("NSA comes by") | freeze + preserve; disclose **only what the platform actually holds** | Per law | legal review; **minimize what we can disclose** (§5) |

Design stances: quarantine **freezes, it does not delete** (preservation protects both the customer and any
lawful investigation); un-quarantine is **as gated as quarantine** (you can't un-freeze a bad actor alone
either); and **every quarantine is a signed Custodian action** the customer can see in their own audit trail —
no secret freezes. The "GOD didn't pay the bill" case and the "law shows up" case share a mechanism but not a
posture: one is a reversible commercial hold, the other is a legally-bounded preservation.

---

## 5. Key custody — the fork that decides everything

Each Universe has its **own KMS key** (JB's instinct — a key per Universe). *Who holds it* decides whether the
Custodian's "cannot read" is a promise or a **mathematical fact**:

- **Platform-held.** Convenient; the platform can do anything — including read. Weakest trust; the platform
  becomes a single point of compulsion and breach. *Reject for the regulated tier.*
- **Customer-held (BYOK).** The platform genuinely cannot read; strongest privacy; but the platform also cannot
  help recover, and a lost key is a lost Universe.
- **Split / co-held (recommended default for the enterprise tier).** Quarantine (freeze) requires a Custodian
  key; **reading requires the customer's key.** The Custodian can stop a Universe but cannot open it. This is
  the elegant middle — it makes "the landlord cannot read the mail" *true by cryptography*, and it makes the
  lawful-process answer honest: **if we cannot read it, we cannot be compelled to produce plaintext we do not
  hold.** That posture is not just ethical; it is exactly what a regulated buyer (a bank, a hospital, a defense
  program) requires before they will ever touch a hosted world.

> The strongest safety *and* the strongest sales story are the same design: the platform that **structurally
> cannot read its customers** is the one both regulators and dissidents can trust — and the one that cannot be
> turned into a weapon by whoever seizes it.

---

## 6. Trust tiers for Universe creation — capability follows verification

Not every anonymous signup should get spacetime-window-over-real-identities power on day one. Capability is
**gated by the verified trust of the creator** — the same graded-trust logic clouds already use for dangerous
primitives:

- **Anonymous / self-serve:** sandboxed Universes, synthetic or self-owned data only, hard caps on scale,
  **no real-world-identity ingestion**, no cross-tenant anything. (A game, a second brain, a prototype.)
- **Verified individual/org (KYC):** production scale, regulated-data handling under consent floors, the full
  window over *their own* consented world.
- **Regulated / high-assurance:** cross-tenant benchmarks, the heaviest autonomy — behind contracts, audits,
  and BYOK/split-key.

The most dangerous capabilities — ingesting real people, large-scale autonomous operation, anything approaching
cross-tenant reach — are **off by default and unlock with verification**, never the reverse.

---

## 7. The abuse taxonomy — naming the not-good, so we can design against it

You asked me to help you see what you might miss. Named plainly (defensive framing — these are the threat
models the floors and security agents exist to counter):

1. **Surveillance-as-a-service** — a Universe pointed at real people, the window as a stalking/profiling
   dashboard. *Countered by:* no-targeting floor · trust-tier gating of real-identity ingestion · behavioral
   detection of scraping signatures.
2. **Autonomous harm at scale** — agent workforces tuned toward fraud, disinformation, market manipulation,
   coordinated harassment; the self-improving loop makes them *better*. *Countered by:* objective-permissibility
   floors · autonomy ceilings · velocity/targeting signatures.
3. **Walled-garden concealment** — strong isolation + crypto is attractive precisely to those who want a
   deniable operation. *Countered by:* KYC-for-capability · non-optional attribution · Custodian quarantine.
4. **Data laundering** — a Universe as a place to give stolen/illegal data the *appearance* of clean
   provenance. *Countered by:* provenance proves *chain of custody*, not *right to hold* — attribution is not
   absolution; consent floors + regulated-tier gating.
5. **Illegal content** — the obligation every hosted platform carries. *Countered by:* hard floor + mandatory
   action + the T&S/legal program this spec defers to.
6. **The Custodian itself as the ultimate risk** — the one entity with reach into all worlds. *Countered by:*
   the whole of §1 and §5 — asymmetric powers, blinded by key custody, multi-party, fully audited.

---

## 8. The honest limits (what architecture cannot solve)

- **Self-hosting escapes the Custodian.** Orreth-the-software, run on someone's own metal, has no landlord —
  the operator *is* the custodian. The Custodian model governs **the hosted orreth.ai service**, not the
  software in the wild. Software in the wild is governed by law and licensing, as all dual-use tools are; we
  should be clear-eyed that our safety story is strongest for the hosted offering, and set license terms
  accordingly.
- **This needs professionals.** Content-moderation obligations, lawful-process handling, and jurisdictional
  data law are real disciplines. This spec makes the architecture *ready* for a trust-and-safety function and
  legal counsel; it does not replace them. (Fable is not a lawyer.)
- **Governance is a cost and a moat.** It slows some things down. That is not a bug — for the buyers who make
  Orreth a real business, the governance *is* the product. An ungoverned agentic universe is unsellable to
  anyone who matters and dangerous to everyone else.

---

## 9. Decisions — **all locked by JB, 2026-07-01** (recorded in `../decisions/`)

1. **Key custody: split-key, freeze-not-read.** Customer holds the read key; the Custodian holds only a
   freeze/quarantine key. "Cannot read" is a mathematical fact. *Owed: a customer-side recovery story for a
   lost read key (a lost key = a lost Universe) — flagged for the enterprise tier design.*
2. **Custodian read stance: structurally blinded.** Architecturally incapable of reading tenant content;
   floor enforcement is behavioral/metadata only. The capability that would be subpoenaed/breached/coerced
   simply does not exist. This is the public commitment.
3. **Creation gate: invite-only now, trust-tiered later.** Every operator is known during POC; the
   anonymous-sandbox → KYC-verified → regulated-high-assurance tiers (dangerous powers gated behind
   verification) come online as the floors and Custodian mature.
4. **First POC: Earth Mapper first; the Agentic Enterprise designed in parallel.** Dazzle with the
   near-zero-dual-use showcase while building the Custodian + audit surface the northstar requires anyway.

---

*Amends `0000` (adds the Security Agent resident organ + the Custodian tier). Unblocks nothing technical yet —
but it is the spec that lets orreth.ai be launched **without becoming the thing JB is right to fear.**
Security first — now applied to ourselves.* 🥃
