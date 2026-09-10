# 0068 — The Rail and the Stamp

*Drafted 2026-09-07 from the orreth-EnterpriseRAG proof's charter — the proofs era's fourth
kernel dive, paying the proof's KCR-0003 (guardrails as layered, governed, hard-enforced
assets). Grounded in a full survey of the cascade, gateway, safety, and consent machinery
the same day (Appendix A).*

***Status: 🟡 DRAFTED · LOCKED — all three locks taken by JB's word, 2026-09-07, plainly
stated per the language law: L1 proof-required enforcement (the kernel demands the guardrail
proof on every thought; content checks in the checkpoint lane; independent audits either
way — hard enforcement without breaking the never-reads-prompts promise) · L2 every reader
sees the confession (unguarded answers say so in the canvas, the API reply, and the
librarian's voice) · L3 the rule-9 contract fix APPROVED (`floors` declared in the
tier-profile schema — the contract stops lying; parity green before it lands).***

## 1. The demand, verbatim (the proof's charter)

> "The E-RAG architecture should have CRUD Guardrails which you might really want in the
> LiteLLM aspect of Kernel (feels like a single place to CRUD guardrails that the kernel can
> HARD enforce)… if users don't want to use GuardRails they can submit an empty one (kind of
> scary). PII/PCI being an example guardrail… go with the cleanest and strongest approach
> but we are proving Orreth so that is where you would strengthen." — JB, KCR-0003
>
> "I also like the idea of having layered guardrails — the Universal vs Capability level —
> but LOVE your idea about a HITL Approval (visible and able to undo) stamp." — JB, the
> session close (KCR-0003 addendum)

## 2. The problem — what the survey found

The kernel has the *grammar* for layered law and none of the *content*:

1. **Content safety is effectively absent.** Zero hits for pii, pci, guardrail, mask, or
   moderation across the whole backend. The one content-shaped policy in the system is the
   Farm warden's credential sniffer — and its architecture is the perfect seed: **the
   checks are firmware, the pattern list is governed craft** (`speech.py:75-76`), and it
   *stages, never enforces*.
2. **The gateway lane carries no policy reference at all.** `/model/authorize` takes token,
   class, estimate, and an optional model pin — nothing says which law governed the
   thought (`model.rs`: zero hits for floors/policy). "Which guardrails governed this
   answer?" has no answer today.
3. **The vehicle for that answer exists and is asleep.** ResolvedContext — a signed,
   content-addressed policy snapshot — is produced by the Python reference, pinned into
   apertures (`law=…`) and RunRecords (`context_hash`)… and **the Rust resolver crate is
   dead code**: compiled, conformance-tested, never called by `orrethd`. The plane has no
   ResolvedContext at runtime.
4. **Tighten-only is not enforced where it matters.** The Python reference refuses a
   loosening floor (`FloorViolation`, `node.py:142-152`); **Rust has no monotone check at
   all** — inherited-wins is a positional convention. Three adjacent wounds ride along: the
   `/standards` boot pull is unverified in Rust (the Python twin checks the bundle
   signature); `floors` is an **off-contract field** (tier-profile schema says
   `additionalProperties: false`, yet every production profile carries it — the contract
   lies by omission today); and the retention grammar (`KeepRule`) has no content verbs —
   a PII rule literally cannot be expressed.
5. **A refusal is not evidence.** The one-face refusal is a literal
   (`403 · "request cannot be served under this capability"`) plus an unsigned counter
   reset on restart. A guardrail audit trail must be minted independently — and the
   tamper-verify pattern (an observation record landing *either way*, clean and hit,
   scribe-signed) is the proven template.
6. **The stamp's machinery already lives.** The bell/continuity consent grammar: a grant
   minted only from a human's click (the stamp cites the card), window-bounded, visible in
   a ledger, revoked by a sibling on the same worldline — **immediate and ungated**,
   because stopping is always safe. Withdrawn is a state, never a hole; even declining is
   on the record.

## 3. The shape

### 3.1 Guardrail rules — a new grammar beside retention (plain words first)

**In plain words: a guardrail is a written rule about content — "credit-card numbers never
leave in an answer," "social-security numbers are masked at the door" — kept as a versioned,
human-edited asset, checked by machinery that cannot be quietly edited.**

- **The detector is firmware** (the warden split, promoted): category detectors (PII, PCI,
  custom-pattern, classifier-by-reference) ship as release-only code.
- **The rules are craft**: `guardrail-*` assets in their own gated drawer (the 0063
  pattern — checked before landing, teachings on every sibling, genesis fallback served
  loudly). A rule = *match* (category or pattern-list ref, direction: entering/leaving) +
  *action* (**refuse · mask · quarantine-for-review · annotate**) + *reason* (every rule
  says why — the audit trail starts in the policy).
- **PII and PCI ship as the first rails**, mask-by-default, refusable where a rule says so.

### 3.2 Two layers, one lattice (the tighten-only law, finally enforced)

The **Universal set** lives at the universe tier and cascades down; a **Capability set**
may add rails, widen a rail's match, or strengthen its action — never remove, narrow, or
weaken (mask may become refuse; refuse may never become mask). The check is real, both
sides: at publication (the gate refuses a loosening edit with a teaching, the
`FloorViolation` pattern) and at resolve (the composed set is verified monotone — the
`cascade_gate` lattice precedent, ported to Rust at last).

### 3.3 Where enforcement bites — hard, and honest about what "hard" means

**In plain words: the kernel never reads anyone's prompts — that is one of its oldest
promises. So "hard enforcement" means the kernel refuses to let any thought be served
unless that thought carries proof of exactly which guardrail set governed it — and the
checking itself runs in the one lane every thought already passes through.**

- **The resolver wakes.** `orrethd` composes and persists the ResolvedContext (guardrail
  set included), so the policy snapshot has a durable referent — not just a hash.
- **The gateway demands the pin.** `/model/authorize` gains the context reference; a call
  without one — or with a stale one after a guardrail change — gets the one-face refusal,
  byte-identical to a budget miss. The meter entry carries the pin verbatim (the meter
  already persists whatever we send).
- **The content check runs gateway-side, cognition-side** — in the LiteLLM lane JB named:
  inputs checked before the call, outputs before they return. The plane sees proof, never
  prose. Cached answers revalidate when the guardrail version moves (the caching charter
  law, now mechanical).
- **The audit is independent of the refusal.** A scribe-signed `guardrail-audit` record
  lands *either way* — clean or hit, with the rule ref and the action taken — riding the
  tamper-verify pattern. vigil keeps its blindness and its honor: the plane refuses, the
  scribe records, vigil stages what needs a human.

### 3.4 The stamp — the consent grammar, worn openly

An **empty or weakened guardrail set** requires a stamp that is:
- **minted only from a human's click at a gate** (the stamp record cites the card — the
  bell-consent path verbatim);
- **window-bounded** (default 90 days, a dial — scary must be *renewed*, never inherited
  by silence);
- **visible** — in the consents ledger, in the Observatory, and worn by the work itself
  (§3.5);
- **undoable immediately, without a gate** — a revoked sibling on the same worldline;
  stopping is always safe, and the walk-back is a first-class recorded act;
- and **declining is itself durable** — the record keeps that you chose.

### 3.5 The answer confesses (staged as L2)

Work served under an empty set says so where the reader is: the answer's record carries
the stamp ref, and every surface that renders the answer renders the confession — the
canvas, the API reply, the librarian's voice. Scary never silent, all the way down to the
sentence a person actually reads.

### 3.6 The found wounds, paid while we are here

The Rust monotone check (§3.2); the `/standards` pull verifies the bundle signature
(parity with the Python twin — a poisoned standard rejected, not swallowed); and the
off-contract `floors` field is declared honestly (staged as L3 — a rule-9 decision,
because the tier-profile schema is sacred).

## 4. The razor applied (plain words in parentheses)

| Layer | Class |
|---|---|
| Detectors, the monotone check, the gateway pin, the audit shape (the machinery that cannot be quietly edited) | **Firmware** — release |
| `guardrail-*` rules, pattern lists, the Universal and Capability sets (the rules humans write and tune) | **Craft** — gated, versioned, teachings on every sibling |
| Stamp window, audit cadence (numbers with pre-set limits) | **Dials** |
| Stamps, audits, refuse/mask events (what actually happened) | **Records** — signed, purge-reachable |

## 5. The locks (staged for JB, 2026-09-07)

- **L1 — what "hard enforce" means** (§3.3): proof-required at the gateway + content
  checks in the gateway lane + independent audit records — versus the kernel reading
  prompts (which would break its oldest promise).
- **L2 — the confession** (§3.5): does work under an empty set say so to every reader, or
  only in admin views / the record?
- **L3 — the rule-9 contract fix**: declaring `floors` in the sacred tier-profile schema —
  recording a truth production already lives, or leaving the contract's lie until v1.

## 6. The spoonfuls (proposed order)

1. **sp1 — The grammar and the drawer.** ✅ **LANDED 2026-09-09 — the rails have a
   grammar, a drawer, a lattice, and a living version.** `orreth_sim/guardrails.py`:
   the rule shape in plain words (match: a category the firmware can detect — pii ·
   pci — or a pattern list by reference, with a direction; action on the strength
   ladder annotate < mask < quarantine < refuse; and **every rule says WHY** — the
   audit trail starts in the policy). **The first rails ship as genesis**: PII masked
   leaving, PCI refused both ways — planted once at the ask lane (the plant_standard
   idiom). **The drawer**: guardrail-* is PURPOSE by the razor, gate-checked rule by
   rule with teachings on every sibling; an EMPTY set is legal, explicit, and loudly
   scary (sp5's stamp law will demand the signature). **The lattice, enforced at
   publication**: a capability set may add, widen, or strengthen — a weakening or
   narrowing edit REFUSES at the door with the teaching («a child tightens, never
   loosens; refuse may never become mask»); absence never removes (compose always
   keeps every universal rule). **And the 0071 seam PAYS EARLY**: the ask-cache's
   guardrail version is now the LIVE composed set's content hash — a turned rail
   revalidates every cached answer by construction. *Proven live on the rig: the
   genesis rails planted on the first ask; a weakening capability set REFUSED with
   the lattice teaching; a lawful strengthening landed; and the charter's caching law
   walked whole — cached under the standing rails, the universal tightened through
   the one door, the SAME words answered FRESH. The walk found its own wound: the
   stacks pull never carried guardrail-* assets, so the planter re-planted genesis
   beside the human's word — fixed in the hour (the pull carries the rails; zero
   re-plants after). Canon restored through the door. Suite 495→503 (eight grammar
   laws). Rust green.* *Honest remainders: detectors arrive sp4 (rules are policy
   today, enforcement lands with the LiteLLM lane); the resolve-side monotone check
   in Rust is sp2's; the stamp is sp5's.*
2. **sp2 — The resolver wakes.** ✅ **LANDED 2026-09-09 — the dead crate called at
   last, and three old lies stopped.** **The resolver wakes**: `orrethd` composes the
   content-addressed ResolvedContext AT BOOT (the parity-pinned crate's pure fold,
   wrapped with the guardrail pin and re-hashed so the id names the WHOLE law a
   thought runs under), persists every version to Postgres (`resolved_contexts` —
   the id has a durable referent, never just a hash in the air), and serves it at
   `GET /context`; the worker pushes the rails' pin (`POST /context/guardrails`) at
   boot and after every guardrail edit — a turned rail RE-ADDRESSES the law within
   the breath. **The standards pull verified**: becky SIGNS the floors bundle
   (worker-side — the plane never signs) and the plane verifies before serving
   (`bundle_ok`: the root-chained token names the signer, the signature covers the
   floors); a pulling child verifies the same way against its own pinned root and a
   poisoned standard KILLS THE BOOT — fail-closed, the Python twin's law at last in
   Rust; an unsigned pull confesses loudly instead of pretending. **The monotone
   check in Rust**: a local floor that weakens or shortens an inherited one refuses
   the whole boot with the teaching (`floor_flaw`, unit-held both directions). **L3's
   contract line landed** (JB's rule-9 word): `floors` declared in the sacred
   tier-profile schema with its full rule shape — the contract stops lying by
   omission; parity green. *Proven live on the rig: «ResolvedContext composed» at
   every plane's boot; becky's bundle signed, pushed, LIVE-VERIFIED by the plane's
   own bundle_ok at the door, and served to pullers; the context re-addressed with
   the guardrail pin (gr-…, the head ref riding); THREE floors' contexts already
   durable in Postgres. Suite 503 + SDK 24 (parity) + orrethd 12 (four new boot
   laws). The child's own VERIFIED boot line lands at the next rig cycle now that
   bundles stand on parents — named.* *Honest remainders: the bundle re-pushes each
   worker life (in-memory on the plane — a pg row when it itches); soft/skills ride
   the profile into the fold but no profile declares them yet; sp3 makes the gateway
   DEMAND the context id.*
3. **sp3 — The gateway pin.** `/model/authorize` demands the context ref; one-face refusal
   on miss/stale; the meter carries it; cache revalidation on version change.
4. **sp4 — The rails and the audit.** PII/PCI detectors + mask/refuse in the LiteLLM lane;
   the scribe-signed audit landing either way; vigil staging the review-worthy.
5. **sp5 — The stamp.** The consent-grammar stamp end to end: gate card → minted stamp →
   ledger + Observatory visibility → the confession on served work → the one-click
   walk-back, proven by a human in the glass.

## 7. The honest boundary rows this dive moves

- New proven rows at close: layered guardrails enforced monotone both sides; the gateway
  pin ("which guardrails governed this answer" is a lookup); the stamp lifecycle proven by
  a human hand.
- The content-safety absence: from unwritten to named-and-paid (PII/PCI first; the
  detector roster grows by release).
- Parked honestly: classifier-based detectors beyond patterns (await a Stable vision/text
  mind earning the seat); redaction-at-ingest (Dive V's tie-in, this dive ships the verbs).

## Appendix A — evidence trail (survey 2026-09-07)

Dead resolver (`orreth-resolver` workspace member, zero callers); no Rust monotone check
(positional only; Python `node.py:142-152`); unverified `/standards` pull
(`main.rs:126-136` vs `node.py:135-136`); off-contract `floors`
(`tier-profile.schema.json:399` vs `demo-universe.json:16`); retention-only `KeepRule`
(`pruning-policy.schema.json:32-62`); policy-free gateway (`model.rs`, `main.rs:803-855`);
the one face as a literal + unsigned counter (eleven sites; refusal ≠ evidence); warden
firmware/craft split (`console_worker.py:2842-2877`, `speech.py:75-76`); tamper-verify
audit pattern (`console_worker.py:10484-10556`); consent/stamp machinery
(`continuity.py:146-275`, `bell.py:54-110`, `console_worker.py:716-789, 10071-10110`);
the gate lattice precedent (`hitl.py:34-51`).
