# 0013 — The Custodian Tier & Responsible-Universe Architecture

*Design draft for review — the dual-use reckoning, made structural. Prompted by JB's 2026-07-01 discussion:
"this is both AWESOME and SCARY." **Processed by Fable 5** (reconciling an earlier auto-generated pass that
under-specified HITL and — incorrectly — recorded decisions as JB-locked that JB never made; those are
**reopened** in §11). Fable owns the safety engineering; JB owns the vision and the go/no-go. Not legal advice —
the legal-process and content-obligation parts need real trust-and-safety and legal counsel before launch; this
spec makes the architecture ready for them.*

---

## Why this exists (named plainly)

Orreth lets anyone build a **secure, scoped, identity-aware world** — an agentic workforce you tune and govern,
with a window that can occupy any point in its spacetime. Every legitimate use (fleet management, running a
company's whole digital lifecycle, drug studies, prototypes, a personal second brain) shares its machinery with
every illegitimate one. The spacetime window is a **telescope or a wiretap**; the identity fabric is a
**capability chain or a dossier engine**; the self-tuning loop makes an agent workforce **better at its job —
whatever that job is.** JB is right to be scared. The honest answer is not to make the power smaller; it is to
make the **governance inescapable** — the same way Orreth governs everything else, by recursing the architecture
one tier up onto its own creator.

> **Design axiom: assume adversarial tenants.** Most subscribers are legitimate. The architecture must hold
> against the ones who are not, because on an open hosted platform they will come. Safety is the floor everyone
> stands on, not a feature added for the bad ones.

> Orreth's own law is: policy cascades down, floors never loosen, security first, the watchers are watched.
> **The safety architecture is Orreth applied to Orreth.ai.** The platform is the apex above every customer's
> apex — and it is governed *harder* than any tenant.

---

## 1. The Custodian tier — the apex above the apex

Recursion already permits "a Harness above Universes is just another Harness" (0000). The **hosted platform
(orreth.ai) is that Harness** — the **Custodian**. Every customer Universe is its child, **joined at floors-only
or observe-only — never fully-joined** (so platform floors are compelled but the Custodian is not entangled in
tenant operation). The Custodian's powers are **deliberately asymmetric** — this asymmetry is the entire safety
design:

| The Custodian **can** | The Custodian **cannot** |
|---|---|
| **Freeze** a Universe (quarantine — §5) | **Read** a Universe's tenant-private memory (§4 key custody) |
| **Enforce platform floors** that cascade into every Universe (§2) | Author or alter a tenant's own governance |
| **Sense floor-compliance via behavioral/metadata signals** (§3) | Inspect content, prompts, or memory bodies |
| **Preserve** state under lawful process | Silently surveil — every Custodian action is Sourced + Verified + logged |

> The Custodian is a **landlord of worlds, not a spy in them.** It can shut off power and change the locks; it
> cannot read the mail. That asymmetry is what separates "the most responsible infrastructure company" from "the
> most dangerous one." If the Custodian could read every Universe, orreth.ai would be the largest surveillance
> apparatus ever built. It is architecturally forbidden from being that.

**The Custodian is the *most* constrained node in the system.** No single employee is a god (§7 HITL map); every
Custodian action is a signed, immutable access record; its entitlement model is itself transparent and audited.

---

## 2. Platform floors — the meta-cascade

The Custodian sets the floors *above* a Universe's own universal floors — the most foundational rules in the
system, cascading into **every** Universe, **tighten-only** (a tenant may be stricter, never looser). Where the
ethical line lives, expressed as policy not prose:

- **No targeting of non-consenting real-world identities.** Model your own agents and consented principals;
  never turn the substrate into surveillance/profiling of real people who never opted in.
- **Illegal-content prohibition** (CSAM foremost) — hard floor, no exceptions, mandatory action on detection.
- **PII / regulated-data consent floors** — GDPR/health/financial data requires consent + honors erasure (the
  0002/0003 tombstone machinery, elevated to a platform floor).
- **No autonomy designed to evade governance** — no agent may be objective-built to hide from its own or the
  platform's oversight. Attribution (Sourced+Verified) cannot be disabled; **deniability is not a feature.**
- **Autonomy ceilings by trust tier** (§6) — the most dangerous capabilities are gated, not default-on.

These are `Standard`/`PruningPolicy`-shaped artifacts issued at the Custodian scope; the cascade resolver
enforces tighten-only.

---

## 3. The Security Agent (the Warden) — a resident organ, **detection not enforcement**

Add a resident (TCB) agent to the roster at **every** tier — the **Warden** — alongside steward · governance ·
analysis · becky. It is immutable to the Universe GOD (becky-issued, non-removable, un-blindable). **The single
most important correction in this dive: the Warden detects and advises; it does not enforce.**

- **It may:** observe, score, alert, flag anomalies, and rate-limit *within pre-set safety bounds*, and *stage*
  a recommended enforcement action.
- **It may not:** unilaterally quarantine, read plaintext, or act on another tenant. Every consequential action
  is a **control-plane act requiring HITL** (§5, §7). Conflating detection and enforcement in one autonomous
  agent is precisely how a compromised or mis-tuned agent does harm at machine speed — so we split them.
- **Two faces, cleanly scoped:**
  - *Tenant-facing* — the customer's own Warden helps them secure their world (anomaly detection, insider
    threat, their own compliance). A feature they want.
  - *Platform-facing* — what rises to the Custodian is **behavioral + metadata only, never content**:
    volume/velocity, targeting-shape signatures, floor-breach events, declared-purpose drift. The Custodian
    learns *that* a Universe behaves like a scraper or a disinfo farm **without reading one memory body.**
    Telescope, not wiretap — at the platform level too.

> Safety and reliability are the same instrument: the organ that catches a stalker-shaped Universe also catches
> a runaway agent, a cost blowout, or a prompt-injection cascade. It is also Fable's standing adversarial
> reviewer — every new feature is asked "how is this abused, and does the Warden still see it?" before it ships.

---

## 4. Key custody — the fork that decides everything

Each Universe has its **own KMS key** (JB's instinct). This separates two powers that must never be one:

| Plane | Power | Mechanism | Gate |
|---|---|---|---|
| **Control plane** | *freeze* — suspend compute, revoke access, preserve state | operate the key handle + compute, **without reading** | HITL (§5) |
| **Data plane** | *read* tenant plaintext | requires the actual key material | key custody (below) + due process (§6) |

*Who holds the read key* decides whether "cannot read" is a promise or a **mathematical fact**:

- **Platform-managed (default, self-serve).** Convenient, enables managed features; the platform *can* decrypt
  under a gated, logged, HITL process — so this tier's honesty rests entirely on §6 + §7. Fine for a game or a
  second brain; **not** for the regulated tier.
- **BYOK (customer-held).** The platform genuinely cannot read; strongest privacy; a lost key is a lost
  Universe (owed: a customer-side recovery story).
- **Split / threshold (recommended for enterprise/regulated).** Freeze needs a Custodian key; **reading needs
  the customer's key** (or a quorum incl. escrow). The Custodian can stop a Universe but cannot open it.

> The strongest safety *and* the strongest sales story are the same design: a platform that **structurally
> cannot read its customers** is the one a bank, a hospital, a defense program — and a dissident — can trust,
> and the one that cannot be weaponized by whoever seizes it. Quarantine works at **every** tier because it
> lives in the control plane, independent of the read key.

---

## 5. Quarantine — graded, control-plane, HITL-gated

Least-force-first; every rung is a signed, audited, control-plane act:

| Rung | Effect | Reversible | Authorization |
|---|---|---|---|
| **Throttle** | rate-limit within pre-set safety bounds | yes | Warden autonomous (bounded) |
| **Suspend** | pause compute; state preserved | yes | **2 Custodian humans co-sign** |
| **Freeze-preserve** | revoke key/compute access; snapshot-seal (legal hold) | yes (re-grant) | **2 co-sign** + reason on record |
| **Destroy** | permanent deletion of Universe + keys | **no** | **3 co-sign + cooling-off** |

- **Freeze preserves; it does not delete** — protects both the customer and any lawful investigation.
  Destruction matches root-rotation's 3-co-sign bar (0006), with a cooling-off window so no single bad night
  ends a world.
- **Un-quarantine is as gated as quarantine** — you cannot un-freeze a bad actor alone either.
- **Customer notice is the default** — a frozen GOD is told, and why, *unless* a lawful order gags us (a sealed
  audit entry that surfaces when the gag lifts). No secret freezes otherwise.
- **The three triggers share the mechanism, not the posture:** *commercial* (non-payment → notice-then-suspend,
  reversible on payment), *abuse* (floor breach → freeze + review; active child-safety harm freezes first,
  notice after), *lawful process* (freeze + preserve; disclose only what we actually hold — §6).
- **Legal hold overrides right-to-erasure, honestly:** a pending tombstone (0002 §6 / 0003 §2) is *suspended,
  not executed*, under a freeze-preserve — "GDPR erasure" must never become "destroy the evidence." Preserve,
  then adjudicate.

---

## 6. Lawful intervention — due-process-gated, minimized — **never a backdoor**

"If the NSA comes by" deserves a precise answer:

- **No backdoor, ever.** No operator capability to silently read a tenant. BYOK/split tiers make unilateral
  operator access *technically impossible* — a feature we sell, not a gap we hide.
- **Lawful access is:** valid legal process → legal review → **3-co-sign + legal sign-off** (data-plane) →
  scope minimized to exactly what the order covers (via the retrieval contract, 0002) → immutable audit →
  customer notice unless lawfully gagged. The spacetime window is **never** the tool of first resort against a
  person; scoped, minimized retrieval is.
- **The honest posture to any authority:** *"We freeze on lawful order; we read only via due process, minimized
  and logged; and for BYOK/split tenants we cannot read at all — here is the key-holder."* That protects the
  operator, the customer, and the people whose data is the collateral.

---

## 7. HITL placement map (the correction — autonomy only below the harm line)

| Action | HITL |
|---|---|
| Detection, alerting, metadata anomaly flagging, read-only monitoring | **none** (Warden autonomous) |
| Rate-limit within pre-set safety bounds | **none** (Warden, bounded) |
| Onboard a universe in a **flagged/regulated/dual-use domain** (§8) | **1+ Custodian review gate** |
| Suspend / freeze-preserve a universe; un-quarantine | **2 Custodian humans co-sign** |
| Cross-universe query/correlation (platform side; never on plaintext) | **2 Custodian humans** |
| Produce keys / read tenant plaintext under legal process | **3 + legal sign-off** |
| Permanent destruction of a universe/keys | **3 + cooling-off** |
| Trust-root rotation | **3** (locked, 0006) |
| A customer's own apex actions inside their universe | **the customer's** HITL (governed-human-oversight.md) |

> **The rule Fable enforces:** if an action can affect a party who did not initiate it, it escalates to a human.
> Machine speed is for *detection*; human judgment is for *consequence*. (This is the rigor the earlier pass
> missed.)

---

## 8. Trust tiers & onboarding — refuse at the door when you can

Capability follows verification; cheaper and safer to prevent than to quarantine.

- **Declared purpose + acceptable-use attestation at provisioning** — a signed, auditable commitment;
  declared-purpose drift is a Warden signal.
- **Anonymous / self-serve:** sandboxed, synthetic/self-owned data only, hard scale caps, **no real-world-
  identity ingestion**, no cross-tenant anything. (Game, second brain, prototype.) Provisions instantly.
- **Verified individual/org (KYC):** production scale, regulated-data under consent floors, the full window over
  *their own consented* world.
- **Regulated / high-assurance:** cross-tenant benchmarks, heaviest autonomy — behind contracts, audits,
  BYOK/split-key. **Flagged domains** (health, finance, PII-at-scale, bio/cyber/chemical dual-use,
  population-scale observation, influence ops) hit a **human review gate + KYC before a key is issued.**
- **Published refuse-to-host list** (a wall, not a whisper): mass surveillance of non-consenting people; CSAM
  or child exploitation; agentic development of weapons/dangerous dual-use capability; coordinated inauthentic
  behavior; sanctions/regulated-market evasion; any universe whose agents are objective-designed to evade
  oversight.

The most dangerous capabilities are **off by default and unlock with verification** — never the reverse.

---

## 9. The abuse taxonomy — naming the not-good, so we design against it

Category-level only; no operational detail. Each has a named owner in the controls above.

1. **Surveillance-as-a-service** — the window as a stalking/profiling dashboard. *Countered by:* no-targeting
   floor · trust-tier gating of real-identity ingestion · scraping-signature detection.
2. **Autonomous harm at scale** — fleets tuned toward fraud/disinfo/manipulation/harassment. *Countered by:*
   objective-permissibility floors · autonomy ceilings · velocity/targeting signatures.
3. **Walled-garden concealment** — isolation + crypto as a deniable operation. *Countered by:* KYC-for-
   capability · non-optional attribution · quarantine.
4. **Data laundering** — a Universe to give stolen/illegal data clean-looking provenance. *Countered by:*
   provenance proves chain-of-custody, not right-to-hold — **attribution is not absolution** — plus consent
   floors + regulated-tier gating.
5. **Dangerous-capability R&D** — agentic development toward bio/cyber/chemical/weapons capability. *Countered
   by:* flagged-domain gate + refuse-to-host + declared-purpose-drift detection.
6. **Illegal content / exploitation** — CSAM foremost. *Countered by:* absolute floor + mandatory action +
   the T&S/legal program this spec defers to.
7. **The Custodian itself as the ultimate risk** — the one entity with reach into all worlds. *Countered by:*
   §1 asymmetry + §4 key-blinding + §7 multi-party HITL + full audit.

---

## 10. The honest limits (what architecture cannot solve)

- **Self-hosting escapes the Custodian.** Orreth-the-software on someone's own metal has no landlord — the
  operator *is* the custodian. The Custodian model governs the **hosted orreth.ai service**; software in the
  wild is governed by law and license, as all dual-use tools are. Set license terms accordingly; be clear-eyed
  that the safety story is strongest for the hosted offering.
- **This needs professionals.** Content-moderation obligation, lawful-process handling, jurisdictional data law
  are real disciplines. This spec makes the architecture *ready* for a T&S function and legal counsel; it does
  not replace them. (Fable is not a lawyer.)
- **Governance is a cost and a moat.** It slows some things down — and for the buyers who make Orreth a real
  business, the governance *is* the product. An ungoverned agentic universe is unsellable to anyone who matters
  and dangerous to everyone else.

---

## 11. The two POCs

### POC 1 — **Earth Mapper** (the safe showcase; build first)
A Universe whose ecosystem of agents (geography, weather, imagery, logistics, language…) collaborate to render a
**live, rotating understanding of Earth** — discovering, applying, and cascading knowledge as skills; the
spacetime window becomes literal. *Why first:* it exercises the crown jewels — cross-agent collective memory,
skills cascade, the window — on **public/open/consented data only**, near-zero regulatory surface, maximum wow;
de-risks the hard tech and feeds Articles 03/04. *Safety that keeps it clean:* open/consented sources only, **no
observation of identifiable individuals** — Earth as a system, not a surveillance grid (a live demonstration of
the platform-floor model working).

### POC 2 — **The Agentic Enterprise** (JB's northstar; build second)
A truly agentic enterprise that amazes the C-suite (CFO, CRO, CTO, CPO, CEO, CCO) **and** regulators (NIST,
PCI-DSS, PII/GDPR, DORA, SOX, universe audit) — every number Sourced + Verified, each regulator handed a
*scoped, entitled, audited* window. *Why second:* the commercial killer, but it needs the compliance floors, the
full HITL map (§7), and the regulator-entitlement model (governed-human-oversight.md) hardened first. Earth
Mapper proves the substrate; the Enterprise sells it — to the CFO-led buyers who fund the platform.

---

## 12. Open decisions — **reopened for your real call, JB**
*(An earlier auto pass recorded these as "locked"; you never made them. They are yours.)*

1. **Key custody offering.** Tiered — platform-managed default + BYOK + split/escrow for high-assurance (my
   strong lean) — or platform-managed only to start? *A hospital or defense tenant won't sign without BYOK; a
   hobbyist doesn't care. Tiered lets both in and makes "we cannot read you" a sellable promise.*
2. **Quarantine authorization bar.** Confirm: throttle autonomous · suspend/freeze = 2 Custodian co-signs +
   customer notice (unless gagged) · destroy = 3 + cooling-off? *A late invoice gets notice-then-suspend; an
   active child-safety hit freezes first, notice after.*
3. **Onboarding posture.** Risk-tiered (benign self-serve, flagged domains human-gated — my lean) vs
   attestation-only-for-all (faster, weaker door) vs review-everything (safest, slow)? *Risk-tiered lets "my
   second brain" spin up in minutes while "population health analytics" meets a human + KYC first.*
4. **POC sequence.** Earth Mapper first, Enterprise second (my lean) — or Enterprise first because it's the
   northstar? *Earth Mapper is public, dazzling, needs no compliance build; the Enterprise is months and needs
   §7 hardened first.*
5. **The Warden's name.** becky is the IAM agent; the security resident is "the Warden" as a role. Want a
   becky-style given name, and if so, yours to christen.

---

*Amends `0000` (adds the Warden resident organ + the Custodian tier). Reuses `0012`'s co-sign machinery at the
platform tier and extends `governed-human-oversight.md` (humans as governed principals) to the operator.
This is the spec that lets orreth.ai launch **without becoming the thing JB is right to fear** — and proves
"AWESOME and SCARY" can be engineered into "awesome because we designed the scary out, and can prove it."
Security first — now applied to ourselves.* 🥃
