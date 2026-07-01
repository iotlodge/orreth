# 0002 — Living Identity + Retrieval (the substrate keystone)

*Design draft for review. Schemas are language-neutral shapes, not code. Builds on `0001` (the `MemoryRecord`
atom). Discharges the six use-case requirements from `../decisions/README.md`. **Amended 2026-07-01** per the
design review + locked decisions: ScopePath-relative addressing (§3), merge semantics (§3), budget-miss ≡
authz-miss (§4), interview query budget (§5). All §8 decisions locked.*

---

## Why this is the keystone

Everything the vision promises — non-fading memory, collective recall, the game's N lives, the traded player,
the conglomerate's audit, "interview before you buy" — rests on two things being right: **who an identity is**,
and **how memory is retrieved across space and time.** `0001` gave us the memory *atom*. `0002` gives us the
*identity it hangs on* and the *read path that reaches it.*

**The six requirements this discharges** (from the use cases):

| # | Requirement | Where it's answered |
|---|---|---|
| 1 | Identity lineage — archetype → incarnation | §1 |
| 2 | Memory portability — `portable | branch-bound` | §2 |
| 3 | Cross-branch / cross-tenant retrieval authorization | §4 |
| 4 | Showcase / portfolio scope (the interview) | §2, §5 |
| 5 | Retention / tombstone erasure + consent | §6 |
| 6 | Sourced + Verified as a first-class audit property | §3, §4 |

---

## 1. The Living Identity

An `Identity` is a **universe-unique DID** that persists independent of any running process. The process is the
incarnation; the identity is the thread.

```
Identity {
  did        : DID                 # universe-unique, becky-issued, resolvable via the NANDA index
  lineage    : DID?                # → its archetype, if this is an incarnation (null for an archetype/root identity)
  role       : "archetype" | "instance"
  scope      : ScopePath           # current binding: which Universe/Ecosystem/Field this identity lives in
  facts      : AgentFacts          # W3C VC — capabilities + runtime-earned evaluations (the basis of the portfolio)
  keys       : { signing: PubKey } # Ed25519 — signs its memory and its retrievals
  status     : "online" | "offline" | "retired"
  born_at    : EcosystemClock
}
```

### Archetype → instance (requirement 1)

- An **archetype** is a *template* identity — "Cloud-Architect-agent v3", or "You, the player." It carries the
  **shared skills/traits** (which are cascaded Standards, not memory) and spawns instances.
- An **instance** is a **scope-bound** identity that *inherits its archetype's skills* but **accumulates its own,
  isolated memory** in its branch.

> Fan-out (parallel): one archetype → many instances, each in a different Ecosystem, each remembering its own life.
> This is the game's N lives, the conglomerate's "same pricing function across every LOB," the league's roster templates.

### Decoupled from the process (online / offline / reboot)

A running process **attaches** to an identity for a session and **detaches** on offline. Memory is keyed to the
identity's DID, never to the process — so **reboot ≠ death.**

```
Attachment { identity: DID, process: ProcessRef, session_keys: EphemeralKeys, since: EcosystemClock }
```

### Transfer — a governed re-scope (the traded player, the reorg)

Moving an identity between branches is a **governed action**, not a copy: re-bind its `scope`, carry its
**portable** memory (§2), leave its **branch-bound** memory behind, and write a signed access record.

```
Transfer { identity: DID, from: ScopePath, to: ScopePath, approved_by: DID[], carries: "portable-only", at: EcosystemClock, sig: Sig }
```

### Retirement — not deletion

`status: retired` is a **governed end-of-life**: memory is tombstoned per retention/consent (§6), but the fact
that the identity existed remains, for audit. *(The digital-legacy and healthcare cases need exactly this.)*

---

## 2. Memory scopes — extending the `0001` MemoryRecord

Every `MemoryRecord` gains a `visibility` facet. These three axes are what the use cases demand:

```
visibility {
  tenancy  : "tenant-private" | "portfolio"   # walled  vs  interviewable/showcaseable
  mobility : "branch-bound"    | "portable"    # stays with the branch  vs  travels with the identity
  consent  : "active" | { consented_for: Purpose[] } | { tombstoned: … }   # for regulated / personal data (§6)
}
```

- **tenancy — the interview firewall (requirement 4).** `tenant-private` is the raw memory of what an identity did
  for a specific tenant. `portfolio` is a **governed, anonymized/aggregated projection** of it — "closed 400 tickets
  at 0.94 mean score across 3 engagements," *without* revealing the tickets or the clients. **An interview reads
  portfolio only.** You can vet an agent's judgment without extracting its former employer's secrets.
- **mobility — what travels (requirement 2).** On `Transfer`, `portable` memory follows the identity; `branch-bound`
  stays. **Default is `branch-bound`** (safe: memory never follows an identity by accident). Note that an archetype's
  *skills* are portable by nature — they're cascaded Standards, not tenant memory. *(A traded player keeps "how to
  pitch"; leaves "team A's private signs.")*
- **consent — the regulated floor (requirement 5).** For personal/health/financial memory, consent is explicit and
  its withdrawal drives a tombstone (§6).

---

## 3. The retrieval contract — space × time

Retrieval is the third flow, and the point of the substrate. A query navigates **space** (which identities) and
**time** (how far back), gated by **authorization** (§4) and a **per-tier time budget**.

```
Query {
  requester : DID
  subject   : "self" | { identity: DID } | { cohort: Selector }   # own · another identity · a group
  space     : "self" | { ancestors: N } | "apex" | { scope: ScopePath }   # breadth — ScopePath-relative,
                                                                  # NEVER tier-named (0000 §1: recursion stays free;
                                                                  # friendly tier names live in profiles and panes)
  time      : TimeWindow                                          # depth: last-7d … last-year … all-time
  intent    : "recall" | "analyze" | "interview"                  # picks the visibility scope that applies
  budget    : { time_ms, cost, tier_hint? }                       # the configurable per-tier time budget
  auth      : CapabilityToken                                     # proves the requester may read this space (§4)
}
```

### The time-horizon escalation (the L1→L2→L3 cache model)

1. **Serve locally first.** The Field (recent memory) answers what it holds within the query's **time budget**.
2. **Time-horizon miss → escalate.** If the `time` window reaches past the Field's horizon (or the budget is spent),
   the Field **serves what it has and delegates the deeper-time remainder to its parent** (Ecosystem → Universe).
3. **The Universe has no time restriction — all of spacetime.** Deep-time reads cost more to reach, exactly as they should.

> A time-horizon miss escalates a query up a tier — recent memory is cheap and local, deep-time lives at the apex.

### Merge semantics (amended 2026-07-01 — partial + delegate, locked)

When multiple tiers serve one query, the merge is deterministic:

- **Dedup by `ContentHash`** — identical records served by two tiers collapse to one hit; both serving scopes
  are recorded in provenance.
- **Ordering** — newest time-bucket first; relevance-ranked within a bucket. Deterministic: the same corpus
  and query produce the same ordering regardless of which tier answered first.
- **Per-hit fidelity is labeled** — a hit is `verified` (raw, chain checks) or `distilled` (a Distillation,
  chain-verified per `0003` §2; if its raw inputs have lapsed, labeled `distilled — raw expired <policy ref>`).
- **The remainder is explicit** — if budget expires before the deepest tier answers, the result carries
  `remainder: { not_served: TimeWindow }` so the caller knows exactly what was not reached and can re-query
  with a bigger budget. A partial answer never masquerades as a complete one.

### The result — Sourced + Verified (requirement 6)

```
RetrievalResult {
  hits         : [ { ref: ContentHash, source: DID, scope: ScopePath,
                     fidelity: "verified" | "distilled" | "distilled-raw-expired" } ]
  provenance   : { served_by: ScopePath[], time_span, budget_spent }
  verification : "verified" | "partial" | "rejected"   # result-level: partial ⇒ remainder present
  remainder    : { not_served: TimeWindow }?           # what the budget didn't reach — never silent
}
```

- **Sourced** = every hit carries its author identity's DID.
- **Verified** = signature + content-hash checked; tamper-evident. Unverifiable hits are dropped or flagged — a
  retrieval never launders an unattributable memory into an answer.

---

## 4. Authorization — the #1 security surface (requirement 3)

A universe-wide read is the ultimate exfiltration vector, so the read path is governed *harder* than the write path.

- **own** (`subject: self`) — an identity reads its own memory. Baseline capability.
- **cross-agent** (`subject: {identity|cohort}`) — requires an explicit capability grant **and** the target's
  `visibility` must permit it: `portfolio` is readable in an interview; `tenant-private` requires same-tenant + grant.
- **universe-wide** (`space: universe`) — the broadest, most dangerous read; requires a **Universe-level capability**
  held only by the human conductor and named resident analysis agents. This is where "understand anything" runs.
- **Tenant isolation holds on read.** A requester in Ecosystem A **cannot** read Ecosystem B's `tenant-private`
  memory — full stop — unless a human-gated cross-tenant authorization exists. The *only* cross-tenant window is
  `portfolio` scope (a governed, anonymized projection).
- **Every retrieval is itself a signed, append-only access record** — *who read what, when, under which capability.*
  Retrieval is auditable. *(Healthcare and finance require this; it also makes the read path forensically accountable.)*
- **Budget-miss ≡ authz-miss to the caller** *(amended 2026-07-01 — side-channel fix)*: a query that exhausts
  its budget and a query that lacks authorization return indistinguishable responses. Only the privileged
  access log records which occurred — the existence of deeper or walled memory is never leaked by the *shape*
  of a refusal.

---

## 5. The interview — portfolio-scope retrieval (the "Build My First Universe" keystone)

An **interview** is `intent: "interview"`: a **bounded, sandboxed retrieval + converse session** against a candidate
identity, under strict limits:

- **Reads `portfolio` scope only** — `tenant-private` memory is walled.
- **No write, no cross-tenant read, time-boxed** — a read-only sandbox.
- **Query-budgeted, with noised aggregates** *(amended 2026-07-01 — adaptive-query defense)*: an interview
  carries a finite query budget, and portfolio statistics are served with calibrated noise — a motivated
  interviewer running many adaptive queries cannot triangulate tenant-private specifics out of aggregates.
- The candidate **reasons live** (you can test its judgment), but every factual claim resolves to **Sourced +
  Verified** portfolio memory + its AgentFacts (runtime-earned evaluations).

> This is the trust primitive a marketplace has never had: not star ratings — *talk to it yourself,* and everything
> it tells you about its track record is cryptographically backed and its former employers' secrets stay sealed.

---

## 6. Retention, consent, and tombstone (the foundational floor — requirement 5)

- Memory is **append-only**; erasure is a **governed, audited tombstone** (from `0001`) — provably retired, never
  silently lost.
- **Consent** is per-record for personal/regulated memory; withdrawal schedules a tombstone.
- **Retention** is set by the **Tier Profile** (0004): how long raw vs distilled memory is held before pruning (0003) —
  the "configurable for years" dial. Consent + retention floors are **universal** (set at the Universe, non-overridable).

---

## 7. Security properties (consolidated)

- Universe-unique DID; **Ed25519-signed** memory and retrievals; **content-addressed** (tamper-evident).
- Retrieval is a **capability**; every read is a **signed access record** (auditable).
- **Tenant isolation on read**; `portfolio` is the *only* cross-tenant window, and it's a governed anonymized projection.
- **Skills portable, tenant-private memory branch-bound by default** — nothing follows an identity by accident.
- **Retirement ≠ deletion** — the audit trail of an identity's existence survives its end.

---

## 8. Decisions — **all locked by JB, 2026-07-01** (recorded in `../decisions/`)

1. **Portfolio: auto-projection + per-entry owner opt-out**, governed by an anonymization Standard. Defensible
   because the interview sandbox carries a **query budget + noised aggregates** (adaptive-query defense, per the
   2026-07-01 review).
2. **Mobility: `branch-bound` by default.** Nothing follows an identity unless explicitly marked portable;
   skills travel by nature (cascaded Standards, not memory).
3. **Cross-tenant line: anonymized benchmarks only.** Collective reads *up the ancestor chain* are a core,
   capability-gated right for authorized agents. **Sibling** tenant-private memory is never readable raw by a
   sibling — only governed, anonymized aggregates computed at the common parent. Raw universe-wide reads remain
   conductor + resident analysis agents (2 human co-signs, per 0006).
4. **Escalation: serve-what-you-have + delegate the deeper-time remainder.** Cross-tier merge/dedup/ordering
   semantics to be pinned in this spec's amendments.
5. **Transfer: source veto, overridable by a common ancestor** as a governed, signed action — a team must
   release a player; the league can compel under its rules; the override is on the record. Co-signs remain:
   both authorities + the identity owner.
6. **Interview footprint: owner-visible, buyer-invisible.** A minimal signed access record the identity's owner
   sees; future buyers never do — audit without market chill.

---

*Unblocks: `0003` (pruning — what each tier keeps vs distills, which sets retrieval horizons), `0004` (Tier Profile —
the per-tier time budget), `0006` (becky — archetype/instance DID issuance + the capability tokens this spec assumes).*
