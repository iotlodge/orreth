# 0013 — The Custodian Tier & Responsible-Universe Architecture

*Design draft for review — the dual-use reckoning, made structural. Prompted by JB's 2026-07-01 discussion:
"this is both AWESOME and SCARY."*

> **Provenance — corrected 2026-07-02, and itself a case study.** This document went through three passes.
> Pass 1 (2026-07-01) was **Opus 4.8 on auto**: under-specified HITL and recorded decisions as JB-locked that
> JB never made. Pass 2 the same evening — the one that committed itself as *"reconciled by Fable 5"* — was
> **also Opus 4.8**: JB's prompt routed to Fable 5 twice, the stream aborted twice mid-thinking, and the desktop
> app silently fell back; the model self-attributed as Fable because the prompt addressed it that way. Pass 3
> (2026-07-02) is **genuine Fable 5**, verified against the desktop app's HMAC-signed session audit log
> (per-message model IDs), reviewing line-by-line — adopted where sound, amended where not (§3 mechanism
> honesty, §7 floor-change rows, §10 cryptographic-blindness limit). The mislabel is precisely the failure mode
> this spec's own floor — **non-optional attribution** — exists to prevent: the commit said Fable, the wire
> said Opus, and only a signed audit trail made the difference checkable. *The safety architecture caught its
> own author.* §12's decisions survive the correction: the audit log confirms JB genuinely answered them.

*Fable owns the safety engineering; JB owns the vision and the go/no-go. Not legal advice —
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
enforces tighten-only. **The floors are versioned, published artifacts — and changing them is itself the
highest-blast-radius act in the system** (a floor loosened is every tenant's floor loosened), so floor changes
carry their own HITL rows (§7): tightening moves at safety speed; loosening never happens quietly.

---

## 3. The Security Agent — **vigil**, the Warden — a resident organ, **detection not enforcement**

Add a resident (TCB) agent to the roster at **every** tier — **vigil**, the Warden (christened by JB
2026-07-02; becky-style given name, becky's counterpart: becky says *who you are*, vigil watches *what you do*) —
alongside steward · governance · analysis · becky. **"Non-removable" is a contract, not magic** *(Fable 5
correction — the earlier passes asserted "un-blindable" with no mechanism behind the word)*: vigil's presence
and its flowing telemetry are **terms of the hosting join credential** — a platform floor (§2). vigil emits a
signed heartbeat; a Universe that blinds, starves, or removes its Warden goes **silent — and silence is a louder
signal than any alert** (a dead-man switch the Custodian cannot miss). Removal isn't prevented cryptographically;
it is made *self-defeating* — detected within a heartbeat window, treated as a floor breach, answered by the
quarantine ladder (§5). **The single most important correction in this dive stands: vigil detects and advises;
it does not enforce.**

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
  - **The telemetry itself is governed** *(Fable 5 addition; locked by JB 2026-07-02)*: "just metadata" is the
    surveiller's oldest defense, and we don't get to use it. What rises is a **versioned, published contract**
    (`contracts/` — like every other wire in Orreth), and every tenant's pane renders a **live mirror of exactly
    what their Universe reports up**. The Custodian's eyes are enumerated, published, and tenant-watchable —
    *we publish what we can see about you, and you can watch us see it.* Minimization, applied to ourselves.

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
| **Tighten** a platform floor (§2) | **2 co-sign** + versioned publication |
| **Loosen or remove** a platform floor — highest blast radius in the system | **3 co-sign + cooling-off + published changelog** |
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
- **Cryptographic blindness limits content-floor enforcement — on purpose** *(Fable 5 addition)*. For BYOK/split
  tenants the platform *cannot* scan content at rest; content-level floors (illegal content foremost) are
  enforceable only where content transits platform-operated surfaces (ingress/egress, the Model Gateway) and via
  vigil's behavioral signals. That is exactly why the blind tiers sit behind the hardest door (§8) — **you earn
  the right to be unreadable.** The pairing is the design, not a hole in it; it must be said plainly, because a
  regulator will ask.
- **This needs professionals.** Content-moderation obligation, lawful-process handling, jurisdictional data law
  are real disciplines. This spec makes the architecture *ready* for a T&S function and legal counsel; it does
  not replace them. (Fable is not a lawyer.)
- **Governance is a cost and a moat.** It slows some things down — and for the buyers who make Orreth a real
  business, the governance *is* the product. An ungoverned agentic universe is unsellable to anyone who matters
  and dangerous to everyone else.

---

## 11. The proving grounds — three universes, two axes, one funnel

*(Amended 2026-07-02, JB + Fable 5. The spacetime window has **two axes**, and the original two-POC plan proved
only one: Earth Mapper is the **space** axis and cannot prove **time** — a young universe has shallow lived
history, and backfilled archives are ingested data, not lived memory. The League is the **time** axis: its
internal clock outruns wall-clock, so decades of lived, identity-keyed history exist within weeks — the only
honest way to demonstrate "no limit" memory depth on a young platform.)*

### PG-1 — **The League** ("Create Your Sports League" — the time axis; first if we must serialize)
Universe = the league; Ecosystems = conferences; Fields = teams; Agents = players, coaches, scouts, trainers,
commentators. Seasons run at accelerated universe-time: rookie → veteran → legend → hall of fame, with the
memory metabolism **visible to a layperson** — last night's game in full detail, last season as box scores, ten
seasons back as records and legends (0003's pruning-as-fidelity-curve, needing no explanation). *Why it proves
the substrate:* it is nearly a 1:1 costume for decisions already locked — transfers with source veto / league
compel (0002 close-out), scouting = the interview sandbox, draft classes = archetype → incarnation, playbook
secrecy = sibling walls, standings = `0005`'s monoidal roll-up wearing a jersey. *Cost shape (JB's instinct,
confirmed):* **cheap cognition, rich identity** — games simulate programmatically; LLM calls only where they
shine (scouting interviews, commentary). The spend lands in the substrate, which is the thing being proved.
*New requirement it surfaces:* **universe-time vs wall-clock** (the time-dilation dial) — memory horizons,
retention, and pruning cadence run on universe-time; security TTLs and co-signs stay on wall-clock. Owned by
the `0004` Tier Profile dive.

### PG-2 — **Earth Mapper** (the space axis; the poster)
A Universe whose ecosystem of agents (geography, weather, imagery, logistics, language…) collaborate to render a
**live, rotating understanding of Earth** — discovering, applying, and cascading knowledge as skills; the
spacetime window becomes literal. It exercises the crown jewels — cross-agent collective memory, skills
cascade, the window — on **public/open/consented data only**, near-zero regulatory surface, maximum wow;
de-risks the hard tech and feeds Articles 03/04. *Safety that keeps it clean:* open/consented sources only, **no
observation of identifiable individuals** — Earth as a system, not a surveillance grid (a live demonstration of
the platform-floor model working). *Dogfooding floor:* Earth Mapper runs as **orreth.ai's own
first tenant** — same onboarding gate, same floors, same vigil telemetry, same tenant mirror. The demo that shows
off the substrate is also the live proof the governance is real: the first universe we host is one we govern
ourselves, in public.

### PG-3 — **The Agentic Enterprise** (JB's northstar; built **in parallel, always**)
A truly agentic enterprise that amazes the C-suite (CFO, CRO, CTO, CPO, CEO, CCO) **and** regulators (NIST,
PCI-DSS, PII/GDPR, DORA, SOX, universe audit) — every number Sourced + Verified, each regulator handed a
*scoped, entitled, audited* window. It needs the compliance floors, the full HITL map (§7), and the
regulator-entitlement model (governed-human-oversight.md) hardened — so those are built against it continuously
while the public proving grounds run ahead. The League and Earth Mapper prove the substrate; the Enterprise
sells it — to the CFO-led buyers who fund the platform. It is also, plainly, **the portfolio artifact**: the
demonstration that a governed agentic enterprise can be designed, run, and audited — valuable to its author
independent of platform revenue.

### The funnel — **Watch → Play → Build → Buy** (locked 2026-07-02)
Every article ends at a **public, read-only spacetime window** on a living demo universe — no signup; scrub a
league's decades in the browser (`0008`'s hero pane doing GTM duty; engagement begins before any account
exists) → **Play:** create your own league (the `0009` self-serve template flow) → **Build:** the dev docker
eco for engineers → **Buy:** the enterprise track. Every step up the funnel is the same architecture at a
deeper commitment — the demo, the product, and the proof are one artifact.

---

## 12. Decisions — **locked by JB** (via AskUserQuestion; recorded in `../decisions/`)
*(An earlier auto pass falsely recorded 1–4 as locked before JB decided; the audit log confirms JB genuinely
answered them on 2026-07-01. Decisions 5–8 were locked 2026-07-02 during the genuine Fable 5 pass.)*

1. **Key custody: tiered** — platform-managed default + BYOK + split/escrow for high-assurance. "We
   structurally cannot read you" becomes a true, sellable promise at the higher tiers.
2. **Quarantine bars: 2 to freeze, 3 to destroy.** Throttle autonomous (bounded); suspend/freeze = 2 Custodian
   co-signs + customer notice (unless gagged) + state preserved; destroy = 3 + cooling-off. Active child-safety
   harm freezes first, notice after.
3. **Onboarding: risk-tiered.** Benign domains self-serve; flagged domains → human review + KYC before a key
   issues; published refuse-to-host list.
4. **POC order: Earth Mapper first, Agentic Enterprise second** (compliance floors + HITL map built in parallel).
5. **Floor changes: asymmetric bars** *(2026-07-02)* — tighten = 2 co-sign + versioned publication; loosen or
   remove = 3 co-sign + cooling-off + published changelog. Safety moves at safety speed; floors never loosen
   quietly.
6. **Telemetry: published contract + tenant mirror** *(2026-07-02)* — the platform-facing telemetry schema is a
   versioned public contract, and every tenant's pane renders a live mirror of exactly what rises. The
   Custodian's eyes are themselves governed and watchable.
7. **The Warden is christened `vigil`** *(2026-07-02)* — becky says *who you are*; vigil watches *what you do*.
8. **Proving grounds & funnel** *(2026-07-02; amends decision 4)* — the window's two axes split across two
   public universes: **The League** (time; the playable; first if serialized) + **Earth Mapper** (space; the
   poster), with the **Agentic Enterprise northstar built in parallel throughout**. GTM funnel: **Watch → Play →
   Build → Buy** — articles land on a public read-only window, never a signup wall.

**No 0013 items remain open.**

---

*Amends `0000` (adds vigil, the Warden resident organ + the Custodian tier). Reuses **`0006`'s co-sign
machinery** at the platform tier (the earlier passes cited `0012`, which is a reserved, unwritten dive — the
co-signs are locked in 0006; 0012 is where the Custodian's HITL gate & queue *mechanics* will be designed) and
extends `governed-human-oversight.md` (humans as governed principals) to the operator.
This is the spec that lets orreth.ai launch **without becoming the thing JB is right to fear** — and proves
"AWESOME and SCARY" can be engineered into "awesome because we designed the scary out, and can prove it."
Security first — now applied to ourselves.* 🥃
