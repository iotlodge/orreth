# 0033 — The Physics of Memory (the reveal dive: information theory made canon)

*Design draft — proposed by Fable 5 (design owner), from JB's reveal session
(2026-07-14). This is the dive 0030 §2 held a socket for: the data scheme, arriving
as it should have — theory first, record-shape second. Source material: JB × ChatGPT
5.6 (two documents in `tmp/`, never tracked; the outside model saw only
demo.orreth.ai and jsbarth.com/projects/orreth), audited here against canon
0000–0032 and expanded where the design owner judged it needed. Nothing in §7
builds until JB locks §9 — and the coordinate (§4) is a contracts-adjacent change:
rule 9's gate, staged deliberately.*

---

## Why this is the reveal

JB (2026-07-14): *"You and I have in essence removed entropy from data/objects in
time — powerful — and this directly plays into Information Theory."*

Stated with scientific care, because the claim earns scrutiny: in an ordinary
enterprise, the **uncertainty of reconstructing any past moment grows with time**
— logs rotate, schemas drift, context scatters, provenance evaporates. Call it
what it is: the entropy of the record, rising. Orreth's whole architecture is the
refusal of that rise. Every record signed at creation (0001), bi-temporal (0004),
content-addressed, provenance-chained (0003), distilled only under governed
contracts with sealed QA samples, recallable to source. **Reconstruction
uncertainty in Orreth is bounded by contract, not accident** — entropy becomes a
dial the governance sets, per record class, per deployment. That is the science
behind the spacetime window's claim, and it is measurable — which means it can be
demoed, tested, and sold.

Shannon deliberately separated transmitting symbols from meaning. Orreth is the
system that adds what Shannon bracketed out — identity, objective, policy,
provenance, consequence — **without ever weakening the layer he formalized.**

## 1. The outside review, audited (the third convergence)

| Verdict | The review proposed | Orreth's answer |
|---|---|---|
| **Convergent — already canon** | "Context projection as a compiled artifact" (§21: projection_id, source refs, budget, excluded context, signature) | **The aperture, 0031 §2** — independently re-derived a third time. The review adds two fields the aperture adopts: `expected_information_value` and the `distortion_contract` |
| **Convergent — already canon** | Lossless vault + lossy operational memory (§8) | 0003 keep-classes: raw retained → distilled(raw kept) → distilled(raw dropped on schedule); the object store IS the vault |
| **Convergent — already canon** | Reactivation with two clocks (§14) | 0004 bi-temporal + 0031 §5 (rides 0022 Phase 2) |
| **Convergent — already canon** | Redundancy vs corroboration; source-dependence detection (§7) | 0014's corroboration receipts; **adopted sharpening**: independence must be *tested*, one claim copied across ten sites is one voice (extends charlotte's source registry) |
| **Convergent — already canon** | Error-correction analogies, feedback-never-overwrites (§18–19) | Sourced+Verified, annotate-never-rewrite, the lanes |
| **Adopted — the objective function** | **Information Bottleneck** as the formal statement of context projection (§10) | Canonized in §3: the aperture's stated optimization target |
| **Adopted — the missing contract** | **Rate-distortion**: distortion contracts on every distillation, objective-specific (§9) | §5 — the Distillation record (0003) gains `must_preserve / may_compress / prohibited_loss`; the steward's rubric becomes a distortion function |
| **Adopted — the measurement suite** | Entropy, information gain, DIV, distillation ratio, context efficiency, provenance completeness, recall fidelity (§22) | §6 — the harness: computable from records that already exist |
| **Adopted — the decay honesty** | λ varies by knowledge type (§15: a birth date and a location status decay differently) | §5 — retention classes (0004) gain per-class decay/review posture; feeds 0031's freshness and 0032's cadences |
| **Rejected** | Entropy formulas as *runtime* gates everywhere | Measures inform; **the lanes decide** (0024). A number never overrides a gate, and cognition stays plane-blind (covenant 5) |
| **Rejected** | Fusing modalities into scored fused_interpretation at admission | 0029 stands: modalities admit as separate evidence records; fusion is a *derived* record with its own provenance, challengeable like any claim |

## 2. The channel map — Shannon's diagram, Orreth's organs

```text
SOURCE            the world: humans, agents, tools, sensors, documents (DID'd — 0014/0018)
ENCODER           admission: the librarian's gather, upload-as-an-ask (0029), the chassis OBSERVE
CHANNEL           the substrate (storage), the aperture (transmission), the parlor (human channel)
NOISE             sensor error · semantic ambiguity · staleness · hallucination · ADVERSARIAL
                  (injection, forged identity, poisoned tools — the rug-pull door's beat)
DECODER           the resident/workforce mind at its seat
DESTINATION       action · artifact · memory · the human
FEEDBACK          critic markers (0024) · outcomes (0005) · the human's challenge (0031 §5)
```

The insight that reframes 0027: **the substrate is storage capacity; the aperture
is channel capacity — and they were never the same number.** The universe may hold
everything forever; what any seat *receives* is a narrow, governed, signed
transmission. "Owning more information does not mean transmitting more
information" is the intention contract, said in Shannon's voice.

## 3. The formulas — canon, with their Orreth bindings

*(JB's requirement: the science shown, usable in demos and test harnesses. Each
formula binds to records that already exist; none requires new cognition.)*

- **Entropy — uncertainty on the record.** `H(X) = −Σ p(x)·log₂ p(x)`
  Bound to: source-identity distributions (who is speaking — 0029's parked eye
  will emit these), intent ambiguity at the plan gate, contradiction density in a
  domain package. *An answer given under high H must say so* — provenance is UI
  (0008 §1), and now uncertainty is too.
- **Information gain — is another look worth it?** `IG = H(X) − H(X|Y)`
  Bound to: modality activation (0029/0034 — video wakes only when expected gain
  clears its privacy cost), retrieval escalation (is the deep-time hop worth its
  budget), the serials desk's delivery value (0032).
- **Mutual information — the aperture's objective.** `I(C;Y) = H(Y) − H(Y|C)`
  The aperture selects context C maximizing I(C; objective outcome) within the
  token budget — semantic similarity is a *proxy*; this is the *target*.
- **The Information Bottleneck — restraint, formalized.**
  `min I(T;X) − β·I(T;Y)` where X = the universe's whole state, T = the aperture,
  Y = the objective's outcome. **This is 0027 §3 and 0031 §2 as one line of math**:
  hand the seat as little of the universe as possible while preserving what the
  objective needs. β is governance — how much restraint the deployment demands.
- **Rate-distortion — what forgetting is allowed to cost.**
  `min R  s.t.  E[d(x, x̂)] ≤ D` — the steward's distillation is a rate-distortion
  code: minimum representation (rate = tokens/storage) subject to a **declared,
  objective-specific distortion bound**. A medication schedule and a hallway
  conversation do not share a d(·,·). §5 makes the contract explicit.
- **Temporal weight — decay that never deletes truth.** `w(Δt) = e^(−λ·Δt)`
  with **λ per record class** (0004), counteracted by re-observation and
  authority (0031 §5's reactivation). Decay reorders retrieval; it never edits
  the record (0003's law, now with its curve).

## 4. The coordinate — the index made first-class *(rule 9's gate)*

0030 §2 held this socket: *"every act must know which Thought served which
Observation served which Intention served which Objective."* The physics names
what the index must be: **every record's address in the ladder, in the org, in
both times, under an identity** — the five axes the formulas compute over.

```yaml
coordinate:                  # rides ON records — cited, never invented after the fact
  objective:  ContentHash    # the human's origin artifact (0030)
  intention:  ContentHash?   # the delegated unit it served (absent for organ beats)
  observation: ContentHash?  # the chassis act / admission that produced it
  thought:    RunRecordRef?  # the metered model call, when cognition occurred
  identity:   DID            # who (already canon — 0001 author)
  scope:      ScopePath      # where in the organization (already canon)
  occurred_at / received_at: # both clocks (already canon — 0004)
```

- Three of seven axes already ride every record (identity, scope, bi-temporal);
  the ladder axes today live *implicitly* in `derived_from` walks. The coordinate
  makes them **addressable**: "every Thought that served Objective O", "all
  Observations at scope S between T₁ and T₂ under Intention I" become index
  lookups, not lineage recursions.
- The aperture (0031 sp2) pins the downward mirror: what the seat could see. The
  coordinate pins the upward truth: what the act served. **Together they close
  the loop the spacetime walk needs at scale.**
- **Rule 9, honored loudly:** if the coordinate lands as record-shape or a
  contracts/v0 change, that is JB's explicit approval, per field, in §9. The
  design permits a soft landing first: coordinate-as-tags (the GIN indexes
  already serve tag lookups — 0022) before any contract touch.

## 5. Distortion contracts and retention regimes — one physics, many worlds

**The Distillation record (0003) gains the contract:**

```yaml
distillation_contract:       # extends Distillation.method — the rubric becomes a distortion function
  must_preserve: [...]       # decision-critical facts — loss is REFUSED at save
  may_compress: [...]        # narrative, phrasing, redundancy
  prohibited_loss: [...]     # the intolerables (dosage · timing · authority · consent state)
  distortion_bound: D        # measured against the sealed QA sample (0003's 1-in-N, now with a yardstick)
  objective_binding: ...     # WHOSE decisions this representation must stay sufficient for
```

**Retention classes (0004) gain the physics dial** — and this is where JB's two
use cases become one design: *deployments differ in their distortion economics,
not their machinery.*

| Regime | Example classes | λ / review posture | Distortion posture |
|---|---|---|---|
| **Enterprise** | SOX financial (min 7y, raw) · GDPR personal (max, crypto-shred) · ops telemetry (fast decay) | per class, regulator-set | audit classes: near-zero D, raw retained; telemetry: aggressive R |
| **Cognitive Continuity** (0034) | identity claims (λ≈0, never decay) · medication (high review, zero-D) · location status (minutes) · episodic memories (distill, raw in vault) | per class, care-team + human set | `prohibited_loss` carries names, relationships, consent |

Same binary, same steward, same contracts — different dials. **This is the
"wide range of deployments" claim made structural.**

## 6. The harness — the science made runnable *(JB: "helpful in demos and test harnesses")*

A new conformance module, `orreth_sim/infotheory.py`, computing from records that
already exist — no new stores, no cognition, pure functions over the log:

| Metric | Computed from | Demo/test claim |
|---|---|---|
| **Reconstruction entropy** H(moment · record) | provenance walks + retention state | *the headline*: bounded and flat over time in Orreth; provably unbounded without provenance — the entropy-removal demo |
| **Distillation ratio** | raw bytes / distilled bytes per keep-class | compression the auditor can see |
| **Recall fidelity** | distilled vs sealed QA sample, scored by the contract's d(·,·) | 0003's QA dial gets its yardstick |
| **Context efficiency** | decision-relevant info / aperture tokens (from RunRecords × outcomes) | "the smallest context did the best-audited thinking," as a number |
| **Provenance completeness** | % records whose derived_from resolves to source or stub | already ~structural; now a badge |
| **Corroboration independence** | source-DID graph of receipts | one claim on ten sites = one voice, detected |
| **Aperture bottleneck score** | I(T;Y) proxy vs T size across runs | the restraint curve, plotted — grace's evidence stream learns to read it |

Spoonful 1 lands the module + tests; the reel gains an *information physics*
story; the glass can later wear the numbers (beads with DIV chips — deferred to
the Brain Glass, 0034).

## 7. The spoonfuls

| # | Spoonful | Nature |
|---|---|---|
| 1 | **The harness** — infotheory.py + tests + the entropy-removal demo (reel story) | ✅ landed 2026-07-14 — `orreth_sim/infotheory.py` (entropy · information gain · reconstruction entropy w/ live/stub/missing walk · mortal-world counterfactual · distillation ratio · resolution fidelity · context efficiency w/ deterministic runs counted apart · provenance completeness where a stub IS a complete answer · corroboration voices-vs-echoes) + 8 tests (140/140 suite) + `scripts/demo.sh physics` — the headline table live: the mortal staircase climbs 0→64 bits while orreth holds at 0→16, every bit accounted for. **The harness caught a real defect on day one:** `_distill` hashed its body into the record id but never stored it — distillations were body-less (read honestly as stubs). Fixed: the id commits to the body, so the body is stored |
| 2 | **Distortion contracts** — the Distillation record extension + refused-at-save on prohibited_loss + QA scoring against d(·,·) | ✅ landed 2026-07-14 — **substrate behavior, not measurement**: `set_distortion_contract(tag, …)` on every node; `_distill` CARRIES the contract-named values (each citing its source) and merges carried maps from source distillations, so the intolerables survive every tier; the contracted class rides up as tags (and only it — no drag on knowledge/parked flows); **the save-gate lives in `write()`** — a distillation that drops a contract-named key is refused against the NODE's law, whoever wrote it (`DistortionViolation`); pushed-up distillations with unresolvable sources are trusted as the child's signed work, measured instead by `infotheory.contract_fidelity` (carried·cited·held per key; a stub citation counts — the value surviving raw expiry IS the contract working). Contract rides the BODY (id-committed, signed) — zero contracts/v0 touch; promotion into `method` waits at Phase D's gate. 4 new tests, 144/144; the demo gains the contract act: distilled twice, every raw purged, dosage still reads at the top, fidelity 1.0 |
| 3 | **The coordinate, soft** — ladder axes as tags on new records (fingertip/chassis/librarian cite objective/intention hashes they already hold); index lookups in the sim + wire | ✅ landed 2026-07-14 — **on the live rig**: intentions are content-addressed (`make_intention` gains an id that is the hash OF its own four fields — the restraint test now proves it smuggles nothing); `of:<objective>` / `via:<intention>` tags ride every plan, outcome, review marker, assembly, parked failure, and the knowledge a failure commissions (the loop joins the ladder — librarian `tend` inherits the coordinate); `by_coordinate()` is the sim's index lookup; `coordinate_citations()` is the wire's (a tag match over the floors' GIN, never a recursion); the ledger's done card shows it — proven as a human: "the coordinate · **14 record(s) across the floors** cite this objective" with the arithmetic exact (1 plan + 6 outcomes + 6 markers + 1 assembly). 146/146. The hard freeze (contracts/v0) waits at Phase D's gate with the aperture |
| 4 | **The coordinate, hard + the aperture** — contracts/v0 record-shape lock, and 0031 spoonful 2 lands against it (context_hash widens; RunRecord semantics per 0005/0007) | ✅ landed 2026-07-15 — **THE PHASE D GATE, JB's explicit approvals per change (all four)**: ① memory-record gains optional `coordinate` {objective·intention·observation·thought} — top-level, unsigned beside derived_from (signature-subset widening queued as its own question); producers stamp it (plans, outcomes, assemblies, apertures) and the soft of:/via: tags stay valid ② Distillation.method gains `contract` — the sp2-proven shape promoted verbatim; method-first reads with body fallback ③ tier-profile gains `memory.review_interval` + `aperture{beta}` + the named `template` block (the confession honored: 0034 sp1's overlay was contract-illegal as shipped; the overlaid profile now VALIDATES whole, asserted in conformance) ④ run-record `context_hash` widened to the aperture. Parity 10/10 before and after the cuts (covenant 6) · 171/171 · proven live: 7 apertures cut at one apex fan — **0033 IS WHOLE; the aperture socket (0031 sp2) closed with it** |

## 8. Rules this dive writes

1. **Entropy is a dial, not a decay** — reconstruction uncertainty per class is
   set by governed contract; nothing degrades by accident.
2. **Storage is not transmission** — the substrate holds; the aperture transmits;
   their budgets never conflate.
3. **Every distillation declares its distortion** — what must survive, what may
   compress, what loss is refused at save.
4. **Measures inform; lanes decide** — no formula ever overrides a gate.
5. **Every act knows its coordinate** — objective · intention · observation ·
   thought · identity · scope · both clocks. The index IS the claim (0030),
   now with its axes named.

## 9. Decisions

**Canon per JB (2026-07-14, the reveal):** information theory is the science
behind Orreth and shall be incorporated with its formulas · the formulas serve
demos and test harnesses · the entropy-removal framing is the claim · one physics
spans radically different deployments (enterprise ↔ personal continuity) · the
Brain Glass direction (0034) · same rules as 0031: audit deep, take what's
needed, expand where the design owner judges.

**Closed by the design owner (JB may veto):** the Information Bottleneck is the
aperture's stated objective · distortion contracts extend the Distillation record
(never a new store) · fusion stays a derived record (0029 unbroken) · formulas
never gate — lanes gate · the coordinate lands soft (tags) before hard
(contracts) · "removed entropy" is always stated as *reconstruction uncertainty
bounded by contract* — scientifically defensible, never mystical.

**OPEN (JB's locks after reading):**
- **The coordinate's hard shape** — which axes freeze into contracts/v0, and
  when (spoonful 4 = the rule-9 gate; the aperture lands with it).
- **β per tier** — does the bottleneck's restraint dial ride the Tier Profile
  (a contracts touch) or config-as-memory?
- **The headline demo** — is the entropy-removal story reel-first or a live
  glass panel first?
- **Distortion-bound defaults** per the two worked regimes (§5's table is
  proposed, not locked).

---

*Shannon showed how to move a message through noise without losing it. Orreth is
what happens when a whole organization decides its history deserves the same
guarantee — and the guarantee gets a meter.* 🥂
