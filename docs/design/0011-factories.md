# 0011 — Factories (archetype → incarnation, at scale, governed)

*Design draft for review — proposed by Fable 5 (design owner). The second reserved dive (0000 §2/§8) — CO's
farms generalized. **All decisions locked by JB 2026-07-02** (via AskUserQuestion, §5). Contract + simulator
landed with the dive. Companions: `0002 §1` (the lineage model), `0006 §2` (incarnation issuance), `0010`
(every stamped life walks through the Gateway), `0005` (cohorts get their statistics), `0013 §8` (scale caps).*

---

## Why this is a keystone

One archetype, many lives, is the whole multiplier: the game's N lives, the conglomerate's one pricing
function across every LOB, the League's draft class. The Factory is where that multiplication becomes a
**governed act** instead of a loop somebody wrote — ordered, quota-bounded, certified, and observable from
birth. It is also where 0013's *hard scale caps by trust tier* stop being prose: an anonymous self-serve
universe can stamp a handful of lives; a verified tier stamps fleets.

---

## 1. The StampOrder — one order, many lives

`contracts/v0/factory.schema.json`: **archetype · to_scope · count · generation · skills pin ·
per-incarnation budget · probation_runs**, signed by the ordering authority. For each life, the Factory:
issues a scope-bound DID with `lineage → archetype` (becky, `0006 §2`) → leases a budgeted capability token →
doors it through the Gateway (`0010`) → hands back an AgentSurface. **Never raw access; a fleet is stamped the
way a single agent joins.**

- **The generation is a first-class cohort label** — the draft class. `(scope, generation)` feeds the `0005`
  roll-up, so "compare season-3's class to season-1's" is a standings query, not an analytics project.
- **The quota is a wall**: `stamp_quota` (Tier Profile dial) bounds live incarnations per scope; retirement
  (`0002` — a governed end-of-life; the memory outlives the incarnation) frees the slot. Quota-exceeded is a
  refusal, and a vigil signal.

## 2. The BirthCertificate — identity operations are memory

Every stamp writes a signed **birth certificate** at the stamping scope (`0006 §4`'s rule applied): who was
born, from which archetype, in which generation, under which StampOrder, with which skill versions, and its
probation term. `born_at` is **universe-time** — the rookie is born in season 3, not on a Tuesday (0004).
The certificate also travels with the AgentSurface handle, so probation and provenance are checkable at the
point of use.

## 3. Upgrades — memory survives; a re-stamp is a new life

> **Locked 2026-07-02: upgrade in place; re-stamp is new.** When an archetype ships v4, running incarnations
> **keep their identity and their memory** — new skills arrive through the normal Standards cascade (skills
> are cascaded Standards, not memory; already locked). An explicit re-stamp mints a **new** DID with lineage
> to the same archetype — **a sibling, never a silent successor.** The League's player improves in the
> offseason instead of being body-snatched; the Enterprise's accountant keeps five quarters of context through
> an upgrade. Memory is the asset the substrate exists to keep; upgrades don't get to destroy it by default.

## 4. Probation — uncertainty pays for observation

> **Locked 2026-07-02: full-grade until the first bundle.** A fresh incarnation runs at judge sampling **1.0**
> (canary treatment, `0001`) until its first roll-up bundle reaches the certificate's `probation_runs` — then
> the tier's steady 1-in-N. A mis-stamped batch of a hundred rookies is caught in its first runs, not after
> sampling luck; the marketplace's wide confidence intervals (`0005`) narrow under exactly the observation
> that's paying for them. **Rookies play under full observation until they've earned a track record.**

## 5. Decisions — **all locked by JB, 2026-07-02** (via AskUserQuestion; recorded in `../decisions/`)

1. **Upgrade in place; re-stamp is a new life.** Identity and memory persist through archetype upgrades
   (skills cascade); re-stamps are siblings with shared lineage, honestly labeled.
2. **Rookie probation: full-grade until the first bundle reaches probation n**, recorded in the birth
   certificate. Judge tokens go exactly and only where uncertainty is highest.

## 6. Contract & simulator (landed with the dive)

`factory.schema.json` (StampOrder + BirthCertificate) · `tier-profile` gains `stamp_quota` · simulator
`factory.py` (stamp · retire · judge_rate) with certificates written as memory and carried on the surface.
**Three new tests, 23/23 passing:** draft-class-through-the-gateway (with the quota wall and the freed
retirement slot) · upgrade-in-place / re-stamp-is-a-new-life · rookie-probation-until-first-bundle.

---

*Unblocks: `0012` (HITL mechanics — the queues that gates and quotas escalate into), `0009` (a template's
roster is a set of StampOrders the provisioner executes), and the League's opening day: one player archetype,
two teams, a draft class each — stamped, certified, doored, and watched until they've proven themselves.
That is also, precisely, a season.* 🥃
