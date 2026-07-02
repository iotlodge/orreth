# 0007 — The Cascade Resolver (one fold, every law)

*Design draft for review — proposed by Fable 5 (design owner). **All decisions locked by JB 2026-07-02**
(via AskUserQuestion, §5). Contract + simulator landed with the dive. This is the plane's hot path — the
sim proves the semantics; the Rust `orrethd` proves the speed against the same fixtures.*

---

## Why this is a keystone

Every organ asks the same question before acting: *what rules am I under, here, now?* The steward distills
under a rubric, the gateway admits under floors, the factory stamps under quotas, the pane renders under a
tone — all of them need the inherited chain composed into one answer. The resolver is that answer as a **pure,
deterministic fold**: same chain in, bit-identical Resolved Context out.

---

## 1. One resolver, per-field merge laws

The unification this dive contributes: the system has quietly accumulated a family of cascade laws, and they
are all folds with a declared monotone direction —

| Law | Applies to | Direction |
|---|---|---|
| **floor-tighten** | policy floors (0000), platform floors (0013 §2) | strictness only rises (enforced at publication, composed here) |
| **most-specific-wins** | soft standards — the tone dial, defaults | nearest tier wins, attributed; tiebreak = version, then id — never silent |
| **additive** | skills (0001) | union; same name ⇒ higher version |
| **monotone dials** | retention min↑/max↓ (0004 §4), gates co_signs↑/cooling_off↑/ttl↓ (0012 §2) | per-field lattices, same fold |

The merge law travels with the field's contract, not with the resolver — adding a new cascaded dial never
means touching resolver code. **Floors always beat soft**, and a soft conflict is always attributed
(`from_scope` says which tier won).

## 2. Content-addressed policy — the ResolvedContext

The resolver's output is hashed over its canonical content: **same chain ⇒ same id.** That one property makes
policy a first-class citizen of everything already built: **cacheable** (invalidate on bundle version change —
the Rust hot path is a hash lookup), **diffable** (a policy change is a diff of two contexts — 0008's
GraphSpec discipline applied to law), and **canary-able** (run the new context on a cohort before the fleet).

> **Locked 2026-07-02: RunRecords pin their `context_hash`.** *"What rules governed this agent when it did X"*
> is a lookup, not an investigation — the regulator's first question, answered best. Drift analysis splits
> *behavior changed* from *policy changed* cleanly. Memory records stay lighter; their governance is derivable
> from scope + time.

## 3. The read is a pull — and partition fails closed

Resolution is **child-initiated**: the resolver reads up the ancestry (a pull, tier by tier — a parent never
reaches in), and the `as_of` section records exactly what it saw, per tier.

> **Locked 2026-07-02: fail-closed continue + signal.** A partitioned node keeps enforcing its **last-known**
> resolved context — floors persist; rules are never absent while blind — keeps working, and marks every
> stale tier honestly in `as_of`. Resolving blind is a **vigil signal**, and prolonged staleness escalates
> through 0012's queues. The one real risk — missing a floor issued during the split — is bounded by the
> signal, not by halting the world: an Earth Mapper field offline for a day keeps its floors *and* its work,
> and a wall-clock blip never freezes a simulated season.

## 4. Determinism, precisely

Root→leaf fold; canonical ordering everywhere (floors sorted by content hash, maps by key); no clock, no
randomness, no iteration-order dependence — the tests build the same world in reverse declaration order and
get the identical hash. This is also what makes the resolver *conformance-testable* into Rust: the fixtures
are pure input→output pairs.

## 5. Decisions — **all locked by JB, 2026-07-02** (via AskUserQuestion; recorded in `../decisions/`)

1. **RunRecords pin `context_hash`** (memory records don't — derivable, and the substrate stays lean).
2. **Partition: fail-closed continue + signal** — last-known law persists, staleness is loud, availability
   is never hostage to a network blip.

## 6. Contract & simulator (landed with the dive)

`resolved-context.schema.json` · `run-record` gains optional `context_hash` · simulator `resolver.py`
(`resolve()` — the fold) with `soft`/`skills`/`partitioned` on the node. **Five new tests, 32/32 passing:**
deterministic-and-content-addressed (reverse-order world ⇒ same hash) · most-specific-wins with floors riding
along · skills-additive-with-version-tiebreak · partition-fails-closed-and-signals (with resync healing) ·
runs-pin-their-context.

---

*Unblocks: `0009` (a template is, in the end, a pre-authored chain for this resolver to fold) — the last dive
of the design phase — and the Rust plane's hot path, whose conformance fixtures this dive's determinism makes
possible. Every organ now has one answer to "what law am I under": a hash it can cache, diff, and cite.* 🥃
