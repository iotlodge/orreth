# Decisions

The decision ledger — what's **locked**, and what's **open** (to be made in a `design/` dive and then moved up here).
Full rationale for locked items lives in `../vision/FUTURE-the-orreth.md`; use cases that drive the open ones live in
`../vision/use-cases.md`.

---

## ✅ Locked

### The center (rebaselined 2026-06-30 — memory-first)
- **Orreth is a memory substrate**, security-first and identity-anchored, across spacetime. **Governance is its first
  application, not its purpose.**
- **The Living Identity is the primary primitive** — universe-unique, used at every layer, decoupled from the process
  (online / offline / reboot; reboot ≠ death). **Memory is keyed to the identity, not the process.**
- **The Universe is Foundation *and* Apex** — universal policy rests on it (down), all memory rises to it (up).
- **Three flows:** policy **DOWN** (foundational, non-overridable) · memory **UP** (pruned at every layer) · retrieval
  **UP** by time-horizon (Sourced + Verified).
- **The layers are filters** — prune / dedup / summarize / compress to protect the Universe's space (makes "years" affordable).
- **Skills are crystallized memory** — versioned across the universe; they reduce the need to trawl raw memory.
- **Retrieval is the #1 security surface** — an authorized capability, tenant-isolated on read.

### The mechanism
- **Name** Orreth; repo `orreth`; "Harness" = the architectural primitive; tiers Universe / Ecosystem / Field / Agents.
- **One recursive primitive**, `tier` = a Tier Profile (config, not code). **Depth capped at 3**; expandable by SDK/CDK.
- **Roll-up** = monoidal sufficient statistics + signed content-addressed pointers; count-weighted confidence.
- **Cascade** = inherited Standards; floors non-overridable (lexicographic); soft = most-specific-wins; skills additive.
- **Consent = the join spectrum** (fully-joined / floors-only / observe-only / decoupled): **floors compelled for the
  joined, everything else offered**; a leased agent's floor is enforced by its lease/capability credential.
- **Targeting** = one Selector (`all` / `role` / `ecosystem` / `field` / `selection`); target at-or-below only.
- **Security** = recursive DID chain; **resident (TCB) vs registered (workforce)** agents; tenant isolation recurses.
- **Rust** for the plane (identity-verify, ingestion, cascade/pruning resolver, retrieval routing + time-budget gating,
  brainstem); **Python / LangGraph** for cognition (memory stewards, analysis agents).
- **Headroom** adopted as the byte substrate (compression · CacheAligner · CCR reversible store · cross-agent memory);
  governance/pruning *policy* stays ours; vendor / pin / review.
- **Memory records** = append-only + content-addressed + DID-signed; promoted-up-as-pointers; **governed-tombstone erasure**.

---

## 🟡 Open — to be made (drives the substrate keystone dive)

Surfaced by the use cases (`../vision/use-cases.md`). Each becomes a `design/` spec, then locks up here.

1. **Identity lineage — archetype → incarnation.** One template identity, many scoped incarnations; **shared skills,
   isolated memory.** *(game's N lives · "same function across LOBs" · a traded player)*
2. **Memory portability scope — `portable | branch-bound`.** What memory travels when an identity moves branches. *(trade, reorg, new life)*
3. **Cross-branch / cross-tenant retrieval authorization.** Who may read across ecosystems (the conductor: yes; a rival: no). *(compare-my-lives · scout-the-league · benchmark-all-LOBs)*
4. **Showcase / portfolio scope vs tenant-private memory.** The **interview-before-you-buy** mechanism: an identity's
   public, Sourced+Verified portfolio (interviewable) vs its walled tenant-private memory. *(Build My First Universe)*
5. **Retention / governed-tombstone erasure + consent as a foundational floor.** *(healthcare, GDPR)*
6. **Sourced + Verified as a first-class audit property.** *(finance, science, supply chain)*

### Open (carried from `design/0001`, to lock during the keystone dive)
7. **One store or two** for skills vs memories? *(lean: one `MemoryRecord` lineage, skills as a typed view)*
8. **Who may author an acceptance rubric?** *(lean: resident/human only; workforce agents may propose, not ratify)*
9. **Confidence statistic** — exact model *(lean: defer to the Run Record dive)*
10. **`model_judge` cost** at fleet scale *(lean: sample-by-default, full-grade on canary)*
11. **Scaffold portability across model families** *(lean: tag + measure on canary, refuse only if the floor fails)*

### Open (product / GTM — "Build My First Universe")
12. **Universe templates** = a Tier Profile + starter bundle (Standards, skill archetypes, agent-template roster,
    retention config, policy floors). What's in the first templates (Company / League / Game / Lab / Second Brain)?
13. **"Wild vs REAL is a policy dial."** Which policy floors define the tone spectrum, and what's the safe default?
14. **Provisioning / subscription** — self-serve spin-up of a Universe from a template.

---

## ADR convention (for individual decisions once we start logging them)

`NNNN-short-title.md` with: **Context · Decision · Consequences · Status (proposed / accepted / superseded)**.
